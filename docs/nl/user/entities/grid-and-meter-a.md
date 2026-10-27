[en](../../../en-gb/user/entities/grid-and-meter-a.md) | [de](../../../de/user/entities/grid-and-meter-a.md) | nl | [fr](../../../fr/user/entities/grid-and-meter-a.md) | [zh](../../../zh-hans/user/entities/grid-and-meter-a.md) | [es](../../../es/user/entities/grid-and-meter-a.md) | [it](../../../it/user/entities/grid-and-meter-a.md) | [pl](../../../pl/user/entities/grid-and-meter-a.md) | [sv](../../../sv/user/entities/grid-and-meter-a.md)

# Net en Meter A

De netaansluiting en Meter A, de netmeter.

De functielijst van de integratie legt de Net en Meter A-entiteiten uit in [Apparaten en entiteiten](../../../../custom_components/saj_local/docs/features.md#devices-and-entities) en [Optionele apparatuur](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

88 entiteiten. Gegenereerd door `make docs`. Niet met de hand bewerken.

Een voorvoegsel dat in Configureren is ingesteld komt na `saj_` in de ID van elke Net en Meter A-entiteit, bijvoorbeeld `sensor.saj_house_grid_connection_countdown` met het voorvoegsel `house`.

| Naam | Entiteits-ID | Type | Eenheid | Modellen | Apparatuur en aantallen | Standaard ingeschakeld |
| --- | --- | --- | --- | --- | --- | --- |
| Aftelling netaansluiting | `sensor.saj_grid_connection_countdown` | Sensor | s | HS3, H2 | - | Nee |
| Netspanning L1 | `sensor.saj_grid_l1_voltage` | Sensor | V | HS3, H2 | - | Ja |
| Netstroom L1 | `sensor.saj_grid_l1_current` | Sensor | A | HS3, H2 | - | Nee |
| Netfrequentie L1 | `sensor.saj_grid_l1_frequency` | Sensor | Hz | HS3, H2 | - | Ja |
| Netgelijkstroom L1 | `sensor.saj_grid_l1_dc_current` | Sensor | mA | HS3, H2 | - | Nee |
| Netvermogen L1 | `sensor.saj_grid_l1_power` | Sensor | W | HS3, H2 | - | Nee |
| Schijnbaar netvermogen L1 | `sensor.saj_grid_l1_apparent_power` | Sensor | VA | HS3, H2 | - | Nee |
| Netarbeidsfactor L1 | `sensor.saj_grid_l1_power_factor` | Sensor | - | HS3, H2 | - | Nee |
| Netspanning L2 | `sensor.saj_grid_l2_voltage` | Sensor | V | HS3, H2 | Fase 2 en hoger | Ja |
| Netstroom L2 | `sensor.saj_grid_l2_current` | Sensor | A | HS3, H2 | Fase 2 en hoger | Nee |
| Netfrequentie L2 | `sensor.saj_grid_l2_frequency` | Sensor | Hz | HS3, H2 | Fase 2 en hoger | Nee |
| Netgelijkstroom L2 | `sensor.saj_grid_l2_dc_current` | Sensor | mA | HS3, H2 | Fase 2 en hoger | Nee |
| Netvermogen L2 | `sensor.saj_grid_l2_power` | Sensor | W | HS3, H2 | Fase 2 en hoger | Nee |
| Schijnbaar netvermogen L2 | `sensor.saj_grid_l2_apparent_power` | Sensor | VA | HS3, H2 | Fase 2 en hoger | Nee |
| Netarbeidsfactor L2 | `sensor.saj_grid_l2_power_factor` | Sensor | - | HS3, H2 | Fase 2 en hoger | Nee |
| Netspanning L3 | `sensor.saj_grid_l3_voltage` | Sensor | V | HS3, H2 | Fase 3 en hoger | Ja |
| Netstroom L3 | `sensor.saj_grid_l3_current` | Sensor | A | HS3, H2 | Fase 3 en hoger | Nee |
| Netfrequentie L3 | `sensor.saj_grid_l3_frequency` | Sensor | Hz | HS3, H2 | Fase 3 en hoger | Nee |
| Netgelijkstroom L3 | `sensor.saj_grid_l3_dc_current` | Sensor | mA | HS3, H2 | Fase 3 en hoger | Nee |
| Netvermogen L3 | `sensor.saj_grid_l3_power` | Sensor | W | HS3, H2 | Fase 3 en hoger | Nee |
| Schijnbaar netvermogen L3 | `sensor.saj_grid_l3_apparent_power` | Sensor | VA | HS3, H2 | Fase 3 en hoger | Nee |
| Netarbeidsfactor L3 | `sensor.saj_grid_l3_power_factor` | Sensor | - | HS3, H2 | Fase 3 en hoger | Nee |
| Netuitgangsspanning L1 | `sensor.saj_grid_output_l1_voltage` | Sensor | V | HS3, H2 | - | Nee |
| Netuitgangsstroom L1 | `sensor.saj_grid_output_l1_current` | Sensor | A | HS3, H2 | - | Nee |
| Netuitgangsfrequentie L1 | `sensor.saj_grid_output_l1_frequency` | Sensor | Hz | HS3, H2 | - | Nee |
| Netuitgangsvermogen L1 | `sensor.saj_grid_output_l1_power` | Sensor | W | HS3, H2 | - | Nee |
| Netuitgangsspanning L2 | `sensor.saj_grid_output_l2_voltage` | Sensor | V | HS3, H2 | Fase 2 en hoger | Nee |
| Netuitgangsvermogen L2 | `sensor.saj_grid_output_l2_power` | Sensor | W | HS3, H2 | Fase 2 en hoger | Nee |
| Netuitgangsspanning L3 | `sensor.saj_grid_output_l3_voltage` | Sensor | V | HS3, H2 | Fase 3 en hoger | Nee |
| Netuitgangsvermogen L3 | `sensor.saj_grid_output_l3_power` | Sensor | W | HS3, H2 | Fase 3 en hoger | Nee |
| Netvermogen | `sensor.saj_grid_power` | Sensor | W | HS3, H2 | - | Ja |
| Netbelastingvermogen | `sensor.saj_grid_load_power` | Sensor | W | HS3, H2 | - | Nee |
| Netteruglevering L1 vandaag | `sensor.saj_grid_l1_export_energy_today` | Sensor | kWh | HS3, H2 | - | Nee |
| Netteruglevering L1 deze maand | `sensor.saj_grid_l1_export_energy_month` | Sensor | kWh | HS3, H2 | - | Nee |
| Netteruglevering L1 dit jaar | `sensor.saj_grid_l1_export_energy_year` | Sensor | kWh | HS3, H2 | - | Nee |
| Netteruglevering L1 totaal | `sensor.saj_grid_l1_export_energy_total` | Sensor | kWh | HS3, H2 | - | Nee |
| Netafname L1 vandaag | `sensor.saj_grid_l1_import_energy_today` | Sensor | kWh | HS3, H2 | - | Nee |
| Netafname L1 deze maand | `sensor.saj_grid_l1_import_energy_month` | Sensor | kWh | HS3, H2 | - | Nee |
| Netafname L1 dit jaar | `sensor.saj_grid_l1_import_energy_year` | Sensor | kWh | HS3, H2 | - | Nee |
| Netafname L1 totaal | `sensor.saj_grid_l1_import_energy_total` | Sensor | kWh | HS3, H2 | - | Nee |
| Netteruglevering L2 vandaag | `sensor.saj_grid_l2_export_energy_today` | Sensor | kWh | HS3, H2 | Fase 2 en hoger | Nee |
| Netteruglevering L2 deze maand | `sensor.saj_grid_l2_export_energy_month` | Sensor | kWh | HS3, H2 | Fase 2 en hoger | Nee |
| Netteruglevering L2 dit jaar | `sensor.saj_grid_l2_export_energy_year` | Sensor | kWh | HS3, H2 | Fase 2 en hoger | Nee |
| Netteruglevering L2 totaal | `sensor.saj_grid_l2_export_energy_total` | Sensor | kWh | HS3, H2 | Fase 2 en hoger | Nee |
| Netteruglevering L3 vandaag | `sensor.saj_grid_l3_export_energy_today` | Sensor | kWh | HS3, H2 | Fase 3 en hoger | Nee |
| Netteruglevering L3 deze maand | `sensor.saj_grid_l3_export_energy_month` | Sensor | kWh | HS3, H2 | Fase 3 en hoger | Nee |
| Netteruglevering L3 dit jaar | `sensor.saj_grid_l3_export_energy_year` | Sensor | kWh | HS3, H2 | Fase 3 en hoger | Nee |
| Netteruglevering L3 totaal | `sensor.saj_grid_l3_export_energy_total` | Sensor | kWh | HS3, H2 | Fase 3 en hoger | Nee |
| Netafname L2 vandaag | `sensor.saj_grid_l2_import_energy_today` | Sensor | kWh | HS3, H2 | Fase 2 en hoger | Nee |
| Netafname L2 deze maand | `sensor.saj_grid_l2_import_energy_month` | Sensor | kWh | HS3, H2 | Fase 2 en hoger | Nee |
| Netafname L2 dit jaar | `sensor.saj_grid_l2_import_energy_year` | Sensor | kWh | HS3, H2 | Fase 2 en hoger | Nee |
| Netafname L2 totaal | `sensor.saj_grid_l2_import_energy_total` | Sensor | kWh | HS3, H2 | Fase 2 en hoger | Nee |
| Netafname L3 vandaag | `sensor.saj_grid_l3_import_energy_today` | Sensor | kWh | HS3, H2 | Fase 3 en hoger | Nee |
| Netafname L3 deze maand | `sensor.saj_grid_l3_import_energy_month` | Sensor | kWh | HS3, H2 | Fase 3 en hoger | Nee |
| Netafname L3 dit jaar | `sensor.saj_grid_l3_import_energy_year` | Sensor | kWh | HS3, H2 | Fase 3 en hoger | Nee |
| Netafname L3 totaal | `sensor.saj_grid_l3_import_energy_total` | Sensor | kWh | HS3, H2 | Fase 3 en hoger | Nee |
| Netafname vandaag | `sensor.saj_grid_import_energy_today` | Sensor | kWh | HS3, H2 | - | Ja |
| Netafname deze maand | `sensor.saj_grid_import_energy_month` | Sensor | kWh | HS3, H2 | - | Nee |
| Netafname dit jaar | `sensor.saj_grid_import_energy_year` | Sensor | kWh | HS3, H2 | - | Nee |
| Netafname totaal | `sensor.saj_grid_import_energy_total` | Sensor | kWh | HS3, H2 | - | Ja |
| Netteruglevering vandaag | `sensor.saj_grid_export_energy_today` | Sensor | kWh | HS3, H2 | - | Ja |
| Netteruglevering deze maand | `sensor.saj_grid_export_energy_month` | Sensor | kWh | HS3, H2 | - | Nee |
| Netteruglevering dit jaar | `sensor.saj_grid_export_energy_year` | Sensor | kWh | HS3, H2 | - | Nee |
| Netteruglevering totaal | `sensor.saj_grid_export_energy_total` | Sensor | kWh | HS3, H2 | - | Ja |
| Meter A L1 spanning | `sensor.saj_meter_a_l1_voltage` | Sensor | V | HS3, H2 | Meter A | Nee |
| Meter A L1 stroom | `sensor.saj_meter_a_l1_current` | Sensor | A | HS3, H2 | Meter A | Nee |
| Meter A L1 vermogen | `sensor.saj_meter_a_l1_power` | Sensor | W | HS3, H2 | Meter A | Nee |
| Meter A L1 schijnbaar vermogen | `sensor.saj_meter_a_l1_apparent_power` | Sensor | VA | HS3, H2 | Meter A | Nee |
| Meter A L1 arbeidsfactor | `sensor.saj_meter_a_l1_power_factor` | Sensor | - | HS3, H2 | Meter A | Nee |
| Meter A L1 frequentie | `sensor.saj_meter_a_l1_frequency` | Sensor | Hz | HS3, H2 | Meter A | Nee |
| Meter A L2 spanning | `sensor.saj_meter_a_l2_voltage` | Sensor | V | HS3, H2 | Meter A; Fase 2 en hoger | Nee |
| Meter A L2 stroom | `sensor.saj_meter_a_l2_current` | Sensor | A | HS3, H2 | Meter A; Fase 2 en hoger | Nee |
| Meter A L2 vermogen | `sensor.saj_meter_a_l2_power` | Sensor | W | HS3, H2 | Meter A; Fase 2 en hoger | Nee |
| Meter A L2 schijnbaar vermogen | `sensor.saj_meter_a_l2_apparent_power` | Sensor | VA | HS3, H2 | Meter A; Fase 2 en hoger | Nee |
| Meter A L2 arbeidsfactor | `sensor.saj_meter_a_l2_power_factor` | Sensor | - | HS3, H2 | Meter A; Fase 2 en hoger | Nee |
| Meter A L2 frequentie | `sensor.saj_meter_a_l2_frequency` | Sensor | Hz | HS3, H2 | Meter A; Fase 2 en hoger | Nee |
| Meter A L3 spanning | `sensor.saj_meter_a_l3_voltage` | Sensor | V | HS3, H2 | Meter A; Fase 3 en hoger | Nee |
| Meter A L3 stroom | `sensor.saj_meter_a_l3_current` | Sensor | A | HS3, H2 | Meter A; Fase 3 en hoger | Nee |
| Meter A L3 vermogen | `sensor.saj_meter_a_l3_power` | Sensor | W | HS3, H2 | Meter A; Fase 3 en hoger | Nee |
| Meter A L3 schijnbaar vermogen | `sensor.saj_meter_a_l3_apparent_power` | Sensor | VA | HS3, H2 | Meter A; Fase 3 en hoger | Nee |
| Meter A L3 arbeidsfactor | `sensor.saj_meter_a_l3_power_factor` | Sensor | - | HS3, H2 | Meter A; Fase 3 en hoger | Nee |
| Meter A L3 frequentie | `sensor.saj_meter_a_l3_frequency` | Sensor | Hz | HS3, H2 | Meter A; Fase 3 en hoger | Nee |
| Meter A L1 blindvermogen | `sensor.saj_meter_a_l1_reactive_power` | Sensor | var | HS3 | Meter A | Nee |
| Meter A L2 blindvermogen | `sensor.saj_meter_a_l2_reactive_power` | Sensor | var | HS3 | Meter A; Fase 2 en hoger | Nee |
| Meter A L3 blindvermogen | `sensor.saj_meter_a_l3_reactive_power` | Sensor | var | HS3 | Meter A; Fase 3 en hoger | Nee |
| Meter A vermogen | `sensor.saj_meter_a_power` | Sensor | W | HS3, H2 | Meter A | Ja |
| Nettype | `sensor.saj_grid_type` | Sensor | - | H2 | - | Nee |
| Schijnbaar netvermogen | `sensor.saj_grid_apparent_power` | Sensor | VA | H2 | - | Nee |
