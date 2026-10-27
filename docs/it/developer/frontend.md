[en](../../en-gb/developer/frontend.md) | [de](../../de/developer/frontend.md) | [nl](../../nl/developer/frontend.md) | [fr](../../fr/developer/frontend.md) | [zh](../../zh-hans/developer/frontend.md) | [es](../../es/developer/frontend.md) | it | [pl](../../pl/developer/frontend.md) | [sv](../../sv/developer/frontend.md)

# Frontend

Come è organizzato e costruito il bundle delle schede, e come vedere ogni scheda nell'istanza di sviluppo.

L'elenco completo di ciò che il frontend copre è nelle sezioni dell'elenco delle funzionalità [Schede](../../../custom_components/saj_local/docs/features.md#cards) dell'integrazione e [Elementi e configurazione](../../../frontend/docs/features.md#elements-and-setup) e [Tema e lingua](../../../frontend/docs/features.md#theme-and-language) delle schede.

## Build

Le schede, la funzione della scheda tile e il badge sono un unico bundle Lit e TypeScript sotto `frontend/`. `make build` esegue Vite e scrive il bundle in `custom_components/saj_local/frontend/` come `saj-local-<hash>.js` con un `asset-manifest.json`, perché HACS distribuisce la cartella dell'integrazione come un unico archivio. Git traccia il bundle compilato e il manifest, quindi una modifica alle schede viene sottoposta a commit insieme a una nuova build. L'integrazione legge il manifest, serve il file che il manifest nomina e aggiunge l'URL del file al frontend di Home Assistant, quindi gli utenti non aggiungono alcuna risorsa alla plancia.

L'hash cambia a ogni build così un browser non esegue mai un bundle obsoleto. Il costo è che Home Assistant registra il nome di file con l'hash una sola volta, all'avvio: un nuovo bundle richiede un riavvio di Home Assistant prima che al browser venga offerto il nuovo file. L'istanza di sviluppo monta la cartella dell'integrazione, quindi esegui `make build` e riavvia Home Assistant per vedere una modifica.

## Struttura dei sorgenti

La struttura segue ciò che cambia insieme:

- `src/system/` contiene tutto ciò che non è disegno: trovare le entità di un sistema in `hass`, direzione della potenza, giorni della settimana, fasce, guasti, il blocco dei controlli e le chiamate di servizio. La cartella non tocca mai il DOM, quindi le regole sono testate senza un browser.
- `src/ui/` contiene le parti che ogni scheda disegna, con stile dato solo dalle variabili del tema di Home Assistant, perché il frontend di Home Assistant non promette alcun elemento `ha-*` alle schede personalizzate.
- `src/cards/`, `src/features/` e `src/badges/` contengono gli elementi e li registrano nel selettore di Home Assistant.
- `src/i18n/` contiene i testi che servono solo alle schede, un file per lingua, con il nome del codice lingua di Home Assistant come i file nella cartella `translations/` dell'integrazione (l'inglese e le otto lingue di destinazione), con l'inglese come ripiego per qualsiasi altra lingua. Nomi delle entità, stati e valori vengono da Home Assistant.
- `tests/fakes/` contiene un `hass` finto, costruito da un elenco di entità, e le sostituzioni dei moduli che un elemento usa. Ogni test unitario esercita un modulo con ogni collaboratore sostituito da uno dei finti.

Un elemento trova le entità di un sistema tramite dispositivo e chiave di traduzione, mai tramite ID entità, quindi una scheda non dipende mai da un prefisso dell'ID entità.

## Test

`make test-frontend` esegue i test unitari Vitest con la soglia di copertura. `make test-browser-controlled` esegue Playwright sul bundle compilato con dati controllati, e `make test-browser-home-assistant` esegue Playwright su un Home Assistant reale, vedi la [pagina dei controlli](checks.md#target-make). Le schermate della documentazione utente vengono da una terza configurazione di Playwright, vedi [Schermate](documentation.md#schermate).

## Plance di dimostrazione

Vedere ogni scheda con ogni opzione richiede un Home Assistant con sistemi reali, quindi l'ambiente di sviluppo dichiara due plance, `saj-hs3` e `saj-h2`, da `config/dashboards/saj-hs3.yaml` e `config/dashboards/saj-h2.yaml`, tramite il blocco `lovelace: dashboards:` di `config/configuration.yaml`. Le plance sono YAML semplice scritto a mano, e nessuno script genera le plance. Ogni elemento di SAJ Local è un elemento personalizzato configurato dal proprio YAML, quindi ogni scheda, funzione tile e badge è scritto singolarmente con ogni opzione impostata, sotto un titolo che nomina la scheda e le sue opzioni.

- Ogni plancia ha quattro viste: Plancia (le schede di una tipica plancia di sistema, scritte come schede normali), Schede (ogni scheda in ciascuna delle sue combinazioni di opzioni), Funzioni e badge (una scheda tile con la funzione `custom:saj-local-weekdays-feature` per ogni entità dei giorni della settimana di una fascia, e il badge di stato) e Stati vuoti (ogni scheda senza `device` e con il dispositivo di qualcosa che non è SAJ Local).
- Le plance contengono gli ID dispositivo di un'istanza di sviluppo. Uno sviluppatore la cui istanza ha ID dispositivo diversi sostituisce i due ID `device` in ogni file, l'ID del sistema e l'ID di un dispositivo che non è SAJ Local per la vista Stati vuoti, e gli ID delle entità dei giorni della settimana delle fasce quando il prefisso dell'ID entità è diverso.
- Home Assistant legge le dichiarazioni delle plance quando si avvia, quindi riavvia Home Assistant dopo aver modificato `config/configuration.yaml`. Una modifica a un file di plancia compare dopo un ricaricamento della pagina.
