# Usage Guide

*English | [中文](../zh/usage.md) | [Français](../fr/usage.md) | [Español](../es/usage.md) | [العربية](../ar/usage.md) | [Русский](../ru/usage.md)*


*English | [中文](../zh/usage.md) | [Français](../fr/usage.md) | [Español](../es/usage.md) | [العربية](../ar/usage.md) | [Русский](../ru/usage.md)*

This document provides detailed instructions for using the MCP Database Utilities, helping you fully leverage its capabilities for data analysis with AI.

## Basic Workflow

The basic workflow for using MCP Database Utilities is as follows:

1. **Configure Database Connections**: Define your database connections in the `config.yaml` file
2. **Start the MCP Service**: Launch the service through your AI client configuration
3. **Interact with AI**: Ask questions about your databases using natural language
4. **View Results**: The AI will execute necessary queries and present results in an easy-to-understand format

## Available Tools

MCP Database Utilities provides several tools that your AI can use:

### dbutils-list-connections

Lists all available database connections defined in your configuration.

**Example Interaction**:

**You**: "What database connections do I have available?"

**AI**: "I'll check your available database connections. Here's what I found:

1. **postgres-db**
   - Type: PostgreSQL
   - Host: localhost
   - Database: analytics
   - User: analyst

2. **sqlite-db**
   - Type: SQLite
   - Path: /path/to/database.db

3. **mysql-db**
   - Type: MySQL
   - Host: db.example.com
   - Database: customer_data
   - User: reader"

### dbutils-list-tables

Lists all tables in the specified database.

**Example Interaction**:

**You**: "List all tables in my postgres database."

**AI**: "I'll check that for you. Here are the tables in your postgres database:
- customers
- products
- orders
- inventory
- employees"

### dbutils-run-query

Executes SQL queries on the specified database (SELECT operations only).

**Example Interaction**:

**You**: "Query the number of customers who registered in the last 30 days."

**AI**: "Let me check that for you. According to the data, there have been 42 new customer registrations in the last 30 days."

### dbutils-get-stats

Gets statistics about a table, such as row count, size, and column statistics.

**Example Interaction**:

**You**: "Get statistics for the products table."

**AI**: "Here are the statistics for the products table:
- Total rows: 1,245
- Table size: 2.3 MB
- Column statistics:
  * product_id: 1,245 unique values
  * category: 8 distinct categories
  * price: average $45.99, min $5.99, max $299.99"

### dbutils-list-constraints

Lists constraints for a table, such as primary keys, foreign keys, etc.

**Example Interaction**:

**You**: "Show constraints for the orders table."

**AI**: "The orders table has the following constraints:
- Primary key: order_id
- Foreign key: customer_id references customers(id)
- Foreign key: product_id references products(id)
- Check constraint: order_amount > 0"

### dbutils-explain-query

Gets the query execution plan and cost estimates.

**Example Interaction**:

**You**: "Explain the execution plan for this query: SELECT * FROM orders WHERE customer_id = 123"

**AI**: "The execution plan for this query is:
1. Index scan: using customer_id_idx index
2. Estimated cost: 12.5
3. Estimated rows: 8
4. Filter condition: customer_id = 123"

### dbutils-get-performance

Gets database performance metrics.

**Example Interaction**:

**You**: "Get performance metrics for the database."

**AI**: "Current database performance metrics:
- Query execution time: 45ms average
- Cache hit rate: 87%
- Active connections: 3
- Recent error rate: 0.2%"

### dbutils-analyze-query

Analyzes SQL query performance and provides optimization suggestions.

**Example Interaction**:

**You**: "Analyze this query: SELECT * FROM orders JOIN customers ON orders.customer_id = customers.id WHERE order_date > '2023-01-01'"

**AI**: "Query analysis results:
1. Performance issue: Using SELECT * retrieves unnecessary columns
2. Missing index: No index on order_date column
3. Optimization suggestions:
   - Select only needed columns
   - Add an index on the order_date column
   - Consider adding a LIMIT clause to restrict result count"

## Common Usage Scenarios

### 1. Data Exploration

**You**: "I want to understand my database structure."

**AI**: "I can help you explore your database structure. Let me list all tables, and then you can choose one to learn more about its structure."

**You**: "Okay, list all tables."

**AI**: "Your database contains the following tables:
- customers
- products
- orders
- inventory
- employees

Which table would you like to know more about?"

**You**: "Tell me about the structure of the customers table."

**AI**: "The customers table has the following structure:
- id (integer, primary key)
- name (varchar(100), not null)
- email (varchar(100), unique, not null)
- registration_date (date, not null)
- last_login (timestamp)
- status (enum: 'active', 'inactive', 'suspended')"

### 2. Data Analysis

**You**: "Analyze sales trends over the past 6 months."

**AI**: "I'll analyze sales trends over the past 6 months. Let me execute some queries..."

[AI executes multiple queries, analyzing sales data]

**AI**: "Based on the analysis of the past 6 months:
1. Total sales: $1,245,678, up 15% from the previous 6 months
2. Best-selling product: Product X, accounting for 23% of total sales
3. Peak sales periods: Fridays and Saturdays, accounting for 45% of total sales
4. Customer retention rate: 78%, up 5% from the previous 6 months"

### 3. Cross-Database Analysis

**You**: "Compare the users table structure between production and test databases."

**AI**: "I'll compare the users table structure between the two databases..."

[AI queries both databases for table structures]

**AI**: "Differences in the users table structure between production and test databases:
1. Production has an additional 'last_login_ip' column (varchar(45))
2. Test database's 'email' column doesn't have a unique constraint
3. Production has an additional index: idx_user_status
4. Test database is missing the foreign key constraint: fk_user_role"

## Best Practices

### Query Optimization

1. **Limit Result Set Size**: Use LIMIT clauses to restrict the number of rows returned
2. **Select Only Necessary Columns**: Avoid using SELECT *
3. **Use Indexed Columns**: Use columns with indexes in WHERE clauses
4. **Avoid Complex Calculations**: Move complex calculations to the application layer

### Security Recommendations

1. **Use Read-Only Accounts**: Create dedicated read-only database accounts for AI access
2. **Limit Table Access**: Grant access only to necessary tables
3. **Use SSL/TLS**: Enable encryption for remote database connections
4. **Rotate Passwords Regularly**: Change database passwords periodically

### Performance Optimization

1. **Connection Pool Configuration**: Adjust connection pool size based on your usage
2. **Query Timeout Settings**: Set reasonable query timeout durations
3. **Result Caching**: Consider caching for frequently queried data
4. **Monitor Performance**: Regularly check performance metrics to identify potential issues

## Troubleshooting

If you encounter issues during usage, refer to the troubleshooting section in the [Installation Guide](installation.md) or check the [Technical Documentation](technical/architecture.md) for more detailed information.