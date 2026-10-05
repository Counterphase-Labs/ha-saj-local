# Scaffold Project Foundation

## Plan Metadata

- **Revision:** 4
- **Status:** Approved
- **Last revised:** 2026-10-05
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Approval record:** Revision 4 approved by the user on 2026-10-05.

## Outcome And Acceptance

The repository gains a working, empty foundation covering every deliverable named in the requirements, each as a skeleton: the Home Assistant integration, the SAJ library sub-package, the standalone Modbus mock service, a Lovelace frontend package, both Playwright tiers, lint, type checking, tests with coverage gates, a Docker development environment and GitHub workflows.

The work is accepted when:

1. `make setup` followed by `make ci` passes on a clean checkout.
2. `uv run pytest`, `uv run mypy`, `uv run ruff check .` and `uv run ruff format --check .` each pass from the repository root with no extra arguments, because the third-party reusable workflows invoke exactly those commands.
3. The SAJ library tests and the Modbus mock tests pass in an environment where `homeassistant` is not installed.
4. An import of `homeassistant` under `custom_components/saj_modbus/saj/`, or of `homeassistant` or `custom_components` under the mock, fails `make ci`.
5. `make up` starts Home Assistant with the integration mounted alongside the mock container, and the integration can be added through the UI.
6. The controlled Playwright suite loads the built frontend asset, and the Home Assistant Playwright suite adds the integration in a clean containerised instance.
7. No file contains an inline lint, type or coverage bypass.

## Decisions Recorded

| Topic | Decision | Source |
| --- | --- | --- |
| Toolchain location | `uv` and `npm` run on the host. Home Assistant, the mock and the Home Assistant Playwright tier run in Docker. | User, 2026-10-05 |
| CI | Own jobs run the make targets; the `roquerodrigo/workflows` reusable workflows run in addition. | User, 2026-10-05 |
| SAJ library location | Sub-package `custom_components/saj_modbus/saj/` with a lint gate. | User, 2026-10-05 |
| Lint exemptions | The bypass ban covers configuration as well as inline comments. The configuration-level exemptions listed in Phase 2 are permitted for now as a temporary exception. | User, 2026-10-05 |
| Scope | Everything in the requirements, as skeletons. | User, 2026-10-05 |
| Plan style | The plan gives concrete direction and does not point at another repository. | User, 2026-10-05 |
| Release workflow | Not included; added with the first release. | Default, not objected to |
| Dependency updates | Renovate, with Home Assistant pins excluded because they are bumped together by hand. | Default, not objected to |
| Licence | MIT, `Copyright (c) 2026 Carl Sutton @dogmatic69`. | Default, not objected to |

### Approved Deviations From Requirements

- "Development in completely isolated docker environment" is not met by the host toolchain. Approved by the user on 2026-10-05.
- The lint-bypass ban is not fully met while the `tests/**` rule exemptions and the mypy `tests.*` override in Phase 2 are in place. Approved by the user on 2026-10-05 as temporary. Tests are therefore not required to carry type hints yet, which also departs from `code-style.md`.

## Boundaries

- No device functionality: no Modbus access or listener, no entities, no platforms, no options flow.
- Each skeleton contains the smallest unit that lets its toolchain, tests and gates run for real. Nothing is added in anticipation of later features.
- The integration does not register or serve the frontend asset yet; that arrives with the first real card.
- The template files deleted from the working tree are left alone. `README.md`, `LICENSE`, `.gitignore`, `.gitattributes`, `hacs.json` and `config/configuration.yaml` are written fresh at the same paths.
- No git index or history operations.

## Layout

```text
custom_components/saj_modbus/            integration
custom_components/saj_modbus/saj/        SAJ library (no Home Assistant code)
custom_components/saj_modbus/frontend/   built frontend asset (generated, committed)
modbus_mock/                             standalone mock service
    Dockerfile
    saj_modbus_mock/
frontend/                                Lovelace frontend source and browser tests
tests/integration/                       integration tests
tests/saj/                               library tests
tests/modbus_mock/                       mock tests
tests/playwright/                        Home Assistant Playwright harness
```

## Design Notes

### SAJ library import name

