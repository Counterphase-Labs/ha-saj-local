[en](../../../en-gb/user/entities/meter-b.md) | de | [nl](../../../nl/user/entities/meter-b.md) | [fr](../../../fr/user/entities/meter-b.md) | [zh](../../../zh-hans/user/entities/meter-b.md) | [es](../../../es/user/entities/meter-b.md) | [it](../../../it/user/entities/meter-b.md) | [pl](../../../pl/user/entities/meter-b.md) | [sv](../../../sv/user/entities/meter-b.md)

# Zähler B

Zähler B, der zweite Zähler, der einen Solar-Wechselrichter misst.

Die Funktionsliste der Integration erklärt die Entitäten (Zähler B) in [Optionale Ausstattung](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

22 Entitäten. Erzeugt von `make docs`. Nicht von Hand bearbeiten.

Ein in Konfigurieren gesetztes Präfix steht nach `saj_` in der ID jeder Entität (Zähler B), zum Beispiel `sensor.saj_house_meter_b_l1_voltage` mit dem Präfix `house`.

| Name | Entitäts-ID | Typ | Einheit | Modelle | Ausstattung und Anzahl | Standardmäßig aktiviert |
| --- | --- | --- | --- | --- | --- | --- |
| Zähler B L1 Spannung | `sensor.saj_meter_b_l1_voltage` | Sensor | V | HS3, H2 | Zähler B | Nein |
| Zähler B L1 Strom | `sensor.saj_meter_b_l1_current` | Sensor | A | HS3, H2 | Zähler B | Nein |
| Zähler B L1 Leistung | `sensor.saj_meter_b_l1_power` | Sensor | W | HS3, H2 | Zähler B | Nein |
| Zähler B L1 Scheinleistung | `sensor.saj_meter_b_l1_apparent_power` | Sensor | VA | HS3, H2 | Zähler B | Nein |
| Zähler B L1 Leistungsfaktor | `sensor.saj_meter_b_l1_power_factor` | Sensor | - | HS3, H2 | Zähler B | Nein |
| Zähler B L1 Frequenz | `sensor.saj_meter_b_l1_frequency` | Sensor | Hz | HS3, H2 | Zähler B | Nein |
| Zähler B L2 Spannung | `sensor.saj_meter_b_l2_voltage` | Sensor | V | HS3, H2 | Zähler B; Phase 2 und höher | Nein |
| Zähler B L2 Strom | `sensor.saj_meter_b_l2_current` | Sensor | A | HS3, H2 | Zähler B; Phase 2 und höher | Nein |
| Zähler B L2 Leistung | `sensor.saj_meter_b_l2_power` | Sensor | W | HS3, H2 | Zähler B; Phase 2 und höher | Nein |
| Zähler B L2 Scheinleistung | `sensor.saj_meter_b_l2_apparent_power` | Sensor | VA | HS3, H2 | Zähler B; Phase 2 und höher | Nein |
| Zähler B L2 Leistungsfaktor | `sensor.saj_meter_b_l2_power_factor` | Sensor | - | HS3, H2 | Zähler B; Phase 2 und höher | Nein |
| Zähler B L2 Frequenz | `sensor.saj_meter_b_l2_frequency` | Sensor | Hz | HS3, H2 | Zähler B; Phase 2 und höher | Nein |
| Zähler B L3 Spannung | `sensor.saj_meter_b_l3_voltage` | Sensor | V | HS3, H2 | Zähler B; Phase 3 und höher | Nein |
| Zähler B L3 Strom | `sensor.saj_meter_b_l3_current` | Sensor | A | HS3, H2 | Zähler B; Phase 3 und höher | Nein |
| Zähler B L3 Leistung | `sensor.saj_meter_b_l3_power` | Sensor | W | HS3, H2 | Zähler B; Phase 3 und höher | Nein |
| Zähler B L3 Scheinleistung | `sensor.saj_meter_b_l3_apparent_power` | Sensor | VA | HS3, H2 | Zähler B; Phase 3 und höher | Nein |
| Zähler B L3 Leistungsfaktor | `sensor.saj_meter_b_l3_power_factor` | Sensor | - | HS3, H2 | Zähler B; Phase 3 und höher | Nein |
| Zähler B L3 Frequenz | `sensor.saj_meter_b_l3_frequency` | Sensor | Hz | HS3, H2 | Zähler B; Phase 3 und höher | Nein |
| Zähler B L1 Blindleistung | `sensor.saj_meter_b_l1_reactive_power` | Sensor | var | HS3 | Zähler B | Nein |
| Zähler B L2 Blindleistung | `sensor.saj_meter_b_l2_reactive_power` | Sensor | var | HS3 | Zähler B; Phase 2 und höher | Nein |
| Zähler B L3 Blindleistung | `sensor.saj_meter_b_l3_reactive_power` | Sensor | var | HS3 | Zähler B; Phase 3 und höher | Nein |
| Zähler B Leistung | `sensor.saj_meter_b_power` | Sensor | W | HS3, H2 | Zähler B | Ja |
