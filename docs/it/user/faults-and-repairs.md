[en](../../en-gb/user/faults-and-repairs.md) | [de](../../de/user/faults-and-repairs.md) | [nl](../../nl/user/faults-and-repairs.md) | [fr](../../fr/user/faults-and-repairs.md) | [zh](../../zh-hans/user/faults-and-repairs.md) | [es](../../es/user/faults-and-repairs.md) | it | [pl](../../pl/user/faults-and-repairs.md) | [sv](../../sv/user/faults-and-repairs.md)

# Guasti dell'apparecchiatura e riparazioni

La pagina Guasti dell'apparecchiatura e riparazioni spiega come SAJ Local mostra i guasti segnalati dall'inverter, dalla batteria e dal caricatore EV, e quali problemi da riparare SAJ Local solleva in Home Assistant. L'elenco completo del comportamento dei guasti è nella sezione [Guasti dell'apparecchiatura e riparazioni](../../../custom_components/saj_local/docs/features.md#device-faults-and-repairs) dell'elenco delle funzionalità dell'integrazione. Ogni entità di guasto è nelle [entità Guasti](entities/faults.md) del riferimento delle entità.

I guasti dell'apparecchiatura e i problemi da riparare sono distinti. Un guasto dell'apparecchiatura è un'entità che riporta ciò che dice l'apparecchiatura. Un problema da riparare è un problema della connessione di SAJ Local con l'apparecchiatura o della configurazione di SAJ Local, e Home Assistant elenca il problema in Impostazioni e Riparazioni.

## Guasti dell'apparecchiatura

Ogni guasto con nome dell'inverter, della batteria e del caricatore EV è un sensore binario con la classe di dispositivo problema, abilitato per impostazione predefinita. Un guasto ha una cronologia e può far scattare un'automazione.

- **Riepilogo:** l'inverter, la batteria e il caricatore EV hanno ciascuno un guasto di riepilogo, per esempio Guasto dell'inverter, che è acceso quando l'apparecchiatura segnala qualsiasi cosa.
- **Non riconosciuto:** ogni apparecchiatura ha anche un guasto non riconosciuto, acceso quando l'inverter imposta un bit senza significato documentato. Il [download della diagnostica](troubleshooting.md#download-della-diagnostica) elenca il registro e il bit, così puoi segnalare il bit.
- **Un solo ID entità su ogni modello:** un guasto ha un solo ID entità su ogni modello che lo segnala. Un guasto che un modello non segnala non ha entità su quel modello.
- **Moduli batteria:** ogni modulo batteria ha un'entità di guasto e una di avviso. Un HS3 ha un modulo. Un H2 ne ha fino a quattro.
- **Apparecchiature non installate:** i guasti della batteria esistono solo quando c'è una batteria installata, e i guasti del caricatore EV solo quando c'è un caricatore EV installato. Vedi le [apparecchiature opzionali](optional-equipment.md).
- **Un registro di guasti che non può essere letto:** i guasti che dipendono dal registro non sono disponibili. SAJ Local non tira a indovinare.
- **Il log:** un guasto che si accende registra un avviso che nomina il sistema e il guasto. Quando il guasto si cancella, SAJ Local registra una riga informativa.

La [scheda guasti](cards/faults-card.md) elenca in una plancia i guasti attivi di un sistema, con da quanto tempo è iniziato ciascuno. Il pulsante Cancella guasto della scheda invia il comando Cancella il guasto attuale, che richiede [Consenti controllo](changing-settings.md#consentire-il-controllo).

## Problemi da riparare

SAJ Local solleva un problema da riparare per una condizione su cui puoi intervenire.

| Problema da riparare | Sollevato quando | Che cosa puoi fare |
| --- | --- | --- |
| Il sistema è impostato sul modello sbagliato | L'inverter all'indirizzo si identifica con un modello diverso da quello scelto. | Una correzione adotta il modello che SAJ Local ha trovato. Vedi la [sostituzione dell'inverter](replacing-the-inverter.md). |
| Il sistema ora raggiunge un inverter diverso | L'inverter all'indirizzo ha un altro numero di serie. | Una correzione adotta il nuovo inverter. Vedi la [sostituzione dell'inverter](replacing-the-inverter.md). |
| Il sistema raggiunge un dispositivo non riconosciuto | Il tipo di dispositivo non è un modello riconosciuto. | Scegli il modello in Configura. SAJ Local usa poi il modello non verificato. |
| Il sistema ha letture che l'inverter rifiuta | L'inverter ha rifiutato le letture tre volte di seguito. | Una correzione disabilita le entità elencate, così SAJ Local non le legge più. Vedi la [protezione dell'inverter](protecting-the-inverter.md#quando-linverter-rifiuta-una-lettura). |
| Il sistema ha smesso di rispondere | L'inverter non ha risposto per 15 minuti. | Controlla l'alimentazione, la rete e gli altri client Modbus. Il problema scompare alla prima lettura riuscita. |
| Un'apparecchiatura non viene più rilevata | Un'apparecchiatura che SAJ Local aveva rilevato non viene più rilevata. | Controlla l'apparecchiatura, oppure imposta l'apparecchiatura su Non installato in Configura. Vedi le [apparecchiature opzionali](optional-equipment.md#quando-unapparecchiatura-memorizzata-non-viene-più-rilevata). |

![Un problema da riparare in Home Assistant che dice che SAJ HS3MOCK000000000003 ha letture che l'inverter rifiuta](../../images/it/faults-and-repairs-repair-issue.png)

I primi tre problemi sono i problemi del modello. Per un sistema è aperto un solo problema del modello, e il problema che indica che il sistema ha smesso di rispondere non viene sollevato mentre è aperto un problema del modello.

Un problema da riparare scompare quando la condizione del problema termina, o quando rimuovi il sistema. Il problema sulle letture rifiutate scompare anche quando disabiliti un'entità elencata.

## Non ancora supportato

- Un problema da riparare per un guasto dell'apparecchiatura. I guasti dell'apparecchiatura sono entità, e l'integrazione non solleva un problema da riparare per un guasto.
