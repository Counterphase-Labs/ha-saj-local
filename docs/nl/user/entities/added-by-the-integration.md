[en](../../../en-gb/user/entities/added-by-the-integration.md) | [de](../../../de/user/entities/added-by-the-integration.md) | nl | [fr](../../../fr/user/entities/added-by-the-integration.md) | [zh](../../../zh-hans/user/entities/added-by-the-integration.md) | [es](../../../es/user/entities/added-by-the-integration.md) | [it](../../../it/user/entities/added-by-the-integration.md) | [pl](../../../pl/user/entities/added-by-the-integration.md) | [sv](../../../sv/user/entities/added-by-the-integration.md)

# Toegevoegd door de integratie

Entiteiten die de integratie toevoegt buiten de registercatalogus.

De functielijst van de integratie legt de Toegevoegd door de integratie-entiteiten uit in [Instellingen wijzigen](../../../../custom_components/saj_local/docs/features.md#changing-settings) en [Vermogensregeling](../../../../custom_components/saj_local/docs/features.md#power-control).

7 entiteiten. Gegenereerd door `make docs`. Niet met de hand bewerken.

Een voorvoegsel dat in Configureren is ingesteld komt na `saj_` in de ID van elke Toegevoegd door de integratie-entiteit, bijvoorbeeld `binary_sensor.saj_house_control_allowed` met het voorvoegsel `house`.

| Naam | Entiteits-ID | Type | Eenheid | Modellen | Apparatuur en aantallen | Standaard ingeschakeld |
| --- | --- | --- | --- | --- | --- | --- |
| Bediening toegestaan | `binary_sensor.saj_control_allowed` | Binaire sensor | - | HS3, H2 | - | Ja |
| Vermogensregeling batterij | `switch.saj_battery_power_control` | Schakelaar | - | HS3, H2 | Batterij | Nee |
| Vermogensdoel batterij | `number.saj_battery_power_target` | Nummer | W | HS3, H2 | Batterij | Nee |
| Vermogensregeling net | `switch.saj_grid_power_control` | Schakelaar | - | HS3 | Meter A | Nee |
| Vermogensdoel net | `number.saj_grid_power_target` | Nummer | W | HS3 | Meter A | Nee |
| Vermogensregeling omvormer | `switch.saj_inverter_power_control` | Schakelaar | - | HS3 | - | Nee |
| Vermogensdoel omvormer | `number.saj_inverter_power_target` | Nummer | W | HS3 | - | Nee |
