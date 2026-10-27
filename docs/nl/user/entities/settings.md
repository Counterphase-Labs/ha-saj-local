[en](../../../en-gb/user/entities/settings.md) | [de](../../../de/user/entities/settings.md) | nl | [fr](../../../fr/user/entities/settings.md) | [zh](../../../zh-hans/user/entities/settings.md) | [es](../../../es/user/entities/settings.md) | [it](../../../it/user/entities/settings.md) | [pl](../../../pl/user/entities/settings.md) | [sv](../../../sv/user/entities/settings.md)

# Instellingen

Instellingen en opdrachten die de omvormer wijzigen.

De functielijst van de integratie legt de Instellingen-entiteiten uit in [Instellingen wijzigen](../../../../custom_components/saj_local/docs/features.md#changing-settings).

22 entiteiten. Gegenereerd door `make docs`. Niet met de hand bewerken.

Een voorvoegsel dat in Configureren is ingesteld komt na `saj_` in de ID van elke Instellingen-entiteit, bijvoorbeeld `number.saj_house_passive_mode` met het voorvoegsel `house`.

| Naam | Entiteits-ID | Type | Eenheid | Modellen | Apparatuur en aantallen | Standaard ingeschakeld |
| --- | --- | --- | --- | --- | --- | --- |
| Passieve modus | `number.saj_passive_mode` | Nummer | - | HS3, H2 | - | Nee |
| Passief netoplaadvermogen | `number.saj_passive_grid_charge_power` | Nummer | % | HS3, H2 | - | Nee |
| Passief netontlaadvermogen | `number.saj_passive_grid_discharge_power` | Nummer | % | HS3, H2 | - | Nee |
| Toepassingsmodus | `select.saj_application_mode` | Selectie | - | HS3, H2 | - | Ja |
| Limiet afnamevermogen net | `number.saj_grid_import_power_limit` | Nummer | % | HS3, H2 | - | Nee |
| Limiet terugleveringsvermogen net | `number.saj_grid_export_power_limit` | Nummer | % | HS3, H2 | - | Nee |
| Limiet terugleveringsvermogen | `number.saj_export_limit_power` | Nummer | % | HS3, H2 | - | Nee |
| Limiet terugleveringsstroom | `number.saj_export_limit_current` | Nummer | A | HS3, H2 | - | Nee |
| Modus terugleveringslimiet | `select.saj_export_limit_mode` | Selectie | - | HS3, H2 | - | Nee |
| Tijdgestuurd inactieve modus | `select.saj_time_of_use_idle_mode` | Selectie | - | HS3, H2 | - | Nee |
| Tijdgestuurde netontlading | `switch.saj_time_of_use_grid_discharge` | Schakelaar | - | HS3, H2 | - | Nee |
| LED-modus | `select.saj_led_mode` | Selectie | - | HS3, H2 | - | Nee |
| EV-lader ingeschakeld | `switch.saj_ev_enabled` | Schakelaar | - | HS3 | - | Nee |
| Huidige storing wissen | `button.saj_clear_current_fault` | Knop | - | HS3, H2 | - | Nee |
| Omvormer herstarten | `button.saj_restart_inverter` | Knop | - | HS3, H2 | - | Nee |
| Klok synchroniseren | `button.saj_synchronise_clock` | Knop | - | HS3, H2 | - | Nee |
| EMS-time-out | `number.saj_ems_timeout` | Nummer | s | HS3 | - | Nee |
| EMS-limiet afnamevermogen omvormer | `number.saj_ems_inverter_import_power_limit` | Nummer | % | HS3 | - | Nee |
| EMS-limiet terugleveringsvermogen omvormer | `number.saj_ems_inverter_export_power_limit` | Nummer | % | HS3 | - | Nee |
| EMS-limiet zonnevermogen | `number.saj_ems_pv_power_limit` | Nummer | % | HS3 | - | Nee |
| EMS-limiet zonnevermogen verwijderen | `button.saj_ems_pv_power_limit_remove` | Knop | - | HS3 | - | Nee |
| Zoemer | `switch.saj_buzzer` | Schakelaar | - | H2 | - | Nee |
