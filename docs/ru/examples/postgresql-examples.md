# Примеры PostgreSQL

*[English](../../en/examples/postgresql-examples.md) | [中文](../../zh/examples/postgresql-examples.md) | [Français](../../fr/examples/postgresql-examples.md) | [Español](../../es/examples/postgresql-examples.md) | [العربية](../../ar/examples/postgresql-examples.md) | Русский*

Этот документ содержит примеры использования MCP Database Utilities с базами данных PostgreSQL.

## Настройка соединения с PostgreSQL

Для подключения к базе данных PostgreSQL вам необходимо добавить соответствующую конфигурацию в ваш файл конфигурации:

```yaml
connections:
  my-postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: mydatabase
    user: myuser
    password: mypassword
    ssl:
      mode: verify-full
      cert: /path/to/client-cert.pem  # опционально
      key: /path/to/client-key.pem    # опционально
      root: /path/to/root.crt         # опционально
    pool:
      max_size: 5
      timeout: 30
```

### Параметры соединения

| Параметр | Обязательный | Описание |
|----------|--------------|----------|
| `type` | Да | Тип базы данных, должен быть `postgres` |
| `host` | Да | Хост сервера PostgreSQL |
| `port` | Нет | Порт сервера PostgreSQL (по умолчанию: 5432) |
| `dbname` | Да | Имя базы данных для подключения |
| `user` | Да | Имя пользователя для аутентификации |
| `password` | Да | Пароль для аутентификации |
| `ssl.mode` | Нет | Режим SSL: disable, allow, prefer, require, verify-ca, verify-full |
| `ssl.cert` | Нет | Путь к клиентскому сертификату |
| `ssl.key` | Нет | Путь к клиентскому ключу |
| `ssl.root` | Нет | Путь к корневому сертификату |
| `pool.max_size` | Нет | Максимальный размер пула соединений (по умолчанию: 5) |
| `pool.timeout` | Нет | Таймаут соединения в секундах (по умолчанию: 30) |

## Примеры взаимодействия

### Просмотр доступных таблиц

**Вы**: "Можете ли вы показать мне все таблицы в базе данных my-postgres?"

**ИИ**: "Я проверю таблицы в базе данных my-postgres для вас. Вот список таблиц:

```
              Имя таблицы              |  Схема  |  Владелец  
-------------------------------------+--------+------------
 customers                           | public | postgres
 products                            | public | postgres
 orders                              | public | postgres
 order_items                         | public | postgres
 inventory                           | public | postgres
 suppliers                           | public | postgres
 employees                           | public | postgres
 departments                         | public | postgres
 product_categories                  | public | postgres
 customer_addresses                  | public | postgres
 shipping                            | public | postgres
 payments                            | public | postgres
```

### Изучение структуры таблицы

**Вы**: "Какова структура таблицы customers?"

**ИИ**: "Вот структура таблицы customers в базе данных my-postgres:

```
                                         Таблица "public.customers"
        Столбец        |           Тип            | Сортировка | Nullable |             По умолчанию              
-----------------------+-------------------------+-----------+----------+--------------------------------------
 id                    | integer                 |           | not null | nextval('customers_id_seq'::regclass)
 first_name            | character varying(50)   |           | not null | 
 last_name             | character varying(50)   |           | not null | 
 email                 | character varying(100)  |           | not null | 
 phone                 | character varying(20)   |           |          | 
 created_at            | timestamp with time zone|           | not null | CURRENT_TIMESTAMP
 updated_at            | timestamp with time zone|           | not null | CURRENT_TIMESTAMP
 last_login            | timestamp with time zone|           |          | 
 status                | character varying(20)   |           | not null | 'active'::character varying
 total_spent           | numeric(10,2)           |           | not null | 0.00
 loyalty_points        | integer                 |           | not null | 0
 date_of_birth         | date                    |           |          | 
 preferences           | jsonb                   |           |          | '{}'::jsonb
Индексы:
    "customers_pkey" PRIMARY KEY, btree (id)
    "customers_email_key" UNIQUE CONSTRAINT, btree (email)
    "customers_last_name_idx" btree (last_name)
    "customers_status_idx" btree (status)
Ссылки извне:
    TABLE "customer_addresses" CONSTRAINT "customer_addresses_customer_id_fkey" FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
    TABLE "orders" CONSTRAINT "orders_customer_id_fkey" FOREIGN KEY (customer_id) REFERENCES customers(id)
```

