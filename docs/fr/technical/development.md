# Guide de Développement

*[English](../../en/technical/development.md) | [中文](../../zh/technical/development.md) | Français | [Español](../../es/technical/development.md) | [العربية](../../ar/technical/development.md) | [Русский](../../ru/technical/development.md)*

Ce document fournit des informations détaillées sur le processus de développement, les normes de code et les meilleures pratiques pour contribuer au projet MCP Database Utilities.

## Configuration de l'Environnement de Développement

### Prérequis

- Python 3.10 ou supérieur
- Git
- Éditeur de code ou IDE (VS Code, PyCharm, etc.)
- Docker (optionnel, pour les tests avec différentes bases de données)

### Installation pour le Développement

1. **Cloner le Dépôt**

```bash
git clone https://github.com/donghao1393/mcp-dbutils.git
cd mcp-dbutils
```

2. **Créer un Environnement Virtuel**

```bash
# Avec venv
python -m venv venv
source venv/bin/activate  # Sur Linux/macOS
# ou
.\venv\Scripts\activate  # Sur Windows

# Avec uv (recommandé)
uv venv
source .venv/bin/activate  # Sur Linux/macOS
# ou
.\.venv\Scripts\activate  # Sur Windows
```

3. **Installer les Dépendances de Développement**

```bash
# Avec pip
pip install -e ".[dev,test,docs]"

# Avec uv (recommandé)
uv pip install -e ".[dev,test,docs]"
```

4. **Configurer les Hooks de Pre-commit**

```bash
pre-commit install
```

### Bases de Données pour le Développement

Pour développer et tester localement, vous pouvez utiliser Docker pour exécuter différentes bases de données:

#### SQLite

SQLite ne nécessite pas de configuration spéciale, il suffit de créer un fichier de base de données:

```bash
# Créer une base de données SQLite de test
sqlite3 test.db < tests/fixtures/sqlite_schema.sql
```

#### PostgreSQL

```bash
# Démarrer PostgreSQL avec Docker
docker run --name postgres-dev -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -p 5432:5432 -d postgres:14

# Créer une base de données de test
docker exec -i postgres-dev psql -U postgres -c "CREATE DATABASE testdb;"
docker exec -i postgres-dev psql -U postgres -d testdb < tests/fixtures/postgres_schema.sql
```

#### MySQL

```bash
# Démarrer MySQL avec Docker
docker run --name mysql-dev -e MYSQL_ROOT_PASSWORD=mysql -e MYSQL_DATABASE=testdb -p 3306:3306 -d mysql:8

# Attendre que MySQL démarre
sleep 20

# Charger le schéma de test
docker exec -i mysql-dev mysql -uroot -pmysql testdb < tests/fixtures/mysql_schema.sql
```

## Structure du Projet

```
mcp-dbutils/
├── .github/                    # Configurations GitHub Actions
├── docs/                       # Documentation
│   ├── en/                     # Documentation en anglais
│   ├── zh/                     # Documentation en chinois
│   ├── fr/                     # Documentation en français
│   ├── es/                     # Documentation en espagnol
│   ├── ar/                     # Documentation en arabe
│   └── ru/                     # Documentation en russe
├── mcp_dbutils/                # Code source principal
│   ├── __init__.py             # Initialisation du package
│   ├── __main__.py             # Point d'entrée pour l'exécution directe
│   ├── adapters/               # Adaptateurs de base de données
│   │   ├── __init__.py
│   │   ├── base.py             # Classe de base pour les adaptateurs
│   │   ├── sqlite.py           # Adaptateur SQLite
│   │   ├── postgres.py         # Adaptateur PostgreSQL
│   │   └── mysql.py            # Adaptateur MySQL
│   ├── config/                 # Gestion de la configuration
│   │   ├── __init__.py
│   │   └── loader.py           # Chargeur de configuration
│   ├── mcp/                    # Implémentation du protocole MCP
│   │   ├── __init__.py
│   │   ├── server.py           # Serveur MCP
│   │   └── tools.py            # Outils MCP
│   ├── query/                  # Traitement des requêtes
│   │   ├── __init__.py
│   │   ├── parser.py           # Analyseur de requêtes
│   │   └── validator.py        # Validateur de requêtes
│   └── utils/                  # Utilitaires
│       ├── __init__.py
│       ├── logging.py          # Configuration de la journalisation
│       └── security.py         # Utilitaires de sécurité
├── tests/                      # Tests
│   ├── __init__.py
│   ├── conftest.py             # Configuration pytest
│   ├── fixtures/               # Fixtures pour les tests
│   ├── unit/                   # Tests unitaires
│   └── integration/            # Tests d'intégration
├── .gitignore                  # Fichiers à ignorer par Git
├── .pre-commit-config.yaml     # Configuration pre-commit
├── LICENSE                     # Licence du projet
├── pyproject.toml              # Configuration du projet Python
├── README.md                   # Documentation principale
└── README_*.md                 # Documentation dans d'autres langues
```

