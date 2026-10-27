[en](../../en-gb/user/supported-equipment.md) | de | [nl](../../nl/user/supported-equipment.md) | [fr](../../fr/user/supported-equipment.md) | [zh](../../zh-hans/user/supported-equipment.md) | [es](../../es/user/supported-equipment.md) | [it](../../it/user/supported-equipment.md) | [pl](../../pl/user/supported-equipment.md) | [sv](../../sv/user/supported-equipment.md)

# Unterstützte Ausstattung

Die Seite Unterstützte Ausstattung listet die SAJ-Produkte auf, die SAJ Local unterstützt, die optionale Ausstattung, die jedes Modell haben kann, und was noch nicht unterstützt wird. Die vollständige Liste dessen, was die Einrichtung leistet, steht im Abschnitt [Einrichtung und Erkennung](../../../custom_components/saj_local/docs/features.md#setup-and-detection) der Funktionsliste der Integration.

## Unterstützte Modelle

SAJ Local erkennt ein Modell am Gerätetyp, den der Wechselrichter meldet. Jeder andere Gerätetyp wird nicht erkannt.

| Modell | Erkannt als | Optionale Ausstattung, die SAJ Local erkennt |
| --- | --- | --- |
| HS3 | Gerätetyp `0x1610`, drei Phasen | Batterie, Zähler A, Zähler B, Wallbox, Parallelsystem |
| H2, einphasig, zwei Solar-Strings | Gerätetyp `0x005a` | Batterie, Zähler A, Zähler B, Parallelsystem |
| H2, einphasig, drei Solar-Strings | Gerätetyp `0x005b` | Batterie, Zähler A, Zähler B, Parallelsystem |

Die Unterschiede zwischen den Modellen, die du im Betrieb siehst:

- **Wallbox:** nur der HS3. Der H2 hat keine Wallbox-Entitäten, keine Wallbox-Zeitfenster und keinen Wallbox-Abschnitt auf der Steuerungs-Karte.
- **Batteriepacks:** Ein H2 hat Entitäten für bis zu fünf Batteriepacks. Ein HS3 hat Entitäten für ein Batteriepack. Siehe [optionale Ausstattung](optional-equipment.md).
- **EMS:** nur der HS3. Siehe [Einstellungen ändern](changing-settings.md#ems).
- **Leistungssteuerung:** Der HS3 bietet Batterie, Netz und Wechselrichter. Der H2 bietet nur Batterie. Siehe [Leistungssteuerung](power-control.md).

[Optionale Ausstattung](optional-equipment.md) erklärt, wie die Erkennung funktioniert und wie du die Erkennung überschreibst. Die [Entitätsreferenz](entities/README.md) listet auf, welches Modell und welche Ausstattung jede Entität braucht.

## Noch nicht unterstützt

- Die automatische Erkennung erkennt nur die drei Gerätetypen in der Tabelle. Andere SAJ-Produkte, etwa der HS2, der H1 und der AS1, werden nicht erkannt.
- Andere H2-Varianten, etwa der dreiphasige H2, melden andere Gerätetypen und werden nicht automatisch erkannt. Du kannst das Modell von Hand wählen, und SAJ Local markiert das Modell dann als ungeprüft. Messwerte können falsch sein, weil SAJ Local die Messwerte nicht prüfen kann. Siehe [Erste Schritte](getting-started.md#wenn-der-wechselrichter-nicht-erkannt-wird).
- Einstellungen ändern bei einem System, dessen Modell ungeprüft ist. Das Lesen funktioniert, und jede Änderung wird abgelehnt.

## Worauf die Unterstützung beruht

Die Unterstützung des HS3 wurde von Hand an einem echten HS3 geprüft. Die Unterstützung des H2 beruht auf der SAJ-Protokolldokumentation und auf Feldberichten und wurde nicht von Hand an einem H2 geprüft. Auch das Schreiben von Einstellungen und die Leistungssteuerung beim H2 beruhen auf Dokumentation und Feldberichten.
