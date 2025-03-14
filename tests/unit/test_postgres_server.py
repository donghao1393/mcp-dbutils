"""Unit tests for PostgreSQL server implementation"""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import mcp.types as types
import psycopg2
import pytest
from psycopg2.pool import SimpleConnectionPool

from mcp_dbutils.postgres.config import PostgreSQLConfig
from mcp_dbutils.postgres.server import PostgreSQLServer


@pytest.fixture
def mock_postgres_config():
    """Mock PostgreSQL configuration"""
    config = MagicMock(spec=PostgreSQLConfig)
    config.host = "localhost"
    config.port = 5432
    config.database = "test_db"
    config.user = "test_user"
    config.password = "test_password"
    config.debug = False
    
    # Mock the get_connection_params method
    config.get_connection_params.return_value = {
        "host": "localhost",
        "port": 5432,
        "database": "test_db",
        "user": "test_user",
        "password": "test_password"
    }
    
    # Mock the get_masked_connection_info method
    config.get_masked_connection_info.return_value = {
        "host": "localhost",
        "port": 5432,
        "database": "test_db",
        "user": "test_user",
        "password": "********"
    }
    
    return config


@pytest.fixture
def mock_cursor():
    """Mock PostgreSQL cursor"""
    cursor = MagicMock()
    cursor.__enter__ = MagicMock(return_value=cursor)
    cursor.__exit__ = MagicMock(return_value=None)
    return cursor


@pytest.fixture
def mock_connection(mock_cursor):
    """Mock PostgreSQL connection"""
    connection = MagicMock()
    connection.cursor.return_value = mock_cursor
    connection.close = MagicMock()
    return connection


@pytest.fixture
def mock_pool(mock_connection):
    """Mock PostgreSQL connection pool"""
    pool = MagicMock(spec=SimpleConnectionPool)
    pool.getconn.return_value = mock_connection
    pool.putconn = MagicMock()
    pool.closeall = MagicMock()
    return pool


