# Trim Check Output For Agents

## Plan Metadata

- **Revision:** 3
- **Status:** Approved
- **Roadmap item:** None. Tooling for agents and developers.
- **Last revised:** 2026-10-20
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Source design:** the check runner of the sibling project ha-energy-mpc (its plan "Token-Efficient Tooling", revision 3, and the later fix that kills check tools with the runner). The runner, parsers, settings and rules below are copied from ha-energy-mpc as closely as the requirements of this project allow. Every difference from ha-energy-mpc is named under "Differences From ha-energy-mpc".

## Outcome And Scope

Every check an agent or developer runs prints only what is needed to understand the result, whether `make ci` runs the check or an agent runs the tool directly. A passing step prints one checkbox line. A failing step prints the checkbox line plus only the failure details needed to fix the failure. An optional verbosity flag restores the raw tool output. The same make targets run locally and in GitHub workflows.

| Need | Today | With this plan |
| --- | --- | --- |
| Know whether `make ci` passed | Raw output of every tool, often thousands of lines | One `[x]` or `[ ]` line per step and one final result line |
| Find every failure | `make ci` stops at the first failing command | Every selected step runs, and every failure is reported in one run |
| Fix a failure | Search the raw output by hand with `grep` and `tail` | `file:line message` per finding, failing test IDs with short tracebacks |
| Run one tool on a few files | Run the tool directly with hand-made trimming | A make target per tool, with `ARGS` for paths and options |
| Check one test file | `--no-cov`, or a whole-package coverage failure | The 100 % gate applied to the module the test file tests, with the module's other test files run alongside |
| Prove each module is covered by its own tests | Never checked; the whole-suite run counts coverage from any test | `make ci` gates every module at 100 % from the test files of that module alone |
| Know GitHub runs what `make ci` runs | GitHub runs a hand-picked list of targets | GitHub runs `make ci` itself |
| Tell a hang from a failure | A killed run looks like a failed run | A timeout, a signal or a missing tool is reported as such |
| Stop a runaway test run | Killing make can leave the tool running | Stopping the runner stops the tool's whole process group, giving the tool time to clean up first; every tool has a memory limit |

Included:

- A standard-library check runner, its step definitions, its parsers and the subset coverage scope, all in `.github/scripts/`, with unit tests.
- Quiet output set in each tool's own configuration.
- The `Makefile` rewritten around the runner, keeping every target name the requirements fix.
- A per-module coverage step, `test-modules`, in `make ci` and `make test`.
- `.github/workflows/ci.yml` running `make ci` in one job, so GitHub runs every step of `make ci`.
- A unit test file for every module with logic that has none, and the tests each module needs to reach 100 % from its own test files.
- The repair texts hassfest forced out of `translations/en.json` moved into the fix-flow confirm steps, with the removed translation test cases restored.
- A user-level Claude Code `env` block for the quiet git, docker compose and uv settings.
- The `tests/` folders renamed to the layout under "Test Folder Layout".
- `AGENTS.md`, `documentation/development.md` and `CONTRIBUTING.md` updated.

Not changed: the integration, the SAJ library, the Modbus mock and the cards, except for a serious issue the new checks expose (see Decisions). Existing tests are not rewritten; test files move only as "Test Folder Layout" sets out (see Decisions). The external `roquerodrigo/workflows` jobs (lint, tests, validate) and the `hacs` job are unchanged.

## Why

A review of 166 agent sessions in ha-energy-mpc found that agents ran the lint and test tools directly far more often than through make, and rebuilt the trimming by hand on almost every call (about 1,300 `| tail`, 800 `| grep` and 850 `--no-cov`). A clean pytest run printed about 60 KB, nearly all of the output noise.

The agent sessions of this project show the same pattern at an earlier stage:

| Pattern | Calls |
| --- | --- |
| `\| grep` on command output | 234 |
| `\| tail` on command output | 129 |
| Playwright, Vitest, jscpd, tsc, ESLint and Prettier run directly | about 200 |
| `make ci` | 31 |
| `--no-cov` | 6 |

The current `Makefile` stops at the first failing command and prints raw tool output.

## Requirements

Non Functional section of `../requirements.md`:

- All commands are exposed as make targets. One `make build` builds everything, with no build target per part. One `make test` runs every test suite, and each suite has its own target. One `make ci` runs every check, and the partial targets that make up `make ci` stay.
- All testing and verification can run in GitHub workflows through the same make targets.
- 100 % unit test coverage for all lines, statements and paths, from unit tests alone.
- A unit test exercises one module through its own public interface, with collaborators replaced by stubs, and does not start processes or servers, open sockets, read project files or depend on real time.
- Integration tests are only critical-path smoke tests, are few, are kept separate from the unit tests and do not count toward coverage.
- The SAJ library can be tested completely isolated from Home Assistant.
- No `noqa` or other inline lint or test bypass.

## Requirement Changes

None.

## Decisions

