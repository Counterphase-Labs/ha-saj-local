[en](../../en-gb/developer/environment.md) | [de](../../de/developer/environment.md) | [nl](../../nl/developer/environment.md) | [fr](../../fr/developer/environment.md) | [zh](../../zh-hans/developer/environment.md) | es | [it](../../it/developer/environment.md) | [pl](../../pl/developer/environment.md) | [sv](../../sv/developer/environment.md)

# Entorno de desarrollo

Cómo preparar una copia de trabajo y ejecutar la instancia de desarrollo de Home Assistant con los simuladores.

## Preparar una copia de trabajo

Una copia de trabajo necesita [uv](https://docs.astral.sh/uv/) para las herramientas de Python, Node.js y npm para las tarjetas, Docker con Docker Compose para Home Assistant y los simuladores, y `make`. Las versiones necesarias se fijan en `pyproject.toml` y en `frontend/package.json`. Tras clonar, `make setup` instala las dependencias de Python, las dependencias del frontend y el navegador Chromium que usan las pruebas de Playwright.

## Ejecutar Home Assistant

`make up` arranca Home Assistant con la integración y dos simuladores Modbus, un HS3 y un H2. `make logs` sigue el registro de Home Assistant y `make down` lo detiene todo.

Home Assistant está en el puerto 8123. El simulador HS3 responde a Modbus en el puerto 5020 del host y el simulador H2 en el 5021, y las páginas de los simuladores están en el 5080 y el 5081. Dentro de Docker, Home Assistant llega a los simuladores por los nombres de servicio `mock` y `mock-h2` en el puerto 502. No se necesita ningún inversor real. La [página del simulador](simulator.md) explica cómo conectarse a los simuladores y cambiar lo que simulan.

Para usar otros puertos del host, otra zona horaria u otros escenarios, copia [compose.override.yaml.example](../../../compose.override.yaml.example) en el archivo ignorado `compose.override.yaml` y cambia lo que difiera. No edites `compose.yaml` para necesidades locales, porque `make mock-smoke` también arranca `compose.yaml`.

## Docker

El desarrollo se ejecuta en contenedores para que Home Assistant sea una versión conocida y fijada, con una configuración limpia. Los servicios se definen en estos archivos:

- [compose.yaml](../../../compose.yaml): el entorno interactivo, con Home Assistant, el simulador HS3 `mock` y el simulador H2 `mock-h2`. La integración se monta en modo de solo lectura en Home Assistant, así que el contenedor nunca escribe en el árbol de código fuente. Los simuladores guardan sus cambios en `mock/state/hs3/` y `mock/state/h2/`, que Git ignora.
- [compose.playwright.yaml](../../../compose.playwright.yaml): un Home Assistant desechable construido a partir de `Dockerfile.playwright-home-assistant`, con un simulador HS3, un simulador H2 y ejecutores de Playwright. `make test-browser-home-assistant` usa los servicios `homeassistant`, `mock`, `mock-h2` y `playwright` para demostrar que cada punto de conexión se puede añadir, se carga, informa de valores de sensores, muestra la potencia solar en una tarjeta de flujo de potencia y, una vez permitido el control, acepta un ajuste cambiado. `make docs-images` usa los servicios `homeassistant`, `mock-docs`, `mock-h2` y `playwright-docs`, consulta [Capturas de pantalla](documentation.md#capturas-de-pantalla). Los servicios no comparten ningún estado con el entorno interactivo.
- `compose.override.yaml`: los puertos, la zona horaria y los escenarios de tu máquina. Git ignora el archivo, y `compose.override.yaml.example` muestra la forma.

Bajo `config/`, Git sigue solo `configuration.yaml` y los dos paneles de muestra de `config/dashboards/`. El resto es estado local de Home Assistant.

La [página de comprobaciones](checks.md) lista lo que ejecuta cada objetivo de make, y la [página del frontend](frontend.md#paneles-de-muestra) describe los dos paneles de muestra.
