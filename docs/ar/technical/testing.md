# دليل الاختبار

*[English](../../en/technical/testing.md) | [中文](../../zh/technical/testing.md) | [Français](../../fr/technical/testing.md) | [Español](../../es/technical/testing.md) | العربية | [Русский](../../ru/technical/testing.md)*

يصف هذا المستند استراتيجية الاختبار، والأدوات، وأفضل الممارسات لاختبار MCP Database Utilities.

## فلسفة الاختبار

يعتمد نهجنا في الاختبار على المبادئ التالية:

1. **اختبارات شاملة**: تغطية جميع جوانب الكود، من الدوال الفردية إلى النظام الكامل
2. **اختبارات آلية**: يجب أن تكون جميع الاختبارات آلية وقابلة للتنفيذ عبر CI/CD
3. **اختبارات سريعة**: يجب أن تنفذ الاختبارات بسرعة للسماح بتغذية راجعة سريعة
4. **اختبارات معزولة**: يجب أن يكون كل اختبار مستقلاً ولا يعتمد على اختبارات أخرى
5. **اختبارات حتمية**: يجب أن تنتج الاختبارات نفس النتائج في كل تنفيذ

## أنواع الاختبارات

### اختبارات الوحدة

تتحقق اختبارات الوحدة من سلوك المكونات الفردية (الدوال، الفئات، الطرق) في عزلة.

**الخصائص**:
- سريعة التنفيذ
- تختبر وحدة كود واحدة
- تستخدم المحاكاة لعزل الكود المختبر
- لا تعتمد على موارد خارجية (قواعد بيانات، شبكة، إلخ)

**مثال**:

```python
def test_query_validator():
    """اختبار أن مدقق الاستعلام يحدد بشكل صحيح الاستعلامات غير المصرح بها."""
    validator = QueryValidator()
    
    # استعلام SELECT صالح
    assert validator.validate("SELECT * FROM users") is True
    
    # استعلامات غير مصرح بها
    assert validator.validate("INSERT INTO users VALUES (1, 'test')") is False
    assert validator.validate("UPDATE users SET name = 'test' WHERE id = 1") is False
    assert validator.validate("DELETE FROM users WHERE id = 1") is False
    assert validator.validate("DROP TABLE users") is False
```

### اختبارات التكامل

تتحقق اختبارات التكامل من أن المكونات المختلفة تعمل بشكل صحيح معًا.

**الخصائص**:
- أبطأ من اختبارات الوحدة
- تختبر التفاعل بين عدة مكونات
- يمكن أن تستخدم موارد خارجية حقيقية أو محاكاة
- تتحقق من أن الواجهات بين المكونات تعمل بشكل صحيح

**مثال**:

```python
def test_sqlite_adapter_integration():
    """اختبار التكامل بين محول SQLite ومدير الاستعلامات."""
    # إنشاء قاعدة بيانات SQLite في الذاكرة
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # إنشاء جدول اختبار
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test VALUES (1, 'test1'), (2, 'test2')")
    connection.commit()
    
    # إنشاء مدير استعلامات مع المحول
    query_manager = QueryManager(adapter)
    
    # تنفيذ استعلام عبر المدير
    results = query_manager.execute("SELECT * FROM test WHERE id = 1")
    
    # التحقق من النتائج
    assert len(results) == 1
    assert results[0]["id"] == 1
    assert results[0]["name"] == "test1"
```

### اختبارات من طرف إلى طرف

تتحقق اختبارات من طرف إلى طرف من أن النظام الكامل يعمل بشكل صحيح من البداية إلى النهاية.

**الخصائص**:
- الأبطأ في التنفيذ
- تختبر النظام الكامل في بيئة قريبة من الإنتاج
- تستخدم موارد خارجية حقيقية
- تتحقق من سيناريوهات الاستخدام الحقيقية

**مثال**:

```python
def test_mcp_server_end_to_end():
    """اختبار خادم MCP من طرف إلى طرف مع قاعدة بيانات حقيقية."""
    # بدء خادم MCP مع تكوين اختبار
    config_path = "tests/fixtures/test_config.yaml"
    server = MCPServer(config_path)
    server.start()
    
    try:
        # إنشاء عميل MCP محاكي
        client = MockMCPClient()
        
        # تنفيذ استعلام عبر بروتوكول MCP
        response = client.execute_tool("dbutils-list-tables", {"connection": "test-sqlite"})
        
        # التحقق من الاستجابة
        assert "tables" in response
        assert "test" in response["tables"]
        
        # تنفيذ استعلام SQL
        response = client.execute_tool("dbutils-run-query", {
            "connection": "test-sqlite",
            "query": "SELECT * FROM test WHERE id = 1"
        })
        
        # التحقق من النتائج
        assert len(response["results"]) == 1
        assert response["results"][0]["id"] == 1
        assert response["results"][0]["name"] == "test1"
    finally:
        # إيقاف الخادم
        server.stop()
```

### اختبارات الأداء

تتحقق اختبارات الأداء من أن النظام يلبي متطلبات الأداء.

**الخصائص**:
- تقيس وقت التنفيذ، واستخدام الذاكرة، إلخ
- تتحقق من أن النظام يمكنه التعامل مع الحمل المتوقع
- تحدد نقاط الاختناق

**مثال**:

```python
def test_query_performance():
    """اختبار أداء الاستعلامات."""
    # تكوين المحول مع قاعدة بيانات اختبار
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # إنشاء جدول اختبار مع العديد من الصفوف
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    
    # إدراج 10000 صف
    for i in range(10000):
        cursor.execute("INSERT INTO test VALUES (?, ?)", (i, f"test{i}"))
    connection.commit()
    
    # قياس وقت تنفيذ استعلام
    start_time = time.time()
    results = adapter.execute_query("SELECT * FROM test WHERE id < 1000")
    end_time = time.time()
    
    # التحقق من أن الاستعلام ينفذ في أقل من 100 مللي ثانية
    assert end_time - start_time < 0.1
    assert len(results) == 1000
```

### اختبارات الأمان

تتحقق اختبارات الأمان من أن النظام آمن ضد الهجمات.

**الخصائص**:
- تتحقق من أن النظام يقاوم الهجمات المعروفة
- تختبر آليات الأمان
- تحدد الثغرات المحتملة

**مثال**:

```python
def test_sql_injection_prevention():
    """اختبار أن النظام محمي ضد حقن SQL."""
    # تكوين المحول مع قاعدة بيانات اختبار
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # إنشاء جدول اختبار
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'secret')")
    connection.commit()
    
    # إنشاء مدير استعلامات مع المحول
    query_manager = QueryManager(adapter)
    
    # محاولة حقن SQL
    malicious_query = "SELECT * FROM users WHERE username = 'admin' OR 1=1 --'"
    
    # التحقق من أن مدير الاستعلامات يكتشف ويمنع الحقن
    with pytest.raises(SecurityException):
        query_manager.execute(malicious_query)
```

## أدوات الاختبار

### pytest

