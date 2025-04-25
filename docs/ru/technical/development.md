# Руководство по разработке

*[English](../../en/technical/development.md) | [中文](../../zh/technical/development.md) | [Français](../../fr/technical/development.md) | [Español](../../es/technical/development.md) | [العربية](../../ar/technical/development.md) | Русский*

Этот документ предоставляет подробную информацию о процессе разработки, стандартах кода и лучших практиках для вклада в проект MCP Database Utilities.

## Настройка среды разработки

### Предварительные требования

- Python 3.10 или выше
- Git
- Редактор кода или IDE (VS Code, PyCharm и т.д.)
- Docker (опционально, для тестирования с различными базами данных)

### Установка для разработки

1. **Клонирование репозитория**

```bash
git clone https://github.com/donghao1393/mcp-dbutils.git
cd mcp-dbutils
```

2. **Создание виртуального окружения**

```bash
# Использование venv
python -m venv venv
source venv/bin/activate  # На Linux/macOS
# или
.\venv\Scripts\activate  # На Windows

# Использование uv (рекомендуется)
uv venv
source .venv/bin/activate  # На Linux/macOS
# или
.\.venv\Scripts\activate  # На Windows
```

3. **Установка зависимостей для разработки**

```bash
# Использование pip
pip install -e ".[dev,test,docs]"

# Использование uv (рекомендуется)
uv pip install -e ".[dev,test,docs]"
```

4. **Настройка pre-commit хуков**

```bash
pre-commit install
```

### Базы данных для разработки

Для локальной разработки и тестирования вы можете использовать Docker для запуска различных баз данных:

#### SQLite

SQLite не требует специальной настройки, вам просто нужно создать файл базы данных:

```bash
# Создание тестовой базы данных SQLite
sqlite3 test.db < tests/fixtures/sqlite_schema.sql
```

#### PostgreSQL

```bash
# Запуск PostgreSQL с использованием Docker
docker run --name postgres-dev -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -p 5432:5432 -d postgres:14

# Создание тестовой базы данных
docker exec -i postgres-dev psql -U postgres -c "CREATE DATABASE testdb;"
docker exec -i postgres-dev psql -U postgres -d testdb < tests/fixtures/postgres_schema.sql
```

#### MySQL

```bash
# Запуск MySQL с использованием Docker
docker run --name mysql-dev -e MYSQL_ROOT_PASSWORD=mysql -e MYSQL_DATABASE=testdb -p 3306:3306 -d mysql:8

# Ожидание запуска MySQL
sleep 20

# Загрузка тестовой схемы
docker exec -i mysql-dev mysql -uroot -pmysql testdb < tests/fixtures/mysql_schema.sql
```

## Структура проекта

```
mcp-dbutils/
├── .github/                    # Конфигурации GitHub Actions
├── docs/                       # Документация
│   ├── en/                     # Документация на английском
│   ├── zh/                     # Документация на китайском
│   ├── fr/                     # Документация на французском
│   ├── es/                     # Документация на испанском
│   ├── ar/                     # Документация на арабском
│   └── ru/                     # Документация на русском
├── mcp_dbutils/                # Основной исходный код
│   ├── __init__.py             # Инициализация пакета
│   ├── __main__.py             # Точка входа для прямого выполнения
│   ├── adapters/               # Адаптеры баз данных
│   │   ├── __init__.py
│   │   ├── base.py             # Базовый класс для адаптеров
│   │   ├── sqlite.py           # Адаптер SQLite
│   │   ├── postgres.py         # Адаптер PostgreSQL
│   │   └── mysql.py            # Адаптер MySQL
│   ├── config/                 # Управление конфигурацией
│   │   ├── __init__.py
│   │   └── loader.py           # Загрузчик конфигурации
│   ├── mcp/                    # Реализация протокола MCP
│   │   ├── __init__.py
│   │   ├── server.py           # MCP-сервер
│   │   └── tools.py            # MCP-инструменты
│   ├── query/                  # Обработка запросов
│   │   ├── __init__.py
│   │   ├── parser.py           # Парсер запросов
│   │   └── validator.py        # Валидатор запросов
│   └── utils/                  # Утилиты
│       ├── __init__.py
│       ├── logging.py          # Конфигурация логирования
│       └── security.py         # Утилиты безопасности
├── tests/                      # Тесты
│   ├── __init__.py
│   ├── conftest.py             # Конфигурация pytest
│   ├── fixtures/               # Фикстуры для тестов
│   ├── unit/                   # Модульные тесты
│   └── integration/            # Интеграционные тесты
├── .gitignore                  # Файлы для игнорирования Git
├── .pre-commit-config.yaml     # Конфигурация pre-commit
├── LICENSE                     # Лицензия проекта
├── pyproject.toml              # Конфигурация Python-проекта
├── README.md                   # Основная документация
└── README_*.md                 # Документация на других языках
```

