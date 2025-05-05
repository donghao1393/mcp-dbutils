"""
测试适配器基类

这个模块测试多数据库支持架构中的适配器基类。
"""

import pytest
from unittest.mock import Mock

from mcp_dbutils.multi_db.adapter.base import AdapterBase
from mcp_dbutils.multi_db.error.exceptions import DatabaseError


# 创建一个具体的AdapterBase子类用于测试
class TestAdapter(AdapterBase):
    """测试用的适配器类"""
    
    def execute_query(self, query, params=None):
        """执行查询"""
        return "query_result"
        
    def execute_write(self, query, params=None):
        """执行写操作"""
        return {"affected_rows": 1, "last_insert_id": 123}
        
    def list_resources(self):
        """列出资源"""
        return [{"name": "resource1"}, {"name": "resource2"}]
        
    def describe_resource(self, resource_name):
        """描述资源"""
        return {"name": resource_name, "columns": []}
        
    def get_resource_stats(self, resource_name):
        """获取资源统计信息"""
        return {"row_count": 100, "size": 1024}
        
    def extract_resource_name(self, query):
        """从查询中提取资源名"""
        return "resource_name"


class TestAdapterBase:
    """测试AdapterBase类"""
    
    def test_init(self):
        """测试初始化"""
        connection = Mock()
        adapter = TestAdapter(connection)
        assert adapter.connection == connection
        
    def test_execute_query(self):
        """测试执行查询"""
        connection = Mock()
        adapter = TestAdapter(connection)
        result = adapter.execute_query("SELECT 1")
        assert result == "query_result"
        
    def test_execute_write(self):
        """测试执行写操作"""
        connection = Mock()
        adapter = TestAdapter(connection)
        result = adapter.execute_write("INSERT INTO table VALUES (1)")
        assert result == {"affected_rows": 1, "last_insert_id": 123}
        
    def test_list_resources(self):
        """测试列出资源"""
        connection = Mock()
        adapter = TestAdapter(connection)
        result = adapter.list_resources()
        assert result == [{"name": "resource1"}, {"name": "resource2"}]
        
    def test_describe_resource(self):
        """测试描述资源"""
        connection = Mock()
        adapter = TestAdapter(connection)
        result = adapter.describe_resource("test_resource")
        assert result == {"name": "test_resource", "columns": []}
        
    def test_get_resource_stats(self):
        """测试获取资源统计信息"""
        connection = Mock()
        adapter = TestAdapter(connection)
        result = adapter.get_resource_stats("test_resource")
        assert result == {"row_count": 100, "size": 1024}
        
    def test_extract_resource_name(self):
        """测试从查询中提取资源名"""
        connection = Mock()
        adapter = TestAdapter(connection)
        result = adapter.extract_resource_name("SELECT * FROM table")
        assert result == "resource_name"
