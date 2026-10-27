[en](../../../en-gb/user/entities/added-by-the-integration.md) | [de](../../../de/user/entities/added-by-the-integration.md) | [nl](../../../nl/user/entities/added-by-the-integration.md) | [fr](../../../fr/user/entities/added-by-the-integration.md) | [zh](../../../zh-hans/user/entities/added-by-the-integration.md) | [es](../../../es/user/entities/added-by-the-integration.md) | [it](../../../it/user/entities/added-by-the-integration.md) | [pl](../../../pl/user/entities/added-by-the-integration.md) | sv

# Tillagt av integrationen

Entiteter som integrationen lägger till utanför registerkatalogen.

Integrationens funktionslista förklarar entiteterna för Tillagt av integrationen i [Ändra inställningar](../../../../custom_components/saj_local/docs/features.md#changing-settings) och [Effektstyrning](../../../../custom_components/saj_local/docs/features.md#power-control).

7 entiteter. Genereras av `make docs`. Redigera inte för hand.

Ett prefix som anges i Konfigurera hamnar efter `saj_` i ID:t för varje entitet i Tillagt av integrationen, till exempel `binary_sensor.saj_house_control_allowed` med prefixet `house`.

| Namn | Entitets-ID | Typ | Enhet | Modeller | Utrustning och antal | Aktiverad som standard |
| --- | --- | --- | --- | --- | --- | --- |
| Styrning tillåten | `binary_sensor.saj_control_allowed` | Binär sensor | - | HS3, H2 | - | Ja |
| Batterieffektstyrning | `switch.saj_battery_power_control` | Brytare | - | HS3, H2 | Batteri | Nej |
| Batterieffektmål | `number.saj_battery_power_target` | Nummer | W | HS3, H2 | Batteri | Nej |
| Näteffektstyrning | `switch.saj_grid_power_control` | Brytare | - | HS3 | Mätare A | Nej |
| Näteffektmål | `number.saj_grid_power_target` | Nummer | W | HS3 | Mätare A | Nej |
| Växelriktareffektstyrning | `switch.saj_inverter_power_control` | Brytare | - | HS3 | - | Nej |
| Växelriktareffektmål | `number.saj_inverter_power_target` | Nummer | W | HS3 | - | Nej |
