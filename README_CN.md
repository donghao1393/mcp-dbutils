# MCP 数据库工具

<!-- 项目状态徽章 -->
[![构建状态](https://img.shields.io/github/workflow/status/donghao1393/mcp-dbutils/Quality%20Assurance?label=tests)](https://github.com/donghao1393/mcp-dbutils/actions)
[![覆盖率](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/donghao1393/bdd0a63ec2a816539ff8c136ceb41e48/raw/coverage.json)](https://github.com/donghao1393/mcp-dbutils/actions)
[![质量门禁状态](https://sonarcloud.io/api/project_badges/measure?project=donghao1393_mcp-dbutils&metric=alert_status)](https://sonarcloud.io/dashboard?id=donghao1393_mcp-dbutils)

<!-- 版本和安装徽章 -->
[![PyPI 版本](https://img.shields.io/pypi/v/mcp-dbutils)](https://pypi.org/project/mcp-dbutils/)
[![PyPI 下载量](https://img.shields.io/pypi/dm/mcp-dbutils)](https://pypi.org/project/mcp-dbutils/)
[![Smithery](https://smithery.ai/badge/@donghao1393/mcp-dbutils)](https://smithery.ai/server/@donghao1393/mcp-dbutils)

<!-- 技术规格徽章 -->
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![许可证](https://img.shields.io/github/license/donghao1393/mcp-dbutils)](LICENSE)
[![GitHub 星标](https://img.shields.io/github/stars/donghao1393/mcp-dbutils?style=social)](https://github.com/donghao1393/mcp-dbutils/stargazers)

[English](README.md) | [技术指南](docs/technical-guide.md)

## MCP 数据库工具是什么？

MCP 数据库工具是一个全能型 MCP 服务，使您的 AI 能够通过安全地访问多种类型的数据库（SQLite、MySQL、PostgreSQL 等）在统一的连接配置中进行数据分析。

可以将其视为 AI 系统和您的数据库之间的安全桥梁，允许 AI 读取和分析您的数据，而无需直接访问数据库或冒数据被修改的风险。

## 为什么使用 MCP 数据库工具？

- **通用 AI 支持**：适用于任何支持 MCP 协议的 AI 系统
- **多数据库支持**：使用相同的接口连接 SQLite、MySQL、PostgreSQL
- **安全数据访问**：只读操作确保您的数据不会被修改
- **简单配置**：单个 YAML 文件用于所有数据库连接
- **增强隐私**：您的数据保持本地，敏感信息自动受到保护
- **高级功能**：表格探索、架构分析和查询执行

## 开始使用

### 1. 快速安装

最简单的安装方式是通过 Smithery：

```bash
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

或使用 uvx（无需安装）：
```bash
uvx mcp-dbutils --config /path/to/config.yaml
```

或使用 pip：
```bash
pip install mcp-dbutils
```

或使用 Docker：
```bash
docker run -i --rm \
  -v /path/to/config.yaml:/app/config.yaml \
  -v /path/to/sqlite.db:/app/sqlite.db \  # 可选：用于SQLite数据库
  -e MCP_DEBUG=1 \  # 可选：启用调试模式
  mcp/dbutils --config /app/config.yaml
```

> **Docker数据库连接注意事项：**
> - 对于SQLite：使用 `-v /path/to/sqlite.db:/app/sqlite.db` 挂载数据库文件
> - 对于主机上运行的PostgreSQL：
>   - Mac/Windows：在配置中使用 `host.docker.internal` 作为主机
>   - Linux：使用 `172.17.0.1`（docker0 IP）或使用 `--network="host"` 运行

### 2. 简单配置

创建一个包含数据库信息的 config.yaml 文件：

```yaml
connections:
  my-sqlite:
    type: sqlite
    path: /path/to/my-database.db
    
  my-postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: my_database
    user: my_user
    password: my_password
```

### 3. 连接到您的 AI 系统

添加到您的 AI 系统的 MCP 配置中：

```json
"mcpServers": {
  "dbutils": {
    "command": "uvx",
    "args": [
      "mcp-dbutils",
      "--config",
      "/path/to/config.yaml"
    ]
  }
}
```

对于Docker安装：
```json
"mcpServers": {
  "dbutils": {
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
    ]
  }
}
```

### 4. 开始与您的 AI 一起使用

就是这样！现在您的 AI 可以：
- 列出数据库中的表
- 查看表结构
- 运行 SQL 查询分析您的数据
- 基于您的数据提供洞察

只需询问有关您数据的问题，AI 将使用连接帮助您找到答案。

## 交互示例

**您**："能否列出我的 my-postgres 数据库中的所有表？"

**AI**："我来为您查看。以下是您的 my-postgres 数据库中的表：
- customers（客户）
- products（产品）
- orders（订单）
- inventory（库存）
- employees（员工）"

**您**："customers 表的结构是什么样的？"

**AI**："customers 表有以下结构：
- id（整数，主键）
- name（文本）
- email（文本）
- registration_date（日期）
- last_purchase（日期）
- total_spent（数值）"

**您**："过去一个月有多少客户进行了购买？"

**AI**："让我运行查询查找... 根据数据，过去一个月有 128 位客户进行了购买。这些购买的总价值为 25,437.82 元。"

## 安全和隐私

您的数据安全是我们的优先事项：

- **只读访问**：AI 只能查看数据，永远不会修改它
- **安全连接**：支持 SSL/TLS 加密数据库连接
- **本地处理**：您的数据保留在您的计算机上
- **敏感数据保护**：密码和连接详细信息在日志中自动隐藏

## 可用工具

MCP 数据库工具提供了几个您的 AI 可以使用的工具：

- **dbutils-list-tables**：列出数据库中的所有表
- **dbutils-run-query**：执行 SQL 查询（仅 SELECT）
- **dbutils-get-stats**：获取有关表的统计信息
- **dbutils-list-constraints**：列出表约束
- **dbutils-explain-query**：获取查询执行计划
- **dbutils-get-performance**：获取数据库性能指标
- **dbutils-analyze-query**：分析查询以进行优化

## 需要更多帮助？

- [技术文档](docs/technical-guide.md) - 适用于开发人员和高级用户
- [GitHub Issues](https://github.com/donghao1393/mcp-dbutils/issues) - 报告错误或请求功能
- [Smithery](https://smithery.ai/server/@donghao1393/mcp-dbutils) - 简化安装和更新

## 系统要求

- Python 3.10 或更高版本
- 支持 MCP 协议的 AI 系统
- 一个或多个：PostgreSQL、SQLite 或 MySQL 数据库

## 许可证

该项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。