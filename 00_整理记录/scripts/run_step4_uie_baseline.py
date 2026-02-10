from __future__ import annotations

import argparse
import json
import re
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import paddle
from paddlenlp import Taskflow


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "00_整理记录"


DOC_FIELD_TO_LABEL = {
    "title": "\u6807\u9898",
    "document_no": "\u6587\u53f7",
    "issue_date": "\u53d1\u5e03\u65e5\u671f",
    "effective_start_date": "\u5b9e\u65bd\u8d77\u59cb\u65e5\u671f",
    "effective_end_date": "\u5b9e\u65bd\u7ed3\u675f\u65e5\u671f",
    "org_name": "\u53d1\u6587\u673a\u6784",
    "region_name": "\u9002\u7528\u5730\u533a",
    "target_name": "\u9002\u7528\u5bf9\u8c61",
}

CLAUSE_FIELD_TO_LABEL = {
    "mechanism_type": "\u673a\u5236\u7c7b\u578b",
    "mechanism_name": "\u673a\u5236\u540d\u79f0",
    "clause_type": "\u6761\u6b3e\u7c7b\u578b",
    "raw_value": "\u53c2\u6570\u503c",
    "raw_unit": "\u53c2\u6570\u5355\u4f4d",
    "direction": "\u65b9\u5411",
    "condition_text": "\u6761\u4ef6",
    "task_subject": "\u4efb\u52a1\u4e3b\u4f53",
    "task_action": "\u4efb\u52a1\u52a8\u4f5c",
    "task_deadline": "\u4efb\u52a1\u671f\u9650",
    "task_assessment": "\u4efb\u52a1\u8003\u6838",
}


