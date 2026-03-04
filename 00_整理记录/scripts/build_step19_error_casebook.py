#!/usr/bin/env python3
"""
Build Step19 error casebook with before/after examples.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[2]
RECORD_DIR = REPO_ROOT / "00_整理记录"
RESULT_DIR = REPO_ROOT / "结果文件夹"


def read_jsonl(path: Path) -> List[Dict]:
    out: List[Dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def read_clause_map(path: Path) -> Dict[str, str]:
    m: Dict[str, str] = {}
    for row in read_jsonl(path):
        m[str(row.get("clause_id"))] = str(row.get("clause_text") or "")
    return m


def clip(s: str, n: int = 180) -> str:
    if len(s) <= n:
        return s
    return s[:n] + "..."


def build_casebook(
    full_mentions_path: Path,
    baseline_mentions_path: Path,
    clause_corpus_path: Path,
    edge_signals_path: Path,
) -> Dict:
    full_rows = read_jsonl(full_mentions_path)
    base_rows = read_jsonl(baseline_mentions_path)
    clause_map = read_clause_map(clause_corpus_path)
    full_by_id = {str(r.get("param_mention_id")): r for r in full_rows}
    base_by_id = {str(r.get("param_mention_id")): r for r in base_rows}

    cases: List[Dict] = []

    # Case group A: binding repaired in full vs no_rebind baseline
    repaired = []
    for mid, fr in full_by_id.items():
        br = base_by_id.get(mid)
        if not br:
            continue
        full_mech = str(fr.get("mechanism_type") or "")
        base_mech = str(br.get("mechanism_type") or "")
        if full_mech and (not base_mech or full_mech != base_mech):
            score = (1 if bool(fr.get("strict_high")) else 0) + (1 if not bool(br.get("strict_high")) else 0)
            repaired.append((score, mid, fr, br))
    repaired.sort(key=lambda x: x[0], reverse=True)

    for _, mid, fr, br in repaired[:3]:
        clause_id = str(fr.get("clause_id") or "")
        cases.append(
            {
                "case_type": "misbinding_repair",
                "mention_id": mid,
                "doc_instance_id": str(fr.get("doc_instance_id") or ""),
                "clause_id": clause_id,
                "clause_text_snippet": clip(clause_map.get(clause_id, "")),
                "before": {
                    "method": "no_rebind",
                    "mechanism_type": br.get("mechanism_type"),
                    "bind_reason": br.get("mechanism_bind_reason"),
                    "strict_high": br.get("strict_high"),
                    "bind_confidence": br.get("bind_confidence"),
                },
                "after": {
                    "method": "full",
                    "mechanism_type": fr.get("mechanism_type"),
                    "bind_reason": fr.get("mechanism_bind_reason"),
                    "strict_high": fr.get("strict_high"),
                    "bind_confidence": fr.get("bind_confidence"),
                },
                "why_it_matters": "Mechanism binding recovered under full pipeline; candidate rebind and guards improve high-confidence usability.",
            }
        )

    # Case group B: unit normalization example
    unit_case: Optional[Dict] = None
    for fr in full_rows:
        raw_unit = str(fr.get("raw_unit") or "")
        norm_unit = str(fr.get("norm_unit") or "")
        rule = str(fr.get("normalization_rule") or "")
        if raw_unit and norm_unit and raw_unit != norm_unit and "yuan_per_degree_to_yuan_per_kwh" in rule:
            unit_case = fr
            break
    if unit_case is None:
        for fr in full_rows:
            raw_unit = str(fr.get("raw_unit") or "")
            norm_unit = str(fr.get("norm_unit") or "")
            if raw_unit and norm_unit and raw_unit != norm_unit:
                unit_case = fr
                break

    if unit_case is not None:
        cid = str(unit_case.get("clause_id") or "")
        cases.append(
            {
                "case_type": "unit_normalization_repair",
                "mention_id": str(unit_case.get("param_mention_id") or ""),
                "doc_instance_id": str(unit_case.get("doc_instance_id") or ""),
                "clause_id": cid,
                "clause_text_snippet": clip(clause_map.get(cid, "")),
                "before": {
                    "raw_value": unit_case.get("raw_value"),
                    "raw_unit": unit_case.get("raw_unit"),
                    "normalization_rule": unit_case.get("normalization_rule"),
                },
                "after": {
                    "norm_value": unit_case.get("norm_value"),
                    "norm_unit": unit_case.get("norm_unit"),
                    "canonical_key": unit_case.get("canonical_key"),
                },
                "why_it_matters": "Unit harmonization converts heterogeneous expressions into canonical units for cross-document comparability.",
            }
        )

    # Case group C: semantic collision signal
    with edge_signals_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        semantic_row = None
        for row in reader:
            if str(row.get("conflict_type")) == "semantic_collision":
                semantic_row = row
                break
    if semantic_row is not None:
        target = str(semantic_row.get("target") or "")
        mention_id = target.split(":", 1)[1] if ":" in target else target
        fr = full_by_id.get(mention_id, {})
        cid = str(fr.get("clause_id") or semantic_row.get("clause_id") or "")
        cases.append(
            {
                "case_type": "semantic_collision_flagged",
                "mention_id": mention_id,
                "doc_instance_id": str(semantic_row.get("doc_instance_id") or ""),
                "clause_id": cid,
                "clause_text_snippet": clip(clause_map.get(cid, "")),
                "before": {
                    "edge_id": semantic_row.get("edge_id"),
                    "conflict_type": semantic_row.get("conflict_type"),
                    "risk_level": semantic_row.get("risk_level"),
                    "alt_candidates_count": semantic_row.get("alt_candidates_count"),
                },
                "after": {
                    "action": "flagged_for_review",
                    "support_count": semantic_row.get("support_count"),
                    "conflict_count": semantic_row.get("conflict_count"),
                },
                "why_it_matters": "Semantic collision is transformed into graph edge signal, enabling risk-aware review without hiding ambiguous facts.",
            }
        )

    return {
        "input": {
            "full_mentions": str(full_mentions_path.relative_to(REPO_ROOT)),
            "baseline_mentions": str(baseline_mentions_path.relative_to(REPO_ROOT)),
            "clause_corpus": str(clause_corpus_path.relative_to(REPO_ROOT)),
            "edge_signals": str(edge_signals_path.relative_to(REPO_ROOT)),
        },
        "case_count": len(cases),
        "cases": cases[:5],
    }


def write_md(report: Dict, output_md: Path) -> None:
    lines: List[str] = []
    lines.append("# Step19 失败样例与修复前后对照")
    lines.append("")
    lines.append(f"- case_count: {report['case_count']}")
    lines.append("")
    for idx, c in enumerate(report["cases"], start=1):
        lines.append(f"## Case {idx}: {c['case_type']}")
        lines.append(f"- mention_id: `{c['mention_id']}`")
        lines.append(f"- clause_id: `{c['clause_id']}`")
        lines.append(f"- clause_text_snippet: {c['clause_text_snippet']}")
        lines.append("- before:")
        for k, v in (c.get("before") or {}).items():
            lines.append(f"  - {k}: {v}")
        lines.append("- after:")
        for k, v in (c.get("after") or {}).items():
            lines.append(f"  - {k}: {v}")
        lines.append(f"- why_it_matters: {c['why_it_matters']}")
        lines.append("")
    output_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Step19 error casebook report.")
    parser.add_argument(
        "--full-mentions",
        default="00_整理记录/step5_seq_step2_v2_rebind14_fixabcd_plus2_parameter_mentions.jsonl",
        help="Full method mention file.",
    )
    parser.add_argument(
        "--baseline-mentions",
        default="00_整理记录/step15_baseline_no_rebind_parameter_mentions.jsonl",
        help="Baseline mention file (before).",
    )
    parser.add_argument(
        "--clause-corpus",
        default="00_整理记录/step3_clause_corpus.jsonl",
        help="Clause corpus file.",
    )
    parser.add_argument(
        "--edge-signals",
        default="结果文件夹/step8_2_iter1/edge_signals.csv",
        help="Edge signal csv.",
    )
    parser.add_argument(
        "--output-json",
        default="00_整理记录/step19_error_casebook.json",
        help="Output JSON path.",
    )
    parser.add_argument(
        "--output-md",
        default="00_整理记录/step19_error_casebook.md",
        help="Output Markdown path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_casebook(
        full_mentions_path=(REPO_ROOT / args.full_mentions).resolve(),
        baseline_mentions_path=(REPO_ROOT / args.baseline_mentions).resolve(),
        clause_corpus_path=(REPO_ROOT / args.clause_corpus).resolve(),
        edge_signals_path=(REPO_ROOT / args.edge_signals).resolve(),
    )
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
                "case_count": report.get("case_count"),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
