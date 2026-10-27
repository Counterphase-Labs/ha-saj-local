[en](../../../en-gb/user/entities/parallel-system.md) | [de](../../../de/user/entities/parallel-system.md) | [nl](../../../nl/user/entities/parallel-system.md) | [fr](../../../fr/user/entities/parallel-system.md) | [zh](../../../zh-hans/user/entities/parallel-system.md) | es | [it](../../../it/user/entities/parallel-system.md) | [pl](../../../pl/user/entities/parallel-system.md) | [sv](../../../sv/user/entities/parallel-system.md)

# Sistema en paralelo

Las lecturas de un sistema de máquinas en paralelo.

La lista de funciones de la integración explica las entidades de Sistema en paralelo en [Equipo opcional](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

63 entidades. Generado por `make docs`. No editar a mano.

Un prefijo definido en Configurar va después de `saj_` en el ID de cada entidad de Sistema en paralelo, por ejemplo `sensor.saj_house_parallel_id` con el prefijo `house`.

| Nombre | ID de entidad | Tipo | Unidad | Modelos | Equipo y números | Habilitada por defecto |
| --- | --- | --- | --- | --- | --- | --- |
| ID de máquina en paralelo | `sensor.saj_parallel_id` | Sensor | - | HS3, H2 | Sistema en paralelo | No |
| Número de máquinas en paralelo | `sensor.saj_parallel_count` | Sensor | - | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: estado de carga de la batería | `sensor.saj_parallel_battery_soc` | Sensor | % | HS3, H2 | Sistema en paralelo | Sí |
| Sistema en paralelo: capacidad de la batería | `sensor.saj_parallel_battery_capacity` | Sensor | Ah | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: potencia del contador B | `sensor.saj_parallel_meter_b_power` | Sensor | W | HS3 | Sistema en paralelo | No |
| Sistema en paralelo: energía solar de hoy | `sensor.saj_parallel_pv_energy_today` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía solar de este mes | `sensor.saj_parallel_pv_energy_month` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía solar de este año | `sensor.saj_parallel_pv_energy_year` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía solar total | `sensor.saj_parallel_pv_energy_total` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía de carga de la batería de hoy | `sensor.saj_parallel_battery_charge_energy_today` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía de carga de la batería de este mes | `sensor.saj_parallel_battery_charge_energy_month` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía de carga de la batería de este año | `sensor.saj_parallel_battery_charge_energy_year` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía de carga de la batería total | `sensor.saj_parallel_battery_charge_energy_total` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía de descarga de la batería de hoy | `sensor.saj_parallel_battery_discharge_energy_today` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía de descarga de la batería de este mes | `sensor.saj_parallel_battery_discharge_energy_month` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía de descarga de la batería de este año | `sensor.saj_parallel_battery_discharge_energy_year` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía de descarga de la batería total | `sensor.saj_parallel_battery_discharge_energy_total` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L1 exportada a la red de hoy | `sensor.saj_parallel_grid_l1_export_energy_today` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L1 exportada a la red de este mes | `sensor.saj_parallel_grid_l1_export_energy_month` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L1 exportada a la red de este año | `sensor.saj_parallel_grid_l1_export_energy_year` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L1 exportada a la red total | `sensor.saj_parallel_grid_l1_export_energy_total` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L2 exportada a la red de hoy | `sensor.saj_parallel_grid_l2_export_energy_today` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L2 exportada a la red de este mes | `sensor.saj_parallel_grid_l2_export_energy_month` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L2 exportada a la red de este año | `sensor.saj_parallel_grid_l2_export_energy_year` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L2 exportada a la red total | `sensor.saj_parallel_grid_l2_export_energy_total` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L3 exportada a la red de hoy | `sensor.saj_parallel_grid_l3_export_energy_today` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L3 exportada a la red de este mes | `sensor.saj_parallel_grid_l3_export_energy_month` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L3 exportada a la red de este año | `sensor.saj_parallel_grid_l3_export_energy_year` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L3 exportada a la red total | `sensor.saj_parallel_grid_l3_export_energy_total` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L1 importada de la red de hoy | `sensor.saj_parallel_grid_l1_import_energy_today` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L1 importada de la red de este mes | `sensor.saj_parallel_grid_l1_import_energy_month` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L1 importada de la red de este año | `sensor.saj_parallel_grid_l1_import_energy_year` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L1 importada de la red total | `sensor.saj_parallel_grid_l1_import_energy_total` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L2 importada de la red de hoy | `sensor.saj_parallel_grid_l2_import_energy_today` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L2 importada de la red de este mes | `sensor.saj_parallel_grid_l2_import_energy_month` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L2 importada de la red de este año | `sensor.saj_parallel_grid_l2_import_energy_year` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L2 importada de la red total | `sensor.saj_parallel_grid_l2_import_energy_total` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L3 importada de la red de hoy | `sensor.saj_parallel_grid_l3_import_energy_today` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L3 importada de la red de este mes | `sensor.saj_parallel_grid_l3_import_energy_month` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L3 importada de la red de este año | `sensor.saj_parallel_grid_l3_import_energy_year` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía L3 importada de la red total | `sensor.saj_parallel_grid_l3_import_energy_total` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía de la carga doméstica de hoy | `sensor.saj_parallel_load_energy_today` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía de la carga doméstica de este mes | `sensor.saj_parallel_load_energy_month` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía de la carga doméstica de este año | `sensor.saj_parallel_load_energy_year` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía de la carga doméstica total | `sensor.saj_parallel_load_energy_total` | Sensor | kWh | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: energía importada de la red de hoy | `sensor.saj_parallel_grid_import_energy_today` | Sensor | kWh | HS3 | Sistema en paralelo | No |
| Sistema en paralelo: energía importada de la red de este mes | `sensor.saj_parallel_grid_import_energy_month` | Sensor | kWh | HS3 | Sistema en paralelo | No |
| Sistema en paralelo: energía importada de la red de este año | `sensor.saj_parallel_grid_import_energy_year` | Sensor | kWh | HS3 | Sistema en paralelo | No |
| Sistema en paralelo: energía importada de la red total | `sensor.saj_parallel_grid_import_energy_total` | Sensor | kWh | HS3 | Sistema en paralelo | No |
| Sistema en paralelo: energía exportada a la red de hoy | `sensor.saj_parallel_grid_export_energy_today` | Sensor | kWh | HS3 | Sistema en paralelo | No |
| Sistema en paralelo: energía exportada a la red de este mes | `sensor.saj_parallel_grid_export_energy_month` | Sensor | kWh | HS3 | Sistema en paralelo | No |
| Sistema en paralelo: energía exportada a la red de este año | `sensor.saj_parallel_grid_export_energy_year` | Sensor | kWh | HS3 | Sistema en paralelo | No |
| Sistema en paralelo: energía exportada a la red total | `sensor.saj_parallel_grid_export_energy_total` | Sensor | kWh | HS3 | Sistema en paralelo | No |
| Sistema en paralelo: energía del contador solar de hoy | `sensor.saj_parallel_pv_meter_energy_today` | Sensor | kWh | HS3 | Sistema en paralelo | No |
| Sistema en paralelo: energía del contador solar de este mes | `sensor.saj_parallel_pv_meter_energy_month` | Sensor | kWh | HS3 | Sistema en paralelo | No |
| Sistema en paralelo: energía del contador solar de este año | `sensor.saj_parallel_pv_meter_energy_year` | Sensor | kWh | HS3 | Sistema en paralelo | No |
| Sistema en paralelo: energía del contador solar total | `sensor.saj_parallel_pv_meter_energy_total` | Sensor | kWh | HS3 | Sistema en paralelo | No |
| Sistema en paralelo: potencia de la carga de respaldo | `sensor.saj_parallel_backup_load_power` | Sensor | W | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: potencia de la batería | `sensor.saj_parallel_battery_power` | Sensor | W | HS3, H2 | Sistema en paralelo | Sí |
| Sistema en paralelo: potencia de carga de la red | `sensor.saj_parallel_grid_load_power` | Sensor | W | HS3, H2 | Sistema en paralelo | No |
| Sistema en paralelo: potencia de la red | `sensor.saj_parallel_grid_power` | Sensor | W | HS3, H2 | Sistema en paralelo | Sí |
| Sistema en paralelo: potencia de la carga doméstica | `sensor.saj_parallel_load_power` | Sensor | W | HS3, H2 | Sistema en paralelo | Sí |
| Sistema en paralelo: potencia solar | `sensor.saj_parallel_pv_power` | Sensor | W | HS3, H2 | Sistema en paralelo | Sí |
