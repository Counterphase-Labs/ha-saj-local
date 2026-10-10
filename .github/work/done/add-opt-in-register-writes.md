# Add Opt-In Register Writes

## Plan Metadata

- **Revision:** 7
- **Status:** Approved
- **Last revised:** 2026-10-10
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Roadmap item:** 1 in `../roadmap.md`
- **Builds on:** `add-register-catalogue-with-full-sensor-coverage.md` and the plans it builds on. Everything in those plans that is not restated or explicitly replaced here continues to apply.

## Outcome And Scope

An installation can change its inverter's settings from Home Assistant once its owner has switched control on. Until then nothing is ever written, as today.

With control on, every `number`, `select`, `switch` and `time` entity that the catalogue already creates sends its change to the device, confirms it by reading the register back and shows the value the device now holds. Commands that have nothing to read (clear faults, restart, set the clock) become `button` entities. On the HS3 the EMS targets and limits become settable; they are never polled and are read only by the heartbeat.

| | Today | With this plan |
| --- | --- | --- |
| Existing controls that can change the device | 0 | HS3 149 of 169; H2 90 of 95. The rest are protected commissioning rows |
| HS3 entities | 594 | 607: 8 EMS targets and limits, 5 buttons |
| H2 entities, single-phase with two strings | 262 | 266: 4 buttons |
| Entity platforms | 6 | 7: `button` added |
| Modbus functions sent | `0x03` | `0x03`, `0x06`, `0x10` |

Requirements delivered:

| Requirement | Delivered by |
| --- | --- |
| Target both reading and writing of registries. Write requires opt in | One **Allow control** option per installation, off by default, confirmed when switched on. The library itself refuses to write without it |
| Platform stability and correctness is paramount | A write is validated before anything is sent, sent once, never retried or replayed, and confirmed by read-back. The entity always shows what the device holds |
| Intelligent Modbus access that does not put the system in danger of overload | Every write request is counted against the endpoint's request budget, and writes have their own allowance inside it. A write over the allowance is refused, not queued |
| Convention over configuration; avoid pages of configuration | One switch, and on a model with EMS one heartbeat interval with a default. No per-entity or per-category write settings |
| Clear and detailed errors | Each way a write can be refused or fail has its own translated message, stating whether the device was changed, was not changed, or is in an unknown state |
| Full localisation | Every new entity name, option, step and error is a translation key |
| SAJ implemented as a stand-alone library with no Home Assistant code | Encoding, the write rules, the write sequence and the allowance live in the library. The integration maps an entity action to one library call |
| Sensor names must remain stable | No existing key or entity ID changes. New keys are fixed here |

Included:

- The opt-in in Configure and its confirmation.
- Encoding of values to register words, and the `0x06` and `0x10` requests in the client.
- The write rules, the write sequence, the write allowance and failure handling.
- Writes for the existing `number`, `select`, `switch` and `time` rows of both models.
- Write-only rows: a register that is written and never polled.
- Command buttons, and the `button` platform.
- HS3 EMS targets and limits, the managed heartbeat and its interval in Configure, and what happens to EMS when Home Assistant stops.
- Diagnostics, logging, documentation and the roadmap update.

## Decisions

Decisions 1 to 3 were made by the user on 2026-10-10. Decisions 4 to 8 are set by this plan and listed so they can be challenged.

| # | Decision | Outcome |
| --- | --- | --- |
| 1 | Whether commissioning settings may be changed | Read-only for now: the risk is high. They keep their control type and entity ID, and a change is refused with its own message. Making them adjustable can be looked at later. See Protected Settings |
| 2 | Which write-only commands are delivered | Clear fault history, clear current fault, restart and synchronise clock. Clear energy history and factory reset are too dangerous and remain available in the official app; this can be revisited. See Commands |
| 3 | How far EMS goes | The targets and limits are settable, and the integration keeps the EMS functions it switched on alive with a managed heartbeat that reads each target at a configurable interval, 60 seconds by default. Those functions are switched off when the installation unloads or Home Assistant stops. See EMS |
| 4 | Which Modbus function a write uses | A one-word row is written with `0x06`. A row of several words is written with one `0x10`, never as several `0x06` requests, so a value is never half written |
| 5 | Whether changing one entity may write another register | No. One change writes one register. The schedule slots do nothing unless the application mode is time-of-use; the integration does not switch the mode for the user |
| 6 | Whether a device on a model override may be written | No. Its addresses are assumed, not verified, so a write could land on a register that means something else |
| 7 | How many writes are allowed | 20 write requests in any 60 seconds per endpoint, inside the budget of 40. Raised from 10 by the user on 2026-10-10. See Device Protection |
| 8 | Application modes the device reports that the catalogue does not name | `application_mode` gains option 11 `time_of_use_bms` on HS3 and option 12 `ai_saving` on H2. See Application Mode |

