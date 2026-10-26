# Reduce Make CI Time

## Plan Metadata

- **Revision:** 2
- **Status:** Approved
- **Roadmap item:** Drastically reduce make ci time
- **Last revised:** 2026-10-26
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Builds on:** `../done/trim-check-output-for-agents.md` (the check runner, `test-modules` and the per-module coverage gate)

## Outcome And Scope

`make ci` keeps every check and every gate and finishes in far less wall-clock time. Steps still run one after another; no step runs in parallel with another step.

In scope:

- One coverage run gives both the total gate of `test-python` and the per-module gate of `test-modules`, replacing the 90 separate pytest runs of `test-modules`.
- The tests that do not need Home Assistant run without the Home Assistant pytest plugin.
- Slow unit tests are found from measured per-test durations and fixed.
- A duration gate fails `test-python` when the body of any unit test takes over 200 ms in the coverage run.
- The Home Assistant image for the browser tests uses the card bundle the `build` step already built.
- The simulator image is built once per `make ci` and reused by every step that starts the simulator.

Out of scope: running steps in parallel, and the request-budget wait in the Home Assistant browser test (see "The Home Assistant browser test keeps its order" under "Decisions").

## Why

Measured on 2026-10-25, one warm local `make ci`, 23 of 23 steps passed, about 471 s in total:

| Step | Time |
|---|---|
| `test-modules` | 237 s |
| `test-browser-home-assistant` | 100 s |
| `test-python` | 39 s |
| `mock-smoke` | 39 s |
| `tsc` | 10 s |
| `eslint` | 8.4 s |
| `test-isolated` | 7.9 s |
| `test-frontend` | 6.6 s |
| `validate` | 6.0 s |
| `test-runner-processes` | 4.6 s |
| `test-browser-controlled` | 3.7 s |
| `prettier` | 3.0 s |
| `mock-build` | 2.3 s |
| `build` | 1.1 s |
| `ruff`, `mypy`, `import-lint`, `complexipy`, `copy-paste`, `release-check`, `freeze-check`, `docs-check`, `template-check` | under 1 s each |

Where the time goes:

- **`test-modules`** starts one pytest process for each of the 90 gated modules. About 1.8 s of the 3.1 s each process takes is the start-up of the Home Assistant pytest plugin.
- **The Home Assistant pytest plugin adds about 5 ms to every test**, including the 3,393 tests in `tests/saj`, `tests/mock` and `tests/scripts` that never use Home Assistant. Those 3,393 tests take 22.9 s with the plugin and 5.9 s without the plugin.
- **`test-browser-home-assistant`** spends 5 s building, 7 s starting, 81 s in the one Playwright test and 8 s tearing down. 45 s of the Playwright test is the first settings change after control is allowed (`frontend/tests/browser/home-assistant/configuration.spec.ts`, `expectSettingChangeToShow`), which waits for the integration's request budget of 40 requests per 60 s (`custom_components/saj_local/saj/budget.py`).
- **The card bundle is built twice:** by the `build` step and again by the first stage of `Dockerfile.playwright-home-assistant`.
- **The simulator image is built up to four times:** by `mock-build`, by `docker build` and by `docker compose up --build` in `tests/mock-integration/smoke.sh`, and by `compose.playwright.yaml`.

Per-test durations, with the split this plan introduces:

| Tests | Count | Median | Over 5 ms | Over 10 ms | Over 50 ms |
|---|---|---|---|---|---|
| `tests/saj`, `tests/mock`, `tests/scripts`, without the Home Assistant plugin | 3,393 | 1.0 ms | 19 | 5 | 2 |
| `tests/saj-integration`, with the Home Assistant plugin | 1,837 | 5.0 ms | 860 | 269 | 6 |

The tests over 50 ms:

| Test | Time |
|---|---|
| `tests/saj/test_h2_settings.py::test_the_new_writable_h2_settings_are_protected_apart_from_the_ones_allowed` | 1,949 ms |
| `tests/saj-integration/test_identity_and_history.py::test_moving_and_removing_sensors_and_deleting_groups_leave_entities_alone` | 235 ms |
| `tests/saj-integration/test_binary_sensor.py::test_a_fault_is_on_when_the_derived_value_is_not_zero[1-True]` | 141 ms |
| `tests/saj-integration/test_identity_and_history.py::test_replacing_the_model_while_groups_exist_leaves_entities_alone[swap1]` | 103 ms |
| `tests/saj-integration/test_identity_and_history.py::test_replacing_the_model_while_groups_exist_leaves_entities_alone[swap0]` | 89 ms |
| `tests/mock/test_machine.py::test_a_refused_link_setting_names_its_key_and_changes_nothing[values10-x-unknown key]` | 77 ms |
| `tests/saj-integration/test_coordinator_write.py::test_a_release_waits_for_a_cycle_longer_than_its_limit` | 63 ms |
| `tests/saj-integration/test_translations.py::test_no_two_entities_share_a_display_name` | 53 ms |

