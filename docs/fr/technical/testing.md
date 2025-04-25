# Guide de Test

*[English](../../en/technical/testing.md) | [中文](../../zh/technical/testing.md) | Français | [Español](../../es/technical/testing.md) | [العربية](../../ar/technical/testing.md) | [Русский](../../ru/technical/testing.md)*

Ce document décrit la stratégie de test, les outils et les meilleures pratiques pour tester MCP Database Utilities.

## Philosophie de Test

Notre approche de test est basée sur les principes suivants:

1. **Tests Complets**: Couvrir tous les aspects du code, des fonctions individuelles au système complet
2. **Tests Automatisés**: Tous les tests doivent être automatisés et exécutables via CI/CD
3. **Tests Rapides**: Les tests doivent s'exécuter rapidement pour permettre un feedback rapide
4. **Tests Isolés**: Chaque test doit être indépendant et ne pas dépendre d'autres tests
5. **Tests Déterministes**: Les tests doivent produire les mêmes résultats à chaque exécution

## Types de Tests

### Tests Unitaires

Les tests unitaires vérifient le comportement des composants individuels (fonctions, classes, méthodes) en isolation.

**Caractéristiques**:
- Rapides à exécuter
- Testent une seule unité de code
- Utilisent des mocks pour isoler le code testé
- Ne dépendent pas de ressources externes (bases de données, réseau, etc.)

**Exemple**:

```python
def test_query_validator():
    """Teste que le validateur de requête identifie correctement les requêtes non autorisées."""
    validator = QueryValidator()
    
    # Requête SELECT valide
    assert validator.validate("SELECT * FROM users") is True
    
    # Requêtes non autorisées
    assert validator.validate("INSERT INTO users VALUES (1, 'test')") is False
    assert validator.validate("UPDATE users SET name = 'test' WHERE id = 1") is False
    assert validator.validate("DELETE FROM users WHERE id = 1") is False
    assert validator.validate("DROP TABLE users") is False
```

### Tests d'Intégration

Les tests d'intégration vérifient que différents composants fonctionnent correctement ensemble.

**Caractéristiques**:
- Plus lents que les tests unitaires
- Testent l'interaction entre plusieurs composants
- Peuvent utiliser des ressources externes réelles ou simulées
- Vérifient que les interfaces entre les composants fonctionnent correctement

**Exemple**:

```python
def test_sqlite_adapter_integration():
    """Teste l'intégration entre l'adaptateur SQLite et le gestionnaire de requêtes."""
    # Créer une base de données SQLite en mémoire
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # Créer une table de test
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test VALUES (1, 'test1'), (2, 'test2')")
    connection.commit()
    
    # Créer un gestionnaire de requêtes avec l'adaptateur
    query_manager = QueryManager(adapter)
    
    # Exécuter une requête via le gestionnaire
    results = query_manager.execute("SELECT * FROM test WHERE id = 1")
    
    # Vérifier les résultats
    assert len(results) == 1
    assert results[0]["id"] == 1
    assert results[0]["name"] == "test1"
```

### Tests de Bout en Bout

Les tests de bout en bout vérifient que le système complet fonctionne correctement de bout en bout.

**Caractéristiques**:
- Les plus lents à exécuter
- Testent le système complet dans un environnement proche de la production
- Utilisent des ressources externes réelles
- Vérifient les scénarios d'utilisation réels

**Exemple**:

```python
def test_mcp_server_end_to_end():
    """Teste le serveur MCP de bout en bout avec une base de données réelle."""
    # Démarrer le serveur MCP avec une configuration de test
    config_path = "tests/fixtures/test_config.yaml"
    server = MCPServer(config_path)
    server.start()
    
    try:
        # Créer un client MCP simulé
        client = MockMCPClient()
        
        # Exécuter une requête via le protocole MCP
        response = client.execute_tool("dbutils-list-tables", {"connection": "test-sqlite"})
        
        # Vérifier la réponse
        assert "tables" in response
        assert "test" in response["tables"]
        
        # Exécuter une requête SQL
        response = client.execute_tool("dbutils-run-query", {
            "connection": "test-sqlite",
            "query": "SELECT * FROM test WHERE id = 1"
        })
        
        # Vérifier les résultats
        assert len(response["results"]) == 1
        assert response["results"][0]["id"] == 1
        assert response["results"][0]["name"] == "test1"
    finally:
        # Arrêter le serveur
        server.stop()
```

### Tests de Performance

Les tests de performance vérifient que le système répond aux exigences de performance.

**Caractéristiques**:
- Mesurent le temps d'exécution, l'utilisation de mémoire, etc.
- Vérifient que le système peut gérer la charge prévue
- Identifient les goulots d'étranglement

**Exemple**:

```python
def test_query_performance():
    """Teste la performance des requêtes."""
    # Configurer l'adaptateur avec une base de données de test
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # Créer une table de test avec de nombreuses lignes
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    
    # Insérer 10000 lignes
    for i in range(10000):
        cursor.execute("INSERT INTO test VALUES (?, ?)", (i, f"test{i}"))
    connection.commit()
    
    # Mesurer le temps d'exécution d'une requête
    start_time = time.time()
    results = adapter.execute_query("SELECT * FROM test WHERE id < 1000")
    end_time = time.time()
    
    # Vérifier que la requête s'exécute en moins de 100ms
    assert end_time - start_time < 0.1
    assert len(results) == 1000
```

