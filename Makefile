PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
UVICORN := $(VENV)/bin/uvicorn

.PHONY: help venv install-web install-step4 run-web test lint-py step9-eval

help:
	@echo "Available targets:"
	@echo "  make venv          - create virtualenv"
	@echo "  make install-web   - install Step11 web dependencies"
	@echo "  make install-step4 - install Step4 UIE dependencies"
	@echo "  make run-web       - run Step11 web service on APP_PORT (default 18081)"
	@echo "  make test          - run unit tests under 00_整理记录/tests"
	@echo "  make lint-py       - syntax check for langgraph_qa"
	@echo "  make step9-eval    - run Step9 eval pipeline"

venv:
	$(PYTHON) -m venv $(VENV)

install-web:
	$(PIP) install -U pip
	$(PIP) install -r requirements-web.txt

install-step4:
	$(PIP) install -r requirements-step4.txt

run-web:
	APP_PORT=$${APP_PORT:-18081} bash 00_整理记录/scripts/run_step11_langgraph_server.sh

test:
	$(PYTHON) -m unittest discover -s 00_整理记录/tests -p 'test_*.py'

lint-py:
	$(PYTHON) -m py_compile langgraph_qa/server.py langgraph_qa/workflow.py

step9-eval:
	$(PYTHON) 00_整理记录/scripts/run_step9_neo4j_eval.py --overwrite
	$(PYTHON) 00_整理记录/scripts/run_step9_query_eval.py
	$(PYTHON) 00_整理记录/scripts/run_step9_simulation.py
	$(PYTHON) 00_整理记录/scripts/eval_step9_gate.py
