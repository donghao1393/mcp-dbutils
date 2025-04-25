# MySQL 示例

*[English](../../en/examples/mysql-examples.md) | 中文 | [Français](../../fr/examples/mysql-examples.md) | [Español](../../es/examples/mysql-examples.md) | [العربية](../../ar/examples/mysql-examples.md) | [Русский](../../ru/examples/mysql-examples.md)*

本文档提供了使用 MCP 数据库工具与 MySQL 数据库交互的实用示例。这些示例展示了如何利用 MySQL 的特性进行数据分析和查询优化。

## 基础查询示例

### 列出所有表

```sql
SHOW TABLES;
```

或者使用信息架构：

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'your_database_name';
```

### 查看表结构

```sql
DESCRIBE customers;
```

或者使用信息架构获取更详细的信息：

```sql
SELECT column_name, data_type, character_maximum_length, is_nullable
FROM information_schema.columns
WHERE table_name = 'customers' AND table_schema = 'your_database_name'
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

## MySQL 特有功能

### 全文搜索

MySQL 提供了全文搜索功能，可以高效地搜索文本内容：

```sql
-- 创建全文索引（如果尚未创建）
ALTER TABLE products ADD FULLTEXT(name, description);

-- 使用自然语言模式进行全文搜索
SELECT * FROM products
WHERE MATCH(name, description) AGAINST('comfortable durable' IN NATURAL LANGUAGE MODE);

-- 使用布尔模式进行更精确的搜索
SELECT * FROM products
WHERE MATCH(name, description) AGAINST('+comfortable -leather' IN BOOLEAN MODE);

-- 带排名的全文搜索
SELECT id, name, description,
       MATCH(name, description) AGAINST('comfortable durable' IN NATURAL LANGUAGE MODE) AS relevance
FROM products
WHERE MATCH(name, description) AGAINST('comfortable durable' IN NATURAL LANGUAGE MODE)
ORDER BY relevance DESC;
```

### 存储过程

MySQL 支持存储过程，可以封装复杂的业务逻辑：

```sql
-- 创建一个简单的存储过程来获取客户订单
DELIMITER //
CREATE PROCEDURE get_customer_orders(IN customer_id_param INT)
BEGIN
    SELECT o.id, o.order_date, o.total_amount, o.status
    FROM orders o
    WHERE o.customer_id = customer_id_param
    ORDER BY o.order_date DESC;
END //
DELIMITER ;

-- 调用存储过程
CALL get_customer_orders(123);
```

### 事件调度器

MySQL 的事件调度器可以自动执行定期任务：

```sql
-- 启用事件调度器
SET GLOBAL event_scheduler = ON;

-- 创建每日汇总销售数据的事件
DELIMITER //
CREATE EVENT daily_sales_summary
ON SCHEDULE EVERY 1 DAY
STARTS '2023-01-01 23:00:00'
DO
BEGIN
    INSERT INTO sales_summary (date, total_sales, order_count)
    SELECT
        DATE(order_date) AS date,
        SUM(total_amount) AS total_sales,
        COUNT(*) AS order_count
    FROM orders
    WHERE DATE(order_date) = DATE(NOW() - INTERVAL 1 DAY)
    GROUP BY DATE(order_date);
END //
DELIMITER ;
```

## 高级查询技巧

### 窗口函数 (MySQL 8.0+)

MySQL 8.0 及以上版本支持窗口函数：

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

### 公共表表达式 (CTE) (MySQL 8.0+)

MySQL 8.0 及以上版本支持 CTE：

```sql
-- 使用 CTE 查找高价值客户
WITH high_value_customers AS (
  SELECT
    customer_id,
    SUM(total_amount) AS total_spent
  FROM orders
  GROUP BY customer_id
  HAVING SUM(total_amount) > 10000
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

### 使用 JSON 数据 (MySQL 5.7+)

MySQL 5.7 及以上版本支持 JSON 数据类型：

```sql
-- 查询 JSON 字段中的特定属性
SELECT
  id,
  name,
  JSON_EXTRACT(preferences, '$.theme') AS theme,
  JSON_EXTRACT(preferences, '$.language') AS language
FROM users;

