import json
import subprocess
import sys
from pathlib import Path

from policy_extraction_utils import (
    OUTPUT_DIR,
    build_doc_meta_with_compensation,
    build_priority3_annotation_set,
    build_task_clause_records,
    evaluate_weak_value_set,
    iter_policy_files,
    load_no_parameter_top25,
)


def write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def run_normalization_tests(project_root: Path) -> dict:
    test_path = project_root / "00_整理记录" / "tests" / "test_postprocess_normalizer.py"
    cmd = [sys.executable, "-m", "unittest", str(test_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "command": " ".join(cmd),
        "return_code": proc.returncode,
        "passed": proc.returncode == 0,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def build_after_check_markdown(after_summary: dict) -> str:
    p1 = after_summary["priority1"]
    p2 = after_summary["priority2"]
    p3 = after_summary["priority3"]
    p4 = after_summary["priority4"]

    lines = [
        "# v1.4 优先项改后体检报告",
        "",
        f"生成时间：{after_summary['generated_at']}",
        "",
        "## 总结",
        f"- 优先1（文件名补偿+冲突仲裁）：issue_date 覆盖 {p1['before_coverage_rate']['issue_date']}% -> {p1['after_coverage_rate']['issue_date']}%，doc_type 覆盖 {p1['before_coverage_rate']['doc_type']}% -> {p1['after_coverage_rate']['doc_type']}%，document_no 覆盖 {p1['before_coverage_rate']['document_no']}% -> {p1['after_coverage_rate']['document_no']}%。",
        f"- 优先2（任务型条款结构化）：任务条款 {p2['task_clauses']} 条，主体覆盖 {p2['task_field_coverage']['task_subject']}%，动作覆盖 {p2['task_field_coverage']['task_action']}%，期限覆盖 {p2['task_field_coverage']['task_deadline']}%，考核覆盖 {p2['task_field_coverage']['task_assessment']}%。",
        f"- 优先3（no_parameter_top25 验证）：样本 {p3['doc_count']} 份，机制召回（micro_recall）{p3['micro_recall']}，误抽率（false_positive_rate）{p3['false_positive_rate']}，完全匹配率 {p3['doc_exact_match_rate']}。",
        f"- 优先4（归一顺序单测）：测试通过={p4['passed']}（return_code={p4['return_code']}）。",
        "",
        "## 产物文件",
        "- priority1: `00_整理记录/priority1_doc_meta_compensation.json`",
        "- priority1 sample: `00_整理记录/priority1_doc_meta_compensation_sample.json`",
        "- priority2 records: `00_整理记录/priority2_task_clause_structured.jsonl`",
        "- priority2 summary: `00_整理记录/priority2_task_clause_summary.json`",
        "- priority3 set: `00_整理记录/priority3_no_parameter_top25_annotation.jsonl`",
        "- priority3 eval: `00_整理记录/priority3_uie_weak_value_eval.json`",
        "- priority4 tests: `00_整理记录/priority4_normalization_tests.json`",
        "- after check json: `00_整理记录/schema_v1_4_fit_check_after_priority_updates.json`",
        "",
        "## 说明",
        "- 优先3当前使用 `uie_proxy_keyword_baseline` 进行弱数值样本预验收；同一评估脚本可替换成真实 UIE 预测结果继续复用。",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    project_root = OUTPUT_DIR.parent
    files = iter_policy_files()

    # Priority 1
    p1_rows, p1_summary = build_doc_meta_with_compensation(files)
    write_json(OUTPUT_DIR / "priority1_doc_meta_compensation.json", {"summary": p1_summary, "rows": p1_rows})
    write_json(
        OUTPUT_DIR / "priority1_doc_meta_compensation_sample.json",
        {"summary": p1_summary, "rows_sample": p1_rows[:40]},
    )

    # Priority 2
    p2_records, p2_summary = build_task_clause_records(files)
    write_jsonl(OUTPUT_DIR / "priority2_task_clause_structured.jsonl", p2_records)
    write_json(OUTPUT_DIR / "priority2_task_clause_summary.json", p2_summary)

    # Priority 3
    no_param = load_no_parameter_top25()
    p3_ann = build_priority3_annotation_set(no_param)
    write_jsonl(OUTPUT_DIR / "priority3_no_parameter_top25_annotation.jsonl", p3_ann)
    p3_eval = evaluate_weak_value_set(p3_ann)
    write_json(OUTPUT_DIR / "priority3_uie_weak_value_eval.json", p3_eval)

    # Priority 4
    p4_test = run_normalization_tests(project_root)
    write_json(OUTPUT_DIR / "priority4_normalization_tests.json", p4_test)

    after_summary = {
        "generated_at": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "priority1": p1_summary,
        "priority2": p2_summary,
        "priority3": {
            "evaluation_mode": p3_eval["evaluation_mode"],
            "doc_count": p3_eval["doc_count"],
            "micro_precision": p3_eval["micro_precision"],
            "micro_recall": p3_eval["micro_recall"],
            "false_positive_rate": p3_eval["false_positive_rate"],
            "doc_exact_match_rate": p3_eval["doc_exact_match_rate"],
        },
        "priority4": {
            "passed": p4_test["passed"],
            "return_code": p4_test["return_code"],
        },
        "output_files": {
            "priority1": "00_整理记录/priority1_doc_meta_compensation.json",
            "priority2": "00_整理记录/priority2_task_clause_structured.jsonl",
            "priority3": "00_整理记录/priority3_uie_weak_value_eval.json",
            "priority4": "00_整理记录/priority4_normalization_tests.json",
        },
    }
    write_json(OUTPUT_DIR / "schema_v1_4_fit_check_after_priority_updates.json", after_summary)
    md = build_after_check_markdown(after_summary)
    (OUTPUT_DIR / "schema_v1_4_fit_check_after_priority_updates.md").write_text(md, encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
