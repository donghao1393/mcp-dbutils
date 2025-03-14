"""Unit tests for MySQL server implementation"""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import mcp.types as types
import pytest
from mysql.connector.pooling import MySQLConnectionPool

from mcp_dbutils.mysql.config import MySQLConfig
from mcp_dbutils.mysql.server import MySQLServer


@pytest.fixture
def mock_mysql_config():
    """Mock MySQL configuration"""
    config = MagicMock(spec=MySQLConfig)
    config.host = "localhost"
    config.port = 3306
    config.database = "test_db"
    config.user = "test_user"
    config.password = "test_password"
    config.debug = False
    
    # Mock the get_connection_params method
    config.get_connection_params.return_value = {
        "host": "localhost",
        "port": 3306,
        "database": "test_db",
        "user": "test_user",
        "password": "test_password"
    }
    
    # Mock the get_masked_connection_info method
    config.get_masked_connection_info.return_value = {
        "host": "localhost",
        "port": 3306,
        "database": "test_db",
        "user": "test_user",
        "password": "********"
    }
    
    return config


@pytest.fixture
def mock_cursor():
    """Mock MySQL cursor"""
    cursor = MagicMock()
    cursor.__enter__ = MagicMock(return_value=cursor)
    cursor.__exit__ = MagicMock(return_value=None)
    return cursor


@pytest.fixture
def mock_connection(mock_cursor):
    """Mock MySQL connection"""
    connection = MagicMock()
    connection.cursor.return_value = mock_cursor
    connection.close = MagicMock()
    return connection


@pytest.fixture
def mock_pool(mock_connection):
    """Mock MySQL connection pool"""
    pool = MagicMock(spec=MySQLConnectionPool)
    pool.get_connection.return_value = mock_connection
    return pool


