[en](../../en-gb/developer/README.md) | de | [nl](../../nl/developer/README.md) | [fr](../../fr/developer/README.md) | [zh](../../zh-hans/developer/README.md) | [es](../../es/developer/README.md) | [it](../../it/developer/README.md) | [pl](../../pl/developer/README.md) | [sv](../../sv/developer/README.md)

# Entwicklerdokumentation von SAJ Local

Wie SAJ Local gebaut, geprüft und veröffentlicht wird und wo die Wahrheit über jeden Teil liegt. Die Dokumentation erklärt, warum das Projekt so gebaut ist, wie es gebaut ist, und verlinkt auf die Datei, die jede Tatsache enthält. Versionen, Befehlslisten und Registerkarten stehen im Code und in der Konfiguration, nicht hier.

Für einen funktionierenden Checkout und das Einreichen einer Änderung beginne mit [CONTRIBUTING.md](../../../CONTRIBUTING.md). SAJ Local ist eine rein lokale Integration für Home Assistant: SAJ Local spricht über das lokale Netzwerk mit dem Wechselrichter und fügt keinen Cloud-Dienst und kein zusätzliches SDK hinzu.

## Entwickeln ohne Wechselrichter

Der Simulator ist ein Stellvertreter-SAJ-Gerät, daher braucht die meiste Arbeit keine Hardware. Jeder Simulator liefert eine Seite aus, die zeigt, was das simulierte System gerade tut, und einem Entwickler erlaubt, das System zu ändern, während Home Assistant abfragt, ohne ein Szenario zu bearbeiten und neu zu starten.

![Die Übersicht der Seite des HS3-Simulators: die Statusleiste, das Energiefluss-Diagramm und eine Karte für jedes eingebaute Ausstattungsteil](../../images/de/developer-simulator-page-overview.png)

[Modbus-Simulator](simulator.md) erklärt, wofür der Simulator da ist und wie du ein Szenario ausführst. [Simulatorseite](simulator-page.md) zeigt jede Ansicht der Seite.

## Seiten

- [Modbus-Simulator](simulator.md): wofür der Simulator da ist, Szenarien und das Ausführen eines anderen Systems.
- [Simulatorseite](simulator-page.md): jede Ansicht der Seite, der Registerinspektor, das Verkehrsprotokoll, Verbindungsfehler, Voreinstellungen und gespeicherter Zustand.
- [Umgebung](environment.md): einen Checkout einrichten und das Entwicklungs-Home-Assistant mit den Simulatoren ausführen.
- [Prüfungen](checks.md): die Make-Targets, die Abdeckungsschranke und wie du einen Lauf eingrenzt.
- [Architektur](architecture.md): die SAJ-Bibliothek und die Integration, Profile, der Katalog, die Abfrage und stabile Namen.
- [Frontend](frontend.md): der Quellcode der Karten, der Build und die Showcase-Dashboards.
- [Dokumentation](documentation.md): wie diese Seiten, die erzeugte Entitätsreferenz und die Screenshots erstellt und geprüft werden.
- [Veröffentlichen](releasing.md): die Erhöhung der Home-Assistant-Version und die Schritte vor einer Veröffentlichung.

Die Benutzerdokumentation steht in der [Benutzerdokumentation](../user/README.md).

## Wo die Wahrheit liegt

| Frage | Maßgebliche Quelle |
| --- | --- |
| Was muss das Projekt leisten? | [Globale Anforderungen](../../../.github/work/requirements.md), [Anforderungen der Integration](../../../custom_components/saj_local/docs/requirements.md), [Anforderungen der Karten](../../../frontend/docs/requirements.md), [Anforderungen des Simulators](../../../mock/docs/requirements.md) |
| Was leistet jeder Teil heute? | [Funktionen der Integration](../../../custom_components/saj_local/docs/features.md), [Funktionen der Karten](../../../frontend/docs/features.md), [Funktionen des Simulators](../../../mock/docs/features.md) |
| Wie werden Code, Tests und Dokumentation geschrieben? | [code-style.md](../../../.github/work/code-style.md) |
| Welche Regeln binden alle, die hier arbeiten? | [AGENTS.md](../../../AGENTS.md) |
| Was wurde gebaut, und warum? | [done/index.md](../../../.github/work/done/index.md) |
| Was ist geplant? | [.github/work/future/](../../../.github/work/future/) |
| Welche Befehle gibt es? | [Makefile](../../../Makefile) |
| Was führt CI aus? | [ci.yml](../../../.github/workflows/ci.yml) |
| Python-Abhängigkeiten und Werkzeugeinstellungen | [pyproject.toml](../../../pyproject.toml) |
| Frontend-Abhängigkeiten und Skripte | [frontend/package.json](../../../frontend/package.json) |
| Entwicklungsdienste | [compose.yaml](../../../compose.yaml) |

Bestehender Code hat keine Autorität über Anforderungen. Wo sie sich widersprechen, ist der Code falsch oder der Verantwortliche ändert die Anforderung.

## Code-Stil

[code-style.md](../../../.github/work/code-style.md) ist die maßgebliche Quelle. Die Dokumentationsregel von code-style.md prägt diese Seiten: erkläre das Warum, nicht das Wie, und lass Namen und Typen den Rest beschreiben.
