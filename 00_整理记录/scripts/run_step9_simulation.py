#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

from step9_neo4j_utils import Neo4jHttpClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Step9 risk-aware simulation")
    parser.add_argument("--output-dir", default="00_整理记录/step9_iter1", help="Step9 output directory")
    parser.add_argument("--neo4j-url", default="http://127.0.0.1:17474", help="Neo4j HTTP URL")
    parser.add_argument("--neo4j-user", default="neo4j", help="Neo4j username")
    parser.add_argument("--neo4j-password", default="policykg_step9", help="Neo4j password")
    parser.add_argument("--topn", type=int, default=100, help="Top-N for risk ranking comparison")
    return parser.parse_args()


def stable_json(obj: object) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def risk_penalty(risk_level: str) -> float:
    level = (risk_level or "").lower()
    if level == "high":
        return 0.25
    if level == "medium":
        return 0.08
    return 0.0


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    client = Neo4jHttpClient(base_url=args.neo4j_url, user=args.neo4j_user, password=args.neo4j_password, timeout=120)
    client.wait_ready(max_wait_seconds=120)

    mechanism_hotspots = client.execute(
        "MATCH (m:Mechanism)-[r:mechanism_has_parameter_definition]->() "
        "RETURN m.id AS mechanism_id, m.mechanism_type AS mechanism_type, "
        "sum(coalesce(toInteger(r.conflict_count), 0)) AS total_conflict "
        "ORDER BY total_conflict DESC, mechanism_id ASC LIMIT 20"
    )

    high_risk_facts = client.execute(
        "MATCH ()-[r]->() WHERE r.risk_level = 'high' "
        "RETURN r.edge_id AS edge_id, type(r) AS predicate, r.source AS source, r.target AS target, "
        "r.doc_instance_id AS doc_instance_id, r.clause_id AS clause_id, r.conflict_type AS conflict_type, "
        "toInteger(coalesce(r.conflict_count, 0)) AS conflict_count, "
        "toInteger(coalesce(r.alt_candidates_count, 0)) AS alt_candidates_count "
        "ORDER BY conflict_count DESC, edge_id ASC LIMIT 30"
    )

    backfill_candidates = client.execute(
        "MATCH ()-[ra]->() "
        "WHERE ra.track = 'strict_all' AND NOT EXISTS { "
        "  MATCH ()-[rh]->() "
        "  WHERE rh.track = 'strict_high' "
        "    AND rh.source = ra.source "
        "    AND rh.predicate = ra.predicate "
        "    AND rh.target = ra.target "
        "    AND rh.clause_id = ra.clause_id "
        "} "
        "RETURN ra.source AS source, ra.predicate AS predicate, ra.target AS target, "
        "ra.clause_id AS clause_id, ra.unit AS unit "
        "LIMIT 100"
    )

    candidate_edges = client.execute(
        "MATCH ()-[r:mechanism_has_parameter_definition]->() "
        "WHERE coalesce(r.track, '') = 'strict_all' "
        "RETURN r.edge_id AS edge_id, r.source AS source, r.target AS target, r.doc_instance_id AS doc_instance_id, "
        "r.clause_id AS clause_id, r.unit AS unit, "
        "toFloat(coalesce(r.confidence, 0.0)) AS confidence, "
        "toInteger(coalesce(r.conflict_count, 0)) AS conflict_count, "
        "toInteger(coalesce(r.alt_candidates_count, 0)) AS alt_candidates_count, "
        "coalesce(r.risk_level, 'low') AS risk_level"
    )

    for row in candidate_edges:
        row["risk_adjusted_score"] = (
            float(row.get("confidence", 0.0))
            - 0.06 * int(row.get("conflict_count", 0))
            - 0.03 * int(row.get("alt_candidates_count", 0))
            - risk_penalty(str(row.get("risk_level", "low")))
        )

    by_confidence = sorted(candidate_edges, key=lambda x: (-float(x["confidence"]), str(x["edge_id"])))
    by_adjusted = sorted(candidate_edges, key=lambda x: (-float(x["risk_adjusted_score"]), str(x["edge_id"])))

    topn = max(1, int(args.topn))
    baseline_top = by_confidence[:topn]
    adjusted_top = by_adjusted[:topn]

    def high_risk_count(rows: List[Dict[str, object]]) -> int:
        return sum(1 for r in rows if str(r.get("risk_level", "")).lower() == "high")

    def avg_conflict(rows: List[Dict[str, object]]) -> float:
        if not rows:
            return 0.0
        return sum(int(r.get("conflict_count", 0)) for r in rows) / len(rows)

    baseline_high = high_risk_count(baseline_top)
    adjusted_high = high_risk_count(adjusted_top)

    baseline_high_ratio = (baseline_high / len(baseline_top)) if baseline_top else 0.0
    adjusted_high_ratio = (adjusted_high / len(adjusted_top)) if adjusted_top else 0.0

    baseline_avg_conflict = avg_conflict(baseline_top)
    adjusted_avg_conflict = avg_conflict(adjusted_top)

    removed_high_risk = [
        r
        for r in baseline_top
        if str(r.get("risk_level", "")).lower() == "high"
        and all(r["edge_id"] != x["edge_id"] for x in adjusted_top)
    ][:20]

    added_low_risk = [
        r
        for r in adjusted_top
        if str(r.get("risk_level", "")).lower() in {"low", "medium"}
        and all(r["edge_id"] != x["edge_id"] for x in baseline_top)
    ][:20]

    simulation_summary = {
        "candidate_pool_size": len(candidate_edges),
        "topn": topn,
        "baseline_top_high_risk_count": baseline_high,
        "adjusted_top_high_risk_count": adjusted_high,
        "baseline_top_high_risk_ratio": baseline_high_ratio,
        "adjusted_top_high_risk_ratio": adjusted_high_ratio,
        "baseline_top_avg_conflict": baseline_avg_conflict,
        "adjusted_top_avg_conflict": adjusted_avg_conflict,
        "high_risk_reduction": baseline_high - adjusted_high,
        "high_risk_ratio_reduction": baseline_high_ratio - adjusted_high_ratio,
        "risk_aware_improved": adjusted_high_ratio < baseline_high_ratio,
        "risk_aware_non_regression": adjusted_high_ratio <= baseline_high_ratio,
    }

    casebook = {
        "neo4j": {
            "url": args.neo4j_url,
        },
        "hotspot_analysis": {
            "top_mechanism_conflict": mechanism_hotspots,
            "high_risk_facts": high_risk_facts,
            "strict_all_backfill_candidates_preview": backfill_candidates,
        },
        "risk_aware_rerank": {
            "summary": simulation_summary,
            "baseline_top_preview": baseline_top[:20],
            "risk_adjusted_top_preview": adjusted_top[:20],
            "removed_high_risk_preview": removed_high_risk,
            "added_low_risk_preview": added_low_risk,
        },
    }

    out_path = output_dir / "step9_simulation_casebook.json"
    out_path.write_text(json.dumps(casebook, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(stable_json({"output": str(out_path), "risk_aware_improved": simulation_summary["risk_aware_improved"]}))


if __name__ == "__main__":
    main()
