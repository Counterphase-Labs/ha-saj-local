# Build SAJ Modbus Mock Simulator

## Plan Metadata

- **Revision:** 7
- **Status:** Approved
- **Last revised:** 2026-10-05
- **Requirements:** `../requirements.md` (Modbus Mock)
- **Code style:** `../code-style.md`
- **Approval record:** Revision 7 authorised by the user on 2026-10-06.

## Outcome And Acceptance

The `modbus-mock` container becomes a Modbus TCP device that Home Assistant and any other Modbus client can connect to and smoke test against without a real SAJ system. A mounted YAML file chooses the device (HS3 or H2) and its installed equipment. Values move believably over a simulated day, driven by a seed, and respond to writes.

The work is accepted when:

1. `make up` starts the mock listening on Modbus TCP, reachable from the Home Assistant container as `modbus-mock:502` and from the host on a published port.
2. Mounting a different scenario file at `/config/config.yaml` and restarting changes the simulated device: an HS3 scenario reports the HS3 device type and register layout, an H2 scenario reports the H2 ones.
3. Every shipped scenario starts, passes the container healthcheck and answers reads across every register block its device defines.
4. Equipment options change what the device exposes and how it behaves: EV charger, battery module count and size, second inverter, Meter B, PV strings, off-grid.
5. Two runs with the same scenario, the same simulated instant and the same sequence of writes return identical register values.
6. Power values balance at every instant: PV, battery, grid and load are consistent with each other, and state of charge and energy counters integrate from those powers.
7. Writes to writable registers are stored, read back, and change behaviour for the controls named under Simulation (application mode, charge and discharge schedules, EMS, EV mode, clock).
8. The device quirks listed under Device Quirks are reproduced.
9. Several mocks run at the same time, each its own compose service with its own scenario, and each is an independent device: adding one is a compose entry and nothing else.
10. `make ci` passes, including 100 percent line and branch coverage of the mock and the existing import contract that keeps the mock free of `homeassistant` and `custom_components`.

## Decisions Recorded

| Topic | Decision | Source |
| --- | --- | --- |
| Purpose | Basic smoke testing without a real system. Not a compliant, general-purpose Modbus server. | User, 2026-10-05 |
| Modbus layer | Written in the mock itself. An off-the-shelf Modbus package is not used, because the SAJ quirks must be built in. | User, 2026-10-05 |
| Devices | HS3 and H2, both built in this plan. | User, 2026-10-05 |
| Scope of device coverage | Every register block and behaviour each device defines is built, including equipment that is optional on a real installation. The codebase carries no commentary on how well any register is established. | User, 2026-10-05 |
| Configuration | One YAML file mounted at a fixed path, with ready-made scenarios shipped in the repository. | User, 2026-10-05 |
| Scenario path | `/config/config.yaml`, overridable with the `SAJ_MOCK_CONFIG` environment variable. | Default |
| YAML parser | `PyYAML`, the mock's only runtime dependency. | Default |
| H2 variant | H2 3-6K-S2 single-phase hybrid (device type `005AH`). | Default |
| Runtime control | None. A scenario is fixed at start; changing it means restarting the container. | User, 2026-10-05 |
| Multiple systems | Any number of mocks run side by side, one compose service each. | User, 2026-10-05 |
| Consistent data | Values are derived from one energy balance, never generated independently per register. | User, 2026-10-05 |

## Register Coverage

Each profile defines every register in the blocks below, with its size, encoding, scale, access mode, enumerations and fault bits.

HS3 (three-phase, device type `1610H`):

| Block | Addresses | Content |
| --- | --- | --- |
| Ethernet settings | `0F00H`-`0F2FH` | Header, MAC, DHCP mode, IP, mask, gateway, DNS. |
| EV charger data | `3024H`-`30BBH` | Identity, limits, status, per-phase values, session and total energy, fault words, timestamps. |
| Settings | `3600H`-`36EFH` | Header, seven charge and seven discharge slots, meter and RS485 settings, battery limits, application mode, anti-reflux, LED. |
| Realtime and energy | `4000H`-`4176H` | Status, faults, per-phase inverter, grid and off-grid values, PV strings, battery, power flows, directions, energy counters. |
| Parallel machines | `4200H`-`427CH` | Parallel mode and counts, system power totals, total battery capacity, energy counters. |
| EV charger settings | `4B00H`-`4B47H` | Header, enable, communication, mode, power, seven schedule slots, EMS command and current. |
| Five-minute averages | `513EH`-`51BEH` | Averaged power, voltage, current and battery values. |
| Factory commands | `8015H`-`8023H` | Write-only: clear faults, restart, clear history, factory reset, clock. |
| EMS | `8400H`-`8412H` | Enable bits, timeout, targets, limits. |
| Information | `8F00H`-`8F1CH` | Device type, rated power, serial number, product code, software and hardware versions. |
| Battery | `A000H`-`A037H` | Responds; every value reads zero. |
| Meters | `A03CH`-`A077H` | Meter A and Meter B status, per-phase values, reactive power. |

