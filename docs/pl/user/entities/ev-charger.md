[en](../../../en-gb/user/entities/ev-charger.md) | [de](../../../de/user/entities/ev-charger.md) | [nl](../../../nl/user/entities/ev-charger.md) | [fr](../../../fr/user/entities/ev-charger.md) | [zh](../../../zh-hans/user/entities/ev-charger.md) | [es](../../../es/user/entities/ev-charger.md) | [it](../../../it/user/entities/ev-charger.md) | pl | [sv](../../../sv/user/entities/ev-charger.md)

# Ładowarka EV

Ładowarka EV i jej elementy sterowania ładowaniem.

Lista funkcji integracji wyjaśnia encje obszaru Ładowarka EV w [Wyposażenie opcjonalne](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

Liczba encji: 87. Wygenerowano poleceniem `make docs`. Nie edytuj ręcznie.

Prefiks ustawiony w Skonfiguruj trafia po `saj_` w ID każdej encji: Ładowarka EV, na przykład `sensor.saj_house_ev_serial_number` z prefiksem `house`.

| Nazwa | ID encji | Typ | Jednostka | Modele | Wyposażenie i liczba | Włączona domyślnie |
| --- | --- | --- | --- | --- | --- | --- |
| Numer seryjny ładowarki EV | `sensor.saj_ev_serial_number` | Sensor | - | HS3 | Ładowarka EV | Nie |
| Model ładowarki EV | `sensor.saj_ev_model` | Sensor | - | HS3 | Ładowarka EV | Nie |
| Wersja oprogramowania ładowarki EV | `sensor.saj_ev_software_version` | Sensor | - | HS3 | Ładowarka EV | Nie |
| Wersja sprzętu ładowarki EV | `sensor.saj_ev_hardware_version` | Sensor | - | HS3 | Ładowarka EV | Nie |
| Liczba faz ładowarki EV | `sensor.saj_ev_phase_count` | Sensor | - | HS3 | Ładowarka EV | Nie |
| Minimalna moc ładowarki EV | `sensor.saj_ev_minimum_power` | Sensor | W | HS3 | Ładowarka EV | Nie |
| Maksymalna moc ładowarki EV | `sensor.saj_ev_maximum_power` | Sensor | W | HS3 | Ładowarka EV | Nie |
| Tryb pracy ładowarki EV | `sensor.saj_ev_work_mode` | Sensor | - | HS3 | Ładowarka EV | Nie |
| Stan ładowarki EV | `sensor.saj_ev_status` | Sensor | - | HS3 | Ładowarka EV | Tak |
| Napięcie L1 ładowarki EV | `sensor.saj_ev_l1_voltage` | Sensor | V | HS3 | Ładowarka EV | Nie |
| Prąd L1 ładowarki EV | `sensor.saj_ev_l1_current` | Sensor | A | HS3 | Ładowarka EV | Nie |
| Napięcie L2 ładowarki EV | `sensor.saj_ev_l2_voltage` | Sensor | V | HS3 | Ładowarka EV | Nie |
| Prąd L2 ładowarki EV | `sensor.saj_ev_l2_current` | Sensor | A | HS3 | Ładowarka EV | Nie |
| Napięcie L3 ładowarki EV | `sensor.saj_ev_l3_voltage` | Sensor | V | HS3 | Ładowarka EV | Nie |
| Prąd L3 ładowarki EV | `sensor.saj_ev_l3_current` | Sensor | A | HS3 | Ładowarka EV | Nie |
| Moc ładowarki EV | `sensor.saj_ev_power` | Sensor | W | HS3 | Ładowarka EV | Tak |
| Czas ładowania EV | `sensor.saj_ev_charge_duration` | Sensor | min | HS3 | Ładowarka EV | Nie |
| Energia sesji ładowarki EV | `sensor.saj_ev_session_energy` | Sensor | kWh | HS3 | Ładowarka EV | Tak |
| Energia całkowita ładowarki EV | `sensor.saj_ev_total_energy` | Sensor | kWh | HS3 | Ładowarka EV | Tak |
| Napięcie sygnału sterującego (control pilot) ładowarki EV | `sensor.saj_ev_control_pilot_voltage` | Sensor | V | HS3 | Ładowarka EV | Nie |
| Współczynnik wypełnienia ładowarki EV | `sensor.saj_ev_duty_cycle` | Sensor | % | HS3 | Ładowarka EV | Nie |
| Zdalne sterowanie ładowarką EV | `sensor.saj_ev_remote_control` | Sensor | - | HS3 | Ładowarka EV | Nie |
| Wartość zadana prądu ładowarki EV | `sensor.saj_ev_current_setpoint` | Sensor | A | HS3 | Ładowarka EV | Nie |
| Początek sesji ładowarki EV | `sensor.saj_ev_session_start` | Sensor | - | HS3 | Ładowarka EV | Nie |
| Koniec sesji ładowarki EV | `sensor.saj_ev_session_end` | Sensor | - | HS3 | Ładowarka EV | Nie |
| Wersja protokołu ustawień ładowarki EV | `sensor.saj_ev_settings_protocol_version` | Sensor | - | HS3 | Ładowarka EV | Nie |
| Adres ładowarki EV | `sensor.saj_ev_address` | Sensor | - | HS3 | Ładowarka EV | Nie |
| Szybkość transmisji ładowarki EV | `sensor.saj_ev_baud_rate` | Sensor | - | HS3 | Ładowarka EV | Nie |
| Liczba ładowarek EV | `sensor.saj_ev_charger_count` | Sensor | - | HS3 | Ładowarka EV | Nie |
| Limit czasu komunikacji ładowarki EV | `sensor.saj_ev_communication_timeout` | Sensor | s | HS3 | Ładowarka EV | Nie |
| Tryb portu ładowarki EV | `sensor.saj_ev_port_mode` | Sensor | - | HS3 | Ładowarka EV | Nie |
| Adres portu ładowarki EV | `sensor.saj_ev_port_address` | Sensor | - | HS3 | Ładowarka EV | Nie |
| Tryb ładowarki EV | `select.saj_ev_mode` | Selektor | - | HS3 | Ładowarka EV | Tak |
| Moc ładowania EV | `number.saj_ev_charge_power` | Liczba | W | HS3 | Ładowarka EV | Nie |
| Czas rozpoczęcia przedziału 1 ładowarki EV | `time.saj_ev_slot_1_start` | Czas | - | HS3 | Ładowarka EV | Nie |
| Czas zakończenia przedziału 1 ładowarki EV | `time.saj_ev_slot_1_end` | Czas | - | HS3 | Ładowarka EV | Nie |
| Tryb przedziału 1 ładowarki EV | `select.saj_ev_slot_1_mode` | Selektor | - | HS3 | Ładowarka EV | Nie |
| Ładowanie z sieci w przedziale 1 ładowarki EV | `switch.saj_ev_slot_1_grid_charging` | Przełącznik | - | HS3 | Ładowarka EV | Nie |
| Rozładowanie baterii w przedziale 1 ładowarki EV | `switch.saj_ev_slot_1_battery_discharge` | Przełącznik | - | HS3 | Ładowarka EV | Nie |
| Dni tygodnia przedziału 1 ładowarki EV | `number.saj_ev_slot_1_days` | Liczba | - | HS3 | Ładowarka EV | Nie |
| Moc przedziału 1 ładowarki EV | `number.saj_ev_slot_1_power` | Liczba | W | HS3 | Ładowarka EV | Nie |
| Czas rozpoczęcia przedziału 2 ładowarki EV | `time.saj_ev_slot_2_start` | Czas | - | HS3 | Ładowarka EV | Nie |
| Czas zakończenia przedziału 2 ładowarki EV | `time.saj_ev_slot_2_end` | Czas | - | HS3 | Ładowarka EV | Nie |
| Tryb przedziału 2 ładowarki EV | `select.saj_ev_slot_2_mode` | Selektor | - | HS3 | Ładowarka EV | Nie |
| Ładowanie z sieci w przedziale 2 ładowarki EV | `switch.saj_ev_slot_2_grid_charging` | Przełącznik | - | HS3 | Ładowarka EV | Nie |
| Rozładowanie baterii w przedziale 2 ładowarki EV | `switch.saj_ev_slot_2_battery_discharge` | Przełącznik | - | HS3 | Ładowarka EV | Nie |
| Dni tygodnia przedziału 2 ładowarki EV | `number.saj_ev_slot_2_days` | Liczba | - | HS3 | Ładowarka EV | Nie |
| Moc przedziału 2 ładowarki EV | `number.saj_ev_slot_2_power` | Liczba | W | HS3 | Ładowarka EV | Nie |
| Czas rozpoczęcia przedziału 3 ładowarki EV | `time.saj_ev_slot_3_start` | Czas | - | HS3 | Ładowarka EV | Nie |
| Czas zakończenia przedziału 3 ładowarki EV | `time.saj_ev_slot_3_end` | Czas | - | HS3 | Ładowarka EV | Nie |
| Tryb przedziału 3 ładowarki EV | `select.saj_ev_slot_3_mode` | Selektor | - | HS3 | Ładowarka EV | Nie |
| Ładowanie z sieci w przedziale 3 ładowarki EV | `switch.saj_ev_slot_3_grid_charging` | Przełącznik | - | HS3 | Ładowarka EV | Nie |
| Rozładowanie baterii w przedziale 3 ładowarki EV | `switch.saj_ev_slot_3_battery_discharge` | Przełącznik | - | HS3 | Ładowarka EV | Nie |
| Dni tygodnia przedziału 3 ładowarki EV | `number.saj_ev_slot_3_days` | Liczba | - | HS3 | Ładowarka EV | Nie |
| Moc przedziału 3 ładowarki EV | `number.saj_ev_slot_3_power` | Liczba | W | HS3 | Ładowarka EV | Nie |
| Czas rozpoczęcia przedziału 4 ładowarki EV | `time.saj_ev_slot_4_start` | Czas | - | HS3 | Ładowarka EV | Nie |
| Czas zakończenia przedziału 4 ładowarki EV | `time.saj_ev_slot_4_end` | Czas | - | HS3 | Ładowarka EV | Nie |
| Tryb przedziału 4 ładowarki EV | `select.saj_ev_slot_4_mode` | Selektor | - | HS3 | Ładowarka EV | Nie |
| Ładowanie z sieci w przedziale 4 ładowarki EV | `switch.saj_ev_slot_4_grid_charging` | Przełącznik | - | HS3 | Ładowarka EV | Nie |
| Rozładowanie baterii w przedziale 4 ładowarki EV | `switch.saj_ev_slot_4_battery_discharge` | Przełącznik | - | HS3 | Ładowarka EV | Nie |
| Dni tygodnia przedziału 4 ładowarki EV | `number.saj_ev_slot_4_days` | Liczba | - | HS3 | Ładowarka EV | Nie |
| Moc przedziału 4 ładowarki EV | `number.saj_ev_slot_4_power` | Liczba | W | HS3 | Ładowarka EV | Nie |
| Czas rozpoczęcia przedziału 5 ładowarki EV | `time.saj_ev_slot_5_start` | Czas | - | HS3 | Ładowarka EV | Nie |
| Czas zakończenia przedziału 5 ładowarki EV | `time.saj_ev_slot_5_end` | Czas | - | HS3 | Ładowarka EV | Nie |
| Tryb przedziału 5 ładowarki EV | `select.saj_ev_slot_5_mode` | Selektor | - | HS3 | Ładowarka EV | Nie |
| Ładowanie z sieci w przedziale 5 ładowarki EV | `switch.saj_ev_slot_5_grid_charging` | Przełącznik | - | HS3 | Ładowarka EV | Nie |
| Rozładowanie baterii w przedziale 5 ładowarki EV | `switch.saj_ev_slot_5_battery_discharge` | Przełącznik | - | HS3 | Ładowarka EV | Nie |
| Dni tygodnia przedziału 5 ładowarki EV | `number.saj_ev_slot_5_days` | Liczba | - | HS3 | Ładowarka EV | Nie |
| Moc przedziału 5 ładowarki EV | `number.saj_ev_slot_5_power` | Liczba | W | HS3 | Ładowarka EV | Nie |
| Czas rozpoczęcia przedziału 6 ładowarki EV | `time.saj_ev_slot_6_start` | Czas | - | HS3 | Ładowarka EV | Nie |
| Czas zakończenia przedziału 6 ładowarki EV | `time.saj_ev_slot_6_end` | Czas | - | HS3 | Ładowarka EV | Nie |
| Tryb przedziału 6 ładowarki EV | `select.saj_ev_slot_6_mode` | Selektor | - | HS3 | Ładowarka EV | Nie |
| Ładowanie z sieci w przedziale 6 ładowarki EV | `switch.saj_ev_slot_6_grid_charging` | Przełącznik | - | HS3 | Ładowarka EV | Nie |
| Rozładowanie baterii w przedziale 6 ładowarki EV | `switch.saj_ev_slot_6_battery_discharge` | Przełącznik | - | HS3 | Ładowarka EV | Nie |
| Dni tygodnia przedziału 6 ładowarki EV | `number.saj_ev_slot_6_days` | Liczba | - | HS3 | Ładowarka EV | Nie |
| Moc przedziału 6 ładowarki EV | `number.saj_ev_slot_6_power` | Liczba | W | HS3 | Ładowarka EV | Nie |
| Czas rozpoczęcia przedziału 7 ładowarki EV | `time.saj_ev_slot_7_start` | Czas | - | HS3 | Ładowarka EV | Nie |
| Czas zakończenia przedziału 7 ładowarki EV | `time.saj_ev_slot_7_end` | Czas | - | HS3 | Ładowarka EV | Nie |
| Tryb przedziału 7 ładowarki EV | `select.saj_ev_slot_7_mode` | Selektor | - | HS3 | Ładowarka EV | Nie |
| Ładowanie z sieci w przedziale 7 ładowarki EV | `switch.saj_ev_slot_7_grid_charging` | Przełącznik | - | HS3 | Ładowarka EV | Nie |
| Rozładowanie baterii w przedziale 7 ładowarki EV | `switch.saj_ev_slot_7_battery_discharge` | Przełącznik | - | HS3 | Ładowarka EV | Nie |
| Dni tygodnia przedziału 7 ładowarki EV | `number.saj_ev_slot_7_days` | Liczba | - | HS3 | Ładowarka EV | Nie |
| Moc przedziału 7 ładowarki EV | `number.saj_ev_slot_7_power` | Liczba | W | HS3 | Ładowarka EV | Nie |
| Ładowanie ładowarki EV minimalnym prądem | `switch.saj_ev_minimum_current_charging` | Przełącznik | - | HS3 | Ładowarka EV | Nie |
| Ładowanie EMS ładowarki EV | `switch.saj_ev_ems_charging` | Przełącznik | - | HS3 | Ładowarka EV | Nie |
| Tryb fazowy EMS ładowarki EV | `select.saj_ev_ems_phase_mode` | Selektor | - | HS3 | Ładowarka EV | Nie |
| Prąd ładowania EMS ładowarki EV | `number.saj_ev_ems_charge_current` | Liczba | A | HS3 | Ładowarka EV | Nie |
