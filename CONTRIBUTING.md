# Contributing

[![Python](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FCounterphase-Labs%2Fha-saj-local%2Fmain%2Fpyproject.toml&logo=python&logoColor=white)](pyproject.toml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Lit](https://img.shields.io/badge/Lit-324FFF?logo=lit&logoColor=white)](https://lit.dev/)

Thanks for helping. Platform stability and correctness come first, so every change has to pass the same checks CI runs.

This page is the short version: how to get set up and send a change. The [development guide](documentation/development.md) explains how the project is put together and why.

## What you need

- [uv](https://docs.astral.sh/uv/)
- Node.js and npm
- Docker with Docker Compose
- `make`

Required versions are set in `pyproject.toml` and `frontend/package.json`.

## Set up

```bash
make setup
```

## Run it

```bash
make up     # start Home Assistant with the integration and the Modbus simulators
make logs   # follow the Home Assistant log
make down   # stop everything
```

Home Assistant is then on the port published in `compose.yaml`. You do not need a real inverter: the simulators stand in for one. See [The Modbus simulator](documentation/development.md#the-modbus-simulator) for how to connect to them and change what they simulate.

## Check your change

```bash
make ci
```

This runs everything CI runs, and GitHub runs `make ci` itself, so the result matches. The command must pass before you send a change. `make ci` prints one line per step and a final result line, and a failing step adds the findings needed to fix the failure. Add `V=1`, for example `make ci V=1`, to show the raw tool output. The other targets in the `Makefile` run parts of it while you work. The rules behind the checks are in [Testing](documentation/development.md#testing). Python tests live in six folders under `tests/`: `tests/saj` (unit tests of the SAJ library), `tests/saj-integration` (unit tests of the Home Assistant integration), `tests/mock` (unit tests of the Modbus mock, with `profiles/` and `simulation/`), `tests/mock-integration` (the container smoke script and the shipped-scenario test of the Modbus mock), `tests/playwright` (the Docker scripts for the browser tests) and `tests/scripts` (the unit tests of the check runner, and its real-process tests in `test_runner_processes.py`).

## Send your change

Commit messages use a semantic type and need both a title and a body that explains why the change is made. The full rules are under Commit Message Guidelines in [AGENTS.md](AGENTS.md).

## Read more

- [Development guide](documentation/development.md): architecture, tooling, Docker and the Modbus simulator.
- Requirements: what the project must do. [Global](.github/work/requirements.md), [integration](custom_components/saj_local/docs/requirements.md), [cards](frontend/docs/requirements.md) and [simulator](mock/docs/requirements.md).
- [Code style](.github/work/code-style.md): how code, tests and documentation are written.
- [AGENTS.md](AGENTS.md): the rules that bind everyone working in the repository, including how to bump the Home Assistant version.
