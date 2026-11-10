[en](../../../en-gb/user/entities/inverter-and-pv.md) | [de](../../../de/user/entities/inverter-and-pv.md) | [nl](../../../nl/user/entities/inverter-and-pv.md) | fr | [zh](../../../zh-hans/user/entities/inverter-and-pv.md) | [es](../../../es/user/entities/inverter-and-pv.md) | [it](../../../it/user/entities/inverter-and-pv.md) | [pl](../../../pl/user/entities/inverter-and-pv.md) | [sv](../../../sv/user/entities/inverter-and-pv.md)

# Onduleur et solaire

Sortie de l'onduleur, chaînes solaires, port de secours, compteurs d'énergie, versions et charge domestique.

La liste des fonctionnalités de l'intégration explique les entités de Onduleur et solaire dans [Appareils et entités](../../../../custom_components/saj_local/docs/features.md#devices-and-entities).

244 entités. Généré par `make docs`. Ne pas modifier à la main.

Un préfixe défini dans Configurer se place après `saj_` dans l'ID de chaque entité de Onduleur et solaire, par exemple `sensor.saj_house_ethernet_protocol_version` avec le préfixe `house`.

| Nom | ID d'entité | Type | Unité | Modèles | Équipement et nombres | Activée par défaut |
| --- | --- | --- | --- | --- | --- | --- |
| Version du protocole Ethernet | `sensor.saj_ethernet_protocol_version` | Capteur | - | HS3 | - | Non |
| Adresse MAC Ethernet | `sensor.saj_ethernet_mac_address` | Capteur | - | HS3 | - | Non |
| Mode Ethernet | `sensor.saj_ethernet_mode` | Capteur | - | HS3 | - | Non |
| Adresse IP Ethernet | `sensor.saj_ethernet_ip_address` | Capteur | - | HS3 | - | Non |
| Masque de sous-réseau Ethernet | `sensor.saj_ethernet_subnet_mask` | Capteur | - | HS3 | - | Non |
| Passerelle Ethernet | `sensor.saj_ethernet_gateway` | Capteur | - | HS3 | - | Non |
| DNS principal Ethernet | `sensor.saj_ethernet_dns_primary` | Capteur | - | HS3 | - | Non |
| DNS secondaire Ethernet | `sensor.saj_ethernet_dns_secondary` | Capteur | - | HS3 | - | Non |
| Séquence des réglages | `sensor.saj_settings_sequence` | Capteur | - | HS3, H2 | - | Non |
| Version du protocole des réglages | `sensor.saj_settings_protocol_version` | Capteur | - | HS3 | - | Non |
| Configuration du compteur | `sensor.saj_meter_configuration` | Capteur | - | HS3, H2 | - | Non |
| Adresse du compteur | `sensor.saj_meter_address` | Capteur | - | HS3, H2 | - | Non |
| Adresse RS485 | `sensor.saj_rs485_address` | Capteur | - | HS3, H2 | - | Non |
| Débit en bauds RS485 | `sensor.saj_rs485_baud_rate` | Capteur | - | HS3, H2 | - | Non |
| Protocole de batterie | `sensor.saj_battery_protocol` | Capteur | - | HS3, H2 | - | Non |
| Adresse esclave RS485 | `sensor.saj_rs485_slave_address` | Capteur | - | HS3 | - | Non |
| Débit en bauds esclave RS485 | `sensor.saj_rs485_slave_baud_rate` | Capteur | - | HS3 | - | Non |
| Horloge de l'onduleur | `sensor.saj_inverter_clock` | Capteur | - | HS3, H2 | - | Non |
| Mode de fonctionnement | `sensor.saj_operating_mode` | Capteur | - | HS3, H2 | - | Oui |
| Température de l'onduleur | `sensor.saj_inverter_temperature` | Capteur | °C | HS3, H2 | - | Oui |
| Température ambiante | `sensor.saj_ambient_temperature` | Capteur | °C | HS3, H2 | - | Non |
| Courant de fuite | `sensor.saj_leakage_current` | Capteur | mA | HS3, H2 | - | Non |
| Résistance d'isolement PV1 | `sensor.saj_pv1_insulation_resistance` | Capteur | kΩ | HS3, H2 | - | Non |
| Résistance d'isolement PV2 | `sensor.saj_pv2_insulation_resistance` | Capteur | kΩ | HS3, H2 | Chaîne solaire 2 et suivantes | Non |
| Consigne de puissance de décharge de l'onduleur | `sensor.saj_inverter_discharge_power_setpoint` | Capteur | W | HS3, H2 | - | Non |
| Consigne de puissance de charge de l'onduleur | `sensor.saj_inverter_charge_power_setpoint` | Capteur | W | HS3, H2 | - | Non |
| Protocole de batterie (en vigueur) | `sensor.saj_battery_protocol_active` | Capteur | - | HS3, H2 | - | Non |
| Configuration du compteur (en vigueur) | `sensor.saj_meter_configuration_active` | Capteur | - | HS3, H2 | - | Non |
| Tension onduleur L1 | `sensor.saj_inverter_l1_voltage` | Capteur | V | HS3, H2 | - | Non |
| Courant onduleur L1 | `sensor.saj_inverter_l1_current` | Capteur | A | HS3, H2 | - | Non |
| Fréquence onduleur L1 | `sensor.saj_inverter_l1_frequency` | Capteur | Hz | HS3, H2 | - | Non |
| Puissance onduleur L1 | `sensor.saj_inverter_l1_power` | Capteur | W | HS3, H2 | - | Non |
| Puissance apparente onduleur L1 | `sensor.saj_inverter_l1_apparent_power` | Capteur | VA | HS3, H2 | - | Non |
| Tension onduleur L2 | `sensor.saj_inverter_l2_voltage` | Capteur | V | HS3, H2 | Phase 2 et suivantes | Non |
| Courant onduleur L2 | `sensor.saj_inverter_l2_current` | Capteur | A | HS3, H2 | Phase 2 et suivantes | Non |
| Fréquence onduleur L2 | `sensor.saj_inverter_l2_frequency` | Capteur | Hz | HS3, H2 | Phase 2 et suivantes | Non |
| Puissance onduleur L2 | `sensor.saj_inverter_l2_power` | Capteur | W | HS3, H2 | Phase 2 et suivantes | Non |
| Puissance apparente onduleur L2 | `sensor.saj_inverter_l2_apparent_power` | Capteur | VA | HS3, H2 | Phase 2 et suivantes | Non |
| Tension onduleur L3 | `sensor.saj_inverter_l3_voltage` | Capteur | V | HS3, H2 | Phase 3 et suivantes | Non |
| Courant onduleur L3 | `sensor.saj_inverter_l3_current` | Capteur | A | HS3, H2 | Phase 3 et suivantes | Non |
| Fréquence onduleur L3 | `sensor.saj_inverter_l3_frequency` | Capteur | Hz | HS3, H2 | Phase 3 et suivantes | Non |
| Puissance onduleur L3 | `sensor.saj_inverter_l3_power` | Capteur | W | HS3, H2 | Phase 3 et suivantes | Non |
| Puissance apparente onduleur L3 | `sensor.saj_inverter_l3_apparent_power` | Capteur | VA | HS3, H2 | Phase 3 et suivantes | Non |
| Tension secours L1 | `sensor.saj_backup_l1_voltage` | Capteur | V | HS3, H2 | - | Non |
| Courant secours L1 | `sensor.saj_backup_l1_current` | Capteur | A | HS3, H2 | - | Non |
| Fréquence secours L1 | `sensor.saj_backup_l1_frequency` | Capteur | Hz | HS3, H2 | - | Non |
| Tension continue secours L1 | `sensor.saj_backup_l1_dc_voltage` | Capteur | mV | HS3, H2 | - | Non |
| Puissance secours L1 | `sensor.saj_backup_l1_power` | Capteur | W | HS3, H2 | - | Non |
| Puissance apparente secours L1 | `sensor.saj_backup_l1_apparent_power` | Capteur | VA | HS3, H2 | - | Non |
| Tension secours L2 | `sensor.saj_backup_l2_voltage` | Capteur | V | HS3, H2 | Phase 2 et suivantes | Non |
| Courant secours L2 | `sensor.saj_backup_l2_current` | Capteur | A | HS3, H2 | Phase 2 et suivantes | Non |
| Fréquence secours L2 | `sensor.saj_backup_l2_frequency` | Capteur | Hz | HS3, H2 | Phase 2 et suivantes | Non |
| Tension continue secours L2 | `sensor.saj_backup_l2_dc_voltage` | Capteur | mV | HS3, H2 | Phase 2 et suivantes | Non |
| Puissance secours L2 | `sensor.saj_backup_l2_power` | Capteur | W | HS3, H2 | Phase 2 et suivantes | Non |
| Puissance apparente secours L2 | `sensor.saj_backup_l2_apparent_power` | Capteur | VA | HS3, H2 | Phase 2 et suivantes | Non |
| Tension secours L3 | `sensor.saj_backup_l3_voltage` | Capteur | V | HS3, H2 | Phase 3 et suivantes | Non |
| Courant secours L3 | `sensor.saj_backup_l3_current` | Capteur | A | HS3, H2 | Phase 3 et suivantes | Non |
| Fréquence secours L3 | `sensor.saj_backup_l3_frequency` | Capteur | Hz | HS3, H2 | Phase 3 et suivantes | Non |
| Tension continue secours L3 | `sensor.saj_backup_l3_dc_voltage` | Capteur | mV | HS3, H2 | Phase 3 et suivantes | Non |
| Puissance secours L3 | `sensor.saj_backup_l3_power` | Capteur | W | HS3, H2 | Phase 3 et suivantes | Non |
| Puissance apparente secours L3 | `sensor.saj_backup_l3_apparent_power` | Capteur | VA | HS3, H2 | Phase 3 et suivantes | Non |
| Tension du bus continu | `sensor.saj_dc_bus_voltage` | Capteur | V | HS3, H2 | - | Non |
| Tension du bus continu esclave | `sensor.saj_dc_bus_slave_voltage` | Capteur | V | HS3, H2 | - | Non |
| Tension PV1 | `sensor.saj_pv1_voltage` | Capteur | V | HS3, H2 | - | Oui |
| Courant PV1 | `sensor.saj_pv1_current` | Capteur | A | HS3, H2 | - | Oui |
| Puissance PV1 | `sensor.saj_pv1_power` | Capteur | W | HS3, H2 | - | Oui |
| Tension PV2 | `sensor.saj_pv2_voltage` | Capteur | V | HS3, H2 | Chaîne solaire 2 et suivantes | Oui |
| Courant PV2 | `sensor.saj_pv2_current` | Capteur | A | HS3, H2 | Chaîne solaire 2 et suivantes | Oui |
| Puissance PV2 | `sensor.saj_pv2_power` | Capteur | W | HS3, H2 | Chaîne solaire 2 et suivantes | Oui |
| Puissance solaire | `sensor.saj_pv_power` | Capteur | W | HS3, H2 | - | Oui |
| Puissance de l'onduleur | `sensor.saj_inverter_power` | Capteur | W | HS3, H2 | - | Oui |
| Énergie solaire du jour | `sensor.saj_pv_energy_today` | Capteur | kWh | HS3, H2 | - | Oui |
| Énergie solaire du mois | `sensor.saj_pv_energy_month` | Capteur | kWh | HS3, H2 | - | Non |
| Énergie solaire de l'année | `sensor.saj_pv_energy_year` | Capteur | kWh | HS3, H2 | - | Non |
| Énergie solaire totale | `sensor.saj_pv_energy_total` | Capteur | kWh | HS3, H2 | - | Oui |
| Énergie de la charge domestique du jour | `sensor.saj_load_energy_today` | Capteur | kWh | HS3, H2 | - | Oui |
| Énergie de la charge domestique du mois | `sensor.saj_load_energy_month` | Capteur | kWh | HS3, H2 | - | Non |
| Énergie de la charge domestique de l'année | `sensor.saj_load_energy_year` | Capteur | kWh | HS3, H2 | - | Non |
| Énergie de la charge domestique totale | `sensor.saj_load_energy_total` | Capteur | kWh | HS3, H2 | - | Oui |
| Énergie du circuit de secours du jour | `sensor.saj_backup_load_energy_today` | Capteur | kWh | HS3, H2 | - | Oui |
| Énergie du circuit de secours du mois | `sensor.saj_backup_load_energy_month` | Capteur | kWh | HS3, H2 | - | Non |
| Énergie du circuit de secours de l'année | `sensor.saj_backup_load_energy_year` | Capteur | kWh | HS3, H2 | - | Non |
| Énergie du circuit de secours totale | `sensor.saj_backup_load_energy_total` | Capteur | kWh | HS3, H2 | - | Oui |
| Mode parallèle | `sensor.saj_parallel_mode` | Capteur | - | HS3, H2 | - | Non |
| Machines en parallèle en ligne | `sensor.saj_parallel_online_count` | Capteur | - | HS3, H2 | - | Non |
| Puissance du réseau (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_power` | Capteur | W | HS3 | - | Non |
| Puissance réseau L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_l1_power` | Capteur | W | HS3 | - | Non |
| Tension réseau L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_l1_voltage` | Capteur | V | HS3 | - | Non |
| Courant réseau L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_l1_current` | Capteur | A | HS3 | - | Non |
| Fréquence réseau L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_l1_frequency` | Capteur | Hz | HS3 | - | Non |
| Puissance réseau L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_l2_power` | Capteur | W | HS3 | Phase 2 et suivantes | Non |
| Tension réseau L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_l2_voltage` | Capteur | V | HS3 | Phase 2 et suivantes | Non |
| Courant réseau L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_l2_current` | Capteur | A | HS3 | Phase 2 et suivantes | Non |
| Fréquence réseau L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_l2_frequency` | Capteur | Hz | HS3 | Phase 2 et suivantes | Non |
| Puissance réseau L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_l3_power` | Capteur | W | HS3 | Phase 3 et suivantes | Non |
| Tension réseau L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_l3_voltage` | Capteur | V | HS3 | Phase 3 et suivantes | Non |
| Courant réseau L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_l3_current` | Capteur | A | HS3 | Phase 3 et suivantes | Non |
| Fréquence réseau L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_l3_frequency` | Capteur | Hz | HS3 | Phase 3 et suivantes | Non |
| Puissance de l'onduleur (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_inverter_power` | Capteur | W | HS3 | - | Non |
| Puissance onduleur L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_inverter_l1_power` | Capteur | W | HS3 | - | Non |
| Tension onduleur L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_inverter_l1_voltage` | Capteur | V | HS3 | - | Non |
| Courant onduleur L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_inverter_l1_current` | Capteur | A | HS3 | - | Non |
| Fréquence onduleur L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_inverter_l1_frequency` | Capteur | Hz | HS3 | - | Non |
| Puissance onduleur L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_inverter_l2_power` | Capteur | W | HS3 | Phase 2 et suivantes | Non |
| Tension onduleur L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_inverter_l2_voltage` | Capteur | V | HS3 | Phase 2 et suivantes | Non |
| Courant onduleur L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_inverter_l2_current` | Capteur | A | HS3 | Phase 2 et suivantes | Non |
| Fréquence onduleur L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_inverter_l2_frequency` | Capteur | Hz | HS3 | Phase 2 et suivantes | Non |
| Puissance onduleur L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_inverter_l3_power` | Capteur | W | HS3 | Phase 3 et suivantes | Non |
| Tension onduleur L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_inverter_l3_voltage` | Capteur | V | HS3 | Phase 3 et suivantes | Non |
| Courant onduleur L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_inverter_l3_current` | Capteur | A | HS3 | Phase 3 et suivantes | Non |
| Fréquence onduleur L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_inverter_l3_frequency` | Capteur | Hz | HS3 | Phase 3 et suivantes | Non |
| Puissance de la charge domestique (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_load_power` | Capteur | W | HS3 | - | Non |
| Puissance charge domestique L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_load_l1_power` | Capteur | W | HS3 | - | Non |
| Tension charge domestique L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_load_l1_voltage` | Capteur | V | HS3 | - | Non |
| Courant charge domestique L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_load_l1_current` | Capteur | A | HS3 | - | Non |
| Fréquence charge domestique L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_load_l1_frequency` | Capteur | Hz | HS3 | - | Non |
| Puissance charge domestique L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_load_l2_power` | Capteur | W | HS3 | Phase 2 et suivantes | Non |
| Tension charge domestique L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_load_l2_voltage` | Capteur | V | HS3 | Phase 2 et suivantes | Non |
| Courant charge domestique L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_load_l2_current` | Capteur | A | HS3 | Phase 2 et suivantes | Non |
| Fréquence charge domestique L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_load_l2_frequency` | Capteur | Hz | HS3 | Phase 2 et suivantes | Non |
| Puissance charge domestique L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_load_l3_power` | Capteur | W | HS3 | Phase 3 et suivantes | Non |
| Tension charge domestique L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_load_l3_voltage` | Capteur | V | HS3 | Phase 3 et suivantes | Non |
| Courant charge domestique L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_load_l3_current` | Capteur | A | HS3 | Phase 3 et suivantes | Non |
| Fréquence charge domestique L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_load_l3_frequency` | Capteur | Hz | HS3 | Phase 3 et suivantes | Non |
| Puissance de la charge du réseau (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_load_power` | Capteur | W | HS3 | - | Non |
| Puissance charge du réseau L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_load_l1_power` | Capteur | W | HS3 | - | Non |
| Tension charge du réseau L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_load_l1_voltage` | Capteur | V | HS3 | - | Non |
| Courant charge du réseau L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_load_l1_current` | Capteur | A | HS3 | - | Non |
| Fréquence charge du réseau L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_load_l1_frequency` | Capteur | Hz | HS3 | - | Non |
| Puissance charge du réseau L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_load_l2_power` | Capteur | W | HS3 | Phase 2 et suivantes | Non |
| Tension charge du réseau L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_load_l2_voltage` | Capteur | V | HS3 | Phase 2 et suivantes | Non |
| Courant charge du réseau L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_load_l2_current` | Capteur | A | HS3 | Phase 2 et suivantes | Non |
| Fréquence charge du réseau L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_load_l2_frequency` | Capteur | Hz | HS3 | Phase 2 et suivantes | Non |
| Puissance charge du réseau L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_load_l3_power` | Capteur | W | HS3 | Phase 3 et suivantes | Non |
| Tension charge du réseau L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_load_l3_voltage` | Capteur | V | HS3 | Phase 3 et suivantes | Non |
| Courant charge du réseau L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_load_l3_current` | Capteur | A | HS3 | Phase 3 et suivantes | Non |
| Fréquence charge du réseau L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_grid_load_l3_frequency` | Capteur | Hz | HS3 | Phase 3 et suivantes | Non |
| Puissance du circuit de secours (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_backup_power` | Capteur | W | HS3 | - | Non |
| Puissance secours L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_backup_l1_power` | Capteur | W | HS3 | - | Non |
| Tension secours L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_backup_l1_voltage` | Capteur | V | HS3 | - | Non |
| Courant secours L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_backup_l1_current` | Capteur | A | HS3 | - | Non |
| Fréquence secours L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_backup_l1_frequency` | Capteur | Hz | HS3 | - | Non |
| Puissance secours L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_backup_l2_power` | Capteur | W | HS3 | Phase 2 et suivantes | Non |
| Tension secours L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_backup_l2_voltage` | Capteur | V | HS3 | Phase 2 et suivantes | Non |
| Courant secours L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_backup_l2_current` | Capteur | A | HS3 | Phase 2 et suivantes | Non |
| Fréquence secours L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_backup_l2_frequency` | Capteur | Hz | HS3 | Phase 2 et suivantes | Non |
| Puissance secours L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_backup_l3_power` | Capteur | W | HS3 | Phase 3 et suivantes | Non |
| Tension secours L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_backup_l3_voltage` | Capteur | V | HS3 | Phase 3 et suivantes | Non |
| Courant secours L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_backup_l3_current` | Capteur | A | HS3 | Phase 3 et suivantes | Non |
| Fréquence secours L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_backup_l3_frequency` | Capteur | Hz | HS3 | Phase 3 et suivantes | Non |
| Puissance solaire (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_pv_power` | Capteur | W | HS3 | - | Non |
| Tension PV1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_pv1_voltage` | Capteur | V | HS3 | - | Non |
| Courant PV1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_pv1_current` | Capteur | A | HS3 | - | Non |
| Puissance PV1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_pv1_power` | Capteur | W | HS3 | - | Non |
| Tension PV2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_pv2_voltage` | Capteur | V | HS3 | Chaîne solaire 2 et suivantes | Non |
| Courant PV2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_pv2_current` | Capteur | A | HS3 | Chaîne solaire 2 et suivantes | Non |
| Puissance PV2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_pv2_power` | Capteur | W | HS3 | Chaîne solaire 2 et suivantes | Non |
| Puissance du générateur (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_generator_power` | Capteur | W | HS3 | - | Non |
| Puissance générateur L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_generator_l1_power` | Capteur | W | HS3 | - | Non |
| Tension générateur L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_generator_l1_voltage` | Capteur | V | HS3 | - | Non |
| Courant générateur L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_generator_l1_current` | Capteur | A | HS3 | - | Non |
| Fréquence générateur L1 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_generator_l1_frequency` | Capteur | Hz | HS3 | - | Non |
| Puissance générateur L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_generator_l2_power` | Capteur | W | HS3 | Phase 2 et suivantes | Non |
| Tension générateur L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_generator_l2_voltage` | Capteur | V | HS3 | Phase 2 et suivantes | Non |
| Courant générateur L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_generator_l2_current` | Capteur | A | HS3 | Phase 2 et suivantes | Non |
| Fréquence générateur L2 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_generator_l2_frequency` | Capteur | Hz | HS3 | Phase 2 et suivantes | Non |
| Puissance générateur L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_generator_l3_power` | Capteur | W | HS3 | Phase 3 et suivantes | Non |
| Tension générateur L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_generator_l3_voltage` | Capteur | V | HS3 | Phase 3 et suivantes | Non |
| Courant générateur L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_generator_l3_current` | Capteur | A | HS3 | Phase 3 et suivantes | Non |
| Fréquence générateur L3 (moyenne sur 5 minutes) | `sensor.saj_five_minute_average_generator_l3_frequency` | Capteur | Hz | HS3 | Phase 3 et suivantes | Non |
| Code produit | `sensor.saj_product_code` | Capteur | - | HS3, H2 | - | Non |
| Version logicielle de l'écran | `sensor.saj_display_software_version` | Capteur | - | HS3, H2 | - | Non |
| Version logicielle maître | `sensor.saj_master_software_version` | Capteur | - | HS3, H2 | - | Non |
| Version logicielle esclave | `sensor.saj_slave_software_version` | Capteur | - | HS3, H2 | - | Non |
| Version matérielle de l'écran | `sensor.saj_display_hardware_version` | Capteur | - | HS3, H2 | - | Non |
| Version matérielle de la commande | `sensor.saj_control_hardware_version` | Capteur | - | HS3, H2 | - | Non |
| Version matérielle de la puissance | `sensor.saj_power_hardware_version` | Capteur | - | HS3, H2 | - | Non |
| Nombre de modules de batterie | `sensor.saj_battery_pack_count` | Capteur | - | HS3, H2 | - | Non |
| État du compteur A | `sensor.saj_meter_a_status` | Capteur | - | HS3, H2 | - | Non |
| État du compteur B | `sensor.saj_meter_b_status` | Capteur | - | HS3, H2 | - | Non |
| Puissance du circuit de secours | `sensor.saj_backup_load_power` | Capteur | W | HS3, H2 | - | Oui |
| Puissance de la charge domestique | `sensor.saj_load_power` | Capteur | W | HS3, H2 | - | Oui |
| Autoconsommation du jour | `sensor.saj_self_consumption_today` | Capteur | % | HS3, H2 | - | Non |
| Autosuffisance du jour | `sensor.saj_self_sufficiency_today` | Capteur | % | HS3, H2 | - | Non |
| Puissance du surplus solaire | `sensor.saj_solar_surplus_power` | Capteur | W | HS3, H2 | - | Non |
| Mode de flux inverse | `sensor.saj_reverse_flow_mode` | Capteur | - | H2 | - | Non |
| Hystérésis de fréquence FCAS | `sensor.saj_fcas_frequency_hysteresis` | Capteur | Hz | H2 | - | Non |
| Rôle en parallèle | `sensor.saj_parallel_role` | Capteur | - | H2 | - | Non |
| Numéro en parallèle | `sensor.saj_parallel_number` | Capteur | - | H2 | - | Non |
| Mode parallèle configuré | `sensor.saj_parallel_configured_mode` | Capteur | - | H2 | - | Non |
| Mode d'entrée de la batterie | `sensor.saj_battery_input_mode` | Capteur | - | H2 | - | Non |
| Mode d'entrée solaire | `sensor.saj_pv_input_mode` | Capteur | - | H2 | - | Non |
| Mode hors réseau | `sensor.saj_off_grid_mode` | Capteur | - | H2 | - | Non |
| Tension de sortie hors réseau | `sensor.saj_off_grid_output_voltage` | Capteur | V | H2 | - | Non |
| Fréquence de sortie hors réseau | `sensor.saj_off_grid_output_frequency` | Capteur | Hz | H2 | - | Non |
| Activation du moteur | `sensor.saj_motor_enable` | Capteur | - | H2 | - | Non |
| Modèle de la machine | `sensor.saj_machine_model` | Capteur | - | H2 | - | Non |
| Puissance nominale | `sensor.saj_rated_power` | Capteur | W | H2 | - | Non |
| Indicateurs de fonction 1 | `sensor.saj_function_flags_1` | Capteur | - | H2 | - | Non |
| Indicateurs de fonction 2 | `sensor.saj_function_flags_2` | Capteur | - | H2 | - | Non |
| Composante continue maximale du courant | `sensor.saj_max_dc_current_component` | Capteur | mA | H2 | - | Non |
| Composante continue maximale de la tension | `sensor.saj_max_dc_voltage_component` | Capteur | V | H2 | - | Non |
| Limite de résistance d'isolement | `sensor.saj_insulation_resistance_limit` | Capteur | kΩ | H2 | - | Non |
| Courant de fuite maximal | `sensor.saj_max_leakage_current` | Capteur | mA | H2 | - | Non |
| Arrêt de l'onduleur | `sensor.saj_inverter_stop` | Capteur | - | H2 | - | Non |
| Tension de démarrage solaire | `sensor.saj_pv_start_voltage` | Capteur | V | H2 | - | Non |
| Tension d'arrêt solaire | `sensor.saj_pv_shutdown_voltage` | Capteur | V | H2 | - | Non |
| Tension MPPT haute | `sensor.saj_mppt_voltage_high` | Capteur | V | H2 | - | Non |
| Tension MPPT basse | `sensor.saj_mppt_voltage_low` | Capteur | V | H2 | - | Non |
| Durée de balayage MPPT | `sensor.saj_mppt_scan_time` | Capteur | min | H2 | - | Non |
| Nombre d'erreurs de l'onduleur | `sensor.saj_inverter_error_count` | Capteur | - | H2 | - | Non |
| Résistance d'isolement PV3 | `sensor.saj_pv3_insulation_resistance` | Capteur | kΩ | H2 | Chaîne solaire 3 et suivantes | Non |
| Résistance d'isolement PV4 | `sensor.saj_pv4_insulation_resistance` | Capteur | kΩ | H2 | Chaîne solaire 4 et suivantes | Non |
| État matériel DRM | `sensor.saj_drm_hardware_status` | Capteur | - | H2 | - | Non |
| État logiciel DRM | `sensor.saj_drm_software_status` | Capteur | - | H2 | - | Non |
| Séquence d'enregistrement des défauts | `sensor.saj_fault_record_sequence` | Capteur | - | H2 | - | Non |
| Mode d'application (en vigueur) | `sensor.saj_application_mode_active` | Capteur | - | H2 | - | Non |
| Tension PV3 | `sensor.saj_pv3_voltage` | Capteur | V | H2 | Chaîne solaire 3 et suivantes | Oui |
| Courant PV3 | `sensor.saj_pv3_current` | Capteur | A | H2 | Chaîne solaire 3 et suivantes | Oui |
| Puissance PV3 | `sensor.saj_pv3_power` | Capteur | W | H2 | Chaîne solaire 3 et suivantes | Oui |
| Tension PV4 | `sensor.saj_pv4_voltage` | Capteur | V | H2 | Chaîne solaire 4 et suivantes | Oui |
| Courant PV4 | `sensor.saj_pv4_current` | Capteur | A | H2 | Chaîne solaire 4 et suivantes | Oui |
| Puissance PV4 | `sensor.saj_pv4_power` | Capteur | W | H2 | Chaîne solaire 4 et suivantes | Oui |
| Puissance du réseau (TC) | `sensor.saj_ct_grid_power` | Capteur | W | H2 | - | Non |
| Puissance apparente du réseau (TC) | `sensor.saj_ct_grid_apparent_power` | Capteur | VA | H2 | - | Non |
| Puissance solaire (TC) | `sensor.saj_ct_pv_power` | Capteur | W | H2 | - | Non |
| Puissance apparente solaire (TC) | `sensor.saj_ct_pv_apparent_power` | Capteur | VA | H2 | - | Non |
| Puissance apparente de l'onduleur | `sensor.saj_inverter_apparent_power` | Capteur | VA | H2 | - | Non |
| Puissance apparente du circuit de secours | `sensor.saj_backup_load_apparent_power` | Capteur | VA | H2 | - | Non |
| Durée de production solaire du jour | `sensor.saj_pv_generation_time_today` | Capteur | h | H2 | - | Non |
| Durée de production solaire totale | `sensor.saj_pv_generation_time_total` | Capteur | h | H2 | - | Non |
| Énergie de l'onduleur du jour | `sensor.saj_inverter_energy_today` | Capteur | kWh | H2 | - | Non |
| Énergie de l'onduleur du mois | `sensor.saj_inverter_energy_month` | Capteur | kWh | H2 | - | Non |
| Énergie de l'onduleur de l'année | `sensor.saj_inverter_energy_year` | Capteur | kWh | H2 | - | Non |
| Énergie de l'onduleur totale | `sensor.saj_inverter_energy_total` | Capteur | kWh | H2 | - | Non |
| Énergie PV2 du jour | `sensor.saj_pv2_energy_today` | Capteur | kWh | H2 | Chaîne solaire 2 et suivantes | Non |
| Énergie PV2 du mois | `sensor.saj_pv2_energy_month` | Capteur | kWh | H2 | Chaîne solaire 2 et suivantes | Non |
| Énergie PV2 de l'année | `sensor.saj_pv2_energy_year` | Capteur | kWh | H2 | Chaîne solaire 2 et suivantes | Non |
| Énergie PV2 totale | `sensor.saj_pv2_energy_total` | Capteur | kWh | H2 | Chaîne solaire 2 et suivantes | Non |
| Énergie PV3 du jour | `sensor.saj_pv3_energy_today` | Capteur | kWh | H2 | Chaîne solaire 3 et suivantes | Non |
| Énergie PV3 du mois | `sensor.saj_pv3_energy_month` | Capteur | kWh | H2 | Chaîne solaire 3 et suivantes | Non |
| Énergie PV3 de l'année | `sensor.saj_pv3_energy_year` | Capteur | kWh | H2 | Chaîne solaire 3 et suivantes | Non |
| Énergie PV3 totale | `sensor.saj_pv3_energy_total` | Capteur | kWh | H2 | Chaîne solaire 3 et suivantes | Non |
| Version du protocole d'identité | `sensor.saj_identity_protocol_version` | Capteur | - | H2 | - | Non |
