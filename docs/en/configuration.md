# Configuration Guide

*English | [中文](../zh/configuration.md) | [Français](../fr/configuration.md) | [Español](../es/configuration.md) | [العربية](../ar/configuration.md) | [Русский](../ru/configuration.md)*


*English | [中文](../zh/configuration.md) | [Français](../fr/configuration.md) | [Español](../es/configuration.md) | [العربية](../ar/configuration.md) | [Русский](../ru/configuration.md)*

This document provides various configuration examples for MCP Database Utilities, from basic setups to advanced scenarios, helping you correctly configure and optimize your database connections.

## Basic Configuration

### SQLite Basic Configuration

SQLite is a lightweight file-based database with a very simple configuration:

```yaml
connections:
  my-sqlite:
    type: sqlite
    path: /path/to/database.db
    # Optional: database encryption password
    password: optional_encryption_password
```

### PostgreSQL Basic Configuration

Standard PostgreSQL connection configuration:

```yaml
connections:
  my-postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: my_database
    user: postgres_user
    password: postgres_password
```

### MySQL Basic Configuration

Standard MySQL connection configuration:

```yaml
connections:
  my-mysql:
    type: mysql
    host: localhost
    port: 3306
    database: my_database
    user: mysql_user
    password: mysql_password
    charset: utf8mb4  # Recommended for full Unicode support
```

## Multiple Database Configuration

You can define multiple database connections in the same configuration file:

```yaml
connections:
  # Development SQLite database
  dev-db:
    type: sqlite
    path: /path/to/dev.db

  # Testing PostgreSQL database
  test-db:
    type: postgres
    host: test-postgres.example.com
    port: 5432
    dbname: test_db
    user: test_user
    password: test_pass

  # Production MySQL database
  prod-db:
    type: mysql
    host: prod-mysql.example.com
    port: 3306
    database: prod_db
    user: prod_user
    password: prod_pass
    charset: utf8mb4
```

## Advanced Configuration

### URL-Style Configuration

In addition to using standard configuration properties, you can also use database URLs for partial configuration. Best practice is to put the database connection structure in the URL, but keep sensitive information and specific parameters separate:

**PostgreSQL URL Configuration (Recommended Approach)**:

```yaml
connections:
  # Using URL for PostgreSQL (best practice)
  postgres-url:
    type: postgres
    url: postgresql://host:5432/dbname
    user: postgres_user
    password: postgres_password
    # Other parameters configured here
```

**MySQL URL Configuration (Recommended Approach)**:

```yaml
connections:
  # Using URL for MySQL (best practice)
  mysql-url:
    type: mysql
    url: mysql://host:3306/dbname
    user: mysql_user
    password: mysql_password
    charset: utf8mb4
```

**Legacy URL Configuration Style** (not recommended for production):

While the following approach works, it's not recommended for production environments due to the risk of special character parsing errors:

```yaml
connections:
  legacy-url:
    type: postgres
    url: postgresql://user:password@host:5432/dbname?param1=value1
    # Note: Not recommended to include credentials in URL
```

**When to Use URL vs. Standard Configuration**:
- URL configuration is suitable for:
  - When you already have a database connection string
  - Need to include specific connection parameters in the URL
  - Migrating from other systems with connection strings
- Standard configuration is suitable for:
  - Clearer configuration structure
  - Need to manage each configuration property separately
  - Easier to modify individual parameters without affecting the overall connection
  - Better security and maintainability

In any case, you should avoid including sensitive information (like usernames, passwords) in the URL and instead provide them separately in the configuration parameters.

### SSL/TLS Secure Connections

#### PostgreSQL SSL Configuration

**Using URL Parameters for SSL**:

```yaml
connections:
  pg-ssl-url:
    type: postgres
    url: postgresql://postgres.example.com:5432/secure_db?sslmode=verify-full&sslcert=/path/to/cert.pem&sslkey=/path/to/key.pem&sslrootcert=/path/to/root.crt
    user: secure_user
    password: secure_pass
```

**Using Dedicated SSL Configuration Section**:

```yaml
connections:
  pg-ssl-full:
    type: postgres
    host: secure-postgres.example.com
    port: 5432
    dbname: secure_db
    user: secure_user
    password: secure_pass
    ssl:
      mode: verify-full  # Most secure verification mode
      cert: /path/to/client-cert.pem  # Client certificate
      key: /path/to/client-key.pem    # Client private key
      root: /path/to/root.crt         # CA certificate
```

**PostgreSQL SSL Mode Explanation**:
- `disable`: No SSL used at all (not recommended for production)
- `require`: Use SSL but don't verify certificate (encryption only, no authentication)
- `verify-ca`: Verify server certificate is signed by a trusted CA
- `verify-full`: Verify server certificate and hostname match (most secure option)

