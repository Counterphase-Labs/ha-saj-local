[en](../../en-gb/developer/documentation.md) | de | [nl](../../nl/developer/documentation.md) | [fr](../../fr/developer/documentation.md) | [zh](../../zh-hans/developer/documentation.md) | [es](../../es/developer/documentation.md) | [it](../../it/developer/documentation.md) | [pl](../../pl/developer/documentation.md) | [sv](../../sv/developer/documentation.md)

# Dokumentation

Wie die Dokumentationsseiten aufgebaut sind, wie die Entitätsreferenz und die Screenshots erstellt werden und woran `make docs-check` scheitert.

## Aufbau

Benutzerseiten liegen in `docs/en-gb/user/` und Entwicklerseiten in `docs/en-gb/developer/`. Jeder Ordner hat einen Index `README.md`, und jede Seite behandelt ein Thema. Keine geschriebene Seite ist länger als 300 Zeilen. Jede Tatsache hat einen Verantwortlichen, aufgeführt unter [Quellen](#quellen), und jede andere Seite verlinkt auf den Verantwortlichen, statt die Tatsache zu wiederholen.

Screenshots liegen in `docs/images/en-gb/`. Jedes Bild muss von einer Seite referenziert werden.

Schreibe die englischen Seiten in britischem Englisch, im Tonfall von Counterphase, und verwende die Begriffe, die die Übersetzungen der Integration den Benutzern zeigen. Die Benutzerseiten beschreiben SAJ allgemein und markieren an der Stelle des Unterschieds, wo sich der HS3 und der H2 unterscheiden. Eine Seite wird nie in eine Seite pro Modell aufgeteilt.

## Funktionslisten zuerst

Die drei Funktionslisten sind die Grundlage jeder Seite: [Integration](../../../custom_components/saj_local/docs/features.md), [Karten](../../../frontend/docs/features.md) und [Simulator](../../../mock/docs/features.md). Ein Abschnitt einer Funktionsliste sagt, was gebaut ist, und nennt die zu lesenden Dateien in der Zeile `Files:` des Abschnitts. Bestätige jede Aussage anhand dieser Dateien, bevor du sie dokumentierst. Die Anforderungsdokumente sagen, was beabsichtigt ist, und werden nur für die Absicht gelesen. Ein Verhalten, das in einem Anforderungsdokument steht, aber in keiner Funktionsliste, ist nicht gebaut, und eine Benutzerseite beschreibt das Verhalten nicht als verfügbar. Wo eine Funktionsliste und der Code sich widersprechen, ist der Code das, was Benutzer bekommen, also korrigiere die Funktionsliste in derselben Änderung.

Eine Seite, die Code beschreibt, verlinkt auf den Abschnitt der Funktionsliste, dessen Zeile `Files:` den Code nennt, und wiederholt die Dateiliste nicht.

Eine Änderung einer Fähigkeit aktualisiert die Funktionsliste des Teils und jede Benutzerseite, die auf den geänderten Abschnitt verlinkt, in derselben Änderung. Die Regel steht in der `AGENTS.md` im Wurzelverzeichnis.

## Erzeugte Entitätsreferenz

`docs/en-gb/user/entities/` enthält eine erzeugte Seite pro Bereich und einen Index `README.md`. Führe `make docs` aus, um die Seiten neu zu erzeugen, und committe dann die neu erzeugten Seiten. Prosaseiten nennen nie eine Entität von Hand; die Prosaseiten verlinken auf die erzeugten Seiten. Erzeugte Seiten sind von der Grenze von 300 Zeilen ausgenommen, weil Leser einen Bereich wie die Batterie durchsuchen, statt ihn zu lesen.

Der Generator ist `.github/scripts/docs_check.py`, von `make docs` mit `--write` ausgeführt. Der Generator importiert nur die SAJ-Bibliothek und liest `custom_components/saj_local/translations/en.json`, daher braucht der Generator kein Home Assistant. Jede Bereichsseite beginnt mit einem Link auf die Abschnitte der Funktionsliste, die den Bereich behandeln, und einer Zeile zum Präfix der Entitäts-ID, und hat dann eine Zeile pro Entität mit dem Namen aus `en.json`, der Entitäts-ID ohne Präfix, dem Typ, der Einheit, den Modellen, die die Entität haben, der Ausstattung, die bei jeder Phasen-, String- oder Packanzahl vorhanden sein muss, und ob die Entität standardmäßig aktiviert ist. Eine Entität, die zwei Modelle verschieden definieren, zum Beispiel mit einer anderen Einheit, bekommt eine Zeile pro Definition.

### Quellen der Entitäten

Jede Entität stammt aus einer dieser Quellen, und der Generator liest alle:

| Quelle | Code | Entitäten |
| --- | --- | --- |
| Der Registerkatalog jedes ausgelieferten Modells | `catalogue_of` in [catalogue.py](../../../custom_components/saj_local/saj/catalogue.py), aufgerufen für jedes Profil in `PROFILES` von [profiles.py](../../../custom_components/saj_local/saj/profiles.py), wobei Zeilen übersprungen werden, die nicht bereitgestellt werden | Sensoren, Binärsensoren (die Fehler), Zahlen, Auswahlen, Schalter, Zeiten und Schaltflächen |
| Der Sensor Steuerung zugelassen | `CONTROL_ALLOWED_KEY` in [binary_sensor.py](../../../custom_components/saj_local/binary_sensor.py) | `binary_sensor.saj_control_allowed`, bei beiden Modellen |
| Die Schalter und Zahlen der Leistungssteuerung | `power_control` jedes Profils ([hs3.py](../../../custom_components/saj_local/saj/models/hs3.py) und [h2.py](../../../custom_components/saj_local/saj/models/h2.py)), die `PowerFunction`-Schlüssel in [models/\_\_init\_\_.py](../../../custom_components/saj_local/saj/models/__init__.py) und `FUNCTION_EQUIPMENT` in [power_control.py](../../../custom_components/saj_local/saj/power_control.py), erstellt von [switch.py](../../../custom_components/saj_local/switch.py) und [number.py](../../../custom_components/saj_local/number.py) | Ein Schalter und eine Zahl für jede Leistungsfunktion eines Modells: Batterie bei beiden Modellen, Netz und Wechselrichter beim HS3 |

`make docs-check` schlägt fehl, wenn eine Entität im Block `entity` von `en.json` auf keiner Bereichsseite steht, daher fällt eine Entitätsquelle, die der Generator nicht liest, sofort auf. Eine neue Quelle braucht einen Generator, der die Quelle liest, und eine Zeile in der Tabelle oben.

### Bereiche

Eine Entität landet im ersten passenden Bereich, in dieser Reihenfolge:

1. Entitäten außerhalb des Katalogs: Von der Integration hinzugefügt.
2. Binärsensoren aus dem Katalog, das sind die Fehler: Fehler.
3. Entitäten mit einem Batteriepack-Index: Batteriepacks.
4. Entitäten optionaler Ausstattung: Batterie, Netz und Zähler A, Zähler B, Wallbox oder Parallelsystem.
5. Schreibbare Entitäten ohne Ausstattung: Einstellungen.
6. Entitäten, deren Schlüssel mit `grid_` beginnt: Netz und Zähler A.
7. Alles andere: Wechselrichter und PV.

Die Tabelle `AREAS` in `.github/scripts/docs_check.py` nennt die Bereiche, ihre Zusammenfassungen und die Abschnitte der Funktionsliste, die jede Bereichsseite verlinkt.

## Prüfungen

`make docs-check` führt `.github/scripts/docs_check.py` ohne `--write` aus und meldet pro Befund eine Zeile:

- eine erzeugte Seite, die von dem abweicht, was `make docs` schreiben würde;
- eine Entität in `en.json`, die auf keiner Bereichsseite steht, und eine erzeugte Entität ohne Namen in `en.json`;
- ein relativer Link, ein Bild oder ein Überschriften-Anker, der nicht aufgelöst wird, in den Seiten, `README.md`, `CONTRIBUTING.md`, `SECURITY.md` und jeder `AGENTS.md`, einschließlich der Links in die Funktionslisten und die Anforderungsdokumente;
- ein Bild in `docs/images/`, das keine Seite referenziert;
- eine geschriebene Seite über 300 Zeilen;
- ein Abschnitt einer Funktionsliste ohne Zeile in der [Tabelle der Funktionsabdeckung](#tabelle-der-funktionsabdeckung), ein in der Tabelle genannter Abschnitt, den die Funktionsliste nicht hat, eine in der Tabelle genannte Seite, die nicht existiert, und eine Seite, die nicht auf den in der Zeile genannten Abschnitt der Funktionsliste verlinkt, über den Überschriften-Anker des Abschnitts.

`make docs-check` ist ein Schritt von `make ci`, und GitHub führt `make ci` aus, daher braucht die Prüfung keine Änderung am Workflow. Die Prüfung liest keinen Screenshot über die Regeln für Links und verwaiste Bilder hinaus und startet keinen Browser.

## Screenshots

Jeder Screenshot in `docs/images/<code>/` wird von `make docs-images` aus einem echten Home Assistant in Docker erstellt, dessen Benutzersprache auf die Sprache des Ordners gesetzt ist, oder von den Simulatorseiten desselben Laufs. `make docs-images` führt jede Sprache aus, Englisch zuerst, mit frischen Containern für jeden Lauf, und `ARGS=<code>` wählt eine Sprache. Kein Screenshot wird von Hand bearbeitet oder aufgenommen, daher lässt sich der Satz neu aufbauen, sobald sich die Oberfläche ändert. Die Screenshots zeigen die Simulatoren, daher ist jeder Messwert in einem Screenshot ein simulierter Wert.

Das Target führt `tests/playwright/run-docs-images.sh` aus, das die Dienste `homeassistant` und `playwright-docs` von [compose.playwright.yaml](../../../compose.playwright.yaml) baut, das Wegwerf-Home-Assistant und zwei Simulatoren startet, die Spec ausführt und danach die Container, Volumes und lokalen Images entfernt. Das Target braucht Docker, hat dasselbe Zeitlimit wie `make test-browser-home-assistant` und nimmt Optionen über `ARGS` entgegen, die das Skript erhält. Das Home-Assistant-Image wird aus `Dockerfile.playwright-home-assistant` gebaut, das das Karten-Bundle baut und die Integration ins Image kopiert, daher wird kein Integrationscode eingebunden. Die Spec ist `frontend/tests/browser/docs/screenshots.spec.ts`, konfiguriert durch `frontend/playwright.docs.config.ts`.

- **Systeme.** Der HS3 ist der Simulator `mock-docs` mit `mock/scenarios/hs3-full-house.yaml`, der jede Ausstattung eingebaut hat. Der H2 ist der Simulator `mock-h2` mit `mock/scenarios/h2-battery.yaml` und erhält das Entitäts-Präfix `h2`. Kein Simulator bindet einen Zustandsordner ein, daher beginnt jeder Lauf beim Szenario.
- **Feste Bedingungen.** Der Viewport ist 1280 mal 800 Pixel, das Design ist hell und die Uhr ist echt. Ein hoher Dialog oder eine hohe Karte wird in einem 1600 Pixel hohen Fenster aufgenommen, weil die feste Kopfzeile von Home Assistant sonst den oberen Teil des Elements verdecken würde.
- **Sprache.** Jeder Lauf setzt sowohl die Home-Assistant-Serversprache, bevor SAJ Local eingerichtet wird, damit die Entitäten mit Namen in dieser Sprache angelegt werden, als auch die Benutzersprache, über den Sprachcode und nicht über die Bezeichnung der Sprachauswahl. Der Lauf schlägt fehl, wenn ein Entitätsname von SAJ Local nicht in der Sprache des Laufs ist. Die Bilder gehen nach `docs/images/<code>/`. Die Spec öffnet Bildschirme über die URL-Route, findet die Felder der SAJ-Local-Formulare über ihr Attribut `name` und findet Bedienelemente von Home Assistant, die nur einen Text haben, über den Text, der zur Laufzeit mit `hass.localize` aus dem laufenden Home Assistant gelesen wird. Die Spec enthält keine Tabelle von Bezeichnungen, daher führt jede Sprache dieselben Schritte aus.
- **Namen.** Jede Datei heißt `<page>-<subject>.png`, wobei `<page>` der Seitenpfad mit `/` durch `-` ersetzt ist, zum Beispiel `cards-battery-card.png`, und die Seite, die das Bild zeigt, verlinkt auf die Datei.
- **Simulatorseiten.** Die Screenshots der Simulatorseiten stammen von den zwei Simulatoren desselben Laufs, `mock-docs` und `mock-h2`, und verwenden das Namenspräfix `developer-simulator-page-`. Sie werden zuletzt aufgenommen, nach jedem Home-Assistant-Screenshot, damit nichts, was auf einer Simulatorseite getan wird, einen Home-Assistant-Screenshot ändert. Die Spec setzt auf der HS3-Seite den Fehler „Fan 1 fault“, und das Register, das der Reparatur-Screenshot den Simulator verweigern lässt, bleibt verweigert, daher zeigen die Ansicht Link, das Verkehrsprotokoll und die Änderungen in der Statusleiste echte Änderungen.
- **Einrichtung.** Die Spec legt über die Onboarding-API einen Benutzer an, fügt den HS3 über den Einrichtungsablauf im Browser hinzu, fügt den H2 über die API des Einrichtungsablaufs hinzu, schaltet bei beiden Systemen Steuerung zulassen ein und fügt über die WebSocket-API von Home Assistant für jedes System ein Dashboard mit jeder SAJ-Local-Karte und dem Status-Badge hinzu.
- **Alles oder nichts.** Die Spec wartet bis zu zwei Minuten darauf, dass beide Systeme Solarleistung melden. Die Spec schreibt die Bilder erst, nachdem jeder Schritt bestanden hat, daher lässt ein fehlgeschlagener Lauf die committeten Bilder unverändert.
- **Wartezeiten.** Die Spec wartet auf einen Bildschirm, indem sie auf den Zustand prüft, den der Bildschirm zeigt, nie mit einer festen Pause.
- **Reparatur.** Der Reparatur-Screenshot zeigt die Reparaturmeldung zu verweigerten Registern. Die Spec fügt eine Abfragegruppe für die Wechselrichtertemperatur mit einem Intervall von 10 Sekunden hinzu, lässt den Simulator dieses Register über `POST /api/link` der Simulatorseite verweigern und wartet bis zu zwei Minuten, bis `repairs/list_issues` das Problem `registers_refused` von SAJ Local auflistet. Der Lauf schlägt mit einer Meldung fehl, die das fehlende Problem nennt, wenn das Problem nicht erscheint.
- **Formulare.** Die Warnung zur Präfixänderung wird aufgenommen und das Formular danach geschlossen, was den Ablauf abbricht, daher wird kein Präfix gespeichert. Die Warnung zu Steuerung zulassen wird aufgenommen und danach bestätigt, weil die Karten Steuerung zulassen brauchen.
- **Fehlschläge.** Der HTML-Bericht liegt in `frontend/playwright-report/docs/`, und ein fehlgeschlagener Lauf speichert das Home-Assistant-Protokoll als `frontend/test-results/docs/home-assistant.log`.

Screenshots werden weder in CI noch anderswo Pixel für Pixel verglichen. Home Assistant stellt Live-Werte und Schriften von Lauf zu Lauf verschieden dar, daher würde ein Pixelvergleich ohne echte Änderung fehlschlagen. Prüfe ein geändertes Bild, indem du das Bild ansiehst.

### Einen Screenshot hinzufügen oder ändern

1. Füge die Aufnahme in der Spec hinzu oder ändere sie, mit dem Dateinamen in der Form `<page>-<subject>.png`.
2. Referenziere das Bild von der Seite, die das Thema erklärt.
3. Führe `make docs-images` aus, sieh dir die geänderten Bilder an und committe die geänderten Bilder.
4. Führe `make docs-check` aus. Ein Bild, das keine Seite referenziert, und ein Link auf ein Bild, das nicht existiert, werden beide gemeldet.

`make docs-images` ist kein Schritt von `make ci`, und CI erzeugt die Bilder nicht neu. Führe das Target vor jeder Veröffentlichung aus, siehe die [Seite Veröffentlichen](releasing.md).

## Eine Seite hinzufügen

1. Lege die Seite unter `docs/en-gb/user/` oder `docs/en-gb/developer/` an und verlinke die Seite vom Index des Ordners.
2. Verlinke die Seite auf den Abschnitt der Funktionsliste, dessen Zeile `Files:` den Code nennt, den die Seite beschreibt.
3. Füge die Seite zur Zeile dieses Abschnitts in der Tabelle der Funktionsabdeckung hinzu, oder füge eine Zeile hinzu. Ein neuer Abschnitt einer Funktionsliste braucht eine Zeile, bevor `make docs-check` besteht.
4. Führe `make docs-check` aus.

Halte die Seiten nützlich: verlinke auf die Datei, die eine Tatsache enthält, statt die Tatsache zu kopieren, halte den Grund einer Entscheidung fest, weil sich Gründe selten und Details ständig ändern, und halte Beispiele knapp und führe jedes Beispiel erneut aus, wenn sich das Beispiel ändert.

## Sprachen

Die Dokumentation gibt es auf Englisch und in jeder Zielsprache der [globalen Anforderungen](../../../.github/work/requirements.md#language). Die Funktionslisten und die Anforderungsdokumente bleiben nur auf Englisch.

- **Aufbau.** Jede Sprache hat die gleichrangigen Ordner `docs/<code>/user/`, `docs/<code>/developer/` und `docs/images/<code>/`, mit denselben Dateinamen in jeder Sprache. Die Codes sind `en-gb`, `de`, `nl`, `fr`, `zh-hans`, `es`, `it`, `pl` und `sv`. Ein Codeblock, der in mehreren Sprachen gleich ist, bleibt auf jeder Seite im Text und steht in einem Markerpaar `jscpd:ignore-start` und `jscpd:ignore-end`, nur unter einer Ausnahme, die der Benutzer in einem Plan genehmigt hat, wie `AGENTS.md` es festlegt. Ein Markerpaar umschließt einen Codeblock und nichts anderes.
- **Generator.** `make docs` schreibt `docs/<code>/user/entities/` für jede Sprache aus der passenden Datei in `custom_components/saj_local/translations/`. Die Namen der Ausstattung stammen aus derselben Übersetzungsdatei, und die anderen Texte des Generators stammen aus `.github/scripts/docs_text/<code>.json`.
- **Dokumentationsprüfung.** `make docs-check` wendet jede Regel auf jeden Sprachordner an. Die [Tabelle der Funktionsabdeckung](#tabelle-der-funktionsabdeckung) auf dieser Seite gilt für jede Sprache unter denselben Seitennamen, und die Regel für verwaiste Bilder prüft `docs/images/<code>/` gegen die Seiten derselben Sprache.
- **Sprachleiste.** Die erste Zeile jeder Seite unter `docs/<code>/user/` und `docs/<code>/developer/`, die erzeugten Entitätsseiten eingeschlossen, ist die Sprachleiste `en | de | nl | fr | zh | es | it | pl | sv`, immer in dieser Reihenfolge. Jede Bezeichnung außer der aktuellen Sprache verlinkt dieselbe Seite im Ordner der jeweiligen Sprache, und die aktuelle Sprache ist einfacher Text. `make docs` schreibt die Sprachleiste, und `make docs-check` meldet eine Seite, deren erste Zeile nicht die erwartete Sprachleiste ist, sowie einen Link der Sprachleiste auf eine Seite, die nicht existiert.
- **Übersetzte README.** Die `README.md` im Wurzelverzeichnis bleibt englisch und ist unter `docs/<code>/README.md` übersetzt, deren Links auf die Seiten der jeweiligen Sprache zeigen. Die `README.md` im Wurzelverzeichnis und jede `docs/<code>/README.md` tragen dieselbe Sprachleiste als erste Zeile, und `make docs-check` meldet eine fehlende `docs/<code>/README.md`.
- **Screenshots.** `make docs-images` führt die Spec einmal pro Sprache aus, Englisch zuerst, mit frischen Containern für jeden Lauf. `ARGS=<code>` wählt eine Sprache, siehe [Screenshots](#screenshots).
- **Begriffe.** Die Seite `user/nomenclature.md` jeder Sprache ist die Liste der Begriffe, denen jede Übersetzung der Integration, der Karten und der Seiten der Sprache folgt, hier die Seite [Begriffe](../user/nomenclature.md). Die englische Seite `user/nomenclature.md` ist die Quelle.
- **Englisch ändern.** Eine Änderung an einem englischen Text, einer Seite oder einem Screenshot aktualisiert jede Sprache in derselben Änderung. Keine Prüfung hält die Sprachen im Gleichschritt.

## Tabelle der Funktionsabdeckung

Jeder Abschnitt einer Funktionsliste wird anhand der Zeile `Files:` des Abschnitts untersucht und von den hier genannten Seiten abgedeckt. Jede genannte Seite verlinkt auf den Abschnitt über den Überschriften-Anker des Abschnitts. Die Tabelle steht nur auf der englischen Seite [Dokumentation](../../en-gb/developer/documentation.md#feature-coverage-table), und `docs-check` liest die Tabelle von dort. Die Tabelle gilt in jeder Sprache für dieselben Seitennamen, und eine hinzugefügte, zusammengeführte oder geteilte Seite aktualisiert die Tabelle in derselben Änderung.

## Quellen

| Tatsache | Verantwortlicher |
| --- | --- |
| Was SAJ Local leistet, in einer kurzen Zusammenfassung | [Benutzerindex](../user/README.md) |
| Was jeder Teil kann | die drei Funktionslisten |
| Unterstützte Modelle und Ausstattung | [Unterstützte Ausstattung](../user/supported-equipment.md) |
| Entitätsnamen, Entitäts-IDs, Modelle, Ausstattung und Standardwerte | der Katalog und `translations/en.json`, über die [Entitätsreferenz](../user/entities/README.md) |
| Entitätstypen, Regeln zur Standardaktivierung und Vorzeichenkonventionen | der Abschnitt Geräte und Entitäten der Funktionsliste der Integration |
| Entwicklungsumgebung | [Umgebung](environment.md) |
| Make-Targets und Prüfregeln | [Prüfungen](checks.md) |
| Erhöhung der Home-Assistant-Version | [Veröffentlichen](releasing.md) |
| Screenshot für die Übersicht der Website | `docs/images/en-gb/cards-power-flow-card.png`, bei jeder Veröffentlichung nach `assets/images/saj-local-power-flow.png` im Repository `website` kopiert, siehe die [Seite Veröffentlichen](releasing.md) |
| Wie man ein Sicherheitsproblem meldet | `SECURITY.md` |
| Issue-Labels und die Regeln für Labels | `.github/labels.yml` und `CONTRIBUTING.md` |
| Lizenzbedingungen | `LICENSE` |
| Beabsichtigtes Produktverhalten | `.github/work/requirements.md` und die drei Anforderungsdokumente der Teile |
