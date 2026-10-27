[en](../../en-gb/developer/documentation.md) | [de](../../de/developer/documentation.md) | [nl](../../nl/developer/documentation.md) | fr | [zh](../../zh-hans/developer/documentation.md) | [es](../../es/developer/documentation.md) | [it](../../it/developer/documentation.md) | [pl](../../pl/developer/documentation.md) | [sv](../../sv/developer/documentation.md)

# Documentation

Comment les pages de documentation sont organisées, comment la référence des entités et les captures d'écran sont faites, et ce sur quoi `make docs-check` échoue.

## Organisation

Les pages utilisateur se trouvent dans `docs/en-gb/user/` et les pages développeur dans `docs/en-gb/developer/`. Chaque dossier a un index `README.md`, et chaque page couvre un sujet. Aucune page écrite ne dépasse 300 lignes. Chaque fait a un propriétaire, listé sous [Sources](#sources), et toute autre page renvoie au propriétaire au lieu de répéter le fait.

Les captures d'écran se trouvent dans `docs/images/en-gb/`. Chaque image doit être référencée par une page.

Écrivez les pages anglaises en anglais britannique, dans le ton de Counterphase, et employez les termes que les traductions de l'intégration montrent aux utilisateurs. Les pages utilisateur décrivent SAJ en général et indiquent, à l'endroit de la différence, où le HS3 et le H2 diffèrent. Une page ne se divise jamais en une page par modèle.

## Les listes des fonctionnalités d'abord

Les trois listes des fonctionnalités sont la base de chaque page : [intégration](../../../custom_components/saj_local/docs/features.md), [cartes](../../../frontend/docs/features.md) et [simulateur](../../../mock/docs/features.md). Une section d'une liste des fonctionnalités dit ce qui est construit et nomme les fichiers à lire sur la ligne `Files:` de la section. Confirmez chaque affirmation d'après ces fichiers avant de la documenter. Les documents d'exigences disent ce qui est voulu et ne sont lus que pour l'intention. Un comportement qui apparaît dans un document d'exigences mais dans aucune liste des fonctionnalités n'est pas construit, et une page utilisateur ne décrit pas ce comportement comme disponible. Quand une liste des fonctionnalités et le code divergent, le code est ce que les utilisateurs obtiennent, corrigez donc la liste des fonctionnalités dans la même modification.

Une page qui décrit du code renvoie à la section de la liste des fonctionnalités dont la ligne `Files:` nomme le code, et ne répète pas la liste des fichiers.

Une modification de capacité met à jour la liste des fonctionnalités de la partie et chaque page utilisateur qui renvoie à la section modifiée, dans la même modification. La règle se trouve dans le `AGENTS.md` racine.

## Référence des entités générée

`docs/en-gb/user/entities/` contient une page générée par zone et un index `README.md`. Lancez `make docs` pour régénérer les pages, puis validez les pages régénérées. Les pages de prose ne nomment jamais une entité à la main ; les pages de prose renvoient aux pages générées. Les pages générées sont exemptées de la limite de 300 lignes, car les lecteurs cherchent dans une zone comme la batterie au lieu de la lire.

Le générateur est `.github/scripts/docs_check.py`, lancé avec `--write` par `make docs`. Le générateur importe uniquement la bibliothèque SAJ et lit `custom_components/saj_local/translations/en.json`, il n'a donc pas besoin de Home Assistant. Chaque page de zone s'ouvre sur un lien vers les sections de la liste des fonctionnalités qui couvrent la zone et une ligne sur le préfixe d'ID d'entité, puis a une ligne par entité avec le nom de `en.json`, l'ID d'entité sans préfixe, le type, l'unité, les modèles qui ont l'entité, l'équipement qui doit être installé pour tout nombre de phases, de chaînes ou de modules, et si l'entité est activée par défaut. Une entité que deux modèles définissent différemment, par exemple avec une autre unité, obtient une ligne par définition.

### Sources des entités

Chaque entité vient de l'une de ces sources, et le générateur les lit toutes :

| Source | Code | Entités |
| --- | --- | --- |
| Le catalogue de registres de chaque modèle livré | `catalogue_of` dans [catalogue.py](../../../custom_components/saj_local/saj/catalogue.py), appelé pour chaque profil de `PROFILES` dans [profiles.py](../../../custom_components/saj_local/saj/profiles.py), en ignorant les lignes qui ne sont pas exposées | Capteurs, capteurs binaires (les défauts), nombres, sélections, interrupteurs, heures et boutons |
| Le capteur de contrôle autorisé | `CONTROL_ALLOWED_KEY` dans [binary_sensor.py](../../../custom_components/saj_local/binary_sensor.py) | `binary_sensor.saj_control_allowed`, sur les deux modèles |
| Les interrupteurs et nombres du pilotage de puissance | `power_control` de chaque profil ([hs3.py](../../../custom_components/saj_local/saj/models/hs3.py) et [h2.py](../../../custom_components/saj_local/saj/models/h2.py)), les clés `PowerFunction` dans [models/\_\_init\_\_.py](../../../custom_components/saj_local/saj/models/__init__.py) et `FUNCTION_EQUIPMENT` dans [power_control.py](../../../custom_components/saj_local/saj/power_control.py), créés par [switch.py](../../../custom_components/saj_local/switch.py) et [number.py](../../../custom_components/saj_local/number.py) | Un interrupteur et un nombre pour chaque fonction de puissance d'un modèle : batterie sur les deux modèles, réseau et onduleur sur le HS3 |

`make docs-check` échoue quand une entité du bloc `entity` de `en.json` figure sur aucune page de zone, une source d'entités que le générateur ne lit pas est donc trouvée aussitôt. Une nouvelle source demande que le générateur lise la source et une ligne dans le tableau ci-dessus.

### Zones

Une entité atterrit dans la première zone qui correspond, dans cet ordre :

1. Entités hors du catalogue : Ajoutées par l'intégration.
2. Capteurs binaires du catalogue, qui sont les défauts : Défauts.
3. Entités avec un index de module de batterie : Modules de batterie.
4. Entités d'équipement optionnel : Batterie, Réseau et compteur A, Compteur B, Chargeur de VE ou Système en parallèle.
5. Entités modifiables sans équipement : Réglages.
6. Entités dont la clé commence par `grid_` : Réseau et compteur A.
7. Tout le reste : Onduleur et solaire.

Le tableau `AREAS` de `.github/scripts/docs_check.py` nomme les zones, leurs résumés et les sections de la liste des fonctionnalités que chaque page de zone référence.

## Vérifications

`make docs-check` lance `.github/scripts/docs_check.py` sans `--write` et signale une ligne par constat :

- une page générée qui diffère de ce que `make docs` écrirait ;
- une entité de `en.json` qui figure sur aucune page de zone, et une entité générée sans nom dans `en.json` ;
- un lien relatif, une image ou une ancre de titre qui ne se résout pas, dans les pages, `README.md`, `CONTRIBUTING.md`, `SECURITY.md` et chaque `AGENTS.md`, y compris les liens vers les listes des fonctionnalités et les documents d'exigences ;
- une image de `docs/images/` qu'aucune page ne référence ;
- une page écrite de plus de 300 lignes ;
- une section de liste des fonctionnalités sans ligne dans le [tableau de couverture des fonctionnalités](#tableau-de-couverture-des-fonctionnalités), une section nommée dans le tableau que la liste des fonctionnalités n'a pas, une page nommée dans le tableau qui n'existe pas, et une page qui ne renvoie pas à la section de la liste des fonctionnalités nommée dans la ligne, par l'ancre de titre de la section.

`make docs-check` est une étape de `make ci`, et GitHub lance `make ci`, la vérification n'a donc besoin d'aucune modification du workflow. La vérification ne lit aucune capture d'écran au-delà des règles sur les liens et les images orphelines et ne lance aucun navigateur.

## Captures d'écran

Chaque capture d'écran de `docs/images/<code>/` est faite par `make docs-images` depuis un vrai Home Assistant dans Docker dont la langue d'utilisateur est celle du dossier, ou depuis les pages des simulateurs de la même exécution. `make docs-images` lance chaque langue, l'anglais d'abord, avec des conteneurs neufs pour chaque exécution, et `ARGS=<code>` choisit une langue. Aucune capture d'écran n'est modifiée ni prise à la main, l'ensemble peut donc être refait chaque fois que l'interface change. Les captures d'écran montrent les simulateurs, donc chaque mesure d'une capture d'écran est une valeur simulée.

La cible lance `tests/playwright/run-docs-images.sh`, qui construit les services `homeassistant` et `playwright-docs` de [compose.playwright.yaml](../../../compose.playwright.yaml), démarre le Home Assistant jetable et deux simulateurs, exécute la spec, puis supprime les conteneurs, les volumes et les images locales. La cible a besoin de Docker, a la même limite de temps que `make test-browser-home-assistant` et accepte des options par `ARGS`, que le script reçoit. L'image de Home Assistant est construite à partir de `Dockerfile.playwright-home-assistant`, qui construit le bundle des cartes et copie l'intégration dans l'image, aucun code d'intégration n'est donc monté. La spec est `frontend/tests/browser/docs/screenshots.spec.ts`, configurée par `frontend/playwright.docs.config.ts`.

- **Systèmes.** Le HS3 est le simulateur `mock-docs` sur `mock/scenarios/hs3-full-house.yaml`, qui a tout l'équipement installé. Le H2 est le simulateur `mock-h2` sur `mock/scenarios/h2-battery.yaml` et reçoit le préfixe d'entité `h2`. Aucun simulateur ne monte de dossier d'état, chaque exécution part donc du scénario.
- **Conditions fixes.** La fenêtre fait 1280 sur 800 pixels, le thème est clair et l'horloge est réelle. Une boîte de dialogue ou une carte haute est prise dans une fenêtre de 1600 pixels de haut, car l'en-tête fixe de Home Assistant cacherait le haut de l'élément.
- **Langue.** Chaque exécution définit à la fois la langue du serveur Home Assistant, avant la configuration de SAJ Local pour que les entités soient créées avec des noms dans cette langue, et la langue d'utilisateur, par le code de langue et non par le libellé du sélecteur de langue. L'exécution échoue si un nom d'entité de SAJ Local n'est pas dans la langue de l'exécution. Les images vont dans `docs/images/<code>/`. La spec ouvre les écrans par leur route d'URL, trouve les champs des formulaires de SAJ Local par leur attribut `name`, et trouve les commandes de Home Assistant qui n'ont que du texte par le texte lu à l'exécution depuis le Home Assistant en cours avec `hass.localize`. La spec ne contient aucune table de libellés, chaque langue exécute donc les mêmes étapes.
- **Noms.** Chaque fichier se nomme `<page>-<subject>.png`, où `<page>` est le chemin de la page avec `/` remplacé par `-`, par exemple `cards-battery-card.png`, et la page qui montre l'image renvoie au fichier.
- **Pages des simulateurs.** Les captures d'écran des pages des simulateurs viennent des deux simulateurs de la même exécution, `mock-docs` et `mock-h2`, et utilisent le préfixe de nom `developer-simulator-page-`. Elles sont prises en dernier, après chaque capture d'écran de Home Assistant, pour que rien de ce qui est fait sur une page de simulateur ne change une capture d'écran de Home Assistant. La spec active le défaut « Fan 1 fault » sur la page du HS3, et le registre que la capture de la réparation fait refuser au simulateur reste refusé, si bien que la vue Link, le journal du trafic et les changements de la barre d'état montrent de vrais changements.
- **Préparation.** La spec crée un utilisateur par l'API d'accueil, ajoute le HS3 par l'assistant de configuration dans le navigateur, ajoute le H2 par l'API de l'assistant de configuration, active Autoriser le contrôle sur les deux systèmes et ajoute un tableau de bord par système avec chaque carte SAJ Local et le badge d'état, par l'API WebSocket de Home Assistant.
- **Tout ou rien.** La spec attend jusqu'à deux minutes que les deux systèmes signalent la puissance solaire. La spec n'écrit les images qu'une fois toutes les étapes réussies, un échec laisse donc les images validées telles quelles.
- **Attentes.** La spec attend un écran en vérifiant l'état que l'écran montre, jamais par une pause fixe.
- **Réparation.** La capture de la réparation montre la réparation des registres refusés. La spec ajoute un groupe d'interrogation pour la température de l'onduleur avec un intervalle de 10 secondes, fait refuser ce registre au simulateur par `POST /api/link` de la page du simulateur, et attend jusqu'à deux minutes que `repairs/list_issues` liste le problème `registers_refused` de SAJ Local. L'exécution échoue avec un message qui nomme le problème manquant quand le problème n'apparaît pas.
- **Formulaires.** L'avertissement du changement de préfixe est capturé puis le formulaire est fermé, ce qui annule le flux, aucun préfixe n'est donc enregistré. L'avertissement d'Autoriser le contrôle est capturé puis confirmé, car les cartes ont besoin du contrôle autorisé.
- **Échecs.** Le rapport HTML se trouve dans `frontend/playwright-report/docs/`, et une exécution en échec enregistre le journal de Home Assistant sous `frontend/test-results/docs/home-assistant.log`.

Les captures d'écran ne sont pas comparées pixel par pixel, ni en CI ni ailleurs. Home Assistant affiche les valeurs en direct et les polices différemment d'une exécution à l'autre, une comparaison de pixels échouerait donc sans changement réel. Vérifiez une image modifiée en regardant l'image.

### Ajouter ou modifier une capture d'écran

1. Ajoutez ou modifiez la capture dans la spec, avec le nom de fichier sous la forme `<page>-<subject>.png`.
2. Référencez l'image depuis la page qui explique le sujet.
3. Lancez `make docs-images`, regardez les images modifiées et validez les images modifiées.
4. Lancez `make docs-check`. Une image qu'aucune page ne référence et un lien vers une image qui n'existe pas sont tous deux signalés.

`make docs-images` n'est pas une étape de `make ci`, et la CI ne régénère pas les images. Lancez la cible avant chaque publication, voir la [page de publication](releasing.md).

## Ajouter une page

1. Créez la page sous `docs/en-gb/user/` ou `docs/en-gb/developer/` et reliez la page depuis l'index du dossier.
2. Reliez la page à la section de la liste des fonctionnalités dont la ligne `Files:` nomme le code que la page décrit.
3. Ajoutez la page à la ligne de cette section dans le tableau de couverture des fonctionnalités, ou ajoutez une ligne. Une nouvelle section de liste des fonctionnalités demande une ligne avant que `make docs-check` réussisse.
4. Lancez `make docs-check`.

Gardez les pages utiles : renvoyez au fichier qui contient un fait au lieu de copier le fait, consignez la raison d'une décision car les raisons changent rarement et les détails constamment, et gardez peu d'exemples en relançant chaque exemple quand il change.

## Langues

La documentation existe en anglais et dans chaque langue cible des [exigences globales](../../../.github/work/requirements.md#language). Les listes des fonctionnalités et les documents d'exigences restent uniquement en anglais.

- **Organisation.** Chaque langue a les dossiers frères `docs/<code>/user/`, `docs/<code>/developer/` et `docs/images/<code>/`, avec les mêmes noms de fichiers dans chaque langue. Les codes sont `en-gb`, `de`, `nl`, `fr`, `zh-hans`, `es`, `it`, `pl` et `sv`. Un bloc de code identique dans plusieurs langues reste dans le texte de chaque page et est entouré d'une paire de marqueurs `jscpd:ignore-start` et `jscpd:ignore-end`, uniquement sous une exception que l'utilisateur a approuvée dans un plan, comme le dit `AGENTS.md`. Une paire de marqueurs entoure un seul bloc de code et rien d'autre.
- **Générateur.** `make docs` écrit `docs/<code>/user/entities/` pour chaque langue à partir du fichier correspondant de `custom_components/saj_local/translations/`. Les noms d'équipement viennent du même fichier de traduction, et les autres textes du générateur viennent de `.github/scripts/docs_text/<code>.json`.
- **Vérification de la documentation.** `make docs-check` applique chaque règle à chaque dossier de langue. Le [tableau de couverture des fonctionnalités](#tableau-de-couverture-des-fonctionnalités) de cette page s'applique à chaque langue sous les mêmes noms de pages, et la règle des images orphelines vérifie `docs/images/<code>/` par rapport aux pages de la même langue.
- **Barre de langues.** La première ligne de chaque page sous `docs/<code>/user/` et `docs/<code>/developer/`, pages d'entités générées comprises, est la barre de langues `en | de | nl | fr | zh | es | it | pl | sv`, toujours dans cet ordre. Chaque libellé sauf celui de la langue courante renvoie à la même page dans le dossier de cette langue, et la langue courante est du texte simple. `make docs` écrit la barre de langues, et `make docs-check` signale une page dont la première ligne n'est pas la barre de langues attendue ainsi qu'un lien de la barre vers une page qui n'existe pas.
- **README traduit.** Le `README.md` à la racine du dépôt reste en anglais et est traduit dans `docs/<code>/README.md`, dont les liens pointent vers les pages de cette langue. Le `README.md` racine et chaque `docs/<code>/README.md` portent la même barre de langues en première ligne, et `make docs-check` signale un `docs/<code>/README.md` manquant.
- **Captures d'écran.** `make docs-images` lance la spec une fois par langue, l'anglais d'abord, avec des conteneurs neufs pour chaque exécution. `ARGS=<code>` choisit une langue, voir [Captures d'écran](#captures-décran).
- **Nomenclature.** La page `user/nomenclature.md` de chaque langue est la liste des termes que suit chaque traduction de l'intégration, des cartes et des pages de la langue, ici la page [Nomenclature](../user/nomenclature.md). La page anglaise `user/nomenclature.md` est la source.
- **Modifier l'anglais.** Une modification d'un texte, d'une page ou d'une capture d'écran anglais met à jour chaque langue dans la même modification. Aucune vérification ne garde les langues synchronisées.

## Tableau de couverture des fonctionnalités

Chaque section de liste des fonctionnalités est examinée à partir de la ligne `Files:` de la section et couverte par les pages nommées ici. Chaque page nommée renvoie à la section par l'ancre de titre de la section. Le tableau se trouve uniquement sur la page anglaise [Documentation](../../en-gb/developer/documentation.md#feature-coverage-table), et `docs-check` lit le tableau à cet endroit. Le tableau s'applique dans chaque langue aux mêmes noms de pages, et une page ajoutée, fusionnée ou scindée met à jour le tableau dans la même modification.

## Sources

| Fait | Propriétaire |
| --- | --- |
| Ce que fait SAJ Local, en un court résumé | [index utilisateur](../user/README.md) |
| Ce que peut faire chaque partie | les trois listes des fonctionnalités |
| Modèles et équipements pris en charge | [équipements pris en charge](../user/supported-equipment.md) |
| Noms d'entités, ID d'entité, modèles, équipements et valeurs par défaut | le catalogue et `translations/en.json`, par la [référence des entités](../user/entities/README.md) |
| Types d'entités, règles d'activation par défaut et conventions de signe | la section Appareils et entités de la liste des fonctionnalités de l'intégration |
| Mise en place du développement | [environnement](environment.md) |
| Cibles make et règles de vérification | [vérifications](checks.md) |
| Mise à jour de la version de Home Assistant | [publication](releasing.md) |
| Capture d'écran de la vue d'ensemble du site | `docs/images/en-gb/cards-power-flow-card.png`, copiée vers `assets/images/saj-local-power-flow.png` dans le dépôt `website` à chaque publication, voir la [page de publication](releasing.md) |
| Comment signaler un problème de sécurité | `SECURITY.md` |
| Étiquettes des tickets et règles des étiquettes | `.github/labels.yml` et `CONTRIBUTING.md` |
| Conditions de licence | `LICENSE` |
| Comportement prévu du produit | `.github/work/requirements.md` et les trois documents d'exigences des parties |
