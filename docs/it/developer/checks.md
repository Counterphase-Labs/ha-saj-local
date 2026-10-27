[en](../../en-gb/developer/checks.md) | [de](../../de/developer/checks.md) | [nl](../../nl/developer/checks.md) | [fr](../../fr/developer/checks.md) | [zh](../../zh-hans/developer/checks.md) | [es](../../es/developer/checks.md) | it | [pl](../../pl/developer/checks.md) | [sv](../../sv/developer/checks.md)

# Controlli

Che cosa esegue ogni target make, come restringere un'esecuzione e le regole che ogni controllo segue.

## Target make

Ogni azione è un target make e la CI chiama gli stessi target, quindi superare i controlli in locale e superarli nella CI significano la stessa cosa. Un nuovo passaggio della CI parte come target make. `make help` elenca ogni target con una riga, e `make help ARGS=<target>` descrive un target: che cosa esegue il target, che cosa stampa il target in caso di successo e di fallimento, che cosa fa `ARGS` e, per un target di raggruppamento, i passaggi che il target esegue.

`make ci` esegue ogni passaggio di controllo ed è la definizione di completato. GitHub esegue `make ci` stesso nell'unico job `checks` di [ci.yml](../../../.github/workflows/ci.yml), insieme ai job condivisi di `roquerodrigo/workflows` (`lint`, `tests`, `validate`) e al job `hacs`, quindi un passaggio aggiunto a `make ci` viene eseguito in GitHub senza modifiche al workflow. Esegui i target più ristretti mentre iteri.

`make build` è l'unica build di produzione del frontend. `make test` esegue ogni suite di test, e ogni suite ha il proprio target così una suite può essere eseguita da sola:

| Target | Suite |
| --- | --- |
| `make test-python` | I test unitari pytest della libreria, dell'integrazione, del simulatore e dell'esecutore dei controlli, senza `tests/mock-integration` e `tests/scripts/test_runner_processes.py`, con la soglia di copertura del 100 % di righe e rami. Un'esecuzione completa consiste in due esecuzioni pytest in un unico file di dati di copertura con il core `ctrace` e un contesto di copertura per test: `tests/saj`, `tests/mock` e `tests/scripts` senza il plugin di Home Assistant e con i socket bloccati, poi `tests/saj-integration` con il plugin e la soglia sui dati combinati. Il passaggio fallisce anche per il corpo di qualsiasi test che richiede più di 200 ms, senza contare la preparazione e lo smontaggio delle fixture. |
| `make test-frontend` | I test unitari Vitest delle schede, con la soglia di copertura. |
| `make test-modules` | Ogni modulo con logica (qualsiasi funzione, metodo o ramo) rispetto ai soli file di test unitari associati al modulo, con copertura del 100 % di righe e rami richiesta per modulo. La soglia legge i dati di copertura di `make test-python`, quindi `make test-modules` esegue prima `make test-python`. Un modulo con logica e senza file di test unitari fallisce, e un modulo senza logica, come un modulo vuoto o una tabella di dati, viene saltato. |
| `make test-isolated` | I test `tests/saj` e `tests/mock` in un ambiente senza Home Assistant, che dimostra il confine tra la libreria, il simulatore e Home Assistant. La copertura è vincolata sui moduli che i file di test testano. |
| `make test-runner-processes` | I test con processi reali dell'esecutore dei controlli in `tests/scripts/test_runner_processes.py`, che avviano processi reali e sono fuori dalla copertura. |
| `make test-browser-controlled` | Playwright sulla build del bundle e su dati controllati, senza Home Assistant. |
| `make test-browser-home-assistant` | Playwright su un Home Assistant usa e getta con un simulatore HS3 e un simulatore H2, che dimostra che le schede si caricano e funzionano nel frontend reale. Il target esegue prima `make build` e `make mock-build`, perché l'immagine di Home Assistant copia il bundle delle schede dall'albero di lavoro e i simulatori usano l'immagine `saj-local-mock`. |
| `make mock-smoke` | Il contenitore del simulatore risponde a un client, poi vengono eseguiti i test in `tests/mock-integration`. Il target esegue prima `make mock-build` ed esegue gli scenari dall'immagine `saj-local-mock`. |

Anche i controlli che compongono `make ci` hanno un target ciascuno, così uno strumento può essere eseguito da solo:

| Target | Controllo |
| --- | --- |
| `make ruff` | `ruff format --check` e `ruff check`. |
| `make mypy` | Il controllo dei tipi rigoroso. |
| `make import-lint` | I contratti di import-linter. |
| `make complexipy` | Il limite di complessità cognitiva. |
| `make copy-paste` | Il rilevamento jscpd di codice e testo duplicati, sull'intero repository compreso `docs/`. |
| `make prettier`, `make tsc`, `make eslint` | Formattazione, controllo dei tipi e lint del frontend. |
| `make build` | La build di produzione Vite del frontend. |
| `make release-check` | L'archivio HACS contiene `asset-manifest.json` e il bundle delle schede compilato. L'archivio viene creato dai file in `custom_components/saj_local/`, quindi il bundle compilato deve essere nell'albero. La versione in `custom_components/saj_local/manifest.json`, `pyproject.toml` e `frontend/package.json` è `X.Y.Z` o `X.Y.ZbN` e uguale in tutti e tre i file, e un tag su `HEAD` è uguale alla versione. Senza tag su `HEAD` il confronto con il tag viene saltato. |
| `make freeze-check` | Nessuna chiave di entità, ID entità, chiave di impostazione memorizzata o tipo di scheda viene rimosso, e nessuna piattaforma di entità, unità, classe di dispositivo, classe di stato o valore di stato cambia, rispetto al tag della versione stabile più recente. I tag beta vengono saltati, quindi una beta non congela mai la superficie. Senza un tag di versione stabile il passaggio riesce. |
| `make docs-check` | Il riferimento delle entità generato, i collegamenti, le immagini, la lunghezza delle pagine, la copertura dell'elenco delle funzionalità e la barra delle lingue. Vedi la [pagina della documentazione](documentation.md#controlli). |
| `make template-check` | `bug.yml` richiede il download della diagnostica, ogni etichetta che un modulo di segnalazione applica o collega esiste in `.github/labels.yml`, e il menu a discesa del modello di `bug.yml` corrisponde ai modelli in `translations/en.json`. |
| `make mock-build` | L'immagine del simulatore si costruisce e non contiene bytecode. |
| `make validate` | hassfest sull'albero di lavoro, in Docker. La convalida HACS legge il repository pubblicato, quindi solo il job `hacs` del workflow esegue la convalida HACS. |

`make lint`, `make python-ci`, `make frontend-check` e `make frontend-ci` eseguono gruppi di questi target.

Altri quattro target non sono controlli. `make setup` installa le dipendenze Python e frontend e Chromium, `make docs` rigenera il riferimento delle entità, `make docs-images` crea le schermate della documentazione, esegue prima `make build` e `make mock-build` come il test del browser con Home Assistant, e non è un passaggio di `make ci`, e `make up`, `make down` e `make logs` eseguono l'Home Assistant di sviluppo, vedi la [pagina dell'ambiente](environment.md#eseguire-home-assistant).

Ogni target passa dall'esecutore dei controlli in `.github/scripts/`. L'esecutore stampa una riga `[x]` o `[ ]` per passaggio, i risultati di un passaggio fallito come `file:line message`, e una riga finale con il risultato. L'esecutore esegue ogni passaggio selezionato anche dopo che uno fallisce, e segnala come tali un timeout, un segnale o uno strumento mancante. Ogni passaggio ha un limite di tempo. L'output sobrio esiste perché una persona o un agente legga solo ciò che serve per correggere un fallimento.

Le GitHub Actions sono fissate a un hash di commit, così un tag spostato non può cambiare ciò che esegue la CI.

## Opzioni

- `ARGS="..."` passa percorsi e opzioni a un target di un singolo strumento, per esempio `make test-python ARGS="tests/saj/test_poller.py -k decode"` o `make ruff ARGS="custom_components/saj_local/coordinator.py"`. `make help ARGS=<target>` indica che cosa fa `ARGS` per ogni target.
- `ONLY=<step,...>` esegue un sottoinsieme dei passaggi di un target di raggruppamento, per esempio `make ci ONLY=ruff,mypy`. Un nome che il target non esegue è un errore.
- `V=1` trasmette l'output grezzo dello strumento e disattiva la configurazione sobria degli strumenti e le impostazioni dell'ambiente per quell'esecuzione.

## Copertura di un'esecuzione parziale

Un `make test-python` completo misura e vincola l'intero pacchetto. Quando `ARGS` seleziona file o cartelle di test, il target misura la copertura solo per i moduli che i file di test testano, aggiunge all'esecuzione gli altri file di test unitari associati a quei moduli, e applica la stessa soglia del 100 % a quei moduli. Un'esecuzione di `tests/saj-integration/test_coordinator_write.py` esegue quindi anche `test_coordinator.py` e `test_coordinator_power.py` e vincola `coordinator.py`. Il modulo è il file con il nome del file di test senza il prefisso `test_`, cercato per cartella di test:

La [tabella delle cartelle di test e delle cartelle dei moduli](../../en-gb/developer/checks.md#coverage-of-a-subset-run) si trova nella pagina in inglese.

I file di test senza un modulo con lo stesso nome sono elencati in `.github/scripts/pytest_scope.json`, ciascuno con i moduli che il file testa, e un file di test senza un modulo noto viene rifiutato finché il file non viene aggiunto lì. L'associazione per cartella è in `.github/scripts/pytest_scope.py`. Selezionare test con `-k`, `-m` o `--lf` richiede un file di test in `ARGS`, così la copertura può essere vincolata sul modulo che il file testa.

Un `make test-python` completo registra quale test ha eseguito ogni riga e ramo (un contesto di copertura per test), così un'esecuzione alimenta entrambe le soglie. Il core `ctrace` è impostato solo per l'esecuzione completa, nell'ambiente dei suoi comandi, perché il core `sysmon` predefinito registra una riga per il primo test che la esegue e lascia così i test successivi senza un contesto. La stessa esecuzione completa misura la durata del corpo di ogni test, e qualsiasi corpo sopra i 200 ms fa fallire il passaggio con l'ID del test e il tempo. 200 ms sotto copertura sono circa 50 ms in un'esecuzione normale, sopra i 125 ms che i test sani raggiungono sotto copertura, quindi la soglia non fallisce a caso. Un'esecuzione parziale mantiene il core `sysmon`, non registra contesti e non applica alcuna soglia di durata.

`test-modules` viene eseguito in `make ci` e vincola ogni modulo al 100 % di copertura di righe e rami dai soli file di test unitari associati al modulo. La soglia conta solo i contesti di quei file di test e il codice eseguito quando il modulo viene importato, quindi la copertura dai test di altri moduli non conta. `test-modules` legge i dati di copertura di `test-python`, quindi `make test-modules` da solo esegue prima `test-python` e `make ci` esegue i test una volta. Un modulo con logica e senza file di test unitari fa fallire il passaggio, e un modulo senza logica viene saltato, perché i requisiti vietano i test delle costanti. Un modulo che supera la soglia solo nell'esecuzione completa di `test-python` significa che altri test coprono il modulo per caso, ed è una lacuna reale da correggere. `test-isolated` vincola la copertura come qualsiasi esecuzione parziale.

## Test

Le regole sono nella [sezione Test dei requisiti globali](../../../.github/work/requirements.md#testing). I motivi:

- **La copertura conta solo i test unitari.** Un test che collega moduli reali tra loro alza la cifra senza dimostrare nessuno dei moduli.
- **I test unitari sono veloci e isolati.** Niente socket, server, file di fixture, tempo reale o simulazioni lunghe. Tempo, casualità e I/O vengono iniettati in tutto il codice per questo motivo.
- **I test di integrazione dimostrano solo che le parti si collegano.** Per il simulatore il test di integrazione è `make mock-smoke`.
- **Nessuna scappatoia inline** ai controlli di lint, di tipo o di copertura. Cambia la configurazione, dove la decisione è visibile, o ristruttura il codice.
- **Verifica il comportamento, non le costanti.** Un test che ripete l'indirizzo di un registro non dimostra nulla.

`tests/` contiene esattamente sei cartelle:

- `tests/saj`: test unitari della libreria SAJ.
- `tests/saj-integration`: test unitari dell'integrazione Home Assistant, non test di integrazione.
- `tests/mock`: test unitari del simulatore Modbus, con `profiles/` e `simulation/`.
- `tests/mock-integration`: lo script smoke del contenitore e il test dello scenario distribuito del simulatore.
- `tests/playwright`: gli script Docker per i test del browser.
- `tests/scripts`: i test unitari dell'esecutore dei controlli, e i suoi test con processi reali in `test_runner_processes.py`.

`tests/mock-integration` e `tests/scripts/test_runner_processes.py` sono fuori dall'esecuzione unitaria e fuori dalla copertura.

## Stack

| Elemento | Perché |
| --- | --- |
| Python con `uv` | Un solo file di lock, le stesse installazioni in locale e nella CI. |
| Ruff, tutte le regole attive | Ogni eccezione è una decisione visibile in `[tool.ruff.lint]`. |
| mypy | La decodifica dei registri invita a errori di scala, segno e larghezza che i tipi intercettano. |
| import-linter | Rende i confini nella [pagina dell'architettura](architecture.md#come-è-suddiviso-il-progetto) un controllo che può fallire. |
| complexipy, jscpd | Il codice della mappa dei registri cresce per duplicazione; i limiti fermano la crescita. |
| pytest, copertura dei rami al 100 per cento | Vedi [Test](#test). |
| Lit, TypeScript, Vite | Il frontend di Home Assistant è Lit, quindi le schede non hanno bisogno di un secondo framework. |
| Playwright | Pilota le schede in un browser reale e in un Home Assistant reale, e crea le [schermate della documentazione](documentation.md#schermate). |
| Docker Compose | Vedi la [pagina dell'ambiente](environment.md#docker). |

Home Assistant è fissato in diversi file che devono cambiare insieme, altrimenti lint e test girano su core diversi. I passaggi sono nella [pagina del rilascio](releasing.md#aggiornare-la-versione-di-home-assistant).
