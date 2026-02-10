from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from policy_extraction_utils import MECHANISM_PATTERNS_PROXY, extract_task_fields


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "00_整理记录"
if not OUTPUT_DIR.exists():
    OUTPUT_DIR = PROJECT_ROOT / "00_鏁寸悊璁板綍"

DOC_FIELDS = [
    "title",
    "document_no",
    "issue_date",
    "effective_start_date",
    "effective_end_date",
    "org_name",
    "region_name",
    "target_name",
]

CLAUSE_FIELDS = [
    "mechanism_type",
    "mechanism_name",
    "clause_type",
    "raw_value",
    "raw_unit",
    "direction",
    "condition_text",
    "task_subject",
    "task_action",
    "task_deadline",
    "task_assessment",
]

MECH_PRIORITY = [
    "tou_pricing",
    "tiered_pricing",
    "differential_penalty_pricing",
    "subsidy",
    "task_assessment",
    "technology_route",
    "general_price_adjustment",
]

LOW_CONF_SOURCES = {"fallback_clause_type_lowconf", "rule_context_neighbor_lowconf"}
CLAUSE_IDX_RE = re.compile(r"#clause_(\d+)$")

TASK_HINT_RE = re.compile(
    r"\u4efb\u52a1|\u8003\u6838|\u9a8c\u6536|\u63a8\u8fdb|\u843d\u5b9e|\u8d23\u4efb|\u671f\u9650|\u622a\u81f3|\u5230\d{4}\u5e74"
)
UP_RE = re.compile(r"\u4e0a\u6d6e|\u63d0\u9ad8|\u52a0\u4ef7|\u4e0a\u8c03|\u589e\u957f")
DOWN_RE = re.compile(r"\u4e0b\u6d6e|\u964d\u4f4e|\u964d\u4ef7|\u4e0b\u8c03|\u51cf\u5c11")

NUMERIC_RE = re.compile(r"\d")
CN_NUM_RE = re.compile(r"[零〇一二三四五六七八九十百千万两壹贰叁肆伍陆柒捌玖拾佰仟]")
TIME_RANGE_RE = re.compile(r"\d{1,2}:\d{2}\s*[-~\u81f3]\s*\d{1,2}:\d{2}")
RATIO_RE = re.compile(r"\d+(?:\.\d+)?\s*:\s*\d+(?:\.\d+)?(?:\s*:\s*\d+(?:\.\d+)?)?")
CN_PERCENT_RE = re.compile(r"\u767e\u5206\u4e4b[零〇一二三四五六七八九十百千万两\d\.]+")

PARAM_PATTERNS_BASIC = [
    re.compile(
        r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>\u5143/\u5343\u74e6\u65f6|\u5143/\u5ea6|%|％|\u4e07\u5143/\u6751|\u4e07\u5143|\u5143|\u5343\u74e6\u65f6|kwh|kw|mw|kva|\u5c0f\u65f6)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?P<value>\d+(?:\.\d+)?\s*[-~\u81f3]\s*\d+(?:\.\d+)?)\s*(?P<unit>\u5143/\u5343\u74e6\u65f6|\u5143/\u5ea6|%|％|\u5343\u74e6\u65f6|\u5143)?",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?P<value>\d+(?:\.\d+)?\s*:\s*\d+(?:\.\d+)?(?:\s*:\s*\d+(?:\.\d+)?)?)(?P<unit>\u6bd4|\u6bd4\u4ef7)?",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?P<value>\d{1,2}:\d{2}\s*[-~\u81f3]\s*\d{1,2}:\d{2})(?P<unit>\u65f6\u6bb5)?",
        re.IGNORECASE,
    ),
]