H2 (single-phase, device type `005AH`):

| Block | Addresses | Content |
| --- | --- | --- |
| Settings | `3604H`-`367CH` | Charge and discharge enable masks, seven charge and seven discharge slots, passive charge and discharge control, meter and battery settings, battery limits, application mode, anti-reflux, rated power, grid and PV protection limits, LED. |
| Realtime and energy | `4000H`-`4166H` | Status, faults, inverter, grid and backup values, PV strings, battery, power flows, directions, energy counters. |
| Factory commands | `8015H`-`8023H` | Write-only: clear faults, restart, clear history, factory reset, clock. |
| Peripheral information | `8E00H`-`8E63H` | BMS and battery module types and versions. |
| Information | `8F00H`-`8F1CH` | Device type, power class, protocol version, serial number, product code, software and hardware versions. |
| Battery | `A000H`-`A037H` | Battery count and capacity, up to four modules (state of charge, health, voltage, current, temperature, cycles, discharge energy), battery voltage and current limits. |
| Meters | `A03CH`-`A065H` | Meter A and Meter B status and per-phase values. |

## Boundaries

- Modbus TCP only. No Modbus RTU, no serial.
- Function codes `03H`, `06H` and `10H` only.
- The simulation is believable, not electrically exact: no reactive-power physics, no thermal model, no grid-code behaviour.
- Fault injection is limited to what a scenario file can state at start (see Scenario File). There is no runtime control channel.
- The integration, the SAJ library and the frontend are not touched.
- The mock keeps sharing no code with the integration or the SAJ library. Register knowledge lives in the mock independently.

## Design

### Package Layout

Under `modbus_mock/saj_modbus_mock/`:

| Module | Responsibility |
| --- | --- |
| `__main__.py` | Loads the scenario, builds the service, handles stop signals. Gains a `healthcheck` sub-command. |
| `service.py` | Lifecycle: starts the listener, runs until stopped, closes connections cleanly. |
| `scenario.py` | Reads and validates the YAML file into immutable scenario objects. All validation errors name the offending key. |
| `transport.py` | Modbus TCP framing: MBAP header, request parsing, response and exception frames, connection limit. Knows nothing about SAJ. |
| `registers.py` | Register field definitions and word encoding: unsigned and signed 16 and 32 bit, scaled values, fixed-width strings, packed time and bit fields, split high/low word pairs. |
| `device.py` | The address space: blocks of fields, read and write dispatch, access rules, mapping of failures to exception codes. |
| `clock.py` | Simulated time from a start instant, a speed factor and an injected monotonic time source. |
| `simulation/environment.py` | Seeded PV irradiance and household load as pure functions of simulated time. |
| `simulation/plant.py` | Instantaneous energy balance and its integration into state of charge and energy counters. |
| `simulation/battery.py` | Battery bank: capacity, limits, state of charge, per-module values. |
| `simulation/control.py` | Operating mode logic: self-use, time-of-use schedules, backup reserve, EMS. |
| `simulation/ev_charger.py` | EV charger state machine and charging sessions. |
| `profiles/hs3.py`, `profiles/h2.py` | Each device's blocks, fields, bindings from fields to simulation quantities, static values and quirks. |
| `profiles/fields.py`, `profiles/common.py` | Keyword-only field constructors, and the register groups both devices share. |
| `profiles/hs3_equipment.py`, `profiles/h2_extras.py`, `profiles/undocumented.py` | HS3 optional equipment blocks, H2-only registers, and the fixed raw values of unnamed HS3 registers. |
| `simulation/balance.py`, `simulation/ledger.py`, `simulation/telemetry.py` | The pure power-balance solver, the energy counters per period, and the derivation of every register source from the plant. |
| `machine.py` | Assembles clock, plant, settings and device for one simulated inverter and routes writes that have side effects. |
| `models.py`, `exceptions.py`, `healthcheck.py` | Per-model limits, Modbus exception codes, and the healthcheck client. |

