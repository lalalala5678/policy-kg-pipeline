from __future__ import annotations

import argparse
import csv
import json
import random
import re
from pathlib import Path
from typing import Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "00_整理记录"
if not OUTPUT_DIR.exists():
    OUTPUT_DIR = PROJECT_ROOT / "00_鏁寸悊璁板綍"

LOW_CONF_SOURCES = {"fallback_clause_type_lowconf", "rule_context_neighbor_lowconf"}
CN_NUM_RE = re.compile(r"[零〇一二三四五六七八九十百千万两壹贰叁肆伍陆柒捌玖拾佰仟]")
CN_PERCENT_RE = re.compile(r"\u767e\u5206\u4e4b[零〇一二三四五六七八九十百千万两\d\.]+")
TIME_RANGE_RE = re.compile(r"\d{1,2}:\d{2}\s*[-~\u81f3]\s*\d{1,2}:\d{2}")
RATIO_RE = re.compile(r"\d+(?:\.\d+)?\s*:\s*\d+(?:\.\d+)?(?:\s*:\s*\d+(?:\.\d+)?)?")

MECH_TEXT_HINTS = {
    "tou_pricing": re.compile(
        r"\u5206\u65f6|\u5cf0\u8c37|\u5cf0\u5e73\u8c37|\u5cf0\u6bb5|\u8c37\u6bb5|\u5c16\u5cf0|"
        r"\d{1,2}:\d{2}\s*[-~\u81f3]\s*\d{1,2}:\d{2}|\d+(?:\.\d+)?\s*:\s*\d+(?:\.\d+)?(?:\s*:\s*\d+(?:\.\d+)?)?"
    ),
    "tiered_pricing": re.compile(r"\u9636\u68af|\u5206\u6863|\u6863\u4f4d|\u4e00\u6863|\u4e8c\u6863|\u4e09\u6863"),
    "differential_penalty_pricing": re.compile(r"\u5dee\u522b\u7535\u4ef7|\u60e9\u7f5a|\u9650\u5236\u7c7b|\u6dd8\u6c70\u7c7b"),
    "general_price_adjustment": re.compile(r"\u4e0a\u6d6e|\u4e0b\u6d6e|\u4e0a\u8c03|\u4e0b\u8c03|\u52a0\u4ef7|\u964d\u4ef7|\u8c03\u6574\u7535\u4ef7"),
    "subsidy": re.compile(r"\u8865\u8d34|\u8865\u52a9|\u5956\u52b1|\u5956\u8865|\u8865\u507f"),
    "task_assessment": re.compile(r"\u4efb\u52a1|\u8003\u6838|\u9a8c\u6536|\u63a8\u8fdb|\u8d23\u4efb"),
    "technology_route": re.compile(r"\u7535\u80fd\u66ff\u4ee3|\u6e05\u6d01\u53d6\u6696|\u7164\u6539\u7535|\u5cb8\u7535"),
}


