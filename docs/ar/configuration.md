<div dir="rtl">

# دليل التكوين

*[English](../en/configuration.md) | [中文](../zh/configuration.md) | [Français](../fr/configuration.md) | [Español](../es/configuration.md) | العربية | [Русский](../ru/configuration.md)*

يقدم هذا المستند أمثلة تكوين متنوعة لـ MCP Database Utilities، من التكوينات الأساسية إلى السيناريوهات المتقدمة، مما يساعدك على تكوين وتحسين اتصالات قاعدة البيانات الخاصة بك بشكل صحيح.

## التكوين الأساسي

### التكوين الأساسي لـ SQLite

SQLite هي قاعدة بيانات خفيفة قائمة على الملفات مع تكوين بسيط جدًا:

```yaml
connections:
  my-sqlite:
    type: sqlite
    path: /path/to/database.db
    # اختياري: كلمة مرور تشفير قاعدة البيانات
    password: optional_encryption_password
```

### التكوين الأساسي لـ PostgreSQL

تكوين اتصال PostgreSQL القياسي:

```yaml
connections:
  my-postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: my_database
    user: postgres_user
    password: postgres_password
```

### التكوين الأساسي لـ MySQL

تكوين اتصال MySQL القياسي:

```yaml
connections:
  my-mysql:
    type: mysql
    host: localhost
    port: 3306
    database: my_database
    user: mysql_user
    password: mysql_password
    charset: utf8mb4  # موصى به لدعم Unicode الكامل
```

## تكوين قواعد بيانات متعددة

يمكنك تحديد اتصالات قاعدة بيانات متعددة في نفس ملف التكوين:

```yaml
connections:
  # قاعدة بيانات SQLite للتطوير
  dev-db:
    type: sqlite
    path: /path/to/dev.db

  # قاعدة بيانات PostgreSQL للاختبار
  test-db:
    type: postgres
    host: test-postgres.example.com
    port: 5432
    dbname: test_db
    user: test_user
    password: test_pass

  # قاعدة بيانات MySQL للإنتاج
  prod-db:
    type: mysql
    host: prod-mysql.example.com
    port: 3306
    database: prod_db
    user: prod_user
    password: prod_pass
    charset: utf8mb4
```

## التكوين المتقدم

### تكوين نمط URL

بالإضافة إلى استخدام خصائص التكوين القياسية، يمكنك أيضًا استخدام عناوين URL لقاعدة البيانات للتكوين الجزئي. أفضل ممارسة هي وضع بنية اتصال قاعدة البيانات في عنوان URL، ولكن الاحتفاظ بالمعلومات الحساسة والمعلمات المحددة منفصلة:

**تكوين URL لـ PostgreSQL (النهج الموصى به)**:

```yaml
connections:
  # استخدام URL لـ PostgreSQL (أفضل ممارسة)
  postgres-url:
    type: postgres
    url: postgresql://host:5432/dbname
    user: postgres_user
    password: postgres_password
    # معلمات أخرى مكونة هنا
```

**تكوين URL لـ MySQL (النهج الموصى به)**:

```yaml
connections:
  # استخدام URL لـ MySQL (أفضل ممارسة)
  mysql-url:
    type: mysql
    url: mysql://host:3306/dbname
    user: mysql_user
    password: mysql_password
    charset: utf8mb4
```

**نمط تكوين URL القديم** (غير موصى به للإنتاج):

على الرغم من أن النهج التالي يعمل، إلا أنه غير موصى به لبيئات الإنتاج بسبب خطر أخطاء تحليل الأحرف الخاصة:

```yaml
connections:
  legacy-url:
    type: postgres
    url: postgresql://user:password@host:5432/dbname?param1=value1
    # ملاحظة: لا يُنصح بتضمين بيانات الاعتماد في عنوان URL
```

**متى تستخدم URL مقابل التكوين القياسي**:
- تكوين URL مناسب لـ:
  - عندما يكون لديك بالفعل سلسلة اتصال قاعدة بيانات
  - تحتاج إلى تضمين معلمات اتصال محددة في عنوان URL
  - الترحيل من أنظمة أخرى ذات سلاسل اتصال
