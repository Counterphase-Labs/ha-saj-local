[en](../../en-gb/user/nomenclature.md) | de | [nl](../../nl/user/nomenclature.md) | [fr](../../fr/user/nomenclature.md) | [zh](../../zh-hans/user/nomenclature.md) | [es](../../es/user/nomenclature.md) | [it](../../it/user/nomenclature.md) | [pl](../../pl/user/nomenclature.md) | [sv](../../sv/user/nomenclature.md)

# Begriffe

Die Begriffe, die SAJ Local, die Dashboard-Karten und die Dokumentation verwenden, jeweils mit einer Bedeutung in einem Satz. Jede Übersetzung der Integration, der Karten und der Dokumentation verwendet für jede hier aufgeführte Sache genau einen Begriff. Der Abschnitt [Sprachen](../../../custom_components/saj_local/docs/features.md#languages) der Funktionsliste der Integration nennt die Sprachen, in denen SAJ Local erscheint.

## SAJ-Geräte und Messwerte

| Begriff | Bedeutung |
| --- | --- |
| Wechselrichter | Das SAJ-Gerät, das den Gleichstrom von Solarmodulen und Batterie in Wechselstrom für das Haus und das Netz umwandelt. |
| HS3 | Das SAJ-Hybrid-Wechselrichtermodell HS3, ein dreiphasiges Modell. |
| H2 | Das SAJ-Hybrid-Wechselrichtermodell H2, ein einphasiges Modell. |
| Modell | Der Wechselrichtertyp, mit dem SAJ Local die Registerliste auswählt: Automatisch, HS3 oder H2. |
| Automatisch | Die Modellauswahl, die das Modell anhand des vom Wechselrichter gemeldeten Gerätetyps erkennt. |
| Optionale Ausstattung | Ausstattung, die eine Anlage haben kann oder nicht: eine Batterie, Zähler A, Zähler B, eine Wallbox oder ein Parallelsystem. |
| Vorhanden | Die Einstellung, die SAJ Local mitteilt, dass ein Teil der optionalen Ausstattung installiert ist. |
| Nicht vorhanden | Die Einstellung, die SAJ Local mitteilt, dass ein Teil der optionalen Ausstattung nicht installiert ist. |
| Batterie | Der am Wechselrichter angeschlossene Energiespeicher. |
| Batteriepack | Ein Batteriemodul einer Batterie, angezeigt als Pack gefolgt von einer Nummer. |
| Ladezustand | Wie voll die Batterie ist, in Prozent. |
| Reserve | Die Batterieladung, die der Wechselrichter zurückhält und nicht unterschreitet. |
| Solar | Die Leistung, die die Solarmodule erzeugen. |
| Solar-String | Eine Gruppe in Reihe geschalteter Solarmodule, die an einen Eingang des Wechselrichters angeschlossen ist. |
| Phase | Ein Leiter der Wechselstromversorgung. |
| Netz | Das öffentliche Stromnetz, an das das Haus angeschlossen ist. |
| Netzbezug | Leistung aus dem Netz beziehen. |
| Einspeisung | Leistung in das Netz abgeben. |
| Laden | Leistung in die Batterie speisen. |
| Entladen | Leistung aus der Batterie entnehmen. |
| Haus | Die Leistung, die das Haus verbraucht. |
| Notstromlast | Die Verbraucher, die bei einem Netzausfall weiter aus der Batterie und den Solarmodulen versorgt werden. |
| Zähler A | Der erste Stromzähler, der an den Wechselrichter angeschlossen werden kann. |
| Zähler B | Der zweite Stromzähler, der an den Wechselrichter angeschlossen werden kann. |
| Wallbox | Eine Ladestation für Elektrofahrzeuge, die an den Wechselrichter angeschlossen ist. |
| Parallelsystem | Mehrere Wechselrichter, die als ein System zusammenarbeiten. |
| Fehler | Ein Problem, das das Gerät meldet, mit einem Register und einem Bit. |
| Fehler quittieren | Die Schaltfläche, die den Wechselrichter auffordert, einen gemeldeten Fehler zu quittieren. |
| Betriebszustand | Der Zustand, in dem sich der Wechselrichter befindet, etwa Betrieb oder Standby. |
| Modus | Die Betriebsart des Wechselrichters, etwa Zeitsteuerung. |
| Zeitsteuerung | Der Modus, in dem die Batterie in den von dir festgelegten Zeitfenstern lädt und entlädt. |
| Zeitfenster | Ein Zeitraum des Zeitplans der Zeitsteuerung für Laden, Entladen oder die Wallbox. |
| EMS | Die Energiemanagementsystem-Funktionen des Wechselrichters, die ein von außen vorgegebenes Leistungsziel halten. |
| EMS-Heartbeat | Wie oft SAJ Local die EMS-Ziele liest, um die EMS-Funktionen aktiv zu halten. |
| EMS-Timeout | Die Zeit, nach der der Wechselrichter eine EMS-Funktion beendet, die nicht aktiv gehalten wird. |
| Rückstromschutz | Der Schutz des Wechselrichters vor Leistung, die in den Wechselrichter zurückfließt und den die EMS-Funktionen abschalten. |
| Leistungssteuerung | Die Batterie, den Netzanschluss oder den Wechselrichter auf einer festen Leistung halten. |
| Leistungsziel | Die Leistung, die eine Funktion der Leistungssteuerung hält. |
| Zeitplan | Die Zeiten, zu denen eine Funktion der Leistungssteuerung läuft. |
| Steuerung zulassen | Die Einstellung, die Home Assistant erlaubt, die Einstellungen des Wechselrichters zu ändern. |
| Steuerung | Die Möglichkeit, die Einstellungen des Wechselrichters zu ändern, im Gegensatz zum bloßen Lesen. |
| Register | Eine nummerierte Speicherstelle des Wechselrichters, die einen Messwert oder eine Einstellung enthält. |
| Verweigertes Register | Ein Register, auf das der Wechselrichter nicht antwortet. |
| Modbus TCP | Das Netzwerkprotokoll, mit dem SAJ Local mit dem Wechselrichter spricht. |
| Host | Die Netzwerkadresse des Wechselrichters. |
| Port | Der Netzwerkport des Wechselrichters, standardmäßig 502. |
| Unit-ID | Die Modbus-Adresse des Wechselrichters, von 1 bis 247. |
| Kommunikationsmodul | Der Teil des Wechselrichters, der Netzwerkanfragen beantwortet. |
| Block | Ein Registerbereich, der mit einer einzigen Anfrage gelesen wird. |
| Echtzeit | Der Block der Messwerte, die sich von Sekunde zu Sekunde ändern. |
| Fünf-Minuten-Mittelwerte | Der Block der Messwerte, die der Wechselrichter über fünf Minuten mittelt. |
| Energie | Der Block der Messwerte zu erzeugter und verbrauchter Energie, etwa die Energie von heute. |
| Identität | Das Modell, die Seriennummer und die Versionen, die der Wechselrichter meldet. |

## Konzepte von SAJ Local

| Begriff | Bedeutung |
| --- | --- |
| System | Ein Wechselrichter mit seiner Ausstattung, der zu Home Assistant hinzugefügt wurde. |
| Installation | Ein Konfigurationseintrag von SAJ Local, das heißt ein System. |
| Präfix | Optionaler Text, der den Entitäts-IDs einer Installation hinzugefügt wird, wenn es mehr als ein System gibt. |
| Abfrage | Den Wechselrichter in Abständen auslesen. |
| Abfragegruppe | Eine gewählte Menge von Entitäten, die SAJ Local schneller oder langsamer als im Standardintervall liest. |
| Aktualisierungsintervall | Die Sekunden zwischen zwei Lesevorgängen des Wechselrichters, angezeigt als „Sekunden zwischen Aktualisierungen“. |
| Anfragelast | Die Anzahl der Anfragen pro Minute, die SAJ Local an den Wechselrichter sendet, gegenüber dem Limit von 40 in 60 Sekunden. |
| Budget | Das Limit für die Anfragelast. |
| Modellwechsel | Ein System auf einen neuen Wechselrichter oder zwischen einem H2 und einem HS3 umstellen und den Verlauf behalten. |
| Ungeprüft | Ein Modell, das von Hand gewählt wurde und nicht anhand des Gerätetyps geprüft werden konnte. |
| Diagnosedownload | Die Datei mit einem datenschutzfreundlichen Abbild des Systems für einen Fehlerbericht. |
| Debug-Protokollierung | Die Option, die ausführliche Protokollzeilen zur Fehlersuche schreibt. |
| Dashboard-Karte | Eine Karte, die SAJ Local zu den Home-Assistant-Dashboards hinzufügt. |
| Energiefluss-Karte | Die Karte, die den Live-Leistungsfluss zwischen Solar, Batterie, Netz und Haus zeigt. |
| Status-Karte | Die Karte, die den Betriebszustand, den Modus, wichtige Messwerte und Fehler zeigt. |
| Fehler-Karte | Die Karte, die die aktiven Fehler auflistet. |
| Batterie-Karte | Die Karte, die die Batteriewerte und eine Zeile pro Pack zeigt. |
| Steuerungs-Karte | Die Karte, die die gemeinsamen Bedienelemente des Systems zeigt. |
| Zeitplan-Karte | Die Karte, die die Zeitfenster mit einer Wochenzeitleiste zeigt. |
| Wochentage-Funktion für Kachel-Karten | Die sieben Tagesschaltflächen, die zu einer Kachel-Karte hinzugefügt werden können. |
| Status-Badge | Das Badge, das den Betriebszustand und die Anzahl der aktiven Fehler zeigt. |

## Home-Assistant-Konzepte

| Begriff | Bedeutung |
| --- | --- |
| Home Assistant | Die Hausautomations-Software, zu der SAJ Local als Integration gehört. |
| Integration | Software, die eine Art von Gerät oder Dienst mit Home Assistant verbindet. |
| HACS | Der Home Assistant Community Store, über den SAJ Local installiert wird. |
| Benutzerdefiniertes Repository | Ein Repository, das nicht in der Standardliste von HACS steht und über seine Adresse zu HACS hinzugefügt wird; das Badge „HACS Benutzerdefiniert“ in den READMEs kennzeichnet SAJ Local als ein solches. |
| Einrichtungsablauf | Der Einrichtungsdialog, der ein System hinzufügt. |
| Konfigurationseintrag | Die gespeicherte Einrichtung eines Systems. |
| Untereintrag | Ein Teil eines Konfigurationseintrags, der für sich hinzugefügt und geändert wird, etwa eine Abfragegruppe oder ein Leistungszeitplan. |
| Konfigurieren | Die Schaltfläche einer Integration, die ihre Optionen öffnet. |
| Geräte & Dienste | Die Einstellungsseite von Home Assistant, die Integrationen, Geräte und Entitäten auflistet. |
| Einstellungen | Die Seite von Home Assistant zum Konfigurieren von Home Assistant. |
| Gerät | Der Eintrag in Home Assistant für ein Stück Ausstattung, das Entitäten enthält. Jedes System ist ein Gerät. |
| Entität | Ein Messwert, eine Einstellung oder ein Befehl, den Home Assistant anzeigt. |
| Entitäts-ID | Die eindeutige Kennung einer Entität, etwa sensor.saj_pv_power. |
| Sensor | Eine Entität, die einen Messwert zeigt. |
| Binärsensor | Eine Entität, die entweder an oder aus ist, etwa ein Fehler. |
| Zahl | Eine Entität, die eine veränderbare Zahl enthält. |
| Auswahl | Eine Entität, die eine Wahl aus einer Liste enthält. |
| Schalter | Eine Entität, die du ein- oder ausschalten kannst. |
| Zeit | Eine Entität, die eine Tageszeit enthält. |
| Schaltfläche | Eine Entität, die beim Drücken eine Aktion ausführt. |
| Standardmäßig aktiviert | Ob eine Entität eingeschaltet ist, wenn das System hinzugefügt wird. |
| Deaktiviert | Eine Entität, die Home Assistant nicht liest oder anzeigt. |
| Reparaturmeldung | Ein Hinweis in Home Assistant, dass etwas deine Handlung braucht, mit einer Schaltfläche „Beheben“. |
| Dashboard | Eine Home-Assistant-Oberfläche aus Karten. |
| Karte | Ein Block auf einem Dashboard. |
| Kachel-Karte | Eine Home-Assistant-Karte, die eine Entität zeigt und der Funktionen hinzugefügt werden können. |
| Badge | Ein kleines Element in der Badge-Zeile am oberen Rand eines Dashboards. |
| Automatisierung | Eine Regel, nach der Home Assistant handelt, wenn etwas geschieht. |
| Helfer | Eine Entität in Home Assistant, die du selbst erstellst, etwa ein Zeitplan-Helfer. |
| Bereich | Ein Raum oder Ort, in dem Geräte gruppiert werden. |
| Design | Die Farben der Home-Assistant-Oberfläche. |
| Sprache | Die Sprache, die ein Home-Assistant-Benutzer auf der Profilseite wählt. |
| Neu laden | Eine Integration neu starten, ohne Home Assistant neu zu starten. |
| Neustart | Home Assistant neu starten. |
| Entwicklerwerkzeuge | Die Home-Assistant-Seiten zum Prüfen von Zuständen und zum Aufrufen von Aktionen. |
| Protokoll | Die Aufzeichnung der Meldungen von Home Assistant. |
