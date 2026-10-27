[en](../../en-gb/user/protecting-the-inverter.md) | [de](../../de/user/protecting-the-inverter.md) | [nl](../../nl/user/protecting-the-inverter.md) | fr | [zh](../../zh-hans/user/protecting-the-inverter.md) | [es](../../es/user/protecting-the-inverter.md) | [it](../../it/user/protecting-the-inverter.md) | [pl](../../pl/user/protecting-the-inverter.md) | [sv](../../sv/user/protecting-the-inverter.md)

# Protéger l'onduleur

La page Protéger l'onduleur liste les limites que SAJ Local applique à tout ce que SAJ Local envoie, pour que le module de communication de l'onduleur continue de servir Home Assistant. Un module peut cesser de servir un client qui l'interroge trop fort, aucun réglage ne supprime donc une limite. La liste complète se trouve dans la section [Protection de l'onduleur](../../../custom_components/saj_local/docs/features.md#protecting-the-inverter) de la liste des fonctionnalités de l'intégration.

## Les limites

- **Une connexion, une requête à la fois.** SAJ Local ouvre une connexion vers un onduleur et attend chaque réponse avant d'envoyer la requête suivante, avec une courte pause entre les requêtes.
- **40 requêtes en 60 secondes, quelle que soit la fenêtre.** La limite s'applique par adresse d'onduleur. SAJ Local compte d'un rechargement à l'autre, donc un rechargement, une nouvelle tentative de configuration ou une vérification de connexion ne peut pas dépasser la limite. Une requête au-delà de la limite attend.
- **Les registres voisins partagent une requête.** SAJ Local lit les registres proches les uns des autres en une seule requête, jamais au-delà d'un bloc que le modèle documente. Une requête n'est jamais plus grande que 32 registres sur le HS3 ou 56 sur le H2. Regrouper les entités qui sont côte à côte coûte moins, voir l'[interrogation](polling.md).
- **Aucune nouvelle tentative dans un cycle.** Après une lecture échouée, l'attente avant la tentative suivante double à partir du plus court intervalle, jusqu'à 5 minutes. L'attente survit aux rechargements. Le premier bon cycle relit tout.
- **Chaque attente a une limite de temps.** Un onduleur bloqué met fin à un cycle comme un échec et n'arrête pas l'interrogation. Une réponse tardive ou parasite est écartée.
- **Une connexion fermée est rouverte une fois.** Ce cycle relit alors chaque entité activée, pour qu'aucune valeur ne soit plus ancienne que la reconnexion.
- **Au plus 20 changements en 60 secondes.** Voir [modifier les réglages](changing-settings.md#ce-qui-arrive-à-un-changement). Un changement au-delà de la limite est refusé et non mis en file d'attente.

## Quand l'onduleur refuse une lecture

Un refus est une réponse et non un échec. Seules les entités de la requête refusée deviennent indisponibles, et les autres continuent de se mettre à jour.

1. SAJ Local coupe la requête refusée en deux moitiés au fil des cycles suivants, jusqu'à trouver l'entité refusée.
2. Une entité refusée trois fois de suite est suspendue. L'entité s'affiche comme indisponible et n'est plus lue.
3. SAJ Local réessaie une entité suspendue une fois par jour, et chaque fois que l'intégration se charge. L'entité revient quand le registre répond.
4. Un problème de réparation liste les entités suspendues. Le correctif du problème désactive les entités, pour que SAJ Local ne lise plus les entités définitivement. Voir [défauts et réparations](faults-and-repairs.md#problèmes-de-réparation).

## Quand l'onduleur cesse de répondre

Un problème de réparation indique quand un onduleur n'a pas répondu depuis 15 minutes. Le problème disparaît à la première bonne lecture. Vérifiez l'alimentation de l'onduleur et du module de communication, le réseau, et qu'aucun autre client Modbus ne tient la connexion.

## Pas encore pris en charge

- Modifier les limites. Les limites protègent l'onduleur, aucun réglage ne relève donc une limite.