- **Copy, then adapt.** The runner, parsers, subset coverage scope, tool configuration, agent rules and process safety come from ha-energy-mpc. Changes are limited to the differences listed below.
- **Only noise is removed, never content.** Colour codes, progress bars, banners, hints, decoration, passing-test lists and fully covered files are noise. Error messages, tracebacks, warnings and the location of every finding are content and are never cut. Generated files (the built card bundle and the lock files) are the one exception: their text diff is hidden because the text cannot be reviewed and the source is in the same diff.
- **Placement.** The runner lives in `.github/scripts/`, and make is the entry point.
- **Target names follow the requirements.** `build`, `test`, `test-python`, `test-frontend`, `test-isolated`, `test-browser-controlled`, `test-browser-home-assistant`, `lint`, `python-ci`, `frontend-check`, `frontend-ci`, `ci`, `copy-paste`, `release-check`, `mock-build`, `mock-smoke`, `setup`, `up`, `down` and `logs` keep their names. Per-tool targets are added for the lint tools. No alias targets are added.
- **No `--no-cov`.** `test-isolated` drops `--no-cov` and gates coverage on the modules its test files test, in the same way as any subset run.
- **Every check runs everywhere.** `make ci` runs every check and test step, and GitHub runs `make ci` itself in one job. No check exists that only runs by hand.
- **Per-module coverage gate.** `requirements.md` asks for 100 % coverage from unit tests alone, one module per test file. The `test-modules` step runs, for each module, every unit test file mapped to the module, and requires 100 % line and branch coverage of that module alone. A module tested across several files (for example `coordinator.py` by `test_coordinator.py`, `test_coordinator_power.py` and `test_coordinator_write.py`) passes when those files together cover the module; coverage from the tests of other modules does not count. A module with logic and no unit test file fails the step. A module with no logic (no function, no method and no branch), such as an empty module or a module that only holds a data table, is skipped, because the requirements forbid tests of constants.
- **Existing tests are not rewritten.** No existing test file is rewritten, merged, split or deleted. Test files move only to the folders "Test Folder Layout" sets out, with no change other than the import paths the move requires. A unit test is added only where `make ci` fails without the test, and only as an addition to the test file named after the module, or as a new test file named after the module when the module has none. Because `test-modules` is part of `make ci`, every module below 100 % from its own test files gets the missing tests.
- **Shared test files.** A test file maps to the module the file tests. A shared test file is used only for shared functionality, such as `tests/saj/test_control_hs3.py` and `tests/saj/test_h2_settings.py`, which test the shared `Control` with one model each.
- **Product code changes only for a serious issue.** The integration, the SAJ library, the Modbus mock and the cards change only when the new checks expose a serious issue, and the change is limited to exactly that issue. Any other finding, including a hassfest finding from the local `validate` step, is reported to the user instead of fixed. A hassfest fix keeps every user-facing text: text hassfest does not allow in one place moves to the place hassfest allows.
- **Test folder layout.** `tests/` holds exactly `saj`, `saj-integration`, `mock`, `mock-integration`, `playwright` and `scripts`, as "Test Folder Layout" sets out. No other test folder exists.
- **Runner tests are split into unit tests and integration tests.** Unit tests of the runner, the steps, the parsers, the scope and the release check live in `tests/scripts/`, replace processes, signals, the clock and the file system with stubs, and give the 100 % coverage of `.github/scripts`. The ha-energy-mpc tests that start real processes (output capture, the timeout report, the signal report and the process-group kill when the runner is stopped) are integration tests in `tests/scripts/test_runner_processes.py`, run by their own suite target `test-runner-processes`, kept out of the unit test run and out of coverage.
- **HACS stays external.** `make validate` runs hassfest against the working tree and runs in GitHub as part of `make ci`. HACS validation reads the pushed repository, so HACS validation stays in the existing `hacs` workflow job only. The external `lint`, `tests` and `validate` jobs stay as they are.
- **Agent environment is user-level.** The git, docker compose and uv settings for agent shells go into the `env` block of the user-level Claude Code settings file (`~/.claude/settings.json`), which applies to every project. No project settings file and no `.claude` symlink are added to this repository. The runner sets the docker compose and uv settings for its own steps, so make targets are quiet for a human too.
- **No `pytest-timeout`.** As in ha-energy-mpc, runaway runs are stopped by the runner's process-group kill, per-step timeouts and the memory limit, not by a per-test timeout.
- **No comments.** Scripts and configuration follow `../code-style.md` and carry no comments or docblocks.

## Differences From ha-energy-mpc

