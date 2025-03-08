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
    async def cleanup(self):
        """Cleanup resources"""
        pass

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
                    name="query",
                    description="Execute read-only SQL query",
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
                    name="list_tables",
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
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            if "database" not in arguments:
                raise ConfigurationError("Database configuration name must be specified")

            database = arguments["database"]

            if name == "list_tables":
                async with self.get_handler(database) as handler:
                    tables = await handler.get_tables()
                    formatted_tables = "\n".join([
                        f"Table: {table.name}\n" +
                        f"URI: {table.uri}\n" +
                        (f"Description: {table.description}\n" if table.description else "") +
                        "---"
                        for table in tables
                    ])
                    return [types.TextContent(type="text", text=formatted_tables)]
            elif name == "query":
                sql = arguments.get("sql", "").strip()
                if not sql:
                    raise ConfigurationError("SQL query cannot be empty")

                # Only allow SELECT statements
                if not sql.lower().startswith("select"):
                    raise ConfigurationError("Only SELECT queries are supported for security reasons")

                async with self.get_handler(database) as handler:
                    result = await handler.execute_query(sql)
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