class TestMySQLServer:
    """Test MySQL server implementation"""
    
    @patch("mysql.connector.connect")
    @patch("mysql.connector.pooling.MySQLConnectionPool")
    def test_init(self, mock_pool_class, mock_connect, mock_mysql_config):
        """Test server initialization"""
        # Setup
        mock_connect.return_value = MagicMock()
        mock_pool_class.return_value = MagicMock(spec=MySQLConnectionPool)
        
        # Execute
        server = MySQLServer(mock_mysql_config)
        
        # Verify
        assert server.config == mock_mysql_config
        mock_connect.assert_called_once()
        mock_pool_class.assert_called_once()
        assert hasattr(server, "pool")
    
    @pytest.mark.asyncio
    async def test_list_resources(self, mock_mysql_config, mock_pool, mock_cursor):
        """Test listing resources"""
        # Setup
        mock_tables = [
            {"table_name": "users", "description": "User table"},
            {"table_name": "products", "description": None}
        ]
        mock_cursor.fetchall.return_value = mock_tables
        
        with patch.object(MySQLServer, "__init__", return_value=None):
            server = MySQLServer(None)
            server.config = mock_mysql_config
            server.pool = mock_pool
            server.log = MagicMock()
            
            # Execute
            resources = await server.list_resources()
            
            # Verify
            assert len(resources) == 2
            assert resources[0].name == "users schema"
            assert resources[0].uri == "mysql://localhost/users/schema"
            assert resources[0].description == "User table"
            assert resources[1].name == "products schema"
            assert resources[1].description is None
            mock_pool.get_connection.assert_called_once()
            mock_cursor.execute.assert_called_once()
            mock_cursor.fetchall.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_read_resource(self, mock_mysql_config, mock_pool, mock_cursor):
        """Test reading resource"""
        # Setup
        mock_columns = [
            {"column_name": "id", "data_type": "int", "is_nullable": "NO", "description": "Primary key"},
            {"column_name": "name", "data_type": "varchar", "is_nullable": "YES", "description": "User name"}
        ]
        mock_constraints = [
            {"constraint_name": "pk_users", "constraint_type": "PRIMARY KEY"}
        ]
        
        # Configure mock cursor to return different results for different queries
        def mock_execute(query, params=None):
            if "columns" in query:
                mock_cursor.fetchall.return_value = mock_columns
            elif "constraints" in query:
                mock_cursor.fetchall.return_value = mock_constraints
        
        mock_cursor.execute.side_effect = mock_execute
        
        with patch.object(MySQLServer, "__init__", return_value=None):
            server = MySQLServer(None)
            server.config = mock_mysql_config
            server.pool = mock_pool
            server.log = MagicMock()
            
            # Execute
            result = await server.read_resource("mysql://localhost/users/schema")
            
            # Verify
            result_dict = eval(result)  # Convert string representation to dict
            assert len(result_dict["columns"]) == 2
            assert result_dict["columns"][0]["name"] == "id"
            assert result_dict["columns"][0]["nullable"] is False
            assert len(result_dict["constraints"]) == 1
            assert result_dict["constraints"][0]["name"] == "pk_users"
            mock_pool.get_connection.assert_called_once()
            assert mock_cursor.execute.call_count == 2
    
    def test_get_tools(self, mock_mysql_config):
        """Test getting tools"""
        # Setup
        with patch.object(MySQLServer, "__init__", return_value=None):
            server = MySQLServer(None)
            
            # Execute
            tools = server.get_tools()
            
            # Verify
            assert len(tools) == 1
            assert tools[0].name == "query"
            assert "SQL" in tools[0].description
            assert "sql" in tools[0].inputSchema["properties"]
            assert "sql" in tools[0].inputSchema["required"]
    
    @pytest.mark.asyncio
    async def test_call_tool_query(self, mock_mysql_config, mock_pool, mock_cursor):
        """Test calling query tool"""
        # Setup
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [{"id": 1, "name": "Test User"}]
        
        with patch.object(MySQLServer, "__init__", return_value=None):
            server = MySQLServer(None)
            server.config = mock_mysql_config
            server.pool = mock_pool
            server.log = MagicMock()
            
            # Execute
            result = await server.call_tool("query", {"sql": "SELECT * FROM users"})
            
            # Verify
            assert len(result) == 1
            assert result[0].type == "text"
            result_dict = eval(result[0].text)
            assert result_dict["type"] == "mysql"
            assert result_dict["query_result"]["row_count"] == 1
            assert "id" in result_dict["query_result"]["columns"]
            assert "name" in result_dict["query_result"]["columns"]
            mock_pool.get_connection.assert_called_once()
            assert mock_cursor.execute.call_count >= 2  # SET TRANSACTION + query + ROLLBACK
    
    @pytest.mark.asyncio
    async def test_call_tool_invalid_name(self, mock_mysql_config):
        """Test calling invalid tool"""
        # Setup
        with patch.object(MySQLServer, "__init__", return_value=None):
            server = MySQLServer(None)
            server.config = mock_mysql_config
            server.log = MagicMock()
            
            # Execute and verify
            with pytest.raises(ValueError, match="未知工具"):
                await server.call_tool("invalid_tool", {})
    
    @pytest.mark.asyncio
    async def test_call_tool_empty_sql(self, mock_mysql_config):
        """Test calling query tool with empty SQL"""
        # Setup
        with patch.object(MySQLServer, "__init__", return_value=None):
            server = MySQLServer(None)
            server.config = mock_mysql_config
            server.log = MagicMock()
            
            # Execute and verify
            with pytest.raises(ValueError, match="SQL查询不能为空"):
                await server.call_tool("query", {"sql": ""})
    
    @pytest.mark.asyncio
    async def test_call_tool_non_select(self, mock_mysql_config):
        """Test calling query tool with non-SELECT SQL"""
        # Setup
        with patch.object(MySQLServer, "__init__", return_value=None):
            server = MySQLServer(None)
            server.config = mock_mysql_config
            server.log = MagicMock()
            
            # Execute and verify
            with pytest.raises(ValueError, match="仅支持SELECT查询"):
                await server.call_tool("query", {"sql": "DELETE FROM users"})
    
    @pytest.mark.asyncio
    async def test_call_tool_query_error(self, mock_mysql_config, mock_pool, mock_cursor):
        """Test calling query tool with error"""
        # Setup
        mock_cursor.execute.side_effect = Exception("Test error")
        
        with patch.object(MySQLServer, "__init__", return_value=None):
            server = MySQLServer(None)
            server.config = mock_mysql_config
            server.pool = mock_pool
            server.log = MagicMock()
            
            # Execute
            result = await server.call_tool("query", {"sql": "SELECT * FROM users"})
            
            # Verify
            assert len(result) == 1
            assert result[0].type == "text"
            result_dict = eval(result[0].text)
            assert result_dict["type"] == "mysql"
            assert "error" in result_dict
            assert "Test error" in result_dict["error"]
            mock_pool.get_connection.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup(self, mock_mysql_config, mock_pool):
        """Test cleanup"""
        # Setup
        with patch.object(MySQLServer, "__init__", return_value=None):
            server = MySQLServer(None)
            server.pool = mock_pool
            server.log = MagicMock()
            
            # Execute
            await server.cleanup()
            
            # Verify
            server.log.assert_called_once()
