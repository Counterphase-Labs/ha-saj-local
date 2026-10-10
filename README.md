# SAJ Local Home Assistant Integration

![SAJ Local](images/header.png)

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz)
[![Home Assistant](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fdogmatic69%2Fhome-assistant-saj-modbus%2Fmain%2Fhacs.json&query=%24.homeassistant&suffix=%2B&label=Home%20Assistant&logo=homeassistant&logoColor=white&color=41BDF5)](https://www.home-assistant.io)
[![Release](https://img.shields.io/github/v/release/dogmatic69/home-assistant-saj-modbus)](https://github.com/dogmatic69/home-assistant-saj-modbus/releases)
[![Active installs](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fanalytics.home-assistant.io%2Fcustom_integrations.json&query=%24.saj_local.total&label=active%20installs&logo=homeassistant&logoColor=white&color=41BDF5)](https://analytics.home-assistant.io)
[![CI](https://github.com/dogmatic69/home-assistant-saj-modbus/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/dogmatic69/home-assistant-saj-modbus/actions/workflows/ci.yml)
[![Licence](https://img.shields.io/github/license/dogmatic69/home-assistant-saj-modbus)](LICENSE)

⭐ [Star the project on GitHub](https://github.com/dogmatic69/home-assistant-saj-modbus): your support is a real motivation! 🙏😊

Your SAJ solar system in Home Assistant, read straight from the inverter over your own network. No cloud account, no vendor app in the middle, and a polling approach designed to be gentle on the hardware.

This is an unofficial, community-built integration. It is not made, supported or endorsed by SAJ. See the [disclaimer](#disclaimer).

> **Status: in active development and not yet released.** The current iteration reads every register it knows for one or more SAJ HS3 or H2 inverters over local Modbus TCP and shows settings with their current value. Once you switch on **Allow control** in setup or Configure, the settings can be changed from Home Assistant. There is no published release yet.

## What it is being built to deliver

### Works the way you expect

- **Sensible by default.** Add your inverter and get a working setup without wading through pages of options.
- **Finds your system for you.** The inverter, battery and related equipment are detected automatically, with an override when you know better.
- **Consistent entity names across SAJ models.** Dashboards and automations are written once and keep working across models.
- **Survives hardware upgrades.** Moving from an H2 to an HS3, for example, keeps your history continuous where the systems overlap, such as total PV power. Sensors that no longer apply, such as a battery you no longer have, simply go away.
- **Multiple systems.** Connect more than one SAJ system to the same Home Assistant.

### Gentle on your inverter

- **Careful Modbus access.** One connection per inverter, one request at a time, and a hard ceiling of 40 requests in any 60 seconds per inverter address that no setting, reload or failure can exceed, with particular care for AIO3 systems.
- **You choose what is read.** Only a small core set is enabled by default and the rest is created disabled. Disable an entity in Home Assistant and its register is no longer read; enable one and it joins the next cycle.
- **Update cadences you control.** Set a default refresh rate and create polling groups that read selected entities faster or slower, with the request load shown before you save.

### Read, and when you want it, write

- **Read-only unless you say otherwise.** Writing is opt-in per installation, so nothing changes on your inverter by accident. Until you switch on **Allow control**, settings are shown as their real control type but refuse every change with a message saying where to switch control on, and nothing is sent to the inverter. See [Changing settings](#changing-settings).

### Lovelace cards

- **Dashboard cards** you can add to your own dashboards, both for viewing information and for changing configuration.

### Easy to live with

- **Fully localised.** The interface is built for translation from the start.
- **Clear errors.** When something goes wrong you are told what and why, rather than left with a silent failure.
- **Privacy-focused diagnostics.** Debug dumps use Home Assistant's own tools and are built to be safe to share. Optional debug logging is meant to be useful, not noisy.
- **Fully local.** Everything talks to your inverter over your network. Nothing is sent to a cloud service.

## Supported equipment

The goal is wide coverage of common SAJ household inverters, batteries and related equipment. The SAJ HS3 is the development reference system and the H2 is supported at the same level.

| Product | Sensors | Controls | PV | Battery | Grid meter | Second meter | EV charger | Parallel inverters | Off-grid |
| ------- | :-----: | :------: | :-: | :-----: | :--------: | :----------: | :--------: | :----------------: | :------: |
| HS3 all-in-one | ✅ | ❌ | ✅ | ✅ | – | – | – | – | – |
| HS2 all-in-one | – | – | – | – | – | – | – | – | – |
| H2 single-phase, 3–6 kW | ✅ | ❌ | ✅ | ✅ | – | ❌ | ❌ | ❌ | – |
| H2 single-phase, 5–10 kW | ✅ | ❌ | ✅ | ✅ | – | – | – | – | – |
| H2 single-phase low voltage, 5–12 kW | – | – | – | – | – | – | – | – | – |
| H2 three-phase | – | – | – | – | – | – | – | – | – |
| H1 hybrid | – | – | – | – | – | – | – | – | – |
| AS1 AC-coupled | – | – | ❌ | – | – | – | – | – | – |
| R6 on-grid | – | – | – | ❌ | – | – | – | – | ❌ |
| R5 on-grid | – | – | – | ❌ | – | – | – | – | ❌ |

✅ supported, ❌ not supported, – not implemented yet.

**Sensors** covers reading values from the inverter and **Controls** covers changing its settings. Controls are shown with their current value and can be changed once control is allowed for the installation. See [Changing settings](#changing-settings) for what has been exercised on real hardware.

### What is exposed

Every register the integration knows for a model becomes an entity, one of seven types so that each setting has the control Home Assistant users expect:

| Entity type | What it is |
| --- | --- |
| `sensor` | Read-only numbers, counters, statuses, text, clocks and timestamps |
| `number` | A setting with a numeric range |
| `select` | A setting with named options |
| `switch` | A setting that is off or on, and each named bit of a packed register |
| `time` | A time of day, such as the start or end of a schedule |
| `text` | A text setting, such as a network address. Every text row is a commissioning setting and read-only |
| `button` | A command with nothing to read, such as restart. Created disabled |

An HS3 has 607 entities and a single-phase H2 with two PV strings has 266. Only the core set is enabled by default, 39 on the HS3 and 36 on the H2: power, voltage, temperature and state of charge readings, the energy counters and the main battery limits. The rest is created disabled, so a new installation stays light on the inverter and you enable what you want. A packed register that holds several values is read once and each value is its own entity. Equipment a unit may not have, such as an EV charger or a second meter, is created disabled on every unit.

A device only gets the entities that fit it: an H2 with one PV string has no second-string entities. A device running on a manually chosen model that is not recognised gets every entity of the model, since its shape is unknown, with those beyond one phase and two strings disabled.

Settings are in the configuration category, and versions, commissioning settings and network settings are in the diagnostic category. A value outside a setting's documented range is shown as read; the range limits what can be set, not what is shown. An enumerated value with no known name is shown as unknown, and its code is listed in diagnostics so it can be reported.

The HS3 register behaviour has been verified by hand. The H2 behaviour comes from SAJ protocol documentation and field observations of H2-family units, and has not been hand-verified on an H2 by this project.

## Installation

There is no published release yet. The development integration can be added through Home Assistant using the inverter's host, Modbus TCP port (default `502`) and unit ID (default `1`). The **Model** field defaults to Automatic, which identifies an HS3 or an H2 from the device itself. Choose a model manually only when the inverter is not recognised: a selection that contradicts a recognised device is rejected, and a selection applied to an unrecognised device is saved only after its required registers answer and you confirm it. Disabling an entity in Home Assistant stops its register being read. The default update interval is 60 seconds and no interval can be shorter than 10 seconds.

Setup only requires the device identity and six core readings (operating mode, battery state of charge, load, solar, battery and grid power) to answer, so a register one unit happens to lack cannot block it. The device type that setup or Configure last verified is stored with the installation, which lets the forms work out the request load while the installation is not loaded.

Moving an installation between an H2 and an HS3 is done through Configure. Confirm the replacement and the device, entities, names and history stay with the installation. An entity keeps its history across the move where both models have it.

### Limitations

- Automatic detection recognises the HS3 and the single-phase H2 only. Other H2-family units, such as the three-phase H2, report other device types and need the model chosen manually, with readings that may be wrong because they cannot be verified.
- AS2, HS2 and other SAJ products are not recognised.
- The sign of total grid power is published as the inverter reports it and is not labelled as import or export.

[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=dogmatic69&repository=home-assistant-saj-modbus&category=integration)
[![Open your Home Assistant instance and start setting up SAJ Local.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=saj_local)

## How it works

The integration connects to your inverter over Modbus TCP on your local network and reads its registers on a schedule you control. All communication stays between Home Assistant and the inverter.

### Polling groups

By default every enabled entity is read at the installation's update interval. To read some entities faster or slower, open the integration page, choose **Add polling group** and give the group a name, a number of seconds between updates (at least 10) and the entities it holds. A group can hold any entity of the installation, whatever its type. Edit or delete a group from the same page. An entity belongs to at most one group, and every entity in no group stays on the default interval.

The entities are listed in register order and each is labelled with the block of registers it is read from (realtime, energy, settings, battery, meters, versions and so on), so entities that can share a request sit together. Disabled entities can be chosen too and are marked "(disabled)" in the list; they cost nothing until they are enabled.

Changing a group reloads the integration once. It never touches the entities themselves: moving an entity between groups, removing it from a group or deleting the group keeps the entity, its name and its history.

All cadences of an installation share one clock, so a 10 second group and a 60 second default are read together every sixth tick, in one combined read where registers are next to each other. A cycle that overruns is not caught up: the missed ticks are dropped and polling carries on from the next tick.

#### The request load

With a full register set the cost of a choice is no longer obvious, so the polling group form and Configure show it, as requests per minute against the budget of 40 (for example "15 of 40 requests per minute" on an HS3 with the default core set and a 10-second group of load, solar, battery and grid power). It is worked out from the cadences, the entities that are enabled and the register layout; showing it sends nothing to the inverter. Only enabled entities count. Each cadence is planned on its own, so the figure is an upper bound: when two cadences fall on the same tick their entities share requests. The cost belongs to the whole selection rather than to one entity, because four entities in one block cost one request and two in different blocks cost two, so no per-entity cost is shown.

After a valid polling group submission, nothing is saved yet. A result step shows how many requests one read of the group takes, the load before and the load with the group saved, and lets you save or go back and change the selection with your input kept. When the load with the group is over the budget it says that cadences will run slower than configured; saving is still allowed. Configure adds a similar confirmation, after the model, replacement and prefix confirmations, when a changed default interval puts the load over the budget.

Enabling an entity in Home Assistant cannot be intercepted by a form, so the warning logged at load and the figure in diagnostics cover that case.

### Entity IDs and the prefix

Entity IDs are fixed by the integration, never by the text shown on a dashboard: `<domain>.saj_<key>`, where the domain is the entity type, for example `sensor.saj_pv_power` and `number.saj_backup_reserve_soc`. A key is unique across all entity types, so the same key never exists as two kinds of entity. Display names can be reworded freely; the key in the ID cannot.

Each installation has an optional **Prefix**, empty by default. With the prefix `house` the IDs become `sensor.saj_house_pv_power` and `number.saj_house_backup_reserve_soc`, so a second system with its own prefix never ends up with `_2` IDs. A prefix uses lowercase letters and digits only, with no underscores, and is at most 32 characters. Underscores are excluded so that two prefixes can never produce the same ID. It must be unique: two installations cannot share a prefix, and an empty prefix counts, so only one installation can have none. It cannot start the name of any entity of any supported model, so `battery` is refused because `battery_power` exists, and so are words like `grid`, `meter`, `inverter`, `backup`, `pv1`, `load`, `ev`, `parallel` and `average`. Otherwise `saj_battery_power` could mean the entity `battery_power` or the prefix `battery` and the entity `power`. Setup is refused when any ID the installation would create, in any entity type, is already taken in Home Assistant. These rules apply when a prefix is set or changed; saving other Configure settings with the prefix unchanged does not re-check it.

The prefix can be added, changed or removed in Configure. Before anything is saved you are shown the old and new pattern and warned that automations, scripts, dashboards, templates and Energy settings using the old IDs will stop working until you update them. On confirmation the installation's entities of every type are renamed through Home Assistant's entity registry, which carries their history and long-term statistics to the new IDs, and the integration reloads. Only an entity still at the ID the old prefix produces is renamed; one you renamed yourself is left alone. Disabled entities are renamed too.

A change is refused, and nothing is renamed, when a new ID is already taken or when Home Assistant already holds long-term statistics under a new ID, for example from a deleted installation that used the prefix. Home Assistant will not move statistics onto an ID that already has them. Short-term state history under a new ID cannot be detected, so the old ID's recent state history is not carried over in that case while statistics still are. Setup does not check statistics, so adding an installation back with the prefix of a deleted one continues that installation's history.

If a later release adds an entity and its ID is already taken, Home Assistant gives the new entity a numeric suffix and a warning naming both IDs is logged.

Diagnostics never contain the prefix. They show the pattern as `<domain>.saj_<key>` or `<domain>.saj_[redacted]_<key>`, which tells you whether a prefix is set.

### Changing settings

Control is off by default. You can switch on **Allow control** during setup or later in Configure; either way you are asked to confirm, after any model confirmation (and, in Configure, any replacement, prefix and load confirmations), because entity changes and automations will then change inverter settings, and because enabling EMS functions disables the inverter's reverse-current protection. On an HS3, the confirmation during setup also asks for the EMS heartbeat; in Configure the heartbeat is a field on the main form. Switching it off needs no confirmation. The installation reloads when the option changes.

With control on, a change is checked before anything is sent, in this order: control is on, the model was verified (an installation on a manually chosen model that could not be verified is never written to), the setting is not a commissioning setting, the value is valid, the inverter is reachable, and the write allowance has room. Each refusal has its own message saying that the inverter was not changed. Then the change is written once and read back, and the entity shows the value the inverter actually holds. If the inverter accepts the request but holds a different value, the entity shows that value and the action fails. If the inverter answers with an exception, the message gives its code and says the inverter was not changed. If there is no answer, the message says the change may or may not have been applied, nothing is sent again, and the connection is reopened with a full read.

A packed register that holds several settings is read, only the changed field is replaced and the register is written back, so the other fields are never disturbed. One change writes one register: changing `charge_slot_1_power` leaves `charge_slot_1_days` as it was. Schedule slots do nothing unless the application mode is time-of-use; the integration does not switch the mode for you. Application mode `ems` on its own leaves the inverter idle with the house running from the grid and there is no automatic exit. The application mode also offers `time_of_use_bms` on the HS3 and `ai_saving` on the H2, which those units report when the SAJ app selects those modes; neither has been written over Modbus.

**Commissioning settings stay read-only for now.** The meter and its address, RS485, the battery protocol, the network, the EV charger link and the settings sequence number are refused whatever you do, because a wrong value can cut the inverter off from its meter, battery, charger or from Home Assistant itself. This may be revisited. Clearing the energy history and factory reset are not offered; the official app covers them. This may be revisited too.

**Commands** are buttons, created disabled and in the configuration category: clear fault history, clear current fault, restart inverter, synchronise clock (which sends Home Assistant's local time) and, on the HS3, remove the EMS PV power limit. A command is sent once; when no acknowledgement arrives the message says it may or may not have run. After a restart the inverter stops answering for a while and the normal back-off applies.

#### EMS on the HS3

The HS3 can be put under external control. The EMS enable switches, the EMS timeout and eight write-only numbers (inverter, battery and grid power targets, battery current limits, import and export power limits and the PV power limit) are available. A positive target sells or discharges and a negative one buys or charges. The targets and limits are read only by the heartbeat while you own an EMS function, and then show the value the inverter holds, marked as assumed; otherwise they show the last value this installation sent and are unknown before the first write. A PV power limit of "no limit" shows as unknown. Grid-point control needs a meter; this is not checked.

EMS functions you switch on from Home Assistant are kept alive by a heartbeat: every **EMS heartbeat** interval (60 seconds by default, 30 to 3600, asked for in the setup confirmation and shown in Configure, only for a model with EMS) the target of each function you own is read once, followed by the five limits in three more read requests. Reading counts as EMS activity, so nothing is written and no write slot is used, and the entities show the values the inverter holds, even if they were cleared or changed elsewhere. A function you own gets beats whether or not its target was ever set from Home Assistant. A beat counts against the request budget and its pacing but not against the write allowance; one that is refused or answered with an exception is dropped and the next is sent on time. A limits read is not a beat: if the inverter answers it with an exception it is skipped without a warning, and if it gets no answer it is handled like any lost connection. The two inverter switches exclude each other. A function cannot be switched on while the inverter's EMS timeout is at or below the heartbeat interval, and the timeout cannot be set that low. Ownership survives a lost connection: while the inverter is unreachable beats are dropped, and they resume by themselves when it is back. The first dropped beat of a function logs a warning, because the inverter's EMS timeout ends the function if beats keep failing, and the recovery is logged once. Ownership ends when you switch the function off, or when a poll finds the function switched off in the inverter. A function that was already on when the integration loaded is left alone: no beat, and it is not switched off. When the integration unloads or Home Assistant stops, it tries to switch off the functions you switched on, clearing only those bits. This is a best effort, not a guarantee: it cannot happen when the inverter is unreachable or Home Assistant stops abruptly. The switch-off works only for the EMS functions and is the one write the allowance does not refuse, though it is counted against it. It waits for a read in progress before its 5 seconds start; if that fails a warning names the inverter's timeout as the fallback. Whether the timeout can be relied on is not settled: on the real unit it fired at 5 seconds but did not at 20 or 60 seconds while another client polled, so the integration does not rely on it.

#### What has been exercised on real hardware

Verified on a real HS3 with single-register writes: the application mode, the backup reserve, the passive battery charge power, the four EMS enable switches, the EMS timeout and the eight EMS targets and limits. Implemented from field reports of H2 units, not exercised by this project: the H2 schedule slots, application mode, passive mode and its powers, the battery limits, the power limits and the export limit. Documented only, never exercised on real hardware: every other writable setting, every write of more than one register, and every command.

### Protecting the inverter

Communication modules can stop serving a client that polls too hard, so the limits below apply to everything the integration sends and cannot be configured away.

- One connection and one request in flight per inverter, with a pause between requests. Checking a connection in Configure uses the installation's own connection rather than a second one.
- At most 40 requests in any 60 seconds per inverter address. The count is kept for as long as Home Assistant runs, so reloading the integration, editing a polling group, a setup retry and the connection check in Configure all draw on the same allowance instead of starting from zero. A request that would exceed this waits; nothing is sent early or dropped. One request reads one block of neighbouring registers, so grouping entities that sit together costs less. At load a warning is logged if your cadences plan more than the limit, and diagnostics show the planned load.
- No retries inside a cycle. After a failed cycle the wait before the next attempt doubles from the shortest interval up to 5 minutes, then the first cycle that succeeds reads everything again. The wait also survives reloads and applies to loading the integration: a load attempted too early reports not ready without contacting the inverter, and a failed load counts as a failure. Checking a connection yourself in setup or Configure is never held back by the wait and still counts towards the 40 requests; a check that passes clears the wait, because the inverter has just answered, and one that fails leaves it as it was.
- Every wait is time-limited, so a stalled inverter ends a cycle as a failure instead of stopping polling silently. A late or stray response is discarded and never read as a value.
- Registers that sit close together are read in one request, and the few words between them are read and discarded. Only registers inside a block the device documents are ever bridged, a request never leaves its block, and a request is never larger than the sizes already in sustained use on each model: 32 registers on the HS3 and 56 on the H2. Without this, disabling an entity would split a block in two and make the load worse. A full read of the core set is 9 requests on an HS3 and 5 on an H2, and a full read of every row is 36 on an HS3 and 11 on an H2.
- Some registers are never polled, whatever is enabled. The HS3 EMS targets and limits count as EMS activity when read, which keeps the inverter under external control, so they are write-only entities. Only the heartbeat reads them, once per interval while you own an EMS function: the target of each owned function, then the five limits. Without an owned function they show the last value you sent. Write-only commands and one HS3 identity register are never read at all. Entities that are not read are not offered in polling groups.
- Writes draw on the same 40 requests as reads and have a smaller allowance inside it: at most 20 write requests in any 60 seconds per inverter address. A change over the allowance is refused, not queued, because a setting applied a minute late is worse than one refused. A change is sent once and never retried or replayed after a reconnect. The switch-off of EMS functions when Home Assistant stops is the one write the allowance does not refuse, though it is counted against it; it works only for EMS functions. The heartbeat reads and so uses no write slot.
- A connection the inverter has closed in the meantime is reopened once and the device is verified; that cycle then reads every enabled entity again, so no value predates the reconnect.

### When the inverter refuses a register

A refusal is an answer, not a failure. Only the entities in the refused request become unavailable and the others keep updating. A request that holds several entities is not retried entity by entity, which would cost one request per entity after a single refusal. Instead the refused request is halved from the next cycle, split at the entity boundary nearest the middle, and halved again while a half is refused, until the refused entity is alone. A half that succeeds returns to normal planning. If both halves succeed, the fault lay in a gap word between them, so that gap is remembered and not bridged again until the integration next loads. A refused region costs at most two requests a cycle while it is narrowed.

After three refusals in a row a lone entity is suspended: shown as unavailable, no longer read, logged once with the exception code and listed in diagnostics. A suspended entity is tried again once a day and whenever the integration loads, and comes back as soon as the register answers. An inverter that reports itself busy or failed stops the cycle instead, and every entity is unavailable until it recovers.

### Diagnostics

Diagnostics list the enabled entity keys, the cadences with the requests each takes, the planned load against the budget, refused and suspended entities, the gaps found that are no longer bridged, and the requests currently being narrowed. An enumerated value with no known name is listed under its key with its code. The values of serial numbers, the product code, the MAC address and the network addresses, of the inverter or of an EV charger, are never included, nor are the host, the prefix or polling group names.

## Help and feedback

Questions, bug reports and ideas are welcome on the [issue tracker](https://github.com/dogmatic69/home-assistant-saj-modbus/issues).

## Contributing

Developer setup, tooling and project conventions are in [CONTRIBUTING.md](CONTRIBUTING.md).

## Disclaimer

This project is an independent, community-built integration. It is not affiliated with, authorised, sponsored or endorsed by SAJ (Guangzhou Sanjing Electric Co., Ltd.) or any of its subsidiaries or affiliates.

SAJ, the SAJ logo and all related product names, model names and trademarks are the property of their respective owners. They are used here only to identify the equipment this integration works with.

The software is provided as is, without warranty of any kind. You use it at your own risk: the authors accept no liability for damage to equipment, loss of data, loss of warranty or any other consequence of using it. This applies in particular to writing settings to your inverter.

## Licence

[MIT](LICENSE)
