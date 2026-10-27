[en](../../../en-gb/user/entities/faults.md) | [de](../../../de/user/entities/faults.md) | [nl](../../../nl/user/entities/faults.md) | [fr](../../../fr/user/entities/faults.md) | [zh](../../../zh-hans/user/entities/faults.md) | es | [it](../../../it/user/entities/faults.md) | [pl](../../../pl/user/entities/faults.md) | [sv](../../../sv/user/entities/faults.md)

# Fallos

Fallos que informan el inversor, la batería y el cargador de VE.

La lista de funciones de la integración explica las entidades de Fallos en [Fallos del dispositivo y reparaciones](../../../../custom_components/saj_local/docs/features.md#device-faults-and-repairs).

139 entidades. Generado por `make docs`. No editar a mano.

Un prefijo definido en Configurar va después de `saj_` en el ID de cada entidad de Fallos, por ejemplo `binary_sensor.saj_house_battery_pack1_fault` con el prefijo `house`.

| Nombre | ID de entidad | Tipo | Unidad | Modelos | Equipo y números | Habilitada por defecto |
| --- | --- | --- | --- | --- | --- | --- |
| Fallo del módulo de batería 1 | `binary_sensor.saj_battery_pack1_fault` | Sensor binario | - | HS3, H2 | Batería | Sí |
| Aviso del módulo de batería 1 | `binary_sensor.saj_battery_pack1_warning` | Sensor binario | - | HS3, H2 | Batería | Sí |
| Fallo de la batería | `binary_sensor.saj_battery_fault` | Sensor binario | - | HS3, H2 | Batería | Sí |
| Fabricante del BMS de la batería incompatible | `binary_sensor.saj_battery_fault_bms_incompatible` | Sensor binario | - | HS3 | Batería | Sí |
| Disyuntor de la batería abierto | `binary_sensor.saj_battery_fault_breaker_open` | Sensor binario | - | HS3 | Batería | Sí |
| Celdas de la batería no coinciden | `binary_sensor.saj_battery_fault_cell_incompatible` | Sensor binario | - | HS3 | Batería | Sí |
| Temperatura de celda de la batería demasiado alta | `binary_sensor.saj_battery_fault_cell_over_temperature` | Sensor binario | - | HS3 | Batería | Sí |
| Sobretensión de celda de la batería | `binary_sensor.saj_battery_fault_cell_overvoltage` | Sensor binario | - | HS3 | Batería | Sí |
| Fabricante de celdas de la batería no coincide | `binary_sensor.saj_battery_fault_cell_supplier_incompatible` | Sensor binario | - | HS3 | Batería | Sí |
| Diferencia de temperatura entre celdas de la batería demasiado grande | `binary_sensor.saj_battery_fault_cell_temperature_difference` | Sensor binario | - | HS3 | Batería | Sí |
| Subtensión de celda de la batería | `binary_sensor.saj_battery_fault_cell_undervoltage` | Sensor binario | - | HS3 | Batería | Sí |
| Diferencia de tensión entre celdas de la batería demasiado grande, nivel 1 | `binary_sensor.saj_battery_fault_cell_voltage_difference_1` | Sensor binario | - | HS3 | Batería | Sí |
| Diferencia de tensión entre celdas de la batería demasiado grande, nivel 2 | `binary_sensor.saj_battery_fault_cell_voltage_difference_2` | Sensor binario | - | HS3 | Batería | Sí |
| Batería demasiado fría para cargar | `binary_sensor.saj_battery_fault_charge_cold` | Sensor binario | - | HS3 | Batería | Sí |
| Batería demasiado caliente para cargar | `binary_sensor.saj_battery_fault_charge_hot` | Sensor binario | - | HS3 | Batería | Sí |
| Sobrecorriente de carga de la batería | `binary_sensor.saj_battery_fault_charge_overcurrent` | Sensor binario | - | HS3 | Batería | Sí |
| Sobretensión del puerto de carga de la batería | `binary_sensor.saj_battery_fault_charging_port_overvoltage` | Sensor binario | - | HS3 | Batería | Sí |
| Batería demasiado fría para descargar | `binary_sensor.saj_battery_fault_discharge_cold` | Sensor binario | - | HS3 | Batería | Sí |
| Batería demasiado caliente para descargar | `binary_sensor.saj_battery_fault_discharge_hot` | Sensor binario | - | HS3 | Batería | Sí |
| Sobrecorriente de descarga de la batería | `binary_sensor.saj_battery_fault_discharge_overcurrent` | Sensor binario | - | HS3 | Batería | Sí |
| Fallo del fusible de la batería | `binary_sensor.saj_battery_fault_fuse` | Sensor binario | - | HS3 | Batería | Sí |
| Fallo de hardware del BMS de la batería | `binary_sensor.saj_battery_fault_hardware` | Sensor binario | - | HS3 | Batería | Sí |
| Fallo de aislamiento del BMS de la batería | `binary_sensor.saj_battery_fault_insulation` | Sensor binario | - | HS3 | Batería | Sí |
| Comunicación interna del BMS de la batería perdida | `binary_sensor.saj_battery_fault_internal_communication` | Sensor binario | - | HS3 | Batería | Sí |
| Fallo de direccionamiento de módulos de la batería | `binary_sensor.saj_battery_fault_pack_sequence` | Sensor binario | - | HS3 | Batería | Sí |
| Fallo de precarga de la batería | `binary_sensor.saj_battery_fault_precharge` | Sensor binario | - | HS3 | Batería | Sí |
| Fallo del relé del BMS de la batería | `binary_sensor.saj_battery_fault_relay` | Sensor binario | - | HS3 | Batería | Sí |
| Cortocircuito de la batería | `binary_sensor.saj_battery_fault_short_circuit` | Sensor binario | - | HS3 | Batería | Sí |
| Sistema de la batería bloqueado | `binary_sensor.saj_battery_fault_system_locked` | Sensor binario | - | HS3 | Batería | Sí |
| Tensión total de la batería alta | `binary_sensor.saj_battery_fault_total_overvoltage` | Sensor binario | - | HS3 | Batería | Sí |
| Tensión total de la batería baja | `binary_sensor.saj_battery_fault_total_undervoltage` | Sensor binario | - | HS3 | Batería | Sí |
| Fallo de coincidencia de la tensión total de la batería | `binary_sensor.saj_battery_fault_total_voltage_matching` | Sensor binario | - | HS3 | Batería | Sí |
| Fallo no reconocido de la batería | `binary_sensor.saj_battery_fault_unrecognised` | Sensor binario | - | HS3, H2 | Batería | Sí |
| Nivel de tensión de la batería no coincide | `binary_sensor.saj_battery_fault_voltage_level_mismatch` | Sensor binario | - | HS3 | Batería | Sí |
| Fallo del cargador de VE | `binary_sensor.saj_ev_fault` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Sobrecorriente de CA del cargador de VE | `binary_sensor.saj_ev_fault_ac_overcurrent` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Sobrefrecuencia de CA del cargador de VE | `binary_sensor.saj_ev_fault_ac_overfrequency` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Sobretensión de CA del cargador de VE | `binary_sensor.saj_ev_fault_ac_overvoltage` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Corriente residual de CA del cargador de VE | `binary_sensor.saj_ev_fault_ac_residual_current` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Subfrecuencia de CA del cargador de VE | `binary_sensor.saj_ev_fault_ac_underfrequency` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Subtensión de CA del cargador de VE | `binary_sensor.saj_ev_fault_ac_undervoltage` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Fallo de Bluetooth del cargador de VE | `binary_sensor.saj_ev_fault_bluetooth` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Fallo de corriente del conector del cargador de VE | `binary_sensor.saj_ev_fault_connector_current` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Fallo del bloqueo del conector del cargador de VE | `binary_sensor.saj_ev_fault_connector_lock` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Fallo del piloto de control del cargador de VE (por debajo de 2 V) | `binary_sensor.saj_ev_fault_control_pilot` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Fallo A de corriente residual de CC del cargador de VE | `binary_sensor.saj_ev_fault_dc_residual_current_a` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Fallo B de corriente residual de CC del cargador de VE | `binary_sensor.saj_ev_fault_dc_residual_current_b` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Fallo C de corriente residual de CC del cargador de VE | `binary_sensor.saj_ev_fault_dc_residual_current_c` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Parada de emergencia del cargador de VE | `binary_sensor.saj_ev_fault_emergency_stop` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Fallo de puesta a tierra del cargador de VE | `binary_sensor.saj_ev_fault_grounding` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Temperatura del terminal de entrada del cargador de VE demasiado alta | `binary_sensor.saj_ev_fault_input_terminal_over_temperature` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Fallo del contador del cargador de VE | `binary_sensor.saj_ev_fault_meter` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Sobrecarga del cargador de VE | `binary_sensor.saj_ev_fault_overload` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Fallo de secuencia de fases del cargador de VE | `binary_sensor.saj_ev_fault_phase_sequence` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Fallo del circuito RCD del cargador de VE | `binary_sensor.saj_ev_fault_rcd_circuit` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Fallo del relé del cargador de VE | `binary_sensor.saj_ev_fault_relay` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Temperatura del relé del cargador de VE demasiado alta | `binary_sensor.saj_ev_fault_relay_over_temperature` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Tiempo de espera de comunicación RS485 del cargador de VE agotado | `binary_sensor.saj_ev_fault_rs485_timeout` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Fallo de suministro eléctrico del cargador de VE | `binary_sensor.saj_ev_fault_supply` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Temperatura del cargador de VE demasiado baja | `binary_sensor.saj_ev_fault_under_temperature` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Fallo no reconocido del cargador de VE | `binary_sensor.saj_ev_fault_unrecognised` | Sensor binario | - | HS3 | Cargador de VE | Sí |
| Fallo del inversor | `binary_sensor.saj_inverter_fault` | Sensor binario | - | HS3, H2 | - | Sí |
| Comunicación con la placa de detección de arco perdida | `binary_sensor.saj_inverter_fault_afci_communication` | Sensor binario | - | HS3 | - | Sí |
| Fallo de arco | `binary_sensor.saj_inverter_fault_arc` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo del dispositivo de detección de arco | `binary_sensor.saj_inverter_fault_arc_device` | Sensor binario | - | HS3 | - | Sí |
| Autorización caducada | `binary_sensor.saj_inverter_fault_authorisation_expired` | Sensor binario | - | HS3, H2 | - | Sí |
| Tensión de carga de la batería alta | `binary_sensor.saj_inverter_fault_battery_charge_overvoltage` | Sensor binario | - | HS3, H2 | - | Sí |
| Tensión de descarga de la batería baja | `binary_sensor.saj_inverter_fault_battery_discharge_undervoltage` | Sensor binario | - | HS3, H2 | - | Sí |
| Circuito abierto de la batería | `binary_sensor.saj_inverter_fault_battery_open_circuit` | Sensor binario | - | HS3, H2 | - | Sí |
| Sobrecorriente del puerto de la batería | `binary_sensor.saj_inverter_fault_battery_overcurrent` | Sensor binario | - | HS3, H2 | - | Sí |
| Sobrecarga del puerto de la batería | `binary_sensor.saj_inverter_fault_battery_overload` | Sensor binario | - | HS3, H2 | - | Sí |
| Sobretensión del puerto de la batería | `binary_sensor.saj_inverter_fault_battery_overvoltage` | Sensor binario | - | HS3, H2 | - | Sí |
| Tiempo de arranque suave de la batería agotado | `binary_sensor.saj_inverter_fault_battery_soft_start` | Sensor binario | - | HS3, H2 | - | Sí |
| Comunicación con el BMS perdida | `binary_sensor.saj_inverter_fault_bms_communication` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo del dispositivo BMS | `binary_sensor.saj_inverter_fault_bms_device` | Sensor binario | - | HS3, H2 | - | Sí |
| Sobretensión de hardware del bus de CC | `binary_sensor.saj_inverter_fault_bus_hardware_overvoltage` | Sensor binario | - | HS3, H2 | - | Sí |
| Desequilibrio de tensión del bus de CC | `binary_sensor.saj_inverter_fault_bus_imbalance` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo de memoria del controlador | `binary_sensor.saj_inverter_fault_controller_memory` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo del dispositivo CT | `binary_sensor.saj_inverter_fault_ct_device` | Sensor binario | - | HS3 | - | Sí |
| Fallo del sensor de corriente | `binary_sensor.saj_inverter_fault_current_sensor` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo del sensor de inyección de CC | `binary_sensor.saj_inverter_fault_dc_injection_device` | Sensor binario | - | HS3, H2 | - | Sí |
| Comunicación con la unidad CC-CC perdida | `binary_sensor.saj_inverter_fault_dcdc_communication` | Sensor binario | - | HS3 | - | Sí |
| Fallo de la unidad CC-CC | `binary_sensor.saj_inverter_fault_dcdc_device` | Sensor binario | - | HS3 | - | Sí |
| Fallo del reloj de la placa de pantalla | `binary_sensor.saj_inverter_fault_display_clock` | Sensor binario | - | HS3, H2 | - | Sí |
| Comunicación con la placa de pantalla perdida | `binary_sensor.saj_inverter_fault_display_communication` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo de memoria de la placa de pantalla | `binary_sensor.saj_inverter_fault_display_memory` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo DRM0 | `binary_sensor.saj_inverter_fault_drm0` | Sensor binario | - | HS3, H2 | - | Sí |
| Comunicación con el cargador de VE perdida | `binary_sensor.saj_inverter_fault_ev_charger_communication` | Sensor binario | - | HS3 | - | Sí |
| Fallo del ventilador 1 | `binary_sensor.saj_inverter_fault_fan_1` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo del ventilador 2 | `binary_sensor.saj_inverter_fault_fan_2` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo del ventilador 3 | `binary_sensor.saj_inverter_fault_fan_3` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo del ventilador 4 | `binary_sensor.saj_inverter_fault_fan_4` | Sensor binario | - | HS3, H2 | - | Sí |
| Sobretensión media de 10 minutos de la red | `binary_sensor.saj_inverter_fault_grid_average_overvoltage` | Sensor binario | - | HS3, H2 | - | Sí |
| Pérdida de la red | `binary_sensor.saj_inverter_fault_grid_lost` | Sensor binario | - | HS3, H2 | - | Sí |
| Sobrefrecuencia de la red | `binary_sensor.saj_inverter_fault_grid_overfrequency` | Sensor binario | - | HS3, H2 | - | Sí |
| Inyección de CC alta en la fase R de la red | `binary_sensor.saj_inverter_fault_grid_phase_r_dc_injection` | Sensor binario | - | HS3, H2 | - | Sí |
| Tensión continua alta en la fase R de la red | `binary_sensor.saj_inverter_fault_grid_phase_r_dc_voltage` | Sensor binario | - | HS3, H2 | - | Sí |
| Sobretensión en la fase R de la red | `binary_sensor.saj_inverter_fault_grid_phase_r_overvoltage` | Sensor binario | - | HS3, H2 | - | Sí |
| Subtensión en la fase R de la red | `binary_sensor.saj_inverter_fault_grid_phase_r_undervoltage` | Sensor binario | - | HS3, H2 | - | Sí |
| Inyección de CC alta en la fase S de la red | `binary_sensor.saj_inverter_fault_grid_phase_s_dc_injection` | Sensor binario | - | HS3, H2 | - | Sí |
| Tensión continua alta en la fase S de la red | `binary_sensor.saj_inverter_fault_grid_phase_s_dc_voltage` | Sensor binario | - | HS3, H2 | - | Sí |
| Sobretensión en la fase S de la red | `binary_sensor.saj_inverter_fault_grid_phase_s_overvoltage` | Sensor binario | - | HS3, H2 | - | Sí |
| Subtensión en la fase S de la red | `binary_sensor.saj_inverter_fault_grid_phase_s_undervoltage` | Sensor binario | - | HS3, H2 | - | Sí |
| Inyección de CC alta en la fase T de la red | `binary_sensor.saj_inverter_fault_grid_phase_t_dc_injection` | Sensor binario | - | HS3, H2 | - | Sí |
| Tensión continua alta en la fase T de la red | `binary_sensor.saj_inverter_fault_grid_phase_t_dc_voltage` | Sensor binario | - | HS3, H2 | - | Sí |
| Sobretensión en la fase T de la red | `binary_sensor.saj_inverter_fault_grid_phase_t_overvoltage` | Sensor binario | - | HS3, H2 | - | Sí |
| Subtensión en la fase T de la red | `binary_sensor.saj_inverter_fault_grid_phase_t_undervoltage` | Sensor binario | - | HS3, H2 | - | Sí |
| Subfrecuencia de la red | `binary_sensor.saj_inverter_fault_grid_underfrequency` | Sensor binario | - | HS3, H2 | - | Sí |
| Sobrecorriente de hardware del inversor | `binary_sensor.saj_inverter_fault_hardware_overcurrent` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo de aislamiento | `binary_sensor.saj_inverter_fault_insulation` | Sensor binario | - | HS3, H2 | - | Sí |
| Comunicación interna perdida | `binary_sensor.saj_inverter_fault_internal_communication` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo de corriente de fuga | `binary_sensor.saj_inverter_fault_leakage_current` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo del sensor de corriente de fuga | `binary_sensor.saj_inverter_fault_leakage_current_device` | Sensor binario | - | HS3, H2 | - | Sí |
| Comunicación con el contador perdida | `binary_sensor.saj_inverter_fault_meter_communication` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo de tensión neutro-tierra | `binary_sensor.saj_inverter_fault_neutral_earth_voltage` | Sensor binario | - | HS3, H2 | - | Sí |
| Subtensión de la salida aislada de la red | `binary_sensor.saj_inverter_fault_off_grid_undervoltage` | Sensor binario | - | HS3, H2 | - | Sí |
| Sobrecarga de la salida | `binary_sensor.saj_inverter_fault_output_overload` | Sensor binario | - | HS3, H2 | - | Sí |
| Temperatura demasiado alta | `binary_sensor.saj_inverter_fault_over_temperature` | Sensor binario | - | HS3, H2 | - | Sí |
| Comunicación del sistema en paralelo perdida | `binary_sensor.saj_inverter_fault_parallel_communication` | Sensor binario | - | HS3 | - | Sí |
| Sobrecorriente de hardware PV | `binary_sensor.saj_inverter_fault_pv_hardware_overcurrent` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo de entrada PV | `binary_sensor.saj_inverter_fault_pv_input` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo del modo de entrada PV | `binary_sensor.saj_inverter_fault_pv_input_mode` | Sensor binario | - | HS3, H2 | - | Sí |
| Comunicación con el contador solar perdida | `binary_sensor.saj_inverter_fault_pv_meter_communication` | Sensor binario | - | HS3 | - | Sí |
| Sobretensión PV | `binary_sensor.saj_inverter_fault_pv_overvoltage` | Sensor binario | - | HS3, H2 | - | Sí |
| Sobrecorriente de software PV | `binary_sensor.saj_inverter_fault_pv_software_overcurrent` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo del relé | `binary_sensor.saj_inverter_fault_relay` | Sensor binario | - | HS3, H2 | - | Sí |
| Comunicación con el controlador esclavo perdida | `binary_sensor.saj_inverter_fault_slave_communication` | Sensor binario | - | HS3 | - | Sí |
| Temperatura demasiado baja | `binary_sensor.saj_inverter_fault_under_temperature` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo no reconocido del inversor | `binary_sensor.saj_inverter_fault_unrecognised` | Sensor binario | - | HS3, H2 | - | Sí |
| Fallo del módulo de batería 2 | `binary_sensor.saj_battery_pack2_fault` | Sensor binario | - | H2 | Batería; Módulo de batería 2 y superiores | Sí |
| Aviso del módulo de batería 2 | `binary_sensor.saj_battery_pack2_warning` | Sensor binario | - | H2 | Batería; Módulo de batería 2 y superiores | Sí |
| Fallo del módulo de batería 3 | `binary_sensor.saj_battery_pack3_fault` | Sensor binario | - | H2 | Batería; Módulo de batería 3 y superiores | Sí |
| Aviso del módulo de batería 3 | `binary_sensor.saj_battery_pack3_warning` | Sensor binario | - | H2 | Batería; Módulo de batería 3 y superiores | Sí |
| Fallo del módulo de batería 4 | `binary_sensor.saj_battery_pack4_fault` | Sensor binario | - | H2 | Batería; Módulo de batería 4 y superiores | Sí |
| Aviso del módulo de batería 4 | `binary_sensor.saj_battery_pack4_warning` | Sensor binario | - | H2 | Batería; Módulo de batería 4 y superiores | Sí |
| Sobretensión del bus de CC | `binary_sensor.saj_inverter_fault_bus_overvoltage` | Sensor binario | - | H2 | - | Sí |
| Subtensión del bus de CC | `binary_sensor.saj_inverter_fault_bus_undervoltage` | Sensor binario | - | H2 | - | Sí |
| Fallo de fase de la red | `binary_sensor.saj_inverter_fault_grid_phase` | Sensor binario | - | H2 | - | Sí |
| Funcionamiento en isla | `binary_sensor.saj_inverter_fault_islanding` | Sensor binario | - | H2 | - | Sí |
