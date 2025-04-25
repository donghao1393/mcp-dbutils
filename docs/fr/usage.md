# Guide d'Utilisation

*[English](../en/usage.md) | [中文](../zh/usage.md) | Français | [Español](../es/usage.md) | [العربية](../ar/usage.md) | [Русский](../ru/usage.md)*

Ce document fournit des instructions détaillées pour utiliser MCP Database Utilities, vous aidant à exploiter pleinement ses capacités pour l'analyse de données avec l'IA.

## Flux de Travail de Base

Le flux de travail de base pour utiliser MCP Database Utilities est le suivant :

1. **Configurer les Connexions à la Base de Données** : Définissez vos connexions à la base de données dans le fichier `config.yaml`
2. **Démarrer le Service MCP** : Lancez le service via la configuration de votre client IA
3. **Interagir avec l'IA** : Posez des questions sur vos bases de données en langage naturel
4. **Voir les Résultats** : L'IA exécutera les requêtes nécessaires et présentera les résultats dans un format facile à comprendre

## Outils Disponibles

MCP Database Utilities fournit plusieurs outils que votre IA peut utiliser :

### dbutils-list-connections

Liste toutes les connexions de base de données disponibles définies dans votre configuration.

**Exemple d'Interaction** :

**Vous** : "Quelles connexions de base de données ai-je à disposition ?"

**IA** : "Je vais vérifier vos connexions de base de données disponibles. Voici ce que j'ai trouvé :

1. **postgres-db**
   - Type : PostgreSQL
   - Hôte : localhost
   - Base de données : analytics
   - Utilisateur : analyst

2. **sqlite-db**
   - Type : SQLite
   - Chemin : /path/to/database.db

3. **mysql-db**
   - Type : MySQL
   - Hôte : db.example.com
   - Base de données : customer_data
   - Utilisateur : reader"

### dbutils-list-tables

Liste toutes les tables dans la base de données spécifiée.

**Exemple d'Interaction** :

**Vous** : "Listez toutes les tables dans ma base de données postgres."

**IA** : "Je vais vérifier cela pour vous. Voici les tables dans votre base de données postgres :
- clients
- produits
- commandes
- inventaire
- employes"

### dbutils-run-query

Exécute des requêtes SQL sur la base de données spécifiée (opérations SELECT uniquement).

**Exemple d'Interaction** :

**Vous** : "Interrogez le nombre de clients qui se sont inscrits au cours des 30 derniers jours."

**IA** : "Laissez-moi vérifier cela pour vous. Selon les données, il y a eu 42 nouvelles inscriptions de clients au cours des 30 derniers jours."

### dbutils-get-stats

Obtient des statistiques sur une table, telles que le nombre de lignes, la taille et les statistiques de colonnes.

**Exemple d'Interaction** :

**Vous** : "Obtenez des statistiques pour la table produits."

**IA** : "Voici les statistiques pour la table produits :
- Total des lignes : 1 245
- Taille de la table : 2,3 Mo
- Statistiques des colonnes :
  * product_id : 1 245 valeurs uniques
  * catégorie : 8 catégories distinctes
  * prix : moyenne 45,99 €, min 5,99 €, max 299,99 €"

### dbutils-list-constraints

Liste les contraintes pour une table, telles que les clés primaires, les clés étrangères, etc.

**Exemple d'Interaction** :

**Vous** : "Montrez les contraintes pour la table commandes."

**IA** : "La table commandes a les contraintes suivantes :
- Clé primaire : order_id
- Clé étrangère : customer_id référence clients(id)
- Clé étrangère : product_id référence produits(id)
- Contrainte de vérification : order_amount > 0"

### dbutils-explain-query

Obtient le plan d'exécution de la requête et les estimations de coût.

**Exemple d'Interaction** :

**Vous** : "Expliquez le plan d'exécution pour cette requête : SELECT * FROM commandes WHERE customer_id = 123"

**IA** : "Le plan d'exécution pour cette requête est :
1. Scan d'index : utilisation de l'index customer_id_idx
2. Coût estimé : 12,5
3. Lignes estimées : 8
4. Condition de filtre : customer_id = 123"

### dbutils-get-performance

Obtient des métriques de performance de la base de données.

**Exemple d'Interaction** :

**Vous** : "Obtenez des métriques de performance pour la base de données."

**IA** : "Métriques de performance actuelles de la base de données :
- Temps d'exécution de la requête : 45 ms en moyenne
- Taux de succès du cache : 87 %
- Connexions actives : 3
- Taux d'erreur récent : 0,2 %"

### dbutils-analyze-query

Analyse les performances des requêtes SQL et fournit des suggestions d'optimisation.

**Exemple d'Interaction** :

