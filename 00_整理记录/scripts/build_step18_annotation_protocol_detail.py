#!/usr/bin/env python3
"""
Build Step18 annotation protocol detail report for paper methods section.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List


REPO_ROOT = Path(__file__).resolve().parents[2]
RECORD_DIR = REPO_ROOT / "00_整理记录"


def read_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def count_jsonl(path: Path) -> int:
    n = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                n += 1
    return n


def build_report() -> Dict:
    sampling = read_json(RECORD_DIR / "step6_iter4_fixabcd_plus_gold_sampling_plan.json")
    iaa = read_json(RECORD_DIR / "step6_iter4_fixabcd_plus_iaa_report.json")
    pass_a_file = RECORD_DIR / "step6_iter4_fixabcd_plus_gold_passA_labels.jsonl"
    pass_b_file = RECORD_DIR / "step6_iter4_fixabcd_plus_gold_passB_labels.jsonl"
    adjudicated_file = RECORD_DIR / "step6_iter4_fixabcd_plus_gold_adjudicated.jsonl"
    sample_file = RECORD_DIR / "step6_iter4_fixabcd_plus_gold_sample_v1.jsonl"

    pass_a_count = count_jsonl(pass_a_file)
    pass_b_count = count_jsonl(pass_b_file)
    adjudicated_count = count_jsonl(adjudicated_file)
    sample_count = count_jsonl(sample_file)

    # The pipeline contains two blind passes (A/B) and one adjudication stage.
    role_layout = {
        "blind_annotators": 2,
        "adjudication_stage": 1,
        "total_roles": 3,
    }

    return {
        "input": {
            "sampling_plan": "00_整理记录/step6_iter4_fixabcd_plus_gold_sampling_plan.json",
            "iaa_report": "00_整理记录/step6_iter4_fixabcd_plus_iaa_report.json",
            "passA_labels": "00_整理记录/step6_iter4_fixabcd_plus_gold_passA_labels.jsonl",
            "passB_labels": "00_整理记录/step6_iter4_fixabcd_plus_gold_passB_labels.jsonl",
            "adjudicated_labels": "00_整理记录/step6_iter4_fixabcd_plus_gold_adjudicated.jsonl",
        },
        "role_layout": role_layout,
        "workflow": [
            "Step-A: passA blind labeling",
            "Step-B: passB blind labeling",
            "Step-C: disagreement adjudication and gold finalization",
        ],
        "sample_counts": {
            "sample_v1_count": sample_count,
            "passA_count": pass_a_count,
            "passB_count": pass_b_count,
            "adjudicated_count": adjudicated_count,
        },
        "sampling_structure": {
            "target_total": sampling.get("target_total"),
            "actual_total": sampling.get("actual_total"),
            "strict_high_count": sampling.get("strict_high_count"),
            "hard_case_count": sampling.get("hard_case_count"),
            "bind_group_distribution": sampling.get("bind_group_distribution"),
            "hard_tag_distribution": sampling.get("hard_tag_distribution"),
            "mechanism_distribution": sampling.get("mechanism_distribution"),
            "param_type_distribution": sampling.get("param_type_distribution"),
        },
        "iaa_metrics": iaa.get("iaa"),
        "quality_metrics": iaa.get("quality"),
        "error_clusters": iaa.get("error_clusters"),
        "all_targets_passed": iaa.get("all_targets_passed"),
    }


def write_md(report: Dict, output_md: Path) -> None:
    lines: List[str] = []
    lines.append("# Step18 标注流程细节报告")
    lines.append("")
    lines.append("## 角色与流程")
    rl = report["role_layout"]
    lines.append(f"- blind_annotators: {rl['blind_annotators']}")
    lines.append(f"- adjudication_stage: {rl['adjudication_stage']}")
    lines.append(f"- total_roles: {rl['total_roles']}")
    for w in report["workflow"]:
        lines.append(f"- {w}")
    lines.append("")
    lines.append("## 样本与轮次规模")
    sc = report["sample_counts"]
    for k, v in sc.items():
        lines.append(f"- {k}: {v}")
    ss = report["sampling_structure"]
    lines.append(f"- target_total: {ss['target_total']}")
    lines.append(f"- actual_total: {ss['actual_total']}")
    lines.append(f"- strict_high_count: {ss['strict_high_count']}")
    lines.append(f"- hard_case_count: {ss['hard_case_count']}")
    lines.append("")
    lines.append("## IAA 指标")
    for k, v in (report.get("iaa_metrics") or {}).items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Gold 质量指标")
    q = report.get("quality_metrics") or {}
    den = q.get("denominators", {})
    lines.append(f"- denominators: {den}")
    for k in ["mechanism_precision_on_valid_numeric", "normalization_precision_on_valid_numeric", "strict_high_precision"]:
        if k in q:
            lines.append(f"- {k}: {q[k]}")
    lines.append("")
    lines.append("## 硬错误簇")
    for k, v in (report.get("error_clusters") or {}).items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append(f"- all_targets_passed: {report.get('all_targets_passed')}")
    lines.append("")
    output_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Step18 annotation detail report.")
    parser.add_argument(
        "--output-json",
        default="00_整理记录/step18_annotation_protocol_detail.json",
        help="Output JSON path.",
    )
    parser.add_argument(
        "--output-md",
        default="00_整理记录/step18_annotation_protocol_detail.md",
        help="Output Markdown path.",
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
