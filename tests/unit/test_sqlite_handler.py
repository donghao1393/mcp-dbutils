"""Unit tests for SQLite connection handler"""

from unittest.mock import MagicMock, patch

import pytest
import sqlite3

from mcp_dbutils.base import ConnectionHandlerError
from mcp_dbutils.sqlite.handler import SQLiteHandler


class TestSQLiteHandler:
    """Test SQLite handler functionality with mocks"""

    @pytest.fixture
    def mock_cursor(self):
        """Create a mock cursor for SQLite"""
        cursor = MagicMock()
        cursor.fetchall.return_value = []
        cursor.fetchone.return_value = {}
        return cursor

    @pytest.fixture
    def mock_conn(self, mock_cursor):
        """Create a mock connection for SQLite"""
        conn = MagicMock()
        conn.cursor.return_value = mock_cursor
        conn.execute.return_value = mock_cursor
        return conn

    @pytest.fixture
    def handler(self):
        """Create a SQLite handler with mocks"""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', MagicMock()), \
             patch('yaml.safe_load', return_value={
                 'connections': {
                     'test_sqlite': {
                         'type': 'sqlite',
                         'path': '/path/to/test.db'
                     }
                 }
             }):
            handler = SQLiteHandler('config.yaml', 'test_sqlite')
            handler.log = MagicMock()
            handler.stats = MagicMock()
            return handler

    @pytest.mark.asyncio
    async def test_cleanup(self, handler):
        """Test cleanup method"""
        # Mock the handler.stats.to_dict method
        handler.stats.to_dict.return_value = {'queries': 10, 'errors': 0}
        
        # Call the method
        await handler.cleanup()
        
        # Verify log was called with the correct messages
        handler.log.assert_any_call('info', 'Final SQLite handler stats: {\'queries\': 10, \'errors\': 0}')
        handler.log.assert_any_call('debug', 'SQLite handler cleanup complete')
        
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
        handler.log.assert_any_call('info', 'Final SQLite handler stats: {\'queries\': 10, \'errors\': 0}')
        handler.log.assert_any_call('debug', 'Closing SQLite connection')
        handler.log.assert_any_call('debug', 'SQLite handler cleanup complete')
        
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
        handler.log.assert_any_call('info', 'Final SQLite handler stats: {\'queries\': 10, \'errors\': 0}')
        handler.log.assert_any_call('debug', 'Closing SQLite connection')
        handler.log.assert_any_call('warning', 'Error closing SQLite connection: Connection close error')
        handler.log.assert_any_call('debug', 'SQLite handler cleanup complete')
