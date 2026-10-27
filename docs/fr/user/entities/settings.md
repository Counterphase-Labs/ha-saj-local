[en](../../../en-gb/user/entities/settings.md) | [de](../../../de/user/entities/settings.md) | [nl](../../../nl/user/entities/settings.md) | fr | [zh](../../../zh-hans/user/entities/settings.md) | [es](../../../es/user/entities/settings.md) | [it](../../../it/user/entities/settings.md) | [pl](../../../pl/user/entities/settings.md) | [sv](../../../sv/user/entities/settings.md)

# Réglages

Réglages et commandes qui modifient l'onduleur.

La liste des fonctionnalités de l'intégration explique les entités de Réglages dans [Modification des réglages](../../../../custom_components/saj_local/docs/features.md#changing-settings).

22 entités. Généré par `make docs`. Ne pas modifier à la main.

Un préfixe défini dans Configurer se place après `saj_` dans l'ID de chaque entité de Réglages, par exemple `number.saj_house_passive_mode` avec le préfixe `house`.

| Nom | ID d'entité | Type | Unité | Modèles | Équipement et nombres | Activée par défaut |
| --- | --- | --- | --- | --- | --- | --- |
| Mode passif | `number.saj_passive_mode` | Nombre | - | HS3, H2 | - | Non |
| Puissance de charge depuis le réseau en mode passif | `number.saj_passive_grid_charge_power` | Nombre | % | HS3, H2 | - | Non |
| Puissance de décharge vers le réseau en mode passif | `number.saj_passive_grid_discharge_power` | Nombre | % | HS3, H2 | - | Non |
| Mode d'application | `select.saj_application_mode` | Sélection | - | HS3, H2 | - | Oui |
| Limite de puissance de soutirage du réseau | `number.saj_grid_import_power_limit` | Nombre | % | HS3, H2 | - | Non |
| Limite de puissance d'injection dans le réseau | `number.saj_grid_export_power_limit` | Nombre | % | HS3, H2 | - | Non |
| Puissance de limite d'injection | `number.saj_export_limit_power` | Nombre | % | HS3, H2 | - | Non |
| Courant de limite d'injection | `number.saj_export_limit_current` | Nombre | A | HS3, H2 | - | Non |
| Mode de limite d'injection | `select.saj_export_limit_mode` | Sélection | - | HS3, H2 | - | Non |
| Mode d'inactivité du mode horaire | `select.saj_time_of_use_idle_mode` | Sélection | - | HS3, H2 | - | Non |
| Décharge vers le réseau en mode horaire | `switch.saj_time_of_use_grid_discharge` | Interrupteur | - | HS3, H2 | - | Non |
| Mode des LED | `select.saj_led_mode` | Sélection | - | HS3, H2 | - | Non |
| Chargeur de VE activé | `switch.saj_ev_enabled` | Interrupteur | - | HS3 | - | Non |
| Effacer le défaut en cours | `button.saj_clear_current_fault` | Bouton | - | HS3, H2 | - | Non |
| Redémarrer l'onduleur | `button.saj_restart_inverter` | Bouton | - | HS3, H2 | - | Non |
| Synchroniser l'horloge | `button.saj_synchronise_clock` | Bouton | - | HS3, H2 | - | Non |
| Délai d'expiration EMS | `number.saj_ems_timeout` | Nombre | s | HS3 | - | Non |
| Limite de puissance de soutirage de l'onduleur EMS | `number.saj_ems_inverter_import_power_limit` | Nombre | % | HS3 | - | Non |
| Limite de puissance d'injection de l'onduleur EMS | `number.saj_ems_inverter_export_power_limit` | Nombre | % | HS3 | - | Non |
| Limite de puissance solaire EMS | `number.saj_ems_pv_power_limit` | Nombre | % | HS3 | - | Non |
| Supprimer la limite de puissance solaire EMS | `button.saj_ems_pv_power_limit_remove` | Bouton | - | HS3 | - | Non |
| Avertisseur sonore | `switch.saj_buzzer` | Interrupteur | - | H2 | - | Non |
