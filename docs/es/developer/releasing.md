[en](../../en-gb/developer/releasing.md) | [de](../../de/developer/releasing.md) | [nl](../../nl/developer/releasing.md) | [fr](../../fr/developer/releasing.md) | [zh](../../zh-hans/developer/releasing.md) | es | [it](../../it/developer/releasing.md) | [pl](../../pl/developer/releasing.md) | [sv](../../sv/developer/releasing.md)

# Publicación de versiones

Qué hacer antes de una versión, cómo se publica una versión y cómo se sube la versión de Home Assistant. Subir una etiqueta de versión inicia el flujo de trabajo `Release` de `.github/workflows/release.yml`, que comprueba la etiqueta, ejecuta las comprobaciones y crea una versión borrador de GitHub.

## Versiones

Una versión es una versión de GitHub creada a partir de una etiqueta de versión en `main`. La etiqueta no tiene prefijo `v` y es igual a la versión de `custom_components/saj_local/manifest.json`, `pyproject.toml` y `frontend/package.json`. Una versión estable es `X.Y.Z` y una beta es `X.Y.ZbN`, publicada como una versión preliminar de GitHub. Las betas anteriores a la primera versión estable son `1.0.0b1`, `1.0.0b2` y así sucesivamente, la primera versión estable es `1.0.0`, y el control de versiones semántico se aplica desde `1.0.0`. Las notas de la versión viven solo en la versión de GitHub, y las notas de una beta nombran cada cambio en una entidad, un ajuste guardado, un tipo de tarjeta o un ajuste de tarjeta desde la beta anterior. La sección [Publicación de versiones](../../../.github/work/requirements.md#releases) de los requisitos del proyecto contiene la regla.

## Antes de una versión

Haz esto en `main`, en orden.

1. **Ejecuta `make ci`.** La [página de comprobaciones](checks.md) lista lo que ejecuta `make ci`.
2. **Ejecuta `make docs-images`.** La documentación de usuario muestra la interfaz, y CI no regenera las imágenes, así que cada versión necesita un juego nuevo. El objetivo necesita Docker. Ejecuta el objetivo, mira cada imagen cambiada, confirma las imágenes cambiadas en `docs/images/<idioma>/` para cada idioma y ejecuta `make docs-check`. Una ejecución que falla no escribe ninguna imagen, así que no publiques con una ejecución fallida. Lee [Capturas de pantalla](documentation.md#capturas-de-pantalla) para saber qué hace la ejecución y por qué cada lectura de una imagen es simulada.
3. **Copia la captura del sitio en el mismo paso.** Copia `docs/images/en-gb/cards-power-flow-card.png` en `assets/images/saj-local-power-flow.png` del repositorio `website` y confirma la copia allí, porque la página de SAJ Local en `counterphase.dev` muestra una copia de la imagen. Ninguna comprobación detecta una copia obsoleta, porque CI de este repositorio no puede ver el repositorio del sitio.
4. **Ejecuta `make release-check`.** El paso crea un archivo a partir de `custom_components/saj_local/` y falla cuando al archivo le falta `asset-manifest.json` o el paquete de tarjetas compilado. Ejecuta `make build` y confirma primero el paquete cuando las tarjetas cambiaron.
5. **Fija la nueva versión.** Fija la versión en `custom_components/saj_local/manifest.json`, `pyproject.toml` y `frontend/package.json`. Ejecuta `uv lock` para que `uv.lock` registre la versión del proyecto, y ejecuta `npm install --package-lock-only` en `frontend/` para que `frontend/package-lock.json` registre la versión. Ejecuta `make release-check`, confirma en `main` y espera a que CI pase.

Las capturas de pantalla son la única parte de una versión que CI no puede comprobar. Un cambio que añade o quita una imagen hace fallar `make docs-check` por las reglas de imagen sin usar y de imagen que falta. Un cambio en la interfaz que deja una imagen obsoleta no hace fallar nada, así que el paso 2 es lo que mantiene actualizadas las imágenes.

## Publicar una versión

1. Sube la etiqueta: `git tag 1.0.0b1` y luego `git push origin 1.0.0b1`.
2. Espera al flujo de trabajo `Release`. El flujo de trabajo exige que el commit etiquetado esté en `main`, ejecuta `make ci` mediante `ci.yml` y crea una versión borrador con las notas generadas por GitHub.
3. Abre la versión borrador y edita las notas generadas. Para una beta, nombra cada cambio en una entidad, un ajuste guardado, un tipo de tarjeta o un ajuste de tarjeta desde la beta anterior.
4. Pulsa Publish.

Una ejecución fallida no crea ningún borrador. Elimina la etiqueta con `git push origin :refs/tags/<tag>` y `git tag -d <tag>`, arregla `main` y etiqueta de nuevo.

HACS ofrece una beta publicada a los usuarios que activan «Mostrar versiones beta» y una versión estable publicada a todos los usuarios. Un usuario sin el interruptor recibe la punta de `main` hasta que exista `1.0.0`, y por eso `main` debe pasar `make ci` antes de cada subida.

## Subir la versión de Home Assistant

La versión de Home Assistant está fijada en varios archivos que deben actualizarse juntos, o de lo contrario el contenedor de desarrollo, las pruebas de navegador y la ejecución de capturas de pantalla, CI, HACS y el arnés de pruebas se desincronizan:

1. `compose.yaml`: `ghcr.io/home-assistant/home-assistant:<X.Y.Z>`, el entorno de ejecución de Home Assistant de desarrollo.
2. `Dockerfile.playwright-home-assistant`: la línea `FROM ghcr.io/home-assistant/home-assistant:<X.Y.Z>` de la imagen que usan `make test-browser-home-assistant` y `make docs-images`.
3. `pyproject.toml`, `[dependency-groups] dev`: `homeassistant==<X.Y.Z>` para el lint y mypy de CI, **y** `pytest-homeassistant-custom-component==<versión correspondiente>`. El arnés de pruebas incluye su propio `homeassistant` fijado, así que las dos fijaciones deben proceder de la misma versión de Home Assistant, o de lo contrario el lint y las pruebas resuelven núcleos distintos.
4. `hacs.json`: `"homeassistant": "<X.Y.Z>"`, el núcleo mínimo de Home Assistant que exige HACS.
5. `uv.lock`: ejecuta `uv lock` tras editar `pyproject.toml`, para que el archivo de bloqueo registre las nuevas fijaciones.

Verifica la correspondencia en PyPI antes de confirmar: el `requires_dist` de `pytest-homeassistant-custom-component` debe listar el mismo `homeassistant==<X.Y.Z>` fijado en `pyproject.toml`.

Tras una subida, ejecuta `make ci` y `make docs-images`, porque una nueva versión de Home Assistant puede cambiar las pantallas que muestran las imágenes.
