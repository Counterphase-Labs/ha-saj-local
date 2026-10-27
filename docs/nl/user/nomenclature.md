[en](../../en-gb/user/nomenclature.md) | [de](../../de/user/nomenclature.md) | nl | [fr](../../fr/user/nomenclature.md) | [zh](../../zh-hans/user/nomenclature.md) | [es](../../es/user/nomenclature.md) | [it](../../it/user/nomenclature.md) | [pl](../../pl/user/nomenclature.md) | [sv](../../sv/user/nomenclature.md)

# Nomenclatuur

De termen die SAJ Local, de dashboardkaarten en de documentatie gebruiken, elk met een uitleg in één regel. Elke vertaling van de integratie, de kaarten en de documentatie gebruikt voor elk onderdeel in deze lijst één term. In de sectie [Talen](../../../custom_components/saj_local/docs/features.md#languages) van de functielijst van de integratie staan de talen die SAJ Local levert.

## SAJ-apparatuur en metingen

| Term | Betekenis |
| --- | --- |
| Omvormer | De SAJ-eenheid die de gelijkstroom van de zonnepanelen en de batterij omzet in wisselstroom voor het huis en het net. |
| HS3 | Het SAJ HS3-hybride omvormermodel, een driefasig model. |
| H2 | Het SAJ H2-hybride omvormermodel, een eenfasig model. |
| Model | Het omvormertype dat SAJ Local gebruikt om de registerlijst te kiezen: Automatisch, HS3 of H2. |
| Automatisch | De modelkeuze die het model herkent aan het apparaattype dat de omvormer meldt. |
| Optionele apparatuur | Apparatuur die een installatie wel of niet kan hebben: een batterij, Meter A, Meter B, een EV-lader of een parallel systeem. |
| Geïnstalleerd | De instelling die SAJ Local vertelt dat een onderdeel van de optionele apparatuur is geïnstalleerd. |
| Niet geïnstalleerd | De instelling die SAJ Local vertelt dat een onderdeel van de optionele apparatuur niet is geïnstalleerd. |
| Batterij | De energieopslag die op de omvormer is aangesloten. |
| Batterijpack | Eén batterijmodule in een batterij, weergegeven als Pack gevolgd door een nummer. |
| Laadniveau | Hoe vol de batterij is, als percentage. |
| Reserve | De batterijlading die de omvormer achterhoudt en waaronder hij niet ontlaadt. |
| Zon | Het vermogen dat de zonnepanelen opwekken. |
| Zonnestring | Eén groep in serie geschakelde zonnepanelen die op één ingang van de omvormer is aangesloten. |
| Fase | Eén geleider van de wisselstroomvoeding. |
| Net | Het openbare elektriciteitsnet waarop het huis is aangesloten. |
| Afname | Vermogen uit het net halen. |
| Teruglevering | Vermogen aan het net leveren. |
| Opladen | Vermogen in de batterij stoppen. |
| Ontladen | Vermogen uit de batterij halen. |
| Huis | Het vermogen dat het huis verbruikt. |
| Back-upbelasting | De verbruikers die bij een netstoring van stroom blijven voorzien door de batterij en de zonnepanelen. |
| Meter A | De eerste elektriciteitsmeter die op de omvormer kan worden aangesloten. |
| Meter B | De tweede elektriciteitsmeter die op de omvormer kan worden aangesloten. |
| EV-lader | Een oplader voor elektrische voertuigen die op de omvormer is aangesloten. |
| Parallel systeem | Meerdere omvormers die samenwerken als één systeem. |
| Storing | Een probleem dat de apparatuur meldt, met een register en een bit. |
| Storing wissen | De knop die de omvormer vraagt een gemelde storing te wissen. |
| Bedrijfstoestand | De toestand waarin de omvormer zich bevindt, zoals in bedrijf of stand-by. |
| Modus | De bedrijfsmodus van de omvormer, zoals tijdgestuurd. |
| Tijdgestuurd | De modus waarin de batterij oplaadt en ontlaadt in de tijdvakken die u instelt. |
| Tijdvak | Eén periode van het tijdgestuurde schema voor opladen, ontladen of de EV-lader. |
| EMS | De functies voor energiebeheer van de omvormer, die een vermogensdoel van buitenaf aanhouden. |
| EMS-hartslag | Hoe vaak SAJ Local de EMS-doelen uitleest om de EMS-functies actief te houden. |
| EMS-time-out | De tijd waarna de omvormer een EMS-functie beëindigt die niet actief wordt gehouden. |
| Terugstroombeveiliging | De beveiliging van de omvormer tegen vermogen dat terugstroomt naar de omvormer, die de EMS-functies uitschakelen. |
| Vermogensregeling | De batterij, de netaansluiting of de omvormer op een ingesteld vermogen houden. |
| Vermogensdoel | Het vermogen dat een vermogensregelfunctie aanhoudt. |
| Schema | De tijden waarop een vermogensregelfunctie draait. |
| Bediening toestaan | De instelling waarmee Home Assistant de instellingen van de omvormer mag wijzigen. |
| Bediening | Het vermogen om de instellingen van de omvormer te wijzigen, in plaats van hem alleen uit te lezen. |
| Register | Een genummerde geheugenlocatie van de omvormer die één meting of instelling bevat. |
| Geweigerd register | Een register waarop de omvormer niet antwoordt. |
| Modbus TCP | Het netwerkprotocol dat SAJ Local gebruikt om met de omvormer te praten. |
| Host | Het netwerkadres van de omvormer. |
| Poort | De netwerkpoort van de omvormer, standaard 502. |
| Unit-ID | Het Modbus-adres van de omvormer, van 1 tot 247. |
| Communicatiemodule | Het onderdeel van de omvormer dat netwerkverzoeken beantwoordt. |
| Blok | Een bereik van registers dat met één verzoek wordt uitgelezen. |
| Realtime | Het blok metingen dat van seconde tot seconde verandert. |
| Vijfminutengemiddelden | Het blok metingen waarvan de omvormer het gemiddelde over vijf minuten neemt. |
| Energie | Het blok metingen van opgewekte en verbruikte energie, zoals de energie van vandaag. |
| Identiteit | Het model, het serienummer en de versies die de omvormer meldt. |

## SAJ Local-begrippen

| Term | Betekenis |
| --- | --- |
| Systeem | Eén omvormer, met zijn apparatuur, toegevoegd aan Home Assistant. |
| Installatie | Eén SAJ Local-configuratie-item, dat is één systeem. |
| Voorvoegsel | Optionele tekst die aan de entiteits-ID's van één installatie wordt toegevoegd, gebruikt als er meer dan één systeem is. |
| Polling | De omvormer met tussenpozen uitlezen. |
| Pollinggroep | Een gekozen set entiteiten die SAJ Local sneller of langzamer uitleest dan het standaardinterval. |
| Update-interval | De seconden tussen twee uitlezingen van de omvormer, weergegeven als "Seconden tussen updates". |
| Verzoekbelasting | Het aantal verzoeken per minuut dat SAJ Local naar de omvormer stuurt, ten opzichte van de limiet van 40 in 60 seconden. |
| Budget | De limiet voor de verzoekbelasting. |
| Vervanging | Een systeem verplaatsen naar een nieuwe omvormer, of tussen een H2 en een HS3, met behoud van de geschiedenis. |
| Niet geverifieerd | Een model dat met de hand is gekozen en niet aan het apparaattype kon worden getoetst. |
| Diagnosedownload | Het bestand met een privacyveilige momentopname van het systeem voor een foutmelding. |
| Debuglogging | De optie die gedetailleerde logregels schrijft om een probleem te vinden. |
| Dashboardkaart | Een kaart die SAJ Local aan Home Assistant-dashboards toevoegt. |
| Vermogensstroomkaart | De kaart die het live vermogen tussen zon, batterij, net en huis toont. |
| Statuskaart | De kaart die de bedrijfstoestand, de modus, belangrijke metingen en storingen toont. |
| Storingenkaart | De kaart die de actieve storingen opsomt. |
| Batterijkaart | De kaart die de batterijmetingen en één rij per pack toont. |
| Bedieningskaart | De kaart die de gedeelde bediening van het systeem toont. |
| Schemakaart | De kaart die de tijdvakken met een weektijdlijn toont. |
| Weekdagen-tegelkaartfunctie | De zeven dagknoppen die aan een tegelkaart kunnen worden toegevoegd. |
| Statusbadge | De badge die de bedrijfstoestand en het aantal actieve storingen toont. |

## Home Assistant-begrippen

| Term | Betekenis |
| --- | --- |
| Home Assistant | De domoticasoftware waarvan SAJ Local een integratie is. |
| Integratie | Software die een soort apparaat of dienst met Home Assistant verbindt. |
| HACS | De Home Assistant Community Store, gebruikt om SAJ Local te installeren. |
| Aangepaste repository | Een repository die niet in de standaardlijst van HACS staat en via het adres aan HACS wordt toegevoegd; de badge „HACS aangepast” in de README's markeert SAJ Local als zo'n repository. |
| Configuratiestroom | De instelprocedure die een systeem toevoegt. |
| Configuratie-item | De opgeslagen instelling van één systeem. |
| Subitem | Een onderdeel van een configuratie-item dat afzonderlijk wordt toegevoegd en gewijzigd, zoals een pollinggroep of een vermogensschema. |
| Configureren | De knop van een integratie die de opties opent. |
| Apparaten & services | De Home Assistant-instellingenpagina die integraties, apparaten en entiteiten opsomt. |
| Instellingen | De Home Assistant-pagina om Home Assistant te configureren. |
| Apparaat | Het Home Assistant-record van één stuk apparatuur dat entiteiten bevat. Elk systeem is één apparaat. |
| Entiteit | Eén meting, instelling of opdracht die Home Assistant toont. |
| Entiteits-ID | De unieke identificatie van een entiteit, zoals sensor.saj_pv_power. |
| Sensor | Een entiteit die een meting toont. |
| Binaire sensor | Een entiteit die aan of uit is, zoals een storing. |
| Nummer | Een entiteit met een getal dat u kunt wijzigen. |
| Selectie | Een entiteit met één keuze uit een lijst. |
| Schakelaar | Een entiteit die u aan of uit kunt zetten. |
| Tijd | Een entiteit met een tijdstip van de dag. |
| Knop | Een entiteit die een actie uitvoert als erop wordt gedrukt. |
| Standaard ingeschakeld | Of een entiteit aan staat wanneer het systeem wordt toegevoegd. |
| Uitgeschakeld | Een entiteit die Home Assistant niet uitleest of toont. |
| Reparatie | Een melding in Home Assistant dat uw actie nodig is, met een knop Herstellen. |
| Dashboard | Een Home Assistant-scherm opgebouwd uit kaarten. |
| Kaart | Eén blok op een dashboard. |
| Tegelkaart | Een Home Assistant-kaart die één entiteit toont en waaraan functies kunnen worden toegevoegd. |
| Badge | Een klein item in de badgerij bovenaan een dashboard. |
| Automatisering | Een regel waarmee Home Assistant handelt wanneer er iets gebeurt. |
| Helper | Een Home Assistant-entiteit die u zelf aanmaakt, zoals een schemahelper. |
| Gebied | Een kamer of plaats waarin apparaten worden gegroepeerd. |
| Thema | De kleuren van de Home Assistant-interface. |
| Taal | De taal die een Home Assistant-gebruiker kiest op de profielpagina. |
| Herladen | Eén integratie herstarten zonder Home Assistant te herstarten. |
| Herstarten | Home Assistant herstarten. |
| Ontwikkelaarstools | De Home Assistant-pagina's om statussen te controleren en acties aan te roepen. |
| Logboek | Het Home Assistant-overzicht van meldingen. |
