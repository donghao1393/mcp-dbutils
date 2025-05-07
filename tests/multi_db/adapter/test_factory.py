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
        # 创建一个真实的SQLConnection类的子类，而不是Mock
        class TestSQLConnection(SQLConnection):
            def __init__(self, config=None):
                self.db_type = "mysql"

        # 创建一个真实的SQLAdapter类的子类，而不是Mock
        class TestSQLAdapter:
            def __init__(self, connection):
                self.connection = connection

        factory = AdapterFactory()

        # 保存原始类
        original_class = factory.adapter_classes[SQLConnection]

        try:
            # 替换为测试类
            factory.adapter_classes[TestSQLConnection] = TestSQLAdapter

            # 创建连接
            connection = TestSQLConnection()

            # 测试
            adapter = factory.create_adapter(connection)

            assert isinstance(adapter, TestSQLAdapter)
            assert adapter.connection == connection
        finally:
            # 恢复原始类
            factory.adapter_classes[SQLConnection] = original_class
            # 删除测试类
            if TestSQLConnection in factory.adapter_classes:
                del factory.adapter_classes[TestSQLConnection]

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

        # 创建真实的类，而不是Mock
        class TestConnectionClass:
            pass

        class TestAdapterClass:
            pass

        factory.register_adapter_class(TestConnectionClass, TestAdapterClass)
        assert factory.adapter_classes[TestConnectionClass] == TestAdapterClass

    def test_get_supported_connection_types(self):
        """测试获取支持的连接类型"""
        factory = AdapterFactory()
        supported_types = factory.get_supported_connection_types()
        assert 'SQLConnection' in supported_types
