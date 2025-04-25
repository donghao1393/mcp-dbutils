# Installation Guide

*English | [中文](../zh/installation.md) | [Français](../fr/installation.md) | [Español](../es/installation.md) | [العربية](../ar/installation.md) | [Русский](../ru/installation.md)*


*English | [中文](../zh/installation.md) | [Français](../fr/installation.md) | [Español](../es/installation.md) | [العربية](../ar/installation.md) | [Русский](../ru/installation.md)*

This document provides simple, easy-to-follow steps to install and configure MCP Database Utilities, allowing your AI assistant to safely access and analyze your databases.

## What is MCP?

MCP (Model Context Protocol) is a protocol that allows AI applications (like Claude) to use external tools. MCP Database Utilities is one such tool that enables AI to read your database content without modifying any data.

## Before You Begin

Before starting the installation, please ensure you have:

- An MCP-compatible AI application (like Claude Desktop, Cursor, etc.)
- At least one database you want the AI to access (SQLite, MySQL, or PostgreSQL)

## Choose Your Installation Method

We offer four simple installation methods. Choose the **ONE** that works best for you:

| Installation Method | Best For | Advantages |
|---------|---------|------|
| **Option A: Using uvx** | Most users | Simple and quick, recommended |
| **Option B: Using Docker** | Users who prefer containerized apps | Isolated environment |
| **Option C: Using Smithery** | Claude Desktop users | One-click installation, easiest |
| **Option D: Offline Installation** | Users in environments without internet | No network connection needed |

## Option A: Using uvx (Recommended)

### Step 1: Install the uv tool

**On Mac or Linux**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**On Windows**:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, verify it's working by typing this command in your terminal:
```bash
uv --version
```
You should see something like `uv 0.5.5` in the output.

### Step 2: Create a database configuration file

1. Create a file named `config.yaml` on your computer
2. Copy the following content into the file (choose the one that matches your database type):

**SQLite Database Example**:
```yaml
connections:
  my_sqlite:
    type: sqlite
    path: C:/path/to/your/database.db
```

**PostgreSQL Database Example**:
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

**MySQL Database Example**:
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

> Please replace the example information with your actual database details. For more configuration options, see the [Configuration Guide](configuration.md).

### Step 3: Configure your AI application

#### Claude Desktop Configuration

1. Open the Claude Desktop application
2. Click the settings icon in the bottom left
3. Select "MCP Servers"
4. Click "Add Server"
5. Add the following configuration:

```json
"dbutils": {
  "command": "uvx",
  "args": [
    "mcp-dbutils",
    "--config",
    "C:/Users/YourUsername/config.yaml"
  ]
}
```

> Important: Replace `C:/Users/YourUsername/config.yaml` with the actual path to the configuration file you created in Step 2.

#### Cursor Configuration

1. Open the Cursor application
2. Go to "Settings" → "MCP"
3. Click "Add MCP Server"
4. Fill in the following information:
   - Name: `Database Utility MCP`
   - Type: `Command` (default)
   - Command: `uvx mcp-dbutils --config C:/Users/YourUsername/config.yaml`

> Important: Replace `C:/Users/YourUsername/config.yaml` with the actual path to the configuration file you created in Step 2.

## Option B: Using Docker

### Step 1: Install Docker

If you don't have Docker installed, download and install it from [docker.com](https://www.docker.com/products/docker-desktop/).

### Step 2: Create a database configuration file

Same as Step 2 in Option A, create a `config.yaml` file.

### Step 3: Configure your AI application

#### Claude Desktop Configuration

1. Open the Claude Desktop application
2. Click the settings icon in the bottom left
3. Select "MCP Servers"
4. Click "Add Server"
5. Add the following configuration:

```json
"dbutils": {
  "command": "docker",
  "args": [
    "run",
    "-i",
    "--rm",
    "-v",
    "C:/Users/YourUsername/config.yaml:/app/config.yaml",
    "mcp/dbutils",
    "--config",
    "/app/config.yaml"
  ]
}
```

> Important: Replace `C:/Users/YourUsername/config.yaml` with the actual path to the configuration file you created in Step 2.

#### Cursor Configuration

1. Open the Cursor application
2. Go to "Settings" → "MCP"
3. Click "Add MCP Server"
4. Fill in the following information:
   - Name: `Database Utility MCP`
   - Type: `Command` (default)
   - Command: `docker run -i --rm -v C:/Users/YourUsername/config.yaml:/app/config.yaml mcp/dbutils --config /app/config.yaml`

> Important: Replace `C:/Users/YourUsername/config.yaml` with the actual path to the configuration file you created in Step 2.

## Option C: Using Smithery (One-Click for Claude)

If you use Claude Desktop, this is the simplest installation method:

