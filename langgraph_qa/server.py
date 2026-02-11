from __future__ import annotations

import os
import secrets
import threading
import time
import uuid
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

if not DEEPSEEK_API_KEY:
    raise RuntimeError("DEEPSEEK_API_KEY is required. Put it in .env.langgraph or .env.local")

qa_service = LangGraphPolicyQA(
    neo4j_uri=NEO4J_URI,
    neo4j_user=NEO4J_USER,
    neo4j_password=NEO4J_PASSWORD,
    deepseek_api_key=DEEPSEEK_API_KEY,
    deepseek_model=DEEPSEEK_MODEL,
    deepseek_base_url=DEEPSEEK_BASE_URL,
    max_rounds=9,
    max_rows=20,
)

app = FastAPI(title="LangGraph Policy QA", version="1.1.0")
app.add_middleware(
    SessionMiddleware,
    secret_key=APP_SESSION_SECRET,
    max_age=60 * 60 * 8,
    same_site="lax",
    https_only=False,
)


JOB_LOCK = threading.Lock()
JOBS: Dict[str, Dict[str, Any]] = {}
JOB_EXPIRE_SECONDS = 60 * 60 * 6
JOB_MAX_STORE = 200


class LoginPayload(BaseModel):
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=256)


class AskPayload(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class AskStartPayload(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


def _is_authenticated(request: Request) -> bool:
    return bool(request.session.get("auth") is True and request.session.get("username"))


def _require_auth(request: Request) -> str:
    if not _is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return str(request.session["username"])


def _prune_jobs(now_ts: int) -> None:
    stale_ids = [
        job_id
        for job_id, job in JOBS.items()
        if now_ts - int(job.get("updated_at", now_ts)) > JOB_EXPIRE_SECONDS
    ]
    for job_id in stale_ids:
        JOBS.pop(job_id, None)

    if len(JOBS) <= JOB_MAX_STORE:
        return
    ordered = sorted(JOBS.items(), key=lambda kv: int(kv[1].get("updated_at", 0)))
    for job_id, _ in ordered[: len(JOBS) - JOB_MAX_STORE]:
        JOBS.pop(job_id, None)


def _run_async_job(job_id: str, question: str, username: str) -> None:
    def on_progress(event: Dict[str, Any]) -> None:
        with JOB_LOCK:
            job = JOBS.get(job_id)
            if not job:
                return
            event_type = str(event.get("type", ""))
            if event_type == "round_complete":
                step = event.get("step")
                if isinstance(step, dict):
                    job["steps"] = list(job.get("steps", [])) + [step]
                job["current_round"] = int(event.get("current_round", job.get("current_round", 0)))
            elif event_type in {"started", "finished"}:
                job["current_round"] = int(event.get("current_round", job.get("current_round", 0)))
            job["updated_at"] = int(time.time())

    try:
        result = qa_service.ask(question, progress_callback=on_progress)
        with JOB_LOCK:
            job = JOBS.get(job_id)
            if not job:
                return
            job["status"] = "completed"
            job["result"] = result
            job["subquestions"] = result.get("subquestions", [])
            job["steps"] = result.get("steps", [])
            job["current_round"] = len(result.get("steps", []))
            job["final_answer"] = result.get("final_answer", "")
            job["stop_reason"] = result.get("stop_reason", "")
            job["updated_at"] = int(time.time())
    except Exception as exc:
        with JOB_LOCK:
            job = JOBS.get(job_id)
            if not job:
                return
            job["status"] = "failed"
            job["error"] = str(exc)
            job["updated_at"] = int(time.time())


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
        "max_rounds": qa_service.max_rounds,
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


@app.post("/api/ask/start")
def ask_start(payload: AskStartPayload, request: Request) -> Dict[str, Any]:
    username = _require_auth(request)
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is empty")

    now_ts = int(time.time())
    job_id = uuid.uuid4().hex
    job = {
        "job_id": job_id,
        "user": username,
        "question": question,
        "status": "running",
        "current_round": 0,
        "max_rounds": qa_service.max_rounds,
        "subquestions": [],
        "steps": [],
        "final_answer": "",
        "stop_reason": "",
        "result": None,
        "error": "",
        "created_at": now_ts,
        "updated_at": now_ts,
    }

    with JOB_LOCK:
        _prune_jobs(now_ts)
        JOBS[job_id] = job

    t = threading.Thread(target=_run_async_job, args=(job_id, question, username), daemon=True)
    t.start()

    return {
        "ok": True,
        "job_id": job_id,
        "status": "running",
        "max_rounds": qa_service.max_rounds,
    }


@app.get("/api/ask/status/{job_id}")
def ask_status(job_id: str, request: Request) -> Dict[str, Any]:
    username = _require_auth(request)
    with JOB_LOCK:
        job = JOBS.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.get("user") != username:
            raise HTTPException(status_code=403, detail="Forbidden")
        payload = dict(job)

    current_round = int(payload.get("current_round", 0))
    max_rounds = max(1, int(payload.get("max_rounds", qa_service.max_rounds)))
    progress = int(min(100, round((current_round / max_rounds) * 100)))
    if payload.get("status") == "completed":
        progress = 100

    return {
        "ok": True,
        "job_id": payload.get("job_id"),
        "status": payload.get("status"),
        "current_round": current_round,
        "max_rounds": max_rounds,
        "progress": progress,
        "subquestions": payload.get("subquestions", []),
        "steps": payload.get("steps", []),
        "final_answer": payload.get("final_answer", ""),
        "stop_reason": payload.get("stop_reason", ""),
        "error": payload.get("error", ""),
    }


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
