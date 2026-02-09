import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "00_整理记录"


@dataclass(frozen=True)
class ThemeDef:
    key: str
    name_zh: str
    keywords: Tuple[str, ...]
    path_markers: Tuple[str, ...]


THEME_DEFS: Sequence[ThemeDef] = (
    ThemeDef(
        key="tou_pricing",
        name_zh="分时电价",
        keywords=("分时电价", "峰谷", "尖峰", "谷段", "平段", "时段电价"),
        path_markers=("01_电价政策/01_分时电价/",),
    ),
    ThemeDef(
        key="tiered_pricing",
        name_zh="阶梯电价",
        keywords=("阶梯电价", "第一档", "第二档", "第三档", "一户多人口"),
        path_markers=("01_电价政策/02_阶梯与差别电价/",),
    ),
    ThemeDef(
        key="differential_pricing",
        name_zh="差别电价",
        keywords=("差别电价", "惩罚性电价", "淘汰类", "限制类", "加价电价"),
        path_markers=("01_电价政策/02_阶梯与差别电价/",),
    ),
    ThemeDef(
        key="subsidy",
        name_zh="补贴补助",
        keywords=("补贴", "补助", "奖补", "奖励", "资金支持", "运行补贴"),
        path_markers=(
            "02_电能替代与清洁取暖/01_政策文本/",
            "01_电价政策/03_综合与其他/",
        ),
    ),
    ThemeDef(
        key="shore_power",
        name_zh="岸电",
        keywords=("岸电", "靠港", "船舶", "港口", "岸电系统"),
        path_markers=("02_电能替代与清洁取暖/01_政策文本/",),
    ),
    ThemeDef(
        key="clean_heating",
        name_zh="清洁取暖",
        keywords=("清洁取暖", "清洁供暖", "煤改电", "煤改气", "采暖季"),
        path_markers=("02_电能替代与清洁取暖/01_政策文本/",),
    ),
)


DATE_IN_NAME_RE = re.compile(r"(20\d{2})年")
NUMERIC_PARAMETER_RE = re.compile(r"\d+(?:\.\d+)?\s*(?:元|万元|%|千瓦时|吨|户|村|平方)")
ORG_RE = re.compile(
    r"国家发展改革委|发展和改革委员会|发展改革委|人民政府|国务院|国家能源局|交通运输部|财政部|工业和信息化部|生态环境部|电网有限公司"
)
DOC_NO_RE = re.compile(r"[\u4e00-\u9fa5A-Za-z]{0,10}〔\d{4}〕\d+号|〔\d{4}〕\d+号")
ISSUE_DATE_RE = re.compile(r"(20\d{2})年(\d{1,2})月(\d{1,2})日")
REGION_RE = re.compile(r"[\u4e00-\u9fa5]{2,10}(?:省|市|自治区|自治州|区)")
TARGET_RE = re.compile(
    r"居民用户|工商业用户|电动汽车|充电设施|港口企业|船舶|农村地区|供暖用户|高耗能企业|电解铝|钢铁|水泥"
)


def iter_policy_files() -> List[Path]:
    files: List[Path] = []
    for top_dir in sorted(PROJECT_ROOT.iterdir(), key=lambda p: p.name):
        if not top_dir.is_dir():
            continue
        if not re.match(r"^\d{2}_", top_dir.name):
            continue
        if top_dir.name.startswith("00_"):
            continue
        for file_path in top_dir.rglob("*.txt"):
            rel_parts = file_path.relative_to(PROJECT_ROOT).parts
            # Exclude compiled bundles and compressed package folder.
            if rel_parts[0].startswith("02_") and len(rel_parts) > 1 and rel_parts[1].startswith(("02_", "03_")):
                continue
            files.append(file_path)
    return sorted(files, key=lambda p: str(p))