def read_jsonl(path: Path) -> List[Dict]:
    rows: List[Dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


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


def span_is_valid(item: Dict, text: str) -> bool:
    st = item.get("start")
    ed = item.get("end")
    val = str(item.get("text", ""))
    return isinstance(st, int) and isinstance(ed, int) and 0 <= st <= ed <= len(text) and text[st:ed] == val


def top_item(items: List[Dict]) -> Dict | None:
    if not items:
        return None
    return sorted(items, key=lambda x: float(x.get("probability", 0.0)), reverse=True)[0]


def source_bucket(source: str) -> str:
    if source in LOW_CONF_SOURCES:
        return "lowconf_fallback"
    if source in ("rule_pattern", "rule_pattern_ext"):
        return "rule_pattern"
    if source == "rule_numeric_keyword":
        return "rule_numeric_keyword"
    if source == "rule_context_neighbor":
        return "rule_context_neighbor"
    if source.startswith("fallback_clause_type"):
        return "fallback_other"
    if source in ("", "uie"):
        return "uie_or_empty"
    return "other"


def is_strict_ready(row: Dict) -> bool:
    pred = row.get("prediction", {})
    mech = pred.get("mechanism_type") or []
    ctype = pred.get("clause_type") or []
    raw = pred.get("raw_value") or []
    return bool(mech and ctype and raw and any(is_numeric_like(str(x.get("text", ""))) for x in raw))


def auto_semantic_check(mechanism_type: str, clause_text: str, raw_items: List[Dict]) -> Dict:
    hint_re = MECH_TEXT_HINTS.get(mechanism_type)
    mechanism_hint_hit = bool(hint_re.search(clause_text)) if hint_re else False
    raw_numeric_hit = any(is_numeric_like(str(x.get("text", ""))) for x in raw_items)
    raw_span_valid = any(span_is_valid(x, clause_text) for x in raw_items)
    auto_pass = mechanism_hint_hit and raw_numeric_hit
    return {
        "mechanism_hint_hit": mechanism_hint_hit,
        "raw_numeric_hit": raw_numeric_hit,
        "raw_span_valid_any": raw_span_valid,
        "auto_pass": auto_pass,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build semantic audit samples for Step4 strict triplets.")
    parser.add_argument("--clause-pred-file", type=str, default="00_整理记录/step4_iter3_v2plus_clause_predictions.jsonl")
    parser.add_argument("--clause-source-file", type=str, default="00_整理记录/step3_clause_corpus.jsonl")
    parser.add_argument("--sample-size", type=int, default=80)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-prefix", type=str, default="step4_semantic_audit")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sample_size = max(50, min(100, args.sample_size))

    clause_rows = read_jsonl(PROJECT_ROOT / args.clause_pred_file)
    source_rows = read_jsonl(PROJECT_ROOT / args.clause_source_file)
    text_map = {x["clause_id"]: x.get("clause_text", "") for x in source_rows}
    source_path_map = {x["clause_id"]: x.get("source_path", "") for x in source_rows}

    strict_rows = []
    for row in clause_rows:
        if not is_strict_ready(row):
            continue
        pred = row.get("prediction", {})
        top_mech = top_item(pred.get("mechanism_type") or [])
        mech = str((top_mech or {}).get("text", ""))
        source = str((top_mech or {}).get("source", ""))
        strict_rows.append(
            {
                "clause_id": row.get("clause_id"),
                "doc_instance_id": row.get("doc_instance_id"),
                "source_path": source_path_map.get(row.get("clause_id"), row.get("source_path", "")),
                "mechanism_type": mech,
                "mechanism_source": source,
                "source_bucket": source_bucket(source),
                "prediction": pred,
                "clause_text": text_map.get(row.get("clause_id"), ""),
            }
        )

    random.seed(args.seed)
    by_bucket: Dict[str, List[Dict]] = {}
    for row in strict_rows:
        by_bucket.setdefault(row["source_bucket"], []).append(row)
    for bucket in by_bucket:
        random.shuffle(by_bucket[bucket])

    buckets = sorted(by_bucket.keys())
    sampled: List[Dict] = []
    remaining = sample_size
    for i, bucket in enumerate(buckets):
        bucket_rows = by_bucket[bucket]
        if i == len(buckets) - 1:
            take = min(len(bucket_rows), remaining)
        else:
            quota = max(1, round(sample_size * len(bucket_rows) / max(1, len(strict_rows))))
            take = min(len(bucket_rows), quota, remaining)
        sampled.extend(bucket_rows[:take])
        remaining = sample_size - len(sampled)
        if remaining <= 0:
            break
    if len(sampled) < sample_size:
        used_ids = {x["clause_id"] for x in sampled}
        pool = [x for x in strict_rows if x["clause_id"] not in used_ids]
        random.shuffle(pool)
        sampled.extend(pool[: sample_size - len(sampled)])

    auto_pass_count = 0
    bucket_stats: Dict[str, Dict[str, int]] = {}
    csv_rows = []
    for idx, row in enumerate(sampled, start=1):
        pred = row["prediction"]
        raw_items = pred.get("raw_value") or []
        raw_units = pred.get("raw_unit") or []
        clause_type = (pred.get("clause_type") or [{}])[0].get("text", "")
        checks = auto_semantic_check(row["mechanism_type"], row["clause_text"], raw_items)
        if checks["auto_pass"]:
            auto_pass_count += 1
        bkt = row["source_bucket"]
        bucket_stats.setdefault(bkt, {"count": 0, "auto_pass": 0})
        bucket_stats[bkt]["count"] += 1
        bucket_stats[bkt]["auto_pass"] += int(checks["auto_pass"])
        csv_rows.append(
            {
                "sample_id": idx,
                "clause_id": row["clause_id"],
                "source_path": row["source_path"],
                "mechanism_type": row["mechanism_type"],
                "mechanism_source": row["mechanism_source"],
                "source_bucket": bkt,
                "clause_type": clause_type,
                "raw_value_top": (raw_items[0].get("text") if raw_items else ""),
                "raw_unit_top": (raw_units[0].get("text") if raw_units else ""),
                "auto_mechanism_hint_hit": checks["mechanism_hint_hit"],
                "auto_raw_numeric_hit": checks["raw_numeric_hit"],
                "auto_raw_span_valid_any": checks["raw_span_valid_any"],
                "auto_semantic_pass": checks["auto_pass"],
                "human_label": "",
                "human_note": "",
                "clause_text": row["clause_text"],
            }
        )

    report = {
        "sample_size": len(csv_rows),
        "strict_pool_size": len(strict_rows),
        "auto_semantic_pass_rate": round(auto_pass_count / max(1, len(csv_rows)), 6),
        "bucket_stats": {
            k: {
                "count": v["count"],
                "auto_pass": v["auto_pass"],
                "auto_pass_rate": round(v["auto_pass"] / max(1, v["count"]), 6),
            }
            for k, v in bucket_stats.items()
        },
        "note": "This is an automatic semantic consistency precheck, not human gold precision.",
    }

    csv_path = OUTPUT_DIR / f"{args.output_prefix}_sample.csv"
    json_path = OUTPUT_DIR / f"{args.output_prefix}_report.json"
    md_path = OUTPUT_DIR / f"{args.output_prefix}_report.md"

    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()) if csv_rows else [])
        if csv_rows:
            writer.writeheader()
            writer.writerows(csv_rows)

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_lines = [
        f"# {args.output_prefix} Auto Semantic Audit",
        "",
        f"- strict_pool_size: {report['strict_pool_size']}",
        f"- sample_size: {report['sample_size']}",
        f"- auto_semantic_pass_rate: {report['auto_semantic_pass_rate']}",
        f"- note: {report['note']}",
        "",
        "## Bucket Stats",
    ]
    for bkt, stat in report["bucket_stats"].items():
        md_lines.append(f"- {bkt}: count={stat['count']}, auto_pass_rate={stat['auto_pass_rate']}")
    md_lines += [
        "",
        "## Artifacts",
        f"- `{csv_path.relative_to(PROJECT_ROOT).as_posix()}`",
        f"- `{json_path.relative_to(PROJECT_ROOT).as_posix()}`",
    ]
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print("semantic audit sample done")


if __name__ == "__main__":
    main()

