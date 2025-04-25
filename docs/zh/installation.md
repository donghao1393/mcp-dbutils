# 安装指南

*[English](../en/installation.md) | 中文 | [Français](../fr/installation.md) | [Español](../es/installation.md) | [العربية](../ar/installation.md) | [Русский](../ru/installation.md)*

本文档提供了简单易懂的步骤，帮助您安装和配置 MCP 数据库工具，让您的 AI 助手能够安全地访问和分析您的数据库。

## 什么是 MCP？

MCP（Model Context Protocol）是一种让 AI 应用（如 Claude）能够使用外部工具的协议。MCP 数据库工具就是这样一个工具，它允许 AI 读取您的数据库内容，但不会修改任何数据。

## 安装前的准备

在开始安装前，请确认您有：

- 一个支持 MCP 的 AI 应用（如 Claude Desktop、Cursor 等）
- 至少一个您想让 AI 访问的数据库（SQLite、MySQL 或 PostgreSQL）

## 安装方式选择

我们提供四种简单的安装方式，请选择**最适合您**的一种：

| 安装方式 | 适合人群 | 优势 |
|---------|---------|------|
| **方式 A：使用 uvx** | 大多数用户 | 简单快捷，推荐首选 |
| **方式 B：使用 Docker** | 喜欢容器化应用的用户 | 环境隔离，不影响系统 |
| **方式 C：使用 Smithery** | Claude Desktop 用户 | 一键安装，最简单 |
| **方式 D：离线安装** | 需要在无网络环境使用的用户 | 不需要网络连接 |

## 方式 A：使用 uvx 安装（推荐）

### 步骤 1：安装 uv 工具

**在 Mac 或 Linux 上**：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**在 Windows 上**：
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

安装后，请在终端中输入以下命令确认安装成功：
```bash
uv --version
```
您应该能看到类似 `uv 0.5.5` 的版本信息。

### 步骤 2：创建数据库配置文件

1. 在您的电脑上创建一个名为 `config.yaml` 的文件
2. 将以下内容复制到文件中（根据您的数据库类型选择一种）：

**SQLite 数据库示例**：
```yaml
connections:
  my_sqlite:
    type: sqlite
    path: C:/数据库文件路径/my_database.db
```

**PostgreSQL 数据库示例**：
```yaml
connections:
  my_postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: my_database
    user: postgres_user
    password: postgres_password
```

**MySQL 数据库示例**：
```yaml
connections:
  my_mysql:
    type: mysql
    host: localhost
    port: 3306
    database: my_database
    user: mysql_user
    password: mysql_password
```

> 请将示例中的信息替换为您实际的数据库信息。更多配置选项请参考[配置指南](configuration.md)。

### 步骤 3：配置您的 AI 应用

#### Claude Desktop 配置

1. 打开 Claude Desktop 应用
2. 点击左下角的设置图标
3. 选择 "MCP 服务器"
4. 点击 "添加服务器"
5. 在配置文件中添加：

```json
"dbutils": {
  "command": "uvx",
  "args": [
    "mcp-dbutils",
    "--config",
    "C:/Users/您的用户名/config.yaml"
  ]
}
```

> 重要：请将 `C:/Users/您的用户名/config.yaml` 替换为您在步骤 2 中创建的配置文件的实际路径。

#### Cursor 配置

1. 打开 Cursor 应用
2. 点击 "设置" → "MCP"
3. 点击 "添加 MCP 服务器"
4. 填写以下信息：
   - 名称：`Database Utility MCP`
   - 类型：`Command`（默认）
   - 命令：`uvx mcp-dbutils --config C:/Users/您的用户名/config.yaml`

> 重要：请将 `C:/Users/您的用户名/config.yaml` 替换为您在步骤 2 中创建的配置文件的实际路径。

## 方式 B：使用 Docker 安装

### 步骤 1：安装 Docker

