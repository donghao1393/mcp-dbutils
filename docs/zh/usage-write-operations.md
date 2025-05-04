# 数据库写操作使用指南

本文档详细介绍如何使用MCP数据库工具的写操作功能。在使用写操作功能前，请确保您已经正确配置了数据库连接的写权限。如果您尚未配置，请参阅[数据库写操作配置指南](./configuration-write-operations.md)。

> ⚠️ **安全警告**：数据库写操作可能导致数据丢失或损坏。请谨慎使用，并确保您了解相关风险。建议在执行写操作前备份重要数据。

## 1. 写操作工具概述

MCP数据库工具提供了`dbutils-execute-write`工具，用于执行数据库写操作（INSERT、UPDATE、DELETE）。该工具仅适用于配置了`writable: true`的数据库连接。

工具定义：

```json
{
  "name": "dbutils-execute-write",
  "description": "执行数据库写操作（INSERT、UPDATE、DELETE）。仅适用于配置了writable=true的连接。所有操作都会被记录到审计日志中。",
  "inputSchema": {
    "type": "object",
    "properties": {
      "connection": {
        "type": "string",
        "description": "数据库连接名称"
      },
      "sql": {
        "type": "string",
        "description": "SQL写操作语句（INSERT、UPDATE、DELETE）"
      },
      "confirmation": {
        "type": "string",
        "description": "输入'CONFIRM_WRITE'确认执行写操作"
      }
    },
    "required": ["connection", "sql", "confirmation"]
  }
}
```

## 2. 基本用法

### 2.1 插入数据

```
工具: dbutils-execute-write
参数:
  connection: "example_db"
  sql: "INSERT INTO users (name, email) VALUES ('张三', 'zhangsan@example.com')"
  confirmation: "CONFIRM_WRITE"
```

### 2.2 更新数据

```
工具: dbutils-execute-write
参数:
  connection: "example_db"
  sql: "UPDATE users SET email = 'new_email@example.com' WHERE id = 123"
  confirmation: "CONFIRM_WRITE"
```

### 2.3 删除数据

```
工具: dbutils-execute-write
参数:
  connection: "example_db"
  sql: "DELETE FROM temp_data WHERE created_at < '2025-01-01'"
  confirmation: "CONFIRM_WRITE"
```

## 3. 高级用法

### 3.1 批量操作

对于批量操作，建议使用数据库支持的批量语法，而不是多次调用工具：

```
工具: dbutils-execute-write
参数:
  connection: "example_db"
  sql: "INSERT INTO logs (event, timestamp) VALUES 
        ('event1', '2025-05-01 10:00:00'),
        ('event2', '2025-05-01 10:05:00'),
        ('event3', '2025-05-01 10:10:00')"
  confirmation: "CONFIRM_WRITE"
```

### 3.2 事务管理

目前，每个写操作都在单独的事务中执行。如果您需要在一个事务中执行多个操作，请使用数据库支持的事务语法：

**MySQL/PostgreSQL示例**：
```
工具: dbutils-execute-write
参数:
  connection: "example_db"
  sql: "BEGIN;
        INSERT INTO orders (customer_id, total) VALUES (123, 1000);
        INSERT INTO order_items (order_id, product_id, quantity) VALUES (LAST_INSERT_ID(), 456, 2);
        COMMIT;"
  confirmation: "CONFIRM_WRITE"
```

**SQLite示例**：
```
工具: dbutils-execute-write
参数:
  connection: "sqlite_db"
  sql: "BEGIN TRANSACTION;
        INSERT INTO orders (customer_id, total) VALUES (123, 1000);
        INSERT INTO order_items (order_id, product_id, quantity) VALUES (last_insert_rowid(), 456, 2);
        COMMIT;"
  confirmation: "CONFIRM_WRITE"
```

## 4. 审计日志

所有写操作都会被记录到审计日志中。您可以通过以下MCP资源访问审计日志：

### 4.1 查看连接的审计日志

```
资源: dbutils://audit-logs/{connection_name}
```

例如：
```
dbutils://audit-logs/example_db
```

### 4.2 查看特定表的审计日志

```
资源: dbutils://audit-logs/{connection_name}/{table_name}
```

例如：
```
dbutils://audit-logs/example_db/users
```

## 5. 最佳实践

### 5.1 安全建议

1. **验证SQL语句**：
   - 执行写操作前，先使用`dbutils-run-query`验证SELECT语句
   - 对于复杂的更新或删除操作，先使用WHERE子句测试影响范围

