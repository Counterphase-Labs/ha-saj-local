[en](../../en-gb/user/nomenclature.md) | [de](../../de/user/nomenclature.md) | [nl](../../nl/user/nomenclature.md) | fr | [zh](../../zh-hans/user/nomenclature.md) | [es](../../es/user/nomenclature.md) | [it](../../it/user/nomenclature.md) | [pl](../../pl/user/nomenclature.md) | [sv](../../sv/user/nomenclature.md)

# Nomenclature

Les termes que SAJ Local, les cartes du tableau de bord et la documentation utilisent, chacun avec sa signification en une ligne. Chaque traduction de l'intégration, des cartes et de la documentation emploie un seul terme pour chaque chose listée ici. La section [Langues](../../../custom_components/saj_local/docs/features.md#languages) de la liste des fonctionnalités de l'intégration nomme les langues que SAJ Local fournit.

## Équipement SAJ et mesures

| Terme | Signification |
| --- | --- |
| Onduleur | L'appareil SAJ qui transforme le courant continu du solaire et de la batterie en courant alternatif pour la maison et le réseau. |
| HS3 | Le modèle d'onduleur hybride SAJ HS3, un modèle triphasé. |
| H2 | Le modèle d'onduleur hybride SAJ H2, un modèle monophasé. |
| Modèle | Le type d'onduleur que SAJ Local utilise pour choisir la liste des registres : Automatique, HS3 ou H2. |
| Automatique | Le choix de modèle qui reconnaît le modèle d'après le type d'appareil que l'onduleur signale. |
| Équipement optionnel | Un équipement qu'une installation peut avoir ou non : une batterie, le compteur A, le compteur B, un chargeur de VE ou un système en parallèle. |
| Installé | Le réglage qui indique à SAJ Local qu'un équipement optionnel est installé. |
| Non installé | Le réglage qui indique à SAJ Local qu'un équipement optionnel n'est pas installé. |
| Batterie | Le stockage d'énergie raccordé à l'onduleur. |
| Module de batterie | Un module d'une batterie, affiché sous la forme Module suivi d'un numéro. |
| État de charge | Le niveau de remplissage de la batterie, en pourcentage. |
| Réserve | La charge de la batterie que l'onduleur garde en réserve et sous laquelle il ne décharge pas. |
| Solaire | La puissance produite par les panneaux solaires. |
| Chaîne solaire | Un groupe de panneaux solaires câblés en série et raccordés à une entrée de l'onduleur. |
| Phase | Un conducteur de l'alimentation en courant alternatif. |
| Réseau | Le réseau public d'électricité auquel la maison est raccordée. |
| Soutirage | Prélever de la puissance sur le réseau. |
| Injection | Envoyer de la puissance vers le réseau. |
| Charge | Mettre de la puissance dans la batterie. |
| Décharge | Prélever de la puissance dans la batterie. |
| Maison | La puissance que la maison consomme. |
| Circuit de secours | Les charges qui restent alimentées par la batterie et les panneaux solaires lorsque le réseau tombe en panne. |
| Compteur A | Le premier compteur électrique qui peut être raccordé à l'onduleur. |
| Compteur B | Le second compteur électrique qui peut être raccordé à l'onduleur. |
| Chargeur de VE | Un chargeur de véhicule électrique raccordé à l'onduleur. |
| Système en parallèle | Plusieurs onduleurs qui fonctionnent ensemble comme un seul système. |
| Défaut | Un problème que l'équipement signale, avec un registre et un bit. |
| Effacer le défaut | Le bouton qui demande à l'onduleur d'effacer un défaut signalé. |
| État de fonctionnement | L'état dans lequel se trouve l'onduleur, par exemple en marche ou en veille. |
| Mode | Le mode de fonctionnement de l'onduleur, par exemple le mode horaire. |
| Mode horaire | Le mode dans lequel la batterie se charge et se décharge pendant les plages horaires que vous réglez. |
| Plage horaire | Une période du programme horaire pour la charge, la décharge ou le chargeur de VE. |
| EMS | Les fonctions de gestion de l'énergie de l'onduleur, qui maintiennent une puissance cible venue de l'extérieur. |
| Signal de vie EMS | La fréquence à laquelle SAJ Local lit les cibles EMS pour maintenir les fonctions EMS actives. |
| Délai d'expiration EMS | Le délai après lequel l'onduleur met fin à une fonction EMS qui n'est pas maintenue active. |
| Protection contre le courant inverse | La protection de l'onduleur contre le retour de puissance vers l'onduleur, que les fonctions EMS désactivent. |
| Pilotage de puissance | Maintenir la batterie, le raccordement au réseau ou l'onduleur à une puissance fixée. |
| Puissance cible | La puissance qu'une fonction de pilotage de puissance maintient. |
| Programme | Les moments où une fonction de pilotage de puissance s'exécute. |
| Autoriser le contrôle | Le réglage qui permet à Home Assistant de modifier les réglages de l'onduleur. |
| Contrôle | La possibilité de modifier les réglages de l'onduleur, par opposition à seulement le lire. |
| Registre | Un emplacement mémoire numéroté de l'onduleur qui contient une mesure ou un réglage. |
| Registre refusé | Un registre auquel l'onduleur refuse de répondre. |
| Modbus TCP | Le protocole réseau que SAJ Local utilise pour communiquer avec l'onduleur. |
| Hôte | L'adresse réseau de l'onduleur. |
| Port | Le port réseau de l'onduleur, 502 par défaut. |
| ID d'unité | L'adresse Modbus de l'onduleur, de 1 à 247. |
| Module de communication | La partie de l'onduleur qui répond aux requêtes réseau. |
| Bloc | Une plage de registres lue avec une seule requête. |
| Temps réel | Le bloc de mesures qui changent d'une seconde à l'autre. |
| Moyennes sur cinq minutes | Le bloc de mesures que l'onduleur moyenne sur cinq minutes. |
| Énergie | Le bloc de mesures d'énergie produite et consommée, par exemple l'énergie du jour. |
| Identité | Le modèle, le numéro de série et les versions que l'onduleur signale. |

