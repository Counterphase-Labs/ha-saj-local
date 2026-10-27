[en](../../en-gb/user/protecting-the-inverter.md) | [de](../../de/user/protecting-the-inverter.md) | [nl](../../nl/user/protecting-the-inverter.md) | [fr](../../fr/user/protecting-the-inverter.md) | [zh](../../zh-hans/user/protecting-the-inverter.md) | es | [it](../../it/user/protecting-the-inverter.md) | [pl](../../pl/user/protecting-the-inverter.md) | [sv](../../sv/user/protecting-the-inverter.md)

# Proteger el inversor

La página Proteger el inversor lista los límites que SAJ Local aplica a todo lo que envía, para que el módulo de comunicación del inversor siga atendiendo a Home Assistant. Un módulo puede dejar de atender a un cliente que sondea con demasiada insistencia, así que ningún ajuste elimina un límite. La lista completa está en la sección [Proteger el inversor](../../../custom_components/saj_local/docs/features.md#protecting-the-inverter) de la lista de funciones de la integración.

## Los límites

- **Una conexión, una solicitud a la vez.** SAJ Local abre una conexión con un inversor y espera cada respuesta antes de enviar la siguiente solicitud, con una breve pausa entre solicitudes.
- **40 solicitudes en cualquier periodo de 60 segundos.** El límite se aplica por dirección de inversor. SAJ Local cuenta a través de las recargas, así que una recarga, un reintento de configuración o una comprobación de conexión no pueden superar el límite. Una solicitud por encima del límite espera.
- **Los registros vecinos comparten una solicitud.** SAJ Local lee en una sola solicitud los registros que están cerca unos de otros, nunca más allá de un bloque que documenta el modelo. Una solicitud nunca supera los 32 registros en el HS3 ni los 56 en el H2. Agrupar las entidades que están juntas cuesta menos, consulta el [sondeo](polling.md).
- **Sin reintentos dentro de un ciclo.** Tras una lectura fallida, la espera antes del siguiente intento se duplica a partir del intervalo más corto, hasta 5 minutos. La espera se mantiene a través de las recargas. El primer ciclo correcto lo lee todo de nuevo.
- **Cada espera tiene un límite de tiempo.** Un inversor bloqueado termina un ciclo como fallo y no detiene el sondeo. Una respuesta tardía o perdida se descarta.
- **Una conexión cerrada se reabre una vez.** Ese ciclo vuelve entonces a leer cada entidad habilitada, así que ningún valor es más antiguo que la reconexión.
- **Como máximo 20 cambios en 60 segundos.** Consulta [cambiar ajustes](changing-settings.md#qué-ocurre-con-un-cambio). Un cambio por encima del límite se rechaza y no se pone en cola.

## Cuando el inversor rechaza una lectura

Un rechazo es una respuesta y no un fallo. Solo pasan a no disponibles las entidades de la solicitud rechazada, y las demás siguen actualizándose.

1. SAJ Local divide por la mitad la solicitud rechazada en los ciclos siguientes, hasta encontrar la entidad rechazada.
2. Una entidad rechazada tres veces seguidas se suspende. La entidad se muestra como no disponible y deja de leerse.
3. SAJ Local vuelve a probar una entidad suspendida una vez al día, y siempre que se carga la integración. La entidad vuelve cuando el registro responde.
4. Un aviso de reparación lista las entidades suspendidas. La corrección del aviso deshabilita las entidades, así que SAJ Local deja de leerlas definitivamente. Consulta [fallos y reparaciones](faults-and-repairs.md#avisos-de-reparación).

## Cuando el inversor deja de responder

Un aviso de reparación indica cuándo un inversor no ha respondido en 15 minutos. El aviso desaparece con la primera lectura correcta. Comprueba la alimentación del inversor y del módulo de comunicación, la red, y que ningún otro cliente Modbus mantenga la conexión.

## Aún no compatible

- Cambiar los límites. Los límites protegen el inversor, así que ningún ajuste sube un límite.
