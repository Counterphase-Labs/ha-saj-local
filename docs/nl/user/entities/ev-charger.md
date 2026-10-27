[en](../../../en-gb/user/entities/ev-charger.md) | [de](../../../de/user/entities/ev-charger.md) | nl | [fr](../../../fr/user/entities/ev-charger.md) | [zh](../../../zh-hans/user/entities/ev-charger.md) | [es](../../../es/user/entities/ev-charger.md) | [it](../../../it/user/entities/ev-charger.md) | [pl](../../../pl/user/entities/ev-charger.md) | [sv](../../../sv/user/entities/ev-charger.md)

# EV-lader

De EV-lader en de bediening van het opladen.

De functielijst van de integratie legt de EV-lader-entiteiten uit in [Optionele apparatuur](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

87 entiteiten. Gegenereerd door `make docs`. Niet met de hand bewerken.

Een voorvoegsel dat in Configureren is ingesteld komt na `saj_` in de ID van elke EV-lader-entiteit, bijvoorbeeld `sensor.saj_house_ev_serial_number` met het voorvoegsel `house`.

| Naam | Entiteits-ID | Type | Eenheid | Modellen | Apparatuur en aantallen | Standaard ingeschakeld |
| --- | --- | --- | --- | --- | --- | --- |
| Serienummer EV-lader | `sensor.saj_ev_serial_number` | Sensor | - | HS3 | EV-lader | Nee |
| Model EV-lader | `sensor.saj_ev_model` | Sensor | - | HS3 | EV-lader | Nee |
| Softwareversie EV-lader | `sensor.saj_ev_software_version` | Sensor | - | HS3 | EV-lader | Nee |
| Hardwareversie EV-lader | `sensor.saj_ev_hardware_version` | Sensor | - | HS3 | EV-lader | Nee |
| Aantal fasen EV-lader | `sensor.saj_ev_phase_count` | Sensor | - | HS3 | EV-lader | Nee |
| Minimaal vermogen EV-lader | `sensor.saj_ev_minimum_power` | Sensor | W | HS3 | EV-lader | Nee |
| Maximaal vermogen EV-lader | `sensor.saj_ev_maximum_power` | Sensor | W | HS3 | EV-lader | Nee |
| Werkmodus EV-lader | `sensor.saj_ev_work_mode` | Sensor | - | HS3 | EV-lader | Nee |
| Status EV-lader | `sensor.saj_ev_status` | Sensor | - | HS3 | EV-lader | Ja |
| Spanning L1 EV-lader | `sensor.saj_ev_l1_voltage` | Sensor | V | HS3 | EV-lader | Nee |
| Stroom L1 EV-lader | `sensor.saj_ev_l1_current` | Sensor | A | HS3 | EV-lader | Nee |
| Spanning L2 EV-lader | `sensor.saj_ev_l2_voltage` | Sensor | V | HS3 | EV-lader | Nee |
| Stroom L2 EV-lader | `sensor.saj_ev_l2_current` | Sensor | A | HS3 | EV-lader | Nee |
| Spanning L3 EV-lader | `sensor.saj_ev_l3_voltage` | Sensor | V | HS3 | EV-lader | Nee |
| Stroom L3 EV-lader | `sensor.saj_ev_l3_current` | Sensor | A | HS3 | EV-lader | Nee |
| Vermogen EV-lader | `sensor.saj_ev_power` | Sensor | W | HS3 | EV-lader | Ja |
| EV-oplaadduur | `sensor.saj_ev_charge_duration` | Sensor | min | HS3 | EV-lader | Nee |
| Sessie-energie EV-lader | `sensor.saj_ev_session_energy` | Sensor | kWh | HS3 | EV-lader | Ja |
| Totale energie EV-lader | `sensor.saj_ev_total_energy` | Sensor | kWh | HS3 | EV-lader | Ja |
| Control pilot-spanning EV-lader | `sensor.saj_ev_control_pilot_voltage` | Sensor | V | HS3 | EV-lader | Nee |
| Dutycycle EV-lader | `sensor.saj_ev_duty_cycle` | Sensor | % | HS3 | EV-lader | Nee |
| Afstandsbediening EV-lader | `sensor.saj_ev_remote_control` | Sensor | - | HS3 | EV-lader | Nee |
| Stroomsetpoint EV-lader | `sensor.saj_ev_current_setpoint` | Sensor | A | HS3 | EV-lader | Nee |
| Sessiestart EV-lader | `sensor.saj_ev_session_start` | Sensor | - | HS3 | EV-lader | Nee |
| Sessie-einde EV-lader | `sensor.saj_ev_session_end` | Sensor | - | HS3 | EV-lader | Nee |
| Protocolversie van instellingen EV-lader | `sensor.saj_ev_settings_protocol_version` | Sensor | - | HS3 | EV-lader | Nee |
| EV-laderadres | `sensor.saj_ev_address` | Sensor | - | HS3 | EV-lader | Nee |
| EV-laderbaudrate | `sensor.saj_ev_baud_rate` | Sensor | - | HS3 | EV-lader | Nee |
| Aantal EV-laders | `sensor.saj_ev_charger_count` | Sensor | - | HS3 | EV-lader | Nee |
| EV-ladercommunicatie-time-out | `sensor.saj_ev_communication_timeout` | Sensor | s | HS3 | EV-lader | Nee |
| EV-laderpoortmodus | `sensor.saj_ev_port_mode` | Sensor | - | HS3 | EV-lader | Nee |
| EV-laderpoortadres | `sensor.saj_ev_port_address` | Sensor | - | HS3 | EV-lader | Nee |
| EV-ladermodus | `select.saj_ev_mode` | Selectie | - | HS3 | EV-lader | Ja |
| EV-oplaadvermogen | `number.saj_ev_charge_power` | Nummer | W | HS3 | EV-lader | Nee |
| EV-ladertijdvak 1 starttijd | `time.saj_ev_slot_1_start` | Tijd | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 1 eindtijd | `time.saj_ev_slot_1_end` | Tijd | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 1 modus | `select.saj_ev_slot_1_mode` | Selectie | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 1 opladen via net | `switch.saj_ev_slot_1_grid_charging` | Schakelaar | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 1 batterijontlading | `switch.saj_ev_slot_1_battery_discharge` | Schakelaar | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 1 weekdagen | `number.saj_ev_slot_1_days` | Nummer | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 1 vermogen | `number.saj_ev_slot_1_power` | Nummer | W | HS3 | EV-lader | Nee |
| EV-ladertijdvak 2 starttijd | `time.saj_ev_slot_2_start` | Tijd | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 2 eindtijd | `time.saj_ev_slot_2_end` | Tijd | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 2 modus | `select.saj_ev_slot_2_mode` | Selectie | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 2 opladen via net | `switch.saj_ev_slot_2_grid_charging` | Schakelaar | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 2 batterijontlading | `switch.saj_ev_slot_2_battery_discharge` | Schakelaar | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 2 weekdagen | `number.saj_ev_slot_2_days` | Nummer | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 2 vermogen | `number.saj_ev_slot_2_power` | Nummer | W | HS3 | EV-lader | Nee |
| EV-ladertijdvak 3 starttijd | `time.saj_ev_slot_3_start` | Tijd | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 3 eindtijd | `time.saj_ev_slot_3_end` | Tijd | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 3 modus | `select.saj_ev_slot_3_mode` | Selectie | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 3 opladen via net | `switch.saj_ev_slot_3_grid_charging` | Schakelaar | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 3 batterijontlading | `switch.saj_ev_slot_3_battery_discharge` | Schakelaar | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 3 weekdagen | `number.saj_ev_slot_3_days` | Nummer | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 3 vermogen | `number.saj_ev_slot_3_power` | Nummer | W | HS3 | EV-lader | Nee |
| EV-ladertijdvak 4 starttijd | `time.saj_ev_slot_4_start` | Tijd | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 4 eindtijd | `time.saj_ev_slot_4_end` | Tijd | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 4 modus | `select.saj_ev_slot_4_mode` | Selectie | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 4 opladen via net | `switch.saj_ev_slot_4_grid_charging` | Schakelaar | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 4 batterijontlading | `switch.saj_ev_slot_4_battery_discharge` | Schakelaar | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 4 weekdagen | `number.saj_ev_slot_4_days` | Nummer | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 4 vermogen | `number.saj_ev_slot_4_power` | Nummer | W | HS3 | EV-lader | Nee |
| EV-ladertijdvak 5 starttijd | `time.saj_ev_slot_5_start` | Tijd | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 5 eindtijd | `time.saj_ev_slot_5_end` | Tijd | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 5 modus | `select.saj_ev_slot_5_mode` | Selectie | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 5 opladen via net | `switch.saj_ev_slot_5_grid_charging` | Schakelaar | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 5 batterijontlading | `switch.saj_ev_slot_5_battery_discharge` | Schakelaar | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 5 weekdagen | `number.saj_ev_slot_5_days` | Nummer | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 5 vermogen | `number.saj_ev_slot_5_power` | Nummer | W | HS3 | EV-lader | Nee |
| EV-ladertijdvak 6 starttijd | `time.saj_ev_slot_6_start` | Tijd | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 6 eindtijd | `time.saj_ev_slot_6_end` | Tijd | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 6 modus | `select.saj_ev_slot_6_mode` | Selectie | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 6 opladen via net | `switch.saj_ev_slot_6_grid_charging` | Schakelaar | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 6 batterijontlading | `switch.saj_ev_slot_6_battery_discharge` | Schakelaar | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 6 weekdagen | `number.saj_ev_slot_6_days` | Nummer | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 6 vermogen | `number.saj_ev_slot_6_power` | Nummer | W | HS3 | EV-lader | Nee |
| EV-ladertijdvak 7 starttijd | `time.saj_ev_slot_7_start` | Tijd | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 7 eindtijd | `time.saj_ev_slot_7_end` | Tijd | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 7 modus | `select.saj_ev_slot_7_mode` | Selectie | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 7 opladen via net | `switch.saj_ev_slot_7_grid_charging` | Schakelaar | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 7 batterijontlading | `switch.saj_ev_slot_7_battery_discharge` | Schakelaar | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 7 weekdagen | `number.saj_ev_slot_7_days` | Nummer | - | HS3 | EV-lader | Nee |
| EV-ladertijdvak 7 vermogen | `number.saj_ev_slot_7_power` | Nummer | W | HS3 | EV-lader | Nee |
| EV-lader opladen met minimale stroom | `switch.saj_ev_minimum_current_charging` | Schakelaar | - | HS3 | EV-lader | Nee |
| EMS-opladen EV-lader | `switch.saj_ev_ems_charging` | Schakelaar | - | HS3 | EV-lader | Nee |
| EMS-fasemodus EV-lader | `select.saj_ev_ems_phase_mode` | Selectie | - | HS3 | EV-lader | Nee |
| EMS-oplaadstroom EV-lader | `number.saj_ev_ems_charge_current` | Nummer | A | HS3 | EV-lader | Nee |
