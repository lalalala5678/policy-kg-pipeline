import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "00_整理记录"


DOC_TYPE_RULES: List[Tuple[str, re.Pattern[str]]] = [
    ("notice", re.compile(r"\u901a\u77e5")),
    ("opinion", re.compile(r"\u610f\u89c1")),
    ("plan", re.compile(r"\u65b9\u6848|\u89c4\u5212|\u8ba1\u5212")),
    ("measure", re.compile(r"\u529e\u6cd5|\u7ec6\u5219|\u89c4\u5219")),
    ("program", re.compile(r"\u884c\u52a8\u65b9\u6848|\u5b9e\u65bd\u65b9\u6848")),
    ("announcement", re.compile(r"\u516c\u544a|\u901a\u544a")),
    ("guideline", re.compile(r"\u6307\u5357|\u5bfc\u5219")),
    ("reply_letter", re.compile(r"\u7b54\u590d|\u51fd")),
]


MECHANISM_PATTERNS_PROXY: Dict[str, re.Pattern[str]] = {
    "tou_pricing": re.compile(r"\u5cf0\u8c37|\u5206\u65f6\u7535\u4ef7|\u5c16\u5cf0|\u5e73\u6bb5|\u8c37\u6bb5"),
    "tiered_pricing": re.compile(r"\u9636\u68af\u7535\u4ef7|\u7b2c\u4e00\u6863|\u7b2c\u4e8c\u6863|\u7b2c\u4e09\u6863"),
    "differential_penalty_pricing": re.compile(r"\u5dee\u522b\u7535\u4ef7|\u60e9\u7f5a\u6027\u7535\u4ef7|\u6dd8\u6c70\u7c7b|\u9650\u5236\u7c7b"),
    "general_price_adjustment": re.compile(r"\u4e0b\u8c03\u7535\u4ef7|\u964d\u4f4e.*\u7535\u4ef7|\u964d\u4ef7|\u7535\u4ef7\u6539\u9769|\u8c03\u6574\u7535\u4ef7"),
    "subsidy": re.compile(r"\u8865\u8d34|\u8865\u52a9|\u5956\u52b1|\u5956\u8865|\u8865\u507f"),
    "task_assessment": re.compile(r"\u4efb\u52a1|\u76ee\u6807|\u8003\u6838|\u9a8c\u6536|\u63a8\u8fdb|\u8d23\u4efb\u5206\u5de5"),
    "technology_route": re.compile(r"\u7164\u6539\u7535|\u7535\u80fd\u66ff\u4ee3|\u5cb8\u7535|\u5145\u7535\u57fa\u7840\u8bbe\u65bd|\u6e05\u6d01\u53d6\u6696"),
}


MECHANISM_PATTERNS_SILVER: Dict[str, re.Pattern[str]] = {
    "tou_pricing": re.compile(r"\u5cf0\u8c37|\u5206\u65f6\u7535\u4ef7|\u5c16\u5cf0|\u5e73\u6bb5|\u8c37\u6bb5|\u65f6\u6bb5\u7535\u4ef7"),
    "tiered_pricing": re.compile(r"\u9636\u68af\u7535\u4ef7|\u7b2c\u4e00\u6863|\u7b2c\u4e8c\u6863|\u7b2c\u4e09\u6863|\u5206\u6863\u7535\u4ef7"),
    "differential_penalty_pricing": re.compile(r"\u5dee\u522b\u7535\u4ef7|\u60e9\u7f5a\u6027\u7535\u4ef7|\u6dd8\u6c70\u7c7b|\u9650\u5236\u7c7b|\u52a0\u4ef7"),
    "general_price_adjustment": re.compile(
        r"\u4e0b\u8c03\u7535\u4ef7|\u964d\u4f4e.*\u7535\u4ef7|\u964d\u4ef7|\u7535\u4ef7\u6539\u9769|\u5b8c\u5584\u7535\u4ef7\u653f\u7b56|\u4f18\u5316\u7535\u4ef7\u653f\u7b56|\u8c03\u6574\u7535\u4ef7"
    ),
    "subsidy": re.compile(r"\u8865\u8d34|\u8865\u52a9|\u5956\u52b1|\u5956\u8865|\u8865\u507f"),
    "task_assessment": re.compile(r"\u4efb\u52a1|\u76ee\u6807|\u8003\u6838|\u9a8c\u6536|\u63a8\u8fdb|\u8d23\u4efb\u5206\u5de5|\u5de5\u4f5c\u8981\u6c42"),
    "technology_route": re.compile(r"\u7164\u6539\u7535|\u7535\u80fd\u66ff\u4ee3|\u5cb8\u7535|\u5145\u7535\u57fa\u7840\u8bbe\u65bd|\u6e05\u6d01\u53d6\u6696|\u70ed\u6cf5"),
}


