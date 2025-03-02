# MCP Database Utilities

![GitHub Repo stars](https://img.shields.io/github/stars/donghao1393/mcp-dbutils)
![PyPI version](https://img.shields.io/pypi/v/mcp-dbutils)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/donghao1393/bdd0a63ec2a816539ff8c136ceb41e48/raw/coverage.json)](https://github.com/donghao1393/mcp-dbutils/actions)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/github/license/donghao1393/mcp-dbutils)
[![smithery badge](https://smithery.ai/badge/@donghao1393/mcp-dbutils)](https://smithery.ai/server/@donghao1393/mcp-dbutils)

[中文文档](README_CN.md)

## Overview
MCP Database Utilities is a unified database access service that supports multiple database types (PostgreSQL and SQLite). Through its abstraction layer design, it provides a simple and unified database operation interface for MCP servers.

## Features
- Unified database access interface
- Support for multiple database configurations
- Secure read-only query execution
- Table structure and schema information retrieval
- Intelligent connection management and resource cleanup
- Debug mode support

## Installation and Configuration

### Installation Methods
#### Installing via Smithery

To install Database Utilities for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@donghao1393/mcp-dbutils):

```bash
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

#### Using uvx (Recommended)
No installation required, run directly using `uvx`:
```bash
uvx mcp-dbutils --config /path/to/config.yaml
```

Add to Claude configuration:
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
      "MCP_DEBUG": "1"  // Optional: Enable debug mode
    }
  }
}
```

#### Using pip
```bash
pip install mcp-dbutils
```

Add to Claude configuration:
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
      "MCP_DEBUG": "1"  // Optional: Enable debug mode
    }
  }
}
```

#### Using Docker
```bash
docker run -i --rm \
  -v /path/to/config.yaml:/app/config.yaml \
  -v /path/to/sqlite.db:/app/sqlite.db \  # Optional: for SQLite database
  -e MCP_DEBUG=1 \  # Optional: Enable debug mode
  mcp/dbutils --config /app/config.yaml
```

Add to Claude configuration:
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
      "/path/to/sqlite.db:/app/sqlite.db",  // Optional: for SQLite database
      "mcp/dbutils",
      "--config",
      "/app/config.yaml"
    ],
    "env": {
      "MCP_DEBUG": "1"  // Optional: Enable debug mode
    }
  }
}
```

> **Note for Docker database connections:**
> - For SQLite: Mount your database file using `-v /path/to/sqlite.db:/app/sqlite.db`
> - For PostgreSQL running on host:
>   - On Mac/Windows: Use `host.docker.internal` as host in config
>   - On Linux: Use `172.17.0.1` (docker0 IP) or run with `--network="host"`

### Requirements
- Python 3.10+
- PostgreSQL (optional)
- SQLite3 (optional)

### Configuration File
The project requires a YAML configuration file, specified via the `--config` parameter. Configuration example:

```yaml
databases:
  # Standard PostgreSQL configuration example
  my_postgres:
    type: postgres
    dbname: test_db
    user: postgres
    password: secret
    host: host.docker.internal  # For Mac/Windows
    # host: 172.17.0.1         # For Linux (docker0 IP)
    port: 5432

  # PostgreSQL with JDBC URL example
  my_postgres_jdbc:
    type: postgres
    jdbc_url: jdbc:postgresql://host.docker.internal:5432/test_db
    user: postgres            # Credentials must be provided separately
    password: secret          # Not included in JDBC URL for security

  # SQLite standard configuration
  my_sqlite:
    type: sqlite
    path: /app/sqlite.db       # Database file path
    password: optional_password # optional

  # SQLite with JDBC URL configuration
  my_sqlite_jdbc:
    type: sqlite
    jdbc_url: jdbc:sqlite:/app/data.db?mode=ro&cache=shared  # Supports query parameters
    password: optional_password    # Provided separately for security
```

The configuration supports JDBC URL format for both PostgreSQL and SQLite:

PostgreSQL:
1. Standard configuration with individual parameters
2. JDBC URL configuration with separate credentials

SQLite:
1. Standard configuration with path parameter
2. JDBC URL configuration with query parameters support:
   - mode=ro: Read-only mode
   - cache=shared: Shared cache mode
   - Other SQLite URI parameters

