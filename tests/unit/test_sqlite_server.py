"""Unit tests for SQLite server implementation"""
import json
import sqlite3
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import mcp.types as types
import pytest

from mcp_dbutils.sqlite.config import SQLiteConfig
from mcp_dbutils.sqlite.server import SQLiteServer


@pytest.fixture
def mock_sqlite_config():
    """Mock SQLite configuration"""
    config = MagicMock(spec=SQLiteConfig)
    config.path = "/path/to/test.db"
    config.absolute_path = "/path/to/test.db"
    config.debug = False

    # Mock the get_connection_params method
    config.get_connection_params.return_value = {
        "database": "/path/to/test.db"
    }

    # Mock the get_masked_connection_info method
    config.get_masked_connection_info.return_value = {
        "database": "/path/to/test.db"
    }

    return config


@pytest.fixture
def mock_cursor():
    """Mock SQLite cursor"""
    cursor = MagicMock()
    cursor.fetchall.return_value = []
    cursor.description = []
    return cursor


@pytest.fixture
def mock_connection(mock_cursor):
    """Mock SQLite connection"""
    connection = MagicMock()
    connection.execute.return_value = mock_cursor
    connection.row_factory = None
    connection.close = MagicMock()
    return connection


class TestSQLiteServer:
    """Test SQLite server implementation"""

    @patch("sqlite3.connect")
    @patch("pathlib.Path.mkdir")
    def test_init(self, mock_mkdir, mock_connect, mock_sqlite_config):
        """Test server initialization"""
        # Setup
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = None

        # Execute
        server = SQLiteServer(mock_sqlite_config)

        # Verify
        assert server.config == mock_sqlite_config
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_connect.assert_called_once()

    @patch("sqlite3.connect")
    def test_get_connection(self, mock_connect, mock_sqlite_config):
        """Test getting connection"""
        # Setup
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        with patch.object(SQLiteServer, "__init__", return_value=None):
            server = SQLiteServer(None)
            server.config = mock_sqlite_config
            server.log = MagicMock()

            # Execute
            connection = server._get_connection()

            # Verify
            assert connection == mock_conn
            mock_connect.assert_called_once_with(**mock_sqlite_config.get_connection_params())
            assert connection.row_factory == sqlite3.Row

    @pytest.mark.asyncio
    @patch("sqlite3.connect")
    async def test_list_resources(self, mock_connect, mock_sqlite_config, mock_connection, mock_cursor):
        """Test listing resources"""
        # Setup
        mock_connect.return_value = mock_connection
        mock_cursor.fetchall.return_value = [("users",), ("products",)]

        with patch.object(SQLiteServer, "__init__", return_value=None), \
             patch.object(SQLiteServer, "_get_connection", return_value=mock_connection):
            server = SQLiteServer(None)
            server.config = mock_sqlite_config
            server.log = MagicMock()

            # Execute
            resources = await server.list_resources()

            # Verify
            assert len(resources) == 2
            assert resources[0].name == "users schema"
            # Convert AnyUrl to string for comparison
            assert str(resources[0].uri) == "sqlite://users/schema"
            assert resources[1].name == "products schema"
            mock_connection.execute.assert_called_once()
            mock_cursor.fetchall.assert_called_once()

    @pytest.mark.asyncio
    @patch("sqlite3.connect")
    async def test_read_resource(self, mock_connect, mock_sqlite_config, mock_connection, mock_cursor):
        """Test reading resource"""
        # Setup
        mock_connect.return_value = mock_connection

        # Mock table_info results
        table_info_results = [
            {"name": "id", "type": "INTEGER", "notnull": 1, "pk": 1},
            {"name": "name", "type": "TEXT", "notnull": 0, "pk": 0}
        ]

        # Mock index_list results
        index_list_results = [
            {"name": "idx_name", "unique": 1}
        ]

        # Configure mock cursor to return different results for different queries
        def mock_execute(query):
            if "table_info" in query:
                mock_cursor.fetchall.return_value = table_info_results
            elif "index_list" in query:
                mock_cursor.fetchall.return_value = index_list_results
            return mock_cursor

        mock_connection.execute.side_effect = mock_execute

        with patch.object(SQLiteServer, "__init__", return_value=None), \
             patch.object(SQLiteServer, "_get_connection", return_value=mock_connection):
            server = SQLiteServer(None)
            server.config = mock_sqlite_config
            server.log = MagicMock()

            # Execute
            result = await server.read_resource("sqlite://users/schema")

            # Verify
            import json
            result_dict = json.loads(result)  # Convert JSON string to dict
            assert len(result_dict["columns"]) == 2
            assert result_dict["columns"][0]["name"] == "id"
            assert result_dict["columns"][0]["primary_key"] is True
            assert result_dict["columns"][1]["name"] == "name"
            assert result_dict["columns"][1]["nullable"] is True
            assert len(result_dict["indexes"]) == 1
            assert result_dict["indexes"][0]["name"] == "idx_name"
            assert result_dict["indexes"][0]["unique"] is True
            assert mock_connection.execute.call_count == 2

    def test_get_tools(self, mock_sqlite_config):
        """Test getting tools"""
        # Setup
        with patch.object(SQLiteServer, "__init__", return_value=None):
            server = SQLiteServer(None)

            # Execute
            tools = server.get_tools()

            # Verify
            assert len(tools) == 1
            assert tools[0].name == "query"
            assert "SQL" in tools[0].description
            assert "sql" in tools[0].inputSchema["properties"]
            assert "sql" in tools[0].inputSchema["required"]

    @pytest.mark.asyncio
    @patch("sqlite3.connect")
    async def test_call_tool_query(self, mock_connect, mock_sqlite_config, mock_connection, mock_cursor):
        """Test calling query tool"""
        # Setup
        mock_connect.return_value = mock_connection
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [{"id": 1, "name": "Test User"}]

        with patch.object(SQLiteServer, "__init__", return_value=None), \
             patch.object(SQLiteServer, "_get_connection", return_value=mock_connection):
            server = SQLiteServer(None)
            server.config = mock_sqlite_config
            server.log = MagicMock()

            # Execute
            result = await server.call_tool("query", {"sql": "SELECT * FROM users"})

            # Verify
            assert len(result) == 1
            assert result[0].type == "text"
            import json
            result_dict = json.loads(result[0].text)
            assert result_dict["type"] == "sqlite"
            assert result_dict["query_result"]["row_count"] == 1
            assert "id" in result_dict["query_result"]["columns"]
            assert "name" in result_dict["query_result"]["columns"]
            mock_connection.execute.assert_called_once_with("SELECT * FROM users")
            mock_cursor.fetchall.assert_called_once()

    @pytest.mark.asyncio
    @patch("sqlite3.connect")
    async def test_call_tool_with_connection(self, mock_connect, mock_sqlite_config, mock_cursor):
        """Test calling query tool with specific connection"""
        # Setup
        mock_connection = MagicMock()
        mock_connection.execute.return_value = mock_cursor
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [{"id": 1, "name": "Test User"}]
        mock_connect.return_value = mock_connection

        with patch.object(SQLiteServer, "__init__", return_value=None), \
             patch.object(SQLiteConfig, "from_yaml") as mock_from_yaml:

            mock_config = MagicMock(spec=SQLiteConfig)
            mock_config.get_connection_params.return_value = {"database": "/path/to/other.db"}
            mock_config.get_masked_connection_info.return_value = {"database": "/path/to/other.db"}
            mock_from_yaml.return_value = mock_config

            server = SQLiteServer(None)
            server.config = mock_sqlite_config
            server.config_path = "/path/to/config.yaml"
            server.log = MagicMock()

            # Execute the method with a specific connection
            try:
                await server.call_tool("query", {
                    "sql": "SELECT * FROM users",
                    "connection": "test_connection"
                })
            except Exception:
                # We don't care about the result, just that from_yaml was called
                pass

            # Verify that from_yaml was called with the correct arguments
            mock_from_yaml.assert_called_once_with("/path/to/config.yaml", "test_connection")
            mock_connect.assert_called_once_with(**mock_config.get_connection_params())

    @pytest.mark.asyncio
    async def test_call_tool_invalid_name(self, mock_sqlite_config):
        """Test calling invalid tool"""
        # Setup
        with patch.object(SQLiteServer, "__init__", return_value=None):
            server = SQLiteServer(None)
            server.config = mock_sqlite_config
            server.log = MagicMock()

            # Execute and verify
            with pytest.raises(ValueError, match="未知工具"):
                await server.call_tool("invalid_tool", {})

    @pytest.mark.asyncio
    async def test_call_tool_empty_sql(self, mock_sqlite_config):
        """Test calling query tool with empty SQL"""
        # Setup
        with patch.object(SQLiteServer, "__init__", return_value=None):
            server = SQLiteServer(None)
            server.config = mock_sqlite_config
            server.log = MagicMock()

            # Execute and verify
            with pytest.raises(ValueError, match="SQL查询不能为空"):
                await server.call_tool("query", {"sql": ""})

    @pytest.mark.asyncio
    async def test_call_tool_non_select(self, mock_sqlite_config):
        """Test calling query tool with non-SELECT SQL"""
        # Setup
        with patch.object(SQLiteServer, "__init__", return_value=None):
            server = SQLiteServer(None)
            server.config = mock_sqlite_config
            server.log = MagicMock()

            # Execute and verify
            with pytest.raises(ValueError, match="仅支持SELECT查询"):
                await server.call_tool("query", {"sql": "DELETE FROM users"})

    @pytest.mark.asyncio
    @patch("sqlite3.connect")
    async def test_call_tool_query_error(self, mock_connect, mock_sqlite_config):
        """Test calling query tool with error"""
        # Setup
        mock_connect.return_value = MagicMock()
        mock_connect.return_value.execute.side_effect = sqlite3.Error("no such table: users")

        with patch.object(SQLiteServer, "__init__", return_value=None), \
             patch.object(SQLiteServer, "_get_connection", side_effect=mock_connect):
            server = SQLiteServer(None)
            server.config = mock_sqlite_config
            server.log = MagicMock()

            # Execute
            result = await server.call_tool("query", {"sql": "SELECT * FROM users"})

            # Verify
            assert len(result) == 1
            assert result[0].type == "text"
            import json
            result_dict = json.loads(result[0].text)
            assert result_dict["type"] == "sqlite"
            assert "error" in result_dict
            assert "no such table" in result_dict["error"]

    @pytest.mark.asyncio
    async def test_cleanup(self, mock_sqlite_config):
        """Test cleanup"""
        # Setup
        with patch.object(SQLiteServer, "__init__", return_value=None):
            server = SQLiteServer(None)
            server.config = mock_sqlite_config
            server.log = MagicMock()

            # Execute
            await server.cleanup()

            # Verify - SQLite doesn't need cleanup, so just make sure it doesn't error
            pass

    @pytest.mark.asyncio
    @patch("sqlite3.connect")
    async def test_call_tool_connection_close_error(self, mock_connect, mock_sqlite_config, mock_connection):
        """Test error handling when closing connection"""
        # Setup
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [{"id": 1, "name": "Test User"}]
        mock_connection.execute.return_value = mock_cursor

        # We need to make the close method raise an exception only when called directly,
        # not when called through the context manager
        original_close = mock_connection.close
        close_call_count = 0

        def side_effect_close():
            nonlocal close_call_count
            close_call_count += 1
            # Only raise on the second call (after the with block)
            if close_call_count > 1:
                raise Exception("Connection close error")

        mock_connection.close = MagicMock(side_effect=side_effect_close)

        with patch.object(SQLiteServer, "__init__", return_value=None), \
             patch.object(SQLiteServer, "_get_connection", return_value=mock_connection):
            server = SQLiteServer(None)
            server.config = mock_sqlite_config
            server.log = MagicMock()

            # Execute
            result = await server.call_tool("query", {"sql": "SELECT * FROM users"})

            # Verify basic result
            assert len(result) == 1

            # Verify warning log was called
            warning_calls = [call for call in server.log.call_args_list if call[0][0] == 'warning']
            assert any('Connection close error' in call[0][1] for call in warning_calls)
