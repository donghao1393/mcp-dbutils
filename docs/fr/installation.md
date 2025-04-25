# Guide d'Installation

*[English](../en/installation.md) | [中文](../zh/installation.md) | Français | [Español](../es/installation.md) | [العربية](../ar/installation.md) | [Русский](../ru/installation.md)*

Ce document fournit des étapes simples et faciles à suivre pour installer et configurer MCP Database Utilities, permettant à votre assistant IA d'accéder et d'analyser vos bases de données en toute sécurité.

## Qu'est-ce que MCP ?

MCP (Model Context Protocol) est un protocole qui permet aux applications d'IA (comme Claude) d'utiliser des outils externes. MCP Database Utilities est l'un de ces outils qui permet à l'IA de lire le contenu de votre base de données sans modifier aucune donnée.

## Avant de Commencer

Avant de commencer l'installation, veuillez vous assurer que vous disposez de :

- Une application IA compatible avec MCP (comme Claude Desktop, Cursor, etc.)
- Au moins une base de données à laquelle vous souhaitez que l'IA accède (SQLite, MySQL ou PostgreSQL)

## Choisissez Votre Méthode d'Installation

Nous proposons quatre méthodes d'installation simples. Choisissez celle qui vous convient le mieux :

| Méthode d'Installation | Idéal Pour | Avantages |
|---------|---------|------|
| **Option A : Utilisation de uvx** | La plupart des utilisateurs | Simple et rapide, recommandé |
| **Option B : Utilisation de Docker** | Utilisateurs préférant les applications conteneurisées | Environnement isolé |
| **Option C : Utilisation de Smithery** | Utilisateurs de Claude Desktop | Installation en un clic, la plus facile |
| **Option D : Installation Hors Ligne** | Utilisateurs dans des environnements sans internet | Pas de connexion réseau nécessaire |

## Option A : Utilisation de uvx (Recommandé)

### Étape 1 : Installer l'outil uv

**Sur Mac ou Linux** :
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Sur Windows** :
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Après l'installation, vérifiez que cela fonctionne en tapant cette commande dans votre terminal :
```bash
uv --version
```
Vous devriez voir quelque chose comme `uv 0.5.5` dans la sortie.

### Étape 2 : Créer un fichier de configuration de base de données

1. Créez un fichier nommé `config.yaml` sur votre ordinateur
2. Copiez le contenu suivant dans le fichier (choisissez celui qui correspond à votre type de base de données) :

**Exemple de Base de Données SQLite** :
```yaml
connections:
  my_sqlite:
    type: sqlite
    path: C:/path/to/your/database.db
```

**Exemple de Base de Données PostgreSQL** :
```yaml
connections:
  my_postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: my_database
    user: postgres_user
    password: postgres_password
```

**Exemple de Base de Données MySQL** :
```yaml
connections:
  my_mysql:
    type: mysql
    host: localhost
    port: 3306
    database: my_database
    user: mysql_user
    password: mysql_password
```

> Veuillez remplacer les informations d'exemple par les détails réels de votre base de données. Pour plus d'options de configuration, consultez le [Guide de Configuration](configuration.md).

### Étape 3 : Configurer votre application IA

#### Configuration de Claude Desktop

1. Ouvrez l'application Claude Desktop
2. Cliquez sur l'icône des paramètres en bas à gauche
3. Sélectionnez "MCP Servers"
4. Cliquez sur "Add Server"
5. Ajoutez la configuration suivante :

```json
"dbutils": {
  "command": "uvx",
  "args": [
    "mcp-dbutils",
    "--config",
    "C:/Users/VotreNomUtilisateur/config.yaml"
  ]
}
```

> Important : Remplacez `C:/Users/VotreNomUtilisateur/config.yaml` par le chemin réel vers le fichier de configuration que vous avez créé à l'Étape 2.

#### Configuration de Cursor

1. Ouvrez l'application Cursor
2. Allez dans "Settings" → "MCP"
3. Cliquez sur "Add MCP Server"
4. Remplissez les informations suivantes :
   - Name: `Database Utility MCP`
   - Type: `Command` (par défaut)
   - Command: `uvx mcp-dbutils --config C:/Users/VotreNomUtilisateur/config.yaml`

> Important : Remplacez `C:/Users/VotreNomUtilisateur/config.yaml` par le chemin réel vers le fichier de configuration que vous avez créé à l'Étape 2.

## Option B : Utilisation de Docker

