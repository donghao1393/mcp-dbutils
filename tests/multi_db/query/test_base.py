"""
测试查询基类

这个模块测试多数据库支持架构中的查询基类。
"""

import pytest
from unittest.mock import Mock

from mcp_dbutils.multi_db.query.base import Query, QueryBuilder


# 创建一个具体的Query子类用于测试
class TestQuery(Query):
    """测试用的查询类"""
    
    def __init__(self, query_string, params=None):
        self.query_string = query_string
        self.params = params or {}
        
    def get_query_string(self):
        """获取查询字符串"""
        return self.query_string
        
    def get_params(self):
        """获取查询参数"""
        return self.params


# 创建一个具体的QueryBuilder子类用于测试
class TestQueryBuilder(QueryBuilder):
    """测试用的查询构建器类"""
    
    def __init__(self):
        self.resource_name = None
        self.fields = None
        self.data = None
        self.condition = None
        self.order_fields = None
        self.limit_count = None
        self.offset_count = None
        
    def select(self, resource_name, fields=None):
        """构建选择查询"""
        self.resource_name = resource_name
        self.fields = fields
        return self
        
    def insert(self, resource_name, data):
        """构建插入查询"""
        self.resource_name = resource_name
        self.data = data
        return self
        
    def update(self, resource_name, data, condition=None):
        """构建更新查询"""
        self.resource_name = resource_name
        self.data = data
        self.condition = condition
        return self
        
    def delete(self, resource_name, condition=None):
        """构建删除查询"""
        self.resource_name = resource_name
        self.condition = condition
        return self
        
    def where(self, condition):
        """添加条件"""
        self.condition = condition
        return self
        
    def order_by(self, fields):
        """添加排序"""
        self.order_fields = fields
        return self
        
    def limit(self, count):
        """添加限制"""
        self.limit_count = count
        return self
        
    def offset(self, count):
        """添加偏移"""
        self.offset_count = count
        return self
        
    def build(self):
        """构建查询"""
        query_string = f"Query for {self.resource_name}"
        params = {}
        if self.data:
            params.update(self.data)
        if self.condition:
            params.update(self.condition)
        return TestQuery(query_string, params)


class TestQueryClass:
    """测试Query类"""
    
    def test_init(self):
        """测试初始化"""
        query = TestQuery("SELECT 1", {"param": "value"})
        assert query.get_query_string() == "SELECT 1"
        assert query.get_params() == {"param": "value"}
        
    def test_init_no_params(self):
        """测试没有参数的初始化"""
        query = TestQuery("SELECT 1")
        assert query.get_query_string() == "SELECT 1"
        assert query.get_params() == {}


class TestQueryBuilderClass:
    """测试QueryBuilder类"""
    
    def test_select(self):
        """测试构建选择查询"""
        builder = TestQueryBuilder()
        result = builder.select("test_table", ["field1", "field2"])
        assert result == builder
        assert builder.resource_name == "test_table"
        assert builder.fields == ["field1", "field2"]
        
    def test_insert(self):
        """测试构建插入查询"""
        builder = TestQueryBuilder()
        data = {"field1": "value1", "field2": "value2"}
        result = builder.insert("test_table", data)
        assert result == builder
        assert builder.resource_name == "test_table"
        assert builder.data == data
        
    def test_update(self):
        """测试构建更新查询"""
        builder = TestQueryBuilder()
        data = {"field1": "value1", "field2": "value2"}
        condition = {"id": 1}
        result = builder.update("test_table", data, condition)
        assert result == builder
        assert builder.resource_name == "test_table"
        assert builder.data == data
        assert builder.condition == condition
        
    def test_delete(self):
        """测试构建删除查询"""
        builder = TestQueryBuilder()
        condition = {"id": 1}
        result = builder.delete("test_table", condition)
        assert result == builder
        assert builder.resource_name == "test_table"
        assert builder.condition == condition
        
    def test_where(self):
        """测试添加条件"""
        builder = TestQueryBuilder()
        condition = {"field": "value"}
        result = builder.where(condition)
        assert result == builder
        assert builder.condition == condition
        
    def test_order_by(self):
        """测试添加排序"""
        builder = TestQueryBuilder()
        fields = ["field1", "field2"]
        result = builder.order_by(fields)
        assert result == builder
        assert builder.order_fields == fields
        
    def test_limit(self):
        """测试添加限制"""
        builder = TestQueryBuilder()
        result = builder.limit(10)
        assert result == builder
        assert builder.limit_count == 10
        
    def test_offset(self):
        """测试添加偏移"""
        builder = TestQueryBuilder()
        result = builder.offset(20)
        assert result == builder
        assert builder.offset_count == 20
        
    def test_build(self):
        """测试构建查询"""
        builder = TestQueryBuilder()
        builder.select("test_table", ["field1", "field2"])
        builder.where({"id": 1})
        query = builder.build()
        assert isinstance(query, TestQuery)
        assert query.get_query_string() == "Query for test_table"
        assert query.get_params() == {"id": 1}
