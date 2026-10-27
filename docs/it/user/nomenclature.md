[en](../../en-gb/user/nomenclature.md) | [de](../../de/user/nomenclature.md) | [nl](../../nl/user/nomenclature.md) | [fr](../../fr/user/nomenclature.md) | [zh](../../zh-hans/user/nomenclature.md) | [es](../../es/user/nomenclature.md) | it | [pl](../../pl/user/nomenclature.md) | [sv](../../sv/user/nomenclature.md)

# Nomenclatura

I termini che SAJ Local, le schede della plancia e la documentazione usano, ciascuno con un significato in una riga. Ogni traduzione dell'integrazione, delle schede e della documentazione usa un solo termine per ogni elemento elencato qui. La sezione [Lingue](../../../custom_components/saj_local/docs/features.md#languages) dell'elenco delle funzionalità dell'integrazione indica le lingue in cui SAJ Local è disponibile.

## Apparecchiature SAJ e letture

| Termine | Significato |
| --- | --- |
| Inverter | L'unità SAJ che trasforma la corrente continua del solare e della batteria in corrente alternata per la casa e per la rete. |
| HS3 | Il modello di inverter ibrido SAJ HS3, un modello trifase. |
| H2 | Il modello di inverter ibrido SAJ H2, un modello monofase. |
| Modello | Il tipo di inverter che SAJ Local usa per scegliere l'elenco dei registri: Automatico, HS3 o H2. |
| Automatico | La scelta del modello che riconosce il modello dal tipo di dispositivo comunicato dall'inverter. |
| Apparecchiature opzionali | Apparecchiature che un impianto può avere o non avere: una batteria, il Contatore A, il Contatore B, un caricatore EV o un sistema in parallelo. |
| Installato | L'impostazione che indica a SAJ Local che un'apparecchiatura opzionale è installata. |
| Non installato | L'impostazione che indica a SAJ Local che un'apparecchiatura opzionale non è installata. |
| Batteria | L'accumulo di energia collegato all'inverter. |
| Modulo batteria | Un modulo di una batteria, mostrato come Modulo seguito da un numero. |
| Stato di carica | Quanto è carica la batteria, in percentuale. |
| Riserva | La carica della batteria che l'inverter trattiene e sotto la quale non scarica. |
| Solare | La potenza prodotta dai pannelli solari. |
| Stringa solare | Un gruppo di pannelli solari collegati in serie e connessi a un ingresso dell'inverter. |
| Fase | Un conduttore dell'alimentazione in corrente alternata. |
| Rete | La rete elettrica pubblica a cui è collegata la casa. |
| Prelievo | Prendere potenza dalla rete. |
| Immissione | Inviare potenza alla rete. |
| In carica | Immettere potenza nella batteria. |
| In scarica | Prelevare potenza dalla batteria. |
| Casa | La potenza che la casa consuma. |
| Carichi di backup | I carichi che restano alimentati dalla batteria e dai pannelli solari quando la rete si interrompe. |
| Contatore A | Il primo contatore elettrico che può essere collegato all'inverter. |
| Contatore B | Il secondo contatore elettrico che può essere collegato all'inverter. |
| Caricatore EV | Un caricatore per veicoli elettrici collegato all'inverter. |
| Sistema in parallelo | Più inverter che lavorano insieme come un unico sistema. |
| Guasto | Un problema segnalato dall'apparecchiatura, con un registro e un bit. |
| Cancella guasto | Il pulsante che chiede all'inverter di cancellare un guasto segnalato. |
| Stato di funzionamento | Lo stato in cui si trova l'inverter, per esempio in funzione o in standby. |
| Modalità | La modalità di funzionamento dell'inverter, per esempio a fasce orarie. |
| Fasce orarie | La modalità in cui la batteria si carica e si scarica nelle fasce che imposti. |
| Fascia | Un periodo di tempo della programmazione a fasce orarie per la carica, la scarica o il caricatore EV. |
| EMS | Le funzioni del sistema di gestione dell'energia dell'inverter, che mantengono un obiettivo di potenza dato dall'esterno. |
| Heartbeat EMS | La frequenza con cui SAJ Local legge gli obiettivi EMS per mantenere attive le funzioni EMS. |
| Timeout EMS | Il tempo dopo il quale l'inverter termina una funzione EMS che non viene mantenuta attiva. |
| Protezione dalla corrente inversa | La protezione dell'inverter contro il flusso di potenza verso l'inverter, che le funzioni EMS disattivano. |
| Controllo della potenza | Mantenere la batteria, il collegamento alla rete o l'inverter a una potenza impostata. |
| Obiettivo di potenza | La potenza che una funzione di controllo della potenza mantiene. |
| Pianificazione | Gli orari in cui una funzione di controllo della potenza è attiva. |
| Consenti controllo | L'impostazione che permette a Home Assistant di modificare le impostazioni dell'inverter. |
| Controllo | La possibilità di modificare le impostazioni dell'inverter, invece della sola lettura. |
| Registro | Una posizione di memoria numerata dell'inverter che contiene una lettura o un'impostazione. |
| Registro rifiutato | Un registro a cui l'inverter rifiuta di rispondere. |
| Modbus TCP | Il protocollo di rete che SAJ Local usa per comunicare con l'inverter. |
| Host | L'indirizzo di rete dell'inverter. |
| Porta | La porta di rete dell'inverter, 502 per impostazione predefinita. |
| ID unità | L'indirizzo Modbus dell'inverter, da 1 a 247. |
| Modulo di comunicazione | La parte dell'inverter che risponde alle richieste di rete. |
| Blocco | Un intervallo di registri che viene letto con una sola richiesta. |
| Tempo reale | Il blocco di letture che cambiano di secondo in secondo. |
| Medie di cinque minuti | Il blocco di letture che l'inverter calcola come media su cinque minuti. |
| Energia | Il blocco di letture dell'energia prodotta e consumata, come l'energia di oggi. |
| Identità | Il modello, il numero di serie e le versioni comunicati dall'inverter. |

