[en](../../en-gb/developer/frontend.md) | [de](../../de/developer/frontend.md) | [nl](../../nl/developer/frontend.md) | fr | [zh](../../zh-hans/developer/frontend.md) | [es](../../es/developer/frontend.md) | [it](../../it/developer/frontend.md) | [pl](../../pl/developer/frontend.md) | [sv](../../sv/developer/frontend.md)

# Frontend

Comment le bundle des cartes est organisé et compilé, et comment voir chaque carte dans l'instance de développement.

La liste complète de ce que couvre le frontend se trouve dans les sections de la liste des fonctionnalités [Cartes](../../../custom_components/saj_local/docs/features.md#cards) de l'intégration et [Éléments et configuration](../../../frontend/docs/features.md#elements-and-setup) et [Thème et langue](../../../frontend/docs/features.md#theme-and-language) des cartes.

## Compilation

Les cartes, la fonctionnalité de carte tuile et le badge forment un seul bundle Lit et TypeScript sous `frontend/`. `make build` exécute Vite et écrit le bundle dans `custom_components/saj_local/frontend/` sous la forme `saj-local-<hash>.js` avec un `asset-manifest.json`, car HACS livre le répertoire de l'intégration comme une seule archive. Git suit le bundle compilé et le manifeste, une modification des cartes est donc validée avec une nouvelle compilation. L'intégration lit le manifeste, sert le fichier que le manifeste nomme et ajoute l'URL du fichier au frontend de Home Assistant, les utilisateurs n'ajoutent donc aucune ressource de tableau de bord.

Le hash change à chaque compilation pour qu'un navigateur n'exécute jamais un bundle périmé. Le coût est que Home Assistant enregistre le nom de fichier avec hash une seule fois, au démarrage : un nouveau bundle demande un redémarrage de Home Assistant avant que le navigateur se voie proposer le nouveau fichier. L'instance de développement monte le répertoire de l'intégration, exécutez donc `make build` et redémarrez Home Assistant pour voir une modification.

## Organisation des sources

L'organisation suit ce qui change ensemble :

- `src/system/` contient tout ce qui n'est pas du dessin : trouver les entités d'un système dans `hass`, le sens de la puissance, les jours de la semaine, les plages horaires, les défauts, le verrou de contrôle et les appels de service. Le dossier ne touche jamais au DOM, les règles sont donc testées sans navigateur.
- `src/ui/` contient les parties que chaque carte dessine, stylées uniquement avec les variables de thème de Home Assistant, car le frontend de Home Assistant ne promet aucun élément `ha-*` aux cartes personnalisées.
- `src/cards/`, `src/features/` et `src/badges/` contiennent les éléments et enregistrent les éléments auprès du sélecteur de Home Assistant.
- `src/i18n/` contient les textes dont seules les cartes ont besoin, un fichier par langue, nommé d'après le code de langue de Home Assistant comme les fichiers du dossier `translations/` de l'intégration (l'anglais et les huit langues cibles), avec l'anglais comme repli pour toute autre langue. Les noms des entités, les états et les valeurs viennent de Home Assistant.
- `tests/fakes/` contient un faux `hass`, construit à partir d'une liste d'entités, et les remplacements des modules qu'un élément utilise. Chaque test unitaire exerce un module dont chaque collaborateur est remplacé par l'un des faux.

Un élément trouve les entités d'un système par l'appareil et la clé de traduction, jamais par l'ID d'entité, une carte ne dépend donc jamais d'un préfixe d'ID d'entité.

## Tests

`make test-frontend` exécute les tests unitaires Vitest avec le seuil de couverture. `make test-browser-controlled` exécute Playwright sur le bundle compilé avec des données contrôlées, et `make test-browser-home-assistant` exécute Playwright sur un vrai Home Assistant, voir la [page des vérifications](checks.md#cibles-make). Les captures d'écran de la documentation utilisateur viennent d'une troisième configuration Playwright, voir [Captures d'écran](documentation.md#captures-décran).

## Tableaux de bord de démonstration

Voir chaque carte avec chaque option demande un Home Assistant avec de vrais systèmes, l'environnement de développement déclare donc deux tableaux de bord, `saj-hs3` et `saj-h2`, à partir de `config/dashboards/saj-hs3.yaml` et `config/dashboards/saj-h2.yaml`, par le bloc `lovelace: dashboards:` de `config/configuration.yaml`. Les tableaux de bord sont du YAML simple écrit à la main, et aucun script ne génère les tableaux de bord. Chaque élément SAJ Local est un élément personnalisé configuré par son propre YAML, donc chaque carte, fonctionnalité de carte tuile et badge est écrit individuellement avec chaque option définie, sous un titre qui nomme la carte et ses options.

- Chaque tableau de bord a quatre vues : Dashboard (les cartes d'un tableau de bord de système typique, écrites comme des cartes simples), Cards (chaque carte dans chacune de ses combinaisons d'options), Features and badges (une carte tuile avec la fonctionnalité `custom:saj-local-weekdays-feature` pour chaque entité de jours de plage, et le badge d'état) et Empty states (chaque carte sans `device` et avec l'appareil de quelque chose qui n'est pas SAJ Local).
- Les tableaux de bord contiennent les ID d'appareil d'une instance de développement. Un développeur dont l'instance a d'autres ID d'appareil remplace les deux ID `device` de chaque fichier, l'ID du système et l'ID d'un appareil qui n'est pas SAJ Local pour la vue Empty states, ainsi que les ID d'entité des jours de plage quand le préfixe d'ID d'entité diffère.
- Home Assistant lit les déclarations de tableaux de bord au démarrage de Home Assistant, redémarrez donc Home Assistant après avoir modifié `config/configuration.yaml`. Une modification d'un fichier de tableau de bord apparaît après un rechargement de la page.
