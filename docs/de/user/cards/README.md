[en](../../../en-gb/user/cards/README.md) | de | [nl](../../../nl/user/cards/README.md) | [fr](../../../fr/user/cards/README.md) | [zh](../../../zh-hans/user/cards/README.md) | [es](../../../es/user/cards/README.md) | [it](../../../it/user/cards/README.md) | [pl](../../../pl/user/cards/README.md) | [sv](../../../sv/user/cards/README.md)

# Dashboard-Karten

Die Seite Dashboard-Karten erklärt, wie du die SAJ-Local-Karten zu einem Dashboard hinzufügst und ein System wählst, und listet auf, was jedes Element zeigt. Die vollständigen Listen stehen in den Abschnitten [Elemente und Einrichtung](../../../../frontend/docs/features.md#elements-and-setup) und [Design und Sprache](../../../../frontend/docs/features.md#theme-and-language) der Funktionsliste der Karten sowie im Abschnitt [Karten](../../../../custom_components/saj_local/docs/features.md#cards) der Funktionsliste der Integration.

SAJ Local liefert die Karten aus und registriert die Karten bei Home Assistant, wenn Home Assistant startet. Die Karten erscheinen in der Kartenauswahl, daher gibt es keine Ressource hinzuzufügen und keinen Cache zu leeren.

## Elemente

| Element | Was das Element zeigt |
| --- | --- |
| [Energiefluss-Karte](power-flow-card.md) | Die Live-Leistung zwischen Solar, Batterie, Netz, Haus und der optionalen Ausstattung. |
| [Status-Karte](status-card.md) | Den Betriebszustand, den Anwendungsmodus, wichtige Messwerte, die Energie von heute, eine Fehlerübersicht und ob die Steuerung zugelassen ist. |
| [Fehler-Karte](faults-card.md) | Die aktiven Fehler jedes Ausstattungsteils und eine Schaltfläche Fehler quittieren. |
| [Batterie-Karte](battery-card.md) | Den Ladezustand mit markierten Grenzen, die Batteriewerte und eine Zeilengruppe für jedes Pack. |
| [Steuerungs-Karte](controls-card.md) | Die Einstellungen des Systems in Abschnitten. |
| [Zeitplan-Karte](schedule-card.md) | Die Zeitfenster für Laden, Entladen und Wallbox, eine Wochenzeitleiste und einen Zeitfenster-Editor. |
| [Wochentage-Funktion für Kachel-Karten](weekdays-feature.md) | Sieben Tagesschaltflächen auf einer Kachel-Karte für die Tage eines Zeitfensters. |
| [Status-Badge](status-badge.md) | Ein Badge mit dem Betriebszustand und der Anzahl der Ausstattungsteile mit einem aktiven Fehler. |

## Ein Element hinzufügen

1. Bearbeite ein Dashboard und wähle Karte hinzufügen. Für die Wochentage-Funktion fügst du eine Kachel-Karte hinzu und öffnest die Funktionen der Kachel-Karte. Für das Badge bearbeitest du die Badges des Dashboards.
2. Wähle das SAJ-Local-Element in der Auswahl. Die sechs Karten zeigen eine Live-Vorschau.
3. Wähle das System im Feld System des visuellen Editors. Eine neue Karte oder ein neues Badge beginnt mit dem ersten System. Die Wochentage-Funktion hat keinen Editor, weil die Funktion die Entität der Kachel-Karte verwendet.

Ein Zuhause mit zwei Systemen fügt eine Karte einmal je System hinzu. Der Titel einer Karte ist der Gerätename des Systems gefolgt vom Modell, zum Beispiel SAJ HS3 (12000 W). SAJ Local fügt die Seriennummer nur hinzu, wenn zwei Systeme sonst einen identischen Titel hätten. Benenne jedes Gerät in Home Assistant um, wenn du andere Titel möchtest.

Die Elemente finden die Entitäten eines Systems über die Entitätsregistrierung und nicht über die Entitäts-ID, daher funktionieren die Elemente weiter, wenn du ein [Präfix](../entities-and-prefix.md#das-präfix) änderst.

## Was jedes Element tut

- **Nur was das System hat.** Ein Teil, dessen Entität nicht existiert oder deaktiviert ist, wird nicht gezeichnet, daher zeigt jede Karte nur, was das System hat. Ein Teil für ein Modell erscheint nur auf diesem Modell, und jede Elementseite nennt die Teile.
- **Eine leere Karte sagt, warum.** Eine Karte, bei der keine der Entitäten der Karte aktiviert ist, sagt, welche Art von Entität du aktivieren musst, mit einem Link zur Geräteseite des Systems.
- **Ein System, das nicht antwortet.** Eine Karte sagt das und blendet die Werte ab.
- **Tippe auf einen Wert.** Das Tippen auf einen Wert öffnet die Details der Entität in Home Assistant.
- **Gesperrte Bedienelemente.** Solange [Steuerung zulassen](../changing-settings.md#steuerung-zulassen) für das System aus ist, ist jedes Bedienelement deaktiviert, und ein Schloss verweist auf die Einstellungen der Integration. Das Einschalten von Steuerung zulassen aktiviert auch die Entitäten, die die Karten brauchen, siehe [den Steuerungssatz](../changing-settings.md#der-steuerungssatz).
- **Eine Änderung pro Entscheidung.** Ein Schieberegler ändert den Wechselrichter, wenn du den Schieberegler loslässt. Ein Zahlenfeld ändert den Wechselrichter mit Enter oder wenn du das Feld verlässt. Eine Liste, ein Schalter oder ein Zeitfeld ändert den Wechselrichter bei der Änderung. Das Bedienelement zeigt dann den Wert, den der Wechselrichter hält, und eine Ablehnung erscheint unter dem Bedienelement in den Worten der Integration.

## Design und Sprache

Die Elemente folgen dem Design von Home Assistant. Entitätsnamen, Werte und Zustände verwenden die Formatierung und die Sprache von Home Assistant. Die Texte der Karten gibt es auf Englisch, Deutsch, Niederländisch, Französisch, Vereinfachtem Chinesisch, Spanisch, Italienisch, Polnisch und Schwedisch. Ein Dashboard in einer anderen Sprache zeigt die Texte der Karten auf Englisch.

## Noch nicht unterstützt

- Kartentexte in anderen Sprachen als den neun oben.
