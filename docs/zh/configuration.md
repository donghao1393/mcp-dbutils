# 配置指南

*[English](../en/configuration.md) | 中文 | [Français](../fr/configuration.md) | [Español](../es/configuration.md) | [العربية](../ar/configuration.md) | [Русский](../ru/configuration.md)*

本文档提供了MCP数据库工具的各种配置示例，从基础配置到高级场景，帮助您正确设置和优化数据库连接。

## 基础配置

### SQLite基础配置

SQLite是一种轻量级文件数据库，配置非常简单：

```yaml
connections:
  my-sqlite:
    type: sqlite
    path: /path/to/database.db
    # 可选：数据库加密密码
    password: optional_encryption_password
```

### PostgreSQL基础配置

标准的PostgreSQL连接配置：

```yaml
connections:
  my-postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: my_database
    user: postgres_user
    password: postgres_password
```

### MySQL基础配置

标准的MySQL连接配置：

```yaml
connections:
  my-mysql:
    type: mysql
    host: localhost
    port: 3306
    database: my_database
    user: mysql_user
    password: mysql_password
    charset: utf8mb4  # 推荐使用utf8mb4支持完整Unicode
```

## 多数据库配置

您可以在同一个配置文件中定义多个数据库连接：

```yaml
connections:
  # 开发环境SQLite数据库
  dev-db:
    type: sqlite
    path: /path/to/dev.db

  # 测试环境PostgreSQL数据库
  test-db:
    type: postgres
    host: test-postgres.example.com
    port: 5432
    dbname: test_db
    user: test_user
    password: test_pass

  # 生产环境MySQL数据库
  prod-db:
    type: mysql
    host: prod-mysql.example.com
    port: 3306
    database: prod_db
    user: prod_user
    password: prod_pass
    charset: utf8mb4
```

## 高级配置

### URL风格配置

除了使用标准配置属性外，您还可以使用数据库URL进行部分配置。最佳实践是将数据库连接结构放在URL中，但将敏感信息和特定参数分开配置：

**PostgreSQL URL配置（推荐方式）**：

```yaml
connections:
  # 使用URL配置PostgreSQL（最佳实践）
  postgres-url:
    type: postgres
    url: postgresql://host:5432/dbname
    user: postgres_user
    password: postgres_password
    # 其他参数在此配置
```

**MySQL URL配置（推荐方式）**：

```yaml
connections:
  # 使用URL配置MySQL（最佳实践）
  mysql-url:
    type: mysql
    url: mysql://host:3306/dbname
    user: mysql_user
    password: mysql_password
    charset: utf8mb4
```

**传统URL配置方式**（不推荐用于生产环境）：

虽然以下方式可行，但不建议在生产环境中使用，因为存在特殊字符解析错误的风险：

```yaml
connections:
  legacy-url:
    type: postgres
    url: postgresql://user:password@host:5432/dbname?param1=value1
    # 注意：不推荐在URL中包含凭据
```

**何时使用URL配置vs标准配置**：
- URL配置适合于：
  - 当您已经有现成的数据库连接结构
  - 需要在URL中包含特定连接参数
  - 从其他系统迁移而来的连接配置
- 标准配置适合于：
  - 更清晰的配置结构
  - 需要单独管理每个配置属性
  - 便于修改单个参数而不影响整体连接
  - 更好的安全性和可维护性

在任何情况下，都应避免将敏感信息（如用户名、密码）包含在URL中，而应单独在配置参数中提供。

### SSL/TLS安全连接

#### PostgreSQL SSL配置

**使用URL参数的SSL配置**：

```yaml
connections:
  pg-ssl-url:
    type: postgres
    url: postgresql://postgres.example.com:5432/secure_db?sslmode=verify-full&sslcert=/path/to/cert.pem&sslkey=/path/to/key.pem&sslrootcert=/path/to/root.crt
    user: secure_user
    password: secure_pass
```

**使用专属SSL配置部分**：

```yaml
connections:
  pg-ssl-full:
    type: postgres
    host: secure-postgres.example.com
    port: 5432
    dbname: secure_db
    user: secure_user
    password: secure_pass
    ssl:
      mode: verify-full  # 最安全的验证模式
      cert: /path/to/client-cert.pem  # 客户端证书
      key: /path/to/client-key.pem    # 客户端私钥
      root: /path/to/root.crt         # CA证书
```

**PostgreSQL SSL模式说明**：
- `disable`: 完全不使用SSL（不推荐用于生产环境）
- `require`: 使用SSL但不验证证书（仅加密，无身份验证）
- `verify-ca`: 验证服务器证书是由受信任的CA签名
- `verify-full`: 验证服务器证书和主机名匹配（最安全选项）

