[en](../../en-gb/developer/documentation.md) | [de](../../de/developer/documentation.md) | [nl](../../nl/developer/documentation.md) | [fr](../../fr/developer/documentation.md) | [zh](../../zh-hans/developer/documentation.md) | [es](../../es/developer/documentation.md) | it | [pl](../../pl/developer/documentation.md) | [sv](../../sv/developer/documentation.md)

# Documentazione

Come sono organizzate le pagine della documentazione, come vengono create il riferimento delle entità e le schermate, e su che cosa fallisce `make docs-check`.

## Struttura

Le pagine utente stanno in `docs/en-gb/user/` e le pagine per sviluppatori in `docs/en-gb/developer/`. Ogni cartella ha un indice `README.md`, e ogni pagina copre un argomento. Nessuna pagina scritta supera le 300 righe. Ogni fatto ha un responsabile, elencato in [Fonti](#fonti), e ogni altra pagina rimanda al responsabile invece di riformulare il fatto.

Le schermate stanno in `docs/images/en-gb/`. Ogni immagine deve essere referenziata da una pagina.

Le pagine in inglese si scrivono in inglese britannico, nel tono di voce di Counterphase, e usano i termini che le traduzioni dell'integrazione mostrano agli utenti. Le pagine utente descrivono SAJ in generale e indicano, nel punto della differenza, dove l'HS3 e l'H2 differiscono. Una pagina non si divide mai in una pagina per modello.

## Prima gli elenchi delle funzionalità

I tre elenchi delle funzionalità sono la base di ogni pagina: [integrazione](../../../custom_components/saj_local/docs/features.md), [schede](../../../frontend/docs/features.md) e [simulatore](../../../mock/docs/features.md). Una sezione di un elenco delle funzionalità dice che cosa è costruito e nomina i file da leggere nella riga `Files:` della sezione. Conferma ogni affermazione rispetto a quei file prima di documentarla. I documenti dei requisiti dicono che cosa è previsto e si leggono solo per l'intento. Un comportamento che compare in un documento dei requisiti ma in nessun elenco delle funzionalità non è costruito, e una pagina utente non descrive il comportamento come disponibile. Dove un elenco delle funzionalità e il codice non concordano, il codice è ciò che gli utenti ottengono, quindi correggi l'elenco delle funzionalità nella stessa modifica.

Una pagina che descrive codice rimanda alla sezione dell'elenco delle funzionalità la cui riga `Files:` nomina il codice, e non ripete l'elenco dei file.

Una modifica di capacità aggiorna l'elenco delle funzionalità della parte e ogni pagina utente che rimanda alla sezione modificata, nella stessa modifica. L'`AGENTS.md` principale contiene la regola.

## Riferimento delle entità generato

`docs/en-gb/user/entities/` contiene una pagina generata per ogni area e un indice `README.md`. Esegui `make docs` per rigenerare le pagine, poi fai commit delle pagine rigenerate. Le pagine in prosa non nominano mai un'entità a mano; le pagine in prosa rimandano alle pagine generate. Le pagine generate sono esenti dal limite di 300 righe, perché i lettori cercano un'area come la batteria invece di leggere l'area.

Il generatore è `.github/scripts/docs_check.py`, eseguito con `--write` da `make docs`. Il generatore importa solo la libreria SAJ e legge `custom_components/saj_local/translations/en.json`, quindi il generatore non ha bisogno di Home Assistant. Ogni pagina di area si apre con un collegamento alle sezioni dell'elenco delle funzionalità che coprono l'area e con una riga sul prefisso dell'ID entità, e poi ha una riga per entità con il nome da `en.json`, l'ID entità senza prefisso, il tipo, l'unità, i modelli che hanno l'entità, le apparecchiature che devono essere installate con qualsiasi numero di fasi, stringhe o moduli batteria, e se l'entità è abilitata per impostazione predefinita. Un'entità che due modelli definiscono in modo diverso, per esempio con un'altra unità, ottiene una riga per ogni definizione.

### Fonti delle entità

Ogni entità viene da una di queste fonti, e il generatore le legge tutte:

| Fonte | Codice | Entità |
| --- | --- | --- |
| Il catalogo dei registri di ogni modello distribuito | `catalogue_of` in [catalogue.py](../../../custom_components/saj_local/saj/catalogue.py), chiamato per ogni profilo in `PROFILES` di [profiles.py](../../../custom_components/saj_local/saj/profiles.py), saltando le righe che non sono esposte | Sensori, sensori binari (i guasti), numeri, selezioni, interruttori, ore e pulsanti |
| Il sensore di controllo consentito | `CONTROL_ALLOWED_KEY` in [binary_sensor.py](../../../custom_components/saj_local/binary_sensor.py) | `binary_sensor.saj_control_allowed`, su entrambi i modelli |
| Gli interruttori e i numeri del controllo della potenza | `power_control` di ogni profilo ([hs3.py](../../../custom_components/saj_local/saj/models/hs3.py) e [h2.py](../../../custom_components/saj_local/saj/models/h2.py)), le chiavi `PowerFunction` in [models/\_\_init\_\_.py](../../../custom_components/saj_local/saj/models/__init__.py) e `FUNCTION_EQUIPMENT` in [power_control.py](../../../custom_components/saj_local/saj/power_control.py), creati da [switch.py](../../../custom_components/saj_local/switch.py) e [number.py](../../../custom_components/saj_local/number.py) | Un interruttore e un numero per ogni funzione di potenza di un modello: batteria su entrambi i modelli, rete e inverter sull'HS3 |

`make docs-check` fallisce quando un'entità nel blocco `entity` di `en.json` non è in nessuna pagina di area, quindi una fonte di entità che il generatore non legge viene trovata subito. Una nuova fonte richiede che il generatore legga la fonte e una riga nella tabella qui sopra.

### Aree

Un'entità finisce nella prima area che corrisponde, in quest'ordine:

1. Entità fuori dal catalogo: Aggiunte dall'integrazione.
2. Sensori binari dal catalogo, che sono i guasti: Guasti.
3. Entità con un indice di modulo batteria: Moduli batteria.
4. Entità di apparecchiature opzionali: Batteria, Rete e Contatore A, Contatore B, Caricatore EV o Sistema in parallelo.
5. Entità scrivibili senza apparecchiatura: Impostazioni.
6. Entità la cui chiave inizia con `grid_`: Rete e Contatore A.
7. Tutto il resto: Inverter e solare.

La tabella `AREAS` di `.github/scripts/docs_check.py` nomina le aree, i loro riepiloghi e le sezioni dell'elenco delle funzionalità che ogni pagina di area collega.

## Controlli

`make docs-check` esegue `.github/scripts/docs_check.py` senza `--write` e riporta una riga per ogni rilievo:

- una pagina generata che differisce da ciò che scriverebbe `make docs`;
- un'entità in `en.json` che non è in nessuna pagina di area, e un'entità generata senza nome in `en.json`;
- un collegamento relativo, un'immagine o un'ancora di titolo che non si risolve, nelle pagine, in `README.md`, `CONTRIBUTING.md`, `SECURITY.md` e in ogni `AGENTS.md`, compresi i collegamenti negli elenchi delle funzionalità e nei documenti dei requisiti;
- un'immagine in `docs/images/` che nessuna pagina referenzia;
- una pagina scritta di oltre 300 righe;
- una sezione di un elenco delle funzionalità senza riga nella [Tabella di copertura delle funzionalità](#tabella-di-copertura-delle-funzionalità), una sezione nominata nella tabella che l'elenco delle funzionalità non ha, una pagina nominata nella tabella che non esiste, e una pagina che non rimanda alla sezione dell'elenco delle funzionalità nominata nella riga, tramite l'ancora del titolo della sezione.

`make docs-check` è un passaggio di `make ci`, e GitHub esegue `make ci`, quindi il controllo non richiede alcuna modifica al workflow. Il controllo non legge alcuna schermata oltre alle regole sui collegamenti e sulle immagini orfane e non avvia alcun browser.

## Schermate

Ogni schermata in `docs/images/<code>/` è creata da `make docs-images` da un Home Assistant reale in Docker con la lingua dell'utente impostata sulla lingua della cartella, oppure dalle pagine dei simulatori della stessa esecuzione. `make docs-images` esegue ogni lingua contemporaneamente, ogni lingua nei propri contenitori nuovi, e `ARGS=<code>` seleziona una lingua. Nessuna schermata viene modificata o catturata a mano, quindi l'insieme può essere ricostruito ogni volta che l'interfaccia cambia. Le schermate mostrano i simulatori, quindi ogni lettura in una schermata è un valore simulato.

Il target esegue `tests/playwright/run-docs-images.sh`, che costruisce una sola volta per tutte le lingue le immagini dei servizi `homeassistant` e `playwright-docs` di [compose.playwright.yaml](../../../compose.playwright.yaml), avvia per ogni lingua un Home Assistant usa e getta e due simulatori, esegue la specifica e poi rimuove i contenitori, i volumi e le immagini locali. I contenitori Playwright vengono eseguiti come utente dell'host, quindi nessun file di un'esecuzione appartiene a root, anche dopo un'esecuzione interrotta prima della fine. Il target richiede Docker, ha lo stesso limite di tempo di `make test-browser-home-assistant` e accetta opzioni tramite `ARGS`, che lo script riceve. L'immagine di Home Assistant è costruita da `Dockerfile.playwright-home-assistant`, che costruisce il bundle delle schede e copia l'integrazione nell'immagine, quindi nessun codice dell'integrazione è montato. La specifica è `frontend/tests/browser/docs/screenshots.spec.ts`, configurata da `frontend/playwright.docs.config.ts`.

- **Sistemi.** L'HS3 è il simulatore `mock-docs` su `mock/scenarios/hs3-full-house.yaml`, che ha ogni apparecchiatura installata. L'H2 è il simulatore `mock-h2` su `mock/scenarios/h2-battery.yaml` e ottiene il prefisso di entità `h2`. Nessuno dei due simulatori monta una cartella di stato, quindi ogni esecuzione parte dallo scenario.
- **Condizioni fisse.** La finestra è di 1280 per 800 pixel e il tema è chiaro. Una finestra di dialogo o una scheda alta viene catturata in una finestra alta 1600 pixel, perché l'intestazione fissa di Home Assistant coprirebbe la parte superiore dell'elemento.
- **Orologi fermi.** Dopo aver riportato ogni simulatore al suo scenario, la specifica ferma gli orologi simulati di entrambi i simulatori all'ora di inizio dello scenario per tutta l'esecuzione, quindi le letture sono uguali a ogni esecuzione. Le schermate delle pagine dei simulatori e la schermata della riparazione mostrano valori di tempo fissi, non quelli reali. Per ogni pagina del simulatore, la specifica dà al browser una copia dei dati della pagina con frequenze delle richieste, orari, durate e indirizzi dei client fissi, e fissa l'orologio del browser. Per la schermata della riparazione, la specifica fissa l'orologio del browser a 5 secondi dopo la creazione del problema di riparazione da parte di Home Assistant, quindi il problema mostra «5 secondi fa».
- **Lingue in parallelo.** Le lingue vengono eseguite contemporaneamente, ciascuna nei propri contenitori. L'esecuzione avvia tante lingue alla volta quanti gruppi di quattro processori ha la macchina. Ogni lingua scrive la propria cartella dei risultati `frontend/test-results/docs/<code>/` e la propria cartella del rapporto `frontend/playwright-report/docs/<code>/`. Una lingua fallita non ferma le altre lingue.
- **Lingua.** Ogni esecuzione imposta sia la lingua del server di Home Assistant, prima della configurazione di SAJ Local così che le entità siano create con nomi in quella lingua, sia la lingua dell'utente, tramite il codice lingua e non tramite l'etichetta del selettore della lingua. L'esecuzione fallisce se il nome di un'entità di SAJ Local non è nella lingua dell'esecuzione. Le immagini vanno in `docs/images/<code>/`. La specifica apre le schermate tramite la route dell'URL, trova i campi dei moduli di SAJ Local tramite il loro attributo `name`, e trova i controlli di Home Assistant che hanno solo testo tramite il testo letto durante l'esecuzione dall'Home Assistant in funzione con `hass.localize`. La specifica non contiene alcuna tabella di etichette, quindi ogni lingua esegue gli stessi passaggi.
- **Nomi.** Ogni file è chiamato `<page>-<subject>.png`, dove `<page>` è il percorso della pagina con `/` sostituito da `-`, per esempio `cards-battery-card.png`, e la pagina che mostra l'immagine rimanda al file.
- **Pagine dei simulatori.** Le schermate delle pagine dei simulatori vengono dai due simulatori della stessa esecuzione, `mock-docs` e `mock-h2`, e usano il prefisso di nome `developer-simulator-page-`. Vengono create per ultime, dopo ogni schermata di Home Assistant, così nulla di ciò che si fa su una pagina di un simulatore cambia una schermata di Home Assistant. La specifica imposta il guasto «Fan 1 fault» sulla pagina dell'HS3, e il registro che la schermata della riparazione fa rifiutare al simulatore resta rifiutato, quindi la vista Link, il registro del traffico e le modifiche nella barra di stato mostrano modifiche reali.
- **Preparazione.** La specifica crea un utente tramite l'API di onboarding, aggiunge l'HS3 tramite il flusso di configurazione nel browser, aggiunge l'H2 tramite l'API del flusso di configurazione, attiva Consenti controllo per entrambi i sistemi e aggiunge una plancia per ogni sistema con ogni scheda di SAJ Local e il badge di stato, tramite l'API WebSocket di Home Assistant.
- **Tutto o niente.** La specifica attende fino a due minuti che entrambi i sistemi riportino la potenza solare. La specifica scrive le immagini solo dopo che ogni passaggio è riuscito, quindi un'esecuzione fallita lascia le immagini di cui è stato fatto il commit com'erano.
- **Attese.** La specifica attende una schermata verificando lo stato che la schermata mostra, mai con una pausa fissa.
- **Riparazione.** La schermata della riparazione mostra la riparazione dei registri rifiutati. La specifica aggiunge un gruppo di polling per la temperatura dell'inverter con un intervallo di 10 secondi, fa rifiutare quel registro al simulatore tramite `POST /api/link` della pagina del simulatore, e attende fino a due minuti che `repairs/list_issues` elenchi il problema `registers_refused` di SAJ Local. L'esecuzione fallisce con un messaggio che nomina il problema mancante quando il problema non compare.
- **Moduli.** L'avviso di modifica del prefisso viene catturato e poi il modulo viene chiuso, il che interrompe il flusso, quindi nessun prefisso viene salvato. L'avviso di Consenti controllo viene catturato e poi confermato, perché le schede richiedono il controllo consentito.
- **Fallimenti.** Il rapporto HTML di ogni lingua è in `frontend/playwright-report/docs/<code>/`, e una lingua fallita salva il log di Home Assistant nella propria cartella dei risultati `frontend/test-results/docs/<code>/`. L'esecuzione fallita nomina ogni lingua fallita e la sua cartella del rapporto.

Le schermate non vengono confrontate pixel per pixel, né nella CI né altrove. Home Assistant rende valori in tempo reale e font in modo diverso da un'esecuzione all'altra, quindi un confronto pixel per pixel fallirebbe senza una modifica reale. Rivedi un'immagine cambiata guardandola.

### Aggiungere o modificare una schermata

1. Aggiungi o modifica la cattura nella specifica, con il nome del file nella forma `<page>-<subject>.png`.
2. Referenzia l'immagine dalla pagina che spiega l'argomento.
3. Esegui `make docs-images`, guarda le immagini cambiate e fai commit delle immagini cambiate.
4. Esegui `make docs-check`. Un'immagine che nessuna pagina referenzia, e un collegamento a un'immagine che non esiste, vengono entrambi segnalati.

`make docs-images` non è un passaggio di `make ci`, e la CI non rigenera le immagini. Esegui il target prima di ogni rilascio, vedi la [pagina del rilascio](releasing.md).

## Aggiungere una pagina

1. Crea la pagina sotto `docs/en-gb/user/` o `docs/en-gb/developer/` e collega la pagina dall'indice della cartella.
2. Collega la pagina alla sezione dell'elenco delle funzionalità la cui riga `Files:` nomina il codice che la pagina descrive.
3. Aggiungi la pagina alla riga di quella sezione nella Tabella di copertura delle funzionalità, oppure aggiungi una riga. Una nuova sezione di un elenco delle funzionalità richiede una riga prima che `make docs-check` passi.
4. Esegui `make docs-check`.

Mantieni le pagine utili: rimanda al file che contiene un fatto invece di copiare il fatto, registra il motivo di una decisione perché i motivi cambiano di rado e i dettagli di continuo, e tieni pochi esempi ed esegui di nuovo ogni esempio quando cambia.

## Lingue

La documentazione esiste in inglese e in ogni lingua di destinazione dei [requisiti globali](../../../.github/work/requirements.md#language). Gli elenchi delle funzionalità e i documenti dei requisiti restano solo in inglese.

- **Struttura.** Ogni lingua ha le cartelle sorelle `docs/<code>/user/`, `docs/<code>/developer/` e `docs/images/<code>/`, con gli stessi nomi di file in ogni lingua. I codici sono `en-gb`, `de`, `nl`, `fr`, `zh-hans`, `es`, `it`, `pl` e `sv`. Un blocco di codice uguale in più lingue resta nel testo di ogni pagina ed è racchiuso in una coppia di marcatori `jscpd:ignore-start` e `jscpd:ignore-end`, solo con un'eccezione che l'utente ha approvato in un piano, come dice `AGENTS.md`. Una coppia di marcatori racchiude un solo blocco di codice e nient'altro.
- **Generatore.** `make docs` scrive `docs/<code>/user/entities/` per ogni lingua dal file corrispondente in `custom_components/saj_local/translations/`. I nomi delle apparecchiature vengono dallo stesso file di traduzione, e gli altri testi del generatore vengono da `.github/scripts/docs_text/<code>.json`.
- **Controllo della documentazione.** `make docs-check` esegue ogni regola su ogni cartella di lingua. La [Tabella di copertura delle funzionalità](#tabella-di-copertura-delle-funzionalità) di questa pagina si applica a ogni lingua con gli stessi nomi di pagina, e la regola sulle immagini orfane controlla `docs/images/<code>/` rispetto alle pagine della stessa lingua.
- **Barra delle lingue.** La prima riga di ogni pagina sotto `docs/<code>/user/` e `docs/<code>/developer/`, comprese le pagine delle entità generate, è la barra delle lingue `en | de | nl | fr | zh | es | it | pl | sv`, sempre in quest'ordine. Ogni etichetta tranne quella della lingua corrente rimanda alla stessa pagina nella cartella di quella lingua, e la lingua corrente è testo semplice. `make docs` scrive la barra delle lingue, e `make docs-check` segnala una pagina la cui prima riga non è la barra delle lingue prevista e un collegamento della barra a una pagina che non esiste.
- **README tradotto.** Il `README.md` nella radice del repository resta in inglese ed è tradotto in `docs/<code>/README.md`, i cui collegamenti puntano alle pagine di quella lingua. Il `README.md` radice e ogni `docs/<code>/README.md` portano la stessa barra delle lingue come prima riga, e `make docs-check` segnala un `docs/<code>/README.md` mancante.
- **Schermate.** `make docs-images` esegue la specifica per ogni lingua contemporaneamente, ogni lingua nei propri contenitori nuovi, con la propria cartella dei risultati e del rapporto. `ARGS=<code>` seleziona una lingua, vedi [Schermate](#schermate).
- **Nomenclatura.** La pagina `user/nomenclature.md` di ogni lingua è l'elenco dei termini che ogni traduzione dell'integrazione, delle schede e delle pagine della lingua segue. La [nomenclatura](../user/nomenclature.md) inglese è la fonte.
- **Modificare l'inglese.** Una modifica a un testo, a una pagina o a una schermata in inglese aggiorna ogni lingua nella stessa modifica. Nessun controllo mantiene le lingue allineate.

## Tabella di copertura delle funzionalità

Ogni sezione di un elenco delle funzionalità viene esaminata dalla riga `Files:` della sezione e coperta dalle pagine nominate qui. Ogni pagina nominata rimanda alla sezione tramite l'ancora del titolo della sezione. Un nome di pagina è relativo a `docs/en-gb/` e rimanda alla pagina. La tabella si trova solo nella pagina inglese [Documentation](../../en-gb/developer/documentation.md#feature-coverage-table), e `docs-check` legge la tabella da lì. La tabella si applica in ogni lingua agli stessi nomi di pagina, e una pagina aggiunta, unita o divisa aggiorna la tabella nella stessa modifica.

## Fonti

| Fatto | Responsabile |
| --- | --- |
| Che cosa fa SAJ Local, in un breve riepilogo | [indice utente](../user/README.md) |
| Che cosa può fare ogni parte | i tre elenchi delle funzionalità |
| Modelli e apparecchiature supportati | [apparecchiature supportate](../user/supported-equipment.md) |
| Nomi delle entità, ID entità, modelli, apparecchiature e valori predefiniti | il catalogo e `translations/en.json`, tramite il [riferimento delle entità](../user/entities/README.md) |
| Tipi di entità, regole di abilitazione predefinita e convenzioni dei segni | la sezione Devices and entities dell'elenco delle funzionalità dell'integrazione |
| Impostazione dello sviluppo | [ambiente](environment.md) |
| Target make e regole dei controlli | [controlli](checks.md) |
| Rilascio e aggiornamento della versione di Home Assistant | [rilascio](releasing.md) |
| Schermata panoramica del sito | `docs/images/en-gb/cards-power-flow-card.png`, copiata dai maintainer sul sito web del progetto a ogni rilascio, vedi la [pagina del rilascio](releasing.md) |
| Come segnalare un problema di sicurezza | `SECURITY.md` |
| Etichette delle segnalazioni e regole per le etichette | `.github/labels.yml` e `CONTRIBUTING.md` |
| Termini della licenza | `LICENSE` |
| Comportamento previsto del prodotto | `.github/work/requirements.md` e i tre documenti dei requisiti delle parti |
