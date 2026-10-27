[en](../../README.md) | [de](../de/README.md) | [nl](../nl/README.md) | fr | [zh](../zh-hans/README.md) | [es](../es/README.md) | [it](../it/README.md) | [pl](../pl/README.md) | [sv](../sv/README.md)

# Intégration SAJ Local pour Home Assistant

![SAJ Local](../../images/header.png)

[![HACS personnalisé](https://img.shields.io/badge/HACS-personnalis%C3%A9-41BDF5.svg)](https://hacs.xyz)
[![Home Assistant](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FCounterphase-Labs%2Fha-saj-local%2Fmain%2Fhacs.json&query=%24.homeassistant&suffix=%2B&label=Home%20Assistant&logo=homeassistant&logoColor=white&color=41BDF5)](https://www.home-assistant.io)
[![Publication](https://img.shields.io/github/v/release/Counterphase-Labs/ha-saj-local?label=Publication)](https://github.com/Counterphase-Labs/ha-saj-local/releases)
[![Installations actives](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fanalytics.home-assistant.io%2Fcustom_integrations.json&query=%24.saj_local.total&label=Installations%20actives&logo=homeassistant&logoColor=white&color=41BDF5)](https://analytics.home-assistant.io)
[![Vérifications](https://github.com/Counterphase-Labs/ha-saj-local/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Counterphase-Labs/ha-saj-local/actions/workflows/ci.yml)
[![Licence](https://img.shields.io/github/license/Counterphase-Labs/ha-saj-local?label=Licence)](../../LICENSE)

⭐ [Mettez une étoile au projet sur GitHub](https://github.com/Counterphase-Labs/ha-saj-local) : votre soutien est une vraie motivation ! 🙏😊

Votre installation solaire SAJ dans Home Assistant, lue directement depuis l'onduleur sur votre propre réseau. Pas de compte cloud, pas d'application du fabricant au milieu, et une approche d'interrogation conçue pour ménager le matériel.

Il s'agit d'une intégration non officielle, développée par la communauté. Elle n'est ni conçue, ni prise en charge, ni approuvée par SAJ. Voir l'[avis de non-responsabilité](user/README.md#avis-de-non-responsabilité).

> **Statut : en développement actif et pas encore publiée.** Il n'existe pas encore de version publiée.

## Pourquoi SAJ Local

- **Des réglages par défaut sensés.** Ajoutez votre onduleur et obtenez une configuration qui fonctionne, sans parcourir des pages d'options. L'onduleur, la batterie et l'équipement associé sont détectés automatiquement.
- **Ménage votre onduleur.** Une connexion et une requête à la fois, et un plafond strict de requêtes qu'aucun réglage, rechargement ou défaut ne peut dépasser. Vous choisissez ce qui est lu et à quelle fréquence.
- **Lecture seule, sauf avis contraire.** L'écriture est facultative pour chaque installation, de sorte que rien ne change sur votre onduleur par accident.
- **Les mêmes noms sur tous les modèles.** Les tableaux de bord et les automatisations s'écrivent une seule fois, continuent de fonctionner sur tous les modèles SAJ et survivent au passage d'un H2 à un HS3.
- **Plusieurs systèmes.** Connectez plus d'un système SAJ au même Home Assistant.
- **Cartes de tableau de bord.** Des cartes pour consulter des informations et pour modifier la configuration, ajoutées depuis le sélecteur de cartes.
- **Des erreurs claires et des diagnostics sûrs.** Quand quelque chose se passe mal, on vous dit quoi et pourquoi, et les exports de débogage sont conçus pour pouvoir être partagés sans risque.
- **Entièrement local.** Tout communique avec votre onduleur sur votre réseau. Rien n'est envoyé à un service cloud.

## Équipement pris en charge

Le SAJ HS3 et le SAJ H2 monophasé sont pris en charge. Voir [équipement pris en charge](user/supported-equipment.md) pour la liste complète et ce qui n'est pas encore pris en charge.

## Documentation

- [Documentation utilisateur](user/README.md) : installer, configurer et utiliser SAJ Local.
- [Documentation développeur](developer/README.md) : comment SAJ Local est construit, vérifié et publié.
- [Contribuer](../../CONTRIBUTING.md) : préparer une copie de travail et envoyer une modification.

## Aide et retours

Les questions, les rapports de bogue et les idées sont les bienvenus sur le [suivi des tickets](https://github.com/Counterphase-Labs/ha-saj-local/issues).

Signalez un problème de sécurité en privé, voir la [politique de sécurité](../../SECURITY.md).

## Licence

[MIT](../../LICENSE)
