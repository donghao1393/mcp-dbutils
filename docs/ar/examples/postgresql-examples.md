# أمثلة PostgreSQL

*[English](../../en/examples/postgresql-examples.md) | [中文](../../zh/examples/postgresql-examples.md) | [Français](../../fr/examples/postgresql-examples.md) | [Español](../../es/examples/postgresql-examples.md) | العربية | [Русский](../../ru/examples/postgresql-examples.md)*

يقدم هذا المستند أمثلة عملية للعمل مع قواعد بيانات PostgreSQL باستخدام MCP Database Utilities.

## التكوين الأساسي

```yaml
connections:
  my-postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: my_database
    user: postgres_user
    password: postgres_password
    # خيارات إضافية
    sslmode: prefer  # الخيارات: disable, allow, prefer, require, verify-ca, verify-full
```

## العمليات الشائعة

### سرد المخططات

**أنت**: "اعرض جميع المخططات في قاعدة بيانات PostgreSQL الخاصة بي."

**الذكاء الاصطناعي**: "إليك المخططات في قاعدة بيانات PostgreSQL الخاصة بك:
- public
- analytics
- auth
- reporting
- audit"

### سرد الجداول

**أنت**: "اعرض جميع الجداول في المخطط public."

**الذكاء الاصطناعي**: "إليك الجداول في المخطط public:
- users
- products
- orders
- categories
- suppliers
- inventory"

### عرض بنية الجدول

**أنت**: "أظهر لي بنية جدول users."

**الذكاء الاصطناعي**: "جدول users له البنية التالية:
- id (SERIAL, PRIMARY KEY)
- name (VARCHAR(100), NOT NULL)
- email (VARCHAR(100), NOT NULL, UNIQUE)
- created_at (TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT NOW())
- last_login (TIMESTAMP WITH TIME ZONE)
- status (VARCHAR(20), DEFAULT 'active')
- metadata (JSONB)
- role_id (INTEGER, REFERENCES roles(id))"

### استعلام أساسي

**أنت**: "أظهر لي آخر 5 مستخدمين مسجلين."

**الذكاء الاصطناعي**: "إليك آخر 5 مستخدمين مسجلين:

| id | name | email | created_at |
|----|------|-------|------------|
| 42 | محمد أحمد | mohammed@example.com | 2023-11-25 14:32:15+01 |
| 41 | فاطمة علي | fatima@example.com | 2023-11-24 09:45:22+01 |
| 40 | أحمد محمود | ahmed@example.com | 2023-11-23 18:12:05+01 |
| 39 | سارة حسن | sara@example.com | 2023-11-22 11:30:47+01 |
| 38 | عمر خالد | omar@example.com | 2023-11-21 16:08:33+01 |"

## استعلامات متقدمة

### ربط الجداول

**أنت**: "أظهر لي آخر 3 طلبات مع معلومات العميل والمنتج."

**الذكاء الاصطناعي**: "إليك آخر 3 طلبات مع معلومات العميل والمنتج:

| order_id | order_date | customer_name | customer_email | product_name | price | quantity |
|----------|------------|---------------|----------------|--------------|-------|----------|
| 1042 | 2023-11-25 | محمد أحمد | mohammed@example.com | هاتف ذكي برو | 899.99 | 1 |
| 1041 | 2023-11-24 | سارة حسن | sara@example.com | سماعات لاسلكية | 129.50 | 2 |
| 1040 | 2023-11-23 | أحمد محمود | ahmed@example.com | حاسوب محمول | 1299.00 | 1 |"

### دوال التجميع

**أنت**: "ما هو إجمالي المبيعات حسب فئة المنتج لهذا الشهر؟"

**الذكاء الاصطناعي**: "إليك إجمالي المبيعات حسب فئة المنتج لهذا الشهر:

