[en](../../en-gb/developer/frontend.md) | [de](../../de/developer/frontend.md) | nl | [fr](../../fr/developer/frontend.md) | [zh](../../zh-hans/developer/frontend.md) | [es](../../es/developer/frontend.md) | [it](../../it/developer/frontend.md) | [pl](../../pl/developer/frontend.md) | [sv](../../sv/developer/frontend.md)

# Frontend

Hoe de kaartbundel is georganiseerd en gebouwd, en hoe u elke kaart bekijkt in de ontwikkelinstantie.

De volledige lijst van wat de frontend omvat staat in de secties [Kaarten](../../../custom_components/saj_local/docs/features.md#cards) van de integratie en [Elementen en installatie](../../../frontend/docs/features.md#elements-and-setup) en [Thema en taal](../../../frontend/docs/features.md#theme-and-language) van de kaarten.

## Build

De kaarten, de tegelkaartfunctie en de badge zijn één Lit- en TypeScript-bundel onder `frontend/`. `make build` draait Vite en schrijft de bundel in `custom_components/saj_local/frontend/` als `saj-local-<hash>.js` met een `asset-manifest.json`, omdat HACS de integratiemap als één archief levert. Git volgt de gebouwde bundel en het manifest, dus een wijziging aan de kaarten wordt samen met een nieuwe build vastgelegd. De integratie leest het manifest, serveert het bestand dat het manifest noemt en voegt de URL van het bestand toe aan de Home Assistant-frontend, zodat gebruikers geen dashboardresource toevoegen.

De hash verandert bij elke build, zodat een browser nooit een verouderde bundel draait. De prijs is dat Home Assistant de gehashte bestandsnaam één keer registreert, bij het starten: een nieuwe bundel heeft een herstart van Home Assistant nodig voordat de browser het nieuwe bestand aangeboden krijgt. De ontwikkelinstantie mount de integratiemap, dus draai `make build` en herstart Home Assistant om een wijziging te zien.

## Broncode-indeling

De indeling volgt wat samen verandert:

- `src/system/` bevat alles wat geen tekenwerk is: de entiteiten van een systeem vinden in `hass`, vermogensrichting, weekdagen, tijdvakken, storingen, het bedieningsslot en serviceaanroepen. De map raakt nooit de DOM, zodat de regels zonder browser worden getest.
- `src/ui/` bevat de onderdelen die elke kaart tekent, alleen gestileerd met de themavariabelen van Home Assistant, omdat de Home Assistant-frontend geen `ha-*`-element aan aangepaste kaarten belooft.
- `src/cards/`, `src/features/` en `src/badges/` bevatten de elementen en registreren de elementen bij de Home Assistant-kiezer.
- `src/i18n/` bevat de tekst die alleen de kaarten nodig hebben, één bestand per taal, genoemd naar de Home Assistant-taalcode zoals de bestanden in de map `translations/` van de integratie (Engels en de acht doeltalen), met Engels als terugval voor elke andere taal. Entiteitsnamen, statussen en waarden komen van Home Assistant.
- `tests/fakes/` bevat een nep-`hass`, gebouwd uit een lijst van entiteiten, en de vervangingen voor de modules die een element gebruikt. Elke unittest oefent één module uit met elke samenwerkende partij vervangen door een van de fakes.

Een element vindt de entiteiten van een systeem op apparaat en vertaalsleutel, nooit op entiteits-ID, zodat een kaart nooit afhangt van een voorvoegsel van de entiteits-ID.

## Tests

`make test-frontend` draait de Vitest-unittests met de dekkingsdrempel. `make test-browser-controlled` draait Playwright tegen de gebouwde bundel met gecontroleerde gegevens, en `make test-browser-home-assistant` draait Playwright tegen een echte Home Assistant, zie de [pagina Controles](checks.md#make-targets). De schermafbeeldingen van de gebruikersdocumentatie komen uit een derde Playwright-configuratie, zie [Schermafbeeldingen](documentation.md#schermafbeeldingen).

## Showcase-dashboards

Om elke kaart in elke optie te bekijken is een Home Assistant met echte systemen nodig, dus de ontwikkelomgeving declareert twee dashboards, `saj-hs3` en `saj-h2`, uit `config/dashboards/saj-hs3.yaml` en `config/dashboards/saj-h2.yaml`, via het blok `lovelace: dashboards:` van `config/configuration.yaml`. De dashboards zijn gewone YAML die met de hand is geschreven, en geen script genereert de dashboards. Elk SAJ Local-element is een custom element dat door zijn eigen YAML wordt geconfigureerd, dus elke kaart, tegelfunctie en badge is afzonderlijk uitgeschreven met elke optie ingesteld, onder een kop die de kaart en de opties noemt.

- Elk dashboard heeft vier weergaven: Dashboard (de kaarten van een typisch systeemdashboard, uitgeschreven als gewone kaarten), Cards (elke kaart in elke optiecombinatie), Features and badges (een tegelkaart met de functie `custom:saj-local-weekdays-feature` voor elke weekdagenentiteit van een tijdvak, en de statusbadge) en Empty states (elke kaart zonder `device` en met het apparaat van iets wat geen SAJ Local is).
- De dashboards bevatten de apparaat-ID's van één ontwikkelinstantie. Een ontwikkelaar met een instantie met andere apparaat-ID's vervangt de twee `device`-ID's in elk bestand, de ID van het systeem en de ID van een apparaat dat geen SAJ Local is voor de weergave Empty states, en de entiteits-ID's van de weekdagen van de tijdvakken wanneer het voorvoegsel van de entiteits-ID afwijkt.
- Home Assistant leest de dashboarddeclaraties wanneer Home Assistant start, dus herstart Home Assistant na het wijzigen van `config/configuration.yaml`. Een wijziging aan een dashboardbestand verschijnt na het herladen van de pagina.
