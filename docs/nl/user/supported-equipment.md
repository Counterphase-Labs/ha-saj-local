[en](../../en-gb/user/supported-equipment.md) | [de](../../de/user/supported-equipment.md) | nl | [fr](../../fr/user/supported-equipment.md) | [zh](../../zh-hans/user/supported-equipment.md) | [es](../../es/user/supported-equipment.md) | [it](../../it/user/supported-equipment.md) | [pl](../../pl/user/supported-equipment.md) | [sv](../../sv/user/supported-equipment.md)

# Ondersteunde apparatuur

De pagina Ondersteunde apparatuur vermeldt de SAJ-producten die SAJ Local ondersteunt, de optionele apparatuur die elk model kan hebben en wat nog niet wordt ondersteund. De volledige lijst van wat de installatie doet staat in de sectie [Installatie en detectie](../../../custom_components/saj_local/docs/features.md#setup-and-detection) van de functielijst van de integratie.

## Ondersteunde modellen

SAJ Local herkent een model aan het apparaattype dat de omvormer meldt. Elk ander apparaattype wordt niet herkend.

| Model | Herkend als | Optionele apparatuur die SAJ Local detecteert |
| --- | --- | --- |
| HS3 | Apparaattype `0x1610`, drie fasen | Batterij, Meter A, Meter B, EV-lader, parallel systeem |
| H2, eenfasig, twee zonnestrings | Apparaattype `0x005a` | Batterij, Meter A, Meter B, parallel systeem |
| H2, eenfasig, drie zonnestrings | Apparaattype `0x005b` | Batterij, Meter A, Meter B, parallel systeem |

De verschillen tussen de modellen die u in het gebruik ziet:

- **EV-lader:** alleen de HS3. De H2 heeft geen EV-laderentiteiten, EV-ladertijdvakken of EV-laderonderdeel op de bedieningskaart.
- **Batterijpacks:** een H2 heeft entiteiten voor maximaal vijf batterijpacks. Een HS3 heeft entiteiten voor één batterijpack. Zie [optionele apparatuur](optional-equipment.md).
- **EMS:** alleen de HS3. Zie [instellingen wijzigen](changing-settings.md#ems).
- **Vermogensregeling:** de HS3 biedt Batterij, Net en Omvormer. De H2 biedt alleen Batterij. Zie [vermogensregeling](power-control.md).

[Optionele apparatuur](optional-equipment.md) legt uit hoe de detectie werkt en hoe u de detectie overschrijft. Het [entiteitenoverzicht](entities/README.md) vermeldt welk model en welke apparatuur elke entiteit nodig heeft.

## Nog niet ondersteund

- Automatische detectie herkent alleen de drie apparaattypen in de tabel. Andere SAJ-producten, zoals de HS2, de H1 en de AS1, worden niet herkend.
- Andere H2-varianten, zoals de driefasige H2, melden andere apparaattypen en worden niet automatisch herkend. U kunt het model met de hand kiezen, en SAJ Local markeert het model dan als niet geverifieerd. Metingen kunnen onjuist zijn, omdat SAJ Local de metingen niet kan toetsen. Zie [aan de slag](getting-started.md#wanneer-de-omvormer-niet-wordt-herkend).
- Instellingen wijzigen op een systeem waarvan het model niet is geverifieerd. Uitlezen werkt en elke wijziging wordt geweigerd.

## Waar de ondersteuning op berust

De HS3-ondersteuning is met de hand geverifieerd op een echte HS3. De H2-ondersteuning berust op SAJ-protocoldocumentatie en praktijkmeldingen en is niet met de hand geverifieerd op een H2. Het schrijven van instellingen en de vermogensregeling op de H2 berusten ook op documentatie en praktijkmeldingen.
