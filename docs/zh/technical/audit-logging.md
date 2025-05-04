# 数据库写操作审计日志系统

## 1. 概述

审计日志系统是数据库写操作功能的核心安全组件，负责记录所有写操作的详细信息，以便于追踪、审计和问题排查。本文档详细介绍审计日志系统的设计、实现和使用方法。

## 2. 设计目标

- **完整记录**：记录所有写操作的详细信息
- **不可篡改**：确保日志记录不可被修改或删除
- **易于访问**：提供多种方式访问和查询日志
- **性能影响小**：最小化对数据库操作性能的影响
- **安全存储**：保护日志数据的安全性和隐私性

## 3. 日志内容

每条审计日志记录包含以下信息：

| 字段 | 类型 | 描述 | 示例 |
|-----|-----|------|-----|
| `timestamp` | DateTime | 操作时间戳 | `2025-05-01 10:15:30.123` |
| `connection_name` | String | 数据库连接名称 | `postgres_example` |
| `table_name` | String | 操作的表名 | `users` |
| `operation_type` | Enum | 操作类型 | `INSERT`, `UPDATE`, `DELETE` |
| `sql_statement` | String | SQL语句（可能脱敏） | `INSERT INTO users (name, email) VALUES (?, ?)` |
| `affected_rows` | Integer | 影响的行数 | `5` |
| `status` | Enum | 操作结果 | `SUCCESS`, `FAILED` |
| `error_message` | String | 错误信息（如果失败） | `Foreign key constraint failed` |
| `execution_time` | Float | 执行时间（毫秒） | `15.3` |
| `user_context` | String | 用户上下文（如果可用） | `session_123` |

## 4. 存储机制

审计日志采用多级存储机制，确保数据的可靠性和可访问性：

### 4.1 内存缓冲

- 最新的日志记录保存在内存缓冲区中
- 缓冲区大小可配置，默认保存最近1000条记录
- 提供快速访问最近操作的能力

### 4.2 文件存储

- 日志记录定期写入本地文件系统
- 使用滚动日志文件，按日期或大小分割
- 文件格式为JSON，便于解析和查询
- 默认路径为`logs/audit/`目录

### 4.3 数据库存储（可选）

- 可选配置将日志记录存储到单独的数据库中
- 支持关系型数据库（SQLite、MySQL、PostgreSQL）
- 提供高级查询和分析能力

## 5. 访问机制

审计日志提供多种访问方式：

### 5.1 MCP资源

通过MCP资源端点访问审计日志：

```
dbutils://audit-logs/{connection_name}
dbutils://audit-logs/{connection_name}/{table_name}
```

支持以下查询参数：
- `start_time`: 开始时间（ISO 8601格式）
- `end_time`: 结束时间（ISO 8601格式）
- `operation_type`: 操作类型（INSERT/UPDATE/DELETE）
- `status`: 操作状态（SUCCESS/FAILED）
- `limit`: 返回记录数量限制

### 5.2 API接口

提供编程接口访问审计日志：

```python
# 获取连接的审计日志
logs = audit_logger.get_logs(connection_name, 
                            start_time=None, 
                            end_time=None, 
                            operation_type=None, 
                            status=None, 
                            limit=100)

# 获取表的审计日志
logs = audit_logger.get_table_logs(connection_name, 
                                  table_name, 
                                  start_time=None, 
                                  end_time=None, 
                                  operation_type=None, 
                                  status=None, 
                                  limit=100)
```

### 5.3 日志文件

直接访问日志文件：

```
logs/audit/dbutils-audit-{date}.json
```

## 6. 实现细节

### 6.1 日志记录流程

```python
def log_write_operation(connection_name, table_name, operation_type, sql, start_time):
    """记录写操作到审计日志"""
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds() * 1000
    
    # 创建日志记录
    log_entry = {
        "timestamp": end_time.isoformat(),
        "connection_name": connection_name,
        "table_name": table_name,
        "operation_type": operation_type,
        "sql_statement": sanitize_sql(sql),
        "affected_rows": get_affected_rows(),
        "status": "SUCCESS",
        "execution_time": execution_time,
        "user_context": get_user_context()
    }
    
    # 添加到内存缓冲
    memory_buffer.append(log_entry)
    
    # 写入文件
    write_to_file(log_entry)
    
    # 写入数据库（如果配置）
    if db_storage_enabled:
        write_to_database(log_entry)
```

### 6.2 SQL语句脱敏

为了保护敏感数据，SQL语句在记录前会进行脱敏处理：