**Vous** : "Analysez cette requête : SELECT * FROM commandes JOIN clients ON commandes.customer_id = clients.id WHERE order_date > '2023-01-01'"

**IA** : "Résultats de l'analyse de la requête :
1. Problème de performance : L'utilisation de SELECT * récupère des colonnes inutiles
2. Index manquant : Pas d'index sur la colonne order_date
3. Suggestions d'optimisation :
   - Sélectionnez uniquement les colonnes nécessaires
   - Ajoutez un index sur la colonne order_date
   - Envisagez d'ajouter une clause LIMIT pour restreindre le nombre de résultats"

## Scénarios d'Utilisation Courants

### 1. Exploration de Données

**Vous** : "Je veux comprendre la structure de ma base de données."

**IA** : "Je peux vous aider à explorer la structure de votre base de données. Laissez-moi lister toutes les tables, puis vous pourrez en choisir une pour en savoir plus sur sa structure."

**Vous** : "D'accord, listez toutes les tables."

**IA** : "Votre base de données contient les tables suivantes :
- clients
- produits
- commandes
- inventaire
- employes

Sur quelle table souhaitez-vous en savoir plus ?"

**Vous** : "Parlez-moi de la structure de la table clients."

**IA** : "La table clients a la structure suivante :
- id (entier, clé primaire)
- nom (varchar(100), non null)
- email (varchar(100), unique, non null)
- date_inscription (date, non null)
- derniere_connexion (timestamp)
- statut (enum : 'actif', 'inactif', 'suspendu')"

### 2. Analyse de Données

**Vous** : "Analysez les tendances des ventes au cours des 6 derniers mois."

**IA** : "Je vais analyser les tendances des ventes au cours des 6 derniers mois. Laissez-moi exécuter quelques requêtes..."

[L'IA exécute plusieurs requêtes, analysant les données de vente]

**IA** : "Basé sur l'analyse des 6 derniers mois :
1. Ventes totales : 1 245 678 €, en hausse de 15 % par rapport aux 6 mois précédents
2. Produit le plus vendu : Produit X, représentant 23 % des ventes totales
3. Périodes de pointe des ventes : vendredis et samedis, représentant 45 % des ventes totales
4. Taux de fidélisation des clients : 78 %, en hausse de 5 % par rapport aux 6 mois précédents"

### 3. Analyse Inter-Bases de Données

**Vous** : "Comparez la structure de la table utilisateurs entre les bases de données de production et de test."

**IA** : "Je vais comparer la structure de la table utilisateurs entre les deux bases de données..."

[L'IA interroge les deux bases de données pour les structures de table]

**IA** : "Différences dans la structure de la table utilisateurs entre les bases de données de production et de test :
1. La production a une colonne supplémentaire 'derniere_ip_connexion' (varchar(45))
2. La colonne 'email' de la base de données de test n'a pas de contrainte unique
3. La production a un index supplémentaire : idx_user_status
4. La base de données de test manque la contrainte de clé étrangère : fk_user_role"

## Meilleures Pratiques

### Optimisation des Requêtes

1. **Limiter la Taille des Résultats** : Utilisez des clauses LIMIT pour restreindre le nombre de lignes retournées
2. **Sélectionner Uniquement les Colonnes Nécessaires** : Évitez d'utiliser SELECT *
3. **Utiliser des Colonnes Indexées** : Utilisez des colonnes avec des index dans les clauses WHERE
4. **Éviter les Calculs Complexes** : Déplacez les calculs complexes vers la couche application

### Recommandations de Sécurité

1. **Utiliser des Comptes en Lecture Seule** : Créez des comptes de base de données dédiés en lecture seule pour l'accès IA
2. **Limiter l'Accès aux Tables** : Accordez l'accès uniquement aux tables nécessaires
3. **Utiliser SSL/TLS** : Activez le chiffrement pour les connexions à distance à la base de données
4. **Faire Pivoter les Mots de Passe Régulièrement** : Changez périodiquement les mots de passe de la base de données

### Optimisation des Performances

1. **Configuration du Pool de Connexions** : Ajustez la taille du pool de connexions en fonction de votre utilisation
2. **Paramètres de Délai d'Attente des Requêtes** : Définissez des durées de délai d'attente raisonnables pour les requêtes
3. **Mise en Cache des Résultats** : Envisagez la mise en cache pour les données fréquemment interrogées
4. **Surveiller les Performances** : Vérifiez régulièrement les métriques de performance pour identifier les problèmes potentiels

## Dépannage

Si vous rencontrez des problèmes pendant l'utilisation, consultez la section de dépannage dans le [Guide d'Installation](installation.md) ou consultez la [Documentation Technique](technical/architecture.md) pour des informations plus détaillées.
