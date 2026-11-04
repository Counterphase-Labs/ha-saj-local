[en](../../../en-gb/user/entities/grid-and-meter-a.md) | [de](../../../de/user/entities/grid-and-meter-a.md) | [nl](../../../nl/user/entities/grid-and-meter-a.md) | fr | [zh](../../../zh-hans/user/entities/grid-and-meter-a.md) | [es](../../../es/user/entities/grid-and-meter-a.md) | [it](../../../it/user/entities/grid-and-meter-a.md) | [pl](../../../pl/user/entities/grid-and-meter-a.md) | [sv](../../../sv/user/entities/grid-and-meter-a.md)

# Réseau et compteur A

Le raccordement au réseau et le compteur A, le compteur du réseau.

La liste des fonctionnalités de l'intégration explique les entités de Réseau et compteur A dans [Appareils et entités](../../../../custom_components/saj_local/docs/features.md#devices-and-entities) et [Équipement optionnel](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

101 entités. Généré par `make docs`. Ne pas modifier à la main.

Un préfixe défini dans Configurer se place après `saj_` dans l'ID de chaque entité de Réseau et compteur A, par exemple `sensor.saj_house_grid_connection_countdown` avec le préfixe `house`.

| Nom | ID d'entité | Type | Unité | Modèles | Équipement et nombres | Activée par défaut |
| --- | --- | --- | --- | --- | --- | --- |
| Compte à rebours de raccordement au réseau | `sensor.saj_grid_connection_countdown` | Capteur | s | HS3, H2 | - | Non |
| Tension réseau L1 | `sensor.saj_grid_l1_voltage` | Capteur | V | HS3, H2 | - | Oui |
| Fréquence réseau L1 | `sensor.saj_grid_l1_frequency` | Capteur | Hz | HS3, H2 | - | Oui |
| Courant continu réseau L1 | `sensor.saj_grid_l1_dc_current` | Capteur | mA | HS3, H2 | - | Non |
| Tension réseau L2 | `sensor.saj_grid_l2_voltage` | Capteur | V | HS3, H2 | Phase 2 et suivantes | Oui |
| Fréquence réseau L2 | `sensor.saj_grid_l2_frequency` | Capteur | Hz | HS3, H2 | Phase 2 et suivantes | Non |
| Courant continu réseau L2 | `sensor.saj_grid_l2_dc_current` | Capteur | mA | HS3, H2 | Phase 2 et suivantes | Non |
| Tension réseau L3 | `sensor.saj_grid_l3_voltage` | Capteur | V | HS3, H2 | Phase 3 et suivantes | Oui |
| Fréquence réseau L3 | `sensor.saj_grid_l3_frequency` | Capteur | Hz | HS3, H2 | Phase 3 et suivantes | Non |
| Courant continu réseau L3 | `sensor.saj_grid_l3_dc_current` | Capteur | mA | HS3, H2 | Phase 3 et suivantes | Non |
| Tension de sortie réseau L1 | `sensor.saj_grid_output_l1_voltage` | Capteur | V | HS3, H2 | - | Non |
| Courant de sortie réseau L1 | `sensor.saj_grid_output_l1_current` | Capteur | A | HS3, H2 | - | Non |
| Fréquence de sortie réseau L1 | `sensor.saj_grid_output_l1_frequency` | Capteur | Hz | HS3, H2 | - | Non |
| Puissance de sortie réseau L1 | `sensor.saj_grid_output_l1_power` | Capteur | W | HS3, H2 | - | Non |
| Tension de sortie réseau L2 | `sensor.saj_grid_output_l2_voltage` | Capteur | V | HS3, H2 | Phase 2 et suivantes | Non |
| Puissance de sortie réseau L2 | `sensor.saj_grid_output_l2_power` | Capteur | W | HS3, H2 | Phase 2 et suivantes | Non |
| Tension de sortie réseau L3 | `sensor.saj_grid_output_l3_voltage` | Capteur | V | HS3, H2 | Phase 3 et suivantes | Non |
| Puissance de sortie réseau L3 | `sensor.saj_grid_output_l3_power` | Capteur | W | HS3, H2 | Phase 3 et suivantes | Non |
| Puissance de la charge du réseau | `sensor.saj_grid_load_power` | Capteur | W | HS3, H2 | - | Non |
| Énergie injectée réseau L1 du jour | `sensor.saj_grid_l1_export_energy_today` | Capteur | kWh | HS3, H2 | - | Non |
| Énergie injectée réseau L1 du mois | `sensor.saj_grid_l1_export_energy_month` | Capteur | kWh | HS3, H2 | - | Non |
| Énergie injectée réseau L1 de l'année | `sensor.saj_grid_l1_export_energy_year` | Capteur | kWh | HS3, H2 | - | Non |
| Énergie injectée réseau L1 totale | `sensor.saj_grid_l1_export_energy_total` | Capteur | kWh | HS3, H2 | - | Non |
| Énergie soutirée réseau L1 du jour | `sensor.saj_grid_l1_import_energy_today` | Capteur | kWh | HS3, H2 | - | Non |
| Énergie soutirée réseau L1 du mois | `sensor.saj_grid_l1_import_energy_month` | Capteur | kWh | HS3, H2 | - | Non |
| Énergie soutirée réseau L1 de l'année | `sensor.saj_grid_l1_import_energy_year` | Capteur | kWh | HS3, H2 | - | Non |
| Énergie soutirée réseau L1 totale | `sensor.saj_grid_l1_import_energy_total` | Capteur | kWh | HS3, H2 | - | Non |
| Énergie injectée réseau L2 du jour | `sensor.saj_grid_l2_export_energy_today` | Capteur | kWh | HS3, H2 | Phase 2 et suivantes | Non |
| Énergie injectée réseau L2 du mois | `sensor.saj_grid_l2_export_energy_month` | Capteur | kWh | HS3, H2 | Phase 2 et suivantes | Non |
| Énergie injectée réseau L2 de l'année | `sensor.saj_grid_l2_export_energy_year` | Capteur | kWh | HS3, H2 | Phase 2 et suivantes | Non |
| Énergie injectée réseau L2 totale | `sensor.saj_grid_l2_export_energy_total` | Capteur | kWh | HS3, H2 | Phase 2 et suivantes | Non |
| Énergie injectée réseau L3 du jour | `sensor.saj_grid_l3_export_energy_today` | Capteur | kWh | HS3, H2 | Phase 3 et suivantes | Non |
| Énergie injectée réseau L3 du mois | `sensor.saj_grid_l3_export_energy_month` | Capteur | kWh | HS3, H2 | Phase 3 et suivantes | Non |
| Énergie injectée réseau L3 de l'année | `sensor.saj_grid_l3_export_energy_year` | Capteur | kWh | HS3, H2 | Phase 3 et suivantes | Non |
| Énergie injectée réseau L3 totale | `sensor.saj_grid_l3_export_energy_total` | Capteur | kWh | HS3, H2 | Phase 3 et suivantes | Non |
| Énergie soutirée réseau L2 du jour | `sensor.saj_grid_l2_import_energy_today` | Capteur | kWh | HS3, H2 | Phase 2 et suivantes | Non |
| Énergie soutirée réseau L2 du mois | `sensor.saj_grid_l2_import_energy_month` | Capteur | kWh | HS3, H2 | Phase 2 et suivantes | Non |
| Énergie soutirée réseau L2 de l'année | `sensor.saj_grid_l2_import_energy_year` | Capteur | kWh | HS3, H2 | Phase 2 et suivantes | Non |
| Énergie soutirée réseau L2 totale | `sensor.saj_grid_l2_import_energy_total` | Capteur | kWh | HS3, H2 | Phase 2 et suivantes | Non |
| Énergie soutirée réseau L3 du jour | `sensor.saj_grid_l3_import_energy_today` | Capteur | kWh | HS3, H2 | Phase 3 et suivantes | Non |
| Énergie soutirée réseau L3 du mois | `sensor.saj_grid_l3_import_energy_month` | Capteur | kWh | HS3, H2 | Phase 3 et suivantes | Non |
| Énergie soutirée réseau L3 de l'année | `sensor.saj_grid_l3_import_energy_year` | Capteur | kWh | HS3, H2 | Phase 3 et suivantes | Non |
| Énergie soutirée réseau L3 totale | `sensor.saj_grid_l3_import_energy_total` | Capteur | kWh | HS3, H2 | Phase 3 et suivantes | Non |
| Énergie soutirée du réseau du jour | `sensor.saj_grid_import_energy_today` | Capteur | kWh | HS3, H2 | - | Oui |
| Énergie soutirée du réseau du mois | `sensor.saj_grid_import_energy_month` | Capteur | kWh | HS3, H2 | - | Non |
| Énergie soutirée du réseau de l'année | `sensor.saj_grid_import_energy_year` | Capteur | kWh | HS3, H2 | - | Non |
| Énergie soutirée du réseau totale | `sensor.saj_grid_import_energy_total` | Capteur | kWh | HS3, H2 | - | Oui |
| Énergie injectée dans le réseau du jour | `sensor.saj_grid_export_energy_today` | Capteur | kWh | HS3, H2 | - | Oui |
| Énergie injectée dans le réseau du mois | `sensor.saj_grid_export_energy_month` | Capteur | kWh | HS3, H2 | - | Non |
| Énergie injectée dans le réseau de l'année | `sensor.saj_grid_export_energy_year` | Capteur | kWh | HS3, H2 | - | Non |
| Énergie injectée dans le réseau totale | `sensor.saj_grid_export_energy_total` | Capteur | kWh | HS3, H2 | - | Oui |
| Tension compteur A L1 | `sensor.saj_meter_a_l1_voltage` | Capteur | V | HS3, H2 | Compteur A | Non |
| Courant compteur A L1 | `sensor.saj_meter_a_l1_current` | Capteur | A | HS3, H2 | Compteur A | Non |
| Puissance compteur A L1 | `sensor.saj_meter_a_l1_power` | Capteur | W | HS3, H2 | Compteur A | Non |
| Puissance apparente compteur A L1 | `sensor.saj_meter_a_l1_apparent_power` | Capteur | VA | HS3, H2 | Compteur A | Non |
| Facteur de puissance compteur A L1 | `sensor.saj_meter_a_l1_power_factor` | Capteur | - | HS3, H2 | Compteur A | Non |
| Fréquence compteur A L1 | `sensor.saj_meter_a_l1_frequency` | Capteur | Hz | HS3, H2 | Compteur A | Non |
| Tension compteur A L2 | `sensor.saj_meter_a_l2_voltage` | Capteur | V | HS3, H2 | Compteur A; Phase 2 et suivantes | Non |
| Courant compteur A L2 | `sensor.saj_meter_a_l2_current` | Capteur | A | HS3, H2 | Compteur A; Phase 2 et suivantes | Non |
| Puissance compteur A L2 | `sensor.saj_meter_a_l2_power` | Capteur | W | HS3, H2 | Compteur A; Phase 2 et suivantes | Non |
| Puissance apparente compteur A L2 | `sensor.saj_meter_a_l2_apparent_power` | Capteur | VA | HS3, H2 | Compteur A; Phase 2 et suivantes | Non |
| Facteur de puissance compteur A L2 | `sensor.saj_meter_a_l2_power_factor` | Capteur | - | HS3, H2 | Compteur A; Phase 2 et suivantes | Non |
| Fréquence compteur A L2 | `sensor.saj_meter_a_l2_frequency` | Capteur | Hz | HS3, H2 | Compteur A; Phase 2 et suivantes | Non |
| Tension compteur A L3 | `sensor.saj_meter_a_l3_voltage` | Capteur | V | HS3, H2 | Compteur A; Phase 3 et suivantes | Non |
| Courant compteur A L3 | `sensor.saj_meter_a_l3_current` | Capteur | A | HS3, H2 | Compteur A; Phase 3 et suivantes | Non |
| Puissance compteur A L3 | `sensor.saj_meter_a_l3_power` | Capteur | W | HS3, H2 | Compteur A; Phase 3 et suivantes | Non |
| Puissance apparente compteur A L3 | `sensor.saj_meter_a_l3_apparent_power` | Capteur | VA | HS3, H2 | Compteur A; Phase 3 et suivantes | Non |
| Facteur de puissance compteur A L3 | `sensor.saj_meter_a_l3_power_factor` | Capteur | - | HS3, H2 | Compteur A; Phase 3 et suivantes | Non |
| Fréquence compteur A L3 | `sensor.saj_meter_a_l3_frequency` | Capteur | Hz | HS3, H2 | Compteur A; Phase 3 et suivantes | Non |
| Puissance réactive compteur A L1 | `sensor.saj_meter_a_l1_reactive_power` | Capteur | var | HS3 | Compteur A | Non |
| Puissance réactive compteur A L2 | `sensor.saj_meter_a_l2_reactive_power` | Capteur | var | HS3 | Compteur A; Phase 2 et suivantes | Non |
| Puissance réactive compteur A L3 | `sensor.saj_meter_a_l3_reactive_power` | Capteur | var | HS3 | Compteur A; Phase 3 et suivantes | Non |
| Puissance apparente réseau L1 | `sensor.saj_grid_l1_apparent_power` | Capteur | VA | HS3 | Compteur A | Non |
| Courant réseau L1 | `sensor.saj_grid_l1_current` | Capteur | A | HS3 | Compteur A | Non |
| Puissance réseau L1 | `sensor.saj_grid_l1_power` | Capteur | W | HS3 | Compteur A | Non |
| Facteur de puissance réseau L1 | `sensor.saj_grid_l1_power_factor` | Capteur | - | HS3 | Compteur A | Non |
| Puissance apparente réseau L2 | `sensor.saj_grid_l2_apparent_power` | Capteur | VA | HS3 | Compteur A; Phase 2 et suivantes | Non |
| Courant réseau L2 | `sensor.saj_grid_l2_current` | Capteur | A | HS3 | Compteur A; Phase 2 et suivantes | Non |
| Puissance réseau L2 | `sensor.saj_grid_l2_power` | Capteur | W | HS3 | Compteur A; Phase 2 et suivantes | Non |
| Facteur de puissance réseau L2 | `sensor.saj_grid_l2_power_factor` | Capteur | - | HS3 | Compteur A; Phase 2 et suivantes | Non |
| Puissance apparente réseau L3 | `sensor.saj_grid_l3_apparent_power` | Capteur | VA | HS3 | Compteur A; Phase 3 et suivantes | Non |
| Courant réseau L3 | `sensor.saj_grid_l3_current` | Capteur | A | HS3 | Compteur A; Phase 3 et suivantes | Non |
| Puissance réseau L3 | `sensor.saj_grid_l3_power` | Capteur | W | HS3 | Compteur A; Phase 3 et suivantes | Non |
| Facteur de puissance réseau L3 | `sensor.saj_grid_l3_power_factor` | Capteur | - | HS3 | Compteur A; Phase 3 et suivantes | Non |
| Puissance du réseau | `sensor.saj_grid_power` | Capteur | W | HS3 | Compteur A | Oui |
| Puissance du compteur A | `sensor.saj_meter_a_power` | Capteur | W | HS3, H2 | Compteur A | Oui |
| Type de réseau | `sensor.saj_grid_type` | Capteur | - | H2 | - | Non |
| Courant réseau L1 | `sensor.saj_grid_l1_current` | Capteur | A | H2 | - | Non |
| Puissance réseau L1 | `sensor.saj_grid_l1_power` | Capteur | W | H2 | - | Non |
| Puissance apparente réseau L1 | `sensor.saj_grid_l1_apparent_power` | Capteur | VA | H2 | - | Non |
| Facteur de puissance réseau L1 | `sensor.saj_grid_l1_power_factor` | Capteur | - | H2 | - | Non |
| Courant réseau L2 | `sensor.saj_grid_l2_current` | Capteur | A | H2 | Phase 2 et suivantes | Non |
| Puissance réseau L2 | `sensor.saj_grid_l2_power` | Capteur | W | H2 | Phase 2 et suivantes | Non |
| Puissance apparente réseau L2 | `sensor.saj_grid_l2_apparent_power` | Capteur | VA | H2 | Phase 2 et suivantes | Non |
| Facteur de puissance réseau L2 | `sensor.saj_grid_l2_power_factor` | Capteur | - | H2 | Phase 2 et suivantes | Non |
| Courant réseau L3 | `sensor.saj_grid_l3_current` | Capteur | A | H2 | Phase 3 et suivantes | Non |
| Puissance réseau L3 | `sensor.saj_grid_l3_power` | Capteur | W | H2 | Phase 3 et suivantes | Non |
| Puissance apparente réseau L3 | `sensor.saj_grid_l3_apparent_power` | Capteur | VA | H2 | Phase 3 et suivantes | Non |
| Facteur de puissance réseau L3 | `sensor.saj_grid_l3_power_factor` | Capteur | - | H2 | Phase 3 et suivantes | Non |
| Puissance du réseau | `sensor.saj_grid_power` | Capteur | W | H2 | - | Oui |
| Puissance apparente du réseau | `sensor.saj_grid_apparent_power` | Capteur | VA | H2 | - | Non |