- التكوين القياسي مناسب لـ:
  - بنية تكوين أكثر وضوحًا
  - الحاجة إلى إدارة كل خاصية تكوين بشكل منفصل
  - أسهل لتعديل المعلمات الفردية دون التأثير على الاتصال العام
  - أمان وقابلية للصيانة أفضل

في جميع الحالات، يجب تجنب تضمين المعلومات الحساسة (مثل أسماء المستخدمين وكلمات المرور) في عنوان URL وبدلاً من ذلك توفيرها بشكل منفصل في معلمات التكوين.

### اتصالات SSL/TLS الآمنة

#### تكوين SSL لـ PostgreSQL

**استخدام معلمات URL لـ SSL**:

```yaml
connections:
  pg-ssl-url:
    type: postgres
    url: postgresql://postgres.example.com:5432/secure_db?sslmode=verify-full&sslcert=/path/to/cert.pem&sslkey=/path/to/key.pem&sslrootcert=/path/to/root.crt
    user: secure_user
    password: secure_pass
```

**استخدام قسم تكوين SSL مخصص**:

```yaml
connections:
  pg-ssl-full:
    type: postgres
    host: secure-postgres.example.com
    port: 5432
    dbname: secure_db
    user: secure_user
    password: secure_pass
    ssl:
      mode: verify-full  # وضع التحقق الأكثر أمانًا
      cert: /path/to/client-cert.pem  # شهادة العميل
      key: /path/to/client-key.pem    # مفتاح العميل الخاص
      root: /path/to/root.crt         # شهادة CA
```

**شرح وضع SSL لـ PostgreSQL**:
- `disable`: لا يتم استخدام SSL على الإطلاق (غير موصى به للإنتاج)
- `require`: استخدام SSL ولكن عدم التحقق من الشهادة (التشفير فقط، بدون مصادقة)
- `verify-ca`: التحقق من أن شهادة الخادم موقعة من قبل CA موثوق بها
- `verify-full`: التحقق من شهادة الخادم وتطابق اسم المضيف (الخيار الأكثر أمانًا)

#### تكوين SSL لـ MySQL

**استخدام معلمات URL لـ SSL**:

```yaml
connections:
  mysql-ssl-url:
    type: mysql
    url: mysql://mysql.example.com:3306/secure_db?ssl-mode=verify_identity&ssl-ca=/path/to/ca.pem&ssl-cert=/path/to/client-cert.pem&ssl-key=/path/to/client-key.pem
    user: secure_user
    password: secure_pass
```

**استخدام قسم تكوين SSL مخصص**:

```yaml
connections:
  mysql-ssl-full:
    type: mysql
    host: secure-mysql.example.com
    port: 3306
    database: secure_db
    user: secure_user
    password: secure_pass
    charset: utf8mb4
    ssl:
      mode: verify_identity  # وضع التحقق الأكثر أمانًا
      ca: /path/to/ca.pem         # شهادة CA
      cert: /path/to/client-cert.pem  # شهادة العميل
      key: /path/to/client-key.pem    # مفتاح العميل الخاص
```

**شرح وضع SSL لـ MySQL**:
- `disabled`: لا يتم استخدام SSL (غير موصى به للإنتاج)
- `preferred`: استخدام SSL إذا كان متاحًا، وإلا استخدام اتصال غير مشفر
- `required`: يجب استخدام SSL، ولكن عدم التحقق من شهادة الخادم
- `verify_ca`: التحقق من أن شهادة الخادم موقعة من قبل CA موثوق بها
- `verify_identity`: التحقق من شهادة الخادم وتطابق اسم المضيف (الخيار الأكثر أمانًا)

### التكوين المتقدم لـ SQLite

**استخدام معلمات URI**:

```yaml
connections:
  sqlite-advanced:
    type: sqlite
    path: /path/to/db.sqlite?mode=ro&cache=shared&immutable=1
```

