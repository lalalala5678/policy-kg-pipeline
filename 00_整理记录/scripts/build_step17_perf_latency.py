#!/usr/bin/env python3
"""
Build Step17 performance report:
- Step9 import elapsed time + peak RSS (via /usr/bin/time)
- Query latency distribution (P50/P95) over Step8.2 query pack
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple

from step9_neo4j_utils import Neo4jHttpClient


REPO_ROOT = Path(__file__).resolve().parents[2]


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


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    xs = sorted(values)
    k = (len(xs) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return xs[int(k)]
    d0 = xs[f] * (c - k)
    d1 = xs[c] * (k - f)
    return d0 + d1


def run_import_timed(python_bin: str) -> Dict:
    cmd = [
        "/usr/bin/time",
        "-f",
        "elapsed_sec=%e max_rss_kb=%M",
        python_bin,
        "00_整理记录/scripts/run_step9_neo4j_eval.py",
        "--overwrite",
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    elapsed = None
    max_rss_kb = None
    for line in (proc.stderr or "").splitlines():
        m = re.search(r"elapsed_sec=([0-9.]+)\s+max_rss_kb=([0-9]+)", line.strip())
        if m:
            elapsed = float(m.group(1))
            max_rss_kb = int(m.group(2))
            break
    return {
        "command": " ".join(cmd),
        "return_code": proc.returncode,
        "elapsed_sec": elapsed,
        "max_rss_kb": max_rss_kb,
        "stdout_tail": "\n".join((proc.stdout or "").splitlines()[-3:]),
        "stderr_tail": "\n".join((proc.stderr or "").splitlines()[-3:]),
    }


def benchmark_queries(
    client: Neo4jHttpClient,
    query_defs: Dict[str, dict],
    query_examples: Dict[str, dict],
    repeat: int,
) -> Tuple[List[Dict], Dict]:
    per_query: List[Dict] = []
    all_lat_ms: List[float] = []
    # one warm-up round
    for qid in sorted(query_defs.keys()):
        q = query_defs[qid]
        params = query_examples.get(qid, {}).get("params", {"limit": 10})
        client.execute(q["cypher"], parameters=params)

    for qid in sorted(query_defs.keys()):
        q = query_defs[qid]
        params = query_examples.get(qid, {}).get("params", {"limit": 10})
        lat_ms: List[float] = []
        result_counts: List[int] = []
        errors: List[str] = []
        for _ in range(repeat):
            t0 = time.perf_counter()
            try:
                rows = client.execute(q["cypher"], parameters=params)
                dt = (time.perf_counter() - t0) * 1000.0
                lat_ms.append(dt)
                all_lat_ms.append(dt)
                result_counts.append(len(rows))
            except Exception as exc:
                errors.append(str(exc))
        per_query.append(
            {
                "query_id": qid,
                "title": q["title"],
                "repeat": repeat,
                "success_runs": len(lat_ms),
                "error_runs": len(errors),
                "result_count_median": int(statistics.median(result_counts)) if result_counts else 0,
                "latency_ms_p50": round(percentile(lat_ms, 0.50), 3) if lat_ms else None,
                "latency_ms_p95": round(percentile(lat_ms, 0.95), 3) if lat_ms else None,
                "latency_ms_mean": round(sum(lat_ms) / len(lat_ms), 3) if lat_ms else None,
                "error_sample": errors[:1],
            }
        )

    overall = {
        "query_count": len(query_defs),
        "repeat": repeat,
        "total_runs": len(query_defs) * repeat,
        "successful_runs": len(all_lat_ms),
        "latency_ms_p50": round(percentile(all_lat_ms, 0.50), 3) if all_lat_ms else None,
        "latency_ms_p95": round(percentile(all_lat_ms, 0.95), 3) if all_lat_ms else None,
        "latency_ms_mean": round(sum(all_lat_ms) / len(all_lat_ms), 3) if all_lat_ms else None,
    }
    return per_query, overall


def write_md(report: Dict, output_md: Path) -> None:
    lines: List[str] = []
    lines.append("# Step17 性能与延迟评测报告")
    lines.append("")
    imp = report["import_benchmark"]
    lines.append("## Step9 导入耗时与峰值内存")
    lines.append(f"- elapsed_sec: {imp.get('elapsed_sec')}")
    lines.append(f"- max_rss_kb: {imp.get('max_rss_kb')}")
    lines.append(f"- return_code: {imp.get('return_code')}")
    lines.append("")
    ov = report["query_latency_overall"]
    lines.append("## 查询延迟总体")
    lines.append(f"- query_count: {ov.get('query_count')}")
    lines.append(f"- repeat: {ov.get('repeat')}")
    lines.append(f"- successful_runs: {ov.get('successful_runs')}/{ov.get('total_runs')}")
    lines.append(f"- latency_ms_p50: {ov.get('latency_ms_p50')}")
    lines.append(f"- latency_ms_p95: {ov.get('latency_ms_p95')}")
    lines.append(f"- latency_ms_mean: {ov.get('latency_ms_mean')}")
    lines.append("")
    lines.append("## 每个模板延迟（P50/P95）")
    lines.append("| query_id | title | success_runs | latency_ms_p50 | latency_ms_p95 |")
    lines.append("|---|---|---:|---:|---:|")
    for q in report["query_latency_by_template"]:
        lines.append(
            f"| {q['query_id']} | {q['title']} | {q['success_runs']} | {q['latency_ms_p50']} | {q['latency_ms_p95']} |"
        )
    lines.append("")
    output_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Step17 performance report.")
    parser.add_argument("--python-bin", default="python3", help="Python executable.")
    parser.add_argument("--step8-2-dir", default="结果文件夹/step8_2_iter1", help="Step8.2 directory.")
    parser.add_argument("--neo4j-url", default="http://127.0.0.1:17474", help="Neo4j HTTP URL.")
    parser.add_argument("--neo4j-user", default="neo4j", help="Neo4j username.")
    parser.add_argument("--neo4j-password", default="policykg_step9", help="Neo4j password.")
    parser.add_argument("--repeat", type=int, default=30, help="Repeat runs per query template.")
    parser.add_argument(
        "--output-json",
        default="00_整理记录/step17_perf_latency_report.json",
        help="Output JSON path.",
    )
    parser.add_argument(
        "--output-md",
        default="00_整理记录/step17_perf_latency_report.md",
        help="Output Markdown path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    step8_2_dir = (REPO_ROOT / args.step8_2_dir).resolve()
    query_pack = step8_2_dir / "query_pack.cql"
    query_examples_path = step8_2_dir / "query_examples.json"

    query_defs = parse_query_pack(query_pack)
    query_examples = {x["query_id"]: x for x in json.loads(query_examples_path.read_text(encoding="utf-8"))}

    import_bench = run_import_timed(args.python_bin)
    if import_bench["return_code"] != 0:
        raise RuntimeError(f"step9 import benchmark failed: {import_bench['stderr_tail']}")

    client = Neo4jHttpClient(base_url=args.neo4j_url, user=args.neo4j_user, password=args.neo4j_password, timeout=120)
    client.wait_ready(max_wait_seconds=120)
    per_query, overall = benchmark_queries(client, query_defs, query_examples, repeat=int(args.repeat))

    report = {
        "input": {
            "step8_2_dir": str(step8_2_dir.relative_to(REPO_ROOT)),
            "neo4j_url": args.neo4j_url,
            "repeat": int(args.repeat),
        },
        "import_benchmark": import_bench,
        "query_latency_overall": overall,
        "query_latency_by_template": per_query,
    }

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
                "latency_ms_p50": overall.get("latency_ms_p50"),
                "latency_ms_p95": overall.get("latency_ms_p95"),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
