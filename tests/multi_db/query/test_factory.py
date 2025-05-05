"""
测试查询工厂

这个模块测试多数据库支持架构中的查询工厂。
"""

import pytest
from unittest.mock import Mock, patch

from mcp_dbutils.multi_db.query.factory import QueryBuilderFactory
from mcp_dbutils.multi_db.query.sql import SQLQueryBuilder
from mcp_dbutils.multi_db.error.exceptions import ConfigurationError


class TestQueryBuilderFactory:
    """测试QueryBuilderFactory类"""
    
    def test_init(self):
        """测试初始化"""
        factory = QueryBuilderFactory()
        assert 'mysql' in factory.builder_classes
        assert 'postgresql' in factory.builder_classes
        assert 'sqlite' in factory.builder_classes
        assert factory.builder_classes['mysql'] == SQLQueryBuilder
        
    @patch('mcp_dbutils.multi_db.query.sql.SQLQueryBuilder')
    def test_create_query_builder_mysql(self, mock_sql_builder):
        """测试创建MySQL查询构建器"""
        mock_instance = Mock()
        mock_sql_builder.return_value = mock_instance
        
        factory = QueryBuilderFactory()
        builder = factory.create_query_builder("mysql")
        
        mock_sql_builder.assert_called_once_with("mysql")
        assert builder == mock_instance
        
    @patch('mcp_dbutils.multi_db.query.sql.SQLQueryBuilder')
    def test_create_query_builder_postgresql(self, mock_sql_builder):
        """测试创建PostgreSQL查询构建器"""
        mock_instance = Mock()
        mock_sql_builder.return_value = mock_instance
        
        factory = QueryBuilderFactory()
        builder = factory.create_query_builder("postgresql")
        
        mock_sql_builder.assert_called_once_with("postgresql")
        assert builder == mock_instance
        
    @patch('mcp_dbutils.multi_db.query.sql.SQLQueryBuilder')
    def test_create_query_builder_sqlite(self, mock_sql_builder):
        """测试创建SQLite查询构建器"""
        mock_instance = Mock()
        mock_sql_builder.return_value = mock_instance
        
        factory = QueryBuilderFactory()
        builder = factory.create_query_builder("sqlite")
        
        mock_sql_builder.assert_called_once_with("sqlite")
        assert builder == mock_instance
        
    def test_create_query_builder_no_type(self):
        """测试没有类型时创建查询构建器"""
        factory = QueryBuilderFactory()
        with pytest.raises(ConfigurationError) as excinfo:
            factory.create_query_builder(None)
        assert "Database type is required" in str(excinfo.value)
        
    def test_create_query_builder_unsupported_type(self):
        """测试不支持的类型时创建查询构建器"""
        factory = QueryBuilderFactory()
        with pytest.raises(ConfigurationError) as excinfo:
            factory.create_query_builder("unsupported")
        assert "Unsupported database type: unsupported" in str(excinfo.value)
        
    def test_register_builder_class(self):
        """测试注册查询构建器类"""
        factory = QueryBuilderFactory()
        mock_class = Mock()
        factory.register_builder_class("custom", mock_class)
        assert factory.builder_classes["custom"] == mock_class
        
    def test_get_supported_types(self):
        """测试获取支持的类型"""
        factory = QueryBuilderFactory()
        supported_types = factory.get_supported_types()
        assert 'mysql' in supported_types
        assert 'postgresql' in supported_types
        assert 'sqlite' in supported_types
