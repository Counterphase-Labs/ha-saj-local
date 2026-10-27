[en](../../../en-gb/user/entities/settings.md) | [de](../../../de/user/entities/settings.md) | [nl](../../../nl/user/entities/settings.md) | [fr](../../../fr/user/entities/settings.md) | [zh](../../../zh-hans/user/entities/settings.md) | es | [it](../../../it/user/entities/settings.md) | [pl](../../../pl/user/entities/settings.md) | [sv](../../../sv/user/entities/settings.md)

# Ajustes

Ajustes y órdenes que cambian el inversor.

La lista de funciones de la integración explica las entidades de Ajustes en [Cambiar ajustes](../../../../custom_components/saj_local/docs/features.md#changing-settings).

22 entidades. Generado por `make docs`. No editar a mano.

Un prefijo definido en Configurar va después de `saj_` en el ID de cada entidad de Ajustes, por ejemplo `number.saj_house_passive_mode` con el prefijo `house`.

| Nombre | ID de entidad | Tipo | Unidad | Modelos | Equipo y números | Habilitada por defecto |
| --- | --- | --- | --- | --- | --- | --- |
| Modo pasivo | `number.saj_passive_mode` | Número | - | HS3, H2 | - | No |
| Potencia de carga de la red en modo pasivo | `number.saj_passive_grid_charge_power` | Número | % | HS3, H2 | - | No |
| Potencia de descarga de la red en modo pasivo | `number.saj_passive_grid_discharge_power` | Número | % | HS3, H2 | - | No |
| Modo de aplicación | `select.saj_application_mode` | Seleccionar | - | HS3, H2 | - | Sí |
| Límite de potencia de importación de la red | `number.saj_grid_import_power_limit` | Número | % | HS3, H2 | - | No |
| Límite de potencia de exportación a la red | `number.saj_grid_export_power_limit` | Número | % | HS3, H2 | - | No |
| Potencia del límite de exportación | `number.saj_export_limit_power` | Número | % | HS3, H2 | - | No |
| Corriente del límite de exportación | `number.saj_export_limit_current` | Número | A | HS3, H2 | - | No |
| Modo del límite de exportación | `select.saj_export_limit_mode` | Seleccionar | - | HS3, H2 | - | No |
| Modo inactivo del horario programado | `select.saj_time_of_use_idle_mode` | Seleccionar | - | HS3, H2 | - | No |
| Descarga a la red del horario programado | `switch.saj_time_of_use_grid_discharge` | Interruptor | - | HS3, H2 | - | No |
| Modo LED | `select.saj_led_mode` | Seleccionar | - | HS3, H2 | - | No |
| Cargador de VE habilitado | `switch.saj_ev_enabled` | Interruptor | - | HS3 | - | No |
| Borrar fallo actual | `button.saj_clear_current_fault` | Botón | - | HS3, H2 | - | No |
| Reiniciar inversor | `button.saj_restart_inverter` | Botón | - | HS3, H2 | - | No |
| Sincronizar reloj | `button.saj_synchronise_clock` | Botón | - | HS3, H2 | - | No |
| Tiempo de espera de EMS | `number.saj_ems_timeout` | Número | s | HS3 | - | No |
| Límite de potencia de importación del inversor por EMS | `number.saj_ems_inverter_import_power_limit` | Número | % | HS3 | - | No |
| Límite de potencia de exportación del inversor por EMS | `number.saj_ems_inverter_export_power_limit` | Número | % | HS3 | - | No |
| Límite de potencia solar por EMS | `number.saj_ems_pv_power_limit` | Número | % | HS3 | - | No |
| Quitar límite de potencia solar por EMS | `button.saj_ems_pv_power_limit_remove` | Botón | - | HS3 | - | No |
| Zumbador | `switch.saj_buzzer` | Interruptor | - | H2 | - | No |
