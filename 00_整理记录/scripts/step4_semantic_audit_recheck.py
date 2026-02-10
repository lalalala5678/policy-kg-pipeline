from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "00_整理记录"
if not OUTPUT_DIR.exists():
    OUTPUT_DIR = PROJECT_ROOT / "00_鏁寸悊璁板綍"


LOW_CONF_SOURCES = {"fallback_clause_type_lowconf", "rule_context_neighbor_lowconf"}
HIGH_CONF_RULE_SOURCES = {"rule_pattern", "rule_pattern_ext", "rule_numeric_keyword", "rule_context_neighbor"}


CN_NUM_RE = re.compile(r"[零〇一二三四五六七八九十百千万两壹贰叁肆伍陆柒捌玖拾佰仟]")
CN_PERCENT_RE = re.compile(r"\u767e\u5206\u4e4b[零〇一二三四五六七八九十百千万两\d\.]+")
TIME_RANGE_RE = re.compile(r"\d{1,2}:\d{2}\s*[-~\u81f3]\s*\d{1,2}:\d{2}")
RATIO_RE = re.compile(r"\d+(?:\.\d+)?\s*:\s*\d+(?:\.\d+)?(?:\s*:\s*\d+(?:\.\d+)?)?")


MECH_HINTS = {
    "tou_pricing": re.compile(
        r"\u5206\u65f6|\u5cf0\u8c37|\u5cf0\u5e73\u8c37|\u5cf0\u6bb5|\u8c37\u6bb5|\u5c16\u5cf0|\u5e73\u6bb5|\u65f6\u6bb5|"
        r"\d{1,2}:\d{2}\s*[-~\u81f3]\s*\d{1,2}:\d{2}|"
        r"\d+(?:\.\d+)?\s*:\s*\d+(?:\.\d+)?(?:\s*:\s*\d+(?:\.\d+)?)?"
    ),
    "tiered_pricing": re.compile(r"\u9636\u68af|\u6863\u4f4d|\u5206\u6863|\u4e00\u6863|\u4e8c\u6863|\u4e09\u6863"),
    "differential_penalty_pricing": re.compile(r"\u5dee\u522b\u7535\u4ef7|\u60e9\u7f5a|\u9650\u5236\u7c7b|\u6dd8\u6c70\u7c7b"),
    "general_price_adjustment": re.compile(r"\u4e0a\u6d6e|\u4e0b\u6d6e|\u4e0a\u8c03|\u4e0b\u8c03|\u52a0\u4ef7|\u964d\u4ef7|\u8c03\u6574\u7535\u4ef7|\u7535\u4ef7"),
    "subsidy": re.compile(r"\u8865\u8d34|\u8865\u52a9|\u5956\u52b1|\u5956\u8865|\u8865\u507f|\u6bcf\u6237\u6bcf\u5e74|\u4f4e\u4fdd|\u4e94\u4fdd"),
    "task_assessment": re.compile(r"\u4efb\u52a1|\u76ee\u6807|\u8003\u6838|\u9a8c\u6536|\u63a8\u8fdb|\u8d23\u4efb"),
    "technology_route": re.compile(r"\u7535\u80fd\u66ff\u4ee3|\u6e05\u6d01\u53d6\u6696|\u7164\u6539\u7535|\u5cb8\u7535"),
}


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() == "true"


def is_numeric_like(text: str) -> bool:
    if not text:
        return False
    return bool(
        re.search(r"\d", text)
        or CN_NUM_RE.search(text)
        or CN_PERCENT_RE.search(text)
        or TIME_RANGE_RE.search(text)
        or RATIO_RE.search(text)
    )


def source_bucket(source: str) -> str:
    if source in LOW_CONF_SOURCES:
        return "lowconf"
    if source in HIGH_CONF_RULE_SOURCES:
        return "rule_highconf"
    if source.startswith("fallback_clause_type"):
        return "fallback_other"
    if source in ("", "uie"):
        return "uie_or_empty"
    return "other"


