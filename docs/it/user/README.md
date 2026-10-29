[en](../../en-gb/user/README.md) | [de](../../de/user/README.md) | [nl](../../nl/user/README.md) | [fr](../../fr/user/README.md) | [zh](../../zh-hans/user/README.md) | [es](../../es/user/README.md) | it | [pl](../../pl/user/README.md) | [sv](../../sv/user/README.md)

# Documentazione utente di SAJ Local

SAJ Local è un'integrazione locale per Home Assistant. SAJ Local legge un impianto solare SAJ HS3 o H2 direttamente dall'inverter tramite Modbus TCP sulla tua rete e, quando consenti il controllo, modifica da Home Assistant le impostazioni dell'inverter. SAJ Local non richiede alcun account cloud e limita le richieste all'inverter, in modo che il modulo di comunicazione dell'inverter continui a funzionare.

SAJ Local è un'integrazione non ufficiale, creata dalla comunità. SAJ non produce, non supporta e non approva SAJ Local. Vedi l'[esclusione di responsabilità](#esclusione-di-responsabilità).

SAJ Local non ha ancora una versione stabile. Ogni versione prima di `1.0.0` è una beta, vedi [versioni beta](installation.md#versioni-beta). Ogni pagina qui sotto indica che cosa non è ancora supportato. La documentazione riguarda l'HS3 e l'H2 e segnala le differenze con una nota come «Solo HS3». Le schermate provengono da sistemi simulati, quindi le letture non sono reali.

## Da dove iniziare

1. [Installa SAJ Local](installation.md) con HACS.
2. Controlla che il tuo inverter sia tra le [apparecchiature supportate](supported-equipment.md).
3. [Inizia](getting-started.md): aggiungi il tuo primo sistema.
4. Leggi le [apparecchiature opzionali](optional-equipment.md), che SAJ Local rileva per te.

## Capire il tuo sistema

- [Entità e prefisso](entities-and-prefix.md): che cosa sono le entità, come si formano gli ID entità e come aggiungere un prefisso.
- [Riferimento delle entità](entities/README.md): ogni entità, con l'ID entità, i modelli, le apparecchiature e l'impostazione predefinita. Generato dall'integrazione.
- [Polling](polling.md): ogni quanto viene letto l'inverter e come leggere alcune entità più velocemente o più lentamente.
- [Protezione dell'inverter](protecting-the-inverter.md): i limiti che SAJ Local mantiene sulle proprie richieste.

## Modificare le impostazioni

- [Modifica delle impostazioni](changing-settings.md): consentire il controllo, cambiare le impostazioni e usare EMS.
- [Controllo della potenza](power-control.md): mantenere la batteria, il collegamento alla rete o l'inverter a una potenza impostata, a mano o con una pianificazione.
- [Sostituzione dell'inverter](replacing-the-inverter.md): spostare un sistema su un nuovo inverter, o tra un H2 e un HS3, mantenendo la cronologia.

## Plance

- [Schede della plancia](cards/README.md): le schede, la funzione per la scheda tile e il badge che SAJ Local aggiunge a Home Assistant.

## Termini

- [Nomenclatura](nomenclature.md): i termini SAJ e Home Assistant che l'integrazione, le schede e la documentazione usano, con il loro significato.

## Quando qualcosa non va

- [Guasti dell'apparecchiatura e riparazioni](faults-and-repairs.md): i guasti che l'apparecchiatura segnala e i problemi da riparare che SAJ Local solleva.
- [Risoluzione dei problemi](troubleshooting.md): diagnostica, registrazione di debug e dove chiedere aiuto.

## Che cosa può fare ogni parte

Gli elenchi delle funzionalità indicano che cosa è realizzato oggi: [l'integrazione](../../../custom_components/saj_local/docs/features.md) e [le schede](../../../frontend/docs/features.md).

Sviluppatori: vedi la [documentazione per sviluppatori](../developer/README.md).

## Esclusione di responsabilità

SAJ Local è un'integrazione indipendente, creata dalla comunità. SAJ Local non è affiliato a SAJ (Guangzhou Sanjing Electric Co., Ltd.), e SAJ e le sue controllate e affiliate non hanno autorizzato, sponsorizzato né approvato SAJ Local.

SAJ, il logo SAJ e tutti i nomi di prodotto, i nomi di modello e i marchi correlati sono di proprietà dei rispettivi titolari. La documentazione usa i nomi solo per identificare le apparecchiature con cui funziona SAJ Local.

Il software è fornito così com'è, senza garanzie di alcun tipo. Usi SAJ Local a tuo rischio: gli autori non accettano alcuna responsabilità per danni alle apparecchiature, perdita di dati, perdita della garanzia o qualsiasi altra conseguenza dell'uso di SAJ Local. L'avvertenza vale in particolare per la scrittura di impostazioni sul tuo inverter.

## Ringraziamenti

Il supporto dell'H2 si basa sulla ricerca sui registri e sulle prove sul campo di stanus74 in [SAJ H2 Modbus](https://github.com/stanus74/home-assistant-saj-h2-modbus). Grazie.
