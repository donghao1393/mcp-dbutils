"""Unit tests for base.py helper methods"""
import importlib
import json
import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import mcp.types as types
import pytest
import yaml

from mcp_dbutils.base import (
    ConfigurationError,
    ConnectionHandler,
    ConnectionServer,
)


class TestBaseHelpers:
    """Test helper methods in base.py"""
    
    @pytest.fixture
    def mock_config_yaml(self):
        """Mock configuration YAML content"""
        return """
        connections:
          test_sqlite:
            type: sqlite
            path: /path/to/test.db
          test_postgres:
            type: postgres
            host: localhost
            port: 5432
            database: test_db
            user: test_user
            password: test_password
          test_mysql:
            type: mysql
            host: localhost
            port: 3306
            database: test_db
            user: test_user
            password: test_password
          test_invalid:
            type: invalid_type
          test_missing_type:
            host: localhost
        """
    
    @pytest.fixture
    def server(self):
        """Create a connection server"""
        with patch('builtins.open', mock_open()):
            server = ConnectionServer("/path/to/config.yaml", debug=True)
            server.send_log = MagicMock()
            return server
    
    def test_get_config_or_raise_valid(self, server, mock_config_yaml):
        """Test _get_config_or_raise with valid input"""
        with patch('builtins.open', mock_open(read_data=mock_config_yaml)):
            result = server._get_config_or_raise("test_sqlite")
            assert result == {"type": "sqlite", "path": "/path/to/test.db"}
    
    def test_get_config_or_raise_invalid_yaml(self, server):
        """Test _get_config_or_raise with invalid YAML"""
        with patch('builtins.open', mock_open(read_data="invalid: yaml: content:")), pytest.raises(yaml.YAMLError):
            server._get_config_or_raise("test_connection")
    
    def test_get_config_or_raise_missing_connections(self, server):
        """Test _get_config_or_raise with missing connections section"""
        with patch('builtins.open', mock_open(read_data="other_section: value")), pytest.raises(ConfigurationError, match="must contain 'connections' section"):
            server._get_config_or_raise("test_connection")
    
    def test_get_config_or_raise_connection_not_found(self, server, mock_config_yaml):
        """Test _get_config_or_raise with non-existent connection"""
        with patch('builtins.open', mock_open(read_data=mock_config_yaml)), pytest.raises(ConfigurationError, match="Connection not found"):
            server._get_config_or_raise("nonexistent")
    
    def test_get_config_or_raise_missing_type(self, server, mock_config_yaml):
        """Test _get_config_or_raise with connection missing type field"""
        with patch('builtins.open', mock_open(read_data=mock_config_yaml)), pytest.raises(ConfigurationError, match="must include 'type' field"):
            server._get_config_or_raise("test_missing_type")

    @patch('mcp_dbutils.base.ConnectionServer._create_handler_for_type')
    @pytest.mark.asyncio
    async def test_get_handler_setup_session(self, mock_create_handler, server, mock_config_yaml):
        """Test get_handler sets session if available"""
        mock_handler = MagicMock()
        mock_handler.stats = MagicMock()
        mock_handler.cleanup = AsyncMock()
        mock_create_handler.return_value = mock_handler
        
        server.server = MagicMock()
        server.server.session = "test_session"
        
        with patch('builtins.open', mock_open(read_data=mock_config_yaml)):
            async with server.get_handler("test_sqlite") as handler:
                assert handler._session == "test_session"
                assert handler.stats.record_connection_start.called
        
        # Check cleanup is called
        assert mock_handler.stats.record_connection_end.called
        assert mock_handler.cleanup.called

    @patch('mcp_dbutils.sqlite.handler.SQLiteHandler')
    def test_create_handler_for_type_sqlite(self, mock_sqlite_handler, server):
        """Test _create_handler_for_type with SQLite"""
        mock_instance = MagicMock()
        mock_sqlite_handler.return_value = mock_instance
        
        result = server._create_handler_for_type('sqlite', 'test_connection')
        
        mock_sqlite_handler.assert_called_once_with(
            server.config_path, 'test_connection', server.debug
        )
        assert result == mock_instance
        assert server.send_log.called

    @patch('mcp_dbutils.postgres.handler.PostgreSQLHandler')
    def test_create_handler_for_type_postgres(self, mock_postgres_handler, server):
        """Test _create_handler_for_type with PostgreSQL"""
        mock_instance = MagicMock()
        mock_postgres_handler.return_value = mock_instance
        
        result = server._create_handler_for_type('postgres', 'test_connection')
        
        mock_postgres_handler.assert_called_once_with(
            server.config_path, 'test_connection', server.debug
        )
        assert result == mock_instance
        assert server.send_log.called

    @patch('mcp_dbutils.mysql.handler.MySQLHandler')
    def test_create_handler_for_type_mysql(self, mock_mysql_handler, server):
        """Test _create_handler_for_type with MySQL"""
        mock_instance = MagicMock()
        mock_mysql_handler.return_value = mock_instance
        
        result = server._create_handler_for_type('mysql', 'test_connection')
        
        mock_mysql_handler.assert_called_once_with(
            server.config_path, 'test_connection', server.debug
        )
        assert result == mock_instance
        assert server.send_log.called

    def test_create_handler_for_type_unsupported(self, server):
        """Test _create_handler_for_type with unsupported database type"""
        with pytest.raises(ConfigurationError, match="Unsupported database type"):
            server._create_handler_for_type('unsupported', 'test_connection')

    def test_import_error_handled(self, server):
        """Test ImportError is converted to ConfigurationError"""
        # 模拟导入错误
        original_import = __import__
        
        def mock_import_error(name, *args, **kwargs):
            if 'sqlite' in name:
                raise ImportError("Module not found")
            return original_import(name, *args, **kwargs)
            
        with patch('builtins.__import__', side_effect=mock_import_error), \
             patch('builtins.open', mock_open(read_data="""
            connections:
              test_connection:
                type: sqlite
                path: /path/to/db.sqlite
            """)), \
             pytest.raises(ConfigurationError, match="Failed to import"):
            server._create_handler_for_type('sqlite', 'test_connection')

    @pytest.mark.asyncio
    async def test_handle_list_tables(self, server):
        """Test _handle_list_tables helper method"""
        mock_handler = AsyncMock()
        mock_handler.db_type = "test_db"
        mock_handler.get_tables.return_value = [
            types.Resource(uri="test://table1", name="table1", description="Test Table 1"),
            types.Resource(uri="test://table2", name="table2")
        ]
        
        with patch.object(server, 'get_handler', return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_handler),
            __aexit__=AsyncMock()
        )):
            result = await server._handle_list_tables("test_connection")
            
        assert len(result) == 1
        assert result[0].type == "text"
        assert "[test_db]" in result[0].text
        assert "Table: table1" in result[0].text
        assert "Table: table2" in result[0].text
        assert "Description: Test Table 1" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_list_tables_empty(self, server):
        """Test _handle_list_tables with empty table list"""
        mock_handler = AsyncMock()
        mock_handler.db_type = "test_db"
        mock_handler.get_tables.return_value = []
        
        with patch.object(server, 'get_handler', return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_handler),
            __aexit__=AsyncMock()
        )):
            result = await server._handle_list_tables("test_connection")
            
        assert len(result) == 1
        assert result[0].type == "text"
        assert "[test_db] No tables found" in result[0].text

    def test_get_optimization_suggestions(self, server):
        """Test _get_optimization_suggestions helper method"""
        # Test seq scan suggestion
        result = server._get_optimization_suggestions("seq scan on table", 0.2)
        assert len(result) == 1
        assert "Consider adding an index" in result[0]
        
        # Test hash join suggestion
        result = server._get_optimization_suggestions("hash join on tables", 0.6)
        assert len(result) > 0
        # 检查至少一条建议包含索引或优化连接相关内容
        assert any("index" in r.lower() or "join" in r.lower() for r in result)
        
        # Test slow query suggestion
        result = server._get_optimization_suggestions("normal plan", 0.6)
        assert len(result) > 0
        assert any("slow" in r.lower() or "optimiz" in r.lower() for r in result)
        
        # Test temporary tables suggestion
        result = server._get_optimization_suggestions("creates temporary table for", 0.1)
        assert len(result) > 0
        assert any("temporary" in r.lower() for r in result)
        
        # Test no suggestions
        result = server._get_optimization_suggestions("normal plan", 0.05)
        assert len(result) == 0
        
    @pytest.mark.asyncio
    async def test_handle_analyze_query(self, server):
        """Test _handle_analyze_query helper method"""
        # Mock a handler for testing
        mock_handler = AsyncMock()
        mock_handler.db_type = "test_db"
        mock_handler.explain_query.return_value = "Execution Plan Details"
        mock_handler.execute_query = AsyncMock()
        
        with patch.object(server, 'get_handler', return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_handler),
            __aexit__=AsyncMock()
        )), patch.object(server, '_get_optimization_suggestions', return_value=["- Test suggestion"]):
            # Test with a valid SQL query
            result = await server._handle_analyze_query("test_connection", "SELECT * FROM test")
            
            # Verify the handler methods were called
            mock_handler.explain_query.assert_called_once_with("SELECT * FROM test")
            mock_handler.execute_query.assert_called_once_with("SELECT * FROM test")
            
            # Check the result format
            assert len(result) == 1
            assert result[0].type == "text"
            assert "[test_db] Query Analysis" in result[0].text
            assert "SQL: SELECT * FROM test" in result[0].text
            assert "Execution Plan:" in result[0].text
            assert "Execution Plan Details" in result[0].text
            assert "Optimization Suggestions:" in result[0].text
            assert "- Test suggestion" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_analyze_query_empty_sql(self, server):
        """Test _handle_analyze_query with empty SQL"""
        with pytest.raises(ConfigurationError):
            await server._handle_analyze_query("test_connection", "")
            
    @pytest.mark.asyncio
    async def test_handle_analyze_query_non_select(self, server):
        """Test _handle_analyze_query with non-SELECT query"""
        # Mock a handler for testing
        mock_handler = AsyncMock()
        mock_handler.db_type = "test_db"
        mock_handler.explain_query.return_value = "Execution Plan Details"
        
        with patch.object(server, 'get_handler', return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_handler),
            __aexit__=AsyncMock()
        )), patch.object(server, '_get_optimization_suggestions', return_value=[]):
            # Test with INSERT query (should not call execute_query)
            result = await server._handle_analyze_query("test_connection", "INSERT INTO test VALUES (1, 2)")
            
            # Verify explain was called but execute was not
            mock_handler.explain_query.assert_called_once_with("INSERT INTO test VALUES (1, 2)")
            mock_handler.execute_query.assert_not_called()
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert "INSERT INTO test VALUES (1, 2)" in result[0].text
            
    @pytest.mark.asyncio
    async def test_handle_analyze_query_execution_error(self, server):
        """Test _handle_analyze_query with query execution error"""
        # Mock a handler for testing
        mock_handler = AsyncMock()
        mock_handler.db_type = "test_db"
        mock_handler.explain_query.return_value = "Execution Plan Details"
        mock_handler.execute_query.side_effect = Exception("Query execution failed")
        
        with patch.object(server, 'get_handler', return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_handler),
            __aexit__=AsyncMock()
        )), patch.object(server, '_get_optimization_suggestions', return_value=[]), \
             patch.object(server, 'send_log'):
            # Test with a SELECT query that fails during execution
            result = await server._handle_analyze_query("test_connection", "SELECT * FROM test")
            
            # We should still get a result with the execution plan
            assert len(result) == 1
            assert server.send_log.called
            assert "Execution Plan:" in result[0].text 