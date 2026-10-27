[en](../../en-gb/user/installation.md) | [de](../../de/user/installation.md) | [nl](../../nl/user/installation.md) | fr | [zh](../../zh-hans/user/installation.md) | [es](../../es/user/installation.md) | [it](../../it/user/installation.md) | [pl](../../pl/user/installation.md) | [sv](../../sv/user/installation.md)

# Installation

La page Installation installe SAJ Local avec HACS, le Home Assistant Community Store. La liste complète de ce que fait la configuration se trouve dans la section [Configuration et détection](../../../custom_components/saj_local/docs/features.md#setup-and-detection) de la liste des fonctionnalités de l'intégration.

SAJ Local n'a pas encore de version publiée. Consultez les [équipements pris en charge](supported-equipment.md) avant d'installer.

## Ce dont vous avez besoin

- Home Assistant à la version minimale indiquée dans [`hacs.json`](../../../hacs.json), et HACS.
- Un onduleur SAJ pris en charge qui répond en Modbus TCP sur votre réseau local. Il vous faut l'adresse de l'onduleur, ainsi que le port et l'ID d'unité lorsque le port ou l'ID d'unité n'est pas la valeur par défaut.
- Rien d'autre. SAJ Local communique directement avec l'onduleur et n'envoie rien à un service cloud.

## Installer

1. Ouvrez SAJ Local dans HACS avec le premier bouton ci-dessous. HACS vous demande d'ajouter le dépôt si le dépôt n'est pas encore listé.
2. Téléchargez SAJ Local dans HACS.
3. Redémarrez Home Assistant.
4. Ajoutez votre système avec le second bouton ci-dessous, ou suivez la [prise en main](getting-started.md).

[![Ouvrir votre instance Home Assistant et ouvrir le dépôt SAJ Local dans HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Counterphase-Labs&repository=ha-saj-local&category=integration)
[![Ouvrir votre instance Home Assistant et commencer la configuration de SAJ Local.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=saj_local)

SAJ Local fournit lui-même les cartes du tableau de bord, il n'y a donc aucune ressource de carte à ajouter. Voir les [cartes du tableau de bord](cards/README.md).

## Versions bêta

Jusqu'à la première version stable, chaque version de SAJ Local est une bêta. Dans HACS, ouvrez SAJ Local, ouvrez le menu, choisissez Télécharger à nouveau, activez « Afficher les versions bêta » et téléchargez la bêta la plus récente. Sans cet interrupteur, HACS installe la version de développement de SAJ Local.
