[en](../../../en-gb/user/entities/inverter-and-pv.md) | de | [nl](../../../nl/user/entities/inverter-and-pv.md) | [fr](../../../fr/user/entities/inverter-and-pv.md) | [zh](../../../zh-hans/user/entities/inverter-and-pv.md) | [es](../../../es/user/entities/inverter-and-pv.md) | [it](../../../it/user/entities/inverter-and-pv.md) | [pl](../../../pl/user/entities/inverter-and-pv.md) | [sv](../../../sv/user/entities/inverter-and-pv.md)

# Wechselrichter und PV

Wechselrichterleistung, Solar-Strings, Notstromanschluss, Energiezähler, Versionen und die Hauslast.

Die Funktionsliste der Integration erklärt die Entitäten (Wechselrichter und PV) in [Geräte und Entitäten](../../../../custom_components/saj_local/docs/features.md#devices-and-entities).

241 Entitäten. Erzeugt von `make docs`. Nicht von Hand bearbeiten.

Ein in Konfigurieren gesetztes Präfix steht nach `saj_` in der ID jeder Entität (Wechselrichter und PV), zum Beispiel `sensor.saj_house_ethernet_protocol_version` mit dem Präfix `house`.

| Name | Entitäts-ID | Typ | Einheit | Modelle | Ausstattung und Anzahl | Standardmäßig aktiviert |
| --- | --- | --- | --- | --- | --- | --- |
| Ethernet-Protokollversion | `sensor.saj_ethernet_protocol_version` | Sensor | - | HS3 | - | Nein |
| Ethernet-MAC-Adresse | `sensor.saj_ethernet_mac_address` | Sensor | - | HS3 | - | Nein |
| Ethernet-Modus | `sensor.saj_ethernet_mode` | Sensor | - | HS3 | - | Nein |
| Ethernet-IP-Adresse | `sensor.saj_ethernet_ip_address` | Sensor | - | HS3 | - | Nein |
| Ethernet-Subnetzmaske | `sensor.saj_ethernet_subnet_mask` | Sensor | - | HS3 | - | Nein |
| Ethernet-Gateway | `sensor.saj_ethernet_gateway` | Sensor | - | HS3 | - | Nein |
| Ethernet-Primär-DNS | `sensor.saj_ethernet_dns_primary` | Sensor | - | HS3 | - | Nein |
| Ethernet-Sekundär-DNS | `sensor.saj_ethernet_dns_secondary` | Sensor | - | HS3 | - | Nein |
| Einstellungsfolge | `sensor.saj_settings_sequence` | Sensor | - | HS3, H2 | - | Nein |
| Einstellungsprotokollversion | `sensor.saj_settings_protocol_version` | Sensor | - | HS3 | - | Nein |
| Zählerkonfiguration | `sensor.saj_meter_configuration` | Sensor | - | HS3, H2 | - | Nein |
| Zähleradresse | `sensor.saj_meter_address` | Sensor | - | HS3, H2 | - | Nein |
| RS485-Adresse | `sensor.saj_rs485_address` | Sensor | - | HS3, H2 | - | Nein |
| RS485-Baudrate | `sensor.saj_rs485_baud_rate` | Sensor | - | HS3, H2 | - | Nein |
| Batterieprotokoll | `sensor.saj_battery_protocol` | Sensor | - | HS3, H2 | - | Nein |
| RS485-Slave-Adresse | `sensor.saj_rs485_slave_address` | Sensor | - | HS3 | - | Nein |
| RS485-Slave-Baudrate | `sensor.saj_rs485_slave_baud_rate` | Sensor | - | HS3 | - | Nein |
| Uhr des Wechselrichters | `sensor.saj_inverter_clock` | Sensor | - | HS3, H2 | - | Nein |
| Betriebsmodus | `sensor.saj_operating_mode` | Sensor | - | HS3, H2 | - | Ja |
| Temperatur des Wechselrichters | `sensor.saj_inverter_temperature` | Sensor | °C | HS3, H2 | - | Ja |
| Umgebungstemperatur | `sensor.saj_ambient_temperature` | Sensor | °C | HS3, H2 | - | Nein |
| Ableitstrom | `sensor.saj_leakage_current` | Sensor | mA | HS3, H2 | - | Nein |
| PV1-Isolationswiderstand | `sensor.saj_pv1_insulation_resistance` | Sensor | kΩ | HS3, H2 | - | Nein |
| PV2-Isolationswiderstand | `sensor.saj_pv2_insulation_resistance` | Sensor | kΩ | HS3, H2 | PV-String 2 und höher | Nein |
| Wechselrichter-Entladeleistungssollwert | `sensor.saj_inverter_discharge_power_setpoint` | Sensor | W | HS3, H2 | - | Nein |
| Wechselrichter-Ladeleistungssollwert | `sensor.saj_inverter_charge_power_setpoint` | Sensor | W | HS3, H2 | - | Nein |
| Batterieprotokoll (wirksam) | `sensor.saj_battery_protocol_active` | Sensor | - | HS3, H2 | - | Nein |
| Zählerkonfiguration (wirksam) | `sensor.saj_meter_configuration_active` | Sensor | - | HS3, H2 | - | Nein |
| Wechselrichterspannung L1 | `sensor.saj_inverter_l1_voltage` | Sensor | V | HS3, H2 | - | Nein |
| Wechselrichterstrom L1 | `sensor.saj_inverter_l1_current` | Sensor | A | HS3, H2 | - | Nein |
| Wechselrichterfrequenz L1 | `sensor.saj_inverter_l1_frequency` | Sensor | Hz | HS3, H2 | - | Nein |
| Wechselrichterleistung L1 | `sensor.saj_inverter_l1_power` | Sensor | W | HS3, H2 | - | Nein |
| Wechselrichterscheinleistung L1 | `sensor.saj_inverter_l1_apparent_power` | Sensor | VA | HS3, H2 | - | Nein |
| Wechselrichterspannung L2 | `sensor.saj_inverter_l2_voltage` | Sensor | V | HS3, H2 | Phase 2 und höher | Nein |
| Wechselrichterstrom L2 | `sensor.saj_inverter_l2_current` | Sensor | A | HS3, H2 | Phase 2 und höher | Nein |
| Wechselrichterfrequenz L2 | `sensor.saj_inverter_l2_frequency` | Sensor | Hz | HS3, H2 | Phase 2 und höher | Nein |
| Wechselrichterleistung L2 | `sensor.saj_inverter_l2_power` | Sensor | W | HS3, H2 | Phase 2 und höher | Nein |
| Wechselrichterscheinleistung L2 | `sensor.saj_inverter_l2_apparent_power` | Sensor | VA | HS3, H2 | Phase 2 und höher | Nein |
| Wechselrichterspannung L3 | `sensor.saj_inverter_l3_voltage` | Sensor | V | HS3, H2 | Phase 3 und höher | Nein |
| Wechselrichterstrom L3 | `sensor.saj_inverter_l3_current` | Sensor | A | HS3, H2 | Phase 3 und höher | Nein |
| Wechselrichterfrequenz L3 | `sensor.saj_inverter_l3_frequency` | Sensor | Hz | HS3, H2 | Phase 3 und höher | Nein |
| Wechselrichterleistung L3 | `sensor.saj_inverter_l3_power` | Sensor | W | HS3, H2 | Phase 3 und höher | Nein |
| Wechselrichterscheinleistung L3 | `sensor.saj_inverter_l3_apparent_power` | Sensor | VA | HS3, H2 | Phase 3 und höher | Nein |
| Notstromspannung L1 | `sensor.saj_backup_l1_voltage` | Sensor | V | HS3, H2 | - | Nein |
| Notstrom-Strom L1 | `sensor.saj_backup_l1_current` | Sensor | A | HS3, H2 | - | Nein |
| Notstromfrequenz L1 | `sensor.saj_backup_l1_frequency` | Sensor | Hz | HS3, H2 | - | Nein |
| Notstromgleichspannung L1 | `sensor.saj_backup_l1_dc_voltage` | Sensor | mV | HS3, H2 | - | Nein |
| Notstromleistung L1 | `sensor.saj_backup_l1_power` | Sensor | W | HS3, H2 | - | Nein |
| Notstromscheinleistung L1 | `sensor.saj_backup_l1_apparent_power` | Sensor | VA | HS3, H2 | - | Nein |
| Notstromspannung L2 | `sensor.saj_backup_l2_voltage` | Sensor | V | HS3, H2 | Phase 2 und höher | Nein |
| Notstrom-Strom L2 | `sensor.saj_backup_l2_current` | Sensor | A | HS3, H2 | Phase 2 und höher | Nein |
| Notstromfrequenz L2 | `sensor.saj_backup_l2_frequency` | Sensor | Hz | HS3, H2 | Phase 2 und höher | Nein |
| Notstromgleichspannung L2 | `sensor.saj_backup_l2_dc_voltage` | Sensor | mV | HS3, H2 | Phase 2 und höher | Nein |
| Notstromleistung L2 | `sensor.saj_backup_l2_power` | Sensor | W | HS3, H2 | Phase 2 und höher | Nein |
| Notstromscheinleistung L2 | `sensor.saj_backup_l2_apparent_power` | Sensor | VA | HS3, H2 | Phase 2 und höher | Nein |
| Notstromspannung L3 | `sensor.saj_backup_l3_voltage` | Sensor | V | HS3, H2 | Phase 3 und höher | Nein |
| Notstrom-Strom L3 | `sensor.saj_backup_l3_current` | Sensor | A | HS3, H2 | Phase 3 und höher | Nein |
| Notstromfrequenz L3 | `sensor.saj_backup_l3_frequency` | Sensor | Hz | HS3, H2 | Phase 3 und höher | Nein |
| Notstromgleichspannung L3 | `sensor.saj_backup_l3_dc_voltage` | Sensor | mV | HS3, H2 | Phase 3 und höher | Nein |
| Notstromleistung L3 | `sensor.saj_backup_l3_power` | Sensor | W | HS3, H2 | Phase 3 und höher | Nein |
| Notstromscheinleistung L3 | `sensor.saj_backup_l3_apparent_power` | Sensor | VA | HS3, H2 | Phase 3 und höher | Nein |
| Zwischenkreisspannung | `sensor.saj_dc_bus_voltage` | Sensor | V | HS3, H2 | - | Nein |
| Zwischenkreisspannung (Slave) | `sensor.saj_dc_bus_slave_voltage` | Sensor | V | HS3, H2 | - | Nein |
| PV1-Spannung | `sensor.saj_pv1_voltage` | Sensor | V | HS3, H2 | - | Ja |
| PV1-Strom | `sensor.saj_pv1_current` | Sensor | A | HS3, H2 | - | Ja |
| PV1-Leistung | `sensor.saj_pv1_power` | Sensor | W | HS3, H2 | - | Ja |
| PV2-Spannung | `sensor.saj_pv2_voltage` | Sensor | V | HS3, H2 | PV-String 2 und höher | Ja |
| PV2-Strom | `sensor.saj_pv2_current` | Sensor | A | HS3, H2 | PV-String 2 und höher | Ja |
| PV2-Leistung | `sensor.saj_pv2_power` | Sensor | W | HS3, H2 | PV-String 2 und höher | Ja |
| Hauslastleistung | `sensor.saj_load_power` | Sensor | W | HS3, H2 | - | Ja |
| Solarleistung | `sensor.saj_pv_power` | Sensor | W | HS3, H2 | - | Ja |
| Wechselrichterleistung | `sensor.saj_inverter_power` | Sensor | W | HS3, H2 | - | Ja |
| Solarenergie heute | `sensor.saj_pv_energy_today` | Sensor | kWh | HS3, H2 | - | Ja |
| Solarenergie diesen Monat | `sensor.saj_pv_energy_month` | Sensor | kWh | HS3, H2 | - | Nein |
| Solarenergie dieses Jahr | `sensor.saj_pv_energy_year` | Sensor | kWh | HS3, H2 | - | Nein |
| Solarenergie gesamt | `sensor.saj_pv_energy_total` | Sensor | kWh | HS3, H2 | - | Ja |
| Hauslastenergie heute | `sensor.saj_load_energy_today` | Sensor | kWh | HS3, H2 | - | Ja |
| Hauslastenergie diesen Monat | `sensor.saj_load_energy_month` | Sensor | kWh | HS3, H2 | - | Nein |
| Hauslastenergie dieses Jahr | `sensor.saj_load_energy_year` | Sensor | kWh | HS3, H2 | - | Nein |
| Hauslastenergie gesamt | `sensor.saj_load_energy_total` | Sensor | kWh | HS3, H2 | - | Ja |
| Notstromlast-Energie heute | `sensor.saj_backup_load_energy_today` | Sensor | kWh | HS3, H2 | - | Ja |
| Notstromlast-Energie diesen Monat | `sensor.saj_backup_load_energy_month` | Sensor | kWh | HS3, H2 | - | Nein |
| Notstromlast-Energie dieses Jahr | `sensor.saj_backup_load_energy_year` | Sensor | kWh | HS3, H2 | - | Nein |
| Notstromlast-Energie gesamt | `sensor.saj_backup_load_energy_total` | Sensor | kWh | HS3, H2 | - | Ja |
| Parallelmodus | `sensor.saj_parallel_mode` | Sensor | - | HS3, H2 | - | Nein |
| Parallelgeräte online | `sensor.saj_parallel_online_count` | Sensor | - | HS3, H2 | - | Nein |
| Netzleistung (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_power` | Sensor | W | HS3 | - | Nein |
| Netzleistung L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_l1_power` | Sensor | W | HS3 | - | Nein |
| Netzspannung L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_l1_voltage` | Sensor | V | HS3 | - | Nein |
| Netzstrom L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_l1_current` | Sensor | A | HS3 | - | Nein |
| Netzfrequenz L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_l1_frequency` | Sensor | Hz | HS3 | - | Nein |
| Netzleistung L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_l2_power` | Sensor | W | HS3 | Phase 2 und höher | Nein |
| Netzspannung L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_l2_voltage` | Sensor | V | HS3 | Phase 2 und höher | Nein |
| Netzstrom L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_l2_current` | Sensor | A | HS3 | Phase 2 und höher | Nein |
| Netzfrequenz L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_l2_frequency` | Sensor | Hz | HS3 | Phase 2 und höher | Nein |
| Netzleistung L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_l3_power` | Sensor | W | HS3 | Phase 3 und höher | Nein |
| Netzspannung L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_l3_voltage` | Sensor | V | HS3 | Phase 3 und höher | Nein |
| Netzstrom L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_l3_current` | Sensor | A | HS3 | Phase 3 und höher | Nein |
| Netzfrequenz L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_l3_frequency` | Sensor | Hz | HS3 | Phase 3 und höher | Nein |
| Wechselrichterleistung (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_inverter_power` | Sensor | W | HS3 | - | Nein |
| Wechselrichterleistung L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_inverter_l1_power` | Sensor | W | HS3 | - | Nein |
| Wechselrichterspannung L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_inverter_l1_voltage` | Sensor | V | HS3 | - | Nein |
| Wechselrichterstrom L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_inverter_l1_current` | Sensor | A | HS3 | - | Nein |
| Wechselrichterfrequenz L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_inverter_l1_frequency` | Sensor | Hz | HS3 | - | Nein |
| Wechselrichterleistung L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_inverter_l2_power` | Sensor | W | HS3 | Phase 2 und höher | Nein |
| Wechselrichterspannung L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_inverter_l2_voltage` | Sensor | V | HS3 | Phase 2 und höher | Nein |
| Wechselrichterstrom L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_inverter_l2_current` | Sensor | A | HS3 | Phase 2 und höher | Nein |
| Wechselrichterfrequenz L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_inverter_l2_frequency` | Sensor | Hz | HS3 | Phase 2 und höher | Nein |
| Wechselrichterleistung L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_inverter_l3_power` | Sensor | W | HS3 | Phase 3 und höher | Nein |
| Wechselrichterspannung L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_inverter_l3_voltage` | Sensor | V | HS3 | Phase 3 und höher | Nein |
| Wechselrichterstrom L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_inverter_l3_current` | Sensor | A | HS3 | Phase 3 und höher | Nein |
| Wechselrichterfrequenz L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_inverter_l3_frequency` | Sensor | Hz | HS3 | Phase 3 und höher | Nein |
| Hauslastleistung (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_load_power` | Sensor | W | HS3 | - | Nein |
| Hauslastleistung L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_load_l1_power` | Sensor | W | HS3 | - | Nein |
| Hauslastspannung L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_load_l1_voltage` | Sensor | V | HS3 | - | Nein |
| Hauslaststrom L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_load_l1_current` | Sensor | A | HS3 | - | Nein |
| Hauslastfrequenz L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_load_l1_frequency` | Sensor | Hz | HS3 | - | Nein |
| Hauslastleistung L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_load_l2_power` | Sensor | W | HS3 | Phase 2 und höher | Nein |
| Hauslastspannung L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_load_l2_voltage` | Sensor | V | HS3 | Phase 2 und höher | Nein |
| Hauslaststrom L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_load_l2_current` | Sensor | A | HS3 | Phase 2 und höher | Nein |
| Hauslastfrequenz L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_load_l2_frequency` | Sensor | Hz | HS3 | Phase 2 und höher | Nein |
| Hauslastleistung L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_load_l3_power` | Sensor | W | HS3 | Phase 3 und höher | Nein |
| Hauslastspannung L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_load_l3_voltage` | Sensor | V | HS3 | Phase 3 und höher | Nein |
| Hauslaststrom L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_load_l3_current` | Sensor | A | HS3 | Phase 3 und höher | Nein |
| Hauslastfrequenz L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_load_l3_frequency` | Sensor | Hz | HS3 | Phase 3 und höher | Nein |
| Netzlastleistung (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_load_power` | Sensor | W | HS3 | - | Nein |
| Netzlastleistung L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_load_l1_power` | Sensor | W | HS3 | - | Nein |
| Netzlastspannung L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_load_l1_voltage` | Sensor | V | HS3 | - | Nein |
| Netzlaststrom L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_load_l1_current` | Sensor | A | HS3 | - | Nein |
| Netzlastfrequenz L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_load_l1_frequency` | Sensor | Hz | HS3 | - | Nein |
| Netzlastleistung L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_load_l2_power` | Sensor | W | HS3 | Phase 2 und höher | Nein |
| Netzlastspannung L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_load_l2_voltage` | Sensor | V | HS3 | Phase 2 und höher | Nein |
| Netzlaststrom L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_load_l2_current` | Sensor | A | HS3 | Phase 2 und höher | Nein |
| Netzlastfrequenz L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_load_l2_frequency` | Sensor | Hz | HS3 | Phase 2 und höher | Nein |
| Netzlastleistung L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_load_l3_power` | Sensor | W | HS3 | Phase 3 und höher | Nein |
| Netzlastspannung L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_load_l3_voltage` | Sensor | V | HS3 | Phase 3 und höher | Nein |
| Netzlaststrom L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_load_l3_current` | Sensor | A | HS3 | Phase 3 und höher | Nein |
| Netzlastfrequenz L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_grid_load_l3_frequency` | Sensor | Hz | HS3 | Phase 3 und höher | Nein |
| Notstromleistung (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_backup_power` | Sensor | W | HS3 | - | Nein |
| Notstromleistung L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_backup_l1_power` | Sensor | W | HS3 | - | Nein |
| Notstromspannung L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_backup_l1_voltage` | Sensor | V | HS3 | - | Nein |
| Notstrom-Strom L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_backup_l1_current` | Sensor | A | HS3 | - | Nein |
| Notstromfrequenz L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_backup_l1_frequency` | Sensor | Hz | HS3 | - | Nein |
| Notstromleistung L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_backup_l2_power` | Sensor | W | HS3 | Phase 2 und höher | Nein |
| Notstromspannung L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_backup_l2_voltage` | Sensor | V | HS3 | Phase 2 und höher | Nein |
| Notstrom-Strom L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_backup_l2_current` | Sensor | A | HS3 | Phase 2 und höher | Nein |
| Notstromfrequenz L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_backup_l2_frequency` | Sensor | Hz | HS3 | Phase 2 und höher | Nein |
| Notstromleistung L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_backup_l3_power` | Sensor | W | HS3 | Phase 3 und höher | Nein |
| Notstromspannung L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_backup_l3_voltage` | Sensor | V | HS3 | Phase 3 und höher | Nein |
| Notstrom-Strom L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_backup_l3_current` | Sensor | A | HS3 | Phase 3 und höher | Nein |
| Notstromfrequenz L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_backup_l3_frequency` | Sensor | Hz | HS3 | Phase 3 und höher | Nein |
| Solarleistung (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_pv_power` | Sensor | W | HS3 | - | Nein |
| PV1-Spannung (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_pv1_voltage` | Sensor | V | HS3 | - | Nein |
| PV1-Strom (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_pv1_current` | Sensor | A | HS3 | - | Nein |
| PV1-Leistung (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_pv1_power` | Sensor | W | HS3 | - | Nein |
| PV2-Spannung (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_pv2_voltage` | Sensor | V | HS3 | PV-String 2 und höher | Nein |
| PV2-Strom (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_pv2_current` | Sensor | A | HS3 | PV-String 2 und höher | Nein |
| PV2-Leistung (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_pv2_power` | Sensor | W | HS3 | PV-String 2 und höher | Nein |
| Generatorleistung (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_generator_power` | Sensor | W | HS3 | - | Nein |
| Generatorleistung L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_generator_l1_power` | Sensor | W | HS3 | - | Nein |
| Generatorspannung L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_generator_l1_voltage` | Sensor | V | HS3 | - | Nein |
| Generatorstrom L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_generator_l1_current` | Sensor | A | HS3 | - | Nein |
| Generatorfrequenz L1 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_generator_l1_frequency` | Sensor | Hz | HS3 | - | Nein |
| Generatorleistung L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_generator_l2_power` | Sensor | W | HS3 | Phase 2 und höher | Nein |
| Generatorspannung L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_generator_l2_voltage` | Sensor | V | HS3 | Phase 2 und höher | Nein |
| Generatorstrom L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_generator_l2_current` | Sensor | A | HS3 | Phase 2 und höher | Nein |
| Generatorfrequenz L2 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_generator_l2_frequency` | Sensor | Hz | HS3 | Phase 2 und höher | Nein |
| Generatorleistung L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_generator_l3_power` | Sensor | W | HS3 | Phase 3 und höher | Nein |
| Generatorspannung L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_generator_l3_voltage` | Sensor | V | HS3 | Phase 3 und höher | Nein |
| Generatorstrom L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_generator_l3_current` | Sensor | A | HS3 | Phase 3 und höher | Nein |
| Generatorfrequenz L3 (5-Minuten-Mittelwert) | `sensor.saj_five_minute_average_generator_l3_frequency` | Sensor | Hz | HS3 | Phase 3 und höher | Nein |
| Produktcode | `sensor.saj_product_code` | Sensor | - | HS3, H2 | - | Nein |
| Display-Softwareversion | `sensor.saj_display_software_version` | Sensor | - | HS3, H2 | - | Nein |
| Master-Softwareversion | `sensor.saj_master_software_version` | Sensor | - | HS3, H2 | - | Nein |
| Slave-Softwareversion | `sensor.saj_slave_software_version` | Sensor | - | HS3, H2 | - | Nein |
| Display-Hardwareversion | `sensor.saj_display_hardware_version` | Sensor | - | HS3, H2 | - | Nein |
| Steuerungs-Hardwareversion | `sensor.saj_control_hardware_version` | Sensor | - | HS3, H2 | - | Nein |
| Leistungsteil-Hardwareversion | `sensor.saj_power_hardware_version` | Sensor | - | HS3, H2 | - | Nein |
| Anzahl der Batteriepacks | `sensor.saj_battery_pack_count` | Sensor | - | HS3, H2 | - | Nein |
| Zähler A Status | `sensor.saj_meter_a_status` | Sensor | - | HS3, H2 | - | Nein |
| Zähler B Status | `sensor.saj_meter_b_status` | Sensor | - | HS3, H2 | - | Nein |
| Notstromlastleistung | `sensor.saj_backup_load_power` | Sensor | W | HS3, H2 | - | Ja |
| Rückstrommodus | `sensor.saj_reverse_flow_mode` | Sensor | - | H2 | - | Nein |
| FCAS-Frequenzhysterese | `sensor.saj_fcas_frequency_hysteresis` | Sensor | Hz | H2 | - | Nein |
| Parallelrolle | `sensor.saj_parallel_role` | Sensor | - | H2 | - | Nein |
| Parallelnummer | `sensor.saj_parallel_number` | Sensor | - | H2 | - | Nein |
| Konfigurierter Parallelmodus | `sensor.saj_parallel_configured_mode` | Sensor | - | H2 | - | Nein |
| Batterie-Eingangsmodus | `sensor.saj_battery_input_mode` | Sensor | - | H2 | - | Nein |
| PV-Eingangsmodus | `sensor.saj_pv_input_mode` | Sensor | - | H2 | - | Nein |
| Netzunabhängiger Modus | `sensor.saj_off_grid_mode` | Sensor | - | H2 | - | Nein |
| Ausgangsspannung (netzunabhängig) | `sensor.saj_off_grid_output_voltage` | Sensor | V | H2 | - | Nein |
| Ausgangsfrequenz (netzunabhängig) | `sensor.saj_off_grid_output_frequency` | Sensor | Hz | H2 | - | Nein |
| Motorfreigabe | `sensor.saj_motor_enable` | Sensor | - | H2 | - | Nein |
| Gerätemodell | `sensor.saj_machine_model` | Sensor | - | H2 | - | Nein |
| Nennleistung | `sensor.saj_rated_power` | Sensor | W | H2 | - | Nein |
| Funktionsflags 1 | `sensor.saj_function_flags_1` | Sensor | - | H2 | - | Nein |
| Funktionsflags 2 | `sensor.saj_function_flags_2` | Sensor | - | H2 | - | Nein |
| Maximale Gleichstromkomponente | `sensor.saj_max_dc_current_component` | Sensor | mA | H2 | - | Nein |
| Maximale Gleichspannungskomponente | `sensor.saj_max_dc_voltage_component` | Sensor | V | H2 | - | Nein |
| Isolationswiderstandsgrenze | `sensor.saj_insulation_resistance_limit` | Sensor | kΩ | H2 | - | Nein |
| Maximaler Ableitstrom | `sensor.saj_max_leakage_current` | Sensor | mA | H2 | - | Nein |
| Wechselrichter-Stopp | `sensor.saj_inverter_stop` | Sensor | - | H2 | - | Nein |
| PV-Startspannung | `sensor.saj_pv_start_voltage` | Sensor | V | H2 | - | Nein |
| PV-Abschaltspannung | `sensor.saj_pv_shutdown_voltage` | Sensor | V | H2 | - | Nein |
| MPPT-Spannung oben | `sensor.saj_mppt_voltage_high` | Sensor | V | H2 | - | Nein |
| MPPT-Spannung unten | `sensor.saj_mppt_voltage_low` | Sensor | V | H2 | - | Nein |
| MPPT-Suchzeit | `sensor.saj_mppt_scan_time` | Sensor | min | H2 | - | Nein |
| Fehleranzahl des Wechselrichters | `sensor.saj_inverter_error_count` | Sensor | - | H2 | - | Nein |
| PV3-Isolationswiderstand | `sensor.saj_pv3_insulation_resistance` | Sensor | kΩ | H2 | PV-String 3 und höher | Nein |
| PV4-Isolationswiderstand | `sensor.saj_pv4_insulation_resistance` | Sensor | kΩ | H2 | PV-String 4 und höher | Nein |
| DRM-Hardwarestatus | `sensor.saj_drm_hardware_status` | Sensor | - | H2 | - | Nein |
| DRM-Softwarestatus | `sensor.saj_drm_software_status` | Sensor | - | H2 | - | Nein |
| Fehleraufzeichnungsfolge | `sensor.saj_fault_record_sequence` | Sensor | - | H2 | - | Nein |
| Anwendungsmodus (wirksam) | `sensor.saj_application_mode_active` | Sensor | - | H2 | - | Nein |
| PV3-Spannung | `sensor.saj_pv3_voltage` | Sensor | V | H2 | PV-String 3 und höher | Ja |
| PV3-Strom | `sensor.saj_pv3_current` | Sensor | A | H2 | PV-String 3 und höher | Ja |
| PV3-Leistung | `sensor.saj_pv3_power` | Sensor | W | H2 | PV-String 3 und höher | Ja |
| PV4-Spannung | `sensor.saj_pv4_voltage` | Sensor | V | H2 | PV-String 4 und höher | Ja |
| PV4-Strom | `sensor.saj_pv4_current` | Sensor | A | H2 | PV-String 4 und höher | Ja |
| PV4-Leistung | `sensor.saj_pv4_power` | Sensor | W | H2 | PV-String 4 und höher | Ja |
| CT-Netzleistung | `sensor.saj_ct_grid_power` | Sensor | W | H2 | - | Nein |
| CT-Netzscheinleistung | `sensor.saj_ct_grid_apparent_power` | Sensor | VA | H2 | - | Nein |
| CT-Solarleistung | `sensor.saj_ct_pv_power` | Sensor | W | H2 | - | Nein |
| CT-Solarscheinleistung | `sensor.saj_ct_pv_apparent_power` | Sensor | VA | H2 | - | Nein |
| Wechselrichterscheinleistung | `sensor.saj_inverter_apparent_power` | Sensor | VA | H2 | - | Nein |
| Notstromlast-Scheinleistung | `sensor.saj_backup_load_apparent_power` | Sensor | VA | H2 | - | Nein |
| Solar-Erzeugungszeit heute | `sensor.saj_pv_generation_time_today` | Sensor | h | H2 | - | Nein |
| Solar-Erzeugungszeit gesamt | `sensor.saj_pv_generation_time_total` | Sensor | h | H2 | - | Nein |
| Wechselrichterenergie heute | `sensor.saj_inverter_energy_today` | Sensor | kWh | H2 | - | Nein |
| Wechselrichterenergie diesen Monat | `sensor.saj_inverter_energy_month` | Sensor | kWh | H2 | - | Nein |
| Wechselrichterenergie dieses Jahr | `sensor.saj_inverter_energy_year` | Sensor | kWh | H2 | - | Nein |
| Wechselrichterenergie gesamt | `sensor.saj_inverter_energy_total` | Sensor | kWh | H2 | - | Nein |
| PV2-Energie heute | `sensor.saj_pv2_energy_today` | Sensor | kWh | H2 | PV-String 2 und höher | Nein |
| PV2-Energie diesen Monat | `sensor.saj_pv2_energy_month` | Sensor | kWh | H2 | PV-String 2 und höher | Nein |
| PV2-Energie dieses Jahr | `sensor.saj_pv2_energy_year` | Sensor | kWh | H2 | PV-String 2 und höher | Nein |
| PV2-Energie gesamt | `sensor.saj_pv2_energy_total` | Sensor | kWh | H2 | PV-String 2 und höher | Nein |
| PV3-Energie heute | `sensor.saj_pv3_energy_today` | Sensor | kWh | H2 | PV-String 3 und höher | Nein |
| PV3-Energie diesen Monat | `sensor.saj_pv3_energy_month` | Sensor | kWh | H2 | PV-String 3 und höher | Nein |
| PV3-Energie dieses Jahr | `sensor.saj_pv3_energy_year` | Sensor | kWh | H2 | PV-String 3 und höher | Nein |
| PV3-Energie gesamt | `sensor.saj_pv3_energy_total` | Sensor | kWh | H2 | PV-String 3 und höher | Nein |
| Identitätsprotokollversion | `sensor.saj_identity_protocol_version` | Sensor | - | H2 | - | Nein |
