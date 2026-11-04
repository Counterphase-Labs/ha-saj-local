[en](../../en-gb/developer/checks.md) | [de](../../de/developer/checks.md) | [nl](../../nl/developer/checks.md) | fr | [zh](../../zh-hans/developer/checks.md) | [es](../../es/developer/checks.md) | [it](../../it/developer/checks.md) | [pl](../../pl/developer/checks.md) | [sv](../../sv/developer/checks.md)

# Vérifications

Ce que lance chaque cible make, comment restreindre une exécution et les règles que suit chaque vérification.

## Cibles make

Chaque action est une cible make et la CI appelle les mêmes cibles, réussir en local et réussir en CI signifient donc la même chose. Une nouvelle étape de CI commence comme une cible make. `make help` liste chaque cible en une ligne, et `make help ARGS=<cible>` décrit une cible : ce que la cible lance, ce que la cible affiche en cas de succès et en cas d'échec, ce que fait `ARGS` et, pour une cible de regroupement, les étapes que la cible lance.

`make ci` lance chaque étape de vérification et définit ce qu'est « terminé ». GitHub lance `make ci` lui-même dans l'unique job `checks` de [ci.yml](../../../.github/workflows/ci.yml), à côté des jobs partagés de `roquerodrigo/workflows` (`lint`, `tests`, `validate`), une étape ajoutée à `make ci` s'exécute donc dans GitHub sans modifier le workflow. Lancez les cibles plus étroites pendant que vous itérez.

`make build` est l'unique compilation de production du frontend. `make test` lance chaque suite de tests, et chaque suite a sa propre cible pour pouvoir lancer une suite seule :

| Cible | Suite |
| --- | --- |
| `make test-python` | Les tests unitaires pytest de la bibliothèque, de l'intégration, du simulateur et de l'exécuteur de vérifications, sans `tests/mock-integration` ni `tests/scripts/test_runner_processes.py`, avec le seuil de couverture de 100 % des lignes et des branches. Une exécution complète est deux exécutions de pytest vers un seul fichier de données de couverture, avec le cœur `ctrace` et un contexte de couverture par test : `tests/saj`, `tests/mock` et `tests/scripts` sans le plugin Home Assistant et avec les sockets bloqués, puis `tests/saj-integration` avec le plugin et le seuil sur les données combinées. L'étape échoue aussi pour le corps de tout test qui dépasse 200 ms, la préparation et le nettoyage des fixtures n'étant pas comptés. |
| `make test-frontend` | Les tests unitaires Vitest des cartes, avec le seuil de couverture. |
| `make test-modules` | Chaque module avec de la logique (toute fonction, méthode ou branche) face aux seuls fichiers de tests unitaires associés au module, avec 100 % de couverture des lignes et des branches exigé par module. Le seuil lit les données de couverture de `make test-python`, donc `make test-modules` lance d'abord `make test-python`. Un module avec de la logique et sans fichier de tests unitaires échoue, et un module sans logique, comme un module vide ou une table de données, est ignoré. |
| `make test-isolated` | Les tests de `tests/saj` et `tests/mock` dans un environnement sans Home Assistant, ce qui prouve la frontière entre la bibliothèque, le simulateur et Home Assistant. La couverture est contrôlée sur les modules que testent les fichiers de tests. |
| `make test-runner-processes` | Les tests à processus réels de l'exécuteur de vérifications dans `tests/scripts/test_runner_processes.py`, qui lancent de vrais processus et sont hors couverture. |
| `make test-browser-controlled` | Playwright sur le bundle compilé et des données contrôlées, sans Home Assistant. |
| `make test-browser-home-assistant` | Playwright sur un Home Assistant jetable avec un simulateur HS3 et un simulateur H2, ce qui prouve que les cartes se chargent et fonctionnent dans le vrai frontend. La cible lance d'abord `make build` et `make mock-build`, car l'image de Home Assistant copie le bundle des cartes depuis l'arbre de travail et les simulateurs utilisent l'image `saj-local-mock`. |
| `make mock-smoke` | Le conteneur du simulateur répond à un client, puis les tests de `tests/mock-integration` s'exécutent. La cible lance d'abord `make mock-build` et exécute les scénarios depuis l'image `saj-local-mock`. |

Les vérifications qui composent `make ci` ont aussi chacune une cible, pour pouvoir lancer un outil seul :