| Area | ha-energy-mpc | This plan |
| --- | --- | --- |
| Target names | Tool names (`pytest`, `vitest`, `frontend-build`, `browser-*`) | Existing names fixed by the requirements (`test-python`, `test-frontend`, `build`, `test-browser-*`) |
| Extra steps | none | `import-lint`, `test-isolated`, `test-runner-processes`, `mock-build`, `mock-smoke` |
| Runner tests | One test set; some tests start real processes and use real time, and count toward coverage | Unit tests with stubs give the coverage; the real-process tests are separate integration tests outside coverage |
| Coverage | 90 % lines | 100 % lines and branches (`--cov-branch`); the pytest coverage parser reads the branch columns |
| Subset gaps | Recorded on the roadmap | `test-modules` in `make ci` gates every module on its own test files; missing tests are added |
| GitHub | Workflow steps per target | One job runs `make ci` |
| Test layout | Flat `tests/` | `tests/saj`, `tests/saj-integration`, `tests/mock` (with `profiles/` and `simulation/`), `tests/mock-integration`, `tests/playwright`, `tests/scripts` |
| Agent environment | Tracked project file plus an untracked `.claude/settings.json` symlink | User-level `env` block |
| `up` | `up` plus a readiness script | The existing `up` command, run through the runner; no `restart` target and no readiness script |
| Hypothesis | Statistics turned off | Not used in this project |

## Design

### Runner

`.github/scripts/check_runner.py` is copied unchanged in behaviour. The runner:

- runs every selected step even after one fails, then exits non-zero when any step failed;
- prints one line per step, for example `[x] test-python  1840 passed  100.0% cov  41s`, followed by the step's details, and `[ ]` with the failure details for a failing step;
- prints a final line, for example `result: 17 of 18 steps passed  failed: mypy`;
- reports a step killed by a signal, a timeout or a missing tool as `killed by signal SIGKILL`, `timed out after 600s` or `tool not found: <tool>`, distinct from a test or lint failure, followed by the raw output of the step;
- falls back to the non-empty raw output lines (npm banners removed) when a step fails and the parser found no details;
- flushes standard output after every step's report and before the runner stops itself on a stop signal, so a run whose output goes to a pipe or a file, such as the GitHub job log or an agent's background run, shows each step as the step finishes and keeps every finished step when the run is stopped;
- when `GITHUB_ACTIONS` is set, puts each step's raw output in a collapsed `::group::` and emits one `::error file=…,line=…::` annotation per finding, or one `::error title=<step>::` line when the step has no findings;
- runs required steps first (`test-browser-controlled` requires `build`) and passes `ARGS` only to the step the target names.

### Process Safety

Copied from the ha-energy-mpc fix that kills check tools with the runner:

- Each tool starts in its own session so a timeout or a stopped runner reaches the whole tool tree.
- A tool is stopped in two stages, both on a timeout and when the runner receives SIGTERM, SIGINT or SIGHUP: the runner sends SIGTERM to the tool's whole process group, waits up to a grace period of 60 s (`STOP_GRACE_SECONDS`) for the tool to exit, and then sends SIGKILL to the group, which ends anything still running. The grace period exists because `tests/playwright/run-home-assistant.sh` and `tests/mock-integration/smoke.sh` remove their Docker compose projects, containers, volumes and images in a `trap … EXIT HUP INT TERM`, and a shell trap never runs on SIGKILL. The grace period ends as soon as the tool exits; on a stop signal the runner reaps the tool itself, so an exited tool left as a zombie does not hold the runner for the whole grace period. A process group that is already gone is not an error. On the first stop signal the runner ignores SIGTERM, SIGINT and SIGHUP until the tool exits or the grace period ends, so a repeat stop signal, such as a second Ctrl-C, does not send a second SIGTERM that would end the cleanup of either script part way through `docker compose down`.
- After stopping the tool on a stop signal, the runner exits on the same signal, so make reports the run as terminated. A timeout is still reported as `timed out after <n>s`.
- Every tool starts with an 8 GiB limit on its data segment (`RLIMIT_DATA`), lowered to the hard limit when the hard limit is smaller. The limit passes through uv to pytest and holds even when the runner is killed outright.
- Per-step timeouts: 600 s for lint, format, build and support steps, 1800 s for the default and the browser steps, 3600 s for the pytest steps.

### Steps And Make Targets

`.github/scripts/check_steps.py` defines each step's command, parser, working directory, timeout and the options `V=1` adds. Every target runs through the runner. Single-tool targets use `--forward-args` so `ARGS` reaches the tool.

