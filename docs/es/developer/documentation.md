[en](../../en-gb/developer/documentation.md) | [de](../../de/developer/documentation.md) | [nl](../../nl/developer/documentation.md) | [fr](../../fr/developer/documentation.md) | [zh](../../zh-hans/developer/documentation.md) | es | [it](../../it/developer/documentation.md) | [pl](../../pl/developer/documentation.md) | [sv](../../sv/developer/documentation.md)

# Documentación

Cómo se organizan las páginas de documentación, cómo se hacen la referencia de entidades y las capturas de pantalla, y en qué falla `make docs-check`.

## Organización

Las páginas de usuario están en `docs/en-gb/user/` y las páginas para desarrolladores en `docs/en-gb/developer/`. Cada carpeta tiene un índice `README.md`, y cada página trata un solo tema. Ninguna página escrita supera las 300 líneas. Cada dato tiene un responsable, indicado en [Fuentes](#fuentes), y las demás páginas enlazan con el responsable en lugar de repetir el dato.

Las capturas de pantalla están en `docs/images/en-gb/`. Toda imagen debe estar referenciada por una página.

Escribe las páginas inglesas en inglés británico, con el tono de voz de Counterphase, y usa los términos que las traducciones de la integración muestran a los usuarios. Las páginas de usuario describen SAJ en general e indican, en el punto de la diferencia, dónde se diferencian el HS3 y el H2. Una página nunca se divide en una página por modelo.

## Primero las listas de funciones

Las tres listas de funciones son la base de cada página: la de la [integración](../../../custom_components/saj_local/docs/features.md), la de las [tarjetas](../../../frontend/docs/features.md) y la del [simulador](../../../mock/docs/features.md). Una sección de una lista de funciones dice qué está construido y nombra los archivos que hay que leer en la línea `Files:` de la sección. Confirma cada afirmación con esos archivos antes de documentarla. Los documentos de requisitos dicen qué se pretende y se leen solo para conocer la intención. Un comportamiento que aparece en un documento de requisitos pero en ninguna lista de funciones no está construido, y una página de usuario no describe el comportamiento como disponible. Cuando una lista de funciones y el código discrepan, el código es lo que reciben los usuarios, así que corrige la lista de funciones en el mismo cambio.

Una página que describe código enlaza con la sección de la lista de funciones cuya línea `Files:` nombra el código, y no repite la lista de archivos.

Un cambio de capacidad actualiza la lista de funciones de la parte y cada página de usuario que enlaza con la sección cambiada, en el mismo cambio. El `AGENTS.md` de la raíz contiene la regla.

## Referencia de entidades generada

`docs/en-gb/user/entities/` contiene una página generada por área y un índice `README.md`. Ejecuta `make docs` para regenerar las páginas y confirma después las páginas regeneradas. Las páginas en prosa nunca nombran una entidad a mano; las páginas en prosa enlazan con las páginas generadas. Las páginas generadas están exentas del límite de 300 líneas, porque los lectores buscan en un área como la batería en lugar de leer el área.

El generador es `.github/scripts/docs_check.py`, ejecutado con `--write` por `make docs`. El generador importa solo la biblioteca SAJ y lee `custom_components/saj_local/translations/en.json`, así que el generador no necesita Home Assistant. Cada página de área empieza con un enlace a las secciones de la lista de funciones que cubren el área y una línea sobre el prefijo del ID de entidad, y después tiene una fila por entidad con el nombre de `en.json`, el ID de entidad sin prefijo, el tipo, la unidad, los modelos que tienen la entidad, el equipo que debe estar instalado con cualquier número de fases, strings o módulos, y si la entidad está habilitada por defecto. Una entidad que dos modelos definen de forma distinta, por ejemplo con otra unidad, recibe una fila por definición.

### Fuentes de entidades

Cada entidad procede de una de estas fuentes, y el generador las lee todas:

| Fuente | Código | Entidades |
| --- | --- | --- |
| El catálogo de registros de cada modelo distribuido | `catalogue_of` en [catalogue.py](../../../custom_components/saj_local/saj/catalogue.py), llamado para cada perfil de `PROFILES` en [profiles.py](../../../custom_components/saj_local/saj/profiles.py), omitiendo las filas que no se exponen | Sensores, sensores binarios (los fallos), números, selecciones, interruptores, horas y botones |
| El sensor de control permitido | `CONTROL_ALLOWED_KEY` en [binary_sensor.py](../../../custom_components/saj_local/binary_sensor.py) | `binary_sensor.saj_control_allowed`, en ambos modelos |
| Los interruptores y números del control de potencia | `power_control` de cada perfil ([hs3.py](../../../custom_components/saj_local/saj/models/hs3.py) y [h2.py](../../../custom_components/saj_local/saj/models/h2.py)), las claves `PowerFunction` en [models/\_\_init\_\_.py](../../../custom_components/saj_local/saj/models/__init__.py) y `FUNCTION_EQUIPMENT` en [power_control.py](../../../custom_components/saj_local/saj/power_control.py), creados por [switch.py](../../../custom_components/saj_local/switch.py) y [number.py](../../../custom_components/saj_local/number.py) | Un interruptor y un número por cada función de potencia de un modelo: batería en ambos modelos, red e inversor en el HS3 |

`make docs-check` falla cuando una entidad del bloque `entity` de `en.json` no está en ninguna página de área, así que una fuente de entidades que el generador no lee se descubre de inmediato. Una fuente nueva necesita que el generador lea la fuente y una fila en la tabla anterior.

### Áreas

Una entidad va a la primera área que coincide, en este orden:

1. Entidades fuera del catálogo: Añadidas por la integración.
2. Sensores binarios del catálogo, que son los fallos: Fallos.
3. Entidades con un índice de módulo de batería: Módulos de batería.
4. Entidades de equipo opcional: Batería, Red y Contador A, Contador B, Cargador de VE o Sistema en paralelo.
5. Entidades escribibles sin equipo: Ajustes.
6. Entidades cuya clave empieza por `grid_`: Red y Contador A.
7. Todo lo demás: Inversor y PV.

La tabla `AREAS` de `.github/scripts/docs_check.py` nombra las áreas, sus resúmenes y las secciones de la lista de funciones que enlaza cada página de área.

## Comprobaciones

`make docs-check` ejecuta `.github/scripts/docs_check.py` sin `--write` e informa de una línea por hallazgo:

- una página generada que difiere de lo que escribiría `make docs`;
- una entidad de `en.json` que no está en ninguna página de área, y una entidad generada sin nombre en `en.json`;
- un enlace relativo, una imagen o un ancla de encabezado que no se resuelve, en las páginas, `README.md`, `CONTRIBUTING.md`, `SECURITY.md` y cada `AGENTS.md`, incluidos los enlaces a las listas de funciones y a los documentos de requisitos;
- una imagen de `docs/images/` que ninguna página referencia;
- una página escrita de más de 300 líneas;
- una sección de una lista de funciones sin fila en la [Tabla de cobertura de funciones](#tabla-de-cobertura-de-funciones), una sección nombrada en la tabla que la lista de funciones no tiene, una página nombrada en la tabla que no existe, y una página que no enlaza con la sección de la lista de funciones nombrada en la fila, mediante el ancla de encabezado de la sección.

`make docs-check` es un paso de `make ci`, y GitHub ejecuta `make ci`, así que la comprobación no necesita cambios en el flujo de trabajo. La comprobación no lee ninguna captura de pantalla más allá de las reglas de enlace e imagen huérfana y no inicia ningún navegador.

## Capturas de pantalla

Cada captura de pantalla de `docs/images/<código>/` la hace `make docs-images` desde un Home Assistant real en Docker con el idioma del usuario fijado al idioma de la carpeta, o desde las páginas del simulador de la misma ejecución. `make docs-images` ejecuta todos los idiomas, el inglés primero, con contenedores nuevos en cada ejecución, y `ARGS=<código>` selecciona un idioma. Ninguna captura se edita ni se hace a mano, así que el conjunto se puede reconstruir cuando cambia la interfaz. Las capturas muestran los simuladores, así que cada lectura de una captura es un valor simulado.

El objetivo ejecuta `tests/playwright/run-docs-images.sh`, que construye los servicios `homeassistant` y `playwright-docs` de [compose.playwright.yaml](../../../compose.playwright.yaml), inicia el Home Assistant desechable y dos simuladores, ejecuta la especificación y después elimina los contenedores, los volúmenes y las imágenes locales. El objetivo necesita Docker, tiene el mismo límite de tiempo que `make test-browser-home-assistant` y acepta opciones mediante `ARGS`, que recibe el script. La imagen de Home Assistant se construye a partir de `Dockerfile.playwright-home-assistant`, que compila el paquete de tarjetas y copia la integración en la imagen, así que no se monta ningún código de la integración. La especificación es `frontend/tests/browser/docs/screenshots.spec.ts`, configurada por `frontend/playwright.docs.config.ts`.

- **Sistemas.** El HS3 es el simulador `mock-docs` con `mock/scenarios/hs3-full-house.yaml`, que tiene todo el equipo instalado. El H2 es el simulador `mock-h2` con `mock/scenarios/h2-battery.yaml` y recibe el prefijo de entidad `h2`. Ningún simulador monta una carpeta de estado, así que cada ejecución parte del escenario.
- **Condiciones fijas.** La ventana es de 1280 por 800 píxeles, el tema es claro y el reloj es real. Un diálogo o una tarjeta altos se capturan en una ventana de 1600 píxeles de alto, porque la cabecera fija de Home Assistant taparía la parte superior del elemento.
- **Idioma.** Cada ejecución fija tanto el idioma del servidor de Home Assistant, antes de configurar SAJ Local para que las entidades se creen con nombres en ese idioma, como el idioma de usuario, por el código de idioma y no por la etiqueta del selector de idioma. La ejecución falla si un nombre de entidad de SAJ Local no está en el idioma de la ejecución. Las imágenes van a `docs/images/<código>/`. La especificación abre las pantallas por su ruta URL, encuentra los campos de los formularios de SAJ Local por su atributo `name` y encuentra los controles de Home Assistant que solo tienen texto por el texto que se lee en tiempo de ejecución del Home Assistant en marcha con `hass.localize`. La especificación no contiene ninguna tabla de etiquetas, así que todos los idiomas siguen los mismos pasos.
- **Nombres.** Cada archivo se llama `<página>-<tema>.png`, donde `<página>` es la ruta de la página con `/` sustituida por `-`, por ejemplo `cards-battery-card.png`, y la página que muestra la imagen enlaza con el archivo.
- **Páginas del simulador.** Las capturas de las páginas del simulador proceden de los dos simuladores de la misma ejecución, `mock-docs` y `mock-h2`, y usan el prefijo de nombre `developer-simulator-page-`. Se hacen al final, después de cada captura de Home Assistant, para que nada de lo que se haga en una página del simulador cambie una captura de Home Assistant. La especificación activa el fallo "Fan 1 fault" en la página del HS3, y el registro que la captura de la reparación hace que el simulador rechace sigue rechazado, así que la vista Link, el registro de tráfico y los cambios de la barra de estado muestran cambios reales.
- **Preparación.** La especificación crea un usuario mediante la API de incorporación, añade el HS3 mediante el flujo de configuración en el navegador, añade el H2 mediante la API del flujo de configuración, activa Permitir control en ambos sistemas y añade un panel por sistema con todas las tarjetas de SAJ Local y la insignia de estado, mediante la API WebSocket de Home Assistant.
- **Todo o nada.** La especificación espera hasta dos minutos a que ambos sistemas informen de potencia solar. La especificación escribe las imágenes solo después de que todos los pasos hayan pasado, así que una ejecución fallida deja las imágenes confirmadas como estaban.
- **Esperas.** La especificación espera a una pantalla comprobando el estado que muestra la pantalla, nunca con una pausa fija.
- **Reparación.** La captura de la reparación muestra la reparación de registros rechazados. La especificación añade un grupo de sondeo para la temperatura del inversor con un intervalo de 10 segundos, hace que el simulador rechace ese registro mediante `POST /api/link` de la página del simulador y espera hasta dos minutos a que `repairs/list_issues` liste el problema `registers_refused` de SAJ Local. La ejecución falla con un mensaje que nombra el problema ausente cuando el problema no aparece.
- **Formularios.** Se captura el aviso del cambio de prefijo y después se cierra el formulario, lo que aborta el flujo, así que no se guarda ningún prefijo. Se captura el aviso de Permitir control y después se confirma, porque las tarjetas necesitan el control permitido.
- **Fallos.** El informe HTML está en `frontend/playwright-report/docs/`, y una ejecución fallida guarda el registro de Home Assistant como `frontend/test-results/docs/home-assistant.log`.

Las capturas de pantalla no se comparan píxel a píxel, ni en CI ni en ningún otro sitio. Home Assistant dibuja los valores en vivo y las fuentes de forma distinta entre ejecuciones, así que una comparación de píxeles fallaría sin un cambio real. Revisa una imagen cambiada mirando la imagen.

### Añadir o cambiar una captura de pantalla

1. Añade o cambia la captura en la especificación, con el nombre de archivo de la forma `<página>-<tema>.png`.
2. Referencia la imagen desde la página que explica el tema.
3. Ejecuta `make docs-images`, mira las imágenes cambiadas y confirma las imágenes cambiadas.
4. Ejecuta `make docs-check`. Se informa tanto de una imagen que ninguna página referencia como de un enlace a una imagen que no existe.

`make docs-images` no es un paso de `make ci`, y CI no regenera las imágenes. Ejecuta el objetivo antes de cada versión, consulta la [página de publicación de versiones](releasing.md).

## Añadir una página

1. Crea la página en `docs/en-gb/user/` o `docs/en-gb/developer/` y enlaza la página desde el índice de la carpeta.
2. Enlaza la página con la sección de la lista de funciones cuya línea `Files:` nombra el código que describe la página.
3. Añade la página a la fila de esa sección de la Tabla de cobertura de funciones, o añade una fila. Una sección nueva de una lista de funciones necesita una fila antes de que `make docs-check` pase.
4. Ejecuta `make docs-check`.

Mantén las páginas útiles: enlaza con el archivo que contiene un dato en lugar de copiar el dato, registra el motivo de una decisión porque los motivos cambian rara vez y los detalles constantemente, y mantén pocos ejemplos y ejecuta cada ejemplo de nuevo cuando el ejemplo cambie.

## Idiomas

La documentación existe en inglés y en cada idioma de destino de los [requisitos globales](../../../.github/work/requirements.md#language). Las listas de funciones y los documentos de requisitos siguen solo en inglés.

- **Estructura.** Cada idioma tiene las carpetas hermanas `docs/<código>/user/`, `docs/<código>/developer/` y `docs/images/<código>/`, con los mismos nombres de archivo en todos los idiomas. Los códigos son `en-gb`, `de`, `nl`, `fr`, `zh-hans`, `es`, `it`, `pl` y `sv`. Un bloque de código igual en varios idiomas se queda en el texto de cada página y se envuelve en una pareja de marcadores `jscpd:ignore-start` y `jscpd:ignore-end`, solo bajo una excepción que el usuario aprobó en un plan, como dice `AGENTS.md`. Una pareja de marcadores envuelve un solo bloque de código y nada más.
- **Generador.** `make docs` escribe `docs/<código>/user/entities/` para cada idioma a partir del archivo correspondiente de `custom_components/saj_local/translations/`. Los nombres de equipo proceden del mismo archivo de traducción, y los demás textos del generador proceden de `.github/scripts/docs_text/<código>.json`.
- **Comprobación de documentación.** `make docs-check` aplica cada regla a cada carpeta de idioma. La [Tabla de cobertura de funciones](#tabla-de-cobertura-de-funciones) de esta página se aplica a todos los idiomas con los mismos nombres de página, y la regla de imágenes huérfanas comprueba `docs/images/<código>/` frente a las páginas del mismo idioma.
- **Barra de idiomas.** La primera línea de cada página bajo `docs/<código>/user/` y `docs/<código>/developer/`, incluidas las páginas de entidades generadas, es la barra de idiomas `en | de | nl | fr | zh | es | it | pl | sv`, siempre en ese orden. Cada etiqueta salvo la del idioma actual enlaza la misma página en la carpeta de ese idioma, y el idioma actual es texto plano. `make docs` escribe la barra de idiomas, y `make docs-check` señala una página cuya primera línea no es la barra de idiomas esperada y un enlace de la barra a una página que no existe.
- **README traducido.** El `README.md` de la raíz del repositorio sigue en inglés y se traduce en `docs/<código>/README.md`, cuyos enlaces apuntan a las páginas de ese idioma. El `README.md` raíz y cada `docs/<código>/README.md` llevan la misma barra de idiomas como primera línea, y `make docs-check` señala un `docs/<código>/README.md` que falte.
- **Capturas de pantalla.** `make docs-images` ejecuta la especificación una vez por idioma, el inglés primero, con contenedores nuevos en cada ejecución. `ARGS=<código>` selecciona un idioma, consulta [Capturas de pantalla](#capturas-de-pantalla).
- **Nomenclatura.** La página `user/nomenclature.md` de cada idioma es la lista de términos que sigue toda traducción de la integración, de las tarjetas y de las páginas del idioma. La [nomenclatura](../user/nomenclature.md) en inglés es la fuente.
- **Cambiar el inglés.** Un cambio en un texto, una página o una captura en inglés actualiza todos los idiomas en el mismo cambio. Ninguna comprobación mantiene los idiomas sincronizados.

## Tabla de cobertura de funciones

Cada sección de una lista de funciones se investiga a partir de la línea `Files:` de la sección y la cubren las páginas que se nombran aquí. Cada página nombrada enlaza con la sección mediante el ancla de encabezado de la sección. El nombre de una página es relativo a `docs/en-gb/` y enlaza con la página. La tabla se encuentra solo en la página inglesa [Documentation](../../en-gb/developer/documentation.md#feature-coverage-table), y `docs-check` lee la tabla desde allí. La tabla se aplica en cada idioma a los mismos nombres de página, y una página añadida, fusionada o dividida actualiza la tabla en el mismo cambio.

## Fuentes

| Dato | Responsable |
| --- | --- |
| Qué hace SAJ Local, en un resumen breve | [índice de usuario](../user/README.md) |
| Qué puede hacer cada parte | las tres listas de funciones |
| Modelos y equipos compatibles | [equipos compatibles](../user/supported-equipment.md) |
| Nombres de entidad, ID de entidad, modelos, equipos y valores por defecto | el catálogo y `translations/en.json`, mediante la [referencia de entidades](../user/entities/README.md) |
| Tipos de entidad, reglas de habilitada por defecto y convenciones de signo | la sección Devices and entities de la lista de funciones de la integración |
| Configuración del desarrollo | [entorno](environment.md) |
| Objetivos de make y reglas de comprobación | [comprobaciones](checks.md) |
| Publicación de versiones y subida de versión de Home Assistant | [publicación de versiones](releasing.md) |
| Captura general del sitio | `docs/images/en-gb/cards-power-flow-card.png`, que los mantenedores copian al sitio web del proyecto en cada versión, consulta la [página de publicación de versiones](releasing.md) |
| Cómo informar de un problema de seguridad | `SECURITY.md` |
| Etiquetas de incidencias y reglas de las etiquetas | `.github/labels.yml` y `CONTRIBUTING.md` |
| Términos de la licencia | `LICENSE` |
| Comportamiento previsto del producto | `.github/work/requirements.md` y los tres documentos de requisitos de las partes |
