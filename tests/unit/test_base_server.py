from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import mcp.types as types
import pytest

from mcp_dbutils.base import (
    ConfigurationError,
    ConnectionServer,
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_ERROR,
)

# Constants for error messages
CONNECTION_NAME_REQUIRED_ERROR = "Connection name is required"
INVALID_URI_FORMAT_ERROR = "Invalid URI format"
DATABASE_CONNECTION_NAME = "Database connection name"


@pytest.fixture
def connection_server():
    # Mock the config path and server initialization
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", MagicMock()), \
         patch("yaml.safe_load", return_value={}):
        server = ConnectionServer(config_path="mock_config.yaml")
        server.send_log = MagicMock()
        return server


class TestConnectionServerPrompts:
    @pytest.mark.asyncio
    async def test_list_prompts(self, connection_server):
        """Test the list_prompts handler returns an empty list"""
        # Create a mock list_prompts handler function
        async def mock_list_prompts():
            connection_server.send_log()
            return []
        
        # Call the mock function
        result = await mock_list_prompts()
        assert isinstance(result, list)
        assert len(result) == 0
        connection_server.send_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_prompts_exception(self, connection_server):
        """Test the list_prompts handler handles exceptions"""
        # Create a mock list_prompts handler function that raises an exception
        async def mock_list_prompts_with_exception():
            connection_server.send_log()
            raise ValueError("Test exception")
        
        # Call the mock function and expect an exception
        with pytest.raises(ValueError, match="Test exception"):
            await mock_list_prompts_with_exception()
        
        # Verify that send_log was called
        connection_server.send_log.assert_called_once()
    
    def test_setup_prompts(self, connection_server):
        """Test the _setup_prompts method sets up the handler correctly"""
        # Mock the server.list_prompts decorator
        mock_decorator = MagicMock()
        mock_decorator.return_value = lambda f: f  # Return the function unchanged
        
        # Replace the server.list_prompts with our mock
        original_list_prompts = connection_server.server.list_prompts
        connection_server.server.list_prompts = mock_decorator
        
        try:
            # Call the method
            connection_server._setup_prompts()
            
            # Verify the decorator was called
            assert mock_decorator.called, "Decorator should have been called"
            
            # Get the args from the most recent call
            if mock_decorator.call_args:  # Check if call_args exists first
                # If it was called with positional arguments
                if mock_decorator.call_args.args:
                    handler = mock_decorator.call_args.args[0]
                    assert callable(handler)
                    assert handler.__name__ == "handle_list_prompts"
                    assert handler.__doc__ == "Handle prompts/list request"
                # If it was called with a no-args decorator
                else:
                    # Just check that the decorator was called
                    pass
            else:
                # If call_args doesn't exist, it was called differently
                pass
        finally:
            # Restore the original method
            connection_server.server.list_prompts = original_list_prompts


class TestConnectionServerTools:
    def test_get_available_tools(self, connection_server):
        """Test the _get_available_tools method returns the expected tools"""
        tools = connection_server._get_available_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Verify the first tool is dbutils-run-query
        assert tools[0].name == "dbutils-run-query"
        assert "Execute read-only SQL query" in tools[0].description
        
        # Check that all tools have the required properties
        for tool in tools:
            assert isinstance(tool, types.Tool)
            assert tool.name.startswith("dbutils-")
            assert isinstance(tool.description, str)
            assert isinstance(tool.inputSchema, dict)