## Deferred

Everything roadmap item 1 names that this plan does not deliver, with where it goes. The roadmap is updated with these lines when the work is done.

| What | Registers | Why not here | Goes to |
| --- | --- | --- | --- |
| EMS control of the EV charger | HS3 `0x4B46`–`0x4B47` | Defined by the document only. No reading shows that they respond, there is no charger to test against, and the start bit is inverted (0 is on), so a mistake starts or stops a charge | Roadmap 3, equipment detection, which needs a charger reading for the EV block anyway |
| Clear energy history, factory reset | `0x801B`, `0x801C`, both models | Decision 2: not reversible, never exercised on a real unit, a Home Assistant button has no confirmation, and the official app can do both | Listed in the roadmap as excluded, with this reason, open to being revisited |
| Changing commissioning settings | The rows under Protected Settings | Decision 1: high risk | Listed in the roadmap as read-only for now, with this reason, to be looked at later |
| An EMS controller: targets held in watts, schedules | HS3 `0x8400`–`0x8412` | It is a feature built on these writes, not the write path | A new roadmap item |
| Whether the EMS timeout fires at 20 and 60 seconds with all polling stopped | HS3 `0x8401` | Needs a test on the real unit with Home Assistant stopped | Open question in the roadmap |
| Where the SAJ app stores the minimum, maximum and forced SOC of its TOU (BMS) settings | Not found in HS3 `0x3600`–`0x36EF` | Unknown register, so no row is possible | Open question in the roadmap |
| A weekday picker for schedule slots | Day masks stay numbers from 0 to 127, now settable | A picker is a card | Roadmap 2, unchanged |

## Rules Replaced From Earlier Plans

| Earlier rule | Now |
| --- | --- |
| Every control raises the not-enabled error on any change. | A change passes the write rules and is sent. The not-enabled error is one of those rules. |
| A row that is not a sensor is writable. | A row states its access: read-only, read and write, or write-only. Protected rows are read-only whatever their entity type. |
| Every row lies inside a readable span, so a Never Read register cannot be catalogued by mistake. | Every row that is read lies inside a span. A write-only row must lie outside every span, which keeps the same protection: a register cannot be both. |
| The EMS targets and limits have no row. | They are write-only rows. They are never polled. They are read only by the heartbeat, while a function is owned. |
| Two rows share a register only as packed fields. | Command rows may also share a register: each writes a different fixed value. |
| A polling group may hold any catalogue entity of the installation. | Any entity that is read. Write-only rows and buttons are not offered. |
| The catalogue has six entity types. | Seven: `button`. |
| The budget makes a request wait until it fits; nothing is dropped. | Unchanged for every request, reads and writes alike. In addition, a write beyond the write allowance is refused before anything is sent. |

## Evidence

The mock is not a source for anything in this plan. The sources and their order of authority are those of the catalogue plan: real readings, field implementation, SAJ protocol documents.

What the real HS3 readings establish about writing:

