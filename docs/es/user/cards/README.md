[en](../../../en-gb/user/cards/README.md) | [de](../../../de/user/cards/README.md) | [nl](../../../nl/user/cards/README.md) | [fr](../../../fr/user/cards/README.md) | [zh](../../../zh-hans/user/cards/README.md) | es | [it](../../../it/user/cards/README.md) | [pl](../../../pl/user/cards/README.md) | [sv](../../../sv/user/cards/README.md)

# Tarjetas del panel

La página Tarjetas del panel explica cómo añadir las tarjetas de SAJ Local a un panel y elegir un sistema, y lista lo que muestra cada elemento. Las listas completas están en las secciones [Elementos y configuración](../../../../frontend/docs/features.md#elements-and-setup) y [Tema e idioma](../../../../frontend/docs/features.md#theme-and-language) de la lista de funciones de las tarjetas, y en la sección [Tarjetas](../../../../custom_components/saj_local/docs/features.md#cards) de la lista de funciones de la integración.

SAJ Local ofrece las tarjetas y las registra en Home Assistant cuando Home Assistant arranca. Las tarjetas aparecen en el selector de tarjetas, así que no hay ningún recurso que añadir ni ninguna caché que borrar.

## Elementos

| Elemento | Qué muestra el elemento |
| --- | --- |
| [Tarjeta de flujo de potencia](power-flow-card.md) | La potencia en vivo entre solar, batería, red, casa y el equipo opcional. |
| [Tarjeta de estado](status-card.md) | El estado de funcionamiento, el modo de aplicación, las lecturas clave, la energía de hoy, un resumen de fallos y si se permite el control. |
| [Tarjeta de fallos](faults-card.md) | Los fallos activos de cada equipo, y un botón Borrar fallo. |
| [Tarjeta de batería](battery-card.md) | El estado de carga con los límites marcados, las lecturas de la batería y un grupo de filas por cada módulo. |
| [Tarjeta de controles](controls-card.md) | Los ajustes del sistema en secciones. |
| [Tarjeta de programación](schedule-card.md) | Las franjas de carga, de descarga y del cargador de VE, una línea de tiempo semanal y un editor de franjas. |
| [Función de tarjeta mosaico de días de la semana](weekdays-feature.md) | Siete botones de días en una tarjeta mosaico, para los días de una franja. |
| [Insignia de estado](status-badge.md) | Una insignia con el estado de funcionamiento y el número de equipos con un fallo activo. |

## Añadir un elemento

1. Edita un panel y elige Añadir tarjeta. Para la función de días de la semana, añade una tarjeta mosaico y abre las funciones de la tarjeta mosaico. Para la insignia, edita las insignias del panel.
2. Elige el elemento de SAJ Local en el selector. Las seis tarjetas muestran una vista previa en vivo.
3. Elige el sistema en el campo Sistema del editor visual. Una tarjeta o insignia nueva empieza con el primer sistema. La función de días de la semana no tiene editor, porque la función usa la entidad de la tarjeta mosaico.

Una casa con dos sistemas añade una tarjeta una vez por sistema. El título de una tarjeta es el nombre del dispositivo del sistema seguido del modelo, por ejemplo SAJ HS3 (12000 W). SAJ Local añade el número de serie solo cuando dos sistemas tendrían de otro modo un título idéntico. Cambia el nombre de cada dispositivo en Home Assistant si quieres otros títulos.

Los elementos encuentran las entidades de un sistema mediante el registro de entidades, y no por ID de entidad, así que los elementos siguen funcionando cuando cambias un [prefijo](../entities-and-prefix.md#el-prefijo).

## Qué hace cada elemento

- **Solo lo que tiene el sistema.** Una parte cuya entidad no existe o está deshabilitada no se dibuja, así que cada tarjeta muestra solo lo que tiene el sistema. Una parte de un modelo aparece solo en ese modelo, y la página de cada elemento nombra las partes.
- **Una tarjeta vacía dice por qué.** Una tarjeta sin ninguna de sus entidades habilitada dice qué tipo de entidad habilitar, con un enlace a la página del dispositivo del sistema.
- **Un sistema que no responde.** Una tarjeta lo indica y atenúa los valores.
- **Pulsa un valor.** Al pulsar un valor se abren los detalles de la entidad en Home Assistant.
- **Controles bloqueados.** Mientras [Permitir control](../changing-settings.md#permitir-control) está desactivado para el sistema, todos los controles están deshabilitados y un candado enlaza con los ajustes de la integración. Activar Permitir control también habilita las entidades que necesitan las tarjetas, consulta [el conjunto de control](../changing-settings.md#el-conjunto-de-control).
- **Un cambio por decisión.** Un control deslizante cambia el inversor cuando lo sueltas. Un campo numérico cambia el inversor al pulsar Intro o al salir del campo. Una lista, un interruptor o un campo de hora cambia el inversor al cambiar. El control muestra entonces el valor que tiene el inversor, y un rechazo aparece bajo el control con las palabras de la integración.

## Tema e idioma

Los elementos siguen el tema de Home Assistant. Los nombres de las entidades, los valores y los estados usan el formato y el idioma de Home Assistant. Los textos de las tarjetas existen en inglés, alemán, neerlandés, francés, chino simplificado, español, italiano, polaco y sueco. Un panel en cualquier otro idioma muestra los textos de las tarjetas en inglés.

## Aún no compatible

- Textos de las tarjetas en idiomas distintos de los nueve anteriores.
