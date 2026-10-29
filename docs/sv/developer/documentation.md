[en](../../en-gb/developer/documentation.md) | [de](../../de/developer/documentation.md) | [nl](../../nl/developer/documentation.md) | [fr](../../fr/developer/documentation.md) | [zh](../../zh-hans/developer/documentation.md) | [es](../../es/developer/documentation.md) | [it](../../it/developer/documentation.md) | [pl](../../pl/developer/documentation.md) | sv

# Dokumentation

Hur dokumentationssidorna är organiserade, hur entitetsreferensen och skärmbilderna görs och vad `make docs-check` misslyckas på.

## Struktur

Användarsidorna finns i `docs/en-gb/user/` och utvecklarsidorna i `docs/en-gb/developer/`. Varje mapp har ett `README.md`-index, och varje sida behandlar ett ämne. Ingen skriven sida är längre än 300 rader. Varje faktum har en ägare, listad under [Källor](#källor), och varje annan sida länkar till ägaren i stället för att upprepa faktumet.

Skärmbilderna finns i `docs/images/en-gb/`. Varje bild måste vara refererad av en sida.

Skriv sidorna på brittisk engelska, i Counterphases tonläge, och använd de termer som integrationens översättningar visar för användarna. Användarsidorna beskriver SAJ i allmänhet och markerar, där skillnaden uppstår, var HS3 och H2 skiljer sig åt. En sida delas aldrig upp i en sida per modell.

## Funktionslistor först

De tre funktionslistorna är grunden för varje sida: [integrationens](../../../custom_components/saj_local/docs/features.md), [kortens](../../../frontend/docs/features.md) och [simulatorns](../../../mock/docs/features.md). Ett avsnitt i en funktionslista säger vad som är byggt och namnger de filer som ska läsas på avsnittets rad `Files:`. Bekräfta varje påstående mot dessa filer innan du dokumenterar påståendet. Kravdokumenten säger vad som är avsett och läses bara för avsikten. Ett beteende som finns i ett kravdokument men i ingen funktionslista är inte byggt, och en användarsida beskriver inte beteendet som tillgängligt. Där en funktionslista och koden skiljer sig åt är det koden som användarna får, så rätta funktionslistan i samma ändring.

En sida som beskriver kod länkar till det avsnitt i funktionslistan vars rad `Files:` namnger koden, och upprepar inte fillistan.

En ändring av en förmåga uppdaterar delens funktionslista och varje användarsida som länkar till det ändrade avsnittet, i samma ändring. Regeln finns i rotens `AGENTS.md`.

## Genererad entitetsreferens

`docs/en-gb/user/entities/` innehåller en genererad sida per område och ett `README.md`-index. Kör `make docs` för att generera sidorna på nytt och checka sedan in de genererade sidorna. Skrivna sidor namnger aldrig en entitet för hand; de länkar till de genererade sidorna. Genererade sidor är undantagna från gränsen på 300 rader, eftersom läsare söker i ett område, till exempel batteriet, i stället för att läsa området.

Generatorn är `.github/scripts/docs_check.py`, körd med `--write` av `make docs`. Generatorn importerar bara SAJ-biblioteket och läser `custom_components/saj_local/translations/en.json`, så generatorn behöver ingen Home Assistant. Varje områdessida öppnar med en länk till de funktionslisteavsnitt som täcker området och en rad om entitets-ID-prefixet, och har sedan en rad per entitet med namnet från `en.json`, entitets-ID utan prefix, typen, enheten, de modeller som har entiteten, den utrustning som måste vara installerad vid valfritt antal faser, strängar eller packar, och om entiteten är aktiverad som standard. En entitet som två modeller definierar olika, till exempel med en annan enhet, får en rad per definition.

### Entitetskällor

Varje entitet kommer från en av dessa källor, och generatorn läser alla:

| Källa | Kod | Entiteter |
| --- | --- | --- |
| Registerkatalogen för varje levererad modell | `catalogue_of` i [catalogue.py](../../../custom_components/saj_local/saj/catalogue.py), anropad för varje profil i `PROFILES` i [profiles.py](../../../custom_components/saj_local/saj/profiles.py), med rader som inte exponeras överhoppade | Sensorer, binära sensorer (felen), nummer, val, brytare, tider och knappar |
| Sensorn för tillåten styrning | `CONTROL_ALLOWED_KEY` i [binary_sensor.py](../../../custom_components/saj_local/binary_sensor.py) | `binary_sensor.saj_control_allowed`, på båda modellerna |
| Effektstyrningens brytare och nummer | `power_control` för varje profil ([hs3.py](../../../custom_components/saj_local/saj/models/hs3.py) och [h2.py](../../../custom_components/saj_local/saj/models/h2.py)), nycklarna `PowerFunction` i [models/\_\_init\_\_.py](../../../custom_components/saj_local/saj/models/__init__.py) och `FUNCTION_EQUIPMENT` i [power_control.py](../../../custom_components/saj_local/saj/power_control.py), skapade av [switch.py](../../../custom_components/saj_local/switch.py) och [number.py](../../../custom_components/saj_local/number.py) | En brytare och ett nummer för varje effektfunktion i en modell: batteri på båda modellerna, nät och växelriktare på HS3 |

`make docs-check` misslyckas när en entitet i blocket `entity` i `en.json` finns på ingen områdessida, så en entitetskälla som generatorn inte läser upptäcks genast. En ny källa kräver att generatorn läser källan och en rad i tabellen ovan.

### Områden

En entitet hamnar i det första område som matchar, i denna ordning:

1. Entiteter utanför katalogen: Tillagt av integrationen.
2. Binära sensorer från katalogen, som är felen: Fel.
3. Entiteter med ett batteripackindex: Batteripack.
4. Entiteter för valfri utrustning: Batteri, Nät och Mätare A, Mätare B, Elbilsladdare eller Parallellsystem.
5. Skrivbara entiteter utan utrustning: Inställningar.
6. Entiteter vars nyckel börjar med `grid_`: Nät och Mätare A.
7. Allt annat: Växelriktare och PV.

Tabellen `AREAS` i `.github/scripts/docs_check.py` namnger områdena, deras sammanfattningar och de funktionslisteavsnitt som varje områdessida länkar till.

## Kontroller

`make docs-check` kör `.github/scripts/docs_check.py` utan `--write` och rapporterar en rad per fynd:

- en genererad sida som skiljer sig från vad `make docs` skulle skriva;
- en entitet i `en.json` som finns på ingen områdessida, och en genererad entitet utan namn i `en.json`;
- en relativ länk, bild eller rubrikankare som inte går att lösa upp, på sidorna, i `README.md`, `CONTRIBUTING.md`, `SECURITY.md` och varje `AGENTS.md`, inklusive länkar in i funktionslistorna och kravdokumenten;
- en bild i `docs/images/` som ingen sida refererar;
- en skriven sida över 300 rader;
- ett funktionslisteavsnitt utan rad i [Tabell över funktionstäckning](#tabell-över-funktionstäckning), ett avsnitt som nämns i tabellen men som funktionslistan inte har, en sida som nämns i tabellen men inte finns, och en sida som inte länkar till det funktionslisteavsnitt som raden anger, via avsnittets rubrikankare.

`make docs-check` är ett steg i `make ci`, och GitHub kör `make ci`, så kontrollen behöver ingen ändring av arbetsflödet. Kontrollen läser ingen skärmbild utöver reglerna för länkar och föräldralösa bilder och startar ingen webbläsare.

## Skärmbilder

Varje skärmbild i `docs/images/<code>/` görs av `make docs-images` från en riktig Home Assistant i Docker med användarspråket inställt på mappens språk, eller från simulatorsidorna i samma körning. `make docs-images` kör varje språk, engelska först, med nya containrar för varje körning, och `ARGS=<code>` väljer ett språk. Ingen skärmbild redigeras eller tas för hand, så uppsättningen kan byggas om närhelst gränssnittet ändras. Skärmbilderna visar simulatorerna, så varje avläsning i en skärmbild är ett simulerat värde.

Målet kör `tests/playwright/run-docs-images.sh`, som bygger tjänsterna `homeassistant` och `playwright-docs` i [compose.playwright.yaml](../../../compose.playwright.yaml), startar engångs-Home Assistant och två simulatorer, kör specifikationen och tar sedan bort containrarna, volymerna och de lokala avbilderna. Målet kräver Docker, har samma tidsgräns som `make test-browser-home-assistant` och tar alternativ genom `ARGS`, som skriptet tar emot. Home Assistant-avbilden byggs från `Dockerfile.playwright-home-assistant`, som bygger kortpaketet och kopierar in integrationen i avbilden, så ingen integrationskod monteras. Specifikationen är `frontend/tests/browser/docs/screenshots.spec.ts`, konfigurerad av `frontend/playwright.docs.config.ts`.

- **System.** HS3 är simulatorn `mock-docs` på `mock/scenarios/hs3-full-house.yaml`, som har all utrustning installerad. H2 är simulatorn `mock-h2` på `mock/scenarios/h2-battery.yaml` och får entitetsprefixet `h2`. Ingen av simulatorerna monterar en tillståndsmapp, så varje körning börjar från scenariot.
- **Fasta villkor.** Visningsytan är 1280 gånger 800 pixlar, temat är ljust och klockan är verklig. En hög dialogruta eller ett högt kort tas i ett fönster som är 1600 pixlar högt, eftersom Home Assistants fasta sidhuvud annars skulle täcka elementets överkant.
- **Språk.** Varje körning ställer in både Home Assistants serverspråk, innan SAJ Local ställs in så att entiteterna skapas med namn på det språket, och användarspråket, med språkkoden och inte med etiketten i språkväljaren. Körningen misslyckas om ett entitetsnamn från SAJ Local inte är på körningens språk. Bilderna hamnar i `docs/images/<code>/`. Specifikationen öppnar skärmar via URL-väg, hittar fälten i SAJ Local-formulär via deras attribut `name` och hittar Home Assistant-kontroller som bara har text via texten som läses vid körning från den körande Home Assistant med `hass.localize`. Specifikationen har ingen tabell över etiketter, så varje språk kör samma steg.
- **Namn.** Varje fil heter `<page>-<subject>.png`, där `<page>` är sidans sökväg med `/` ersatt av `-`, till exempel `cards-battery-card.png`, och sidan som visar bilden länkar till filen.
- **Simulatorsidor.** Skärmbilderna av simulatorsidorna kommer från de två simulatorerna i samma körning, `mock-docs` och `mock-h2`, och använder namnprefixet `developer-simulator-page-`. De tas sist, efter varje Home Assistant-skärmbild, så att inget som görs på en simulatorsida ändrar en Home Assistant-skärmbild. Specifikationen sätter felet "Fan 1 fault" på HS3-sidan, och registret som reparationsskärmbilden får simulatorn att neka förblir nekat, så vyn Link, trafikloggen och ändringarna i statusfältet visar verkliga ändringar.
- **Förberedelse.** Specifikationen skapar en användare genom onboarding-API:t, lägger till HS3 genom konfigurationsflödet i webbläsaren, lägger till H2 genom konfigurationsflödets API, slår på Tillåt styrning för båda systemen och lägger till en instrumentpanel per system med varje SAJ Local-kort och statusmärket, genom Home Assistants WebSocket-API.
- **Allt eller inget.** Specifikationen väntar upp till två minuter på att båda systemen rapporterar solenergi. Specifikationen skriver bilderna först när varje steg har klarats, så en misslyckad körning lämnar de incheckade bilderna som de var.
- **Väntan.** Specifikationen väntar på en skärm genom att kontrollera det tillstånd som skärmen visar, aldrig med en fast väntetid.
- **Reparation.** Reparationsskärmbilden visar reparationen för nekade register. Specifikationen lägger till en avfrågningsgrupp för växelriktarens temperatur med ett intervall på 10 sekunder, får simulatorn att neka det registret genom `POST /api/link` på simulatorsidan och väntar upp till två minuter tills `repairs/list_issues` listar SAJ Locals ärende `registers_refused`. Körningen misslyckas med ett meddelande som namnger det saknade ärendet när ärendet inte dyker upp.
- **Formulär.** Varningen vid prefixändring fångas och därefter stängs formuläret, vilket avbryter flödet, så inget prefix sparas. Varningen Tillåt styrning fångas och bekräftas sedan, eftersom korten behöver tillåten styrning.
- **Fel.** HTML-rapporten finns i `frontend/playwright-report/docs/`, och en misslyckad körning sparar Home Assistant-loggen som `frontend/test-results/docs/home-assistant.log`.

Skärmbilder jämförs inte pixel för pixel, varken i CI eller någon annanstans. Home Assistant renderar live-värden och typsnitt olika mellan körningar, så en pixeljämförelse skulle misslyckas utan en verklig ändring. Granska en ändrad bild genom att titta på bilden.

### Lägga till eller ändra en skärmbild

1. Lägg till eller ändra tagningen i specifikationen, med filnamnet i formen `<page>-<subject>.png`.
2. Referera bilden från den sida som förklarar ämnet.
3. Kör `make docs-images`, titta på de ändrade bilderna och checka in de ändrade bilderna.
4. Kör `make docs-check`. En bild som ingen sida refererar, och en länk till en bild som inte finns, rapporteras båda.

`make docs-images` är inte ett steg i `make ci`, och CI genererar inte bilderna på nytt. Kör målet före varje utgåva, se [sidan om utgåvor](releasing.md).

## Lägga till en sida

1. Skapa sidan under `docs/en-gb/user/` eller `docs/en-gb/developer/` och länka sidan från mappens index.
2. Länka sidan till det funktionslisteavsnitt vars rad `Files:` namnger den kod som sidan beskriver.
3. Lägg till sidan i raden för det avsnittet i Tabell över funktionstäckning, eller lägg till en rad. Ett nytt funktionslisteavsnitt behöver en rad innan `make docs-check` går igenom.
4. Kör `make docs-check`.

Håll sidorna användbara: länka till filen som håller ett faktum i stället för att kopiera faktumet, anteckna skälet till ett beslut eftersom skäl sällan ändras och detaljer ständigt, och håll exemplen få och kör varje exempel på nytt när exemplet ändras.

## Språk

Dokumentationen finns på engelska och på varje målspråk i de [globala kraven](../../../.github/work/requirements.md#language). Funktionslistorna och kravdokumenten förblir enbart engelska.

- **Struktur.** Varje språk har syskonmapparna `docs/<code>/user/`, `docs/<code>/developer/` och `docs/images/<code>/`, med samma filnamn i varje språk. Koderna är `en-gb`, `de`, `nl`, `fr`, `zh-hans`, `es`, `it`, `pl` och `sv`. Ett kodblock som är detsamma i flera språk blir kvar i texten på varje sida och omges av ett markörpar `jscpd:ignore-start` och `jscpd:ignore-end`, bara under ett undantag som användaren har godkänt i en plan, som `AGENTS.md` säger. Ett markörpar omger ett enda kodblock och inget annat.
- **Generator.** `make docs` skriver `docs/<code>/user/entities/` för varje språk från motsvarande fil i `custom_components/saj_local/translations/`. Utrustningsnamnen kommer från samma översättningsfil, och generatorns övriga texter från `.github/scripts/docs_text/<code>.json`.
- **Dokumentationskontroll.** `make docs-check` kör varje regel på varje språkmapp. [Tabell över funktionstäckning](#tabell-över-funktionstäckning) på denna sida gäller varje språk under samma sidnamn, och regeln för föräldralösa bilder kontrollerar `docs/images/<code>/` mot sidorna i samma språk.
- **Språkfält.** Första raden på varje sida under `docs/<code>/user/` och `docs/<code>/developer/`, de genererade entitetssidorna inräknade, är språkfältet `en | de | nl | fr | zh | es | it | pl | sv`, alltid i den ordningen. Varje etikett utom det aktuella språket länkar till samma sida i det språkets mapp, och det aktuella språket är vanlig text. `make docs` skriver språkfältet, och `make docs-check` rapporterar en sida vars första rad inte är det väntade språkfältet samt en länk i språkfältet till en sida som inte finns.
- **Översatt README.** `README.md` i arkivets rot förblir engelsk och är översatt i `docs/<code>/README.md`, vars länkar pekar på sidorna för det språket. Rot-`README.md` och varje `docs/<code>/README.md` har samma språkfält som första rad, och `make docs-check` rapporterar en saknad `docs/<code>/README.md`.
- **Skärmbilder.** `make docs-images` kör specifikationen en gång för varje språk, engelska först, med nya containrar för varje körning. `ARGS=<code>` väljer ett språk, se [Skärmbilder](#skärmbilder).
- **Nomenklatur.** Sidan `user/nomenclature.md` i varje språk är listan över termer som varje översättning av integrationen, korten och språkets sidor följer. Källan är den engelska sidan [Nomenklatur](../../en-gb/user/nomenclature.md).
- **Ändra engelskan.** En ändring av en engelsk text, sida eller skärmbild uppdaterar varje språk i samma ändring. Ingen kontroll håller språken i takt.

## Tabell över funktionstäckning

Varje funktionslisteavsnitt undersöks utifrån avsnittets rad `Files:` och täcks av de sidor som nämns här. Varje nämnd sida länkar till avsnittet via avsnittets rubrikankare. Ett sidnamn är relativt `docs/en-gb/` och länkar till sidan. Tabellen finns bara på den engelska sidan [Dokumentation](../../en-gb/developer/documentation.md#feature-coverage-table), och `docs-check` läser tabellen därifrån. Tabellen gäller i varje språk för samma sidnamn, och en sida som läggs till, slås ihop eller delas uppdaterar tabellen i samma ändring.

## Källor

| Faktum | Ägare |
| --- | --- |
| Vad SAJ Local gör, i en kort sammanfattning | [användarindexet](../user/README.md) |
| Vad varje del kan göra | de tre funktionslistorna |
| Modeller och utrustning som stöds | [utrustning som stöds](../user/supported-equipment.md) |
| Entitetsnamn, entitets-ID, modeller, utrustning och standardvärden | katalogen och `translations/en.json`, genom [entitetsreferensen](../user/entities/README.md) |
| Entitetstyper, regler för aktivering som standard och teckenkonventioner | integrationens funktionslisteavsnitt Enheter och entiteter |
| Utvecklingsmiljö | [miljö](environment.md) |
| Make-mål och kontrollregler | [kontroller](checks.md) |
| Utgåvor och höjning av Home Assistant-versionen | [utgåvor](releasing.md) |
| Skärmbild av översikten för webbplatsen | `docs/images/en-gb/cards-power-flow-card.png`, kopierad av underhållarna till projektets webbplats vid varje utgåva, se [sidan om utgåvor](releasing.md) |
| Hur ett säkerhetsproblem rapporteras | `SECURITY.md` |
| Ärendeetiketter och reglerna för etiketter | `.github/labels.yml` och `CONTRIBUTING.md` |
| Licensvillkor | `LICENSE` |
| Avsett produktbeteende | `.github/work/requirements.md` och de tre delarnas kravdokument |
