"""
MongoDB适配器单元测试

这个模块包含MongoDB适配器的单元测试。
"""

import unittest
from unittest.mock import MagicMock, patch

import mcp.types as types

from mcp_dbutils.base import ConnectionHandlerError
from mcp_dbutils.mongo.adapted_handler import AdaptedMongoDBHandler


class TestMongoDBAdaptedHandler(unittest.TestCase):
    """MongoDB适配器单元测试类"""

    def setUp(self):
        """设置测试环境"""
        # 创建一个模拟的配置路径和连接名
        self.config_path = "test_config.yaml"
        self.connection = "test_mongodb"
        
        # 模拟配置加载
        self.config_mock = {
            'type': 'mongodb',
            'host': 'localhost',
            'port': 27017,
            'database': 'test_db',
            'username': 'test_user',
            'password': 'test_password',
            'auth_source': 'admin',
            'debug': True,
            'writable': True,
            'write_permissions': {'default_policy': 'deny_all', 'tables': {}}
        }
        
        # 创建MongoDB适配器
        with patch('mcp_dbutils.mongo.config.MongoDBConfig.from_yaml', return_value=MagicMock(
            host='localhost',
            port='27017',
            database='test_db',
            username='test_user',
            password='test_password',
            auth_source='admin',
            uri=None,
            debug=True,
            writable=True,
            write_permissions=None,
            to_dict=lambda: self.config_mock
        )):
            self.handler = AdaptedMongoDBHandler(self.config_path, self.connection, debug=True)
        
        # 模拟连接和适配器
        self.handler._connection = MagicMock()
        self.handler._adapter = MagicMock()
        self.handler._ensure_connection = MagicMock(return_value=(self.handler._connection, self.handler._adapter))

    def test_db_type(self):
        """测试数据库类型属性"""
        self.assertEqual(self.handler.db_type, 'mongodb')

    def test_load_config(self):
        """测试加载配置"""
        with patch('mcp_dbutils.mongo.config.MongoDBConfig.from_yaml', return_value=MagicMock(
            host='localhost',
            port='27017',
            database='test_db',
            username='test_user',
            password='test_password',
            auth_source='admin',
            uri=None,
            debug=True,
            writable=True,
            write_permissions=None,
            to_dict=lambda: self.config_mock
        )):
            config = self.handler._load_config()
            self.assertEqual(config['type'], 'mongodb')
            self.assertEqual(config['host'], 'localhost')
            self.assertEqual(config['port'], 27017)
            self.assertEqual(config['database'], 'test_db')
            self.assertEqual(config['username'], 'test_user')
            self.assertEqual(config['password'], 'test_password')
            self.assertEqual(config['auth_source'], 'admin')
            self.assertEqual(config['debug'], True)
            self.assertEqual(config['writable'], True)

    def test_get_tables(self):
        """测试获取集合列表"""
        # 模拟适配器的list_resources方法
        collections = [
            {'name': 'users', 'type': 'COLLECTION', 'count': 10, 'size': 1024},
            {'name': 'products', 'type': 'COLLECTION', 'count': 5, 'size': 512}
        ]
        self.handler._adapter.list_resources.return_value = collections
        
        # 执行测试
        result = self.handler.get_tables()
        
        # 验证结果
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, 'users schema')
        self.assertEqual(result[0].uri, 'mongodb://test_mongodb/users/schema')
        self.assertEqual(result[1].name, 'products schema')
        self.assertEqual(result[1].uri, 'mongodb://test_mongodb/products/schema')

    def test_get_schema(self):
        """测试获取集合结构"""
        # 模拟适配器的describe_resource方法
        collection_info = {
            'name': 'users',
            'type': 'COLLECTION',
            'fields': [
                {'name': '_id', 'type': 'ObjectId', 'sample_value': '60b9b4b9e6b3f3b3e8b4b4b9'},
                {'name': 'name', 'type': 'str', 'sample_value': 'John'}
            ],
            'indexes': [
                {'name': '_id_', 'unique': True, 'columns': ['_id'], 'directions': [1]}
            ]
        }
        self.handler._adapter.describe_resource.return_value = collection_info
        
        # 执行测试
        result = self.handler.get_schema('users')
        
        # 验证结果
        self.assertIn('name', result)
        self.assertIn('type', result)
        self.assertIn('fields', result)
        self.assertIn('indexes', result)

    def test_execute_query(self):
        """测试执行查询"""
        # 模拟适配器的execute_query方法
        query_result = [{'name': 'John', 'age': 25}]
        self.handler._adapter.execute_query.return_value = query_result
        
        # 执行测试
        result = self.handler._execute_query('{"operation": "find", "collection": "users", "filter": {"age": {"$gt": 18}}}')
        
        # 验证结果
        self.assertEqual(result, str(query_result))

    def test_execute_write_query(self):
        """测试执行写操作"""
        # 模拟适配器的execute_write方法
        write_result = {'inserted_id': '123'}
        self.handler._adapter.execute_write.return_value = write_result
        
        # 执行测试
        result = self.handler._execute_write_query('{"operation": "insert_one", "collection": "users", "document": {"name": "John", "age": 25}}')
        
        # 验证结果
        self.assertEqual(result, str(write_result))

    def test_get_table_description(self):
        """测试获取集合描述"""
        # 模拟适配器的describe_resource方法
        collection_info = {
            'name': 'users',
            'type': 'COLLECTION',
            'count': 10,
            'size': 1024,
            'avg_obj_size': 102.4,
            'storage_size': 2048,
            'index_size': 512,
            'total_size': 1536,
            'fields': [
                {'name': '_id', 'type': 'ObjectId', 'sample_value': '60b9b4b9e6b3f3b3e8b4b4b9'},
                {'name': 'name', 'type': 'str', 'sample_value': 'John'}
            ],
            'indexes': [
                {'name': '_id_', 'unique': True, 'columns': ['_id'], 'directions': [1]}
            ]
        }
        self.handler._adapter.describe_resource.return_value = collection_info
        
        # 执行测试
        result = self.handler.get_table_description('users')
        
        # 验证结果
        self.assertIn('Collection: users', result)
        self.assertIn('Document Count: 10', result)
        self.assertIn('_id (ObjectId)', result)
        self.assertIn('name (str)', result)
        self.assertIn('Index: _id_', result)


if __name__ == '__main__':
    unittest.main()