SUBJECT_PATTERNS: List[re.Pattern[str]] = [
    re.compile(
        r"\u56fd\u52a1\u9662|\u56fd\u5bb6\u53d1\u5c55\u6539\u9769\u59d4|\u53d1\u6539\u59d4|\u80fd\u6e90\u5c40|\u8d22\u653f\u90e8|\u4ea4\u901a\u8fd0\u8f93\u90e8|\u5404\u7ea7\u4eba\u6c11\u653f\u5e9c|\u5404\u5730\u653f\u5e9c|\u5404\u90e8\u95e8|\u4ef7\u683c\u4e3b\u7ba1\u90e8\u95e8|\u4f9b\u7535\u516c\u53f8|\u7535\u7f51\u4f01\u4e1a|\u76f8\u5173\u5355\u4f4d"
    ),
]


ACTION_KEYWORDS: List[str] = [
    "\u63a8\u8fdb",
    "\u7ec4\u7ec7",
    "\u843d\u5b9e",
    "\u5236\u5b9a",
    "\u5b8c\u5584",
    "\u5efa\u7acb",
    "\u5b9e\u65bd",
    "\u6267\u884c",
    "\u5f00\u5c55",
    "\u52a0\u5f3a",
    "\u5b8c\u6210",
    "\u52a0\u5feb",
    "\u63a8\u52a8",
    "\u4e25\u683c",
    "\u53d6\u6d88",
    "\u4f18\u5316",
]


ASSESSMENT_PATTERN = re.compile(r"[^。；;]{0,20}(\u8003\u6838|\u9a8c\u6536|\u7763\u5bfc|\u76d1\u7763|\u8bc4\u4f30|\u901a\u62a5)[^。；;]{0,20}")
DEADLINE_PATTERN = re.compile(
    r"\d{4}\u5e74\d{1,2}\u6708\d{1,2}\u65e5\u524d|\d{4}\u5e74\u5e95\u524d|\u5230\d{4}\u5e74|\d{4}\u2014\d{4}\u5e74|\d{4}-\d{4}\u5e74|\d{4}\u5e74"
)


DOCUMENT_NO_PATTERN = re.compile(r"[\u4e00-\u9fa5A-Za-z]{0,10}\u3014\d{4}\u3015\d+\u53f7|\u3014\d{4}\u3015\d+\u53f7")
DATE_PATTERN = re.compile(r"(\d{4})\u5e74(\d{1,2})\u6708(\d{1,2})\u65e5")


def iter_policy_files() -> List[Path]:
    files = []
    for top in ("01_电价政策", "02_电能替代与清洁取暖"):
        root = PROJECT_ROOT / top
        for f in root.rglob("*.txt"):
            files.append(f)
    return sorted(files, key=lambda p: str(p))


