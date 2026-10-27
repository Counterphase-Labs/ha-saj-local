[en](../../../en-gb/user/cards/README.md) | [de](../../../de/user/cards/README.md) | [nl](../../../nl/user/cards/README.md) | [fr](../../../fr/user/cards/README.md) | [zh](../../../zh-hans/user/cards/README.md) | [es](../../../es/user/cards/README.md) | it | [pl](../../../pl/user/cards/README.md) | [sv](../../../sv/user/cards/README.md)

# Schede della plancia

La pagina Schede della plancia spiega come aggiungere le schede di SAJ Local a una plancia e scegliere un sistema, ed elenca che cosa mostra ogni elemento. Gli elenchi completi sono nelle sezioni [Elementi e configurazione](../../../../frontend/docs/features.md#elements-and-setup) e [Tema e lingua](../../../../frontend/docs/features.md#theme-and-language) dell'elenco delle funzionalità delle schede, e nella sezione [Schede](../../../../custom_components/saj_local/docs/features.md#cards) dell'elenco delle funzionalità dell'integrazione.

SAJ Local fornisce le schede e le registra in Home Assistant all'avvio di Home Assistant. Le schede compaiono nel selettore delle schede, quindi non c'è alcuna risorsa da aggiungere e nessuna cache da svuotare.

## Elementi

| Elemento | Che cosa mostra l'elemento |
| --- | --- |
| [Scheda flusso di potenza](power-flow-card.md) | La potenza in tempo reale tra solare, batteria, rete, casa e apparecchiature opzionali. |
| [Scheda stato](status-card.md) | Lo stato di funzionamento, la modalità, le letture principali, l'energia di oggi, un riepilogo dei guasti e se il controllo è consentito. |
| [Scheda guasti](faults-card.md) | I guasti attivi di ogni apparecchiatura e un pulsante Cancella guasto. |
| [Scheda batteria](battery-card.md) | Lo stato di carica con i limiti segnati, le letture della batteria e un gruppo di righe per ogni modulo. |
| [Scheda controlli](controls-card.md) | Le impostazioni del sistema in sezioni. |
| [Scheda pianificazione](schedule-card.md) | Le fasce di carica, di scarica e del caricatore EV, una linea temporale settimanale e un editor di fasce. |
| [Funzione giorni della settimana per la scheda tile](weekdays-feature.md) | Sette pulsanti dei giorni su una scheda tile, per i giorni di una fascia. |
| [Badge di stato](status-badge.md) | Un badge con lo stato di funzionamento e il numero di apparecchiature con un guasto attivo. |

## Aggiungere un elemento

1. Modifica una plancia e scegli Aggiungi scheda. Per la funzione giorni della settimana, aggiungi una scheda tile e apri le funzioni della scheda tile. Per il badge, modifica i badge della plancia.
2. Scegli l'elemento SAJ Local nel selettore. Le sei schede mostrano un'anteprima in tempo reale.
3. Scegli il sistema nel campo Sistema dell'editor visuale. Una nuova scheda o un nuovo badge parte con il primo sistema. La funzione giorni della settimana non ha un editor, perché la funzione usa l'entità della scheda tile.

Una casa con due sistemi aggiunge una scheda una volta per sistema. Il titolo di una scheda è il nome del dispositivo del sistema seguito dal modello, per esempio SAJ HS3 (12000 W). SAJ Local aggiunge il numero di serie solo quando altrimenti due sistemi avrebbero un titolo identico. Rinomina ogni dispositivo in Home Assistant se vuoi altri titoli.

Gli elementi trovano le entità di un sistema tramite il registro delle entità, e non tramite l'ID entità, quindi gli elementi continuano a funzionare quando cambi un [prefisso](../entities-and-prefix.md#il-prefisso).

## Che cosa fa ogni elemento

- **Solo ciò che ha il sistema.** Una parte la cui entità non esiste o è disabilitata non viene disegnata, quindi ogni scheda mostra solo ciò che ha il sistema. Una parte per un solo modello compare solo su quel modello, e la pagina di ogni elemento nomina le parti.
- **Una scheda vuota dice perché.** Una scheda senza nessuna delle sue entità abilitata indica quale tipo di entità abilitare, con un collegamento alla pagina del dispositivo del sistema.
- **Un sistema che non risponde.** Una scheda lo dice e attenua i valori.
- **Tocca un valore.** Toccare un valore apre i dettagli dell'entità in Home Assistant.
- **Controlli bloccati.** Finché [Consenti controllo](../changing-settings.md#consentire-il-controllo) è disattivato per il sistema, ogni controllo è disabilitato e un lucchetto rimanda alle impostazioni dell'integrazione. Attivare Consenti controllo abilita anche le entità di cui le schede hanno bisogno, vedi [l'insieme dei controlli](../changing-settings.md#linsieme-dei-controlli).
- **Una modifica per decisione.** Un cursore modifica l'inverter quando lo rilasci. Un campo numerico modifica l'inverter con Invio o quando lasci il campo. Un elenco, un interruttore o un campo dell'ora modifica l'inverter al cambiamento. Il controllo mostra poi il valore che l'inverter contiene, e un rifiuto compare sotto il controllo con le parole dell'integrazione.

## Tema e lingua

Gli elementi seguono il tema di Home Assistant. Nomi delle entità, valori e stati usano la formattazione e la lingua di Home Assistant. I testi delle schede esistono in inglese, tedesco, olandese, francese, cinese semplificato, spagnolo, italiano, polacco e svedese. Una plancia in qualsiasi altra lingua mostra i testi delle schede in inglese.

## Non ancora supportato

- I testi delle schede in lingue diverse dalle nove sopra.
