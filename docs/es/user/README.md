[en](../../en-gb/user/README.md) | [de](../../de/user/README.md) | [nl](../../nl/user/README.md) | [fr](../../fr/user/README.md) | [zh](../../zh-hans/user/README.md) | es | [it](../../it/user/README.md) | [pl](../../pl/user/README.md) | [sv](../../sv/user/README.md)

# Documentación de usuario de SAJ Local

SAJ Local es una integración local de Home Assistant. SAJ Local lee un sistema solar SAJ HS3 o H2 directamente del inversor por Modbus TCP en tu propia red y, cuando permites el control, cambia los ajustes del inversor desde Home Assistant. SAJ Local no necesita ninguna cuenta en la nube y limita las solicitudes al inversor para que el módulo de comunicación del inversor siga funcionando.

SAJ Local es una integración no oficial, creada por la comunidad. SAJ no fabrica, no respalda ni apoya SAJ Local. Consulta el [descargo de responsabilidad](#descargo-de-responsabilidad).

SAJ Local aún no tiene ninguna versión estable. Toda versión anterior a `1.0.0` es una beta, consulta [versiones beta](installation.md#versiones-beta). Cada página siguiente indica qué aún no es compatible. La documentación cubre el HS3 y el H2, y marca las diferencias con una nota como «solo HS3». Las capturas de pantalla proceden de sistemas simulados, así que las lecturas no son reales.

## Empieza aquí

1. [Instala SAJ Local](installation.md) con HACS.
2. Comprueba que tu inversor figura en los [equipos compatibles](supported-equipment.md).
3. [Primeros pasos](getting-started.md): añade tu primer sistema.
4. Lee sobre el [equipo opcional](optional-equipment.md), que SAJ Local detecta por ti.

## Entiende tu sistema

- [Entidades y el prefijo](entities-and-prefix.md): qué son las entidades, cómo se forman los ID de entidad y cómo añadir un prefijo.
- [Referencia de entidades](entities/README.md): todas las entidades, con el ID de entidad, los modelos, el equipo y el valor por defecto. Generada a partir de la integración.
- [Sondeo](polling.md): con qué frecuencia se lee el inversor y cómo leer algunas entidades más rápido o más despacio.
- [Proteger el inversor](protecting-the-inverter.md): los límites que SAJ Local aplica a sus propias solicitudes.

## Cambia cosas

- [Cambiar ajustes](changing-settings.md): permitir el control, cambiar ajustes y usar EMS.
- [Control de potencia](power-control.md): mantén la batería, la conexión a la red o el inversor a una potencia fija, a mano o con una programación.
- [Sustituir el inversor](replacing-the-inverter.md): pasa un sistema a un inversor nuevo, o entre un H2 y un HS3, y conserva el historial.

## Paneles

- [Tarjetas del panel](cards/README.md): las tarjetas, la función de la tarjeta mosaico y la insignia que SAJ Local añade a Home Assistant.

## Términos

- [Nomenclatura](nomenclature.md): los términos de SAJ y de Home Assistant que usan la integración, las tarjetas y la documentación, con su significado.

## Cuando algo va mal

- [Fallos del dispositivo y reparaciones](faults-and-repairs.md): los fallos que informa el equipo y los avisos de reparación que genera SAJ Local.
- [Solución de problemas](troubleshooting.md): diagnósticos, registro de depuración y dónde pedir ayuda.

## Qué puede hacer cada parte

Las listas de funciones indican qué está construido hoy: [la integración](../../../custom_components/saj_local/docs/features.md) y [las tarjetas](../../../frontend/docs/features.md).

Desarrolladores: consulta la [documentación para desarrolladores](../developer/README.md).

## Descargo de responsabilidad

SAJ Local es una integración independiente, creada por la comunidad. SAJ Local no está afiliada a SAJ (Guangzhou Sanjing Electric Co., Ltd.), y SAJ y sus filiales y empresas asociadas no han autorizado, patrocinado ni respaldado SAJ Local.

SAJ, el logotipo de SAJ y todos los nombres de producto, nombres de modelo y marcas relacionados son propiedad de sus respectivos titulares. La documentación usa los nombres solo para identificar el equipo con el que funciona SAJ Local.

El software se proporciona tal cual, sin garantía de ningún tipo. Usas SAJ Local bajo tu propia responsabilidad: los autores no aceptan ninguna responsabilidad por daños al equipo, pérdida de datos, pérdida de la garantía ni ninguna otra consecuencia de usar SAJ Local. La advertencia se aplica en particular a la escritura de ajustes en tu inversor.

## Agradecimientos

La compatibilidad con el H2 se basa en la investigación de registros y las pruebas de campo de stanus74 en [SAJ H2 Modbus](https://github.com/stanus74/home-assistant-saj-h2-modbus). Gracias.
