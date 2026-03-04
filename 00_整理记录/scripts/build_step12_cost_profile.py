#!/usr/bin/env python3
"""
Build Step12 cost profile and reproducibility-alignment report.

This report is intentionally lightweight and runnable on low-resource hosts.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]
RECORD_DIR = REPO_ROOT / "00_整理记录"
RESULT_DIR = REPO_ROOT / "结果文件夹"


def read_json(path: Path) -> Dict:
    text = path.read_text(encoding="utf-8-sig")
    return json.loads(text)


def get_mem_total_gib() -> float:
    meminfo = Path("/proc/meminfo")
    if not meminfo.exists():
        return -1.0
    for line in meminfo.read_text(encoding="utf-8").splitlines():
        if line.startswith("MemTotal:"):
            parts = line.split()
            # kB -> GiB
            kb = float(parts[1])
            return round(kb / 1024.0 / 1024.0, 3)
    return -1.0


def size_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            total += p.stat().st_size
    return total


def run_cmd(cmd: List[str], cwd: Path) -> Dict:
    t0 = time.perf_counter()
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    elapsed = round(time.perf_counter() - t0, 3)
    stdout_tail = "\n".join(proc.stdout.strip().splitlines()[-3:]) if proc.stdout else ""
    stderr_tail = "\n".join(proc.stderr.strip().splitlines()[-3:]) if proc.stderr else ""
    return {
        "command": " ".join(cmd),
        "elapsed_sec": elapsed,
        "return_code": proc.returncode,
        "stdout_tail": stdout_tail,
        "stderr_tail": stderr_tail,
    }


def build_benchmarks(python_bin: str) -> Tuple[List[Dict], List[Path]]:
    cmds = [
        (
            "step5_normalize_validate_costprobe",
            [
                python_bin,
                "00_整理记录/scripts/run_step5_normalize_validate.py",
                "--clause-pred-file",
                "00_整理记录/step4_seq_step2_clause_predictions.jsonl",
                "--clause-source-file",
                "00_整理记录/step3_clause_corpus.jsonl",
                "--output-prefix",
                "step5_costprofile",
                "--bind-min-score",
                "1.0",
                "--strict-high-threshold",
                "0.6",
            ],
            [RECORD_DIR / "step5_costprofile_parameter_definitions.jsonl",
             RECORD_DIR / "step5_costprofile_parameter_mentions.jsonl",
             RECORD_DIR / "step5_costprofile_triples_spo.jsonl",
             RECORD_DIR / "step5_costprofile_validation_report.json",
             RECORD_DIR / "step5_costprofile_validation_report.md"],
        ),
        (
            "step6_gold_iaa_costprobe",
            [
                python_bin,
                "00_整理记录/scripts/run_step6_gold_iaa.py",
                "--mentions",
                "00_整理记录/step5_costprofile_parameter_mentions.jsonl",
                "--clause-corpus",
                "00_整理记录/step3_clause_corpus.jsonl",
                "--sample-size",
                "300",
                "--strict-min",
                "140",
                "--hard-min",
                "80",
                "--seed",
                "20260211",
                "--output-prefix",
                "step6_costprofile",
            ],
            [RECORD_DIR / "step6_costprofile_error_clusters.md",
             RECORD_DIR / "step6_costprofile_gold_adjudicated.jsonl",
             RECORD_DIR / "step6_costprofile_gold_passA_labels.jsonl",
             RECORD_DIR / "step6_costprofile_gold_passB_labels.jsonl",
             RECORD_DIR / "step6_costprofile_gold_sample_v1.jsonl",
             RECORD_DIR / "step6_costprofile_gold_sampling_plan.json",
             RECORD_DIR / "step6_costprofile_iaa_report.json",
             RECORD_DIR / "step6_costprofile_iaa_report.md"],
        ),
        (
            "step8_2_query_pack_costprobe",
            [
                python_bin,
                "00_整理记录/scripts/run_step8_2_query_pack.py",
                "--step8-dir",
                "结果文件夹/step8_iter1",
                "--output-dir",
                "00_整理记录/step8_2_costprofile",
                "--overwrite",
            ],
            [RECORD_DIR / "step8_2_costprofile"],
        ),
        (
            "step9_query_eval",
            [python_bin, "00_整理记录/scripts/run_step9_query_eval.py"],
            [],
        ),
        (
            "step9_gate_eval",
            [python_bin, "00_整理记录/scripts/eval_step9_gate.py"],
            [],
        ),
    ]

    rows: List[Dict] = []
    cleanup_paths: List[Path] = []
    for bench_id, cmd, outputs in cmds:
        row = run_cmd(cmd, cwd=REPO_ROOT)
        row["id"] = bench_id
        rows.append(row)
        cleanup_paths.extend(outputs)
    return rows, cleanup_paths


def cleanup_paths(paths: List[Path]) -> None:
    for p in paths:
        if not p.exists():
            continue
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()


def to_human_mb(n: int) -> float:
    return round(n / 1024.0 / 1024.0, 3)


def build_report(run_bench: bool, python_bin: str, keep_bench_artifacts: bool) -> Dict:
    step1 = read_json(RECORD_DIR / "policy_readthrough_summary.json")
    step3 = read_json(RECORD_DIR / "step3_qc_report.json")
    step8_stats = read_json(RESULT_DIR / "step8_iter1" / "stats.json")
    step8_2_eval = read_json(RESULT_DIR / "step8_2_iter1" / "step8_2_eval_report.json")
    step9_gate = read_json(RECORD_DIR / "step9_iter1" / "step9_gate_report.json")

    env = {
        "hostname": platform.node(),
        "os": platform.platform(),
        "python": platform.python_version(),
        "cpu_cores": os.cpu_count(),
        "mem_total_gib": get_mem_total_gib(),
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    data_scale = {
        "file_total": step1.get("file_count"),
        "char_total": step1.get("total_chars"),
        "document_units": step3.get("unit_document_count"),
        "clause_total": (step3.get("clause_qc") or {}).get("clause_total"),
    }

    graph_scale = {
        "strict_high_nodes": step8_stats.get("strict_high", {}).get("node_count"),
        "strict_high_edges": step8_stats.get("strict_high", {}).get("edge_count"),
        "strict_all_nodes": step8_stats.get("strict_all", {}).get("node_count"),
        "strict_all_edges": step8_stats.get("strict_all", {}).get("edge_count"),
        "neo4j_node_total": (step9_gate.get("snapshot") or {}).get("import", {}).get("node_total"),
        "neo4j_edge_total": (step9_gate.get("snapshot") or {}).get("import", {}).get("edge_total"),
        "query_template_count": step8_2_eval.get("metrics", {}).get("query_template_count"),
    }

    artifacts = {
        "step8_iter1_mb": to_human_mb(size_bytes(RESULT_DIR / "step8_iter1")),
        "step8_2_iter1_mb": to_human_mb(size_bytes(RESULT_DIR / "step8_2_iter1")),
        "step9_iter1_mb": to_human_mb(size_bytes(RECORD_DIR / "step9_iter1")),
        "step5_mentions_mb": to_human_mb(size_bytes(RECORD_DIR / "step5_seq_step2_v2_rebind14_fixabcd_plus2_parameter_mentions.jsonl")),
        "step5_definitions_mb": to_human_mb(size_bytes(RECORD_DIR / "step5_seq_step2_v2_rebind14_fixabcd_plus2_parameter_definitions.jsonl")),
        "step5_triples_mb": to_human_mb(size_bytes(RECORD_DIR / "step5_seq_step2_v2_rebind14_fixabcd_plus2_triples_spo.jsonl")),
    }

    if run_bench:
        benchmarks, bench_outputs = build_benchmarks(python_bin)
        if not keep_bench_artifacts:
            cleanup_paths(bench_outputs)
    else:
        benchmarks, bench_outputs = [], []
    bench_ok = all(x.get("return_code", 1) == 0 for x in benchmarks) if benchmarks else None

    reproducibility_alignment = {
        "artifacts": [
            "结果文件夹/README_使用指南.md",
            "结果文件夹/step8_iter1/manifest.json",
            "结果文件夹/step8_iter1/validation_report.json",
            "结果文件夹/step8_2_iter1/step8_2_eval_report.json",
            "00_整理记录/step9_iter1/step9_gate_report.json",
        ],
        "data": {
            "public_structured": [
                "00_整理记录/step3_clause_corpus.jsonl",
                "00_整理记录/step5_seq_step2_v2_rebind14_fixabcd_plus2_parameter_mentions.jsonl",
                "00_整理记录/step5_seq_step2_v2_rebind14_fixabcd_plus2_parameter_definitions.jsonl",
            ],
            "traceability_fields": [
                "doc_instance_id",
                "clause_id",
                "evidence_span_start",
                "evidence_span_end",
                "canonical_key",
            ],
        },
        "environment": {
            "python": env["python"],
            "cpu_cores": env["cpu_cores"],
            "mem_total_gib": env["mem_total_gib"],
        },
        "results": {
            "deterministic_replay_match": read_json(RESULT_DIR / "step8_iter1" / "validation_report.json").get(
                "checks", {}
            ).get("deterministic_replay_match"),
            "step9_all_targets_passed": step9_gate.get("all_targets_passed"),
            "step9_query_execution_success_rate": (step9_gate.get("snapshot") or {}).get("query", {}).get(
                "query_execution_success_rate"
            ),
            "step9_core_path_coverage": (step9_gate.get("snapshot") or {}).get("query", {}).get("core_path_coverage"),
        },
    }

    return {
        "environment": env,
        "data_scale": data_scale,
        "graph_scale": graph_scale,
        "artifact_sizes_mb": artifacts,
        "benchmarks": benchmarks,
        "benchmarks_all_passed": bench_ok,
        "keep_bench_artifacts": keep_bench_artifacts,
        "reproducibility_alignment": reproducibility_alignment,
        "notes": [
            "Benchmarks are measured on cached intermediate artifacts and include script runtime only.",
            "Step4 full UIE inference cost is not included in this report.",
        ],
    }


def write_md(report: Dict, output_md: Path) -> None:
    env = report["environment"]
    data_scale = report["data_scale"]
    graph = report["graph_scale"]
    sizes = report["artifact_sizes_mb"]
    benches = report.get("benchmarks", [])

    lines: List[str] = []
    lines.append("# Step12 成本画像与复现对齐报告")
    lines.append("")
    lines.append("## 环境")
    lines.append(f"- timestamp_utc: {env.get('timestamp_utc')}")
    lines.append(f"- os: {env.get('os')}")
    lines.append(f"- python: {env.get('python')}")
    lines.append(f"- cpu_cores: {env.get('cpu_cores')}")
    lines.append(f"- mem_total_gib: {env.get('mem_total_gib')}")
    lines.append("")
    lines.append("## 数据与图规模")
    lines.append(f"- file_total: {data_scale.get('file_total')}")
    lines.append(f"- char_total: {data_scale.get('char_total')}")
    lines.append(f"- document_units: {data_scale.get('document_units')}")
    lines.append(f"- clause_total: {data_scale.get('clause_total')}")
    lines.append(f"- strict_high nodes/edges: {graph.get('strict_high_nodes')}/{graph.get('strict_high_edges')}")
    lines.append(f"- strict_all nodes/edges: {graph.get('strict_all_nodes')}/{graph.get('strict_all_edges')}")
    lines.append(f"- neo4j nodes/edges: {graph.get('neo4j_node_total')}/{graph.get('neo4j_edge_total')}")
    lines.append("")
    lines.append("## 产物体量（MB）")
    lines.append("| artifact | size_mb |")
    lines.append("|---|---:|")
    for k, v in sizes.items():
        lines.append(f"| {k} | {v} |")
    lines.append("")
    lines.append("## 脚本耗时")
    if benches:
        lines.append("| id | elapsed_sec | return_code |")
        lines.append("|---|---:|---:|")
        for b in benches:
            lines.append(f"| {b.get('id')} | {b.get('elapsed_sec')} | {b.get('return_code')} |")
    else:
        lines.append("- 未执行 benchmark（run_bench=false）")
    lines.append("")
    lines.append("## 备注")
    for note in report.get("notes", []):
        lines.append(f"- {note}")
    lines.append("")
    output_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Step12 cost profile report.")
    parser.add_argument(
        "--output-json",
        type=str,
        default="00_整理记录/step12_cost_profile_report.json",
        help="Output JSON report path.",
    )
    parser.add_argument(
        "--output-md",
        type=str,
        default="00_整理记录/step12_cost_profile_report.md",
        help="Output Markdown report path.",
    )
    parser.add_argument(
        "--run-bench",
        action="store_true",
        help="Run lightweight benchmark commands to measure elapsed time.",
    )
    parser.add_argument(
        "--python-bin",
        type=str,
        default="python3",
        help="Python executable for benchmark commands.",
    )
    parser.add_argument(
        "--keep-bench-artifacts",
        action="store_true",
        help="Keep temporary benchmark artifacts (default is cleanup).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_report(
        run_bench=bool(args.run_bench),
        python_bin=str(args.python_bin),
        keep_bench_artifacts=bool(args.keep_bench_artifacts),
    )

    output_json = (REPO_ROOT / args.output_json).resolve()
    output_md = (REPO_ROOT / args.output_md).resolve()
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    with output_json.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    write_md(report, output_md)

    print(
        json.dumps(
            {
                "output_json": str(output_json.relative_to(REPO_ROOT)),
                "output_md": str(output_md.relative_to(REPO_ROOT)),
                "benchmarks_all_passed": report.get("benchmarks_all_passed"),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
