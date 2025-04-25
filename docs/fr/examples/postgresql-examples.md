# Exemples PostgreSQL

*[English](../../en/examples/postgresql-examples.md) | [中文](../../zh/examples/postgresql-examples.md) | Français | [Español](../../es/examples/postgresql-examples.md) | [العربية](../../ar/examples/postgresql-examples.md) | [Русский](../../ru/examples/postgresql-examples.md)*

Ce document fournit des exemples pratiques pour travailler avec des bases de données PostgreSQL en utilisant MCP Database Utilities.

## Configuration de Base

```yaml
connections:
  my-postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: my_database
    user: postgres_user
    password: postgres_password
    # Options supplémentaires
    sslmode: prefer  # Options: disable, allow, prefer, require, verify-ca, verify-full
```

## Opérations Courantes

### Lister les Schémas

**Vous**: "Listez tous les schémas dans ma base de données PostgreSQL."

**IA**: "Voici les schémas dans votre base de données PostgreSQL:
- public
- analytics
- auth
- reporting
- audit"

### Lister les Tables

**Vous**: "Listez toutes les tables dans le schéma public."

**IA**: "Voici les tables dans le schéma public:
- utilisateurs
- produits
- commandes
- categories
- fournisseurs
- inventaire"

### Afficher la Structure d'une Table

**Vous**: "Montrez-moi la structure de la table utilisateurs."

**IA**: "La table utilisateurs a la structure suivante:
- id (SERIAL, PRIMARY KEY)
- nom (VARCHAR(100), NOT NULL)
- email (VARCHAR(100), NOT NULL, UNIQUE)
- date_creation (TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT NOW())
- derniere_connexion (TIMESTAMP WITH TIME ZONE)
- statut (VARCHAR(20), DEFAULT 'actif')
- metadata (JSONB)
- role_id (INTEGER, REFERENCES roles(id))"

### Requête de Base

**Vous**: "Montrez-moi les 5 derniers utilisateurs inscrits."

**IA**: "Voici les 5 derniers utilisateurs inscrits:

| id | nom | email | date_creation |
|----|-----|-------|---------------|
| 42 | Jean Dupont | jean@example.com | 2023-11-25 14:32:15+01 |
| 41 | Marie Martin | marie@example.com | 2023-11-24 09:45:22+01 |
| 40 | Pierre Durand | pierre@example.com | 2023-11-23 18:12:05+01 |
| 39 | Sophie Lefebvre | sophie@example.com | 2023-11-22 11:30:47+01 |
| 38 | Thomas Bernard | thomas@example.com | 2023-11-21 16:08:33+01 |"

## Requêtes Avancées

### Jointure de Tables

**Vous**: "Montrez-moi les 3 dernières commandes avec les informations client et produit."

**IA**: "Voici les 3 dernières commandes avec les informations client et produit:

| commande_id | date_commande | nom_client | email_client | nom_produit | prix | quantité |
|-------------|---------------|------------|--------------|-------------|------|----------|
| 1042 | 2023-11-25 | Jean Dupont | jean@example.com | Smartphone Pro | 899,99 € | 1 |
| 1041 | 2023-11-24 | Sophie Lefebvre | sophie@example.com | Écouteurs sans fil | 129,50 € | 2 |
| 1040 | 2023-11-23 | Pierre Durand | pierre@example.com | Ordinateur portable | 1299,00 € | 1 |"

### Fonctions d'Agrégation

**Vous**: "Quel est le montant total des ventes par catégorie de produit ce mois-ci?"

**IA**: "Voici le montant total des ventes par catégorie de produit pour ce mois-ci:

| catégorie | total_ventes |
|-----------|--------------|
| Électronique | 28 456,75 € |
| Vêtements | 12 389,30 € |
| Maison et Jardin | 9 876,50 € |
| Sports et Loisirs | 7 654,25 € |
| Livres et Médias | 3 210,80 € |"

### Utilisation des CTE (Common Table Expressions)

**Vous**: "Utilisez une CTE pour trouver les clients qui ont dépensé plus que la moyenne ce mois-ci."

**IA**: "Voici les clients qui ont dépensé plus que la moyenne ce mois-ci, en utilisant une CTE:

| id_client | nom | email | total_dépensé | moyenne_globale |
|-----------|-----|-------|---------------|-----------------|
| 23 | Marie Martin | marie@example.com | 1 456,78 € | 345,67 € |
| 42 | Jean Dupont | jean@example.com | 1 245,50 € | 345,67 € |
| 15 | Thomas Bernard | thomas@example.com | 987,25 € | 345,67 € |
| 31 | Sophie Lefebvre | sophie@example.com | 876,30 € | 345,67 € |
| 8 | Pierre Durand | pierre@example.com | 654,90 € | 345,67 € |

Cette requête utilise une CTE pour calculer d'abord la moyenne des dépenses, puis trouve les clients dont les dépenses dépassent cette moyenne."

