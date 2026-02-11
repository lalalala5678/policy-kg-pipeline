from __future__ import annotations

import json
import re
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, TypedDict

from langgraph.graph import END, START, StateGraph
from neo4j import GraphDatabase
from neo4j_graphrag.exceptions import Text2CypherRetrievalError
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.retrievers.text2cypher import Text2CypherRetriever


class QueryStep(TypedDict):
    round: int
    subquestion: str
    cypher: str
    row_count: int
    rows: List[Dict[str, Any]]
    error: str


class QAState(TypedDict):
    question: str
    subquestions: List[str]
    current_round: int
    next_subquestion: str
    should_stop: bool
    stop_reason: str
    steps: List[QueryStep]
    final_answer: str


ProgressCallback = Callable[[Dict[str, Any]], None]
_PROGRESS_CALLBACK: ContextVar[Optional[ProgressCallback]] = ContextVar(
    "progress_callback", default=None
)


TEXT2CYPHER_STRICT_PROMPT = """
Task: Generate EXACTLY ONE read-only Cypher query for the Neo4j graph.

Runtime Graph Schema (authoritative; case-sensitive):
{schema}

Examples (optional):
{examples}

User Question:
{query_text}

Correction Feedback:
{feedback}

Hard constraints:
1) ONLY use labels, relationship types, properties, and directed relationship patterns listed in Runtime Graph Schema.
2) Return exactly ONE Cypher statement, and it MUST be read-only.
3) Forbidden keywords: CREATE, MERGE, DELETE, DETACH, SET, REMOVE, DROP, LOAD CSV, CALL dbms, CALL apoc.
4) Do NOT use Cypher parameters like $limit, $name, $xxx. Use literal values directly (e.g., LIMIT 20).
5) Do NOT invent business dimensions not present in schema (e.g., Region, TargetGroup, industry share, seasonal trend, time-series metrics).
6) If question cannot be answered from current graph schema/data, return exactly:
   RETURN 'INSUFFICIENT_SCHEMA' AS status, 'missing required entities/properties' AS reason LIMIT 1
7) Do NOT output markdown, explanation, or code fences. Output Cypher only.

Cypher:
"""


NEXT_ACTION_PROMPT = """
You are the controller of a multi-round Neo4j analysis workflow.

Authoritative graph capability:
{capability_hint}

User question:
{question}

Completed rounds: {current_round}
Max rounds: {max_rounds}

History (JSON):
{history_json}

Return STRICT JSON only:
{{
  "decision": "continue" | "stop",
  "subquestion": "...",
  "reason": "..."
}}

Rules:
1) If current evidence is enough to answer, choose "stop".
2) If evidence is insufficient but graph may still provide useful support, choose "continue" and provide ONE short Chinese internal task.
3) Subquestion must be answerable from current schema. Never invent non-existing entities/relations.
4) If repeated empty/error rounds indicate no additional graph evidence is likely, choose "stop".
5) If current_round >= max_rounds, decision must be "stop".
6) "subquestion" is an internal task for the agent itself, NOT a question to the user.
7) Never use second-person wording such as: 你, 您, 请问, 是否希望, 还是.
8) Prefer imperative internal style like: "检索...", "定位...", "统计...", "验证...".
"""


WRITE_KEYWORD_RE = re.compile(
    r"\b(create|merge|delete|detach|set|remove|drop|load\s+csv|call\s+dbms|call\s+apoc)\b",
    flags=re.IGNORECASE,
)


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen: Set[str] = set()
    out: List[str] = []
    for x in items:
        v = x.strip()
        if not v or v in seen:
            continue
        seen.add(v)
        out.append(v)
    return out


