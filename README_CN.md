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

### 以安全为先的设计，为所有人服务

安全是我们的首要设计原则，特别适合小微企业、初创公司和注重数据安全的个人用户，让您无需复杂的安全基础设施也能安心进行数据分析：

- **连接隔离**：每个数据库连接都通过名称管理并严格隔离，避免跨连接的安全漏洞
- **按需连接**：仅在AI请求时才连接数据库，完成后立即断开连接
- **配置保护**：使用独立的YAML配置文件，消除误解风险（如直接命令中的特殊字符错误）
- **最小数据暴露**：仅与您的数据库和AI模型通信 - 使用本地AI模型时，数据无需离开您的计算机
- **无写入权限**：您的数据默认受到保护 - 服务仅以只读模式运行

## 为什么使用 MCP 数据库工具？

- **通用 AI 支持**：适用于任何支持 MCP 协议的 AI 系统
- **多数据库支持**：使用相同的接口连接 SQLite、MySQL、PostgreSQL
- **安全数据访问**：只读操作确保您的数据不会被修改
- **简单配置**：单个 YAML 文件用于所有数据库连接
- **增强隐私**：您的数据保持本地，敏感信息自动受到保护
- **高级功能**：表格探索、架构分析和查询执行

## 开始使用

### 1. 安装指南

选择**以下一种**方法进行安装：

#### 方式A：使用uvx（推荐）

此方法使用`uvx`，它是Python包管理工具"uv"的一部分。以下是设置步骤：

1. **首先安装uv和uvx：**

   **在macOS或Linux上：**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   **在Windows上：**
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

   安装后，重启您的终端或命令提示符。

2. **创建配置文件**（详见下一节）

3. **将此配置添加到您的AI客户端：**

**对于Claude Desktop：**
- 打开Claude Desktop
- 前往设置 → 开发者
- 在"MCP Servers"部分添加以下配置：

```json
"dbutils": {
  "command": "uvx",
  "args": [
    "mcp-dbutils",
    "--config",
    "/完整/路径/到您的/config.yaml"
  ]
}
```

**对于Cursor：**
- 打开Cursor
- 前往设置 → MCP
- 点击"添加MCP服务器"并填写：
  - 名称：`Database Utility MCP`
  - 类型：`Command`（默认）
  - 命令：`uvx mcp-dbutils --config /完整/路径/到您的/config.yaml`

> **uvx设置的重要注意事项：**
> - 将`/完整/路径/到您的/config.yaml`替换为您配置文件的实际完整路径
> - 如果收到找不到uvx的错误，请确保步骤1成功完成
> - 您可以在终端中输入`uvx --version`来验证uvx是否已安装

#### 方式B：使用Docker手动安装

1. 如果您没有Docker，请从[docker.com](https://www.docker.com/products/docker-desktop/)安装

2. 创建配置文件（详见下一节）

3. 将此配置添加到您的AI客户端：

**对于Claude Desktop：**
- 打开Claude Desktop
- 前往设置 → 开发者
- 在"MCP Servers"部分添加以下配置：

```json
"dbutils": {
  "command": "docker",
  "args": [
    "run",
    "-i",
    "--rm",
    "-v",
    "/完整/路径/到您的/config.yaml:/app/config.yaml",
    "-v",
    "/完整/路径/到您的/sqlite.db:/app/sqlite.db",  // 仅SQLite数据库需要
    "mcp/dbutils",
    "--config",
    "/app/config.yaml"
  ]
}
```

> **Docker的重要注意事项：**
> - 将`/完整/路径/到您的/config.yaml`替换为您配置文件的实际完整路径
> - 对于SQLite数据库，同样替换sqlite.db的路径为您的实际数据库路径
> - 对于其他类型的数据库，完全删除SQLite卷行

#### 方式C：使用Smithery（Claude一键配置）

此方法自动安装并配置服务到Claude：

```bash
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

安装完成后，直接跳到"使用服务"部分。

### 2. 配置

创建一个名为`config.yaml`的文件，包含您的数据库连接详细信息：

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

### 4. 使用服务

正确安装和配置后，您的AI现在可以：
- 列出数据库中的表
- 查看表结构
- 安全执行SQL查询
- 跨多个数据库分析数据

**验证一切正常工作：**

1. 向您的AI提问类似："你能检查一下是否可以连接到我的数据库吗？"
2. 如果配置正确，AI应回复它可以连接到您配置文件中指定的数据库
3. 尝试一个简单的命令，如："列出我数据库中的表"

如果遇到问题，请检查：
- 您的配置文件语法是否正确
- 数据库连接详细信息是否准确
- 您的AI客户端是否正确配置了MCP服务器
- 您的数据库是否可从您的计算机访问

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