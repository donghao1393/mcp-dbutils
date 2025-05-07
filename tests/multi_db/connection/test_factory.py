"""
测试连接工厂

这个模块测试多数据库支持架构中的连接工厂。
"""

from unittest.mock import Mock

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

    def test_create_connection_mysql(self):
        """测试创建MySQL连接"""
        factory = ConnectionFactory()

        # 保存原始类
        original_class = factory.connection_classes['mysql']

        try:
            # 替换为Mock
            mock_class = Mock()
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            factory.connection_classes['mysql'] = mock_class

            # 测试
            config = {"type": "mysql", "host": "localhost", "port": 3306}
            connection = factory.create_connection(config)

            mock_class.assert_called_once_with(config)
            assert connection == mock_instance
        finally:
            # 恢复原始类
            factory.connection_classes['mysql'] = original_class

    def test_create_connection_postgresql(self):
        """测试创建PostgreSQL连接"""
        factory = ConnectionFactory()

        # 保存原始类
        original_class = factory.connection_classes['postgresql']

        try:
            # 替换为Mock
            mock_class = Mock()
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            factory.connection_classes['postgresql'] = mock_class

            # 测试
            config = {"type": "postgresql", "host": "localhost", "port": 5432}
            connection = factory.create_connection(config)

            mock_class.assert_called_once_with(config)
            assert connection == mock_instance
        finally:
            # 恢复原始类
            factory.connection_classes['postgresql'] = original_class

    def test_create_connection_sqlite(self):
        """测试创建SQLite连接"""
        factory = ConnectionFactory()

        # 保存原始类
        original_class = factory.connection_classes['sqlite']

        try:
            # 替换为Mock
            mock_class = Mock()
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            factory.connection_classes['sqlite'] = mock_class

            # 测试
            config = {"type": "sqlite", "database": ":memory:"}
            connection = factory.create_connection(config)

            mock_class.assert_called_once_with(config)
            assert connection == mock_instance
        finally:
            # 恢复原始类
            factory.connection_classes['sqlite'] = original_class

    def test_create_connection_no_config(self):
        """测试没有配置时创建连接"""
        factory = ConnectionFactory()
        try:
            factory.create_connection(None)
            assert False, "应该抛出ConfigurationError异常"
        except ConfigurationError as e:
            assert "Connection configuration is required" in str(e)

    def test_create_connection_no_type(self):
        """测试没有类型时创建连接"""
        factory = ConnectionFactory()
        try:
            factory.create_connection({})
            assert False, "应该抛出ConfigurationError异常"
        except ConfigurationError as e:
            assert "Database type is required" in str(e)

    def test_create_connection_unsupported_type(self):
        """测试不支持的类型时创建连接"""
        factory = ConnectionFactory()
        try:
            factory.create_connection({"type": "unsupported"})
            assert False, "应该抛出ConfigurationError异常"
        except ConfigurationError as e:
            assert "Unsupported database type: unsupported" in str(e)

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
