"""Connection server base class"""

class ConnectionHandlerError(Exception):
    """Base exception for connection errors"""
    pass

class ConfigurationError(ConnectionHandlerError):
    """Configuration related errors"""
    pass

class ConnectionError(ConnectionHandlerError):
    """Connection related errors"""
    pass

from abc import ABC, abstractmethod
from typing import Any, List, Optional, AsyncContextManager
from contextlib import asynccontextmanager
import json
import yaml
import time
from datetime import datetime
from importlib.metadata import metadata
from mcp.server import Server, NotificationOptions
import mcp.server.stdio
import mcp.types as types
from mcp.shared.session import RequestResponder

from .log import create_logger
from .stats import ResourceStats

# 获取包信息用于日志命名
pkg_meta = metadata("mcp-dbutils")

# MCP日志级别常量
LOG_LEVEL_DEBUG = "debug"       # 0
LOG_LEVEL_INFO = "info"        # 1
LOG_LEVEL_NOTICE = "notice"    # 2
LOG_LEVEL_WARNING = "warning"  # 3
LOG_LEVEL_ERROR = "error"      # 4
LOG_LEVEL_CRITICAL = "critical" # 5
LOG_LEVEL_ALERT = "alert"      # 6
LOG_LEVEL_EMERGENCY = "emergency" # 7

