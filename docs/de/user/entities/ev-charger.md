[en](../../../en-gb/user/entities/ev-charger.md) | de | [nl](../../../nl/user/entities/ev-charger.md) | [fr](../../../fr/user/entities/ev-charger.md) | [zh](../../../zh-hans/user/entities/ev-charger.md) | [es](../../../es/user/entities/ev-charger.md) | [it](../../../it/user/entities/ev-charger.md) | [pl](../../../pl/user/entities/ev-charger.md) | [sv](../../../sv/user/entities/ev-charger.md)

# Wallbox

Die Wallbox und ihre Ladesteuerung.

Die Funktionsliste der Integration erklärt die Entitäten (Wallbox) in [Optionale Ausstattung](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

87 Entitäten. Erzeugt von `make docs`. Nicht von Hand bearbeiten.

Ein in Konfigurieren gesetztes Präfix steht nach `saj_` in der ID jeder Entität (Wallbox), zum Beispiel `sensor.saj_house_ev_serial_number` mit dem Präfix `house`.

| Name | Entitäts-ID | Typ | Einheit | Modelle | Ausstattung und Anzahl | Standardmäßig aktiviert |
| --- | --- | --- | --- | --- | --- | --- |
| Wallbox-Seriennummer | `sensor.saj_ev_serial_number` | Sensor | - | HS3 | Wallbox | Nein |
| Wallbox-Modell | `sensor.saj_ev_model` | Sensor | - | HS3 | Wallbox | Nein |
| Wallbox-Softwareversion | `sensor.saj_ev_software_version` | Sensor | - | HS3 | Wallbox | Nein |
| Wallbox-Hardwareversion | `sensor.saj_ev_hardware_version` | Sensor | - | HS3 | Wallbox | Nein |
| Wallbox-Phasenanzahl | `sensor.saj_ev_phase_count` | Sensor | - | HS3 | Wallbox | Nein |
| Wallbox-Mindestleistung | `sensor.saj_ev_minimum_power` | Sensor | W | HS3 | Wallbox | Nein |
| Wallbox-Höchstleistung | `sensor.saj_ev_maximum_power` | Sensor | W | HS3 | Wallbox | Nein |
| Wallbox-Betriebsmodus | `sensor.saj_ev_work_mode` | Sensor | - | HS3 | Wallbox | Nein |
| Wallbox-Status | `sensor.saj_ev_status` | Sensor | - | HS3 | Wallbox | Ja |
| Wallbox-Spannung L1 | `sensor.saj_ev_l1_voltage` | Sensor | V | HS3 | Wallbox | Nein |
| Wallbox-Strom L1 | `sensor.saj_ev_l1_current` | Sensor | A | HS3 | Wallbox | Nein |
| Wallbox-Spannung L2 | `sensor.saj_ev_l2_voltage` | Sensor | V | HS3 | Wallbox | Nein |
| Wallbox-Strom L2 | `sensor.saj_ev_l2_current` | Sensor | A | HS3 | Wallbox | Nein |
| Wallbox-Spannung L3 | `sensor.saj_ev_l3_voltage` | Sensor | V | HS3 | Wallbox | Nein |
| Wallbox-Strom L3 | `sensor.saj_ev_l3_current` | Sensor | A | HS3 | Wallbox | Nein |
| Wallbox-Leistung | `sensor.saj_ev_power` | Sensor | W | HS3 | Wallbox | Ja |
| Wallbox-Ladedauer | `sensor.saj_ev_charge_duration` | Sensor | min | HS3 | Wallbox | Nein |
| Wallbox-Ladesitzungsenergie | `sensor.saj_ev_session_energy` | Sensor | kWh | HS3 | Wallbox | Ja |
| Wallbox-Gesamtenergie | `sensor.saj_ev_total_energy` | Sensor | kWh | HS3 | Wallbox | Ja |
| Wallbox-Control-Pilot-Spannung | `sensor.saj_ev_control_pilot_voltage` | Sensor | V | HS3 | Wallbox | Nein |
| Wallbox-Tastgrad | `sensor.saj_ev_duty_cycle` | Sensor | % | HS3 | Wallbox | Nein |
| Wallbox-Fernsteuerung | `sensor.saj_ev_remote_control` | Sensor | - | HS3 | Wallbox | Nein |
| Wallbox-Stromsollwert | `sensor.saj_ev_current_setpoint` | Sensor | A | HS3 | Wallbox | Nein |
| Wallbox-Ladesitzungsbeginn | `sensor.saj_ev_session_start` | Sensor | - | HS3 | Wallbox | Nein |
| Wallbox-Ladesitzungsende | `sensor.saj_ev_session_end` | Sensor | - | HS3 | Wallbox | Nein |
| Wallbox-Einstellungsprotokollversion | `sensor.saj_ev_settings_protocol_version` | Sensor | - | HS3 | Wallbox | Nein |
| Wallbox-Adresse | `sensor.saj_ev_address` | Sensor | - | HS3 | Wallbox | Nein |
| Wallbox-Baudrate | `sensor.saj_ev_baud_rate` | Sensor | - | HS3 | Wallbox | Nein |
| Anzahl der Wallboxen | `sensor.saj_ev_charger_count` | Sensor | - | HS3 | Wallbox | Nein |
| Wallbox-Kommunikations-Timeout | `sensor.saj_ev_communication_timeout` | Sensor | s | HS3 | Wallbox | Nein |
| Wallbox-Portmodus | `sensor.saj_ev_port_mode` | Sensor | - | HS3 | Wallbox | Nein |
| Wallbox-Portadresse | `sensor.saj_ev_port_address` | Sensor | - | HS3 | Wallbox | Nein |
| Wallbox-Modus | `select.saj_ev_mode` | Auswahl | - | HS3 | Wallbox | Ja |
| Wallbox-Ladeleistung | `number.saj_ev_charge_power` | Zahl | W | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 1 Startzeit | `time.saj_ev_slot_1_start` | Zeit | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 1 Endzeit | `time.saj_ev_slot_1_end` | Zeit | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 1 Modus | `select.saj_ev_slot_1_mode` | Auswahl | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 1 Laden aus dem Netz | `switch.saj_ev_slot_1_grid_charging` | Schalter | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 1 Batterieentladung | `switch.saj_ev_slot_1_battery_discharge` | Schalter | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 1 Wochentage | `number.saj_ev_slot_1_days` | Zahl | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 1 Leistung | `number.saj_ev_slot_1_power` | Zahl | W | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 2 Startzeit | `time.saj_ev_slot_2_start` | Zeit | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 2 Endzeit | `time.saj_ev_slot_2_end` | Zeit | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 2 Modus | `select.saj_ev_slot_2_mode` | Auswahl | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 2 Laden aus dem Netz | `switch.saj_ev_slot_2_grid_charging` | Schalter | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 2 Batterieentladung | `switch.saj_ev_slot_2_battery_discharge` | Schalter | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 2 Wochentage | `number.saj_ev_slot_2_days` | Zahl | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 2 Leistung | `number.saj_ev_slot_2_power` | Zahl | W | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 3 Startzeit | `time.saj_ev_slot_3_start` | Zeit | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 3 Endzeit | `time.saj_ev_slot_3_end` | Zeit | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 3 Modus | `select.saj_ev_slot_3_mode` | Auswahl | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 3 Laden aus dem Netz | `switch.saj_ev_slot_3_grid_charging` | Schalter | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 3 Batterieentladung | `switch.saj_ev_slot_3_battery_discharge` | Schalter | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 3 Wochentage | `number.saj_ev_slot_3_days` | Zahl | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 3 Leistung | `number.saj_ev_slot_3_power` | Zahl | W | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 4 Startzeit | `time.saj_ev_slot_4_start` | Zeit | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 4 Endzeit | `time.saj_ev_slot_4_end` | Zeit | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 4 Modus | `select.saj_ev_slot_4_mode` | Auswahl | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 4 Laden aus dem Netz | `switch.saj_ev_slot_4_grid_charging` | Schalter | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 4 Batterieentladung | `switch.saj_ev_slot_4_battery_discharge` | Schalter | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 4 Wochentage | `number.saj_ev_slot_4_days` | Zahl | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 4 Leistung | `number.saj_ev_slot_4_power` | Zahl | W | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 5 Startzeit | `time.saj_ev_slot_5_start` | Zeit | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 5 Endzeit | `time.saj_ev_slot_5_end` | Zeit | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 5 Modus | `select.saj_ev_slot_5_mode` | Auswahl | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 5 Laden aus dem Netz | `switch.saj_ev_slot_5_grid_charging` | Schalter | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 5 Batterieentladung | `switch.saj_ev_slot_5_battery_discharge` | Schalter | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 5 Wochentage | `number.saj_ev_slot_5_days` | Zahl | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 5 Leistung | `number.saj_ev_slot_5_power` | Zahl | W | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 6 Startzeit | `time.saj_ev_slot_6_start` | Zeit | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 6 Endzeit | `time.saj_ev_slot_6_end` | Zeit | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 6 Modus | `select.saj_ev_slot_6_mode` | Auswahl | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 6 Laden aus dem Netz | `switch.saj_ev_slot_6_grid_charging` | Schalter | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 6 Batterieentladung | `switch.saj_ev_slot_6_battery_discharge` | Schalter | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 6 Wochentage | `number.saj_ev_slot_6_days` | Zahl | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 6 Leistung | `number.saj_ev_slot_6_power` | Zahl | W | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 7 Startzeit | `time.saj_ev_slot_7_start` | Zeit | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 7 Endzeit | `time.saj_ev_slot_7_end` | Zeit | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 7 Modus | `select.saj_ev_slot_7_mode` | Auswahl | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 7 Laden aus dem Netz | `switch.saj_ev_slot_7_grid_charging` | Schalter | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 7 Batterieentladung | `switch.saj_ev_slot_7_battery_discharge` | Schalter | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 7 Wochentage | `number.saj_ev_slot_7_days` | Zahl | - | HS3 | Wallbox | Nein |
| Wallbox-Zeitfenster 7 Leistung | `number.saj_ev_slot_7_power` | Zahl | W | HS3 | Wallbox | Nein |
| Wallbox-Laden mit Mindeststrom | `switch.saj_ev_minimum_current_charging` | Schalter | - | HS3 | Wallbox | Nein |
| Wallbox-EMS-Laden | `switch.saj_ev_ems_charging` | Schalter | - | HS3 | Wallbox | Nein |
| Wallbox-EMS-Phasenmodus | `select.saj_ev_ems_phase_mode` | Auswahl | - | HS3 | Wallbox | Nein |
| Wallbox-EMS-Ladestrom | `number.saj_ev_ems_charge_current` | Zahl | A | HS3 | Wallbox | Nein |
