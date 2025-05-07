"""
测试适配器工厂

这个模块测试多数据库支持架构中的适配器工厂。
"""

from unittest.mock import Mock

from mcp_dbutils.multi_db.adapter.factory import AdapterFactory
from mcp_dbutils.multi_db.adapter.sql import SQLAdapter
from mcp_dbutils.multi_db.connection.sql import SQLConnection
from mcp_dbutils.multi_db.error.exceptions import ConfigurationError


class TestAdapterFactory:
    """测试AdapterFactory类"""

    def test_init(self):
        """测试初始化"""
        factory = AdapterFactory()
        assert SQLConnection in factory.adapter_classes
        assert factory.adapter_classes[SQLConnection] == SQLAdapter

    def test_create_adapter_sql(self):
        """测试创建SQL适配器"""
        factory = AdapterFactory()

        # 保存原始类
        original_class = factory.adapter_classes[SQLConnection]

        try:
            # 替换为Mock
            mock_class = Mock()
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            factory.adapter_classes[SQLConnection] = mock_class

            # 创建一个带有db_type属性的Mock
            connection = Mock(spec=SQLConnection)
            connection.db_type = "mysql"

            # 测试
            adapter = factory.create_adapter(connection)

            mock_class.assert_called_once_with(connection)
            assert adapter == mock_instance
        finally:
            # 恢复原始类
            factory.adapter_classes[SQLConnection] = original_class

    def test_create_adapter_no_connection(self):
        """测试没有连接时创建适配器"""
        factory = AdapterFactory()
        try:
            factory.create_adapter(None)
            raise AssertionError("应该抛出ConfigurationError异常")
        except ConfigurationError as e:
            assert "Connection is required" in str(e)

    def test_create_adapter_unsupported_type(self):
        """测试不支持的连接类型时创建适配器"""
        factory = AdapterFactory()
        connection = Mock()  # 不是SQLConnection的实例
        try:
            factory.create_adapter(connection)
            raise AssertionError("应该抛出ConfigurationError异常")
        except ConfigurationError as e:
            assert "Unsupported connection type" in str(e)

    def test_register_adapter_class(self):
        """测试注册适配器类"""
        factory = AdapterFactory()

        # 创建一个带有__name__属性的Mock
        connection_class = Mock()
        connection_class.__name__ = "MockConnection"

        adapter_class = Mock()
        factory.register_adapter_class(connection_class, adapter_class)
        assert factory.adapter_classes[connection_class] == adapter_class

    def test_get_supported_connection_types(self):
        """测试获取支持的连接类型"""
        factory = AdapterFactory()
        supported_types = factory.get_supported_connection_types()
        assert 'SQLConnection' in supported_types
