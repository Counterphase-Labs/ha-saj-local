[en](../../../en-gb/user/entities/README.md) | de | [nl](../../../nl/user/entities/README.md) | [fr](../../../fr/user/entities/README.md) | [zh](../../../zh-hans/user/entities/README.md) | [es](../../../es/user/entities/README.md) | [it](../../../it/user/entities/README.md) | [pl](../../../pl/user/entities/README.md) | [sv](../../../sv/user/entities/README.md)

# Entitäten

Jede Entität, die SAJ Local erstellen kann, eine Seite je Bereich. Der Abschnitt [Geräte und Entitäten](../../../../custom_components/saj_local/docs/features.md#devices-and-entities) der Funktionsliste der Integration erklärt die Entitätstypen, welche Entitäten standardmäßig aktiviert sind und das Vorzeichen der Leistungswerte.

Ein System erhält nur die Entitäten, die zu seinem Modell, seiner vorhandenen Ausstattung und seiner Anzahl an Phasen, Solar-Strings und Batteriepacks passen. Die Spalte Modelle nennt, welche Modelle eine Entität haben, und die Spalte Ausstattung und Anzahl nennt, was vorhanden sein muss.

Erzeugt von `make docs`. Nicht von Hand bearbeiten.

| Bereich | Entitäten | Was sie enthält |
| --- | --- | --- |
| [Wechselrichter und PV](inverter-and-pv.md) | 241 | Wechselrichterleistung, Solar-Strings, Notstromanschluss, Energiezähler, Versionen und die Hauslast |
| [Netz und Zähler A](grid-and-meter-a.md) | 88 | Der Netzanschluss und Zähler A, der Netzzähler |
| [Zähler B](meter-b.md) | 22 | Zähler B, der zweite Zähler, der einen Solar-Wechselrichter misst |
| [Batterie](battery.md) | 133 | Die Batterie als Ganzes |
| [Batteriepacks](battery-packs.md) | 58 | Messwerte und Identität jedes Batteriepacks |
| [Wallbox](ev-charger.md) | 87 | Die Wallbox und ihre Ladesteuerung |
| [Parallelsystem](parallel-system.md) | 63 | Die Messwerte eines Parallelsystems |
| [Einstellungen](settings.md) | 22 | Einstellungen und Befehle, die den Wechselrichter ändern |
| [Fehler](faults.md) | 139 | Fehler, die der Wechselrichter, die Batterie und die Wallbox melden |
| [Von der Integration hinzugefügt](added-by-the-integration.md) | 7 | Entitäten, die die Integration außerhalb des Registerkatalogs hinzufügt |
