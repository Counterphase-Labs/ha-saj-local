# Integration Requirements

Global requirements: [requirements.md](../../../.github/work/requirements.md)

## Setup and detection

Features: [Setup and detection](features.md#setup-and-detection)

- Integration domain: `saj_local`; display name: **SAJ Local**.

- Convention over configuration. Configuration options carry sensible defaults

- Avoid extensive configuration options that result in pages of complex config flows

- Automatic detection where possible, with override an option. AKA detect system automatically.

- Connecting to multiple different modbus systems can happen

## Devices and entities

Features: [Devices and entities](features.md#devices-and-entities)

- Each system is one Home Assistant device. A later split into sub-devices keeps the system's device as the base device, so cards and device automations pointing at the system's device keep working.

- Battery and grid power use one sign on every model, in readings and in targets: positive when the battery discharges or the system sends power to the grid, negative when the battery charges or the system takes power from the grid.

## Entity IDs and prefix

Features: [Entity IDs and prefix](features.md#entity-ids-and-prefix)

- Entity IDs are fixed by code, never derived from display text: `<domain>.saj_<key>`, or `<domain>.saj_<prefix>_<key>` when a prefix is set. `<domain>` is the Home Assistant entity type, for example `sensor.saj_pv_power` or `number.saj_backup_reserve_soc`

- Each system has an optional prefix, empty by default

- Prefixes must be unique across systems. Empty counts as a value, so only one system can have no prefix

- A prefix can be added, changed or removed later. The user is warned about the consequences before it is applied

- Changing a prefix renames the entities and must keep their history

## Polling

Features: [Polling](features.md#polling)

- Ability to read only certain sensors or exclude certain sensors

- Ability to configure default sensor update cadence

- Ability to read selected sensors at a higher or lower cadence

- Ability to create one or more different sensor reading cadences

## Protecting the inverter

Features: [Protecting the inverter](features.md#protecting-the-inverter)

- Use intelligent modbus access that does not put the system in danger of overload, especially AIO3 systems

## Changing settings

Features: [Changing settings](features.md#changing-settings)

- Target both reading and writing of registries. Write requires opt in

- Writing is off for every new system. It is switched on per system, with a warning first

- Each system shows whether changes are allowed, so dashboards can show its controls as locked

- Switching writing on also enables the system's controls, and the warning shows the added request load. Switching writing off disables the controls that switching writing on enabled. A control the user disabled or enabled by hand keeps the user's choice

- A system whose model could not be verified is never written to

- Dangerous changes are never made from Home Assistant. Users make them in the SAJ elekeeper app. This covers:
  - Commissioning settings (meter, RS485, battery protocol, network, EV charger link). They are read-only: a wrong value can cut the inverter off from its meter, battery, charger or Home Assistant
  - Actions that cannot be undone (factory reset, clearing energy history). They are not offered

- After a change, the entity shows the value the inverter actually holds

- A failed change says clearly whether the inverter was changed, was not changed, or is in an unknown state

- Changes are rate limited so they cannot overload the inverter

- Controls are shared, not built per model. A control such as a state of charge limit, an export limit or EV charging is defined once and offered by every model that can do it. On a model that cannot do it, or where the equipment is not fitted, the control is not shown.

## EMS

Features: [EMS](features.md#ems)

- EMS functions switched on from Home Assistant are kept alive by a heartbeat, every 60 seconds by default and configurable, and are switched off when Home Assistant stops

## Power control

Features: [Power control](features.md#power-control)

- Power control (holding the battery, the grid connection point or the inverter at a set power) is offered the same way on every model that can do it: the same entities, in watts. How it is done on the inverter belongs to its model

- Optionally, a power control function can follow a Home Assistant schedule helper the user picks. The integration switches the function on when the schedule turns on and off when it turns off

## Model replacement

Features: [Model replacement](features.md#model-replacement)

- Users may upgrade, for example from H2 to HS3. Data loss should be minimal and restricted to cases where sensors are incompatible. A if both systems have solar, total PV power should have continuity. If old had battery and new does not, it is reasonable to expect sensors for battery are no longer available.

## Diagnostics and debug logging

Features: [Diagnostics and debug logging](features.md#diagnostics-and-debug-logging)

- clear and detailed errors with good error handling

- extensive and useful debug dump tools using native HA solutions that are privacy focused

- option to enable debug logging which will provide clear and helpful debug logs rather than spam that creates log fatigue

## Languages

Features: [Languages](features.md#languages)

- Every user-facing text of the integration exists in every target language of the [global requirements](../../../.github/work/requirements.md#language), with the same keys and the same placeholders as the English text.

- Log messages stay in English.

- Entity IDs do not change with the language.

## Cards

Features: [Cards](features.md#cards)

[Cards requirements](../../../frontend/docs/requirements.md)

## SAJ library

- There must be a clear separation of concerns between SAJ modbus integration logic and the Home Assistant platform logic. SAJ must be implemented as a stand alone "library" that is included by the integration. The SAJ module MUST NOT contain any Home Assistant specific code and MUST be able to be tested completely isolated from any HA modules, classes, environment or otherwise.

- Despite SAJ being implemented as a stand alone library, it will not be used anywhere else outside of the integration.