-- 使用 JSON 路径操作符 (MySQL 8.0+)
SELECT
  id,
  name,
  preferences->'$.theme' AS theme,
  preferences->'$.language' AS language
FROM users;

-- 使用 JSON 条件过滤
SELECT * FROM products
WHERE JSON_EXTRACT(attributes, '$.color') = 'red'
AND JSON_EXTRACT(attributes, '$.weight') < 100;

-- 更新 JSON 数据
UPDATE users
SET preferences = JSON_SET(preferences,
                          '$.theme', 'dark',
                          '$.notifications', JSON_OBJECT('email', true, 'sms', false))
WHERE id = 123;
```

## 性能优化技巧

### 使用 EXPLAIN

使用 `EXPLAIN` 可以查看查询计划，帮助优化查询：

```sql
EXPLAIN
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

-- 使用 FORCE INDEX 提示优化器使用特定索引
SELECT * FROM orders
FORCE INDEX (idx_orders_customer_date)
WHERE customer_id = 123 AND order_date > '2023-01-01';
```

### 分区表查询

对于分区表，确保查询包含分区键以提高性能：

```sql
-- 创建分区表
CREATE TABLE sales (
    id INT NOT NULL,
    sale_date DATE NOT NULL,
    customer_id INT,
    amount DECIMAL(10,2),
    PRIMARY KEY (id, sale_date)
)
PARTITION BY RANGE (YEAR(sale_date)) (
    PARTITION p2021 VALUES LESS THAN (2022),
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION pmax VALUES LESS THAN MAXVALUE
);

-- 高效的分区表查询（包含分区键）
SELECT * FROM sales
WHERE sale_date BETWEEN '2023-01-01' AND '2023-01-31'
AND customer_id = 456;

-- 查看分区信息
SELECT
    PARTITION_NAME,
    TABLE_ROWS,
    AVG_ROW_LENGTH,
    DATA_LENGTH
FROM
    information_schema.PARTITIONS
WHERE
    TABLE_SCHEMA = 'your_database_name'
    AND TABLE_NAME = 'sales';
```

## 实际应用场景

### 场景 1：销售数据分析

分析过去 12 个月的销售趋势：

```sql
-- 按月统计销售额
SELECT
  DATE_FORMAT(order_date, '%Y-%m') AS month,
  SUM(total_amount) AS monthly_sales,
  COUNT(DISTINCT customer_id) AS unique_customers,
  SUM(total_amount) / COUNT(DISTINCT customer_id) AS avg_per_customer
FROM orders
WHERE order_date >= DATE_SUB(CURRENT_DATE, INTERVAL 12 MONTH)
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY month;

-- 计算同比增长
SELECT
  current_year.month,
  current_year.sales AS current_sales,
  previous_year.sales AS previous_sales,
  (current_year.sales - previous_year.sales) / previous_year.sales * 100 AS growth_percent
FROM (
  SELECT
    DATE_FORMAT(order_date, '%m') AS month,
    SUM(total_amount) AS sales
  FROM orders
  WHERE order_date >= DATE_FORMAT(DATE_SUB(CURRENT_DATE, INTERVAL 1 YEAR), '%Y-01-01')
    AND order_date < DATE_FORMAT(CURRENT_DATE, '%Y-01-01')
  GROUP BY DATE_FORMAT(order_date, '%m')
) previous_year
JOIN (
  SELECT
    DATE_FORMAT(order_date, '%m') AS month,
    SUM(total_amount) AS sales
  FROM orders
  WHERE order_date >= DATE_FORMAT(CURRENT_DATE, '%Y-01-01')
  GROUP BY DATE_FORMAT(order_date, '%m')
) current_year ON current_year.month = previous_year.month
ORDER BY STR_TO_DATE(current_year.month, '%m');
```

### 场景 2：客户细分分析

根据购买行为对客户进行细分：

```sql
-- RFM (Recency, Frequency, Monetary) 分析
WITH customer_rfm AS (
  SELECT
    customer_id,
    DATEDIFF(CURRENT_DATE, MAX(order_date)) AS recency,
    COUNT(*) AS frequency,
    SUM(total_amount) AS monetary
  FROM orders
  WHERE order_date >= DATE_SUB(CURRENT_DATE, INTERVAL 1 YEAR)
  GROUP BY customer_id
)
SELECT
  c.id,
  c.name,
  c.email,
  CASE
    WHEN rfm.recency <= 30 THEN 'Recent'
    WHEN rfm.recency <= 90 THEN 'Mid'
    ELSE 'Old'
  END AS recency_segment,
  CASE
    WHEN rfm.frequency >= 10 THEN 'High'
    WHEN rfm.frequency >= 5 THEN 'Mid'
    ELSE 'Low'
  END AS frequency_segment,
  CASE
    WHEN rfm.monetary >= 5000 THEN 'High'
    WHEN rfm.monetary >= 1000 THEN 'Mid'
    ELSE 'Low'
  END AS monetary_segment,
  CONCAT(
    CASE
      WHEN rfm.recency <= 30 THEN 'R'
      WHEN rfm.recency <= 90 THEN 'r'
      ELSE '-'
    END,
    CASE
      WHEN rfm.frequency >= 10 THEN 'F'
      WHEN rfm.frequency >= 5 THEN 'f'
      ELSE '-'
    END,
    CASE
      WHEN rfm.monetary >= 5000 THEN 'M'
      WHEN rfm.monetary >= 1000 THEN 'm'
      ELSE '-'
    END
  ) AS rfm_segment
