[en](../../../en-gb/user/entities/settings.md) | [de](../../../de/user/entities/settings.md) | [nl](../../../nl/user/entities/settings.md) | [fr](../../../fr/user/entities/settings.md) | [zh](../../../zh-hans/user/entities/settings.md) | [es](../../../es/user/entities/settings.md) | [it](../../../it/user/entities/settings.md) | pl | [sv](../../../sv/user/entities/settings.md)

# Ustawienia

Ustawienia i polecenia, które zmieniają falownik.

Lista funkcji integracji wyjaśnia encje obszaru Ustawienia w [Zmiana ustawień](../../../../custom_components/saj_local/docs/features.md#changing-settings).

Liczba encji: 22. Wygenerowano poleceniem `make docs`. Nie edytuj ręcznie.

Prefiks ustawiony w Skonfiguruj trafia po `saj_` w ID każdej encji: Ustawienia, na przykład `number.saj_house_passive_mode` z prefiksem `house`.

| Nazwa | ID encji | Typ | Jednostka | Modele | Wyposażenie i liczba | Włączona domyślnie |
| --- | --- | --- | --- | --- | --- | --- |
| Tryb pasywny | `number.saj_passive_mode` | Liczba | - | HS3, H2 | - | Nie |
| Moc ładowania z sieci w trybie pasywnym | `number.saj_passive_grid_charge_power` | Liczba | % | HS3, H2 | - | Nie |
| Moc oddawania do sieci w trybie pasywnym | `number.saj_passive_grid_discharge_power` | Liczba | % | HS3, H2 | - | Nie |
| Tryb aplikacji | `select.saj_application_mode` | Selektor | - | HS3, H2 | - | Tak |
| Limit mocy poboru z sieci | `number.saj_grid_import_power_limit` | Liczba | % | HS3, H2 | - | Nie |
| Limit mocy oddawania do sieci | `number.saj_grid_export_power_limit` | Liczba | % | HS3, H2 | - | Nie |
| Moc limitu oddawania | `number.saj_export_limit_power` | Liczba | % | HS3, H2 | - | Nie |
| Prąd limitu oddawania | `number.saj_export_limit_current` | Liczba | A | HS3, H2 | - | Nie |
| Tryb limitu oddawania | `select.saj_export_limit_mode` | Selektor | - | HS3, H2 | - | Nie |
| Tryb bezczynności taryfy czasowej | `select.saj_time_of_use_idle_mode` | Selektor | - | HS3, H2 | - | Nie |
| Oddawanie do sieci w taryfie czasowej | `switch.saj_time_of_use_grid_discharge` | Przełącznik | - | HS3, H2 | - | Nie |
| Tryb LED | `select.saj_led_mode` | Selektor | - | HS3, H2 | - | Nie |
| Ładowarka EV włączona | `switch.saj_ev_enabled` | Przełącznik | - | HS3 | - | Nie |
| Wyczyść bieżącą usterkę | `button.saj_clear_current_fault` | Przycisk | - | HS3, H2 | - | Nie |
| Uruchom falownik ponownie | `button.saj_restart_inverter` | Przycisk | - | HS3, H2 | - | Nie |
| Synchronizuj zegar | `button.saj_synchronise_clock` | Przycisk | - | HS3, H2 | - | Nie |
| Limit czasu EMS | `number.saj_ems_timeout` | Liczba | s | HS3 | - | Nie |
| Limit mocy poboru falownika EMS | `number.saj_ems_inverter_import_power_limit` | Liczba | % | HS3 | - | Nie |
| Limit mocy oddawania falownika EMS | `number.saj_ems_inverter_export_power_limit` | Liczba | % | HS3 | - | Nie |
| Limit mocy słonecznej EMS | `number.saj_ems_pv_power_limit` | Liczba | % | HS3 | - | Nie |
| Usuń limit mocy słonecznej EMS | `button.saj_ems_pv_power_limit_remove` | Przycisk | - | HS3 | - | Nie |
| Buzzer | `switch.saj_buzzer` | Przełącznik | - | H2 | - | Nie |
