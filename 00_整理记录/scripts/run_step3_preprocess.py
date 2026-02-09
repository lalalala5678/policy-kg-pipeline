from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List

from step3_preprocess_utils import (
    OUTPUT_DIR,
    PIPELINE_PARAMS,
    PREPROCESS_VERSION,
    build_unit_documents,
    get_git_commit,
    list_source_txt_files,
    mapping_roundtrip_mismatch_count,
    now_str,
    preprocess_text_with_offset,
    segment_clauses,
    sha256_text,
    stable_hash_obj,
    summarize_clause_lengths,
)


def write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_markdown_report(qc: Dict) -> str:
    lines = [
        "# Step3 预处理与切分体检报告",
        "",
        f"- 生成时间: {qc['generated_at']}",
        f"- preprocess_version: {qc['preprocess_version']}",
        f"- git_commit: {qc['git_commit']}",
        f"- pipeline_params_hash: {qc['pipeline_params_hash']}",
        "",
        "## 输入与切分规模",
        f"- 原始 source 文件数: {qc['source_file_count']}",
        f"- 独立 unit 文档数: {qc['unit_document_count']}",
        f"- 汇总拼接来源文件数: {qc['compiled_source_file_count']}",
        f"- 汇总拆分后 chunk 数: {qc['compiled_chunk_count']}",
        f"- 编码使用统计: {qc['encoding_used_count']}",
        "",
        "## 文本预处理变化",
        f"- 总 raw 字符数: {qc['raw_char_total']}",
        f"- 总 clean 字符数: {qc['clean_char_total']}",
        f"- 删除 BOM: {qc['preprocess_change_counts']['removed_bom_count']}",
        f"- CRLF 归一: {qc['preprocess_change_counts']['collapsed_crlf_count']}",
        f"- CR 转 LF: {qc['preprocess_change_counts']['converted_cr_count']}",
        f"- 删除控制字符: {qc['preprocess_change_counts']['removed_control_count']}",
        "",
        "## Offset 映射质量",
        f"- 映射 mismatch 文档数: {qc['offset_mapping_qc']['docs_with_mismatch']}",
        f"- mismatch 字符总数: {qc['offset_mapping_qc']['mismatch_char_total']}",
        f"- mismatch 比例: {qc['offset_mapping_qc']['mismatch_ratio']}",
        "",
        "## 条款切分质量",
        f"- clause 总数: {qc['clause_qc']['clause_total']}",
        f"- 无 clause 文档数: {qc['clause_qc']['docs_without_clause']}",
        f"- 平均 clause/文档: {qc['clause_qc']['avg_clause_per_doc']}",
        f"- clause 长度统计: {qc['clause_qc']['length_summary']}",
        f"- clause 类型分布: {qc['clause_qc']['clause_type_distribution']}",
        "",
        "## 门禁结果",
        f"- all_doc_have_ids: {qc['quality_gates']['all_doc_have_ids']}",
        f"- all_clause_span_valid: {qc['quality_gates']['all_clause_span_valid']}",
        f"- no_offset_mismatch: {qc['quality_gates']['no_offset_mismatch']}",
        f"- clause_non_empty_rate_ge_99: {qc['quality_gates']['clause_non_empty_rate_ge_99']}",
        f"- clause_max_len_le_400: {qc['quality_gates']['clause_max_len_le_400']}",
        f"- overall_pass: {qc['quality_gates']['overall_pass']}",
        "",
        "## 产物",
        "- `00_整理记录/step3_input_manifest.json`",
        "- `00_整理记录/step3_document_corpus.jsonl`",
        "- `00_整理记录/step3_clause_corpus.jsonl`",
        "- `00_整理记录/step3_offset_map.jsonl`",
        "- `00_整理记录/step3_qc_report.json`",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    source_files = list_source_txt_files()
    unit_docs, source_meta_rows, encoding_counter = build_unit_documents(source_files)
    pipeline_params_hash = stable_hash_obj(PIPELINE_PARAMS)
    git_commit = get_git_commit()

    manifest_rows: List[Dict] = []
    doc_rows: List[Dict] = []
    clause_rows: List[Dict] = []
    offset_rows: List[Dict] = []

    preprocess_change_counts = Counter()
    clause_type_counter = Counter()
    clause_lengths: List[int] = []
    docs_without_clause = 0
    docs_with_table_clause = 0
    docs_with_mismatch = 0
    mismatch_char_total = 0
    raw_char_total = 0
    clean_char_total = 0
    clause_span_invalid = 0
    clause_non_empty = 0

    for unit in unit_docs:
        prep = preprocess_text_with_offset(unit.raw_text)
        raw_len = len(unit.raw_text)
        clean_len = len(prep.clean_text)
        raw_char_total += raw_len
        clean_char_total += clean_len

        preprocess_change_counts["removed_bom_count"] += prep.removed_bom_count
        preprocess_change_counts["collapsed_crlf_count"] += prep.collapsed_crlf_count
        preprocess_change_counts["converted_cr_count"] += prep.converted_cr_count
        preprocess_change_counts["removed_control_count"] += prep.removed_control_count

        mismatch = mapping_roundtrip_mismatch_count(unit.raw_text, prep.clean_text, prep)
        mismatch_char_total += mismatch
        if mismatch > 0:
            docs_with_mismatch += 1

        clauses = segment_clauses(clean_text=prep.clean_text, raw_len=raw_len, preprocess_result=prep)
        if not clauses:
            docs_without_clause += 1

        has_table_clause = False
        for idx, clause in enumerate(clauses):
            clause_id = f"{unit.doc_instance_id}#clause_{idx:04d}"
            clause_text = clause["clause_text"]
            clause_non_empty += 1 if clause_text else 0
            clause_lengths.append(clause["char_count"])
            clause_type_counter[clause["clause_type_prelim"]] += 1

            if clause["is_table_row_clause"]:
                has_table_clause = True

            if not (0 <= clause["clean_span_start"] < clause["clean_span_end"] <= clean_len):
                clause_span_invalid += 1
            if not (0 <= clause["raw_span_start"] < clause["raw_span_end"] <= raw_len):
                clause_span_invalid += 1

            clause_rows.append(
                {
                    "clause_id": clause_id,
                    "doc_id": unit.doc_id,
                    "doc_instance_id": unit.doc_instance_id,
                    "source_path": unit.source_path,
                    "parent_source_path": unit.parent_source_path,
                    "clause_index": idx,
                    "clause_type_prelim": clause["clause_type_prelim"],
                    "article_no": clause["article_no"],
                    "clause_text": clause_text,
                    "clean_span_start": clause["clean_span_start"],
                    "clean_span_end": clause["clean_span_end"],
                    "raw_span_start": clause["raw_span_start"],
                    "raw_span_end": clause["raw_span_end"],
                    "evidence_scope": "clause",
                    "evidence_anchor_id": clause_id,
                    "preprocess_version": PREPROCESS_VERSION,
                    "pipeline_params_hash": pipeline_params_hash,
                }
            )

        if has_table_clause:
            docs_with_table_clause += 1

        manifest_rows.append(
            {
                "doc_id": unit.doc_id,
                "doc_instance_id": unit.doc_instance_id,
                "source_path": unit.source_path,
                "parent_source_path": unit.parent_source_path,
                "chunk_index": unit.chunk_index,
                "chunk_title": unit.chunk_title,
                "chunk_raw_start": unit.chunk_raw_start,
                "chunk_raw_end": unit.chunk_raw_end,
                "is_compiled_chunk": unit.is_compiled_chunk,
                "source_file_sha256": unit.source_file_sha256,
                "source_bytes": unit.source_bytes,
                "raw_text_sha256": unit.raw_text_sha256,
                "encoding_used": unit.encoding_used,
                "raw_char_count": raw_len,
                "clean_char_count": clean_len,
                "offset_map_summary": {
                    "clean_to_raw_len": len(prep.clean_to_raw_start),
                    "raw_to_clean_len": len(prep.raw_to_clean),
                    "mapping_roundtrip_mismatch": mismatch,
                },
                "preprocess_version": PREPROCESS_VERSION,
                "pipeline_params_hash": pipeline_params_hash,
                "git_commit": git_commit,
            }
        )

        doc_rows.append(
            {
                "doc_id": unit.doc_id,
                "doc_instance_id": unit.doc_instance_id,
                "source_path": unit.source_path,
                "parent_source_path": unit.parent_source_path,
                "chunk_index": unit.chunk_index,
                "chunk_title": unit.chunk_title,
                "is_compiled_chunk": unit.is_compiled_chunk,
                "encoding_used": unit.encoding_used,
                "source_file_sha256": unit.source_file_sha256,
                "raw_text_sha256": unit.raw_text_sha256,
                "clean_text_sha256": sha256_text(prep.clean_text),
                "raw_char_count": raw_len,
                "clean_char_count": clean_len,
                "text_clean": prep.clean_text,
                "preprocess_change_count": {
                    "removed_bom_count": prep.removed_bom_count,
                    "collapsed_crlf_count": prep.collapsed_crlf_count,
                    "converted_cr_count": prep.converted_cr_count,
                    "removed_control_count": prep.removed_control_count,
                },
                "mapping_roundtrip_mismatch": mismatch,
                "preprocess_version": PREPROCESS_VERSION,
                "pipeline_params_hash": pipeline_params_hash,
            }
        )

        offset_rows.append(
            {
                "doc_instance_id": unit.doc_instance_id,
                "source_path": unit.source_path,
                "raw_char_count": raw_len,
                "clean_char_count": clean_len,
                "clean_to_raw_start": prep.clean_to_raw_start,
                "clean_to_raw_end": prep.clean_to_raw_end,
                "raw_to_clean": prep.raw_to_clean,
            }
        )

    clause_total = len(clause_rows)
    unit_doc_count = len(unit_docs)
    clause_non_empty_rate = round((clause_non_empty / clause_total) if clause_total else 0.0, 6)
    mismatch_ratio = round((mismatch_char_total / clean_char_total) if clean_char_total else 0.0, 8)

    quality_gates = {
        "all_doc_have_ids": all(x.get("doc_id") and x.get("doc_instance_id") for x in manifest_rows),
        "all_clause_span_valid": clause_span_invalid == 0,
        "no_offset_mismatch": mismatch_char_total == 0,
        "clause_non_empty_rate_ge_99": clause_non_empty_rate >= 0.99,
        "clause_max_len_le_400": max(clause_lengths) <= 400 if clause_lengths else True,
    }
    quality_gates["overall_pass"] = all(quality_gates.values())

    qc_report = {
        "generated_at": now_str(),
        "preprocess_version": PREPROCESS_VERSION,
        "git_commit": git_commit,
        "pipeline_params_hash": pipeline_params_hash,
        "source_file_count": len(source_files),
        "unit_document_count": unit_doc_count,
        "compiled_source_file_count": sum(1 for x in source_meta_rows if x["is_compiled_source"]),
        "compiled_chunk_count": sum(1 for x in manifest_rows if x["is_compiled_chunk"]),
        "encoding_used_count": dict(encoding_counter),
        "raw_char_total": raw_char_total,
        "clean_char_total": clean_char_total,
        "preprocess_change_counts": dict(preprocess_change_counts),
        "offset_mapping_qc": {
            "docs_with_mismatch": docs_with_mismatch,
            "mismatch_char_total": mismatch_char_total,
            "mismatch_ratio": mismatch_ratio,
        },
        "clause_qc": {
            "clause_total": clause_total,
            "docs_without_clause": docs_without_clause,
            "docs_with_table_clause": docs_with_table_clause,
            "avg_clause_per_doc": round((clause_total / unit_doc_count) if unit_doc_count else 0.0, 4),
            "length_summary": summarize_clause_lengths(clause_lengths),
            "clause_type_distribution": dict(clause_type_counter),
            "clause_span_invalid_count": clause_span_invalid,
            "clause_non_empty_rate": clause_non_empty_rate,
        },
        "quality_gates": quality_gates,
        "artifacts": {
            "manifest": "00_整理记录/step3_input_manifest.json",
            "document_corpus": "00_整理记录/step3_document_corpus.jsonl",
            "clause_corpus": "00_整理记录/step3_clause_corpus.jsonl",
            "offset_map": "00_整理记录/step3_offset_map.jsonl",
        },
    }

    manifest = {
        "generated_at": now_str(),
        "preprocess_version": PREPROCESS_VERSION,
        "git_commit": git_commit,
        "pipeline_params_hash": pipeline_params_hash,
        "doc_id_rule": {
            "doc_id": "sha256(unit_raw_text)  # content hash as stable primary key",
            "doc_instance_id": "sha256(source_path + source_file_sha256 + chunk_index + raw_text_sha256)",
            "why": "doc_id remains stable under path rename; doc_instance_id preserves lineage",
        },
        "decode_strategy": ["utf-8", "gb18030_fallback"],
        "source_file_count": len(source_files),
        "unit_document_count": unit_doc_count,
        "source_files": source_meta_rows,
        "unit_documents": manifest_rows,
    }

    write_json(OUTPUT_DIR / "step3_input_manifest.json", manifest)
    write_jsonl(OUTPUT_DIR / "step3_document_corpus.jsonl", doc_rows)
    write_jsonl(OUTPUT_DIR / "step3_clause_corpus.jsonl", clause_rows)
    write_jsonl(OUTPUT_DIR / "step3_offset_map.jsonl", offset_rows)
    write_json(OUTPUT_DIR / "step3_qc_report.json", qc_report)
    (OUTPUT_DIR / "step3_qc_report.md").write_text(build_markdown_report(qc_report), encoding="utf-8")

    debug_rows = {
        "docs_with_mismatch_top20": [x for x in manifest_rows if x["offset_map_summary"]["mapping_roundtrip_mismatch"] > 0][
            :20
        ],
        "docs_without_clause_top20": [x for x in manifest_rows if x["source_path"] not in {c["source_path"] for c in clause_rows}][
            :20
        ],
        "clause_samples_top30": clause_rows[:30],
    }
    write_json(OUTPUT_DIR / "step3_debug_samples.json", debug_rows)
    print("step3 done")


if __name__ == "__main__":
    main()
