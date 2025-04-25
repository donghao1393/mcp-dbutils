# Руководство по тестированию

*[English](../../en/technical/testing.md) | [中文](../../zh/technical/testing.md) | [Français](../../fr/technical/testing.md) | [Español](../../es/technical/testing.md) | [العربية](../../ar/technical/testing.md) | Русский*

Этот документ описывает стратегию тестирования, инструменты и лучшие практики для тестирования MCP Database Utilities.

## Философия тестирования

Наш подход к тестированию основан на следующих принципах:

1. **Всеобъемлющие тесты**: Покрытие всех аспектов кода, от отдельных функций до полной системы
2. **Автоматизированные тесты**: Все тесты должны быть автоматизированы и выполняемы через CI/CD
3. **Быстрые тесты**: Тесты должны выполняться быстро для обеспечения быстрой обратной связи
4. **Изолированные тесты**: Каждый тест должен быть независимым и не зависеть от других тестов
5. **Детерминированные тесты**: Тесты должны давать одинаковые результаты при каждом выполнении

## Типы тестов

### Модульные тесты

Модульные тесты проверяют поведение отдельных компонентов (функций, классов, методов) в изоляции.

**Характеристики**:
- Быстрое выполнение
- Тестируют одну единицу кода
- Используют моки для изоляции тестируемого кода
- Не зависят от внешних ресурсов (баз данных, сети и т.д.)

**Пример**:

```python
def test_query_validator():
    """Тест, что валидатор запросов правильно идентифицирует неавторизованные запросы."""
    validator = QueryValidator()
    
    # Валидный SELECT-запрос
    assert validator.validate("SELECT * FROM users") is True
    
    # Неавторизованные запросы
    assert validator.validate("INSERT INTO users VALUES (1, 'test')") is False
    assert validator.validate("UPDATE users SET name = 'test' WHERE id = 1") is False
    assert validator.validate("DELETE FROM users WHERE id = 1") is False
    assert validator.validate("DROP TABLE users") is False
```

### Интеграционные тесты

Интеграционные тесты проверяют, что различные компоненты правильно работают вместе.

**Характеристики**:
- Медленнее модульных тестов
- Тестируют взаимодействие между несколькими компонентами
- Могут использовать реальные или моковые внешние ресурсы
- Проверяют, что интерфейсы между компонентами работают правильно

**Пример**:

```python
def test_sqlite_adapter_integration():
    """Интеграционный тест между SQLite-адаптером и менеджером запросов."""
    # Создание SQLite базы данных в памяти
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # Создание тестовой таблицы
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test VALUES (1, 'test1'), (2, 'test2')")
    connection.commit()
    
    # Создание менеджера запросов с адаптером
    query_manager = QueryManager(adapter)
    
    # Выполнение запроса через менеджер
    results = query_manager.execute("SELECT * FROM test WHERE id = 1")
    
    # Проверка результатов
    assert len(results) == 1
    assert results[0]["id"] == 1
    assert results[0]["name"] == "test1"
```

### End-to-End тесты

End-to-End тесты проверяют, что полная система работает правильно от начала до конца.

**Характеристики**:
- Самые медленные в выполнении
- Тестируют полную систему в среде, близкой к продакшену
- Используют реальные внешние ресурсы
- Проверяют реальные сценарии использования

**Пример**:

```python
def test_mcp_server_end_to_end():
    """End-to-End тест MCP-сервера с реальной базой данных."""
    # Запуск MCP-сервера с тестовой конфигурацией
    config_path = "tests/fixtures/test_config.yaml"
    server = MCPServer(config_path)
    server.start()
    
    try:
        # Создание моковского MCP-клиента
        client = MockMCPClient()
        
        # Выполнение запроса через MCP-протокол
        response = client.execute_tool("dbutils-list-tables", {"connection": "test-sqlite"})
        
        # Проверка ответа
        assert "tables" in response
        assert "test" in response["tables"]
        
        # Выполнение SQL-запроса
        response = client.execute_tool("dbutils-run-query", {
            "connection": "test-sqlite",
            "query": "SELECT * FROM test WHERE id = 1"
        })
        
        # Проверка результатов
        assert len(response["results"]) == 1
        assert response["results"][0]["id"] == 1
        assert response["results"][0]["name"] == "test1"
    finally:
        # Остановка сервера
        server.stop()
```

### Тесты производительности

Тесты производительности проверяют, что система соответствует требованиям к производительности.

**Характеристики**:
- Измеряют время выполнения, использование памяти и т.д.
- Проверяют, что система может справиться с ожидаемой нагрузкой
- Выявляют узкие места

**Пример**:

```python
def test_query_performance():
    """Тест производительности запросов."""
    # Настройка адаптера с тестовой базой данных
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # Создание тестовой таблицы с множеством строк
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    
    # Вставка 10000 строк
    for i in range(10000):
        cursor.execute("INSERT INTO test VALUES (?, ?)", (i, f"test{i}"))
    connection.commit()
    
    # Измерение времени выполнения запроса
    start_time = time.time()
    results = adapter.execute_query("SELECT * FROM test WHERE id < 1000")
    end_time = time.time()
    
    # Проверка, что запрос выполняется менее чем за 100 мс
    assert end_time - start_time < 0.1
    assert len(results) == 1000
```

