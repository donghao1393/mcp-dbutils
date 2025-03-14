"""Unit tests for base connection classes"""
import json
import os
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

import mcp.types as types
import pytest
import yaml

from mcp_dbutils.base import (
    ConfigurationError,
    ConnectionError,
    ConnectionHandler,
    ConnectionServer,
    DATABASE_CONNECTION_NAME,
    EMPTY_QUERY_ERROR,
    EMPTY_TABLE_NAME_ERROR,
    CONNECTION_NAME_REQUIRED_ERROR,
    SELECT_ONLY_ERROR,
    INVALID_URI_FORMAT_ERROR
)


class MockConnectionHandler(ConnectionHandler):
    """Mock implementation of ConnectionHandler for testing"""
    
    def __init__(self, config_path, connection, debug=False):
        super().__init__(config_path, connection, debug)
        self.db_type = "mock"
        self.cleanup_called = False
    
    @property
    def db_type(self) -> str:
        return self._db_type
    
    @db_type.setter
    def db_type(self, value):
        self._db_type = value
    
    async def get_tables(self) -> list[types.Resource]:
        return [
            types.Resource(
                uri=f"mock://table1/schema",
                name="table1",
                description="Test table 1",
                mimeType="application/json"
            ),
            types.Resource(
                uri=f"mock://table2/schema",
                name="table2",
                description=None,
                mimeType="application/json"
            )
        ]
    
    async def get_schema(self, table_name: str) -> str:
        return json.dumps({
            "columns": [
                {"name": "id", "type": "INTEGER", "nullable": False},
                {"name": "name", "type": "TEXT", "nullable": True}
            ]
        })
    
    async def _execute_query(self, sql: str) -> str:
        if "error" in sql.lower():
            raise ConnectionError("Test query error")
        return json.dumps({
            "columns": ["id", "name"],
            "rows": [{"id": 1, "name": "Test"}]
        })
    
    async def get_table_description(self, table_name: str) -> str:
        return f"Description for {table_name}"
    
    async def get_table_ddl(self, table_name: str) -> str:
        return f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY, name TEXT)"
    
    async def get_table_indexes(self, table_name: str) -> str:
        return f"Indexes for {table_name}: idx_name"
    
    async def get_table_stats(self, table_name: str) -> str:
        return f"Stats for {table_name}: 100 rows, 10KB"
    
    async def get_table_constraints(self, table_name: str) -> str:
        return f"Constraints for {table_name}: PRIMARY KEY (id)"
    
    async def explain_query(self, sql: str) -> str:
        return f"Explain plan for: {sql}"
    
    async def cleanup(self):
        self.cleanup_called = True


