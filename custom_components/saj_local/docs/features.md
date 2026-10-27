# Integration Features

SAJ Local brings an SAJ HS3 or H2 solar system into Home Assistant, read and, when allowed, controlled straight from the inverter over Modbus TCP on the local network. Nothing is sent to a cloud service.

## Setup and detection

A system is added with the inverter's network address and is recognised from the device itself. Setup asks only for what cannot be found out.

Files: [config_flow.py](../config_flow.py), [\_\_init\_\_.py](../__init__.py), [device.py](../saj/device.py), [profiles.py](../saj/profiles.py), [telemetry.py](../saj/telemetry.py)

Requirements: [Setup and detection](requirements.md#setup-and-detection)

- A system is added with its host, Modbus TCP port (502 by default) and unit ID (1 by default, from 1 to 247).
- The model is Automatic by default, which recognises the HS3 and the single-phase H2 from the device type the inverter reports.
- The HS3 or the H2 can be chosen by hand when the inverter is not recognised. A choice that contradicts a recognised inverter is refused. A choice for an unrecognised inverter is saved only after its required readings answer and you confirm it, and the device then shows the model as unverified.
- Setup needs only the identity and six core readings to answer: operating mode, battery state of charge, load power, solar power, battery power and grid power. A register one unit lacks does not block setup.
- Several SAJ systems can be added to one Home Assistant. An endpoint or inverter serial that is already set up is refused.
- A failed setup says what went wrong: no connection, no answer in time, a refused reading, invalid data, an unrecognised device or a wrong model.
- Host, port, unit ID, update interval and model can be changed later in Configure, and are saved only after the endpoint is checked.

## Devices and entities

Each system is one Home Assistant device, and every reading, setting and command the integration knows for the model is one of its entities.

Files: [entity.py](../entity.py), [sensor.py](../sensor.py), [binary_sensor.py](../binary_sensor.py), [number.py](../number.py), [select.py](../select.py), [switch.py](../switch.py), [time.py](../time.py), [button.py](../button.py), [catalogue.py](../saj/catalogue.py), [definitions.py](../saj/definitions.py)

Requirements: [Devices and entities](requirements.md#devices-and-entities)

- Each system is one device named SAJ. The device's model shows the model and rated power, for example "HS3 (12000 W)", with "unverified" added when the model could not be verified. A new system is titled SAJ and its serial number.
- Entities come in seven types: sensors, binary sensors, numbers, selects, switches, times and buttons, so each setting has the control Home Assistant users expect.
- Only a core set is enabled by default: power, voltage, temperature and state of charge readings, the energy counters, the main battery limits and every fault. Everything else is created disabled.
- A disabled entity is not read from the inverter. Enabling an entity adds it to the next read.
- A device gets only the entities that fit it, so an H2 with one solar string has no second-string entities. A system on a model chosen by hand for an unrecognised inverter gets every entity of the model, with those beyond one phase and two strings disabled.
- Settings are in the configuration category. Versions, commissioning settings and network settings are in the diagnostic category.
- A register that packs several values is read once, and each value is its own entity.
- Readings cover the inverter output and the backup port per phase, each solar string, the grid per phase, Meter A and Meter B, the battery and each battery pack, the household load, and the energy of today, this month, this year and in total for solar, load, backup load, battery charge, battery discharge, grid import and grid export.
- The HS3 also has five-minute averages of its readings. A parallel system adds the readings of the whole parallel system.
- Versions, network settings, the inverter clock, the limits the inverter is applying and the installer settings are readings in the diagnostic category.
- The H2 has identity entities for each battery pack, created disabled.
- Battery power and grid power use one sign on every model: battery power is positive while the battery discharges, and grid power is positive while the system exports. Meter A follows the grid sign. Meter B reads positive while its solar inverter generates.
- An option code with no known name shows as unknown, and diagnostics list the code so it can be reported.

## Optional equipment

The integration checks which optional equipment the inverter has every time it loads, and creates entities only for what is fitted.

Files: [equipment.py](../equipment.py), [equipment.py (SAJ library)](../saj/equipment.py), [detection.py](../saj/detection.py), [config_flow.py](../config_flow.py), [issues.py](../issues.py)

- The battery, Meter A, Meter B and a parallel system are detected on both models. The EV charger is detected on the HS3 only.
- When the inverter does not answer the check, a battery and Meter A are assumed and the other equipment is not.
- Detected equipment is remembered, so a meter that is offline during a restart keeps its entities.
- When remembered equipment is no longer detected, a repair issue names the equipment and the system, and the equipment's entities stay.
- The Equipment section of Configure sets each piece of equipment to Automatic, Fitted or Not fitted, and says what is treated as fitted now. Not fitted removes the equipment's entities, including your changes to them. Entity IDs stay the same, so history continues if the equipment is fitted again.
- The H2 limits its battery pack entities to the pack count the inverter reports, up to five packs. A count of 0 keeps every pack. The highest count seen is remembered. The HS3 has entities for one pack.
- An HS3 with an EV charger also gets the EV charger's readings, settings, charging slots and EMS charging controls.

## Entity IDs and prefix

Entity IDs are fixed by the integration, so dashboards and automations work the same on every model and every system.

Files: [const.py](../const.py), [config_flow.py](../config_flow.py), [entity.py](../entity.py)

Requirements: [Entity IDs and prefix](requirements.md#entity-ids-and-prefix)

- Every entity ID has the form `<type>.saj_<key>`, for example `sensor.saj_pv_power`. Renaming an entity's display name does not change the ID.
- An optional prefix per system adds a word to every entity ID, for example `sensor.saj_house_pv_power`, so a second system never gets `_2` IDs.
- A prefix uses lowercase letters and digits only, up to 32 characters. Two systems cannot share a prefix, and only one system can have none. A prefix that would clash with an entity name, such as `battery`, is refused.
- Setup is refused when an entity ID the system would create is already taken. When a later entity's ID is taken, Home Assistant adds a number to the ID and a warning names the entity's kind and key.
- The prefix can be added, changed or removed in Configure. The old and new patterns are shown with a warning that automations, scripts, dashboards, templates and Energy settings using the old IDs stop working until updated.
- A prefix change renames every entity of the system, enabled or disabled, and moves history and long-term statistics to the new IDs. Entities you renamed yourself are left alone.
- A prefix change is refused, and nothing is renamed, when a new ID is taken or Home Assistant already holds long-term statistics under a new ID.

## Polling

You choose what is read and how often, and the integration shows what each choice costs the inverter.

Files: [config_flow.py](../config_flow.py), [schedule.py](../saj/schedule.py), [load.py](../saj/load.py), [poller.py](../saj/poller.py), [coordinator.py](../coordinator.py)

Requirements: [Polling](requirements.md#polling)

- Every enabled entity is read every 60 seconds by default. The interval can be changed in Configure and is never shorter than 10 seconds.
- Polling groups read chosen entities faster or slower than the default. A group has a name, an interval and its entities, of any type, and an entity belongs to one group at most.
- The polling group form lists entities in register order, each labelled with the block it is read from, so entities that can share a request sit together. Disabled entities can be chosen too.
- Before a polling group is saved, a review step shows the requests one read of the group takes and the load before and after, as requests per minute against the limit of 40. The group can still be saved when it goes over the limit, with a warning that reads will run slower.
- Configure shows the current load and asks for confirmation when a new default interval goes over the limit.
- Changing or deleting a polling group keeps the entities, their names and their history.
- All intervals of a system share one clock, so entities due together are read together. A read that overruns is not caught up.

## Protecting the inverter

The integration limits everything it sends, so the inverter's communication module is never overloaded. None of these limits can be configured away.

Files: [client.py](../saj/client.py), [budget.py](../saj/budget.py), [guard.py](../saj/guard.py), [health.py](../saj/health.py), [telemetry.py](../saj/telemetry.py), [poller.py](../saj/poller.py), [issues.py](../issues.py), [repairs.py](../repairs.py)

Requirements: [Protecting the inverter](requirements.md#protecting-the-inverter)

- Each inverter gets one connection and one request at a time, with a short pause between requests.
- No more than 40 requests go to an inverter address in any 60 seconds. The count survives reloads, so a reload, a setup retry or a connection check cannot exceed the limit. A request over the limit waits.
- Neighbouring registers are read in one request, never beyond a block the model documents and never larger than 32 registers on the HS3 or 56 on the H2.
- A failed read is not retried in the same cycle. The wait before the next attempt doubles from the shortest interval, up to 5 minutes, and survives reloads.
- Every wait has a time limit, so a stalled inverter ends a cycle as a failure instead of stopping polling. A late or stray answer is discarded.
- A connection the inverter closed is reopened once, and that cycle reads every enabled entity again.
- When the inverter refuses a reading, only the entities in that request become unavailable. The request is split in halves over the next cycles until the refused entity is found.
- An entity refused three times in a row is no longer read. The entity is tried again once a day and whenever the integration loads, and a repair issue lists the entities, with a fix that disables them.
- A repair issue says when an inverter has not answered for 15 minutes, and goes away at the first good reading.

## Changing settings

Writing to the inverter is off until you allow control for a system, and every change is checked, sent once and read back.

Files: [control.py](../saj/control.py), [controls.py](../controls.py), [errors.py](../errors.py), [config_flow.py](../config_flow.py), [binary_sensor.py](../binary_sensor.py), [button.py](../button.py)

Requirements: [Changing settings](requirements.md#changing-settings)

- Allow control is off for every new system. Switching Allow control on, in setup or Configure, asks for confirmation with a warning about what a wrong setting can do and the added request load. Switching Allow control off needs no confirmation.
- While Allow control is off, settings show their current value but refuse every change with a message saying where to switch control on, and nothing is sent.
- Each system has a Control allowed binary sensor, on while the system accepts changes.
- Switching Allow control on enables the system's control set: the slot, mode, battery, grid, EV charger and power control entities, the LED mode, the H2's buzzer, and the clock and fault commands. Switching Allow control off disables the entities the integration enabled. An entity you enabled or disabled yourself keeps your choice.
- A change is refused with its own message when control is off, the model is unverified, the setting is a commissioning setting, the value is invalid, the inverter is unreachable or the write limit is reached. The inverter is not changed.
- A change is written once and read back, and the entity shows the value the inverter holds. When the inverter refuses the change, the message gives its exception code. When no answer comes, the message says the change may or may not have been applied, and nothing is sent again. When the inverter holds a different value, the entity shows that value and the change fails.
- A change to one setting of a packed register leaves the other settings in the register untouched.
- Settings cover the application mode, seven charge slots and seven discharge slots (each with start, end, power, days and on or off), the time-of-use idle mode and grid discharge, the backup reserve, the battery charge and discharge limits, battery auto wake, the export limit, the grid import and export power limits and the passive mode powers. An HS3 with an EV charger adds the charger's settings and seven EV charger slots.
- Commissioning settings are shown but cannot be changed: the meter, RS485, the battery protocol, the network and the EV charger link, and on the H2 also the grid type, the parallel set-up, the input modes, the protection limits and other installer settings.
- No more than 20 changes go to an inverter address in any 60 seconds. A change over the limit is refused, not queued.
- A system on a model that could not be verified is never written to.
- Buttons clear the current fault, restart the inverter and synchronise the inverter clock with Home Assistant's local time, and on the HS3 remove the EMS solar power limit. The buttons are created disabled.
- The H2 also has a buzzer switch and a battery forced charge power limit. Both models have the LED mode.

## EMS

On the HS3, EMS puts the inverter under external control. The integration keeps the EMS functions it switched on alive and switches them off when it stops.

Files: [ems.py](../saj/ems.py), [coordinator.py](../coordinator.py), [config_flow.py](../config_flow.py), [number.py](../number.py)

Requirements: [EMS](requirements.md#ems)

- EMS exists on the HS3 only. The EMS timeout and five limits (battery charge and discharge current, inverter import and export power, and solar power) are entities. The limits can be set but are not polled. Between heartbeats they show the last value sent, and are unknown before the first change.
- EMS functions switched on from Home Assistant are kept alive by a heartbeat that reads each function's target and the limits. Reading keeps the function alive, so the heartbeat writes nothing.
- The EMS heartbeat is 60 seconds by default and can be set from 30 to 3600 seconds, in the Allow control confirmation at setup and in Configure.
- An EMS function cannot be switched on while the inverter's EMS timeout is not longer than the heartbeat, and the timeout cannot be set that low.
- When the integration unloads or Home Assistant stops, the EMS functions switched on from Home Assistant are switched off. A function that was already on when the integration loaded is left alone.
- The switch-off on stop is a best effort. When the inverter cannot be reached or Home Assistant stops abruptly, the functions stay on until the inverter's own EMS timeout ends them.

## Power control

Power control holds the battery, the grid connection point or the inverter at a set power in watts, the same way on every model that can do it.

Files: [power_control.py](../saj/power_control.py), [coordinator.py](../coordinator.py), [switch.py](../switch.py), [number.py](../number.py), [config_flow.py](../config_flow.py)

Requirements: [Power control](requirements.md#power-control)

- The HS3 offers Battery, Grid and Inverter power control. The H2 offers Battery power control only.
- Each function has a switch and a power target in whole watts, created disabled and in the configuration category. A positive power discharges, exports or puts out. A negative power charges, imports or takes in.
- The power target is rounded to the nearest step the inverter supports, and shows the power the inverter holds.
- A function needs a power target before it can be switched on. The target is kept across restarts and sent when the function starts. Changing the target while the function runs sends the new power at once.
- Only one function runs at a time. Switching on a function while another runs is refused with a message naming the running function.
- The switch is on while the inverter reports the function running, even when the function was started outside Home Assistant.
- A function switched on from Home Assistant is switched off when the integration unloads or Home Assistant stops. On the H2 a function left running by an abrupt stop keeps running.
- A start that fails is undone, and a stop that fails is sent again every heartbeat interval until the inverter reports the function stopped.
- A power control schedule makes a function follow a Home Assistant schedule helper: on while the schedule is on, off when it turns off. A schedule block can carry a power in watts, otherwise the function's power target is used.
- Each function follows one schedule, and a schedule helper drives one function per system. A schedule follows a rename of its helper. A schedule cannot be added while Allow control is off.
- Power control does nothing while Allow control is off or the model is unverified.

## Model replacement

A system keeps its device, entities and history when the inverter behind it is replaced.

Files: [config_flow.py](../config_flow.py), [repairs.py](../repairs.py), [issues.py](../issues.py)

Requirements: [Model replacement](requirements.md#model-replacement)

- A system moves between an H2 and an HS3, or to a new inverter, through Configure. After you confirm, the device, entities, names and history stay with the system. An entity keeps its history across the move when both models have it.
- When the inverter at a system's address identifies as another model, or has another serial, the system is not loaded and a repair issue offers to adopt the inverter found, keeping entity IDs, history, Allow control and every other setting.
- When the device at the address is not a recognised model, a repair issue says so and points to Configure.

## Device faults and repairs

The faults the inverter, the battery and the EV charger report are binary sensors, so they have history and can trigger automations.

Files: [binary_sensor.py](../binary_sensor.py), [faults.py](../saj/faults.py), [faults.py (models)](../saj/models/faults.py), [shared_faults.py](../saj/models/shared_faults.py), [hs3.py](../saj/models/hs3.py), [h2.py](../saj/models/h2.py), [coordinator.py](../coordinator.py)

- Every named fault of the inverter, the battery and the EV charger is a problem binary sensor, enabled by default.
- The inverter, the battery and the EV charger each have a summary fault that is on when anything is reported, and an unrecognised fault that is on when a bit with no documented meaning is set.
- A fault has the same entity ID on every model that reports it. A fault a model does not report has no entity there.
- Each battery pack has a fault and a warning entity: one pack on the HS3 and up to four on the H2.
- When a fault register cannot be read, the faults that depend on it are unavailable instead of guessed.
- A fault turning on logs one warning naming the system and the fault, and its clearing logs one information line.
- Battery faults exist only when a battery is fitted, and EV charger faults only when an EV charger is fitted.
- A device fault raises no repair issue. The repair issues SAJ Local raises belong to other sections: the wrong model, a different inverter and an unrecognised device to [Model replacement](#model-replacement), refused readings and an inverter that has stopped answering to [Protecting the inverter](#protecting-the-inverter), and equipment no longer detected to [Optional equipment](#optional-equipment).

## Diagnostics and debug logging

Home Assistant's own diagnostics download and debug logging show what the inverter returns and what the integration did, without giving away who or where you are.

Files: [diagnostics.py](../diagnostics.py), [memory.py](../saj/memory.py), [label.py](../label.py), [log.py](../saj/log.py), [errors.py](../errors.py)

Requirements: [Diagnostics and debug logging](requirements.md#diagnostics-and-debug-logging)

- The diagnostics download lists the enabled entities, the intervals with the requests each takes, the planned load against the limit, refused and suspended entities, active faults with their raw words, unrecognised fault bits, open repair issues, how long the inverter has been failing, and the power control functions with which is running, which is owned and each schedule's outstanding action.
- The diagnostics download includes a snapshot of the raw words of every register read since the integration loaded, with the age of each, and every request that got no usable answer, with the reason.
- Debug logging records each connection, poll, request, write, heartbeat and schedule change, one line per event.
- Every log line starts with the system's title and the serial masked to its last three characters, so lines from two systems can be told apart.
- Diagnostics and logs never contain the host, port, unit ID, full serial, MAC address, network addresses, EV charger serial, prefix or polling group names.
- Every error the integration raises says what went wrong and whether the inverter was changed.

## Languages

Every text the integration shows to users exists in English and in every target language, so a Home Assistant user sees SAJ Local in the language of the user's profile.

Files: [en.json](../translations/en.json), [de.json](../translations/de.json), [nl.json](../translations/nl.json), [fr.json](../translations/fr.json), [zh-Hans.json](../translations/zh-Hans.json), [es.json](../translations/es.json), [it.json](../translations/it.json), [pl.json](../translations/pl.json), [sv.json](../translations/sv.json)

Requirements: [Languages](requirements.md#languages)

- English (`en.json`), German (`de.json`), Dutch (`nl.json`), French (`fr.json`), Simplified Chinese (`zh-Hans.json`), Spanish (`es.json`), Italian (`it.json`), Polish (`pl.json`) and Swedish (`sv.json`).
- Setup and options forms, entity names and states, repair issues and error messages are translated.
- Every language has the same keys and placeholders as English.
- Log messages stay in English.
- Entity IDs are the same in every language.

## Cards

The integration serves its own dashboard cards. The cards are listed in [the cards' feature list](../../../frontend/docs/features.md).

Files: [frontend.py](../frontend.py)

Requirements: [Cards](requirements.md#cards)

- The integration registers its cards, tile card feature and badge with Home Assistant when Home Assistant starts, so they appear in the card picker with no resource to add.
