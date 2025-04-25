# Platform-Specific Installation Guide

*English | [中文](../zh/installation-platform-specific.md) | [Français](../fr/installation-platform-specific.md) | [Español](../es/installation-platform-specific.md) | [العربية](../ar/installation-platform-specific.md) | [Русский](../ru/installation-platform-specific.md)*


*English | [中文](../zh/installation-platform-specific.md) | [Français](../fr/installation-platform-specific.md) | [Español](../es/installation-platform-specific.md) | [العربية](../ar/installation-platform-specific.md) | [Русский](../ru/installation-platform-specific.md)*

This document provides detailed instructions for installing and configuring MCP Database Utilities on different operating systems.

## Linux Installation Guide

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager

### Installation with uv (Recommended)

1. Install uv (if not already installed):

```bash
curl -sSf https://raw.githubusercontent.com/astral-sh/uv/main/install.sh | bash
```

2. Install MCP Database Utilities using uv:

```bash
uv pip install mcp-dbutils
```

3. Verify installation:

```bash
python -c "import mcp_dbutils; print(mcp_dbutils.__version__)"
```

### Installation with Virtual Environment

1. Create a virtual environment:

```bash
python3 -m venv mcp-env
source mcp-env/bin/activate
```

2. Install MCP Database Utilities:

```bash
pip install mcp-dbutils
```

### Offline Installation

1. Download the package and its dependencies in an environment with internet access:

```bash
uv pip download mcp-dbutils -d ./mcp-packages
```

2. Copy the `mcp-packages` directory to the target environment

3. Install in the target environment:

```bash
uv pip install --no-index --find-links=./mcp-packages mcp-dbutils
```

Or use the offline run mode:

```bash
uv --directory /path/to/local/mcp-dbutils run mcp-dbutils
```

### Specific Linux Distribution Notes

#### Ubuntu/Debian

Ensure Python development package is installed:

```bash
sudo apt update
sudo apt install -y python3-dev
```

#### CentOS/RHEL

Ensure Python development package is installed:

```bash
sudo yum install -y python3-devel
```

#### Arch Linux

Ensure Python is installed:

```bash
sudo pacman -S python-pip
```

## macOS Installation Guide

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager
- Homebrew (recommended for installing Python)

### Installation with uv (Recommended)

1. Install uv (if not already installed):

```bash
curl -sSf https://raw.githubusercontent.com/astral-sh/uv/main/install.sh | bash
```

2. Install MCP Database Utilities using uv:

```bash
uv pip install mcp-dbutils
```

### Installing Python with Homebrew

If you haven't installed Python yet, you can use Homebrew:

```bash
brew install python
```

### Apple Silicon (M1/M2/M3) Special Notes

For Macs with Apple Silicon chips:

1. Ensure you're using the ARM64 version of Python:

```bash
which python3
# Should show /opt/homebrew/bin/python3 instead of /usr/local/bin/python3
```

2. If you encounter installation issues, try using Rosetta 2:

```bash
arch -x86_64 uv pip install mcp-dbutils
```

## Windows Installation Guide

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager

### Installation with uv (Recommended)

1. Install uv (if not already installed):

In PowerShell (with administrator privileges):

```powershell
iwr -useb https://raw.githubusercontent.com/astral-sh/uv/main/install.ps1 | iex
```

2. Install MCP Database Utilities using uv:

```powershell
uv pip install mcp-dbutils
```

### Installation with Virtual Environment

1. Create a virtual environment:

```powershell
python -m venv mcp-env
.\mcp-env\Scripts\Activate.ps1
```

2. Install MCP Database Utilities:

```powershell
pip install mcp-dbutils
```



### WSL (Windows Subsystem for Linux) Installation

If you prefer working in a Linux environment, you can use WSL:

1. Install WSL (in PowerShell with administrator privileges):

```powershell
wsl --install
```

2. After installation is complete, launch WSL and follow the Linux installation guide above

## Docker Installation Guide

### Using Pre-built Image

1. Pull the MCP Database Utilities image:

```bash
docker pull mcp/dbutils
```

2. Run the container:

```bash
docker run -i --rm \
  -v /path/to/config.yaml:/app/config.yaml \
  mcp/dbutils --config /app/config.yaml
```

### Building a Custom Image

1. Create a Dockerfile:

```dockerfile
FROM python:3.10-slim

RUN pip install --no-cache-dir mcp-dbutils

WORKDIR /app
COPY config.yaml /app/config.yaml

ENTRYPOINT ["mcp-dbutils"]
CMD ["--config", "/app/config.yaml"]
```

2. Build the image:

```bash
docker build -t custom-mcp-dbutils .
```

3. Run the container:

```bash
docker run -i --rm custom-mcp-dbutils
```

## Troubleshooting

### Common Issues

1. **Database driver errors when connecting**

   MCP Database Utilities will automatically try to import the appropriate driver based on your configured database type. If you encounter driver errors, you may need to install the corresponding Python database adapter:

   ```bash
   # If you need to connect to PostgreSQL
   uv pip install psycopg2-binary

   # If you need to connect to MySQL
   uv pip install mysqlclient

   # If you need to connect to SQLite (usually included with Python)
   uv pip install pysqlite3
   ```

   Note: MCP Database Utilities does not include these databases itself; it only provides connections to your existing databases.

2. **Permission errors**

   - Linux/macOS: Ensure your configuration file and database files have the correct permissions
   - Windows: Run Command Prompt or PowerShell as administrator

3. **Version compatibility issues**

   Make sure you're using Python 3.10 or higher:

   ```bash
   python --version
   ```

### Getting Help

If you encounter installation problems, you can:

1. Check if similar issues exist in [GitHub Issues](https://github.com/donghao1393/mcp-dbutils/issues)
2. Submit a new issue with a detailed description of your problem and environment
3. Seek help on [Smithery](https://smithery.ai/server/@donghao1393/mcp-dbutils)
