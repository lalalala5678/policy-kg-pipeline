#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

from step9_neo4j_utils import Neo4jHttpClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Step9 query evaluation on Neo4j")
    parser.add_argument("--step8-2-dir", default="结果文件夹/step8_2_iter1", help="Step8.2 output directory")
    parser.add_argument("--output-dir", default="00_整理记录/step9_iter1", help="Step9 output directory")
    parser.add_argument("--neo4j-url", default="http://127.0.0.1:17474", help="Neo4j HTTP URL")
    parser.add_argument("--neo4j-user", default="neo4j", help="Neo4j username")
    parser.add_argument("--neo4j-password", default="policykg_step9", help="Neo4j password")
    return parser.parse_args()


def stable_json(obj: object) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def parse_query_pack(path: Path) -> Dict[str, dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    queries: Dict[str, dict] = {}
    current_id = None
    current_title = None
    for line in lines:
        m = re.match(r"\s*//\s*(Q\d+)\s+([A-Za-z0-9_]+)", line)
        if m:
            current_id = m.group(1)
            current_title = m.group(2)
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        if current_id:
            queries[current_id] = {
                "query_id": current_id,
                "title": current_title,
                "cypher": stripped.rstrip(";").strip(),
            }
            current_id = None
            current_title = None
    return queries


def main() -> None:
    args = parse_args()

    step8_2_dir = Path(args.step8_2_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    query_pack = step8_2_dir / "query_pack.cql"
    query_examples_path = step8_2_dir / "query_examples.json"
    step8_2_eval_path = step8_2_dir / "step8_2_eval_report.json"

    required = [query_pack, query_examples_path, step8_2_eval_path]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"missing required inputs: {missing}")

    query_defs = parse_query_pack(query_pack)
    query_examples = json.loads(query_examples_path.read_text(encoding="utf-8"))
    step8_2_eval = json.loads(step8_2_eval_path.read_text(encoding="utf-8"))

    example_by_id = {item["query_id"]: item for item in query_examples}
    path_tag_by_id = {item["query_id"]: item.get("path_tag", "") for item in step8_2_eval.get("query_eval", [])}

    client = Neo4jHttpClient(base_url=args.neo4j_url, user=args.neo4j_user, password=args.neo4j_password, timeout=120)
    client.wait_ready(max_wait_seconds=120)

    eval_rows: List[dict] = []
    for query_id in sorted(query_defs.keys()):
        q = query_defs[query_id]
        ex = example_by_id.get(query_id, {"params": {"limit": 10}})
        params = ex.get("params", {})
        try:
            records = client.execute(q["cypher"], parameters=params)
            eval_rows.append(
                {
                    "query_id": query_id,
                    "title": q["title"],
                    "path_tag": path_tag_by_id.get(query_id, ""),
                    "executed_successfully": True,
                    "result_count": len(records),
                    "result_preview": records[:3],
                    "params": params,
                    "error": "",
                }
            )
        except Exception as exc:
            eval_rows.append(
                {
                    "query_id": query_id,
                    "title": q["title"],
                    "path_tag": path_tag_by_id.get(query_id, ""),
                    "executed_successfully": False,
                    "result_count": 0,
                    "result_preview": [],
                    "params": params,
                    "error": str(exc),
                }
            )

    total = len(eval_rows)
    success = sum(1 for r in eval_rows if r["executed_successfully"])
    non_empty = sum(1 for r in eval_rows if r["executed_successfully"] and r["result_count"] > 0)
    parameterized = sum(1 for r in eval_rows if isinstance(r.get("params"), dict) and len(r.get("params", {})) > 0)

    success_rate = (success / total) if total else 1.0
    non_empty_rate = (non_empty / total) if total else 1.0
    parameterized_coverage = (parameterized / total) if total else 1.0

    required_core_tags = {"forward_main", "reverse_main"}
    covered_core_tags = {
        r["path_tag"]
        for r in eval_rows
        if r["executed_successfully"] and r["result_count"] > 0 and r["path_tag"] in required_core_tags
    }
    core_path_coverage = 1.0 if required_core_tags.issubset(covered_core_tags) else 0.0

    risk_rows = [r for r in eval_rows if r.get("path_tag") == "risk_signal"]
    risk_non_empty = sum(1 for r in risk_rows if r["executed_successfully"] and r["result_count"] > 0)
    risk_query_coverage = (risk_non_empty / len(risk_rows)) if risk_rows else 1.0

    checks = {
        "query_template_count_10_20": 10 <= total <= 20,
        "query_execution_success_rate_100": abs(success_rate - 1.0) < 1e-12,
        "core_path_coverage_100": abs(core_path_coverage - 1.0) < 1e-12,
        "parameterized_example_coverage_100": abs(parameterized_coverage - 1.0) < 1e-12,
        "non_empty_query_rate_ge_95": non_empty_rate >= 0.95,
        "risk_signal_query_coverage_ge_95": risk_query_coverage >= 0.95,
    }

    report = {
        "input": {
            "query_pack": str(query_pack),
            "query_examples": str(query_examples_path),
            "step8_2_eval_report": str(step8_2_eval_path),
        },
        "neo4j": {
            "url": args.neo4j_url,
        },
        "metrics": {
            "query_template_count": total,
            "query_execution_success_rate": success_rate,
            "core_path_coverage": core_path_coverage,
            "parameterized_example_coverage": parameterized_coverage,
            "non_empty_query_rate": non_empty_rate,
            "risk_signal_query_coverage": risk_query_coverage,
        },
        "query_eval": eval_rows,
        "checks": checks,
        "all_targets_passed": all(checks.values()),
    }

    out_path = output_dir / "step9_query_exec_report.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(stable_json({"output": str(out_path), "all_targets_passed": report["all_targets_passed"]}))


if __name__ == "__main__":
    main()
