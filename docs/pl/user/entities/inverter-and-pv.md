[en](../../../en-gb/user/entities/inverter-and-pv.md) | [de](../../../de/user/entities/inverter-and-pv.md) | [nl](../../../nl/user/entities/inverter-and-pv.md) | [fr](../../../fr/user/entities/inverter-and-pv.md) | [zh](../../../zh-hans/user/entities/inverter-and-pv.md) | [es](../../../es/user/entities/inverter-and-pv.md) | [it](../../../it/user/entities/inverter-and-pv.md) | pl | [sv](../../../sv/user/entities/inverter-and-pv.md)

# Falownik i PV

Wyjście falownika, ciągi paneli, port awaryjny, liczniki energii, wersje i obciążenie gospodarstwa domowego.

Lista funkcji integracji wyjaśnia encje obszaru Falownik i PV w [Urządzenia i encje](../../../../custom_components/saj_local/docs/features.md#devices-and-entities).

Liczba encji: 241. Wygenerowano poleceniem `make docs`. Nie edytuj ręcznie.

Prefiks ustawiony w Skonfiguruj trafia po `saj_` w ID każdej encji: Falownik i PV, na przykład `sensor.saj_house_ethernet_protocol_version` z prefiksem `house`.

| Nazwa | ID encji | Typ | Jednostka | Modele | Wyposażenie i liczba | Włączona domyślnie |
| --- | --- | --- | --- | --- | --- | --- |
| Wersja protokołu Ethernet | `sensor.saj_ethernet_protocol_version` | Sensor | - | HS3 | - | Nie |
| Adres MAC Ethernet | `sensor.saj_ethernet_mac_address` | Sensor | - | HS3 | - | Nie |
| Tryb Ethernet | `sensor.saj_ethernet_mode` | Sensor | - | HS3 | - | Nie |
| Adres IP Ethernet | `sensor.saj_ethernet_ip_address` | Sensor | - | HS3 | - | Nie |
| Maska podsieci Ethernet | `sensor.saj_ethernet_subnet_mask` | Sensor | - | HS3 | - | Nie |
| Brama Ethernet | `sensor.saj_ethernet_gateway` | Sensor | - | HS3 | - | Nie |
| Podstawowy DNS Ethernet | `sensor.saj_ethernet_dns_primary` | Sensor | - | HS3 | - | Nie |
| Dodatkowy DNS Ethernet | `sensor.saj_ethernet_dns_secondary` | Sensor | - | HS3 | - | Nie |
| Numer kolejny ustawień | `sensor.saj_settings_sequence` | Sensor | - | HS3, H2 | - | Nie |
| Wersja protokołu ustawień | `sensor.saj_settings_protocol_version` | Sensor | - | HS3 | - | Nie |
| Konfiguracja licznika | `sensor.saj_meter_configuration` | Sensor | - | HS3, H2 | - | Nie |
| Adres licznika | `sensor.saj_meter_address` | Sensor | - | HS3, H2 | - | Nie |
| Adres RS485 | `sensor.saj_rs485_address` | Sensor | - | HS3, H2 | - | Nie |
| Szybkość transmisji RS485 | `sensor.saj_rs485_baud_rate` | Sensor | - | HS3, H2 | - | Nie |
| Protokół baterii | `sensor.saj_battery_protocol` | Sensor | - | HS3, H2 | - | Nie |
| Adres podrzędny RS485 | `sensor.saj_rs485_slave_address` | Sensor | - | HS3 | - | Nie |
| Szybkość transmisji podrzędnego RS485 | `sensor.saj_rs485_slave_baud_rate` | Sensor | - | HS3 | - | Nie |
| Zegar falownika | `sensor.saj_inverter_clock` | Sensor | - | HS3, H2 | - | Nie |
| Tryb pracy | `sensor.saj_operating_mode` | Sensor | - | HS3, H2 | - | Tak |
| Temperatura falownika | `sensor.saj_inverter_temperature` | Sensor | °C | HS3, H2 | - | Tak |
| Temperatura otoczenia | `sensor.saj_ambient_temperature` | Sensor | °C | HS3, H2 | - | Nie |
| Prąd upływu | `sensor.saj_leakage_current` | Sensor | mA | HS3, H2 | - | Nie |
| Rezystancja izolacji PV1 | `sensor.saj_pv1_insulation_resistance` | Sensor | kΩ | HS3, H2 | - | Nie |
| Rezystancja izolacji PV2 | `sensor.saj_pv2_insulation_resistance` | Sensor | kΩ | HS3, H2 | Ciąg paneli PV 2 i wyższe | Nie |
| Wartość zadana mocy rozładowania falownika | `sensor.saj_inverter_discharge_power_setpoint` | Sensor | W | HS3, H2 | - | Nie |
| Wartość zadana mocy ładowania falownika | `sensor.saj_inverter_charge_power_setpoint` | Sensor | W | HS3, H2 | - | Nie |
| Protokół baterii (obowiązujący) | `sensor.saj_battery_protocol_active` | Sensor | - | HS3, H2 | - | Nie |
| Konfiguracja licznika (obowiązująca) | `sensor.saj_meter_configuration_active` | Sensor | - | HS3, H2 | - | Nie |
| Napięcie falownika L1 | `sensor.saj_inverter_l1_voltage` | Sensor | V | HS3, H2 | - | Nie |
| Prąd falownika L1 | `sensor.saj_inverter_l1_current` | Sensor | A | HS3, H2 | - | Nie |
| Częstotliwość falownika L1 | `sensor.saj_inverter_l1_frequency` | Sensor | Hz | HS3, H2 | - | Nie |
| Moc falownika L1 | `sensor.saj_inverter_l1_power` | Sensor | W | HS3, H2 | - | Nie |
| Moc pozorna falownika L1 | `sensor.saj_inverter_l1_apparent_power` | Sensor | VA | HS3, H2 | - | Nie |
| Napięcie falownika L2 | `sensor.saj_inverter_l2_voltage` | Sensor | V | HS3, H2 | Faza 2 i wyższe | Nie |
| Prąd falownika L2 | `sensor.saj_inverter_l2_current` | Sensor | A | HS3, H2 | Faza 2 i wyższe | Nie |
| Częstotliwość falownika L2 | `sensor.saj_inverter_l2_frequency` | Sensor | Hz | HS3, H2 | Faza 2 i wyższe | Nie |
| Moc falownika L2 | `sensor.saj_inverter_l2_power` | Sensor | W | HS3, H2 | Faza 2 i wyższe | Nie |
| Moc pozorna falownika L2 | `sensor.saj_inverter_l2_apparent_power` | Sensor | VA | HS3, H2 | Faza 2 i wyższe | Nie |
| Napięcie falownika L3 | `sensor.saj_inverter_l3_voltage` | Sensor | V | HS3, H2 | Faza 3 i wyższe | Nie |
| Prąd falownika L3 | `sensor.saj_inverter_l3_current` | Sensor | A | HS3, H2 | Faza 3 i wyższe | Nie |
| Częstotliwość falownika L3 | `sensor.saj_inverter_l3_frequency` | Sensor | Hz | HS3, H2 | Faza 3 i wyższe | Nie |
| Moc falownika L3 | `sensor.saj_inverter_l3_power` | Sensor | W | HS3, H2 | Faza 3 i wyższe | Nie |
| Moc pozorna falownika L3 | `sensor.saj_inverter_l3_apparent_power` | Sensor | VA | HS3, H2 | Faza 3 i wyższe | Nie |
| Napięcie awaryjne L1 | `sensor.saj_backup_l1_voltage` | Sensor | V | HS3, H2 | - | Nie |
| Prąd awaryjny L1 | `sensor.saj_backup_l1_current` | Sensor | A | HS3, H2 | - | Nie |
| Częstotliwość awaryjna L1 | `sensor.saj_backup_l1_frequency` | Sensor | Hz | HS3, H2 | - | Nie |
| Napięcie stałe awaryjne L1 | `sensor.saj_backup_l1_dc_voltage` | Sensor | mV | HS3, H2 | - | Nie |
| Moc awaryjna L1 | `sensor.saj_backup_l1_power` | Sensor | W | HS3, H2 | - | Nie |
| Moc pozorna awaryjna L1 | `sensor.saj_backup_l1_apparent_power` | Sensor | VA | HS3, H2 | - | Nie |
| Napięcie awaryjne L2 | `sensor.saj_backup_l2_voltage` | Sensor | V | HS3, H2 | Faza 2 i wyższe | Nie |
| Prąd awaryjny L2 | `sensor.saj_backup_l2_current` | Sensor | A | HS3, H2 | Faza 2 i wyższe | Nie |
| Częstotliwość awaryjna L2 | `sensor.saj_backup_l2_frequency` | Sensor | Hz | HS3, H2 | Faza 2 i wyższe | Nie |
| Napięcie stałe awaryjne L2 | `sensor.saj_backup_l2_dc_voltage` | Sensor | mV | HS3, H2 | Faza 2 i wyższe | Nie |
| Moc awaryjna L2 | `sensor.saj_backup_l2_power` | Sensor | W | HS3, H2 | Faza 2 i wyższe | Nie |
| Moc pozorna awaryjna L2 | `sensor.saj_backup_l2_apparent_power` | Sensor | VA | HS3, H2 | Faza 2 i wyższe | Nie |
| Napięcie awaryjne L3 | `sensor.saj_backup_l3_voltage` | Sensor | V | HS3, H2 | Faza 3 i wyższe | Nie |
| Prąd awaryjny L3 | `sensor.saj_backup_l3_current` | Sensor | A | HS3, H2 | Faza 3 i wyższe | Nie |
| Częstotliwość awaryjna L3 | `sensor.saj_backup_l3_frequency` | Sensor | Hz | HS3, H2 | Faza 3 i wyższe | Nie |
| Napięcie stałe awaryjne L3 | `sensor.saj_backup_l3_dc_voltage` | Sensor | mV | HS3, H2 | Faza 3 i wyższe | Nie |
| Moc awaryjna L3 | `sensor.saj_backup_l3_power` | Sensor | W | HS3, H2 | Faza 3 i wyższe | Nie |
| Moc pozorna awaryjna L3 | `sensor.saj_backup_l3_apparent_power` | Sensor | VA | HS3, H2 | Faza 3 i wyższe | Nie |
| Napięcie szyny DC | `sensor.saj_dc_bus_voltage` | Sensor | V | HS3, H2 | - | Nie |
| Napięcie szyny DC (podrzędnej) | `sensor.saj_dc_bus_slave_voltage` | Sensor | V | HS3, H2 | - | Nie |
| Napięcie PV1 | `sensor.saj_pv1_voltage` | Sensor | V | HS3, H2 | - | Tak |
| Prąd PV1 | `sensor.saj_pv1_current` | Sensor | A | HS3, H2 | - | Tak |
| Moc PV1 | `sensor.saj_pv1_power` | Sensor | W | HS3, H2 | - | Tak |
| Napięcie PV2 | `sensor.saj_pv2_voltage` | Sensor | V | HS3, H2 | Ciąg paneli PV 2 i wyższe | Tak |
| Prąd PV2 | `sensor.saj_pv2_current` | Sensor | A | HS3, H2 | Ciąg paneli PV 2 i wyższe | Tak |
| Moc PV2 | `sensor.saj_pv2_power` | Sensor | W | HS3, H2 | Ciąg paneli PV 2 i wyższe | Tak |
| Moc obciążenia domu | `sensor.saj_load_power` | Sensor | W | HS3, H2 | - | Tak |
| Moc słoneczna | `sensor.saj_pv_power` | Sensor | W | HS3, H2 | - | Tak |
| Moc falownika | `sensor.saj_inverter_power` | Sensor | W | HS3, H2 | - | Tak |
| Energia słoneczna dzisiaj | `sensor.saj_pv_energy_today` | Sensor | kWh | HS3, H2 | - | Tak |
| Energia słoneczna w tym miesiącu | `sensor.saj_pv_energy_month` | Sensor | kWh | HS3, H2 | - | Nie |
| Energia słoneczna w tym roku | `sensor.saj_pv_energy_year` | Sensor | kWh | HS3, H2 | - | Nie |
| Energia słoneczna łącznie | `sensor.saj_pv_energy_total` | Sensor | kWh | HS3, H2 | - | Tak |
| Energia obciążenia domu dzisiaj | `sensor.saj_load_energy_today` | Sensor | kWh | HS3, H2 | - | Tak |
| Energia obciążenia domu w tym miesiącu | `sensor.saj_load_energy_month` | Sensor | kWh | HS3, H2 | - | Nie |
| Energia obciążenia domu w tym roku | `sensor.saj_load_energy_year` | Sensor | kWh | HS3, H2 | - | Nie |
| Energia obciążenia domu łącznie | `sensor.saj_load_energy_total` | Sensor | kWh | HS3, H2 | - | Tak |
| Energia odbiorów awaryjnych dzisiaj | `sensor.saj_backup_load_energy_today` | Sensor | kWh | HS3, H2 | - | Tak |
| Energia odbiorów awaryjnych w tym miesiącu | `sensor.saj_backup_load_energy_month` | Sensor | kWh | HS3, H2 | - | Nie |
| Energia odbiorów awaryjnych w tym roku | `sensor.saj_backup_load_energy_year` | Sensor | kWh | HS3, H2 | - | Nie |
| Energia odbiorów awaryjnych łącznie | `sensor.saj_backup_load_energy_total` | Sensor | kWh | HS3, H2 | - | Tak |
| Tryb równoległy | `sensor.saj_parallel_mode` | Sensor | - | HS3, H2 | - | Nie |
| Maszyny równoległe online | `sensor.saj_parallel_online_count` | Sensor | - | HS3, H2 | - | Nie |
| Moc sieci (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_power` | Sensor | W | HS3 | - | Nie |
| Moc sieci L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_l1_power` | Sensor | W | HS3 | - | Nie |
| Napięcie sieci L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_l1_voltage` | Sensor | V | HS3 | - | Nie |
| Prąd sieci L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_l1_current` | Sensor | A | HS3 | - | Nie |
| Częstotliwość sieci L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_l1_frequency` | Sensor | Hz | HS3 | - | Nie |
| Moc sieci L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_l2_power` | Sensor | W | HS3 | Faza 2 i wyższe | Nie |
| Napięcie sieci L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_l2_voltage` | Sensor | V | HS3 | Faza 2 i wyższe | Nie |
| Prąd sieci L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_l2_current` | Sensor | A | HS3 | Faza 2 i wyższe | Nie |
| Częstotliwość sieci L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_l2_frequency` | Sensor | Hz | HS3 | Faza 2 i wyższe | Nie |
| Moc sieci L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_l3_power` | Sensor | W | HS3 | Faza 3 i wyższe | Nie |
| Napięcie sieci L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_l3_voltage` | Sensor | V | HS3 | Faza 3 i wyższe | Nie |
| Prąd sieci L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_l3_current` | Sensor | A | HS3 | Faza 3 i wyższe | Nie |
| Częstotliwość sieci L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_l3_frequency` | Sensor | Hz | HS3 | Faza 3 i wyższe | Nie |
| Moc falownika (średnia 5-minutowa) | `sensor.saj_five_minute_average_inverter_power` | Sensor | W | HS3 | - | Nie |
| Moc falownika L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_inverter_l1_power` | Sensor | W | HS3 | - | Nie |
| Napięcie falownika L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_inverter_l1_voltage` | Sensor | V | HS3 | - | Nie |
| Prąd falownika L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_inverter_l1_current` | Sensor | A | HS3 | - | Nie |
| Częstotliwość falownika L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_inverter_l1_frequency` | Sensor | Hz | HS3 | - | Nie |
| Moc falownika L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_inverter_l2_power` | Sensor | W | HS3 | Faza 2 i wyższe | Nie |
| Napięcie falownika L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_inverter_l2_voltage` | Sensor | V | HS3 | Faza 2 i wyższe | Nie |
| Prąd falownika L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_inverter_l2_current` | Sensor | A | HS3 | Faza 2 i wyższe | Nie |
| Częstotliwość falownika L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_inverter_l2_frequency` | Sensor | Hz | HS3 | Faza 2 i wyższe | Nie |
| Moc falownika L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_inverter_l3_power` | Sensor | W | HS3 | Faza 3 i wyższe | Nie |
| Napięcie falownika L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_inverter_l3_voltage` | Sensor | V | HS3 | Faza 3 i wyższe | Nie |
| Prąd falownika L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_inverter_l3_current` | Sensor | A | HS3 | Faza 3 i wyższe | Nie |
| Częstotliwość falownika L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_inverter_l3_frequency` | Sensor | Hz | HS3 | Faza 3 i wyższe | Nie |
| Moc obciążenia domu (średnia 5-minutowa) | `sensor.saj_five_minute_average_load_power` | Sensor | W | HS3 | - | Nie |
| Moc obciążenia domu L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_load_l1_power` | Sensor | W | HS3 | - | Nie |
| Napięcie obciążenia domu L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_load_l1_voltage` | Sensor | V | HS3 | - | Nie |
| Prąd obciążenia domu L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_load_l1_current` | Sensor | A | HS3 | - | Nie |
| Częstotliwość obciążenia domu L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_load_l1_frequency` | Sensor | Hz | HS3 | - | Nie |
| Moc obciążenia domu L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_load_l2_power` | Sensor | W | HS3 | Faza 2 i wyższe | Nie |
| Napięcie obciążenia domu L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_load_l2_voltage` | Sensor | V | HS3 | Faza 2 i wyższe | Nie |
| Prąd obciążenia domu L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_load_l2_current` | Sensor | A | HS3 | Faza 2 i wyższe | Nie |
| Częstotliwość obciążenia domu L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_load_l2_frequency` | Sensor | Hz | HS3 | Faza 2 i wyższe | Nie |
| Moc obciążenia domu L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_load_l3_power` | Sensor | W | HS3 | Faza 3 i wyższe | Nie |
| Napięcie obciążenia domu L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_load_l3_voltage` | Sensor | V | HS3 | Faza 3 i wyższe | Nie |
| Prąd obciążenia domu L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_load_l3_current` | Sensor | A | HS3 | Faza 3 i wyższe | Nie |
| Częstotliwość obciążenia domu L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_load_l3_frequency` | Sensor | Hz | HS3 | Faza 3 i wyższe | Nie |
| Moc obciążenia sieci (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_load_power` | Sensor | W | HS3 | - | Nie |
| Moc obciążenia sieci L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_load_l1_power` | Sensor | W | HS3 | - | Nie |
| Napięcie obciążenia sieci L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_load_l1_voltage` | Sensor | V | HS3 | - | Nie |
| Prąd obciążenia sieci L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_load_l1_current` | Sensor | A | HS3 | - | Nie |
| Częstotliwość obciążenia sieci L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_load_l1_frequency` | Sensor | Hz | HS3 | - | Nie |
| Moc obciążenia sieci L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_load_l2_power` | Sensor | W | HS3 | Faza 2 i wyższe | Nie |
| Napięcie obciążenia sieci L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_load_l2_voltage` | Sensor | V | HS3 | Faza 2 i wyższe | Nie |
| Prąd obciążenia sieci L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_load_l2_current` | Sensor | A | HS3 | Faza 2 i wyższe | Nie |
| Częstotliwość obciążenia sieci L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_load_l2_frequency` | Sensor | Hz | HS3 | Faza 2 i wyższe | Nie |
| Moc obciążenia sieci L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_load_l3_power` | Sensor | W | HS3 | Faza 3 i wyższe | Nie |
| Napięcie obciążenia sieci L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_load_l3_voltage` | Sensor | V | HS3 | Faza 3 i wyższe | Nie |
| Prąd obciążenia sieci L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_load_l3_current` | Sensor | A | HS3 | Faza 3 i wyższe | Nie |
| Częstotliwość obciążenia sieci L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_grid_load_l3_frequency` | Sensor | Hz | HS3 | Faza 3 i wyższe | Nie |
| Moc awaryjna (średnia 5-minutowa) | `sensor.saj_five_minute_average_backup_power` | Sensor | W | HS3 | - | Nie |
| Moc awaryjna L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_backup_l1_power` | Sensor | W | HS3 | - | Nie |
| Napięcie awaryjne L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_backup_l1_voltage` | Sensor | V | HS3 | - | Nie |
| Prąd awaryjny L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_backup_l1_current` | Sensor | A | HS3 | - | Nie |
| Częstotliwość awaryjna L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_backup_l1_frequency` | Sensor | Hz | HS3 | - | Nie |
| Moc awaryjna L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_backup_l2_power` | Sensor | W | HS3 | Faza 2 i wyższe | Nie |
| Napięcie awaryjne L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_backup_l2_voltage` | Sensor | V | HS3 | Faza 2 i wyższe | Nie |
| Prąd awaryjny L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_backup_l2_current` | Sensor | A | HS3 | Faza 2 i wyższe | Nie |
| Częstotliwość awaryjna L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_backup_l2_frequency` | Sensor | Hz | HS3 | Faza 2 i wyższe | Nie |
| Moc awaryjna L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_backup_l3_power` | Sensor | W | HS3 | Faza 3 i wyższe | Nie |
| Napięcie awaryjne L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_backup_l3_voltage` | Sensor | V | HS3 | Faza 3 i wyższe | Nie |
| Prąd awaryjny L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_backup_l3_current` | Sensor | A | HS3 | Faza 3 i wyższe | Nie |
| Częstotliwość awaryjna L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_backup_l3_frequency` | Sensor | Hz | HS3 | Faza 3 i wyższe | Nie |
| Moc słoneczna (średnia 5-minutowa) | `sensor.saj_five_minute_average_pv_power` | Sensor | W | HS3 | - | Nie |
| Napięcie PV1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_pv1_voltage` | Sensor | V | HS3 | - | Nie |
| Prąd PV1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_pv1_current` | Sensor | A | HS3 | - | Nie |
| Moc PV1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_pv1_power` | Sensor | W | HS3 | - | Nie |
| Napięcie PV2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_pv2_voltage` | Sensor | V | HS3 | Ciąg paneli PV 2 i wyższe | Nie |
| Prąd PV2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_pv2_current` | Sensor | A | HS3 | Ciąg paneli PV 2 i wyższe | Nie |
| Moc PV2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_pv2_power` | Sensor | W | HS3 | Ciąg paneli PV 2 i wyższe | Nie |
| Moc generatora (średnia 5-minutowa) | `sensor.saj_five_minute_average_generator_power` | Sensor | W | HS3 | - | Nie |
| Moc generatora L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_generator_l1_power` | Sensor | W | HS3 | - | Nie |
| Napięcie generatora L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_generator_l1_voltage` | Sensor | V | HS3 | - | Nie |
| Prąd generatora L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_generator_l1_current` | Sensor | A | HS3 | - | Nie |
| Częstotliwość generatora L1 (średnia 5-minutowa) | `sensor.saj_five_minute_average_generator_l1_frequency` | Sensor | Hz | HS3 | - | Nie |
| Moc generatora L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_generator_l2_power` | Sensor | W | HS3 | Faza 2 i wyższe | Nie |
| Napięcie generatora L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_generator_l2_voltage` | Sensor | V | HS3 | Faza 2 i wyższe | Nie |
| Prąd generatora L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_generator_l2_current` | Sensor | A | HS3 | Faza 2 i wyższe | Nie |
| Częstotliwość generatora L2 (średnia 5-minutowa) | `sensor.saj_five_minute_average_generator_l2_frequency` | Sensor | Hz | HS3 | Faza 2 i wyższe | Nie |
| Moc generatora L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_generator_l3_power` | Sensor | W | HS3 | Faza 3 i wyższe | Nie |
| Napięcie generatora L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_generator_l3_voltage` | Sensor | V | HS3 | Faza 3 i wyższe | Nie |
| Prąd generatora L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_generator_l3_current` | Sensor | A | HS3 | Faza 3 i wyższe | Nie |
| Częstotliwość generatora L3 (średnia 5-minutowa) | `sensor.saj_five_minute_average_generator_l3_frequency` | Sensor | Hz | HS3 | Faza 3 i wyższe | Nie |
| Kod produktu | `sensor.saj_product_code` | Sensor | - | HS3, H2 | - | Nie |
| Wersja oprogramowania wyświetlacza | `sensor.saj_display_software_version` | Sensor | - | HS3, H2 | - | Nie |
| Wersja oprogramowania głównego | `sensor.saj_master_software_version` | Sensor | - | HS3, H2 | - | Nie |
| Wersja oprogramowania podrzędnego | `sensor.saj_slave_software_version` | Sensor | - | HS3, H2 | - | Nie |
| Wersja sprzętu wyświetlacza | `sensor.saj_display_hardware_version` | Sensor | - | HS3, H2 | - | Nie |
| Wersja sprzętu sterowania | `sensor.saj_control_hardware_version` | Sensor | - | HS3, H2 | - | Nie |
| Wersja sprzętu części mocy | `sensor.saj_power_hardware_version` | Sensor | - | HS3, H2 | - | Nie |
| Liczba modułów baterii | `sensor.saj_battery_pack_count` | Sensor | - | HS3, H2 | - | Nie |
| Stan licznika A | `sensor.saj_meter_a_status` | Sensor | - | HS3, H2 | - | Nie |
| Stan licznika B | `sensor.saj_meter_b_status` | Sensor | - | HS3, H2 | - | Nie |
| Moc odbiorów awaryjnych | `sensor.saj_backup_load_power` | Sensor | W | HS3, H2 | - | Tak |
| Tryb przepływu zwrotnego | `sensor.saj_reverse_flow_mode` | Sensor | - | H2 | - | Nie |
| Histereza częstotliwości FCAS | `sensor.saj_fcas_frequency_hysteresis` | Sensor | Hz | H2 | - | Nie |
| Rola w systemie równoległym | `sensor.saj_parallel_role` | Sensor | - | H2 | - | Nie |
| Numer w systemie równoległym | `sensor.saj_parallel_number` | Sensor | - | H2 | - | Nie |
| Skonfigurowany tryb równoległy | `sensor.saj_parallel_configured_mode` | Sensor | - | H2 | - | Nie |
| Tryb wejścia baterii | `sensor.saj_battery_input_mode` | Sensor | - | H2 | - | Nie |
| Tryb wejścia PV | `sensor.saj_pv_input_mode` | Sensor | - | H2 | - | Nie |
| Tryb pracy poza siecią | `sensor.saj_off_grid_mode` | Sensor | - | H2 | - | Nie |
| Napięcie wyjścia poza siecią | `sensor.saj_off_grid_output_voltage` | Sensor | V | H2 | - | Nie |
| Częstotliwość wyjścia poza siecią | `sensor.saj_off_grid_output_frequency` | Sensor | Hz | H2 | - | Nie |
| Włączenie silnika | `sensor.saj_motor_enable` | Sensor | - | H2 | - | Nie |
| Model maszyny | `sensor.saj_machine_model` | Sensor | - | H2 | - | Nie |
| Moc znamionowa | `sensor.saj_rated_power` | Sensor | W | H2 | - | Nie |
| Flagi funkcji 1 | `sensor.saj_function_flags_1` | Sensor | - | H2 | - | Nie |
| Flagi funkcji 2 | `sensor.saj_function_flags_2` | Sensor | - | H2 | - | Nie |
| Maksymalna składowa prądu stałego | `sensor.saj_max_dc_current_component` | Sensor | mA | H2 | - | Nie |
| Maksymalna składowa napięcia stałego | `sensor.saj_max_dc_voltage_component` | Sensor | V | H2 | - | Nie |
| Limit rezystancji izolacji | `sensor.saj_insulation_resistance_limit` | Sensor | kΩ | H2 | - | Nie |
| Maksymalny prąd upływu | `sensor.saj_max_leakage_current` | Sensor | mA | H2 | - | Nie |
| Zatrzymanie falownika | `sensor.saj_inverter_stop` | Sensor | - | H2 | - | Nie |
| Napięcie startu PV | `sensor.saj_pv_start_voltage` | Sensor | V | H2 | - | Nie |
| Napięcie wyłączenia PV | `sensor.saj_pv_shutdown_voltage` | Sensor | V | H2 | - | Nie |
| Górne napięcie MPPT | `sensor.saj_mppt_voltage_high` | Sensor | V | H2 | - | Nie |
| Dolne napięcie MPPT | `sensor.saj_mppt_voltage_low` | Sensor | V | H2 | - | Nie |
| Czas skanowania MPPT | `sensor.saj_mppt_scan_time` | Sensor | min | H2 | - | Nie |
| Liczba błędów falownika | `sensor.saj_inverter_error_count` | Sensor | - | H2 | - | Nie |
| Rezystancja izolacji PV3 | `sensor.saj_pv3_insulation_resistance` | Sensor | kΩ | H2 | Ciąg paneli PV 3 i wyższe | Nie |
| Rezystancja izolacji PV4 | `sensor.saj_pv4_insulation_resistance` | Sensor | kΩ | H2 | Ciąg paneli PV 4 i wyższe | Nie |
| Stan sprzętowy DRM | `sensor.saj_drm_hardware_status` | Sensor | - | H2 | - | Nie |
| Stan programowy DRM | `sensor.saj_drm_software_status` | Sensor | - | H2 | - | Nie |
| Numer kolejny zapisu usterki | `sensor.saj_fault_record_sequence` | Sensor | - | H2 | - | Nie |
| Tryb aplikacji (obowiązujący) | `sensor.saj_application_mode_active` | Sensor | - | H2 | - | Nie |
| Napięcie PV3 | `sensor.saj_pv3_voltage` | Sensor | V | H2 | Ciąg paneli PV 3 i wyższe | Tak |
| Prąd PV3 | `sensor.saj_pv3_current` | Sensor | A | H2 | Ciąg paneli PV 3 i wyższe | Tak |
| Moc PV3 | `sensor.saj_pv3_power` | Sensor | W | H2 | Ciąg paneli PV 3 i wyższe | Tak |
| Napięcie PV4 | `sensor.saj_pv4_voltage` | Sensor | V | H2 | Ciąg paneli PV 4 i wyższe | Tak |
| Prąd PV4 | `sensor.saj_pv4_current` | Sensor | A | H2 | Ciąg paneli PV 4 i wyższe | Tak |
| Moc PV4 | `sensor.saj_pv4_power` | Sensor | W | H2 | Ciąg paneli PV 4 i wyższe | Tak |
| Moc sieci z przekładnika CT | `sensor.saj_ct_grid_power` | Sensor | W | H2 | - | Nie |
| Moc pozorna sieci z przekładnika CT | `sensor.saj_ct_grid_apparent_power` | Sensor | VA | H2 | - | Nie |
| Moc słoneczna z przekładnika CT | `sensor.saj_ct_pv_power` | Sensor | W | H2 | - | Nie |
| Moc pozorna słoneczna z przekładnika CT | `sensor.saj_ct_pv_apparent_power` | Sensor | VA | H2 | - | Nie |
| Moc pozorna falownika | `sensor.saj_inverter_apparent_power` | Sensor | VA | H2 | - | Nie |
| Moc pozorna odbiorów awaryjnych | `sensor.saj_backup_load_apparent_power` | Sensor | VA | H2 | - | Nie |
| Czas produkcji energii słonecznej dzisiaj | `sensor.saj_pv_generation_time_today` | Sensor | h | H2 | - | Nie |
| Czas produkcji energii słonecznej łącznie | `sensor.saj_pv_generation_time_total` | Sensor | h | H2 | - | Nie |
| Energia falownika dzisiaj | `sensor.saj_inverter_energy_today` | Sensor | kWh | H2 | - | Nie |
| Energia falownika w tym miesiącu | `sensor.saj_inverter_energy_month` | Sensor | kWh | H2 | - | Nie |
| Energia falownika w tym roku | `sensor.saj_inverter_energy_year` | Sensor | kWh | H2 | - | Nie |
| Energia falownika łącznie | `sensor.saj_inverter_energy_total` | Sensor | kWh | H2 | - | Nie |
| Energia PV2 dzisiaj | `sensor.saj_pv2_energy_today` | Sensor | kWh | H2 | Ciąg paneli PV 2 i wyższe | Nie |
| Energia PV2 w tym miesiącu | `sensor.saj_pv2_energy_month` | Sensor | kWh | H2 | Ciąg paneli PV 2 i wyższe | Nie |
| Energia PV2 w tym roku | `sensor.saj_pv2_energy_year` | Sensor | kWh | H2 | Ciąg paneli PV 2 i wyższe | Nie |
| Energia PV2 łącznie | `sensor.saj_pv2_energy_total` | Sensor | kWh | H2 | Ciąg paneli PV 2 i wyższe | Nie |
| Energia PV3 dzisiaj | `sensor.saj_pv3_energy_today` | Sensor | kWh | H2 | Ciąg paneli PV 3 i wyższe | Nie |
| Energia PV3 w tym miesiącu | `sensor.saj_pv3_energy_month` | Sensor | kWh | H2 | Ciąg paneli PV 3 i wyższe | Nie |
| Energia PV3 w tym roku | `sensor.saj_pv3_energy_year` | Sensor | kWh | H2 | Ciąg paneli PV 3 i wyższe | Nie |
| Energia PV3 łącznie | `sensor.saj_pv3_energy_total` | Sensor | kWh | H2 | Ciąg paneli PV 3 i wyższe | Nie |
| Wersja protokołu tożsamości | `sensor.saj_identity_protocol_version` | Sensor | - | H2 | - | Nie |
