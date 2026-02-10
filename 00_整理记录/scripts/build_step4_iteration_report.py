from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "00_整理记录"


ITER_FILES = [
    ("iter0_baseline", OUTPUT_DIR / "step4_iter0_baseline_kb_score.json"),
    ("iter1_v1", OUTPUT_DIR / "step4_iter1_v1_kb_score.json"),
    ("iter2_v2", OUTPUT_DIR / "step4_iter2_v2_kb_score.json"),
    ("iter3_v2plus", OUTPUT_DIR / "step4_iter3_v2plus_kb_score.json"),
]


def main() -> None:
    rows = []
    for name, path in ITER_FILES:
        if not path.exists():
            continue
        obj = json.loads(path.read_text(encoding="utf-8"))
        m = obj["metrics"]
        s = obj["scores"]
        rows.append(
            {
                "iteration": name,
                "total_score": s["total_score"],
                "structure_score": s["structure_score"],
                "evidence_score": s["evidence_score"],
                "doc_score": s["doc_score"],
                "clause_score": s["clause_score"],
                "mechanism_non_empty_rate": m["mechanism_non_empty_rate"],
                "clause_type_non_empty_rate": m["clause_type_non_empty_rate"],
                "raw_non_empty_rate": m["raw_non_empty_rate"],
                "strict_triplet_ready_rate": m["strict_triplet_ready_rate"],
                "param_bind_rate": m["param_bind_rate"],
                "task_ready_rate": m["task_ready_rate"],
                "doc_min_ready_rate": m["doc_min_ready_rate"],
                "doc_rich_ready_rate": m["doc_rich_ready_rate"],
                "is_good": obj["is_good"],
            }
        )

    out_json = OUTPUT_DIR / "step4_iteration_scores.json"
    out_md = OUTPUT_DIR / "step4_iteration_scores.md"
    out_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Step4 Iteration Scores",
        "",
        "| iteration | total | structure | evidence | doc | clause | mechanism_rate | clause_type_rate | raw_rate | strict_triplet_rate | bind_rate | task_rate | is_good |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for x in rows:
        lines.append(
            f"| {x['iteration']} | {x['total_score']:.3f} | {x['structure_score']:.3f} | {x['evidence_score']:.3f} | {x['doc_score']:.3f} | {x['clause_score']:.3f} | {x['mechanism_non_empty_rate']:.4f} | {x['clause_type_non_empty_rate']:.4f} | {x['raw_non_empty_rate']:.4f} | {x['strict_triplet_ready_rate']:.4f} | {x['param_bind_rate']:.4f} | {x['task_ready_rate']:.4f} | {x['is_good']} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("- score excludes runtime performance; it only targets KB import usability.")
    lines.append("- strict_triplet_ready_rate uses: mechanism_type + clause_type + numeric raw_value.")

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("report done")


if __name__ == "__main__":
    main()