1. Make sure you have Node.js installed
2. Open a terminal or command prompt
3. Run the following command:

```bash
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

4. Follow the on-screen prompts to complete the installation

This method automatically handles all configuration, so you don't need to manually edit any files.

## Option D: Offline Installation

If you need to use the tool in an environment without internet access, or want to use a specific version:

### Step 1: Get the source code

In an environment with internet access:
1. Download the source code from GitHub: `git clone https://github.com/donghao1393/mcp-dbutils.git`
2. Or download a zip file from the [Releases page](https://github.com/donghao1393/mcp-dbutils/releases)
3. Copy the downloaded files to your offline environment

### Step 2: Create a database configuration file

Same as Step 2 in Option A, create a `config.yaml` file.

### Step 3: Configure your AI application

#### Claude Desktop Configuration

1. Open the Claude Desktop application
2. Click the settings icon in the bottom left
3. Select "MCP Servers"
4. Click "Add Server"
5. Add the following configuration:

```json
"dbutils": {
  "command": "uv",
  "args": [
    "--directory",
    "C:/Users/YourUsername/mcp-dbutils",
    "run",
    "mcp-dbutils",
    "--config",
    "C:/Users/YourUsername/config.yaml"
  ]
}
```

> Important: Replace the paths with the actual paths to your source code directory and configuration file.

## Verifying Your Installation

After completing the installation, let's verify that everything is working correctly:

### Testing the Connection

1. Open your AI application (Claude Desktop or Cursor)
2. Ask your AI: **"Can you check if you're able to connect to my database?"**
3. If configured correctly, the AI will respond that it has successfully connected to your database

### Try Simple Commands

Once connected, you can try these simple commands:

- **"List all tables in my database"**
- **"Describe the structure of the customers table"**
- **"Query the top 5 most expensive products in the products table"**

## Troubleshooting Common Issues

### Issue 1: AI Cannot Find the uvx Command

**Symptom**: AI responds with "uvx command not found" or similar error

**Solution**:
1. Confirm uv is properly installed: Run `uv --version` in your terminal
2. If installed but still getting errors, it might be an environment variable issue:
   - On Windows, check if the PATH environment variable includes the uv installation directory
   - On Mac/Linux, you might need to restart your terminal or run `source ~/.bashrc` or `source ~/.zshrc`

### Issue 2: Cannot Connect to Database

**Symptom**: AI reports it cannot connect to your database

**Solution**:
1. **Check if your database is running**: Make sure your database server is started
2. **Verify connection information**: Carefully check the host, port, username, and password in your config.yaml
3. **Check network settings**:
   - If using Docker, for local databases, use `host.docker.internal` as the hostname
   - Confirm that firewalls are not blocking the connection

### Issue 3: Configuration File Path Error

**Symptom**: AI reports it cannot find the configuration file

**Solution**:
1. **Use absolute paths**: Make sure you're using complete absolute paths in your AI application configuration
2. **Check file permissions**: Ensure the configuration file is readable by the current user
3. **Avoid special characters**: Don't use special characters or spaces in the path, or use quotes if necessary

### Issue 4: SQLite Database Path Problems

**Symptom**: Connection fails when using SQLite

**Solution**:
1. **Check file path**: Make sure the SQLite database file exists and the path is correct
2. **Check permissions**: Ensure the database file has read permissions
3. **When using Docker**: Make sure you've correctly mapped the SQLite file path

## Updating to the Latest Version

Regular updates provide new features and security fixes. Choose the update method that matches your installation method:

### Option A (uvx) Update

When you run MCP Database Utilities using the `uvx` command (e.g., `uvx mcp-dbutils`), it automatically uses the latest version without requiring manual updates.

If you're using the traditional installation method (not the `uvx` command), you can update manually with:

```bash
uv pip install -U mcp-dbutils
```

### Option B (Docker) Update

```bash
docker pull mcp/dbutils:latest
```

### Option C (Smithery) Update

```bash
npx -y @smithery/cli update @donghao1393/mcp-dbutils
```

### Option D (Offline) Update

1. Download the latest version of the source code in an environment with internet access
2. Replace the source code files in your offline environment

## Example Interactions

After successful installation, you can try these example conversations:

**You**: Can you list all tables in my database?

**AI**: Let me check your database. Here are the tables in your database:
- customers
- products
- orders
- inventory

**You**: What does the customers table look like?

**AI**: The customers table has the following structure:
- id (integer, primary key)
- name (text)
- email (text)
- registration_date (date)
- last_purchase (date)

**You**: How many customers made purchases in the last month?

**AI**: Let me run a query to find out... According to the data, 28 customers made purchases in the last month. The total value of these purchases was $15,742.50.