Таблица customers содержит информацию о клиентах, включая их контактные данные, статус, историю покупок и предпочтения. Обратите внимание на использование типа данных jsonb для хранения предпочтений, что является одной из мощных функций PostgreSQL."

### Выполнение запросов

**Вы**: "Сколько клиентов у нас в каждом статусе?"

**ИИ**: "Я выполню запрос для подсчета клиентов по статусам. Вот результаты:

```sql
SELECT status, COUNT(*) as customer_count 
FROM customers 
GROUP BY status 
ORDER BY customer_count DESC;
```

```
  status   | customer_count 
-----------+----------------
 active    | 5,432
 inactive  | 876
 suspended | 124
 pending   | 98
 blocked   | 45
```

Большинство ваших клиентов имеют статус 'active' (5,432), за ними следуют 'inactive' (876) и 'suspended' (124)."

### Анализ данных с использованием продвинутых функций PostgreSQL

**Вы**: "Можете ли вы проанализировать распределение заказов по месяцам и показать месячный рост?"

**ИИ**: "Я проанализирую распределение заказов по месяцам и рассчитаю месячный рост, используя оконные функции PostgreSQL:

```sql
SELECT 
    date_trunc('month', order_date) as month,
    COUNT(*) as order_count,
    SUM(total_amount) as monthly_revenue,
    ROUND(
        (SUM(total_amount) - LAG(SUM(total_amount), 1) OVER (ORDER BY date_trunc('month', order_date))) / 
        LAG(SUM(total_amount), 1) OVER (ORDER BY date_trunc('month', order_date)) * 100, 
        2
    ) as revenue_growth_pct
FROM 
    orders
WHERE 
    order_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '12 months')
    AND order_date < DATE_TRUNC('month', CURRENT_DATE)
GROUP BY 
    date_trunc('month', order_date)
ORDER BY 
    month;
```

```
    month    | order_count | monthly_revenue | revenue_growth_pct 
-------------+-------------+-----------------+-------------------
 2022-11-01  | 1,245       | 245,678.90      | null
 2022-12-01  | 1,876       | 387,654.32      | 57.79
 2023-01-01  | 987         | 198,765.43      | -48.73
 2023-02-01  | 876         | 187,654.32      | -5.59
 2023-03-01  | 1,023       | 210,987.65      | 12.43
 2023-04-01  | 1,156       | 232,109.87      | 10.01
 2023-05-01  | 1,287       | 254,321.09      | 9.57
 2023-06-01  | 1,345       | 265,432.10      | 4.37
 2023-07-01  | 1,432       | 276,543.21      | 4.19
 2023-08-01  | 1,521       | 287,654.32      | 4.02
 2023-09-01  | 1,634       | 298,765.43      | 3.86
 2023-10-01  | 1,789       | 321,098.76      | 7.48
```

**Анализ:**

1. **Сезонные тенденции**:
   - Пик заказов и выручки в декабре (праздничный сезон)
   - Значительное снижение в январе-феврале (постпраздничный спад)
   - Постепенный рост с марта по октябрь

2. **Рост выручки**:
   - Наибольший рост: декабрь (+57.79%)
   - Наибольшее снижение: январь (-48.73%)
   - Стабильный рост с марта по октябрь (в среднем +6.49% в месяц)

3. **Объем заказов vs. Выручка**:
   - Средняя стоимость заказа в декабре: $206.64
   - Средняя стоимость заказа в октябре: $179.49
   - Общая тенденция: количество заказов растет быстрее, чем выручка, что указывает на снижение средней стоимости заказа

4. **Рекомендации**:
   - Подготовьтесь к праздничному сезону с увеличенными запасами
   - Рассмотрите возможность специальных промоакций в январе-феврале для смягчения постпраздничного спада
   - Разработайте стратегии для увеличения средней стоимости заказа"

