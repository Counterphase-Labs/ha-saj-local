.PHONY: setup up down logs build lint copy-paste test test-python test-frontend test-isolated python-ci frontend-check test-browser-controlled test-browser-home-assistant frontend-ci release-check mock-build mock-smoke ci

setup:
	uv sync --group dev --group lint
	cd frontend && npm ci
	cd frontend && npx playwright install chromium

up:
	docker compose up -d --build --remove-orphans --force-recreate

down:
	docker compose down

logs:
	docker compose logs -f homeassistant

build:
	cd frontend && npm run build

lint:
	uv run ruff format --check .
	uv run ruff check .
	uv run mypy
	PYTHONPATH=.:modbus_mock uv run lint-imports
	uv run complexipy --snapshot-ignore=true --failed=true

copy-paste:
	uv run jscpd --exit-code 1 --no-colors --no-tips .

test: test-python test-frontend test-isolated test-browser-controlled test-browser-home-assistant mock-smoke

test-python:
	uv run pytest

test-frontend:
	cd frontend && npm run test

test-isolated:
	UV_PROJECT_ENVIRONMENT=.venv-isolated uv run --only-group test pytest --no-cov tests/saj tests/modbus_mock

python-ci: lint copy-paste test-python test-isolated

frontend-check:
	cd frontend && npm run format:check
	cd frontend && npm run typecheck
	cd frontend && npm run lint
	$(MAKE) test-frontend

test-browser-controlled: build
	cd frontend && npm run test:browser:controlled

test-browser-home-assistant:
	tests/playwright/run-home-assistant.sh

frontend-ci: frontend-check test-browser-controlled

release-check:
	@set -eu; \
	temp_dir=$$(mktemp -d); \
	archive="$$temp_dir/saj_local.zip"; \
	trap 'rm -r "$$temp_dir"' 0; \
	(cd custom_components && zip -qr "$$archive" saj_local); \
	unzip -Z1 "$$archive" | grep -Eq '^saj_local/frontend/asset-manifest\.json$$'; \
	unzip -Z1 "$$archive" | grep -Eq '^saj_local/frontend/saj-local-[A-Za-z0-9_-]+\.js$$'

mock-build:
	docker compose build modbus-mock
	docker compose run --rm --no-deps --entrypoint python modbus-mock -c "import pathlib, sys; sys.exit(any(pathlib.Path('/app').rglob('*.py[cod]')) or any(pathlib.Path('/app').rglob('__pycache__')))"

mock-smoke:
	tests/modbus_mock/smoke.sh

ci: python-ci frontend-ci release-check mock-build mock-smoke test-browser-home-assistant
