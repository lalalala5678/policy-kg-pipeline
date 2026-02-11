#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from step9_neo4j_utils import Neo4jHttpClient


FORBIDDEN_CYPHER_RE = re.compile(
    r"\b("
    r"create|merge|delete|detach|remove|set|drop|"
    r"load\s+csv|"
    r"call\s+dbms|"
    r"apoc\."
    r")\b",
    flags=re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run DeepSeek + Neo4j question answering")
    parser.add_argument("--question", required=True, help="Natural language question")
    parser.add_argument("--output-dir", default="00_整理记录/step10_iter1", help="Output directory")
    parser.add_argument("--env-file", default=".env.local", help="Optional env file for API keys")
    parser.add_argument("--neo4j-url", default="http://127.0.0.1:17474", help="Neo4j HTTP URL")
    parser.add_argument("--neo4j-user", default="neo4j", help="Neo4j username")
    parser.add_argument("--neo4j-password", default="policykg_step9", help="Neo4j password")
    parser.add_argument("--deepseek-base-url", default="https://api.deepseek.com", help="DeepSeek base URL")
    parser.add_argument("--deepseek-model", default="deepseek-chat", help="DeepSeek model")
    parser.add_argument("--temperature", type=float, default=0.0, help="LLM temperature")
    parser.add_argument("--max-rows", type=int, default=30, help="Max rows to keep in final report")
    parser.add_argument("--skip-answer", action="store_true", help="Skip final natural language answer call")
    parser.add_argument("--print-cypher", action="store_true", help="Print generated Cypher to stdout")
    return parser.parse_args()


def stable_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


def _http_post_json(url: str, payload: Dict[str, Any], headers: Dict[str, str], timeout: int = 60) -> Dict[str, Any]:
    req = urllib.request.Request(
        url=url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
        raise RuntimeError(f"HTTP {exc.code} {url}: {detail}") from exc
    except Exception as exc:
        raise RuntimeError(f"request failed {url}: {exc}") from exc
    try:
        return json.loads(body)
    except Exception as exc:
        raise RuntimeError(f"invalid json from {url}: {body[:500]}") from exc


def deepseek_chat(
    *,
    api_key: str,
    base_url: str,
    model: str,
    messages: List[Dict[str, str]],
    temperature: float,
    timeout: int = 60,
) -> str:
    clean_base = base_url.rstrip("/")
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    endpoints = [
        f"{clean_base}/chat/completions",
        f"{clean_base}/v1/chat/completions",
    ]
    last_error = ""
    for endpoint in endpoints:
        try:
            obj = _http_post_json(endpoint, payload, headers, timeout=timeout)
        except Exception as exc:
            last_error = str(exc)
            continue
        choices = obj.get("choices", [])
        if not choices:
            last_error = f"no choices in response from {endpoint}: {obj}"
            continue
        content = choices[0].get("message", {}).get("content", "")
        if not isinstance(content, str) or not content.strip():
            last_error = f"empty content from {endpoint}: {obj}"
            continue
        return content.strip()
    raise RuntimeError(f"deepseek chat failed: {last_error}")


def extract_first_json_object(text: str) -> Dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return json.loads(stripped)
    code_block = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if code_block:
        return json.loads(code_block.group(1))
    start = text.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            ch = text[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[start : i + 1]
                    try:
                        return json.loads(candidate)
                    except Exception:
                        break
        start = text.find("{", start + 1)
    raise RuntimeError(f"cannot parse json object from model output: {text[:500]}")


def sanitize_cypher(cypher: str) -> str:
    if not isinstance(cypher, str):
        raise RuntimeError("cypher must be string")
    c = cypher.strip().strip("`").strip()
    if not c:
        raise RuntimeError("empty cypher")
    if FORBIDDEN_CYPHER_RE.search(c):
        raise RuntimeError(f"write cypher is forbidden: {c}")
    if "return" not in c.lower():
        raise RuntimeError("cypher must include RETURN")
    return c


def make_schema_snapshot(client: Neo4jHttpClient) -> Dict[str, Any]:
    labels = client.execute(
        "MATCH (n) UNWIND labels(n) AS label RETURN label, count(*) AS cnt ORDER BY cnt DESC, label ASC"
    )
    predicates = client.execute("MATCH ()-[r]->() RETURN type(r) AS predicate, count(*) AS cnt ORDER BY cnt DESC, predicate ASC")
    return {
        "labels": labels,
        "predicates": predicates,
    }


def propose_cypher(
    *,
    api_key: str,
    base_url: str,
    model: str,
    question: str,
    schema_snapshot: Dict[str, Any],
    temperature: float,
    max_rows: int,
) -> Tuple[str, Dict[str, Any], str, str]:
    system = (
        "You are a Neo4j Cypher planner. "
        "Return ONLY a JSON object with keys: cypher, params, reason. "
        "Cypher must be read-only and must include RETURN and LIMIT. "
        "Never use CREATE/MERGE/SET/DELETE/REMOVE/DROP/LOAD CSV/APOC/dbms procedures. "
        "Use only labels and predicates provided."
    )
    user = {
        "question": question,
        "max_rows": max_rows,
        "schema_snapshot": schema_snapshot,
    }
    raw = deepseek_chat(
        api_key=api_key,
        base_url=base_url,
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
        ],
        temperature=temperature,
    )
    obj = extract_first_json_object(raw)
    cypher = sanitize_cypher(str(obj.get("cypher", "")))
    params = obj.get("params", {})
    if not isinstance(params, dict):
        params = {}
    reason = str(obj.get("reason", ""))
    return cypher, params, reason, raw


def answer_question(
    *,
    api_key: str,
    base_url: str,
    model: str,
    question: str,
    cypher: str,
    params: Dict[str, Any],
    rows: List[Dict[str, Any]],
    temperature: float,
) -> str:
    system = (
        "You answer user questions using query results from a policy knowledge graph. "
        "Be concise, factual, and mention uncertainty when evidence is insufficient."
    )
    user = {
        "question": question,
        "cypher": cypher,
        "params": params,
        "row_count": len(rows),
        "rows_preview": rows[:20],
    }
    return deepseek_chat(
        api_key=api_key,
        base_url=base_url,
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
        ],
        temperature=temperature,
    )


def main() -> None:
    args = parse_args()
    load_env_file(Path(args.env_file))

    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "DEEPSEEK_API_KEY is missing. Set env var or put it in --env-file (default .env.local)."
        )

    client = Neo4jHttpClient(
        base_url=args.neo4j_url,
        user=args.neo4j_user,
        password=args.neo4j_password,
        timeout=120,
    )
    client.wait_ready(max_wait_seconds=120)

    schema_snapshot = make_schema_snapshot(client)
    cypher, params, reason, model_raw = propose_cypher(
        api_key=api_key,
        base_url=args.deepseek_base_url,
        model=args.deepseek_model,
        question=args.question,
        schema_snapshot=schema_snapshot,
        temperature=args.temperature,
        max_rows=max(1, int(args.max_rows)),
    )
    if args.print_cypher:
        print(cypher)

    rows = client.execute(cypher, parameters=params)
    max_rows = max(1, int(args.max_rows))
    rows_capped = rows[:max_rows]

    answer = ""
    if not args.skip_answer:
        answer = answer_question(
            api_key=api_key,
            base_url=args.deepseek_base_url,
            model=args.deepseek_model,
            question=args.question,
            cypher=cypher,
            params=params,
            rows=rows_capped,
            temperature=args.temperature,
        )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = output_dir / f"step10_deepseek_qa_{ts}.json"
    report = {
        "generated_at_utc": ts,
        "question": args.question,
        "neo4j": {
            "url": args.neo4j_url,
        },
        "deepseek": {
            "base_url": args.deepseek_base_url,
            "model": args.deepseek_model,
        },
        "planner": {
            "cypher": cypher,
            "params": params,
            "reason": reason,
            "raw_model_output": model_raw,
        },
        "query_result": {
            "row_count_total": len(rows),
            "row_count_capped": len(rows_capped),
            "rows": rows_capped,
        },
        "final_answer": answer,
    }
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(stable_json({"output": str(out_path), "row_count_total": len(rows), "answer_len": len(answer)}))


if __name__ == "__main__":
    main()
