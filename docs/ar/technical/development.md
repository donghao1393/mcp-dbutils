# دليل التطوير

*[English](../../en/technical/development.md) | [中文](../../zh/technical/development.md) | [Français](../../fr/technical/development.md) | [Español](../../es/technical/development.md) | العربية | [Русский](../../ru/technical/development.md)*

يوفر هذا المستند معلومات مفصلة حول عملية التطوير، ومعايير الكود، وأفضل الممارسات للمساهمة في مشروع MCP Database Utilities.

## إعداد بيئة التطوير

### المتطلبات الأساسية

- Python 3.10 أو أحدث
- Git
- محرر كود أو بيئة تطوير متكاملة (VS Code، PyCharm، إلخ)
- Docker (اختياري، للاختبار مع قواعد بيانات مختلفة)

### التثبيت للتطوير

1. **استنساخ المستودع**

```bash
git clone https://github.com/donghao1393/mcp-dbutils.git
cd mcp-dbutils
```

2. **إنشاء بيئة افتراضية**

```bash
# باستخدام venv
python -m venv venv
source venv/bin/activate  # على Linux/macOS
# أو
.\venv\Scripts\activate  # على Windows

# باستخدام uv (موصى به)
uv venv
source .venv/bin/activate  # على Linux/macOS
# أو
.\.venv\Scripts\activate  # على Windows
```

3. **تثبيت تبعيات التطوير**

```bash
# باستخدام pip
pip install -e ".[dev,test,docs]"

# باستخدام uv (موصى به)
uv pip install -e ".[dev,test,docs]"
```

4. **إعداد خطافات ما قبل الالتزام**

```bash
pre-commit install
```

### قواعد البيانات للتطوير

للتطوير والاختبار محليًا، يمكنك استخدام Docker لتشغيل قواعد بيانات مختلفة:

#### SQLite

لا يتطلب SQLite إعدادًا خاصًا، فقط تحتاج إلى إنشاء ملف قاعدة بيانات:

```bash
# إنشاء قاعدة بيانات SQLite للاختبار
sqlite3 test.db < tests/fixtures/sqlite_schema.sql
```

#### PostgreSQL

```bash
# بدء PostgreSQL باستخدام Docker
docker run --name postgres-dev -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -p 5432:5432 -d postgres:14

# إنشاء قاعدة بيانات اختبار
docker exec -i postgres-dev psql -U postgres -c "CREATE DATABASE testdb;"
docker exec -i postgres-dev psql -U postgres -d testdb < tests/fixtures/postgres_schema.sql
```

#### MySQL

```bash
# بدء MySQL باستخدام Docker
docker run --name mysql-dev -e MYSQL_ROOT_PASSWORD=mysql -e MYSQL_DATABASE=testdb -p 3306:3306 -d mysql:8

# انتظار بدء MySQL
sleep 20

# تحميل مخطط الاختبار
docker exec -i mysql-dev mysql -uroot -pmysql testdb < tests/fixtures/mysql_schema.sql
```

## هيكل المشروع

```
mcp-dbutils/
├── .github/                    # تكوينات GitHub Actions
├── docs/                       # التوثيق
│   ├── en/                     # التوثيق بالإنجليزية
│   ├── zh/                     # التوثيق بالصينية
│   ├── fr/                     # التوثيق بالفرنسية
│   ├── es/                     # التوثيق بالإسبانية
│   ├── ar/                     # التوثيق بالعربية
│   └── ru/                     # التوثيق بالروسية
├── mcp_dbutils/                # الكود المصدري الرئيسي
│   ├── __init__.py             # تهيئة الحزمة
│   ├── __main__.py             # نقطة الدخول للتنفيذ المباشر
│   ├── adapters/               # محولات قاعدة البيانات
│   │   ├── __init__.py
│   │   ├── base.py             # الفئة الأساسية للمحولات
│   │   ├── sqlite.py           # محول SQLite
│   │   ├── postgres.py         # محول PostgreSQL
│   │   └── mysql.py            # محول MySQL
│   ├── config/                 # إدارة التكوين
│   │   ├── __init__.py
│   │   └── loader.py           # محمل التكوين
│   ├── mcp/                    # تنفيذ بروتوكول MCP
│   │   ├── __init__.py
│   │   ├── server.py           # خادم MCP
│   │   └── tools.py            # أدوات MCP
│   ├── query/                  # معالجة الاستعلامات
│   │   ├── __init__.py
│   │   ├── parser.py           # محلل الاستعلامات
│   │   └── validator.py        # مدقق الاستعلامات
│   └── utils/                  # أدوات مساعدة
│       ├── __init__.py
│       ├── logging.py          # تكوين التسجيل
│       └── security.py         # أدوات مساعدة للأمان
├── tests/                      # الاختبارات
│   ├── __init__.py
│   ├── conftest.py             # تكوين pytest
│   ├── fixtures/               # تجهيزات للاختبارات
│   ├── unit/                   # اختبارات الوحدة
│   └── integration/            # اختبارات التكامل
├── .gitignore                  # ملفات لتجاهلها من قبل Git
├── .pre-commit-config.yaml     # تكوين pre-commit
├── LICENSE                     # ترخيص المشروع
├── pyproject.toml              # تكوين مشروع Python
├── README.md                   # التوثيق الرئيسي
└── README_*.md                 # التوثيق بلغات أخرى
```

