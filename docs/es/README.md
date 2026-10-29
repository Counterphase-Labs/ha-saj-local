[en](../../README.md) | [de](../de/README.md) | [nl](../nl/README.md) | [fr](../fr/README.md) | [zh](../zh-hans/README.md) | es | [it](../it/README.md) | [pl](../pl/README.md) | [sv](../sv/README.md)

# Integración SAJ Local para Home Assistant

![SAJ Local](../../images/header.png)

[![HACS personalizado](https://img.shields.io/badge/HACS-personalizado-41BDF5.svg)](https://hacs.xyz)
[![Home Assistant](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FCounterphase-Labs%2Fha-saj-local%2Fmain%2Fhacs.json&query=%24.homeassistant&suffix=%2B&label=Home%20Assistant&logo=homeassistant&logoColor=white&color=41BDF5)](https://www.home-assistant.io)
[![Versión](https://img.shields.io/github/v/release/Counterphase-Labs/ha-saj-local?label=Versi%C3%B3n)](https://github.com/Counterphase-Labs/ha-saj-local/releases)
[![Instalaciones activas](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fanalytics.home-assistant.io%2Fcustom_integrations.json&query=%24.saj_local.total&label=Instalaciones%20activas&logo=homeassistant&logoColor=white&color=41BDF5)](https://analytics.home-assistant.io)
[![Comprobaciones](https://github.com/Counterphase-Labs/ha-saj-local/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Counterphase-Labs/ha-saj-local/actions/workflows/ci.yml)
[![Licencia](https://img.shields.io/github/license/Counterphase-Labs/ha-saj-local?label=Licencia)](../../LICENSE)

⭐ [Dale una estrella al proyecto en GitHub](https://github.com/Counterphase-Labs/ha-saj-local): ¡tu apoyo es una motivación real! 🙏😊

Tu sistema solar SAJ en Home Assistant, leído directamente del inversor a través de tu propia red. Sin cuenta en la nube, sin aplicación del fabricante de por medio y con un método de sondeo pensado para ser amable con el hardware.

Esta es una integración no oficial, creada por la comunidad. SAJ no la ha creado, ni da soporte, ni la respalda. Consulta el [descargo de responsabilidad](user/README.md#descargo-de-responsabilidad).

> **Estado: versión preliminar.** SAJ Local aún no tiene ninguna versión estable. Toda versión anterior a `1.0.0` es una beta, y las notas de versión de una beta nombran cada cambio incompatible. Consulta [versiones beta](user/installation.md#versiones-beta).

## Por qué SAJ Local

- **Sensato por defecto.** Añade tu inversor y obtén una configuración que funciona sin tener que recorrer páginas de opciones. El inversor, la batería y el equipo relacionado se detectan automáticamente.
- **Amable con tu inversor.** Una conexión y una solicitud a la vez, y un tope estricto de solicitudes que ningún ajuste, recarga o fallo puede superar. Tú eliges qué se lee y con qué frecuencia.
- **Solo lectura, salvo que digas lo contrario.** La escritura es opcional en cada instalación, así que nada cambia en tu inversor por accidente.
- **Los mismos nombres en todos los modelos.** Los paneles y las automatizaciones se escriben una vez y siguen funcionando en todos los modelos SAJ, y sobreviven al paso de un H2 a un HS3.
- **Varios sistemas.** Conecta más de un sistema SAJ al mismo Home Assistant.
- **Tarjetas para el panel.** Tarjetas para ver información y para cambiar la configuración, que se añaden desde el selector de tarjetas.
- **Errores claros y diagnósticos seguros.** Cuando algo sale mal, se te dice qué y por qué, y los volcados de depuración están pensados para poder compartirse sin riesgo.
- **Totalmente local.** Todo se comunica con tu inversor a través de tu red. No se envía nada a un servicio en la nube.

## Equipos compatibles

Son compatibles el SAJ HS3 y el SAJ H2 monofásico. Consulta los [equipos compatibles](user/supported-equipment.md) para ver la lista completa y lo que todavía no es compatible.

## Documentación

- [Documentación de usuario](user/README.md): instala, configura y utiliza SAJ Local.
- [Documentación para desarrolladores](developer/README.md): cómo se construye, se comprueba y se publica SAJ Local.
- [Cómo contribuir](../../CONTRIBUTING.md): prepara una copia de trabajo y envía un cambio.

## Ayuda y comentarios

Las preguntas, los informes de errores y las ideas son bienvenidos en el [gestor de incidencias](https://github.com/Counterphase-Labs/ha-saj-local/issues).

Informa de un problema de seguridad de forma privada, consulta la [política de seguridad](../../SECURITY.md).

## Licencia

[MIT](../../LICENSE)
