#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

from step9_neo4j_utils import Neo4jHttpClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Step9 Neo4j import and validation")
    parser.add_argument("--step8-dir", default="结果文件夹/step8_iter1", help="Step8 package directory")
    parser.add_argument("--step8-2-dir", default="结果文件夹/step8_2_iter1", help="Step8.2 package directory")
    parser.add_argument("--output-dir", default="00_整理记录/step9_iter1", help="Step9 output directory")
    parser.add_argument("--container-name", default="policy-kg-step9-neo4j", help="Neo4j container name")
    parser.add_argument("--neo4j-image", default="neo4j:5.26.0-community", help="Neo4j Docker image")
    parser.add_argument("--neo4j-user", default="neo4j", help="Neo4j username")
    parser.add_argument("--neo4j-password", default="policykg_step9", help="Neo4j password")
    parser.add_argument("--http-port", type=int, default=17474, help="Neo4j HTTP host port")
    parser.add_argument("--bolt-port", type=int, default=17687, help="Neo4j Bolt host port")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output directory")
    parser.add_argument("--reset-container", action="store_true", help="Recreate container if exists")
    return parser.parse_args()


def stable_json(obj: object) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def run_cmd(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)
        return sum(1 for _ in reader)


def load_edge_counter(path: Path) -> Counter:
    counter: Counter = Counter()
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row.get("predicate", ""), row.get("track", ""))
            counter[key] += 1
    return counter


def docker_container_status(container_name: str) -> str:
    cp = run_cmd(
        [
            "docker",
            "ps",
            "-a",
            "--filter",
            f"name=^{container_name}$",
            "--format",
            "{{.Status}}",
        ],
        check=False,
    )
    status = cp.stdout.strip()
    if not status:
        return "absent"
    if status.startswith("Up"):
        return "running"
    return "stopped"


def ensure_neo4j_container(args: argparse.Namespace) -> Dict[str, object]:
    status_before = docker_container_status(args.container_name)

    if args.reset_container and status_before != "absent":
        run_cmd(["docker", "rm", "-f", args.container_name], check=False)
        status_before = "absent"

    inspect_image = run_cmd(["docker", "image", "inspect", args.neo4j_image], check=False)
    if inspect_image.returncode != 0:
        run_cmd(["docker", "pull", args.neo4j_image], check=True)

    created = False
    if status_before == "absent":
        run_cmd(
            [
                "docker",
                "run",
                "-d",
                "--name",
                args.container_name,
                "-p",
                f"{args.http_port}:7474",
                "-p",
                f"{args.bolt_port}:7687",
                "-e",
                f"NEO4J_AUTH={args.neo4j_user}/{args.neo4j_password}",
                "-e",
                "NEO4J_dbms_security_allow__csv__import__from__file__urls=true",
                "-e",
                f"NEO4J_server_bolt_advertised__address=:{args.bolt_port}",
                "-e",
                "NEO4J_server_memory_heap_initial__size=384m",
                "-e",
                "NEO4J_server_memory_heap_max__size=768m",
                "-e",
                "NEO4J_server_memory_pagecache_size=256m",
                args.neo4j_image,
            ],
            check=True,
        )
        created = True
    elif status_before == "stopped":
        run_cmd(["docker", "start", args.container_name], check=True)

    return {
        "status_before": status_before,
        "created": created,
        "status_after": docker_container_status(args.container_name),
    }


def stage_import_files(container_name: str, files: List[Tuple[Path, str]]) -> List[dict]:
    run_cmd(["docker", "exec", container_name, "mkdir", "-p", "/var/lib/neo4j/import/step9"], check=True)
    staged: List[dict] = []
    for src, dst_name in files:
        run_cmd(["docker", "cp", str(src), f"{container_name}:/var/lib/neo4j/import/step9/{dst_name}"], check=True)
        staged.append({"source": str(src), "dest": f"/var/lib/neo4j/import/step9/{dst_name}"})
    return staged