class TestPostgreSQLServer:
    """Test PostgreSQL server implementation"""
    
    @patch("psycopg2.connect")
    @patch("psycopg2.pool.SimpleConnectionPool")
    def test_init(self, mock_pool_class, mock_connect, mock_postgres_config):
        """Test server initialization"""
        # Setup
        mock_connect.return_value = MagicMock()
        mock_pool_class.return_value = MagicMock(spec=SimpleConnectionPool)
        
        # Execute
        server = PostgreSQLServer(mock_postgres_config)
        
        # Verify
        assert server.config == mock_postgres_config
        mock_connect.assert_called_once()
        mock_pool_class.assert_called_once()
        assert hasattr(server, "pool")
    
    @pytest.mark.asyncio
    async def test_list_resources(self, mock_postgres_config, mock_pool, mock_cursor):
        """Test listing resources"""
        # Setup
        mock_tables = [
            ("users", "User table"),
            ("products", None)
        ]
        mock_cursor.fetchall.return_value = mock_tables
        
        with patch.object(PostgreSQLServer, "__init__", return_value=None):
            server = PostgreSQLServer(None)
            server.config = mock_postgres_config
            server.pool = mock_pool
            server.log = MagicMock()
            
            # Execute
            resources = await server.list_resources()
            
            # Verify
            assert len(resources) == 2
            assert resources[0].name == "users schema"
            assert resources[0].uri == "postgres://localhost/users/schema"
            assert resources[0].description == "User table"
            assert resources[1].name == "products schema"
            assert resources[1].description is None
            mock_pool.getconn.assert_called_once()
            mock_cursor.execute.assert_called_once()
            mock_cursor.fetchall.assert_called_once()
            mock_pool.putconn.assert_called_once_with(mock_connection)
    
    @pytest.mark.asyncio
    async def test_read_resource(self, mock_postgres_config, mock_pool, mock_cursor):
        """Test reading resource"""
        # Setup
        mock_columns = [
            ("id", "integer", "NO", "Primary key"),
            ("name", "varchar", "YES", "User name")
        ]
        mock_constraints = [
            ("pk_users", "p")  # p is for primary key in PostgreSQL
        ]
        
        # Configure mock cursor to return different results for different queries
        def mock_execute(query, params=None):
            if "columns" in query:
                mock_cursor.fetchall.return_value = mock_columns
            elif "constraint" in query:
                mock_cursor.fetchall.return_value = mock_constraints
        
        mock_cursor.execute.side_effect = mock_execute
        
        with patch.object(PostgreSQLServer, "__init__", return_value=None):
            server = PostgreSQLServer(None)
            server.config = mock_postgres_config
            server.pool = mock_pool
            server.log = MagicMock()
            
            # Execute
            result = await server.read_resource("postgres://localhost/users/schema")
            
            # Verify
            result_dict = eval(result)  # Convert string representation to dict
            assert len(result_dict["columns"]) == 2
            assert result_dict["columns"][0]["name"] == "id"
            assert result_dict["columns"][0]["nullable"] is False
            assert len(result_dict["constraints"]) == 1
            assert result_dict["constraints"][0]["name"] == "pk_users"
            mock_pool.getconn.assert_called_once()
            assert mock_cursor.execute.call_count == 2
            mock_pool.putconn.assert_called_once_with(mock_connection)
    
    def test_get_tools(self, mock_postgres_config):
        """Test getting tools"""
        # Setup
        with patch.object(PostgreSQLServer, "__init__", return_value=None):
            server = PostgreSQLServer(None)
            
            # Execute
            tools = server.get_tools()
            
            # Verify
            assert len(tools) == 1
            assert tools[0].name == "query"
            assert "SQL" in tools[0].description
            assert "sql" in tools[0].inputSchema["properties"]
            assert "sql" in tools[0].inputSchema["required"]
    
    @pytest.mark.asyncio
    async def test_call_tool_query(self, mock_postgres_config, mock_pool, mock_cursor):
        """Test calling query tool"""
        # Setup
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(1, "Test User")]
        
        with patch.object(PostgreSQLServer, "__init__", return_value=None):
            server = PostgreSQLServer(None)
            server.config = mock_postgres_config
            server.pool = mock_pool
            server.log = MagicMock()
            
            # Execute
            result = await server.call_tool("query", {"sql": "SELECT * FROM users"})
            
            # Verify
            assert len(result) == 1
            assert result[0].type == "text"
            result_dict = eval(result[0].text)
            assert result_dict["type"] == "postgres"
            assert result_dict["query_result"]["row_count"] == 1
            assert "id" in result_dict["query_result"]["columns"]
            assert "name" in result_dict["query_result"]["columns"]
            mock_pool.getconn.assert_called_once()
            assert mock_cursor.execute.call_count >= 2  # BEGIN TRANSACTION + query + ROLLBACK
            mock_pool.putconn.assert_called_once_with(mock_connection)
    
    @pytest.mark.asyncio
    async def test_call_tool_with_connection(self, mock_postgres_config, mock_cursor):
        """Test calling query tool with specific connection"""
        # Setup
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(1, "Test User")]
        
        with patch.object(PostgreSQLServer, "__init__", return_value=None), \
             patch("psycopg2.connect") as mock_connect, \
             patch.object(PostgreSQLConfig, "from_yaml") as mock_from_yaml:
            
            mock_connection = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_connection
            
            mock_config = MagicMock(spec=PostgreSQLConfig)
            mock_config.get_connection_params.return_value = {"host": "test_host"}
            mock_config.get_masked_connection_info.return_value = {"host": "test_host"}
            mock_from_yaml.return_value = mock_config
            
            server = PostgreSQLServer(None)
            server.config = mock_postgres_config
            server.config_path = "/path/to/config.yaml"
            server.log = MagicMock()
            
            # Execute
            result = await server.call_tool("query", {
                "sql": "SELECT * FROM users",
                "connection": "test_connection"
            })
            
            # Verify
            assert len(result) == 1
            result_dict = eval(result[0].text)
            assert result_dict["type"] == "postgres"
            assert result_dict["config_name"] == "test_connection"
            mock_from_yaml.assert_called_once_with("/path/to/config.yaml", "test_connection")
            mock_connect.assert_called_once()
            mock_connection.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_call_tool_invalid_name(self, mock_postgres_config):
        """Test calling invalid tool"""
        # Setup
        with patch.object(PostgreSQLServer, "__init__", return_value=None):
            server = PostgreSQLServer(None)
            server.config = mock_postgres_config
            server.log = MagicMock()
            
            # Execute and verify
            with pytest.raises(ValueError, match="未知工具"):
                await server.call_tool("invalid_tool", {})
    
    @pytest.mark.asyncio
    async def test_call_tool_empty_sql(self, mock_postgres_config):
        """Test calling query tool with empty SQL"""
        # Setup
        with patch.object(PostgreSQLServer, "__init__", return_value=None):
            server = PostgreSQLServer(None)
            server.config = mock_postgres_config
            server.log = MagicMock()
            
            # Execute and verify
            with pytest.raises(ValueError, match="SQL查询不能为空"):
                await server.call_tool("query", {"sql": ""})
    
    @pytest.mark.asyncio
    async def test_call_tool_non_select(self, mock_postgres_config):
        """Test calling query tool with non-SELECT SQL"""
        # Setup
        with patch.object(PostgreSQLServer, "__init__", return_value=None):
            server = PostgreSQLServer(None)
            server.config = mock_postgres_config
            server.log = MagicMock()
            
            # Execute and verify
            with pytest.raises(ValueError, match="仅支持SELECT查询"):
                await server.call_tool("query", {"sql": "DELETE FROM users"})
    
    @pytest.mark.asyncio
    async def test_call_tool_query_error(self, mock_postgres_config, mock_pool, mock_cursor):
        """Test calling query tool with error"""
        # Setup
        pg_error = psycopg2.Error()
        pg_error.pgcode = "42P01"  # Undefined table
        pg_error.pgerror = "relation \"users\" does not exist"
        mock_cursor.execute.side_effect = pg_error
        
        with patch.object(PostgreSQLServer, "__init__", return_value=None):
            server = PostgreSQLServer(None)
            server.config = mock_postgres_config
            server.pool = mock_pool
            server.log = MagicMock()
            
            # Execute
            result = await server.call_tool("query", {"sql": "SELECT * FROM users"})
            
            # Verify
            assert len(result) == 1
            assert result[0].type == "text"
            result_dict = eval(result[0].text)
            assert result_dict["type"] == "postgres"
            assert "error" in result_dict
            assert "42P01" in result_dict["error"]
            assert "relation" in result_dict["error"]
            mock_pool.getconn.assert_called_once()
            mock_pool.putconn.assert_called_once_with(mock_connection)
    
    @pytest.mark.asyncio
    async def test_call_tool_generic_error(self, mock_postgres_config, mock_pool, mock_cursor):
        """Test calling query tool with generic error"""
        # Setup
        mock_cursor.execute.side_effect = Exception("Generic error")
        
        with patch.object(PostgreSQLServer, "__init__", return_value=None):
            server = PostgreSQLServer(None)
            server.config = mock_postgres_config
            server.pool = mock_pool
            server.log = MagicMock()
            
            # Execute
            result = await server.call_tool("query", {"sql": "SELECT * FROM users"})
            
            # Verify
            assert len(result) == 1
            result_dict = eval(result[0].text)
            assert "error" in result_dict
            assert "Generic error" in result_dict["error"]
            mock_pool.getconn.assert_called_once()
            mock_pool.putconn.assert_called_once_with(mock_connection)
    
    @pytest.mark.asyncio
    async def test_cleanup(self, mock_postgres_config, mock_pool):
        """Test cleanup"""
        # Setup
        with patch.object(PostgreSQLServer, "__init__", return_value=None):
            server = PostgreSQLServer(None)
            server.pool = mock_pool
            server.log = MagicMock()
            
            # Execute
            await server.cleanup()
            
            # Verify
            server.log.assert_called_once()
            mock_pool.closeall.assert_called_once()
