# Developing the SAJ Local Home Assistant Integration

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

- **SAJ library** (`custom_components/saj_local/saj/`): everything about SAJ devices and Modbus. It must not import Home Assistant, so device logic can be tested with plain inputs. It ships inside the integration; the split is a design boundary, not a package.
- **Home Assistant integration** (the rest of `custom_components/saj_local/`): config flow, entities, diagnostics, translations. Keep it thin. Logic that would be true without Home Assistant belongs in the library.
- **Frontend** (`frontend/`): the Lovelace cards. The build output is written into the integration directory because HACS ships that directory as one archive.
- **Modbus simulator** (`modbus_mock/`): a separate program that shares no code with the others. See [The Modbus simulator](#the-modbus-simulator).

The import contracts under `[tool.importlinter]` in `pyproject.toml` enforce these boundaries in the lint step.

### Device profiles

The library holds no per-model code. A model is a `Profile` declaration in `saj/profiles.py`: its device type codes, the semantic keys it supports and whether its register contract is hand-verified. One identity reader and one telemetry reader serve every profile, and one pure function resolves the model from the reported device type and the user's selection.

Keep it that way: a model that uses the same registers is a new `Profile` value and nothing else. A branch on a specific profile, in the library or in the integration, is a defect. The integration builds its Model dropdown from the library's profile list and never names a model.

A recognised device type is authoritative, so no selection can make the library treat a recognised device as another model. The detected model is never stored; it is derived from the device each time, and only the user's selection is saved. Setup and Configure share one validation routine so both enforce the same outcomes.

The library's model errors live in `saj/errors.py`, and an import-linter contract allows only the integration's `errors.py` to import that module. It is the single place that turns those errors into translation keys and placeholders, so a new error needs an edit there and nowhere else.

### Optional equipment

Rows of optional equipment carry an explicit `equipment` field on their `Definition`, set where the keys or families are defined and never derived from the key text. The catalogue serves the rows of a device type and a set of fitted equipment (`Fit`), so telemetry, load, control and the entities all work from the same set, and rows of equipment that is not fitted are never planned, read, offered in a polling group or writable. A profile declares one `Probe` per piece of equipment it can have: conditions on catalogue keys, any of which finds the equipment, and what an unanswered probe means. Catalogue construction rejects a probe whose key is missing, unreadable or itself tagged with equipment, and a combined value whose sources belong to other equipment, so a probe key always exists on every unit.

Detection (`saj/detection.py`) reads every probe key of the equipment being probed in one planned read through the telemetry reader, so probes whose keys share a block share a request; a model with rows for more than one battery pack adds the pack count to the same read. A refusal or an undecodable value is an answer and follows the probe's unanswered result, and a refused request leaves every probe it carried unanswered; a lost connection or a timeout is not an answer, and fails setup like any other read. The decision of what is fitted from the setting, the remembered set and the probe results is a pure function in `saj/equipment.py`, as is the pack limit: the highest valid count seen, forgotten with a battery set to Not fitted. The integration (`equipment.py`) stores the remembered set and the pack limit in the entry data before the platforms load, so no reload is triggered, reports remembered equipment that is no longer detected (a log warning, a diagnostics flag and a repair issue per installation and equipment), and removes the registry entries of rows that are not in the fit. The settings are entry options; the remembered set and the pack limit are entry data, which Configure preserves when it saves and drops when the unit is replaced.

Where a model has no hand-verified readings, its evidence is ranked: field tooling in sustained use and field reports first, then the model's document, and the simulator never. A row takes the evidence of the best source that covers it, so a row field reports confirm is `IMPLEMENTED` and enabled by default, and a row only the document defines is `DOCUMENTED` and created disabled. Where the document's English contradicts its Chinese the Chinese is used. A word with no meaning (reserved or pass-through words) is not an entity; it stays in the register snapshot. Settings that a wrong value would make dangerous are added to `COMMISSIONING_KEYS` when they are catalogued, so a model never exposes a writable row that is not protected by accident.

Both models place the grid import and export totals on the all-phase counters and the first-phase counters as `grid_l1_*` rows, so the keys mean the same on both. The H2 battery identity is one family indexed by pack (`battery_pack_identity`), five members at a fixed stride; the pack limit applies to it like every other pack row, and the highest pack row a model has sets its pack maximum, which is why the H2 maximum is five while its state, fault and energy families stop at four.

Whether a row is enabled by default follows its core mark for Meter A, Meter B, the EV charger and the parallel system (`ENABLED_WITHOUT_EVIDENCE` in `saj/models`), because those rows exist only when the equipment is fitted. Battery and inverter rows keep the evidence rule. Pack rows carry the pack index through the `PACK` family role, and the fit's pack limit removes the rows above it. A bit field can be inverted (`Definition.inverted`, `Format.inverted`), decoded and encoded in the codec, which is how `ev_ems_charging` shows charging on when the register bit is 0 while the packed-field read-modify-write keeps the other bits. A model's `Replacement` can turn a combined key into a single addressed register (`uncombined`), which is how the H2 reads each parallel power from one 16-bit register while the HS3 keeps combining low and high words under the same keys.

### Polling

The library decides what to read and when, and protects the device; the integration only presents the result. Polling rules live in the library because they describe the device, not Home Assistant, so no integration code can bypass them.

- **Schedule, budget, health and poller** (`saj/schedule.py`, `budget.py`, `health.py`, `poller.py`) each own one decision and take time and waiting as inputs. Nothing in them reads a clock or sleeps, which is what lets their tests run instantly and deterministically. Only the client's defaults and the coordinator's wiring touch real time.
- **One shared time grid per installation.** Cadences that are offset from each other would never share a request; a common grid lets coincident ticks be planned together, and dropping missed ticks stops an overrun from becoming a backlog.
- **The request budget is a device property.** It counts requests, because that is what field reports describe, and it is a library constant rather than a setting so that no configuration can exceed it. Waiting for the budget lengthens a cycle instead of dropping reads.
- **A response is classified, not treated as pass or fail.** A refused register is an answer from a healthy device and affects only its sensors; only busy and device-failure codes and link errors fail a cycle. This is why one refused block can no longer make every entity flap.
- **Failed cycles back off and never retry inside the cycle.** Retries multiply load exactly when a module is struggling. The single exception is a stale kept connection, which is not a device failure; it is reopened, identity is verified and the cycle becomes a full read so no published value predates the reconnect.
- **The budget and the back-off belong to the endpoint, not to a load** (`saj/guard.py`). A reload, a group edit or a setup retry builds a new client, and a budget or failure count held there would start from zero each time, which is how a module gets hammered by Home Assistant's own retries. The integration keeps one guard per host and port in `hass.data` for the life of Home Assistant and gives it to every client and poller, including the temporary client of a setup or Configure check. Loading asks the guard first and reports not ready before opening a connection; a check started by the user bypasses the back-off but not the budget. A check that passes resets the back-off, since the device has just answered and the load that follows should not be refused for a failure that has already healed; a failed check changes nothing, so a user retrying a bad address cannot extend or erase the protection.
- **Polling groups are config subentries.** They give native add, edit and delete on the integration page without changing Setup or Configure. A group stores semantic sensor keys, never entity IDs, and entities are never attached to a subentry, because Home Assistant deletes the entities of a deleted subentry and a group must not take a sensor or its history with it.
- **State is written only for sensors that were read** or whose availability changed, so a fast group does not make slow sensors look refreshed.
- **Wake-ups are rounded up.** Home Assistant schedules a coordinator on whole seconds, and a wake-up that fires early would find nothing due and waste a slot.

### Device faults and repairs

A fault is a model-neutral key with one name on every model that reports it. A model states, in its `Profile.faults` (`saj/models/hs3.py`, `h2.py`), which bits of which fault words report each key, and the fault words themselves are ordinary placed rows that are never entities (`Definition.exposed` is false). Bit positions are data, so correcting one changes no key. Conditions that both models report the same way are shared in `saj/models/shared_faults.py`; a model lists only what it differs in.

The catalogue builds the fault entities from that map instead of from placements: a named fault, an unrecognised row and a summary row per piece of equipment that has fault words, each a combined row whose `ANY_BIT` operation tests the bits of its source words. The summary also reads the battery pack words, which are plain rows of the `battery_pack_faults` family. Catalogue construction rejects a word that is not a placed row, a source that lies in no fault word or outside its word, a bit that two faults claim and a fault whose words belong to other equipment. Fault rows are enabled by default whatever their evidence, because the user chose that for every fault, and the planner keeps their source words in the request it already makes where the block is read anyway. `hidden_sources` gives the coordinator the words behind the enabled fault entities, so they are read even though no entity shows them, and diagnostics and the fault log use the raw words. Decoding of words to active faults and unrecognised bits, and the watch that turns two readings into raised and cleared faults, are pure library code (`saj/faults.py`).

All issue IDs, their raising and their removal live in `issues.py`: the equipment, model, refusal and unreachable issues. Library errors are never imported there; `errors.translate_error` supplies the translation key and placeholders that decide whether an error is a model finding. The refusal issue keeps its keys in its issue data, so a reload, which starts a fresh `ReadHealth`, can still clear a key that now answers. The unreachable issue reads the endpoint guard's failing-since time (`saj/guard.py`), which survives reloads like the rest of the guard, and is checked at every failed cycle and every load attempt, including a load ended by the back-off.

The fixes are Home Assistant repair flows (`repairs.py`). The model fix does not duplicate Configure: `EntryChanges` in `config_flow.py` holds the validation, the conflict checks and the save that Configure and the repair share, and the repair calls it with the saved settings and the model set to Automatic. For a loaded installation the validation borrows the coordinator's client (`async_validation_session`), which is closed when the session ends, even on failure. The session then requests a refresh, scheduled as a task so the form does not wait for a poll and run after the cycle lock is released. That poll sees a disconnected client and reconnects through `Poller._reopen`, which holds the identity check; a connected client would skip it, and until it ran writes and heartbeats would be refused as not connected. The unreachable issue appears at the first failed retry after 15 minutes, which back-off makes 15 to 20 minutes into an outage.

### Debug dump and logging

The register memory (`saj/memory.py`) lives in `ModbusTcpClient`, because the client is the one place every read passes through: polls, heartbeats, write read-backs, detection and identity all feed it with no code of their own. It records answered words per address and failed ranges per address and count, with the client's own clock so tests need no real time. Each `ModbusErrorMessage` that can reach the wire maps to one of four outcomes in `FAILURE_OUTCOMES`: refusals are `exception`, both timeouts are `timeout`, a failed connect, a peer close and an incomplete response are `connection_lost`, and a mismatched header or a malformed length, register count or acknowledgement is `malformed_reply`. A refused span or value never reaches the wire and is not remembered. Writes are not remembered as reads. A failure is dropped when the same range answers, and words stay with their own age, so a dump shows both what was last good and what has failed since. The snapshot is built on demand from the device's catalogue rows, so grouping by key costs nothing while polling.

Privacy is decided where the words are, not where they are shown. `Definition.private` marks the rows whose content identifies a person or a network; `private_rows` gives them plus the inverter serial range, which no row covers but which identity and the H2 identity block read. The snapshot never carries private words at all, not even to the integration, and marks the entry instead; `diagnostics.py` substitutes Home Assistant's redaction marker, which keeps the library free of Home Assistant. A read that covers only part of a private row is hidden whole, so a partial overlap cannot leak a word. The validation client of Setup, Configure and the repair forms must not pollute the dump: Configure on a loaded entry reuses the coordinator's client, so `async_validation_session` wraps it in `ModbusTcpClient.unremembered`.

Logging (`saj/log.py`) has to give every line a system label and keep Home Assistant's per-integration debug switch working. A `LoggerAdapter` built from each module's own logger does both, because the logger name is unchanged and only the message gains the prefix. The label is built from the entry title and the serial the entry was created with, which is known before identity has been read, so even the first line of a setup is labelled and the full serial, which the default title contains, never reaches a log. `label.py` builds it for integration modules, and setup passes the same text to every library object, which builds its own adapter. A poll line is assembled by the poller from the requests that went through its counting reader, so a failed poll still reports the requests it made, including one cut off by the cycle deadline, which is listed as a timeout.

### Stable names

Sensor names are a contract with every dashboard and automation a user writes. The library presents one set of names, units and formats across SAJ models, so a hardware upgrade keeps history wherever the old and new systems overlap. Map a new device onto the existing vocabulary before inventing names.

Entity IDs are part of the same contract. `sensor_object_id` in `const.py` is the only place the format is defined, and everything else (the sensor, the rename on a prefix change, the confirmation text, diagnostics) calls it. A sensor key is therefore part of an entity ID: renaming a key is a breaking change, rewording a label is not. Sensor unique IDs stay the config entry ID plus the key and are untouched by a prefix change. The prefix is a Home Assistant concern and lives only in the integration's entry options, never in the SAJ library.

A prefix change renames through the entity registry because that is what makes the recorder carry history and statistics to the new ID. The recorder refuses to move statistics onto an ID that already has them, so the change is checked first with one metadata lookup (`async_list_statistic_ids`) and every check is repeated when the change is saved, before the first rename.

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

- **Writes have one path.** An entity action calls `SajEntity.async_change`, which calls the coordinator's single `write` method. The EMS cleanup uses the same lock and error handling. The heartbeat is not a write: it reads each owned function's target through the library's keep-alive read, then the EMS limits through the library's limits read, under the same cycle lock, and uses no write slot. Only `custom_components/saj_local/errors.py` may import the library's errors; the rest go through it.
- **The simulator is not a source for write behaviour.** Writes are specified by the SAJ protocol documents and real readings. If the simulator departs from the documented `0x06` and `0x10` behaviour, that is a simulator defect to raise, not something to adjust the integration around.

## Code style

[code-style.md](../.github/work/code-style.md) is the authority. Its documentation rule shapes this guide: explain why, not how, and let names and types describe the rest.

## Docker

Development runs in containers so Home Assistant is a known, pinned release with a clean configuration.

- [compose.yaml](../compose.yaml): the interactive environment, Home Assistant plus the simulators. The integration is mounted read-only so the container never writes into the source tree.
- [compose.playwright.yaml](../compose.playwright.yaml): a throwaway Home Assistant with an HS3 simulator and an H2 simulator, for the browser smoke test that proves each endpoint can be added, loads, reports sensor values and, once control is allowed, shows a changed setting. It shares no state with the interactive environment.
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
