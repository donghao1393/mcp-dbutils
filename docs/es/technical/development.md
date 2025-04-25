# Guía de Desarrollo

*[English](../../en/technical/development.md) | [中文](../../zh/technical/development.md) | [Français](../../fr/technical/development.md) | Español | [العربية](../../ar/technical/development.md) | [Русский](../../ru/technical/development.md)*

Este documento proporciona información detallada sobre el proceso de desarrollo, estándares de código y mejores prácticas para contribuir al proyecto MCP Database Utilities.

## Configuración del Entorno de Desarrollo

### Requisitos Previos

- Python 3.10 o superior
- Git
- Editor de código o IDE (VS Code, PyCharm, etc.)
- Docker (opcional, para pruebas con diferentes bases de datos)

### Instalación para Desarrollo

1. **Clonar el Repositorio**

```bash
git clone https://github.com/donghao1393/mcp-dbutils.git
cd mcp-dbutils
```

2. **Crear un Entorno Virtual**

```bash
# Con venv
python -m venv venv
source venv/bin/activate  # En Linux/macOS
# o
.\venv\Scripts\activate  # En Windows

# Con uv (recomendado)
uv venv
source .venv/bin/activate  # En Linux/macOS
# o
.\.venv\Scripts\activate  # En Windows
```

3. **Instalar Dependencias de Desarrollo**

```bash
# Con pip
pip install -e ".[dev,test,docs]"

# Con uv (recomendado)
uv pip install -e ".[dev,test,docs]"
```

4. **Configurar Hooks de Pre-commit**

```bash
pre-commit install
```

### Bases de Datos para Desarrollo

Para desarrollar y probar localmente, puede usar Docker para ejecutar diferentes bases de datos:

#### SQLite

SQLite no requiere configuración especial, solo necesita crear un archivo de base de datos:

```bash
# Crear una base de datos SQLite de prueba
sqlite3 test.db < tests/fixtures/sqlite_schema.sql
```

#### PostgreSQL

```bash
# Iniciar PostgreSQL con Docker
docker run --name postgres-dev -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -p 5432:5432 -d postgres:14

# Crear una base de datos de prueba
docker exec -i postgres-dev psql -U postgres -c "CREATE DATABASE testdb;"
docker exec -i postgres-dev psql -U postgres -d testdb < tests/fixtures/postgres_schema.sql
```

#### MySQL

```bash
# Iniciar MySQL con Docker
docker run --name mysql-dev -e MYSQL_ROOT_PASSWORD=mysql -e MYSQL_DATABASE=testdb -p 3306:3306 -d mysql:8

# Esperar a que MySQL inicie
sleep 20

# Cargar el esquema de prueba
docker exec -i mysql-dev mysql -uroot -pmysql testdb < tests/fixtures/mysql_schema.sql
```

## Estructura del Proyecto

```
mcp-dbutils/
├── .github/                    # Configuraciones GitHub Actions
├── docs/                       # Documentación
│   ├── en/                     # Documentación en inglés
│   ├── zh/                     # Documentación en chino
│   ├── fr/                     # Documentación en francés
│   ├── es/                     # Documentación en español
│   ├── ar/                     # Documentación en árabe
│   └── ru/                     # Documentación en ruso
├── mcp_dbutils/                # Código fuente principal
│   ├── __init__.py             # Inicialización del paquete
│   ├── __main__.py             # Punto de entrada para ejecución directa
│   ├── adapters/               # Adaptadores de base de datos
│   │   ├── __init__.py
│   │   ├── base.py             # Clase base para adaptadores
│   │   ├── sqlite.py           # Adaptador SQLite
│   │   ├── postgres.py         # Adaptador PostgreSQL
│   │   └── mysql.py            # Adaptador MySQL
│   ├── config/                 # Gestión de configuración
│   │   ├── __init__.py
│   │   └── loader.py           # Cargador de configuración
│   ├── mcp/                    # Implementación del protocolo MCP
│   │   ├── __init__.py
│   │   ├── server.py           # Servidor MCP
│   │   └── tools.py            # Herramientas MCP
│   ├── query/                  # Procesamiento de consultas
│   │   ├── __init__.py
│   │   ├── parser.py           # Analizador de consultas
│   │   └── validator.py        # Validador de consultas
│   └── utils/                  # Utilidades
│       ├── __init__.py
│       ├── logging.py          # Configuración de registro
│       └── security.py         # Utilidades de seguridad
├── tests/                      # Pruebas
│   ├── __init__.py
│   ├── conftest.py             # Configuración pytest
│   ├── fixtures/               # Fixtures para pruebas
│   ├── unit/                   # Pruebas unitarias
│   └── integration/            # Pruebas de integración
├── .gitignore                  # Archivos a ignorar por Git
├── .pre-commit-config.yaml     # Configuración pre-commit
├── LICENSE                     # Licencia del proyecto
├── pyproject.toml              # Configuración del proyecto Python
├── README.md                   # Documentación principal
└── README_*.md                 # Documentación en otros idiomas
```

