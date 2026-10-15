# Add Full H2 Support

## Plan Metadata

- **Revision:** 1
- **Status:** Approved
- **Last revised:** 2026-10-14
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Roadmap item:** "Full H2 support" in `../roadmap.md`
- **Builds on:** `add-register-catalogue-with-full-sensor-coverage.md`, `add-model-neutral-power-control-with-schedules.md`, `add-device-faults-and-repairs.md`, `add-debug-dump-and-logging.md` and the plans they build on. Everything in those plans that is not restated or explicitly replaced here continues to apply.

## Outcome And Scope

An H2 offers everything the common interface offers that an H2 can do, the same way as the HS3, and every setting and reading the H2 has is catalogued.

| | Today | With this plan |
| --- | --- | --- |
| Registers only the H2 document defines | Not catalogued, listed by the catalogue plan as left for this item | Catalogued, each with its evidence |
| Grid import and export energy totals | The H2 places the totals on the phase-1 counters. The HS3 places them on the all-phase counters and has separate phase-1 counters | Both models place the totals on the all-phase counters and have the phase-1 counters as their own keys |
| Battery voltage and current | Created disabled on the H2 (documented only) | Enabled by default, as on the HS3 |
| Application mode | No peak shaving option | Peak shaving offered on the H2 |
| Battery and BMS identity of each pack | Not catalogued | Type, versions and serials per pack, serials private |
| H2 settings that can be changed | Those of the opt-in writes plan | Also the buzzer, the LED ring and the battery forced charge power. Every other new setting is shown and never written |
| Grid and Inverter power control | Not offered on the H2 | Not offered on the H2, with the evidence that the H2 cannot do it. The roadmap item is corrected |
| Parallel-system readings | Placed on the H2. The H2 simulator does not serve them | Placed on the H2 with their H2 evidence. The H2 simulator serves them and can simulate an H2 in a parallel system |

Included:

- The H2 model file, new definitions and the one new family, spans and protected keys.
- The H2 simulator serving every row this plan places.
- Translations, README, `documentation/development.md` and the roadmap update.

Not changed: detection and the recognised device types, power control, faults, repairs, the browser smoke test.

Recognising other H2-family units, such as the three-phase H2, is not part of this item. The roadmap holds it under "Other models".

## Requirements

| Requirement | How it is met |
| --- | --- |
| Wide SAJ support for common household inverter, battery and related equipment | Every register the H2 document defines and every register field tooling reads on an H2 is catalogued, apart from words with no meaning (Decision 9) |
| An abstraction layer across SAJ systems: consistent names, values, units and behaviour | A register that means the same as an HS3 row takes the HS3 key: `led_mode`, `grid_connection_countdown`, `settings_sequence`, the grid energy totals and the phase-1 counters. New keys are model-neutral, with no model in their name |
| A feature is left out only on a model that lacks the possibility to do it | Grid and Inverter power control are left out on the H2 because no register holds either point at a set power (Evidence). Everything else the common interface offers is placed |
| Target both reading and writing of registries. Write requires opt in | The three new writable settings go through the existing opt-in, write path, rate limit and read-back |
| Dangerous changes are never made from Home Assistant. Commissioning settings are read-only | Grid type, parallel set-up, input wiring, rated power and model, protection limits, PV and MPPT limits, lead-acid battery parameters, BMS update and reverse-flow mode are commissioning settings. They join the protected keys and refuse changes, as the existing commissioning settings do (Decision 5) |
| Actions that cannot be undone are not offered | Clearing energy yield (`0x801B`) and factory reset (`0x801C`) stay out |
| Privacy-focused debug dump | Battery and BMS serials are private rows: hidden in the snapshot and redacted in diagnostics |
| Use intelligent modbus access that does not overload the system | New rows are created disabled except the grid totals, which add one request to the default H2 read (Decision 2). Battery voltage and current fit an existing request |
| Platform stability and correctness is paramount | Every new row carries its evidence. The H2 stays marked as not hand-verified. A refused block is handled by the existing narrowing and refused-register repair |
| Sensor names must remain stable | No HS3 key changes. On the H2, `grid_export_energy_*` and `grid_import_energy_*` keep their keys and move to the all-phase counters. New keys are fixed here |
| 100% unit test coverage from unit tests only; no tests of constants | Tests cover behaviour: placement, protection, inversion, pack limits, privacy and option decoding. No test asserts an address or a scale |

