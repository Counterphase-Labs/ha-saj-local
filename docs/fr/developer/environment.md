[en](../../en-gb/developer/environment.md) | [de](../../de/developer/environment.md) | [nl](../../nl/developer/environment.md) | fr | [zh](../../zh-hans/developer/environment.md) | [es](../../es/developer/environment.md) | [it](../../it/developer/environment.md) | [pl](../../pl/developer/environment.md) | [sv](../../sv/developer/environment.md)

# Environnement de développement

Comment préparer une copie de travail et exécuter l'instance Home Assistant de développement avec les simulateurs.

## Préparer une copie de travail

Une copie de travail a besoin de [uv](https://docs.astral.sh/uv/) pour les outils Python, de Node.js et npm pour les cartes, de Docker avec Docker Compose pour Home Assistant et les simulateurs, et de `make`. Les versions requises sont fixées dans `pyproject.toml` et `frontend/package.json`. Après le clonage, `make setup` installe les dépendances Python, les dépendances du frontend et le navigateur Chromium que les tests Playwright utilisent.

## Exécuter Home Assistant

`make up` démarre Home Assistant avec l'intégration et deux simulateurs Modbus, un HS3 et un H2. `make logs` suit le journal de Home Assistant et `make down` arrête tout.

Home Assistant est sur le port 8123. Le simulateur HS3 répond en Modbus sur le port hôte 5020 et le simulateur H2 sur 5021, et les pages des simulateurs sont sur 5080 et 5081. Dans Docker, Home Assistant atteint les simulateurs par les noms de service `mock` et `mock-h2` sur le port 502. Aucun vrai onduleur n'est nécessaire. La [page du simulateur](simulator.md) explique comment se connecter aux simulateurs et modifier ce que les simulateurs simulent.

Pour utiliser d'autres ports hôte, un autre fuseau horaire ou d'autres scénarios, copiez [compose.override.yaml.example](../../../compose.override.yaml.example) vers le fichier ignoré `compose.override.yaml` et modifiez ce qui diffère. Ne modifiez pas `compose.yaml` pour des besoins locaux, car `make mock-smoke` démarre aussi `compose.yaml`.

## Docker

Le développement s'exécute dans des conteneurs pour que Home Assistant soit une version connue et épinglée, avec une configuration propre. Les services sont définis dans ces fichiers :

- [compose.yaml](../../../compose.yaml) : l'environnement interactif, avec Home Assistant, le simulateur HS3 `mock` et le simulateur H2 `mock-h2`. L'intégration est montée en lecture seule dans Home Assistant, le conteneur n'écrit donc jamais dans l'arborescence des sources. Les simulateurs conservent leurs changements dans `mock/state/hs3/` et `mock/state/h2/`, que Git ignore.
- [compose.playwright.yaml](../../../compose.playwright.yaml) : un Home Assistant jetable construit à partir de `Dockerfile.playwright-home-assistant`, avec un simulateur HS3, un simulateur H2 et des exécuteurs Playwright. `make test-browser-home-assistant` utilise les services `homeassistant`, `mock`, `mock-h2` et `playwright` pour prouver que chaque point d'accès peut être ajouté, se charge, rapporte des valeurs de capteurs, affiche la puissance solaire sur une carte de flux de puissance et, une fois le contrôle autorisé, accepte un réglage modifié. `make docs-images` utilise les services `homeassistant`, `mock-docs`, `mock-h2` et `playwright-docs`, voir [Captures d'écran](documentation.md#captures-décran). Les services ne partagent aucun état avec l'environnement interactif.
- `compose.override.yaml` : les ports, le fuseau horaire et les scénarios de votre machine. Git ignore le fichier, et `compose.override.yaml.example` montre la forme.

Sous `config/`, Git ne suit que `configuration.yaml` et les deux tableaux de bord de démonstration dans `config/dashboards/`. Le reste est l'état local de Home Assistant.

La [page des vérifications](checks.md) liste ce que chaque cible make exécute, et la [page du frontend](frontend.md#tableaux-de-bord-de-démonstration) décrit les deux tableaux de bord de démonstration.
