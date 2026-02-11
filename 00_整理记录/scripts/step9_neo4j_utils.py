from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class Neo4jHttpError(RuntimeError):
    pass


@dataclass
class Neo4jHttpClient:
    base_url: str
    user: str
    password: str
    timeout: int = 60

    def _auth_header(self) -> str:
        token = base64.b64encode(f"{self.user}:{self.password}".encode("utf-8")).decode("ascii")
        return f"Basic {token}"

    def execute(self, statement: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        payload = {
            "statements": [
                {
                    "statement": statement,
                    "parameters": parameters or {},
                }
            ]
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url=f"{self.base_url.rstrip('/')}/db/neo4j/tx/commit",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": self._auth_header(),
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
            raise Neo4jHttpError(f"HTTP {exc.code}: {detail}") from exc
        except Exception as exc:
            raise Neo4jHttpError(f"request failed: {exc}") from exc

        try:
            obj = json.loads(body)
        except Exception as exc:
            raise Neo4jHttpError(f"invalid json response: {body[:500]}") from exc

        errors = obj.get("errors", [])
        if errors:
            raise Neo4jHttpError(json.dumps(errors, ensure_ascii=False))

        results = obj.get("results", [])
        if not results:
            return []
        result = results[0]
        columns = result.get("columns", [])
        rows = []
        for item in result.get("data", []):
            values = item.get("row", [])
            row = {columns[i]: values[i] for i in range(min(len(columns), len(values)))}
            rows.append(row)
        return rows

    def execute_scalar(self, statement: str, parameters: Optional[Dict[str, Any]] = None, key: str = "value") -> Any:
        rows = self.execute(statement, parameters=parameters)
        if not rows:
            return None
        return rows[0].get(key)

    def wait_ready(self, max_wait_seconds: int = 180, interval_seconds: float = 2.0) -> None:
        deadline = time.time() + max_wait_seconds
        last_error = ""
        while time.time() < deadline:
            try:
                rows = self.execute("RETURN 1 AS value")
                if rows and rows[0].get("value") == 1:
                    return
            except Exception as exc:  # pragma: no cover
                last_error = str(exc)
            time.sleep(interval_seconds)
        raise Neo4jHttpError(f"neo4j not ready within {max_wait_seconds}s: {last_error}")