### Étape 1 : Installer Docker

Si vous n'avez pas Docker installé, téléchargez et installez-le depuis [docker.com](https://www.docker.com/products/docker-desktop/).

### Étape 2 : Créer un fichier de configuration de base de données

Identique à l'Étape 2 de l'Option A, créez un fichier `config.yaml`.

### Étape 3 : Configurer votre application IA

#### Configuration de Claude Desktop

1. Ouvrez l'application Claude Desktop
2. Cliquez sur l'icône des paramètres en bas à gauche
3. Sélectionnez "MCP Servers"
4. Cliquez sur "Add Server"
5. Ajoutez la configuration suivante :

```json
"dbutils": {
  "command": "docker",
  "args": [
    "run",
    "-i",
    "--rm",
    "-v",
    "C:/Users/VotreNomUtilisateur/config.yaml:/app/config.yaml",
    "mcp/dbutils",
    "--config",
    "/app/config.yaml"
  ]
}
```

> Important : Remplacez `C:/Users/VotreNomUtilisateur/config.yaml` par le chemin réel vers le fichier de configuration que vous avez créé à l'Étape 2.

#### Configuration de Cursor

1. Ouvrez l'application Cursor
2. Allez dans "Settings" → "MCP"
3. Cliquez sur "Add MCP Server"
4. Remplissez les informations suivantes :
   - Name: `Database Utility MCP`
   - Type: `Command` (par défaut)
   - Command: `docker run -i --rm -v C:/Users/VotreNomUtilisateur/config.yaml:/app/config.yaml mcp/dbutils --config /app/config.yaml`

> Important : Remplacez `C:/Users/VotreNomUtilisateur/config.yaml` par le chemin réel vers le fichier de configuration que vous avez créé à l'Étape 2.

## Option C : Utilisation de Smithery (Un Clic pour Claude)

Si vous utilisez Claude Desktop, c'est la méthode d'installation la plus simple :

1. Assurez-vous d'avoir Node.js installé
2. Ouvrez un terminal ou une invite de commande
3. Exécutez la commande suivante :