| Cible | Vérification |
| --- | --- |
| `make ruff` | `ruff format --check` et `ruff check`. |
| `make mypy` | La vérification stricte des types. |
| `make import-lint` | Les contrats d'import-linter. |
| `make complexipy` | La limite de complexité cognitive. |
| `make copy-paste` | La détection de code et de texte dupliqués par jscpd, sur tout le dépôt y compris `docs/`. |
| `make prettier`, `make tsc`, `make eslint` | Mise en forme, vérification des types et lint du frontend. |
| `make build` | La compilation de production Vite du frontend. |
| `make release-check` | L'archive HACS contient `asset-manifest.json` et le bundle compilé des cartes. L'archive est faite à partir des fichiers de `custom_components/saj_local/`, le bundle compilé doit donc être dans l'arbre. La version dans `custom_components/saj_local/manifest.json`, `pyproject.toml` et `frontend/package.json` est `X.Y.Z` ou `X.Y.ZbN` et identique dans les trois fichiers, et un tag sur `HEAD` est égal à la version. Sans tag sur `HEAD`, la comparaison avec le tag est ignorée. |
| `make freeze-check` | Aucune clé d'entité, aucun ID d'entité, aucune clé de réglage enregistrée et aucun type de carte n'est supprimé, et aucune plateforme d'entité, unité, classe d'appareil, classe d'état ni valeur d'état ne change, par rapport au tag de version stable le plus récent. Les tags bêta sont ignorés, une bêta ne fige donc jamais la surface. Sans tag de version stable, l'étape réussit. |
| `make docs-check` | La référence des entités générée, les liens, les images, la barre de langues de chaque page, la longueur des pages et la couverture de la liste des fonctionnalités. Voir la [page de documentation](documentation.md#vérifications). |
| `make template-check` | `bug.yml` exige le téléchargement des diagnostics, chaque libellé qu'un modèle de ticket applique ou référence existe dans `.github/labels.yml`, et la liste déroulante des modèles de `bug.yml` correspond aux modèles de `translations/en.json`. |
| `make mock-build` | L'image du simulateur se construit et ne contient aucun bytecode. |
| `make validate` | hassfest sur l'arbre de travail, dans Docker. La validation HACS lit le dépôt poussé, donc seul le job de workflow `validate` lance la validation HACS. |

`make lint`, `make python-ci`, `make frontend-check` et `make frontend-ci` lancent des groupes de ces cibles.

Quatre autres cibles ne sont pas des vérifications. `make setup` installe les dépendances Python et frontend et Chromium, `make docs` régénère la référence des entités, `make docs-images` fait les captures d'écran de la documentation, lance d'abord `make build` et `make mock-build` comme le test navigateur de Home Assistant et n'est pas une étape de `make ci`, et `make up`, `make down` et `make logs` exécutent le Home Assistant de développement, voir la [page de l'environnement](environment.md#exécuter-home-assistant).

Chaque cible passe par l'exécuteur de vérifications dans `.github/scripts/`. L'exécuteur affiche une ligne `[x]` ou `[ ]` par étape, les constats d'une étape en échec sous la forme `file:line message` et une ligne de résultat final. L'exécuteur lance chaque étape choisie même quand l'une échoue, et signale un délai dépassé, un signal ou un outil manquant comme tel. Chaque étape a une limite de temps. La sortie sobre existe pour qu'une personne ou un agent ne lise que ce qu'il faut pour corriger un échec.

Les GitHub Actions sont épinglées sur un hash de commit pour qu'un tag déplacé ne puisse pas changer ce que lance la CI.

## Options

- `ARGS="..."` transmet des chemins et des options à une cible à un seul outil, par exemple `make test-python ARGS="tests/saj/test_poller.py -k decode"` ou `make ruff ARGS="custom_components/saj_local/coordinator.py"`. `make help ARGS=<cible>` indique ce que fait `ARGS` pour chaque cible.
- `ONLY=<étape,...>` lance un sous-ensemble des étapes d'une cible de regroupement, par exemple `make ci ONLY=ruff,mypy`. Un nom que la cible ne lance pas est une erreur.
- `V=1` diffuse la sortie brute de l'outil et désactive pour cette exécution la configuration sobre des outils et les réglages d'environnement.

## Couverture d'une exécution partielle

Une exécution complète de `make test-python` mesure et contrôle tout le paquet. Quand `ARGS` choisit des fichiers de tests ou des dossiers, la cible mesure la couverture uniquement pour les modules que testent les fichiers de tests, ajoute à l'exécution les autres fichiers de tests unitaires associés à ces modules et applique le même seuil de 100 % à ces modules. Une exécution de `tests/saj-integration/test_coordinator_write.py` lance donc aussi `test_coordinator.py` et `test_coordinator_power.py` et contrôle `coordinator.py`. Le module est le fichier portant le nom du fichier de tests sans le préfixe `test_`, recherché par dossier de tests :

Le [tableau des dossiers de tests et des dossiers de modules](../../en-gb/developer/checks.md#coverage-of-a-subset-run) se trouve sur la page anglaise.

Les fichiers de tests sans module du même nom sont listés dans `.github/scripts/pytest_scope.json`, chacun avec les modules que le fichier teste, et un fichier de tests sans module connu est rejeté tant qu'il n'est pas ajouté à ce fichier. L'association par dossier se trouve dans `.github/scripts/pytest_scope.py`. Choisir des tests avec `-k`, `-m` ou `--lf` demande un fichier de tests dans `ARGS`, pour que la couverture puisse être contrôlée sur le module que teste le fichier.

Une exécution complète de `make test-python` enregistre quel test a exécuté chaque ligne et chaque branche (un contexte de couverture par test), si bien qu'une seule exécution alimente les deux seuils. Le cœur `ctrace` n'est défini que pour l'exécution complète, dans l'environnement de ses commandes, car le cœur par défaut `sysmon` n'enregistre une ligne que pour le premier test qui l'exécute et laisse donc les tests suivants sans contexte. La même exécution complète mesure la durée du corps de chaque test, et tout corps de plus de 200 ms fait échouer l'étape avec l'ID du test et la durée. 200 ms sous couverture font environ 50 ms dans une exécution normale, au-dessus des 125 ms qu'atteignent les tests sains sous couverture, le seuil n'échoue donc pas au hasard. Une exécution partielle garde le cœur `sysmon`, n'enregistre aucun contexte et n'applique aucun seuil de durée.

`test-modules` s'exécute dans `make ci` et contrôle chaque module à 100 % de couverture des lignes et des branches grâce aux seuls fichiers de tests unitaires associés au module. Le seuil ne compte que les contextes de ces fichiers de tests et le code exécuté à l'import du module, la couverture venant des tests d'autres modules ne compte donc pas. `test-modules` lit les données de couverture de `test-python`, donc `make test-modules` seul lance d'abord `test-python` et `make ci` lance les tests une fois. Un module avec de la logique et sans fichier de tests unitaires fait échouer l'étape, et un module sans logique est ignoré, car les exigences interdisent les tests de constantes. Un module qui ne passe le seuil que dans l'exécution complète de `test-python` signifie que d'autres tests couvrent le module par accident, et c'est une vraie lacune à corriger. `test-isolated` contrôle la couverture comme toute exécution partielle.

## Tests

Les règles se trouvent dans la [section Tests des exigences globales](../../../.github/work/requirements.md#testing). Les raisons :

- **La couverture ne compte que les tests unitaires.** Un test qui relie de vrais modules fait monter le chiffre sans prouver aucun de ces modules.
- **Les tests unitaires sont rapides et isolés.** Pas de sockets, de serveurs, de fichiers de fixtures, de temps réel ni de longues simulations. Le temps, le hasard et les E/S sont injectés partout dans le code pour cette raison.
- **Les tests d'intégration prouvent seulement que les parties se connectent.** Pour le simulateur, le test d'intégration est `make mock-smoke`.
- **Aucun contournement dans le code** des vérifications de lint, de types ou de couverture. Modifiez la configuration, où la décision est visible, ou restructurez le code.
- **Vérifiez le comportement, pas les constantes.** Un test qui répète une adresse de registre ne prouve rien.

`tests/` contient exactement six dossiers :

- `tests/saj` : tests unitaires de la bibliothèque SAJ.
- `tests/saj-integration` : tests unitaires de l'intégration Home Assistant, pas des tests d'intégration.
- `tests/mock` : tests unitaires du simulateur Modbus, avec `profiles/` et `simulation/`.
- `tests/mock-integration` : le script de test de fumée du conteneur et le test des scénarios livrés du simulateur.
- `tests/playwright` : les scripts Docker des tests navigateur.
- `tests/scripts` : les tests unitaires de l'exécuteur de vérifications, et ses tests à processus réels dans `test_runner_processes.py`.

`tests/mock-integration` et `tests/scripts/test_runner_processes.py` sont hors de l'exécution unitaire et hors couverture.

## Pile technique

| Élément | Pourquoi |
| --- | --- |
| Python avec `uv` | Un seul fichier de verrouillage, les mêmes installations en local et en CI. |
| Ruff, toutes les règles activées | Chaque exception est une décision visible dans `[tool.ruff.lint]`. |
| mypy | Le décodage des registres invite à des erreurs d'échelle, de signe et de largeur que les types détectent. |
| import-linter | Fait des frontières de la [page d'architecture](architecture.md#comment-le-projet-est-découpé) une vérification qui échoue. |
| complexipy, jscpd | Le code des cartes de registres grossit par duplication ; les limites arrêtent cette croissance. |
| pytest, 100 pour cent de couverture des branches | Voir [Tests](#tests). |
| Lit, TypeScript, Vite | Le frontend de Home Assistant est en Lit, les cartes n'ont donc pas besoin d'un second framework. |
| Playwright | Pilote les cartes dans un vrai navigateur et dans un vrai Home Assistant, et fait les [captures d'écran de la documentation](documentation.md#captures-décran). |
| Docker Compose | Voir la [page de l'environnement](environment.md#docker). |

Home Assistant est épinglé dans plusieurs fichiers qui doivent changer ensemble, sinon le lint et les tests s'exécutent sur des cœurs différents. Les étapes se trouvent sur la [page de publication](releasing.md#mettre-à-jour-la-version-de-home-assistant).