Python executes `custom_components/saj_modbus/__init__.py` before any sub-package of it, and that file must import Home Assistant. The library therefore cannot be imported as `custom_components.saj_modbus.saj` in an environment without Home Assistant.

- The integration imports the library relatively (`from .saj import ...`).
- Library modules import each other relatively only.
- Library tests import it as the top-level package `saj`, made importable by adding `custom_components/saj_modbus` to pytest's `pythonpath`.
- Integration tests never import `saj` by its top-level name, and library tests never import `custom_components`. This keeps the two module identities from meeting in one test.

### Mock independence

The mock is its own top-level package, `saj_modbus_mock`, in its own directory with its own Dockerfile whose build context is `modbus_mock/` alone. It shares no code with the integration or the SAJ library. Tests import it through a `modbus_mock` entry in pytest's `pythonpath`.

### Isolation gates

- **Lint gate (import-linter):** `forbidden` contracts with `include_external_packages = true`. Verified to work with the `custom_components` namespace package on import-linter 2.15.
- **Isolated test run:** library and mock tests run in a second virtual environment built from a dependency group that excludes Home Assistant. For the library this also catches an import of the surrounding integration, because a relative import above the top-level `saj` package fails there.

### Coverage

- **Python:** one root `uv run pytest` run measures line and branch coverage for `custom_components/saj_modbus` (library included) and `modbus_mock/saj_modbus_mock`, and enforces 100 percent. The isolated run uses `--no-cov`; it proves isolation and does not gate coverage.
- **Frontend:** vitest thresholds for lines, functions, statements and branches are all 100.

### Version pins

| Item | Pin |
| --- | --- |
| Python | 3.14 (`requires-python = ">=3.14.2"`) |
| Home Assistant | 2026.9.3 |
| `pytest-homeassistant-custom-component` | 0.13.366 (its `requires_dist` lists `homeassistant==2026.9.3`; verified on PyPI) |
| Node | 22 |
| Playwright | 1.63.0, with container image `mcr.microsoft.com/playwright:v1.63.0-noble` |

## Phases

### Phase 1 — Repository Hygiene

- `.editorconfig`:

  ```ini
  root = true

  [*]
  charset = utf-8
  end_of_line = lf
  insert_final_newline = true
  trim_trailing_whitespace = true
  indent_style = space
  indent_size = 4

  [*.md]
  trim_trailing_whitespace = false

  [*.{yaml,yml,json,toml}]
  indent_size = 2

  [Makefile]
  indent_style = tab
  ```

- `.gitattributes`: `* text=auto eol=lf`.
- `.gitignore` entries: `__pycache__`, `.pytest*`, `*.egg-info`, `*/build/*`, `*/dist/*`, `**/coverage/`, `**/node_modules/`, `**/playwright-report/`, `**/test-results/`, `.coverage`, `coverage.xml`, `.DS_Store`, `.vscode`, `.ruff_cache`, `.mypy_cache`, `.complexipy_cache`, `.venv`, `.venv-isolated`, `.env`, `.claude`, `CLAUDE.md`, `.opencode`, `.codex`, `config/*` with `!config/configuration.yaml`, and `compose.override.yaml`.
- `.dockerignore` entries: `.git`, `.venv`, `.venv-isolated`, `config`, `frontend/coverage`, `frontend/node_modules`, `frontend/playwright-report`, `frontend/test-results`, `**/__pycache__/`, `**/*.py[cod]`.
- `LICENSE`: the standard MIT text with `Copyright (c) 2026 Carl Sutton @dogmatic69`.
- `README.md`: what the project is, that it is unreleased, and a table of the make targets from Phase 7.
- `.github/CODEOWNERS`: `* @dogmatic69`.
- `.github/PULL_REQUEST_TEMPLATE.md` with four sections: Summary; Type of change (bug fix, new feature, refactor, documentation, tooling); Test plan (`make ci` passes; all translation locales updated when user-facing strings changed); Checklist (`AGENTS.md` or README updated when architecture or workflow changed).
- `.github/ISSUE_TEMPLATE/config.yml`: `blank_issues_enabled: false`.
- `.github/ISSUE_TEMPLATE/bug.yml`: a form with required fields for System Health details, a checklist (debug logging enabled, template completed, single issue, not a duplicate), a description, reproduction steps and debug logs rendered as text, plus an optional diagnostics dump field.
- `.github/ISSUE_TEMPLATE/feature_request.yml`: a form with a checklist (template completed, single request, not a duplicate) and required fields for the problem, the desired solution, alternatives considered and additional context.
- `.pre-commit-config.yaml`: local hooks `uv run ruff format`, `uv run ruff check --fix` (both for Python files, serial) and `uv run mypy` (no filenames passed); plus `pre-commit-hooks` v6.0.0 with `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-json`, `check-toml`, `check-merge-conflict` and `mixed-line-ending --fix=lf`.
- `.github/renovate.json`: extends `config:recommended`; weekly schedule; one group each for GitHub Actions, Python, npm and Docker updates; a package rule with `enabled: false` matching `homeassistant`, `pytest-homeassistant-custom-component` and `ghcr.io/home-assistant/home-assistant`.

