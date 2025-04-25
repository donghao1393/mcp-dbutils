# Exemples SQLite

*[English](../../en/examples/sqlite-examples.md) | [中文](../../zh/examples/sqlite-examples.md) | Français | [Español](../../es/examples/sqlite-examples.md) | [العربية](../../ar/examples/sqlite-examples.md) | [Русский](../../ru/examples/sqlite-examples.md)*

Ce document fournit des exemples pratiques pour travailler avec des bases de données SQLite en utilisant MCP Database Utilities.

## Configuration de base

```yaml
connections:
  my-sqlite:
    type: sqlite
    path: /path/to/database.db
```

## Opérations courantes

### Lister les tables

**Vous**: "Listez toutes les tables dans ma base de données SQLite."

**IA**: "Voici les tables dans votre base de données SQLite:
- utilisateurs
- produits
- commandes
- catégories"

### Afficher la structure d'une table

**Vous**: "Montrez-moi la structure de la table utilisateurs."

**IA**: "La table utilisateurs a la structure suivante:
- id (INTEGER, PRIMARY KEY)
- username (TEXT, NOT NULL)
- email (TEXT, NOT NULL, UNIQUE)
- created_at (TIMESTAMP)
- last_login (TIMESTAMP)
- status (TEXT)"

### Requête de base

**Vous**: "Montrez-moi les 5 premiers utilisateurs par date de dernière connexion."

**IA**: "Voici les 5 premiers utilisateurs par date de dernière connexion:

| id | username | email | last_login |
|----|----------|-------|------------|
| 42 | johndoe | john@example.com | 2023-11-25 14:32:15 |
| 17 | janedoe | jane@example.com | 2023-11-24 09:45:22 |
| 31 | bobsmith | bob@example.com | 2023-11-23 18:12:05 |
| 8 | alicejones | alice@example.com | 2023-11-22 11:30:47 |
| 53 | mikebrown | mike@example.com | 2023-11-21 16:08:33 |"

## Requêtes avancées

### Jointure de tables

**Vous**: "Montrez-moi les 3 dernières commandes avec les informations utilisateur."

**IA**: "Voici les 3 dernières commandes avec les informations utilisateur:

| order_id | order_date | username | email | total_amount |
|----------|------------|----------|-------|--------------|
| 1042 | 2023-11-25 | johndoe | john@example.com | 125,99 € |
| 1041 | 2023-11-24 | alicejones | alice@example.com | 89,50 € |
| 1040 | 2023-11-23 | bobsmith | bob@example.com | 212,75 € |"

### Fonctions d'agrégation

**Vous**: "Quel est le montant moyen des commandes par catégorie?"

**IA**: "Voici le montant moyen des commandes par catégorie:

| catégorie | montant_moyen |
|----------|----------------|
| Électronique | 245,75 € |
| Vêtements | 78,30 € |
| Livres | 32,50 € |
| Maison et cuisine | 124,90 € |
| Sports et loisirs | 156,25 € |"

## Analyse de performance

### Plan d'exécution de requête

**Vous**: "Expliquez le plan d'exécution pour: SELECT * FROM orders WHERE user_id = 42"

**IA**: "Plan d'exécution pour la requête:
```
QUERY PLAN
------------------------------------------------------------
SEARCH TABLE orders USING INDEX idx_user_id (user_id=?)
```

Cette requête utilise l'index `idx_user_id` pour rechercher efficacement les commandes pour user_id 42."

### Statistiques de table

**Vous**: "Obtenez les statistiques pour la table commandes."

**IA**: "Statistiques pour la table commandes:
- Nombre de lignes: 1 245
- Taille: 2,3 Mo
- Indices: 3 (clé primaire, idx_user_id, idx_order_date)
- Longueur moyenne de ligne: 1,9 Ko"

## Travailler avec les fonctionnalités SQLite

### Utilisation de FTS (Recherche en texte intégral)

**Vous**: "Trouvez les produits contenant 'écouteurs sans fil'."

**IA**: "Voici les produits correspondant à 'écouteurs sans fil':

| product_id | nom | description | prix |
|------------|------|-------------|-------|
| 123 | Écouteurs Sans Fil Premium | Écouteurs sans fil avec réduction de bruit et 30 heures d'autonomie | 199,99 € |
| 145 | Écouteurs Sans Fil Sport | Écouteurs sans fil étanches pour le sport | 89,99 € |
| 187 | Écouteurs Sans Fil Budget | Écouteurs sans fil abordables avec une bonne qualité sonore | 49,99 € |"

### Utilisation des fonctions JSON

**Vous**: "Montrez-moi les utilisateurs avec 'premium' dans leurs préférences."

**IA**: "Voici les utilisateurs avec 'premium' dans leurs préférences:

| id | username | préférences |
|----|----------|-------------|
| 42 | johndoe | {\"abonnement\": \"premium\", \"thème\": \"sombre\"} |
| 17 | janedoe | {\"abonnement\": \"premium\", \"thème\": \"clair\"} |
| 53 | mikebrown | {\"abonnement\": \"premium\", \"thème\": \"auto\"} |"

## Dépannage

### Problèmes courants

1. **Fichier non trouvé**
   - Assurez-vous que le chemin vers votre fichier de base de données SQLite est correct
   - Vérifiez les permissions du fichier
   - Assurez-vous que le fichier existe

2. **Base de données verrouillée**
   - SQLite ne permet qu'un seul écrivain à la fois
   - Assurez-vous qu'aucun autre processus n'écrit dans la base de données
   - Envisagez d'utiliser le mode WAL pour une meilleure concurrence

3. **Problèmes de performance**
   - Ajoutez des index pour les colonnes fréquemment interrogées
   - Utilisez EXPLAIN QUERY PLAN pour identifier les requêtes lentes
   - Envisagez d'utiliser des instructions préparées pour les requêtes répétitives
