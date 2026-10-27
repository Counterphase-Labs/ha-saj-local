[en](../../en-gb/user/installation.md) | de | [nl](../../nl/user/installation.md) | [fr](../../fr/user/installation.md) | [zh](../../zh-hans/user/installation.md) | [es](../../es/user/installation.md) | [it](../../it/user/installation.md) | [pl](../../pl/user/installation.md) | [sv](../../sv/user/installation.md)

# Installation

Die Seite Installation installiert SAJ Local mit HACS, dem Home Assistant Community Store. Die vollständige Liste dessen, was die Einrichtung leistet, steht im Abschnitt [Einrichtung und Erkennung](../../../custom_components/saj_local/docs/features.md#setup-and-detection) der Funktionsliste der Integration.

SAJ Local hat noch keine veröffentlichte Version. Prüfe die [unterstützte Ausstattung](supported-equipment.md), bevor du installierst.

## Was du brauchst

- Home Assistant in der Mindestversion, die [`hacs.json`](../../../hacs.json) nennt, und HACS.
- Einen unterstützten SAJ-Wechselrichter, der in deinem lokalen Netzwerk Modbus TCP beantwortet. Du brauchst die Adresse des Wechselrichters sowie den Port und die Unit-ID, wenn Port oder Unit-ID nicht dem Standard entsprechen.
- Sonst nichts. SAJ Local spricht direkt mit dem Wechselrichter und sendet nichts an einen Cloud-Dienst.

## Installieren

1. Öffne SAJ Local in HACS mit der ersten Schaltfläche unten. HACS bittet dich, das Repository hinzuzufügen, wenn das Repository noch nicht aufgeführt ist.
2. Lade SAJ Local in HACS herunter.
3. Starte Home Assistant neu.
4. Füge dein System mit der zweiten Schaltfläche unten hinzu oder folge den [Ersten Schritten](getting-started.md).

[![Öffne deine Home-Assistant-Instanz und öffne das Repository von SAJ Local in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Counterphase-Labs&repository=ha-saj-local&category=integration)
[![Öffne deine Home-Assistant-Instanz und beginne mit der Einrichtung von SAJ Local.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=saj_local)

SAJ Local liefert Dashboard-Karten selbst aus, daher musst du keine Karten-Ressource hinzufügen. Siehe [Dashboard-Karten](cards/README.md).

## Beta-Versionen

Bis zur ersten stabilen Version ist jede Version von SAJ Local eine Beta. Öffne in HACS SAJ Local, öffne das Menü, wähle Erneut herunterladen, schalte „Beta-Versionen anzeigen“ ein und lade die neueste Beta herunter. Ohne den Schalter installiert HACS die Entwicklungsversion von SAJ Local.