```bash
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

4. Suivez les instructions à l'écran pour terminer l'installation

Cette méthode gère automatiquement toute la configuration, vous n'avez donc pas besoin de modifier manuellement des fichiers.

## Option D : Installation Hors Ligne

Si vous devez utiliser l'outil dans un environnement sans accès à Internet, ou si vous souhaitez utiliser une version spécifique :

### Étape 1 : Obtenir le code source

Dans un environnement avec accès à Internet :
1. Téléchargez le code source depuis GitHub : `git clone https://github.com/donghao1393/mcp-dbutils.git`
2. Ou téléchargez un fichier zip depuis la [page des Releases](https://github.com/donghao1393/mcp-dbutils/releases)
3. Copiez les fichiers téléchargés dans votre environnement hors ligne

### Étape 2 : Créer un fichier de configuration de base de données

Identique à l'Étape 2 de l'Option A, créez un fichier `config.yaml`.

### Étape 3 : Configurer votre application IA

#### Configuration de Claude Desktop

1. Ouvrez l'application Claude Desktop
2. Cliquez sur l'icône des paramètres en bas à gauche
3. Sélectionnez "MCP Servers"
4. Cliquez sur "Add Server"
5. Ajoutez la configuration suivante :

```json
"dbutils": {
  "command": "uv",
  "args": [
    "--directory",
    "C:/Users/VotreNomUtilisateur/mcp-dbutils",
    "run",
    "mcp-dbutils",
    "--config",
    "C:/Users/VotreNomUtilisateur/config.yaml"
  ]
}
```

> Important : Remplacez les chemins par les chemins réels vers votre répertoire de code source et votre fichier de configuration.

## Vérification de Votre Installation

Après avoir terminé l'installation, vérifions que tout fonctionne correctement :

### Test de la Connexion

1. Ouvrez votre application IA (Claude Desktop ou Cursor)
2. Demandez à votre IA : **"Pouvez-vous vérifier si vous êtes capable de vous connecter à ma base de données ?"**
3. Si configuré correctement, l'IA répondra qu'elle s'est connectée avec succès à votre base de données

### Essayez des Commandes Simples

Une fois connecté, vous pouvez essayer ces commandes simples :

- **"Listez toutes les tables de ma base de données"**
- **"Décrivez la structure de la table clients"**
- **"Interrogez les 5 produits les plus chers dans la table produits"**

## Résolution des Problèmes Courants

### Problème 1 : L'IA ne Trouve pas la Commande uvx

**Symptôme** : L'IA répond avec "commande uvx introuvable" ou une erreur similaire

**Solution** :
1. Confirmez que uv est correctement installé : Exécutez `uv --version` dans votre terminal
2. Si installé mais que vous obtenez toujours des erreurs, il pourrait s'agir d'un problème de variable d'environnement :
   - Sur Windows, vérifiez si la variable d'environnement PATH inclut le répertoire d'installation de uv
   - Sur Mac/Linux, vous devrez peut-être redémarrer votre terminal ou exécuter `source ~/.bashrc` ou `source ~/.zshrc`

### Problème 2 : Impossible de se Connecter à la Base de Données

**Symptôme** : L'IA signale qu'elle ne peut pas se connecter à votre base de données

**Solution** :
1. **Vérifiez si votre base de données est en cours d'exécution** : Assurez-vous que votre serveur de base de données est démarré
2. **Vérifiez les informations de connexion** : Vérifiez soigneusement l'hôte, le port, le nom d'utilisateur et le mot de passe dans votre config.yaml
3. **Vérifiez les paramètres réseau** :
   - Si vous utilisez Docker, pour les bases de données locales, utilisez `host.docker.internal` comme nom d'hôte
   - Confirmez que les pare-feu ne bloquent pas la connexion

### Problème 3 : Erreur de Chemin du Fichier de Configuration

**Symptôme** : L'IA signale qu'elle ne peut pas trouver le fichier de configuration

**Solution** :
1. **Utilisez des chemins absolus** : Assurez-vous d'utiliser des chemins absolus complets dans la configuration de votre application IA
2. **Vérifiez les permissions de fichier** : Assurez-vous que le fichier de configuration est lisible par l'utilisateur actuel
3. **Évitez les caractères spéciaux** : N'utilisez pas de caractères spéciaux ou d'espaces dans le chemin, ou utilisez des guillemets si nécessaire

### Problème 4 : Problèmes de Chemin de Base de Données SQLite

**Symptôme** : La connexion échoue lors de l'utilisation de SQLite

**Solution** :
1. **Vérifiez le chemin du fichier** : Assurez-vous que le fichier de base de données SQLite existe et que le chemin est correct
2. **Vérifiez les permissions** : Assurez-vous que le fichier de base de données a des permissions de lecture
3. **Lors de l'utilisation de Docker** : Assurez-vous d'avoir correctement mappé le chemin du fichier SQLite

## Mise à Jour vers la Dernière Version

Des mises à jour régulières fournissent de nouvelles fonctionnalités et des correctifs de sécurité. Choisissez la méthode de mise à jour qui correspond à votre méthode d'installation :

### Option A (uvx) Mise à Jour

Lorsque vous exécutez MCP Database Utilities en utilisant la commande `uvx` (par exemple, `uvx mcp-dbutils`), elle utilise automatiquement la dernière version sans nécessiter de mises à jour manuelles.

Si vous utilisez la méthode d'installation traditionnelle (pas la commande `uvx`), vous pouvez mettre à jour manuellement avec :

```bash
uv pip install -U mcp-dbutils
```

### Option B (Docker) Mise à Jour

```bash
docker pull mcp/dbutils:latest
```

### Option C (Smithery) Mise à Jour

```bash
npx -y @smithery/cli update @donghao1393/mcp-dbutils
```

### Option D (Hors Ligne) Mise à Jour

1. Téléchargez la dernière version du code source dans un environnement avec accès à Internet
2. Remplacez les fichiers de code source dans votre environnement hors ligne

## Exemples d'Interactions

Après une installation réussie, vous pouvez essayer ces conversations d'exemple :

**Vous** : Pouvez-vous lister toutes les tables de ma base de données ?

**IA** : Laissez-moi vérifier votre base de données. Voici les tables dans votre base de données :
- clients
- produits
- commandes
- inventaire

**Vous** : À quoi ressemble la table clients ?

**IA** : La table clients a la structure suivante :
- id (entier, clé primaire)
- nom (texte)
- email (texte)
- date_inscription (date)
- dernier_achat (date)

**Vous** : Combien de clients ont effectué des achats le mois dernier ?

**IA** : Laissez-moi exécuter une requête pour le savoir... Selon les données, 28 clients ont effectué des achats le mois dernier. La valeur totale de ces achats était de 15 742,50 €.