### Utilisation des Fenêtres (Window Functions)

**Vous**: "Montrez-moi le classement des produits les plus vendus par catégorie."

**IA**: "Voici le classement des produits les plus vendus par catégorie:

| catégorie | nom_produit | quantité_vendue | rang_dans_catégorie |
|-----------|-------------|-----------------|---------------------|
| Électronique | Smartphone Pro | 1245 | 1 |
| Électronique | Écouteurs sans fil | 987 | 2 |
| Électronique | Tablette Ultra | 876 | 3 |
| Vêtements | T-shirt Premium | 543 | 1 |
| Vêtements | Jean Classique | 432 | 2 |
| Vêtements | Chaussures de Sport | 321 | 3 |
| Maison et Jardin | Cafetière Automatique | 234 | 1 |
| Maison et Jardin | Set de Cuisine | 210 | 2 |
| Maison et Jardin | Lampe Design | 198 | 3 |

Cette requête utilise la fonction de fenêtrage ROW_NUMBER() pour classer les produits par quantité vendue au sein de chaque catégorie."

## Analyse de Performance

### Plan d'Exécution de Requête

**Vous**: "Expliquez le plan d'exécution pour: SELECT * FROM commandes JOIN clients ON commandes.client_id = clients.id WHERE commandes.date > '2023-01-01'"

**IA**: "Plan d'exécution pour la requête:
```
                                                   QUERY PLAN
-----------------------------------------------------------------------------------------------------------------
 Hash Join  (cost=33.38..1756.15 rows=1250 width=172)
   Hash Cond: (commandes.client_id = clients.id)
   ->  Seq Scan on commandes  (cost=0.00..1250.50 rows=1250 width=96)
         Filter: (date > '2023-01-01'::date)
   ->  Hash  (cost=18.50..18.50 rows=1150 width=76)
         ->  Seq Scan on clients  (cost=0.00..18.50 rows=1150 width=76)
```

Analyse:
1. Un scan séquentiel est effectué sur la table 'commandes' avec un filtre sur la date
2. Un scan séquentiel est effectué sur la table 'clients'
3. Une jointure de hachage est utilisée pour combiner les résultats

Recommandations d'optimisation:
- Ajouter un index sur commandes.date pour éviter le scan séquentiel
- Vérifier si un index existe déjà sur clients.id (clé primaire)"

### Statistiques de Table

**Vous**: "Obtenez les statistiques pour la table commandes."

**IA**: "Statistiques pour la table commandes:
- Nombre de lignes estimé: 15 423
- Taille de la table: 4,2 Mo
- Taille des index: 3,1 Mo
- Taux de lecture du cache: 98,5%
- Dernière VACUUM: 2023-11-20 08:15:32
- Dernière ANALYZE: 2023-11-20 08:15:32
- Bloat estimé: 3,2%
- Indices:
  * commandes_pkey (id): 1,1 Mo
  * idx_commandes_client_id (client_id): 0,8 Mo
  * idx_commandes_date (date): 0,7 Mo
  * idx_commandes_statut (statut): 0,5 Mo"

## Fonctionnalités Spécifiques à PostgreSQL

### Utilisation des Types de Données JSON/JSONB

**Vous**: "Montrez-moi les utilisateurs avec des préférences spécifiques dans leur champ metadata."

**IA**: "Voici les utilisateurs avec des préférences spécifiques dans leur champ metadata JSONB:

