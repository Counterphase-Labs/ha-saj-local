[en](../../../en-gb/user/entities/grid-and-meter-a.md) | [de](../../../de/user/entities/grid-and-meter-a.md) | [nl](../../../nl/user/entities/grid-and-meter-a.md) | [fr](../../../fr/user/entities/grid-and-meter-a.md) | [zh](../../../zh-hans/user/entities/grid-and-meter-a.md) | [es](../../../es/user/entities/grid-and-meter-a.md) | [it](../../../it/user/entities/grid-and-meter-a.md) | pl | [sv](../../../sv/user/entities/grid-and-meter-a.md)

# Sieć i Licznik A

Przyłącze sieciowe i Licznik A, licznik sieci.

Lista funkcji integracji wyjaśnia encje obszaru Sieć i Licznik A w [Urządzenia i encje](../../../../custom_components/saj_local/docs/features.md#devices-and-entities) i [Wyposażenie opcjonalne](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

Liczba encji: 88. Wygenerowano poleceniem `make docs`. Nie edytuj ręcznie.

Prefiks ustawiony w Skonfiguruj trafia po `saj_` w ID każdej encji: Sieć i Licznik A, na przykład `sensor.saj_house_grid_connection_countdown` z prefiksem `house`.

| Nazwa | ID encji | Typ | Jednostka | Modele | Wyposażenie i liczba | Włączona domyślnie |
| --- | --- | --- | --- | --- | --- | --- |
| Odliczanie do podłączenia do sieci | `sensor.saj_grid_connection_countdown` | Sensor | s | HS3, H2 | - | Nie |
| Napięcie sieci L1 | `sensor.saj_grid_l1_voltage` | Sensor | V | HS3, H2 | - | Tak |
| Prąd sieci L1 | `sensor.saj_grid_l1_current` | Sensor | A | HS3, H2 | - | Nie |
| Częstotliwość sieci L1 | `sensor.saj_grid_l1_frequency` | Sensor | Hz | HS3, H2 | - | Tak |
| Prąd stały sieci L1 | `sensor.saj_grid_l1_dc_current` | Sensor | mA | HS3, H2 | - | Nie |
| Moc sieci L1 | `sensor.saj_grid_l1_power` | Sensor | W | HS3, H2 | - | Nie |
| Moc pozorna sieci L1 | `sensor.saj_grid_l1_apparent_power` | Sensor | VA | HS3, H2 | - | Nie |
| Współczynnik mocy sieci L1 | `sensor.saj_grid_l1_power_factor` | Sensor | - | HS3, H2 | - | Nie |
| Napięcie sieci L2 | `sensor.saj_grid_l2_voltage` | Sensor | V | HS3, H2 | Faza 2 i wyższe | Tak |
| Prąd sieci L2 | `sensor.saj_grid_l2_current` | Sensor | A | HS3, H2 | Faza 2 i wyższe | Nie |
| Częstotliwość sieci L2 | `sensor.saj_grid_l2_frequency` | Sensor | Hz | HS3, H2 | Faza 2 i wyższe | Nie |
| Prąd stały sieci L2 | `sensor.saj_grid_l2_dc_current` | Sensor | mA | HS3, H2 | Faza 2 i wyższe | Nie |
| Moc sieci L2 | `sensor.saj_grid_l2_power` | Sensor | W | HS3, H2 | Faza 2 i wyższe | Nie |
| Moc pozorna sieci L2 | `sensor.saj_grid_l2_apparent_power` | Sensor | VA | HS3, H2 | Faza 2 i wyższe | Nie |
| Współczynnik mocy sieci L2 | `sensor.saj_grid_l2_power_factor` | Sensor | - | HS3, H2 | Faza 2 i wyższe | Nie |
| Napięcie sieci L3 | `sensor.saj_grid_l3_voltage` | Sensor | V | HS3, H2 | Faza 3 i wyższe | Tak |
| Prąd sieci L3 | `sensor.saj_grid_l3_current` | Sensor | A | HS3, H2 | Faza 3 i wyższe | Nie |
| Częstotliwość sieci L3 | `sensor.saj_grid_l3_frequency` | Sensor | Hz | HS3, H2 | Faza 3 i wyższe | Nie |
| Prąd stały sieci L3 | `sensor.saj_grid_l3_dc_current` | Sensor | mA | HS3, H2 | Faza 3 i wyższe | Nie |
| Moc sieci L3 | `sensor.saj_grid_l3_power` | Sensor | W | HS3, H2 | Faza 3 i wyższe | Nie |
| Moc pozorna sieci L3 | `sensor.saj_grid_l3_apparent_power` | Sensor | VA | HS3, H2 | Faza 3 i wyższe | Nie |
| Współczynnik mocy sieci L3 | `sensor.saj_grid_l3_power_factor` | Sensor | - | HS3, H2 | Faza 3 i wyższe | Nie |
| Napięcie wyjścia sieciowego L1 | `sensor.saj_grid_output_l1_voltage` | Sensor | V | HS3, H2 | - | Nie |
| Prąd wyjścia sieciowego L1 | `sensor.saj_grid_output_l1_current` | Sensor | A | HS3, H2 | - | Nie |
| Częstotliwość wyjścia sieciowego L1 | `sensor.saj_grid_output_l1_frequency` | Sensor | Hz | HS3, H2 | - | Nie |
| Moc wyjścia sieciowego L1 | `sensor.saj_grid_output_l1_power` | Sensor | W | HS3, H2 | - | Nie |
| Napięcie wyjścia sieciowego L2 | `sensor.saj_grid_output_l2_voltage` | Sensor | V | HS3, H2 | Faza 2 i wyższe | Nie |
| Moc wyjścia sieciowego L2 | `sensor.saj_grid_output_l2_power` | Sensor | W | HS3, H2 | Faza 2 i wyższe | Nie |
| Napięcie wyjścia sieciowego L3 | `sensor.saj_grid_output_l3_voltage` | Sensor | V | HS3, H2 | Faza 3 i wyższe | Nie |
| Moc wyjścia sieciowego L3 | `sensor.saj_grid_output_l3_power` | Sensor | W | HS3, H2 | Faza 3 i wyższe | Nie |
| Moc sieci | `sensor.saj_grid_power` | Sensor | W | HS3, H2 | - | Tak |
| Moc obciążenia sieci | `sensor.saj_grid_load_power` | Sensor | W | HS3, H2 | - | Nie |
| Energia oddana do sieci L1 dzisiaj | `sensor.saj_grid_l1_export_energy_today` | Sensor | kWh | HS3, H2 | - | Nie |
| Energia oddana do sieci L1 w tym miesiącu | `sensor.saj_grid_l1_export_energy_month` | Sensor | kWh | HS3, H2 | - | Nie |
| Energia oddana do sieci L1 w tym roku | `sensor.saj_grid_l1_export_energy_year` | Sensor | kWh | HS3, H2 | - | Nie |
| Energia oddana do sieci L1 łącznie | `sensor.saj_grid_l1_export_energy_total` | Sensor | kWh | HS3, H2 | - | Nie |
| Energia pobrana z sieci L1 dzisiaj | `sensor.saj_grid_l1_import_energy_today` | Sensor | kWh | HS3, H2 | - | Nie |
| Energia pobrana z sieci L1 w tym miesiącu | `sensor.saj_grid_l1_import_energy_month` | Sensor | kWh | HS3, H2 | - | Nie |
| Energia pobrana z sieci L1 w tym roku | `sensor.saj_grid_l1_import_energy_year` | Sensor | kWh | HS3, H2 | - | Nie |
| Energia pobrana z sieci L1 łącznie | `sensor.saj_grid_l1_import_energy_total` | Sensor | kWh | HS3, H2 | - | Nie |
| Energia oddana do sieci L2 dzisiaj | `sensor.saj_grid_l2_export_energy_today` | Sensor | kWh | HS3, H2 | Faza 2 i wyższe | Nie |
| Energia oddana do sieci L2 w tym miesiącu | `sensor.saj_grid_l2_export_energy_month` | Sensor | kWh | HS3, H2 | Faza 2 i wyższe | Nie |
| Energia oddana do sieci L2 w tym roku | `sensor.saj_grid_l2_export_energy_year` | Sensor | kWh | HS3, H2 | Faza 2 i wyższe | Nie |
| Energia oddana do sieci L2 łącznie | `sensor.saj_grid_l2_export_energy_total` | Sensor | kWh | HS3, H2 | Faza 2 i wyższe | Nie |
| Energia oddana do sieci L3 dzisiaj | `sensor.saj_grid_l3_export_energy_today` | Sensor | kWh | HS3, H2 | Faza 3 i wyższe | Nie |
| Energia oddana do sieci L3 w tym miesiącu | `sensor.saj_grid_l3_export_energy_month` | Sensor | kWh | HS3, H2 | Faza 3 i wyższe | Nie |
| Energia oddana do sieci L3 w tym roku | `sensor.saj_grid_l3_export_energy_year` | Sensor | kWh | HS3, H2 | Faza 3 i wyższe | Nie |
| Energia oddana do sieci L3 łącznie | `sensor.saj_grid_l3_export_energy_total` | Sensor | kWh | HS3, H2 | Faza 3 i wyższe | Nie |
| Energia pobrana z sieci L2 dzisiaj | `sensor.saj_grid_l2_import_energy_today` | Sensor | kWh | HS3, H2 | Faza 2 i wyższe | Nie |
| Energia pobrana z sieci L2 w tym miesiącu | `sensor.saj_grid_l2_import_energy_month` | Sensor | kWh | HS3, H2 | Faza 2 i wyższe | Nie |
| Energia pobrana z sieci L2 w tym roku | `sensor.saj_grid_l2_import_energy_year` | Sensor | kWh | HS3, H2 | Faza 2 i wyższe | Nie |
| Energia pobrana z sieci L2 łącznie | `sensor.saj_grid_l2_import_energy_total` | Sensor | kWh | HS3, H2 | Faza 2 i wyższe | Nie |
| Energia pobrana z sieci L3 dzisiaj | `sensor.saj_grid_l3_import_energy_today` | Sensor | kWh | HS3, H2 | Faza 3 i wyższe | Nie |
| Energia pobrana z sieci L3 w tym miesiącu | `sensor.saj_grid_l3_import_energy_month` | Sensor | kWh | HS3, H2 | Faza 3 i wyższe | Nie |
| Energia pobrana z sieci L3 w tym roku | `sensor.saj_grid_l3_import_energy_year` | Sensor | kWh | HS3, H2 | Faza 3 i wyższe | Nie |
| Energia pobrana z sieci L3 łącznie | `sensor.saj_grid_l3_import_energy_total` | Sensor | kWh | HS3, H2 | Faza 3 i wyższe | Nie |
| Energia pobrana z sieci dzisiaj | `sensor.saj_grid_import_energy_today` | Sensor | kWh | HS3, H2 | - | Tak |
| Energia pobrana z sieci w tym miesiącu | `sensor.saj_grid_import_energy_month` | Sensor | kWh | HS3, H2 | - | Nie |
| Energia pobrana z sieci w tym roku | `sensor.saj_grid_import_energy_year` | Sensor | kWh | HS3, H2 | - | Nie |
| Energia pobrana z sieci łącznie | `sensor.saj_grid_import_energy_total` | Sensor | kWh | HS3, H2 | - | Tak |
| Energia oddana do sieci dzisiaj | `sensor.saj_grid_export_energy_today` | Sensor | kWh | HS3, H2 | - | Tak |
| Energia oddana do sieci w tym miesiącu | `sensor.saj_grid_export_energy_month` | Sensor | kWh | HS3, H2 | - | Nie |
| Energia oddana do sieci w tym roku | `sensor.saj_grid_export_energy_year` | Sensor | kWh | HS3, H2 | - | Nie |
| Energia oddana do sieci łącznie | `sensor.saj_grid_export_energy_total` | Sensor | kWh | HS3, H2 | - | Tak |
| Napięcie licznika A L1 | `sensor.saj_meter_a_l1_voltage` | Sensor | V | HS3, H2 | Licznik A | Nie |
| Prąd licznika A L1 | `sensor.saj_meter_a_l1_current` | Sensor | A | HS3, H2 | Licznik A | Nie |
| Moc licznika A L1 | `sensor.saj_meter_a_l1_power` | Sensor | W | HS3, H2 | Licznik A | Nie |
| Moc pozorna licznika A L1 | `sensor.saj_meter_a_l1_apparent_power` | Sensor | VA | HS3, H2 | Licznik A | Nie |
| Współczynnik mocy licznika A L1 | `sensor.saj_meter_a_l1_power_factor` | Sensor | - | HS3, H2 | Licznik A | Nie |
| Częstotliwość licznika A L1 | `sensor.saj_meter_a_l1_frequency` | Sensor | Hz | HS3, H2 | Licznik A | Nie |
| Napięcie licznika A L2 | `sensor.saj_meter_a_l2_voltage` | Sensor | V | HS3, H2 | Licznik A; Faza 2 i wyższe | Nie |
| Prąd licznika A L2 | `sensor.saj_meter_a_l2_current` | Sensor | A | HS3, H2 | Licznik A; Faza 2 i wyższe | Nie |
| Moc licznika A L2 | `sensor.saj_meter_a_l2_power` | Sensor | W | HS3, H2 | Licznik A; Faza 2 i wyższe | Nie |
| Moc pozorna licznika A L2 | `sensor.saj_meter_a_l2_apparent_power` | Sensor | VA | HS3, H2 | Licznik A; Faza 2 i wyższe | Nie |
| Współczynnik mocy licznika A L2 | `sensor.saj_meter_a_l2_power_factor` | Sensor | - | HS3, H2 | Licznik A; Faza 2 i wyższe | Nie |
| Częstotliwość licznika A L2 | `sensor.saj_meter_a_l2_frequency` | Sensor | Hz | HS3, H2 | Licznik A; Faza 2 i wyższe | Nie |
| Napięcie licznika A L3 | `sensor.saj_meter_a_l3_voltage` | Sensor | V | HS3, H2 | Licznik A; Faza 3 i wyższe | Nie |
| Prąd licznika A L3 | `sensor.saj_meter_a_l3_current` | Sensor | A | HS3, H2 | Licznik A; Faza 3 i wyższe | Nie |
| Moc licznika A L3 | `sensor.saj_meter_a_l3_power` | Sensor | W | HS3, H2 | Licznik A; Faza 3 i wyższe | Nie |
| Moc pozorna licznika A L3 | `sensor.saj_meter_a_l3_apparent_power` | Sensor | VA | HS3, H2 | Licznik A; Faza 3 i wyższe | Nie |
| Współczynnik mocy licznika A L3 | `sensor.saj_meter_a_l3_power_factor` | Sensor | - | HS3, H2 | Licznik A; Faza 3 i wyższe | Nie |
| Częstotliwość licznika A L3 | `sensor.saj_meter_a_l3_frequency` | Sensor | Hz | HS3, H2 | Licznik A; Faza 3 i wyższe | Nie |
| Moc bierna licznika A L1 | `sensor.saj_meter_a_l1_reactive_power` | Sensor | var | HS3 | Licznik A | Nie |
| Moc bierna licznika A L2 | `sensor.saj_meter_a_l2_reactive_power` | Sensor | var | HS3 | Licznik A; Faza 2 i wyższe | Nie |
| Moc bierna licznika A L3 | `sensor.saj_meter_a_l3_reactive_power` | Sensor | var | HS3 | Licznik A; Faza 3 i wyższe | Nie |
| Moc licznika A | `sensor.saj_meter_a_power` | Sensor | W | HS3, H2 | Licznik A | Tak |
| Typ sieci | `sensor.saj_grid_type` | Sensor | - | H2 | - | Nie |
| Moc pozorna sieci | `sensor.saj_grid_apparent_power` | Sensor | VA | H2 | - | Nie |
