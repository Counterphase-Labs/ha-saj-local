[en](../../../en-gb/user/entities/parallel-system.md) | [de](../../../de/user/entities/parallel-system.md) | [nl](../../../nl/user/entities/parallel-system.md) | [fr](../../../fr/user/entities/parallel-system.md) | [zh](../../../zh-hans/user/entities/parallel-system.md) | [es](../../../es/user/entities/parallel-system.md) | [it](../../../it/user/entities/parallel-system.md) | [pl](../../../pl/user/entities/parallel-system.md) | sv

# Parallellsystem

Avläsningarna från ett parallellt maskinsystem.

Integrationens funktionslista förklarar entiteterna för Parallellsystem i [Valfri utrustning](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

63 entiteter. Genereras av `make docs`. Redigera inte för hand.

Ett prefix som anges i Konfigurera hamnar efter `saj_` i ID:t för varje entitet i Parallellsystem, till exempel `sensor.saj_house_parallel_id` med prefixet `house`.

| Namn | Entitets-ID | Typ | Enhet | Modeller | Utrustning och antal | Aktiverad som standard |
| --- | --- | --- | --- | --- | --- | --- |
| Parallellmaskin-ID | `sensor.saj_parallel_id` | Sensor | - | HS3, H2 | Parallellsystem | Nej |
| Antal parallellmaskiner | `sensor.saj_parallel_count` | Sensor | - | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem batteri laddningsnivå | `sensor.saj_parallel_battery_soc` | Sensor | % | HS3, H2 | Parallellsystem | Ja |
| Parallellsystem batterikapacitet | `sensor.saj_parallel_battery_capacity` | Sensor | Ah | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem mätare B effekt | `sensor.saj_parallel_meter_b_power` | Sensor | W | HS3 | Parallellsystem | Nej |
| Parallellsystem solenergi idag | `sensor.saj_parallel_pv_energy_today` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem solenergi denna månad | `sensor.saj_parallel_pv_energy_month` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem solenergi i år | `sensor.saj_parallel_pv_energy_year` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem solenergi totalt | `sensor.saj_parallel_pv_energy_total` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem batteri laddningsenergi idag | `sensor.saj_parallel_battery_charge_energy_today` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem batteri laddningsenergi denna månad | `sensor.saj_parallel_battery_charge_energy_month` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem batteri laddningsenergi i år | `sensor.saj_parallel_battery_charge_energy_year` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem batteri laddningsenergi totalt | `sensor.saj_parallel_battery_charge_energy_total` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem batteri urladdningsenergi idag | `sensor.saj_parallel_battery_discharge_energy_today` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem batteri urladdningsenergi denna månad | `sensor.saj_parallel_battery_discharge_energy_month` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem batteri urladdningsenergi i år | `sensor.saj_parallel_battery_discharge_energy_year` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem batteri urladdningsenergi totalt | `sensor.saj_parallel_battery_discharge_energy_total` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L1-exportenergi idag | `sensor.saj_parallel_grid_l1_export_energy_today` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L1-exportenergi denna månad | `sensor.saj_parallel_grid_l1_export_energy_month` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L1-exportenergi i år | `sensor.saj_parallel_grid_l1_export_energy_year` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L1-exportenergi totalt | `sensor.saj_parallel_grid_l1_export_energy_total` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L2-exportenergi idag | `sensor.saj_parallel_grid_l2_export_energy_today` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L2-exportenergi denna månad | `sensor.saj_parallel_grid_l2_export_energy_month` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L2-exportenergi i år | `sensor.saj_parallel_grid_l2_export_energy_year` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L2-exportenergi totalt | `sensor.saj_parallel_grid_l2_export_energy_total` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L3-exportenergi idag | `sensor.saj_parallel_grid_l3_export_energy_today` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L3-exportenergi denna månad | `sensor.saj_parallel_grid_l3_export_energy_month` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L3-exportenergi i år | `sensor.saj_parallel_grid_l3_export_energy_year` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L3-exportenergi totalt | `sensor.saj_parallel_grid_l3_export_energy_total` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L1-importenergi idag | `sensor.saj_parallel_grid_l1_import_energy_today` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L1-importenergi denna månad | `sensor.saj_parallel_grid_l1_import_energy_month` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L1-importenergi i år | `sensor.saj_parallel_grid_l1_import_energy_year` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L1-importenergi totalt | `sensor.saj_parallel_grid_l1_import_energy_total` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L2-importenergi idag | `sensor.saj_parallel_grid_l2_import_energy_today` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L2-importenergi denna månad | `sensor.saj_parallel_grid_l2_import_energy_month` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L2-importenergi i år | `sensor.saj_parallel_grid_l2_import_energy_year` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L2-importenergi totalt | `sensor.saj_parallel_grid_l2_import_energy_total` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L3-importenergi idag | `sensor.saj_parallel_grid_l3_import_energy_today` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L3-importenergi denna månad | `sensor.saj_parallel_grid_l3_import_energy_month` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L3-importenergi i år | `sensor.saj_parallel_grid_l3_import_energy_year` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät L3-importenergi totalt | `sensor.saj_parallel_grid_l3_import_energy_total` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem hushållslast energi idag | `sensor.saj_parallel_load_energy_today` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem hushållslast energi denna månad | `sensor.saj_parallel_load_energy_month` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem hushållslast energi i år | `sensor.saj_parallel_load_energy_year` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem hushållslast energi totalt | `sensor.saj_parallel_load_energy_total` | Sensor | kWh | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät importenergi idag | `sensor.saj_parallel_grid_import_energy_today` | Sensor | kWh | HS3 | Parallellsystem | Nej |
| Parallellsystem nät importenergi denna månad | `sensor.saj_parallel_grid_import_energy_month` | Sensor | kWh | HS3 | Parallellsystem | Nej |
| Parallellsystem nät importenergi i år | `sensor.saj_parallel_grid_import_energy_year` | Sensor | kWh | HS3 | Parallellsystem | Nej |
| Parallellsystem nät importenergi totalt | `sensor.saj_parallel_grid_import_energy_total` | Sensor | kWh | HS3 | Parallellsystem | Nej |
| Parallellsystem nät exportenergi idag | `sensor.saj_parallel_grid_export_energy_today` | Sensor | kWh | HS3 | Parallellsystem | Nej |
| Parallellsystem nät exportenergi denna månad | `sensor.saj_parallel_grid_export_energy_month` | Sensor | kWh | HS3 | Parallellsystem | Nej |
| Parallellsystem nät exportenergi i år | `sensor.saj_parallel_grid_export_energy_year` | Sensor | kWh | HS3 | Parallellsystem | Nej |
| Parallellsystem nät exportenergi totalt | `sensor.saj_parallel_grid_export_energy_total` | Sensor | kWh | HS3 | Parallellsystem | Nej |
| Parallellsystem solmätare energi idag | `sensor.saj_parallel_pv_meter_energy_today` | Sensor | kWh | HS3 | Parallellsystem | Nej |
| Parallellsystem solmätare energi denna månad | `sensor.saj_parallel_pv_meter_energy_month` | Sensor | kWh | HS3 | Parallellsystem | Nej |
| Parallellsystem solmätare energi i år | `sensor.saj_parallel_pv_meter_energy_year` | Sensor | kWh | HS3 | Parallellsystem | Nej |
| Parallellsystem solmätare energi totalt | `sensor.saj_parallel_pv_meter_energy_total` | Sensor | kWh | HS3 | Parallellsystem | Nej |
| Parallellsystem reservlast effekt | `sensor.saj_parallel_backup_load_power` | Sensor | W | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem batterieffekt | `sensor.saj_parallel_battery_power` | Sensor | W | HS3, H2 | Parallellsystem | Ja |
| Parallellsystem nätlast effekt | `sensor.saj_parallel_grid_load_power` | Sensor | W | HS3, H2 | Parallellsystem | Nej |
| Parallellsystem nät effekt | `sensor.saj_parallel_grid_power` | Sensor | W | HS3, H2 | Parallellsystem | Ja |
| Parallellsystem hushållslast effekt | `sensor.saj_parallel_load_power` | Sensor | W | HS3, H2 | Parallellsystem | Ja |
| Parallellsystem soleffekt | `sensor.saj_parallel_pv_power` | Sensor | W | HS3, H2 | Parallellsystem | Ja |
