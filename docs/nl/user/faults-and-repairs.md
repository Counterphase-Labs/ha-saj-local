[en](../../en-gb/user/faults-and-repairs.md) | [de](../../de/user/faults-and-repairs.md) | nl | [fr](../../fr/user/faults-and-repairs.md) | [zh](../../zh-hans/user/faults-and-repairs.md) | [es](../../es/user/faults-and-repairs.md) | [it](../../it/user/faults-and-repairs.md) | [pl](../../pl/user/faults-and-repairs.md) | [sv](../../sv/user/faults-and-repairs.md)

# Apparaatstoringen en reparaties

De pagina Apparaatstoringen en reparaties legt uit hoe SAJ Local de storingen toont die de omvormer, de batterij en de EV-lader melden, en welke reparaties SAJ Local in Home Assistant aanmaakt. De volledige lijst van het storingsgedrag staat in de sectie [Apparaatstoringen en reparaties](../../../custom_components/saj_local/docs/features.md#device-faults-and-repairs) van de functielijst van de integratie. Elke storingsentiteit staat in de [storingsentiteiten](entities/faults.md) van het entiteitenoverzicht.

Apparaatstoringen en reparaties staan los van elkaar. Een apparaatstoring is een entiteit die meldt wat de apparatuur zegt. Een reparatie is een probleem met de verbinding van SAJ Local met de apparatuur of met de instelling van SAJ Local, en Home Assistant toont de reparatie onder Instellingen en Reparaties.

## Apparaatstoringen

Elke benoemde storing van de omvormer, de batterij en de EV-lader is een binaire sensor met de apparaatklasse probleem, standaard ingeschakeld. Een storing heeft geschiedenis en kan een automatisering starten.

- **Samenvatting:** de omvormer, de batterij en de EV-lader hebben elk een samenvattende storing, bijvoorbeeld Omvormerstoring, die aan staat wanneer de apparatuur iets meldt.
- **Niet herkend:** elk onderdeel van de apparatuur heeft ook een niet-herkende storing die aan staat wanneer de omvormer een bit zet zonder gedocumenteerde betekenis. De [diagnosedownload](troubleshooting.md#diagnose-downloaden) vermeldt het register en het bit, zodat u het bit kunt melden.
- **Eén entiteits-ID op elk model:** een storing heeft één entiteits-ID op elk model dat de storing meldt. Een storing die een model niet meldt, heeft op dat model geen entiteit.
- **Batterijpacks:** elk batterijpack heeft een storings- en een waarschuwingsentiteit. Een HS3 heeft één pack. Een H2 heeft er maximaal vier.
- **Apparatuur die niet is geïnstalleerd:** batterijstoringen bestaan alleen wanneer een batterij is geïnstalleerd, en EV-laderstoringen alleen wanneer een EV-lader is geïnstalleerd. Zie [optionele apparatuur](optional-equipment.md).
- **Een storingsregister dat niet kan worden gelezen:** de storingen die van het register afhangen, zijn niet beschikbaar. SAJ Local gokt niet.
- **Het logboek:** een storing die aangaat, logt één waarschuwing die het systeem en de storing noemt. Wanneer de storing verdwijnt, logt SAJ Local één informatieregel.

De [storingenkaart](cards/faults-card.md) toont de actieve storingen van een systeem op een dashboard, met hoe lang geleden elke storing begon. De knop Storing wissen van de kaart verstuurt de opdracht Huidige storing wissen, waarvoor [Bediening toestaan](changing-settings.md#bediening-toestaan) nodig is.

## Reparaties

SAJ Local maakt een reparatie aan voor een situatie waar u iets aan kunt doen.

| Reparatie | Aangemaakt wanneer | Wat u kunt doen |
| --- | --- | --- |
| Het systeem is op het verkeerde model ingesteld | De omvormer op het adres identificeert zich als een ander model dan het gekozen model. | Een herstelactie neemt het model over dat SAJ Local vond. Zie [de omvormer vervangen](replacing-the-inverter.md). |
| Het systeem bereikt nu een andere omvormer | De omvormer op het adres heeft een ander serienummer. | Een herstelactie neemt de nieuwe omvormer over. Zie [de omvormer vervangen](replacing-the-inverter.md). |
| Het systeem bereikt een niet-herkend apparaat | Het apparaattype is geen herkend model. | Kies het model in Configureren. SAJ Local gebruikt het model dan niet geverifieerd. |
| Het systeem heeft metingen die de omvormer weigert | De omvormer weigerde de metingen drie keer achter elkaar. | Een herstelactie schakelt de vermelde entiteiten uit, zodat SAJ Local de entiteiten niet meer uitleest. Zie [de omvormer beschermen](protecting-the-inverter.md#wanneer-de-omvormer-een-meting-weigert). |
| Het systeem antwoordt niet meer | De omvormer heeft 15 minuten niet geantwoord. | Controleer de stroom, het netwerk en andere Modbus-clients. De reparatie verdwijnt bij de eerste goede meting. |
| Apparatuur wordt niet meer gedetecteerd | Apparatuur die SAJ Local eerder detecteerde, wordt niet meer gedetecteerd. | Controleer de apparatuur, of stel de apparatuur in Configureren in op Niet geïnstalleerd. Zie [optionele apparatuur](optional-equipment.md#wanneer-onthouden-apparatuur-niet-meer-wordt-gedetecteerd). |

![Een reparatie in Home Assistant die zegt dat SAJ HS3MOCK000000000003 metingen heeft die de omvormer weigert](../../images/nl/faults-and-repairs-repair-issue.png)

De eerste drie reparaties zijn de modelreparaties. Er is voor een systeem maar één modelreparatie tegelijk open, en de reparatie dat het systeem niet meer antwoordt wordt niet aangemaakt zolang een modelreparatie open is.

Een reparatie verdwijnt wanneer de situatie van de reparatie eindigt, of wanneer u het systeem verwijdert. De reparatie over geweigerde metingen verdwijnt ook wanneer u een vermelde entiteit uitschakelt.

## Nog niet ondersteund

- Een reparatie voor een apparaatstoring. Apparaatstoringen zijn entiteiten, en de integratie maakt voor een storing geen reparatie aan.
