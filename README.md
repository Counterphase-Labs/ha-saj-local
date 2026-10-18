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
| H2 single-phase, 3–6 kW | ✅ | ❌ | ✅ | ✅ | – | ❌ | ❌ | ✅ | – |
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

Every register the integration knows for a model becomes an entity, one of eight types so that each setting has the control Home Assistant users expect:

| Entity type | What it is |
| --- | --- |
| `sensor` | Read-only numbers, counters, statuses, text, clocks and timestamps |
| `binary_sensor` | A fault the inverter, the battery or the EV charger reports, shown as a problem that is on or off, see [Device faults and repairs](#device-faults-and-repairs), and `control_allowed`, which is on while the system accepts changes, see [Control allowed](#control-allowed) |
| `number` | A setting with a numeric range |
| `select` | A setting with named options |
| `switch` | A setting that is off or on, and each named bit of a packed register |
| `time` | A time of day, such as the start or end of a schedule |
| `text` | A text setting, such as a network address. Every text row is a commissioning setting and read-only |
| `button` | A command with nothing to read, such as restart. Created disabled |

An HS3 with every optional piece of equipment has 742 entities and a single-phase H2 with two PV strings and every optional piece of equipment has 484. Only a core set is enabled by default: power, voltage, temperature and state of charge readings, the energy counters, the main battery limits and every fault entity. An HS3 with a battery and a grid meter (Meter A) has 143 enabled by default and an H2 has 113. Optional equipment adds its own defaults when it is fitted: the second meter's total power, the EV charger's status, mode, power and energy counters, and the parallel system's powers and state of charge, which brings an HS3 with everything fitted to 181 and an H2 to 119. The rest is created disabled, so a new installation stays light on the inverter and you enable what you want. A packed register that holds several values is read once and each value is its own entity. Equipment a unit may not have is only created when it is fitted, see [Optional equipment](#optional-equipment).

A device only gets the entities that fit it: an H2 with one PV string has no second-string entities. A device running on a manually chosen model that is not recognised gets every entity of the model, since its shape is unknown, with those beyond one phase and two strings disabled. The HS3 has no register for the live total of the backup port, so its backup load power is the sum of the three backup phase powers; the five-minute average backup power is a different reading and is not used for it.

Settings are in the configuration category, and versions, commissioning settings and network settings are in the diagnostic category. A value outside a setting's documented range is shown as read; the range limits what can be set, not what is shown. An enumerated value with no known name is shown as unknown, and its code is listed in diagnostics so it can be reported.

The HS3 register behaviour has been verified by hand. The H2 behaviour comes from SAJ protocol documentation and field observations of H2-family units, and has not been hand-verified on an H2 by this project. On the H2, the grid import and export totals and the first-phase counters (the same keys as on the HS3), the battery voltage and current, the battery low-voltage warning and the peak shaving mode rest on field reports and field tooling in sustained use; every other H2 row rests on the SAJ H2 document only. One field report has the grid totals unavailable on a single-phase unit: if a unit refuses them, the repair issue for refused registers names the entities, and the first-phase counters, which equal the total on a single-phase unit, can be enabled instead.

## Installation

There is no published release yet. The development integration can be added through Home Assistant using the inverter's host, Modbus TCP port (default `502`) and unit ID (default `1`). The **Model** field defaults to Automatic, which identifies an HS3 or an H2 from the device itself. Choose a model manually only when the inverter is not recognised: a selection that contradicts a recognised device is rejected, and a selection applied to an unrecognised device is saved only after its required registers answer and you confirm it. Disabling an entity in Home Assistant stops its register being read. The default update interval is 60 seconds and no interval can be shorter than 10 seconds.

Setup only requires the device identity and six core readings (operating mode, battery state of charge, load, solar, battery and grid power) to answer, so a register one unit happens to lack cannot block it. The device type that setup or Configure last verified is stored with the installation, which lets the forms work out the request load while the installation is not loaded.

### Optional equipment

Nothing about equipment is asked during setup. Every time the integration loads, which includes every Home Assistant start and every reload, it checks which optional equipment the inverter has and creates entities only for that: the battery, the grid meter (Meter A), a second meter (Meter B) and a parallel machine system on both models, and the EV charger on an HS3. An HS3 with a battery and nothing else has 503 entities instead of 742, and an H2 with no battery has none of the 193 battery entities. The check reads all of its registers together, at most 4 requests on either model, so the default request load does not change. The battery is detected from the battery protocol, Meter A and Meter B from their meter status, the EV charger from its enable setting and a parallel system from the parallel mode and the number of machines online. If the inverter does not answer a check, a battery and Meter A are assumed and the others are not. A unit that refuses the parallel check costs one refused request per load and gets no parallel entities.

Equipment that was detected is remembered and stays fitted, so a meter that is offline during a restart does not take its entities away. When a remembered piece of equipment is no longer detected, one warning per load names it and the values read, diagnostics flag it, a repair issue in Home Assistant names the installation and the equipment and asks you to check it or set it to Not fitted in Configure, and its entities stay and read whatever the inverter answers. The repair issue goes away at the next load that detects the equipment again or no longer has it on Automatic, and when the installation is removed. Equipment fitted later is picked up at the next restart or reload.

The H2 can hold up to five battery packs and reports how many it has. A count from 1 to 5 limits the pack entities to that many packs; a count of 0, which units commonly report with a battery fitted, leaves all of them. Each of the five packs has identity entities (BMS type, BMS serial number, BMS software and hardware version, battery type of 50, 80 or 100 Ah and battery serial number), created disabled, and the two serial numbers are private: they are never in the register snapshot or in diagnostics. The state, health, fault and energy entities of a pack cover the first four packs. The highest count seen is remembered, never lowered automatically, forgotten when the battery is set to Not fitted or the inverter is replaced, and diagnostics show the count read and the limit in use. The HS3 has entities for one pack and does not read the count for this.

Configure has a collapsed **Equipment** section with a field for each piece of equipment the model can have: **Automatic** (the default), **Fitted** and **Not fitted**. The section also says what is treated as fitted now. Fitted creates the entities without checking. Not fitted removes the equipment's entities from Home Assistant, including any changes you made to them such as renaming, and forgets what was detected; choosing Automatic afterwards detects it again from scratch. Entity IDs do not change, so history continues if the equipment is fitted again. Entities of equipment that is not fitted cannot be read, polled or written.

An HS3 with an EV charger also offers its EMS charging controls, created disabled: a switch for charging, a phase mode of three-phase or single-phase, and a charge current of 6 to 32 A. The charging bit is inverted on the inverter and the switch shows and takes on and off the right way round. Like other settings they can be changed once control is allowed.

Moving an installation between an H2 and an HS3 is done through Configure. Confirm the replacement and the device, entities, names and history stay with the installation. An entity keeps its history across the move where both models have it.

### Limitations

- Automatic detection recognises the HS3 and the single-phase H2 only. Other H2-family units, such as the three-phase H2, report other device types and need the model chosen manually, with readings that may be wrong because they cannot be verified.
- AS2, HS2 and other SAJ products are not recognised.
- Battery and grid power use one sign on every model, so a reading means the same on an HS3 and an H2 and the power flow card can draw the direction without knowing the model. Battery power is positive while the battery discharges and negative while it charges. Grid power is positive while the system sends power to the grid and negative while it takes power from the grid. The same convention is used by the power control targets.

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

If a later release adds an entity and its ID is already taken, Home Assistant gives the new entity a numeric suffix and a warning names the entity's kind and key, not its ID, because the ID would reveal the prefix.

Diagnostics never contain the prefix. They show the pattern as `<domain>.saj_<key>` or `<domain>.saj_[redacted]_<key>`, which tells you whether a prefix is set.

### Changing settings

Control is off by default. You can switch on **Allow control** during setup or later in Configure; either way you are asked to confirm, after any model confirmation (and, in Configure, any replacement, prefix and load confirmations), because entity changes and automations will then change inverter settings, and because enabling EMS functions disables the inverter's reverse-current protection. On an HS3, the confirmation during setup also asks for the EMS heartbeat; in Configure the heartbeat is a field on the main form. Switching it off needs no confirmation. The installation reloads when the option changes.

With control on, a change is checked before anything is sent, in this order: control is on, the model was verified (an installation on a manually chosen model that could not be verified is never written to), the setting is not a commissioning setting, the value is valid, the inverter is reachable, and the write allowance has room. Each refusal has its own message saying that the inverter was not changed. Then the change is written once and read back, and the entity shows the value the inverter actually holds. If the inverter accepts the request but holds a different value, the entity shows that value and the action fails. If the inverter answers with an exception, the message gives its code and says the inverter was not changed. If there is no answer, the message says the change may or may not have been applied, nothing is sent again, and the connection is reopened with a full read.

A packed register that holds several settings is read, only the changed field is replaced and the register is written back, so the other fields are never disturbed. One change writes one register: changing `charge_slot_1_power` leaves `charge_slot_1_days` as it was. Schedule slots do nothing unless the application mode is time-of-use; the integration does not switch the mode for you. Application mode `ems` on its own leaves the inverter idle with the house running from the grid and there is no automatic exit. The application mode also offers `time_of_use_bms` on the HS3 and `ai_saving` on the H2, which those units report when the SAJ app selects those modes; neither has been written over Modbus. The H2 also offers `peak_shaving`, which field reports show selected in the SAJ app, read back and written over Modbus; the H2 document does not list it. `application_mode_active` shows the mode the H2 is running in.

On the H2 three more settings can be changed: the buzzer (`switch.saj_buzzer`, on while the inverter's buzzer is not forbidden), the LED ring (`select.saj_led_mode`, the same four options as the HS3) and the battery forced charge power (`number.saj_battery_forced_charge_power_limit`, 10 to 100 % of rated power, which limits how much power may charge the battery from the grid). The H2's off-grid mode and inverter stop are readings only; they are not controls.

**Commissioning settings stay read-only for now.** The meter and its address, RS485, the battery protocol, the network, the EV charger link and the settings sequence number are refused whatever you do. On the H2 this also covers the grid type, the parallel set-up, the battery and PV input modes, the rated power and machine model, the protection limits, the PV start and shutdown voltages and the MPPT limits, the lead-acid battery parameters, the BMS update, the reverse-flow mode and the off-grid output voltage and frequency. They are shown with their real control type and refuse changes, because a wrong value can cut the inverter off from its meter, battery, charger or from Home Assistant itself. This may be revisited. Clearing the energy history and factory reset are not offered; the official app covers them. This may be revisited too.

**Commands** are buttons, created disabled and in the configuration category: clear fault history, clear current fault, restart inverter, synchronise clock (which sends Home Assistant's local time) and, on the HS3, remove the EMS PV power limit. A command is sent once; when no acknowledgement arrives the message says it may or may not have run. After a restart the inverter stops answering for a while and the normal back-off applies.

#### Control allowed

Every system has a `binary_sensor.saj_control_allowed` (`binary_sensor.saj_<prefix>_control_allowed` when a prefix is set), named "Control allowed" and in the diagnostic category. It is on while the system's **Allow control** option is on and the model is verified, which is the same condition that lets the integration write. It is a read-only sensor and not a switch on purpose: a switch on a dashboard would switch writing on without the warning that Configure shows first. The dashboard cards read the sensor and show their controls as locked while it is off.

#### The control set

Most schedule slot entities and many controls are created disabled, so a dashboard card would have nothing to show or change. Switching **Allow control** on therefore also enables the system's control set: every entity a card can change, which is every field of the charge, discharge and EV charger slots, the power control switches and targets of every function the system offers, the application mode and time-of-use settings, the battery and grid limits, the EV charger settings, the buzzer, the LED mode, the clock synchronisation command and the clear fault command. Battery pack readings and other read-only entities are not part of the set. Entities that were already enabled stay as they are.

- **What the confirmation shows.** The **Allow control** confirmation states how many control entities will be enabled and how reading them changes the request load. With every piece of equipment fitted and the default 60-second interval the set is 141 entities on an HS3 and raises the load from 14 to 18 of 40 requests per minute, and is 87 entities on an H2 and raises the load from 9 to 10. The setup flow cannot know the equipment of a system that does not exist yet, so it counts with every piece of equipment fitted and says "up to"; Configure uses the equipment found and its figures are exact.
- **The second reload.** The entities appear about 30 seconds after saving, because Home Assistant reloads a system 30 seconds after any of its entities is enabled, whoever enables the entity. That reload unloads the system, and unloading switches off every power control function that was switched on from Home Assistant, as every reload does. Wait until the entities appear before changing anything, or a power control function switched on in between is switched off again. The same second reload follows whenever a new member of the set appears later, such as the EV charger slots once an EV charger is detected.
- **Switching off.** Switching **Allow control** off, or running a model that is not verified, disables every entity the set enabled and removes the mark the integration left on it. Home Assistant removes each disabled entity at once, no reload follows and the request load returns to what it was before. An entity you enabled yourself has no mark and stays enabled.
- **Your choice wins.** An entity you disabled before switching control on stays disabled, and a card then counts the slot as left out. If you disable an entity of the set while control is on, it stays disabled from then on.

#### EMS on the HS3

The HS3 can be put under external control. The EMS enable switches, the EMS timeout and eight write-only numbers (inverter, battery and grid power targets, battery current limits, import and export power limits and the PV power limit) are available. A positive target sells or discharges and a negative one buys or charges. The targets and limits are read only by the heartbeat while you own an EMS function, and then show the value the inverter holds, marked as assumed; otherwise they show the last value this installation sent and are unknown before the first write. A PV power limit of "no limit" shows as unknown. Grid-point control needs a meter; this is not checked.

EMS functions you switch on from Home Assistant are kept alive by a heartbeat: every **EMS heartbeat** interval (60 seconds by default, 30 to 3600, asked for in the setup confirmation and shown in Configure, only for a model with EMS) the target of each function you own is read once, followed by the five limits in three more read requests. Reading counts as EMS activity, so nothing is written and no write slot is used, and the entities show the values the inverter holds, even if they were cleared or changed elsewhere. A function you own gets beats whether or not its target was ever set from Home Assistant. A beat counts against the request budget and its pacing but not against the write allowance; one that is refused or answered with an exception is dropped and the next is sent on time. A limits read is not a beat: if the inverter answers it with an exception it is skipped without a warning, and if it gets no answer it is handled like any lost connection. The two inverter switches exclude each other. A function cannot be switched on while the inverter's EMS timeout is at or below the heartbeat interval, and the timeout cannot be set that low. Ownership survives a lost connection: while the inverter is unreachable beats are dropped, and they resume by themselves when it is back. The first dropped beat of a function logs a warning, because the inverter's EMS timeout ends the function if beats keep failing, and the recovery is logged once. Ownership ends when you switch the function off, or when a poll finds the function switched off in the inverter. A function that was already on when the integration loaded is left alone: no beat, and it is not switched off. When the integration unloads or Home Assistant stops, it tries to switch off the functions you switched on, clearing only those bits. This is a best effort, not a guarantee: it cannot happen when the inverter is unreachable or Home Assistant stops abruptly. The switch-off works only for the functions you switched on, through the EMS bits or through power control, and is the one write the allowance does not refuse, though it is counted against it. It waits for a read in progress before its 5 seconds start; if that fails a warning names the inverter's timeout as the fallback. Whether the timeout can be relied on is not settled: on the real unit it fired at 5 seconds but did not at 20 or 60 seconds while another client polled, so the integration does not rely on it.

#### Power control

Power control holds one point of the system at a set power in watts, the same way on every model that can do it. There are three functions: **Battery** (the battery charges or discharges at the set power), **Grid** (the grid connection point imports or exports at the set power) and **Inverter** (the inverter takes in or puts out the set power). Each function a system has gets a switch (`switch.saj_battery_power_control`, `switch.saj_grid_power_control`, `switch.saj_inverter_power_control`) and a number (`number.saj_battery_power_target` and so on, with the prefix when one is set), in watts and whole watts. They are created disabled and in the configuration category. A positive power discharges, exports or puts out; a negative power charges, imports or takes in, on every model. The target is rounded to the nearest step the inverter has (1.2 W on a 12000 W HS3, 8 W on an 8000 W H2) and shows what the inverter holds. The switch is on while the inverter reports the function running, even if it was started with the model's own rows.

| | HS3 | H2 |
| --- | --- | --- |
| Functions | Battery, Grid (needs Meter A), Inverter | Battery |
| How | The EMS enable bit and target row of the function, in the share of rated power (0.01 %) | Passive mode: the application mode, the direction and the charge or discharge power (0.1 %, up to 110 % of rated power) |
| Range | Minus to plus rated power | Minus to plus 110 % of rated power |
| Kept alive | By the EMS heartbeat | Nothing to do; nothing in any source says passive mode times out |
| If Home Assistant stops abruptly | The inverter's EMS timeout may end the function (see above, it is not relied on) | The function keeps running until it is switched off |
| Stopped by | Clearing the enable bit; the target is left | Direction standby, then the application mode it was in before (stored, self-use when not known) |

Switching on needs a target to have been set. Before anything is written, the state rows of the system's other functions are read afresh (one request where they share a register), whatever entities are enabled, so a function started outside Home Assistant is seen; the start is refused, naming the function that is running, and nothing is written. Two functions never run at once. That read follows the rules of the read before a write: it needs control on, a verified model and an open connection, and it counts against the request budget. A system with one function has no other function to read. Setting the target while a function runs sends it at once; otherwise it is kept, survives a restart and is sent when the function starts. Power control does nothing while Allow control is off or the model is a manual override. Every write is an ordinary write: validated, sent once, read back and counted against the write allowance. The switch-off is the exception, and it accepts only the writes of a stop: an enable bit to off, the passive direction to standby, and the application mode to a mode other than passive mode; anything else is refused. A switch-off that fails is sent again every heartbeat interval until the inverter reports the function not running.

On the H2 a function is **running** whenever the inverter is in passive mode, whatever the direction. A power of 0 is direction standby inside passive mode: the function is still running, at 0 W, the switch stays on, and a later power is an ordinary change of power (the power row, then the direction). The function stops running when the application mode leaves passive mode. A stop that gets its direction through but not its mode leaves the inverter in passive mode, so the function is still running, owned, and the stop is sent again every heartbeat interval. When a poll finds the inverter out of passive mode the function is released and the remembered mode is forgotten, so a mode someone else chose is never overwritten later.

A start that fails part way is stopped again. If that stop fails too, the function is owned and its stop is outstanding: it is sent again every heartbeat interval until it is confirmed or a poll reads the function as not running. This holds with or without a schedule, and unload and stop switch the function off like any owned function. The error you see is the one the start failed with.

Messages that name a function use its translated name, the same one the schedule form shows.

An H2 has Battery power control only. No H2 register holds the grid connection point or the inverter output at a set power: the passive grid charge power had no effect in field tests and the passive grid discharge power only caps what passive mode sends to the grid, so Grid and Inverter power control are not offered on the H2.

The HS3 writes the target and then sets the enable bit of the function (the inverter uses the bit that leaves EMS by the inverter's own timeout). The H2 writes the power row of the direction, reads and remembers the application mode unless it is already passive, writes passive mode and then the direction. The H2 writes are from field reports and the H2 document and have not been exercised by this project.

A function switched on through power control is switched off on unload and when Home Assistant stops. A function found running when the integration loads is left running and is not owned, unless a schedule is on for it. On a model with no keep-alive and no timeout, a function left running by a Home Assistant that stopped abruptly keeps running: that is the H2.

##### Power control schedules

First make a **schedule helper** in Home Assistant (Settings, Devices & services, Helpers, Schedule) with its times and weekdays. Then open the system's page and choose **Add power control schedule**; pick the function and the schedule helper. A schedule can be changed or removed on the same page, and doing so reloads the system. The integration has no times or weekdays of its own, and Setup and Configure are unchanged. The form refuses a schedule while Allow control is off, a function that already has a schedule in this system, and a schedule helper already used by another schedule of this system.

A block of the schedule helper can carry the additional data `power`, in whole watts with the sign above, for example `power: -600` to charge the battery at 600 W. Without it the function's power target is used.

The function is wanted while the schedule helper's state is `on`; any other state, including unavailable, unknown and a helper that no longer exists, is not wanted. The controller compares what is wanted with what the inverter reports after the first successful polling cycle of a load, whenever a schedule changes state or its `power` changes, and then once per heartbeat interval for as long as an action is outstanding.

| Situation | What happens |
| --- | --- |
| A schedule turns on, or is on at load, and no function is running | The target is set from the block's `power` when it has one, then the function starts |
| The block has no `power` and no target has been set | Not started; outstanding, with its own warning |
| The schedule's function is already running | The power is changed when the block has one, and the function is taken over |
| A different function is running | Nothing is written; outstanding |
| The start is refused or fails | Outstanding; each attempt is a new change, sent once |
| The start has succeeded | Nothing more while the schedule stays on, except a new `power`. A target changed by hand stays. A function switched off by hand or by the inverter stays off until the schedule next turns on |
| The schedule moves to a block with a different `power` while on | The power is changed |
| The block's `power` is not a whole number inside the target's range | Not started and not written; outstanding, with its own warning |
| A schedule turns off and the function is owned | The function is stopped |
| The stop is refused or fails | Outstanding until it is confirmed or a poll reads the function as not running |
| Allow control is off, or the model is an override | Nothing, ever |
| The inverter is unreachable | The write rules refuse with nothing sent; outstanding |

With nothing wanted and nothing outstanding the controller sends nothing. Diagnostics list the functions a system has and how each is done, which is running and which is owned, each schedule with its function, helper, whether it is on and the action outstanding, and no power value.

#### What has been exercised on real hardware

Power control on the H2 (passive mode with the application mode, direction and powers) is implemented from field reports and the H2 document and has not been exercised by this project. Verified on a real HS3 with single-register writes: the application mode, the backup reserve, the passive battery charge power, the four EMS enable switches, the EMS timeout and the eight EMS targets and limits. Implemented from field reports of H2 units, not exercised by this project: the H2 schedule slots, application mode, passive mode and its powers, the battery limits, the power limits and the export limit. Documented only, never exercised on real hardware: on the H2 the buzzer switch, the LED mode and the battery forced charge power limit, and every other writable setting, every write of more than one register, and every command.

### Dashboard cards

The integration serves its own cards and registers them with Home Assistant when it starts, so they appear in the card picker with no resource to add and nothing to clear from a cache. Every element is set up by choosing one SAJ system with its **System** option, so a home with two systems adds the same card twice, once per system. In a two-system home, rename each system's device (Settings, Devices & services, the device, the pencil) so the titles say which is which: a system's title is its device name followed by its model, and the serial number is added only when two titles would otherwise match. Elements find a system's entities through the entity registry and never by entity ID, so they keep working when a prefix changes. A part whose entity does not exist or is disabled is not drawn, so each card shows only what its system has. Values, names and states use Home Assistant's own formatting, text follows the Home Assistant language, and the cards follow the theme.

| Element | What it shows | Options |
| --- | --- | --- |
| `saj-local-power-flow-card` | Live power between solar, battery, grid, home and the optional equipment, with the direction and speed of each flow | `show_strings` (off by default) lists each solar string, `show_optional` (on by default) draws the EV charger, backup load and Meter B, `scope` (`system` or `parallel`, `system` by default) chooses the system's own readings or the parallel system's readings, and a system without parallel readings shows the empty state with `parallel` |
| `saj-local-status-card` | Operating state, application mode, key readings, today's energy, a fault summary and whether changes are allowed | `show_energy` (on by default) |
| `saj-local-faults-card` | Active faults per piece of equipment with how long ago each began, and clear fault | `show_clear_groups` (on by default) shows the groups with no fault |
| `saj-local-battery-card` | State of charge with the reserve and limits marked, battery power and readings, one row group per pack | `show_packs` (on by default) |
| `saj-local-controls-card` | The shared settings the system offers, grouped into sections | `sections`, a list of `mode`, `battery`, `grid`, `power_control`, `ev_charger` and `device` (all by default) |
| `saj-local-schedule-card` | Charge, discharge and EV charger slots, a week timeline and a slot editor | `kinds`, a list of `charge`, `discharge` and `ev` (all by default), `show_timeline` (on by default) |
| `saj-local-weekdays` | A tile card feature with seven named day buttons for a slot's weekdays entity | None. Add it to a tile card whose entity is a slot weekdays number |
| `saj-local-status-badge` | A badge with the operating state and the number of active faults | None |

A few details are worth knowing:

- The battery card shows pack readings only for the pack entities you have enabled, because most of them are created disabled. The faults card shows every pack fault and warning, which are enabled by default.
- A card that finds none of its entities says which kind of entity to enable and links to the device page, because Home Assistant gives dashboards no way to list entities that are disabled. A schedule slot is drawn only when every entity of the slot is enabled, and the card counts the slots it left out.
- While `control_allowed` is off, every control on the controls, schedule and faults cards and on the weekdays feature is disabled and the card links to the integration's settings, where Allow control is switched on with its warning. Switching Allow control on is also what enables the entities the cards need, see [The control set](#the-control-set).
- A control writes once per decision: a slider when released, a number field on Enter or on leaving the field, a select, switch or time field on change, and the weekday buttons 1.5 seconds after the last press. The control then shows the value the inverter holds, never a guess, and a refusal is shown under the control in the integration's own words.
- The slot weekday buttons start on your first weekday. The number stored on the inverter does not move: Monday is bit 0 and Sunday bit 6 on every model, so Monday, Wednesday and Friday is 21.
- Charge and discharge slots only run in a time-of-use application mode, so the schedule card shows a notice with the mode select when the mode is another one. Both **Time-of-use** and **Time-of-use (BMS)** count, because the SAJ app keeps the charge settings of the BMS mode in the ordinary charge slots.
- The power flow card draws the sign convention under [Limitations](#limitations): a grid power of -2000 W draws the grid line flowing towards the inverter and labels the grid "Importing". Meter B is shown as a reading with no direction because its sign is not established on either model.
- The controls card has no Restart inverter button, so a tap on a dashboard cannot restart the inverter. Restart stays an entity.

**Adding a card.** Edit a dashboard, add a card, choose the SAJ Local card in the card picker and pick the system. Each card, tile feature and badge is configured by its own YAML, with the system's `device` ID and the options in the table above.

```yaml
type: custom:saj-local-power-flow-card
device: 0123456789abcdef0123456789abcdef
show_strings: false
show_optional: true
scope: system
```

A tile card takes the weekdays feature on a slot's weekdays entity, and a badge takes the system's `device` ID:

```yaml
type: tile
entity: number.saj_charge_slot_1_days
features:
  - type: custom:saj-local-weekdays
```

```yaml
type: custom:saj-local-status-badge
device: 0123456789abcdef0123456789abcdef
```

### Protecting the inverter

Communication modules can stop serving a client that polls too hard, so the limits below apply to everything the integration sends and cannot be configured away.

- One connection and one request in flight per inverter, with a pause between requests. Checking a connection in Configure uses the installation's own connection rather than a second one.
- At most 40 requests in any 60 seconds per inverter address. The count is kept for as long as Home Assistant runs, so reloading the integration, editing a polling group, a setup retry and the connection check in Configure all draw on the same allowance instead of starting from zero. A request that would exceed this waits; nothing is sent early or dropped. One request reads one block of neighbouring registers, so grouping entities that sit together costs less. At load a warning is logged if your cadences plan more than the limit, and diagnostics show the planned load.
- No retries inside a cycle. After a failed cycle the wait before the next attempt doubles from the shortest interval up to 5 minutes, then the first cycle that succeeds reads everything again. The wait also survives reloads and applies to loading the integration: a load attempted too early reports not ready without contacting the inverter, and a failed load counts as a failure. Checking a connection yourself in setup or Configure is never held back by the wait and still counts towards the 40 requests; a check that passes clears the wait, because the inverter has just answered, and one that fails leaves it as it was.
- Every wait is time-limited, so a stalled inverter ends a cycle as a failure instead of stopping polling silently. A late or stray response is discarded and never read as a value.
- Registers that sit close together are read in one request, and the few words between them are read and discarded. Only registers inside a block the device documents are ever bridged, a request never leaves its block, and a request is never larger than the sizes already in sustained use on each model: 32 registers on the HS3 and 56 on the H2. Without this, disabling an entity would split a block in two and make the load worse. A full read of the default set with a battery and Meter A is 10 requests on an HS3 and 8 on an H2, and a full read of every row with everything fitted is 36 on an HS3 and 17 on an H2. One of those requests reads the battery pack fault words, which lie in a block that nothing else in the default set touches; every other fault word lies in a request the default set already makes.
- Some registers are never polled, whatever is enabled. The HS3 EMS targets and limits count as EMS activity when read, which keeps the inverter under external control, so they are write-only entities. Only the heartbeat reads them, once per interval while you own an EMS function: the target of each owned function, then the five limits. Without an owned function they show the last value you sent. Write-only commands and one HS3 identity register are never read at all. Entities that are not read are not offered in polling groups.
- Writes draw on the same 40 requests as reads and have a smaller allowance inside it: at most 20 write requests in any 60 seconds per inverter address. A change over the allowance is refused, not queued, because a setting applied a minute late is worse than one refused. A change is sent once and never retried or replayed after a reconnect. The switch-off of owned power control functions, on unload and when Home Assistant stops, is the one write the allowance does not refuse, though it is counted against it. The heartbeat reads and so uses no write slot.
- A connection the inverter has closed in the meantime is reopened once and the device is verified; that cycle then reads every enabled entity again, so no value predates the reconnect.

### When the inverter refuses a register

A refusal is an answer, not a failure. Only the entities in the refused request become unavailable and the others keep updating. A request that holds several entities is not retried entity by entity, which would cost one request per entity after a single refusal. Instead the refused request is halved from the next cycle, split at the entity boundary nearest the middle, and halved again while a half is refused, until the refused entity is alone. A half that succeeds returns to normal planning. If both halves succeed, the fault lay in a gap word between them, so that gap is remembered and not bridged again until the integration next loads. A refused region costs at most two requests a cycle while it is narrowed.

After three refusals in a row a lone entity is suspended: shown as unavailable, no longer read, logged once with the exception code and listed in diagnostics. A suspended entity is tried again once a day and whenever the integration loads, and comes back as soon as the register answers. A suspension also raises one repair issue for the installation that lists the affected entities by name. Its fix disables them, as you would yourself, so they are no longer read. Without the fix the issue goes away by itself at the first retest where every listed register answers, at most a day later, or straight away at a reload; it also goes when a listed entity is disabled or its equipment is no longer fitted. An inverter that reports itself busy or failed stops the cycle instead, and every entity is unavailable until it recovers.

### Device faults and repairs

The inverter, the battery and its packs and the EV charger report faults, and each one is a `binary_sensor` with the problem device class, so it has history and can trigger automations. Each piece of equipment has a primary summary (`inverter_fault`, `battery_fault`, `ev_fault`) that is on when anything is reported, a diagnostic entity for every named fault, and an `unrecognised` entity that is on when a bit is set that has no documented meaning on that model. A fault has one key and one name on every model that reports it, so `binary_sensor.saj_inverter_fault_grid_lost` means the same on an HS3 and an H2. A fault a model does not report has no entity there: an H2 has no CT device fault and an HS3 has no islanding fault. Two registers can report the same condition, as grid loss does on both models, and the fault is on when either does. An HS3 has 129 fault entities and an H2 73, all enabled by default. Battery entities exist only when a battery is fitted and EV charger entities only when the charger is fitted. The battery packs add a fault and a warning entity each that is on when the pack's word is not 0, one pack on an HS3 and up to four on an H2 within the pack count; both count towards the battery summary and their codes are in diagnostics.

When a fault register is unavailable or refused, every fault entity that depends on it is unavailable instead of guessing. The registers are read with the other entities of the same block, so no fault adds a request, except the battery packs described under [Protecting the inverter](#protecting-the-inverter). A fault turning on logs one warning naming the installation and the fault, and its clearing one info line. An unrecognised bit turning on logs one warning naming its register and bit. What the HS3 reports is checked against its protocol document only: the fault registers answer on a real HS3 and read 0 while it runs without a fault, but no non-zero reading has been recorded, so a wrong bit position would show as a wrong name or as unrecognised. The EV charger's fault bits are laid out by assumption, because the document does not give the byte order of its fault bytes. The H2 fault bits come from the protocol document, where three English descriptions contradict the Chinese; the Chinese meaning is used.

Home Assistant repairs name the conditions you can act on:

| Repair | Raised when | What it offers |
| --- | --- | --- |
| Wrong model | The device at the address identifies as a different model from the one chosen | A fix that adopts the detected model |
| Different inverter | The device at the address has another serial from the one the installation was set up with | A fix that adopts the new inverter |
| Unrecognised device | The device type is not a known model | Nothing to fix here: choose a model in Configure, where it is used unverified |
| Refused readings | A register is suspended after repeated refusals | A fix that disables the listed entities |
| Not answering | The inverter has failed continuously for 15 minutes; raised at the first failed retry after that, so 15 to 20 minutes into an outage | Nothing to fix: check power, the network and other Modbus clients |

The first three are raised when the integration loads or reconnects, and only one of them is open per installation. The two fixes show the model and serial that the device reports now, then save through the same validation and replacement path as Configure with the model set to Automatic, and reload the installation once. Checking the device for a fix or in Configure closes the installation's connection afterwards and polls straight away, so the installation reconnects and checks the serial again at once. Entity IDs, unique IDs and history are kept, and Allow control and every other setting are unchanged. If the device reports something different from what the form showed, the form says so and shows the new values instead of saving them. The not answering repair is not raised while a model repair is open, and clears at the first good read or when a model repair is raised. Repairs do not survive a Home Assistant restart; each is raised again when its condition recurs. They go away when the installation is removed.

### Diagnostics and debug logging

When something is wrong, two things let you or a maintainer see what the inverter is actually returning and what the integration did about it, without giving away who or where you are. Both use Home Assistant's own tools, so nothing needs installing and nothing is sent anywhere.

**Download diagnostics.** On the integration's page open the three-dot menu of the installation and choose Download diagnostics. The file lists the enabled entity keys, the cadences with the requests each takes, the planned load against the budget, refused and suspended entities, the gaps found that are no longer bridged, and the requests currently being narrowed. For each piece of equipment it lists the raw fault words in hex, the active fault keys and the unrecognised bits as register and bit, together with the battery pack fault and warning codes, the open repair issues with the keys of the refusal repair, and how long the endpoint has been failing. An enumerated value with no known name is listed under its key with its code.

The file also holds a register snapshot, which is what lets a maintainer check a decoding or an address against the real device. `registers` lists the latest raw words of every register the integration has read since it loaded, in hex and ordered by address, including registers that no entity shows and words that were only read because a poll bridged a gap inside a block. A word that belongs to a known setting or reading is grouped under that key; any other word is listed alone with no key. Each entry says how many seconds ago it was read. `failed` lists every request that did not get a usable answer, by start address and count, with its outcome and its age. The outcome is `exception` with the exception code when the inverter refused the request, `timeout` when nothing answered, `connection_lost` when the connection dropped, or `malformed_reply` when the reply did not make sense. The difference matters: the inverter accepts one Modbus TCP connection, so another client holding it makes requests time out in a way that looks like unsupported registers. A failure disappears from the list when the same request later succeeds, while words read earlier at those addresses stay, with their own age. The snapshot adds no request to the inverter; it only remembers what a poll, a heartbeat, a write read-back, equipment detection or the identity check already read, and it starts empty each time the installation loads. The checks made by Setup, Configure and the repair forms use their own connection and are not part of it.

**Debug logging.** On the integration's page choose Enable debug logging from the menu next to the integration's name, reproduce the problem and choose Disable debug logging, which downloads the log of every installation. Debug lines record what the integration did: the identity read at load and on reconnect, each connection opened or closed with the reason, one line per poll with the cadences due, every request and its outcome, how long the cycle took and when it wakes next, the back-off delay and failure count, when a refused request is split and into which halves, each write with its register and the words about to be sent, each EMS heartbeat and each change of a schedule helper. There is one line per event, not one per request, and no decoded value is in the lines added for this. Warnings and information lines are unchanged: one per change of state.

Every log line starts with the installation's title and the serial masked to its last three characters, so lines from two systems can be told apart and matched to the `serial` in diagnostics. A title that contains the serial, as the default `SAJ <serial>` does, has it masked in place (`SAJ xxxxx123`); any other title is followed by the masked serial (`Garage (xxxxx123)`).

**What they leave out.** Neither diagnostics nor logs contain the host, port, unit ID, the full serial, the MAC address, the network addresses, an EV charger's serial, the prefix or polling group names. In the register snapshot the words of those registers, and of the inverter's serial range, are replaced by Home Assistant's redaction marker: the entry is still listed with its key and age, so you can see the register answered without seeing what it said. A write's debug line shows the words it sends except for those registers.

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
