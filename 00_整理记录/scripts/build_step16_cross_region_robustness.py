#!/usr/bin/env python3
"""
Build cross-region robustness statistics from Step5 mentions (posterior stratification).
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]


REGION_PATTERNS: List[Tuple[str, List[str]]] = [
    ("北京", ["北京"]),
    ("天津", ["天津"]),
    ("上海", ["上海"]),
    ("重庆", ["重庆"]),
    ("河北", ["河北"]),
    ("山西", ["山西"]),
    ("辽宁", ["辽宁"]),
    ("吉林", ["吉林"]),
    ("黑龙江", ["黑龙江"]),
    ("江苏", ["江苏"]),
    ("浙江", ["浙江"]),
    ("安徽", ["安徽"]),
    ("福建", ["福建"]),
    ("江西", ["江西"]),
    ("山东", ["山东"]),
    ("河南", ["河南"]),
    ("湖北", ["湖北"]),
    ("湖南", ["湖南"]),
    ("广东", ["广东"]),
    ("海南", ["海南"]),
    ("四川", ["四川"]),
    ("贵州", ["贵州"]),
    ("云南", ["云南"]),
    ("陕西", ["陕西"]),
    ("甘肃", ["甘肃"]),
    ("青海", ["青海"]),
    ("台湾", ["台湾"]),
    ("内蒙古", ["内蒙古", "蒙西", "蒙东"]),
    ("广西", ["广西"]),
    ("西藏", ["西藏"]),
    ("宁夏", ["宁夏"]),
    ("新疆", ["新疆"]),
]


def detect_region(source_path: str) -> str:
    text = source_path or ""
    for region, patterns in REGION_PATTERNS:
        for p in patterns:
            if p in text:
                return region
    return "unknown"


def read_jsonl(path: Path) -> List[Dict]:
    rows: List[Dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def build_report(mentions_file: Path) -> Dict:
    rows = read_jsonl(mentions_file)
    agg = defaultdict(lambda: defaultdict(int))

    for m in rows:
        region = detect_region(str(m.get("source_path") or ""))
        a = agg[region]
        a["mention_total"] += 1
        valid_all = bool(m.get("evidence_span_valid") and m.get("normalization_attempted"))
        if valid_all:
            a["valid_all"] += 1
            if bool(m.get("normalization_matched")):
                a["normalization_matched_valid_all"] += 1
            if str(m.get("mechanism_type") or ""):
                a["mechanism_bound_valid_all"] += 1
            if bool(m.get("strict_high")):
                a["strict_high_valid_all"] += 1
        valid_numeric = bool(valid_all and m.get("normalization_matched") and m.get("is_numeric_like"))
        if valid_numeric:
            a["valid_numeric"] += 1
            if str(m.get("mechanism_type") or ""):
                a["mechanism_bound_valid_numeric"] += 1
            if bool(m.get("strict_high")):
                a["strict_high_valid_numeric"] += 1

    out_rows: List[Dict] = []
    for region in sorted(agg.keys()):
        a = agg[region]
        va = max(int(a["valid_all"]), 1)
        vn = max(int(a["valid_numeric"]), 1)
        out_rows.append(
            {
                "region": region,
                "mention_total": int(a["mention_total"]),
                "valid_all": int(a["valid_all"]),
                "valid_numeric": int(a["valid_numeric"]),
                "normalization_matched_rate_on_valid_all": round(a["normalization_matched_valid_all"] / va, 6),
                "mechanism_bound_rate_valid_all": round(a["mechanism_bound_valid_all"] / va, 6),
                "strict_high_rate_valid_all": round(a["strict_high_valid_all"] / va, 6),
                "mechanism_bound_rate_valid_numeric": round(a["mechanism_bound_valid_numeric"] / vn, 6),
                "strict_high_rate_valid_numeric": round(a["strict_high_valid_numeric"] / vn, 6),
            }
        )

    stable = [r for r in out_rows if int(r["valid_all"]) >= 20 and r["region"] != "unknown"]

    def metric_span(key: str) -> Dict:
        vals = [float(r[key]) for r in stable]
        if not vals:
            return {"min": None, "max": None, "range": None, "std": None}
        return {
            "min": min(vals),
            "max": max(vals),
            "range": round(max(vals) - min(vals), 6),
            "std": round(statistics.pstdev(vals), 6),
        }

    return {
        "input": {
            "mentions_file": str(mentions_file.relative_to(REPO_ROOT)),
            "region_rule": "source_path keyword matching (province/autonomous-region aliases)",
        },
        "rows": out_rows,
        "summary": {
            "region_count": len(out_rows),
            "stable_region_threshold_valid_all": 20,
            "stable_region_count": len(stable),
            "unknown_region_mentions": int(agg["unknown"]["mention_total"]) if "unknown" in agg else 0,
            "stability": {
                "normalization_matched_rate_on_valid_all": metric_span("normalization_matched_rate_on_valid_all"),
                "mechanism_bound_rate_valid_all": metric_span("mechanism_bound_rate_valid_all"),
                "strict_high_rate_valid_all": metric_span("strict_high_rate_valid_all"),
            },
        },
    }


def write_md(report: Dict, output_md: Path) -> None:
    lines: List[str] = []
    lines.append("# Step16 跨地区稳健性统计（后验）")
    lines.append("")
    lines.append(f"- 输入 mentions: `{report['input']['mentions_file']}`")
    lines.append(f"- region_rule: {report['input']['region_rule']}")
    lines.append(f"- region_count: {report['summary']['region_count']}")
    lines.append(f"- stable_region_count: {report['summary']['stable_region_count']}")
    lines.append(f"- unknown_region_mentions: {report['summary']['unknown_region_mentions']}")
    lines.append("")
    lines.append("| region | mention_total | valid_all | valid_numeric | norm_matched/valid_all | mech_bound/valid_all | strict_high/valid_all |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for r in report["rows"]:
        lines.append(
            f"| {r['region']} | {r['mention_total']} | {r['valid_all']} | {r['valid_numeric']} | "
            f"{r['normalization_matched_rate_on_valid_all']:.6f} | {r['mechanism_bound_rate_valid_all']:.6f} | "
            f"{r['strict_high_rate_valid_all']:.6f} |"
        )
    lines.append("")
    lines.append("## 稳定性摘要（valid_all>=20, 排除 unknown）")
    for k, v in report["summary"]["stability"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    output_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Step16 cross-region robustness report.")
    parser.add_argument(
        "--mentions",
        type=str,
        default="00_整理记录/step5_seq_step2_v2_rebind14_fixabcd_plus2_parameter_mentions.jsonl",
        help="Step5 mention file.",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default="00_整理记录/step16_cross_region_robustness_report.json",
        help="Output JSON path.",
    )
    parser.add_argument(
        "--output-md",
        type=str,
        default="00_整理记录/step16_cross_region_robustness_report.md",
        help="Output Markdown path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mentions_file = (REPO_ROOT / args.mentions).resolve()
    report = build_report(mentions_file)
    output_json = (REPO_ROOT / args.output_json).resolve()
    output_md = (REPO_ROOT / args.output_md).resolve()
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_md(report, output_md)
    print(
        json.dumps(
            {
                "output_json": str(output_json.relative_to(REPO_ROOT)),
                "output_md": str(output_md.relative_to(REPO_ROOT)),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