PARAM_PATTERNS_ADVANCED = [
    re.compile(
        r"(?P<value>\u767e\u5206\u4e4b[零〇一二三四五六七八九十百千万两\d\.]+)(?P<unit>%|％)?",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?P<value>(?:\u4e0d\u8d85\u8fc7|\u4e0d\u9ad8\u4e8e|\u4e0d\u4f4e\u4e8e|\u4e0d\u5c11\u4e8e|\u4ee5\u4e0a|\u4ee5\u4e0b|\u4ee5\u5185|\u81f3)\s*[零〇一二三四五六七八九十百千万两\d]+(?:\.\d+)?)\s*(?P<unit>%|％|\u5143/\u5343\u74e6\u65f6|\u5143/\u5ea6|\u5143|\u4e07\u5143|\u5343\u74e6\u65f6)?",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?P<value>[零〇一二三四五六七八九十百千万两壹贰叁肆伍陆柒捌玖拾佰仟]+(?:\.\d+)?)\s*(?P<unit>%|％|\u5143/\u5343\u74e6\u65f6|\u5143/\u5ea6|\u5143|\u4e07\u5143|\u5343\u74e6\u65f6|\u5ea6)",
        re.IGNORECASE,
    ),
]

TARGETED_MECH_PATTERNS = {
    "tou_pricing": re.compile(
        r"\u5206\u65f6|\u5cf0\u8c37|\u5cf0\u5e73\u8c37|\u5cf0\u6bb5|\u8c37\u6bb5|\u5c16\u5cf0|\u65f6\u6bb5|"
        r"\d{1,2}:\d{2}\s*[-~\u81f3]\s*\d{1,2}:\d{2}|\d+(?:\.\d+)?\s*:\s*\d+(?:\.\d+)?(?:\s*:\s*\d+(?:\.\d+)?)?"
    ),
    "subsidy": re.compile(r"\u8865\u8d34|\u8865\u52a9|\u5956\u52b1|\u8865\u507f|\u6bcf\u6237\u6bcf\u5e74|\u4f4e\u4fdd|\u4e94\u4fdd"),
    "general_price_adjustment": re.compile(r"\u4e0a\u6d6e|\u4e0b\u6d6e|\u4e0a\u8c03|\u4e0b\u8c03|\u52a0\u4ef7|\u964d\u4ef7|\u4ef7\u5dee|\u7535\u4ef7"),
    "tiered_pricing": re.compile(r"\u9636\u68af|\u6863\u4f4d|\u5206\u6863|\u4e00\u6863|\u4e8c\u6863|\u4e09\u6863"),
}

MECH_UPGRADE_PATTERNS = {
    "tou_pricing": re.compile(
        r"\u5206\u65f6|\u5cf0\u8c37|\u5cf0\u5e73\u8c37|\u5cf0\u6bb5|\u8c37\u6bb5|"
        r"\d{1,2}:\d{2}\s*[-~\u81f3]\s*\d{1,2}:\d{2}|\d+(?:\.\d+)?\s*:\s*\d+(?:\.\d+)?(?:\s*:\s*\d+(?:\.\d+)?)?"
    ),
    "tiered_pricing": re.compile(r"\u9636\u68af|\u6863\u4f4d|\u5206\u6863|\u4e00\u6863|\u4e8c\u6863|\u4e09\u6863"),
    "differential_penalty_pricing": re.compile(r"\u5dee\u522b\u7535\u4ef7|\u60e9\u7f5a\u6027"),
    "subsidy": re.compile(r"\u8865\u8d34|\u8865\u52a9|\u5956\u52b1"),
    "task_assessment": re.compile(r"\u4efb\u52a1|\u8003\u6838|\u9a8c\u6536"),
    "technology_route": re.compile(r"\u7535\u80fd\u66ff\u4ee3|\u6e05\u6d01\u53d6\u6696|\u7164\u6539\u7535|\u5cb8\u7535"),
    "general_price_adjustment": re.compile(r"\u4e0a\u6d6e|\u4e0b\u6d6e|\u4e0a\u8c03|\u4e0b\u8c03|\u52a0\u4ef7|\u964d\u4ef7|\u8c03\u6574\u7535\u4ef7"),
}

