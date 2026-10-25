# Checks

What each make target runs, how to narrow a run, and the rules every check follows.

## Make targets

Every action is a make target and CI calls the same targets, so passing locally and passing in CI mean the same thing. A new CI step starts as a make target. `make help` lists every target with one line, and `make help ARGS=<target>` describes one target: what the target runs, what the target prints on success and on failure, what `ARGS` does and, for a grouping target, the steps the target runs.

`make ci` runs every check step and is the definition of done. GitHub runs `make ci` itself in the one `checks` job of [ci.yml](../../../.github/workflows/ci.yml), alongside the shared `roquerodrigo/workflows` jobs (`lint`, `tests`, `validate`) and the `hacs` job, so a step added to `make ci` runs in GitHub with no workflow change. Run the narrower targets while iterating.

`make build` is the one production build of the frontend. `make test` runs every test suite, and each suite has its own target so one suite can be run alone:

| Target | Suite |
| --- | --- |
| `make test-python` | The pytest unit tests of the library, the integration, the simulator and the check runner, without `tests/mock-integration` and `tests/scripts/test_runner_processes.py`, with the 100 % line and branch coverage gate. |
| `make test-frontend` | The Vitest unit tests of the cards, with the coverage gate. |
| `make test-modules` | Every module with logic (any function, method or branch) against the unit test files mapped to the module alone, with 100 % line and branch coverage required per module. A module with logic and no unit test file fails, and a module with no logic, such as an empty module or a data table, is skipped. |
| `make test-isolated` | The `tests/saj` and `tests/mock` tests in an environment that has no Home Assistant, which proves the boundary between the library, the simulator and Home Assistant. Coverage is gated on the modules the test files test. |
| `make test-runner-processes` | The real-process tests of the check runner in `tests/scripts/test_runner_processes.py`, which start real processes and are outside coverage. |
| `make test-browser-controlled` | Playwright against the built bundle and controlled data, with no Home Assistant. |
| `make test-browser-home-assistant` | Playwright against a throwaway Home Assistant with an HS3 simulator and an H2 simulator, which proves the cards load and work in the real frontend. |
| `make mock-smoke` | The simulator container answers a client, then the tests in `tests/mock-integration` run. |

The checks that make up `make ci` also have a target each, so one tool can be run alone:

