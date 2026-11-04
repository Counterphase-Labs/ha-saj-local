[en](../../../en-gb/user/entities/grid-and-meter-a.md) | [de](../../../de/user/entities/grid-and-meter-a.md) | [nl](../../../nl/user/entities/grid-and-meter-a.md) | [fr](../../../fr/user/entities/grid-and-meter-a.md) | [zh](../../../zh-hans/user/entities/grid-and-meter-a.md) | [es](../../../es/user/entities/grid-and-meter-a.md) | [it](../../../it/user/entities/grid-and-meter-a.md) | [pl](../../../pl/user/entities/grid-and-meter-a.md) | sv

# Nät och Mätare A

Nätanslutningen och Mätare A, nätmätaren.

Integrationens funktionslista förklarar entiteterna för Nät och Mätare A i [Enheter och entiteter](../../../../custom_components/saj_local/docs/features.md#devices-and-entities) och [Valfri utrustning](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

101 entiteter. Genereras av `make docs`. Redigera inte för hand.

Ett prefix som anges i Konfigurera hamnar efter `saj_` i ID:t för varje entitet i Nät och Mätare A, till exempel `sensor.saj_house_grid_connection_countdown` med prefixet `house`.

| Namn | Entitets-ID | Typ | Enhet | Modeller | Utrustning och antal | Aktiverad som standard |
| --- | --- | --- | --- | --- | --- | --- |
| Nedräkning till nätanslutning | `sensor.saj_grid_connection_countdown` | Sensor | s | HS3, H2 | - | Nej |
| Nät L1-spänning | `sensor.saj_grid_l1_voltage` | Sensor | V | HS3, H2 | - | Ja |
| Nät L1-frekvens | `sensor.saj_grid_l1_frequency` | Sensor | Hz | HS3, H2 | - | Ja |
| Nät L1-likström | `sensor.saj_grid_l1_dc_current` | Sensor | mA | HS3, H2 | - | Nej |
| Nät L2-spänning | `sensor.saj_grid_l2_voltage` | Sensor | V | HS3, H2 | Fas 2 och högre | Ja |
| Nät L2-frekvens | `sensor.saj_grid_l2_frequency` | Sensor | Hz | HS3, H2 | Fas 2 och högre | Nej |
| Nät L2-likström | `sensor.saj_grid_l2_dc_current` | Sensor | mA | HS3, H2 | Fas 2 och högre | Nej |
| Nät L3-spänning | `sensor.saj_grid_l3_voltage` | Sensor | V | HS3, H2 | Fas 3 och högre | Ja |
| Nät L3-frekvens | `sensor.saj_grid_l3_frequency` | Sensor | Hz | HS3, H2 | Fas 3 och högre | Nej |
| Nät L3-likström | `sensor.saj_grid_l3_dc_current` | Sensor | mA | HS3, H2 | Fas 3 och högre | Nej |
| Nätutgång L1-spänning | `sensor.saj_grid_output_l1_voltage` | Sensor | V | HS3, H2 | - | Nej |
| Nätutgång L1-ström | `sensor.saj_grid_output_l1_current` | Sensor | A | HS3, H2 | - | Nej |
| Nätutgång L1-frekvens | `sensor.saj_grid_output_l1_frequency` | Sensor | Hz | HS3, H2 | - | Nej |
| Nätutgång L1-effekt | `sensor.saj_grid_output_l1_power` | Sensor | W | HS3, H2 | - | Nej |
| Nätutgång L2-spänning | `sensor.saj_grid_output_l2_voltage` | Sensor | V | HS3, H2 | Fas 2 och högre | Nej |
| Nätutgång L2-effekt | `sensor.saj_grid_output_l2_power` | Sensor | W | HS3, H2 | Fas 2 och högre | Nej |
| Nätutgång L3-spänning | `sensor.saj_grid_output_l3_voltage` | Sensor | V | HS3, H2 | Fas 3 och högre | Nej |
| Nätutgång L3-effekt | `sensor.saj_grid_output_l3_power` | Sensor | W | HS3, H2 | Fas 3 och högre | Nej |
| Nätlasteffekt | `sensor.saj_grid_load_power` | Sensor | W | HS3, H2 | - | Nej |
| Nät L1-exportenergi idag | `sensor.saj_grid_l1_export_energy_today` | Sensor | kWh | HS3, H2 | - | Nej |
| Nät L1-exportenergi denna månad | `sensor.saj_grid_l1_export_energy_month` | Sensor | kWh | HS3, H2 | - | Nej |
| Nät L1-exportenergi i år | `sensor.saj_grid_l1_export_energy_year` | Sensor | kWh | HS3, H2 | - | Nej |
| Nät L1-exportenergi totalt | `sensor.saj_grid_l1_export_energy_total` | Sensor | kWh | HS3, H2 | - | Nej |
| Nät L1-importenergi idag | `sensor.saj_grid_l1_import_energy_today` | Sensor | kWh | HS3, H2 | - | Nej |
| Nät L1-importenergi denna månad | `sensor.saj_grid_l1_import_energy_month` | Sensor | kWh | HS3, H2 | - | Nej |
| Nät L1-importenergi i år | `sensor.saj_grid_l1_import_energy_year` | Sensor | kWh | HS3, H2 | - | Nej |
| Nät L1-importenergi totalt | `sensor.saj_grid_l1_import_energy_total` | Sensor | kWh | HS3, H2 | - | Nej |
| Nät L2-exportenergi idag | `sensor.saj_grid_l2_export_energy_today` | Sensor | kWh | HS3, H2 | Fas 2 och högre | Nej |
| Nät L2-exportenergi denna månad | `sensor.saj_grid_l2_export_energy_month` | Sensor | kWh | HS3, H2 | Fas 2 och högre | Nej |
| Nät L2-exportenergi i år | `sensor.saj_grid_l2_export_energy_year` | Sensor | kWh | HS3, H2 | Fas 2 och högre | Nej |
| Nät L2-exportenergi totalt | `sensor.saj_grid_l2_export_energy_total` | Sensor | kWh | HS3, H2 | Fas 2 och högre | Nej |
| Nät L3-exportenergi idag | `sensor.saj_grid_l3_export_energy_today` | Sensor | kWh | HS3, H2 | Fas 3 och högre | Nej |
| Nät L3-exportenergi denna månad | `sensor.saj_grid_l3_export_energy_month` | Sensor | kWh | HS3, H2 | Fas 3 och högre | Nej |
| Nät L3-exportenergi i år | `sensor.saj_grid_l3_export_energy_year` | Sensor | kWh | HS3, H2 | Fas 3 och högre | Nej |
| Nät L3-exportenergi totalt | `sensor.saj_grid_l3_export_energy_total` | Sensor | kWh | HS3, H2 | Fas 3 och högre | Nej |
| Nät L2-importenergi idag | `sensor.saj_grid_l2_import_energy_today` | Sensor | kWh | HS3, H2 | Fas 2 och högre | Nej |
| Nät L2-importenergi denna månad | `sensor.saj_grid_l2_import_energy_month` | Sensor | kWh | HS3, H2 | Fas 2 och högre | Nej |
| Nät L2-importenergi i år | `sensor.saj_grid_l2_import_energy_year` | Sensor | kWh | HS3, H2 | Fas 2 och högre | Nej |
| Nät L2-importenergi totalt | `sensor.saj_grid_l2_import_energy_total` | Sensor | kWh | HS3, H2 | Fas 2 och högre | Nej |
| Nät L3-importenergi idag | `sensor.saj_grid_l3_import_energy_today` | Sensor | kWh | HS3, H2 | Fas 3 och högre | Nej |
| Nät L3-importenergi denna månad | `sensor.saj_grid_l3_import_energy_month` | Sensor | kWh | HS3, H2 | Fas 3 och högre | Nej |
| Nät L3-importenergi i år | `sensor.saj_grid_l3_import_energy_year` | Sensor | kWh | HS3, H2 | Fas 3 och högre | Nej |
| Nät L3-importenergi totalt | `sensor.saj_grid_l3_import_energy_total` | Sensor | kWh | HS3, H2 | Fas 3 och högre | Nej |
| Nätimportenergi idag | `sensor.saj_grid_import_energy_today` | Sensor | kWh | HS3, H2 | - | Ja |
| Nätimportenergi denna månad | `sensor.saj_grid_import_energy_month` | Sensor | kWh | HS3, H2 | - | Nej |
| Nätimportenergi i år | `sensor.saj_grid_import_energy_year` | Sensor | kWh | HS3, H2 | - | Nej |
| Nätimportenergi totalt | `sensor.saj_grid_import_energy_total` | Sensor | kWh | HS3, H2 | - | Ja |
| Nätexportenergi idag | `sensor.saj_grid_export_energy_today` | Sensor | kWh | HS3, H2 | - | Ja |
| Nätexportenergi denna månad | `sensor.saj_grid_export_energy_month` | Sensor | kWh | HS3, H2 | - | Nej |
| Nätexportenergi i år | `sensor.saj_grid_export_energy_year` | Sensor | kWh | HS3, H2 | - | Nej |
| Nätexportenergi totalt | `sensor.saj_grid_export_energy_total` | Sensor | kWh | HS3, H2 | - | Ja |
| Mätare A L1-spänning | `sensor.saj_meter_a_l1_voltage` | Sensor | V | HS3, H2 | Mätare A | Nej |
| Mätare A L1-ström | `sensor.saj_meter_a_l1_current` | Sensor | A | HS3, H2 | Mätare A | Nej |
| Mätare A L1-effekt | `sensor.saj_meter_a_l1_power` | Sensor | W | HS3, H2 | Mätare A | Nej |
| Mätare A L1 skenbar effekt | `sensor.saj_meter_a_l1_apparent_power` | Sensor | VA | HS3, H2 | Mätare A | Nej |
| Mätare A L1-effektfaktor | `sensor.saj_meter_a_l1_power_factor` | Sensor | - | HS3, H2 | Mätare A | Nej |
| Mätare A L1-frekvens | `sensor.saj_meter_a_l1_frequency` | Sensor | Hz | HS3, H2 | Mätare A | Nej |
| Mätare A L2-spänning | `sensor.saj_meter_a_l2_voltage` | Sensor | V | HS3, H2 | Mätare A; Fas 2 och högre | Nej |
| Mätare A L2-ström | `sensor.saj_meter_a_l2_current` | Sensor | A | HS3, H2 | Mätare A; Fas 2 och högre | Nej |
| Mätare A L2-effekt | `sensor.saj_meter_a_l2_power` | Sensor | W | HS3, H2 | Mätare A; Fas 2 och högre | Nej |
| Mätare A L2 skenbar effekt | `sensor.saj_meter_a_l2_apparent_power` | Sensor | VA | HS3, H2 | Mätare A; Fas 2 och högre | Nej |
| Mätare A L2-effektfaktor | `sensor.saj_meter_a_l2_power_factor` | Sensor | - | HS3, H2 | Mätare A; Fas 2 och högre | Nej |
| Mätare A L2-frekvens | `sensor.saj_meter_a_l2_frequency` | Sensor | Hz | HS3, H2 | Mätare A; Fas 2 och högre | Nej |
| Mätare A L3-spänning | `sensor.saj_meter_a_l3_voltage` | Sensor | V | HS3, H2 | Mätare A; Fas 3 och högre | Nej |
| Mätare A L3-ström | `sensor.saj_meter_a_l3_current` | Sensor | A | HS3, H2 | Mätare A; Fas 3 och högre | Nej |
| Mätare A L3-effekt | `sensor.saj_meter_a_l3_power` | Sensor | W | HS3, H2 | Mätare A; Fas 3 och högre | Nej |
| Mätare A L3 skenbar effekt | `sensor.saj_meter_a_l3_apparent_power` | Sensor | VA | HS3, H2 | Mätare A; Fas 3 och högre | Nej |
| Mätare A L3-effektfaktor | `sensor.saj_meter_a_l3_power_factor` | Sensor | - | HS3, H2 | Mätare A; Fas 3 och högre | Nej |
| Mätare A L3-frekvens | `sensor.saj_meter_a_l3_frequency` | Sensor | Hz | HS3, H2 | Mätare A; Fas 3 och högre | Nej |
| Mätare A L1 reaktiv effekt | `sensor.saj_meter_a_l1_reactive_power` | Sensor | var | HS3 | Mätare A | Nej |
| Mätare A L2 reaktiv effekt | `sensor.saj_meter_a_l2_reactive_power` | Sensor | var | HS3 | Mätare A; Fas 2 och högre | Nej |
| Mätare A L3 reaktiv effekt | `sensor.saj_meter_a_l3_reactive_power` | Sensor | var | HS3 | Mätare A; Fas 3 och högre | Nej |
| Nät L1 skenbar effekt | `sensor.saj_grid_l1_apparent_power` | Sensor | VA | HS3 | Mätare A | Nej |
| Nät L1-ström | `sensor.saj_grid_l1_current` | Sensor | A | HS3 | Mätare A | Nej |
| Nät L1-effekt | `sensor.saj_grid_l1_power` | Sensor | W | HS3 | Mätare A | Nej |
| Nät L1-effektfaktor | `sensor.saj_grid_l1_power_factor` | Sensor | - | HS3 | Mätare A | Nej |
| Nät L2 skenbar effekt | `sensor.saj_grid_l2_apparent_power` | Sensor | VA | HS3 | Mätare A; Fas 2 och högre | Nej |
| Nät L2-ström | `sensor.saj_grid_l2_current` | Sensor | A | HS3 | Mätare A; Fas 2 och högre | Nej |
| Nät L2-effekt | `sensor.saj_grid_l2_power` | Sensor | W | HS3 | Mätare A; Fas 2 och högre | Nej |
| Nät L2-effektfaktor | `sensor.saj_grid_l2_power_factor` | Sensor | - | HS3 | Mätare A; Fas 2 och högre | Nej |
| Nät L3 skenbar effekt | `sensor.saj_grid_l3_apparent_power` | Sensor | VA | HS3 | Mätare A; Fas 3 och högre | Nej |
| Nät L3-ström | `sensor.saj_grid_l3_current` | Sensor | A | HS3 | Mätare A; Fas 3 och högre | Nej |
| Nät L3-effekt | `sensor.saj_grid_l3_power` | Sensor | W | HS3 | Mätare A; Fas 3 och högre | Nej |
| Nät L3-effektfaktor | `sensor.saj_grid_l3_power_factor` | Sensor | - | HS3 | Mätare A; Fas 3 och högre | Nej |
| Näteffekt | `sensor.saj_grid_power` | Sensor | W | HS3 | Mätare A | Ja |
| Mätare A effekt | `sensor.saj_meter_a_power` | Sensor | W | HS3, H2 | Mätare A | Ja |
| Nättyp | `sensor.saj_grid_type` | Sensor | - | H2 | - | Nej |
| Nät L1-ström | `sensor.saj_grid_l1_current` | Sensor | A | H2 | - | Nej |
| Nät L1-effekt | `sensor.saj_grid_l1_power` | Sensor | W | H2 | - | Nej |
| Nät L1 skenbar effekt | `sensor.saj_grid_l1_apparent_power` | Sensor | VA | H2 | - | Nej |
| Nät L1-effektfaktor | `sensor.saj_grid_l1_power_factor` | Sensor | - | H2 | - | Nej |
| Nät L2-ström | `sensor.saj_grid_l2_current` | Sensor | A | H2 | Fas 2 och högre | Nej |
| Nät L2-effekt | `sensor.saj_grid_l2_power` | Sensor | W | H2 | Fas 2 och högre | Nej |
| Nät L2 skenbar effekt | `sensor.saj_grid_l2_apparent_power` | Sensor | VA | H2 | Fas 2 och högre | Nej |
| Nät L2-effektfaktor | `sensor.saj_grid_l2_power_factor` | Sensor | - | H2 | Fas 2 och högre | Nej |
| Nät L3-ström | `sensor.saj_grid_l3_current` | Sensor | A | H2 | Fas 3 och högre | Nej |
| Nät L3-effekt | `sensor.saj_grid_l3_power` | Sensor | W | H2 | Fas 3 och högre | Nej |
| Nät L3 skenbar effekt | `sensor.saj_grid_l3_apparent_power` | Sensor | VA | H2 | Fas 3 och högre | Nej |
| Nät L3-effektfaktor | `sensor.saj_grid_l3_power_factor` | Sensor | - | H2 | Fas 3 och högre | Nej |
| Näteffekt | `sensor.saj_grid_power` | Sensor | W | H2 | - | Ja |
| Nät skenbar effekt | `sensor.saj_grid_apparent_power` | Sensor | VA | H2 | - | Nej |
