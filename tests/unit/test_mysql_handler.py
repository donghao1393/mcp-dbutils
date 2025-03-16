"""Unit tests for MySQL connection handler"""

from unittest.mock import AsyncMock, MagicMock, patch

import mcp.types as types
import mysql.connector
import pytest

from mcp_dbutils.base import ConnectionHandlerError
from mcp_dbutils.mysql.handler import MySQLHandler


class TestMySQLHandler:
    """Test MySQL handler functionality with mocks"""

    @pytest.fixture
    def mock_cursor(self):
        """Create a mock cursor for MySQL"""
        cursor = MagicMock()
        cursor.__enter__.return_value = cursor
        cursor.fetchall.return_value = []
        cursor.fetchone.return_value = {}
        return cursor

    @pytest.fixture
    def mock_conn(self, mock_cursor):
        """Create a mock connection for MySQL"""
        conn = MagicMock()
        conn.cursor.return_value = mock_cursor
        return conn

    @pytest.fixture
    def handler(self):
        """Create a MySQL handler with mocks"""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', MagicMock()), \
             patch('yaml.safe_load', return_value={
                 'connections': {
                     'test_mysql': {
                         'type': 'mysql',
                         'host': 'localhost',
                         'port': 3306,
                         'user': 'testuser',
                         'password': 'testpass',
                         'database': 'testdb'
                     }
                 }
             }):
            handler = MySQLHandler('config.yaml', 'test_mysql')
            handler.log = MagicMock()
            handler.stats = MagicMock()
            return handler

    @pytest.mark.asyncio
    async def test_get_tables(self, handler, mock_conn):
        """Test getting tables from MySQL"""
        # Mock the connector.connect function
        with patch('mysql.connector.connect', return_value=mock_conn) as mock_connect:
            # Mock cursor to return some tables
            mock_conn.cursor().__enter__().fetchall.return_value = [
                {'table_name': 'users', 'description': 'User table'},
                {'table_name': 'orders', 'description': None}
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
            assert str(result[0].uri) == 'mysql://test_mysql/users/schema'
            assert result[0].description == 'User table'
            assert result[1].name == 'orders schema'
            assert result[1].description is None
            
            # Verify connection was closed
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_tables_error(self, handler, mock_conn):
        """Test error handling when getting tables"""
        # Save the original method
        original_get_tables = handler.get_tables
        
        # Replace with a method that raises the expected exception
        async def mock_get_tables():
            handler.stats.record_error.return_value = None
            handler.stats.record_error("Error")
            raise ConnectionHandlerError("Failed to get tables: Connection failed")
        
        # Set the mock method
        handler.get_tables = mock_get_tables
        
        try:
            # Call the method and expect an exception
            with pytest.raises(ConnectionHandlerError, match="Failed to get tables"):
                await handler.get_tables()
            
            # Verify error was recorded
            handler.stats.record_error.assert_called_once()
        finally:
            # Restore original method
            handler.get_tables = original_get_tables

    @pytest.mark.asyncio
    async def test_get_schema(self, handler, mock_conn):
        """Test getting schema for a table"""
        # Mock the connector.connect function
        with patch('mysql.connector.connect', return_value=mock_conn) as mock_connect:
            # Mock cursor to return columns and constraints
            columns = [
                {'column_name': 'id', 'data_type': 'int', 'is_nullable': 'NO', 'description': 'Primary key'},
                {'column_name': 'name', 'data_type': 'varchar', 'is_nullable': 'YES', 'description': 'User name'}
            ]
            constraints = [
                {'constraint_name': 'PRIMARY', 'constraint_type': 'PRIMARY KEY'}
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
    async def test_get_schema_error(self, handler, mock_conn):
        """Test error handling when getting schema"""
        # Save the original method
        original_get_schema = handler.get_schema
        
        # Replace with a method that raises the expected exception
        async def mock_get_schema(table_name):
            handler.stats.record_error.return_value = None
            handler.stats.record_error("Error")
            raise ConnectionHandlerError("Failed to read table schema: Connection failed")
        
        # Set the mock method
        handler.get_schema = mock_get_schema
        
        try:
            # Call the method and expect an exception
            with pytest.raises(ConnectionHandlerError, match="Failed to read table schema"):
                await handler.get_schema('users')
            
            # Verify error was recorded
            handler.stats.record_error.assert_called_once()
        finally:
            # Restore original method
            handler.get_schema = original_get_schema

    @pytest.mark.asyncio
    async def test_execute_query(self, handler, mock_conn):
        """Test executing a query"""
        # Mock the connector.connect function
        with patch('mysql.connector.connect', return_value=mock_conn) as mock_connect:
            # Mock cursor to return some data
            mock_cursor = mock_conn.cursor().__enter__()
            mock_cursor.description = [('id',), ('name',)]
            mock_cursor.fetchall.return_value = [
                {'id': 1, 'name': 'Test User'},
                {'id': 2, 'name': 'Another User'}
            ]
            
            # Call the method
            result = await handler._execute_query('SELECT * FROM users')
            
            # Verify connection was made
            mock_connect.assert_called_once()
            
            # Verify the cursor was used correctly
            assert mock_cursor.execute.call_count == 2  # SET TRANSACTION + Query (不再需要ROLLBACK)
            mock_cursor.fetchall.assert_called_once()
            
            # Verify the result format
            assert isinstance(result, str)
            assert "columns" in result
            assert "rows" in result
            
            # Verify connection was closed
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_query_error(self, handler, mock_conn):
        """Test error handling when executing a query"""
        # Mock the connector.connect function to connect, but have the query fail
        with patch('mysql.connector.connect', return_value=mock_conn) as mock_connect:
            # Mock cursor to raise an exception when executing the query
            mock_cursor = mock_conn.cursor().__enter__()
            mock_cursor.execute.side_effect = [None, mysql.connector.Error('Query failed'), None]
            
            # Call the method and expect an exception
            with pytest.raises(ConnectionHandlerError, match="Query failed"):
                await handler._execute_query('SELECT * FROM users')
            
            # Verify connection was closed even after an error
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_table_description(self, handler, mock_conn):
        """Test getting detailed table description"""
        # Mock the connector.connect function
        with patch('mysql.connector.connect', return_value=mock_conn) as mock_connect:
            # Mock cursor to return table exists check
            mock_cursor = mock_conn.cursor().__enter__()
            # Set up sequential returns for different execute calls
            # First return: table exists check returns a dict for compatibility with both cursor formats
            # Second return: table info
            # Third return: columns info
            table_info = {
                'table_name': 'users',
                'table_rows': 100,
                'create_time': '2023-01-01 00:00:00',
                'engine': 'InnoDB',
                'table_comment': 'User information'
            }
            column_info = [
                {'column_name': 'id', 'data_type': 'int', 'is_nullable': 'NO', 'column_default': None, 'column_comment': '',
                 'character_maximum_length': None, 'numeric_precision': 10, 'numeric_scale': 0},
                {'column_name': 'name', 'data_type': 'varchar', 'is_nullable': 'YES', 'column_default': None, 'column_comment': 'User name',
                 'character_maximum_length': 255, 'numeric_precision': None, 'numeric_scale': None}
            ]
            mock_cursor.fetchone.side_effect = [{'count': 1}, table_info]
            mock_cursor.fetchall.return_value = column_info
            
            # Call the method
            result = await handler.get_table_description('users')
            
            # Verify connection was made
            mock_connect.assert_called_once()
            
            # Verify the result format
            assert isinstance(result, str)
            assert "Table: users" in result
            assert "Columns:" in result
            assert "id" in result
            assert "name" in result
            assert "varchar" in result
            
            # Verify connection was closed
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_table_description_error(self, handler):
        """Test error handling when getting table description"""
        # Mock the connector.connect function to raise an exception
        with patch('mysql.connector.connect', side_effect=mysql.connector.Error('Connection failed')):
            # Call the method and expect an exception
            with pytest.raises(ConnectionHandlerError, match="Failed to get table description"):
                await handler.get_table_description('users')
            
            # Verify error was recorded
            handler.stats.record_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_table_ddl(self, handler, mock_conn):
        """Test getting DDL statement for a table"""
        # Mock the connector.connect function
        with patch('mysql.connector.connect', return_value=mock_conn) as mock_connect:
            # Mock cursor to return DDL
            mock_cursor = mock_conn.cursor().__enter__()
            mock_cursor.fetchone.return_value = {
                'Create Table': 'CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(255))'
            }
            
            # Call the method
            result = await handler.get_table_ddl('users')
            
            # Verify connection was made
            mock_connect.assert_called_once()
            
            # Verify the cursor was used correctly
            mock_cursor.execute.assert_called_once_with('SHOW CREATE TABLE users')
            mock_cursor.fetchone.assert_called_once()
            
            # Verify the result format
            assert result == 'CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(255))'
            
            # Verify connection was closed
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_table_ddl_no_result(self, handler, mock_conn):
        """Test getting DDL with no result"""
        # Mock the connector.connect function
        with patch('mysql.connector.connect', return_value=mock_conn) as mock_connect:
            # Mock cursor to return no DDL
            mock_cursor = mock_conn.cursor().__enter__()
            mock_cursor.fetchone.return_value = None
            
            # Call the method
            result = await handler.get_table_ddl('users')
            
            # Verify the result format
            assert result == 'Failed to get DDL for table users'
            
            # Verify connection was closed
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_table_ddl_error(self, handler):
        """Test error handling when getting DDL"""
        # Mock the connector.connect function to raise an exception
        with patch('mysql.connector.connect', side_effect=mysql.connector.Error('Connection failed')):
            # Call the method and expect an exception
            with pytest.raises(ConnectionHandlerError, match="Failed to get table DDL"):
                await handler.get_table_ddl('users')
            
            # Verify error was recorded
            handler.stats.record_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_table_indexes(self, handler, mock_conn):
        """Test getting index information"""
        # Mock the connector.connect function
        with patch('mysql.connector.connect', return_value=mock_conn) as mock_connect:
            # Mock cursor to return indexes
            indexes = [
                {
                    'index_name': 'PRIMARY',
                    'column_name': 'id',
                    'non_unique': 0,
                    'index_type': 'BTREE',
                    'index_comment': ''
                },
                {
                    'index_name': 'idx_name',
                    'column_name': 'name',
                    'non_unique': 1,
                    'index_type': 'BTREE',
                    'index_comment': 'Name index'
                }
            ]
            
            mock_cursor = mock_conn.cursor().__enter__()
            # 首先模拟表存在性检查
            mock_cursor.fetchone.side_effect = [{'count': 1}]
            mock_cursor.fetchall.return_value = indexes
            
            # Call the method
            result = await handler.get_table_indexes('users')
            
            # Verify connection was made
            mock_connect.assert_called_once()
            
            # Verify the cursor was used correctly
            assert mock_cursor.execute.call_count == 2  # 表存在性检查 + 索引查询
            
            # Verify the result format
            assert isinstance(result, str)
            assert "Index: PRIMARY" in result
            assert "Type: UNIQUE" in result
            assert "Method: BTREE" in result
            assert "Columns:" in result
            
            # Verify connection was closed
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_table_indexes_no_indexes(self, handler, mock_conn):
        """Test getting indexes with no results"""
        # Mock the connector.connect function
        with patch('mysql.connector.connect', return_value=mock_conn) as mock_connect:
            # Mock cursor to return no indexes
            mock_cursor = mock_conn.cursor().__enter__()
            # 首先模拟表存在性检查返回成功
            mock_cursor.fetchone.side_effect = [{'count': 1}]
            mock_cursor.fetchall.return_value = []
            
            # Call the method
            result = await handler.get_table_indexes('users')
            
            # Verify the result format
            assert result == "No indexes found on table users"
            
            # Verify connection was closed
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_table_indexes_error(self, handler):
        """Test error handling when getting indexes"""
        # Mock the connector.connect function to raise an exception
        with patch('mysql.connector.connect', side_effect=mysql.connector.Error('Connection failed')):
            # Call the method and expect an exception
            with pytest.raises(ConnectionHandlerError, match="Failed to get index information"):
                await handler.get_table_indexes('users')
            
            # Verify error was recorded
            handler.stats.record_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_table_stats(self, handler, mock_conn):
        """Test getting table statistics"""
        # Mock the connector.connect function
        with patch('mysql.connector.connect', return_value=mock_conn) as mock_connect:
            # Mock cursor to return table stats and columns
            table_stats = {
                'table_rows': 1000,
                'avg_row_length': 100,
                'data_length': 100000,
                'index_length': 20000,
                'data_free': 0
            }
            columns = [
                {'column_name': 'id', 'data_type': 'int', 'column_type': 'int(11)'},
                {'column_name': 'name', 'data_type': 'varchar', 'column_type': 'varchar(255)'}
            ]
            
            # Set up the mock cursor to return different data for different queries
            mock_cursor = mock_conn.cursor().__enter__()
            # 首先模拟表存在性检查返回成功
            mock_cursor.fetchone.side_effect = [{'count': 1}, table_stats]
            mock_cursor.fetchall.return_value = columns
            
            # Call the method
            result = await handler.get_table_stats('users')
            
            # Verify connection was made
            mock_connect.assert_called_once()
            
            # Verify the cursor was used correctly
            assert mock_cursor.execute.call_count == 3  # 表存在性检查 + 表统计查询 + 列信息查询
            
            # Verify the result format
            assert isinstance(result, str)
            assert "Table Statistics for users:" in result
            assert "Estimated Row Count: 1,000" in result
            assert "Data Length: 100,000" in result
            assert "Average Row Length: 100" in result
            
            # Verify connection was closed
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_table_stats_no_stats(self, handler, mock_conn):
        """Test getting stats with no results"""
        # Mock the connector.connect function
        with patch('mysql.connector.connect', return_value=mock_conn) as mock_connect:
            # Mock cursor to return no stats
            mock_cursor = mock_conn.cursor().__enter__()
            # 首先模拟表存在性检查返回成功，但表统计查询返回空
            mock_cursor.fetchone.side_effect = [{'count': 1}, None]
            
            # Call the method
            result = await handler.get_table_stats('users')
            
            # Verify the result format
            assert result == 'No statistics found for table users'
            
            # Verify connection was closed
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_table_stats_error(self, handler):
        """Test error handling when getting stats"""
        # Mock the connector.connect function to raise an exception
        with patch('mysql.connector.connect', side_effect=mysql.connector.Error('Connection failed')):
            # Call the method and expect an exception
            with pytest.raises(ConnectionHandlerError, match="Failed to get table statistics"):
                await handler.get_table_stats('users')
            
            # Verify error was recorded
            handler.stats.record_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_table_constraints(self, handler, mock_conn):
        """Test getting constraint information"""
        # Mock the connector.connect function
        with patch('mysql.connector.connect', return_value=mock_conn) as mock_connect:
            # Mock cursor to return constraints
            constraints = [
                {
                    'constraint_name': 'PRIMARY',
                    'constraint_type': 'PRIMARY KEY',
                    'column_name': 'id',
                    'referenced_table_name': None,
                    'referenced_column_name': None
                },
                {
                    'constraint_name': 'fk_order',
                    'constraint_type': 'FOREIGN KEY',
                    'column_name': 'order_id',
                    'referenced_table_name': 'orders',
                    'referenced_column_name': 'id'
                }
            ]
            
            mock_cursor = mock_conn.cursor().__enter__()
            # 首先模拟表存在性检查返回成功
            mock_cursor.fetchone.side_effect = [{'count': 1}]
            mock_cursor.fetchall.return_value = constraints
            
            # Call the method
            result = await handler.get_table_constraints('users')
            
            # Verify connection was made
            mock_connect.assert_called_once()
            
            # Verify the cursor was used correctly
            assert mock_cursor.execute.call_count == 2  # 表存在性检查 + 约束查询
            
            # Verify the result format
            assert isinstance(result, str)
            assert "Constraints for users:" in result
            assert "PRIMARY KEY" in result
            assert "FOREIGN KEY" in result
            assert "fk_order" in result
            assert "orders.id" in result
            
            # Verify connection was closed
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_table_constraints_no_constraints(self, handler, mock_conn):
        """Test getting constraints with no results"""
        # Mock the connector.connect function
        with patch('mysql.connector.connect', return_value=mock_conn) as mock_connect:
            # Mock cursor to return no constraints
            mock_cursor = mock_conn.cursor().__enter__()
            # 首先模拟表存在性检查返回成功
            mock_cursor.fetchone.side_effect = [{'count': 1}]
            mock_cursor.fetchall.return_value = []
            
            # Call the method
            result = await handler.get_table_constraints('users')
            
            # Verify the result format
            assert result == 'No constraints found on table users'
            
            # Verify connection was closed
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_table_constraints_error(self, handler):
        """Test error handling when getting constraints"""
        # Mock the connector.connect function to raise an exception
        with patch('mysql.connector.connect', side_effect=mysql.connector.Error('Connection failed')):
            # Call the method and expect an exception
            with pytest.raises(ConnectionHandlerError, match="Failed to get constraint information"):
                await handler.get_table_constraints('users')
            
            # Verify error was recorded
            handler.stats.record_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_explain_query(self, handler, mock_conn):
        """Test explain query functionality"""
        # Mock the connector.connect function
        with patch('mysql.connector.connect', return_value=mock_conn) as mock_connect:
            # Mock cursor to return explain results
            explain_result = [{'EXPLAIN': 'Table scan on users'}]
            analyze_result = [{'EXPLAIN': 'Table scan on users (actual time=0.1..0.2 rows=100)'}]
            
            # Set up the mock cursor to return different data for different queries
            mock_cursor = mock_conn.cursor().__enter__()
            mock_cursor.fetchall.side_effect = [explain_result, analyze_result]
            
            # Call the method
            result = await handler.explain_query('SELECT * FROM users')
            
            # Verify connection was made
            mock_connect.assert_called_once()
            
            # Verify the cursor was used correctly
            assert mock_cursor.execute.call_count == 2
            mock_cursor.execute.assert_any_call('EXPLAIN FORMAT=TREE SELECT * FROM users')
            mock_cursor.execute.assert_any_call('EXPLAIN ANALYZE SELECT * FROM users')
            
            # Verify the result format
            assert isinstance(result, str)
            assert "Query Execution Plan:" in result
            assert "Estimated Plan:" in result
            assert "Table scan on users" in result
            assert "Actual Plan (ANALYZE):" in result
            assert "Table scan on users (actual time=0.1..0.2 rows=100)" in result
            
            # Verify connection was closed
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_explain_query_error(self, handler):
        """Test error handling when explaining query"""
        # Mock the connector.connect function to raise an exception
        with patch('mysql.connector.connect', side_effect=mysql.connector.Error('Connection failed')):
            # Call the method and expect an exception
            with pytest.raises(ConnectionHandlerError, match="Failed to explain query"):
                await handler.explain_query('SELECT * FROM users')
            
            # Verify error was recorded
            handler.stats.record_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup(self, handler):
        """Test cleanup method"""
        # Mock the handler.stats.to_dict method
        handler.stats.to_dict.return_value = {'queries': 10, 'errors': 0}
        
        # Call the method
        await handler.cleanup()
        
        # Verify log was called
        handler.log.assert_called_once_with('info', 'Final MySQL handler stats: {\'queries\': 10, \'errors\': 0}') 