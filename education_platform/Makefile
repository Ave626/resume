VENV ?= .venv
PYTHON ?= $(VENV)/bin/python
UVICORN ?= $(VENV)/bin/uvicorn
ALEMBIC ?= $(VENV)/bin/alembic
RUFF ?= $(VENV)/bin/ruff

HOST ?= 127.0.0.1
PORT ?= 8000

.PHONY: install run dev worker redis compose-up compose-down compose-logs migrate migrate-down migration lint format clean

install:
	@chmod +x ./setup_env.sh
	./setup_env.sh

compose-up:
	docker compose up -d

compose-down:
	docker compose down

compose-logs:
	docker compose logs -f

run:
	$(UVICORN) app.main:app --reload --host $(HOST) --port $(PORT)

dev: run

worker:
	$(PYTHON) -m app.run_code_submission_worker

redis:
	@docker start redis 2>/dev/null || docker run -d --name redis -p 6379:6379 redis:7-alpine

migrate:
	$(ALEMBIC) upgrade head

migrate-down:
	$(ALEMBIC) downgrade -1

migration:
	@if [ -z "$(m)" ]; then echo "Error: provide migration description via m=\"name\""; exit 1; fi
	$(ALEMBIC) revision --autogenerate -m "$(m)"

lint:
	$(RUFF) check .

format:
	$(RUFF) format .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache
