[en](../../en-gb/developer/checks.md) | [de](../../de/developer/checks.md) | [nl](../../nl/developer/checks.md) | [fr](../../fr/developer/checks.md) | [zh](../../zh-hans/developer/checks.md) | [es](../../es/developer/checks.md) | [it](../../it/developer/checks.md) | [pl](../../pl/developer/checks.md) | sv

# Kontroller

Vad varje make-mål kör, hur du avgränsar en körning och vilka regler varje kontroll följer.

## Make-mål

Varje åtgärd är ett make-mål och CI anropar samma mål, så att godkänt lokalt och godkänt i CI betyder samma sak. Ett nytt CI-steg börjar som ett make-mål. `make help` listar varje mål på en rad, och `make help ARGS=<target>` beskriver ett mål: vad målet kör, vad målet skriver ut vid lyckad och misslyckad körning, vad `ARGS` gör och, för ett samlingsmål, vilka steg målet kör.

`make ci` kör varje kontrollsteg och är definitionen av klart. GitHub kör själva `make ci` i det enda jobbet `checks` i [ci.yml](../../../.github/workflows/ci.yml), vid sidan av de delade jobben från `roquerodrigo/workflows` (`lint`, `tests`, `validate`), så ett steg som läggs till i `make ci` körs i GitHub utan någon ändring av arbetsflödet. Kör de smalare målen medan du itererar.

`make build` är det enda produktionsbygget av frontend. `make test` kör varje testsvit, och varje svit har ett eget mål så att en svit kan köras för sig:

| Mål | Svit |
| --- | --- |
| `make test-python` | Pytest-enhetstesterna för biblioteket, integrationen, simulatorn och kontrollkörningen, utan `tests/mock-integration` och `tests/scripts/test_runner_processes.py`, med täckningsgränsen på 100 % av rader och grenar. En full körning är två pytest-körningar till en gemensam täckningsfil med kärnan `ctrace` och en täckningskontext per test: `tests/saj`, `tests/mock` och `tests/scripts` utan Home Assistant-insticksmodulen och med blockerade sockets, därefter `tests/saj-integration` med insticksmodulen och gränsen på de kombinerade data. Steget misslyckas också för kroppen av varje test som tar över 200 ms, utan att fixturernas uppsättning och nedmontering räknas. |
| `make test-frontend` | Vitest-enhetstesterna för korten, med täckningsgränsen. |
| `make test-modules` | Varje modul med logik (varje funktion, metod eller gren) mot enbart de enhetstestfiler som är kopplade till modulen, med 100 % rad- och grentäckning krävd per modul. Gränsen läser täckningsdata från `make test-python`, så `make test-modules` kör `make test-python` först. En modul med logik och utan enhetstestfil misslyckas, och en modul utan logik, till exempel en tom modul eller en datatabell, hoppas över. |
| `make test-isolated` | Testerna i `tests/saj` och `tests/mock` i en miljö utan Home Assistant, vilket bevisar gränsen mellan biblioteket, simulatorn och Home Assistant. Täckningen kontrolleras för de moduler som testfilerna testar. |
| `make test-runner-processes` | Kontrollkörningens riktiga processtester i `tests/scripts/test_runner_processes.py`, som startar riktiga processer och ligger utanför täckningen. |
| `make test-browser-controlled` | Playwright mot det byggda paketet och kontrollerade data, utan Home Assistant. |
| `make test-browser-home-assistant` | Playwright mot en engångs-Home Assistant med en HS3-simulator och en H2-simulator, vilket bevisar att korten laddas och fungerar i det riktiga gränssnittet. Målet kör först `make build` och `make mock-build`, eftersom Home Assistant-avbilden kopierar kortpaketet från arbetsträdet och simulatorerna använder avbilden `saj-local-mock`. |
| `make mock-smoke` | Simulatorns container svarar en klient, därefter körs testerna i `tests/mock-integration`. Målet kör först `make mock-build` och kör scenarierna från avbilden `saj-local-mock`. |

Kontrollerna som utgör `make ci` har också ett mål var, så att ett verktyg kan köras för sig:

