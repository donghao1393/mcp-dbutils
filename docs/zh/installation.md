# 安装指南

本文档提供了安装和配置 MCP 数据库工具的详细步骤。

## 系统要求

在安装 MCP 数据库工具之前，请确保您的系统满足以下要求：

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

## 安装方法

选择**以下一种**方法进行安装：

### 方式A：使用uvx（推荐）

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
   > 请查看我们全面的[配置指南](configuration.md)文档。

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

### 方式B：使用Docker手动安装

1. 如果您没有Docker，请从[docker.com](https://www.docker.com/products/docker-desktop/)安装

2. 创建配置文件（详见[配置指南](configuration.md)）

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

**对于Cursor：**
- 打开Cursor
- 转到设置 → MCP
- 点击"添加MCP服务器"并填写：
  - 名称：`Database Utility MCP`
  - 类型：`Command`（默认）
  - 命令：`docker run -i --rm -v /完整/路径/到您的/config.yaml:/app/config.yaml -v /完整/路径/到您的/sqlite.db:/app/sqlite.db mcp/dbutils --config /app/config.yaml`

> **Docker的重要注意事项：**
> - 将`/完整/路径/到您的/config.yaml`替换为您配置文件的实际完整路径
> - 对于SQLite数据库，同样替换sqlite.db的路径为您的实际数据库路径
> - 对于其他类型的数据库，完全删除SQLite卷行

### 方式C：使用Smithery（Claude一键配置）

此方法自动安装并配置服务到Claude：

```bash
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

安装完成后，直接跳到"验证安装"部分。

### 方式D：离线安装

如果您需要在无法访问互联网的环境中安装，或者希望使用特定版本的 MCP 数据库工具，可以使用离线安装方法：

1. **获取 MCP 数据库工具源代码**：
   - 从 GitHub 下载特定版本：`git clone https://github.com/donghao1393/mcp-dbutils.git`
   - 切换到所需版本：`cd mcp-dbutils && git checkout v1.x.x`（替换为实际版本号）
   - 或者直接从 [Releases 页面](https://github.com/donghao1393/mcp-dbutils/releases) 下载源代码压缩包

2. **使用 uv 直接从本地目录运行**：
   ```bash
   uv --directory /path/to/local/mcp-dbutils run mcp-dbutils --config /path/to/config.yaml
   ```

3. **将此配置添加到您的AI客户端**：

**对于基于JSON的MCP客户端**：
```json
"dbutils": {
  "command": "uv",
  "args": [
    "--directory",
    "/path/to/local/mcp-dbutils",
    "run",
    "mcp-dbutils",
    "--config",
    "/path/to/config.yaml"
  ]
}
```

> **离线安装的重要注意事项：**
> - 确保替换 `/path/to/local/mcp-dbutils` 为实际的本地源代码路径
> - 确保替换 `/path/to/config.yaml` 为实际的配置文件路径
> - 此方法不需要安装包到全局环境，直接从源代码运行

## 验证安装

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

## 常见问题解决

### 1. uvx未找到

**问题**：配置后，AI报告"找不到uvx命令"。

**解决方案**：
- 确认uv已正确安装：`uv --version`
- 确保uv在您的PATH中
- 尝试使用完整路径：`/path/to/uvx`

### 2. Docker连接问题

**问题**：使用Docker方式时无法连接到主机上的数据库。

**解决方案**：
- 在macOS/Windows上使用`host.docker.internal`作为主机名
- 在Linux上使用Docker网桥IP（通常是`172.17.0.1`）
- 或使用`--network="host"`启动Docker容器

### 3. 配置文件路径问题

**问题**：AI报告无法找到或读取配置文件。

**解决方案**：
- 确保使用绝对路径而非相对路径
- 检查文件权限，确保配置文件可读
- 验证路径中没有特殊字符或空格

### 4. 数据库连接失败

**问题**：AI报告无法连接到数据库。

**解决方案**：
- 验证数据库服务器是否运行
- 检查主机名、端口、用户名和密码是否正确
- 确认网络防火墙允许连接
- 对于SQLite，确保文件路径正确且可访问

## 更新

要更新到最新版本：

### 使用uvx的更新

```bash
uv pip install -U mcp-dbutils
```

### 使用Docker的更新

```bash
docker pull mcp/dbutils:latest
```

### 使用Smithery的更新

```bash
npx -y @smithery/cli update @donghao1393/mcp-dbutils
```