| Finding | Detail |
| --- | --- |
| `0x06` works | Every write made on the unit was a single-register `0x06` request. Each was acknowledged and read back unchanged |
| Registers with a confirmed write | `0x3647` application mode, `0x3651` backup reserve, `0x3639` passive battery charge power, `0x8400` EMS enable with values 1, 2, 8, 32 and 0, `0x8401` EMS timeout, and the EMS targets and limits `0x8402`–`0x8405` and `0x840F`–`0x8412` |
| A write is followed by the device | `0x402C` followed a write of `0x3651`. The SAJ app shows a Modbus write after a delay |
| A value outside the offered steps is accepted | `0x3639` accepted 42 (4.2 %) although the app offers whole percent |
| The document's range can be wrong | `0x8405` accepted 1001 and 1667 against a documented maximum of 1000 |
| Application mode 6 written on its own | The inverter goes idle and the house runs from the grid. There is no automatic exit |
| Application mode 11 | Set by the SAJ app for its TOU (BMS) mode. Not in the document |
| EMS enable bits | Each bit works on its own. Bit 0 rewrites `0x3647` to 6 and restores it when cleared; bits 1, 3 and 5 leave it alone. Clearing `0x8400` ends EMS within seconds and returns to the mode in force before. Clearing it does not clear the target |
| EMS timeout | Fired at 5 seconds. Did not fire at 20 or 60 seconds, for up to 408 seconds, while another client was polling the unit once a minute. Not tested with all polling stopped |
| Reading an EMS target or limit | Counts as EMS activity |
| The schedule registers | The SAJ app wrote slot 1 to `0x3604` and `0x3606`–`0x3608`: day-mask bit 0 is Monday and power is a whole percent of rated power |

Not established on a real unit: any `0x10` request, any write to a schedule register over Modbus, any EV charger write, any command register, and any write on an H2.

What field implementation establishes:

- H2 units are written in sustained use with single `0x06` requests: the schedule slots, application mode, passive mode and its four powers, the three battery limits, the four power limits and the export limit.
- Packed registers are changed by reading the register, replacing the bits and writing it back. A direct write of a packed register is the known way to destroy the other field.
- Controls are switched off when the reported device type is not a recognised one.
- A command is sent once and never repeated when no acknowledgement arrives.
- An H2 in the app's AI Saving mode reports application mode 12, and users need to be able to set it back.

What the documents establish: both define `0x06` and `0x10`, exception responses as the function code plus `0x80`, and SAJ exception codes beyond the standard ones (`0x10` incorrect password, `0x11` verification error, `0x12` invalid parameter, `0x13` system locked). The HS3 document states that enabling EMS makes the operating mode invalid and disables reverse-current protection.

Each row's write evidence follows from this:

| Write evidence | Rows |
| --- | --- |
| Verified on HS3 | `application_mode`, `backup_reserve_soc`, `passive_battery_charge_power`, the four `ems_*_control` switches, `ems_timeout`, the eight EMS targets and limits |
| Implemented on H2 | The H2 rows listed above |
| Documented | Every other writable row, every `0x10` write and every command |

Write evidence does not decide whether a row may be written; the write rules do. It is stated in the README so a user knows which controls have been exercised on real hardware.

## Behaviour

### Opting In

- Setup and Configure both have the field **Allow control**, off by default, so an installation is read-only unless its owner chooses otherwise. The only other field this plan adds is the EMS heartbeat interval; see EMS.
- Switching it on adds a confirmation. In Configure it comes after the model, replacement, prefix and load confirmations; in setup it comes after the model confirmation, and nothing is created before it is confirmed. It says that entity changes and automations will change inverter settings, and that enabling EMS functions disables the inverter's reverse-current protection. Switching it off needs no confirmation.
- The option is saved with the others and the installation reloads, as for any Configure change.
- With control off, every control and button refuses with the existing not-enabled message, which now names where to switch it on. Entities are created and shown exactly as today.

### Write Rules

A change is checked in this order. The first rule that fails ends it with that rule's message, and nothing is sent.

| # | Rule | Message says |
| --- | --- | --- |
| 1 | Control is on for the installation | Control is not enabled; switch it on in Configure |
| 2 | The device was recognised, not assumed from a model override | The model could not be verified, so its settings cannot be changed |
| 3 | The row is not protected | This is a commissioning setting and cannot be changed from Home Assistant |
| 4 | The value is valid for the row: inside its range, one of its options, a valid time | What was wrong with the value |
| 5 | The endpoint is not backing off and its connection is open | The inverter is not reachable right now; nothing was changed |
| 6 | The write allowance has room | Too many changes in the last minute; nothing was changed |

Rule 5 exists because a connection is only trusted after the poller has verified the device's serial on it. A write never opens a connection of its own.

### Values

| Row | What is sent |
| --- | --- |
| `number` | The value divided by the row's scale, rounded to the nearest whole raw step. Signed rows as two's complement. Two-word rows most significant word first |
| `select` | The code of the chosen option |
| `switch` | 1 or 0, or the row's bit |
| `time` | Hours in the high byte, minutes in the low byte. Seconds are dropped |
| A packed field | The register's current word with only the field's bits replaced. Every other bit is sent back as read, named or not |
| `button` | The row's fixed value, or the clock words |