## Concetti di SAJ Local

| Termine | Significato |
| --- | --- |
| Sistema | Un inverter, con le sue apparecchiature, aggiunto a Home Assistant. |
| Installazione | Una voce di configurazione di SAJ Local, che corrisponde a un sistema. |
| Prefisso | Testo facoltativo aggiunto agli ID entità di un'installazione, usato quando c'è più di un sistema. |
| Polling | Leggere l'inverter a intervalli. |
| Gruppo di polling | Un insieme scelto di entità che SAJ Local legge più velocemente o più lentamente dell'intervallo predefinito. |
| Intervallo di aggiornamento | I secondi tra due letture dell'inverter, mostrato come «Secondi tra gli aggiornamenti». |
| Carico di richieste | Il numero di richieste al minuto che SAJ Local invia all'inverter, rispetto al limite di 40 in 60 secondi. |
| Limite | Il tetto del carico di richieste. |
| Sostituzione del modello | Spostare un sistema su un nuovo inverter, o tra un H2 e un HS3, mantenendo la cronologia. |
| Non verificato | Un modello scelto a mano che non è stato possibile controllare rispetto al tipo di dispositivo. |
| Download diagnostica | Il file che contiene un'istantanea del sistema, sicura per la privacy, da allegare a una segnalazione di errore. |
| Registrazione di debug | L'opzione che scrive righe di log dettagliate per trovare un problema. |
| Scheda della plancia | Una scheda che SAJ Local aggiunge alle plance di Home Assistant. |
| Scheda flusso di potenza | La scheda che mostra la potenza in tempo reale tra solare, batteria, rete e casa. |
| Scheda stato | La scheda che mostra lo stato di funzionamento, la modalità, le letture principali e i guasti. |
| Scheda guasti | La scheda che elenca i guasti attivi. |
| Scheda batteria | La scheda che mostra le letture della batteria e una riga per ogni modulo. |
| Scheda controlli | La scheda che mostra i controlli condivisi del sistema. |
| Scheda pianificazione | La scheda che mostra le fasce con una linea temporale settimanale. |
| Funzione giorni della settimana per la scheda tile | I sette pulsanti dei giorni che si possono aggiungere a una scheda tile. |
| Badge di stato | Il badge che mostra lo stato di funzionamento e il numero di guasti attivi. |

