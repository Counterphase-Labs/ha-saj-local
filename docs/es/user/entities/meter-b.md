[en](../../../en-gb/user/entities/meter-b.md) | [de](../../../de/user/entities/meter-b.md) | [nl](../../../nl/user/entities/meter-b.md) | [fr](../../../fr/user/entities/meter-b.md) | [zh](../../../zh-hans/user/entities/meter-b.md) | es | [it](../../../it/user/entities/meter-b.md) | [pl](../../../pl/user/entities/meter-b.md) | [sv](../../../sv/user/entities/meter-b.md)

# Contador B

El Contador B, el segundo contador, que mide un inversor solar.

La lista de funciones de la integración explica las entidades de Contador B en [Equipo opcional](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

22 entidades. Generado por `make docs`. No editar a mano.

Un prefijo definido en Configurar va después de `saj_` en el ID de cada entidad de Contador B, por ejemplo `sensor.saj_house_meter_b_l1_voltage` con el prefijo `house`.

| Nombre | ID de entidad | Tipo | Unidad | Modelos | Equipo y números | Habilitada por defecto |
| --- | --- | --- | --- | --- | --- | --- |
| Tensión L1 del contador B | `sensor.saj_meter_b_l1_voltage` | Sensor | V | HS3, H2 | Contador B | No |
| Corriente L1 del contador B | `sensor.saj_meter_b_l1_current` | Sensor | A | HS3, H2 | Contador B | No |
| Potencia L1 del contador B | `sensor.saj_meter_b_l1_power` | Sensor | W | HS3, H2 | Contador B | No |
| Potencia aparente L1 del contador B | `sensor.saj_meter_b_l1_apparent_power` | Sensor | VA | HS3, H2 | Contador B | No |
| Factor de potencia L1 del contador B | `sensor.saj_meter_b_l1_power_factor` | Sensor | - | HS3, H2 | Contador B | No |
| Frecuencia L1 del contador B | `sensor.saj_meter_b_l1_frequency` | Sensor | Hz | HS3, H2 | Contador B | No |
| Tensión L2 del contador B | `sensor.saj_meter_b_l2_voltage` | Sensor | V | HS3, H2 | Contador B; Fase 2 y superiores | No |
| Corriente L2 del contador B | `sensor.saj_meter_b_l2_current` | Sensor | A | HS3, H2 | Contador B; Fase 2 y superiores | No |
| Potencia L2 del contador B | `sensor.saj_meter_b_l2_power` | Sensor | W | HS3, H2 | Contador B; Fase 2 y superiores | No |
| Potencia aparente L2 del contador B | `sensor.saj_meter_b_l2_apparent_power` | Sensor | VA | HS3, H2 | Contador B; Fase 2 y superiores | No |
| Factor de potencia L2 del contador B | `sensor.saj_meter_b_l2_power_factor` | Sensor | - | HS3, H2 | Contador B; Fase 2 y superiores | No |
| Frecuencia L2 del contador B | `sensor.saj_meter_b_l2_frequency` | Sensor | Hz | HS3, H2 | Contador B; Fase 2 y superiores | No |
| Tensión L3 del contador B | `sensor.saj_meter_b_l3_voltage` | Sensor | V | HS3, H2 | Contador B; Fase 3 y superiores | No |
| Corriente L3 del contador B | `sensor.saj_meter_b_l3_current` | Sensor | A | HS3, H2 | Contador B; Fase 3 y superiores | No |
| Potencia L3 del contador B | `sensor.saj_meter_b_l3_power` | Sensor | W | HS3, H2 | Contador B; Fase 3 y superiores | No |
| Potencia aparente L3 del contador B | `sensor.saj_meter_b_l3_apparent_power` | Sensor | VA | HS3, H2 | Contador B; Fase 3 y superiores | No |
| Factor de potencia L3 del contador B | `sensor.saj_meter_b_l3_power_factor` | Sensor | - | HS3, H2 | Contador B; Fase 3 y superiores | No |
| Frecuencia L3 del contador B | `sensor.saj_meter_b_l3_frequency` | Sensor | Hz | HS3, H2 | Contador B; Fase 3 y superiores | No |
| Potencia reactiva L1 del contador B | `sensor.saj_meter_b_l1_reactive_power` | Sensor | var | HS3 | Contador B | No |
| Potencia reactiva L2 del contador B | `sensor.saj_meter_b_l2_reactive_power` | Sensor | var | HS3 | Contador B; Fase 2 y superiores | No |
| Potencia reactiva L3 del contador B | `sensor.saj_meter_b_l3_reactive_power` | Sensor | var | HS3 | Contador B; Fase 3 y superiores | No |
| Potencia del contador B | `sensor.saj_meter_b_power` | Sensor | W | HS3, H2 | Contador B | Sí |
