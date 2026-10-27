[en](../../../en-gb/user/entities/settings.md) | [de](../../../de/user/entities/settings.md) | [nl](../../../nl/user/entities/settings.md) | [fr](../../../fr/user/entities/settings.md) | [zh](../../../zh-hans/user/entities/settings.md) | [es](../../../es/user/entities/settings.md) | it | [pl](../../../pl/user/entities/settings.md) | [sv](../../../sv/user/entities/settings.md)

# Impostazioni

Impostazioni e comandi che modificano l'inverter.

Le entità dell'area «Impostazioni» sono descritte nell'elenco delle funzionalità dell'integrazione, in [Modifica delle impostazioni](../../../../custom_components/saj_local/docs/features.md#changing-settings).

22 entità. Generato da `make docs`. Non modificare a mano.

Un prefisso impostato in Configura va dopo `saj_` nell'ID di ogni entità dell'area «Impostazioni», per esempio `number.saj_house_passive_mode` con il prefisso `house`.

| Nome | ID entità | Tipo | Unità | Modelli | Apparecchiature e quantità | Abilitata per impostazione predefinita |
| --- | --- | --- | --- | --- | --- | --- |
| Modalità passiva | `number.saj_passive_mode` | Numero | - | HS3, H2 | - | No |
| Potenza di carica dalla rete in modalità passiva | `number.saj_passive_grid_charge_power` | Numero | % | HS3, H2 | - | No |
| Potenza di scarica verso la rete in modalità passiva | `number.saj_passive_grid_discharge_power` | Numero | % | HS3, H2 | - | No |
| Modalità applicativa | `select.saj_application_mode` | Selezione | - | HS3, H2 | - | Sì |
| Limite della potenza prelevata dalla rete | `number.saj_grid_import_power_limit` | Numero | % | HS3, H2 | - | No |
| Limite della potenza immessa in rete | `number.saj_grid_export_power_limit` | Numero | % | HS3, H2 | - | No |
| Potenza del limite di immissione | `number.saj_export_limit_power` | Numero | % | HS3, H2 | - | No |
| Corrente del limite di immissione | `number.saj_export_limit_current` | Numero | A | HS3, H2 | - | No |
| Modalità del limite di immissione | `select.saj_export_limit_mode` | Selezione | - | HS3, H2 | - | No |
| Modalità di inattività a fasce orarie | `select.saj_time_of_use_idle_mode` | Selezione | - | HS3, H2 | - | No |
| Scarica verso la rete a fasce orarie | `switch.saj_time_of_use_grid_discharge` | Interruttore | - | HS3, H2 | - | No |
| Modalità LED | `select.saj_led_mode` | Selezione | - | HS3, H2 | - | No |
| Caricatore EV abilitato | `switch.saj_ev_enabled` | Interruttore | - | HS3 | - | No |
| Cancella il guasto attuale | `button.saj_clear_current_fault` | Pulsante | - | HS3, H2 | - | No |
| Riavvia l'inverter | `button.saj_restart_inverter` | Pulsante | - | HS3, H2 | - | No |
| Sincronizza l'orologio | `button.saj_synchronise_clock` | Pulsante | - | HS3, H2 | - | No |
| Timeout EMS | `number.saj_ems_timeout` | Numero | s | HS3 | - | No |
| Limite EMS della potenza prelevata dall'inverter | `number.saj_ems_inverter_import_power_limit` | Numero | % | HS3 | - | No |
| Limite EMS della potenza immessa dall'inverter | `number.saj_ems_inverter_export_power_limit` | Numero | % | HS3 | - | No |
| Limite EMS della potenza solare | `number.saj_ems_pv_power_limit` | Numero | % | HS3 | - | No |
| Rimuovi il limite EMS della potenza solare | `button.saj_ems_pv_power_limit_remove` | Pulsante | - | HS3 | - | No |
| Cicalino | `switch.saj_buzzer` | Interruttore | - | H2 | - | No |
