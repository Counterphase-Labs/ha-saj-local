[en](../../../en-gb/user/entities/settings.md) | de | [nl](../../../nl/user/entities/settings.md) | [fr](../../../fr/user/entities/settings.md) | [zh](../../../zh-hans/user/entities/settings.md) | [es](../../../es/user/entities/settings.md) | [it](../../../it/user/entities/settings.md) | [pl](../../../pl/user/entities/settings.md) | [sv](../../../sv/user/entities/settings.md)

# Einstellungen

Einstellungen und Befehle, die den Wechselrichter ändern.

Die Funktionsliste der Integration erklärt die Entitäten (Einstellungen) in [Einstellungen ändern](../../../../custom_components/saj_local/docs/features.md#changing-settings).

22 Entitäten. Erzeugt von `make docs`. Nicht von Hand bearbeiten.

Ein in Konfigurieren gesetztes Präfix steht nach `saj_` in der ID jeder Entität (Einstellungen), zum Beispiel `number.saj_house_passive_mode` mit dem Präfix `house`.

| Name | Entitäts-ID | Typ | Einheit | Modelle | Ausstattung und Anzahl | Standardmäßig aktiviert |
| --- | --- | --- | --- | --- | --- | --- |
| Passivmodus | `number.saj_passive_mode` | Zahl | - | HS3, H2 | - | Nein |
| Passivmodus Netz-Ladeleistung | `number.saj_passive_grid_charge_power` | Zahl | % | HS3, H2 | - | Nein |
| Passivmodus Netz-Entladeleistung | `number.saj_passive_grid_discharge_power` | Zahl | % | HS3, H2 | - | Nein |
| Anwendungsmodus | `select.saj_application_mode` | Auswahl | - | HS3, H2 | - | Ja |
| Netzbezugsleistungsgrenze | `number.saj_grid_import_power_limit` | Zahl | % | HS3, H2 | - | Nein |
| Netzeinspeiseleistungsgrenze | `number.saj_grid_export_power_limit` | Zahl | % | HS3, H2 | - | Nein |
| Einspeisebegrenzungsleistung | `number.saj_export_limit_power` | Zahl | % | HS3, H2 | - | Nein |
| Einspeisebegrenzungsstrom | `number.saj_export_limit_current` | Zahl | A | HS3, H2 | - | Nein |
| Einspeisebegrenzungsmodus | `select.saj_export_limit_mode` | Auswahl | - | HS3, H2 | - | Nein |
| Leerlaufmodus der Zeitsteuerung | `select.saj_time_of_use_idle_mode` | Auswahl | - | HS3, H2 | - | Nein |
| Netzentladung der Zeitsteuerung | `switch.saj_time_of_use_grid_discharge` | Schalter | - | HS3, H2 | - | Nein |
| LED-Modus | `select.saj_led_mode` | Auswahl | - | HS3, H2 | - | Nein |
| Wallbox aktiviert | `switch.saj_ev_enabled` | Schalter | - | HS3 | - | Nein |
| Aktuellen Fehler quittieren | `button.saj_clear_current_fault` | Schaltfläche | - | HS3, H2 | - | Nein |
| Wechselrichter neu starten | `button.saj_restart_inverter` | Schaltfläche | - | HS3, H2 | - | Nein |
| Uhr synchronisieren | `button.saj_synchronise_clock` | Schaltfläche | - | HS3, H2 | - | Nein |
| EMS-Timeout | `number.saj_ems_timeout` | Zahl | s | HS3 | - | Nein |
| EMS-Wechselrichter-Bezugsleistungsgrenze | `number.saj_ems_inverter_import_power_limit` | Zahl | % | HS3 | - | Nein |
| EMS-Wechselrichter-Einspeiseleistungsgrenze | `number.saj_ems_inverter_export_power_limit` | Zahl | % | HS3 | - | Nein |
| EMS-Solarleistungsgrenze | `number.saj_ems_pv_power_limit` | Zahl | % | HS3 | - | Nein |
| EMS-Solarleistungsgrenze entfernen | `button.saj_ems_pv_power_limit_remove` | Schaltfläche | - | HS3 | - | Nein |
| Summer | `switch.saj_buzzer` | Schalter | - | H2 | - | Nein |