### Phase 2 — Python Tooling

`pyproject.toml` is the single source for these settings; they are described here rather than quoted so that the plan is not a copy of the file.

Project and uv:

- `[project]`: name `home-assistant-saj-modbus`, version `0.1.0`, a one-line description, `requires-python = ">=3.14.2"`.
- `[tool.uv]`: `package = false`, because the repository is a custom integration and not an installable package.

Dependency groups, every entry pinned exactly:

| Group | Contents |
| --- | --- |
| `test` | `pytest` 9.0.3, `pytest-asyncio` 1.4.0, `pytest-cov` 7.1.0. This is the isolated environment; runtime dependencies of the library and the mock join it when they exist. |
| `dev` | includes the `test` group, plus `homeassistant` 2026.9.3, `pytest-homeassistant-custom-component` 0.13.366, `pre-commit` 4.6.2 |
| `lint` | `ruff` 0.16.4, `mypy` 2.3.1, `complexipy` 8.0.1, `jscpd` 5.2.0, `import-linter` 2.15 |

Pytest (`[tool.pytest.ini_options]`):

- `asyncio_mode` is `auto`; `testpaths` is `tests`.
- `pythonpath` lists the repository root, `custom_components/saj_modbus` and `modbus_mock`.
- `addopts` measures coverage for `custom_components/saj_modbus` and `modbus_mock/saj_modbus_mock`, enables branch coverage, reports missing lines in the terminal, and fails under 100.

Mypy (`[tool.mypy]`):

- Python 3.14; `files` lists `custom_components/saj_modbus` and `modbus_mock/saj_modbus_mock`.
- Missing imports are ignored and followed imports are silent.
- Enabled checks: strict optional, no implicit optional, redundant casts, unused ignores, unreachable code, untyped definitions checked and disallowed, generic `Any` disallowed.
- An override for `tests.*` turns off the two untyped-definition settings (temporary exception, see Approved Deviations).

Ruff (`[tool.ruff]`):

- Target `py314`; the formatter excludes Markdown files.
- Lint selects `ALL` and ignores `ANN401` (`typing.Any` is needed at Home Assistant boundaries), `D` (docstrings are not required), `COM812` and `ISC001` (both conflict with the formatter) and `CPY001` (no copyright headers).
- isort treats `saj` and `saj_modbus_mock` as first-party.
- pytest-style fixtures are written without parentheses; pyupgrade keeps runtime typing; McCabe complexity limit is 20.
- `tests/**` additionally ignores `S101`, `S105`, `S106`, `ANN`, `ARG001`, `PLC0415`, `SLF001` and `PLR2004` (temporary exception, see Approved Deviations).

Complexipy (`[tool.complexipy]`): same paths as mypy, maximum complexity 20, cache directory `.complexipy_cache`, colour off.

Import-linter (`[tool.importlinter]`): root packages `custom_components.saj_modbus` and `saj_modbus_mock`, external packages included, and two `forbidden` contracts:

| Contract | Source | Forbidden |
| --- | --- | --- |
| SAJ library does not import Home Assistant | `custom_components.saj_modbus.saj` | `homeassistant` |
| Modbus mock is standalone | `saj_modbus_mock` | `homeassistant`, `custom_components` |

