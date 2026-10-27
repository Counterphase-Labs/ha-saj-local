[en](../../en-gb/user/replacing-the-inverter.md) | [de](../../de/user/replacing-the-inverter.md) | nl | [fr](../../fr/user/replacing-the-inverter.md) | [zh](../../zh-hans/user/replacing-the-inverter.md) | [es](../../es/user/replacing-the-inverter.md) | [it](../../it/user/replacing-the-inverter.md) | [pl](../../pl/user/replacing-the-inverter.md) | [sv](../../sv/user/replacing-the-inverter.md)

# De omvormer vervangen

De pagina De omvormer vervangen legt uit hoe u een systeem naar een nieuwe omvormer verplaatst, of tussen een H2 en een HS3, en het apparaat, de entiteiten en de geschiedenis behoudt. De volledige lijst staat in de sectie [Modelvervanging](../../../custom_components/saj_local/docs/features.md#model-replacement) van de functielijst van de integratie.

## Een systeem bewust verplaatsen

1. Zorg dat de nieuwe omvormer bereikbaar is. Als de nieuwe omvormer een ander adres heeft, voert u het adres in de volgende stap in.
2. Open Configureren, het tandwiel op de rij van het systeem op de integratiepagina van SAJ Local.
3. Wijzig de host, de poort of het unit-ID als het adres is gewijzigd. Laat Model op Automatisch staan, of kies het model als de omvormer niet wordt herkend.
4. Kies Verzenden en bevestig dan de vervanging. De bevestiging noemt het model en het serienummer die SAJ Local vond.

Nadat u bevestigt, blijven het apparaat, de entiteiten, de namen van de entiteiten en de geschiedenis bij het systeem. Een entiteit behoudt de geschiedenis over de verplaatsing wanneer beide modellen de entiteit hebben. SAJ Local vergeet de apparatuur die op de oude omvormer is gedetecteerd en het aantal batterijpacks van de oude omvormer, en detecteert de apparatuur opnieuw op de nieuwe omvormer.

## Wanneer de omvormer op het adres zonder uw toedoen verandert

SAJ Local controleert de identiteit van de omvormer elke keer dat het systeem laadt. Wanneer de omvormer op het adres zich als een ander model identificeert, of een ander serienummer heeft, laadt SAJ Local het systeem niet en maakt een reparatie aan. De herstelactie van de reparatie toont het model en het serienummer die de omvormer nu meldt, en neemt de omvormer over die u bevestigt.

- Entiteits-ID's, geschiedenis, Bediening toestaan en elke andere instelling blijven ongewijzigd.
- Wanneer de omvormer iets anders meldt dan wat het formulier toonde, zegt het formulier dat en toont het de nieuwe waarden in plaats van de oude waarden op te slaan.
- Wanneer het apparaat op het adres geen herkend model is, zegt een reparatie dat en verwijst naar Configureren. Er is niets over te nemen. Kies het model met de hand, zie [aan de slag](getting-started.md#wanneer-de-omvormer-niet-wordt-herkend).

De reparaties staan vermeld in [storingen en reparaties](faults-and-repairs.md#reparaties).

## Nog niet ondersteund

- Een omvormer overnemen die al bij een ander systeem hoort. SAJ Local weigert de overname.
