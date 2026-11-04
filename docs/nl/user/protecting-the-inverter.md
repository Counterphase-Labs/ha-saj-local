[en](../../en-gb/user/protecting-the-inverter.md) | [de](../../de/user/protecting-the-inverter.md) | nl | [fr](../../fr/user/protecting-the-inverter.md) | [zh](../../zh-hans/user/protecting-the-inverter.md) | [es](../../es/user/protecting-the-inverter.md) | [it](../../it/user/protecting-the-inverter.md) | [pl](../../pl/user/protecting-the-inverter.md) | [sv](../../sv/user/protecting-the-inverter.md)

# De omvormer beschermen

De pagina De omvormer beschermen vermeldt de limieten die SAJ Local aanhoudt voor alles wat SAJ Local verstuurt, zodat de communicatiemodule van de omvormer Home Assistant blijft bedienen. Een module kan stoppen met het bedienen van een client die te hard pollt, dus geen enkele instelling heft een limiet op. De volledige lijst staat in de sectie [De omvormer beschermen](../../../custom_components/saj_local/docs/features.md#protecting-the-inverter) van de functielijst van de integratie.

## De limieten

- **Eén verbinding, één verzoek tegelijk.** SAJ Local opent één verbinding met een omvormer en wacht op elk antwoord voordat het volgende verzoek wordt verstuurd, met een korte pauze tussen verzoeken.
- **40 verzoeken in elke 60 seconden.** De limiet geldt per omvormeradres. SAJ Local telt over herladingen heen, dus een herlading, een nieuwe installatiepoging of een verbindingscontrole kan de limiet niet overschrijden. Een verzoek boven de limiet wacht.
- **Naburige registers delen een verzoek.** SAJ Local leest registers die dicht bij elkaar liggen in één verzoek, nooit voorbij een blok dat het model documenteert. Een verzoek is nooit groter dan 32 registers op de HS3 of 56 op de H2. Entiteiten groeperen die bij elkaar liggen kost minder, zie [polling](polling.md).
- **Geen nieuwe pogingen binnen een cyclus.** Na een mislukte uitlezing verdubbelt de wachttijd voor de volgende poging vanaf het kortste interval, tot 5 minuten. De wachttijd blijft bestaan over herladingen heen. De eerste goede cyclus leest alles opnieuw uit.
- **Elke wachttijd heeft een tijdslimiet.** Een vastgelopen omvormer beëindigt een cyclus als mislukking en stopt de polling niet. Een laat of verdwaald antwoord wordt verworpen.
- **Een gesloten verbinding wordt één keer heropend.** Die cyclus leest dan elke ingeschakelde entiteit opnieuw uit, zodat geen enkele waarde ouder is dan het herverbinden.
- **Twee soorten registerlezingen.** SAJ Local leest houdregisters (Modbus-functie 03) en invoerregisters (functie 04). De HS3 levert de metingen van de EV-lader als invoerregisters. Beide soorten tellen mee voor de 40 verzoeken, en een weigering van de ene soort schort de andere nooit op.
- **Hooguit 20 wijzigingen in 60 seconden.** Zie [instellingen wijzigen](changing-settings.md#wat-er-met-een-wijziging-gebeurt). Een wijziging boven de limiet wordt geweigerd en niet in de wachtrij gezet.

## Wanneer de omvormer een meting weigert

Een weigering is een antwoord en geen mislukking. Alleen de entiteiten in het geweigerde verzoek worden niet beschikbaar, en de andere blijven bijwerken.

1. SAJ Local splitst het geweigerde verzoek in de volgende cycli in tweeën, tot de geweigerde entiteit is gevonden.
2. Een entiteit die drie keer achter elkaar is geweigerd, wordt opgeschort. De entiteit toont als niet beschikbaar en wordt niet meer uitgelezen.
3. SAJ Local probeert een opgeschorte entiteit één keer per dag opnieuw, en telkens wanneer de integratie laadt. De entiteit komt terug wanneer het register antwoordt.
4. Een reparatie vermeldt de opgeschorte entiteiten. De herstelactie van de reparatie schakelt de entiteiten uit, zodat SAJ Local de entiteiten voorgoed niet meer uitleest. Zie [storingen en reparaties](faults-and-repairs.md#reparaties).

## Wanneer de omvormer niet meer antwoordt

Een reparatie meldt wanneer een omvormer 15 minuten niet heeft geantwoord. De reparatie verdwijnt bij de eerste goede meting. Controleer de stroom van de omvormer en van de communicatiemodule, het netwerk, en dat geen andere Modbus-client de verbinding vasthoudt.

## Nog niet ondersteund

- De limieten wijzigen. De limieten beschermen de omvormer, dus geen enkele instelling verhoogt een limiet.
