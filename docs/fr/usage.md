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

Liste toutes les connexions de base de données disponibles avec des informations détaillées, notamment le type de base de données, l'hôte, le port et le nom de la base de données, tout en masquant les informations sensibles comme les mots de passe. Le paramètre optionnel check_status permet de vérifier si chaque connexion est disponible, bien que cela puisse augmenter le temps de réponse. Utilisez cet outil lorsque vous devez comprendre les ressources de base de données disponibles ou diagnostiquer des problèmes de connexion.

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

Liste toutes les tables dans la connexion de base de données spécifiée avec les noms de tables, les URI et les descriptions disponibles, regroupées par type de base de données pour une identification facile. Cet outil est utile pour explorer la structure de la base de données et comprendre quelles tables sont disponibles pour l'analyse.

**Exemple d'Interaction** :

**Vous** : "Listez toutes les tables dans ma base de données postgres."

**IA** : "Je vais vérifier cela pour vous. Voici les tables dans votre base de données postgres :
- clients
- produits
- commandes
- inventaire
- employes"

### dbutils-run-query

Exécute des requêtes SQL en lecture seule (SELECT uniquement) sur la base de données spécifiée, avec prise en charge de requêtes complexes, notamment JOIN, GROUP BY et fonctions d'agrégation, renvoyant des résultats structurés avec des noms de colonnes et des lignes de données. Cet outil est essentiel pour extraire des informations spécifiques des bases de données et effectuer des analyses personnalisées.

**Exemple d'Interaction** :

**Vous** : "Interrogez le nombre de clients qui se sont inscrits au cours des 30 derniers jours."

**IA** : "Laissez-moi vérifier cela pour vous. Selon les données, il y a eu 42 nouvelles inscriptions de clients au cours des 30 derniers jours."

### dbutils-describe-table

Fournit des informations détaillées sur la structure d'une table, notamment les noms de colonnes, les types de données, la nullabilité, les valeurs par défaut et les commentaires dans un format facile à lire. Cet outil est particulièrement utile pour comprendre le schéma d'une table avant d'exécuter des requêtes ou d'analyser des données.

**Exemple d'Interaction** :

**Vous** : "Décrivez la structure de la table clients."

**IA** : "Voici la structure de la table clients :
| Colonne | Type | Nullable | Défaut | Description |
|---------|------|----------|--------|-------------|
| id | INTEGER | Non | NULL | Identifiant unique du client |
| nom | VARCHAR(100) | Non | NULL | Nom complet du client |
| email | VARCHAR(100) | Non | NULL | Adresse email (unique) |
| date_inscription | DATE | Non | CURRENT_DATE | Date d'inscription |
| derniere_connexion | TIMESTAMP | Oui | NULL | Horodatage de la dernière connexion |
| statut | ENUM | Non | 'actif' | Statut du compte (actif, inactif, suspendu) |"

### dbutils-get-ddl

Récupère l'instruction DDL (Data Definition Language) complète pour créer la table spécifiée, y compris toutes les définitions de colonnes, contraintes et index. Cet outil est utile pour comprendre la définition exacte d'une table ou pour recréer une structure de table similaire dans un autre environnement.

**Exemple d'Interaction** :

**Vous** : "Montrez-moi le DDL pour la table commandes."

**IA** : "Voici l'instruction DDL pour la table commandes :
```sql
CREATE TABLE commandes (
  order_id INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT NOT NULL,
  order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount > 0),
  status VARCHAR(20) NOT NULL DEFAULT 'en attente',
  FOREIGN KEY (customer_id) REFERENCES clients(id)
);

CREATE INDEX idx_order_date ON commandes(order_date);
CREATE INDEX idx_customer_id ON commandes(customer_id);
```"

### dbutils-list-indexes

Liste tous les index sur la table spécifiée, y compris les noms d'index, les types (unique/non unique), les méthodes d'index et les colonnes incluses, regroupés par nom d'index. Cet outil est utile pour comprendre comment une table est indexée, ce qui peut aider à optimiser les requêtes et à améliorer les performances.

**Exemple d'Interaction** :

**Vous** : "Quels index existent sur la table produits ?"

**IA** : "Voici les index sur la table produits :
1. **pk_product_id** (Primaire)
   - Colonnes : product_id
   - Type : B-tree
   - Unique : Oui

2. **idx_category** (Secondaire)
   - Colonnes : category_id
   - Type : B-tree
   - Unique : Non

3. **idx_product_name** (Secondaire)
   - Colonnes : name
   - Type : B-tree
   - Unique : Non

4. **idx_price_category** (Secondaire)
   - Colonnes : price, category_id
   - Type : B-tree
   - Unique : Non"

### dbutils-get-stats

Récupère des informations statistiques sur la table, notamment le nombre estimé de lignes, la longueur moyenne des lignes, la taille des données et la taille de l'index. Ces statistiques sont utiles pour comprendre la volumétrie des données et planifier des optimisations de performance.

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

Liste toutes les contraintes sur la table, y compris les clés primaires, les clés étrangères, les contraintes uniques et les contraintes de vérification, avec les tables et colonnes référencées pour les clés étrangères. Cet outil est utile pour comprendre les relations entre les tables et les règles d'intégrité des données.

**Exemple d'Interaction** :

**Vous** : "Montrez les contraintes pour la table commandes."

**IA** : "La table commandes a les contraintes suivantes :
- Clé primaire : order_id
- Clé étrangère : customer_id référence clients(id)
- Clé étrangère : product_id référence produits(id)
- Contrainte de vérification : order_amount > 0"

### dbutils-explain-query

Fournit le plan d'exécution d'une requête SQL, montrant comment le moteur de base de données traitera la requête, y compris les méthodes d'accès, les types de jointure et les coûts estimés. Cet outil est essentiel pour comprendre et optimiser les performances des requêtes complexes.

**Exemple d'Interaction** :

**Vous** : "Expliquez le plan d'exécution pour cette requête : SELECT * FROM commandes WHERE customer_id = 123"

**IA** : "Le plan d'exécution pour cette requête est :
1. Scan d'index : utilisation de l'index customer_id_idx
2. Coût estimé : 12,5
3. Lignes estimées : 8
4. Condition de filtre : customer_id = 123"

### dbutils-get-performance

Récupère les métriques de performance pour la connexion à la base de données, notamment le nombre de requêtes, le temps d'exécution moyen, l'utilisation de la mémoire et les statistiques d'erreur. Ces informations sont précieuses pour surveiller la santé de la base de données et identifier les goulots d'étranglement potentiels.

**Exemple d'Interaction** :

**Vous** : "Obtenez des métriques de performance pour la base de données."

**IA** : "Métriques de performance actuelles de la base de données :
- Temps d'exécution de la requête : 45 ms en moyenne
- Taux de succès du cache : 87 %
- Connexions actives : 3
- Taux d'erreur récent : 0,2 %"

### dbutils-analyze-query

Analyse les caractéristiques de performance d'une requête SQL, fournissant un plan d'exécution, un temps d'exécution réel et des recommandations d'optimisation spécifiques. Cet outil va au-delà de l'explication simple en identifiant les problèmes potentiels et en suggérant des améliorations concrètes pour accélérer l'exécution des requêtes.

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