### Tests de Sécurité

Les tests de sécurité vérifient que le système est sécurisé contre les attaques.

**Caractéristiques**:
- Vérifient que le système résiste aux attaques connues
- Testent les mécanismes de sécurité
- Identifient les vulnérabilités potentielles

**Exemple**:

```python
def test_sql_injection_prevention():
    """Teste que le système est protégé contre les injections SQL."""
    # Configurer l'adaptateur avec une base de données de test
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # Créer une table de test
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'secret')")
    connection.commit()
    
    # Créer un gestionnaire de requêtes avec l'adaptateur
    query_manager = QueryManager(adapter)
    
    # Tenter une injection SQL
    malicious_query = "SELECT * FROM users WHERE username = 'admin' OR 1=1 --'"
    
    # Vérifier que le gestionnaire de requêtes détecte et bloque l'injection
    with pytest.raises(SecurityException):
        query_manager.execute(malicious_query)
```

## Outils de Test

### pytest

Nous utilisons [pytest](https://docs.pytest.org/) comme framework de test principal:

```bash
# Installer pytest et les plugins
pip install pytest pytest-cov pytest-mock

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

### Fixtures pytest

Les fixtures pytest permettent de configurer l'environnement de test:

```python
@pytest.fixture
def sqlite_adapter():
    """Fixture qui fournit un adaptateur SQLite configuré avec une base de données en mémoire."""
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # Créer une table de test
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test VALUES (1, 'test1'), (2, 'test2')")
    connection.commit()
    
    yield adapter
    
    # Nettoyage
    adapter.disconnect()

def test_with_fixture(sqlite_adapter):
    """Teste l'adaptateur SQLite en utilisant la fixture."""
    results = sqlite_adapter.execute_query("SELECT * FROM test WHERE id = 1")
    assert len(results) == 1
    assert results[0]["id"] == 1
    assert results[0]["name"] == "test1"
```

### Mocking

Nous utilisons `unittest.mock` ou `pytest-mock` pour les mocks:

```python
def test_with_mock(mocker):
    """Teste une fonction en utilisant des mocks."""
    # Créer un mock pour la connexion à la base de données
    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    
    # Configurer le mock pour retourner des résultats spécifiques
    mock_cursor.fetchall.return_value = [("test1",), ("test2",)]
    mock_cursor.description = [("name",)]
    
    # Remplacer la méthode de connexion par le mock
    mocker.patch("mcp_dbutils.adapters.sqlite.sqlite3.connect", return_value=mock_connection)
    
    # Créer l'adaptateur
    adapter = SQLiteAdapter({"type": "sqlite", "path": "dummy.db"})
    
    # Exécuter la requête
    results = adapter.execute_query("SELECT name FROM test")
    
    # Vérifier que la requête a été exécutée correctement
    mock_cursor.execute.assert_called_once_with("SELECT name FROM test")
    assert len(results) == 2
    assert results[0]["name"] == "test1"
    assert results[1]["name"] == "test2"
```

### Bases de Données de Test

Pour les tests d'intégration, nous utilisons des bases de données réelles:

- **SQLite**: Base de données en mémoire (`:memory:`)
- **PostgreSQL**: Instance Docker pour les tests
- **MySQL**: Instance Docker pour les tests

```python
@pytest.fixture(scope="session")
def postgres_adapter():
    """Fixture qui fournit un adaptateur PostgreSQL configuré avec une base de données de test."""
    # Démarrer PostgreSQL avec Docker
    container = start_postgres_container()
    
    # Attendre que PostgreSQL soit prêt
    wait_for_postgres(container)
    
    # Configurer l'adaptateur
    config = {
        "type": "postgres",
        "host": "localhost",
        "port": container.get_exposed_port(5432),
        "dbname": "testdb",
        "user": "postgres",
        "password": "postgres"
    }
    adapter = PostgreSQLAdapter(config)
    
    # Créer une table de test
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id SERIAL PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test (name) VALUES ('test1'), ('test2')")
    connection.commit()
    
    yield adapter
    
    # Nettoyage
    adapter.disconnect()
    container.stop()
```

## Organisation des Tests

Les tests sont organisés dans le répertoire `tests/`:

```
tests/
├── __init__.py
├── conftest.py              # Fixtures partagées
├── fixtures/                # Données de test
│   ├── sqlite_schema.sql    # Schéma SQLite pour les tests
│   ├── postgres_schema.sql  # Schéma PostgreSQL pour les tests
│   └── mysql_schema.sql     # Schéma MySQL pour les tests
├── unit/                    # Tests unitaires
│   ├── __init__.py
│   ├── test_adapters.py     # Tests des adaptateurs
│   ├── test_config.py       # Tests de la configuration
│   ├── test_mcp.py          # Tests du protocole MCP
│   └── test_query.py        # Tests du traitement des requêtes
├── integration/             # Tests d'intégration
│   ├── __init__.py
│   ├── test_sqlite.py       # Tests d'intégration SQLite
│   ├── test_postgres.py     # Tests d'intégration PostgreSQL
│   └── test_mysql.py        # Tests d'intégration MySQL
└── e2e/                     # Tests de bout en bout
    ├── __init__.py
    └── test_mcp_server.py   # Tests du serveur MCP
```

## Bonnes Pratiques

### Nommage des Tests

Suivez ces conventions de nommage:

- Les fichiers de test commencent par `test_`
- Les fonctions de test commencent par `test_`
- Les noms des tests doivent être descriptifs et indiquer ce qui est testé

```python
# Bon
def test_query_validator_rejects_insert_statements():
    ...

# Mauvais
def test_validator():
    ...
```

### Assertions

Utilisez les assertions pytest pour des messages d'erreur plus clairs:

```python
# Bon
assert result == expected, f"Expected {expected}, got {result}"

# Mauvais
if result != expected:
    raise AssertionError("Test failed")
```

### Isolation des Tests

Chaque test doit être indépendant:

- Ne pas dépendre de l'état laissé par d'autres tests
- Utiliser des fixtures pour configurer et nettoyer l'environnement
- Éviter les variables globales ou partagées

```python
# Bon
def test_independent_1(sqlite_adapter):
    sqlite_adapter.execute_query("INSERT INTO test VALUES (3, 'test3')")
    results = sqlite_adapter.execute_query("SELECT * FROM test WHERE id = 3")
    assert len(results) == 1

def test_independent_2(sqlite_adapter):
    # Ce test ne dépend pas de l'état créé par test_independent_1
    results = sqlite_adapter.execute_query("SELECT * FROM test WHERE id = 1")
    assert len(results) == 1
```

### Tests Paramétrés

Utilisez les tests paramétrés pour tester plusieurs cas:

```python
@pytest.mark.parametrize("query,is_valid", [
    ("SELECT * FROM users", True),
    ("INSERT INTO users VALUES (1, 'test')", False),
    ("UPDATE users SET name = 'test' WHERE id = 1", False),
    ("DELETE FROM users WHERE id = 1", False),
    ("DROP TABLE users", False),
])
def test_query_validator_parametrized(query, is_valid):
    """Teste que le validateur de requête identifie correctement les requêtes non autorisées."""
    validator = QueryValidator()
    assert validator.validate(query) is is_valid
```

### Tests de Régression

Créez des tests spécifiques pour les bugs corrigés:

```python
def test_regression_issue_123():
    """Teste que le bug #123 est corrigé."""
    # Le bug était: l'adaptateur SQLite ne gérait pas correctement les valeurs NULL
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # Créer une table de test
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test VALUES (1, NULL)")
    connection.commit()
    
    # Vérifier que les valeurs NULL sont correctement gérées
    results = adapter.execute_query("SELECT * FROM test WHERE id = 1")
    assert len(results) == 1
    assert results[0]["id"] == 1
    assert results[0]["name"] is None
```

## Intégration Continue

Les tests sont exécutés automatiquement via GitHub Actions:

```yaml
# .github/workflows/test.yml
name: Test

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11, 3.12]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev,test]"
    - name: Lint with ruff
      run: |
        ruff check .
    - name: Test with pytest
      run: |
        pytest --cov=mcp_dbutils --cov-report=xml
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Couverture de Code

