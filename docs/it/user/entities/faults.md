[en](../../../en-gb/user/entities/faults.md) | [de](../../../de/user/entities/faults.md) | [nl](../../../nl/user/entities/faults.md) | [fr](../../../fr/user/entities/faults.md) | [zh](../../../zh-hans/user/entities/faults.md) | [es](../../../es/user/entities/faults.md) | it | [pl](../../../pl/user/entities/faults.md) | [sv](../../../sv/user/entities/faults.md)

# Guasti

Guasti segnalati dall'inverter, dalla batteria e dal caricatore EV.

Le entità dell'area «Guasti» sono descritte nell'elenco delle funzionalità dell'integrazione, in [Guasti dell'apparecchiatura e riparazioni](../../../../custom_components/saj_local/docs/features.md#device-faults-and-repairs).

139 entità. Generato da `make docs`. Non modificare a mano.

Un prefisso impostato in Configura va dopo `saj_` nell'ID di ogni entità dell'area «Guasti», per esempio `binary_sensor.saj_house_battery_pack1_fault` con il prefisso `house`.

| Nome | ID entità | Tipo | Unità | Modelli | Apparecchiature e quantità | Abilitata per impostazione predefinita |
| --- | --- | --- | --- | --- | --- | --- |
| Guasto modulo batteria 1 | `binary_sensor.saj_battery_pack1_fault` | Sensore binario | - | HS3, H2 | Batteria | Sì |
| Avviso modulo batteria 1 | `binary_sensor.saj_battery_pack1_warning` | Sensore binario | - | HS3, H2 | Batteria | Sì |
| Guasto della batteria | `binary_sensor.saj_battery_fault` | Sensore binario | - | HS3, H2 | Batteria | Sì |
| Produttore del BMS della batteria incompatibile | `binary_sensor.saj_battery_fault_bms_incompatible` | Sensore binario | - | HS3 | Batteria | Sì |
| Interruttore automatico della batteria aperto | `binary_sensor.saj_battery_fault_breaker_open` | Sensore binario | - | HS3 | Batteria | Sì |
| Celle della batteria non corrispondenti | `binary_sensor.saj_battery_fault_cell_incompatible` | Sensore binario | - | HS3 | Batteria | Sì |
| Sovratemperatura di una cella della batteria | `binary_sensor.saj_battery_fault_cell_over_temperature` | Sensore binario | - | HS3 | Batteria | Sì |
| Sovratensione di una cella della batteria | `binary_sensor.saj_battery_fault_cell_overvoltage` | Sensore binario | - | HS3 | Batteria | Sì |
| Produttore delle celle della batteria non corrispondente | `binary_sensor.saj_battery_fault_cell_supplier_incompatible` | Sensore binario | - | HS3 | Batteria | Sì |
| Differenza di temperatura tra le celle della batteria troppo grande | `binary_sensor.saj_battery_fault_cell_temperature_difference` | Sensore binario | - | HS3 | Batteria | Sì |
| Sottotensione di una cella della batteria | `binary_sensor.saj_battery_fault_cell_undervoltage` | Sensore binario | - | HS3 | Batteria | Sì |
| Differenza di tensione tra le celle della batteria troppo grande, livello 1 | `binary_sensor.saj_battery_fault_cell_voltage_difference_1` | Sensore binario | - | HS3 | Batteria | Sì |
| Differenza di tensione tra le celle della batteria troppo grande, livello 2 | `binary_sensor.saj_battery_fault_cell_voltage_difference_2` | Sensore binario | - | HS3 | Batteria | Sì |
| Batteria troppo fredda per caricare | `binary_sensor.saj_battery_fault_charge_cold` | Sensore binario | - | HS3 | Batteria | Sì |
| Batteria troppo calda per caricare | `binary_sensor.saj_battery_fault_charge_hot` | Sensore binario | - | HS3 | Batteria | Sì |
| Sovracorrente di carica della batteria | `binary_sensor.saj_battery_fault_charge_overcurrent` | Sensore binario | - | HS3 | Batteria | Sì |
| Sovratensione della porta di carica della batteria | `binary_sensor.saj_battery_fault_charging_port_overvoltage` | Sensore binario | - | HS3 | Batteria | Sì |
| Batteria troppo fredda per scaricare | `binary_sensor.saj_battery_fault_discharge_cold` | Sensore binario | - | HS3 | Batteria | Sì |
| Batteria troppo calda per scaricare | `binary_sensor.saj_battery_fault_discharge_hot` | Sensore binario | - | HS3 | Batteria | Sì |
| Sovracorrente di scarica della batteria | `binary_sensor.saj_battery_fault_discharge_overcurrent` | Sensore binario | - | HS3 | Batteria | Sì |
| Guasto del fusibile della batteria | `binary_sensor.saj_battery_fault_fuse` | Sensore binario | - | HS3 | Batteria | Sì |
| Guasto hardware del BMS della batteria | `binary_sensor.saj_battery_fault_hardware` | Sensore binario | - | HS3 | Batteria | Sì |
| Guasto di isolamento del BMS della batteria | `binary_sensor.saj_battery_fault_insulation` | Sensore binario | - | HS3 | Batteria | Sì |
| Comunicazione interna del BMS della batteria persa | `binary_sensor.saj_battery_fault_internal_communication` | Sensore binario | - | HS3 | Batteria | Sì |
| Guasto di indirizzamento dei moduli batteria | `binary_sensor.saj_battery_fault_pack_sequence` | Sensore binario | - | HS3 | Batteria | Sì |
| Guasto di precarica della batteria | `binary_sensor.saj_battery_fault_precharge` | Sensore binario | - | HS3 | Batteria | Sì |
| Guasto del relè del BMS della batteria | `binary_sensor.saj_battery_fault_relay` | Sensore binario | - | HS3 | Batteria | Sì |
| Cortocircuito della batteria | `binary_sensor.saj_battery_fault_short_circuit` | Sensore binario | - | HS3 | Batteria | Sì |
| Sistema della batteria bloccato | `binary_sensor.saj_battery_fault_system_locked` | Sensore binario | - | HS3 | Batteria | Sì |
| Tensione totale della batteria alta | `binary_sensor.saj_battery_fault_total_overvoltage` | Sensore binario | - | HS3 | Batteria | Sì |
| Tensione totale della batteria bassa | `binary_sensor.saj_battery_fault_total_undervoltage` | Sensore binario | - | HS3 | Batteria | Sì |
| Mancata corrispondenza della tensione totale della batteria | `binary_sensor.saj_battery_fault_total_voltage_matching` | Sensore binario | - | HS3 | Batteria | Sì |
| Guasto non riconosciuto della batteria | `binary_sensor.saj_battery_fault_unrecognised` | Sensore binario | - | HS3, H2 | Batteria | Sì |
| Livello di tensione della batteria non corrispondente | `binary_sensor.saj_battery_fault_voltage_level_mismatch` | Sensore binario | - | HS3 | Batteria | Sì |
| Guasto del caricatore EV | `binary_sensor.saj_ev_fault` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Sovracorrente CA del caricatore EV | `binary_sensor.saj_ev_fault_ac_overcurrent` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Sovrafrequenza CA del caricatore EV | `binary_sensor.saj_ev_fault_ac_overfrequency` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Sovratensione CA del caricatore EV | `binary_sensor.saj_ev_fault_ac_overvoltage` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Corrente residua CA del caricatore EV | `binary_sensor.saj_ev_fault_ac_residual_current` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Sottofrequenza CA del caricatore EV | `binary_sensor.saj_ev_fault_ac_underfrequency` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Sottotensione CA del caricatore EV | `binary_sensor.saj_ev_fault_ac_undervoltage` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Guasto Bluetooth del caricatore EV | `binary_sensor.saj_ev_fault_bluetooth` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Guasto di corrente del connettore del caricatore EV | `binary_sensor.saj_ev_fault_connector_current` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Guasto del blocco del connettore del caricatore EV | `binary_sensor.saj_ev_fault_connector_lock` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Guasto del control pilot del caricatore EV (sotto 2 V) | `binary_sensor.saj_ev_fault_control_pilot` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Guasto A della corrente residua CC del caricatore EV | `binary_sensor.saj_ev_fault_dc_residual_current_a` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Guasto B della corrente residua CC del caricatore EV | `binary_sensor.saj_ev_fault_dc_residual_current_b` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Guasto C della corrente residua CC del caricatore EV | `binary_sensor.saj_ev_fault_dc_residual_current_c` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Arresto di emergenza del caricatore EV | `binary_sensor.saj_ev_fault_emergency_stop` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Guasto di messa a terra del caricatore EV | `binary_sensor.saj_ev_fault_grounding` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Sovratemperatura del morsetto di ingresso del caricatore EV | `binary_sensor.saj_ev_fault_input_terminal_over_temperature` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Guasto del contatore del caricatore EV | `binary_sensor.saj_ev_fault_meter` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Sovraccarico del caricatore EV | `binary_sensor.saj_ev_fault_overload` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Guasto della sequenza delle fasi del caricatore EV | `binary_sensor.saj_ev_fault_phase_sequence` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Guasto del circuito RCD del caricatore EV | `binary_sensor.saj_ev_fault_rcd_circuit` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Guasto del relè del caricatore EV | `binary_sensor.saj_ev_fault_relay` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Sovratemperatura del relè del caricatore EV | `binary_sensor.saj_ev_fault_relay_over_temperature` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Timeout di comunicazione RS485 del caricatore EV | `binary_sensor.saj_ev_fault_rs485_timeout` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Guasto dell'alimentazione elettrica del caricatore EV | `binary_sensor.saj_ev_fault_supply` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Sottotemperatura del caricatore EV | `binary_sensor.saj_ev_fault_under_temperature` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Guasto non riconosciuto del caricatore EV | `binary_sensor.saj_ev_fault_unrecognised` | Sensore binario | - | HS3 | Caricatore EV | Sì |
| Guasto dell'inverter | `binary_sensor.saj_inverter_fault` | Sensore binario | - | HS3, H2 | - | Sì |
| Comunicazione con la scheda di rilevamento archi persa | `binary_sensor.saj_inverter_fault_afci_communication` | Sensore binario | - | HS3 | - | Sì |
| Guasto da arco elettrico | `binary_sensor.saj_inverter_fault_arc` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto del dispositivo di rilevamento archi | `binary_sensor.saj_inverter_fault_arc_device` | Sensore binario | - | HS3 | - | Sì |
| Autorizzazione scaduta | `binary_sensor.saj_inverter_fault_authorisation_expired` | Sensore binario | - | HS3, H2 | - | Sì |
| Tensione di carica della batteria alta | `binary_sensor.saj_inverter_fault_battery_charge_overvoltage` | Sensore binario | - | HS3, H2 | - | Sì |
| Tensione di scarica della batteria bassa | `binary_sensor.saj_inverter_fault_battery_discharge_undervoltage` | Sensore binario | - | HS3, H2 | - | Sì |
| Circuito aperto della batteria | `binary_sensor.saj_inverter_fault_battery_open_circuit` | Sensore binario | - | HS3, H2 | - | Sì |
| Sovracorrente della porta della batteria | `binary_sensor.saj_inverter_fault_battery_overcurrent` | Sensore binario | - | HS3, H2 | - | Sì |
| Sovraccarico della porta della batteria | `binary_sensor.saj_inverter_fault_battery_overload` | Sensore binario | - | HS3, H2 | - | Sì |
| Sovratensione della porta della batteria | `binary_sensor.saj_inverter_fault_battery_overvoltage` | Sensore binario | - | HS3, H2 | - | Sì |
| Timeout dell'avvio graduale della batteria | `binary_sensor.saj_inverter_fault_battery_soft_start` | Sensore binario | - | HS3, H2 | - | Sì |
| Comunicazione con il BMS persa | `binary_sensor.saj_inverter_fault_bms_communication` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto del dispositivo BMS | `binary_sensor.saj_inverter_fault_bms_device` | Sensore binario | - | HS3, H2 | - | Sì |
| Sovratensione hardware del bus CC | `binary_sensor.saj_inverter_fault_bus_hardware_overvoltage` | Sensore binario | - | HS3, H2 | - | Sì |
| Squilibrio della tensione del bus CC | `binary_sensor.saj_inverter_fault_bus_imbalance` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto della memoria del controller | `binary_sensor.saj_inverter_fault_controller_memory` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto del dispositivo CT | `binary_sensor.saj_inverter_fault_ct_device` | Sensore binario | - | HS3 | - | Sì |
| Guasto del sensore di corrente | `binary_sensor.saj_inverter_fault_current_sensor` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto del sensore di iniezione CC | `binary_sensor.saj_inverter_fault_dc_injection_device` | Sensore binario | - | HS3, H2 | - | Sì |
| Comunicazione con l'unità DC-DC persa | `binary_sensor.saj_inverter_fault_dcdc_communication` | Sensore binario | - | HS3 | - | Sì |
| Guasto dell'unità DC-DC | `binary_sensor.saj_inverter_fault_dcdc_device` | Sensore binario | - | HS3 | - | Sì |
| Guasto dell'orologio della scheda display | `binary_sensor.saj_inverter_fault_display_clock` | Sensore binario | - | HS3, H2 | - | Sì |
| Comunicazione con la scheda display persa | `binary_sensor.saj_inverter_fault_display_communication` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto della memoria della scheda display | `binary_sensor.saj_inverter_fault_display_memory` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto DRM0 | `binary_sensor.saj_inverter_fault_drm0` | Sensore binario | - | HS3, H2 | - | Sì |
| Comunicazione con il caricatore EV persa | `binary_sensor.saj_inverter_fault_ev_charger_communication` | Sensore binario | - | HS3 | - | Sì |
| Guasto della ventola 1 | `binary_sensor.saj_inverter_fault_fan_1` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto della ventola 2 | `binary_sensor.saj_inverter_fault_fan_2` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto della ventola 3 | `binary_sensor.saj_inverter_fault_fan_3` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto della ventola 4 | `binary_sensor.saj_inverter_fault_fan_4` | Sensore binario | - | HS3, H2 | - | Sì |
| Sovratensione media di rete su 10 minuti | `binary_sensor.saj_inverter_fault_grid_average_overvoltage` | Sensore binario | - | HS3, H2 | - | Sì |
| Rete assente | `binary_sensor.saj_inverter_fault_grid_lost` | Sensore binario | - | HS3, H2 | - | Sì |
| Sovrafrequenza di rete | `binary_sensor.saj_inverter_fault_grid_overfrequency` | Sensore binario | - | HS3, H2 | - | Sì |
| Iniezione CC di rete fase R alta | `binary_sensor.saj_inverter_fault_grid_phase_r_dc_injection` | Sensore binario | - | HS3, H2 | - | Sì |
| Tensione continua di rete fase R alta | `binary_sensor.saj_inverter_fault_grid_phase_r_dc_voltage` | Sensore binario | - | HS3, H2 | - | Sì |
| Sovratensione di rete fase R | `binary_sensor.saj_inverter_fault_grid_phase_r_overvoltage` | Sensore binario | - | HS3, H2 | - | Sì |
| Sottotensione di rete fase R | `binary_sensor.saj_inverter_fault_grid_phase_r_undervoltage` | Sensore binario | - | HS3, H2 | - | Sì |
| Iniezione CC di rete fase S alta | `binary_sensor.saj_inverter_fault_grid_phase_s_dc_injection` | Sensore binario | - | HS3, H2 | - | Sì |
| Tensione continua di rete fase S alta | `binary_sensor.saj_inverter_fault_grid_phase_s_dc_voltage` | Sensore binario | - | HS3, H2 | - | Sì |
| Sovratensione di rete fase S | `binary_sensor.saj_inverter_fault_grid_phase_s_overvoltage` | Sensore binario | - | HS3, H2 | - | Sì |
| Sottotensione di rete fase S | `binary_sensor.saj_inverter_fault_grid_phase_s_undervoltage` | Sensore binario | - | HS3, H2 | - | Sì |
| Iniezione CC di rete fase T alta | `binary_sensor.saj_inverter_fault_grid_phase_t_dc_injection` | Sensore binario | - | HS3, H2 | - | Sì |
| Tensione continua di rete fase T alta | `binary_sensor.saj_inverter_fault_grid_phase_t_dc_voltage` | Sensore binario | - | HS3, H2 | - | Sì |
| Sovratensione di rete fase T | `binary_sensor.saj_inverter_fault_grid_phase_t_overvoltage` | Sensore binario | - | HS3, H2 | - | Sì |
| Sottotensione di rete fase T | `binary_sensor.saj_inverter_fault_grid_phase_t_undervoltage` | Sensore binario | - | HS3, H2 | - | Sì |
| Sottofrequenza di rete | `binary_sensor.saj_inverter_fault_grid_underfrequency` | Sensore binario | - | HS3, H2 | - | Sì |
| Sovracorrente hardware dell'inverter | `binary_sensor.saj_inverter_fault_hardware_overcurrent` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto di isolamento | `binary_sensor.saj_inverter_fault_insulation` | Sensore binario | - | HS3, H2 | - | Sì |
| Comunicazione interna persa | `binary_sensor.saj_inverter_fault_internal_communication` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto di corrente di dispersione | `binary_sensor.saj_inverter_fault_leakage_current` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto del sensore della corrente di dispersione | `binary_sensor.saj_inverter_fault_leakage_current_device` | Sensore binario | - | HS3, H2 | - | Sì |
| Comunicazione con il contatore persa | `binary_sensor.saj_inverter_fault_meter_communication` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto di tensione tra neutro e terra | `binary_sensor.saj_inverter_fault_neutral_earth_voltage` | Sensore binario | - | HS3, H2 | - | Sì |
| Sottotensione dell'uscita off-grid | `binary_sensor.saj_inverter_fault_off_grid_undervoltage` | Sensore binario | - | HS3, H2 | - | Sì |
| Sovraccarico dell'uscita | `binary_sensor.saj_inverter_fault_output_overload` | Sensore binario | - | HS3, H2 | - | Sì |
| Sovratemperatura | `binary_sensor.saj_inverter_fault_over_temperature` | Sensore binario | - | HS3, H2 | - | Sì |
| Comunicazione del sistema in parallelo persa | `binary_sensor.saj_inverter_fault_parallel_communication` | Sensore binario | - | HS3 | - | Sì |
| Sovracorrente hardware PV | `binary_sensor.saj_inverter_fault_pv_hardware_overcurrent` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto dell'ingresso PV | `binary_sensor.saj_inverter_fault_pv_input` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto della modalità di ingresso PV | `binary_sensor.saj_inverter_fault_pv_input_mode` | Sensore binario | - | HS3, H2 | - | Sì |
| Comunicazione con il contatore solare persa | `binary_sensor.saj_inverter_fault_pv_meter_communication` | Sensore binario | - | HS3 | - | Sì |
| Sovratensione PV | `binary_sensor.saj_inverter_fault_pv_overvoltage` | Sensore binario | - | HS3, H2 | - | Sì |
| Sovracorrente software PV | `binary_sensor.saj_inverter_fault_pv_software_overcurrent` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto del relè | `binary_sensor.saj_inverter_fault_relay` | Sensore binario | - | HS3, H2 | - | Sì |
| Comunicazione con il controller slave persa | `binary_sensor.saj_inverter_fault_slave_communication` | Sensore binario | - | HS3 | - | Sì |
| Sottotemperatura | `binary_sensor.saj_inverter_fault_under_temperature` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto non riconosciuto dell'inverter | `binary_sensor.saj_inverter_fault_unrecognised` | Sensore binario | - | HS3, H2 | - | Sì |
| Guasto modulo batteria 2 | `binary_sensor.saj_battery_pack2_fault` | Sensore binario | - | H2 | Batteria; Modulo batteria 2 e successivi | Sì |
| Avviso modulo batteria 2 | `binary_sensor.saj_battery_pack2_warning` | Sensore binario | - | H2 | Batteria; Modulo batteria 2 e successivi | Sì |
| Guasto modulo batteria 3 | `binary_sensor.saj_battery_pack3_fault` | Sensore binario | - | H2 | Batteria; Modulo batteria 3 e successivi | Sì |
| Avviso modulo batteria 3 | `binary_sensor.saj_battery_pack3_warning` | Sensore binario | - | H2 | Batteria; Modulo batteria 3 e successivi | Sì |
| Guasto modulo batteria 4 | `binary_sensor.saj_battery_pack4_fault` | Sensore binario | - | H2 | Batteria; Modulo batteria 4 e successivi | Sì |
| Avviso modulo batteria 4 | `binary_sensor.saj_battery_pack4_warning` | Sensore binario | - | H2 | Batteria; Modulo batteria 4 e successivi | Sì |
| Sovratensione del bus CC | `binary_sensor.saj_inverter_fault_bus_overvoltage` | Sensore binario | - | H2 | - | Sì |
| Sottotensione del bus CC | `binary_sensor.saj_inverter_fault_bus_undervoltage` | Sensore binario | - | H2 | - | Sì |
| Guasto di fase della rete | `binary_sensor.saj_inverter_fault_grid_phase` | Sensore binario | - | H2 | - | Sì |
| Funzionamento in isola | `binary_sensor.saj_inverter_fault_islanding` | Sensore binario | - | H2 | - | Sì |
