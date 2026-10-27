[en](../../../en-gb/user/entities/parallel-system.md) | [de](../../../de/user/entities/parallel-system.md) | [nl](../../../nl/user/entities/parallel-system.md) | fr | [zh](../../../zh-hans/user/entities/parallel-system.md) | [es](../../../es/user/entities/parallel-system.md) | [it](../../../it/user/entities/parallel-system.md) | [pl](../../../pl/user/entities/parallel-system.md) | [sv](../../../sv/user/entities/parallel-system.md)

# Système en parallèle

Les mesures d'un système de machines en parallèle.

La liste des fonctionnalités de l'intégration explique les entités de Système en parallèle dans [Équipement optionnel](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

63 entités. Généré par `make docs`. Ne pas modifier à la main.

Un préfixe défini dans Configurer se place après `saj_` dans l'ID de chaque entité de Système en parallèle, par exemple `sensor.saj_house_parallel_id` avec le préfixe `house`.

| Nom | ID d'entité | Type | Unité | Modèles | Équipement et nombres | Activée par défaut |
| --- | --- | --- | --- | --- | --- | --- |
| ID de la machine en parallèle | `sensor.saj_parallel_id` | Capteur | - | HS3, H2 | Système en parallèle | Non |
| Nombre de machines en parallèle | `sensor.saj_parallel_count` | Capteur | - | HS3, H2 | Système en parallèle | Non |
| État de charge de la batterie du système en parallèle | `sensor.saj_parallel_battery_soc` | Capteur | % | HS3, H2 | Système en parallèle | Oui |
| Capacité de la batterie du système en parallèle | `sensor.saj_parallel_battery_capacity` | Capteur | Ah | HS3, H2 | Système en parallèle | Non |
| Puissance du compteur B du système en parallèle | `sensor.saj_parallel_meter_b_power` | Capteur | W | HS3 | Système en parallèle | Non |
| Énergie solaire du système en parallèle du jour | `sensor.saj_parallel_pv_energy_today` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie solaire du système en parallèle du mois | `sensor.saj_parallel_pv_energy_month` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie solaire du système en parallèle de l'année | `sensor.saj_parallel_pv_energy_year` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie solaire du système en parallèle totale | `sensor.saj_parallel_pv_energy_total` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie de charge de la batterie du système en parallèle du jour | `sensor.saj_parallel_battery_charge_energy_today` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie de charge de la batterie du système en parallèle du mois | `sensor.saj_parallel_battery_charge_energy_month` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie de charge de la batterie du système en parallèle de l'année | `sensor.saj_parallel_battery_charge_energy_year` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie de charge de la batterie du système en parallèle totale | `sensor.saj_parallel_battery_charge_energy_total` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie de décharge de la batterie du système en parallèle du jour | `sensor.saj_parallel_battery_discharge_energy_today` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie de décharge de la batterie du système en parallèle du mois | `sensor.saj_parallel_battery_discharge_energy_month` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie de décharge de la batterie du système en parallèle de l'année | `sensor.saj_parallel_battery_discharge_energy_year` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie de décharge de la batterie du système en parallèle totale | `sensor.saj_parallel_battery_discharge_energy_total` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie injectée réseau L1 du système en parallèle du jour | `sensor.saj_parallel_grid_l1_export_energy_today` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie injectée réseau L1 du système en parallèle du mois | `sensor.saj_parallel_grid_l1_export_energy_month` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie injectée réseau L1 du système en parallèle de l'année | `sensor.saj_parallel_grid_l1_export_energy_year` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie injectée réseau L1 du système en parallèle totale | `sensor.saj_parallel_grid_l1_export_energy_total` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie injectée réseau L2 du système en parallèle du jour | `sensor.saj_parallel_grid_l2_export_energy_today` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie injectée réseau L2 du système en parallèle du mois | `sensor.saj_parallel_grid_l2_export_energy_month` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie injectée réseau L2 du système en parallèle de l'année | `sensor.saj_parallel_grid_l2_export_energy_year` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie injectée réseau L2 du système en parallèle totale | `sensor.saj_parallel_grid_l2_export_energy_total` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie injectée réseau L3 du système en parallèle du jour | `sensor.saj_parallel_grid_l3_export_energy_today` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie injectée réseau L3 du système en parallèle du mois | `sensor.saj_parallel_grid_l3_export_energy_month` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie injectée réseau L3 du système en parallèle de l'année | `sensor.saj_parallel_grid_l3_export_energy_year` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie injectée réseau L3 du système en parallèle totale | `sensor.saj_parallel_grid_l3_export_energy_total` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie soutirée réseau L1 du système en parallèle du jour | `sensor.saj_parallel_grid_l1_import_energy_today` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie soutirée réseau L1 du système en parallèle du mois | `sensor.saj_parallel_grid_l1_import_energy_month` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie soutirée réseau L1 du système en parallèle de l'année | `sensor.saj_parallel_grid_l1_import_energy_year` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie soutirée réseau L1 du système en parallèle totale | `sensor.saj_parallel_grid_l1_import_energy_total` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie soutirée réseau L2 du système en parallèle du jour | `sensor.saj_parallel_grid_l2_import_energy_today` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie soutirée réseau L2 du système en parallèle du mois | `sensor.saj_parallel_grid_l2_import_energy_month` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie soutirée réseau L2 du système en parallèle de l'année | `sensor.saj_parallel_grid_l2_import_energy_year` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie soutirée réseau L2 du système en parallèle totale | `sensor.saj_parallel_grid_l2_import_energy_total` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie soutirée réseau L3 du système en parallèle du jour | `sensor.saj_parallel_grid_l3_import_energy_today` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie soutirée réseau L3 du système en parallèle du mois | `sensor.saj_parallel_grid_l3_import_energy_month` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie soutirée réseau L3 du système en parallèle de l'année | `sensor.saj_parallel_grid_l3_import_energy_year` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie soutirée réseau L3 du système en parallèle totale | `sensor.saj_parallel_grid_l3_import_energy_total` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie de la charge domestique du système en parallèle du jour | `sensor.saj_parallel_load_energy_today` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie de la charge domestique du système en parallèle du mois | `sensor.saj_parallel_load_energy_month` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie de la charge domestique du système en parallèle de l'année | `sensor.saj_parallel_load_energy_year` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie de la charge domestique du système en parallèle totale | `sensor.saj_parallel_load_energy_total` | Capteur | kWh | HS3, H2 | Système en parallèle | Non |
| Énergie soutirée du réseau du système en parallèle du jour | `sensor.saj_parallel_grid_import_energy_today` | Capteur | kWh | HS3 | Système en parallèle | Non |
| Énergie soutirée du réseau du système en parallèle du mois | `sensor.saj_parallel_grid_import_energy_month` | Capteur | kWh | HS3 | Système en parallèle | Non |
| Énergie soutirée du réseau du système en parallèle de l'année | `sensor.saj_parallel_grid_import_energy_year` | Capteur | kWh | HS3 | Système en parallèle | Non |
| Énergie soutirée du réseau du système en parallèle totale | `sensor.saj_parallel_grid_import_energy_total` | Capteur | kWh | HS3 | Système en parallèle | Non |
| Énergie injectée dans le réseau du système en parallèle du jour | `sensor.saj_parallel_grid_export_energy_today` | Capteur | kWh | HS3 | Système en parallèle | Non |
| Énergie injectée dans le réseau du système en parallèle du mois | `sensor.saj_parallel_grid_export_energy_month` | Capteur | kWh | HS3 | Système en parallèle | Non |
| Énergie injectée dans le réseau du système en parallèle de l'année | `sensor.saj_parallel_grid_export_energy_year` | Capteur | kWh | HS3 | Système en parallèle | Non |
| Énergie injectée dans le réseau du système en parallèle totale | `sensor.saj_parallel_grid_export_energy_total` | Capteur | kWh | HS3 | Système en parallèle | Non |
| Énergie du compteur solaire du système en parallèle du jour | `sensor.saj_parallel_pv_meter_energy_today` | Capteur | kWh | HS3 | Système en parallèle | Non |
| Énergie du compteur solaire du système en parallèle du mois | `sensor.saj_parallel_pv_meter_energy_month` | Capteur | kWh | HS3 | Système en parallèle | Non |
| Énergie du compteur solaire du système en parallèle de l'année | `sensor.saj_parallel_pv_meter_energy_year` | Capteur | kWh | HS3 | Système en parallèle | Non |
| Énergie du compteur solaire du système en parallèle totale | `sensor.saj_parallel_pv_meter_energy_total` | Capteur | kWh | HS3 | Système en parallèle | Non |
| Puissance du circuit de secours du système en parallèle | `sensor.saj_parallel_backup_load_power` | Capteur | W | HS3, H2 | Système en parallèle | Non |
| Puissance de la batterie du système en parallèle | `sensor.saj_parallel_battery_power` | Capteur | W | HS3, H2 | Système en parallèle | Oui |
| Puissance de la charge du réseau du système en parallèle | `sensor.saj_parallel_grid_load_power` | Capteur | W | HS3, H2 | Système en parallèle | Non |
| Puissance du réseau du système en parallèle | `sensor.saj_parallel_grid_power` | Capteur | W | HS3, H2 | Système en parallèle | Oui |
| Puissance de la charge domestique du système en parallèle | `sensor.saj_parallel_load_power` | Capteur | W | HS3, H2 | Système en parallèle | Oui |
| Puissance solaire du système en parallèle | `sensor.saj_parallel_pv_power` | Capteur | W | HS3, H2 | Système en parallèle | Oui |
