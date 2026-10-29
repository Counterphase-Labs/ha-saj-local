[en](../../en-gb/developer/releasing.md) | [de](../../de/developer/releasing.md) | [nl](../../nl/developer/releasing.md) | [fr](../../fr/developer/releasing.md) | [zh](../../zh-hans/developer/releasing.md) | [es](../../es/developer/releasing.md) | it | [pl](../../pl/developer/releasing.md) | [sv](../../sv/developer/releasing.md)

# Rilascio

Che cosa fare prima di un rilascio, come viene pubblicato un rilascio e come si aggiorna la versione di Home Assistant. Inviare un tag di versione avvia il workflow `Release` in `.github/workflows/release.yml`, che controlla il tag, esegue i controlli e crea una bozza di rilascio GitHub.

## Versioni

Un rilascio è un rilascio GitHub creato da un tag di versione su `main`. Il tag non ha il prefisso `v` ed è uguale alla versione in `custom_components/saj_local/manifest.json`, `pyproject.toml` e `frontend/package.json`. Un rilascio stabile è `X.Y.Z` e una beta è `X.Y.ZbN`, pubblicata come pre-rilascio GitHub. Le beta prima del primo rilascio stabile sono `1.0.0b1`, `1.0.0b2` e così via, il primo rilascio stabile è `1.0.0`, e il Semantic Versioning si applica da `1.0.0`. Le note di rilascio vivono solo nel rilascio GitHub, e le note di una beta nominano ogni modifica a un'entità, a un'impostazione memorizzata, a un tipo di scheda o a un'impostazione di scheda dalla beta precedente. La sezione [Rilascio](../../../.github/work/requirements.md#releases) dei requisiti del progetto contiene la regola.

## Prima di un rilascio

Fai questi passaggi su `main`, in ordine.

1. **Esegui `make ci`.** La [pagina dei controlli](checks.md) elenca che cosa esegue `make ci`.
2. **Esegui `make docs-images`.** La documentazione utente mostra l'interfaccia, e la CI non rigenera le immagini, quindi ogni rilascio richiede un insieme nuovo. Il target richiede Docker. Esegui il target, guarda ogni immagine cambiata, sottoponi a commit le immagini cambiate in `docs/images/en-gb/` ed esegui `make docs-check`. Un'esecuzione che fallisce non scrive alcuna immagine, quindi non rilasciare con un'esecuzione fallita. Leggi [Schermate](documentation.md#schermate) per sapere che cosa fa l'esecuzione e perché ogni lettura in un'immagine è simulata.
3. **Copia la schermata del sito nello stesso passaggio.** Copia `docs/images/en-gb/cards-power-flow-card.png` in `assets/images/saj-local-power-flow.png` nel repository `website` e sottoponi a commit la copia lì, perché la pagina di SAJ Local su `counterphase.dev` mostra una copia dell'immagine. Nessun controllo rileva una copia obsoleta, perché la CI di questo repository non vede il repository del sito.
4. **Esegui `make release-check`.** Il passaggio crea un archivio da `custom_components/saj_local/` e fallisce quando l'archivio non contiene `asset-manifest.json`, il bundle compilato delle schede o `THIRD_PARTY_LICENSES.md`, le licenze delle librerie nel bundle. Esegui prima `make build` e sottoponi a commit il bundle e il file delle licenze quando le schede sono cambiate.
5. **Imposta la nuova versione.** Imposta la versione in `custom_components/saj_local/manifest.json`, `pyproject.toml` e `frontend/package.json`. Esegui `uv lock` perché `uv.lock` registri la versione del progetto, ed esegui `npm install --package-lock-only` in `frontend/` perché `frontend/package-lock.json` registri la versione. Esegui `make release-check`, fai commit su `main` e attendi che la CI passi.

Le schermate sono l'unica parte di un rilascio che la CI non può controllare. Una modifica che aggiunge o rimuove un'immagine fa fallire `make docs-check` tramite le regole sulle immagini inutilizzate e mancanti. Una modifica all'interfaccia che lascia un'immagine obsoleta non fa fallire nulla, quindi il passaggio 2 è ciò che mantiene aggiornate le immagini.

## Pubblicare un rilascio

1. Invia il tag: `git tag 1.0.0b1`, poi `git push origin 1.0.0b1`.
2. Attendi il workflow `Release`. Il workflow richiede il commit con il tag su `main`, esegue `make ci` tramite `ci.yml` e crea una bozza di rilascio con le note generate da GitHub.
3. Apri la bozza di rilascio e modifica le note generate. Per una beta, nomina ogni modifica a un'entità, a un'impostazione memorizzata, a un tipo di scheda o a un'impostazione di scheda dalla beta precedente.
4. Premi Publish.

Un'esecuzione fallita non crea alcuna bozza. Elimina il tag con `git push origin :refs/tags/<tag>` e `git tag -d <tag>`, correggi `main` e assegna di nuovo il tag.

HACS offre una beta pubblicata agli utenti che attivano «Show beta versions» e un rilascio stabile pubblicato a ogni utente. Un utente senza l'interruttore riceve la punta di `main` finché `1.0.0` non esiste, ed è per questo che `main` deve superare `make ci` prima di ogni push.

## Aggiornare la versione di Home Assistant

La versione di Home Assistant è fissata in diversi file che devono essere aggiornati insieme, altrimenti il contenitore di sviluppo, i test del browser e l'esecuzione delle schermate, la CI, HACS e il banco di prova si discostano tra loro:

1. `compose.yaml`: `ghcr.io/home-assistant/home-assistant:<X.Y.Z>`, il runtime di Home Assistant di sviluppo.
2. `Dockerfile.playwright-home-assistant`: la riga `FROM ghcr.io/home-assistant/home-assistant:<X.Y.Z>` dell'immagine che `make test-browser-home-assistant` e `make docs-images` usano.
3. `pyproject.toml`, `[dependency-groups] dev`: `homeassistant==<X.Y.Z>` per il lint e mypy della CI, **e** `pytest-homeassistant-custom-component==<versione corrispondente>`. Il banco di prova include il proprio `homeassistant` fissato, quindi le due versioni fissate devono venire dallo stesso rilascio di Home Assistant, altrimenti lint e test risolvono core diversi.
4. `hacs.json`: `"homeassistant": "<X.Y.Z>"`, il core di Home Assistant minimo che HACS impone.
5. `uv.lock`: esegui `uv lock` dopo la modifica di `pyproject.toml`, così il file di lock registra le nuove versioni fissate.

Verifica l'abbinamento su PyPI prima del commit: i `requires_dist` di `pytest-homeassistant-custom-component` devono elencare lo stesso `homeassistant==<X.Y.Z>` fissato in `pyproject.toml`.

Dopo un aggiornamento, esegui `make ci` e `make docs-images`, perché una nuova versione di Home Assistant può cambiare le schermate che le immagini mostrano.