| Target | Runs | Prints on success / on failure |
| --- | --- | --- |
| `ruff` | `uv run ruff format --check`, then `uv run ruff check` | formatted, no findings / each unformatted file, and `file:line code message` per finding |
| `mypy` | `uv run mypy` | no errors / `file:line error: message [code]` per error |
| `import-lint` | `uv run lint-imports` with `PYTHONPATH=.:modbus_mock` | contracts kept / each broken contract with its import chains |
| `complexipy` | `uv run complexipy --plain` | none over the limit / each function over the limit with its score |
| `copy-paste` | `uv run jscpd .` | no duplicates / each duplicated block as `file:lines ↔ file:lines` |
| `test-python` | `uv run pytest` | pass count, total coverage, every warning exactly as pytest prints the warning, and each file below 100 % with its missing lines and branches / failing test IDs with short tracebacks, plus the same warnings and files, and the required threshold when the gate fails |
| `test-isolated` | `uv run --only-group test pytest tests/saj tests/mock` with `UV_PROJECT_ENVIRONMENT=.venv-isolated`, coverage scoped as a subset run | as `test-python` |
| `test-runner-processes` | `uv run pytest -o addopts="-q --tb=short" tests/scripts/test_runner_processes.py`, so the run has no coverage options and does not count toward coverage | pass count and warnings / failing test IDs with short tracebacks |
| `test-modules` | for each module with logic, `uv run pytest` over the unit test files mapped to the module, with coverage reported for that module only; `ARGS` names modules to limit the run | modules covered out of modules gated / per failing module: the module, its coverage and missing lines and branches, failing tests, or `no unit test file` |
| `prettier` | `npm run format:check` in `frontend/` | formatted / each unformatted file |
| `tsc` | `npm run typecheck` in `frontend/` | no errors / `file:line code message` per error |
| `eslint` | `npm run lint` in `frontend/` | no findings / `file:line rule message` per finding |
| `test-frontend` | `npm run test` in `frontend/` | pass count / failing tests with assertion messages, and the coverage table when the gate fails |
| `build` | `npm run build` in `frontend/` | built asset names / build failure |
| `test-browser-controlled` | `npm run test:browser:controlled` in `frontend/`, after `build` | pass count / failing tests with assertion messages, plus the report path `frontend/playwright-report/controlled` |
| `test-browser-home-assistant` | `tests/playwright/run-home-assistant.sh` | pass count / failing tests with assertion messages, plus the report path `frontend/playwright-report/home-assistant` |
| `release-check` | `.github/scripts/release_check.py` | archive complete / each missing archive entry |
| `mock-build` | `docker compose build modbus-mock`, then the existing bytecode check in the built image | built, no bytecode / build failure, or the bytecode check failure |
| `mock-smoke` | `tests/mock-integration/smoke.sh`, then `uv run pytest -o addopts="-q --tb=short" tests/mock-integration`, with no coverage options | scenarios answered / the raw failure output, or failing test IDs with short tracebacks |
| `validate` | `docker run --quiet --rm` of `ghcr.io/home-assistant/hassfest` against the working tree | manifest valid / each failed check with its message |
| `setup` | `uv sync --group dev --group lint`, `npm ci --loglevel=error`, `npx playwright install chromium` | one line per step |
| `up`, `down` | `docker compose up -d --build --remove-orphans --force-recreate`; `docker compose down` | one line per action |
| `logs` | `docker compose logs -f homeassistant`, not through the runner | the log, unchanged |

Grouping targets list runner steps. The steps of each grouping target (`lint`, `test`, `python-ci`, `frontend-check`, `frontend-ci`, `ci`) are kept in one place, `GROUPS` in `.github/scripts/check_steps.py`; `ci` runs every check step, including `test-modules`.

`make help` lists every make target with a one-line summary and ends with a line naming `make help ARGS=<target>` for the detail of one target, and `make help ARGS=<target>` describes one target: what the target runs, what the target prints on success and on failure, what `ARGS` does for the target, and for a grouping target the steps the target runs. The help text is held with each step (`Step.help`) and each group (`Group.summary`) in `.github/scripts/check_steps.py` and printed by `.github/scripts/check_help.py` through the runner's `--describe` option, so a step or group added or changed there is described without a documentation edit. An unknown target name, or more than one name, exits non-zero.

The `Makefile` takes the ha-energy-mpc form:

```make
RUNNER = python3 .github/scripts/check_runner.py

ruff mypy import-lint complexipy copy-paste test-python test-modules test-isolated test-runner-processes prettier tsc eslint test-frontend build test-browser-controlled test-browser-home-assistant release-check mock-build mock-smoke validate:
	@$(RUNNER) --forward-args $@

lint:
	@$(RUNNER) ruff mypy import-lint complexipy

ci:
	@$(RUNNER) checks
```

with the remaining grouping and support targets written the same way.

### Parsers

`.github/scripts/check_parsers.py` is copied with the parsers for pytest, ruff format, ruff check, mypy, complexipy, jscpd, tsc, ESLint, Prettier, Vitest, Playwright, the Vite build, the release check, hassfest and plain steps. Changes:

- **pytest coverage rows.** With `--cov-branch`, coverage rows carry `Stmts Miss Branch BrPart Cover Missing`. The row and `TOTAL` patterns accept both the two-count and the four-count forms, and the missing column keeps branch arcs such as `12->15`.
- **import-linter.** A new parser reads the `Contracts: N kept, M broken.` line for the summary, and on failure keeps each broken contract's name and its import chains as details, with one finding per broken contract.
- **Plain steps.** `mock-build`, `mock-smoke`, `setup`, `up` and `down` use the `plain` parser; on failure the runner prints the raw output lines.

### Coverage Of A Subset Run

