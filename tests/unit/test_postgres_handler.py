"""Unit tests for PostgreSQL connection handler"""

from unittest.mock import MagicMock, patch

import psycopg2
import pytest

from mcp_dbutils.base import ConnectionHandlerError
from mcp_dbutils.postgres.handler import PostgreSQLHandler


class TestPostgreSQLHandler:
    """Test PostgreSQL handler functionality with mocks"""

    @pytest.fixture
    def mock_cursor(self):
        """Create a mock cursor for PostgreSQL"""
        cursor = MagicMock()
        cursor.__enter__.return_value = cursor
        cursor.fetchall.return_value = []
        cursor.fetchone.return_value = {}
        return cursor

    @pytest.fixture
    def mock_conn(self, mock_cursor):
        """Create a mock connection for PostgreSQL"""
        conn = MagicMock()
        conn.cursor.return_value = mock_cursor
        return conn

    @pytest.fixture
    def handler(self):
        """Create a PostgreSQL handler with mocks"""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', MagicMock()), \
             patch('yaml.safe_load', return_value={
                 'connections': {
                     'test_postgres': {
                         'type': 'postgres',
                         'host': 'localhost',
                         'port': 5432,
                         'user': 'testuser',
                         'password': 'testpass',
                         'dbname': 'testdb'
                     }
                 }
             }):
            handler = PostgreSQLHandler('config.yaml', 'test_postgres')
            handler.log = MagicMock()
            handler.stats = MagicMock()
            return handler

    @pytest.mark.asyncio
    async def test_get_tables(self, handler, mock_conn):
        """Test getting tables from PostgreSQL"""
        # Mock the psycopg2.connect function
        with patch('psycopg2.connect', return_value=mock_conn) as mock_connect:
            # Mock cursor to return some tables
            mock_conn.cursor().__enter__().fetchall.return_value = [
                ('users', 'User table'),
                ('orders', None)
            ]

            # Call the method
            result = await handler.get_tables()

            # Verify connection was made with correct parameters
            mock_connect.assert_called_once()

            # Verify the cursor was used correctly
            mock_conn.cursor().__enter__().execute.assert_called_once()
            mock_conn.cursor().__enter__().fetchall.assert_called_once()

            # Verify the result format
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0].name == 'users schema'
            assert str(result[0].uri) == 'postgres://test_postgres/users/schema'
            assert result[0].description == 'User table'
            assert result[1].name == 'orders schema'
            assert result[1].description is None

            # Verify connection was closed
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_tables_error(self, handler):
        """Test error handling when getting tables with connection failure"""
        # Mock the psycopg2.connect function to raise an exception
        with patch('psycopg2.connect', side_effect=psycopg2.Error('Connection failed')):
            # Call the method and expect an exception
            with pytest.raises(ConnectionHandlerError, match="Failed to get constraint information"):
                await handler.get_tables()

            # Verify error was recorded
            handler.stats.record_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_schema(self, handler, mock_conn):
        """Test getting schema for a table"""
        # Mock the psycopg2.connect function
        with patch('psycopg2.connect', return_value=mock_conn) as mock_connect:
            # Mock cursor to return columns and constraints
            columns = [
                ('id', 'integer', 'NO', 'Primary key'),
                ('name', 'varchar', 'YES', 'User name')
            ]
            constraints = [
                ('pk_users', 'p')
            ]

            # Set up the mock cursor to return different data for different queries
            mock_cursor = mock_conn.cursor().__enter__()
            mock_cursor.fetchall.side_effect = [columns, constraints]

            # Call the method
            result = await handler.get_schema('users')

            # Verify connection was made with correct parameters
            mock_connect.assert_called_once()

            # Verify the cursor was used correctly for both queries
            assert mock_cursor.execute.call_count == 2

            # Verify the result format (it should be a string representation of dict)
            assert isinstance(result, str)
            assert "'columns':" in result
            assert "'constraints':" in result

            # Verify connection was closed
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_schema_error(self, handler):
        """Test error handling when getting schema with connection failure"""
        # Mock the psycopg2.connect function to raise an exception
        with patch('psycopg2.connect', side_effect=psycopg2.Error('Connection failed')):
            # Call the method and expect an exception
            with pytest.raises(ConnectionHandlerError, match="Failed to read table schema"):
                await handler.get_schema('users')

            # Verify error was recorded
            handler.stats.record_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_special_character_password(self):
        """Test handling of special characters in password"""
        # Create a handler with a password containing special characters
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', MagicMock()), \
             patch('yaml.safe_load', return_value={
                 'connections': {
                     'test_postgres': {
                         'type': 'postgres',
                         'host': 'localhost',
                         'port': 5432,
                         'user': 'testuser',
                         'password': 'test?pass!@#$%^&*()',  # Password with special characters
                         'dbname': 'testdb'
                     }
                 }
             }):
            special_handler = PostgreSQLHandler('config.yaml', 'test_postgres')
            special_handler.log = MagicMock()
            special_handler.stats = MagicMock()

            # Mock successful connection
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.__enter__.return_value = mock_cursor
            mock_cursor.fetchall.return_value = [
                ('users', 'User table')
            ]
            mock_conn.cursor.return_value = mock_cursor

            with patch('psycopg2.connect', return_value=mock_conn) as mock_connect:
                # Test get_tables method
                result = await special_handler.get_tables()

                # Verify connection was made with correct parameters including special character password
                mock_connect.assert_called_once()
                call_args = mock_connect.call_args[1]
                assert 'password' in call_args
                assert call_args['password'] == 'test?pass!@#$%^&*()'

                # Verify the result
                assert len(result) == 1
                assert result[0].name == 'users schema'

                # Verify connection was closed
                mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_special_character_password_connection_error(self):
        """Test error handling with special characters in password"""
        # Create a handler with a password containing special characters
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', MagicMock()), \
             patch('yaml.safe_load', return_value={
                 'connections': {
                     'test_postgres': {
                         'type': 'postgres',
                         'host': 'localhost',
                         'port': 5432,
                         'user': 'testuser',
                         'password': 'test?pass!@#$%^&*()',  # Password with special characters
                         'dbname': 'testdb'
                     }
                 }
             }):
            special_handler = PostgreSQLHandler('config.yaml', 'test_postgres')
            special_handler.log = MagicMock()
            special_handler.stats = MagicMock()

            # Mock connection failure
            with patch('psycopg2.connect', side_effect=psycopg2.Error('Connection failed')):
                # Test get_tables method with connection failure
                with pytest.raises(ConnectionHandlerError, match="Failed to get constraint information"):
                    await special_handler.get_tables()

                # Verify error was recorded
                special_handler.stats.record_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_variable_scope_handling(self):
        """Test proper handling of variable scope in connection methods"""
        # Create a handler
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', MagicMock()), \
             patch('yaml.safe_load', return_value={
                 'connections': {
                     'test_postgres': {
                         'type': 'postgres',
                         'host': 'localhost',
                         'port': 5432,
                         'user': 'testuser',
                         'password': 'testpass',
                         'dbname': 'testdb'
                     }
                 }
             }):
            handler = PostgreSQLHandler('config.yaml', 'test_postgres')
            handler.log = MagicMock()
            handler.stats = MagicMock()

            # Test all methods that use connection handling with try/finally blocks
            methods_to_test = [
                ('get_tables', []),
                ('get_schema', ['users']),
                ('get_table_description', ['users']),
                ('get_table_ddl', ['users']),
                ('get_table_indexes', ['users']),
                ('get_table_stats', ['users']),
                ('get_table_constraints', ['users']),
                ('explain_query', ['SELECT * FROM users'])
            ]

            for method_name, args in methods_to_test:
                # Mock connection failure
                with patch('psycopg2.connect', side_effect=psycopg2.Error('Connection failed')):
                    method = getattr(handler, method_name)

                    # Call the method and expect an exception
                    with pytest.raises(ConnectionHandlerError):
                        await method(*args)

                    # Verify error was recorded
                    handler.stats.record_error.assert_called()

    @pytest.mark.asyncio
    async def test_cleanup(self, handler):
        """Test cleanup method"""
        # Mock the handler.stats.to_dict method
        handler.stats.to_dict.return_value = {'queries': 10, 'errors': 0}

        # Call the method
        await handler.cleanup()

        # Verify log was called with the correct messages
        handler.log.assert_any_call('info', 'Final PostgreSQL handler stats: {\'queries\': 10, \'errors\': 0}')
        handler.log.assert_any_call('debug', 'PostgreSQL handler cleanup complete')

    @pytest.mark.asyncio
    async def test_cleanup_with_connection(self, handler):
        """Test cleanup method with active connection"""
        # Mock the handler.stats.to_dict method
        handler.stats.to_dict.return_value = {'queries': 10, 'errors': 0}

        # Mock connection
        mock_conn = MagicMock()
        handler._connection = mock_conn

        # Call the method
        await handler.cleanup()

        # Verify connection was closed
        mock_conn.close.assert_called_once()
        assert handler._connection is None

        # Verify logs
        handler.log.assert_any_call('info', 'Final PostgreSQL handler stats: {\'queries\': 10, \'errors\': 0}')
        handler.log.assert_any_call('debug', 'Closing PostgreSQL connection')
        handler.log.assert_any_call('debug', 'PostgreSQL handler cleanup complete')

    @pytest.mark.asyncio
    async def test_cleanup_with_connection_error(self, handler):
        """Test cleanup method with connection error"""
        # Mock the handler.stats.to_dict method
        handler.stats.to_dict.return_value = {'queries': 10, 'errors': 0}

        # Mock connection with error on close
        mock_conn = MagicMock()
        mock_conn.close.side_effect = Exception("Connection close error")
        handler._connection = mock_conn

        # Call the method
        await handler.cleanup()

        # Verify connection close was attempted
        mock_conn.close.assert_called_once()

        # Verify logs
        handler.log.assert_any_call('info', 'Final PostgreSQL handler stats: {\'queries\': 10, \'errors\': 0}')
        handler.log.assert_any_call('debug', 'Closing PostgreSQL connection')
        handler.log.assert_any_call('warning', 'Error closing PostgreSQL connection: Connection close error')
        handler.log.assert_any_call('debug', 'PostgreSQL handler cleanup complete')
