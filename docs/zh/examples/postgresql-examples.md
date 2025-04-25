# PostgreSQL 示例

*[English](../../en/examples/postgresql-examples.md) | 中文 | [Français](../../fr/examples/postgresql-examples.md) | [Español](../../es/examples/postgresql-examples.md) | [العربية](../../ar/examples/postgresql-examples.md) | [Русский](../../ru/examples/postgresql-examples.md)*

本文档提供了使用 MCP 数据库工具与 PostgreSQL 数据库交互的实用示例。这些示例展示了如何利用 PostgreSQL 的特性进行数据分析和查询优化。

## 基础查询示例

### 列出所有表

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

### 查看表结构

```sql
SELECT column_name, data_type, character_maximum_length, is_nullable
FROM information_schema.columns
WHERE table_name = 'customers'
ORDER BY ordinal_position;
```

### 基本数据查询

```sql
-- 查询客户表中的前 10 条记录
SELECT * FROM customers LIMIT 10;

-- 按条件筛选
SELECT * FROM customers WHERE city = '北京' AND status = 'active';

-- 排序查询
SELECT customer_id, name, registration_date
FROM customers
ORDER BY registration_date DESC
LIMIT 20;
```

## PostgreSQL 特有功能

### JSON 数据查询

PostgreSQL 提供了强大的 JSON 处理功能，可以直接查询和操作 JSON 数据：

```sql
-- 查询 JSON 字段中的特定属性
SELECT
  id,
  name,
  preferences->>'theme' AS theme,
  preferences->>'language' AS language
FROM users;

-- 使用 JSON 条件过滤
SELECT * FROM products
WHERE attributes->>'color' = 'red'
AND CAST(attributes->>'weight' AS INTEGER) < 100;

-- 使用 JSON 数组
SELECT * FROM orders
WHERE items @> '[{"product_id": 123}]'::jsonb;
```

### 全文搜索

PostgreSQL 的全文搜索功能可以高效地搜索文本内容：

```sql
-- 创建全文搜索向量
SELECT to_tsvector('english', description) FROM products;

-- 使用全文搜索查询
SELECT title, description
FROM products
WHERE to_tsvector('english', description) @@ to_tsquery('english', 'comfortable & durable');

-- 带排名的全文搜索
SELECT title, description,
       ts_rank(to_tsvector('english', description), to_tsquery('english', 'comfortable & durable')) AS rank
FROM products
WHERE to_tsvector('english', description) @@ to_tsquery('english', 'comfortable & durable')
ORDER BY rank DESC;
```

### 数组操作

PostgreSQL 支持数组数据类型，可以直接在 SQL 中操作数组：

```sql
-- 查询包含特定标签的产品
SELECT * FROM products WHERE 'organic' = ANY(tags);

-- 数组交集
SELECT * FROM products WHERE tags && ARRAY['eco-friendly', 'sustainable'];

-- 展开数组
SELECT id, unnest(tags) AS tag FROM products;

-- 数组聚合
SELECT category, array_agg(name) AS product_names
FROM products
GROUP BY category;
```

## 高级查询技巧

### 窗口函数

窗口函数可以在不改变结果集行数的情况下执行计算：

```sql
-- 按类别计算产品排名
SELECT
  name,
  category,
  price,
  RANK() OVER (PARTITION BY category ORDER BY price DESC) as price_rank
FROM products;

-- 计算移动平均
SELECT
  date,
  sales,
  AVG(sales) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS weekly_avg
FROM daily_sales;

-- 计算累计总和
SELECT
  date,
  sales,
  SUM(sales) OVER (ORDER BY date) AS cumulative_sales
FROM daily_sales;
```

### 公共表表达式 (CTE)

使用 CTE 可以简化复杂查询：

```sql
-- 使用 CTE 查找高价值客户
WITH high_value_customers AS (
  SELECT
    customer_id,
    SUM(amount) AS total_spent
  FROM orders
  GROUP BY customer_id
  HAVING SUM(amount) > 10000
)
SELECT c.name, c.email, hvc.total_spent
FROM high_value_customers hvc
JOIN customers c ON hvc.customer_id = c.id
ORDER BY hvc.total_spent DESC;

-- 递归 CTE 查询组织结构
WITH RECURSIVE org_hierarchy AS (
  -- 基础查询：找出顶级管理者
  SELECT id, name, manager_id, 1 AS level
  FROM employees
  WHERE manager_id IS NULL

  UNION ALL

  -- 递归查询：找出每个员工的下属
  SELECT e.id, e.name, e.manager_id, oh.level + 1
  FROM employees e
  JOIN org_hierarchy oh ON e.manager_id = oh.id
)
SELECT id, name, level
FROM org_hierarchy
ORDER BY level, name;
```

## 性能优化技巧

### 使用 EXPLAIN ANALYZE

使用 `EXPLAIN ANALYZE` 可以查看查询计划和执行时间，帮助优化查询：

```sql
EXPLAIN ANALYZE
SELECT c.name, COUNT(o.id) AS order_count
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE c.status = 'active'
GROUP BY c.name
ORDER BY order_count DESC;
```

### 优化索引使用

确保查询使用了适当的索引：

