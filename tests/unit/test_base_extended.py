"""Extended tests for base module"""
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import mcp.types as types
import pytest
import yaml

from mcp_dbutils.base import (
    CONNECTION_NOT_WRITABLE_ERROR,
    UNSUPPORTED_WRITE_OPERATION_ERROR,
    WRITE_CONFIRMATION_REQUIRED_ERROR,
    WRITE_OPERATION_NOT_ALLOWED_ERROR,
    ConfigurationError,
    ConnectionHandler,
    ConnectionServer,
)


class TestConnectionServerExtended:
    """Extended tests for ConnectionServer class"""

    @pytest.fixture
    def config_file(self):
        """Create a temporary config file for testing"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            config = {
                "connections": {
                    "test_conn": {
                        "type": "sqlite",
                        "database": ":memory:",
                        "writable": True
                    },
                    "test_conn_readonly": {
                        "type": "sqlite",
                        "database": ":memory:",
                        "writable": False
                    },
                    "test_conn_with_permissions": {
                        "type": "sqlite",
                        "database": ":memory:",
                        "writable": True,
                        "write_permissions": {
                            "tables": {
                                "users": {
                                    "operations": ["INSERT", "UPDATE"]
                                },
                                "posts": {
                                    "operations": ["INSERT", "UPDATE", "DELETE"]
                                }
                            },
                            "default_policy": "read_only"
                        }
                    },
                    "test_conn_allow_all": {
                        "type": "sqlite",
                        "database": ":memory:",
                        "writable": True,
                        "write_permissions": {
                            "default_policy": "allow_all"
                        }
                    }
                }
            }
            yaml.dump(config, f)
            f.flush()
            yield f.name
        os.unlink(f.name)

    @pytest.fixture
    def server(self, config_file):
        """Create a ConnectionServer instance for testing"""
        server = ConnectionServer(config_file)
        server.send_log = MagicMock()
        return server

    @pytest.mark.asyncio
    async def test_check_write_permission_writable(self, server):
        """Test _check_write_permission with writable connection"""
        # Connection is writable and has no specific permissions
        # Method should return None (no exception) if permission is granted
        await server._check_write_permission("test_conn", "users", "INSERT")
        await server._check_write_permission("test_conn", "users", "UPDATE")
        await server._check_write_permission("test_conn", "users", "DELETE")

    @pytest.mark.asyncio
    async def test_check_write_permission_readonly(self, server):
        """Test _check_write_permission with readonly connection"""
        # Connection is not writable
        with pytest.raises(ConfigurationError, match=CONNECTION_NOT_WRITABLE_ERROR):
            await server._check_write_permission("test_conn_readonly", "users", "INSERT")

    @pytest.mark.asyncio
    async def test_check_write_permission_with_table_permissions(self, server):
        """Test _check_write_permission with table-specific permissions"""
        # Table 'users' allows INSERT and UPDATE but not DELETE
        await server._check_write_permission("test_conn_with_permissions", "users", "INSERT")
        await server._check_write_permission("test_conn_with_permissions", "users", "UPDATE")

        with pytest.raises(ConfigurationError) as excinfo:
            await server._check_write_permission("test_conn_with_permissions", "users", "DELETE")
        assert "No permission to perform DELETE operation on table users" in str(excinfo.value)

        # Table 'posts' allows all operations
        await server._check_write_permission("test_conn_with_permissions", "posts", "INSERT")
        await server._check_write_permission("test_conn_with_permissions", "posts", "UPDATE")
        await server._check_write_permission("test_conn_with_permissions", "posts", "DELETE")

        # Table 'unknown_table' is not explicitly configured, default policy is read_only
        with pytest.raises(ConfigurationError) as excinfo:
            await server._check_write_permission("test_conn_with_permissions", "unknown_table", "INSERT")
        assert "No permission to perform INSERT operation on table unknown_table" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_check_write_permission_allow_all(self, server):
        """Test _check_write_permission with allow_all default policy"""
        # Default policy is allow_all
        await server._check_write_permission("test_conn_allow_all", "any_table", "INSERT")
        await server._check_write_permission("test_conn_allow_all", "any_table", "UPDATE")
        await server._check_write_permission("test_conn_allow_all", "any_table", "DELETE")

    @pytest.mark.asyncio
    async def test_handle_execute_write_success(self, server):
        """Test _handle_execute_write with successful operation"""
        # Mock the handler
        mock_handler = AsyncMock()
        mock_handler.execute_write_query.return_value = "Write operation executed successfully. 1 row affected."

        # Mock the get_handler method to return an async context manager
        class AsyncContextManagerMock:
            async def __aenter__(self):
                return mock_handler

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None

        server.get_handler = MagicMock(return_value=AsyncContextManagerMock())

        # Mock the _check_write_permission method
        server._check_write_permission = AsyncMock()

        result = await server._handle_execute_write(
            connection="test_conn",
            sql="INSERT INTO users (name) VALUES ('test')",
            confirmation="CONFIRM_WRITE"
        )

        # Verify handler was called
        server.get_handler.assert_called_once_with("test_conn")
        server._check_write_permission.assert_called_once_with("test_conn", "USERS", "INSERT")
        mock_handler.execute_write_query.assert_called_once_with("INSERT INTO users (name) VALUES ('test')")

        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Write operation executed successfully" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_execute_write_no_confirmation(self, server):
        """Test _handle_execute_write without confirmation"""
        with pytest.raises(ConfigurationError, match=WRITE_CONFIRMATION_REQUIRED_ERROR):
            await server._handle_execute_write(
                connection="test_conn",
                sql="INSERT INTO users (name) VALUES ('test')",
                confirmation=""
            )

    @pytest.mark.asyncio
    async def test_handle_execute_write_invalid_confirmation(self, server):
        """Test _handle_execute_write with invalid confirmation"""
        with pytest.raises(ConfigurationError, match=WRITE_CONFIRMATION_REQUIRED_ERROR):
            await server._handle_execute_write(
                connection="test_conn",
                sql="INSERT INTO users (name) VALUES ('test')",
                confirmation="WRONG_CONFIRMATION"
            )

    @pytest.mark.asyncio
    async def test_handle_execute_write_unsupported_operation(self, server):
        """Test _handle_execute_write with unsupported operation"""
        with pytest.raises(ConfigurationError, match=UNSUPPORTED_WRITE_OPERATION_ERROR.format(operation="SELECT")):
            await server._handle_execute_write(
                connection="test_conn",
                sql="SELECT * FROM users",
                confirmation="CONFIRM_WRITE"
            )

    @pytest.mark.asyncio
    async def test_handle_execute_write_no_permission(self, server):
        """Test _handle_execute_write without permission"""
        # Mock the _check_write_permission method to raise error
        server._check_write_permission = AsyncMock(
            side_effect=ConfigurationError(WRITE_OPERATION_NOT_ALLOWED_ERROR.format(
                operation="DELETE", table="users"
            ))
        )

        with pytest.raises(ConfigurationError, match="No permission to perform DELETE operation on table users"):
            await server._handle_execute_write(
                connection="test_conn_with_permissions",
                sql="DELETE FROM users WHERE id = 1",
                confirmation="CONFIRM_WRITE"
            )

    @pytest.mark.asyncio
    async def test_handle_execute_write_execution_error(self, server):
        """Test _handle_execute_write with execution error"""
        # Mock the handler
        mock_handler = AsyncMock()
        mock_handler.execute_write_query.side_effect = Exception("Execution error")

        # Mock the get_handler method to return an async context manager
        class AsyncContextManagerMock:
            async def __aenter__(self):
                return mock_handler

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None

        server.get_handler = MagicMock(return_value=AsyncContextManagerMock())

        # Mock the _check_write_permission method
        server._check_write_permission = AsyncMock()

        with pytest.raises(Exception, match="Execution error"):
            await server._handle_execute_write(
                connection="test_conn",
                sql="INSERT INTO users (name) VALUES ('test')",
                confirmation="CONFIRM_WRITE"
            )

        # No need to verify result as we're expecting an exception

    def test_get_sql_type(self, server):
        """Test _get_sql_type method"""
        # Test SELECT statement
        assert server._get_sql_type("SELECT * FROM users") == "SELECT"
        assert server._get_sql_type("  SELECT  * FROM users") == "SELECT"
        assert server._get_sql_type("select * from users") == "SELECT"

        # Test INSERT statement
        assert server._get_sql_type("INSERT INTO users VALUES (1, 'test')") == "INSERT"
        assert server._get_sql_type("insert into users values (1, 'test')") == "INSERT"

        # Test UPDATE statement
        assert server._get_sql_type("UPDATE users SET name = 'test' WHERE id = 1") == "UPDATE"
        assert server._get_sql_type("update users set name = 'test' where id = 1") == "UPDATE"

        # Test DELETE statement
        assert server._get_sql_type("DELETE FROM users WHERE id = 1") == "DELETE"
        assert server._get_sql_type("delete from users where id = 1") == "DELETE"

        # Test CREATE statement
        assert server._get_sql_type("CREATE TABLE users (id INT, name TEXT)") == "CREATE"
        assert server._get_sql_type("create table users (id int, name text)") == "CREATE"

        # Test ALTER statement
        assert server._get_sql_type("ALTER TABLE users ADD COLUMN email TEXT") == "ALTER"
        assert server._get_sql_type("alter table users add column email text") == "ALTER"

        # Test DROP statement
        assert server._get_sql_type("DROP TABLE users") == "DROP"
        assert server._get_sql_type("drop table users") == "DROP"

        # Test TRUNCATE statement
        assert server._get_sql_type("TRUNCATE TABLE users") == "TRUNCATE"
        assert server._get_sql_type("truncate table users") == "TRUNCATE"

        # Test transaction statements
        assert server._get_sql_type("BEGIN TRANSACTION") == "TRANSACTION_START"
        assert server._get_sql_type("START TRANSACTION") == "TRANSACTION_START"
        assert server._get_sql_type("COMMIT") == "TRANSACTION_COMMIT"
        assert server._get_sql_type("ROLLBACK") == "TRANSACTION_ROLLBACK"

        # Test unknown statement
        assert server._get_sql_type("UNKNOWN STATEMENT") == "UNKNOWN"
        assert server._get_sql_type("") == "UNKNOWN"

    def test_extract_table_name(self, server):
        """Test _extract_table_name method"""
        # Test INSERT statement
        assert server._extract_table_name("INSERT INTO users VALUES (1, 'test')").lower() == "users"
        assert server._extract_table_name("INSERT INTO public.users VALUES (1, 'test')").lower() == "public.users"

        # Test UPDATE statement
        assert server._extract_table_name("UPDATE users SET name = 'test' WHERE id = 1").lower() == "users"
        assert server._extract_table_name("UPDATE public.users SET name = 'test' WHERE id = 1").lower() == "public.users"

        # Test DELETE statement
        assert server._extract_table_name("DELETE FROM users WHERE id = 1").lower() == "users"
        assert server._extract_table_name("DELETE FROM public.users WHERE id = 1").lower() == "public.users"

        # Test with quoted table name
        assert server._extract_table_name('INSERT INTO "users" VALUES (1, \'test\')').lower() == "users"
        assert server._extract_table_name("INSERT INTO `users` VALUES (1, 'test')").lower() == "users"
        assert server._extract_table_name("INSERT INTO [users] VALUES (1, 'test')").lower() == "users"

        # Test unknown statement
        assert server._extract_table_name("UNKNOWN STATEMENT") == "unknown_table"


class TestConnectionHandlerExtended:
    """Extended tests for ConnectionHandler class"""

    class MockHandler(ConnectionHandler):
        """Mock implementation of ConnectionHandler for testing"""

        @property
        def db_type(self) -> str:
            return "mock"

        async def get_tables(self) -> list[types.Resource]:
            return []

        async def get_schema(self, table_name: str) -> str:
            return "{}"

        async def _execute_query(self, sql: str) -> str:
            return "Query executed"

        async def _execute_write_query(self, sql: str) -> str:
            return "Write operation executed successfully. 1 row affected."

        async def get_table_description(self, table_name: str) -> str:
            return f"Description of {table_name}"

        async def get_table_ddl(self, table_name: str) -> str:
            return f"DDL for {table_name}"

        async def get_table_indexes(self, table_name: str) -> str:
            return f"Indexes for {table_name}"

        async def get_table_stats(self, table_name: str) -> str:
            return f"Stats for {table_name}"

        async def get_table_constraints(self, table_name: str) -> str:
            return f"Constraints for {table_name}"

        async def explain_query(self, sql: str) -> str:
            return f"Explanation for {sql}"

        async def test_connection(self) -> bool:
            return True

        async def cleanup(self):
            pass

    @pytest.fixture
    def config_file(self):
        """Create a temporary config file for testing"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            config = {
                "connections": {
                    "test_conn": {
                        "type": "mock",
                        "database": ":memory:"
                    }
                }
            }
            yaml.dump(config, f)
            f.flush()
            yield f.name
        os.unlink(f.name)

    @pytest.fixture
    def handler(self, config_file):
        """Create a MockHandler instance for testing"""
        handler = self.MockHandler(config_file, "test_conn")
        handler.send_log = MagicMock()
        handler._session = MagicMock()
        return handler

    @pytest.mark.asyncio
    async def test_execute_query(self, handler):
        """Test execute_query method"""
        # Mock the _execute_query method
        handler._execute_query = AsyncMock(return_value="Query result")

        result = await handler.execute_query("SELECT * FROM users")

        # Verify _execute_query was called
        handler._execute_query.assert_called_once_with("SELECT * FROM users")

        # Verify result
        assert result == "Query result"

        # Verify stats were updated
        assert handler.stats.query_count == 1
        assert len(handler.stats.query_durations) == 1

    @pytest.mark.asyncio
    async def test_execute_query_error(self, handler):
        """Test execute_query method with error"""
        # Mock the _execute_query method to raise error
        handler._execute_query = AsyncMock(side_effect=Exception("Query error"))

        with pytest.raises(Exception, match="Query error"):
            await handler.execute_query("SELECT * FROM users")

        # Verify stats were updated
        assert handler.stats.query_count == 1
        assert handler.stats.error_count == 1
        assert "Exception" in handler.stats.error_types

    @pytest.mark.asyncio
    async def test_execute_write_query(self, handler):
        """Test execute_write_query method"""
        # Mock the _execute_write_query method
        handler._execute_write_query = AsyncMock(return_value="Write operation executed successfully. 1 row affected.")

        result = await handler.execute_write_query("INSERT INTO users (name) VALUES ('test')")

        # Verify _execute_write_query was called
        handler._execute_write_query.assert_called_once_with("INSERT INTO users (name) VALUES ('test')")

        # Verify result
        assert result == "Write operation executed successfully. 1 row affected."

        # Verify stats were updated
        assert handler.stats.query_count == 1
        assert len(handler.stats.query_durations) == 1

    @pytest.mark.asyncio
    async def test_execute_write_query_error(self, handler):
        """Test execute_write_query method with error"""
        # Mock the _execute_write_query method to raise error
        handler._execute_write_query = AsyncMock(side_effect=Exception("Write error"))

        with pytest.raises(Exception, match="Write error"):
            await handler.execute_write_query("INSERT INTO users (name) VALUES ('test')")

        # Verify stats were updated
        assert handler.stats.query_count == 1
        assert handler.stats.error_count == 1
        assert "Exception" in handler.stats.error_types

    @pytest.mark.asyncio
    async def test_execute_write_query_unsupported_operation(self, handler):
        """Test execute_write_query method with unsupported operation"""
        with pytest.raises(ValueError, match=UNSUPPORTED_WRITE_OPERATION_ERROR.format(operation="SELECT")):
            await handler.execute_write_query("SELECT * FROM users")

    @pytest.mark.asyncio
    async def test_execute_tool_query(self, handler):
        """Test execute_tool_query method"""
        # Mock the tool methods
        handler.get_table_description = AsyncMock(return_value="Table description")
        handler.get_table_ddl = AsyncMock(return_value="Table DDL")
        handler.get_table_indexes = AsyncMock(return_value="Table indexes")
        handler.get_table_stats = AsyncMock(return_value="Table stats")
        handler.get_table_constraints = AsyncMock(return_value="Table constraints")
        handler.explain_query = AsyncMock(return_value="Query explanation")

        # Test each tool
        result1 = await handler.execute_tool_query("dbutils-describe-table", table_name="users")
        assert result1 == "[mock]\nTable description"
        handler.get_table_description.assert_called_once_with("users")

        result2 = await handler.execute_tool_query("dbutils-get-ddl", table_name="users")
        assert result2 == "[mock]\nTable DDL"
        handler.get_table_ddl.assert_called_once_with("users")

        result3 = await handler.execute_tool_query("dbutils-list-indexes", table_name="users")
        assert result3 == "[mock]\nTable indexes"
        handler.get_table_indexes.assert_called_once_with("users")

        result4 = await handler.execute_tool_query("dbutils-get-stats", table_name="users")
        assert result4 == "[mock]\nTable stats"
        handler.get_table_stats.assert_called_once_with("users")

        result5 = await handler.execute_tool_query("dbutils-list-constraints", table_name="users")
        assert result5 == "[mock]\nTable constraints"
        handler.get_table_constraints.assert_called_once_with("users")

        result6 = await handler.execute_tool_query("dbutils-explain-query", sql="SELECT * FROM users")
        assert result6 == "[mock]\nQuery explanation"
        handler.explain_query.assert_called_once_with("SELECT * FROM users")

    @pytest.mark.asyncio
    async def test_execute_tool_query_unknown_tool(self, handler):
        """Test execute_tool_query method with unknown tool"""
        with pytest.raises(ValueError, match="Unknown tool"):
            await handler.execute_tool_query("unknown-tool")

    @pytest.mark.asyncio
    async def test_execute_tool_query_missing_sql(self, handler):
        """Test execute_tool_query method with missing SQL"""
        with pytest.raises(ValueError):
            await handler.execute_tool_query("dbutils-explain-query")

    @pytest.mark.asyncio
    async def test_execute_tool_query_error(self, handler):
        """Test execute_tool_query method with error"""
        # Mock the tool method to raise error
        handler.get_table_description = AsyncMock(side_effect=Exception("Tool error"))

        with pytest.raises(Exception, match="Tool error"):
            await handler.execute_tool_query("dbutils-describe-table", table_name="users")

        # Verify stats were updated
        assert handler.stats.error_count == 1
        assert "Exception" in handler.stats.error_types
