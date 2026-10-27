en | [de](../../de/user/replacing-the-inverter.md) | [nl](../../nl/user/replacing-the-inverter.md) | [fr](../../fr/user/replacing-the-inverter.md) | [zh](../../zh-hans/user/replacing-the-inverter.md) | [es](../../es/user/replacing-the-inverter.md) | [it](../../it/user/replacing-the-inverter.md) | [pl](../../pl/user/replacing-the-inverter.md) | [sv](../../sv/user/replacing-the-inverter.md)

# Replacing the inverter

The Replacing the inverter page explains how to move a system to a new inverter, or between an H2 and an HS3, and keep the device, the entities and the history. The full list is in the [Model replacement](../../../custom_components/saj_local/docs/features.md#model-replacement) section of the integration feature list.

## Move a system on purpose

1. Make sure the new inverter is reachable. If the new inverter has another address, you enter the address in the next step.
2. Open Configure, the gear on the system's row on the SAJ Local integration page.
3. Change the host, port or unit ID if the address changed. Leave Model on Automatic, or choose the model if the inverter is not recognised.
4. Choose Submit, then confirm the replacement. The confirmation names the model and the serial number that SAJ Local found.

After you confirm, the device, the entities, the names of the entities and the history stay with the system. An entity keeps the history across the move when both models have the entity. SAJ Local forgets the equipment detected on the old inverter and the battery pack count of the old inverter, and detects the equipment again on the new inverter.

## When the inverter at the address changes without you

SAJ Local checks the identity of the inverter every time the system loads. When the inverter at the address identifies as another model, or has another serial number, SAJ Local does not load the system and raises a repair issue. The fix of the repair issue shows the model and the serial number that the inverter reports now, and adopts the inverter you confirm.

- Entity IDs, history, Allow control and every other setting stay unchanged.
- When the inverter reports something different from what the form showed, the form says so and shows the new values instead of saving the old values.
- When the device at the address is not a recognised model, a repair issue says so and points to Configure. There is nothing to adopt. Choose the model by hand, see [get started](getting-started.md#when-the-inverter-is-not-recognised).

The repair issues are listed in [faults and repairs](faults-and-repairs.md#repair-issues).

## Not supported yet

- Adopting an inverter that already belongs to another system. SAJ Local refuses the adoption.
