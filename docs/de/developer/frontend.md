[en](../../en-gb/developer/frontend.md) | de | [nl](../../nl/developer/frontend.md) | [fr](../../fr/developer/frontend.md) | [zh](../../zh-hans/developer/frontend.md) | [es](../../es/developer/frontend.md) | [it](../../it/developer/frontend.md) | [pl](../../pl/developer/frontend.md) | [sv](../../sv/developer/frontend.md)

# Frontend

Wie das Karten-Bundle aufgebaut und gebaut wird und wie du jede Karte in der Entwicklungsinstanz ansiehst.

Die vollständige Liste dessen, was das Frontend abdeckt, steht in den Abschnitten der Funktionslisten [Karten](../../../custom_components/saj_local/docs/features.md#cards) der Integration und [Elemente und Einrichtung](../../../frontend/docs/features.md#elements-and-setup) und [Design und Sprache](../../../frontend/docs/features.md#theme-and-language) der Karten.

## Build

Die Karten, die Funktion für Kachel-Karten und das Badge sind ein Lit-und-TypeScript-Bundle unter `frontend/`. `make build` führt Vite aus und schreibt das Bundle als `saj-local-<hash>.js` mit einer `asset-manifest.json` nach `custom_components/saj_local/frontend/`, weil HACS das Verzeichnis der Integration als ein Archiv ausliefert. Git verfolgt das gebaute Bundle und das Manifest, daher wird eine Änderung an den Karten zusammen mit einem neuen Build committet. Die Integration liest das Manifest, liefert die Datei aus, die das Manifest nennt, und fügt die URL der Datei dem Home-Assistant-Frontend hinzu, sodass Benutzer keine Dashboard-Ressource hinzufügen.

Der Hash ändert sich mit jedem Build, damit ein Browser nie ein veraltetes Bundle ausführt. Der Preis ist, dass Home Assistant den gehashten Dateinamen einmal beim Start registriert: Ein neues Bundle braucht einen Neustart von Home Assistant, bevor dem Browser die neue Datei angeboten wird. Die Entwicklungsinstanz bindet das Verzeichnis der Integration ein, also führe `make build` aus und starte Home Assistant neu, um eine Änderung zu sehen.

## Aufbau des Quellcodes

Der Aufbau folgt dem, was sich zusammen ändert:

- `src/system/` enthält alles, was nicht zeichnet: die Entitäten eines Systems in `hass` finden, Leistungsrichtung, Wochentage, Zeitfenster, Fehler, die Steuerungssperre und Dienstaufrufe. Der Ordner berührt nie das DOM, daher werden die Regeln ohne Browser getestet.
- `src/ui/` enthält die Teile, die jede Karte zeichnet, nur mit den Design-Variablen von Home Assistant gestaltet, weil das Home-Assistant-Frontend Karten von Drittanbietern kein `ha-*`-Element verspricht.
- `src/cards/`, `src/features/` und `src/badges/` enthalten die Elemente und registrieren die Elemente bei der Auswahl von Home Assistant.
- `src/i18n/` enthält den Text, den nur die Karten brauchen, eine Datei pro Sprache, benannt nach dem Home-Assistant-Sprachcode wie die Dateien im Ordner `translations/` der Integration (Englisch und die acht Zielsprachen), mit Englisch als Rückfall für jede andere Sprache. Entitätsnamen, Zustände und Werte kommen von Home Assistant.
- `tests/fakes/` enthält ein gefälschtes `hass`, aus einer Liste von Entitäten gebaut, und die Ersatzimplementierungen für die Module, die ein Element verwendet. Jeder Unit-Test prüft ein Modul, bei dem jeder Mitspieler durch einen der Fakes ersetzt ist.

Ein Element findet die Entitäten eines Systems über Gerät und Übersetzungsschlüssel, nie über die Entitäts-ID, daher hängt eine Karte nie von einem Präfix der Entitäts-ID ab.

## Tests

`make test-frontend` führt die Vitest-Unit-Tests mit der Abdeckungsschranke aus. `make test-browser-controlled` führt Playwright gegen das gebaute Bundle mit kontrollierten Daten aus, und `make test-browser-home-assistant` führt Playwright gegen ein echtes Home Assistant aus, siehe die [Seite Prüfungen](checks.md#make-targets). Die Screenshots der Benutzerdokumentation stammen aus einer dritten Playwright-Konfiguration, siehe [Screenshots](documentation.md#screenshots).

## Showcase-Dashboards

Jede Karte in jeder Option anzusehen braucht ein Home Assistant mit echten Systemen, daher deklariert die Entwicklungsumgebung zwei Dashboards, `saj-hs3` und `saj-h2`, aus `config/dashboards/saj-hs3.yaml` und `config/dashboards/saj-h2.yaml`, über den Block `lovelace: dashboards:` von `config/configuration.yaml`. Die Dashboards sind einfaches, von Hand geschriebenes YAML, und kein Skript erzeugt die Dashboards. Jedes SAJ-Local-Element ist ein Custom Element, das durch sein eigenes YAML konfiguriert wird, daher ist jede Karte, jede Kachel-Funktion und jedes Badge einzeln mit jeder gesetzten Option ausgeschrieben, unter einer Überschrift, die die Karte und ihre Optionen nennt.

- Jedes Dashboard hat vier Ansichten: Dashboard (die Karten eines typischen Systemdashboards, als einfache Karten ausgeschrieben), Cards (jede Karte in jeder ihrer Optionskombinationen), Features and badges (eine Kachel-Karte mit der Funktion `custom:saj-local-weekdays-feature` für jede Wochentage-Entität eines Zeitfensters, und das Status-Badge) und Empty states (jede Karte ohne `device` und mit dem Gerät von etwas, das nicht SAJ Local ist).
- Die Dashboards enthalten die Geräte-IDs einer Entwicklungsinstanz. Ein Entwickler, dessen Instanz andere Geräte-IDs hat, ersetzt die zwei `device`-IDs in jeder Datei, die ID des Systems und die ID eines Geräts, das nicht SAJ Local ist, für die Ansicht Empty states, und die Entitäts-IDs der Wochentage der Zeitfenster, wenn das Präfix der Entitäts-ID abweicht.
- Home Assistant liest die Dashboard-Deklarationen beim Start von Home Assistant, also starte Home Assistant nach einer Änderung von `config/configuration.yaml` neu. Eine Änderung an einer Dashboard-Datei zeigt sich nach dem Neuladen der Seite.