A `number`'s range is the catalogue's. Three rows gain a range in this plan because the full range of their encoding is wider than the device's:

| Key | Range | Source |
| --- | --- | --- |
| `ev_charge_power`, `ev_slot_<n>_power` | 0–11000 W | HS3 document |
| `passive_mode` | 0–2, unchanged | Listed for completeness |

### Write Sequence

One write at a time per installation. A write waits for a polling cycle in flight to finish and a cycle waits for a write, so a read-change-write of a packed register can never be interleaved with anything.

| Row | Requests |
| --- | --- |
| One-word row | Write with `0x06`, then read the row back: 2 |
| Row of several words | Write with `0x10`, then read the row back: 2 |
| Packed field | Read the register, write it with `0x06`, read it back: 3. When the register already holds the wanted bits nothing is written: 1 |
| Write-only row | Write: 1. There is nothing to read |

Outcomes:

| What happens | Device state | Entity | Result of the action |
| --- | --- | --- | --- |
| Acknowledged, and the read-back equals what was sent | Changed | Shows the new value at once, with every other entity that shares the register | Succeeds |
| Acknowledged, and the read-back differs | Whatever the device chose | Shows the read-back | Fails: the inverter accepted the request but holds a different value |
| The device answers with an exception | Not changed | Unchanged | Fails: rejected, with the exception code. The connection stays open and the endpoint does not back off, because the device is answering |
| No answer, or a broken answer, to the write | Unknown | Unchanged until the next read | Fails: the change may or may not have been applied. The connection is closed, the endpoint counts a failure and backs off, and the next cycle is a full read |
| The write is acknowledged and the read-back fails | Changed | Unchanged until the next read | Fails with the same unknown-state message and the same link handling |
| A write-only row is acknowledged | Changed | Shows the value sent, marked as assumed | Succeeds |

A write is never retried and never replayed after a reconnect. Entities that mirror a setting elsewhere, such as `backup_reserve_soc_active`, follow at their next read.

### Device Protection

- Every request of a write goes through the client like a read: it is counted against the endpoint's budget of 40 requests in 60 seconds and paced after the previous request.
- Writes have an allowance of **20 write requests in any 60 seconds** per endpoint. It belongs to the endpoint and survives reloads, like the budget. A write over it is refused; it is not queued, because a setting applied a minute late is worse than one refused. The EMS switch-off on unload and stop is the one write it does not refuse.
- No document gives a write rate. The figure is a named library constant. Total traffic stays capped by the budget of 40, so an installation that writes at the limit, with read-backs, slows its own reading for that minute.
- A change to the value the device already holds still costs requests. Only a packed field can tell without writing.

The request load shown in the forms is unchanged: it is the planned load of reading. Writes are not planned load.

### Protected Settings

These rows are read-only for now. They keep their entity type, entity ID and reading, so making one adjustable later changes no entity ID. A change is refused by rule 3.

| Group | Keys |
| --- | --- |
| Metering | `meter_configuration`, `meter_address` |
| RS485 | `rs485_address`, `rs485_baud_rate`, `rs485_slave_address`, `rs485_slave_baud_rate` |
| Battery | `battery_protocol` |
| Network | `ethernet_mode`, `ethernet_ip_address`, `ethernet_subnet_mask`, `ethernet_gateway`, `ethernet_dns_primary`, `ethernet_dns_secondary` |
| EV charger link | `ev_address`, `ev_baud_rate`, `ev_charger_count`, `ev_communication_timeout`, `ev_port_mode`, `ev_port_address` |
| Header | `settings_sequence` |

The reason is the same for all but the last: a wrong value cuts the inverter off from its meter, its battery, its charger or from Home Assistant itself, and it cannot then be put right from Home Assistant. `settings_sequence` is the settings block's own sequence number, not a setting.

With every `text` row protected, no text is ever written and the text encodings stay decode-only.

### Application Mode

`application_mode` is the one control whose options the real units go beyond.

| Model | Option added | Evidence |
| --- | --- | --- |
| HS3 | 11 `time_of_use_bms` | Read on the real HS3 after the SAJ app selected TOU (BMS) |
| H2 | 12 `ai_saving` | Field report: reported by an H2 in the app's AI Saving mode |

