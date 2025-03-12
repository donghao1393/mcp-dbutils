# MCP 数据库服务

## 项目简介
MCP数据库服务是一个统一的数据库访问服务，支持多种数据库类型（PostgreSQL和SQLite）。它通过抽象层设计，为MCP服务器提供了简单、统一的数据库操作接口。

## 功能特性
- 统一的数据库访问接口
- 支持多个数据库配置
- 安全的只读查询执行
- 表结构和模式信息查询
- 通过MCP工具列出数据库表
- 智能的连接管理和资源清理
- 支持调试模式
- PostgreSQL的SSL/TLS连接支持

## 安装与配置

### 安装方式

#### 使用 uvx 安装（推荐）
不需要专门安装，直接使用 `uvx` 运行：
```bash
uvx mcp-dbutils --config /path/to/config.yaml
```

添加到 Claude 配置：
```json
"mcpServers": {
  "mcp-dbutils": {
    "command": "uvx",
    "args": [
      "mcp-dbutils",
      "--config",
      "/path/to/config.yaml"
    ],
    "env": {
      "MCP_DEBUG": "1"  // 可选：启用调试模式
    }
  }
}
```

#### 使用 pip 安装
```bash
pip install mcp-dbutils
```

添加到 Claude 配置：
```json
"mcpServers": {
  "mcp-dbutils": {
    "command": "python",
    "args": [
      "-m",
      "mcp_dbutils",
      "--config",
      "/path/to/config.yaml"
    ],
    "env": {
      "MCP_DEBUG": "1"  // 可选：启用调试模式
    }
  }
}
```

#### 使用 Docker 安装
```bash
docker run -i --rm \
  -v /path/to/config.yaml:/app/config.yaml \
  -v /path/to/sqlite.db:/app/sqlite.db \  # 可选：用于SQLite数据库
  -e MCP_DEBUG=1 \  # 可选：启用调试模式
  mcp/dbutils --config /app/config.yaml
```

添加到 Claude 配置：
```json
"mcpServers": {
  "mcp-dbutils": {
    "command": "docker",
    "args": [
      "run",
      "-i",
      "--rm",
      "-v",
      "/path/to/config.yaml:/app/config.yaml",
      "-v",
      "/path/to/sqlite.db:/app/sqlite.db",  // 可选：用于SQLite数据库
      "mcp/dbutils",
      "--config",
      "/app/config.yaml"
    ],
    "env": {
      "MCP_DEBUG": "1"  // 可选：启用调试模式
    }
  }
}
```

> **Docker数据库连接说明：**
> - SQLite数据库：使用 `-v /path/to/sqlite.db:/app/sqlite.db` 映射数据库文件
> - 主机上运行的PostgreSQL：
>   - Mac/Windows：配置中使用 `host.docker.internal`
>   - Linux：使用 `172.17.0.1`（docker0网络IP）或使用 `--network="host"` 运行

### 环境要求
- Python 3.10+
- PostgreSQL (可选)
- SQLite3 (可选)

### 配置文件
项目运行需要一个YAML格式的配置文件，通过 `--config` 参数指定路径。配置示例：

```yaml
connections:
  # SQLite配置示例
  dev-db:
    type: sqlite
    path: /path/to/dev.db
    # 密码是可选的
    password: 

  # PostgreSQL标准配置
  test-db:
    type: postgres
    host: postgres.example.com
    port: 5432
    dbname: test_db
    user: test_user
    password: test_pass

  # PostgreSQL URL配置（带SSL）
  prod-db:
    type: postgres
    url: postgresql://postgres.example.com:5432/prod-db?sslmode=verify-full
    user: prod_user
    password: prod_pass
    
  # PostgreSQL完整SSL配置示例
  secure-db:
    type: postgres
    host: secure-db.example.com
    port: 5432
    dbname: secure_db
    user: secure_user
    password: secure_pass
    ssl:
      mode: verify-full  # disable/require/verify-ca/verify-full
      cert: /path/to/client-cert.pem
      key: /path/to/client-key.pem
      root: /path/to/root.crt
```

PostgreSQL SSL配置选项：
1. 使用URL参数：
   ```
   postgresql://host:port/dbname?sslmode=verify-full&sslcert=/path/to/cert.pem
   ```
2. 使用专门的SSL配置部分：
   ```yaml
   ssl:
     mode: verify-full  # SSL验证模式
     cert: /path/to/cert.pem      # 客户端证书
     key: /path/to/key.pem        # 客户端私钥
     root: /path/to/root.crt      # CA证书
   ```

SSL模式：
- disable: 不使用SSL
- require: 使用SSL但不验证证书
- verify-ca: 验证服务器证书是由受信任的CA签名
- verify-full: 验证服务器证书和主机名匹配

SQLite配置选项：
1. 基本路径配置：
   ```yaml
   type: sqlite
   path: /path/to/db.sqlite
   password: optional_password  # 可选的加密密码
   ```
2. 使用URI参数：
   ```yaml
   type: sqlite
   path: /path/to/db.sqlite?mode=ro&cache=shared
   ```

### 调试模式
设置环境变量 `MCP_DEBUG=1` 启用调试模式，可以看到详细的日志输出。

[剩余的README内容保持不变...]