class TestConnectionHandler:
    """Test ConnectionHandler abstract base class"""
    
    @pytest.fixture
    def handler(self):
        """Create a mock connection handler"""
        return MockConnectionHandler("/path/to/config.yaml", "test_connection", debug=True)
    
    def test_init(self, handler):
        """Test initialization"""
        assert handler.config_path == "/path/to/config.yaml"
        assert handler.connection == "test_connection"
        assert handler.debug is True
        assert handler.db_type == "mock"
        assert hasattr(handler, "stats")
        assert hasattr(handler, "log")
    
    @pytest.mark.asyncio
    async def test_execute_query_success(self, handler):
        """Test successful query execution"""
        result = await handler.execute_query("SELECT * FROM test")
        assert "columns" in result
        assert "rows" in result
        assert handler.stats.query_count == 1
        assert len(handler.stats.query_durations) == 1
    
    @pytest.mark.asyncio
    async def test_execute_query_error(self, handler):
        """Test query execution with error"""
        with pytest.raises(ConnectionError, match="Test query error"):
            await handler.execute_query("SELECT * FROM error_table")
        assert handler.stats.query_count == 1
        assert len(handler.stats.error_types) == 1
        assert handler.stats.error_types.get("ConnectionError") == 1
    
    @pytest.mark.asyncio
    async def test_execute_tool_query(self, handler):
        """Test tool query execution"""
        # Test describe table
        result = await handler.execute_tool_query("dbutils-describe-table", table_name="test_table")
        assert "[mock]" in result
        assert "Description for test_table" in result
        
        # Test get DDL
        result = await handler.execute_tool_query("dbutils-get-ddl", table_name="test_table")
        assert "[mock]" in result
        assert "CREATE TABLE test_table" in result
        
        # Test list indexes
        result = await handler.execute_tool_query("dbutils-list-indexes", table_name="test_table")
        assert "[mock]" in result
        assert "Indexes for test_table" in result
        
        # Test get stats
        result = await handler.execute_tool_query("dbutils-get-stats", table_name="test_table")
        assert "[mock]" in result
        assert "Stats for test_table" in result
        
        # Test list constraints
        result = await handler.execute_tool_query("dbutils-list-constraints", table_name="test_table")
        assert "[mock]" in result
        assert "Constraints for test_table" in result
        
        # Test explain query
        result = await handler.execute_tool_query("dbutils-explain-query", sql="SELECT * FROM test")
        assert "[mock]" in result
        assert "Explain plan for" in result
    
    @pytest.mark.asyncio
    async def test_execute_tool_query_error(self, handler):
        """Test tool query execution with errors"""
        # Test unknown tool
        with pytest.raises(ValueError, match="Unknown tool"):
            await handler.execute_tool_query("unknown-tool")
        
        # Test explain query without SQL
        with pytest.raises(ValueError):
            await handler.execute_tool_query("dbutils-explain-query")
    
    @pytest.mark.asyncio
    async def test_send_log(self, handler):
        """Test send_log method"""
        # Without MCP session
        handler.send_log("info", "Test message")
        
        # With MCP session
        mock_session = MagicMock()
        mock_request_context = MagicMock()
        mock_session.request_context = mock_request_context
        handler._session = mock_session
        
        handler.send_log("error", "Test error message")
        mock_request_context.session.send_log_message.assert_called_once()


