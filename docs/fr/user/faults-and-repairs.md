[en](../../en-gb/user/faults-and-repairs.md) | [de](../../de/user/faults-and-repairs.md) | [nl](../../nl/user/faults-and-repairs.md) | fr | [zh](../../zh-hans/user/faults-and-repairs.md) | [es](../../es/user/faults-and-repairs.md) | [it](../../it/user/faults-and-repairs.md) | [pl](../../pl/user/faults-and-repairs.md) | [sv](../../sv/user/faults-and-repairs.md)

# Défauts de l'équipement et réparations

La page Défauts de l'équipement et réparations explique comment SAJ Local affiche les défauts que l'onduleur, la batterie et le chargeur de VE signalent, et quels problèmes de réparation SAJ Local déclenche dans Home Assistant. La liste complète du comportement des défauts se trouve dans la section [Défauts de l'équipement et réparations](../../../custom_components/saj_local/docs/features.md#device-faults-and-repairs) de la liste des fonctionnalités de l'intégration. Chaque entité de défaut figure dans les [entités de défauts](entities/faults.md) de la référence des entités.

Les défauts de l'équipement et les problèmes de réparation sont distincts. Un défaut de l'équipement est une entité qui rapporte ce que dit l'équipement. Un problème de réparation est un problème avec la connexion de SAJ Local à l'équipement ou avec la configuration de SAJ Local, et Home Assistant liste le problème sous Paramètres puis Réparations.

## Défauts de l'équipement

Chaque défaut nommé de l'onduleur, de la batterie et du chargeur de VE est un capteur binaire avec la classe d'appareil problème, activé par défaut. Un défaut a un historique et peut déclencher une automatisation.

- **Résumé :** l'onduleur, la batterie et le chargeur de VE ont chacun un défaut de résumé, par exemple Défaut de l'onduleur, qui est activé quand l'équipement signale quoi que ce soit.
- **Non reconnu :** chaque équipement a aussi un défaut non reconnu qui est activé quand l'onduleur positionne un bit sans signification documentée. Le [téléchargement des diagnostics](troubleshooting.md#télécharger-les-diagnostics) liste le registre et le bit, pour que vous puissiez signaler le bit.
- **Un seul ID d'entité sur chaque modèle :** un défaut a un seul ID d'entité sur chaque modèle qui signale le défaut. Un défaut qu'un modèle ne signale pas n'a aucune entité sur ce modèle.
- **Modules de batterie :** chaque module de batterie a une entité de défaut et une entité d'avertissement. Un HS3 a un module. Un H2 en a jusqu'à quatre.
- **Équipement non installé :** les défauts de la batterie n'existent que lorsqu'une batterie est installée, et les défauts du chargeur de VE que lorsqu'un chargeur de VE est installé. Voir l'[équipement optionnel](optional-equipment.md).
- **Un registre de défauts qui ne peut pas être lu :** les défauts qui dépendent du registre sont indisponibles. SAJ Local ne devine pas.
- **Le journal :** un défaut qui s'active consigne un avertissement qui nomme le système et le défaut. Quand le défaut disparaît, SAJ Local consigne une ligne d'information.

La [carte des défauts](cards/faults-card.md) liste les défauts actifs d'un système sur un tableau de bord, avec le temps écoulé depuis le début de chacun. Le bouton Effacer le défaut de la carte envoie la commande Effacer le défaut en cours, qui nécessite [Autoriser le contrôle](changing-settings.md#autoriser-le-contrôle).

## Problèmes de réparation

SAJ Local déclenche un problème de réparation pour une situation sur laquelle vous pouvez agir.

| Problème de réparation | Déclenché quand | Ce que vous pouvez faire |
| --- | --- | --- |
| Le système est réglé sur un mauvais modèle | L'onduleur à l'adresse s'identifie comme un autre modèle que celui choisi. | Un correctif adopte le modèle que SAJ Local a trouvé. Voir [remplacer l'onduleur](replacing-the-inverter.md). |
| Le système atteint maintenant un autre onduleur | L'onduleur à l'adresse a un autre numéro de série. | Un correctif adopte le nouvel onduleur. Voir [remplacer l'onduleur](replacing-the-inverter.md). |
| Le système atteint un appareil non reconnu | Le type d'appareil n'est pas un modèle reconnu. | Choisissez le modèle dans Configurer. SAJ Local utilise alors le modèle sans vérification. |
| Le système a des mesures que l'onduleur refuse | L'onduleur a refusé les mesures trois fois de suite. | Un correctif désactive les entités listées, pour que SAJ Local ne lise plus les entités. Voir [protéger l'onduleur](protecting-the-inverter.md#quand-londuleur-refuse-une-lecture). |
| Le système ne répond plus | L'onduleur n'a pas répondu depuis 15 minutes. | Vérifiez l'alimentation, le réseau et les autres clients Modbus. Le problème disparaît à la première bonne lecture. |
| L'équipement n'est plus détecté | Un équipement que SAJ Local avait détecté n'est plus détecté. | Vérifiez l'équipement, ou réglez l'équipement sur Non installé dans Configurer. Voir l'[équipement optionnel](optional-equipment.md#quand-léquipement-mémorisé-nest-plus-détecté). |

![Un problème de réparation dans Home Assistant qui indique que SAJ HS3MOCK000000000003 a des mesures que l'onduleur refuse](../../images/fr/faults-and-repairs-repair-issue.png)

Les trois premiers problèmes sont les problèmes de modèle. Un seul des problèmes de modèle est ouvert pour un système, et le problème indiquant que le système ne répond plus n'est pas déclenché tant qu'un problème de modèle est ouvert.

Un problème de réparation disparaît quand la situation du problème prend fin, ou quand vous supprimez le système. Le problème sur les mesures refusées disparaît aussi quand vous désactivez une entité listée.

## Pas encore pris en charge

- Un problème de réparation pour un défaut de l'équipement. Les défauts de l'équipement sont des entités, et l'intégration ne déclenche pas de problème de réparation pour un défaut.
