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


def normalize_parameter(raw_text: str, context_text: str = "") -> Dict[str, object]:
    merged = f"{raw_text} {context_text}".strip()

    # Priority 1: yuan/degree must normalize before generic yuan.
    m = re.search(r"(?P<value>\d+(?:\.\d+)?)\s*\u5143/\u5ea6", merged)
    if m:
        return {
            "matched": True,
            "rule": "yuan_per_degree_to_yuan_per_kwh",
            "param_type": "price_value",
            "norm_value": float(m.group("value")),
            "norm_unit": "yuan_per_kwh",
        }

    # Priority 2: ten-thousand yuan per village should be captured before plain ten-thousand yuan.
    m = re.search(r"(?P<value>\d+(?:\.\d+)?)\s*\u4e07\u5143/\u6751", merged)
    if m:
        return {
            "matched": True,
            "rule": "ten_thousand_yuan_per_village",
            "param_type": "subsidy_amount",
            "norm_value": float(m.group("value")),
            "norm_unit": "ten_thousand_yuan",
            "scope_unit": "village",
        }

    # Priority 3: tonnage class must be treated as tonnage threshold.
    m = re.search(r"(?P<value>\d+(?:\.\d+)?)\s*\u4e07?\u5428\u7ea7", merged)
    if m:
        value = float(m.group("value"))
        if "\u4e07\u5428\u7ea7" in merged:
            value = value * 10000.0
        return {
            "matched": True,
            "rule": "tonnage_class_threshold",
            "param_type": "tonnage_threshold",
            "norm_value": value,
            "norm_unit": "ton",
        }

    m = re.search(r"(?P<value>\d+(?:\.\d+)?)\s*\u4e07\u5143", merged)
    if m:
        return {
            "matched": True,
            "rule": "ten_thousand_yuan_generic",
            "param_type": "subsidy_amount",
            "norm_value": float(m.group("value")),
            "norm_unit": "ten_thousand_yuan",
        }

    m = re.search(r"(?P<value>\d+(?:\.\d+)?)\s*\u5143", merged)
    if m:
        return {
            "matched": True,
            "rule": "yuan_generic",
            "param_type": "subsidy_amount",
            "norm_value": float(m.group("value")),
            "norm_unit": "yuan",
        }

    return {
        "matched": False,
        "rule": "no_match",
        "param_type": None,
        "norm_value": None,
        "norm_unit": None,
    }
