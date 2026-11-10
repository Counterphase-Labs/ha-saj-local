[en](../../../en-gb/user/entities/inverter-and-pv.md) | [de](../../../de/user/entities/inverter-and-pv.md) | [nl](../../../nl/user/entities/inverter-and-pv.md) | [fr](../../../fr/user/entities/inverter-and-pv.md) | [zh](../../../zh-hans/user/entities/inverter-and-pv.md) | [es](../../../es/user/entities/inverter-and-pv.md) | [it](../../../it/user/entities/inverter-and-pv.md) | [pl](../../../pl/user/entities/inverter-and-pv.md) | sv

# Växelriktare och PV

Växelriktarens utgång, solcellssträngar, reservport, energiräknare, versioner och hushållets last.

Integrationens funktionslista förklarar entiteterna för Växelriktare och PV i [Enheter och entiteter](../../../../custom_components/saj_local/docs/features.md#devices-and-entities).

244 entiteter. Genereras av `make docs`. Redigera inte för hand.

Ett prefix som anges i Konfigurera hamnar efter `saj_` i ID:t för varje entitet i Växelriktare och PV, till exempel `sensor.saj_house_ethernet_protocol_version` med prefixet `house`.

| Namn | Entitets-ID | Typ | Enhet | Modeller | Utrustning och antal | Aktiverad som standard |
| --- | --- | --- | --- | --- | --- | --- |
| Ethernet-protokollversion | `sensor.saj_ethernet_protocol_version` | Sensor | - | HS3 | - | Nej |
| Ethernet-MAC-adress | `sensor.saj_ethernet_mac_address` | Sensor | - | HS3 | - | Nej |
| Ethernet-läge | `sensor.saj_ethernet_mode` | Sensor | - | HS3 | - | Nej |
| Ethernet-IP-adress | `sensor.saj_ethernet_ip_address` | Sensor | - | HS3 | - | Nej |
| Ethernet-nätmask | `sensor.saj_ethernet_subnet_mask` | Sensor | - | HS3 | - | Nej |
| Ethernet-gateway | `sensor.saj_ethernet_gateway` | Sensor | - | HS3 | - | Nej |
| Ethernet primär DNS | `sensor.saj_ethernet_dns_primary` | Sensor | - | HS3 | - | Nej |
| Ethernet sekundär DNS | `sensor.saj_ethernet_dns_secondary` | Sensor | - | HS3 | - | Nej |
| Inställningarnas ordningsnummer | `sensor.saj_settings_sequence` | Sensor | - | HS3, H2 | - | Nej |
| Inställningsprotokollversion | `sensor.saj_settings_protocol_version` | Sensor | - | HS3 | - | Nej |
| Mätarkonfiguration | `sensor.saj_meter_configuration` | Sensor | - | HS3, H2 | - | Nej |
| Mätaradress | `sensor.saj_meter_address` | Sensor | - | HS3, H2 | - | Nej |
| RS485-adress | `sensor.saj_rs485_address` | Sensor | - | HS3, H2 | - | Nej |
| RS485-överföringshastighet | `sensor.saj_rs485_baud_rate` | Sensor | - | HS3, H2 | - | Nej |
| Batteriprotokoll | `sensor.saj_battery_protocol` | Sensor | - | HS3, H2 | - | Nej |
| RS485-slavadress | `sensor.saj_rs485_slave_address` | Sensor | - | HS3 | - | Nej |
| RS485-slavens överföringshastighet | `sensor.saj_rs485_slave_baud_rate` | Sensor | - | HS3 | - | Nej |
| Växelriktarens klocka | `sensor.saj_inverter_clock` | Sensor | - | HS3, H2 | - | Nej |
| Driftläge | `sensor.saj_operating_mode` | Sensor | - | HS3, H2 | - | Ja |
| Växelriktartemperatur | `sensor.saj_inverter_temperature` | Sensor | °C | HS3, H2 | - | Ja |
| Omgivningstemperatur | `sensor.saj_ambient_temperature` | Sensor | °C | HS3, H2 | - | Nej |
| Läckström | `sensor.saj_leakage_current` | Sensor | mA | HS3, H2 | - | Nej |
| PV1-isolationsresistans | `sensor.saj_pv1_insulation_resistance` | Sensor | kΩ | HS3, H2 | - | Nej |
| PV2-isolationsresistans | `sensor.saj_pv2_insulation_resistance` | Sensor | kΩ | HS3, H2 | PV-sträng 2 och högre | Nej |
| Börvärde urladdningseffekt växelriktare | `sensor.saj_inverter_discharge_power_setpoint` | Sensor | W | HS3, H2 | - | Nej |
| Börvärde laddningseffekt växelriktare | `sensor.saj_inverter_charge_power_setpoint` | Sensor | W | HS3, H2 | - | Nej |
| Batteriprotokoll (gällande) | `sensor.saj_battery_protocol_active` | Sensor | - | HS3, H2 | - | Nej |
| Mätarkonfiguration (gällande) | `sensor.saj_meter_configuration_active` | Sensor | - | HS3, H2 | - | Nej |
| Växelriktare L1-spänning | `sensor.saj_inverter_l1_voltage` | Sensor | V | HS3, H2 | - | Nej |
| Växelriktare L1-ström | `sensor.saj_inverter_l1_current` | Sensor | A | HS3, H2 | - | Nej |
| Växelriktare L1-frekvens | `sensor.saj_inverter_l1_frequency` | Sensor | Hz | HS3, H2 | - | Nej |
| Växelriktare L1-effekt | `sensor.saj_inverter_l1_power` | Sensor | W | HS3, H2 | - | Nej |
| Växelriktare L1 skenbar effekt | `sensor.saj_inverter_l1_apparent_power` | Sensor | VA | HS3, H2 | - | Nej |
| Växelriktare L2-spänning | `sensor.saj_inverter_l2_voltage` | Sensor | V | HS3, H2 | Fas 2 och högre | Nej |
| Växelriktare L2-ström | `sensor.saj_inverter_l2_current` | Sensor | A | HS3, H2 | Fas 2 och högre | Nej |
| Växelriktare L2-frekvens | `sensor.saj_inverter_l2_frequency` | Sensor | Hz | HS3, H2 | Fas 2 och högre | Nej |
| Växelriktare L2-effekt | `sensor.saj_inverter_l2_power` | Sensor | W | HS3, H2 | Fas 2 och högre | Nej |
| Växelriktare L2 skenbar effekt | `sensor.saj_inverter_l2_apparent_power` | Sensor | VA | HS3, H2 | Fas 2 och högre | Nej |
| Växelriktare L3-spänning | `sensor.saj_inverter_l3_voltage` | Sensor | V | HS3, H2 | Fas 3 och högre | Nej |
| Växelriktare L3-ström | `sensor.saj_inverter_l3_current` | Sensor | A | HS3, H2 | Fas 3 och högre | Nej |
| Växelriktare L3-frekvens | `sensor.saj_inverter_l3_frequency` | Sensor | Hz | HS3, H2 | Fas 3 och högre | Nej |
| Växelriktare L3-effekt | `sensor.saj_inverter_l3_power` | Sensor | W | HS3, H2 | Fas 3 och högre | Nej |
| Växelriktare L3 skenbar effekt | `sensor.saj_inverter_l3_apparent_power` | Sensor | VA | HS3, H2 | Fas 3 och högre | Nej |
| Reserv L1-spänning | `sensor.saj_backup_l1_voltage` | Sensor | V | HS3, H2 | - | Nej |
| Reserv L1-ström | `sensor.saj_backup_l1_current` | Sensor | A | HS3, H2 | - | Nej |
| Reserv L1-frekvens | `sensor.saj_backup_l1_frequency` | Sensor | Hz | HS3, H2 | - | Nej |
| Reserv L1-likspänning | `sensor.saj_backup_l1_dc_voltage` | Sensor | mV | HS3, H2 | - | Nej |
| Reserv L1-effekt | `sensor.saj_backup_l1_power` | Sensor | W | HS3, H2 | - | Nej |
| Reserv L1 skenbar effekt | `sensor.saj_backup_l1_apparent_power` | Sensor | VA | HS3, H2 | - | Nej |
| Reserv L2-spänning | `sensor.saj_backup_l2_voltage` | Sensor | V | HS3, H2 | Fas 2 och högre | Nej |
| Reserv L2-ström | `sensor.saj_backup_l2_current` | Sensor | A | HS3, H2 | Fas 2 och högre | Nej |
| Reserv L2-frekvens | `sensor.saj_backup_l2_frequency` | Sensor | Hz | HS3, H2 | Fas 2 och högre | Nej |
| Reserv L2-likspänning | `sensor.saj_backup_l2_dc_voltage` | Sensor | mV | HS3, H2 | Fas 2 och högre | Nej |
| Reserv L2-effekt | `sensor.saj_backup_l2_power` | Sensor | W | HS3, H2 | Fas 2 och högre | Nej |
| Reserv L2 skenbar effekt | `sensor.saj_backup_l2_apparent_power` | Sensor | VA | HS3, H2 | Fas 2 och högre | Nej |
| Reserv L3-spänning | `sensor.saj_backup_l3_voltage` | Sensor | V | HS3, H2 | Fas 3 och högre | Nej |
| Reserv L3-ström | `sensor.saj_backup_l3_current` | Sensor | A | HS3, H2 | Fas 3 och högre | Nej |
| Reserv L3-frekvens | `sensor.saj_backup_l3_frequency` | Sensor | Hz | HS3, H2 | Fas 3 och högre | Nej |
| Reserv L3-likspänning | `sensor.saj_backup_l3_dc_voltage` | Sensor | mV | HS3, H2 | Fas 3 och högre | Nej |
| Reserv L3-effekt | `sensor.saj_backup_l3_power` | Sensor | W | HS3, H2 | Fas 3 och högre | Nej |
| Reserv L3 skenbar effekt | `sensor.saj_backup_l3_apparent_power` | Sensor | VA | HS3, H2 | Fas 3 och högre | Nej |
| Likspänning på DC-bussen | `sensor.saj_dc_bus_voltage` | Sensor | V | HS3, H2 | - | Nej |
| Likspänning på DC-bussen (slav) | `sensor.saj_dc_bus_slave_voltage` | Sensor | V | HS3, H2 | - | Nej |
| PV1-spänning | `sensor.saj_pv1_voltage` | Sensor | V | HS3, H2 | - | Ja |
| PV1-ström | `sensor.saj_pv1_current` | Sensor | A | HS3, H2 | - | Ja |
| PV1-effekt | `sensor.saj_pv1_power` | Sensor | W | HS3, H2 | - | Ja |
| PV2-spänning | `sensor.saj_pv2_voltage` | Sensor | V | HS3, H2 | PV-sträng 2 och högre | Ja |
| PV2-ström | `sensor.saj_pv2_current` | Sensor | A | HS3, H2 | PV-sträng 2 och högre | Ja |
| PV2-effekt | `sensor.saj_pv2_power` | Sensor | W | HS3, H2 | PV-sträng 2 och högre | Ja |
| Soleffekt | `sensor.saj_pv_power` | Sensor | W | HS3, H2 | - | Ja |
| Växelriktareffekt | `sensor.saj_inverter_power` | Sensor | W | HS3, H2 | - | Ja |
| Solenergi idag | `sensor.saj_pv_energy_today` | Sensor | kWh | HS3, H2 | - | Ja |
| Solenergi denna månad | `sensor.saj_pv_energy_month` | Sensor | kWh | HS3, H2 | - | Nej |
| Solenergi i år | `sensor.saj_pv_energy_year` | Sensor | kWh | HS3, H2 | - | Nej |
| Solenergi totalt | `sensor.saj_pv_energy_total` | Sensor | kWh | HS3, H2 | - | Ja |
| Hushållslastenergi idag | `sensor.saj_load_energy_today` | Sensor | kWh | HS3, H2 | - | Ja |
| Hushållslastenergi denna månad | `sensor.saj_load_energy_month` | Sensor | kWh | HS3, H2 | - | Nej |
| Hushållslastenergi i år | `sensor.saj_load_energy_year` | Sensor | kWh | HS3, H2 | - | Nej |
| Hushållslastenergi totalt | `sensor.saj_load_energy_total` | Sensor | kWh | HS3, H2 | - | Ja |
| Reservlastenergi idag | `sensor.saj_backup_load_energy_today` | Sensor | kWh | HS3, H2 | - | Ja |
| Reservlastenergi denna månad | `sensor.saj_backup_load_energy_month` | Sensor | kWh | HS3, H2 | - | Nej |
| Reservlastenergi i år | `sensor.saj_backup_load_energy_year` | Sensor | kWh | HS3, H2 | - | Nej |
| Reservlastenergi totalt | `sensor.saj_backup_load_energy_total` | Sensor | kWh | HS3, H2 | - | Ja |
| Parallelläge | `sensor.saj_parallel_mode` | Sensor | - | HS3, H2 | - | Nej |
| Parallellmaskiner online | `sensor.saj_parallel_online_count` | Sensor | - | HS3, H2 | - | Nej |
| Näteffekt (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_power` | Sensor | W | HS3 | - | Nej |
| Nät L1-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_l1_power` | Sensor | W | HS3 | - | Nej |
| Nät L1-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_l1_voltage` | Sensor | V | HS3 | - | Nej |
| Nät L1-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_l1_current` | Sensor | A | HS3 | - | Nej |
| Nät L1-frekvens (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_l1_frequency` | Sensor | Hz | HS3 | - | Nej |
| Nät L2-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_l2_power` | Sensor | W | HS3 | Fas 2 och högre | Nej |
| Nät L2-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_l2_voltage` | Sensor | V | HS3 | Fas 2 och högre | Nej |
| Nät L2-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_l2_current` | Sensor | A | HS3 | Fas 2 och högre | Nej |
| Nät L2-frekvens (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_l2_frequency` | Sensor | Hz | HS3 | Fas 2 och högre | Nej |
| Nät L3-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_l3_power` | Sensor | W | HS3 | Fas 3 och högre | Nej |
| Nät L3-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_l3_voltage` | Sensor | V | HS3 | Fas 3 och högre | Nej |
| Nät L3-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_l3_current` | Sensor | A | HS3 | Fas 3 och högre | Nej |
| Nät L3-frekvens (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_l3_frequency` | Sensor | Hz | HS3 | Fas 3 och högre | Nej |
| Växelriktareffekt (medelvärde 5 min) | `sensor.saj_five_minute_average_inverter_power` | Sensor | W | HS3 | - | Nej |
| Växelriktare L1-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_inverter_l1_power` | Sensor | W | HS3 | - | Nej |
| Växelriktare L1-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_inverter_l1_voltage` | Sensor | V | HS3 | - | Nej |
| Växelriktare L1-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_inverter_l1_current` | Sensor | A | HS3 | - | Nej |
| Växelriktare L1-frekvens (medelvärde 5 min) | `sensor.saj_five_minute_average_inverter_l1_frequency` | Sensor | Hz | HS3 | - | Nej |
| Växelriktare L2-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_inverter_l2_power` | Sensor | W | HS3 | Fas 2 och högre | Nej |
| Växelriktare L2-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_inverter_l2_voltage` | Sensor | V | HS3 | Fas 2 och högre | Nej |
| Växelriktare L2-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_inverter_l2_current` | Sensor | A | HS3 | Fas 2 och högre | Nej |
| Växelriktare L2-frekvens (medelvärde 5 min) | `sensor.saj_five_minute_average_inverter_l2_frequency` | Sensor | Hz | HS3 | Fas 2 och högre | Nej |
| Växelriktare L3-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_inverter_l3_power` | Sensor | W | HS3 | Fas 3 och högre | Nej |
| Växelriktare L3-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_inverter_l3_voltage` | Sensor | V | HS3 | Fas 3 och högre | Nej |
| Växelriktare L3-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_inverter_l3_current` | Sensor | A | HS3 | Fas 3 och högre | Nej |
| Växelriktare L3-frekvens (medelvärde 5 min) | `sensor.saj_five_minute_average_inverter_l3_frequency` | Sensor | Hz | HS3 | Fas 3 och högre | Nej |
| Hushållslasteffekt (medelvärde 5 min) | `sensor.saj_five_minute_average_load_power` | Sensor | W | HS3 | - | Nej |
| Hushållslast L1-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_load_l1_power` | Sensor | W | HS3 | - | Nej |
| Hushållslast L1-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_load_l1_voltage` | Sensor | V | HS3 | - | Nej |
| Hushållslast L1-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_load_l1_current` | Sensor | A | HS3 | - | Nej |
| Hushållslast L1-frekvens (medelvärde 5 min) | `sensor.saj_five_minute_average_load_l1_frequency` | Sensor | Hz | HS3 | - | Nej |
| Hushållslast L2-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_load_l2_power` | Sensor | W | HS3 | Fas 2 och högre | Nej |
| Hushållslast L2-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_load_l2_voltage` | Sensor | V | HS3 | Fas 2 och högre | Nej |
| Hushållslast L2-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_load_l2_current` | Sensor | A | HS3 | Fas 2 och högre | Nej |
| Hushållslast L2-frekvens (medelvärde 5 min) | `sensor.saj_five_minute_average_load_l2_frequency` | Sensor | Hz | HS3 | Fas 2 och högre | Nej |
| Hushållslast L3-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_load_l3_power` | Sensor | W | HS3 | Fas 3 och högre | Nej |
| Hushållslast L3-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_load_l3_voltage` | Sensor | V | HS3 | Fas 3 och högre | Nej |
| Hushållslast L3-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_load_l3_current` | Sensor | A | HS3 | Fas 3 och högre | Nej |
| Hushållslast L3-frekvens (medelvärde 5 min) | `sensor.saj_five_minute_average_load_l3_frequency` | Sensor | Hz | HS3 | Fas 3 och högre | Nej |
| Nätlasteffekt (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_load_power` | Sensor | W | HS3 | - | Nej |
| Nätlast L1-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_load_l1_power` | Sensor | W | HS3 | - | Nej |
| Nätlast L1-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_load_l1_voltage` | Sensor | V | HS3 | - | Nej |
| Nätlast L1-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_load_l1_current` | Sensor | A | HS3 | - | Nej |
| Nätlast L1-frekvens (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_load_l1_frequency` | Sensor | Hz | HS3 | - | Nej |
| Nätlast L2-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_load_l2_power` | Sensor | W | HS3 | Fas 2 och högre | Nej |
| Nätlast L2-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_load_l2_voltage` | Sensor | V | HS3 | Fas 2 och högre | Nej |
| Nätlast L2-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_load_l2_current` | Sensor | A | HS3 | Fas 2 och högre | Nej |
| Nätlast L2-frekvens (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_load_l2_frequency` | Sensor | Hz | HS3 | Fas 2 och högre | Nej |
| Nätlast L3-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_load_l3_power` | Sensor | W | HS3 | Fas 3 och högre | Nej |
| Nätlast L3-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_load_l3_voltage` | Sensor | V | HS3 | Fas 3 och högre | Nej |
| Nätlast L3-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_load_l3_current` | Sensor | A | HS3 | Fas 3 och högre | Nej |
| Nätlast L3-frekvens (medelvärde 5 min) | `sensor.saj_five_minute_average_grid_load_l3_frequency` | Sensor | Hz | HS3 | Fas 3 och högre | Nej |
| Reserveffekt (medelvärde 5 min) | `sensor.saj_five_minute_average_backup_power` | Sensor | W | HS3 | - | Nej |
| Reserv L1-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_backup_l1_power` | Sensor | W | HS3 | - | Nej |
| Reserv L1-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_backup_l1_voltage` | Sensor | V | HS3 | - | Nej |
| Reserv L1-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_backup_l1_current` | Sensor | A | HS3 | - | Nej |
| Reserv L1-frekvens (medelvärde 5 min) | `sensor.saj_five_minute_average_backup_l1_frequency` | Sensor | Hz | HS3 | - | Nej |
| Reserv L2-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_backup_l2_power` | Sensor | W | HS3 | Fas 2 och högre | Nej |
| Reserv L2-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_backup_l2_voltage` | Sensor | V | HS3 | Fas 2 och högre | Nej |
| Reserv L2-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_backup_l2_current` | Sensor | A | HS3 | Fas 2 och högre | Nej |
| Reserv L2-frekvens (medelvärde 5 min) | `sensor.saj_five_minute_average_backup_l2_frequency` | Sensor | Hz | HS3 | Fas 2 och högre | Nej |
| Reserv L3-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_backup_l3_power` | Sensor | W | HS3 | Fas 3 och högre | Nej |
| Reserv L3-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_backup_l3_voltage` | Sensor | V | HS3 | Fas 3 och högre | Nej |
| Reserv L3-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_backup_l3_current` | Sensor | A | HS3 | Fas 3 och högre | Nej |
| Reserv L3-frekvens (medelvärde 5 min) | `sensor.saj_five_minute_average_backup_l3_frequency` | Sensor | Hz | HS3 | Fas 3 och högre | Nej |
| Soleffekt (medelvärde 5 min) | `sensor.saj_five_minute_average_pv_power` | Sensor | W | HS3 | - | Nej |
| PV1-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_pv1_voltage` | Sensor | V | HS3 | - | Nej |
| PV1-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_pv1_current` | Sensor | A | HS3 | - | Nej |
| PV1-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_pv1_power` | Sensor | W | HS3 | - | Nej |
| PV2-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_pv2_voltage` | Sensor | V | HS3 | PV-sträng 2 och högre | Nej |
| PV2-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_pv2_current` | Sensor | A | HS3 | PV-sträng 2 och högre | Nej |
| PV2-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_pv2_power` | Sensor | W | HS3 | PV-sträng 2 och högre | Nej |
| Generatoreffekt (medelvärde 5 min) | `sensor.saj_five_minute_average_generator_power` | Sensor | W | HS3 | - | Nej |
| Generator L1-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_generator_l1_power` | Sensor | W | HS3 | - | Nej |
| Generator L1-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_generator_l1_voltage` | Sensor | V | HS3 | - | Nej |
| Generator L1-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_generator_l1_current` | Sensor | A | HS3 | - | Nej |
| Generator L1-frekvens (medelvärde 5 min) | `sensor.saj_five_minute_average_generator_l1_frequency` | Sensor | Hz | HS3 | - | Nej |
| Generator L2-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_generator_l2_power` | Sensor | W | HS3 | Fas 2 och högre | Nej |
| Generator L2-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_generator_l2_voltage` | Sensor | V | HS3 | Fas 2 och högre | Nej |
| Generator L2-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_generator_l2_current` | Sensor | A | HS3 | Fas 2 och högre | Nej |
| Generator L2-frekvens (medelvärde 5 min) | `sensor.saj_five_minute_average_generator_l2_frequency` | Sensor | Hz | HS3 | Fas 2 och högre | Nej |
| Generator L3-effekt (medelvärde 5 min) | `sensor.saj_five_minute_average_generator_l3_power` | Sensor | W | HS3 | Fas 3 och högre | Nej |
| Generator L3-spänning (medelvärde 5 min) | `sensor.saj_five_minute_average_generator_l3_voltage` | Sensor | V | HS3 | Fas 3 och högre | Nej |
| Generator L3-ström (medelvärde 5 min) | `sensor.saj_five_minute_average_generator_l3_current` | Sensor | A | HS3 | Fas 3 och högre | Nej |
| Generator L3-frekvens (medelvärde 5 min) | `sensor.saj_five_minute_average_generator_l3_frequency` | Sensor | Hz | HS3 | Fas 3 och högre | Nej |
| Produktkod | `sensor.saj_product_code` | Sensor | - | HS3, H2 | - | Nej |
| Displayns programvaruversion | `sensor.saj_display_software_version` | Sensor | - | HS3, H2 | - | Nej |
| Masterns programvaruversion | `sensor.saj_master_software_version` | Sensor | - | HS3, H2 | - | Nej |
| Slavens programvaruversion | `sensor.saj_slave_software_version` | Sensor | - | HS3, H2 | - | Nej |
| Displayns maskinvaruversion | `sensor.saj_display_hardware_version` | Sensor | - | HS3, H2 | - | Nej |
| Styrningens maskinvaruversion | `sensor.saj_control_hardware_version` | Sensor | - | HS3, H2 | - | Nej |
| Effektdelens maskinvaruversion | `sensor.saj_power_hardware_version` | Sensor | - | HS3, H2 | - | Nej |
| Antal batteripack | `sensor.saj_battery_pack_count` | Sensor | - | HS3, H2 | - | Nej |
| Mätare A status | `sensor.saj_meter_a_status` | Sensor | - | HS3, H2 | - | Nej |
| Mätare B status | `sensor.saj_meter_b_status` | Sensor | - | HS3, H2 | - | Nej |
| Reservlast effekt | `sensor.saj_backup_load_power` | Sensor | W | HS3, H2 | - | Ja |
| Hushållslasteffekt | `sensor.saj_load_power` | Sensor | W | HS3, H2 | - | Ja |
| Egenanvändning idag | `sensor.saj_self_consumption_today` | Sensor | % | HS3, H2 | - | Nej |
| Självförsörjning idag | `sensor.saj_self_sufficiency_today` | Sensor | % | HS3, H2 | - | Nej |
| Solöverskottseffekt | `sensor.saj_solar_surplus_power` | Sensor | W | HS3, H2 | - | Nej |
| Läge för omvänt flöde | `sensor.saj_reverse_flow_mode` | Sensor | - | H2 | - | Nej |
| FCAS frekvenshysteres | `sensor.saj_fcas_frequency_hysteresis` | Sensor | Hz | H2 | - | Nej |
| Parallellroll | `sensor.saj_parallel_role` | Sensor | - | H2 | - | Nej |
| Parallellnummer | `sensor.saj_parallel_number` | Sensor | - | H2 | - | Nej |
| Konfigurerat parallelläge | `sensor.saj_parallel_configured_mode` | Sensor | - | H2 | - | Nej |
| Batteriingångsläge | `sensor.saj_battery_input_mode` | Sensor | - | H2 | - | Nej |
| PV-ingångsläge | `sensor.saj_pv_input_mode` | Sensor | - | H2 | - | Nej |
| Fristående läge | `sensor.saj_off_grid_mode` | Sensor | - | H2 | - | Nej |
| Fristående utgångsspänning | `sensor.saj_off_grid_output_voltage` | Sensor | V | H2 | - | Nej |
| Fristående utgångsfrekvens | `sensor.saj_off_grid_output_frequency` | Sensor | Hz | H2 | - | Nej |
| Motoraktivering | `sensor.saj_motor_enable` | Sensor | - | H2 | - | Nej |
| Maskinmodell | `sensor.saj_machine_model` | Sensor | - | H2 | - | Nej |
| Märkeffekt | `sensor.saj_rated_power` | Sensor | W | H2 | - | Nej |
| Funktionsflaggor 1 | `sensor.saj_function_flags_1` | Sensor | - | H2 | - | Nej |
| Funktionsflaggor 2 | `sensor.saj_function_flags_2` | Sensor | - | H2 | - | Nej |
| Största likströmskomponent | `sensor.saj_max_dc_current_component` | Sensor | mA | H2 | - | Nej |
| Största likspänningskomponent | `sensor.saj_max_dc_voltage_component` | Sensor | V | H2 | - | Nej |
| Gräns för isolationsresistans | `sensor.saj_insulation_resistance_limit` | Sensor | kΩ | H2 | - | Nej |
| Största läckström | `sensor.saj_max_leakage_current` | Sensor | mA | H2 | - | Nej |
| Växelriktarstopp | `sensor.saj_inverter_stop` | Sensor | - | H2 | - | Nej |
| PV-startspänning | `sensor.saj_pv_start_voltage` | Sensor | V | H2 | - | Nej |
| PV-avstängningsspänning | `sensor.saj_pv_shutdown_voltage` | Sensor | V | H2 | - | Nej |
| MPPT-spänning hög | `sensor.saj_mppt_voltage_high` | Sensor | V | H2 | - | Nej |
| MPPT-spänning låg | `sensor.saj_mppt_voltage_low` | Sensor | V | H2 | - | Nej |
| MPPT-skanningstid | `sensor.saj_mppt_scan_time` | Sensor | min | H2 | - | Nej |
| Antal växelriktarfel | `sensor.saj_inverter_error_count` | Sensor | - | H2 | - | Nej |
| PV3-isolationsresistans | `sensor.saj_pv3_insulation_resistance` | Sensor | kΩ | H2 | PV-sträng 3 och högre | Nej |
| PV4-isolationsresistans | `sensor.saj_pv4_insulation_resistance` | Sensor | kΩ | H2 | PV-sträng 4 och högre | Nej |
| DRM maskinvarustatus | `sensor.saj_drm_hardware_status` | Sensor | - | H2 | - | Nej |
| DRM programvarustatus | `sensor.saj_drm_software_status` | Sensor | - | H2 | - | Nej |
| Felposternas ordningsnummer | `sensor.saj_fault_record_sequence` | Sensor | - | H2 | - | Nej |
| Applikationsläge (gällande) | `sensor.saj_application_mode_active` | Sensor | - | H2 | - | Nej |
| PV3-spänning | `sensor.saj_pv3_voltage` | Sensor | V | H2 | PV-sträng 3 och högre | Ja |
| PV3-ström | `sensor.saj_pv3_current` | Sensor | A | H2 | PV-sträng 3 och högre | Ja |
| PV3-effekt | `sensor.saj_pv3_power` | Sensor | W | H2 | PV-sträng 3 och högre | Ja |
| PV4-spänning | `sensor.saj_pv4_voltage` | Sensor | V | H2 | PV-sträng 4 och högre | Ja |
| PV4-ström | `sensor.saj_pv4_current` | Sensor | A | H2 | PV-sträng 4 och högre | Ja |
| PV4-effekt | `sensor.saj_pv4_power` | Sensor | W | H2 | PV-sträng 4 och högre | Ja |
| CT-näteffekt | `sensor.saj_ct_grid_power` | Sensor | W | H2 | - | Nej |
| Skenbar CT-näteffekt | `sensor.saj_ct_grid_apparent_power` | Sensor | VA | H2 | - | Nej |
| CT-soleffekt | `sensor.saj_ct_pv_power` | Sensor | W | H2 | - | Nej |
| Skenbar CT-soleffekt | `sensor.saj_ct_pv_apparent_power` | Sensor | VA | H2 | - | Nej |
| Växelriktare skenbar effekt | `sensor.saj_inverter_apparent_power` | Sensor | VA | H2 | - | Nej |
| Reservlast skenbar effekt | `sensor.saj_backup_load_apparent_power` | Sensor | VA | H2 | - | Nej |
| Soltid idag | `sensor.saj_pv_generation_time_today` | Sensor | h | H2 | - | Nej |
| Soltid totalt | `sensor.saj_pv_generation_time_total` | Sensor | h | H2 | - | Nej |
| Växelriktarenergi idag | `sensor.saj_inverter_energy_today` | Sensor | kWh | H2 | - | Nej |
| Växelriktarenergi denna månad | `sensor.saj_inverter_energy_month` | Sensor | kWh | H2 | - | Nej |
| Växelriktarenergi i år | `sensor.saj_inverter_energy_year` | Sensor | kWh | H2 | - | Nej |
| Växelriktarenergi totalt | `sensor.saj_inverter_energy_total` | Sensor | kWh | H2 | - | Nej |
| PV2-energi idag | `sensor.saj_pv2_energy_today` | Sensor | kWh | H2 | PV-sträng 2 och högre | Nej |
| PV2-energi denna månad | `sensor.saj_pv2_energy_month` | Sensor | kWh | H2 | PV-sträng 2 och högre | Nej |
| PV2-energi i år | `sensor.saj_pv2_energy_year` | Sensor | kWh | H2 | PV-sträng 2 och högre | Nej |
| PV2-energi totalt | `sensor.saj_pv2_energy_total` | Sensor | kWh | H2 | PV-sträng 2 och högre | Nej |
| PV3-energi idag | `sensor.saj_pv3_energy_today` | Sensor | kWh | H2 | PV-sträng 3 och högre | Nej |
| PV3-energi denna månad | `sensor.saj_pv3_energy_month` | Sensor | kWh | H2 | PV-sträng 3 och högre | Nej |
| PV3-energi i år | `sensor.saj_pv3_energy_year` | Sensor | kWh | H2 | PV-sträng 3 och högre | Nej |
| PV3-energi totalt | `sensor.saj_pv3_energy_total` | Sensor | kWh | H2 | PV-sträng 3 och högre | Nej |
| Identitetsprotokollversion | `sensor.saj_identity_protocol_version` | Sensor | - | H2 | - | Nej |