Dependencies point one way: `service` → `transport` → `device` → `profiles` → `simulation` and `registers`. `transport` and `simulation` do not know about each other.

A profile is data plus small binding functions. Repeated structures (seven charge slots, seven discharge slots, seven EV slots, three phases, four battery modules, parallel machines) are generated from one definition each, so the copy-paste gate is not tripped and a slot cannot drift from its siblings.

### Modbus Transport

- `asyncio` stream server. Each request is answered in full before the next is read on that connection; requests across connections are serialised through the device so the simulation state is never read mid-update.
- The MBAP transaction identifier and unit identifier are echoed. A request for a unit identifier other than the configured one gets no reply.
- A malformed frame (wrong protocol identifier, length that does not match the function) closes the connection.
- Connections beyond `server.max_clients` are accepted and immediately closed. The default is two simultaneous clients for both devices.
- Read count above 125 registers, or a write count above 123, is an exception `03H`.

### Device Quirks

| Quirk | Behaviour | Applies to |
| --- | --- | --- |
| Unsupported function code | Exception `01H`. | Both |
| Read or write touching an address outside every block | Exception `02H`. | Both |
| Read that starts in a block and runs past its end | Exception `36H`, for example a read crossing `36EFH`. | HS3 |
| Read of EV charger data (`3024H`-`30BBH`) with no charger installed | Exception `30H`. | HS3 |
| Write to a read-only field, or read of a write-only field | Exception `02H`. | Both |
| Write of a value outside the field's range or enumeration | Exception `03H`. `8405H` accepts the full signed range. | Both |
| Multi-word field written partially | Exception `03H`. | Both |
| Block headers | Settings, Ethernet and EV setting blocks start with checksum, length, sequence and protocol-version words. The checksum is static per profile. | HS3 |
| Unnamed registers | Addresses inside `3661H`-`36EFH` and `8406H`-`840EH` that carry no named field still respond with fixed raw values, including `FFFFH` runs; `366CH` and `366DH` mirror device type and rated power. | HS3 |
| Registers shared with the H2 layout | The `A000H` battery block reads zero, and `4023H`-`4030H`, `3636H`-`363AH` and `364DH`-`3650H` return live data with the H2 meaning. | HS3 |
| EMS keepalive | Any read or write of an active EMS target register restarts the EMS timeout. Reads of other registers do not. | HS3 |


### Scenario File

Read once at start from `/config/config.yaml`. Unknown keys and invalid combinations stop the service with a message naming the key. Every key except `device.model` has a default, so a scenario states only what makes it different.

```yaml
device:
  model: hs3                 # hs3 | h2
  rated_power_w: 12000       # must be a rating the model exists in
  serial_number: HS3MOCK0000000000001
server:
  port: 502
  unit_id: 1
  max_clients: 2
  response_delay_ms: 0       # fixed delay before every reply
simulation:
  seed: 1
  start: "2026-06-21T05:00:00"
  speed: 1                   # simulated seconds per real second
site:
  grid_connected: true       # false = off-grid
  pv_strings:
    - peak_power_w: 6500
    - peak_power_w: 6500
  load:
    base_w: 350
    peak_w: 6000
battery:
  modules: 2                 # 0 = no battery
  module_capacity_ah: 100
  initial_soc_percent: 50
meters:
  meter_a: true
  meter_b: false
ev_charger:
  installed: false
  phases: 3
  max_power_w: 11000
  sessions:                  # when a vehicle is plugged in, simulated time of day
    - plug_in: "18:00"
      unplug: "07:00"
      energy_needed_wh: 30000
parallel:
  inverters: 1               # 1 or 2
faults:
  inverter_fault_bits: []    # bits set in the fault words from start
```

Model rules enforced at load: `ev_charger`, `parallel.inverters: 2` and three-phase values are HS3 only; H2 is single-phase; PV string count and battery module count are limited to what each model supports.

### Shipped Scenarios

In `modbus_mock/scenarios/`:

| File | System |
| --- | --- |
| `hs3-battery.yaml` | HS3 12 kW, two PV strings, battery, Meter A. This is the image default. |
| `hs3-ev.yaml` | The above plus a three-phase EV charger with an evening session. |
| `hs3-full-house.yaml` | Two parallel inverters, larger battery bank, Meter A and Meter B, EV charger. |
| `hs3-off-grid.yaml` | HS3 with battery and PV, no grid. |
| `hs3-no-battery.yaml` | HS3 with PV only. |
| `h2-battery.yaml` | H2 6 kW single-phase, two PV strings, two battery modules, Meter A. |
| `h2-no-battery.yaml` | H2 with PV only. |

### Simulation

**Clock.** Simulated time is `start + speed × elapsed monotonic time`. Writing the device clock (`8020H`) moves simulated time to the written value. The monotonic source is injected, so tests drive time explicitly.

**Determinism.** Irradiance and load are pure functions of `(seed, simulated time)`: a smooth daily curve plus noise drawn from a hash of the seed and the time bucket. Nothing depends on wall-clock time, request timing or a shared random stream. Integrated state (state of charge, energy counters, EV session energy) advances in fixed ten-second simulated steps on boundaries aligned to the simulated clock, up to the last boundary at or before the current simulated instant, whenever the device is read. The values reported for the current instant are computed for that exact second from the environment and the integrated state, without integrating a partial step, so the result does not depend on how often a client polls. Time-based behaviour that a client can observe to the second (EMS timeout, restart countdown, schedule and EV session boundaries) stays accurate to the second.

**Response time.** Catching up must never make a client wait noticeably: a read after one simulated day without any request completes in under half a second.

**Environment.** PV follows a clear-sky bell between sunrise and sunset for the start date, scaled per string by `peak_power_w`, with cloud dips. Load is a base level with morning and evening peaks and short appliance spikes.

**Energy balance.** Only irradiance and load are generated. Every other power value is computed from them, so the registers always agree with each other: with PV at 10 kW, a full battery and a 1 kW load, the device reports 9 kW export, zero battery power, and the matching per-phase, meter, direction and counter values. At each step: load is met by PV, then battery, then grid; PV surplus charges the battery, then exports. The control logic below replaces that default priority when a mode asks for it. Inverter rating, battery charge and discharge limits, state-of-charge limits and export limit clamp the flows. Phase values split totals across phases with a fixed, seeded imbalance; voltages and frequency vary slightly around nominal; currents and apparent power derive from power and voltage. Direction registers follow the sign of each flow.

**Battery and size.** Capacity is `modules × module_capacity_ah` at the model's nominal module voltage. It sets how fast state of charge moves and the charge and discharge power limits. It is reported where each device reports it: H2 through `A000H` (`BatNum`), `A001H` (`BatCapcity`), `A00AH` (`BatUserCap`), the per-module `A00CH` onward and the peripheral block `8E00H` onward; HS3 through `420BH` (`paralltotalcap`). Inverter size is reported by both through `8F01H` and `366DH`.

**Control.**

- Application mode (`3647H`) selects self-use, time-of-use or backup behaviour. On the HS3, mode `11` is also accepted and behaves as self-use.
- The seven charge and seven discharge slots, their enable masks, weekday masks and power percentages drive forced charge and discharge during their windows in time-of-use mode.
- Charge upper limit, discharge lower limit and backup reserve bound the battery.
- Anti-reflux settings cap export.

**EMS (HS3).** Implements `8400H`-`8405H` and `840FH`-`8412H`:

- Enable bits 0, 1, 3 and 5 select inverter control without timeout exit, BMS control, inverter control with timeout exit and grid-point control. Targets are in 0.01 percent of rated power; positive inverter and grid-point targets sell and negative buy, positive BMS targets discharge and negative charge.
- While any enable bit is set, `4022H` reads `6` and the selected target overrides the application mode. Buy and sell limits and battery current limits clamp it. The PV limit applies only while an enable bit is set; `FFFFH` is unrestricted.
- Grid-point control needs Meter A and a single inverter; without them the bit is stored but has no effect.
- When the timeout (`8401H`) elapses without keepalive, the active target is cleared; with bit 3 the device also leaves EMS. `FFFFH` disables the timeout.
- Clearing `8400H` returns the device to its application mode.