Per-test durations inside the coverage run, with the `ctrace` core and per-test contexts, measured on 2026-10-26:

| Tests | Over 50 ms | Over 100 ms | Over 200 ms | Slowest test that takes under 50 ms in a normal run |
|---|---|---|---|---|
| `tests/saj`, `tests/mock`, `tests/scripts` | 5 | 2 | 1 | 125 ms |
| `tests/saj-integration` | 9 | 4 | 2 | 76 ms |

The coverage run makes a test about 4 times slower than a normal run, and a test's first run in a file can spike from imports. A test that takes under 50 ms in a normal run reaches up to 125 ms in the coverage run.

### After

Measured on 2026-10-26, after the implementation, on the same machine with a load average of 10 to 14 from other sessions. Four `make ci` runs took 251 s, 244 s, 249 s and 256 s against about 471 s before. The first three passed 23 of 23 steps. The fourth failed `test-browser-home-assistant` once, when Playwright could not find its own trace file as the browser context closed, after every assertion had passed; a rerun of the target passed in 102 s.

| Step | Before | After |
|---|---|---|
| `test-modules` | 237 s | 2.7 s |
| `test-browser-home-assistant` | 100 s | 102–105 s |
| `test-python` | 39 s | 50–58 s |
| `mock-smoke` | 39 s | 34–35 s |
| `tsc` | 10 s | 11–12 s |
| `eslint` | 8.4 s | 8.3–8.8 s |
| `test-isolated` | 7.9 s | 5.8–6.2 s |
| `test-frontend` | 6.6 s | 5.4–5.6 s |
| `validate` | 6.0 s | 6.0–6.3 s |
| `test-runner-processes` | 4.6 s | 4.7–5.0 s |
| `test-browser-controlled` | 3.7 s | 3.6–3.9 s |
| `prettier` | 3.0 s | 3.2–3.5 s |
| `mock-build` | 2.3 s | 2.2–2.5 s |
| `build` | 1.1 s | 1.1 s |
| `ruff`, `mypy`, `import-lint`, `complexipy`, `copy-paste`, `release-check`, `freeze-check`, `docs-check`, `template-check` | under 1 s each | under 1 s each |

`test-python` now holds the whole coverage run that `test-python` and `test-modules` shared before: about 55 s against 276 s.

Per-test durations after, in a normal run:

| Tests | Count | Total | Median | Over 5 ms | Over 10 ms | Over 50 ms |
|---|---|---|---|---|---|---|
| `tests/saj`, `tests/mock`, `tests/scripts`, without the Home Assistant plugin | 3,403 | 2.5 s | 1.0 ms | 18 | 3 | 0 |
| `tests/saj-integration`, with the Home Assistant plugin | 1,841 | 13.5 s | 6.0 ms | 1,167 | 271 | 4 |

The 8 tests listed under "Why" after:

| Test | Before | After |
|---|---|---|
| `test_the_new_writable_h2_settings_are_protected_apart_from_the_ones_allowed` | 1,949 ms | under 1 ms |
| `test_moving_and_removing_sensors_and_deleting_groups_leave_entities_alone`, split into `test_deleting_groups_leaves_entities_alone`, `test_creating_a_group_leaves_entities_alone` and 3 cases of `test_moving_and_removing_sensors_leave_entities_alone` | 235 ms | 20–30 ms each on most runs; up to 59 ms on runs under load |
| `test_a_fault_is_on_when_the_derived_value_is_not_zero[1-True]` | 141 ms | 19 ms |
| `test_replacing_the_model_while_groups_exist_leaves_entities_alone[swap1]` and `[swap0]` | 103 ms and 89 ms | 17–29 ms |
| `test_a_refused_link_setting_names_its_key_and_changes_nothing[values10-x-unknown key]` | 77 ms | 1 ms |
| `test_a_release_waits_for_a_cycle_longer_than_its_limit` | 63 ms | 12 ms |
| `test_no_two_entities_share_a_display_name` | 53 ms | 33 ms |

The tests over 50 ms in the last normal run of `tests/saj-integration` were `test_diagnostics_show_the_serial_only_masked` (60 ms), `test_creating_a_group_leaves_entities_alone` (56 ms) and two cases of `test_moving_and_removing_sensors_leave_entities_alone` (56 ms and 55 ms). The three group tests run at 20–30 ms on most runs, and `test_diagnostics_show_the_serial_only_masked` was under 50 ms in the run measured before the implementation. No test tripped the 200 ms duration gate in any of the four `make ci` runs.

## Requirements