DATE_IN_TITLE_PATTERN = re.compile(r"(\d{4}\u5e74\d{1,2}\u6708\d{1,2}\u65e5)")
DOC_NO_PATTERN = re.compile(r"[\u4e00-\u9fa5A-Za-z]{0,10}\u3014\d{4}\u3015\d+\u53f7|\u3014\d{4}\u3015\d+\u53f7")
ORG_FROM_TITLE_PATTERN = re.compile(r"^(?P<org>.+?)(\u5173\u4e8e|\u5370\u53d1|\u53d1\u5e03|\u901a\u77e5|\u610f\u89c1|\u65b9\u6848)")


@dataclass
class IterStats:
    clause_type_filled: int = 0
    mechanism_filled_by_pattern: int = 0
    mechanism_filled_by_fallback: int = 0
    mechanism_filled_by_numeric_keyword: int = 0
    mechanism_filled_by_neighbor: int = 0
    lowconf_upgraded: int = 0
    lowconf_dropped: int = 0
    raw_value_filled_by_rule: int = 0
    raw_value_filled_by_advanced_rule: int = 0
    raw_unit_filled_by_rule: int = 0
    direction_filled_by_rule: int = 0
    task_filled_by_rule: int = 0
    bind_true_count: int = 0
    bind_total_raw_clause: int = 0
    doc_title_filled: int = 0
    doc_issue_date_filled: int = 0
    doc_document_no_filled: int = 0
    doc_org_name_filled: int = 0