Also:

- `.jscpd.json`: `"gitignore": true`, `"ignore": ["**/package-lock.json"]`, `"minLines": 5`, `"minTokens": 50`, `"mode": "mild"`.
- `uv.lock`: generated by `uv sync --group dev --group lint`, committed.

### Phase 3 — Integration And Library Skeleton

Under `custom_components/saj_modbus/`:

- `manifest.json`: domain `saj_modbus`, name `SAJ Modbus`, `codeowners: ["@dogmatic69"]`, `config_flow: true`, documentation `https://github.com/dogmatic69/home-assistant-saj-modbus`, issue tracker the same URL with `/issues`, `integration_type: "hub"`, `iot_class: "local_polling"`, `requirements: []`, `version: "0.1.0"`. No `single_config_entry`, because the requirements assume several Modbus systems.
- `const.py`: `DOMAIN`.
- `__init__.py`: `async_setup_entry` and `async_unload_entry`, both succeeding without side effects.
- `config_flow.py`: a config flow whose user step shows an empty confirmation form and, on submit, creates an entry titled `SAJ Modbus` with no data.
- `translations/en.json`: title and description for the user step.
- `saj/__init__.py`: empty.

Tests:

- `tests/__init__.py`, `tests/integration/__init__.py`, `tests/saj/__init__.py`, `tests/modbus_mock/__init__.py`: empty.
- `tests/integration/conftest.py`: an autouse fixture that requests `enable_custom_integrations`. Do not declare `pytest_plugins`; the Home Assistant test plugin loads through its entry point, and `tests/` must stay importable without Home Assistant.
- `tests/integration/test_init.py`: a config entry reaches the loaded state after setup and the not-loaded state after unload.
- `tests/integration/test_config_flow.py`: starting the user flow returns a form; submitting it creates an entry.
- `tests/saj/test_import.py`: the library package imports. Its value is that it runs where Home Assistant is absent.

### Phase 4 — Modbus Mock Skeleton

Under `modbus_mock/`:

- `saj_modbus_mock/__init__.py`: empty.
- `saj_modbus_mock/service.py`: an asynchronous service that starts, runs until asked to stop, and stops cleanly. It opens no socket.
- `saj_modbus_mock/__main__.py`: runs the service and requests a stop on `SIGTERM` or `SIGINT`.
- `Dockerfile`:

  ```dockerfile
  FROM python:3.14-slim

  RUN useradd --system --no-create-home mock
  WORKDIR /app
  COPY saj_modbus_mock ./saj_modbus_mock
  USER mock

  CMD ["python", "-m", "saj_modbus_mock"]
  ```

  Pin the base image by the digest current at implementation time. There is no dependency installation step until the mock has a dependency.

Tests in `tests/modbus_mock/`:

- `test_service.py`: the service keeps running until a stop is requested and then returns.
- `test_main.py`: the entry point stops the service when the process receives a termination signal.

### Phase 5 — Frontend Skeleton

Under `frontend/`:

- `package.json`: name `saj-modbus-frontend`, private, `"type": "module"`, `engines.node >= 22`. Scripts: `build` (`vite build`), `format` (`prettier --write .`), `format:check` (`prettier --check .`), `lint` (`eslint .`), `test` (`vitest run`), `typecheck` (`tsc --noEmit`), `test:browser:controlled` and `test:browser:home-assistant` (`playwright test --config` with the matching config file). Dependency `lit` 3.3.3. Development dependencies: `@eslint/js` 10.0.1, `@playwright/test` 1.63.0, `@types/node` 24.10.1, `@vitest/coverage-v8` 5.0.0, `eslint` 10.10.0, `jsdom` 30.0.1, `prettier` 3.9.6, `typescript` 6.0.3, `typescript-eslint` 8.70.0, `vite` 8.3.0, `vitest` 5.0.0. All pinned exactly; `package-lock.json` committed.
- `.prettierignore`: `coverage`, `node_modules`, `playwright-report`, `test-results`.
- `tsconfig.json`: target and lib `ES2022` with `DOM` and `DOM.Iterable`, module `ESNext`, `moduleResolution: "Bundler"`, `strict`, `noUncheckedIndexedAccess`, `noUnusedLocals`, `noUnusedParameters`, `verbatimModuleSyntax`, `useDefineForClassFields: false`, types `vitest/globals` and `node`; includes `src`, `tests` and the root config files.
- `eslint.config.js`: `@eslint/js` recommended plus `typescript-eslint` `strictTypeChecked` and `stylisticTypeChecked`, using the project service; ignores `coverage`; rule `@typescript-eslint/consistent-type-imports` set to error.
- `vite.config.ts`: library build with entry `src/card.ts`, ES format, `emptyOutDir: true`, `outDir` `../custom_components/saj_modbus/frontend`, `manifest: "asset-manifest.json"`, entry file name `saj-modbus-card-[hash].js`. Vitest: `jsdom` environment, `tests/**/*.test.ts`, v8 coverage enabled with text reporter and thresholds of 100 for lines, functions, statements and branches.
- `src/card.ts`: one Lit custom element, `saj-modbus-card`, that accepts a Lovelace card configuration through `setConfig` and renders its title inside `ha-card`. A configuration without a title is rejected with an error.
- `tests/card.test.ts`: the element renders the configured title; a configuration without a title is rejected.
- `playwright.controlled.config.ts`: `testDir` `tests/browser/controlled`, fully parallel, `outputDir` `test-results/controlled`, list and HTML reporters (HTML to `playwright-report/controlled`), headless Chromium, screenshots only on failure, traces retained on failure.
- `playwright.home-assistant.config.ts`: `testDir` `tests/browser/home-assistant`, not parallel, `forbidOnly`, `outputDir` `test-results/home-assistant`, list and HTML reporters (HTML to `playwright-report/home-assistant`), test timeout 120 s, expect timeout 15 s, `baseURL` from `HOME_ASSISTANT_URL` defaulting to `http://homeassistant:8123`, action timeout 15 s, navigation timeout 30 s, headless Chromium, screenshots only on failure, traces retained on failure.
- `tests/browser/support/test.ts`: exports `expect` and a `test` extended with an automatic `browserFailures` fixture. The fixture records console errors, uncaught page errors and failed requests, and fails the test if any were recorded. It ignores the console message "The AudioContext was not allowed to start" and failed requests to `basemaps.cartocdn.com`, both of which a stock Home Assistant frontend produces.
- `tests/browser/controlled/card.spec.ts`: locates the built `saj-modbus-card-*.js` file in `custom_components/saj_modbus/frontend`, injects it into a blank page as a module script, mounts the element with a controlled configuration, and expects the title to be visible.
- `tests/browser/home-assistant/configuration.spec.ts`: one test that
  1. opens `/`, completes onboarding (create the account, accept the default location and country, skip analytics, finish) and confirms the URL no longer contains `onboarding`;
  2. opens Settings, then Devices & services, then Add integration, searches for `SAJ Modbus` and selects it;
  3. submits the confirmation form and closes the success dialog;
  4. expects `SAJ Modbus` to be listed among the configured integrations.

  Locate elements by role and accessible name.

The built asset under `custom_components/saj_modbus/frontend/` (the hashed JavaScript file and `asset-manifest.json`) is committed so that a HACS installation contains it.

### Phase 6 — Docker Environments

Development:

- `compose.yaml`:

  ```yaml
  services:
    homeassistant:
      image: ghcr.io/home-assistant/home-assistant:2026.9.3
      ports:
        - "8123:8123"
      environment:
        TZ: UTC
        PYTHONPYCACHEPREFIX: /tmp/saj_modbus_pycache
      volumes:
        - ./config:/config
        - ./custom_components/saj_modbus:/config/custom_components/saj_modbus:ro
      tmpfs:
        - /config/custom_components/saj_modbus/__pycache__
      healthcheck:
        test:
          - CMD
          - python
          - -c
          - >-
            import urllib.request;
            urllib.request.urlopen('http://127.0.0.1:8123/', timeout=5)
        interval: 10s
        timeout: 5s
        retries: 12
        start_period: 30s
      restart: unless-stopped

    modbus-mock:
      build:
        context: ./modbus_mock
      restart: unless-stopped
  ```

