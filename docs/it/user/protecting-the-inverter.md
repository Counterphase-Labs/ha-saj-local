[en](../../en-gb/user/protecting-the-inverter.md) | [de](../../de/user/protecting-the-inverter.md) | [nl](../../nl/user/protecting-the-inverter.md) | [fr](../../fr/user/protecting-the-inverter.md) | [zh](../../zh-hans/user/protecting-the-inverter.md) | [es](../../es/user/protecting-the-inverter.md) | it | [pl](../../pl/user/protecting-the-inverter.md) | [sv](../../sv/user/protecting-the-inverter.md)

# Protezione dell'inverter

La pagina Protezione dell'inverter elenca i limiti che SAJ Local mantiene su tutto ciò che invia, in modo che il modulo di comunicazione dell'inverter continui a servire Home Assistant. Un modulo può smettere di servire un client che esegue il polling troppo intensamente, quindi nessuna impostazione rimuove un limite. L'elenco completo è nella sezione [Protezione dell'inverter](../../../custom_components/saj_local/docs/features.md#protecting-the-inverter) dell'elenco delle funzionalità dell'integrazione.

## I limiti

- **Una connessione, una richiesta alla volta.** SAJ Local apre una connessione a un inverter e attende ogni risposta prima di inviare la richiesta successiva, con una breve pausa tra le richieste.
- **40 richieste in 60 secondi.** Il limite vale per indirizzo di inverter. SAJ Local conta attraverso le ricariche, quindi una ricarica, un nuovo tentativo di configurazione o un controllo della connessione non possono superare il limite. Una richiesta oltre il limite attende.
- **I registri vicini condividono una richiesta.** SAJ Local legge in una sola richiesta i registri vicini tra loro, mai oltre un blocco che il modello documenta. Una richiesta non è mai più grande di 32 registri sull'HS3 o di 56 sull'H2. Raggruppare le entità che stanno vicine costa meno, vedi il [polling](polling.md).
- **Nessun nuovo tentativo nello stesso ciclo.** Dopo una lettura fallita, l'attesa prima del tentativo successivo raddoppia a partire dall'intervallo più breve, fino a 5 minuti. L'attesa sopravvive alle ricariche. Il primo ciclo riuscito legge di nuovo tutto.
- **Ogni attesa ha un limite di tempo.** Un inverter bloccato termina un ciclo come fallimento e non ferma il polling. Una risposta tardiva o estranea viene scartata.
- **Una connessione chiusa viene riaperta una volta.** Quel ciclo legge poi di nuovo ogni entità abilitata, quindi nessun valore è più vecchio della riconnessione.
- **Al massimo 20 modifiche in 60 secondi.** Vedi la [modifica delle impostazioni](changing-settings.md#che-cosa-succede-a-una-modifica). Una modifica oltre il limite viene rifiutata e non messa in coda.

## Quando l'inverter rifiuta una lettura

Un rifiuto è una risposta e non un fallimento. Solo le entità nella richiesta rifiutata diventano non disponibili, e le altre continuano ad aggiornarsi.

1. SAJ Local divide a metà la richiesta rifiutata nei cicli successivi, finché non trova l'entità rifiutata.
2. Un'entità rifiutata tre volte di seguito viene sospesa. L'entità appare come non disponibile e non viene più letta.
3. SAJ Local riprova un'entità sospesa una volta al giorno, e ogni volta che l'integrazione viene caricata. L'entità torna quando il registro risponde.
4. Un problema da riparare elenca le entità sospese. La correzione del problema disabilita le entità, così SAJ Local non le legge più in via definitiva. Vedi [guasti e riparazioni](faults-and-repairs.md#problemi-da-riparare).

## Quando l'inverter smette di rispondere

Un problema da riparare indica quando un inverter non risponde da 15 minuti. Il problema scompare alla prima lettura riuscita. Controlla l'alimentazione dell'inverter e del modulo di comunicazione, la rete, e che nessun altro client Modbus occupi la connessione.

## Non ancora supportato

- La modifica dei limiti. I limiti proteggono l'inverter, quindi nessuna impostazione alza un limite.