class ConnectionHandler(ABC):
    """Abstract base class defining common interface for connection handlers"""

    def __init__(self, config_path: str, connection: str, debug: bool = False):
        """Initialize connection handler

        Args:
            config_path: Path to configuration file
            connection: Database connection name
            debug: Enable debug mode
        """
        self.config_path = config_path
        self.connection = connection
        self.debug = debug
        # 创建stderr日志记录器用于本地调试
        self.log = create_logger(f"{pkg_meta['Name']}.handler.{connection}", debug)
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
        if self._session and hasattr(self._session, 'request_context'):
            self._session.request_context.session.send_log_message(
                level=level,
                data=message
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

    async def execute_query(self, sql: str) -> str:
        """Execute SQL query with performance tracking"""
        start_time = datetime.now()
        try:
            self.stats.record_query()
            result = await self._execute_query(sql)
            duration = (datetime.now() - start_time).total_seconds()
            self.stats.record_query_duration(sql, duration)
            self.stats.update_memory_usage(result)
            self.send_log(LOG_LEVEL_INFO, f"Query executed in {duration*1000:.2f}ms. Resource stats: {json.dumps(self.stats.to_dict())}")
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.stats.record_error(e.__class__.__name__)
            self.send_log(LOG_LEVEL_ERROR, f"Query error after {duration*1000:.2f}ms - {str(e)}\nResource stats: {json.dumps(self.stats.to_dict())}")
            raise

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
    async def cleanup(self):
        """Cleanup resources"""
        pass

    async def execute_tool_query(self, tool_name: str, table_name: str = "", sql: str = "") -> str:
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
                    raise ValueError("SQL query required for explain-query tool")
                result = await self.explain_query(sql)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
                
            self.stats.update_memory_usage(result)
            self.send_log(LOG_LEVEL_INFO, f"Resource stats: {json.dumps(self.stats.to_dict())}")
            return f"[{self.db_type}]\n{result}"
            
        except Exception as e:
            self.stats.record_error(e.__class__.__name__)
            self.send_log(LOG_LEVEL_ERROR, f"Tool error - {str(e)}\nResource stats: {json.dumps(self.stats.to_dict())}")
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
        self.logger = create_logger(f"{pkg_meta['Name']}.server", debug)
        self.server = Server(
            name=pkg_meta["Name"],
            version=pkg_meta["Version"]
        )
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
        if hasattr(self.server, 'session') and self.server.session:
            try:
                self.server.session.send_log_message(
                    level=level,
                    data=message
                )
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

    @asynccontextmanager
    async def get_handler(self, connection: str) -> AsyncContextManager[ConnectionHandler]:
        """Get connection handler

        Get appropriate connection handler based on connection name

        Args:
            connection: Database connection name

        Returns:
            AsyncContextManager[ConnectionHandler]: Context manager for connection handler
        """
        # Read configuration file to determine database type
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
            if not config or 'connections' not in config:
                raise ConfigurationError("Configuration file must contain 'connections' section")
            if connection not in config['connections']:
                available_connections = list(config['connections'].keys())
                raise ConfigurationError(f"Connection not found: {connection}. Available connections: {available_connections}")

            db_config = config['connections'][connection]

            handler = None
            try:
                if 'type' not in db_config:
                    raise ConfigurationError("Database configuration must include 'type' field")

                db_type = db_config['type']
                self.send_log(LOG_LEVEL_DEBUG, f"Creating handler for database type: {db_type}")
                if db_type == 'sqlite':
                    from .sqlite.handler import SQLiteHandler
                    handler = SQLiteHandler(self.config_path, connection, self.debug)
                elif db_type == 'postgres':
                    from .postgres.handler import PostgreSQLHandler
                    handler = PostgreSQLHandler(self.config_path, connection, self.debug)
                elif db_type == 'mysql':
                    from .mysql.handler import MySQLHandler
                    handler = MySQLHandler(self.config_path, connection, self.debug)
                else:
                    raise ConfigurationError(f"Unsupported database type: {db_type}")

                # Set session for MCP logging
                if hasattr(self.server, 'session'):
                    handler._session = self.server.session

                handler.stats.record_connection_start()
                self.send_log(LOG_LEVEL_DEBUG, f"Handler created successfully for {connection}")
                self.send_log(LOG_LEVEL_INFO, f"Resource stats: {json.dumps(handler.stats.to_dict())}")
                yield handler
            except yaml.YAMLError as e:
                raise ConfigurationError(f"Invalid YAML configuration: {str(e)}")
            except ImportError as e:
                raise ConfigurationError(f"Failed to import handler for {db_type}: {str(e)}")
            finally:
                if handler:
                    self.send_log(LOG_LEVEL_DEBUG, f"Cleaning up handler for {connection}")
                    handler.stats.record_connection_end()
                    self.send_log(LOG_LEVEL_INFO, f"Final resource stats: {json.dumps(handler.stats.to_dict())}")
                    await handler.cleanup()

    def _setup_handlers(self):
        """Setup MCP handlers"""
        @self.server.list_resources()
        async def handle_list_resources(arguments: dict | None = None) -> list[types.Resource]:
            if not arguments or 'connection' not in arguments:
                # Return empty list when no connection specified
                return []

            connection = arguments['connection']
            async with self.get_handler(connection) as handler:
                return await handler.get_tables()

        @self.server.read_resource()
        async def handle_read_resource(uri: str, arguments: dict | None = None) -> str:
            if not arguments or 'connection' not in arguments:
                raise ConfigurationError("Connection name must be specified")

            parts = uri.split('/')
            if len(parts) < 3:
                raise ConfigurationError("Invalid resource URI format")

            connection = arguments['connection']
            table_name = parts[-2]  # URI format: xxx/table_name/schema

            async with self.get_handler(connection) as handler:
                return await handler.get_schema(table_name)

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return [
                types.Tool(
                    name="dbutils-run-query",
                    description="Execute read-only SQL query on database connection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection": {
                                "type": "string",
                                "description": "Database connection name"
                            },
                            "sql": {
                                "type": "string",
                                "description": "SQL query (SELECT only)"
                            }
                        },
                        "required": ["connection", "sql"]
                    }
                ),
                types.Tool(
                    name="dbutils-list-tables",
                    description="List all available tables in the specified database connection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection": {
                                "type": "string",
                                "description": "Database connection name"
                            }
                        },
                        "required": ["connection"]
                    }
                ),
                types.Tool(
                    name="dbutils-describe-table",
                    description="Get detailed information about a table's structure",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection": {
                                "type": "string",
                                "description": "Database connection name"
                            },
                            "table": {
                                "type": "string",
                                "description": "Table name to describe"
                            }
                        },
                        "required": ["connection", "table"]
                    }
                ),
                types.Tool(
                    name="dbutils-get-ddl",
                    description="Get DDL statement for creating the table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection": {
                                "type": "string",
                                "description": "Database connection name"
                            },
                            "table": {
                                "type": "string",
                                "description": "Table name to get DDL for"
                            }
                        },
                        "required": ["connection", "table"]
                    }
                ),
                types.Tool(
                    name="dbutils-list-indexes",
                    description="List all indexes on the specified table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection": {
                                "type": "string",
                                "description": "Database connection name"
                            },
                            "table": {
                                "type": "string",
                                "description": "Table name to list indexes for"
                            }
                        },
                        "required": ["connection", "table"]
                    }
                ),
                types.Tool(
                    name="dbutils-get-stats",
                    description="Get table statistics like row count and size",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection": {
                                "type": "string",
                                "description": "Database connection name"
                            },
                            "table": {
                                "type": "string",
                                "description": "Table name to get statistics for"
                            }
                        },
                        "required": ["connection", "table"]
                    }
                ),
                types.Tool(
                    name="dbutils-list-constraints",
                    description="List all constraints (primary key, foreign keys, etc) on the table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection": {
                                "type": "string",
                                "description": "Database connection name"
                            },
                            "table": {
                                "type": "string",
                                "description": "Table name to list constraints for"
                            }
                        },
                        "required": ["connection", "table"]
                    }
                ),
                types.Tool(
                    name="dbutils-explain-query",
                    description="Get execution plan for a SQL query",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection": {
                                "type": "string",
                                "description": "Database connection name"
                            },
                            "sql": {
                                "type": "string",
                                "description": "SQL query to explain"
                            }
                        },
                        "required": ["connection", "sql"]
                    }
                ),
                types.Tool(
                    name="dbutils-get-performance",
                    description="Get database performance statistics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection": {
                                "type": "string",
                                "description": "Database connection name"
                            }
                        },
                        "required": ["connection"]
                    }
                ),
                types.Tool(
                    name="dbutils-analyze-query",
                    description="Analyze a SQL query for performance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection": {
                                "type": "string",
                                "description": "Database connection name"
                            },
                            "sql": {
                                "type": "string",
                                "description": "SQL query to analyze"
                            }
                        },
                        "required": ["connection", "sql"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            if "connection" not in arguments:
                raise ConfigurationError("Connection name must be specified")
            
            connection = arguments["connection"]

            if name == "dbutils-list-tables":
                async with self.get_handler(connection) as handler:
                    tables = await handler.get_tables()
                    if not tables:
                        # 空表列表的情况也返回数据库类型
                        return [types.TextContent(type="text", text=f"[{handler.db_type}] No tables found")]
                    
                    formatted_tables = "\n".join([
                        f"Table: {table.name}\n" +
                        f"URI: {table.uri}\n" +
                        (f"Description: {table.description}\n" if table.description else "") +
                        "---"
                        for table in tables
                    ])
                    # 添加数据库类型前缀
                    return [types.TextContent(type="text", text=f"[{handler.db_type}]\n{formatted_tables}")]
            elif name == "dbutils-run-query":
                sql = arguments.get("sql", "").strip()
                if not sql:
                    raise ConfigurationError("SQL query cannot be empty")

                # Only allow SELECT statements
                if not sql.lower().startswith("select"):
                    raise ConfigurationError("Only SELECT queries are supported for security reasons")

                async with self.get_handler(connection) as handler:
                    result = await handler.execute_query(sql)
                    return [types.TextContent(type="text", text=result)]
            elif name in ["dbutils-describe-table", "dbutils-get-ddl", "dbutils-list-indexes",
                         "dbutils-get-stats", "dbutils-list-constraints"]:
                table = arguments.get("table", "").strip()
                if not table:
                    raise ConfigurationError("Table name cannot be empty")
                
                async with self.get_handler(connection) as handler:
                    result = await handler.execute_tool_query(name, table_name=table)
                    return [types.TextContent(type="text", text=result)]
            elif name == "dbutils-explain-query":
                sql = arguments.get("sql", "").strip()
                if not sql:
                    raise ConfigurationError("SQL query cannot be empty")
                
                async with self.get_handler(connection) as handler:
                    result = await handler.execute_tool_query(name, sql=sql)
                    return [types.TextContent(type="text", text=result)]
            elif name == "dbutils-get-performance":
                async with self.get_handler(connection) as handler:
                    performance_stats = handler.stats.get_performance_stats()
                    return [types.TextContent(type="text", text=f"[{handler.db_type}]\n{performance_stats}")]
            elif name == "dbutils-analyze-query":
                sql = arguments.get("sql", "").strip()
                if not sql:
                    raise ConfigurationError("SQL query cannot be empty")
                
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
                            self.send_log(LOG_LEVEL_ERROR, f"Query execution failed during analysis: {str(e)}")
                    duration = (datetime.now() - start_time).total_seconds()
                    
                    # Combine analysis results
                    analysis = [
                        f"[{handler.db_type}] Query Analysis",
                        f"SQL: {sql}",
                        f"",
                        f"Execution Time: {duration*1000:.2f}ms",
                        f"",
                        f"Execution Plan:",
                        explain_result
                    ]
                    
                    # Add optimization suggestions based on execution plan and timing
                    suggestions = []
                    if "seq scan" in explain_result.lower() and duration > 0.1:
                        suggestions.append("- Consider adding an index to avoid sequential scan")
                    if "hash join" in explain_result.lower() and duration > 0.5:
                        suggestions.append("- Consider optimizing join conditions")
                    if duration > 0.5:  # 500ms
                        suggestions.append("- Query is slow, consider optimizing or adding caching")
                    if "temporary" in explain_result.lower():
                        suggestions.append("- Query creates temporary tables, consider restructuring")
                    
                    if suggestions:
                        analysis.append("\nOptimization Suggestions:")
                        analysis.extend(suggestions)
                        
                    return [types.TextContent(type="text", text="\n".join(analysis))]
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
