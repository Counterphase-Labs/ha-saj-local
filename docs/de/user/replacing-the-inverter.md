[en](../../en-gb/user/replacing-the-inverter.md) | de | [nl](../../nl/user/replacing-the-inverter.md) | [fr](../../fr/user/replacing-the-inverter.md) | [zh](../../zh-hans/user/replacing-the-inverter.md) | [es](../../es/user/replacing-the-inverter.md) | [it](../../it/user/replacing-the-inverter.md) | [pl](../../pl/user/replacing-the-inverter.md) | [sv](../../sv/user/replacing-the-inverter.md)

# Den Wechselrichter austauschen

Die Seite Den Wechselrichter austauschen erklärt, wie du ein System auf einen neuen Wechselrichter oder zwischen einem H2 und einem HS3 umstellst und dabei das Gerät, die Entitäten und den Verlauf behältst. Die vollständige Liste steht im Abschnitt [Modellwechsel](../../../custom_components/saj_local/docs/features.md#model-replacement) der Funktionsliste der Integration.

## Ein System absichtlich umstellen

1. Stelle sicher, dass der neue Wechselrichter erreichbar ist. Wenn der neue Wechselrichter eine andere Adresse hat, gibst du die Adresse im nächsten Schritt ein.
2. Öffne Konfigurieren, das Zahnrad in der Zeile des Systems auf der Seite der SAJ-Local-Integration.
3. Ändere Host, Port oder Unit-ID, wenn sich die Adresse geändert hat. Lass Modell auf Automatisch oder wähle das Modell, wenn der Wechselrichter nicht erkannt wird.
4. Wähle Absenden und bestätige dann den Austausch. Die Bestätigung nennt das Modell und die Seriennummer, die SAJ Local gefunden hat.

Nachdem du bestätigt hast, bleiben das Gerät, die Entitäten, die Namen der Entitäten und der Verlauf beim System. Eine Entität behält den Verlauf über die Umstellung hinweg, wenn beide Modelle die Entität haben. SAJ Local vergisst die Ausstattung, die am alten Wechselrichter erkannt wurde, und die Anzahl der Batteriepacks des alten Wechselrichters und erkennt die Ausstattung am neuen Wechselrichter neu.

## Wenn sich der Wechselrichter an der Adresse ohne dein Zutun ändert

SAJ Local prüft die Identität des Wechselrichters jedes Mal, wenn das System geladen wird. Wenn sich der Wechselrichter an der Adresse als anderes Modell meldet oder eine andere Seriennummer hat, lädt SAJ Local das System nicht und löst eine Reparaturmeldung aus. Die Behebung der Reparaturmeldung zeigt das Modell und die Seriennummer, die der Wechselrichter jetzt meldet, und übernimmt den Wechselrichter, den du bestätigst.

- Entitäts-IDs, Verlauf, Steuerung zulassen und jede andere Einstellung bleiben unverändert.
- Wenn der Wechselrichter etwas anderes meldet als das, was das Formular gezeigt hat, sagt das Formular das und zeigt die neuen Werte, statt die alten Werte zu speichern.
- Wenn das Gerät an der Adresse kein erkanntes Modell ist, sagt eine Reparaturmeldung das und verweist auf Konfigurieren. Es gibt nichts zu übernehmen. Wähle das Modell von Hand, siehe [Erste Schritte](getting-started.md#wenn-der-wechselrichter-nicht-erkannt-wird).

Die Reparaturmeldungen sind unter [Gerätefehler und Reparaturen](faults-and-repairs.md#reparaturmeldungen) aufgelistet.

## Noch nicht unterstützt

- Einen Wechselrichter übernehmen, der schon zu einem anderen System gehört. SAJ Local lehnt die Übernahme ab.
