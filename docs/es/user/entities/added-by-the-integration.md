[en](../../../en-gb/user/entities/added-by-the-integration.md) | [de](../../../de/user/entities/added-by-the-integration.md) | [nl](../../../nl/user/entities/added-by-the-integration.md) | [fr](../../../fr/user/entities/added-by-the-integration.md) | [zh](../../../zh-hans/user/entities/added-by-the-integration.md) | es | [it](../../../it/user/entities/added-by-the-integration.md) | [pl](../../../pl/user/entities/added-by-the-integration.md) | [sv](../../../sv/user/entities/added-by-the-integration.md)

# Añadidas por la integración

Entidades que la integración añade fuera del catálogo de registros.

La lista de funciones de la integración explica las entidades de Añadidas por la integración en [Cambiar ajustes](../../../../custom_components/saj_local/docs/features.md#changing-settings) y [Control de potencia](../../../../custom_components/saj_local/docs/features.md#power-control).

7 entidades. Generado por `make docs`. No editar a mano.

Un prefijo definido en Configurar va después de `saj_` en el ID de cada entidad de Añadidas por la integración, por ejemplo `binary_sensor.saj_house_control_allowed` con el prefijo `house`.

| Nombre | ID de entidad | Tipo | Unidad | Modelos | Equipo y números | Habilitada por defecto |
| --- | --- | --- | --- | --- | --- | --- |
| Control permitido | `binary_sensor.saj_control_allowed` | Sensor binario | - | HS3, H2 | - | Sí |
| Control de potencia de la batería | `switch.saj_battery_power_control` | Interruptor | - | HS3, H2 | Batería | No |
| Objetivo de potencia de la batería | `number.saj_battery_power_target` | Número | W | HS3, H2 | Batería | No |
| Control de potencia de la red | `switch.saj_grid_power_control` | Interruptor | - | HS3 | Contador A | No |
| Objetivo de potencia de la red | `number.saj_grid_power_target` | Número | W | HS3 | Contador A | No |
| Control de potencia del inversor | `switch.saj_inverter_power_control` | Interruptor | - | HS3 | - | No |
| Objetivo de potencia del inversor | `number.saj_inverter_power_target` | Número | W | HS3 | - | No |
