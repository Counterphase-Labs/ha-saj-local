[en](../../../en-gb/user/entities/parallel-system.md) | de | [nl](../../../nl/user/entities/parallel-system.md) | [fr](../../../fr/user/entities/parallel-system.md) | [zh](../../../zh-hans/user/entities/parallel-system.md) | [es](../../../es/user/entities/parallel-system.md) | [it](../../../it/user/entities/parallel-system.md) | [pl](../../../pl/user/entities/parallel-system.md) | [sv](../../../sv/user/entities/parallel-system.md)

# Parallelsystem

Die Messwerte eines Parallelsystems.

Die Funktionsliste der Integration erklärt die Entitäten (Parallelsystem) in [Optionale Ausstattung](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

63 Entitäten. Erzeugt von `make docs`. Nicht von Hand bearbeiten.

Ein in Konfigurieren gesetztes Präfix steht nach `saj_` in der ID jeder Entität (Parallelsystem), zum Beispiel `sensor.saj_house_parallel_id` mit dem Präfix `house`.

| Name | Entitäts-ID | Typ | Einheit | Modelle | Ausstattung und Anzahl | Standardmäßig aktiviert |
| --- | --- | --- | --- | --- | --- | --- |
| Parallelgerät-ID | `sensor.saj_parallel_id` | Sensor | - | HS3, H2 | Parallelsystem | Nein |
| Anzahl der Parallelgeräte | `sensor.saj_parallel_count` | Sensor | - | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Batterie-Ladezustand | `sensor.saj_parallel_battery_soc` | Sensor | % | HS3, H2 | Parallelsystem | Ja |
| Parallelsystem Batteriekapazität | `sensor.saj_parallel_battery_capacity` | Sensor | Ah | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Zähler B Leistung | `sensor.saj_parallel_meter_b_power` | Sensor | W | HS3 | Parallelsystem | Nein |
| Parallelsystem Solarenergie heute | `sensor.saj_parallel_pv_energy_today` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Solarenergie diesen Monat | `sensor.saj_parallel_pv_energy_month` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Solarenergie dieses Jahr | `sensor.saj_parallel_pv_energy_year` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Solarenergie gesamt | `sensor.saj_parallel_pv_energy_total` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Batterie-Ladeenergie heute | `sensor.saj_parallel_battery_charge_energy_today` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Batterie-Ladeenergie diesen Monat | `sensor.saj_parallel_battery_charge_energy_month` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Batterie-Ladeenergie dieses Jahr | `sensor.saj_parallel_battery_charge_energy_year` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Batterie-Ladeenergie gesamt | `sensor.saj_parallel_battery_charge_energy_total` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Batterie-Entladeenergie heute | `sensor.saj_parallel_battery_discharge_energy_today` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Batterie-Entladeenergie diesen Monat | `sensor.saj_parallel_battery_discharge_energy_month` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Batterie-Entladeenergie dieses Jahr | `sensor.saj_parallel_battery_discharge_energy_year` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Batterie-Entladeenergie gesamt | `sensor.saj_parallel_battery_discharge_energy_total` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzeinspeiseenergie L1 heute | `sensor.saj_parallel_grid_l1_export_energy_today` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzeinspeiseenergie L1 diesen Monat | `sensor.saj_parallel_grid_l1_export_energy_month` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzeinspeiseenergie L1 dieses Jahr | `sensor.saj_parallel_grid_l1_export_energy_year` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzeinspeiseenergie L1 gesamt | `sensor.saj_parallel_grid_l1_export_energy_total` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzeinspeiseenergie L2 heute | `sensor.saj_parallel_grid_l2_export_energy_today` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzeinspeiseenergie L2 diesen Monat | `sensor.saj_parallel_grid_l2_export_energy_month` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzeinspeiseenergie L2 dieses Jahr | `sensor.saj_parallel_grid_l2_export_energy_year` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzeinspeiseenergie L2 gesamt | `sensor.saj_parallel_grid_l2_export_energy_total` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzeinspeiseenergie L3 heute | `sensor.saj_parallel_grid_l3_export_energy_today` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzeinspeiseenergie L3 diesen Monat | `sensor.saj_parallel_grid_l3_export_energy_month` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzeinspeiseenergie L3 dieses Jahr | `sensor.saj_parallel_grid_l3_export_energy_year` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzeinspeiseenergie L3 gesamt | `sensor.saj_parallel_grid_l3_export_energy_total` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzbezugsenergie L1 heute | `sensor.saj_parallel_grid_l1_import_energy_today` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzbezugsenergie L1 diesen Monat | `sensor.saj_parallel_grid_l1_import_energy_month` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzbezugsenergie L1 dieses Jahr | `sensor.saj_parallel_grid_l1_import_energy_year` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzbezugsenergie L1 gesamt | `sensor.saj_parallel_grid_l1_import_energy_total` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzbezugsenergie L2 heute | `sensor.saj_parallel_grid_l2_import_energy_today` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzbezugsenergie L2 diesen Monat | `sensor.saj_parallel_grid_l2_import_energy_month` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzbezugsenergie L2 dieses Jahr | `sensor.saj_parallel_grid_l2_import_energy_year` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzbezugsenergie L2 gesamt | `sensor.saj_parallel_grid_l2_import_energy_total` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzbezugsenergie L3 heute | `sensor.saj_parallel_grid_l3_import_energy_today` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzbezugsenergie L3 diesen Monat | `sensor.saj_parallel_grid_l3_import_energy_month` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzbezugsenergie L3 dieses Jahr | `sensor.saj_parallel_grid_l3_import_energy_year` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzbezugsenergie L3 gesamt | `sensor.saj_parallel_grid_l3_import_energy_total` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Hauslastenergie heute | `sensor.saj_parallel_load_energy_today` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Hauslastenergie diesen Monat | `sensor.saj_parallel_load_energy_month` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Hauslastenergie dieses Jahr | `sensor.saj_parallel_load_energy_year` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Hauslastenergie gesamt | `sensor.saj_parallel_load_energy_total` | Sensor | kWh | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzbezugsenergie heute | `sensor.saj_parallel_grid_import_energy_today` | Sensor | kWh | HS3 | Parallelsystem | Nein |
| Parallelsystem Netzbezugsenergie diesen Monat | `sensor.saj_parallel_grid_import_energy_month` | Sensor | kWh | HS3 | Parallelsystem | Nein |
| Parallelsystem Netzbezugsenergie dieses Jahr | `sensor.saj_parallel_grid_import_energy_year` | Sensor | kWh | HS3 | Parallelsystem | Nein |
| Parallelsystem Netzbezugsenergie gesamt | `sensor.saj_parallel_grid_import_energy_total` | Sensor | kWh | HS3 | Parallelsystem | Nein |
| Parallelsystem Netzeinspeiseenergie heute | `sensor.saj_parallel_grid_export_energy_today` | Sensor | kWh | HS3 | Parallelsystem | Nein |
| Parallelsystem Netzeinspeiseenergie diesen Monat | `sensor.saj_parallel_grid_export_energy_month` | Sensor | kWh | HS3 | Parallelsystem | Nein |
| Parallelsystem Netzeinspeiseenergie dieses Jahr | `sensor.saj_parallel_grid_export_energy_year` | Sensor | kWh | HS3 | Parallelsystem | Nein |
| Parallelsystem Netzeinspeiseenergie gesamt | `sensor.saj_parallel_grid_export_energy_total` | Sensor | kWh | HS3 | Parallelsystem | Nein |
| Parallelsystem Solarzählerenergie heute | `sensor.saj_parallel_pv_meter_energy_today` | Sensor | kWh | HS3 | Parallelsystem | Nein |
| Parallelsystem Solarzählerenergie diesen Monat | `sensor.saj_parallel_pv_meter_energy_month` | Sensor | kWh | HS3 | Parallelsystem | Nein |
| Parallelsystem Solarzählerenergie dieses Jahr | `sensor.saj_parallel_pv_meter_energy_year` | Sensor | kWh | HS3 | Parallelsystem | Nein |
| Parallelsystem Solarzählerenergie gesamt | `sensor.saj_parallel_pv_meter_energy_total` | Sensor | kWh | HS3 | Parallelsystem | Nein |
| Parallelsystem Notstromlastleistung | `sensor.saj_parallel_backup_load_power` | Sensor | W | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Batterieleistung | `sensor.saj_parallel_battery_power` | Sensor | W | HS3, H2 | Parallelsystem | Ja |
| Parallelsystem Netzlastleistung | `sensor.saj_parallel_grid_load_power` | Sensor | W | HS3, H2 | Parallelsystem | Nein |
| Parallelsystem Netzleistung | `sensor.saj_parallel_grid_power` | Sensor | W | HS3, H2 | Parallelsystem | Ja |
| Parallelsystem Hauslastleistung | `sensor.saj_parallel_load_power` | Sensor | W | HS3, H2 | Parallelsystem | Ja |
| Parallelsystem Solarleistung | `sensor.saj_parallel_pv_power` | Sensor | W | HS3, H2 | Parallelsystem | Ja |
