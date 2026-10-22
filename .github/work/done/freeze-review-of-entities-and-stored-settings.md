# Freeze Review Of Entities And Stored Settings

## Plan Metadata

- **Revision:** 2
- **Status:** Approved
- **Roadmap item:** Freeze review of entities and stored settings
- **Last revised:** 2026-10-22
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Order:** After `rename-mock-and-clone-to-saj-local.md`, so the paths below are the paths after the rename. Before the roadmap items "HS3 fault bits, EV charger fault bytes and meter totals" and "Target languages and translations".

## Outcome And Scope

After the first release, every entity key, entity ID, unique ID, device identifier, stored setting and card setting becomes permanent: a change breaks users' automations, dashboards, history or saved configuration. The present plan reviews the whole surface once, while breaking changes are still allowed, fixes every mistake found, and adds a `make ci` step that stops a later change from breaking the released surface.

Included:

- A review of every entity both models can create: key, platform, unit, device class, state class, state values, entity category, default-enabled state, and English display name.
- A review of the identifiers: unique ID, device identifier and entity ID scheme.
- A review of the stored settings: config entry data, options, the polling-group and power-schedule subentries, the power control store, and the values stored inside each.
- A review of the card surface: card, badge and card feature type names, card settings, and the English card texts.
- The device structure for the first release, recorded as a requirement.
- Fixes for every finding the user approves.
- A `freeze-check` step in `make ci`, comparing the surface with the newest release tag.

Not changed: how values are read, decoded or written; the HS3 fault bit positions, EV charger fault byte order and meter total formula (roadmap item "HS3 fault bits, EV charger fault bytes and meter totals"); languages other than English (roadmap item "Target languages and translations").

## Requirements

- Non Functional in `../requirements.md`: "Backwards compatibility MUST drive architecture decisions. Sensor names must remain stable. Architecture decisions should limit the possibility of being boxed into creating breaking changes."
- Non Functional in `../requirements.md`: before release, breaking changes are allowed and no backwards compatibility layer is written. Every fix in the present plan is a direct change with no migration code.
- Non Functional in `../requirements.md`: one unified interface across models, "consistent names, values, units and behaviour"; one sign for battery and grid power on every model; controls defined once and shared.
- Entity IDs in `../requirements.md`: entity IDs are fixed by code, `<domain>.saj_<key>` or `<domain>.saj_<prefix>_<key>`; changing a prefix keeps history.
- Main Integration in `../requirements.md`: every Lovelace element is set up by choosing a system and keeps working when the system's prefix changes; full localisation support.
- Non Functional in `../requirements.md`: 100 % unit test coverage from unit tests alone; no tests of hard-coded values; all commands exposed as make targets; GitHub runs the same make targets.

## Requirement Changes

Two additions to `../requirements.md`, applied with the present plan:

1. Under Main Integration: "Each system is one Home Assistant device. A later split into sub-devices keeps the system's device as the base device, so cards and device automations pointing at the system's device keep working."
2. Under Non Functional: "Once a release exists, `make ci` fails when a change removes an entity key, a stored setting key, a card type or a card setting, changes an entity's platform, unit, device class, state class or state values, removes a value a card setting accepts, or lowers a config entry or store version, compared with the newest release tag."

## Decisions