- `compose.override.yaml.example`: overrides the `homeassistant` published port to `8124:8123` using `!override` and sets `TZ`, as a template for the ignored `compose.override.yaml`.
- `config/configuration.yaml`: `default_config:`, and a `logger` block with default `info` and `custom_components.saj_modbus: debug`.
- `hacs.json`: `"name": "SAJ Modbus"`, `"homeassistant": "2026.9.3"`, `"hacs": "2.0.5"`. No zip release keys until the release workflow exists.

Home Assistant Playwright tier:

- `Dockerfile.playwright-home-assistant`: a first stage from `mcr.microsoft.com/playwright:v1.63.0-noble` that runs `npm ci` and `npm run build` in `frontend/`; a final stage from `ghcr.io/home-assistant/home-assistant:2026.9.3` that copies `tests/playwright/home-assistant/configuration.yaml` to `/config/configuration.yaml`, copies `custom_components/saj_modbus` to `/config/custom_components/saj_modbus`, and copies the freshly built `frontend` directory over the integration's copy.
- `Dockerfile.playwright-runner`: from `mcr.microsoft.com/playwright:v1.63.0-noble`, runs `npm ci` in `frontend/`, copies the frontend sources, installs `tests/playwright/run-browser-tests.sh` as its command.
- `compose.playwright.yaml`: a `homeassistant` service built from the first Dockerfile, with the same health check on a 5 s interval and 24 retries and a named volume for `/config`; a `playwright` service built from the second, depending on `homeassistant` being healthy, with `HOME_ASSISTANT_URL=http://homeassistant:8123`, `PLAYWRIGHT_RESULT_UID` and `PLAYWRIGHT_RESULT_GID` passed through, `init: true`, `ipc: host`, and `frontend/playwright-report` and `frontend/test-results` bind-mounted.
- `tests/playwright/run-home-assistant.sh`: a POSIX shell script that uses a compose project name unique to the process (`saj-modbus-playwright-$$`), builds the images, starts `homeassistant` and waits for health, runs the `playwright` service, and on exit always tears the project down with volumes and locally built images. On failure it first writes the Home Assistant container log to `frontend/test-results/home-assistant/home-assistant.log`. It exports the caller's user and group IDs for the runner and exits with the test status.
- `tests/playwright/run-browser-tests.sh`: runs `npm run test:browser:home-assistant`, then changes ownership of the report and result directories to the passed user and group IDs so the host user can read them, and exits with the test status.
- `tests/playwright/home-assistant/configuration.yaml`: a `homeassistant` block with a name, latitude, longitude, elevation, metric units, currency and time zone, so onboarding needs no location lookup; and `default_config:`.

### Phase 7 — Make Targets

| Target | Action |
| --- | --- |
| `setup` | `uv sync --group dev --group lint`; in `frontend/`, `npm ci` and `npx playwright install chromium` |
| `up` | `docker compose up -d --build --remove-orphans --force-recreate` |
| `down` | `docker compose down` |
| `logs` | `docker compose logs -f homeassistant` |
| `lint` | `uv run ruff format --check .`; `uv run ruff check .`; `uv run mypy`; `PYTHONPATH=.:modbus_mock uv run lint-imports`; `uv run complexipy --snapshot-ignore=true --failed=true` |
| `copy-paste` | `uv run jscpd --exit-code 1 --no-colors --no-tips .` |
| `test` | `uv run pytest` |
| `test-isolated` | `UV_PROJECT_ENVIRONMENT=.venv-isolated uv run --only-group test pytest --no-cov tests/saj tests/modbus_mock` |
| `python-ci` | `lint`, `copy-paste`, `test`, `test-isolated`, in that order |
| `frontend-check` | in `frontend/`: `npm run format:check`, `npm run typecheck`, `npm run lint`, `npm run test` |
| `frontend-build` | in `frontend/`: `npm run build` |
| `test-browser-controlled` | depends on `frontend-build`; in `frontend/`: `npm run test:browser:controlled` |
| `test-browser-home-assistant` | `tests/playwright/run-home-assistant.sh` |
| `frontend-ci` | `frontend-check`, `test-browser-controlled` |
| `release-check` | zips `custom_components/saj_modbus` into a temporary directory and fails unless the archive lists `saj_modbus/frontend/asset-manifest.json` and a `saj_modbus/frontend/saj-modbus-card-*.js` file |
| `mock-build` | `docker compose build modbus-mock` |
| `ci` | `python-ci`, `frontend-ci`, `release-check`, `mock-build`, `test-browser-home-assistant` |

