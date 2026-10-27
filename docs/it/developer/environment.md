[en](../../en-gb/developer/environment.md) | [de](../../de/developer/environment.md) | [nl](../../nl/developer/environment.md) | [fr](../../fr/developer/environment.md) | [zh](../../zh-hans/developer/environment.md) | [es](../../es/developer/environment.md) | it | [pl](../../pl/developer/environment.md) | [sv](../../sv/developer/environment.md)

# Ambiente di sviluppo

Come preparare una copia di lavoro ed eseguire l'istanza di sviluppo di Home Assistant con i simulatori.

## Preparare una copia di lavoro

Una copia di lavoro richiede [uv](https://docs.astral.sh/uv/) per gli strumenti Python, Node.js e npm per le schede, Docker con Docker Compose per Home Assistant e i simulatori, e `make`. Le versioni richieste sono impostate in `pyproject.toml` e `frontend/package.json`. Dopo la clonazione, `make setup` installa le dipendenze Python, le dipendenze del frontend e il browser Chromium che i test Playwright usano.

## Eseguire Home Assistant

`make up` avvia Home Assistant con l'integrazione e due simulatori Modbus, un HS3 e un H2. `make logs` segue il log di Home Assistant e `make down` ferma tutto.

Home Assistant è sulla porta 8123. Il simulatore HS3 risponde in Modbus sulla porta 5020 dell'host e il simulatore H2 sulla 5021, e le pagine dei simulatori sono sulle porte 5080 e 5081. Dentro Docker, Home Assistant raggiunge i simulatori tramite i nomi di servizio `mock` e `mock-h2` sulla porta 502. Non serve alcun inverter reale. La [pagina del simulatore](simulator.md) spiega come connettersi ai simulatori e come cambiare ciò che i simulatori simulano.

Per usare altre porte dell'host, un altro fuso orario o altri scenari, copia [compose.override.yaml.example](../../../compose.override.yaml.example) nel file ignorato `compose.override.yaml` e cambia ciò che differisce. Non modificare `compose.yaml` per esigenze locali, perché anche `make mock-smoke` avvia `compose.yaml`.

## Docker

Lo sviluppo gira in contenitori, così Home Assistant è una versione nota e fissata con una configurazione pulita. I servizi sono definiti in questi file:

- [compose.yaml](../../../compose.yaml): l'ambiente interattivo, con Home Assistant, il simulatore HS3 `mock` e il simulatore H2 `mock-h2`. L'integrazione è montata in sola lettura in Home Assistant, quindi il contenitore non scrive mai nell'albero dei sorgenti. I simulatori conservano le proprie modifiche in `mock/state/hs3/` e `mock/state/h2/`, che Git ignora.
- [compose.playwright.yaml](../../../compose.playwright.yaml): un Home Assistant usa e getta costruito da `Dockerfile.playwright-home-assistant`, con un simulatore HS3, un simulatore H2 e gli esecutori di Playwright. `make test-browser-home-assistant` usa i servizi `homeassistant`, `mock`, `mock-h2` e `playwright` per dimostrare che ogni endpoint può essere aggiunto, si carica, riporta valori dei sensori, mostra la potenza solare su una scheda flusso di potenza e, una volta consentito il controllo, accetta un'impostazione modificata. `make docs-images` usa i servizi `homeassistant`, `mock-docs`, `mock-h2` e `playwright-docs`, vedi [Schermate](documentation.md#schermate). I servizi non condividono alcuno stato con l'ambiente interattivo.
- `compose.override.yaml`: le porte, il fuso orario e gli scenari della tua macchina. Git ignora il file, e `compose.override.yaml.example` ne mostra la forma.

Sotto `config/`, Git traccia solo `configuration.yaml` e le due plance di dimostrazione in `config/dashboards/`. Il resto è stato locale di Home Assistant.

La [pagina dei controlli](checks.md) elenca che cosa esegue ogni target make, e la [pagina del frontend](frontend.md#plance-di-dimostrazione) descrive le due plance di dimostrazione.