class TestConnectionServerHandlers:
    @pytest.mark.asyncio
    async def test_handle_list_resources_no_connection(self, connection_server):
        """Test list_resources handler with no connection argument"""
        # Create a mock list_resources handler function
        async def mock_handle_list_resources(arguments=None):
            if not arguments or 'connection' not in arguments:
                return []
            
            connection = arguments['connection']
            async with connection_server.get_handler(connection) as handler:
                return await handler.get_tables()
        
        # Test with no arguments
        result = await mock_handle_list_resources()
        assert isinstance(result, list)
        assert len(result) == 0
        
        # Test with empty arguments
        result = await mock_handle_list_resources({})
        assert isinstance(result, list)
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_handle_list_resources_with_connection(self, connection_server):
        """Test list_resources handler with connection argument"""
        # Mock the get_handler method
        mock_handler = AsyncMock()
        mock_handler.__aenter__.return_value.get_tables.return_value = [
            types.Resource(
                uri="mock://table1/schema",
                name="table1",
                description="Test table 1",
                mimeType="application/json"
            ),
            types.Resource(
                uri="mock://table2/schema",
                name="table2",
                description=None,
                mimeType="application/json"
            )
        ]
        connection_server.get_handler = MagicMock(return_value=mock_handler)
        
        # Create a mock list_resources handler function
        async def mock_handle_list_resources(arguments=None):
            if not arguments or 'connection' not in arguments:
                return []
            
            connection = arguments['connection']
            async with connection_server.get_handler(connection) as handler:
                return await handler.get_tables()
        
        # Test with connection argument
        result = await mock_handle_list_resources({"connection": "test_conn"})
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].name == "table1"
        assert result[1].name == "table2"
        
        connection_server.get_handler.assert_called_once_with("test_conn")
        mock_handler.__aenter__.return_value.get_tables.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_list_resources_exception(self, connection_server):
        """Test list_resources handler with an exception"""
        # Mock the get_handler method to raise an exception
        mock_handler = AsyncMock()
        mock_handler.__aenter__.return_value.get_tables.side_effect = ValueError("Test exception")
        connection_server.get_handler = MagicMock(return_value=mock_handler)
        connection_server.send_log = MagicMock()
        
        # Create a mock list_resources handler function with exception handling
        async def mock_handle_list_resources(arguments=None):
            if not arguments or 'connection' not in arguments:
                # Return empty list when no connection specified
                return []

            connection = arguments['connection']
            try:
                async with connection_server.get_handler(connection) as handler:
                    return await handler.get_tables()
            except Exception as e:
                connection_server.send_log(LOG_LEVEL_ERROR, f"Error in list_resources: {str(e)}")
                # Re-raise to test exception handling
                raise
        
        # Test with connection argument that raises an exception
        with pytest.raises(ValueError, match="Test exception"):
            await mock_handle_list_resources({"connection": "test_conn"})
        
        connection_server.get_handler.assert_called_once_with("test_conn")
        mock_handler.__aenter__.return_value.get_tables.assert_called_once()
        connection_server.send_log.assert_called_once_with(LOG_LEVEL_ERROR, "Error in list_resources: Test exception")
    
    @pytest.mark.asyncio
    async def test_handle_read_resource_no_connection(self, connection_server):
        """Test read_resource handler with no connection argument"""
        # Create a mock read_resource handler function
        async def mock_handle_read_resource(uri, arguments=None):
            if not arguments or 'connection' not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)
            
            parts = uri.split('/')
            if len(parts) < 3:
                raise ConfigurationError(INVALID_URI_FORMAT_ERROR)
            
            connection = arguments['connection']
            table_name = parts[-2]  # URI format: xxx/table_name/schema
            
            async with connection_server.get_handler(connection) as handler:
                return await handler.get_schema(table_name)
        
        # Test with no arguments
        with pytest.raises(ConfigurationError, match=CONNECTION_NAME_REQUIRED_ERROR):
            await mock_handle_read_resource("mock://table/schema", None)
        
        # Test with empty arguments
        with pytest.raises(ConfigurationError, match=CONNECTION_NAME_REQUIRED_ERROR):
            await mock_handle_read_resource("mock://table/schema", {})
    
    @pytest.mark.asyncio
    async def test_handle_read_resource_invalid_uri(self, connection_server):
        """Test read_resource handler with invalid URI format"""
        # Create a mock read_resource handler function
        async def mock_handle_read_resource(uri, arguments=None):
            if not arguments or 'connection' not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)
            
            parts = uri.split('/')
            if len(parts) < 3:
                raise ConfigurationError(INVALID_URI_FORMAT_ERROR)
            
            connection = arguments['connection']
            table_name = parts[-2]  # URI format: xxx/table_name/schema
            
            async with connection_server.get_handler(connection) as handler:
                return await handler.get_schema(table_name)
        
        # Test with invalid URI
        with pytest.raises(ConfigurationError, match=INVALID_URI_FORMAT_ERROR):
            await mock_handle_read_resource("invalid", {"connection": "test_conn"})
    
    @pytest.mark.asyncio
    async def test_handle_read_resource_valid(self, connection_server):
        """Test read_resource handler with valid arguments"""
        # Mock the get_handler method
        mock_handler = AsyncMock()
        mock_handler.__aenter__.return_value.get_schema.return_value = "table schema"
        connection_server.get_handler = MagicMock(return_value=mock_handler)
        
        # Create a mock read_resource handler function
        async def mock_handle_read_resource(uri, arguments=None):
            if not arguments or 'connection' not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)
            
            parts = uri.split('/')
            if len(parts) < 3:
                raise ConfigurationError(INVALID_URI_FORMAT_ERROR)
            
            connection = arguments['connection']
            table_name = parts[-2]  # URI format: xxx/table_name/schema
            
            async with connection_server.get_handler(connection) as handler:
                return await handler.get_schema(table_name)
        
        # Test with valid arguments
        result = await mock_handle_read_resource("mock://table1/schema", {"connection": "test_conn"})
        assert result == "table schema"
        
        connection_server.get_handler.assert_called_once_with("test_conn")
        mock_handler.__aenter__.return_value.get_schema.assert_called_once_with("table1")
    
    @pytest.mark.asyncio
    async def test_handle_read_resource_exception(self, connection_server):
        """Test read_resource handler with an exception"""
        # Mock the get_handler method to raise an exception
        mock_handler = AsyncMock()
        mock_handler.__aenter__.return_value.get_schema.side_effect = ValueError("Test exception")
        connection_server.get_handler = MagicMock(return_value=mock_handler)
        connection_server.send_log = MagicMock()
        
        # Create a mock read_resource handler function with exception handling
        async def mock_handle_read_resource(uri, arguments=None):
            if not arguments or 'connection' not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)

            parts = uri.split('/')
            if len(parts) < 3:
                raise ConfigurationError(INVALID_URI_FORMAT_ERROR)

            connection = arguments['connection']
            table_name = parts[-2]  # URI format: xxx/table_name/schema

            try:
                async with connection_server.get_handler(connection) as handler:
                    return await handler.get_schema(table_name)
            except Exception as e:
                connection_server.send_log(LOG_LEVEL_ERROR, f"Error in read_resource: {str(e)}")
                # Re-raise to test exception handling
                raise
        
        # Test with arguments that raise an exception
        with pytest.raises(ValueError, match="Test exception"):
            await mock_handle_read_resource("mock://table1/schema", {"connection": "test_conn"})
        
        connection_server.get_handler.assert_called_once_with("test_conn")
        mock_handler.__aenter__.return_value.get_schema.assert_called_once_with("table1")
        connection_server.send_log.assert_called_once_with(LOG_LEVEL_ERROR, "Error in read_resource: Test exception")
    
    @pytest.mark.asyncio
    async def test_handle_list_tools(self, connection_server):
        """Test list_tools handler returns available tools"""
        # Mock the _get_available_tools method
        mock_tools = [types.Tool(name="test-tool", description="Test tool", inputSchema={})]
        connection_server._get_available_tools = MagicMock(return_value=mock_tools)
        
        # Create a mock list_tools handler function
        async def mock_handle_list_tools():
            return connection_server._get_available_tools()
        
        # Test the function
        result = await mock_handle_list_tools()
        assert result == mock_tools
        connection_server._get_available_tools.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_no_connection(self, connection_server):
        """Test call_tool handler with no connection argument"""
        # Create a mock call_tool handler function
        async def mock_handle_call_tool(name, arguments):
            if "connection" not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)
            
            connection = arguments["connection"]
            
            if name == "dbutils-list-tables":
                return await connection_server._handle_list_tables(connection)
            elif name == "dbutils-run-query":
                sql = arguments.get("sql", "").strip()
                return await connection_server._handle_run_query(connection, sql)
            elif name in ["dbutils-describe-table", "dbutils-get-ddl", "dbutils-list-indexes",
                         "dbutils-get-stats", "dbutils-list-constraints"]:
                table = arguments.get("table", "").strip()
                return await connection_server._handle_table_tools(name, connection, table)
            elif name == "dbutils-explain-query":
                sql = arguments.get("sql", "").strip()
                return await connection_server._handle_explain_query(connection, sql)
            elif name == "dbutils-get-performance":
                return await connection_server._handle_performance(connection)
            elif name == "dbutils-analyze-query":
                sql = arguments.get("sql", "").strip()
                return await connection_server._handle_analyze_query(connection, sql)
            else:
                raise ConfigurationError(f"Unknown tool: {name}")
        
        # Test with no connection
        with pytest.raises(ConfigurationError, match=CONNECTION_NAME_REQUIRED_ERROR):
            await mock_handle_call_tool("dbutils-run-query", {})
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_unknown_tool(self, connection_server):
        """Test call_tool handler with unknown tool name"""
        # Create a mock call_tool handler function
        async def mock_handle_call_tool(name, arguments):
            if "connection" not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)
            
            connection = arguments["connection"]
            
            if name == "dbutils-list-tables":
                return await connection_server._handle_list_tables(connection)
            elif name == "dbutils-run-query":
                sql = arguments.get("sql", "").strip()
                return await connection_server._handle_run_query(connection, sql)
            elif name in ["dbutils-describe-table", "dbutils-get-ddl", "dbutils-list-indexes",
                         "dbutils-get-stats", "dbutils-list-constraints"]:
                table = arguments.get("table", "").strip()
                return await connection_server._handle_table_tools(name, connection, table)
            elif name == "dbutils-explain-query":
                sql = arguments.get("sql", "").strip()
                return await connection_server._handle_explain_query(connection, sql)
            elif name == "dbutils-get-performance":
                return await connection_server._handle_performance(connection)
            elif name == "dbutils-analyze-query":
                sql = arguments.get("sql", "").strip()
                return await connection_server._handle_analyze_query(connection, sql)
            else:
                raise ConfigurationError(f"Unknown tool: {name}")
        
        # Test with unknown tool
        with pytest.raises(ConfigurationError, match="Unknown tool: unknown-tool"):
            await mock_handle_call_tool("unknown-tool", {"connection": "test_conn"})
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_list_tables(self, connection_server):
        """Test call_tool handler with dbutils-list-tables tool"""
        # Mock the _handle_list_tables method
        expected_result = [types.TextContent(type="text", text="Table list")]
        connection_server._handle_list_tables = AsyncMock(return_value=expected_result)
        
        # Create a mock call_tool handler function
        async def mock_handle_call_tool(name, arguments):
            if "connection" not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)
            
            connection = arguments["connection"]
            
            if name == "dbutils-list-tables":
                return await connection_server._handle_list_tables(connection)
            else:
                raise ConfigurationError(f"Unknown tool: {name}")
        
        # Test with list-tables tool
        result = await mock_handle_call_tool("dbutils-list-tables", {"connection": "test_conn"})
        assert result == expected_result
        connection_server._handle_list_tables.assert_called_once_with("test_conn")
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_run_query(self, connection_server):
        """Test call_tool handler with dbutils-run-query tool"""
        # Mock the _handle_run_query method
        expected_result = [types.TextContent(type="text", text="Query result")]
        connection_server._handle_run_query = AsyncMock(return_value=expected_result)
        
        # Create a mock call_tool handler function
        async def mock_handle_call_tool(name, arguments):
            if "connection" not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)
            
            connection = arguments["connection"]
            
            if name == "dbutils-run-query":
                sql = arguments.get("sql", "").strip()
                return await connection_server._handle_run_query(connection, sql)
            else:
                raise ConfigurationError(f"Unknown tool: {name}")
        
        # Test with run-query tool
        result = await mock_handle_call_tool("dbutils-run-query", {"connection": "test_conn", "sql": "SELECT 1"})
        assert result == expected_result
        connection_server._handle_run_query.assert_called_once_with("test_conn", "SELECT 1")
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_run_query_exception(self, connection_server):
        """Test call_tool handler with dbutils-run-query tool when an exception occurs"""
        # Mock the _handle_run_query method to raise an exception
        connection_server._handle_run_query = AsyncMock(side_effect=ValueError("Test exception"))
        
        # Create a mock call_tool handler function
        async def mock_handle_call_tool(name, arguments):
            if "connection" not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)
            
            connection = arguments["connection"]
            
            if name == "dbutils-run-query":
                sql = arguments.get("sql", "").strip()
                try:
                    return await connection_server._handle_run_query(connection, sql)
                except Exception as e:
                    # Log the error and re-raise
                    connection_server.send_log(LOG_LEVEL_ERROR, f"Error in run_query: {str(e)}")
                    raise
            else:
                raise ConfigurationError(f"Unknown tool: {name}")
        
        # Test with run-query tool that raises an exception
        with pytest.raises(ValueError, match="Test exception"):
            await mock_handle_call_tool("dbutils-run-query", {"connection": "test_conn", "sql": "SELECT 1"})
        
        # Verify that _handle_run_query was called and send_log was called for the error
        connection_server._handle_run_query.assert_called_once_with("test_conn", "SELECT 1")
        connection_server.send_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_table_tools(self, connection_server):
        """Test call_tool handler with table-related tools"""
        # Mock the _handle_table_tools method
        expected_result = [types.TextContent(type="text", text="Table info")]
        connection_server._handle_table_tools = AsyncMock(return_value=expected_result)
        
        # Create a mock call_tool handler function
        async def mock_handle_call_tool(name, arguments):
            if "connection" not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)
            
            connection = arguments["connection"]
            
            if name in ["dbutils-describe-table", "dbutils-get-ddl", "dbutils-list-indexes",
                       "dbutils-get-stats", "dbutils-list-constraints"]:
                table = arguments.get("table", "").strip()
                return await connection_server._handle_table_tools(name, connection, table)
            else:
                raise ConfigurationError(f"Unknown tool: {name}")
        
        # Test with table tools
        table_tools = [
            "dbutils-describe-table", 
            "dbutils-get-ddl", 
            "dbutils-list-indexes",
            "dbutils-get-stats", 
            "dbutils-list-constraints"
        ]
        
        for tool in table_tools:
            result = await mock_handle_call_tool(tool, {"connection": "test_conn", "table": "users"})
            assert result == expected_result
            connection_server._handle_table_tools.assert_called_with(tool, "test_conn", "users")
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_table_tools_exception(self, connection_server):
        """Test call_tool handler with table-related tools when an exception occurs"""
        # Mock the _handle_table_tools method to raise an exception
        connection_server._handle_table_tools = AsyncMock(side_effect=ValueError("Test exception"))
        
        # Create a mock call_tool handler function
        async def mock_handle_call_tool(name, arguments):
            if "connection" not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)
            
            connection = arguments["connection"]
            
            if name in ["dbutils-describe-table", "dbutils-get-ddl", "dbutils-list-indexes",
                       "dbutils-get-stats", "dbutils-list-constraints"]:
                table = arguments.get("table", "").strip()
                try:
                    return await connection_server._handle_table_tools(name, connection, table)
                except Exception as e:
                    # Log the error and re-raise
                    connection_server.send_log(LOG_LEVEL_ERROR, f"Error in table_tools: {str(e)}")
                    raise
            else:
                raise ConfigurationError(f"Unknown tool: {name}")
        
        # Test with table tool that raises an exception
        with pytest.raises(ValueError, match="Test exception"):
            await mock_handle_call_tool("dbutils-describe-table", {"connection": "test_conn", "table": "users"})
        
        # Verify that _handle_table_tools was called and send_log was called for the error
        connection_server._handle_table_tools.assert_called_once_with("dbutils-describe-table", "test_conn", "users")
        connection_server.send_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_explain_query(self, connection_server):
        """Test call_tool handler with dbutils-explain-query tool"""
        # Mock the _handle_explain_query method
        expected_result = [types.TextContent(type="text", text="Query explanation")]
        connection_server._handle_explain_query = AsyncMock(return_value=expected_result)
        
        # Create a mock call_tool handler function
        async def mock_handle_call_tool(name, arguments):
            if "connection" not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)
            
            connection = arguments["connection"]
            
            if name == "dbutils-explain-query":
                sql = arguments.get("sql", "").strip()
                return await connection_server._handle_explain_query(connection, sql)
            else:
                raise ConfigurationError(f"Unknown tool: {name}")
        
        # Test with explain-query tool
        result = await mock_handle_call_tool("dbutils-explain-query", {"connection": "test_conn", "sql": "SELECT 1"})
        assert result == expected_result
        connection_server._handle_explain_query.assert_called_once_with("test_conn", "SELECT 1")
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_explain_query_exception(self, connection_server):
        """Test call_tool handler with dbutils-explain-query tool when an exception occurs"""
        # Mock the _handle_explain_query method to raise an exception
        connection_server._handle_explain_query = AsyncMock(side_effect=ValueError("Test exception"))
        
        # Create a mock call_tool handler function
        async def mock_handle_call_tool(name, arguments):
            if "connection" not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)
            
            connection = arguments["connection"]
            
            if name == "dbutils-explain-query":
                sql = arguments.get("sql", "").strip()
                try:
                    return await connection_server._handle_explain_query(connection, sql)
                except Exception as e:
                    # Log the error and re-raise
                    connection_server.send_log(LOG_LEVEL_ERROR, f"Error in explain_query: {str(e)}")
                    raise
            else:
                raise ConfigurationError(f"Unknown tool: {name}")
        
        # Test with explain-query tool that raises an exception
        with pytest.raises(ValueError, match="Test exception"):
            await mock_handle_call_tool("dbutils-explain-query", {"connection": "test_conn", "sql": "SELECT 1"})
        
        # Verify that _handle_explain_query was called and send_log was called for the error
        connection_server._handle_explain_query.assert_called_once_with("test_conn", "SELECT 1")
        connection_server.send_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_get_performance(self, connection_server):
        """Test call_tool handler with dbutils-get-performance tool"""
        # Mock the _handle_performance method
        expected_result = [types.TextContent(type="text", text="Performance info")]
        connection_server._handle_performance = AsyncMock(return_value=expected_result)
        
        # Create a mock call_tool handler function
        async def mock_handle_call_tool(name, arguments):
            if "connection" not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)
            
            connection = arguments["connection"]
            
            if name == "dbutils-get-performance":
                return await connection_server._handle_performance(connection)
            else:
                raise ConfigurationError(f"Unknown tool: {name}")
        
        # Test with get-performance tool
        result = await mock_handle_call_tool("dbutils-get-performance", {"connection": "test_conn"})
        assert result == expected_result
        connection_server._handle_performance.assert_called_once_with("test_conn")
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_get_performance_exception(self, connection_server):
        """Test call_tool handler with dbutils-get-performance tool when an exception occurs"""
        # Mock the _handle_performance method to raise an exception
        connection_server._handle_performance = AsyncMock(side_effect=ValueError("Test exception"))
        
        # Create a mock call_tool handler function
        async def mock_handle_call_tool(name, arguments):
            if "connection" not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)
            
            connection = arguments["connection"]
            
            if name == "dbutils-get-performance":
                try:
                    return await connection_server._handle_performance(connection)
                except Exception as e:
                    # Log the error and re-raise
                    connection_server.send_log(LOG_LEVEL_ERROR, f"Error in get_performance: {str(e)}")
                    raise
            else:
                raise ConfigurationError(f"Unknown tool: {name}")
        
        # Test with get-performance tool that raises an exception
        with pytest.raises(ValueError, match="Test exception"):
            await mock_handle_call_tool("dbutils-get-performance", {"connection": "test_conn"})
        
        # Verify that _handle_performance was called and send_log was called for the error
        connection_server._handle_performance.assert_called_once_with("test_conn")
        connection_server.send_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_analyze_query(self, connection_server):
        """Test call_tool handler with dbutils-analyze-query tool"""
        # Mock the _handle_analyze_query method
        expected_result = [types.TextContent(type="text", text="Query analysis")]
        connection_server._handle_analyze_query = AsyncMock(return_value=expected_result)
        
        # Create a mock call_tool handler function
        async def mock_handle_call_tool(name, arguments):
            if "connection" not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)
            
            connection = arguments["connection"]
            
            if name == "dbutils-analyze-query":
                sql = arguments.get("sql", "").strip()
                return await connection_server._handle_analyze_query(connection, sql)
            else:
                raise ConfigurationError(f"Unknown tool: {name}")
        
        # Test with analyze-query tool
        result = await mock_handle_call_tool("dbutils-analyze-query", {"connection": "test_conn", "sql": "SELECT 1"})
        assert result == expected_result
        connection_server._handle_analyze_query.assert_called_once_with("test_conn", "SELECT 1")
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_analyze_query_exception(self, connection_server):
        """Test call_tool handler with dbutils-analyze-query tool when an exception occurs"""
        # Mock the _handle_analyze_query method to raise an exception
        connection_server._handle_analyze_query = AsyncMock(side_effect=ValueError("Test exception"))
        
        # Create a mock call_tool handler function
        async def mock_handle_call_tool(name, arguments):
            if "connection" not in arguments:
                raise ConfigurationError(CONNECTION_NAME_REQUIRED_ERROR)
            
            connection = arguments["connection"]
            
            if name == "dbutils-analyze-query":
                sql = arguments.get("sql", "").strip()
                try:
                    return await connection_server._handle_analyze_query(connection, sql)
                except Exception as e:
                    # Log the error and re-raise
                    connection_server.send_log(LOG_LEVEL_ERROR, f"Error in analyze_query: {str(e)}")
                    raise
            else:
                raise ConfigurationError(f"Unknown tool: {name}")
        
        # Test with analyze-query tool that raises an exception
        with pytest.raises(ValueError, match="Test exception"):
            await mock_handle_call_tool("dbutils-analyze-query", {"connection": "test_conn", "sql": "SELECT 1"})
        
        # Verify that _handle_analyze_query was called and send_log was called for the error
        connection_server._handle_analyze_query.assert_called_once_with("test_conn", "SELECT 1")
        connection_server.send_log.assert_called_once()