`.github/scripts/pytest_scope.py` and `.github/scripts/pytest_scope.json` are copied. A full `make test-python` measures and gates the whole package. When `ARGS` selects test files or folders, the target measures coverage only for the modules those files test, adds the other unit test files mapped to those modules to the run, and applies the 100 % gate to those modules, so a run of `test_coordinator_write.py` also runs `test_coordinator.py` and `test_coordinator_power.py` and gates `coordinator.py`. Selecting tests with `-k`, `-m` or `--lf` needs a test file in `ARGS`. A test file with no known module is rejected until the file is added to `pytest_scope.json`.

The module is the file with the test file's name, without the `test_` prefix, looked up by test folder. The folder mapping is kept in one place, the table of the "Coverage of a subset run" section of `AGENTS.md`, and in `MODULE_DIRECTORIES` of `.github/scripts/pytest_scope.py`.

These 14 test files have no module of the same name and get an entry in `pytest_scope.json` naming the module or modules each file tests:

- `tests/saj-integration/test_config_flow_schedule.py`, `test_coordinator_power.py`, `test_coordinator_write.py`, `test_identity_and_history.py`, `test_init.py`, `test_power_entities.py`, `test_translations.py`
- `tests/mock/profiles/test_profiles.py`, `tests/mock/test_main.py`
- `tests/saj/test_control_hs3.py`, `test_control_members.py`, `test_h2_settings.py`, `test_import.py`, `test_power_control_models.py`

`test-isolated` uses the same scope: the modules of every test file under `tests/saj` and `tests/mock`.

The unit test files are every `test_*.py` under the test folders of that folder mapping except `tests/scripts/test_runner_processes.py`. `test-modules` inverts the mapping: each module under `custom_components/saj_local`, `modbus_mock/saj_modbus_mock` and `.github/scripts` gets the unit test files mapped to the module. Modules with logic and without a unit test file before this revision get a new test file named after the module: `tests/saj-integration/test_label.py`, `tests/saj/test_errors.py`, and, with a `pytest_scope.json` entry because the names are taken or are `__init__`, `tests/saj/test_models.py` for `saj/models/__init__.py` and `tests/saj/test_model_faults.py` for `saj/models/faults.py`.

### Test Folder Layout

| Folder | Holds | Today |
| --- | --- | --- |
| `tests/saj` | unit tests of the SAJ library (`custom_components/saj_local/saj`) | `tests/saj`, unchanged |
| `tests/saj-integration` | unit tests of the Home Assistant integration (`custom_components/saj_local`) | `tests/integration`, renamed |
| `tests/mock` | unit tests of the Modbus mock (`modbus_mock/saj_modbus_mock`), with `profiles/` and `simulation/` | `tests/modbus_mock`, renamed, without the two files below |
| `tests/mock-integration` | integration tests of the Modbus mock: the container smoke script and the shipped-scenario test | `tests/modbus_mock/smoke.sh` and `tests/modbus_mock/test_scenario_files.py` |
| `tests/playwright` | the Docker scripts for the browser tests | `tests/playwright`, unchanged |
| `tests/scripts` | the check runner's unit tests, and its real-process integration tests in `test_runner_processes.py` | new |

Imports of `tests.modbus_mock` become `tests.mock`. No module imports from `tests/saj-integration` or `tests/mock-integration`, so the hyphenated names need no import. `tests/mock-integration` and `tests/scripts/test_runner_processes.py` are outside the unit run and outside coverage.

### Controlled At The Source

Every tool is made quiet in the tool's own configuration, so a direct run is as quiet as a run through make, locally and in GitHub workflows.

| Tool | Where | Change |
| --- | --- | --- |
| pytest | `pyproject.toml` `addopts` | add `-q`, `--tb=short`, `--ignore=tests/mock-integration` and `--ignore=tests/scripts/test_runner_processes.py`, so the unit test runs never collect the integration tests; replace `--cov-report=term-missing` with `--cov-report=term-missing:skip-covered`; add `--cov=.github/scripts`; keep `--cov-branch` and `--cov-fail-under=100`; add `.github/scripts` to `pythonpath` |
| ruff | `pyproject.toml` `[tool.ruff]` | `output-format = "concise"`; `.github/scripts/**` per-file ignores `INP001`, `S603`, `S607` |
| mypy | `pyproject.toml` `[tool.mypy]` | add `.github/scripts` to `files`; `pretty = false`, `show_error_codes = true`, `show_error_context = false`, `error_summary = false`, `color_output = false` |
| complexipy | `pyproject.toml` `[tool.complexipy]` | add `.github/scripts` to `paths`; `failed = true`, `snapshot-ignore = true` (the Makefile flags move here) |
| jscpd | `.jscpd.json` | `"reporters": ["ai"]`, `"noColors": true`, `"noTips": true`, `"exitCode": 1` (the Makefile flags move here) |
| npm | new `frontend/.npmrc` | `fund=false`, `audit=false`, `update-notifier=false`, `progress=false` |
| ESLint | new `frontend/eslint-compact-formatter.js`; `frontend/package.json`; `frontend/eslint.config.js` | `lint` becomes `eslint --format ./eslint-compact-formatter.js .`, printing `file:line:column rule message`; the formatter file is added to the ESLint ignores |
| tsc | `frontend/package.json` | `typecheck` becomes `tsc --noEmit --pretty false` |
| Prettier | `frontend/package.json` | `format:check` becomes `prettier --check --log-level warn .` |
| Vitest | `frontend/vite.config.ts` | `reporters: ["agent"]`; coverage `reporter: [["text", { skipFull: true }]]` |
| Playwright | `frontend/playwright.controlled.config.ts`, `frontend/playwright.home-assistant.config.ts` | `["list"]` becomes `["dot"]`; the HTML reporter keeps `open: "never"` |
| git | `.gitattributes` | `custom_components/saj_local/frontend/saj-local-*.js -diff`, `uv.lock -diff`, `frontend/package-lock.json -diff`, so `git diff` and `git show` print one `Binary files differ` line for each; `git diff --text` still shows the content |