## Decisions

There is no H2 available to this project. Field tooling in sustained use on H2 units, and the field reports around it, are the H2 evidence and are taken as correct where they do not contradict each other. The H2 document is used where no field evidence exists. These decisions are set by this plan and listed so they can be challenged.

| # | Decision | Outcome |
| --- | --- | --- |
| 1 | Grid and Inverter power control on the H2 | Not offered. The passive grid charge power had no effect in field tests. The passive grid discharge power caps what passive mode sends to the grid; it does not hold the grid connection point at a power. Nothing holds the inverter output at a power. The roadmap item's "This includes holding the grid connection point and the inverter at a set power" is replaced by the evidence that the H2 cannot do it |
| 2 | Where the H2's grid energy totals come from | The all-phase counters `0x4167`–`0x4176`, as on the HS3. Field tooling reads them on H2 units and enables them by default as the grid counters for the Home Assistant Energy dashboard. The phase-1 counters `0x40EF`–`0x40FE` become `grid_l1_*`, as on the HS3. This adds one request to the default H2 read with a battery and Meter A (7 to 8). One field report has the all-phase counters unavailable on a single-phase unit: if a unit refuses them, the existing refused-register repair names the entities, and the phase-1 counters, equal to the total on a single-phase unit, can be enabled |
| 3 | Battery voltage and current (`0x4069`, `0x406A`) | Implemented evidence, so enabled by default as core rows. A field report on an H2-6K-LS2 found them correct, with current negative while charging. They fit the existing request that starts at the battery temperature, so no request is added |
| 4 | Application mode 10 | Added to the H2 options as `peak_shaving`. Field reports show it selected in the SAJ app, read back as 10, and written over Modbus for months on an H2-10K-T2. It is absent from the H2 document |
| 5 | Which new settings are protected | Commissioning, kept read-only like the existing ones: reverse-flow mode `0x3635`, FCAS frequency hysteresis `0x3642`, the lead-acid battery parameters `0x3652`–`0x3659`, BMS update ID and mode `0x365D`–`0x365E`, parallel role, number and mode `0x3661`–`0x3663`, float and equalising charge voltage `0x3664`–`0x3665`, battery and PV input mode `0x3666`–`0x3667`, off-grid output voltage and frequency `0x3669`–`0x366A`, motor enable `0x366B`, machine model and rated power `0x366C`–`0x366D`, the two function flag words `0x366E`–`0x366F`, DC, insulation and leakage limits `0x3670`–`0x3673`, grid type `0x3674`, PV start and shutdown voltage and the MPPT limits and scan time `0x3678`–`0x367C`. A wrong value in any of them cuts the inverter off from its equipment, breaks grid compliance or damages hardware |
| 6 | Which new settings are writable | The buzzer `0x3632`, the LED ring `0x3675` and the battery forced charge power `0x3676` |
| 7 | Off-grid mode `0x3668` and inverter stop `0x3677` | Catalogued as readings. Making them controls, the same on every model, is the "Common controls" item, which already owns off-grid mode and inverter on and off |
| 8 | Battery and BMS identity `0x8E00`–`0x8E63` | One family indexed by pack, with five members, stride 20 words. The pack limit applies to it like every other pack row. The H2 pack maximum becomes 5, matching the five identity slots in the document and field reports of up to five stacked packs |
| 9 | Words with no meaning | Not entities: the reserved fault word `0x400D`, the running data pass-through `0x401C`–`0x4021`, and the reserved words `0x4070` and `0x40B0`–`0x40BB`. They remain in the register snapshot |
| 10 | Device type, sub-type and serial as entities | Not added. They are shown on the device and in diagnostics on every model, and no model has them as entities |
| 11 | `0x401B`, settings change counter | Takes the HS3 key `settings_sequence`: on both models it counts changes to the settings |
| 12 | Parallel-system readings `0x4200`–`0x4264` on the H2 | Kept as placed today, created disabled. The H2 document used here ends its realtime area at `0x4165`, but the field tooling's author cites the same block from an H2-family document, and a field report has it answering with live values on an H2. The H2 simulator serves the block and can simulate an H2 in a parallel system, which field reports describe on H2-family units |
| 13 | Parallel-system state of charge `0x4209` | Read in whole percent on both models. The H2-family document gives 0.01 %, but a field report on an H2 read the state of charge correctly in whole percent, and readings on an HS3 show 100 for 100 %. The key does not change |
| 14 | Meter B phases 2 and 3 (`0xA05A`–`0xA065`) | Follow the unit's identified phase count, as every meter row does: a unit identified as single-phase gets the Meter B phase 1 rows only, a unit identified as three-phase gets all three. Unchanged from today |

