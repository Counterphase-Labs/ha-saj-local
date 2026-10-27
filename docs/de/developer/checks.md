[en](../../en-gb/developer/checks.md) | de | [nl](../../nl/developer/checks.md) | [fr](../../fr/developer/checks.md) | [zh](../../zh-hans/developer/checks.md) | [es](../../es/developer/checks.md) | [it](../../it/developer/checks.md) | [pl](../../pl/developer/checks.md) | [sv](../../sv/developer/checks.md)

# Prüfungen

Was jedes Make-Target ausführt, wie du einen Lauf eingrenzt und welche Regeln jede Prüfung befolgt.

## Make-Targets

Jede Aktion ist ein Make-Target, und CI ruft dieselben Targets auf. Lokal bestehen und in CI bestehen bedeuten daher dasselbe. Ein neuer CI-Schritt beginnt als Make-Target. `make help` listet jedes Target mit einer Zeile auf, und `make help ARGS=<target>` beschreibt ein Target: was das Target ausführt, was das Target bei Erfolg und bei einem Fehler ausgibt, was `ARGS` bewirkt und, bei einem gruppierenden Target, welche Schritte das Target ausführt.

`make ci` führt jeden Prüfschritt aus und ist die Definition von „fertig“. GitHub führt `make ci` selbst im einen Job `checks` von [ci.yml](../../../.github/workflows/ci.yml) aus, neben den gemeinsamen Jobs von `roquerodrigo/workflows` (`lint`, `tests`, `validate`) und dem Job `hacs`. Ein Schritt, der zu `make ci` hinzukommt, läuft also in GitHub ohne Änderung am Workflow. Führe beim Iterieren die engeren Targets aus.

`make build` ist der eine Produktions-Build des Frontends. `make test` führt jede Testsuite aus, und jede Suite hat ein eigenes Target, damit eine Suite allein laufen kann:

| Target | Suite |
| --- | --- |
| `make test-python` | Die pytest-Unit-Tests der Bibliothek, der Integration, des Simulators und des Prüfläufers, ohne `tests/mock-integration` und `tests/scripts/test_runner_processes.py`, mit der Abdeckungsschranke von 100 % für Zeilen und Zweige. Ein vollständiger Lauf besteht aus zwei pytest-Läufen in eine gemeinsame Abdeckungsdatei mit dem Kern `ctrace` und einem Abdeckungskontext pro Test: `tests/saj`, `tests/mock` und `tests/scripts` ohne das Home-Assistant-Plugin und mit gesperrten Sockets, dann `tests/saj-integration` mit dem Plugin und der Schranke auf den zusammengeführten Daten. Der Schritt schlägt auch für den Rumpf jedes Tests fehl, der länger als 200 ms dauert, Einrichtung und Abbau der Fixtures nicht mitgezählt. |
| `make test-frontend` | Die Vitest-Unit-Tests der Karten, mit der Abdeckungsschranke. |
| `make test-modules` | Jedes Modul mit Logik (jede Funktion, Methode oder Verzweigung) gegen die Unit-Test-Dateien, die allein dem Modul zugeordnet sind, mit 100 % Zeilen- und Zweigabdeckung pro Modul. Die Schranke liest die Abdeckungsdaten von `make test-python`, daher führt `make test-modules` zuerst `make test-python` aus. Ein Modul mit Logik und ohne Unit-Test-Datei schlägt fehl, und ein Modul ohne Logik, etwa ein leeres Modul oder eine Datentabelle, wird übersprungen. |
| `make test-isolated` | Die Tests von `tests/saj` und `tests/mock` in einer Umgebung ohne Home Assistant, was die Grenze zwischen der Bibliothek, dem Simulator und Home Assistant beweist. Die Abdeckung wird auf den Modulen geprüft, die die Testdateien testen. |
| `make test-runner-processes` | Die Echtprozess-Tests des Prüfläufers in `tests/scripts/test_runner_processes.py`, die echte Prozesse starten und außerhalb der Abdeckung liegen. |
| `make test-browser-controlled` | Playwright gegen das gebaute Bundle und kontrollierte Daten, ohne Home Assistant. |
| `make test-browser-home-assistant` | Playwright gegen ein Wegwerf-Home-Assistant mit einem HS3-Simulator und einem H2-Simulator, was beweist, dass die Karten im echten Frontend laden und funktionieren. Das Target führt zuerst `make build` und `make mock-build` aus, weil das Home-Assistant-Image das Karten-Bundle aus dem Arbeitsverzeichnis kopiert und die Simulatoren das Image `saj-local-mock` verwenden. |
| `make mock-smoke` | Der Simulator-Container beantwortet einen Client, danach laufen die Tests in `tests/mock-integration`. Das Target führt zuerst `make mock-build` aus und führt die Szenarien aus dem Image `saj-local-mock` aus. |