Without them the select shows unknown while the device is in that mode, and a user who changes the mode cannot put it back. Neither has been written over Modbus. A device that rejects the code answers with an exception and the user is told.

`ems` (6) stays an option on HS3. On its own it leaves the inverter idle; the README says so.

### Commands

Write-only rows on both models, each a `button`, created disabled, in the configuration category. Evidence is Documented for all of them.

| Key | Register | Sends |
| --- | --- | --- |
| `clear_fault_history` | `0x8015` | 1 |
| `clear_current_fault` | `0x8015` | 2 |
| `restart_inverter` | `0x801A` | 1 |
| `synchronise_clock` | `0x8020`, 4 words | Home Assistant's local time now: year; month and day; hour and minute; second and a zero byte. One `0x10` request |

A press passes the write rules like any change. It is sent once. When no acknowledgement arrives the message says the command may or may not have run, and it is not sent again.

After `restart_inverter` the device stops answering for a while. That is handled by the existing failed-cycle and back-off rules; nothing special is done.

### EMS

HS3 only.

The existing rows `ems_inverter_control`, `ems_inverter_control_with_timeout_exit`, `ems_battery_control`, `ems_grid_control` (bits of `0x8400`) and `ems_timeout` (`0x8401`) become writable like any other row: they are read, and written by the packed-field and one-word sequences.

New write-only rows, each a `number`, created disabled:

| Key | Register | Encoding | Scale | Unit | Range |
| --- | --- | --- | --- | --- | --- |
| `ems_inverter_power_target` | `0x8402` | I16 | 0.01 | % of rated power | −100 to 100 |
| `ems_battery_charge_current_limit` | `0x8403` | U16 | 0.1 | A | 0 to 200 |
| `ems_battery_discharge_current_limit` | `0x8404` | U16 | 0.1 | A | 0 to 20 |
| `ems_battery_power_target` | `0x8405` | I16 | 0.01 | % of rated power | −100 to 100 |
| `ems_inverter_import_power_limit` | `0x840F` | U16 | 0.01 | % of rated power | 0 to 100 |
| `ems_inverter_export_power_limit` | `0x8410` | U16 | 0.01 | % of rated power | 0 to 100 |
| `ems_grid_power_target` | `0x8411` | I16 | 0.01 | % of rated power | −100 to 100 |
| `ems_pv_power_limit` | `0x8412` | U16 | 0.01 | % of rated power | 0 to 100 |

And one more button, `ems_pv_power_limit_remove`, which writes `0xFFFF` to `0x8412`: the device's value for no limit, which is outside the number's range.

- The sign is the device's: a positive target sells or discharges, a negative one buys or charges. The entity names say so.
- The battery target's upper range is 100 %, not the document's 10 %: the real unit accepted and followed values above it.
- The two current-limit ranges are the document's. It gives 200 A for charge and 20 A for discharge; the real unit held 20.0 A in both. A device that disagrees rejects the value.
- A write-only `number` shows the last value this installation sent and the device acknowledged, marked as assumed. Before the first write it is unknown. While an EMS function is owned it also takes the value the heartbeat reads, so it follows the device, including the device clearing a target when its timeout fires. With nothing owned it is not read and does not follow a change made elsewhere. A PV limit read as `0xFFFF`, no limit, is shown as unknown.

An EMS function is **owned** by the installation from the moment it switches the function's enable bit on until the bit is switched off, a polling cycle reads the bit as off, or the installation unloads. A lost connection does not end it. Each function has one target:

| Function | Enable bit of `0x8400` | Target |
| --- | --- | --- |
| Inverter control | Bit 0 or bit 3 | `ems_inverter_power_target` |
| Battery control | Bit 1 | `ems_battery_power_target` |
| Grid control | Bit 5 | `ems_grid_power_target` |

What the integration does about EMS, and nothing more:

| Rule | Behaviour |
| --- | --- |
| Exclusive inverter bits | Switching on `ems_inverter_control` or `ems_inverter_control_with_timeout_exit` clears the other in the same write. They are two forms of one function |
| Nothing at load | No EMS register is written when an installation loads, reloads or reconnects. An EMS function found already on is left on, shown as on, and not owned: it gets no heartbeat and is not switched off |
| Timeout longer than the heartbeat | Switching a function on reads `0x8401` together with `0x8400`, in one request. It is refused when the device's timeout is not longer than the heartbeat interval, because EMS would drop out between beats. No timeout (`0xFFFF`) passes. `ems_timeout` cannot be set to a value at or below the interval |
| Heartbeat | Once per interval, the target of every owned function is read: one request for its one register. The document and the real unit both show that reading a target keeps its function online. An owned function gets its beat whether or not its target was ever set. The value read is shown by the target's entity |
| A beat is a read | It needs control on, a verified model and an open connection, like a write, and it never opens a connection. It counts against the budget, not the write allowance, is sent once and is never retried. Only the three targets can be read this way. A beat that is refused or answered with an exception is dropped and the next one is sent on time. A beat with no answer is a lost connection. The first dropped beat of a function is logged as a warning and its recovery as info |
| Limits follow the beat | After the owned targets, each beat reads the five limits in three requests, grouped by adjacency and never covering another register, and their entities show the values. A target of a function that is not owned is never read. A limits read is not a beat: an exception is logged at debug and is not a dropped beat; no answer is a lost connection |
| Lost connection | Ownership survives a lost connection. Beats are dropped while the inverter is unreachable and resume when it is back, and the owned functions are still switched off on the way out. Ownership ends when a polling cycle reads an owned enable bit as off: the inverter or someone else switched it off |
| Switched off on the way out | The enable bits of the owned functions are cleared when the installation unloads and when Home Assistant stops: one read-change-write of `0x8400`, clearing only those bits. It is not held back by the write allowance, which only the EMS enable bits can bypass, it waits for a polling cycle or write in flight to finish, and its own requests are bounded to 5 seconds. Every other write rule applies: it never opens a connection of its own. A failure is logged as a warning naming the timeout as the fallback. Targets are left as they are; with the bit clear they have no effect |

The heartbeat interval is one field, **EMS heartbeat**, in seconds, shown only for a model that has EMS rows. In Configure it is on the form. In setup the model is not known until the form is submitted, so it is on the control confirmation. The default is **60** and the range is **30 to 3600**. At the minimum, three owned functions cost 12 read requests a minute, 6 for the targets and 6 for the limits, inside the budget of 40. The device's timeout register holds up to 65534 seconds, so an interval of an hour still fits under a timeout. Changing the interval reloads the installation like any Configure change, which switches off the functions it owned.

Two things the heartbeat does not settle:

- Whether it matters. The real unit left EMS at a timeout of 5 seconds but kept buying or selling at its last target for minutes at 20 and 60 seconds while another client was polling. Whether the timeout can be relied on is an open question, so the integration clears the enable bits on the way out and does not rely on the timeout.
- A stalled automation. While Home Assistant runs, an owned function is kept alive at its last target even if whatever was setting that target has stopped. Switching the function off ends it.

Not enforced: that grid-point control needs a meter. The requirements are silent and the row that reports the meter is not read by default. The README states it.

### Diagnostics And Logging

Diagnostics gain: whether control is on, the write allowance and how much of it is used, counts of writes acknowledged, rejected and unconfirmed since load, the last write's key, outcome and exception code, the heartbeat interval, the EMS functions owned, and counts of beats sent and dropped. No written value is included.

Logging:

| Level | When |
| --- | --- |
| Debug | Each write: key, address, function and words sent, and the read-back. A beat dropped |
| Info | A command acknowledged; EMS bits cleared on unload; a heartbeat recovered; ownership ended because the bit was read as off |
| Warning | A write unconfirmed; a read-back that differs; the first dropped beat of a function; EMS cleanup failed |

A refusal by the write rules is not logged: the user already has the message.

## Implementation Design

### SAJ Library

No Home Assistant import. Everything model-specific stays data.