| Mål | Kontroll |
| --- | --- |
| `make ruff` | `ruff format --check` och `ruff check`. |
| `make mypy` | Den strikta typkontrollen. |
| `make import-lint` | Import-linter-kontrakten. |
| `make complexipy` | Gränsen för kognitiv komplexitet. |
| `make copy-paste` | jscpd-upptäckt av duplicerad kod och text, över hela arkivet inklusive `docs/`. |
| `make prettier`, `make tsc`, `make eslint` | Formatering, typkontroll och lint av frontend. |
| `make build` | Vites produktionsbygge av frontend. |
| `make release-check` | HACS-arkivet innehåller `asset-manifest.json` och det byggda kortpaketet. Arkivet görs av filerna i `custom_components/saj_local/`, så det byggda paketet måste finnas i trädet. Versionen i `custom_components/saj_local/manifest.json`, `pyproject.toml` och `frontend/package.json` är `X.Y.Z` eller `X.Y.ZbN` och densamma i alla tre filerna, och en tagg vid `HEAD` är lika med versionen. Utan tagg vid `HEAD` hoppas jämförelsen med taggen över. |
| `make freeze-check` | Ingen entitetsnyckel, inget entitets-ID, ingen sparad inställningsnyckel och ingen korttyp tas bort, och ingen entitetsplattform, enhet, enhetsklass, tillståndsklass eller tillståndsvärde ändras, jämfört med den senaste stabila versionstaggen. Betataggar hoppas över, så en beta fryser aldrig ytan. Utan stabil versionstagg går steget igenom. |
| `make docs-check` | Den genererade entitetsreferensen, länkar, bilder, sidlängd, täckningen av funktionslistan och språkfältet. Se [dokumentationssidan](documentation.md#kontroller). |
| `make template-check` | `bug.yml` kräver diagnostiknedladdningen, varje etikett som en ärendemall sätter eller länkar finns i `.github/labels.yml`, och modellrullgardinen i `bug.yml` stämmer med modellerna i `translations/en.json`. |
| `make mock-build` | Simulatoravbilden byggs och innehåller ingen bytekod. |
| `make validate` | hassfest mot arbetsträdet, i Docker. HACS-valideringen läser det pushade arkivet, så bara arbetsflödesjobbet `validate` kör HACS-valideringen. |

`make lint`, `make python-ci`, `make frontend-check` och `make frontend-ci` kör grupper av dessa mål.

Fyra mål till är inte kontroller. `make setup` installerar Python- och frontend-beroendena och Chromium, `make docs` genererar entitetsreferensen på nytt, `make docs-images` tar dokumentationens skärmbilder, kör först `make build` och `make mock-build` som Home Assistant-webbläsartestet och är inte ett steg i `make ci`, och `make up`, `make down` och `make logs` kör utvecklings-Home Assistant, se [miljösidan](environment.md#kör-home-assistant).

Varje mål körs genom kontrollkörningen i `.github/scripts/`. Kontrollkörningen skriver ut en rad `[x]` eller `[ ]` per steg, fynden i ett misslyckat steg som `file:line message` och en slutrad med resultatet. Kontrollkörningen kör varje valt steg även efter att ett har misslyckats och rapporterar en tidsgräns, en signal eller ett saknat verktyg som sådant. Varje steg har en tidsgräns. Den sparsamma utskriften finns så att en person eller en agent läser bara det som behövs för att åtgärda ett fel.

GitHub Actions är fästa vid en incheckningshash så att en flyttad tagg inte kan ändra vad CI kör.

## Alternativ

- `ARGS="..."` skickar sökvägar och alternativ till ett mål med ett enda verktyg, till exempel `make test-python ARGS="tests/saj/test_poller.py -k decode"` eller `make ruff ARGS="custom_components/saj_local/coordinator.py"`. `make help ARGS=<target>` anger vad `ARGS` gör för varje mål.
- `ONLY=<step,...>` kör en delmängd av stegen i ett samlingsmål, till exempel `make ci ONLY=ruff,mypy`. Ett namn som målet inte kör är ett fel.
- `V=1` strömmar verktygets råa utskrift och stänger av den sparsamma verktygskonfigurationen och miljöinställningarna för den körningen.

## Täckning vid delkörning

En full `make test-python` mäter och kontrollerar hela paketet. När `ARGS` väljer testfiler eller mappar mäter målet täckning bara för de moduler som testfilerna testar, lägger till de andra enhetstestfilerna som är kopplade till dessa moduler i körningen och tillämpar samma gräns på 100 % på dessa moduler. En körning av `tests/saj-integration/test_coordinator_write.py` kör därför också `test_coordinator.py` och `test_coordinator_power.py` och kontrollerar `coordinator.py`. Modulen är filen med testfilens namn utan prefixet `test_`, uppslagen efter testmapp:

[Tabellen över testmappar och modulmappar](../../en-gb/developer/checks.md#coverage-of-a-subset-run) finns på den engelska sidan.

Testfiler utan modul med samma namn listas i `.github/scripts/pytest_scope.json`, var och en med de moduler som filen testar, och en testfil utan känd modul avvisas tills filen läggs till där. Mappningen av mappar finns i `.github/scripts/pytest_scope.py`. Att välja tester med `-k`, `-m` eller `--lf` kräver en testfil i `ARGS`, så att täckningen kan kontrolleras för den modul som filen testar.

En full `make test-python` registrerar vilket test som körde varje rad och gren (en täckningskontext per test), så att en körning matar båda gränserna. Kärnan `ctrace` sätts bara för den fulla körningen, i miljön för dess kommandon, eftersom standardkärnan `sysmon` registrerar en rad för det första test som kör raden och därmed lämnar senare test utan kontext. Samma fulla körning mäter varaktigheten för varje testkropp, och varje kropp över 200 ms får steget att misslyckas med test-ID och tid. 200 ms under täckning är ungefär 50 ms i en vanlig körning, över de 125 ms som friska test når under täckning, så gränsen misslyckas inte slumpmässigt. En delkörning behåller kärnan `sysmon`, registrerar inga kontexter och tillämpar ingen tidsgräns.

`test-modules` körs i `make ci` och kontrollerar varje modul mot 100 % rad- och grentäckning från enbart de enhetstestfiler som är kopplade till modulen. Gränsen räknar bara kontexterna för dessa testfiler och koden som körs när modulen importeras, så täckning från andra modulers test räknas inte. `test-modules` läser täckningsdata från `test-python`, så `make test-modules` ensamt kör `test-python` först och `make ci` kör testerna en gång. En modul med logik och utan enhetstestfil får steget att misslyckas, och en modul utan logik hoppas över, eftersom kraven förbjuder tester av konstanter. En modul som bara klarar gränsen i den fulla körningen av `test-python` betyder att andra test täcker modulen av en slump, och det är en verklig lucka att åtgärda. `test-isolated` kontrollerar täckningen på samma sätt som en delkörning.

## Testning

Reglerna finns i [avsnittet Testning i de globala kraven](../../../.github/work/requirements.md#testing). Skälen:

- **Täckning räknar bara enhetstester.** Ett test som kopplar ihop riktiga moduler höjer siffran utan att bevisa någon av modulerna.
- **Enhetstester är snabba och isolerade.** Inga sockets, servrar, fixturfiler, verklig tid eller långa simuleringar. Tid, slumptal och in- och utdata injiceras genom hela koden av just det skälet.
- **Integrationstester bevisar bara att delarna kopplas ihop.** För simulatorn är integrationstestet `make mock-smoke`.
- **Inga omvägar i koden** förbi lint-, typ- eller täckningskontroller. Ändra konfigurationen, där beslutet syns, eller strukturera om koden.
- **Testa beteende, inte konstanter.** Ett test som upprepar en registeradress bevisar ingenting.

`tests/` innehåller exakt sex mappar:

- `tests/saj`: enhetstester av SAJ-biblioteket.
- `tests/saj-integration`: enhetstester av Home Assistant-integrationen, inte integrationstester.
- `tests/mock`: enhetstester av Modbus-simulatorn, med `profiles/` och `simulation/`.
- `tests/mock-integration`: containerns smoke-skript och testet av simulatorns levererade scenarier.
- `tests/playwright`: Docker-skripten för webbläsartesterna.
- `tests/scripts`: enhetstesterna för kontrollkörningen, och dess riktiga processtester i `test_runner_processes.py`.

`tests/mock-integration` och `tests/scripts/test_runner_processes.py` ligger utanför enhetskörningen och utanför täckningen.

## Stack

| Del | Varför |
| --- | --- |
| Python med `uv` | En låsfil, samma installationer lokalt och i CI. |
| Ruff, alla regler på | Varje undantag är ett synligt beslut i `[tool.ruff.lint]`. |
| mypy | Registeravkodning inbjuder till fel i skalning, tecken och bredd som typer fångar. |
| import-linter | Gör gränserna på [arkitektursidan](architecture.md#så-är-projektet-uppdelat) till en kontroll som kan misslyckas. |
| complexipy, jscpd | Kod för registerkartor växer genom duplicering; gränserna stoppar tillväxten. |
| pytest, 100 procent grentäckning | Se [Testning](#testning). |
| Lit, TypeScript, Vite | Home Assistants frontend är Lit, så korten behöver inget annat ramverk. |
| Playwright | Styr korten i en riktig webbläsare och i en riktig Home Assistant, och tar [dokumentationens skärmbilder](documentation.md#skärmbilder). |
| Docker Compose | Se [miljösidan](environment.md#docker). |

Home Assistant är fastlåst i flera filer som måste ändras tillsammans, annars kör lint och tester mot olika kärnor. Stegen finns på [sidan om utgåvor](releasing.md#höja-home-assistant-versionen).
