[en](../../en-gb/developer/frontend.md) | [de](../../de/developer/frontend.md) | [nl](../../nl/developer/frontend.md) | [fr](../../fr/developer/frontend.md) | [zh](../../zh-hans/developer/frontend.md) | es | [it](../../it/developer/frontend.md) | [pl](../../pl/developer/frontend.md) | [sv](../../sv/developer/frontend.md)

# Frontend

Cómo se organiza y se compila el paquete de las tarjetas, y cómo ver cada tarjeta en la instancia de desarrollo.

La lista completa de lo que cubre el frontend está en las secciones de las listas de funciones [Tarjetas](../../../custom_components/saj_local/docs/features.md#cards) de la integración y [Elementos y configuración](../../../frontend/docs/features.md#elements-and-setup) y [Tema e idioma](../../../frontend/docs/features.md#theme-and-language) de las tarjetas.

## Compilación

Las tarjetas, la función de la tarjeta mosaico y la insignia son un único paquete de Lit y TypeScript bajo `frontend/`. `make build` ejecuta Vite y escribe el paquete en `custom_components/saj_local/frontend/` como `saj-local-<hash>.js` con un `asset-manifest.json`, porque HACS distribuye el directorio de la integración como un único archivo. Git sigue el paquete compilado y el manifiesto, así que un cambio en las tarjetas se confirma junto con una nueva compilación. La integración lee el manifiesto, sirve el archivo que nombra el manifiesto y añade la URL del archivo al frontend de Home Assistant, así que los usuarios no añaden ningún recurso al panel.

El hash cambia con cada compilación para que un navegador nunca ejecute un paquete obsoleto. El coste es que Home Assistant registra el nombre de archivo con hash una sola vez, al arrancar: un paquete nuevo necesita reiniciar Home Assistant antes de que se ofrezca al navegador el archivo nuevo. La instancia de desarrollo monta el directorio de la integración, así que ejecuta `make build` y reinicia Home Assistant para ver un cambio.

## Estructura del código fuente

La estructura sigue lo que cambia junto:

- `src/system/` contiene todo lo que no es dibujo: encontrar las entidades de un sistema en `hass`, la dirección de la potencia, los días de la semana, las franjas del horario, los fallos, el bloqueo de control y las llamadas a servicios. La carpeta nunca toca el DOM, así que las reglas se prueban sin un navegador.
- `src/ui/` contiene las partes que dibuja cada tarjeta, con estilos solo de las variables del tema de Home Assistant, porque el frontend de Home Assistant no promete ningún elemento `ha-*` a las tarjetas personalizadas.
- `src/cards/`, `src/features/` y `src/badges/` contienen los elementos y registran los elementos en el selector de Home Assistant.
- `src/i18n/` contiene el texto que solo necesitan las tarjetas, un archivo por idioma, con el nombre del código de idioma de Home Assistant como los archivos de la carpeta `translations/` de la integración (inglés y los ocho idiomas de destino), con el inglés como alternativa para cualquier otro idioma. Los nombres de las entidades, los estados y los valores proceden de Home Assistant.
- `tests/fakes/` contiene un `hass` falso, construido a partir de una lista de entidades, y los sustitutos de los módulos que usa un elemento. Cada prueba unitaria ejercita un módulo con todos los colaboradores sustituidos por uno de los falsos.

Un elemento encuentra las entidades de un sistema por dispositivo y clave de traducción, nunca por ID de entidad, así que una tarjeta nunca depende de un prefijo de ID de entidad.

## Pruebas

`make test-frontend` ejecuta las pruebas unitarias de Vitest con la barrera de cobertura. `make test-browser-controlled` ejecuta Playwright contra el paquete compilado con datos controlados, y `make test-browser-home-assistant` ejecuta Playwright contra un Home Assistant real, consulta la [página de comprobaciones](checks.md#objetivos-de-make). Las capturas de pantalla de la documentación de usuario proceden de una tercera configuración de Playwright, consulta [Capturas de pantalla](documentation.md#capturas-de-pantalla).

## Paneles de muestra

Ver cada tarjeta con cada opción necesita un Home Assistant con sistemas reales, así que el entorno de desarrollo declara dos paneles, `saj-hs3` y `saj-h2`, a partir de `config/dashboards/saj-hs3.yaml` y `config/dashboards/saj-h2.yaml`, mediante el bloque `lovelace: dashboards:` de `config/configuration.yaml`. Los paneles son YAML simple escrito a mano, y ningún script genera los paneles. Cada elemento de SAJ Local es un elemento personalizado configurado con su propio YAML, así que cada tarjeta, función de mosaico e insignia se escribe individualmente con cada opción fijada, bajo un encabezado que nombra la tarjeta y sus opciones.

- Cada panel tiene cuatro vistas: Panel (las tarjetas de un panel típico de sistema, escritas como tarjetas simples), Tarjetas (cada tarjeta en cada una de sus combinaciones de opciones), Funciones e insignias (una tarjeta mosaico con la función `custom:saj-local-weekdays-feature` para cada entidad de días de la semana de una franja, y la insignia de estado) y Estados vacíos (cada tarjeta sin `device` y con el dispositivo de algo que no es SAJ Local).
- Los paneles contienen los ID de dispositivo de una instancia de desarrollo. Un desarrollador cuya instancia tenga ID de dispositivo distintos sustituye los dos ID `device` de cada archivo, el ID del sistema y el ID de un dispositivo que no es SAJ Local para la vista Estados vacíos, y los ID de entidad de días de la semana de las franjas cuando el prefijo de ID de entidad difiere.
- Home Assistant lee las declaraciones de los paneles cuando arranca Home Assistant, así que reinicia Home Assistant tras cambiar `config/configuration.yaml`. Un cambio en un archivo de panel se muestra tras recargar la página.
