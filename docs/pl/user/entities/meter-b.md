[en](../../../en-gb/user/entities/meter-b.md) | [de](../../../de/user/entities/meter-b.md) | [nl](../../../nl/user/entities/meter-b.md) | [fr](../../../fr/user/entities/meter-b.md) | [zh](../../../zh-hans/user/entities/meter-b.md) | [es](../../../es/user/entities/meter-b.md) | [it](../../../it/user/entities/meter-b.md) | pl | [sv](../../../sv/user/entities/meter-b.md)

# Licznik B

Licznik B, drugi licznik, który mierzy falownik fotowoltaiczny.

Lista funkcji integracji wyjaśnia encje obszaru Licznik B w [Wyposażenie opcjonalne](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

Liczba encji: 22. Wygenerowano poleceniem `make docs`. Nie edytuj ręcznie.

Prefiks ustawiony w Skonfiguruj trafia po `saj_` w ID każdej encji: Licznik B, na przykład `sensor.saj_house_meter_b_l1_voltage` z prefiksem `house`.

| Nazwa | ID encji | Typ | Jednostka | Modele | Wyposażenie i liczba | Włączona domyślnie |
| --- | --- | --- | --- | --- | --- | --- |
| Napięcie licznika B L1 | `sensor.saj_meter_b_l1_voltage` | Sensor | V | HS3, H2 | Licznik B | Nie |
| Prąd licznika B L1 | `sensor.saj_meter_b_l1_current` | Sensor | A | HS3, H2 | Licznik B | Nie |
| Moc licznika B L1 | `sensor.saj_meter_b_l1_power` | Sensor | W | HS3, H2 | Licznik B | Nie |
| Moc pozorna licznika B L1 | `sensor.saj_meter_b_l1_apparent_power` | Sensor | VA | HS3, H2 | Licznik B | Nie |
| Współczynnik mocy licznika B L1 | `sensor.saj_meter_b_l1_power_factor` | Sensor | - | HS3, H2 | Licznik B | Nie |
| Częstotliwość licznika B L1 | `sensor.saj_meter_b_l1_frequency` | Sensor | Hz | HS3, H2 | Licznik B | Nie |
| Napięcie licznika B L2 | `sensor.saj_meter_b_l2_voltage` | Sensor | V | HS3, H2 | Licznik B; Faza 2 i wyższe | Nie |
| Prąd licznika B L2 | `sensor.saj_meter_b_l2_current` | Sensor | A | HS3, H2 | Licznik B; Faza 2 i wyższe | Nie |
| Moc licznika B L2 | `sensor.saj_meter_b_l2_power` | Sensor | W | HS3, H2 | Licznik B; Faza 2 i wyższe | Nie |
| Moc pozorna licznika B L2 | `sensor.saj_meter_b_l2_apparent_power` | Sensor | VA | HS3, H2 | Licznik B; Faza 2 i wyższe | Nie |
| Współczynnik mocy licznika B L2 | `sensor.saj_meter_b_l2_power_factor` | Sensor | - | HS3, H2 | Licznik B; Faza 2 i wyższe | Nie |
| Częstotliwość licznika B L2 | `sensor.saj_meter_b_l2_frequency` | Sensor | Hz | HS3, H2 | Licznik B; Faza 2 i wyższe | Nie |
| Napięcie licznika B L3 | `sensor.saj_meter_b_l3_voltage` | Sensor | V | HS3, H2 | Licznik B; Faza 3 i wyższe | Nie |
| Prąd licznika B L3 | `sensor.saj_meter_b_l3_current` | Sensor | A | HS3, H2 | Licznik B; Faza 3 i wyższe | Nie |
| Moc licznika B L3 | `sensor.saj_meter_b_l3_power` | Sensor | W | HS3, H2 | Licznik B; Faza 3 i wyższe | Nie |
| Moc pozorna licznika B L3 | `sensor.saj_meter_b_l3_apparent_power` | Sensor | VA | HS3, H2 | Licznik B; Faza 3 i wyższe | Nie |
| Współczynnik mocy licznika B L3 | `sensor.saj_meter_b_l3_power_factor` | Sensor | - | HS3, H2 | Licznik B; Faza 3 i wyższe | Nie |
| Częstotliwość licznika B L3 | `sensor.saj_meter_b_l3_frequency` | Sensor | Hz | HS3, H2 | Licznik B; Faza 3 i wyższe | Nie |
| Moc bierna licznika B L1 | `sensor.saj_meter_b_l1_reactive_power` | Sensor | var | HS3 | Licznik B | Nie |
| Moc bierna licznika B L2 | `sensor.saj_meter_b_l2_reactive_power` | Sensor | var | HS3 | Licznik B; Faza 2 i wyższe | Nie |
| Moc bierna licznika B L3 | `sensor.saj_meter_b_l3_reactive_power` | Sensor | var | HS3 | Licznik B; Faza 3 i wyższe | Nie |
| Moc licznika B | `sensor.saj_meter_b_power` | Sensor | W | HS3, H2 | Licznik B | Tak |