| category | total_sales |
|----------|-------------|
| إلكترونيات | 28,456.75 |
| ملابس | 12,389.30 |
| منزل وحديقة | 9,876.50 |
| رياضة وترفيه | 7,654.25 |
| كتب ووسائط | 3,210.80 |"

### استخدام التعبيرات الجدولية المشتركة (CTE)

**أنت**: "استخدم CTE للعثور على العملاء الذين أنفقوا أكثر من المتوسط هذا الشهر."

**الذكاء الاصطناعي**: "إليك العملاء الذين أنفقوا أكثر من المتوسط هذا الشهر، باستخدام CTE:

| customer_id | name | email | total_spent | global_average |
|-------------|------|-------|-------------|----------------|
| 23 | فاطمة علي | fatima@example.com | 1,456.78 | 345.67 |
| 42 | محمد أحمد | mohammed@example.com | 1,245.50 | 345.67 |
| 15 | عمر خالد | omar@example.com | 987.25 | 345.67 |
| 31 | سارة حسن | sara@example.com | 876.30 | 345.67 |
| 8 | أحمد محمود | ahmed@example.com | 654.90 | 345.67 |

هذا الاستعلام يستخدم CTE لحساب متوسط الإنفاق أولاً، ثم يجد العملاء الذين يتجاوز إنفاقهم هذا المتوسط."

### استخدام دوال النافذة (Window Functions)

**أنت**: "أظهر لي ترتيب المنتجات الأكثر مبيعًا حسب الفئة."

**الذكاء الاصطناعي**: "إليك ترتيب المنتجات الأكثر مبيعًا حسب الفئة:

| category | product_name | quantity_sold | rank_in_category |
|----------|--------------|---------------|------------------|
| إلكترونيات | هاتف ذكي برو | 1245 | 1 |
| إلكترونيات | سماعات لاسلكية | 987 | 2 |
| إلكترونيات | تابلت ألترا | 876 | 3 |
| ملابس | تي شيرت بريميوم | 543 | 1 |
| ملابس | جينز كلاسيك | 432 | 2 |
| ملابس | أحذية رياضية | 321 | 3 |
| منزل وحديقة | ماكينة قهوة أوتوماتيكية | 234 | 1 |
| منزل وحديقة | طقم مطبخ | 210 | 2 |
| منزل وحديقة | مصباح تصميم | 198 | 3 |

هذا الاستعلام يستخدم دالة النافذة ROW_NUMBER() لترتيب المنتجات حسب الكمية المباعة داخل كل فئة."

## تحليل الأداء

### خطة تنفيذ الاستعلام

**أنت**: "اشرح خطة تنفيذ الاستعلام: SELECT * FROM orders JOIN customers ON orders.customer_id = customers.id WHERE orders.date > '2023-01-01'"

**الذكاء الاصطناعي**: "خطة تنفيذ الاستعلام:
```
                                                   QUERY PLAN
-----------------------------------------------------------------------------------------------------------------
 Hash Join  (cost=33.38..1756.15 rows=1250 width=172)
   Hash Cond: (orders.customer_id = customers.id)
   ->  Seq Scan on orders  (cost=0.00..1250.50 rows=1250 width=96)
         Filter: (date > '2023-01-01'::date)
   ->  Hash  (cost=18.50..18.50 rows=1150 width=76)
         ->  Seq Scan on customers  (cost=0.00..18.50 rows=1150 width=76)
```

التحليل:
1. يتم إجراء مسح تسلسلي على جدول 'orders' مع تصفية على التاريخ
2. يتم إجراء مسح تسلسلي على جدول 'customers'
3. يتم استخدام ربط تجزئة لدمج النتائج

توصيات التحسين:
- إضافة فهرس على orders.date لتجنب المسح التسلسلي
- التحقق مما إذا كان هناك فهرس موجود بالفعل على customers.id (المفتاح الأساسي)"

### إحصائيات الجدول

**أنت**: "احصل على إحصائيات لجدول orders."

