#!/usr/bin/env python
"""Validate Step8 graph package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple


CANONICAL_UNITS = {
    "percent",
    "yuan",
    "kwh",
    "time_window",
    "ten_thousand_yuan",
    "yuan_per_kwh",
    "household",
    "yuan_per_sqm",
    "hour",
    "month",
    "year",
    "ton",
    "kw",
    "mw",
    "kva",
    "yuan_per_ton",
    "yuan_per_watt",
    "none",
    "",
}

EDGE_SCHEMA = {
    "contains_clause": ("PolicyDocument", "Clause"),
    "contains_mechanism": ("PolicyDocument", "Mechanism"),
    "mechanism_anchor_clause": ("Mechanism", "Clause"),
    "clause_supports_mechanism": ("Clause", "Mechanism"),
    "mechanism_has_parameter_definition": ("Mechanism", "ParameterDefinition"),
    "clause_has_parameter_mention": ("Clause", "ParameterMention"),
    "parameter_mention_refers_to_definition": ("ParameterMention", "ParameterDefinition"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Step8 package")
    parser.add_argument("--package-dir", required=True, help="Path to graph package run dir")
    parser.add_argument(
        "--compare-package",
        default=None,
        help="Optional package dir for deterministic replay comparison",
    )
    parser.add_argument(
        "--output-json",
        default=None,
        help="Optional report output path; default <package-dir>/validation_report.json",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> List[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def parse_anchor_list(raw: str) -> List[dict]:
    if not raw:
        return []
    try:
        value = json.loads(raw)
        if isinstance(value, list):
            return value
        return []
    except Exception:
        return []


def compare_hashes(manifest_a: dict, manifest_b: dict) -> Tuple[bool, List[dict]]:
    ignore_paths = {"manifest.json", "config.json"}
    by_path_a = {row["path"]: row for row in manifest_a.get("files", [])}
    by_path_b = {row["path"]: row for row in manifest_b.get("files", [])}
    mismatches: List[dict] = []
    for path in sorted(set(by_path_a) | set(by_path_b)):
        if path in ignore_paths:
            continue
        row_a = by_path_a.get(path)
        row_b = by_path_b.get(path)
        if row_a is None or row_b is None:
            mismatches.append({"path": path, "reason": "missing_in_one_package"})
            continue
        if row_a.get("sha256") != row_b.get("sha256") or row_a.get("row_count") != row_b.get("row_count"):
            mismatches.append(
                {
                    "path": path,
                    "sha256_a": row_a.get("sha256"),
                    "sha256_b": row_b.get("sha256"),
                    "row_count_a": row_a.get("row_count"),
                    "row_count_b": row_b.get("row_count"),
                }
            )
    return len(mismatches) == 0, mismatches


def main() -> None:
    args = parse_args()
    package_dir = Path(args.package_dir)
    manifest = read_json(package_dir / "manifest.json")
    config = read_json(package_dir / "config.json")
    stats = read_json(package_dir / "stats.json")

    file_integrity_checks: List[dict] = []
    file_integrity_pass = True
    for item in manifest.get("files", []):
        file_path = package_dir / item["path"]
        exists = file_path.exists()
        actual_hash = sha256_file(file_path) if exists else None
        hash_ok = exists and actual_hash == item.get("sha256")
        file_integrity_checks.append(
            {
                "path": item["path"],
                "exists": exists,
                "manifest_sha256": item.get("sha256"),
                "actual_sha256": actual_hash,
                "hash_match": hash_ok,
                "manifest_row_count": item.get("row_count"),
            }
        )
        if not hash_ok:
            file_integrity_pass = False

    track_reports: Dict[str, dict] = {}
    global_warnings: List[str] = []

    for track in manifest.get("tracks", []):
        nodes = read_csv(package_dir / track / "nodes.csv")
        edges = read_csv(package_dir / track / "edges.csv")
        node_ids = [n["id"] for n in nodes]
        edge_ids = [e["id"] for e in edges]
        node_label_by_id = {n["id"]: n["label"] for n in nodes}

        pk_nodes_ok = len(node_ids) == len(set(node_ids))
        pk_edges_ok = len(edge_ids) == len(set(edge_ids))

        fk_miss = 0
        schema_violations = 0
        evidence_bad = 0
        unit_bad = 0
        unit_missing = 0
        predicate_counter = Counter()

        for e in edges:
            predicate = e["predicate"]
            predicate_counter[predicate] += 1
            src = e["source"]
            tgt = e["target"]
            src_label = node_label_by_id.get(src)
            tgt_label = node_label_by_id.get(tgt)
            if src_label is None or tgt_label is None:
                fk_miss += 1
                continue
            expected = EDGE_SCHEMA.get(predicate)
            if expected is None or expected != (src_label, tgt_label):
                schema_violations += 1

            anchors = parse_anchor_list(e.get("evidence_anchors", ""))
            if track == "strict_high":
                if not anchors:
                    evidence_bad += 1
                else:
                    for anchor in anchors:
                        if (
                            not anchor.get("doc_instance_id")
                            or not anchor.get("clause_id")
                            or anchor.get("char_start") is None
                            or anchor.get("char_end") is None
                        ):
                            evidence_bad += 1
                            break

            unit = (e.get("unit") or "").strip().lower()
            if track == "strict_high":
                if e["predicate"] in {"parameter_mention_refers_to_definition", "mechanism_has_parameter_definition"}:
                    if not unit:
                        unit_missing += 1
                    elif unit not in CANONICAL_UNITS:
                        unit_bad += 1

        node_def_unit_bad = 0
        if track == "strict_high":
            for n in nodes:
                if n.get("label") != "ParameterDefinition":
                    continue
                unit = (n.get("norm_unit") or "").strip().lower()
                if unit and unit not in CANONICAL_UNITS:
                    node_def_unit_bad += 1

        checks = {
            "pk_nodes_unique": pk_nodes_ok,
            "pk_edges_unique": pk_edges_ok,
            "fk_integrity": fk_miss == 0,
            "schema_integrity": schema_violations == 0,
            "evidence_traceability_strict_high": (track != "strict_high") or evidence_bad == 0,
            "edge_unit_legal_strict_high": (track != "strict_high") or (unit_bad == 0 and unit_missing == 0),
            "node_unit_legal_strict_high": (track != "strict_high") or node_def_unit_bad == 0,
            "dry_run_simulated": pk_nodes_ok and pk_edges_ok and fk_miss == 0 and schema_violations == 0,
        }

        track_reports[track] = {
            "counts": {
                "nodes": len(nodes),
                "edges": len(edges),
                "predicates": dict(predicate_counter),
            },
            "errors": {
                "fk_missing": fk_miss,
                "schema_violations": schema_violations,
                "evidence_bad": evidence_bad,
                "unit_bad": unit_bad,
                "unit_missing": unit_missing,
                "node_def_unit_bad": node_def_unit_bad,
            },
            "checks": checks,
            "all_checks_passed": all(checks.values()),
        }

    # conflict explainability check
    conflicts = []
    conflicts_path = package_dir / "conflicts.jsonl"
    if conflicts_path.exists():
        with conflicts_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                conflicts.append(json.loads(line))
    conflict_explain_ok = all(c.get("resolution_reason") and c.get("resolution_action") for c in conflicts)

    # distribution alerts
    if "strict_high" in track_reports and "strict_all" in track_reports:
        p_high = track_reports["strict_high"]["counts"]["predicates"]
        p_all = track_reports["strict_all"]["counts"]["predicates"]
        for predicate, all_count in p_all.items():
            if all_count <= 0:
                continue
            high_count = p_high.get(predicate, 0)
            ratio = high_count / all_count
            if ratio < 0.35:
                global_warnings.append(
                    f"predicate_low_coverage:{predicate}:strict_high/strict_all={ratio:.4f}"
                )

    deterministic_check = {"enabled": args.compare_package is not None, "passed": None, "mismatches": []}
    if args.compare_package:
        compare_manifest = read_json(Path(args.compare_package) / "manifest.json")
        passed, mismatches = compare_hashes(manifest, compare_manifest)
        deterministic_check["passed"] = passed
        deterministic_check["mismatches"] = mismatches

    top_checks = {
        "manifest_file_integrity": file_integrity_pass,
        "conflict_explainability": conflict_explain_ok,
    }
    for track, report in track_reports.items():
        for name, passed in report["checks"].items():
            top_checks[f"{track}:{name}"] = bool(passed)
    if deterministic_check["enabled"]:
        top_checks["deterministic_replay_match"] = bool(deterministic_check["passed"])

    report = {
        "package_dir": str(package_dir),
        "run_id": manifest.get("run_id"),
        "schema_version": manifest.get("schema_version"),
        "extraction_version": manifest.get("extraction_version"),
        "config": config,
        "stats_snapshot": stats,
        "file_integrity_checks": file_integrity_checks,
        "track_reports": track_reports,
        "conflict_count": len(conflicts),
        "conflict_explainability_ok": conflict_explain_ok,
        "warnings": global_warnings,
        "deterministic_check": deterministic_check,
        "checks": top_checks,
        "all_targets_passed": all(top_checks.values()),
    }

    output_json = Path(args.output_json) if args.output_json else package_dir / "validation_report.json"
    with output_json.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write("\n")
    print(json.dumps({"validation_report": str(output_json), "all_targets_passed": report["all_targets_passed"]}))


if __name__ == "__main__":
    main()
