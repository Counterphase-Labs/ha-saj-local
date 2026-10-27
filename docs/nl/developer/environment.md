[en](../../en-gb/developer/environment.md) | [de](../../de/developer/environment.md) | nl | [fr](../../fr/developer/environment.md) | [zh](../../zh-hans/developer/environment.md) | [es](../../es/developer/environment.md) | [it](../../it/developer/environment.md) | [pl](../../pl/developer/environment.md) | [sv](../../sv/developer/environment.md)

# Ontwikkelomgeving

Hoe u een checkout instelt en de ontwikkel-Home Assistant-instantie met de simulators draait.

## Een checkout instellen

Een checkout heeft [uv](https://docs.astral.sh/uv/) nodig voor de Python-tools, Node.js en npm voor de kaarten, Docker met Docker Compose voor Home Assistant en de simulators, en `make`. De vereiste versies staan in `pyproject.toml` en `frontend/package.json`. Na het klonen installeert `make setup` de Python-afhankelijkheden, de frontend-afhankelijkheden en de Chromium-browser die de Playwright-tests gebruiken.

## Home Assistant draaien

`make up` start Home Assistant met de integratie en twee Modbus-simulators, een HS3 en een H2. `make logs` volgt het Home Assistant-logboek en `make down` stopt alles.

Home Assistant staat op poort 8123. De HS3-simulator antwoordt op Modbus op hostpoort 5020 en de H2-simulator op 5021, en de simulatorpagina's staan op 5080 en 5081. Binnen Docker bereikt Home Assistant de simulators via de servicenamen `mock` en `mock-h2` op poort 502. Er is geen echte omvormer nodig. De [simulatorpagina](simulator.md) legt uit hoe u verbinding maakt met de simulators en wijzigt wat de simulators simuleren.

Kopieer [compose.override.yaml.example](../../../compose.override.yaml.example) naar het genegeerde `compose.override.yaml` en wijzig wat afwijkt om andere hostpoorten, een andere tijdzone of andere scenario's te gebruiken. Bewerk `compose.yaml` niet voor lokale behoeften, omdat `make mock-smoke` ook `compose.yaml` start.

## Docker

Ontwikkeling draait in containers, zodat Home Assistant een bekende, vastgepinde release met een schone configuratie is. De services worden in deze bestanden gedefinieerd:

- [compose.yaml](../../../compose.yaml): de interactieve omgeving, met Home Assistant, de HS3-simulator `mock` en de H2-simulator `mock-h2`. De integratie wordt alleen-lezen in Home Assistant gemount, zodat de container nooit in de broncodeboom schrijft. De simulators bewaren hun wijzigingen in `mock/state/hs3/` en `mock/state/h2/`, die Git negeert.
- [compose.playwright.yaml](../../../compose.playwright.yaml): een wegwerp-Home Assistant gebouwd uit `Dockerfile.playwright-home-assistant`, met een HS3-simulator, een H2-simulator en Playwright-runners. `make test-browser-home-assistant` gebruikt de services `homeassistant`, `mock`, `mock-h2` en `playwright` om te bewijzen dat elk eindpunt kan worden toegevoegd, laadt, sensorwaarden meldt, zonnevermogen toont op een vermogensstroomkaart en, zodra bediening is toegestaan, een gewijzigde instelling accepteert. `make docs-images` gebruikt de services `homeassistant`, `mock-docs`, `mock-h2` en `playwright-docs`, zie [Schermafbeeldingen](documentation.md#schermafbeeldingen). De services delen geen toestand met de interactieve omgeving.
- `compose.override.yaml`: de poorten, tijdzone en scenario's van uw machine. Git negeert het bestand, en `compose.override.yaml.example` toont de vorm.

Onder `config/` volgt Git alleen `configuration.yaml` en de twee showcase-dashboards in `config/dashboards/`. De rest is lokale Home Assistant-toestand.

De [pagina Controles](checks.md) vermeldt wat elke make-target draait, en de [frontendpagina](frontend.md#showcase-dashboards) beschrijft de twee showcase-dashboards.