def relative_path(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")


def read_text(path: Path) -> str:
    data = path.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("gb18030", errors="ignore")


def compact_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_year(file_name: str) -> Optional[int]:
    match = DATE_IN_NAME_RE.search(file_name)
    if not match:
        return None
    return int(match.group(1))


def count_keyword_hits(text: str, keywords: Iterable[str]) -> Tuple[int, List[str]]:
    hits = []
    total = 0
    for kw in keywords:
        c = text.count(kw)
        if c > 0:
            total += c
            hits.append(kw)
    return total, hits


def score_document_for_theme(theme: ThemeDef, title: str, text: str, rel: str) -> Tuple[int, Dict[str, object]]:
    title_hits_count, title_hits = count_keyword_hits(title, theme.keywords)
    body_hits_count, body_hits = count_keyword_hits(text[:5000], theme.keywords)
    path_hits_count, path_hits = count_keyword_hits(rel, theme.keywords)
    marker_hits = [m for m in theme.path_markers if m in rel]
    marker_score = len(marker_hits) * 8

    score = title_hits_count * 5 + body_hits_count * 2 + path_hits_count * 3 + marker_score
    detail = {
        "title_hits": title_hits,
        "body_hits": body_hits,
        "path_hits": path_hits,
        "path_marker_hits": marker_hits,
        "title_hits_count": title_hits_count,
        "body_hits_count": body_hits_count,
        "path_hits_count": path_hits_count,
        "path_marker_score": marker_score,
    }
    return score, detail


def sample_with_year_balance(candidates: List[Dict[str, object]], target_n: int) -> List[Dict[str, object]]:
    if len(candidates) <= target_n:
        return candidates

    picked: List[Dict[str, object]] = []
    used_paths = set()
    used_years = set()

    ranked = sorted(
        candidates,
        key=lambda x: (
            -int(x["score"]),
            -int(x.get("char_count") or 0),
            str(x["source_path"]),
        ),
    )
    top_score = int(ranked[0]["score"])
    min_score = max(6, int(top_score * 0.25))

    # Pass 1: one sample per year when possible.
    for row in ranked:
        if len(picked) >= target_n:
            break
        year = row.get("year")
        rel = row["source_path"]
        if rel in used_paths:
            continue
        if year is None or year in used_years:
            continue
        if int(row["score"]) < min_score:
            continue
        picked.append(row)
        used_paths.add(rel)
        used_years.add(year)

    # Pass 2: fill remaining by score.
    for row in ranked:
        if len(picked) >= target_n:
            break
        rel = row["source_path"]
        if rel in used_paths:
            continue
        if int(row["score"]) < min_score:
            continue
        picked.append(row)
        used_paths.add(rel)

    # Pass 3: if still not enough, allow low score fallback to keep sample size stable.
    for row in ranked:
        if len(picked) >= target_n:
            break
        rel = row["source_path"]
        if rel in used_paths:
            continue
        picked.append(row)
        used_paths.add(rel)

    return picked


def split_clauses(text: str) -> List[str]:
    parts = re.split(r"[。；;\n]", text)
    clauses = []
    for part in parts:
        c = compact_text(part)
        if len(c) < 20:
            continue
        if len(c) > 220:
            continue
        clauses.append(c)
    return clauses


def build_sampling(per_theme: int = 8) -> Dict[str, object]:
    files = iter_policy_files()
    doc_records: List[Dict[str, object]] = []
    by_theme_candidates: Dict[str, List[Dict[str, object]]] = {t.key: [] for t in THEME_DEFS}

    for path in files:
        rel = relative_path(path)
        title = path.stem
        raw_text = read_text(path)
        text = compact_text(raw_text)
        year = parse_year(path.name)
        char_count = len(text)

        doc_info = {
            "source_path": rel,
            "title": title,
            "year": year,
            "char_count": char_count,
            "theme_matches": {},
        }

        for theme in THEME_DEFS:
            score, detail = score_document_for_theme(theme, title, text, rel)
            if score <= 0:
                continue
            match_row = {
                "source_path": rel,
                "title": title,
                "year": year,
                "char_count": char_count,
                "score": score,
                "match_detail": detail,
            }
            doc_info["theme_matches"][theme.key] = {
                "score": score,
                "keywords": sorted(set(detail["title_hits"] + detail["body_hits"] + detail["path_hits"])),
            }
            by_theme_candidates[theme.key].append(match_row)

        doc_records.append(doc_info)

    theme_outputs = []
    union_map: Dict[str, Dict[str, object]] = {}
    for theme in THEME_DEFS:
        candidates = by_theme_candidates[theme.key]
        sampled = sample_with_year_balance(candidates, per_theme)
        sampled_rel_set = set()
        sampled_rows = []
        for row in sampled:
            rel = str(row["source_path"])
            sampled_rel_set.add(rel)
            sampled_rows.append(
                {
                    "source_path": rel,
                    "title": row["title"],
                    "year": row["year"],
                    "char_count": row["char_count"],
                    "score": row["score"],
                    "match_keywords": sorted(
                        set(
                            row["match_detail"]["title_hits"]
                            + row["match_detail"]["body_hits"]
                            + row["match_detail"]["path_hits"]
                        )
                    ),
                }
            )
            if rel not in union_map:
                union_map[rel] = {
                    "source_path": rel,
                    "title": row["title"],
                    "year": row["year"],
                    "char_count": row["char_count"],
                    "themes": [],
                }
            union_map[rel]["themes"].append(theme.key)

        theme_outputs.append(
            {
                "theme_key": theme.key,
                "theme_name_zh": theme.name_zh,
                "candidate_count": len(candidates),
                "sampled_count": len(sampled_rows),
                "sampled_docs": sampled_rows,
            }
        )

    union_rows = sorted(
        union_map.values(),
        key=lambda x: (
            x["year"] is None,
            x["year"] or 0,
            x["source_path"],
        ),
    )
    for row in union_rows:
        row["themes"] = sorted(set(row["themes"]))

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scope": {
            "total_policy_docs": len(files),
            "exclude_paths": [
                "02_电能替代与清洁取暖/02_汇总拼接/*.txt",
                "02_电能替代与清洁取暖/03_原始压缩包/*",
            ],
            "per_theme_target": per_theme,
            "themes_required": [t.name_zh for t in THEME_DEFS],
        },
        "theme_sampling": theme_outputs,
        "annotation_pool_union": {
            "doc_count": len(union_rows),
            "docs": union_rows,
        },
        "all_doc_theme_match_count": sum(1 for d in doc_records if d["theme_matches"]),
    }


