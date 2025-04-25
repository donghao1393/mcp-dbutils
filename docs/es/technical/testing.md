# Guía de Pruebas

*[English](../../en/technical/testing.md) | [中文](../../zh/technical/testing.md) | [Français](../../fr/technical/testing.md) | Español | [العربية](../../ar/technical/testing.md) | [Русский](../../ru/technical/testing.md)*

Este documento describe la estrategia de pruebas, herramientas y mejores prácticas para probar MCP Database Utilities.

## Filosofía de Pruebas

Nuestro enfoque de pruebas se basa en los siguientes principios:

1. **Pruebas Completas**: Cubrir todos los aspectos del código, desde funciones individuales hasta el sistema completo
2. **Pruebas Automatizadas**: Todas las pruebas deben ser automatizadas y ejecutables a través de CI/CD
3. **Pruebas Rápidas**: Las pruebas deben ejecutarse rápidamente para permitir retroalimentación rápida
4. **Pruebas Aisladas**: Cada prueba debe ser independiente y no depender de otras pruebas
5. **Pruebas Deterministas**: Las pruebas deben producir los mismos resultados en cada ejecución

## Tipos de Pruebas

### Pruebas Unitarias

Las pruebas unitarias verifican el comportamiento de componentes individuales (funciones, clases, métodos) en aislamiento.

**Características**:
- Rápidas de ejecutar
- Prueban una sola unidad de código
- Utilizan mocks para aislar el código probado
- No dependen de recursos externos (bases de datos, red, etc.)

**Ejemplo**:

```python
def test_query_validator():
    """Prueba que el validador de consulta identifica correctamente las consultas no autorizadas."""
    validator = QueryValidator()
    
    # Consulta SELECT válida
    assert validator.validate("SELECT * FROM users") is True
    
    # Consultas no autorizadas
    assert validator.validate("INSERT INTO users VALUES (1, 'test')") is False
    assert validator.validate("UPDATE users SET name = 'test' WHERE id = 1") is False
    assert validator.validate("DELETE FROM users WHERE id = 1") is False
    assert validator.validate("DROP TABLE users") is False
```

### Pruebas de Integración

Las pruebas de integración verifican que diferentes componentes funcionan correctamente juntos.

**Características**:
- Más lentas que las pruebas unitarias
- Prueban la interacción entre varios componentes
- Pueden utilizar recursos externos reales o simulados
- Verifican que las interfaces entre los componentes funcionan correctamente

**Ejemplo**:

```python
def test_sqlite_adapter_integration():
    """Prueba la integración entre el adaptador SQLite y el gestor de consultas."""
    # Crear una base de datos SQLite en memoria
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # Crear una tabla de prueba
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test VALUES (1, 'test1'), (2, 'test2')")
    connection.commit()
    
    # Crear un gestor de consultas con el adaptador
    query_manager = QueryManager(adapter)
    
    # Ejecutar una consulta a través del gestor
    results = query_manager.execute("SELECT * FROM test WHERE id = 1")
    
    # Verificar los resultados
    assert len(results) == 1
    assert results[0]["id"] == 1
    assert results[0]["name"] == "test1"
```

### Pruebas de Extremo a Extremo

Las pruebas de extremo a extremo verifican que el sistema completo funciona correctamente de principio a fin.

**Características**:
- Las más lentas de ejecutar
- Prueban el sistema completo en un entorno cercano a producción
- Utilizan recursos externos reales
- Verifican escenarios de uso reales

**Ejemplo**:

