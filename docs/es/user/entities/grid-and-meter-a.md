[en](../../../en-gb/user/entities/grid-and-meter-a.md) | [de](../../../de/user/entities/grid-and-meter-a.md) | [nl](../../../nl/user/entities/grid-and-meter-a.md) | [fr](../../../fr/user/entities/grid-and-meter-a.md) | [zh](../../../zh-hans/user/entities/grid-and-meter-a.md) | es | [it](../../../it/user/entities/grid-and-meter-a.md) | [pl](../../../pl/user/entities/grid-and-meter-a.md) | [sv](../../../sv/user/entities/grid-and-meter-a.md)

# Red y Contador A

La conexión a la red y el Contador A, el contador de la red.

La lista de funciones de la integración explica las entidades de Red y Contador A en [Dispositivos y entidades](../../../../custom_components/saj_local/docs/features.md#devices-and-entities) y [Equipo opcional](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

88 entidades. Generado por `make docs`. No editar a mano.

Un prefijo definido en Configurar va después de `saj_` en el ID de cada entidad de Red y Contador A, por ejemplo `sensor.saj_house_grid_connection_countdown` con el prefijo `house`.

| Nombre | ID de entidad | Tipo | Unidad | Modelos | Equipo y números | Habilitada por defecto |
| --- | --- | --- | --- | --- | --- | --- |
| Cuenta atrás de conexión a la red | `sensor.saj_grid_connection_countdown` | Sensor | s | HS3, H2 | - | No |
| Tensión L1 de la red | `sensor.saj_grid_l1_voltage` | Sensor | V | HS3, H2 | - | Sí |
| Corriente L1 de la red | `sensor.saj_grid_l1_current` | Sensor | A | HS3, H2 | - | No |
| Frecuencia L1 de la red | `sensor.saj_grid_l1_frequency` | Sensor | Hz | HS3, H2 | - | Sí |
| Corriente continua L1 de la red | `sensor.saj_grid_l1_dc_current` | Sensor | mA | HS3, H2 | - | No |
| Potencia L1 de la red | `sensor.saj_grid_l1_power` | Sensor | W | HS3, H2 | - | No |
| Potencia aparente L1 de la red | `sensor.saj_grid_l1_apparent_power` | Sensor | VA | HS3, H2 | - | No |
| Factor de potencia L1 de la red | `sensor.saj_grid_l1_power_factor` | Sensor | - | HS3, H2 | - | No |
| Tensión L2 de la red | `sensor.saj_grid_l2_voltage` | Sensor | V | HS3, H2 | Fase 2 y superiores | Sí |
| Corriente L2 de la red | `sensor.saj_grid_l2_current` | Sensor | A | HS3, H2 | Fase 2 y superiores | No |
| Frecuencia L2 de la red | `sensor.saj_grid_l2_frequency` | Sensor | Hz | HS3, H2 | Fase 2 y superiores | No |
| Corriente continua L2 de la red | `sensor.saj_grid_l2_dc_current` | Sensor | mA | HS3, H2 | Fase 2 y superiores | No |
| Potencia L2 de la red | `sensor.saj_grid_l2_power` | Sensor | W | HS3, H2 | Fase 2 y superiores | No |
| Potencia aparente L2 de la red | `sensor.saj_grid_l2_apparent_power` | Sensor | VA | HS3, H2 | Fase 2 y superiores | No |
| Factor de potencia L2 de la red | `sensor.saj_grid_l2_power_factor` | Sensor | - | HS3, H2 | Fase 2 y superiores | No |
| Tensión L3 de la red | `sensor.saj_grid_l3_voltage` | Sensor | V | HS3, H2 | Fase 3 y superiores | Sí |
| Corriente L3 de la red | `sensor.saj_grid_l3_current` | Sensor | A | HS3, H2 | Fase 3 y superiores | No |
| Frecuencia L3 de la red | `sensor.saj_grid_l3_frequency` | Sensor | Hz | HS3, H2 | Fase 3 y superiores | No |
| Corriente continua L3 de la red | `sensor.saj_grid_l3_dc_current` | Sensor | mA | HS3, H2 | Fase 3 y superiores | No |
| Potencia L3 de la red | `sensor.saj_grid_l3_power` | Sensor | W | HS3, H2 | Fase 3 y superiores | No |
| Potencia aparente L3 de la red | `sensor.saj_grid_l3_apparent_power` | Sensor | VA | HS3, H2 | Fase 3 y superiores | No |
| Factor de potencia L3 de la red | `sensor.saj_grid_l3_power_factor` | Sensor | - | HS3, H2 | Fase 3 y superiores | No |
| Tensión de salida L1 a la red | `sensor.saj_grid_output_l1_voltage` | Sensor | V | HS3, H2 | - | No |
| Corriente de salida L1 a la red | `sensor.saj_grid_output_l1_current` | Sensor | A | HS3, H2 | - | No |
| Frecuencia de salida L1 a la red | `sensor.saj_grid_output_l1_frequency` | Sensor | Hz | HS3, H2 | - | No |
| Potencia de salida L1 a la red | `sensor.saj_grid_output_l1_power` | Sensor | W | HS3, H2 | - | No |
| Tensión de salida L2 a la red | `sensor.saj_grid_output_l2_voltage` | Sensor | V | HS3, H2 | Fase 2 y superiores | No |
| Potencia de salida L2 a la red | `sensor.saj_grid_output_l2_power` | Sensor | W | HS3, H2 | Fase 2 y superiores | No |
| Tensión de salida L3 a la red | `sensor.saj_grid_output_l3_voltage` | Sensor | V | HS3, H2 | Fase 3 y superiores | No |
| Potencia de salida L3 a la red | `sensor.saj_grid_output_l3_power` | Sensor | W | HS3, H2 | Fase 3 y superiores | No |
| Potencia de la red | `sensor.saj_grid_power` | Sensor | W | HS3, H2 | - | Sí |
| Potencia de carga de la red | `sensor.saj_grid_load_power` | Sensor | W | HS3, H2 | - | No |
| Energía L1 exportada a la red de hoy | `sensor.saj_grid_l1_export_energy_today` | Sensor | kWh | HS3, H2 | - | No |
| Energía L1 exportada a la red de este mes | `sensor.saj_grid_l1_export_energy_month` | Sensor | kWh | HS3, H2 | - | No |
| Energía L1 exportada a la red de este año | `sensor.saj_grid_l1_export_energy_year` | Sensor | kWh | HS3, H2 | - | No |
| Energía L1 exportada a la red total | `sensor.saj_grid_l1_export_energy_total` | Sensor | kWh | HS3, H2 | - | No |
| Energía L1 importada de la red de hoy | `sensor.saj_grid_l1_import_energy_today` | Sensor | kWh | HS3, H2 | - | No |
| Energía L1 importada de la red de este mes | `sensor.saj_grid_l1_import_energy_month` | Sensor | kWh | HS3, H2 | - | No |
| Energía L1 importada de la red de este año | `sensor.saj_grid_l1_import_energy_year` | Sensor | kWh | HS3, H2 | - | No |
| Energía L1 importada de la red total | `sensor.saj_grid_l1_import_energy_total` | Sensor | kWh | HS3, H2 | - | No |
| Energía L2 exportada a la red de hoy | `sensor.saj_grid_l2_export_energy_today` | Sensor | kWh | HS3, H2 | Fase 2 y superiores | No |
| Energía L2 exportada a la red de este mes | `sensor.saj_grid_l2_export_energy_month` | Sensor | kWh | HS3, H2 | Fase 2 y superiores | No |
| Energía L2 exportada a la red de este año | `sensor.saj_grid_l2_export_energy_year` | Sensor | kWh | HS3, H2 | Fase 2 y superiores | No |
| Energía L2 exportada a la red total | `sensor.saj_grid_l2_export_energy_total` | Sensor | kWh | HS3, H2 | Fase 2 y superiores | No |
| Energía L3 exportada a la red de hoy | `sensor.saj_grid_l3_export_energy_today` | Sensor | kWh | HS3, H2 | Fase 3 y superiores | No |
| Energía L3 exportada a la red de este mes | `sensor.saj_grid_l3_export_energy_month` | Sensor | kWh | HS3, H2 | Fase 3 y superiores | No |
| Energía L3 exportada a la red de este año | `sensor.saj_grid_l3_export_energy_year` | Sensor | kWh | HS3, H2 | Fase 3 y superiores | No |
| Energía L3 exportada a la red total | `sensor.saj_grid_l3_export_energy_total` | Sensor | kWh | HS3, H2 | Fase 3 y superiores | No |
| Energía L2 importada de la red de hoy | `sensor.saj_grid_l2_import_energy_today` | Sensor | kWh | HS3, H2 | Fase 2 y superiores | No |
| Energía L2 importada de la red de este mes | `sensor.saj_grid_l2_import_energy_month` | Sensor | kWh | HS3, H2 | Fase 2 y superiores | No |
| Energía L2 importada de la red de este año | `sensor.saj_grid_l2_import_energy_year` | Sensor | kWh | HS3, H2 | Fase 2 y superiores | No |
| Energía L2 importada de la red total | `sensor.saj_grid_l2_import_energy_total` | Sensor | kWh | HS3, H2 | Fase 2 y superiores | No |
| Energía L3 importada de la red de hoy | `sensor.saj_grid_l3_import_energy_today` | Sensor | kWh | HS3, H2 | Fase 3 y superiores | No |
| Energía L3 importada de la red de este mes | `sensor.saj_grid_l3_import_energy_month` | Sensor | kWh | HS3, H2 | Fase 3 y superiores | No |
| Energía L3 importada de la red de este año | `sensor.saj_grid_l3_import_energy_year` | Sensor | kWh | HS3, H2 | Fase 3 y superiores | No |
| Energía L3 importada de la red total | `sensor.saj_grid_l3_import_energy_total` | Sensor | kWh | HS3, H2 | Fase 3 y superiores | No |
| Energía importada de la red de hoy | `sensor.saj_grid_import_energy_today` | Sensor | kWh | HS3, H2 | - | Sí |
| Energía importada de la red de este mes | `sensor.saj_grid_import_energy_month` | Sensor | kWh | HS3, H2 | - | No |
| Energía importada de la red de este año | `sensor.saj_grid_import_energy_year` | Sensor | kWh | HS3, H2 | - | No |
| Energía importada de la red total | `sensor.saj_grid_import_energy_total` | Sensor | kWh | HS3, H2 | - | Sí |
| Energía exportada a la red de hoy | `sensor.saj_grid_export_energy_today` | Sensor | kWh | HS3, H2 | - | Sí |
| Energía exportada a la red de este mes | `sensor.saj_grid_export_energy_month` | Sensor | kWh | HS3, H2 | - | No |
| Energía exportada a la red de este año | `sensor.saj_grid_export_energy_year` | Sensor | kWh | HS3, H2 | - | No |
| Energía exportada a la red total | `sensor.saj_grid_export_energy_total` | Sensor | kWh | HS3, H2 | - | Sí |
| Tensión L1 del contador A | `sensor.saj_meter_a_l1_voltage` | Sensor | V | HS3, H2 | Contador A | No |
| Corriente L1 del contador A | `sensor.saj_meter_a_l1_current` | Sensor | A | HS3, H2 | Contador A | No |
| Potencia L1 del contador A | `sensor.saj_meter_a_l1_power` | Sensor | W | HS3, H2 | Contador A | No |
| Potencia aparente L1 del contador A | `sensor.saj_meter_a_l1_apparent_power` | Sensor | VA | HS3, H2 | Contador A | No |
| Factor de potencia L1 del contador A | `sensor.saj_meter_a_l1_power_factor` | Sensor | - | HS3, H2 | Contador A | No |
| Frecuencia L1 del contador A | `sensor.saj_meter_a_l1_frequency` | Sensor | Hz | HS3, H2 | Contador A | No |
| Tensión L2 del contador A | `sensor.saj_meter_a_l2_voltage` | Sensor | V | HS3, H2 | Contador A; Fase 2 y superiores | No |
| Corriente L2 del contador A | `sensor.saj_meter_a_l2_current` | Sensor | A | HS3, H2 | Contador A; Fase 2 y superiores | No |
| Potencia L2 del contador A | `sensor.saj_meter_a_l2_power` | Sensor | W | HS3, H2 | Contador A; Fase 2 y superiores | No |
| Potencia aparente L2 del contador A | `sensor.saj_meter_a_l2_apparent_power` | Sensor | VA | HS3, H2 | Contador A; Fase 2 y superiores | No |
| Factor de potencia L2 del contador A | `sensor.saj_meter_a_l2_power_factor` | Sensor | - | HS3, H2 | Contador A; Fase 2 y superiores | No |
| Frecuencia L2 del contador A | `sensor.saj_meter_a_l2_frequency` | Sensor | Hz | HS3, H2 | Contador A; Fase 2 y superiores | No |
| Tensión L3 del contador A | `sensor.saj_meter_a_l3_voltage` | Sensor | V | HS3, H2 | Contador A; Fase 3 y superiores | No |
| Corriente L3 del contador A | `sensor.saj_meter_a_l3_current` | Sensor | A | HS3, H2 | Contador A; Fase 3 y superiores | No |
| Potencia L3 del contador A | `sensor.saj_meter_a_l3_power` | Sensor | W | HS3, H2 | Contador A; Fase 3 y superiores | No |
| Potencia aparente L3 del contador A | `sensor.saj_meter_a_l3_apparent_power` | Sensor | VA | HS3, H2 | Contador A; Fase 3 y superiores | No |
| Factor de potencia L3 del contador A | `sensor.saj_meter_a_l3_power_factor` | Sensor | - | HS3, H2 | Contador A; Fase 3 y superiores | No |
| Frecuencia L3 del contador A | `sensor.saj_meter_a_l3_frequency` | Sensor | Hz | HS3, H2 | Contador A; Fase 3 y superiores | No |
| Potencia reactiva L1 del contador A | `sensor.saj_meter_a_l1_reactive_power` | Sensor | var | HS3 | Contador A | No |
| Potencia reactiva L2 del contador A | `sensor.saj_meter_a_l2_reactive_power` | Sensor | var | HS3 | Contador A; Fase 2 y superiores | No |
| Potencia reactiva L3 del contador A | `sensor.saj_meter_a_l3_reactive_power` | Sensor | var | HS3 | Contador A; Fase 3 y superiores | No |
| Potencia del contador A | `sensor.saj_meter_a_power` | Sensor | W | HS3, H2 | Contador A | Sí |
| Tipo de red | `sensor.saj_grid_type` | Sensor | - | H2 | - | No |
| Potencia aparente de la red | `sensor.saj_grid_apparent_power` | Sensor | VA | H2 | - | No |
