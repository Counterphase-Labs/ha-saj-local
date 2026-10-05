# Developing the SAJ Modbus Home Assistant Integration

This guide explains why the project is built the way it is and links to the file that holds each fact. Versions, command lists and register maps live in the code and configuration, not here.

To get a working checkout and send a change, start with [CONTRIBUTING.md](../CONTRIBUTING.md).

## Where the truth lives

| Question | Authority |
| --- | --- |
| What must the project do? | [requirements.md](../.github/work/requirements.md) |
| How is code, testing and documentation written? | [code-style.md](../.github/work/code-style.md) |
| What rules bind everyone working here? | [AGENTS.md](../AGENTS.md) |
| What was built, and why? | [done/index.md](../.github/work/done/index.md) |
| What is planned? | [.github/work/future/](../.github/work/future/) |
| Which commands exist? | [Makefile](../Makefile) |
| What does CI run? | [ci.yml](../.github/workflows/ci.yml) |
| Python dependencies and tool settings | [pyproject.toml](../pyproject.toml) |
| Frontend dependencies and scripts | [frontend/package.json](../frontend/package.json) |
| Development services | [compose.yaml](../compose.yaml) |

Existing code has no authority over requirements. Where they disagree, the code is wrong or the owner changes the requirement.

## How the project is divided

Four parts, kept apart on purpose:

