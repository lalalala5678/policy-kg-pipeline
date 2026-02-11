#!/usr/bin/env python
"""Step8 graph package exporter.

Builds deterministic graph packages from Step7b outputs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


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
}

KNOWN_MECHANISMS = {
    "tou_pricing",
    "tiered_pricing",
    "differential_penalty_pricing",
    "general_price_adjustment",
    "subsidy",
    "task_assessment",
    "technology_route",
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
    parser = argparse.ArgumentParser(description="Step8 graph exporter")
    parser.add_argument(
        "--mentions",
        default="00_整理记录/step7b_iterB_rulefix_parameter_mentions.jsonl",
        help="Step5 mention jsonl",
    )
    parser.add_argument(
        "--definitions",
        default="00_整理记录/step7b_iterB_rulefix_parameter_definitions.jsonl",
        help="Step5 definition jsonl",
    )
    parser.add_argument(
        "--clause-corpus",
        default="00_整理记录/step3_clause_corpus.jsonl",
        help="Step3 clause corpus jsonl",
    )
    parser.add_argument(
        "--output-root",
        default="00_整理记录/graph_pkg",
        help="Output package root",
    )
    parser.add_argument("--run-id", required=True, help="Run id for package directory")
    parser.add_argument(
        "--tracks",
        default="strict_high,strict_all",
        help="Comma separated tracks",
    )
    parser.add_argument(
        "--extraction-version",
        default="step7b_iterB_rulefix",
        help="Extraction version string",
    )
    parser.add_argument(
        "--schema-version",
        default="schema_v1.4",
        help="Schema version string",
    )
    parser.add_argument(
        "--strict-all-topk",
        type=int,
        default=5,
        help="Top-K mechanism/definition edges kept per mechanism in strict_all",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing run directory",
    )
    return parser.parse_args()


def stable_json(obj: object) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_jsonl(path: Path) -> List[dict]:
    rows: List[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def get_git_commit() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        return out
    except Exception:
        return "unknown"


def ensure_dir(path: Path, overwrite: bool) -> None:
    if path.exists():
        if not overwrite:
            raise FileExistsError(f"output run dir already exists: {path}")
    path.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_jsonl(path: Path, rows: Iterable[dict]) -> int:
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(stable_json(row))
            f.write("\n")
            count += 1
    return count


def write_json(path: Path, obj: object) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write("\n")


def write_csv(path: Path, rows: List[dict], fieldnames: List[str]) -> int:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return len(rows)


def node_id(label: str, local_id: str) -> str:
    return f"{label}:{local_id}"


def edge_id(fact_key: str) -> str:
    digest = hashlib.sha256(fact_key.encode("utf-8")).hexdigest()[:24]
    return f"edge_{digest}"


def evidence_anchor_from_mention(m: dict) -> dict:
    return {
        "doc_instance_id": m.get("doc_instance_id"),
        "clause_id": m.get("clause_id"),
        "char_start": m.get("evidence_span_start"),
        "char_end": m.get("evidence_span_end"),
    }


def evidence_anchor_from_clause(c: dict) -> dict:
    return {
        "doc_instance_id": c.get("doc_instance_id"),
        "clause_id": c.get("clause_id"),
        "char_start": c.get("clean_span_start"),
        "char_end": c.get("clean_span_end"),
    }


def first_non_empty(*values: object) -> Optional[object]:
    for v in values:
        if v is None:
            continue
        if isinstance(v, str) and not v.strip():
            continue
        return v
    return None


@dataclass
class TrackResult:
    nodes: List[dict]
    edges: List[dict]
    triples: List[dict]
    rejects: List[dict]
    conflicts: List[dict]
    stats: dict


def qualify_mention(track: str, m: dict) -> Tuple[bool, Optional[str]]:
    if not m.get("param_mention_id"):
        return False, "E_SCHEMA_VIOLATION"
    if not m.get("clause_id") or not m.get("doc_instance_id"):
        return False, "E_FK_MISSING"
    if not m.get("param_def_id"):
        return False, "E_FK_MISSING"
    mechanism = first_non_empty(m.get("mechanism_bind_after"), m.get("mechanism_type"))
    if mechanism not in KNOWN_MECHANISMS:
        return False, "E_MECHANISM_UNKNOWN"
    if track == "strict_all":
        if not bool(m.get("strict_all")):
            return False, "E_STRICT_FILTER"
        if not bool(m.get("normalization_matched")):
            return False, "E_VALUE_PARSE_FAIL"
        return True, None
    if not bool(m.get("strict_high")):
        return False, "E_STRICT_FILTER"
    if not bool(m.get("strict_compat_ok")):
        return False, "E_STRICT_COMPAT_FAIL"
    if not bool(m.get("evidence_span_valid")):
        return False, "E_NO_EVIDENCE"
    if bool(m.get("is_numeric_like")):
        if not bool(m.get("normalization_matched")):
            return False, "E_VALUE_PARSE_FAIL"
        unit = str(m.get("norm_unit") or "").strip().lower()
        if not unit:
            return False, "E_UNIT_MISSING"
        if unit not in CANONICAL_UNITS:
            return False, "E_UNIT_NON_CANONICAL"
    return True, None


def build_track(
    track: str,
    mentions: List[dict],
    definitions_by_id: Dict[str, dict],
    clause_by_id: Dict[str, dict],
    extraction_version: str,
    strict_all_topk: int,
) -> TrackResult:
    accepted: List[dict] = []
    rejects: List[dict] = []
    for m in mentions:
        ok, reason = qualify_mention(track, m)
        if not ok:
            rejects.append(
                {
                    "track": track,
                    "mention_id": m.get("param_mention_id"),
                    "doc_instance_id": m.get("doc_instance_id"),
                    "clause_id": m.get("clause_id"),
                    "reason_code": reason,
                }
            )
            continue
        accepted.append(m)

    mechanism_to_defs: Dict[str, Counter] = defaultdict(Counter)
    for m in accepted:
        mech = first_non_empty(m.get("mechanism_id"), m.get("mechanism_bind_after"))
        if mech is None:
            continue
        mechanism_to_defs[str(mech)][str(m["param_def_id"])] += 1

    allowed_mechanism_def_pairs: set[Tuple[str, str]] = set()
    for mech, counter in mechanism_to_defs.items():
        if track == "strict_all" and strict_all_topk > 0:
            for def_id, _ in counter.most_common(strict_all_topk):
                allowed_mechanism_def_pairs.add((mech, def_id))
        else:
            for def_id in counter:
                allowed_mechanism_def_pairs.add((mech, def_id))

    nodes: Dict[str, dict] = {}

    def upsert_node(node: dict) -> None:
        node_id_value = node["id"]
        if node_id_value in nodes:
            return
        nodes[node_id_value] = node

    raw_edges: List[dict] = []

    for m in accepted:
        clause = clause_by_id.get(m["clause_id"])
        if clause is None:
            rejects.append(
                {
                    "track": track,
                    "mention_id": m.get("param_mention_id"),
                    "doc_instance_id": m.get("doc_instance_id"),
                    "clause_id": m.get("clause_id"),
                    "reason_code": "E_FK_MISSING",
                }
            )
            continue
        param_def = definitions_by_id.get(m["param_def_id"])
        if param_def is None:
            rejects.append(
                {
                    "track": track,
                    "mention_id": m.get("param_mention_id"),
                    "doc_instance_id": m.get("doc_instance_id"),
                    "clause_id": m.get("clause_id"),
                    "reason_code": "E_FK_MISSING",
                }
            )
            continue

        mechanism_local = first_non_empty(m.get("mechanism_id"), m.get("mechanism_bind_after"))
        mechanism_local = str(mechanism_local)
        def_local = str(m["param_def_id"])
        if (mechanism_local, def_local) not in allowed_mechanism_def_pairs:
            rejects.append(
                {
                    "track": track,
                    "mention_id": m.get("param_mention_id"),
                    "doc_instance_id": m.get("doc_instance_id"),
                    "clause_id": m.get("clause_id"),
                    "reason_code": "E_STRICT_ALL_TOPK_OVERFLOW",
                }
            )
            continue

        doc_node = {
            "id": node_id("PolicyDocument", str(m["doc_instance_id"])),
            "label": "PolicyDocument",
            "doc_instance_id": str(m["doc_instance_id"]),
            "source_path": str(first_non_empty(m.get("source_path"), clause.get("source_path")) or ""),
            "name": os.path.basename(str(first_non_empty(m.get("source_path"), clause.get("source_path")) or "")),
            "extraction_version": extraction_version,
            "track": track,
        }
        clause_node = {
            "id": node_id("Clause", str(m["clause_id"])),
            "label": "Clause",
            "doc_instance_id": str(m["doc_instance_id"]),
            "clause_id": str(m["clause_id"]),
            "clause_index": clause.get("clause_index"),
            "clause_type_prelim": clause.get("clause_type_prelim"),
            "clause_text": clause.get("clause_text"),
            "extraction_version": extraction_version,
            "track": track,
        }
        mechanism_node = {
            "id": node_id("Mechanism", mechanism_local),
            "label": "Mechanism",
            "doc_instance_id": str(m["doc_instance_id"]),
            "mechanism_id": mechanism_local,
            "mechanism_type": first_non_empty(m.get("mechanism_bind_after"), m.get("mechanism_type")),
            "mechanism_source": m.get("mechanism_source"),
            "extraction_version": extraction_version,
            "track": track,
        }
        mention_node = {
            "id": node_id("ParameterMention", str(m["param_mention_id"])),
            "label": "ParameterMention",
            "doc_instance_id": str(m["doc_instance_id"]),
            "clause_id": str(m["clause_id"]),
            "param_mention_id": str(m["param_mention_id"]),
            "mechanism_id": mechanism_local,
            "param_type": m.get("param_type"),
            "raw_value": m.get("raw_value"),
            "raw_unit": m.get("raw_unit"),
            "norm_value": m.get("norm_value"),
            "norm_unit": m.get("norm_unit"),
            "bind_confidence": m.get("bind_confidence"),
            "strict_all": m.get("strict_all"),
            "strict_high": m.get("strict_high"),
            "extraction_version": extraction_version,
            "track": track,
        }
        def_node = {
            "id": node_id("ParameterDefinition", def_local),
            "label": "ParameterDefinition",
            "param_def_id": def_local,
            "canonical_key": param_def.get("canonical_key"),
            "param_type": param_def.get("param_type"),
            "norm_value": param_def.get("norm_value"),
            "norm_unit": param_def.get("norm_unit"),
            "range_start": param_def.get("range_start"),
            "range_end": param_def.get("range_end"),
            "op": param_def.get("op"),
            "scope_unit": param_def.get("scope_unit"),
            "extraction_version": extraction_version,
            "track": track,
        }
        upsert_node(doc_node)
        upsert_node(clause_node)
        upsert_node(mechanism_node)
        upsert_node(mention_node)
        upsert_node(def_node)

        mention_anchor = evidence_anchor_from_mention(m)
        clause_anchor = evidence_anchor_from_clause(clause)

        raw_edges.extend(
            [
                {
                    "source": doc_node["id"],
                    "predicate": "contains_clause",
                    "target": clause_node["id"],
                    "doc_instance_id": str(m["doc_instance_id"]),
                    "clause_id": str(m["clause_id"]),
                    "unit": "",
                    "confidence": 1.0,
                    "track": track,
                    "evidence_anchor": clause_anchor,
                },
                {
                    "source": doc_node["id"],
                    "predicate": "contains_mechanism",
                    "target": mechanism_node["id"],
                    "doc_instance_id": str(m["doc_instance_id"]),
                    "clause_id": str(m["clause_id"]),
                    "unit": "",
                    "confidence": float(m.get("bind_confidence") or 0.0),
                    "track": track,
                    "evidence_anchor": mention_anchor,
                },
                {
                    "source": mechanism_node["id"],
                    "predicate": "mechanism_anchor_clause",
                    "target": clause_node["id"],
                    "doc_instance_id": str(m["doc_instance_id"]),
                    "clause_id": str(m["clause_id"]),
                    "unit": "",
                    "confidence": float(m.get("bind_confidence") or 0.0),
                    "track": track,
                    "evidence_anchor": mention_anchor,
                },
                {
                    "source": clause_node["id"],
                    "predicate": "clause_supports_mechanism",
                    "target": mechanism_node["id"],
                    "doc_instance_id": str(m["doc_instance_id"]),
                    "clause_id": str(m["clause_id"]),
                    "unit": "",
                    "confidence": float(m.get("bind_confidence") or 0.0),
                    "track": track,
                    "evidence_anchor": mention_anchor,
                },
                {
                    "source": clause_node["id"],
                    "predicate": "clause_has_parameter_mention",
                    "target": mention_node["id"],
                    "doc_instance_id": str(m["doc_instance_id"]),
                    "clause_id": str(m["clause_id"]),
                    "unit": "",
                    "confidence": 1.0,
                    "track": track,
                    "evidence_anchor": mention_anchor,
                },
                {
                    "source": mention_node["id"],
                    "predicate": "parameter_mention_refers_to_definition",
                    "target": def_node["id"],
                    "doc_instance_id": str(m["doc_instance_id"]),
                    "clause_id": str(m["clause_id"]),
                    "unit": str(m.get("norm_unit") or ""),
                    "confidence": float(m.get("bind_confidence") or 0.0),
                    "track": track,
                    "evidence_anchor": mention_anchor,
                },
                {
                    "source": mechanism_node["id"],
                    "predicate": "mechanism_has_parameter_definition",
                    "target": def_node["id"],
                    "doc_instance_id": str(m["doc_instance_id"]),
                    "clause_id": str(m["clause_id"]),
                    "unit": str(m.get("norm_unit") or ""),
                    "confidence": float(m.get("bind_confidence") or 0.0),
                    "track": track,
                    "evidence_anchor": mention_anchor,
                },
            ]
        )

    edge_map: Dict[str, dict] = {}
    conflicts: List[dict] = []
    for e in raw_edges:
        fact_key = "|".join(
            [
                e["track"],
                e["doc_instance_id"],
                e["clause_id"],
                e["source"],
                e["predicate"],
                e["target"],
                e["unit"],
            ]
        )
        if fact_key not in edge_map:
            edge_map[fact_key] = {
                "id": edge_id(fact_key),
                "source": e["source"],
                "predicate": e["predicate"],
                "target": e["target"],
                "unit": e["unit"],
                "confidence": e["confidence"],
                "doc_instance_id": e["doc_instance_id"],
                "clause_id": e["clause_id"],
                "track": e["track"],
                "support_count": 1,
                "evidence_anchors": [e["evidence_anchor"]],
            }
            continue
        entry = edge_map[fact_key]
        entry["support_count"] += 1
        entry["confidence"] = max(float(entry["confidence"]), float(e["confidence"]))
        if e["evidence_anchor"] not in entry["evidence_anchors"]:
            entry["evidence_anchors"].append(e["evidence_anchor"])
        conflicts.append(
            {
                "track": track,
                "fact_key": fact_key,
                "resolution_reason": "E_CONFLICT_SAME_KEY",
                "resolution_action": "aggregate_evidence_anchors",
                "edge_id": entry["id"],
            }
        )

    node_rows = sorted(nodes.values(), key=lambda x: (x["label"], x["id"]))
    edge_rows = sorted(edge_map.values(), key=lambda x: (x["predicate"], x["source"], x["target"], x["id"]))

    triples = []
    for e in edge_rows:
        triples.append(
            {
                "subject": e["source"],
                "predicate": e["predicate"],
                "object": e["target"],
                "track": e["track"],
            }
        )
    triples.sort(key=lambda x: (x["predicate"], x["subject"], x["object"]))

    stats = {
        "track": track,
        "mention_total_input": len(mentions),
        "mention_accepted": len(accepted),
        "reject_count": len(rejects),
        "node_count": len(node_rows),
        "edge_count": len(edge_rows),
        "triple_count": len(triples),
        "predicate_distribution": dict(Counter(e["predicate"] for e in edge_rows)),
        "label_distribution": dict(Counter(n["label"] for n in node_rows)),
        "reject_reason_distribution": dict(Counter(r["reason_code"] for r in rejects)),
    }
    return TrackResult(
        nodes=node_rows,
        edges=edge_rows,
        triples=triples,
        rejects=rejects,
        conflicts=conflicts,
        stats=stats,
    )


def main() -> None:
    args = parse_args()
    tracks = [t.strip() for t in args.tracks.split(",") if t.strip()]
    if not tracks:
        raise ValueError("no tracks specified")

    mentions_path = Path(args.mentions)
    definitions_path = Path(args.definitions)
    clause_path = Path(args.clause_corpus)
    out_root = Path(args.output_root)
    run_dir = out_root / args.run_id
    ensure_dir(run_dir, overwrite=args.overwrite)

    mentions = load_jsonl(mentions_path)
    definitions = load_jsonl(definitions_path)
    clauses = load_jsonl(clause_path)
    definitions_by_id = {str(d["param_def_id"]): d for d in definitions if d.get("param_def_id")}
    clause_by_id = {str(c["clause_id"]): c for c in clauses if c.get("clause_id")}

    rejects_all: List[dict] = []
    conflicts_all: List[dict] = []
    package_stats: Dict[str, dict] = {}
    manifest_files: List[dict] = []

    config = {
        "run_id": args.run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": get_git_commit(),
        "input": {
            "mentions": str(mentions_path),
            "definitions": str(definitions_path),
            "clause_corpus": str(clause_path),
        },
        "tracks": tracks,
        "schema_version": args.schema_version,
        "extraction_version": args.extraction_version,
        "strict_all_topk": args.strict_all_topk,
        "known_mechanisms": sorted(KNOWN_MECHANISMS),
        "canonical_units": sorted(CANONICAL_UNITS),
        "edge_schema": EDGE_SCHEMA,
    }
    write_json(run_dir / "config.json", config)
    manifest_files.append(
        {
            "path": "config.json",
            "row_count": None,
            "sha256": sha256_file(run_dir / "config.json"),
        }
    )

    for track in tracks:
        track_dir = run_dir / track
        track_dir.mkdir(parents=True, exist_ok=True)
        result = build_track(
            track=track,
            mentions=mentions,
            definitions_by_id=definitions_by_id,
            clause_by_id=clause_by_id,
            extraction_version=args.extraction_version,
            strict_all_topk=args.strict_all_topk,
        )

        node_fields = [
            "id",
            "label",
            "name",
            "doc_instance_id",
            "clause_id",
            "clause_index",
            "clause_type_prelim",
            "clause_text",
            "mechanism_id",
            "mechanism_type",
            "mechanism_source",
            "param_mention_id",
            "param_def_id",
            "param_type",
            "raw_value",
            "raw_unit",
            "norm_value",
            "norm_unit",
            "canonical_key",
            "range_start",
            "range_end",
            "op",
            "scope_unit",
            "bind_confidence",
            "strict_all",
            "strict_high",
            "source_path",
            "extraction_version",
            "track",
        ]
        edge_fields = [
            "id",
            "source",
            "predicate",
            "target",
            "unit",
            "confidence",
            "doc_instance_id",
            "clause_id",
            "support_count",
            "track",
            "evidence_anchors",
        ]
        for edge in result.edges:
            edge["evidence_anchors"] = stable_json(edge["evidence_anchors"])

        nodes_csv = track_dir / "nodes.csv"
        edges_csv = track_dir / "edges.csv"
        triples_jsonl = track_dir / "triples_spo.jsonl"
        node_count = write_csv(nodes_csv, result.nodes, node_fields)
        edge_count = write_csv(edges_csv, result.edges, edge_fields)
        triple_count = write_jsonl(triples_jsonl, result.triples)

        package_stats[track] = result.stats

        for rel_path, rows in [
            (f"{track}/nodes.csv", node_count),
            (f"{track}/edges.csv", edge_count),
            (f"{track}/triples_spo.jsonl", triple_count),
        ]:
            file_path = run_dir / rel_path
            manifest_files.append(
                {
                    "path": rel_path,
                    "row_count": rows,
                    "sha256": sha256_file(file_path),
                }
            )

        rejects_all.extend(result.rejects)
        conflicts_all.extend(result.conflicts)

    rejects_all = sorted(
        rejects_all,
        key=lambda x: (
            str(x.get("track")),
            str(x.get("reason_code")),
            str(x.get("doc_instance_id")),
            str(x.get("clause_id")),
            str(x.get("mention_id")),
        ),
    )
    conflicts_all = sorted(
        conflicts_all,
        key=lambda x: (str(x.get("track")), str(x.get("fact_key")), str(x.get("edge_id"))),
    )

    rejects_path = run_dir / "rejects.jsonl"
    conflicts_path = run_dir / "conflicts.jsonl"
    stats_path = run_dir / "stats.json"
    write_jsonl(rejects_path, rejects_all)
    write_jsonl(conflicts_path, conflicts_all)
    write_json(stats_path, package_stats)

    for rel_path, rows in [
        ("rejects.jsonl", len(rejects_all)),
        ("conflicts.jsonl", len(conflicts_all)),
        ("stats.json", None),
    ]:
        file_path = run_dir / rel_path
        manifest_files.append(
            {
                "path": rel_path,
                "row_count": rows,
                "sha256": sha256_file(file_path),
            }
        )

    manifest = {
        "run_id": args.run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": get_git_commit(),
        "schema_version": args.schema_version,
        "extraction_version": args.extraction_version,
        "tracks": tracks,
        "files": sorted(manifest_files, key=lambda x: x["path"]),
    }
    write_json(run_dir / "manifest.json", manifest)
    print(stable_json({"run_dir": str(run_dir), "tracks": tracks, "ok": True}))


if __name__ == "__main__":
    main()
