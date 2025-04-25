# PostgreSQL Examples

*English | [中文](../../zh/examples/postgresql-examples.md) | [Français](../../fr/examples/postgresql-examples.md) | [Español](../../es/examples/postgresql-examples.md) | [العربية](../../ar/examples/postgresql-examples.md) | [Русский](../../ru/examples/postgresql-examples.md)*

This document provides practical examples for interacting with PostgreSQL databases using MCP Database Utilities. These examples demonstrate how to leverage PostgreSQL features for data analysis and query optimization.

## Basic Query Examples

### Listing All Tables

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

### Viewing Table Structure

```sql
SELECT column_name, data_type, character_maximum_length, is_nullable
FROM information_schema.columns
WHERE table_name = 'customers'
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

## PostgreSQL-Specific Features

### JSON Data Queries

PostgreSQL provides powerful JSON processing capabilities for directly querying and manipulating JSON data:

```sql
-- Query specific properties from JSON fields
SELECT
  id,
  name,
  preferences->>'theme' AS theme,
  preferences->>'language' AS language
FROM users;

-- Filter using JSON conditions
SELECT * FROM products
WHERE attributes->>'color' = 'red'
AND CAST(attributes->>'weight' AS INTEGER) < 100;

-- Using JSON arrays
SELECT * FROM orders
WHERE items @> '[{"product_id": 123}]'::jsonb;
```

### Full-Text Search

PostgreSQL's full-text search capabilities efficiently search text content:

```sql
-- Create full-text search vector
SELECT to_tsvector('english', description) FROM products;

-- Use full-text search query
SELECT title, description
FROM products
WHERE to_tsvector('english', description) @@ to_tsquery('english', 'comfortable & durable');

-- Full-text search with ranking
SELECT title, description,
       ts_rank(to_tsvector('english', description), to_tsquery('english', 'comfortable & durable')) AS rank
FROM products
WHERE to_tsvector('english', description) @@ to_tsquery('english', 'comfortable & durable')
ORDER BY rank DESC;
```

### Array Operations

PostgreSQL supports array data types that can be manipulated directly in SQL:

```sql
-- Query products with specific tags
SELECT * FROM products WHERE 'organic' = ANY(tags);

-- Array intersection
SELECT * FROM products WHERE tags && ARRAY['eco-friendly', 'sustainable'];

-- Expand arrays
SELECT id, unnest(tags) AS tag FROM products;

-- Array aggregation
SELECT category, array_agg(name) AS product_names
FROM products
GROUP BY category;
```

## Advanced Query Techniques

### Window Functions

Window functions perform calculations without changing the result set row count:

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

### Common Table Expressions (CTEs)

CTEs simplify complex queries:

```sql
-- Use CTE to find high-value customers
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

## Performance Optimization Tips

### Using EXPLAIN ANALYZE

Use `EXPLAIN ANALYZE` to view query plans and execution times to help optimize queries:

```sql
EXPLAIN ANALYZE
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
```

### Partitioned Table Queries

For partitioned tables, ensure queries include the partition key for better performance:

```sql
-- Efficient partitioned table query (includes partition key)
SELECT * FROM sales
WHERE sale_date BETWEEN '2023-01-01' AND '2023-01-31'
AND product_id = 456;
```

## Real-World Application Scenarios

### Scenario 1: Sales Data Analysis

Analyze sales trends over the past 12 months:

```sql
-- Monthly sales statistics
SELECT
  DATE_TRUNC('month', order_date) AS month,
  SUM(amount) AS monthly_sales,
  COUNT(DISTINCT customer_id) AS unique_customers,
  SUM(amount) / COUNT(DISTINCT customer_id) AS avg_per_customer
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;

-- Calculate year-over-year growth
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

### Scenario 2: Customer Segmentation Analysis

Segment customers based on purchasing behavior:

```sql
-- RFM (Recency, Frequency, Monetary) analysis
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
```

## AI Interaction Examples

Here are some example conversations with AI using PostgreSQL data:

**You**: Can you analyze which products had the fastest sales growth over the past 6 months?

**AI**: I'll analyze that for you. Here are the products with the fastest sales growth over the past 6 months:

```
Product Name      | Sales 6 Months Ago | Current Sales | Growth Percentage
------------------|-------------------|--------------|------------------
Smart Watch Pro   | $125,430          | $356,780     | 184.4%
Wireless Earbuds X3| $89,670          | $213,450     | 138.0%
Smart Home Kit    | $56,890           | $132,670     | 133.2%
Ultra-Thin Laptop | $432,780          | $876,540     | 102.5%
Health Monitor Band| $78,340          | $145,670     | 86.0%
```

The Smart Watch Pro shows the most significant sales growth at 184.4%. Wireless earbuds and smart home products also performed exceptionally well. This may be related to recent marketing campaigns and product upgrades.

**You**: Which cities do our high-value customers primarily come from? What's their average spending?

**AI**: Based on data analysis, your high-value customers (those spending over $10,000 annually) are primarily distributed in these cities:

```
City      | High-Value Customer Count | Average Annual Spending
----------|--------------------------|----------------------
New York  | 342                      | $18,765
San Francisco | 287                  | $19,432
Los Angeles | 213                    | $17,890
Chicago   | 176                      | $16,543
Seattle   | 124                      | $15,876
```

While San Francisco doesn't have the highest number of high-value customers, they have the highest average spending at $19,432. New York has the most high-value customers with 342. This data can help you develop more targeted marketing strategies and customer service plans.