### Использование JSON-функций PostgreSQL

**Вы**: "Можете ли вы проанализировать предпочтения наших клиентов, хранящиеся в поле preferences?"

**ИИ**: "Я проанализирую предпочтения клиентов, используя JSON-функции PostgreSQL:

```sql
SELECT 
    preferences->>'preferred_category' as category,
    COUNT(*) as customer_count,
    ROUND(AVG((preferences->>'price_sensitivity')::numeric), 2) as avg_price_sensitivity,
    ROUND(AVG((preferences->>'brand_loyalty')::numeric), 2) as avg_brand_loyalty
FROM 
    customers
WHERE 
    preferences IS NOT NULL 
    AND preferences->>'preferred_category' IS NOT NULL
GROUP BY 
    preferences->>'preferred_category'
ORDER BY 
    customer_count DESC;
```

```
    category    | customer_count | avg_price_sensitivity | avg_brand_loyalty 
----------------+----------------+-----------------------+-------------------
 Electronics    | 1,245          | 3.75                  | 4.12
 Clothing       | 987            | 4.23                  | 3.45
 Home & Kitchen | 876            | 3.56                  | 3.78
 Sports         | 654            | 3.12                  | 4.32
 Beauty         | 543            | 4.45                  | 3.98
 Books          | 432            | 2.87                  | 3.56
 Toys           | 321            | 3.65                  | 3.21
 Automotive     | 234            | 3.34                  | 4.56
 Grocery        | 198            | 4.67                  | 2.98
 Jewelry        | 156            | 2.45                  | 4.78
```

**Анализ предпочтений клиентов:**

1. **Популярные категории**:
   - Электроника является наиболее предпочтительной категорией (1,245 клиентов)
   - За ней следуют Одежда (987) и Товары для дома и кухни (876)

2. **Ценовая чувствительность** (по шкале 1-5, где 5 - наиболее чувствительны к цене):
   - Клиенты, предпочитающие Продукты питания, наиболее чувствительны к цене (4.67)
   - Клиенты, предпочитающие Ювелирные изделия, наименее чувствительны к цене (2.45)
   - Электроника имеет среднюю ценовую чувствительность (3.75)

3. **Лояльность к бренду** (по шкале 1-5, где 5 - наиболее лояльны):
   - Клиенты, предпочитающие Ювелирные изделия, наиболее лояльны к бренду (4.78)
   - Клиенты, предпочитающие Автомобильные товары, также очень лояльны (4.56)
   - Клиенты, предпочитающие Продукты питания, наименее лояльны к бренду (2.98)

4. **Стратегические выводы**:
   - Для Электроники: умеренная ценовая чувствительность и высокая лояльность к бренду указывают на возможность премиального ценообразования для известных брендов
   - Для Одежды: высокая ценовая чувствительность предполагает акцент на ценностные предложения и скидки
   - Для Ювелирных изделий: низкая ценовая чувствительность и высокая лояльность к бренду указывают на возможность премиального ценообразования и эксклюзивных предложений"

### Использование оконных функций

**Вы**: "Можете ли вы показать мне топ-3 продукта в каждой категории по продажам?"

**ИИ**: "Я использую оконные функции PostgreSQL для определения топ-3 продуктов в каждой категории:

```sql
WITH product_sales AS (
    SELECT 
        p.id,
        p.name,
        pc.name as category,
        SUM(oi.quantity) as total_units_sold,
        SUM(oi.quantity * oi.unit_price) as total_revenue,
        RANK() OVER (PARTITION BY pc.name ORDER BY SUM(oi.quantity * oi.unit_price) DESC) as rank
    FROM 
        products p
    JOIN 
        product_categories pc ON p.category_id = pc.id
    JOIN 
        order_items oi ON p.id = oi.product_id
    GROUP BY 
        p.id, p.name, pc.name
)
SELECT 
    category,
    id,
    name,
    total_units_sold,
    total_revenue
FROM 
    product_sales
WHERE 
    rank <= 3
ORDER BY 
    category, rank;
```

