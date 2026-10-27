[en](../../../en-gb/user/entities/added-by-the-integration.md) | de | [nl](../../../nl/user/entities/added-by-the-integration.md) | [fr](../../../fr/user/entities/added-by-the-integration.md) | [zh](../../../zh-hans/user/entities/added-by-the-integration.md) | [es](../../../es/user/entities/added-by-the-integration.md) | [it](../../../it/user/entities/added-by-the-integration.md) | [pl](../../../pl/user/entities/added-by-the-integration.md) | [sv](../../../sv/user/entities/added-by-the-integration.md)

# Von der Integration hinzugefügt

Entitäten, die die Integration außerhalb des Registerkatalogs hinzufügt.

Die Funktionsliste der Integration erklärt die Entitäten (Von der Integration hinzugefügt) in [Einstellungen ändern](../../../../custom_components/saj_local/docs/features.md#changing-settings) und [Leistungssteuerung](../../../../custom_components/saj_local/docs/features.md#power-control).

7 Entitäten. Erzeugt von `make docs`. Nicht von Hand bearbeiten.

Ein in Konfigurieren gesetztes Präfix steht nach `saj_` in der ID jeder Entität (Von der Integration hinzugefügt), zum Beispiel `binary_sensor.saj_house_control_allowed` mit dem Präfix `house`.

| Name | Entitäts-ID | Typ | Einheit | Modelle | Ausstattung und Anzahl | Standardmäßig aktiviert |
| --- | --- | --- | --- | --- | --- | --- |
| Steuerung zugelassen | `binary_sensor.saj_control_allowed` | Binärsensor | - | HS3, H2 | - | Ja |
| Batterie-Leistungssteuerung | `switch.saj_battery_power_control` | Schalter | - | HS3, H2 | Batterie | Nein |
| Batterie-Leistungsziel | `number.saj_battery_power_target` | Zahl | W | HS3, H2 | Batterie | Nein |
| Netz-Leistungssteuerung | `switch.saj_grid_power_control` | Schalter | - | HS3 | Zähler A | Nein |
| Netz-Leistungsziel | `number.saj_grid_power_target` | Zahl | W | HS3 | Zähler A | Nein |
| Wechselrichter-Leistungssteuerung | `switch.saj_inverter_power_control` | Schalter | - | HS3 | - | Nein |
| Wechselrichter-Leistungsziel | `number.saj_inverter_power_target` | Zahl | W | HS3 | - | Nein |
