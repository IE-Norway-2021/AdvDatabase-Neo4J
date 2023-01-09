# Laboratory 2 – Diving deeper with Neo4j <!-- omit in toc -->

**Jade Gröli & David González León**

---

- [1. Introduction](#1-introduction)
- [2. Installation et lancement des containers](#2-installation-et-lancement-des-containers)
- [3. Description de l'architecture](#3-description-de-larchitecture)
  - [3.1. Liste des paramètres choisis](#31-liste-des-paramètres-choisis)
- [4. Description de l'application](#4-description-de-lapplication)
  - [4.1. "Nettoyage" des données](#41-nettoyage-des-données)
  - [4.2. Preprocessing des données](#42-preprocessing-des-données)
  - [4.3. Insertion dans la DB](#43-insertion-dans-la-db)
- [5. Analyse des performances](#5-analyse-des-performances)

---

# 1. Introduction

Ce repo contient le code de l'application python qui permet d'insérer les données de la base de donnée DBLP dans une base de données Neo4j. Il contient également un fichier docker-compose.yml qui permet de lancer l'application et la base de données Neo4j dans des containers docker.

# 2. Installation et lancement des containers

Pour lancer l'application entière, il faut tout d'abord avoir à la racine de ce repo un fichier db.json qui correspond aux données à insérer. Ensuite, il faut lancer la commande `docker-compose up --build` qui va lancer les containers et les lier entre eux. L'application s'exécutera alors, et annoncera une fois que l'insertion de toutes les données sera terminée.

Pour accéder à l'interface de neo4j, il faut aller sur l'adresse `localhost:7474` et se connecter avec les identifiants `neo4j` et `test`.

La base de donnée utilisée pour tester cette application est la base de donnée DBLP version 13. L'application chargera automatiquement 10'000 articles de cette base de donnée. Pour modifier cette valeur, il faut modifier la constante `MAX_NODES` dans le fichier [docker-compose.yml](docker-compose.yml). L'application n'a été testée qu'avec cette valeur ou des valeurs inférieures.

# 3. Description de l'architecture

L'architecture de cet application est composée de deux containers :

-   Un container qui contient l'application python qui va parser les données et les insérer dans la base de données.
-   Un container qui contient la base de données Neo4j qui va recevoir les données insérées par l'application python.

L'intégralité du code de l'application se trouve dans le dossier src.

## 3.1. Liste des paramètres choisis

Pour déterminer quels paramètres utiliser pour les différents noeuds de la base de donnée, nous avons parcourus le fichier dblpExample.json, qui contient un extrait de la base de donnée originale. Pour les deux noeuds à créer nous avons retenu les valeurs suivantes :

-   Noeud Author :
    -   \_id : l'identifiant de l'auteur, qui est unique
    -   name : le nom de l'auteur
-   Noeud Article
    -   \_id : l'identifiant de l'article, qui est unique
    -   title : le titre de l'article

Nous avons décidé de ne garder que ces éléments la, car ils nous paraissaient être les points essentiels de ces deux noeuds. D'autres attributs pourraient cependant être facilement ajouté dans un deuxième temps.

Nous avons également conservé les références de chaque article, afin de pouvoir créer la relation CITES entre les articles.

# 4. Description de l'application

L'application python est composée de trois parties principales décrites dans les sections suivantes.

## 4.1. "Nettoyage" des données

Le fichier json contenant l'ensemble des données est parcouru ligne par ligne. Un nombre maximum d'item à lire dans le fichier json est fixé (MAX_NODES dans le code). La fonction 'clean' parcourt le fichier ligne par ligne et enlève les caractères et les expressions qui ne sont pas reconnus dans le format json tel que les "\" ou les "NumberInt". La lecture s'arrête lorsque le nombre maximum d'item est atteint. Cette fonction fournit un nouveau fichier json syntaxiquement correct et avec le nombre d'item souhaité. C'est ce nouveau fichier json qui sera utilisé pour inséré les données dans la base de données.

Nous avons préféré cette technique au lieu d'utiliser un driver permettant de lire du bson, qui est le format original de la base de donnée, pour plusieurs raisons. La première est que le fichier n'est pas non plus complètement correct avec le format bson, notamment à cause des "\". La deuxième est que le driver ne permet pas de lire le fichier item par item, ce qui aurait nécessité de stocker l'intégralité du fichier en mémoire, ce qui n'est pas possible avec la taille de la base de donnée.

## 4.2. Preprocessing des données

Le fichier json créé à l'aide de la fonction `clean` est parcouru pour extraire les différentes données ainsi que les relations entre ces données. Ces informations sont stockées dans des tableaux : un pour les auteurs et un pour les articles. Des [dataclass](https://docs.python.org/3/library/dataclasses.html) sont créées pour stocker les informations des auteurs et des articles. Les tableaux des articles et des auteurs stockent des instances de ces classes. Les relations sont : CITES (un article cite un autre article) et AUTHORED (les auteurs qui ont écrit l'articles. Ces références sont conservées dans la dataclass de l'article.

Cette partie a posé un certain nombre de problème puisqu'en raison des limitations dû à la mémoire, il n'était pas possible d'ouvrir le fichier dans son intégralité. Pour cela, nous avons utilisé la librairie [ijson](https://pypi.org/project/ijson/) qui n'ouvre le fichier qu'item par item.

## 4.3. Insertion dans la DB

Pour insérer les données dans la base de donnée neo4j, nous avons utilisé le driver [py2neo](https://py2neo.org/2021.1/). Il offre notamment un certain nombre de fonctions qui permettent d'effectuer des insertions de donnée en bulk, ce qui permet d’accélérer les performances de notre application ([documentation](https://py2neo.org/2021.1/bulk/index.html)).

Nous insérons donc les données en utilisant ces fonctions. Nous effectuons d'abord les insertions des noeuds Author et Article avec la fonction `create_node`, puis nous créons les relations entre ces noeuds. Pour les relations, nous avons utilisé la fonction `create_relationships` qui permet d'insérer plusieurs relations en une seule requête. Nous avons utilisé cette fonction pour insérer les relations CITES et AUTHORED.

En ce qui concerne les relations CITES, nous avons remarqué qu'aucun des identifiants des articles référencés ne renvoyait vers un articles de la base de donnée si nous ne prenions pas tous les éléments du fichier donné. Nous avons donc choisi de ne pas insérer une relation CITES si l'articles référencé n'est pas dans la base de donnée. Comme les noeuds Article et Author sont tous créés avant les relations, nous pouvons vérifier si l'identifiant de l'article référencé est présent dans la base de donnée. S'il ne l'est pas, nous ne créons pas la relation CITES. Cela à pour conséquence que nous n'avons aucune relation CITES dans la base de données finale avec 10'000 noeuds. Pour 20'000 noeuds nous n'obtenons que 6 relations CITES.

# 5. Analyse des performances

Nous avons effectué deux tests de performances avec deux tailles de graphes, une fois 10'000 articles et une autre fois pour 20'000 articles. Nous avons obtenu les résultats suivants :

```bash
app_1  | Performance test result : (number of article = 10000, memory in MB = 42.547651, time in seconds = 414.07366919517517)
app_1  | Performance test result : (number of article = 20000, memory in MB = 58.702344, time in seconds = 1735.0233600139618)
```
