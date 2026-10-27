[en](../../en-gb/developer/environment.md) | [de](../../de/developer/environment.md) | [nl](../../nl/developer/environment.md) | [fr](../../fr/developer/environment.md) | [zh](../../zh-hans/developer/environment.md) | [es](../../es/developer/environment.md) | [it](../../it/developer/environment.md) | [pl](../../pl/developer/environment.md) | sv

# Utvecklingsmiljö

Hur du ställer in en arbetskopia och kör utvecklingsinstansen av Home Assistant med simulatorerna.

## Ställ in en arbetskopia

En arbetskopia behöver [uv](https://docs.astral.sh/uv/) för Python-verktygen, Node.js och npm för korten, Docker med Docker Compose för Home Assistant och simulatorerna, samt `make`. De versioner som krävs anges i `pyproject.toml` och `frontend/package.json`. Efter kloning installerar `make setup` Python-beroendena, frontend-beroendena och webbläsaren Chromium som Playwright-testerna använder.

## Kör Home Assistant

`make up` startar Home Assistant med integrationen och två Modbus-simulatorer, en HS3 och en H2. `make logs` följer Home Assistants logg och `make down` stoppar allt.

Home Assistant finns på port 8123. HS3-simulatorn svarar på Modbus på värdporten 5020 och H2-simulatorn på 5021, och simulatorsidorna finns på 5080 och 5081. Inuti Docker når Home Assistant simulatorerna via tjänstnamnen `mock` och `mock-h2` på port 502. Ingen riktig växelriktare behövs. [Simulatorsidan](simulator.md) förklarar hur du ansluter till simulatorerna och ändrar vad simulatorerna simulerar.

För att använda andra värdportar, en annan tidszon eller andra scenarier, kopiera [compose.override.yaml.example](../../../compose.override.yaml.example) till den ignorerade filen `compose.override.yaml` och ändra det som skiljer sig. Redigera inte `compose.yaml` för lokala behov, eftersom `make mock-smoke` startar `compose.yaml` också.

## Docker

Utveckling sker i containrar så att Home Assistant är en känd, fastlåst version med en ren konfiguration. Tjänsterna definieras i dessa filer:

- [compose.yaml](../../../compose.yaml): den interaktiva miljön, med Home Assistant, HS3-simulatorn `mock` och H2-simulatorn `mock-h2`. Integrationen monteras skrivskyddat i Home Assistant, så containern skriver aldrig i källträdet. Simulatorerna behåller sina ändringar i `mock/state/hs3/` och `mock/state/h2/`, som Git ignorerar.
- [compose.playwright.yaml](../../../compose.playwright.yaml): en engångs-Home Assistant byggd från `Dockerfile.playwright-home-assistant`, med en HS3-simulator, en H2-simulator och Playwright-körare. `make test-browser-home-assistant` använder tjänsterna `homeassistant`, `mock`, `mock-h2` och `playwright` för att bevisa att varje slutpunkt kan läggas till, laddas, rapporterar sensorvärden, visar solenergi på ett effektflödeskort och, när styrning är tillåten, tar emot en ändrad inställning. `make docs-images` använder tjänsterna `homeassistant`, `mock-docs`, `mock-h2` och `playwright-docs`, se [Skärmbilder](documentation.md#skärmbilder). Tjänsterna delar inget tillstånd med den interaktiva miljön.
- `compose.override.yaml`: portarna, tidszonen och scenarierna för din maskin. Git ignorerar filen, och `compose.override.yaml.example` visar formen.

Under `config/` spårar Git bara `configuration.yaml` och de två demoinstrumentpanelerna i `config/dashboards/`. Resten är lokalt Home Assistant-tillstånd.

[Kontrollsidan](checks.md) listar vad varje make-mål kör, och [frontend-sidan](frontend.md#demoinstrumentpaneler) beskriver de två demoinstrumentpanelerna.
