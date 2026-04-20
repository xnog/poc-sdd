.PHONY: run install test lint typecheck clean

VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
UVICORN := $(VENV)/bin/uvicorn

$(VENV):
	uv venv
	$(PIP) install -e ".[dev]"

install: $(VENV)

run: install
	$(UVICORN) src.main:app --reload --port 8000

test: install
	$(VENV)/bin/pytest

lint: install
	$(VENV)/bin/ruff check .

typecheck: install
	$(VENV)/bin/mypy src

clean:
	rm -rf $(VENV) .pytest_cache .mypy_cache .ruff_cache __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} +