- **Display names are in scope.** The review covers the English entity names and state labels in `custom_components/saj_local/translations/en.json` and the card texts in `frontend/src/i18n/en.json`, so the translations roadmap item translates final texts. Chosen 2026-10-21.
- **One device per system.** The first release keeps one device per system. A later sub-device split keeps the system's device as the base device. The backlog Idea "Sub-devices" stays an Idea. Chosen 2026-10-21.
- **Freeze check compares with the newest release tag.** No duplicate list and no committed hash. The surface is generated from code at both points and compared. Chosen 2026-10-21; design under "Freeze Check".
- **Unique IDs stay based on the config entry ID.** `entity_unique_id` in `custom_components/saj_local/const.py` builds `<entry id>_<key>`, and `entity.py:114` identifies the device as `(saj_local, <entry id>)`. The alternative, the inverter serial, is the config entry's unique ID, and the reconfigure flow replaces the serial when an inverter is swapped (`save` in `config_flow.py`, `unique_id=change.device.serial`). A serial-based unique ID would detach every entity and the device on an inverter swap. Entity history is keyed by entity ID, and entity IDs are fixed by code, so removing and re-adding a system keeps history with the entry-based unique ID too. The review records the identifier scheme as checked, with no change.
- **Card settings are frozen.** Home Assistant stores card settings in users' dashboards, so a renamed or removed card setting, or a removed value of a select setting, breaks saved cards. Chosen 2026-10-22.
- **Version numbers may rise.** The freeze check lets `VERSION`, `MINOR_VERSION` and the store version rise and fails a fall, because the versioning rule requires a rise with every stored-form change. Chosen 2026-10-22.
- **Findings approved, except finding 21.** The user approved findings 1 to 20 and 22 to 28 under "Findings" on 2026-10-22, with the corrections recorded in the rows. The user rejected finding 21: English texts and keys use British spelling, always. Finding 17 was withdrawn because the HS3 PDF documents the 13 keys.
- **Findings go to the user before fixes.** The review appends a findings table to the present plan in a new revision. Each finding states the problem and one recommended fix. Fixes start once the user has ruled on the findings.

## Surface Under Review

Figures from the catalogue on 2026-10-21 (`CATALOGUES` in `custom_components/saj_local/saj/catalogue.py`, exposed and not private registers):

| | HS3 | H2 |
| --- | --- | --- |
| Entities from the register catalogue | 734 | 565 |
| Default-enabled (`core`) | 182 | 127 |
| Controls | 139 | 89 |
| sensor / binary_sensor / number / time / switch / select / button | 425 / 129 / 77 / 42 / 37 / 19 / 5 | 353 / 73 / 79 / 28 / 17 / 11 / 4 |
| Evidence | 447 verified, 148 documented, 103 respond unchecked, 36 respond undocumented | 402 implemented, 163 documented |

433 keys exist on both models, 301 only on the HS3 and 132 only on the H2: 866 distinct keys. Entities outside the register catalogue: `control_allowed` (`binary_sensor.py`), the power control entities (`saj/power_control.py`, `number.py`), and the fault summary and unrecognised-fault entities (`fault_summary_key` and `fault_unrecognised_key` in `saj/definitions.py`).

Stored settings:

| Where | Keys and stored values |
| --- | --- |
| Config entry `data` | `host`, `port`, `unit_id`, `model`, `device_type`, `detected_equipment`, `fitted_equipment`, `highest_pack_count` |
| Config entry `options` | `scan_interval`, `prefix`, `allow_control`, `ems_heartbeat`, `equipment` (equipment name → `automatic` / `fitted` / `not_fitted`) |
| Subentry `polling_group` | `scan_interval`, `sensors` (a list of entity keys) |
| Subentry `power_schedule` | `function` (`battery` / `grid` / `inverter`), `schedule` (a schedule entity ID) |
| Store `saj_local.power_control.<entry id>`, version 1 | `targets` and `remembered_modes`, each keyed by power function |
| Config flow | `VERSION = 1`, no `MINOR_VERSION`, no `async_migrate_entry` |

Stored values matter as much as keys: the model keys, the equipment names (`battery`, `meter_a`, `meter_b`, `ev_charger`, `parallel`), the equipment settings and the power functions are all written into the config entry or the store. The `sensors` list of a polling group holds entity keys, so renaming an entity key also breaks every saved polling group.

