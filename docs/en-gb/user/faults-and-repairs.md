# Device faults and repairs

The Device faults and repairs page explains how SAJ Local shows the faults that the inverter, the battery and the EV charger report, and which repair issues SAJ Local raises in Home Assistant. The full list of fault behaviour is in the [Device faults and repairs](../../../custom_components/saj_local/docs/features.md#device-faults-and-repairs) section of the integration feature list. Every fault entity is in the [Faults entities](entities/faults.md) of the entity reference.

Device faults and repair issues are separate. A device fault is an entity that reports what the equipment says. A repair issue is a problem with SAJ Local's connection to the equipment or with the set-up of SAJ Local, and Home Assistant lists the issue under Settings and Repairs.

## Device faults

Every named fault of the inverter, the battery and the EV charger is a binary sensor with the problem device class, enabled by default. A fault has history and can trigger an automation.

- **Summary:** the inverter, the battery and the EV charger each have a summary fault, for example Inverter fault, that is on when the equipment reports anything.
- **Unrecognised:** each piece of equipment also has an unrecognised fault that is on when the inverter sets a bit with no documented meaning. The [diagnostics download](troubleshooting.md#download-diagnostics) lists the register and the bit, so you can report the bit.
- **One entity ID on every model:** a fault has one entity ID on every model that reports the fault. A fault that a model does not report has no entity on that model.
- **Battery packs:** each battery pack has a fault and a warning entity. An HS3 has one pack. An H2 has up to four.
- **Equipment that is not fitted:** battery faults exist only when a battery is fitted, and EV charger faults only when an EV charger is fitted. See [optional equipment](optional-equipment.md).
- **A fault register that cannot be read:** the faults that depend on the register are unavailable. SAJ Local does not guess.
- **The log:** a fault that turns on logs one warning that names the system and the fault. When the fault clears, SAJ Local logs one information line.

The [faults card](cards/faults-card.md) lists the active faults of a system on a dashboard, with how long ago each began. The Clear fault button of the card sends the Clear current fault command, which needs [Allow control](changing-settings.md#allow-control).

## Repair issues

SAJ Local raises a repair issue for a condition you can act on.

| Repair issue | Raised when | What you can do |
| --- | --- | --- |
| The system is set to the wrong model | The inverter at the address identifies as another model than the one chosen. | A fix adopts the model that SAJ Local found. See [replacing the inverter](replacing-the-inverter.md). |
| The system now reaches a different inverter | The inverter at the address has another serial number. | A fix adopts the new inverter. See [replacing the inverter](replacing-the-inverter.md). |
| The system reaches an unrecognised device | The device type is not a recognised model. | Choose the model in Configure. SAJ Local then uses the model unverified. |
| The system has readings the inverter refuses | The inverter refused the readings three times in a row. | A fix disables the listed entities, so SAJ Local no longer reads the entities. See [protecting the inverter](protecting-the-inverter.md#when-the-inverter-refuses-a-reading). |
| The system has stopped answering | The inverter has not answered for 15 minutes. | Check the power, the network and other Modbus clients. The issue goes away at the first good reading. |
| Equipment is no longer detected | Equipment that SAJ Local detected before is no longer detected. | Check the equipment, or set the equipment to Not fitted in Configure. See [optional equipment](optional-equipment.md#when-remembered-equipment-is-no-longer-detected). |

![A repair issue in Home Assistant that says SAJ HS3MOCK000000000003 has readings the inverter refuses](../../images/en-gb/faults-and-repairs-repair-issue.png)

The first three issues are the model issues. Only one of the model issues is open for a system, and the issue that the system has stopped answering is not raised while a model issue is open.

A repair issue goes away when the condition of the issue ends, or when you remove the system. The issue about refused readings also goes away when you disable a listed entity.

## Not supported yet

- A repair issue for a device fault. Device faults are entities, and the integration does not raise a repair issue for a fault.
