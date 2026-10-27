[en](../../en-gb/user/replacing-the-inverter.md) | [de](../../de/user/replacing-the-inverter.md) | [nl](../../nl/user/replacing-the-inverter.md) | [fr](../../fr/user/replacing-the-inverter.md) | [zh](../../zh-hans/user/replacing-the-inverter.md) | [es](../../es/user/replacing-the-inverter.md) | it | [pl](../../pl/user/replacing-the-inverter.md) | [sv](../../sv/user/replacing-the-inverter.md)

# Sostituzione dell'inverter

La pagina Sostituzione dell'inverter spiega come spostare un sistema su un nuovo inverter, o tra un H2 e un HS3, mantenendo il dispositivo, le entità e la cronologia. L'elenco completo è nella sezione [Sostituzione del modello](../../../custom_components/saj_local/docs/features.md#model-replacement) dell'elenco delle funzionalità dell'integrazione.

## Spostare un sistema di proposito

1. Assicurati che il nuovo inverter sia raggiungibile. Se il nuovo inverter ha un altro indirizzo, inserisci l'indirizzo nel passaggio successivo.
2. Apri Configura, l'ingranaggio sulla riga del sistema nella pagina dell'integrazione SAJ Local.
3. Cambia l'host, la porta o l'ID unità se l'indirizzo è cambiato. Lascia Modello su Automatico, oppure scegli il modello se l'inverter non viene riconosciuto.
4. Scegli Invia, poi conferma la sostituzione. La conferma nomina il modello e il numero di serie che SAJ Local ha trovato.

Dopo la conferma, il dispositivo, le entità, i nomi delle entità e la cronologia restano con il sistema. Un'entità mantiene la cronologia attraverso lo spostamento quando entrambi i modelli hanno l'entità. SAJ Local dimentica le apparecchiature rilevate sul vecchio inverter e il conteggio dei moduli batteria del vecchio inverter, e rileva di nuovo le apparecchiature sul nuovo inverter.

## Quando l'inverter all'indirizzo cambia senza di te

SAJ Local controlla l'identità dell'inverter ogni volta che il sistema viene caricato. Quando l'inverter all'indirizzo si identifica con un altro modello, o ha un altro numero di serie, SAJ Local non carica il sistema e solleva un problema da riparare. La correzione del problema da riparare mostra il modello e il numero di serie che l'inverter comunica ora, e adotta l'inverter che confermi.

- ID entità, cronologia, Consenti controllo e ogni altra impostazione restano invariati.
- Quando l'inverter comunica qualcosa di diverso da ciò che il modulo mostrava, il modulo lo dice e mostra i nuovi valori invece di salvare i vecchi.
- Quando il dispositivo all'indirizzo non è un modello riconosciuto, un problema da riparare lo dice e rimanda a Configura. Non c'è nulla da adottare. Scegli il modello a mano, vedi [inizia](getting-started.md#quando-linverter-non-viene-riconosciuto).

I problemi da riparare sono elencati in [guasti e riparazioni](faults-and-repairs.md#problemi-da-riparare).

## Non ancora supportato

- L'adozione di un inverter che appartiene già a un altro sistema. SAJ Local rifiuta l'adozione.