```python
def test_mcp_server_end_to_end():
    """Prueba el servidor MCP de extremo a extremo con una base de datos real."""
    # Iniciar el servidor MCP con una configuración de prueba
    config_path = "tests/fixtures/test_config.yaml"
    server = MCPServer(config_path)
    server.start()
    
    try:
        # Crear un cliente MCP simulado
        client = MockMCPClient()
        
        # Ejecutar una consulta a través del protocolo MCP
        response = client.execute_tool("dbutils-list-tables", {"connection": "test-sqlite"})
        
        # Verificar la respuesta
        assert "tables" in response
        assert "test" in response["tables"]
        
        # Ejecutar una consulta SQL
        response = client.execute_tool("dbutils-run-query", {
            "connection": "test-sqlite",
            "query": "SELECT * FROM test WHERE id = 1"
        })
        
        # Verificar los resultados
        assert len(response["results"]) == 1
        assert response["results"][0]["id"] == 1
        assert response["results"][0]["name"] == "test1"
    finally:
        # Detener el servidor
        server.stop()
```

### Pruebas de Rendimiento

Las pruebas de rendimiento verifican que el sistema cumple con los requisitos de rendimiento.

**Características**:
- Miden el tiempo de ejecución, uso de memoria, etc.
- Verifican que el sistema puede manejar la carga prevista
- Identifican cuellos de botella

**Ejemplo**:

```python
def test_query_performance():
    """Prueba el rendimiento de las consultas."""
    # Configurar el adaptador con una base de datos de prueba
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # Crear una tabla de prueba con muchas filas
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    
    # Insertar 10000 filas
    for i in range(10000):
        cursor.execute("INSERT INTO test VALUES (?, ?)", (i, f"test{i}"))
    connection.commit()
    
    # Medir el tiempo de ejecución de una consulta
    start_time = time.time()
    results = adapter.execute_query("SELECT * FROM test WHERE id < 1000")
    end_time = time.time()
    
    # Verificar que la consulta se ejecuta en menos de 100ms
    assert end_time - start_time < 0.1
    assert len(results) == 1000
```

### Pruebas de Seguridad

Las pruebas de seguridad verifican que el sistema es seguro contra ataques.

**Características**:
- Verifican que el sistema resiste a ataques conocidos
- Prueban los mecanismos de seguridad
- Identifican vulnerabilidades potenciales

**Ejemplo**:

```python
def test_sql_injection_prevention():
    """Prueba que el sistema está protegido contra inyecciones SQL."""
    # Configurar el adaptador con una base de datos de prueba
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # Crear una tabla de prueba
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'secret')")
    connection.commit()
    
    # Crear un gestor de consultas con el adaptador
    query_manager = QueryManager(adapter)
    
    # Intentar una inyección SQL
    malicious_query = "SELECT * FROM users WHERE username = 'admin' OR 1=1 --'"
    
    # Verificar que el gestor de consultas detecta y bloquea la inyección
    with pytest.raises(SecurityException):
        query_manager.execute(malicious_query)
```

## Herramientas de Prueba

### pytest