## Estándares de Código

### Estilo de Código

Seguimos [PEP 8](https://peps.python.org/pep-0008/) con algunas modificaciones:

- Longitud máxima de línea: 100 caracteres
- Uso de comillas dobles para cadenas de texto
- Uso de f-strings para formateo de cadenas

### Formateo Automático

Utilizamos las siguientes herramientas para el formateo automático:

- **Black**: Para el formateo del código
- **isort**: Para ordenar importaciones
- **Ruff**: Para linting y verificación del código

Estas herramientas están configuradas en `pyproject.toml` y se ejecutan automáticamente a través de pre-commit.

### Docstrings

Utilizamos el formato Google para docstrings:

```python
def function_with_types_in_docstring(param1, param2):
    """Ejemplo de función con documentación de tipos.

    Args:
        param1 (int): El primer parámetro.
        param2 (str): El segundo parámetro.

    Returns:
        bool: El valor de retorno. True para éxito, False en caso contrario.

    Raises:
        ValueError: Si param1 es negativo.
        TypeError: Si param2 no es una cadena.
    """
    if param1 < 0:
        raise ValueError("param1 debe ser positivo.")
    if not isinstance(param2, str):
        raise TypeError("param2 debe ser una cadena.")
    return True
```

### Convenciones de Nomenclatura

- **Clases**: PascalCase (ej: `DatabaseAdapter`)
- **Funciones y métodos**: snake_case (ej: `connect_to_database`)
- **Variables**: snake_case (ej: `connection_pool`)
- **Constantes**: UPPER_SNAKE_CASE (ej: `MAX_CONNECTIONS`)
- **Módulos**: snake_case (ej: `database_adapter.py`)
- **Paquetes**: snake_case (ej: `mcp_dbutils`)

### Importaciones

Organice las importaciones en el siguiente orden:

1. Importaciones de la biblioteca estándar
2. Importaciones de bibliotecas de terceros
3. Importaciones del proyecto

Utilice isort para ordenar automáticamente las importaciones.

## Proceso de Desarrollo

### Flujo de Trabajo Git

Seguimos un flujo de trabajo basado en características:

1. Cree una rama desde `main` para cada característica o corrección
2. Nombre la rama según el formato: `feature/nombre-de-la-caracteristica` o `fix/nombre-de-la-correccion`
3. Haga commits regulares con mensajes claros
4. Envíe un Pull Request a `main` cuando la característica esté lista

### Mensajes de Commit

Seguimos el formato [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Tipos comunes:
- `feat`: Nueva característica
- `fix`: Corrección de bug
- `docs`: Cambios en la documentación
- `style`: Formateo, punto y coma faltante, etc. (sin cambio de código)
- `refactor`: Refactorización de código
- `test`: Adición o corrección de pruebas
- `chore`: Tareas de mantenimiento, actualizaciones de dependencias, etc.

Ejemplos:
```
feat(sqlite): añadir soporte para consultas parametrizadas
fix(postgres): corregir gestión de tiempos de espera de conexión
docs: actualizar documentación de instalación
```

### Pull Requests

- Cree un Pull Request (PR) para cada característica o corrección
- Asegúrese de que todas las pruebas pasen
- Asegúrese de que el código esté formateado correctamente
- Solicite una revisión de código de al menos otro desarrollador
- Resuelva todos los comentarios antes de fusionar

### Revisión de Código

Al revisar código, verifique:

1. **Funcionalidad**: ¿El código hace lo que se supone que debe hacer?
2. **Calidad**: ¿El código está bien escrito, es legible y mantenible?
3. **Pruebas**: ¿Hay pruebas apropiadas?
4. **Documentación**: ¿La documentación está actualizada?
5. **Seguridad**: ¿Hay problemas de seguridad potenciales?

## Pruebas

### Tipos de Pruebas

- **Pruebas Unitarias**: Prueban funciones o clases individuales
- **Pruebas de Integración**: Prueban la interacción entre varios componentes
- **Pruebas de Extremo a Extremo**: Prueban el sistema completo

### Ejecución de Pruebas

```bash
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

### Escritura de Pruebas

Utilice pytest para escribir pruebas:

```python
def test_connection_success():
    """Prueba que la conexión a la base de datos tiene éxito con parámetros válidos."""
    config = {
        "type": "sqlite",
        "path": ":memory:"
    }
    adapter = SQLiteAdapter(config)
    connection = adapter.connect()
    assert connection is not None
    adapter.disconnect()

def test_connection_failure():
    """Prueba que la conexión falla con parámetros inválidos."""
    config = {
        "type": "sqlite",
        "path": "/nonexistent/path/to/db.sqlite"
    }
    adapter = SQLiteAdapter(config)
    with pytest.raises(ConnectionError):
        adapter.connect()
```

### Mocking

Utilice `unittest.mock` o `pytest-mock` para mocks:

```python
def test_query_execution(mocker):
    """Prueba la ejecución de consulta con un mock de conexión."""
    # Crear un mock para la conexión
    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    
    # Configurar el mock para devolver resultados específicos
    mock_cursor.fetchall.return_value = [("row1",), ("row2",)]
    mock_cursor.description = [("column1",)]
    
    # Inyectar el mock en el adaptador
    adapter = SQLiteAdapter({"type": "sqlite", "path": ":memory:"})
    adapter._connection = mock_connection
    
    # Ejecutar la consulta
    results = adapter.execute_query("SELECT * FROM test")
    
    # Verificar que la consulta se ejecutó correctamente
    mock_cursor.execute.assert_called_once_with("SELECT * FROM test")
    assert len(results) == 2
    assert results[0][0] == "row1"
    assert results[1][0] == "row2"
```

## Documentación

### Documentación del Código

- Documente todas las clases, métodos y funciones públicas
- Utilice el formato de docstring Google
- Incluya ejemplos de uso cuando sea relevante

### Documentación del Proyecto

- Mantenga actualizado el README.md con información esencial
- Documente las características en el directorio `docs/`
- Proporcione ejemplos de uso

### Generación de Documentación

Utilizamos MkDocs para generar la documentación:

```bash
# Instalar MkDocs y dependencias
pip install mkdocs mkdocs-material

# Generar la documentación
mkdocs build

# Servir la documentación localmente
mkdocs serve
```

## Versionado y Publicación

### Versionado Semántico

Seguimos el [Versionado Semántico](https://semver.org/):

- **MAJOR**: Cambios incompatibles con versiones anteriores
- **MINOR**: Adiciones de características retrocompatibles
- **PATCH**: Correcciones de bugs retrocompatibles

### Proceso de Publicación

1. Actualice la versión en `pyproject.toml`
2. Actualice el CHANGELOG.md
3. Cree una etiqueta Git con la nueva versión
4. Envíe la etiqueta a GitHub
5. GitHub Actions construirá y publicará automáticamente el paquete en PyPI

```bash
# Ejemplo de proceso de publicación
# 1. Actualizar la versión en pyproject.toml
# 2. Actualizar CHANGELOG.md
# 3. Commit de los cambios
git add pyproject.toml CHANGELOG.md
git commit -m "chore: preparar versión 1.2.3"

# 4. Crear y enviar la etiqueta
git tag v1.2.3
git push origin main v1.2.3
```

## Integración Continua

Utilizamos GitHub Actions para la integración continua:

- **Lint**: Verifica el estilo del código
- **Test**: Ejecuta las pruebas en diferentes versiones de Python y sistemas operativos
- **Build**: Construye el paquete
- **Publish**: Publica el paquete en PyPI (solo para etiquetas)

Los flujos de trabajo están definidos en el directorio `.github/workflows/`.

## Recursos Adicionales

- [Documentación de Python](https://docs.python.org/)
- [PEP 8 -- Guía de Estilo para Código Python](https://peps.python.org/pep-0008/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Documentación de pytest](https://docs.pytest.org/)
- [Documentación de Black](https://black.readthedocs.io/)
- [Documentación de isort](https://pycqa.github.io/isort/)
- [Documentación de Ruff](https://beta.ruff.rs/docs/)
- [Documentación de pre-commit](https://pre-commit.com/)
