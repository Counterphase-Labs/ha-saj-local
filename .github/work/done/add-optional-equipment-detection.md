# Add Optional Equipment Detection

## Plan Metadata

- **Revision:** 3
- **Status:** Approved
- **Last revised:** 2026-10-11
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Roadmap item:** "Optional equipment detection" in the [Roadmap project](https://github.com/orgs/Counterphase-Labs/projects/1)
- **Builds on:** `add-opt-in-register-writes.md` and the plans it builds on. Everything in those plans that is not restated or explicitly replaced here continues to apply.

## Outcome And Scope

Every time an installation is set up, which includes every Home Assistant start and every reload, the integration works out which optional equipment an installation has and creates entities only for that equipment. Each piece of equipment can be forced to fitted or not fitted in Configure.

| Requirement | Delivered by |
| --- | --- |
| Automatic detection where possible, with override an option | Battery, Meter A, Meter B, EV charger and parallel system are detected; each has an Automatic, Fitted, Not fitted setting |
| Convention over configuration; no pages of config | Nothing is asked during setup. The settings sit in one collapsed section of Configure, all on Automatic |
| Ability to read only certain sensors | Rows of equipment that is not fitted do not exist, so they are never read or written |
| Target both reading and writing of registries | EMS control of the EV charger, for an installation that has one |
| Clear and detailed errors | Equipment that was detected and no longer is raises a repair issue |
| A new system without a battery loses only its battery sensors (Assumptions) | Battery rows are removed when no battery is fitted; every other entity keeps its ID and history |

Entities by equipment, measured from the shipped catalogue. Probe keys are not counted: they belong to the inverter.

| Equipment | Models | HS3 entities | H2 entities (every phase and string) | Enabled by default when fitted |
| --- | --- | --- | --- | --- |
| Battery | HS3, H2 | 124 | 137 | 11 on HS3, 10 on H2, as today |
| Meter A | HS3, H2 | 25 | 19 | `meter_a_power` |
| Meter B | HS3, H2 | 25 | 19 | `meter_b_power` |
| EV charger | HS3 | 87 | — | Status, mode, power, session energy, total energy |
| Parallel system | HS3, H2 | 75 | 50 | The PV, battery, grid and load powers and the state of charge |

## Decisions

| # | Decision | Outcome |
| --- | --- | --- |
| 1 | Whether optional equipment becomes its own Home Assistant device | Decided by the user 2026-10-11: one device, as today. Child devices raise the question of splitting the whole installation into devices, which is not part of this work |
| 2 | Whether automatic detection can remove equipment | Confirmed by the user 2026-10-11: never. Equipment that was detected and now is not is reported instead. Meter B is detected from a live status, so a meter that is offline during a restart would otherwise take its entities with it. See Remembered Equipment |
| 3 | What an unanswered probe means | Accepted by the user 2026-10-11: battery is assumed fitted, the others not fitted. A battery is the common case and carries default-enabled entities; the others carry none |
| 4 | Narrowing battery-pack rows to the number of packs | Built. The pack count limits the rows only when it reads at least 1; see Battery Packs |
| 5 | Whether the probes wait for readings from the real HS3 | Decided by the user 2026-10-11: no. Its values at the probe registers were never recorded, so the probes rest on the documents and field tooling for now |
| 6 | Which battery protocol options the H2 has | Decided by the user 2026-10-11: its own, from the H2 document. The shared list holds the HS3's codes only, so an H2 code had no name. See H2 Battery Protocol |
| 7 | Whether a request may cross registers of equipment that is not fitted | Decided by the user 2026-10-11: yes, inside a documented block, under the catalogue plan's bridging rule. No row of equipment that is not fitted is ever requested |
| 8 | The browser smoke test after setup grew by the detection requests | Decided by the user 2026-10-11: the smoke test waits longer for its setting change. The request budget is unchanged |
| 9 | Work this plan first set aside | Set by the user 2026-10-11: none of it is deferred. EMS control of the EV charger, detected equipment enabled by default, battery-pack rows limited to the packs present, parallel rows on H2, the repair issue and Meter A are all built here |
| 10 | `meter_a_power` enabled by default on H2, where it is document-only, adding one request to the H2 default read | Decided by the user 2026-10-11: keep it. Meter A follows the same rule as the other detected equipment |

## Evidence

Same sources and order of authority as the catalogue plan: real HS3 readings, field tooling in sustained use, then the SAJ protocol documents. The mock is not a source.

| Equipment | Probe | Fitted when | Evidence |
| --- | --- | --- | --- |
| Battery, HS3 | `battery_protocol` `0x363B` | not 0 | Verified: reads 24 (SAJ-BU3) on a real HS3 with a battery. Document: 0 is "battery not in use" |
| Battery, H2 | `battery_protocol_active` `0x4028` | not 0 | Implemented. Document: 0 is "no using battery". `0x363B` is document-only on H2 |
| Meter A | `meter_a_status` `0xA03C` | 1 | Verified on HS3: reads 1 with its meter online. Document-only on H2. Field tooling keys Meter A on exactly this |
| Meter B | `meter_b_status` `0xA053` | 1 | Responds, unchecked on HS3; document-only on H2. Field tooling keys Meter B on exactly this |
| EV charger | `ev_enabled` `0x4B04` | 1 | Verified as readable. Field tooling keys the charger on exactly this |
| Parallel system | `parallel_mode` `0x4200`, `parallel_online_count` `0x4203` | mode not 0, or online count above 1 | HS3: responds, unchecked. Field tooling uses exactly this rule. H2: see Parallel On H2 |

What the readings rule out as probes:

- **Battery pack count `0xA000` and online code `0xA00B`** as a sign of a battery: they read 0 on a real HS3 with a battery, and field reports show the same on H2-family units with SAJ batteries, including packs 2 and 3 reading zero with three packs fitted. A count of 0 therefore says nothing; a count of 1 or more is used, see Battery Packs.
- **Parallel power words `0x4204`–`0x4209`** carry live values on a single, non-parallel H2-family unit in one field report.
- **EV charger data `0x3024`–`0x30BB`** is refused with exception `0x30` on a real HS3 without a charger. A refusal is not used as a probe: it costs a refused request on every setup, and the module has misbehaved after refusals before.

Gaps:

- No reading exists from a unit without a battery, with a charger, with a second meter or in a parallel system. Every "fitted" and "not fitted" value above other than the HS3 battery rests on the documents and field tooling.
- The real HS3's values at `0x4B04`, `0xA053` and `0x4200`–`0x4203` were never recorded. That unit has no charger, no second meter and no parallel machine, so all three should read as not fitted. Reading them is not a step of this plan (Decision 5); it is kept under Open Questions below. A wrong probe is corrected by the override until then.

## Behaviour

### Equipment And Rows

| Equipment | Rows |
| --- | --- |
| Battery | Keys starting `battery_`, `average_battery_`, `passive_battery_`, `backup_reserve_soc`, `ems_battery_`, `charge_slot` and `discharge_slot` |
| Meter A | Keys starting `meter_a_` |
| Meter B | Keys starting `meter_b_` |
| EV charger | Keys starting `ev_` |
| Parallel system | Keys starting `parallel_` |

`meter_configuration` and `meter_address` are inverter settings and belong to no equipment.

Probe keys belong to the inverter and exist on every unit, whatever is fitted: `battery_protocol`, `battery_protocol_active`, `battery_pack_count`, `meter_a_status`, `meter_b_status`, `ev_enabled`, `parallel_mode`, `parallel_online_count`. They are how a user sees why equipment was not detected.

The prefixes describe the grouping; in code a row's equipment is an explicit field on its definition, never derived from its key.

### Detection

- Runs at every setup, so on every Home Assistant start and every reload, after the model is identified and before the first read.
- Every probe key of the equipment being probed, and the pack count, is read in one planned read, so probes in the same block share a request: at most 4 requests on either model, inside the request budget.
- Only equipment set to Automatic is probed.
- A probe that is refused or returns a value that cannot be decoded is unanswered: battery and Meter A are then assumed fitted, the others not fitted. Meter A is assumed for the same reason as the battery (Decision 3): it is the common case and carries a default-enabled entity. A refused request leaves every probe it carried unanswered. A timeout fails setup as any other read does.
- Runs on a model override too. It only reads.

### Remembered Equipment

Equipment detected on Automatic is remembered with the installation and stays fitted on later setups, whatever the probe then reads. It is forgotten only when the user sets it to Not fitted; returning to Automatic detects from scratch.

Equipment fitted later is picked up at the next restart or reload.

Remembered equipment that a probe now reads as not fitted stays fitted and is reported three ways: one warning per setup naming the equipment and the probe values, a flag in diagnostics, and a repair issue. Its rows read whatever the device answers.

The repair issue is one per installation and piece of equipment, a warning that is not fixable from the issue itself. It names the installation and the equipment and says what to do: check the equipment, or set it to Not fitted in Configure. It is raised at the setup that finds the lapse and removed at the first setup where the equipment is detected again or is no longer on Automatic, and when the installation is removed.

### Override

Configure gains a collapsed **Equipment** section with one field per piece of equipment the model can have: Automatic (default), Fitted, Not fitted. H2 shows Battery, Meter A, Meter B and Parallel system; HS3 shows all five. The section's description states what is currently treated as fitted. Setup does not ask.

Fitted creates the rows without probing. Their values are whatever the device answers, and rows it refuses follow the existing refusal handling.

### Entities

- Rows of equipment that is not fitted are not created, read, planned, offered in polling groups or writable.
- At setup, registry entries of this installation whose row belongs to equipment that is not fitted are removed, so no "no longer provided" entities are left behind. Entity IDs are fixed, so long-term statistics continue if the equipment is fitted later. Registry customisations of the removed entities are lost; the Not fitted option says so.
- A polling group keeps the keys of equipment that is not fitted and ignores them, as it already does for keys the device does not have.
- A combined value exists only when its equipment is fitted.

### Enabled By Default

Rows of optional equipment exist only when that equipment is fitted, so their default no longer waits for a reading of the equipment: a row of Meter A, Meter B, the EV charger or the parallel system that is marked core is enabled by default whatever its evidence. Battery rows and inverter rows keep the earlier rule, enabled by default only when Verified on HS3 or Implemented on H2. The rule for a model override, where rows beyond one phase and two strings are created disabled, is unchanged.

| Equipment | Core rows |
| --- | --- |
| Meter A | `meter_a_power`, as today |
| Meter B | `meter_b_power`, new: the sum of the three Meter B phase powers, built like `meter_a_power` |
| EV charger | `ev_status`, `ev_mode`, `ev_power`, `ev_session_energy`, `ev_total_energy` |
| Parallel system | `parallel_pv_power`, `parallel_battery_power`, `parallel_grid_power`, `parallel_load_power`, `parallel_battery_soc` |

An entity already in the registry keeps the enabled or disabled state it has.

### EV Charger EMS Control

HS3 only, rows of the EV charger, catalogued as Documented and created disabled:

| Key | Register | Entity | Value |
| --- | --- | --- | --- |
| `ev_ems_charging` | `0x4B46` bit 0 | switch | The bit is inverted on the device: 0 is charging on, 1 is off. The entity shows and takes on and off the right way round |
| `ev_ems_phase_mode` | `0x4B46` bits 1–2 | select | 0 three-phase, 1 single-phase. Code 2 is reserved and code 3 repeats three-phase; neither is offered, and either reads as unknown with the code in diagnostics |
| `ev_ems_charge_current` | `0x4B47` | number | 6 to 32 A in steps of 0.1 A |

- The document marks both registers read and write. They are read like any other enabled row and written through the existing write path: control must be on, the model verified, the register is read, changed and read back, and a packed field keeps the other bits.
- They are not commissioning settings and are not protected.
- The EV charger settings block is extended to `0x4B47` to hold them.
- No reading of these registers exists and there is no charger to test against. Whether reading them counts as EMS activity, as it does for the inverter's EMS targets, is not known; they are created disabled, so nothing reads them until the user enables them.

### Battery Packs

`battery_pack_count` (`0xA000`) is read with the probes on a model that has rows for more than one pack. A count from 1 up to the model's maximum limits the pack rows, `battery_pack<n>_…`, to that many packs. A count of 0, a count above the maximum, or no answer leaves every pack row in place, because 0 is what a real HS3 with a battery reports. The highest count seen is remembered with the installation and is never lowered automatically; setting the battery to Not fitted forgets it. The HS3 has rows for one pack, so nothing changes there and it does not read the count for this.

### Parallel On H2

The H2 gets the parallel block: `0x4200`–`0x4264`.

- Evidence: a protocol document of the H2 family defines the block at these addresses, and one field report shows an H2-family unit answering `0x4204`–`0x4209` with live values. The single-phase H2 document this project holds does not list it. The rows are catalogued as Documented.
- Rows: `parallel_mode`, `parallel_id`, `parallel_count`, `parallel_online_count`, `parallel_battery_soc` (`0x4209`), `parallel_battery_capacity` (`0x420B`), the six powers, and the energy counters for PV, battery charge, battery discharge, export and import per phase, and load (`0x4215`–`0x4264`).
- The six powers keep their keys, `parallel_pv_power` and the rest. On H2 each is one 16-bit register (`0x4204`–`0x4208`, `0x420A`): PV, backup load and grid load unsigned, battery, grid and load signed. On HS3 each stays the 32-bit value made from its low and high words. The H2 has no high words, no `parallel_meter_b_power` and no grid import, grid export or PV meter energy counters.
- Detection and the override work as on HS3. Unanswered means not fitted, so an H2 that does not have the block costs one refused request per setup and gets no parallel entity.

### H2 Battery Protocol

`battery_protocol` (`0x363B`) on H2 takes its options from the H2 document: 0 not in use, 2 lead-acid, 20 Dyness DYNESS-H, 21 Pylon SC0500, 22 B2 CAN. The HS3 keeps 0 not in use and 24 SAJ BU3. The row stays Documented on H2, so it is created disabled, and it stays a read-only commissioning setting. `battery_protocol_active` (`0x4028`) stays a plain code on both models; detection only asks whether it is zero.

### Diagnostics And Logging

- Diagnostics gain, per piece of equipment: the setting, the raw probe values, whether it is remembered, whether it is remembered but no longer detected, and the result; and the pack count read and the one in use.
- One info line when the fitted set of an installation changes. One warning per setup for remembered equipment that is no longer detected. Probe values at debug.

## Implementation Design

### SAJ Library

| Module | Change |
| --- | --- |
| `saj/equipment.py`, `saj/detection.py` | The settings, the resolution and the probe read. Detection reads every probe key in one planned read |
| `saj/definitions.py` | `Definition.equipment`. Meter A tagged. `meter_b_power`. The three EV charger EMS rows, with a bit field that can be inverted. The core marks under Enabled By Default |
| `saj/codec.py` | An inverted single-bit field, decoded and encoded |
| `saj/models/` | Probes: five on HS3, four on H2. The H2 parallel block and its replacements; a replacement can turn a combined key into a single register for a model. The H2 battery protocol options. The HS3 EV charger settings span to `0x4B47` |
| `saj/catalogue.py` | Rows selected by shape, fitted equipment and pack count. Core for optional equipment rows does not depend on evidence. The probe and combination checks |
| `saj/device.py` | `Device.equipment` and the pack count in use |
| `saj/telemetry.py`, `saj/load.py`, `saj/control.py` | Take the fit wherever they take the device type |

### Integration

| Module | Change |
| --- | --- |
| `const.py` | The equipment option and what is stored with the entry: detected set, fitted set, highest pack count |
| `equipment.py` | Detection at setup, the stored values, registry removal, the warning, and the repair issue raised and removed |
| `__init__.py` | Calls it after identify; removes the installation's repair issues when the entry is removed |
| `config_flow.py` | The Equipment section with the model's fields. Stored-data loads and polling-group choices use the stored fit |
| `entity.py`, `coordinator.py`, `diagnostics.py` | Use the device's fit; the diagnostics additions |
| `translations/en.json` | The section and its fields, the repair issue, the new entities and option names |

### Modbus Mock

Built from the documents, not from the integration: a scenario with no battery modules reports 0 at `0x363B` and `0x4028`, and the H2 mock reports a battery code its own document lists. No other change; the charger enable, Meter B status and parallel counts already follow the scenario.

## Open Questions

Nothing in this plan is deferred. One question stays open by the user's decision (Decision 5) and is kept here, not in the roadmap: what the real HS3 reads at `0x4B04`, `0xA053` and `0x4200`–`0x4203`. That unit has no charger, no second meter and no parallel machine, so all three should read as not fitted.

## Verification And Acceptance

Unit tests, each on one module with collaborators replaced, using rows and probes built for the test:

- Equipment: each condition met and not met; any-of; a refused and an undecodable probe for each unanswered result; equipment not on Automatic not probed; probes in one block sharing a request, and a refused request leaving each of its probes unanswered.
- Pack count: 0, in range, above the maximum and unanswered; the highest seen kept; forgotten with the battery set to Not fitted; not read on a model with one pack.
- Codec: an inverted bit decoded and encoded, and the other bits of its register kept.
- Catalogue: rows by fitted set and pack count; core for an optional equipment row whatever its evidence, and unchanged for battery and inverter rows; a combined key placed as a single register on one model and combined on another; the H2 battery protocol options decoded and the HS3's unchanged; a combined value following its equipment; each rejected probe and the mixed-equipment combination rejected.
- Telemetry, load, control: rows of equipment that is not fitted are not planned, counted or writable.
- Repair issue: raised for a lapse, not raised otherwise, removed when detected again, when the setting leaves Automatic and when the installation is removed.
- Setup: each of setting × remembered × probe result; the remembered set stored only when it changes; the warning for remembered equipment that is no longer detected, once per setup and for nothing else; Not fitted forgets; registry entries removed for equipment that is not fitted and for nothing else.
- Config flow: the section's fields per model; a change saved and applied; stored-data loads and polling-group choices follow the stored set.
- Diagnostics: the additions.
- Mock: the battery protocol registers with and without modules, per model.

Smoke: the existing per-model smoke test passes, with its wait for the setting change lengthened past the 60-second budget window: the reload that follows switching control on now includes the detection requests, and a write made straight after it waits for the budget. No new browser test, and no other change to the existing one.

Acceptance:

1. An HS3 reporting battery protocol 0 has no battery entity; one reporting 24 has all of them, with the same entity IDs and unique IDs as today.
2. An HS3 with no charger, second meter or parallel machine has no `ev_`, `meter_b_` or `parallel_` entity other than the probe keys, and with every entity enabled no row of that equipment is ever requested. No request reads any register in `0x3024`–`0x30BB`, `0x4204`–`0x427C` or `0x4B05`–`0x4B45`. Meter B words that lie between Meter A rows may be crossed by a Meter A request, as any gap inside a documented block may.
3. Meter B detected once is still fitted after a restart during which its status reads 0, and that restart logs one warning naming it. An EV charger enabled on the inverter after setup has its entities after the next restart.
4. Not fitted removes the equipment's entities and registry entries; Automatic afterwards detects from scratch.
5. Fitted creates the rows whatever the probe reads, and sends no probe for that equipment.
6. No setting of a piece of equipment that is not fitted can be written, with control on.
7. Setup sends at most 4 detection requests on either model.
8. An H2 reporting 22 at `0x363B` shows its battery protocol by name.
9. Meter B that was detected and now reads offline has a repair issue naming it, and the issue is gone after a setup that detects it again.
10. A newly detected EV charger has its status, mode, power and both energy entities enabled by default, and a newly detected Meter B has `meter_b_power` enabled.
11. On an HS3 with a charger and control on, switching `ev_ems_charging` on writes bit 0 of `0x4B46` as 0 and leaves bits 1 and 2 as they were; `ev_ems_phase_mode` never writes code 2 or 3.
12. An installation with no Meter A has no `meter_a_` entity other than `meter_a_status`.
13. An H2 reporting 2 packs has pack rows for packs 1 and 2 only; one reporting 0 has all of them.
14. An H2 whose parallel probe answers as fitted has `parallel_pv_power` read from `0x4204` as one register; an H2 that refuses the probe has no parallel entity.
15. `make ci` passes with the coverage gate.

## Work Sequence

Steps 1 to 6 are built. Steps 7 to 13 are the work first set aside.

1. `Definition.equipment`, the catalogue selection and checks, and the fitted set through telemetry, load and control, with every equipment treated as fitted. Behaviour unchanged.
2. `saj/equipment.py` and the profile probes.
3. Setup: detection, the remembered set and registry removal.
4. The Equipment section in Configure, translations and diagnostics.
5. The mock's battery protocol registers.
6. README and `documentation/development.md`.
7. Detection in one planned read.
8. Meter A as optional equipment.
9. The repair issue.
10. Optional equipment rows enabled by default, and `meter_b_power`.
11. EV charger EMS control, with the inverted bit field.
12. Battery-pack rows limited by the pack count.
13. Parallel on H2. Then README and `documentation/development.md` for steps 7 to 13.

Each step ends with `make ci` passing.

## Revisions

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-11 | First draft. |
| 2 | 2026-10-11 | The H2 gets its own battery protocol options (Decision 6). A request may cross registers of equipment that is not fitted inside a documented block, and acceptance check 2 is reworded to match (Decision 7). The smoke test's wait for its setting change is lengthened instead of passing unchanged (Decision 8). |
| 3 | 2026-10-11 | At the user's direction nothing is deferred: EMS control of the EV charger, optional equipment enabled by default, battery-pack rows limited by the pack count, parallel on H2, the repair issue and Meter A are built in this plan. Detection reads its probes in one planned read. |
