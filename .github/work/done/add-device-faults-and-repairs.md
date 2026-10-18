# Add Device Faults And Repairs

## Plan Metadata

- **Revision:** 1
- **Status:** Approved
- **Last revised:** 2026-10-13
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Roadmap item:** "Device faults and Repairs" in the [Roadmap project](https://github.com/orgs/Counterphase-Labs/projects/1)
- **Builds on:** `add-model-neutral-power-control-with-schedules.md`, `add-optional-equipment-detection.md` and the plans they build on. Everything in those plans that is not restated or explicitly replaced here continues to apply.

## Outcome And Scope

A user sees the faults that the inverter, the battery and its packs, and the EV charger report. Each fault appears by name, translated, with history. For the three conditions the user can act on, the user gets a Home Assistant repair:

| Condition | Today | With this plan |
| --- | --- | --- |
| A fault reported by the inverter, the battery, a battery pack or the EV charger | Not read. Only the inverter status shows "Fault" | One problem sensor per piece of equipment and one per named fault, the same keys on every model that reports that fault |
| The device at the address reports a different model, is not a recognised model, or has a different serial | The entry fails to load, or goes unavailable at reconnect, with a translated error | A repair that names the system and what was found. A model or serial change can be adopted from the repair |
| A register the inverter keeps refusing | One warning log and a diagnostics entry. The entity is unavailable | A repair listing the affected entities. Its fix disables them. It clears by itself when they answer again |
| A system that has stopped answering | Entities unavailable, one warning log | A repair after 15 minutes of continuous failure. It clears at the first good read |

New entities, counted from the tables below, all enabled by default:

| Equipment | HS3 | H2 |
| --- | --- | --- |
| Inverter: summary, unrecognised, named faults | 2 + 66 | 2 + 61 |
| Battery: summary, unrecognised, named faults, pack fault and warning | 2 + 30 + 2 (one pack) | 2 + 0 + up to 8 (four packs) |
| EV charger: summary, unrecognised, named faults | 2 + 25 | — |
| Total, everything fitted | 129 | 73 |

Included:

- A `binary_sensor` platform.
- Fault definitions in the library: model-neutral keys. Each model's file states which bits of which registers report each fault.
- The four repair issues, two of them with fix flows. The existing equipment issue moves into the same module.
- Diagnostics, logging, translations, README and `documentation/development.md`.

Not changed: the inverter status (`operating_mode`), the clear-fault buttons, the mock, the browser smoke test.

## Requirements

| Requirement | How it is met |
| --- | --- |
| Clear and detailed errors with good error handling | Every fault is named. Each actionable condition is a repair that says what happened and what to do |
| An abstraction layer across SAJ systems: consistent names, values, formats | A fault has one key and one name on every model. Each model maps its own bits to it. Nothing tests for a model |
| A feature is left out only on a model that lacks the possibility to do it | A fault entity exists on every model that documents a bit for it, and only there |
| Full localisation | Every fault name, issue title, description and fix step is a translation key |
| Automatic detection, with override | A model or serial change can be adopted from the repair. It goes through the same validation as Configure |
| SAJ implemented as a stand-alone library | Fault mapping, decoding, the failing-since time and suspension transitions are library code with no Home Assistant import. Issues and fix flows are integration code |
| Use intelligent modbus access that does not overload the system | The inverter, EV charger and `0x400B` fault words fit in requests the default read already makes. The battery-pack words add one request per poll when a battery is fitted: 2 words on HS3, 8 on H2 (Decision 18) |
| Sensor names must remain stable | No existing key or entity ID changes. New keys are fixed here |

## Decisions

Decisions 1 to 4 were made by the user on 2026-10-12, and Decisions 14, 18, 19, 20 and 21 on 2026-10-13. The others are set by this plan and listed so they can be challenged.

| # | Decision | Outcome |
| --- | --- | --- |
| 1 | How named faults appear | One `binary_sensor` per named fault, enabled by default, in the Diagnostic category, plus one problem sensor per piece of equipment. The default does not depend on evidence level |
| 2 | Wrong-model repair | Fixable. The fix flow adopts the detected model through the same validation and replacement path as Configure |
| 3 | Refused-register repair | Raised when a register is suspended. Fixable: the fix disables the listed entities. Approved on the condition that it clears by itself after a glitch: it clears when every listed register answers again, see Refused Registers |
| 4 | Back-off repair | Raised after 15 minutes of continuous failure. Cleared at the first good read |
| 5 | One key per condition, not per bit | A condition that two registers report becomes one fault, on when either bit is set. For example, grid loss is HS3 `0x4005` bit 23 and `0x4009` bit 23. Field reports show both bits set together on an H2-family unit during grid loss. The raw words stay in diagnostics, so no information is lost |
| 6 | A bit with no documented meaning for the model | It is never given a name borrowed from the other model. It turns on the equipment's "unrecognised fault" entity and is listed in diagnostics with its register and bit. This covers HS3 `0x4007` bits 0–4 and `0x4009` bits 10–11, which are missing from the HS3 document, and every reserved bit |
| 7 | HS3 `0x4005` bit 16 | T-phase undervoltage. Both documents print "SVoltLowFault" again, but the bit sits in the T-phase position, between T-phase overvoltage and the frequency faults |
| 8 | HS3 `0x400B` bits 26–29 | Named from the document's definition column (total voltage matching, system locked, fuse, charging port overvoltage). The name column reads "Reserved", but the definition column defines them |
| 9 | H2 English wording that contradicts the Chinese | The Chinese meaning is used: `0x4007` bit 7 is meter communication lost (English: "DSP and PC lost"); `0x4009` bit 14 is 10-minute average overvoltage (English: "under voltage"); `0x4007` bit 20 is an arc fault (English: "electric error") |
| 10 | H2 `0x400B` | Read. The H2 document lists it as the BMS error message in Chinese and "Reserve" in English, with no bit table. Any set bit turns on `battery_fault_unrecognised` |
| 11 | Battery pack fault and warning words, `0xA002` + 2(n−1) and `0xA003` + 2(n−1) | No bit table exists on either model. Each pack gets a fault and a warning problem sensor that is on when its word is not 0. The code is shown in diagnostics. They follow the existing pack rows: the pack count, the battery equipment, and the evidence of the pack family on each model |
| 12 | EV charger fault byte layout | Undocumented. Table 4.10.1 has eight bytes, Faults[0] to Faults[7], which is 64 bits across the two 32-bit registers. Faults[0]–[3] are taken as the bytes of `0x30AB` from the least significant, and Faults[4]–[7] as `0x30AD`, all reserved. Field reports show both registers at 0 in every charger state tested, so this cannot be checked yet. Catalogued as Documented |
| 13 | Word order of the 32-bit fault registers | The catalogue's existing U32 order. Field reports from an H2-family unit decoded in this order gave the expected names during a grid loss |
| 14 | What a model repair covers | Decided by the user 2026-10-13: all three. A model mismatch, an unsupported device, and a changed serial (identity mismatch). All three mean the device at the address is not the configured one, and all three are fixed in Configure today. Mismatch and serial change can be fixed from the repair. An unsupported device cannot, because no model can be detected |
| 15 | Back-off issue while a model issue is open | Not raised, and an open one is removed when a model issue is raised. A model error on reconnect also backs off, and its cause is already reported. Without the removal, an inverter that is offline for 15 minutes and comes back as a different unit would show "stopped answering" next to the serial-change repair, although it answers, and both would stay until the fix is applied, because the unreachable issue only clears at a good read |
| 16 | Issues across a Home Assistant restart | Not persistent. Each one is raised again when its condition recurs |
| 17 | Who the fix flow's disable is recorded as | The user (`disabled_by` user), so the entities read as disabled by the user and are re-enabled the normal way |
| 18 | The extra request for battery-pack words | Decided by the user 2026-10-13: accepted. The pack words lie in the battery block, which the default read does not otherwise touch. Pack entities stay enabled and count toward `battery_fault`. The HS3 default read with battery and Meter A goes from 9 to 10 requests, the H2 from 6 to 7 |
| 19 | The connection a validation borrows from a loaded installation | Decided by the user 2026-10-13: validation closes it when done. A live test showed that opening the serial-change repair connected the installation's own Modbus client to the other unit, so the next poll skipped its reconnect and identity check, read the other unit's data, and cleared the repair. Closing it makes the next poll reconnect and check identity. This covers Configure too, which shares the validation. The installation then polls straight away, also decided by the user 2026-10-13, so it reconnects and re-checks identity at once instead of staying disconnected until its next poll. Without that, a power-control write in the gap is refused as not reachable and an EMS heartbeat is dropped with a warning. It costs one extra connect and one extra read after each validation |
| 20 | When the unreachable issue appears | Decided by the user 2026-10-13: at the first failed retry after 15 minutes, so 15 to 20 minutes into an outage, because back-off spaces retries up to 5 minutes apart. No timer is added |
| 21 | Logging a repair closed by its fix | Decided by the user 2026-10-13: each fix flow logs one info line when it completes. Home Assistant deletes a fixed issue itself, so the issues module never sees it clear |

## Evidence

Same sources and order of authority as earlier plans: real HS3 readings, field tooling in sustained use and field reports, then the SAJ protocol documents. The mock is not a source.

| Registers | Model | Content | Evidence |
| --- | --- | --- | --- |
| `0x4005`, `0x4007`, `0x4009`, 2 words each | HS3 | Bit tables 4.11.1–4.11.3 | Verified: respond on a real HS3 and read 0 while it runs without a fault. No non-zero reading recorded |
| `0x400B`, 2 words | HS3 | BMS bit table 4.11.4. The HS3's only battery fault source | Documented |
| `0x4005`, `0x4007`, `0x4009` | H2 | Section 4.6 tables, matched to addresses by register order and reserved-bit numbering | Implemented: field tooling decodes them and field reports show named faults during a grid loss |
| `0x400B` | H2 | No table | Documented |
| `0x30AB`, `0x30AD`, 2 words each | HS3 | Table 4.10.1 | Documented. Field reports: 0 in every state |
| `0xA002`–`0xA009` | H2 | Pack 1–4 fault and warning words, no table | Implemented: read by field tooling, 0 in every report |
| `0xA002`, `0xA003` | HS3 | Pack 1 fault and warning | Responds, undocumented, as the rest of the HS3 pack block |
| `0x8F00` | both | Device type. HS3 `0x1610` on three units, H2 `0x005A`/`0x005B` | As in the H2 support plan |

Gaps: no reading exists of any non-zero fault word on an HS3, or of the EV charger or BMS words on any unit with a fault. Bit positions rest on the documents. A wrong position shows as the wrong name or as unrecognised. It is corrected in the model file and changes no key.

## Behaviour

### Fault Entities

Each piece of equipment that reports faults has three kinds of entity:

| Entity | Key | On when | Category | Device class |
| --- | --- | --- | --- | --- |
| Summary | `inverter_fault`, `battery_fault`, `ev_fault` | Any bit of the equipment's fault registers is set, named or not, or any pack word is not 0 | None (primary) | problem |
| Named fault | `inverter_fault_<condition>`, `battery_fault_<condition>`, `ev_fault_<condition>` | Any bit the model maps to it is set | Diagnostic | problem |
| Unrecognised | `inverter_fault_unrecognised`, `battery_fault_unrecognised`, `ev_fault_unrecognised` | A set bit has no named fault on this model | Diagnostic | problem |
| Pack | `battery_pack<n>_fault`, `battery_pack<n>_warning` | The pack's word is not 0 | Diagnostic | problem |

- Inverter entities exist on every system. Battery entities exist only when the battery is fitted, and EV charger entities only when the charger is fitted. Each is tagged with its equipment like every other row.
- A named fault exists only on a model that maps at least one bit to it.
- Every entity is enabled by default (Decision 1). An entity already in the registry keeps its state.
- When the register is unavailable or refused, every entity that depends on it is unavailable. The fault entities never guess.
- Every entity is read on the default cadence, like any other row. The user can put any of them in a polling group.

### Inverter Faults

Sources are `register:bit`. A dash means the model does not report the fault.

| Key | Name | HS3 | H2 |
| --- | --- | --- | --- |
| `inverter_fault_internal_communication` | Internal communication lost | `0x4005:0`, `0x4009:4` | `0x4005:0`, `0x4009:4` |
| `inverter_fault_meter_communication` | Meter communication lost | `0x4005:1`, `0x4007:7` | `0x4005:1`, `0x4007:7` |
| `inverter_fault_display_memory` | Display board memory fault | `0x4005:2` | `0x4005:2` |
| `inverter_fault_display_clock` | Display board clock fault | `0x4005:3` | `0x4005:3` |
| `inverter_fault_bms_device` | BMS device fault | `0x4005:4` | `0x4005:4` |
| `inverter_fault_bms_communication` | BMS communication lost | `0x4005:5` | `0x4005:5` |
| `inverter_fault_ct_device` | CT device fault | `0x4005:6` | — |
| `inverter_fault_afci_communication` | Arc detection board communication lost | `0x4005:7` | — |
| `inverter_fault_slave_communication` | Slave controller communication lost | `0x4005:8` | — |
| `inverter_fault_pv_meter_communication` | PV meter communication lost | `0x4005:9` | — |
| `inverter_fault_ev_charger_communication` | EV charger communication lost | `0x4005:10` | — |
| `inverter_fault_grid_phase_r_overvoltage` | Grid phase R overvoltage | `0x4005:11`, `0x4009:8` | `0x4005:11`, `0x4009:8` |
| `inverter_fault_grid_phase_r_undervoltage` | Grid phase R undervoltage | `0x4005:12`, `0x4009:9` | `0x4005:12`, `0x4009:9` |
| `inverter_fault_grid_phase_s_overvoltage` | Grid phase S overvoltage | `0x4005:13` | `0x4005:13`, `0x4009:10` |
| `inverter_fault_grid_phase_s_undervoltage` | Grid phase S undervoltage | `0x4005:14` | `0x4005:14`, `0x4009:11` |
| `inverter_fault_grid_phase_t_overvoltage` | Grid phase T overvoltage | `0x4005:15`, `0x4009:12` | `0x4005:15`, `0x4009:12` |
| `inverter_fault_grid_phase_t_undervoltage` | Grid phase T undervoltage | `0x4005:16`, `0x4009:13` | `0x4005:16`, `0x4009:13` |
| `inverter_fault_grid_overfrequency` | Grid overfrequency | `0x4005:17`, `0x4009:17` | `0x4005:17`, `0x4009:17` |
| `inverter_fault_grid_underfrequency` | Grid underfrequency | `0x4005:18`, `0x4009:18` | `0x4005:18`, `0x4009:18` |
| `inverter_fault_dcdc_communication` | DC-DC unit communication lost | `0x4005:19` | — |
| `inverter_fault_dcdc_device` | DC-DC unit fault | `0x4005:20` | — |
| `inverter_fault_parallel_communication` | Parallel system communication lost | `0x4005:21`, `0x4009:25` | — |
| `inverter_fault_grid_lost` | Grid lost | `0x4005:23`, `0x4009:23` | `0x4005:23`, `0x4009:23` |
| `inverter_fault_pv_input_mode` | PV input mode fault | `0x4005:24` | `0x4005:24` |
| `inverter_fault_pv_hardware_overcurrent` | PV hardware overcurrent | `0x4005:25`, `0x4007:9` | `0x4005:25`, `0x4007:9` |
| `inverter_fault_pv_overvoltage` | PV overvoltage | `0x4005:26` | `0x4005:26`, `0x4007:3` |
| `inverter_fault_bus_hardware_overvoltage` | DC bus hardware overvoltage | `0x4005:27`, `0x4007:8` | `0x4005:27`, `0x4007:8` |
| `inverter_fault_bus_overvoltage` | DC bus overvoltage | — | `0x4007:0` |
| `inverter_fault_bus_undervoltage` | DC bus undervoltage | — | `0x4007:1` |
| `inverter_fault_grid_phase` | Grid phase fault | — | `0x4007:2` |
| `inverter_fault_islanding` | Islanding | — | `0x4007:4` |
| `inverter_fault_arc_device` | Arc detection device fault | `0x4007:5` | — |
| `inverter_fault_pv_input` | PV input fault | `0x4007:6` | `0x4007:6` |
| `inverter_fault_hardware_overcurrent` | Inverter hardware overcurrent | `0x4007:11` | `0x4007:11` |
| `inverter_fault_neutral_earth_voltage` | Neutral to earth voltage fault | `0x4007:14` | `0x4007:14` |
| `inverter_fault_drm0` | DRM0 fault | `0x4007:15` | `0x4007:15` |
| `inverter_fault_fan_1` | Fan 1 fault | `0x4007:16` | `0x4007:16` |
| `inverter_fault_fan_2` | Fan 2 fault | `0x4007:17` | `0x4007:17` |
| `inverter_fault_fan_3` | Fan 3 fault | `0x4007:18` | `0x4007:18` |
| `inverter_fault_fan_4` | Fan 4 fault | `0x4007:19` | `0x4007:19` |
| `inverter_fault_arc` | Arc fault | `0x4007:20` | `0x4007:20` |
| `inverter_fault_pv_software_overcurrent` | PV software overcurrent | `0x4007:21` | `0x4007:21` |
| `inverter_fault_battery_overvoltage` | Battery port overvoltage | `0x4007:22` | `0x4007:22` |
| `inverter_fault_battery_overcurrent` | Battery port overcurrent | `0x4007:23` | `0x4007:23` |
| `inverter_fault_battery_charge_overvoltage` | Battery charge voltage high | `0x4007:24` | `0x4007:24` |
| `inverter_fault_battery_overload` | Battery port overload | `0x4007:25` | `0x4007:25` |
| `inverter_fault_battery_soft_start` | Battery soft start timeout | `0x4007:26` | `0x4007:26` |
| `inverter_fault_output_overload` | Output overload | `0x4007:27` | `0x4007:27` |
| `inverter_fault_battery_open_circuit` | Battery open circuit | `0x4007:28` | `0x4007:28` |
| `inverter_fault_battery_discharge_undervoltage` | Battery discharge voltage low | `0x4007:29` | `0x4007:29` |
| `inverter_fault_authorisation_expired` | Authorisation expired | `0x4007:30` | `0x4007:30` |
| `inverter_fault_display_communication` | Display board communication lost | `0x4007:31` | `0x4007:31` |
| `inverter_fault_relay` | Relay fault | `0x4009:0` | `0x4009:0` |
| `inverter_fault_controller_memory` | Controller memory fault | `0x4009:1` | `0x4009:1` |
| `inverter_fault_over_temperature` | Over temperature | `0x4009:2` | `0x4009:2` |
| `inverter_fault_under_temperature` | Under temperature | `0x4009:3` | `0x4009:3` |
| `inverter_fault_leakage_current_device` | Leakage current sensor fault | `0x4009:5` | `0x4009:5` |
| `inverter_fault_dc_injection_device` | DC injection sensor fault | `0x4009:6` | `0x4009:6` |
| `inverter_fault_current_sensor` | Current sensor fault | `0x4009:7` | `0x4009:7` |
| `inverter_fault_grid_average_overvoltage` | Grid 10-minute average overvoltage | `0x4009:14` | `0x4009:14` |
| `inverter_fault_off_grid_undervoltage` | Off-grid output undervoltage | `0x4009:15` | `0x4009:15` |
| `inverter_fault_grid_phase_r_dc_voltage` | Grid phase R DC voltage high | `0x4009:20` | `0x4009:20` |
| `inverter_fault_grid_phase_s_dc_voltage` | Grid phase S DC voltage high | `0x4009:21` | `0x4009:21` |
| `inverter_fault_grid_phase_t_dc_voltage` | Grid phase T DC voltage high | `0x4009:22` | `0x4009:22` |
| `inverter_fault_leakage_current` | Leakage current fault | `0x4009:26` | `0x4009:26` |
| `inverter_fault_grid_phase_r_dc_injection` | Grid phase R DC injection high | `0x4009:27` | `0x4009:27` |
| `inverter_fault_grid_phase_s_dc_injection` | Grid phase S DC injection high | `0x4009:28` | `0x4009:28` |
| `inverter_fault_grid_phase_t_dc_injection` | Grid phase T DC injection high | `0x4009:29` | `0x4009:29` |
| `inverter_fault_insulation` | Insulation fault | `0x4009:30` | `0x4009:30` |
| `inverter_fault_bus_imbalance` | DC bus voltage imbalance | `0x4009:31` | `0x4009:31` |

Bits not listed are unrecognised on that model (Decision 6). On HS3 that is `0x4005` bits 22 and 28–31; `0x4007` bits 0–4, 10, 12 and 13; and `0x4009` bits 10, 11, 16, 19 and 24. On H2 it is `0x4005` bits 6–10, 19–22 and 28–31; `0x4007` bits 5, 10, 12 and 13; and `0x4009` bits 16, 19, 24 and 25.

Phase R, S and T are the documents' R/S/T and L1/L2/L3. The names above are the English translations. The keys are what the plan fixes. Battery fault names start with "Battery" and EV charger fault names with "EV charger", as every other battery and EV charger entity name does, so that no two entities of a system share a name.

### Battery Faults

HS3 `0x400B`, table 4.11.4. Rows of the battery equipment.

| Bit | Key | Name |
| --- | --- | --- |
| 0 | `battery_fault_internal_communication` | Battery BMS internal communication lost |
| 1 | `battery_fault_pack_sequence` | Battery pack addressing fault |
| 2 | `battery_fault_discharge_overcurrent` | Battery discharge overcurrent |
| 3 | `battery_fault_charge_overcurrent` | Battery charge overcurrent |
| 4 | `battery_fault_total_undervoltage` | Battery total voltage low |
| 5 | `battery_fault_total_overvoltage` | Battery total voltage high |
| 6 | `battery_fault_cell_undervoltage` | Battery cell undervoltage |
| 7 | `battery_fault_cell_overvoltage` | Battery cell overvoltage |
| 8 | `battery_fault_hardware` | Battery BMS hardware fault |
| 9 | `battery_fault_charge_cold` | Battery too cold to charge |
| 10 | `battery_fault_charge_hot` | Battery too hot to charge |
| 11 | `battery_fault_discharge_cold` | Battery too cold to discharge |
| 12 | `battery_fault_discharge_hot` | Battery too hot to discharge |
| 13 | `battery_fault_relay` | Battery BMS relay fault |
| 14 | `battery_fault_precharge` | Battery pre-charge fault |
| 15 | `battery_fault_insulation` | Battery BMS insulation fault |
| 16 | `battery_fault_bms_incompatible` | Battery BMS manufacturer incompatible |
| 17 | `battery_fault_cell_supplier_incompatible` | Battery cell manufacturer mismatch |
| 18 | `battery_fault_cell_incompatible` | Battery cell mismatch |
| 19 | `battery_fault_voltage_level_mismatch` | Battery voltage level mismatch |
| 20 | `battery_fault_breaker_open` | Battery circuit breaker open |
| 21 | `battery_fault_cell_temperature_difference` | Battery cell temperature difference too large |
| 22 | `battery_fault_cell_voltage_difference_2` | Battery cell voltage difference too large, level 2 |
| 23 | `battery_fault_cell_voltage_difference_1` | Battery cell voltage difference too large, level 1 |
| 24 | `battery_fault_cell_over_temperature` | Battery cell over temperature |
| 25 | `battery_fault_short_circuit` | Battery short circuit |
| 26 | `battery_fault_total_voltage_matching` | Battery total voltage matching failure |
| 27 | `battery_fault_system_locked` | Battery system locked |
| 28 | `battery_fault_fuse` | Battery fuse fault |
| 29 | `battery_fault_charging_port_overvoltage` | Battery charging port overvoltage |

Bits 30 and 31 are unrecognised. On H2 every `0x400B` bit is unrecognised (Decision 10). Packs are as in Decision 11: on H2, packs 1 to 4, limited by the pack count. On HS3, pack 1, as the existing pack rows are.

### EV Charger Faults

HS3 `0x30AB`, table 4.10.1, laid out as Decision 12: bit = 8 × byte + row. Rows of the EV charger equipment.

| Bit | Key | Name |
| --- | --- | --- |
| 0 | `ev_fault_relay_over_temperature` | EV charger relay over temperature |
| 1 | `ev_fault_overload` | EV charger overload |
| 2 | `ev_fault_ac_overvoltage` | EV charger AC overvoltage |
| 3 | `ev_fault_ac_undervoltage` | EV charger AC undervoltage |
| 4 | `ev_fault_ac_overcurrent` | EV charger AC overcurrent |
| 5 | `ev_fault_ac_overfrequency` | EV charger AC overfrequency |
| 6 | `ev_fault_ac_underfrequency` | EV charger AC underfrequency |
| 7 | `ev_fault_dc_residual_current_a` | EV charger DC residual current fault A |
| 8 | `ev_fault_emergency_stop` | EV charger emergency stop |
| 9 | `ev_fault_under_temperature` | EV charger under temperature |
| 10 | `ev_fault_ac_residual_current` | EV charger AC residual current |
| 11 | `ev_fault_input_terminal_over_temperature` | EV charger input terminal over temperature |
| 12 | `ev_fault_bluetooth` | EV charger Bluetooth fault |
| 13 | `ev_fault_dc_residual_current_b` | EV charger DC residual current fault B |
| 14 | `ev_fault_relay` | EV charger relay fault |
| 15 | `ev_fault_grounding` | EV charger grounding fault |
| 16 | `ev_fault_phase_sequence` | EV charger phase sequence fault |
| 17 | `ev_fault_rcd_circuit` | EV charger RCD circuit fault |
| 18 | `ev_fault_rs485_timeout` | EV charger RS485 communication timeout |
| 19 | `ev_fault_supply` | EV charger electricity supply fault |
| 22 | `ev_fault_meter` | EV charger meter fault |
| 23 | `ev_fault_control_pilot` | EV charger control pilot fault (below 2 V) |
| 29 | `ev_fault_connector_lock` | EV charger connector lock fault |
| 30 | `ev_fault_connector_current` | EV charger connector current fault |
| 31 | `ev_fault_dc_residual_current_c` | EV charger DC residual current fault C |

`0x30AB` bits 20, 21 and 24–28, and every bit of `0x30AD`, are unrecognised. The H2 has no EV charger rows.

### Logging

- One warning when a fault turns on, naming the installation and the fault key. One info line when it clears. Nothing is logged on a cycle where nothing changed.
- One warning when an unrecognised bit turns on, naming the register and bit.
- Each repair issue raised: one warning. Cleared: one info line, including when its fix closes it (Decision 21).

### Diagnostics

Diagnostics gain the following:

- Per piece of equipment: the raw fault words in hex, the active fault keys, and the unrecognised bits as `register:bit`.
- The pack fault and warning codes.
- The open repair issues of the installation and, for the refusal issue, its keys.
- The endpoint's failing-since age in seconds.

### Repair: Model

| Issue | Raised when | Fixable | Says |
| --- | --- | --- | --- |
| `model_mismatch` | Identify raises a model mismatch at load or at reconnect | Yes | The installation, the model it is set to, and the model detected |
| `identity_mismatch` | The serial differs from the approved one, at load or at reconnect | Yes | The installation, the approved serial, and the serial found |
| `unsupported_device` | Automatic and the device type is not recognised | No | The installation and the device type. A model can be chosen in Configure, where it is used unverified |

- One issue of these three per installation at a time, severity error. Raising one removes the others, and removes `endpoint_unreachable` (Decision 15).
- Removed at the first load where identify succeeds, and when the installation is removed.
- The fix flow has one confirm step. It shows what was detected (model and serial) and says what adopting it does. It is the same message as Configure's replacement confirmation: identities, entity IDs and history are kept, and device details change. On submit it runs the shared validation that setup and Configure use, with the selection set to Automatic. It saves the result through the same code path that Configure's replacement uses, then reloads the entry.
- A validation error is shown on the confirm form, translated, and nothing is saved. If what the device reports now differs from what the issue named, the form says so and shows the new values. It never saves values the user did not see.
- Allow control and every other option are unchanged by the fix.

### Repair: Refused Registers

| Issue | Raised when | Fixable |
| --- | --- | --- |
| `registers_refused` | A register is suspended (3 consecutive refusals) | Yes |

- One issue per installation, severity warning. It lists the affected entities by their current names. Keys with no entity, such as power-control state keys, are listed by key.
- The issue keeps the set of keys it reports in its issue data, which lasts across reloads but not across a restart.
- A key is added when it is suspended. It is removed when it answers again or is no longer read because its entity was disabled or removed, or its equipment is no longer fitted. When the set is empty the issue is removed.
- **Clearing after a glitch:** a suspended register is re-tested once a day, and every register is re-tested at each reload. The issue therefore clears by itself at the first re-test where every listed register answers, at most a day later, or straight away after a reload. After a reload, a key in the issue that answers is removed even though the new load had not suspended it.
- The fix flow has one confirm step listing the entities. On submit it disables them in the entity registry, as disabled by the user (Decision 17), and the issue is removed. Polling follows the enabled entities, so they stop being read without further action.
- Removed when the installation is removed.

### Repair: Endpoint Unreachable

| Issue | Raised when | Fixable |
| --- | --- | --- |
| `endpoint_unreachable` | The endpoint has failed continuously for 15 minutes | No |

- Per installation, severity error. It names the installation, host and port, and says what to check: power to the inverter and its communication module, the network, and that no other Modbus client holds the connection.
- The endpoint guard records when the current run of failures started. It is cleared by a success, as the failure count is. The check runs at every failed cycle and at every load attempt, including a load ended early by back-off. So the issue is raised even when the entry has never loaded since the outage started. It appears at the first failed retry after 15 minutes, which back-off makes 15 to 20 minutes into the outage (Decision 20).
- Removed at the first successful cycle or load, and when the installation is removed.
- Not raised while a model issue is open for the installation, and removed when a model issue is raised (Decision 15). A good read is not the only way it clears: the device answering with the wrong model or serial also proves it is reachable.

### Existing Equipment Issue

`equipment_not_detected` is unchanged in behaviour. It moves into the shared issues module, so that all issue IDs, creation and removal sit in one place.

## Implementation Design

### SAJ Library

| Module | Change |
| --- | --- |
| `saj/definitions.py` | `EntityKind.BINARY_SENSOR` and a problem quantity. The fault definitions: summary, named and unrecognised per equipment, and the pack fault and warning members of the pack family. Each has explicit equipment |
| `saj/faults.py` (new) | The model-neutral fault model: a fault source as register and bit, a model's fault map from key to sources, and the decoding of the raw words into active keys and unrecognised bits. Pure functions, no I/O |
| `saj/models/hs3.py`, `saj/models/h2.py` | Each model's fault map from the tables above, its fault words, and the pack members. The fault words lie in existing spans |
| `saj/catalogue.py` | Fault rows are placed only where the model maps a source to them. A summary or unrecognised row exists when its equipment has fault words on the model. Checks: every source lies in a fault word of the model, no bit maps to two faults, and every fault word is a placed row |
| `saj/telemetry.py` | The fault values are derived from the decoded words in the same cycle. A dependent fault is unavailable when its word is |
| `saj/guard.py` | `failing_since`, set on the first failure of a run and cleared by `succeeded` |
| `saj/poller.py` | Exposes the keys that answered in a cycle, so the integration can clear refusal-issue keys after a reload |

The fault words are rows read like any other, never entities. They are planned whenever any fault entity of their equipment is enabled.

### Integration

| Module | Change |
| --- | --- |
| `const.py` | `Platform.BINARY_SENSOR`, the issue translation keys, the 15-minute threshold |
| `binary_sensor.py` (new) | The entity class: on, off or unavailable from the derived fault value |
| `issues.py` (new) | Every issue ID of the integration: raise, update and remove for model, refusal, unreachable and equipment issues. `equipment.py` uses it |
| `repairs.py` (new) | `async_create_fix_flow` and the two fix flows. The model fix flow calls the shared validation and the Configure replacement save path. Each fix flow logs its completion |
| `config_flow.py` | The replacement save path and validation, made callable from the fix flow without duplication |
| `__init__.py` | Raises and removes model issues at load. Checks the unreachable threshold at load attempts. Removes every issue of the installation when it is removed |
| `coordinator.py` | Model issue at reconnect. Refusal issue from suspension transitions and answered keys. The unreachable check at failed cycles and removal at success. Fault transition logging |
| `diagnostics.py` | The additions above |
| `translations/en.json` | Every new entity name, the four issues, and both fix flows |

## Verification And Acceptance

Unit tests, each on one module with collaborators replaced, using rows, maps and words built for the test:

- Faults: decoding of each word to active keys; a fault with two sources on from either; unrecognised bits on a model with gaps; all zero; a 32-bit word's high and low halves.
- Catalogue: fault rows placed only where mapped; summary and unrecognised rows per equipment; each rejected map (source outside a fault word, a bit mapped twice); pack members limited by pack count; rows of equipment that is not fitted absent.
- Telemetry: fault values derived in the cycle; unavailable with their word.
- Guard: failing-since set once per run and cleared by success.
- Poller: answered keys reported.
- Binary sensor: on, off and unavailable.
- Issues: each issue raised, updated and removed on each of its conditions; only one model issue at a time; no unreachable issue while a model issue is open, and an open one removed when a model issue is raised; refusal keys added, removed when answered, when no longer read and after a reload; all removed with the installation; the equipment issue unchanged.
- Repairs: model fix confirmed, cancelled, and failing validation with nothing saved; changed device values shown before saving; refusal fix disables the listed entities as the user and removes the issue; each fix logs its completion. Config flow: a validation that borrowed a loaded installation's client leaves it closed (Decision 19).
- Coordinator and setup: each trigger reaches the issues module; fault transitions logged once.
- Diagnostics: the additions.
- Translations: every new row named, issues and fix flows present.

Smoke: the existing per-model smoke test passes unchanged. No new browser test.

Acceptance:

1. An HS3 whose `0x4005` reads with bit 23 set and `0x4009` with bit 23 set shows `binary_sensor.saj_inverter_fault` on and `binary_sensor.saj_inverter_fault_grid_lost` on. No other named fault is on.
2. An HS3 whose `0x4007` reads with bit 2 set shows `inverter_fault` and `inverter_fault_unrecognised` on, and diagnostics list `0x4007:2`. An H2 with the same bit shows `inverter_fault_grid_phase` on.
3. An H2 has no `inverter_fault_ct_device` entity; an HS3 has no `inverter_fault_islanding` entity.
4. A system without a fitted battery has no `battery_fault` entity; one without an EV charger has no `ev_fault` entity.
5. An H2 reporting 2 packs, with pack 2's warning word at 5, shows `battery_pack2_warning` on, `battery_fault` on, and the code 5 in diagnostics. It has no pack 3 or 4 fault entity.
6. Reading the fault entities adds no request to the default read on either model, except the one battery-pack request when a battery is fitted (Decision 18).
7. An HS3 entry set to H2 fails to load with a `model_mismatch` issue naming both models. Confirming the fix saves the HS3 model and reloads the entry. Entity IDs, unique IDs and history are kept, and the issue is gone.
8. A register refused 3 cycles in a row raises `registers_refused` listing its entity. Confirming the fix disables that entity and removes the issue. When the register instead answers at its re-test or after a reload, the issue is removed with no action.
9. An endpoint that stops answering raises `endpoint_unreachable` after 15 minutes and not before. The issue is gone after the first good read.
10. Removing the installation removes every issue it raised.
11. `make ci` passes with the coverage gate.

## Work Sequence

1. `EntityKind.BINARY_SENSOR`, the platform and entity class, translations scaffolding.
2. `saj/faults.py`, the fault definitions, the model maps and the catalogue placement and checks.
3. Derived fault values in telemetry, pack members, logging and diagnostics.
4. `issues.py`, moving the equipment issue into it.
5. Model issues and their fix flow.
6. Refused-register issue and its fix flow, including answered keys after a reload.
7. Failing-since in the guard and the unreachable issue.
8. README and `documentation/development.md`.

Each step ends with `make ci` passing.

## Revisions

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-12 | First draft, with the user's Decisions 1 to 4, 14, 18, 19, 20 and 21. |
