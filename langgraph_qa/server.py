from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from starlette.middleware.sessions import SessionMiddleware

from .workflow import LangGraphPolicyQA


for env_name in [".env.langgraph", ".env.local"]:
    load_dotenv(env_name, override=False)


APP_USERNAME = os.getenv("APP_USERNAME", "neo4j")
APP_PASSWORD = os.getenv("APP_PASSWORD", "policykg_step9")
APP_SESSION_SECRET = os.getenv("APP_SESSION_SECRET", "change-me-langgraph-session-secret")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:17687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "policykg_step9")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
KG_SCHEMA_PATH = os.getenv("KG_SCHEMA_PATH", "结果文件夹/schema_v1.yaml")

if not DEEPSEEK_API_KEY:
    raise RuntimeError("DEEPSEEK_API_KEY is required. Put it in .env.langgraph or .env.local")

qa_service = LangGraphPolicyQA(
    neo4j_uri=NEO4J_URI,
    neo4j_user=NEO4J_USER,
    neo4j_password=NEO4J_PASSWORD,
    deepseek_api_key=DEEPSEEK_API_KEY,
    deepseek_model=DEEPSEEK_MODEL,
    deepseek_base_url=DEEPSEEK_BASE_URL,
    schema_path=KG_SCHEMA_PATH,
    max_rounds=3,
    max_rows=20,
)

app = FastAPI(title="LangGraph Policy QA", version="1.0.0")
app.add_middleware(
    SessionMiddleware,
    secret_key=APP_SESSION_SECRET,
    max_age=60 * 60 * 8,
    same_site="lax",
    https_only=False,
)


class LoginPayload(BaseModel):
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=256)


class AskPayload(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


def _is_authenticated(request: Request) -> bool:
    return bool(request.session.get("auth") is True and request.session.get("username"))


def _require_auth(request: Request) -> str:
    if not _is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return str(request.session["username"])


@app.on_event("shutdown")
def _shutdown() -> None:
    qa_service.close()


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    html_path = Path(__file__).with_name("static").joinpath("index.html")
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.get("/api/health")
def health(request: Request) -> Dict[str, Any]:
    return {
        "ok": True,
        "authenticated": _is_authenticated(request),
        "model": DEEPSEEK_MODEL,
        "neo4j_uri": NEO4J_URI,
    }


@app.post("/api/login")
def login(payload: LoginPayload, request: Request) -> Dict[str, Any]:
    user_ok = secrets.compare_digest(payload.username, APP_USERNAME)
    pass_ok = secrets.compare_digest(payload.password, APP_PASSWORD)
    if not (user_ok and pass_ok):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    request.session["auth"] = True
    request.session["username"] = payload.username
    return {"ok": True, "username": payload.username}


@app.post("/api/logout")
def logout(request: Request) -> Dict[str, Any]:
    request.session.clear()
    return {"ok": True}


@app.post("/api/ask")
def ask(payload: AskPayload, request: Request) -> Dict[str, Any]:
    username = _require_auth(request)
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is empty")
    result = qa_service.ask(question)
    return {
        "ok": True,
        "user": username,
        "result": result,
    }

