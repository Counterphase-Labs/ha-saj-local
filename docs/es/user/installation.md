[en](../../en-gb/user/installation.md) | [de](../../de/user/installation.md) | [nl](../../nl/user/installation.md) | [fr](../../fr/user/installation.md) | [zh](../../zh-hans/user/installation.md) | es | [it](../../it/user/installation.md) | [pl](../../pl/user/installation.md) | [sv](../../sv/user/installation.md)

# Instalación

La página Instalación instala SAJ Local con HACS, la tienda de la comunidad de Home Assistant (Home Assistant Community Store). La lista completa de lo que hace la configuración está en la sección [Configuración y detección](../../../custom_components/saj_local/docs/features.md#setup-and-detection) de la lista de funciones de la integración.

SAJ Local todavía no tiene ninguna versión publicada. Comprueba los [equipos compatibles](supported-equipment.md) antes de instalar.

## Qué necesitas

- Home Assistant en la versión mínima indicada en [`hacs.json`](../../../hacs.json), y HACS.
- Un inversor SAJ compatible que responda a Modbus TCP en tu red local. Necesitas la dirección del inversor, y el puerto y el ID de unidad cuando no sean los de por defecto.
- Nada más. SAJ Local habla directamente con el inversor y no envía nada a ningún servicio en la nube.

## Instalar

1. Abre SAJ Local en HACS con el primer botón de abajo. HACS te pide añadir el repositorio si el repositorio todavía no figura en la lista.
2. Descarga SAJ Local en HACS.
3. Reinicia Home Assistant.
4. Añade tu sistema con el segundo botón de abajo, o sigue los [primeros pasos](getting-started.md).

[![Abre tu instancia de Home Assistant y abre el repositorio de SAJ Local en HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Counterphase-Labs&repository=ha-saj-local&category=integration)
[![Abre tu instancia de Home Assistant y empieza a configurar SAJ Local.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=saj_local)

SAJ Local ofrece tarjetas del panel, así que no hay ningún recurso de tarjeta que añadir. Consulta las [tarjetas del panel](cards/README.md).

## Versiones beta

Hasta la primera versión estable, cada versión de SAJ Local es una beta. En HACS, abre SAJ Local, abre el menú, elige Volver a descargar, activa «Mostrar versiones beta» y descarga la beta más reciente. Sin ese interruptor, HACS instala la versión de desarrollo de SAJ Local.
