# Modbus simulator

![The Overview of the HS3 simulator page: the status bar, the power-flow diagram and one card for each piece of fitted equipment](../../images/en-gb/developer-simulator-page-overview.png)

What the simulator is for, how to run and configure a scenario, and how to extend the simulator.

The full list of what the simulator covers is in the feature list sections [Simulated models](../../../mock/docs/features.md#simulated-models), [Scenarios](../../../mock/docs/features.md#scenarios), [Variation](../../../mock/docs/features.md#variation).

The simulator is a stand-in SAJ device that Home Assistant or any Modbus client can connect to, so the integration can be developed without owning the hardware or risking the hardware. The simulator aims at believable smoke testing, not exact emulation, and is not a general Modbus server. The package is `mock/saj_local_mock/`, and each simulator runs in its own container.

## Design decisions

- **Standalone.** The simulator shares no code with the integration, and an import-linter contract forbids the simulator from importing Home Assistant or `custom_components`. If both sides used the same register definitions, a mistake in the definitions would be invisible.
- **Its own Modbus layer.** Real SAJ devices break the standard: odd exception codes, blocks that reject reads across their end, a low client limit. The integration has to cope with such failures, so the failures are built in.
- **One container, one device.** Each instance keeps its own state, in its own folder under `mock/state/`, so instances never affect each other.
- **Changeable while running.** The scenario is the starting point, not the only input. The simulator page and incoming requests change the running system, and the scenario stays the known state to return to.
- **Deterministic.** Weather and load depend only on the seed and the simulated time. The same scenario, instant and writes give the same values, however often a client polls.
- **One energy balance.** Only irradiance and load are generated; everything else is derived, so the registers never contradict each other.
- **Writes take effect.** Settings are stored, read back and acted on. A write from the page goes through the same validation and handling as a Modbus write, so the integration cannot tell the two apart and the page cannot put the device in a state a client could not.
- **The page knows nothing about models.** The page builds itself from the description the device gives, so a new model needs no page change. The page is a development tool, so the page is plain HTML, CSS and JavaScript files in `mock/static/` served as they are, with no libraries, no build step and no tests of the page's own, while the Python behind the page is tested like the rest. See the [simulator page](simulator-page.md).
- **The module is part of the simulation.** The Modbus server stands for the communication module a client connects to, so the failures field reports describe of those modules (slow or missing answers, odd exception codes, dropped connections, a lockout) are settings of the simulator and not special cases scattered through the device.
- **Write behaviour comes from the SAJ documents.** Writes are specified by the SAJ protocol documents and real readings, not by the simulator. If the simulator departs from the documented `0x06` and `0x10` behaviour, the departure is a simulator defect to raise, not something to adjust the integration around.

## Finding your way around

| For | Look in |
| --- | --- |
| Why the simulator is built as it is | The done work [Build SAJ Modbus Mock Simulator](../../../.github/work/done/build-saj-modbus-mock-simulator.md), [Add Simulator Control Panel](../../../.github/work/done/add-simulator-control-panel.md) and [Redesign Simulator Panel With Inspector And Link Faults](../../../.github/work/done/redesign-simulator-panel-with-inspector-and-link-faults.md) |
| Ready-made systems | [mock/scenarios/](../../../mock/scenarios/) |
| Valid scenario keys and defaults | `mock/saj_local_mock/scenario.py` |
| What each model supports | `mock/saj_local_mock/models.py` |
| Registers | `mock/saj_local_mock/profiles/` |
| How values evolve | `mock/saj_local_mock/simulation/` |
| Services and ports | [compose.yaml](../../../compose.yaml) |
| Simulator page | `panel.py` (routes), `description.py`, `presets.py` and the page in [mock/static/](../../../mock/static/) |
| Link faults | `mock/saj_local_mock/link.py` (settings, bounds, decisions) and `transport.py` (carrying the decisions out) |
| Traffic record | `mock/saj_local_mock/traffic.py` |
| Fault bits per model | `mock/saj_local_mock/profiles/fault_tables.py` |
| Saved state | `mock/saj_local_mock/persistence.py` |

The transport knows nothing about SAJ, the device owns addresses and access rules, a profile binds registers to simulated quantities, and the simulation does not know how values are transported. Keeping the layers apart is what lets each layer be unit tested alone.

## Talking to the simulator from a terminal

`make up` starts the simulators. Home Assistant reaches each by its Compose service name on the simulator's own port; from your machine use `localhost` and the published port from `compose.yaml`.

The examples use [mbpoll](https://github.com/epsilonrt/mbpoll) against the HS3 simulator's published port. `-0` makes addresses match the register maps, `-1` reads once, `-t 4` selects holding registers and `-a` is the unit id.

Read the device type and rated power (registers `0x8F00` and `0x8F01`):

```bash
mbpoll -m tcp -p 5020 -a 1 -0 -1 -t 4:hex -r 0x8F00 -c 2 localhost
```

An HS3 and an H2 answer with different device types, which is the quickest way to confirm which system a port is simulating.

Write a setting and read the setting back (here the application mode at `0x3647`):

```bash
mbpoll -m tcp -p 5020 -a 1 -0 -t 4 -r 0x3647 localhost 1
mbpoll -m tcp -p 5020 -a 1 -0 -1 -t 4 -r 0x3647 localhost
```

See how the simulator refuses a request, for example an address outside every block:

```bash
mbpoll -m tcp -p 5020 -a 1 -0 -1 -t 4 -r 0x0001 localhost
```

Watch a value change by dropping `-1`; mbpoll then polls once a second until stopped.

Run the simulator's own healthcheck, which needs no client installed:

```bash
docker compose exec mock python -m saj_local_mock healthcheck; echo $?
```

Writes are kept across restarts in `mock/state/`, which Git ignores, and reset from the simulator page or by deleting the folder contents, see [Saved state](simulator-page.md#presets-saved-state-and-export). Addresses come from the profiles; the three above are only starting points.

## Configuring a scenario

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

Two sections shape the random behaviour and the faults at start; a third, `link`, is described under [Link faults](simulator-page.md#link-faults). `variation` sets the bounds, depth and period of the solar, load and grid generators (the load level stays in `site.load`), and `faults` lists the active fault bits per equipment by register and bit, plus battery pack codes:

```yaml
variation:
  cloud_depth: 0.9
faults:
  inverter:
    - {register: 0x4005, bit: 23}
  packs:
    - {pack: 1, fault: 1}
```

A wrong key or an impossible combination stops the simulator at start and names the key. The simulator writes the line to the error output and exits:

```text
invalid scenario: ev_charger.installed: not available on h2
```

## Running a different or extra system

**Try a scenario once**, without touching any file. The simulator runs in the foreground on its own port until you stop the simulator:

```bash
docker compose run --rm --no-deps -p 5030:502 \
  -v ./mock/scenarios/hs3-off-grid.yaml:/config/config.yaml:ro \
  -v ./mock/state/off-grid:/data \
  mock
```

The extra `-v` is needed because the `mock` service otherwise brings the `/data` mount of `mock/state/hs3/`, and the first change in the off-grid run would replace the development HS3 `state.json` with off-grid state. The off-grid run keeps its own state in `mock/state/off-grid/` across runs.

Point the first `-v` at your own file to run a scenario you wrote.

**Change what `make up` starts** in `compose.override.yaml`. Mounting another file over the same path replaces the scenario; a new service adds a system:

```yaml
services:
  mock:
    volumes:
      - ./mock/scenarios/hs3-ev.yaml:/config/config.yaml:ro

  mock-off-grid:
    build:
      context: ./mock
    volumes:
      - ./mock/scenarios/hs3-off-grid.yaml:/config/config.yaml:ro
    ports:
      - "5022:502"
```

Each service is an independent device with its own state. Home Assistant reaches the new service as `mock-off-grid`, so several systems can be added to one Home Assistant side by side.

## Extending the simulator

- **New scenario:** a file in `mock/scenarios/`. `make mock-smoke` picks up every file in the folder.
- **New model:** an entry in `models.py`, a profile in `profiles/`, and acceptance by the scenario validation in `scenario.py`.
- **New quirk:** in the layer that owns it. Framing and connections in the transport, addresses and access in the device, model behaviour in the profile.

The simulator passes the same gates as the integration, see the [checks page](checks.md).
