[en](../../../en-gb/user/entities/ev-charger.md) | [de](../../../de/user/entities/ev-charger.md) | [nl](../../../nl/user/entities/ev-charger.md) | [fr](../../../fr/user/entities/ev-charger.md) | [zh](../../../zh-hans/user/entities/ev-charger.md) | es | [it](../../../it/user/entities/ev-charger.md) | [pl](../../../pl/user/entities/ev-charger.md) | [sv](../../../sv/user/entities/ev-charger.md)

# Cargador de VE

El cargador de VE y sus controles de carga.

La lista de funciones de la integración explica las entidades de Cargador de VE en [Equipo opcional](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

87 entidades. Generado por `make docs`. No editar a mano.

Un prefijo definido en Configurar va después de `saj_` en el ID de cada entidad de Cargador de VE, por ejemplo `sensor.saj_house_ev_serial_number` con el prefijo `house`.

| Nombre | ID de entidad | Tipo | Unidad | Modelos | Equipo y números | Habilitada por defecto |
| --- | --- | --- | --- | --- | --- | --- |
| Número de serie del cargador de VE | `sensor.saj_ev_serial_number` | Sensor | - | HS3 | Cargador de VE | No |
| Modelo del cargador de VE | `sensor.saj_ev_model` | Sensor | - | HS3 | Cargador de VE | No |
| Versión de software del cargador de VE | `sensor.saj_ev_software_version` | Sensor | - | HS3 | Cargador de VE | No |
| Versión de hardware del cargador de VE | `sensor.saj_ev_hardware_version` | Sensor | - | HS3 | Cargador de VE | No |
| Número de fases del cargador de VE | `sensor.saj_ev_phase_count` | Sensor | - | HS3 | Cargador de VE | No |
| Potencia mínima del cargador de VE | `sensor.saj_ev_minimum_power` | Sensor | W | HS3 | Cargador de VE | No |
| Potencia máxima del cargador de VE | `sensor.saj_ev_maximum_power` | Sensor | W | HS3 | Cargador de VE | No |
| Modo de trabajo del cargador de VE | `sensor.saj_ev_work_mode` | Sensor | - | HS3 | Cargador de VE | No |
| Estado del cargador de VE | `sensor.saj_ev_status` | Sensor | - | HS3 | Cargador de VE | Sí |
| Tensión L1 del cargador de VE | `sensor.saj_ev_l1_voltage` | Sensor | V | HS3 | Cargador de VE | No |
| Corriente L1 del cargador de VE | `sensor.saj_ev_l1_current` | Sensor | A | HS3 | Cargador de VE | No |
| Tensión L2 del cargador de VE | `sensor.saj_ev_l2_voltage` | Sensor | V | HS3 | Cargador de VE | No |
| Corriente L2 del cargador de VE | `sensor.saj_ev_l2_current` | Sensor | A | HS3 | Cargador de VE | No |
| Tensión L3 del cargador de VE | `sensor.saj_ev_l3_voltage` | Sensor | V | HS3 | Cargador de VE | No |
| Corriente L3 del cargador de VE | `sensor.saj_ev_l3_current` | Sensor | A | HS3 | Cargador de VE | No |
| Potencia del cargador de VE | `sensor.saj_ev_power` | Sensor | W | HS3 | Cargador de VE | Sí |
| Duración de la carga del VE | `sensor.saj_ev_charge_duration` | Sensor | min | HS3 | Cargador de VE | No |
| Energía de la sesión del cargador de VE | `sensor.saj_ev_session_energy` | Sensor | kWh | HS3 | Cargador de VE | Sí |
| Energía total del cargador de VE | `sensor.saj_ev_total_energy` | Sensor | kWh | HS3 | Cargador de VE | Sí |
| Tensión del piloto de control del cargador de VE | `sensor.saj_ev_control_pilot_voltage` | Sensor | V | HS3 | Cargador de VE | No |
| Ciclo de trabajo del cargador de VE | `sensor.saj_ev_duty_cycle` | Sensor | % | HS3 | Cargador de VE | No |
| Control remoto del cargador de VE | `sensor.saj_ev_remote_control` | Sensor | - | HS3 | Cargador de VE | No |
| Consigna de corriente del cargador de VE | `sensor.saj_ev_current_setpoint` | Sensor | A | HS3 | Cargador de VE | No |
| Inicio de sesión del cargador de VE | `sensor.saj_ev_session_start` | Sensor | - | HS3 | Cargador de VE | No |
| Fin de sesión del cargador de VE | `sensor.saj_ev_session_end` | Sensor | - | HS3 | Cargador de VE | No |
| Versión del protocolo de ajustes del cargador de VE | `sensor.saj_ev_settings_protocol_version` | Sensor | - | HS3 | Cargador de VE | No |
| Dirección del cargador de VE | `sensor.saj_ev_address` | Sensor | - | HS3 | Cargador de VE | No |
| Velocidad en baudios del cargador de VE | `sensor.saj_ev_baud_rate` | Sensor | - | HS3 | Cargador de VE | No |
| Número de cargadores de VE | `sensor.saj_ev_charger_count` | Sensor | - | HS3 | Cargador de VE | No |
| Tiempo de espera de comunicación del cargador de VE | `sensor.saj_ev_communication_timeout` | Sensor | s | HS3 | Cargador de VE | No |
| Modo del puerto del cargador de VE | `sensor.saj_ev_port_mode` | Sensor | - | HS3 | Cargador de VE | No |
| Dirección del puerto del cargador de VE | `sensor.saj_ev_port_address` | Sensor | - | HS3 | Cargador de VE | No |
| Modo del cargador de VE | `select.saj_ev_mode` | Seleccionar | - | HS3 | Cargador de VE | Sí |
| Potencia de carga del VE | `number.saj_ev_charge_power` | Número | W | HS3 | Cargador de VE | No |
| Hora de inicio de la franja 1 del cargador de VE | `time.saj_ev_slot_1_start` | Hora | - | HS3 | Cargador de VE | No |
| Hora de fin de la franja 1 del cargador de VE | `time.saj_ev_slot_1_end` | Hora | - | HS3 | Cargador de VE | No |
| Modo de la franja 1 del cargador de VE | `select.saj_ev_slot_1_mode` | Seleccionar | - | HS3 | Cargador de VE | No |
| Carga desde la red de la franja 1 del cargador de VE | `switch.saj_ev_slot_1_grid_charging` | Interruptor | - | HS3 | Cargador de VE | No |
| Descarga de la batería de la franja 1 del cargador de VE | `switch.saj_ev_slot_1_battery_discharge` | Interruptor | - | HS3 | Cargador de VE | No |
| Días de la semana de la franja 1 del cargador de VE | `number.saj_ev_slot_1_days` | Número | - | HS3 | Cargador de VE | No |
| Potencia de la franja 1 del cargador de VE | `number.saj_ev_slot_1_power` | Número | W | HS3 | Cargador de VE | No |
| Hora de inicio de la franja 2 del cargador de VE | `time.saj_ev_slot_2_start` | Hora | - | HS3 | Cargador de VE | No |
| Hora de fin de la franja 2 del cargador de VE | `time.saj_ev_slot_2_end` | Hora | - | HS3 | Cargador de VE | No |
| Modo de la franja 2 del cargador de VE | `select.saj_ev_slot_2_mode` | Seleccionar | - | HS3 | Cargador de VE | No |
| Carga desde la red de la franja 2 del cargador de VE | `switch.saj_ev_slot_2_grid_charging` | Interruptor | - | HS3 | Cargador de VE | No |
| Descarga de la batería de la franja 2 del cargador de VE | `switch.saj_ev_slot_2_battery_discharge` | Interruptor | - | HS3 | Cargador de VE | No |
| Días de la semana de la franja 2 del cargador de VE | `number.saj_ev_slot_2_days` | Número | - | HS3 | Cargador de VE | No |
| Potencia de la franja 2 del cargador de VE | `number.saj_ev_slot_2_power` | Número | W | HS3 | Cargador de VE | No |
| Hora de inicio de la franja 3 del cargador de VE | `time.saj_ev_slot_3_start` | Hora | - | HS3 | Cargador de VE | No |
| Hora de fin de la franja 3 del cargador de VE | `time.saj_ev_slot_3_end` | Hora | - | HS3 | Cargador de VE | No |
| Modo de la franja 3 del cargador de VE | `select.saj_ev_slot_3_mode` | Seleccionar | - | HS3 | Cargador de VE | No |
| Carga desde la red de la franja 3 del cargador de VE | `switch.saj_ev_slot_3_grid_charging` | Interruptor | - | HS3 | Cargador de VE | No |
| Descarga de la batería de la franja 3 del cargador de VE | `switch.saj_ev_slot_3_battery_discharge` | Interruptor | - | HS3 | Cargador de VE | No |
| Días de la semana de la franja 3 del cargador de VE | `number.saj_ev_slot_3_days` | Número | - | HS3 | Cargador de VE | No |
| Potencia de la franja 3 del cargador de VE | `number.saj_ev_slot_3_power` | Número | W | HS3 | Cargador de VE | No |
| Hora de inicio de la franja 4 del cargador de VE | `time.saj_ev_slot_4_start` | Hora | - | HS3 | Cargador de VE | No |
| Hora de fin de la franja 4 del cargador de VE | `time.saj_ev_slot_4_end` | Hora | - | HS3 | Cargador de VE | No |
| Modo de la franja 4 del cargador de VE | `select.saj_ev_slot_4_mode` | Seleccionar | - | HS3 | Cargador de VE | No |
| Carga desde la red de la franja 4 del cargador de VE | `switch.saj_ev_slot_4_grid_charging` | Interruptor | - | HS3 | Cargador de VE | No |
| Descarga de la batería de la franja 4 del cargador de VE | `switch.saj_ev_slot_4_battery_discharge` | Interruptor | - | HS3 | Cargador de VE | No |
| Días de la semana de la franja 4 del cargador de VE | `number.saj_ev_slot_4_days` | Número | - | HS3 | Cargador de VE | No |
| Potencia de la franja 4 del cargador de VE | `number.saj_ev_slot_4_power` | Número | W | HS3 | Cargador de VE | No |
| Hora de inicio de la franja 5 del cargador de VE | `time.saj_ev_slot_5_start` | Hora | - | HS3 | Cargador de VE | No |
| Hora de fin de la franja 5 del cargador de VE | `time.saj_ev_slot_5_end` | Hora | - | HS3 | Cargador de VE | No |
| Modo de la franja 5 del cargador de VE | `select.saj_ev_slot_5_mode` | Seleccionar | - | HS3 | Cargador de VE | No |
| Carga desde la red de la franja 5 del cargador de VE | `switch.saj_ev_slot_5_grid_charging` | Interruptor | - | HS3 | Cargador de VE | No |
| Descarga de la batería de la franja 5 del cargador de VE | `switch.saj_ev_slot_5_battery_discharge` | Interruptor | - | HS3 | Cargador de VE | No |
| Días de la semana de la franja 5 del cargador de VE | `number.saj_ev_slot_5_days` | Número | - | HS3 | Cargador de VE | No |
| Potencia de la franja 5 del cargador de VE | `number.saj_ev_slot_5_power` | Número | W | HS3 | Cargador de VE | No |
| Hora de inicio de la franja 6 del cargador de VE | `time.saj_ev_slot_6_start` | Hora | - | HS3 | Cargador de VE | No |
| Hora de fin de la franja 6 del cargador de VE | `time.saj_ev_slot_6_end` | Hora | - | HS3 | Cargador de VE | No |
| Modo de la franja 6 del cargador de VE | `select.saj_ev_slot_6_mode` | Seleccionar | - | HS3 | Cargador de VE | No |
| Carga desde la red de la franja 6 del cargador de VE | `switch.saj_ev_slot_6_grid_charging` | Interruptor | - | HS3 | Cargador de VE | No |
| Descarga de la batería de la franja 6 del cargador de VE | `switch.saj_ev_slot_6_battery_discharge` | Interruptor | - | HS3 | Cargador de VE | No |
| Días de la semana de la franja 6 del cargador de VE | `number.saj_ev_slot_6_days` | Número | - | HS3 | Cargador de VE | No |
| Potencia de la franja 6 del cargador de VE | `number.saj_ev_slot_6_power` | Número | W | HS3 | Cargador de VE | No |
| Hora de inicio de la franja 7 del cargador de VE | `time.saj_ev_slot_7_start` | Hora | - | HS3 | Cargador de VE | No |
| Hora de fin de la franja 7 del cargador de VE | `time.saj_ev_slot_7_end` | Hora | - | HS3 | Cargador de VE | No |
| Modo de la franja 7 del cargador de VE | `select.saj_ev_slot_7_mode` | Seleccionar | - | HS3 | Cargador de VE | No |
| Carga desde la red de la franja 7 del cargador de VE | `switch.saj_ev_slot_7_grid_charging` | Interruptor | - | HS3 | Cargador de VE | No |
| Descarga de la batería de la franja 7 del cargador de VE | `switch.saj_ev_slot_7_battery_discharge` | Interruptor | - | HS3 | Cargador de VE | No |
| Días de la semana de la franja 7 del cargador de VE | `number.saj_ev_slot_7_days` | Número | - | HS3 | Cargador de VE | No |
| Potencia de la franja 7 del cargador de VE | `number.saj_ev_slot_7_power` | Número | W | HS3 | Cargador de VE | No |
| Carga a corriente mínima del cargador de VE | `switch.saj_ev_minimum_current_charging` | Interruptor | - | HS3 | Cargador de VE | No |
| Carga EMS del cargador de VE | `switch.saj_ev_ems_charging` | Interruptor | - | HS3 | Cargador de VE | No |
| Modo de fases EMS del cargador de VE | `select.saj_ev_ems_phase_mode` | Seleccionar | - | HS3 | Cargador de VE | No |
| Corriente de carga EMS del cargador de VE | `number.saj_ev_ems_charge_current` | Número | A | HS3 | Cargador de VE | No |
