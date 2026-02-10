from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "00_整理记录"
if not OUTPUT_DIR.exists():
    OUTPUT_DIR = PROJECT_ROOT / "00_鏁寸悊璁板綍"

DOC_KEYS = [
    "title",
    "document_no",
    "issue_date",
    "effective_start_date",
    "effective_end_date",
    "org_name",
    "region_name",
    "target_name",
]

CLAUSE_KEYS = [
    "mechanism_type",
    "mechanism_name",
    "clause_type",
    "raw_value",
    "raw_unit",
    "direction",
    "condition_text",
    "task_subject",
    "task_action",
    "task_deadline",
    "task_assessment",
]

LOW_CONF_SOURCES = {"fallback_clause_type_lowconf", "rule_context_neighbor_lowconf"}
CN_NUM_RE = re.compile(r"[零〇一二三四五六七八九十百千万两壹贰叁肆伍陆柒捌玖拾佰仟]")
CN_PERCENT_RE = re.compile(r"\u767e\u5206\u4e4b[零〇一二三四五六七八九十百千万两\d\.]+")
TIME_RANGE_RE = re.compile(r"\d{1,2}:\d{2}\s*[-~\u81f3]\s*\d{1,2}:\d{2}")
RATIO_RE = re.compile(r"\d+(?:\.\d+)?\s*:\s*\d+(?:\.\d+)?(?:\s*:\s*\d+(?:\.\d+)?)?")


