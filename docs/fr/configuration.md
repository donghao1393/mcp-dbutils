# Guide de Configuration

*[English](../en/configuration.md) | [中文](../zh/configuration.md) | Français | [Español](../es/configuration.md) | [العربية](../ar/configuration.md) | [Русский](../ru/configuration.md)*

Ce document fournit divers exemples de configuration pour MCP Database Utilities, des configurations de base aux scénarios avancés, vous aidant à configurer et optimiser correctement vos connexions de base de données.

## Configuration de Base

### Configuration de Base SQLite

SQLite est une base de données légère basée sur des fichiers avec une configuration très simple :

```yaml
connections:
  my-sqlite:
    type: sqlite
    path: /path/to/database.db
    # Optionnel : mot de passe de chiffrement de la base de données
    password: optional_encryption_password
```

### Configuration de Base PostgreSQL

Configuration de connexion PostgreSQL standard :

```yaml
connections:
  my-postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: my_database
    user: postgres_user
    password: postgres_password
```

### Configuration de Base MySQL

Configuration de connexion MySQL standard :

```yaml
connections:
  my-mysql:
    type: mysql
    host: localhost
    port: 3306
    database: my_database
    user: mysql_user
    password: mysql_password
    charset: utf8mb4  # Recommandé pour la prise en charge complète d'Unicode
```

## Configuration de Plusieurs Bases de Données

Vous pouvez définir plusieurs connexions de base de données dans le même fichier de configuration :

```yaml
connections:
  # Base de données SQLite de développement
  dev-db:
    type: sqlite
    path: /path/to/dev.db

  # Base de données PostgreSQL de test
  test-db:
    type: postgres
    host: test-postgres.example.com
    port: 5432
    dbname: test_db
    user: test_user
    password: test_pass

  # Base de données MySQL de production
  prod-db:
    type: mysql
    host: prod-mysql.example.com
    port: 3306
    database: prod_db
    user: prod_user
    password: prod_pass
    charset: utf8mb4
```

## Configuration Avancée

### Configuration de Style URL

En plus d'utiliser des propriétés de configuration standard, vous pouvez également utiliser des URL de base de données pour une configuration partielle. La meilleure pratique consiste à mettre la structure de connexion à la base de données dans l'URL, mais à garder les informations sensibles et les paramètres spécifiques séparés :

**Configuration URL PostgreSQL (Approche Recommandée)** :

```yaml
connections:
  # Utilisation d'URL pour PostgreSQL (meilleure pratique)
  postgres-url:
    type: postgres
    url: postgresql://host:5432/dbname
    user: postgres_user
    password: postgres_password
    # Autres paramètres configurés ici
```

**Configuration URL MySQL (Approche Recommandée)** :

```yaml
connections:
  # Utilisation d'URL pour MySQL (meilleure pratique)
  mysql-url:
    type: mysql
    url: mysql://host:3306/dbname
    user: mysql_user
    password: mysql_password
    charset: utf8mb4
```

**Style de Configuration URL Hérité** (non recommandé pour la production) :

Bien que l'approche suivante fonctionne, elle n'est pas recommandée pour les environnements de production en raison du risque d'erreurs d'analyse des caractères spéciaux :

```yaml
connections:
  legacy-url:
    type: postgres
    url: postgresql://user:password@host:5432/dbname?param1=value1
    # Remarque : Il n'est pas recommandé d'inclure les identifiants dans l'URL
```

**Quand Utiliser URL vs Configuration Standard** :
- La configuration URL convient pour :
  - Lorsque vous avez déjà une chaîne de connexion à la base de données
  - Besoin d'inclure des paramètres de connexion spécifiques dans l'URL
  - Migration depuis d'autres systèmes avec des chaînes de connexion
- La configuration standard convient pour :
  - Structure de configuration plus claire
  - Besoin de gérer chaque propriété de configuration séparément
  - Plus facile de modifier des paramètres individuels sans affecter la connexion globale
  - Meilleure sécurité et maintenabilité

Dans tous les cas, vous devriez éviter d'inclure des informations sensibles (comme les noms d'utilisateur, les mots de passe) dans l'URL et les fournir séparément dans les paramètres de configuration.

### Connexions Sécurisées SSL/TLS

#### Configuration SSL PostgreSQL

**Utilisation des Paramètres URL pour SSL** :

```yaml
connections:
  pg-ssl-url:
    type: postgres
    url: postgresql://postgres.example.com:5432/secure_db?sslmode=verify-full&sslcert=/path/to/cert.pem&sslkey=/path/to/key.pem&sslrootcert=/path/to/root.crt
    user: secure_user
    password: secure_pass
```

**Utilisation d'une Section de Configuration SSL Dédiée** :

```yaml
connections:
  pg-ssl-full:
    type: postgres
    host: secure-postgres.example.com
    port: 5432
    dbname: secure_db
    user: secure_user
    password: secure_pass
    ssl:
      mode: verify-full  # Mode de vérification le plus sécurisé
      cert: /path/to/client-cert.pem  # Certificat client
      key: /path/to/client-key.pem    # Clé privée client
      root: /path/to/root.crt         # Certificat CA
```

