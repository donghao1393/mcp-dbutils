# MySQL Examples

*English | [中文](../../zh/examples/mysql-examples.md) | [Français](../../fr/examples/mysql-examples.md) | [Español](../../es/examples/mysql-examples.md) | [العربية](../../ar/examples/mysql-examples.md) | [Русский](../../ru/examples/mysql-examples.md)*

This document provides practical examples for interacting with MySQL databases using MCP Database Utilities. These examples demonstrate how to leverage MySQL features for data analysis and query optimization.

## Basic Query Examples

### Listing All Tables

```sql
SHOW TABLES;
```

Or using information schema:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'your_database_name';
```

### Viewing Table Structure

```sql
DESCRIBE customers;
```

Or using information schema for more detailed information:

```sql
SELECT column_name, data_type, character_maximum_length, is_nullable
FROM information_schema.columns
WHERE table_name = 'customers' AND table_schema = 'your_database_name'
ORDER BY ordinal_position;
```

### Basic Data Queries

```sql
-- Query the first 10 records from the customers table
SELECT * FROM customers LIMIT 10;

-- Filter by conditions
SELECT * FROM customers WHERE city = 'New York' AND status = 'active';

-- Sorting queries
SELECT customer_id, name, registration_date
FROM customers
ORDER BY registration_date DESC
LIMIT 20;
```

## MySQL-Specific Features

### Full-Text Search

MySQL provides full-text search capabilities for efficiently searching text content:

```sql
-- Create full-text index (if not already created)
ALTER TABLE products ADD FULLTEXT(name, description);

-- Use natural language mode for full-text search
SELECT * FROM products
WHERE MATCH(name, description) AGAINST('comfortable durable' IN NATURAL LANGUAGE MODE);

-- Use boolean mode for more precise searching
SELECT * FROM products
WHERE MATCH(name, description) AGAINST('+comfortable -leather' IN BOOLEAN MODE);

-- Full-text search with ranking
SELECT id, name, description,
       MATCH(name, description) AGAINST('comfortable durable' IN NATURAL LANGUAGE MODE) AS relevance
FROM products
WHERE MATCH(name, description) AGAINST('comfortable durable' IN NATURAL LANGUAGE MODE)
ORDER BY relevance DESC;
```

### Stored Procedures

MySQL supports stored procedures to encapsulate complex business logic:

```sql
-- Create a simple stored procedure to get customer orders
DELIMITER //
CREATE PROCEDURE get_customer_orders(IN customer_id_param INT)
BEGIN
    SELECT o.id, o.order_date, o.total_amount, o.status
    FROM orders o
    WHERE o.customer_id = customer_id_param
    ORDER BY o.order_date DESC;
END //
DELIMITER ;

-- Call the stored procedure
CALL get_customer_orders(123);
```

### Event Scheduler

MySQL's event scheduler can automatically execute periodic tasks:

```sql
-- Enable event scheduler
SET GLOBAL event_scheduler = ON;

-- Create an event to summarize daily sales data
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

## Advanced Query Techniques

### Window Functions (MySQL 8.0+)

MySQL 8.0 and above supports window functions:

```sql
-- Calculate product ranking by category
SELECT
  name,
  category,
  price,
  RANK() OVER (PARTITION BY category ORDER BY price DESC) as price_rank
FROM products;

-- Calculate moving average
SELECT
  date,
  sales,
  AVG(sales) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS weekly_avg
FROM daily_sales;

-- Calculate cumulative sum
SELECT
  date,
  sales,
  SUM(sales) OVER (ORDER BY date) AS cumulative_sales
FROM daily_sales;
```

### Common Table Expressions (CTEs) (MySQL 8.0+)

MySQL 8.0 and above supports CTEs:

```sql
-- Use CTE to find high-value customers
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

-- Recursive CTE to query organizational structure
WITH RECURSIVE org_hierarchy AS (
  -- Base query: find top-level managers
  SELECT id, name, manager_id, 1 AS level
  FROM employees
  WHERE manager_id IS NULL

  UNION ALL

  -- Recursive query: find each employee's subordinates
  SELECT e.id, e.name, e.manager_id, oh.level + 1
  FROM employees e
  JOIN org_hierarchy oh ON e.manager_id = oh.id
)
SELECT id, name, level
FROM org_hierarchy
ORDER BY level, name;
```

### Using JSON Data (MySQL 5.7+)

MySQL 5.7 and above supports JSON data type:

```sql
-- Query specific properties from JSON fields
SELECT
  id,
  name,
  JSON_EXTRACT(preferences, '$.theme') AS theme,
  JSON_EXTRACT(preferences, '$.language') AS language
FROM users;

-- Using JSON path operator (MySQL 8.0+)
SELECT
  id,
  name,
  preferences->'$.theme' AS theme,
  preferences->'$.language' AS language
FROM users;

-- Filter using JSON conditions
SELECT * FROM products
WHERE JSON_EXTRACT(attributes, '$.color') = 'red'
AND JSON_EXTRACT(attributes, '$.weight') < 100;

-- Update JSON data
UPDATE users
SET preferences = JSON_SET(preferences,
                          '$.theme', 'dark',
                          '$.notifications', JSON_OBJECT('email', true, 'sms', false))
WHERE id = 123;
```

## Performance Optimization Tips

### Using EXPLAIN

Use `EXPLAIN` to view query plans and help optimize queries:

```sql
EXPLAIN
SELECT c.name, COUNT(o.id) AS order_count
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE c.status = 'active'
GROUP BY c.name
ORDER BY order_count DESC;
```

### Optimizing Index Usage

Ensure queries use appropriate indexes:

```sql
-- Check if a query uses indexes
EXPLAIN
SELECT * FROM orders
WHERE customer_id = 123 AND order_date > '2023-01-01';

-- Create composite index to optimize specific queries
CREATE INDEX idx_orders_customer_date
ON orders(customer_id, order_date);

-- Use FORCE INDEX hint to make optimizer use a specific index
SELECT * FROM orders
FORCE INDEX (idx_orders_customer_date)
WHERE customer_id = 123 AND order_date > '2023-01-01';
```

### Partitioned Table Queries

For partitioned tables, ensure queries include the partition key for better performance:

```sql
-- Create a partitioned table
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

-- Efficient partitioned table query (includes partition key)
SELECT * FROM sales
WHERE sale_date BETWEEN '2023-01-01' AND '2023-01-31'
AND customer_id = 456;

-- View partition information
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

## Real-World Application Scenarios

### Scenario 1: Sales Data Analysis

Analyze sales trends over the past 12 months:

```sql
-- Monthly sales statistics
SELECT
  DATE_FORMAT(order_date, '%Y-%m') AS month,
  SUM(total_amount) AS monthly_sales,
  COUNT(DISTINCT customer_id) AS unique_customers,
  SUM(total_amount) / COUNT(DISTINCT customer_id) AS avg_per_customer
FROM orders
WHERE order_date >= DATE_SUB(CURRENT_DATE, INTERVAL 12 MONTH)
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY month;

-- Calculate year-over-year growth
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

### Scenario 2: Customer Segmentation Analysis

Segment customers based on purchasing behavior:

```sql
-- RFM (Recency, Frequency, Monetary) analysis
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

### Scenario 3: Inventory Management

Analyze inventory status and restocking needs:

```sql
-- Identify products that need restocking
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

-- Calculate product turnover rate
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

## AI Interaction Examples

Here are some example conversations with AI using MySQL data:

**You**: Can you analyze which product categories had the highest sales in the past 6 months?

**AI**: I'll analyze that for you. Here are the product categories with the highest sales over the past 6 months:

```
Product Category | Sales Amount  | Order Count | Avg Order Amount
----------------|--------------|------------|----------------
Electronics     | $2,345,670    | 4,532      | $517.58
Home Goods      | $1,456,890    | 6,789      | $214.60
Clothing        | $987,450      | 8,901      | $110.94
Beauty & Care   | $876,540      | 5,678      | $154.38
Food & Beverage | $654,320      | 7,890      | $82.93
```

The Electronics category has the highest sales at $2,345,670, despite not having the highest order count. The Clothing category has the most orders, but a lower average order amount. This indicates that Electronics are high-value items, while Clothing represents high-frequency purchases.

**You**: Where are our customers primarily located? Can you sort by customer count?

**AI**: Based on data analysis, your customers are primarily distributed in these cities:

```
City       | Customer Count | Percentage | Avg Spending
-----------|---------------|------------|-------------
New York   | 4,532         | 18.6%      | $1,876
Los Angeles| 3,987         | 16.4%      | $2,043
Chicago    | 2,876         | 11.8%      | $1,654
Houston    | 2,543         | 10.5%      | $1,932
Phoenix    | 1,876         | 7.7%       | $1,432
Philadelphia| 1,654        | 6.8%       | $1,765
San Antonio| 1,432         | 5.9%       | $1,321
San Diego  | 1,321         | 5.4%       | $1,543
Other Cities| 4,123        | 16.9%      | $1,234
```

New York and Los Angeles have the highest number of customers, together accounting for 35% of your total customer base. Notably, Los Angeles customers have the highest average spending at $2,043, indicating significant growth potential in that market.