.DEFAULT_GOAL := help
SHELL := /bin/bash

COMPOSE       = docker compose
UV            = uv
PYTEST        = $(UV) run pytest
COV_REPORT    = term-missing


.PHONY: help
help:
	@echo ""
	@echo "  Usage: make <target>"
	@echo ""
	@echo "  Development"
	@echo "  ─────────────────────────────────────────────"
	@echo "  install          Install all dependencies (incl. dev)"
	@echo "  run              Run app locally with uvicorn"
	@echo "  migrate          Run Alembic migrations locally"
	@echo "  migrate-create   Create new migration  (name=<name>)"
	@echo ""
	@echo "  Testing"
	@echo "  ─────────────────────────────────────────────"
	@echo "  test             Run tests"
	@echo "  test-cov         Run tests with HTML + terminal coverage"
	@echo "  test-cov-xml     Run tests with XML coverage (CI)"
	@echo ""
	@echo "  Docker"
	@echo "  ─────────────────────────────────────────────"
	@echo "  docker-build     Build Docker images (no cache)"
	@echo "  docker-up        Start containers in background"
	@echo "  docker-down      Stop and remove containers"
	@echo "  docker-restart   Rebuild and restart everything"
	@echo "  docker-logs      Tail logs for all containers"
	@echo "  docker-logs-app  Tail logs for the app container"
	@echo "  docker-ps        Show running containers"
	@echo ""

.PHONY: install
install:
	$(UV) sync --group dev

.PHONY: run
run:
	$(UV) run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

.PHONY: migrate
migrate:
	cd src && $(UV) run alembic upgrade head

.PHONY: migrate-create
migrate-create:
	cd src && $(UV) run alembic revision --autogenerate -m "$(name)"

.PHONY: test
test:
	$(PYTEST) -v

.PHONY: test-cov
test-cov:
	$(PYTEST) -v \
		--cov=src \
		--cov-report=$(COV_REPORT) \
		--cov-report=html:src/coverage_html \
		--cov-config=pyproject.toml

.PHONY: test-cov-xml
test-cov-xml:
	$(PYTEST) -v \
		--cov=src \
		--cov-report=xml:coverage.xml \
		--cov-config=pyproject.toml

.PHONY: docker-build
docker-build:
	$(COMPOSE) build --no-cache

.PHONY: docker-up
docker-up:
	$(COMPOSE) up -d

.PHONY: docker-down
docker-down:
	$(COMPOSE) down --volumes

.PHONY: docker-restart
docker-restart: docker-down docker-build docker-up

.PHONY: docker-logs
docker-logs:
	$(COMPOSE) logs -f

.PHONY: docker-logs-app
docker-logs-app:
	$(COMPOSE) logs -f app

.PHONY: docker-ps
docker-ps:
	$(COMPOSE) ps