def relative_path(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")


def read_policy_text(path: Path) -> str:
    data = path.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("gb18030", errors="ignore")


def normalize_date_token(date_token: str) -> str:
    m = DATE_PATTERN.search(date_token)
    if not m:
        return date_token
    y, mo, d = m.groups()
    return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"


def classify_doc_type(text: str) -> Optional[str]:
    for doc_type, rule in DOC_TYPE_RULES:
        if rule.search(text):
            return doc_type
    return None


def extract_document_meta_from_text(text: str) -> Dict[str, Optional[str]]:
    first_800 = text[:800]
    issue_date = None
    m_date = DATE_PATTERN.search(text)
    if m_date:
        issue_date = normalize_date_token(m_date.group(0))

    doc_type = classify_doc_type(first_800)
    doc_no = None
    m_doc_no = DOCUMENT_NO_PATTERN.search(text[:12000])
    if m_doc_no:
        doc_no = m_doc_no.group(0)
    return {"issue_date": issue_date, "doc_type": doc_type, "document_no": doc_no}


def extract_document_meta_from_filename(file_name: str) -> Dict[str, Optional[str]]:
    stem = Path(file_name).stem
    issue_date = None
    m_date = DATE_PATTERN.search(stem)
    if m_date:
        issue_date = normalize_date_token(m_date.group(0))
    doc_type = classify_doc_type(stem)
    doc_no = None
    m_doc_no = DOCUMENT_NO_PATTERN.search(stem)
    if m_doc_no:
        doc_no = m_doc_no.group(0)
    return {"issue_date": issue_date, "doc_type": doc_type, "document_no": doc_no}


def arbitrate_field(
    field: str,
    body_value: Optional[str],
    filename_value: Optional[str],
) -> Dict[str, Optional[str]]:
    result = {
        "value": None,
        "source": None,
        "conflict": False,
        "body_value": body_value,
        "filename_value": filename_value,
    }
    if body_value and filename_value:
        if body_value == filename_value:
            result["value"] = body_value
            result["source"] = "body_primary"
            return result
        result["value"] = body_value
        result["source"] = "body_primary_conflict_filename"
        result["conflict"] = True
        return result
    if body_value:
        result["value"] = body_value
        result["source"] = "body_primary"
        return result
    if filename_value:
        result["value"] = filename_value
        result["source"] = "filename_compensation"
        return result
    result["source"] = "missing"
    return result


def build_doc_meta_with_compensation(files: Iterable[Path]) -> Tuple[List[Dict], Dict]:
    rows: List[Dict] = []
    before = {"issue_date": 0, "doc_type": 0, "document_no": 0}
    after = {"issue_date": 0, "doc_type": 0, "document_no": 0}
    compensated = {"issue_date": 0, "doc_type": 0, "document_no": 0}
    conflicts = {"issue_date": 0, "doc_type": 0, "document_no": 0}

    files = list(files)
    for p in files:
        text = read_policy_text(p)
        body = extract_document_meta_from_text(text)
        name = extract_document_meta_from_filename(p.name)
        item = {"source_path": relative_path(p), "fields": {}}

        for field in ("issue_date", "doc_type", "document_no"):
            if body[field]:
                before[field] += 1
            merged = arbitrate_field(field, body[field], name[field])
            if merged["value"]:
                after[field] += 1
            if merged["source"] == "filename_compensation":
                compensated[field] += 1
            if merged["conflict"]:
                conflicts[field] += 1
            item["fields"][field] = merged

        rows.append(item)

    total = max(1, len(files))
    summary = {
        "total_docs": len(files),
        "before_coverage": before,
        "after_coverage": after,
        "before_coverage_rate": {k: round(before[k] * 100.0 / total, 2) for k in before},
        "after_coverage_rate": {k: round(after[k] * 100.0 / total, 2) for k in after},
        "filename_compensation_count": compensated,
        "conflict_count": conflicts,
    }
    return rows, summary


def segment_clauses(text: str) -> List[str]:
    text = text.replace("\r\n", "\n")
    pieces = re.split(r"[；。]", text)
    clauses = []
    for raw in pieces:
        c = raw.strip()
        if not c:
            continue
        clauses.append(c)
    return clauses


def extract_task_fields(clause_text: str) -> Dict[str, object]:
    subject = None
    for p in SUBJECT_PATTERNS:
        m = p.search(clause_text)
        if m:
            subject = m.group(0)
            break
    if not subject:
        m = re.search(r"^\s*([\u4e00-\u9fa5]{2,18})(?=要|应|须|需|负责|开展|推进|落实|完善|建立|执行)", clause_text)
        if m:
            subject = m.group(1)

    actions: List[str] = []
    for a in ACTION_KEYWORDS:
        if a in clause_text and a not in actions:
            actions.append(a)

    deadline = None
    m_deadline = DEADLINE_PATTERN.search(clause_text)
    if m_deadline:
        deadline = m_deadline.group(0)

    assessment = None
    m_assess = ASSESSMENT_PATTERN.search(clause_text)
    if m_assess:
        assessment = m_assess.group(0)

    return {
        "task_subject": subject,
        "task_action": actions,
        "task_deadline": deadline,
        "task_assessment": assessment,
    }


def is_task_clause(clause_text: str) -> bool:
    return bool(
        re.search(r"\u4efb\u52a1|\u76ee\u6807|\u8003\u6838|\u9a8c\u6536|\u63a8\u8fdb|\u8d23\u4efb\u5206\u5de5|\u5de5\u4f5c\u8981\u6c42", clause_text)
    )


def build_task_clause_records(files: Iterable[Path]) -> Tuple[List[Dict], Dict]:
    files = list(files)
    records: List[Dict] = []
    total_clauses = 0
    task_clauses = 0
    with_subject = 0
    with_action = 0
    with_deadline = 0
    with_assessment = 0
    docs_with_task = set()

    for p in files:
        text = read_policy_text(p)
        rel = relative_path(p)
        clauses = segment_clauses(text)
        total_clauses += len(clauses)
        for idx, clause in enumerate(clauses):
            if not is_task_clause(clause):
                continue
            task_clauses += 1
            docs_with_task.add(rel)
            fields = extract_task_fields(clause)
            if fields["task_subject"]:
                with_subject += 1
            if fields["task_action"]:
                with_action += 1
            if fields["task_deadline"]:
                with_deadline += 1
            if fields["task_assessment"]:
                with_assessment += 1
            records.append(
                {
                    "source_path": rel,
                    "clause_id": f"{rel}#clause_{idx}",
                    "clause_text": clause,
                    **fields,
                }
            )

    denom = max(1, task_clauses)
    summary = {
        "total_docs": len(files),
        "total_clauses": total_clauses,
        "task_clauses": task_clauses,
        "docs_with_task_clause": len(docs_with_task),
        "task_field_coverage": {
            "task_subject": round(with_subject * 100.0 / denom, 2),
            "task_action": round(with_action * 100.0 / denom, 2),
            "task_deadline": round(with_deadline * 100.0 / denom, 2),
            "task_assessment": round(with_assessment * 100.0 / denom, 2),
        },
    }
    return records, summary


def predict_mechanisms(text: str, patterns: Dict[str, re.Pattern[str]]) -> Set[str]:
    preds = set()
    for mech, pat in patterns.items():
        if pat.search(text):
            preds.add(mech)
    return preds


def load_no_parameter_top25() -> List[str]:
    fit_json = OUTPUT_DIR / "schema_v1_4_fit_check.json"
    if not fit_json.exists():
        return []
    data = json.loads(fit_json.read_text(encoding="utf-8-sig"))
    items = data.get("risk_samples", {}).get("no_parameter_top25", [])
    return list(items)[:25]


def build_priority3_annotation_set(no_parameter_paths: List[str]) -> List[Dict]:
    ann = []
    for rel in no_parameter_paths:
        path = PROJECT_ROOT / rel.replace("\\", "/")
        if not path.exists():
            continue
        text = read_policy_text(path)
        ann.append(
            {
                "source_path": rel.replace("\\", "/"),
                "title": path.stem,
                "text_preview": text[:1200],
                "silver_expected_mechanisms": sorted(predict_mechanisms(path.stem + "\n" + text, MECHANISM_PATTERNS_SILVER)),
            }
        )
    return ann


def evaluate_weak_value_set(annotation_set: List[Dict]) -> Dict:
    doc_tp = 0
    doc_fp = 0
    doc_fn = 0
    doc_exact_match = 0
    per_doc = []
    for item in annotation_set:
        text = item["title"] + "\n" + item.get("text_preview", "")
        pred = predict_mechanisms(text, MECHANISM_PATTERNS_PROXY)
        gold = set(item.get("silver_expected_mechanisms", []))
        tp = len(pred & gold)
        fp = len(pred - gold)
        fn = len(gold - pred)
        doc_tp += tp
        doc_fp += fp
        doc_fn += fn
        if pred == gold:
            doc_exact_match += 1
        per_doc.append(
            {
                "source_path": item["source_path"],
                "gold": sorted(gold),
                "pred": sorted(pred),
                "tp": tp,
                "fp": fp,
                "fn": fn,
            }
        )
    precision = doc_tp / (doc_tp + doc_fp) if (doc_tp + doc_fp) > 0 else 0.0
    recall = doc_tp / (doc_tp + doc_fn) if (doc_tp + doc_fn) > 0 else 0.0
    fp_rate = doc_fp / max(1, doc_tp + doc_fp)
    summary = {
        "evaluation_mode": "uie_proxy_keyword_baseline",
        "doc_count": len(annotation_set),
        "micro_precision": round(precision, 4),
        "micro_recall": round(recall, 4),
        "false_positive_rate": round(fp_rate, 4),
        "doc_exact_match_rate": round(doc_exact_match * 1.0 / max(1, len(annotation_set)), 4),
        "details": per_doc,
    }
    return summary


CN_NUM_DIGITS: Dict[str, int] = {
    "\u96f6": 0,
    "\u3007": 0,
    "\u4e00": 1,
    "\u4e8c": 2,
    "\u4e24": 2,
    "\u4e09": 3,
    "\u56db": 4,
    "\u4e94": 5,
    "\u516d": 6,
    "\u4e03": 7,
    "\u516b": 8,
    "\u4e5d": 9,
    "\u58f9": 1,
    "\u8d30": 2,
    "\u53c1": 3,
    "\u8086": 4,
    "\u4f0d": 5,
    "\u9646": 6,
    "\u67d2": 7,
    "\u634c": 8,
    "\u7396": 9,
}

CN_NUM_SMALL_UNITS: Dict[str, int] = {"\u5341": 10, "\u767e": 100, "\u5343": 1000}
CN_NUM_LARGE_UNITS: Dict[str, int] = {"\u4e07": 10000, "\u4ebf": 100000000}

CN_NUM_BODY = "\u96f6\u3007\u4e00\u4e8c\u4e24\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e\u5343\u4e07\u4ebf\u58f9\u8d30\u53c1\u8086\u4f0d\u9646\u67d2\u634c\u7396\u70b9"
DATE_LIKE_VALUE_RE = re.compile(r"^(?:19|20)\d{2}(?:[-/\.年]\d{1,2}){1,2}(?:\u65e5)?$")
YEAR_ONLY_RE = re.compile(r"^(?:19|20)\d{2}$")
ARTICLE_NO_RE = re.compile(r"^\s*\u7b2c[\u4e00-\u9fa5\d]+\s*[\u6761\u6b3e\u9879]\s*$")
TIME_WINDOW_VALUE_RE = re.compile(
    r"(?P<start>[0-2]?\d[:\uFF1A][0-5]\d)\s*[-~\u81f3\u5230]\s*(?P<end>[0-2]?\d[:\uFF1A][0-5]\d)"
)
RATIO_VALUE_RE = re.compile(r"(?P<value>\d+(?:\.\d+)?\s*:\s*\d+(?:\.\d+)?(?:\s*:\s*\d+(?:\.\d+)?)?)")
SUBSIDY_CUES_RE = re.compile(r"\u8865\u8d34|\u8865\u52a9|\u5956\u52b1|\u5956\u8865|\u8d44\u52a9|\u8865\u507f")
PRICE_CUES_RE = re.compile(r"\u7535\u4ef7|\u4ef7\u5dee|\u5206\u65f6|\u5cf0\u8c37|\u4e0a\u6d6e|\u4e0b\u6d6e|\u52a0\u4ef7|\u964d\u4ef7")
THRESHOLD_CUES_RE = re.compile(
    r"\u4e0d\u8d85\u8fc7|\u4e0d\u9ad8\u4e8e|\u4e0d\u4f4e\u4e8e|\u4e0d\u5c11\u4e8e|\u4ee5\u4e0a|\u4ee5\u4e0b|\u4ee5\u5185|\u81f3\u5c11|\u6700\u9ad8|\u6700\u4f4e|\u8fbe\u5230|\u8d85\u8fc7"
)
PREFIX_FILTER_RE = re.compile(
    r"^\s*(?:\u4e0d\u8d85\u8fc7|\u4e0d\u9ad8\u4e8e|\u4e0d\u4f4e\u4e8e|\u4e0d\u5c11\u4e8e|\u4e0d\u5f97\u4f4e\u4e8e|\u4ee5\u4e0a|\u4ee5\u4e0b|\u4ee5\u5185|\u81f3\u5c11|\u6700\u9ad8|\u6700\u4f4e|\u7ea6|\u5927\u7ea6|\u7ea6\u4e3a|\u8fbe\u5230)\s*"
)


def _normalize_time_token(value: str) -> str:
    if not value:
        return value
    parts = value.replace("\uFF1A", ":").split(":")
    if len(parts) != 2:
        return value.replace("\uFF1A", ":")
    hh = f"{int(parts[0]):02d}"
    mm = f"{int(parts[1]):02d}"
    return f"{hh}:{mm}"


def _parse_cn_integer(token: str) -> Optional[int]:
    if not token:
        return None
    total = 0
    section = 0
    number = 0
    has_known = False
    for ch in token:
        if ch in CN_NUM_DIGITS:
            number = CN_NUM_DIGITS[ch]
            has_known = True
            continue
        if ch in CN_NUM_SMALL_UNITS:
            unit = CN_NUM_SMALL_UNITS[ch]
            if number == 0:
                number = 1
            section += number * unit
            number = 0
            has_known = True
            continue
        if ch in CN_NUM_LARGE_UNITS:
            unit = CN_NUM_LARGE_UNITS[ch]
            section += number
            if section == 0:
                section = 1
            total += section * unit
            section = 0
            number = 0
            has_known = True
            continue
        if ch.isspace():
            continue
        return None
    if not has_known:
        return None
    return total + section + number


def _parse_number_token(token: str) -> Optional[float]:
    if token is None:
        return None
    cleaned = token.strip().replace(",", "").replace("\uff0c", "")
    cleaned = PREFIX_FILTER_RE.sub("", cleaned)
    if not cleaned:
        return None
    if cleaned.startswith("\u767e\u5206\u4e4b"):
        pct_raw = cleaned[len("\u767e\u5206\u4e4b") :]
        pct_val = _parse_number_token(pct_raw)
        return pct_val
    if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", cleaned):
        return float(cleaned)
    if "\u70b9" in cleaned:
        int_part, frac_part = cleaned.split("\u70b9", 1)
        int_val = _parse_cn_integer(int_part) if int_part else 0
        if int_val is None:
            return None
        frac_digits: List[str] = []
        for ch in frac_part:
            if ch in CN_NUM_DIGITS:
                frac_digits.append(str(CN_NUM_DIGITS[ch]))
                continue
            if ch.isspace():
                continue
            return None
        if not frac_digits:
            return float(int_val)
        return float(f"{int_val}.{''.join(frac_digits)}")
    int_val = _parse_cn_integer(cleaned)
    return float(int_val) if int_val is not None else None


def _base_normalize_result(rule: str) -> Dict[str, object]:
    return {
        "matched": True,
        "rule": rule,
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


def _base_unmatched_result(rule: str) -> Dict[str, object]:
    return {
        "matched": False,
        "rule": rule,
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


def _pick_search_space(raw_no_space: str, merged_no_space: str) -> Tuple[str, str]:
    # Prefer the extracted mention text itself to avoid context leakage.
    # Context is only used for cue disambiguation or rare fallback.
    return raw_no_space, merged_no_space


def normalize_parameter(raw_text: str, context_text: str = "") -> Dict[str, object]:
    raw = (raw_text or "").strip()
    context = (context_text or "").strip()
    raw_no_space = re.sub(r"\s+", "", raw)
    merged = f"{raw} {context}".strip()
    merged_no_space = re.sub(r"\s+", "", merged)
    primary_space, fallback_space = _pick_search_space(raw_no_space, merged_no_space)

    if not raw:
        return _base_unmatched_result("empty_value")
    if DATE_LIKE_VALUE_RE.fullmatch(raw):
        return _base_unmatched_result("date_like_filtered")
    if YEAR_ONLY_RE.fullmatch(raw):
        return _base_unmatched_result("year_like_filtered")
    if ARTICLE_NO_RE.fullmatch(raw):
        return _base_unmatched_result("article_no_filtered")

    m = TIME_WINDOW_VALUE_RE.search(primary_space)
    if m:
        start = _normalize_time_token(m.group("start"))
        end = _normalize_time_token(m.group("end"))
        out = _base_normalize_result("time_window")
        out["param_type"] = "time_window"
        out["norm_value"] = f"{start}-{end}"
        out["norm_unit"] = "time_window"
        out["norm_start"] = start
        out["norm_end"] = end
        out["op"] = "between"
        return out

    for text in (primary_space, fallback_space):
        m = re.search(r"(?P<value>\d+(?:\.\d+)?)\s*\u5143/\u5ea6", text)
        if m:
            out = _base_normalize_result("yuan_per_degree_to_yuan_per_kwh")
            out["param_type"] = "price_value"
            out["norm_value"] = float(m.group("value"))
            out["norm_unit"] = "yuan_per_kwh"
            return out

        m = re.search(r"(?P<value>\d+(?:\.\d+)?)\s*\u5206/\u5343\u74e6\u65f6", text)
        if m:
            out = _base_normalize_result("fen_per_kwh_to_yuan_per_kwh")
            out["param_type"] = "price_value"
            out["norm_value"] = float(m.group("value")) / 100.0
            out["norm_unit"] = "yuan_per_kwh"
            return out

        m = re.search(r"(?P<value>\d+(?:\.\d+)?)\s*\u5143/\u5343\u74e6\u65f6", text)
        if m:
            out = _base_normalize_result("yuan_per_kwh")
            out["param_type"] = "price_value"
            out["norm_value"] = float(m.group("value"))
            out["norm_unit"] = "yuan_per_kwh"
            return out

        m = re.search(r"(?P<value>\d+(?:\.\d+)?)\s*\u4e07\u5143/\u6751", text)
        if m:
            out = _base_normalize_result("ten_thousand_yuan_per_village")
            out["param_type"] = "subsidy_amount"
            out["norm_value"] = float(m.group("value"))
            out["norm_unit"] = "ten_thousand_yuan"
            out["scope_unit"] = "village"
            return out

        m = re.search(r"(?P<value>\d+(?:\.\d+)?)\s*\u5143/(?:\u5e73\u65b9\u7c73|\u33a1|m2|M2)", text)
        if m:
            out = _base_normalize_result("yuan_per_sqm")
            out["param_type"] = "area_subsidy_amount"
            out["norm_value"] = float(m.group("value"))
            out["norm_unit"] = "yuan_per_sqm"
            return out

        m = re.search(r"(?P<value>\d+(?:\.\d+)?)\s*\u5143/\u74e6", text)
        if m:
            out = _base_normalize_result("yuan_per_watt")
            out["param_type"] = "subsidy_amount"
            out["norm_value"] = float(m.group("value"))
            out["norm_unit"] = "yuan_per_watt"
            return out

        m = re.search(r"(?P<value>\d+(?:\.\d+)?)\s*\u5143/(?:\u603b\u5428|\u5428)", text)
        if m:
            out = _base_normalize_result("yuan_per_ton")
            out["param_type"] = "subsidy_amount"
            out["norm_value"] = float(m.group("value"))
            out["norm_unit"] = "yuan_per_ton"
            return out

    m = re.search(r"(?P<value>\d+(?:\.\d+)?)\s*[%\uFF05]", primary_space)
    if m:
        out = _base_normalize_result("percent_numeric")
        out["param_type"] = "price_delta_pct" if PRICE_CUES_RE.search(merged) else "ratio_target"
        out["norm_value"] = float(m.group("value"))
        out["norm_unit"] = "percent"
        return out

    m = re.search(r"\u767e\u5206\u4e4b(?P<value>[" + CN_NUM_BODY + r"\d\.]+)", primary_space)
    if m:
        pct = _parse_number_token(m.group("value"))
        if pct is not None:
            out = _base_normalize_result("percent_chinese")
            out["param_type"] = "price_delta_pct" if PRICE_CUES_RE.search(merged) else "ratio_target"
            out["norm_value"] = pct
            out["norm_unit"] = "percent"
            return out

    m = RATIO_VALUE_RE.search(primary_space)
    if m:
        out = _base_normalize_result("ratio_sequence")
        out["param_type"] = "ratio_target"
        out["norm_value"] = m.group("value").replace(" ", "")
        out["norm_unit"] = "none"
        return out

    m = re.search(
        r"(?P<start>[0-9]+(?:\.[0-9]+)?|[" + CN_NUM_BODY + r"]+)\s*[-~\u81f3\u5230]\s*(?P<end>[0-9]+(?:\.[0-9]+)?|[" + CN_NUM_BODY + r"]+)\s*(?P<unit>\u5343\u74e6\u65f6|kWh|KWH|kwh|\u5ea6)",
        primary_space,
    )
    if m:
        start_val = _parse_number_token(m.group("start"))
        end_val = _parse_number_token(m.group("end"))
        if start_val is not None and end_val is not None:
            out = _base_normalize_result("kwh_threshold_range")
            out["param_type"] = "consumption_threshold_kwh"
            out["norm_value"] = float(end_val)
            out["norm_unit"] = "kwh"
            out["range_start"] = float(start_val)
            out["range_end"] = float(end_val)
            out["op"] = "between"
            return out

    m = re.search(
        r"(?P<value>[0-9]+(?:\.[0-9]+)?|[" + CN_NUM_BODY + r"]+)\s*(?P<unit>\u4e07\u5343\u74e6|\u5146\u74e6|MW|mw|\u5343\u74e6(?!\u65f6)|kW|kw|W|w|\u5343\u4f0f\u5b89|kVA|kva)",
        primary_space,
    )
    if m:
        val = _parse_number_token(m.group("value"))
        if val is not None:
            unit_raw = m.group("unit")
            unit_lower = unit_raw.lower()
            if unit_raw == "\u4e07\u5343\u74e6":
                val = val * 10.0
                norm_unit = "mw"
            elif unit_raw == "\u5146\u74e6" or unit_lower == "mw":
                norm_unit = "mw"
            elif unit_raw == "\u5343\u74e6" or unit_lower == "kw":
                norm_unit = "kw"
            elif unit_lower == "w":
                val = val / 1000.0
                norm_unit = "kw"
            else:
                norm_unit = "kva"
            out = _base_normalize_result("capacity_value")
            out["param_type"] = "capacity_threshold" if THRESHOLD_CUES_RE.search(merged) else "other"
            out["norm_value"] = val
            out["norm_unit"] = norm_unit
            return out

    m = re.search(r"(?P<value>[0-9]+(?:\.[0-9]+)?|[" + CN_NUM_BODY + r"]+)\s*(?P<unit>\u5c0f\u65f6|\u65f6)", primary_space)
    if m:
        val = _parse_number_token(m.group("value"))
        if val is not None:
            out = _base_normalize_result("duration_hour")
            out["param_type"] = "duration_threshold_hour"
            out["norm_value"] = val
            out["norm_unit"] = "hour"
            out["op"] = "threshold" if THRESHOLD_CUES_RE.search(merged) else None
            return out

    m = re.search(r"(?P<value>[0-9]+(?:\.[0-9]+)?|[" + CN_NUM_BODY + r"]+)\s*(?P<unit>\u6237)", primary_space)
    if m:
        val = _parse_number_token(m.group("value"))
        if val is not None:
            out = _base_normalize_result("household_count")
            out["param_type"] = "target_household_count"
            out["norm_value"] = val
            out["norm_unit"] = "household"
            out["op"] = "threshold" if THRESHOLD_CUES_RE.search(merged) else None
            return out

    m = re.search(
        r"(?P<value>[0-9]+(?:\.[0-9]+)?|[" + CN_NUM_BODY + r"]+)\s*(?P<unit>\u4e07\u5428\u7ea7|\u4e07\u5428|\u5428\u7ea7|\u84b8\u5428/\u65f6|\u84b8\u5428|\u8f7d\u91cd\u5428|\u603b\u5428|\u5428)",
        primary_space,
    )
    if m:
        val = _parse_number_token(m.group("value"))
        if val is not None:
            unit_raw = m.group("unit")
            if unit_raw in ("\u4e07\u5428\u7ea7", "\u4e07\u5428"):
                val = val * 10000.0
                norm_unit = "ton"
            elif unit_raw == "\u84b8\u5428/\u65f6":
                norm_unit = "ton_per_hour"
            elif unit_raw in ("\u8f7d\u91cd\u5428", "\u603b\u5428"):
                norm_unit = "deadweight_ton"
            else:
                norm_unit = "ton"
            out = _base_normalize_result("tonnage_class_threshold" if "\u5428\u7ea7" in unit_raw else "tonnage_value")
            out["param_type"] = "tonnage_threshold"
            out["norm_value"] = val
            out["norm_unit"] = norm_unit
            return out

    m = re.search(
        r"(?P<value>[0-9]+(?:\.[0-9]+)?|[" + CN_NUM_BODY + r"]+)\s*(?P<unit>\u5343\u74e6\u65f6|kWh|KWH|kwh|\u5ea6)",
        primary_space,
    )
    if m:
        val = _parse_number_token(m.group("value"))
        if val is not None:
            out = _base_normalize_result("kwh_threshold")
            out["param_type"] = "consumption_threshold_kwh"
            out["norm_value"] = val
            out["norm_unit"] = "kwh"
            if THRESHOLD_CUES_RE.search(merged):
                out["op"] = "threshold"
            return out

    m = re.search(r"(?P<value>\d+(?:\.\d+)?)\s*\u4e07\u5143", primary_space)
    if m:
        out = _base_normalize_result("ten_thousand_yuan_generic")
        out["param_type"] = "subsidy_amount"
        out["norm_value"] = float(m.group("value"))
        out["norm_unit"] = "ten_thousand_yuan"
        return out

    m = re.search(r"(?P<value>\d+(?:\.\d+)?)\s*\u5143", primary_space)
    if m:
        out = _base_normalize_result("yuan_generic")
        if PRICE_CUES_RE.search(merged):
            out["param_type"] = "price_value"
        elif SUBSIDY_CUES_RE.search(merged):
            out["param_type"] = "subsidy_amount"
        else:
            out["param_type"] = "subsidy_amount"
        out["norm_value"] = float(m.group("value"))
        out["norm_unit"] = "yuan"
        return out

    m = re.search(
        r"(?:(?:\u4e0d\u5c11\u4e8e|\u4e0d\u4f4e\u4e8e|\u4e0d\u8d85\u8fc7|\u81f3\u5c11)\s*)?(?P<value>[0-9]+(?:\.[0-9]+)?|[" + CN_NUM_BODY + r"]+)\s*(?P<unit>\u4e2a\u6708|\u6708)",
        primary_space,
    )
    if m:
        val = _parse_number_token(m.group("value"))
        if val is not None:
            out = _base_normalize_result("duration_month")
            out["param_type"] = "duration_threshold_month"
            out["norm_value"] = val
            out["norm_unit"] = "month"
            out["op"] = "threshold"
            return out

    m = re.search(r"(?:(?:\u4e0d\u5c11\u4e8e|\u4e0d\u4f4e\u4e8e|\u4e0d\u8d85\u8fc7|\u81f3\u5c11)\s*)?(?P<value>[" + CN_NUM_BODY + r"\d\.]+)$", primary_space)
    if m and re.search(r"\u6708|\u5e74|\u91c7\u6696\u5b63", merged):
        val = _parse_number_token(m.group("value"))
        if val is not None:
            out = _base_normalize_result("duration_month_context")
            out["param_type"] = "duration_threshold_month"
            out["norm_value"] = val
            out["norm_unit"] = "month"
            out["op"] = "threshold"
            return out

    return _base_unmatched_result("no_match")
