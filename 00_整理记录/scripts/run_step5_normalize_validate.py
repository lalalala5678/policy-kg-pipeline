from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from policy_extraction_utils import normalize_parameter


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "00_整理记录"
if not OUTPUT_DIR.exists():
    for candidate in PROJECT_ROOT.iterdir():
        if candidate.is_dir() and str(candidate.name).startswith("00_"):
            OUTPUT_DIR = candidate
            break


KNOWN_MECHANISMS = [
    "tou_pricing",
    "tiered_pricing",
    "differential_penalty_pricing",
    "general_price_adjustment",
    "subsidy",
    "task_assessment",
    "technology_route",
]
KNOWN_MECHANISMS_SET = set(KNOWN_MECHANISMS)
PRICING_MECHANISMS = {
    "tou_pricing",
    "tiered_pricing",
    "differential_penalty_pricing",
    "general_price_adjustment",
}
LOW_CONF_SOURCES = {"fallback_clause_type_lowconf", "rule_context_neighbor_lowconf"}
HIGH_CONF_BIND_REASONS = {"keyword_hit", "keyword_plus_prior", "param_type_map"}

MECHANISM_POSITIVE_PATTERNS: Dict[str, re.Pattern[str]] = {
    "tou_pricing": re.compile(r"\u5206\u65f6|\u5cf0\u8c37|\u5cf0\u5e73\u8c37|\u5c16\u5cf0|\u5cf0\u6bb5|\u8c37\u6bb5|\u5e73\u6bb5|\u65f6\u6bb5\u7535\u4ef7|\u4f4e\u8c37"),
    "tiered_pricing": re.compile(r"\u9636\u68af|\u4e00\u6863|\u4e8c\u6863|\u4e09\u6863|\u5206\u6863|\u6863\u4f4d"),
    "differential_penalty_pricing": re.compile(r"\u5dee\u522b\u7535\u4ef7|\u60e9\u7f5a\u6027|\u6dd8\u6c70\u7c7b|\u9650\u5236\u7c7b"),
    "general_price_adjustment": re.compile(r"\u4e0a\u6d6e|\u4e0b\u6d6e|\u4e0a\u8c03|\u4e0b\u8c03|\u52a0\u4ef7|\u964d\u4ef7|\u8c03\u4ef7|\u7535\u4ef7\u8c03\u6574"),
    "subsidy": re.compile(r"\u8865\u8d34|\u8865\u52a9|\u5956\u52b1|\u5956\u8865|\u8865\u507f|\u8d22\u653f\u652f\u6301"),
    "task_assessment": re.compile(r"\u4efb\u52a1|\u76ee\u6807|\u8003\u6838|\u9a8c\u6536|\u63a8\u8fdb|\u843d\u5b9e|\u5b8c\u6210\u7387|\u8fbe\u6807"),
    "technology_route": re.compile(r"\u7535\u80fd\u66ff\u4ee3|\u6e05\u6d01\u53d6\u6696|\u7164\u6539\u7535|\u5cb8\u7535|\u70ed\u6cf5|\u7535\u6c14\u5316"),
}
NEGATIVE_DOMAIN_PATTERN = re.compile(
    r"PM2\.5|\u7ec6\u9897\u7c92\u7269|\u4e8c\u6c27\u5316\u786b|\u6c2e\u6c27\u5316\u7269|\u5316\u5b66\u9700\u6c27\u91cf|COD|\u6c28\u6c2e|\u7a7a\u6c14\u8d28\u91cf\u4f18\u826f\u5929\u6570|"
    r"\u53d7\u6c61\u67d3\u8015\u5730|\u6c61\u67d3\u5730\u5757|\u751f\u6001\u4fdd\u62a4\u7ea2\u7ebf|\u68ee\u6797\u8986\u76d6\u7387|\u8fd1\u5cb8\u6d77\u57df\u6c34\u8d28|\u65ad\u9762\u6c34\u8d28"
)

PARAM_PRIOR: Dict[str, Dict[str, float]] = {
    "time_window": {"tou_pricing": 1.8},
    "price_delta_pct": {
        "tou_pricing": 1.4,
        "general_price_adjustment": 1.2,
        "differential_penalty_pricing": 1.0,
    },
    "price_value": {
        "general_price_adjustment": 1.2,
        "tou_pricing": 1.0,
        "tiered_pricing": 0.9,
        "subsidy": 0.8,
    },
    "consumption_threshold_kwh": {"tiered_pricing": 1.6, "subsidy": 0.6},
    "subsidy_amount": {"subsidy": 1.8},
    "area_subsidy_amount": {"subsidy": 1.8},
    "funding_share_ratio": {"subsidy": 1.5, "task_assessment": 0.7},
    "ratio_target": {"task_assessment": 1.0, "technology_route": 0.9},
    "capacity_threshold": {"technology_route": 1.2, "task_assessment": 0.8},
    "tonnage_threshold": {"technology_route": 1.2, "task_assessment": 0.8},
    "duration_threshold_month": {"task_assessment": 1.2, "subsidy": 0.8},
    "duration_threshold_year": {"task_assessment": 1.0, "subsidy": 0.9},
}

NUMERIC_RE = re.compile(r"\d")
CN_NUM_RE = re.compile(r"[\u96f6\u3007\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e\u5343\u4e07\u4e24\u58f9\u8d30\u53c1\u8086\u4f0d\u9646\u67d2\u634c\u7396\u62fe\u4f70\u4edf]")
CN_PERCENT_RE = re.compile(r"\u767e\u5206\u4e4b[\u96f6\u3007\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e\u5343\u4e07\d\.]+")
TIME_RANGE_RE = re.compile(r"\d{1,2}:\d{2}\s*[-~\u81f3\u5230]\s*\d{1,2}:\d{2}")
TIME_POINT_RE = re.compile(r"^[0-2]?\d[:\uFF1A][0-5]\d$")
RATIO_RE = re.compile(r"\d+(?:\.\d+)?\s*:\s*\d+(?:\.\d+)?(?:\s*:\s*\d+(?:\.\d+)?)?")
YEAR_RANGE_RE = re.compile(r"^(?:19|20)\d{2}\s*[-~\u81f3\u5230]\s*(?:19|20)\d{2}$")
DATE_PART_RE = re.compile(r"^(?:19|20)\d{2}[-/\.](?:0?[1-9]|1[0-2])(?:[-/\.](?:0?[1-9]|[12]\d|3[01]))?$")
POWER_CONTEXT_RE = re.compile(r"\u7535\u4ef7|\u5206\u65f6|\u5cf0\u8c37|\u8865\u8d34|\u5cb8\u7535|\u53d6\u6696|\u7535\u80fd\u66ff\u4ee3|\u7528\u7535|\u5343\u74e6\u65f6|\u5ea6")
POLLUTANT_UNIT_RE = re.compile(r"\u5316\u5b66\u9700\u6c27\u91cf|\u6c28\u6c2e|\u4e8c\u6c27\u5316\u786b|\u6c2e\u6c27\u5316\u7269|PM2\.5|\u6392\u653e\u6d53\u5ea6")
PRICE_UNIT_HINT_RE = re.compile(r"\u5143/\u5ea6|\u5143/\u5343\u74e6\u65f6|\u5206/\u5343\u74e6\u65f6")
PHYSICAL_UNIT_HINT_RE = re.compile(r"\u5343\u74e6\u65f6|kWh|KWH|kwh|\u5ea6(?!\u7535\u4ef7)|\u5428|MW|mw|kW|kw|W|w|kVA|kva")
TIER_THRESHOLD_CUE_RE = re.compile(r"\u7b2c\u4e00\u6863|\u7b2c\u4e8c\u6863|\u7b2c\u4e09\u6863|\u5206\u6863|\u9636\u68af|\u6863\u4f4d|\u9608\u503c|\u4e0d\u8d85\u8fc7|\u4ee5\u4e0a|\u4ee5\u5185|\u57fa\u6570")
TRANSPORT_CONTEXT_RE = re.compile(r"\u6bcf\u767e\u516c\u91cc|\u4e58\u7528\u8f66|\u65b0\u80fd\u6e90\u6c7d\u8f66|\u65b0\u8f66|\u81ea\u52a8\u9a7e\u9a76")
PRICE_DELTA_CUE_RE = re.compile(r"\u4e0a\u6d6e|\u4e0b\u6d6e|\u52a0\u4ef7|\u964d\u4ef7|\u8c03\u4ef7|\u63d0\u9ad8|\u964d\u4f4e|\u6da8\u4ef7|\u964d\u5e45")
FUNDING_SHARE_CUE_RE = re.compile(r"\u5206\u62c5|\u627f\u62c5|\u5171\u62c5|\u8d44\u91d1\u7531|\u4e2d\u592e|\u7701|\u5e02|\u53bf|\u533a")
NON_MONEY_COUNT_UNIT_RE = re.compile(r"\u6237|\u5bb6|\u53f0|\u4e2a|\u4eba")
LOW_CONF_BIND_REASONS = {"candidate_score", "step4_inherit", "step4_fallback", "time_window_tou_hint"}
UNIT_ALIAS_MAP = {
    "Ԫ": "\u5143",
    "��Ԫ": "\u4e07\u5143",
    "ǧ��ʱ": "\u5343\u74e6\u65f6",
    "Ԫ/ǧ��ʱ": "\u5143/\u5343\u74e6\u65f6",
    "Ԫ/��": "\u5143/\u5ea6",
    "Сʱ": "\u5c0f\u65f6",
    "ʱ��": "\u65f6\u6bb5",
}


