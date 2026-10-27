[en](../../../en-gb/user/entities/ev-charger.md) | [de](../../../de/user/entities/ev-charger.md) | [nl](../../../nl/user/entities/ev-charger.md) | [fr](../../../fr/user/entities/ev-charger.md) | [zh](../../../zh-hans/user/entities/ev-charger.md) | [es](../../../es/user/entities/ev-charger.md) | [it](../../../it/user/entities/ev-charger.md) | [pl](../../../pl/user/entities/ev-charger.md) | sv

# Elbilsladdare

Elbilsladdaren och dess laddningsstyrningar.

Integrationens funktionslista förklarar entiteterna för Elbilsladdare i [Valfri utrustning](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

87 entiteter. Genereras av `make docs`. Redigera inte för hand.

Ett prefix som anges i Konfigurera hamnar efter `saj_` i ID:t för varje entitet i Elbilsladdare, till exempel `sensor.saj_house_ev_serial_number` med prefixet `house`.

| Namn | Entitets-ID | Typ | Enhet | Modeller | Utrustning och antal | Aktiverad som standard |
| --- | --- | --- | --- | --- | --- | --- |
| Elbilsladdarens serienummer | `sensor.saj_ev_serial_number` | Sensor | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens modell | `sensor.saj_ev_model` | Sensor | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens programvaruversion | `sensor.saj_ev_software_version` | Sensor | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens maskinvaruversion | `sensor.saj_ev_hardware_version` | Sensor | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens antal faser | `sensor.saj_ev_phase_count` | Sensor | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens minimieffekt | `sensor.saj_ev_minimum_power` | Sensor | W | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens maximieffekt | `sensor.saj_ev_maximum_power` | Sensor | W | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens arbetsläge | `sensor.saj_ev_work_mode` | Sensor | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens status | `sensor.saj_ev_status` | Sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens L1-spänning | `sensor.saj_ev_l1_voltage` | Sensor | V | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens L1-ström | `sensor.saj_ev_l1_current` | Sensor | A | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens L2-spänning | `sensor.saj_ev_l2_voltage` | Sensor | V | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens L2-ström | `sensor.saj_ev_l2_current` | Sensor | A | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens L3-spänning | `sensor.saj_ev_l3_voltage` | Sensor | V | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens L3-ström | `sensor.saj_ev_l3_current` | Sensor | A | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens effekt | `sensor.saj_ev_power` | Sensor | W | HS3 | Elbilsladdare | Ja |
| Elbilsladdningens varaktighet | `sensor.saj_ev_charge_duration` | Sensor | min | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens sessionsenergi | `sensor.saj_ev_session_energy` | Sensor | kWh | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens total energi | `sensor.saj_ev_total_energy` | Sensor | kWh | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens pilotsignalspänning | `sensor.saj_ev_control_pilot_voltage` | Sensor | V | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens pulskvot | `sensor.saj_ev_duty_cycle` | Sensor | % | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens fjärrstyrning | `sensor.saj_ev_remote_control` | Sensor | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens strömbörvärde | `sensor.saj_ev_current_setpoint` | Sensor | A | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens sessionsstart | `sensor.saj_ev_session_start` | Sensor | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens sessionsslut | `sensor.saj_ev_session_end` | Sensor | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens inställningsprotokollversion | `sensor.saj_ev_settings_protocol_version` | Sensor | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens adress | `sensor.saj_ev_address` | Sensor | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens överföringshastighet | `sensor.saj_ev_baud_rate` | Sensor | - | HS3 | Elbilsladdare | Nej |
| Antal elbilsladdare | `sensor.saj_ev_charger_count` | Sensor | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens tidsgräns för kommunikation | `sensor.saj_ev_communication_timeout` | Sensor | s | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens portläge | `sensor.saj_ev_port_mode` | Sensor | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens portadress | `sensor.saj_ev_port_address` | Sensor | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens läge | `select.saj_ev_mode` | Val | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdningseffekt | `number.saj_ev_charge_power` | Nummer | W | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 1 starttid | `time.saj_ev_slot_1_start` | Tid | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 1 sluttid | `time.saj_ev_slot_1_end` | Tid | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 1 läge | `select.saj_ev_slot_1_mode` | Val | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 1 nätladdning | `switch.saj_ev_slot_1_grid_charging` | Brytare | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 1 batteriurladdning | `switch.saj_ev_slot_1_battery_discharge` | Brytare | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 1 veckodagar | `number.saj_ev_slot_1_days` | Nummer | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 1 effekt | `number.saj_ev_slot_1_power` | Nummer | W | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 2 starttid | `time.saj_ev_slot_2_start` | Tid | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 2 sluttid | `time.saj_ev_slot_2_end` | Tid | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 2 läge | `select.saj_ev_slot_2_mode` | Val | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 2 nätladdning | `switch.saj_ev_slot_2_grid_charging` | Brytare | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 2 batteriurladdning | `switch.saj_ev_slot_2_battery_discharge` | Brytare | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 2 veckodagar | `number.saj_ev_slot_2_days` | Nummer | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 2 effekt | `number.saj_ev_slot_2_power` | Nummer | W | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 3 starttid | `time.saj_ev_slot_3_start` | Tid | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 3 sluttid | `time.saj_ev_slot_3_end` | Tid | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 3 läge | `select.saj_ev_slot_3_mode` | Val | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 3 nätladdning | `switch.saj_ev_slot_3_grid_charging` | Brytare | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 3 batteriurladdning | `switch.saj_ev_slot_3_battery_discharge` | Brytare | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 3 veckodagar | `number.saj_ev_slot_3_days` | Nummer | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 3 effekt | `number.saj_ev_slot_3_power` | Nummer | W | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 4 starttid | `time.saj_ev_slot_4_start` | Tid | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 4 sluttid | `time.saj_ev_slot_4_end` | Tid | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 4 läge | `select.saj_ev_slot_4_mode` | Val | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 4 nätladdning | `switch.saj_ev_slot_4_grid_charging` | Brytare | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 4 batteriurladdning | `switch.saj_ev_slot_4_battery_discharge` | Brytare | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 4 veckodagar | `number.saj_ev_slot_4_days` | Nummer | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 4 effekt | `number.saj_ev_slot_4_power` | Nummer | W | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 5 starttid | `time.saj_ev_slot_5_start` | Tid | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 5 sluttid | `time.saj_ev_slot_5_end` | Tid | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 5 läge | `select.saj_ev_slot_5_mode` | Val | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 5 nätladdning | `switch.saj_ev_slot_5_grid_charging` | Brytare | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 5 batteriurladdning | `switch.saj_ev_slot_5_battery_discharge` | Brytare | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 5 veckodagar | `number.saj_ev_slot_5_days` | Nummer | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 5 effekt | `number.saj_ev_slot_5_power` | Nummer | W | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 6 starttid | `time.saj_ev_slot_6_start` | Tid | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 6 sluttid | `time.saj_ev_slot_6_end` | Tid | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 6 läge | `select.saj_ev_slot_6_mode` | Val | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 6 nätladdning | `switch.saj_ev_slot_6_grid_charging` | Brytare | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 6 batteriurladdning | `switch.saj_ev_slot_6_battery_discharge` | Brytare | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 6 veckodagar | `number.saj_ev_slot_6_days` | Nummer | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 6 effekt | `number.saj_ev_slot_6_power` | Nummer | W | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 7 starttid | `time.saj_ev_slot_7_start` | Tid | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 7 sluttid | `time.saj_ev_slot_7_end` | Tid | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 7 läge | `select.saj_ev_slot_7_mode` | Val | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 7 nätladdning | `switch.saj_ev_slot_7_grid_charging` | Brytare | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 7 batteriurladdning | `switch.saj_ev_slot_7_battery_discharge` | Brytare | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 7 veckodagar | `number.saj_ev_slot_7_days` | Nummer | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdartidslucka 7 effekt | `number.saj_ev_slot_7_power` | Nummer | W | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens laddning med minimiström | `switch.saj_ev_minimum_current_charging` | Brytare | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens EMS-laddning | `switch.saj_ev_ems_charging` | Brytare | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens EMS-fasläge | `select.saj_ev_ems_phase_mode` | Val | - | HS3 | Elbilsladdare | Nej |
| Elbilsladdarens EMS-laddningsström | `number.saj_ev_ems_charge_current` | Nummer | A | HS3 | Elbilsladdare | Nej |