## Evidence

Order of authority: field tooling in sustained use on H2 units and field reports, then the H2 document. The simulator is not a source.

### Power control

| Finding | Source |
| --- | --- |
| In passive mode only the battery charge power `0x3639` changed the charging power. The passive grid charge power `0x3637` and the grid import limit `0x364F` had no effect | Field tests on HS2 units, repeated by the field tooling's author |
| In passive mode the passive grid discharge power `0x3638` limits the power sent to the grid. At 0, a unit's PV output went to 0 | Field report, two HS2 units in on-grid parallel |
| Passive mode holds the battery at its set power; PV only reduces what is taken from the grid | Field tooling's author |
| A register that holds the grid connection point or the inverter output at a power | None in the document, the field tooling or any field report |

### Readings and settings

| Registers | Content | Evidence |
| --- | --- | --- |
| `0x4167`–`0x4176` | All-phase import ("feed-in") and export ("sell") energy, today, month, year, total, U32, 0.01 kWh | Implemented: read by field tooling, enabled by default there. Absent from the document. One report of them unavailable on an HS2-5K-S2-X |
| `0xA033` | Battery low-voltage warning, 0.1 V | Implemented: read by field tooling |
| `0x4069`, `0x406A` | Battery voltage 0.1 V, current 0.01 A | Implemented: field report on an H2-6K-LS2 |
| `0x3647` value 10 | Peak shaving | Implemented: field reports |
| `0x3632` | Buzzer, 0 enabled, 1 disabled | Documented |
| `0x3675` | LED ring, the same four options as the HS3 row | Documented |
| `0x3676` | Battery forced and equalising charge power, limits grid charging of the battery, 10 to 100 % of rated power in 0.1 % | Documented |
| `0x3668` | Off-grid mode, 0 off, 1 on | Documented |
| `0x3677` | Inverter stop, 1 shuts down | Documented |
| Decision 5 rows | As listed there | Documented |
| `0x400F` | Number of inverter errors and warnings | Documented |
| `0x4017`, `0x4018` | DRM hardware and software status, one bit per DRM | Documented |
| `0x4019` | Grid connection countdown, seconds | Documented, the same as the HS3 row |
| `0x401A` | Fault record sequence, up to 60000 then 1 | Documented |
| `0x401B` | Settings change counter | Documented |
| `0x4022` | Application mode in effect, 0 to 3 | Documented |
| `0x406B`, `0x406C` | Battery controller 1 and 2 current, 0.01 A | Documented |
| `0x40BC`, `0x40BD` | PV grid-connected generation time today (U16) and total (U32), 0.1 h | Documented |
| `0x8E00`–`0x8E63` | Per pack: BMS type, BMS serial (16 characters), BMS software and hardware version (0.001), battery type (50, 80 or 100 Ah), battery serial | Documented |
| `0x4200`–`0x4264` | Parallel-system mode, IDs, counts, power, SOC, capacity and energy, with the same layout as the HS3 block | Documented in an H2-family document cited by the field tooling's author. A field report from an H2 behind an AIO3 gateway found `0x4204`–`0x4209`, `0x4216` and `0x421E` answering with live values, SOC correct. Field reports describe H2-family units run in on-grid parallel (Decision 12). On the H2 each power at `0x4204`–`0x420A` is one 16-bit register (PV, backup and on-grid load unsigned; battery, grid and load signed), with no high words |
| `0x4209` | Parallel-system state of charge | Field report on an H2 and readings on an HS3: whole percent. The H2-family document says 0.01 % (Decision 13) |
| `0x3659` | Lead-acid battery total capacity, Ah, default 0 | Documented: applies to lead-acid batteries only |