def read_jsonl(path: Path) -> List[Dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def ensure_result_list(raw_result: object) -> List[Dict]:
    if isinstance(raw_result, list):
        return [x for x in raw_result if isinstance(x, dict)]
    if isinstance(raw_result, dict):
        return [raw_result]
    return []


def now_hms() -> str:
    return datetime.now().strftime("%H:%M:%S")


def extract_source_path_from_text_blob(text: str) -> str | None:
    if not text:
        return None
    m = re.search(r"【SOURCE_PATH】([^\r\n]+)", text)
    if not m:
        return None
    return m.group(1).strip()


def normalize_items(items: List[Dict], min_prob: float) -> List[Dict]:
    normalized = []
    for item in items or []:
        prob = float(item.get("probability", 0.0))
        if prob < min_prob:
            continue
        start = item.get("start")
        end = item.get("end")
        normalized.append(
            {
                "text": item.get("text"),
                "start": int(start) if start is not None else None,
                "end": int(end) if end is not None else None,
                "probability": round(prob, 6),
            }
        )
    return normalized


def map_result_by_schema(result_obj: Dict, field_to_label: Dict[str, str], min_prob: float) -> Dict[str, List[Dict]]:
    mapped: Dict[str, List[Dict]] = {}
    for field, label in field_to_label.items():
        mapped[field] = normalize_items(result_obj.get(label, []), min_prob=min_prob)
    return mapped


def batched(items: List[Dict], batch_size: int) -> Iterable[List[Dict]]:
    for idx in range(0, len(items), batch_size):
        yield items[idx : idx + batch_size]


def build_doc_input_text(doc_row: Dict, text_max_chars: int) -> str:
    if doc_row.get("text"):
        return (doc_row.get("text") or "")[:text_max_chars]
    title = doc_row.get("chunk_title") or doc_row.get("title") or ""
    clean_text = doc_row.get("text_clean") or ""
    clean_text = clean_text[:text_max_chars]
    return f"{title}\n{clean_text}".strip()


def build_clause_input_text(clause_row: Dict, text_max_chars: int) -> str:
    text = clause_row.get("clause_text") or clause_row.get("text") or ""
    return text[:text_max_chars]


def build_doc_keys(row: Dict, idx: int) -> Dict[str, str]:
    doc_id = row.get("doc_id") or row.get("id") or f"doc_{idx}"
    doc_instance_id = row.get("doc_instance_id") or f"docinst_{doc_id}"
    source_path = row.get("source_path") or extract_source_path_from_text_blob(row.get("text", "")) or ""
    return {"doc_id": str(doc_id), "doc_instance_id": str(doc_instance_id), "source_path": source_path}


def build_clause_keys(row: Dict, idx: int) -> Dict[str, str]:
    clause_id = row.get("clause_id") or row.get("id") or f"clause_{idx}"
    doc_instance_id = row.get("doc_instance_id") or f"docinst_{clause_id}"
    source_path = row.get("source_path") or extract_source_path_from_text_blob(row.get("text", "")) or ""
    return {"clause_id": str(clause_id), "doc_instance_id": str(doc_instance_id), "source_path": source_path}


def count_non_empty_field(pred_rows: List[Dict], fields: Iterable[str]) -> Dict[str, int]:
    counters = {field: 0 for field in fields}
    for row in pred_rows:
        pred = row["prediction"]
        for field in fields:
            if pred.get(field):
                counters[field] += 1
    return counters


def run_doc_level(
    doc_rows: List[Dict],
    batch_size: int,
    text_max_chars: int,
    min_prob: float,
    progress_every: int,
) -> Tuple[List[Dict], Dict[str, int], float, Dict[str, int]]:
    model = Taskflow("information_extraction", schema=list(DOC_FIELD_TO_LABEL.values()))
    output_rows: List[Dict] = []
    start_t = time.time()
    batch_error_count = 0
    item_error_count = 0
    total_batches = max((len(doc_rows) + batch_size - 1) // batch_size, 1)
    print(f"[{now_hms()}] doc-level start: rows={len(doc_rows)}, batches={total_batches}", flush=True)

    global_idx = 0
    for batch_idx, batch in enumerate(batched(doc_rows, batch_size=batch_size), start=1):
        input_texts = [build_doc_input_text(x, text_max_chars=text_max_chars) for x in batch]
        try:
            results = ensure_result_list(model(input_texts))
            if len(results) != len(batch):
                raise RuntimeError(f"batch result size mismatch: got={len(results)} expect={len(batch)}")
            has_batch_error = False
        except Exception as ex:
            has_batch_error = True
            batch_error_count += 1
            print(f"[{now_hms()}] doc-level batch {batch_idx} failed, fallback single: {ex}", flush=True)
            results = []
            for row, source_text in zip(batch, input_texts):
                global_idx += 1
                keys = build_doc_keys(row, idx=global_idx)
                try:
                    single_result = ensure_result_list(model([source_text]))
                    result_obj = single_result[0] if single_result else {}
                    error_msg = None
                except Exception as ex_single:
                    item_error_count += 1
                    result_obj = {}
                    error_msg = str(ex_single)
                mapped = map_result_by_schema(result_obj, field_to_label=DOC_FIELD_TO_LABEL, min_prob=min_prob)
                output_rows.append(
                    {
                        "doc_id": keys["doc_id"],
                        "doc_instance_id": keys["doc_instance_id"],
                        "source_path": keys["source_path"],
                        "input_text_preview": source_text[:300],
                        "prediction": mapped,
                        "error": error_msg,
                    }
                )
        if has_batch_error:
            if progress_every > 0 and (batch_idx % progress_every == 0 or batch_idx == total_batches):
                print(f"[{now_hms()}] doc-level progress: {batch_idx}/{total_batches}", flush=True)
            continue

        for row, result_obj, source_text in zip(batch, results, input_texts):
            global_idx += 1
            keys = build_doc_keys(row, idx=global_idx)
            mapped = map_result_by_schema(result_obj, field_to_label=DOC_FIELD_TO_LABEL, min_prob=min_prob)
            output_rows.append(
                {
                    "doc_id": keys["doc_id"],
                    "doc_instance_id": keys["doc_instance_id"],
                    "source_path": keys["source_path"],
                    "input_text_preview": source_text[:300],
                    "prediction": mapped,
                }
            )
        if progress_every > 0 and (batch_idx % progress_every == 0 or batch_idx == total_batches):
            print(f"[{now_hms()}] doc-level progress: {batch_idx}/{total_batches}", flush=True)

    elapsed = time.time() - start_t
    hit_counts = count_non_empty_field(output_rows, DOC_FIELD_TO_LABEL.keys())
    stats = {
        "batch_error_count": batch_error_count,
        "item_error_count": item_error_count,
    }
    print(f"[{now_hms()}] doc-level done: elapsed={round(elapsed, 2)}s", flush=True)
    return output_rows, hit_counts, elapsed, stats


def run_clause_level(
    clause_rows: List[Dict],
    batch_size: int,
    min_prob: float,
    text_max_chars: int,
    progress_every: int,
) -> Tuple[List[Dict], Dict[str, int], float, Dict[str, int]]:
    model = Taskflow("information_extraction", schema=list(CLAUSE_FIELD_TO_LABEL.values()))
    output_rows: List[Dict] = []
    start_t = time.time()
    batch_error_count = 0
    item_error_count = 0
    truncated_input_count = 0
    total_batches = max((len(clause_rows) + batch_size - 1) // batch_size, 1)
    print(f"[{now_hms()}] clause-level start: rows={len(clause_rows)}, batches={total_batches}", flush=True)

    global_idx = 0
    for batch_idx, batch in enumerate(batched(clause_rows, batch_size=batch_size), start=1):
        input_texts = []
        for row in batch:
            original_text = row.get("clause_text") or row.get("text") or ""
            if len(original_text) > text_max_chars:
                truncated_input_count += 1
            input_texts.append(build_clause_input_text(row, text_max_chars=text_max_chars))
        try:
            results = ensure_result_list(model(input_texts))
            if len(results) != len(batch):
                raise RuntimeError(f"batch result size mismatch: got={len(results)} expect={len(batch)}")
            has_batch_error = False
        except Exception as ex:
            has_batch_error = True
            batch_error_count += 1
            print(f"[{now_hms()}] clause-level batch {batch_idx} failed, fallback single: {ex}", flush=True)
            for row, source_text in zip(batch, input_texts):
                global_idx += 1
                keys = build_clause_keys(row, idx=global_idx)
                try:
                    single_result = ensure_result_list(model([source_text]))
                    result_obj = single_result[0] if single_result else {}
                    error_msg = None
                except Exception as ex_single:
                    item_error_count += 1
                    result_obj = {}
                    error_msg = str(ex_single)
                mapped = map_result_by_schema(result_obj, field_to_label=CLAUSE_FIELD_TO_LABEL, min_prob=min_prob)
                output_rows.append(
                    {
                        "clause_id": keys["clause_id"],
                        "doc_instance_id": keys["doc_instance_id"],
                        "source_path": keys["source_path"],
                        "input_text_preview": source_text[:300],
                        "prediction": mapped,
                        "error": error_msg,
                    }
                )
        if has_batch_error:
            if progress_every > 0 and (batch_idx % progress_every == 0 or batch_idx == total_batches):
                print(f"[{now_hms()}] clause-level progress: {batch_idx}/{total_batches}", flush=True)
            continue

        for row, result_obj, source_text in zip(batch, results, input_texts):
            global_idx += 1
            keys = build_clause_keys(row, idx=global_idx)
            mapped = map_result_by_schema(result_obj, field_to_label=CLAUSE_FIELD_TO_LABEL, min_prob=min_prob)
            output_rows.append(
                {
                    "clause_id": keys["clause_id"],
                    "doc_instance_id": keys["doc_instance_id"],
                    "source_path": keys["source_path"],
                    "input_text_preview": source_text[:300],
                    "prediction": mapped,
                }
            )
        if progress_every > 0 and (batch_idx % progress_every == 0 or batch_idx == total_batches):
            print(f"[{now_hms()}] clause-level progress: {batch_idx}/{total_batches}", flush=True)

    elapsed = time.time() - start_t
    hit_counts = count_non_empty_field(output_rows, CLAUSE_FIELD_TO_LABEL.keys())
    stats = {
        "batch_error_count": batch_error_count,
        "item_error_count": item_error_count,
        "truncated_input_count": truncated_input_count,
    }
    print(f"[{now_hms()}] clause-level done: elapsed={round(elapsed, 2)}s", flush=True)
    return output_rows, hit_counts, elapsed, stats


def top_sources_by_predictions(rows: List[Dict], key: str, top_n: int = 20) -> List[Tuple[str, int]]:
    counter = Counter()
    for row in rows:
        pred = row["prediction"]
        hit = sum(1 for v in pred.values() if v)
        if hit > 0:
            counter[row[key]] += hit
    return counter.most_common(top_n)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Step4 UIE baseline extraction on Step3 corpora.")
    parser.add_argument(
        "--doc-source-file",
        type=str,
        default="00_整理记录/step3_document_corpus.jsonl",
        help="Path to doc-level JSONL source relative to project root",
    )
    parser.add_argument(
        "--clause-source-file",
        type=str,
        default="00_整理记录/step3_clause_corpus.jsonl",
        help="Path to clause-level JSONL source relative to project root",
    )
    parser.add_argument("--output-prefix", type=str, default="step4_uie")
    parser.add_argument(
        "--stages",
        type=str,
        choices=["both", "doc", "clause"],
        default="both",
        help="Run doc-level, clause-level, or both",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        help="Device to use, e.g. auto/cpu/gpu:0",
    )
    parser.add_argument("--doc-limit", type=int, default=0, help="0 means all documents")
    parser.add_argument("--clause-limit", type=int, default=0, help="0 means all clauses")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--doc-text-max-chars", type=int, default=1600)
    parser.add_argument("--clause-text-max-chars", type=int, default=400)
    parser.add_argument("--doc-progress-every", type=int, default=10)
    parser.add_argument("--clause-progress-every", type=int, default=50)
    parser.add_argument("--min-prob", type=float, default=0.3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.device == "auto":
        if paddle.is_compiled_with_cuda():
            selected_device = "gpu:0"
        else:
            selected_device = "cpu"
    else:
        selected_device = args.device
    paddle.set_device(selected_device)
    print(
        f"[{now_hms()}] runtime device={selected_device}, compiled_with_cuda={paddle.is_compiled_with_cuda()}",
        flush=True,
    )

    doc_source = PROJECT_ROOT / args.doc_source_file
    clause_source = PROJECT_ROOT / args.clause_source_file

    if not doc_source.exists():
        raise FileNotFoundError(f"doc source not found: {doc_source}")
    if not clause_source.exists():
        raise FileNotFoundError(f"clause source not found: {clause_source}")

    doc_rows = read_jsonl(doc_source)
    clause_rows = read_jsonl(clause_source)
    if args.stages in ("both", "doc") and args.doc_limit > 0:
        doc_rows = doc_rows[: args.doc_limit]
    if args.stages in ("both", "clause") and args.clause_limit > 0:
        clause_rows = clause_rows[: args.clause_limit]

    doc_pred_rows: List[Dict] = []
    doc_hit_counts: Dict[str, int] = {k: 0 for k in DOC_FIELD_TO_LABEL.keys()}
    doc_elapsed = 0.0
    doc_run_stats: Dict[str, int] = {"batch_error_count": 0, "item_error_count": 0}
    if args.stages in ("both", "doc"):
        doc_pred_rows, doc_hit_counts, doc_elapsed, doc_run_stats = run_doc_level(
            doc_rows=doc_rows,
            batch_size=args.batch_size,
            text_max_chars=args.doc_text_max_chars,
            min_prob=args.min_prob,
            progress_every=args.doc_progress_every,
        )

    clause_pred_rows: List[Dict] = []
    clause_hit_counts: Dict[str, int] = {k: 0 for k in CLAUSE_FIELD_TO_LABEL.keys()}
    clause_elapsed = 0.0
    clause_run_stats: Dict[str, int] = {
        "batch_error_count": 0,
        "item_error_count": 0,
        "truncated_input_count": 0,
    }
    if args.stages in ("both", "clause"):
        clause_pred_rows, clause_hit_counts, clause_elapsed, clause_run_stats = run_clause_level(
            clause_rows=clause_rows,
            batch_size=args.batch_size,
            min_prob=args.min_prob,
            text_max_chars=args.clause_text_max_chars,
            progress_every=args.clause_progress_every,
        )

    doc_pred_name = f"{args.output_prefix}_doc_predictions.jsonl"
    clause_pred_name = f"{args.output_prefix}_clause_predictions.jsonl"
    summary_json_name = f"{args.output_prefix}_summary.json"
    summary_md_name = f"{args.output_prefix}_summary.md"

    write_jsonl(OUTPUT_DIR / doc_pred_name, doc_pred_rows)
    write_jsonl(OUTPUT_DIR / clause_pred_name, clause_pred_rows)

    summary = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "run_config": {
            "stages": args.stages,
            "device": selected_device,
            "doc_limit": args.doc_limit,
            "clause_limit": args.clause_limit,
            "batch_size": args.batch_size,
            "doc_text_max_chars": args.doc_text_max_chars,
            "clause_text_max_chars": args.clause_text_max_chars,
            "min_prob": args.min_prob,
        },
        "input": {
            "doc_source_file": str(doc_source.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "clause_source_file": str(clause_source.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "doc_count": len(doc_rows) if args.stages in ("both", "doc") else 0,
            "clause_count": len(clause_rows) if args.stages in ("both", "clause") else 0,
        },
        "doc_level": {
            "elapsed_sec": round(doc_elapsed, 3),
            "throughput_doc_per_sec": round(len(doc_rows) / doc_elapsed, 3) if doc_elapsed else None,
            "non_empty_field_count": doc_hit_counts,
            "non_empty_field_rate": {
                k: round(v / len(doc_rows), 6) if doc_rows else 0.0 for k, v in doc_hit_counts.items()
            },
            "run_stats": doc_run_stats,
            "top_source_by_hit": top_sources_by_predictions(doc_pred_rows, key="source_path", top_n=20),
        },
        "clause_level": {
            "elapsed_sec": round(clause_elapsed, 3),
            "throughput_clause_per_sec": round(len(clause_rows) / clause_elapsed, 3) if clause_elapsed else None,
            "non_empty_field_count": clause_hit_counts,
            "non_empty_field_rate": {
                k: round(v / len(clause_rows), 6) if clause_rows else 0.0 for k, v in clause_hit_counts.items()
            },
            "run_stats": clause_run_stats,
            "top_source_by_hit": top_sources_by_predictions(clause_pred_rows, key="source_path", top_n=20),
        },
        "artifacts": {
            "doc_predictions": f"00_整理记录/{doc_pred_name}",
            "clause_predictions": f"00_整理记录/{clause_pred_name}",
        },
    }
    write_json(OUTPUT_DIR / summary_json_name, summary)

    md_lines = [
        "# Step4 UIE Baseline Summary",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- doc_count: {summary['input']['doc_count']}",
        f"- clause_count: {summary['input']['clause_count']}",
        "",
        "## Doc-level",
        f"- elapsed_sec: {summary['doc_level']['elapsed_sec']}",
        f"- throughput_doc_per_sec: {summary['doc_level']['throughput_doc_per_sec']}",
        f"- non_empty_field_rate: {summary['doc_level']['non_empty_field_rate']}",
        f"- run_stats: {summary['doc_level']['run_stats']}",
        "",
        "## Clause-level",
        f"- elapsed_sec: {summary['clause_level']['elapsed_sec']}",
        f"- throughput_clause_per_sec: {summary['clause_level']['throughput_clause_per_sec']}",
        f"- non_empty_field_rate: {summary['clause_level']['non_empty_field_rate']}",
        f"- run_stats: {summary['clause_level']['run_stats']}",
        "",
        "## Artifacts",
        f"- `00_整理记录/{doc_pred_name}`",
        f"- `00_整理记录/{clause_pred_name}`",
        f"- `00_整理记录/{summary_json_name}`",
    ]
    (OUTPUT_DIR / summary_md_name).write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print("step4 uie baseline done")


if __name__ == "__main__":
    main()