**Explication du Mode SSL PostgreSQL** :
- `disable` : Pas de SSL utilisé du tout (non recommandé pour la production)
- `require` : Utiliser SSL mais ne pas vérifier le certificat (chiffrement uniquement, pas d'authentification)
- `verify-ca` : Vérifier que le certificat du serveur est signé par une CA de confiance
- `verify-full` : Vérifier le certificat du serveur et que le nom d'hôte correspond (option la plus sécurisée)

#### Configuration SSL MySQL

**Utilisation des Paramètres URL pour SSL** :

```yaml
connections:
  mysql-ssl-url:
    type: mysql
    url: mysql://mysql.example.com:3306/secure_db?ssl-mode=verify_identity&ssl-ca=/path/to/ca.pem&ssl-cert=/path/to/client-cert.pem&ssl-key=/path/to/client-key.pem
    user: secure_user
    password: secure_pass
```

**Utilisation d'une Section de Configuration SSL Dédiée** :

```yaml
connections:
  mysql-ssl-full:
    type: mysql
    host: secure-mysql.example.com
    port: 3306
    database: secure_db
    user: secure_user
    password: secure_pass
    charset: utf8mb4
    ssl:
      mode: verify_identity  # Mode de vérification le plus sécurisé
      ca: /path/to/ca.pem         # Certificat CA
      cert: /path/to/client-cert.pem  # Certificat client
      key: /path/to/client-key.pem    # Clé privée client
```

**Explication du Mode SSL MySQL** :
- `disabled` : Pas de SSL utilisé (non recommandé pour la production)
- `preferred` : Utiliser SSL si disponible, sinon utiliser une connexion non chiffrée
- `required` : SSL doit être utilisé, mais ne pas vérifier le certificat du serveur
- `verify_ca` : Vérifier que le certificat du serveur est signé par une CA de confiance
- `verify_identity` : Vérifier le certificat du serveur et que le nom d'hôte correspond (option la plus sécurisée)

### Configuration Avancée SQLite

**Utilisation des Paramètres URI** :

```yaml
connections:
  sqlite-advanced:
    type: sqlite
    path: /path/to/db.sqlite?mode=ro&cache=shared&immutable=1
```

**Paramètres URI SQLite Courants** :
- `mode=ro` : Mode lecture seule (option sûre)
- `cache=shared` : Mode de cache partagé, améliore les performances multi-threads
- `immutable=1` : Marquer la base de données comme immuable, améliore les performances
- `nolock=1` : Désactiver le verrouillage de fichier (à utiliser uniquement lorsqu'on est certain qu'aucune autre connexion n'existe)

## Configuration Spéciale pour l'Environnement Docker

Lors de l'exécution dans un conteneur Docker, la connexion aux bases de données sur l'hôte nécessite une configuration spéciale :

### Connexion à PostgreSQL/MySQL sur l'Hôte

**Sur macOS/Windows** :
Utilisez le nom d'hôte spécial `host.docker.internal` pour accéder à l'hôte Docker :

```yaml
connections:
  docker-postgres:
    type: postgres
    host: host.docker.internal  # Nom DNS spécial pointant vers l'hôte Docker
    port: 5432
    dbname: my_database
    user: postgres_user
    password: postgres_password
```

**Sur Linux** :
Utilisez l'IP du pont Docker ou utilisez le mode réseau hôte :

```yaml
connections:
  docker-mysql:
    type: mysql
    host: 172.17.0.1  # IP du pont Docker par défaut, pointe vers l'hôte
    port: 3306
    database: my_database
    user: mysql_user
    password: mysql_password
```

Ou utilisez `--network="host"` lors du démarrage du conteneur Docker, puis utilisez `localhost` comme nom d'hôte.

### Mappage SQLite

Pour SQLite, vous devez mapper le fichier de base de données dans le conteneur :

```bash
docker run -i --rm \
  -v /path/to/config.yaml:/app/config.yaml \
  -v /path/to/database.db:/app/database.db \
  mcp/dbutils --config /app/config.yaml
```

Puis pointez vers le chemin mappé dans votre configuration :

```yaml
connections:
  docker-sqlite:
    type: sqlite
    path: /app/database.db  # Chemin à l'intérieur du conteneur, pas le chemin de l'hôte
```

## Scénarios de Configuration Courants

### Gestion Multi-Environnements

Une bonne pratique consiste à utiliser des conventions de nommage claires pour différents environnements :

```yaml
connections:
  # Environnement de développement
  dev-postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: dev_db
    user: dev_user
    password: dev_pass

  # Environnement de test
  test-postgres:
    type: postgres
    host: test-server.example.com
    port: 5432
    dbname: test_db
    user: test_user
    password: test_pass

  # Environnement de production
  prod-postgres:
    type: postgres
    host: prod-db.example.com
    port: 5432
    dbname: prod_db
    user: prod_user
    password: prod_pass
    ssl:
      mode: verify-full
      cert: /path/to/cert.pem
      key: /path/to/key.pem
      root: /path/to/root.crt
```

### Configuration Spécifique pour Lecture Seule et Analytique

Pour les scénarios d'analyse de données, il est recommandé d'utiliser des comptes en lecture seule et une configuration optimisée :

```yaml
connections:
  analytics-mysql:
    type: mysql
    host: analytics-db.example.com
    port: 3306
    database: analytics
    user: analytics_readonly  # Utiliser un compte avec des permissions en lecture seule
    password: readonly_pass
    charset: utf8mb4
    # Définir un délai d'attente plus long adapté à l'analyse de données
```

## Conseils de Dépannage

Si votre configuration de connexion ne fonctionne pas, essayez :

1. **Vérifier la Connexion de Base** : Utilisez le client natif de la base de données pour vérifier que la connexion fonctionne
2. **Vérifier la Connectivité Réseau** : Assurez-vous que les ports réseau sont ouverts, que les pare-feu autorisent l'accès
3. **Vérifier les Identifiants** : Confirmez que le nom d'utilisateur et le mot de passe sont corrects
4. **Problèmes de Chemin** : Pour SQLite, assurez-vous que le chemin existe et a des permissions de lecture
5. **Erreurs SSL** : Vérifiez les chemins et les permissions des certificats, vérifiez que les certificats ne sont pas expirés