نستخدم [pytest](https://docs.pytest.org/) كإطار اختبار رئيسي:

```bash
# تثبيت pytest والإضافات
pip install pytest pytest-cov pytest-mock

# تنفيذ جميع الاختبارات
pytest

# تنفيذ اختبارات محددة
pytest tests/unit/
pytest tests/integration/

# تنفيذ مع تغطية الكود
pytest --cov=mcp_dbutils

# إنشاء تقرير تغطية HTML
pytest --cov=mcp_dbutils --cov-report=html
```

### تجهيزات pytest

تسمح تجهيزات pytest بإعداد بيئة الاختبار:

```python
@pytest.fixture
def sqlite_adapter():
    """تجهيزة توفر محول SQLite مكون مع قاعدة بيانات في الذاكرة."""
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # إنشاء جدول اختبار
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test VALUES (1, 'test1'), (2, 'test2')")
    connection.commit()
    
    yield adapter
    
    # التنظيف
    adapter.disconnect()

def test_with_fixture(sqlite_adapter):
    """اختبار محول SQLite باستخدام التجهيزة."""
    results = sqlite_adapter.execute_query("SELECT * FROM test WHERE id = 1")
    assert len(results) == 1
    assert results[0]["id"] == 1
    assert results[0]["name"] == "test1"
```

### المحاكاة

نستخدم `unittest.mock` أو `pytest-mock` للمحاكاة:

```python
def test_with_mock(mocker):
    """اختبار دالة باستخدام المحاكاة."""
    # إنشاء محاكاة لاتصال قاعدة البيانات
    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    
    # تكوين المحاكاة لإرجاع نتائج محددة
    mock_cursor.fetchall.return_value = [("test1",), ("test2",)]
    mock_cursor.description = [("name",)]
    
    # استبدال طريقة الاتصال بالمحاكاة
    mocker.patch("mcp_dbutils.adapters.sqlite.sqlite3.connect", return_value=mock_connection)
    
    # إنشاء المحول
    adapter = SQLiteAdapter({"type": "sqlite", "path": "dummy.db"})
    
    # تنفيذ الاستعلام
    results = adapter.execute_query("SELECT name FROM test")
    
    # التحقق من أن الاستعلام تم تنفيذه بشكل صحيح
    mock_cursor.execute.assert_called_once_with("SELECT name FROM test")
    assert len(results) == 2
    assert results[0]["name"] == "test1"
    assert results[1]["name"] == "test2"
```

### قواعد بيانات الاختبار

لاختبارات التكامل، نستخدم قواعد بيانات حقيقية:

- **SQLite**: قاعدة بيانات في الذاكرة (`:memory:`)
- **PostgreSQL**: نسخة Docker للاختبارات
- **MySQL**: نسخة Docker للاختبارات

```python
@pytest.fixture(scope="session")
def postgres_adapter():
    """تجهيزة توفر محول PostgreSQL مكون مع قاعدة بيانات اختبار."""
    # بدء PostgreSQL مع Docker
    container = start_postgres_container()
    
    # انتظار جاهزية PostgreSQL
    wait_for_postgres(container)
    
    # تكوين المحول
    config = {
        "type": "postgres",
        "host": "localhost",
        "port": container.get_exposed_port(5432),
        "dbname": "testdb",
        "user": "postgres",
        "password": "postgres"
    }
    adapter = PostgreSQLAdapter(config)
    
    # إنشاء جدول اختبار
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id SERIAL PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test (name) VALUES ('test1'), ('test2')")
    connection.commit()
    
    yield adapter
    
    # التنظيف
    adapter.disconnect()
    container.stop()
```

## تنظيم الاختبارات

يتم تنظيم الاختبارات في دليل `tests/`:

```
tests/
├── __init__.py
├── conftest.py              # تجهيزات مشتركة
├── fixtures/                # بيانات اختبار
│   ├── sqlite_schema.sql    # مخطط SQLite للاختبارات
│   ├── postgres_schema.sql  # مخطط PostgreSQL للاختبارات
│   └── mysql_schema.sql     # مخطط MySQL للاختبارات
├── unit/                    # اختبارات الوحدة
│   ├── __init__.py
│   ├── test_adapters.py     # اختبارات المحولات
│   ├── test_config.py       # اختبارات التكوين
│   ├── test_mcp.py          # اختبارات بروتوكول MCP
│   └── test_query.py        # اختبارات معالجة الاستعلامات
├── integration/             # اختبارات التكامل
│   ├── __init__.py
│   ├── test_sqlite.py       # اختبارات تكامل SQLite
│   ├── test_postgres.py     # اختبارات تكامل PostgreSQL
│   └── test_mysql.py        # اختبارات تكامل MySQL
└── e2e/                     # اختبارات من طرف إلى طرف
    ├── __init__.py
    └── test_mcp_server.py   # اختبارات خادم MCP
```

## أفضل الممارسات

### تسمية الاختبارات

اتبع هذه اصطلاحات التسمية:

- ملفات الاختبار تبدأ بـ `test_`
- دوال الاختبار تبدأ بـ `test_`
- أسماء الاختبارات يجب أن تكون وصفية وتشير إلى ما يتم اختباره

```python
# جيد
def test_query_validator_rejects_insert_statements():
    ...

# سيء
def test_validator():
    ...
```

### التأكيدات

استخدم تأكيدات pytest لرسائل خطأ أكثر وضوحًا:

```python
# جيد
assert result == expected, f"توقعت {expected}، حصلت على {result}"

# سيء
if result != expected:
    raise AssertionError("فشل الاختبار")
```

### عزل الاختبارات

يجب أن يكون كل اختبار مستقلاً:

- لا يعتمد على الحالة التي تركتها اختبارات أخرى
- استخدم تجهيزات لإعداد وتنظيف البيئة
- تجنب المتغيرات العالمية أو المشتركة

```python
# جيد
def test_independent_1(sqlite_adapter):
    sqlite_adapter.execute_query("INSERT INTO test VALUES (3, 'test3')")
    results = sqlite_adapter.execute_query("SELECT * FROM test WHERE id = 3")
    assert len(results) == 1

def test_independent_2(sqlite_adapter):
    # هذا الاختبار لا يعتمد على الحالة التي أنشأها test_independent_1
    results = sqlite_adapter.execute_query("SELECT * FROM test WHERE id = 1")
    assert len(results) == 1
```

### اختبارات معلمة

استخدم اختبارات معلمة لاختبار حالات متعددة:

```python
@pytest.mark.parametrize("query,is_valid", [
    ("SELECT * FROM users", True),
    ("INSERT INTO users VALUES (1, 'test')", False),
    ("UPDATE users SET name = 'test' WHERE id = 1", False),
    ("DELETE FROM users WHERE id = 1", False),
    ("DROP TABLE users", False),
])
def test_query_validator_parametrized(query, is_valid):
    """اختبار أن مدقق الاستعلام يحدد بشكل صحيح الاستعلامات غير المصرح بها."""
    validator = QueryValidator()
    assert validator.validate(query) is is_valid
```

### اختبارات الانحدار

أنشئ اختبارات محددة للأخطاء المصححة:

```python
def test_regression_issue_123():
    """اختبار أن الخطأ #123 تم إصلاحه."""
    # الخطأ كان: محول SQLite لا يتعامل بشكل صحيح مع قيم NULL
    config = {"type": "sqlite", "path": ":memory:"}
    adapter = SQLiteAdapter(config)
    
    # إنشاء جدول اختبار
    connection = adapter.connect()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test VALUES (1, NULL)")
    connection.commit()
    
    # التحقق من أن قيم NULL يتم التعامل معها بشكل صحيح
    results = adapter.execute_query("SELECT * FROM test WHERE id = 1")
    assert len(results) == 1
    assert results[0]["id"] == 1
    assert results[0]["name"] is None
```

## التكامل المستمر

يتم تنفيذ الاختبارات تلقائيًا عبر GitHub Actions:

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

## تغطية الكود

نهدف إلى تغطية كود بنسبة 90% على الأقل:

```bash
# تنفيذ الاختبارات مع التغطية
pytest --cov=mcp_dbutils

# إنشاء تقرير تغطية HTML
pytest --cov=mcp_dbutils --cov-report=html
```

تقرير التغطية متاح في دليل `htmlcov/`.

## استكشاف أخطاء الاختبارات وإصلاحها

### اختبارات فاشلة

إذا فشل اختبار:

1. اقرأ رسالة الخطأ بعناية
2. تحقق من التأكيدات التي فشلت
3. استخدم `pytest -v` لمزيد من التفاصيل
4. استخدم `pytest --pdb` للتصحيح التفاعلي

### اختبارات بطيئة

إذا كانت الاختبارات بطيئة:

1. حدد الاختبارات البطيئة باستخدام `pytest --durations=10`
2. استخدم المحاكاة بدلاً من الموارد الحقيقية عندما يكون ذلك ممكنًا
3. حسّن التجهيزات لتقليل وقت الإعداد
4. استخدم `pytest-xdist` لتنفيذ الاختبارات بالتوازي

### اختبارات غير مستقرة (متقلبة)

إذا كانت الاختبارات غير مستقرة (تفشل بشكل عشوائي):

1. حدد الاختبارات غير المستقرة
2. تحقق من التبعيات الخارجية (قواعد البيانات، الشبكة، إلخ)
3. تأكد من أن الاختبارات معزولة
4. استخدم `pytest-rerunfailures` لإعادة تنفيذ الاختبارات الفاشلة

## الخلاصة

الاختبارات ضرورية لضمان جودة وموثوقية MCP Database Utilities. باتباع أفضل الممارسات واستخدام الأدوات المناسبة، يمكننا الحفاظ على مجموعة اختبارات شاملة وفعالة تمنحنا الثقة في الكود الخاص بنا.
