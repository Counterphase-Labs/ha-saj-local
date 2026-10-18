# Add Model-Neutral Power Control With Schedules

## Plan Metadata

- **Revision:** 1
- **Status:** Approved
- **Last revised:** 2026-10-12
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Roadmap item:** "Power control" in the [Roadmap project](https://github.com/orgs/Counterphase-Labs/projects/1)
- **Builds on:** `add-opt-in-register-writes.md`, `add-optional-equipment-detection.md` and the plans they build on. Everything in those plans that is not restated or explicitly replaced here continues to apply.

## Outcome And Scope

Every SAJ system that can be told to hold a power gets the same thing, whatever its model: the same entities, in watts, and the option of following a Home Assistant schedule helper. How the inverter is made to do it differs per model and stays inside the model.

A **power control function** holds one point of the system at a set power:

| Function | What it holds |
| --- | --- |
| Battery | The battery charges or discharges at the set power |
| Grid | The grid connection point imports or exports at the set power |
| Inverter | The inverter takes in or puts out the set power |

Each model states which functions it has and how each is done. Nothing in the integration, the forms or the entities names a model.

| | Today | With this plan |
| --- | --- | --- |
| Holding a power | HS3: raw EMS switches and targets in % of rated power. H2: raw application mode, passive direction and passive powers in % | The same switch and the same target in watts per function, on every model that has the function |
| Running it for a period | An automation the user writes, different per model | A Home Assistant schedule helper, attached to the system |
| Model-specific rows | — | Unchanged. They stay what they are: the inverter's own registers |
| Setup and Configure | — | Unchanged |

Included:

- The power control functions in the library, and how the HS3 and the H2 each do them.
- A switch and a power target per function a system has.
- Power control schedules: attaching a Home Assistant schedule helper to a function, and following it.
- Diagnostics, logging, translations, README and the roadmap update.

## Requirements

`../requirements.md` has the non-functional requirement of an abstraction across SAJ systems with consistent names, values and formats. The user approved these two lines for its Writing section on 2026-10-11 and they are in place:

- Power control (holding the battery, the grid connection point or the inverter at a set power) is offered the same way on every model that can do it: the same entities, in watts. How it is done on the inverter belongs to its model
- Optionally, a power control function can follow a Home Assistant schedule helper the user picks. The integration switches the function on when the schedule turns on and off when it turns off

Requirements this plan is held to:

| Requirement | How it is met |
| --- | --- |
| An abstraction layer across SAJ systems: consistent names, values, formats | One set of keys, one unit and one sign for power control on every model |
| Convention over configuration; avoid pages of complex config flows | Times and weekdays are edited in Home Assistant's own schedule helper. Setup and Configure gain nothing. A schedule is a separate addition of two fields |
| Write requires opt in | Power control does nothing while Allow control is off |
| A system whose model could not be verified is never written to | Power control does nothing on a model override |
| After a change, the entity shows the value the inverter actually holds | The switch shows whether the inverter reports the function running, and the target shows the power the inverter holds, in watts |
| Changes are rate limited | Every write is counted against the write allowance |
| EMS functions switched on from Home Assistant are kept alive by a heartbeat and switched off when Home Assistant stops | Unchanged, and extended: any function switched on through power control is switched off on unload and on stop, on every model |
| Platform stability and correctness is paramount | A switch-off is repeated until the inverter confirms it |
| SAJ implemented as a stand-alone library | Functions, methods, conversions and what to do next are library code with no timer and no Home Assistant import |
| Sensor names must remain stable | No existing key or entity ID changes. New keys are fixed here |
| Full localisation | Every new entity name, field and message is a translation key |

## Decisions

Decisions 1 to 5 were made by the user on 2026-10-11. Decisions 6 to 18 are set by this plan and listed so they can be challenged.

| # | Decision | Outcome |
| --- | --- | --- |
| 1 | What is built | Power targets in watts, and schedules |
| 2 | Whether it is built per model | No. One abstraction, with as near the same functionality on every system as its inverter allows. How it is done belongs to each model |
| 3 | What a schedule is | A native Home Assistant schedule helper. The integration has no schedule form of its own |
| 4 | Where a schedule is attached | As a separate addition to the system, like a polling group. Not in setup or Configure |
| 5 | Which systems get it | Any system whose model has the function. Nothing tests for a model |
| 6 | What the user is given | Per function a `switch` and a `number`, with the same keys on every model. See Entities |
| 7 | What happens to the model-specific rows | Nothing. The HS3 EMS rows and the H2 passive rows keep their keys, units and behaviour. Power control is a layer over them |
| 8 | Sign of a power | Positive discharges, exports or puts out. Negative charges, imports or takes in. The same on every model |
| 9 | Whether two functions may run at once on a system | No. No function has been exercised together with another |
| 10 | Which HS3 inverter enable bit is used | `ems_inverter_control_with_timeout_exit`: when the inverter's own timeout fires it leaves EMS |
| 11 | What the H2 is returned to | The application mode it was in before. It is stored with the system so a restart does not lose it. When it is not known, self-use |
| 12 | Where a schedule's power comes from | From the schedule block's additional data, `power` in watts, when the block has it. Otherwise the function's target |
| 13 | What a schedule does when its function is already running, or is switched off while the schedule is on | Already running: it takes the function over. Switched off meanwhile: nothing, until the schedule next turns on |
| 14 | Whether the write allowance can hold back a switch-off | No. The exemption the EMS switch-off has becomes the exemption of any power control switch-off |
| 15 | Which functions each model has | HS3: Battery, Grid, Inverter. H2: Battery. See Evidence |
| 16 | When an operating-mode function counts as running | While the inverter is in the method's mode, whatever the direction. Standby inside the mode is the function running at 0 W, as a target of 0 is on an enable-bit model |
| 17 | How a start learns that another function is running | By reading the other functions' state rows afresh before anything is written. It does not depend on which entities are enabled |
| 18 | What happens to a start that fails part way and cannot be undone | The function is owned and its stop is outstanding: it is sent again each heartbeat interval until confirmed, with or without a schedule |

## Rules Replaced From Earlier Plans

| Earlier rule | Now |
| --- | --- |
| No EMS register is written when an installation loads, reloads or reconnects. | Unchanged without a schedule. A function whose schedule is on starts after the first successful polling cycle |
| An EMS function found already on is left on and not owned. | The same for any function on any model, except one whose schedule is on: Decision 13 |
| The switch-off on unload and stop works only for the EMS enable bits and is the one write the allowance does not refuse. | It works for the switch-off of any power control function |
| EMS functions are owned, kept alive and switched off on the way out. | Ownership is of a power control function. The heartbeat stays what it is and applies to a function whose model says it needs one |

## Evidence

The mock is not a source for anything in this plan. The sources and their order of authority are those of the catalogue plan: real readings, field implementation, SAJ protocol documents.

### HS3

Real readings:

| Finding | Detail |
| --- | --- |
| Rated power | `0x8F01` read 12000 |
| Each function works on its own enable bit | Bit 1 battery, bit 5 grid, bit 3 inverter, each put the inverter under control within seconds without touching the application mode |
| Targets are a share of rated power | `0x8405`, `0x8411` and `0x8402` are each confirmed at 0.01 % of rated power: 500 gave about 600 W, 1000 about 1200 W |
| Sign | Positive sells or discharges, negative buys or charges |
| A target does nothing while its bit is clear, and clearing the bit leaves the target | Seen for each function |
| Clearing the bit ends control within about 8 seconds | The inverter returns to the mode it was in before, by itself |
| Grid control held its target at the meter as the load changed | With Meter A online |
| The inverter's timeout | Fired at 5 seconds under bit 3. Did not fire at 20 or 60 seconds while another client was polling. A controller must clear the bit itself |
| Combined enable bits | Not exercised |

### H2

| Finding | Source |
| --- | --- |
| Rated power is `0x8F01` in W | Field implementation, settled in the H2 plan |
| Application mode 3 is passive mode. `0x3636` is 0 standby, 1 discharge, 2 charge, in effect in passive mode | H2 document |
| `0x3639` battery charge power and `0x363A` battery discharge power are a share of rated power in steps of 0.1 %, range 0 to 110 % | H2 document |
| Charging the battery at a set power by: application mode 3, the charge power, then direction 2. Ending it by: direction 0, then the application mode back | Field reports of sustained daily use |
| Direction 0 inside passive mode is a standby of its own: the unit stays in passive mode | Field reports |
| Discharging by direction 1 and the discharge power | Field implementation |
| A timeout or keep-alive for passive mode | None in any source |
| `0x3637` and `0x3638`, passive grid charge and discharge power | Named by the H2 document with no meaning given. No source shows what they do, so no Grid function is built on them |
| A register that holds the inverter or the grid connection point at a power | None in any source |

None of the H2 writes has been exercised by this project. The README says so.

### Home Assistant

The schedule helper, in the version this project pins: its state is `on` inside a time block and `off` outside, and a block's additional data is exposed as state attributes while the block is active.

## Behaviour

### Entities

For each function a system has:

| Key | Entity | Meaning |
| --- | --- | --- |
| `battery_power_control`, `grid_power_control`, `inverter_power_control` | `switch` | On while the inverter reports the function running |
| `battery_power_target`, `grid_power_target`, `inverter_power_target` | `number`, W, whole watts | The power the function runs at |

- Entity IDs follow the existing rule: `switch.saj_battery_power_control`, `number.saj_battery_power_target`, with the prefix when one is set.
- A function's entities exist only when the system's model has the function and its equipment is fitted: Battery needs the battery, Grid needs Meter A.
- They are created disabled and in the configuration category, like the other controls.
- The target's range is what the model gives: minus to plus rated power on the HS3, minus to plus 110 % of rated power on the H2.
- A value is rounded to the nearest step the inverter has: 1.2 W on a 12000 W HS3, 8 W on an 8000 W H2. The entity shows what the inverter holds.
- They are not read rows and are not offered in polling groups.

Switching on:

| Step | Behaviour |
| --- | --- |
| No target has been set | Refused: set a power first. Nothing is sent |
| Another function is running on the system | Refused, naming it. Nothing is written. The state rows of the system's other functions are read afresh for this, in one request where they share a register, so a function started outside Home Assistant is seen whatever entities are enabled |
| Otherwise | The model's start, at the target. See How Each Model Does It |

Setting the target:

- While the function is running it is sent to the inverter at once, by the model's change of power.
- While it is not running it is kept by the integration, survives a restart, and is sent when the function starts.

Switching off is the model's stop.

The switch and the target follow the inverter. A function started with the model's own rows, or by something else, shows as on.

### How Each Model Does It

A model file states, per function, a method and the rows it uses. There are two methods. A third way of working is a third method; a model that works one of these two ways is data only: no module outside a model file names a row key of a model. Everything the library and the integration do about a function, for the power control entities and for the model's own rows alike, comes from the statement.

**Enable bit.** HS3, all three functions.

| | Rows | Requests |
| --- | --- | --- |
| Start | Read the state rows of the other functions, write the target row, then set the enable bit by the existing switch-on, with its timeout check and its alternate forms cleared | 5, 2 of them writes |
| Change of power | Write the target row | 1 |
| Stop | Clear the enable bit. The target is left | 3, 1 a write |
| Running | The enable row or one of its alternate forms is set. The state rows of the function are all of them | — |
| Power held | The target row, read only by the heartbeat while the function is owned | — |
| Kept alive | By the existing heartbeat | — |

The statement of an enable-bit function names: the enable row; the alternate enable rows, which are other forms of the same function and exclude it; the target row; the timeout row that the switch-on checks against the heartbeat, when the model has one; and the limit rows read with the heartbeat, when the model has them. The exclusive bits, the timeout check, the heartbeat and the limits read that the writes plan gave the HS3 EMS rows are unchanged in behaviour and are driven by this statement.

| Function | Enable row | Alternate enable rows | Target row | Held as |
| --- | --- | --- | --- | --- |
| Battery | `ems_battery_control` | — | `ems_battery_power_target` | Signed share of rated power, 0.01 % |
| Grid | `ems_grid_control` | — | `ems_grid_power_target` | The same |
| Inverter | `ems_inverter_control_with_timeout_exit` | `ems_inverter_control` | `ems_inverter_power_target` | The same |

On the HS3 every function names `ems_timeout` as its timeout row and the five EMS limits as its limit rows.

**Operating mode.** H2, Battery.

| | Rows | Requests |
| --- | --- | --- |
| Start | Write the power row of the direction, read `application_mode` and remember it unless it is already passive, write `application_mode` to passive, write `passive_mode` to the direction | 7, 3 of them writes |
| Change of power | Write the power row of the direction, then `passive_mode` when the direction changes | 2 or 4 |
| Stop | Write `passive_mode` to standby, then `application_mode` to the remembered mode | 4, 2 of them writes |
| Running | `application_mode` is passive. Standby is running at 0 W | — |
| Power held | The power row of the direction `passive_mode` shows, negative for charge, and 0 in standby | — |
| Kept alive | Nothing to do | — |

| Function | Charge power row | Discharge power row | Held as |
| --- | --- | --- | --- |
| Battery | `passive_battery_charge_power` | `passive_battery_discharge_power` | Unsigned share of rated power, 0.1 % |

- A power of 0 on the H2 is direction standby. The function is still running, at 0 W: the switch stays on, and a later power is sent like any change of power.
- A stop that gets its first write through and not its second is outstanding: the inverter is still in the mode, so the function is still running and owned, and the mode is put back at the next attempt.
- The remembered mode is stored with the system. It is cleared when the stop completes, and when a polling cycle reads the inverter out of the mode: someone else has chosen a mode and it is not overwritten.
- Every write is an ordinary write: validated, sent once, read back.
- A start that fails part way is stopped again. When that stop fails too, the function is owned and the stop is outstanding: it is sent again each heartbeat interval until it is confirmed or a polling cycle reads the function as not running, whether or not a schedule exists. Unload and stop switch it off like any owned function.

### Ownership

What the writes plan says of an EMS function owned by the installation holds for a power control function on any model:

- A function switched on through power control is owned until it is switched off, a polling cycle reads it as not running, or the installation unloads.
- This holds on every model with no exception: an operating-mode function is released when a polling cycle reads the inverter out of the mode.
- An owned function is switched off when the installation unloads and when Home Assistant stops, bounded to 5 seconds, not held back by the write allowance.
- The switch-off that the allowance does not refuse accepts only the writes of a stop of one of the device's functions, with the values a stop has: an enable row to off; the direction row to standby; the mode row to a mode other than the method's own. Any other key or value is refused.
- A function found running at load is left running and not owned.
- On a model with no keep-alive and no timeout, a function left running by a Home Assistant that stopped abruptly keeps running. The README says so, per model.

### Adding A Power Control Schedule

The user makes a schedule helper in Home Assistant, with its times and weekdays, as for any other use.

A **power control schedule** is then added from the system's page, the same way a polling group is, and can be changed or removed there. It is offered for any system that has at least one function. Setup and Configure are unchanged.

| Field | Value |
| --- | --- |
| Function | The functions the system has |
| Schedule | One Home Assistant schedule helper |

Refused in the form, each with its own message:

- Allow control is off.
- The function already has a schedule in this system.
- The schedule helper is already used by another schedule of this system.

- The entry is titled by its function.
- A block of the schedule helper may carry additional data `power`, in whole watts, with the sign of Decision 8. The README shows it.
- Adding, changing or removing a schedule reloads the system, as for a polling group.

### Following A Schedule

A function is wanted while its schedule's state is `on`. Any other state, including unavailable, unknown and a schedule that no longer exists, is not wanted.

The controller compares what is wanted with what the inverter reports, and acts:

- after the first successful polling cycle of a load,
- whenever a schedule changes state or its `power` changes,
- then once per heartbeat interval for as long as an action is still outstanding.

| Situation | Action |
| --- | --- |
| A schedule turns on, or is on at load, and no function is running | Set the target from the block's `power` when it has one, then start the function |
| The block has no `power` and no target has been set | Not started. Outstanding, with its own warning |
| The schedule's function is already running | Change the power when the block has one, and take ownership |
| A different function is running | Nothing is written. Outstanding |
| The start is refused or fails | Outstanding. Each attempt is a new change, sent once. A start that failed part way and could not be undone leaves a stop outstanding first: Decision 18 |
| The start has succeeded | Nothing more while the schedule stays on, except a new `power`. A target changed by hand stays. A function switched off by hand or by the inverter stays off |
| The schedule moves to a block with a different `power` while on | The model's change of power |
| The block's `power` is not a whole number inside the target's range | Not started and not written. Outstanding, with its own warning |
| A schedule turns off and the function is owned | The model's stop |
| The stop is refused or fails | Outstanding until it is confirmed or a polling cycle reads the function as not running |
| Allow control is off, or the model is an override | Nothing, ever |
| The inverter is unreachable | The existing write rule refuses with nothing sent. Outstanding |

A schedule does exactly what the switch and the target do. With nothing wanted and nothing outstanding the controller sends nothing.

### Diagnostics And Logging

Diagnostics gain: the functions the system has and the method of each, which is running and which is owned, each schedule with its function and schedule helper, whether it is on, and the action outstanding. No power value is included.

| Level | When |
| --- | --- |
| Info | A function started; a function stopped; an outstanding action succeeded |
| Warning | The first failed attempt of a start or a stop, with the reason; a start held back by another function; a `power` that cannot be used; a switch-off on unload that failed |
| Debug | Each later failed attempt |

## Implementation Design

### SAJ Library

No Home Assistant import. No timer. The library never sees a schedule: it is told which function is wanted and at what power.

| Module | Change |
| --- | --- |
| `saj/power_control.py` | New. The functions and their keys. The two methods, each as data: the rows it uses, how a power in watts becomes raw values for a rated power, the ordered writes of a start, a change of power and a stop, how running and the power held are read from values. The functions a device has, from its model's statement, its rows and its fitted equipment. What to do next, from what is wanted, what the device reports, what is owned and what has already succeeded |
| `saj/models/__init__.py` | A profile carries its power control statement. A model that says nothing has none. The enable-bit statement carries the enable row, its alternates, the target row, the timeout row and the limit rows |
| `saj/models/hs3.py`, `saj/models/h2.py` | Each model's statement, as in How Each Model Does It |
| `saj/ems.py` | Ownership, the heartbeat keys and the switch-off are of a power control function. The exclusive forms, the timeout check and the heartbeat take their rows from the device's statements. No row key of a model is named here, in `saj/control.py`, in `saj/definitions.py` constants used for control, or in the integration |
| `saj/control.py` | The allowance-exempt switch-off takes the stop of a power control function, checked by key and by value as under Ownership. Nothing else may use it. The keep-alive read and the limits read take their rows from the device's statements. A fresh read of the functions' state rows for a start |
| `saj/errors.py` | The refusals: no target set, another function running, a power that cannot be used |

### Integration

| Module | Change |
| --- | --- |
| `const.py` | The schedule subentry type and its two field names. Reading an entry's schedules |
| `config_flow.py` | The schedule subentry flow, add and reconfigure, beside the polling-group one. Which functions are offered is asked of the library for the system's device; the flow never tests the model. The setup and Configure forms are not touched |
| `coordinator.py` | Holds the system's functions, targets and schedules. Sends a start, a change of power and a stop through the existing write path under the cycle lock. Listens to the schedule helpers. Asks the library what to do after the first cycle, on each schedule change and each heartbeat interval while something is outstanding. Stores the remembered mode and the targets with the system |
| `switch.py`, `number.py` | The power control switch and target, beside the catalogue ones, created from the functions the library reports |
| `entity.py` | The shared base for an entity that is not a catalogue row, with the same ID rule |
| `errors.py` | Each new refusal to its translated message. A function is named in a message by its translated name, never by its key |
| `__init__.py` | Passes the entry's schedules to the coordinator. The switch-off on unload and on stop is of every owned function |
| `diagnostics.py` | The additions under Diagnostics And Logging |
| `translations/` | The six entity names, the subentry form, its refusals and the new messages |
| `README.md` | Power control per function; what each model has and how it is done; what stays running when Home Assistant stops abruptly, per model; making a schedule helper and its `power` data; every rule under Following A Schedule; the write evidence |

### Modbus Mock

Not changed, and not consulted.

## Roadmap Changes

Done with the rest of the work:

- "New item, EMS controller" and the heading "Deferred by the opt-in register writes plan" are removed.
- Power control becomes item 8, with what this plan delivers.
- Item 1's "Where it stands today" loses the sentence that points at the removed section.

## Verification And Acceptance

Unit tests, each on one module with collaborators replaced, using models, rows and devices built for the test:

- Power control, enable-bit method: watts to raw and back at two rated powers; the writes of a start, a change of power and a stop, in order; running and the power held from values.
- Power control, operating-mode method: the same; a negative power is charge and a positive one discharge; a change of sign; a power of 0 is running at 0 W and a later power is a change of power; running in the mode with each direction and not running out of it; the mode remembered and not overwritten when already passive; a stop with the mode not known.
- Power control, statements: an enable-bit model built for the test with row names of its own gets the exclusive forms, the timeout check, the heartbeat and the limits read with no code change.
- Power control, functions of a device: by the model's statement, by a missing row, by battery and Meter A; none for a model that states nothing.
- Power control, what to do next: each row of the Following A Schedule table; nothing after a successful start; two functions wanted at once.
- Control: the exempt switch-off accepts a function's stop with the allowance full and nothing else: each key that is not a stop row refused, and each stop row refused with a value a stop does not have, for both methods. The fresh state read.
- Coordinator: a start, a change and a stop sent in order under the lock; a start refused when the fresh read shows another function running, with nothing written; a start that fails part way stopped again; one whose undo also fails left owned with its stop outstanding and sent again each heartbeat interval with no schedule; an operating-mode function released and its remembered mode cleared when a cycle reads the inverter out of the mode; a target kept while not running and sent at the start; ownership and the switch-off on unload for each method; the remembered mode stored and cleared; the action after the first cycle, on a schedule change, and repeated each heartbeat interval while outstanding and not after; a schedule state that is not `on` treated as off; nothing sent with control off.
- Entities: the switch and target created per function reported; their IDs; each refusal surfacing its message, with the function by its translated name.
- Config flow: the subentry offered for a device with a function and not for one without, with no model name in the test; the function options; each refusal; reconfigure; the setup and Configure forms unchanged.
- Diagnostics: the additions present and no power value.

Acceptance:

1. An HS3 with a battery and Meter A has the switch and target of Battery, Grid and Inverter. An H2 with a battery has those of Battery. The keys are the same on both.
2. On a 12000 W HS3, `battery_power_target` at −600 and `battery_power_control` on writes −500 to `0x8405` and then sets bit 1 of `0x8400`. Off clears bit 1.
3. On an 8000 W H2 in self-use, the same two changes write 75 to `0x3639`, 3 to `0x3647` and 2 to `0x3636`. Off writes 0 to `0x3636` and 0 to `0x3647`.
4. With a schedule for Battery, a block with `power` −600 turning on does what 2 or 3 does, and the schedule turning off does the off.
5. No code added by this plan tests which model a system is. A model gains power control and schedules by a statement in its model file.
6. The integration has no form that asks for a time or a weekday, and the setup and Configure forms have no power control field.
7. A stop that fails is sent again each heartbeat interval until the inverter reports the function not running.
8. A function switched off by hand while its schedule is on is not started again until the schedule next turns on.
9. With Allow control off, or on a model override, nothing is written.
10. A function switched on through power control is off after the system is unloaded, on both models.
11. Every existing entity keeps its entity ID, unique ID, unit and behaviour.
12. On an H2, a schedule block of 0 W followed by a block of −600 W charges at 600 W in the second block.
13. On an H2, a start that fails after the application mode was written, and whose undo fails, ends with the inverter back in the mode it was in before, with or without a schedule.
14. With the allowance full, the exempt switch-off refuses a write of the direction to charge or discharge and a write of the mode to the method's own mode.
15. A start is refused when another function was started outside Home Assistant and its entities are disabled.
16. No module outside a model file names a row key of a model for power control, the heartbeat, the exclusive forms or the timeout check.
17. On an HS3, the inverter function switched on through `ems_inverter_control` shows `inverter_power_control` as on, stays owned and kept alive across polling cycles, is switched off on unload, and makes a start of another function refuse.
18. `make ci` passes with the coverage gate.

## Work Sequence

1. `saj/power_control.py`: functions, the two methods, the functions of a device. The models' statements.
2. Ownership and the exempt switch-off made of a power control function. Behaviour unchanged.
3. The coordinator's start, change and stop, the stored target and mode, and the switch and target entities.
4. What to do next, the schedule subentry flow, and the coordinator following schedules.
5. Diagnostics, translations, README and the roadmap.

Each step ends with `make ci` passing.

## Revisions

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-11 | First draft. |