| Module | Change |
| --- | --- |
| `saj/codec.py` | Encoding, the inverse of decoding: a value and a format to words, for the numeric encodings, time of day and the clock. Replacing a field's bits in a word. A value that cannot be encoded raises a library write error, not `ValueError`, which the read path treats as bad device data |
| `saj/client.py` | `write_single_register` and `write_multiple_registers`. Reads and writes share one request path, so the budget, the pause, late-frame handling, the timeout and the close-on-failure rules are written once. The acknowledgement must echo the address and the value or count |
| `saj/definitions.py` | `Access` on a definition, replacing the rule that a non-sensor is writable. `EntityKind.BUTTON`. A command's fixed value. The protected keys. The new definitions: four commands, eight EMS rows, the PV-limit button. The added ranges |
| `saj/models/hs3.py`, `saj/models/h2.py` | Addresses and evidence for the new rows. The added application-mode options |
| `saj/catalogue.py` | A row that is read must lie inside a span; a write-only row must lie outside every span. Command rows may share a register. The rows of a device split into those that are read and those that are not |
| `saj/telemetry.py` | Planning and the supported keys of a cadence ignore write-only rows |
| `saj/budget.py`, `saj/guard.py` | The write allowance, owned by the endpoint guard beside the budget |
| `saj/control.py` | New. The write rules, the request plan for a row, the sequence with its read-back, and the result: the values now known and what happened. It is given the client, the device, the guard, whether control is on and a clock, and takes a key and a value |
| `saj/ems.py` | New. The EMS functions with their bits and targets, ownership, the exclusive inverter bits, the timeout check, the interval's limits, and which targets a beat reads. It holds no timer |
| `saj/errors.py` | The write errors: one per rule, plus rejected, unconfirmed, mismatched and the EMS timeout refusal |
| `saj/poller.py` | One method for a link failure that did not come from a cycle: it closes, tells the guard, requires a full read and returns the next wake-up. A failed write uses it |

The opt-in is passed into `saj/control.py` and enforced there, so no integration code path can cause a write with control off.

### Integration

| Module | Change |
| --- | --- |
| `const.py` | The control option and the heartbeat interval option. `PLATFORMS` gains `button` |
| `config_flow.py` | The Allow control field and its confirmation step, in setup and in Configure. The EMS heartbeat field: in Configure shown from the stored device type, in setup on the confirmation from the device just identified. The polling-group options leave out rows that are not read |
| `coordinator.py` | One write method: takes the cycle lock, calls the library, merges the returned values and notifies the entities of the keys that changed without disturbing the polling schedule. Remembers what was sent to write-only rows. On a link failure it schedules the wake-up the poller returns and keeps EMS ownership; a cycle that reads an owned enable bit as off ends it. Runs the heartbeat timer, which asks the library which targets to read |
| `entity.py` | The shared path from an entity action to the coordinator's write |
| `number.py`, `select.py`, `switch.py`, `time.py` | Each action calls the shared path with its value. `text.py` is unchanged: every text row is protected |
| `button.py` | New. Thin, like the others |
| `errors.py` | Each library write error to its translated message. Rule refusals are validation errors; device failures are operation errors |
| `__init__.py` | Builds the control with the entry's option. EMS cleanup on unload and on Home Assistant stopping |
| `diagnostics.py` | The additions under Diagnostics And Logging |
| `translations/` | The option, the confirmation, the errors, and the names of the new entities and options |

### Modbus Mock

Not changed, and not consulted. If the smoke test shows the mock departs from documented device behaviour for `0x06` or `0x10`, that is raised as a mock defect against the documents, not adjusted to suit the integration.

### What Is Removed

- `control_not_enabled()` being raised unconditionally in the five control platforms.
- `Definition.writable` derived from the entity kind.

## Verification And Acceptance

Unit tests, each on one module with collaborators replaced, using rows built for the test:

- Codec: each encoding there and back; scale and rounding to a raw step; signed values; a two-word value; a time with seconds; the clock; replacing a field without touching other bits; each value that cannot be encoded.
- Client: the `0x06` and `0x10` frames; an acknowledgement that echoes and one that does not; an exception response keeps the connection; a timeout closes it; the budget and pause apply to writes.
- Catalogue: a write-only row inside a span rejected; a read row outside one rejected; two commands sharing a register accepted; the read and unread rows of a device.
- Planning: an enabled write-only key causes no request, with every entity enabled.
- Allowance and guard: room, full, the window sliding, and surviving a second client.
- Control: each rule refusing with nothing sent, in order; each row type's request sequence; a packed field keeping the other bits; a packed field already at the value; each outcome in the Write Sequence table; a write-only row never read by a write; the keep-alive read accepted for the three targets only; the limits read covering the five limits only; the switch-off accepted for the EMS enable bits only, with the allowance full; no second attempt after a timeout.
- EMS: ownership gained and lost; the exclusive bits; the timeout check at, below and above the interval and with no timeout; a beat for each owned function and none for one not owned; a function found on at load not owned.
- Coordinator: a write waits for a cycle; values published to the right keys; sharing entities updated; the schedule undisturbed; a link failure schedules the back-off and keeps ownership and the heartbeat; beats resume after a reconnect; a cycle that reads an owned bit as off ends ownership; the first dropped beat warns once; the owned bits cleared on unload and on stop, and only those.
- Entities: each platform passing its value; each error surfacing its message; a write-only number unknown, then showing what was sent as assumed.
- Config flow: the confirmation shown only when control is switched on, in setup and in Configure; nothing saved or created before it; the heartbeat field on the setup confirmation for a model with EMS rows; the heartbeat field shown only for a model with EMS rows and held to its range; write-only rows absent from the polling-group options.
- Diagnostics: the additions present and no written value.