## Normes de Code

### Style de Code

Nous suivons [PEP 8](https://peps.python.org/pep-0008/) avec quelques modifications:

- Longueur de ligne maximale: 100 caractères
- Utilisation de guillemets doubles pour les chaînes de caractères
- Utilisation de f-strings pour le formatage de chaînes

### Formatage Automatique

Nous utilisons les outils suivants pour le formatage automatique:

- **Black**: Pour le formatage du code
- **isort**: Pour trier les imports
- **Ruff**: Pour le linting et la vérification du code

Ces outils sont configurés dans `pyproject.toml` et exécutés automatiquement via pre-commit.

### Docstrings

Nous utilisons le format Google pour les docstrings:

```python
def function_with_types_in_docstring(param1, param2):
    """Exemple de fonction avec documentation de types.

    Args:
        param1 (int): Le premier paramètre.
        param2 (str): Le second paramètre.

    Returns:
        bool: La valeur de retour. True pour succès, False sinon.

    Raises:
        ValueError: Si param1 est négatif.
        TypeError: Si param2 n'est pas une chaîne.
    """
    if param1 < 0:
        raise ValueError("param1 doit être positif.")
    if not isinstance(param2, str):
        raise TypeError("param2 doit être une chaîne.")
    return True
```

### Conventions de Nommage

- **Classes**: PascalCase (ex: `DatabaseAdapter`)
- **Fonctions et méthodes**: snake_case (ex: `connect_to_database`)
- **Variables**: snake_case (ex: `connection_pool`)
- **Constantes**: UPPER_SNAKE_CASE (ex: `MAX_CONNECTIONS`)
- **Modules**: snake_case (ex: `database_adapter.py`)
- **Packages**: snake_case (ex: `mcp_dbutils`)

### Imports

Organisez les imports dans l'ordre suivant:

1. Imports de la bibliothèque standard
2. Imports de bibliothèques tierces
3. Imports du projet

Utilisez isort pour trier automatiquement les imports.

## Processus de Développement

### Flux de Travail Git

Nous suivons un flux de travail basé sur les fonctionnalités:

1. Créez une branche à partir de `main` pour chaque fonctionnalité ou correction
2. Nommez la branche selon le format: `feature/nom-de-la-fonctionnalité` ou `fix/nom-du-correctif`
3. Faites des commits réguliers avec des messages clairs
4. Soumettez une Pull Request vers `main` lorsque la fonctionnalité est prête

### Messages de Commit

Nous suivons le format [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types courants:
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Modifications de la documentation
- `style`: Formatage, point-virgule manquant, etc. (pas de changement de code)
- `refactor`: Refactorisation du code
- `test`: Ajout ou correction de tests
- `chore`: Tâches de maintenance, mises à jour de dépendances, etc.

Exemples:
```
feat(sqlite): ajouter support pour les requêtes paramétrées
fix(postgres): corriger la gestion des timeouts de connexion
docs: mettre à jour la documentation d'installation
```

### Pull Requests

- Créez une Pull Request (PR) pour chaque fonctionnalité ou correction
- Assurez-vous que tous les tests passent
- Assurez-vous que le code est formaté correctement
- Demandez une revue de code à au moins un autre développeur
- Résolvez tous les commentaires avant de fusionner

### Revue de Code

Lors de la revue de code, vérifiez:

1. **Fonctionnalité**: Le code fait-il ce qu'il est censé faire?
2. **Qualité**: Le code est-il bien écrit, lisible et maintenable?
3. **Tests**: Y a-t-il des tests appropriés?
4. **Documentation**: La documentation est-elle à jour?
5. **Sécurité**: Y a-t-il des problèmes de sécurité potentiels?

## Tests

### Types de Tests

- **Tests Unitaires**: Testent des fonctions ou classes individuelles
- **Tests d'Intégration**: Testent l'interaction entre plusieurs composants
- **Tests de Bout en Bout**: Testent le système complet

### Exécution des Tests

```bash
# Exécuter tous les tests
pytest

# Exécuter des tests spécifiques
pytest tests/unit/
pytest tests/integration/

# Exécuter avec couverture de code
pytest --cov=mcp_dbutils

# Générer un rapport de couverture HTML
pytest --cov=mcp_dbutils --cov-report=html
```

### Écriture de Tests

Utilisez pytest pour écrire des tests:

```python
def test_connection_success():
    """Teste que la connexion à la base de données réussit avec des paramètres valides."""
    config = {
        "type": "sqlite",
        "path": ":memory:"
    }
    adapter = SQLiteAdapter(config)
    connection = adapter.connect()
    assert connection is not None
    adapter.disconnect()

def test_connection_failure():
    """Teste que la connexion échoue avec des paramètres invalides."""
    config = {
        "type": "sqlite",
        "path": "/nonexistent/path/to/db.sqlite"
    }
    adapter = SQLiteAdapter(config)
    with pytest.raises(ConnectionError):
        adapter.connect()
```

### Mocking

Utilisez `unittest.mock` ou `pytest-mock` pour les mocks:

```python
def test_query_execution(mocker):
    """Teste l'exécution de requête avec un mock de connexion."""
    # Créer un mock pour la connexion
    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    
    # Configurer le mock pour retourner des résultats spécifiques
    mock_cursor.fetchall.return_value = [("row1",), ("row2",)]
    mock_cursor.description = [("column1",)]
    
    # Injecter le mock dans l'adaptateur
    adapter = SQLiteAdapter({"type": "sqlite", "path": ":memory:"})
    adapter._connection = mock_connection
    
    # Exécuter la requête
    results = adapter.execute_query("SELECT * FROM test")
    
    # Vérifier que la requête a été exécutée correctement
    mock_cursor.execute.assert_called_once_with("SELECT * FROM test")
    assert len(results) == 2
    assert results[0][0] == "row1"
    assert results[1][0] == "row2"
```

## Documentation

### Documentation du Code

- Documentez toutes les classes, méthodes et fonctions publiques
- Utilisez le format de docstring Google
- Incluez des exemples d'utilisation lorsque c'est pertinent

### Documentation du Projet

- Maintenez à jour le README.md avec les informations essentielles
- Documentez les fonctionnalités dans le répertoire `docs/`
- Fournissez des exemples d'utilisation

### Génération de Documentation

Nous utilisons MkDocs pour générer la documentation:

```bash
# Installer MkDocs et les dépendances
pip install mkdocs mkdocs-material

# Générer la documentation
mkdocs build

# Servir la documentation localement
mkdocs serve
```

## Versionnement et Publication

### Versionnement Sémantique

Nous suivons le [Versionnement Sémantique](https://semver.org/):

- **MAJOR**: Changements incompatibles avec les versions précédentes
- **MINOR**: Ajouts de fonctionnalités rétrocompatibles
- **PATCH**: Corrections de bugs rétrocompatibles

### Processus de Publication

1. Mettez à jour la version dans `pyproject.toml`
2. Mettez à jour le CHANGELOG.md
3. Créez un tag Git avec la nouvelle version
4. Poussez le tag vers GitHub
5. GitHub Actions construira et publiera automatiquement le package sur PyPI

```bash
# Exemple de processus de publication
# 1. Mettre à jour la version dans pyproject.toml
# 2. Mettre à jour CHANGELOG.md
# 3. Commit les changements
git add pyproject.toml CHANGELOG.md
git commit -m "chore: préparer la version 1.2.3"

# 4. Créer et pousser le tag
git tag v1.2.3
git push origin main v1.2.3
```

## Intégration Continue

Nous utilisons GitHub Actions pour l'intégration continue:

- **Lint**: Vérifie le style du code
- **Test**: Exécute les tests sur différentes versions de Python et systèmes d'exploitation
- **Build**: Construit le package
- **Publish**: Publie le package sur PyPI (uniquement pour les tags)

Les workflows sont définis dans le répertoire `.github/workflows/`.

## Ressources Additionnelles

- [Documentation Python](https://docs.python.org/)
- [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Ruff Documentation](https://beta.ruff.rs/docs/)
- [pre-commit Documentation](https://pre-commit.com/)