def read_jsonl(path: Path) -> List[Dict]:
    rows: List[Dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[Dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def source_rank(source: str) -> int:
    if source in ("rule_pattern", "rule_pattern_ext", "rule_numeric_keyword"):
        return 0
    if source == "rule_context_neighbor":
        return 1
    if source == "fallback_clause_type":
        return 2
    if source in ("", "uie"):
        return 3
    if source.startswith("fallback_clause_type"):
        return 4
    if source in LOW_CONF_SOURCES:
        return 5
    return 6


def top_item(items: List[Dict]) -> Optional[Dict]:
    if not items:
        return None
    return sorted(items, key=lambda x: (source_rank(str(x.get("source", ""))), -float(x.get("probability", 0.0))))[0]


def as_text(items: List[Dict]) -> Optional[str]:
    t = top_item(items)
    if not t:
        return None
    text = str(t.get("text", "")).strip()
    return text or None


def span_valid(text: str, value: str, start: object, end: object) -> bool:
    if not isinstance(start, int) or not isinstance(end, int):
        return False
    if start < 0 or end < start or end > len(text):
        return False
    return text[start:end] == value


def pick_unit(raw_item: Dict, unit_items: List[Dict]) -> Optional[Dict]:
    if not unit_items:
        return None
    if not isinstance(raw_item.get("end"), int):
        return top_item(unit_items)
    raw_end = int(raw_item["end"])
    candidates: List[Tuple[int, float, Dict]] = []
    for u in unit_items:
        st = u.get("start")
        if not isinstance(st, int):
            continue
        gap = st - raw_end
        if gap < 0:
            continue
        candidates.append((gap, -float(u.get("probability", 0.0)), u))
    if candidates:
        candidates.sort(key=lambda x: (x[0], x[1]))
        return candidates[0][2]
    return top_item(unit_items)


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


def should_skip_raw_mention(raw_value: str, raw_unit: Optional[str], clause_text: str) -> Tuple[bool, str]:
    raw = (raw_value or "").strip()
    unit = (raw_unit or "").strip()
    merged = f"{raw}{unit}"
    if YEAR_RANGE_RE.fullmatch(raw) or DATE_PART_RE.fullmatch(raw):
        return True, "time_meta_filtered"
    if raw in {"\u7535\u91cf", "\u5bb9\u91cf", "\u6d53\u5ea6", "\u70ed\u8d1f\u8377", "\u5e73\u5747\u5428\u4f4d", "\u8239\u9f84"}:
        return True, "label_only_filtered"
    if POLLUTANT_UNIT_RE.search(unit):
        return True, "pollutant_unit_filtered"
    if NEGATIVE_DOMAIN_PATTERN.search(merged) and not POWER_CONTEXT_RE.search(clause_text):
        return True, "negative_domain_filtered"
    return False, ""


def canonicalize_unit_alias(raw_unit: Optional[str]) -> Optional[str]:
    if raw_unit is None:
        return None
    unit = str(raw_unit).strip()
    return UNIT_ALIAS_MAP.get(unit, unit)


def normalize_time_token(value: str) -> str:
    token = (value or "").strip().replace("\uFF1A", ":")
    parts = token.split(":")
    if len(parts) != 2:
        return token
    try:
        return f"{int(parts[0]):02d}:{int(parts[1]):02d}"
    except ValueError:
        return token


def extract_local_window(clause_text: str, start: Optional[int], end: Optional[int], radius: int = 28) -> str:
    if not isinstance(start, int) or not isinstance(end, int):
        return clause_text
    lo = max(0, start - radius)
    hi = min(len(clause_text), end + radius)
    return clause_text[lo:hi]


def parse_arabic_number(text: str) -> Optional[float]:
    if not text:
        return None
    m = re.search(r"[+-]?\d+(?:\.\d+)?", text)
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None


def apply_post_normalization_guards(
    raw_value: str,
    raw_unit: Optional[str],
    clause_text: str,
    raw_start: Optional[int],
    raw_end: Optional[int],
    norm: Dict[str, object],
) -> Tuple[Dict[str, object], Optional[str]]:
    adjusted = dict(norm)
    guard_action: Optional[str] = None
    raw_text = (raw_value or "").strip()
    unit_text = (raw_unit or "").strip()
    merged_raw = f"{raw_text}{unit_text}"
    local_window = extract_local_window(clause_text, raw_start, raw_end)
    narrow_window = extract_local_window(clause_text, raw_start, raw_end, radius=10)

    if TIME_POINT_RE.fullmatch(raw_text):
        if not bool(adjusted.get("matched")) or str(adjusted.get("param_type") or "") == "ratio_target":
            t = normalize_time_token(raw_text)
            adjusted.update(
                {
                    "matched": True,
                    "rule": "time_point_retyped",
                    "param_type": "time_window",
                    "norm_value": t,
                    "norm_unit": "time_window",
                    "norm_start": t,
                    "norm_end": t,
                    "range_start": None,
                    "range_end": None,
                    "op": "point",
                    "scope_unit": None,
                }
            )
            guard_action = "time_point_retyped"

    if bool(adjusted.get("matched")) and str(adjusted.get("norm_unit") or "") == "yuan_per_kwh":
        raw_has_physical_unit = bool(PHYSICAL_UNIT_HINT_RE.search(merged_raw))
        raw_has_price_unit = bool(PRICE_UNIT_HINT_RE.search(merged_raw))
        local_has_price_unit = bool(PRICE_UNIT_HINT_RE.search(local_window))
        if (raw_has_physical_unit and not raw_has_price_unit) or (not raw_has_price_unit and not local_has_price_unit):
            raw_num = parse_arabic_number(raw_text)
            if raw_num is not None and PHYSICAL_UNIT_HINT_RE.search(merged_raw):
                adjusted.update(
                    {
                        "matched": True,
                        "rule": "kwh_threshold_retyped_from_price_conflict",
                        "param_type": "consumption_threshold_kwh",
                        "norm_value": float(raw_num),
                        "norm_unit": "kwh",
                        "norm_start": None,
                        "norm_end": None,
                        "range_start": None,
                        "range_end": None,
                        "op": "threshold" if TIER_THRESHOLD_CUE_RE.search(clause_text) else None,
                        "scope_unit": None,
                    }
                )
                guard_action = "price_conflict_retyped_to_kwh"
            else:
                adjusted.update(
                    {
                        "matched": False,
                        "rule": "price_conflict_filtered",
                        "param_type": None,
                        "norm_value": None,
                        "norm_unit": None,
                        "norm_start": None,
                        "norm_end": None,
                        "range_start": None,
                        "range_end": None,
                        "op": None,
                        "scope_unit": None,
                    }
                )
                guard_action = "price_conflict_filtered"

    if bool(adjusted.get("matched")) and str(adjusted.get("param_type") or "") == "price_value":
        raw_num = parse_arabic_number(raw_text)
        if raw_num is not None and raw_num >= 10 and PHYSICAL_UNIT_HINT_RE.search(merged_raw) and not PRICE_UNIT_HINT_RE.search(merged_raw):
            adjusted.update(
                {
                    "matched": True,
                    "rule": "tier_threshold_retyped_from_price_value",
                    "param_type": "consumption_threshold_kwh",
                    "norm_value": float(raw_num),
                    "norm_unit": "kwh",
                    "norm_start": None,
                    "norm_end": None,
                    "range_start": None,
                    "range_end": None,
                    "op": "threshold" if TIER_THRESHOLD_CUE_RE.search(clause_text) else None,
                    "scope_unit": None,
                }
            )
            guard_action = "tier_threshold_retyped"

    if bool(adjusted.get("matched")) and str(adjusted.get("param_type") or "") in {"duration_threshold_month", "duration_threshold_year"}:
        if PRICE_UNIT_HINT_RE.search(merged_raw) or PHYSICAL_UNIT_HINT_RE.search(merged_raw):
            adjusted.update(
                {
                    "matched": False,
                    "rule": "duration_context_conflict_filtered",
                    "param_type": None,
                    "norm_value": None,
                    "norm_unit": None,
                    "norm_start": None,
                    "norm_end": None,
                    "range_start": None,
                    "range_end": None,
                    "op": None,
                    "scope_unit": None,
                }
            )
            guard_action = "duration_context_conflict_filtered"

    if bool(adjusted.get("matched")) and str(adjusted.get("param_type") or "") in {"subsidy_amount", "price_value"}:
        raw_num = parse_arabic_number(raw_text)
        raw_escaped = re.escape(raw_text)
        if (
            raw_num is not None
            and re.search(raw_escaped + r"\s*(\u6237|\u5bb6|\u53f0|\u4e2a|\u4eba)", local_window)
            and str(adjusted.get("norm_unit") or "") in {"yuan", "yuan_per_kwh"}
        ):
            adjusted.update(
                {
                    "matched": True,
                    "rule": "household_count_retyped_from_mismatch_unit",
                    "param_type": "target_household_count",
                    "norm_value": float(raw_num),
                    "norm_unit": "household",
                    "norm_start": None,
                    "norm_end": None,
                    "range_start": None,
                    "range_end": None,
                    "op": "threshold" if TIER_THRESHOLD_CUE_RE.search(clause_text) else None,
                    "scope_unit": None,
                }
            )
            guard_action = "household_count_retyped"

    if bool(adjusted.get("matched")) and str(adjusted.get("param_type") or "") == "price_value":
        raw_num = parse_arabic_number(raw_text)
        local_has_price_per_unit = bool(re.search(r"(?:\u6bcf\u5343\u74e6\u65f6|\u6bcf\u5ea6|/\u5343\u74e6\u65f6|/\u5ea6)", narrow_window))
        local_has_subsidy_cue = bool(re.search(r"\u8865\u8d34|\u8865\u52a9|\u5956\u8865|\u8d44\u91d1", clause_text))
        if (
            raw_num is not None
            and raw_num >= 100
            and str(adjusted.get("norm_unit") or "") == "yuan"
            and local_has_subsidy_cue
            and not local_has_price_per_unit
        ):
            adjusted.update(
                {
                    "matched": True,
                    "rule": "price_value_retyped_to_subsidy_amount_context",
                    "param_type": "subsidy_amount",
                    "norm_value": float(raw_num),
                    "norm_unit": "yuan",
                    "norm_start": None,
                    "norm_end": None,
                    "range_start": None,
                    "range_end": None,
                    "op": None,
                    "scope_unit": None,
                }
            )
            guard_action = "price_value_retyped_to_subsidy_amount"

    if bool(adjusted.get("matched")) and str(adjusted.get("param_type") or "") == "subsidy_amount":
        raw_num = parse_arabic_number(raw_text)
        local_has_price_per_unit = bool(re.search(r"(?:\u6bcf\u5343\u74e6\u65f6|\u6bcf\u5ea6)", local_window))
        local_has_delta_cue = bool(PRICE_DELTA_CUE_RE.search(local_window))
        if raw_num is not None and raw_num <= 5 and local_has_price_per_unit and local_has_delta_cue:
            adjusted.update(
                {
                    "matched": True,
                    "rule": "subsidy_amount_retyped_to_price_value_context",
                    "param_type": "price_value",
                    "norm_value": float(raw_num),
                    "norm_unit": "yuan_per_kwh",
                    "norm_start": None,
                    "norm_end": None,
                    "range_start": None,
                    "range_end": None,
                    "op": None,
                    "scope_unit": None,
                }
            )
            guard_action = "subsidy_amount_retyped_to_price_value"

    if bool(adjusted.get("matched")) and str(adjusted.get("param_type") or "") == "ratio_target":
        if ":" in raw_text and FUNDING_SHARE_CUE_RE.search(clause_text):
            adjusted["param_type"] = "funding_share_ratio"
            adjusted["rule"] = "ratio_sequence_funding_share_retyped"
            guard_action = "funding_share_ratio_retyped"

    return adjusted, guard_action


def build_norm_input(
    raw_value: str,
    raw_unit: Optional[str],
    clause_text: str,
    raw_start: Optional[int],
    raw_end: Optional[int],
) -> Tuple[str, bool]:
    def _local_unit_repair(raw_text_local: str, local_text: str) -> Optional[str]:
        raw_escaped_local = re.escape(raw_text_local)
        patterns = [
            r"(元/度|元/千瓦时|分/千瓦时)",
            r"(千瓦时|kWh|KWH|kwh|度)",
            r"(万元/村|万元|元)",
            r"(户|家|台|个|人)",
        ]
        for unit_pat in patterns:
            m_local = re.search(raw_escaped_local + r"\s*" + unit_pat, local_text)
            if m_local:
                return f"{raw_text_local}{m_local.group(1)}"
        return None

    raw_text = (raw_value or "").strip()
    unit_text = (raw_unit or "").strip()
    if not unit_text or unit_text in raw_text:
        return raw_text, False
    local_window = extract_local_window(clause_text, raw_start, raw_end)
    if re.search(r"\d", unit_text):
        repaired = _local_unit_repair(raw_text, local_window)
        if repaired:
            return repaired, True
        return raw_text, True

    raw_escaped = re.escape(raw_text)

    # Unit prediction can be mis-paired in dense clauses; prefer local anchors around raw value.
    if PHYSICAL_UNIT_HINT_RE.search(unit_text):
        if re.search(raw_escaped + r"\s*(?:\u5143(?:/\u5ea6|/\u5343\u74e6\u65f6)?|\u5206/\u5343\u74e6\u65f6)", local_window):
            repaired = _local_unit_repair(raw_text, local_window)
            if repaired:
                return repaired, True
            return raw_text, True
    if "\u5143" in unit_text:
        if re.search(raw_escaped + r"\s*(?:\u6237|\u5bb6|\u53f0|\u4e2a|\u4eba)", local_window):
            repaired = _local_unit_repair(raw_text, local_window)
            if repaired:
                return repaired, True
            return raw_text, True
        if re.search(raw_escaped + r"\s*(?:\u5343\u74e6\u65f6|kWh|KWH|kwh|\u5ea6)", local_window):
            repaired = _local_unit_repair(raw_text, local_window)
            if repaired:
                return repaired, True
            return raw_text, True

    return f"{raw_text}{unit_text}", False


def is_parenthetical_weak_constraint(clause_text: str, raw_start: Optional[int], raw_end: Optional[int], param_type: Optional[str]) -> bool:
    if param_type not in {"duration_threshold_month", "duration_threshold_year"}:
        return False
    if not isinstance(raw_start, int) or not isinstance(raw_end, int):
        return False
    left = clause_text.rfind("\uff08", 0, raw_start + 1)
    right = clause_text.find("\uff09", raw_end)
    if left == -1 or right == -1:
        return False
    # Ignore very long parenthesis ranges to reduce accidental hits.
    return (right - left) <= 24


def is_param_unit_compatible(
    param_type: Optional[str],
    raw_value: str,
    raw_unit: Optional[str],
    norm_unit: Optional[str],
    clause_text: str,
    raw_start: Optional[int],
    raw_end: Optional[int],
) -> bool:
    if not param_type:
        return False
    unit_text = (raw_unit or "").strip()
    merged_raw = f"{raw_value}{unit_text}"
    local_window = extract_local_window(clause_text, raw_start, raw_end)

    if param_type in {"duration_threshold_month", "duration_threshold_year"}:
        if PRICE_UNIT_HINT_RE.search(merged_raw) or PHYSICAL_UNIT_HINT_RE.search(merged_raw):
            return False
        if param_type == "duration_threshold_year":
            return bool(re.search(r"\u5e74", merged_raw + local_window))
        return bool(re.search(r"\u4e2a\u6708|\u6708|\u91c7\u6696\u5b63", merged_raw + local_window))

    if param_type == "price_value":
        if unit_text and not re.search(r"\u5143|\u5206", unit_text):
            return False
        if norm_unit == "yuan_per_kwh":
            return bool(PRICE_UNIT_HINT_RE.search(merged_raw + local_window))
        return True

    if param_type in {"subsidy_amount", "area_subsidy_amount"}:
        if re.search(re.escape(raw_value) + r"\s*(\u6237|\u5bb6|\u53f0|\u4e2a|\u4eba)", local_window):
            return False
        return True

    if param_type == "target_household_count":
        if unit_text and NON_MONEY_COUNT_UNIT_RE.search(unit_text):
            return True
        return bool(re.search(re.escape(raw_value) + r"\s*(\u6237|\u5bb6|\u53f0|\u4e2a|\u4eba)", local_window))

    if param_type == "funding_share_ratio":
        return ":" in (raw_value or "")

    return True


def format_norm_value(value: object, unit: Optional[str]) -> str:
    if value is None:
        return "<null>"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        out = f"{float(value):.6f}".rstrip("0").rstrip(".")
        return out if out else "0"
    out = str(value).strip()
    if unit == "percent" and out.endswith("%"):
        out = out[:-1].strip()
    return out or "<null>"


def canonical_payload(
    param_type: str,
    norm_value: object,
    norm_unit: Optional[str],
    norm_start: object,
    norm_end: object,
    op: Optional[str],
    range_start: object,
    range_end: object,
) -> str:
    return "|".join(
        [
            param_type or "<null>",
            format_norm_value(norm_value, norm_unit),
            norm_unit or "<null>",
            str(norm_start if norm_start is not None else "<null>"),
            str(norm_end if norm_end is not None else "<null>"),
            op or "<null>",
            str(range_start if range_start is not None else "<null>"),
            str(range_end if range_end is not None else "<null>"),
        ]
    )


def canonical_key(
    param_type: str,
    norm_value: object,
    norm_unit: Optional[str],
    norm_start: object,
    norm_end: object,
    op: Optional[str],
    range_start: object,
    range_end: object,
) -> str:
    payload = canonical_payload(param_type, norm_value, norm_unit, norm_start, norm_end, op, range_start, range_end)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def make_id(prefix: str, payload: str, n: int = 20) -> str:
    return f"{prefix}_{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:n]}"


def count_hits(pattern: re.Pattern[str], text: str) -> int:
    return sum(1 for _ in pattern.finditer(text))


def param_prior_weight(param_type: Optional[str], mechanism: str) -> float:
    if not param_type:
        return 0.0
    return float(PARAM_PRIOR.get(str(param_type), {}).get(mechanism, 0.0))


def build_clause_candidates(
    clause_text: str,
    step4_mechanism: Optional[str],
    step4_source: Optional[str],
    clause_param_types: List[str],
) -> Tuple[List[Dict], int]:
    negative_hits = count_hits(NEGATIVE_DOMAIN_PATTERN, clause_text)
    transport_hits = count_hits(TRANSPORT_CONTEXT_RE, clause_text)
    candidates: List[Dict] = []
    for mechanism in KNOWN_MECHANISMS:
        pos_hits = count_hits(MECHANISM_POSITIVE_PATTERNS[mechanism], clause_text)
        neg_hits = negative_hits if mechanism in PRICING_MECHANISMS else 0
        prior = max((param_prior_weight(pt, mechanism) for pt in clause_param_types), default=0.0)

        if step4_mechanism == mechanism:
            if str(step4_source or "") in LOW_CONF_SOURCES:
                inherit_bonus = 0.2
            else:
                inherit_bonus = 0.6
        else:
            inherit_bonus = 0.0

        forced_drop = bool(neg_hits > 0 and pos_hits == 0 and mechanism in PRICING_MECHANISMS)
        score = pos_hits * 1.6 - neg_hits * 2.2 + prior * 1.0 + inherit_bonus
        if mechanism in PRICING_MECHANISMS and transport_hits > 0 and pos_hits == 0:
            score -= 1.8
        if forced_drop:
            score -= 1.5
        if score <= 0:
            continue

        candidates.append(
            {
                "mechanism": mechanism,
                "score": round(float(score), 6),
                "pos_hits": int(pos_hits),
                "neg_hits": int(neg_hits),
                "prior": round(float(prior), 6),
                "inherit_bonus": round(float(inherit_bonus), 6),
                "forced_drop": forced_drop,
            }
        )

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates, negative_hits


def choose_binding_for_mention(
    candidates: List[Dict],
    mention_param_type: Optional[str],
    step4_mechanism: Optional[str],
    bind_min_score: float,
) -> Tuple[Optional[str], str, float, Optional[Dict], bool]:
    if not candidates:
        return None, "no_candidate", 0.0, None, False

    mention_rank: List[Tuple[float, Dict, float]] = []
    for cand in candidates:
        prior = param_prior_weight(mention_param_type, cand["mechanism"])
        score = float(cand["score"]) + prior * 1.2
        if cand.get("forced_drop"):
            score -= 1.5
        mention_rank.append((score, cand, prior))
    mention_rank.sort(key=lambda x: x[0], reverse=True)

    top_score, top_cand, top_prior = mention_rank[0]
    second_score = mention_rank[1][0] if len(mention_rank) > 1 else 0.0
    margin = top_score - second_score
    confidence = 1.0 / (1.0 + math.exp(-margin)) if top_score > 0 else 0.0

    has_negative_conflict = bool(top_cand.get("neg_hits", 0) > 0 and top_cand.get("pos_hits", 0) == 0)
    if has_negative_conflict:
        return None, "drop_by_negative", confidence, top_cand, True
    if top_score < bind_min_score:
        return None, "unknown_low_score", confidence, top_cand, False

    mechanism = str(top_cand["mechanism"])
    if top_cand.get("pos_hits", 0) > 0 and top_prior >= 0.8:
        reason = "keyword_plus_prior"
    elif top_cand.get("pos_hits", 0) > 0:
        reason = "keyword_hit"
    elif top_prior >= 1.2:
        reason = "param_type_map"
    elif step4_mechanism == mechanism:
        reason = "step4_inherit"
    else:
        reason = "candidate_score"
    return mechanism, reason, confidence, top_cand, False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Step5 normalization, correction, and validation.")
    parser.add_argument(
        "--clause-pred-file",
        type=str,
        default="00_整理记录/step4_seq_step2_clause_predictions.jsonl",
        help="Clause-level prediction JSONL from Step4.",
    )
    parser.add_argument(
        "--clause-source-file",
        type=str,
        default="00_整理记录/step3_clause_corpus.jsonl",
        help="Clause corpus JSONL from Step3.",
    )
    parser.add_argument(
        "--output-prefix",
        type=str,
        default="step5",
        help="Output prefix under 00_整理记录.",
    )
    parser.add_argument(
        "--bind-min-score",
        type=float,
        default=1.0,
        help="Minimum mention-level candidate score to keep known mechanism binding.",
    )
    parser.add_argument(
        "--strict-high-threshold",
        type=float,
        default=0.6,
        help="Confidence threshold for strict_high.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    clause_pred_rows = read_jsonl(PROJECT_ROOT / args.clause_pred_file)
    clause_source_rows = read_jsonl(PROJECT_ROOT / args.clause_source_file)
    clause_text_map = {r["clause_id"]: str(r.get("clause_text", "")) for r in clause_source_rows}

    mentions: List[Dict] = []
    definitions: Dict[str, Dict] = {}
    triples: List[Dict] = []
    triple_seen = set()

    param_type_counter: Counter = Counter()
    norm_unit_counter: Counter = Counter()
    rule_counter: Counter = Counter()
    filtered_counter: Counter = Counter()
    bind_reason_counter: Counter = Counter()
    bind_transition_counter: Counter = Counter()
    post_guard_counter: Counter = Counter()
    conflict_bucket: Dict[Tuple[str, str, str], set] = defaultdict(set)
    parse_error_count = 0

    span_ok = 0
    matched_ok = 0
    canonical_ok = 0
    mechanism_bound = 0
    ready_with_mechanism = 0
    strict_all_count = 0
    strict_high_count = 0
    local_supported_count = 0
    pricing_negative_conflict_count = 0

    valid_all_den = 0
    valid_numeric_den = 0
    mechanism_bound_valid_all = 0
    mechanism_bound_valid_numeric = 0
    normalization_attempted_count = 0

    clause_candidate_non_empty = 0
    clause_negative_count = 0
    raw_value_filtered_non_value = 0
    raw_value_filtered_by_rule = 0
    unit_pairing_dropped_count = 0
    unit_alias_applied_count = 0
    full_clause_retry_success_count = 0
    low_confidence_cap_count = 0
    time_window_tou_override_count = 0
    strict_high_compat_block_count = 0
    strict_high_weak_constraint_block_count = 0
    skip_reason_counter: Counter = Counter()

    for row in clause_pred_rows:
        clause_id = str(row.get("clause_id", ""))
        doc_instance_id = str(row.get("doc_instance_id", ""))
        source_path = str(row.get("source_path", ""))
        clause_text = clause_text_map.get(clause_id, "")

        pred = row.get("prediction") or {}
        if not isinstance(pred, dict):
            parse_error_count += 1
            continue

        raw_items = pred.get("raw_value") or []
        unit_items = pred.get("raw_unit") or []
        mech_item_before = top_item(pred.get("mechanism_type") or [])
        mechanism_before = str(mech_item_before.get("text", "")).strip() if mech_item_before else None
        mechanism_before_source = str(mech_item_before.get("source", "")).strip() if mech_item_before else None
        direction = as_text(pred.get("direction") or [])
        condition_text = as_text(pred.get("condition_text") or [])

        draft_mentions: List[Dict] = []
        clause_param_types: List[str] = []

        for idx, raw_item in enumerate(raw_items):
            raw_value = str(raw_item.get("text", "")).strip()
            if not raw_value:
                continue

            raw_start = raw_item.get("start")
            raw_end = raw_item.get("end")
            chosen_unit_item = pick_unit(raw_item, unit_items)
            raw_unit = str(chosen_unit_item.get("text", "")).strip() if chosen_unit_item else None
            if raw_unit == "":
                raw_unit = None
            raw_unit_norm = canonicalize_unit_alias(raw_unit)
            if raw_unit and raw_unit_norm and raw_unit_norm != raw_unit:
                unit_alias_applied_count += 1
            if not (is_numeric_like_text(raw_value) or is_numeric_like_text(raw_unit_norm or "")):
                raw_value_filtered_non_value += 1
                continue
            skip_it, skip_reason = should_skip_raw_mention(raw_value, raw_unit_norm, clause_text)
            if skip_it:
                raw_value_filtered_by_rule += 1
                skip_reason_counter[skip_reason] += 1
                continue

            this_span_ok = span_valid(clause_text, raw_value, raw_start, raw_end)
            if this_span_ok:
                span_ok += 1
            merged_for_norm, unit_pairing_dropped = build_norm_input(
                raw_value=raw_value,
                raw_unit=raw_unit_norm,
                clause_text=clause_text,
                raw_start=raw_start if isinstance(raw_start, int) else None,
                raw_end=raw_end if isinstance(raw_end, int) else None,
            )
            if unit_pairing_dropped:
                unit_pairing_dropped_count += 1

            normalization_attempted_count += 1
            norm_context = extract_local_window(clause_text, raw_start if isinstance(raw_start, int) else None, raw_end if isinstance(raw_end, int) else None)
            norm = normalize_parameter(merged_for_norm, norm_context)
            norm, guard_action = apply_post_normalization_guards(
                raw_value=raw_value,
                raw_unit=raw_unit_norm,
                clause_text=clause_text,
                raw_start=raw_start if isinstance(raw_start, int) else None,
                raw_end=raw_end if isinstance(raw_end, int) else None,
                norm=norm,
            )
            if not bool(norm.get("matched")) and raw_unit_norm is None:
                raw_num = parse_arabic_number(raw_value)
                if raw_num is not None and raw_num < 10:
                    retry_norm = normalize_parameter(raw_value, clause_text)
                    retry_norm, retry_guard_action = apply_post_normalization_guards(
                        raw_value=raw_value,
                        raw_unit=raw_unit_norm,
                        clause_text=clause_text,
                        raw_start=raw_start if isinstance(raw_start, int) else None,
                        raw_end=raw_end if isinstance(raw_end, int) else None,
                        norm=retry_norm,
                    )
                    if bool(retry_norm.get("matched")):
                        norm = retry_norm
                        guard_action = retry_guard_action or "retry_full_clause_decimal"
                        full_clause_retry_success_count += 1
            if guard_action:
                post_guard_counter[guard_action] += 1
            rule = str(norm.get("rule") or "no_rule")
            rule_counter[rule] += 1
            if rule.endswith("_filtered"):
                filtered_counter[rule] += 1

            matched = bool(norm.get("matched"))
            if matched:
                matched_ok += 1

            param_type = norm.get("param_type")
            if matched and param_type:
                clause_param_types.append(str(param_type))

            mention_key = f"{clause_id}|{idx}|{raw_start}|{raw_end}|{raw_value}"
            mention_id = make_id("pm", mention_key)
            draft_mentions.append(
                {
                    "mention_id": mention_id,
                    "raw_value": raw_value,
                    "raw_unit": raw_unit,
                    "raw_unit_norm": raw_unit_norm,
                    "raw_start": raw_start if isinstance(raw_start, int) else None,
                    "raw_end": raw_end if isinstance(raw_end, int) else None,
                    "span_ok": this_span_ok,
                    "normalization_attempted": True,
                    "is_numeric_like": is_numeric_like_text(raw_value),
                    "rule": rule,
                    "matched": matched,
                    "param_type": param_type,
                    "norm_value": norm.get("norm_value"),
                    "norm_unit": norm.get("norm_unit"),
                    "norm_start": norm.get("norm_start"),
                    "norm_end": norm.get("norm_end"),
                    "range_start": norm.get("range_start"),
                    "range_end": norm.get("range_end"),
                    "op": norm.get("op"),
                    "scope_unit": norm.get("scope_unit"),
                    "post_guard_action": guard_action,
                }
            )

        clause_candidates, clause_negative_hits = build_clause_candidates(
            clause_text=clause_text,
            step4_mechanism=mechanism_before,
            step4_source=mechanism_before_source,
            clause_param_types=clause_param_types,
        )
        if clause_candidates:
            clause_candidate_non_empty += 1
        if clause_negative_hits > 0:
            clause_negative_count += 1

        for draft in draft_mentions:
            bind_after, bind_reason, bind_confidence, bind_support, dropped_by_negative = choose_binding_for_mention(
                candidates=clause_candidates,
                mention_param_type=str(draft.get("param_type") or ""),
                step4_mechanism=mechanism_before,
                bind_min_score=float(args.bind_min_score),
            )

            if bind_after is None and mechanism_before in KNOWN_MECHANISMS_SET:
                skip_pricing_fallback = bool(
                    mechanism_before in PRICING_MECHANISMS
                    and count_hits(TRANSPORT_CONTEXT_RE, clause_text) > 0
                    and count_hits(MECHANISM_POSITIVE_PATTERNS[mechanism_before], clause_text) == 0
                )
                if not (clause_negative_hits > 0 and mechanism_before in PRICING_MECHANISMS) and not skip_pricing_fallback:
                    bind_after = mechanism_before
                    bind_reason = "step4_fallback"
                    bind_confidence = max(bind_confidence, 0.45)
                    bind_support = {
                        "mechanism": mechanism_before,
                        "score": 0.0,
                        "pos_hits": 0,
                        "neg_hits": clause_negative_hits if mechanism_before in PRICING_MECHANISMS else 0,
                    }

            # Time expressions are clause-local anchors for TOU and should not drift to ratio/task buckets.
            if str(draft.get("param_type") or "") == "time_window":
                tou_candidate = next((c for c in clause_candidates if c.get("mechanism") == "tou_pricing"), None)
                if tou_candidate is not None and int(tou_candidate.get("pos_hits", 0)) > 0 and bind_after != "tou_pricing":
                    bind_after = "tou_pricing"
                    bind_reason = "time_window_tou_hint"
                    bind_support = tou_candidate
                    bind_confidence = max(float(bind_confidence), 0.59)
                    dropped_by_negative = False
                    time_window_tou_override_count += 1

            if bind_reason in LOW_CONF_BIND_REASONS and float(bind_confidence) > 0.59:
                bind_confidence = 0.59
                low_confidence_cap_count += 1

            bind_reason_counter[bind_reason] += 1
            bind_transition_counter[f"{mechanism_before or 'None'}->{bind_after or 'None'}"] += 1

            mechanism_id = None
            if bind_after in KNOWN_MECHANISMS_SET:
                mechanism_id = make_id("mechanism", f"{doc_instance_id}|{bind_after}|{clause_id}")

            strict_all = bool(draft["span_ok"] and draft["matched"] and bind_after in KNOWN_MECHANISMS_SET)
            strict_compat_ok = is_param_unit_compatible(
                param_type=str(draft.get("param_type") or ""),
                raw_value=str(draft.get("raw_value") or ""),
                raw_unit=draft.get("raw_unit_norm"),
                norm_unit=str(draft.get("norm_unit") or "") if draft.get("norm_unit") is not None else None,
                clause_text=clause_text,
                raw_start=draft.get("raw_start") if isinstance(draft.get("raw_start"), int) else None,
                raw_end=draft.get("raw_end") if isinstance(draft.get("raw_end"), int) else None,
            )
            weak_constraint = is_parenthetical_weak_constraint(
                clause_text=clause_text,
                raw_start=draft.get("raw_start") if isinstance(draft.get("raw_start"), int) else None,
                raw_end=draft.get("raw_end") if isinstance(draft.get("raw_end"), int) else None,
                param_type=str(draft.get("param_type") or ""),
            )
            strict_high = bool(
                strict_all
                and bind_reason in HIGH_CONF_BIND_REASONS
                and float(bind_confidence) >= float(args.strict_high_threshold)
                and not dropped_by_negative
                and strict_compat_ok
                and not weak_constraint
            )
            if strict_all and not strict_compat_ok:
                strict_high_compat_block_count += 1
            if strict_all and weak_constraint:
                strict_high_weak_constraint_block_count += 1

            is_local_supported = bool(
                bind_after in KNOWN_MECHANISMS_SET
                and bind_support is not None
                and (
                    int(bind_support.get("pos_hits", 0)) > 0
                    or param_prior_weight(str(draft.get("param_type") or ""), str(bind_after)) >= 1.2
                )
                and not dropped_by_negative
            )

            if bind_after in KNOWN_MECHANISMS_SET:
                mechanism_bound += 1

            valid_all = bool(draft["span_ok"] and draft["normalization_attempted"])
            valid_numeric = bool(valid_all and draft["matched"] and draft["is_numeric_like"])
            if valid_all:
                valid_all_den += 1
                if bind_after in KNOWN_MECHANISMS_SET:
                    mechanism_bound_valid_all += 1
            if valid_numeric:
                valid_numeric_den += 1
                if bind_after in KNOWN_MECHANISMS_SET:
                    mechanism_bound_valid_numeric += 1
                if strict_all:
                    strict_all_count += 1
                if strict_high:
                    strict_high_count += 1
                if is_local_supported:
                    local_supported_count += 1
                if dropped_by_negative and bind_after in PRICING_MECHANISMS:
                    pricing_negative_conflict_count += 1

            mention: Dict[str, object] = {
                "param_mention_id": draft["mention_id"],
                "doc_instance_id": doc_instance_id,
                "source_path": source_path,
                "clause_id": clause_id,
                "mechanism_id": mechanism_id,
                "mechanism_type": bind_after,
                "mechanism_source": "step5_rebind",
                "mechanism_bind_before": mechanism_before,
                "mechanism_bind_before_source": mechanism_before_source,
                "mechanism_bind_after": bind_after,
                "mechanism_bind_reason": bind_reason,
                "bind_confidence": round(float(bind_confidence), 6),
                "raw_value": draft["raw_value"],
                "raw_unit": draft["raw_unit"],
                "direction": direction,
                "condition_text": condition_text,
                "evidence_scope": "clause",
                "evidence_anchor_id": clause_id,
                "evidence_span_start": draft["raw_start"],
                "evidence_span_end": draft["raw_end"],
                "evidence_span_valid": draft["span_ok"],
                "normalization_attempted": draft["normalization_attempted"],
                "normalization_rule": draft["rule"],
                "normalization_matched": draft["matched"],
                "is_numeric_like": draft["is_numeric_like"],
                "param_type": draft["param_type"],
                "norm_value": draft["norm_value"],
                "norm_unit": draft["norm_unit"],
                "norm_start": draft["norm_start"],
                "norm_end": draft["norm_end"],
                "range_start": draft["range_start"],
                "range_end": draft["range_end"],
                "op": draft["op"],
                "scope_unit": draft["scope_unit"],
                "clause_negative_hits": clause_negative_hits,
                "strict_all": strict_all,
                "strict_high": strict_high,
                "strict_compat_ok": strict_compat_ok,
                "strict_weak_constraint": weak_constraint,
            }

            if draft["matched"] and draft["param_type"] and draft["norm_unit"]:
                key = canonical_key(
                    str(draft["param_type"]),
                    draft["norm_value"],
                    str(draft["norm_unit"]),
                    draft["norm_start"],
                    draft["norm_end"],
                    str(draft["op"]) if draft["op"] is not None else None,
                    draft["range_start"],
                    draft["range_end"],
                )
                canonical_ok += 1
                mention["canonical_key"] = key
                param_def_id = make_id("pd", key)
                mention["param_def_id"] = param_def_id

                if key not in definitions:
                    definitions[key] = {
                        "param_def_id": param_def_id,
                        "canonical_key": key,
                        "param_type": draft["param_type"],
                        "norm_value": draft["norm_value"],
                        "norm_unit": draft["norm_unit"],
                        "norm_start": draft["norm_start"],
                        "norm_end": draft["norm_end"],
                        "range_start": draft["range_start"],
                        "range_end": draft["range_end"],
                        "op": draft["op"],
                        "scope_unit": draft["scope_unit"],
                        "mention_count": 0,
                        "sample_mention_ids": [],
                    }
                definitions[key]["mention_count"] += 1
                if len(definitions[key]["sample_mention_ids"]) < 5:
                    definitions[key]["sample_mention_ids"].append(str(draft["mention_id"]))

                param_type_counter[str(draft["param_type"])] += 1
                norm_unit_counter[str(draft["norm_unit"])] += 1
                if bind_after in KNOWN_MECHANISMS_SET:
                    conflict_bucket[(doc_instance_id, str(bind_after), str(draft["param_type"]))].add(str(draft["norm_unit"]))
                    ready_with_mechanism += 1

                t1 = (f"Clause:{clause_id}", "clause_has_parameter_mention", f"ParameterMention:{draft['mention_id']}")
                t2 = (
                    f"ParameterMention:{draft['mention_id']}",
                    "parameter_mention_refers_to_definition",
                    f"ParameterDefinition:{param_def_id}",
                )
                for triple in (t1, t2):
                    if triple not in triple_seen:
                        triple_seen.add(triple)
                        triples.append({"subject": triple[0], "predicate": triple[1], "object": triple[2]})
                if mechanism_id:
                    t3 = (
                        f"Mechanism:{mechanism_id}",
                        "mechanism_has_parameter_definition",
                        f"ParameterDefinition:{param_def_id}",
                    )
                    if t3 not in triple_seen:
                        triple_seen.add(t3)
                        triples.append({"subject": t3[0], "predicate": t3[1], "object": t3[2]})

            mentions.append(mention)

    conflict_items = []
    for key, units in conflict_bucket.items():
        if len(units) <= 1:
            continue
        doc_instance_id, mechanism_type, param_type = key
        conflict_items.append(
            {
                "doc_instance_id": doc_instance_id,
                "mechanism_type": mechanism_type,
                "param_type": param_type,
                "norm_units": sorted(units),
            }
        )

    conflict_items = sorted(conflict_items, key=lambda x: (x["doc_instance_id"], x["mechanism_type"], x["param_type"]))
    definitions_rows = sorted(definitions.values(), key=lambda x: x["param_def_id"])

    mention_total = len(mentions)
    all_clause_den = len(clause_pred_rows)

    def safe_rate(num: int, den: int) -> float:
        return (float(num) / float(den)) if den > 0 else 0.0

    span_valid_rate = safe_rate(span_ok, mention_total)
    matched_rate = safe_rate(matched_ok, mention_total)
    canonical_rate = safe_rate(canonical_ok, mention_total)
    mechanism_bound_rate = safe_rate(mechanism_bound, mention_total)
    ready_with_mechanism_rate = safe_rate(ready_with_mechanism, mention_total)
    mechanism_bound_rate_valid_all = safe_rate(mechanism_bound_valid_all, valid_all_den)
    mechanism_bound_rate_valid_numeric = safe_rate(mechanism_bound_valid_numeric, valid_numeric_den)
    strict_all_rate_valid_numeric = safe_rate(strict_all_count, valid_numeric_den)
    strict_high_rate_valid_numeric = safe_rate(strict_high_count, valid_numeric_den)
    local_supported_rate_valid_numeric = safe_rate(local_supported_count, valid_numeric_den)
    pricing_negative_conflict_rate_valid_numeric = safe_rate(pricing_negative_conflict_count, valid_numeric_den)

    targets = {
        "normalization_matched_rate": 0.90,
        "mechanism_bound_rate_valid_numeric": 0.85,
        "strict_high_rate_valid_numeric": 0.65,
        "local_supported_rate_valid_numeric": 0.85,
    }
    target_pass = {
        "normalization_matched_rate": matched_rate >= targets["normalization_matched_rate"],
        "mechanism_bound_rate_valid_numeric": mechanism_bound_rate_valid_numeric >= targets["mechanism_bound_rate_valid_numeric"],
        "strict_high_rate_valid_numeric": strict_high_rate_valid_numeric >= targets["strict_high_rate_valid_numeric"],
        "local_supported_rate_valid_numeric": local_supported_rate_valid_numeric >= targets["local_supported_rate_valid_numeric"],
    }

    report = {
        "input": {
            "clause_pred_file": args.clause_pred_file,
            "clause_source_file": args.clause_source_file,
            "clause_total": all_clause_den,
            "known_mechanisms": KNOWN_MECHANISMS,
            "strict_high_threshold": args.strict_high_threshold,
            "bind_min_score": args.bind_min_score,
        },
        "frozen_denominators": {
            "all_clause": all_clause_den,
            "valid_all": valid_all_den,
            "valid_numeric": valid_numeric_den,
            "mention_total": mention_total,
        },
        "counts": {
            "mention_total": mention_total,
            "definition_total": len(definitions_rows),
            "triple_total": len(triples),
            "parse_error_count": parse_error_count,
            "span_valid_count": span_ok,
            "normalization_attempted_count": normalization_attempted_count,
            "normalization_matched_count": matched_ok,
            "canonical_key_count": canonical_ok,
            "mechanism_bound_count": mechanism_bound,
            "ready_with_mechanism_count": ready_with_mechanism,
            "strict_all_count": strict_all_count,
            "strict_high_count": strict_high_count,
            "mechanism_bound_valid_all_count": mechanism_bound_valid_all,
            "mechanism_bound_valid_numeric_count": mechanism_bound_valid_numeric,
            "local_supported_count": local_supported_count,
            "pricing_negative_conflict_count": pricing_negative_conflict_count,
            "unit_conflict_group_count": len(conflict_items),
            "clause_candidate_non_empty_count": clause_candidate_non_empty,
            "clause_negative_count": clause_negative_count,
            "raw_value_filtered_non_value_count": raw_value_filtered_non_value,
            "raw_value_filtered_by_rule_count": raw_value_filtered_by_rule,
            "unit_pairing_dropped_count": unit_pairing_dropped_count,
            "unit_alias_applied_count": unit_alias_applied_count,
            "full_clause_retry_success_count": full_clause_retry_success_count,
            "post_guard_adjusted_count": sum(post_guard_counter.values()),
            "low_confidence_cap_count": low_confidence_cap_count,
            "time_window_tou_override_count": time_window_tou_override_count,
            "strict_high_compat_block_count": strict_high_compat_block_count,
            "strict_high_weak_constraint_block_count": strict_high_weak_constraint_block_count,
        },
        "rates": {
            "span_valid_rate": round(span_valid_rate, 6),
            "normalization_matched_rate": round(matched_rate, 6),
            "canonical_key_rate": round(canonical_rate, 6),
            "mechanism_bound_rate": round(mechanism_bound_rate, 6),
            "ready_with_mechanism_rate": round(ready_with_mechanism_rate, 6),
            "mechanism_bound_rate_valid_all": round(mechanism_bound_rate_valid_all, 6),
            "mechanism_bound_rate_valid_numeric": round(mechanism_bound_rate_valid_numeric, 6),
            "strict_all_rate_valid_numeric": round(strict_all_rate_valid_numeric, 6),
            "strict_high_rate_valid_numeric": round(strict_high_rate_valid_numeric, 6),
            "local_supported_rate_valid_numeric": round(local_supported_rate_valid_numeric, 6),
            "pricing_negative_conflict_rate_valid_numeric": round(pricing_negative_conflict_rate_valid_numeric, 6),
            "clause_candidate_non_empty_rate": round(safe_rate(clause_candidate_non_empty, all_clause_den), 6),
            "clause_negative_rate": round(safe_rate(clause_negative_count, all_clause_den), 6),
        },
        "metrics_with_denominator": {
            "normalization_matched_on_mentions": {
                "num": matched_ok,
                "den": mention_total,
                "rate": round(matched_rate, 6),
            },
            "mechanism_bound_on_valid_all": {
                "num": mechanism_bound_valid_all,
                "den": valid_all_den,
                "rate": round(mechanism_bound_rate_valid_all, 6),
            },
            "mechanism_bound_on_valid_numeric": {
                "num": mechanism_bound_valid_numeric,
                "den": valid_numeric_den,
                "rate": round(mechanism_bound_rate_valid_numeric, 6),
            },
            "strict_all_on_valid_numeric": {
                "num": strict_all_count,
                "den": valid_numeric_den,
                "rate": round(strict_all_rate_valid_numeric, 6),
            },
            "strict_high_on_valid_numeric": {
                "num": strict_high_count,
                "den": valid_numeric_den,
                "rate": round(strict_high_rate_valid_numeric, 6),
            },
        },
        "targets": targets,
        "target_pass": target_pass,
        "all_targets_passed": all(target_pass.values()),
        "distribution": {
            "param_type_top20": dict(param_type_counter.most_common(20)),
            "norm_unit_top20": dict(norm_unit_counter.most_common(20)),
            "rule_top20": dict(rule_counter.most_common(20)),
            "filtered_rule_counts": dict(filtered_counter),
            "bind_reason_top20": dict(bind_reason_counter.most_common(20)),
            "bind_transition_top20": dict(bind_transition_counter.most_common(20)),
            "skip_reason_top20": dict(skip_reason_counter.most_common(20)),
            "post_guard_top20": dict(post_guard_counter.most_common(20)),
        },
        "unit_conflicts_top20": conflict_items[:20],
    }

    prefix = args.output_prefix
    mentions_file = OUTPUT_DIR / f"{prefix}_parameter_mentions.jsonl"
    defs_file = OUTPUT_DIR / f"{prefix}_parameter_definitions.jsonl"
    triples_file = OUTPUT_DIR / f"{prefix}_triples_spo.jsonl"
    report_json_file = OUTPUT_DIR / f"{prefix}_validation_report.json"
    report_md_file = OUTPUT_DIR / f"{prefix}_validation_report.md"

    write_jsonl(mentions_file, mentions)
    write_jsonl(defs_file, definitions_rows)
    write_jsonl(triples_file, triples)
    write_json(report_json_file, report)

    md_lines = [
        f"# {prefix} normalization + correction + validation report",
        "",
        "## Inputs",
        f"- clause_pred_file: `{args.clause_pred_file}`",
        f"- clause_source_file: `{args.clause_source_file}`",
        f"- clause_total: {all_clause_den}",
        f"- strict_high_threshold: {args.strict_high_threshold}",
        f"- bind_min_score: {args.bind_min_score}",
        "",
        "## Frozen Denominators",
        f"- all_clause: {all_clause_den}",
        f"- mention_total: {mention_total}",
        f"- valid_all: {valid_all_den}",
        f"- valid_numeric: {valid_numeric_den}",
        "",
        "## Main Metrics (num/den/rate)",
        f"- normalization_matched_on_mentions: {matched_ok}/{mention_total} = {matched_rate:.6f}",
        f"- mechanism_bound_on_valid_all: {mechanism_bound_valid_all}/{valid_all_den} = {mechanism_bound_rate_valid_all:.6f}",
        f"- mechanism_bound_on_valid_numeric: {mechanism_bound_valid_numeric}/{valid_numeric_den} = {mechanism_bound_rate_valid_numeric:.6f}",
        f"- strict_all_on_valid_numeric: {strict_all_count}/{valid_numeric_den} = {strict_all_rate_valid_numeric:.6f}",
        f"- strict_high_on_valid_numeric: {strict_high_count}/{valid_numeric_den} = {strict_high_rate_valid_numeric:.6f}",
        "",
        "## Target Check",
        f"- normalization_matched_rate >= {targets['normalization_matched_rate']}: {target_pass['normalization_matched_rate']}",
        f"- mechanism_bound_rate_valid_numeric >= {targets['mechanism_bound_rate_valid_numeric']}: {target_pass['mechanism_bound_rate_valid_numeric']}",
        f"- strict_high_rate_valid_numeric >= {targets['strict_high_rate_valid_numeric']}: {target_pass['strict_high_rate_valid_numeric']}",
        f"- local_supported_rate_valid_numeric >= {targets['local_supported_rate_valid_numeric']}: {target_pass['local_supported_rate_valid_numeric']}",
        "",
        "## Top Bind Reasons",
    ]
    for k, v in bind_reason_counter.most_common(15):
        md_lines.append(f"- {k}: {v}")
    md_lines.extend(
        [
            "",
            "## Artifacts",
            f"- `{mentions_file.relative_to(PROJECT_ROOT).as_posix()}`",
            f"- `{defs_file.relative_to(PROJECT_ROOT).as_posix()}`",
            f"- `{triples_file.relative_to(PROJECT_ROOT).as_posix()}`",
            f"- `{report_json_file.relative_to(PROJECT_ROOT).as_posix()}`",
        ]
    )
    report_md_file.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(json.dumps(report["counts"], ensure_ascii=False))
    print(json.dumps(report["rates"], ensure_ascii=False))
    print(json.dumps({"target_pass": target_pass, "all_targets_passed": report["all_targets_passed"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