```
    category    |  id  |           name           | total_units_sold | total_revenue 
----------------+------+--------------------------+-----------------+---------------
 Automotive     | 145  | Premium Car Vacuum       | 876             | 87,600.00
 Automotive     | 167  | Bluetooth Car Adapter    | 1,234           | 61,700.00
 Automotive     | 189  | Car Phone Mount          | 1,567           | 47,010.00
 Beauty         | 234  | Luxury Face Cream        | 765             | 114,750.00
 Beauty         | 256  | Professional Hair Dryer  | 654             | 98,100.00
 Beauty         | 278  | Skincare Gift Set        | 543             | 81,450.00
 Books          | 345  | Bestselling Novel        | 1,876           | 56,280.00
 Books          | 367  | Cooking Encyclopedia     | 987             | 49,350.00
 Books          | 389  | Self-Help Bestseller     | 876             | 43,800.00
 Clothing       | 56   | Designer Jeans           | 1,543           | 154,300.00
 Clothing       | 78   | Winter Jacket            | 987             | 148,050.00
 Clothing       | 90   | Running Shoes            | 1,765           | 141,200.00
 Electronics    | 12   | Premium Laptop           | 765             | 918,000.00
 Electronics    | 34   | Smartphone Pro           | 1,432           | 716,000.00
 Electronics    | 45   | Wireless Headphones      | 2,345           | 351,750.00
 Grocery        | 456  | Organic Coffee Beans     | 2,345           | 70,350.00
 Grocery        | 478  | Premium Chocolate Box    | 1,876           | 56,280.00
 Grocery        | 490  | Specialty Olive Oil      | 1,234           | 49,360.00
 Home & Kitchen | 123  | Robot Vacuum Cleaner     | 654             | 261,600.00
 Home & Kitchen | 134  | Smart Coffee Maker       | 876             | 175,200.00
 Home & Kitchen | 156  | Professional Blender     | 765             | 153,000.00
 Jewelry        | 567  | Diamond Earrings         | 123             | 184,500.00
 Jewelry        | 589  | Gold Necklace            | 234             | 175,500.00
 Jewelry        | 601  | Silver Bracelet          | 345             | 103,500.00
 Sports         | 278  | Mountain Bike            | 234             | 234,000.00
 Sports         | 290  | Tennis Racket Pro        | 456             | 136,800.00
 Sports         | 312  | Fitness Smartwatch       | 987             | 118,440.00
 Toys           | 678  | Educational Robot Kit    | 543             | 108,600.00
 Toys           | 690  | Building Blocks Set      | 876             | 87,600.00
 Toys           | 712  | Remote Control Car       | 987             | 78,960.00
```

**Анализ:**

1. **Высокая стоимость vs. Объем**:
   - Электроника имеет наивысшую выручку, особенно Premium Laptop (918,000.00)
   - Продукты питания и Игрушки имеют высокие объемы продаж, но более низкую общую выручку

2. **Средняя стоимость единицы**:
   - Ювелирные изделия: самая высокая средняя стоимость (~1,500.00 за единицу)
   - Электроника: также высокая средняя стоимость (~500.00 за единицу)
   - Книги и Продукты питания: самая низкая средняя стоимость (~30.00 за единицу)

3. **Распределение выручки**:
   - Электроника: топ-3 продукта генерируют ~2 миллиона в выручке
   - Ювелирные изделия: топ-3 продукта генерируют ~460,000 в выручке
   - Товары для дома и кухни: топ-3 продукта генерируют ~590,000 в выручке

4. **Рекомендации**:
   - Сосредоточьтесь на высокодоходных категориях: Электроника, Ювелирные изделия, Товары для дома и кухни
   - Для категорий с низкой стоимостью единицы (Книги, Продукты питания): увеличьте объем продаж через пакетные предложения
   - Для категорий с высокой стоимостью единицы (Ювелирные изделия, Электроника): улучшите опыт покупателя для увеличения конверсии"

## Советы по оптимизации

### Индексы

PostgreSQL предлагает несколько типов индексов для оптимизации запросов:

1. **B-tree индексы** (по умолчанию):
   ```sql
   CREATE INDEX idx_customers_last_name ON customers(last_name);
   ```

