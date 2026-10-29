[en](../../en-gb/user/installation.md) | [de](../../de/user/installation.md) | nl | [fr](../../fr/user/installation.md) | [zh](../../zh-hans/user/installation.md) | [es](../../es/user/installation.md) | [it](../../it/user/installation.md) | [pl](../../pl/user/installation.md) | [sv](../../sv/user/installation.md)

# Installatie

De pagina Installatie installeert SAJ Local met HACS, de Home Assistant Community Store. De volledige lijst van wat de installatie doet staat in de sectie [Installatie en detectie](../../../custom_components/saj_local/docs/features.md#setup-and-detection) van de functielijst van de integratie.

SAJ Local heeft nog geen stabiele release. Elke release vóór `1.0.0` is een bèta, zie [bètaversies](#bètaversies). Controleer de [ondersteunde apparatuur](supported-equipment.md) voordat u installeert.

## Wat u nodig hebt

- Home Assistant op de minimumversie die in [`hacs.json`](../../../hacs.json) staat, en HACS.
- Een ondersteunde SAJ-omvormer die op uw lokale netwerk antwoordt via Modbus TCP. U hebt het adres van de omvormer nodig, en de poort en het unit-ID wanneer de poort of het unit-ID niet de standaard is.
- Verder niets. SAJ Local praat rechtstreeks met de omvormer en stuurt niets naar een cloudservice.

## Installeren

1. Open SAJ Local in HACS met de eerste knop hieronder. HACS vraagt u de repository toe te voegen als de repository nog niet in de lijst staat.
2. Download SAJ Local in HACS.
3. Herstart Home Assistant.
4. Voeg uw systeem toe met de tweede knop hieronder, of volg [aan de slag](getting-started.md).

[![Open uw Home Assistant-instantie en open de SAJ Local-repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Counterphase-Labs&repository=ha-saj-local&category=integration)
[![Open uw Home Assistant-instantie en begin met het instellen van SAJ Local.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=saj_local)

SAJ Local levert dashboardkaarten, dus er is geen kaartresource toe te voegen. Zie [dashboardkaarten](cards/README.md).

## Bètaversies

Tot de eerste stabiele release is elke release van SAJ Local een bèta. Open in HACS SAJ Local, open het menu, kies Opnieuw downloaden, zet "Bètaversies tonen" aan en download de nieuwste bèta. Zonder de schakelaar installeert HACS de ontwikkelversie van SAJ Local.
