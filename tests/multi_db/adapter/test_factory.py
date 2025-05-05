"""
测试适配器工厂

这个模块测试多数据库支持架构中的适配器工厂。
"""

import pytest
from unittest.mock import Mock, patch

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
        
    @patch('mcp_dbutils.multi_db.adapter.sql.SQLAdapter')
    def test_create_adapter_sql(self, mock_sql_adapter):
        """测试创建SQL适配器"""
        mock_instance = Mock()
        mock_sql_adapter.return_value = mock_instance
        
        factory = AdapterFactory()
        connection = Mock(spec=SQLConnection)
        adapter = factory.create_adapter(connection)
        
        mock_sql_adapter.assert_called_once_with(connection)
        assert adapter == mock_instance
        
    def test_create_adapter_no_connection(self):
        """测试没有连接时创建适配器"""
        factory = AdapterFactory()
        with pytest.raises(ConfigurationError) as excinfo:
            factory.create_adapter(None)
        assert "Connection is required" in str(excinfo.value)
        
    def test_create_adapter_unsupported_type(self):
        """测试不支持的连接类型时创建适配器"""
        factory = AdapterFactory()
        connection = Mock()  # 不是SQLConnection的实例
        with pytest.raises(ConfigurationError) as excinfo:
            factory.create_adapter(connection)
        assert "Unsupported connection type" in str(excinfo.value)
        
    def test_register_adapter_class(self):
        """测试注册适配器类"""
        factory = AdapterFactory()
        connection_class = Mock()
        adapter_class = Mock()
        factory.register_adapter_class(connection_class, adapter_class)
        assert factory.adapter_classes[connection_class] == adapter_class
        
    def test_get_supported_connection_types(self):
        """测试获取支持的连接类型"""
        factory = AdapterFactory()
        supported_types = factory.get_supported_connection_types()
        assert 'SQLConnection' in supported_types