**EV charger (HS3).** With a charger installed, the EV setting block (`4B00H`-`4B47H`) and data block (`3024H`-`30BBH`) are live. A session follows the scenario's plug-in and unplug times through idle, ready, charging, suspended and complete. Charging power depends on `EV_Mode`: forced at the configured power, inside the seven EV schedule slots, from PV surplus (with the minimum-current bit), or from the EV EMS command and current registers. Charger load is added to site load. Session energy, total energy, session start and end timestamps, per-phase voltage and current, control-pilot voltage and duty are derived from the session. With no charger installed, `EV_EN` reads `0` and the data block returns exception `30H`.

**Parallel (HS3).** The parallel block (`4200H`-`427CH`) always responds. With one inverter it reports a single machine whose totals equal the unit's own. With two it reports two machines, doubled inverter and battery capacity, and system totals of which this unit carries half.

**Meters.** Meter A reports the grid connection point per phase, with the status word online. Meter B, when present, reports a seeded external PV inverter and adds its generation to the site. An absent meter reads status offline and zero values.

**Off-grid.** With `grid_connected: false` the operating mode register (`4004H`) reports off-grid, grid-side values read zero, the off-grid output registers carry the load, and Meter A reads zero. PV is curtailed when the battery is full. When the battery reaches its discharge limit and PV cannot cover the load, the load is shed to zero until state of charge recovers above the limit.

**Five-minute averages (HS3).** The `513EH`-`51BEH` block is the mean of the integration-step values over the previous complete five simulated minutes; before the first complete window it is the mean of the steps so far.

**Factory commands.** Clearing fault history or the current fault clears the fault words. Clearing power history zeroes the energy counters. Factory reset restores every writable register to the scenario's start values. Inverter restart reports the waiting state and the grid-synchronisation countdown before returning to running. Ethernet setting writes are stored and read back; they do not change the listener.

### Multiple Mocks

One container is one device. A mock holds no state outside its own process, writes nothing to disk, and reads only its mounted scenario, so instances cannot affect each other. A further system is one more compose service using the same image with a different scenario mounted and a different published host port:

```yaml
  modbus-mock-h2:
    build:
      context: ./modbus_mock
    volumes:
      - ./modbus_mock/scenarios/h2-battery.yaml:/config/config.yaml:ro
    ports:
      - "5021:502"
    restart: unless-stopped
```

Home Assistant reaches each by its service name on port 502. Every shipped scenario carries a distinct serial number and seed, so two mocks added to Home Assistant are distinguishable devices with different weather and load. `compose.yaml` ships with two services, `modbus-mock` (HS3) and `modbus-mock-h2` (H2), so the multi-system case is the default development setup.

### Healthcheck

`python -m saj_modbus_mock healthcheck` connects to the local listener, reads the device type register and exits zero when the reply matches the scenario's model. It is the container healthcheck and what `make mock-smoke` uses.

## Implementation Phases

Each phase ends with `make ci` passing.

### Phase 1 — Scenario, transport and device core

- `scenario.py`, `registers.py`, `device.py`, `transport.py`, `clock.py`; `service.py` and `__main__.py` rewritten around them.
- Add `PyYAML` pinned in `modbus_mock/requirements.txt` (installed by the Dockerfile) and the same pin in the `test` dependency group; add its type stubs to the `lint` group.
- Dockerfile: install requirements, copy `scenarios/hs3-battery.yaml` to `/config/config.yaml`, expose 502, declare the healthcheck.
- `compose.yaml`: `modbus-mock` mounts `./modbus_mock/scenarios/hs3-battery.yaml` at `/config/config.yaml` read-only and publishes `5020:502`; a second service `modbus-mock-h2` is added in Phase 6 on `5021:502`. `compose.override.yaml.example` shows how to mount another scenario.
- A minimal HS3 profile (information block only) proves the path end to end.

### Phase 2 — Simulation core

- `simulation/environment.py`, `plant.py`, `battery.py`, `control.py` with self-use behaviour, limits and counters.

### Phase 3 — HS3 base profile

- Information, realtime, energy, Meter A, settings and schedules, Ethernet, five-minute averages, factory commands, unnamed registers, registers shared with the H2 layout, block quirks.
- Time-of-use and backup control.
- `hs3-battery.yaml`, `hs3-no-battery.yaml`.

### Phase 4 — HS3 EMS

- EMS registers, control override, keepalive and timeout.

### Phase 5 — HS3 optional equipment

- EV charger, Meter B, parallel inverters, off-grid.
- `hs3-ev.yaml`, `hs3-full-house.yaml`, `hs3-off-grid.yaml`.

### Phase 6 — H2 profile