#### MySQL SSL Configuration

**Using URL Parameters for SSL**:

```yaml
connections:
  mysql-ssl-url:
    type: mysql
    url: mysql://mysql.example.com:3306/secure_db?ssl-mode=verify_identity&ssl-ca=/path/to/ca.pem&ssl-cert=/path/to/client-cert.pem&ssl-key=/path/to/client-key.pem
    user: secure_user
    password: secure_pass
```

**Using Dedicated SSL Configuration Section**:

```yaml
connections:
  mysql-ssl-full:
    type: mysql
    host: secure-mysql.example.com
    port: 3306
    database: secure_db
    user: secure_user
    password: secure_pass
    charset: utf8mb4
    ssl:
      mode: verify_identity  # Most secure verification mode
      ca: /path/to/ca.pem         # CA certificate
      cert: /path/to/client-cert.pem  # Client certificate
      key: /path/to/client-key.pem    # Client private key
```

**MySQL SSL Mode Explanation**:
- `disabled`: No SSL used (not recommended for production)
- `preferred`: Use SSL if available, otherwise use non-encrypted connection
- `required`: SSL must be used, but don't verify server certificate
- `verify_ca`: Verify server certificate is signed by a trusted CA
- `verify_identity`: Verify server certificate and hostname match (most secure option)

### SQLite Advanced Configuration

**Using URI Parameters**:

```yaml
connections:
  sqlite-advanced:
    type: sqlite
    path: /path/to/db.sqlite?mode=ro&cache=shared&immutable=1
```

**Common SQLite URI Parameters**:
- `mode=ro`: Read-only mode (safe option)
- `cache=shared`: Shared cache mode, improves multi-threaded performance
- `immutable=1`: Mark database as immutable, improves performance
- `nolock=1`: Disable file locking (use only when certain no other connections exist)

## Docker Environment Special Configuration

When running in a Docker container, connecting to databases on the host requires special configuration:

### Connecting to PostgreSQL/MySQL on Host

**On macOS/Windows**:
Use the special hostname `host.docker.internal` to access the Docker host:

```yaml
connections:
  docker-postgres:
    type: postgres
    host: host.docker.internal  # Special DNS name pointing to Docker host
    port: 5432
    dbname: my_database
    user: postgres_user
    password: postgres_password
```

**On Linux**:
Use the Docker bridge IP or use host network mode:

```yaml
connections:
  docker-mysql:
    type: mysql
    host: 172.17.0.1  # Docker default bridge IP, points to host
    port: 3306
    database: my_database
    user: mysql_user
    password: mysql_password
```

Or use `--network="host"` when starting the Docker container, then use `localhost` as the hostname.

### SQLite Mapping

For SQLite, you need to map the database file into the container:

```bash
docker run -i --rm \
  -v /path/to/config.yaml:/app/config.yaml \
  -v /path/to/database.db:/app/database.db \
  mcp/dbutils --config /app/config.yaml
```

Then point to the mapped path in your configuration:

```yaml
connections:
  docker-sqlite:
    type: sqlite
    path: /app/database.db  # Path inside container, not host path
```

## Common Configuration Scenarios

### Multi-Environment Management

A good practice is to use clear naming conventions for different environments:

```yaml
connections:
  # Development environment
  dev-postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: dev_db
    user: dev_user
    password: dev_pass

  # Testing environment
  test-postgres:
    type: postgres
    host: test-server.example.com
    port: 5432
    dbname: test_db
    user: test_user
    password: test_pass

  # Production environment
  prod-postgres:
    type: postgres
    host: prod-db.example.com
    port: 5432
    dbname: prod_db
    user: prod_user
    password: prod_pass
    ssl:
      mode: verify-full
      cert: /path/to/cert.pem
      key: /path/to/key.pem
      root: /path/to/root.crt
```

### Read-Only and Analytics-Specific Configuration

For data analysis scenarios, it's recommended to use read-only accounts and optimized configuration:

```yaml
connections:
  analytics-mysql:
    type: mysql
    host: analytics-db.example.com
    port: 3306
    database: analytics
    user: analytics_readonly  # Use account with read-only permissions
    password: readonly_pass
    charset: utf8mb4
    # Set longer timeout suitable for data analysis
```

## Troubleshooting Tips

If your connection configuration isn't working, try:

1. **Verify Basic Connection**: Use the database's native client to verify the connection works
2. **Check Network Connectivity**: Ensure network ports are open, firewalls allow access
3. **Verify Credentials**: Confirm username and password are correct
4. **Path Issues**: For SQLite, ensure the path exists and has read permissions
5. **SSL Errors**: Check certificate paths and permissions, verify certificates aren't expired