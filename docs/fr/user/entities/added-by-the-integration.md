[en](../../../en-gb/user/entities/added-by-the-integration.md) | [de](../../../de/user/entities/added-by-the-integration.md) | [nl](../../../nl/user/entities/added-by-the-integration.md) | fr | [zh](../../../zh-hans/user/entities/added-by-the-integration.md) | [es](../../../es/user/entities/added-by-the-integration.md) | [it](../../../it/user/entities/added-by-the-integration.md) | [pl](../../../pl/user/entities/added-by-the-integration.md) | [sv](../../../sv/user/entities/added-by-the-integration.md)

# Ajoutées par l'intégration

Entités que l'intégration ajoute en dehors du catalogue de registres.

La liste des fonctionnalités de l'intégration explique les entités de Ajoutées par l'intégration dans [Modification des réglages](../../../../custom_components/saj_local/docs/features.md#changing-settings) et [Pilotage de puissance](../../../../custom_components/saj_local/docs/features.md#power-control).

7 entités. Généré par `make docs`. Ne pas modifier à la main.

Un préfixe défini dans Configurer se place après `saj_` dans l'ID de chaque entité de Ajoutées par l'intégration, par exemple `binary_sensor.saj_house_control_allowed` avec le préfixe `house`.

| Nom | ID d'entité | Type | Unité | Modèles | Équipement et nombres | Activée par défaut |
| --- | --- | --- | --- | --- | --- | --- |
| Contrôle autorisé | `binary_sensor.saj_control_allowed` | Capteur binaire | - | HS3, H2 | - | Oui |
| Pilotage de puissance de la batterie | `switch.saj_battery_power_control` | Interrupteur | - | HS3, H2 | Batterie | Non |
| Puissance cible de la batterie | `number.saj_battery_power_target` | Nombre | W | HS3, H2 | Batterie | Non |
| Pilotage de puissance du réseau | `switch.saj_grid_power_control` | Interrupteur | - | HS3 | Compteur A | Non |
| Puissance cible du réseau | `number.saj_grid_power_target` | Nombre | W | HS3 | Compteur A | Non |
| Pilotage de puissance de l'onduleur | `switch.saj_inverter_power_control` | Interrupteur | - | HS3 | - | Non |
| Puissance cible de l'onduleur | `number.saj_inverter_power_target` | Nombre | W | HS3 | - | Non |
