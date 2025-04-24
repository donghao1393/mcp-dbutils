# 平台特定安装指南

本文档提供了在不同操作系统上安装和配置 MCP 数据库工具的详细指南。

## Linux 安装指南

### 前提条件

- Python 3.10 或更高版本
- pip 或 uv 包管理器
- 对于数据库连接：相应数据库的客户端库

### 使用 uv 安装（推荐）

1. 安装 uv（如果尚未安装）：

```bash
curl -sSf https://raw.githubusercontent.com/astral-sh/uv/main/install.sh | bash
```

2. 使用 uv 安装 MCP 数据库工具：

```bash
uv pip install mcp-dbutils
```

3. 验证安装：

```bash
python -c "import mcp_dbutils; print(mcp_dbutils.__version__)"
```

### 使用虚拟环境安装

1. 创建虚拟环境：

```bash
python3 -m venv mcp-env
source mcp-env/bin/activate
```

2. 安装 MCP 数据库工具：

```bash
pip install mcp-dbutils
```

### 离线安装

1. 在有网络连接的环境中下载包及其依赖：

```bash
uv pip download mcp-dbutils -d ./mcp-packages
```

2. 将 `mcp-packages` 目录复制到目标环境

3. 在目标环境中安装：

```bash
uv pip install --no-index --find-links=./mcp-packages mcp-dbutils
```

或使用离线运行模式：

```bash
uv --directory /path/to/local/mcp-dbutils run mcp-dbutils
```

### 特定 Linux 发行版注意事项

#### Ubuntu/Debian

安装必要的系统依赖：

```bash
sudo apt update
sudo apt install -y python3-dev libpq-dev default-libmysqlclient-dev
```

#### CentOS/RHEL

安装必要的系统依赖：

```bash
sudo yum install -y python3-devel postgresql-devel mysql-devel
```

#### Arch Linux

安装必要的系统依赖：

```bash
sudo pacman -S python-pip postgresql-libs mariadb-libs
```

## macOS 安装指南

### 前提条件

- Python 3.10 或更高版本
- pip 或 uv 包管理器
- Homebrew（推荐，用于安装数据库客户端库）

### 使用 uv 安装（推荐）

1. 安装 uv（如果尚未安装）：

```bash
curl -sSf https://raw.githubusercontent.com/astral-sh/uv/main/install.sh | bash
```

2. 使用 uv 安装 MCP 数据库工具：

```bash
uv pip install mcp-dbutils
```

### 使用 Homebrew 安装依赖

如果需要连接到 PostgreSQL 或 MySQL 数据库，安装相应的客户端库：

```bash
# 对于 PostgreSQL
brew install postgresql

# 对于 MySQL
brew install mysql-client
```

注意：安装 MySQL 客户端后，可能需要将其添加到 PATH 中：

```bash
echo 'export PATH="/usr/local/opt/mysql-client/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Apple Silicon (M1/M2/M3) 特别说明

对于 Apple Silicon 芯片的 Mac，某些数据库连接器可能需要特殊处理：

1. 确保使用 ARM64 版本的 Python：

```bash
which python3
# 应该显示 /opt/homebrew/bin/python3 而不是 /usr/local/bin/python3
```

2. 如果遇到库兼容性问题，尝试使用 Rosetta 2：

```bash
arch -x86_64 uv pip install mcp-dbutils
```

## Windows 安装指南

### 前提条件

- Python 3.10 或更高版本
- pip 或 uv 包管理器
- 对于数据库连接：相应数据库的客户端库

### 使用 uv 安装（推荐）

1. 安装 uv（如果尚未安装）：

在 PowerShell 中运行（需要管理员权限）：

```powershell
iwr -useb https://raw.githubusercontent.com/astral-sh/uv/main/install.ps1 | iex
```

2. 使用 uv 安装 MCP 数据库工具：

```powershell
uv pip install mcp-dbutils
```

### 使用虚拟环境安装

1. 创建虚拟环境：

```powershell
python -m venv mcp-env
.\mcp-env\Scripts\Activate.ps1
```

2. 安装 MCP 数据库工具：

```powershell
pip install mcp-dbutils
```

### 数据库客户端库安装

#### PostgreSQL

1. 下载并安装 PostgreSQL：https://www.postgresql.org/download/windows/
2. 确保将 PostgreSQL bin 目录添加到 PATH 环境变量

#### MySQL

1. 下载并安装 MySQL Connector/C：https://dev.mysql.com/downloads/connector/c/
2. 确保将 MySQL bin 目录添加到 PATH 环境变量

### WSL (Windows Subsystem for Linux) 安装

如果您更喜欢在 Linux 环境中工作，可以使用 WSL：

1. 安装 WSL（在 PowerShell 中运行，需要管理员权限）：

```powershell
wsl --install
```

2. 安装完成后，启动 WSL 并按照上面的 Linux 安装指南进行操作

## Docker 安装指南

### 使用预构建镜像

1. 拉取 MCP 数据库工具镜像：

```bash
docker pull mcp/dbutils
```

2. 运行容器：

```bash
docker run -i --rm \
  -v /path/to/config.yaml:/app/config.yaml \
  mcp/dbutils --config /app/config.yaml
```

### 构建自定义镜像

1. 创建 Dockerfile：

```dockerfile
FROM python:3.10-slim

RUN pip install --no-cache-dir mcp-dbutils

WORKDIR /app
COPY config.yaml /app/config.yaml

ENTRYPOINT ["mcp-dbutils"]
CMD ["--config", "/app/config.yaml"]
```

2. 构建镜像：

```bash
docker build -t custom-mcp-dbutils .
```

3. 运行容器：

```bash
docker run -i --rm custom-mcp-dbutils
```

## 故障排除

### 常见问题

1. **找不到数据库驱动程序**

   确保已安装相应的数据库客户端库：
   
   ```bash
   # PostgreSQL
   uv pip install psycopg2-binary
   
   # MySQL
   uv pip install mysqlclient
   
   # SQLite (通常已包含在 Python 中)
   uv pip install pysqlite3
   ```

2. **权限错误**

   - Linux/macOS：确保配置文件和数据库文件具有正确的权限
   - Windows：以管理员身份运行命令提示符或 PowerShell

3. **版本兼容性问题**

   确保使用 Python 3.10 或更高版本：
   
   ```bash
   python --version
   ```

### 获取帮助

如果您遇到安装问题，可以：

1. 查看[GitHub Issues](https://github.com/donghao1393/mcp-dbutils/issues)中是否有类似问题
2. 提交新的 Issue，详细描述您的问题和环境
3. 在[Smithery](https://smithery.ai/server/@donghao1393/mcp-dbutils)上寻求帮助
