[en](../../../en-gb/user/entities/meter-b.md) | [de](../../../de/user/entities/meter-b.md) | [nl](../../../nl/user/entities/meter-b.md) | [fr](../../../fr/user/entities/meter-b.md) | [zh](../../../zh-hans/user/entities/meter-b.md) | [es](../../../es/user/entities/meter-b.md) | [it](../../../it/user/entities/meter-b.md) | [pl](../../../pl/user/entities/meter-b.md) | sv

# Mätare B

Mätare B, den andra mätaren som mäter en solcellsväxelriktare.

Integrationens funktionslista förklarar entiteterna för Mätare B i [Valfri utrustning](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

22 entiteter. Genereras av `make docs`. Redigera inte för hand.

Ett prefix som anges i Konfigurera hamnar efter `saj_` i ID:t för varje entitet i Mätare B, till exempel `sensor.saj_house_meter_b_l1_voltage` med prefixet `house`.

| Namn | Entitets-ID | Typ | Enhet | Modeller | Utrustning och antal | Aktiverad som standard |
| --- | --- | --- | --- | --- | --- | --- |
| Mätare B L1-spänning | `sensor.saj_meter_b_l1_voltage` | Sensor | V | HS3, H2 | Mätare B | Nej |
| Mätare B L1-ström | `sensor.saj_meter_b_l1_current` | Sensor | A | HS3, H2 | Mätare B | Nej |
| Mätare B L1-effekt | `sensor.saj_meter_b_l1_power` | Sensor | W | HS3, H2 | Mätare B | Nej |
| Mätare B L1 skenbar effekt | `sensor.saj_meter_b_l1_apparent_power` | Sensor | VA | HS3, H2 | Mätare B | Nej |
| Mätare B L1-effektfaktor | `sensor.saj_meter_b_l1_power_factor` | Sensor | - | HS3, H2 | Mätare B | Nej |
| Mätare B L1-frekvens | `sensor.saj_meter_b_l1_frequency` | Sensor | Hz | HS3, H2 | Mätare B | Nej |
| Mätare B L2-spänning | `sensor.saj_meter_b_l2_voltage` | Sensor | V | HS3, H2 | Mätare B; Fas 2 och högre | Nej |
| Mätare B L2-ström | `sensor.saj_meter_b_l2_current` | Sensor | A | HS3, H2 | Mätare B; Fas 2 och högre | Nej |
| Mätare B L2-effekt | `sensor.saj_meter_b_l2_power` | Sensor | W | HS3, H2 | Mätare B; Fas 2 och högre | Nej |
| Mätare B L2 skenbar effekt | `sensor.saj_meter_b_l2_apparent_power` | Sensor | VA | HS3, H2 | Mätare B; Fas 2 och högre | Nej |
| Mätare B L2-effektfaktor | `sensor.saj_meter_b_l2_power_factor` | Sensor | - | HS3, H2 | Mätare B; Fas 2 och högre | Nej |
| Mätare B L2-frekvens | `sensor.saj_meter_b_l2_frequency` | Sensor | Hz | HS3, H2 | Mätare B; Fas 2 och högre | Nej |
| Mätare B L3-spänning | `sensor.saj_meter_b_l3_voltage` | Sensor | V | HS3, H2 | Mätare B; Fas 3 och högre | Nej |
| Mätare B L3-ström | `sensor.saj_meter_b_l3_current` | Sensor | A | HS3, H2 | Mätare B; Fas 3 och högre | Nej |
| Mätare B L3-effekt | `sensor.saj_meter_b_l3_power` | Sensor | W | HS3, H2 | Mätare B; Fas 3 och högre | Nej |
| Mätare B L3 skenbar effekt | `sensor.saj_meter_b_l3_apparent_power` | Sensor | VA | HS3, H2 | Mätare B; Fas 3 och högre | Nej |
| Mätare B L3-effektfaktor | `sensor.saj_meter_b_l3_power_factor` | Sensor | - | HS3, H2 | Mätare B; Fas 3 och högre | Nej |
| Mätare B L3-frekvens | `sensor.saj_meter_b_l3_frequency` | Sensor | Hz | HS3, H2 | Mätare B; Fas 3 och högre | Nej |
| Mätare B L1 reaktiv effekt | `sensor.saj_meter_b_l1_reactive_power` | Sensor | var | HS3 | Mätare B | Nej |
| Mätare B L2 reaktiv effekt | `sensor.saj_meter_b_l2_reactive_power` | Sensor | var | HS3 | Mätare B; Fas 2 och högre | Nej |
| Mätare B L3 reaktiv effekt | `sensor.saj_meter_b_l3_reactive_power` | Sensor | var | HS3 | Mätare B; Fas 3 och högre | Nej |
| Mätare B effekt | `sensor.saj_meter_b_power` | Sensor | W | HS3, H2 | Mätare B | Ja |
