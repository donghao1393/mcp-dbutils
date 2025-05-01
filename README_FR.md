# MCP Database Utilities

<!-- Badges d'état du projet -->
[![État de la construction](https://img.shields.io/github/workflow/status/donghao1393/mcp-dbutils/Quality%20Assurance?label=tests)](https://github.com/donghao1393/mcp-dbutils/actions)
[![Couverture](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/donghao1393/bdd0a63ec2a816539ff8c136ceb41e48/raw/coverage.json)](https://github.com/donghao1393/mcp-dbutils/actions)
[![Statut de la porte de qualité](https://sonarcloud.io/api/project_badges/measure?project=donghao1393_mcp-dbutils&metric=alert_status)](https://sonarcloud.io/dashboard?id=donghao1393_mcp-dbutils)

<!-- Badges de version et d'installation -->
[![Version PyPI](https://img.shields.io/pypi/v/mcp-dbutils)](https://pypi.org/project/mcp-dbutils/)
[![Téléchargements PyPI](https://img.shields.io/pypi/dm/mcp-dbutils)](https://pypi.org/project/mcp-dbutils/)
[![Smithery](https://smithery.ai/badge/@donghao1393/mcp-dbutils)](https://smithery.ai/server/@donghao1393/mcp-dbutils)

<!-- Badges de spécifications techniques -->
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Licence](https://img.shields.io/github/license/donghao1393/mcp-dbutils)](LICENSE)
[![Étoiles GitHub](https://img.shields.io/github/stars/donghao1393/mcp-dbutils?style=social)](https://github.com/donghao1393/mcp-dbutils/stargazers)

[English](README_EN.md) | [中文](README.md) | [Español](README_ES.md) | [العربية](README_AR.md) | [Русский](README_RU.md) | [Documentation](#documentation)

## Introduction

MCP Database Utilities est un service MCP tout-en-un qui permet à votre IA d'effectuer des analyses de données en accédant à différents types de bases de données (SQLite, MySQL, PostgreSQL, et plus) avec une configuration de connexion unifiée de manière sécurisée.

Considérez-le comme un pont sécurisé entre les systèmes d'IA et vos bases de données, permettant à l'IA de lire et d'analyser vos données sans accès direct à la base de données ou sans risquer de modifications des données.

### Caractéristiques clés

- **Sécurité d'abord** : Opérations strictement en lecture seule, pas d'accès direct à la base de données, connexions isolées, connectivité à la demande, délais d'expiration automatiques
- **Protection de la vie privée** : Traitement local, exposition minimale des données, protection des identifiants, masquage des données sensibles
- **Support de multiples bases de données** : Connectez-vous à SQLite, MySQL, PostgreSQL avec la même interface
- **Configuration simple** : Un seul fichier YAML pour toutes vos connexions de base de données
- **Capacités avancées** : Exploration de tables, analyse de schéma et exécution de requêtes

> 🔒 **Note de sécurité** : MCP Database Utilities est construit avec une architecture axée sur la sécurité, ce qui le rend idéal pour les entreprises, les startups et les particuliers qui valorisent la protection des données. En savoir plus sur notre [architecture de sécurité](docs/fr/technical/security.md).

## Démarrage rapide

Nous proposons plusieurs méthodes d'installation, notamment uvx, Docker et Smithery. Pour des étapes détaillées d'installation et de configuration, consultez le [Guide d'installation](docs/fr/installation.md).

### Étapes de base

1. **Installer** : Choisissez votre méthode d'installation préférée ([instructions détaillées](docs/fr/installation.md))
2. **Configurer** : Créez un fichier YAML avec les informations de connexion à votre base de données ([guide de configuration](docs/fr/configuration.md))
3. **Connecter** : Ajoutez la configuration à votre client IA
4. **Utiliser** : Commencez à interagir avec vos bases de données ([guide d'utilisation](docs/fr/usage.md))

## Exemples d'interactions

**Vous** : "Pouvez-vous lister toutes les tables dans ma base de données my-postgres ?"

**IA** : "Je vais vérifier cela pour vous. Voici les tables dans votre base de données my-postgres :
- clients
- produits
- commandes
- inventaire
- employés"

**Vous** : "À quoi ressemble la table clients ?"

**IA** : "La table clients a la structure suivante :
- id (entier, clé primaire)
- nom (texte)
- email (texte)
- date_inscription (date)
- dernier_achat (date)
- total_depense (numérique)"

**Vous** : "Combien de clients ont effectué des achats le mois dernier ?"

**IA** : "Laissez-moi exécuter une requête pour le savoir... Selon les données, 128 clients ont effectué des achats le mois dernier. La valeur totale de ces achats était de 25 437,82 €."

## Outils disponibles

MCP Database Utilities fournit plusieurs outils que votre IA peut utiliser :

- **dbutils-list-connections** : Liste toutes les connexions de base de données disponibles avec des informations détaillées, notamment le type de base de données, l'hôte, le port et le nom de la base de données, tout en masquant les informations sensibles comme les mots de passe.
- **dbutils-list-tables** : Liste toutes les tables de la connexion de base de données spécifiée avec les noms de tables, les URI et les descriptions disponibles, regroupées par type de base de données pour une identification facile.
- **dbutils-run-query** : Exécute des requêtes SQL en lecture seule (SELECT uniquement) avec prise en charge de requêtes complexes, notamment JOIN, GROUP BY et fonctions d'agrégation, renvoyant des résultats structurés avec des noms de colonnes et des lignes de données.
- **dbutils-describe-table** : Fournit des informations détaillées sur la structure d'une table, notamment les noms de colonnes, les types de données, la nullabilité, les valeurs par défaut et les commentaires dans un format facile à lire.
- **dbutils-get-ddl** : Récupère l'instruction DDL (Data Definition Language) complète pour créer la table spécifiée, y compris toutes les définitions de colonnes, contraintes et index.
- **dbutils-list-indexes** : Liste tous les index sur la table spécifiée, y compris les noms d'index, les types (unique/non unique), les méthodes d'index et les colonnes incluses, regroupés par nom d'index.
- **dbutils-get-stats** : Récupère des informations statistiques sur la table, notamment le nombre estimé de lignes, la longueur moyenne des lignes, la taille des données et la taille de l'index.
- **dbutils-list-constraints** : Liste toutes les contraintes sur la table, y compris les clés primaires, les clés étrangères, les contraintes uniques et les contraintes de vérification, avec les tables et colonnes référencées pour les clés étrangères.
- **dbutils-explain-query** : Fournit le plan d'exécution d'une requête SQL, montrant comment le moteur de base de données traitera la requête, y compris les méthodes d'accès, les types de jointure et les coûts estimés.
- **dbutils-get-performance** : Obtient des métriques de performance de la base de données, notamment le nombre de requêtes, le temps d'exécution moyen, l'utilisation de la mémoire et les statistiques d'erreur.
- **dbutils-analyze-query** : Analyse les caractéristiques de performance d'une requête SQL, fournissant un plan d'exécution, un temps d'exécution réel et des recommandations d'optimisation spécifiques.

Pour des descriptions détaillées et des exemples d'utilisation de ces outils, consultez le [Guide d'utilisation](docs/fr/usage.md).

## Documentation

### Mise en route
- [Guide d'installation](docs/fr/installation.md) - Étapes d'installation détaillées et instructions de configuration
- [Guide d'installation spécifique à la plateforme](docs/fr/installation-platform-specific.md) - Instructions d'installation pour différents systèmes d'exploitation
- [Guide de configuration](docs/fr/configuration.md) - Exemples de configuration de connexion à la base de données et meilleures pratiques
- [Guide d'utilisation](docs/fr/usage.md) - Flux de travail de base et scénarios d'utilisation courants

### Documentation technique
- [Conception de l'architecture](docs/fr/technical/architecture.md) - Architecture du système et composants
- [Architecture de sécurité](docs/fr/technical/security.md) - Fonctionnalités de sécurité et mécanismes de protection
- [Guide de développement](docs/fr/technical/development.md) - Qualité du code et flux de travail de développement
- [Guide de test](docs/fr/technical/testing.md) - Framework de test et meilleures pratiques
- [Intégration SonarCloud](docs/fr/technical/sonarcloud-integration.md) - Guide d'intégration SonarCloud et IA

### Documentation d'exemples
- [Exemples SQLite](docs/fr/examples/sqlite-examples.md) - Exemples d'opérations de base de données SQLite
- [Exemples PostgreSQL](docs/fr/examples/postgresql-examples.md) - Exemples d'opérations de base de données PostgreSQL
- [Exemples MySQL](docs/fr/examples/mysql-examples.md) - Exemples d'opérations de base de données MySQL
- [Interactions LLM avancées](docs/fr/examples/advanced-llm-interactions.md) - Exemples d'interactions avancées avec divers LLM

### Support et commentaires
- [Problèmes GitHub](https://github.com/donghao1393/mcp-dbutils/issues) - Signaler des problèmes ou demander des fonctionnalités
- [Smithery](https://smithery.ai/server/@donghao1393/mcp-dbutils) - Installation et mises à jour simplifiées

## Historique des étoiles

[![Graphique d'historique des étoiles](https://starchart.cc/donghao1393/mcp-dbutils.svg?variant=adaptive)](https://starchart.cc/donghao1393/mcp-dbutils)

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.
