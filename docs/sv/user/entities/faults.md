[en](../../../en-gb/user/entities/faults.md) | [de](../../../de/user/entities/faults.md) | [nl](../../../nl/user/entities/faults.md) | [fr](../../../fr/user/entities/faults.md) | [zh](../../../zh-hans/user/entities/faults.md) | [es](../../../es/user/entities/faults.md) | [it](../../../it/user/entities/faults.md) | [pl](../../../pl/user/entities/faults.md) | sv

# Fel

Fel som växelriktaren, batteriet och elbilsladdaren rapporterar.

Integrationens funktionslista förklarar entiteterna för Fel i [Enhetsfel och reparationer](../../../../custom_components/saj_local/docs/features.md#device-faults-and-repairs).

139 entiteter. Genereras av `make docs`. Redigera inte för hand.

Ett prefix som anges i Konfigurera hamnar efter `saj_` i ID:t för varje entitet i Fel, till exempel `binary_sensor.saj_house_battery_pack1_fault` med prefixet `house`.

| Namn | Entitets-ID | Typ | Enhet | Modeller | Utrustning och antal | Aktiverad som standard |
| --- | --- | --- | --- | --- | --- | --- |
| Batteripack 1 fel | `binary_sensor.saj_battery_pack1_fault` | Binär sensor | - | HS3, H2 | Batteri | Ja |
| Batteripack 1 varning | `binary_sensor.saj_battery_pack1_warning` | Binär sensor | - | HS3, H2 | Batteri | Ja |
| Batterifel | `binary_sensor.saj_battery_fault` | Binär sensor | - | HS3, H2 | Batteri | Ja |
| Batteriets BMS-tillverkare inkompatibel | `binary_sensor.saj_battery_fault_bms_incompatible` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriets kretsbrytare öppen | `binary_sensor.saj_battery_fault_breaker_open` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriets celler stämmer inte | `binary_sensor.saj_battery_fault_cell_incompatible` | Binär sensor | - | HS3 | Batteri | Ja |
| Battericell övertemperatur | `binary_sensor.saj_battery_fault_cell_over_temperature` | Binär sensor | - | HS3 | Batteri | Ja |
| Battericell överspänning | `binary_sensor.saj_battery_fault_cell_overvoltage` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriets celltillverkare stämmer inte | `binary_sensor.saj_battery_fault_cell_supplier_incompatible` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriets celltemperaturskillnad för stor | `binary_sensor.saj_battery_fault_cell_temperature_difference` | Binär sensor | - | HS3 | Batteri | Ja |
| Battericell underspänning | `binary_sensor.saj_battery_fault_cell_undervoltage` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriets cellspänningsskillnad för stor, nivå 1 | `binary_sensor.saj_battery_fault_cell_voltage_difference_1` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriets cellspänningsskillnad för stor, nivå 2 | `binary_sensor.saj_battery_fault_cell_voltage_difference_2` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriet för kallt för laddning | `binary_sensor.saj_battery_fault_charge_cold` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriet för varmt för laddning | `binary_sensor.saj_battery_fault_charge_hot` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriladdningsöverström | `binary_sensor.saj_battery_fault_charge_overcurrent` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriets laddningsport överspänning | `binary_sensor.saj_battery_fault_charging_port_overvoltage` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriet för kallt för urladdning | `binary_sensor.saj_battery_fault_discharge_cold` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriet för varmt för urladdning | `binary_sensor.saj_battery_fault_discharge_hot` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriurladdningsöverström | `binary_sensor.saj_battery_fault_discharge_overcurrent` | Binär sensor | - | HS3 | Batteri | Ja |
| Batterisäkringsfel | `binary_sensor.saj_battery_fault_fuse` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriets BMS maskinvarufel | `binary_sensor.saj_battery_fault_hardware` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriets BMS isolationsfel | `binary_sensor.saj_battery_fault_insulation` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriets interna BMS-kommunikation förlorad | `binary_sensor.saj_battery_fault_internal_communication` | Binär sensor | - | HS3 | Batteri | Ja |
| Fel i batteripackets adressering | `binary_sensor.saj_battery_fault_pack_sequence` | Binär sensor | - | HS3 | Batteri | Ja |
| Fel i batteriets förladdning | `binary_sensor.saj_battery_fault_precharge` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriets BMS reläfel | `binary_sensor.saj_battery_fault_relay` | Binär sensor | - | HS3 | Batteri | Ja |
| Batterikortslutning | `binary_sensor.saj_battery_fault_short_circuit` | Binär sensor | - | HS3 | Batteri | Ja |
| Batterisystem låst | `binary_sensor.saj_battery_fault_system_locked` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriets totalspänning hög | `binary_sensor.saj_battery_fault_total_overvoltage` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriets totalspänning låg | `binary_sensor.saj_battery_fault_total_undervoltage` | Binär sensor | - | HS3 | Batteri | Ja |
| Batteriets totalspänning kunde inte matchas | `binary_sensor.saj_battery_fault_total_voltage_matching` | Binär sensor | - | HS3 | Batteri | Ja |
| Okänt batterifel | `binary_sensor.saj_battery_fault_unrecognised` | Binär sensor | - | HS3, H2 | Batteri | Ja |
| Batteriets spänningsnivå stämmer inte | `binary_sensor.saj_battery_fault_voltage_level_mismatch` | Binär sensor | - | HS3 | Batteri | Ja |
| Elbilsladdarfel | `binary_sensor.saj_ev_fault` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens AC-överström | `binary_sensor.saj_ev_fault_ac_overcurrent` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens AC-överfrekvens | `binary_sensor.saj_ev_fault_ac_overfrequency` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens AC-överspänning | `binary_sensor.saj_ev_fault_ac_overvoltage` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens AC-restström | `binary_sensor.saj_ev_fault_ac_residual_current` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens AC-underfrekvens | `binary_sensor.saj_ev_fault_ac_underfrequency` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens AC-underspänning | `binary_sensor.saj_ev_fault_ac_undervoltage` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens Bluetooth-fel | `binary_sensor.saj_ev_fault_bluetooth` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens fel i kontaktströmmen | `binary_sensor.saj_ev_fault_connector_current` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens fel i kontaktlåset | `binary_sensor.saj_ev_fault_connector_lock` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens pilotsignalfel (under 2 V) | `binary_sensor.saj_ev_fault_control_pilot` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens DC-restströmsfel A | `binary_sensor.saj_ev_fault_dc_residual_current_a` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens DC-restströmsfel B | `binary_sensor.saj_ev_fault_dc_residual_current_b` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens DC-restströmsfel C | `binary_sensor.saj_ev_fault_dc_residual_current_c` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens nödstopp | `binary_sensor.saj_ev_fault_emergency_stop` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens jordningsfel | `binary_sensor.saj_ev_fault_grounding` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens ingångsplint övertemperatur | `binary_sensor.saj_ev_fault_input_terminal_over_temperature` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens mätarfel | `binary_sensor.saj_ev_fault_meter` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens överbelastning | `binary_sensor.saj_ev_fault_overload` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens fasföljdsfel | `binary_sensor.saj_ev_fault_phase_sequence` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens fel i jordfelsbrytarkretsen | `binary_sensor.saj_ev_fault_rcd_circuit` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens reläfel | `binary_sensor.saj_ev_fault_relay` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens relä övertemperatur | `binary_sensor.saj_ev_fault_relay_over_temperature` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens tidsgräns för RS485-kommunikation | `binary_sensor.saj_ev_fault_rs485_timeout` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens fel i elförsörjningen | `binary_sensor.saj_ev_fault_supply` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Elbilsladdarens undertemperatur | `binary_sensor.saj_ev_fault_under_temperature` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Okänt elbilsladdarfel | `binary_sensor.saj_ev_fault_unrecognised` | Binär sensor | - | HS3 | Elbilsladdare | Ja |
| Växelriktarfel | `binary_sensor.saj_inverter_fault` | Binär sensor | - | HS3, H2 | - | Ja |
| Kommunikation med ljusbågskortet förlorad | `binary_sensor.saj_inverter_fault_afci_communication` | Binär sensor | - | HS3 | - | Ja |
| Ljusbågsfel | `binary_sensor.saj_inverter_fault_arc` | Binär sensor | - | HS3, H2 | - | Ja |
| Fel på ljusbågsdetektorn | `binary_sensor.saj_inverter_fault_arc_device` | Binär sensor | - | HS3 | - | Ja |
| Auktorisering utgången | `binary_sensor.saj_inverter_fault_authorisation_expired` | Binär sensor | - | HS3, H2 | - | Ja |
| Batteriets laddningsspänning hög | `binary_sensor.saj_inverter_fault_battery_charge_overvoltage` | Binär sensor | - | HS3, H2 | - | Ja |
| Batteriets urladdningsspänning låg | `binary_sensor.saj_inverter_fault_battery_discharge_undervoltage` | Binär sensor | - | HS3, H2 | - | Ja |
| Batteri bruten krets | `binary_sensor.saj_inverter_fault_battery_open_circuit` | Binär sensor | - | HS3, H2 | - | Ja |
| Batteriport överström | `binary_sensor.saj_inverter_fault_battery_overcurrent` | Binär sensor | - | HS3, H2 | - | Ja |
| Batteriport överbelastning | `binary_sensor.saj_inverter_fault_battery_overload` | Binär sensor | - | HS3, H2 | - | Ja |
| Batteriport överspänning | `binary_sensor.saj_inverter_fault_battery_overvoltage` | Binär sensor | - | HS3, H2 | - | Ja |
| Tidsgräns för batteriets mjukstart | `binary_sensor.saj_inverter_fault_battery_soft_start` | Binär sensor | - | HS3, H2 | - | Ja |
| Kommunikation med BMS förlorad | `binary_sensor.saj_inverter_fault_bms_communication` | Binär sensor | - | HS3, H2 | - | Ja |
| BMS-enhetsfel | `binary_sensor.saj_inverter_fault_bms_device` | Binär sensor | - | HS3, H2 | - | Ja |
| DC-bussmaskinvaruöverspänning | `binary_sensor.saj_inverter_fault_bus_hardware_overvoltage` | Binär sensor | - | HS3, H2 | - | Ja |
| Obalans i DC-busspänning | `binary_sensor.saj_inverter_fault_bus_imbalance` | Binär sensor | - | HS3, H2 | - | Ja |
| Minnesfel i styrenheten | `binary_sensor.saj_inverter_fault_controller_memory` | Binär sensor | - | HS3, H2 | - | Ja |
| CT-enhetsfel | `binary_sensor.saj_inverter_fault_ct_device` | Binär sensor | - | HS3 | - | Ja |
| Strömsensorfel | `binary_sensor.saj_inverter_fault_current_sensor` | Binär sensor | - | HS3, H2 | - | Ja |
| Fel på sensorn för likströmsinmatning | `binary_sensor.saj_inverter_fault_dc_injection_device` | Binär sensor | - | HS3, H2 | - | Ja |
| Kommunikation med DC-DC-enheten förlorad | `binary_sensor.saj_inverter_fault_dcdc_communication` | Binär sensor | - | HS3 | - | Ja |
| DC-DC-enhetsfel | `binary_sensor.saj_inverter_fault_dcdc_device` | Binär sensor | - | HS3 | - | Ja |
| Klockfel på displaykortet | `binary_sensor.saj_inverter_fault_display_clock` | Binär sensor | - | HS3, H2 | - | Ja |
| Kommunikation med displaykortet förlorad | `binary_sensor.saj_inverter_fault_display_communication` | Binär sensor | - | HS3, H2 | - | Ja |
| Minnesfel på displaykortet | `binary_sensor.saj_inverter_fault_display_memory` | Binär sensor | - | HS3, H2 | - | Ja |
| DRM0-fel | `binary_sensor.saj_inverter_fault_drm0` | Binär sensor | - | HS3, H2 | - | Ja |
| Kommunikation med elbilsladdaren förlorad | `binary_sensor.saj_inverter_fault_ev_charger_communication` | Binär sensor | - | HS3 | - | Ja |
| Fläkt 1 fel | `binary_sensor.saj_inverter_fault_fan_1` | Binär sensor | - | HS3, H2 | - | Ja |
| Fläkt 2 fel | `binary_sensor.saj_inverter_fault_fan_2` | Binär sensor | - | HS3, H2 | - | Ja |
| Fläkt 3 fel | `binary_sensor.saj_inverter_fault_fan_3` | Binär sensor | - | HS3, H2 | - | Ja |
| Fläkt 4 fel | `binary_sensor.saj_inverter_fault_fan_4` | Binär sensor | - | HS3, H2 | - | Ja |
| Nät 10-minuters medelvärde överspänning | `binary_sensor.saj_inverter_fault_grid_average_overvoltage` | Binär sensor | - | HS3, H2 | - | Ja |
| Nätet förlorat | `binary_sensor.saj_inverter_fault_grid_lost` | Binär sensor | - | HS3, H2 | - | Ja |
| Nätöverfrekvens | `binary_sensor.saj_inverter_fault_grid_overfrequency` | Binär sensor | - | HS3, H2 | - | Ja |
| Nätfas R likströmsinmatning hög | `binary_sensor.saj_inverter_fault_grid_phase_r_dc_injection` | Binär sensor | - | HS3, H2 | - | Ja |
| Nätfas R likspänning hög | `binary_sensor.saj_inverter_fault_grid_phase_r_dc_voltage` | Binär sensor | - | HS3, H2 | - | Ja |
| Nätfas R överspänning | `binary_sensor.saj_inverter_fault_grid_phase_r_overvoltage` | Binär sensor | - | HS3, H2 | - | Ja |
| Nätfas R underspänning | `binary_sensor.saj_inverter_fault_grid_phase_r_undervoltage` | Binär sensor | - | HS3, H2 | - | Ja |
| Nätfas S likströmsinmatning hög | `binary_sensor.saj_inverter_fault_grid_phase_s_dc_injection` | Binär sensor | - | HS3, H2 | - | Ja |
| Nätfas S likspänning hög | `binary_sensor.saj_inverter_fault_grid_phase_s_dc_voltage` | Binär sensor | - | HS3, H2 | - | Ja |
| Nätfas S överspänning | `binary_sensor.saj_inverter_fault_grid_phase_s_overvoltage` | Binär sensor | - | HS3, H2 | - | Ja |
| Nätfas S underspänning | `binary_sensor.saj_inverter_fault_grid_phase_s_undervoltage` | Binär sensor | - | HS3, H2 | - | Ja |
| Nätfas T likströmsinmatning hög | `binary_sensor.saj_inverter_fault_grid_phase_t_dc_injection` | Binär sensor | - | HS3, H2 | - | Ja |
| Nätfas T likspänning hög | `binary_sensor.saj_inverter_fault_grid_phase_t_dc_voltage` | Binär sensor | - | HS3, H2 | - | Ja |
| Nätfas T överspänning | `binary_sensor.saj_inverter_fault_grid_phase_t_overvoltage` | Binär sensor | - | HS3, H2 | - | Ja |
| Nätfas T underspänning | `binary_sensor.saj_inverter_fault_grid_phase_t_undervoltage` | Binär sensor | - | HS3, H2 | - | Ja |
| Nätunderfrekvens | `binary_sensor.saj_inverter_fault_grid_underfrequency` | Binär sensor | - | HS3, H2 | - | Ja |
| Maskinvaruöverström växelriktare | `binary_sensor.saj_inverter_fault_hardware_overcurrent` | Binär sensor | - | HS3, H2 | - | Ja |
| Isolationsfel | `binary_sensor.saj_inverter_fault_insulation` | Binär sensor | - | HS3, H2 | - | Ja |
| Intern kommunikation förlorad | `binary_sensor.saj_inverter_fault_internal_communication` | Binär sensor | - | HS3, H2 | - | Ja |
| Läckströmsfel | `binary_sensor.saj_inverter_fault_leakage_current` | Binär sensor | - | HS3, H2 | - | Ja |
| Fel på läckströmssensorn | `binary_sensor.saj_inverter_fault_leakage_current_device` | Binär sensor | - | HS3, H2 | - | Ja |
| Kommunikation med mätare förlorad | `binary_sensor.saj_inverter_fault_meter_communication` | Binär sensor | - | HS3, H2 | - | Ja |
| Fel i spänning mellan nolla och jord | `binary_sensor.saj_inverter_fault_neutral_earth_voltage` | Binär sensor | - | HS3, H2 | - | Ja |
| Fristående utgång underspänning | `binary_sensor.saj_inverter_fault_off_grid_undervoltage` | Binär sensor | - | HS3, H2 | - | Ja |
| Utgång överbelastad | `binary_sensor.saj_inverter_fault_output_overload` | Binär sensor | - | HS3, H2 | - | Ja |
| Övertemperatur | `binary_sensor.saj_inverter_fault_over_temperature` | Binär sensor | - | HS3, H2 | - | Ja |
| Kommunikation i parallellsystemet förlorad | `binary_sensor.saj_inverter_fault_parallel_communication` | Binär sensor | - | HS3 | - | Ja |
| PV maskinvaruöverström | `binary_sensor.saj_inverter_fault_pv_hardware_overcurrent` | Binär sensor | - | HS3, H2 | - | Ja |
| PV-ingångsfel | `binary_sensor.saj_inverter_fault_pv_input` | Binär sensor | - | HS3, H2 | - | Ja |
| Fel i PV-ingångsläge | `binary_sensor.saj_inverter_fault_pv_input_mode` | Binär sensor | - | HS3, H2 | - | Ja |
| Kommunikation med solmätaren förlorad | `binary_sensor.saj_inverter_fault_pv_meter_communication` | Binär sensor | - | HS3 | - | Ja |
| PV överspänning | `binary_sensor.saj_inverter_fault_pv_overvoltage` | Binär sensor | - | HS3, H2 | - | Ja |
| PV programvaruöverström | `binary_sensor.saj_inverter_fault_pv_software_overcurrent` | Binär sensor | - | HS3, H2 | - | Ja |
| Reläfel | `binary_sensor.saj_inverter_fault_relay` | Binär sensor | - | HS3, H2 | - | Ja |
| Kommunikation med slavstyrenheten förlorad | `binary_sensor.saj_inverter_fault_slave_communication` | Binär sensor | - | HS3 | - | Ja |
| Undertemperatur | `binary_sensor.saj_inverter_fault_under_temperature` | Binär sensor | - | HS3, H2 | - | Ja |
| Okänt växelriktarfel | `binary_sensor.saj_inverter_fault_unrecognised` | Binär sensor | - | HS3, H2 | - | Ja |
| Batteripack 2 fel | `binary_sensor.saj_battery_pack2_fault` | Binär sensor | - | H2 | Batteri; Batteripack 2 och högre | Ja |
| Batteripack 2 varning | `binary_sensor.saj_battery_pack2_warning` | Binär sensor | - | H2 | Batteri; Batteripack 2 och högre | Ja |
| Batteripack 3 fel | `binary_sensor.saj_battery_pack3_fault` | Binär sensor | - | H2 | Batteri; Batteripack 3 och högre | Ja |
| Batteripack 3 varning | `binary_sensor.saj_battery_pack3_warning` | Binär sensor | - | H2 | Batteri; Batteripack 3 och högre | Ja |
| Batteripack 4 fel | `binary_sensor.saj_battery_pack4_fault` | Binär sensor | - | H2 | Batteri; Batteripack 4 och högre | Ja |
| Batteripack 4 varning | `binary_sensor.saj_battery_pack4_warning` | Binär sensor | - | H2 | Batteri; Batteripack 4 och högre | Ja |
| DC-bussöverspänning | `binary_sensor.saj_inverter_fault_bus_overvoltage` | Binär sensor | - | H2 | - | Ja |
| DC-bussunderspänning | `binary_sensor.saj_inverter_fault_bus_undervoltage` | Binär sensor | - | H2 | - | Ja |
| Nätfasfel | `binary_sensor.saj_inverter_fault_grid_phase` | Binär sensor | - | H2 | - | Ja |
| Ödrift | `binary_sensor.saj_inverter_fault_islanding` | Binär sensor | - | H2 | - | Ja |
