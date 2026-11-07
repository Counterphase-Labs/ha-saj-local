[en](../../en-gb/developer/documentation.md) | [de](../../de/developer/documentation.md) | nl | [fr](../../fr/developer/documentation.md) | [zh](../../zh-hans/developer/documentation.md) | [es](../../es/developer/documentation.md) | [it](../../it/developer/documentation.md) | [pl](../../pl/developer/documentation.md) | [sv](../../sv/developer/documentation.md)

# Documentatie

Hoe de documentatiepagina's zijn georganiseerd, hoe het entiteitenoverzicht en de schermafbeeldingen worden gemaakt en waarop `make docs-check` faalt.

## Indeling

Gebruikerspagina's staan in `docs/en-gb/user/` en ontwikkelaarspagina's in `docs/en-gb/developer/`. Elke map heeft een index `README.md`, en elke pagina behandelt één onderwerp. Geen geschreven pagina is langer dan 300 regels. Elk feit heeft één eigenaar, vermeld onder [Bronnen](#bronnen), en elke andere pagina linkt naar de eigenaar in plaats van het feit te herhalen.

Schermafbeeldingen staan in `docs/images/en-gb/`. Elke afbeelding moet door een pagina worden gebruikt.

Schrijf de Engelse pagina's in Brits Engels, in de toon van Counterphase, en gebruik de termen die de vertalingen van de integratie aan gebruikers tonen. De gebruikerspagina's beschrijven SAJ in het algemeen en geven op het punt van het verschil aan waar de HS3 en de H2 verschillen. Een pagina splitst nooit op in één pagina per model.

## Eerst de functielijsten

De drie functielijsten vormen de basis van elke pagina: [integratie](../../../custom_components/saj_local/docs/features.md), [kaarten](../../../frontend/docs/features.md) en [simulator](../../../mock/docs/features.md). Een sectie van een functielijst zegt wat is gebouwd en noemt de bestanden die u moet lezen op de regel `Files:` van de sectie. Controleer elke bewering aan de hand van die bestanden voordat u de bewering documenteert. De requirementdocumenten zeggen wat de bedoeling is en worden alleen voor de bedoeling gelezen. Een gedrag dat in een requirementdocument staat maar in geen enkele functielijst, is niet gebouwd, en een gebruikerspagina beschrijft het gedrag niet als beschikbaar. Waar een functielijst en de code verschillen, is de code wat gebruikers krijgen, dus corrigeer de functielijst in dezelfde wijziging.

Een pagina die code beschrijft linkt naar de sectie van de functielijst waarvan de regel `Files:` de code noemt, en herhaalt de bestandslijst niet.

Een wijziging van een mogelijkheid werkt de functielijst van het onderdeel bij, en elke gebruikerspagina die naar de gewijzigde sectie linkt, in dezelfde wijziging. De root-`AGENTS.md` bevat de regel.

## Gegenereerd entiteitenoverzicht

`docs/en-gb/user/entities/` bevat één gegenereerde pagina per gebied en een index `README.md`. Draai `make docs` om de pagina's opnieuw te genereren en commit daarna de opnieuw gegenereerde pagina's. Prozapagina's noemen nooit met de hand een entiteit; de prozapagina's linken naar de gegenereerde pagina's. Gegenereerde pagina's zijn vrijgesteld van de limiet van 300 regels, omdat lezers een gebied zoals de batterij doorzoeken in plaats van het gebied te lezen.

De generator is `.github/scripts/docs_check.py`, door `make docs` met `--write` gedraaid. De generator importeert alleen de SAJ-bibliotheek en leest `custom_components/saj_local/translations/en.json`, dus de generator heeft geen Home Assistant nodig. Elke gebiedspagina opent met een link naar de secties van de functielijst die het gebied behandelen en een regel over het voorvoegsel van de entiteits-ID, en heeft dan één rij per entiteit met de naam uit `en.json`, de entiteits-ID zonder voorvoegsel, het type, de eenheid, de modellen die de entiteit hebben, de apparatuur die met elk aantal fasen, strings of packs moet zijn geïnstalleerd, en of de entiteit standaard is ingeschakeld. Een entiteit die twee modellen verschillend definiëren, bijvoorbeeld met een andere eenheid, krijgt één rij per definitie.

### Entiteitsbronnen

Elke entiteit komt uit een van deze bronnen, en de generator leest ze allemaal:

| Bron | Code | Entiteiten |
| --- | --- | --- |
| De registercatalogus van elk geleverd model | `catalogue_of` in [catalogue.py](../../../custom_components/saj_local/saj/catalogue.py), aangeroepen voor elk profiel in `PROFILES` van [profiles.py](../../../custom_components/saj_local/saj/profiles.py), waarbij rijen die niet worden getoond worden overgeslagen | Sensoren, binaire sensoren (de storingen), nummers, selecties, schakelaars, tijden en knoppen |
| De sensor Bediening toegestaan | `CONTROL_ALLOWED_KEY` in [binary_sensor.py](../../../custom_components/saj_local/binary_sensor.py) | `binary_sensor.saj_control_allowed`, op beide modellen |
| De schakelaars en nummers van de vermogensregeling | `power_control` van elk profiel ([hs3.py](../../../custom_components/saj_local/saj/models/hs3.py) en [h2.py](../../../custom_components/saj_local/saj/models/h2.py)), de `PowerFunction`-sleutels in [models/\_\_init\_\_.py](../../../custom_components/saj_local/saj/models/__init__.py) en `FUNCTION_EQUIPMENT` in [power_control.py](../../../custom_components/saj_local/saj/power_control.py), aangemaakt door [switch.py](../../../custom_components/saj_local/switch.py) en [number.py](../../../custom_components/saj_local/number.py) | Een schakelaar en een nummer voor elke vermogensfunctie van een model: batterij op beide modellen, net en omvormer op de HS3 |

`make docs-check` faalt wanneer een entiteit in het blok `entity` van `en.json` op geen enkele gebiedspagina staat, dus een entiteitsbron die de generator niet leest wordt direct gevonden. Een nieuwe bron vraagt dat de generator de bron leest en een rij in de tabel hierboven.

### Gebieden

Een entiteit komt terecht in het eerste gebied dat past, in deze volgorde:

1. Entiteiten buiten de catalogus: Toegevoegd door de integratie.
2. Binaire sensoren uit de catalogus, dat zijn de storingen: Storingen.
3. Entiteiten met een index van een batterijpack: Batterijpacks.
4. Entiteiten van optionele apparatuur: Batterij, Net en Meter A, Meter B, EV-lader of Parallel systeem.
5. Schrijfbare entiteiten zonder apparatuur: Instellingen.
6. Entiteiten waarvan de sleutel begint met `grid_`: Net en Meter A.
7. Al het andere: Omvormer en PV.

De tabel `AREAS` van `.github/scripts/docs_check.py` noemt de gebieden, hun samenvattingen en de secties van de functielijst waarnaar elke gebiedspagina linkt.

## Controles

`make docs-check` draait `.github/scripts/docs_check.py` zonder `--write` en meldt één regel per bevinding:

- een gegenereerde pagina die verschilt van wat `make docs` zou schrijven;
- een entiteit in `en.json` die op geen enkele gebiedspagina staat, en een gegenereerde entiteit zonder naam in `en.json`;
- een relatieve link, afbeelding of kopanker die niet oplost, in de pagina's, `README.md`, `CONTRIBUTING.md`, `SECURITY.md` en elke `AGENTS.md`, inclusief links naar de functielijsten en de requirementdocumenten;
- een afbeelding in `docs/images/` die geen enkele pagina gebruikt;
- een geschreven pagina van meer dan 300 regels;
- een sectie van een functielijst zonder rij in de [Tabel functiedekking](#tabel-functiedekking), een sectie in de tabel die de functielijst niet heeft, een pagina in de tabel die niet bestaat, en een pagina die niet linkt naar de sectie van de functielijst in de rij, via de kopanker van de sectie.

`make docs-check` is een stap van `make ci`, en GitHub draait `make ci`, dus de controle vraagt geen workflowwijziging. De controle leest geen schermafbeelding behalve voor de link- en weesregels en start geen browser.

## Schermafbeeldingen

Elke schermafbeelding in `docs/images/<code>/` wordt door `make docs-images` gemaakt vanuit een echte Home Assistant in Docker met de gebruikerstaal ingesteld op de taal van de map, of vanuit de simulatorpagina's van dezelfde run. `make docs-images` draait elke taal tegelijk, elke taal in eigen verse containers, en `ARGS=<code>` kiest één taal. Geen schermafbeelding wordt met de hand bewerkt of gemaakt, dus de set kan worden herbouwd wanneer de interface verandert. De schermafbeeldingen tonen de simulators, dus elke meting in een schermafbeelding is een gesimuleerde waarde.

De target draait `tests/playwright/run-docs-images.sh`, dat de images van de services `homeassistant` en `playwright-docs` van [compose.playwright.yaml](../../../compose.playwright.yaml) één keer voor alle talen bouwt, voor elke taal een wegwerp-Home Assistant en twee simulators start, de spec draait en daarna de containers, volumes en lokale images verwijdert. De Playwright-containers draaien als de hostgebruiker, dus geen bestand van een run is eigendom van root, ook niet na een run die vroegtijdig stopte. De target heeft Docker nodig, heeft dezelfde tijdslimiet als `make test-browser-home-assistant` en neemt opties via `ARGS`, die het script ontvangt. Het Home Assistant-image wordt gebouwd uit `Dockerfile.playwright-home-assistant`, dat de kaartbundel bouwt en de integratie in het image kopieert, dus er wordt geen integratiecode gemount. De spec is `frontend/tests/browser/docs/screenshots.spec.ts`, ingesteld door `frontend/playwright.docs.config.ts`.

- **Systemen.** De HS3 is de simulator `mock-docs` op `mock/scenarios/hs3-full-house.yaml`, waarop alle apparatuur is geïnstalleerd. De H2 is de simulator `mock-h2` op `mock/scenarios/h2-battery.yaml` en krijgt het entiteitsvoorvoegsel `h2`. Geen van beide simulators mount een statusmap, dus elke run begint bij het scenario.
- **Vaste omstandigheden.** Het venster is 1280 bij 800 pixels en het thema is licht. Een hoog dialoogvenster of een hoge kaart wordt gemaakt in een venster van 1600 pixels hoog, omdat de vaste kop van Home Assistant anders de bovenkant van het element zou bedekken.
- **Stilgezette klokken.** Nadat de spec elke simulator naar zijn scenario heeft teruggezet, zet de spec de gesimuleerde klokken van beide simulators voor de hele run stil op de starttijd van het scenario, dus de metingen zijn bij elke run gelijk. De schermafbeeldingen van de simulatorpagina's en de reparatieschermafbeelding tonen vaste tijdwaarden, niet de echte. Voor elke simulatorpagina geeft de spec de browser een kopie van de paginagegevens met vaste aanvraagsnelheden, tijden, duren en clientadressen, en zet de spec de klok van de browser vast. Voor de reparatieschermafbeelding zet de spec de klok van de browser vast op 5 seconden nadat Home Assistant het reparatieprobleem heeft aangemaakt, dus het probleem toont "5 seconden geleden".
- **Parallelle talen.** De talen draaien tegelijk, elke taal in eigen containers. De run start tegelijk zoveel talen als de machine groepen van vier processors heeft. Elke taal schrijft zijn eigen resultatenmap `frontend/test-results/docs/<code>/` en rapportmap `frontend/playwright-report/docs/<code>/`. Een mislukte taal stopt de andere talen niet.
- **Taal.** Elke run stelt zowel de servertaal van Home Assistant in, voordat SAJ Local wordt ingesteld zodat de entiteiten met namen in die taal worden aangemaakt, als de gebruikerstaal, met de taalcode en niet met het label van de taalkiezer. De run mislukt als een entiteitsnaam van SAJ Local niet in de taal van de run staat. De afbeeldingen gaan naar `docs/images/<code>/`. De spec opent schermen via een URL-route, vindt de velden van SAJ Local-formulieren aan hun attribuut `name` en vindt besturingselementen van Home Assistant die alleen tekst hebben aan de tekst die tijdens de run met `hass.localize` uit de draaiende Home Assistant wordt gelezen. De spec bevat geen tabel met labels, dus elke taal doorloopt dezelfde stappen.
- **Namen.** Elk bestand heet `<pagina>-<onderwerp>.png`, waarbij `<pagina>` het paginapad is met `/` vervangen door `-`, bijvoorbeeld `cards-battery-card.png`, en de pagina die de afbeelding toont linkt naar het bestand.
- **Simulatorpagina's.** De schermafbeeldingen van de simulatorpagina's komen van de twee simulators van dezelfde run, `mock-docs` en `mock-h2`, en gebruiken het naamvoorvoegsel `developer-simulator-page-`. Ze worden als laatste gemaakt, na elke Home Assistant-schermafbeelding, zodat niets wat op een simulatorpagina wordt gedaan een Home Assistant-schermafbeelding verandert. De spec stelt de storing "Fan 1 fault" in op de HS3-pagina, en het register dat de reparatieschermafbeelding de simulator laat weigeren blijft geweigerd, dus de weergave Link, het verkeerslogboek en de wijzigingen in de statusbalk tonen echte wijzigingen.
- **Opzet.** De spec maakt een gebruiker aan via de onboarding-API, voegt de HS3 toe via de configuratiestroom in de browser, voegt de H2 toe via de API van de configuratiestroom, zet Bediening toestaan aan voor beide systemen en voegt via de Home Assistant WebSocket-API voor elk systeem één dashboard toe met alle SAJ Local-kaarten en de statusbadge.
- **Alles of niets.** De spec wacht maximaal twee minuten tot beide systemen zonnevermogen melden. De spec schrijft de afbeeldingen pas nadat elke stap is geslaagd, dus een mislukte run laat de gecommitte afbeeldingen zoals ze waren.
- **Wachten.** De spec wacht op een scherm door te controleren op de toestand die het scherm toont, nooit met een vaste pauze.
- **Reparatie.** De reparatieschermafbeelding toont de reparatie voor geweigerde registers. De spec voegt een pollinggroep voor de omvormertemperatuur toe met een interval van 10 seconden, laat de simulator dat register weigeren via `POST /api/link` van de simulatorpagina en wacht maximaal twee minuten tot `repairs/list_issues` het probleem `registers_refused` van SAJ Local vermeldt. De run faalt met een melding die het ontbrekende probleem noemt wanneer het probleem niet verschijnt.
- **Formulieren.** De waarschuwing bij het wijzigen van het voorvoegsel wordt vastgelegd en daarna wordt het formulier gesloten, wat de stroom afbreekt, dus er wordt geen voorvoegsel opgeslagen. De waarschuwing bij Bediening toestaan wordt vastgelegd en daarna bevestigd, omdat de kaarten toegestane bediening nodig hebben.
- **Fouten.** Het HTML-rapport van elke taal staat in `frontend/playwright-report/docs/<code>/`, en een mislukte taal bewaart het Home Assistant-logboek in de resultatenmap `frontend/test-results/docs/<code>/`. De mislukte run noemt elke mislukte taal en de rapportmap ervan.

Schermafbeeldingen worden niet pixel voor pixel vergeleken, niet in CI en nergens anders. Home Assistant tekent live waarden en lettertypen bij elke run anders, dus een pixelvergelijking zou zonder echte wijziging falen. Beoordeel een gewijzigde afbeelding door naar de afbeelding te kijken.

### Een schermafbeelding toevoegen of wijzigen

1. Voeg de opname toe of wijzig de opname in de spec, met de bestandsnaam in de vorm `<pagina>-<onderwerp>.png`.
2. Verwijs naar de afbeelding vanaf de pagina die het onderwerp uitlegt.
3. Draai `make docs-images`, bekijk de gewijzigde afbeeldingen en commit de gewijzigde afbeeldingen.
4. Draai `make docs-check`. Een afbeelding waar geen pagina naar verwijst en een link naar een afbeelding die niet bestaat worden beide gemeld.

`make docs-images` is geen stap van `make ci`, en CI genereert de afbeeldingen niet opnieuw. Draai de target voor elke release, zie de [releasepagina](releasing.md).

## Een pagina toevoegen

1. Maak de pagina onder `docs/en-gb/user/` of `docs/en-gb/developer/` en link de pagina vanuit de index van de map.
2. Link de pagina naar de sectie van de functielijst waarvan de regel `Files:` de code noemt die de pagina beschrijft.
3. Voeg de pagina toe aan de rij van die sectie in de Tabel functiedekking, of voeg een rij toe. Een nieuwe sectie van een functielijst heeft een rij nodig voordat `make docs-check` slaagt.
4. Draai `make docs-check`.

Houd de pagina's bruikbaar: link naar het bestand dat een feit bevat in plaats van het feit te kopiëren, leg de reden van een besluit vast omdat redenen zelden veranderen en details voortdurend, en houd voorbeelden schaars en draai elk voorbeeld opnieuw wanneer het voorbeeld verandert.

## Talen

De documentatie bestaat in het Engels en in elke doeltaal van de [globale requirements](../../../.github/work/requirements.md#language). De functielijsten en de requirementdocumenten blijven alleen Engels.

- **Indeling.** Elke taal heeft de zustermappen `docs/<code>/user/`, `docs/<code>/developer/` en `docs/images/<code>/`, met in elke taal dezelfde bestandsnamen. De codes zijn `en-gb`, `de`, `nl`, `fr`, `zh-hans`, `es`, `it`, `pl` en `sv`. Een codeblok dat in meerdere talen gelijk is, blijft op elke pagina in de tekst staan en staat in een markeringspaar `jscpd:ignore-start` en `jscpd:ignore-end`, alleen onder een uitzondering die de gebruiker in een plan heeft goedgekeurd, zoals `AGENTS.md` bepaalt. Een markeringspaar omvat één codeblok en niets anders.
- **Generator.** `make docs` schrijft `docs/<code>/user/entities/` voor elke taal uit het bijbehorende bestand in `custom_components/saj_local/translations/`. De apparatuurnamen komen uit hetzelfde vertaalbestand, en de andere teksten van de generator komen uit `.github/scripts/docs_text/<code>.json`.
- **Documentatiecontrole.** `make docs-check` past elke regel toe op elke taalmap. De [Tabel functiedekking](#tabel-functiedekking) op deze pagina geldt voor elke taal onder dezelfde paginanamen, en de regel voor weesafbeeldingen controleert `docs/images/<code>/` tegen de pagina's van dezelfde taal.
- **Taalbalk.** De eerste regel van elke pagina onder `docs/<code>/user/` en `docs/<code>/developer/`, de gegenereerde entiteitspagina's inbegrepen, is de taalbalk `en | de | nl | fr | zh | es | it | pl | sv`, altijd in die volgorde. Elk label behalve de huidige taal verwijst naar dezelfde pagina in de map van die taal, en de huidige taal is gewone tekst. `make docs` schrijft de taalbalk, en `make docs-check` meldt een pagina waarvan de eerste regel niet de verwachte taalbalk is en een link van de taalbalk naar een pagina die niet bestaat.
- **Vertaalde README.** De `README.md` in de hoofdmap blijft Engels en is vertaald in `docs/<code>/README.md`, waarvan de links naar de pagina's van die taal verwijzen. De `README.md` in de hoofdmap en elke `docs/<code>/README.md` hebben dezelfde taalbalk als eerste regel, en `make docs-check` meldt een ontbrekende `docs/<code>/README.md`.
- **Schermafbeeldingen.** `make docs-images` draait de spec voor elke taal tegelijk, elke taal in eigen verse containers, met een eigen resultatenmap en rapportmap. `ARGS=<code>` kiest één taal, zie [Schermafbeeldingen](#schermafbeeldingen).
- **Nomenclatuur.** De pagina `user/nomenclature.md` van elke taal is de lijst met termen die elke vertaling van de integratie, de kaarten en de pagina's van de taal volgt. De Engelse [nomenclatuur](../user/nomenclature.md) is de bron.
- **Engels wijzigen.** Een wijziging van een Engelse tekst, pagina of schermafbeelding werkt elke taal bij in dezelfde wijziging. Geen controle houdt de talen gelijk.

## Tabel functiedekking

Elke sectie van een functielijst wordt onderzocht vanaf de regel `Files:` van de sectie en gedekt door de pagina's die hier worden genoemd. Elke genoemde pagina linkt naar de sectie via de kopanker van de sectie. Een paginanaam is relatief ten opzichte van `docs/en-gb/` en linkt naar de pagina. De tabel staat alleen op de Engelse pagina [Documentatie](../../en-gb/developer/documentation.md#feature-coverage-table), en `docs-check` leest de tabel van daar. De tabel geldt in elke taal voor dezelfde paginanamen, en een pagina die wordt toegevoegd, samengevoegd of gesplitst werkt de tabel in dezelfde wijziging bij.

## Bronnen

| Feit | Eigenaar |
| --- | --- |
| Wat SAJ Local doet, in één korte samenvatting | [gebruikersindex](../user/README.md) |
| Wat elk onderdeel kan | de drie functielijsten |
| Ondersteunde modellen en apparatuur | [ondersteunde apparatuur](../user/supported-equipment.md) |
| Entiteitsnamen, entiteits-ID's, modellen, apparatuur en standaardwaarden | de catalogus en `translations/en.json`, via het [entiteitenoverzicht](../user/entities/README.md) |
| Entiteitstypen, regels voor standaard ingeschakeld en tekenconventies | de sectie Apparaten en entiteiten van de functielijst van de integratie |
| Ontwikkelomgeving | [omgeving](environment.md) |
| Make-targets en controleregels | [controles](checks.md) |
| Releasen en ophoging van de Home Assistant-versie | [releasen](releasing.md) |
| Overzichtsschermafbeelding van de site | `docs/images/en-gb/cards-power-flow-card.png`, bij elke release door de maintainers naar de projectwebsite gekopieerd, zie de [releasepagina](releasing.md) |
| Hoe u een beveiligingsprobleem meldt | `SECURITY.md` |
| Issuelabels en de regels voor labels | `.github/labels.yml` en `CONTRIBUTING.md` |
| Licentievoorwaarden | `LICENSE` |
| Beoogd productgedrag | `.github/work/requirements.md` en de drie requirementdocumenten van de onderdelen |
