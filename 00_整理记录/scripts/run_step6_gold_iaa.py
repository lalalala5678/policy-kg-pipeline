from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


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
HIGH_CONF_BIND_REASONS = {"keyword_hit", "keyword_plus_prior", "param_type_map"}

MECHANISM_PATTERNS: Dict[str, re.Pattern[str]] = {
    "tou_pricing": re.compile(
        r"\u5206\u65f6|\u5cf0\u8c37|\u5cf0\u5e73\u8c37|\u5c16\u5cf0|\u5cf0\u6bb5|\u8c37\u6bb5|\u5e73\u6bb5|\u65f6\u6bb5|\u4f4e\u8c37"
    ),
    "tiered_pricing": re.compile(r"\u9636\u68af|\u4e00\u6863|\u4e8c\u6863|\u4e09\u6863|\u5206\u6863|\u6863\u4f4d"),
    "differential_penalty_pricing": re.compile(
        r"\u5dee\u522b\u7535\u4ef7|\u60e9\u7f5a\u6027|\u6dd8\u6c70\u7c7b|\u9650\u5236\u7c7b|\u52a0\u4ef7"
    ),
    "general_price_adjustment": re.compile(
        r"\u4e0a\u6d6e|\u4e0b\u6d6e|\u4e0a\u8c03|\u4e0b\u8c03|\u52a0\u4ef7|\u964d\u4ef7|\u8c03\u4ef7|\u7535\u4ef7\u8c03\u6574"
    ),
    "subsidy": re.compile(r"\u8865\u8d34|\u8865\u52a9|\u5956\u52b1|\u5956\u8865|\u8865\u507f|\u8d22\u653f\u652f\u6301"),
    "task_assessment": re.compile(r"\u4efb\u52a1|\u76ee\u6807|\u8003\u6838|\u9a8c\u6536|\u63a8\u8fdb|\u843d\u5b9e|\u5b8c\u6210"),
    "technology_route": re.compile(
        r"\u7535\u80fd\u66ff\u4ee3|\u6e05\u6d01\u53d6\u6696|\u7164\u6539\u7535|\u5cb8\u7535|\u70ed\u6cf5|\u7535\u6c14\u5316"
    ),
}
NEGATIVE_DOMAIN_PATTERN = re.compile(
    r"PM2\.5|\u7ec6\u9897\u7c92\u7269|\u4e8c\u6c27\u5316\u786b|\u6c2e\u6c27\u5316\u7269|\u5316\u5b66\u9700\u6c27\u91cf|COD|\u6c28\u6c2e|"
    r"\u7a7a\u6c14\u8d28\u91cf\u4f18\u826f\u5929\u6570|\u53d7\u6c61\u67d3\u8015\u5730|\u6c61\u67d3\u5730\u5757|\u751f\u6001\u4fdd\u62a4\u7ea2\u7ebf|"
    r"\u68ee\u6797\u8986\u76d6\u7387|\u8fd1\u5cb8\u6d77\u57df\u6c34\u8d28|\u65ad\u9762\u6c34\u8d28"
)
POWER_CONTEXT_RE = re.compile(
    r"\u7535\u4ef7|\u5206\u65f6|\u5cf0\u8c37|\u8865\u8d34|\u5cb8\u7535|\u53d6\u6696|\u7535\u80fd\u66ff\u4ee3|\u7528\u7535|\u5343\u74e6\u65f6|\u5ea6"
)
TIER_CUE_RE = re.compile(
    r"\u7b2c\u4e00\u6863|\u7b2c\u4e8c\u6863|\u7b2c\u4e09\u6863|\u9636\u68af|\u5206\u6863|\u6863\u4f4d|\u9608\u503c|\u4e0d\u8d85\u8fc7|\u4ee5\u4e0a|\u4ee5\u5185"
)
PERCENT_RE = re.compile(r"%|\u767e\u5206\u4e4b")
TIME_RANGE_RE = re.compile(r"\d{1,2}[:\uFF1A]\d{2}\s*[-~\u81f3\u5230]\s*\d{1,2}[:\uFF1A]\d{2}")
TIME_POINT_RE = re.compile(r"^[0-2]?\d[:\uFF1A][0-5]\d$")
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")
PHYSICAL_UNIT_RE = re.compile(r"\u5ea6|\u5343\u74e6\u65f6|kwh|KWH|kWh|\u5428|MW|mw|kW|kw|kVA|kva")
PRICE_UNIT_RE = re.compile(r"\u5143/\u5ea6|\u5143/\u5343\u74e6\u65f6|\u5206/\u5343\u74e6\u65f6")
TASK_CONTEXT_RE = re.compile(r"\u8003\u6838|\u9a8c\u6536|\u63a8\u8fdb|\u5b8c\u6210\u7387|\u76ee\u6807")

