# SQLite Examples

*English | [中文](../../zh/examples/sqlite-examples.md) | [Français](../../fr/examples/sqlite-examples.md) | [Español](../../es/examples/sqlite-examples.md) | [العربية](../../ar/examples/sqlite-examples.md) | [Русский](../../ru/examples/sqlite-examples.md)*

This document provides practical examples for working with SQLite databases using MCP Database Utilities.

## Basic Configuration

```yaml
connections:
  my-sqlite:
    type: sqlite
    path: /path/to/database.db
```

## Common Operations

### Listing Tables

**You**: "List all tables in my SQLite database."

**AI**: "Here are the tables in your SQLite database:
- users
- products
- orders
- categories"

### Viewing Table Structure

**You**: "Show me the structure of the users table."

**AI**: "The users table has the following structure:
- id (INTEGER, PRIMARY KEY)
- username (TEXT, NOT NULL)
- email (TEXT, NOT NULL, UNIQUE)
- created_at (TIMESTAMP)
- last_login (TIMESTAMP)
- status (TEXT)"

### Basic Query

**You**: "Show me the top 5 users by last login date."

**AI**: "Here are the top 5 users by last login date:

| id | username | email | last_login |
|----|----------|-------|------------|
| 42 | johndoe | john@example.com | 2023-11-25 14:32:15 |
| 17 | janedoe | jane@example.com | 2023-11-24 09:45:22 |
| 31 | bobsmith | bob@example.com | 2023-11-23 18:12:05 |
| 8 | alicejones | alice@example.com | 2023-11-22 11:30:47 |
| 53 | mikebrown | mike@example.com | 2023-11-21 16:08:33 |"

## Advanced Queries

### Joining Tables

**You**: "Show me the last 3 orders with user information."

**AI**: "Here are the last 3 orders with user information:

| order_id | order_date | username | email | total_amount |
|----------|------------|----------|-------|--------------|
| 1042 | 2023-11-25 | johndoe | john@example.com | $125.99 |
| 1041 | 2023-11-24 | alicejones | alice@example.com | $89.50 |
| 1040 | 2023-11-23 | bobsmith | bob@example.com | $212.75 |"

### Aggregate Functions

**You**: "What's the average order amount per category?"

**AI**: "Here's the average order amount per category:

| category | average_amount |
|----------|----------------|
| Electronics | $245.75 |
| Clothing | $78.30 |
| Books | $32.50 |
| Home & Kitchen | $124.90 |
| Sports & Outdoors | $156.25 |"

## Performance Analysis

### Query Execution Plan

**You**: "Explain the execution plan for: SELECT * FROM orders WHERE user_id = 42"

**AI**: "Execution plan for the query:
```
QUERY PLAN
------------------------------------------------------------
SEARCH TABLE orders USING INDEX idx_user_id (user_id=?)
```

This query uses the index `idx_user_id` to efficiently find orders for user_id 42."

### Table Statistics

**You**: "Get statistics for the orders table."

**AI**: "Statistics for the orders table:
- Row count: 1,245
- Size: 2.3 MB
- Indexes: 3 (primary key, idx_user_id, idx_order_date)
- Average row length: 1.9 KB"

## Working with SQLite-Specific Features

### Using FTS (Full-Text Search)

**You**: "Search for products containing 'wireless headphones'."

**AI**: "Here are products matching 'wireless headphones':

| product_id | name | description | price |
|------------|------|-------------|-------|
| 123 | Premium Wireless Headphones | Noise-cancelling wireless headphones with 30-hour battery life | $199.99 |
| 145 | Sport Wireless Headphones | Water-resistant wireless headphones for sports | $89.99 |
| 187 | Budget Wireless Headphones | Affordable wireless headphones with good sound quality | $49.99 |"

### Using JSON Functions

**You**: "Show me users with 'premium' in their preferences."

**AI**: "Here are users with 'premium' in their preferences:

| id | username | preferences |
|----|----------|-------------|
| 42 | johndoe | {\"subscription\": \"premium\", \"theme\": \"dark\"} |
| 17 | janedoe | {\"subscription\": \"premium\", \"theme\": \"light\"} |
| 53 | mikebrown | {\"subscription\": \"premium\", \"theme\": \"auto\"} |"

## Troubleshooting

### Common Issues

1. **File Not Found**
   - Ensure the path to your SQLite database file is correct
   - Check file permissions
   - Verify the file exists

2. **Locked Database**
   - SQLite allows only one writer at a time
   - Ensure no other process is writing to the database
   - Consider using WAL mode for better concurrency

3. **Performance Issues**
   - Add indexes for frequently queried columns
   - Use EXPLAIN QUERY PLAN to identify slow queries
   - Consider using prepared statements for repeated queries