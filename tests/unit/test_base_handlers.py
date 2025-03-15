from unittest.mock import AsyncMock, MagicMock, patch

import mcp.types as types
import pytest

from mcp_dbutils.base import ConfigurationError, ConnectionServer

# Constants for error messages - use the actual error messages from the code
EMPTY_QUERY_ERROR = "SQL query cannot be empty"
SELECT_ONLY_ERROR = "Only SELECT queries are supported for security reasons"
EMPTY_TABLE_NAME_ERROR = "Table name cannot be empty"

class TestBaseHandlers:
    """Test base.py handler functions"""
    
    @pytest.fixture
    def mock_handler(self):
        """Create a mock handler"""
        handler = AsyncMock()
        handler.db_type = "mock_db"
        handler.stats = MagicMock()
        handler.stats.get_performance_stats.return_value = "Performance stats"
        handler.execute_query = AsyncMock(return_value="Query result")
        handler.execute_tool_query = AsyncMock(return_value="Tool result")
        handler.explain_query = AsyncMock(return_value="Explain result")
        return handler
    
    @pytest.fixture
    def server(self):
        """Create a server instance with mocked components"""
        with patch('mcp_dbutils.base.mcp.server.Server'), \
             patch('mcp_dbutils.base.ConnectionServer._setup_handlers'), \
             patch('mcp_dbutils.base.ConnectionServer._setup_prompts'):
            server = ConnectionServer(config_path="test_config.yaml")
            # Mock the config loading
            server._config = {"connections": {"test_conn": {"type": "mock"}}}
            return server
    
    @pytest.mark.asyncio
    async def test_handle_run_query_empty(self, server):
        """Test _handle_run_query with empty query"""
        with pytest.raises(ConfigurationError, match=EMPTY_QUERY_ERROR):
            await server._handle_run_query("test_conn", "")
    
    @pytest.mark.asyncio
    async def test_handle_run_query_non_select(self, server):
        """Test _handle_run_query with non-SELECT query"""
        with pytest.raises(ConfigurationError, match=SELECT_ONLY_ERROR):
            await server._handle_run_query("test_conn", "INSERT INTO table VALUES (1)")
    
    @pytest.mark.asyncio
    async def test_handle_run_query(self, server, mock_handler):
        """Test _handle_run_query with valid query"""
        with patch.object(server, 'get_handler') as mock_get_handler:
            mock_get_handler.return_value.__aenter__.return_value = mock_handler
            
            result = await server._handle_run_query("test_conn", "SELECT * FROM table")
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert result[0].text == "Query result"
            mock_handler.execute_query.assert_awaited_once_with("SELECT * FROM table")
    
    @pytest.mark.asyncio
    async def test_handle_table_tools_empty(self, server):
        """Test _handle_table_tools with empty table name"""
        with pytest.raises(ConfigurationError, match=EMPTY_TABLE_NAME_ERROR):
            await server._handle_table_tools("tool_name", "test_conn", "")
    
    @pytest.mark.asyncio
    async def test_handle_table_tools(self, server, mock_handler):
        """Test _handle_table_tools with valid table name"""
        with patch.object(server, 'get_handler') as mock_get_handler:
            mock_get_handler.return_value.__aenter__.return_value = mock_handler
            
            result = await server._handle_table_tools("tool_name", "test_conn", "table_name")
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert result[0].text == "Tool result"
            mock_handler.execute_tool_query.assert_awaited_once_with("tool_name", table_name="table_name")
    
    @pytest.mark.asyncio
    async def test_handle_explain_query_empty(self, server):
        """Test _handle_explain_query with empty query"""
        with pytest.raises(ConfigurationError, match=EMPTY_QUERY_ERROR):
            await server._handle_explain_query("test_conn", "")
    
    @pytest.mark.asyncio
    async def test_handle_explain_query(self, server, mock_handler):
        """Test _handle_explain_query with valid query"""
        with patch.object(server, 'get_handler') as mock_get_handler:
            mock_get_handler.return_value.__aenter__.return_value = mock_handler
            
            result = await server._handle_explain_query("test_conn", "SELECT * FROM table")
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert result[0].text == "Tool result"
            mock_handler.execute_tool_query.assert_awaited_once_with("dbutils-explain-query", sql="SELECT * FROM table")
    
    @pytest.mark.asyncio
    async def test_handle_performance(self, server, mock_handler):
        """Test _handle_performance"""
        with patch.object(server, 'get_handler') as mock_get_handler:
            mock_get_handler.return_value.__aenter__.return_value = mock_handler
            
            result = await server._handle_performance("test_conn")
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert result[0].text == "[mock_db]\nPerformance stats"
            mock_handler.stats.get_performance_stats.assert_called_once() 