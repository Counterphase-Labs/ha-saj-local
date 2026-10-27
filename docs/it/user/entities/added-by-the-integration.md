[en](../../../en-gb/user/entities/added-by-the-integration.md) | [de](../../../de/user/entities/added-by-the-integration.md) | [nl](../../../nl/user/entities/added-by-the-integration.md) | [fr](../../../fr/user/entities/added-by-the-integration.md) | [zh](../../../zh-hans/user/entities/added-by-the-integration.md) | [es](../../../es/user/entities/added-by-the-integration.md) | it | [pl](../../../pl/user/entities/added-by-the-integration.md) | [sv](../../../sv/user/entities/added-by-the-integration.md)

# Aggiunte dall'integrazione

Entità che l'integrazione aggiunge al di fuori del catalogo dei registri.

Le entità dell'area «Aggiunte dall'integrazione» sono descritte nell'elenco delle funzionalità dell'integrazione, in [Modifica delle impostazioni](../../../../custom_components/saj_local/docs/features.md#changing-settings) e [Controllo della potenza](../../../../custom_components/saj_local/docs/features.md#power-control).

7 entità. Generato da `make docs`. Non modificare a mano.

Un prefisso impostato in Configura va dopo `saj_` nell'ID di ogni entità dell'area «Aggiunte dall'integrazione», per esempio `binary_sensor.saj_house_control_allowed` con il prefisso `house`.

| Nome | ID entità | Tipo | Unità | Modelli | Apparecchiature e quantità | Abilitata per impostazione predefinita |
| --- | --- | --- | --- | --- | --- | --- |
| Controllo consentito | `binary_sensor.saj_control_allowed` | Sensore binario | - | HS3, H2 | - | Sì |
| Controllo della potenza della batteria | `switch.saj_battery_power_control` | Interruttore | - | HS3, H2 | Batteria | No |
| Obiettivo di potenza della batteria | `number.saj_battery_power_target` | Numero | W | HS3, H2 | Batteria | No |
| Controllo della potenza della rete | `switch.saj_grid_power_control` | Interruttore | - | HS3 | Contatore A | No |
| Obiettivo di potenza della rete | `number.saj_grid_power_target` | Numero | W | HS3 | Contatore A | No |
| Controllo della potenza dell'inverter | `switch.saj_inverter_power_control` | Interruttore | - | HS3 | - | No |
| Obiettivo di potenza dell'inverter | `number.saj_inverter_power_target` | Numero | W | HS3 | - | No |
