[en](../../en-gb/developer/environment.md) | de | [nl](../../nl/developer/environment.md) | [fr](../../fr/developer/environment.md) | [zh](../../zh-hans/developer/environment.md) | [es](../../es/developer/environment.md) | [it](../../it/developer/environment.md) | [pl](../../pl/developer/environment.md) | [sv](../../sv/developer/environment.md)

# Entwicklungsumgebung

Wie du einen Checkout einrichtest und die Entwicklungsinstanz von Home Assistant mit den Simulatoren ausführst.

## Einen Checkout einrichten

Ein Checkout braucht [uv](https://docs.astral.sh/uv/) für die Python-Werkzeuge, Node.js und npm für die Karten, Docker mit Docker Compose für Home Assistant und die Simulatoren sowie `make`. Die benötigten Versionen stehen in `pyproject.toml` und `frontend/package.json`. Nach dem Klonen installiert `make setup` die Python-Abhängigkeiten, die Frontend-Abhängigkeiten und den Chromium-Browser, den die Playwright-Tests verwenden.

## Home Assistant ausführen

`make up` startet Home Assistant mit der Integration und zwei Modbus-Simulatoren, einem HS3 und einem H2. `make logs` folgt dem Protokoll von Home Assistant und `make down` stoppt alles.

Home Assistant liegt auf Port 8123. Der HS3-Simulator beantwortet Modbus auf dem Host-Port 5020 und der H2-Simulator auf 5021, und die Simulatorseiten liegen auf 5080 und 5081. Innerhalb von Docker erreicht Home Assistant die Simulatoren über die Dienstnamen `mock` und `mock-h2` auf Port 502. Es wird kein echter Wechselrichter gebraucht. Die [Simulatorseite](simulator.md) erklärt, wie du dich mit den Simulatoren verbindest und änderst, was die Simulatoren simulieren.

Um andere Host-Ports, eine andere Zeitzone oder andere Szenarien zu verwenden, kopiere [compose.override.yaml.example](../../../compose.override.yaml.example) nach `compose.override.yaml`, das von Git ignoriert wird, und ändere, was abweicht. Bearbeite `compose.yaml` nicht für lokale Bedürfnisse, weil `make mock-smoke` ebenfalls `compose.yaml` startet.

## Docker

Die Entwicklung läuft in Containern, damit Home Assistant ein bekanntes, festgelegtes Release mit sauberer Konfiguration ist. Die Dienste sind in diesen Dateien definiert:

- [compose.yaml](../../../compose.yaml): die interaktive Umgebung mit Home Assistant, dem HS3-Simulator `mock` und dem H2-Simulator `mock-h2`. Die Integration wird schreibgeschützt in Home Assistant eingebunden, sodass der Container nie in den Quellbaum schreibt. Die Simulatoren behalten ihre Änderungen in `mock/state/hs3/` und `mock/state/h2/`, die Git ignoriert.
- [compose.playwright.yaml](../../../compose.playwright.yaml): ein Wegwerf-Home-Assistant, gebaut aus `Dockerfile.playwright-home-assistant`, mit einem HS3-Simulator, einem H2-Simulator und Playwright-Läufern. `make test-browser-home-assistant` verwendet die Dienste `homeassistant`, `mock`, `mock-h2` und `playwright`, um zu beweisen, dass sich jeder Endpunkt hinzufügen lässt, lädt, Sensorwerte meldet, die Solarleistung auf einer Energiefluss-Karte zeigt und, sobald die Steuerung zugelassen ist, eine geänderte Einstellung annimmt. `make docs-images` verwendet die Dienste `homeassistant`, `mock-docs`, `mock-h2` und `playwright-docs`, siehe [Screenshots](documentation.md#screenshots). Die Dienste teilen keinen Zustand mit der interaktiven Umgebung.
- `compose.override.yaml`: die Ports, die Zeitzone und die Szenarien deines Rechners. Git ignoriert die Datei, und `compose.override.yaml.example` zeigt die Form.

Unter `config/` verfolgt Git nur `configuration.yaml` und die zwei Showcase-Dashboards in `config/dashboards/`. Der Rest ist lokaler Home-Assistant-Zustand.

Die [Seite Prüfungen](checks.md) listet auf, was jedes Make-Target ausführt, und die [Frontend-Seite](frontend.md#showcase-dashboards) beschreibt die zwei Showcase-Dashboards.