Card surface: the card types `saj-local-power-flow-card`, `saj-local-status-card`, `saj-local-faults-card`, `saj-local-battery-card`, `saj-local-controls-card`, `saj-local-schedule-card`, the badge `saj-local-status-badge`, the card feature `saj-local-weekdays`, and the card settings of each element (`device` on every card and the badge, plus the display options of each card, such as `scope` and `sections`), with the values each select setting accepts.

## Review Checklist

The review first generates an inventory in the scratchpad (not committed) from the freeze surface script: one row per key with the HS3 and H2 values side by side, plus the English name and state labels. The rule checks below run as a throwaway script over the inventory; the remaining checks are read by hand.

### Entities

1. **Key naming.** Snake case, describes the quantity rather than the register, carries no model name, and follows the patterns already used for phases, PV strings, battery packs and equipment.
2. **One key per meaning.** Each of the 301 HS3-only and 132 H2-only keys is checked for a key on the other model with the same meaning under a different name. A pair found is merged into one key.
3. **Same form on both models.** For each of the 433 shared keys, the platform, unit, device class, state class and state values are identical on both models.
4. **Platform.** Each key uses the right platform. A platform change after release changes the entity ID's domain, so the platform is permanent.
5. **Units, device classes, state classes.** Every combination is one Home Assistant accepts; energy counters are `total_increasing` or `total` as the register behaves; battery and grid power follow the one sign convention.
6. **State values.** Enum options and binary sensor meanings (including `inverted`) are final, because automations compare against state values.
7. **Entity category and default-enabled state.** Diagnostic and configuration entities carry the right category; default-enabled entities are the ones most users need, chosen the same way on both models. A default-enabled change after release does not break existing installs, but the review settles the defaults once for new installs.
8. **Evidence.** Entities resting only on the SAJ document or on an unchecked answer (`documented`, `responds unchecked`, `responds undocumented`) are checked for a name claiming more than the evidence shows.
9. **English display names and state labels.** Consistent between models and between related entities, sentence case, no repetition of the device name, Home Assistant naming style.

### Identifiers

10. **Unique ID, device identifier and entity ID scheme.** Checked against the decision above and the Entity IDs section of `../requirements.md`, including the prefix rename path.

### Stored settings

11. **Config entry data and options.** Each key is needed, has the right owner (`data` for what identifies the system, `options` for what the user tunes), and has a final name and value form.
12. **Subentries.** The `polling_group` and `power_schedule` types, their data keys and their value forms.
13. **Power control store.** The store key, version, top-level keys and value forms.
14. **Versioning rule.** After release, a change to any stored form raises the config entry `VERSION` or `MINOR_VERSION`, or the store version, with a migration. The rule is written into `AGENTS.md`. No migration code is written now.

### Cards

15. **Card, badge and feature type names, and the card settings.** Final names, consistent with each other.
16. **English card texts** in `frontend/src/i18n/en.json`.

## Freeze Check

- **Surface script.** A new `.github/scripts/freeze_surface.py` prints the surface of the code tree given as its argument, as JSON:
  - for each model, every entity key with platform, unit, device class, state class and state values, built from the same functions the platforms use (the catalogue, `presentation_of` in `entity.py`, the power control and fault summary keys) and not from a hand-written list;
  - the unique ID, device identifier and entity ID forms, built by calling `entity_unique_id`, `fixed_entity_id` and the device identifier code with placeholder values;
  - the config entry data and option keys, the subentry types and data keys, the store key form, the store version, `VERSION` and `MINOR_VERSION`, and the stored value sets (model keys, equipment names, equipment settings, power functions);
  - the card, badge and feature type names read from the registrations in `frontend/src`; the script fails loudly when the registrations yield no names;
  - for each card, badge and feature, every card setting name and the values each select setting accepts, read from the element's editor definition (`getConfigForm` and the shared fields in `frontend/src/cards/editor.ts`), not from a text match over the whole file; the script fails loudly when an element with an editor yields no settings.
