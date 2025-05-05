"""Connection server base class"""

import json
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from datetime import datetime
from importlib.metadata import metadata
from typing import Any, AsyncContextManager, Dict

import mcp.server.stdio
import mcp.types as types
import yaml
from mcp.server import Server

from .audit import format_logs, get_logs, log_write_operation
from .log import create_logger
from .stats import ResourceStats


class ConnectionHandlerError(Exception):
    """Base exception for connection errors"""

    pass


class ConfigurationError(ConnectionHandlerError):
    """Configuration related errors"""

    pass


class ConnectionError(ConnectionHandlerError):
    """Connection related errors"""

    pass


# 常量定义
DATABASE_CONNECTION_NAME = "Database connection name"
EMPTY_QUERY_ERROR = "SQL query cannot be empty"
SQL_QUERY_REQUIRED_ERROR = "SQL query required for explain-query tool"
EMPTY_TABLE_NAME_ERROR = "Table name cannot be empty"
CONNECTION_NAME_REQUIRED_ERROR = "Connection name must be specified"
SELECT_ONLY_ERROR = "Only SELECT queries are supported for security reasons"
INVALID_URI_FORMAT_ERROR = "Invalid resource URI format"
CONNECTION_NOT_WRITABLE_ERROR = "This connection is not configured for write operations. Add 'writable: true' to the connection configuration."
WRITE_OPERATION_NOT_ALLOWED_ERROR = "No permission to perform {operation} operation on table {table}."
WRITE_CONFIRMATION_REQUIRED_ERROR = "Operation not confirmed. To execute write operations, you must set confirmation='CONFIRM_WRITE'."
UNSUPPORTED_WRITE_OPERATION_ERROR = "Unsupported SQL operation: {operation}. Only INSERT, UPDATE, DELETE are supported."

# 获取包信息用于日志命名
pkg_meta = metadata("mcp-dbutils")

# 日志名称常量
LOG_NAME = "dbutils"

# MCP日志级别常量
LOG_LEVEL_DEBUG = "debug"  # 0
LOG_LEVEL_INFO = "info"  # 1
LOG_LEVEL_NOTICE = "notice"  # 2
LOG_LEVEL_WARNING = "warning"  # 3
LOG_LEVEL_ERROR = "error"  # 4
LOG_LEVEL_CRITICAL = "critical"  # 5
LOG_LEVEL_ALERT = "alert"  # 6
LOG_LEVEL_EMERGENCY = "emergency"  # 7


