# 数据库写操作功能设计

## 1. 概述

MCP数据库工具目前仅支持只读操作，为了增强功能灵活性，我们计划添加可选的数据库写操作支持。该功能将默认保持禁用状态，只有在用户通过配置文件明确启用后才会激活。

## 2. 设计目标

- **安全优先**：默认禁用写操作，需要明确配置才能启用
- **细粒度控制**：支持表级和操作级的权限控制
- **审计追踪**：记录所有写操作，便于审计和问题排查
- **用户友好**：提供清晰的配置方式和文档
- **向后兼容**：现有的只读功能不受影响

## 3. 安全模型

安全模型基于以下几个层次的保护：

### 3.1 连接级权限

每个数据库连接默认为只读模式。要启用写操作，必须在配置文件中明确设置`writable: true`。

```yaml
connections:
  example_db:
    type: postgres
    # 其他连接信息...
    writable: true  # 明确启用写操作
```

### 3.2 表级权限

对于启用了写操作的连接，可以进一步限制哪些表允许写操作：

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

如果未指定表级权限，则默认策略由`default_policy`决定：

```yaml
write_permissions:
  default_policy: read_only  # 或 allow_all
```

### 3.3 操作级权限

对于每个允许写操作的表，可以指定允许的操作类型（INSERT、UPDATE、DELETE）：

```yaml
tables:
  users:
    operations: [INSERT, UPDATE]  # 只允许插入和更新，不允许删除
```

如果未指定操作级权限，则默认允许所有写操作（INSERT、UPDATE、DELETE）。

## 4. 审计日志

所有写操作都将被记录到审计日志中，包括以下信息：

- 操作时间戳
- 连接名称
- 表名
- 操作类型（INSERT/UPDATE/DELETE）
- SQL语句（可能会脱敏）
- 影响的行数
- 操作结果（成功/失败）

审计日志将通过以下方式提供访问：

1. **MCP资源**：通过`dbutils://audit-logs/{connection_name}`资源URI访问
2. **日志文件**：写入到本地日志文件
3. **API**：提供编程接口访问审计日志

## 5. 配置格式

完整的配置格式示例：

```yaml
connections:
  sqlite_example:
    type: sqlite
    database: ":memory:"
    # 未指定writable，默认为false（只读）
    
  postgres_example:
    type: postgres
    host: localhost
    port: 5432
    database: mydb
    user: postgres
    password: ******
    writable: true  # 启用写操作
    
    # 细粒度权限控制（可选）
    write_permissions:
      # 表级权限
      tables:
        users:
          operations: [INSERT, UPDATE]  # 操作级权限
        logs:
          operations: [INSERT]
        temp_data:
          operations: [INSERT, UPDATE, DELETE]
      
      # 默认策略（可选，默认为read_only）
      default_policy: read_only  # 或 allow_all
```

## 6. API设计

### 6.1 新增工具

添加以下MCP工具：

```python
types.Tool(
    name="dbutils-execute-write",
    description="执行数据库写操作（INSERT、UPDATE、DELETE）。仅适用于配置了writable=true的连接。所有操作都会被记录到审计日志中。",
    inputSchema={
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "description": "数据库连接名称",
            },
            "sql": {
                "type": "string",
                "description": "SQL写操作语句（INSERT、UPDATE、DELETE）",
            },
            "confirmation": {
                "type": "string",
                "description": "输入'CONFIRM_WRITE'确认执行写操作",
            },
        },
        "required": ["connection", "sql", "confirmation"],
    },
)
```

### 6.2 新增资源

添加以下MCP资源：

```python
@mcp.resource("dbutils://audit-logs/{connection_name}")
def get_audit_logs(connection_name: str) -> str:
    """获取指定连接的审计日志"""
    logs = audit_logger.get_logs(connection_name)
    return format_logs(logs)

@mcp.resource("dbutils://audit-logs/{connection_name}/{table_name}")
def get_table_audit_logs(connection_name: str, table_name: str) -> str:
    """获取指定表的审计日志"""
    logs = audit_logger.get_logs(connection_name, table_name)
    return format_logs(logs)
```

## 7. 实现计划

1. **配置解析**：
   - 在`config.py`中添加对新配置项的解析
   - 确保默认值为安全的只读模式

2. **基础类扩展**：
   - 在`base.py`中扩展`DatabaseHandler`类，添加写操作相关方法
   - 添加权限检查逻辑

3. **数据库特定实现**：
   - 在各数据库模块中实现写操作方法
   - 处理数据库特定的事务管理

4. **审计日志系统**：
   - 实现审计日志记录和存储
   - 添加MCP资源端点

5. **新工具添加**：
   - 添加`dbutils-execute-write`工具
   - 实现权限检查和审计日志集成

## 8. 向后兼容性

这是一个breaking change，因为它改变了项目的核心安全模型（从"只读"到"可配置读写"）。我们将：

1. **版本号升级**：按照语义化版本规范，这应该是一个主版本号升级（例如从1.x.x到2.0.0）

2. **明确的更新日志**：
   ```markdown
   # 2.0.0 (2025-XX-XX)
   
   ## Breaking Changes
   
   - 添加了可选的数据库写入功能。默认行为保持不变（只读），但现在可以通过配置启用写操作。
   - 新增了写操作相关的配置选项和工具。
   ```

3. **迁移指南**：提供从只读版本迁移到新版本的详细指南，强调安全配置的重要性

## 9. 安全考虑

1. **明确的文档警告**：
   - 在文档中明确说明启用写操作的风险
   - 提供最佳实践建议

2. **沙箱环境**：
   - 建议用户在生产环境中使用只读连接
   - 写操作最好用于开发或测试环境

3. **权限最小化**：
   - 建议使用有限权限的数据库用户
   - 只授予必要的表和操作权限