## Notions de SAJ Local

| Terme | Signification |
| --- | --- |
| Système | Un onduleur, avec son équipement, ajouté à Home Assistant. |
| Installation | Une entrée de configuration SAJ Local, c'est-à-dire un système. |
| Préfixe | Un texte optionnel ajouté aux ID d'entité d'une installation, utilisé lorsqu'il y a plus d'un système. |
| Interrogation | Lire l'onduleur à intervalles réguliers. |
| Groupe d'interrogation | Un ensemble choisi d'entités que SAJ Local lit plus vite ou plus lentement que l'intervalle par défaut. |
| Intervalle de mise à jour | Les secondes entre deux lectures de l'onduleur, affiché sous la forme « Secondes entre les mises à jour ». |
| Charge de requêtes | Le nombre de requêtes par minute que SAJ Local envoie à l'onduleur, par rapport à la limite de 40 en 60 secondes. |
| Budget | La limite de la charge de requêtes. |
| Remplacement de modèle | Passer un système à un nouvel onduleur, ou entre un H2 et un HS3, en conservant l'historique. |
| Non vérifié | Un modèle choisi à la main et qui n'a pas pu être vérifié d'après le type d'appareil. |
| Téléchargement des diagnostics | Le fichier qui contient un instantané du système, sans données personnelles, pour un rapport de bogue. |
| Journalisation de débogage | L'option qui écrit des lignes de journal détaillées pour trouver un problème. |
| Carte du tableau de bord | Une carte que SAJ Local ajoute aux tableaux de bord de Home Assistant. |
| Carte de flux de puissance | La carte qui affiche la puissance en direct entre le solaire, la batterie, le réseau et la maison. |
| Carte d'état | La carte qui affiche l'état de fonctionnement, le mode, les mesures clés et les défauts. |
| Carte des défauts | La carte qui liste les défauts actifs. |
| Carte de batterie | La carte qui affiche les mesures de la batterie et une ligne par module. |
| Carte de contrôle | La carte qui affiche les commandes communes du système. |
| Carte de programme | La carte qui affiche les plages horaires avec une chronologie de la semaine. |
| Fonctionnalité de carte tuile Jours de la semaine | Les sept boutons de jour qui peuvent être ajoutés à une carte tuile. |
| Badge d'état | Le badge qui affiche l'état de fonctionnement et le nombre de défauts actifs. |