### Agent Environment

The user-level Claude Code settings file (`~/.claude/settings.json`) gains an `env` block, applied to every agent shell in every project on the machine:

- `COMPOSE_PROGRESS=quiet` and `UV_NO_PROGRESS=1`.
- `GIT_CONFIG_COUNT=47` with `GIT_CONFIG_KEY_n` / `GIT_CONFIG_VALUE_n` pairs setting each of these `advice.*` keys to `false`: `addEmbeddedRepo`, `addEmptyPathspec`, `addIgnoredFile`, `amWorkDir`, `ambiguousFetchRefspec`, `checkoutAmbiguousRemoteBranchName`, `commitBeforeMerge`, `defaultBranchName`, `detachedHead`, `diverging`, `fetchRemoteHEADWarn`, `fetchShowForcedUpdates`, `forceDeleteBranch`, `graftFileDeprecated`, `ignoredHook`, `implicitIdentity`, `mergeConflict`, `nestedTag`, `objectNameWarning`, `pushAlreadyExists`, `pushFetchFirst`, `pushNeedsForce`, `pushNonFFCurrent`, `pushNonFFMatching`, `pushNonFastForward`, `pushRefNeedsUpdate`, `pushUnqualifiedRefName`, `pushUpdateRejected`, `rebaseTodoError`, `refSyntax`, `resetNoRefresh`, `resolveConflict`, `rmHints`, `sequencerInUse`, `setUpstreamFailure`, `skippedCherryPicks`, `sparseIndexExpanded`, `statusAheadBehindWarning`, `statusHints`, `statusUoption`, `submoduleAlternateErrorStrategyDie`, `submoduleMergeConflict`, `submodulesNotUpdated`, `suggestDetachingHead`, `updateSparsePath`, `waitingForEditor`, `worktreeAddOrphan`.

The git settings only remove hint lines; `git status`, `git diff`, `git show` and `git log` content is unchanged. The block lives outside the repository, so another machine needs the same block. The runner's `SPARSE_ENVIRONMENT` in `check_steps.py` sets `COMPOSE_PROGRESS` and `UV_NO_PROGRESS` for every step it runs, independent of the user-level block.

### Verbosity And Selection

- `V=1` streams the raw tool output of any target and turns off the quiet settings for that run: the runner removes `SPARSE_ENVIRONMENT` and passes each step's verbose options (for example `--output-format=full` for ruff check, `--pretty --error-summary` for mypy, `--cov-report=term-missing` for pytest, `--reporter=list` for Playwright, `--reporter=default --coverage.reporter=text` for Vitest, `--format stylish` for ESLint, `--pretty true` for tsc, `--log-level log` for Prettier, `--reporters console` for jscpd, no `--plain` for complexipy).
- `ONLY=<step,...>` runs a subset of the steps of a grouping target, for example `make ci ONLY=ruff,mypy`.
- `ARGS="..."` passes paths and options to a single-tool target, for example `make test-python ARGS="tests/saj/test_poller.py -k decode"` or `make ruff ARGS="custom_components/saj_local/coordinator.py"`.

### GitHub Workflows

`.github/workflows/ci.yml` has one `checks` job in place of the `python`, `frontend`, `mock` and `home-assistant-smoke` jobs. The job sets up Python 3.14 with uv and the `dev` and `lint` groups, Node 22 with `npm ci` and Chromium, uses the Docker of the GitHub runner, and runs `make ci`. GitHub therefore runs exactly the steps of `make ci`, and a step added to `make ci` runs in GitHub with no workflow change. The runner prints a collapsed `::group::` and `::error` annotations for each step, so a failure names its step. The browser failure upload stays, covering both Playwright report folders.

The external `lint`, `tests` and `validate` jobs and the `hacs` job are unchanged.

### Documentation

`AGENTS.md`:

- "Verification workflow" is replaced by a description of the runner's output, `make help` in place of a targets and grouping table, `ARGS`, `ONLY`, `V=1` and the coverage of a subset run.
- "Verification workflow" also states that `.github/work/` (requirements, code style, plans and done work) is never excluded from the copy-paste check or any other check, so duplicated text found there is fixed in the documents, not hidden.
- New "Agent use" section, copied from ha-energy-mpc:
  - Use the make target where one exists; a covered tool may be run directly for anything else.
  - Allowed: filtering, piping and redirecting any output (`| grep`, `| tail`, `> file`); selecting tests or stopping early with a test path or node ID, `-k`, `-x`, `--lf` and `-s`; a longer shell timeout or a background run for a long target such as `make ci`.
  - Forbidden: any way of getting verbose output out of the trimmed output, that is `V=1`, options such as `--cov-report=term`, `-v` or `--reporter=verbose`, environment or configuration overrides, and unsetting the agent environment. `--no-cov` is forbidden too.
  - When the trimmed output does not explain a failure clearly enough to fix the failure, the agent stops and asks the user to run the verbose command in the session, for example `! make test-python V=1 ARGS="tests/saj/test_poller.py"`. After the cause is understood, the agent fixes the step's parser in `.github/scripts/check_parsers.py` and adds a unit test for the case.
- New "Efficient reading" section, copied from ha-energy-mpc: read the files a task needs instead of exploring, do not read the same content twice, never list or search `.venv`, `.venv-isolated` or `node_modules`, and never read less of something needed (a code review reads the whole diff). The built card bundle, `uv.lock` and `frontend/package-lock.json` print as one `Binary files differ` line; use `git diff --text` only when their content is the subject.
- "Repository Layout" is expanded to name `custom_components/saj_local/` (with `saj/` the library and `frontend/` the built bundle), `modbus_mock/`, `frontend/`, `tests/` and its folders as "Test Folder Layout" sets out, `.github/scripts/`, `.github/work/`, `config/`, `documentation/`, the compose and Dockerfile files, `Makefile` and `pyproject.toml`.

`documentation/development.md` "Commands and CI": the target table gains the per-tool lint targets, `test-modules` and `validate`, states that GitHub runs `make ci`, and states the runner's output, `ARGS`, `ONLY` and `V=1`.

`CONTRIBUTING.md` "Check your change": states that `make ci` prints one line per step and a final result line, and that `V=1` shows the raw tool output.

## Code Changes

- `.github/scripts/check_runner.py`: copied from ha-energy-mpc, including process safety.
- `.github/scripts/check_steps.py`: copied, with the steps, groups and support steps above, and the help text of each step and group.
- `.github/scripts/check_help.py`: the `make help` listing and the description of one target.
- `.github/scripts/check_parsers.py`: copied, with the branch coverage rows and the import-linter parser.
- `.github/scripts/pytest_scope.py`: copied, with the folder mapping above, the expansion of a subset run to the other test files of its modules, and the module-to-test-files mapping `test-modules` uses.
- `.github/scripts/pytest_scope.json`: the 14 entries above, plus `tests/saj/test_models.py` and `tests/saj/test_model_faults.py`.
- `.github/scripts/check_steps.py`: the `test-modules` step, one pytest command per module, with a step summary of modules covered.
- `.github/scripts/release_check.py`: the archive check moved out of the `Makefile`; checks for `saj_local/frontend/asset-manifest.json` and a `saj_local/frontend/saj-local-<hash>.js` entry and prints `missing <entry>` for each one absent.
- `tests/scripts/`: unit tests for the runner, the steps, the parsers, the scope and the release check, meeting the unit test requirement: `subprocess`, `os.killpg`, `os.waitpid`, `signal`, `resource`, the clock, the timer and the file system are stubbed. 100 % line and branch coverage of `.github/scripts`.
- `tests/scripts/test_runner_processes.py`: the ha-energy-mpc real-process runner tests as integration tests: a child process's output is captured, a child process past its timeout is reported as timed out, a child process killed by a signal is reported as killed, a runner stopped with SIGTERM leaves no child or grandchild process running, and a timed-out shell tool runs its `trap … TERM` cleanup before the runner reports the timeout and leaves no process running. Only critical-path cases; no parser or reporting logic is tested here.
- `tests/`: the folder moves under "Test Folder Layout", with only the import-path edits the moves require; `tests/mock-integration/smoke.sh` keeps working from its new folder.
- `custom_components/saj_local/manifest.json` and `custom_components/saj_local/translations/en.json`: the two hassfest errors fixed, treated as serious because the external `validate` job fails on the same errors. The `description` of `model_mismatch`, `identity_mismatch` and `registers_refused` moves into the fix-flow confirm description, so the configured model or serial, the detected one, and the daily retry of refused readings stay visible. `custom_components/saj_local/repairs.py`: when the fresh device read of the confirm step gives no model or serial, the confirm step falls back to the detected model or serial held by the open issue (`detected_model` for `model_mismatch`, `found_serial` for `identity_mismatch`), and to `?` only when the issue holds neither; `selected_model` and `approved_serial` fall back to `?` when the issue is no longer open, so the confirm description never lacks a placeholder it names; `tests/saj-integration/test_repairs.py` covers the fallback, and `tests/saj-integration/test_translations.py` keeps the placeholder test cases for the three issues, pointed at the confirm description.
- Unit tests added where `make ci` fails without the test: additions to the test file named after the module, or the new test files named under "Coverage Of A Subset Run".
- `Makefile`, `pyproject.toml`, `.jscpd.json`, `.gitattributes`, `frontend/.npmrc`, `frontend/eslint-compact-formatter.js`, `frontend/eslint.config.js`, `frontend/package.json`, `frontend/vite.config.ts`, both Playwright configs: as described above.
- `.github/workflows/ci.yml`: one job running `make ci`, as described above.
- `AGENTS.md`, `documentation/development.md`, `CONTRIBUTING.md`: as described above.
- User-level Claude Code settings file: the `env` block above (outside the repository).