def independent_check(row: Dict[str, str]) -> Tuple[bool, Dict[str, bool]]:
    mechanism_type = row.get("mechanism_type", "")
    mechanism_source = row.get("mechanism_source", "")
    clause_text = row.get("clause_text", "")
    raw_value = row.get("raw_value_top", "")
    raw_unit = row.get("raw_unit_top", "")

    hint_re = MECH_HINTS.get(mechanism_type)
    mechanism_hint_hit = bool(hint_re.search(clause_text)) if hint_re else False
    raw_numeric_hit = is_numeric_like(raw_value) or is_numeric_like(clause_text)
    raw_unit_hit = bool(raw_unit.strip())

    # Independent decision:
    # 1) high-conf rule sources can pass with numeric value even when wording is concise
    # 2) lowconf sources must satisfy explicit mechanism hint in text
    if mechanism_source in LOW_CONF_SOURCES:
        indep_pass = raw_numeric_hit and mechanism_hint_hit
    else:
        indep_pass = raw_numeric_hit and (mechanism_hint_hit or mechanism_source in HIGH_CONF_RULE_SOURCES or raw_unit_hit)

    detail = {
        "mechanism_hint_hit": mechanism_hint_hit,
        "raw_numeric_hit": raw_numeric_hit,
        "raw_unit_hit": raw_unit_hit,
    }
    return indep_pass, detail


