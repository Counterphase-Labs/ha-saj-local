[en](../../../en-gb/user/entities/inverter-and-pv.md) | [de](../../../de/user/entities/inverter-and-pv.md) | nl | [fr](../../../fr/user/entities/inverter-and-pv.md) | [zh](../../../zh-hans/user/entities/inverter-and-pv.md) | [es](../../../es/user/entities/inverter-and-pv.md) | [it](../../../it/user/entities/inverter-and-pv.md) | [pl](../../../pl/user/entities/inverter-and-pv.md) | [sv](../../../sv/user/entities/inverter-and-pv.md)

# Omvormer en PV

Uitgang van de omvormer, zonnestrings, back-uppoort, energietellers, versies en de huishoudelijke belasting.

De functielijst van de integratie legt de Omvormer en PV-entiteiten uit in [Apparaten en entiteiten](../../../../custom_components/saj_local/docs/features.md#devices-and-entities).

244 entiteiten. Gegenereerd door `make docs`. Niet met de hand bewerken.

Een voorvoegsel dat in Configureren is ingesteld komt na `saj_` in de ID van elke Omvormer en PV-entiteit, bijvoorbeeld `sensor.saj_house_ethernet_protocol_version` met het voorvoegsel `house`.

| Naam | Entiteits-ID | Type | Eenheid | Modellen | Apparatuur en aantallen | Standaard ingeschakeld |
| --- | --- | --- | --- | --- | --- | --- |
| Ethernet-protocolversie | `sensor.saj_ethernet_protocol_version` | Sensor | - | HS3 | - | Nee |
| Ethernet-MAC-adres | `sensor.saj_ethernet_mac_address` | Sensor | - | HS3 | - | Nee |
| Ethernet-modus | `sensor.saj_ethernet_mode` | Sensor | - | HS3 | - | Nee |
| Ethernet-IP-adres | `sensor.saj_ethernet_ip_address` | Sensor | - | HS3 | - | Nee |
| Ethernet-subnetmasker | `sensor.saj_ethernet_subnet_mask` | Sensor | - | HS3 | - | Nee |
| Ethernet-gateway | `sensor.saj_ethernet_gateway` | Sensor | - | HS3 | - | Nee |
| Ethernet primaire DNS | `sensor.saj_ethernet_dns_primary` | Sensor | - | HS3 | - | Nee |
| Ethernet secundaire DNS | `sensor.saj_ethernet_dns_secondary` | Sensor | - | HS3 | - | Nee |
| Volgnummer instellingen | `sensor.saj_settings_sequence` | Sensor | - | HS3, H2 | - | Nee |
| Protocolversie van instellingen | `sensor.saj_settings_protocol_version` | Sensor | - | HS3 | - | Nee |
| Meterconfiguratie | `sensor.saj_meter_configuration` | Sensor | - | HS3, H2 | - | Nee |
| Meteradres | `sensor.saj_meter_address` | Sensor | - | HS3, H2 | - | Nee |
| RS485-adres | `sensor.saj_rs485_address` | Sensor | - | HS3, H2 | - | Nee |
| RS485-baudrate | `sensor.saj_rs485_baud_rate` | Sensor | - | HS3, H2 | - | Nee |
| Batterijprotocol | `sensor.saj_battery_protocol` | Sensor | - | HS3, H2 | - | Nee |
| RS485-slave-adres | `sensor.saj_rs485_slave_address` | Sensor | - | HS3 | - | Nee |
| RS485-slave-baudrate | `sensor.saj_rs485_slave_baud_rate` | Sensor | - | HS3 | - | Nee |
| Omvormerklok | `sensor.saj_inverter_clock` | Sensor | - | HS3, H2 | - | Nee |
| Bedrijfsmodus | `sensor.saj_operating_mode` | Sensor | - | HS3, H2 | - | Ja |
| Omvormertemperatuur | `sensor.saj_inverter_temperature` | Sensor | °C | HS3, H2 | - | Ja |
| Omgevingstemperatuur | `sensor.saj_ambient_temperature` | Sensor | °C | HS3, H2 | - | Nee |
| Lekstroom | `sensor.saj_leakage_current` | Sensor | mA | HS3, H2 | - | Nee |
| PV1-isolatieweerstand | `sensor.saj_pv1_insulation_resistance` | Sensor | kΩ | HS3, H2 | - | Nee |
| PV2-isolatieweerstand | `sensor.saj_pv2_insulation_resistance` | Sensor | kΩ | HS3, H2 | PV-string 2 en hoger | Nee |
| Setpoint ontlaadvermogen omvormer | `sensor.saj_inverter_discharge_power_setpoint` | Sensor | W | HS3, H2 | - | Nee |
| Setpoint oplaadvermogen omvormer | `sensor.saj_inverter_charge_power_setpoint` | Sensor | W | HS3, H2 | - | Nee |
| Batterijprotocol (van kracht) | `sensor.saj_battery_protocol_active` | Sensor | - | HS3, H2 | - | Nee |
| Meterconfiguratie (van kracht) | `sensor.saj_meter_configuration_active` | Sensor | - | HS3, H2 | - | Nee |
| Omvormerspanning L1 | `sensor.saj_inverter_l1_voltage` | Sensor | V | HS3, H2 | - | Nee |
| Omvormerstroom L1 | `sensor.saj_inverter_l1_current` | Sensor | A | HS3, H2 | - | Nee |
| Omvormerfrequentie L1 | `sensor.saj_inverter_l1_frequency` | Sensor | Hz | HS3, H2 | - | Nee |
| Omvormervermogen L1 | `sensor.saj_inverter_l1_power` | Sensor | W | HS3, H2 | - | Nee |
| Schijnbaar omvormervermogen L1 | `sensor.saj_inverter_l1_apparent_power` | Sensor | VA | HS3, H2 | - | Nee |
| Omvormerspanning L2 | `sensor.saj_inverter_l2_voltage` | Sensor | V | HS3, H2 | Fase 2 en hoger | Nee |
| Omvormerstroom L2 | `sensor.saj_inverter_l2_current` | Sensor | A | HS3, H2 | Fase 2 en hoger | Nee |
| Omvormerfrequentie L2 | `sensor.saj_inverter_l2_frequency` | Sensor | Hz | HS3, H2 | Fase 2 en hoger | Nee |
| Omvormervermogen L2 | `sensor.saj_inverter_l2_power` | Sensor | W | HS3, H2 | Fase 2 en hoger | Nee |
| Schijnbaar omvormervermogen L2 | `sensor.saj_inverter_l2_apparent_power` | Sensor | VA | HS3, H2 | Fase 2 en hoger | Nee |
| Omvormerspanning L3 | `sensor.saj_inverter_l3_voltage` | Sensor | V | HS3, H2 | Fase 3 en hoger | Nee |
| Omvormerstroom L3 | `sensor.saj_inverter_l3_current` | Sensor | A | HS3, H2 | Fase 3 en hoger | Nee |
| Omvormerfrequentie L3 | `sensor.saj_inverter_l3_frequency` | Sensor | Hz | HS3, H2 | Fase 3 en hoger | Nee |
| Omvormervermogen L3 | `sensor.saj_inverter_l3_power` | Sensor | W | HS3, H2 | Fase 3 en hoger | Nee |
| Schijnbaar omvormervermogen L3 | `sensor.saj_inverter_l3_apparent_power` | Sensor | VA | HS3, H2 | Fase 3 en hoger | Nee |
| Back-upspanning L1 | `sensor.saj_backup_l1_voltage` | Sensor | V | HS3, H2 | - | Nee |
| Back-upstroom L1 | `sensor.saj_backup_l1_current` | Sensor | A | HS3, H2 | - | Nee |
| Back-upfrequentie L1 | `sensor.saj_backup_l1_frequency` | Sensor | Hz | HS3, H2 | - | Nee |
| Back-upgelijkspanning L1 | `sensor.saj_backup_l1_dc_voltage` | Sensor | mV | HS3, H2 | - | Nee |
| Back-upvermogen L1 | `sensor.saj_backup_l1_power` | Sensor | W | HS3, H2 | - | Nee |
| Schijnbaar back-upvermogen L1 | `sensor.saj_backup_l1_apparent_power` | Sensor | VA | HS3, H2 | - | Nee |
| Back-upspanning L2 | `sensor.saj_backup_l2_voltage` | Sensor | V | HS3, H2 | Fase 2 en hoger | Nee |
| Back-upstroom L2 | `sensor.saj_backup_l2_current` | Sensor | A | HS3, H2 | Fase 2 en hoger | Nee |
| Back-upfrequentie L2 | `sensor.saj_backup_l2_frequency` | Sensor | Hz | HS3, H2 | Fase 2 en hoger | Nee |
| Back-upgelijkspanning L2 | `sensor.saj_backup_l2_dc_voltage` | Sensor | mV | HS3, H2 | Fase 2 en hoger | Nee |
| Back-upvermogen L2 | `sensor.saj_backup_l2_power` | Sensor | W | HS3, H2 | Fase 2 en hoger | Nee |
| Schijnbaar back-upvermogen L2 | `sensor.saj_backup_l2_apparent_power` | Sensor | VA | HS3, H2 | Fase 2 en hoger | Nee |
| Back-upspanning L3 | `sensor.saj_backup_l3_voltage` | Sensor | V | HS3, H2 | Fase 3 en hoger | Nee |
| Back-upstroom L3 | `sensor.saj_backup_l3_current` | Sensor | A | HS3, H2 | Fase 3 en hoger | Nee |
| Back-upfrequentie L3 | `sensor.saj_backup_l3_frequency` | Sensor | Hz | HS3, H2 | Fase 3 en hoger | Nee |
| Back-upgelijkspanning L3 | `sensor.saj_backup_l3_dc_voltage` | Sensor | mV | HS3, H2 | Fase 3 en hoger | Nee |
| Back-upvermogen L3 | `sensor.saj_backup_l3_power` | Sensor | W | HS3, H2 | Fase 3 en hoger | Nee |
| Schijnbaar back-upvermogen L3 | `sensor.saj_backup_l3_apparent_power` | Sensor | VA | HS3, H2 | Fase 3 en hoger | Nee |
| DC-busspanning | `sensor.saj_dc_bus_voltage` | Sensor | V | HS3, H2 | - | Nee |
| Slavespanning DC-bus | `sensor.saj_dc_bus_slave_voltage` | Sensor | V | HS3, H2 | - | Nee |
| PV1-spanning | `sensor.saj_pv1_voltage` | Sensor | V | HS3, H2 | - | Ja |
| PV1-stroom | `sensor.saj_pv1_current` | Sensor | A | HS3, H2 | - | Ja |
| PV1-vermogen | `sensor.saj_pv1_power` | Sensor | W | HS3, H2 | - | Ja |
| PV2-spanning | `sensor.saj_pv2_voltage` | Sensor | V | HS3, H2 | PV-string 2 en hoger | Ja |
| PV2-stroom | `sensor.saj_pv2_current` | Sensor | A | HS3, H2 | PV-string 2 en hoger | Ja |
| PV2-vermogen | `sensor.saj_pv2_power` | Sensor | W | HS3, H2 | PV-string 2 en hoger | Ja |
| Zonnevermogen | `sensor.saj_pv_power` | Sensor | W | HS3, H2 | - | Ja |
| Omvormervermogen | `sensor.saj_inverter_power` | Sensor | W | HS3, H2 | - | Ja |
| Zonne-energie vandaag | `sensor.saj_pv_energy_today` | Sensor | kWh | HS3, H2 | - | Ja |
| Zonne-energie deze maand | `sensor.saj_pv_energy_month` | Sensor | kWh | HS3, H2 | - | Nee |
| Zonne-energie dit jaar | `sensor.saj_pv_energy_year` | Sensor | kWh | HS3, H2 | - | Nee |
| Zonne-energie totaal | `sensor.saj_pv_energy_total` | Sensor | kWh | HS3, H2 | - | Ja |
| Huisverbruik vandaag | `sensor.saj_load_energy_today` | Sensor | kWh | HS3, H2 | - | Ja |
| Huisverbruik deze maand | `sensor.saj_load_energy_month` | Sensor | kWh | HS3, H2 | - | Nee |
| Huisverbruik dit jaar | `sensor.saj_load_energy_year` | Sensor | kWh | HS3, H2 | - | Nee |
| Huisverbruik totaal | `sensor.saj_load_energy_total` | Sensor | kWh | HS3, H2 | - | Ja |
| Back-upbelasting vandaag | `sensor.saj_backup_load_energy_today` | Sensor | kWh | HS3, H2 | - | Ja |
| Back-upbelasting deze maand | `sensor.saj_backup_load_energy_month` | Sensor | kWh | HS3, H2 | - | Nee |
| Back-upbelasting dit jaar | `sensor.saj_backup_load_energy_year` | Sensor | kWh | HS3, H2 | - | Nee |
| Back-upbelasting totaal | `sensor.saj_backup_load_energy_total` | Sensor | kWh | HS3, H2 | - | Ja |
| Parallelle modus | `sensor.saj_parallel_mode` | Sensor | - | HS3, H2 | - | Nee |
| Parallelle machines online | `sensor.saj_parallel_online_count` | Sensor | - | HS3, H2 | - | Nee |
| Netvermogen (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_power` | Sensor | W | HS3 | - | Nee |
| Netvermogen L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_l1_power` | Sensor | W | HS3 | - | Nee |
| Netspanning L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_l1_voltage` | Sensor | V | HS3 | - | Nee |
| Netstroom L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_l1_current` | Sensor | A | HS3 | - | Nee |
| Netfrequentie L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_l1_frequency` | Sensor | Hz | HS3 | - | Nee |
| Netvermogen L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_l2_power` | Sensor | W | HS3 | Fase 2 en hoger | Nee |
| Netspanning L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_l2_voltage` | Sensor | V | HS3 | Fase 2 en hoger | Nee |
| Netstroom L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_l2_current` | Sensor | A | HS3 | Fase 2 en hoger | Nee |
| Netfrequentie L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_l2_frequency` | Sensor | Hz | HS3 | Fase 2 en hoger | Nee |
| Netvermogen L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_l3_power` | Sensor | W | HS3 | Fase 3 en hoger | Nee |
| Netspanning L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_l3_voltage` | Sensor | V | HS3 | Fase 3 en hoger | Nee |
| Netstroom L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_l3_current` | Sensor | A | HS3 | Fase 3 en hoger | Nee |
| Netfrequentie L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_l3_frequency` | Sensor | Hz | HS3 | Fase 3 en hoger | Nee |
| Omvormervermogen (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_inverter_power` | Sensor | W | HS3 | - | Nee |
| Omvormervermogen L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_inverter_l1_power` | Sensor | W | HS3 | - | Nee |
| Omvormerspanning L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_inverter_l1_voltage` | Sensor | V | HS3 | - | Nee |
| Omvormerstroom L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_inverter_l1_current` | Sensor | A | HS3 | - | Nee |
| Omvormerfrequentie L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_inverter_l1_frequency` | Sensor | Hz | HS3 | - | Nee |
| Omvormervermogen L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_inverter_l2_power` | Sensor | W | HS3 | Fase 2 en hoger | Nee |
| Omvormerspanning L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_inverter_l2_voltage` | Sensor | V | HS3 | Fase 2 en hoger | Nee |
| Omvormerstroom L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_inverter_l2_current` | Sensor | A | HS3 | Fase 2 en hoger | Nee |
| Omvormerfrequentie L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_inverter_l2_frequency` | Sensor | Hz | HS3 | Fase 2 en hoger | Nee |
| Omvormervermogen L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_inverter_l3_power` | Sensor | W | HS3 | Fase 3 en hoger | Nee |
| Omvormerspanning L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_inverter_l3_voltage` | Sensor | V | HS3 | Fase 3 en hoger | Nee |
| Omvormerstroom L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_inverter_l3_current` | Sensor | A | HS3 | Fase 3 en hoger | Nee |
| Omvormerfrequentie L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_inverter_l3_frequency` | Sensor | Hz | HS3 | Fase 3 en hoger | Nee |
| Huisvermogen (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_load_power` | Sensor | W | HS3 | - | Nee |
| Huisvermogen L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_load_l1_power` | Sensor | W | HS3 | - | Nee |
| Huisspanning L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_load_l1_voltage` | Sensor | V | HS3 | - | Nee |
| Huisstroom L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_load_l1_current` | Sensor | A | HS3 | - | Nee |
| Huisfrequentie L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_load_l1_frequency` | Sensor | Hz | HS3 | - | Nee |
| Huisvermogen L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_load_l2_power` | Sensor | W | HS3 | Fase 2 en hoger | Nee |
| Huisspanning L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_load_l2_voltage` | Sensor | V | HS3 | Fase 2 en hoger | Nee |
| Huisstroom L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_load_l2_current` | Sensor | A | HS3 | Fase 2 en hoger | Nee |
| Huisfrequentie L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_load_l2_frequency` | Sensor | Hz | HS3 | Fase 2 en hoger | Nee |
| Huisvermogen L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_load_l3_power` | Sensor | W | HS3 | Fase 3 en hoger | Nee |
| Huisspanning L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_load_l3_voltage` | Sensor | V | HS3 | Fase 3 en hoger | Nee |
| Huisstroom L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_load_l3_current` | Sensor | A | HS3 | Fase 3 en hoger | Nee |
| Huisfrequentie L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_load_l3_frequency` | Sensor | Hz | HS3 | Fase 3 en hoger | Nee |
| Netbelastingvermogen (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_load_power` | Sensor | W | HS3 | - | Nee |
| Netbelastingvermogen L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_load_l1_power` | Sensor | W | HS3 | - | Nee |
| Netbelastingspanning L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_load_l1_voltage` | Sensor | V | HS3 | - | Nee |
| Netbelastingstroom L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_load_l1_current` | Sensor | A | HS3 | - | Nee |
| Netbelastingfrequentie L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_load_l1_frequency` | Sensor | Hz | HS3 | - | Nee |
| Netbelastingvermogen L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_load_l2_power` | Sensor | W | HS3 | Fase 2 en hoger | Nee |
| Netbelastingspanning L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_load_l2_voltage` | Sensor | V | HS3 | Fase 2 en hoger | Nee |
| Netbelastingstroom L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_load_l2_current` | Sensor | A | HS3 | Fase 2 en hoger | Nee |
| Netbelastingfrequentie L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_load_l2_frequency` | Sensor | Hz | HS3 | Fase 2 en hoger | Nee |
| Netbelastingvermogen L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_load_l3_power` | Sensor | W | HS3 | Fase 3 en hoger | Nee |
| Netbelastingspanning L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_load_l3_voltage` | Sensor | V | HS3 | Fase 3 en hoger | Nee |
| Netbelastingstroom L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_load_l3_current` | Sensor | A | HS3 | Fase 3 en hoger | Nee |
| Netbelastingfrequentie L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_grid_load_l3_frequency` | Sensor | Hz | HS3 | Fase 3 en hoger | Nee |
| Back-upvermogen (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_backup_power` | Sensor | W | HS3 | - | Nee |
| Back-upvermogen L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_backup_l1_power` | Sensor | W | HS3 | - | Nee |
| Back-upspanning L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_backup_l1_voltage` | Sensor | V | HS3 | - | Nee |
| Back-upstroom L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_backup_l1_current` | Sensor | A | HS3 | - | Nee |
| Back-upfrequentie L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_backup_l1_frequency` | Sensor | Hz | HS3 | - | Nee |
| Back-upvermogen L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_backup_l2_power` | Sensor | W | HS3 | Fase 2 en hoger | Nee |
| Back-upspanning L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_backup_l2_voltage` | Sensor | V | HS3 | Fase 2 en hoger | Nee |
| Back-upstroom L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_backup_l2_current` | Sensor | A | HS3 | Fase 2 en hoger | Nee |
| Back-upfrequentie L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_backup_l2_frequency` | Sensor | Hz | HS3 | Fase 2 en hoger | Nee |
| Back-upvermogen L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_backup_l3_power` | Sensor | W | HS3 | Fase 3 en hoger | Nee |
| Back-upspanning L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_backup_l3_voltage` | Sensor | V | HS3 | Fase 3 en hoger | Nee |
| Back-upstroom L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_backup_l3_current` | Sensor | A | HS3 | Fase 3 en hoger | Nee |
| Back-upfrequentie L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_backup_l3_frequency` | Sensor | Hz | HS3 | Fase 3 en hoger | Nee |
| Zonnevermogen (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_pv_power` | Sensor | W | HS3 | - | Nee |
| PV1-spanning (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_pv1_voltage` | Sensor | V | HS3 | - | Nee |
| PV1-stroom (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_pv1_current` | Sensor | A | HS3 | - | Nee |
| PV1-vermogen (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_pv1_power` | Sensor | W | HS3 | - | Nee |
| PV2-spanning (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_pv2_voltage` | Sensor | V | HS3 | PV-string 2 en hoger | Nee |
| PV2-stroom (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_pv2_current` | Sensor | A | HS3 | PV-string 2 en hoger | Nee |
| PV2-vermogen (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_pv2_power` | Sensor | W | HS3 | PV-string 2 en hoger | Nee |
| Generatorvermogen (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_generator_power` | Sensor | W | HS3 | - | Nee |
| Generatorvermogen L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_generator_l1_power` | Sensor | W | HS3 | - | Nee |
| Generatorspanning L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_generator_l1_voltage` | Sensor | V | HS3 | - | Nee |
| Generatorstroom L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_generator_l1_current` | Sensor | A | HS3 | - | Nee |
| Generatorfrequentie L1 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_generator_l1_frequency` | Sensor | Hz | HS3 | - | Nee |
| Generatorvermogen L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_generator_l2_power` | Sensor | W | HS3 | Fase 2 en hoger | Nee |
| Generatorspanning L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_generator_l2_voltage` | Sensor | V | HS3 | Fase 2 en hoger | Nee |
| Generatorstroom L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_generator_l2_current` | Sensor | A | HS3 | Fase 2 en hoger | Nee |
| Generatorfrequentie L2 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_generator_l2_frequency` | Sensor | Hz | HS3 | Fase 2 en hoger | Nee |
| Generatorvermogen L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_generator_l3_power` | Sensor | W | HS3 | Fase 3 en hoger | Nee |
| Generatorspanning L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_generator_l3_voltage` | Sensor | V | HS3 | Fase 3 en hoger | Nee |
| Generatorstroom L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_generator_l3_current` | Sensor | A | HS3 | Fase 3 en hoger | Nee |
| Generatorfrequentie L3 (gemiddelde over 5 minuten) | `sensor.saj_five_minute_average_generator_l3_frequency` | Sensor | Hz | HS3 | Fase 3 en hoger | Nee |
| Productcode | `sensor.saj_product_code` | Sensor | - | HS3, H2 | - | Nee |
| Displaysoftwareversie | `sensor.saj_display_software_version` | Sensor | - | HS3, H2 | - | Nee |
| Mastersoftwareversie | `sensor.saj_master_software_version` | Sensor | - | HS3, H2 | - | Nee |
| Slavesoftwareversie | `sensor.saj_slave_software_version` | Sensor | - | HS3, H2 | - | Nee |
| Displayhardwareversie | `sensor.saj_display_hardware_version` | Sensor | - | HS3, H2 | - | Nee |
| Hardwareversie regeling | `sensor.saj_control_hardware_version` | Sensor | - | HS3, H2 | - | Nee |
| Hardwareversie vermogen | `sensor.saj_power_hardware_version` | Sensor | - | HS3, H2 | - | Nee |
| Aantal batterijpacks | `sensor.saj_battery_pack_count` | Sensor | - | HS3, H2 | - | Nee |
| Meter A status | `sensor.saj_meter_a_status` | Sensor | - | HS3, H2 | - | Nee |
| Meter B status | `sensor.saj_meter_b_status` | Sensor | - | HS3, H2 | - | Nee |
| Back-upbelastingvermogen | `sensor.saj_backup_load_power` | Sensor | W | HS3, H2 | - | Ja |
| Huisvermogen | `sensor.saj_load_power` | Sensor | W | HS3, H2 | - | Ja |
| Eigen verbruik vandaag | `sensor.saj_self_consumption_today` | Sensor | % | HS3, H2 | - | Nee |
| Zelfvoorziening vandaag | `sensor.saj_self_sufficiency_today` | Sensor | % | HS3, H2 | - | Nee |
| Zonne-overschotvermogen | `sensor.saj_solar_surplus_power` | Sensor | W | HS3, H2 | - | Nee |
| Terugstroommodus | `sensor.saj_reverse_flow_mode` | Sensor | - | H2 | - | Nee |
| FCAS-frequentiehysterese | `sensor.saj_fcas_frequency_hysteresis` | Sensor | Hz | H2 | - | Nee |
| Parallelrol | `sensor.saj_parallel_role` | Sensor | - | H2 | - | Nee |
| Parallelnummer | `sensor.saj_parallel_number` | Sensor | - | H2 | - | Nee |
| Parallel geconfigureerde modus | `sensor.saj_parallel_configured_mode` | Sensor | - | H2 | - | Nee |
| Batterijingangsmodus | `sensor.saj_battery_input_mode` | Sensor | - | H2 | - | Nee |
| PV-ingangsmodus | `sensor.saj_pv_input_mode` | Sensor | - | H2 | - | Nee |
| Off-gridmodus | `sensor.saj_off_grid_mode` | Sensor | - | H2 | - | Nee |
| Uitgangsspanning off-grid | `sensor.saj_off_grid_output_voltage` | Sensor | V | H2 | - | Nee |
| Uitgangsfrequentie off-grid | `sensor.saj_off_grid_output_frequency` | Sensor | Hz | H2 | - | Nee |
| Motor inschakelen | `sensor.saj_motor_enable` | Sensor | - | H2 | - | Nee |
| Machinemodel | `sensor.saj_machine_model` | Sensor | - | H2 | - | Nee |
| Nominaal vermogen | `sensor.saj_rated_power` | Sensor | W | H2 | - | Nee |
| Functievlaggen 1 | `sensor.saj_function_flags_1` | Sensor | - | H2 | - | Nee |
| Functievlaggen 2 | `sensor.saj_function_flags_2` | Sensor | - | H2 | - | Nee |
| Maximale gelijkstroomcomponent | `sensor.saj_max_dc_current_component` | Sensor | mA | H2 | - | Nee |
| Maximale gelijkspanningscomponent | `sensor.saj_max_dc_voltage_component` | Sensor | V | H2 | - | Nee |
| Isolatieweerstandslimiet | `sensor.saj_insulation_resistance_limit` | Sensor | kΩ | H2 | - | Nee |
| Maximale lekstroom | `sensor.saj_max_leakage_current` | Sensor | mA | H2 | - | Nee |
| Omvormerstop | `sensor.saj_inverter_stop` | Sensor | - | H2 | - | Nee |
| PV-startspanning | `sensor.saj_pv_start_voltage` | Sensor | V | H2 | - | Nee |
| PV-uitschakelspanning | `sensor.saj_pv_shutdown_voltage` | Sensor | V | H2 | - | Nee |
| MPPT-spanning hoog | `sensor.saj_mppt_voltage_high` | Sensor | V | H2 | - | Nee |
| MPPT-spanning laag | `sensor.saj_mppt_voltage_low` | Sensor | V | H2 | - | Nee |
| MPPT-scantijd | `sensor.saj_mppt_scan_time` | Sensor | min | H2 | - | Nee |
| Aantal omvormerfouten | `sensor.saj_inverter_error_count` | Sensor | - | H2 | - | Nee |
| PV3-isolatieweerstand | `sensor.saj_pv3_insulation_resistance` | Sensor | kΩ | H2 | PV-string 3 en hoger | Nee |
| PV4-isolatieweerstand | `sensor.saj_pv4_insulation_resistance` | Sensor | kΩ | H2 | PV-string 4 en hoger | Nee |
| DRM-hardwarestatus | `sensor.saj_drm_hardware_status` | Sensor | - | H2 | - | Nee |
| DRM-softwarestatus | `sensor.saj_drm_software_status` | Sensor | - | H2 | - | Nee |
| Volgnummer storingsrecord | `sensor.saj_fault_record_sequence` | Sensor | - | H2 | - | Nee |
| Toepassingsmodus (van kracht) | `sensor.saj_application_mode_active` | Sensor | - | H2 | - | Nee |
| PV3-spanning | `sensor.saj_pv3_voltage` | Sensor | V | H2 | PV-string 3 en hoger | Ja |
| PV3-stroom | `sensor.saj_pv3_current` | Sensor | A | H2 | PV-string 3 en hoger | Ja |
| PV3-vermogen | `sensor.saj_pv3_power` | Sensor | W | H2 | PV-string 3 en hoger | Ja |
| PV4-spanning | `sensor.saj_pv4_voltage` | Sensor | V | H2 | PV-string 4 en hoger | Ja |
| PV4-stroom | `sensor.saj_pv4_current` | Sensor | A | H2 | PV-string 4 en hoger | Ja |
| PV4-vermogen | `sensor.saj_pv4_power` | Sensor | W | H2 | PV-string 4 en hoger | Ja |
| CT-netvermogen | `sensor.saj_ct_grid_power` | Sensor | W | H2 | - | Nee |
| Schijnbaar CT-netvermogen | `sensor.saj_ct_grid_apparent_power` | Sensor | VA | H2 | - | Nee |
| CT-zonnevermogen | `sensor.saj_ct_pv_power` | Sensor | W | H2 | - | Nee |
| Schijnbaar CT-zonnevermogen | `sensor.saj_ct_pv_apparent_power` | Sensor | VA | H2 | - | Nee |
| Schijnbaar omvormervermogen | `sensor.saj_inverter_apparent_power` | Sensor | VA | H2 | - | Nee |
| Schijnbaar back-upbelastingvermogen | `sensor.saj_backup_load_apparent_power` | Sensor | VA | H2 | - | Nee |
| Zonne-opwektijd vandaag | `sensor.saj_pv_generation_time_today` | Sensor | h | H2 | - | Nee |
| Zonne-opwektijd totaal | `sensor.saj_pv_generation_time_total` | Sensor | h | H2 | - | Nee |
| Omvormerenergie vandaag | `sensor.saj_inverter_energy_today` | Sensor | kWh | H2 | - | Nee |
| Omvormerenergie deze maand | `sensor.saj_inverter_energy_month` | Sensor | kWh | H2 | - | Nee |
| Omvormerenergie dit jaar | `sensor.saj_inverter_energy_year` | Sensor | kWh | H2 | - | Nee |
| Omvormerenergie totaal | `sensor.saj_inverter_energy_total` | Sensor | kWh | H2 | - | Nee |
| PV2-energie vandaag | `sensor.saj_pv2_energy_today` | Sensor | kWh | H2 | PV-string 2 en hoger | Nee |
| PV2-energie deze maand | `sensor.saj_pv2_energy_month` | Sensor | kWh | H2 | PV-string 2 en hoger | Nee |
| PV2-energie dit jaar | `sensor.saj_pv2_energy_year` | Sensor | kWh | H2 | PV-string 2 en hoger | Nee |
| PV2-energie totaal | `sensor.saj_pv2_energy_total` | Sensor | kWh | H2 | PV-string 2 en hoger | Nee |
| PV3-energie vandaag | `sensor.saj_pv3_energy_today` | Sensor | kWh | H2 | PV-string 3 en hoger | Nee |
| PV3-energie deze maand | `sensor.saj_pv3_energy_month` | Sensor | kWh | H2 | PV-string 3 en hoger | Nee |
| PV3-energie dit jaar | `sensor.saj_pv3_energy_year` | Sensor | kWh | H2 | PV-string 3 en hoger | Nee |
| PV3-energie totaal | `sensor.saj_pv3_energy_total` | Sensor | kWh | H2 | PV-string 3 en hoger | Nee |
| Protocolversie identiteit | `sensor.saj_identity_protocol_version` | Sensor | - | H2 | - | Nee |
