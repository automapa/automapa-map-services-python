.PHONY: help install test test-unit test-integration lint format-check typecheck compile check examples
.PHONY: docker-build docker-test docker-test-unit docker-test-integration docker-lint docker-format-check docker-typecheck docker-compile docker-check

UV      ?= uv
EXAMPLES = $(shell find examples -name '*.py' -not -name 'bootstrap.py' | sort)

help: ## Wyświetla dostępne komendy
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

install: ## Instaluje zależności (uv sync)
	$(UV) sync --extra dev

test: ## Uruchamia wszystkie testy (unit + integration)
	$(UV) run pytest tests/

test-unit: ## Uruchamia tylko testy jednostkowe
	$(UV) run pytest tests/unit/ -v

test-integration: ## Uruchamia tylko testy integracyjne
	$(UV) run pytest tests/integration/ -v

lint: ## Uruchamia linter ruff
	$(UV) run ruff check .

format-check: ## Sprawdza formatowanie kodu (ruff format)
	$(UV) run ruff format --check .

typecheck: ## Uruchamia analizę typów (mypy)
	$(UV) run mypy automapa_map_services

compile: ## Sprawdza składnię Python (compileall)
	$(UV) run python -m compileall -q automapa_map_services tests examples

check: lint format-check typecheck compile test ## Pełna weryfikacja: lint + format + typy + kompilacja + testy

examples: ## Uruchamia wszystkie przykłady jeden po drugim (wymaga .env z danymi API)
	@pass=0; fail=0; \
	for f in $(EXAMPLES); do \
		echo ">>> $$f"; \
		if $(UV) run python $$f; then \
			pass=$$((pass + 1)); \
		else \
			fail=$$((fail + 1)); \
		fi; \
		echo ""; \
	done; \
	echo "=== Summary: $$pass passed, $$fail failed ==="

docker-build: ## Buduje obraz Docker
	docker compose build

docker-test: docker-build ## Uruchamia wszystkie testy w Dockerze (wymaga .env)
	docker compose run --rm pytest

docker-test-unit: docker-build ## Uruchamia testy jednostkowe w Dockerze
	docker compose run --rm pytest-unit

docker-test-integration: docker-build ## Uruchamia testy integracyjne w Dockerze (wymaga .env)
	docker compose run --rm pytest-integration

docker-lint: docker-build ## Uruchamia ruff w Dockerze
	docker compose run --rm ruff

docker-format-check: docker-build ## Sprawdza formatowanie w Dockerze
	docker compose run --rm ruff-format-check

docker-typecheck: docker-build ## Uruchamia mypy w Dockerze
	docker compose run --rm mypy

docker-compile: docker-build ## Sprawdza składnię Python w Dockerze
	docker compose run --rm compile

docker-check: docker-build ## Pełna weryfikacja w Dockerze (lint + format + typy + kompilacja + testy)
	docker compose run --rm ruff
	docker compose run --rm ruff-format-check
	docker compose run --rm mypy
	docker compose run --rm compile
	docker compose run --rm pytest
