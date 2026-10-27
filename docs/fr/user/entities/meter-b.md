[en](../../../en-gb/user/entities/meter-b.md) | [de](../../../de/user/entities/meter-b.md) | [nl](../../../nl/user/entities/meter-b.md) | fr | [zh](../../../zh-hans/user/entities/meter-b.md) | [es](../../../es/user/entities/meter-b.md) | [it](../../../it/user/entities/meter-b.md) | [pl](../../../pl/user/entities/meter-b.md) | [sv](../../../sv/user/entities/meter-b.md)

# Compteur B

Le compteur B, le second compteur qui mesure un onduleur solaire.

La liste des fonctionnalités de l'intégration explique les entités de Compteur B dans [Équipement optionnel](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

22 entités. Généré par `make docs`. Ne pas modifier à la main.

Un préfixe défini dans Configurer se place après `saj_` dans l'ID de chaque entité de Compteur B, par exemple `sensor.saj_house_meter_b_l1_voltage` avec le préfixe `house`.

| Nom | ID d'entité | Type | Unité | Modèles | Équipement et nombres | Activée par défaut |
| --- | --- | --- | --- | --- | --- | --- |
| Tension compteur B L1 | `sensor.saj_meter_b_l1_voltage` | Capteur | V | HS3, H2 | Compteur B | Non |
| Courant compteur B L1 | `sensor.saj_meter_b_l1_current` | Capteur | A | HS3, H2 | Compteur B | Non |
| Puissance compteur B L1 | `sensor.saj_meter_b_l1_power` | Capteur | W | HS3, H2 | Compteur B | Non |
| Puissance apparente compteur B L1 | `sensor.saj_meter_b_l1_apparent_power` | Capteur | VA | HS3, H2 | Compteur B | Non |
| Facteur de puissance compteur B L1 | `sensor.saj_meter_b_l1_power_factor` | Capteur | - | HS3, H2 | Compteur B | Non |
| Fréquence compteur B L1 | `sensor.saj_meter_b_l1_frequency` | Capteur | Hz | HS3, H2 | Compteur B | Non |
| Tension compteur B L2 | `sensor.saj_meter_b_l2_voltage` | Capteur | V | HS3, H2 | Compteur B; Phase 2 et suivantes | Non |
| Courant compteur B L2 | `sensor.saj_meter_b_l2_current` | Capteur | A | HS3, H2 | Compteur B; Phase 2 et suivantes | Non |
| Puissance compteur B L2 | `sensor.saj_meter_b_l2_power` | Capteur | W | HS3, H2 | Compteur B; Phase 2 et suivantes | Non |
| Puissance apparente compteur B L2 | `sensor.saj_meter_b_l2_apparent_power` | Capteur | VA | HS3, H2 | Compteur B; Phase 2 et suivantes | Non |
| Facteur de puissance compteur B L2 | `sensor.saj_meter_b_l2_power_factor` | Capteur | - | HS3, H2 | Compteur B; Phase 2 et suivantes | Non |
| Fréquence compteur B L2 | `sensor.saj_meter_b_l2_frequency` | Capteur | Hz | HS3, H2 | Compteur B; Phase 2 et suivantes | Non |
| Tension compteur B L3 | `sensor.saj_meter_b_l3_voltage` | Capteur | V | HS3, H2 | Compteur B; Phase 3 et suivantes | Non |
| Courant compteur B L3 | `sensor.saj_meter_b_l3_current` | Capteur | A | HS3, H2 | Compteur B; Phase 3 et suivantes | Non |
| Puissance compteur B L3 | `sensor.saj_meter_b_l3_power` | Capteur | W | HS3, H2 | Compteur B; Phase 3 et suivantes | Non |
| Puissance apparente compteur B L3 | `sensor.saj_meter_b_l3_apparent_power` | Capteur | VA | HS3, H2 | Compteur B; Phase 3 et suivantes | Non |
| Facteur de puissance compteur B L3 | `sensor.saj_meter_b_l3_power_factor` | Capteur | - | HS3, H2 | Compteur B; Phase 3 et suivantes | Non |
| Fréquence compteur B L3 | `sensor.saj_meter_b_l3_frequency` | Capteur | Hz | HS3, H2 | Compteur B; Phase 3 et suivantes | Non |
| Puissance réactive compteur B L1 | `sensor.saj_meter_b_l1_reactive_power` | Capteur | var | HS3 | Compteur B | Non |
| Puissance réactive compteur B L2 | `sensor.saj_meter_b_l2_reactive_power` | Capteur | var | HS3 | Compteur B; Phase 2 et suivantes | Non |
| Puissance réactive compteur B L3 | `sensor.saj_meter_b_l3_reactive_power` | Capteur | var | HS3 | Compteur B; Phase 3 et suivantes | Non |
| Puissance du compteur B | `sensor.saj_meter_b_power` | Capteur | W | HS3, H2 | Compteur B | Oui |