Die Prüfungen, aus denen `make ci` besteht, haben ebenfalls je ein Target, damit ein Werkzeug allein laufen kann:

| Target | Prüfung |
| --- | --- |
| `make ruff` | `ruff format --check` und `ruff check`. |
| `make mypy` | Die strikte Typprüfung. |
| `make import-lint` | Die Verträge von import-linter. |
| `make complexipy` | Die Grenze der kognitiven Komplexität. |
| `make copy-paste` | Erkennung von doppeltem Code und Text mit jscpd, über das ganze Repository einschließlich `docs/`. |
| `make prettier`, `make tsc`, `make eslint` | Formatierung, Typprüfung und Lint des Frontends. |
| `make build` | Der Vite-Produktions-Build des Frontends. |
| `make release-check` | Das HACS-Archiv enthält `asset-manifest.json` und das gebaute Karten-Bundle. Das Archiv wird aus den Dateien in `custom_components/saj_local/` gebaut, daher muss das gebaute Bundle im Baum liegen. Die Version in `custom_components/saj_local/manifest.json`, `pyproject.toml` und `frontend/package.json` ist `X.Y.Z` oder `X.Y.ZbN` und in allen drei Dateien gleich, und ein Tag bei `HEAD` entspricht der Version. Ohne Tag bei `HEAD` entfällt der Tag-Vergleich. |
| `make freeze-check` | Kein Entitätsschlüssel, keine Entitäts-ID, kein gespeicherter Einstellungsschlüssel und kein Kartentyp wird entfernt, und keine Entitätsplattform, Einheit, Geräteklasse, Zustandsklasse und kein Zustandswert ändert sich, verglichen mit dem neuesten stabilen Release-Tag. Beta-Tags werden übersprungen, damit eine Beta nie die Oberfläche einfriert. Ohne stabilen Release-Tag besteht der Schritt. |
| `make docs-check` | Die erzeugte Entitätsreferenz, Links, Bilder, Seitenlänge, die Abdeckung der Funktionsliste und die Sprachleiste. Siehe die [Seite Dokumentation](documentation.md#prüfungen). |
| `make template-check` | `bug.yml` verlangt den Diagnosedownload, jedes Label, das eine Issue-Vorlage anwendet oder verlinkt, existiert in `.github/labels.yml`, und das Modell-Dropdown von `bug.yml` stimmt mit den Modellen in `translations/en.json` überein. |
| `make mock-build` | Das Simulator-Image wird gebaut und enthält keinen Bytecode. |
| `make validate` | hassfest gegen das Arbeitsverzeichnis, in Docker. Die HACS-Validierung liest das gepushte Repository, daher führt nur der Workflow-Job `hacs` die HACS-Validierung aus. |

`make lint`, `make python-ci`, `make frontend-check` und `make frontend-ci` führen Gruppen dieser Targets aus.

Vier weitere Targets sind keine Prüfungen. `make setup` installiert die Python- und Frontend-Abhängigkeiten und Chromium, `make docs` erzeugt die Entitätsreferenz neu, `make docs-images` erstellt die Screenshots der Dokumentation, führt wie der Home-Assistant-Browsertest zuerst `make build` und `make mock-build` aus und ist kein Schritt von `make ci`, und `make up`, `make down` und `make logs` führen das Entwicklungs-Home-Assistant aus, siehe die [Seite Umgebung](environment.md#home-assistant-ausführen).

Jedes Target läuft über den Prüfläufer in `.github/scripts/`. Der Prüfläufer gibt pro Schritt eine Zeile `[x]` oder `[ ]` aus, die Befunde eines fehlgeschlagenen Schritts als `file:line message` und eine abschließende Ergebniszeile. Der Prüfläufer führt jeden gewählten Schritt auch dann aus, wenn einer fehlschlägt, und meldet ein Zeitlimit, ein Signal oder ein fehlendes Werkzeug als solches. Jeder Schritt hat ein Zeitlimit. Die knappe Ausgabe sorgt dafür, dass ein Mensch oder ein Agent nur liest, was zur Behebung eines Fehlers nötig ist.

GitHub Actions sind an einen Commit-Hash gebunden, damit ein verschobener Tag nicht ändern kann, was CI ausführt.

## Optionen

- `ARGS="..."` gibt Pfade und Optionen an ein Ein-Werkzeug-Target weiter, zum Beispiel `make test-python ARGS="tests/saj/test_poller.py -k decode"` oder `make ruff ARGS="custom_components/saj_local/coordinator.py"`. `make help ARGS=<target>` nennt, was `ARGS` für jedes Target bewirkt.
- `ONLY=<step,...>` führt eine Teilmenge der Schritte eines gruppierenden Targets aus, zum Beispiel `make ci ONLY=ruff,mypy`. Ein Name, den das Target nicht ausführt, ist ein Fehler.
- `V=1` gibt die rohe Werkzeugausgabe aus und schaltet für diesen Lauf die knappe Werkzeugkonfiguration und die Umgebungseinstellungen ab.

## Abdeckung eines Teillaufs

Ein vollständiger Lauf von `make test-python` misst und prüft das ganze Paket. Wählt `ARGS` Testdateien oder Ordner aus, misst das Target die Abdeckung nur für die Module, die die Testdateien testen, nimmt die anderen Unit-Test-Dateien, die diesen Modulen zugeordnet sind, in den Lauf auf und wendet dieselbe Schranke von 100 % auf diese Module an. Ein Lauf von `tests/saj-integration/test_coordinator_write.py` führt daher auch `test_coordinator.py` und `test_coordinator_power.py` aus und prüft `coordinator.py`. Das Modul ist die Datei mit dem Namen der Testdatei ohne das Präfix `test_`, nachgeschlagen nach Testordner:

Die [Tabelle der Testordner und Modulordner](../../en-gb/developer/checks.md#coverage-of-a-subset-run) steht auf der englischen Seite.

Testdateien ohne Modul gleichen Namens stehen in `.github/scripts/pytest_scope.json`, jede mit den Modulen, die die Datei testet, und eine Testdatei ohne bekanntes Modul wird abgelehnt, bis die Datei dort eingetragen ist. Die Ordnerzuordnung steht in `.github/scripts/pytest_scope.py`. Tests mit `-k`, `-m` oder `--lf` auszuwählen braucht eine Testdatei in `ARGS`, damit die Abdeckung auf dem Modul geprüft werden kann, das die Datei testet.

Ein vollständiger Lauf von `make test-python` zeichnet auf, welcher Test jede Zeile und jeden Zweig ausgeführt hat (ein Abdeckungskontext pro Test), sodass ein Lauf beide Schranken speist. Der Kern `ctrace` wird nur für den vollständigen Lauf gesetzt, in der Umgebung seiner Befehle, weil der Standardkern `sysmon` eine Zeile nur für den ersten Test aufzeichnet, der die Zeile ausführt, und so spätere Tests ohne Kontext lässt. Derselbe vollständige Lauf misst die Dauer jedes Testrumpfs, und jeder Rumpf über 200 ms lässt den Schritt mit der Test-ID und der Zeit fehlschlagen. 200 ms unter Abdeckung sind in einem normalen Lauf etwa 50 ms, über den 125 ms, die gesunde Tests unter Abdeckung erreichen, daher schlägt die Schranke nicht zufällig fehl. Ein Teillauf behält den Kern `sysmon`, zeichnet keine Kontexte auf und wendet keine Dauerschranke an.

`test-modules` läuft in `make ci` und prüft jedes Modul auf 100 % Zeilen- und Zweigabdeckung durch die Unit-Test-Dateien, die allein dem Modul zugeordnet sind. Die Schranke zählt nur die Kontexte dieser Testdateien und den Code, der beim Import des Moduls läuft, daher zählt Abdeckung durch die Tests anderer Module nicht. `test-modules` liest die Abdeckungsdaten von `test-python`, daher führt `make test-modules` allein zuerst `test-python` aus, und `make ci` führt die Tests einmal aus. Ein Modul mit Logik und ohne Unit-Test-Datei lässt den Schritt fehlschlagen, und ein Modul ohne Logik wird übersprungen, weil die Anforderungen Tests von Konstanten verbieten. Ein Modul, das die Schranke nur im vollständigen Lauf von `test-python` besteht, bedeutet, dass andere Tests das Modul zufällig abdecken, und das ist eine echte Lücke, die zu schließen ist. `test-isolated` prüft die Abdeckung wie jeder Teillauf.

## Testen

Die Regeln stehen im [Abschnitt Tests der globalen Anforderungen](../../../.github/work/requirements.md#testing). Die Gründe:

- **Die Abdeckung zählt nur Unit-Tests.** Ein Test, der echte Module verdrahtet, hebt die Zahl, ohne eines der Module zu beweisen.
- **Unit-Tests sind schnell und isoliert.** Keine Sockets, Server, Fixture-Dateien, Echtzeit oder langen Simulationen. Zeit, Zufall und E/A werden aus diesem Grund überall im Code injiziert.
- **Integrationstests beweisen nur, dass Teile zusammenhängen.** Für den Simulator ist der Integrationstest `make mock-smoke`.
- **Keine Umgehungen im Code** von Lint-, Typ- oder Abdeckungsprüfungen. Ändere die Konfiguration, wo die Entscheidung sichtbar ist, oder strukturiere den Code um.
- **Prüfe Verhalten, nicht Konstanten.** Ein Test, der eine Registeradresse wiederholt, beweist nichts.

`tests/` enthält genau sechs Ordner:

- `tests/saj`: Unit-Tests der SAJ-Bibliothek.
- `tests/saj-integration`: Unit-Tests der Home-Assistant-Integration, keine Integrationstests.
- `tests/mock`: Unit-Tests des Modbus-Simulators, mit `profiles/` und `simulation/`.
- `tests/mock-integration`: das Container-Smoke-Skript und der Test der ausgelieferten Szenarien des Simulators.
- `tests/playwright`: die Docker-Skripte für die Browsertests.
- `tests/scripts`: die Unit-Tests des Prüfläufers und seine Echtprozess-Tests in `test_runner_processes.py`.

`tests/mock-integration` und `tests/scripts/test_runner_processes.py` liegen außerhalb des Unit-Laufs und außerhalb der Abdeckung.

## Stack

| Baustein | Warum |
| --- | --- |
| Python mit `uv` | Eine Lock-Datei, dieselben Installationen lokal und in CI. |
| Ruff, alle Regeln an | Jede Ausnahme ist eine sichtbare Entscheidung in `[tool.ruff.lint]`. |
| mypy | Das Dekodieren von Registern verführt zu Fehlern bei Skalierung, Vorzeichen und Breite, die Typen abfangen. |
| import-linter | Macht die Grenzen der [Architekturseite](architecture.md#wie-das-projekt-aufgeteilt-ist) zu einer fehlschlagenden Prüfung. |
| complexipy, jscpd | Code der Registerkarten wächst durch Duplikation; die Grenzen stoppen das Wachstum. |
| pytest, 100 Prozent Zweigabdeckung | Siehe [Testen](#testen). |
| Lit, TypeScript, Vite | Das Frontend von Home Assistant ist Lit, daher brauchen die Karten kein zweites Framework. |
| Playwright | Steuert die Karten in einem echten Browser und in einem echten Home Assistant und erstellt die [Screenshots der Dokumentation](documentation.md#screenshots). |
| Docker Compose | Siehe die [Seite Umgebung](environment.md#docker). |

Home Assistant ist in mehreren Dateien festgelegt, die sich zusammen ändern müssen, sonst laufen Lint und Tests gegen unterschiedliche Kerne. Die Schritte stehen auf der [Seite Veröffentlichen](releasing.md#die-home-assistant-version-erhöhen).