Nous visons une couverture de code d'au moins 90%:

```bash
# Exécuter les tests avec couverture
pytest --cov=mcp_dbutils

# Générer un rapport de couverture HTML
pytest --cov=mcp_dbutils --cov-report=html
```

Le rapport de couverture est disponible dans le répertoire `htmlcov/`.

## Dépannage des Tests

### Tests Qui Échouent

Si un test échoue:

1. Lisez attentivement le message d'erreur
2. Vérifiez les assertions qui ont échoué
3. Utilisez `pytest -v` pour plus de détails
4. Utilisez `pytest --pdb` pour déboguer interactivement

### Tests Lents

Si les tests sont lents:

1. Identifiez les tests lents avec `pytest --durations=10`
2. Utilisez des mocks au lieu de ressources réelles lorsque possible
3. Optimisez les fixtures pour réduire le temps de configuration
4. Utilisez `pytest-xdist` pour exécuter les tests en parallèle

### Tests Flaky (Instables)

Si les tests sont instables (échouent de manière aléatoire):

1. Identifiez les tests instables
2. Vérifiez les dépendances externes (bases de données, réseau, etc.)
3. Assurez-vous que les tests sont isolés
4. Utilisez `pytest-rerunfailures` pour réexécuter les tests qui échouent

## Conclusion

Les tests sont essentiels pour garantir la qualité et la fiabilité de MCP Database Utilities. En suivant les bonnes pratiques et en utilisant les outils appropriés, nous pouvons maintenir une suite de tests complète et efficace qui nous donne confiance dans notre code.
