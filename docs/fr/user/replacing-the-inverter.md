[en](../../en-gb/user/replacing-the-inverter.md) | [de](../../de/user/replacing-the-inverter.md) | [nl](../../nl/user/replacing-the-inverter.md) | fr | [zh](../../zh-hans/user/replacing-the-inverter.md) | [es](../../es/user/replacing-the-inverter.md) | [it](../../it/user/replacing-the-inverter.md) | [pl](../../pl/user/replacing-the-inverter.md) | [sv](../../sv/user/replacing-the-inverter.md)

# Remplacer l'onduleur

La page Remplacer l'onduleur explique comment passer un système à un nouvel onduleur, ou entre un H2 et un HS3, en conservant l'appareil, les entités et l'historique. La liste complète se trouve dans la section [Remplacement de modèle](../../../custom_components/saj_local/docs/features.md#model-replacement) de la liste des fonctionnalités de l'intégration.

## Passer un système à un autre onduleur volontairement

1. Assurez-vous que le nouvel onduleur est joignable. Si le nouvel onduleur a une autre adresse, vous saisissez l'adresse à l'étape suivante.
2. Ouvrez Configurer, l'engrenage sur la ligne du système dans la page de l'intégration SAJ Local.
3. Modifiez l'hôte, le port ou l'ID d'unité si l'adresse a changé. Laissez Modèle sur Automatique, ou choisissez le modèle si l'onduleur n'est pas reconnu.
4. Choisissez Soumettre, puis confirmez le remplacement. La confirmation nomme le modèle et le numéro de série que SAJ Local a trouvés.

Après votre confirmation, l'appareil, les entités, les noms des entités et l'historique restent avec le système. Une entité conserve l'historique d'un modèle à l'autre quand les deux modèles ont l'entité. SAJ Local oublie l'équipement détecté sur l'ancien onduleur et le nombre de modules de batterie de l'ancien onduleur, et détecte de nouveau l'équipement sur le nouvel onduleur.

## Quand l'onduleur à l'adresse change sans vous

SAJ Local vérifie l'identité de l'onduleur chaque fois que le système se charge. Quand l'onduleur à l'adresse s'identifie comme un autre modèle, ou a un autre numéro de série, SAJ Local ne charge pas le système et déclenche un problème de réparation. Le correctif du problème de réparation montre le modèle et le numéro de série que l'onduleur signale maintenant, et adopte l'onduleur que vous confirmez.

- Les ID d'entité, l'historique, Autoriser le contrôle et tous les autres réglages restent inchangés.
- Quand l'onduleur signale autre chose que ce que le formulaire montrait, le formulaire le dit et montre les nouvelles valeurs au lieu d'enregistrer les anciennes.
- Quand l'appareil à l'adresse n'est pas un modèle reconnu, un problème de réparation le dit et renvoie vers Configurer. Il n'y a rien à adopter. Choisissez le modèle à la main, voir la [prise en main](getting-started.md#quand-londuleur-nest-pas-reconnu).

Les problèmes de réparation sont listés dans [défauts et réparations](faults-and-repairs.md#problèmes-de-réparation).

## Pas encore pris en charge

- Adopter un onduleur qui appartient déjà à un autre système. SAJ Local refuse l'adoption.