**معلمات URI الشائعة لـ SQLite**:
- `mode=ro`: وضع القراءة فقط (خيار آمن)
- `cache=shared`: وضع ذاكرة التخزين المؤقت المشتركة، يحسن أداء متعدد المؤشرات
- `immutable=1`: تمييز قاعدة البيانات على أنها غير قابلة للتغيير، يحسن الأداء
- `nolock=1`: تعطيل قفل الملف (استخدم فقط عندما تكون متأكدًا من عدم وجود اتصالات أخرى)

## تكوين خاص لبيئة Docker

عند التشغيل في حاوية Docker، يتطلب الاتصال بقواعد البيانات على المضيف تكوينًا خاصًا:

### الاتصال بـ PostgreSQL/MySQL على المضيف

**على macOS/Windows**:
استخدم اسم المضيف الخاص `host.docker.internal` للوصول إلى مضيف Docker:

```yaml
connections:
  docker-postgres:
    type: postgres
    host: host.docker.internal  # اسم DNS خاص يشير إلى مضيف Docker
    port: 5432
    dbname: my_database
    user: postgres_user
    password: postgres_password
```

**على Linux**:
استخدم IP جسر Docker أو استخدم وضع شبكة المضيف:

```yaml
connections:
  docker-mysql:
    type: mysql
    host: 172.17.0.1  # IP جسر Docker الافتراضي، يشير إلى المضيف
    port: 3306
    database: my_database
    user: mysql_user
    password: mysql_password
```

أو استخدم `--network="host"` عند بدء حاوية Docker، ثم استخدم `localhost` كاسم المضيف.

### تعيين SQLite

بالنسبة لـ SQLite، تحتاج إلى تعيين ملف قاعدة البيانات في الحاوية:

```bash
docker run -i --rm \
  -v /path/to/config.yaml:/app/config.yaml \
  -v /path/to/database.db:/app/database.db \
  mcp/dbutils --config /app/config.yaml
```

ثم أشر إلى المسار المعين في التكوين الخاص بك:

```yaml
connections:
  docker-sqlite:
    type: sqlite
    path: /app/database.db  # المسار داخل الحاوية، وليس مسار المضيف
```

## سيناريوهات التكوين الشائعة

### إدارة البيئات المتعددة

ممارسة جيدة هي استخدام اصطلاحات تسمية واضحة للبيئات المختلفة:

```yaml
connections:
  # بيئة التطوير
  dev-postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: dev_db
    user: dev_user
    password: dev_pass

  # بيئة الاختبار
  test-postgres:
    type: postgres
    host: test-server.example.com
    port: 5432
    dbname: test_db
    user: test_user
    password: test_pass

  # بيئة الإنتاج
  prod-postgres:
    type: postgres
    host: prod-db.example.com
    port: 5432
    dbname: prod_db
    user: prod_user
    password: prod_pass
    ssl:
      mode: verify-full
      cert: /path/to/cert.pem
      key: /path/to/key.pem
      root: /path/to/root.crt
```

### تكوين محدد للقراءة فقط والتحليلات

بالنسبة لسيناريوهات تحليل البيانات، يوصى باستخدام حسابات للقراءة فقط وتكوين محسن:

```yaml
connections:
  analytics-mysql:
    type: mysql
    host: analytics-db.example.com
    port: 3306
    database: analytics
    user: analytics_readonly  # استخدام حساب بأذونات قراءة فقط
    password: readonly_pass
    charset: utf8mb4
    # تعيين مهلة أطول مناسبة لتحليل البيانات
```

## نصائح استكشاف الأخطاء وإصلاحها

إذا كان تكوين الاتصال الخاص بك لا يعمل، جرب:

1. **التحقق من الاتصال الأساسي**: استخدم عميل قاعدة البيانات الأصلي للتحقق من أن الاتصال يعمل
2. **التحقق من اتصال الشبكة**: تأكد من فتح منافذ الشبكة، وأن جدران الحماية تسمح بالوصول
3. **التحقق من بيانات الاعتماد**: تأكد من صحة اسم المستخدم وكلمة المرور
4. **مشاكل المسار**: بالنسبة لـ SQLite، تأكد من وجود المسار ولديه أذونات قراءة
5. **أخطاء SSL**: تحقق من مسارات وأذونات الشهادات، تحقق من أن الشهادات غير منتهية الصلاحية

</div>
