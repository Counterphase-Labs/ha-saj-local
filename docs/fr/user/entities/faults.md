[en](../../../en-gb/user/entities/faults.md) | [de](../../../de/user/entities/faults.md) | [nl](../../../nl/user/entities/faults.md) | fr | [zh](../../../zh-hans/user/entities/faults.md) | [es](../../../es/user/entities/faults.md) | [it](../../../it/user/entities/faults.md) | [pl](../../../pl/user/entities/faults.md) | [sv](../../../sv/user/entities/faults.md)

# Défauts

Défauts que l'onduleur, la batterie et le chargeur de VE signalent.

La liste des fonctionnalités de l'intégration explique les entités de Défauts dans [Défauts de l'équipement et réparations](../../../../custom_components/saj_local/docs/features.md#device-faults-and-repairs).

139 entités. Généré par `make docs`. Ne pas modifier à la main.

Un préfixe défini dans Configurer se place après `saj_` dans l'ID de chaque entité de Défauts, par exemple `binary_sensor.saj_house_battery_pack1_fault` avec le préfixe `house`.

| Nom | ID d'entité | Type | Unité | Modèles | Équipement et nombres | Activée par défaut |
| --- | --- | --- | --- | --- | --- | --- |
| Défaut du module de batterie 1 | `binary_sensor.saj_battery_pack1_fault` | Capteur binaire | - | HS3, H2 | Batterie | Oui |
| Avertissement du module de batterie 1 | `binary_sensor.saj_battery_pack1_warning` | Capteur binaire | - | HS3, H2 | Batterie | Oui |
| Défaut de la batterie | `binary_sensor.saj_battery_fault` | Capteur binaire | - | HS3, H2 | Batterie | Oui |
| Fabricant du BMS de la batterie incompatible | `binary_sensor.saj_battery_fault_bms_incompatible` | Capteur binaire | - | HS3 | Batterie | Oui |
| Disjoncteur de la batterie ouvert | `binary_sensor.saj_battery_fault_breaker_open` | Capteur binaire | - | HS3 | Batterie | Oui |
| Cellules de la batterie non concordantes | `binary_sensor.saj_battery_fault_cell_incompatible` | Capteur binaire | - | HS3 | Batterie | Oui |
| Surchauffe d'une cellule de la batterie | `binary_sensor.saj_battery_fault_cell_over_temperature` | Capteur binaire | - | HS3 | Batterie | Oui |
| Surtension d'une cellule de la batterie | `binary_sensor.saj_battery_fault_cell_overvoltage` | Capteur binaire | - | HS3 | Batterie | Oui |
| Fabricant des cellules de la batterie non concordant | `binary_sensor.saj_battery_fault_cell_supplier_incompatible` | Capteur binaire | - | HS3 | Batterie | Oui |
| Écart de température entre cellules de la batterie trop grand | `binary_sensor.saj_battery_fault_cell_temperature_difference` | Capteur binaire | - | HS3 | Batterie | Oui |
| Sous-tension d'une cellule de la batterie | `binary_sensor.saj_battery_fault_cell_undervoltage` | Capteur binaire | - | HS3 | Batterie | Oui |
| Écart de tension entre cellules de la batterie trop grand, niveau 1 | `binary_sensor.saj_battery_fault_cell_voltage_difference_1` | Capteur binaire | - | HS3 | Batterie | Oui |
| Écart de tension entre cellules de la batterie trop grand, niveau 2 | `binary_sensor.saj_battery_fault_cell_voltage_difference_2` | Capteur binaire | - | HS3 | Batterie | Oui |
| Batterie trop froide pour charger | `binary_sensor.saj_battery_fault_charge_cold` | Capteur binaire | - | HS3 | Batterie | Oui |
| Batterie trop chaude pour charger | `binary_sensor.saj_battery_fault_charge_hot` | Capteur binaire | - | HS3 | Batterie | Oui |
| Surintensité de charge de la batterie | `binary_sensor.saj_battery_fault_charge_overcurrent` | Capteur binaire | - | HS3 | Batterie | Oui |
| Surtension du port de charge de la batterie | `binary_sensor.saj_battery_fault_charging_port_overvoltage` | Capteur binaire | - | HS3 | Batterie | Oui |
| Batterie trop froide pour décharger | `binary_sensor.saj_battery_fault_discharge_cold` | Capteur binaire | - | HS3 | Batterie | Oui |
| Batterie trop chaude pour décharger | `binary_sensor.saj_battery_fault_discharge_hot` | Capteur binaire | - | HS3 | Batterie | Oui |
| Surintensité de décharge de la batterie | `binary_sensor.saj_battery_fault_discharge_overcurrent` | Capteur binaire | - | HS3 | Batterie | Oui |
| Défaut de fusible de la batterie | `binary_sensor.saj_battery_fault_fuse` | Capteur binaire | - | HS3 | Batterie | Oui |
| Défaut matériel du BMS de la batterie | `binary_sensor.saj_battery_fault_hardware` | Capteur binaire | - | HS3 | Batterie | Oui |
| Défaut d'isolement du BMS de la batterie | `binary_sensor.saj_battery_fault_insulation` | Capteur binaire | - | HS3 | Batterie | Oui |
| Communication interne du BMS de la batterie perdue | `binary_sensor.saj_battery_fault_internal_communication` | Capteur binaire | - | HS3 | Batterie | Oui |
| Défaut d'adressage des modules de batterie | `binary_sensor.saj_battery_fault_pack_sequence` | Capteur binaire | - | HS3 | Batterie | Oui |
| Défaut de précharge de la batterie | `binary_sensor.saj_battery_fault_precharge` | Capteur binaire | - | HS3 | Batterie | Oui |
| Défaut de relais du BMS de la batterie | `binary_sensor.saj_battery_fault_relay` | Capteur binaire | - | HS3 | Batterie | Oui |
| Court-circuit de la batterie | `binary_sensor.saj_battery_fault_short_circuit` | Capteur binaire | - | HS3 | Batterie | Oui |
| Système de batterie verrouillé | `binary_sensor.saj_battery_fault_system_locked` | Capteur binaire | - | HS3 | Batterie | Oui |
| Tension totale de la batterie trop haute | `binary_sensor.saj_battery_fault_total_overvoltage` | Capteur binaire | - | HS3 | Batterie | Oui |
| Tension totale de la batterie trop basse | `binary_sensor.saj_battery_fault_total_undervoltage` | Capteur binaire | - | HS3 | Batterie | Oui |
| Échec de la concordance de la tension totale de la batterie | `binary_sensor.saj_battery_fault_total_voltage_matching` | Capteur binaire | - | HS3 | Batterie | Oui |
| Défaut non reconnu de la batterie | `binary_sensor.saj_battery_fault_unrecognised` | Capteur binaire | - | HS3, H2 | Batterie | Oui |
| Niveaux de tension de la batterie non concordants | `binary_sensor.saj_battery_fault_voltage_level_mismatch` | Capteur binaire | - | HS3 | Batterie | Oui |
| Défaut du chargeur de VE | `binary_sensor.saj_ev_fault` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Surintensité alternative du chargeur de VE | `binary_sensor.saj_ev_fault_ac_overcurrent` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Surfréquence alternative du chargeur de VE | `binary_sensor.saj_ev_fault_ac_overfrequency` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Surtension alternative du chargeur de VE | `binary_sensor.saj_ev_fault_ac_overvoltage` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Courant résiduel alternatif du chargeur de VE | `binary_sensor.saj_ev_fault_ac_residual_current` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Sous-fréquence alternative du chargeur de VE | `binary_sensor.saj_ev_fault_ac_underfrequency` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Sous-tension alternative du chargeur de VE | `binary_sensor.saj_ev_fault_ac_undervoltage` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Défaut Bluetooth du chargeur de VE | `binary_sensor.saj_ev_fault_bluetooth` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Défaut de courant du connecteur du chargeur de VE | `binary_sensor.saj_ev_fault_connector_current` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Défaut du verrouillage du connecteur du chargeur de VE | `binary_sensor.saj_ev_fault_connector_lock` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Défaut du signal pilote du chargeur de VE (sous 2 V) | `binary_sensor.saj_ev_fault_control_pilot` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Défaut A de courant résiduel continu du chargeur de VE | `binary_sensor.saj_ev_fault_dc_residual_current_a` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Défaut B de courant résiduel continu du chargeur de VE | `binary_sensor.saj_ev_fault_dc_residual_current_b` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Défaut C de courant résiduel continu du chargeur de VE | `binary_sensor.saj_ev_fault_dc_residual_current_c` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Arrêt d'urgence du chargeur de VE | `binary_sensor.saj_ev_fault_emergency_stop` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Défaut de mise à la terre du chargeur de VE | `binary_sensor.saj_ev_fault_grounding` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Surchauffe de la borne d'entrée du chargeur de VE | `binary_sensor.saj_ev_fault_input_terminal_over_temperature` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Défaut du compteur du chargeur de VE | `binary_sensor.saj_ev_fault_meter` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Surcharge du chargeur de VE | `binary_sensor.saj_ev_fault_overload` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Défaut d'ordre des phases du chargeur de VE | `binary_sensor.saj_ev_fault_phase_sequence` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Défaut du circuit différentiel du chargeur de VE | `binary_sensor.saj_ev_fault_rcd_circuit` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Défaut de relais du chargeur de VE | `binary_sensor.saj_ev_fault_relay` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Surchauffe du relais du chargeur de VE | `binary_sensor.saj_ev_fault_relay_over_temperature` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Délai de communication RS485 du chargeur de VE dépassé | `binary_sensor.saj_ev_fault_rs485_timeout` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Défaut d'alimentation électrique du chargeur de VE | `binary_sensor.saj_ev_fault_supply` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Température trop basse du chargeur de VE | `binary_sensor.saj_ev_fault_under_temperature` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Défaut non reconnu du chargeur de VE | `binary_sensor.saj_ev_fault_unrecognised` | Capteur binaire | - | HS3 | Chargeur de VE | Oui |
| Défaut de l'onduleur | `binary_sensor.saj_inverter_fault` | Capteur binaire | - | HS3, H2 | - | Oui |
| Communication avec la carte de détection d'arc perdue | `binary_sensor.saj_inverter_fault_afci_communication` | Capteur binaire | - | HS3 | - | Oui |
| Défaut d'arc | `binary_sensor.saj_inverter_fault_arc` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut du dispositif de détection d'arc | `binary_sensor.saj_inverter_fault_arc_device` | Capteur binaire | - | HS3 | - | Oui |
| Autorisation expirée | `binary_sensor.saj_inverter_fault_authorisation_expired` | Capteur binaire | - | HS3, H2 | - | Oui |
| Tension de charge de la batterie trop haute | `binary_sensor.saj_inverter_fault_battery_charge_overvoltage` | Capteur binaire | - | HS3, H2 | - | Oui |
| Tension de décharge de la batterie trop basse | `binary_sensor.saj_inverter_fault_battery_discharge_undervoltage` | Capteur binaire | - | HS3, H2 | - | Oui |
| Circuit ouvert de la batterie | `binary_sensor.saj_inverter_fault_battery_open_circuit` | Capteur binaire | - | HS3, H2 | - | Oui |
| Surintensité du port batterie | `binary_sensor.saj_inverter_fault_battery_overcurrent` | Capteur binaire | - | HS3, H2 | - | Oui |
| Surcharge du port batterie | `binary_sensor.saj_inverter_fault_battery_overload` | Capteur binaire | - | HS3, H2 | - | Oui |
| Surtension du port batterie | `binary_sensor.saj_inverter_fault_battery_overvoltage` | Capteur binaire | - | HS3, H2 | - | Oui |
| Délai de démarrage progressif de la batterie dépassé | `binary_sensor.saj_inverter_fault_battery_soft_start` | Capteur binaire | - | HS3, H2 | - | Oui |
| Communication avec le BMS perdue | `binary_sensor.saj_inverter_fault_bms_communication` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut du dispositif BMS | `binary_sensor.saj_inverter_fault_bms_device` | Capteur binaire | - | HS3, H2 | - | Oui |
| Surtension matérielle du bus continu | `binary_sensor.saj_inverter_fault_bus_hardware_overvoltage` | Capteur binaire | - | HS3, H2 | - | Oui |
| Déséquilibre de tension du bus continu | `binary_sensor.saj_inverter_fault_bus_imbalance` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut de mémoire du contrôleur | `binary_sensor.saj_inverter_fault_controller_memory` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut du dispositif TC | `binary_sensor.saj_inverter_fault_ct_device` | Capteur binaire | - | HS3 | - | Oui |
| Défaut du capteur de courant | `binary_sensor.saj_inverter_fault_current_sensor` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut du capteur d'injection de courant continu | `binary_sensor.saj_inverter_fault_dc_injection_device` | Capteur binaire | - | HS3, H2 | - | Oui |
| Communication avec l'unité DC-DC perdue | `binary_sensor.saj_inverter_fault_dcdc_communication` | Capteur binaire | - | HS3 | - | Oui |
| Défaut de l'unité DC-DC | `binary_sensor.saj_inverter_fault_dcdc_device` | Capteur binaire | - | HS3 | - | Oui |
| Défaut d'horloge de la carte d'affichage | `binary_sensor.saj_inverter_fault_display_clock` | Capteur binaire | - | HS3, H2 | - | Oui |
| Communication avec la carte d'affichage perdue | `binary_sensor.saj_inverter_fault_display_communication` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut de mémoire de la carte d'affichage | `binary_sensor.saj_inverter_fault_display_memory` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut DRM0 | `binary_sensor.saj_inverter_fault_drm0` | Capteur binaire | - | HS3, H2 | - | Oui |
| Communication avec le chargeur de VE perdue | `binary_sensor.saj_inverter_fault_ev_charger_communication` | Capteur binaire | - | HS3 | - | Oui |
| Défaut du ventilateur 1 | `binary_sensor.saj_inverter_fault_fan_1` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut du ventilateur 2 | `binary_sensor.saj_inverter_fault_fan_2` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut du ventilateur 3 | `binary_sensor.saj_inverter_fault_fan_3` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut du ventilateur 4 | `binary_sensor.saj_inverter_fault_fan_4` | Capteur binaire | - | HS3, H2 | - | Oui |
| Surtension moyenne du réseau sur 10 minutes | `binary_sensor.saj_inverter_fault_grid_average_overvoltage` | Capteur binaire | - | HS3, H2 | - | Oui |
| Réseau perdu | `binary_sensor.saj_inverter_fault_grid_lost` | Capteur binaire | - | HS3, H2 | - | Oui |
| Surfréquence du réseau | `binary_sensor.saj_inverter_fault_grid_overfrequency` | Capteur binaire | - | HS3, H2 | - | Oui |
| Injection de courant continu de la phase R du réseau trop élevée | `binary_sensor.saj_inverter_fault_grid_phase_r_dc_injection` | Capteur binaire | - | HS3, H2 | - | Oui |
| Tension continue de la phase R du réseau trop haute | `binary_sensor.saj_inverter_fault_grid_phase_r_dc_voltage` | Capteur binaire | - | HS3, H2 | - | Oui |
| Surtension de la phase R du réseau | `binary_sensor.saj_inverter_fault_grid_phase_r_overvoltage` | Capteur binaire | - | HS3, H2 | - | Oui |
| Sous-tension de la phase R du réseau | `binary_sensor.saj_inverter_fault_grid_phase_r_undervoltage` | Capteur binaire | - | HS3, H2 | - | Oui |
| Injection de courant continu de la phase S du réseau trop élevée | `binary_sensor.saj_inverter_fault_grid_phase_s_dc_injection` | Capteur binaire | - | HS3, H2 | - | Oui |
| Tension continue de la phase S du réseau trop haute | `binary_sensor.saj_inverter_fault_grid_phase_s_dc_voltage` | Capteur binaire | - | HS3, H2 | - | Oui |
| Surtension de la phase S du réseau | `binary_sensor.saj_inverter_fault_grid_phase_s_overvoltage` | Capteur binaire | - | HS3, H2 | - | Oui |
| Sous-tension de la phase S du réseau | `binary_sensor.saj_inverter_fault_grid_phase_s_undervoltage` | Capteur binaire | - | HS3, H2 | - | Oui |
| Injection de courant continu de la phase T du réseau trop élevée | `binary_sensor.saj_inverter_fault_grid_phase_t_dc_injection` | Capteur binaire | - | HS3, H2 | - | Oui |
| Tension continue de la phase T du réseau trop haute | `binary_sensor.saj_inverter_fault_grid_phase_t_dc_voltage` | Capteur binaire | - | HS3, H2 | - | Oui |
| Surtension de la phase T du réseau | `binary_sensor.saj_inverter_fault_grid_phase_t_overvoltage` | Capteur binaire | - | HS3, H2 | - | Oui |
| Sous-tension de la phase T du réseau | `binary_sensor.saj_inverter_fault_grid_phase_t_undervoltage` | Capteur binaire | - | HS3, H2 | - | Oui |
| Sous-fréquence du réseau | `binary_sensor.saj_inverter_fault_grid_underfrequency` | Capteur binaire | - | HS3, H2 | - | Oui |
| Surintensité matérielle de l'onduleur | `binary_sensor.saj_inverter_fault_hardware_overcurrent` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut d'isolement | `binary_sensor.saj_inverter_fault_insulation` | Capteur binaire | - | HS3, H2 | - | Oui |
| Communication interne perdue | `binary_sensor.saj_inverter_fault_internal_communication` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut de courant de fuite | `binary_sensor.saj_inverter_fault_leakage_current` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut du capteur de courant de fuite | `binary_sensor.saj_inverter_fault_leakage_current_device` | Capteur binaire | - | HS3, H2 | - | Oui |
| Communication avec le compteur perdue | `binary_sensor.saj_inverter_fault_meter_communication` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut de tension neutre-terre | `binary_sensor.saj_inverter_fault_neutral_earth_voltage` | Capteur binaire | - | HS3, H2 | - | Oui |
| Sous-tension de la sortie hors réseau | `binary_sensor.saj_inverter_fault_off_grid_undervoltage` | Capteur binaire | - | HS3, H2 | - | Oui |
| Surcharge de la sortie | `binary_sensor.saj_inverter_fault_output_overload` | Capteur binaire | - | HS3, H2 | - | Oui |
| Surchauffe | `binary_sensor.saj_inverter_fault_over_temperature` | Capteur binaire | - | HS3, H2 | - | Oui |
| Communication du système en parallèle perdue | `binary_sensor.saj_inverter_fault_parallel_communication` | Capteur binaire | - | HS3 | - | Oui |
| Surintensité matérielle solaire | `binary_sensor.saj_inverter_fault_pv_hardware_overcurrent` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut de l'entrée solaire | `binary_sensor.saj_inverter_fault_pv_input` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut du mode d'entrée solaire | `binary_sensor.saj_inverter_fault_pv_input_mode` | Capteur binaire | - | HS3, H2 | - | Oui |
| Communication avec le compteur solaire perdue | `binary_sensor.saj_inverter_fault_pv_meter_communication` | Capteur binaire | - | HS3 | - | Oui |
| Surtension solaire | `binary_sensor.saj_inverter_fault_pv_overvoltage` | Capteur binaire | - | HS3, H2 | - | Oui |
| Surintensité logicielle solaire | `binary_sensor.saj_inverter_fault_pv_software_overcurrent` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut de relais | `binary_sensor.saj_inverter_fault_relay` | Capteur binaire | - | HS3, H2 | - | Oui |
| Communication avec le contrôleur esclave perdue | `binary_sensor.saj_inverter_fault_slave_communication` | Capteur binaire | - | HS3 | - | Oui |
| Température trop basse | `binary_sensor.saj_inverter_fault_under_temperature` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut non reconnu de l'onduleur | `binary_sensor.saj_inverter_fault_unrecognised` | Capteur binaire | - | HS3, H2 | - | Oui |
| Défaut du module de batterie 2 | `binary_sensor.saj_battery_pack2_fault` | Capteur binaire | - | H2 | Batterie; Module de batterie 2 et suivants | Oui |
| Avertissement du module de batterie 2 | `binary_sensor.saj_battery_pack2_warning` | Capteur binaire | - | H2 | Batterie; Module de batterie 2 et suivants | Oui |
| Défaut du module de batterie 3 | `binary_sensor.saj_battery_pack3_fault` | Capteur binaire | - | H2 | Batterie; Module de batterie 3 et suivants | Oui |
| Avertissement du module de batterie 3 | `binary_sensor.saj_battery_pack3_warning` | Capteur binaire | - | H2 | Batterie; Module de batterie 3 et suivants | Oui |
| Défaut du module de batterie 4 | `binary_sensor.saj_battery_pack4_fault` | Capteur binaire | - | H2 | Batterie; Module de batterie 4 et suivants | Oui |
| Avertissement du module de batterie 4 | `binary_sensor.saj_battery_pack4_warning` | Capteur binaire | - | H2 | Batterie; Module de batterie 4 et suivants | Oui |
| Surtension du bus continu | `binary_sensor.saj_inverter_fault_bus_overvoltage` | Capteur binaire | - | H2 | - | Oui |
| Sous-tension du bus continu | `binary_sensor.saj_inverter_fault_bus_undervoltage` | Capteur binaire | - | H2 | - | Oui |
| Défaut de phase du réseau | `binary_sensor.saj_inverter_fault_grid_phase` | Capteur binaire | - | H2 | - | Oui |
| Îlotage | `binary_sensor.saj_inverter_fault_islanding` | Capteur binaire | - | H2 | - | Oui |
