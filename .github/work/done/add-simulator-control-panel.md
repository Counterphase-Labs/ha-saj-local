# Add Simulator Control Panel

## Plan Metadata

- **Revision:** 1
- **Status:** Approved
- **Last revised:** 2026-10-16
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Roadmap item:** "Simulator control panel" in `../roadmap.md`
- **Builds on:** `../done/build-saj-modbus-mock-simulator.md`, `../done/add-device-faults-and-repairs.md`, `../done/add-full-h2-support.md` and the plans they build on. Everything in those plans that is not restated or explicitly replaced here continues to apply.

## Outcome And Scope

A developer opens a web page for each running simulator. From it they change the simulated system while it runs, without editing its scenario or restarting it, and they see the change in Home Assistant on its next poll. Changes made from Home Assistant show on the page within a few seconds.

| Need | Today | With this plan |
| --- | --- | --- |
| Change a writable setting | Write it over Modbus with a client tool | Pick or type it on the page. Enumerations are listed as `<raw code> <name>`, for example `6 EMS` |
| Put the device into a fault and take it out | Only `0x4007` bits, and only from the scenario file at start | Every fault bit the model has on the inverter, battery, battery packs and EV charger, named where the SAJ document names it and listed as `reserved` where it does not |
| Shape the randomness | Fixed constants and a fixed seed | Sliders and fields for the shape, bounds and speed of solar, cloud, load, grid voltage and frequency, plus the seed |
| Force a value | Not possible | Hold PV, load, grid voltage or frequency at a value, set the battery state of charge, plug the car in or out, reset the energy counters, move the clock and change its speed |
| Get back to a known state | Restart the container | Reset to the scenario, or apply a preset such as "High load" or "Grid lost" |
| Keep a tuned state | Lost on restart | Saved and restored across restarts. Exportable as scenario YAML so it can be committed and reproduced |

Included:

- An HTTP server in the simulator process, beside the Modbus server, on its own port.
- A description of the simulated model built from its profile: settings, commands, faults, variation parameters and overrides.
- One plain HTML page with vanilla JavaScript, served by the simulator. No libraries, no build step, no external requests.
- Variation parameters and overrides in the simulation, and the `variation` and generalised `faults` scenario sections.
- A fault map per model covering every fault register, and the fault effects listed below.
- Labels for enumerated settings.
- Persistence of the running state in a volume, reset, presets and scenario export.
- Compose ports and volumes, the smoke test, `documentation/development.md` and the requirement changes below.

Not changed: the integration, its tests and the browser smoke tests. The Modbus behaviour of the simulator is unchanged except that the registers listed under Faults now carry fault state and the version registers (`0x8F02`, `0x8F17` to `0x8F1B`, `0x0F03` on the HS3 and `0x8E09`, `0x8E0A`, `0x8E1D`, `0x8E1E` on the H2) now read their intended values 1000 to 1006 instead of the 65535 that an overflowing scale used to clip them to.

## Requirements

| Requirement | How it is met |
| --- | --- |
| The simulator can be configured to simulate different SAJ devices and their behaviours | The page is built from the model's description, so HS3 and H2 each get their own settings, faults and equipment without a page per model |
| Deterministic randomised behaviour with reproducible seeds | Variation stays a pure function of seed, parameters and simulated time. Every parameter the page changes can be written in the scenario, and the page exports the running state as a scenario |
| Behaviour believable and consistent, not every detail | Faults set the device's own bits, and a few have the effect the fault names, for example a battery too hot to charge stops charging |
| A standalone docker service | The page is served by the simulator itself and loads nothing from outside the container |
| 100% unit test coverage | Applies to all Python in the simulator, including the HTTP handlers, description, persistence and presets. The page is exempt under the requirement change below |
| Integration tests only as smoke tests | `make mock-smoke` checks that the page and its description answer |
| Development dependencies are not shipped | aiohttp is added to the simulator image and the test group only. The integration's manifest does not change |

## Requirement Changes

Added under "Modbus Mock" in `requirements.md`:

- Each running simulator offers a simple web page, served by the simulator itself, that changes the simulated system while it runs, without editing its scenario or restarting it.
- The page can set every setting a client can write, put the device into and out of every fault the model reports, shape the random variation (its bounds, depth, speed and seed), force readings such as power, state of charge and line voltage, and reset counters and the clock.
- The page builds its controls from the simulated model's own description, so a new model needs no page of its own. Raw values are shown with a short name, so the page is usable without the protocol document at hand.
- The page shows the current value of everything it controls, refreshed every few seconds, so a change made from Home Assistant is visible on it.
- Changes made on the page are kept across restarts. The page can reset the simulator to its scenario, apply ready-made presets for quick smoke testing, and export the running state as a scenario.
- The page is a development tool: plain HTML and JavaScript with no libraries, no build step and no tests of its own. The simulator code behind it is held to the same test rules as the rest of the project.

The design decisions in `documentation/development.md` that say the simulator is "fixed at start" with "no runtime control" and "no state outside the process" are rewritten to match.

## Decisions

Decisions 1 to 10 were made by the user on 2026-10-15. The others are set by this plan and listed so they can be challenged.

| # | Decision | Outcome |
| --- | --- | --- |
| 1 | Where fault codes and names come from | The SAJ documents and real-device observations: the same bit layout as the Device faults plan, with the document's names. The integration's code is not copied or referenced. Any disagreement between the two shows a defect on one side |
| 2 | What a fault does | It sets the device's own bits. Effects the fault's name describes are added where a real system does them (see Fault Effects). Nothing more is modelled |
| 3 | How raw values are shown | `<raw code> <short name>` in select lists, for example `11 TOU (BMS)`. Values without a name show the raw code only |
| 4 | Persistence | The running state is saved and restored across restarts, with a reset to the scenario and built-in presets |
| 5 | Page technology | One HTML file with vanilla JavaScript and CSS, no libraries, no build, no tests |
| 6 | HTTP server library | aiohttp, a development dependency of the simulator only |
| 7 | What the page controls besides settings | Readings and the shape of the random generators: bounds, depth, speed, spikes and holds, battery state of charge, energy counters, the clock |
| 8 | Seed and state changes | Changing the seed or a variation parameter changes the noise and phase weights from that moment. The battery, energy counters and clock carry on unless reset separately |
| 9 | Two clients | The page polls the state every 3 seconds. No locking: the last write wins, as on a real device |
| 10 | Requirement changes | As in Requirement Changes above |
| 11 | How a change reaches the device | A setting changed on the page goes through the same validation and the same written-field handling as a Modbus write. A page write therefore counts as a settings change, syncs EMS, keeps EMS alive where a Modbus write would, and runs commands. Raw values outside the field's range or options, or outside what its register can hold, are refused with the reason |
| 12 | Raw or scaled input | Settings are entered as raw register values. The scaled value is shown next to them. This keeps the page honest about what the device holds |
| 13 | Where the page is served | Port 8080 in the container, set by `server.panel_port` in the scenario. Compose publishes it as `${SAJ_MOCK_PANEL_HOST_PORT:-5080}` for the HS3 simulator and `${SAJ_MOCK_H2_PANEL_HOST_PORT:-5081}` for the H2. No authentication: the simulator is a development tool |
| 14 | What is persisted | The settings a client can write (fixed registers come from the code, so a change to one is never masked by an old file), fault state, variation parameters, holds, battery state of charge, energy totals with where each day, month and year started (so a restart is not a counter reset), the simulated clock and the EV hand state: whether a car is plugged in by hand with its remaining energy need (0 for a car that is complete), and the end of any scenario window kept shut after a hand unplug. A real inverter keeps its settings, counters and clock across a restart too. A saved file without EV hand state restores as no hand state, and one without period starts restores the totals and starts the periods from them, so the state version stays 1 |
| 15 | When state is saved | After every change from the page or a Modbus write, at most once a second, every 60 seconds while running, and on stop. The file is written to a temporary name and renamed, so a crash never leaves half a file |
| 16 | A saved state from a different scenario | The state file records a hash of the scenario. If the scenario changed, the saved state is ignored, the simulator starts from the scenario, and it logs one line saying so. The file is kept, not deleted. A saved setting is checked like a write (Decision 11); a saved state with a value a write would refuse is ignored the same way |
| 17 | What a preset does | Return settings, variation, seed, faults and holds to the scenario, then apply the preset's changes. Presets give a known set of conditions every time instead of stacking on whatever ran before. The simulated time, the clock speed, the energy counters and the battery state of charge carry on, unless the preset sets them (Battery empty and Battery full set the state of charge), so Home Assistant never sees the clock jump back or a lifetime total fall and record a meter reset. A preset does not delete the saved state; it marks the state changed so it is saved. Only Reset to the scenario rewinds everything |
| 18 | Presets on a model or system that lacks the equipment | Not offered. "EV charging" appears only where an EV charger is fitted, battery presets only where a battery is fitted |
| 19 | Bits the document does not name | Listed as `<register> bit <n> reserved`, so the integration's "unrecognised fault" path can be tested |
| 20 | Clearing faults | The clear-fault command `0x8015` follows the SAJ documents: value 2 (clear current fault) clears every active fault on every piece of equipment, and the page's "Clear all faults" sends it. Value 1 (clear fault history) leaves the active faults, because the simulator keeps no fault history |