#### MySQL SSL配置

**使用URL参数的SSL配置**：

```yaml
connections:
  mysql-ssl-url:
    type: mysql
    url: mysql://mysql.example.com:3306/secure_db?ssl-mode=verify_identity&ssl-ca=/path/to/ca.pem&ssl-cert=/path/to/client-cert.pem&ssl-key=/path/to/client-key.pem
    user: secure_user
    password: secure_pass
```

**使用专属SSL配置部分**：

```yaml
connections:
  mysql-ssl-full:
    type: mysql
    host: secure-mysql.example.com
    port: 3306
    database: secure_db
    user: secure_user
    password: secure_pass
    charset: utf8mb4
    ssl:
      mode: verify_identity  # 最安全的验证模式
      ca: /path/to/ca.pem         # CA证书
      cert: /path/to/client-cert.pem  # 客户端证书
      key: /path/to/client-key.pem    # 客户端私钥
```

**MySQL SSL模式说明**：
- `disabled`: 不使用SSL（不推荐用于生产环境）
- `preferred`: 如果可用就使用SSL，否则使用非加密连接
- `required`: 必须使用SSL，但不验证服务器证书
- `verify_ca`: 验证服务器证书是由受信任的CA签名
- `verify_identity`: 验证服务器证书和主机名匹配（最安全选项）

### SQLite高级配置

**使用URI参数**：

```yaml
connections:
  sqlite-advanced:
    type: sqlite
    path: /path/to/db.sqlite?mode=ro&cache=shared&immutable=1
```

**常用SQLite URI参数**：
- `mode=ro`: 只读模式（安全选项）
- `cache=shared`: 共享缓存模式，提高多线程性能
- `immutable=1`: 标记数据库为不可变，提高性能
- `nolock=1`: 禁用文件锁定（仅当确定没有其他连接时使用）

## Docker环境特殊配置

在Docker容器中运行时，连接到主机上的数据库需要特殊配置：

### 连接主机上的PostgreSQL/MySQL

**在macOS/Windows上**：
使用特殊主机名`host.docker.internal`来访问Docker主机：

```yaml
connections:
  docker-postgres:
    type: postgres
    host: host.docker.internal  # 特殊DNS名称指向Docker主机
    port: 5432
    dbname: my_database
    user: postgres_user
    password: postgres_password
```

**在Linux上**：
使用Docker网桥IP或使用host网络模式：

```yaml
connections:
  docker-mysql:
    type: mysql
    host: 172.17.0.1  # Docker默认网桥IP，指向主机
    port: 3306
    database: my_database
    user: mysql_user
    password: mysql_password
```

或者使用`--network="host"`启动Docker容器，然后使用`localhost`作为主机名。

### SQLite映射

对于SQLite，需要将数据库文件映射到容器中：

```bash
docker run -i --rm \
  -v /path/to/config.yaml:/app/config.yaml \
  -v /path/to/database.db:/app/database.db \
  mcp/dbutils --config /app/config.yaml
```

然后在配置中指向映射的路径：

```yaml
connections:
  docker-sqlite:
    type: sqlite
    path: /app/database.db  # 容器内的路径，而非主机路径
```

## 常见配置场景

### 多环境管理

一种良好实践是为不同环境使用清晰的命名约定：

```yaml
connections:
  # 开发环境
  dev-postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: dev_db
    user: dev_user
    password: dev_pass

  # 测试环境
  test-postgres:
    type: postgres
    host: test-server.example.com
    port: 5432
    dbname: test_db
    user: test_user
    password: test_pass

  # 生产环境
  prod-postgres:
    type: postgres
    host: prod-db.example.com
    port: 5432
    dbname: prod_db
    user: prod_user
    password: prod_pass
    ssl:
      mode: verify-full
      cert: /path/to/cert.pem
      key: /path/to/key.pem
      root: /path/to/root.crt
```

### 只读与分析专用配置

对于数据分析场景，建议使用只读账户和优化的配置：

```yaml
connections:
  analytics-mysql:
    type: mysql
    host: analytics-db.example.com
    port: 3306
    database: analytics
    user: analytics_readonly  # 使用只读权限账户
    password: readonly_pass
    charset: utf8mb4
    # 设置较长的超时时间，适合数据分析
```

## 故障排除提示

如果连接配置无法工作，请尝试：

1. **验证基本连接**：使用数据库原生客户端验证连接是否可行
2. **检查网络连接**：确保网络端口开放，防火墙允许访问
3. **验证凭据**：确认用户名和密码正确
4. **路径问题**：对于SQLite，确保路径存在且有读取权限
5. **SSL错误**：检查证书路径和权限，验证证书是否过期