FROM customers c
JOIN customer_rfm rfm ON c.id = rfm.customer_id
ORDER BY rfm.recency, rfm.frequency DESC, rfm.monetary DESC;
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

-- 计算产品周转率
SELECT
  p.id,
  p.name,
  p.category,
  i.current_stock,
  COALESCE(s.total_sold, 0) AS total_sold_last_30_days,
  CASE
    WHEN i.current_stock > 0 AND COALESCE(s.total_sold, 0) > 0
    THEN (COALESCE(s.total_sold, 0) / i.current_stock) * 30
    ELSE 0
  END AS turnover_rate
FROM products p
JOIN inventory i ON p.id = i.product_id
LEFT JOIN (
  SELECT
    oi.product_id,
    SUM(oi.quantity) AS total_sold
  FROM order_items oi
  JOIN orders o ON oi.order_id = o.id
  WHERE o.order_date >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY)
    AND o.status = 'completed'
  GROUP BY oi.product_id
) s ON p.id = s.product_id
ORDER BY turnover_rate DESC;
```

## 与 AI 的交互示例

以下是一些与 AI 交互使用 MySQL 数据的示例对话：

**您**：能否帮我分析过去 6 个月中，哪些产品类别的销售额最高？

**AI**：我来帮您分析。以下是过去 6 个月销售额最高的产品类别：

```
产品类别       | 销售额      | 订单数量  | 平均订单金额
-------------|-----------|---------|------------
电子产品       | ¥2,345,670 | 4,532   | ¥517.58
家居用品       | ¥1,456,890 | 6,789   | ¥214.60
服装鞋帽       | ¥987,450   | 8,901   | ¥110.94
美妆个护       | ¥876,540   | 5,678   | ¥154.38
食品饮料       | ¥654,320   | 7,890   | ¥82.93
```

电子产品类别的销售额最高，达到 ¥2,345,670，尽管订单数量不是最多的。服装鞋帽类别的订单数量最多，但平均订单金额较低。这表明电子产品是高价值商品，而服装是高频次购买商品。

**您**：我们的客户主要来自哪些城市？能否按照客户数量排序？

**AI**：根据数据分析，您的客户主要分布在以下城市：

```
城市     | 客户数量  | 占比     | 平均消费额
--------|---------|---------|------------
北京     | 4,532   | 18.6%   | ¥1,876
上海     | 3,987   | 16.4%   | ¥2,043
广州     | 2,876   | 11.8%   | ¥1,654
深圳     | 2,543   | 10.5%   | ¥1,932
成都     | 1,876   | 7.7%    | ¥1,432
杭州     | 1,654   | 6.8%    | ¥1,765
武汉     | 1,432   | 5.9%    | ¥1,321
南京     | 1,321   | 5.4%    | ¥1,543
其他城市  | 4,123   | 16.9%   | ¥1,234
```

北京和上海的客户数量最多，合计占总客户数的 35%。值得注意的是，上海客户的平均消费额最高，达到 ¥2,043，这表明上海市场有很大的发展潜力。