A field report shows the H2 settings block answering beyond `0x367C`, so reading up to `0x367C` stays inside what answers. A refused range is narrowed by the existing read planner.

Where the document's English contradicts its Chinese, the Chinese is used: `0x3664` is the float charge voltage and `0x3665` the equalising charge voltage.

## Behaviour

### New Entities

Every new entity is created disabled, except the grid totals, which are core as on the HS3. Commissioning settings show their real control type and refuse changes with the existing protected-setting error. Readings of the `Quantity` types that are diagnostic today stay in the Diagnostic category.

| Key | Register | Kind | Notes |
| --- | --- | --- | --- |
| `buzzer` | `0x3632` | switch | On when the register is 0 |
| `led_mode` | `0x3675` | select | HS3 key and options |
| `battery_forced_charge_power_limit` | `0x3676` | number | Battery equipment, power-limit setting, 10 to 100 % |
| `off_grid_mode` | `0x3668` | reading | Decision 7 |
| `inverter_stop` | `0x3677` | reading | Decision 7 |
| `inverter_error_count` | `0x400F` | reading | |
| `drm_hardware_status`, `drm_software_status` | `0x4017`, `0x4018` | reading | Code |
| `grid_connection_countdown` | `0x4019` | reading | HS3 key |
| `fault_record_sequence` | `0x401A` | reading | |
| `settings_sequence` | `0x401B` | reading | HS3 key, Decision 11 |
| `application_mode_active` | `0x4022` | reading | The H2 application mode options |
| `battery_controller_1_current`, `battery_controller_2_current` | `0x406B`, `0x406C` | reading | Battery equipment |
| `pv_generation_time_today`, `pv_generation_time_total` | `0x40BC`, `0x40BD` | reading | Hours |
| `battery_voltage_low_warning` | `0xA033` | reading | Battery equipment, next to `battery_voltage_high_protection` |
| `grid_import_energy_*`, `grid_export_energy_*` | `0x4167`, `0x416F` | reading | Moved, Decision 2 |
| `grid_l1_import_energy_*`, `grid_l1_export_energy_*` | `0x40F7`, `0x40EF` | reading | HS3 keys, Decision 2 |
| `battery_pack{n}_bms_type`, `_bms_serial_number`, `_bms_software_version`, `_bms_hardware_version`, `_type`, `_serial_number` | `0x8E00` + 20(n−1) | reading | Battery equipment, n = 1 to 5, serials private, Decision 8 |
| Decision 5 settings | As listed | number or select | Protected. Keys named after their meaning with a `lead_acid_`, `parallel_`, `off_grid_`, `pv_` or `mppt_` prefix where that is what they govern |

`application_mode` gains `10: peak_shaving` on the H2. `battery_voltage` and `battery_current` become enabled by default on the H2.

### Request Load

The default H2 read with a battery and Meter A goes from 7 to 8 requests (Decision 2). The read with every row and everything fitted is recounted, and the README states both numbers. The battery identity block adds requests only when its entities are enabled.

### Power Control

Unchanged. The H2 has Battery power control only. The README states why it has no Grid or Inverter control.

## Implementation Design

### SAJ Library

| Module | Change |
| --- | --- |
| `saj/definitions.py` | The new definitions, the battery identity family, `Unit.HOUR`, the new option maps, the Decision 5 keys added to `COMMISSIONING_KEYS`, and `parallel_battery_soc` read in whole percent (Decision 13) |
| `saj/models/h2.py` | Placements with their evidence, the battery identity family, the grid total and phase-1 families as on the HS3, the realtime span extended to `0x4176`, a battery identity span `0x8E00`–`0x8E63`, `peak_shaving` in the application mode options, and battery voltage and current moved to Implemented. |
| `saj/catalogue.py` | No change expected. If a placement needs one, the change is model-neutral |

### Integration

| Module | Change |
| --- | --- |
| `translations/en.json` | Names of every new entity and option |
| `equipment.py` | No change. The H2 pack maximum of 5 comes from the catalogue |

### Modbus Mock

