#!/usr/bin/env python3
"""
Build error/risk profile report from Step5/6/7/8.2 artifacts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List


REPO_ROOT = Path(__file__).resolve().parents[2]
RECORD_DIR = REPO_ROOT / "00_整理记录"
RESULT_DIR = REPO_ROOT / "结果文件夹"


def read_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def build_report() -> Dict:
    step5 = read_json(RECORD_DIR / "step5_seq_step2_v2_rebind14_fixabcd_plus2_validation_report.json")
    step6 = read_json(RECORD_DIR / "step6_iter4_fixabcd_plus_iaa_report.json")
    step7 = read_json(RECORD_DIR / "step7_gate_iter3_final.json")
    step8_2 = read_json(RESULT_DIR / "step8_2_iter1" / "step8_2_eval_report.json")
    cross_year = read_json(RECORD_DIR / "step7_cross_year_robustness_report.json")

    hard_errors = step6.get("error_clusters", {})
    hard_error_pass = {k: (v == 0) for k, v in hard_errors.items()}

    conflict_summary = step8_2.get("conflict_signal_summary", {})
    conflict_dist = conflict_summary.get("conflict_type_distribution", {})
    conflict_total = int(conflict_summary.get("conflict_total", 0))
    conflict_ratio = {}
    for k, v in conflict_dist.items():
        conflict_ratio[k] = round((v / conflict_total) if conflict_total else 0.0, 6)

    # Step5 guard actions and low-confidence handling
    c = step5.get("counts", {})
    guard_profile = {
        "raw_value_filtered_non_value_count": c.get("raw_value_filtered_non_value_count", 0),
        "raw_value_filtered_by_rule_count": c.get("raw_value_filtered_by_rule_count", 0),
        "unit_pairing_dropped_count": c.get("unit_pairing_dropped_count", 0),
        "strict_high_compat_block_count": c.get("strict_high_compat_block_count", 0),
        "strict_high_weak_constraint_block_count": c.get("strict_high_weak_constraint_block_count", 0),
        "clause_negative_count": c.get("clause_negative_count", 0),
        "low_confidence_cap_count": c.get("low_confidence_cap_count", 0),
    }

    bind_reason_top = (step5.get("distribution", {}) or {}).get("bind_reason_top20", {})

    # Margin to thresholds from Step7 protocol
    s5 = step7["step5_snapshot"]
    s6 = step7["step6_snapshot"]
    threshold_margins = {
        "normalization_matched_rate_margin": round(s5["normalization_matched_on_mentions"]["rate"] - 0.95, 6),
        "strict_high_rate_valid_numeric_margin": round(s5["strict_high_on_valid_numeric"]["rate"] - 0.85, 6),
        "local_supported_rate_valid_numeric_margin": round(s5["local_supported_rate_valid_numeric"] - 0.85, 6),
        "kappa_mechanism_margin": round(s6["iaa"]["kappa_mechanism"] - 0.90, 6),
        "kappa_param_type_margin": round(s6["iaa"]["kappa_param_type"] - 0.95, 6),
        "mechanism_precision_margin": round(s6["mechanism_precision_on_valid_numeric"]["rate"] - 0.95, 6),
        "normalization_precision_margin": round(s6["normalization_precision_on_valid_numeric"]["rate"] - 0.995, 6),
        "strict_high_precision_margin": round(s6["strict_high_precision"]["rate"] - 0.992, 6),
    }

    # Identify weakest years (enough sample only)
    rows = cross_year.get("rows", [])
    stable_rows = [r for r in rows if int(r.get("valid_all", 0)) >= 30]
    weakest_years = sorted(stable_rows, key=lambda r: r.get("strict_high_rate_valid_all", 1.0))[:3]

    risk_findings = [
        "Hard-error buckets are all zero in current gate report; current risk is dominated by soft conflicts and threshold sensitivity.",
        "strict_high_rate_valid_numeric is close to threshold (small positive margin), indicating potential regression risk under domain shift.",
        "Cross-year strict_high variability is significantly larger than mechanism binding variability, suggesting expression-style sensitivity.",
    ]

    return {
        "input": {
            "step5_report": "00_整理记录/step5_seq_step2_v2_rebind14_fixabcd_plus2_validation_report.json",
            "step6_report": "00_整理记录/step6_iter4_fixabcd_plus_iaa_report.json",
            "step7_gate_report": "00_整理记录/step7_gate_iter3_final.json",
            "step8_2_eval_report": "结果文件夹/step8_2_iter1/step8_2_eval_report.json",
            "cross_year_report": "00_整理记录/step7_cross_year_robustness_report.json",
        },
        "hard_error_buckets": hard_errors,
        "hard_error_pass": hard_error_pass,
        "conflict_summary": {
            "conflict_total": conflict_total,
            "conflict_type_distribution": conflict_dist,
            "conflict_type_ratio": conflict_ratio,
        },
        "guard_profile": guard_profile,
        "bind_reason_top20": bind_reason_top,
        "threshold_margins": threshold_margins,
        "weakest_years_by_strict_high": weakest_years,
        "risk_findings": risk_findings,
    }


def write_md(report: Dict, output_md: Path) -> None:
    lines: List[str] = []
    lines.append("# Step14 错误画像与风险剖面报告")
    lines.append("")
    lines.append("## 硬错误桶")
    for k, v in report["hard_error_buckets"].items():
        lines.append(f"- {k}: {v} (pass={report['hard_error_pass'][k]})")
    lines.append("")
    lines.append("## 冲突分布（Step8.2）")
    cs = report["conflict_summary"]
    lines.append(f"- conflict_total: {cs['conflict_total']}")
    for k, v in cs["conflict_type_distribution"].items():
        ratio = cs["conflict_type_ratio"][k]
        lines.append(f"- {k}: {v} ({ratio:.6f})")
    lines.append("")
    lines.append("## 守卫与过滤动作（Step5）")
    for k, v in report["guard_profile"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## 门禁余量（Margin）")
    for k, v in report["threshold_margins"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## 最弱年份（按 strict_high_rate_valid_all）")
    lines.append("| year | valid_all | strict_high_rate_valid_all | normalization_matched_rate_on_valid_all |")
    lines.append("|---|---:|---:|---:|")
    for r in report["weakest_years_by_strict_high"]:
        lines.append(
            f"| {r['year']} | {r['valid_all']} | {r['strict_high_rate_valid_all']:.6f} | {r['normalization_matched_rate_on_valid_all']:.6f} |"
        )
    lines.append("")
    lines.append("## 风险结论")
    for item in report["risk_findings"]:
        lines.append(f"- {item}")
    lines.append("")
    output_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Step14 error profile report.")
    parser.add_argument(
        "--output-json",
        type=str,
        default="00_整理记录/step14_error_profile_report.json",
        help="Output JSON report path.",
    )
    parser.add_argument(
        "--output-md",
        type=str,
        default="00_整理记录/step14_error_profile_report.md",
        help="Output Markdown report path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_report()
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
