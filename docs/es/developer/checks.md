[en](../../en-gb/developer/checks.md) | [de](../../de/developer/checks.md) | [nl](../../nl/developer/checks.md) | [fr](../../fr/developer/checks.md) | [zh](../../zh-hans/developer/checks.md) | es | [it](../../it/developer/checks.md) | [pl](../../pl/developer/checks.md) | [sv](../../sv/developer/checks.md)

# Comprobaciones

Qué ejecuta cada objetivo de make, cómo acotar una ejecución y las reglas que sigue toda comprobación.

## Objetivos de make

Cada acción es un objetivo de make y CI llama a los mismos objetivos, así que pasar en local y pasar en CI significan lo mismo. Un paso nuevo de CI empieza como un objetivo de make. `make help` lista cada objetivo con una línea, y `make help ARGS=<objetivo>` describe un objetivo: qué ejecuta el objetivo, qué imprime el objetivo si tiene éxito y si falla, qué hace `ARGS` y, para un objetivo de agrupación, los pasos que ejecuta el objetivo.

`make ci` ejecuta cada paso de comprobación y es la definición de terminado. GitHub ejecuta `make ci` en el único trabajo `checks` de [ci.yml](../../../.github/workflows/ci.yml), junto a los trabajos compartidos de `roquerodrigo/workflows` (`lint`, `tests`, `validate`) y el trabajo `hacs`, así que un paso añadido a `make ci` se ejecuta en GitHub sin cambiar el flujo de trabajo. Ejecuta los objetivos más acotados mientras iteras.

`make build` es la única compilación de producción del frontend. `make test` ejecuta todas las suites de pruebas, y cada suite tiene su propio objetivo para poder ejecutar una suite sola:

| Objetivo | Suite |
| --- | --- |
| `make test-python` | Las pruebas unitarias de pytest de la biblioteca, la integración, el simulador y el ejecutor de comprobaciones, sin `tests/mock-integration` ni `tests/scripts/test_runner_processes.py`, con la barrera de cobertura del 100 % de líneas y ramas. Una ejecución completa son dos ejecuciones de pytest sobre un mismo archivo de datos de cobertura con el núcleo `ctrace` y un contexto de cobertura por prueba: `tests/saj`, `tests/mock` y `tests/scripts` sin el complemento de Home Assistant y con los sockets bloqueados, y después `tests/saj-integration` con el complemento y la barrera sobre los datos combinados. El paso también falla por el cuerpo de cualquier prueba que tarde más de 200 ms, sin contar la preparación ni el desmontaje de los fixtures. |
| `make test-frontend` | Las pruebas unitarias de Vitest de las tarjetas, con la barrera de cobertura. |
| `make test-modules` | Cada módulo con lógica (cualquier función, método o rama) frente solo a los archivos de pruebas unitarias asignados al módulo, con el 100 % de cobertura de líneas y ramas exigido por módulo. La barrera lee los datos de cobertura de `make test-python`, así que `make test-modules` ejecuta primero `make test-python`. Un módulo con lógica y sin archivo de pruebas unitarias falla, y un módulo sin lógica, como un módulo vacío o una tabla de datos, se omite. |
| `make test-isolated` | Las pruebas de `tests/saj` y `tests/mock` en un entorno sin Home Assistant, lo que demuestra la frontera entre la biblioteca, el simulador y Home Assistant. La cobertura se exige sobre los módulos que prueban los archivos de pruebas. |
| `make test-runner-processes` | Las pruebas con procesos reales del ejecutor de comprobaciones en `tests/scripts/test_runner_processes.py`, que inician procesos reales y quedan fuera de la cobertura. |
| `make test-browser-controlled` | Playwright contra el paquete compilado y datos controlados, sin Home Assistant. |
| `make test-browser-home-assistant` | Playwright contra un Home Assistant desechable con un simulador HS3 y un simulador H2, lo que demuestra que las tarjetas cargan y funcionan en el frontend real. El objetivo ejecuta primero `make build` y `make mock-build`, porque la imagen de Home Assistant copia el paquete de tarjetas del árbol de trabajo y los simuladores usan la imagen `saj-local-mock`. |
| `make mock-smoke` | El contenedor del simulador responde a un cliente y después se ejecutan las pruebas de `tests/mock-integration`. El objetivo ejecuta primero `make mock-build` y ejecuta los escenarios desde la imagen `saj-local-mock`. |

Las comprobaciones que forman `make ci` también tienen un objetivo cada una, para poder ejecutar una herramienta sola:

| Objetivo | Comprobación |
| --- | --- |
| `make ruff` | `ruff format --check` y `ruff check`. |
| `make mypy` | La comprobación estricta de tipos. |
| `make import-lint` | Los contratos de import-linter. |
| `make complexipy` | El límite de complejidad cognitiva. |
| `make copy-paste` | Detección de código y texto duplicados con jscpd, sobre todo el repositorio, incluido `docs/`. |
| `make prettier`, `make tsc`, `make eslint` | Formato, comprobación de tipos y lint del frontend. |
| `make build` | La compilación de producción de Vite del frontend. |
| `make release-check` | El archivo de HACS contiene `asset-manifest.json` y el paquete de tarjetas compilado. El archivo se crea a partir de los archivos de `custom_components/saj_local/`, así que el paquete compilado debe estar en el árbol. La versión de `custom_components/saj_local/manifest.json`, `pyproject.toml` y `frontend/package.json` es `X.Y.Z` o `X.Y.ZbN` e igual en los tres archivos, y una etiqueta en `HEAD` es igual a la versión. Sin etiqueta en `HEAD` se omite la comparación de la etiqueta. |
| `make freeze-check` | No se quita ninguna clave de entidad, ID de entidad, clave de ajuste guardado ni tipo de tarjeta, y no cambia ninguna plataforma de entidad, unidad, clase de dispositivo, clase de estado ni valor de estado, en comparación con la etiqueta de versión estable más reciente. Las etiquetas beta se omiten, así que una beta nunca congela la superficie. Sin etiqueta de versión estable el paso pasa. |
| `make docs-check` | La referencia de entidades generada, los enlaces, las imágenes, la longitud de las páginas, la cobertura de la lista de funciones y la barra de idiomas. Consulta la [página de documentación](documentation.md#comprobaciones). |
| `make template-check` | `bug.yml` exige la descarga de diagnósticos, toda etiqueta que una plantilla de incidencia aplica o enlaza existe en `.github/labels.yml`, y el desplegable de modelos de `bug.yml` coincide con los modelos de `translations/en.json`. |
| `make mock-build` | La imagen del simulador se compila y no contiene bytecode. |
| `make validate` | hassfest sobre el árbol de trabajo, en Docker. La validación de HACS lee el repositorio publicado, así que solo el trabajo `hacs` de CI ejecuta la validación de HACS. |

`make lint`, `make python-ci`, `make frontend-check` y `make frontend-ci` ejecutan grupos de estos objetivos.

Otros cuatro objetivos no son comprobaciones. `make setup` instala las dependencias de Python y del frontend y Chromium, `make docs` regenera la referencia de entidades, `make docs-images` hace las capturas de pantalla de la documentación, ejecuta primero `make build` y `make mock-build` como la prueba de navegador de Home Assistant y no es un paso de `make ci`, y `make up`, `make down` y `make logs` ejecutan el Home Assistant de desarrollo, consulta la [página del entorno](environment.md#ejecutar-home-assistant).

Todo objetivo se ejecuta mediante el ejecutor de comprobaciones de `.github/scripts/`. El ejecutor imprime una línea `[x]` o `[ ]` por paso, los hallazgos de un paso que falla como `file:line message` y una línea de resultado final. El ejecutor ejecuta cada paso seleccionado aunque uno falle, e informa de un tiempo de espera agotado, una señal o una herramienta ausente como tales. Cada paso tiene un límite de tiempo. La salida reducida existe para que una persona o un agente lea solo lo necesario para corregir un fallo.

Las acciones de GitHub están fijadas a un hash de confirmación para que una etiqueta movida no pueda cambiar lo que ejecuta CI.

## Opciones

- `ARGS="..."` pasa rutas y opciones a un objetivo de una sola herramienta, por ejemplo `make test-python ARGS="tests/saj/test_poller.py -k decode"` o `make ruff ARGS="custom_components/saj_local/coordinator.py"`. `make help ARGS=<objetivo>` indica qué hace `ARGS` en cada objetivo.
- `ONLY=<paso,...>` ejecuta un subconjunto de los pasos de un objetivo de agrupación, por ejemplo `make ci ONLY=ruff,mypy`. Un nombre que el objetivo no ejecuta es un error.
- `V=1` muestra en directo la salida sin procesar de la herramienta y desactiva la configuración reducida de la herramienta y los ajustes del entorno en esa ejecución.

## Cobertura de una ejecución parcial

Un `make test-python` completo mide y exige la cobertura de todo el paquete. Cuando `ARGS` selecciona archivos o carpetas de pruebas, el objetivo mide la cobertura solo de los módulos que prueban los archivos de pruebas, añade a la ejecución los demás archivos de pruebas unitarias asignados a esos módulos y aplica la misma barrera del 100 % a esos módulos. Una ejecución de `tests/saj-integration/test_coordinator_write.py` ejecuta por tanto también `test_coordinator.py` y `test_coordinator_power.py` y exige la cobertura de `coordinator.py`. El módulo es el archivo con el nombre del archivo de pruebas sin el prefijo `test_`, buscado por carpeta de pruebas:

La [tabla de carpetas de pruebas y carpetas de módulos](../../en-gb/developer/checks.md#coverage-of-a-subset-run) está en la página en inglés.

Los archivos de pruebas sin un módulo del mismo nombre se listan en `.github/scripts/pytest_scope.json`, cada uno con los módulos que prueba el archivo, y un archivo de pruebas sin módulo conocido se rechaza hasta que se añada allí. La asignación por carpeta está en `.github/scripts/pytest_scope.py`. Seleccionar pruebas con `-k`, `-m` o `--lf` exige un archivo de pruebas en `ARGS`, para poder exigir la cobertura del módulo que prueba el archivo.

Un `make test-python` completo registra qué prueba ejecutó cada línea y cada rama (un contexto de cobertura por prueba), así que una ejecución alimenta ambas barreras. El núcleo `ctrace` se fija solo para la ejecución completa, en el entorno de sus comandos, porque el núcleo `sysmon` por defecto registra una línea para la primera prueba que la ejecuta y así deja sin contexto a las pruebas posteriores. La misma ejecución completa mide la duración del cuerpo de cada prueba, y cualquier cuerpo de más de 200 ms hace fallar el paso con el ID de la prueba y el tiempo. 200 ms con cobertura son unos 50 ms en una ejecución normal, por encima de los 125 ms que alcanzan las pruebas sanas con cobertura, así que la barrera no falla al azar. Una ejecución parcial mantiene el núcleo `sysmon`, no registra contextos y no aplica barrera de duración.

`test-modules` se ejecuta en `make ci` y exige a cada módulo el 100 % de cobertura de líneas y ramas con los archivos de pruebas unitarias asignados al módulo solamente. La barrera cuenta solo los contextos de esos archivos de pruebas y el código que se ejecuta al importar el módulo, así que la cobertura de las pruebas de otros módulos no cuenta. `test-modules` lee los datos de cobertura de `test-python`, así que `make test-modules` solo ejecuta primero `test-python` y `make ci` ejecuta las pruebas una vez. Un módulo con lógica y sin archivo de pruebas unitarias hace fallar el paso, y un módulo sin lógica se omite, porque los requisitos prohíben las pruebas de constantes. Un módulo que solo pasa la barrera en la ejecución completa de `test-python` significa que otras pruebas cubren el módulo por casualidad, y eso es una laguna real que corregir. `test-isolated` exige la cobertura igual que cualquier ejecución parcial.

## Pruebas

Las reglas están en la [sección Pruebas de los requisitos globales](../../../.github/work/requirements.md#testing). Los motivos:

- **La cobertura cuenta solo las pruebas unitarias.** Una prueba que conecta módulos reales sube la cifra sin demostrar ninguno de los módulos.
- **Las pruebas unitarias son rápidas y aisladas.** Sin sockets, servidores, archivos fixture, tiempo real ni simulaciones largas. El tiempo, el azar y la E/S se inyectan en todo el código por este motivo.
- **Las pruebas de integración solo demuestran que las partes se conectan.** Para el simulador, la prueba de integración es `make mock-smoke`.
- **Sin elusiones en línea** de las comprobaciones de lint, tipos o cobertura. Cambia la configuración, donde la decisión es visible, o reestructura el código.
- **Comprueba el comportamiento, no las constantes.** Una prueba que repite la dirección de un registro no demuestra nada.

`tests/` contiene exactamente seis carpetas:

- `tests/saj`: pruebas unitarias de la biblioteca SAJ.
- `tests/saj-integration`: pruebas unitarias de la integración de Home Assistant, no pruebas de integración.
- `tests/mock`: pruebas unitarias del simulador Modbus, con `profiles/` y `simulation/`.
- `tests/mock-integration`: el script de humo del contenedor y la prueba del escenario distribuido del simulador.
- `tests/playwright`: los scripts de Docker para las pruebas de navegador.
- `tests/scripts`: las pruebas unitarias del ejecutor de comprobaciones y sus pruebas con procesos reales en `test_runner_processes.py`.

`tests/mock-integration` y `tests/scripts/test_runner_processes.py` quedan fuera de la ejecución unitaria y fuera de la cobertura.

## Pila tecnológica

| Pieza | Por qué |
| --- | --- |
| Python con `uv` | Un solo archivo de bloqueo, las mismas instalaciones en local y en CI. |
| Ruff, todas las reglas activadas | Cada excepción es una decisión visible en `[tool.ruff.lint]`. |
| mypy | La decodificación de registros invita a errores de escala, signo y anchura que los tipos detectan. |
| import-linter | Convierte las fronteras de la [página de arquitectura](architecture.md#cómo-se-divide-el-proyecto) en una comprobación que falla. |
| complexipy, jscpd | El código de mapas de registros crece por duplicación; los límites detienen el crecimiento. |
| pytest, 100 por ciento de cobertura de ramas | Consulta [Pruebas](#pruebas). |
| Lit, TypeScript, Vite | El frontend de Home Assistant es Lit, así que las tarjetas no necesitan un segundo framework. |
| Playwright | Maneja las tarjetas en un navegador real y en un Home Assistant real, y hace las [capturas de pantalla de la documentación](documentation.md#capturas-de-pantalla). |
| Docker Compose | Consulta la [página del entorno](environment.md#docker). |

Home Assistant está fijado en varios archivos que deben cambiar a la vez, o lint y pruebas se ejecutan contra núcleos distintos. Los pasos están en la [página de publicación de versiones](releasing.md#subir-la-versión-de-home-assistant).
