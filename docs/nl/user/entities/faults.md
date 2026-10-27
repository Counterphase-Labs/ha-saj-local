[en](../../../en-gb/user/entities/faults.md) | [de](../../../de/user/entities/faults.md) | nl | [fr](../../../fr/user/entities/faults.md) | [zh](../../../zh-hans/user/entities/faults.md) | [es](../../../es/user/entities/faults.md) | [it](../../../it/user/entities/faults.md) | [pl](../../../pl/user/entities/faults.md) | [sv](../../../sv/user/entities/faults.md)

# Storingen

Storingen die de omvormer, de batterij en de EV-lader melden.

De functielijst van de integratie legt de Storingen-entiteiten uit in [Apparaatstoringen en reparaties](../../../../custom_components/saj_local/docs/features.md#device-faults-and-repairs).

139 entiteiten. Gegenereerd door `make docs`. Niet met de hand bewerken.

Een voorvoegsel dat in Configureren is ingesteld komt na `saj_` in de ID van elke Storingen-entiteit, bijvoorbeeld `binary_sensor.saj_house_battery_pack1_fault` met het voorvoegsel `house`.

| Naam | Entiteits-ID | Type | Eenheid | Modellen | Apparatuur en aantallen | Standaard ingeschakeld |
| --- | --- | --- | --- | --- | --- | --- |
| Batterijpack 1 storing | `binary_sensor.saj_battery_pack1_fault` | Binaire sensor | - | HS3, H2 | Batterij | Ja |
| Batterijpack 1 waarschuwing | `binary_sensor.saj_battery_pack1_warning` | Binaire sensor | - | HS3, H2 | Batterij | Ja |
| Batterijstoring | `binary_sensor.saj_battery_fault` | Binaire sensor | - | HS3, H2 | Batterij | Ja |
| BMS-fabrikant batterij niet compatibel | `binary_sensor.saj_battery_fault_bms_incompatible` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterijstroomonderbreker open | `binary_sensor.saj_battery_fault_breaker_open` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterijcel komt niet overeen | `binary_sensor.saj_battery_fault_cell_incompatible` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterijcel te hoge temperatuur | `binary_sensor.saj_battery_fault_cell_over_temperature` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterijceloverspanning | `binary_sensor.saj_battery_fault_cell_overvoltage` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterijcelfabrikant komt niet overeen | `binary_sensor.saj_battery_fault_cell_supplier_incompatible` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterijceltemperatuurverschil te groot | `binary_sensor.saj_battery_fault_cell_temperature_difference` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterijcelonderspanning | `binary_sensor.saj_battery_fault_cell_undervoltage` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterijcelspanningsverschil te groot, niveau 1 | `binary_sensor.saj_battery_fault_cell_voltage_difference_1` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterijcelspanningsverschil te groot, niveau 2 | `binary_sensor.saj_battery_fault_cell_voltage_difference_2` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterij te koud om op te laden | `binary_sensor.saj_battery_fault_charge_cold` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterij te heet om op te laden | `binary_sensor.saj_battery_fault_charge_hot` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterijoplaadoverstroom | `binary_sensor.saj_battery_fault_charge_overcurrent` | Binaire sensor | - | HS3 | Batterij | Ja |
| Overspanning oplaadpoort batterij | `binary_sensor.saj_battery_fault_charging_port_overvoltage` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterij te koud om te ontladen | `binary_sensor.saj_battery_fault_discharge_cold` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterij te heet om te ontladen | `binary_sensor.saj_battery_fault_discharge_hot` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterijontlaadoverstroom | `binary_sensor.saj_battery_fault_discharge_overcurrent` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterijzekeringstoring | `binary_sensor.saj_battery_fault_fuse` | Binaire sensor | - | HS3 | Batterij | Ja |
| BMS-hardwarestoring batterij | `binary_sensor.saj_battery_fault_hardware` | Binaire sensor | - | HS3 | Batterij | Ja |
| BMS-isolatiestoring batterij | `binary_sensor.saj_battery_fault_insulation` | Binaire sensor | - | HS3 | Batterij | Ja |
| Interne BMS-communicatie batterij verloren | `binary_sensor.saj_battery_fault_internal_communication` | Binaire sensor | - | HS3 | Batterij | Ja |
| Storing adressering batterijpack | `binary_sensor.saj_battery_fault_pack_sequence` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterijvoorlaadstoring | `binary_sensor.saj_battery_fault_precharge` | Binaire sensor | - | HS3 | Batterij | Ja |
| BMS-relaisstoring batterij | `binary_sensor.saj_battery_fault_relay` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterijkortsluiting | `binary_sensor.saj_battery_fault_short_circuit` | Binaire sensor | - | HS3 | Batterij | Ja |
| Batterijsysteem vergrendeld | `binary_sensor.saj_battery_fault_system_locked` | Binaire sensor | - | HS3 | Batterij | Ja |
| Totale batterijspanning hoog | `binary_sensor.saj_battery_fault_total_overvoltage` | Binaire sensor | - | HS3 | Batterij | Ja |
| Totale batterijspanning laag | `binary_sensor.saj_battery_fault_total_undervoltage` | Binaire sensor | - | HS3 | Batterij | Ja |
| Afstemming totale batterijspanning mislukt | `binary_sensor.saj_battery_fault_total_voltage_matching` | Binaire sensor | - | HS3 | Batterij | Ja |
| Niet-herkende batterijstoring | `binary_sensor.saj_battery_fault_unrecognised` | Binaire sensor | - | HS3, H2 | Batterij | Ja |
| Batterijspanningsniveau komt niet overeen | `binary_sensor.saj_battery_fault_voltage_level_mismatch` | Binaire sensor | - | HS3 | Batterij | Ja |
| EV-laderstoring | `binary_sensor.saj_ev_fault` | Binaire sensor | - | HS3 | EV-lader | Ja |
| AC-overstroom EV-lader | `binary_sensor.saj_ev_fault_ac_overcurrent` | Binaire sensor | - | HS3 | EV-lader | Ja |
| AC-overfrequentie EV-lader | `binary_sensor.saj_ev_fault_ac_overfrequency` | Binaire sensor | - | HS3 | EV-lader | Ja |
| AC-overspanning EV-lader | `binary_sensor.saj_ev_fault_ac_overvoltage` | Binaire sensor | - | HS3 | EV-lader | Ja |
| AC-reststroom EV-lader | `binary_sensor.saj_ev_fault_ac_residual_current` | Binaire sensor | - | HS3 | EV-lader | Ja |
| AC-onderfrequentie EV-lader | `binary_sensor.saj_ev_fault_ac_underfrequency` | Binaire sensor | - | HS3 | EV-lader | Ja |
| AC-onderspanning EV-lader | `binary_sensor.saj_ev_fault_ac_undervoltage` | Binaire sensor | - | HS3 | EV-lader | Ja |
| Bluetooth-storing EV-lader | `binary_sensor.saj_ev_fault_bluetooth` | Binaire sensor | - | HS3 | EV-lader | Ja |
| Stroomstoring connector EV-lader | `binary_sensor.saj_ev_fault_connector_current` | Binaire sensor | - | HS3 | EV-lader | Ja |
| Vergrendelingsstoring connector EV-lader | `binary_sensor.saj_ev_fault_connector_lock` | Binaire sensor | - | HS3 | EV-lader | Ja |
| Control pilot-storing EV-lader (onder 2 V) | `binary_sensor.saj_ev_fault_control_pilot` | Binaire sensor | - | HS3 | EV-lader | Ja |
| DC-reststroomstoring A EV-lader | `binary_sensor.saj_ev_fault_dc_residual_current_a` | Binaire sensor | - | HS3 | EV-lader | Ja |
| DC-reststroomstoring B EV-lader | `binary_sensor.saj_ev_fault_dc_residual_current_b` | Binaire sensor | - | HS3 | EV-lader | Ja |
| DC-reststroomstoring C EV-lader | `binary_sensor.saj_ev_fault_dc_residual_current_c` | Binaire sensor | - | HS3 | EV-lader | Ja |
| EV-ladernoodstop | `binary_sensor.saj_ev_fault_emergency_stop` | Binaire sensor | - | HS3 | EV-lader | Ja |
| EV-laderaardingsstoring | `binary_sensor.saj_ev_fault_grounding` | Binaire sensor | - | HS3 | EV-lader | Ja |
| Ingangsklem EV-lader te hoge temperatuur | `binary_sensor.saj_ev_fault_input_terminal_over_temperature` | Binaire sensor | - | HS3 | EV-lader | Ja |
| EV-ladermeterstoring | `binary_sensor.saj_ev_fault_meter` | Binaire sensor | - | HS3 | EV-lader | Ja |
| EV-laderoverbelasting | `binary_sensor.saj_ev_fault_overload` | Binaire sensor | - | HS3 | EV-lader | Ja |
| EV-laderfasevolgordestoring | `binary_sensor.saj_ev_fault_phase_sequence` | Binaire sensor | - | HS3 | EV-lader | Ja |
| RCD-circuitstoring EV-lader | `binary_sensor.saj_ev_fault_rcd_circuit` | Binaire sensor | - | HS3 | EV-lader | Ja |
| EV-laderrelaisstoring | `binary_sensor.saj_ev_fault_relay` | Binaire sensor | - | HS3 | EV-lader | Ja |
| Relais EV-lader te hoge temperatuur | `binary_sensor.saj_ev_fault_relay_over_temperature` | Binaire sensor | - | HS3 | EV-lader | Ja |
| RS485-communicatie-time-out EV-lader | `binary_sensor.saj_ev_fault_rs485_timeout` | Binaire sensor | - | HS3 | EV-lader | Ja |
| EV-laderstroomvoorzieningsstoring | `binary_sensor.saj_ev_fault_supply` | Binaire sensor | - | HS3 | EV-lader | Ja |
| EV-lader te lage temperatuur | `binary_sensor.saj_ev_fault_under_temperature` | Binaire sensor | - | HS3 | EV-lader | Ja |
| Niet-herkende EV-laderstoring | `binary_sensor.saj_ev_fault_unrecognised` | Binaire sensor | - | HS3 | EV-lader | Ja |
| Omvormerstoring | `binary_sensor.saj_inverter_fault` | Binaire sensor | - | HS3, H2 | - | Ja |
| Communicatie met boogdetectiebord verloren | `binary_sensor.saj_inverter_fault_afci_communication` | Binaire sensor | - | HS3 | - | Ja |
| Boogstoring | `binary_sensor.saj_inverter_fault_arc` | Binaire sensor | - | HS3, H2 | - | Ja |
| Storing boogdetectieapparaat | `binary_sensor.saj_inverter_fault_arc_device` | Binaire sensor | - | HS3 | - | Ja |
| Autorisatie verlopen | `binary_sensor.saj_inverter_fault_authorisation_expired` | Binaire sensor | - | HS3, H2 | - | Ja |
| Batterijoplaadspanning hoog | `binary_sensor.saj_inverter_fault_battery_charge_overvoltage` | Binaire sensor | - | HS3, H2 | - | Ja |
| Batterijontlaadspanning laag | `binary_sensor.saj_inverter_fault_battery_discharge_undervoltage` | Binaire sensor | - | HS3, H2 | - | Ja |
| Open circuit batterij | `binary_sensor.saj_inverter_fault_battery_open_circuit` | Binaire sensor | - | HS3, H2 | - | Ja |
| Overstroom batterijpoort | `binary_sensor.saj_inverter_fault_battery_overcurrent` | Binaire sensor | - | HS3, H2 | - | Ja |
| Overbelasting batterijpoort | `binary_sensor.saj_inverter_fault_battery_overload` | Binaire sensor | - | HS3, H2 | - | Ja |
| Overspanning batterijpoort | `binary_sensor.saj_inverter_fault_battery_overvoltage` | Binaire sensor | - | HS3, H2 | - | Ja |
| Time-out zachte start batterij | `binary_sensor.saj_inverter_fault_battery_soft_start` | Binaire sensor | - | HS3, H2 | - | Ja |
| BMS-communicatie verloren | `binary_sensor.saj_inverter_fault_bms_communication` | Binaire sensor | - | HS3, H2 | - | Ja |
| BMS-apparaatstoring | `binary_sensor.saj_inverter_fault_bms_device` | Binaire sensor | - | HS3, H2 | - | Ja |
| Hardware-overspanning DC-bus | `binary_sensor.saj_inverter_fault_bus_hardware_overvoltage` | Binaire sensor | - | HS3, H2 | - | Ja |
| DC-busspanning onbalans | `binary_sensor.saj_inverter_fault_bus_imbalance` | Binaire sensor | - | HS3, H2 | - | Ja |
| Geheugenstoring regelaar | `binary_sensor.saj_inverter_fault_controller_memory` | Binaire sensor | - | HS3, H2 | - | Ja |
| CT-apparaatstoring | `binary_sensor.saj_inverter_fault_ct_device` | Binaire sensor | - | HS3 | - | Ja |
| Storing stroomsensor | `binary_sensor.saj_inverter_fault_current_sensor` | Binaire sensor | - | HS3, H2 | - | Ja |
| Storing DC-injectiesensor | `binary_sensor.saj_inverter_fault_dc_injection_device` | Binaire sensor | - | HS3, H2 | - | Ja |
| Communicatie met DC-DC-eenheid verloren | `binary_sensor.saj_inverter_fault_dcdc_communication` | Binaire sensor | - | HS3 | - | Ja |
| Storing DC-DC-eenheid | `binary_sensor.saj_inverter_fault_dcdc_device` | Binaire sensor | - | HS3 | - | Ja |
| Klokstoring displaybord | `binary_sensor.saj_inverter_fault_display_clock` | Binaire sensor | - | HS3, H2 | - | Ja |
| Communicatie met displaybord verloren | `binary_sensor.saj_inverter_fault_display_communication` | Binaire sensor | - | HS3, H2 | - | Ja |
| Geheugenstoring displaybord | `binary_sensor.saj_inverter_fault_display_memory` | Binaire sensor | - | HS3, H2 | - | Ja |
| DRM0-storing | `binary_sensor.saj_inverter_fault_drm0` | Binaire sensor | - | HS3, H2 | - | Ja |
| Communicatie met EV-lader verloren | `binary_sensor.saj_inverter_fault_ev_charger_communication` | Binaire sensor | - | HS3 | - | Ja |
| Storing ventilator 1 | `binary_sensor.saj_inverter_fault_fan_1` | Binaire sensor | - | HS3, H2 | - | Ja |
| Storing ventilator 2 | `binary_sensor.saj_inverter_fault_fan_2` | Binaire sensor | - | HS3, H2 | - | Ja |
| Storing ventilator 3 | `binary_sensor.saj_inverter_fault_fan_3` | Binaire sensor | - | HS3, H2 | - | Ja |
| Storing ventilator 4 | `binary_sensor.saj_inverter_fault_fan_4` | Binaire sensor | - | HS3, H2 | - | Ja |
| Overspanning 10-minutengemiddelde net | `binary_sensor.saj_inverter_fault_grid_average_overvoltage` | Binaire sensor | - | HS3, H2 | - | Ja |
| Net verloren | `binary_sensor.saj_inverter_fault_grid_lost` | Binaire sensor | - | HS3, H2 | - | Ja |
| Netoverfrequentie | `binary_sensor.saj_inverter_fault_grid_overfrequency` | Binaire sensor | - | HS3, H2 | - | Ja |
| Netfase R DC-injectie hoog | `binary_sensor.saj_inverter_fault_grid_phase_r_dc_injection` | Binaire sensor | - | HS3, H2 | - | Ja |
| Netfase R gelijkspanning hoog | `binary_sensor.saj_inverter_fault_grid_phase_r_dc_voltage` | Binaire sensor | - | HS3, H2 | - | Ja |
| Netfase R overspanning | `binary_sensor.saj_inverter_fault_grid_phase_r_overvoltage` | Binaire sensor | - | HS3, H2 | - | Ja |
| Netfase R onderspanning | `binary_sensor.saj_inverter_fault_grid_phase_r_undervoltage` | Binaire sensor | - | HS3, H2 | - | Ja |
| Netfase S DC-injectie hoog | `binary_sensor.saj_inverter_fault_grid_phase_s_dc_injection` | Binaire sensor | - | HS3, H2 | - | Ja |
| Netfase S gelijkspanning hoog | `binary_sensor.saj_inverter_fault_grid_phase_s_dc_voltage` | Binaire sensor | - | HS3, H2 | - | Ja |
| Netfase S overspanning | `binary_sensor.saj_inverter_fault_grid_phase_s_overvoltage` | Binaire sensor | - | HS3, H2 | - | Ja |
| Netfase S onderspanning | `binary_sensor.saj_inverter_fault_grid_phase_s_undervoltage` | Binaire sensor | - | HS3, H2 | - | Ja |
| Netfase T DC-injectie hoog | `binary_sensor.saj_inverter_fault_grid_phase_t_dc_injection` | Binaire sensor | - | HS3, H2 | - | Ja |
| Netfase T gelijkspanning hoog | `binary_sensor.saj_inverter_fault_grid_phase_t_dc_voltage` | Binaire sensor | - | HS3, H2 | - | Ja |
| Netfase T overspanning | `binary_sensor.saj_inverter_fault_grid_phase_t_overvoltage` | Binaire sensor | - | HS3, H2 | - | Ja |
| Netfase T onderspanning | `binary_sensor.saj_inverter_fault_grid_phase_t_undervoltage` | Binaire sensor | - | HS3, H2 | - | Ja |
| Netonderfrequentie | `binary_sensor.saj_inverter_fault_grid_underfrequency` | Binaire sensor | - | HS3, H2 | - | Ja |
| Hardware-overstroom omvormer | `binary_sensor.saj_inverter_fault_hardware_overcurrent` | Binaire sensor | - | HS3, H2 | - | Ja |
| Isolatiestoring | `binary_sensor.saj_inverter_fault_insulation` | Binaire sensor | - | HS3, H2 | - | Ja |
| Interne communicatie verloren | `binary_sensor.saj_inverter_fault_internal_communication` | Binaire sensor | - | HS3, H2 | - | Ja |
| Lekstroomstoring | `binary_sensor.saj_inverter_fault_leakage_current` | Binaire sensor | - | HS3, H2 | - | Ja |
| Storing lekstroomsensor | `binary_sensor.saj_inverter_fault_leakage_current_device` | Binaire sensor | - | HS3, H2 | - | Ja |
| Metercommunicatie verloren | `binary_sensor.saj_inverter_fault_meter_communication` | Binaire sensor | - | HS3, H2 | - | Ja |
| Storing spanning nulleider naar aarde | `binary_sensor.saj_inverter_fault_neutral_earth_voltage` | Binaire sensor | - | HS3, H2 | - | Ja |
| Off-griduitgang onderspanning | `binary_sensor.saj_inverter_fault_off_grid_undervoltage` | Binaire sensor | - | HS3, H2 | - | Ja |
| Uitgangsoverbelasting | `binary_sensor.saj_inverter_fault_output_overload` | Binaire sensor | - | HS3, H2 | - | Ja |
| Te hoge temperatuur | `binary_sensor.saj_inverter_fault_over_temperature` | Binaire sensor | - | HS3, H2 | - | Ja |
| Communicatie met parallel systeem verloren | `binary_sensor.saj_inverter_fault_parallel_communication` | Binaire sensor | - | HS3 | - | Ja |
| PV-hardware-overstroom | `binary_sensor.saj_inverter_fault_pv_hardware_overcurrent` | Binaire sensor | - | HS3, H2 | - | Ja |
| Storing PV-ingang | `binary_sensor.saj_inverter_fault_pv_input` | Binaire sensor | - | HS3, H2 | - | Ja |
| Storing PV-ingangsmodus | `binary_sensor.saj_inverter_fault_pv_input_mode` | Binaire sensor | - | HS3, H2 | - | Ja |
| Communicatie met zonnemeter verloren | `binary_sensor.saj_inverter_fault_pv_meter_communication` | Binaire sensor | - | HS3 | - | Ja |
| PV-overspanning | `binary_sensor.saj_inverter_fault_pv_overvoltage` | Binaire sensor | - | HS3, H2 | - | Ja |
| PV-software-overstroom | `binary_sensor.saj_inverter_fault_pv_software_overcurrent` | Binaire sensor | - | HS3, H2 | - | Ja |
| Relaisstoring | `binary_sensor.saj_inverter_fault_relay` | Binaire sensor | - | HS3, H2 | - | Ja |
| Communicatie met slave-regelaar verloren | `binary_sensor.saj_inverter_fault_slave_communication` | Binaire sensor | - | HS3 | - | Ja |
| Te lage temperatuur | `binary_sensor.saj_inverter_fault_under_temperature` | Binaire sensor | - | HS3, H2 | - | Ja |
| Niet-herkende omvormerstoring | `binary_sensor.saj_inverter_fault_unrecognised` | Binaire sensor | - | HS3, H2 | - | Ja |
| Batterijpack 2 storing | `binary_sensor.saj_battery_pack2_fault` | Binaire sensor | - | H2 | Batterij; Batterijpack 2 en hoger | Ja |
| Batterijpack 2 waarschuwing | `binary_sensor.saj_battery_pack2_warning` | Binaire sensor | - | H2 | Batterij; Batterijpack 2 en hoger | Ja |
| Batterijpack 3 storing | `binary_sensor.saj_battery_pack3_fault` | Binaire sensor | - | H2 | Batterij; Batterijpack 3 en hoger | Ja |
| Batterijpack 3 waarschuwing | `binary_sensor.saj_battery_pack3_warning` | Binaire sensor | - | H2 | Batterij; Batterijpack 3 en hoger | Ja |
| Batterijpack 4 storing | `binary_sensor.saj_battery_pack4_fault` | Binaire sensor | - | H2 | Batterij; Batterijpack 4 en hoger | Ja |
| Batterijpack 4 waarschuwing | `binary_sensor.saj_battery_pack4_warning` | Binaire sensor | - | H2 | Batterij; Batterijpack 4 en hoger | Ja |
| Overspanning DC-bus | `binary_sensor.saj_inverter_fault_bus_overvoltage` | Binaire sensor | - | H2 | - | Ja |
| Onderspanning DC-bus | `binary_sensor.saj_inverter_fault_bus_undervoltage` | Binaire sensor | - | H2 | - | Ja |
| Storing netfase | `binary_sensor.saj_inverter_fault_grid_phase` | Binaire sensor | - | H2 | - | Ja |
| Eilandvorming | `binary_sensor.saj_inverter_fault_islanding` | Binaire sensor | - | H2 | - | Ja |
