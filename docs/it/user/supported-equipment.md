[en](../../en-gb/user/supported-equipment.md) | [de](../../de/user/supported-equipment.md) | [nl](../../nl/user/supported-equipment.md) | [fr](../../fr/user/supported-equipment.md) | [zh](../../zh-hans/user/supported-equipment.md) | [es](../../es/user/supported-equipment.md) | it | [pl](../../pl/user/supported-equipment.md) | [sv](../../sv/user/supported-equipment.md)

# Apparecchiature supportate

La pagina Apparecchiature supportate elenca i prodotti SAJ che SAJ Local supporta, le apparecchiature opzionali che ogni modello può avere e che cosa non è ancora supportato. L'elenco completo di ciò che fa la configurazione è nella sezione [Configurazione e rilevamento](../../../custom_components/saj_local/docs/features.md#setup-and-detection) dell'elenco delle funzionalità dell'integrazione.

## Modelli supportati

SAJ Local riconosce un modello dal tipo di dispositivo comunicato dall'inverter. Qualsiasi altro tipo di dispositivo non viene riconosciuto.

| Modello | Riconosciuto come | Apparecchiature opzionali che SAJ Local rileva |
| --- | --- | --- |
| HS3 | Tipo di dispositivo `0x1610`, tre fasi | Batteria, Contatore A, Contatore B, Caricatore EV, sistema in parallelo |
| H2, monofase, due stringhe solari | Tipo di dispositivo `0x005a` | Batteria, Contatore A, Contatore B, sistema in parallelo |
| H2, monofase, tre stringhe solari | Tipo di dispositivo `0x005b` | Batteria, Contatore A, Contatore B, sistema in parallelo |

Le differenze tra i modelli che si notano nell'uso:

- **Caricatore EV:** solo l'HS3. L'H2 non ha entità del caricatore EV, fasce del caricatore EV né sezione del caricatore EV nella scheda controlli.
- **Moduli batteria:** un H2 ha entità per fino a cinque moduli batteria. Un HS3 ha entità per un modulo batteria. Vedi le [apparecchiature opzionali](optional-equipment.md).
- **EMS:** solo l'HS3. Vedi la [modifica delle impostazioni](changing-settings.md#ems).
- **Controllo della potenza:** l'HS3 offre Batteria, Rete e Inverter. L'H2 offre solo Batteria. Vedi il [controllo della potenza](power-control.md).

Le [apparecchiature opzionali](optional-equipment.md) spiegano come funziona il rilevamento e come correggerlo. Il [riferimento delle entità](entities/README.md) elenca quale modello e quale apparecchiatura richiede ogni entità.

## Non ancora supportato

- Il rilevamento automatico riconosce solo i tre tipi di dispositivo nella tabella. Altri prodotti SAJ, come l'HS2, l'H1 e l'AS1, non vengono riconosciuti.
- Altre varianti dell'H2, come l'H2 trifase, comunicano altri tipi di dispositivo e non vengono riconosciute automaticamente. Puoi scegliere il modello a mano, e SAJ Local lo contrassegna come non verificato. Le letture possono essere errate, perché SAJ Local non può controllarle. Vedi [inizia](getting-started.md#quando-linverter-non-viene-riconosciuto).
- La modifica delle impostazioni su un sistema con un modello non verificato. La lettura funziona, e ogni modifica viene rifiutata.

## Su che cosa si basa il supporto

Il supporto dell'HS3 è stato verificato a mano su un HS3 reale. Il supporto dell'H2 si basa sulla documentazione del protocollo SAJ e su segnalazioni sul campo, e non è stato verificato a mano su un H2. Anche la scrittura delle impostazioni e il controllo della potenza sull'H2 si basano su documentazione e segnalazioni sul campo.
