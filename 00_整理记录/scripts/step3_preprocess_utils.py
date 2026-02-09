from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "00_整理记录"
PREPROCESS_VERSION = "step3_preprocess_v1.0"


SPLIT_ANCHOR_RE = re.compile(r"(?=<h2>file:)", flags=re.IGNORECASE)
SPLIT_TITLE_RE = re.compile(r"<h2>file:(.*?)</h2>", flags=re.IGNORECASE | re.DOTALL)


CLAUSE_BOUNDARY_PATTERNS: Sequence[re.Pattern[str]] = (
    re.compile(r"\u7b2c[\u4e00-\u9fa5\d]+\u6761"),
    re.compile(r"\u7b2c[\u4e00-\u9fa5\d]+\u6b3e"),
    re.compile(r"\u7b2c[\u4e00-\u9fa5\d]+\u9879"),
    re.compile(r"\uff08[\u4e00-\u9fa5\d]+\uff09"),
    re.compile(r"(?m)^\s*\d+\)"),
    re.compile(r"(?m)^\s*\d+\."),
    re.compile(r"(?m)^[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341]+\u3001"),
)
CLAUSE_PUNCT_RE = re.compile(r"[\uff1b\u3002]")
CLAUSE_COMMA_RE = re.compile(r"[\uff0c,]")
TABLE_COL_SPLIT_RE = re.compile(r"\t+|\s{2,}")


SUBSIDY_RE = re.compile(r"\u8865\u8d34|\u8865\u52a9|\u5956\u8865|\u5956\u52b1")
TASK_RE = re.compile(r"\u4efb\u52a1|\u76ee\u6807|\u8003\u6838|\u9a8c\u6536|\u8d23\u4efb\u5206\u5de5|\u5de5\u4f5c\u8981\u6c42")
TIME_RE = re.compile(r"\d{4}\u5e74|\d{1,2}\u6708\d{1,2}\u65e5|\u65f6\u6bb5|\u91c7\u6696\u5b63|\u81f3|\u671f\u95f4")
PRICING_RE = re.compile(
    r"\u7535\u4ef7|\u5206\u65f6|\u5cf0\u8c37|\u9636\u68af|\u5dee\u522b|\u4e0a\u6d6e|\u4e0b\u6d6e|\u4e0b\u8c03|\u52a0\u4ef7|\u964d\u4ef7"
)
SCOPE_RE = re.compile(r"\u9002\u7528|\u8303\u56f4|\u5bf9\u8c61|\u7528\u6237")
EXEC_RE = re.compile(r"\u6267\u884c|\u843d\u5b9e|\u7ec4\u7ec7|\u5b9e\u65bd|\u8d1f\u8d23")
DEF_RE = re.compile(r"\u662f\u6307|\u5b9a\u4e49")

ARTICLE_NO_RE = re.compile(
    r"^\s*(\u7b2c[\u4e00-\u9fa5\d]+[\u6761\u6b3e\u9879]|\uff08[\u4e00-\u9fa5\d]+\uff09|\d+[.)]|[\u4e00-\u9fa5]+\u3001)"
)


PIPELINE_PARAMS = {
    "decode_strategy": ["utf-8", "gb18030_fallback"],
    "compiled_split_anchor_regex": SPLIT_ANCHOR_RE.pattern,
    "compiled_split_title_regex": SPLIT_TITLE_RE.pattern,
    "preprocess": {
        "normalize_newline": True,
        "remove_bom": True,
        "remove_control_chars_excluding_tab_lf": True,
    },
    "clause_segmentation": {
        "boundary_patterns": [p.pattern for p in CLAUSE_BOUNDARY_PATTERNS],
        "punctuation_pattern": CLAUSE_PUNCT_RE.pattern,
        "comma_pattern": CLAUSE_COMMA_RE.pattern,
        "min_clause_chars": 20,
        "max_clause_chars": 400,
        "merge_short_tail": True,
        "table_row_fallback": {
            "enabled": True,
            "column_delimiter_regex": TABLE_COL_SPLIT_RE.pattern,
            "min_cells": 2,
        },
    },
}


