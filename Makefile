.PHONY: help install run dev test clean format lint verify-phoenix phoenix-ui

help:
	@echo "ADK Agents Phoenix - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install      Install dependencies"
	@echo "  make dev-install  Install with dev dependencies"
	@echo ""
	@echo "Running:"
	@echo "  make run          Run the agent"
	@echo "  make dev          Run with DEBUG logging"
	@echo "  make verify-phoenix  Verify Phoenix configuration"
	@echo ""
	@echo "Quality:"
	@echo "  make test         Run tests"
	@echo "  make lint         Lint code"
	@echo "  make format       Format code"
	@echo "  make clean        Remove build artifacts"
	@echo ""
	@echo "Examples:"
	@echo "  make run-model model=claude-3-opus-20240229"
	@echo "  make run-endpoint https://my-phoenix:6006/v1/traces"

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"

run:
	python main.py

dev:
	LOG_LEVEL=DEBUG python main.py

run-model:
	PRIMARY_MODEL=$(model) python main.py

run-endpoint:
	PHOENIX_ENDPOINT=$(endpoint) python main.py

verify-phoenix:
	python verify_phoenix_config.py

test:
	pytest tests/ -v

lint:
	ruff check app/ main.py
	mypy app/ main.py || true

format:
	black app/ main.py
	isort app/ main.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info

phoenix-ui:
	@echo "Opening Phoenix UI at http://127.0.0.1:6006"
	@python -m webbrowser "http://127.0.0.1:6006" || true
