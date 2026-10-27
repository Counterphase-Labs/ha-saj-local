[en](../../../en-gb/user/entities/faults.md) | [de](../../../de/user/entities/faults.md) | [nl](../../../nl/user/entities/faults.md) | [fr](../../../fr/user/entities/faults.md) | [zh](../../../zh-hans/user/entities/faults.md) | [es](../../../es/user/entities/faults.md) | [it](../../../it/user/entities/faults.md) | pl | [sv](../../../sv/user/entities/faults.md)

# Usterki

Usterki zgłaszane przez falownik, baterię i ładowarkę EV.

Lista funkcji integracji wyjaśnia encje obszaru Usterki w [Usterki urządzeń i naprawy](../../../../custom_components/saj_local/docs/features.md#device-faults-and-repairs).

Liczba encji: 139. Wygenerowano poleceniem `make docs`. Nie edytuj ręcznie.

Prefiks ustawiony w Skonfiguruj trafia po `saj_` w ID każdej encji: Usterki, na przykład `binary_sensor.saj_house_battery_pack1_fault` z prefiksem `house`.

| Nazwa | ID encji | Typ | Jednostka | Modele | Wyposażenie i liczba | Włączona domyślnie |
| --- | --- | --- | --- | --- | --- | --- |
| Usterka modułu baterii 1 | `binary_sensor.saj_battery_pack1_fault` | Sensor binarny | - | HS3, H2 | Bateria | Tak |
| Ostrzeżenie modułu baterii 1 | `binary_sensor.saj_battery_pack1_warning` | Sensor binarny | - | HS3, H2 | Bateria | Tak |
| Usterka baterii | `binary_sensor.saj_battery_fault` | Sensor binarny | - | HS3, H2 | Bateria | Tak |
| Niezgodny producent BMS baterii | `binary_sensor.saj_battery_fault_bms_incompatible` | Sensor binarny | - | HS3 | Bateria | Tak |
| Wyłącznik obwodu baterii otwarty | `binary_sensor.saj_battery_fault_breaker_open` | Sensor binarny | - | HS3 | Bateria | Tak |
| Niezgodność ogniw baterii | `binary_sensor.saj_battery_fault_cell_incompatible` | Sensor binarny | - | HS3 | Bateria | Tak |
| Zbyt wysoka temperatura ogniwa baterii | `binary_sensor.saj_battery_fault_cell_over_temperature` | Sensor binarny | - | HS3 | Bateria | Tak |
| Zbyt wysokie napięcie ogniwa baterii | `binary_sensor.saj_battery_fault_cell_overvoltage` | Sensor binarny | - | HS3 | Bateria | Tak |
| Niezgodny producent ogniw baterii | `binary_sensor.saj_battery_fault_cell_supplier_incompatible` | Sensor binarny | - | HS3 | Bateria | Tak |
| Zbyt duża różnica temperatur ogniw baterii | `binary_sensor.saj_battery_fault_cell_temperature_difference` | Sensor binarny | - | HS3 | Bateria | Tak |
| Zbyt niskie napięcie ogniwa baterii | `binary_sensor.saj_battery_fault_cell_undervoltage` | Sensor binarny | - | HS3 | Bateria | Tak |
| Zbyt duża różnica napięć ogniw baterii, poziom 1 | `binary_sensor.saj_battery_fault_cell_voltage_difference_1` | Sensor binarny | - | HS3 | Bateria | Tak |
| Zbyt duża różnica napięć ogniw baterii, poziom 2 | `binary_sensor.saj_battery_fault_cell_voltage_difference_2` | Sensor binarny | - | HS3 | Bateria | Tak |
| Bateria zbyt zimna do ładowania | `binary_sensor.saj_battery_fault_charge_cold` | Sensor binarny | - | HS3 | Bateria | Tak |
| Bateria zbyt gorąca do ładowania | `binary_sensor.saj_battery_fault_charge_hot` | Sensor binarny | - | HS3 | Bateria | Tak |
| Przetężenie ładowania baterii | `binary_sensor.saj_battery_fault_charge_overcurrent` | Sensor binarny | - | HS3 | Bateria | Tak |
| Przepięcie portu ładowania baterii | `binary_sensor.saj_battery_fault_charging_port_overvoltage` | Sensor binarny | - | HS3 | Bateria | Tak |
| Bateria zbyt zimna do rozładowania | `binary_sensor.saj_battery_fault_discharge_cold` | Sensor binarny | - | HS3 | Bateria | Tak |
| Bateria zbyt gorąca do rozładowania | `binary_sensor.saj_battery_fault_discharge_hot` | Sensor binarny | - | HS3 | Bateria | Tak |
| Przetężenie rozładowania baterii | `binary_sensor.saj_battery_fault_discharge_overcurrent` | Sensor binarny | - | HS3 | Bateria | Tak |
| Usterka bezpiecznika baterii | `binary_sensor.saj_battery_fault_fuse` | Sensor binarny | - | HS3 | Bateria | Tak |
| Usterka sprzętowa BMS baterii | `binary_sensor.saj_battery_fault_hardware` | Sensor binarny | - | HS3 | Bateria | Tak |
| Usterka izolacji BMS baterii | `binary_sensor.saj_battery_fault_insulation` | Sensor binarny | - | HS3 | Bateria | Tak |
| Utracona komunikacja wewnętrzna BMS baterii | `binary_sensor.saj_battery_fault_internal_communication` | Sensor binarny | - | HS3 | Bateria | Tak |
| Usterka adresowania modułów baterii | `binary_sensor.saj_battery_fault_pack_sequence` | Sensor binarny | - | HS3 | Bateria | Tak |
| Usterka wstępnego ładowania baterii | `binary_sensor.saj_battery_fault_precharge` | Sensor binarny | - | HS3 | Bateria | Tak |
| Usterka przekaźnika BMS baterii | `binary_sensor.saj_battery_fault_relay` | Sensor binarny | - | HS3 | Bateria | Tak |
| Zwarcie baterii | `binary_sensor.saj_battery_fault_short_circuit` | Sensor binarny | - | HS3 | Bateria | Tak |
| System baterii zablokowany | `binary_sensor.saj_battery_fault_system_locked` | Sensor binarny | - | HS3 | Bateria | Tak |
| Zbyt wysokie napięcie całkowite baterii | `binary_sensor.saj_battery_fault_total_overvoltage` | Sensor binarny | - | HS3 | Bateria | Tak |
| Zbyt niskie napięcie całkowite baterii | `binary_sensor.saj_battery_fault_total_undervoltage` | Sensor binarny | - | HS3 | Bateria | Tak |
| Niepowodzenie dopasowania napięcia całkowitego baterii | `binary_sensor.saj_battery_fault_total_voltage_matching` | Sensor binarny | - | HS3 | Bateria | Tak |
| Nierozpoznana usterka baterii | `binary_sensor.saj_battery_fault_unrecognised` | Sensor binarny | - | HS3, H2 | Bateria | Tak |
| Niezgodność poziomu napięcia baterii | `binary_sensor.saj_battery_fault_voltage_level_mismatch` | Sensor binarny | - | HS3 | Bateria | Tak |
| Usterka ładowarki EV | `binary_sensor.saj_ev_fault` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Przetężenie AC ładowarki EV | `binary_sensor.saj_ev_fault_ac_overcurrent` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Zbyt wysoka częstotliwość AC ładowarki EV | `binary_sensor.saj_ev_fault_ac_overfrequency` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Przepięcie AC ładowarki EV | `binary_sensor.saj_ev_fault_ac_overvoltage` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Prąd różnicowy AC ładowarki EV | `binary_sensor.saj_ev_fault_ac_residual_current` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Zbyt niska częstotliwość AC ładowarki EV | `binary_sensor.saj_ev_fault_ac_underfrequency` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Zbyt niskie napięcie AC ładowarki EV | `binary_sensor.saj_ev_fault_ac_undervoltage` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Usterka Bluetooth ładowarki EV | `binary_sensor.saj_ev_fault_bluetooth` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Usterka prądu złącza ładowarki EV | `binary_sensor.saj_ev_fault_connector_current` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Usterka blokady złącza ładowarki EV | `binary_sensor.saj_ev_fault_connector_lock` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Usterka sygnału sterującego (control pilot) ładowarki EV (poniżej 2 V) | `binary_sensor.saj_ev_fault_control_pilot` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Usterka prądu różnicowego DC A ładowarki EV | `binary_sensor.saj_ev_fault_dc_residual_current_a` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Usterka prądu różnicowego DC B ładowarki EV | `binary_sensor.saj_ev_fault_dc_residual_current_b` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Usterka prądu różnicowego DC C ładowarki EV | `binary_sensor.saj_ev_fault_dc_residual_current_c` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Zatrzymanie awaryjne ładowarki EV | `binary_sensor.saj_ev_fault_emergency_stop` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Usterka uziemienia ładowarki EV | `binary_sensor.saj_ev_fault_grounding` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Zbyt wysoka temperatura zacisku wejściowego ładowarki EV | `binary_sensor.saj_ev_fault_input_terminal_over_temperature` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Usterka licznika ładowarki EV | `binary_sensor.saj_ev_fault_meter` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Przeciążenie ładowarki EV | `binary_sensor.saj_ev_fault_overload` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Usterka kolejności faz ładowarki EV | `binary_sensor.saj_ev_fault_phase_sequence` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Usterka obwodu RCD ładowarki EV | `binary_sensor.saj_ev_fault_rcd_circuit` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Usterka przekaźnika ładowarki EV | `binary_sensor.saj_ev_fault_relay` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Zbyt wysoka temperatura przekaźnika ładowarki EV | `binary_sensor.saj_ev_fault_relay_over_temperature` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Przekroczony czas komunikacji RS485 ładowarki EV | `binary_sensor.saj_ev_fault_rs485_timeout` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Usterka zasilania elektrycznego ładowarki EV | `binary_sensor.saj_ev_fault_supply` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Zbyt niska temperatura ładowarki EV | `binary_sensor.saj_ev_fault_under_temperature` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Nierozpoznana usterka ładowarki EV | `binary_sensor.saj_ev_fault_unrecognised` | Sensor binarny | - | HS3 | Ładowarka EV | Tak |
| Usterka falownika | `binary_sensor.saj_inverter_fault` | Sensor binarny | - | HS3, H2 | - | Tak |
| Utracona komunikacja z płytką wykrywania łuku | `binary_sensor.saj_inverter_fault_afci_communication` | Sensor binarny | - | HS3 | - | Tak |
| Usterka łuku elektrycznego | `binary_sensor.saj_inverter_fault_arc` | Sensor binarny | - | HS3, H2 | - | Tak |
| Usterka urządzenia wykrywania łuku | `binary_sensor.saj_inverter_fault_arc_device` | Sensor binarny | - | HS3 | - | Tak |
| Autoryzacja wygasła | `binary_sensor.saj_inverter_fault_authorisation_expired` | Sensor binarny | - | HS3, H2 | - | Tak |
| Zbyt wysokie napięcie ładowania baterii | `binary_sensor.saj_inverter_fault_battery_charge_overvoltage` | Sensor binarny | - | HS3, H2 | - | Tak |
| Zbyt niskie napięcie rozładowania baterii | `binary_sensor.saj_inverter_fault_battery_discharge_undervoltage` | Sensor binarny | - | HS3, H2 | - | Tak |
| Rozwarty obwód baterii | `binary_sensor.saj_inverter_fault_battery_open_circuit` | Sensor binarny | - | HS3, H2 | - | Tak |
| Przetężenie portu baterii | `binary_sensor.saj_inverter_fault_battery_overcurrent` | Sensor binarny | - | HS3, H2 | - | Tak |
| Przeciążenie portu baterii | `binary_sensor.saj_inverter_fault_battery_overload` | Sensor binarny | - | HS3, H2 | - | Tak |
| Przepięcie portu baterii | `binary_sensor.saj_inverter_fault_battery_overvoltage` | Sensor binarny | - | HS3, H2 | - | Tak |
| Przekroczony czas miękkiego startu baterii | `binary_sensor.saj_inverter_fault_battery_soft_start` | Sensor binarny | - | HS3, H2 | - | Tak |
| Utracona komunikacja z BMS | `binary_sensor.saj_inverter_fault_bms_communication` | Sensor binarny | - | HS3, H2 | - | Tak |
| Usterka urządzenia BMS | `binary_sensor.saj_inverter_fault_bms_device` | Sensor binarny | - | HS3, H2 | - | Tak |
| Sprzętowe przepięcie szyny DC | `binary_sensor.saj_inverter_fault_bus_hardware_overvoltage` | Sensor binarny | - | HS3, H2 | - | Tak |
| Asymetria napięcia szyny DC | `binary_sensor.saj_inverter_fault_bus_imbalance` | Sensor binarny | - | HS3, H2 | - | Tak |
| Usterka pamięci kontrolera | `binary_sensor.saj_inverter_fault_controller_memory` | Sensor binarny | - | HS3, H2 | - | Tak |
| Usterka przekładnika CT | `binary_sensor.saj_inverter_fault_ct_device` | Sensor binarny | - | HS3 | - | Tak |
| Usterka czujnika prądu | `binary_sensor.saj_inverter_fault_current_sensor` | Sensor binarny | - | HS3, H2 | - | Tak |
| Usterka czujnika składowej stałej | `binary_sensor.saj_inverter_fault_dc_injection_device` | Sensor binarny | - | HS3, H2 | - | Tak |
| Utracona komunikacja z przetwornicą DC-DC | `binary_sensor.saj_inverter_fault_dcdc_communication` | Sensor binarny | - | HS3 | - | Tak |
| Usterka przetwornicy DC-DC | `binary_sensor.saj_inverter_fault_dcdc_device` | Sensor binarny | - | HS3 | - | Tak |
| Usterka zegara płytki wyświetlacza | `binary_sensor.saj_inverter_fault_display_clock` | Sensor binarny | - | HS3, H2 | - | Tak |
| Utracona komunikacja z płytką wyświetlacza | `binary_sensor.saj_inverter_fault_display_communication` | Sensor binarny | - | HS3, H2 | - | Tak |
| Usterka pamięci płytki wyświetlacza | `binary_sensor.saj_inverter_fault_display_memory` | Sensor binarny | - | HS3, H2 | - | Tak |
| Usterka DRM0 | `binary_sensor.saj_inverter_fault_drm0` | Sensor binarny | - | HS3, H2 | - | Tak |
| Utracona komunikacja z ładowarką EV | `binary_sensor.saj_inverter_fault_ev_charger_communication` | Sensor binarny | - | HS3 | - | Tak |
| Usterka wentylatora 1 | `binary_sensor.saj_inverter_fault_fan_1` | Sensor binarny | - | HS3, H2 | - | Tak |
| Usterka wentylatora 2 | `binary_sensor.saj_inverter_fault_fan_2` | Sensor binarny | - | HS3, H2 | - | Tak |
| Usterka wentylatora 3 | `binary_sensor.saj_inverter_fault_fan_3` | Sensor binarny | - | HS3, H2 | - | Tak |
| Usterka wentylatora 4 | `binary_sensor.saj_inverter_fault_fan_4` | Sensor binarny | - | HS3, H2 | - | Tak |
| Przepięcie średniej 10-minutowej sieci | `binary_sensor.saj_inverter_fault_grid_average_overvoltage` | Sensor binarny | - | HS3, H2 | - | Tak |
| Utrata sieci | `binary_sensor.saj_inverter_fault_grid_lost` | Sensor binarny | - | HS3, H2 | - | Tak |
| Zbyt wysoka częstotliwość sieci | `binary_sensor.saj_inverter_fault_grid_overfrequency` | Sensor binarny | - | HS3, H2 | - | Tak |
| Zbyt wysoka składowa stała fazy sieci R | `binary_sensor.saj_inverter_fault_grid_phase_r_dc_injection` | Sensor binarny | - | HS3, H2 | - | Tak |
| Zbyt wysokie napięcie stałe fazy sieci R | `binary_sensor.saj_inverter_fault_grid_phase_r_dc_voltage` | Sensor binarny | - | HS3, H2 | - | Tak |
| Przepięcie fazy sieci R | `binary_sensor.saj_inverter_fault_grid_phase_r_overvoltage` | Sensor binarny | - | HS3, H2 | - | Tak |
| Zbyt niskie napięcie fazy sieci R | `binary_sensor.saj_inverter_fault_grid_phase_r_undervoltage` | Sensor binarny | - | HS3, H2 | - | Tak |
| Zbyt wysoka składowa stała fazy sieci S | `binary_sensor.saj_inverter_fault_grid_phase_s_dc_injection` | Sensor binarny | - | HS3, H2 | - | Tak |
| Zbyt wysokie napięcie stałe fazy sieci S | `binary_sensor.saj_inverter_fault_grid_phase_s_dc_voltage` | Sensor binarny | - | HS3, H2 | - | Tak |
| Przepięcie fazy sieci S | `binary_sensor.saj_inverter_fault_grid_phase_s_overvoltage` | Sensor binarny | - | HS3, H2 | - | Tak |
| Zbyt niskie napięcie fazy sieci S | `binary_sensor.saj_inverter_fault_grid_phase_s_undervoltage` | Sensor binarny | - | HS3, H2 | - | Tak |
| Zbyt wysoka składowa stała fazy sieci T | `binary_sensor.saj_inverter_fault_grid_phase_t_dc_injection` | Sensor binarny | - | HS3, H2 | - | Tak |
| Zbyt wysokie napięcie stałe fazy sieci T | `binary_sensor.saj_inverter_fault_grid_phase_t_dc_voltage` | Sensor binarny | - | HS3, H2 | - | Tak |
| Przepięcie fazy sieci T | `binary_sensor.saj_inverter_fault_grid_phase_t_overvoltage` | Sensor binarny | - | HS3, H2 | - | Tak |
| Zbyt niskie napięcie fazy sieci T | `binary_sensor.saj_inverter_fault_grid_phase_t_undervoltage` | Sensor binarny | - | HS3, H2 | - | Tak |
| Zbyt niska częstotliwość sieci | `binary_sensor.saj_inverter_fault_grid_underfrequency` | Sensor binarny | - | HS3, H2 | - | Tak |
| Sprzętowe przetężenie falownika | `binary_sensor.saj_inverter_fault_hardware_overcurrent` | Sensor binarny | - | HS3, H2 | - | Tak |
| Usterka izolacji | `binary_sensor.saj_inverter_fault_insulation` | Sensor binarny | - | HS3, H2 | - | Tak |
| Utracona komunikacja wewnętrzna | `binary_sensor.saj_inverter_fault_internal_communication` | Sensor binarny | - | HS3, H2 | - | Tak |
| Usterka prądu upływu | `binary_sensor.saj_inverter_fault_leakage_current` | Sensor binarny | - | HS3, H2 | - | Tak |
| Usterka czujnika prądu upływu | `binary_sensor.saj_inverter_fault_leakage_current_device` | Sensor binarny | - | HS3, H2 | - | Tak |
| Utracona komunikacja z licznikiem | `binary_sensor.saj_inverter_fault_meter_communication` | Sensor binarny | - | HS3, H2 | - | Tak |
| Usterka napięcia między przewodem neutralnym a ziemią | `binary_sensor.saj_inverter_fault_neutral_earth_voltage` | Sensor binarny | - | HS3, H2 | - | Tak |
| Zbyt niskie napięcie wyjścia poza siecią | `binary_sensor.saj_inverter_fault_off_grid_undervoltage` | Sensor binarny | - | HS3, H2 | - | Tak |
| Przeciążenie wyjścia | `binary_sensor.saj_inverter_fault_output_overload` | Sensor binarny | - | HS3, H2 | - | Tak |
| Zbyt wysoka temperatura | `binary_sensor.saj_inverter_fault_over_temperature` | Sensor binarny | - | HS3, H2 | - | Tak |
| Utracona komunikacja systemu równoległego | `binary_sensor.saj_inverter_fault_parallel_communication` | Sensor binarny | - | HS3 | - | Tak |
| Sprzętowe przetężenie PV | `binary_sensor.saj_inverter_fault_pv_hardware_overcurrent` | Sensor binarny | - | HS3, H2 | - | Tak |
| Usterka wejścia PV | `binary_sensor.saj_inverter_fault_pv_input` | Sensor binarny | - | HS3, H2 | - | Tak |
| Usterka trybu wejścia PV | `binary_sensor.saj_inverter_fault_pv_input_mode` | Sensor binarny | - | HS3, H2 | - | Tak |
| Utracona komunikacja z licznikiem słonecznym | `binary_sensor.saj_inverter_fault_pv_meter_communication` | Sensor binarny | - | HS3 | - | Tak |
| Przepięcie PV | `binary_sensor.saj_inverter_fault_pv_overvoltage` | Sensor binarny | - | HS3, H2 | - | Tak |
| Programowe przetężenie PV | `binary_sensor.saj_inverter_fault_pv_software_overcurrent` | Sensor binarny | - | HS3, H2 | - | Tak |
| Usterka przekaźnika | `binary_sensor.saj_inverter_fault_relay` | Sensor binarny | - | HS3, H2 | - | Tak |
| Utracona komunikacja z kontrolerem podrzędnym | `binary_sensor.saj_inverter_fault_slave_communication` | Sensor binarny | - | HS3 | - | Tak |
| Zbyt niska temperatura | `binary_sensor.saj_inverter_fault_under_temperature` | Sensor binarny | - | HS3, H2 | - | Tak |
| Nierozpoznana usterka falownika | `binary_sensor.saj_inverter_fault_unrecognised` | Sensor binarny | - | HS3, H2 | - | Tak |
| Usterka modułu baterii 2 | `binary_sensor.saj_battery_pack2_fault` | Sensor binarny | - | H2 | Bateria; Moduł baterii 2 i wyższe | Tak |
| Ostrzeżenie modułu baterii 2 | `binary_sensor.saj_battery_pack2_warning` | Sensor binarny | - | H2 | Bateria; Moduł baterii 2 i wyższe | Tak |
| Usterka modułu baterii 3 | `binary_sensor.saj_battery_pack3_fault` | Sensor binarny | - | H2 | Bateria; Moduł baterii 3 i wyższe | Tak |
| Ostrzeżenie modułu baterii 3 | `binary_sensor.saj_battery_pack3_warning` | Sensor binarny | - | H2 | Bateria; Moduł baterii 3 i wyższe | Tak |
| Usterka modułu baterii 4 | `binary_sensor.saj_battery_pack4_fault` | Sensor binarny | - | H2 | Bateria; Moduł baterii 4 i wyższe | Tak |
| Ostrzeżenie modułu baterii 4 | `binary_sensor.saj_battery_pack4_warning` | Sensor binarny | - | H2 | Bateria; Moduł baterii 4 i wyższe | Tak |
| Przepięcie szyny DC | `binary_sensor.saj_inverter_fault_bus_overvoltage` | Sensor binarny | - | H2 | - | Tak |
| Zbyt niskie napięcie szyny DC | `binary_sensor.saj_inverter_fault_bus_undervoltage` | Sensor binarny | - | H2 | - | Tak |
| Usterka fazy sieci | `binary_sensor.saj_inverter_fault_grid_phase` | Sensor binarny | - | H2 | - | Tak |
| Praca wyspowa | `binary_sensor.saj_inverter_fault_islanding` | Sensor binarny | - | H2 | - | Tak |
