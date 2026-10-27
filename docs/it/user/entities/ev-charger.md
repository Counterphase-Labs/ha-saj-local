[en](../../../en-gb/user/entities/ev-charger.md) | [de](../../../de/user/entities/ev-charger.md) | [nl](../../../nl/user/entities/ev-charger.md) | [fr](../../../fr/user/entities/ev-charger.md) | [zh](../../../zh-hans/user/entities/ev-charger.md) | [es](../../../es/user/entities/ev-charger.md) | it | [pl](../../../pl/user/entities/ev-charger.md) | [sv](../../../sv/user/entities/ev-charger.md)

# Caricatore EV

Il caricatore EV e i suoi controlli di ricarica.

Le entità dell'area «Caricatore EV» sono descritte nell'elenco delle funzionalità dell'integrazione, in [Apparecchiature opzionali](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

87 entità. Generato da `make docs`. Non modificare a mano.

Un prefisso impostato in Configura va dopo `saj_` nell'ID di ogni entità dell'area «Caricatore EV», per esempio `sensor.saj_house_ev_serial_number` con il prefisso `house`.

| Nome | ID entità | Tipo | Unità | Modelli | Apparecchiature e quantità | Abilitata per impostazione predefinita |
| --- | --- | --- | --- | --- | --- | --- |
| Numero di serie del caricatore EV | `sensor.saj_ev_serial_number` | Sensore | - | HS3 | Caricatore EV | No |
| Modello del caricatore EV | `sensor.saj_ev_model` | Sensore | - | HS3 | Caricatore EV | No |
| Versione software del caricatore EV | `sensor.saj_ev_software_version` | Sensore | - | HS3 | Caricatore EV | No |
| Versione hardware del caricatore EV | `sensor.saj_ev_hardware_version` | Sensore | - | HS3 | Caricatore EV | No |
| Numero di fasi del caricatore EV | `sensor.saj_ev_phase_count` | Sensore | - | HS3 | Caricatore EV | No |
| Potenza minima del caricatore EV | `sensor.saj_ev_minimum_power` | Sensore | W | HS3 | Caricatore EV | No |
| Potenza massima del caricatore EV | `sensor.saj_ev_maximum_power` | Sensore | W | HS3 | Caricatore EV | No |
| Modalità di lavoro del caricatore EV | `sensor.saj_ev_work_mode` | Sensore | - | HS3 | Caricatore EV | No |
| Stato del caricatore EV | `sensor.saj_ev_status` | Sensore | - | HS3 | Caricatore EV | Sì |
| Tensione L1 del caricatore EV | `sensor.saj_ev_l1_voltage` | Sensore | V | HS3 | Caricatore EV | No |
| Corrente L1 del caricatore EV | `sensor.saj_ev_l1_current` | Sensore | A | HS3 | Caricatore EV | No |
| Tensione L2 del caricatore EV | `sensor.saj_ev_l2_voltage` | Sensore | V | HS3 | Caricatore EV | No |
| Corrente L2 del caricatore EV | `sensor.saj_ev_l2_current` | Sensore | A | HS3 | Caricatore EV | No |
| Tensione L3 del caricatore EV | `sensor.saj_ev_l3_voltage` | Sensore | V | HS3 | Caricatore EV | No |
| Corrente L3 del caricatore EV | `sensor.saj_ev_l3_current` | Sensore | A | HS3 | Caricatore EV | No |
| Potenza del caricatore EV | `sensor.saj_ev_power` | Sensore | W | HS3 | Caricatore EV | Sì |
| Durata della ricarica EV | `sensor.saj_ev_charge_duration` | Sensore | min | HS3 | Caricatore EV | No |
| Energia della sessione del caricatore EV | `sensor.saj_ev_session_energy` | Sensore | kWh | HS3 | Caricatore EV | Sì |
| Energia totale del caricatore EV | `sensor.saj_ev_total_energy` | Sensore | kWh | HS3 | Caricatore EV | Sì |
| Tensione del control pilot del caricatore EV | `sensor.saj_ev_control_pilot_voltage` | Sensore | V | HS3 | Caricatore EV | No |
| Duty cycle del caricatore EV | `sensor.saj_ev_duty_cycle` | Sensore | % | HS3 | Caricatore EV | No |
| Controllo remoto del caricatore EV | `sensor.saj_ev_remote_control` | Sensore | - | HS3 | Caricatore EV | No |
| Valore impostato della corrente del caricatore EV | `sensor.saj_ev_current_setpoint` | Sensore | A | HS3 | Caricatore EV | No |
| Inizio della sessione del caricatore EV | `sensor.saj_ev_session_start` | Sensore | - | HS3 | Caricatore EV | No |
| Fine della sessione del caricatore EV | `sensor.saj_ev_session_end` | Sensore | - | HS3 | Caricatore EV | No |
| Versione del protocollo delle impostazioni del caricatore EV | `sensor.saj_ev_settings_protocol_version` | Sensore | - | HS3 | Caricatore EV | No |
| Indirizzo del caricatore EV | `sensor.saj_ev_address` | Sensore | - | HS3 | Caricatore EV | No |
| Baud rate del caricatore EV | `sensor.saj_ev_baud_rate` | Sensore | - | HS3 | Caricatore EV | No |
| Numero di caricatori EV | `sensor.saj_ev_charger_count` | Sensore | - | HS3 | Caricatore EV | No |
| Timeout di comunicazione del caricatore EV | `sensor.saj_ev_communication_timeout` | Sensore | s | HS3 | Caricatore EV | No |
| Modalità della porta del caricatore EV | `sensor.saj_ev_port_mode` | Sensore | - | HS3 | Caricatore EV | No |
| Indirizzo della porta del caricatore EV | `sensor.saj_ev_port_address` | Sensore | - | HS3 | Caricatore EV | No |
| Modalità del caricatore EV | `select.saj_ev_mode` | Selezione | - | HS3 | Caricatore EV | Sì |
| Potenza di ricarica EV | `number.saj_ev_charge_power` | Numero | W | HS3 | Caricatore EV | No |
| Ora di inizio fascia 1 del caricatore EV | `time.saj_ev_slot_1_start` | Ora | - | HS3 | Caricatore EV | No |
| Ora di fine fascia 1 del caricatore EV | `time.saj_ev_slot_1_end` | Ora | - | HS3 | Caricatore EV | No |
| Modalità fascia 1 del caricatore EV | `select.saj_ev_slot_1_mode` | Selezione | - | HS3 | Caricatore EV | No |
| Ricarica dalla rete fascia 1 del caricatore EV | `switch.saj_ev_slot_1_grid_charging` | Interruttore | - | HS3 | Caricatore EV | No |
| Scarica della batteria fascia 1 del caricatore EV | `switch.saj_ev_slot_1_battery_discharge` | Interruttore | - | HS3 | Caricatore EV | No |
| Giorni della settimana fascia 1 del caricatore EV | `number.saj_ev_slot_1_days` | Numero | - | HS3 | Caricatore EV | No |
| Potenza fascia 1 del caricatore EV | `number.saj_ev_slot_1_power` | Numero | W | HS3 | Caricatore EV | No |
| Ora di inizio fascia 2 del caricatore EV | `time.saj_ev_slot_2_start` | Ora | - | HS3 | Caricatore EV | No |
| Ora di fine fascia 2 del caricatore EV | `time.saj_ev_slot_2_end` | Ora | - | HS3 | Caricatore EV | No |
| Modalità fascia 2 del caricatore EV | `select.saj_ev_slot_2_mode` | Selezione | - | HS3 | Caricatore EV | No |
| Ricarica dalla rete fascia 2 del caricatore EV | `switch.saj_ev_slot_2_grid_charging` | Interruttore | - | HS3 | Caricatore EV | No |
| Scarica della batteria fascia 2 del caricatore EV | `switch.saj_ev_slot_2_battery_discharge` | Interruttore | - | HS3 | Caricatore EV | No |
| Giorni della settimana fascia 2 del caricatore EV | `number.saj_ev_slot_2_days` | Numero | - | HS3 | Caricatore EV | No |
| Potenza fascia 2 del caricatore EV | `number.saj_ev_slot_2_power` | Numero | W | HS3 | Caricatore EV | No |
| Ora di inizio fascia 3 del caricatore EV | `time.saj_ev_slot_3_start` | Ora | - | HS3 | Caricatore EV | No |
| Ora di fine fascia 3 del caricatore EV | `time.saj_ev_slot_3_end` | Ora | - | HS3 | Caricatore EV | No |
| Modalità fascia 3 del caricatore EV | `select.saj_ev_slot_3_mode` | Selezione | - | HS3 | Caricatore EV | No |
| Ricarica dalla rete fascia 3 del caricatore EV | `switch.saj_ev_slot_3_grid_charging` | Interruttore | - | HS3 | Caricatore EV | No |
| Scarica della batteria fascia 3 del caricatore EV | `switch.saj_ev_slot_3_battery_discharge` | Interruttore | - | HS3 | Caricatore EV | No |
| Giorni della settimana fascia 3 del caricatore EV | `number.saj_ev_slot_3_days` | Numero | - | HS3 | Caricatore EV | No |
| Potenza fascia 3 del caricatore EV | `number.saj_ev_slot_3_power` | Numero | W | HS3 | Caricatore EV | No |
| Ora di inizio fascia 4 del caricatore EV | `time.saj_ev_slot_4_start` | Ora | - | HS3 | Caricatore EV | No |
| Ora di fine fascia 4 del caricatore EV | `time.saj_ev_slot_4_end` | Ora | - | HS3 | Caricatore EV | No |
| Modalità fascia 4 del caricatore EV | `select.saj_ev_slot_4_mode` | Selezione | - | HS3 | Caricatore EV | No |
| Ricarica dalla rete fascia 4 del caricatore EV | `switch.saj_ev_slot_4_grid_charging` | Interruttore | - | HS3 | Caricatore EV | No |
| Scarica della batteria fascia 4 del caricatore EV | `switch.saj_ev_slot_4_battery_discharge` | Interruttore | - | HS3 | Caricatore EV | No |
| Giorni della settimana fascia 4 del caricatore EV | `number.saj_ev_slot_4_days` | Numero | - | HS3 | Caricatore EV | No |
| Potenza fascia 4 del caricatore EV | `number.saj_ev_slot_4_power` | Numero | W | HS3 | Caricatore EV | No |
| Ora di inizio fascia 5 del caricatore EV | `time.saj_ev_slot_5_start` | Ora | - | HS3 | Caricatore EV | No |
| Ora di fine fascia 5 del caricatore EV | `time.saj_ev_slot_5_end` | Ora | - | HS3 | Caricatore EV | No |
| Modalità fascia 5 del caricatore EV | `select.saj_ev_slot_5_mode` | Selezione | - | HS3 | Caricatore EV | No |
| Ricarica dalla rete fascia 5 del caricatore EV | `switch.saj_ev_slot_5_grid_charging` | Interruttore | - | HS3 | Caricatore EV | No |
| Scarica della batteria fascia 5 del caricatore EV | `switch.saj_ev_slot_5_battery_discharge` | Interruttore | - | HS3 | Caricatore EV | No |
| Giorni della settimana fascia 5 del caricatore EV | `number.saj_ev_slot_5_days` | Numero | - | HS3 | Caricatore EV | No |
| Potenza fascia 5 del caricatore EV | `number.saj_ev_slot_5_power` | Numero | W | HS3 | Caricatore EV | No |
| Ora di inizio fascia 6 del caricatore EV | `time.saj_ev_slot_6_start` | Ora | - | HS3 | Caricatore EV | No |
| Ora di fine fascia 6 del caricatore EV | `time.saj_ev_slot_6_end` | Ora | - | HS3 | Caricatore EV | No |
| Modalità fascia 6 del caricatore EV | `select.saj_ev_slot_6_mode` | Selezione | - | HS3 | Caricatore EV | No |
| Ricarica dalla rete fascia 6 del caricatore EV | `switch.saj_ev_slot_6_grid_charging` | Interruttore | - | HS3 | Caricatore EV | No |
| Scarica della batteria fascia 6 del caricatore EV | `switch.saj_ev_slot_6_battery_discharge` | Interruttore | - | HS3 | Caricatore EV | No |
| Giorni della settimana fascia 6 del caricatore EV | `number.saj_ev_slot_6_days` | Numero | - | HS3 | Caricatore EV | No |
| Potenza fascia 6 del caricatore EV | `number.saj_ev_slot_6_power` | Numero | W | HS3 | Caricatore EV | No |
| Ora di inizio fascia 7 del caricatore EV | `time.saj_ev_slot_7_start` | Ora | - | HS3 | Caricatore EV | No |
| Ora di fine fascia 7 del caricatore EV | `time.saj_ev_slot_7_end` | Ora | - | HS3 | Caricatore EV | No |
| Modalità fascia 7 del caricatore EV | `select.saj_ev_slot_7_mode` | Selezione | - | HS3 | Caricatore EV | No |
| Ricarica dalla rete fascia 7 del caricatore EV | `switch.saj_ev_slot_7_grid_charging` | Interruttore | - | HS3 | Caricatore EV | No |
| Scarica della batteria fascia 7 del caricatore EV | `switch.saj_ev_slot_7_battery_discharge` | Interruttore | - | HS3 | Caricatore EV | No |
| Giorni della settimana fascia 7 del caricatore EV | `number.saj_ev_slot_7_days` | Numero | - | HS3 | Caricatore EV | No |
| Potenza fascia 7 del caricatore EV | `number.saj_ev_slot_7_power` | Numero | W | HS3 | Caricatore EV | No |
| Ricarica a corrente minima del caricatore EV | `switch.saj_ev_minimum_current_charging` | Interruttore | - | HS3 | Caricatore EV | No |
| Ricarica EMS del caricatore EV | `switch.saj_ev_ems_charging` | Interruttore | - | HS3 | Caricatore EV | No |
| Modalità di fase EMS del caricatore EV | `select.saj_ev_ems_phase_mode` | Selezione | - | HS3 | Caricatore EV | No |
| Corrente di carica EMS del caricatore EV | `number.saj_ev_ems_charge_current` | Numero | A | HS3 | Caricatore EV | No |