2. **限制影响范围**：
   - 使用WHERE子句限制更新或删除的范围
   - 考虑使用LIMIT子句限制影响的行数（如果数据库支持）

3. **备份重要数据**：
   - 在执行重要的写操作前备份数据
   - 使用事务确保操作的原子性

### 5.2 性能建议

1. **批量操作**：
   - 使用批量插入而不是多次单行插入
   - 对于大量数据，考虑分批处理

2. **索引考虑**：
   - 注意写操作对索引的影响
   - 大量写操作可能需要临时禁用索引（需要数据库管理员权限）

3. **事务大小**：
   - 避免在单个事务中处理过多数据
   - 对于大量数据，考虑分割为多个较小的事务

## 6. 故障排查

### 6.1 常见错误

| 错误消息 | 可能的原因 | 解决方案 |
|---------|-----------|---------|
| "Connection is not configured for write operations" | 连接未设置`writable: true` | 在配置文件中添加`writable: true` |
| "No permission to perform [操作] on table [表名]" | 表未被允许执行该操作 | 在配置中添加表和操作权限 |
| "Operation not confirmed" | 未提供正确的确认参数 | 确保`confirmation`参数为`"CONFIRM_WRITE"` |
| "Syntax error in SQL statement" | SQL语法错误 | 检查SQL语句的语法 |
| "Foreign key constraint failed" | 违反外键约束 | 检查相关表的数据完整性 |

### 6.2 调试技巧

1. **分析SQL**：
   - 使用`dbutils-explain-query`分析SQL执行计划
   - 使用`dbutils-analyze-query`获取性能建议

2. **检查审计日志**：
   - 查看审计日志了解操作历史
   - 分析失败操作的详细信息

3. **测试环境**：
   - 在测试环境中先验证复杂操作
   - 使用小数据集测试后再应用到大数据集

## 7. 示例场景

### 7.1 用户管理系统

**创建用户**：
```
工具: dbutils-execute-write
参数:
  connection: "user_db"
  sql: "INSERT INTO users (username, email, created_at) VALUES ('newuser', 'newuser@example.com', CURRENT_TIMESTAMP)"
  confirmation: "CONFIRM_WRITE"
```

**更新用户信息**：
```
工具: dbutils-execute-write
参数:
  connection: "user_db"
  sql: "UPDATE users SET email = 'updated@example.com', last_updated = CURRENT_TIMESTAMP WHERE username = 'newuser'"
  confirmation: "CONFIRM_WRITE"
```

**删除非活跃用户**：
```
工具: dbutils-execute-write
参数:
  connection: "user_db"
  sql: "DELETE FROM users WHERE last_login < DATE_SUB(CURRENT_DATE, INTERVAL 1 YEAR) AND status = 'inactive'"
  confirmation: "CONFIRM_WRITE"
```

### 7.2 日志系统

**记录事件**：
```
工具: dbutils-execute-write
参数:
  connection: "log_db"
  sql: "INSERT INTO system_logs (event_type, message, timestamp) VALUES ('LOGIN', 'User login successful', CURRENT_TIMESTAMP)"
  confirmation: "CONFIRM_WRITE"
```

**清理旧日志**：
```
工具: dbutils-execute-write
参数:
  connection: "log_db"
  sql: "DELETE FROM system_logs WHERE timestamp < DATE_SUB(CURRENT_DATE, INTERVAL 90 DAY)"
  confirmation: "CONFIRM_WRITE"
```

### 7.3 库存管理

**更新库存**：
```
工具: dbutils-execute-write
参数:
  connection: "inventory_db"
  sql: "UPDATE products SET stock_quantity = stock_quantity - 5 WHERE product_id = 1234"
  confirmation: "CONFIRM_WRITE"
```

**批量添加产品**：
```
工具: dbutils-execute-write
参数:
  connection: "inventory_db"
  sql: "INSERT INTO products (name, category, price, stock_quantity) VALUES 
        ('产品A', '电子', 199.99, 100),
        ('产品B', '电子', 299.99, 50),
        ('产品C', '家居', 99.99, 200)"
  confirmation: "CONFIRM_WRITE"
```

## 8. 相关资源

- [数据库写操作配置指南](./configuration-write-operations.md)
- [数据库写操作功能设计](./technical/write-operations-design.md)
- [安全架构](./technical/security.md)
- [审计日志指南](./technical/audit-logging.md)
