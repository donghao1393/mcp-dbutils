# Installation Guide

This document provides detailed steps for installing and configuring the MCP Database Utilities.

## System Requirements

Before installing MCP Database Utilities, ensure your system meets the following requirements:

- Python 3.10 or higher
- One of the following:
  - **For uvx installation**: uv package manager
  - **For Docker installation**: Docker Desktop
  - **For Smithery installation**: Node.js 14+
- Supported databases:
  - SQLite 3.x
  - PostgreSQL 12+
  - MySQL 8+
- Supported AI clients:
  - Claude Desktop
  - Cursor
  - Any MCP-compatible client

## Installation Methods

Choose **ONE** of the following methods to install:

### Option A: Using uvx (Recommended)

This method uses `uvx`, which is part of the Python package manager tool called "uv". Here's how to set it up:

1. **Install uv and uvx first:**

   **On macOS or Linux:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   **On Windows:**
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

   After installation, verify that uv is installed correctly:
   ```bash
   uv --version
   # Should display something like: uv 0.5.5 (Homebrew 2024-11-27)
   ```

2. **Create a configuration file** named `config.yaml` with your database connection details:

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

   > For advanced configuration options (SSL connections, connection pooling, etc.),
   > please check out our comprehensive [Configuration Guide](configuration.md) document.

3. **Add this configuration to your AI client:**

**For JSON-based MCP clients:**
- Locate and edit your client's MCP configuration file:
  - **Claude Desktop (Mac)**: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - **Cline (Mac)**: `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
  - **Cursor (Mac)**: `~/.cursor/mcp.json`
  - **Other clients**: Refer to your client's documentation for the MCP configuration file location
- Add the following configuration to the JSON file:

```json
"dbutils": {
  "command": "uvx",
  "args": [
    "mcp-dbutils",
    "--config",
    "/full/path/to/your/config.yaml"
  ]
}
```

> **Important Notes for uvx Setup:**
> - Replace `/full/path/to/your/config.yaml` with the actual full path to your config file
> - If you get an error about uvx not being found, make sure step 1 was completed successfully
> - You can verify uvx is installed by typing `uv --version` in your terminal

### Option B: Manual Installation with Docker

1. Install Docker from [docker.com](https://www.docker.com/products/docker-desktop/) if you don't have it

2. Create a configuration file (see [Configuration Guide](configuration.md) for details)

3. Add this configuration to your AI client:

**For JSON-based MCP clients:**
- Locate and edit your client's MCP configuration file:
  - **Claude Desktop (Mac)**: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - **Cline (Mac)**: `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
  - **Cursor (Mac/Windows)**: `~/.cursor/mcp.json`
  - **Other clients**: Refer to your client's documentation for the MCP configuration file location
- Add the following configuration to the JSON file:

```json
"dbutils": {
  "command": "docker",
  "args": [
    "run",
    "-i",
    "--rm",
    "-v",
    "/full/path/to/your/config.yaml:/app/config.yaml",
    "-v",
    "/full/path/to/your/sqlite.db:/app/sqlite.db",  // Only needed for SQLite
    "mcp/dbutils",
    "--config",
    "/app/config.yaml"
  ]
}
```

**For Cursor:**
- Open Cursor
- Go to Settings → MCP
- Click "Add MCP Server" and fill in:
  - Name: `Database Utility MCP`
  - Type: `Command` (default)
  - Command: `docker run -i --rm -v /full/path/to/your/config.yaml:/app/config.yaml -v /full/path/to/your/sqlite.db:/app/sqlite.db mcp/dbutils --config /app/config.yaml`

> **Important Notes for Docker:**
> - Replace `/full/path/to/your/config.yaml` with the actual full path to your config file
> - For SQLite databases, also replace the sqlite.db path with your actual database path
> - For other database types, remove the SQLite volume line entirely

### Option C: Using Smithery (One-Click for Claude)

This method automatically installs AND configures the service for Claude:

```bash
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

After installation completes, skip to the "Verifying Installation" section.

### Option D: Offline Installation

If you need to install in an environment without internet access, or want to use a specific version of MCP Database Utilities, you can use the offline installation method:

1. **Get the MCP Database Utilities source code**:
   - Download a specific version from GitHub: `git clone https://github.com/donghao1393/mcp-dbutils.git`
   - Switch to the desired version: `cd mcp-dbutils && git checkout v1.x.x` (replace with actual version number)
   - Or download the source code archive directly from the [Releases page](https://github.com/donghao1393/mcp-dbutils/releases)

2. **Use uv to run directly from the local directory**:
   ```bash
   uv --directory /path/to/local/mcp-dbutils run mcp-dbutils --config /path/to/config.yaml
   ```

3. **Add this configuration to your AI client**:

**For JSON-based MCP clients**:
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

> **Important Notes for Offline Installation:**
> - Make sure to replace `/path/to/local/mcp-dbutils` with the actual path to your local source code
> - Make sure to replace `/path/to/config.yaml` with the actual path to your configuration file
> - This method doesn't require installing the package globally, it runs directly from the source code

## Verifying Installation

Once installed and configured properly, your AI can now:
- List tables in your database
- View table structures
- Execute SQL queries safely
- Analyze data across multiple databases

**To verify everything is working:**

1. Ask your AI something like: "Can you check if you're able to connect to my database?"
2. If properly configured, the AI should reply that it can connect to the database specified in your config file
3. Try a simple command like: "List the tables in my database"

If you encounter any issues, check:
- Your configuration file syntax is correct
- The database connection details are accurate
- Your AI client has the MCP server properly configured
- Your database is accessible from your computer

## Troubleshooting

### 1. uvx Not Found

**Problem**: After configuration, the AI reports "uvx command not found".

**Solution**:
- Confirm uv is properly installed: `uv --version`
- Ensure uv is in your PATH
- Try using the full path: `/path/to/uvx`

### 2. Docker Connection Issues

**Problem**: Unable to connect to databases on the host when using Docker.

**Solution**:
- On macOS/Windows, use `host.docker.internal` as the hostname
- On Linux, use the Docker bridge IP (typically `172.17.0.1`)
- Or use `--network="host"` when starting the Docker container

### 3. Configuration File Path Issues

**Problem**: AI reports it cannot find or read the configuration file.

**Solution**:
- Make sure you're using absolute paths, not relative paths
- Check file permissions to ensure the config file is readable
- Verify there are no special characters or spaces in the path

### 4. Database Connection Failures

**Problem**: AI reports it cannot connect to the database.

**Solution**:
- Verify the database server is running
- Check that hostname, port, username, and password are correct
- Confirm network firewalls allow the connection
- For SQLite, ensure the file path is correct and accessible

## Updating

To update to the latest version:

### Updating with uvx

```bash
uv pip install -U mcp-dbutils
```

### Updating with Docker

```bash
docker pull mcp/dbutils:latest
```

### Updating with Smithery

```bash
npx -y @smithery/cli update @donghao1393/mcp-dbutils
```