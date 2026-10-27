[en](../../en-gb/user/supported-equipment.md) | [de](../../de/user/supported-equipment.md) | [nl](../../nl/user/supported-equipment.md) | fr | [zh](../../zh-hans/user/supported-equipment.md) | [es](../../es/user/supported-equipment.md) | [it](../../it/user/supported-equipment.md) | [pl](../../pl/user/supported-equipment.md) | [sv](../../sv/user/supported-equipment.md)

# Équipements pris en charge

La page Équipements pris en charge liste les produits SAJ que SAJ Local prend en charge, l'équipement optionnel que chaque modèle peut avoir et ce qui n'est pas encore pris en charge. La liste complète de ce que fait la configuration se trouve dans la section [Configuration et détection](../../../custom_components/saj_local/docs/features.md#setup-and-detection) de la liste des fonctionnalités de l'intégration.

## Modèles pris en charge

SAJ Local reconnaît un modèle d'après le type d'appareil que l'onduleur signale. Tout autre type d'appareil n'est pas reconnu.

| Modèle | Reconnu comme | Équipement optionnel que SAJ Local détecte |
| --- | --- | --- |
| HS3 | Type d'appareil `0x1610`, trois phases | Batterie, compteur A, compteur B, chargeur de VE, système en parallèle |
| H2, monophasé, deux chaînes solaires | Type d'appareil `0x005a` | Batterie, compteur A, compteur B, système en parallèle |
| H2, monophasé, trois chaînes solaires | Type d'appareil `0x005b` | Batterie, compteur A, compteur B, système en parallèle |

Les différences entre les modèles que vous voyez à l'usage :

- **Chargeur de VE :** le HS3 uniquement. Le H2 n'a ni entités de chargeur de VE, ni plages de chargeur de VE, ni section Chargeur de VE sur la carte de contrôle.
- **Modules de batterie :** un H2 a des entités pour jusqu'à cinq modules de batterie. Un HS3 a des entités pour un module de batterie. Voir l'[équipement optionnel](optional-equipment.md).
- **EMS :** le HS3 uniquement. Voir [modifier les réglages](changing-settings.md#ems).
- **Pilotage de puissance :** le HS3 propose Batterie, Réseau et Onduleur. Le H2 propose Batterie uniquement. Voir le [pilotage de puissance](power-control.md).

L'[équipement optionnel](optional-equipment.md) explique comment la détection fonctionne et comment la remplacer. La [référence des entités](entities/README.md) liste le modèle et l'équipement dont chaque entité a besoin.

## Pas encore pris en charge

- La détection automatique ne reconnaît que les trois types d'appareil du tableau. Les autres produits SAJ, comme le HS2, le H1 et l'AS1, ne sont pas reconnus.
- Les autres variantes du H2, comme le H2 triphasé, signalent d'autres types d'appareil et ne sont pas reconnues automatiquement. Vous pouvez choisir le modèle à la main, et SAJ Local marque alors le modèle comme non vérifié. Les mesures peuvent être erronées, car SAJ Local ne peut pas les vérifier. Voir la [prise en main](getting-started.md#quand-londuleur-nest-pas-reconnu).
- Modifier les réglages d'un système dont le modèle est non vérifié. La lecture fonctionne, et chaque changement est refusé.

## Sur quoi repose la prise en charge

La prise en charge du HS3 a été vérifiée à la main sur un vrai HS3. La prise en charge du H2 repose sur la documentation du protocole SAJ et sur des retours du terrain, et n'a pas été vérifiée à la main sur un H2. L'écriture de réglages et le pilotage de puissance sur le H2 reposent aussi sur la documentation et sur des retours du terrain.