- `.github/work/requirements.md`, Testing: "100% unit test coverage for all lines, statements and paths", from unit tests alone.
- `.github/work/requirements.md`, Testing: "Unit tests MUST be fast. A unit test that takes more than a few milliseconds is not a unit test."
- `.github/work/requirements.md`, Testing: a unit test does not open a socket or network connection.
- `.github/work/requirements.md`, Verification: "One `make ci` runs every check. The partial targets that make up `make ci` stay", and "One `make build` builds everything the project builds".
- `custom_components/saj_local/docs/requirements.md`: the SAJ library "MUST be able to be tested completely isolated from any HA modules".

## Requirement Changes

None.

## Decisions

- **One coverage run with per-test contexts gives both gates.** Coverage records which test ran each line and branch (`--cov-context=test`). The per-module gate counts, for each module, only the contexts of the unit test files mapped to the module by `module_tests` in `.github/scripts/pytest_scope.py`, plus the empty context, which holds the code run when a module is imported. Coverage from the tests of other modules does not count, so the gate is as strict as the 90 separate runs. Verified on 2026-10-25: 90 of 90 modules pass, matching the separate runs; `.github/scripts/pytest_scope.py` gated on `tests/scripts/test_check_steps.py` alone drops from 100 % to 91.4 %, so coverage from another module's tests is rejected.
- **The coverage run uses the `ctrace` core.** On Python 3.14, coverage defaults to the `sysmon` core, which records a line only the first time the line runs in a process, so later tests get no context for the line. With `sysmon`, 32 of the 90 modules failed a gate the separate runs pass. `ctrace` records every context. The core is set only on the commands of the full `test-python` run, through the command environment (`COVERAGE_CORE=ctrace`), not in `pyproject.toml`, so subset runs and `test-isolated` keep the faster `sysmon` core.
- **The coverage run is two pytest commands into one coverage data file.** The first command runs `tests/saj`, `tests/mock` and `tests/scripts` with `-p no:homeassistant --disable-socket --allow-unix-socket`; pytest-socket keeps the socket ban the Home Assistant plugin applied. The second command runs `tests/saj-integration` with the Home Assistant plugin and `--cov-append`, and applies the 100 % total gate. Measured: 45.7 s and 32.6 s, then 5.5 s for the per-module gate, about 84 s against 276 s today.
- **`test-modules` reads the coverage data of `test-python`.** `test-modules` declares `requires=("test-python",)`, and the coverage data file lives in the runner's scratch folder. `make test-modules` alone therefore runs `test-python` first and prints the `test-python` line too, and the tests run only once in `make ci`. Both targets stay, as the Verification requirement says. A separate coverage run for `test-modules` was rejected, because `make ci` would then run every test twice, adding about 80 s.
- **A duration gate inside the coverage run, at 200 ms.** `test-python` fails when the call phase of any unit test, fixture set-up and teardown excluded, takes over 200 ms in the full coverage run. The gate reads the timings of the coverage run itself, so the tests run once. 200 ms in the coverage run is about 50 ms of normal run time, and stays above the 125 ms that healthy tests reach under coverage, so the gate does not fail at random. A 100 ms limit was rejected because a healthy test measured at 125 ms would fail. A separate timing run without coverage was rejected because the tests would run one extra time. Subset runs (`ARGS`) apply no duration gate.
- **The ~5 ms floor of `tests/saj-integration` is accepted.** The Home Assistant `hass` test fixture puts each test in `tests/saj-integration` at about 5 ms, and the plan treats that floor as "a few milliseconds". Rewriting the integration tests toward stubs to go below the floor was rejected as a very large rewrite of 26 test files, with stubs that can drift from real Home Assistant behaviour.
- **Every test over 50 ms in a normal run is fixed.** The 8 tests listed under "Why" are rewritten to meet the unit test requirement, even the ones that pass the 200 ms gate.
- **The Home Assistant browser test keeps its order.** `frontend/tests/browser/home-assistant/configuration.spec.ts` is not changed. Revision 1 reordered the test so the HS3 request budget would refill while the H2 checks ran. Measured on 2026-10-26, the reorder saved about 2 s: the 45 s wait follows the reload of the HS3 entry that allowing control triggers, the H2 checks take about 10 s, and the wait moved to the next check instead of going away. The reorder was reverted.
- **Subset runs do not change.** `make test-python ARGS=…` keeps today's scoped coverage, with the `sysmon` core and no contexts.
- **The Home Assistant image copies the bundle from the working tree.** The frontend stage of `Dockerfile.playwright-home-assistant` is removed. `COPY custom_components/saj_local` already brings `custom_components/saj_local/frontend`. `test-browser-home-assistant` and `docs-images` declare `requires=("build",)`, so the copied bundle is the one `build` just wrote.
- **One simulator image, named `saj-local-mock`.** `mock-build` builds the image. `compose.yaml` gives the `mock` service `image: saj-local-mock` beside the `build` section, and `mock-h2` uses `image: saj-local-mock` with `pull_policy: never` and no `build` section. `compose.playwright.yaml` uses `image: saj-local-mock` with `pull_policy: never` and no `build` section for `mock`, `mock-h2` and `mock-docs`. `tests/mock-integration/smoke.sh` runs the scenarios from `saj-local-mock` and drops its own `docker build`, its `--build` and its image removal. `mock-smoke`, `test-browser-home-assistant` and `docs-images` declare `requires=("mock-build",)`. `down --rmi local` leaves a named image alone, so the image survives teardown.