```python
def sanitize_sql(sql):
    """对SQL语句进行脱敏处理"""
    # 替换VALUES子句中的具体值
    sanitized = re.sub(r"VALUES\s*\((.*?)\)", "VALUES (?)", sql, flags=re.IGNORECASE)
    
    # 替换WHERE子句中的具体值
    sanitized = re.sub(r"(WHERE\s+\w+\s*=\s*)('[^']*'|\d+)", r"\1?", sanitized, flags=re.IGNORECASE)
    
    return sanitized
```

### 6.3 日志轮转

文件日志采用轮转机制，防止单个文件过大：

```python
def setup_file_logger():
    """设置文件日志记录器"""
    log_dir = "logs/audit"
    os.makedirs(log_dir, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        f"{log_dir}/dbutils-audit.json",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    
    return file_handler
```

## 7. 配置选项

审计日志系统提供以下配置选项：

```yaml
audit_logging:
  # 启用/禁用审计日志
  enabled: true
  
  # 内存缓冲设置
  memory_buffer:
    size: 1000  # 缓冲区大小
  
  # 文件存储设置
  file_storage:
    enabled: true
    path: "logs/audit"
    max_file_size: 10485760  # 10MB
    backup_count: 10
  
  # 数据库存储设置
  database_storage:
    enabled: false
    connection: "audit_db"  # 使用配置中定义的连接
  
  # 日志内容设置
  content:
    sanitize_sql: true  # 是否脱敏SQL
    include_user_context: true  # 是否包含用户上下文
```

## 8. 安全考虑

### 8.1 日志保护

为保护审计日志的安全性，建议采取以下措施：

1. **文件权限**：
   - 设置适当的文件系统权限，限制日志文件的访问
   - 只允许必要的用户和进程访问日志目录

2. **加密**：
   - 考虑对敏感日志内容进行加密
   - 使用安全的加密算法和密钥管理

3. **备份**：
   - 定期备份审计日志
   - 将备份存储在安全的位置

### 8.2 隐私保护

为保护用户隐私，审计日志系统采取以下措施：

1. **数据脱敏**：
   - SQL语句中的具体值会被替换为占位符
   - 敏感字段（如密码）不会被记录

2. **访问控制**：
   - 限制对审计日志的访问
   - 实施基于角色的访问控制

## 9. 性能优化

为最小化审计日志对系统性能的影响，采取以下优化措施：

1. **异步记录**：
   - 日志写入操作在后台线程中异步执行
   - 不阻塞主要数据库操作

2. **批量写入**：
   - 多条日志记录批量写入文件或数据库
   - 减少I/O操作次数

3. **缓冲策略**：
   - 使用内存缓冲区暂存日志记录
   - 定期刷新到持久存储

## 10. 使用示例

### 10.1 查询最近的写操作

```
资源: dbutils://audit-logs/postgres_example?limit=10
```

### 10.2 查询特定表的操作

```
资源: dbutils://audit-logs/postgres_example/users?operation_type=INSERT
```

### 10.3 查询特定时间范围的操作

```
资源: dbutils://audit-logs/postgres_example?start_time=2025-05-01T00:00:00&end_time=2025-05-02T00:00:00
```

### 10.4 查询失败的操作

```
资源: dbutils://audit-logs/postgres_example?status=FAILED
```

## 11. 故障排查

### 11.1 常见问题

| 问题 | 可能的原因 | 解决方案 |
|-----|-----------|---------|
| 日志未记录 | 审计日志系统未启用 | 检查配置中的`audit_logging.enabled`设置 |
| 日志文件未创建 | 文件存储路径权限问题 | 检查日志目录的访问权限 |
| 日志内容不完整 | 内存缓冲区溢出 | 增加内存缓冲区大小或减少刷新间隔 |
| 日志查询性能差 | 日志文件过大或过多 | 优化查询参数，限制返回结果数量 |

### 11.2 日志分析工具

为便于分析审计日志，可以使用以下工具：

1. **内置查询**：
   - 使用MCP资源端点的查询参数
   - 支持基本的过滤和排序

2. **外部工具**：
   - 使用jq等工具分析JSON格式的日志文件
   - 导入到数据分析工具进行高级分析

## 12. 未来扩展

审计日志系统计划的未来扩展：

1. **高级分析**：
   - 添加统计和趋势分析功能
   - 支持异常检测和警报

2. **集成**：
   - 与外部日志管理系统集成
   - 支持SIEM（安全信息和事件管理）系统

3. **可视化**：
   - 提供日志数据的可视化界面
   - 支持交互式查询和报告
