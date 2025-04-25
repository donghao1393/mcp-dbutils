# Exemples MySQL

*[English](../../en/examples/mysql-examples.md) | [中文](../../zh/examples/mysql-examples.md) | Français | [Español](../../es/examples/mysql-examples.md) | [العربية](../../ar/examples/mysql-examples.md) | [Русский](../../ru/examples/mysql-examples.md)*

Ce document fournit des exemples pratiques pour travailler avec des bases de données MySQL en utilisant MCP Database Utilities.

## Configuration de Base

```yaml
connections:
  my-mysql:
    type: mysql
    host: localhost
    port: 3306
    database: my_database
    user: mysql_user
    password: mysql_password
    charset: utf8mb4  # Recommandé pour le support complet d'Unicode
```

## Opérations Courantes

### Lister les Tables

**Vous**: "Listez toutes les tables dans ma base de données MySQL."

**IA**: "Voici les tables dans votre base de données MySQL:
- utilisateurs
- produits
- commandes
- catégories
- fournisseurs
- inventaire"

### Afficher la Structure d'une Table

**Vous**: "Montrez-moi la structure de la table utilisateurs."

**IA**: "La table utilisateurs a la structure suivante:
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- nom (VARCHAR(100), NOT NULL)
- email (VARCHAR(100), NOT NULL, UNIQUE)
- date_creation (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP)
- derniere_connexion (DATETIME)
- statut (ENUM('actif', 'inactif', 'suspendu'), DEFAULT 'actif')
- role_id (INT, FOREIGN KEY references roles(id))"

### Requête de Base

**Vous**: "Montrez-moi les 5 derniers utilisateurs inscrits."

**IA**: "Voici les 5 derniers utilisateurs inscrits:

| id | nom | email | date_creation |
|----|-----|-------|---------------|
| 42 | Jean Dupont | jean@example.com | 2023-11-25 14:32:15 |
| 41 | Marie Martin | marie@example.com | 2023-11-24 09:45:22 |
| 40 | Pierre Durand | pierre@example.com | 2023-11-23 18:12:05 |
| 39 | Sophie Lefebvre | sophie@example.com | 2023-11-22 11:30:47 |
| 38 | Thomas Bernard | thomas@example.com | 2023-11-21 16:08:33 |"

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

### Utilisation des Sous-requêtes

**Vous**: "Quels clients ont dépensé plus que la moyenne ce mois-ci?"

**IA**: "Voici les clients qui ont dépensé plus que la moyenne ce mois-ci:

| id_client | nom | email | total_dépensé | moyenne_globale |
|-----------|-----|-------|---------------|-----------------|
| 23 | Marie Martin | marie@example.com | 1 456,78 € | 345,67 € |
| 42 | Jean Dupont | jean@example.com | 1 245,50 € | 345,67 € |
| 15 | Thomas Bernard | thomas@example.com | 987,25 € | 345,67 € |
| 31 | Sophie Lefebvre | sophie@example.com | 876,30 € | 345,67 € |
| 8 | Pierre Durand | pierre@example.com | 654,90 € | 345,67 € |"

## Analyse de Performance

### Plan d'Exécution de Requête

**Vous**: "Expliquez le plan d'exécution pour: SELECT * FROM commandes JOIN clients ON commandes.client_id = clients.id WHERE commandes.date > '2023-01-01'"

**IA**: "Plan d'exécution pour la requête:
```
+----+-------------+------------+------------+--------+---------------+---------+---------+----------------------+------+----------+-------+
| id | select_type | table      | partitions | type   | possible_keys | key     | key_len | ref                  | rows | filtered | Extra |
+----+-------------+------------+------------+--------+---------------+---------+---------+----------------------+------+----------+-------+
|  1 | SIMPLE      | commandes  | NULL       | range  | idx_date      | idx_date| 5       | NULL                 | 1250 | 100.00   | Using where |
|  1 | SIMPLE      | clients    | NULL       | eq_ref | PRIMARY       | PRIMARY | 4       | db.commandes.client_id | 1    | 100.00   | NULL  |
+----+-------------+------------+------------+--------+---------------+---------+---------+----------------------+------+----------+-------+
```

Cette requête utilise:
1. Un scan de plage sur la table 'commandes' en utilisant l'index 'idx_date'
2. Une recherche par clé primaire sur la table 'clients' pour chaque ligne correspondante de 'commandes'
3. Estimation: environ 1250 lignes seront examinées dans la table 'commandes'"

### Statistiques de Table

**Vous**: "Obtenez les statistiques pour la table commandes."

