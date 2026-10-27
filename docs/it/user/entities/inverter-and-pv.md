[en](../../../en-gb/user/entities/inverter-and-pv.md) | [de](../../../de/user/entities/inverter-and-pv.md) | [nl](../../../nl/user/entities/inverter-and-pv.md) | [fr](../../../fr/user/entities/inverter-and-pv.md) | [zh](../../../zh-hans/user/entities/inverter-and-pv.md) | [es](../../../es/user/entities/inverter-and-pv.md) | it | [pl](../../../pl/user/entities/inverter-and-pv.md) | [sv](../../../sv/user/entities/inverter-and-pv.md)

# Inverter e solare

Uscita dell'inverter, stringhe solari, porta di backup, contatori di energia, versioni e carico domestico.

Le entità dell'area «Inverter e solare» sono descritte nell'elenco delle funzionalità dell'integrazione, in [Dispositivi ed entità](../../../../custom_components/saj_local/docs/features.md#devices-and-entities).

241 entità. Generato da `make docs`. Non modificare a mano.

Un prefisso impostato in Configura va dopo `saj_` nell'ID di ogni entità dell'area «Inverter e solare», per esempio `sensor.saj_house_ethernet_protocol_version` con il prefisso `house`.

| Nome | ID entità | Tipo | Unità | Modelli | Apparecchiature e quantità | Abilitata per impostazione predefinita |
| --- | --- | --- | --- | --- | --- | --- |
| Versione del protocollo Ethernet | `sensor.saj_ethernet_protocol_version` | Sensore | - | HS3 | - | No |
| Indirizzo MAC Ethernet | `sensor.saj_ethernet_mac_address` | Sensore | - | HS3 | - | No |
| Modalità Ethernet | `sensor.saj_ethernet_mode` | Sensore | - | HS3 | - | No |
| Indirizzo IP Ethernet | `sensor.saj_ethernet_ip_address` | Sensore | - | HS3 | - | No |
| Subnet mask Ethernet | `sensor.saj_ethernet_subnet_mask` | Sensore | - | HS3 | - | No |
| Gateway Ethernet | `sensor.saj_ethernet_gateway` | Sensore | - | HS3 | - | No |
| DNS primario Ethernet | `sensor.saj_ethernet_dns_primary` | Sensore | - | HS3 | - | No |
| DNS secondario Ethernet | `sensor.saj_ethernet_dns_secondary` | Sensore | - | HS3 | - | No |
| Sequenza delle impostazioni | `sensor.saj_settings_sequence` | Sensore | - | HS3, H2 | - | No |
| Versione del protocollo delle impostazioni | `sensor.saj_settings_protocol_version` | Sensore | - | HS3 | - | No |
| Configurazione del contatore | `sensor.saj_meter_configuration` | Sensore | - | HS3, H2 | - | No |
| Indirizzo del contatore | `sensor.saj_meter_address` | Sensore | - | HS3, H2 | - | No |
| Indirizzo RS485 | `sensor.saj_rs485_address` | Sensore | - | HS3, H2 | - | No |
| Baud rate RS485 | `sensor.saj_rs485_baud_rate` | Sensore | - | HS3, H2 | - | No |
| Protocollo della batteria | `sensor.saj_battery_protocol` | Sensore | - | HS3, H2 | - | No |
| Indirizzo slave RS485 | `sensor.saj_rs485_slave_address` | Sensore | - | HS3 | - | No |
| Baud rate slave RS485 | `sensor.saj_rs485_slave_baud_rate` | Sensore | - | HS3 | - | No |
| Orologio dell'inverter | `sensor.saj_inverter_clock` | Sensore | - | HS3, H2 | - | No |
| Modalità di funzionamento | `sensor.saj_operating_mode` | Sensore | - | HS3, H2 | - | Sì |
| Temperatura dell'inverter | `sensor.saj_inverter_temperature` | Sensore | °C | HS3, H2 | - | Sì |
| Temperatura ambiente | `sensor.saj_ambient_temperature` | Sensore | °C | HS3, H2 | - | No |
| Corrente di dispersione | `sensor.saj_leakage_current` | Sensore | mA | HS3, H2 | - | No |
| Resistenza di isolamento PV1 | `sensor.saj_pv1_insulation_resistance` | Sensore | kΩ | HS3, H2 | - | No |
| Resistenza di isolamento PV2 | `sensor.saj_pv2_insulation_resistance` | Sensore | kΩ | HS3, H2 | Stringa PV 2 e successive | No |
| Valore impostato della potenza di scarica dell'inverter | `sensor.saj_inverter_discharge_power_setpoint` | Sensore | W | HS3, H2 | - | No |
| Valore impostato della potenza di carica dell'inverter | `sensor.saj_inverter_charge_power_setpoint` | Sensore | W | HS3, H2 | - | No |
| Protocollo della batteria (in vigore) | `sensor.saj_battery_protocol_active` | Sensore | - | HS3, H2 | - | No |
| Configurazione del contatore (in vigore) | `sensor.saj_meter_configuration_active` | Sensore | - | HS3, H2 | - | No |
| Tensione inverter L1 | `sensor.saj_inverter_l1_voltage` | Sensore | V | HS3, H2 | - | No |
| Corrente inverter L1 | `sensor.saj_inverter_l1_current` | Sensore | A | HS3, H2 | - | No |
| Frequenza inverter L1 | `sensor.saj_inverter_l1_frequency` | Sensore | Hz | HS3, H2 | - | No |
| Potenza inverter L1 | `sensor.saj_inverter_l1_power` | Sensore | W | HS3, H2 | - | No |
| Potenza apparente inverter L1 | `sensor.saj_inverter_l1_apparent_power` | Sensore | VA | HS3, H2 | - | No |
| Tensione inverter L2 | `sensor.saj_inverter_l2_voltage` | Sensore | V | HS3, H2 | Fase 2 e successive | No |
| Corrente inverter L2 | `sensor.saj_inverter_l2_current` | Sensore | A | HS3, H2 | Fase 2 e successive | No |
| Frequenza inverter L2 | `sensor.saj_inverter_l2_frequency` | Sensore | Hz | HS3, H2 | Fase 2 e successive | No |
| Potenza inverter L2 | `sensor.saj_inverter_l2_power` | Sensore | W | HS3, H2 | Fase 2 e successive | No |
| Potenza apparente inverter L2 | `sensor.saj_inverter_l2_apparent_power` | Sensore | VA | HS3, H2 | Fase 2 e successive | No |
| Tensione inverter L3 | `sensor.saj_inverter_l3_voltage` | Sensore | V | HS3, H2 | Fase 3 e successive | No |
| Corrente inverter L3 | `sensor.saj_inverter_l3_current` | Sensore | A | HS3, H2 | Fase 3 e successive | No |
| Frequenza inverter L3 | `sensor.saj_inverter_l3_frequency` | Sensore | Hz | HS3, H2 | Fase 3 e successive | No |
| Potenza inverter L3 | `sensor.saj_inverter_l3_power` | Sensore | W | HS3, H2 | Fase 3 e successive | No |
| Potenza apparente inverter L3 | `sensor.saj_inverter_l3_apparent_power` | Sensore | VA | HS3, H2 | Fase 3 e successive | No |
| Tensione backup L1 | `sensor.saj_backup_l1_voltage` | Sensore | V | HS3, H2 | - | No |
| Corrente backup L1 | `sensor.saj_backup_l1_current` | Sensore | A | HS3, H2 | - | No |
| Frequenza backup L1 | `sensor.saj_backup_l1_frequency` | Sensore | Hz | HS3, H2 | - | No |
| Tensione continua backup L1 | `sensor.saj_backup_l1_dc_voltage` | Sensore | mV | HS3, H2 | - | No |
| Potenza backup L1 | `sensor.saj_backup_l1_power` | Sensore | W | HS3, H2 | - | No |
| Potenza apparente backup L1 | `sensor.saj_backup_l1_apparent_power` | Sensore | VA | HS3, H2 | - | No |
| Tensione backup L2 | `sensor.saj_backup_l2_voltage` | Sensore | V | HS3, H2 | Fase 2 e successive | No |
| Corrente backup L2 | `sensor.saj_backup_l2_current` | Sensore | A | HS3, H2 | Fase 2 e successive | No |
| Frequenza backup L2 | `sensor.saj_backup_l2_frequency` | Sensore | Hz | HS3, H2 | Fase 2 e successive | No |
| Tensione continua backup L2 | `sensor.saj_backup_l2_dc_voltage` | Sensore | mV | HS3, H2 | Fase 2 e successive | No |
| Potenza backup L2 | `sensor.saj_backup_l2_power` | Sensore | W | HS3, H2 | Fase 2 e successive | No |
| Potenza apparente backup L2 | `sensor.saj_backup_l2_apparent_power` | Sensore | VA | HS3, H2 | Fase 2 e successive | No |
| Tensione backup L3 | `sensor.saj_backup_l3_voltage` | Sensore | V | HS3, H2 | Fase 3 e successive | No |
| Corrente backup L3 | `sensor.saj_backup_l3_current` | Sensore | A | HS3, H2 | Fase 3 e successive | No |
| Frequenza backup L3 | `sensor.saj_backup_l3_frequency` | Sensore | Hz | HS3, H2 | Fase 3 e successive | No |
| Tensione continua backup L3 | `sensor.saj_backup_l3_dc_voltage` | Sensore | mV | HS3, H2 | Fase 3 e successive | No |
| Potenza backup L3 | `sensor.saj_backup_l3_power` | Sensore | W | HS3, H2 | Fase 3 e successive | No |
| Potenza apparente backup L3 | `sensor.saj_backup_l3_apparent_power` | Sensore | VA | HS3, H2 | Fase 3 e successive | No |
| Tensione del bus CC | `sensor.saj_dc_bus_voltage` | Sensore | V | HS3, H2 | - | No |
| Tensione del bus CC slave | `sensor.saj_dc_bus_slave_voltage` | Sensore | V | HS3, H2 | - | No |
| Tensione PV1 | `sensor.saj_pv1_voltage` | Sensore | V | HS3, H2 | - | Sì |
| Corrente PV1 | `sensor.saj_pv1_current` | Sensore | A | HS3, H2 | - | Sì |
| Potenza PV1 | `sensor.saj_pv1_power` | Sensore | W | HS3, H2 | - | Sì |
| Tensione PV2 | `sensor.saj_pv2_voltage` | Sensore | V | HS3, H2 | Stringa PV 2 e successive | Sì |
| Corrente PV2 | `sensor.saj_pv2_current` | Sensore | A | HS3, H2 | Stringa PV 2 e successive | Sì |
| Potenza PV2 | `sensor.saj_pv2_power` | Sensore | W | HS3, H2 | Stringa PV 2 e successive | Sì |
| Potenza del carico domestico | `sensor.saj_load_power` | Sensore | W | HS3, H2 | - | Sì |
| Potenza solare | `sensor.saj_pv_power` | Sensore | W | HS3, H2 | - | Sì |
| Potenza dell'inverter | `sensor.saj_inverter_power` | Sensore | W | HS3, H2 | - | Sì |
| Energia solare oggi | `sensor.saj_pv_energy_today` | Sensore | kWh | HS3, H2 | - | Sì |
| Energia solare questo mese | `sensor.saj_pv_energy_month` | Sensore | kWh | HS3, H2 | - | No |
| Energia solare quest'anno | `sensor.saj_pv_energy_year` | Sensore | kWh | HS3, H2 | - | No |
| Energia solare totale | `sensor.saj_pv_energy_total` | Sensore | kWh | HS3, H2 | - | Sì |
| Energia del carico domestico oggi | `sensor.saj_load_energy_today` | Sensore | kWh | HS3, H2 | - | Sì |
| Energia del carico domestico questo mese | `sensor.saj_load_energy_month` | Sensore | kWh | HS3, H2 | - | No |
| Energia del carico domestico quest'anno | `sensor.saj_load_energy_year` | Sensore | kWh | HS3, H2 | - | No |
| Energia del carico domestico totale | `sensor.saj_load_energy_total` | Sensore | kWh | HS3, H2 | - | Sì |
| Energia dei carichi di backup oggi | `sensor.saj_backup_load_energy_today` | Sensore | kWh | HS3, H2 | - | Sì |
| Energia dei carichi di backup questo mese | `sensor.saj_backup_load_energy_month` | Sensore | kWh | HS3, H2 | - | No |
| Energia dei carichi di backup quest'anno | `sensor.saj_backup_load_energy_year` | Sensore | kWh | HS3, H2 | - | No |
| Energia dei carichi di backup totale | `sensor.saj_backup_load_energy_total` | Sensore | kWh | HS3, H2 | - | Sì |
| Modalità parallelo | `sensor.saj_parallel_mode` | Sensore | - | HS3, H2 | - | No |
| Macchine in parallelo online | `sensor.saj_parallel_online_count` | Sensore | - | HS3, H2 | - | No |
| Potenza della rete (media 5 minuti) | `sensor.saj_five_minute_average_grid_power` | Sensore | W | HS3 | - | No |
| Potenza rete L1 (media 5 minuti) | `sensor.saj_five_minute_average_grid_l1_power` | Sensore | W | HS3 | - | No |
| Tensione rete L1 (media 5 minuti) | `sensor.saj_five_minute_average_grid_l1_voltage` | Sensore | V | HS3 | - | No |
| Corrente rete L1 (media 5 minuti) | `sensor.saj_five_minute_average_grid_l1_current` | Sensore | A | HS3 | - | No |
| Frequenza rete L1 (media 5 minuti) | `sensor.saj_five_minute_average_grid_l1_frequency` | Sensore | Hz | HS3 | - | No |
| Potenza rete L2 (media 5 minuti) | `sensor.saj_five_minute_average_grid_l2_power` | Sensore | W | HS3 | Fase 2 e successive | No |
| Tensione rete L2 (media 5 minuti) | `sensor.saj_five_minute_average_grid_l2_voltage` | Sensore | V | HS3 | Fase 2 e successive | No |
| Corrente rete L2 (media 5 minuti) | `sensor.saj_five_minute_average_grid_l2_current` | Sensore | A | HS3 | Fase 2 e successive | No |
| Frequenza rete L2 (media 5 minuti) | `sensor.saj_five_minute_average_grid_l2_frequency` | Sensore | Hz | HS3 | Fase 2 e successive | No |
| Potenza rete L3 (media 5 minuti) | `sensor.saj_five_minute_average_grid_l3_power` | Sensore | W | HS3 | Fase 3 e successive | No |
| Tensione rete L3 (media 5 minuti) | `sensor.saj_five_minute_average_grid_l3_voltage` | Sensore | V | HS3 | Fase 3 e successive | No |
| Corrente rete L3 (media 5 minuti) | `sensor.saj_five_minute_average_grid_l3_current` | Sensore | A | HS3 | Fase 3 e successive | No |
| Frequenza rete L3 (media 5 minuti) | `sensor.saj_five_minute_average_grid_l3_frequency` | Sensore | Hz | HS3 | Fase 3 e successive | No |
| Potenza dell'inverter (media 5 minuti) | `sensor.saj_five_minute_average_inverter_power` | Sensore | W | HS3 | - | No |
| Potenza inverter L1 (media 5 minuti) | `sensor.saj_five_minute_average_inverter_l1_power` | Sensore | W | HS3 | - | No |
| Tensione inverter L1 (media 5 minuti) | `sensor.saj_five_minute_average_inverter_l1_voltage` | Sensore | V | HS3 | - | No |
| Corrente inverter L1 (media 5 minuti) | `sensor.saj_five_minute_average_inverter_l1_current` | Sensore | A | HS3 | - | No |
| Frequenza inverter L1 (media 5 minuti) | `sensor.saj_five_minute_average_inverter_l1_frequency` | Sensore | Hz | HS3 | - | No |
| Potenza inverter L2 (media 5 minuti) | `sensor.saj_five_minute_average_inverter_l2_power` | Sensore | W | HS3 | Fase 2 e successive | No |
| Tensione inverter L2 (media 5 minuti) | `sensor.saj_five_minute_average_inverter_l2_voltage` | Sensore | V | HS3 | Fase 2 e successive | No |
| Corrente inverter L2 (media 5 minuti) | `sensor.saj_five_minute_average_inverter_l2_current` | Sensore | A | HS3 | Fase 2 e successive | No |
| Frequenza inverter L2 (media 5 minuti) | `sensor.saj_five_minute_average_inverter_l2_frequency` | Sensore | Hz | HS3 | Fase 2 e successive | No |
| Potenza inverter L3 (media 5 minuti) | `sensor.saj_five_minute_average_inverter_l3_power` | Sensore | W | HS3 | Fase 3 e successive | No |
| Tensione inverter L3 (media 5 minuti) | `sensor.saj_five_minute_average_inverter_l3_voltage` | Sensore | V | HS3 | Fase 3 e successive | No |
| Corrente inverter L3 (media 5 minuti) | `sensor.saj_five_minute_average_inverter_l3_current` | Sensore | A | HS3 | Fase 3 e successive | No |
| Frequenza inverter L3 (media 5 minuti) | `sensor.saj_five_minute_average_inverter_l3_frequency` | Sensore | Hz | HS3 | Fase 3 e successive | No |
| Potenza del carico domestico (media 5 minuti) | `sensor.saj_five_minute_average_load_power` | Sensore | W | HS3 | - | No |
| Potenza carico domestico L1 (media 5 minuti) | `sensor.saj_five_minute_average_load_l1_power` | Sensore | W | HS3 | - | No |
| Tensione carico domestico L1 (media 5 minuti) | `sensor.saj_five_minute_average_load_l1_voltage` | Sensore | V | HS3 | - | No |
| Corrente carico domestico L1 (media 5 minuti) | `sensor.saj_five_minute_average_load_l1_current` | Sensore | A | HS3 | - | No |
| Frequenza carico domestico L1 (media 5 minuti) | `sensor.saj_five_minute_average_load_l1_frequency` | Sensore | Hz | HS3 | - | No |
| Potenza carico domestico L2 (media 5 minuti) | `sensor.saj_five_minute_average_load_l2_power` | Sensore | W | HS3 | Fase 2 e successive | No |
| Tensione carico domestico L2 (media 5 minuti) | `sensor.saj_five_minute_average_load_l2_voltage` | Sensore | V | HS3 | Fase 2 e successive | No |
| Corrente carico domestico L2 (media 5 minuti) | `sensor.saj_five_minute_average_load_l2_current` | Sensore | A | HS3 | Fase 2 e successive | No |
| Frequenza carico domestico L2 (media 5 minuti) | `sensor.saj_five_minute_average_load_l2_frequency` | Sensore | Hz | HS3 | Fase 2 e successive | No |
| Potenza carico domestico L3 (media 5 minuti) | `sensor.saj_five_minute_average_load_l3_power` | Sensore | W | HS3 | Fase 3 e successive | No |
| Tensione carico domestico L3 (media 5 minuti) | `sensor.saj_five_minute_average_load_l3_voltage` | Sensore | V | HS3 | Fase 3 e successive | No |
| Corrente carico domestico L3 (media 5 minuti) | `sensor.saj_five_minute_average_load_l3_current` | Sensore | A | HS3 | Fase 3 e successive | No |
| Frequenza carico domestico L3 (media 5 minuti) | `sensor.saj_five_minute_average_load_l3_frequency` | Sensore | Hz | HS3 | Fase 3 e successive | No |
| Potenza del carico di rete (media 5 minuti) | `sensor.saj_five_minute_average_grid_load_power` | Sensore | W | HS3 | - | No |
| Potenza carico di rete L1 (media 5 minuti) | `sensor.saj_five_minute_average_grid_load_l1_power` | Sensore | W | HS3 | - | No |
| Tensione carico di rete L1 (media 5 minuti) | `sensor.saj_five_minute_average_grid_load_l1_voltage` | Sensore | V | HS3 | - | No |
| Corrente carico di rete L1 (media 5 minuti) | `sensor.saj_five_minute_average_grid_load_l1_current` | Sensore | A | HS3 | - | No |
| Frequenza carico di rete L1 (media 5 minuti) | `sensor.saj_five_minute_average_grid_load_l1_frequency` | Sensore | Hz | HS3 | - | No |
| Potenza carico di rete L2 (media 5 minuti) | `sensor.saj_five_minute_average_grid_load_l2_power` | Sensore | W | HS3 | Fase 2 e successive | No |
| Tensione carico di rete L2 (media 5 minuti) | `sensor.saj_five_minute_average_grid_load_l2_voltage` | Sensore | V | HS3 | Fase 2 e successive | No |
| Corrente carico di rete L2 (media 5 minuti) | `sensor.saj_five_minute_average_grid_load_l2_current` | Sensore | A | HS3 | Fase 2 e successive | No |
| Frequenza carico di rete L2 (media 5 minuti) | `sensor.saj_five_minute_average_grid_load_l2_frequency` | Sensore | Hz | HS3 | Fase 2 e successive | No |
| Potenza carico di rete L3 (media 5 minuti) | `sensor.saj_five_minute_average_grid_load_l3_power` | Sensore | W | HS3 | Fase 3 e successive | No |
| Tensione carico di rete L3 (media 5 minuti) | `sensor.saj_five_minute_average_grid_load_l3_voltage` | Sensore | V | HS3 | Fase 3 e successive | No |
| Corrente carico di rete L3 (media 5 minuti) | `sensor.saj_five_minute_average_grid_load_l3_current` | Sensore | A | HS3 | Fase 3 e successive | No |
| Frequenza carico di rete L3 (media 5 minuti) | `sensor.saj_five_minute_average_grid_load_l3_frequency` | Sensore | Hz | HS3 | Fase 3 e successive | No |
| Potenza backup (media 5 minuti) | `sensor.saj_five_minute_average_backup_power` | Sensore | W | HS3 | - | No |
| Potenza backup L1 (media 5 minuti) | `sensor.saj_five_minute_average_backup_l1_power` | Sensore | W | HS3 | - | No |
| Tensione backup L1 (media 5 minuti) | `sensor.saj_five_minute_average_backup_l1_voltage` | Sensore | V | HS3 | - | No |
| Corrente backup L1 (media 5 minuti) | `sensor.saj_five_minute_average_backup_l1_current` | Sensore | A | HS3 | - | No |
| Frequenza backup L1 (media 5 minuti) | `sensor.saj_five_minute_average_backup_l1_frequency` | Sensore | Hz | HS3 | - | No |
| Potenza backup L2 (media 5 minuti) | `sensor.saj_five_minute_average_backup_l2_power` | Sensore | W | HS3 | Fase 2 e successive | No |
| Tensione backup L2 (media 5 minuti) | `sensor.saj_five_minute_average_backup_l2_voltage` | Sensore | V | HS3 | Fase 2 e successive | No |
| Corrente backup L2 (media 5 minuti) | `sensor.saj_five_minute_average_backup_l2_current` | Sensore | A | HS3 | Fase 2 e successive | No |
| Frequenza backup L2 (media 5 minuti) | `sensor.saj_five_minute_average_backup_l2_frequency` | Sensore | Hz | HS3 | Fase 2 e successive | No |
| Potenza backup L3 (media 5 minuti) | `sensor.saj_five_minute_average_backup_l3_power` | Sensore | W | HS3 | Fase 3 e successive | No |
| Tensione backup L3 (media 5 minuti) | `sensor.saj_five_minute_average_backup_l3_voltage` | Sensore | V | HS3 | Fase 3 e successive | No |
| Corrente backup L3 (media 5 minuti) | `sensor.saj_five_minute_average_backup_l3_current` | Sensore | A | HS3 | Fase 3 e successive | No |
| Frequenza backup L3 (media 5 minuti) | `sensor.saj_five_minute_average_backup_l3_frequency` | Sensore | Hz | HS3 | Fase 3 e successive | No |
| Potenza solare (media 5 minuti) | `sensor.saj_five_minute_average_pv_power` | Sensore | W | HS3 | - | No |
| Tensione PV1 (media 5 minuti) | `sensor.saj_five_minute_average_pv1_voltage` | Sensore | V | HS3 | - | No |
| Corrente PV1 (media 5 minuti) | `sensor.saj_five_minute_average_pv1_current` | Sensore | A | HS3 | - | No |
| Potenza PV1 (media 5 minuti) | `sensor.saj_five_minute_average_pv1_power` | Sensore | W | HS3 | - | No |
| Tensione PV2 (media 5 minuti) | `sensor.saj_five_minute_average_pv2_voltage` | Sensore | V | HS3 | Stringa PV 2 e successive | No |
| Corrente PV2 (media 5 minuti) | `sensor.saj_five_minute_average_pv2_current` | Sensore | A | HS3 | Stringa PV 2 e successive | No |
| Potenza PV2 (media 5 minuti) | `sensor.saj_five_minute_average_pv2_power` | Sensore | W | HS3 | Stringa PV 2 e successive | No |
| Potenza del generatore (media 5 minuti) | `sensor.saj_five_minute_average_generator_power` | Sensore | W | HS3 | - | No |
| Potenza generatore L1 (media 5 minuti) | `sensor.saj_five_minute_average_generator_l1_power` | Sensore | W | HS3 | - | No |
| Tensione generatore L1 (media 5 minuti) | `sensor.saj_five_minute_average_generator_l1_voltage` | Sensore | V | HS3 | - | No |
| Corrente generatore L1 (media 5 minuti) | `sensor.saj_five_minute_average_generator_l1_current` | Sensore | A | HS3 | - | No |
| Frequenza generatore L1 (media 5 minuti) | `sensor.saj_five_minute_average_generator_l1_frequency` | Sensore | Hz | HS3 | - | No |
| Potenza generatore L2 (media 5 minuti) | `sensor.saj_five_minute_average_generator_l2_power` | Sensore | W | HS3 | Fase 2 e successive | No |
| Tensione generatore L2 (media 5 minuti) | `sensor.saj_five_minute_average_generator_l2_voltage` | Sensore | V | HS3 | Fase 2 e successive | No |
| Corrente generatore L2 (media 5 minuti) | `sensor.saj_five_minute_average_generator_l2_current` | Sensore | A | HS3 | Fase 2 e successive | No |
| Frequenza generatore L2 (media 5 minuti) | `sensor.saj_five_minute_average_generator_l2_frequency` | Sensore | Hz | HS3 | Fase 2 e successive | No |
| Potenza generatore L3 (media 5 minuti) | `sensor.saj_five_minute_average_generator_l3_power` | Sensore | W | HS3 | Fase 3 e successive | No |
| Tensione generatore L3 (media 5 minuti) | `sensor.saj_five_minute_average_generator_l3_voltage` | Sensore | V | HS3 | Fase 3 e successive | No |
| Corrente generatore L3 (media 5 minuti) | `sensor.saj_five_minute_average_generator_l3_current` | Sensore | A | HS3 | Fase 3 e successive | No |
| Frequenza generatore L3 (media 5 minuti) | `sensor.saj_five_minute_average_generator_l3_frequency` | Sensore | Hz | HS3 | Fase 3 e successive | No |
| Codice prodotto | `sensor.saj_product_code` | Sensore | - | HS3, H2 | - | No |
| Versione software del display | `sensor.saj_display_software_version` | Sensore | - | HS3, H2 | - | No |
| Versione software master | `sensor.saj_master_software_version` | Sensore | - | HS3, H2 | - | No |
| Versione software slave | `sensor.saj_slave_software_version` | Sensore | - | HS3, H2 | - | No |
| Versione hardware del display | `sensor.saj_display_hardware_version` | Sensore | - | HS3, H2 | - | No |
| Versione hardware di controllo | `sensor.saj_control_hardware_version` | Sensore | - | HS3, H2 | - | No |
| Versione hardware di potenza | `sensor.saj_power_hardware_version` | Sensore | - | HS3, H2 | - | No |
| Numero di moduli batteria | `sensor.saj_battery_pack_count` | Sensore | - | HS3, H2 | - | No |
| Stato del contatore A | `sensor.saj_meter_a_status` | Sensore | - | HS3, H2 | - | No |
| Stato del contatore B | `sensor.saj_meter_b_status` | Sensore | - | HS3, H2 | - | No |
| Potenza dei carichi di backup | `sensor.saj_backup_load_power` | Sensore | W | HS3, H2 | - | Sì |
| Modalità di flusso inverso | `sensor.saj_reverse_flow_mode` | Sensore | - | H2 | - | No |
| Isteresi di frequenza FCAS | `sensor.saj_fcas_frequency_hysteresis` | Sensore | Hz | H2 | - | No |
| Ruolo in parallelo | `sensor.saj_parallel_role` | Sensore | - | H2 | - | No |
| Numero in parallelo | `sensor.saj_parallel_number` | Sensore | - | H2 | - | No |
| Modalità parallelo configurata | `sensor.saj_parallel_configured_mode` | Sensore | - | H2 | - | No |
| Modalità di ingresso della batteria | `sensor.saj_battery_input_mode` | Sensore | - | H2 | - | No |
| Modalità di ingresso PV | `sensor.saj_pv_input_mode` | Sensore | - | H2 | - | No |
| Modalità off-grid | `sensor.saj_off_grid_mode` | Sensore | - | H2 | - | No |
| Tensione di uscita off-grid | `sensor.saj_off_grid_output_voltage` | Sensore | V | H2 | - | No |
| Frequenza di uscita off-grid | `sensor.saj_off_grid_output_frequency` | Sensore | Hz | H2 | - | No |
| Abilitazione del motore | `sensor.saj_motor_enable` | Sensore | - | H2 | - | No |
| Modello della macchina | `sensor.saj_machine_model` | Sensore | - | H2 | - | No |
| Potenza nominale | `sensor.saj_rated_power` | Sensore | W | H2 | - | No |
| Flag di funzione 1 | `sensor.saj_function_flags_1` | Sensore | - | H2 | - | No |
| Flag di funzione 2 | `sensor.saj_function_flags_2` | Sensore | - | H2 | - | No |
| Componente massima della corrente continua | `sensor.saj_max_dc_current_component` | Sensore | mA | H2 | - | No |
| Componente massima della tensione continua | `sensor.saj_max_dc_voltage_component` | Sensore | V | H2 | - | No |
| Limite della resistenza di isolamento | `sensor.saj_insulation_resistance_limit` | Sensore | kΩ | H2 | - | No |
| Corrente di dispersione massima | `sensor.saj_max_leakage_current` | Sensore | mA | H2 | - | No |
| Arresto dell'inverter | `sensor.saj_inverter_stop` | Sensore | - | H2 | - | No |
| Tensione di avvio PV | `sensor.saj_pv_start_voltage` | Sensore | V | H2 | - | No |
| Tensione di spegnimento PV | `sensor.saj_pv_shutdown_voltage` | Sensore | V | H2 | - | No |
| Tensione MPPT alta | `sensor.saj_mppt_voltage_high` | Sensore | V | H2 | - | No |
| Tensione MPPT bassa | `sensor.saj_mppt_voltage_low` | Sensore | V | H2 | - | No |
| Tempo di scansione MPPT | `sensor.saj_mppt_scan_time` | Sensore | min | H2 | - | No |
| Numero di errori dell'inverter | `sensor.saj_inverter_error_count` | Sensore | - | H2 | - | No |
| Resistenza di isolamento PV3 | `sensor.saj_pv3_insulation_resistance` | Sensore | kΩ | H2 | Stringa PV 3 e successive | No |
| Resistenza di isolamento PV4 | `sensor.saj_pv4_insulation_resistance` | Sensore | kΩ | H2 | Stringa PV 4 e successive | No |
| Stato hardware DRM | `sensor.saj_drm_hardware_status` | Sensore | - | H2 | - | No |
| Stato software DRM | `sensor.saj_drm_software_status` | Sensore | - | H2 | - | No |
| Sequenza dei registri dei guasti | `sensor.saj_fault_record_sequence` | Sensore | - | H2 | - | No |
| Modalità applicativa (in vigore) | `sensor.saj_application_mode_active` | Sensore | - | H2 | - | No |
| Tensione PV3 | `sensor.saj_pv3_voltage` | Sensore | V | H2 | Stringa PV 3 e successive | Sì |
| Corrente PV3 | `sensor.saj_pv3_current` | Sensore | A | H2 | Stringa PV 3 e successive | Sì |
| Potenza PV3 | `sensor.saj_pv3_power` | Sensore | W | H2 | Stringa PV 3 e successive | Sì |
| Tensione PV4 | `sensor.saj_pv4_voltage` | Sensore | V | H2 | Stringa PV 4 e successive | Sì |
| Corrente PV4 | `sensor.saj_pv4_current` | Sensore | A | H2 | Stringa PV 4 e successive | Sì |
| Potenza PV4 | `sensor.saj_pv4_power` | Sensore | W | H2 | Stringa PV 4 e successive | Sì |
| Potenza della rete CT | `sensor.saj_ct_grid_power` | Sensore | W | H2 | - | No |
| Potenza apparente della rete CT | `sensor.saj_ct_grid_apparent_power` | Sensore | VA | H2 | - | No |
| Potenza solare CT | `sensor.saj_ct_pv_power` | Sensore | W | H2 | - | No |
| Potenza apparente solare CT | `sensor.saj_ct_pv_apparent_power` | Sensore | VA | H2 | - | No |
| Potenza apparente dell'inverter | `sensor.saj_inverter_apparent_power` | Sensore | VA | H2 | - | No |
| Potenza apparente dei carichi di backup | `sensor.saj_backup_load_apparent_power` | Sensore | VA | H2 | - | No |
| Tempo di generazione solare oggi | `sensor.saj_pv_generation_time_today` | Sensore | h | H2 | - | No |
| Tempo di generazione solare totale | `sensor.saj_pv_generation_time_total` | Sensore | h | H2 | - | No |
| Energia dell'inverter oggi | `sensor.saj_inverter_energy_today` | Sensore | kWh | H2 | - | No |
| Energia dell'inverter questo mese | `sensor.saj_inverter_energy_month` | Sensore | kWh | H2 | - | No |
| Energia dell'inverter quest'anno | `sensor.saj_inverter_energy_year` | Sensore | kWh | H2 | - | No |
| Energia dell'inverter totale | `sensor.saj_inverter_energy_total` | Sensore | kWh | H2 | - | No |
| Energia PV2 oggi | `sensor.saj_pv2_energy_today` | Sensore | kWh | H2 | Stringa PV 2 e successive | No |
| Energia PV2 questo mese | `sensor.saj_pv2_energy_month` | Sensore | kWh | H2 | Stringa PV 2 e successive | No |
| Energia PV2 quest'anno | `sensor.saj_pv2_energy_year` | Sensore | kWh | H2 | Stringa PV 2 e successive | No |
| Energia PV2 totale | `sensor.saj_pv2_energy_total` | Sensore | kWh | H2 | Stringa PV 2 e successive | No |
| Energia PV3 oggi | `sensor.saj_pv3_energy_today` | Sensore | kWh | H2 | Stringa PV 3 e successive | No |
| Energia PV3 questo mese | `sensor.saj_pv3_energy_month` | Sensore | kWh | H2 | Stringa PV 3 e successive | No |
| Energia PV3 quest'anno | `sensor.saj_pv3_energy_year` | Sensore | kWh | H2 | Stringa PV 3 e successive | No |
| Energia PV3 totale | `sensor.saj_pv3_energy_total` | Sensore | kWh | H2 | Stringa PV 3 e successive | No |
| Versione del protocollo di identità | `sensor.saj_identity_protocol_version` | Sensore | - | H2 | - | No |
