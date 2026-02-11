#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if [ ! -x ".venv/bin/uvicorn" ]; then
  echo "missing .venv/bin/uvicorn; please install dependencies first" >&2
  exit 1
fi

export PYTHONUNBUFFERED=1
export APP_PORT="${APP_PORT:-18081}"

exec .venv/bin/uvicorn langgraph_qa.server:app --host 0.0.0.0 --port "$APP_PORT"