The H2 simulator serves every row this plan places, from the H2 document and the field evidence above. It already serves most of them. It gains whatever is missing, such as the all-phase counters on the H2 and application mode 10. It is not shaped around the integration.

| Area | Behaviour |
| --- | --- |
| Parallel-system block `0x4200`–`0x4264` | Served on the H2 with the HS3 layout (Decision 12), except that each power at `0x4204`–`0x420A` is a single 16-bit register with no high words, as the H2-family document defines it. An H2 scenario can configure a parallel system |
| Lead-acid battery total capacity `0x3659` | The documented default 0. The simulated battery is lithium with a BMS, and the register applies to lead-acid batteries only |
| Machine model `0x366C` and rated power `0x366D` | The simulated unit's own model and rating, as a real unit reports them. Both lie inside the documented ranges |
| Battery packs | Up to 5 on the H2, matching the document's five pack identity slots |
| Meter B `0xA053`–`0xA065` | An H2 scenario can fit a Meter B, served as the H2 document defines it. Field reports describe H2-family units with a second meter, such as one measuring a separate PV inverter |

## Roadmap Changes

On delivery:

- "Full H2 support" is removed.
- Under "Rough ideas", the sub-devices note that the battery has no catalogued identity is corrected: the H2 battery identity is catalogued.

## Documentation

- README: the H2 rows of the support table; entity and default counts; the request counts; the new writable settings; peak shaving; the commissioning list; the H2 pack maximum of 5; why the H2 has no Grid or Inverter power control; which H2 claims rest on field reports and which on the document only.
- `documentation/development.md`: the H2 evidence rules of this plan, the battery identity family, and the grid totals placement now shared by both models.

## Verification And Acceptance

Unit tests, each on one module with collaborators replaced:

- Catalogue: the H2 places every new key; the battery identity members follow the pack limit, with all five without a limit; serial rows are private; Decision 5 keys are protected; the grid totals and phase-1 counters are placed as on the HS3.
- Codec and write path: `buzzer` reads on at 0 and writes 0 for on; a write to a protected new key is refused without touching the inverter; `battery_forced_charge_power_limit` writes and reads back through the existing path.
- Options: `application_mode` on the H2 decodes and encodes `peak_shaving`.
- Codec: `parallel_battery_soc` decodes a raw 100 as 100 %.
- Translations: every new entity and option is named.
- Simulator: unit tests for any rows it gains; the H2 lead-acid capacity reads 0 with a battery fitted; an H2 scenario accepts 5 packs and refuses 6; an H2 scenario with a parallel system serves the parallel block; an H2 scenario with a Meter B serves its status and readings.

Smoke: the existing per-model smoke test passes unchanged. No new browser test.

Acceptance:

1. An H2 with a battery and Meter A reads the default set in 8 requests, and `sensor.saj_grid_import_energy_total` comes from the all-phase counter.
2. `sensor.saj_battery_voltage` and `sensor.saj_battery_current` are enabled by default on a new H2 installation.
3. With control allowed, `select.saj_application_mode` offers `peak_shaving` on an H2 and not on an HS3.
4. With control allowed, `switch.saj_buzzer`, `select.saj_led_mode` and `number.saj_battery_forced_charge_power_limit` change the H2 and show the value read back.
5. With control allowed, a change to `select.saj_grid_type` or any other Decision 5 setting is refused with the protected-setting error and nothing is written.
6. An H2 reporting 2 packs has identity entities for packs 1 and 2 only. With a count of 0 it has five.
7. The diagnostics snapshot of an H2 with identity entities enabled shows the serial rows redacted.
8. An H2 has no Grid or Inverter power control entities, and the README says why.
9. A simulated H2 in a parallel system shows the parallel-system entities when they are enabled.
10. A simulated H2 with 5 packs runs, and the integration shows identity entities for all five.
11. No HS3 key, entity ID or request count changes.
12. `make ci` passes with the coverage gate.

## Work Sequence

1. Definitions: units, options, the new keys, the identity family, the protected keys.
2. The H2 model file: placements, families, spans, options, evidence changes.
3. The simulator rows.
4. Translations.
5. README, `documentation/development.md`.

Each step ends with `make ci` passing.

## Revisions

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-14 | First draft. |
