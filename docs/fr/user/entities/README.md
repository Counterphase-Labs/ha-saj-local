[en](../../../en-gb/user/entities/README.md) | [de](../../../de/user/entities/README.md) | [nl](../../../nl/user/entities/README.md) | fr | [zh](../../../zh-hans/user/entities/README.md) | [es](../../../es/user/entities/README.md) | [it](../../../it/user/entities/README.md) | [pl](../../../pl/user/entities/README.md) | [sv](../../../sv/user/entities/README.md)

# Entités

Toutes les entités que SAJ Local peut créer, une page par zone. La section [Appareils et entités](../../../../custom_components/saj_local/docs/features.md#devices-and-entities) de la liste des fonctionnalités de l'intégration explique les types d'entités, les entités activées par défaut et le signe des mesures de puissance.

Un système n'obtient que les entités qui correspondent à son modèle, à son équipement installé et à son nombre de phases, de chaînes solaires et de modules de batterie. La colonne Modèles indique quels modèles ont une entité, et la colonne Équipement et nombres indique ce qui doit être installé.

Généré par `make docs`. Ne pas modifier à la main.

| Zone | Entités | Contenu |
| --- | --- | --- |
| [Onduleur et solaire](inverter-and-pv.md) | 244 | Sortie de l'onduleur, chaînes solaires, port de secours, compteurs d'énergie, versions et charge domestique |
| [Réseau et compteur A](grid-and-meter-a.md) | 101 | Le raccordement au réseau et le compteur A, le compteur du réseau |
| [Compteur B](meter-b.md) | 22 | Le compteur B, le second compteur qui mesure un onduleur solaire |
| [Batterie](battery.md) | 138 | La batterie dans son ensemble |
| [Modules de batterie](battery-packs.md) | 58 | Mesures et identité de chaque module de batterie |
| [Chargeur de VE](ev-charger.md) | 87 | Le chargeur de VE et ses commandes de charge |
| [Système en parallèle](parallel-system.md) | 63 | Les mesures d'un système de machines en parallèle |
| [Réglages](settings.md) | 22 | Réglages et commandes qui modifient l'onduleur |
| [Défauts](faults.md) | 139 | Défauts que l'onduleur, la batterie et le chargeur de VE signalent |
| [Ajoutées par l'intégration](added-by-the-integration.md) | 7 | Entités que l'intégration ajoute en dehors du catalogue de registres |
