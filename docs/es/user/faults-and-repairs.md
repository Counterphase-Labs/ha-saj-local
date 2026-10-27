[en](../../en-gb/user/faults-and-repairs.md) | [de](../../de/user/faults-and-repairs.md) | [nl](../../nl/user/faults-and-repairs.md) | [fr](../../fr/user/faults-and-repairs.md) | [zh](../../zh-hans/user/faults-and-repairs.md) | es | [it](../../it/user/faults-and-repairs.md) | [pl](../../pl/user/faults-and-repairs.md) | [sv](../../sv/user/faults-and-repairs.md)

# Fallos del dispositivo y reparaciones

La página Fallos del dispositivo y reparaciones explica cómo muestra SAJ Local los fallos que informan el inversor, la batería y el cargador de VE, y qué avisos de reparación genera SAJ Local en Home Assistant. La lista completa del comportamiento de los fallos está en la sección [Fallos del dispositivo y reparaciones](../../../custom_components/saj_local/docs/features.md#device-faults-and-repairs) de la lista de funciones de la integración. Cada entidad de fallo está en las [entidades de fallos](entities/faults.md) de la referencia de entidades.

Los fallos del dispositivo y los avisos de reparación son cosas distintas. Un fallo del dispositivo es una entidad que informa de lo que dice el equipo. Un aviso de reparación es un problema con la conexión de SAJ Local con el equipo o con la configuración de SAJ Local, y Home Assistant lista el aviso en Ajustes y Reparaciones.

## Fallos del dispositivo

Cada fallo con nombre del inversor, de la batería y del cargador de VE es un sensor binario con la clase de dispositivo de problema, habilitado por defecto. Un fallo tiene historial y puede activar una automatización.

- **Resumen:** el inversor, la batería y el cargador de VE tienen cada uno un fallo de resumen, por ejemplo Fallo del inversor, que está activo cuando el equipo informa de cualquier cosa.
- **No reconocido:** cada equipo tiene además un fallo no reconocido que está activo cuando el inversor activa un bit sin significado documentado. La [descarga de diagnósticos](troubleshooting.md#descargar-los-diagnósticos) lista el registro y el bit, para que puedas informar del bit.
- **Un único ID de entidad en todos los modelos:** un fallo tiene un único ID de entidad en todos los modelos que informan del fallo. Un fallo que un modelo no informa no tiene entidad en ese modelo.
- **Módulos de batería:** cada módulo de batería tiene una entidad de fallo y una de advertencia. Un HS3 tiene un módulo. Un H2 tiene hasta cuatro.
- **Equipo que no está instalado:** los fallos de la batería existen solo cuando hay una batería instalada, y los del cargador de VE solo cuando hay un cargador de VE instalado. Consulta el [equipo opcional](optional-equipment.md).
- **Un registro de fallos que no se puede leer:** los fallos que dependen del registro no están disponibles. SAJ Local no adivina.
- **El registro:** un fallo que se activa escribe una advertencia que nombra el sistema y el fallo. Cuando el fallo se borra, SAJ Local escribe una línea informativa.

La [tarjeta de fallos](cards/faults-card.md) lista los fallos activos de un sistema en un panel, con cuánto hace que empezó cada uno. El botón Borrar fallo de la tarjeta envía la orden Borrar fallo actual, que necesita [Permitir control](changing-settings.md#permitir-control).

## Avisos de reparación

SAJ Local genera un aviso de reparación para una situación en la que puedes actuar.

| Aviso de reparación | Se genera cuando | Qué puedes hacer |
| --- | --- | --- |
| El sistema tiene configurado un modelo incorrecto | El inversor de la dirección se identifica como un modelo distinto del elegido. | Una corrección adopta el modelo que encontró SAJ Local. Consulta [sustituir el inversor](replacing-the-inverter.md). |
| El sistema ahora llega a un inversor distinto | El inversor de la dirección tiene otro número de serie. | Una corrección adopta el inversor nuevo. Consulta [sustituir el inversor](replacing-the-inverter.md). |
| El sistema llega a un dispositivo no reconocido | El tipo de dispositivo no es un modelo reconocido. | Elige el modelo en Configurar. SAJ Local usa entonces el modelo sin verificar. |
| El sistema tiene lecturas que el inversor rechaza | El inversor rechazó las lecturas tres veces seguidas. | Una corrección deshabilita las entidades listadas, así que SAJ Local deja de leerlas. Consulta [proteger el inversor](protecting-the-inverter.md#cuando-el-inversor-rechaza-una-lectura). |
| El sistema ha dejado de responder | El inversor no ha respondido en 15 minutos. | Comprueba la alimentación, la red y otros clientes Modbus. El aviso desaparece con la primera lectura correcta. |
| El equipo ya no se detecta | El equipo que SAJ Local detectó antes ya no se detecta. | Comprueba el equipo, o ajusta el equipo a No instalado en Configurar. Consulta el [equipo opcional](optional-equipment.md#cuando-el-equipo-recordado-ya-no-se-detecta). |

![Un aviso de reparación en Home Assistant que dice que SAJ HS3MOCK000000000003 tiene lecturas que el inversor rechaza](../../images/es/faults-and-repairs-repair-issue.png)

Los tres primeros avisos son los avisos de modelo. Solo uno de los avisos de modelo está abierto para un sistema, y el aviso de que el sistema ha dejado de responder no se genera mientras hay un aviso de modelo abierto.

Un aviso de reparación desaparece cuando termina la situación que lo causó, o cuando quitas el sistema. El aviso de lecturas rechazadas también desaparece cuando deshabilitas una entidad listada.

## Aún no compatible

- Un aviso de reparación para un fallo del dispositivo. Los fallos del dispositivo son entidades, y la integración no genera un aviso de reparación para un fallo.
