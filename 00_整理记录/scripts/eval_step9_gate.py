#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Step9 gate")
    parser.add_argument("--step9-dir", default="00_整理记录/step9_iter1", help="Step9 output directory")
    parser.add_argument("--output", default="00_整理记录/step9_iter1/step9_gate_report.json", help="Gate report output path")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def stable_json(obj: object) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def main() -> None:
    args = parse_args()
    step9_dir = Path(args.step9_dir)

    import_report_path = step9_dir / "step9_neo4j_import_report.json"
    query_report_path = step9_dir / "step9_query_exec_report.json"
    sim_casebook_path = step9_dir / "step9_simulation_casebook.json"

    missing = [str(p) for p in [import_report_path, query_report_path, sim_casebook_path] if not p.exists()]
    if missing:
        raise FileNotFoundError(f"missing required inputs: {missing}")

    import_report = load_json(import_report_path)
    query_report = load_json(query_report_path)
    casebook = load_json(sim_casebook_path)

    sim_summary = casebook.get("risk_aware_rerank", {}).get("summary", {})
    hotspot = casebook.get("hotspot_analysis", {})

    checks = {
        "step9_import_gate_passed": bool(import_report.get("all_targets_passed", False)),
        "step9_query_gate_passed": bool(query_report.get("all_targets_passed", False)),
        "neo4j_traceability_rate_100": float(import_report.get("actual", {}).get("traceability_rate", 0.0)) == 1.0,
        "query_execution_success_rate_100": float(query_report.get("metrics", {}).get("query_execution_success_rate", 0.0)) == 1.0,
        "core_path_coverage_100": float(query_report.get("metrics", {}).get("core_path_coverage", 0.0)) == 1.0,
        "simulation_high_risk_cases_non_empty": len(hotspot.get("high_risk_facts", [])) > 0,
        "simulation_backfill_candidates_non_empty": len(hotspot.get("strict_all_backfill_candidates_preview", [])) > 0,
        "risk_aware_rerank_non_regression": bool(sim_summary.get("risk_aware_non_regression", False)),
    }

    report = {
        "input": {
            "step9_dir": str(step9_dir),
            "import_report": str(import_report_path),
            "query_report": str(query_report_path),
            "simulation_casebook": str(sim_casebook_path),
        },
        "snapshot": {
            "import": {
                "node_total": import_report.get("actual", {}).get("node_total"),
                "edge_total": import_report.get("actual", {}).get("edge_total"),
                "traceability_rate": import_report.get("actual", {}).get("traceability_rate"),
            },
            "query": {
                "query_template_count": query_report.get("metrics", {}).get("query_template_count"),
                "query_execution_success_rate": query_report.get("metrics", {}).get("query_execution_success_rate"),
                "core_path_coverage": query_report.get("metrics", {}).get("core_path_coverage"),
            },
            "simulation": sim_summary,
        },
        "checks": checks,
        "all_targets_passed": all(checks.values()),
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(stable_json({"output": str(out_path), "all_targets_passed": report["all_targets_passed"]}))


if __name__ == "__main__":
    main()
