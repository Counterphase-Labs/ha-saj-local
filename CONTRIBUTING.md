# Contributing

[![Python](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FCounterphase-Labs%2Fha-saj-local%2Fmain%2Fpyproject.toml&logo=python&logoColor=white)](pyproject.toml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Lit](https://img.shields.io/badge/Lit-324FFF?logo=lit&logoColor=white)](https://lit.dev/)

Thanks for helping. Platform stability and correctness come first, so every change has to pass the same checks CI runs.

This page is the short version: how to get set up and send a change. The [developer documentation](docs/en-gb/developer/README.md) explains how the project is put together and why.

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

Home Assistant is then on the port published in `compose.yaml`. You do not need a real inverter: the simulators stand in for one. See [the simulator page](docs/en-gb/developer/simulator.md) for how to connect to them and change what they simulate.

## Check your change

```bash
make ci
```

This runs everything CI runs, and GitHub runs `make ci` itself, so the result matches. The command must pass before you send a change. The other targets in the `Makefile` run parts of it while you work. The [checks page](docs/en-gb/developer/checks.md) lists what each target runs, how to narrow a run, where the Python tests live and the rules behind the checks.

## Send your change

Commit messages use a semantic type and need both a title and a body that explains why the change is made. The full rules are under Commit Message Guidelines in [AGENTS.md](AGENTS.md).

## Issue labels

The labels are defined in `.github/labels.yml` and applied by the workflow `.github/workflows/labels.yml`. A label made by hand on GitHub is deleted on the next sync, so a new label goes into the file.

Once triaged, every issue carries one priority, one status, one goal and one aspect label, plus one part label when the issue concerns the integration, the cards or the simulator. An issue about developer tooling or the documentation as a whole carries no part label. An issue labelled `🚦 status: awaiting triage` may lack the others.

A closed issue gets `🏁 status: ready for dev` when resolved or `⛔️ status: discarded` when not. Status labels are kept current as the issue changes.

The rules come from the [Creative Commons repository label guide](https://opensource.creativecommons.org/contributing-code/repo-labels/).

## Read more

- [Developer documentation](docs/en-gb/developer/README.md): architecture, tooling, Docker and the Modbus simulator.
- Requirements: what the project must do. [Global](.github/work/requirements.md), [integration](custom_components/saj_local/docs/requirements.md), [cards](frontend/docs/requirements.md) and [simulator](mock/docs/requirements.md).
- [Code style](.github/work/code-style.md): how code, tests and documentation are written.
- [AGENTS.md](AGENTS.md): the rules that bind everyone working in the repository.
- [Releasing](docs/en-gb/developer/releasing.md): how to bump the Home Assistant version.