| id | nom | email | preferences |
|----|-----|-------|-------------|
| 42 | Jean Dupont | jean@example.com | {\"theme\": \"dark\", \"notifications\": true, \"language\": \"fr\"} |
| 23 | Marie Martin | marie@example.com | {\"theme\": \"light\", \"notifications\": false, \"language\": \"fr\"} |
| 15 | Thomas Bernard | thomas@example.com | {\"theme\": \"auto\", \"notifications\": true, \"language\": \"en\"} |

Cette requête utilise l'opérateur -> pour accéder aux propriétés JSONB et filtrer les résultats en fonction des préférences des utilisateurs."

### Utilisation des Types Géométriques

**Vous**: "Trouvez les magasins dans un rayon de 5 km autour d'un point donné."

**IA**: "Voici les magasins dans un rayon de 5 km autour du point (48.8566, 2.3522) (coordonnées de Paris):

| id | nom | adresse | distance_km |
|----|-----|---------|-------------|
| 12 | Magasin Centre | 15 Rue de Rivoli, Paris | 0,8 |
| 8 | Magasin Marais | 25 Rue des Archives, Paris | 1,2 |
| 15 | Magasin Montparnasse | 7 Rue du Départ, Paris | 2,5 |
| 23 | Magasin La Défense | 4 Place de la Défense, Puteaux | 4,7 |

Cette requête utilise le type de données POINT et la fonction ST_Distance pour calculer la distance entre les emplacements."

### Utilisation des Vues Matérialisées

**Vous**: "Quelles informations sont disponibles dans la vue matérialisée 'rapport_ventes_mensuel'?"

**IA**: "La vue matérialisée 'rapport_ventes_mensuel' contient les données suivantes:

| année | mois | catégorie | total_ventes | nombre_commandes | panier_moyen |
|-------|------|-----------|--------------|------------------|--------------|
| 2023 | 11 | Électronique | 125 456,78 € | 1245 | 100,77 € |
| 2023 | 11 | Vêtements | 87 654,32 € | 1876 | 46,72 € |
| 2023 | 11 | Maison et Jardin | 65 432,10 € | 876 | 74,69 € |
| 2023 | 10 | Électronique | 115 678,90 € | 1156 | 100,07 € |
| 2023 | 10 | Vêtements | 76 543,21 € | 1654 | 46,28 € |
| 2023 | 10 | Maison et Jardin | 54 321,09 € | 765 | 71,01 € |

Cette vue matérialisée est rafraîchie quotidiennement et fournit un résumé préagrégé des ventes par mois et par catégorie."

### Utilisation des Extensions

**Vous**: "Quelles extensions PostgreSQL sont installées dans la base de données?"

**IA**: "Les extensions suivantes sont installées dans la base de données:

1. **pg_stat_statements**
   - Fournit des statistiques d'exécution pour toutes les instructions SQL exécutées

2. **PostGIS**
   - Ajoute le support pour les objets géographiques permettant les requêtes de localisation

3. **pgcrypto**
   - Fournit des fonctions cryptographiques

4. **uuid-ossp**
   - Fournit des fonctions pour générer des UUID

5. **pg_trgm**
   - Fournit des fonctions et opérateurs pour déterminer la similarité de texte basée sur la correspondance de trigrammes

6. **hstore**
   - Fournit un type de données pour stocker des ensembles de paires clé/valeur"

## Dépannage

### Problèmes Courants

1. **Erreur "too many connections"**
   - Cause: Le nombre maximum de connexions simultanées a été atteint
   - Solution: Augmentez max_connections dans postgresql.conf ou optimisez votre application pour utiliser un pool de connexions

2. **Performances lentes**
   - Causes possibles:
     * Requêtes non optimisées
     * Indices manquants
     * VACUUM non exécuté régulièrement
     * Configuration de serveur inadéquate
   - Solutions:
     * Utilisez EXPLAIN ANALYZE pour analyser les requêtes
     * Ajoutez des indices appropriés
     * Configurez autovacuum correctement
     * Optimisez la configuration du serveur (shared_buffers, work_mem, etc.)

3. **Blocages (deadlocks)**
   - Cause: Deux transactions ou plus attendent mutuellement la libération de verrous
   - Solution: Vérifiez pg_locks et pg_stat_activity pour identifier les transactions bloquantes

### Commandes de Diagnostic Utiles

```sql
-- Voir les connexions actives
SELECT * FROM pg_stat_activity;

-- Identifier les requêtes lentes
SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;

-- Vérifier les verrous
SELECT * FROM pg_locks l JOIN pg_stat_activity a ON l.pid = a.pid;

-- Vérifier la taille des tables et des index
SELECT
  table_name,
  pg_size_pretty(table_size) AS table_size,
  pg_size_pretty(indexes_size) AS indexes_size,
  pg_size_pretty(total_size) AS total_size
FROM (
  SELECT
    table_name,
    pg_table_size(table_name) AS table_size,
    pg_indexes_size(table_name) AS indexes_size,
    pg_total_relation_size(table_name) AS total_size
  FROM (
    SELECT ('"' || table_schema || '"."' || table_name || '"') AS table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
  ) AS all_tables
) AS pretty_sizes
ORDER BY total_size DESC;
```

## Bonnes Pratiques

1. **Sécurité**
   - Utilisez des rôles avec privilèges minimaux
   - Activez SSL pour les connexions
   - Utilisez des requêtes préparées pour éviter les injections SQL
   - Considérez l'utilisation de Row-Level Security pour un contrôle d'accès granulaire

2. **Performance**
   - Indexez les colonnes fréquemment utilisées dans les clauses WHERE, JOIN et ORDER BY
   - Utilisez EXPLAIN ANALYZE pour comprendre et optimiser les plans d'exécution
   - Configurez autovacuum pour maintenir la santé de la base de données
   - Utilisez des vues matérialisées pour les requêtes complexes fréquemment exécutées

3. **Maintenance**
   - Planifiez des sauvegardes régulières avec pg_dump
   - Configurez la réplication pour la haute disponibilité
   - Surveillez régulièrement les performances avec pg_stat_statements
   - Mettez à jour régulièrement vers les dernières versions mineures pour les correctifs de sécurité
