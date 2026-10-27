en | [de](../../de/user/README.md) | [nl](../../nl/user/README.md) | [fr](../../fr/user/README.md) | [zh](../../zh-hans/user/README.md) | [es](../../es/user/README.md) | [it](../../it/user/README.md) | [pl](../../pl/user/README.md) | [sv](../../sv/user/README.md)

# SAJ Local user documentation

SAJ Local is a local Home Assistant integration. SAJ Local reads a SAJ HS3 or H2 solar system straight from the inverter over Modbus TCP on your own network and, when you allow control, changes the settings of the inverter from Home Assistant. SAJ Local needs no cloud account, and limits the requests to the inverter so the communication module of the inverter keeps working.

SAJ Local is an unofficial, community-built integration. SAJ does not make, support or endorse SAJ Local. See the [disclaimer](#disclaimer).

SAJ Local is in development and has no published release yet. Each page below states what is not supported yet. The documentation covers the HS3 and the H2, and marks the differences with a note such as "HS3 only". The screenshots come from simulated systems, so the readings are not real.

## Start here

1. [Install SAJ Local](installation.md) with HACS.
2. Check that your inverter is in the [supported equipment](supported-equipment.md).
3. [Get started](getting-started.md): add your first system.
4. Read about [optional equipment](optional-equipment.md), which SAJ Local detects for you.

## Understand your system

- [Entities and the prefix](entities-and-prefix.md): what the entities are, how the entity IDs are formed and how to add a prefix.
- [Entity reference](entities/README.md): every entity, with the entity ID, the models, the equipment and the default. Generated from the integration.
- [Polling](polling.md): how often the inverter is read, and how to read some entities faster or slower.
- [Protecting the inverter](protecting-the-inverter.md): the limits SAJ Local keeps on the requests of SAJ Local.

## Change things

- [Changing settings](changing-settings.md): allow control, change settings and use EMS.
- [Power control](power-control.md): hold the battery, the grid connection or the inverter at a set power, by hand or with a schedule.
- [Replacing the inverter](replacing-the-inverter.md): move a system to a new inverter, or between an H2 and an HS3, and keep the history.

## Dashboards

- [Dashboard cards](cards/README.md): the cards, the tile card feature and the badge that SAJ Local adds to Home Assistant.

## Terms

- [Nomenclature](nomenclature.md): the SAJ and Home Assistant terms that the integration, the cards and the documentation use, with their meaning.

## When something is wrong

- [Device faults and repairs](faults-and-repairs.md): the faults that the equipment reports and the repair issues that SAJ Local raises.
- [Troubleshooting](troubleshooting.md): diagnostics, debug logging and where to ask for help.

## What each part can do

The feature lists say what is built today: [the integration](../../../custom_components/saj_local/docs/features.md) and [the cards](../../../frontend/docs/features.md).

Developers: see the [developer documentation](../developer/README.md).

## Disclaimer

SAJ Local is an independent, community-built integration. SAJ Local is not affiliated with SAJ (Guangzhou Sanjing Electric Co., Ltd.), and SAJ and the subsidiaries and affiliates of SAJ have not authorised, sponsored or endorsed SAJ Local.

SAJ, the SAJ logo and all related product names, model names and trademarks are the property of the respective owners. The documentation uses the names only to identify the equipment that SAJ Local works with.

The software is provided as is, without warranty of any kind. You use SAJ Local at your own risk: the authors accept no liability for damage to equipment, loss of data, loss of warranty or any other consequence of using SAJ Local. The warning applies in particular to writing settings to your inverter.

## Acknowledgements

H2 support builds on the register research and field testing of stanus74 in [SAJ H2 Modbus](https://github.com/stanus74/home-assistant-saj-h2-modbus). Thank you.
