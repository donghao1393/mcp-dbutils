# Guide d'Installation Spécifique à la Plateforme

*[English](../en/installation-platform-specific.md) | [中文](../zh/installation-platform-specific.md) | Français | [Español](../es/installation-platform-specific.md) | [العربية](../ar/installation-platform-specific.md) | [Русский](../ru/installation-platform-specific.md)*

Ce document fournit des instructions d'installation détaillées pour MCP Database Utilities sur différents systèmes d'exploitation et environnements.

## Installation sur Windows

### Prérequis

- Python 3.10 ou supérieur
- Accès administrateur (pour certaines étapes)
- Connexion Internet (pour le téléchargement des packages)

### Installation de Python

1. Téléchargez Python depuis [python.org](https://www.python.org/downloads/windows/)
2. Exécutez l'installateur et assurez-vous de cocher l'option "Add Python to PATH"
3. Vérifiez l'installation en ouvrant une invite de commande et en tapant :
   ```
   python --version
   ```

### Installation de uv

1. Ouvrez PowerShell en tant qu'administrateur
2. Exécutez la commande suivante :
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
3. Vérifiez l'installation :
   ```
   uv --version
   ```

### Installation de MCP Database Utilities

#### Option 1 : Installation avec uvx (Recommandée)

```powershell
# Aucune installation préalable nécessaire
# uvx gère tout automatiquement
```

Configurez votre client IA pour utiliser :
```
uvx mcp-dbutils --config C:\path\to\config.yaml
```

#### Option 2 : Installation traditionnelle

```powershell
# Créez un environnement virtuel (optionnel mais recommandé)
python -m venv venv
.\venv\Scripts\activate

# Installez avec uv
uv pip install mcp-dbutils
```

#### Option 3 : Installation avec Smithery

```powershell
# Assurez-vous que Node.js est installé
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

## Installation sur macOS

### Prérequis

- Python 3.10 ou supérieur
- Homebrew (recommandé)
- Connexion Internet (pour le téléchargement des packages)

### Installation de Python

1. Installez Homebrew si ce n'est pas déjà fait :
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Installez Python :
   ```bash
   brew install python@3.10
   ```

3. Vérifiez l'installation :
   ```bash
   python3 --version
   ```

### Installation de uv

1. Ouvrez le Terminal
2. Exécutez la commande suivante :
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Vérifiez l'installation :
   ```bash
   uv --version
   ```

### Installation de MCP Database Utilities

#### Option 1 : Installation avec uvx (Recommandée)

```bash
# Aucune installation préalable nécessaire
# uvx gère tout automatiquement
```

Configurez votre client IA pour utiliser :
```
uvx mcp-dbutils --config /path/to/config.yaml
```

#### Option 2 : Installation traditionnelle

```bash
# Créez un environnement virtuel (optionnel mais recommandé)
python3 -m venv venv
source venv/bin/activate

# Installez avec uv
uv pip install mcp-dbutils
```

#### Option 3 : Installation avec Smithery

```bash
# Assurez-vous que Node.js est installé
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

## Installation sur Linux

### Prérequis

- Python 3.10 ou supérieur
- Privilèges sudo (pour certaines étapes)
- Connexion Internet (pour le téléchargement des packages)

### Installation de Python

#### Sur Ubuntu/Debian :

```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev
```

#### Sur Fedora :

```bash
sudo dnf install python3.10 python3.10-devel
```

#### Sur Arch Linux :

```bash
sudo pacman -S python
```

### Installation de uv

1. Ouvrez le Terminal
2. Exécutez la commande suivante :
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Vérifiez l'installation :
   ```bash
   uv --version
   ```

### Installation de MCP Database Utilities

#### Option 1 : Installation avec uvx (Recommandée)

```bash
# Aucune installation préalable nécessaire
# uvx gère tout automatiquement
```

Configurez votre client IA pour utiliser :
```
uvx mcp-dbutils --config /path/to/config.yaml
```

#### Option 2 : Installation traditionnelle

```bash
# Créez un environnement virtuel (optionnel mais recommandé)
python3 -m venv venv
source venv/bin/activate

# Installez avec uv
uv pip install mcp-dbutils
```

#### Option 3 : Installation avec Smithery

```bash
# Assurez-vous que Node.js est installé
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

## Installation dans un Conteneur Docker

### Prérequis

- Docker installé et fonctionnel
- Connexion Internet (pour télécharger l'image Docker)

### Utilisation de l'Image Docker Officielle

1. Tirez l'image Docker :
   ```bash
   docker pull mcp/dbutils
   ```

2. Exécutez le conteneur avec votre fichier de configuration :
   ```bash
   docker run -i --rm -v /path/to/config.yaml:/app/config.yaml mcp/dbutils --config /app/config.yaml
   ```

### Création d'une Image Docker Personnalisée

Si vous avez besoin de personnaliser l'image Docker, vous pouvez créer votre propre Dockerfile :

```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir mcp-dbutils

ENTRYPOINT ["mcp-dbutils"]
CMD ["--help"]
```

Construisez et exécutez votre image personnalisée :

```bash
docker build -t custom-mcp-dbutils .
docker run -i --rm -v /path/to/config.yaml:/app/config.yaml custom-mcp-dbutils --config /app/config.yaml
```

## Installation Hors Ligne

Pour les environnements sans accès Internet, vous pouvez préparer une installation hors ligne :

### Étape 1 : Téléchargement des Packages (sur une machine avec Internet)

```bash
# Créez un répertoire pour les packages
mkdir mcp-dbutils-offline
cd mcp-dbutils-offline

# Téléchargez les packages avec leurs dépendances
uv pip download mcp-dbutils -d ./packages
```

### Étape 2 : Transfert vers la Machine Hors Ligne

Transférez le répertoire `mcp-dbutils-offline` vers la machine hors ligne à l'aide d'une clé USB ou d'un autre moyen.

### Étape 3 : Installation sur la Machine Hors Ligne

```bash
# Créez un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur Linux/macOS
# ou
.\venv\Scripts\activate  # Sur Windows

# Installez depuis les packages téléchargés
uv pip install --no-index --find-links=./packages mcp-dbutils
```

## Dépannage

### Problème : "Command not found" après l'installation

**Solution** :
- Assurez-vous que le répertoire d'installation est dans votre PATH
- Sur Windows, essayez de redémarrer l'invite de commande ou PowerShell
- Sur Linux/macOS, exécutez `source ~/.bashrc` ou `source ~/.zshrc`

### Problème : Erreurs de Dépendances

**Solution** :
- Assurez-vous d'avoir Python 3.10 ou supérieur
- Essayez d'installer avec `--verbose` pour voir les erreurs détaillées :
  ```
  uv pip install --verbose mcp-dbutils
  ```

### Problème : Erreurs de Permission

**Solution** :
- Sur Windows, exécutez PowerShell en tant qu'administrateur
- Sur Linux/macOS, utilisez `sudo` si nécessaire ou installez dans un environnement virtuel

### Problème : Erreurs avec Docker

**Solution** :
- Vérifiez que Docker est en cours d'exécution : `docker info`
- Assurez-vous que les chemins de montage sont corrects et accessibles
- Sur Linux, vous pourriez avoir besoin d'ajouter votre utilisateur au groupe docker :
  ```
  sudo usermod -aG docker $USER
  ```
  (Déconnectez-vous et reconnectez-vous pour que les changements prennent effet)

## Ressources Supplémentaires

- [Documentation Python](https://docs.python.org/)
- [Documentation Docker](https://docs.docker.com/)
- [Documentation uv](https://github.com/astral-sh/uv)
- [Documentation Smithery](https://smithery.ai/docs)
