[en](../../en-gb/user/replacing-the-inverter.md) | [de](../../de/user/replacing-the-inverter.md) | [nl](../../nl/user/replacing-the-inverter.md) | [fr](../../fr/user/replacing-the-inverter.md) | [zh](../../zh-hans/user/replacing-the-inverter.md) | es | [it](../../it/user/replacing-the-inverter.md) | [pl](../../pl/user/replacing-the-inverter.md) | [sv](../../sv/user/replacing-the-inverter.md)

# Sustituir el inversor

La página Sustituir el inversor explica cómo pasar un sistema a un inversor nuevo, o entre un H2 y un HS3, y conservar el dispositivo, las entidades y el historial. La lista completa está en la sección [Sustitución de modelo](../../../custom_components/saj_local/docs/features.md#model-replacement) de la lista de funciones de la integración.

## Pasar un sistema a propósito

1. Asegúrate de que el inversor nuevo es accesible. Si el inversor nuevo tiene otra dirección, introduces la dirección en el paso siguiente.
2. Abre Configurar, el engranaje de la fila del sistema en la página de la integración SAJ Local.
3. Cambia el host, el puerto o el ID de unidad si la dirección cambió. Deja Modelo en Automático, o elige el modelo si el inversor no se reconoce.
4. Elige Enviar y confirma la sustitución. La confirmación nombra el modelo y el número de serie que encontró SAJ Local.

Después de confirmar, el dispositivo, las entidades, los nombres de las entidades y el historial se quedan con el sistema. Una entidad conserva el historial a través del cambio cuando ambos modelos tienen la entidad. SAJ Local olvida el equipo detectado en el inversor antiguo y el recuento de módulos de batería del inversor antiguo, y vuelve a detectar el equipo en el inversor nuevo.

## Cuando el inversor de la dirección cambia sin que lo hagas tú

SAJ Local comprueba la identidad del inversor cada vez que se carga el sistema. Cuando el inversor de la dirección se identifica como otro modelo, o tiene otro número de serie, SAJ Local no carga el sistema y genera un aviso de reparación. La corrección del aviso de reparación muestra el modelo y el número de serie que informa ahora el inversor, y adopta el inversor que confirmes.

- Los ID de entidad, el historial, Permitir control y todos los demás ajustes no cambian.
- Cuando el inversor informa de algo distinto de lo que mostró el formulario, el formulario lo dice y muestra los valores nuevos en lugar de guardar los antiguos.
- Cuando el dispositivo de la dirección no es un modelo reconocido, un aviso de reparación lo indica y remite a Configurar. No hay nada que adoptar. Elige el modelo a mano, consulta los [primeros pasos](getting-started.md#cuando-no-se-reconoce-el-inversor).

Los avisos de reparación se listan en [fallos y reparaciones](faults-and-repairs.md#avisos-de-reparación).

## Aún no compatible

- Adoptar un inversor que ya pertenece a otro sistema. SAJ Local rechaza la adopción.