Utilizamos [pytest](https://docs.pytest.org/) como framework principal de pruebas:

```bash
# Instalar pytest y plugins
pip install pytest pytest-cov pytest-mock

# Ejecutar todas las pruebas
pytest

# Ejecutar pruebas específicas
pytest tests/unit/
pytest tests/integration/

# Ejecutar con cobertura de código
pytest --cov=mcp_dbutils

# Generar un informe de cobertura HTML
pytest --cov=mcp_dbutils --cov-report=html
```

### Fixtures de pytest

Las fixtures de pytest permiten configurar el entorno de prueba:

```python
@pytest.fixture
def sqlite_adapter():
    """Fixture que proporciona un adaptador SQLite configurado con una base de datos en memoria."""
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # Crear una tabla de prueba
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test VALUES (1, 'test1'), (2, 'test2')")
    connection.commit()
    
    yield adapter
    
    # Limpieza
    adapter.disconnect()

def test_with_fixture(sqlite_adapter):
    """Prueba el adaptador SQLite usando la fixture."""
    results = sqlite_adapter.execute_query("SELECT * FROM test WHERE id = 1")
    assert len(results) == 1
    assert results[0]["id"] == 1
    assert results[0]["name"] == "test1"
```

### Mocking

Utilizamos `unittest.mock` o `pytest-mock` para los mocks:

```python
def test_with_mock(mocker):
    """Prueba una función usando mocks."""
    # Crear un mock para la conexión a la base de datos
    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    
    # Configurar el mock para devolver resultados específicos
    mock_cursor.fetchall.return_value = [("test1",), ("test2",)]
    mock_cursor.description = [("name",)]
    
    # Reemplazar el método de conexión con el mock
    mocker.patch("mcp_dbutils.adapters.sqlite.sqlite3.connect", return_value=mock_connection)
    
    # Crear el adaptador
    adapter = SQLiteAdapter({"type": "sqlite", "path": "dummy.db"})
    
    # Ejecutar la consulta
    results = adapter.execute_query("SELECT name FROM test")
    
    # Verificar que la consulta se ejecutó correctamente
    mock_cursor.execute.assert_called_once_with("SELECT name FROM test")
    assert len(results) == 2
    assert results[0]["name"] == "test1"
    assert results[1]["name"] == "test2"
```

### Bases de Datos de Prueba

Para las pruebas de integración, utilizamos bases de datos reales:

- **SQLite**: Base de datos en memoria (`:memory:`)
- **PostgreSQL**: Instancia Docker para pruebas
- **MySQL**: Instancia Docker para pruebas

```python
@pytest.fixture(scope="session")
def postgres_adapter():
    """Fixture que proporciona un adaptador PostgreSQL configurado con una base de datos de prueba."""
    # Iniciar PostgreSQL con Docker
    container = start_postgres_container()
    
    # Esperar a que PostgreSQL esté listo
    wait_for_postgres(container)
    
    # Configurar el adaptador
    config = {
        "type": "postgres",
        "host": "localhost",
        "port": container.get_exposed_port(5432),
        "dbname": "testdb",
        "user": "postgres",
        "password": "postgres"
    }
    adapter = PostgreSQLAdapter(config)
    
    # Crear una tabla de prueba
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id SERIAL PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test (name) VALUES ('test1'), ('test2')")
    connection.commit()
    
    yield adapter
    
    # Limpieza
    adapter.disconnect()
    container.stop()
```

## Organización de las Pruebas

Las pruebas están organizadas en el directorio `tests/`:

```
tests/
├── __init__.py
├── conftest.py              # Fixtures compartidas
├── fixtures/                # Datos de prueba
│   ├── sqlite_schema.sql    # Esquema SQLite para pruebas
│   ├── postgres_schema.sql  # Esquema PostgreSQL para pruebas
│   └── mysql_schema.sql     # Esquema MySQL para pruebas
├── unit/                    # Pruebas unitarias
│   ├── __init__.py
│   ├── test_adapters.py     # Pruebas de adaptadores
│   ├── test_config.py       # Pruebas de configuración
│   ├── test_mcp.py          # Pruebas del protocolo MCP
│   └── test_query.py        # Pruebas de procesamiento de consultas
├── integration/             # Pruebas de integración
│   ├── __init__.py
│   ├── test_sqlite.py       # Pruebas de integración SQLite
│   ├── test_postgres.py     # Pruebas de integración PostgreSQL
│   └── test_mysql.py        # Pruebas de integración MySQL
└── e2e/                     # Pruebas de extremo a extremo
    ├── __init__.py
    └── test_mcp_server.py   # Pruebas del servidor MCP
```

## Mejores Prácticas

### Nomenclatura de Pruebas

Siga estas convenciones de nomenclatura:

- Los archivos de prueba comienzan con `test_`
- Las funciones de prueba comienzan con `test_`
- Los nombres de las pruebas deben ser descriptivos e indicar lo que se está probando

```python
# Bueno
def test_query_validator_rejects_insert_statements():
    ...

# Malo
def test_validator():
    ...
```

### Aserciones

Utilice las aserciones de pytest para mensajes de error más claros:

```python
# Bueno
assert result == expected, f"Se esperaba {expected}, se obtuvo {result}"

# Malo
if result != expected:
    raise AssertionError("Prueba fallida")
```

### Aislamiento de Pruebas

Cada prueba debe ser independiente:

- No depender del estado dejado por otras pruebas
- Utilizar fixtures para configurar y limpiar el entorno
- Evitar variables globales o compartidas

```python
# Bueno
def test_independent_1(sqlite_adapter):
    sqlite_adapter.execute_query("INSERT INTO test VALUES (3, 'test3')")
    results = sqlite_adapter.execute_query("SELECT * FROM test WHERE id = 3")
    assert len(results) == 1

def test_independent_2(sqlite_adapter):
    # Esta prueba no depende del estado creado por test_independent_1
    results = sqlite_adapter.execute_query("SELECT * FROM test WHERE id = 1")
    assert len(results) == 1
```

### Pruebas Parametrizadas

Utilice pruebas parametrizadas para probar múltiples casos:

```python
@pytest.mark.parametrize("query,is_valid", [
    ("SELECT * FROM users", True),
    ("INSERT INTO users VALUES (1, 'test')", False),
    ("UPDATE users SET name = 'test' WHERE id = 1", False),
    ("DELETE FROM users WHERE id = 1", False),
    ("DROP TABLE users", False),
])
def test_query_validator_parametrized(query, is_valid):
    """Prueba que el validador de consulta identifica correctamente las consultas no autorizadas."""
    validator = QueryValidator()
    assert validator.validate(query) is is_valid
```

### Pruebas de Regresión

Cree pruebas específicas para los bugs corregidos:

```python
def test_regression_issue_123():
    """Prueba que el bug #123 está corregido."""
    # El bug era: el adaptador SQLite no manejaba correctamente los valores NULL
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # Crear una tabla de prueba
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test VALUES (1, NULL)")
    connection.commit()
    
    # Verificar que los valores NULL se manejan correctamente
    results = adapter.execute_query("SELECT * FROM test WHERE id = 1")
    assert len(results) == 1
    assert results[0]["id"] == 1
    assert results[0]["name"] is None
```

## Integración Continua

Las pruebas se ejecutan automáticamente a través de GitHub Actions:

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

## Cobertura de Código

Aspiramos a una cobertura de código de al menos 90%:

```bash
# Ejecutar las pruebas con cobertura
pytest --cov=mcp_dbutils

# Generar un informe de cobertura HTML
pytest --cov=mcp_dbutils --cov-report=html
```

El informe de cobertura está disponible en el directorio `htmlcov/`.

## Solución de Problemas de Pruebas

### Pruebas que Fallan

Si una prueba falla:

1. Lea cuidadosamente el mensaje de error
2. Verifique las aserciones que fallaron
3. Utilice `pytest -v` para más detalles
4. Utilice `pytest --pdb` para depurar interactivamente

### Pruebas Lentas

Si las pruebas son lentas:

1. Identifique las pruebas lentas con `pytest --durations=10`
2. Utilice mocks en lugar de recursos reales cuando sea posible
3. Optimice las fixtures para reducir el tiempo de configuración
4. Utilice `pytest-xdist` para ejecutar las pruebas en paralelo

### Pruebas Inestables (Flaky)

Si las pruebas son inestables (fallan de manera aleatoria):

1. Identifique las pruebas inestables
2. Verifique las dependencias externas (bases de datos, red, etc.)
3. Asegúrese de que las pruebas estén aisladas
4. Utilice `pytest-rerunfailures` para volver a ejecutar las pruebas que fallan

## Conclusión

Las pruebas son esenciales para garantizar la calidad y fiabilidad de MCP Database Utilities. Siguiendo las mejores prácticas y utilizando las herramientas adecuadas, podemos mantener una suite de pruebas completa y eficaz que nos da confianza en nuestro código.