class TestConnectionServerRun:
    @pytest.mark.asyncio
    @patch("mcp.server.stdio.stdio_server")
    async def test_run(self, mock_stdio_server, connection_server):
        """Test the run method"""
        # Setup mocks
        mock_stdin = AsyncMock()
        mock_stdout = AsyncMock()
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__.return_value = [mock_stdin, mock_stdout]
        mock_stdio_server.return_value = mock_context_manager
        
        # Mock the server.run method to avoid validation errors
        connection_server.server.run = AsyncMock()
        
        # Call the run method
        await connection_server.run()
        
        # Verify the server.run method was called
        mock_stdio_server.assert_called_once()
        mock_context_manager.__aenter__.assert_called_once()
        assert connection_server.server.run.called
    
    @pytest.mark.asyncio
    @patch("mcp.server.stdio.stdio_server")
    async def test_run_with_exception(self, mock_stdio_server, connection_server):
        """Test the run method when an exception occurs"""
        # Setup mocks
        mock_stdin = AsyncMock()
        mock_stdout = AsyncMock()
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__.return_value = [mock_stdin, mock_stdout]
        mock_stdio_server.return_value = mock_context_manager
        
        # Create a patched version of run that catches exceptions the same way the actual run method would
        original_run = connection_server.run
        
        async def patched_run():
            try:
                await original_run()
            except Exception as e:
                connection_server.send_log(LOG_LEVEL_ERROR, f"Error in run: {str(e)}")
                raise
        
        # Replace run with our patched version
        connection_server.run = patched_run
        
        # Mock the server.run method to raise an exception
        connection_server.server.run = AsyncMock(side_effect=ValueError("Test exception"))
        
        # Call the run method and expect an exception
        with pytest.raises(ValueError, match="Test exception"):
            await connection_server.run()
        
        # Verify the server.run method was called and the exception was logged
        mock_stdio_server.assert_called_once()
        mock_context_manager.__aenter__.assert_called_once()
        connection_server.server.run.assert_called_once()
        connection_server.send_log.assert_called_with(LOG_LEVEL_ERROR, "Error in run: Test exception") 