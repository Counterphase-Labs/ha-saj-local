[en](../../../en-gb/user/entities/added-by-the-integration.md) | [de](../../../de/user/entities/added-by-the-integration.md) | [nl](../../../nl/user/entities/added-by-the-integration.md) | [fr](../../../fr/user/entities/added-by-the-integration.md) | [zh](../../../zh-hans/user/entities/added-by-the-integration.md) | [es](../../../es/user/entities/added-by-the-integration.md) | [it](../../../it/user/entities/added-by-the-integration.md) | pl | [sv](../../../sv/user/entities/added-by-the-integration.md)

# Dodane przez integrację

Encje, które integracja dodaje poza katalogiem rejestrów.

Lista funkcji integracji wyjaśnia encje obszaru Dodane przez integrację w [Zmiana ustawień](../../../../custom_components/saj_local/docs/features.md#changing-settings) i [Sterowanie mocą](../../../../custom_components/saj_local/docs/features.md#power-control).

Liczba encji: 7. Wygenerowano poleceniem `make docs`. Nie edytuj ręcznie.

Prefiks ustawiony w Skonfiguruj trafia po `saj_` w ID każdej encji: Dodane przez integrację, na przykład `binary_sensor.saj_house_control_allowed` z prefiksem `house`.

| Nazwa | ID encji | Typ | Jednostka | Modele | Wyposażenie i liczba | Włączona domyślnie |
| --- | --- | --- | --- | --- | --- | --- |
| Sterowanie dozwolone | `binary_sensor.saj_control_allowed` | Sensor binarny | - | HS3, H2 | - | Tak |
| Sterowanie mocą baterii | `switch.saj_battery_power_control` | Przełącznik | - | HS3, H2 | Bateria | Nie |
| Moc zadana baterii | `number.saj_battery_power_target` | Liczba | W | HS3, H2 | Bateria | Nie |
| Sterowanie mocą sieci | `switch.saj_grid_power_control` | Przełącznik | - | HS3 | Licznik A | Nie |
| Moc zadana sieci | `number.saj_grid_power_target` | Liczba | W | HS3 | Licznik A | Nie |
| Sterowanie mocą falownika | `switch.saj_inverter_power_control` | Przełącznik | - | HS3 | - | Nie |
| Moc zadana falownika | `number.saj_inverter_power_target` | Liczba | W | HS3 | - | Nie |