**IA**: "Statistiques pour la table commandes:
- Nombre de lignes: 15 423
- Taille de la table: 4,2 Mo
- Taille moyenne de ligne: 285 octets
- Indices:
  * PRIMARY (id): 1,1 Mo
  * idx_client_id (client_id): 0,8 Mo
  * idx_date (date): 0,7 Mo
  * idx_statut (statut): 0,4 Mo
- Fragmentation: 2,3%
- Dernier ANALYZE TABLE: 2023-11-20 08:15:32"

## Fonctionnalités Spécifiques à MySQL

### Utilisation des Procédures Stockées

**Vous**: "Pouvez-vous me montrer comment appeler la procédure stockée 'get_client_orders'?"

**IA**: "Pour appeler la procédure stockée 'get_client_orders' qui récupère toutes les commandes d'un client spécifique, vous pouvez utiliser:

```sql
CALL get_client_orders(42);
```

Résultat:

| commande_id | date | montant | statut |
|-------------|------|---------|--------|
| 1042 | 2023-11-25 | 899,99 € | livré |
| 987 | 2023-10-12 | 245,50 € | livré |
| 856 | 2023-09-03 | 78,25 € | livré |
| 743 | 2023-08-17 | 129,99 € | livré |

Cette procédure stockée accepte un paramètre client_id et renvoie toutes les commandes associées à ce client."

### Utilisation des Vues

**Vous**: "Quelles informations sont disponibles dans la vue 'client_summary'?"

**IA**: "La vue 'client_summary' fournit un résumé des activités de chaque client:

| client_id | nom | email | total_commandes | montant_total | derniere_commande | statut_fidelite |
|-----------|-----|-------|-----------------|---------------|-------------------|-----------------|
| 42 | Jean Dupont | jean@example.com | 12 | 3 456,78 € | 2023-11-25 | Gold |
| 23 | Marie Martin | marie@example.com | 8 | 2 345,67 € | 2023-11-24 | Silver |
| 15 | Thomas Bernard | thomas@example.com | 5 | 1 234,56 € | 2023-11-20 | Bronze |

Cette vue combine des données des tables clients, commandes et programme_fidelite pour fournir une vue d'ensemble de l'activité de chaque client."

### Utilisation des Événements

**Vous**: "Y a-t-il des événements programmés dans la base de données?"

**IA**: "Oui, voici les événements programmés dans la base de données:

1. **daily_sales_report**
   - Fréquence: Quotidienne à 23:00
   - Description: Génère un rapport quotidien des ventes et l'insère dans la table 'rapports_ventes'
   
2. **monthly_customer_cleanup**
   - Fréquence: Le 1er de chaque mois à 02:00
   - Description: Archive les clients inactifs depuis plus de 12 mois
   
3. **hourly_inventory_check**
   - Fréquence: Toutes les heures
   - Description: Vérifie les niveaux d'inventaire et génère des alertes pour les produits en rupture de stock"

## Dépannage

### Problèmes Courants

1. **Erreur "Too many connections"**
   - Cause: Le nombre maximum de connexions simultanées a été atteint
   - Solution: Augmentez max_connections dans my.cnf ou optimisez votre application pour utiliser un pool de connexions

2. **Erreur "Lock wait timeout exceeded"**
   - Cause: Une transaction attend trop longtemps pour acquérir un verrou
   - Solution: Vérifiez les transactions longues ou bloquées avec `SHOW PROCESSLIST` et optimisez vos transactions

3. **Performances lentes**
   - Causes possibles:
     * Requêtes non optimisées
     * Indices manquants
     * Configuration de serveur inadéquate
   - Solutions:
     * Utilisez EXPLAIN pour analyser les requêtes
     * Ajoutez des indices appropriés
     * Optimisez la configuration du serveur (innodb_buffer_pool_size, etc.)

### Commandes de Diagnostic Utiles

```sql
-- Voir les processus en cours
SHOW PROCESSLIST;

-- Vérifier l'état des tables
CHECK TABLE nom_table;

-- Optimiser une table
OPTIMIZE TABLE nom_table;

-- Voir les variables système
SHOW VARIABLES LIKE '%buffer%';

-- Voir les statistiques de performance
SHOW ENGINE INNODB STATUS;
```

## Bonnes Pratiques

1. **Sécurité**
   - Utilisez des comptes avec privilèges minimaux
   - Activez SSL pour les connexions
   - Utilisez des requêtes préparées pour éviter les injections SQL

2. **Performance**
   - Indexez les colonnes fréquemment utilisées dans les clauses WHERE, JOIN et ORDER BY
   - Évitez SELECT * et ne sélectionnez que les colonnes nécessaires
   - Utilisez EXPLAIN pour analyser et optimiser les requêtes

3. **Maintenance**
   - Planifiez des sauvegardes régulières
   - Configurez la réplication pour la haute disponibilité
   - Surveillez régulièrement les performances et l'utilisation des ressources
