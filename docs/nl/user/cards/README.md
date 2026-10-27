[en](../../../en-gb/user/cards/README.md) | [de](../../../de/user/cards/README.md) | nl | [fr](../../../fr/user/cards/README.md) | [zh](../../../zh-hans/user/cards/README.md) | [es](../../../es/user/cards/README.md) | [it](../../../it/user/cards/README.md) | [pl](../../../pl/user/cards/README.md) | [sv](../../../sv/user/cards/README.md)

# Dashboardkaarten

De pagina Dashboardkaarten legt uit hoe u de SAJ Local-kaarten aan een dashboard toevoegt en een systeem kiest, en vermeldt wat elk element toont. De volledige lijsten staan in de secties [Elementen en installatie](../../../../frontend/docs/features.md#elements-and-setup) en [Thema en taal](../../../../frontend/docs/features.md#theme-and-language) van de functielijst van de kaarten, en in de sectie [Kaarten](../../../../custom_components/saj_local/docs/features.md#cards) van de functielijst van de integratie.

SAJ Local levert de kaarten en registreert de kaarten bij Home Assistant wanneer Home Assistant start. De kaarten verschijnen in de kaartkiezer, dus er is geen resource toe te voegen en geen cache te wissen.

## Elementen

| Element | Wat het element toont |
| --- | --- |
| [Vermogensstroomkaart](power-flow-card.md) | Live vermogen tussen zon, batterij, net, huis en de optionele apparatuur. |
| [Statuskaart](status-card.md) | De bedrijfstoestand, de toepassingsmodus, belangrijke metingen, de energie van vandaag, een storingsoverzicht en of bediening is toegestaan. |
| [Storingenkaart](faults-card.md) | De actieve storingen van elk onderdeel van de apparatuur, en een knop Storing wissen. |
| [Batterijkaart](battery-card.md) | Het laadniveau met de limieten gemarkeerd, de batterijmetingen en één rijgroep per pack. |
| [Bedieningskaart](controls-card.md) | De instellingen van het systeem in secties. |
| [Schemakaart](schedule-card.md) | De oplaad-, ontlaad- en EV-laadtijdvakken, een weektijdlijn en een tijdvakeditor. |
| [Weekdagen-tegelkaartfunctie](weekdays-feature.md) | Zeven dagknoppen op een tegelkaart, voor de dagen van een tijdvak. |
| [Statusbadge](status-badge.md) | Een badge met de bedrijfstoestand en het aantal onderdelen van de apparatuur met een actieve storing. |

## Een element toevoegen

1. Bewerk een dashboard en kies Kaart toevoegen. Voeg voor de weekdagenfunctie een tegelkaart toe en open de functies van de tegelkaart. Bewerk voor de badge de badges van het dashboard.
2. Kies het SAJ Local-element in de kiezer. De zes kaarten tonen een live voorbeeld.
3. Kies het systeem in het veld Systeem van de visuele editor. Een nieuwe kaart of badge begint met het eerste systeem. De weekdagenfunctie heeft geen editor, omdat de functie de entiteit van de tegelkaart gebruikt.

Een huis met twee systemen voegt een kaart één keer per systeem toe. De titel van een kaart is de apparaatnaam van het systeem gevolgd door het model, bijvoorbeeld SAJ HS3 (12000 W). SAJ Local voegt het serienummer alleen toe wanneer twee systemen anders een identieke titel zouden hebben. Hernoem elk apparaat in Home Assistant als u andere titels wilt.

De elementen vinden de entiteiten van een systeem via het entiteitenregister, en niet via de entiteits-ID, zodat de elementen blijven werken wanneer u een [voorvoegsel](../entities-and-prefix.md#het-voorvoegsel) wijzigt.

## Wat elk element doet

- **Alleen wat het systeem heeft.** Een onderdeel waarvan de entiteit niet bestaat of is uitgeschakeld, wordt niet getekend, dus elke kaart toont alleen wat het systeem heeft. Een onderdeel voor één model verschijnt alleen op dat model, en elke elementpagina noemt de onderdelen.
- **Een lege kaart zegt waarom.** Een kaart waarvan geen van de entiteiten is ingeschakeld, zegt welk soort entiteit u moet inschakelen, met een link naar de apparaatpagina van het systeem.
- **Een systeem dat niet antwoordt.** Een kaart zegt dat en dimt de waarden.
- **Tik op een waarde.** Tikken op een waarde opent de details van de entiteit in Home Assistant.
- **Vergrendelde bediening.** Zolang [Bediening toestaan](../changing-settings.md#bediening-toestaan) uit staat voor het systeem, is elke bediening uitgeschakeld en verwijst een slot naar de instellingen van de integratie. Bediening toestaan inschakelen schakelt ook de entiteiten in die de kaarten nodig hebben, zie [de bedieningsset](../changing-settings.md#de-bedieningsset).
- **Eén wijziging per beslissing.** Een schuifregelaar wijzigt de omvormer wanneer u de schuifregelaar loslaat. Een getalveld wijzigt de omvormer bij Enter of wanneer u het veld verlaat. Een lijst, een schakelaar of een tijdveld wijzigt de omvormer bij de wijziging. De bediening toont daarna de waarde die de omvormer bevat, en een weigering verschijnt onder de bediening in de woorden van de integratie.

## Thema en taal

De elementen volgen het Home Assistant-thema. Entiteitsnamen, waarden en statussen gebruiken de opmaak en de taal van Home Assistant. De teksten van de kaarten bestaan in het Engels, Duits, Nederlands, Frans, vereenvoudigd Chinees, Spaans, Italiaans, Pools en Zweeds. Een dashboard in een andere taal toont de teksten van de kaarten in het Engels.

## Nog niet ondersteund

- Kaartteksten in andere talen dan de negen hierboven.
