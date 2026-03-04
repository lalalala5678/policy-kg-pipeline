#!/usr/bin/env python3
"""
Run and aggregate Step15 external baseline experiments under a unified protocol.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List


REPO_ROOT = Path(__file__).resolve().parents[2]
RECORD_DIR = REPO_ROOT / "00_整理记录"


def run_cmd(cmd: List[str]) -> Dict:
    t0 = time.perf_counter()
    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    elapsed = round(time.perf_counter() - t0, 3)
    return {
        "command": " ".join(cmd),
        "return_code": proc.returncode,
        "elapsed_sec": elapsed,
        "stdout_tail": "\n".join((proc.stdout or "").splitlines()[-3:]),
        "stderr_tail": "\n".join((proc.stderr or "").splitlines()[-3:]),
    }


def read_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def strict_high_rate_valid_all(report: Dict) -> float:
    den = int((report.get("frozen_denominators") or {}).get("valid_all", 0))
    num = int((report.get("counts") or {}).get("strict_high_count", 0))
    return round((num / den) if den else 0.0, 6)


def local_supported_rate_valid_all(report: Dict) -> float:
    den = int((report.get("frozen_denominators") or {}).get("valid_all", 0))
    num = int((report.get("counts") or {}).get("local_supported_count", 0))
    return round((num / den) if den else 0.0, 6)


def build_rows(reports: Dict[str, Dict]) -> List[Dict]:
    rows: List[Dict] = []
    for name, rep in reports.items():
        rows.append(
            {
                "baseline": name,
                "binding_mode": rep["input"].get("binding_mode"),
                "disable_strict_high_guards": rep["input"].get("disable_strict_high_guards"),
                "bind_min_score": rep["input"].get("bind_min_score"),
                "strict_high_threshold": rep["input"].get("strict_high_threshold"),
                "valid_all": rep["frozen_denominators"].get("valid_all"),
                "valid_numeric": rep["frozen_denominators"].get("valid_numeric"),
                "normalization_matched_rate": rep["rates"].get("normalization_matched_rate"),
                "mechanism_bound_rate_valid_all": rep["rates"].get("mechanism_bound_rate_valid_all"),
                "mechanism_bound_rate_valid_numeric": rep["rates"].get("mechanism_bound_rate_valid_numeric"),
                "strict_high_rate_valid_numeric": rep["rates"].get("strict_high_rate_valid_numeric"),
                "strict_high_rate_valid_all": strict_high_rate_valid_all(rep),
                "local_supported_rate_valid_numeric": rep["rates"].get("local_supported_rate_valid_numeric"),
                "local_supported_rate_valid_all": local_supported_rate_valid_all(rep),
                "all_targets_passed": rep.get("all_targets_passed"),
                "report_path": rep["_report_path"],
            }
        )
    return rows


def write_csv(path: Path, rows: List[Dict], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fieldnames})


def write_md(path: Path, rows: List[Dict], runs: Dict[str, Dict]) -> None:
    lines: List[str] = []
    lines.append("# Step15 外部基线对照（同口径）")
    lines.append("")
    lines.append("## 设计")
    lines.append("- `full`: 完整方法（full binding + strict_high guards）")
    lines.append("- `uie_only`: 仅使用 Step4 机制绑定，不使用候选重绑定")
    lines.append("- `rule_only`: 忽略 Step4 机制先验/回退，仅靠规则候选")
    lines.append("- `no_rebind`: `bind_min_score=99`，近似关闭候选驱动重绑定")
    lines.append("- `no_gate`: 关闭 strict_high guards（strict_high=strict_all）")
    lines.append("")
    lines.append("## 结果表")
    lines.append(
        "| baseline | valid_all | valid_numeric | norm_matched | mech_bound(valid_all) | strict_high(valid_all) | local_supported(valid_all) | all_targets_passed |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
    for r in rows:
        lines.append(
            f"| {r['baseline']} | {r['valid_all']} | {r['valid_numeric']} | {r['normalization_matched_rate']:.6f} | "
            f"{r['mechanism_bound_rate_valid_all']:.6f} | {r['strict_high_rate_valid_all']:.6f} | "
            f"{r['local_supported_rate_valid_all']:.6f} | {r['all_targets_passed']} |"
        )
    lines.append("")
    lines.append("## 运行记录")
    for k, v in runs.items():
        lines.append(f"- {k}: return_code={v['return_code']}, elapsed_sec={v['elapsed_sec']}, cmd=`{v['command']}`")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Step15 external baseline report.")
    parser.add_argument(
        "--clause-pred-file",
        type=str,
        default="00_整理记录/step4_seq_step2_clause_predictions.jsonl",
        help="Clause prediction file.",
    )
    parser.add_argument(
        "--clause-source-file",
        type=str,
        default="00_整理记录/step3_clause_corpus.jsonl",
        help="Clause corpus file.",
    )
    parser.add_argument(
        "--output-prefix",
        type=str,
        default="step15_baseline",
        help="Output prefix under 00_整理记录.",
    )
    parser.add_argument(
        "--python-bin",
        type=str,
        default="python3",
        help="Python executable.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_cmd = [
        args.python_bin,
        "00_整理记录/scripts/run_step5_normalize_validate.py",
        "--clause-pred-file",
        args.clause_pred_file,
        "--clause-source-file",
        args.clause_source_file,
        "--strict-high-threshold",
        "0.6",
        "--bind-min-score",
        "1.0",
    ]

    variants = {
        "full": ["--output-prefix", f"{args.output_prefix}_full", "--binding-mode", "full"],
        "uie_only": ["--output-prefix", f"{args.output_prefix}_uie_only", "--binding-mode", "uie_only"],
        "rule_only": ["--output-prefix", f"{args.output_prefix}_rule_only", "--binding-mode", "rule_only"],
        "no_rebind": [
            "--output-prefix",
            f"{args.output_prefix}_no_rebind",
            "--binding-mode",
            "full",
            "--bind-min-score",
            "99",
        ],
        "no_gate": [
            "--output-prefix",
            f"{args.output_prefix}_no_gate",
            "--binding-mode",
            "full",
            "--disable-strict-high-guards",
        ],
    }

    run_log: Dict[str, Dict] = {}
    reports: Dict[str, Dict] = {}
    for name, extra in variants.items():
        cmd = list(base_cmd) + extra
        run_log[name] = run_cmd(cmd)
        if run_log[name]["return_code"] != 0:
            raise RuntimeError(f"baseline {name} failed: {run_log[name]['stderr_tail']}")
        report_path = RECORD_DIR / f"{args.output_prefix}_{name}_validation_report.json"
        rep = read_json(report_path)
        rep["_report_path"] = str(report_path.relative_to(REPO_ROOT))
        reports[name] = rep

    rows = build_rows(reports)
    csv_path = RECORD_DIR / f"{args.output_prefix}_comparison.csv"
    json_path = RECORD_DIR / f"{args.output_prefix}_comparison.json"
    md_path = RECORD_DIR / f"{args.output_prefix}_comparison.md"

    fields = [
        "baseline",
        "binding_mode",
        "disable_strict_high_guards",
        "bind_min_score",
        "strict_high_threshold",
        "valid_all",
        "valid_numeric",
        "normalization_matched_rate",
        "mechanism_bound_rate_valid_all",
        "mechanism_bound_rate_valid_numeric",
        "strict_high_rate_valid_numeric",
        "strict_high_rate_valid_all",
        "local_supported_rate_valid_numeric",
        "local_supported_rate_valid_all",
        "all_targets_passed",
        "report_path",
    ]
    write_csv(csv_path, rows, fields)
    json_path.write_text(
        json.dumps(
            {
                "variants": variants,
                "runs": run_log,
                "rows": rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_md(md_path, rows, run_log)

    print(
        json.dumps(
            {
                "comparison_csv": str(csv_path.relative_to(REPO_ROOT)),
                "comparison_json": str(json_path.relative_to(REPO_ROOT)),
                "comparison_md": str(md_path.relative_to(REPO_ROOT)),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