class TestConnectionServer:
    """Test ConnectionServer class"""
    
    @pytest.fixture
    def mock_config_yaml(self):
        """Mock configuration YAML content"""
        return """
        connections:
          test_sqlite:
            type: sqlite
            path: /path/to/test.db
          test_postgres:
            type: postgres
            host: localhost
            port: 5432
            database: test_db
            user: test_user
            password: test_password
          test_mysql:
            type: mysql
            host: localhost
            port: 3306
            database: test_db
            user: test_user
            password: test_password
          test_invalid:
            type: invalid_type
          test_missing_type:
            host: localhost
        """
    
    @pytest.fixture
    def server(self):
        """Create a connection server"""
        with patch('builtins.open', mock_open()):
            server = ConnectionServer("/path/to/config.yaml", debug=True)
            return server
    
    def test_init(self, server):
        """Test initialization"""
        assert server.config_path == "/path/to/config.yaml"
        assert server.debug is True
        assert hasattr(server, "server")
        assert hasattr(server, "logger")
    
    def test_send_log(self, server):
        """Test send_log method"""
        # Without MCP session
        server.send_log("info", "Test message")
        
        # With MCP session
        mock_session = MagicMock()
        server.server.session = mock_session
        
        server.send_log("error", "Test error message")
        mock_session.send_log_message.assert_called_once()
        
        # Test with exception
        mock_session.send_log_message.side_effect = Exception("Test exception")
        server.send_log("error", "This should not raise")
    
    @pytest.mark.asyncio
    async def test_get_handler_sqlite(self, server, mock_config_yaml):
        """Test get_handler for SQLite"""
        with patch('builtins.open', mock_open(read_data=mock_config_yaml)):
            with patch('mcp_dbutils.sqlite.handler.SQLiteHandler') as mock_handler_class:
                mock_handler = MagicMock()
                mock_handler.stats = MagicMock()
                mock_handler_class.return_value = mock_handler
                
                async with server.get_handler("test_sqlite") as handler:
                    assert handler == mock_handler
                    mock_handler_class.assert_called_once_with("/path/to/config.yaml", "test_sqlite", True)
                
                # Verify cleanup was called
                mock_handler.cleanup.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_get_handler_postgres(self, server, mock_config_yaml):
        """Test get_handler for PostgreSQL"""
        with patch('builtins.open', mock_open(read_data=mock_config_yaml)):
            with patch('mcp_dbutils.postgres.handler.PostgreSQLHandler') as mock_handler_class:
                mock_handler = MagicMock()
                mock_handler.stats = MagicMock()
                mock_handler_class.return_value = mock_handler
                
                async with server.get_handler("test_postgres") as handler:
                    assert handler == mock_handler
                    mock_handler_class.assert_called_once_with("/path/to/config.yaml", "test_postgres", True)
                
                # Verify cleanup was called
                mock_handler.cleanup.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_get_handler_mysql(self, server, mock_config_yaml):
        """Test get_handler for MySQL"""
        with patch('builtins.open', mock_open(read_data=mock_config_yaml)):
            with patch('mcp_dbutils.mysql.handler.MySQLHandler') as mock_handler_class:
                mock_handler = MagicMock()
                mock_handler.stats = MagicMock()
                mock_handler_class.return_value = mock_handler
                
                async with server.get_handler("test_mysql") as handler:
                    assert handler == mock_handler
                    mock_handler_class.assert_called_once_with("/path/to/config.yaml", "test_mysql", True)
                
                # Verify cleanup was called
                mock_handler.cleanup.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_get_handler_errors(self, server, mock_config_yaml):
        """Test get_handler with various error conditions"""
        # Test invalid connection
        with patch('builtins.open', mock_open(read_data=mock_config_yaml)):
            with pytest.raises(ConfigurationError, match="Connection not found"):
                async with server.get_handler("non_existent"):
                    pass
        
        # Test invalid database type
        with patch('builtins.open', mock_open(read_data=mock_config_yaml)):
            with pytest.raises(ConfigurationError, match="Unsupported database type"):
                async with server.get_handler("test_invalid"):
                    pass
        
        # Test missing type
        with patch('builtins.open', mock_open(read_data=mock_config_yaml)):
            with pytest.raises(ConfigurationError, match="must include 'type' field"):
                async with server.get_handler("test_missing_type"):
                    pass
        
        # Test invalid YAML
        with patch('builtins.open', mock_open(read_data="invalid: yaml: content:")):
            with pytest.raises(ConfigurationError, match="Invalid YAML configuration"):
                async with server.get_handler("test_sqlite"):
                    pass
        
        # Test import error
        with patch('builtins.open', mock_open(read_data=mock_config_yaml)):
            with patch('mcp_dbutils.sqlite.handler.SQLiteHandler', side_effect=ImportError("Test import error")):
                with pytest.raises(ConfigurationError, match="Failed to import handler"):
                    async with server.get_handler("test_sqlite"):
                        pass
    
    @pytest.mark.asyncio
    async def test_handle_list_resources(self, server):
        """Test list_resources handler"""
        # Get the handler function
        list_resources_handler = None
        for handler in server.server._handlers:
            if handler.__name__ == "handle_list_resources":
                list_resources_handler = handler
                break
        
        assert list_resources_handler is not None
        
        # Test without connection
        result = await list_resources_handler()
        assert result == []
        
        # Test with connection
        mock_handler = AsyncMock()
        mock_tables = [MagicMock(), MagicMock()]
        mock_handler.get_tables.return_value = mock_tables
        
        with patch.object(server, 'get_handler') as mock_get_handler:
            mock_context_manager = asynccontextmanager(lambda connection: (yield mock_handler))
            mock_get_handler.return_value = mock_context_manager()
            
            result = await list_resources_handler({"connection": "test_connection"})
            assert result == mock_tables
            mock_handler.get_tables.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_handle_read_resource(self, server):
        """Test read_resource handler"""
        # Get the handler function
        read_resource_handler = None
        for handler in server.server._handlers:
            if handler.__name__ == "handle_read_resource":
                read_resource_handler = handler
                break
        
        assert read_resource_handler is not None
        
        # Test without connection
        with pytest.raises(ConfigurationError, match=CONNECTION_NAME_REQUIRED_ERROR):
            await read_resource_handler("mock://table/schema")
        
        # Test invalid URI format
        with pytest.raises(ConfigurationError, match=INVALID_URI_FORMAT_ERROR):
            await read_resource_handler("invalid_uri", {"connection": "test_connection"})
        
        # Test with valid URI
        mock_handler = AsyncMock()
        mock_schema = '{"columns": [{"name": "id", "type": "INTEGER"}]}'
        mock_handler.get_schema.return_value = mock_schema
        
        with patch.object(server, 'get_handler') as mock_get_handler:
            mock_context_manager = asynccontextmanager(lambda connection: (yield mock_handler))
            mock_get_handler.return_value = mock_context_manager()
            
            result = await read_resource_handler("mock://table1/schema", {"connection": "test_connection"})
            assert result == mock_schema
            mock_handler.get_schema.assert_awaited_once_with("table1")
    
    @pytest.mark.asyncio
    async def test_handle_list_tools(self, server):
        """Test list_tools handler"""
        # Get the handler function
        list_tools_handler = None
        for handler in server.server._handlers:
            if handler.__name__ == "handle_list_tools":
                list_tools_handler = handler
                break
        
        assert list_tools_handler is not None
        
        # Test tool list
        tools = await list_tools_handler()
        assert len(tools) > 0
        
        # Verify some specific tools
        tool_names = [tool.name for tool in tools]
        assert "dbutils-run-query" in tool_names
        assert "dbutils-list-tables" in tool_names
        assert "dbutils-describe-table" in tool_names
        assert "dbutils-explain-query" in tool_names
    
    @pytest.mark.asyncio
    async def test_handle_call_tool(self, server):
        """Test call_tool handler"""
        # Get the handler function
        call_tool_handler = None
        for handler in server.server._handlers:
            if handler.__name__ == "handle_call_tool":
                call_tool_handler = handler
                break
        
        assert call_tool_handler is not None
        
        # Test without connection
        with pytest.raises(ConfigurationError, match=CONNECTION_NAME_REQUIRED_ERROR):
            await call_tool_handler("dbutils-run-query", {})
        
        # Setup mock handler
        mock_handler = AsyncMock()
        mock_handler.db_type = "mock"
        mock_handler.get_tables.return_value = [
            types.Resource(uri="mock://table1/schema", name="Table 1", description="Test table")
        ]
        mock_handler.execute_query.return_value = '{"columns": ["id"], "rows": [{"id": 1}]}'
        mock_handler.execute_tool_query.return_value = "[mock]\nTest result"
        mock_handler.explain_query.return_value = "Test explain plan"
        mock_handler.stats = MagicMock()
        mock_handler.stats.get_performance_stats.return_value = "Test performance stats"
        
        with patch.object(server, 'get_handler') as mock_get_handler:
            mock_context_manager = asynccontextmanager(lambda connection: (yield mock_handler))
            mock_get_handler.return_value = mock_context_manager()
            
            # Test dbutils-list-tables
            result = await call_tool_handler("dbutils-list-tables", {"connection": "test_connection"})
            assert len(result) == 1
            assert result[0].type == "text"
            assert "[mock]" in result[0].text
            assert "Table: Table 1" in result[0].text
            mock_handler.get_tables.assert_awaited_once()
            
            # Test dbutils-list-tables with empty result
            mock_handler.get_tables.reset_mock()
            mock_handler.get_tables.return_value = []
            result = await call_tool_handler("dbutils-list-tables", {"connection": "test_connection"})
            assert len(result) == 1
            assert "No tables found" in result[0].text
            
            # Test dbutils-run-query
            result = await call_tool_handler("dbutils-run-query", {
                "connection": "test_connection",
                "sql": "SELECT * FROM test"
            })
            assert len(result) == 1
            assert result[0].text == '{"columns": ["id"], "rows": [{"id": 1}]}'
            mock_handler.execute_query.assert_awaited_once_with("SELECT * FROM test")
            
            # Test dbutils-run-query with empty SQL
            with pytest.raises(ConfigurationError, match=EMPTY_QUERY_ERROR):
                await call_tool_handler("dbutils-run-query", {
                    "connection": "test_connection",
                    "sql": ""
                })
            
            # Test dbutils-run-query with non-SELECT SQL
            with pytest.raises(ConfigurationError, match=SELECT_ONLY_ERROR):
                await call_tool_handler("dbutils-run-query", {
                    "connection": "test_connection",
                    "sql": "DELETE FROM test"
                })
            
            # Test dbutils-describe-table
            result = await call_tool_handler("dbutils-describe-table", {
                "connection": "test_connection",
                "table": "test_table"
            })
            assert len(result) == 1
            assert result[0].text == "[mock]\nTest result"
            mock_handler.execute_tool_query.assert_awaited_once_with("dbutils-describe-table", table_name="test_table")
            
            # Test dbutils-describe-table with empty table
            mock_handler.execute_tool_query.reset_mock()
            with pytest.raises(ConfigurationError, match=EMPTY_TABLE_NAME_ERROR):
                await call_tool_handler("dbutils-describe-table", {
                    "connection": "test_connection",
                    "table": ""
                })
            
            # Test dbutils-explain-query
            mock_handler.execute_tool_query.reset_mock()
            result = await call_tool_handler("dbutils-explain-query", {
                "connection": "test_connection",
                "sql": "SELECT * FROM test"
            })
            assert len(result) == 1
            assert result[0].text == "[mock]\nTest result"
            mock_handler.execute_tool_query.assert_awaited_once_with("dbutils-explain-query", sql="SELECT * FROM test")
            
            # Test dbutils-get-performance
            result = await call_tool_handler("dbutils-get-performance", {
                "connection": "test_connection"
            })
            assert len(result) == 1
            assert "[mock]" in result[0].text
            assert "Test performance stats" in result[0].text
            
            # Test dbutils-analyze-query
            result = await call_tool_handler("dbutils-analyze-query", {
                "connection": "test_connection",
                "sql": "SELECT * FROM test"
            })
            assert len(result) == 1
            assert "[mock] Query Analysis" in result[0].text
            assert "SQL: SELECT * FROM test" in result[0].text
            assert "Execution Plan:" in result[0].text
            mock_handler.explain_query.assert_awaited_once_with("SELECT * FROM test")
            mock_handler.execute_query.assert_awaited()
            
            # Test unknown tool
            with pytest.raises(ConfigurationError, match="Unknown tool"):
                await call_tool_handler("unknown-tool", {"connection": "test_connection"})
    
    @pytest.mark.asyncio
    async def test_handle_list_prompts(self, server):
        """Test list_prompts handler"""
        # Get the handler function
        list_prompts_handler = None
        for handler in server.server._handlers:
            if handler.__name__ == "handle_list_prompts":
                list_prompts_handler = handler
                break
        
        assert list_prompts_handler is not None
        
        # Test normal operation
        result = await list_prompts_handler()
        assert result == []
        
        # Test with exception
        with patch.object(server, 'send_log') as mock_send_log:
            with patch.object(list_prompts_handler, '__wrapped__', side_effect=Exception("Test exception")):
                with pytest.raises(Exception, match="Test exception"):
                    await list_prompts_handler()
                mock_send_log.assert_called_with("error", "Error in list_prompts: Test exception")
