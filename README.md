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
- Database tables listing via MCP tools
- Intelligent connection management and resource cleanup
- Debug mode support
- SSL/TLS connection support for PostgreSQL

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
The project requires a YAML configuration file, specified via the `--config` parameter. Configuration examples:

```yaml
connections:
  # SQLite configuration examples
  dev-db:
    type: sqlite
    path: /path/to/dev.db
    # Password is optional
    password: 

  # PostgreSQL standard configuration
  test-db:
    type: postgres
    host: postgres.example.com
    port: 5432
    dbname: test_db
    user: test_user
    password: test_pass

  # PostgreSQL URL configuration with SSL
  prod-db:
    type: postgres
    url: postgresql://postgres.example.com:5432/prod-db?sslmode=verify-full
    user: prod_user
    password: prod_pass
    
  # PostgreSQL full SSL configuration example
  secure-db:
    type: postgres
    host: secure-db.example.com
    port: 5432
    dbname: secure_db
    user: secure_user
    password: secure_pass
    ssl:
      mode: verify-full  # disable/require/verify-ca/verify-full
      cert: /path/to/client-cert.pem
      key: /path/to/client-key.pem
      root: /path/to/root.crt
```

PostgreSQL SSL Configuration Options:
1. Using URL parameters:
   ```
   postgresql://host:port/dbname?sslmode=verify-full&sslcert=/path/to/cert.pem
   ```
2. Using dedicated SSL configuration section:
   ```yaml
   ssl:
     mode: verify-full  # SSL verification mode
     cert: /path/to/cert.pem      # Client certificate
     key: /path/to/key.pem        # Client private key
     root: /path/to/root.crt      # CA certificate
   ```

SSL Modes:
- disable: No SSL
- require: Use SSL but no certificate verification
- verify-ca: Verify server certificate is signed by trusted CA
- verify-full: Verify server certificate and hostname match

SQLite Configuration Options:
1. Basic configuration with path:
   ```yaml
   type: sqlite
   path: /path/to/db.sqlite
   password: optional_password  # Optional encryption
   ```
2. Using URI parameters:
   ```yaml
   type: sqlite
   path: /path/to/db.sqlite?mode=ro&cache=shared
   ```

### Debug Mode
Set environment variable `MCP_DEBUG=1` to enable debug mode for detailed logging output.

[Rest of the README content remains unchanged...]