如果您还没有安装 Docker，请从 [docker.com](https://www.docker.com/products/docker-desktop/) 下载并安装。

### 步骤 2：创建数据库配置文件

与方式 A 的步骤 2 相同，创建一个 `config.yaml` 文件。

### 步骤 3：配置您的 AI 应用

#### Claude Desktop 配置

1. 打开 Claude Desktop 应用
2. 点击左下角的设置图标
3. 选择 "MCP 服务器"
4. 点击 "添加服务器"
5. 在配置文件中添加：

```json
"dbutils": {
  "command": "docker",
  "args": [
    "run",
    "-i",
    "--rm",
    "-v",
    "C:/Users/您的用户名/config.yaml:/app/config.yaml",
    "mcp/dbutils",
    "--config",
    "/app/config.yaml"
  ]
}
```

> 重要：请将 `C:/Users/您的用户名/config.yaml` 替换为您在步骤 2 中创建的配置文件的实际路径。

#### Cursor 配置

1. 打开 Cursor 应用
2. 点击 "设置" → "MCP"
3. 点击 "添加 MCP 服务器"
4. 填写以下信息：
   - 名称：`Database Utility MCP`
   - 类型：`Command`（默认）
   - 命令：`docker run -i --rm -v C:/Users/您的用户名/config.yaml:/app/config.yaml mcp/dbutils --config /app/config.yaml`

> 重要：请将 `C:/Users/您的用户名/config.yaml` 替换为您在步骤 2 中创建的配置文件的实际路径。

## 方式 C：使用 Smithery 安装（Claude 一键配置）

如果您使用 Claude Desktop，这是最简单的安装方式：

1. 确保您已安装 Node.js
2. 打开终端或命令提示符
3. 运行以下命令：

```bash
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

4. 按照屏幕上的提示完成安装

这种方法会自动完成所有配置，无需手动编辑任何文件。

## 方式 D：离线安装

如果您需要在无法访问互联网的环境中使用，或者想使用特定版本：

### 步骤 1：获取源代码

在有网络的环境中：
1. 从 GitHub 下载源代码：`git clone https://github.com/donghao1393/mcp-dbutils.git`
2. 或从 [Releases 页面](https://github.com/donghao1393/mcp-dbutils/releases) 下载压缩包
3. 将下载的文件复制到您的离线环境

### 步骤 2：创建数据库配置文件

与方式 A 的步骤 2 相同，创建一个 `config.yaml` 文件。

### 步骤 3：配置您的 AI 应用

#### Claude Desktop 配置

1. 打开 Claude Desktop 应用
2. 点击左下角的设置图标
3. 选择 "MCP 服务器"
4. 点击 "添加服务器"
5. 在配置文件中添加：

```json
"dbutils": {
  "command": "uv",
  "args": [
    "--directory",
    "C:/Users/您的用户名/mcp-dbutils",
    "run",
    "mcp-dbutils",
    "--config",
    "C:/Users/您的用户名/config.yaml"
  ]
}
```

> 重要：请将路径替换为您实际的源代码目录和配置文件路径。

## 验证安装是否成功

完成安装后，让我们来验证一切是否正常工作：

### 测试连接

1. 打开您的 AI 应用（Claude Desktop 或 Cursor）
2. 向 AI 提问：**"你能检查一下是否可以连接到我的数据库吗？"**
3. 如果配置正确，AI 会回复它已成功连接到您的数据库

### 尝试简单命令

成功连接后，您可以尝试以下简单命令：

- **"列出我数据库中的所有表"**
- **"描述 customers 表的结构"**
- **"查询 products 表中价格最高的 5 个产品"**

## 常见问题解决

### 问题 1：AI 无法找到 uvx 命令

**现象**：AI 回复 "找不到 uvx 命令" 或类似错误

**解决方法**：
1. 确认 uv 已正确安装：在终端中运行 `uv --version`
2. 如果已安装但仍报错，可能是环境变量问题：
   - 在 Windows 上，检查 PATH 环境变量是否包含 uv 安装目录
   - 在 Mac/Linux 上，可能需要重启终端或运行 `source ~/.bashrc` 或 `source ~/.zshrc`

### 问题 2：无法连接到数据库

**现象**：AI 报告无法连接到您的数据库

**解决方法**：
1. **检查数据库是否运行**：确保您的数据库服务器已启动
2. **验证连接信息**：仔细检查 config.yaml 中的主机名、端口、用户名和密码
3. **检查网络设置**：
   - 如果使用 Docker，对于本地数据库，请使用 `host.docker.internal` 作为主机名
   - 确认防火墙未阻止连接

### 问题 3：配置文件路径错误

**现象**：AI 报告找不到配置文件

**解决方法**：
1. **使用绝对路径**：确保在 AI 应用配置中使用了完整的绝对路径
2. **检查文件权限**：确保配置文件对当前用户可读
3. **避免特殊字符**：路径中不要包含特殊字符或空格，如有必要请使用引号

### 问题 4：SQLite 数据库路径问题

**现象**：使用 SQLite 时连接失败

**解决方法**：
1. **检查文件路径**：确保 SQLite 数据库文件存在且路径正确
2. **检查权限**：确保数据库文件有读取权限
3. **使用 Docker 时**：确保正确映射了 SQLite 文件路径

## 更新到最新版本

定期更新可以获得新功能和安全修复。根据您的安装方式选择相应的更新方法：

### 方式 A（uvx）更新

当您使用 `uvx` 命令运行 MCP 数据库工具时（如 `uvx mcp-dbutils`），它会自动使用最新版本，无需手动更新。

如果您使用的是传统安装方式（非 `uvx` 命令），可以通过以下命令手动更新：

```bash
uv pip install -U mcp-dbutils
```

### 方式 B（Docker）更新

```bash
docker pull mcp/dbutils:latest
```

### 方式 C（Smithery）更新

```bash
npx -y @smithery/cli update @donghao1393/mcp-dbutils
```

### 方式 D（离线）更新

1. 在有网络的环境中下载最新版本的源代码
2. 替换您离线环境中的源代码文件

## 使用示例

成功安装后，您可以尝试以下对话示例：

**您**：能否列出我数据库中的所有表？

**AI**：我来查看您的数据库中有哪些表。以下是您数据库中的表：
- customers（客户）
- products（产品）
- orders（订单）
- inventory（库存）

**您**：customers 表的结构是什么？

**AI**：customers 表有以下结构：
- id（整数，主键）
- name（文本）
- email（文本）
- registration_date（日期）
- last_purchase（日期）

**您**：过去一个月有多少客户进行了购买？

**AI**：让我查询一下...根据数据，过去一个月有 28 位客户进行了购买，总购买金额为 ¥15,742.50。