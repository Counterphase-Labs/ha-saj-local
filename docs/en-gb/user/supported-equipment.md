en | [de](../../de/user/supported-equipment.md) | [nl](../../nl/user/supported-equipment.md) | [fr](../../fr/user/supported-equipment.md) | [zh](../../zh-hans/user/supported-equipment.md) | [es](../../es/user/supported-equipment.md) | [it](../../it/user/supported-equipment.md) | [pl](../../pl/user/supported-equipment.md) | [sv](../../sv/user/supported-equipment.md)

# Supported equipment

The Supported equipment page lists the SAJ products SAJ Local supports, the optional equipment each model can have and what is not supported yet. The full list of what setup does is in the [Setup and detection](../../../custom_components/saj_local/docs/features.md#setup-and-detection) section of the integration feature list.

## Supported models

SAJ Local recognises a model from the device type the inverter reports. Any other device type is not recognised.

| Model | Recognised as | Optional equipment SAJ Local detects |
| --- | --- | --- |
| HS3 | Device type `0x1610`, three phases | Battery, Meter A, Meter B, EV charger, parallel system |
| H2, single phase, two solar strings | Device type `0x005a` | Battery, Meter A, Meter B, parallel system |
| H2, single phase, three solar strings | Device type `0x005b` | Battery, Meter A, Meter B, parallel system |

The differences between the models that you see in use:

- **EV charger:** the HS3 only. The H2 has no EV charger entities, EV charger slots or EV charger section on the controls card.
- **Battery packs:** an H2 has entities for up to five battery packs. An HS3 has entities for one battery pack. See [optional equipment](optional-equipment.md).
- **EMS:** the HS3 only. See [changing settings](changing-settings.md#ems).
- **Power control:** the HS3 offers Battery, Grid and Inverter. The H2 offers Battery only. See [power control](power-control.md).

[Optional equipment](optional-equipment.md) explains how detection works and how to override the detection. The [entity reference](entities/README.md) lists which model and which equipment each entity needs.

## Not supported yet

- Automatic detection recognises only the three device types in the table. Other SAJ products, such as the HS2, the H1 and the AS1, are not recognised.
- Other H2 variants, such as the three-phase H2, report other device types and are not recognised automatically. You can choose the model by hand, and SAJ Local then marks the model as unverified. Readings may be wrong, because SAJ Local cannot check the readings. See [get started](getting-started.md#when-the-inverter-is-not-recognised).
- Changing settings on a system whose model is unverified. Reading works, and every change is refused.

## What the support rests on

The HS3 support has been verified by hand on a real HS3. The H2 support rests on SAJ protocol documentation and field reports, and has not been verified by hand on an H2. Writing settings and power control on the H2 also rest on documentation and field reports.