- **Comparison.** The `freeze-check` step finds the newest tag reachable from `HEAD` (`git describe --tags --abbrev=0`). With no tag, the step passes and prints "no release tag". With a tag, the step extracts the tagged tree with `git archive` into a temporary folder, runs the tagged tree's own `freeze_surface.py` on the tagged tree, runs the current `freeze_surface.py` on the working tree, and compares. Any key, form or value present at the tag and missing or different now fails the step, with one line per break, for example `hs3 sensor battery_power: unit W -> kW`. Additions pass. `VERSION`, `MINOR_VERSION` and the store version pass a rise and fail a fall.
- **Placement.** The step is added to the check runner in `.github/scripts/check_steps.py`, runs in `make ci`, and gets its own `make freeze-check` target. The comparison logic has unit tests with stubbed git and process calls; no unit test reads project files.
- **GitHub.** `.github/workflows/ci.yml` checks out with `fetch-depth: 0`, so tags are present.
- **Tags are releases.** The check treats every tag as a release. The roadmap item "Release workflow and versioning" therefore tags only releases.

## Implementation

1. Add `freeze_surface.py`, the `freeze-check` step, the make target, the unit tests and the `ci.yml` change. `make ci` passes with "no release tag".
2. Generate the inventory and carry out checks 1 to 16.
3. Append the findings table to the present plan as a new revision: one row per finding with the key or setting, the problem and the one recommended fix.
4. After the user has ruled on the findings, apply the approved fixes: definitions, translations (`custom_components/saj_local/translations/en.json`, `frontend/src/i18n/en.json`), config flow, store, cards, the development dashboards in `config/dashboards/`, the Playwright tests, and the simulator where a key is shared with the simulator page.
5. Apply the two requirement changes and the versioning rule in `AGENTS.md`.
6. The development Home Assistant config entries are removed and added again whenever a fix changes a stored form, since no migration code is written before release.

## Verification

- `make ci` passes, including `freeze-check`.
- A trial run with a local throwaway tag on the commit before the fixes shows the freeze check listing the fixed keys as breaks; the throwaway tag is deleted after the trial and never pushed.
- Both development systems (HS3 and H2) load with no errors in the Home Assistant log, and every card on the development dashboards shows values.

## Findings

Review of 2026-10-22 over the inventory generated by `freeze_surface.py`: 873 keys, 741 HS3 entities and 568 H2 entities (the catalogue figures above plus the entities outside the register catalogue), 436 keys shared by both models. Each row awaits the user's ruling; no fix is applied before the ruling.

