[en](../../README.md) | de | [nl](../nl/README.md) | [fr](../fr/README.md) | [zh](../zh-hans/README.md) | [es](../es/README.md) | [it](../it/README.md) | [pl](../pl/README.md) | [sv](../sv/README.md)

# SAJ Local Home-Assistant-Integration

![SAJ Local](../../images/header.png)

[![HACS Benutzerdefiniert](https://img.shields.io/badge/HACS-Benutzerdefiniert-41BDF5.svg)](https://hacs.xyz)
[![Home Assistant](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FCounterphase-Labs%2Fha-saj-local%2Fmain%2Fhacs.json&query=%24.homeassistant&suffix=%2B&label=Home%20Assistant&logo=homeassistant&logoColor=white&color=41BDF5)](https://www.home-assistant.io)
[![Veröffentlichung](https://img.shields.io/github/v/release/Counterphase-Labs/ha-saj-local?label=Ver%C3%B6ffentlichung)](https://github.com/Counterphase-Labs/ha-saj-local/releases)
[![Aktive Installationen](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fanalytics.home-assistant.io%2Fcustom_integrations.json&query=%24.saj_local.total&label=Aktive%20Installationen&logo=homeassistant&logoColor=white&color=41BDF5)](https://analytics.home-assistant.io)
[![Prüfungen](https://github.com/Counterphase-Labs/ha-saj-local/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Counterphase-Labs/ha-saj-local/actions/workflows/ci.yml)
[![Lizenz](https://img.shields.io/github/license/Counterphase-Labs/ha-saj-local?label=Lizenz)](../../LICENSE)

⭐ [Unterstütze das Projekt auf GitHub mit einem Stern](https://github.com/Counterphase-Labs/ha-saj-local): Deine Unterstützung ist eine echte Motivation! 🙏😊

Deine SAJ-Solaranlage in Home Assistant, direkt aus dem Wechselrichter über dein eigenes Netzwerk gelesen. Kein Cloud-Konto, keine Hersteller-App dazwischen und eine Abfragestrategie, die schonend mit der Hardware umgeht.

Dies ist eine inoffizielle, von der Community entwickelte Integration. Sie wird weder von SAJ hergestellt noch unterstützt oder gutgeheißen. Siehe den [Haftungsausschluss](user/README.md#haftungsausschluss).

> **Status: in aktiver Entwicklung und noch nicht veröffentlicht.** Es gibt noch keine veröffentlichte Version.

## Warum SAJ Local

- **Sinnvolle Voreinstellungen.** Füge deinen Wechselrichter hinzu und erhalte eine funktionierende Einrichtung, ohne dich durch Seiten voller Optionen zu arbeiten. Der Wechselrichter, die Batterie und die zugehörige Ausstattung werden automatisch erkannt.
- **Schonend für deinen Wechselrichter.** Eine Verbindung und eine Anfrage zur Zeit sowie eine feste Obergrenze für Anfragen, die keine Einstellung, kein Neuladen und kein Fehler überschreiten kann. Du bestimmst, was gelesen wird und wie oft.
- **Nur lesen, solange du nichts anderes sagst.** Schreiben ist pro Installation optional, damit sich am Wechselrichter nichts versehentlich ändert.
- **Dieselben Namen bei jedem Modell.** Dashboards und Automatisierungen werden einmal geschrieben, funktionieren weiter über alle SAJ-Modelle hinweg und überstehen den Wechsel von einem H2 auf einen HS3.
- **Mehrere Systeme.** Verbinde mehr als ein SAJ-System mit demselben Home Assistant.
- **Dashboard-Karten.** Karten zum Anzeigen von Informationen und zum Ändern der Konfiguration, hinzugefügt über die Kartenauswahl.
- **Klare Fehler und sichere Diagnosen.** Wenn etwas schiefgeht, erfährst du was und warum, und Debug-Dumps sind so gebaut, dass sie sich gefahrlos teilen lassen.
- **Vollständig lokal.** Alles spricht über dein Netzwerk mit deinem Wechselrichter. Nichts wird an einen Cloud-Dienst gesendet.

## Unterstützte Geräte

Der SAJ HS3 und der einphasige SAJ H2 werden unterstützt. Die vollständige Liste und was noch nicht unterstützt wird, steht unter [unterstützte Geräte](user/supported-equipment.md).

## Dokumentation

- [Benutzerdokumentation](user/README.md): SAJ Local installieren, einrichten und bedienen.
- [Entwicklerdokumentation](developer/README.md): wie SAJ Local gebaut, geprüft und veröffentlicht wird.
- [Mitwirken](../../CONTRIBUTING.md): einen Checkout einrichten und eine Änderung einreichen.

## Hilfe und Feedback

Fragen, Fehlerberichte und Ideen sind im [Issue-Tracker](https://github.com/Counterphase-Labs/ha-saj-local/issues) willkommen.

Melde ein Sicherheitsproblem privat, siehe die [Sicherheitsrichtlinie](../../SECURITY.md).

## Lizenz

[MIT](../../LICENSE)
