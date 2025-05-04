"""Test base module write operations"""

import json
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from mcp.types import TextContent

from mcp_dbutils.base import (
    ConnectionServer,
    ConfigurationError,
    ConnectionHandlerError,
    WRITE_CONFIRMATION_REQUIRED_ERROR,
    UNSUPPORTED_WRITE_OPERATION_ERROR,
    CONNECTION_NOT_WRITABLE_ERROR,
    WRITE_OPERATION_NOT_ALLOWED_ERROR,
)


class TestBaseWriteOperations:
    """Test base module write operations"""

    @pytest.fixture
    def connection_server(self):
        """Create a ConnectionServer instance for testing"""
        server = ConnectionServer("tests/fixtures/config.yaml", debug=True)
        # Mock the server's send_log method
        server.send_log = MagicMock()
        return server

    @pytest.mark.asyncio
    async def test_get_sql_type(self, connection_server):
        """Test _get_sql_type method"""
        # Test SELECT statement
        assert connection_server._get_sql_type("SELECT * FROM users") == "SELECT"
        
        # Test INSERT statement
        assert connection_server._get_sql_type("INSERT INTO users VALUES (1, 'test')") == "INSERT"
        
        # Test UPDATE statement
        assert connection_server._get_sql_type("UPDATE users SET name = 'test' WHERE id = 1") == "UPDATE"
        
        # Test DELETE statement
        assert connection_server._get_sql_type("DELETE FROM users WHERE id = 1") == "DELETE"
        
        # Test CREATE statement
        assert connection_server._get_sql_type("CREATE TABLE users (id INT)") == "CREATE"
        
        # Test ALTER statement
        assert connection_server._get_sql_type("ALTER TABLE users ADD COLUMN name TEXT") == "ALTER"
        
        # Test DROP statement
        assert connection_server._get_sql_type("DROP TABLE users") == "DROP"
        
        # Test TRUNCATE statement
        assert connection_server._get_sql_type("TRUNCATE TABLE users") == "TRUNCATE"
        
        # Test BEGIN statement
        assert connection_server._get_sql_type("BEGIN TRANSACTION") == "TRANSACTION_START"
        
        # Test START statement
        assert connection_server._get_sql_type("START TRANSACTION") == "TRANSACTION_START"
        
        # Test COMMIT statement
        assert connection_server._get_sql_type("COMMIT") == "TRANSACTION_COMMIT"
        
        # Test ROLLBACK statement
        assert connection_server._get_sql_type("ROLLBACK") == "TRANSACTION_ROLLBACK"
        
        # Test unknown statement
        assert connection_server._get_sql_type("UNKNOWN STATEMENT") == "UNKNOWN"
        
        # Test case insensitivity
        assert connection_server._get_sql_type("select * from users") == "SELECT"
        assert connection_server._get_sql_type("insert into users values (1, 'test')") == "INSERT"

    @pytest.mark.asyncio
    async def test_extract_table_name(self, connection_server):
        """Test _extract_table_name method"""
        # Test INSERT statement
        assert connection_server._extract_table_name("INSERT INTO users VALUES (1, 'test')") == "users"
        
        # Test INSERT statement with schema
        assert connection_server._extract_table_name("INSERT INTO public.users VALUES (1, 'test')") == "public.users"
        
        # Test UPDATE statement
        assert connection_server._extract_table_name("UPDATE users SET name = 'test' WHERE id = 1") == "users"
        
        # Test DELETE statement
        assert connection_server._extract_table_name("DELETE FROM users WHERE id = 1") == "users"
        
        # Test with quoted table name
        assert connection_server._extract_table_name('INSERT INTO "users" VALUES (1, \'test\')') == "users"
        assert connection_server._extract_table_name("INSERT INTO `users` VALUES (1, 'test')") == "users"
        assert connection_server._extract_table_name("INSERT INTO [users] VALUES (1, 'test')") == "users"
        
        # Test unknown statement
        assert connection_server._extract_table_name("UNKNOWN STATEMENT") == "unknown_table"

    @pytest.mark.asyncio
    async def test_check_write_permission_no_config(self, connection_server):
        """Test _check_write_permission method with no config"""
        # Mock _get_config_or_raise to return a config without write permissions
        connection_server._get_config_or_raise = MagicMock(return_value={
            "type": "mysql",
            "host": "localhost",
            "port": 3306,
            "database": "test",
            "user": "test",
            "password": "test"
        })
        
        # Test with no write permission
        with pytest.raises(ConfigurationError, match=CONNECTION_NOT_WRITABLE_ERROR):
            await connection_server._check_write_permission("test_conn", "users", "INSERT")

    @pytest.mark.asyncio
    async def test_check_write_permission_with_config(self, connection_server):
        """Test _check_write_permission method with config"""
        # Mock _get_config_or_raise to return a config with write permissions
        connection_server._get_config_or_raise = MagicMock(return_value={
            "type": "mysql",
            "host": "localhost",
            "port": 3306,
            "database": "test",
            "user": "test",
            "password": "test",
            "writable": True
        })
        
        # Test with write permission but no table restrictions
        await connection_server._check_write_permission("test_conn", "users", "INSERT")
        
        # Test with write permission and table restrictions
        connection_server._get_config_or_raise = MagicMock(return_value={
            "type": "mysql",
            "host": "localhost",
            "port": 3306,
            "database": "test",
            "user": "test",
            "password": "test",
            "writable": True,
            "write_permissions": {
                "users": ["INSERT", "UPDATE"]
            }
        })
        
        # Test with allowed operation
        await connection_server._check_write_permission("test_conn", "users", "INSERT")
        
        # Test with disallowed operation
        with pytest.raises(ConfigurationError, match=WRITE_OPERATION_NOT_ALLOWED_ERROR.format(operation="DELETE", table="users")):
            await connection_server._check_write_permission("test_conn", "users", "DELETE")
        
        # Test with disallowed table
        with pytest.raises(ConfigurationError, match=WRITE_OPERATION_NOT_ALLOWED_ERROR.format(operation="INSERT", table="orders")):
            await connection_server._check_write_permission("test_conn", "orders", "INSERT")

    @pytest.mark.asyncio
    async def test_handle_execute_write_no_confirmation(self, connection_server):
        """Test _handle_execute_write method without confirmation"""
        # Test without confirmation
        with pytest.raises(ConfigurationError, match=WRITE_CONFIRMATION_REQUIRED_ERROR):
            await connection_server._handle_execute_write("test_conn", "INSERT INTO users VALUES (1, 'test')", "")

    @pytest.mark.asyncio
    async def test_handle_execute_write_unsupported_operation(self, connection_server):
        """Test _handle_execute_write method with unsupported operation"""
        # Mock _get_sql_type to return an unsupported operation
        connection_server._get_sql_type = MagicMock(return_value="SELECT")
        
        # Test with unsupported operation
        with pytest.raises(ConfigurationError, match=UNSUPPORTED_WRITE_OPERATION_ERROR.format(operation="SELECT")):
            await connection_server._handle_execute_write("test_conn", "SELECT * FROM users", "CONFIRM_WRITE")

    @pytest.mark.asyncio
    async def test_handle_execute_write_success(self, connection_server):
        """Test _handle_execute_write method with success"""
        # Mock required methods
        connection_server._get_sql_type = MagicMock(return_value="INSERT")
        connection_server._extract_table_name = MagicMock(return_value="users")
        connection_server._get_config_or_raise = MagicMock(return_value={
            "type": "mysql",
            "host": "localhost",
            "port": 3306,
            "database": "test",
            "user": "test",
            "password": "test",
            "writable": True
        })
        connection_server._check_write_permission = AsyncMock()
        
        # Mock get_handler to return a handler that returns a success message
        mock_handler = AsyncMock()
        mock_handler.__aenter__.return_value.execute_write_query.return_value = "Write operation executed successfully. 1 row affected."
        connection_server.get_handler = MagicMock(return_value=mock_handler)
        
        # Test with success
        result = await connection_server._handle_execute_write(
            "test_conn", 
            "INSERT INTO users VALUES (1, 'test')",
            "CONFIRM_WRITE"
        )
        
        # Verify the result
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].type == "text"
        assert "Write operation executed successfully" in result[0].text
        
        # Verify the methods were called correctly
        connection_server._get_sql_type.assert_called_once_with("INSERT INTO users VALUES (1, 'test')")
        connection_server._extract_table_name.assert_called_once_with("INSERT INTO users VALUES (1, 'test')")
        connection_server._get_config_or_raise.assert_called_once_with("test_conn")
        connection_server._check_write_permission.assert_called_once_with("test_conn", "users", "INSERT")
        connection_server.get_handler.assert_called_once_with("test_conn")
        mock_handler.__aenter__.return_value.execute_write_query.assert_called_once_with(
            "INSERT INTO users VALUES (1, 'test')"
        )

    @pytest.mark.asyncio
    async def test_handle_execute_write_error(self, connection_server):
        """Test _handle_execute_write method with error"""
        # Mock required methods
        connection_server._get_sql_type = MagicMock(return_value="UPDATE")
        connection_server._extract_table_name = MagicMock(return_value="users")
        connection_server._get_config_or_raise = MagicMock(return_value={
            "type": "mysql",
            "host": "localhost",
            "port": 3306,
            "database": "test",
            "user": "test",
            "password": "test",
            "writable": True
        })
        connection_server._check_write_permission = AsyncMock()
        
        # Mock get_handler to return a handler that raises an exception
        mock_handler = AsyncMock()
        mock_handler.__aenter__.return_value.execute_write_query.side_effect = ConnectionHandlerError("Database error")
        connection_server.get_handler = MagicMock(return_value=mock_handler)
        
        # Test with error
        with pytest.raises(ConnectionHandlerError, match="Database error"):
            await connection_server._handle_execute_write(
                "test_conn", 
                "UPDATE users SET name = 'test' WHERE id = 1",
                "CONFIRM_WRITE"
            )
        
        # Verify the methods were called correctly
        connection_server._get_sql_type.assert_called_once_with("UPDATE users SET name = 'test' WHERE id = 1")
        connection_server._extract_table_name.assert_called_once_with("UPDATE users SET name = 'test' WHERE id = 1")
        connection_server._get_config_or_raise.assert_called_once_with("test_conn")
        connection_server._check_write_permission.assert_called_once_with("test_conn", "users", "UPDATE")
        connection_server.get_handler.assert_called_once_with("test_conn")
        mock_handler.__aenter__.return_value.execute_write_query.assert_called_once_with(
            "UPDATE users SET name = 'test' WHERE id = 1"
        )

    @pytest.mark.asyncio
    async def test_handle_get_audit_logs(self, connection_server):
        """Test _handle_get_audit_logs method"""
        # Mock get_logs and format_logs functions
        with patch("mcp_dbutils.base.get_logs") as mock_get_logs, \
             patch("mcp_dbutils.base.format_logs") as mock_format_logs:
            mock_get_logs.return_value = [
                {
                    "timestamp": "2023-01-01T12:00:00",
                    "connection_name": "test_conn",
                    "table_name": "users",
                    "operation_type": "INSERT",
                    "sql_statement": "INSERT INTO users VALUES (?)",
                    "affected_rows": 1,
                    "status": "SUCCESS",
                    "execution_time": 10.5
                }
            ]
            mock_format_logs.return_value = "Formatted audit logs"
            
            # Test with all parameters
            result = await connection_server._handle_get_audit_logs(
                "test_conn", 
                "users",
                "INSERT",
                "SUCCESS",
                10
            )
            
            # Verify the result
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].type == "text"
            assert "Formatted audit logs" in result[0].text
            
            # Verify get_logs was called correctly
            mock_get_logs.assert_called_once_with(
                connection_name="test_conn",
                table_name="users",
                operation_type="INSERT",
                status="SUCCESS",
                limit=10
            )
            
            # Verify format_logs was called correctly
            mock_format_logs.assert_called_once_with(mock_get_logs.return_value)
            
            # Test with minimal parameters
            mock_get_logs.reset_mock()
            mock_format_logs.reset_mock()
            
            result = await connection_server._handle_get_audit_logs("test_conn", "", "", "", 100)
            
            # Verify get_logs was called correctly
            mock_get_logs.assert_called_once_with(
                connection_name="test_conn",
                table_name="",
                operation_type="",
                status="",
                limit=100
            )

    @pytest.mark.asyncio
    async def test_handle_get_audit_logs_error(self, connection_server):
        """Test _handle_get_audit_logs method with error"""
        # Mock get_logs to raise an exception
        with patch("mcp_dbutils.base.get_logs", side_effect=ValueError("Test error")):
            # Test with error
            with pytest.raises(ValueError, match="Test error"):
                await connection_server._handle_get_audit_logs("test_conn", "users", "INSERT", "SUCCESS", 10)

    @pytest.mark.asyncio
    async def test_handle_call_tool_execute_write(self, connection_server):
        """Test call_tool handler with dbutils-execute-write tool"""
        # Mock the _handle_execute_write method
        connection_server._handle_execute_write = AsyncMock(return_value=[
            TextContent(type="text", text="Write operation executed successfully")
        ])
        
        # Create a mock call_tool handler function
        async def mock_handle_call_tool(name, arguments):
            if name == "dbutils-execute-write":
                connection = arguments.get("connection", "")
                sql = arguments.get("sql", "").strip()
                confirmation = arguments.get("confirmation", "").strip()
                return await connection_server._handle_execute_write(connection, sql, confirmation)
            else:
                raise ValueError(f"Unknown tool: {name}")
        
        # Test with execute-write tool
        result = await mock_handle_call_tool("dbutils-execute-write", {
            "connection": "test_conn", 
            "sql": "INSERT INTO users (name) VALUES ('Test User')",
            "confirmation": "CONFIRM_WRITE"
        })
        
        # Verify the result
        assert result == [TextContent(type="text", text="Write operation executed successfully")]
        
        # Verify _handle_execute_write was called correctly
        connection_server._handle_execute_write.assert_called_once_with(
            "test_conn", 
            "INSERT INTO users (name) VALUES ('Test User')",
            "CONFIRM_WRITE"
        )

    @pytest.mark.asyncio
    async def test_handle_call_tool_get_audit_logs(self, connection_server):
        """Test call_tool handler with dbutils-get-audit-logs tool"""
        # Mock the _handle_get_audit_logs method
        connection_server._handle_get_audit_logs = AsyncMock(return_value=[
            TextContent(type="text", text="Audit logs")
        ])
        
        # Create a mock call_tool handler function
        async def mock_handle_call_tool(name, arguments):
            if name == "dbutils-get-audit-logs":
                connection = arguments.get("connection", "")
                table = arguments.get("table", "").strip()
                operation_type = arguments.get("operation_type", "").strip()
                status = arguments.get("status", "").strip()
                limit = arguments.get("limit", 100)
                return await connection_server._handle_get_audit_logs(connection, table, operation_type, status, limit)
            else:
                raise ValueError(f"Unknown tool: {name}")
        
        # Test with get-audit-logs tool
        result = await mock_handle_call_tool("dbutils-get-audit-logs", {
            "connection": "test_conn", 
            "table": "users",
            "operation_type": "INSERT",
            "status": "SUCCESS",
            "limit": 10
        })
        
        # Verify the result
        assert result == [TextContent(type="text", text="Audit logs")]
        
        # Verify _handle_get_audit_logs was called correctly
        connection_server._handle_get_audit_logs.assert_called_once_with(
            "test_conn", 
            "users",
            "INSERT",
            "SUCCESS",
            10
        )