## Notions de Home Assistant

| Terme | Signification |
| --- | --- |
| Home Assistant | Le logiciel de domotique dont SAJ Local est une intégration. |
| Intégration | Un logiciel qui raccorde un type d'appareil ou de service à Home Assistant. |
| HACS | Le Home Assistant Community Store, utilisé pour installer SAJ Local. |
| Dépôt personnalisé | Un dépôt qui ne figure pas dans la liste par défaut de HACS et qui est ajouté à HACS par son adresse ; le badge « HACS personnalisé » des README signale SAJ Local comme tel. |
| Assistant de configuration | La boîte de dialogue de configuration qui ajoute un système. |
| Entrée de configuration | La configuration enregistrée d'un système. |
| Sous-entrée | Une partie d'une entrée de configuration qui s'ajoute et se modifie séparément, par exemple un groupe d'interrogation ou un programme de puissance. |
| Configurer | Le bouton d'une intégration qui ouvre ses options. |
| Appareils et services | La page des paramètres de Home Assistant qui liste les intégrations, les appareils et les entités. |
| Paramètres | La page de Home Assistant pour configurer Home Assistant. |
| Appareil | L'enregistrement dans Home Assistant d'un équipement qui contient des entités. Chaque système est un appareil. |
| Entité | Une mesure, un réglage ou une commande que Home Assistant affiche. |
| ID d'entité | L'identifiant unique d'une entité, par exemple sensor.saj_pv_power. |
| Capteur | Une entité qui affiche une mesure. |
| Capteur binaire | Une entité qui est soit activée, soit désactivée, par exemple un défaut. |
| Nombre | Une entité qui contient un nombre que vous pouvez modifier. |
| Sélection | Une entité qui contient un choix dans une liste. |
| Interrupteur | Une entité que vous pouvez activer ou désactiver. |
| Heure | Une entité qui contient une heure de la journée. |
| Bouton | Une entité qui exécute une action lorsqu'on appuie dessus. |
| Activée par défaut | Indique si une entité est activée quand le système est ajouté. |
| Désactivée | Une entité que Home Assistant ne lit pas et n'affiche pas. |
| Réparation | Un avis dans Home Assistant indiquant qu'une action de votre part est nécessaire, avec un bouton Corriger. |
| Tableau de bord | Un écran de Home Assistant composé de cartes. |
| Carte | Un bloc d'un tableau de bord. |
| Carte tuile | Une carte de Home Assistant qui affiche une entité et à laquelle on peut ajouter des fonctionnalités. |
| Badge | Un petit élément de la rangée de badges en haut d'un tableau de bord. |
| Automatisation | Une règle qui fait agir Home Assistant lorsque quelque chose se produit. |
| Entrée | Une entité de Home Assistant que vous créez vous-même, par exemple une entrée de programme horaire. |
| Pièce | Une pièce ou un lieu dans lequel les appareils sont regroupés. |
| Thème | Les couleurs de l'interface de Home Assistant. |
| Langue | La langue qu'un utilisateur de Home Assistant choisit sur la page du profil. |
| Recharger | Redémarrer une seule intégration sans redémarrer Home Assistant. |
| Redémarrer | Redémarrer Home Assistant. |
| Outils de développement | Les pages de Home Assistant pour vérifier les états et appeler des actions. |
| Journal | L'enregistrement des messages de Home Assistant. |
