"""Database server base class"""

class DatabaseError(Exception):
    """Base exception for database errors"""
    pass

class ConfigurationError(DatabaseError):
    """Configuration related errors"""
    pass

class ConnectionError(DatabaseError):
    """Connection related errors"""
    pass

from abc import ABC, abstractmethod
from typing import Any, List, Optional, AsyncContextManager
from contextlib import asynccontextmanager
import json
import yaml
from importlib.metadata import metadata
from mcp.server import Server, NotificationOptions
import mcp.server.stdio
import mcp.types as types
from mcp.shared.session import RequestResponder

from .log import create_logger
from .stats import ResourceStats

# 获取包信息用于日志命名
pkg_meta = metadata("mcp-dbutils")

class DatabaseHandler(ABC):
    """Abstract base class defining common interface for database handlers"""

    def __init__(self, config_path: str, database: str, debug: bool = False):
        """Initialize database handler

        Args:
            config_path: Path to configuration file
            database: Database configuration name
            debug: Enable debug mode
        """
        self.config_path = config_path
        self.database = database
        self.debug = debug
        self.log = create_logger(f"{pkg_meta['Name']}.handler.{database}", debug)
        self.stats = ResourceStats()

    @property
    @abstractmethod
    def db_type(self) -> str:
        """Return database type"""
        pass

    @abstractmethod
    async def get_tables(self) -> list[types.Resource]:
        """Get list of table resources from database"""
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
        """Execute SQL query"""
        try:
            self.stats.record_query()
            result = await self._execute_query(sql)
            self.stats.update_memory_usage(result)
            self.log("info", f"Resource stats: {json.dumps(self.stats.to_dict())}")
            return result
        except Exception as e:
            self.stats.record_error(e.__class__.__name__)
            self.log("error", f"Query error - {str(e)}\nResource stats: {json.dumps(self.stats.to_dict())}")
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
            self.log("info", f"Resource stats: {json.dumps(self.stats.to_dict())}")
            return f"[{self.db_type}]\n{result}"
            
        except Exception as e:
            self.stats.record_error(e.__class__.__name__)
            self.log("error", f"Tool error - {str(e)}\nResource stats: {json.dumps(self.stats.to_dict())}")
            raise