All targets are declared `.PHONY`.

### Phase 8 — GitHub Workflow

`.github/workflows/ci.yml`:

- Triggers: push to `main`, and pull requests.
- Concurrency group `ci-${{ github.ref }}`, cancelling in-progress runs for pull requests only.
- Top-level `permissions: contents: read`.
- Every checkout uses `persist-credentials: false`.

Jobs:

| Job | Steps |
| --- | --- |
| `python` | checkout; `roquerodrigo/workflows/actions/setup-python` with `python-version: "3.14"` and `groups: dev lint`; `make python-ci` |
| `frontend` | checkout; `actions/setup-node` with Node 22 and npm cache keyed on `frontend/package-lock.json`; `npm ci` in `frontend/`; `npx playwright install --with-deps chromium`; `make frontend-ci`; `make release-check` |
| `mock` | checkout; `make mock-build` |
| `home-assistant-smoke` | checkout; `make test-browser-home-assistant`; on failure upload `frontend/playwright-report/home-assistant` and `frontend/test-results/home-assistant` as an artifact kept for 7 days |
| `lint` | calls `roquerodrigo/workflows/.github/workflows/python-lint.yml` |
| `tests` | needs `lint`; calls `roquerodrigo/workflows/.github/workflows/python-test.yml` |
| `validate` | needs `lint`; calls `roquerodrigo/workflows/.github/workflows/home-assistant-validate.yml` with `hacs: false` |
| `hacs` | checkout; `hacs/action` with `category: integration` and `ignore: brands`, because the reusable validation workflow cannot pass `ignore` and no brand images exist yet |

Pins, each written as a commit SHA with a version comment:

| Action | SHA | Version |
| --- | --- | --- |
| `actions/checkout` | `3d3c42e5aac5ba805825da76410c181273ba90b1` | v7.0.1 |
| `actions/setup-node` | `820762786026740c76f36085b0efc47a31fe5020` | v7.0.0 |
| `actions/upload-artifact` | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` | v7.0.1 |
| `hacs/action` | `d556e736723344f83838d08488c983a15381059a` | 22.5.0 |
| `roquerodrigo/workflows` (action and reusable workflows) | `c8f4cdbb114d339ae54e35cd460ada75403d0271` | main |

## Verification

- `make setup && make ci` passes.
- Temporarily add `import homeassistant` to a file under `saj/` and under `saj_modbus_mock/`; confirm `make lint` and `make test-isolated` fail; remove both.
- `make up`; confirm the mock container stays running; add the integration through the UI; `make down` and confirm the mock exits promptly.
- The workflow can only be verified after a push. Two conditions are outside the repository: HACS validation reads the repository through the public GitHub API, so it fails on a private repository, and it requires a repository description and topics to be set on GitHub.

## Known Limitations

- The reusable `python-lint.yml` and `python-test.yml` workflows internally reference their own setup action at `@main`, so pinning the caller by SHA does not make them fully immutable.
- The Playwright onboarding steps depend on Home Assistant's UI text for the pinned version; the exact accessible names must be confirmed against the running instance during implementation.

## Revisions

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-05 | Initial draft covering the integration, library, tooling, development Home Assistant and CI. |
| 2 | 2026-10-05 | Scope decided by the user: added the Modbus mock skeleton, frontend skeleton, both Playwright tiers, their make targets and CI jobs; renamed the isolated test group and target to cover the mock. |
| 3 | 2026-10-05 | At the user's direction, removed every pointer to another repository and replaced each with concrete file content or settings. No change to scope or design. |
| 4 | 2026-10-05 | At the user's direction, replaced the quoted `pyproject.toml` with a description of its settings so the plan no longer trips copy-paste detection. No change to scope or design. |
