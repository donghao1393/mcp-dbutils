"""
MongoDB适配器单元测试

这个模块包含MongoDB适配器的单元测试。
"""

import unittest
from unittest.mock import MagicMock, patch

from bson.objectid import ObjectId

from mcp_dbutils.multi_db.adapter.mongo import MongoAdapter
from mcp_dbutils.multi_db.connection.mongo import MongoConnection
from mcp_dbutils.multi_db.error.exceptions import (
    ConnectionError,
    DatabaseError,
    QueryError,
    ResourceNotFoundError,
)


class TestMongoAdapter(unittest.TestCase):
    """MongoDB适配器单元测试类"""

    def setUp(self):
        """设置测试环境"""
        # 创建一个模拟的MongoDB连接
        self.mock_connection = MagicMock(spec=MongoConnection)
        self.mock_connection.db = MagicMock()
        self.mock_connection.is_connected.return_value = True

        # 创建MongoDB适配器
        self.adapter = MongoAdapter(self.mock_connection)
        self.adapter.mongo_connection = self.mock_connection

    def test_execute_query_valid(self):
        """测试执行有效的查询"""
        # 准备测试数据
        query = {
            'operation': 'find',
            'collection': 'users',
            'filter': {'age': {'$gt': 18}}
        }
        expected_result = [{'name': 'John', 'age': 25}]

        # 设置模拟行为
        self.mock_connection.execute.return_value = expected_result

        # 执行测试
        result = self.adapter.execute_query(query)

        # 验证结果
        self.assertEqual(result, expected_result)
        self.mock_connection.execute.assert_called_once_with(query, None)

    def test_execute_query_invalid_operation(self):
        """测试执行无效的查询操作"""
        # 准备测试数据
        query = {
            'operation': 'insert_one',  # 这是一个写操作，不是读操作
            'collection': 'users',
            'document': {'name': 'John', 'age': 25}
        }

        # 执行测试并验证异常
        with self.assertRaises(QueryError) as context:
            self.adapter.execute_query(query)

        self.assertIn("not a read operation", str(context.exception))

    def test_execute_write_valid(self):
        """测试执行有效的写操作"""
        # 准备测试数据
        query = {
            'operation': 'insert_one',
            'collection': 'users',
            'document': {'name': 'John', 'age': 25}
        }
        expected_result = {'inserted_id': '123'}

        # 设置模拟行为
        self.mock_connection.execute.return_value = expected_result

        # 执行测试
        result = self.adapter.execute_write(query)

        # 验证结果
        self.assertEqual(result, expected_result)
        self.mock_connection.execute.assert_called_once_with(query, None)

    def test_execute_write_invalid_operation(self):
        """测试执行无效的写操作"""
        # 准备测试数据
        query = {
            'operation': 'find',  # 这是一个读操作，不是写操作
            'collection': 'users',
            'filter': {'age': {'$gt': 18}}
        }

        # 执行测试并验证异常
        with self.assertRaises(QueryError) as context:
            self.adapter.execute_write(query)

        self.assertIn("not a write operation", str(context.exception))

    def test_list_resources(self):
        """测试列出集合"""
        # 准备测试数据
        collections = ['users', 'products', 'orders']

        # 设置模拟行为
        self.mock_connection.db.list_collection_names.return_value = collections

        # 模拟_get_collection_stats方法
        self.adapter._get_collection_stats = MagicMock(return_value={
            'count': 10,
            'size': 1024
        })

        # 执行测试
        result = self.adapter.list_resources()

        # 验证结果
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['name'], 'users')
        self.assertEqual(result[0]['type'], 'COLLECTION')
        self.assertEqual(result[0]['count'], 10)
        self.assertEqual(result[0]['size'], 1024)

    def test_describe_resource_existing(self):
        """测试描述存在的集合"""
        # 准备测试数据
        resource_name = 'users'

        # 设置模拟行为
        self.adapter._resource_exists = MagicMock(return_value=True)
        self.adapter._get_collection_stats = MagicMock(return_value={
            'count': 10,
            'size': 1024,
            'avg_obj_size': 102.4,
            'storage_size': 2048,
            'index_size': 512,
            'total_size': 1536
        })
        self.adapter._get_indexes = MagicMock(return_value=[
            {'name': '_id_', 'unique': True, 'columns': ['_id'], 'directions': [1]}
        ])
        self.adapter._get_fields = MagicMock(return_value=[
            {'name': '_id', 'type': 'ObjectId', 'sample_value': '60b9b4b9e6b3f3b3e8b4b4b9'},
            {'name': 'name', 'type': 'str', 'sample_value': 'John'}
        ])

        # 执行测试
        result = self.adapter.describe_resource(resource_name)

        # 验证结果
        self.assertEqual(result['name'], resource_name)
        self.assertEqual(result['type'], 'COLLECTION')
        self.assertEqual(result['count'], 10)
        self.assertEqual(result['size'], 1024)
        self.assertEqual(len(result['indexes']), 1)
        self.assertEqual(len(result['fields']), 2)

    def test_describe_resource_nonexistent(self):
        """测试描述不存在的集合"""
        # 准备测试数据
        resource_name = 'nonexistent'

        # 设置模拟行为
        self.adapter._resource_exists = MagicMock(return_value=False)

        # 执行测试并验证异常
        with self.assertRaises(ResourceNotFoundError) as context:
            self.adapter.describe_resource(resource_name)

        self.assertIn("does not exist", str(context.exception))

    def test_get_resource_stats(self):
        """测试获取集合统计信息"""
        # 准备测试数据
        resource_name = 'users'

        # 设置模拟行为
        self.adapter._resource_exists = MagicMock(return_value=True)
        self.adapter._get_collection_stats = MagicMock(return_value={
            'count': 10,
            'size': 1024,
            'avg_obj_size': 102.4,
            'storage_size': 2048,
            'index_size': 512,
            'total_size': 1536
        })

        # 执行测试
        result = self.adapter.get_resource_stats(resource_name)

        # 验证结果
        self.assertEqual(result['count'], 10)
        self.assertEqual(result['size'], 1024)
        self.assertEqual(result['avg_obj_size'], 102.4)
        self.assertEqual(result['storage_size'], 2048)
        self.assertEqual(result['index_size'], 512)
        self.assertEqual(result['total_size'], 1536)

    def test_extract_resource_name(self):
        """测试从查询中提取集合名"""
        # 准备测试数据
        query = {
            'operation': 'find',
            'collection': 'users',
            'filter': {'age': {'$gt': 18}}
        }

        # 执行测试
        result = self.adapter.extract_resource_name(query)

        # 验证结果
        self.assertEqual(result, 'USERS')  # 应该返回大写的集合名


if __name__ == '__main__':
    unittest.main()