2. **Частичные индексы** (для подмножества данных):
   ```sql
   CREATE INDEX idx_active_customers ON customers(id) WHERE status = 'active';
   ```

3. **Многоколоночные индексы**:
   ```sql
   CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
   ```

4. **GIN индексы** (для JSON и массивов):
   ```sql
   CREATE INDEX idx_customer_preferences ON customers USING GIN(preferences);
   ```

5. **Проверка использования индексов**:
   ```sql
   EXPLAIN ANALYZE SELECT * FROM customers WHERE email = 'example@email.com';
   ```

### Оптимизация запросов

1. **Используйте EXPLAIN ANALYZE для анализа запросов**:
   ```sql
   EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 123;
   ```

2. **Используйте CTE для улучшения читаемости сложных запросов**:
   ```sql
   WITH monthly_sales AS (
       SELECT date_trunc('month', order_date) as month, SUM(total_amount) as revenue
       FROM orders
       GROUP BY date_trunc('month', order_date)
   )
   SELECT * FROM monthly_sales ORDER BY month;
   ```

3. **Используйте LIMIT для ограничения результатов**:
   ```sql
   SELECT * FROM products ORDER BY created_at DESC LIMIT 100;
   ```

4. **Используйте подходящие типы данных**:
   - Используйте `text` для строк переменной длины
   - Используйте `timestamp with time zone` для временных меток
   - Используйте `numeric` для точных денежных значений
   - Используйте `jsonb` вместо `json` для лучшей производительности

## Продвинутые функции PostgreSQL

### Материализованные представления

Материализованные представления сохраняют результаты запроса для быстрого доступа:

```sql
CREATE MATERIALIZED VIEW monthly_sales AS
SELECT 
    date_trunc('month', order_date) as month,
    SUM(total_amount) as revenue
FROM 
    orders
GROUP BY 
    date_trunc('month', order_date);

-- Обновление материализованного представления
REFRESH MATERIALIZED VIEW monthly_sales;
```

### Полнотекстовый поиск

PostgreSQL предлагает мощные возможности полнотекстового поиска:

```sql
-- Создание индекса для полнотекстового поиска
CREATE INDEX idx_product_search ON products USING GIN(to_tsvector('english', name || ' ' || description));

-- Поиск продуктов
SELECT name, description
FROM products
WHERE to_tsvector('english', name || ' ' || description) @@ to_tsquery('english', 'wireless & headphones');
```

### Хранение и запрос JSON-данных

PostgreSQL отлично работает с JSON-данными:

```sql
-- Запрос конкретных полей JSON
SELECT 
    id,
    preferences->>'preferred_category' as category,
    (preferences->>'price_sensitivity')::numeric as price_sensitivity
FROM 
    customers
WHERE 
    (preferences->>'brand_loyalty')::numeric > 4;

-- Обновление JSON-поля
UPDATE customers
SET preferences = jsonb_set(preferences, '{preferred_category}', '"Electronics"')
WHERE id = 123;
```

### Расширения

PostgreSQL поддерживает множество расширений:

1. **PostGIS** для геопространственных данных:
   ```sql
   CREATE EXTENSION postgis;
   
   -- Запрос клиентов в радиусе 10 км от точки
   SELECT * FROM customer_addresses
   WHERE ST_DWithin(
       location,
       ST_SetSRID(ST_MakePoint(-73.935242, 40.730610), 4326),
       10000
   );
   ```

2. **pg_stat_statements** для мониторинга запросов:
   ```sql
   CREATE EXTENSION pg_stat_statements;
   
   -- Просмотр самых медленных запросов
   SELECT query, calls, total_time, mean_time
   FROM pg_stat_statements
   ORDER BY mean_time DESC
   LIMIT 10;
   ```

## Заключение

PostgreSQL — это мощная система управления базами данных с богатым набором функций, которая отлично работает с MCP Database Utilities. Используя продвинутые функции PostgreSQL, такие как JSON-поддержка, оконные функции и материализованные представления, вы можете эффективно анализировать и управлять вашими данными через интерфейс ИИ.