## Behaviour

### The Model Description

`GET /api/description` returns everything the page needs to build its controls. The page contains no model names, addresses or field lists. Each variation parameter says whether its range suits a slider.

| Section | Content per entry |
| --- | --- |
| Model | Model name, rated power, phases, serial, fitted equipment (battery and pack count, Meter A, Meter B, EV charger, parallel inverters) |
| Settings | Name, address, group (the register block it sits in), raw encoding, scale, minimum, maximum, options with labels |
| Commands | Name, address, options with labels |
| Faults | Equipment (inverter, battery, pack n, EV charger), register, bit, name or `reserved`. Pack fault and warning words are a raw code, not bits, where no bit table exists |
| Variation | Name, group, minimum, maximum, step, unit, default (the scenario's value) |
| Holds | The readings that can be held, with their range and unit |
| Presets | Name and short description, only those that apply to this system |

Only equipment that is fitted appears. A setting in a block the device refuses, such as the EV charger block without a charger, is not listed.

### State And Writes

`GET /api/state` returns the current raw and scaled value of every setting, the active fault bits and pack codes, every variation parameter and hold, the simulated time and speed, and a small set of live readings so the effect of a change is visible: PV, load, grid, battery and EV charger power, battery state of charge, grid voltage and frequency, operating mode and running application mode. It also reports the current value of each reading a hold can fix, so the page starts a new hold where the reading is. Rounded readings never show a negative zero.

| Request | Effect |
| --- | --- |
| `POST /api/settings` | Sets one or more settings by name and raw value (Decision 11) |
| `POST /api/commands` | Runs a command by name and value, such as restart or clear faults |
| `POST /api/faults` | Sets or clears fault bits and pack codes |
| `POST /api/variation` | Sets variation parameters and the seed |
| `POST /api/holds` | Holds a reading at a value or releases it |
| `POST /api/battery` | Sets the state of charge now |
| `POST /api/ev` | Plugs the car in with an energy need, or unplugs it. A hand plug-in lasts until the car is unplugged by hand. A car whose need is met stays plugged in, complete and drawing nothing, until then. A hand unplug ends the session, and a scenario window open at that moment stays shut until it closes; scenario sessions then apply as normal |
| `POST /api/clock` | Sets the simulated time and speed |
| `POST /api/ledger/reset` | Sets every energy counter back to its scenario start value |
| `POST /api/reset` | Returns everything to the scenario, including the clock, the energy counters and the battery, and deletes the saved state |
| `POST /api/presets/<name>` | Applies a preset (Decision 17) |
| `GET /api/scenario` | The scenario as YAML with the running settings that the scenario can express: seed, variation, faults, equipment and start time |
| `GET /` | The page |

A refused request answers 400 with the reason in the same words the scenario parser uses, for example `app_mode: value outside enumeration`. Nothing is changed by a refused request.

The HTTP server runs on the same event loop as the Modbus server and calls the same machine directly, so a page change and a Modbus write never interleave inside a step. Page requests do not count toward the Modbus client limit.

### Enumeration Labels

Labels come from the SAJ documents and real readings. They are short names, not translations.

| Setting | HS3 | H2 |
| --- | --- | --- |
| Application mode | 0 Self-use, 1 Time, 2 Backup, 6 EMS, 11 TOU (BMS) | 0 Self-use, 1 Time, 2 Backup, 3 Passive, 10 Peak shaving, 14 Old mode |
| Anti-reflux mode | 0 Off, 1 Total power, 2 Phase current, 3 Phase power | Same |
| Mode outside time-of-use slots | 0 Standby, 1 Self-use | Same |
| LED | 0 All off, 1 Outer ring on, 2 Inner ring on, 3 All on | As the H2 document defines it |
| Meter mode | As the HS3 document lists them, for example 0 No meter, 3 Three-phase four-wire | As the H2 document lists them |
| Baud rate | 0 115200, 1 57600, 2 38400, 3 19200, 4 9600, 5 4800, 6 2400, 7 1200 | Same |
| Battery protocol | 0 Not in use, 24 SAJ-BU3 | As the H2 document lists them |
| EV charger mode | 0 Disabled, 1 Standard, 2 Time-based, 3 PV surplus, 4 EMS | — |
| EMS enable (HS3) | 0 Off, and every other combination of the four enable bits named by the bits it sets, joined with `+`: bit 0 Inverter, bit 1 Battery, bit 3 Inverter timeout exit, bit 5 Grid, for example `3 Inverter + Battery` | — |

Commands are labelled the same way: clear faults 1 Clear fault history, 2 Clear current fault; restart 1 Restart; clear energy history 1 Clear energy history; factory reset 1 Factory reset. Every other enumeration in the profiles gets labels the same way where its document names the values. Labels are optional data on the field. They do not change what the device accepts.

### Faults

Every fault register of the model carries state, instead of the fixed zeros served today.

| Equipment | HS3 | H2 |
| --- | --- | --- |
| Inverter | `0x4005`, `0x4007`, `0x4009`, 32 bits each | Same registers |
| Battery | `0x400B`, 32 bits, named from the BMS table | `0x400B`, 32 bits, all `reserved` (the H2 document has no table) |
| Battery packs | Pack 1 fault and warning words as raw codes | Packs 1 to 4 fault and warning words as raw codes, limited by the pack count |
| EV charger | `0x30AB` and `0x30AD`, 64 bits | — |

The simulator's fault map is a data table per model in the simulator's profiles, written from the documents' bit tables. It follows the bit layout of the Device faults plan, including its readings of the documents: the T-phase undervoltage bit, the HS3 BMS bits 26 to 29, the Chinese meaning where the H2 English contradicts it, and the EV charger byte layout.

The scenario's `faults` section becomes one list per piece of equipment, by register and bit (`inverter`, `battery`, `ev_charger`) plus `packs` as codes per pack, replacing `faults.inverter_fault_bits`.

### Fault Effects

| Fault | Effect |
| --- | --- |
| An inverter fault naming a grid, power-stage, temperature or safety condition (grid voltage or frequency, grid DC voltage or injection, grid phase fault, islanding, PV or DC bus or inverter overcurrent or overvoltage, battery port, charge voltage, discharge voltage, soft start and open circuit faults, output overload, off-grid output undervoltage, relay, insulation, leakage current, DC injection, current and arc faults, neutral to earth voltage, over and under temperature, controller memory) | The inverter stops: operating mode Fault, no PV, battery or export flow |
| Grid lost (`0x4005:23` or `0x4009:23`) | The inverter runs off-grid: no grid flow, the house is supplied from PV and battery |
| Meter communication lost | Meter A reads as absent, as when the grid is lost: its readings are zero, its status is off, and the energy management grid-point target is not applied. The inverter keeps running |
| Any other named inverter fault (communication, display board, fan, DRM0, authorisation, CT device, BMS device and DC-DC unit faults) | Its bit only |
| Battery too cold or too hot to charge | No charging |
| Battery too cold or too hot to discharge | No discharging |
| Battery total or cell overvoltage | No charging |
| Battery total or cell undervoltage | No discharging |
| Any other named battery fault, or a pack fault code other than 0 | No charging or discharging |
| Any named EV charger fault | The charger stops charging |
| A reserved bit, a pack warning code | Bit or code only |

Which inverter conditions stop it is data in the fault table, one effect per condition, not a comparison of names.

### Variation

The constants in the environment become parameters with today's values as defaults. Each can be set in a new `variation` scenario section and on the page.

| Group | Parameters |
| --- | --- |
| Solar | Peak scale (percentage of the configured string peaks), cloud cover depth, cloud cover period, passing cloud depth, passing cloud period, string jitter depth |
| Load | Base and peak (taken from `site.load`), drift depth, drift period, spike chance, spike size, spike duration |
| Grid | Nominal voltage, voltage swing, voltage period, nominal frequency, frequency swing, frequency period, phase imbalance |
| Seed | `simulation.seed`, 0 to 65535 |

A parameter change takes effect from the current simulated second. Noise remains a pure function of seed, parameters and time, so the same scenario reproduces exactly.

### Holds

PV power, household load, grid voltage and grid frequency can each be held at a fixed value. A held reading replaces the generated one before the energy balance, so every derived register stays consistent. Releasing a hold returns the generated value.

### Presets

A preset returns settings, variation, seed, faults and holds to the scenario, then applies the changes in the table (Decision 17). The simulated time, the clock speed, the energy counters and the battery state of charge carry on unless the preset sets them.

| Preset | Changes from the scenario | Offered when |
| --- | --- | --- |
| Clear sky | No cloud cover, no passing cloud | Always |
| Overcast | Peak scale 30%, deep cloud cover, frequent passing cloud | Always |
| High load | Base 1500 W, peak 9000 W, frequent large spikes | Always |
| Low load | Base 150 W, peak 1000 W, no spikes | Always |
| Unstable grid | Wide voltage and frequency swing with a short period | Always |
| Grid lost | Grid lost fault on both bits | Always |
| Inverter over temperature | Inverter over temperature fault | Always |
| Battery empty | State of charge 5% | Battery fitted |
| Battery full | State of charge 100% | Battery fitted |
| Battery too hot to charge | That battery fault | Battery fitted, model names the bit |
| Battery pack fault | Pack 1 fault code 1 | Battery fitted |
| Meter communication lost | Meter communication fault | Meter A fitted |
| EV charging | Car plugged in needing 20 kWh, charger in standard mode | EV charger fitted |

### The Page

- One page per simulator at `http://localhost:<panel port>/`.
- A header with the model, serial, simulated time and live readings, refreshed every 3 seconds.
- Sections built from the description: Settings (grouped by block), Commands, Faults (grouped by equipment), Variation (a slider and a number field for each parameter, kept in step; a parameter with more than 1000 steps between its bounds, such as the seed, has the number field only), Holds, Battery, EV charger, Clock, Presets, and Reset and Export.
- A control shows the device's current value. While a control has focus, polling does not overwrite it. A refused change shows its reason next to the control.
- The page works offline and stores nothing in the browser.

### Persistence

- The state file is `/data/state.json` in a named volume per simulator service.
- Without the volume the simulator runs as today and logs one line that changes will not be kept.
- Reset deletes the file and rebuilds the machine from the scenario. A preset does not delete it.
- The EV hand state is saved as the remaining energy need of a hand-plugged car, 0 when it is complete, and the second at which a window kept shut closes. A file without it restores as no hand state.

## Code Changes

| Area | Change |
| --- | --- |
| `simulation/environment.py` | Constants become a variation parameter object with today's values as defaults. Functions take it as an argument. Holds are applied by the plant before the balance |
| `simulation/plant.py` | Fault state per equipment, the fault effects (including Meter A lost, which the controller and the telemetry both honour), holds, a runtime seed and variation change, setting the state of charge, and plugging the car in or out |
| `simulation/telemetry.py` | Fault words for every fault register from the fault state |
| `profiles/` | Fault map per model with an effect per inverter condition, labels on enumerated fields, fault registers driven by telemetry instead of fixed zeros, and the version registers encoded as raw values 1000 to 1006 so they no longer clip to 65535 |
| `registers.py` | Optional labels on a field |
| `device.py` | A named write for one field through the same validation and observer as a Modbus write |
| `machine.py` | The description, the state, the control operations, reset, presets and the snapshot used by persistence |
| `scenario.py` | `server.panel_port`, the `variation` section and the generalised `faults` section, and export to YAML |
| New `panel.py` | aiohttp routes that translate requests into machine calls and answers |
| New `persistence.py` | Load, save, scenario hash, atomic write |
| New `presets.py` | The preset table and when each applies |
| New `static/index.html` | The page |
| `service.py` | Starts and stops the panel and the saver with the Modbus server. `__main__.py` is unchanged |
| `modbus_mock/requirements.txt`, `pyproject.toml` | `aiohttp==3.14.3` in the simulator image and the test group |
| `Dockerfile` | Copy the page, create `/data` owned by the simulator user, expose 8080 |
| `compose.yaml` | Panel ports and state volumes |
| `compose.playwright.yaml` | Unchanged: the Playwright stack already has no state volume or panel port, so every run starts from its scenario |
| Scenarios | Updated to the generalised `faults` section where they use faults |
| `tests/modbus_mock/smoke.sh` | Fetch the description and the page from each scenario |
| `documentation/development.md` | The control panel, its ports, persistence and reset, the presets, the new scenario sections, and the rewritten design decisions |

## Verification And Acceptance

Unit tests, each on one module with collaborators replaced:

- Variation: each parameter changes the shape it names; defaults reproduce today's values; the same seed and parameters give the same values.
- Plant: each fault effect; holds feed the balance; a seed change keeps the battery, counters and clock.
- Telemetry: each fault register reflects its fault state.
- Device: a named write is validated and observed exactly like a Modbus write.
- Machine: the description lists only fitted equipment and readable blocks; state reports what was changed; reset returns everything to the scenario; each preset gives the expected settings, variation and faults and keeps the time, the clock speed, the energy totals and the state of charge unless it sets them; the state reports the live value of each hold's reading.
- Scenario: the new sections parse, reject bad values with the key, and an exported scenario parses back to the same running state.
- Persistence: save and load round-trip; a changed scenario is ignored with a log line; a saved setting a write would refuse is ignored with a log line; a refused saved state keeps the file; period starts survive a restart and an older file without them still restores; a write is atomic; a missing volume does not stop the simulator.
- Panel: each route calls the machine and answers; a refused change answers 400 with the reason and changes nothing.

Smoke: `make mock-smoke` starts each scenario and fetches `/` and `/api/description`.

Manual acceptance, in `make up`:

1. Open both pages. Each shows its model's settings, faults and presets only.
2. Change the application mode on the HS3 page. Home Assistant shows it after its next poll.
3. Change the application mode from Home Assistant. The page shows it within a few seconds.
4. Apply "Grid lost". Home Assistant shows the grid lost fault and the inverter off-grid. "Clear all faults" clears it.
5. Apply "Battery too hot to charge" with PV surplus. Charging stops and the fault shows in Home Assistant.
6. Set a reserved bit. Home Assistant shows an unrecognised fault.
7. Restart the containers. The changes are still there. Reset returns the scenario.
8. Export the scenario, run it in a fresh simulator, and the variation matches.

`make ci` passes.

## Roadmap Changes

On delivery "Simulator control panel" is removed from the roadmap.

## Revision History

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-15 | First draft |