class DatabaseServer:
    """Unified database server class"""

    def __init__(self, config_path: str, debug: bool = False):
        """Initialize database server

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
        self._setup_handlers()
        self._setup_prompts()

    def _setup_prompts(self):
        """Setup prompts handlers"""
        @self.server.list_prompts()
        async def handle_list_prompts() -> list[types.Prompt]:
            """Handle prompts/list request"""
            try:
                self.logger("debug", "Handling list_prompts request")
                return []
            except Exception as e:
                self.logger("error", f"Error in list_prompts: {str(e)}")
                raise

    @asynccontextmanager
    async def get_handler(self, database: str) -> AsyncContextManager[DatabaseHandler]:
        """Get database handler

        Get appropriate database handler based on configuration name

        Args:
            database: Database configuration name

        Returns:
            AsyncContextManager[DatabaseHandler]: Context manager for database handler
        """
        # Read configuration file to determine database type
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
            if not config or 'databases' not in config:
                raise ConfigurationError("Configuration file must contain 'databases' section")
            if database not in config['databases']:
                available_dbs = list(config['databases'].keys())
                raise ConfigurationError(f"Database configuration not found: {database}. Available configurations: {available_dbs}")

            db_config = config['databases'][database]

            handler = None
            try:
                if 'type' not in db_config:
                    raise ConfigurationError("Database configuration must include 'type' field")

                db_type = db_config['type']
                self.logger("debug", f"Creating handler for database type: {db_type}")
                if db_type == 'sqlite':
                    from .sqlite.handler import SqliteHandler
                    handler = SqliteHandler(self.config_path, database, self.debug)
                elif db_type == 'postgres':
                    from .postgres.handler import PostgresHandler
                    handler = PostgresHandler(self.config_path, database, self.debug)
                else:
                    raise ConfigurationError(f"Unsupported database type: {db_type}")

                handler.stats.record_connection_start()
                self.logger("debug", f"Handler created successfully for {database}")
                self.logger("info", f"Resource stats: {json.dumps(handler.stats.to_dict())}")
                yield handler
            except yaml.YAMLError as e:
                raise ConfigurationError(f"Invalid YAML configuration: {str(e)}")
            except ImportError as e:
                raise ConfigurationError(f"Failed to import handler for {db_type}: {str(e)}")
            finally:
                if handler:
                    self.logger("debug", f"Cleaning up handler for {database}")
                    handler.stats.record_connection_end()
                    self.logger("info", f"Final resource stats: {json.dumps(handler.stats.to_dict())}")
                    await handler.cleanup()

    def _setup_handlers(self):
        """Setup MCP handlers"""
        @self.server.list_resources()
        async def handle_list_resources(arguments: dict | None = None) -> list[types.Resource]:
            if not arguments or 'database' not in arguments:
                # Return empty list when no database specified
                return []

            database = arguments['database']
            async with self.get_handler(database) as handler:
                return await handler.get_tables()

        @self.server.read_resource()
        async def handle_read_resource(uri: str, arguments: dict | None = None) -> str:
            if not arguments or 'database' not in arguments:
                raise ConfigurationError("Database configuration name must be specified")

            parts = uri.split('/')
            if len(parts) < 3:
                raise ConfigurationError("Invalid resource URI format")

            database = arguments['database']
            table_name = parts[-2]  # URI format: xxx/table_name/schema

            async with self.get_handler(database) as handler:
                return await handler.get_schema(table_name)

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return [
                types.Tool(
                    name="dbutils-run-query",
                    description="Execute read-only SQL query on database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database": {
                                "type": "string",
                                "description": "Database configuration name"
                            },
                            "sql": {
                                "type": "string",
                                "description": "SQL query (SELECT only)"
                            }
                        },
                        "required": ["database", "sql"]
                    }
                ),
                types.Tool(
                    name="dbutils-list-tables",
                    description="List all available tables in the specified database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database": {
                                "type": "string",
                                "description": "Database configuration name"
                            }
                        },
                        "required": ["database"]
                    }
                ),
                types.Tool(
                    name="dbutils-describe-table",
                    description="Get detailed information about a table's structure",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database": {
                                "type": "string",
                                "description": "Database configuration name"
                            },
                            "table": {
                                "type": "string",
                                "description": "Table name to describe"
                            }
                        },
                        "required": ["database", "table"]
                    }
                ),
                types.Tool(
                    name="dbutils-get-ddl",
                    description="Get DDL statement for creating the table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database": {
                                "type": "string",
                                "description": "Database configuration name"
                            },
                            "table": {
                                "type": "string",
                                "description": "Table name to get DDL for"
                            }
                        },
                        "required": ["database", "table"]
                    }
                ),
                types.Tool(
                    name="dbutils-list-indexes",
                    description="List all indexes on the specified table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database": {
                                "type": "string",
                                "description": "Database configuration name"
                            },
                            "table": {
                                "type": "string",
                                "description": "Table name to list indexes for"
                            }
                        },
                        "required": ["database", "table"]
                    }
                ),
                types.Tool(
                    name="dbutils-get-stats",
                    description="Get table statistics like row count and size",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database": {
                                "type": "string",
                                "description": "Database configuration name"
                            },
                            "table": {
                                "type": "string",
                                "description": "Table name to get statistics for"
                            }
                        },
                        "required": ["database", "table"]
                    }
                ),
                types.Tool(
                    name="dbutils-list-constraints",
                    description="List all constraints (primary key, foreign keys, etc) on the table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database": {
                                "type": "string",
                                "description": "Database configuration name"
                            },
                            "table": {
                                "type": "string",
                                "description": "Table name to list constraints for"
                            }
                        },
                        "required": ["database", "table"]
                    }
                ),
                types.Tool(
                    name="dbutils-explain-query",
                    description="Get execution plan for a SQL query",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "database": {
                                "type": "string",
                                "description": "Database configuration name"
                            },
                            "sql": {
                                "type": "string",
                                "description": "SQL query to explain"
                            }
                        },
                        "required": ["database", "sql"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            if "database" not in arguments:
                raise ConfigurationError("Database configuration name must be specified")

            database = arguments["database"]

            if name == "dbutils-list-tables":
                async with self.get_handler(database) as handler:
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

                async with self.get_handler(database) as handler:
                    result = await handler.execute_query(sql)
                    return [types.TextContent(type="text", text=result)]
            elif name in ["dbutils-describe-table", "dbutils-get-ddl", "dbutils-list-indexes",
                         "dbutils-get-stats", "dbutils-list-constraints"]:
                table = arguments.get("table", "").strip()
                if not table:
                    raise ConfigurationError("Table name cannot be empty")
                
                async with self.get_handler(database) as handler:
                    result = await handler.execute_tool_query(name, table_name=table)
                    return [types.TextContent(type="text", text=result)]
            elif name == "dbutils-explain-query":
                sql = arguments.get("sql", "").strip()
                if not sql:
                    raise ConfigurationError("SQL query cannot be empty")
                
                async with self.get_handler(database) as handler:
                    result = await handler.execute_tool_query(name, sql=sql)
                    return [types.TextContent(type="text", text=result)]
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
