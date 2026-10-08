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

> **Status: in active development and not yet released.** The first working iteration supports read-only monitoring of one or more SAJ HS3 or H2 inverters over local Modbus TCP. There is no published release yet.

## What it is being built to deliver

### Works the way you expect

- **Sensible by default.** Add your inverter and get a working setup without wading through pages of options.
- **Finds your system for you.** The inverter, battery and related equipment are detected automatically, with an override when you know better.
- **Consistent sensor names across SAJ models.** Dashboards and automations are written once and keep working across models.
- **Survives hardware upgrades.** Moving from an H2 to an HS3, for example, keeps your history continuous where the systems overlap, such as total PV power. Sensors that no longer apply, such as a battery you no longer have, simply go away.
- **Multiple systems.** Connect more than one SAJ system to the same Home Assistant.

### Gentle on your inverter

- **Careful Modbus access.** One connection per inverter, one request at a time, and a hard ceiling of 40 requests in any 60 seconds per inverter address that no setting, reload or failure can exceed, with particular care for AIO3 systems.
- **You choose what is read.** Disable a sensor in Home Assistant and its register is no longer read.
- **Update cadences you control.** Set a default refresh rate and create polling groups that read selected sensors faster or slower.

### Read, and when you want it, write

- **Read-only unless you say otherwise.** Writing registers is opt-in, so nothing changes on your inverter by accident.

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

**Sensors** covers reading values from the inverter and **Controls** covers changing its settings. The initial iteration exposes operating mode, solar power, battery power, battery charge, total grid power and household load on both the HS3 and the H2. The remaining columns are optional equipment and operating modes.

The HS3 register behaviour has been verified by hand. The H2 behaviour comes from SAJ protocol documentation and field observations of H2-family units, and has not been hand-verified on an H2 by this project.

## Installation

There is no published release yet. The development integration can be added through Home Assistant using the inverter's host, Modbus TCP port (default `502`) and unit ID (default `1`). The **Model** field defaults to Automatic, which identifies an HS3 or an H2 from the device itself. Choose a model manually only when the inverter is not recognised: a selection that contradicts a recognised device is rejected, and a selection applied to an unrecognised device is saved only after its required registers answer and you confirm it. Home Assistant's sensor controls disable readings that are not needed. The default update interval is 60 seconds and no interval can be shorter than 10 seconds.

Moving an installation between an H2 and an HS3 is done through Configure. Confirm the replacement and the device, entities, names and history stay with the installation.

### Limitations

- Automatic detection recognises the HS3 and the single-phase H2 only. Other H2-family units, such as the three-phase H2, report other device types and need the model chosen manually, with readings that may be wrong because they cannot be verified.
- AS2, HS2 and other SAJ products are not recognised.
- The sign of total grid power is published as the inverter reports it and is not labelled as import or export.

[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=dogmatic69&repository=home-assistant-saj-modbus&category=integration)
[![Open your Home Assistant instance and start setting up SAJ Local.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=saj_local)

## How it works

The integration connects to your inverter over Modbus TCP on your local network and reads its registers on a schedule you control. All communication stays between Home Assistant and the inverter.

### Polling groups

By default every sensor is read at the installation's update interval. To read some sensors faster or slower, open the integration page, choose **Add polling group** and give the group a name, a number of seconds between updates (at least 10) and the sensors it holds. Edit or delete a group from the same page. A sensor belongs to at most one group, and every sensor in no group stays on the default interval.

Changing a group reloads the integration once. It never touches the sensors themselves: moving a sensor between groups, removing it from a group or deleting the group keeps the entity, its name and its history.

All cadences of an installation share one clock, so a 10 second group and a 60 second default are read together every sixth tick, in one combined read where registers are next to each other. A cycle that overruns is not caught up: the missed ticks are dropped and polling carries on from the next tick.

### Protecting the inverter

Communication modules can stop serving a client that polls too hard, so the limits below apply to everything the integration sends and cannot be configured away.

- One connection and one request in flight per inverter, with a pause between requests. Checking a connection in Configure uses the installation's own connection rather than a second one.
- At most 40 requests in any 60 seconds per inverter address. The count is kept for as long as Home Assistant runs, so reloading the integration, editing a polling group, a setup retry and the connection check in Configure all draw on the same allowance instead of starting from zero. A request that would exceed this waits; nothing is sent early or dropped. One request reads one block of neighbouring registers, so grouping sensors that sit together costs less. At load a warning is logged if your cadences plan more than the limit, and diagnostics show the planned load.
- No retries inside a cycle. After a failed cycle the wait before the next attempt doubles from the shortest interval up to 5 minutes, then the first cycle that succeeds reads everything again. The wait also survives reloads and applies to loading the integration: a load attempted too early reports not ready without contacting the inverter, and a failed load counts as a failure. Checking a connection yourself in setup or Configure is never held back by the wait and still counts towards the 40 requests; a check that passes clears the wait, because the inverter has just answered, and one that fails leaves it as it was.
- Every wait is time-limited, so a stalled inverter ends a cycle as a failure instead of stopping polling silently. A late or stray response is discarded and never read as a value.
- A connection the inverter has closed in the meantime is reopened once and the device is verified; that cycle then reads every enabled sensor again, so no value predates the reconnect.

### When the inverter refuses a register

A refusal is an answer, not a failure. Only the sensor in the refused request becomes unavailable and the others keep updating. From the next cycle that sensor is read on its own. After three refusals in a row it is suspended: shown as unavailable, no longer read, logged once with the exception code and listed in diagnostics. A suspended sensor is tried again once a day and whenever the integration loads, and comes back as soon as the register answers. An inverter that reports itself busy or failed stops the cycle instead, and every sensor is unavailable until it recovers.

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