## Стандарты кода

### Стиль кода

Мы следуем [PEP 8](https://peps.python.org/pep-0008/) с некоторыми модификациями:

- Максимальная длина строки: 100 символов
- Использование двойных кавычек для строк
- Использование f-строк для форматирования строк

### Автоматическое форматирование

Мы используем следующие инструменты для автоматического форматирования:

- **Black**: для форматирования кода
- **isort**: для сортировки импортов
- **Ruff**: для линтинга и проверки кода

Эти инструменты настроены в `pyproject.toml` и автоматически запускаются через pre-commit.

### Документирование кода

Мы используем формат Google для документирования кода:

```python
def function_with_types_in_docstring(param1, param2):
    """Пример функции с типами в документации.

    Args:
        param1 (int): Первый параметр.
        param2 (str): Второй параметр.

    Returns:
        bool: Возвращаемое значение. True для успеха, False в противном случае.

    Raises:
        ValueError: Если param1 отрицательный.
        TypeError: Если param2 не строка.
    """
    if param1 < 0:
        raise ValueError("param1 должен быть положительным.")
    if not isinstance(param2, str):
        raise TypeError("param2 должен быть строкой.")
    return True
```

### Соглашения об именовании

- **Классы**: PascalCase (пример: `DatabaseAdapter`)
- **Функции и методы**: snake_case (пример: `connect_to_database`)
- **Переменные**: snake_case (пример: `connection_pool`)
- **Константы**: UPPER_SNAKE_CASE (пример: `MAX_CONNECTIONS`)
- **Модули**: snake_case (пример: `database_adapter.py`)
- **Пакеты**: snake_case (пример: `mcp_dbutils`)

### Импорты

Организуйте импорты в следующем порядке:

1. Импорты из стандартной библиотеки
2. Импорты из внешних библиотек
3. Импорты из проекта

Используйте isort для автоматической сортировки импортов.

## Процесс разработки

### Git-рабочий процесс

Мы следуем рабочему процессу, основанному на функциях:

1. Создайте ветку от `main` для каждой функции или исправления
2. Назовите ветку в соответствии с форматом: `feature/название-функции` или `fix/название-исправления`
3. Делайте регулярные коммиты с ясными сообщениями
4. Отправьте pull request в `main`, когда функция готова

### Сообщения коммитов

Мы следуем формату [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Распространенные типы:
- `feat`: новая функция
- `fix`: исправление бага
- `docs`: изменения в документации
- `style`: форматирование, отсутствующие точки с запятой и т.д. (без изменения кода)
- `refactor`: рефакторинг кода
- `test`: добавление или исправление тестов
- `chore`: задачи обслуживания, обновления зависимостей и т.д.

Примеры:
```
feat(sqlite): добавлена поддержка параметризованных запросов
fix(postgres): исправлено управление таймаутами соединений
docs: обновлена документация по установке
```

### Pull Requests

- Создайте pull request (PR) для каждой функции или исправления
- Убедитесь, что все тесты проходят
- Убедитесь, что код правильно отформатирован
- Запросите обзор кода как минимум от одного другого разработчика
- Разрешите все комментарии перед слиянием

### Обзор кода

При обзоре кода проверьте:

1. **Функциональность**: Делает ли код то, что должен делать?
2. **Качество**: Хорошо ли написан код, читабелен ли он, поддерживаем ли?
3. **Тесты**: Есть ли соответствующие тесты?
4. **Документация**: Обновлена ли документация?
5. **Безопасность**: Есть ли потенциальные проблемы безопасности?

## Тестирование

### Типы тестов

- **Модульные тесты**: Тестируют отдельные функции или классы
- **Интеграционные тесты**: Тестируют взаимодействие между несколькими компонентами
- **End-to-end тесты**: Тестируют полную систему

### Запуск тестов

```bash
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

### Написание тестов

Используйте pytest для написания тестов:

```python
def test_connection_success():
    """Тест успешного соединения с базой данных с валидными параметрами."""
    config = {
        "type": "sqlite",
        "path": ":memory:"
    }
    adapter = SQLiteAdapter(config)
    connection = adapter.connect()
    assert connection is not None
    adapter.disconnect()

def test_connection_failure():
    """Тест неудачного соединения с невалидными параметрами."""
    config = {
        "type": "sqlite",
        "path": "/nonexistent/path/to/db.sqlite"
    }
    adapter = SQLiteAdapter(config)
    with pytest.raises(ConnectionError):
        adapter.connect()
```

### Моки

Используйте `unittest.mock` или `pytest-mock` для моков:

```python
def test_query_execution(mocker):
    """Тест выполнения запроса с моком соединения."""
    # Создание мока соединения
    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    
    # Настройка мока для возврата конкретных результатов
    mock_cursor.fetchall.return_value = [("row1",), ("row2",)]
    mock_cursor.description = [("column1",)]
    
    # Внедрение мока в адаптер
    adapter = SQLiteAdapter({"type": "sqlite", "path": ":memory:"})
    adapter._connection = mock_connection
    
    # Выполнение запроса
    results = adapter.execute_query("SELECT * FROM test")
    
    # Проверка, что запрос был выполнен правильно
    mock_cursor.execute.assert_called_once_with("SELECT * FROM test")
    assert len(results) == 2
    assert results[0][0] == "row1"
    assert results[1][0] == "row2"
```

## Документация

### Документирование кода

- Документируйте все публичные классы, методы и функции
- Используйте формат документации Google
- Включайте примеры использования, когда это уместно

### Документация проекта

- Поддерживайте README.md в актуальном состоянии с основной информацией
- Документируйте функции в директории `docs/`
- Предоставляйте примеры использования

### Создание документации

Мы используем MkDocs для создания документации:

```bash
# Установка MkDocs и зависимостей
pip install mkdocs mkdocs-material

# Сборка документации
mkdocs build

# Локальное обслуживание документации
mkdocs serve
```

## Версионирование и публикация

### Семантическое версионирование

Мы следуем [Семантическому версионированию](https://semver.org/):

- **MAJOR**: несовместимые изменения API
- **MINOR**: добавление функциональности с обратной совместимостью
- **PATCH**: исправления багов с обратной совместимостью

### Процесс публикации

1. Обновите версию в `pyproject.toml`
2. Обновите CHANGELOG.md
3. Создайте Git-тег с новой версией
4. Отправьте тег в GitHub
5. GitHub Actions автоматически соберет и опубликует пакет на PyPI

```bash
# Пример процесса публикации
# 1. Обновление версии в pyproject.toml
# 2. Обновление CHANGELOG.md
# 3. Коммит изменений
git add pyproject.toml CHANGELOG.md
git commit -m "chore: подготовка к релизу 1.2.3"

# 4. Создание и отправка тега
git tag v1.2.3
git push origin main v1.2.3
```

## Непрерывная интеграция

Мы используем GitHub Actions для непрерывной интеграции:

- **Lint**: проверяет стиль кода
- **Test**: запускает тесты на различных версиях Python и операционных системах
- **Build**: собирает пакет
- **Publish**: публикует пакет на PyPI (только для тегов)

Рабочие процессы определены в директории `.github/workflows/`.

## Дополнительные ресурсы

- [Документация Python](https://docs.python.org/)
- [PEP 8 -- Руководство по стилю кода Python](https://peps.python.org/pep-0008/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Документация pytest](https://docs.pytest.org/)
- [Документация Black](https://black.readthedocs.io/)
- [Документация isort](https://pycqa.github.io/isort/)
- [Документация Ruff](https://beta.ruff.rs/docs/)
- [Документация pre-commit](https://pre-commit.com/)
