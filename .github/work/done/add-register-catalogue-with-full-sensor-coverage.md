# Add Register Catalogue With Full Sensor Coverage

## Plan Metadata

- **Revision:** 2
- **Status:** Approved
- **Last revised:** 2026-10-09
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Builds on:** `add-configurable-entity-id-prefix.md` and the plans it builds on. Everything in those plans that is not restated or explicitly replaced here continues to apply.

## Outcome And Scope

The SAJ library describes every register it knows in one catalogue, and both the HS3 and the H2 are read from it. An installation goes from six sensors to every register its model is known to have:

| | Registers known | Catalogued | Entities | Enabled by default |
| --- | --- | --- | --- | --- |
| HS3 | 569 | 537 | 594 | 39 |
| H2, single-phase with two PV strings | 356 | 235 | 262 | 36 |
| H2, every phase and string | 356 | 327 | 354 | up to 44 |

Entities outnumber catalogued registers because some registers pack several values and a few entities combine registers. Every register that is not catalogued is listed, with where it goes, under Deferred. Nothing is left out silently.

Settings that the device allows to be written are catalogued as writable and shown with their current value. Nothing in this plan sends a write.

Requirements delivered:

| Requirement | Delivered by |
| --- | --- |
| Wide SAJ support for common household equipment | Every known register of both supported models, not six values |
| An abstraction layer with consistent sensor names, values and formats across SAJ systems | One key per meaning: 274 keys are shared by the two models |
| Target both reading and writing of registries | Every row records whether the device allows it to be written, with its range or options. The write path itself is the next roadmap item |
| Ability to read only certain sensors or exclude certain sensors | A small core set is enabled by default; the rest are created disabled and are not read until enabled |
| Intelligent Modbus access that does not put the system in danger of overload | A full read of the default set is 9 requests on HS3 and 5 on H2, against 29 and 20 under today's planning rule. Registers whose reading has a side effect are never read |
| Convention over configuration, with clear and detailed errors | The polling-group form and Configure show the request load a choice produces, before it is saved |
| Sensor names must remain stable | Keys are fixed here for the whole register set, before release |
| SAJ implemented as a stand-alone library with no Home Assistant code | The catalogue, decoding and read planning live in the library; the integration only maps a row to an entity |
| Users may upgrade, for example from H2 to HS3, with continuity where both have the value | Shared keys keep their entity and history across a model replacement |
| Full localisation | Every new entity name and option is a translation key |

Included:

- The catalogue and its rows for HS3 and H2, as listed in the Register Inventory at the end of this plan.
- Decoding for 16-bit and 32-bit values, text, clocks, times of day, scales, enumerations, invalid markers, packed fields and combined values.
- Read planning for a catalogue of this size, and the refusal handling that goes with it.
- Device shape: phases and PV strings decide which rows a device has.
- `sensor`, `number`, `select`, `switch`, `time` and `text` entities built from catalogue rows.
- The request load shown in the polling-group form and in Configure.

## Deferred

Everything this plan knows about and does not deliver. Each line was also recorded in the roadmap under the item named, so it survives this plan being completed.

| What | Registers | Why not here | Goes to |
| --- | --- | --- | --- |
| Sending any write, and the opt-in that allows it | Every writable row | The write path, its validation and its safety rules are a feature of their own | Roadmap 1, opt-in writes |
| Write-only commands: clear faults, restart, clear history, factory reset, set clock | `0x8015`, `0x801A`–`0x801C`, `0x8020`–`0x8023`, both models | There is nothing to read | Roadmap 1 |
| EMS targets and limits | HS3 `0x8402`–`0x8405`, `0x840F`–`0x8412` | Reading them counts as EMS activity and keeps the inverter in EMS mode. They must never be polled | Roadmap 1 |
| EMS control of the EV charger | HS3 `0x4B46`–`0x4B47` | Same family of control registers; documented only | Roadmap 1 |
| Inverter, BMS, battery-pack and EV-charger fault and warning words | `0x4005`–`0x400C` both models; HS3 `0x30AB`–`0x30AE`; `0xA002`–`0xA003` both models; H2 `0xA004`–`0xA009` | A raw fault word is not a sensor. Each needs its fault table, and the entity it becomes is decided there | Roadmap 4, faults and Repairs |
| Block header words: checksum, length, sequence | HS3 `0x0F00`–`0x0F02`, `0x4B00`–`0x4B02` | No meaning to a user | Roadmap 5, debug dump |
| HS3 words that respond but have no known meaning | `0x3600`–`0x3601`, `0x3661`–`0x3674`, `0x3676`–`0x367F`, `0x3682`–`0x36EF`, `0x8406`–`0x840E` | No name, so no entity is possible | Roadmap 5, debug dump |
| Deciding which optional equipment is present | EV charger, parallel-machine and Meter B rows | The rows are catalogued here, created disabled on every unit. Creating only what exists needs detection | Roadmap 3, equipment detection |
| A friendlier editor for schedules | Weekday masks are shown as a number from 0 to 127 | A weekday picker is a card, not an entity | Roadmap 2, Lovelace cards |
| H2 vector-sum grid counters | H2 `0x4167`–`0x4176` | Read by existing H2 tooling but absent from the H2 document; what they hold on a single-phase unit is unknown | Roadmap 6, H2 document-only registers |
| H2 registers that only its document defines | Listed below | No field implementation reads them and there is no H2 reading to check the document against, and the documents are known to be wrong in places | Roadmap 6 |
| Meter total by the document's `high × 65535 + low` formula | HS3 `0xA066`–`0xA06B` with the phase powers | The formula is unverified. The high words are catalogued as raw rows | Roadmap 6 |
| What `0x40AD` is | Both models | See Grid Power | Open question, recorded in the roadmap |
| Models other than HS3 and H2 | — | Each needs its own model file and evidence | After roadmap 5 |

H2 registers that only its document defines:

| Registers | Document's description |
| --- | --- |
| `0x3632` | Buzzer on or off |
| `0x3635` | Reverse-flow prevention enable |
| `0x3642` | Return frequency hysteresis |
| `0x3652`–`0x3656` | Lead-acid battery voltage thresholds |
| `0x3657`–`0x3659` | Battery discharge and charge current limits, total capacity |
| `0x365D`–`0x365E` | BMS update ID and mode |
| `0x3661`–`0x3663` | Parallel role, number and mode |
| `0x3664`–`0x3665` | Battery charge voltage and average charge voltage |
| `0x3666`–`0x3668` | Battery input mode, PV input mode, off-grid mode enable |
| `0x3669`–`0x366A` | Off-grid voltage and frequency |
| `0x366B` | Motor enable |
| `0x366C`–`0x366D` | Machine model and rated power |
| `0x366E`–`0x366F` | Function flag words |
| `0x3670`–`0x3673` | Maximum DC current component, DC voltage component, insulation limit, leakage current |
| `0x3674` | Grid type |
| `0x3675` | LED switch |
| `0x3676` | Battery forced charge power |
| `0x3677` | Inverter stop |
| `0x3678`–`0x367C` | PV start and shutdown voltage, MPPT voltage high and low, MPPT scan time |
| `0x400D`–`0x400F` | Reserved fault word and error count |
| `0x4017`–`0x4018` | DRM hardware and software status |
| `0x401A`–`0x4021` | Fault-record and settings-change serial numbers, running data |
| `0x4022` | Application mode in effect |
| `0x4070`, `0x40B0`–`0x40BB` | Reserved |
| `0x40BC`–`0x40BE` | PV generation hours today and total |
| `0x8E00`–`0x8E63` | BMS and battery identity for five modules |

## Decisions

| # | Decision | Outcome |
| --- | --- | --- |
| 1 | How a writable setting is shown before writes exist | Approved 2026-10-08: its real control type from the start, refusing changes. The Entity IDs section of `../requirements.md` now covers every entity domain |
| 2 | Which register is `grid_power` | Unchanged: `0x40A7`. `0x40AD` was considered; the real readings do not support it. See Grid Power |
| 3 | Whether a request may read across registers nobody asked for | Decided 2026-10-08, left by the user to the plan author: yes, inside a documented block, within the request size already in field use on each model |
| 4 | Where rows are defined | Approved 2026-10-08: shared key definitions plus one Python data file per model. Model files read from YAML at runtime were considered and not adopted; see Definitions And Model Files |
| 5 | How much is catalogued | Set by the user 2026-10-08: everything known. A register is left out only with an entry under Deferred |

## Rules Replaced From Earlier Plans

| Earlier rule | Now |
| --- | --- |
| A profile lists the measurement keys it supports. | A model's rows are the keys its model file gives an address, limited to the device's shape. |
| Six sensors, single 16-bit words only. | The Register Inventory. |
| Do not read settings as part of polling. | Enabled setting rows are read like any other row. The registers under Never Read stay unread. |
| Entity IDs are `sensor.saj_<key>`. | `<domain>.saj_<key>`, with the same prefix rule. Keys are unique across all domains. |
| Registers that are not contiguous are read in separate requests; gaps are not bridged. | Gaps are bridged inside a readable span. See Read Planning. |
| After a first refusal, every sensor of the refused request is read in a request of its own. | A refused request is halved until the refused row is alone. See Refused Requests. |
| A valid polling-group submission is saved at once. | It is saved from a result step that shows the load. See Request Load In The Forms. |
| Polling-group options are the installation's sensors, by name. | Its catalogue entities of every domain, in register order, each labelled with its block. |
| Unknown operating-mode code is kept in diagnostics. | The same for every enumerated row. |

## Evidence

The mock is not a source for anything in this plan. The register inventory was built from three sources, in this order of authority:

1. **Real readings.** The project's hand-verified readings of a real HS3: each register read on the unit, its value compared with its stated meaning, and controlled tests for the registers that take commands.
2. **Field implementation.** Existing tooling with sustained use on H2 units, and its HS3 register set, which was derived from those readings.
3. **SAJ protocol documents** for the HS3 and for the single-phase H2.

A real reading overrules a document wherever the two disagree, and overrules any earlier plan. The documents are known to be wrong in places.

The inventory was checked against the documents' own address rows: every row of the HS3 document is in the HS3 inventory, and every row of the H2 document is either in the H2 inventory or listed under Deferred.

Each inventory row states its evidence:

| Evidence | Meaning |
| --- | --- |
| Verified | Read on a real HS3 and found to agree with its meaning |
| Responds, unchecked | Answers on a real HS3; the equipment needed to check its value was not fitted (second meter, parallel machine) |
| Responds, undocumented | Answers on a real HS3 and is defined by the H2 document, not the HS3 one |
| Documented | Defined by the model's document; no reading |
| Implemented | Read by existing H2 field tooling |

A row is enabled by default only when it is Verified on HS3 or Implemented on H2.

Corrections the readings make to the documents, already applied in the inventory:

- Power factor is thousandths: a raw 989 is 0.989.
- `0x40A7` is not confirmed as power at the utility connection; see below.
- The HS3 answers a set of registers that only the H2 document defines. They are catalogued for HS3 as Responds, undocumented.
- The battery-pack block `0xA000`–`0xA037` reads as zeros on an HS3 with a battery. It is catalogued and stays disabled.
- An insulation resistance of 32767 kΩ is the register's upper limit: the real resistance is at or above it. It is shown as read.

### Grid Power

Three sources carry a grid figure. What the real HS3 readings establish:

| Source | Established | Not established |
| --- | --- | --- |
| Meter A, sum of the three phase powers `0xA03F`, `0xA045`, `0xA04B` | Positive is import, negative is export. Confirmed by a controlled test: a grid target of 600 W import and then 600 W export each appeared at the meter within about 20 W. | — |
| `0x40A7` | Responds and changes. It read within 1 W of inverter power `0x40A9`, and earlier plans record it following the inverter's AC port. | That it is power at the utility connection. Its sign stays device-defined. |
| `0x40AD` | Responds and changes. Recorded as load power supplied by the grid. | Its sign and whether it is import and export. One sample read 3495 W, which equals load plus battery charge minus PV to the watt, while the Meter A sum in the same listing read −391 W. The two cannot both be the grid figure for one instant, and the listing does not prove they were one instant. |

The H2 document defines `0x40AD` as system grid power, positive buying and negative selling. That is a document claim with no H2 reading behind it, and the HS3 readings do not confirm it.

So nothing is re-pointed:

- `grid_power` stays `0x40A7`, sign device-defined, as the earlier plans set it.
- `0x40AD` is `grid_load_power`, not core.
- `meter_a_power` is the Meter A sum, core on HS3. It is the grid figure to use where a meter is fitted.

Open: a few simultaneous reads of `0x40A0`–`0x40AD` and the three Meter A powers on the HS3, with the system importing and then exporting, would settle what `0x40AD` is. Until that is done this plan claims nothing about it.

## Behaviour

### Keys

The key of every row is in the Register Inventory and is fixed from this plan on. The naming rules:

- Phases are `l1`, `l2`, `l3` for SAJ's R, S and T. On a single-phase unit the one phase is `l1`.
- A family is `<subject>_l<n>_<quantity>`: `grid`, `inverter`, `backup` (the off-grid port), `grid_output` (SAJ's "on-grid output"), `meter_a`, `meter_b`.
- Energy counters are `<subject>_energy_<period>`, the period being `today`, `month`, `year` or `total`.
- SAJ's "sell" is `export` and its "feed-in" is `import`. The registers at `0x40EF` and `0x40F7` count phase R; the system totals on a three-phase unit are the vector-sum counters at `0x4167` and `0x416F`. So `grid_export_energy` and `grid_import_energy` are the vector sums on HS3 and the phase R counters on a single-phase H2, and they are the only keys with a different address per model.
- A value the device reports back as being in effect is `<setting>_active`, beside the setting itself.
- Optional equipment is prefixed: `ev_`, `parallel_`, `average_`.

### Entities

| Row | Entity |
| --- | --- |
| Read-only number, counter or status | `sensor` |
| Read-only text, clock or timestamp | `sensor`, as text or as a timestamp |
| Writable setting with a numeric range | `number` |
| Writable setting with named options | `select` |
| Writable setting that is off or on, and each named bit of a packed register | `switch` |
| Writable time of day (schedule start and end) | `time` |
| Writable text (network addresses) | `text` |

- Entity ID: `<domain>.saj_<key>`, or `<domain>.saj_<prefix>_<key>` with a prefix. Unique ID stays config entry ID plus key.
- Keys are unique across the whole catalogue, whatever the domain, so a prefix change, a polling group and diagnostics all deal in keys.
- Device class, unit and state class follow from the row's quantity. Counters are `total_increasing`. Settings are in the configuration category; versions, commissioning settings, network settings and header-derived values in the diagnostic category.
- A row that is not core is created disabled. A disabled row is not read, as today.
- Display names and option labels are translation keys.

Packed fields: a register that holds several values is read once and each field is its own entity. The schedule registers are the main case: a slot's third register holds its weekdays in the high byte and its power in the low byte, and the two enable registers hold one bit per slot.

Combined values: an entity made from several registers. There are seven: the Meter A total, and the six parallel-system powers whose 32-bit value is split across two non-adjacent words.

### Controls Before Writes Exist

A `number`, `select`, `switch`, `time` or `text` shows the value read from the device. Changing it is refused with one translated error saying that control of this installation is not enabled. No request is sent. The writes plan replaces the refusal with the opt-in check and the write.

Commissioning settings (meter arrangement and address, RS485 addresses and baud rates, battery protocol, network settings) are catalogued with their real control type like every other writable row. Whether the writes plan ever allows them to be changed is for that plan to decide.

### Values

| Case | State |
| --- | --- |
| A row's invalid marker (`0xFFFF` for versions, zero for identity text) | Unknown |
| `battery_soc` outside 0–100 %, as today | Unknown |
| An enumerated row with a code that has no name | Unknown, and the code is reported in diagnostics under the row's key |
| A `number` whose value is outside its documented range | The value as read. The range limits what can be set, not what is shown |
| A combined value with any source missing or refused | Unknown |

### Device Shape

| Device | Phases | PV strings |
| --- | --- | --- |
| HS3, type `0x1610` | 3 | 2 |
| H2, type `0x005A` | 1 | 2 |
| H2, type `0x005B` | 1 | 3 |
| Any type selected by override and not recognised | The model's maximum: 3 phases; 2 strings on HS3, 4 on H2 | |

A recognised device gets only the rows that fit its shape. A device running on a model override gets every row of the model, because its shape is unknown; rows beyond one phase and two strings are created disabled whatever their core marking.

### Never Read

Some registers must not be polled, whatever is enabled:

- **EMS targets and limits**, HS3 `0x8402`–`0x8405` and `0x840F`–`0x8412`. On a real HS3, access to these registers counts as EMS activity: it restarts the EMS timeout and keeps the inverter under external control. They are outside every readable span and have no row.
- **Write-only commands**, `0x8015`–`0x8023`.
- **`0x8F02` on HS3.** The earlier plans' rule stands.

The EMS enable register `0x8400` and its timeout `0x8401` are catalogued, disabled, as their own two-word span.

### Read Planning

A model declares its readable spans: address ranges that its document defines as one block. Only the HS3 settings span has been read end to end on a real unit; a gap word that a device refuses is found and fenced off by the rules in Refused Requests.

| Span | HS3 | H2 |
| --- | --- | --- |
| Network settings | `0x0F03`–`0x0F2F` | — |
| EV charger data | `0x3024`–`0x30BB` | — |
| Settings | `0x3600`–`0x36EF` | `0x3604`–`0x367C` |
| Realtime and energy | `0x4000`–`0x4176` | `0x4000`–`0x4166` |
| Parallel machines | `0x4200`–`0x427C` | — |
| EV charger settings | `0x4B03`–`0x4B45` | — |
| Five-minute averages | `0x513E`–`0x51BE` | — |
| EMS enable | `0x8400`–`0x8401` | — |
| Identity and versions | `0x8F0D`–`0x8F1C` | `0x8F00`–`0x8F1C` |
| Battery packs | `0xA000`–`0xA037` | `0xA000`–`0xA037` |
| Meters | `0xA03C`–`0xA077` | `0xA03C`–`0xA065` |

A model also declares its largest request: **32 words on HS3 and 56 on H2**. These are the largest requests with sustained field use on each model. Whether a larger request is harmless is unknown, so none is sent.

Rules:

- Two needed registers share a request when they are in the same span and the request stays within the model's largest request. The words between them are read and discarded.
- A request never leaves its span. An HS3 refuses a request that runs past the end of its settings block.
- A multi-word row is never split across requests.
- A request never crosses a break; see Refused Requests.
- A disabled row is never the reason for a request. Its word is read only as a gap word between two rows that are needed.
- Identity is read as today, not through the catalogue.

Why bridge: with gaps unbridged, disabling rows makes the load worse, not better, because every disabled row cuts a request in two. Requests for one full read:

| What is enabled | HS3, unbridged | HS3, bridged | H2, unbridged | H2, bridged |
| --- | --- | --- | --- | --- |
| Core rows | 29 | 9 | 20 | 5 |
| Every row | 45 | 36 | 25 | 11 |
| A fast group of load, PV, battery and grid power | 2 | 1 | 2 | 1 |

At the 60-second default, the core set and a 10-second power group together are 15 requests a minute on HS3, inside the budget of 40. Unbridged they are 41, over it. With every HS3 row enabled the installation is at 36 a minute with no fast group; the forms say so before it is saved.

Field practice this follows:

- H2 is read in fixed blocks of 8 to 56 words that cover the whole map, gap and reserved words included, once a minute.
- HS3 is read in strictly contiguous requests of at most 32 words for the full scan, and in two fixed bridged blocks for fast values: `0x4095`–`0x40AD` and `0x406E`–`0x4076`, with the gap words ignored.

The budget still counts requests.

### Refused Requests

This replaces the per-sensor isolation of the earlier plan, which would cost one request per row after a single refusal of a 56-word request.

| Step | Behaviour |
| --- | --- |
| A request holding several rows is refused | Its rows are unavailable. From the next cycle those rows are read as two requests, split at the row boundary nearest the middle. Neither half is merged with other rows. |
| A half succeeds | Its rows are available and return to normal planning. |
| A half is refused | It is split again, until a request holds one row. |
| Both halves of a split succeed | The fault lay in the gap between them. The gap is marked as a break and no request bridges it again until the next load. |
| A request holding one row is refused | Counted against that row. The third consecutive one suspends the row, as today. A suspended row is also a break. |

A refused region costs a few extra requests a cycle while it is being narrowed: two for the halves, and for a cycle or two one more while rows that have cleared wait to rejoin their neighbours. Re-tests, warnings, the 24-hour period and the rule that refusals are not failed cycles are unchanged.

### Setup Validation

Unchanged: setup and Configure require the identity and the six original keys to read. No other row is required, so a register one unit lacks cannot block setup.

### Request Load In The Forms

With six sensors the cost of a polling group was obvious. With this catalogue it is not, so the forms state it.

The figure is the installation's planned load: the steady-state requests per minute of its cadences, which the library already computes at load and diagnostics already report, against the budget of 40. It is computed, never measured: showing it sends nothing to the device.

- Only enabled rows count. A disabled row in a group costs nothing until it is enabled.
- Each cadence is planned on its own, so the figure is an upper bound: on a tick where two cadences coincide their rows share requests.
- The cost is a property of the whole selection, not of a row. Four rows in one block cost one request; two rows in different blocks cost two. No per-row cost is shown, because it would not add up.

Polling-group form, add and edit:

| Where | Shows |
| --- | --- |
| Form description | The current load, for example "15 of 40 requests per minute". |
| Sensor options | The installation's entities in register order, each labelled with its block (realtime, energy, settings, battery, meters, versions), so entities that can share a request sit together. |
| Result step, after a valid submission | The requests one read of the group takes, the load before, and the load with the group saved. Two choices: save, or change the selection, which returns to the form with the submission kept. |
| Result step, when the load with the group is over the budget | The same, plus a statement that cadences will run slower than configured. Saving is still allowed, as the earlier plan allows an over-budget configuration to load with a warning. |

Nothing is saved until the result step's save choice. The form's existing errors are unchanged and are shown on the form, before the result step.

Configure:

| Where | Shows |
| --- | --- |
| Form description | The current load. |
| A new step in the existing confirmation chain, only when a changed default interval puts the load over the budget | The load before and after, and the same statement. It comes after the model, replacement and prefix confirmations. |

Enabling an entity in Home Assistant cannot be intercepted by a form. The existing warning at load and the figure in diagnostics cover that case.

The forms work while the installation is not loaded, as today. The load depends on the device's rows and addresses, so the device type that setup, Configure or a replacement last verified is stored with the entry.

### Polling Groups And Prefix

- A polling group may hold any catalogue entity of the installation, in any domain, enabled or not. A disabled entity is listed marked as disabled, so groups can be arranged before entities are enabled; it costs nothing until it is enabled.
- The prefix rule that rejects a prefix when a key starts with `<prefix>_` now checks every catalogue key. Words such as `grid`, `battery`, `meter`, `inverter`, `backup`, `pv1`, `load`, `ev`, `parallel` and `average` are therefore refused as prefixes.
- A prefix change renames the installation's entities in every domain.

### Privacy

Diagnostics never include the values of the serial numbers, the product code, the MAC address or the network addresses, whether of the inverter or of the EV charger.

## Implementation Design

### SAJ Library

No Home Assistant import, and no model-specific branch: everything model-specific is data.

#### Definitions And Model Files

A row is defined in two places, so that what a key means is written once and where a model keeps it is written per model.

| Part | Holds | Written |
| --- | --- | --- |
| Definition | Key, quantity, encoding, scale, invalid marker, access (read-only or writable), range or options, core marking, the phase or string it needs, the field it takes from a packed register, or the rows it combines | Once, for all models |
| Model file | The model's name, its device types with the shape of each, its readable spans, its largest request, whether it is hand-verified, the address of every key the model has, and the evidence for each | Once per model |

- A model has a row when its file gives the key an address. There is no separate list of a model's keys.
- A model file may replace a definition's range, options, encoding or scale for that model. It may never replace the quantity: a key means the same thing everywhere.
- A model file is data only. It contains no conditions and no behaviour.
- Row families are generated in both parts from the same base, stride and suffix tables: the definitions get their keys from them and a model file gets its addresses from them. No family is written out row by row.
- Adding a model is adding one file. A firmware variant is a model built from another model's data with some entries replaced; none is shipped by this plan.

The files are Python, not YAML read at runtime. As Python they are checked by the type checker and the catalogue's own validation before release, families are a loop instead of hundreds of rows or a template language, and nothing is read from disk while Home Assistant runs. A data file would still not let a sensor be added without code, because every entity needs a translated name. Because model files hold data only, moving them to a data format later is a mechanical change.

#### Modules

| Module | Responsibility |
| --- | --- |
| `saj/codec.py` | New. Encodings (unsigned and signed 16-bit and 32-bit, text, clock, Unix time, time of day, MAC and address text), scale, invalid markers, enumerations and bit fields. Decodes the words of one row to a value. |
| `saj/definitions.py` | New. `Definition` and the shared definitions, with the family generators. |
| `saj/models/hs3.py`, `saj/models/h2.py` | New. One `Profile` each: the model file described above. |
| `saj/profiles.py` | `Profile` loses its key set and gains its address map, readable spans, largest request and shape per device type. Keeps the list of profiles and the resolution of a device type and model selection to a profile. |
| `saj/catalogue.py` | New. `Register`: a definition joined with one profile's address and replacements. `Catalogue`: the registers of one profile, validated on construction, and the registers of a device: those that fit its shape. |
| `saj/telemetry.py` | Read planning over rows of any width, with spans, the largest request, bridging and breaks. Decoding goes through the codec. A packed field is planned as its register; a combined value as its source rows. |
| `saj/health.py` | Tracks refused requests being narrowed and the breaks found, beside the per-row refusal counts it has today. |
| `saj/poller.py` | Passes the pending splits and breaks into planning and feeds request outcomes back. Its cycle, deadline and result shape are unchanged. |
| `saj/load.py` | New. The planned load of a device as a function of its rows, the enabled keys and the cadences, with no poller or connection needed. The poller's own figure comes from the same function. It is its own module because `saj/budget.py` is imported by the client, which planning depends on. |

`Catalogue` rejects, on construction: an address for a key that has no definition, a duplicate key, two rows overlapping in address unless they are fields of one packed register, a row outside every span of the profile, a combined row whose sources the profile lacks, and a writable row without a range, options or a writable encoding. Every shipped profile's catalogue is built at import, so a bad row cannot reach a release. Because a row must lie inside a span, a Never Read register cannot be catalogued by mistake.

Quantity is a library enumeration (power, voltage, energy and so on). It is what lets the integration choose a unit and device class without a second per-key table.

### Integration

- `entity.py`: new. One base for all six platforms: entity ID, unique ID, device info, availability and the rule that state is written only in a cycle that read the row. This is today's `SajSensor` behaviour, moved.
- `sensor.py`, `number.py`, `select.py`, `switch.py`, `time.py`, `text.py`: thin. Each takes the device's rows for its entity type. The quantity-to-Home-Assistant mapping lives in one place. Every control raises the not-enabled error on any change.
- `const.py`: the ID helpers take the domain. `PLATFORMS` lists the six.
- `coordinator.py`: enabled keys come from the registry entries of all six platforms.
- `config_flow.py`: the polling-group form and the prefix checks and rename cover every domain. The group flow gains the result step, as a menu of save and change selection; Configure gains the over-budget confirmation in `_async_advance`. Both take the load from the library function with the stored device type, the registry's enabled keys and the entry's cadences, so each is tested with plain inputs. Entry data gains the verified device type.
- `diagnostics.py`: enabled keys, unknown enumeration codes by key, breaks found, and requests being narrowed, with the redactions under Privacy.
- `translations/`: names for every row, option labels, block labels, the load texts of both forms, and the not-enabled error.

### Modbus Mock

Not changed, and not consulted. The mock follows documented device behaviour and is not adjusted to suit the catalogue.

### What Is Removed

- `MEASUREMENTS` and the single-word `Measurement` in `saj/telemetry.py`.
- `Profile.measurement_keys` and the profile definitions inside `saj/profiles.py`, which move to the model files.
- The per-key description table in `sensor.py`.
- Per-key isolation after a first refusal.

## Verification And Acceptance

Unit tests, each on one module with collaborators replaced. Tests use rows built for the test, not the shipped table:

- Codec: each encoding, sign handling, word order, scale, each invalid marker, a named and an unnamed enumeration code, a bit field, text with padding, a clock and a time of day.
- Definitions: a family generating its keys, and the same family generating a model's addresses.
- Catalogue: each construction rejection; a model's replacement of a range, options, encoding and scale; rows of a device for each shape, including the override case.
- Planning: bridging inside a span; no bridging across spans or beyond the model's largest request; a multi-word row kept whole at a request boundary; breaks honoured; disabled rows read only as gap words; several fields of one packed register costing one read; a combined value reading its sources.
- Health: a refused request halves; a succeeding half returns to planning; both halves succeeding records a break; a single-row refusal counts toward suspension; a suspended row is a break.
- Poller: splits and breaks carried from one cycle to the next; a re-test still joins the next cycle.
- Budget: planned load for one cadence, several cadences, disabled rows and rows in different blocks.
- Entities: the entity type chosen for a row; core and non-core enabled state; unknown for invalid and unnamed values; each control type refusing a change without a request being sent.
- Config flow: the result step's figures for a new and an edited group; change selection returning to the form with the submission kept; nothing saved before the save choice; the over-budget text; Configure's extra step shown only when a changed interval goes over the budget; both working for an entry that is not loaded.
- Config flow: a group holding entities of several domains; a prefix that shadows a catalogue key; a prefix change renaming entities of every domain.
- Diagnostics: unknown codes, breaks and narrowing reported; each private value absent.

Smoke, against the mock, one per model: the installation loads and a core sensor, an energy counter and a setting each have a value.

Acceptance:

- A new HS3 installation has 39 entities enabled and the rest of its 594 present but disabled, and its full read is nine requests, none over 32 words.
- A new single-phase, two-string H2 installation has 36 of its 262 enabled, and its full read is five requests, none over 56 words.
- Every key in the Register Inventory that is not marked Deferred exists as an entity of the stated type on a device of that model and shape.
- No request is ever sent to an address under Never Read, with every entity enabled.
- Enabling a disabled row adds it to the next cycle with no reload beyond Home Assistant's own.
- Replacing an H2 with an HS3 keeps the entity and history of every key both models have.
- Adding a 10-second group of load, PV, battery and grid power to a default HS3 installation shows one request per read and a load of 15 of 40 before it is saved.
- `make ci` passes with the coverage gate.

## Work Sequence

1. Codec, definitions, the two model files and the catalogue, with the six existing rows only, replacing `MEASUREMENTS`. Behaviour unchanged.
2. Read planning with spans, bridging and breaks; refusal narrowing.
3. Device shape and the full row set for both models, including packed fields and combined values.
4. Entity base and the six platforms; translations.
5. Config flow across domains, diagnostics, documentation.
6. Request load in the polling-group form and Configure.

## Register Inventory

This is the contract for the catalogue. One line per register of each model, in address order. A line either gives the key and entity the register becomes, or says Deferred and why; the destinations are in the Deferred section.

- Addresses are wire addresses. Multi-word values are most significant word first.
- Scale is what the raw value is multiplied by. A blank unit means the value has none.
- Core rows are enabled by default; every other row is created disabled.
- A `number`'s range is in brackets, in the unit shown.
- The enumerations and option lists of `select` and enumerated `sensor` rows follow the tables.

### HS3 Registers

**Ethernet** — 11 registers.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0x0F00` | 1 | U16 | | | Verified | — | Deferred — Debug dump: block header word | |
| `0x0F01` | 1 | U16 | | | Verified | — | Deferred — Debug dump: block header word | |
| `0x0F02` | 1 | U16 | | | Verified | — | Deferred — Debug dump: block header word | |
| `0x0F03` | 1 | U16 | 0.001 |  | Verified | `ethernet_protocol_version` | sensor | Disabled |
| `0x0F04` | 3 | MAC | 1 |  | Verified | `ethernet_mac_address` | sensor (text) | Disabled |
| `0x0F07` | 1 | U16 | 1 |  | Verified | `ethernet_mode` | select | Disabled |
| `0x0F08` | 8 | IPv4 text | 1 |  | Verified | `ethernet_ip_address` | text | Disabled |
| `0x0F10` | 8 | IPv4 text | 1 |  | Verified | `ethernet_subnet_mask` | text | Disabled |
| `0x0F18` | 8 | IPv4 text | 1 |  | Verified | `ethernet_gateway` | text | Disabled |
| `0x0F20` | 8 | IPv4 text | 1 |  | Verified | `ethernet_dns_primary` | text | Disabled |
| `0x0F28` | 8 | IPv4 text | 1 |  | Verified | `ethernet_dns_secondary` | text | Disabled |

**EV charger data** — 27 registers. Optional equipment: EV charger. Every row is created disabled.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0x3024` | 16 | Text | 1 |  | Documented | `ev_serial_number` | sensor (text) | Disabled |
| `0x3034` | 8 | Text | 1 |  | Documented | `ev_model` | sensor (text) | Disabled |
| `0x303C` | 5 | Text | 1 |  | Documented | `ev_software_version` | sensor (text) | Disabled |
| `0x3041` | 5 | Text | 1 |  | Documented | `ev_hardware_version` | sensor (text) | Disabled |
| `0x3046` | 1 | U16 | 1 |  | Documented | `ev_phase_count` | sensor | Disabled |
| `0x3047` | 1 | U16 | 1 | W | Documented | `ev_minimum_power` | sensor | Disabled |
| `0x3048` | 2 | U32 | 1 | W | Documented | `ev_maximum_power` | sensor | Disabled |
| `0x309C` | 1 | U16 | 1 |  | Documented | `ev_work_mode` | sensor (enum) | Disabled |
| `0x309D` | 1 | U16 | 1 |  | Documented | `ev_status` | sensor (enum) | Disabled |
| `0x309E` | 1 | U16 | 0.1 | V | Documented | `ev_l1_voltage` | sensor | Disabled |
| `0x309F` | 1 | U16 | 0.1 | A | Documented | `ev_l1_current` | sensor | Disabled |
| `0x30A0` | 1 | U16 | 0.1 | V | Documented | `ev_l2_voltage` | sensor | Disabled |
| `0x30A1` | 1 | U16 | 0.1 | A | Documented | `ev_l2_current` | sensor | Disabled |
| `0x30A2` | 1 | U16 | 0.1 | V | Documented | `ev_l3_voltage` | sensor | Disabled |
| `0x30A3` | 1 | U16 | 0.1 | A | Documented | `ev_l3_current` | sensor | Disabled |
| `0x30A4` | 2 | U32 | 1 | W | Documented | `ev_power` | sensor | Disabled |
| `0x30A6` | 1 | U16 | 1 | min | Documented | `ev_charge_duration` | sensor | Disabled |
| `0x30A7` | 2 | U32 | 0.001 | kWh | Documented | `ev_session_energy` | sensor | Disabled |
| `0x30A9` | 2 | U32 | 0.001 | kWh | Documented | `ev_total_energy` | sensor | Disabled |
| `0x30AB` | 2 | U32 | | | Documented | — | Deferred — Faults: needs its fault table | |
| `0x30AD` | 2 | U32 | | | Documented | — | Deferred — Faults: needs its fault table | |
| `0x30AF` | 1 | U16 | 1 | V | Documented | `ev_control_pilot_voltage` | sensor | Disabled |
| `0x30B0` | 1 | U16 | 0.1 | % | Documented | `ev_duty_cycle` | sensor | Disabled |
| `0x30B6` | 1 | U16 | 1 |  | Documented | `ev_remote_control` | sensor (enum) | Disabled |
| `0x30B7` | 1 | U16 | 0.1 | A | Documented | `ev_current_setpoint` | sensor | Disabled |
| `0x30B8` | 2 | Unix time | 1 |  | Documented | `ev_session_start` | sensor (time) | Disabled |
| `0x30BA` | 2 | Unix time | 1 |  | Documented | `ev_session_end` | sensor (time) | Disabled |

**Settings** — 74 registers.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0x3602` | 1 | U16 | 1 |  | Verified | `settings_sequence` | number (0–65535) | Disabled |
| `0x3603` | 1 | U16 | 1 |  | Verified | `settings_protocol_version` | sensor | Disabled |
| `0x3604` | 1 | Bits | | | Verified | — | Packed fields, see below | |
| `0x3605` | 1 | Bits | | | Verified | — | Packed fields, see below | |
| `0x3606` | 1 | hh:mm | 1 |  | Verified | `charge_slot_1_start` | time | Disabled |
| `0x3607` | 1 | hh:mm | 1 |  | Documented | `charge_slot_1_end` | time | Disabled |
| `0x3608` | 1 | Bits | | | Documented | — | Packed fields, see below | |
| `0x3609` | 1 | hh:mm | 1 |  | Documented | `charge_slot_2_start` | time | Disabled |
| `0x360A` | 1 | hh:mm | 1 |  | Documented | `charge_slot_2_end` | time | Disabled |
| `0x360B` | 1 | Bits | | | Documented | — | Packed fields, see below | |
| `0x360C` | 1 | hh:mm | 1 |  | Documented | `charge_slot_3_start` | time | Disabled |
| `0x360D` | 1 | hh:mm | 1 |  | Documented | `charge_slot_3_end` | time | Disabled |
| `0x360E` | 1 | Bits | | | Documented | — | Packed fields, see below | |
| `0x360F` | 1 | hh:mm | 1 |  | Documented | `charge_slot_4_start` | time | Disabled |
| `0x3610` | 1 | hh:mm | 1 |  | Documented | `charge_slot_4_end` | time | Disabled |
| `0x3611` | 1 | Bits | | | Documented | — | Packed fields, see below | |
| `0x3612` | 1 | hh:mm | 1 |  | Documented | `charge_slot_5_start` | time | Disabled |
| `0x3613` | 1 | hh:mm | 1 |  | Documented | `charge_slot_5_end` | time | Disabled |
| `0x3614` | 1 | Bits | | | Documented | — | Packed fields, see below | |
| `0x3615` | 1 | hh:mm | 1 |  | Documented | `charge_slot_6_start` | time | Disabled |
| `0x3616` | 1 | hh:mm | 1 |  | Documented | `charge_slot_6_end` | time | Disabled |
| `0x3617` | 1 | Bits | | | Documented | — | Packed fields, see below | |
| `0x3618` | 1 | hh:mm | 1 |  | Documented | `charge_slot_7_start` | time | Disabled |
| `0x3619` | 1 | hh:mm | 1 |  | Documented | `charge_slot_7_end` | time | Disabled |
| `0x361A` | 1 | Bits | | | Documented | — | Packed fields, see below | |
| `0x361B` | 1 | hh:mm | 1 |  | Documented | `discharge_slot_1_start` | time | Disabled |
| `0x361C` | 1 | hh:mm | 1 |  | Documented | `discharge_slot_1_end` | time | Disabled |
| `0x361D` | 1 | Bits | | | Documented | — | Packed fields, see below | |
| `0x361E` | 1 | hh:mm | 1 |  | Documented | `discharge_slot_2_start` | time | Disabled |
| `0x361F` | 1 | hh:mm | 1 |  | Documented | `discharge_slot_2_end` | time | Disabled |
| `0x3620` | 1 | Bits | | | Documented | — | Packed fields, see below | |
| `0x3621` | 1 | hh:mm | 1 |  | Documented | `discharge_slot_3_start` | time | Disabled |
| `0x3622` | 1 | hh:mm | 1 |  | Documented | `discharge_slot_3_end` | time | Disabled |
| `0x3623` | 1 | Bits | | | Documented | — | Packed fields, see below | |
| `0x3624` | 1 | hh:mm | 1 |  | Documented | `discharge_slot_4_start` | time | Disabled |
| `0x3625` | 1 | hh:mm | 1 |  | Documented | `discharge_slot_4_end` | time | Disabled |
| `0x3626` | 1 | Bits | | | Documented | — | Packed fields, see below | |
| `0x3627` | 1 | hh:mm | 1 |  | Documented | `discharge_slot_5_start` | time | Disabled |
| `0x3628` | 1 | hh:mm | 1 |  | Documented | `discharge_slot_5_end` | time | Disabled |
| `0x3629` | 1 | Bits | | | Documented | — | Packed fields, see below | |
| `0x362A` | 1 | hh:mm | 1 |  | Documented | `discharge_slot_6_start` | time | Disabled |
| `0x362B` | 1 | hh:mm | 1 |  | Documented | `discharge_slot_6_end` | time | Disabled |
| `0x362C` | 1 | Bits | | | Documented | — | Packed fields, see below | |
| `0x362D` | 1 | hh:mm | 1 |  | Documented | `discharge_slot_7_start` | time | Disabled |
| `0x362E` | 1 | hh:mm | 1 |  | Documented | `discharge_slot_7_end` | time | Disabled |
| `0x362F` | 1 | Bits | | | Documented | — | Packed fields, see below | |
| `0x3630` | 1 | U16 | 1 |  | Verified | `meter_configuration` | select | Disabled |
| `0x3631` | 1 | U16 | 1 |  | Verified | `meter_address` | number (1–255) | Disabled |
| `0x3633` | 1 | U16 | 1 |  | Verified | `rs485_address` | number (1–127) | Disabled |
| `0x3634` | 1 | U16 | 1 |  | Verified | `rs485_baud_rate` | number (0–65535) | Disabled |
| `0x3636` | 1 | U16 | 1 |  | Responds, undocumented | `passive_mode` | number (0–2) | Disabled |
| `0x3637` | 1 | U16 | 0.1 | % | Responds, undocumented | `passive_grid_charge_power` | number (0–110) | Disabled |
| `0x3638` | 1 | U16 | 0.1 | % | Responds, undocumented | `passive_grid_discharge_power` | number (0–110) | Disabled |
| `0x3639` | 1 | U16 | 0.1 | % | Verified | `passive_battery_charge_power` | number (0–110) | Disabled |
| `0x363A` | 1 | U16 | 0.1 | % | Responds, undocumented | `passive_battery_discharge_power` | number (0–110) | Disabled |
| `0x363B` | 1 | U16 | 1 |  | Verified | `battery_protocol` | select | Disabled |
| `0x3643` | 1 | U16 | 1 |  | Verified | `battery_auto_wake` | switch | Disabled |
| `0x3644` | 1 | U16 | 1 | % | Verified | `battery_discharge_limit_on_grid` | number (0–100) | Core |
| `0x3645` | 1 | U16 | 1 | % | Responds, undocumented | `battery_discharge_limit_off_grid` | number (0–100) | Disabled |
| `0x3646` | 1 | U16 | 1 | % | Documented | `battery_charge_limit` | number (0–100) | Disabled |
| `0x3647` | 1 | U16 | 1 |  | Verified | `application_mode` | select | Core |
| `0x364D` | 1 | U16 | 0.1 | % | Responds, undocumented | `battery_charge_power_limit` | number (0–110) | Disabled |
| `0x364E` | 1 | U16 | 0.1 | % | Responds, undocumented | `battery_discharge_power_limit` | number (0–110) | Disabled |
| `0x364F` | 1 | U16 | 0.1 | % | Responds, undocumented | `grid_import_power_limit` | number (0–110) | Disabled |
| `0x3650` | 1 | U16 | 0.1 | % | Responds, undocumented | `grid_export_power_limit` | number (0–110) | Disabled |
| `0x3651` | 1 | U16 | 1 | % | Verified | `backup_reserve_soc` | number (0–100) | Core |
| `0x365A` | 1 | U16 | 0.1 | % | Verified | `export_limit_power` | number (0–100) | Disabled |
| `0x365B` | 1 | U16 | 0.01 | A | Verified | `export_limit_current` | number (0–3) | Disabled |
| `0x365C` | 1 | U16 | 1 |  | Verified | `export_limit_mode` | select | Disabled |
| `0x365F` | 1 | U16 | 1 |  | Verified | `time_of_use_idle_mode` | select | Disabled |
| `0x3660` | 1 | U16 | 1 |  | Responds, undocumented | `time_of_use_grid_discharge` | switch | Disabled |
| `0x3675` | 1 | U16 | 1 |  | Verified | `led_mode` | select | Disabled |
| `0x3680` | 1 | U16 | 1 |  | Verified | `rs485_slave_address` | number (1–1) | Disabled |
| `0x3681` | 1 | U16 | 1 |  | Verified | `rs485_slave_baud_rate` | select | Disabled |

**Realtime** — 108 registers.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0x4000` | 4 | Clock | 1 |  | Verified | `inverter_clock` | sensor (time) | Disabled |
| `0x4004` | 1 | U16 | 1 |  | Verified | `operating_mode` | sensor | Core |
| `0x4005` | 2 | U32 | | | Verified | — | Deferred — Faults: needs its fault table | |
| `0x4007` | 2 | U32 | | | Verified | — | Deferred — Faults: needs its fault table | |
| `0x4009` | 2 | U32 | | | Verified | — | Deferred — Faults: needs its fault table | |
| `0x400B` | 2 | U32 | | | Documented | — | Deferred — Faults: needs its fault table | |
| `0x4010` | 1 | I16 | 0.1 | °C | Verified | `inverter_temperature` | sensor | Core |
| `0x4011` | 1 | I16 | 0.1 | °C | Verified | `ambient_temperature` | sensor | Disabled |
| `0x4012` | 1 | U16 | 1 | mA | Verified | `leakage_current` | sensor | Disabled |
| `0x4013` | 1 | U16 | 1 | kΩ | Verified | `pv1_insulation_resistance` | sensor | Disabled |
| `0x4014` | 1 | U16 | 1 | kΩ | Verified | `pv2_insulation_resistance` | sensor | Disabled |
| `0x4019` | 1 | U16 | 1 | s | Verified | `grid_connection_countdown` | sensor | Disabled |
| `0x4023` | 1 | I16 | 1 | W | Responds, undocumented | `inverter_discharge_power_setpoint` | sensor | Disabled |
| `0x4024` | 1 | I16 | 1 | W | Responds, undocumented | `inverter_charge_power_setpoint` | sensor | Disabled |
| `0x4025` | 1 | I16 | 0.1 | A | Responds, undocumented | `battery_discharge_current_setpoint` | sensor | Disabled |
| `0x4026` | 1 | I16 | 0.1 | A | Responds, undocumented | `battery_charge_current_setpoint` | sensor | Disabled |
| `0x4027` | 1 | U16 | 1 |  | Responds, undocumented | `battery_status_code` | sensor | Disabled |
| `0x4028` | 1 | I16 | 1 |  | Responds, undocumented | `battery_protocol_active` | sensor | Disabled |
| `0x4029` | 1 | I16 | 1 |  | Responds, undocumented | `battery_charge_limit_active` | sensor | Disabled |
| `0x402A` | 1 | I16 | 1 |  | Verified | `battery_discharge_limit_active` | sensor | Disabled |
| `0x402B` | 1 | I16 | 1 |  | Responds, undocumented | `battery_depth_of_discharge_active` | sensor | Disabled |
| `0x402C` | 1 | I16 | 1 | % | Responds, undocumented | `backup_reserve_soc_active` | sensor | Disabled |
| `0x4030` | 1 | I16 | 1 |  | Responds, undocumented | `meter_configuration_active` | sensor | Disabled |
| `0x4031` | 1 | U16 | 0.1 | V | Verified | `grid_l1_voltage` | sensor | Core |
| `0x4032` | 1 | I16 | 0.01 | A | Verified | `grid_l1_current` | sensor | Disabled |
| `0x4033` | 1 | U16 | 0.01 | Hz | Verified | `grid_l1_frequency` | sensor | Core |
| `0x4034` | 1 | I16 | 1 | mA | Verified | `grid_l1_dc_current` | sensor | Disabled |
| `0x4035` | 1 | I16 | 1 | W | Verified | `grid_l1_power` | sensor | Disabled |
| `0x4036` | 1 | U16 | 1 | VA | Verified | `grid_l1_apparent_power` | sensor | Disabled |
| `0x4037` | 1 | I16 | 0.001 |  | Verified | `grid_l1_power_factor` | sensor | Disabled |
| `0x4038` | 1 | U16 | 0.1 | V | Verified | `grid_l2_voltage` | sensor | Core |
| `0x4039` | 1 | I16 | 0.01 | A | Verified | `grid_l2_current` | sensor | Disabled |
| `0x403A` | 1 | U16 | 0.01 | Hz | Verified | `grid_l2_frequency` | sensor | Disabled |
| `0x403B` | 1 | I16 | 1 | mA | Verified | `grid_l2_dc_current` | sensor | Disabled |
| `0x403C` | 1 | I16 | 1 | W | Verified | `grid_l2_power` | sensor | Disabled |
| `0x403D` | 1 | U16 | 1 | VA | Verified | `grid_l2_apparent_power` | sensor | Disabled |
| `0x403E` | 1 | I16 | 0.001 |  | Verified | `grid_l2_power_factor` | sensor | Disabled |
| `0x403F` | 1 | U16 | 0.1 | V | Verified | `grid_l3_voltage` | sensor | Core |
| `0x4040` | 1 | I16 | 0.01 | A | Verified | `grid_l3_current` | sensor | Disabled |
| `0x4041` | 1 | U16 | 0.01 | Hz | Verified | `grid_l3_frequency` | sensor | Disabled |
| `0x4042` | 1 | I16 | 1 | mA | Verified | `grid_l3_dc_current` | sensor | Disabled |
| `0x4043` | 1 | I16 | 1 | W | Verified | `grid_l3_power` | sensor | Disabled |
| `0x4044` | 1 | U16 | 1 | VA | Verified | `grid_l3_apparent_power` | sensor | Disabled |
| `0x4045` | 1 | I16 | 0.001 |  | Verified | `grid_l3_power_factor` | sensor | Disabled |
| `0x4046` | 1 | U16 | 0.1 | V | Verified | `inverter_l1_voltage` | sensor | Disabled |
| `0x4047` | 1 | I16 | 0.01 | A | Verified | `inverter_l1_current` | sensor | Disabled |
| `0x4048` | 1 | U16 | 0.01 | Hz | Verified | `inverter_l1_frequency` | sensor | Disabled |
| `0x4049` | 1 | I16 | 1 | W | Verified | `inverter_l1_power` | sensor | Disabled |
| `0x404A` | 1 | U16 | 1 | VA | Verified | `inverter_l1_apparent_power` | sensor | Disabled |
| `0x404B` | 1 | U16 | 0.1 | V | Verified | `inverter_l2_voltage` | sensor | Disabled |
| `0x404C` | 1 | I16 | 0.01 | A | Verified | `inverter_l2_current` | sensor | Disabled |
| `0x404D` | 1 | U16 | 0.01 | Hz | Verified | `inverter_l2_frequency` | sensor | Disabled |
| `0x404E` | 1 | I16 | 1 | W | Verified | `inverter_l2_power` | sensor | Disabled |
| `0x404F` | 1 | U16 | 1 | VA | Verified | `inverter_l2_apparent_power` | sensor | Disabled |
| `0x4050` | 1 | U16 | 0.1 | V | Verified | `inverter_l3_voltage` | sensor | Disabled |
| `0x4051` | 1 | I16 | 0.01 | A | Verified | `inverter_l3_current` | sensor | Disabled |
| `0x4052` | 1 | U16 | 0.01 | Hz | Verified | `inverter_l3_frequency` | sensor | Disabled |
| `0x4053` | 1 | I16 | 1 | W | Verified | `inverter_l3_power` | sensor | Disabled |
| `0x4054` | 1 | U16 | 1 | VA | Verified | `inverter_l3_apparent_power` | sensor | Disabled |
| `0x4055` | 1 | U16 | 0.1 | V | Verified | `backup_l1_voltage` | sensor | Disabled |
| `0x4056` | 1 | U16 | 0.01 | A | Verified | `backup_l1_current` | sensor | Disabled |
| `0x4057` | 1 | U16 | 0.01 | Hz | Verified | `backup_l1_frequency` | sensor | Disabled |
| `0x4058` | 1 | I16 | 1 | mV | Verified | `backup_l1_dc_voltage` | sensor | Disabled |
| `0x4059` | 1 | U16 | 1 | W | Verified | `backup_l1_power` | sensor | Disabled |
| `0x405A` | 1 | U16 | 1 | VA | Verified | `backup_l1_apparent_power` | sensor | Disabled |
| `0x405B` | 1 | U16 | 0.1 | V | Verified | `backup_l2_voltage` | sensor | Disabled |
| `0x405C` | 1 | U16 | 0.01 | A | Verified | `backup_l2_current` | sensor | Disabled |
| `0x405D` | 1 | U16 | 0.01 | Hz | Verified | `backup_l2_frequency` | sensor | Disabled |
| `0x405E` | 1 | I16 | 1 | mV | Verified | `backup_l2_dc_voltage` | sensor | Disabled |
| `0x405F` | 1 | U16 | 1 | W | Verified | `backup_l2_power` | sensor | Disabled |
| `0x4060` | 1 | U16 | 1 | VA | Verified | `backup_l2_apparent_power` | sensor | Disabled |
| `0x4061` | 1 | U16 | 0.1 | V | Verified | `backup_l3_voltage` | sensor | Disabled |
| `0x4062` | 1 | U16 | 0.01 | A | Verified | `backup_l3_current` | sensor | Disabled |
| `0x4063` | 1 | U16 | 0.01 | Hz | Verified | `backup_l3_frequency` | sensor | Disabled |
| `0x4064` | 1 | I16 | 1 | mV | Verified | `backup_l3_dc_voltage` | sensor | Disabled |
| `0x4065` | 1 | U16 | 1 | W | Verified | `backup_l3_power` | sensor | Disabled |
| `0x4066` | 1 | U16 | 1 | VA | Verified | `backup_l3_apparent_power` | sensor | Disabled |
| `0x4067` | 1 | U16 | 0.1 | V | Verified | `dc_bus_voltage` | sensor | Disabled |
| `0x4068` | 1 | U16 | 0.1 | V | Verified | `dc_bus_slave_voltage` | sensor | Disabled |
| `0x4069` | 1 | U16 | 0.1 | V | Verified | `battery_voltage` | sensor | Core |
| `0x406A` | 1 | I16 | 0.01 | A | Verified | `battery_current` | sensor | Core |
| `0x406D` | 1 | I16 | 1 | W | Verified | `battery_port_power` | sensor | Disabled |
| `0x406E` | 1 | I16 | 0.1 | °C | Verified | `battery_temperature` | sensor | Core |
| `0x406F` | 1 | U16 | 0.01 | % | Verified | `battery_soc` | sensor | Core |
| `0x4071` | 1 | U16 | 0.1 | V | Verified | `pv1_voltage` | sensor | Core |
| `0x4072` | 1 | U16 | 0.01 | A | Verified | `pv1_current` | sensor | Core |
| `0x4073` | 1 | U16 | 1 | W | Verified | `pv1_power` | sensor | Core |
| `0x4074` | 1 | U16 | 0.1 | V | Verified | `pv2_voltage` | sensor | Core |
| `0x4075` | 1 | U16 | 0.01 | A | Verified | `pv2_current` | sensor | Core |
| `0x4076` | 1 | U16 | 1 | W | Verified | `pv2_power` | sensor | Core |
| `0x408D` | 1 | U16 | 0.1 | V | Verified | `grid_output_l1_voltage` | sensor | Disabled |
| `0x408E` | 1 | U16 | 0.01 | A | Verified | `grid_output_l1_current` | sensor | Disabled |
| `0x408F` | 1 | U16 | 0.01 | Hz | Verified | `grid_output_l1_frequency` | sensor | Disabled |
| `0x4090` | 1 | U16 | 1 | W | Verified | `grid_output_l1_power` | sensor | Disabled |
| `0x4091` | 1 | U16 | 0.1 | V | Verified | `grid_output_l2_voltage` | sensor | Disabled |
| `0x4092` | 1 | U16 | 1 | W | Verified | `grid_output_l2_power` | sensor | Disabled |
| `0x4093` | 1 | U16 | 0.1 | V | Verified | `grid_output_l3_voltage` | sensor | Disabled |
| `0x4094` | 1 | U16 | 1 | W | Verified | `grid_output_l3_power` | sensor | Disabled |
| `0x4095` | 1 | U16 | 1 |  | Verified | `pv_direction` | sensor | Disabled |
| `0x4096` | 1 | I16 | 1 |  | Verified | `battery_direction` | sensor | Disabled |
| `0x4097` | 1 | I16 | 1 |  | Verified | `grid_direction` | sensor | Disabled |
| `0x4098` | 1 | U16 | 1 |  | Responds, undocumented | `output_direction` | sensor | Disabled |
| `0x40A0` | 1 | I16 | 1 | W | Verified | `load_power` | sensor | Core |
| `0x40A5` | 1 | I16 | 1 | W | Verified | `pv_power` | sensor | Core |
| `0x40A6` | 1 | I16 | 1 | W | Verified | `battery_power` | sensor | Core |
| `0x40A7` | 1 | I16 | 1 | W | Verified | `grid_power` | sensor | Core |
| `0x40A9` | 1 | I16 | 1 | W | Verified | `inverter_power` | sensor | Core |
| `0x40AD` | 1 | I16 | 1 | W | Verified | `grid_load_power` | sensor | Disabled |

**Energy counters** — 52 registers.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0x40BF` | 2 | U32 | 0.01 | kWh | Verified | `pv_energy_today` | sensor | Core |
| `0x40C1` | 2 | U32 | 0.01 | kWh | Verified | `pv_energy_month` | sensor | Disabled |
| `0x40C3` | 2 | U32 | 0.01 | kWh | Verified | `pv_energy_year` | sensor | Disabled |
| `0x40C5` | 2 | U32 | 0.01 | kWh | Verified | `pv_energy_total` | sensor | Core |
| `0x40C7` | 2 | U32 | 0.01 | kWh | Verified | `battery_charge_energy_today` | sensor | Core |
| `0x40C9` | 2 | U32 | 0.01 | kWh | Verified | `battery_charge_energy_month` | sensor | Disabled |
| `0x40CB` | 2 | U32 | 0.01 | kWh | Verified | `battery_charge_energy_year` | sensor | Disabled |
| `0x40CD` | 2 | U32 | 0.01 | kWh | Verified | `battery_charge_energy_total` | sensor | Core |
| `0x40CF` | 2 | U32 | 0.01 | kWh | Verified | `battery_discharge_energy_today` | sensor | Core |
| `0x40D1` | 2 | U32 | 0.01 | kWh | Verified | `battery_discharge_energy_month` | sensor | Disabled |
| `0x40D3` | 2 | U32 | 0.01 | kWh | Verified | `battery_discharge_energy_year` | sensor | Disabled |
| `0x40D5` | 2 | U32 | 0.01 | kWh | Verified | `battery_discharge_energy_total` | sensor | Core |
| `0x40DF` | 2 | U32 | 0.01 | kWh | Verified | `load_energy_today` | sensor | Core |
| `0x40E1` | 2 | U32 | 0.01 | kWh | Verified | `load_energy_month` | sensor | Disabled |
| `0x40E3` | 2 | U32 | 0.01 | kWh | Verified | `load_energy_year` | sensor | Disabled |
| `0x40E5` | 2 | U32 | 0.01 | kWh | Verified | `load_energy_total` | sensor | Core |
| `0x40E7` | 2 | U32 | 0.01 | kWh | Verified | `backup_load_energy_today` | sensor | Core |
| `0x40E9` | 2 | U32 | 0.01 | kWh | Verified | `backup_load_energy_month` | sensor | Disabled |
| `0x40EB` | 2 | U32 | 0.01 | kWh | Verified | `backup_load_energy_year` | sensor | Disabled |
| `0x40ED` | 2 | U32 | 0.01 | kWh | Verified | `backup_load_energy_total` | sensor | Core |
| `0x40EF` | 2 | U32 | 0.01 | kWh | Verified | `grid_l1_export_energy_today` | sensor | Disabled |
| `0x40F1` | 2 | U32 | 0.01 | kWh | Verified | `grid_l1_export_energy_month` | sensor | Disabled |
| `0x40F3` | 2 | U32 | 0.01 | kWh | Verified | `grid_l1_export_energy_year` | sensor | Disabled |
| `0x40F5` | 2 | U32 | 0.01 | kWh | Verified | `grid_l1_export_energy_total` | sensor | Disabled |
| `0x40F7` | 2 | U32 | 0.01 | kWh | Verified | `grid_l1_import_energy_today` | sensor | Disabled |
| `0x40F9` | 2 | U32 | 0.01 | kWh | Verified | `grid_l1_import_energy_month` | sensor | Disabled |
| `0x40FB` | 2 | U32 | 0.01 | kWh | Verified | `grid_l1_import_energy_year` | sensor | Disabled |
| `0x40FD` | 2 | U32 | 0.01 | kWh | Verified | `grid_l1_import_energy_total` | sensor | Disabled |
| `0x4147` | 2 | U32 | 0.01 | kWh | Verified | `grid_l2_export_energy_today` | sensor | Disabled |
| `0x4149` | 2 | U32 | 0.01 | kWh | Verified | `grid_l2_export_energy_month` | sensor | Disabled |
| `0x414B` | 2 | U32 | 0.01 | kWh | Verified | `grid_l2_export_energy_year` | sensor | Disabled |
| `0x414D` | 2 | U32 | 0.01 | kWh | Verified | `grid_l2_export_energy_total` | sensor | Disabled |
| `0x414F` | 2 | U32 | 0.01 | kWh | Verified | `grid_l3_export_energy_today` | sensor | Disabled |
| `0x4151` | 2 | U32 | 0.01 | kWh | Verified | `grid_l3_export_energy_month` | sensor | Disabled |
| `0x4153` | 2 | U32 | 0.01 | kWh | Verified | `grid_l3_export_energy_year` | sensor | Disabled |
| `0x4155` | 2 | U32 | 0.01 | kWh | Verified | `grid_l3_export_energy_total` | sensor | Disabled |
| `0x4157` | 2 | U32 | 0.01 | kWh | Verified | `grid_l2_import_energy_today` | sensor | Disabled |
| `0x4159` | 2 | U32 | 0.01 | kWh | Verified | `grid_l2_import_energy_month` | sensor | Disabled |
| `0x415B` | 2 | U32 | 0.01 | kWh | Verified | `grid_l2_import_energy_year` | sensor | Disabled |
| `0x415D` | 2 | U32 | 0.01 | kWh | Verified | `grid_l2_import_energy_total` | sensor | Disabled |
| `0x415F` | 2 | U32 | 0.01 | kWh | Verified | `grid_l3_import_energy_today` | sensor | Disabled |
| `0x4161` | 2 | U32 | 0.01 | kWh | Verified | `grid_l3_import_energy_month` | sensor | Disabled |
| `0x4163` | 2 | U32 | 0.01 | kWh | Verified | `grid_l3_import_energy_year` | sensor | Disabled |
| `0x4165` | 2 | U32 | 0.01 | kWh | Verified | `grid_l3_import_energy_total` | sensor | Disabled |
| `0x4167` | 2 | U32 | 0.01 | kWh | Verified | `grid_import_energy_today` | sensor | Core |
| `0x4169` | 2 | U32 | 0.01 | kWh | Verified | `grid_import_energy_month` | sensor | Disabled |
| `0x416B` | 2 | U32 | 0.01 | kWh | Verified | `grid_import_energy_year` | sensor | Disabled |
| `0x416D` | 2 | U32 | 0.01 | kWh | Verified | `grid_import_energy_total` | sensor | Core |
| `0x416F` | 2 | U32 | 0.01 | kWh | Verified | `grid_export_energy_today` | sensor | Core |
| `0x4171` | 2 | U32 | 0.01 | kWh | Verified | `grid_export_energy_month` | sensor | Disabled |
| `0x4173` | 2 | U32 | 0.01 | kWh | Verified | `grid_export_energy_year` | sensor | Disabled |
| `0x4175` | 2 | U32 | 0.01 | kWh | Verified | `grid_export_energy_total` | sensor | Core |

**Parallel machines** — 71 registers. Optional equipment: parallel. Every row is created disabled.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0x4200` | 1 | U16 | 1 |  | Responds, unchecked | `parallel_mode` | sensor | Disabled |
| `0x4201` | 1 | U16 | 1 |  | Responds, unchecked | `parallel_id` | sensor | Disabled |
| `0x4202` | 1 | U16 | 1 |  | Responds, unchecked | `parallel_count` | sensor | Disabled |
| `0x4203` | 1 | U16 | 1 |  | Responds, unchecked | `parallel_online_count` | sensor | Disabled |
| `0x4204` | 1 | U16 | 1 | W | Responds, unchecked | `parallel_pv_power_low_word` | sensor | Disabled |
| `0x4205` | 1 | U16 | 1 | W | Responds, unchecked | `parallel_battery_power_low_word` | sensor | Disabled |
| `0x4206` | 1 | U16 | 1 | W | Responds, unchecked | `parallel_grid_power_low_word` | sensor | Disabled |
| `0x4207` | 1 | U16 | 1 | W | Responds, unchecked | `parallel_load_power_low_word` | sensor | Disabled |
| `0x4208` | 1 | U16 | 1 | W | Responds, unchecked | `parallel_backup_load_power_low_word` | sensor | Disabled |
| `0x4209` | 1 | U16 | 0.01 | % | Responds, unchecked | `parallel_battery_soc` | sensor | Disabled |
| `0x420A` | 1 | U16 | 1 | W | Responds, unchecked | `parallel_grid_load_power_low_word` | sensor | Disabled |
| `0x420B` | 1 | U16 | 1 | Ah | Responds, unchecked | `parallel_battery_capacity` | sensor | Disabled |
| `0x420C` | 1 | U16 | 1 | W | Responds, unchecked | `parallel_pv_power_high_word` | sensor | Disabled |
| `0x420D` | 1 | I16 | 1 | W | Responds, unchecked | `parallel_battery_power_high_word` | sensor | Disabled |
| `0x420E` | 1 | I16 | 1 | W | Responds, unchecked | `parallel_grid_power_high_word` | sensor | Disabled |
| `0x420F` | 1 | U16 | 1 | W | Responds, unchecked | `parallel_load_power_high_word` | sensor | Disabled |
| `0x4210` | 1 | I16 | 1 | W | Responds, unchecked | `parallel_backup_load_power_high_word` | sensor | Disabled |
| `0x4211` | 1 | I16 | 1 | W | Responds, unchecked | `parallel_grid_load_power_high_word` | sensor | Disabled |
| `0x4212` | 2 | I32 | 1 | W | Responds, unchecked | `parallel_meter_b_power` | sensor | Disabled |
| `0x4215` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_pv_energy_today` | sensor | Disabled |
| `0x4217` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_pv_energy_month` | sensor | Disabled |
| `0x4219` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_pv_energy_year` | sensor | Disabled |
| `0x421B` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_pv_energy_total` | sensor | Disabled |
| `0x421D` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_battery_charge_energy_today` | sensor | Disabled |
| `0x421F` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_battery_charge_energy_month` | sensor | Disabled |
| `0x4221` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_battery_charge_energy_year` | sensor | Disabled |
| `0x4223` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_battery_charge_energy_total` | sensor | Disabled |
| `0x4225` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_battery_discharge_energy_today` | sensor | Disabled |
| `0x4227` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_battery_discharge_energy_month` | sensor | Disabled |
| `0x4229` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_battery_discharge_energy_year` | sensor | Disabled |
| `0x422B` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_battery_discharge_energy_total` | sensor | Disabled |
| `0x422D` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l1_export_energy_today` | sensor | Disabled |
| `0x422F` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l1_export_energy_month` | sensor | Disabled |
| `0x4231` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l1_export_energy_year` | sensor | Disabled |
| `0x4233` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l1_export_energy_total` | sensor | Disabled |
| `0x4235` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l2_export_energy_today` | sensor | Disabled |
| `0x4237` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l2_export_energy_month` | sensor | Disabled |
| `0x4239` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l2_export_energy_year` | sensor | Disabled |
| `0x423B` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l2_export_energy_total` | sensor | Disabled |
| `0x423D` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l3_export_energy_today` | sensor | Disabled |
| `0x423F` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l3_export_energy_month` | sensor | Disabled |
| `0x4241` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l3_export_energy_year` | sensor | Disabled |
| `0x4243` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l3_export_energy_total` | sensor | Disabled |
| `0x4245` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l1_import_energy_today` | sensor | Disabled |
| `0x4247` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l1_import_energy_month` | sensor | Disabled |
| `0x4249` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l1_import_energy_year` | sensor | Disabled |
| `0x424B` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l1_import_energy_total` | sensor | Disabled |
| `0x424D` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l2_import_energy_today` | sensor | Disabled |
| `0x424F` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l2_import_energy_month` | sensor | Disabled |
| `0x4251` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l2_import_energy_year` | sensor | Disabled |
| `0x4253` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l2_import_energy_total` | sensor | Disabled |
| `0x4255` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l3_import_energy_today` | sensor | Disabled |
| `0x4257` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l3_import_energy_month` | sensor | Disabled |
| `0x4259` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l3_import_energy_year` | sensor | Disabled |
| `0x425B` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_l3_import_energy_total` | sensor | Disabled |
| `0x425D` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_load_energy_today` | sensor | Disabled |
| `0x425F` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_load_energy_month` | sensor | Disabled |
| `0x4261` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_load_energy_year` | sensor | Disabled |
| `0x4263` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_load_energy_total` | sensor | Disabled |
| `0x4265` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_import_energy_today` | sensor | Disabled |
| `0x4267` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_import_energy_month` | sensor | Disabled |
| `0x4269` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_import_energy_year` | sensor | Disabled |
| `0x426B` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_import_energy_total` | sensor | Disabled |
| `0x426D` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_export_energy_today` | sensor | Disabled |
| `0x426F` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_export_energy_month` | sensor | Disabled |
| `0x4271` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_export_energy_year` | sensor | Disabled |
| `0x4273` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_grid_export_energy_total` | sensor | Disabled |
| `0x4275` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_pv_meter_energy_today` | sensor | Disabled |
| `0x4277` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_pv_meter_energy_month` | sensor | Disabled |
| `0x4279` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_pv_meter_energy_year` | sensor | Disabled |
| `0x427B` | 2 | U32 | 0.01 | kWh | Responds, unchecked | `parallel_pv_meter_energy_total` | sensor | Disabled |

**EV charger settings** — 44 registers. Optional equipment: EV charger. Every row is created disabled.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0x4B00` | 1 | U16 | | | Verified | — | Deferred — Debug dump: block header word | |
| `0x4B01` | 1 | U16 | | | Verified | — | Deferred — Debug dump: block header word | |
| `0x4B02` | 1 | U16 | | | Verified | — | Deferred — Debug dump: block header word | |
| `0x4B03` | 1 | U16 | 1 |  | Verified | `ev_settings_protocol_version` | sensor | Disabled |
| `0x4B04` | 1 | U16 | 1 |  | Verified | `ev_enabled` | switch | Disabled |
| `0x4B05` | 1 | U16 | 1 |  | Verified | `ev_address` | number (1–127) | Disabled |
| `0x4B06` | 1 | U16 | 1 |  | Verified | `ev_baud_rate` | select | Disabled |
| `0x4B07` | 1 | U16 | 1 |  | Verified | `ev_charger_count` | number (1–3) | Disabled |
| `0x4B08` | 1 | U16 | 1 | s | Verified | `ev_communication_timeout` | number (1–6) | Disabled |
| `0x4B09` | 1 | U16 | 1 |  | Verified | `ev_port_mode` | select | Disabled |
| `0x4B0A` | 1 | U16 | 1 |  | Verified | `ev_port_address` | number (1–254) | Disabled |
| `0x4B12` | 1 | U16 | 1 |  | Verified | `ev_mode` | select | Disabled |
| `0x4B14` | 2 | U32 | 1 | W | Verified | `ev_charge_power` | number | Disabled |
| `0x4B20` | 1 | hh:mm | 1 |  | Verified | `ev_slot_1_start` | time | Disabled |
| `0x4B21` | 1 | hh:mm | 1 |  | Verified | `ev_slot_1_end` | time | Disabled |
| `0x4B22` | 1 | Bits | | | Verified | — | Packed fields, see below | |
| `0x4B23` | 2 | U32 | 1 | W | Verified | `ev_slot_1_power` | number | Disabled |
| `0x4B25` | 1 | hh:mm | 1 |  | Verified | `ev_slot_2_start` | time | Disabled |
| `0x4B26` | 1 | hh:mm | 1 |  | Verified | `ev_slot_2_end` | time | Disabled |
| `0x4B27` | 1 | Bits | | | Verified | — | Packed fields, see below | |
| `0x4B28` | 2 | U32 | 1 | W | Verified | `ev_slot_2_power` | number | Disabled |
| `0x4B2A` | 1 | hh:mm | 1 |  | Verified | `ev_slot_3_start` | time | Disabled |
| `0x4B2B` | 1 | hh:mm | 1 |  | Verified | `ev_slot_3_end` | time | Disabled |
| `0x4B2C` | 1 | Bits | | | Verified | — | Packed fields, see below | |
| `0x4B2D` | 2 | U32 | 1 | W | Verified | `ev_slot_3_power` | number | Disabled |
| `0x4B2F` | 1 | hh:mm | 1 |  | Verified | `ev_slot_4_start` | time | Disabled |
| `0x4B30` | 1 | hh:mm | 1 |  | Verified | `ev_slot_4_end` | time | Disabled |
| `0x4B31` | 1 | Bits | | | Verified | — | Packed fields, see below | |
| `0x4B32` | 2 | U32 | 1 | W | Verified | `ev_slot_4_power` | number | Disabled |
| `0x4B34` | 1 | hh:mm | 1 |  | Verified | `ev_slot_5_start` | time | Disabled |
| `0x4B35` | 1 | hh:mm | 1 |  | Verified | `ev_slot_5_end` | time | Disabled |
| `0x4B36` | 1 | Bits | | | Verified | — | Packed fields, see below | |
| `0x4B37` | 2 | U32 | 1 | W | Verified | `ev_slot_5_power` | number | Disabled |
| `0x4B39` | 1 | hh:mm | 1 |  | Verified | `ev_slot_6_start` | time | Disabled |
| `0x4B3A` | 1 | hh:mm | 1 |  | Verified | `ev_slot_6_end` | time | Disabled |
| `0x4B3B` | 1 | Bits | | | Verified | — | Packed fields, see below | |
| `0x4B3C` | 2 | U32 | 1 | W | Verified | `ev_slot_6_power` | number | Disabled |
| `0x4B3E` | 1 | hh:mm | 1 |  | Verified | `ev_slot_7_start` | time | Disabled |
| `0x4B3F` | 1 | hh:mm | 1 |  | Verified | `ev_slot_7_end` | time | Disabled |
| `0x4B40` | 1 | Bits | | | Verified | — | Packed fields, see below | |
| `0x4B41` | 2 | U32 | 1 | W | Verified | `ev_slot_7_power` | number | Disabled |
| `0x4B43` | 1 | Bits | | | Verified | — | Packed fields, see below | |
| `0x4B46` | 1 | Bits | | | Documented | — | Deferred — Writes: EMS control of the charger | |
| `0x4B47` | 1 | U16 | | | Documented | — | Deferred — Writes: EMS control of the charger | |

**Five-minute averages** — 92 registers.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0x513E` | 2 | I32 | 1 | W | Verified | `average_grid_power` | sensor | Disabled |
| `0x5140` | 2 | I32 | 1 | W | Verified | `average_grid_l1_power` | sensor | Disabled |
| `0x5142` | 1 | U16 | 0.1 | V | Verified | `average_grid_l1_voltage` | sensor | Disabled |
| `0x5143` | 1 | I16 | 0.01 | A | Verified | `average_grid_l1_current` | sensor | Disabled |
| `0x5144` | 1 | U16 | 0.01 | Hz | Verified | `average_grid_l1_frequency` | sensor | Disabled |
| `0x5145` | 2 | I32 | 1 | W | Verified | `average_grid_l2_power` | sensor | Disabled |
| `0x5147` | 1 | U16 | 0.1 | V | Verified | `average_grid_l2_voltage` | sensor | Disabled |
| `0x5148` | 1 | I16 | 0.01 | A | Verified | `average_grid_l2_current` | sensor | Disabled |
| `0x5149` | 1 | U16 | 0.01 | Hz | Verified | `average_grid_l2_frequency` | sensor | Disabled |
| `0x514A` | 2 | I32 | 1 | W | Verified | `average_grid_l3_power` | sensor | Disabled |
| `0x514C` | 1 | U16 | 0.1 | V | Verified | `average_grid_l3_voltage` | sensor | Disabled |
| `0x514D` | 1 | I16 | 0.01 | A | Verified | `average_grid_l3_current` | sensor | Disabled |
| `0x514E` | 1 | U16 | 0.01 | Hz | Verified | `average_grid_l3_frequency` | sensor | Disabled |
| `0x514F` | 2 | I32 | 1 | W | Verified | `average_inverter_power` | sensor | Disabled |
| `0x5151` | 2 | I32 | 1 | W | Verified | `average_inverter_l1_power` | sensor | Disabled |
| `0x5153` | 1 | U16 | 0.1 | V | Verified | `average_inverter_l1_voltage` | sensor | Disabled |
| `0x5154` | 1 | I16 | 0.01 | A | Verified | `average_inverter_l1_current` | sensor | Disabled |
| `0x5155` | 1 | U16 | 0.01 | Hz | Verified | `average_inverter_l1_frequency` | sensor | Disabled |
| `0x5156` | 2 | I32 | 1 | W | Verified | `average_inverter_l2_power` | sensor | Disabled |
| `0x5158` | 1 | U16 | 0.1 | V | Verified | `average_inverter_l2_voltage` | sensor | Disabled |
| `0x5159` | 1 | I16 | 0.01 | A | Verified | `average_inverter_l2_current` | sensor | Disabled |
| `0x515A` | 1 | U16 | 0.01 | Hz | Verified | `average_inverter_l2_frequency` | sensor | Disabled |
| `0x515B` | 2 | I32 | 1 | W | Verified | `average_inverter_l3_power` | sensor | Disabled |
| `0x515D` | 1 | U16 | 0.1 | V | Verified | `average_inverter_l3_voltage` | sensor | Disabled |
| `0x515E` | 1 | I16 | 0.01 | A | Verified | `average_inverter_l3_current` | sensor | Disabled |
| `0x515F` | 1 | U16 | 0.01 | Hz | Verified | `average_inverter_l3_frequency` | sensor | Disabled |
| `0x5160` | 2 | I32 | 1 | W | Verified | `average_load_power` | sensor | Disabled |
| `0x5162` | 2 | I32 | 1 | W | Verified | `average_load_l1_power` | sensor | Disabled |
| `0x5164` | 1 | U16 | 0.1 | V | Verified | `average_load_l1_voltage` | sensor | Disabled |
| `0x5165` | 1 | I16 | 0.01 | A | Verified | `average_load_l1_current` | sensor | Disabled |
| `0x5166` | 1 | U16 | 0.01 | Hz | Verified | `average_load_l1_frequency` | sensor | Disabled |
| `0x5167` | 2 | I32 | 1 | W | Verified | `average_load_l2_power` | sensor | Disabled |
| `0x5169` | 1 | U16 | 0.1 | V | Verified | `average_load_l2_voltage` | sensor | Disabled |
| `0x516A` | 1 | I16 | 0.01 | A | Verified | `average_load_l2_current` | sensor | Disabled |
| `0x516B` | 1 | U16 | 0.01 | Hz | Verified | `average_load_l2_frequency` | sensor | Disabled |
| `0x516C` | 2 | I32 | 1 | W | Verified | `average_load_l3_power` | sensor | Disabled |
| `0x516E` | 1 | U16 | 0.1 | V | Verified | `average_load_l3_voltage` | sensor | Disabled |
| `0x516F` | 1 | I16 | 0.01 | A | Verified | `average_load_l3_current` | sensor | Disabled |
| `0x5170` | 1 | U16 | 0.01 | Hz | Verified | `average_load_l3_frequency` | sensor | Disabled |
| `0x5171` | 2 | I32 | 1 | W | Verified | `average_grid_load_power` | sensor | Disabled |
| `0x5173` | 2 | I32 | 1 | W | Verified | `average_grid_load_l1_power` | sensor | Disabled |
| `0x5175` | 1 | U16 | 0.1 | V | Verified | `average_grid_load_l1_voltage` | sensor | Disabled |
| `0x5176` | 1 | I16 | 0.01 | A | Verified | `average_grid_load_l1_current` | sensor | Disabled |
| `0x5177` | 1 | U16 | 0.01 | Hz | Verified | `average_grid_load_l1_frequency` | sensor | Disabled |
| `0x5178` | 2 | I32 | 1 | W | Verified | `average_grid_load_l2_power` | sensor | Disabled |
| `0x517A` | 1 | U16 | 0.1 | V | Verified | `average_grid_load_l2_voltage` | sensor | Disabled |
| `0x517B` | 1 | I16 | 0.01 | A | Verified | `average_grid_load_l2_current` | sensor | Disabled |
| `0x517C` | 1 | U16 | 0.01 | Hz | Verified | `average_grid_load_l2_frequency` | sensor | Disabled |
| `0x517D` | 2 | I32 | 1 | W | Verified | `average_grid_load_l3_power` | sensor | Disabled |
| `0x517F` | 1 | U16 | 0.1 | V | Verified | `average_grid_load_l3_voltage` | sensor | Disabled |
| `0x5180` | 1 | I16 | 0.01 | A | Verified | `average_grid_load_l3_current` | sensor | Disabled |
| `0x5181` | 1 | U16 | 0.01 | Hz | Verified | `average_grid_load_l3_frequency` | sensor | Disabled |
| `0x5182` | 2 | I32 | 1 | W | Verified | `average_backup_power` | sensor | Disabled |
| `0x5184` | 2 | I32 | 1 | W | Verified | `average_backup_l1_power` | sensor | Disabled |
| `0x5186` | 1 | U16 | 0.1 | V | Verified | `average_backup_l1_voltage` | sensor | Disabled |
| `0x5187` | 1 | I16 | 0.01 | A | Verified | `average_backup_l1_current` | sensor | Disabled |
| `0x5188` | 1 | U16 | 0.01 | Hz | Verified | `average_backup_l1_frequency` | sensor | Disabled |
| `0x5189` | 2 | I32 | 1 | W | Verified | `average_backup_l2_power` | sensor | Disabled |
| `0x518B` | 1 | U16 | 0.1 | V | Verified | `average_backup_l2_voltage` | sensor | Disabled |
| `0x518C` | 1 | I16 | 0.01 | A | Verified | `average_backup_l2_current` | sensor | Disabled |
| `0x518D` | 1 | U16 | 0.01 | Hz | Verified | `average_backup_l2_frequency` | sensor | Disabled |
| `0x518E` | 2 | I32 | 1 | W | Verified | `average_backup_l3_power` | sensor | Disabled |
| `0x5190` | 1 | U16 | 0.1 | V | Verified | `average_backup_l3_voltage` | sensor | Disabled |
| `0x5191` | 1 | I16 | 0.01 | A | Verified | `average_backup_l3_current` | sensor | Disabled |
| `0x5192` | 1 | U16 | 0.01 | Hz | Verified | `average_backup_l3_frequency` | sensor | Disabled |
| `0x5193` | 2 | I32 | 1 | W | Verified | `average_pv_power` | sensor | Disabled |
| `0x5195` | 1 | U16 | 0.1 | V | Verified | `average_pv1_voltage` | sensor | Disabled |
| `0x5196` | 1 | I16 | 0.01 | A | Verified | `average_pv1_current` | sensor | Disabled |
| `0x5197` | 2 | U32 | 1 | W | Verified | `average_pv1_power` | sensor | Disabled |
| `0x5199` | 1 | U16 | 0.1 | V | Verified | `average_pv2_voltage` | sensor | Disabled |
| `0x519A` | 1 | I16 | 0.01 | A | Verified | `average_pv2_current` | sensor | Disabled |
| `0x519B` | 2 | U32 | 1 | W | Verified | `average_pv2_power` | sensor | Disabled |
| `0x51A5` | 2 | I32 | 1 | W | Verified | `average_generator_power` | sensor | Disabled |
| `0x51A7` | 2 | I32 | 1 | W | Verified | `average_generator_l1_power` | sensor | Disabled |
| `0x51A9` | 1 | U16 | 0.1 | V | Verified | `average_generator_l1_voltage` | sensor | Disabled |
| `0x51AA` | 1 | I16 | 0.01 | A | Verified | `average_generator_l1_current` | sensor | Disabled |
| `0x51AB` | 1 | U16 | 0.01 | Hz | Verified | `average_generator_l1_frequency` | sensor | Disabled |
| `0x51AC` | 2 | I32 | 1 | W | Verified | `average_generator_l2_power` | sensor | Disabled |
| `0x51AE` | 1 | U16 | 0.1 | V | Verified | `average_generator_l2_voltage` | sensor | Disabled |
| `0x51AF` | 1 | I16 | 0.01 | A | Verified | `average_generator_l2_current` | sensor | Disabled |
| `0x51B0` | 1 | U16 | 0.01 | Hz | Verified | `average_generator_l2_frequency` | sensor | Disabled |
| `0x51B1` | 2 | I32 | 1 | W | Verified | `average_generator_l3_power` | sensor | Disabled |
| `0x51B3` | 1 | U16 | 0.1 | V | Verified | `average_generator_l3_voltage` | sensor | Disabled |
| `0x51B4` | 1 | I16 | 0.01 | A | Verified | `average_generator_l3_current` | sensor | Disabled |
| `0x51B5` | 1 | U16 | 0.01 | Hz | Verified | `average_generator_l3_frequency` | sensor | Disabled |
| `0x51B6` | 2 | I32 | 1 | W | Verified | `average_battery_power` | sensor | Disabled |
| `0x51B8` | 1 | U16 | 0.01 | % | Verified | `average_battery_soc` | sensor | Disabled |
| `0x51B9` | 2 | I32 | 1 | W | Verified | `average_battery_pack1_power` | sensor | Disabled |
| `0x51BB` | 1 | U16 | 0.1 | V | Verified | `average_battery_pack1_voltage` | sensor | Disabled |
| `0x51BC` | 1 | I16 | 0.01 | A | Verified | `average_battery_pack1_current` | sensor | Disabled |
| `0x51BD` | 1 | U16 | 0.01 | % | Verified | `average_battery_pack1_soc` | sensor | Disabled |
| `0x51BE` | 1 | I16 | 0.1 | °C | Verified | `average_battery_pack1_temperature` | sensor | Disabled |

**Commands** — 5 registers.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0x8015` | 1 | U16 | | | Documented | — | Deferred — Writes: write-only command | |
| `0x801A` | 1 | U16 | | | Documented | — | Deferred — Writes: write-only command | |
| `0x801B` | 1 | U16 | | | Documented | — | Deferred — Writes: write-only command | |
| `0x801C` | 1 | U16 | | | Documented | — | Deferred — Writes: write-only command | |
| `0x8020` | 4 | Clock | | | Documented | — | Deferred — Writes: write-only command | |

**EMS** — 10 registers.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0x8400` | 1 | Bits | | | Verified | — | Packed fields, see below | |
| `0x8401` | 1 | U16 | 1 | s | Verified | `ems_timeout` | number (0–65534) | Disabled |
| `0x8402` | 1 | I16 | | | Verified | — | Deferred — Writes: EMS target or limit; reading keeps the inverter in EMS | |
| `0x8403` | 1 | U16 | | | Verified | — | Deferred — Writes: EMS target or limit; reading keeps the inverter in EMS | |
| `0x8404` | 1 | U16 | | | Verified | — | Deferred — Writes: EMS target or limit; reading keeps the inverter in EMS | |
| `0x8405` | 1 | I16 | | | Verified | — | Deferred — Writes: EMS target or limit; reading keeps the inverter in EMS | |
| `0x840F` | 1 | U16 | | | Verified | — | Deferred — Writes: EMS target or limit; reading keeps the inverter in EMS | |
| `0x8410` | 1 | U16 | | | Verified | — | Deferred — Writes: EMS target or limit; reading keeps the inverter in EMS | |
| `0x8411` | 1 | I16 | | | Verified | — | Deferred — Writes: EMS target or limit; reading keeps the inverter in EMS | |
| `0x8412` | 1 | U16 | | | Verified | — | Deferred — Writes: EMS target or limit; reading keeps the inverter in EMS | |

**Identity and versions** — 10 registers.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0x8F00` | 1 | U16 | | | Verified | — | Deferred — Not an entity: read by identity and shown on the device | |
| `0x8F01` | 1 | U16 | | | Verified | — | Deferred — Not an entity: read by identity and shown on the device | |
| `0x8F03` | 10 | Text | | | Verified | — | Deferred — Not an entity: read by identity and shown on the device | |
| `0x8F0D` | 10 | Text | 1 |  | Verified | `product_code` | sensor (text) | Disabled |
| `0x8F17` | 1 | U16 | 0.001 |  | Verified | `display_software_version` | sensor | Disabled |
| `0x8F18` | 1 | U16 | 0.001 |  | Verified | `master_software_version` | sensor | Disabled |
| `0x8F19` | 1 | U16 | 0.001 |  | Documented | `slave_software_version` | sensor | Disabled |
| `0x8F1A` | 1 | U16 | 0.001 |  | Verified | `display_hardware_version` | sensor | Disabled |
| `0x8F1B` | 1 | U16 | 0.001 |  | Verified | `control_hardware_version` | sensor | Disabled |
| `0x8F1C` | 1 | U16 | 0.001 |  | Verified | `power_hardware_version` | sensor | Disabled |

**Battery packs** — 15 registers.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0xA000` | 1 | U16 | 1 |  | Responds, undocumented | `battery_pack_count` | sensor | Disabled |
| `0xA001` | 1 | U16 | 1 |  | Responds, undocumented | `battery_capacity` | sensor | Disabled |
| `0xA002` | 1 | U16 | | | Responds, undocumented | — | Deferred — Faults: needs its fault table | |
| `0xA003` | 1 | U16 | | | Responds, undocumented | — | Deferred — Faults: needs its fault table | |
| `0xA00A` | 1 | U16 | 1 |  | Responds, undocumented | `battery_usable_capacity` | sensor | Disabled |
| `0xA00B` | 1 | U16 | 1 |  | Responds, undocumented | `battery_online_code` | sensor | Disabled |
| `0xA00C` | 1 | U16 | 0.01 | % | Responds, undocumented | `battery_pack1_soc` | sensor | Disabled |
| `0xA00D` | 1 | U16 | 0.01 | % | Responds, undocumented | `battery_pack1_soh` | sensor | Disabled |
| `0xA00E` | 1 | U16 | 0.1 | V | Responds, undocumented | `battery_pack1_voltage` | sensor | Disabled |
| `0xA00F` | 1 | I16 | 0.01 | A | Responds, undocumented | `battery_pack1_current` | sensor | Disabled |
| `0xA010` | 1 | I16 | 0.1 | °C | Responds, undocumented | `battery_pack1_temperature` | sensor | Disabled |
| `0xA011` | 1 | U16 | 1 |  | Responds, undocumented | `battery_pack1_cycles` | sensor | Disabled |
| `0xA02A` | 2 | U32 | 1 | kWh | Responds, undocumented | `battery_pack1_discharged_energy` | sensor | Disabled |
| `0xA036` | 1 | U16 | 0.1 | A | Responds, undocumented | `battery_discharge_current_limit` | sensor | Disabled |
| `0xA037` | 1 | U16 | 0.1 | A | Responds, undocumented | `battery_charge_current_limit` | sensor | Disabled |

**Meters** — 50 registers.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0xA03C` | 1 | U16 | 1 |  | Verified | `meter_a_status` | sensor (enum) | Disabled |
| `0xA03D` | 1 | U16 | 0.1 | V | Verified | `meter_a_l1_voltage` | sensor | Disabled |
| `0xA03E` | 1 | I16 | 0.01 | A | Verified | `meter_a_l1_current` | sensor | Disabled |
| `0xA03F` | 1 | I16 | 1 | W | Verified | `meter_a_l1_power` | sensor | Disabled |
| `0xA040` | 1 | U16 | 1 | VA | Verified | `meter_a_l1_apparent_power` | sensor | Disabled |
| `0xA041` | 1 | I16 | 0.001 |  | Verified | `meter_a_l1_power_factor` | sensor | Disabled |
| `0xA042` | 1 | U16 | 0.01 | Hz | Verified | `meter_a_l1_frequency` | sensor | Disabled |
| `0xA043` | 1 | U16 | 0.1 | V | Verified | `meter_a_l2_voltage` | sensor | Disabled |
| `0xA044` | 1 | I16 | 0.01 | A | Verified | `meter_a_l2_current` | sensor | Disabled |
| `0xA045` | 1 | I16 | 1 | W | Verified | `meter_a_l2_power` | sensor | Disabled |
| `0xA046` | 1 | U16 | 1 | VA | Verified | `meter_a_l2_apparent_power` | sensor | Disabled |
| `0xA047` | 1 | I16 | 0.001 |  | Verified | `meter_a_l2_power_factor` | sensor | Disabled |
| `0xA048` | 1 | U16 | 0.01 | Hz | Verified | `meter_a_l2_frequency` | sensor | Disabled |
| `0xA049` | 1 | U16 | 0.1 | V | Verified | `meter_a_l3_voltage` | sensor | Disabled |
| `0xA04A` | 1 | I16 | 0.01 | A | Verified | `meter_a_l3_current` | sensor | Disabled |
| `0xA04B` | 1 | I16 | 1 | W | Verified | `meter_a_l3_power` | sensor | Disabled |
| `0xA04C` | 1 | U16 | 1 | VA | Verified | `meter_a_l3_apparent_power` | sensor | Disabled |
| `0xA04D` | 1 | I16 | 0.001 |  | Verified | `meter_a_l3_power_factor` | sensor | Disabled |
| `0xA04E` | 1 | U16 | 0.01 | Hz | Verified | `meter_a_l3_frequency` | sensor | Disabled |
| `0xA053` | 1 | U16 | 1 |  | Responds, unchecked | `meter_b_status` | sensor (enum) | Disabled |
| `0xA054` | 1 | U16 | 0.1 | V | Responds, unchecked | `meter_b_l1_voltage` | sensor | Disabled |
| `0xA055` | 1 | I16 | 0.01 | A | Responds, unchecked | `meter_b_l1_current` | sensor | Disabled |
| `0xA056` | 1 | I16 | 1 | W | Responds, unchecked | `meter_b_l1_power` | sensor | Disabled |
| `0xA057` | 1 | U16 | 1 | VA | Responds, unchecked | `meter_b_l1_apparent_power` | sensor | Disabled |
| `0xA058` | 1 | I16 | 0.001 |  | Responds, unchecked | `meter_b_l1_power_factor` | sensor | Disabled |
| `0xA059` | 1 | U16 | 0.01 | Hz | Responds, unchecked | `meter_b_l1_frequency` | sensor | Disabled |
| `0xA05A` | 1 | U16 | 0.1 | V | Responds, unchecked | `meter_b_l2_voltage` | sensor | Disabled |
| `0xA05B` | 1 | I16 | 0.01 | A | Responds, unchecked | `meter_b_l2_current` | sensor | Disabled |
| `0xA05C` | 1 | I16 | 1 | W | Responds, unchecked | `meter_b_l2_power` | sensor | Disabled |
| `0xA05D` | 1 | U16 | 1 | VA | Responds, unchecked | `meter_b_l2_apparent_power` | sensor | Disabled |
| `0xA05E` | 1 | I16 | 0.001 |  | Responds, unchecked | `meter_b_l2_power_factor` | sensor | Disabled |
| `0xA05F` | 1 | U16 | 0.01 | Hz | Responds, unchecked | `meter_b_l2_frequency` | sensor | Disabled |
| `0xA060` | 1 | U16 | 0.1 | V | Responds, unchecked | `meter_b_l3_voltage` | sensor | Disabled |
| `0xA061` | 1 | I16 | 0.01 | A | Responds, unchecked | `meter_b_l3_current` | sensor | Disabled |
| `0xA062` | 1 | I16 | 1 | W | Responds, unchecked | `meter_b_l3_power` | sensor | Disabled |
| `0xA063` | 1 | U16 | 1 | VA | Responds, unchecked | `meter_b_l3_apparent_power` | sensor | Disabled |
| `0xA064` | 1 | I16 | 0.001 |  | Responds, unchecked | `meter_b_l3_power_factor` | sensor | Disabled |
| `0xA065` | 1 | U16 | 0.01 | Hz | Responds, unchecked | `meter_b_l3_frequency` | sensor | Disabled |
| `0xA066` | 1 | I16 | 1 | W | Verified | `meter_a_l1_power_high_word` | sensor | Disabled |
| `0xA067` | 1 | I16 | 1 | W | Verified | `meter_a_l2_power_high_word` | sensor | Disabled |
| `0xA068` | 1 | I16 | 1 | W | Verified | `meter_a_l3_power_high_word` | sensor | Disabled |
| `0xA069` | 1 | I16 | 1 | W | Responds, unchecked | `meter_b_l1_power_high_word` | sensor | Disabled |
| `0xA06A` | 1 | I16 | 1 | W | Responds, unchecked | `meter_b_l2_power_high_word` | sensor | Disabled |
| `0xA06B` | 1 | I16 | 1 | W | Responds, unchecked | `meter_b_l3_power_high_word` | sensor | Disabled |
| `0xA06C` | 2 | I32 | 1 | var | Verified | `meter_a_l1_reactive_power` | sensor | Disabled |
| `0xA06E` | 2 | I32 | 1 | var | Verified | `meter_a_l2_reactive_power` | sensor | Disabled |
| `0xA070` | 2 | I32 | 1 | var | Verified | `meter_a_l3_reactive_power` | sensor | Disabled |
| `0xA072` | 2 | I32 | 1 | var | Responds, unchecked | `meter_b_l1_reactive_power` | sensor | Disabled |
| `0xA074` | 2 | I32 | 1 | var | Responds, unchecked | `meter_b_l2_reactive_power` | sensor | Disabled |
| `0xA076` | 2 | I32 | 1 | var | Responds, unchecked | `meter_b_l3_reactive_power` | sensor | Disabled |

**Packed fields** — one register holding several values. The register is read once; each field is its own entity. All are created disabled.

| Register | Key | Field | Entity |
| --- | --- | --- | --- |
| `0x3604` | `charge_slot_1_enabled` | bit 0 | switch |
| `0x3604` | `charge_slot_2_enabled` | bit 1 | switch |
| `0x3604` | `charge_slot_3_enabled` | bit 2 | switch |
| `0x3604` | `charge_slot_4_enabled` | bit 3 | switch |
| `0x3604` | `charge_slot_5_enabled` | bit 4 | switch |
| `0x3604` | `charge_slot_6_enabled` | bit 5 | switch |
| `0x3604` | `charge_slot_7_enabled` | bit 6 | switch |
| `0x3605` | `discharge_slot_1_enabled` | bit 0 | switch |
| `0x3605` | `discharge_slot_2_enabled` | bit 1 | switch |
| `0x3605` | `discharge_slot_3_enabled` | bit 2 | switch |
| `0x3605` | `discharge_slot_4_enabled` | bit 3 | switch |
| `0x3605` | `discharge_slot_5_enabled` | bit 4 | switch |
| `0x3605` | `discharge_slot_6_enabled` | bit 5 | switch |
| `0x3605` | `discharge_slot_7_enabled` | bit 6 | switch |
| `0x3608` | `charge_slot_1_days` | bits 8–14, Monday first | number (0–127) |
| `0x3608` | `charge_slot_1_power` | bits 0–7, % of rated power | number (0–100) |
| `0x360B` | `charge_slot_2_days` | bits 8–14, Monday first | number (0–127) |
| `0x360B` | `charge_slot_2_power` | bits 0–7, % of rated power | number (0–100) |
| `0x360E` | `charge_slot_3_days` | bits 8–14, Monday first | number (0–127) |
| `0x360E` | `charge_slot_3_power` | bits 0–7, % of rated power | number (0–100) |
| `0x3611` | `charge_slot_4_days` | bits 8–14, Monday first | number (0–127) |
| `0x3611` | `charge_slot_4_power` | bits 0–7, % of rated power | number (0–100) |
| `0x3614` | `charge_slot_5_days` | bits 8–14, Monday first | number (0–127) |
| `0x3614` | `charge_slot_5_power` | bits 0–7, % of rated power | number (0–100) |
| `0x3617` | `charge_slot_6_days` | bits 8–14, Monday first | number (0–127) |
| `0x3617` | `charge_slot_6_power` | bits 0–7, % of rated power | number (0–100) |
| `0x361A` | `charge_slot_7_days` | bits 8–14, Monday first | number (0–127) |
| `0x361A` | `charge_slot_7_power` | bits 0–7, % of rated power | number (0–100) |
| `0x361D` | `discharge_slot_1_days` | bits 8–14, Monday first | number (0–127) |
| `0x361D` | `discharge_slot_1_power` | bits 0–7, % of rated power | number (0–100) |
| `0x3620` | `discharge_slot_2_days` | bits 8–14, Monday first | number (0–127) |
| `0x3620` | `discharge_slot_2_power` | bits 0–7, % of rated power | number (0–100) |
| `0x3623` | `discharge_slot_3_days` | bits 8–14, Monday first | number (0–127) |
| `0x3623` | `discharge_slot_3_power` | bits 0–7, % of rated power | number (0–100) |
| `0x3626` | `discharge_slot_4_days` | bits 8–14, Monday first | number (0–127) |
| `0x3626` | `discharge_slot_4_power` | bits 0–7, % of rated power | number (0–100) |
| `0x3629` | `discharge_slot_5_days` | bits 8–14, Monday first | number (0–127) |
| `0x3629` | `discharge_slot_5_power` | bits 0–7, % of rated power | number (0–100) |
| `0x362C` | `discharge_slot_6_days` | bits 8–14, Monday first | number (0–127) |
| `0x362C` | `discharge_slot_6_power` | bits 0–7, % of rated power | number (0–100) |
| `0x362F` | `discharge_slot_7_days` | bits 8–14, Monday first | number (0–127) |
| `0x362F` | `discharge_slot_7_power` | bits 0–7, % of rated power | number (0–100) |
| `0x4B22` | `ev_slot_1_mode` | bits 0–2 | select |
| `0x4B22` | `ev_slot_1_grid_charging` | bit 3 | switch |
| `0x4B22` | `ev_slot_1_battery_discharge` | bit 4 | switch |
| `0x4B22` | `ev_slot_1_days` | bits 8–14 | number (0–127) |
| `0x4B27` | `ev_slot_2_mode` | bits 0–2 | select |
| `0x4B27` | `ev_slot_2_grid_charging` | bit 3 | switch |
| `0x4B27` | `ev_slot_2_battery_discharge` | bit 4 | switch |
| `0x4B27` | `ev_slot_2_days` | bits 8–14 | number (0–127) |
| `0x4B2C` | `ev_slot_3_mode` | bits 0–2 | select |
| `0x4B2C` | `ev_slot_3_grid_charging` | bit 3 | switch |
| `0x4B2C` | `ev_slot_3_battery_discharge` | bit 4 | switch |
| `0x4B2C` | `ev_slot_3_days` | bits 8–14 | number (0–127) |
| `0x4B31` | `ev_slot_4_mode` | bits 0–2 | select |
| `0x4B31` | `ev_slot_4_grid_charging` | bit 3 | switch |
| `0x4B31` | `ev_slot_4_battery_discharge` | bit 4 | switch |
| `0x4B31` | `ev_slot_4_days` | bits 8–14 | number (0–127) |
| `0x4B36` | `ev_slot_5_mode` | bits 0–2 | select |
| `0x4B36` | `ev_slot_5_grid_charging` | bit 3 | switch |
| `0x4B36` | `ev_slot_5_battery_discharge` | bit 4 | switch |
| `0x4B36` | `ev_slot_5_days` | bits 8–14 | number (0–127) |
| `0x4B3B` | `ev_slot_6_mode` | bits 0–2 | select |
| `0x4B3B` | `ev_slot_6_grid_charging` | bit 3 | switch |
| `0x4B3B` | `ev_slot_6_battery_discharge` | bit 4 | switch |
| `0x4B3B` | `ev_slot_6_days` | bits 8–14 | number (0–127) |
| `0x4B40` | `ev_slot_7_mode` | bits 0–2 | select |
| `0x4B40` | `ev_slot_7_grid_charging` | bit 3 | switch |
| `0x4B40` | `ev_slot_7_battery_discharge` | bit 4 | switch |
| `0x4B40` | `ev_slot_7_days` | bits 8–14 | number (0–127) |
| `0x4B43` | `ev_minimum_current_charging` | bit 2 | switch |
| `0x8400` | `ems_inverter_control` | bit 0 | switch |
| `0x8400` | `ems_battery_control` | bit 1 | switch |
| `0x8400` | `ems_inverter_control_with_timeout_exit` | bit 3 | switch |
| `0x8400` | `ems_grid_control` | bit 5 | switch |

**Combined values** — one entity from several registers.

| Key | From | Unit | Evidence |
| --- | --- | --- | --- |
| `meter_a_power` | Sum of `meter_a_l<n>_power` over the device's phases | W | Verified: positive is import |
| `parallel_pv_power` | `0x4204` low word and `0x420C` high word as one signed 32-bit value | W | Responds, unchecked |
| `parallel_battery_power` | `0x4205` low word and `0x420D` high word as one signed 32-bit value | W | Responds, unchecked |
| `parallel_grid_power` | `0x4206` low word and `0x420E` high word as one signed 32-bit value | W | Responds, unchecked |
| `parallel_load_power` | `0x4207` low word and `0x420F` high word as one signed 32-bit value | W | Responds, unchecked |
| `parallel_backup_load_power` | `0x4208` low word and `0x4210` high word as one signed 32-bit value | W | Responds, unchecked |
| `parallel_grid_load_power` | `0x420A` low word and `0x4211` high word as one signed 32-bit value | W | Responds, unchecked |

### H2 Registers

**Settings** — 69 registers.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0x3604` | 1 | Bits | | | Implemented | — | Packed fields, see below | |
| `0x3605` | 1 | Bits | | | Implemented | — | Packed fields, see below | |
| `0x3606` | 1 | hh:mm | 1 |  | Implemented | `charge_slot_1_start` | time | Disabled |
| `0x3607` | 1 | hh:mm | 1 |  | Implemented | `charge_slot_1_end` | time | Disabled |
| `0x3608` | 1 | Bits | | | Implemented | — | Packed fields, see below | |
| `0x3609` | 1 | hh:mm | 1 |  | Implemented | `charge_slot_2_start` | time | Disabled |
| `0x360A` | 1 | hh:mm | 1 |  | Implemented | `charge_slot_2_end` | time | Disabled |
| `0x360B` | 1 | Bits | | | Implemented | — | Packed fields, see below | |
| `0x360C` | 1 | hh:mm | 1 |  | Implemented | `charge_slot_3_start` | time | Disabled |
| `0x360D` | 1 | hh:mm | 1 |  | Implemented | `charge_slot_3_end` | time | Disabled |
| `0x360E` | 1 | Bits | | | Implemented | — | Packed fields, see below | |
| `0x360F` | 1 | hh:mm | 1 |  | Implemented | `charge_slot_4_start` | time | Disabled |
| `0x3610` | 1 | hh:mm | 1 |  | Implemented | `charge_slot_4_end` | time | Disabled |
| `0x3611` | 1 | Bits | | | Implemented | — | Packed fields, see below | |
| `0x3612` | 1 | hh:mm | 1 |  | Implemented | `charge_slot_5_start` | time | Disabled |
| `0x3613` | 1 | hh:mm | 1 |  | Implemented | `charge_slot_5_end` | time | Disabled |
| `0x3614` | 1 | Bits | | | Implemented | — | Packed fields, see below | |
| `0x3615` | 1 | hh:mm | 1 |  | Implemented | `charge_slot_6_start` | time | Disabled |
| `0x3616` | 1 | hh:mm | 1 |  | Implemented | `charge_slot_6_end` | time | Disabled |
| `0x3617` | 1 | Bits | | | Implemented | — | Packed fields, see below | |
| `0x3618` | 1 | hh:mm | 1 |  | Implemented | `charge_slot_7_start` | time | Disabled |
| `0x3619` | 1 | hh:mm | 1 |  | Implemented | `charge_slot_7_end` | time | Disabled |
| `0x361A` | 1 | Bits | | | Implemented | — | Packed fields, see below | |
| `0x361B` | 1 | hh:mm | 1 |  | Implemented | `discharge_slot_1_start` | time | Disabled |
| `0x361C` | 1 | hh:mm | 1 |  | Implemented | `discharge_slot_1_end` | time | Disabled |
| `0x361D` | 1 | Bits | | | Implemented | — | Packed fields, see below | |
| `0x361E` | 1 | hh:mm | 1 |  | Implemented | `discharge_slot_2_start` | time | Disabled |
| `0x361F` | 1 | hh:mm | 1 |  | Implemented | `discharge_slot_2_end` | time | Disabled |
| `0x3620` | 1 | Bits | | | Implemented | — | Packed fields, see below | |
| `0x3621` | 1 | hh:mm | 1 |  | Implemented | `discharge_slot_3_start` | time | Disabled |
| `0x3622` | 1 | hh:mm | 1 |  | Implemented | `discharge_slot_3_end` | time | Disabled |
| `0x3623` | 1 | Bits | | | Implemented | — | Packed fields, see below | |
| `0x3624` | 1 | hh:mm | 1 |  | Implemented | `discharge_slot_4_start` | time | Disabled |
| `0x3625` | 1 | hh:mm | 1 |  | Implemented | `discharge_slot_4_end` | time | Disabled |
| `0x3626` | 1 | Bits | | | Implemented | — | Packed fields, see below | |
| `0x3627` | 1 | hh:mm | 1 |  | Implemented | `discharge_slot_5_start` | time | Disabled |
| `0x3628` | 1 | hh:mm | 1 |  | Implemented | `discharge_slot_5_end` | time | Disabled |
| `0x3629` | 1 | Bits | | | Implemented | — | Packed fields, see below | |
| `0x362A` | 1 | hh:mm | 1 |  | Implemented | `discharge_slot_6_start` | time | Disabled |
| `0x362B` | 1 | hh:mm | 1 |  | Implemented | `discharge_slot_6_end` | time | Disabled |
| `0x362C` | 1 | Bits | | | Implemented | — | Packed fields, see below | |
| `0x362D` | 1 | hh:mm | 1 |  | Implemented | `discharge_slot_7_start` | time | Disabled |
| `0x362E` | 1 | hh:mm | 1 |  | Implemented | `discharge_slot_7_end` | time | Disabled |
| `0x362F` | 1 | Bits | | | Implemented | — | Packed fields, see below | |
| `0x3630` | 1 | U16 | 1 |  | Documented | `meter_configuration` | select | Disabled |
| `0x3631` | 1 | U16 | 1 |  | Documented | `meter_address` | number (1–255) | Disabled |
| `0x3633` | 1 | U16 | 1 |  | Documented | `rs485_address` | number (1–127) | Disabled |
| `0x3634` | 1 | U16 | 1 |  | Documented | `rs485_baud_rate` | number (0–65535) | Disabled |
| `0x3636` | 1 | U16 | 1 |  | Implemented | `passive_mode` | number (0–2) | Disabled |
| `0x3637` | 1 | U16 | 0.1 | % | Implemented | `passive_grid_charge_power` | number (0–110) | Disabled |
| `0x3638` | 1 | U16 | 0.1 | % | Implemented | `passive_grid_discharge_power` | number (0–110) | Disabled |
| `0x3639` | 1 | U16 | 0.1 | % | Implemented | `passive_battery_charge_power` | number (0–110) | Disabled |
| `0x363A` | 1 | U16 | 0.1 | % | Implemented | `passive_battery_discharge_power` | number (0–110) | Disabled |
| `0x363B` | 1 | U16 | 1 |  | Documented | `battery_protocol` | select | Disabled |
| `0x3643` | 1 | U16 | 1 |  | Documented | `battery_auto_wake` | switch | Disabled |
| `0x3644` | 1 | U16 | 1 | % | Implemented | `battery_discharge_limit_on_grid` | number (0–100) | Core |
| `0x3645` | 1 | U16 | 1 | % | Implemented | `battery_discharge_limit_off_grid` | number (0–100) | Core |
| `0x3646` | 1 | U16 | 1 | % | Implemented | `battery_charge_limit` | number (0–100) | Core |
| `0x3647` | 1 | U16 | 1 |  | Implemented | `application_mode` | select | Core |
| `0x364D` | 1 | U16 | 0.1 | % | Implemented | `battery_charge_power_limit` | number (0–110) | Disabled |
| `0x364E` | 1 | U16 | 0.1 | % | Implemented | `battery_discharge_power_limit` | number (0–110) | Disabled |
| `0x364F` | 1 | U16 | 0.1 | % | Implemented | `grid_import_power_limit` | number (0–110) | Disabled |
| `0x3650` | 1 | U16 | 0.1 | % | Implemented | `grid_export_power_limit` | number (0–110) | Disabled |
| `0x3651` | 1 | U16 | 1 | % | Documented | `backup_reserve_soc` | number (0–100) | Disabled |
| `0x365A` | 1 | U16 | 0.1 | % | Implemented | `export_limit_power` | number (0–100) | Disabled |
| `0x365B` | 1 | U16 | 0.01 | A | Implemented | `export_limit_current` | number (0–3) | Disabled |
| `0x365C` | 1 | U16 | 1 |  | Implemented | `export_limit_mode` | select | Disabled |
| `0x365F` | 1 | U16 | 1 |  | Implemented | `time_of_use_idle_mode` | select | Disabled |
| `0x3660` | 1 | U16 | 1 |  | Implemented | `time_of_use_grid_discharge` | switch | Disabled |

**Realtime** — 123 registers.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0x4000` | 4 | Clock | 1 |  | Documented | `inverter_clock` | sensor (time) | Disabled |
| `0x4004` | 1 | U16 | 1 |  | Implemented | `operating_mode` | sensor | Core |
| `0x4005` | 2 | U32 | | | Implemented | — | Deferred — Faults: needs its fault table | |
| `0x4007` | 2 | U32 | | | Documented | — | Deferred — Faults: needs its fault table | |
| `0x4009` | 2 | U32 | | | Documented | — | Deferred — Faults: needs its fault table | |
| `0x400B` | 2 | U32 | | | Documented | — | Deferred — Faults: needs its fault table | |
| `0x4010` | 1 | I16 | 0.1 | °C | Implemented | `inverter_temperature` | sensor | Core |
| `0x4011` | 1 | I16 | 0.1 | °C | Implemented | `ambient_temperature` | sensor | Disabled |
| `0x4012` | 1 | U16 | 1 | mA | Implemented | `leakage_current` | sensor | Disabled |
| `0x4013` | 1 | U16 | 1 | kΩ | Implemented | `pv1_insulation_resistance` | sensor | Disabled |
| `0x4014` | 1 | U16 | 1 | kΩ | Implemented | `pv2_insulation_resistance` | sensor | Disabled |
| `0x4015` | 1 | U16 | 1 | kΩ | Implemented | `pv3_insulation_resistance` | sensor | Disabled; units with 3+ strings |
| `0x4016` | 1 | U16 | 1 | kΩ | Implemented | `pv4_insulation_resistance` | sensor | Disabled; units with 4+ strings |
| `0x4023` | 1 | I16 | 1 | W | Implemented | `inverter_discharge_power_setpoint` | sensor | Disabled |
| `0x4024` | 1 | I16 | 1 | W | Implemented | `inverter_charge_power_setpoint` | sensor | Disabled |
| `0x4025` | 1 | I16 | 0.1 | A | Implemented | `battery_discharge_current_setpoint` | sensor | Disabled |
| `0x4026` | 1 | I16 | 0.1 | A | Implemented | `battery_charge_current_setpoint` | sensor | Disabled |
| `0x4027` | 1 | U16 | 1 |  | Implemented | `battery_status_code` | sensor | Disabled |
| `0x4028` | 1 | I16 | 1 |  | Implemented | `battery_protocol_active` | sensor | Disabled |
| `0x4029` | 1 | I16 | 1 |  | Implemented | `battery_charge_limit_active` | sensor | Disabled |
| `0x402A` | 1 | I16 | 1 |  | Implemented | `battery_discharge_limit_active` | sensor | Disabled |
| `0x402B` | 1 | I16 | 1 |  | Implemented | `battery_depth_of_discharge_active` | sensor | Disabled |
| `0x402C` | 1 | I16 | 1 | % | Implemented | `backup_reserve_soc_active` | sensor | Disabled |
| `0x4030` | 1 | I16 | 1 |  | Implemented | `meter_configuration_active` | sensor | Disabled |
| `0x4031` | 1 | U16 | 0.1 | V | Implemented | `grid_l1_voltage` | sensor | Core |
| `0x4032` | 1 | I16 | 0.01 | A | Implemented | `grid_l1_current` | sensor | Disabled |
| `0x4033` | 1 | U16 | 0.01 | Hz | Implemented | `grid_l1_frequency` | sensor | Core |
| `0x4034` | 1 | I16 | 1 | mA | Implemented | `grid_l1_dc_current` | sensor | Disabled |
| `0x4035` | 1 | I16 | 1 | W | Implemented | `grid_l1_power` | sensor | Disabled |
| `0x4036` | 1 | U16 | 1 | VA | Implemented | `grid_l1_apparent_power` | sensor | Disabled |
| `0x4037` | 1 | I16 | 0.001 |  | Implemented | `grid_l1_power_factor` | sensor | Disabled |
| `0x4038` | 1 | U16 | 0.1 | V | Implemented | `grid_l2_voltage` | sensor | Core; 3-phase units only |
| `0x4039` | 1 | I16 | 0.01 | A | Implemented | `grid_l2_current` | sensor | Disabled; 3-phase units only |
| `0x403A` | 1 | U16 | 0.01 | Hz | Implemented | `grid_l2_frequency` | sensor | Disabled; 3-phase units only |
| `0x403B` | 1 | I16 | 1 | mA | Implemented | `grid_l2_dc_current` | sensor | Disabled; 3-phase units only |
| `0x403C` | 1 | I16 | 1 | W | Implemented | `grid_l2_power` | sensor | Disabled; 3-phase units only |
| `0x403D` | 1 | U16 | 1 | VA | Implemented | `grid_l2_apparent_power` | sensor | Disabled; 3-phase units only |
| `0x403E` | 1 | I16 | 0.001 |  | Implemented | `grid_l2_power_factor` | sensor | Disabled; 3-phase units only |
| `0x403F` | 1 | U16 | 0.1 | V | Implemented | `grid_l3_voltage` | sensor | Core; 3-phase units only |
| `0x4040` | 1 | I16 | 0.01 | A | Implemented | `grid_l3_current` | sensor | Disabled; 3-phase units only |
| `0x4041` | 1 | U16 | 0.01 | Hz | Implemented | `grid_l3_frequency` | sensor | Disabled; 3-phase units only |
| `0x4042` | 1 | I16 | 1 | mA | Implemented | `grid_l3_dc_current` | sensor | Disabled; 3-phase units only |
| `0x4043` | 1 | I16 | 1 | W | Implemented | `grid_l3_power` | sensor | Disabled; 3-phase units only |
| `0x4044` | 1 | U16 | 1 | VA | Implemented | `grid_l3_apparent_power` | sensor | Disabled; 3-phase units only |
| `0x4045` | 1 | I16 | 0.001 |  | Implemented | `grid_l3_power_factor` | sensor | Disabled; 3-phase units only |
| `0x4046` | 1 | U16 | 0.1 | V | Implemented | `inverter_l1_voltage` | sensor | Disabled |
| `0x4047` | 1 | I16 | 0.01 | A | Implemented | `inverter_l1_current` | sensor | Disabled |
| `0x4048` | 1 | U16 | 0.01 | Hz | Implemented | `inverter_l1_frequency` | sensor | Disabled |
| `0x4049` | 1 | I16 | 1 | W | Implemented | `inverter_l1_power` | sensor | Disabled |
| `0x404A` | 1 | U16 | 1 | VA | Implemented | `inverter_l1_apparent_power` | sensor | Disabled |
| `0x404B` | 1 | U16 | 0.1 | V | Implemented | `inverter_l2_voltage` | sensor | Disabled; 3-phase units only |
| `0x404C` | 1 | I16 | 0.01 | A | Implemented | `inverter_l2_current` | sensor | Disabled; 3-phase units only |
| `0x404D` | 1 | U16 | 0.01 | Hz | Implemented | `inverter_l2_frequency` | sensor | Disabled; 3-phase units only |
| `0x404E` | 1 | I16 | 1 | W | Implemented | `inverter_l2_power` | sensor | Disabled; 3-phase units only |
| `0x404F` | 1 | U16 | 1 | VA | Implemented | `inverter_l2_apparent_power` | sensor | Disabled; 3-phase units only |
| `0x4050` | 1 | U16 | 0.1 | V | Implemented | `inverter_l3_voltage` | sensor | Disabled; 3-phase units only |
| `0x4051` | 1 | I16 | 0.01 | A | Implemented | `inverter_l3_current` | sensor | Disabled; 3-phase units only |
| `0x4052` | 1 | U16 | 0.01 | Hz | Implemented | `inverter_l3_frequency` | sensor | Disabled; 3-phase units only |
| `0x4053` | 1 | I16 | 1 | W | Implemented | `inverter_l3_power` | sensor | Disabled; 3-phase units only |
| `0x4054` | 1 | U16 | 1 | VA | Implemented | `inverter_l3_apparent_power` | sensor | Disabled; 3-phase units only |
| `0x4055` | 1 | U16 | 0.1 | V | Implemented | `backup_l1_voltage` | sensor | Disabled |
| `0x4056` | 1 | U16 | 0.01 | A | Implemented | `backup_l1_current` | sensor | Disabled |
| `0x4057` | 1 | U16 | 0.01 | Hz | Implemented | `backup_l1_frequency` | sensor | Disabled |
| `0x4058` | 1 | I16 | 1 | mV | Implemented | `backup_l1_dc_voltage` | sensor | Disabled |
| `0x4059` | 1 | U16 | 1 | W | Implemented | `backup_l1_power` | sensor | Disabled |
| `0x405A` | 1 | U16 | 1 | VA | Implemented | `backup_l1_apparent_power` | sensor | Disabled |
| `0x405B` | 1 | U16 | 0.1 | V | Implemented | `backup_l2_voltage` | sensor | Disabled; 3-phase units only |
| `0x405C` | 1 | U16 | 0.01 | A | Implemented | `backup_l2_current` | sensor | Disabled; 3-phase units only |
| `0x405D` | 1 | U16 | 0.01 | Hz | Implemented | `backup_l2_frequency` | sensor | Disabled; 3-phase units only |
| `0x405E` | 1 | I16 | 1 | mV | Implemented | `backup_l2_dc_voltage` | sensor | Disabled; 3-phase units only |
| `0x405F` | 1 | U16 | 1 | W | Implemented | `backup_l2_power` | sensor | Disabled; 3-phase units only |
| `0x4060` | 1 | U16 | 1 | VA | Implemented | `backup_l2_apparent_power` | sensor | Disabled; 3-phase units only |
| `0x4061` | 1 | U16 | 0.1 | V | Implemented | `backup_l3_voltage` | sensor | Disabled; 3-phase units only |
| `0x4062` | 1 | U16 | 0.01 | A | Implemented | `backup_l3_current` | sensor | Disabled; 3-phase units only |
| `0x4063` | 1 | U16 | 0.01 | Hz | Implemented | `backup_l3_frequency` | sensor | Disabled; 3-phase units only |
| `0x4064` | 1 | I16 | 1 | mV | Implemented | `backup_l3_dc_voltage` | sensor | Disabled; 3-phase units only |
| `0x4065` | 1 | U16 | 1 | W | Implemented | `backup_l3_power` | sensor | Disabled; 3-phase units only |
| `0x4066` | 1 | U16 | 1 | VA | Implemented | `backup_l3_apparent_power` | sensor | Disabled; 3-phase units only |
| `0x4067` | 1 | U16 | 0.1 | V | Documented | `dc_bus_voltage` | sensor | Disabled |
| `0x4068` | 1 | U16 | 0.1 | V | Documented | `dc_bus_slave_voltage` | sensor | Disabled |
| `0x4069` | 1 | U16 | 0.1 | V | Documented | `battery_voltage` | sensor | Disabled |
| `0x406A` | 1 | I16 | 0.01 | A | Documented | `battery_current` | sensor | Disabled |
| `0x406D` | 1 | I16 | 1 | W | Documented | `battery_port_power` | sensor | Disabled |
| `0x406E` | 1 | I16 | 0.1 | °C | Implemented | `battery_temperature` | sensor | Core |
| `0x406F` | 1 | U16 | 0.01 | % | Implemented | `battery_soc` | sensor | Core |
| `0x4071` | 1 | U16 | 0.1 | V | Implemented | `pv1_voltage` | sensor | Core |
| `0x4072` | 1 | U16 | 0.01 | A | Implemented | `pv1_current` | sensor | Core |
| `0x4073` | 1 | U16 | 1 | W | Implemented | `pv1_power` | sensor | Core |
| `0x4074` | 1 | U16 | 0.1 | V | Implemented | `pv2_voltage` | sensor | Core |
| `0x4075` | 1 | U16 | 0.01 | A | Implemented | `pv2_current` | sensor | Core |
| `0x4076` | 1 | U16 | 1 | W | Implemented | `pv2_power` | sensor | Core |
| `0x4077` | 1 | U16 | 0.1 | V | Implemented | `pv3_voltage` | sensor | Core; units with 3+ strings |
| `0x4078` | 1 | U16 | 0.01 | A | Implemented | `pv3_current` | sensor | Core; units with 3+ strings |
| `0x4079` | 1 | U16 | 1 | W | Implemented | `pv3_power` | sensor | Core; units with 3+ strings |
| `0x407A` | 1 | U16 | 0.1 | V | Implemented | `pv4_voltage` | sensor | Core; units with 4+ strings |
| `0x407B` | 1 | U16 | 0.01 | A | Implemented | `pv4_current` | sensor | Core; units with 4+ strings |
| `0x407C` | 1 | U16 | 1 | W | Implemented | `pv4_power` | sensor | Core; units with 4+ strings |
| `0x408D` | 1 | U16 | 0.1 | V | Implemented | `grid_output_l1_voltage` | sensor | Disabled |
| `0x408E` | 1 | U16 | 0.01 | A | Implemented | `grid_output_l1_current` | sensor | Disabled |
| `0x408F` | 1 | U16 | 0.01 | Hz | Implemented | `grid_output_l1_frequency` | sensor | Disabled |
| `0x4090` | 1 | U16 | 1 | W | Implemented | `grid_output_l1_power` | sensor | Disabled |
| `0x4091` | 1 | U16 | 0.1 | V | Implemented | `grid_output_l2_voltage` | sensor | Disabled; 3-phase units only |
| `0x4092` | 1 | U16 | 1 | W | Implemented | `grid_output_l2_power` | sensor | Disabled; 3-phase units only |
| `0x4093` | 1 | U16 | 0.1 | V | Implemented | `grid_output_l3_voltage` | sensor | Disabled; 3-phase units only |
| `0x4094` | 1 | U16 | 1 | W | Implemented | `grid_output_l3_power` | sensor | Disabled; 3-phase units only |
| `0x4095` | 1 | U16 | 1 |  | Implemented | `pv_direction` | sensor | Disabled |
| `0x4096` | 1 | I16 | 1 |  | Implemented | `battery_direction` | sensor | Disabled |
| `0x4097` | 1 | I16 | 1 |  | Implemented | `grid_direction` | sensor | Disabled |
| `0x4098` | 1 | U16 | 1 |  | Implemented | `output_direction` | sensor | Disabled |
| `0x40A0` | 1 | I16 | 1 | W | Implemented | `load_power` | sensor | Core |
| `0x40A1` | 1 | I16 | 1 | W | Implemented | `ct_grid_power` | sensor | Disabled |
| `0x40A2` | 1 | I16 | 1 | VA | Implemented | `ct_grid_apparent_power` | sensor | Disabled |
| `0x40A3` | 1 | I16 | 1 | W | Implemented | `ct_pv_power` | sensor | Disabled |
| `0x40A4` | 1 | I16 | 1 | VA | Implemented | `ct_pv_apparent_power` | sensor | Disabled |
| `0x40A5` | 1 | I16 | 1 | W | Implemented | `pv_power` | sensor | Core |
| `0x40A6` | 1 | I16 | 1 | W | Implemented | `battery_power` | sensor | Core |
| `0x40A7` | 1 | I16 | 1 | W | Implemented | `grid_power` | sensor | Core |
| `0x40A8` | 1 | I16 | 1 | VA | Implemented | `grid_apparent_power` | sensor | Disabled |
| `0x40A9` | 1 | I16 | 1 | W | Implemented | `inverter_power` | sensor | Core |
| `0x40AA` | 1 | I16 | 1 | VA | Implemented | `inverter_apparent_power` | sensor | Disabled |
| `0x40AB` | 1 | U16 | 1 | W | Implemented | `backup_load_power` | sensor | Core |
| `0x40AC` | 1 | U16 | 1 | VA | Implemented | `backup_load_apparent_power` | sensor | Disabled |
| `0x40AD` | 1 | I16 | 1 | W | Implemented | `grid_load_power` | sensor | Disabled |

**Energy counters** — 64 registers.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0x40BF` | 2 | U32 | 0.01 | kWh | Implemented | `pv_energy_today` | sensor | Core |
| `0x40C1` | 2 | U32 | 0.01 | kWh | Implemented | `pv_energy_month` | sensor | Disabled |
| `0x40C3` | 2 | U32 | 0.01 | kWh | Implemented | `pv_energy_year` | sensor | Disabled |
| `0x40C5` | 2 | U32 | 0.01 | kWh | Implemented | `pv_energy_total` | sensor | Core |
| `0x40C7` | 2 | U32 | 0.01 | kWh | Implemented | `battery_charge_energy_today` | sensor | Core |
| `0x40C9` | 2 | U32 | 0.01 | kWh | Implemented | `battery_charge_energy_month` | sensor | Disabled |
| `0x40CB` | 2 | U32 | 0.01 | kWh | Implemented | `battery_charge_energy_year` | sensor | Disabled |
| `0x40CD` | 2 | U32 | 0.01 | kWh | Implemented | `battery_charge_energy_total` | sensor | Core |
| `0x40CF` | 2 | U32 | 0.01 | kWh | Implemented | `battery_discharge_energy_today` | sensor | Core |
| `0x40D1` | 2 | U32 | 0.01 | kWh | Implemented | `battery_discharge_energy_month` | sensor | Disabled |
| `0x40D3` | 2 | U32 | 0.01 | kWh | Implemented | `battery_discharge_energy_year` | sensor | Disabled |
| `0x40D5` | 2 | U32 | 0.01 | kWh | Implemented | `battery_discharge_energy_total` | sensor | Core |
| `0x40D7` | 2 | U32 | 0.01 | kWh | Implemented | `inverter_energy_today` | sensor | Disabled |
| `0x40D9` | 2 | U32 | 0.01 | kWh | Implemented | `inverter_energy_month` | sensor | Disabled |
| `0x40DB` | 2 | U32 | 0.01 | kWh | Implemented | `inverter_energy_year` | sensor | Disabled |
| `0x40DD` | 2 | U32 | 0.01 | kWh | Implemented | `inverter_energy_total` | sensor | Disabled |
| `0x40DF` | 2 | U32 | 0.01 | kWh | Implemented | `load_energy_today` | sensor | Core |
| `0x40E1` | 2 | U32 | 0.01 | kWh | Implemented | `load_energy_month` | sensor | Disabled |
| `0x40E3` | 2 | U32 | 0.01 | kWh | Implemented | `load_energy_year` | sensor | Disabled |
| `0x40E5` | 2 | U32 | 0.01 | kWh | Implemented | `load_energy_total` | sensor | Core |
| `0x40E7` | 2 | U32 | 0.01 | kWh | Implemented | `backup_load_energy_today` | sensor | Core |
| `0x40E9` | 2 | U32 | 0.01 | kWh | Implemented | `backup_load_energy_month` | sensor | Disabled |
| `0x40EB` | 2 | U32 | 0.01 | kWh | Implemented | `backup_load_energy_year` | sensor | Disabled |
| `0x40ED` | 2 | U32 | 0.01 | kWh | Implemented | `backup_load_energy_total` | sensor | Core |
| `0x40EF` | 2 | U32 | 0.01 | kWh | Implemented | `grid_export_energy_today` | sensor | Core |
| `0x40F1` | 2 | U32 | 0.01 | kWh | Implemented | `grid_export_energy_month` | sensor | Disabled |
| `0x40F3` | 2 | U32 | 0.01 | kWh | Implemented | `grid_export_energy_year` | sensor | Disabled |
| `0x40F5` | 2 | U32 | 0.01 | kWh | Implemented | `grid_export_energy_total` | sensor | Core |
| `0x40F7` | 2 | U32 | 0.01 | kWh | Implemented | `grid_import_energy_today` | sensor | Core |
| `0x40F9` | 2 | U32 | 0.01 | kWh | Implemented | `grid_import_energy_month` | sensor | Disabled |
| `0x40FB` | 2 | U32 | 0.01 | kWh | Implemented | `grid_import_energy_year` | sensor | Disabled |
| `0x40FD` | 2 | U32 | 0.01 | kWh | Implemented | `grid_import_energy_total` | sensor | Core |
| `0x4137` | 2 | U32 | 0.01 | kWh | Implemented | `pv2_energy_today` | sensor | Disabled |
| `0x4139` | 2 | U32 | 0.01 | kWh | Implemented | `pv2_energy_month` | sensor | Disabled |
| `0x413B` | 2 | U32 | 0.01 | kWh | Implemented | `pv2_energy_year` | sensor | Disabled |
| `0x413D` | 2 | U32 | 0.01 | kWh | Implemented | `pv2_energy_total` | sensor | Disabled |
| `0x413F` | 2 | U32 | 0.01 | kWh | Implemented | `pv3_energy_today` | sensor | Disabled; units with 3+ strings |
| `0x4141` | 2 | U32 | 0.01 | kWh | Implemented | `pv3_energy_month` | sensor | Disabled; units with 3+ strings |
| `0x4143` | 2 | U32 | 0.01 | kWh | Implemented | `pv3_energy_year` | sensor | Disabled; units with 3+ strings |
| `0x4145` | 2 | U32 | 0.01 | kWh | Implemented | `pv3_energy_total` | sensor | Disabled; units with 3+ strings |
| `0x4147` | 2 | U32 | 0.01 | kWh | Implemented | `grid_l2_export_energy_today` | sensor | Disabled; 3-phase units only |
| `0x4149` | 2 | U32 | 0.01 | kWh | Implemented | `grid_l2_export_energy_month` | sensor | Disabled; 3-phase units only |
| `0x414B` | 2 | U32 | 0.01 | kWh | Implemented | `grid_l2_export_energy_year` | sensor | Disabled; 3-phase units only |
| `0x414D` | 2 | U32 | 0.01 | kWh | Implemented | `grid_l2_export_energy_total` | sensor | Disabled; 3-phase units only |
| `0x414F` | 2 | U32 | 0.01 | kWh | Implemented | `grid_l3_export_energy_today` | sensor | Disabled; 3-phase units only |
| `0x4151` | 2 | U32 | 0.01 | kWh | Implemented | `grid_l3_export_energy_month` | sensor | Disabled; 3-phase units only |
| `0x4153` | 2 | U32 | 0.01 | kWh | Implemented | `grid_l3_export_energy_year` | sensor | Disabled; 3-phase units only |
| `0x4155` | 2 | U32 | 0.01 | kWh | Implemented | `grid_l3_export_energy_total` | sensor | Disabled; 3-phase units only |
| `0x4157` | 2 | U32 | 0.01 | kWh | Implemented | `grid_l2_import_energy_today` | sensor | Disabled; 3-phase units only |
| `0x4159` | 2 | U32 | 0.01 | kWh | Implemented | `grid_l2_import_energy_month` | sensor | Disabled; 3-phase units only |
| `0x415B` | 2 | U32 | 0.01 | kWh | Implemented | `grid_l2_import_energy_year` | sensor | Disabled; 3-phase units only |
| `0x415D` | 2 | U32 | 0.01 | kWh | Implemented | `grid_l2_import_energy_total` | sensor | Disabled; 3-phase units only |
| `0x415F` | 2 | U32 | 0.01 | kWh | Implemented | `grid_l3_import_energy_today` | sensor | Disabled; 3-phase units only |
| `0x4161` | 2 | U32 | 0.01 | kWh | Implemented | `grid_l3_import_energy_month` | sensor | Disabled; 3-phase units only |
| `0x4163` | 2 | U32 | 0.01 | kWh | Implemented | `grid_l3_import_energy_year` | sensor | Disabled; 3-phase units only |
| `0x4165` | 2 | U32 | 0.01 | kWh | Implemented | `grid_l3_import_energy_total` | sensor | Disabled; 3-phase units only |
| `0x4167` | 2 | U32 | | | Implemented | — | Deferred — H2 coverage: read by the existing H2 implementation, absent from the H2 document; relation to `0x40EF`/`0x40F7` on a single-phase unit unknown | |
| `0x4169` | 2 | U32 | | | Implemented | — | Deferred — H2 coverage: read by the existing H2 implementation, absent from the H2 document; relation to `0x40EF`/`0x40F7` on a single-phase unit unknown | |
| `0x416B` | 2 | U32 | | | Implemented | — | Deferred — H2 coverage: read by the existing H2 implementation, absent from the H2 document; relation to `0x40EF`/`0x40F7` on a single-phase unit unknown | |
| `0x416D` | 2 | U32 | | | Implemented | — | Deferred — H2 coverage: read by the existing H2 implementation, absent from the H2 document; relation to `0x40EF`/`0x40F7` on a single-phase unit unknown | |
| `0x416F` | 2 | U32 | | | Implemented | — | Deferred — H2 coverage: read by the existing H2 implementation, absent from the H2 document; relation to `0x40EF`/`0x40F7` on a single-phase unit unknown | |
| `0x4171` | 2 | U32 | | | Implemented | — | Deferred — H2 coverage: read by the existing H2 implementation, absent from the H2 document; relation to `0x40EF`/`0x40F7` on a single-phase unit unknown | |
| `0x4173` | 2 | U32 | | | Implemented | — | Deferred — H2 coverage: read by the existing H2 implementation, absent from the H2 document; relation to `0x40EF`/`0x40F7` on a single-phase unit unknown | |
| `0x4175` | 2 | U32 | | | Implemented | — | Deferred — H2 coverage: read by the existing H2 implementation, absent from the H2 document; relation to `0x40EF`/`0x40F7` on a single-phase unit unknown | |

**Commands** — 5 registers.

The same five write-only command registers as the HS3 Commands block above, `0x8015`, `0x801A`–`0x801C` and `0x8020` (four words), all Documented and all Deferred — Writes: write-only command.

**Identity and versions** — 11 registers.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0x8F00` | 1 | U16 | | | Implemented | — | Deferred — Not an entity: read by identity and shown on the device | |
| `0x8F01` | 1 | U16 | | | Implemented | — | Deferred — Not an entity: read by identity and shown on the device | |
| `0x8F02` | 1 | U16 | 0.001 |  | Implemented | `protocol_version` | sensor | Disabled |
| `0x8F03` | 10 | Text | | | Implemented | — | Deferred — Not an entity: read by identity and shown on the device | |
| `0x8F0D` | 10 | Text | 1 |  | Implemented | `product_code` | sensor (text) | Disabled |
| `0x8F17` | 1 | U16 | 0.001 |  | Implemented | `display_software_version` | sensor | Disabled |
| `0x8F18` | 1 | U16 | 0.001 |  | Implemented | `master_software_version` | sensor | Disabled |
| `0x8F19` | 1 | U16 | 0.001 |  | Implemented | `slave_software_version` | sensor | Disabled |
| `0x8F1A` | 1 | U16 | 0.001 |  | Implemented | `display_hardware_version` | sensor | Disabled |
| `0x8F1B` | 1 | U16 | 0.001 |  | Implemented | `control_hardware_version` | sensor | Disabled |
| `0x8F1C` | 1 | U16 | 0.001 |  | Implemented | `power_hardware_version` | sensor | Disabled |

**Battery packs** — 46 registers.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0xA000` | 1 | U16 | 1 |  | Implemented | `battery_pack_count` | sensor | Disabled |
| `0xA001` | 1 | U16 | 1 |  | Implemented | `battery_capacity` | sensor | Disabled |
| `0xA002` | 1 | U16 | | | Implemented | — | Deferred — Faults: needs its fault table | |
| `0xA003` | 1 | U16 | | | Implemented | — | Deferred — Faults: needs its fault table | |
| `0xA004` | 1 | U16 | | | Implemented | — | Deferred — Faults: needs its fault table | |
| `0xA005` | 1 | U16 | | | Implemented | — | Deferred — Faults: needs its fault table | |
| `0xA006` | 1 | U16 | | | Implemented | — | Deferred — Faults: needs its fault table | |
| `0xA007` | 1 | U16 | | | Implemented | — | Deferred — Faults: needs its fault table | |
| `0xA008` | 1 | U16 | | | Implemented | — | Deferred — Faults: needs its fault table | |
| `0xA009` | 1 | U16 | | | Implemented | — | Deferred — Faults: needs its fault table | |
| `0xA00A` | 1 | U16 | 1 |  | Implemented | `battery_usable_capacity` | sensor | Disabled |
| `0xA00B` | 1 | U16 | 1 |  | Implemented | `battery_online_code` | sensor | Disabled |
| `0xA00C` | 1 | U16 | 0.01 | % | Implemented | `battery_pack1_soc` | sensor | Disabled |
| `0xA00D` | 1 | U16 | 0.01 | % | Implemented | `battery_pack1_soh` | sensor | Disabled |
| `0xA00E` | 1 | U16 | 0.1 | V | Implemented | `battery_pack1_voltage` | sensor | Disabled |
| `0xA00F` | 1 | I16 | 0.01 | A | Implemented | `battery_pack1_current` | sensor | Disabled |
| `0xA010` | 1 | I16 | 0.1 | °C | Implemented | `battery_pack1_temperature` | sensor | Disabled |
| `0xA011` | 1 | U16 | 1 |  | Implemented | `battery_pack1_cycles` | sensor | Disabled |
| `0xA012` | 1 | U16 | 0.01 | % | Implemented | `battery_pack2_soc` | sensor | Disabled |
| `0xA013` | 1 | U16 | 0.01 | % | Implemented | `battery_pack2_soh` | sensor | Disabled |
| `0xA014` | 1 | U16 | 0.1 | V | Implemented | `battery_pack2_voltage` | sensor | Disabled |
| `0xA015` | 1 | I16 | 0.01 | A | Implemented | `battery_pack2_current` | sensor | Disabled |
| `0xA016` | 1 | I16 | 0.1 | °C | Implemented | `battery_pack2_temperature` | sensor | Disabled |
| `0xA017` | 1 | U16 | 1 |  | Implemented | `battery_pack2_cycles` | sensor | Disabled |
| `0xA018` | 1 | U16 | 0.01 | % | Implemented | `battery_pack3_soc` | sensor | Disabled |
| `0xA019` | 1 | U16 | 0.01 | % | Implemented | `battery_pack3_soh` | sensor | Disabled |
| `0xA01A` | 1 | U16 | 0.1 | V | Implemented | `battery_pack3_voltage` | sensor | Disabled |
| `0xA01B` | 1 | I16 | 0.01 | A | Implemented | `battery_pack3_current` | sensor | Disabled |
| `0xA01C` | 1 | I16 | 0.1 | °C | Implemented | `battery_pack3_temperature` | sensor | Disabled |
| `0xA01D` | 1 | U16 | 1 |  | Implemented | `battery_pack3_cycles` | sensor | Disabled |
| `0xA01E` | 1 | U16 | 0.01 | % | Implemented | `battery_pack4_soc` | sensor | Disabled |
| `0xA01F` | 1 | U16 | 0.01 | % | Implemented | `battery_pack4_soh` | sensor | Disabled |
| `0xA020` | 1 | U16 | 0.1 | V | Implemented | `battery_pack4_voltage` | sensor | Disabled |
| `0xA021` | 1 | I16 | 0.01 | A | Implemented | `battery_pack4_current` | sensor | Disabled |
| `0xA022` | 1 | I16 | 0.1 | °C | Implemented | `battery_pack4_temperature` | sensor | Disabled |
| `0xA023` | 1 | U16 | 1 |  | Implemented | `battery_pack4_cycles` | sensor | Disabled |
| `0xA02A` | 2 | U32 | 1 | kWh | Implemented | `battery_pack1_discharged_energy` | sensor | Disabled |
| `0xA02C` | 2 | U32 | 1 | kWh | Implemented | `battery_pack2_discharged_energy` | sensor | Disabled |
| `0xA02E` | 2 | U32 | 1 | kWh | Implemented | `battery_pack3_discharged_energy` | sensor | Disabled |
| `0xA030` | 2 | U32 | 1 | kWh | Implemented | `battery_pack4_discharged_energy` | sensor | Disabled |
| `0xA032` | 1 | U16 | 0.1 | V | Implemented | `battery_voltage_high_protection` | sensor | Disabled |
| `0xA033` | 1 | U16 | | | Implemented | — | Deferred — Faults: needs its fault table | |
| `0xA034` | 1 | U16 | 0.1 | V | Implemented | `battery_charge_voltage` | sensor | Disabled |
| `0xA035` | 1 | U16 | 0.1 | V | Implemented | `battery_discharge_cutoff_voltage` | sensor | Disabled |
| `0xA036` | 1 | U16 | 0.1 | A | Implemented | `battery_discharge_current_limit` | sensor | Disabled |
| `0xA037` | 1 | U16 | 0.1 | A | Implemented | `battery_charge_current_limit` | sensor | Disabled |

**Meters** — 38 registers.

| Address | Words | Encoding | Scale | Unit | Evidence | Key | Entity | Default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0xA03C` | 1 | U16 | 1 |  | Documented | `meter_a_status` | sensor (enum) | Disabled |
| `0xA03D` | 1 | U16 | 0.1 | V | Implemented | `meter_a_l1_voltage` | sensor | Disabled |
| `0xA03E` | 1 | I16 | 0.01 | A | Implemented | `meter_a_l1_current` | sensor | Disabled |
| `0xA03F` | 1 | I16 | 1 | W | Implemented | `meter_a_l1_power` | sensor | Disabled |
| `0xA040` | 1 | U16 | 1 | VA | Implemented | `meter_a_l1_apparent_power` | sensor | Disabled |
| `0xA041` | 1 | I16 | 0.001 |  | Implemented | `meter_a_l1_power_factor` | sensor | Disabled |
| `0xA042` | 1 | U16 | 0.01 | Hz | Implemented | `meter_a_l1_frequency` | sensor | Disabled |
| `0xA043` | 1 | U16 | 0.1 | V | Implemented | `meter_a_l2_voltage` | sensor | Disabled; 3-phase units only |
| `0xA044` | 1 | I16 | 0.01 | A | Implemented | `meter_a_l2_current` | sensor | Disabled; 3-phase units only |
| `0xA045` | 1 | I16 | 1 | W | Implemented | `meter_a_l2_power` | sensor | Disabled; 3-phase units only |
| `0xA046` | 1 | U16 | 1 | VA | Implemented | `meter_a_l2_apparent_power` | sensor | Disabled; 3-phase units only |
| `0xA047` | 1 | I16 | 0.001 |  | Implemented | `meter_a_l2_power_factor` | sensor | Disabled; 3-phase units only |
| `0xA048` | 1 | U16 | 0.01 | Hz | Implemented | `meter_a_l2_frequency` | sensor | Disabled; 3-phase units only |
| `0xA049` | 1 | U16 | 0.1 | V | Implemented | `meter_a_l3_voltage` | sensor | Disabled; 3-phase units only |
| `0xA04A` | 1 | I16 | 0.01 | A | Implemented | `meter_a_l3_current` | sensor | Disabled; 3-phase units only |
| `0xA04B` | 1 | I16 | 1 | W | Implemented | `meter_a_l3_power` | sensor | Disabled; 3-phase units only |
| `0xA04C` | 1 | U16 | 1 | VA | Implemented | `meter_a_l3_apparent_power` | sensor | Disabled; 3-phase units only |
| `0xA04D` | 1 | I16 | 0.001 |  | Implemented | `meter_a_l3_power_factor` | sensor | Disabled; 3-phase units only |
| `0xA04E` | 1 | U16 | 0.01 | Hz | Implemented | `meter_a_l3_frequency` | sensor | Disabled; 3-phase units only |
| `0xA053` | 1 | U16 | 1 |  | Documented | `meter_b_status` | sensor (enum) | Disabled |
| `0xA054` | 1 | U16 | 0.1 | V | Documented | `meter_b_l1_voltage` | sensor | Disabled |
| `0xA055` | 1 | I16 | 0.01 | A | Documented | `meter_b_l1_current` | sensor | Disabled |
| `0xA056` | 1 | I16 | 1 | W | Documented | `meter_b_l1_power` | sensor | Disabled |
| `0xA057` | 1 | U16 | 1 | VA | Documented | `meter_b_l1_apparent_power` | sensor | Disabled |
| `0xA058` | 1 | I16 | 0.001 |  | Documented | `meter_b_l1_power_factor` | sensor | Disabled |
| `0xA059` | 1 | U16 | 0.01 | Hz | Documented | `meter_b_l1_frequency` | sensor | Disabled |
| `0xA05A` | 1 | U16 | 0.1 | V | Documented | `meter_b_l2_voltage` | sensor | Disabled; 3-phase units only |
| `0xA05B` | 1 | I16 | 0.01 | A | Documented | `meter_b_l2_current` | sensor | Disabled; 3-phase units only |
| `0xA05C` | 1 | I16 | 1 | W | Documented | `meter_b_l2_power` | sensor | Disabled; 3-phase units only |
| `0xA05D` | 1 | U16 | 1 | VA | Documented | `meter_b_l2_apparent_power` | sensor | Disabled; 3-phase units only |
| `0xA05E` | 1 | I16 | 0.001 |  | Documented | `meter_b_l2_power_factor` | sensor | Disabled; 3-phase units only |
| `0xA05F` | 1 | U16 | 0.01 | Hz | Documented | `meter_b_l2_frequency` | sensor | Disabled; 3-phase units only |
| `0xA060` | 1 | U16 | 0.1 | V | Documented | `meter_b_l3_voltage` | sensor | Disabled; 3-phase units only |
| `0xA061` | 1 | I16 | 0.01 | A | Documented | `meter_b_l3_current` | sensor | Disabled; 3-phase units only |
| `0xA062` | 1 | I16 | 1 | W | Documented | `meter_b_l3_power` | sensor | Disabled; 3-phase units only |
| `0xA063` | 1 | U16 | 1 | VA | Documented | `meter_b_l3_apparent_power` | sensor | Disabled; 3-phase units only |
| `0xA064` | 1 | I16 | 0.001 |  | Documented | `meter_b_l3_power_factor` | sensor | Disabled; 3-phase units only |
| `0xA065` | 1 | U16 | 0.01 | Hz | Documented | `meter_b_l3_frequency` | sensor | Disabled; 3-phase units only |

### Options And Enumerations

| Key | Values |
| --- | --- |
| `operating_mode` | 0 initialisation, 1 standby, 2 operating, 3 off-grid, 4 grid-connected load / bypass, 5 fault, 6 upgrade, 7 debugging, 8 self-check, 9 reset |
| `application_mode` | 0 self-use, 1 time-of-use, 2 backup; HS3 also 6 EMS; H2 also 3 passive and 14 legacy |
| `export_limit_mode` | 0 off, 1 total power, 2 phase current, 3 phase power |
| `time_of_use_idle_mode` | 0 standby, 1 self-use |
| `led_mode` | 0 all off, 1 outer ring on, 2 inner ring on, 3 all on |
| `battery_protocol` | 0 battery not in use, 24 SAJ BU3 |
| `meter_configuration` | 0 no meter or CT, 1 single-phase meter, 2 three-phase three-wire meter, 3 three-phase four-wire meter on a single-phase machine, 10 three-phase four-wire meter in grid and PV arrangement, 11 two three-phase three-wire meters, 12 two three-phase four-wire meters, 13 two single-phase meters, 15 one single-phase meter with two CT channels, 20 one grid CT, 21 grid and PV CTs, 42 one dual-circuit three-phase four-wire meter with six CT channels |
| `rs485_slave_baud_rate`, `ev_baud_rate` | 0 115200, 1 57600, 2 38400, 3 19200, 4 9600, 5 4800, 6 2400, 7 1200 |
| `meter_a_status`, `meter_b_status` | 0 offline, 1 online |
| `ethernet_mode` | 0 manual, 1 automatic (DHCP) |
| `ev_mode`, `ev_work_mode` | 0 disabled, 1 standard (forced charging), 2 time-based, 3 PV surplus, 4 EMS |
| `ev_status` | 1 idle, 2 ready, 3 charging, 4 charger suspended, 5 vehicle suspended, 6 complete |
| `ev_remote_control` | 0 shutdown, 1 on |
| `ev_port_mode` | 0 invalid, 1 host, 2 Modbus slave |
| `ev_slot_<n>_mode` | 0 not set, 1 standard (forced on), 2 PV mode |

The H2 schedule registers `0x3604`–`0x362F` pack their fields exactly as the HS3 ones do, so the charge and discharge rows of the packed-fields table apply to both models. The EV and EMS rows of that table are HS3 only.

Of the combined values, `meter_a_power` also exists on H2, as the sum of the Meter A phase powers the device has. Its evidence there is Documented, so it is created disabled.

## Revisions

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-08 | First draft. |
| 2 | 2026-10-09 | Corrected after implementation review: the HS3 default read is 9 requests and 15 a minute with the power group, not 10 and 16. `meter_a_power` is listed for H2. H2 battery pack 2 to 4 discharged energy is in kWh. The planned-load functions live in `saj/load.py`. An insulation resistance of 32767 kΩ is shown as read. The cost of narrowing is restated. The polling-group form lists disabled entities, marked as disabled. |