def build_doccano_seed_doc_level(pool_docs: List[Dict[str, object]], max_docs: int = 48) -> List[Dict[str, object]]:
    rows = []
    for idx, doc in enumerate(pool_docs[:max_docs], 1):
        path = PROJECT_ROOT / doc["source_path"]
        text = compact_text(read_text(path))
        preview = text[:1500]
        entry_text = (
            f"【SOURCE_PATH】{doc['source_path']}\n"
            f"【TITLE】{doc['title']}\n"
            f"【THEMES】{','.join(doc['themes'])}\n"
            f"{preview}"
        )
        rows.append({"id": idx, "text": entry_text, "labels": []})
    return rows


def pick_clause_for_theme(clauses: List[str], theme_keywords: Sequence[str]) -> Optional[str]:
    ranked = []
    for clause in clauses:
        score = sum(clause.count(kw) for kw in theme_keywords)
        if score <= 0:
            continue
        numeric_bonus = 2 if NUMERIC_PARAMETER_RE.search(clause) else 0
        ranked.append((score + numeric_bonus, clause))
    if not ranked:
        return None
    ranked.sort(key=lambda x: (-x[0], x[1]))
    return ranked[0][1]


def build_doccano_seed_clause_level(pool_docs: List[Dict[str, object]], max_docs: int = 48) -> List[Dict[str, object]]:
    rows = []
    theme_map = {t.key: t for t in THEME_DEFS}
    record_id = 1
    for doc in pool_docs[:max_docs]:
        path = PROJECT_ROOT / doc["source_path"]
        text = read_text(path)
        clauses = split_clauses(text)
        for theme_key in doc["themes"]:
            theme_def = theme_map[theme_key]
            clause = pick_clause_for_theme(clauses, theme_def.keywords)
            if not clause:
                continue
            entry_text = (
                f"【SOURCE_PATH】{doc['source_path']}\n"
                f"【TITLE】{doc['title']}\n"
                f"【THEME】{theme_key}\n"
                f"{clause}"
            )
            rows.append({"id": record_id, "text": entry_text, "labels": []})
            record_id += 1
    return rows