class ConnectionHandler(ABC):
    """Abstract base class defining common interface for connection handlers"""

    def __init__(self, config_path: str, connection: str, debug: bool = False):
        """Initialize connection handler

        Args:
            config_path: Path to configuration file
            connection: str = DATABASE_CONNECTION_NAME
            debug: Enable debug mode
        """
        self.config_path = config_path
        self.connection = connection
        self.debug = debug
        # 创建stderr日志记录器用于本地调试
        self.log = create_logger(f"{LOG_NAME}.handler.{connection}", debug)
        self.stats = ResourceStats()
        self._session = None

    def send_log(self, level: str, message: str):
        """通过MCP发送日志消息和写入stderr

        Args:
            level: 日志级别 (debug/info/notice/warning/error/critical/alert/emergency)
            message: 日志内容
        """
        # 本地stderr日志
        self.log(level, message)

        # MCP日志通知
        if self._session and hasattr(self._session, "request_context"):
            self._session.request_context.session.send_log_message(
                level=level, data=message
            )

    @property
    @abstractmethod
    def db_type(self) -> str:
        """Return database type"""
        pass

    @abstractmethod
    async def get_tables(self) -> list[types.Resource]:
        """Get list of table resources from database connection"""
        pass

    @abstractmethod
    async def get_schema(self, table_name: str) -> str:
        """Get schema information for specified table"""
        pass

    @abstractmethod
    async def _execute_query(self, sql: str) -> str:
        """Internal query execution method to be implemented by subclasses"""
        pass

    @abstractmethod
    async def _execute_write_query(self, sql: str) -> str:
        """Internal write query execution method to be implemented by subclasses"""
        pass

    async def execute_query(self, sql: str) -> str:
        """Execute SQL query with performance tracking"""
        start_time = datetime.now()
        try:
            self.stats.record_query()
            result = await self._execute_query(sql)
            duration = (datetime.now() - start_time).total_seconds()
            self.stats.record_query_duration(sql, duration)
            self.stats.update_memory_usage(result)
            self.send_log(
                LOG_LEVEL_INFO,
                f"Query executed in {duration * 1000:.2f}ms. Resource stats: {json.dumps(self.stats.to_dict())}",
            )
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.stats.record_error(e.__class__.__name__)
            self.send_log(
                LOG_LEVEL_ERROR,
                f"Query error after {duration * 1000:.2f}ms - {str(e)}\nResource stats: {json.dumps(self.stats.to_dict())}",
            )
            raise

    async def execute_write_query(self, sql: str) -> str:
        """Execute SQL write query with performance tracking

        Args:
            sql: SQL write query (INSERT, UPDATE, DELETE)

        Returns:
            str: Execution result

        Raises:
            ValueError: If the SQL is not a write operation
        """
        # Validate SQL type
        sql_type = self._get_sql_type(sql)
        if sql_type not in ["INSERT", "UPDATE", "DELETE"]:
            raise ValueError(UNSUPPORTED_WRITE_OPERATION_ERROR.format(operation=sql_type))

        # Extract table name
        table_name = self._extract_table_name(sql)

        start_time = datetime.now()
        affected_rows = 0
        status = "SUCCESS"
        error_message = None

        try:
            self.stats.record_query()
            self.send_log(
                LOG_LEVEL_INFO,
                f"Executing write operation: {sql_type} on table {table_name}",
            )

            result = await self._execute_write_query(sql)

            # 尝试从结果中提取受影响的行数
            try:
                if "row" in result and "affected" in result:
                    # 从结果字符串中提取受影响的行数
                    import re
                    # 限制数字长度，避免DoS风险
                    match = re.search(r"(\d{1,10}) rows?", result)
                    if match:
                        affected_rows = int(match.group(1))
            except Exception:
                # 如果无法提取，使用默认值
                affected_rows = 1

            duration = (datetime.now() - start_time).total_seconds()
            self.stats.record_query_duration(sql, duration)
            self.stats.update_memory_usage(result)

            # 记录审计日志
            log_write_operation(
                connection_name=self.connection,
                table_name=table_name,
                operation_type=sql_type,
                sql=sql,
                affected_rows=affected_rows,
                execution_time=duration * 1000,  # 转换为毫秒
                status=status,
                error_message=error_message
            )

            self.send_log(
                LOG_LEVEL_INFO,
                f"Write operation executed in {duration * 1000:.2f}ms. Resource stats: {json.dumps(self.stats.to_dict())}",
            )
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.stats.record_error(e.__class__.__name__)
            status = "FAILED"
            error_message = str(e)

            # 记录审计日志（失败）
            log_write_operation(
                connection_name=self.connection,
                table_name=table_name,
                operation_type=sql_type,
                sql=sql,
                affected_rows=0,
                execution_time=duration * 1000,  # 转换为毫秒
                status=status,
                error_message=error_message
            )

            self.send_log(
                LOG_LEVEL_ERROR,
                f"Write operation error after {duration * 1000:.2f}ms - {str(e)}\nResource stats: {json.dumps(self.stats.to_dict())}",
            )
            raise

    def _get_sql_type(self, sql: str) -> str:
        """Get SQL statement type

        Args:
            sql: SQL statement

        Returns:
            str: SQL statement type (SELECT, INSERT, UPDATE, DELETE, etc.)
        """
        sql = sql.strip().upper()
        if sql.startswith("SELECT"):
            return "SELECT"
        elif sql.startswith("INSERT"):
            return "INSERT"
        elif sql.startswith("UPDATE"):
            return "UPDATE"
        elif sql.startswith("DELETE"):
            return "DELETE"
        elif sql.startswith("CREATE"):
            return "CREATE"
        elif sql.startswith("ALTER"):
            return "ALTER"
        elif sql.startswith("DROP"):
            return "DROP"
        elif sql.startswith("TRUNCATE"):
            return "TRUNCATE"
        elif sql.startswith("BEGIN") or sql.startswith("START"):
            return "TRANSACTION_START"
        elif sql.startswith("COMMIT"):
            return "TRANSACTION_COMMIT"
        elif sql.startswith("ROLLBACK"):
            return "TRANSACTION_ROLLBACK"
        else:
            return "UNKNOWN"

    def _extract_table_name(self, sql: str) -> str:
        """Extract table name from SQL statement

        This is a simple implementation that works for basic SQL statements.
        Subclasses may override this method to provide more accurate table name extraction.

        Args:
            sql: SQL statement

        Returns:
            str: Table name
        """
        sql_type = self._get_sql_type(sql)
        sql = sql.strip()

        if sql_type == "INSERT":
            # INSERT INTO table_name ...
            match = sql.upper().split("INTO", 1)
            if len(match) > 1:
                table_part = match[1].strip().split(" ", 1)[0]
                return table_part.strip('`"[]')
        elif sql_type == "UPDATE":
            # UPDATE table_name ...
            match = sql.upper().split("UPDATE", 1)
            if len(match) > 1:
                table_part = match[1].strip().split(" ", 1)[0]
                return table_part.strip('`"[]')
        elif sql_type == "DELETE":
            # DELETE FROM table_name ...
            match = sql.upper().split("FROM", 1)
            if len(match) > 1:
                table_part = match[1].strip().split(" ", 1)[0]
                return table_part.strip('`"[]')

        # Default fallback
        return "unknown_table"

    @abstractmethod
    async def get_table_description(self, table_name: str) -> str:
        """Get detailed table description including columns, types, and comments

        Args:
            table_name: Name of the table to describe

        Returns:
            Formatted table description
        """
        pass

    @abstractmethod
    async def get_table_ddl(self, table_name: str) -> str:
        """Get DDL statement for table including columns, constraints and indexes

        Args:
            table_name: Name of the table to get DDL for

        Returns:
            DDL statement as string
        """
        pass

    @abstractmethod
    async def get_table_indexes(self, table_name: str) -> str:
        """Get index information for table

        Args:
            table_name: Name of the table to get indexes for

        Returns:
            Formatted index information
        """
        pass

    @abstractmethod
    async def get_table_stats(self, table_name: str) -> str:
        """Get table statistics information

        Args:
            table_name: Name of the table to get statistics for

        Returns:
            Formatted statistics information including row count, size, etc.
        """
        pass

    @abstractmethod
    async def get_table_constraints(self, table_name: str) -> str:
        """Get constraint information for table

        Args:
            table_name: Name of the table to get constraints for

        Returns:
            Formatted constraint information including primary keys, foreign keys, etc.
        """
        pass

    @abstractmethod
    async def explain_query(self, sql: str) -> str:
        """Get query execution plan

        Args:
            sql: SQL query to explain

        Returns:
            Formatted query execution plan with cost estimates
        """
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test database connection

        Returns:
            bool: True if connection is successful, False otherwise
        """
        pass

    @abstractmethod
    async def cleanup(self):
        """Cleanup resources"""
        pass

    async def execute_tool_query(
        self, tool_name: str, table_name: str = "", sql: str = ""
    ) -> str:
        """Execute a tool query and return formatted result

        Args:
            tool_name: Name of the tool to execute
            table_name: Name of the table to query (for table-related tools)
            sql: SQL query (for query-related tools)

        Returns:
            Formatted query result
        """
        try:
            self.stats.record_query()

            if tool_name == "dbutils-describe-table":
                result = await self.get_table_description(table_name)
            elif tool_name == "dbutils-get-ddl":
                result = await self.get_table_ddl(table_name)
            elif tool_name == "dbutils-list-indexes":
                result = await self.get_table_indexes(table_name)
            elif tool_name == "dbutils-get-stats":
                result = await self.get_table_stats(table_name)
            elif tool_name == "dbutils-list-constraints":
                result = await self.get_table_constraints(table_name)
            elif tool_name == "dbutils-explain-query":
                if not sql:
                    raise ValueError(SQL_QUERY_REQUIRED_ERROR)
                result = await self.explain_query(sql)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

            self.stats.update_memory_usage(result)
            self.send_log(
                LOG_LEVEL_INFO, f"Resource stats: {json.dumps(self.stats.to_dict())}"
            )
            return f"[{self.db_type}]\n{result}"

        except Exception as e:
            self.stats.record_error(e.__class__.__name__)
            self.send_log(
                LOG_LEVEL_ERROR,
                f"Tool error - {str(e)}\nResource stats: {json.dumps(self.stats.to_dict())}",
            )
            raise


class ConnectionServer:
    """Unified connection server class"""

    def __init__(self, config_path: str, debug: bool = False):
        """Initialize connection server

        Args:
            config_path: Path to configuration file
            debug: Enable debug mode
        """
        self.config_path = config_path
        self.debug = debug
        # 获取包信息用于服务器配置
        pkg_meta = metadata("mcp-dbutils")
        self.logger = create_logger(f"{LOG_NAME}.server", debug)
        self.server = Server(name=LOG_NAME, version=pkg_meta["Version"])
        self._session = None
        self._setup_handlers()
        self._setup_prompts()

    def send_log(self, level: str, message: str):
        """通过MCP发送日志消息和写入stderr

        Args:
            level: 日志级别 (debug/info/notice/warning/error/critical/alert/emergency)
            message: 日志内容
        """
        # 本地stderr日志
        self.logger(level, message)

        # MCP日志通知
        if hasattr(self.server, "session") and self.server.session:
            try:
                self.server.session.send_log_message(level=level, data=message)
            except Exception as e:
                self.logger("error", f"Failed to send MCP log message: {str(e)}")

    def _setup_prompts(self):
        """Setup prompts handlers"""

        @self.server.list_prompts()
        async def handle_list_prompts() -> list[types.Prompt]:
            """Handle prompts/list request"""
            try:
                self.send_log(LOG_LEVEL_DEBUG, "Handling list_prompts request")
                return []
            except Exception as e:
                self.send_log(LOG_LEVEL_ERROR, f"Error in list_prompts: {str(e)}")
                raise

    def _get_config_or_raise(self, connection: str) -> dict:
        """读取配置文件并验证连接配置

        Args:
            connection: 连接名称

        Returns:
            dict: 连接配置

        Raises:
            ConfigurationError: 如果配置文件格式不正确或连接不存在
        """
        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)
            if not config or "connections" not in config:
                raise ConfigurationError(
                    "Configuration file must contain 'connections' section"
                )
            if connection not in config["connections"]:
                available_connections = list(config["connections"].keys())
                raise ConfigurationError(
                    f"Connection not found: {connection}. Available connections: {available_connections}"
                )

            db_config = config["connections"][connection]

            if "type" not in db_config:
                raise ConfigurationError(
                    "Database configuration must include 'type' field"
                )

            return db_config

    def _get_sql_type(self, sql: str) -> str:
        """Get SQL statement type

        Args:
            sql: SQL statement

        Returns:
            str: SQL statement type (SELECT, INSERT, UPDATE, DELETE, etc.)
        """
        sql = sql.strip().upper()
        if sql.startswith("SELECT"):
            return "SELECT"
        elif sql.startswith("INSERT"):
            return "INSERT"
        elif sql.startswith("UPDATE"):
            return "UPDATE"
        elif sql.startswith("DELETE"):
            return "DELETE"
        elif sql.startswith("CREATE"):
            return "CREATE"
        elif sql.startswith("ALTER"):
            return "ALTER"
        elif sql.startswith("DROP"):
            return "DROP"
        elif sql.startswith("TRUNCATE"):
            return "TRUNCATE"
        elif sql.startswith("BEGIN") or sql.startswith("START"):
            return "TRANSACTION_START"
        elif sql.startswith("COMMIT"):
            return "TRANSACTION_COMMIT"
        elif sql.startswith("ROLLBACK"):
            return "TRANSACTION_ROLLBACK"
        else:
            return "UNKNOWN"

    def _extract_table_name(self, sql: str) -> str:
        """Extract table name from SQL statement

        This is a simple implementation that works for basic SQL statements.
        Handles multi-line SQL statements by normalizing whitespace.

        Args:
            sql: SQL statement

        Returns:
            str: Table name
        """
        sql_type = self._get_sql_type(sql)

        # 预处理SQL：规范化空白字符，将多行SQL转换为单行
        # 将所有连续的空白字符（包括换行符、制表符等）替换为单个空格
        normalized_sql = " ".join(sql.split())

        if sql_type == "INSERT":
            # INSERT INTO table_name ...
            match = normalized_sql.upper().split("INTO", 1)
            if len(match) > 1:
                table_part = match[1].strip().split(" ", 1)[0]
                return table_part.strip('`"[]')
        elif sql_type == "UPDATE":
            # UPDATE table_name ...
            match = normalized_sql.upper().split("UPDATE", 1)
            if len(match) > 1:
                table_part = match[1].strip().split(" ", 1)[0]
                return table_part.strip('`"[]')
        elif sql_type == "DELETE":
            # DELETE FROM table_name ...
            match = normalized_sql.upper().split("FROM", 1)
            if len(match) > 1:
                table_part = match[1].strip().split(" ", 1)[0]
                return table_part.strip('`"[]')

        # Default fallback
        return "unknown_table"

    async def _check_write_permission(self, connection: str, table_name: str, operation_type: str) -> None:
        """检查写操作权限

        Args:
            connection: 数据库连接名称
            table_name: 表名
            operation_type: 操作类型 (INSERT, UPDATE, DELETE)

        Raises:
            ConfigurationError: 如果连接不可写或没有表级权限
        """
        # 获取连接配置
        db_config = self._get_config_or_raise(connection)

        # 检查连接是否可写
        if not db_config.get("writable", False):
            raise ConfigurationError(CONNECTION_NOT_WRITABLE_ERROR)

        # 检查是否有写权限配置
        write_permissions = db_config.get("write_permissions", {})
        if not write_permissions:
            # 没有细粒度权限控制，默认允许所有写操作
            return

        # 将表名转换为小写，用于大小写不敏感的比较
        table_name_lower = table_name.lower()

        # 检查表级权限
        tables = write_permissions.get("tables", {})
        if not tables:
            # 没有表级权限配置，检查默认策略
            default_policy = write_permissions.get("default_policy", "read_only")
            if default_policy == "allow_all":
                return
            else:
                # 默认只读
                raise ConfigurationError(WRITE_OPERATION_NOT_ALLOWED_ERROR.format(
                    operation=operation_type, table=table_name
                ))

        # 创建表名到配置的映射，支持大小写不敏感的比较
        tables_lower = {k.lower(): v for k, v in tables.items()}

        # 检查特定表的权限（大小写不敏感）
        if table_name_lower in tables_lower:
            table_config = tables_lower[table_name_lower]
            operations = table_config.get("operations", ["INSERT", "UPDATE", "DELETE"])
            if operation_type in operations:
                return
            else:
                raise ConfigurationError(WRITE_OPERATION_NOT_ALLOWED_ERROR.format(
                    operation=operation_type, table=table_name
                ))
        else:
            # 表未明确配置，检查默认策略
            default_policy = write_permissions.get("default_policy", "read_only")
            if default_policy == "allow_all":
                return
            else:
                # 默认只读
                raise ConfigurationError(WRITE_OPERATION_NOT_ALLOWED_ERROR.format(
                    operation=operation_type, table=table_name
                ))

    def _create_handler_for_type(
        self, db_type: str, connection: str
    ) -> ConnectionHandler:
        """基于数据库类型创建相应的处理器

        Args:
            db_type: 数据库类型
            connection: 连接名称

        Returns:
            ConnectionHandler: 数据库连接处理器

        Raises:
            ConfigurationError: 如果数据库类型不支持或导入失败
        """
        self.send_log(LOG_LEVEL_DEBUG, f"Creating handler for database type: {db_type}")

        try:
            if db_type == "sqlite":
                from .sqlite.handler import SQLiteHandler

                return SQLiteHandler(self.config_path, connection, self.debug)
            elif db_type == "postgres":
                from .postgres.handler import PostgreSQLHandler

                return PostgreSQLHandler(self.config_path, connection, self.debug)
            elif db_type == "mysql":
                from .mysql.handler import MySQLHandler

                return MySQLHandler(self.config_path, connection, self.debug)
            else:
                raise ConfigurationError(f"Unsupported database type: {db_type}")
        except ImportError as e:
            # 捕获导入错误并转换为ConfigurationError，以保持与现有测试兼容
            raise ConfigurationError(
                f"Failed to import handler for {db_type}: {str(e)}"
            )

    @asynccontextmanager
    async def get_handler(
        self, connection: str
    ) -> AsyncContextManager[ConnectionHandler]:
        """Get connection handler

        Get appropriate connection handler based on connection name

        Args:
            connection: str = DATABASE_CONNECTION_NAME

        Returns:
            AsyncContextManager[ConnectionHandler]: Context manager for connection handler
        """
        # Read configuration file and validate connection
        db_config = self._get_config_or_raise(connection)

        # Create appropriate handler based on database type
        handler = None
        try:
            db_type = db_config["type"]
            handler = self._create_handler_for_type(db_type, connection)

            # Set session for MCP logging
            if hasattr(self.server, "session"):
                handler._session = self.server.session

            handler.stats.record_connection_start()
            self.send_log(
                LOG_LEVEL_DEBUG, f"Handler created successfully for {connection}"
            )

            yield handler
        finally:
            if handler:
                self.send_log(LOG_LEVEL_DEBUG, f"Cleaning up handler for {connection}")
                handler.stats.record_connection_end()

                if hasattr(handler, "cleanup") and callable(handler.cleanup):
                    await handler.cleanup()

    def _get_available_tools(self) -> list[types.Tool]:
        """返回所有可用的数据库工具列表

        Returns:
            list[types.Tool]: 工具列表
        """
        return [
            types.Tool(
                name="dbutils-list-connections",
                description="Lists all available database connections defined in the configuration with detailed information including database type, host, port, and database name, while hiding sensitive information like passwords. The optional check_status parameter allows verifying if each connection is available, though this may increase response time. Use this tool when you need to understand available database resources or diagnose connection issues.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "check_status": {
                            "type": "boolean",
                            "description": "Whether to check connection status (may be slow with many connections)",
                            "default": False,
                        }
                    },
                    "required": [],
                },
            ),
            types.Tool(
                name="dbutils-execute-write",
                description="CAUTION: This tool executes data modification operations (INSERT, UPDATE, DELETE) on the specified database. It requires explicit configuration and confirmation. Only available for connections with 'writable: true' in configuration. All operations are logged for audit purposes.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "string",
                            "description": DATABASE_CONNECTION_NAME,
                        },
                        "sql": {
                            "type": "string",
                            "description": "SQL statement (INSERT, UPDATE, DELETE)",
                        },
                        "confirmation": {
                            "type": "string",
                            "description": "Type 'CONFIRM_WRITE' to confirm you understand the risks",
                        },
                    },
                    "required": ["connection", "sql", "confirmation"],
                },
                annotations={
                    "examples": [
                        {
                            "input": {
                                "connection": "example_db",
                                "sql": "INSERT INTO logs (event, timestamp) VALUES ('event1', CURRENT_TIMESTAMP)",
                                "confirmation": "CONFIRM_WRITE"
                            },
                            "output": "Write operation executed successfully. 1 row affected."
                        },
                        {
                            "input": {
                                "connection": "example_db",
                                "sql": "UPDATE users SET status = 'active' WHERE id = 123",
                                "confirmation": "CONFIRM_WRITE"
                            },
                            "output": "Write operation executed successfully. 1 row affected."
                        }
                    ],
                    "usage_tips": [
                        "Always confirm with 'CONFIRM_WRITE' to execute write operations",
                        "Connection must have 'writable: true' in configuration",
                        "Consider using transactions for multiple related operations",
                        "Check audit logs after write operations to verify changes"
                    ]
                }
            ),
            types.Tool(
                name="dbutils-run-query",
                description="Executes read-only SQL queries on the specified database connection. For security, only SELECT statements are supported. Returns structured results with column names and data rows. Supports complex queries including JOINs, GROUP BY, ORDER BY, and aggregate functions. Use this tool when you need to analyze data, validate hypotheses, or extract specific information. Query execution is protected by resource limits and timeouts to prevent system resource overuse.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "string",
                            "description": DATABASE_CONNECTION_NAME,
                        },
                        "sql": {
                            "type": "string",
                            "description": "SQL query (SELECT only)",
                        },
                    },
                    "required": ["connection", "sql"],
                },
                annotations={
                    "examples": [
                        {
                            "input": {
                                "connection": "example_db",
                                "sql": "SELECT id, name, email FROM users LIMIT 10"
                            },
                            "output": "Results showing first 10 users with their IDs, names, and email addresses"
                        },
                        {
                            "input": {
                                "connection": "example_db",
                                "sql": "SELECT department, COUNT(*) as employee_count FROM employees GROUP BY department ORDER BY employee_count DESC"
                            },
                            "output": "Results showing departments and their employee counts in descending order"
                        }
                    ],
                    "usage_tips": [
                        "Always use SELECT statements only - other SQL operations are not permitted",
                        "Use LIMIT to restrict large result sets",
                        "For complex queries, consider using dbutils-explain-query first to understand query execution plan"
                    ]
                }
            ),
            types.Tool(
                name="dbutils-list-tables",
                description="Lists all tables in the specified database connection. Results include table names, URIs, and available table descriptions. Results are grouped by database type and clearly labeled for easy identification. Use this tool when you need to understand database structure or locate specific tables. Only works within the allowed connection scope.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "string",
                            "description": DATABASE_CONNECTION_NAME,
                        }
                    },
                    "required": ["connection"],
                },
                annotations={
                    "examples": [
                        {
                            "input": {"connection": "example_db"},
                            "output": "List of tables in the example_db database with their URIs and descriptions"
                        }
                    ],
                    "usage_tips": [
                        "Use this tool first when exploring a new database to understand its structure",
                        "After listing tables, use dbutils-describe-table to get detailed information about specific tables",
                        "Table URIs can be used with other database tools for further operations"
                    ]
                }
            ),
            types.Tool(
                name="dbutils-describe-table",
                description="Provides detailed information about a table's structure, including column names, data types, nullability, default values, and comments. Results are formatted as an easy-to-read hierarchy that clearly displays all column attributes. Use this tool when you need to understand table structure in depth, analyze data models, or prepare queries. Supports all major database types with consistent output format.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "string",
                            "description": DATABASE_CONNECTION_NAME,
                        },
                        "table": {
                            "type": "string",
                            "description": "Table name to describe",
                        },
                    },
                    "required": ["connection", "table"],
                },
            ),
            types.Tool(
                name="dbutils-get-ddl",
                description="Retrieves the complete DDL (Data Definition Language) statement for creating the specified table. Returns the original CREATE TABLE statement including all column definitions, constraints, indexes, and table options. This tool is valuable when you need to understand the complete table structure, replicate table structure, or perform database migrations. Note that DDL statement format varies by database type.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "string",
                            "description": DATABASE_CONNECTION_NAME,
                        },
                        "table": {
                            "type": "string",
                            "description": "Table name to get DDL for",
                        },
                    },
                    "required": ["connection", "table"],
                },
            ),
            types.Tool(
                name="dbutils-list-indexes",
                description="Lists all indexes on the specified table, including index names, types (unique/non-unique), index methods (e.g., B-tree), and included columns. Results are grouped by index name, clearly showing the structure of multi-column indexes. Use this tool when you need to optimize query performance, understand table access patterns, or diagnose performance issues.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "string",
                            "description": DATABASE_CONNECTION_NAME,
                        },
                        "table": {
                            "type": "string",
                            "description": "Table name to list indexes for",
                        },
                    },
                    "required": ["connection", "table"],
                },
            ),
            types.Tool(
                name="dbutils-get-stats",
                description="Retrieves statistical information about the table, including estimated row count, average row length, data size, index size, and column information. These statistics are valuable for understanding table size, growth trends, and storage characteristics. Use this tool when you need to perform capacity planning, performance optimization, or database maintenance. Note that the precision and availability of statistics may vary by database type.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "string",
                            "description": DATABASE_CONNECTION_NAME,
                        },
                        "table": {
                            "type": "string",
                            "description": "Table name to get statistics for",
                        },
                    },
                    "required": ["connection", "table"],
                },
            ),
            types.Tool(
                name="dbutils-list-constraints",
                description="Lists all constraints on the table, including primary keys, foreign keys, unique constraints, and check constraints. Results are grouped by constraint type, clearly showing constraint names and involved columns. For foreign key constraints, referenced tables and columns are also displayed. Use this tool when you need to understand data integrity rules, table relationships, or data validation logic.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "string",
                            "description": DATABASE_CONNECTION_NAME,
                        },
                        "table": {
                            "type": "string",
                            "description": "Table name to list constraints for",
                        },
                    },
                    "required": ["connection", "table"],
                },
            ),
            types.Tool(
                name="dbutils-explain-query",
                description="Provides the execution plan for a SQL query, showing how the database engine will process the query. Returns detailed execution plan including access methods, join types, sort operations, and estimated costs. Also provides actual execution statistics where available. Use this tool when you need to optimize query performance, understand complex query behavior, or diagnose slow queries. Note that execution plan format varies by database type.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "string",
                            "description": DATABASE_CONNECTION_NAME,
                        },
                        "sql": {
                            "type": "string",
                            "description": "SQL query to explain",
                        },
                    },
                    "required": ["connection", "sql"],
                },
            ),
            types.Tool(
                name="dbutils-get-performance",
                description="Retrieves performance metrics for the database connection, including query count, average execution time, memory usage, and error statistics. These metrics reflect the resource usage of the current session and help monitor and optimize database operations. Use this tool when you need to evaluate query efficiency, identify performance bottlenecks, or monitor resource usage.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "string",
                            "description": DATABASE_CONNECTION_NAME,
                        }
                    },
                    "required": ["connection"],
                },
            ),
            types.Tool(
                name="dbutils-analyze-query",
                description="Analyzes the performance characteristics of a SQL query, providing execution plan, actual execution time, and optimization suggestions. The tool executes the query (SELECT statements only) and measures performance, then provides specific optimization recommendations based on the results, such as adding indexes, restructuring join conditions, or adjusting query structure. Use this tool when you need to improve query performance, understand performance bottlenecks, or learn query optimization techniques.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "string",
                            "description": DATABASE_CONNECTION_NAME,
                        },
                        "sql": {
                            "type": "string",
                            "description": "SQL query to analyze",
                        },
                    },
                    "required": ["connection", "sql"],
                },
            ),
            types.Tool(
                name="dbutils-get-audit-logs",
                description="Retrieves audit logs for database write operations. Shows who performed what operations, when, and with what results. Useful for security monitoring, compliance, and troubleshooting.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "string",
                            "description": "Filter logs by connection name",
                        },
                        "table": {
                            "type": "string",
                            "description": "Filter logs by table name",
                        },
                        "operation_type": {
                            "type": "string",
                            "description": "Filter logs by operation type (INSERT, UPDATE, DELETE)",
                            "enum": ["INSERT", "UPDATE", "DELETE"]
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter logs by operation status (SUCCESS, FAILED)",
                            "enum": ["SUCCESS", "FAILED"]
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of logs to return",
                            "default": 100
                        }
                    },
                    "required": [],
                },
            ),
        ]

    async def _handle_list_connections(
        self, check_status: bool = False
    ) -> list[types.TextContent]:
        """处理列出数据库连接工具调用

        Args:
            check_status: 是否检查连接状态

        Returns:
            list[types.TextContent]: 数据库连接列表
        """
        connections = []

        try:
            # 读取配置文件
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)
                if not config or "connections" not in config:
                    return [
                        types.TextContent(
                            type="text",
                            text="No database connections found in configuration.",
                        )
                    ]

                # 获取配置中的所有连接
                for conn_name, conn_config in config["connections"].items():
                    db_type = conn_config.get("type", "unknown")
                    connection_info = []

                    # 添加基本信息
                    connection_info.append(f"Connection: {conn_name}")
                    connection_info.append(f"Type: {db_type}")

                    # 根据数据库类型添加特定信息（排除敏感信息）
                    if db_type == "sqlite":
                        if "path" in conn_config:
                            connection_info.append(f"Path: {conn_config['path']}")
                        elif "database" in conn_config:
                            connection_info.append(
                                f"Database: {conn_config['database']}"
                            )
                    elif db_type in ["mysql", "postgres", "postgresql"]:
                        if "host" in conn_config:
                            connection_info.append(f"Host: {conn_config['host']}")
                        if "port" in conn_config:
                            connection_info.append(f"Port: {conn_config['port']}")
                        if "database" in conn_config:
                            connection_info.append(
                                f"Database: {conn_config['database']}"
                            )
                        if "user" in conn_config:
                            connection_info.append(f"User: {conn_config['user']}")
                        # 不显示密码

                    # 检查连接状态（如果需要）
                    if check_status:
                        try:
                            async with self.get_handler(conn_name) as handler:
                                # 尝试执行一个简单查询来验证连接
                                await handler.test_connection()
                                connection_info.append("Status: Available")
                        except Exception as e:
                            connection_info.append(f"Status: Unavailable ({str(e)})")

                    connections.append("\n".join(connection_info))
        except Exception as e:
            self.send_log(LOG_LEVEL_ERROR, f"Error listing connections: {str(e)}")
            return [
                types.TextContent(
                    type="text", text=f"Error listing connections: {str(e)}"
                )
            ]

        if not connections:
            return [
                types.TextContent(
                    type="text", text="No database connections found in configuration."
                )
            ]

        result = "Available database connections:\n\n" + "\n\n".join(connections)
        return [types.TextContent(type="text", text=result)]

    async def _handle_list_tables(self, connection: str) -> list[types.TextContent]:
        """处理列表表格工具调用

        Args:
            connection: 数据库连接名称

        Returns:
            list[types.TextContent]: 表格列表
        """
        async with self.get_handler(connection) as handler:
            tables = await handler.get_tables()
            if not tables:
                # 空表列表的情况也返回数据库类型
                return [
                    types.TextContent(
                        type="text", text=f"[{handler.db_type}] No tables found"
                    )
                ]

            formatted_tables = "\n".join(
                [
                    f"Table: {table.name}\n"
                    + f"URI: {table.uri}\n"
                    + (
                        f"Description: {table.description}\n"
                        if table.description
                        else ""
                    )
                    + "---"
                    for table in tables
                ]
            )
            # 添加数据库类型前缀
            return [
                types.TextContent(
                    type="text", text=f"[{handler.db_type}]\n{formatted_tables}"
                )
            ]

    async def _handle_run_query(
        self, connection: str, sql: str
    ) -> list[types.TextContent]:
        """处理运行查询工具调用

        Args:
            connection: 数据库连接名称
            sql: SQL查询语句

        Returns:
            list[types.TextContent]: 查询结果

        Raises:
            ConfigurationError: 如果SQL为空或非SELECT语句
        """
        if not sql:
            raise ConfigurationError(EMPTY_QUERY_ERROR)

        # Only allow SELECT statements
        if not sql.lower().startswith("select"):
            raise ConfigurationError(SELECT_ONLY_ERROR)

        async with self.get_handler(connection) as handler:
            result = await handler.execute_query(sql)
            return [types.TextContent(type="text", text=result)]

    async def _handle_table_tools(
        self, name: str, connection: str, table: str
    ) -> list[types.TextContent]:
        """处理表相关工具调用

        Args:
            name: 工具名称
            connection: 数据库连接名称
            table: 表名

        Returns:
            list[types.TextContent]: 工具执行结果

        Raises:
            ConfigurationError: 如果表名为空
        """
        if not table:
            raise ConfigurationError(EMPTY_TABLE_NAME_ERROR)

        async with self.get_handler(connection) as handler:
            result = await handler.execute_tool_query(name, table_name=table)
            return [types.TextContent(type="text", text=result)]

    async def _handle_explain_query(
        self, connection: str, sql: str
    ) -> list[types.TextContent]:
        """处理解释查询工具调用

        Args:
            connection: 数据库连接名称
            sql: SQL查询语句

        Returns:
            list[types.TextContent]: 查询解释

        Raises:
            ConfigurationError: 如果SQL为空
        """
        if not sql:
            raise ConfigurationError(EMPTY_QUERY_ERROR)

        async with self.get_handler(connection) as handler:
            result = await handler.execute_tool_query("dbutils-explain-query", sql=sql)
            return [types.TextContent(type="text", text=result)]

    async def _handle_performance(self, connection: str) -> list[types.TextContent]:
        """处理性能统计工具调用

        Args:
            connection: 数据库连接名称

        Returns:
            list[types.TextContent]: 性能统计
        """
        async with self.get_handler(connection) as handler:
            performance_stats = handler.stats.get_performance_stats()
            return [
                types.TextContent(
                    type="text", text=f"[{handler.db_type}]\n{performance_stats}"
                )
            ]

    async def _handle_analyze_query(
        self, connection: str, sql: str
    ) -> list[types.TextContent]:
        """处理查询分析工具调用

        Args:
            connection: 数据库连接名称
            sql: SQL查询语句

        Returns:
            list[types.TextContent]: 查询分析结果

        Raises:
            ConfigurationError: 如果SQL为空
        """
        if not sql:
            raise ConfigurationError(EMPTY_QUERY_ERROR)

        async with self.get_handler(connection) as handler:
            # First get the execution plan
            explain_result = await handler.explain_query(sql)

            # Then execute the actual query to measure performance
            start_time = datetime.now()
            if sql.lower().startswith("select"):
                try:
                    await handler.execute_query(sql)
                except Exception as e:
                    # If query fails, we still provide the execution plan
                    self.send_log(
                        LOG_LEVEL_ERROR,
                        f"Query execution failed during analysis: {str(e)}",
                    )
            duration = (datetime.now() - start_time).total_seconds()

            # Combine analysis results
            analysis = [
                f"[{handler.db_type}] Query Analysis",
                f"SQL: {sql}",
                "",
                f"Execution Time: {duration * 1000:.2f}ms",
                "",
                "Execution Plan:",
                explain_result,
            ]

            # Add optimization suggestions
            suggestions = self._get_optimization_suggestions(explain_result, duration)
            if suggestions:
                analysis.append("\nOptimization Suggestions:")
                analysis.extend(suggestions)

            return [types.TextContent(type="text", text="\n".join(analysis))]

    async def _handle_execute_write(
        self, connection: str, sql: str, confirmation: str
    ) -> list[types.TextContent]:
        """处理执行写操作工具调用

        Args:
            connection: 数据库连接名称
            sql: SQL写操作语句
            confirmation: 确认字符串

        Returns:
            list[types.TextContent]: 执行结果

        Raises:
            ConfigurationError: 如果SQL为空、确认字符串不正确、连接不可写或没有表级权限
        """
        if not sql:
            raise ConfigurationError(EMPTY_QUERY_ERROR)

        # 验证确认字符串
        if confirmation != "CONFIRM_WRITE":
            raise ConfigurationError(WRITE_CONFIRMATION_REQUIRED_ERROR)

        # 获取SQL类型和表名
        sql_type = self._get_sql_type(sql.strip())
        if sql_type not in ["INSERT", "UPDATE", "DELETE"]:
            raise ConfigurationError(UNSUPPORTED_WRITE_OPERATION_ERROR.format(operation=sql_type))

        table_name = self._extract_table_name(sql)

        # 获取连接配置并验证写权限
        db_config = self._get_config_or_raise(connection)
        await self._check_write_permission(connection, table_name, sql_type)

        # 执行写操作
        async with self.get_handler(connection) as handler:
            self.send_log(
                LOG_LEVEL_NOTICE,
                f"Executing write operation: {sql_type} on table {table_name} in connection {connection}",
            )

            try:
                result = await handler.execute_write_query(sql)
                self.send_log(
                    LOG_LEVEL_INFO,
                    f"Write operation executed successfully: {sql_type} on table {table_name}",
                )
                return [types.TextContent(type="text", text=result)]
            except Exception as e:
                self.send_log(
                    LOG_LEVEL_ERROR,
                    f"Write operation failed: {str(e)}",
                )
                raise

    async def _handle_get_audit_logs(
        self,
        connection: str = None,
        table: str = None,
        operation_type: str = None,
        status: str = None,
        limit: int = 100
    ) -> list[types.TextContent]:
        """处理获取审计日志工具调用

        Args:
            connection: 数据库连接名称（可选）
            table: 表名（可选）
            operation_type: 操作类型（可选，INSERT/UPDATE/DELETE）
            status: 操作状态（可选，SUCCESS/FAILED）
            limit: 返回记录数量限制

        Returns:
            list[types.TextContent]: 审计日志
        """
        # 获取审计日志
        logs = get_logs(
            connection_name=connection,
            table_name=table,
            operation_type=operation_type,
            status=status,
            limit=limit
        )

        # 格式化日志
        formatted_logs = format_logs(logs)

        # 添加过滤条件信息
        filter_info = []
        if connection:
            filter_info.append(f"Connection: {connection}")
        if table:
            filter_info.append(f"Table: {table}")
        if operation_type:
            filter_info.append(f"Operation: {operation_type}")
        if status:
            filter_info.append(f"Status: {status}")

        if filter_info:
            filter_text = "Filters applied: " + ", ".join(filter_info)
            formatted_logs = f"{filter_text}\n\n{formatted_logs}"

        return [types.TextContent(type="text", text=formatted_logs)]

    def _get_optimization_suggestions(
        self, explain_result: str, duration: float
    ) -> list[str]:
        """根据执行计划和耗时获取优化建议

        Args:
            explain_result: 执行计划
            duration: 查询耗时（秒）

        Returns:
            list[str]: 优化建议列表
        """
        suggestions = []
        if "seq scan" in explain_result.lower() and duration > 0.1:
            suggestions.append("- Consider adding an index to avoid sequential scan")
        if "hash join" in explain_result.lower() and duration > 0.5:
            suggestions.append("- Consider optimizing join conditions")
        if duration > 0.5:  # 500ms
            suggestions.append("- Query is slow, consider optimizing or adding caching")
        if "temporary" in explain_result.lower():
            suggestions.append(
                "- Query creates temporary tables, consider restructuring"
            )

        return suggestions

    def _setup_handlers(self):
        """Setup MCP handlers"""

        @self.server.list_resources()
        async def handle_list_resources(
            arguments: dict | None = None,
        ) -> list[types.Resource]:
            if not arguments or "connection" not in arguments:
                # Return empty list when no connection specified
                return []

            connection = arguments["connection"]
            async with self.get_handler(connection) as handler:
                return await handler.get_tables()

        @self.server.read_resource()
        async def handle_read_resource(uri: str, arguments: dict | None = None) -> str:
            if not arguments or "connection" not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)

            parts = uri.split("/")
            if len(parts) < 3:
                raise ConfigurationError(INVALID_URI_FORMAT_ERROR)

            connection = arguments["connection"]
            table_name = parts[-2]  # URI format: xxx/table_name/schema

            async with self.get_handler(connection) as handler:
                return await handler.get_schema(table_name)

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return self._get_available_tools()

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict
        ) -> list[types.TextContent]:
            # Special case for list-connections which doesn't require a connection
            if name == "dbutils-list-connections":
                check_status = arguments.get("check_status", False)
                return await self._handle_list_connections(check_status)

            if "connection" not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)

            connection = arguments["connection"]

            if name == "dbutils-list-tables":
                return await self._handle_list_tables(connection)
            elif name == "dbutils-run-query":
                sql = arguments.get("sql", "").strip()
                return await self._handle_run_query(connection, sql)
            elif name in [
                "dbutils-describe-table",
                "dbutils-get-ddl",
                "dbutils-list-indexes",
                "dbutils-get-stats",
                "dbutils-list-constraints",
            ]:
                table = arguments.get("table", "").strip()
                return await self._handle_table_tools(name, connection, table)
            elif name == "dbutils-explain-query":
                sql = arguments.get("sql", "").strip()
                return await self._handle_explain_query(connection, sql)
            elif name == "dbutils-get-performance":
                return await self._handle_performance(connection)
            elif name == "dbutils-analyze-query":
                sql = arguments.get("sql", "").strip()
                return await self._handle_analyze_query(connection, sql)
            elif name == "dbutils-execute-write":
                sql = arguments.get("sql", "").strip()
                confirmation = arguments.get("confirmation", "").strip()
                return await self._handle_execute_write(connection, sql, confirmation)
            elif name == "dbutils-get-audit-logs":
                table = arguments.get("table", "").strip()
                operation_type = arguments.get("operation_type", "").strip()
                status = arguments.get("status", "").strip()
                limit = arguments.get("limit", 100)
                return await self._handle_get_audit_logs(connection, table, operation_type, status, limit)
            else:
                raise ConfigurationError(f"Unknown tool: {name}")

    async def run(self):
        """Run server"""
        async with mcp.server.stdio.stdio_server() as streams:
            await self.server.run(
                streams[0],
                streams[1],
                self.server.create_initialization_options()
            )
