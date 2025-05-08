"""
Redis适配器单元测试

这个模块包含Redis适配器的单元测试。
"""

import unittest
from unittest.mock import MagicMock

from mcp_dbutils.multi_db.adapter.redis import RedisAdapter
from mcp_dbutils.multi_db.connection.redis import RedisConnection
from mcp_dbutils.multi_db.error.exceptions import (
    QueryError,
    ResourceNotFoundError,
)


class TestRedisAdapter(unittest.TestCase):
    """Redis适配器单元测试类"""

    def setUp(self):
        """设置测试环境"""
        # 创建一个模拟的Redis连接
        self.mock_connection = MagicMock(spec=RedisConnection)
        self.mock_connection.client = MagicMock()
        self.mock_connection.is_connected.return_value = True

        # 创建Redis适配器
        self.adapter = RedisAdapter(self.mock_connection)
        self.adapter.redis_connection = self.mock_connection

    def test_execute_query_valid(self):
        """测试执行有效的查询"""
        # 准备测试数据
        query = 'GET'
        params = ['user:1']
        expected_result = 'John'

        # 设置模拟行为
        self.mock_connection.execute.return_value = expected_result

        # 执行测试
        result = self.adapter.execute_query(query, params)

        # 验证结果
        self.assertEqual(result, expected_result)
        self.mock_connection.execute.assert_called_once_with(query, params)

    def test_execute_query_invalid_operation(self):
        """测试执行无效的查询操作"""
        # 准备测试数据
        query = 'SET'  # 这是一个写操作，不是读操作
        params = ['user:1', 'John']

        # 执行测试并验证异常
        with self.assertRaises(QueryError) as context:
            self.adapter.execute_query(query, params)

        self.assertIn("not a read command", str(context.exception))

    def test_execute_write_valid(self):
        """测试执行有效的写操作"""
        # 准备测试数据
        query = 'SET'
        params = ['user:1', 'John']
        expected_result = 'OK'

        # 设置模拟行为
        self.mock_connection.execute.return_value = expected_result

        # 执行测试
        result = self.adapter.execute_write(query, params)

        # 验证结果
        self.assertEqual(result, expected_result)
        self.mock_connection.execute.assert_called_once_with(query, params)

    def test_execute_write_invalid_operation(self):
        """测试执行无效的写操作"""
        # 准备测试数据
        query = 'GET'  # 这是一个读操作，不是写操作
        params = ['user:1']

        # 执行测试并验证异常
        with self.assertRaises(QueryError) as context:
            self.adapter.execute_write(query, params)

        self.assertIn("not a write command", str(context.exception))

    def test_list_resources(self):
        """测试列出键"""
        # 准备测试数据
        keys = ['user:1', 'user:2', 'product:1']

        # 设置模拟行为
        self.mock_connection.client.keys.return_value = keys
        self.mock_connection.client.type.side_effect = ['string', 'string', 'hash']
        self.mock_connection.client.ttl.side_effect = [100, -1, 200]

        # 模拟_get_key_size方法
        self.adapter._get_key_size = MagicMock(side_effect=[10, 12, 50])

        # 执行测试
        result = self.adapter.list_resources()

        # 验证结果
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['name'], 'user:1')
        self.assertEqual(result[0]['type'], 'string')
        self.assertEqual(result[0]['ttl'], 100)
        self.assertEqual(result[0]['size'], 10)

        self.assertEqual(result[1]['name'], 'user:2')
        self.assertEqual(result[1]['type'], 'string')
        self.assertIsNone(result[1]['ttl'])  # -1表示没有过期时间
        self.assertEqual(result[1]['size'], 12)

        self.assertEqual(result[2]['name'], 'product:1')
        self.assertEqual(result[2]['type'], 'hash')
        self.assertEqual(result[2]['ttl'], 200)
        self.assertEqual(result[2]['size'], 50)

    def test_describe_resource_existing(self):
        """测试描述存在的键"""
        # 准备测试数据
        resource_name = 'user:1'

        # 设置模拟行为
        self.adapter._resource_exists = MagicMock(return_value=True)
        self.mock_connection.client.type.return_value = 'string'
        self.mock_connection.client.ttl.return_value = 100
        self.adapter._get_key_size = MagicMock(return_value=10)
        self.adapter._get_key_content = MagicMock(return_value='John')

        # 执行测试
        result = self.adapter.describe_resource(resource_name)

        # 验证结果
        self.assertEqual(result['name'], resource_name)
        self.assertEqual(result['type'], 'string')
        self.assertEqual(result['ttl'], 100)
        self.assertEqual(result['size'], 10)
        self.assertEqual(result['content'], 'John')

    def test_describe_resource_nonexistent(self):
        """测试描述不存在的键"""
        # 准备测试数据
        resource_name = 'nonexistent'

        # 设置模拟行为
        self.adapter._resource_exists = MagicMock(return_value=False)

        # 执行测试并验证异常
        with self.assertRaises(ResourceNotFoundError) as context:
            self.adapter.describe_resource(resource_name)

        self.assertIn("does not exist", str(context.exception))

    def test_get_resource_stats(self):
        """测试获取键统计信息"""
        # 准备测试数据
        resource_name = 'user:1'

        # 设置模拟行为
        self.adapter._resource_exists = MagicMock(return_value=True)
        self.mock_connection.client.type.return_value = 'string'
        self.mock_connection.client.ttl.return_value = 100
        self.adapter._get_key_size = MagicMock(return_value=10)
        self.mock_connection.client.memory_usage.return_value = 64

        # 执行测试
        result = self.adapter.get_resource_stats(resource_name)

        # 验证结果
        self.assertEqual(result['type'], 'string')
        self.assertEqual(result['ttl'], 100)
        self.assertEqual(result['size'], 10)
        self.assertEqual(result['memory_usage'], 64)

    def test_extract_resource_name(self):
        """测试从命令中提取键名"""
        # 准备测试数据
        query = 'GET user:1'

        # 执行测试
        result = self.adapter.extract_resource_name(query)

        # 验证结果
        self.assertEqual(result, 'USER:1')  # 应该返回大写的键名


if __name__ == '__main__':
    unittest.main()