def build_labeled_examples(pool_docs: List[Dict[str, object]], max_examples: int = 12) -> List[Dict[str, object]]:
    examples = []
    idx = 1
    for doc in pool_docs:
        if len(examples) >= max_examples:
            break
        path = PROJECT_ROOT / doc["source_path"]
        text = compact_text(read_text(path))
        preview = text[:500]
        entry_text = f"【TITLE】{doc['title']}\n{preview}"

        labels: List[List[object]] = []
        for regex, label_name in (
            (ISSUE_DATE_RE, "ISSUE_DATE"),
            (DOC_NO_RE, "DOCUMENT_NO"),
            (ORG_RE, "ISSUING_ORG"),
            (REGION_RE, "REGION"),
            (TARGET_RE, "TARGET_GROUP"),
        ):
            m = regex.search(entry_text)
            if m:
                labels.append([m.start(), m.end(), label_name])

        if len(labels) < 2:
            continue
        labels.sort(key=lambda x: (x[0], x[1]))
        examples.append({"id": idx, "text": entry_text, "labels": labels})
        idx += 1
    return examples


def write_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_sampling_markdown(path: Path, result: Dict[str, object]) -> None:
    lines = [
        "# Step2 样本文档抽样结果",
        "",
        f"- 生成时间: {result['generated_at']}",
        f"- 样本范围: {result['scope']['total_policy_docs']} 份政策文本（已排除汇总拼接与压缩包目录）",
        f"- 每主题目标样本: {result['scope']['per_theme_target']}",
        f"- 抽样后去重样本池: {result['annotation_pool_union']['doc_count']} 份",
        "",
        "## 主题抽样统计",
    ]
    for theme in result["theme_sampling"]:
        lines.append(
            f"- {theme['theme_name_zh']}（{theme['theme_key']}）: "
            f"候选 {theme['candidate_count']}，抽中 {theme['sampled_count']}"
        )
    lines.extend(
        [
            "",
            "## doccano 导入建议",
            "- 文档级导入文件: `00_整理记录/step2_doccano_seed_doc_level.jsonl`",
            "- 条款级导入文件: `00_整理记录/step2_doccano_seed_clause_level.jsonl`",
            "- 已标注示例文件: `00_整理记录/step2_doccano_labeled_examples.jsonl`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    result = build_sampling(per_theme=8)
    write_json(OUTPUT_DIR / "step2_theme_sampling.json", result)
    write_sampling_markdown(OUTPUT_DIR / "step2_theme_sampling.md", result)

    pool_docs = result["annotation_pool_union"]["docs"]
    doc_level_seed = build_doccano_seed_doc_level(pool_docs, max_docs=48)
    clause_level_seed = build_doccano_seed_clause_level(pool_docs, max_docs=48)
    labeled_examples = build_labeled_examples(pool_docs, max_examples=12)

    write_jsonl(OUTPUT_DIR / "step2_doccano_seed_doc_level.jsonl", doc_level_seed)
    write_jsonl(OUTPUT_DIR / "step2_doccano_seed_clause_level.jsonl", clause_level_seed)
    write_jsonl(OUTPUT_DIR / "step2_doccano_labeled_examples.jsonl", labeled_examples)

    print("step2 sampling artifacts generated")


if __name__ == "__main__":
    main()
