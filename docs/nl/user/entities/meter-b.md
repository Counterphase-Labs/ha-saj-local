[en](../../../en-gb/user/entities/meter-b.md) | [de](../../../de/user/entities/meter-b.md) | nl | [fr](../../../fr/user/entities/meter-b.md) | [zh](../../../zh-hans/user/entities/meter-b.md) | [es](../../../es/user/entities/meter-b.md) | [it](../../../it/user/entities/meter-b.md) | [pl](../../../pl/user/entities/meter-b.md) | [sv](../../../sv/user/entities/meter-b.md)

# Meter B

Meter B, de tweede meter die een zonne-omvormer meet.

De functielijst van de integratie legt de Meter B-entiteiten uit in [Optionele apparatuur](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

22 entiteiten. Gegenereerd door `make docs`. Niet met de hand bewerken.

Een voorvoegsel dat in Configureren is ingesteld komt na `saj_` in de ID van elke Meter B-entiteit, bijvoorbeeld `sensor.saj_house_meter_b_l1_voltage` met het voorvoegsel `house`.

| Naam | Entiteits-ID | Type | Eenheid | Modellen | Apparatuur en aantallen | Standaard ingeschakeld |
| --- | --- | --- | --- | --- | --- | --- |
| Meter B L1 spanning | `sensor.saj_meter_b_l1_voltage` | Sensor | V | HS3, H2 | Meter B | Nee |
| Meter B L1 stroom | `sensor.saj_meter_b_l1_current` | Sensor | A | HS3, H2 | Meter B | Nee |
| Meter B L1 vermogen | `sensor.saj_meter_b_l1_power` | Sensor | W | HS3, H2 | Meter B | Nee |
| Meter B L1 schijnbaar vermogen | `sensor.saj_meter_b_l1_apparent_power` | Sensor | VA | HS3, H2 | Meter B | Nee |
| Meter B L1 arbeidsfactor | `sensor.saj_meter_b_l1_power_factor` | Sensor | - | HS3, H2 | Meter B | Nee |
| Meter B L1 frequentie | `sensor.saj_meter_b_l1_frequency` | Sensor | Hz | HS3, H2 | Meter B | Nee |
| Meter B L2 spanning | `sensor.saj_meter_b_l2_voltage` | Sensor | V | HS3, H2 | Meter B; Fase 2 en hoger | Nee |
| Meter B L2 stroom | `sensor.saj_meter_b_l2_current` | Sensor | A | HS3, H2 | Meter B; Fase 2 en hoger | Nee |
| Meter B L2 vermogen | `sensor.saj_meter_b_l2_power` | Sensor | W | HS3, H2 | Meter B; Fase 2 en hoger | Nee |
| Meter B L2 schijnbaar vermogen | `sensor.saj_meter_b_l2_apparent_power` | Sensor | VA | HS3, H2 | Meter B; Fase 2 en hoger | Nee |
| Meter B L2 arbeidsfactor | `sensor.saj_meter_b_l2_power_factor` | Sensor | - | HS3, H2 | Meter B; Fase 2 en hoger | Nee |
| Meter B L2 frequentie | `sensor.saj_meter_b_l2_frequency` | Sensor | Hz | HS3, H2 | Meter B; Fase 2 en hoger | Nee |
| Meter B L3 spanning | `sensor.saj_meter_b_l3_voltage` | Sensor | V | HS3, H2 | Meter B; Fase 3 en hoger | Nee |
| Meter B L3 stroom | `sensor.saj_meter_b_l3_current` | Sensor | A | HS3, H2 | Meter B; Fase 3 en hoger | Nee |
| Meter B L3 vermogen | `sensor.saj_meter_b_l3_power` | Sensor | W | HS3, H2 | Meter B; Fase 3 en hoger | Nee |
| Meter B L3 schijnbaar vermogen | `sensor.saj_meter_b_l3_apparent_power` | Sensor | VA | HS3, H2 | Meter B; Fase 3 en hoger | Nee |
| Meter B L3 arbeidsfactor | `sensor.saj_meter_b_l3_power_factor` | Sensor | - | HS3, H2 | Meter B; Fase 3 en hoger | Nee |
| Meter B L3 frequentie | `sensor.saj_meter_b_l3_frequency` | Sensor | Hz | HS3, H2 | Meter B; Fase 3 en hoger | Nee |
| Meter B L1 blindvermogen | `sensor.saj_meter_b_l1_reactive_power` | Sensor | var | HS3 | Meter B | Nee |
| Meter B L2 blindvermogen | `sensor.saj_meter_b_l2_reactive_power` | Sensor | var | HS3 | Meter B; Fase 2 en hoger | Nee |
| Meter B L3 blindvermogen | `sensor.saj_meter_b_l3_reactive_power` | Sensor | var | HS3 | Meter B; Fase 3 en hoger | Nee |
| Meter B vermogen | `sensor.saj_meter_b_power` | Sensor | W | HS3, H2 | Meter B | Ja |