**الذكاء الاصطناعي**: "إحصائيات لجدول orders:
- العدد المقدر للصفوف: 15,423
- حجم الجدول: 4.2 ميجابايت
- حجم الفهارس: 3.1 ميجابايت
- معدل إصابة ذاكرة التخزين المؤقت: 98.5%
- آخر VACUUM: 2023-11-20 08:15:32
- آخر ANALYZE: 2023-11-20 08:15:32
- التضخم المقدر: 3.2%
- الفهارس:
  * orders_pkey (id): 1.1 ميجابايت
  * idx_orders_customer_id (customer_id): 0.8 ميجابايت
  * idx_orders_date (date): 0.7 ميجابايت
  * idx_orders_status (status): 0.5 ميجابايت"

## ميزات خاصة بـ PostgreSQL

### استخدام أنواع بيانات JSON/JSONB

**أنت**: "أظهر لي المستخدمين ذوي تفضيلات محددة في حقل metadata الخاص بهم."

**الذكاء الاصطناعي**: "إليك المستخدمين ذوي تفضيلات محددة في حقل metadata JSONB الخاص بهم:

| id | name | email | preferences |
|----|------|-------|-------------|
| 42 | محمد أحمد | mohammed@example.com | {\"theme\": \"dark\", \"notifications\": true, \"language\": \"ar\"} |
| 23 | فاطمة علي | fatima@example.com | {\"theme\": \"light\", \"notifications\": false, \"language\": \"ar\"} |
| 15 | عمر خالد | omar@example.com | {\"theme\": \"auto\", \"notifications\": true, \"language\": \"en\"} |

هذا الاستعلام يستخدم المشغل -> للوصول إلى خصائص JSONB وتصفية النتائج بناءً على تفضيلات المستخدمين."

### استخدام الأنواع الهندسية

**أنت**: "ابحث عن المتاجر في نطاق 5 كم حول نقطة معينة."

**الذكاء الاصطناعي**: "إليك المتاجر في نطاق 5 كم حول النقطة (31.2357, 30.0444) (إحداثيات القاهرة):

| id | name | address | distance_km |
|----|------|---------|-------------|
| 12 | متجر وسط المدينة | 15 شارع قصر النيل، القاهرة | 0.8 |
| 8 | متجر المعادي | 25 شارع 9، المعادي، القاهرة | 1.2 |
| 15 | متجر مدينة نصر | 7 شارع مكرم عبيد، مدينة نصر، القاهرة | 2.5 |
| 23 | متجر الشيخ زايد | 4 محور المركزي، الشيخ زايد | 4.7 |

هذا الاستعلام يستخدم نوع البيانات POINT ودالة ST_Distance لحساب المسافة بين المواقع."

### استخدام العروض المادية (Materialized Views)

**أنت**: "ما هي المعلومات المتاحة في العرض المادي 'monthly_sales_report'؟"

**الذكاء الاصطناعي**: "العرض المادي 'monthly_sales_report' يحتوي على البيانات التالية:

| year | month | category | total_sales | order_count | average_basket |
|------|-------|----------|-------------|-------------|----------------|
| 2023 | 11 | إلكترونيات | 125,456.78 | 1245 | 100.77 |
| 2023 | 11 | ملابس | 87,654.32 | 1876 | 46.72 |
| 2023 | 11 | منزل وحديقة | 65,432.10 | 876 | 74.69 |
| 2023 | 10 | إلكترونيات | 115,678.90 | 1156 | 100.07 |
| 2023 | 10 | ملابس | 76,543.21 | 1654 | 46.28 |
| 2023 | 10 | منزل وحديقة | 54,321.09 | 765 | 71.01 |

هذا العرض المادي يتم تحديثه يوميًا ويوفر ملخصًا مجمعًا مسبقًا للمبيعات حسب الشهر والفئة."

### استخدام الامتدادات

**أنت**: "ما هي امتدادات PostgreSQL المثبتة في قاعدة البيانات؟"

**الذكاء الاصطناعي**: "الامتدادات التالية مثبتة في قاعدة البيانات:

1. **pg_stat_statements**
   - يوفر إحصائيات تنفيذ لجميع عبارات SQL المنفذة

2. **PostGIS**
   - يضيف دعمًا للكائنات الجغرافية مما يتيح استعلامات الموقع

3. **pgcrypto**
   - يوفر وظائف تشفير

4. **uuid-ossp**
   - يوفر وظائف لإنشاء UUIDs

5. **pg_trgm**
   - يوفر وظائف ومشغلات لتحديد تشابه النص بناءً على مطابقة ثلاثية الأحرف

6. **hstore**
   - يوفر نوع بيانات لتخزين مجموعات من أزواج المفتاح/القيمة"

## استكشاف الأخطاء وإصلاحها

### المشاكل الشائعة

1. **خطأ "too many connections"**
   - السبب: تم الوصول إلى الحد الأقصى من الاتصالات المتزامنة
   - الحل: زيادة max_connections في postgresql.conf أو تحسين التطبيق لاستخدام مجمع اتصالات

2. **أداء بطيء**
   - الأسباب المحتملة:
     * استعلامات غير محسنة
     * فهارس مفقودة
     * VACUUM غير منفذ بانتظام
     * تكوين خادم غير مناسب
   - الحلول:
     * استخدم EXPLAIN ANALYZE لتحليل الاستعلامات
     * أضف فهارس مناسبة
     * قم بتكوين autovacuum بشكل صحيح
     * حسّن تكوين الخادم (shared_buffers, work_mem، إلخ)

3. **حالات التوقف (deadlocks)**
   - السبب: معاملتان أو أكثر تنتظران بشكل متبادل تحرير الأقفال
   - الحل: تحقق من pg_locks وpg_stat_activity لتحديد المعاملات المانعة

### أوامر تشخيصية مفيدة

```sql
-- عرض الاتصالات النشطة
SELECT * FROM pg_stat_activity;

-- تحديد الاستعلامات البطيئة
SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;

-- التحقق من الأقفال
SELECT * FROM pg_locks l JOIN pg_stat_activity a ON l.pid = a.pid;

-- التحقق من حجم الجداول والفهارس
SELECT
  table_name,
  pg_size_pretty(table_size) AS table_size,
  pg_size_pretty(indexes_size) AS indexes_size,
  pg_size_pretty(total_size) AS total_size
FROM (
  SELECT
    table_name,
    pg_table_size(table_name) AS table_size,
    pg_indexes_size(table_name) AS indexes_size,
    pg_total_relation_size(table_name) AS total_size
  FROM (
    SELECT ('"' || table_schema || '"."' || table_name || '"') AS table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
  ) AS all_tables
) AS pretty_sizes
ORDER BY total_size DESC;
```

## أفضل الممارسات

1. **الأمان**
   - استخدم أدوارًا بأقل امتيازات
   - قم بتفعيل SSL للاتصالات
   - استخدم الاستعلامات المعدة مسبقًا لتجنب حقن SQL
   - فكر في استخدام Row-Level Security للتحكم الدقيق في الوصول

2. **الأداء**
   - قم بفهرسة الأعمدة المستخدمة بشكل متكرر في عبارات WHERE وJOIN وORDER BY
   - استخدم EXPLAIN ANALYZE لفهم وتحسين خطط التنفيذ
   - قم بتكوين autovacuum للحفاظ على صحة قاعدة البيانات
   - استخدم العروض المادية للاستعلامات المعقدة التي يتم تنفيذها بشكل متكرر

3. **الصيانة**
   - جدولة نسخ احتياطية منتظمة باستخدام pg_dump
   - تكوين النسخ المتماثل للتوافر العالي
   - مراقبة الأداء بانتظام باستخدام pg_stat_statements
   - التحديث بانتظام إلى أحدث الإصدارات الفرعية للحصول على تصحيحات الأمان
