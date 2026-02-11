from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, TypedDict

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
    current_index: int
    steps: List[QueryStep]
    final_answer: str


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
        schema_path: str = "结果文件夹/schema_v1.yaml",
        max_rounds: int = 3,
        max_rows: int = 20,
    ) -> None:
        self.max_rounds = max(1, int(max_rounds))
        self.max_rows = max(1, int(max_rows))
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        schema_text = Path(schema_path).read_text(encoding="utf-8")
        self.llm = OpenAILLM(
            model_name=deepseek_model,
            model_params={"temperature": 0.0},
            api_key=deepseek_api_key,
            base_url=deepseek_base_url,
        )
        self.retriever = Text2CypherRetriever(
            driver=self.driver,
            llm=self.llm,
            neo4j_schema=schema_text,
            examples=self._load_query_examples(),
        )
        self.graph = self._build_graph()

    def close(self) -> None:
        self.driver.close()

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
            if "return" in cypher.lower():
                examples.append(f"Q: Use policy graph query pattern\nCypher: {cypher}")
            if len(examples) >= 12:
                break
        return examples

    def _build_graph(self):
        graph = StateGraph(QAState)
        graph.add_node("plan_subquestions", self._plan_subquestions)
        graph.add_node("run_query", self._run_query)
        graph.add_node("synthesize_answer", self._synthesize_answer)

        graph.add_edge(START, "plan_subquestions")
        graph.add_edge("plan_subquestions", "run_query")
        graph.add_conditional_edges(
            "run_query",
            self._route_after_query,
            {
                "run_query": "run_query",
                "synthesize_answer": "synthesize_answer",
            },
        )
        graph.add_edge("synthesize_answer", END)
        return graph.compile()

    def _safe_json_extract(self, text: str) -> Dict[str, Any]:
        raw = text.strip()
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, flags=re.DOTALL | re.IGNORECASE)
        if fenced:
            raw = fenced.group(1)
        if raw.startswith("{") and raw.endswith("}"):
            return json.loads(raw)
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

    def _plan_subquestions(self, state: QAState) -> Dict[str, Any]:
        question = state["question"].strip()
        prompt = (
            "You are planning multi-step policy graph analysis. "
            "Return strict JSON with key `subquestions` as an array of 2-3 short Chinese questions. "
            "Each subquestion should be answerable from a Neo4j policy graph.\n"
            f"User question: {question}"
        )
        raw = self.llm.invoke(prompt, temperature=0.0).content
        obj = self._safe_json_extract(raw)
        subquestions = obj.get("subquestions", [])
        cleaned: List[str] = []
        if isinstance(subquestions, list):
            for item in subquestions:
                s = str(item).strip()
                if s and s not in cleaned:
                    cleaned.append(s)
        if not cleaned:
            cleaned = [question, f"请补充与该问题相关的关键证据和高风险因素：{question}"]
        if len(cleaned) == 1:
            cleaned.append(f"请补充与该问题相关的关键证据和高风险因素：{question}")
        cleaned = cleaned[: self.max_rounds]
        return {"subquestions": cleaned, "current_index": 0, "steps": []}

    def _normalize_value(self, value: Any) -> Any:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, list):
            return [self._normalize_value(v) for v in value]
        if isinstance(value, dict):
            return {str(k): self._normalize_value(v) for k, v in value.items()}
        return str(value)

    def _run_query(self, state: QAState) -> Dict[str, Any]:
        idx = int(state.get("current_index", 0))
        subquestions = state.get("subquestions", [])
        steps = list(state.get("steps", []))
        if idx >= len(subquestions):
            return {"current_index": idx, "steps": steps}

        subquestion = subquestions[idx]
        cypher = ""
        rows: List[Dict[str, Any]] = []
        error = ""

        try:
            raw = self.retriever.get_search_results(subquestion)
            cypher = str((raw.metadata or {}).get("cypher", ""))
            rows = [
                {str(k): self._normalize_value(v) for k, v in dict(record).items()}
                for record in raw.records
            ][: self.max_rows]
        except Text2CypherRetrievalError as exc:
            error = str(exc)
        except Exception as exc:  # pragma: no cover
            error = str(exc)

        steps.append(
            {
                "round": idx + 1,
                "subquestion": subquestion,
                "cypher": cypher,
                "row_count": len(rows),
                "rows": rows,
                "error": error,
            }
        )
        return {"current_index": idx + 1, "steps": steps}

    def _route_after_query(self, state: QAState) -> str:
        idx = int(state.get("current_index", 0))
        total = len(state.get("subquestions", []))
        if idx < total:
            return "run_query"
        return "synthesize_answer"

    def _synthesize_answer(self, state: QAState) -> Dict[str, Any]:
        question = state["question"]
        steps = state.get("steps", [])
        prompt = (
            "You are an energy policy analyst. "
            "Use query outputs to answer the user question. "
            "If evidence is insufficient, explicitly say uncertainty. "
            "Output concise Chinese answer with sections: 结论, 依据, 风险与不确定性.\n"
            f"用户问题: {question}\n"
            f"查询轨迹(JSON): {json.dumps(steps, ensure_ascii=False)}"
        )
        answer = self.llm.invoke(prompt, temperature=0.1).content.strip()
        return {"final_answer": answer}

    def ask(self, question: str) -> Dict[str, Any]:
        initial_state: QAState = {
            "question": question,
            "subquestions": [],
            "current_index": 0,
            "steps": [],
            "final_answer": "",
        }
        result = self.graph.invoke(initial_state)
        return {
            "question": question,
            "subquestions": result.get("subquestions", []),
            "steps": result.get("steps", []),
            "final_answer": result.get("final_answer", ""),
        }