| Target | Check |
| --- | --- |
| `make ruff` | `ruff format --check` and `ruff check`. |
| `make mypy` | The strict type check. |
| `make import-lint` | The import-linter contracts. |
| `make complexipy` | The cognitive complexity limit. |
| `make copy-paste` | jscpd duplicate code and text detection, over the whole repository including `docs/`. |
| `make prettier`, `make tsc`, `make eslint` | Formatting, type check and lint of the frontend. |
| `make build` | The Vite production build of the frontend. |
| `make release-check` | The HACS archive holds `asset-manifest.json` and the built card bundle. The archive is made from the files in `custom_components/saj_local/`, so the built bundle must be in the tree. The version in `custom_components/saj_local/manifest.json`, `pyproject.toml` and `frontend/package.json` is `X.Y.Z` or `X.Y.ZbN` and the same in all three files, and a tag at `HEAD` equals the version. With no tag at `HEAD` the tag comparison is skipped. |
| `make freeze-check` | No entity key, entity ID, stored setting key or card type is removed, and no entity platform, unit, device class, state class or state value changes, compared with the newest stable release tag. Beta tags are skipped, so a beta never freezes the surface. With no stable release tag the step passes. |
| `make docs-check` | The generated entity reference, links, images, page length and feature list coverage. See the [documentation page](documentation.md#checks). |
| `make template-check` | `bug.yml` requires the diagnostics download, every label an issue template applies or links exists in `.github/labels.yml`, and the model dropdown of `bug.yml` matches the models in `translations/en.json`. |
| `make mock-build` | The simulator image builds and holds no bytecode. |
| `make validate` | hassfest against the working tree, in Docker. HACS validation reads the pushed repository, so only the `hacs` workflow job runs the HACS validation. |

`make lint`, `make python-ci`, `make frontend-check` and `make frontend-ci` run groups of these targets.

Four more targets are not checks. `make setup` installs the Python and frontend dependencies and Chromium, `make docs` regenerates the entity reference, `make docs-images` makes the documentation screenshots and is not a step of `make ci`, and `make up`, `make down` and `make logs` run the development Home Assistant, see the [environment page](environment.md#run-home-assistant).

Every target runs through the check runner in `.github/scripts/`. The runner prints one `[x]` or `[ ]` line per step, the findings of a failing step as `file:line message`, and a final result line. The runner runs every selected step even after one fails, and reports a timeout, a signal or a missing tool as such. Every step has a time limit. The quiet output exists so a person or an agent reads only what is needed to fix a failure.

GitHub Actions are pinned to a commit hash so a moved tag cannot change what CI runs.

## Options

- `ARGS="..."` passes paths and options to a single-tool target, for example `make test-python ARGS="tests/saj/test_poller.py -k decode"` or `make ruff ARGS="custom_components/saj_local/coordinator.py"`. `make help ARGS=<target>` states what `ARGS` does for each target.
- `ONLY=<step,...>` runs a subset of the steps of a grouping target, for example `make ci ONLY=ruff,mypy`. A name that the target does not run is an error.
- `V=1` streams the raw tool output and switches off the sparse tool configuration and environment settings for that run.

## Coverage of a subset run

A full `make test-python` measures and gates the whole package. When `ARGS` selects test files or folders, the target measures coverage only for the modules the test files test, adds the other unit test files mapped to those modules to the run, and applies the same 100 % gate to those modules. A run of `tests/saj-integration/test_coordinator_write.py` therefore also runs `test_coordinator.py` and `test_coordinator_power.py` and gates `coordinator.py`. The module is the file with the test file's name without the `test_` prefix, looked up by test folder:

| Test folder | Module folders |
| --- | --- |
| `tests/saj` | `custom_components/saj_local/saj`, `custom_components/saj_local/saj/models` |
| `tests/saj-integration` | `custom_components/saj_local` |
| `tests/mock` | `mock/saj_local_mock` |
| `tests/mock/profiles` | `mock/saj_local_mock/profiles` |
| `tests/mock/simulation` | `mock/saj_local_mock/simulation` |
| `tests/scripts` | `.github/scripts` |

Test files with no module of the same name are listed in `.github/scripts/pytest_scope.json`, each with the modules the file tests, and a test file with no known module is rejected until the file is added there. The folder mapping is in `.github/scripts/pytest_scope.py`. Selecting tests with `-k`, `-m` or `--lf` needs a test file in `ARGS`, so coverage can be gated on the module the file tests.

`test-modules` runs in `make ci` and gates every module at 100 % line and branch coverage from the unit test files mapped to the module alone, so coverage from the tests of other modules does not count. A module with logic and no unit test file fails the step, and a module with no logic is skipped, because the requirements forbid tests of constants. A module that only passes the gate in the full `test-python` run means other tests cover the module by accident, and that is a real gap to fix. `test-isolated` gates coverage the same way as any subset run.

## Testing

The rules are in the [Testing section of the global requirements](../../../.github/work/requirements.md#testing). The reasons:

- **Coverage counts unit tests only.** A test that wires real modules together raises the figure without proving any one of the modules.
- **Unit tests are fast and isolated.** No sockets, servers, fixture files, real time or long simulations. Time, randomness and I/O are injected throughout the code for this reason.
- **Integration tests only prove that parts connect.** For the simulator the integration test is `make mock-smoke`.
- **No inline bypasses** of lint, type or coverage checks. Change the configuration, where the decision is visible, or restructure the code.
- **Assert behaviour, not constants.** A test that restates a register address proves nothing.

`tests/` holds exactly six folders:

- `tests/saj`: unit tests of the SAJ library.
- `tests/saj-integration`: unit tests of the Home Assistant integration, not integration tests.
- `tests/mock`: unit tests of the Modbus simulator, with `profiles/` and `simulation/`.
- `tests/mock-integration`: the container smoke script and the shipped-scenario test of the simulator.
- `tests/playwright`: the Docker scripts for the browser tests.
- `tests/scripts`: the unit tests of the check runner, and its real-process tests in `test_runner_processes.py`.

`tests/mock-integration` and `tests/scripts/test_runner_processes.py` are outside the unit run and outside coverage.

## Stack

| Piece | Why |
| --- | --- |
| Python with `uv` | One lock file, the same installs locally and in CI. |
| Ruff, all rules on | Each exception is a visible decision in `[tool.ruff.lint]`. |
| mypy | Register decoding invites scaling, sign and width mistakes that types catch. |
| import-linter | Makes the boundaries on the [architecture page](architecture.md#how-the-project-is-divided) a failing check. |
| complexipy, jscpd | Register-map code grows by duplication; the limits stop the growth. |
| pytest, 100 percent branch coverage | See [Testing](#testing). |
| Lit, TypeScript, Vite | Home Assistant's frontend is Lit, so the cards need no second framework. |
| Playwright | Drives the cards in a real browser and in a real Home Assistant, and makes the [documentation screenshots](documentation.md#screenshots). |
| Docker Compose | See the [environment page](environment.md#docker). |

Home Assistant is pinned in several files that must change together, or lint and tests run against different cores. The steps are on the [releasing page](releasing.md#bumping-the-home-assistant-version).
