#!/usr/bin/env python3
"""
Build submission-ready tables and figure guide for the paper.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List


REPO_ROOT = Path(__file__).resolve().parents[2]
RECORD_DIR = REPO_ROOT / "00_整理记录"
RESULT_DIR = REPO_ROOT / "结果文件夹"


def read_json(path: Path) -> Dict:
    text = path.read_text(encoding="utf-8-sig")
    return json.loads(text)


def write_csv(path: Path, rows: List[Dict], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in fieldnames})


def to_markdown_table(rows: List[Dict], columns: List[str]) -> str:
    lines = []
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("|" + "|".join(["---"] * len(columns)) + "|")
    for r in rows:
        vals = [str(r.get(c, "")) for c in columns]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def build_tables(output_dir: Path) -> List[Path]:
    out_paths: List[Path] = []

    step1 = read_json(RECORD_DIR / "policy_readthrough_summary.json")
    step3 = read_json(RECORD_DIR / "step3_qc_report.json")
    step4_iter = read_json(RECORD_DIR / "step4_iteration_scores.json")
    step5_main = read_json(RECORD_DIR / "step5_seq_step2_v2_rebind14_fixabcd_plus2_validation_report.json")
    step5_ablation = read_json(RECORD_DIR / "step5_ablation_norebind99_validation_report.json")
    step6 = read_json(RECORD_DIR / "step6_iter4_fixabcd_plus_iaa_report.json")
    step7 = read_json(RECORD_DIR / "step7_gate_iter3_final.json")
    step7_year = read_json(RECORD_DIR / "step7_cross_year_robustness_report.json")
    step8_stats = read_json(RESULT_DIR / "step8_iter1" / "stats.json")
    step8_val = read_json(RESULT_DIR / "step8_iter1" / "validation_report.json")
    step8_2 = read_json(RESULT_DIR / "step8_2_iter1" / "step8_2_eval_report.json")
    step9_gate = read_json(RECORD_DIR / "step9_iter1" / "step9_gate_report.json")
    step9_query = read_json(RECORD_DIR / "step9_iter1" / "step9_query_exec_report.json")
    step12 = read_json(RECORD_DIR / "step12_cost_profile_report.json")
    step14_path = RECORD_DIR / "step14_error_profile_report.json"
    step14 = read_json(step14_path) if step14_path.exists() else None
    step15_path = RECORD_DIR / "step15_baseline_comparison.json"
    step15 = read_json(step15_path) if step15_path.exists() else None
    step17_path = RECORD_DIR / "step17_perf_latency_report.json"
    step17 = read_json(step17_path) if step17_path.exists() else None
    step18_path = RECORD_DIR / "step18_annotation_protocol_detail.json"
    step18 = read_json(step18_path) if step18_path.exists() else None

    # Table 01: pipeline overview
    t1_rows = [
        {"stage": "Step1", "metric": "file_total", "value": step1.get("file_count"), "source": "policy_readthrough_summary.json"},
        {"stage": "Step3", "metric": "document_units", "value": step3.get("unit_document_count"), "source": "step3_qc_report.json"},
        {"stage": "Step3", "metric": "clause_total", "value": (step3.get("clause_qc") or {}).get("clause_total"), "source": "step3_qc_report.json"},
        {"stage": "Step4", "metric": "iter3_total_score", "value": next(x["total_score"] for x in step4_iter if x["iteration"] == "iter3_v2plus"), "source": "step4_iteration_scores.json"},
        {"stage": "Step5", "metric": "normalization_matched_rate", "value": step5_main["rates"]["normalization_matched_rate"], "source": "step5_seq_step2_v2_rebind14_fixabcd_plus2_validation_report.json"},
        {"stage": "Step6", "metric": "kappa_mechanism", "value": step6["iaa"]["kappa_mechanism"], "source": "step6_iter4_fixabcd_plus_iaa_report.json"},
        {"stage": "Step7", "metric": "all_targets_passed", "value": step7["all_targets_passed"], "source": "step7_gate_iter3_final.json"},
        {"stage": "Step8", "metric": "deterministic_replay_match", "value": step8_val["checks"]["deterministic_replay_match"], "source": "step8_iter1/validation_report.json"},
        {"stage": "Step9", "metric": "query_execution_success_rate", "value": (step9_gate["snapshot"]["query"]["query_execution_success_rate"]), "source": "step9_iter1/step9_gate_report.json"},
    ]
    t1_path = output_dir / "table01_pipeline_overview.csv"
    write_csv(t1_path, t1_rows, ["stage", "metric", "value", "source"])
    out_paths.append(t1_path)

    # Table 02: step4 iterations
    t2_rows = []
    for r in step4_iter:
        t2_rows.append(
            {
                "iteration": r["iteration"],
                "total_score": r["total_score"],
                "structure_score": r["structure_score"],
                "evidence_score": r["evidence_score"],
                "doc_score": r["doc_score"],
                "clause_score": r["clause_score"],
                "strict_triplet_ready_rate": r["strict_triplet_ready_rate"],
                "param_bind_rate": r["param_bind_rate"],
                "is_good": r["is_good"],
            }
        )
    t2_path = output_dir / "table02_step4_iteration_scores.csv"
    write_csv(
        t2_path,
        t2_rows,
        [
            "iteration",
            "total_score",
            "structure_score",
            "evidence_score",
            "doc_score",
            "clause_score",
            "strict_triplet_ready_rate",
            "param_bind_rate",
            "is_good",
        ],
    )
    out_paths.append(t2_path)

    # Table 03: protocol gate thresholds vs observed
    s5 = step7["step5_snapshot"]
    s6 = step7["step6_snapshot"]
    err = step6["error_clusters"]
    t3_rows = [
        {"gate_item": "normalization_matched_rate", "threshold": ">=0.95", "observed": s5["normalization_matched_on_mentions"]["rate"], "pass": step7["target_pass"]["step5_normalization_matched_rate_ge_0_95"]},
        {"gate_item": "mechanism_bound_rate_valid_numeric", "threshold": "=1.0", "observed": s5["mechanism_bound_on_valid_numeric"]["rate"], "pass": step7["target_pass"]["step5_mechanism_bound_rate_valid_numeric_eq_1_0"]},
        {"gate_item": "strict_high_rate_valid_numeric", "threshold": ">=0.85", "observed": s5["strict_high_on_valid_numeric"]["rate"], "pass": step7["target_pass"]["step5_strict_high_rate_valid_numeric_ge_0_85"]},
        {"gate_item": "local_supported_rate_valid_numeric", "threshold": ">=0.85", "observed": s5["local_supported_rate_valid_numeric"], "pass": step7["target_pass"]["step5_local_supported_rate_valid_numeric_ge_0_85"]},
        {"gate_item": "kappa_mechanism", "threshold": ">=0.90", "observed": s6["iaa"]["kappa_mechanism"], "pass": step7["target_pass"]["step6_kappa_mechanism_ge_0_90"]},
        {"gate_item": "kappa_param_type", "threshold": ">=0.95", "observed": s6["iaa"]["kappa_param_type"], "pass": step7["target_pass"]["step6_kappa_param_type_ge_0_95"]},
        {"gate_item": "mechanism_precision_on_valid_numeric", "threshold": ">=0.95", "observed": s6["mechanism_precision_on_valid_numeric"]["rate"], "pass": step7["target_pass"]["step6_mechanism_precision_ge_0_95"]},
        {"gate_item": "normalization_precision_on_valid_numeric", "threshold": ">=0.995", "observed": s6["normalization_precision_on_valid_numeric"]["rate"], "pass": step7["target_pass"]["step6_normalization_precision_ge_0_995"]},
        {"gate_item": "strict_high_precision", "threshold": ">=0.992", "observed": s6["strict_high_precision"]["rate"], "pass": step7["target_pass"]["step6_strict_high_precision_ge_0_992"]},
        {"gate_item": "time_raw_not_time_window", "threshold": "=0", "observed": err["time_raw_not_time_window"], "pass": step7["target_pass"]["step6_hard_error_time_raw_not_time_window_eq_0"]},
        {"gate_item": "price_value_large_raw_small_norm", "threshold": "=0", "observed": err["price_value_large_raw_small_norm"], "pass": step7["target_pass"]["step6_hard_error_price_value_large_raw_small_norm_eq_0"]},
        {"gate_item": "candidate_score_strict_high", "threshold": "=0", "observed": err["candidate_score_strict_high"], "pass": step7["target_pass"]["step6_hard_error_candidate_score_strict_high_eq_0"]},
    ]
    t3_path = output_dir / "table03_protocol_gate_threshold_vs_observed.csv"
    write_csv(t3_path, t3_rows, ["gate_item", "threshold", "observed", "pass"])
    out_paths.append(t3_path)

    # Table 04: ablation
    iter0 = next(x for x in step4_iter if x["iteration"] == "iter0_baseline")
    iter3 = next(x for x in step4_iter if x["iteration"] == "iter3_v2plus")
    full_valid_all = step5_main["frozen_denominators"]["valid_all"]
    abl_valid_all = step5_ablation["frozen_denominators"]["valid_all"]
    full_strict_high_valid_all = step5_main["counts"]["strict_high_count"] / full_valid_all
    full_local_supported_valid_all = step5_main["counts"]["local_supported_count"] / full_valid_all
    abl_strict_high_valid_all = step5_ablation["counts"]["strict_high_count"] / abl_valid_all
    abl_local_supported_valid_all = step5_ablation["counts"]["local_supported_count"] / abl_valid_all

    t4_rows = [
        {
            "metric": "step4_total_score",
            "full_method": iter3["total_score"],
            "ablation": iter0["total_score"],
            "delta": round(iter3["total_score"] - iter0["total_score"], 6),
            "ablation_type": "Ablation-A_no_rule_postprocess",
        },
        {
            "metric": "step4_strict_triplet_ready_rate",
            "full_method": iter3["strict_triplet_ready_rate"],
            "ablation": iter0["strict_triplet_ready_rate"],
            "delta": round(iter3["strict_triplet_ready_rate"] - iter0["strict_triplet_ready_rate"], 6),
            "ablation_type": "Ablation-A_no_rule_postprocess",
        },
        {
            "metric": "step4_param_bind_rate",
            "full_method": iter3["param_bind_rate"],
            "ablation": iter0["param_bind_rate"],
            "delta": round(iter3["param_bind_rate"] - iter0["param_bind_rate"], 6),
            "ablation_type": "Ablation-A_no_rule_postprocess",
        },
        {
            "metric": "step5_mechanism_bound_rate_valid_all",
            "full_method": step5_main["rates"]["mechanism_bound_rate_valid_all"],
            "ablation": step5_ablation["rates"]["mechanism_bound_rate_valid_all"],
            "delta": round(step5_main["rates"]["mechanism_bound_rate_valid_all"] - step5_ablation["rates"]["mechanism_bound_rate_valid_all"], 6),
            "ablation_type": "Ablation-B_bind_min_score_99",
        },
        {
            "metric": "step5_strict_high_rate_valid_all",
            "full_method": round(full_strict_high_valid_all, 6),
            "ablation": round(abl_strict_high_valid_all, 6),
            "delta": round(full_strict_high_valid_all - abl_strict_high_valid_all, 6),
            "ablation_type": "Ablation-B_bind_min_score_99",
        },
        {
            "metric": "step5_local_supported_rate_valid_all",
            "full_method": round(full_local_supported_valid_all, 6),
            "ablation": round(abl_local_supported_valid_all, 6),
            "delta": round(full_local_supported_valid_all - abl_local_supported_valid_all, 6),
            "ablation_type": "Ablation-B_bind_min_score_99",
        },
        {
            "metric": "step5_all_targets_passed",
            "full_method": step5_main["all_targets_passed"],
            "ablation": step5_ablation["all_targets_passed"],
            "delta": "",
            "ablation_type": "Ablation-B_bind_min_score_99",
        },
    ]
    t4_path = output_dir / "table04_ablation_results.csv"
    write_csv(t4_path, t4_rows, ["ablation_type", "metric", "full_method", "ablation", "delta"])
    out_paths.append(t4_path)

    # Table 05: cross-year robustness
    t5_rows = list(step7_year["rows"])
    t5_path = output_dir / "table05_cross_year_robustness.csv"
    write_csv(
        t5_path,
        t5_rows,
        [
            "year",
            "mention_total",
            "valid_all",
            "valid_numeric",
            "normalization_matched_rate_on_valid_all",
            "mechanism_bound_rate_valid_all",
            "strict_high_rate_valid_all",
            "mechanism_bound_rate_valid_numeric",
            "strict_high_rate_valid_numeric",
        ],
    )
    out_paths.append(t5_path)

    # Table 06: cost profile (benchmark)
    t6_rows = []
    for b in step12.get("benchmarks", []):
        t6_rows.append(
            {
                "benchmark_id": b.get("id"),
                "elapsed_sec": b.get("elapsed_sec"),
                "return_code": b.get("return_code"),
                "command": b.get("command"),
            }
        )
    t6_path = output_dir / "table06_cost_profile_benchmarks.csv"
    write_csv(t6_path, t6_rows, ["benchmark_id", "elapsed_sec", "return_code", "command"])
    out_paths.append(t6_path)

    # Table 07: query template execution
    t7_rows = []
    for q in step9_query["query_eval"]:
        t7_rows.append(
            {
                "query_id": q.get("query_id"),
                "title": q.get("title"),
                "path_tag": q.get("path_tag"),
                "executed_successfully": q.get("executed_successfully"),
                "result_count": q.get("result_count"),
                "error": q.get("error"),
            }
        )
    t7_path = output_dir / "table07_query_template_execution.csv"
    write_csv(t7_path, t7_rows, ["query_id", "title", "path_tag", "executed_successfully", "result_count", "error"])
    out_paths.append(t7_path)

    # Table 08: graph package and DB metrics
    t8_rows = [
        {"metric": "strict_high_nodes", "value": step8_stats["strict_high"]["node_count"], "source": "step8_iter1/stats.json"},
        {"metric": "strict_high_edges", "value": step8_stats["strict_high"]["edge_count"], "source": "step8_iter1/stats.json"},
        {"metric": "strict_all_nodes", "value": step8_stats["strict_all"]["node_count"], "source": "step8_iter1/stats.json"},
        {"metric": "strict_all_edges", "value": step8_stats["strict_all"]["edge_count"], "source": "step8_iter1/stats.json"},
        {"metric": "deterministic_replay_match", "value": step8_val["checks"]["deterministic_replay_match"], "source": "step8_iter1/validation_report.json"},
        {"metric": "query_template_count", "value": step8_2["metrics"]["query_template_count"], "source": "step8_2_iter1/step8_2_eval_report.json"},
        {"metric": "query_execution_success_rate", "value": step8_2["metrics"]["query_execution_success_rate"], "source": "step8_2_iter1/step8_2_eval_report.json"},
        {"metric": "core_path_coverage", "value": step9_gate["snapshot"]["query"]["core_path_coverage"], "source": "step9_iter1/step9_gate_report.json"},
        {"metric": "neo4j_node_total", "value": step9_gate["snapshot"]["import"]["node_total"], "source": "step9_iter1/step9_gate_report.json"},
        {"metric": "neo4j_edge_total", "value": step9_gate["snapshot"]["import"]["edge_total"], "source": "step9_iter1/step9_gate_report.json"},
    ]
    t8_path = output_dir / "table08_graph_and_db_metrics.csv"
    write_csv(t8_path, t8_rows, ["metric", "value", "source"])
    out_paths.append(t8_path)

    # Table 09: error/risk profile (optional, if step14 exists)
    if step14 is not None:
        t9_rows: List[Dict] = []
        for k, v in step14.get("hard_error_buckets", {}).items():
            t9_rows.append({"category": "hard_error_bucket", "item": k, "value": v})
        for k, v in step14.get("conflict_summary", {}).get("conflict_type_distribution", {}).items():
            t9_rows.append({"category": "conflict_type_distribution", "item": k, "value": v})
        for k, v in step14.get("threshold_margins", {}).items():
            t9_rows.append({"category": "threshold_margin", "item": k, "value": v})
        t9_path = output_dir / "table09_error_risk_profile.csv"
        write_csv(t9_path, t9_rows, ["category", "item", "value"])
        out_paths.append(t9_path)

    # Table 10: external baseline comparison (optional)
    if step15 is not None:
        t10_rows = step15.get("rows", [])
        t10_path = output_dir / "table10_external_baseline_comparison.csv"
        write_csv(
            t10_path,
            t10_rows,
            [
                "baseline",
                "binding_mode",
                "disable_strict_high_guards",
                "valid_all",
                "valid_numeric",
                "normalization_matched_rate",
                "mechanism_bound_rate_valid_all",
                "strict_high_rate_valid_all",
                "local_supported_rate_valid_all",
                "all_targets_passed",
            ],
        )
        out_paths.append(t10_path)

    # Table 11: query latency by template (optional)
    if step17 is not None:
        t11_rows = step17.get("query_latency_by_template", [])
        t11_path = output_dir / "table11_query_latency_by_template.csv"
        write_csv(
            t11_path,
            t11_rows,
            [
                "query_id",
                "title",
                "repeat",
                "success_runs",
                "error_runs",
                "result_count_median",
                "latency_ms_p50",
                "latency_ms_p95",
                "latency_ms_mean",
            ],
        )
        out_paths.append(t11_path)

    # Table 12: annotation protocol detail (optional)
    if step18 is not None:
        iaa = step18.get("iaa_metrics", {})
        q = step18.get("quality_metrics", {})
        t12_rows = [
            {"metric": "blind_annotators", "value": step18.get("role_layout", {}).get("blind_annotators")},
            {"metric": "adjudication_stage", "value": step18.get("role_layout", {}).get("adjudication_stage")},
            {"metric": "sample_total", "value": step18.get("sample_counts", {}).get("sample_v1_count")},
            {"metric": "strict_high_count", "value": step18.get("sampling_structure", {}).get("strict_high_count")},
            {"metric": "hard_case_count", "value": step18.get("sampling_structure", {}).get("hard_case_count")},
            {"metric": "kappa_mechanism", "value": iaa.get("kappa_mechanism")},
            {"metric": "kappa_param_type", "value": iaa.get("kappa_param_type")},
            {"metric": "mechanism_precision_on_valid_numeric", "value": (q.get("mechanism_precision_on_valid_numeric") or {}).get("rate")},
            {"metric": "normalization_precision_on_valid_numeric", "value": (q.get("normalization_precision_on_valid_numeric") or {}).get("rate")},
            {"metric": "strict_high_precision", "value": (q.get("strict_high_precision") or {}).get("rate")},
        ]
        t12_path = output_dir / "table12_annotation_protocol_summary.csv"
        write_csv(t12_path, t12_rows, ["metric", "value"])
        out_paths.append(t12_path)

    # Figure guide and README
    figure_guide = output_dir / "FIGURE_GUIDE.md"
    figure_guide.write_text(
        "\n".join(
            [
                "# 投稿图件指引",
                "",
                "## Figure 1: Step1-Step9 闭环总览",
                "- 数据来源: `table01_pipeline_overview.csv`",
                "- 建议图型: 分阶段流程图 + 关键指标注释",
                "",
                "## Figure 2: Step4 迭代提升曲线",
                "- 数据来源: `table02_step4_iteration_scores.csv`",
                "- 建议图型: 折线图（total_score, strict_triplet_ready_rate, param_bind_rate）",
                "",
                "## Figure 3: 门禁协议通过矩阵",
                "- 数据来源: `table03_protocol_gate_threshold_vs_observed.csv`",
                "- 建议图型: 热力表/对勾矩阵",
                "",
                "## Figure 4: 消融对比",
                "- 数据来源: `table04_ablation_results.csv`",
                "- 建议图型: 分组柱状图",
                "",
                "## Figure 5: 跨年份稳健性",
                "- 数据来源: `table05_cross_year_robustness.csv`",
                "- 建议图型: 多折线图（norm/mec_bound/strict_high）",
                "",
                "## Figure 6: 运行成本画像",
                "- 数据来源: `table06_cost_profile_benchmarks.csv`, `00_整理记录/step12_cost_profile_report.json`",
                "- 建议图型: 条形图（脚本耗时）+ 表格（产物体量）",
                "",
                "## Figure 7: 查询模板执行覆盖",
                "- 数据来源: `table07_query_template_execution.csv`",
                "- 建议图型: 条形图（result_count）+ 成功率摘要",
                "",
                "## Figure 8: 图包与数据库规模",
                "- 数据来源: `table08_graph_and_db_metrics.csv`",
                "- 建议图型: 对比柱状图（strict_high vs strict_all vs neo4j totals）",
                "",
                "## Figure 9: 错误与风险画像",
                "- 数据来源: `table09_error_risk_profile.csv`, `00_整理记录/step14_error_profile_report.md`",
                "- 建议图型: 风险雷达图/门禁余量条形图",
                "",
                "## Figure 10: 外部基线对照",
                "- 数据来源: `table10_external_baseline_comparison.csv`",
                "- 建议图型: 分组柱状图（strict_high/local_supported）",
                "",
                "## Figure 11: 查询延迟分布",
                "- 数据来源: `table11_query_latency_by_template.csv`",
                "- 建议图型: 每模板 P50/P95 误差条",
                "",
                "## Figure 12: 标注流程与一致性",
                "- 数据来源: `table12_annotation_protocol_summary.csv`",
                "- 建议图型: 流程图 + 指标卡片",
                "",
            ]
        ),
        encoding="utf-8",
    )
    out_paths.append(figure_guide)

    # README
    readme = output_dir / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# 投稿版图表包",
                "",
                "本目录用于论文投稿阶段直接引用的数据表与图件指引。",
                "",
                "## 文件清单",
                "- `table01_pipeline_overview.csv`：Step1-Step9 关键指标总览",
                "- `table02_step4_iteration_scores.csv`：Step4 迭代评分明细",
                "- `table03_protocol_gate_threshold_vs_observed.csv`：门禁阈值与实测对比",
                "- `table04_ablation_results.csv`：最小消融结果",
                "- `table05_cross_year_robustness.csv`：跨年份稳健性",
                "- `table06_cost_profile_benchmarks.csv`：成本画像耗时",
                "- `table07_query_template_execution.csv`：查询模板执行统计",
                "- `table08_graph_and_db_metrics.csv`：图包与数据库规模指标",
                "- `table09_error_risk_profile.csv`：错误与风险画像（若已生成 Step14）",
                "- `table10_external_baseline_comparison.csv`：外部基线同口径对照（若已生成 Step15）",
                "- `table11_query_latency_by_template.csv`：查询延迟 P50/P95（若已生成 Step17）",
                "- `table12_annotation_protocol_summary.csv`：标注流程与一致性摘要（若已生成 Step18）",
                "- `FIGURE_GUIDE.md`：建议图件映射与绘图指引",
                "",
                "## 生成方式",
                "```bash",
                "python3 00_整理记录/scripts/build_step13_submission_tables.py",
                "```",
            ]
        ),
        encoding="utf-8",
    )
    out_paths.append(readme)

    # Summary markdown for quick copy into paper appendix.
    summary_md = output_dir / "APPENDIX_TABLE_SUMMARY.md"
    summary_sections: List[str] = ["# 附录表格摘要", ""]
    summary_sections.append("## 表3 门禁阈值与实测（摘录）")
    summary_sections.append(to_markdown_table(t3_rows[:8], ["gate_item", "threshold", "observed", "pass"]))
    summary_sections.append("")
    summary_sections.append("## 表4 消融结果（摘录）")
    summary_sections.append(to_markdown_table(t4_rows, ["ablation_type", "metric", "full_method", "ablation", "delta"]))
    summary_sections.append("")
    summary_sections.append("## 表6 成本画像（摘录）")
    summary_sections.append(to_markdown_table(t6_rows, ["benchmark_id", "elapsed_sec", "return_code"]))
    summary_md.write_text("\n".join(summary_sections) + "\n", encoding="utf-8")
    out_paths.append(summary_md)

    return out_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build submission-ready table pack.")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="结果文件夹/投稿版图表包",
        help="Output directory for submission table pack.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = (REPO_ROOT / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = build_tables(output_dir)
    print(
        json.dumps(
            {
                "output_dir": str(output_dir.relative_to(REPO_ROOT)),
                "file_count": len(outputs),
                "files": [str(p.relative_to(REPO_ROOT)) for p in outputs],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
