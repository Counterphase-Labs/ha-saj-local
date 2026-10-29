[en](../../en-gb/user/README.md) | de | [nl](../../nl/user/README.md) | [fr](../../fr/user/README.md) | [zh](../../zh-hans/user/README.md) | [es](../../es/user/README.md) | [it](../../it/user/README.md) | [pl](../../pl/user/README.md) | [sv](../../sv/user/README.md)

# Benutzerdokumentation von SAJ Local

SAJ Local ist eine lokale Integration für Home Assistant. SAJ Local liest eine SAJ-HS3- oder -H2-Solaranlage direkt im Wechselrichter über Modbus TCP in deinem eigenen Netzwerk aus und ändert, wenn du die Steuerung zulässt, die Einstellungen des Wechselrichters von Home Assistant aus. SAJ Local braucht kein Cloud-Konto und begrenzt die Anfragen an den Wechselrichter, damit das Kommunikationsmodul des Wechselrichters weiter funktioniert.

SAJ Local ist eine inoffizielle, von der Community gebaute Integration. SAJ stellt SAJ Local nicht her, unterstützt SAJ Local nicht und empfiehlt SAJ Local nicht. Siehe den [Haftungsausschluss](#haftungsausschluss).

SAJ Local hat noch keine stabile Version. Jede Version vor `1.0.0` ist eine Beta, siehe [Beta-Versionen](installation.md#beta-versionen). Jede Seite unten nennt, was noch nicht unterstützt wird. Die Dokumentation behandelt den HS3 und den H2 und kennzeichnet die Unterschiede mit einem Hinweis wie „Nur HS3“. Die Screenshots stammen von simulierten Systemen, daher sind die Messwerte nicht echt.

## Hier beginnen

1. [SAJ Local installieren](installation.md) mit HACS.
2. Prüfe, ob dein Wechselrichter zur [unterstützten Ausstattung](supported-equipment.md) gehört.
3. [Erste Schritte](getting-started.md): dein erstes System hinzufügen.
4. Lies über die [optionale Ausstattung](optional-equipment.md), die SAJ Local für dich erkennt.

## Dein System verstehen

- [Entitäten und das Präfix](entities-and-prefix.md): was die Entitäten sind, wie die Entitäts-IDs gebildet werden und wie du ein Präfix hinzufügst.
- [Entitätsreferenz](entities/README.md): jede Entität mit Entitäts-ID, Modellen, Ausstattung und Standardwert. Aus der Integration erzeugt.
- [Abfrage](polling.md): wie oft der Wechselrichter gelesen wird und wie du einige Entitäten schneller oder langsamer liest.
- [Den Wechselrichter schützen](protecting-the-inverter.md): die Grenzen, die SAJ Local für die eigenen Anfragen einhält.

## Dinge ändern

- [Einstellungen ändern](changing-settings.md): die Steuerung zulassen, Einstellungen ändern und EMS nutzen.
- [Leistungssteuerung](power-control.md): die Batterie, den Netzanschluss oder den Wechselrichter auf einer festen Leistung halten, von Hand oder mit einem Zeitplan.
- [Den Wechselrichter austauschen](replacing-the-inverter.md): ein System auf einen neuen Wechselrichter oder zwischen einem H2 und einem HS3 umstellen und den Verlauf behalten.

## Dashboards

- [Dashboard-Karten](cards/README.md): die Karten, die Funktion für Kachel-Karten und das Badge, die SAJ Local zu Home Assistant hinzufügt.

## Begriffe

- [Begriffe](nomenclature.md): die SAJ- und Home-Assistant-Begriffe, die die Integration, die Karten und die Dokumentation verwenden, mit ihrer Bedeutung.

## Wenn etwas nicht stimmt

- [Gerätefehler und Reparaturen](faults-and-repairs.md): die Fehler, die die Ausstattung meldet, und die Reparaturmeldungen, die SAJ Local auslöst.
- [Fehlerbehebung](troubleshooting.md): Diagnose, Debug-Protokollierung und wo du Hilfe bekommst.

## Was jeder Teil kann

Die Funktionslisten (auf Englisch) nennen, was heute gebaut ist: [die Integration](../../../custom_components/saj_local/docs/features.md) und [die Karten](../../../frontend/docs/features.md).

Entwickler: siehe die [Entwicklerdokumentation](../developer/README.md).

## Haftungsausschluss

SAJ Local ist eine unabhängige, von der Community gebaute Integration. SAJ Local steht in keiner Verbindung zu SAJ (Guangzhou Sanjing Electric Co., Ltd.), und SAJ sowie die Tochter- und Partnerunternehmen von SAJ haben SAJ Local weder autorisiert noch gesponsert noch empfohlen.

SAJ, das SAJ-Logo und alle zugehörigen Produktnamen, Modellnamen und Marken sind Eigentum der jeweiligen Inhaber. Die Dokumentation verwendet die Namen nur, um die Ausstattung zu bezeichnen, mit der SAJ Local arbeitet.

Die Software wird so bereitgestellt, wie sie ist, ohne Gewährleistung jeder Art. Du verwendest SAJ Local auf eigenes Risiko: Die Autoren übernehmen keine Haftung für Schäden an Geräten, Datenverlust, Verlust der Garantie oder jede andere Folge der Nutzung von SAJ Local. Die Warnung gilt insbesondere für das Schreiben von Einstellungen in deinen Wechselrichter.

## Danksagungen

Die Unterstützung des H2 baut auf der Registerforschung und den Feldtests von stanus74 in [SAJ H2 Modbus](https://github.com/stanus74/home-assistant-saj-h2-modbus) auf. Danke.