Smoke, against the mock, one per model: a change is refused while control is off; with control switched on, the setting is changed and shows the new value.

Acceptance checks 2, 3 and 8 are also tested on the shipped HS3 rows, with a link that records every request.

Acceptance:

1. A new installation has control off unless it was switched on and confirmed during setup, and with control off, with every entity enabled no `0x06` or `0x10` request is ever sent.
2. With control on, setting `backup_reserve_soc` on an HS3 sends one `0x06` and one read, and the entity shows the device's value.
3. Changing `charge_slot_1_power` leaves `charge_slot_1_days` as it was, and the reverse.
4. No protected row can be changed, with control on.
5. An installation on a model override cannot be changed, with control on.
6. The twenty-first write request inside 60 seconds is refused and nothing is sent.
7. A write that times out is sent once, reports an unknown state, and the installation recovers through the existing back-off.
8. No polling request ever reads `0x8402`–`0x8405`, `0x840F`–`0x8412` or `0x8015`–`0x8023`, with every entity enabled and after any write. Only the heartbeat reads the EMS registers: a target only while its function is owned, and the five limits only while any function is owned. The command registers are never read.
9. An EMS function switched on from Home Assistant has its target read once per heartbeat interval, 60 seconds unless configured otherwise, for as long as it is owned.
10. An EMS function cannot be switched on while the device's timeout is at or below the heartbeat interval.
11. An EMS function switched on from Home Assistant is off after the installation is unloaded, including after a lost connection that has recovered, and one that was already on at load is untouched.
12. Every existing entity keeps its entity ID and unique ID.
13. `make ci` passes with the coverage gate.

## Work Sequence

1. Codec encoding and the client's two write functions.
2. Access, write-only rows and the catalogue and planning rules, with no new rows. Behaviour unchanged.
3. `saj/control.py`, the allowance and the write errors.
4. The opt-in in Configure, the coordinator's write method, the four control platforms, error translation and diagnostics.
5. Commands and the `button` platform.
6. EMS targets and limits, ownership, the exclusive bits, the timeout check, the heartbeat with its Configure field, and the cleanup.
7. Application-mode options, README, `documentation/development.md`, the roadmap update and the smoke tests.

Each step ends with `make ci` passing.

## Revisions

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-10 | First draft. |
| 2 | 2026-10-10 | The heartbeat repeats a target set before its function was switched on, and keeps it across switching off and a lost connection. Acceptance checks 2, 3 and 8 are tested on the shipped HS3 rows. The smoke test first shows a change refused while control is off. |
| 3 | 2026-10-10 | The EMS switch-off on unload and stop is exempt from the write allowance and waits for a cycle in flight before its 5 seconds start. |
| 4 | 2026-10-10 | Approved by the user. The heartbeat reads each owned function's target instead of writing it again, so revision 2's remembered target is gone. The write allowance is 20. The allowance-exempt switch-off works only for the EMS enable bits. |
| 5 | 2026-10-10 | Ownership survives a lost connection: the heartbeat resumes on reconnect and the functions are still switched off on unload and stop. Ownership ends when a polling cycle reads the enable bit as off. A failing heartbeat is logged as a warning. |
| 6 | 2026-10-10 | Each beat also reads the five EMS limits, so their entities show the value the device holds while a function is owned. |
| 7 | 2026-10-10 | Setup offers Allow control, off by default, with the same confirmation, which also asks for the EMS heartbeat on a model with EMS rows. |
