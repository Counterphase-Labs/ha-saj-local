[en](../../en-gb/developer/checks.md) | [de](../../de/developer/checks.md) | nl | [fr](../../fr/developer/checks.md) | [zh](../../zh-hans/developer/checks.md) | [es](../../es/developer/checks.md) | [it](../../it/developer/checks.md) | [pl](../../pl/developer/checks.md) | [sv](../../sv/developer/checks.md)

# Controles

Wat elke make-target draait, hoe u een run beperkt en de regels die elke controle volgt.

## Make-targets

Elke actie is een make-target en CI roept dezelfde targets aan, dus lokaal slagen en in CI slagen betekenen hetzelfde. Een nieuwe CI-stap begint als make-target. `make help` vermeldt elke target met één regel, en `make help ARGS=<target>` beschrijft één target: wat de target draait, wat de target bij succes en bij falen afdrukt, wat `ARGS` doet en, voor een groeperende target, de stappen die de target draait.

`make ci` draait elke controlestap en is de definitie van klaar. GitHub draait `make ci` zelf in de ene job `checks` van [ci.yml](../../../.github/workflows/ci.yml), naast de gedeelde `roquerodrigo/workflows`-jobs (`lint`, `tests`, `validate`), dus een stap die aan `make ci` wordt toegevoegd draait in GitHub zonder workflowwijziging. Draai de smallere targets tijdens het itereren.

`make build` is de ene productiebuild van de frontend. `make test` draait elke testsuite, en elke suite heeft een eigen target zodat één suite alleen kan worden gedraaid:

| Target | Suite |
| --- | --- |
| `make test-python` | De pytest-unittests van de bibliotheek, de integratie, de simulator en de controlerunner, zonder `tests/mock-integration` en `tests/scripts/test_runner_processes.py`, met de dekkingsdrempel van 100 % voor regels en branches. Een volledige run is twee pytest-runs in één dekkingsgegevensbestand met de `ctrace`-kern en een dekkingscontext per test: `tests/saj`, `tests/mock` en `tests/scripts` zonder de Home Assistant-plugin en met sockets geblokkeerd, dan `tests/saj-integration` met de plugin en de drempel op de gecombineerde gegevens. De stap faalt ook voor de body van elke test die langer dan 200 ms duurt, zonder de opzet en afbraak van fixtures. |
| `make test-frontend` | De Vitest-unittests van de kaarten, met de dekkingsdrempel. |
| `make test-modules` | Elke module met logica (elke functie, methode of branch) tegen alleen de unittestbestanden die aan de module zijn gekoppeld, met per module 100 % regel- en branchdekking vereist. De drempel leest de dekkingsgegevens van `make test-python`, dus `make test-modules` draait eerst `make test-python`. Een module met logica en zonder unittestbestand faalt, en een module zonder logica, zoals een lege module of een gegevenstabel, wordt overgeslagen. |
| `make test-isolated` | De tests van `tests/saj` en `tests/mock` in een omgeving zonder Home Assistant, wat de grens tussen de bibliotheek, de simulator en Home Assistant bewijst. Dekking wordt afgedwongen op de modules die de testbestanden testen. |
| `make test-runner-processes` | De echte-procestests van de controlerunner in `tests/scripts/test_runner_processes.py`, die echte processen starten en buiten de dekking vallen. |
| `make test-browser-controlled` | Playwright tegen de gebouwde bundel en gecontroleerde gegevens, zonder Home Assistant. |
| `make test-browser-home-assistant` | Playwright tegen een wegwerp-Home Assistant met een HS3-simulator en een H2-simulator, wat bewijst dat de kaarten laden en werken in de echte frontend. De target draait eerst `make build` en `make mock-build`, omdat het Home Assistant-image de kaartbundel uit de werkboom kopieert en de simulators het image `saj-local-mock` gebruiken. |
| `make mock-smoke` | De simulatorcontainer beantwoordt een client, daarna draaien de tests in `tests/mock-integration`. De target draait eerst `make mock-build` en draait de scenario's uit het image `saj-local-mock`. |

De controles die `make ci` vormen hebben ook elk een target, zodat één tool alleen kan worden gedraaid:

| Target | Controle |
| --- | --- |
| `make ruff` | `ruff format --check` en `ruff check`. |
| `make mypy` | De strikte typecontrole. |
| `make import-lint` | De import-linter-contracten. |
| `make complexipy` | De limiet voor cognitieve complexiteit. |
| `make copy-paste` | jscpd-detectie van dubbele code en tekst, over de hele repository inclusief `docs/`. |
| `make prettier`, `make tsc`, `make eslint` | Opmaak, typecontrole en lint van de frontend. |
| `make build` | De Vite-productiebuild van de frontend. |
| `make release-check` | Het HACS-archief bevat `asset-manifest.json` en de gebouwde kaartbundel. Het archief wordt gemaakt van de bestanden in `custom_components/saj_local/`, dus de gebouwde bundel moet in de boom staan. De versie in `custom_components/saj_local/manifest.json`, `pyproject.toml` en `frontend/package.json` is `X.Y.Z` of `X.Y.ZbN` en gelijk in alle drie de bestanden, en een tag op `HEAD` is gelijk aan de versie. Zonder tag op `HEAD` wordt de tagvergelijking overgeslagen. |
| `make freeze-check` | Er wordt geen entiteitssleutel, entiteits-ID, opgeslagen instellingssleutel of kaarttype verwijderd, en geen entiteitsplatform, eenheid, apparaatklasse, statusklasse of statuswaarde verandert, vergeleken met de nieuwste stabiele releasetag. Bètatags worden overgeslagen, dus een bèta bevriest het oppervlak nooit. Zonder stabiele releasetag slaagt de stap. |
| `make docs-check` | Het gegenereerde entiteitenoverzicht, links, afbeeldingen, paginalengte, dekking van de functielijsten en de taalbalk. Zie de [documentatiepagina](documentation.md#controles). |
| `make template-check` | `bug.yml` vereist de diagnosedownload, elk label dat een issuesjabloon toepast of waarnaar het linkt bestaat in `.github/labels.yml`, en de modeldropdown van `bug.yml` komt overeen met de modellen in `translations/en.json`. |
| `make mock-build` | Het simulatorimage bouwt en bevat geen bytecode. |
| `make validate` | hassfest tegen de werkboom, in Docker. De HACS-validatie leest de gepushte repository, dus alleen de workflowjob `validate` draait de HACS-validatie. |

`make lint`, `make python-ci`, `make frontend-check` en `make frontend-ci` draaien groepen van deze targets.

Vier andere targets zijn geen controles. `make setup` installeert de Python- en frontend-afhankelijkheden en Chromium, `make docs` regenereert het entiteitenoverzicht, `make docs-images` maakt de documentatieschermafbeeldingen, draait eerst `make build` en `make mock-build` zoals de Home Assistant-browsertest, en is geen stap van `make ci`, en `make up`, `make down` en `make logs` draaien de ontwikkel-Home Assistant, zie de [omgevingspagina](environment.md#home-assistant-draaien).

Elke target draait via de controlerunner in `.github/scripts/`. De runner drukt één regel `[x]` of `[ ]` per stap af, de bevindingen van een falende stap als `file:line message`, en een slotregel met het resultaat. De runner draait elke geselecteerde stap ook nadat er een faalt, en meldt een time-out, een signaal of een ontbrekende tool als zodanig. Elke stap heeft een tijdslimiet. De stille uitvoer bestaat zodat een persoon of een agent alleen leest wat nodig is om een falen te herstellen.

GitHub Actions zijn vastgepind op een commit-hash, zodat een verplaatste tag niet kan wijzigen wat CI draait.

## Opties

- `ARGS="..."` geeft paden en opties door aan een target voor één tool, bijvoorbeeld `make test-python ARGS="tests/saj/test_poller.py -k decode"` of `make ruff ARGS="custom_components/saj_local/coordinator.py"`. `make help ARGS=<target>` zegt wat `ARGS` voor elke target doet.
- `ONLY=<step,...>` draait een deelverzameling van de stappen van een groeperende target, bijvoorbeeld `make ci ONLY=ruff,mypy`. Een naam die de target niet draait is een fout.
- `V=1` streamt de ruwe toolevoer en schakelt de spaarzame toolconfiguratie en omgevingsinstellingen voor die run uit.

## Dekking van een deelrun

Een volledige `make test-python` meet en bewaakt het hele pakket. Wanneer `ARGS` testbestanden of -mappen selecteert, meet de target de dekking alleen voor de modules die de testbestanden testen, voegt de andere unittestbestanden die aan die modules zijn gekoppeld toe aan de run, en past dezelfde drempel van 100 % toe op die modules. Een run van `tests/saj-integration/test_coordinator_write.py` draait dus ook `test_coordinator.py` en `test_coordinator_power.py` en bewaakt `coordinator.py`. De module is het bestand met de naam van het testbestand zonder het voorvoegsel `test_`, opgezocht per testmap:

De [tabel met testmappen en modulemappen](../../en-gb/developer/checks.md#coverage-of-a-subset-run) staat op de Engelse pagina.

Testbestanden zonder module met dezelfde naam staan in `.github/scripts/pytest_scope.json`, elk met de modules die het bestand test, en een testbestand zonder bekende module wordt geweigerd totdat het bestand daar is toegevoegd. De mapkoppeling staat in `.github/scripts/pytest_scope.py`. Tests selecteren met `-k`, `-m` of `--lf` heeft een testbestand in `ARGS` nodig, zodat dekking kan worden bewaakt op de module die het bestand test.

Een volledige `make test-python` registreert welke test elke regel en branch draaide (een dekkingscontext per test), zodat één run beide drempels voedt. De `ctrace`-kern wordt alleen voor de volledige run ingesteld, in de omgeving van de commando's, omdat de standaardkern `sysmon` een regel registreert voor de eerste test die de regel draait en latere tests zo zonder context laat. Dezelfde volledige run meet de duur van elke testbody, en elke body boven 200 ms faalt de stap met de test-ID en de tijd. 200 ms onder dekking is ongeveer 50 ms in een normale run, boven de 125 ms die gezonde tests onder dekking halen, zodat de drempel niet willekeurig faalt. Een deelrun houdt de kern `sysmon`, registreert geen contexten en past geen duurdrempel toe.

`test-modules` draait in `make ci` en bewaakt elke module op 100 % regel- en branchdekking uit alleen de unittestbestanden die aan de module zijn gekoppeld. De drempel telt alleen de contexten van die testbestanden en de code die draait wanneer de module wordt geïmporteerd, dus dekking uit de tests van andere modules telt niet mee. `test-modules` leest de dekkingsgegevens van `test-python`, dus `make test-modules` alleen draait eerst `test-python` en `make ci` draait de tests één keer. Een module met logica en zonder unittestbestand faalt de stap, en een module zonder logica wordt overgeslagen, omdat de requirements tests van constanten verbieden. Een module die de drempel alleen haalt in de volledige run van `test-python` betekent dat andere tests de module bij toeval dekken, en dat is een echte lacune om te herstellen. `test-isolated` bewaakt dekking op dezelfde manier als elke deelrun.

## Testen

De regels staan in de [sectie Testen van de globale requirements](../../../.github/work/requirements.md#testing). De redenen:

- **Dekking telt alleen unittests.** Een test die echte modules aan elkaar koppelt verhoogt het cijfer zonder één van de modules te bewijzen.
- **Unittests zijn snel en geïsoleerd.** Geen sockets, servers, fixturebestanden, echte tijd of lange simulaties. Tijd, toeval en I/O worden daarom overal in de code geïnjecteerd.
- **Integratietests bewijzen alleen dat onderdelen koppelen.** Voor de simulator is de integratietest `make mock-smoke`.
- **Geen inline omzeilingen** van lint-, type- of dekkingscontroles. Wijzig de configuratie, waar de beslissing zichtbaar is, of herstructureer de code.
- **Toets gedrag, geen constanten.** Een test die een registeradres herhaalt bewijst niets.

`tests/` bevat precies zes mappen:

- `tests/saj`: unittests van de SAJ-bibliotheek.
- `tests/saj-integration`: unittests van de Home Assistant-integratie, geen integratietests.
- `tests/mock`: unittests van de Modbus-simulator, met `profiles/` en `simulation/`.
- `tests/mock-integration`: het containersmokescript en de test van het meegeleverde scenario van de simulator.
- `tests/playwright`: de Docker-scripts voor de browsertests.
- `tests/scripts`: de unittests van de controlerunner, en de echte-procestests ervan in `test_runner_processes.py`.

`tests/mock-integration` en `tests/scripts/test_runner_processes.py` vallen buiten de unitrun en buiten de dekking.

## Stack

| Onderdeel | Waarom |
| --- | --- |
| Python met `uv` | Eén lockbestand, dezelfde installaties lokaal en in CI. |
| Ruff, alle regels aan | Elke uitzondering is een zichtbare beslissing in `[tool.ruff.lint]`. |
| mypy | Registerdecodering nodigt uit tot schaal-, teken- en breedtefouten die typen vangen. |
| import-linter | Maakt de grenzen op de [architectuurpagina](architecture.md#hoe-het-project-is-verdeeld) tot een falende controle. |
| complexipy, jscpd | Code voor registerkaarten groeit door duplicatie; de limieten stoppen de groei. |
| pytest, 100 procent branchdekking | Zie [Testen](#testen). |
| Lit, TypeScript, Vite | De frontend van Home Assistant is Lit, dus de kaarten hebben geen tweede framework nodig. |
| Playwright | Stuurt de kaarten aan in een echte browser en in een echte Home Assistant, en maakt de [documentatieschermafbeeldingen](documentation.md#schermafbeeldingen). |
| Docker Compose | Zie de [omgevingspagina](environment.md#docker). |

Home Assistant is in meerdere bestanden vastgepind die samen moeten veranderen, anders draaien lint en tests tegen verschillende kernen. De stappen staan op de [pagina Releasen](releasing.md#de-home-assistant-versie-ophogen).