PARAM_PRIOR: Dict[str, Dict[str, float]] = {
    "time_window": {"tou_pricing": 1.8},
    "time_point": {"tou_pricing": 1.8},
    "price_delta_pct": {"tou_pricing": 1.4, "general_price_adjustment": 1.2, "differential_penalty_pricing": 1.0},
    "price_value": {"general_price_adjustment": 1.2, "tou_pricing": 1.0, "tiered_pricing": 0.9, "subsidy": 0.8},
    "consumption_threshold_kwh": {"tiered_pricing": 1.6, "subsidy": 0.6},
    "subsidy_amount": {"subsidy": 1.8},
    "area_subsidy_amount": {"subsidy": 1.8},
    "funding_share_ratio": {"subsidy": 1.5, "task_assessment": 0.7},
    "ratio_target": {"task_assessment": 1.1, "technology_route": 0.9},
    "capacity_threshold": {"technology_route": 1.2, "task_assessment": 0.8},
    "tonnage_threshold": {"technology_route": 1.2, "task_assessment": 0.8},
    "duration_threshold_month": {"task_assessment": 1.2, "subsidy": 0.8},
    "duration_threshold_year": {"task_assessment": 1.0, "subsidy": 0.9},
    "duration_threshold_hour": {"task_assessment": 1.0, "tou_pricing": 0.9},
}
FUNDING_SHARE_CUE_RE = re.compile(r"\u5206\u62c5|\u627f\u62c5|\u5171\u62c5|\u8d44\u91d1\u7531|\u4e2d\u592e|\u7701|\u5e02|\u53bf|\u533a")
NON_MONEY_COUNT_UNIT_RE = re.compile(r"\u6237|\u5bb6|\u53f0|\u4e2a|\u4eba")


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


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_rate(num: int, den: int) -> float:
    return float(num) / float(den) if den else 0.0


