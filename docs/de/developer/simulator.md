[en](../../en-gb/developer/simulator.md) | de | [nl](../../nl/developer/simulator.md) | [fr](../../fr/developer/simulator.md) | [zh](../../zh-hans/developer/simulator.md) | [es](../../es/developer/simulator.md) | [it](../../it/developer/simulator.md) | [pl](../../pl/developer/simulator.md) | [sv](../../sv/developer/simulator.md)

# Modbus-Simulator

![Die Übersicht der Seite des HS3-Simulators: die Statusleiste, das Energiefluss-Diagramm und eine Karte für jedes eingebaute Ausstattungsteil](../../images/de/developer-simulator-page-overview.png)

Wofür der Simulator da ist, wie du ein Szenario ausführst und konfigurierst und wie du den Simulator erweiterst.

Die vollständige Liste dessen, was der Simulator abdeckt, steht in den Abschnitten der Funktionsliste [Simulierte Modelle](../../../mock/docs/features.md#simulated-models), [Szenarien](../../../mock/docs/features.md#scenarios), [Variation](../../../mock/docs/features.md#variation).

Der Simulator ist ein Stellvertreter-SAJ-Gerät, mit dem sich Home Assistant oder jeder Modbus-Client verbinden kann, damit die Integration entwickelt werden kann, ohne die Hardware zu besitzen oder die Hardware zu gefährden. Der Simulator zielt auf glaubwürdige Smoke-Tests, nicht auf exakte Emulation, und ist kein allgemeiner Modbus-Server. Das Paket ist `mock/saj_local_mock/`, und jeder Simulator läuft in einem eigenen Container.

## Designentscheidungen

- **Eigenständig.** Der Simulator teilt keinen Code mit der Integration, und ein Vertrag von import-linter verbietet dem Simulator, Home Assistant oder `custom_components` zu importieren. Würden beide Seiten dieselben Registerdefinitionen verwenden, bliebe ein Fehler in den Definitionen unsichtbar.
- **Eine eigene Modbus-Schicht.** Echte SAJ-Geräte brechen den Standard: ungewöhnliche Ausnahmecodes, Blöcke, die Lesezugriffe über ihr Ende hinaus ablehnen, ein niedriges Limit für Clients. Die Integration muss mit solchen Fehlern zurechtkommen, daher sind die Fehler eingebaut.
- **Ein Container, ein Gerät.** Jede Instanz hält ihren eigenen Zustand in einem eigenen Ordner unter `mock/state/`, daher beeinflussen sich Instanzen nie.
- **Während des Laufs änderbar.** Das Szenario ist der Ausgangspunkt, nicht die einzige Eingabe. Die Simulatorseite und eingehende Anfragen ändern das laufende System, und das Szenario bleibt der bekannte Zustand, zu dem man zurückkehrt.
- **Deterministisch.** Wetter und Last hängen nur vom Seed und der simulierten Zeit ab. Dasselbe Szenario, derselbe Zeitpunkt und dieselben Schreibzugriffe geben dieselben Werte, egal wie oft ein Client abfragt.
- **Eine Energiebilanz.** Nur Einstrahlung und Last werden erzeugt; alles andere wird abgeleitet, daher widersprechen sich die Register nie.
- **Schreibzugriffe wirken.** Einstellungen werden gespeichert, zurückgelesen und ausgeführt. Ein Schreibzugriff von der Seite durchläuft dieselbe Validierung und Verarbeitung wie ein Modbus-Schreibzugriff, daher kann die Integration beide nicht unterscheiden, und die Seite kann das Gerät nicht in einen Zustand versetzen, den ein Client nicht herstellen könnte.
- **Die Seite weiß nichts über Modelle.** Die Seite baut sich aus der Beschreibung auf, die das Gerät gibt, daher braucht ein neues Modell keine Änderung der Seite. Die Seite ist ein Entwicklungswerkzeug, daher besteht die Seite aus einfachen HTML-, CSS- und JavaScript-Dateien in `mock/static/`, die unverändert ausgeliefert werden, ohne Bibliotheken, ohne Build-Schritt und ohne eigene Tests der Seite, während das Python hinter der Seite wie der Rest getestet wird. Siehe die [Simulatorseite](simulator-page.md).
- **Das Modul ist Teil der Simulation.** Der Modbus-Server steht für das Kommunikationsmodul, mit dem sich ein Client verbindet, daher sind die Fehler, die Feldberichte von diesen Modulen beschreiben (langsame oder fehlende Antworten, ungewöhnliche Ausnahmecodes, abgebrochene Verbindungen, eine Sperre), Einstellungen des Simulators und keine Sonderfälle im ganzen Gerätecode.
- **Das Schreibverhalten stammt aus den SAJ-Dokumenten.** Schreibzugriffe sind durch die Protokolldokumente von SAJ und echte Messwerte festgelegt, nicht durch den Simulator. Weicht der Simulator vom dokumentierten Verhalten von `0x06` und `0x10` ab, ist die Abweichung ein Fehler des Simulators, der zu melden ist, und nichts, um das man die Integration herum anpasst.

## Orientierung

| Wofür | Wo nachsehen |
| --- | --- |
| Warum der Simulator so gebaut ist | Die erledigten Arbeiten [SAJ-Modbus-Mock-Simulator bauen](../../../.github/work/done/build-saj-modbus-mock-simulator.md), [Bedienfeld des Simulators hinzufügen](../../../.github/work/done/add-simulator-control-panel.md) und [Simulator-Bedienfeld mit Inspektor und Verbindungsfehlern neu gestalten](../../../.github/work/done/redesign-simulator-panel-with-inspector-and-link-faults.md) |
| Fertige Systeme | [mock/scenarios/](../../../mock/scenarios/) |
| Gültige Szenarioschlüssel und Standardwerte | `mock/saj_local_mock/scenario.py` |
| Was jedes Modell unterstützt | `mock/saj_local_mock/models.py` |
| Register | `mock/saj_local_mock/profiles/` |
| Wie sich Werte entwickeln | `mock/saj_local_mock/simulation/` |
| Dienste und Ports | [compose.yaml](../../../compose.yaml) |
| Simulatorseite | `panel.py` (Routen), `description.py`, `presets.py` und die Seite in [mock/static/](../../../mock/static/) |
| Verbindungsfehler | `mock/saj_local_mock/link.py` (Einstellungen, Grenzen, Entscheidungen) und `transport.py` (Ausführung der Entscheidungen) |
| Verkehrsaufzeichnung | `mock/saj_local_mock/traffic.py` |
| Fehlerbits pro Modell | `mock/saj_local_mock/profiles/fault_tables.py` |
| Gespeicherter Zustand | `mock/saj_local_mock/persistence.py` |

Der Transport weiß nichts über SAJ, das Gerät besitzt Adressen und Zugriffsregeln, ein Profil bindet Register an simulierte Größen, und die Simulation weiß nicht, wie Werte transportiert werden. Die Schichten getrennt zu halten, erlaubt es, jede Schicht allein per Unit-Test zu testen.

## Mit dem Simulator vom Terminal sprechen

`make up` startet die Simulatoren. Home Assistant erreicht jeden über seinen Compose-Dienstnamen auf dem eigenen Port des Simulators; von deinem Rechner aus verwendest du `localhost` und den veröffentlichten Port aus `compose.yaml`.

Die Beispiele verwenden [mbpoll](https://github.com/epsilonrt/mbpoll) gegen den veröffentlichten Port des HS3-Simulators. `-0` lässt Adressen zu den Registerkarten passen, `-1` liest einmal, `-t 4` wählt Holding-Register und `-a` ist die Unit-ID.

Lies den Gerätetyp und die Nennleistung (Register `0x8F00` und `0x8F01`):

<!-- jscpd:ignore-start -->
```bash
mbpoll -m tcp -p 5020 -a 1 -0 -1 -t 4:hex -r 0x8F00 -c 2 localhost
```
<!-- jscpd:ignore-end -->

Ein HS3 und ein H2 antworten mit verschiedenen Gerätetypen, was der schnellste Weg ist, zu bestätigen, welches System ein Port simuliert.

Schreibe eine Einstellung und lies die Einstellung zurück (hier der Anwendungsmodus bei `0x3647`):

<!-- jscpd:ignore-start -->
```bash
mbpoll -m tcp -p 5020 -a 1 -0 -t 4 -r 0x3647 localhost 1
mbpoll -m tcp -p 5020 -a 1 -0 -1 -t 4 -r 0x3647 localhost
```
<!-- jscpd:ignore-end -->

Sieh, wie der Simulator eine Anfrage ablehnt, zum Beispiel eine Adresse außerhalb jedes Blocks:

<!-- jscpd:ignore-start -->
```bash
mbpoll -m tcp -p 5020 -a 1 -0 -1 -t 4 -r 0x0001 localhost
```
<!-- jscpd:ignore-end -->

Beobachte, wie sich ein Wert ändert, indem du `-1` weglässt; mbpoll fragt dann einmal pro Sekunde ab, bis du stoppst.

Führe den eigenen Healthcheck des Simulators aus, der keinen installierten Client braucht:

<!-- jscpd:ignore-start -->
```bash
docker compose exec mock python -m saj_local_mock healthcheck; echo $?
```
<!-- jscpd:ignore-end -->

Schreibzugriffe bleiben über Neustarts in `mock/state/` erhalten, das Git ignoriert, und werden auf der Simulatorseite oder durch Löschen des Ordnerinhalts zurückgesetzt, siehe [Gespeicherter Zustand](simulator-page.md#voreinstellungen-gespeicherter-zustand-und-export). Adressen stammen aus den Profilen; die drei oben sind nur Ausgangspunkte.

## Ein Szenario konfigurieren

Ein Szenario ist eine YAML-Datei, die unter `/config/config.yaml` eingebunden wird. Nur `device.model` ist erforderlich, daher nennt eine Datei nur, was von den Standardwerten abweicht:

<!-- jscpd:ignore-start -->
```yaml
device:
  model: hs3
simulation:
  start: "2026-06-21T12:00:00"
  speed: 600
battery:
  modules: 4
```
<!-- jscpd:ignore-end -->

Im Beispiel ist `simulation.speed` die Anzahl simulierter Sekunden pro echter Sekunde, daher läuft das Beispiel jede Sekunde zehn simulierte Minuten, beginnend am Mittag im Hochsommer: nützlich, um einen ganzen Tag mit Laden und Entladen in wenigen Minuten zu beobachten. `simulation.seed` wählt das Wetter und die Last.

Zwei Abschnitte formen das Zufallsverhalten und die Fehler beim Start; ein dritter, `link`, ist unter [Verbindungsfehler](simulator-page.md#verbindungsfehler) beschrieben. `variation` legt die Grenzen, die Tiefe und die Periode der Generatoren für Solar, Last und Netz fest (das Lastniveau bleibt in `site.load`), und `faults` listet die aktiven Fehlerbits pro Ausstattung nach Register und Bit auf, dazu Codes der Batteriepacks:

<!-- jscpd:ignore-start -->
```yaml
variation:
  cloud_depth: 0.9
faults:
  inverter:
    - {register: 0x4005, bit: 23}
  packs:
    - {pack: 1, fault: 1}
```
<!-- jscpd:ignore-end -->

Ein falscher Schlüssel oder eine unmögliche Kombination hält den Simulator beim Start an und nennt den Schlüssel. Der Simulator schreibt die Zeile auf die Fehlerausgabe und beendet sich:

```text
invalid scenario: ev_charger.installed: not available on h2
```

## Ein anderes oder zusätzliches System ausführen

**Ein Szenario einmal ausprobieren**, ohne eine Datei zu ändern. Der Simulator läuft im Vordergrund auf einem eigenen Port, bis du den Simulator stoppst:

<!-- jscpd:ignore-start -->
```bash
docker compose run --rm --no-deps -p 5030:502 \
  -v ./mock/scenarios/hs3-off-grid.yaml:/config/config.yaml:ro \
  -v ./mock/state/off-grid:/data \
  mock
```
<!-- jscpd:ignore-end -->

Das zusätzliche `-v` ist nötig, weil der Dienst `mock` sonst die Einbindung `/data` von `mock/state/hs3/` mitbringt, und die erste Änderung im Off-Grid-Lauf würde die `state.json` des Entwicklungs-HS3 durch den Off-Grid-Zustand ersetzen. Der Off-Grid-Lauf behält seinen eigenen Zustand in `mock/state/off-grid/` über Läufe hinweg.

Richte das erste `-v` auf deine eigene Datei, um ein Szenario auszuführen, das du geschrieben hast.

**Ändere, was `make up` startet**, in `compose.override.yaml`. Eine andere Datei über denselben Pfad einzubinden ersetzt das Szenario; ein neuer Dienst fügt ein System hinzu:

<!-- jscpd:ignore-start -->
```yaml
services:
  mock:
    volumes:
      - ./mock/scenarios/hs3-ev.yaml:/config/config.yaml:ro

  mock-off-grid:
    build:
      context: ./mock
    volumes:
      - ./mock/scenarios/hs3-off-grid.yaml:/config/config.yaml:ro
    ports:
      - "5022:502"
```
<!-- jscpd:ignore-end -->

Jeder Dienst ist ein unabhängiges Gerät mit eigenem Zustand. Home Assistant erreicht den neuen Dienst als `mock-off-grid`, daher können mehrere Systeme nebeneinander zu einem Home Assistant hinzugefügt werden.

## Den Simulator erweitern

- **Neues Szenario:** eine Datei in `mock/scenarios/`. `make mock-smoke` nimmt jede Datei im Ordner auf.
- **Neues Modell:** ein Eintrag in `models.py`, ein Profil in `profiles/` und die Annahme durch die Szenariovalidierung in `scenario.py`.
- **Neue Eigenart:** in der Schicht, die sie besitzt. Framing und Verbindungen im Transport, Adressen und Zugriff im Gerät, Modellverhalten im Profil.

Der Simulator besteht dieselben Schranken wie die Integration, siehe die [Seite Prüfungen](checks.md).
