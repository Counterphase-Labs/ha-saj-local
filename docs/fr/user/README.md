[en](../../en-gb/user/README.md) | [de](../../de/user/README.md) | [nl](../../nl/user/README.md) | fr | [zh](../../zh-hans/user/README.md) | [es](../../es/user/README.md) | [it](../../it/user/README.md) | [pl](../../pl/user/README.md) | [sv](../../sv/user/README.md)

# Documentation utilisateur de SAJ Local

SAJ Local est une intégration locale pour Home Assistant. SAJ Local lit un système solaire SAJ HS3 ou H2 directement sur l'onduleur, en Modbus TCP sur votre propre réseau et, lorsque vous autorisez le contrôle, modifie les réglages de l'onduleur depuis Home Assistant. SAJ Local n'a besoin d'aucun compte cloud et limite les requêtes envoyées à l'onduleur pour que le module de communication de l'onduleur continue de fonctionner.

SAJ Local est une intégration non officielle, développée par la communauté. SAJ ne fabrique pas SAJ Local, ne le prend pas en charge et ne l'approuve pas. Voir l'[avis de non-responsabilité](#avis-de-non-responsabilité).

SAJ Local est en développement et n'a pas encore de version publiée. Chaque page ci-dessous indique ce qui n'est pas encore pris en charge. La documentation couvre le HS3 et le H2, et signale les différences par une note comme « HS3 uniquement ». Les captures d'écran proviennent de systèmes simulés, les mesures ne sont donc pas réelles.

## Pour commencer

1. [Installer SAJ Local](installation.md) avec HACS.
2. Vérifiez que votre onduleur figure dans les [équipements pris en charge](supported-equipment.md).
3. [Prise en main](getting-started.md) : ajoutez votre premier système.
4. Lisez la page sur l'[équipement optionnel](optional-equipment.md), que SAJ Local détecte pour vous.

## Comprendre votre système

- [Entités et préfixe](entities-and-prefix.md) : ce que sont les entités, comment les ID d'entité sont formés et comment ajouter un préfixe.
- [Référence des entités](entities/README.md) : chaque entité, avec l'ID d'entité, les modèles, l'équipement et la valeur par défaut. Générée à partir de l'intégration.
- [Interrogation](polling.md) : la fréquence de lecture de l'onduleur, et comment lire certaines entités plus vite ou plus lentement.
- [Protéger l'onduleur](protecting-the-inverter.md) : les limites que SAJ Local applique à ses propres requêtes.

## Modifier les réglages

- [Modifier les réglages](changing-settings.md) : autoriser le contrôle, modifier les réglages et utiliser l'EMS.
- [Pilotage de puissance](power-control.md) : maintenir la batterie, le raccordement au réseau ou l'onduleur à une puissance fixée, à la main ou avec un programme.
- [Remplacer l'onduleur](replacing-the-inverter.md) : passer un système à un nouvel onduleur, ou entre un H2 et un HS3, en conservant l'historique.

## Tableaux de bord

- [Cartes du tableau de bord](cards/README.md) : les cartes, la fonctionnalité de carte tuile et le badge que SAJ Local ajoute à Home Assistant.

## Termes

- [Nomenclature](nomenclature.md) : les termes SAJ et Home Assistant que l'intégration, les cartes et la documentation utilisent, avec leur signification.

## En cas de problème

- [Défauts de l'équipement et réparations](faults-and-repairs.md) : les défauts que l'équipement signale et les problèmes de réparation que SAJ Local déclenche.
- [Dépannage](troubleshooting.md) : diagnostics, journalisation de débogage et où demander de l'aide.

## Ce que chaque partie sait faire

Les listes de fonctionnalités indiquent ce qui est construit aujourd'hui : [l'intégration](../../../custom_components/saj_local/docs/features.md) et [les cartes](../../../frontend/docs/features.md).

Développeurs : voir la [documentation développeur](../developer/README.md).

## Avis de non-responsabilité

SAJ Local est une intégration indépendante, développée par la communauté. SAJ Local n'est pas affilié à SAJ (Guangzhou Sanjing Electric Co., Ltd.), et SAJ ainsi que les filiales et sociétés affiliées de SAJ n'ont ni autorisé, ni parrainé, ni approuvé SAJ Local.

SAJ, le logo SAJ et tous les noms de produits, noms de modèles et marques associés sont la propriété de leurs détenteurs respectifs. La documentation n'emploie ces noms que pour identifier l'équipement avec lequel SAJ Local fonctionne.

Le logiciel est fourni tel quel, sans garantie d'aucune sorte. Vous utilisez SAJ Local à vos propres risques : les auteurs déclinent toute responsabilité en cas de dommage à l'équipement, de perte de données, de perte de garantie ou de toute autre conséquence de l'utilisation de SAJ Local. Cet avertissement s'applique en particulier à l'écriture de réglages dans votre onduleur.

## Remerciements

La prise en charge du H2 s'appuie sur les recherches sur les registres et les essais sur le terrain de stanus74 dans [SAJ H2 Modbus](https://github.com/stanus74/home-assistant-saj-h2-modbus). Merci.
