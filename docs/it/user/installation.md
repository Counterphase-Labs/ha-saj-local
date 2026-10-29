[en](../../en-gb/user/installation.md) | [de](../../de/user/installation.md) | [nl](../../nl/user/installation.md) | [fr](../../fr/user/installation.md) | [zh](../../zh-hans/user/installation.md) | [es](../../es/user/installation.md) | it | [pl](../../pl/user/installation.md) | [sv](../../sv/user/installation.md)

# Installazione

La pagina Installazione installa SAJ Local con HACS, il Home Assistant Community Store. L'elenco completo di ciò che fa la configurazione è nella sezione [Configurazione e rilevamento](../../../custom_components/saj_local/docs/features.md#setup-and-detection) dell'elenco delle funzionalità dell'integrazione.

SAJ Local non ha ancora una versione stabile. Ogni versione prima di `1.0.0` è una beta, vedi [versioni beta](#versioni-beta). Controlla le [apparecchiature supportate](supported-equipment.md) prima di installare.

## Che cosa serve

- Home Assistant alla versione minima indicata in [`hacs.json`](../../../hacs.json), e HACS.
- Un inverter SAJ supportato che risponde a Modbus TCP sulla tua rete locale. Servono l'indirizzo dell'inverter, e la porta e l'ID unità quando la porta o l'ID unità non sono quelli predefiniti.
- Nient'altro. SAJ Local comunica direttamente con l'inverter e non invia nulla a un servizio cloud.

## Installare

1. Apri SAJ Local in HACS con il primo pulsante qui sotto. HACS ti chiede di aggiungere il repository se il repository non è ancora in elenco.
2. Scarica SAJ Local in HACS.
3. Riavvia Home Assistant.
4. Aggiungi il tuo sistema con il secondo pulsante qui sotto, oppure segui [inizia](getting-started.md).

[![Apri la tua istanza di Home Assistant e apri il repository di SAJ Local in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Counterphase-Labs&repository=ha-saj-local&category=integration)
[![Apri la tua istanza di Home Assistant e inizia a configurare SAJ Local.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=saj_local)

SAJ Local fornisce le schede della plancia, quindi non c'è alcuna risorsa di scheda da aggiungere. Vedi le [schede della plancia](cards/README.md).

## Versioni beta

Fino alla prima versione stabile, ogni versione di SAJ Local è una beta. In HACS, apri SAJ Local, apri il menu, scegli Scarica di nuovo, attiva «Mostra versioni beta» e scarica la beta più recente. Senza l'interruttore, HACS installa la versione di sviluppo di SAJ Local.