## Verification And Acceptance

- A clean `make ci` prints one line per step and a final result line.
- A run with failures in two different steps reports both in one run, each with `file:line` details where the tool provides them.
- Every single-tool target accepts `ARGS` for paths and options; every grouping target accepts `ONLY`.
- Every target prints quiet output by default and raw output with `V=1`.
- `make help` lists every target, and `make help ARGS=<target>` describes the target named.
- With output redirected to a file, each step's line appears in the file as soon as the step finishes.
- Running a covered tool directly (for example `uv run pytest tests/saj/test_poller.py`, `uv run ruff check .` or `npm run lint`) is as quiet as the make target. `uv run complexipy` without `--plain` is the one exception, because complexipy has no setting to remove the banner; `AGENTS.md` sends agents to `make complexipy`.
- A passing `make test-python` still prints every warning in full and every file below 100 % coverage with its missing lines and branches.
- `make test-python ARGS="<test file>"` gates coverage on the module the test file tests, running the module's other test files alongside.
- `make test-modules` passes: every module with logic reaches 100 % line and branch coverage from its own unit test files, and every such module has at least one unit test file; data-only modules such as `saj/models/shared_faults.py` and `profiles/undocumented.py` are skipped.
- A step that times out, is killed by a signal or has a missing tool is reported as such.
- `make test-isolated` passes without `--no-cov`.
- Stopping `make test-python` with SIGTERM, SIGINT or SIGHUP leaves no pytest process running.
- A timed-out or stopped tool first receives SIGTERM and gets up to 60 s to exit before the runner sends SIGKILL, so stopping `make mock-smoke` or `make test-browser-home-assistant` with Ctrl-C, or a timeout of either target, runs the Docker cleanup trap of the script and leaves no compose project, container, volume or image behind.
- `make test-runner-processes` and `make mock-smoke` pass, and `make test-python` neither collects nor counts toward coverage `tests/mock-integration` or `tests/scripts/test_runner_processes.py`.
- `tests/` holds exactly `saj`, `saj-integration`, `mock`, `mock-integration`, `playwright` and `scripts`.
- The 100 % coverage of `.github/scripts` comes from the unit tests in `tests/scripts/` alone.
- `git diff` and `git show` print one `Binary files differ` line for the built card bundle, `uv.lock` and `frontend/package-lock.json`.
- `AGENTS.md` forbids overriding the trimmed output and `--no-cov`, allows filtering, piping, redirecting and longer timeouts, and tells agents to ask the user for the verbose run and then fix the parser.
- GitHub runs `make ci` in one job, so every step of `make ci`, including `validate`, `test-modules` and `mock-smoke`, runs in GitHub; the external jobs and the `hacs` job are unchanged.
- The repair texts for `model_mismatch`, `identity_mismatch` and `registers_refused` still state the configured and detected inverter and the daily retry, and `make validate` passes.
- `make ci` passes, with 100 % line and branch coverage including `.github/scripts`, and every module at 100 % from its own unit test files.

## Roadmap Changes

None.

## Revision History

- 1: Copy the ha-energy-mpc check runner, quiet tool configuration, agent rules and process safety, adapted to the target names, extra steps, 100 % branch coverage, nested test layout and unit test rules of this project, with runner unit tests separate from runner integration tests, the test folder layout set by the user, and a user-level agent environment.
- 2: Add the `test-modules` per-module coverage gate to `make ci` and `make test`; run a subset's sibling test files alongside it; run `make ci` itself in GitHub in one job, keeping the external jobs; add unit test files for modules without one and the tests each module needs; keep the repair texts hassfest moved.
- 3: Add `make help`, with the help text and the grouping-target steps held in `.github/scripts/check_steps.py` instead of a table in `AGENTS.md`; add the `AGENTS.md` rule that `.github/work/` is never excluded from a check.
