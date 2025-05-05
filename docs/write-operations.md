# 数据库写操作功能

MCP-DBUtils 2.0.0 版本引入了数据库写操作功能，允许在严格控制的条件下执行数据库写操作（INSERT、UPDATE、DELETE）。

## 功能特点

1. **默认只读**：所有数据库连接默认为只读模式，必须显式配置才能启用写操作。
2. **细粒度权限控制**：支持表级和操作级的细粒度权限控制。
3. **审计日志**：所有写操作都会记录详细的审计日志，包括操作类型、影响的表、SQL语句、执行结果等。
4. **交互式确认**：执行写操作时需要显式确认，防止意外修改数据。
5. **事务支持**：支持事务操作，确保数据一致性。

## 配置写操作

在配置文件中，可以为每个数据库连接单独配置写操作权限：

```yaml
connections:
  example_db:
    type: sqlite
    path: "data/example.db"
    # 启用写操作
    writable: true
    # 细粒度写权限控制
    write_permissions:
      # 默认策略：read_only 或 allow_all
      default_policy: "read_only"
      # 表级权限
      tables:
        users:
          # 允许的操作类型
          operations: ["INSERT", "UPDATE"]
        logs:
          operations: ["INSERT", "UPDATE", "DELETE"]
```

### 配置选项

- `writable`：是否允许写操作，默认为 `false`（只读）。
- `write_permissions`：细粒度写权限配置。
  - `default_policy`：默认策略，可选值为 `read_only`（只读）或 `allow_all`（允许所有写操作）。
  - `tables`：表级权限配置，可以为每个表指定允许的操作类型。

### 表名大小写处理

MCP-DBUtils 在处理表名时采用大小写不敏感的比较策略：

- 在配置文件中，表名可以使用任意大小写（如 `users`、`Users` 或 `USERS`）。
- 在 SQL 语句中，表名同样可以使用任意大小写。
- 系统会自动将表名转换为小写进行比较，确保大小写不影响权限检查。

例如，以下配置和 SQL 语句都能正确匹配：

```yaml
# 配置文件中使用小写表名
tables:
  users:
    operations: ["INSERT", "UPDATE"]
```

```sql
-- SQL 语句中使用大写表名，仍然能正确匹配权限
INSERT INTO USERS (id, name) VALUES (1, 'test');
```

## 使用写操作工具

MCP-DBUtils 提供了 `dbutils-execute-write` 工具用于执行写操作：

```json
{
  "name": "dbutils-execute-write",
  "arguments": {
    "connection": "example_db",
    "sql": "INSERT INTO logs (event, timestamp) VALUES ('event1', CURRENT_TIMESTAMP)",
    "confirmation": "CONFIRM_WRITE"
  }
}
```

### 参数说明

- `connection`：数据库连接名称。
- `sql`：SQL写操作语句（INSERT、UPDATE、DELETE）。
- `confirmation`：确认字符串，必须为 `CONFIRM_WRITE`。

## 审计日志

所有写操作都会记录详细的审计日志，可以通过 `dbutils-get-audit-logs` 工具查询：

```json
{
  "name": "dbutils-get-audit-logs",
  "arguments": {
    "connection": "example_db",
    "table": "logs",
    "operation_type": "INSERT",
    "status": "SUCCESS",
    "limit": 100
  }
}
```

### 参数说明

- `connection`：（可选）按数据库连接名称过滤。
- `table`：（可选）按表名过滤。
- `operation_type`：（可选）按操作类型过滤（INSERT、UPDATE、DELETE）。
- `status`：（可选）按操作状态过滤（SUCCESS、FAILED）。
- `limit`：（可选）返回记录数量限制，默认为 100。

### 审计日志配置

可以在配置文件中自定义审计日志行为：

```yaml
audit:
  enabled: true
  file_storage:
    enabled: true
    path: "logs/audit"
    max_file_size: 10485760  # 10MB
    backup_count: 10
  memory_buffer:
    size: 1000  # 内存中保存的最近日志记录数量
  content:
    sanitize_sql: true  # 是否对SQL语句进行脱敏处理
    include_user_context: true  # 是否包含用户上下文信息
```

## 安全最佳实践

1. **最小权限原则**：只为必要的表和操作启用写权限。
2. **定期审计**：定期检查审计日志，监控数据库写操作。
3. **使用事务**：对于多步骤操作，使用事务确保数据一致性。
4. **参数化查询**：使用参数化查询防止SQL注入攻击。
5. **备份数据**：在执行重要写操作前备份数据。

## 注意事项

- 写操作功能是一项高风险功能，请谨慎使用。
- 所有写操作都会记录审计日志，包括操作类型、影响的表、SQL语句、执行结果等。
- 执行写操作时需要显式确认，防止意外修改数据。
- 默认情况下，所有数据库连接都是只读的，必须显式配置才能启用写操作。