### Debug Mode
Set environment variable `MCP_DEBUG=1` to enable debug mode for detailed logging output.

## Architecture Design

### Core Concept: Abstraction Layer

```mermaid
graph TD
  Client[Client] --> DatabaseServer[Database Server]
  subgraph MCP Server
    DatabaseServer
    DatabaseHandler[Database Handler]
    PostgresHandler[PostgreSQL Handler]
    SQLiteHandler[SQLite Handler]
    DatabaseServer --> DatabaseHandler
    DatabaseHandler --> PostgresHandler
    DatabaseHandler --> SQLiteHandler
  end
  PostgresHandler --> PostgreSQL[(PostgreSQL)]
  SQLiteHandler --> SQLite[(SQLite)]
```

The abstraction layer design is the core architectural concept in MCP Database Utilities. Just like a universal remote control that works with different devices, users only need to know the basic operations without understanding the underlying complexities.

#### 1. Simplified User Interaction
- Users only need to know the database configuration name (e.g., "my_postgres")
- No need to deal with connection parameters and implementation details
- MCP server automatically handles database connections and queries

#### 2. Unified Interface Design
- DatabaseHandler abstract class defines unified operation interfaces
- All specific database implementations (PostgreSQL/SQLite) follow the same interface
- Users interact with different databases in the same way

#### 3. Configuration and Implementation Separation
- Complex database configuration parameters are encapsulated in configuration files
- Runtime access through simple database names
- Easy management and modification of database configurations without affecting business code

### System Components
1. DatabaseServer
   - Core component of the MCP server
   - Handles resource and tool requests
   - Manages database connection lifecycle

2. DatabaseHandler
   - Abstract base class defining unified interface
   - Includes get_tables(), get_schema(), execute_query(), etc.
   - Implemented by PostgreSQL and SQLite handlers

3. Configuration System
   - YAML-based configuration file
   - Support for multiple database configurations
   - Type-safe configuration validation

4. Error Handling and Logging
   - Unified error handling mechanism
   - Detailed logging output
   - Sensitive information masking

## Usage Examples

### Basic Query
```python
# Access through database name
async with server.get_handler("my_postgres") as handler:
    # Execute SQL query
    result = await handler.execute_query("SELECT * FROM users")
```

### View Table Structure
```python
# Get all tables
tables = await handler.get_tables()

# Get specific table schema
schema = await handler.get_schema("users")
```

### Error Handling
```python
try:
    async with server.get_handler("my_db") as handler:
        result = await handler.execute_query("SELECT * FROM users")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Query error: {e}")
```

## Security Notes
- Supports SELECT queries only to protect database security
- Automatically masks sensitive information (like passwords) in logs
- Executes queries in read-only transactions

## API Documentation

### DatabaseServer
Core server class providing:
- Resource list retrieval
- Tool call handling
- Database handler management

### DatabaseHandler
Abstract base class defining interfaces:
- get_tables(): Get table resource list
- get_schema(): Get table structure
- execute_query(): Execute SQL query
- cleanup(): Resource cleanup

### PostgreSQL Implementation
Provides PostgreSQL-specific features:
- Remote connection support
- Table description information
- Constraint queries

### SQLite Implementation
Provides SQLite-specific features:
- File path handling
- URI scheme support
- Password protection support (optional)

## Contributing
Contributions are welcome! Here's how you can help:

1. 🐛 Report bugs: Open an issue describing the bug and how to reproduce it
2. 💡 Suggest features: Open an issue to propose new features
3. 🛠️ Submit PRs: Fork the repo and create a pull request with your changes

### Development Setup
1. Clone the repository
2. Create a virtual environment using `uv venv`
3. Install dependencies with `uv sync --all-extras`
4. Run tests with `pytest`

For detailed guidelines, see [CONTRIBUTING.md](.github/CONTRIBUTING.md)

## Acknowledgments
- [MCP Servers](https://github.com/modelcontextprotocol/servers) for inspiration and demonstration
- AI Editors:
  * [Claude Desktop](https://claude.ai/download)
  * [5ire](https://5ire.app/)
  * [Cline](https://cline.bot)
- [Model Context Protocol](https://modelcontextprotocol.io/) for comprehensive interfaces

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=donghao1393/mcp-dbutils&type=Date)](https://star-history.com/#donghao1393/mcp-dbutils&Date)