| # | Check | Key or setting | Problem | Recommended fix |
| --- | --- | --- | --- | --- |
| 1 | 1 | `battery_charge_limit`, `battery_discharge_limit_on_grid`, `battery_discharge_limit_off_grid` | The three keys are state-of-charge thresholds (the battery card draws the three keys as markers on the `battery_soc` ring), but the keys carry neither `soc` nor the `battery` device class (quantity `percentage` in `_percent_setting`, `saj/definitions.py`), unlike the sibling `backup_reserve_soc`, and `battery_charge_limit` reads as a third kind of charge limit beside `battery_charge_power_limit` and `battery_charge_current_limit`. | Rename the three keys to `battery_charge_soc_limit`, `battery_discharge_soc_limit_on_grid` and `battery_discharge_soc_limit_off_grid`, give the three keys quantity `STATE_OF_CHARGE`, and update the labels, the card key lists and the translations. |
| 2 | 1, 2 | HS3 `meter_{a,b}_l{1,2,3}_power_high_word` (6 keys) and `parallel_{pv,battery,grid,load,backup_load,grid_load}_power_{high,low}_word` (12 keys) | 18 keys name a register word instead of a quantity and are exposed as entities. The HS3 already builds the combined `parallel_*_power` keys from the parallel words, and the six HS3 `parallel_*_power_low_word` keys sit on the addresses where the H2 publishes `parallel_*_power` (0x4204 to 0x420A), so one quantity has two keys across the models. | Set `exposed=False` on the 18 word definitions, so the words stay register sources for the combined keys and for the planned meter totals. |
| 3 | 1 | HS3 `average_*` (92 keys, for example `average_grid_power`) | The key prefix `average_` does not state the five-minute window that the labels state ("Grid power (5-minute average)"), so a later register block with another window has no free key space. | Rename the prefix to `five_minute_average_` for the 92 keys, with the translations, the `average_*` families of the HS3 profile and the simulator page. |
| 4 | 1 | H2 `protocol_version` | The bare key does not name the protocol, while the HS3 keys `ethernet_protocol_version`, `settings_protocol_version` and `ev_settings_protocol_version` each name the protocol. The H2 register 0x8F02 sits in the identity block and is a different register from the HS3 registers. | Rename the H2 key to `identity_protocol_version`, labelled "Identity protocol version". |
| 5 | 2 | HS3 `ems_battery_control`, `ems_grid_control`, `ems_inverter_control`, `ems_inverter_control_with_timeout_exit`, `ems_battery_power_target`, `ems_grid_power_target`, `ems_inverter_power_target` | The seven HS3 entities expose the raw EMS rows of power control (percent targets) beside the shared `<function>_power_control` switches and `<function>_power_target` numbers (watts) that write the same registers. Writing, in `requirements.md`, requires power control to be offered with the same entities, in watts, on every model. | Set `exposed=False` on the seven rows; `power_control` in `saj/models/hs3.py` keeps reading and writing the rows. The other EMS entities (`ems_timeout`, the two current limits, the import and export power limits, `ems_pv_power_limit`, `ems_pv_power_limit_remove`) have no shared counterpart and stay. |
| 6 | 3 | `application_mode`, `battery_protocol` | Platform, unit, device class, state class and `inverted` are identical on all 436 shared keys; only the option sets of the two keys differ by model (`application_mode`: HS3 `self_use`, `time_of_use`, `backup`, `ems`, `time_of_use_bms`; H2 `self_use`, `time_of_use`, `backup`, `passive`, `peak_shaving`, `ai_saving`, `legacy`. `battery_protocol`: HS3 `not_in_use`, `saj_bu3`; H2 `not_in_use`, `lead_acid`, `dyness_h`, `pylon_sc0500`, `b2_can`). | Keep the per-model option sets, because each inverter offers only the modes the inverter has, and freeze the option values per model. |
| 7 | 4 | The 56 keys in `PROTECTED_KEYS` (`saj/definitions.py`): the 50 `COMMISSIONING_KEYS`, `settings_sequence` and the 5 ethernet address settings in `ETHERNET_ADDRESS_KEYS` | Writing, in `requirements.md`, requires commissioning settings to be read-only, but the 56 keys are created as writable `number`, `select` and `text` entities (access `READ_WRITE`) whose writes are refused at run time by `ProtectedSettingError` (`saj/control.py`). Dashboards show controls that always fail, and the entity domain cannot change after release. | Change the 56 definitions to read-only sensors (kind `SENSOR`, access `READ_ONLY`): the selects become enum sensors with the existing options, the numbers keep the unit and device class of the quantity, and the ethernet addresses become text sensors. Remove the `text` platform when no entity uses the `text` platform any more. Keep the `PROTECTED_KEYS` write guard. |
| 8 | 4 | `rs485_baud_rate` | `rs485_baud_rate` is a `number` (quantity `count`, 0 to 65535), while `rs485_slave_baud_rate` and `ev_baud_rate` are selects over `BAUD_RATE_OPTIONS`. | Give `rs485_baud_rate` the `BAUD_RATE_OPTIONS` table, which makes `rs485_baud_rate` an enum sensor under finding 7. |
| 9 | 4 | `clear_fault_history` (button, both models) | Writing, in `requirements.md`, says actions that cannot be undone are not offered. Clearing the inverter's fault history cannot be undone, yet `clear_fault_history` is offered as a button. `clear_current_fault` only acknowledges the active fault and is not part of the present finding. | Remove `clear_fault_history` from the catalogue, both model address maps, the translations and `README.md`. The simulator keeps the command, because the simulator follows documented SAJ behaviour, not the integration. |
| 10 | 5 | `battery_capacity`, `battery_usable_capacity` | Quantity `capacity` with no unit, yet the presentation gives the two keys state class `measurement`; the related keys `parallel_battery_capacity` and `lead_acid_capacity` use `Ah`. | Set unit `Ah` on `battery_capacity` and `battery_usable_capacity`. |
| 11 | 5 | `meter_a_power`, `meter_b_power`, `meter_{a,b}_l{1,2,3}_power`, `parallel_meter_b_power` | Non Functional in `requirements.md` fixes grid power as positive when the system sends power to the grid, but the meter readings are positive on import (verified in `done/add-register-catalogue-with-full-sensor-coverage.md`). | Negate the Meter A power readings (`meter_a_power` and `meter_a_l{1,2,3}_power`) so every grid power reading is positive on export. Meter B is not negated: the HS3 PDF names `4212H` "Photovoltaic Inverter Meter B Power" and meter mode 10 is "grid and PV arrangement", so Meter B measures a separate solar inverter, and `meter_b_power`, `meter_b_l{1,2,3}_power` and `parallel_meter_b_power` read positive while that inverter generates, like `pv_power`. No real Meter B reading exists; the rule assumes Meter B is wired the same way round as Meter A. Corrected 2026-10-22. |
| 12 | 5 | `grid_power`, `grid_l{1,2,3}_power`, `ct_grid_power`, `parallel_grid_power`, `parallel_battery_power`, `battery_port_power`, `average_grid_*_power`, `average_battery_*_power` | Only `battery_power` and the meter sums have a confirmed sign; the sign of 0x40A7 (`grid_power`) is undocumented on both models (`done/add-h2-support-with-shared-device-profiles.md`, "Grid Power Sign"), and the sign is part of the frozen meaning of each key. | Settle the sign of each listed key from a recorded reading of a real inverter where one exists, otherwise from the SAJ protocol documents (`HS3.modbus.protocol.pdf` and `H2-3~6K-S2 single phase communication protocol -2022.12.02-EN.pdf`), record the source in the register notes, and correct any key that is positive on import or on battery charge. The development systems are simulators and are not evidence of inverter behaviour. No key is hidden. Result from the HS3 read recorded in `~/dev/hass/config/packages/saj.md` ("Power sign read (2026-10-22)"): `grid_l1_power`, `grid_l2_power`, `grid_l3_power`, `battery_port_power`, the five-minute average phase grid powers and the five-minute average battery powers already follow the convention; `five_minute_average_grid_power` (`513EH`) is positive on import and is negated. `parallel_grid_power`, `parallel_battery_power` (no parallel system) and the H2 key `ct_grid_power` have no reading and stay as read. |
| 13 | 6 | `pv_direction`, `battery_direction`, `grid_direction`, `output_direction` | The four sensors publish raw numeric codes with no state table, `output_direction` rests only on an undocumented answer, and the signed power sensors already carry the direction. Naming the codes later changes every state value. | Set `exposed=False` on the four definitions. |
| 14 | 6 | `ev_slot_{1..7}_mode` option `pv_mode`, `ev_mode` and `ev_work_mode` option `pv_surplus`, `ev_remote_control` options `shutdown` and `on` | The PV-driven charging mode has two state values (`pv_mode` in `EV_SLOT_MODE_OPTIONS`, `pv_surplus` in the charger mode options), and `EV_REMOTE_CONTROL_OPTIONS` pairs `shutdown` with `on` where the other two-state values are `off` and `on`. | Use `pv_surplus` in `EV_SLOT_MODE_OPTIONS` and `off` and `on` in `EV_REMOTE_CONTROL_OPTIONS`, with the English state labels. |
| 15 | 7 | `backup_reserve_soc`, `battery_charge_limit`, `battery_discharge_limit_off_grid` | `_enabled_by_default` in `saj/catalogue.py` gates `core` on the evidence level, so `backup_reserve_soc` is enabled by default on the HS3 only and the other two keys on the H2 only, because of evidence rather than what users need. | Apply the evidence gate to read entities only, so the three writable state-of-charge settings marked `core` are enabled by default on both models. |
| 16 | 7 | `battery_pack{1..5}_type`, `battery_pack{1..5}_bms_type`, `battery_protocol_active`, `meter_configuration_active`, `application_mode_active`, `drm_hardware_status`, `drm_software_status`, `battery_online_code` | The sensors describe installed hardware or echo a setting in effect, but carry no entity category, unlike the firmware and hardware version sensors, which are `diagnostic`. | Give the listed sensors the `diagnostic` category in `Definition.category`. |
| 17 | 8 | HS3 `parallel_grid_{import,export}_energy_{today,month,year,total}`, `parallel_pv_meter_energy_{today,month,year,total}`, `parallel_meter_b_power` | The 13 keys rest on `responds_unchecked` and name a direction or subject (import against export, a solar meter, meter B of the parallel system) that no document or check supports, and the development systems cannot run a parallel system. | Withdrawn on 2026-10-22: the HS3 PDF documents all 13 registers (`4212H` `parallMeterBPower`, `4265H`-`426BH` `vectorFeedInEnergy` purchased, `426DH`-`4273H` `vectorSellEnergy` sold, `4275H`-`427BH` `PVMeterEnergy`), and the key names match the PDF. The 13 keys stay in the HS3 profile and the power flow card keeps `parallel_meter_b_power`. |
| 18 | 9 | `pv_generation_time_today`, `pv_generation_time_total`, `ems_pv_power_limit`, `ems_pv_power_limit_remove`, `inverter_fault_pv_meter_communication` | Aggregate solar quantities are labelled "Solar" everywhere else (`pv_power` "Solar power", the cards), while the five labels say "PV". Per-string and input labels ("PV1 power", "PV input mode") are a separate, consistent group. | Relabel the five keys "Solar generation time today", "Solar generation time total", "EMS solar power limit", "Remove EMS solar power limit" and "Solar meter communication lost". |
| 19 | 9 | `application_mode_active` | The label "Application mode in effect" differs from the sibling labels such as "Backup reserve state of charge (in effect)". | Relabel `application_mode_active` "Application mode (in effect)". |
| 20 | 9 | 17 entity translations: `sensor` `ethernet_mac_address`, `ev_serial_number`, `battery_pack{1..5}_bms_serial_number`, `battery_pack{1..5}_serial_number`; `text` `ethernet_ip_address`, `ethernet_subnet_mask`, `ethernet_gateway`, `ethernet_dns_primary`, `ethernet_dns_secondary` | The review assumed no platform creates the 17 entities. Home Assistant does create the 17 entities, disabled by default; `private` only masks the values in the diagnostics download. `freeze_surface.py` skipped private registers, so the freeze check missed the 17 entities. | Keep the 17 entities and the English texts (the user chose to keep the entities on 2026-10-22). `freeze_surface.py` includes private registers. |
| 21 | 9 | British spellings in `translations/en.json` and `frontend/src/i18n/en.json` ("Authorisation", "unrecognised", "initialisation", "Synchronise", "customisations", "recognised") | Home Assistant's `en` locale is US English, and the translations roadmap item adds languages from the `en` files. | Rejected by the user on 2026-10-22: English texts and keys use British spelling, always. Every American spelling in the keys, state values and both `en.json` files becomes British. |
| 22 | 12 | Polling group subentry key `sensors` | The stored list holds keys of every readable entity (numbers, switches, selects, binary sensors and times), not only sensors. | Rename the stored key to `keys` (`CONF_SENSORS`, `PollingGroup.data`, `group_cadences`, the form field and the translations). |
| 23 | 12 | Power schedule subentry key `schedule` | The subentry stores the schedule helper's entity ID (`config_flow.py`, `CONF_SCHEDULE: schedule.entity_id`). After the user renames the helper's entity ID, the coordinator listens to an entity ID that no longer exists and the schedule silently stops working. | Store the entity registry ID of the helper and resolve the registry ID to the current entity ID when the coordinator starts and on entity registry updates. |
| 24 | 14 | `freeze_check.py`, versioning rule in `AGENTS.md` | The freeze check compares `VERSION`, `MINOR_VERSION` and the store version as exact values, so the version bump that the versioning rule requires with every stored-form change fails the check (`stored config_flow: VERSION 1 -> 2`). | Compare the three version numbers as non-decreasing (a rise passes, a fall fails) and keep every other value exact. |
| 25 | 15 | Card feature type `saj-local-weekdays` | Every other type ends with the element kind (`-card`, `-badge`); `saj-local-weekdays` does not say the element is a card feature and takes the name a later weekday card would need. | Rename the type and the element tag to `saj-local-weekdays-feature`. |
| 26 | 15 | Card settings `show_clear_groups`, `show_optional`, `kinds` | `show_clear_groups` reads as showing the "Clear fault" action but shows groups without faults; `show_optional` and `kinds` omit the noun the editor labels give ("Show optional equipment", "Slot kinds"). Card settings are stored in users' dashboards. | Rename the settings to `show_groups_without_faults`, `show_optional_equipment` and `slot_kinds`, with the dashboards in `config/dashboards/` and the editor labels. |
| 27 | 15 | Schedule card slot kind value `ev` | The schedule card stores the slot kind `ev`, while the controls card stores the section `ev_charger` and the stored options use the equipment name `ev_charger`. | Use `ev_charger` as the slot kind value (`SlotKind`, `SLOT_KINDS`, label key `option_kind_ev_charger`). |
| 28 | 16 | Card texts "Changes allowed", "Changes off", "Changes are off for this system" | The cards say "changes" where the entity `control_allowed` is labelled "Control allowed" and the option is "Allow control". | Use "Control allowed", "Control off" and "Control is off for this system" in `frontend/src/i18n/en.json`. |

