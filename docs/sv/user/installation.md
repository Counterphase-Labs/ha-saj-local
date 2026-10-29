[en](../../en-gb/user/installation.md) | [de](../../de/user/installation.md) | [nl](../../nl/user/installation.md) | [fr](../../fr/user/installation.md) | [zh](../../zh-hans/user/installation.md) | [es](../../es/user/installation.md) | [it](../../it/user/installation.md) | [pl](../../pl/user/installation.md) | sv

# Installation

Sidan Installation installerar SAJ Local med HACS, Home Assistant Community Store. Den fullständiga listan över vad installationen gör finns i avsnittet [Installation och identifiering](../../../custom_components/saj_local/docs/features.md#setup-and-detection) i integrationens funktionslista.

SAJ Local har ännu ingen stabil version. Varje version före `1.0.0` är en beta, se [betaversioner](#betaversioner). Kontrollera den [utrustning som stöds](supported-equipment.md) innan du installerar.

## Vad du behöver

- Home Assistant i den lägsta version som anges i [`hacs.json`](../../../hacs.json), och HACS.
- En SAJ-växelriktare som stöds och som svarar på Modbus TCP i ditt lokala nätverk. Du behöver växelriktarens adress, samt port och enhets-ID när porten eller enhets-ID:t inte är standardvärdet.
- Inget annat. SAJ Local pratar direkt med växelriktaren och skickar ingenting till någon molntjänst.

## Installera

1. Öppna SAJ Local i HACS med den första knappen nedan. HACS ber dig lägga till arkivet om arkivet inte finns i listan ännu.
2. Ladda ner SAJ Local i HACS.
3. Starta om Home Assistant.
4. Lägg till ditt system med den andra knappen nedan, eller följ [kom igång](getting-started.md).

[![Öppna din Home Assistant-instans och öppna arkivet för SAJ Local i HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Counterphase-Labs&repository=ha-saj-local&category=integration)
[![Öppna din Home Assistant-instans och börja konfigurera SAJ Local.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=saj_local)

SAJ Local levererar instrumentpanelskort, så det finns ingen kortresurs att lägga till. Se [instrumentpanelskort](cards/README.md).

## Betaversioner

Fram till den första stabila versionen är varje version av SAJ Local en beta. Öppna SAJ Local i HACS, öppna menyn, välj Ladda ner igen, slå på "Visa betaversioner" och ladda ner den senaste betaversionen. Utan reglaget installerar HACS utvecklingsversionen av SAJ Local.