@dataclass
class UnitRawDocument:
    source_path: str
    parent_source_path: str
    source_file_sha256: str
    source_bytes: int
    encoding_used: str
    chunk_index: int
    chunk_title: str
    chunk_raw_start: int
    chunk_raw_end: int
    raw_text: str
    raw_text_sha256: str
    doc_id: str
    doc_instance_id: str
    is_compiled_chunk: bool


@dataclass
class PreprocessResult:
    clean_text: str
    clean_to_raw_start: List[int]
    clean_to_raw_end: List[int]
    raw_to_clean: List[int]
    removed_bom_count: int
    collapsed_crlf_count: int
    converted_cr_count: int
    removed_control_count: int


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_hash_obj(obj: object) -> str:
    payload = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_text(payload)


def get_git_commit() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT)
        return out.decode("utf-8", errors="ignore").strip()
    except Exception:
        return "unknown"


def relative_path(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")


def list_source_txt_files() -> List[Path]:
    files: List[Path] = []
    for top in sorted(PROJECT_ROOT.iterdir(), key=lambda x: x.name):
        if not top.is_dir():
            continue
        if not top.name.startswith(("01_", "02_")):
            continue
        for p in top.rglob("*.txt"):
            files.append(p)
    return sorted(files, key=lambda x: str(x))


def decode_policy_bytes(data: bytes) -> Tuple[str, str]:
    try:
        return data.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return data.decode("gb18030", errors="ignore"), "gb18030"


def is_compiled_source(source_rel_path: str) -> bool:
    parts = source_rel_path.split("/")
    return len(parts) >= 2 and parts[0].startswith("02_") and parts[1].startswith("02_")


def split_compiled_text(raw_text: str, file_stem: str) -> List[Tuple[int, int, str, str]]:
    anchors = [m.start() for m in SPLIT_ANCHOR_RE.finditer(raw_text)]
    if not anchors:
        return [(0, len(raw_text), file_stem, raw_text)]

    chunks: List[Tuple[int, int, str, str]] = []
    if anchors[0] > 0:
        prefix = raw_text[: anchors[0]]
        if prefix.strip():
            chunks.append((0, anchors[0], f"{file_stem}_prefix", prefix))

    for idx, start in enumerate(anchors):
        end = anchors[idx + 1] if idx + 1 < len(anchors) else len(raw_text)
        chunk = raw_text[start:end]
        title_match = SPLIT_TITLE_RE.search(chunk[:800])
        if title_match:
            title = title_match.group(1).strip()
            title = re.sub(r"\s+", " ", title)
        else:
            title = f"{file_stem}_chunk_{idx}"
        chunks.append((start, end, title, chunk))
    return chunks


def build_unit_documents(files: Iterable[Path]) -> Tuple[List[UnitRawDocument], List[Dict[str, object]], Dict[str, int]]:
    units: List[UnitRawDocument] = []
    source_meta_rows: List[Dict[str, object]] = []
    encoding_counter: Dict[str, int] = {"utf-8": 0, "gb18030": 0}

    for path in files:
        data = path.read_bytes()
        source_sha = sha256_bytes(data)
        source_rel = relative_path(path)
        raw_text, encoding_used = decode_policy_bytes(data)
        encoding_counter[encoding_used] = encoding_counter.get(encoding_used, 0) + 1

        compiled = is_compiled_source(source_rel)
        chunks = split_compiled_text(raw_text, path.stem) if compiled else [(0, len(raw_text), path.stem, raw_text)]

        source_meta_rows.append(
            {
                "source_path": source_rel,
                "source_file_sha256": source_sha,
                "source_bytes": len(data),
                "source_char_count": len(raw_text),
                "encoding_used": encoding_used,
                "is_compiled_source": compiled,
                "split_unit_count": len(chunks),
            }
        )

        for chunk_index, (raw_start, raw_end, chunk_title, chunk_raw_text) in enumerate(chunks):
            chunk_raw_sha = sha256_text(chunk_raw_text)
            doc_id = chunk_raw_sha
            doc_instance_base = f"{source_rel}|{source_sha}|{chunk_index}|{chunk_raw_sha}"
            doc_instance_id = sha256_text(doc_instance_base)
            unit_source_path = source_rel if not compiled else f"{source_rel}#chunk_{chunk_index}"
            units.append(
                UnitRawDocument(
                    source_path=unit_source_path,
                    parent_source_path=source_rel,
                    source_file_sha256=source_sha,
                    source_bytes=len(data),
                    encoding_used=encoding_used,
                    chunk_index=chunk_index,
                    chunk_title=chunk_title,
                    chunk_raw_start=raw_start,
                    chunk_raw_end=raw_end,
                    raw_text=chunk_raw_text,
                    raw_text_sha256=chunk_raw_sha,
                    doc_id=doc_id,
                    doc_instance_id=doc_instance_id,
                    is_compiled_chunk=compiled,
                )
            )
    return units, source_meta_rows, encoding_counter


def preprocess_text_with_offset(raw_text: str) -> PreprocessResult:
    clean_chars: List[str] = []
    clean_to_raw_start: List[int] = []
    clean_to_raw_end: List[int] = []
    raw_to_clean = [-1] * len(raw_text)

    removed_bom_count = 0
    collapsed_crlf_count = 0
    converted_cr_count = 0
    removed_control_count = 0

    i = 0
    n = len(raw_text)
    while i < n:
        ch = raw_text[i]
        if ch == "\ufeff":
            removed_bom_count += 1
            i += 1
            continue

        if ch == "\r":
            if i + 1 < n and raw_text[i + 1] == "\n":
                clean_idx = len(clean_chars)
                clean_chars.append("\n")
                clean_to_raw_start.append(i)
                clean_to_raw_end.append(i + 2)
                raw_to_clean[i] = clean_idx
                raw_to_clean[i + 1] = clean_idx
                collapsed_crlf_count += 1
                i += 2
                continue
            clean_idx = len(clean_chars)
            clean_chars.append("\n")
            clean_to_raw_start.append(i)
            clean_to_raw_end.append(i + 1)
            raw_to_clean[i] = clean_idx
            converted_cr_count += 1
            i += 1
            continue

        if ord(ch) < 32 and ch not in ("\n", "\t"):
            removed_control_count += 1
            i += 1
            continue

        clean_idx = len(clean_chars)
        clean_chars.append(ch)
        clean_to_raw_start.append(i)
        clean_to_raw_end.append(i + 1)
        raw_to_clean[i] = clean_idx
        i += 1

    clean_text = "".join(clean_chars)
    return PreprocessResult(
        clean_text=clean_text,
        clean_to_raw_start=clean_to_raw_start,
        clean_to_raw_end=clean_to_raw_end,
        raw_to_clean=raw_to_clean,
        removed_bom_count=removed_bom_count,
        collapsed_crlf_count=collapsed_crlf_count,
        converted_cr_count=converted_cr_count,
        removed_control_count=removed_control_count,
    )


def collect_clause_boundaries(text: str) -> List[int]:
    boundaries = set()
    for pat in CLAUSE_BOUNDARY_PATTERNS:
        for m in pat.finditer(text):
            if 0 < m.start() < len(text):
                boundaries.add(m.start())
    return sorted(boundaries)


def split_by_boundaries(text: str, boundaries: Sequence[int]) -> List[Tuple[int, int]]:
    points = [0] + [b for b in boundaries if 0 < b < len(text)] + [len(text)]
    spans: List[Tuple[int, int]] = []
    for i in range(len(points) - 1):
        if points[i] < points[i + 1]:
            spans.append((points[i], points[i + 1]))
    return spans


def split_span_by_punctuation(text: str, start: int, end: int) -> List[Tuple[int, int]]:
    spans: List[Tuple[int, int]] = []
    cursor = start
    for m in CLAUSE_PUNCT_RE.finditer(text, start, end):
        punct_end = m.end()
        if cursor < punct_end:
            spans.append((cursor, punct_end))
        cursor = punct_end
    if cursor < end:
        spans.append((cursor, end))
    return spans


def trim_span(text: str, start: int, end: int) -> Optional[Tuple[int, int]]:
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    if start >= end:
        return None
    return start, end


def split_long_span_by_comma(text: str, start: int, end: int, max_chars: int) -> List[Tuple[int, int]]:
    if end - start <= max_chars:
        return [(start, end)]

    pieces: List[Tuple[int, int]] = []
    cursor = start
    for m in CLAUSE_COMMA_RE.finditer(text, start, end):
        candidate_end = m.end()
        if candidate_end - cursor >= max_chars:
            pieces.append((cursor, candidate_end))
            cursor = candidate_end
    if cursor < end:
        pieces.append((cursor, end))

    normalized: List[Tuple[int, int]] = []
    for p_start, p_end in pieces:
        if p_end - p_start <= max_chars:
            normalized.append((p_start, p_end))
            continue
        seg_start = p_start
        while seg_start < p_end:
            seg_end = min(seg_start + max_chars, p_end)
            normalized.append((seg_start, seg_end))
            seg_start = seg_end
    return normalized


def find_table_row_spans(text: str, min_cells: int) -> List[Tuple[int, int]]:
    spans: List[Tuple[int, int]] = []
    cursor = 0
    for line in text.splitlines(keepends=True):
        line_wo_eol = line.rstrip("\r\n")
        start = cursor
        end = cursor + len(line_wo_eol)
        cursor += len(line)
        if not line_wo_eol.strip():
            continue
        cells = [x for x in TABLE_COL_SPLIT_RE.split(line_wo_eol.strip()) if x]
        if len(cells) >= min_cells:
            trimmed = trim_span(text, start, end)
            if trimmed:
                spans.append(trimmed)
    return spans


def merge_short_tail(spans: List[Tuple[int, int]], text: str, min_chars: int) -> List[Tuple[int, int]]:
    if not spans:
        return spans
    merged: List[Tuple[int, int]] = []
    for start, end in spans:
        if (end - start) < min_chars and merged:
            prev_start, _ = merged[-1]
            merged[-1] = (prev_start, end)
        else:
            merged.append((start, end))
    return merged


def classify_clause_type(clause_text: str, is_table_row: bool) -> str:
    if is_table_row:
        return "table_row_clause"
    if SUBSIDY_RE.search(clause_text):
        return "subsidy_rule"
    if TASK_RE.search(clause_text):
        return "task_assessment"
    if TIME_RE.search(clause_text):
        return "time_rule"
    if PRICING_RE.search(clause_text):
        return "pricing_rule"
    if SCOPE_RE.search(clause_text):
        return "scope_rule"
    if EXEC_RE.search(clause_text):
        return "execution_rule"
    if DEF_RE.search(clause_text):
        return "definition"
    return "other"


def extract_article_no(clause_text: str) -> Optional[str]:
    m = ARTICLE_NO_RE.match(clause_text)
    return m.group(1).strip() if m else None


def clean_span_to_raw_span(
    clean_start: int,
    clean_end: int,
    clean_to_raw_start: Sequence[int],
    clean_to_raw_end: Sequence[int],
    raw_len: int,
) -> Optional[Tuple[int, int]]:
    if clean_start < 0 or clean_end <= clean_start:
        return None
    if clean_end > len(clean_to_raw_start):
        return None
    raw_start = clean_to_raw_start[clean_start]
    raw_end = clean_to_raw_end[clean_end - 1]
    raw_start = max(0, min(raw_start, raw_len))
    raw_end = max(raw_start, min(raw_end, raw_len))
    return raw_start, raw_end


def segment_clauses(clean_text: str, raw_len: int, preprocess_result: PreprocessResult) -> List[Dict[str, object]]:
    min_chars = int(PIPELINE_PARAMS["clause_segmentation"]["min_clause_chars"])
    max_chars = int(PIPELINE_PARAMS["clause_segmentation"]["max_clause_chars"])
    min_cells = int(PIPELINE_PARAMS["clause_segmentation"]["table_row_fallback"]["min_cells"])

    boundaries = collect_clause_boundaries(clean_text)
    stage1_spans = split_by_boundaries(clean_text, boundaries)

    candidate_spans: List[Tuple[int, int]] = []
    for start, end in stage1_spans:
        candidate_spans.extend(split_span_by_punctuation(clean_text, start, end))

    normalized_spans: List[Tuple[int, int]] = []
    for start, end in candidate_spans:
        trimmed = trim_span(clean_text, start, end)
        if not trimmed:
            continue
        t_start, t_end = trimmed
        for s_start, s_end in split_long_span_by_comma(clean_text, t_start, t_end, max_chars):
            s_trimmed = trim_span(clean_text, s_start, s_end)
            if s_trimmed:
                normalized_spans.append(s_trimmed)

    normalized_spans = sorted(set(normalized_spans), key=lambda x: (x[0], x[1]))
    normalized_spans = merge_short_tail(normalized_spans, clean_text, min_chars)

    table_spans = find_table_row_spans(clean_text, min_cells=min_cells)
    table_span_set = set(table_spans)

    full_span_set = set(normalized_spans)
    full_span_set.update(table_span_set)
    final_spans = sorted(full_span_set, key=lambda x: (x[0], x[1]))

    expanded_spans = set()
    for start, end in final_spans:
        for sub_start, sub_end in split_long_span_by_comma(clean_text, start, end, max_chars):
            trimmed = trim_span(clean_text, sub_start, sub_end)
            if not trimmed:
                continue
            expanded_spans.add(trimmed)

    clauses: List[Dict[str, object]] = []
    for start, end in sorted(expanded_spans, key=lambda x: (x[0], x[1])):
        clause_text = clean_text[start:end].strip()
        if not clause_text:
            continue
        if len(clause_text) < min_chars:
            continue
        is_table_row = (start, end) in table_span_set
        clause_type = classify_clause_type(clause_text, is_table_row=is_table_row)
        article_no = extract_article_no(clause_text)
        raw_span = clean_span_to_raw_span(
            clean_start=start,
            clean_end=end,
            clean_to_raw_start=preprocess_result.clean_to_raw_start,
            clean_to_raw_end=preprocess_result.clean_to_raw_end,
            raw_len=raw_len,
        )
        if not raw_span:
            continue
        clauses.append(
            {
                "clause_text": clause_text,
                "clause_type_prelim": clause_type,
                "article_no": article_no,
                "clean_span_start": start,
                "clean_span_end": end,
                "raw_span_start": raw_span[0],
                "raw_span_end": raw_span[1],
                "char_count": len(clause_text),
                "is_table_row_clause": is_table_row,
            }
        )
    return clauses


def normalize_for_roundtrip(raw_slice: str) -> str:
    return raw_slice.replace("\r\n", "\n").replace("\r", "\n")


def mapping_roundtrip_mismatch_count(raw_text: str, clean_text: str, preprocess_result: PreprocessResult) -> int:
    mismatches = 0
    for idx, ch in enumerate(clean_text):
        raw_start = preprocess_result.clean_to_raw_start[idx]
        raw_end = preprocess_result.clean_to_raw_end[idx]
        if raw_start < 0 or raw_end <= raw_start or raw_end > len(raw_text):
            mismatches += 1
            continue
        normalized = normalize_for_roundtrip(raw_text[raw_start:raw_end])
        if normalized != ch:
            mismatches += 1
    return mismatches


def summarize_clause_lengths(lengths: Sequence[int]) -> Dict[str, object]:
    if not lengths:
        return {"count": 0, "min": None, "max": None, "avg": None, "p90": None}
    ordered = sorted(lengths)
    p90_idx = int((len(ordered) - 1) * 0.9)
    return {
        "count": len(lengths),
        "min": min(lengths),
        "max": max(lengths),
        "avg": round(mean(lengths), 2),
        "p90": ordered[p90_idx],
    }


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