```sql
-- 检查查询是否使用了索引
EXPLAIN
SELECT * FROM orders
WHERE customer_id = 123 AND order_date > '2023-01-01';

-- 创建复合索引以优化特定查询
CREATE INDEX idx_orders_customer_date
ON orders(customer_id, order_date);
```

### 分区表查询

对于分区表，确保查询包含分区键以提高性能：

```sql
-- 高效的分区表查询（包含分区键）
SELECT * FROM sales
WHERE sale_date BETWEEN '2023-01-01' AND '2023-01-31'
AND product_id = 456;
```

## 实际应用场景

### 场景 1：销售数据分析

分析过去 12 个月的销售趋势：

```sql
-- 按月统计销售额
SELECT
  DATE_TRUNC('month', order_date) AS month,
  SUM(amount) AS monthly_sales,
  COUNT(DISTINCT customer_id) AS unique_customers,
  SUM(amount) / COUNT(DISTINCT customer_id) AS avg_per_customer
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;

-- 计算同比增长
WITH monthly_sales AS (
  SELECT
    DATE_TRUNC('month', order_date) AS month,
    SUM(amount) AS sales
  FROM orders
  WHERE order_date >= CURRENT_DATE - INTERVAL '24 months'
  GROUP BY DATE_TRUNC('month', order_date)
)
SELECT
  current_year.month,
  current_year.sales AS current_sales,
  previous_year.sales AS previous_sales,
  (current_year.sales - previous_year.sales) / previous_year.sales * 100 AS growth_percent
FROM monthly_sales current_year
JOIN monthly_sales previous_year
  ON current_year.month = previous_year.month + INTERVAL '1 year'
WHERE current_year.month >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY current_year.month;
```

### 场景 2：客户细分分析

根据购买行为对客户进行细分：

```sql
-- RFM (Recency, Frequency, Monetary) 分析
WITH customer_rfm AS (
  SELECT
    customer_id,
    CURRENT_DATE - MAX(order_date) AS recency,
    COUNT(*) AS frequency,
    SUM(amount) AS monetary
  FROM orders
  WHERE order_date >= CURRENT_DATE - INTERVAL '1 year'
  GROUP BY customer_id
),
rfm_scores AS (
  SELECT
    customer_id,
    NTILE(5) OVER (ORDER BY recency DESC) AS r_score,
    NTILE(5) OVER (ORDER BY frequency) AS f_score,
    NTILE(5) OVER (ORDER BY monetary) AS m_score
  FROM customer_rfm
)
SELECT
  customer_id,
  r_score,
  f_score,
  m_score,
  CONCAT(r_score::TEXT, f_score::TEXT, m_score::TEXT) AS rfm_segment
FROM rfm_scores
ORDER BY r_score DESC, f_score DESC, m_score DESC;
```

### 场景 3：库存管理

分析库存状态和补货需求：

```sql
-- 识别需要补货的产品
SELECT
  p.id,
  p.name,
  p.category,
  i.current_stock,
  i.reorder_level,
  COALESCE(o.pending_orders, 0) AS pending_orders,
  i.current_stock - COALESCE(o.pending_orders, 0) AS effective_stock
FROM products p
JOIN inventory i ON p.id = i.product_id
LEFT JOIN (
  SELECT
    product_id,
    SUM(quantity) AS pending_orders
  FROM order_items oi
  JOIN orders o ON oi.order_id = o.id
  WHERE o.status = 'processing'
  GROUP BY product_id
) o ON p.id = o.product_id
WHERE i.current_stock - COALESCE(o.pending_orders, 0) < i.reorder_level
ORDER BY (i.current_stock - COALESCE(o.pending_orders, 0)) / i.reorder_level;
```

## 与 AI 的交互示例

以下是一些与 AI 交互使用 PostgreSQL 数据的示例对话：

**您**：能否帮我分析过去 6 个月中，哪些产品的销售增长最快？

**AI**：我来帮您分析。以下是过去 6 个月销售增长最快的产品：

```
产品名称         | 6个月前销售额 | 当前销售额 | 增长百分比
---------------|------------|----------|--------
智能手表 Pro     | ¥125,430   | ¥356,780 | 184.4%
无线耳机 X3      | ¥89,670    | ¥213,450 | 138.0%
智能家居套装     | ¥56,890    | ¥132,670 | 133.2%
超薄笔记本电脑   | ¥432,780   | ¥876,540 | 102.5%
健康监测手环     | ¥78,340    | ¥145,670 | 86.0%
```

智能手表 Pro 的销售额增长最为显著，增长了 184.4%。无线耳机和智能家居产品也表现出色。这可能与最近的营销活动和产品升级有关。

**您**：我们的高价值客户主要来自哪些城市？他们平均消费是多少？

**AI**：根据数据分析，您的高价值客户（年消费超过 ¥10,000）主要分布在以下城市：

```
城市     | 高价值客户数量 | 平均年消费额
--------|------------|------------
北京     | 342        | ¥18,765
上海     | 287        | ¥19,432
深圳     | 213        | ¥17,890
广州     | 176        | ¥16,543
杭州     | 124        | ¥15,876
```

上海的高价值客户虽然数量不是最多，但平均消费额最高，达到 ¥19,432。北京的高价值客户数量最多，有 342 位。这些数据可以帮助您更有针对性地制定营销策略和客户服务计划。
