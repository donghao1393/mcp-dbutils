# 数据库写操作配置指南

本文档详细介绍如何配置MCP数据库工具的写操作功能。默认情况下，所有数据库连接都是只读的，需要通过明确的配置才能启用写操作。

> ⚠️ **安全警告**：启用数据库写操作可能导致数据丢失或损坏。请确保您了解相关风险，并采取适当的安全措施。建议在生产环境中保持只读模式，或使用严格的权限控制。

## 1. 基本配置

要启用数据库写操作，需要在连接配置中添加`writable: true`参数：

```yaml
connections:
  example_db:
    type: postgres
    host: localhost
    port: 5432
    database: mydb
    user: postgres
    password: secret
    writable: true  # 启用写操作
```

如果未指定`writable`参数，或设置为`false`，则连接将保持只读模式：

```yaml
connections:
  readonly_db:
    type: mysql
    host: localhost
    port: 3306
    database: mydb
    user: root
    password: secret
    # 未指定writable，默认为false（只读）
```

## 2. 细粒度权限控制

对于启用了写操作的连接，您可以进一步控制哪些表允许哪些写操作。

### 2.1 表级权限

通过`write_permissions.tables`配置特定表的写权限：

```yaml
connections:
  example_db:
    # 基本连接信息...
    writable: true
    write_permissions:
      tables:
        users:  # 允许对users表进行写操作
          operations: [INSERT, UPDATE]
        logs:   # 允许对logs表进行写操作
          operations: [INSERT]
```

在上面的例子中：
- `users`表允许INSERT和UPDATE操作，但不允许DELETE
- `logs`表只允许INSERT操作
- 未明确指定的表将遵循默认策略

### 2.2 默认策略

通过`default_policy`设置未明确指定的表的默认权限策略：

```yaml
write_permissions:
  default_policy: read_only  # 未指定的表默认只读
```

可选的默认策略值：
- `read_only`：未明确指定的表默认只读（推荐）
- `allow_all`：未明确指定的表默认允许所有写操作

如果未设置`default_policy`，则默认为`read_only`。

### 2.3 操作级权限

对于每个允许写操作的表，可以指定允许的操作类型：

```yaml
tables:
  users:
    operations: [INSERT, UPDATE]  # 只允许插入和更新，不允许删除
```

可用的操作类型：
- `INSERT`：允许插入新数据
- `UPDATE`：允许更新现有数据
- `DELETE`：允许删除数据

如果未指定`operations`，则默认允许所有写操作（INSERT、UPDATE、DELETE）。

### 2.4 表名大小写处理

MCP-DBUtils 在处理表名时采用大小写不敏感的比较策略：

- 在配置文件中，表名可以使用任意大小写（如 `users`、`Users` 或 `USERS`）。
- 在 SQL 语句中，表名同样可以使用任意大小写。
- 系统会自动将表名转换为小写进行比较，确保大小写不影响权限检查。

例如，以下配置和 SQL 语句都能正确匹配：

```yaml
# 配置文件中使用小写表名
tables:
  users:
    operations: [INSERT, UPDATE]
```

```sql
-- SQL 语句中使用大写表名，仍然能正确匹配权限
INSERT INTO USERS (id, name) VALUES (1, 'test');
```

## 3. 完整配置示例

以下是一个包含多种配置场景的完整示例：

```yaml
connections:
  # 示例1：只读连接（默认）
  readonly_sqlite:
    type: sqlite
    database: ":memory:"
    # 未指定writable，默认为false（只读）

  # 示例2：可写连接，无细粒度控制
  simple_writable_mysql:
    type: mysql
    host: localhost
    port: 3306
    database: simple_db
    user: root
    password: secret
    writable: true
    # 未指定write_permissions，所有表都可写

  # 示例3：可写连接，有表级和操作级控制
  controlled_postgres:
    type: postgres
    host: localhost
    port: 5432
    database: controlled_db
    user: postgres
    password: postgres
    writable: true

    write_permissions:
      # 表级权限
      tables:
        users:
          operations: [INSERT, UPDATE]  # 只允许插入和更新
        logs:
          operations: [INSERT]  # 只允许插入
        temp_data:
          operations: [INSERT, UPDATE, DELETE]  # 允许所有写操作

      # 默认策略
      default_policy: read_only  # 未指定的表默认只读

  # 示例4：可写连接，只有默认策略
  all_writable_postgres:
    type: postgres
    host: localhost
    port: 5432
    database: all_writable_db
    user: postgres
    password: postgres
    writable: true

    write_permissions:
      default_policy: allow_all  # 所有表默认可写
```

## 4. 最佳实践

### 4.1 安全建议

1. **默认只读**：
   - 除非明确需要写操作，否则保持默认的只读模式
   - 生产环境建议使用只读连接

2. **最小权限原则**：
   - 只为必要的表启用写操作
   - 只允许必要的操作类型（如只允许INSERT而不允许DELETE）

3. **数据库用户权限**：
   - 使用权限有限的数据库用户
   - 不要使用数据库管理员账户

4. **审计日志**：
   - 定期检查审计日志，监控写操作
   - 设置异常操作警报

### 4.2 配置建议

1. **明确配置**：
   - 总是明确设置`writable`参数，即使使用默认值
   - 明确设置`default_policy`，避免依赖默认行为

2. **分离环境**：
   - 为开发、测试和生产环境使用不同的配置文件
   - 生产环境配置应该更加严格

3. **注释配置**：
   - 为每个启用写操作的连接添加注释，说明原因
   - 记录配置更改的时间和负责人

## 5. 故障排查

### 5.1 常见问题

1. **写操作被拒绝**：
   - 检查连接是否设置了`writable: true`
   - 检查表是否在允许的表列表中
   - 检查操作类型是否被允许

2. **权限错误**：
   - 检查数据库用户是否有足够的权限
   - 检查数据库服务器的权限设置

3. **审计日志问题**：
   - 检查日志目录的写入权限
   - 检查磁盘空间是否充足

### 5.2 错误消息解释

| 错误消息 | 可能的原因 | 解决方案 |
|---------|-----------|---------|
| "Connection is not configured for write operations" | 连接未设置`writable: true` | 在配置文件中添加`writable: true` |
| "No permission to perform [操作] on table [表名]" | 表未被允许执行该操作 | 在`write_permissions.tables`中添加表和操作 |
| "Operation not confirmed" | 未提供正确的确认参数 | 在工具调用中添加`confirmation: "CONFIRM_WRITE"` |
| "No permission to perform [操作] on table [大写表名]" | SQL语句中使用了大写表名，但配置中使用小写表名 | 系统已支持大小写不敏感的表名比较，此问题在v1.0.1及以上版本已修复 |

## 6. 配置迁移

如果您从早期版本升级，需要注意以下几点：

1. 默认情况下，所有连接保持只读模式，与早期版本行为一致
2. 要启用写操作，需要明确添加新的配置参数
3. 建议在升级后检查所有配置文件，确保安全设置符合预期

## 7. 相关资源

- [数据库写操作功能设计](./technical/write-operations-design.md)
- [安全架构](./technical/security.md)
- [审计日志指南](./technical/audit-logging.md)
