[en](../../en-gb/developer/releasing.md) | [de](../../de/developer/releasing.md) | [nl](../../nl/developer/releasing.md) | fr | [zh](../../zh-hans/developer/releasing.md) | [es](../../es/developer/releasing.md) | [it](../../it/developer/releasing.md) | [pl](../../pl/developer/releasing.md) | [sv](../../sv/developer/releasing.md)

# Publication

Ce qu'il faut faire avant une publication, comment une publication est faite et comment la version de Home Assistant est mise à jour. Pousser une étiquette de version démarre le workflow `Release` dans `.github/workflows/release.yml`, qui vérifie l'étiquette, exécute les vérifications et crée une publication GitHub en brouillon.

## Versions

Une publication est une publication GitHub faite à partir d'une étiquette de version sur `main`. L'étiquette n'a pas de préfixe `v` et est égale à la version dans `custom_components/saj_local/manifest.json`, `pyproject.toml` et `frontend/package.json`. Une publication stable est `X.Y.Z` et une bêta est `X.Y.ZbN`, publiée comme pré-publication GitHub. Les bêtas avant la première publication stable sont `1.0.0b1`, `1.0.0b2` et ainsi de suite, la première publication stable est `1.0.0`, et le versionnement sémantique s'applique à partir de `1.0.0`. Les notes de publication se trouvent uniquement dans la publication GitHub, et les notes d'une bêta nomment chaque changement d'une entité, d'un réglage enregistré, d'un type de carte ou d'un réglage de carte depuis la bêta précédente. La section [Publications](../../../.github/work/requirements.md#releases) des exigences du projet contient la règle.

## Avant une publication

Faites ceci sur `main`, dans l'ordre.

1. **Exécutez `make ci`.** La [page des vérifications](checks.md) liste ce que `make ci` exécute.
2. **Exécutez `make docs-images`.** La documentation utilisateur montre l'interface, et la CI ne régénère pas les images, chaque publication demande donc un jeu neuf. La cible a besoin de Docker. Exécutez la cible, regardez chaque image modifiée, validez les images modifiées dans `docs/images/en-gb/` et exécutez `make docs-check`. Une exécution qui échoue n'écrit aucune image, ne publiez donc pas avec une exécution échouée. Lisez [Captures d'écran](documentation.md#captures-décran) pour ce que fait l'exécution et pourquoi chaque mesure d'une image est simulée.
3. **Copiez la capture d'écran du site dans la même étape.** Copiez `docs/images/en-gb/cards-power-flow-card.png` vers `assets/images/saj-local-power-flow.png` dans le dépôt `website` et validez la copie là-bas, car la page SAJ Local de `counterphase.dev` montre une copie de l'image. Aucune vérification ne détecte une copie périmée, car la CI de ce dépôt ne voit pas le dépôt du site.
4. **Exécutez `make release-check`.** L'étape fabrique une archive à partir de `custom_components/saj_local/` et échoue quand l'archive n'a pas `asset-manifest.json` ou le bundle de cartes compilé. Exécutez `make build` et validez d'abord le bundle quand les cartes ont changé.
5. **Définissez la nouvelle version.** Définissez la version dans `custom_components/saj_local/manifest.json`, `pyproject.toml` et `frontend/package.json`. Exécutez `uv lock` pour que `uv.lock` enregistre la version du projet, et exécutez `npm install --package-lock-only` dans `frontend/` pour que `frontend/package-lock.json` enregistre la version. Exécutez `make release-check`, validez sur `main` et attendez que la CI réussisse.

Les captures d'écran sont la seule partie d'une publication que la CI ne peut pas vérifier. Une modification qui ajoute ou supprime une image fait échouer `make docs-check` par les règles d'image inutilisée et d'image manquante. Une modification de l'interface qui rend une image obsolète ne fait rien échouer, c'est donc l'étape 2 qui maintient les images à jour.

## Publier une version

1. Poussez l'étiquette : `git tag 1.0.0b1`, puis `git push origin 1.0.0b1`.
2. Attendez le workflow `Release`. Le workflow exige que le commit étiqueté soit sur `main`, exécute `make ci` par `ci.yml` et crée une publication en brouillon avec les notes générées par GitHub.
3. Ouvrez la publication en brouillon et modifiez les notes générées. Pour une bêta, nommez chaque changement d'une entité, d'un réglage enregistré, d'un type de carte ou d'un réglage de carte depuis la bêta précédente.
4. Appuyez sur Publish.

Une exécution échouée ne crée aucun brouillon. Supprimez l'étiquette avec `git push origin :refs/tags/<tag>` et `git tag -d <tag>`, corrigez `main` et étiquetez de nouveau.

HACS propose une bêta publiée aux utilisateurs qui activent « Afficher les versions bêta » et une publication stable publiée à tous les utilisateurs. Un utilisateur sans l'interrupteur obtient la pointe de `main` tant que `1.0.0` n'existe pas, c'est pourquoi `main` doit réussir `make ci` avant chaque envoi.

## Mettre à jour la version de Home Assistant

La version de Home Assistant est épinglée dans plusieurs fichiers qui doivent être mis à jour ensemble, sinon le conteneur de développement, les tests de navigateur et l'exécution des captures d'écran, la CI, HACS et le banc de test divergent :

1. `compose.yaml` : `ghcr.io/home-assistant/home-assistant:<X.Y.Z>`, l'environnement d'exécution de Home Assistant de développement.
2. `Dockerfile.playwright-home-assistant` : la ligne `FROM ghcr.io/home-assistant/home-assistant:<X.Y.Z>` de l'image que `make test-browser-home-assistant` et `make docs-images` utilisent.
3. `pyproject.toml`, `[dependency-groups] dev` : `homeassistant==<X.Y.Z>` pour le lint et mypy de la CI, **et** `pytest-homeassistant-custom-component==<matching release>`. Le banc de test livre son propre `homeassistant` épinglé, les deux épinglages doivent donc venir de la même version de Home Assistant, sinon le lint et les tests résolvent des cœurs différents.
4. `hacs.json` : `"homeassistant": "<X.Y.Z>"`, le cœur Home Assistant minimal que HACS impose.
5. `uv.lock` : exécutez `uv lock` après la modification de `pyproject.toml`, pour que le fichier de verrouillage enregistre les nouveaux épinglages.

Vérifiez l'appariement sur PyPI avant de valider : le `requires_dist` de `pytest-homeassistant-custom-component` doit lister le même `homeassistant==<X.Y.Z>` épinglé dans `pyproject.toml`.

Après une mise à jour, exécutez `make ci` et `make docs-images`, car une nouvelle version de Home Assistant peut changer les écrans que les images montrent.