def read_jsonl(path: Path) -> List[Dict]:
    rows: List[Dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def pct(num: int, den: int) -> float:
    return float(num) / float(den) if den > 0 else 0.0


def is_numeric_like_text(text: str) -> bool:
    if not text:
        return False
    return bool(
        re.search(r"\d", text)
        or CN_NUM_RE.search(text)
        or CN_PERCENT_RE.search(text)
        or TIME_RANGE_RE.search(text)
        or RATIO_RE.search(text)
    )


def span_is_valid(item: Dict, text: str) -> bool:
    st = item.get("start")
    ed = item.get("end")
    val = str(item.get("text", ""))
    if st is None or ed is None:
        return False
    if not isinstance(st, int) or not isinstance(ed, int):
        return False
    if st < 0 or ed < st or ed > len(text):
        return False
    return text[st:ed] == val


def mechanism_evidence_is_valid(item: Dict, row: Dict, text: str) -> bool:
    if span_is_valid(item, text):
        return True
    source = str(item.get("source", ""))
    if source.startswith("fallback_clause_type"):
        return True
    if source == "rule_pattern":
        st = item.get("start")
        ed = item.get("end")
        pf = row.get("postfill") or {}
        kw = pf.get("mechanism_keyword")
        kw_st = pf.get("mechanism_keyword_start")
        kw_ed = pf.get("mechanism_keyword_end")
        if (
            isinstance(st, int)
            and isinstance(ed, int)
            and isinstance(kw_st, int)
            and isinstance(kw_ed, int)
            and st == kw_st
            and ed == kw_ed
            and 0 <= st <= ed <= len(text)
            and isinstance(kw, str)
            and text[st:ed] == kw
        ):
            return True
    if source.startswith("rule_context_neighbor"):
        pf = row.get("postfill") or {}
        return bool(pf.get("mechanism_context_anchor_clause_id"))
    return False


def top_mechanism_item(items: List[Dict]) -> Dict | None:
    if not items:
        return None
    return sorted(items, key=lambda x: float(x.get("probability", 0.0)), reverse=True)[0]


def score_kb(metrics: Dict) -> Dict:
    structure_score = 20.0 * (0.5 * metrics["parse_ok_rate"] + 0.5 * metrics["schema_key_complete_rate"])
    evidence_score = 20.0 * (0.5 * metrics["raw_value_span_valid_rate"] + 0.5 * metrics["mechanism_evidence_rate"])
    doc_score = 15.0 * (0.7 * metrics["doc_min_ready_rate"] + 0.3 * metrics["doc_rich_ready_rate"])
    clause_score = 45.0 * (
        0.2 * metrics["mechanism_non_empty_rate"]
        + 0.1 * metrics["clause_type_non_empty_rate"]
        + 0.3 * metrics["strict_triplet_ready_rate"]
        + 0.2 * metrics["param_bind_rate"]
        + 0.2 * metrics["task_ready_rate"]
    )
    clause_score_high_conf = 45.0 * (
        0.2 * metrics["mechanism_non_empty_rate_high_conf"]
        + 0.1 * metrics["clause_type_non_empty_rate"]
        + 0.3 * metrics["strict_triplet_ready_rate_high_conf"]
        + 0.2 * metrics["param_bind_rate"]
        + 0.2 * metrics["task_ready_rate"]
    )
    return {
        "structure_score": round(structure_score, 3),
        "evidence_score": round(evidence_score, 3),
        "doc_score": round(doc_score, 3),
        "clause_score": round(clause_score, 3),
        "total_score": round(structure_score + evidence_score + doc_score + clause_score, 3),
        "clause_score_high_conf": round(clause_score_high_conf, 3),
        "total_score_high_conf": round(structure_score + evidence_score + doc_score + clause_score_high_conf, 3),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score Step4 KB import readiness.")
    parser.add_argument("--doc-pred-file", type=str, default="00_整理记录/step4_gpu_doc_doc_predictions.jsonl")
    parser.add_argument("--clause-pred-file", type=str, default="00_整理记录/step4_gpu_clause_clause_predictions.jsonl")
    parser.add_argument("--clause-source-file", type=str, default="00_整理记录/step3_clause_corpus.jsonl")
    parser.add_argument("--output-prefix", type=str, default="step4_kb_baseline")
    parser.add_argument("--good-threshold", type=float, default=75.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    doc_rows = read_jsonl(PROJECT_ROOT / args.doc_pred_file)
    clause_rows = read_jsonl(PROJECT_ROOT / args.clause_pred_file)
    clause_source_rows = read_jsonl(PROJECT_ROOT / args.clause_source_file)
    clause_text_map = {x["clause_id"]: x.get("clause_text", "") for x in clause_source_rows}

    doc_parse_ok = 0
    doc_key_ok = 0
    for row in doc_rows:
        pred = row.get("prediction")
        if isinstance(pred, dict):
            doc_parse_ok += 1
            if all(k in pred for k in DOC_KEYS):
                doc_key_ok += 1

    clause_parse_ok = 0
    clause_key_ok = 0
    raw_item_total = 0
    raw_item_span_ok = 0
    mech_item_total = 0
    mech_item_evidence_ok = 0
    mechanism_non_empty = 0
    mechanism_non_empty_high_conf = 0
    low_conf_mechanism_clause = 0
    clause_type_non_empty = 0
    raw_non_empty = 0
    raw_numeric_clause = 0
    task_ready = 0
    bind_true = 0
    bind_total = 0
    strict_all_ready = 0
    strict_high_conf_ready = 0

    for row in clause_rows:
        pred = row.get("prediction")
        if not isinstance(pred, dict):
            continue
        clause_parse_ok += 1
        if all(k in pred for k in CLAUSE_KEYS):
            clause_key_ok += 1

        text = clause_text_map.get(row.get("clause_id"), "")
        mech_items = pred.get("mechanism_type", []) or []
        raw_items = pred.get("raw_value", []) or []
        task_items = (
            (pred.get("task_subject", []) or [])
            + (pred.get("task_action", []) or [])
            + (pred.get("task_deadline", []) or [])
            + (pred.get("task_assessment", []) or [])
        )

        top_mech = top_mechanism_item(mech_items)
        top_source = str((top_mech or {}).get("source", ""))
        mech_is_high_conf = bool(mech_items) and (top_source not in LOW_CONF_SOURCES)
        if mech_items:
            mechanism_non_empty += 1
            if mech_is_high_conf:
                mechanism_non_empty_high_conf += 1
            else:
                low_conf_mechanism_clause += 1
        if pred.get("clause_type"):
            clause_type_non_empty += 1
        if raw_items:
            raw_non_empty += 1
            has_numeric = any(is_numeric_like_text(str(x.get("text", ""))) for x in raw_items)
            if has_numeric:
                raw_numeric_clause += 1
            bind_total += 1
            if (row.get("postfill") or {}).get("param_bind_mechanism") is True:
                bind_true += 1
        if task_items:
            task_ready += 1

        if mech_items and pred.get("clause_type") and raw_items:
            has_numeric = any(is_numeric_like_text(str(x.get("text", ""))) for x in raw_items)
            if has_numeric:
                strict_all_ready += 1
                if mech_is_high_conf:
                    strict_high_conf_ready += 1

        for item in raw_items:
            raw_item_total += 1
            if span_is_valid(item, text):
                raw_item_span_ok += 1
        for item in mech_items:
            mech_item_total += 1
            if mechanism_evidence_is_valid(item, row, text):
                mech_item_evidence_ok += 1

    doc_total = len(doc_rows)
    clause_total = len(clause_rows)
    parse_ok_rate = pct(doc_parse_ok + clause_parse_ok, doc_total + clause_total)
    schema_key_complete_rate = pct(doc_key_ok + clause_key_ok, doc_total + clause_total)
    raw_value_span_valid_rate = pct(raw_item_span_ok, raw_item_total)
    mechanism_evidence_rate = pct(mech_item_evidence_ok, mech_item_total)

    doc_min_ready = 0
    doc_rich_ready = 0
    for row in doc_rows:
        pred = row.get("prediction", {})
        if not isinstance(pred, dict):
            continue
        if pred.get("issue_date") or pred.get("org_name") or pred.get("effective_start_date"):
            doc_min_ready += 1
        if pred.get("issue_date") and pred.get("org_name"):
            doc_rich_ready += 1

    metrics = {
        "doc_total": doc_total,
        "clause_total": clause_total,
        "parse_ok_rate": round(parse_ok_rate, 6),
        "schema_key_complete_rate": round(schema_key_complete_rate, 6),
        "raw_value_span_valid_rate": round(raw_value_span_valid_rate, 6),
        "mechanism_evidence_rate": round(mechanism_evidence_rate, 6),
        "doc_min_ready_rate": round(pct(doc_min_ready, doc_total), 6),
        "doc_rich_ready_rate": round(pct(doc_rich_ready, doc_total), 6),
        "mechanism_non_empty_rate": round(pct(mechanism_non_empty, clause_total), 6),
        "mechanism_non_empty_rate_high_conf": round(pct(mechanism_non_empty_high_conf, clause_total), 6),
        "low_conf_mechanism_clause_rate": round(pct(low_conf_mechanism_clause, clause_total), 6),
        "clause_type_non_empty_rate": round(pct(clause_type_non_empty, clause_total), 6),
        "raw_non_empty_rate": round(pct(raw_non_empty, clause_total), 6),
        "raw_numeric_rate_among_raw": round(pct(raw_numeric_clause, raw_non_empty), 6),
        "task_ready_rate": round(pct(task_ready, clause_total), 6),
        "param_bind_rate": round(pct(bind_true, bind_total), 6),
        "strict_triplet_ready_rate": round(pct(strict_all_ready, clause_total), 6),
        "strict_triplet_ready_rate_all": round(pct(strict_all_ready, clause_total), 6),
        "strict_triplet_ready_rate_high_conf": round(pct(strict_high_conf_ready, clause_total), 6),
        "counts": {
            "mechanism_non_empty": mechanism_non_empty,
            "mechanism_non_empty_high_conf": mechanism_non_empty_high_conf,
            "low_conf_mechanism_clause": low_conf_mechanism_clause,
            "clause_type_non_empty": clause_type_non_empty,
            "raw_non_empty": raw_non_empty,
            "raw_numeric_clause": raw_numeric_clause,
            "task_ready": task_ready,
            "param_bind_true": bind_true,
            "param_bind_total_raw_clause": bind_total,
            "strict_triplet_ready": strict_all_ready,
            "strict_triplet_ready_high_conf": strict_high_conf_ready,
            "raw_item_total": raw_item_total,
            "raw_item_span_ok": raw_item_span_ok,
            "mechanism_item_total": mech_item_total,
            "mechanism_item_evidence_ok": mech_item_evidence_ok,
        },
    }
    scores = score_kb(metrics)
    result = {"metrics": metrics, "scores": scores, "good_threshold": args.good_threshold, "is_good": scores["total_score"] >= args.good_threshold}

    out_json = OUTPUT_DIR / f"{args.output_prefix}_kb_score.json"
    out_md = OUTPUT_DIR / f"{args.output_prefix}_kb_score.md"
    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# {args.output_prefix} KB Readiness Score",
        "",
        f"- total_score: {scores['total_score']}",
        f"- total_score_high_conf: {scores['total_score_high_conf']}",
        f"- clause_score: {scores['clause_score']}",
        f"- clause_score_high_conf: {scores['clause_score_high_conf']}",
        f"- good_threshold: {args.good_threshold}",
        f"- is_good: {result['is_good']}",
        "",
        "## Key Metrics",
        f"- mechanism_non_empty_rate: {metrics['mechanism_non_empty_rate']}",
        f"- mechanism_non_empty_rate_high_conf: {metrics['mechanism_non_empty_rate_high_conf']}",
        f"- low_conf_mechanism_clause_rate: {metrics['low_conf_mechanism_clause_rate']}",
        f"- raw_non_empty_rate: {metrics['raw_non_empty_rate']}",
        f"- strict_triplet_ready_rate_all: {metrics['strict_triplet_ready_rate_all']}",
        f"- strict_triplet_ready_rate_high_conf: {metrics['strict_triplet_ready_rate_high_conf']}",
        f"- param_bind_rate: {metrics['param_bind_rate']}",
        f"- task_ready_rate: {metrics['task_ready_rate']}",
        "",
        "## Artifacts",
        f"- `{out_json.relative_to(PROJECT_ROOT).as_posix()}`",
    ]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("score done")


if __name__ == "__main__":
    main()