## معايير الكود

### نمط الكود

نتبع [PEP 8](https://peps.python.org/pep-0008/) مع بعض التعديلات:

- الحد الأقصى لطول السطر: 100 حرف
- استخدام علامات الاقتباس المزدوجة للسلاسل النصية
- استخدام f-strings لتنسيق السلاسل

### التنسيق التلقائي

نستخدم الأدوات التالية للتنسيق التلقائي:

- **Black**: لتنسيق الكود
- **isort**: لترتيب الاستيرادات
- **Ruff**: للتدقيق والتحقق من الكود

هذه الأدوات مكونة في `pyproject.toml` وتنفذ تلقائيًا عبر pre-commit.

### توثيق الكود

نستخدم تنسيق Google لتوثيق الكود:

```python
def function_with_types_in_docstring(param1, param2):
    """مثال على دالة مع توثيق الأنواع.

    Args:
        param1 (int): المعلمة الأولى.
        param2 (str): المعلمة الثانية.

    Returns:
        bool: قيمة الإرجاع. True للنجاح، False خلاف ذلك.

    Raises:
        ValueError: إذا كانت param1 سالبة.
        TypeError: إذا لم تكن param2 سلسلة نصية.
    """
    if param1 < 0:
        raise ValueError("يجب أن تكون param1 موجبة.")
    if not isinstance(param2, str):
        raise TypeError("يجب أن تكون param2 سلسلة نصية.")
    return True
```

### اصطلاحات التسمية

- **الفئات**: PascalCase (مثال: `DatabaseAdapter`)
- **الدوال والطرق**: snake_case (مثال: `connect_to_database`)
- **المتغيرات**: snake_case (مثال: `connection_pool`)
- **الثوابت**: UPPER_SNAKE_CASE (مثال: `MAX_CONNECTIONS`)
- **الوحدات**: snake_case (مثال: `database_adapter.py`)
- **الحزم**: snake_case (مثال: `mcp_dbutils`)

### الاستيرادات

نظم الاستيرادات بالترتيب التالي:

1. استيرادات من المكتبة القياسية
2. استيرادات من مكتبات خارجية
3. استيرادات من المشروع

استخدم isort لترتيب الاستيرادات تلقائيًا.

## عملية التطوير

### سير عمل Git

نتبع سير عمل قائم على الميزات:

1. أنشئ فرعًا من `main` لكل ميزة أو إصلاح
2. سمِّ الفرع وفقًا للتنسيق: `feature/اسم-الميزة` أو `fix/اسم-الإصلاح`
3. قم بالتزامات منتظمة مع رسائل واضحة
4. قدم طلب سحب إلى `main` عندما تكون الميزة جاهزة

### رسائل الالتزام

نتبع تنسيق [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

الأنواع الشائعة:
- `feat`: ميزة جديدة
- `fix`: إصلاح خلل
- `docs`: تغييرات في التوثيق
- `style`: تنسيق، فاصلة منقوطة مفقودة، إلخ (بدون تغيير في الكود)
- `refactor`: إعادة هيكلة الكود
- `test`: إضافة أو إصلاح اختبارات
- `chore`: مهام صيانة، تحديثات التبعيات، إلخ

أمثلة:
```
feat(sqlite): إضافة دعم للاستعلامات المعلمة
fix(postgres): إصلاح إدارة مهل اتصال
docs: تحديث توثيق التثبيت
```

### طلبات السحب

- أنشئ طلب سحب (PR) لكل ميزة أو إصلاح
- تأكد من نجاح جميع الاختبارات
- تأكد من تنسيق الكود بشكل صحيح
- اطلب مراجعة الكود من مطور آخر على الأقل
- حل جميع التعليقات قبل الدمج

### مراجعة الكود

عند مراجعة الكود، تحقق من:

1. **الوظيفة**: هل يفعل الكود ما يفترض به أن يفعل؟
2. **الجودة**: هل الكود مكتوب جيدًا، وقابل للقراءة، وقابل للصيانة؟
3. **الاختبارات**: هل هناك اختبارات مناسبة؟
4. **التوثيق**: هل التوثيق محدث؟
5. **الأمان**: هل هناك مشاكل أمنية محتملة؟

## الاختبارات

### أنواع الاختبارات

- **اختبارات الوحدة**: تختبر دوال أو فئات فردية
- **اختبارات التكامل**: تختبر التفاعل بين عدة مكونات
- **اختبارات من طرف إلى طرف**: تختبر النظام الكامل

### تنفيذ الاختبارات

```bash
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

### كتابة الاختبارات

استخدم pytest لكتابة الاختبارات:

```python
def test_connection_success():
    """اختبار نجاح الاتصال بقاعدة البيانات مع معلمات صالحة."""
    config = {
        "type": "sqlite",
        "path": ":memory:"
    }
    adapter = SQLiteAdapter(config)
    connection = adapter.connect()
    assert connection is not None
    adapter.disconnect()

def test_connection_failure():
    """اختبار فشل الاتصال مع معلمات غير صالحة."""
    config = {
        "type": "sqlite",
        "path": "/nonexistent/path/to/db.sqlite"
    }
    adapter = SQLiteAdapter(config)
    with pytest.raises(ConnectionError):
        adapter.connect()
```

### المحاكاة

استخدم `unittest.mock` أو `pytest-mock` للمحاكاة:

```python
def test_query_execution(mocker):
    """اختبار تنفيذ الاستعلام مع محاكاة الاتصال."""
    # إنشاء محاكاة للاتصال
    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    
    # تكوين المحاكاة لإرجاع نتائج محددة
    mock_cursor.fetchall.return_value = [("row1",), ("row2",)]
    mock_cursor.description = [("column1",)]
    
    # حقن المحاكاة في المحول
    adapter = SQLiteAdapter({"type": "sqlite", "path": ":memory:"})
    adapter._connection = mock_connection
    
    # تنفيذ الاستعلام
    results = adapter.execute_query("SELECT * FROM test")
    
    # التحقق من تنفيذ الاستعلام بشكل صحيح
    mock_cursor.execute.assert_called_once_with("SELECT * FROM test")
    assert len(results) == 2
    assert results[0][0] == "row1"
    assert results[1][0] == "row2"
```

## التوثيق

### توثيق الكود

- وثق جميع الفئات والطرق والدوال العامة
- استخدم تنسيق توثيق Google
- أدرج أمثلة على الاستخدام عندما يكون ذلك ملائمًا

### توثيق المشروع

- حافظ على تحديث README.md بالمعلومات الأساسية
- وثق الميزات في دليل `docs/`
- قدم أمثلة على الاستخدام

### إنشاء التوثيق

نستخدم MkDocs لإنشاء التوثيق:

```bash
# تثبيت MkDocs والتبعيات
pip install mkdocs mkdocs-material

# إنشاء التوثيق
mkdocs build

# خدمة التوثيق محليًا
mkdocs serve
```

## الإصدار والنشر

### الإصدار الدلالي

نتبع [الإصدار الدلالي](https://semver.org/):

- **MAJOR**: تغييرات غير متوافقة مع الإصدارات السابقة
- **MINOR**: إضافات ميزات متوافقة مع الإصدارات السابقة
- **PATCH**: إصلاحات أخطاء متوافقة مع الإصدارات السابقة

### عملية النشر

1. قم بتحديث الإصدار في `pyproject.toml`
2. قم بتحديث CHANGELOG.md
3. أنشئ علامة Git بالإصدار الجديد
4. ادفع العلامة إلى GitHub
5. ستقوم GitHub Actions تلقائيًا ببناء ونشر الحزمة على PyPI

```bash
# مثال على عملية النشر
# 1. تحديث الإصدار في pyproject.toml
# 2. تحديث CHANGELOG.md
# 3. التزام التغييرات
git add pyproject.toml CHANGELOG.md
git commit -m "chore: تحضير الإصدار 1.2.3"

# 4. إنشاء ودفع العلامة
git tag v1.2.3
git push origin main v1.2.3
```

## التكامل المستمر

نستخدم GitHub Actions للتكامل المستمر:

- **Lint**: يتحقق من نمط الكود
- **Test**: ينفذ الاختبارات على إصدارات مختلفة من Python وأنظمة تشغيل
- **Build**: يبني الحزمة
- **Publish**: ينشر الحزمة على PyPI (فقط للعلامات)

تم تعريف سير العمل في دليل `.github/workflows/`.

## موارد إضافية

- [توثيق Python](https://docs.python.org/)
- [PEP 8 -- دليل النمط لكود Python](https://peps.python.org/pep-0008/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [توثيق pytest](https://docs.pytest.org/)
- [توثيق Black](https://black.readthedocs.io/)
- [توثيق isort](https://pycqa.github.io/isort/)
- [توثيق Ruff](https://beta.ruff.rs/docs/)
- [توثيق pre-commit](https://pre-commit.com/)
