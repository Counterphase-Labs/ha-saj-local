[en](../../../en-gb/user/entities/settings.md) | [de](../../../de/user/entities/settings.md) | [nl](../../../nl/user/entities/settings.md) | [fr](../../../fr/user/entities/settings.md) | [zh](../../../zh-hans/user/entities/settings.md) | [es](../../../es/user/entities/settings.md) | [it](../../../it/user/entities/settings.md) | [pl](../../../pl/user/entities/settings.md) | sv

# Inställningar

Inställningar och kommandon som ändrar växelriktaren.

Integrationens funktionslista förklarar entiteterna för Inställningar i [Ändra inställningar](../../../../custom_components/saj_local/docs/features.md#changing-settings).

22 entiteter. Genereras av `make docs`. Redigera inte för hand.

Ett prefix som anges i Konfigurera hamnar efter `saj_` i ID:t för varje entitet i Inställningar, till exempel `number.saj_house_passive_mode` med prefixet `house`.

| Namn | Entitets-ID | Typ | Enhet | Modeller | Utrustning och antal | Aktiverad som standard |
| --- | --- | --- | --- | --- | --- | --- |
| Passivt läge | `number.saj_passive_mode` | Nummer | - | HS3, H2 | - | Nej |
| Passiv nätladdningseffekt | `number.saj_passive_grid_charge_power` | Nummer | % | HS3, H2 | - | Nej |
| Passiv näturladdningseffekt | `number.saj_passive_grid_discharge_power` | Nummer | % | HS3, H2 | - | Nej |
| Applikationsläge | `select.saj_application_mode` | Val | - | HS3, H2 | - | Ja |
| Nätimporteffektgräns | `number.saj_grid_import_power_limit` | Nummer | % | HS3, H2 | - | Nej |
| Nätexporteffektgräns | `number.saj_grid_export_power_limit` | Nummer | % | HS3, H2 | - | Nej |
| Exporteffektgräns | `number.saj_export_limit_power` | Nummer | % | HS3, H2 | - | Nej |
| Exportströmgräns | `number.saj_export_limit_current` | Nummer | A | HS3, H2 | - | Nej |
| Exportgränsläge | `select.saj_export_limit_mode` | Val | - | HS3, H2 | - | Nej |
| Tidsstyrning viloläge | `select.saj_time_of_use_idle_mode` | Val | - | HS3, H2 | - | Nej |
| Tidsstyrning urladdning till nätet | `switch.saj_time_of_use_grid_discharge` | Brytare | - | HS3, H2 | - | Nej |
| LED-läge | `select.saj_led_mode` | Val | - | HS3, H2 | - | Nej |
| Elbilsladdare är aktiverad | `switch.saj_ev_enabled` | Brytare | - | HS3 | - | Nej |
| Rensa aktuellt fel | `button.saj_clear_current_fault` | Knapp | - | HS3, H2 | - | Nej |
| Starta om växelriktaren | `button.saj_restart_inverter` | Knapp | - | HS3, H2 | - | Nej |
| Synkronisera klockan | `button.saj_synchronise_clock` | Knapp | - | HS3, H2 | - | Nej |
| EMS-tidsgräns | `number.saj_ems_timeout` | Nummer | s | HS3 | - | Nej |
| EMS-importeffektgräns växelriktare | `number.saj_ems_inverter_import_power_limit` | Nummer | % | HS3 | - | Nej |
| EMS-exporteffektgräns växelriktare | `number.saj_ems_inverter_export_power_limit` | Nummer | % | HS3 | - | Nej |
| EMS-soleffektgräns | `number.saj_ems_pv_power_limit` | Nummer | % | HS3 | - | Nej |
| Ta bort EMS-soleffektgräns | `button.saj_ems_pv_power_limit_remove` | Knapp | - | HS3 | - | Nej |
| Summer | `switch.saj_buzzer` | Brytare | - | H2 | - | Nej |