- **SAJ library** (`custom_components/saj_modbus/saj/`): everything about SAJ devices and Modbus. It must not import Home Assistant, so device logic can be tested with plain inputs. It ships inside the integration; the split is a design boundary, not a package.
- **Home Assistant integration** (the rest of `custom_components/saj_modbus/`): config flow, entities, diagnostics, translations. Keep it thin. Logic that would be true without Home Assistant belongs in the library.
- **Frontend** (`frontend/`): the Lovelace cards. The build output is written into the integration directory because HACS ships that directory as one archive.
- **Modbus simulator** (`modbus_mock/`): a separate program that shares no code with the others. See [The Modbus simulator](#the-modbus-simulator).

The import contracts under `[tool.importlinter]` in `pyproject.toml` enforce these boundaries in the lint step.

### Stable names

Sensor names are a contract with every dashboard and automation a user writes. The library presents one set of names, units and formats across SAJ models, so a hardware upgrade keeps history wherever the old and new systems overlap. Map a new device onto the existing vocabulary before inventing names.

Until the first release, a wrong design is replaced outright with no compatibility layer. See the Backwards Compatibility notice in `AGENTS.md`.

## Stack

| Piece | Why |
| --- | --- |
| Python with `uv` | One lock file, the same installs locally and in CI. |
| Ruff, all rules on | Each exception is a visible decision in `[tool.ruff.lint]`. |
| mypy | Register decoding invites scaling, sign and width mistakes that types catch. |
| import-linter | Makes the boundaries above a failing check. |
| complexipy, jscpd | Register-map code grows by duplication; these limits stop it. |
| pytest, 100 percent branch coverage | See [Testing](#testing). |
| Lit, TypeScript, Vite | Home Assistant's frontend is Lit, so cards need no second framework. |
| Playwright | Drives the cards in a real browser and in a real Home Assistant. |
| Docker Compose | See [Docker](#docker). |

Home Assistant is pinned in several files that must change together, or lint and tests run against different cores. The steps are under "Bumping the Home Assistant version" in `AGENTS.md`.

## Commands and CI

Every action is a make target and CI calls the same targets, so passing locally and passing in CI mean the same thing. A new CI step starts as a make target.

`make ci` runs everything CI runs and is the definition of done. Run the narrower targets while iterating.

GitHub Actions are pinned to a commit hash so a moved tag cannot change what CI runs.

## Testing

The rules are in the Non Functional section of `requirements.md`. The reasons:

- **Coverage counts unit tests only.** A test that wires real modules together raises the figure without proving any one of them.
- **Unit tests are fast and isolated.** No sockets, servers, fixture files, real time or long simulations. This is why time, randomness and I/O are injected throughout the code.
- **Integration tests only prove things connect.** For the simulator that is `make mock-smoke`.
- **No inline bypasses** of lint, type or coverage checks. Change the configuration, where the decision is visible, or restructure the code.
- **Assert behaviour, not constants.** A test that restates a register address proves nothing.

`tests/integration/` holds the unit tests of the Home Assistant integration, not integration tests.

## Code style

[code-style.md](../.github/work/code-style.md) is the authority. Its documentation rule shapes this guide: explain why, not how, and let names and types describe the rest.

## Docker

Development runs in containers so Home Assistant is a known, pinned release with a clean configuration.

- [compose.yaml](../compose.yaml): the interactive environment, Home Assistant plus the simulators. The integration is mounted read-only so the container never writes into the source tree.
- [compose.playwright.yaml](../compose.playwright.yaml): a throwaway Home Assistant for the browser tests. It shares no state with the interactive one.
- `compose.override.yaml`: your machine's ports, time zone and scenarios. Ignored by git; `compose.override.yaml.example` shows the shape. Do not edit `compose.yaml` for local needs, because the smoke test starts it too.

Under `config/`, only `configuration.yaml` is tracked. The rest is local Home Assistant state.

## The Modbus simulator

A stand-in SAJ device that Home Assistant or any Modbus client can connect to, so the integration can be developed without owning the hardware or risking it. It aims at believable smoke testing, not exact emulation, and it is not a general Modbus server.

### Design decisions

- **Standalone.** It shares no code with the integration. If both sides used the same register definitions, a mistake in them would be invisible.
- **Its own Modbus layer.** Real SAJ devices break the standard: odd exception codes, blocks that reject reads across their end, a low client limit. These are what the integration has to cope with, so they are built in.
- **One container, one device.** No state outside the process, so instances never affect each other.
- **Fixed at start.** No runtime control. The scenario file and incoming requests are the only inputs.
- **Deterministic.** Weather and load depend only on the seed and the simulated time. The same scenario, instant and writes give the same values, however often a client polls.
- **One energy balance.** Only irradiance and load are generated; everything else is derived, so the registers never contradict each other.
- **Writes take effect.** Settings are stored, read back and acted on.

### Finding your way around

| For | Look in |
| --- | --- |
| Full design, register coverage and quirks | The design document under [.github/work/](../.github/work/) (`future/` while in progress, then `done/`) |
| Ready-made systems | [modbus_mock/scenarios/](../modbus_mock/scenarios/) |
| Valid scenario keys and defaults | `modbus_mock/saj_modbus_mock/scenario.py` |
| What each model supports | `modbus_mock/saj_modbus_mock/models.py` |
| Registers | `modbus_mock/saj_modbus_mock/profiles/` |
| How values evolve | `modbus_mock/saj_modbus_mock/simulation/` |
| Services and ports | [compose.yaml](../compose.yaml) |

The transport knows nothing about SAJ, the device owns addresses and access rules, a profile binds registers to simulated quantities, and the simulation does not know how values are transported. Keeping the layers apart is what lets each be unit tested alone.

### Talking to it from a terminal

`make up` starts the simulators. Home Assistant reaches each by its Compose service name on the simulator's own port; from your machine use `localhost` and the published port from `compose.yaml`.

The examples use [mbpoll](https://github.com/epsilonrt/mbpoll) against the first simulator's published port. `-0` makes addresses match the register maps, `-1` reads once, `-t 4` selects holding registers and `-a` is the unit id.

Read the device type and rated power:

```bash
mbpoll -m tcp -p 5020 -a 1 -0 -1 -t 4:hex -r 0x8F00 -c 2 localhost
```

An HS3 and an H2 answer with different device types, which is the quickest way to confirm which system a port is simulating.

Write a setting and read it back (here the application mode):

```bash
mbpoll -m tcp -p 5020 -a 1 -0 -t 4 -r 0x3647 localhost 1
mbpoll -m tcp -p 5020 -a 1 -0 -1 -t 4 -r 0x3647 localhost
```

See how it refuses a request, for example an address outside every block:

```bash
mbpoll -m tcp -p 5020 -a 1 -0 -1 -t 4 -r 0x0001 localhost
```

Watch a value change by dropping `-1`; mbpoll then polls once a second until stopped.

Run the simulator's own healthcheck, which needs no client installed:

```bash
docker compose exec modbus-mock python -m saj_modbus_mock healthcheck; echo $?
```

Writes last until the container restarts. Addresses come from the profiles; the three above are only starting points.

### Configuring a scenario

A scenario is a YAML file mounted at `/config/config.yaml`. Only `device.model` is required, so a file states just what differs from the defaults:

```yaml
device:
  model: hs3
simulation:
  start: "2026-06-21T12:00:00"
  speed: 600
battery:
  modules: 4
```

`simulation.speed` is simulated seconds per real second, so this runs ten simulated minutes every second from midsummer noon: useful for watching a full day of charge and discharge in a few minutes. `simulation.seed` picks the weather and load.

A wrong key or an impossible combination stops the simulator at start and names the key:

```text
invalid scenario: ev_charger.installed: not available on h2
```

### Running a different or extra system

**Try a scenario once**, without touching any file. It runs in the foreground on its own port until you stop it:

```bash
docker compose run --rm --no-deps -p 5030:502 \
  -v ./modbus_mock/scenarios/hs3-off-grid.yaml:/config/config.yaml:ro \
  modbus-mock
```

Point `-v` at your own file to run a scenario you wrote.

**Change what `make up` starts** in `compose.override.yaml`. Mounting another file over the same path replaces the scenario; a new service adds a system:

```yaml
services:
  modbus-mock:
    volumes:
      - ./modbus_mock/scenarios/hs3-ev.yaml:/config/config.yaml:ro

  modbus-mock-off-grid:
    build:
      context: ./modbus_mock
    volumes:
      - ./modbus_mock/scenarios/hs3-off-grid.yaml:/config/config.yaml:ro
    ports:
      - "5022:502"
```

Each service is an independent device with its own state. Home Assistant reaches the new one as `modbus-mock-off-grid`, so several systems can be added to one Home Assistant side by side.

### Extending it

- **New scenario:** a file in `modbus_mock/scenarios/`. `make mock-smoke` picks it up automatically.
- **New model:** an entry in `models.py`, a profile, and acceptance by the scenario validation.
- **New quirk:** in the layer that owns it. Framing and connections in the transport, addresses and access in the device, model behaviour in the profile.

The simulator passes the same gates as the integration.

## Keeping this guide useful

- Link to the file that holds a fact; do not copy it.
- Record the reason for a decision. Reasons change rarely, details constantly.
- Examples are the exception: keep them few, and run them when they change.