## Concetti di Home Assistant

| Termine | Significato |
| --- | --- |
| Home Assistant | Il software di domotica di cui SAJ Local è un'integrazione. |
| Integrazione | Software che collega un tipo di dispositivo o servizio a Home Assistant. |
| HACS | Il Home Assistant Community Store, usato per installare SAJ Local. |
| Archivio digitale personalizzato | Un archivio digitale che non è nell'elenco predefinito di HACS e che viene aggiunto a HACS tramite il suo indirizzo; il badge «HACS personalizzato» nei README segnala SAJ Local come tale. |
| Flusso di configurazione | La finestra di configurazione che aggiunge un sistema. |
| Voce di configurazione | La configurazione salvata di un sistema. |
| Sotto-voce | Una parte di una voce di configurazione che si aggiunge e si modifica da sola, come un gruppo di polling o una pianificazione della potenza. |
| Configura | Il pulsante di un'integrazione che ne apre le opzioni. |
| Dispositivi e servizi | La pagina delle impostazioni di Home Assistant che elenca integrazioni, dispositivi ed entità. |
| Impostazioni | La pagina di Home Assistant per configurare Home Assistant. |
| Dispositivo | Il record di Home Assistant di un'apparecchiatura che contiene entità. Ogni sistema è un dispositivo. |
| Entità | Una lettura, un'impostazione o un comando che Home Assistant mostra. |
| ID entità | L'identificatore univoco di un'entità, come sensor.saj_pv_power. |
| Sensore | Un'entità che mostra una lettura. |
| Sensore binario | Un'entità che è accesa o spenta, come un guasto. |
| Numero | Un'entità che contiene un numero che puoi modificare. |
| Selezione | Un'entità che contiene una scelta da un elenco. |
| Interruttore | Un'entità che puoi accendere o spegnere. |
| Ora | Un'entità che contiene un'ora del giorno. |
| Pulsante | Un'entità che esegue un'azione quando viene premuta. |
| Abilitata per impostazione predefinita | Indica se un'entità è attiva quando il sistema viene aggiunto. |
| Disabilitata | Un'entità che Home Assistant non legge né mostra. |
| Problema da riparare | Un avviso in Home Assistant che indica che serve un tuo intervento, con un pulsante Ripara. |
| Plancia | Una schermata di Home Assistant composta da schede. |
| Scheda | Un blocco di una plancia. |
| Scheda tile | Una scheda di Home Assistant che mostra una sola entità e a cui si possono aggiungere funzioni. |
| Badge | Un piccolo elemento nella riga dei badge in alto in una plancia. |
| Automazione | Una regola che fa agire Home Assistant quando accade qualcosa. |
| Aiutante | Un'entità di Home Assistant che crei tu, come un aiutante di pianificazione. |
| Area | Una stanza o un luogo in cui sono raggruppati i dispositivi. |
| Tema | I colori dell'interfaccia di Home Assistant. |
| Lingua | La lingua che un utente di Home Assistant sceglie nella pagina del profilo. |
| Ricarica | Riavviare una sola integrazione senza riavviare Home Assistant. |
| Riavvio | Riavviare Home Assistant. |
| Strumenti per sviluppatori | Le pagine di Home Assistant per controllare gli stati e chiamare le azioni. |
| Log | Il registro dei messaggi di Home Assistant. |
