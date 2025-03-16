# MCP Database Utilities

<!-- 项目状态徽章 -->
[![Build Status](https://img.shields.io/github/workflow/status/donghao1393/mcp-dbutils/Quality%20Assurance?label=tests)](https://github.com/donghao1393/mcp-dbutils/actions)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/donghao1393/bdd0a63ec2a816539ff8c136ceb41e48/raw/coverage.json)](https://github.com/donghao1393/mcp-dbutils/actions)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=donghao1393_mcp-dbutils&metric=alert_status)](https://sonarcloud.io/dashboard?id=donghao1393_mcp-dbutils)

<!-- 版本和安装徽章 -->
[![PyPI version](https://img.shields.io/pypi/v/mcp-dbutils)](https://pypi.org/project/mcp-dbutils/)
[![PyPI downloads](https://img.shields.io/pypi/dm/mcp-dbutils)](https://pypi.org/project/mcp-dbutils/)
[![Smithery](https://smithery.ai/badge/@donghao1393/mcp-dbutils)](https://smithery.ai/server/@donghao1393/mcp-dbutils)

<!-- 技术规格徽章 -->
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/github/license/donghao1393/mcp-dbutils)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/donghao1393/mcp-dbutils?style=social)](https://github.com/donghao1393/mcp-dbutils/stargazers)

[中文文档](README_CN.md) | [Technical Guide](docs/technical-guide.md)

## What is MCP Database Utilities?

MCP Database Utilities is an all-in-one MCP service that enables your AI to do data analysis by accessing versatile types of database (SQLite, MySQL, PostgreSQL, and more) within a unified connection configuration in a safe way.

Think of it as a secure bridge between AI systems and your databases, allowing AI to read and analyze your data without direct database access or risking data modifications.

## Security and Privacy: Our Top Priority

MCP Database Utilities is built with a **security-first architecture**, making it ideal for businesses, startups, and individuals who value data protection. Our comprehensive security measures include:

### Data Protection

- **Strictly Read-Only**: All operations are limited to SELECT queries only - data cannot be modified
- **No Direct Database Access**: AI interacts with your database through our secure service, never directly
- **Isolated Connections**: Each database connection is managed separately and strictly isolated
- **On-Demand Connectivity**: Connects only when needed and disconnects immediately after task completion
- **Automatic Timeouts**: Long-running operations are automatically terminated to prevent resource abuse

### Privacy Safeguards

- **Local Processing**: All data processing occurs on your local machine - no data sent to external servers
- **Minimal Data Exposure**: Only requested data is returned, limiting exposure scope
- **Credential Protection**: Connection credentials are never exposed to the AI model
- **Sensitive Data Masking**: Passwords and connection details are automatically hidden in logs

### Enterprise-Ready Security

- **SSL/TLS Support**: Encrypted connections to remote databases
- **Configuration Separation**: YAML configuration files eliminate interpretation risks
- **User-Controlled Access**: You decide which databases are accessible
- **Secure Default Settings**: Secure by default with no additional configuration needed

For technical details about our security architecture, see the [Technical Guide](docs/technical-guide.md#通信模式与安全架构).

## Why Use MCP Database Utilities?

- **Universal AI Support**: Works with any AI system that supports the MCP protocol
- **Multiple Database Support**: Connect to SQLite, MySQL, PostgreSQL with the same interface
- **Simple Configuration**: Single YAML file for all your database connections
- **Advanced Capabilities**: Table exploration, schema analysis, and query execution

## System Requirements

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

## Getting Started

### 1. Installation Guide

Choose **ONE** of the following methods to install:

#### Option A: Using uvx (Recommended)

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
   > please check out our comprehensive [Configuration Examples](docs/configuration-examples.md) document.

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

#### Option B: Manual Installation with Docker

1. Install Docker from [docker.com](https://www.docker.com/products/docker-desktop/) if you don't have it

2. Create a configuration file (see next section for details)

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

#### Option C: Using Smithery (One-Click for Claude)

This method automatically installs AND configures the service for Claude:

```bash
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

After installation completes, skip to the "Using the Service" section.

### 4. Using the Service

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

## Example Interactions

**You**: "Can you list all the tables in my my-postgres database?"

**AI**: "I'll check that for you. Here are the tables in your my-postgres database:
- customers
- products
- orders
- inventory
- employees"

**You**: "What does the customers table look like?"

**AI**: "The customers table has the following structure:
- id (integer, primary key)
- name (text)
- email (text)
- registration_date (date)
- last_purchase (date)
- total_spent (numeric)"

**You**: "How many customers made purchases in the last month?"

**AI**: "Let me run a query to find out... According to the data, 128 customers made purchases in the last month. The total value of these purchases was $25,437.82."

## Available Tools

MCP Database Utilities provides several tools that your AI can use:

- **dbutils-list-tables**: Lists all tables in a database
- **dbutils-run-query**: Executes a SQL query (SELECT only)
- **dbutils-get-stats**: Gets statistics about a table
- **dbutils-list-constraints**: Lists table constraints
- **dbutils-explain-query**: Gets query execution plan
- **dbutils-get-performance**: Gets database performance metrics
- **dbutils-analyze-query**: Analyzes queries for optimization

## Need More Help?

- [Technical Documentation](docs/technical-guide.md) - For developers and advanced users
- [GitHub Issues](https://github.com/donghao1393/mcp-dbutils/issues) - Report bugs or request features
- [Smithery](https://smithery.ai/server/@donghao1393/mcp-dbutils) - Simplified installation and updates

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=donghao1393/mcp-dbutils&type=Date)](https://star-history.com/#donghao1393/mcp-dbutils&Date)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