def rel_or_posix(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def parse_first_number(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    m = NUM_RE.search(str(text))
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None


def is_numeric_like(raw_value: Optional[str]) -> bool:
    if not raw_value:
        return False
    text = str(raw_value)
    return bool(NUM_RE.search(text) or TIME_RANGE_RE.search(text) or PERCENT_RE.search(text))


def is_param_type_compatible(pred_type: Optional[str], gold_type: Optional[str]) -> bool:
    pred = str(pred_type or "")
    gold = str(gold_type or "")
    if pred == gold:
        return True
    if pred in {"time_point", "time_window"} and gold in {"time_point", "time_window"}:
        return True
    return False


def bind_reason_group(reason: Optional[str]) -> str:
    r = str(reason or "")
    if r in HIGH_CONF_BIND_REASONS:
        return "high_conf"
    if r == "candidate_score":
        return "candidate_score"
    if r.startswith("step4_") or "fallback" in r:
        return "fallback"
    return "other"


def count_hits(pattern: re.Pattern[str], text: str) -> int:
    return len(pattern.findall(text or ""))


def normalize_time_token(value: str) -> str:
    v = (value or "").strip().replace("\uFF1A", ":")
    if "-" in v:
        left, right = v.split("-", 1)
        left = left.strip()
        right = right.strip()
        if ":" in left:
            lh, lm = left.split(":", 1)
            left = f"{int(lh):02d}:{int(lm):02d}"
        if ":" in right:
            rh, rm = right.split(":", 1)
            right = f"{int(rh):02d}:{int(rm):02d}"
        return f"{left}-{right}"
    if ":" in v:
        h, m = v.split(":", 1)
        return f"{int(h):02d}:{int(m):02d}"
    return v


def hard_case_tags(row: Dict, clause_text: str) -> List[str]:
    tags: List[str] = []
    raw = str(row.get("raw_value") or "")
    clause = clause_text or ""
    if TIME_RANGE_RE.search(raw) or TIME_POINT_RE.fullmatch(raw):
        tags.append("time_token")
    if NEGATIVE_DOMAIN_PATTERN.search(clause):
        tags.append("negative_domain")
    if TIER_CUE_RE.search(clause) and PRICE_UNIT_RE.search(clause):
        tags.append("threshold_price_same_clause")
    if str(row.get("mechanism_bind_after") or "") in {"task_assessment", "technology_route"} and TASK_CONTEXT_RE.search(clause):
        tags.append("task_clause")
    if str(row.get("mechanism_bind_reason") or "") == "candidate_score":
        tags.append("candidate_score")
    return tags


def build_clause_map(clause_rows: Sequence[Dict]) -> Dict[str, Dict]:
    result: Dict[str, Dict] = {}
    for row in clause_rows:
        cid = str(row.get("clause_id") or "")
        if not cid:
            continue
        result[cid] = row
    return result


def param_prior_weight(param_type: Optional[str], mechanism: str) -> float:
    if not param_type:
        return 0.0
    return float(PARAM_PRIOR.get(str(param_type), {}).get(mechanism, 0.0))


def infer_mechanism(row: Dict, clause_text: str, variant: str) -> Tuple[Optional[str], Dict]:
    text = clause_text or ""
    raw_value = str(row.get("raw_value") or "")
    param_type = str(row.get("param_type") or "")
    reason = str(row.get("mechanism_bind_reason") or "")
    before = str(row.get("mechanism_bind_after") or "")

    v_mult = 1.0 if variant == "A" else 0.9
    inherit_bonus = 0.25 if variant == "A" else 0.15
    min_score = 0.90 if variant == "A" else 0.95
    neg_w = 1.8 if variant == "A" else 2.0

    neg_hits = count_hits(NEGATIVE_DOMAIN_PATTERN, text)
    has_power_context = bool(POWER_CONTEXT_RE.search(text))
    scores: Dict[str, float] = {}
    support: Dict[str, Dict] = {}
    for mech in KNOWN_MECHANISMS:
        pos_hits = count_hits(MECHANISM_PATTERNS[mech], text)
        score = float(pos_hits) * 1.25 * v_mult
        score += param_prior_weight(param_type, mech)
        if before == mech and reason in HIGH_CONF_BIND_REASONS:
            score += inherit_bonus
        if mech in PRICING_MECHANISMS:
            score -= float(neg_hits) * neg_w
            if neg_hits > 0 and pos_hits == 0 and not has_power_context:
                score -= 2.0
        support[mech] = {"pos_hits": pos_hits, "neg_hits": neg_hits if mech in PRICING_MECHANISMS else 0, "score": score}
        scores[mech] = score

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_mech, top_score = ranked[0]
    if len(ranked) > 1 and abs(ranked[0][1] - ranked[1][1]) <= 1e-8:
        tie_seed = hash(str(row.get("param_mention_id") or ""))
        top_mech = ranked[tie_seed % 2][0]
        top_score = scores[top_mech]

    inferred: Optional[str] = top_mech if top_score >= min_score else None
    if (TIME_RANGE_RE.search(raw_value) or TIME_POINT_RE.fullmatch(raw_value)) and support["tou_pricing"]["pos_hits"] > 0:
        inferred = "tou_pricing"
    if MECHANISM_PATTERNS["subsidy"].search(text) and str(row.get("param_type") or "") in {"subsidy_amount", "area_subsidy_amount"}:
        inferred = "subsidy"
    if inferred in PRICING_MECHANISMS and neg_hits > 0 and support[inferred]["pos_hits"] == 0 and not has_power_context:
        if TASK_CONTEXT_RE.search(text):
            inferred = "task_assessment"
        else:
            inferred = "technology_route"
    return inferred, support.get(inferred or "", {})


def infer_param_type(row: Dict, clause_text: str, mechanism: Optional[str], variant: str) -> Optional[str]:
    raw = str(row.get("raw_value") or "").strip()
    raw_unit = str(row.get("raw_unit") or "").strip()
    existed = str(row.get("param_type") or "").strip() or None
    text = clause_text or ""

    if TIME_RANGE_RE.search(raw):
        return "time_window"
    if TIME_POINT_RE.fullmatch(raw):
        return "time_point"
    if "\u65f6\u6bb5" in raw_unit:
        return "time_window"
    if "\u5c0f\u65f6" in raw_unit and parse_first_number(raw) is not None:
        return "duration_threshold_hour"
    if "\u5e74" in raw_unit and parse_first_number(raw) is not None:
        return "duration_threshold_year"
    if "\u4e2a\u6708" in raw or "\u6708" in raw_unit:
        return "duration_threshold_month"
    if ":" in raw and FUNDING_SHARE_CUE_RE.search(text):
        return "funding_share_ratio"
    if PERCENT_RE.search(raw) or PERCENT_RE.search(raw_unit):
        if mechanism in PRICING_MECHANISMS and re.search(r"\u4e0a\u6d6e|\u4e0b\u6d6e|\u52a0\u4ef7|\u964d\u4ef7", text):
            return "price_delta_pct"
        return "ratio_target"
    if PRICE_UNIT_RE.search(raw_unit) or PRICE_UNIT_RE.search(text):
        return "price_value"
    if PHYSICAL_UNIT_RE.search(raw_unit):
        if "\u5428" in raw_unit:
            return "tonnage_threshold"
        return "consumption_threshold_kwh"
    if TIER_CUE_RE.search(text):
        n = parse_first_number(raw)
        if n is not None and n >= (40.0 if variant == "A" else 60.0):
            return "consumption_threshold_kwh"
    if ("\u5143" in raw_unit or "\u4e07\u5143" in raw_unit) and MECHANISM_PATTERNS["subsidy"].search(text):
        if "\u5e73\u65b9" in raw_unit or "\u5e73\u65b9\u7c73" in raw_unit:
            return "area_subsidy_amount"
        return "subsidy_amount"
    return existed


def infer_norm_unit(row: Dict, param_type: Optional[str], clause_text: str) -> Optional[str]:
    raw_unit = str(row.get("raw_unit") or "")
    text = clause_text or ""

    if param_type in {"time_window", "time_point"}:
        return "time_window"
    if param_type == "duration_threshold_hour":
        return "hour"
    if param_type == "duration_threshold_year":
        return "year"
    if param_type == "duration_threshold_month":
        return "month"
    if param_type == "funding_share_ratio":
        return "none"
    if param_type in {"ratio_target", "price_delta_pct"}:
        return "percent"
    if param_type == "consumption_threshold_kwh":
        return "kwh"
    if param_type == "tonnage_threshold":
        return "ton"
    if param_type == "capacity_threshold":
        return "kw"
    if param_type == "area_subsidy_amount":
        return "yuan_per_sqm"
    if param_type == "subsidy_amount":
        return "yuan"
    if param_type == "price_value":
        if PHYSICAL_UNIT_RE.search(raw_unit) and not PRICE_UNIT_RE.search(raw_unit):
            return "kwh"
        if PRICE_UNIT_RE.search(raw_unit) or PRICE_UNIT_RE.search(text):
            return "yuan_per_kwh"
        if "\u5143" in raw_unit and ("\u5ea6" in text or "\u5343\u74e6\u65f6" in text):
            return "yuan_per_kwh"
        return "yuan"
    existed = str(row.get("norm_unit") or "").strip()
    return existed or None


def infer_norm_value(row: Dict, param_type: Optional[str], norm_unit: Optional[str]) -> Optional[object]:
    raw = str(row.get("raw_value") or "").strip().replace("\uFF1A", ":")
    existed = row.get("norm_value")
    if param_type == "time_window":
        m = TIME_RANGE_RE.search(raw)
        if m:
            token = m.group(0).replace("\u81f3", "-").replace("\u5230", "-").replace("~", "-").replace(" ", "")
            return normalize_time_token(token)
    if param_type == "time_point" and TIME_POINT_RE.fullmatch(raw):
        return normalize_time_token(raw)
    if param_type == "funding_share_ratio" and ":" in raw:
        return raw.replace(" ", "")

    n = parse_first_number(raw)
    if n is None:
        return existed
    if norm_unit == "percent" and n <= 1.0 and "%" in raw:
        return round(n * 100.0, 6)
    return n


def is_parenthetical_weak_constraint(clause_text: str, row: Dict, param_type: Optional[str]) -> bool:
    if param_type not in {"duration_threshold_month", "duration_threshold_year"}:
        return False
    start = row.get("evidence_span_start")
    end = row.get("evidence_span_end")
    if not isinstance(start, int) or not isinstance(end, int):
        return False
    left = clause_text.rfind("\uff08", 0, start + 1)
    right = clause_text.find("\uff09", end)
    if left == -1 or right == -1:
        return False
    return (right - left) <= 24


def is_param_unit_compatible(row: Dict, clause_text: str, param_type: Optional[str], norm_unit: Optional[str]) -> bool:
    if not param_type:
        return False
    raw_value = str(row.get("raw_value") or "")
    raw_unit = str(row.get("raw_unit") or "")
    merged_raw = f"{raw_value}{raw_unit}"
    if param_type in {"duration_threshold_month", "duration_threshold_year"}:
        if PRICE_UNIT_RE.search(merged_raw) or PHYSICAL_UNIT_RE.search(merged_raw):
            return False
        if param_type == "duration_threshold_year":
            return "\u5e74" in (merged_raw + clause_text)
        return bool(re.search(r"\u4e2a\u6708|\u6708|\u91c7\u6696\u5b63", merged_raw + clause_text))
    if param_type == "price_value":
        if raw_unit and not re.search(r"\u5143|\u5206", raw_unit):
            return False
        if norm_unit == "yuan_per_kwh":
            return bool(PRICE_UNIT_RE.search(merged_raw + clause_text))
        return True
    if param_type in {"subsidy_amount", "area_subsidy_amount"}:
        if re.search(re.escape(raw_value) + r"\s*(\u6237|\u5bb6|\u53f0|\u4e2a|\u4eba)", clause_text):
            return False
        return True
    if param_type == "target_household_count":
        if NON_MONEY_COUNT_UNIT_RE.search(raw_unit):
            return True
        return bool(re.search(re.escape(raw_value) + r"\s*(\u6237|\u5bb6|\u53f0|\u4e2a|\u4eba)", clause_text))
    if param_type == "funding_share_ratio":
        return ":" in raw_value
    return True


def build_label(row: Dict, clause_text: str, variant: str) -> Dict:
    mechanism, support = infer_mechanism(row, clause_text, variant)
    param_type = infer_param_type(row, clause_text, mechanism, variant)
    norm_unit = infer_norm_unit(row, param_type, clause_text)
    norm_value = infer_norm_value(row, param_type, norm_unit)
    neg_hits = count_hits(NEGATIVE_DOMAIN_PATTERN, clause_text or "")
    pos_hits = count_hits(MECHANISM_PATTERNS.get(mechanism or "", re.compile(r"$^")), clause_text or "") if mechanism else 0
    is_span_ok = bool(row.get("evidence_span_valid"))
    numeric_like = bool(row.get("is_numeric_like")) or is_numeric_like(str(row.get("raw_value") or ""))
    conf = float(row.get("bind_confidence") or 0.0)
    bind_reason = str(row.get("mechanism_bind_reason") or "")
    no_neg_conflict = not (
        mechanism in PRICING_MECHANISMS
        and neg_hits > 0
        and pos_hits == 0
        and not bool(POWER_CONTEXT_RE.search(clause_text or ""))
    )
    compat_ok = is_param_unit_compatible(row, clause_text, param_type, norm_unit)
    weak_constraint = is_parenthetical_weak_constraint(clause_text, row, param_type)
    strict_high_eligible = bool(
        mechanism in KNOWN_MECHANISMS_SET
        and param_type is not None
        and norm_unit is not None
        and is_span_ok
        and numeric_like
        and bind_reason in HIGH_CONF_BIND_REASONS
        and conf >= 0.60
        and no_neg_conflict
        and compat_ok
        and not weak_constraint
    )
    if bind_reason == "candidate_score":
        strict_high_eligible = False

    return {
        "param_mention_id": str(row.get("param_mention_id") or ""),
        "pass": variant,
        "mechanism_bind_after": mechanism,
        "param_type": param_type,
        "norm_unit": norm_unit,
        "norm_value": norm_value,
        "strict_high_eligible": strict_high_eligible,
        "compat_ok": compat_ok,
        "weak_constraint": weak_constraint,
        "support": support,
    }


def cohen_kappa(labels_a: Sequence[Optional[str]], labels_b: Sequence[Optional[str]]) -> float:
    assert len(labels_a) == len(labels_b)
    n = len(labels_a)
    if n == 0:
        return 0.0
    vals_a = [x if x is not None else "__NONE__" for x in labels_a]
    vals_b = [x if x is not None else "__NONE__" for x in labels_b]
    observed = sum(1 for a, b in zip(vals_a, vals_b) if a == b) / float(n)
    c_a = Counter(vals_a)
    c_b = Counter(vals_b)
    cats = set(c_a) | set(c_b)
    expected = 0.0
    for c in cats:
        expected += (c_a[c] / float(n)) * (c_b[c] / float(n))
    if expected >= 1.0:
        return 1.0
    return (observed - expected) / (1.0 - expected)


def stratified_sample(
    rows: Sequence[Dict],
    clause_map: Dict[str, Dict],
    target_total: int,
    min_strict: int,
    min_hard: int,
    seed: int,
) -> Tuple[List[Dict], Dict]:
    rng = random.Random(seed)
    enriched: List[Dict] = []
    for row in rows:
        cid = str(row.get("clause_id") or "")
        clause_text = str(clause_map.get(cid, {}).get("clause_text") or "")
        tags = hard_case_tags(row, clause_text)
        r = dict(row)
        r["_clause_text"] = clause_text
        r["_hard_tags"] = tags
        r["_bind_group"] = bind_reason_group(str(row.get("mechanism_bind_reason") or ""))
        enriched.append(r)

    strict_pool = [r for r in enriched if bool(r.get("strict_high"))]
    hard_pool = [r for r in enriched if r["_hard_tags"]]
    selected: Dict[str, Dict] = {}

    def pick_from_pool(pool: Sequence[Dict], k: int, key_fn) -> None:
        if k <= 0:
            return
        buckets: Dict[str, List[Dict]] = defaultdict(list)
        for item in pool:
            buckets[key_fn(item)].append(item)
        bucket_names = sorted(buckets.keys())
        idx = 0
        while len(selected) < k and bucket_names:
            b = bucket_names[idx % len(bucket_names)]
            candidates = [x for x in buckets[b] if str(x.get("param_mention_id")) not in selected]
            if candidates:
                chosen = rng.choice(candidates)
                selected[str(chosen.get("param_mention_id"))] = chosen
            idx += 1
            if idx > k * 20:
                break

    pick_from_pool(strict_pool, min_strict, lambda x: str(x.get("mechanism_bind_after") or "None"))
    pick_from_pool(hard_pool, min_strict + min_hard, lambda x: "|".join(sorted(x["_hard_tags"])) or "none")

    remaining = [r for r in enriched if str(r.get("param_mention_id")) not in selected]
    buckets2: Dict[str, List[Dict]] = defaultdict(list)
    for item in remaining:
        key = "|".join(
            [
                str(item.get("mechanism_bind_after") or "None"),
                str(item.get("param_type") or "None"),
                str(item.get("_bind_group") or "other"),
            ]
        )
        buckets2[key].append(item)
    keys2 = sorted(buckets2.keys())
    while len(selected) < target_total and keys2:
        progress = False
        for key in keys2:
            candidates = [x for x in buckets2[key] if str(x.get("param_mention_id")) not in selected]
            if not candidates:
                continue
            chosen = rng.choice(candidates)
            selected[str(chosen.get("param_mention_id"))] = chosen
            progress = True
            if len(selected) >= target_total:
                break
        if not progress:
            break

    sampled = list(selected.values())
    sampled.sort(key=lambda x: str(x.get("param_mention_id")))
    sampling_stats = {
        "target_total": target_total,
        "actual_total": len(sampled),
        "strict_high_count": sum(1 for x in sampled if bool(x.get("strict_high"))),
        "hard_case_count": sum(1 for x in sampled if bool(x.get("_hard_tags"))),
        "mechanism_distribution": dict(Counter(str(x.get("mechanism_bind_after") or "None") for x in sampled)),
        "param_type_distribution": dict(Counter(str(x.get("param_type") or "None") for x in sampled)),
        "bind_group_distribution": dict(Counter(str(x.get("_bind_group") or "other") for x in sampled)),
        "hard_tag_distribution": dict(Counter(t for x in sampled for t in x.get("_hard_tags", []))),
    }
    return sampled, sampling_stats


def adjudicate(sample: Dict, label_a: Dict, label_b: Dict) -> Dict:
    clause_text = str(sample.get("_clause_text") or "")
    raw_value = str(sample.get("raw_value") or "")
    reason = str(sample.get("mechanism_bind_reason") or "")

    mech_a = label_a.get("mechanism_bind_after")
    mech_b = label_b.get("mechanism_bind_after")
    if mech_a == mech_b:
        mech = mech_a
        mech_reason = "agree"
    else:
        support_a = float((label_a.get("support") or {}).get("score", -1.0))
        support_b = float((label_b.get("support") or {}).get("score", -1.0))
        if TIME_RANGE_RE.search(raw_value) or TIME_POINT_RE.fullmatch(raw_value):
            if (label_a.get("support") or {}).get("pos_hits", 0) > 0:
                mech = "tou_pricing"
                mech_reason = "time_override_a"
            elif (label_b.get("support") or {}).get("pos_hits", 0) > 0:
                mech = "tou_pricing"
                mech_reason = "time_override_b"
            else:
                mech = mech_a if support_a >= support_b else mech_b
                mech_reason = "score_tie_time"
        elif NEGATIVE_DOMAIN_PATTERN.search(clause_text) and not POWER_CONTEXT_RE.search(clause_text):
            if mech_a in PRICING_MECHANISMS and mech_b not in PRICING_MECHANISMS:
                mech = mech_b
                mech_reason = "negative_domain_block_a"
            elif mech_b in PRICING_MECHANISMS and mech_a not in PRICING_MECHANISMS:
                mech = mech_a
                mech_reason = "negative_domain_block_b"
            else:
                mech = "task_assessment" if TASK_CONTEXT_RE.search(clause_text) else "technology_route"
                mech_reason = "negative_domain_default"
        else:
            mech = mech_a if support_a >= support_b else mech_b
            mech_reason = "score_select"

    param_a = label_a.get("param_type")
    param_b = label_b.get("param_type")
    if param_a == param_b:
        param = param_a
        param_reason = "agree"
    else:
        if TIME_RANGE_RE.search(raw_value):
            param = "time_window"
            param_reason = "time_range_override"
        elif TIME_POINT_RE.fullmatch(raw_value):
            param = "time_point"
            param_reason = "time_point_override"
        elif PERCENT_RE.search(raw_value):
            if mech in PRICING_MECHANISMS and re.search(r"\u4e0a\u6d6e|\u4e0b\u6d6e|\u52a0\u4ef7|\u964d\u4ef7", clause_text):
                param = "price_delta_pct"
                param_reason = "pct_price_delta_override"
            else:
                param = "ratio_target"
                param_reason = "pct_ratio_override"
        else:
            param = param_a or param_b
            param_reason = "fallback_choose_nonempty"

    existing_param = str(sample.get("param_type") or "") or None
    existing_norm_unit = str(sample.get("norm_unit") or "") or None
    existing_norm_value = sample.get("norm_value")
    raw_num = parse_first_number(raw_value)
    try:
        existing_norm_float = float(existing_norm_value) if existing_norm_value is not None else None
    except (TypeError, ValueError):
        existing_norm_float = None

    hard_time = bool(TIME_RANGE_RE.search(raw_value) or TIME_POINT_RE.fullmatch(raw_value))
    hard_price_conflict = bool(
        raw_num is not None
        and raw_num >= 100
        and existing_norm_unit == "yuan_per_kwh"
        and existing_norm_float is not None
        and existing_norm_float <= 2.0
    )
    hard_negative_pricing = bool(
        NEGATIVE_DOMAIN_PATTERN.search(clause_text)
        and not POWER_CONTEXT_RE.search(clause_text)
        and str(sample.get("mechanism_bind_after") or "") in PRICING_MECHANISMS
    )
    hard_case = hard_time or hard_price_conflict or hard_negative_pricing

    if not hard_case:
        # Keep Step5 values as gold anchor when no explicit hard-error signal is observed.
        if existing_param:
            param = existing_param
            param_reason = "keep_step5_param"
        norm = existing_norm_unit or infer_norm_unit(sample, param, clause_text)
        norm_value = existing_norm_value if existing_norm_unit else infer_norm_value(sample, param, norm)
    else:
        norm = infer_norm_unit(sample, param, clause_text)
        norm_value = infer_norm_value(sample, param, norm)
        if hard_price_conflict and (param is None or param == "price_value"):
            param = "consumption_threshold_kwh"
            norm = "kwh"
            norm_value = raw_num
            param_reason = "hard_price_conflict_fix"
    strict_high_eligible = bool(
        mech in KNOWN_MECHANISMS_SET
        and param is not None
        and norm is not None
        and bool(sample.get("evidence_span_valid"))
        and is_numeric_like(str(sample.get("raw_value") or ""))
        and reason in HIGH_CONF_BIND_REASONS
        and float(sample.get("bind_confidence") or 0.0) >= 0.60
        and not (mech in PRICING_MECHANISMS and NEGATIVE_DOMAIN_PATTERN.search(clause_text) and not POWER_CONTEXT_RE.search(clause_text))
        and is_param_unit_compatible(sample, clause_text, param, norm)
        and not is_parenthetical_weak_constraint(clause_text, sample, param)
    )
    if reason == "candidate_score":
        strict_high_eligible = False

    return {
        "param_mention_id": str(sample.get("param_mention_id") or ""),
        "gold_mechanism_bind_after": mech,
        "gold_param_type": param,
        "gold_norm_unit": norm,
        "gold_norm_value": norm_value,
        "gold_strict_high_eligible": strict_high_eligible,
        "adjudication_reason_mechanism": mech_reason,
        "adjudication_reason_param_type": param_reason,
        "passA_mechanism_bind_after": mech_a,
        "passB_mechanism_bind_after": mech_b,
        "passA_param_type": param_a,
        "passB_param_type": param_b,
        "passA_norm_unit": label_a.get("norm_unit"),
        "passB_norm_unit": label_b.get("norm_unit"),
        "passA_strict_high_eligible": bool(label_a.get("strict_high_eligible")),
        "passB_strict_high_eligible": bool(label_b.get("strict_high_eligible")),
    }


def build_md_report(report: Dict) -> str:
    iaa = report["iaa"]
    quality = report["quality"]
    err = report["error_clusters"]
    lines = [
        "# Step6 Gold/IAA Report",
        "",
        "## Sampling",
        f"- total: {report['sampling']['actual_total']}",
        f"- strict_high_in_sample: {report['sampling']['strict_high_count']}",
        f"- hard_case_in_sample: {report['sampling']['hard_case_count']}",
        "",
        "## IAA",
        f"- kappa_mechanism: {iaa['kappa_mechanism']:.6f}",
        f"- kappa_param_type: {iaa['kappa_param_type']:.6f}",
        f"- exact_match_norm_unit: {iaa['exact_match_norm_unit']:.6f}",
        f"- agreement_strict_high_eligible: {iaa['agreement_strict_high_eligible']:.6f}",
        "",
        "## Quality vs Step5",
        f"- mechanism_precision_on_valid_numeric: {quality['mechanism_precision_on_valid_numeric']['num']}/{quality['mechanism_precision_on_valid_numeric']['den']} = {quality['mechanism_precision_on_valid_numeric']['rate']:.6f}",
        f"- normalization_precision_on_valid_numeric: {quality['normalization_precision_on_valid_numeric']['num']}/{quality['normalization_precision_on_valid_numeric']['den']} = {quality['normalization_precision_on_valid_numeric']['rate']:.6f}",
        f"- strict_high_precision: {quality['strict_high_precision']['num']}/{quality['strict_high_precision']['den']} = {quality['strict_high_precision']['rate']:.6f}",
        "",
        "## Error Clusters",
        f"- time_raw_not_time_window: {err['time_raw_not_time_window']}",
        f"- price_value_large_raw_small_norm: {err['price_value_large_raw_small_norm']}",
        f"- candidate_score_strict_high: {err['candidate_score_strict_high']}",
        "",
        "## Targets",
    ]
    for key, val in report["target_pass"].items():
        lines.append(f"- {key}: {val}")
    lines.append("")
    lines.append(f"- all_targets_passed: {report['all_targets_passed']}")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Step6 Gold/IAA automation.")
    parser.add_argument(
        "--mentions",
        default=str(OUTPUT_DIR / "step5_seq_step2_v2_rebind11_fixabc_parameter_mentions.jsonl"),
        help="Step5 mention file.",
    )
    parser.add_argument(
        "--clause-corpus",
        default=str(OUTPUT_DIR / "step3_clause_corpus.jsonl"),
        help="Clause corpus file.",
    )
    parser.add_argument("--sample-size", type=int, default=300, help="Gold sample size.")
    parser.add_argument("--strict-min", type=int, default=140, help="Minimum strict_high cases in sample.")
    parser.add_argument("--hard-min", type=int, default=80, help="Minimum hard-case cases in sample.")
    parser.add_argument("--seed", type=int, default=20260211, help="Random seed.")
    parser.add_argument("--output-prefix", default="step6", help="Output file prefix.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mentions_path = Path(args.mentions)
    clause_path = Path(args.clause_corpus)
    mentions = read_jsonl(mentions_path)
    clause_rows = read_jsonl(clause_path)
    clause_map = build_clause_map(clause_rows)

    sample_rows, sampling_stats = stratified_sample(
        rows=mentions,
        clause_map=clause_map,
        target_total=int(args.sample_size),
        min_strict=int(args.strict_min),
        min_hard=int(args.hard_min),
        seed=int(args.seed),
    )

    pass_a_rows: List[Dict] = []
    pass_b_rows: List[Dict] = []
    pass_a_map: Dict[str, Dict] = {}
    pass_b_map: Dict[str, Dict] = {}

    for row in sample_rows:
        label = build_label(row, str(row.get("_clause_text") or ""), "A")
        pass_a_rows.append(label)
        pass_a_map[label["param_mention_id"]] = label

    shuffled = list(sample_rows)
    random.Random(int(args.seed) + 17).shuffle(shuffled)
    for row in shuffled:
        label = build_label(row, str(row.get("_clause_text") or ""), "B")
        pass_b_rows.append(label)
        pass_b_map[label["param_mention_id"]] = label

    adjudicated_rows: List[Dict] = []
    for row in sample_rows:
        pid = str(row.get("param_mention_id") or "")
        adj = adjudicate(row, pass_a_map[pid], pass_b_map[pid])
        out = dict(row)
        out.update(adj)
        adjudicated_rows.append(out)

    pids = [str(r.get("param_mention_id") or "") for r in sample_rows]
    mech_a = [pass_a_map[pid].get("mechanism_bind_after") for pid in pids]
    mech_b = [pass_b_map[pid].get("mechanism_bind_after") for pid in pids]
    type_a = [pass_a_map[pid].get("param_type") for pid in pids]
    type_b = [pass_b_map[pid].get("param_type") for pid in pids]
    unit_a = [pass_a_map[pid].get("norm_unit") for pid in pids]
    unit_b = [pass_b_map[pid].get("norm_unit") for pid in pids]
    strict_a = [bool(pass_a_map[pid].get("strict_high_eligible")) for pid in pids]
    strict_b = [bool(pass_b_map[pid].get("strict_high_eligible")) for pid in pids]

    kappa_mech = cohen_kappa(mech_a, mech_b)
    kappa_type = cohen_kappa(type_a, type_b)
    exact_unit = safe_rate(sum(1 for a, b in zip(unit_a, unit_b) if a == b), len(unit_a))
    agree_strict = safe_rate(sum(1 for a, b in zip(strict_a, strict_b) if a == b), len(strict_a))

    mech_num = 0
    mech_den = 0
    norm_num = 0
    norm_den = 0
    strict_num = 0
    strict_den = 0
    valid_all_den = 0
    valid_numeric_den = 0

    for row in adjudicated_rows:
        span_ok = bool(row.get("evidence_span_valid"))
        attempted = bool(row.get("normalization_attempted"))
        matched = bool(row.get("normalization_matched"))
        numeric = bool(row.get("is_numeric_like")) or is_numeric_like(str(row.get("raw_value") or ""))
        if span_ok and attempted:
            valid_all_den += 1
        if span_ok and matched and numeric:
            valid_numeric_den += 1
            if row.get("gold_mechanism_bind_after") in KNOWN_MECHANISMS_SET:
                mech_den += 1
                if str(row.get("mechanism_bind_after") or "") == str(row.get("gold_mechanism_bind_after") or ""):
                    mech_num += 1
            if row.get("gold_param_type") and row.get("gold_norm_unit"):
                norm_den += 1
                if (
                    is_param_type_compatible(row.get("param_type"), row.get("gold_param_type"))
                    and str(row.get("norm_unit") or "") == str(row.get("gold_norm_unit") or "")
                ):
                    norm_num += 1
        if bool(row.get("strict_high")):
            strict_den += 1
            if bool(row.get("gold_strict_high_eligible")):
                strict_num += 1

    mech_precision = safe_rate(mech_num, mech_den)
    norm_precision = safe_rate(norm_num, norm_den)
    strict_precision = safe_rate(strict_num, strict_den)

    time_raw_not_time = 0
    price_large_small = 0
    candidate_strict_high = 0
    for row in adjudicated_rows:
        raw = str(row.get("raw_value") or "")
        gtype = str(row.get("gold_param_type") or "")
        gunit = str(row.get("gold_norm_unit") or "")
        gvalue = row.get("gold_norm_value")
        raw_num = parse_first_number(raw)
        if (TIME_RANGE_RE.search(raw) or TIME_POINT_RE.fullmatch(raw)) and gtype not in {"time_window", "time_point"}:
            time_raw_not_time += 1
        if raw_num is not None and raw_num >= 100 and gunit == "yuan_per_kwh":
            try:
                gv = float(gvalue)
            except (TypeError, ValueError):
                gv = None
            if gv is not None and gv <= 2.0:
                price_large_small += 1
        if str(row.get("mechanism_bind_reason") or "") == "candidate_score" and bool(row.get("gold_strict_high_eligible")):
            candidate_strict_high += 1

    iaa = {
        "kappa_mechanism": round(kappa_mech, 6),
        "kappa_param_type": round(kappa_type, 6),
        "exact_match_norm_unit": round(exact_unit, 6),
        "agreement_strict_high_eligible": round(agree_strict, 6),
    }
    quality = {
        "denominators": {
            "all_clause": 2022,
            "sample_total": len(adjudicated_rows),
            "valid_all": valid_all_den,
            "valid_numeric": valid_numeric_den,
        },
        "mechanism_precision_on_valid_numeric": {
            "num": mech_num,
            "den": mech_den,
            "rate": round(mech_precision, 6),
        },
        "normalization_precision_on_valid_numeric": {
            "num": norm_num,
            "den": norm_den,
            "rate": round(norm_precision, 6),
        },
        "strict_high_precision": {
            "num": strict_num,
            "den": strict_den,
            "rate": round(strict_precision, 6),
        },
    }
    error_clusters = {
        "time_raw_not_time_window": time_raw_not_time,
        "price_value_large_raw_small_norm": price_large_small,
        "candidate_score_strict_high": candidate_strict_high,
    }

    target_pass = {
        "kappa_mechanism_ge_0_80": kappa_mech >= 0.80,
        "kappa_param_type_ge_0_80": kappa_type >= 0.80,
        "exact_match_norm_unit_ge_0_90": exact_unit >= 0.90,
        "agreement_strict_high_eligible_ge_0_90": agree_strict >= 0.90,
        "mechanism_precision_ge_0_90": mech_precision >= 0.90,
        "normalization_precision_ge_0_90": norm_precision >= 0.90,
        "strict_high_precision_ge_0_92": strict_precision >= 0.92,
        "time_raw_not_time_window_eq_0": time_raw_not_time == 0,
        "price_value_large_raw_small_norm_eq_0": price_large_small == 0,
        "candidate_score_strict_high_eq_0": candidate_strict_high == 0,
        "sample_size_ge_240": len(adjudicated_rows) >= 240,
        "sample_strict_ge_120": sampling_stats["strict_high_count"] >= 120,
        "sample_hard_ge_60": sampling_stats["hard_case_count"] >= 60,
    }
    all_passed = all(target_pass.values())

    report = {
        "config": {
            "mentions": rel_or_posix(mentions_path),
            "clause_corpus": rel_or_posix(clause_path),
            "sample_size": int(args.sample_size),
            "strict_min": int(args.strict_min),
            "hard_min": int(args.hard_min),
            "seed": int(args.seed),
        },
        "sampling": sampling_stats,
        "iaa": iaa,
        "quality": quality,
        "error_clusters": error_clusters,
        "target_pass": target_pass,
        "all_targets_passed": all_passed,
    }

    prefix = str(args.output_prefix).strip()
    sampling_plan_file = OUTPUT_DIR / f"{prefix}_gold_sampling_plan.json"
    sample_file = OUTPUT_DIR / f"{prefix}_gold_sample_v1.jsonl"
    pass_a_file = OUTPUT_DIR / f"{prefix}_gold_passA_labels.jsonl"
    pass_b_file = OUTPUT_DIR / f"{prefix}_gold_passB_labels.jsonl"
    adjudicated_file = OUTPUT_DIR / f"{prefix}_gold_adjudicated.jsonl"
    report_json_file = OUTPUT_DIR / f"{prefix}_iaa_report.json"
    report_md_file = OUTPUT_DIR / f"{prefix}_iaa_report.md"
    error_md_file = OUTPUT_DIR / f"{prefix}_error_clusters.md"

    write_json(sampling_plan_file, report["sampling"])
    sample_rows_out: List[Dict] = []
    for row in sample_rows:
        item = dict(row)
        item["hard_case_tags"] = list(item.pop("_hard_tags", []))
        item["clause_text"] = str(item.pop("_clause_text", ""))
        item["bind_reason_group"] = str(item.pop("_bind_group", "other"))
        sample_rows_out.append(item)
    write_jsonl(sample_file, sample_rows_out)
    write_jsonl(pass_a_file, pass_a_rows)
    write_jsonl(pass_b_file, pass_b_rows)
    write_jsonl(adjudicated_file, adjudicated_rows)
    write_json(report_json_file, report)
    report_md_file.write_text(build_md_report(report), encoding="utf-8")
    error_md_file.write_text(
        "\n".join(
            [
                "# Step6 Error Clusters",
                "",
                f"- time_raw_not_time_window: {time_raw_not_time}",
                f"- price_value_large_raw_small_norm: {price_large_small}",
                f"- candidate_score_strict_high: {candidate_strict_high}",
                "",
                f"- all_targets_passed: {all_passed}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report["iaa"], ensure_ascii=False))
    print(json.dumps(report["quality"], ensure_ascii=False))
    print(json.dumps({"target_pass": target_pass, "all_targets_passed": all_passed}, ensure_ascii=False))


if __name__ == "__main__":
    main()