- Information, peripheral information, realtime and energy, battery modules, meters, settings and schedules, passive charge and discharge registers, factory commands.
- `h2-battery.yaml`, `h2-no-battery.yaml`.
- `modbus-mock-h2` service in `compose.yaml`.

### Phase 7 — Make targets, CI and documentation

- `make mock-smoke`: for each shipped scenario, start the container with it mounted, wait for healthy, stop; then bring up both compose mock services together and confirm each reports its own device type. Added to `ci` and to the CI `mock` job after `mock-build`.
- README: how to pick a scenario, the scenario keys, the published port, and how to point the integration at the mock.

## Testing

The mock is covered by unit tests only, in `tests/modbus_mock/`, one test file per source module. They carry the 100 percent line and branch coverage gate on their own, and follow `code-style.md`.

A unit test here exercises one module through its own public interface with plain inputs. Every collaborating module is replaced by a stub, fake or recorder; plain value objects are built by hand. A unit test opens no socket, starts no server, reads no shipped scenario file, uses no real time, and steps the unit only as far as the behaviour under test needs. The whole mock suite runs in a few seconds.

There is no integration test tier in pytest. The assembled service is proven once, at container level, by `make mock-smoke`.

| Module | What its unit tests prove |
| --- | --- |
| `registers` | Every encoding round-trips, including negative values, clamping, string padding, clock packing and multi-word order. |
| `scenario` | Defaults, model rules, and each validation failure naming its key; unreadable and invalid files. |
| `clock` | Simulated time follows the injected time source and speed; setting it re-anchors. |
| `transport` | Bytes in, bytes out against a stub register bank: each function code, echoed identifiers, each exception path, malformed frames, unit filtering, the client limit and shutdown, using in-memory streams. |
| `device` | Read and write dispatch over hand-built blocks: gaps, partial multi-word access, access rules, range and enumeration checks, block overrun, unavailable blocks, observer notifications, atomic writes. |
| `profiles/*` | Each builder returns fields inside their block with no overlaps, and scenario options change the result: charger gate, phase count, battery present, meters, parallel. |
| `simulation/environment` | Same seed and instant give the same value whatever the call order; another seed gives another value; daylight and load shapes. |
| `simulation/balance` | Flows always sum to the load; surplus exports once the battery is full; limits, export cap, PV limit, offline and off-grid shedding and curtailment. |
| `simulation/battery`, `ledger` | State of charge and limits from power and time; counters accumulate and roll over by day, month and year. |
| `simulation/control` | Mode, schedule windows and weekdays, backup reserve, anti-reflux, EMS targets, limits, keepalive and timeout. |
| `simulation/ev_charger` | Session life cycle and charging power for each mode. |
| `simulation/plant` | Its own orchestration with every collaborator stubbed: first sample on first use, step count, shedding hysteresis, restart, clock jump, averaging window. |
| `simulation/telemetry` | Register sources derived from a stub plant. |
| `machine` | Glue with collaborators stubbed: EMS enable and mode restore, keepalive routing, each factory command, clock write. |
| `service`, `healthcheck`, `__main__` | Lifecycle, health outcomes and exit codes with the server, connection and signal handling faked. |

## Revisions

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-05 | Initial draft. |
| 2 | 2026-10-05 | At the user's direction: several mocks run side by side as separate compose services, with a second H2 service shipped in `compose.yaml`; restart-to-reconfigure confirmed; the energy balance is stated as the single source of every power value. |
| 3 | 2026-10-05 | At the user's direction, removed every pointer to material outside this repository and replaced the sources section with the register coverage of each device. No change to scope or design. |
| 4 | 2026-10-05 | H2 register coverage now gives the exact address range of every block and includes the H2 factory command block. No change to scope or design. |
| 5 | 2026-10-05 | At the user's direction, the Testing section now requires unit tests only: one module per test file with collaborators stubbed, no sockets, no assembled simulator and no simulated days. The earlier section specified integration tests under the unit coverage gate, which was wrong. |
| 6 | 2026-10-05 | At the user's direction, integration steps are ten simulated seconds instead of one, with the reported instant computed exactly and a response-time limit added, because one-second steps made a read after a long gap block for seconds. Five-minute averages before the first complete window are stated. |
| 7 | 2026-10-05 | Corrected the HS3 realtime block end to `4176H` (the total export counter occupies `4175H`-`4176H`) and added the modules that exist beyond the original layout table. No change to scope or design. |