def main() -> None:
    args = parse_args()

    step8_dir = Path(args.step8_dir)
    step8_2_dir = Path(args.step8_2_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=args.overwrite)

    strict_all_nodes = step8_dir / "strict_all" / "nodes.csv"
    strict_high_edges = step8_dir / "strict_high" / "edges.csv"
    strict_all_edges = step8_dir / "strict_all" / "edges.csv"
    edge_signals_csv = step8_2_dir / "edge_signals.csv"

    required_paths = [strict_all_nodes, strict_high_edges, strict_all_edges, edge_signals_csv]
    missing = [str(p) for p in required_paths if not p.exists()]
    if missing:
        raise FileNotFoundError(f"missing required inputs: {missing}")

    docker_info = ensure_neo4j_container(args)

    neo4j_url = f"http://127.0.0.1:{args.http_port}"
    client = Neo4jHttpClient(base_url=neo4j_url, user=args.neo4j_user, password=args.neo4j_password, timeout=120)
    client.wait_ready(max_wait_seconds=240)

    staged_files = stage_import_files(
        args.container_name,
        [
            (strict_all_nodes, "nodes_strict_all.csv"),
            (strict_high_edges, "edges_strict_high.csv"),
            (strict_all_edges, "edges_strict_all.csv"),
            (edge_signals_csv, "edge_signals.csv"),
        ],
    )

    client.execute("MATCH (n) DETACH DELETE n")

    constraint_statements = [
        "CREATE CONSTRAINT policydocument_id IF NOT EXISTS FOR (n:PolicyDocument) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT clause_id IF NOT EXISTS FOR (n:Clause) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT mechanism_id IF NOT EXISTS FOR (n:Mechanism) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT parametermention_id IF NOT EXISTS FOR (n:ParameterMention) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT parameterdefinition_id IF NOT EXISTS FOR (n:ParameterDefinition) REQUIRE n.id IS UNIQUE",
    ]
    for stmt in constraint_statements:
        client.execute(stmt)

    index_statements = [
        "CREATE INDEX clause_doc_instance_idx IF NOT EXISTS FOR (n:Clause) ON (n.doc_instance_id)",
        "CREATE INDEX mechanism_type_idx IF NOT EXISTS FOR (n:Mechanism) ON (n.mechanism_type)",
        "CREATE INDEX definition_param_type_idx IF NOT EXISTS FOR (n:ParameterDefinition) ON (n.param_type)",
        "CREATE INDEX policy_source_path_idx IF NOT EXISTS FOR (n:PolicyDocument) ON (n.source_path)",
    ]
    for stmt in index_statements:
        client.execute(stmt)

    labels = ["PolicyDocument", "Clause", "Mechanism", "ParameterMention", "ParameterDefinition"]
    for label in labels:
        stmt = f"""
CALL {{
  LOAD CSV WITH HEADERS FROM 'file:///step9/nodes_strict_all.csv' AS row
  WITH row WHERE row.label = '{label}'
  MERGE (n:`{label}` {{id: row.id}})
  SET n += row
}} IN TRANSACTIONS OF 1000 ROWS
"""
        client.execute(stmt)

    predicates = [
        "contains_clause",
        "contains_mechanism",
        "mechanism_anchor_clause",
        "clause_supports_mechanism",
        "clause_has_parameter_mention",
        "parameter_mention_refers_to_definition",
        "mechanism_has_parameter_definition",
    ]

    for file_name in ["edges_strict_high.csv", "edges_strict_all.csv"]:
        for predicate in predicates:
            stmt = f"""
CALL {{
  LOAD CSV WITH HEADERS FROM 'file:///step9/{file_name}' AS row
  WITH row WHERE row.predicate = '{predicate}'
  MATCH (s {{id: row.source}})
  MATCH (t {{id: row.target}})
  MERGE (s)-[r:`{predicate}` {{edge_id: row.id}}]->(t)
  SET r += row,
      r.edge_id = row.id,
      r.confidence = toFloat(coalesce(row.confidence, '0')),
      r.support_count = toInteger(coalesce(row.support_count, '0'))
}} IN TRANSACTIONS OF 1000 ROWS
"""
            client.execute(stmt)

    signal_stmt = """
CALL {
  LOAD CSV WITH HEADERS FROM 'file:///step9/edge_signals.csv' AS row
  MATCH ()-[r {edge_id: row.edge_id}]->()
  SET r.conflict_count = toInteger(coalesce(row.conflict_count, '0')),
      r.alt_candidates_count = toInteger(coalesce(row.alt_candidates_count, '0')),
      r.conflict_type = row.conflict_type,
      r.risk_level = row.risk_level
} IN TRANSACTIONS OF 1000 ROWS
"""
    client.execute(signal_stmt)

    expected_node_total = count_csv_rows(strict_all_nodes)
    expected_edge_total = count_csv_rows(strict_high_edges) + count_csv_rows(strict_all_edges)
    expected_signals_total = count_csv_rows(edge_signals_csv)
    expected_pred_track = load_edge_counter(strict_high_edges) + load_edge_counter(strict_all_edges)

    node_total = int(client.execute_scalar("MATCH (n) RETURN count(n) AS value", key="value") or 0)
    edge_total = int(client.execute_scalar("MATCH ()-[r]->() RETURN count(r) AS value", key="value") or 0)
    signal_attached_total = int(
        client.execute_scalar(
            "MATCH ()-[r]->() WHERE coalesce(r.risk_level, '') <> '' RETURN count(r) AS value",
            key="value",
        )
        or 0
    )

    node_label_rows = client.execute(
        "MATCH (n) "
        "UNWIND labels(n) AS lbl "
        "WITH lbl WHERE lbl IN $labels "
        "RETURN lbl AS label, count(*) AS cnt ORDER BY label",
        {"labels": labels},
    )
    edge_pred_rows = client.execute(
        "MATCH ()-[r]->() RETURN type(r) AS predicate, coalesce(r.track, '') AS track, count(*) AS cnt "
        "ORDER BY predicate, track"
    )

    trace_rows = client.execute(
        "MATCH ()-[r]->() "
        "RETURN count(r) AS total, "
        "count(CASE WHEN coalesce(r.doc_instance_id, '') <> '' AND coalesce(r.clause_id, '') <> '' THEN 1 END) AS traceable"
    )
    trace_total = int(trace_rows[0]["total"]) if trace_rows else 0
    traceable = int(trace_rows[0]["traceable"]) if trace_rows else 0
    traceability_rate = (traceable / trace_total) if trace_total else 1.0

    constraint_total = int(client.execute_scalar("SHOW CONSTRAINTS YIELD name RETURN count(*) AS value", key="value") or 0)
    index_total = int(client.execute_scalar("SHOW INDEXES YIELD name RETURN count(*) AS value", key="value") or 0)

    actual_pred_track: Counter = Counter()
    for row in edge_pred_rows:
        actual_pred_track[(row.get("predicate", ""), row.get("track", ""))] = int(row.get("cnt", 0))

    checks = {
        "node_total_match_expected": node_total == expected_node_total,
        "edge_total_match_expected": edge_total == expected_edge_total,
        "risk_signal_attached_on_strict_high_edges": signal_attached_total == expected_signals_total,
        "predicate_track_count_match": dict(actual_pred_track) == dict(expected_pred_track),
        "traceability_rate_100": abs(traceability_rate - 1.0) < 1e-12,
        "constraints_created_ge_5": constraint_total >= 5,
        "indexes_created_ge_4": index_total >= 4,
    }

    report = {
        "input": {
            "step8_dir": str(step8_dir),
            "step8_2_dir": str(step8_2_dir),
            "strict_all_nodes_csv": str(strict_all_nodes),
            "strict_high_edges_csv": str(strict_high_edges),
            "strict_all_edges_csv": str(strict_all_edges),
            "edge_signals_csv": str(edge_signals_csv),
        },
        "neo4j": {
            "url": neo4j_url,
            "container_name": args.container_name,
            "image": args.neo4j_image,
            "http_port": args.http_port,
            "bolt_port": args.bolt_port,
            "docker": docker_info,
        },
        "staged_files": staged_files,
        "expected": {
            "node_total": expected_node_total,
            "edge_total": expected_edge_total,
            "edge_signal_total": expected_signals_total,
            "predicate_track_distribution": {
                f"{k[0]}|{k[1]}": v for k, v in sorted(expected_pred_track.items())
            },
        },
        "actual": {
            "node_total": node_total,
            "edge_total": edge_total,
            "edge_signal_attached_total": signal_attached_total,
            "trace_total": trace_total,
            "traceable": traceable,
            "traceability_rate": traceability_rate,
            "constraint_total": constraint_total,
            "index_total": index_total,
            "node_label_distribution": node_label_rows,
            "predicate_track_distribution": [
                {"predicate": k[0], "track": k[1], "count": v} for k, v in sorted(actual_pred_track.items())
            ],
        },
        "checks": checks,
        "all_targets_passed": all(checks.values()),
    }

    out_path = output_dir / "step9_neo4j_import_report.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(stable_json({"output": str(out_path), "all_targets_passed": report["all_targets_passed"]}))


if __name__ == "__main__":
    main()
