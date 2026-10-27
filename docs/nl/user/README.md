[en](../../en-gb/user/README.md) | [de](../../de/user/README.md) | nl | [fr](../../fr/user/README.md) | [zh](../../zh-hans/user/README.md) | [es](../../es/user/README.md) | [it](../../it/user/README.md) | [pl](../../pl/user/README.md) | [sv](../../sv/user/README.md)

# SAJ Local gebruikersdocumentatie

SAJ Local is een lokale Home Assistant-integratie. SAJ Local leest een SAJ HS3- of H2-zonnesysteem rechtstreeks uit de omvormer via Modbus TCP op uw eigen netwerk en wijzigt, wanneer u bediening toestaat, de instellingen van de omvormer vanuit Home Assistant. SAJ Local heeft geen cloudaccount nodig en beperkt de verzoeken aan de omvormer, zodat de communicatiemodule van de omvormer blijft werken.

SAJ Local is een onofficiële, door de community gebouwde integratie. SAJ maakt, ondersteunt of onderschrijft SAJ Local niet. Zie de [disclaimer](#disclaimer).

SAJ Local is in ontwikkeling en heeft nog geen gepubliceerde release. Elke pagina hieronder vermeldt wat nog niet wordt ondersteund. De documentatie behandelt de HS3 en de H2 en markeert de verschillen met een opmerking zoals "Alleen HS3". De schermafbeeldingen komen van gesimuleerde systemen, dus de metingen zijn niet echt.

## Begin hier

1. [Installeer SAJ Local](installation.md) met HACS.
2. Controleer of uw omvormer in de [ondersteunde apparatuur](supported-equipment.md) staat.
3. [Aan de slag](getting-started.md): voeg uw eerste systeem toe.
4. Lees over [optionele apparatuur](optional-equipment.md), die SAJ Local voor u detecteert.

## Uw systeem begrijpen

- [Entiteiten en het voorvoegsel](entities-and-prefix.md): wat de entiteiten zijn, hoe de entiteits-ID's worden opgebouwd en hoe u een voorvoegsel toevoegt.
- [Entiteitenoverzicht](entities/README.md): elke entiteit, met de entiteits-ID, de modellen, de apparatuur en de standaardinstelling. Gegenereerd uit de integratie.
- [Polling](polling.md): hoe vaak de omvormer wordt uitgelezen en hoe u sommige entiteiten sneller of langzamer uitleest.
- [De omvormer beschermen](protecting-the-inverter.md): de limieten die SAJ Local aanhoudt voor de verzoeken van SAJ Local.

## Dingen wijzigen

- [Instellingen wijzigen](changing-settings.md): bediening toestaan, instellingen wijzigen en EMS gebruiken.
- [Vermogensregeling](power-control.md): houd de batterij, de netaansluiting of de omvormer op een ingesteld vermogen, met de hand of met een schema.
- [De omvormer vervangen](replacing-the-inverter.md): verplaats een systeem naar een nieuwe omvormer, of tussen een H2 en een HS3, en behoud de geschiedenis.

## Dashboards

- [Dashboardkaarten](cards/README.md): de kaarten, de tegelkaartfunctie en de badge die SAJ Local aan Home Assistant toevoegt.

## Termen

- [Nomenclatuur](nomenclature.md): de SAJ- en Home Assistant-termen die de integratie, de kaarten en de documentatie gebruiken, met hun betekenis.

## Als er iets mis is

- [Apparaatstoringen en reparaties](faults-and-repairs.md): de storingen die de apparatuur meldt en de reparaties die SAJ Local aanmaakt.
- [Probleemoplossing](troubleshooting.md): diagnose, debuglogging en waar u hulp kunt vragen.

## Wat elk onderdeel kan

De functielijsten zeggen wat vandaag is gebouwd: [de integratie](../../../custom_components/saj_local/docs/features.md) en [de kaarten](../../../frontend/docs/features.md).

Ontwikkelaars: zie de [ontwikkelaarsdocumentatie](../developer/README.md).

## Disclaimer

SAJ Local is een onafhankelijke, door de community gebouwde integratie. SAJ Local is niet verbonden aan SAJ (Guangzhou Sanjing Electric Co., Ltd.), en SAJ en de dochterondernemingen en gelieerde bedrijven van SAJ hebben SAJ Local niet goedgekeurd, gesponsord of onderschreven.

SAJ, het SAJ-logo en alle bijbehorende productnamen, modelnamen en handelsmerken zijn eigendom van de betreffende eigenaren. De documentatie gebruikt de namen alleen om de apparatuur te benoemen waarmee SAJ Local werkt.

De software wordt geleverd zoals ze is, zonder enige vorm van garantie. U gebruikt SAJ Local op eigen risico: de auteurs aanvaarden geen aansprakelijkheid voor schade aan apparatuur, verlies van gegevens, verlies van garantie of enig ander gevolg van het gebruik van SAJ Local. De waarschuwing geldt met name voor het schrijven van instellingen naar uw omvormer.

## Dankwoord

H2-ondersteuning bouwt voort op het registeronderzoek en de praktijktests van stanus74 in [SAJ H2 Modbus](https://github.com/stanus74/home-assistant-saj-h2-modbus). Bedankt.