def read_jsonl(path: Path) -> List[Dict]:
    rows: List[Dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def ensure_field_dict(pred: Dict) -> None:
    for key in DOC_FIELDS + CLAUSE_FIELDS:
        pred.setdefault(key, [])
        if not isinstance(pred[key], list):
            pred[key] = []


def normalize_item(text: str, start: Optional[int], end: Optional[int], probability: float, source: str) -> Dict:
    return {"text": text, "start": start, "end": end, "probability": float(probability), "source": source}


def add_unique_item(items: List[Dict], item: Dict) -> bool:
    key = (item.get("text"), item.get("start"), item.get("end"), item.get("source"))
    for old in items:
        if (old.get("text"), old.get("start"), old.get("end"), old.get("source")) == key:
            return False
    items.append(item)
    return True


def is_numeric_like_text(text: str) -> bool:
    if not text:
        return False
    return bool(
        NUMERIC_RE.search(text)
        or CN_NUM_RE.search(text)
        or CN_PERCENT_RE.search(text)
        or TIME_RANGE_RE.search(text)
        or RATIO_RE.search(text)
    )


def contains_numeric_like_item(items: List[Dict]) -> bool:
    return any(is_numeric_like_text(str(x.get("text", ""))) for x in items)


def find_span(text: str, sub: str) -> Tuple[Optional[int], Optional[int]]:
    if not text or not sub:
        return None, None
    idx = text.find(sub)
    if idx < 0:
        return None, None
    return idx, idx + len(sub)


def parse_clause_index(clause_id: str) -> int:
    m = CLAUSE_IDX_RE.search(clause_id or "")
    return int(m.group(1)) if m else -1


def source_rank(source: str) -> int:
    if source in ("rule_pattern", "rule_pattern_ext", "rule_numeric_keyword"):
        return 0
    if source == "rule_context_neighbor":
        return 1
    if source == "fallback_clause_type":
        return 2
    if source in ("", "uie"):
        return 3
    if source in LOW_CONF_SOURCES:
        return 5
    if source.startswith("fallback_clause_type"):
        return 4
    return 6


def top_item(items: List[Dict]) -> Optional[Dict]:
    if not items:
        return None
    return sorted(items, key=lambda x: (source_rank(str(x.get("source", ""))), -float(x.get("probability", 0.0))))[0]


def pick_mechanism_by_pattern(clause_text: str) -> Optional[Tuple[str, int, int, str]]:
    for mech in MECH_PRIORITY:
        pattern = MECHANISM_PATTERNS_PROXY.get(mech)
        if not pattern:
            continue
        hit = pattern.search(clause_text)
        if hit:
            return mech, hit.start(), hit.end(), hit.group(0)
    return None


def infer_mechanism_by_clause_fallback(clause_type_prelim: str, clause_text: str) -> Optional[Tuple[str, str]]:
    if clause_type_prelim == "subsidy_rule":
        return "subsidy", "fallback_clause_type"
    if clause_type_prelim == "task_assessment":
        return "task_assessment", "fallback_clause_type"
    if clause_type_prelim == "time_rule":
        if re.search(r"\u5206\u65f6|\u5cf0\u8c37|\u5c16\u5cf0|\u5e73\u6bb5|\u8c37\u6bb5", clause_text):
            return "tou_pricing", "fallback_clause_type"
        return "tou_pricing", "fallback_clause_type_lowconf"
    if clause_type_prelim == "pricing_rule":
        return "general_price_adjustment", "fallback_clause_type_lowconf"
    return None


def skip_numeric_candidate(clause_text: str, start: int, end: int, value: str) -> bool:
    val = value.strip()
    if not val:
        return True
    if re.fullmatch(r"(19|20)\d{2}", val):
        left = clause_text[max(0, start - 2) : start]
        right = clause_text[end : min(len(clause_text), end + 2)]
        if "\u5e74" in (left + right):
            return True
    if re.fullmatch(r"\d{1,2}", val):
        left = clause_text[max(0, start - 2) : start]
        right = clause_text[end : min(len(clause_text), end + 2)]
        if "\u7b2c" in left and any(ch in right for ch in ("\u6761", "\u6b3e", "\u9879")):
            return True
    return False


def extract_rule_params(clause_text: str, enable_advanced: bool, max_items: int = 4) -> List[Tuple[str, Optional[str], int, int, str]]:
    found: List[Tuple[str, Optional[str], int, int, str]] = []
    seen = set()
    patterns = list(PARAM_PATTERNS_BASIC)
    if enable_advanced:
        patterns += PARAM_PATTERNS_ADVANCED
    for pattern in patterns:
        for hit in pattern.finditer(clause_text):
            value = (hit.groupdict().get("value") or "").strip()
            unit = hit.groupdict().get("unit")
            if not value:
                continue
            st = hit.start("value")
            ed = hit.end("value")
            if skip_numeric_candidate(clause_text, st, ed, value):
                continue
            key = (value, st, ed)
            if key in seen:
                continue
            seen.add(key)
            source = "rule_regex_advanced" if pattern in PARAM_PATTERNS_ADVANCED else "rule_regex"
            found.append((value, unit, st, ed, source))
            if len(found) >= max_items:
                return found
    return found


def load_doc_compensation_map() -> Dict[str, Dict[str, Optional[str]]]:
    path = OUTPUT_DIR / "priority1_doc_meta_compensation.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("rows", [])
    out: Dict[str, Dict[str, Optional[str]]] = {}
    for row in rows:
        source_path = row.get("source_path")
        fields = row.get("fields", {})
        if source_path:
            out[source_path] = {k: (fields.get(k) or {}).get("value") for k in ("issue_date", "doc_type", "document_no")}
    return out


def build_doc_clause_index(clause_rows: List[Dict]) -> Dict[str, List[Tuple[int, int]]]:
    grouped: Dict[str, List[Tuple[int, int]]] = {}
    for i, row in enumerate(clause_rows):
        doc_id = str(row.get("doc_instance_id") or "")
        grouped.setdefault(doc_id, []).append((parse_clause_index(str(row.get("clause_id") or "")), i))
    for doc_id in grouped:
        grouped[doc_id].sort(key=lambda x: x[0])
    return grouped


def pick_neighbor_mechanism(clause_rows: List[Dict], doc_clause_index: Dict[str, List[Tuple[int, int]]], row_idx: int) -> Optional[Tuple[str, str, str]]:
    row = clause_rows[row_idx]
    doc_id = str(row.get("doc_instance_id") or "")
    arr = doc_clause_index.get(doc_id, [])
    if not arr:
        return None
    target = parse_clause_index(str(row.get("clause_id") or ""))
    pos = next((i for i, (ci, ri) in enumerate(arr) if ci == target and ri == row_idx), -1)
    if pos < 0:
        return None
    candidates: List[Tuple[int, float, str, str, str]] = []
    for nei_pos in (pos - 1, pos + 1):
        if nei_pos < 0 or nei_pos >= len(arr):
            continue
        _, nei_row_idx = arr[nei_pos]
        nei_row = clause_rows[nei_row_idx]
        t = top_item((nei_row.get("prediction", {}) or {}).get("mechanism_type", []) or [])
        if not t:
            continue
        source = str(t.get("source") or "")
        candidates.append((source_rank(source), -float(t.get("probability") or 0.0), str(t.get("text") or ""), str(nei_row.get("clause_id") or ""), source))
    if not candidates:
        return None
    candidates.sort()
    _, _, mech, anchor_clause_id, anchor_source = candidates[0]
    source = "rule_context_neighbor_lowconf" if anchor_source in LOW_CONF_SOURCES else "rule_context_neighbor"
    return mech, source, anchor_clause_id


def fill_mech_for_numeric_no_mech(
    clause_rows: List[Dict],
    clause_meta: Dict[str, Dict],
    doc_clause_index: Dict[str, List[Tuple[int, int]]],
    stats: IterStats,
) -> None:
    for idx, row in enumerate(clause_rows):
        pred = row.get("prediction", {})
        if pred.get("mechanism_type"):
            continue
        raw_items = pred.get("raw_value") or []
        if not raw_items or not contains_numeric_like_item(raw_items):
            continue
        cid = str(row.get("clause_id") or "")
        text = str((clause_meta.get(cid) or {}).get("clause_text") or "")
        if not text:
            continue

        matched = False
        for mech in ("tou_pricing", "subsidy", "general_price_adjustment", "tiered_pricing"):
            pat = TARGETED_MECH_PATTERNS[mech]
            hit = pat.search(text)
            if not hit:
                continue
            add_unique_item(pred["mechanism_type"], normalize_item(mech, hit.start(), hit.end(), 0.92, "rule_numeric_keyword"))
            row.setdefault("postfill", {})["mechanism_keyword"] = hit.group(0)
            row["postfill"]["mechanism_keyword_start"] = hit.start()
            row["postfill"]["mechanism_keyword_end"] = hit.end()
            stats.mechanism_filled_by_numeric_keyword += 1
            matched = True
            break
        if matched:
            continue

        neighbor = pick_neighbor_mechanism(clause_rows, doc_clause_index, idx)
        if neighbor:
            mech, source, anchor_clause_id = neighbor
            add_unique_item(pred["mechanism_type"], normalize_item(mech, None, None, 0.89, source))
            row.setdefault("postfill", {})["mechanism_context_anchor_clause_id"] = anchor_clause_id
            row["postfill"]["mechanism_context_anchor_source"] = source
            stats.mechanism_filled_by_neighbor += 1


def upgrade_lowconf_mech(
    clause_rows: List[Dict],
    clause_meta: Dict[str, Dict],
    doc_clause_index: Dict[str, List[Tuple[int, int]]],
    stats: IterStats,
    drop_lowconf_after_upgrade: bool,
) -> None:
    for idx, row in enumerate(clause_rows):
        pred = row.get("prediction", {})
        items = pred.get("mechanism_type") or []
        top = top_item(items)
        if not top:
            continue
        source = str(top.get("source") or "")
        if source not in LOW_CONF_SOURCES:
            continue
        mech = str(top.get("text") or "")
        cid = str(row.get("clause_id") or "")
        text = str((clause_meta.get(cid) or {}).get("clause_text") or "")
        upgraded = False

        pat = MECH_UPGRADE_PATTERNS.get(mech)
        if pat:
            hit = pat.search(text)
            if hit:
                add_unique_item(pred["mechanism_type"], normalize_item(mech, hit.start(), hit.end(), 0.93, "rule_pattern_ext"))
                row.setdefault("postfill", {})["mechanism_keyword"] = hit.group(0)
                row["postfill"]["mechanism_keyword_start"] = hit.start()
                row["postfill"]["mechanism_keyword_end"] = hit.end()
                upgraded = True

        if not upgraded:
            neighbor = pick_neighbor_mechanism(clause_rows, doc_clause_index, idx)
            if neighbor:
                nei_mech, nei_source, anchor_clause_id = neighbor
                if nei_mech == mech and nei_source == "rule_context_neighbor":
                    add_unique_item(pred["mechanism_type"], normalize_item(mech, None, None, 0.90, "rule_context_neighbor"))
                    row.setdefault("postfill", {})["mechanism_context_anchor_clause_id"] = anchor_clause_id
                    row["postfill"]["mechanism_context_anchor_source"] = "rule_context_neighbor"
                    upgraded = True

        if upgraded:
            stats.lowconf_upgraded += 1
            if drop_lowconf_after_upgrade:
                kept = [x for x in items if str(x.get("source") or "") not in LOW_CONF_SOURCES]
                if kept:
                    pred["mechanism_type"] = kept
                    stats.lowconf_dropped += 1


def optimize(
    mode: str,
    doc_pred_rows: List[Dict],
    clause_pred_rows: List[Dict],
    doc_meta: Dict[str, Dict],
    clause_meta: Dict[str, Dict],
    doc_comp_map: Dict[str, Dict[str, Optional[str]]],
    enable_neighbor_mech_repair: bool,
    enable_raw_advanced: bool,
    enable_lowconf_reduce: bool,
    drop_lowconf_after_upgrade: bool,
) -> Tuple[List[Dict], List[Dict], Dict]:
    stats = IterStats()

    for row in doc_pred_rows:
        pred = row.setdefault("prediction", {})
        ensure_field_dict(pred)
        source_path = str(row.get("source_path") or "")
        doc = doc_meta.get(row.get("doc_instance_id"), {})
        title_text = str(doc.get("chunk_title") or "").strip()

        if not pred["title"] and title_text:
            add_unique_item(pred["title"], normalize_item(title_text, None, None, 1.0, "step3_title"))
            stats.doc_title_filled += 1

        if not pred["issue_date"]:
            issue = (doc_comp_map.get(source_path) or {}).get("issue_date")
            if not issue and title_text:
                m = DATE_IN_TITLE_PATTERN.search(title_text)
                issue = m.group(1) if m else None
            if issue:
                add_unique_item(pred["issue_date"], normalize_item(issue, None, None, 0.98, "rule_doc_date"))
                stats.doc_issue_date_filled += 1

        if not pred["document_no"]:
            doc_no = (doc_comp_map.get(source_path) or {}).get("document_no")
            if not doc_no and title_text:
                m = DOC_NO_PATTERN.search(title_text)
                doc_no = m.group(0) if m else None
            if doc_no:
                add_unique_item(pred["document_no"], normalize_item(doc_no, None, None, 0.98, "rule_doc_no"))
                stats.doc_document_no_filled += 1

        if not pred["org_name"] and title_text:
            m = ORG_FROM_TITLE_PATTERN.search(title_text)
            if m:
                org = m.group("org").strip()
                if len(org) >= 2:
                    add_unique_item(pred["org_name"], normalize_item(org, None, None, 0.85, "rule_title_org"))
                    stats.doc_org_name_filled += 1

    for row in clause_pred_rows:
        pred = row.setdefault("prediction", {})
        ensure_field_dict(pred)
        cid = str(row.get("clause_id") or "")
        meta = clause_meta.get(cid, {})
        text = str(meta.get("clause_text") or "")
        clause_type_prelim = str(meta.get("clause_type_prelim") or "other")

        if not pred["clause_type"]:
            add_unique_item(pred["clause_type"], normalize_item(clause_type_prelim, None, None, 1.0, "step3_prelim"))
            stats.clause_type_filled += 1

        if not pred["mechanism_type"]:
            hit = pick_mechanism_by_pattern(text)
            if hit:
                mech, st, ed, kw = hit
                add_unique_item(pred["mechanism_type"], normalize_item(mech, st, ed, 0.99, "rule_pattern"))
                row.setdefault("postfill", {})["mechanism_keyword"] = kw
                row["postfill"]["mechanism_keyword_start"] = st
                row["postfill"]["mechanism_keyword_end"] = ed
                stats.mechanism_filled_by_pattern += 1
            else:
                fallback = infer_mechanism_by_clause_fallback(clause_type_prelim, text)
                if fallback:
                    mech, source = fallback
                    add_unique_item(pred["mechanism_type"], normalize_item(mech, None, None, 0.90, source))
                    stats.mechanism_filled_by_fallback += 1

        if mode == "v2":
            needs_raw = (not pred["raw_value"]) or (not contains_numeric_like_item(pred["raw_value"]))
            if needs_raw:
                for value, unit, st, ed, source in extract_rule_params(text, enable_advanced=enable_raw_advanced):
                    if add_unique_item(pred["raw_value"], normalize_item(value, st, ed, 0.98, source)):
                        stats.raw_value_filled_by_rule += 1
                        if source == "rule_regex_advanced":
                            stats.raw_value_filled_by_advanced_rule += 1
                    if unit:
                        ust, ued = find_span(text, unit)
                        if add_unique_item(pred["raw_unit"], normalize_item(unit, ust, ued, 0.97, source)):
                            stats.raw_unit_filled_by_rule += 1

            if not pred["direction"]:
                m_up = UP_RE.search(text)
                m_down = DOWN_RE.search(text)
                if m_up:
                    add_unique_item(pred["direction"], normalize_item(m_up.group(0), m_up.start(), m_up.end(), 0.96, "rule_direction"))
                    stats.direction_filled_by_rule += 1
                elif m_down:
                    add_unique_item(pred["direction"], normalize_item(m_down.group(0), m_down.start(), m_down.end(), 0.96, "rule_direction"))
                    stats.direction_filled_by_rule += 1

            if clause_type_prelim == "task_assessment" or TASK_HINT_RE.search(text):
                fields = extract_task_fields(text)
                for k in ("task_subject", "task_deadline", "task_assessment"):
                    val = fields.get(k)
                    if val and not pred[k]:
                        st, ed = find_span(text, str(val))
                        if add_unique_item(pred[k], normalize_item(str(val), st, ed, 0.95, "rule_task")):
                            stats.task_filled_by_rule += 1
                actions = fields.get("task_action") or []
                if actions and not pred["task_action"]:
                    for a in actions[:3]:
                        st, ed = find_span(text, a)
                        if add_unique_item(pred["task_action"], normalize_item(a, st, ed, 0.95, "rule_task")):
                            stats.task_filled_by_rule += 1

    doc_clause_index = build_doc_clause_index(clause_pred_rows)
    if enable_neighbor_mech_repair:
        fill_mech_for_numeric_no_mech(clause_pred_rows, clause_meta, doc_clause_index, stats)
    if enable_lowconf_reduce:
        upgrade_lowconf_mech(clause_pred_rows, clause_meta, doc_clause_index, stats, drop_lowconf_after_upgrade)

    for row in clause_pred_rows:
        pred = row.get("prediction", {})
        raw_exists = bool(pred.get("raw_value"))
        if not raw_exists:
            continue
        stats.bind_total_raw_clause += 1
        if pred.get("mechanism_type"):
            row.setdefault("postfill", {})["param_bind_mechanism"] = True
            row["postfill"]["bind_reason"] = "rule_mechanism_type_or_uie"
            stats.bind_true_count += 1
        else:
            row.setdefault("postfill", {})["param_bind_mechanism"] = False
            row["postfill"]["bind_reason"] = "no_mechanism"

    summary = {
        "mode": mode,
        "enable_neighbor_mech_repair": enable_neighbor_mech_repair,
        "enable_raw_advanced": enable_raw_advanced,
        "enable_lowconf_reduce": enable_lowconf_reduce,
        "drop_lowconf_after_upgrade": drop_lowconf_after_upgrade,
        "stats": stats.__dict__,
    }
    return doc_pred_rows, clause_pred_rows, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Post-fill Step4 predictions for KB readiness.")
    parser.add_argument("--mode", choices=["v1", "v2"], default="v2")
    parser.add_argument("--doc-pred-file", type=str, default="00_整理记录/step4_gpu_doc_doc_predictions.jsonl")
    parser.add_argument("--clause-pred-file", type=str, default="00_整理记录/step4_gpu_clause_clause_predictions.jsonl")
    parser.add_argument("--doc-source-file", type=str, default="00_整理记录/step3_document_corpus.jsonl")
    parser.add_argument("--clause-source-file", type=str, default="00_整理记录/step3_clause_corpus.jsonl")
    parser.add_argument("--output-prefix", type=str, default="step4_kb_iter")
    parser.add_argument("--enable-neighbor-mech-repair", action="store_true")
    parser.add_argument("--enable-raw-advanced", action="store_true")
    parser.add_argument("--enable-lowconf-reduce", action="store_true")
    parser.add_argument("--keep-lowconf-after-upgrade", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    doc_pred_rows = read_jsonl(PROJECT_ROOT / args.doc_pred_file)
    clause_pred_rows = read_jsonl(PROJECT_ROOT / args.clause_pred_file)
    doc_source_rows = read_jsonl(PROJECT_ROOT / args.doc_source_file)
    clause_source_rows = read_jsonl(PROJECT_ROOT / args.clause_source_file)

    doc_meta = {x.get("doc_instance_id"): x for x in doc_source_rows}
    clause_meta = {x.get("clause_id"): x for x in clause_source_rows}
    doc_comp_map = load_doc_compensation_map()

    doc_out, clause_out, summary = optimize(
        mode=args.mode,
        doc_pred_rows=doc_pred_rows,
        clause_pred_rows=clause_pred_rows,
        doc_meta=doc_meta,
        clause_meta=clause_meta,
        doc_comp_map=doc_comp_map,
        enable_neighbor_mech_repair=args.enable_neighbor_mech_repair,
        enable_raw_advanced=args.enable_raw_advanced,
        enable_lowconf_reduce=args.enable_lowconf_reduce,
        drop_lowconf_after_upgrade=not args.keep_lowconf_after_upgrade,
    )

    doc_out_file = OUTPUT_DIR / f"{args.output_prefix}_doc_predictions.jsonl"
    clause_out_file = OUTPUT_DIR / f"{args.output_prefix}_clause_predictions.jsonl"
    summary_file = OUTPUT_DIR / f"{args.output_prefix}_postfill_summary.json"
    summary_md_file = OUTPUT_DIR / f"{args.output_prefix}_postfill_summary.md"

    write_jsonl(doc_out_file, doc_out)
    write_jsonl(clause_out_file, clause_out)
    write_json(summary_file, summary)
    lines = [
        f"# {args.output_prefix} Postfill Summary",
        "",
        f"- mode: {summary['mode']}",
        f"- enable_neighbor_mech_repair: {summary['enable_neighbor_mech_repair']}",
        f"- enable_raw_advanced: {summary['enable_raw_advanced']}",
        f"- enable_lowconf_reduce: {summary['enable_lowconf_reduce']}",
        f"- drop_lowconf_after_upgrade: {summary['drop_lowconf_after_upgrade']}",
        f"- stats: {summary['stats']}",
        "",
        "## Artifacts",
        f"- `{doc_out_file.relative_to(PROJECT_ROOT).as_posix()}`",
        f"- `{clause_out_file.relative_to(PROJECT_ROOT).as_posix()}`",
        f"- `{summary_file.relative_to(PROJECT_ROOT).as_posix()}`",
    ]
    summary_md_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("postfill done")


if __name__ == "__main__":
    main()
