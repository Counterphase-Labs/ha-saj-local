[en](../../../en-gb/user/entities/grid-and-meter-a.md) | de | [nl](../../../nl/user/entities/grid-and-meter-a.md) | [fr](../../../fr/user/entities/grid-and-meter-a.md) | [zh](../../../zh-hans/user/entities/grid-and-meter-a.md) | [es](../../../es/user/entities/grid-and-meter-a.md) | [it](../../../it/user/entities/grid-and-meter-a.md) | [pl](../../../pl/user/entities/grid-and-meter-a.md) | [sv](../../../sv/user/entities/grid-and-meter-a.md)

# Netz und Zähler A

Der Netzanschluss und Zähler A, der Netzzähler.

Die Funktionsliste der Integration erklärt die Entitäten (Netz und Zähler A) in [Geräte und Entitäten](../../../../custom_components/saj_local/docs/features.md#devices-and-entities) und [Optionale Ausstattung](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

88 Entitäten. Erzeugt von `make docs`. Nicht von Hand bearbeiten.

Ein in Konfigurieren gesetztes Präfix steht nach `saj_` in der ID jeder Entität (Netz und Zähler A), zum Beispiel `sensor.saj_house_grid_connection_countdown` mit dem Präfix `house`.

| Name | Entitäts-ID | Typ | Einheit | Modelle | Ausstattung und Anzahl | Standardmäßig aktiviert |
| --- | --- | --- | --- | --- | --- | --- |
| Countdown der Netzzuschaltung | `sensor.saj_grid_connection_countdown` | Sensor | s | HS3, H2 | - | Nein |
| Netzspannung L1 | `sensor.saj_grid_l1_voltage` | Sensor | V | HS3, H2 | - | Ja |
| Netzstrom L1 | `sensor.saj_grid_l1_current` | Sensor | A | HS3, H2 | - | Nein |
| Netzfrequenz L1 | `sensor.saj_grid_l1_frequency` | Sensor | Hz | HS3, H2 | - | Ja |
| Netzgleichstrom L1 | `sensor.saj_grid_l1_dc_current` | Sensor | mA | HS3, H2 | - | Nein |
| Netzleistung L1 | `sensor.saj_grid_l1_power` | Sensor | W | HS3, H2 | - | Nein |
| Netzscheinleistung L1 | `sensor.saj_grid_l1_apparent_power` | Sensor | VA | HS3, H2 | - | Nein |
| Netzleistungsfaktor L1 | `sensor.saj_grid_l1_power_factor` | Sensor | - | HS3, H2 | - | Nein |
| Netzspannung L2 | `sensor.saj_grid_l2_voltage` | Sensor | V | HS3, H2 | Phase 2 und höher | Ja |
| Netzstrom L2 | `sensor.saj_grid_l2_current` | Sensor | A | HS3, H2 | Phase 2 und höher | Nein |
| Netzfrequenz L2 | `sensor.saj_grid_l2_frequency` | Sensor | Hz | HS3, H2 | Phase 2 und höher | Nein |
| Netzgleichstrom L2 | `sensor.saj_grid_l2_dc_current` | Sensor | mA | HS3, H2 | Phase 2 und höher | Nein |
| Netzleistung L2 | `sensor.saj_grid_l2_power` | Sensor | W | HS3, H2 | Phase 2 und höher | Nein |
| Netzscheinleistung L2 | `sensor.saj_grid_l2_apparent_power` | Sensor | VA | HS3, H2 | Phase 2 und höher | Nein |
| Netzleistungsfaktor L2 | `sensor.saj_grid_l2_power_factor` | Sensor | - | HS3, H2 | Phase 2 und höher | Nein |
| Netzspannung L3 | `sensor.saj_grid_l3_voltage` | Sensor | V | HS3, H2 | Phase 3 und höher | Ja |
| Netzstrom L3 | `sensor.saj_grid_l3_current` | Sensor | A | HS3, H2 | Phase 3 und höher | Nein |
| Netzfrequenz L3 | `sensor.saj_grid_l3_frequency` | Sensor | Hz | HS3, H2 | Phase 3 und höher | Nein |
| Netzgleichstrom L3 | `sensor.saj_grid_l3_dc_current` | Sensor | mA | HS3, H2 | Phase 3 und höher | Nein |
| Netzleistung L3 | `sensor.saj_grid_l3_power` | Sensor | W | HS3, H2 | Phase 3 und höher | Nein |
| Netzscheinleistung L3 | `sensor.saj_grid_l3_apparent_power` | Sensor | VA | HS3, H2 | Phase 3 und höher | Nein |
| Netzleistungsfaktor L3 | `sensor.saj_grid_l3_power_factor` | Sensor | - | HS3, H2 | Phase 3 und höher | Nein |
| Netzausgangsspannung L1 | `sensor.saj_grid_output_l1_voltage` | Sensor | V | HS3, H2 | - | Nein |
| Netzausgangsstrom L1 | `sensor.saj_grid_output_l1_current` | Sensor | A | HS3, H2 | - | Nein |
| Netzausgangsfrequenz L1 | `sensor.saj_grid_output_l1_frequency` | Sensor | Hz | HS3, H2 | - | Nein |
| Netzausgangsleistung L1 | `sensor.saj_grid_output_l1_power` | Sensor | W | HS3, H2 | - | Nein |
| Netzausgangsspannung L2 | `sensor.saj_grid_output_l2_voltage` | Sensor | V | HS3, H2 | Phase 2 und höher | Nein |
| Netzausgangsleistung L2 | `sensor.saj_grid_output_l2_power` | Sensor | W | HS3, H2 | Phase 2 und höher | Nein |
| Netzausgangsspannung L3 | `sensor.saj_grid_output_l3_voltage` | Sensor | V | HS3, H2 | Phase 3 und höher | Nein |
| Netzausgangsleistung L3 | `sensor.saj_grid_output_l3_power` | Sensor | W | HS3, H2 | Phase 3 und höher | Nein |
| Netzleistung | `sensor.saj_grid_power` | Sensor | W | HS3, H2 | - | Ja |
| Netzlastleistung | `sensor.saj_grid_load_power` | Sensor | W | HS3, H2 | - | Nein |
| Netzeinspeiseenergie L1 heute | `sensor.saj_grid_l1_export_energy_today` | Sensor | kWh | HS3, H2 | - | Nein |
| Netzeinspeiseenergie L1 diesen Monat | `sensor.saj_grid_l1_export_energy_month` | Sensor | kWh | HS3, H2 | - | Nein |
| Netzeinspeiseenergie L1 dieses Jahr | `sensor.saj_grid_l1_export_energy_year` | Sensor | kWh | HS3, H2 | - | Nein |
| Netzeinspeiseenergie L1 gesamt | `sensor.saj_grid_l1_export_energy_total` | Sensor | kWh | HS3, H2 | - | Nein |
| Netzbezugsenergie L1 heute | `sensor.saj_grid_l1_import_energy_today` | Sensor | kWh | HS3, H2 | - | Nein |
| Netzbezugsenergie L1 diesen Monat | `sensor.saj_grid_l1_import_energy_month` | Sensor | kWh | HS3, H2 | - | Nein |
| Netzbezugsenergie L1 dieses Jahr | `sensor.saj_grid_l1_import_energy_year` | Sensor | kWh | HS3, H2 | - | Nein |
| Netzbezugsenergie L1 gesamt | `sensor.saj_grid_l1_import_energy_total` | Sensor | kWh | HS3, H2 | - | Nein |
| Netzeinspeiseenergie L2 heute | `sensor.saj_grid_l2_export_energy_today` | Sensor | kWh | HS3, H2 | Phase 2 und höher | Nein |
| Netzeinspeiseenergie L2 diesen Monat | `sensor.saj_grid_l2_export_energy_month` | Sensor | kWh | HS3, H2 | Phase 2 und höher | Nein |
| Netzeinspeiseenergie L2 dieses Jahr | `sensor.saj_grid_l2_export_energy_year` | Sensor | kWh | HS3, H2 | Phase 2 und höher | Nein |
| Netzeinspeiseenergie L2 gesamt | `sensor.saj_grid_l2_export_energy_total` | Sensor | kWh | HS3, H2 | Phase 2 und höher | Nein |
| Netzeinspeiseenergie L3 heute | `sensor.saj_grid_l3_export_energy_today` | Sensor | kWh | HS3, H2 | Phase 3 und höher | Nein |
| Netzeinspeiseenergie L3 diesen Monat | `sensor.saj_grid_l3_export_energy_month` | Sensor | kWh | HS3, H2 | Phase 3 und höher | Nein |
| Netzeinspeiseenergie L3 dieses Jahr | `sensor.saj_grid_l3_export_energy_year` | Sensor | kWh | HS3, H2 | Phase 3 und höher | Nein |
| Netzeinspeiseenergie L3 gesamt | `sensor.saj_grid_l3_export_energy_total` | Sensor | kWh | HS3, H2 | Phase 3 und höher | Nein |
| Netzbezugsenergie L2 heute | `sensor.saj_grid_l2_import_energy_today` | Sensor | kWh | HS3, H2 | Phase 2 und höher | Nein |
| Netzbezugsenergie L2 diesen Monat | `sensor.saj_grid_l2_import_energy_month` | Sensor | kWh | HS3, H2 | Phase 2 und höher | Nein |
| Netzbezugsenergie L2 dieses Jahr | `sensor.saj_grid_l2_import_energy_year` | Sensor | kWh | HS3, H2 | Phase 2 und höher | Nein |
| Netzbezugsenergie L2 gesamt | `sensor.saj_grid_l2_import_energy_total` | Sensor | kWh | HS3, H2 | Phase 2 und höher | Nein |
| Netzbezugsenergie L3 heute | `sensor.saj_grid_l3_import_energy_today` | Sensor | kWh | HS3, H2 | Phase 3 und höher | Nein |
| Netzbezugsenergie L3 diesen Monat | `sensor.saj_grid_l3_import_energy_month` | Sensor | kWh | HS3, H2 | Phase 3 und höher | Nein |
| Netzbezugsenergie L3 dieses Jahr | `sensor.saj_grid_l3_import_energy_year` | Sensor | kWh | HS3, H2 | Phase 3 und höher | Nein |
| Netzbezugsenergie L3 gesamt | `sensor.saj_grid_l3_import_energy_total` | Sensor | kWh | HS3, H2 | Phase 3 und höher | Nein |
| Netzbezugsenergie heute | `sensor.saj_grid_import_energy_today` | Sensor | kWh | HS3, H2 | - | Ja |
| Netzbezugsenergie diesen Monat | `sensor.saj_grid_import_energy_month` | Sensor | kWh | HS3, H2 | - | Nein |
| Netzbezugsenergie dieses Jahr | `sensor.saj_grid_import_energy_year` | Sensor | kWh | HS3, H2 | - | Nein |
| Netzbezugsenergie gesamt | `sensor.saj_grid_import_energy_total` | Sensor | kWh | HS3, H2 | - | Ja |
| Netzeinspeiseenergie heute | `sensor.saj_grid_export_energy_today` | Sensor | kWh | HS3, H2 | - | Ja |
| Netzeinspeiseenergie diesen Monat | `sensor.saj_grid_export_energy_month` | Sensor | kWh | HS3, H2 | - | Nein |
| Netzeinspeiseenergie dieses Jahr | `sensor.saj_grid_export_energy_year` | Sensor | kWh | HS3, H2 | - | Nein |
| Netzeinspeiseenergie gesamt | `sensor.saj_grid_export_energy_total` | Sensor | kWh | HS3, H2 | - | Ja |
| Zähler A L1 Spannung | `sensor.saj_meter_a_l1_voltage` | Sensor | V | HS3, H2 | Zähler A | Nein |
| Zähler A L1 Strom | `sensor.saj_meter_a_l1_current` | Sensor | A | HS3, H2 | Zähler A | Nein |
| Zähler A L1 Leistung | `sensor.saj_meter_a_l1_power` | Sensor | W | HS3, H2 | Zähler A | Nein |
| Zähler A L1 Scheinleistung | `sensor.saj_meter_a_l1_apparent_power` | Sensor | VA | HS3, H2 | Zähler A | Nein |
| Zähler A L1 Leistungsfaktor | `sensor.saj_meter_a_l1_power_factor` | Sensor | - | HS3, H2 | Zähler A | Nein |
| Zähler A L1 Frequenz | `sensor.saj_meter_a_l1_frequency` | Sensor | Hz | HS3, H2 | Zähler A | Nein |
| Zähler A L2 Spannung | `sensor.saj_meter_a_l2_voltage` | Sensor | V | HS3, H2 | Zähler A; Phase 2 und höher | Nein |
| Zähler A L2 Strom | `sensor.saj_meter_a_l2_current` | Sensor | A | HS3, H2 | Zähler A; Phase 2 und höher | Nein |
| Zähler A L2 Leistung | `sensor.saj_meter_a_l2_power` | Sensor | W | HS3, H2 | Zähler A; Phase 2 und höher | Nein |
| Zähler A L2 Scheinleistung | `sensor.saj_meter_a_l2_apparent_power` | Sensor | VA | HS3, H2 | Zähler A; Phase 2 und höher | Nein |
| Zähler A L2 Leistungsfaktor | `sensor.saj_meter_a_l2_power_factor` | Sensor | - | HS3, H2 | Zähler A; Phase 2 und höher | Nein |
| Zähler A L2 Frequenz | `sensor.saj_meter_a_l2_frequency` | Sensor | Hz | HS3, H2 | Zähler A; Phase 2 und höher | Nein |
| Zähler A L3 Spannung | `sensor.saj_meter_a_l3_voltage` | Sensor | V | HS3, H2 | Zähler A; Phase 3 und höher | Nein |
| Zähler A L3 Strom | `sensor.saj_meter_a_l3_current` | Sensor | A | HS3, H2 | Zähler A; Phase 3 und höher | Nein |
| Zähler A L3 Leistung | `sensor.saj_meter_a_l3_power` | Sensor | W | HS3, H2 | Zähler A; Phase 3 und höher | Nein |
| Zähler A L3 Scheinleistung | `sensor.saj_meter_a_l3_apparent_power` | Sensor | VA | HS3, H2 | Zähler A; Phase 3 und höher | Nein |
| Zähler A L3 Leistungsfaktor | `sensor.saj_meter_a_l3_power_factor` | Sensor | - | HS3, H2 | Zähler A; Phase 3 und höher | Nein |
| Zähler A L3 Frequenz | `sensor.saj_meter_a_l3_frequency` | Sensor | Hz | HS3, H2 | Zähler A; Phase 3 und höher | Nein |
| Zähler A L1 Blindleistung | `sensor.saj_meter_a_l1_reactive_power` | Sensor | var | HS3 | Zähler A | Nein |
| Zähler A L2 Blindleistung | `sensor.saj_meter_a_l2_reactive_power` | Sensor | var | HS3 | Zähler A; Phase 2 und höher | Nein |
| Zähler A L3 Blindleistung | `sensor.saj_meter_a_l3_reactive_power` | Sensor | var | HS3 | Zähler A; Phase 3 und höher | Nein |
| Zähler A Leistung | `sensor.saj_meter_a_power` | Sensor | W | HS3, H2 | Zähler A | Ja |
| Netztyp | `sensor.saj_grid_type` | Sensor | - | H2 | - | Nein |
| Netzscheinleistung | `sensor.saj_grid_apparent_power` | Sensor | VA | H2 | - | Nein |