## Design

### Coverage run

`_test_python` in `.github/scripts/check_steps.py` returns two commands when `ARGS` is empty, and today's single scoped command when `ARGS` is given. The two full-run commands set `COVERAGE_CORE=ctrace` and `COVERAGE_FILE=<scratch>/coverage.data` in their environment and replace the `addopts` of `pyproject.toml` with options built in `check_steps.py`, so the first command does not apply the total gate to a partial run.

### Per-module gate

A new script, `.github/scripts/module_gate.py`, reads the coverage data file and, for each module from `gated_modules`, reports coverage counting only the empty context and the contexts of the module's mapped test files. The script prints one line per module below 100 %, with the module path, the percentage and the missing lines and branches, plus one line per module with logic and no unit test file. `_test_modules` returns one command running the script. The per-module command builder, the `coverage-module-N.ini` files, `check_parsers.module_coverage` and `check_parsers.combine_modules` are removed, with their tests; a new parser reads the script's output and keeps today's summary, "90 of 90 modules covered".

### Duration gate

Both full-run pytest commands add `--durations=0 --durations-min=0.2`, so pytest prints only the test phases that took over 200 ms. The parser of `test-python` in `.github/scripts/check_parsers.py` fails the step for each listed `call` phase and prints the test ID with its time; a listed `setup` or `teardown` phase is ignored. A passing run prints nothing extra.

### Slow tests

Each of the 8 tests over 50 ms under "Why" is rewritten to meet the unit test requirement. The 1,949 ms `test_h2_settings.py` test and any test that starts a process or uses real time are the first to fix.

### Documentation

- `docs/en-gb/developer/checks.md`: the `test-python` and `test-modules` rows and "Coverage of a subset run" describe the context-based gate, the `ctrace` core, the two runs, the 200 ms duration gate and that `make test-modules` runs `test-python` first.
- The `Help` text of `test-python`, `test-modules`, `test-browser-home-assistant`, `docs-images` and `mock-smoke` in `.github/scripts/check_steps.py`.

## Code Changes

- `.github/scripts/check_steps.py`: the two-command full `test-python`, the one-command `test-modules` with `requires=("test-python",)`, and the `requires` of `test-browser-home-assistant`, `docs-images` and `mock-smoke`.
- `.github/scripts/module_gate.py`: new.
- `.github/scripts/check_parsers.py`: the parser of `module_gate.py`; the duration lines in the pytest parser; `module_coverage` and `combine_modules` removed.
- `tests/scripts/test_module_gate.py`: new unit tests, with coverage data and the clock stubbed.
- `tests/scripts/test_check_steps.py` and `tests/scripts/test_check_parsers.py`: updated for the changed steps and parsers.
- `Dockerfile.playwright-home-assistant`: the frontend stage removed.
- `compose.yaml`, `compose.playwright.yaml`, `tests/mock-integration/smoke.sh`: the named simulator image.
- The test files of the slow tests under "Why".
- `docs/en-gb/developer/checks.md`.

## Verification And Acceptance

- `make ci` passes.
- For every module, the per-module gate gives the same verdict as today's separate runs. Checked once during implementation by running both gates on the same commit, and by removing one mapped test file of a module to prove the new gate fails that module.
- A test that opens a TCP socket in `tests/saj` fails under the new run.
- `make test-modules` alone runs `test-python` first and gives the same verdict as within `make ci`.
- A unit test whose body sleeps 250 ms fails `test-python` with the test ID and time in the output; a fixture that sleeps 250 ms does not.
- No test that takes under 50 ms in a normal run fails the duration gate across three consecutive `make ci` runs.
- The 8 tests listed under "Why", and every test split from one of the 8, take under 50 ms in a normal run.
- The Home Assistant browser test sees a bundle changed in `frontend/src` without any manual build.
- One `make ci` builds the simulator image once; `docker images` shows `saj-local-mock` after the run and no images left by the run's compose projects.
- The table under "Why" is repeated with the after timings of every step and the after per-test durations.

## Roadmap Changes

None.

## Revision History

| Revision | Date | Change |
|---|---|---|
| 1 | 2026-10-26 | First draft. |
| 2 | 2026-10-26 | Dropped the reorder of the Home Assistant browser test, which measured a saving of about 2 s; the test keeps its order. |
