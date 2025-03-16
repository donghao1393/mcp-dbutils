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

## 什么是 MCP Database Utilities？

![Image](https://github.com/user-attachments/assets/26c4f1a1-7b19-4bdd-b9fd-34ad198b0ce3)

MCP Database Utilities 是一个多功能的 MCP 服务，它使您的 AI 能够通过统一的连接配置安全地访问各种类型的数据库（SQLite、MySQL、PostgreSQL 等）进行数据分析。

您可以将其视为 AI 系统和数据库之间的安全桥梁，允许 AI 在不直接访问数据库或冒数据修改风险的情况下读取和分析您的数据。

## 安全和隐私：我们的首要任务

MCP 数据库工具采用**安全优先的架构**设计，非常适合注重数据保护的企业、初创公司和个人用户。我们的全面安全措施包括：

### 数据保护

- **严格只读**：所有操作仅限于 SELECT 查询 - 数据不可被修改
- **无直接数据库访问**：AI 通过我们的安全服务与数据库交互，永不直接连接
- **隔离连接**：每个数据库连接单独管理并严格隔离
- **按需连接**：仅在需要时连接，任务完成后立即断开
- **自动超时**：长时间运行的操作会自动终止，防止资源滥用

### 隐私保障

- **本地处理**：所有数据处理都在您的本地机器上进行 - 无数据发送至外部服务器
- **最小数据暴露**：仅返回请求的数据，限制暴露范围
- **凭证保护**：连接凭证永不暴露给 AI 模型
- **敏感数据屏蔽**：密码和连接详细信息在日志中自动隐藏

### 企业级安全

- **SSL/TLS 支持**：加密连接到远程数据库
- **配置分离**：YAML 配置文件消除解释风险
- **用户控制访问**：您决定哪些数据库可被访问
- **安全默认设置**：默认安全，无需额外配置

有关我们安全架构的技术详情，请参阅[技术指南](docs/technical-guide.md#通信模式与安全架构)。

## 为什么使用 MCP Database Utilities？

- **通用 AI 支持**：适用于任何支持 MCP 协议的 AI 系统
- **多数据库支持**：使用相同的接口连接 SQLite、MySQL、PostgreSQL
- **简单配置**：所有数据库连接使用单个 YAML 文件
- **高级功能**：表格浏览、架构分析和查询执行

## 系统要求

- Python 3.10 或更高版本
- 以下之一：
  - **uvx 安装方式**：uv 包管理器
  - **Docker 安装方式**：Docker Desktop
  - **Smithery 安装方式**：Node.js 14+
- 支持的数据库：
  - SQLite 3.x
  - PostgreSQL 12+
  - MySQL 8+
- 支持的 AI 客户端：
  - Claude Desktop
  - Cursor
  - 任何兼容 MCP 的客户端

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

   安装后，验证uv是否正确安装：
   ```bash
   uv --version
   # 应显示类似：uv 0.5.5 (Homebrew 2024-11-27)
   ```

2. **创建配置文件**，命名为 `config.yaml`，包含您的数据库连接详情：

   ```yaml
   connections:
     postgres:
       type: postgres
       host: localhost
       port: 5432
       dbname: my_database
       user: my_user
       password: my_password
   ```

   > 有关高级配置选项（SSL连接、连接池等），
   > 请查看我们全面的[配置示例集锦](docs/configuration-examples.md)文档。

3. **将此配置添加到您的AI客户端：**

**对于基于JSON的MCP客户端：**
- 找到并编辑您客户端的MCP配置文件：
  - **Claude Desktop (Mac)**: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - **Cline (Mac)**: `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
  - **Cursor (Mac)**: `~/.cursor/mcp.json`
  - **其他客户端**：请参阅您客户端的文档以了解MCP配置文件位置
- 在JSON文件中添加以下配置：

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

> **uvx设置的重要注意事项：**
> - 将`/完整/路径/到您的/config.yaml`替换为您配置文件的实际完整路径
> - 如果您收到uvx未找到的错误，请确保已成功完成步骤1
> - 您可以通过在终端中输入`uv --version`来验证uvx是否已安装

#### 方式B：使用Docker手动安装

1. 如果您没有Docker，请从[docker.com](https://www.docker.com/products/docker-desktop/)安装

2. 创建配置文件（详见下一节）

3. 将此配置添加到您的AI客户端：

**对于基于JSON的MCP客户端：**
- 找到并编辑您客户端的MCP配置文件：
  - **Claude Desktop (Mac)**: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - **Cline (Mac)**: `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
  - **其他客户端**：请参阅您客户端的文档以了解MCP配置文件位置
- 在JSON文件中添加以下配置：

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

## 星标历史

[![星标历史图表](https://api.star-history.com/svg?repos=donghao1393/mcp-dbutils&type=Date)](https://star-history.com/#donghao1393/mcp-dbutils&Date)

## 许可证

本项目采用 MIT 许可证 - 有关详细信息，请参阅 [LICENSE](LICENSE) 文件。