class LangGraphPolicyQA:
    def __init__(
        self,
        *,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        deepseek_api_key: str,
        deepseek_model: str,
        deepseek_base_url: str,
        max_rounds: int = 9,
        max_rows: int = 20,
        max_t2c_retries: int = 3,
    ) -> None:
        self.max_rounds = max(1, int(max_rounds))
        self.max_rows = max(1, int(max_rows))
        self.max_t2c_retries = max(1, int(max_t2c_retries))
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.llm = OpenAILLM(
            model_name=deepseek_model,
            model_params={"temperature": 0.0},
            api_key=deepseek_api_key,
            base_url=deepseek_base_url,
        )
        runtime_schema = self._build_runtime_schema()
        self.allowed_labels: Set[str] = set(runtime_schema["labels"])
        self.allowed_relationships: Set[str] = set(runtime_schema["relationships"])
        self.allowed_properties: Set[str] = set(runtime_schema["properties"])
        self.allowed_triples: Set[tuple[str, str, str]] = set(runtime_schema["triples"])
        self.runtime_schema_text = runtime_schema["schema_text"]
        self.capability_hint = runtime_schema["capability_hint"]
        self.retriever = Text2CypherRetriever(
            driver=self.driver,
            llm=self.llm,
            neo4j_schema=self.runtime_schema_text,
            examples=self._load_query_examples(),
            custom_prompt=TEXT2CYPHER_STRICT_PROMPT,
        )
        self.graph = self._build_graph()

    def close(self) -> None:
        self.driver.close()

    def _emit_progress(self, payload: Dict[str, Any]) -> None:
        cb = _PROGRESS_CALLBACK.get()
        if cb is None:
            return
        try:
            cb(payload)
        except Exception:
            return

    def _load_query_examples(self) -> List[str]:
        query_pack = Path("结果文件夹/step8_2_iter1/query_pack.cql")
        if not query_pack.exists():
            return []
        lines = query_pack.read_text(encoding="utf-8").splitlines()
        examples: List[str] = []
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue
            cypher = stripped.rstrip(";")
            if "$" in cypher:
                continue
            if "return" in cypher.lower():
                examples.append(f"Q: Use policy graph query pattern\nCypher: {cypher}")
            if len(examples) >= 12:
                break
        return examples

    def _build_runtime_schema(self) -> Dict[str, Any]:
        label_rows, _, _ = self.driver.execute_query(
            "MATCH (n) UNWIND labels(n) AS label RETURN DISTINCT label ORDER BY label"
        )
        rel_rows, _, _ = self.driver.execute_query(
            "MATCH ()-[r]->() RETURN DISTINCT type(r) AS rel ORDER BY rel"
        )
        triple_rows, _, _ = self.driver.execute_query(
            "MATCH (a)-[r]->(b) "
            "UNWIND labels(a) AS src_label "
            "UNWIND labels(b) AS dst_label "
            "RETURN DISTINCT src_label, type(r) AS rel, dst_label ORDER BY src_label, rel, dst_label"
        )
        labels = [str(r["label"]) for r in label_rows]
        relationships = [str(r["rel"]) for r in rel_rows]
        triples = [
            (str(r["src_label"]), str(r["rel"]), str(r["dst_label"]))
            for r in triple_rows
        ]

        node_props: Dict[str, List[str]] = {}
        for label in labels:
            safe = label.replace("`", "``")
            q = (
                f"MATCH (n:`{safe}`) "
                "WITH n LIMIT 800 "
                "UNWIND keys(n) AS k "
                "RETURN k AS prop, count(*) AS freq ORDER BY freq DESC, prop ASC LIMIT 16"
            )
            rows, _, _ = self.driver.execute_query(q)
            node_props[label] = [str(r["prop"]) for r in rows]

        rel_props: Dict[str, List[str]] = {}
        for rel in relationships:
            safe = rel.replace("`", "``")
            q = (
                f"MATCH ()-[r:`{safe}`]->() "
                "WITH r LIMIT 1200 "
                "UNWIND keys(r) AS k "
                "RETURN k AS prop, count(*) AS freq ORDER BY freq DESC, prop ASC LIMIT 16"
            )
            rows, _, _ = self.driver.execute_query(q)
            rel_props[rel] = [str(r["prop"]) for r in rows]

        schema_lines: List[str] = []
        schema_lines.append("Node labels:")
        for label in labels:
            schema_lines.append(f"- {label}: properties={node_props.get(label, [])}")
        schema_lines.append("Relationship types:")
        for rel in relationships:
            schema_lines.append(f"- {rel}: properties={rel_props.get(rel, [])}")
        schema_lines.append("Directed relationship patterns:")
        for src, rel, dst in triples:
            schema_lines.append(f"- ({src})-[:{rel}]->({dst})")
        schema_lines.append("Known restrictions:")
        schema_lines.append("- No Region or TargetGroup labels unless explicitly listed above.")
        schema_lines.append("- No applies_to_region/applies_to_target relations unless explicitly listed above.")
        schema_lines.append("- Prefer existing fields like source_path, track, risk_level, confidence, clause_id, doc_instance_id.")
        schema_lines.append("- This graph is policy text structure; it does not directly contain regional/industry time-series consumption statistics.")

        all_props: Set[str] = set()
        for v in node_props.values():
            all_props.update(v)
        for v in rel_props.values():
            all_props.update(v)

        capability_hint = (
            f"当前可用节点类型: {labels}; "
            f"当前可用关系类型: {relationships}; "
            f"当前可用有向关系模式: {triples}; "
            "如果问题要求图中不存在的结构或时序统计字段，必须返回“证据不足/需要外部数据”。"
        )
        return {
            "labels": labels,
            "relationships": relationships,
            "properties": sorted(all_props),
            "triples": triples,
            "schema_text": "\n".join(schema_lines),
            "capability_hint": capability_hint,
        }

    def _build_graph(self):
        graph = StateGraph(QAState)
        graph.add_node("decide_next_query", self._decide_next_query)
        graph.add_node("run_query", self._run_query)
        graph.add_node("synthesize_answer", self._synthesize_answer)

        graph.add_edge(START, "decide_next_query")
        graph.add_conditional_edges(
            "decide_next_query",
            self._route_after_decision,
            {
                "run_query": "run_query",
                "synthesize_answer": "synthesize_answer",
            },
        )
        graph.add_edge("run_query", "decide_next_query")
        graph.add_edge("synthesize_answer", END)
        return graph.compile()

    def _safe_json_extract(self, text: str) -> Dict[str, Any]:
        raw = text.strip()
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, flags=re.DOTALL | re.IGNORECASE)
        if fenced:
            raw = fenced.group(1)
        if raw.startswith("{") and raw.endswith("}"):
            try:
                return json.loads(raw)
            except Exception:
                pass
        start = raw.find("{")
        while start != -1:
            depth = 0
            for i in range(start, len(raw)):
                if raw[i] == "{":
                    depth += 1
                elif raw[i] == "}":
                    depth -= 1
                    if depth == 0:
                        candidate = raw[start : i + 1]
                        try:
                            return json.loads(candidate)
                        except Exception:
                            break
            start = raw.find("{", start + 1)
        return {}

    def _planner_history_view(self, steps: List[QueryStep]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for s in steps[-6:]:
            sample_rows: List[Dict[str, Any]] = []
            for row in s.get("rows", [])[:2]:
                sample_rows.append(
                    {
                        str(k): (str(v)[:120] + "..." if len(str(v)) > 120 else str(v))
                        for k, v in row.items()
                    }
                )
            out.append(
                {
                    "round": s.get("round"),
                    "subquestion": s.get("subquestion"),
                    "cypher": s.get("cypher"),
                    "row_count": s.get("row_count"),
                    "error": s.get("error"),
                    "sample_rows": sample_rows,
                }
            )
        return out

    def _fallback_internal_subquestion(self, question: str, steps: List[QueryStep]) -> str:
        if not steps:
            return (
                "检索与用户问题最相关的机制链路证据，"
                "优先返回risk_level、confidence、clause_id、doc_instance_id等字段。"
            )
        return (
            "基于已有查询结果补充一条可验证证据链，"
            "聚焦高风险关系、参数定义映射与来源条款信息。"
        )

    def _sanitize_internal_subquestion(
        self,
        *,
        question: str,
        subquestion: str,
        steps: List[QueryStep],
    ) -> str:
        s = (subquestion or "").strip()
        if not s:
            return self._fallback_internal_subquestion(question, steps)

        # Convert any user-facing clarification style into an internal task style.
        interactive_markers = [
            "你",
            "您",
            "请问",
            "是否希望",
            "还是",
            "吗",
            "?",
            "？",
        ]
        if any(tok in s for tok in interactive_markers):
            return self._fallback_internal_subquestion(question, steps)

        # Avoid trailing punctuation that looks like asking the user.
        s = s.rstrip(" ?？")
        if not s:
            return self._fallback_internal_subquestion(question, steps)
        return s

    def _decide_next_query(self, state: QAState) -> Dict[str, Any]:
        current_round = int(state.get("current_round", 0))
        question = state["question"].strip()
        steps = list(state.get("steps", []))

        if current_round >= self.max_rounds:
            return {
                "should_stop": True,
                "stop_reason": f"达到最大轮次上限({self.max_rounds})",
                "next_subquestion": "",
            }

        history_payload = self._planner_history_view(steps)
        prompt = NEXT_ACTION_PROMPT.format(
            capability_hint=self.capability_hint,
            question=question,
            current_round=current_round,
            max_rounds=self.max_rounds,
            history_json=json.dumps(history_payload, ensure_ascii=False),
        )

        decision = "continue"
        subquestion = ""
        reason = ""
        try:
            raw = self.llm.invoke(prompt, temperature=0.0).content
            obj = self._safe_json_extract(raw)
            decision = str(obj.get("decision", "continue")).strip().lower()
            subquestion = str(obj.get("subquestion", "")).strip()
            reason = str(obj.get("reason", "")).strip()
        except Exception:
            decision = "continue"

        if decision not in {"continue", "stop"}:
            decision = "continue"

        if decision == "stop":
            stop_reason = reason or "模型判定证据已足够或继续查询收益较低"
            return {
                "should_stop": True,
                "stop_reason": stop_reason,
                "next_subquestion": "",
            }

        subquestion = self._sanitize_internal_subquestion(
            question=question,
            subquestion=subquestion,
            steps=steps,
        )

        return {
            "should_stop": False,
            "stop_reason": "",
            "next_subquestion": subquestion,
        }

    def _extract_query_labels(self, cypher: str) -> Set[str]:
        labels: Set[str] = set()
        for m in re.finditer(r"\([^\)]*:\s*`?([A-Za-z_][A-Za-z0-9_]*)`?", cypher):
            labels.add(m.group(1))
        return labels

    def _extract_query_rels(self, cypher: str) -> Set[str]:
        rels: Set[str] = set()
        for m in re.finditer(r"\[[^\]]*:\s*`?([A-Za-z_][A-Za-z0-9_]*)`?", cypher):
            rels.add(m.group(1))
        return rels

    def _extract_query_properties(self, cypher: str) -> Set[str]:
        props: Set[str] = set()
        for m in re.finditer(r"\b[A-Za-z_][A-Za-z0-9_]*\.([A-Za-z_][A-Za-z0-9_]*)\b", cypher):
            props.add(m.group(1))
        for block in re.findall(r"\{([^{}]+)\}", cypher):
            for m in re.finditer(r"([A-Za-z_][A-Za-z0-9_]*)\s*:", block):
                props.add(m.group(1))
        return props

    def _extract_query_triples(self, cypher: str) -> Set[tuple[str, str, str]]:
        triples: Set[tuple[str, str, str]] = set()
        fwd = re.compile(
            r"\(\s*[^)]*:\s*`?([A-Za-z_][A-Za-z0-9_]*)`?[^)]*\)\s*-\s*"
            r"\[[^\]]*:\s*`?([A-Za-z_][A-Za-z0-9_]*)`?[^]]*\]\s*->\s*"
            r"\(\s*[^)]*:\s*`?([A-Za-z_][A-Za-z0-9_]*)`?[^)]*\)"
        )
        rev = re.compile(
            r"\(\s*[^)]*:\s*`?([A-Za-z_][A-Za-z0-9_]*)`?[^)]*\)\s*<-\s*"
            r"\[[^\]]*:\s*`?([A-Za-z_][A-Za-z0-9_]*)`?[^]]*\]\s*-\s*"
            r"\(\s*[^)]*:\s*`?([A-Za-z_][A-Za-z0-9_]*)`?[^)]*\)"
        )
        for m in fwd.finditer(cypher):
            triples.add((m.group(1), m.group(2), m.group(3)))
        for m in rev.finditer(cypher):
            triples.add((m.group(3), m.group(2), m.group(1)))
        return triples

    def _validate_cypher_guard(self, cypher: str) -> str:
        c = (cypher or "").strip()
        if not c:
            return "empty cypher"
        if WRITE_KEYWORD_RE.search(c):
            return "write keyword is not allowed"
        labels = self._extract_query_labels(c)
        rels = self._extract_query_rels(c)
        props = self._extract_query_properties(c)
        triples = self._extract_query_triples(c)
        bad_labels = sorted([x for x in labels if x not in self.allowed_labels])
        bad_rels = sorted([x for x in rels if x not in self.allowed_relationships])
        bad_props = sorted([x for x in props if x not in self.allowed_properties])
        bad_triples = sorted([x for x in triples if x not in self.allowed_triples])
        if bad_labels or bad_rels or bad_props or bad_triples:
            return (
                f"unknown schema tokens: bad_labels={bad_labels}, bad_relationships={bad_rels}, bad_properties={bad_props}, bad_triples={bad_triples}, "
                f"allowed_labels={sorted(self.allowed_labels)}, allowed_relationships={sorted(self.allowed_relationships)}, "
                f"allowed_properties={sorted(self.allowed_properties)}, allowed_triples={sorted(self.allowed_triples)}"
            )
        return ""

    def _normalize_value(self, value: Any) -> Any:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, list):
            return [self._normalize_value(v) for v in value]
        if isinstance(value, dict):
            return {str(k): self._normalize_value(v) for k, v in value.items()}
        return str(value)

    def _run_query(self, state: QAState) -> Dict[str, Any]:
        current_round = int(state.get("current_round", 0))
        question = state["question"]
        steps = list(state.get("steps", []))
        subquestions = list(state.get("subquestions", []))

        if state.get("should_stop", False):
            return {
                "current_round": current_round,
                "steps": steps,
                "subquestions": subquestions,
            }

        subquestion = str(state.get("next_subquestion", "")).strip() or question.strip()
        cypher = ""
        rows: List[Dict[str, Any]] = []
        error = ""

        feedback = "No previous error."
        for _ in range(self.max_t2c_retries):
            try:
                raw = self.retriever.get_search_results(
                    subquestion,
                    prompt_params={
                        "feedback": feedback,
                        "schema": self.runtime_schema_text,
                    },
                )
                cypher = str((raw.metadata or {}).get("cypher", ""))
                guard_err = self._validate_cypher_guard(cypher)
                if guard_err:
                    error = guard_err
                    feedback = f"Previous generated Cypher rejected by guard: {guard_err}. Please correct it."
                    continue
                rows = [
                    {str(k): self._normalize_value(v) for k, v in dict(record).items()}
                    for record in raw.records
                ][: self.max_rows]
                error = ""
                break
            except Text2CypherRetrievalError as exc:
                error = str(exc)
                feedback = f"Previous Cypher failed to execute: {error}. Please correct it."
            except Exception as exc:  # pragma: no cover
                error = str(exc)
                feedback = f"Unexpected error: {error}. Please correct it."

        step: QueryStep = {
            "round": current_round + 1,
            "subquestion": subquestion,
            "cypher": cypher,
            "row_count": len(rows),
            "rows": rows,
            "error": error,
        }
        steps.append(step)
        subquestions.append(subquestion)

        self._emit_progress(
            {
                "type": "round_complete",
                "current_round": current_round + 1,
                "max_rounds": self.max_rounds,
                "step": step,
            }
        )

        return {
            "current_round": current_round + 1,
            "steps": steps,
            "subquestions": subquestions,
            "next_subquestion": "",
        }

    def _route_after_decision(self, state: QAState) -> str:
        if bool(state.get("should_stop", False)):
            return "synthesize_answer"
        return "run_query"

    def _synthesize_answer(self, state: QAState) -> Dict[str, Any]:
        question = state["question"]
        steps = state.get("steps", [])
        stop_reason = state.get("stop_reason", "")
        prompt = (
            "You are an energy policy analyst. "
            "Use query outputs to answer the user question. "
            "If evidence is insufficient, explicitly say uncertainty. "
            "Output concise Chinese answer with sections: 结论, 依据, 风险与不确定性.\n"
            f"Graph capability: {self.capability_hint}\n"
            f"停止原因: {stop_reason}\n"
            f"用户问题: {question}\n"
            f"查询轨迹(JSON): {json.dumps(steps, ensure_ascii=False)}"
        )
        answer = self.llm.invoke(prompt, temperature=0.1).content.strip()
        return {"final_answer": answer}

    def ask(
        self,
        question: str,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> Dict[str, Any]:
        initial_state: QAState = {
            "question": question,
            "subquestions": [],
            "current_round": 0,
            "next_subquestion": "",
            "should_stop": False,
            "stop_reason": "",
            "steps": [],
            "final_answer": "",
        }

        token = _PROGRESS_CALLBACK.set(progress_callback)
        try:
            self._emit_progress(
                {
                    "type": "started",
                    "current_round": 0,
                    "max_rounds": self.max_rounds,
                }
            )
            result = self.graph.invoke(initial_state)
            self._emit_progress(
                {
                    "type": "finished",
                    "current_round": len(result.get("steps", [])),
                    "max_rounds": self.max_rounds,
                }
            )
        finally:
            _PROGRESS_CALLBACK.reset(token)

        steps = result.get("steps", [])
        subquestions = _dedupe_keep_order([str(s.get("subquestion", "")) for s in steps])
        return {
            "question": question,
            "subquestions": subquestions,
            "steps": steps,
            "stop_reason": result.get("stop_reason", ""),
            "final_answer": result.get("final_answer", ""),
        }