Checked with no change:

- Check 1: every key is snake case, carries no model name and follows the phase (`l1`), string (`pv1`), pack (`battery_pack1`) and equipment patterns; the only keys naming a register are in findings 2 and 3.
- Check 2: every HS3-only and H2-only key was compared by register address, by label and by name; the only pairs with one meaning under two keys are the parallel words in finding 2.
- Check 5: Home Assistant accepts every unit, device class and state class combination except the capacity keys in finding 10; energy counters are `total_increasing`.
- Check 6: every state value of the 40 option sets has an English label; `inverted` is set only on the switches `buzzer` and `ev_ems_charging`.
- Check 7: controls carry the `config` category, the 136 fault binary sensors and `control_allowed` carry `diagnostic`, and the three fault summaries carry no category.
- Check 10: unique ID `<entry id>_<key>`, device identifier `(saj_local, <entry id>)` and entity ID `<domain>.saj_<key>` or `<domain>.saj_<prefix>_<key>` match the decision on unique IDs and the Entity IDs section of `requirements.md`; the prefix is in no unique ID, so a prefix change keeps history.
- Check 11: every config entry `data` and `options` key has the right owner and a final value form.
- Check 13: the power control store key `saj_local.power_control.<entry id>`, version 1, and the keys `targets` (whole watts) and `remembered_modes` (the register code of the mode to restore), each keyed by power function, are final.

## Revisions

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-21 | Draft created from the roadmap item and the investigation of 2026-10-21. |
| 2 | 2026-10-22 | Findings of the review added; card settings frozen; version numbers may rise. |
