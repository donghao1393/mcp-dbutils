"""
测试查询工厂

这个模块测试多数据库支持架构中的查询工厂。
"""

from unittest.mock import Mock

import pytest

from mcp_dbutils.multi_db.error.exceptions import ConfigurationError
from mcp_dbutils.multi_db.query.factory import QueryBuilderFactory
from mcp_dbutils.multi_db.query.sql import SQLQueryBuilder


class TestQueryBuilderFactory:
    """测试QueryBuilderFactory类"""

    def test_init(self):
        """测试初始化"""
        factory = QueryBuilderFactory()
        assert 'mysql' in factory.builder_classes
        assert 'postgresql' in factory.builder_classes
        assert 'sqlite' in factory.builder_classes
        assert factory.builder_classes['mysql'] == SQLQueryBuilder

    def test_create_query_builder_mysql(self):
        """测试创建MySQL查询构建器"""
        factory = QueryBuilderFactory()

        # 保存原始类
        original_class = factory.builder_classes['mysql']

        try:
            # 替换为Mock
            mock_class = Mock()
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            factory.builder_classes['mysql'] = mock_class

            # 测试
            builder = factory.create_query_builder("mysql")

            mock_class.assert_called_once_with("mysql")
            assert builder == mock_instance
        finally:
            # 恢复原始类
            factory.builder_classes['mysql'] = original_class

    def test_create_query_builder_postgresql(self):
        """测试创建PostgreSQL查询构建器"""
        factory = QueryBuilderFactory()

        # 保存原始类
        original_class = factory.builder_classes['postgresql']

        try:
            # 替换为Mock
            mock_class = Mock()
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            factory.builder_classes['postgresql'] = mock_class

            # 测试
            builder = factory.create_query_builder("postgresql")

            mock_class.assert_called_once_with("postgresql")
            assert builder == mock_instance
        finally:
            # 恢复原始类
            factory.builder_classes['postgresql'] = original_class

    def test_create_query_builder_sqlite(self):
        """测试创建SQLite查询构建器"""
        factory = QueryBuilderFactory()

        # 保存原始类
        original_class = factory.builder_classes['sqlite']

        try:
            # 替换为Mock
            mock_class = Mock()
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            factory.builder_classes['sqlite'] = mock_class

            # 测试
            builder = factory.create_query_builder("sqlite")

            mock_class.assert_called_once_with("sqlite")
            assert builder == mock_instance
        finally:
            # 恢复原始类
            factory.builder_classes['sqlite'] = original_class

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
