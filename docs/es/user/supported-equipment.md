[en](../../en-gb/user/supported-equipment.md) | [de](../../de/user/supported-equipment.md) | [nl](../../nl/user/supported-equipment.md) | [fr](../../fr/user/supported-equipment.md) | [zh](../../zh-hans/user/supported-equipment.md) | es | [it](../../it/user/supported-equipment.md) | [pl](../../pl/user/supported-equipment.md) | [sv](../../sv/user/supported-equipment.md)

# Equipos compatibles

La página Equipos compatibles lista los productos SAJ que admite SAJ Local, el equipo opcional que puede tener cada modelo y qué aún no es compatible. La lista completa de lo que hace la configuración está en la sección [Configuración y detección](../../../custom_components/saj_local/docs/features.md#setup-and-detection) de la lista de funciones de la integración.

## Modelos compatibles

SAJ Local reconoce un modelo a partir del tipo de dispositivo que informa el inversor. Cualquier otro tipo de dispositivo no se reconoce.

| Modelo | Se reconoce como | Equipo opcional que detecta SAJ Local |
| --- | --- | --- |
| HS3 | Tipo de dispositivo `0x1610`, tres fases | Batería, Contador A, Contador B, cargador de VE, sistema en paralelo |
| H2, monofásico, dos strings solares | Tipo de dispositivo `0x005a` | Batería, Contador A, Contador B, sistema en paralelo |
| H2, monofásico, tres strings solares | Tipo de dispositivo `0x005b` | Batería, Contador A, Contador B, sistema en paralelo |

Las diferencias entre los modelos que notas al usarlos:

- **Cargador de VE:** solo el HS3. El H2 no tiene entidades de cargador de VE, franjas de cargador de VE ni sección de cargador de VE en la tarjeta de controles.
- **Módulos de batería:** un H2 tiene entidades para hasta cinco módulos de batería. Un HS3 tiene entidades para un módulo de batería. Consulta el [equipo opcional](optional-equipment.md).
- **EMS:** solo el HS3. Consulta [cambiar ajustes](changing-settings.md#ems).
- **Control de potencia:** el HS3 ofrece Batería, Red e Inversor. El H2 ofrece solo Batería. Consulta el [control de potencia](power-control.md).

El [equipo opcional](optional-equipment.md) explica cómo funciona la detección y cómo anularla. La [referencia de entidades](entities/README.md) lista qué modelo y qué equipo necesita cada entidad.

## Aún no compatible

- La detección automática reconoce solo los tres tipos de dispositivo de la tabla. Otros productos SAJ, como el HS2, el H1 y el AS1, no se reconocen.
- Otras variantes del H2, como el H2 trifásico, informan de otros tipos de dispositivo y no se reconocen automáticamente. Puedes elegir el modelo a mano, y entonces SAJ Local marca el modelo como sin verificar. Las lecturas pueden ser erróneas, porque SAJ Local no puede comprobarlas. Consulta los [primeros pasos](getting-started.md#cuando-no-se-reconoce-el-inversor).
- Cambiar ajustes en un sistema cuyo modelo está sin verificar. La lectura funciona y se rechaza cualquier cambio.

## En qué se basa la compatibilidad

La compatibilidad con el HS3 se ha verificado a mano en un HS3 real. La compatibilidad con el H2 se basa en la documentación del protocolo de SAJ y en informes de campo, y no se ha verificado a mano en un H2. La escritura de ajustes y el control de potencia en el H2 también se basan en documentación e informes de campo.
