[en](../../../en-gb/user/entities/inverter-and-pv.md) | [de](../../../de/user/entities/inverter-and-pv.md) | [nl](../../../nl/user/entities/inverter-and-pv.md) | [fr](../../../fr/user/entities/inverter-and-pv.md) | [zh](../../../zh-hans/user/entities/inverter-and-pv.md) | es | [it](../../../it/user/entities/inverter-and-pv.md) | [pl](../../../pl/user/entities/inverter-and-pv.md) | [sv](../../../sv/user/entities/inverter-and-pv.md)

# Inversor y PV

Salida del inversor, strings solares, puerto de respaldo, contadores de energía, versiones y la carga doméstica.

La lista de funciones de la integración explica las entidades de Inversor y PV en [Dispositivos y entidades](../../../../custom_components/saj_local/docs/features.md#devices-and-entities).

244 entidades. Generado por `make docs`. No editar a mano.

Un prefijo definido en Configurar va después de `saj_` en el ID de cada entidad de Inversor y PV, por ejemplo `sensor.saj_house_ethernet_protocol_version` con el prefijo `house`.

| Nombre | ID de entidad | Tipo | Unidad | Modelos | Equipo y números | Habilitada por defecto |
| --- | --- | --- | --- | --- | --- | --- |
| Versión del protocolo Ethernet | `sensor.saj_ethernet_protocol_version` | Sensor | - | HS3 | - | No |
| Dirección MAC Ethernet | `sensor.saj_ethernet_mac_address` | Sensor | - | HS3 | - | No |
| Modo Ethernet | `sensor.saj_ethernet_mode` | Sensor | - | HS3 | - | No |
| Dirección IP Ethernet | `sensor.saj_ethernet_ip_address` | Sensor | - | HS3 | - | No |
| Máscara de subred Ethernet | `sensor.saj_ethernet_subnet_mask` | Sensor | - | HS3 | - | No |
| Puerta de enlace Ethernet | `sensor.saj_ethernet_gateway` | Sensor | - | HS3 | - | No |
| DNS primario Ethernet | `sensor.saj_ethernet_dns_primary` | Sensor | - | HS3 | - | No |
| DNS secundario Ethernet | `sensor.saj_ethernet_dns_secondary` | Sensor | - | HS3 | - | No |
| Secuencia de ajustes | `sensor.saj_settings_sequence` | Sensor | - | HS3, H2 | - | No |
| Versión del protocolo de ajustes | `sensor.saj_settings_protocol_version` | Sensor | - | HS3 | - | No |
| Configuración del contador | `sensor.saj_meter_configuration` | Sensor | - | HS3, H2 | - | No |
| Dirección del contador | `sensor.saj_meter_address` | Sensor | - | HS3, H2 | - | No |
| Dirección RS485 | `sensor.saj_rs485_address` | Sensor | - | HS3, H2 | - | No |
| Velocidad en baudios RS485 | `sensor.saj_rs485_baud_rate` | Sensor | - | HS3, H2 | - | No |
| Protocolo de batería | `sensor.saj_battery_protocol` | Sensor | - | HS3, H2 | - | No |
| Dirección esclava RS485 | `sensor.saj_rs485_slave_address` | Sensor | - | HS3 | - | No |
| Velocidad en baudios esclava RS485 | `sensor.saj_rs485_slave_baud_rate` | Sensor | - | HS3 | - | No |
| Reloj del inversor | `sensor.saj_inverter_clock` | Sensor | - | HS3, H2 | - | No |
| Modo de funcionamiento | `sensor.saj_operating_mode` | Sensor | - | HS3, H2 | - | Sí |
| Temperatura del inversor | `sensor.saj_inverter_temperature` | Sensor | °C | HS3, H2 | - | Sí |
| Temperatura ambiente | `sensor.saj_ambient_temperature` | Sensor | °C | HS3, H2 | - | No |
| Corriente de fuga | `sensor.saj_leakage_current` | Sensor | mA | HS3, H2 | - | No |
| Resistencia de aislamiento PV1 | `sensor.saj_pv1_insulation_resistance` | Sensor | kΩ | HS3, H2 | - | No |
| Resistencia de aislamiento PV2 | `sensor.saj_pv2_insulation_resistance` | Sensor | kΩ | HS3, H2 | String PV 2 y superiores | No |
| Consigna de potencia de descarga del inversor | `sensor.saj_inverter_discharge_power_setpoint` | Sensor | W | HS3, H2 | - | No |
| Consigna de potencia de carga del inversor | `sensor.saj_inverter_charge_power_setpoint` | Sensor | W | HS3, H2 | - | No |
| Protocolo de batería (en vigor) | `sensor.saj_battery_protocol_active` | Sensor | - | HS3, H2 | - | No |
| Configuración del contador (en vigor) | `sensor.saj_meter_configuration_active` | Sensor | - | HS3, H2 | - | No |
| Tensión L1 del inversor | `sensor.saj_inverter_l1_voltage` | Sensor | V | HS3, H2 | - | No |
| Corriente L1 del inversor | `sensor.saj_inverter_l1_current` | Sensor | A | HS3, H2 | - | No |
| Frecuencia L1 del inversor | `sensor.saj_inverter_l1_frequency` | Sensor | Hz | HS3, H2 | - | No |
| Potencia L1 del inversor | `sensor.saj_inverter_l1_power` | Sensor | W | HS3, H2 | - | No |
| Potencia aparente L1 del inversor | `sensor.saj_inverter_l1_apparent_power` | Sensor | VA | HS3, H2 | - | No |
| Tensión L2 del inversor | `sensor.saj_inverter_l2_voltage` | Sensor | V | HS3, H2 | Fase 2 y superiores | No |
| Corriente L2 del inversor | `sensor.saj_inverter_l2_current` | Sensor | A | HS3, H2 | Fase 2 y superiores | No |
| Frecuencia L2 del inversor | `sensor.saj_inverter_l2_frequency` | Sensor | Hz | HS3, H2 | Fase 2 y superiores | No |
| Potencia L2 del inversor | `sensor.saj_inverter_l2_power` | Sensor | W | HS3, H2 | Fase 2 y superiores | No |
| Potencia aparente L2 del inversor | `sensor.saj_inverter_l2_apparent_power` | Sensor | VA | HS3, H2 | Fase 2 y superiores | No |
| Tensión L3 del inversor | `sensor.saj_inverter_l3_voltage` | Sensor | V | HS3, H2 | Fase 3 y superiores | No |
| Corriente L3 del inversor | `sensor.saj_inverter_l3_current` | Sensor | A | HS3, H2 | Fase 3 y superiores | No |
| Frecuencia L3 del inversor | `sensor.saj_inverter_l3_frequency` | Sensor | Hz | HS3, H2 | Fase 3 y superiores | No |
| Potencia L3 del inversor | `sensor.saj_inverter_l3_power` | Sensor | W | HS3, H2 | Fase 3 y superiores | No |
| Potencia aparente L3 del inversor | `sensor.saj_inverter_l3_apparent_power` | Sensor | VA | HS3, H2 | Fase 3 y superiores | No |
| Tensión L1 de respaldo | `sensor.saj_backup_l1_voltage` | Sensor | V | HS3, H2 | - | No |
| Corriente L1 de respaldo | `sensor.saj_backup_l1_current` | Sensor | A | HS3, H2 | - | No |
| Frecuencia L1 de respaldo | `sensor.saj_backup_l1_frequency` | Sensor | Hz | HS3, H2 | - | No |
| Tensión continua L1 de respaldo | `sensor.saj_backup_l1_dc_voltage` | Sensor | mV | HS3, H2 | - | No |
| Potencia L1 de respaldo | `sensor.saj_backup_l1_power` | Sensor | W | HS3, H2 | - | No |
| Potencia aparente L1 de respaldo | `sensor.saj_backup_l1_apparent_power` | Sensor | VA | HS3, H2 | - | No |
| Tensión L2 de respaldo | `sensor.saj_backup_l2_voltage` | Sensor | V | HS3, H2 | Fase 2 y superiores | No |
| Corriente L2 de respaldo | `sensor.saj_backup_l2_current` | Sensor | A | HS3, H2 | Fase 2 y superiores | No |
| Frecuencia L2 de respaldo | `sensor.saj_backup_l2_frequency` | Sensor | Hz | HS3, H2 | Fase 2 y superiores | No |
| Tensión continua L2 de respaldo | `sensor.saj_backup_l2_dc_voltage` | Sensor | mV | HS3, H2 | Fase 2 y superiores | No |
| Potencia L2 de respaldo | `sensor.saj_backup_l2_power` | Sensor | W | HS3, H2 | Fase 2 y superiores | No |
| Potencia aparente L2 de respaldo | `sensor.saj_backup_l2_apparent_power` | Sensor | VA | HS3, H2 | Fase 2 y superiores | No |
| Tensión L3 de respaldo | `sensor.saj_backup_l3_voltage` | Sensor | V | HS3, H2 | Fase 3 y superiores | No |
| Corriente L3 de respaldo | `sensor.saj_backup_l3_current` | Sensor | A | HS3, H2 | Fase 3 y superiores | No |
| Frecuencia L3 de respaldo | `sensor.saj_backup_l3_frequency` | Sensor | Hz | HS3, H2 | Fase 3 y superiores | No |
| Tensión continua L3 de respaldo | `sensor.saj_backup_l3_dc_voltage` | Sensor | mV | HS3, H2 | Fase 3 y superiores | No |
| Potencia L3 de respaldo | `sensor.saj_backup_l3_power` | Sensor | W | HS3, H2 | Fase 3 y superiores | No |
| Potencia aparente L3 de respaldo | `sensor.saj_backup_l3_apparent_power` | Sensor | VA | HS3, H2 | Fase 3 y superiores | No |
| Tensión del bus de CC | `sensor.saj_dc_bus_voltage` | Sensor | V | HS3, H2 | - | No |
| Tensión del bus de CC esclavo | `sensor.saj_dc_bus_slave_voltage` | Sensor | V | HS3, H2 | - | No |
| Tensión PV1 | `sensor.saj_pv1_voltage` | Sensor | V | HS3, H2 | - | Sí |
| Corriente PV1 | `sensor.saj_pv1_current` | Sensor | A | HS3, H2 | - | Sí |
| Potencia PV1 | `sensor.saj_pv1_power` | Sensor | W | HS3, H2 | - | Sí |
| Tensión PV2 | `sensor.saj_pv2_voltage` | Sensor | V | HS3, H2 | String PV 2 y superiores | Sí |
| Corriente PV2 | `sensor.saj_pv2_current` | Sensor | A | HS3, H2 | String PV 2 y superiores | Sí |
| Potencia PV2 | `sensor.saj_pv2_power` | Sensor | W | HS3, H2 | String PV 2 y superiores | Sí |
| Potencia solar | `sensor.saj_pv_power` | Sensor | W | HS3, H2 | - | Sí |
| Potencia del inversor | `sensor.saj_inverter_power` | Sensor | W | HS3, H2 | - | Sí |
| Energía solar de hoy | `sensor.saj_pv_energy_today` | Sensor | kWh | HS3, H2 | - | Sí |
| Energía solar de este mes | `sensor.saj_pv_energy_month` | Sensor | kWh | HS3, H2 | - | No |
| Energía solar de este año | `sensor.saj_pv_energy_year` | Sensor | kWh | HS3, H2 | - | No |
| Energía solar total | `sensor.saj_pv_energy_total` | Sensor | kWh | HS3, H2 | - | Sí |
| Energía de la carga doméstica de hoy | `sensor.saj_load_energy_today` | Sensor | kWh | HS3, H2 | - | Sí |
| Energía de la carga doméstica de este mes | `sensor.saj_load_energy_month` | Sensor | kWh | HS3, H2 | - | No |
| Energía de la carga doméstica de este año | `sensor.saj_load_energy_year` | Sensor | kWh | HS3, H2 | - | No |
| Energía de la carga doméstica total | `sensor.saj_load_energy_total` | Sensor | kWh | HS3, H2 | - | Sí |
| Energía de la carga de respaldo de hoy | `sensor.saj_backup_load_energy_today` | Sensor | kWh | HS3, H2 | - | Sí |
| Energía de la carga de respaldo de este mes | `sensor.saj_backup_load_energy_month` | Sensor | kWh | HS3, H2 | - | No |
| Energía de la carga de respaldo de este año | `sensor.saj_backup_load_energy_year` | Sensor | kWh | HS3, H2 | - | No |
| Energía de la carga de respaldo total | `sensor.saj_backup_load_energy_total` | Sensor | kWh | HS3, H2 | - | Sí |
| Modo paralelo | `sensor.saj_parallel_mode` | Sensor | - | HS3, H2 | - | No |
| Máquinas en paralelo en línea | `sensor.saj_parallel_online_count` | Sensor | - | HS3, H2 | - | No |
| Potencia de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_power` | Sensor | W | HS3 | - | No |
| Potencia L1 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_l1_power` | Sensor | W | HS3 | - | No |
| Tensión L1 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_l1_voltage` | Sensor | V | HS3 | - | No |
| Corriente L1 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_l1_current` | Sensor | A | HS3 | - | No |
| Frecuencia L1 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_l1_frequency` | Sensor | Hz | HS3 | - | No |
| Potencia L2 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_l2_power` | Sensor | W | HS3 | Fase 2 y superiores | No |
| Tensión L2 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_l2_voltage` | Sensor | V | HS3 | Fase 2 y superiores | No |
| Corriente L2 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_l2_current` | Sensor | A | HS3 | Fase 2 y superiores | No |
| Frecuencia L2 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_l2_frequency` | Sensor | Hz | HS3 | Fase 2 y superiores | No |
| Potencia L3 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_l3_power` | Sensor | W | HS3 | Fase 3 y superiores | No |
| Tensión L3 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_l3_voltage` | Sensor | V | HS3 | Fase 3 y superiores | No |
| Corriente L3 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_l3_current` | Sensor | A | HS3 | Fase 3 y superiores | No |
| Frecuencia L3 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_l3_frequency` | Sensor | Hz | HS3 | Fase 3 y superiores | No |
| Potencia del inversor (promedio de 5 minutos) | `sensor.saj_five_minute_average_inverter_power` | Sensor | W | HS3 | - | No |
| Potencia L1 del inversor (promedio de 5 minutos) | `sensor.saj_five_minute_average_inverter_l1_power` | Sensor | W | HS3 | - | No |
| Tensión L1 del inversor (promedio de 5 minutos) | `sensor.saj_five_minute_average_inverter_l1_voltage` | Sensor | V | HS3 | - | No |
| Corriente L1 del inversor (promedio de 5 minutos) | `sensor.saj_five_minute_average_inverter_l1_current` | Sensor | A | HS3 | - | No |
| Frecuencia L1 del inversor (promedio de 5 minutos) | `sensor.saj_five_minute_average_inverter_l1_frequency` | Sensor | Hz | HS3 | - | No |
| Potencia L2 del inversor (promedio de 5 minutos) | `sensor.saj_five_minute_average_inverter_l2_power` | Sensor | W | HS3 | Fase 2 y superiores | No |
| Tensión L2 del inversor (promedio de 5 minutos) | `sensor.saj_five_minute_average_inverter_l2_voltage` | Sensor | V | HS3 | Fase 2 y superiores | No |
| Corriente L2 del inversor (promedio de 5 minutos) | `sensor.saj_five_minute_average_inverter_l2_current` | Sensor | A | HS3 | Fase 2 y superiores | No |
| Frecuencia L2 del inversor (promedio de 5 minutos) | `sensor.saj_five_minute_average_inverter_l2_frequency` | Sensor | Hz | HS3 | Fase 2 y superiores | No |
| Potencia L3 del inversor (promedio de 5 minutos) | `sensor.saj_five_minute_average_inverter_l3_power` | Sensor | W | HS3 | Fase 3 y superiores | No |
| Tensión L3 del inversor (promedio de 5 minutos) | `sensor.saj_five_minute_average_inverter_l3_voltage` | Sensor | V | HS3 | Fase 3 y superiores | No |
| Corriente L3 del inversor (promedio de 5 minutos) | `sensor.saj_five_minute_average_inverter_l3_current` | Sensor | A | HS3 | Fase 3 y superiores | No |
| Frecuencia L3 del inversor (promedio de 5 minutos) | `sensor.saj_five_minute_average_inverter_l3_frequency` | Sensor | Hz | HS3 | Fase 3 y superiores | No |
| Potencia de la carga doméstica (promedio de 5 minutos) | `sensor.saj_five_minute_average_load_power` | Sensor | W | HS3 | - | No |
| Potencia L1 de la carga doméstica (promedio de 5 minutos) | `sensor.saj_five_minute_average_load_l1_power` | Sensor | W | HS3 | - | No |
| Tensión L1 de la carga doméstica (promedio de 5 minutos) | `sensor.saj_five_minute_average_load_l1_voltage` | Sensor | V | HS3 | - | No |
| Corriente L1 de la carga doméstica (promedio de 5 minutos) | `sensor.saj_five_minute_average_load_l1_current` | Sensor | A | HS3 | - | No |
| Frecuencia L1 de la carga doméstica (promedio de 5 minutos) | `sensor.saj_five_minute_average_load_l1_frequency` | Sensor | Hz | HS3 | - | No |
| Potencia L2 de la carga doméstica (promedio de 5 minutos) | `sensor.saj_five_minute_average_load_l2_power` | Sensor | W | HS3 | Fase 2 y superiores | No |
| Tensión L2 de la carga doméstica (promedio de 5 minutos) | `sensor.saj_five_minute_average_load_l2_voltage` | Sensor | V | HS3 | Fase 2 y superiores | No |
| Corriente L2 de la carga doméstica (promedio de 5 minutos) | `sensor.saj_five_minute_average_load_l2_current` | Sensor | A | HS3 | Fase 2 y superiores | No |
| Frecuencia L2 de la carga doméstica (promedio de 5 minutos) | `sensor.saj_five_minute_average_load_l2_frequency` | Sensor | Hz | HS3 | Fase 2 y superiores | No |
| Potencia L3 de la carga doméstica (promedio de 5 minutos) | `sensor.saj_five_minute_average_load_l3_power` | Sensor | W | HS3 | Fase 3 y superiores | No |
| Tensión L3 de la carga doméstica (promedio de 5 minutos) | `sensor.saj_five_minute_average_load_l3_voltage` | Sensor | V | HS3 | Fase 3 y superiores | No |
| Corriente L3 de la carga doméstica (promedio de 5 minutos) | `sensor.saj_five_minute_average_load_l3_current` | Sensor | A | HS3 | Fase 3 y superiores | No |
| Frecuencia L3 de la carga doméstica (promedio de 5 minutos) | `sensor.saj_five_minute_average_load_l3_frequency` | Sensor | Hz | HS3 | Fase 3 y superiores | No |
| Potencia de carga de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_load_power` | Sensor | W | HS3 | - | No |
| Potencia de carga L1 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_load_l1_power` | Sensor | W | HS3 | - | No |
| Tensión de carga L1 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_load_l1_voltage` | Sensor | V | HS3 | - | No |
| Corriente de carga L1 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_load_l1_current` | Sensor | A | HS3 | - | No |
| Frecuencia de carga L1 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_load_l1_frequency` | Sensor | Hz | HS3 | - | No |
| Potencia de carga L2 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_load_l2_power` | Sensor | W | HS3 | Fase 2 y superiores | No |
| Tensión de carga L2 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_load_l2_voltage` | Sensor | V | HS3 | Fase 2 y superiores | No |
| Corriente de carga L2 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_load_l2_current` | Sensor | A | HS3 | Fase 2 y superiores | No |
| Frecuencia de carga L2 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_load_l2_frequency` | Sensor | Hz | HS3 | Fase 2 y superiores | No |
| Potencia de carga L3 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_load_l3_power` | Sensor | W | HS3 | Fase 3 y superiores | No |
| Tensión de carga L3 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_load_l3_voltage` | Sensor | V | HS3 | Fase 3 y superiores | No |
| Corriente de carga L3 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_load_l3_current` | Sensor | A | HS3 | Fase 3 y superiores | No |
| Frecuencia de carga L3 de la red (promedio de 5 minutos) | `sensor.saj_five_minute_average_grid_load_l3_frequency` | Sensor | Hz | HS3 | Fase 3 y superiores | No |
| Potencia de respaldo (promedio de 5 minutos) | `sensor.saj_five_minute_average_backup_power` | Sensor | W | HS3 | - | No |
| Potencia L1 de respaldo (promedio de 5 minutos) | `sensor.saj_five_minute_average_backup_l1_power` | Sensor | W | HS3 | - | No |
| Tensión L1 de respaldo (promedio de 5 minutos) | `sensor.saj_five_minute_average_backup_l1_voltage` | Sensor | V | HS3 | - | No |
| Corriente L1 de respaldo (promedio de 5 minutos) | `sensor.saj_five_minute_average_backup_l1_current` | Sensor | A | HS3 | - | No |
| Frecuencia L1 de respaldo (promedio de 5 minutos) | `sensor.saj_five_minute_average_backup_l1_frequency` | Sensor | Hz | HS3 | - | No |
| Potencia L2 de respaldo (promedio de 5 minutos) | `sensor.saj_five_minute_average_backup_l2_power` | Sensor | W | HS3 | Fase 2 y superiores | No |
| Tensión L2 de respaldo (promedio de 5 minutos) | `sensor.saj_five_minute_average_backup_l2_voltage` | Sensor | V | HS3 | Fase 2 y superiores | No |
| Corriente L2 de respaldo (promedio de 5 minutos) | `sensor.saj_five_minute_average_backup_l2_current` | Sensor | A | HS3 | Fase 2 y superiores | No |
| Frecuencia L2 de respaldo (promedio de 5 minutos) | `sensor.saj_five_minute_average_backup_l2_frequency` | Sensor | Hz | HS3 | Fase 2 y superiores | No |
| Potencia L3 de respaldo (promedio de 5 minutos) | `sensor.saj_five_minute_average_backup_l3_power` | Sensor | W | HS3 | Fase 3 y superiores | No |
| Tensión L3 de respaldo (promedio de 5 minutos) | `sensor.saj_five_minute_average_backup_l3_voltage` | Sensor | V | HS3 | Fase 3 y superiores | No |
| Corriente L3 de respaldo (promedio de 5 minutos) | `sensor.saj_five_minute_average_backup_l3_current` | Sensor | A | HS3 | Fase 3 y superiores | No |
| Frecuencia L3 de respaldo (promedio de 5 minutos) | `sensor.saj_five_minute_average_backup_l3_frequency` | Sensor | Hz | HS3 | Fase 3 y superiores | No |
| Potencia solar (promedio de 5 minutos) | `sensor.saj_five_minute_average_pv_power` | Sensor | W | HS3 | - | No |
| Tensión PV1 (promedio de 5 minutos) | `sensor.saj_five_minute_average_pv1_voltage` | Sensor | V | HS3 | - | No |
| Corriente PV1 (promedio de 5 minutos) | `sensor.saj_five_minute_average_pv1_current` | Sensor | A | HS3 | - | No |
| Potencia PV1 (promedio de 5 minutos) | `sensor.saj_five_minute_average_pv1_power` | Sensor | W | HS3 | - | No |
| Tensión PV2 (promedio de 5 minutos) | `sensor.saj_five_minute_average_pv2_voltage` | Sensor | V | HS3 | String PV 2 y superiores | No |
| Corriente PV2 (promedio de 5 minutos) | `sensor.saj_five_minute_average_pv2_current` | Sensor | A | HS3 | String PV 2 y superiores | No |
| Potencia PV2 (promedio de 5 minutos) | `sensor.saj_five_minute_average_pv2_power` | Sensor | W | HS3 | String PV 2 y superiores | No |
| Potencia del generador (promedio de 5 minutos) | `sensor.saj_five_minute_average_generator_power` | Sensor | W | HS3 | - | No |
| Potencia L1 del generador (promedio de 5 minutos) | `sensor.saj_five_minute_average_generator_l1_power` | Sensor | W | HS3 | - | No |
| Tensión L1 del generador (promedio de 5 minutos) | `sensor.saj_five_minute_average_generator_l1_voltage` | Sensor | V | HS3 | - | No |
| Corriente L1 del generador (promedio de 5 minutos) | `sensor.saj_five_minute_average_generator_l1_current` | Sensor | A | HS3 | - | No |
| Frecuencia L1 del generador (promedio de 5 minutos) | `sensor.saj_five_minute_average_generator_l1_frequency` | Sensor | Hz | HS3 | - | No |
| Potencia L2 del generador (promedio de 5 minutos) | `sensor.saj_five_minute_average_generator_l2_power` | Sensor | W | HS3 | Fase 2 y superiores | No |
| Tensión L2 del generador (promedio de 5 minutos) | `sensor.saj_five_minute_average_generator_l2_voltage` | Sensor | V | HS3 | Fase 2 y superiores | No |
| Corriente L2 del generador (promedio de 5 minutos) | `sensor.saj_five_minute_average_generator_l2_current` | Sensor | A | HS3 | Fase 2 y superiores | No |
| Frecuencia L2 del generador (promedio de 5 minutos) | `sensor.saj_five_minute_average_generator_l2_frequency` | Sensor | Hz | HS3 | Fase 2 y superiores | No |
| Potencia L3 del generador (promedio de 5 minutos) | `sensor.saj_five_minute_average_generator_l3_power` | Sensor | W | HS3 | Fase 3 y superiores | No |
| Tensión L3 del generador (promedio de 5 minutos) | `sensor.saj_five_minute_average_generator_l3_voltage` | Sensor | V | HS3 | Fase 3 y superiores | No |
| Corriente L3 del generador (promedio de 5 minutos) | `sensor.saj_five_minute_average_generator_l3_current` | Sensor | A | HS3 | Fase 3 y superiores | No |
| Frecuencia L3 del generador (promedio de 5 minutos) | `sensor.saj_five_minute_average_generator_l3_frequency` | Sensor | Hz | HS3 | Fase 3 y superiores | No |
| Código de producto | `sensor.saj_product_code` | Sensor | - | HS3, H2 | - | No |
| Versión de software de la pantalla | `sensor.saj_display_software_version` | Sensor | - | HS3, H2 | - | No |
| Versión de software maestro | `sensor.saj_master_software_version` | Sensor | - | HS3, H2 | - | No |
| Versión de software esclavo | `sensor.saj_slave_software_version` | Sensor | - | HS3, H2 | - | No |
| Versión de hardware de la pantalla | `sensor.saj_display_hardware_version` | Sensor | - | HS3, H2 | - | No |
| Versión de hardware de control | `sensor.saj_control_hardware_version` | Sensor | - | HS3, H2 | - | No |
| Versión de hardware de potencia | `sensor.saj_power_hardware_version` | Sensor | - | HS3, H2 | - | No |
| Número de módulos de batería | `sensor.saj_battery_pack_count` | Sensor | - | HS3, H2 | - | No |
| Estado del contador A | `sensor.saj_meter_a_status` | Sensor | - | HS3, H2 | - | No |
| Estado del contador B | `sensor.saj_meter_b_status` | Sensor | - | HS3, H2 | - | No |
| Potencia de la carga de respaldo | `sensor.saj_backup_load_power` | Sensor | W | HS3, H2 | - | Sí |
| Potencia de la carga doméstica | `sensor.saj_load_power` | Sensor | W | HS3, H2 | - | Sí |
| Autoconsumo de hoy | `sensor.saj_self_consumption_today` | Sensor | % | HS3, H2 | - | No |
| Autosuficiencia de hoy | `sensor.saj_self_sufficiency_today` | Sensor | % | HS3, H2 | - | No |
| Potencia del excedente solar | `sensor.saj_solar_surplus_power` | Sensor | W | HS3, H2 | - | No |
| Modo de flujo inverso | `sensor.saj_reverse_flow_mode` | Sensor | - | H2 | - | No |
| Histéresis de frecuencia FCAS | `sensor.saj_fcas_frequency_hysteresis` | Sensor | Hz | H2 | - | No |
| Función en paralelo | `sensor.saj_parallel_role` | Sensor | - | H2 | - | No |
| Número en paralelo | `sensor.saj_parallel_number` | Sensor | - | H2 | - | No |
| Modo paralelo configurado | `sensor.saj_parallel_configured_mode` | Sensor | - | H2 | - | No |
| Modo de entrada de la batería | `sensor.saj_battery_input_mode` | Sensor | - | H2 | - | No |
| Modo de entrada PV | `sensor.saj_pv_input_mode` | Sensor | - | H2 | - | No |
| Modo aislado de la red | `sensor.saj_off_grid_mode` | Sensor | - | H2 | - | No |
| Tensión de salida aislada de la red | `sensor.saj_off_grid_output_voltage` | Sensor | V | H2 | - | No |
| Frecuencia de salida aislada de la red | `sensor.saj_off_grid_output_frequency` | Sensor | Hz | H2 | - | No |
| Habilitación del motor | `sensor.saj_motor_enable` | Sensor | - | H2 | - | No |
| Modelo de máquina | `sensor.saj_machine_model` | Sensor | - | H2 | - | No |
| Potencia nominal | `sensor.saj_rated_power` | Sensor | W | H2 | - | No |
| Indicadores de función 1 | `sensor.saj_function_flags_1` | Sensor | - | H2 | - | No |
| Indicadores de función 2 | `sensor.saj_function_flags_2` | Sensor | - | H2 | - | No |
| Componente máximo de corriente continua | `sensor.saj_max_dc_current_component` | Sensor | mA | H2 | - | No |
| Componente máximo de tensión continua | `sensor.saj_max_dc_voltage_component` | Sensor | V | H2 | - | No |
| Límite de resistencia de aislamiento | `sensor.saj_insulation_resistance_limit` | Sensor | kΩ | H2 | - | No |
| Corriente de fuga máxima | `sensor.saj_max_leakage_current` | Sensor | mA | H2 | - | No |
| Parada del inversor | `sensor.saj_inverter_stop` | Sensor | - | H2 | - | No |
| Tensión de arranque PV | `sensor.saj_pv_start_voltage` | Sensor | V | H2 | - | No |
| Tensión de apagado PV | `sensor.saj_pv_shutdown_voltage` | Sensor | V | H2 | - | No |
| Tensión MPPT alta | `sensor.saj_mppt_voltage_high` | Sensor | V | H2 | - | No |
| Tensión MPPT baja | `sensor.saj_mppt_voltage_low` | Sensor | V | H2 | - | No |
| Tiempo de escaneo MPPT | `sensor.saj_mppt_scan_time` | Sensor | min | H2 | - | No |
| Número de errores del inversor | `sensor.saj_inverter_error_count` | Sensor | - | H2 | - | No |
| Resistencia de aislamiento PV3 | `sensor.saj_pv3_insulation_resistance` | Sensor | kΩ | H2 | String PV 3 y superiores | No |
| Resistencia de aislamiento PV4 | `sensor.saj_pv4_insulation_resistance` | Sensor | kΩ | H2 | String PV 4 y superiores | No |
| Estado de hardware DRM | `sensor.saj_drm_hardware_status` | Sensor | - | H2 | - | No |
| Estado de software DRM | `sensor.saj_drm_software_status` | Sensor | - | H2 | - | No |
| Secuencia del registro de fallos | `sensor.saj_fault_record_sequence` | Sensor | - | H2 | - | No |
| Modo de aplicación (en vigor) | `sensor.saj_application_mode_active` | Sensor | - | H2 | - | No |
| Tensión PV3 | `sensor.saj_pv3_voltage` | Sensor | V | H2 | String PV 3 y superiores | Sí |
| Corriente PV3 | `sensor.saj_pv3_current` | Sensor | A | H2 | String PV 3 y superiores | Sí |
| Potencia PV3 | `sensor.saj_pv3_power` | Sensor | W | H2 | String PV 3 y superiores | Sí |
| Tensión PV4 | `sensor.saj_pv4_voltage` | Sensor | V | H2 | String PV 4 y superiores | Sí |
| Corriente PV4 | `sensor.saj_pv4_current` | Sensor | A | H2 | String PV 4 y superiores | Sí |
| Potencia PV4 | `sensor.saj_pv4_power` | Sensor | W | H2 | String PV 4 y superiores | Sí |
| Potencia de la red del CT | `sensor.saj_ct_grid_power` | Sensor | W | H2 | - | No |
| Potencia aparente de la red del CT | `sensor.saj_ct_grid_apparent_power` | Sensor | VA | H2 | - | No |
| Potencia solar del CT | `sensor.saj_ct_pv_power` | Sensor | W | H2 | - | No |
| Potencia aparente solar del CT | `sensor.saj_ct_pv_apparent_power` | Sensor | VA | H2 | - | No |
| Potencia aparente del inversor | `sensor.saj_inverter_apparent_power` | Sensor | VA | H2 | - | No |
| Potencia aparente de la carga de respaldo | `sensor.saj_backup_load_apparent_power` | Sensor | VA | H2 | - | No |
| Tiempo de generación solar de hoy | `sensor.saj_pv_generation_time_today` | Sensor | h | H2 | - | No |
| Tiempo de generación solar total | `sensor.saj_pv_generation_time_total` | Sensor | h | H2 | - | No |
| Energía del inversor de hoy | `sensor.saj_inverter_energy_today` | Sensor | kWh | H2 | - | No |
| Energía del inversor de este mes | `sensor.saj_inverter_energy_month` | Sensor | kWh | H2 | - | No |
| Energía del inversor de este año | `sensor.saj_inverter_energy_year` | Sensor | kWh | H2 | - | No |
| Energía del inversor total | `sensor.saj_inverter_energy_total` | Sensor | kWh | H2 | - | No |
| Energía PV2 de hoy | `sensor.saj_pv2_energy_today` | Sensor | kWh | H2 | String PV 2 y superiores | No |
| Energía PV2 de este mes | `sensor.saj_pv2_energy_month` | Sensor | kWh | H2 | String PV 2 y superiores | No |
| Energía PV2 de este año | `sensor.saj_pv2_energy_year` | Sensor | kWh | H2 | String PV 2 y superiores | No |
| Energía PV2 total | `sensor.saj_pv2_energy_total` | Sensor | kWh | H2 | String PV 2 y superiores | No |
| Energía PV3 de hoy | `sensor.saj_pv3_energy_today` | Sensor | kWh | H2 | String PV 3 y superiores | No |
| Energía PV3 de este mes | `sensor.saj_pv3_energy_month` | Sensor | kWh | H2 | String PV 3 y superiores | No |
| Energía PV3 de este año | `sensor.saj_pv3_energy_year` | Sensor | kWh | H2 | String PV 3 y superiores | No |
| Energía PV3 total | `sensor.saj_pv3_energy_total` | Sensor | kWh | H2 | String PV 3 y superiores | No |
| Versión del protocolo de identidad | `sensor.saj_identity_protocol_version` | Sensor | - | H2 | - | No |
