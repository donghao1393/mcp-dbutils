"""
测试连接工厂

这个模块测试多数据库支持架构中的连接工厂。
"""

import pytest
from unittest.mock import Mock, patch

from mcp_dbutils.multi_db.connection.factory import ConnectionFactory
from mcp_dbutils.multi_db.connection.sql import SQLConnection
from mcp_dbutils.multi_db.error.exceptions import ConfigurationError


class TestConnectionFactory:
    """测试ConnectionFactory类"""
    
    def test_init(self):
        """测试初始化"""
        factory = ConnectionFactory()
        assert 'mysql' in factory.connection_classes
        assert 'postgresql' in factory.connection_classes
        assert 'sqlite' in factory.connection_classes
        assert factory.connection_classes['mysql'] == SQLConnection
        
    @patch('mcp_dbutils.multi_db.connection.sql.SQLConnection')
    def test_create_connection_mysql(self, mock_sql_connection):
        """测试创建MySQL连接"""
        mock_instance = Mock()
        mock_sql_connection.return_value = mock_instance
        
        factory = ConnectionFactory()
        config = {"type": "mysql", "host": "localhost", "port": 3306}
        connection = factory.create_connection(config)
        
        mock_sql_connection.assert_called_once_with(config)
        assert connection == mock_instance
        
    @patch('mcp_dbutils.multi_db.connection.sql.SQLConnection')
    def test_create_connection_postgresql(self, mock_sql_connection):
        """测试创建PostgreSQL连接"""
        mock_instance = Mock()
        mock_sql_connection.return_value = mock_instance
        
        factory = ConnectionFactory()
        config = {"type": "postgresql", "host": "localhost", "port": 5432}
        connection = factory.create_connection(config)
        
        mock_sql_connection.assert_called_once_with(config)
        assert connection == mock_instance
        
    @patch('mcp_dbutils.multi_db.connection.sql.SQLConnection')
    def test_create_connection_sqlite(self, mock_sql_connection):
        """测试创建SQLite连接"""
        mock_instance = Mock()
        mock_sql_connection.return_value = mock_instance
        
        factory = ConnectionFactory()
        config = {"type": "sqlite", "database": ":memory:"}
        connection = factory.create_connection(config)
        
        mock_sql_connection.assert_called_once_with(config)
        assert connection == mock_instance
        
    def test_create_connection_no_config(self):
        """测试没有配置时创建连接"""
        factory = ConnectionFactory()
        with pytest.raises(ConfigurationError) as excinfo:
            factory.create_connection(None)
        assert "Connection configuration is required" in str(excinfo.value)
        
    def test_create_connection_no_type(self):
        """测试没有类型时创建连接"""
        factory = ConnectionFactory()
        with pytest.raises(ConfigurationError) as excinfo:
            factory.create_connection({})
        assert "Database type is required" in str(excinfo.value)
        
    def test_create_connection_unsupported_type(self):
        """测试不支持的类型时创建连接"""
        factory = ConnectionFactory()
        with pytest.raises(ConfigurationError) as excinfo:
            factory.create_connection({"type": "unsupported"})
        assert "Unsupported database type: unsupported" in str(excinfo.value)
        
    def test_register_connection_class(self):
        """测试注册连接类"""
        factory = ConnectionFactory()
        mock_class = Mock()
        factory.register_connection_class("custom", mock_class)
        assert factory.connection_classes["custom"] == mock_class
        
    def test_get_supported_types(self):
        """测试获取支持的类型"""
        factory = ConnectionFactory()
        supported_types = factory.get_supported_types()
        assert 'mysql' in supported_types
        assert 'postgresql' in supported_types
        assert 'sqlite' in supported_types