### Тесты безопасности

Тесты безопасности проверяют, что система защищена от атак.

**Характеристики**:
- Проверяют, что система устойчива к известным атакам
- Тестируют механизмы безопасности
- Выявляют потенциальные уязвимости

**Пример**:

```python
def test_sql_injection_prevention():
    """Тест, что система защищена от SQL-инъекций."""
    # Настройка адаптера с тестовой базой данных
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # Создание тестовой таблицы
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'secret')")
    connection.commit()
    
    # Создание менеджера запросов с адаптером
    query_manager = QueryManager(adapter)
    
    # Попытка SQL-инъекции
    malicious_query = "SELECT * FROM users WHERE username = 'admin' OR 1=1 --'"
    
    # Проверка, что менеджер запросов обнаруживает и предотвращает инъекцию
    with pytest.raises(SecurityException):
        query_manager.execute(malicious_query)
```

## Инструменты тестирования

### pytest

Мы используем [pytest](https://docs.pytest.org/) в качестве основного фреймворка для тестирования:

```bash
# Установка pytest и плагинов
pip install pytest pytest-cov pytest-mock

# Запуск всех тестов
pytest

# Запуск конкретных тестов
pytest tests/unit/
pytest tests/integration/

# Запуск с покрытием кода
pytest --cov=mcp_dbutils

# Создание HTML-отчета о покрытии
pytest --cov=mcp_dbutils --cov-report=html
```

### pytest фикстуры

Фикстуры pytest позволяют настраивать среду тестирования:

```python
@pytest.fixture
def sqlite_adapter():
    """Фикстура, предоставляющая SQLite-адаптер, настроенный с базой данных в памяти."""
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # Создание тестовой таблицы
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test VALUES (1, 'test1'), (2, 'test2')")
    connection.commit()
    
    yield adapter
    
    # Очистка
    adapter.disconnect()

def test_with_fixture(sqlite_adapter):
    """Тест SQLite-адаптера с использованием фикстуры."""
    results = sqlite_adapter.execute_query("SELECT * FROM test WHERE id = 1")
    assert len(results) == 1
    assert results[0]["id"] == 1
    assert results[0]["name"] == "test1"
```

### Моки

Мы используем `unittest.mock` или `pytest-mock` для моков:

```python
def test_with_mock(mocker):
    """Тест функции с использованием моков."""
    # Создание мока для соединения с базой данных
    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    
    # Настройка мока для возврата конкретных результатов
    mock_cursor.fetchall.return_value = [("test1",), ("test2",)]
    mock_cursor.description = [("name",)]
    
    # Замена метода соединения моком
    mocker.patch("mcp_dbutils.adapters.sqlite.sqlite3.connect", return_value=mock_connection)
    
    # Создание адаптера
    adapter = SQLiteAdapter({"type": "sqlite", "path": "dummy.db"})
    
    # Выполнение запроса
    results = adapter.execute_query("SELECT name FROM test")
    
    # Проверка, что запрос был выполнен правильно
    mock_cursor.execute.assert_called_once_with("SELECT name FROM test")
    assert len(results) == 2
    assert results[0]["name"] == "test1"
    assert results[1]["name"] == "test2"
```

### Тестовые базы данных

Для интеграционных тестов мы используем реальные базы данных:

- **SQLite**: база данных в памяти (`:memory:`)
- **PostgreSQL**: Docker-версия для тестов
- **MySQL**: Docker-версия для тестов

```python
@pytest.fixture(scope="session")
def postgres_adapter():
    """Фикстура, предоставляющая PostgreSQL-адаптер, настроенный с тестовой базой данных."""
    # Запуск PostgreSQL с Docker
    container = start_postgres_container()
    
    # Ожидание готовности PostgreSQL
    wait_for_postgres(container)
    
    # Настройка адаптера
    config = {
        "type": "postgres",
        "host": "localhost",
        "port": container.get_exposed_port(5432),
        "dbname": "testdb",
        "user": "postgres",
        "password": "postgres"
    }
    adapter = PostgreSQLAdapter(config)
    
    # Создание тестовой таблицы
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id SERIAL PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test (name) VALUES ('test1'), ('test2')")
    connection.commit()
    
    yield adapter
    
    # Очистка
    adapter.disconnect()
    container.stop()
```

## Организация тестов

Тесты организованы в директории `tests/`:

```
tests/
├── __init__.py
├── conftest.py              # Общие фикстуры
├── fixtures/                # Тестовые данные
│   ├── sqlite_schema.sql    # Схема SQLite для тестов
│   ├── postgres_schema.sql  # Схема PostgreSQL для тестов
│   └── mysql_schema.sql     # Схема MySQL для тестов
├── unit/                    # Модульные тесты
│   ├── __init__.py
│   ├── test_adapters.py     # Тесты адаптеров
│   ├── test_config.py       # Тесты конфигурации
│   ├── test_mcp.py          # Тесты MCP-протокола
│   └── test_query.py        # Тесты обработки запросов
├── integration/             # Интеграционные тесты
│   ├── __init__.py
│   ├── test_sqlite.py       # Интеграционные тесты SQLite
│   ├── test_postgres.py     # Интеграционные тесты PostgreSQL
│   └── test_mysql.py        # Интеграционные тесты MySQL
└── e2e/                     # End-to-End тесты
    ├── __init__.py
    └── test_mcp_server.py   # Тесты MCP-сервера
```

## Лучшие практики

### Именование тестов

Следуйте этим соглашениям об именовании:

- Файлы тестов начинаются с `test_`
- Функции тестов начинаются с `test_`
- Имена тестов должны быть описательными и указывать на то, что тестируется

```python
# Хорошо
def test_query_validator_rejects_insert_statements():
    ...

# Плохо
def test_validator():
    ...
```

### Утверждения

Используйте утверждения pytest для более ясных сообщений об ошибках:

```python
# Хорошо
assert result == expected, f"Ожидалось {expected}, получено {result}"

# Плохо
if result != expected:
    raise AssertionError("Тест не пройден")
```

### Изоляция тестов

Каждый тест должен быть независимым:

- Не зависит от состояния, оставленного другими тестами
- Использует фикстуры для настройки и очистки среды
- Избегает глобальных или общих переменных

```python
# Хорошо
def test_independent_1(sqlite_adapter):
    sqlite_adapter.execute_query("INSERT INTO test VALUES (3, 'test3')")
    results = sqlite_adapter.execute_query("SELECT * FROM test WHERE id = 3")
    assert len(results) == 1

def test_independent_2(sqlite_adapter):
    # Этот тест не зависит от состояния, созданного test_independent_1
    results = sqlite_adapter.execute_query("SELECT * FROM test WHERE id = 1")
    assert len(results) == 1
```

### Параметризованные тесты

Используйте параметризованные тесты для тестирования множества случаев:

```python
@pytest.mark.parametrize("query,is_valid", [
    ("SELECT * FROM users", True),
    ("INSERT INTO users VALUES (1, 'test')", False),
    ("UPDATE users SET name = 'test' WHERE id = 1", False),
    ("DELETE FROM users WHERE id = 1", False),
    ("DROP TABLE users", False),
])
def test_query_validator_parametrized(query, is_valid):
    """Тест, что валидатор запросов правильно идентифицирует неавторизованные запросы."""
    validator = QueryValidator()
    assert validator.validate(query) is is_valid
```

### Регрессионные тесты

Создавайте специфические тесты для исправленных ошибок:

```python
def test_regression_issue_123():
    """Тест, что ошибка #123 исправлена."""
    # Ошибка была: SQLite-адаптер неправильно обрабатывал NULL-значения
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # Создание тестовой таблицы
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test VALUES (1, NULL)")
    connection.commit()
    
    # Проверка, что NULL-значения обрабатываются правильно
    results = adapter.execute_query("SELECT * FROM test WHERE id = 1")
    assert len(results) == 1
    assert results[0]["id"] == 1
    assert results[0]["name"] is None
```

## Непрерывная интеграция

Тесты автоматически запускаются через GitHub Actions:

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

## Покрытие кода

Мы стремимся к покрытию кода не менее 90%:

```bash
# Запуск тестов с покрытием
pytest --cov=mcp_dbutils

# Создание HTML-отчета о покрытии
pytest --cov=mcp_dbutils --cov-report=html
```

Отчет о покрытии доступен в директории `htmlcov/`.

## Устранение неполадок с тестами

### Неудачные тесты

Если тест не проходит:

1. Внимательно прочитайте сообщение об ошибке
2. Проверьте неудачные утверждения
3. Используйте `pytest -v` для получения дополнительной информации
4. Используйте `pytest --pdb` для интерактивной отладки

### Медленные тесты

Если тесты выполняются медленно:

1. Идентифицируйте медленные тесты с помощью `pytest --durations=10`
2. Используйте моки вместо реальных ресурсов, когда это возможно
3. Оптимизируйте фикстуры для уменьшения времени настройки
4. Используйте `pytest-xdist` для параллельного выполнения тестов

### Нестабильные тесты (флаки)

Если тесты нестабильны (случайно не проходят):

1. Идентифицируйте нестабильные тесты
2. Проверьте внешние зависимости (базы данных, сеть и т.д.)
3. Убедитесь, что тесты изолированы
4. Используйте `pytest-rerunfailures` для повторного запуска неудачных тестов

## Заключение

Тестирование необходимо для обеспечения качества и надежности MCP Database Utilities. Следуя лучшим практикам и используя соответствующие инструменты, мы можем поддерживать всеобъемлющий и эффективный набор тестов, который дает нам уверенность в нашем коде.
