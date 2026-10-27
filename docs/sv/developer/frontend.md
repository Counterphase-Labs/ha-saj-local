[en](../../en-gb/developer/frontend.md) | [de](../../de/developer/frontend.md) | [nl](../../nl/developer/frontend.md) | [fr](../../fr/developer/frontend.md) | [zh](../../zh-hans/developer/frontend.md) | [es](../../es/developer/frontend.md) | [it](../../it/developer/frontend.md) | [pl](../../pl/developer/frontend.md) | sv

# Frontend

Hur kortpaketet är organiserat och byggs, och hur du tittar på varje kort i utvecklingsinstansen.

Den fullständiga listan över vad frontend omfattar finns i funktionslisteavsnitten [Kort](../../../custom_components/saj_local/docs/features.md#cards) för integrationen och [Element och inställning](../../../frontend/docs/features.md#elements-and-setup) och [Tema och språk](../../../frontend/docs/features.md#theme-and-language) för korten.

## Bygge

Korten, brickkortets funktion och märket är ett Lit- och TypeScript-paket under `frontend/`. `make build` kör Vite och skriver paketet till `custom_components/saj_local/frontend/` som `saj-local-<hash>.js` med en `asset-manifest.json`, eftersom HACS levererar integrationsmappen som ett arkiv. Git spårar det byggda paketet och manifestet, så en ändring av korten checkas in tillsammans med ett nytt bygge. Integrationen läser manifestet, serverar filen som manifestet namnger och lägger till filens URL i Home Assistants frontend, så användare lägger inte till någon instrumentpanelsresurs.

Hashen ändras vid varje bygge så att en webbläsare aldrig kör ett föråldrat paket. Priset är att Home Assistant registrerar filnamnet med hash en gång, vid start: ett nytt paket kräver en omstart av Home Assistant innan webbläsaren erbjuds den nya filen. Utvecklingsinstansen monterar integrationsmappen, så kör `make build` och starta om Home Assistant för att se en ändring.

## Källstruktur

Strukturen följer det som ändras tillsammans:

- `src/system/` innehåller allt som inte är ritning: att hitta ett systems entiteter i `hass`, effektriktning, veckodagar, schematidsluckor, fel, styrlåset och tjänsteanrop. Mappen rör aldrig DOM, så reglerna testas utan webbläsare.
- `src/ui/` innehåller delarna som varje kort ritar, stilsatta enbart med Home Assistants temavariabler, eftersom Home Assistants frontend inte lovar något `ha-*`-element till anpassade kort.
- `src/cards/`, `src/features/` och `src/badges/` innehåller elementen och registrerar elementen i Home Assistants väljare.
- `src/i18n/` innehåller den text som bara korten behöver, en fil per språk, namngiven med Home Assistants språkkod som filerna i integrationens mapp `translations/` (engelska och de åtta målspråken), med engelska som reserv för varje annat språk. Entitetsnamn, tillstånd och värden kommer från Home Assistant.
- `tests/fakes/` innehåller ett falskt `hass`, byggt av en lista med entiteter, och ersättarna för de moduler som ett element använder. Varje enhetstest prövar en modul med varje medarbetare ersatt av en av de falska.

Ett element hittar ett systems entiteter via enhet och översättningsnyckel, aldrig via entitets-ID, så ett kort beror aldrig på ett entitets-ID-prefix.

## Tester

`make test-frontend` kör Vitest-enhetstesterna med täckningsgränsen. `make test-browser-controlled` kör Playwright mot det byggda paketet med kontrollerade data, och `make test-browser-home-assistant` kör Playwright mot en riktig Home Assistant, se [kontrollsidan](checks.md#make-mål). Användardokumentationens skärmbilder kommer från en tredje Playwright-konfiguration, se [Skärmbilder](documentation.md#skärmbilder).

## Demoinstrumentpaneler

Att titta på varje kort i varje alternativ kräver en Home Assistant med riktiga system, så utvecklingsmiljön deklarerar två instrumentpaneler, `saj-hs3` och `saj-h2`, från `config/dashboards/saj-hs3.yaml` och `config/dashboards/saj-h2.yaml`, genom blocket `lovelace: dashboards:` i `config/configuration.yaml`. Instrumentpanelerna är vanlig YAML skriven för hand, och inget skript genererar dem. Varje SAJ Local-element är ett anpassat element som konfigureras med sin egen YAML, så varje kort, brickfunktion och märke skrivs ut för sig med varje alternativ satt, under en rubrik som namnger kortet och dess alternativ.

- Varje instrumentpanel har fyra vyer: Instrumentpanel (korten på en typisk systeminstrumentpanel, utskrivna som vanliga kort), Kort (varje kort i var och en av sina alternativkombinationer), Funktioner och märken (ett brickkort med funktionen `custom:saj-local-weekdays-feature` för varje entitet för tidsluckans veckodagar, och statusmärket) och Tomma tillstånd (varje kort utan `device` och med enheten för något som inte är SAJ Local).
- Instrumentpanelerna innehåller enhets-ID:na för en utvecklingsinstans. En utvecklare vars instans har andra enhets-ID byter ut de två `device`-ID:na i varje fil, systemets ID och ID:t för en enhet som inte är SAJ Local för vyn Tomma tillstånd, samt entitets-ID:na för tidsluckornas veckodagar när entitets-ID-prefixet skiljer sig.
- Home Assistant läser instrumentpanelsdeklarationerna när Home Assistant startar, så starta om Home Assistant efter att ha ändrat `config/configuration.yaml`. En ändring av en instrumentpanelsfil syns efter en omladdning av sidan.