def calc_kappa(tp: int, tn: int, fp: int, fn: int) -> float:
    total = tp + tn + fp + fn
    if total == 0:
        return 0.0
    p0 = (tp + tn) / total
    pa = ((tp + fp) / total) * ((tp + fn) / total)
    pb = ((fn + tn) / total) * ((fp + tn) / total)
    pe = pa + pb
    if pe >= 1.0:
        return 0.0
    return (p0 - pe) / (1.0 - pe)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recheck validity of step4 semantic auto-audit sample.")
    parser.add_argument("--sample-file", type=str, default="00_整理记录/step4_seq_semantic_audit_sample.csv")
    parser.add_argument("--output-prefix", type=str, default="step4_seq_semantic_audit_recheck")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sample_path = PROJECT_ROOT / args.sample_file
    rows = list(csv.DictReader(sample_path.open("r", encoding="utf-8-sig", newline="")))

    required = {
        "sample_id",
        "clause_id",
        "mechanism_type",
        "mechanism_source",
        "source_bucket",
        "raw_value_top",
        "auto_mechanism_hint_hit",
        "auto_raw_numeric_hit",
        "auto_semantic_pass",
        "clause_text",
    }
    missing_columns = sorted(list(required - set(rows[0].keys()))) if rows else sorted(list(required))

    unique_clause_ids = len({x.get("clause_id") for x in rows})
    duplicate_clause_count = len(rows) - unique_clause_ids
    empty_text_rows = sum(1 for x in rows if not str(x.get("clause_text", "")).strip())

    logic_mismatch = 0
    logic_mismatch_ids: List[str] = []
    confusion = Counter()
    by_bucket = defaultdict(lambda: {"n": 0, "auto_true": 0, "indep_true": 0, "agree": 0})
    disagreements: List[Dict[str, object]] = []

    for row in rows:
        auto_hint = parse_bool(row.get("auto_mechanism_hint_hit", "false"))
        auto_raw = parse_bool(row.get("auto_raw_numeric_hit", "false"))
        auto_pass = parse_bool(row.get("auto_semantic_pass", "false"))
        # Expected according to original auto-check design.
        expected_auto = auto_hint and auto_raw
        if auto_pass != expected_auto:
            logic_mismatch += 1
            logic_mismatch_ids.append(row.get("sample_id", ""))

        indep_pass, indep_detail = independent_check(row)

        key = ("auto_true" if auto_pass else "auto_false", "indep_true" if indep_pass else "indep_false")
        confusion[key] += 1

        bucket = source_bucket(row.get("mechanism_source", ""))
        b = by_bucket[bucket]
        b["n"] += 1
        b["auto_true"] += int(auto_pass)
        b["indep_true"] += int(indep_pass)
        b["agree"] += int(auto_pass == indep_pass)

        if auto_pass != indep_pass:
            disagreements.append(
                {
                    "sample_id": row.get("sample_id"),
                    "clause_id": row.get("clause_id"),
                    "bucket": bucket,
                    "mechanism_type": row.get("mechanism_type"),
                    "mechanism_source": row.get("mechanism_source"),
                    "raw_value_top": row.get("raw_value_top"),
                    "auto_pass": auto_pass,
                    "indep_pass": indep_pass,
                    "auto_hint": auto_hint,
                    "indep_hint": indep_detail["mechanism_hint_hit"],
                    "indep_raw_numeric": indep_detail["raw_numeric_hit"],
                    "clause_text_preview": row.get("clause_text", "")[:160],
                }
            )

    tp = confusion[("auto_true", "indep_true")]
    tn = confusion[("auto_false", "indep_false")]
    fp = confusion[("auto_true", "indep_false")]
    fn = confusion[("auto_false", "indep_true")]
    total = len(rows)
    agreement_rate = (tp + tn) / total if total else 0.0
    kappa = calc_kappa(tp, tn, fp, fn)

    bucket_summary = {}
    for bucket, stat in by_bucket.items():
        bucket_summary[bucket] = {
            "count": stat["n"],
            "auto_true_rate": round(stat["auto_true"] / max(1, stat["n"]), 6),
            "indep_true_rate": round(stat["indep_true"] / max(1, stat["n"]), 6),
            "agreement_rate": round(stat["agree"] / max(1, stat["n"]), 6),
        }

    validity = {
        "is_sample_complete": len(missing_columns) == 0 and total == 80 and empty_text_rows == 0 and duplicate_clause_count == 0,
        "is_auto_logic_consistent": logic_mismatch == 0,
        "agreement_rate": round(agreement_rate, 6),
        "cohen_kappa": round(kappa, 6),
        "judgement": "",
    }
    if validity["is_sample_complete"] and validity["is_auto_logic_consistent"] and agreement_rate >= 0.85:
        validity["judgement"] = "Auto audit is structurally valid and reasonably stable under independent recheck."
    elif validity["is_sample_complete"] and validity["is_auto_logic_consistent"]:
        validity["judgement"] = "Auto audit is structurally valid, but semantic agreement is moderate; human review is needed for lowconf buckets."
    else:
        validity["judgement"] = "Auto audit has structural inconsistency; fix dataset or logic first."

    report = {
        "sample_file": args.sample_file,
        "sample_size": total,
        "missing_columns": missing_columns,
        "duplicate_clause_count": duplicate_clause_count,
        "empty_text_rows": empty_text_rows,
        "auto_logic_mismatch_count": logic_mismatch,
        "auto_logic_mismatch_sample_ids": logic_mismatch_ids[:20],
        "confusion_matrix_auto_vs_indep": {
            "auto_true_indep_true": tp,
            "auto_true_indep_false": fp,
            "auto_false_indep_true": fn,
            "auto_false_indep_false": tn,
        },
        "bucket_summary": bucket_summary,
        "validity": validity,
        "disagreements_top20": disagreements[:20],
        "note": "Independent recheck is rule-based second pass, not human gold precision.",
    }

    out_json = OUTPUT_DIR / f"{args.output_prefix}.json"
    out_md = OUTPUT_DIR / f"{args.output_prefix}.md"
    out_csv = OUTPUT_DIR / f"{args.output_prefix}_disagreements.csv"
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if disagreements:
        with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(disagreements[0].keys()))
            writer.writeheader()
            writer.writerows(disagreements)
    else:
        out_csv.write_text("sample_id\n", encoding="utf-8")

    lines = [
        f"# {args.output_prefix}",
        "",
        f"- sample_size: {report['sample_size']}",
        f"- missing_columns: {report['missing_columns']}",
        f"- duplicate_clause_count: {report['duplicate_clause_count']}",
        f"- empty_text_rows: {report['empty_text_rows']}",
        f"- auto_logic_mismatch_count: {report['auto_logic_mismatch_count']}",
        f"- agreement_rate: {report['validity']['agreement_rate']}",
        f"- cohen_kappa: {report['validity']['cohen_kappa']}",
        f"- judgement: {report['validity']['judgement']}",
        "",
        "## Confusion Matrix",
        f"- auto_true_indep_true: {tp}",
        f"- auto_true_indep_false: {fp}",
        f"- auto_false_indep_true: {fn}",
        f"- auto_false_indep_false: {tn}",
        "",
        "## Bucket Summary",
    ]
    for bucket, stat in sorted(bucket_summary.items()):
        lines.append(
            f"- {bucket}: count={stat['count']}, auto_true_rate={stat['auto_true_rate']}, indep_true_rate={stat['indep_true_rate']}, agreement_rate={stat['agreement_rate']}"
        )
    lines += [
        "",
        "## Artifacts",
        f"- `{out_json.relative_to(PROJECT_ROOT).as_posix()}`",
        f"- `{out_csv.relative_to(PROJECT_ROOT).as_posix()}`",
    ]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("semantic audit recheck done")


if __name__ == "__main__":
    main()

