[en](../../../en-gb/user/entities/ev-charger.md) | [de](../../../de/user/entities/ev-charger.md) | [nl](../../../nl/user/entities/ev-charger.md) | fr | [zh](../../../zh-hans/user/entities/ev-charger.md) | [es](../../../es/user/entities/ev-charger.md) | [it](../../../it/user/entities/ev-charger.md) | [pl](../../../pl/user/entities/ev-charger.md) | [sv](../../../sv/user/entities/ev-charger.md)

# Chargeur de VE

Le chargeur de VE et ses commandes de charge.

La liste des fonctionnalités de l'intégration explique les entités de Chargeur de VE dans [Équipement optionnel](../../../../custom_components/saj_local/docs/features.md#optional-equipment).

87 entités. Généré par `make docs`. Ne pas modifier à la main.

Un préfixe défini dans Configurer se place après `saj_` dans l'ID de chaque entité de Chargeur de VE, par exemple `sensor.saj_house_ev_serial_number` avec le préfixe `house`.

| Nom | ID d'entité | Type | Unité | Modèles | Équipement et nombres | Activée par défaut |
| --- | --- | --- | --- | --- | --- | --- |
| Numéro de série du chargeur de VE | `sensor.saj_ev_serial_number` | Capteur | - | HS3 | Chargeur de VE | Non |
| Modèle du chargeur de VE | `sensor.saj_ev_model` | Capteur | - | HS3 | Chargeur de VE | Non |
| Version logicielle du chargeur de VE | `sensor.saj_ev_software_version` | Capteur | - | HS3 | Chargeur de VE | Non |
| Version matérielle du chargeur de VE | `sensor.saj_ev_hardware_version` | Capteur | - | HS3 | Chargeur de VE | Non |
| Nombre de phases du chargeur de VE | `sensor.saj_ev_phase_count` | Capteur | - | HS3 | Chargeur de VE | Non |
| Puissance minimale du chargeur de VE | `sensor.saj_ev_minimum_power` | Capteur | W | HS3 | Chargeur de VE | Non |
| Puissance maximale du chargeur de VE | `sensor.saj_ev_maximum_power` | Capteur | W | HS3 | Chargeur de VE | Non |
| Mode de fonctionnement du chargeur de VE | `sensor.saj_ev_work_mode` | Capteur | - | HS3 | Chargeur de VE | Non |
| État du chargeur de VE | `sensor.saj_ev_status` | Capteur | - | HS3 | Chargeur de VE | Oui |
| Tension L1 du chargeur de VE | `sensor.saj_ev_l1_voltage` | Capteur | V | HS3 | Chargeur de VE | Non |
| Courant L1 du chargeur de VE | `sensor.saj_ev_l1_current` | Capteur | A | HS3 | Chargeur de VE | Non |
| Tension L2 du chargeur de VE | `sensor.saj_ev_l2_voltage` | Capteur | V | HS3 | Chargeur de VE | Non |
| Courant L2 du chargeur de VE | `sensor.saj_ev_l2_current` | Capteur | A | HS3 | Chargeur de VE | Non |
| Tension L3 du chargeur de VE | `sensor.saj_ev_l3_voltage` | Capteur | V | HS3 | Chargeur de VE | Non |
| Courant L3 du chargeur de VE | `sensor.saj_ev_l3_current` | Capteur | A | HS3 | Chargeur de VE | Non |
| Puissance du chargeur de VE | `sensor.saj_ev_power` | Capteur | W | HS3 | Chargeur de VE | Oui |
| Durée de charge du VE | `sensor.saj_ev_charge_duration` | Capteur | min | HS3 | Chargeur de VE | Non |
| Énergie de la session du chargeur de VE | `sensor.saj_ev_session_energy` | Capteur | kWh | HS3 | Chargeur de VE | Oui |
| Énergie totale du chargeur de VE | `sensor.saj_ev_total_energy` | Capteur | kWh | HS3 | Chargeur de VE | Oui |
| Tension du signal pilote du chargeur de VE | `sensor.saj_ev_control_pilot_voltage` | Capteur | V | HS3 | Chargeur de VE | Non |
| Rapport cyclique du chargeur de VE | `sensor.saj_ev_duty_cycle` | Capteur | % | HS3 | Chargeur de VE | Non |
| Commande à distance du chargeur de VE | `sensor.saj_ev_remote_control` | Capteur | - | HS3 | Chargeur de VE | Non |
| Consigne de courant du chargeur de VE | `sensor.saj_ev_current_setpoint` | Capteur | A | HS3 | Chargeur de VE | Non |
| Début de la session du chargeur de VE | `sensor.saj_ev_session_start` | Capteur | - | HS3 | Chargeur de VE | Non |
| Fin de la session du chargeur de VE | `sensor.saj_ev_session_end` | Capteur | - | HS3 | Chargeur de VE | Non |
| Version du protocole des réglages du chargeur de VE | `sensor.saj_ev_settings_protocol_version` | Capteur | - | HS3 | Chargeur de VE | Non |
| Adresse du chargeur de VE | `sensor.saj_ev_address` | Capteur | - | HS3 | Chargeur de VE | Non |
| Débit en bauds du chargeur de VE | `sensor.saj_ev_baud_rate` | Capteur | - | HS3 | Chargeur de VE | Non |
| Nombre de chargeurs de VE | `sensor.saj_ev_charger_count` | Capteur | - | HS3 | Chargeur de VE | Non |
| Délai d'expiration de la communication du chargeur de VE | `sensor.saj_ev_communication_timeout` | Capteur | s | HS3 | Chargeur de VE | Non |
| Mode du port du chargeur de VE | `sensor.saj_ev_port_mode` | Capteur | - | HS3 | Chargeur de VE | Non |
| Adresse du port du chargeur de VE | `sensor.saj_ev_port_address` | Capteur | - | HS3 | Chargeur de VE | Non |
| Mode du chargeur de VE | `select.saj_ev_mode` | Sélection | - | HS3 | Chargeur de VE | Oui |
| Puissance de charge du VE | `number.saj_ev_charge_power` | Nombre | W | HS3 | Chargeur de VE | Non |
| Heure de début de la plage 1 du chargeur de VE | `time.saj_ev_slot_1_start` | Heure | - | HS3 | Chargeur de VE | Non |
| Heure de fin de la plage 1 du chargeur de VE | `time.saj_ev_slot_1_end` | Heure | - | HS3 | Chargeur de VE | Non |
| Mode de la plage 1 du chargeur de VE | `select.saj_ev_slot_1_mode` | Sélection | - | HS3 | Chargeur de VE | Non |
| Charge depuis le réseau de la plage 1 du chargeur de VE | `switch.saj_ev_slot_1_grid_charging` | Interrupteur | - | HS3 | Chargeur de VE | Non |
| Décharge de la batterie de la plage 1 du chargeur de VE | `switch.saj_ev_slot_1_battery_discharge` | Interrupteur | - | HS3 | Chargeur de VE | Non |
| Jours de la plage 1 du chargeur de VE | `number.saj_ev_slot_1_days` | Nombre | - | HS3 | Chargeur de VE | Non |
| Puissance de la plage 1 du chargeur de VE | `number.saj_ev_slot_1_power` | Nombre | W | HS3 | Chargeur de VE | Non |
| Heure de début de la plage 2 du chargeur de VE | `time.saj_ev_slot_2_start` | Heure | - | HS3 | Chargeur de VE | Non |
| Heure de fin de la plage 2 du chargeur de VE | `time.saj_ev_slot_2_end` | Heure | - | HS3 | Chargeur de VE | Non |
| Mode de la plage 2 du chargeur de VE | `select.saj_ev_slot_2_mode` | Sélection | - | HS3 | Chargeur de VE | Non |
| Charge depuis le réseau de la plage 2 du chargeur de VE | `switch.saj_ev_slot_2_grid_charging` | Interrupteur | - | HS3 | Chargeur de VE | Non |
| Décharge de la batterie de la plage 2 du chargeur de VE | `switch.saj_ev_slot_2_battery_discharge` | Interrupteur | - | HS3 | Chargeur de VE | Non |
| Jours de la plage 2 du chargeur de VE | `number.saj_ev_slot_2_days` | Nombre | - | HS3 | Chargeur de VE | Non |
| Puissance de la plage 2 du chargeur de VE | `number.saj_ev_slot_2_power` | Nombre | W | HS3 | Chargeur de VE | Non |
| Heure de début de la plage 3 du chargeur de VE | `time.saj_ev_slot_3_start` | Heure | - | HS3 | Chargeur de VE | Non |
| Heure de fin de la plage 3 du chargeur de VE | `time.saj_ev_slot_3_end` | Heure | - | HS3 | Chargeur de VE | Non |
| Mode de la plage 3 du chargeur de VE | `select.saj_ev_slot_3_mode` | Sélection | - | HS3 | Chargeur de VE | Non |
| Charge depuis le réseau de la plage 3 du chargeur de VE | `switch.saj_ev_slot_3_grid_charging` | Interrupteur | - | HS3 | Chargeur de VE | Non |
| Décharge de la batterie de la plage 3 du chargeur de VE | `switch.saj_ev_slot_3_battery_discharge` | Interrupteur | - | HS3 | Chargeur de VE | Non |
| Jours de la plage 3 du chargeur de VE | `number.saj_ev_slot_3_days` | Nombre | - | HS3 | Chargeur de VE | Non |
| Puissance de la plage 3 du chargeur de VE | `number.saj_ev_slot_3_power` | Nombre | W | HS3 | Chargeur de VE | Non |
| Heure de début de la plage 4 du chargeur de VE | `time.saj_ev_slot_4_start` | Heure | - | HS3 | Chargeur de VE | Non |
| Heure de fin de la plage 4 du chargeur de VE | `time.saj_ev_slot_4_end` | Heure | - | HS3 | Chargeur de VE | Non |
| Mode de la plage 4 du chargeur de VE | `select.saj_ev_slot_4_mode` | Sélection | - | HS3 | Chargeur de VE | Non |
| Charge depuis le réseau de la plage 4 du chargeur de VE | `switch.saj_ev_slot_4_grid_charging` | Interrupteur | - | HS3 | Chargeur de VE | Non |
| Décharge de la batterie de la plage 4 du chargeur de VE | `switch.saj_ev_slot_4_battery_discharge` | Interrupteur | - | HS3 | Chargeur de VE | Non |
| Jours de la plage 4 du chargeur de VE | `number.saj_ev_slot_4_days` | Nombre | - | HS3 | Chargeur de VE | Non |
| Puissance de la plage 4 du chargeur de VE | `number.saj_ev_slot_4_power` | Nombre | W | HS3 | Chargeur de VE | Non |
| Heure de début de la plage 5 du chargeur de VE | `time.saj_ev_slot_5_start` | Heure | - | HS3 | Chargeur de VE | Non |
| Heure de fin de la plage 5 du chargeur de VE | `time.saj_ev_slot_5_end` | Heure | - | HS3 | Chargeur de VE | Non |
| Mode de la plage 5 du chargeur de VE | `select.saj_ev_slot_5_mode` | Sélection | - | HS3 | Chargeur de VE | Non |
| Charge depuis le réseau de la plage 5 du chargeur de VE | `switch.saj_ev_slot_5_grid_charging` | Interrupteur | - | HS3 | Chargeur de VE | Non |
| Décharge de la batterie de la plage 5 du chargeur de VE | `switch.saj_ev_slot_5_battery_discharge` | Interrupteur | - | HS3 | Chargeur de VE | Non |
| Jours de la plage 5 du chargeur de VE | `number.saj_ev_slot_5_days` | Nombre | - | HS3 | Chargeur de VE | Non |
| Puissance de la plage 5 du chargeur de VE | `number.saj_ev_slot_5_power` | Nombre | W | HS3 | Chargeur de VE | Non |
| Heure de début de la plage 6 du chargeur de VE | `time.saj_ev_slot_6_start` | Heure | - | HS3 | Chargeur de VE | Non |
| Heure de fin de la plage 6 du chargeur de VE | `time.saj_ev_slot_6_end` | Heure | - | HS3 | Chargeur de VE | Non |
| Mode de la plage 6 du chargeur de VE | `select.saj_ev_slot_6_mode` | Sélection | - | HS3 | Chargeur de VE | Non |
| Charge depuis le réseau de la plage 6 du chargeur de VE | `switch.saj_ev_slot_6_grid_charging` | Interrupteur | - | HS3 | Chargeur de VE | Non |
| Décharge de la batterie de la plage 6 du chargeur de VE | `switch.saj_ev_slot_6_battery_discharge` | Interrupteur | - | HS3 | Chargeur de VE | Non |
| Jours de la plage 6 du chargeur de VE | `number.saj_ev_slot_6_days` | Nombre | - | HS3 | Chargeur de VE | Non |
| Puissance de la plage 6 du chargeur de VE | `number.saj_ev_slot_6_power` | Nombre | W | HS3 | Chargeur de VE | Non |
| Heure de début de la plage 7 du chargeur de VE | `time.saj_ev_slot_7_start` | Heure | - | HS3 | Chargeur de VE | Non |
| Heure de fin de la plage 7 du chargeur de VE | `time.saj_ev_slot_7_end` | Heure | - | HS3 | Chargeur de VE | Non |
| Mode de la plage 7 du chargeur de VE | `select.saj_ev_slot_7_mode` | Sélection | - | HS3 | Chargeur de VE | Non |
| Charge depuis le réseau de la plage 7 du chargeur de VE | `switch.saj_ev_slot_7_grid_charging` | Interrupteur | - | HS3 | Chargeur de VE | Non |
| Décharge de la batterie de la plage 7 du chargeur de VE | `switch.saj_ev_slot_7_battery_discharge` | Interrupteur | - | HS3 | Chargeur de VE | Non |
| Jours de la plage 7 du chargeur de VE | `number.saj_ev_slot_7_days` | Nombre | - | HS3 | Chargeur de VE | Non |
| Puissance de la plage 7 du chargeur de VE | `number.saj_ev_slot_7_power` | Nombre | W | HS3 | Chargeur de VE | Non |
| Charge au courant minimal du chargeur de VE | `switch.saj_ev_minimum_current_charging` | Interrupteur | - | HS3 | Chargeur de VE | Non |
| Charge EMS du chargeur de VE | `switch.saj_ev_ems_charging` | Interrupteur | - | HS3 | Chargeur de VE | Non |
| Mode de phase EMS du chargeur de VE | `select.saj_ev_ems_phase_mode` | Sélection | - | HS3 | Chargeur de VE | Non |
| Courant de charge EMS du chargeur de VE | `number.saj_ev_ems_charge_current` | Nombre | A | HS3 | Chargeur de VE | Non |
