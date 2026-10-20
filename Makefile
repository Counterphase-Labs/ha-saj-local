RUNNER = python3 .github/scripts/check_runner.py

.PHONY: help setup up down logs ruff mypy import-lint complexipy copy-paste test-python test-modules test-isolated test-runner-processes prettier tsc eslint test-frontend build test-browser-controlled test-browser-home-assistant release-check mock-build mock-smoke validate lint test python-ci frontend-check frontend-ci ci

help:
	@$(RUNNER) --describe $(ARGS)

setup:
	@$(RUNNER) setup

up:
	@$(RUNNER) up

down:
	@$(RUNNER) down

logs:
	docker compose logs -f homeassistant

ruff mypy import-lint complexipy copy-paste test-python test-modules test-isolated test-runner-processes prettier tsc eslint test-frontend build test-browser-controlled test-browser-home-assistant release-check mock-build mock-smoke validate:
	@$(RUNNER) --forward-args $@

lint:
	@$(RUNNER) lint

test:
	@$(RUNNER) test

python-ci:
	@$(RUNNER) python-ci

frontend-check:
	@$(RUNNER) frontend-check

frontend-ci:
	@$(RUNNER) frontend-ci

ci:
	@$(RUNNER) ci
