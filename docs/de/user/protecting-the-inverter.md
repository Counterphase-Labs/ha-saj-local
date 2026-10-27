[en](../../en-gb/user/protecting-the-inverter.md) | de | [nl](../../nl/user/protecting-the-inverter.md) | [fr](../../fr/user/protecting-the-inverter.md) | [zh](../../zh-hans/user/protecting-the-inverter.md) | [es](../../es/user/protecting-the-inverter.md) | [it](../../it/user/protecting-the-inverter.md) | [pl](../../pl/user/protecting-the-inverter.md) | [sv](../../sv/user/protecting-the-inverter.md)

# Den Wechselrichter schützen

Die Seite Den Wechselrichter schützen listet die Grenzen auf, die SAJ Local für alles einhält, was SAJ Local sendet, damit das Kommunikationsmodul des Wechselrichters Home Assistant weiter bedient. Ein Modul kann aufhören, einen Client zu bedienen, der zu stark abfragt, daher entfernt keine Einstellung ein Limit. Die vollständige Liste steht im Abschnitt [Den Wechselrichter schützen](../../../custom_components/saj_local/docs/features.md#protecting-the-inverter) der Funktionsliste der Integration.

## Die Grenzen

- **Eine Verbindung, eine Anfrage nach der anderen.** SAJ Local öffnet eine Verbindung zu einem Wechselrichter und wartet auf jede Antwort, bevor SAJ Local die nächste Anfrage sendet, mit einer kurzen Pause zwischen den Anfragen.
- **40 Anfragen in beliebigen 60 Sekunden.** Das Limit gilt je Wechselrichter-Adresse. SAJ Local zählt über Neuladevorgänge hinweg, daher kann ein Neuladen, ein Wiederholen der Einrichtung oder eine Verbindungsprüfung das Limit nicht überschreiten. Eine Anfrage über dem Limit wartet.
- **Benachbarte Register teilen sich eine Anfrage.** SAJ Local liest Register, die dicht beieinander liegen, in einer Anfrage, nie über einen Block hinaus, den das Modell dokumentiert. Eine Anfrage ist nie größer als 32 Register beim HS3 oder 56 beim H2. Entitäten, die beieinander liegen, zu gruppieren kostet weniger, siehe [Abfrage](polling.md).
- **Keine Wiederholungen innerhalb eines Zyklus.** Nach einem fehlgeschlagenen Lesen verdoppelt sich die Wartezeit vor dem nächsten Versuch, ausgehend vom kürzesten Intervall, bis zu 5 Minuten. Die Wartezeit übersteht Neuladevorgänge. Der erste gute Zyklus liest wieder alles.
- **Jedes Warten hat ein Zeitlimit.** Ein hängender Wechselrichter beendet einen Zyklus als Fehlschlag und stoppt die Abfrage nicht. Eine späte oder verirrte Antwort wird verworfen.
- **Eine geschlossene Verbindung wird einmal wieder geöffnet.** Dieser Zyklus liest dann jede aktivierte Entität erneut, daher ist kein Wert älter als die Wiederverbindung.
- **Höchstens 20 Änderungen in 60 Sekunden.** Siehe [Einstellungen ändern](changing-settings.md#was-mit-einer-änderung-geschieht). Eine Änderung über dem Limit wird abgelehnt und nicht in eine Warteschlange gestellt.

## Wenn der Wechselrichter ein Lesen verweigert

Eine Verweigerung ist eine Antwort und kein Fehlschlag. Nur die Entitäten in der verweigerten Anfrage werden nicht verfügbar, und die anderen werden weiter aktualisiert.

1. SAJ Local halbiert die verweigerte Anfrage über die nächsten Zyklen, bis die verweigerte Entität gefunden ist.
2. Eine Entität, die dreimal hintereinander verweigert wurde, wird ausgesetzt. Die Entität erscheint als nicht verfügbar und wird nicht mehr gelesen.
3. SAJ Local versucht eine ausgesetzte Entität einmal am Tag und bei jedem Laden der Integration erneut. Die Entität kommt zurück, wenn das Register antwortet.
4. Eine Reparaturmeldung listet die ausgesetzten Entitäten auf. Das Beheben der Meldung deaktiviert die Entitäten, sodass SAJ Local die Entitäten dauerhaft nicht mehr liest. Siehe [Gerätefehler und Reparaturen](faults-and-repairs.md#reparaturmeldungen).

## Wenn der Wechselrichter nicht mehr antwortet

Eine Reparaturmeldung sagt, wenn ein Wechselrichter 15 Minuten lang nicht geantwortet hat. Die Meldung verschwindet beim ersten guten Messwert. Prüfe die Stromversorgung des Wechselrichters und des Kommunikationsmoduls, das Netzwerk und ob kein anderer Modbus-Client die Verbindung hält.

## Noch nicht unterstützt

- Die Grenzen ändern. Die Grenzen schützen den Wechselrichter, daher hebt keine Einstellung ein Limit an.
