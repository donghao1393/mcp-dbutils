# MCP Database Utilities

<!-- Project Status Badges -->
[![Build Status](https://img.shields.io/github/workflow/status/donghao1393/mcp-dbutils/Quality%20Assurance?label=tests)](https://github.com/donghao1393/mcp-dbutils/actions)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/donghao1393/bdd0a63ec2a816539ff8c136ceb41e48/raw/coverage.json)](https://github.com/donghao1393/mcp-dbutils/actions)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=donghao1393_mcp-dbutils&metric=alert_status)](https://sonarcloud.io/dashboard?id=donghao1393_mcp-dbutils)

<!-- Version and Installation Badges -->
[![PyPI version](https://img.shields.io/pypi/v/mcp-dbutils)](https://pypi.org/project/mcp-dbutils/)
[![PyPI downloads](https://img.shields.io/pypi/dm/mcp-dbutils)](https://pypi.org/project/mcp-dbutils/)
[![Smithery](https://smithery.ai/badge/@donghao1393/mcp-dbutils)](https://smithery.ai/server/@donghao1393/mcp-dbutils)

<!-- Technical Specification Badges -->
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/github/license/donghao1393/mcp-dbutils)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/donghao1393/mcp-dbutils?style=social)](https://github.com/donghao1393/mcp-dbutils/stargazers)

[中文](README.md) | [Français](README_FR.md) | [Español](README_ES.md) | [العربية](README_AR.md) | [Русский](README_RU.md) | [Documentation](#documentation)

## Introduction

MCP Database Utilities is an all-in-one MCP service that enables your AI to do data analysis by accessing versatile types of database (SQLite, MySQL, PostgreSQL, and more) within a unified connection configuration in a safe way.

Think of it as a secure bridge between AI systems and your databases, allowing AI to read and analyze your data without direct database access or risking data modifications.

### Key Features

- **Security First**: Strictly read-only operations, no direct database access, isolated connections, on-demand connectivity, automatic timeouts
- **Privacy Safeguards**: Local processing, minimal data exposure, credential protection, sensitive data masking
- **Multiple Database Support**: Connect to SQLite, MySQL, PostgreSQL with the same interface
- **Simple Configuration**: Single YAML file for all your database connections
- **Advanced Capabilities**: Table exploration, schema analysis, and query execution

> 🔒 **Security Note**: MCP Database Utilities is built with a security-first architecture, making it ideal for businesses, startups, and individuals who value data protection. Learn more about our [security architecture](docs/en/technical/security.md).

## Quick Start

We offer multiple installation methods, including uvx, Docker, and Smithery. For detailed installation and configuration steps, see the [Installation Guide](docs/en/installation.md).

### Basic Steps

1. **Install**: Choose your preferred installation method ([detailed instructions](docs/en/installation.md))
2. **Configure**: Create a YAML file with your database connection information ([configuration guide](docs/en/configuration.md))
3. **Connect**: Add the configuration to your AI client
4. **Use**: Start interacting with your databases ([usage guide](docs/en/usage.md))

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

- **dbutils-list-connections**: Lists all available database connections in your configuration
- **dbutils-list-tables**: Lists all tables in a database
- **dbutils-run-query**: Executes a SQL query (SELECT only)
- **dbutils-get-stats**: Gets statistics about a table
- **dbutils-list-constraints**: Lists table constraints
- **dbutils-explain-query**: Gets query execution plan
- **dbutils-get-performance**: Gets database performance metrics
- **dbutils-analyze-query**: Analyzes queries for optimization



## Documentation

### Getting Started
- [Installation Guide](docs/en/installation.md) - Detailed installation steps and configuration instructions
- [Platform-Specific Installation Guide](docs/en/installation-platform-specific.md) - Installation instructions for different operating systems
- [Configuration Guide](docs/en/configuration.md) - Database connection configuration examples and best practices
- [Usage Guide](docs/en/usage.md) - Basic workflow and common usage scenarios

### Technical Documentation
- [Architecture Design](docs/en/technical/architecture.md) - System architecture and components
- [Security Architecture](docs/en/technical/security.md) - Security features and protection mechanisms
- [Development Guide](docs/en/technical/development.md) - Code quality and development workflow
- [Testing Guide](docs/en/technical/testing.md) - Testing framework and best practices
- [SonarCloud Integration](docs/en/technical/sonarcloud-integration.md) - SonarCloud and AI integration guide

### Example Documentation
- [SQLite Examples](docs/en/examples/sqlite-examples.md) - SQLite database operation examples
- [PostgreSQL Examples](docs/en/examples/postgresql-examples.md) - PostgreSQL database operation examples
- [MySQL Examples](docs/en/examples/mysql-examples.md) - MySQL database operation examples
- [Advanced LLM Interactions](docs/en/examples/advanced-llm-interactions.md) - Advanced interaction examples with various LLMs

### Support & Feedback
- [GitHub Issues](https://github.com/donghao1393/mcp-dbutils/issues) - Report issues or request features
- [Smithery](https://smithery.ai/server/@donghao1393/mcp-dbutils) - Simplified installation and updates

## Star History

[![Star History Chart](https://starchart.cc/donghao1393/mcp-dbutils.svg?variant=adaptive)](https://starchart.cc/donghao1393/mcp-dbutils)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
