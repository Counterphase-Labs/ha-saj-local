[en](../../../en-gb/user/cards/README.md) | [de](../../../de/user/cards/README.md) | [nl](../../../nl/user/cards/README.md) | fr | [zh](../../../zh-hans/user/cards/README.md) | [es](../../../es/user/cards/README.md) | [it](../../../it/user/cards/README.md) | [pl](../../../pl/user/cards/README.md) | [sv](../../../sv/user/cards/README.md)

# Cartes du tableau de bord

La page Cartes du tableau de bord explique comment ajouter les cartes de SAJ Local à un tableau de bord et choisir un système, et liste ce que chaque élément affiche. Les listes complètes se trouvent dans les sections [Éléments et configuration](../../../../frontend/docs/features.md#elements-and-setup) et [Thème et langue](../../../../frontend/docs/features.md#theme-and-language) de la liste des fonctionnalités des cartes, et dans la section [Cartes](../../../../custom_components/saj_local/docs/features.md#cards) de la liste des fonctionnalités de l'intégration.

SAJ Local fournit les cartes et les enregistre auprès de Home Assistant au démarrage de Home Assistant. Les cartes apparaissent dans le sélecteur de cartes, il n'y a donc aucune ressource à ajouter et aucun cache à vider.

## Éléments

| Élément | Ce que l'élément affiche |
| --- | --- |
| [Carte de flux de puissance](power-flow-card.md) | La puissance en direct entre le solaire, la batterie, le réseau, la maison et l'équipement optionnel. |
| [Carte d'état](status-card.md) | L'état de fonctionnement, le mode d'application, les mesures clés, l'énergie du jour, un résumé des défauts et si le contrôle est autorisé. |
| [Carte des défauts](faults-card.md) | Les défauts actifs de chaque équipement, et un bouton Effacer le défaut. |
| [Carte de batterie](battery-card.md) | L'état de charge avec les limites marquées, les mesures de la batterie et un groupe de lignes pour chaque module. |
| [Carte de contrôle](controls-card.md) | Les réglages du système en sections. |
| [Carte de programme](schedule-card.md) | Les plages de charge, de décharge et de chargeur de VE, une chronologie de la semaine et un éditeur de plage. |
| [Fonctionnalité de carte tuile Jours de la semaine](weekdays-feature.md) | Sept boutons de jour sur une carte tuile, pour les jours d'une plage. |
| [Badge d'état](status-badge.md) | Un badge avec l'état de fonctionnement et le nombre d'équipements ayant un défaut actif. |

## Ajouter un élément

1. Modifiez un tableau de bord et choisissez Ajouter une carte. Pour la fonctionnalité Jours de la semaine, ajoutez une carte tuile et ouvrez les fonctionnalités de la carte tuile. Pour le badge, modifiez les badges du tableau de bord.
2. Choisissez l'élément SAJ Local dans le sélecteur. Les six cartes affichent un aperçu en direct.
3. Choisissez le système dans le champ Système de l'éditeur visuel. Une nouvelle carte ou un nouveau badge démarre avec le premier système. La fonctionnalité Jours de la semaine n'a pas d'éditeur, car la fonctionnalité utilise l'entité de la carte tuile.

Une maison avec deux systèmes ajoute une carte une fois par système. Le titre d'une carte est le nom de l'appareil du système suivi du modèle, par exemple SAJ HS3 (12000 W). SAJ Local n'ajoute le numéro de série que lorsque deux systèmes auraient sinon un titre identique. Renommez chaque appareil dans Home Assistant si vous voulez d'autres titres.

Les éléments trouvent les entités d'un système par le registre des entités, et non par l'ID d'entité, les éléments continuent donc de fonctionner quand vous modifiez un [préfixe](../entities-and-prefix.md#le-préfixe).

## Ce que fait chaque élément

- **Seulement ce que le système a.** Une partie dont l'entité n'existe pas ou est désactivée n'est pas dessinée, chaque carte n'affiche donc que ce que le système a. Une partie propre à un modèle n'apparaît que sur ce modèle, et la page de chaque élément nomme les parties.
- **Une carte vide dit pourquoi.** Une carte dont aucune entité n'est activée indique quel type d'entité activer, avec un lien vers la page de l'appareil du système.
- **Un système qui ne répond pas.** Une carte le dit et atténue les valeurs.
- **Appuyer sur une valeur.** Appuyer sur une valeur ouvre les détails de l'entité dans Home Assistant.
- **Commandes verrouillées.** Tant qu'[Autoriser le contrôle](../changing-settings.md#autoriser-le-contrôle) est désactivé pour le système, chaque commande est désactivée et un cadenas renvoie vers les paramètres de l'intégration. Activer Autoriser le contrôle active aussi les entités dont les cartes ont besoin, voir [l'ensemble de contrôle](../changing-settings.md#lensemble-de-contrôle).
- **Un changement par décision.** Un curseur modifie l'onduleur quand vous relâchez le curseur. Un champ numérique modifie l'onduleur à la touche Entrée ou quand vous quittez le champ. Une liste, un interrupteur ou un champ d'heure modifie l'onduleur au changement. La commande affiche ensuite la valeur que l'onduleur détient, et un refus apparaît sous la commande dans les mots de l'intégration.

## Thème et langue

Les éléments suivent le thème de Home Assistant. Les noms des entités, les valeurs et les états utilisent le formatage et la langue de Home Assistant. Les textes des cartes existent en anglais, allemand, néerlandais, français, chinois simplifié, espagnol, italien, polonais et suédois. Un tableau de bord dans une autre langue affiche les textes des cartes en anglais.

## Pas encore pris en charge

- Les textes des cartes dans des langues autres que les neuf ci-dessus.
