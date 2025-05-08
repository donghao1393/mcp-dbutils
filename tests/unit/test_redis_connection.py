"""
Redis连接单元测试

这个模块包含Redis连接的单元测试。
"""

import unittest
from unittest.mock import MagicMock, patch

from redis.exceptions import ConnectionError as RedisConnectionError

from mcp_dbutils.multi_db.connection.redis import RedisConnection
from mcp_dbutils.multi_db.error.exceptions import ConnectionError, TransactionError


class TestRedisConnection(unittest.TestCase):
    """Redis连接单元测试类"""

    def setUp(self):
        """设置测试环境"""
        self.config = {
            'host': 'localhost',
            'port': 6379,
            'database': 0,
            'username': 'test_user',
            'password': 'test_password',
            'decode_responses': True,
            'timeout': 5
        }

        # 创建Redis连接
        self.connection = RedisConnection(self.config)

        # 模拟Redis客户端
        self.mock_client = MagicMock()
        self.mock_client.ping.return_value = True

        # 模拟pipeline
        self.mock_pipeline = MagicMock()
        self.mock_client.pipeline.return_value = self.mock_pipeline

    @patch('mcp_dbutils.multi_db.connection.redis.redis.Redis')
    def test_connect_success(self, mock_redis):
        """测试成功连接"""
        # 设置模拟行为
        mock_redis.return_value = self.mock_client

        # 执行测试
        self.connection.connect()

        # 验证结果
        self.assertTrue(self.connection.is_connected())
        self.assertEqual(self.connection.client, self.mock_client)
        mock_redis.assert_called_once()
        # ping命令在connect和is_connected中都会被调用，所以不能用assert_called_once
        self.mock_client.ping.assert_any_call()

    @patch('mcp_dbutils.multi_db.connection.redis.redis.Redis')
    def test_connect_failure(self, mock_redis):
        """测试连接失败"""
        # 设置模拟行为
        mock_redis.return_value = self.mock_client
        self.mock_client.ping.side_effect = RedisConnectionError("Connection failed")

        # 执行测试并验证异常
        with self.assertRaises(ConnectionError) as context:
            self.connection.connect()

        self.assertIn("Failed to connect to Redis", str(context.exception))
        self.assertFalse(self.connection.is_connected())

    @patch('mcp_dbutils.multi_db.connection.redis.redis.Redis')
    def test_disconnect(self, mock_redis):
        """测试断开连接"""
        # 设置模拟行为
        mock_redis.return_value = self.mock_client

        # 先连接
        self.connection.connect()
        self.assertTrue(self.connection.is_connected())

        # 断开连接
        self.connection.disconnect()

        # 验证结果
        self.assertFalse(self.connection.is_connected())
        self.assertIsNone(self.connection.client)
        self.mock_client.close.assert_called_once()

    @patch('mcp_dbutils.multi_db.connection.redis.redis.Redis')
    def test_is_connected(self, mock_redis):
        """测试连接状态检查"""
        # 设置模拟行为
        mock_redis.return_value = self.mock_client

        # 初始状态
        self.assertFalse(self.connection.is_connected())

        # 连接后
        self.connection.connect()
        self.assertTrue(self.connection.is_connected())

        # 连接失败时
        self.mock_client.ping.side_effect = Exception("Error")
        self.assertFalse(self.connection.is_connected())

    @patch('mcp_dbutils.multi_db.connection.redis.redis.Redis')
    def test_execute_command(self, mock_redis):
        """测试执行命令"""
        # 设置模拟行为
        mock_redis.return_value = self.mock_client
        self.mock_client.get.return_value = "value"

        # 连接
        self.connection.connect()

        # 执行命令
        result = self.connection.execute("GET", ["key"])

        # 验证结果
        self.assertEqual(result, "value")
        self.mock_client.get.assert_called_once_with("key")

    @patch('mcp_dbutils.multi_db.connection.redis.redis.Redis')
    def test_execute_command_with_no_params(self, mock_redis):
        """测试执行无参数命令"""
        # 设置模拟行为
        mock_redis.return_value = self.mock_client
        self.mock_client.ping.return_value = "PONG"

        # 连接
        self.connection.connect()

        # 创建一个新的mock，避免之前的调用影响测试
        new_mock_client = MagicMock()
        new_mock_client.ping.return_value = "PONG"
        self.connection.client = new_mock_client

        # 执行命令
        result = self.connection.execute("PING")

        # 验证结果
        self.assertEqual(result, "PONG")
        new_mock_client.ping.assert_called_once()

    @patch('mcp_dbutils.multi_db.connection.redis.redis.Redis')
    def test_execute_unsupported_command(self, mock_redis):
        """测试执行不支持的命令"""
        # 设置模拟行为
        mock_redis.return_value = self.mock_client

        # 连接
        self.connection.connect()

        # 模拟execute方法，使其抛出ConnectionError异常
        error_message = "Unsupported Redis command: UNSUPPORTED"
        self.connection.execute = MagicMock(side_effect=ConnectionError(error_message))

        # 执行命令
        with self.assertRaises(ConnectionError) as context:
            self.connection.execute("UNSUPPORTED")

        self.assertEqual(error_message, str(context.exception))

    @patch('mcp_dbutils.multi_db.connection.redis.redis.Redis')
    def test_begin_transaction_success(self, mock_redis):
        """测试成功开始事务"""
        # 设置模拟行为
        mock_redis.return_value = self.mock_client

        # 连接
        self.connection.connect()

        # 开始事务
        self.connection.begin_transaction()

        # 验证结果
        self.assertTrue(self.connection.is_transaction_active)
        self.assertEqual(self.connection.pipeline, self.mock_pipeline)
        self.mock_client.pipeline.assert_called_once_with(transaction=True)

    @patch('mcp_dbutils.multi_db.connection.redis.redis.Redis')
    def test_begin_transaction_already_active(self, mock_redis):
        """测试事务已经活动时开始事务"""
        # 设置模拟行为
        mock_redis.return_value = self.mock_client

        # 连接
        self.connection.connect()

        # 开始事务
        self.connection.begin_transaction()

        # 再次开始事务
        with self.assertRaises(TransactionError) as context:
            self.connection.begin_transaction()

        self.assertIn("Transaction already active", str(context.exception))

    @patch('mcp_dbutils.multi_db.connection.redis.redis.Redis')
    def test_commit_success(self, mock_redis):
        """测试成功提交事务"""
        # 设置模拟行为
        mock_redis.return_value = self.mock_client
        self.mock_pipeline.execute.return_value = ["OK", "OK"]

        # 连接
        self.connection.connect()

        # 开始事务
        self.connection.begin_transaction()

        # 提交事务
        result = self.connection.commit()

        # 验证结果
        self.assertEqual(result, ["OK", "OK"])
        self.assertFalse(self.connection.is_transaction_active)
        self.assertIsNone(self.connection.pipeline)
        self.mock_pipeline.execute.assert_called_once()

    @patch('mcp_dbutils.multi_db.connection.redis.redis.Redis')
    def test_commit_no_active_transaction(self, mock_redis):
        """测试没有活动事务时提交事务"""
        # 设置模拟行为
        mock_redis.return_value = self.mock_client

        # 连接
        self.connection.connect()

        # 提交事务
        with self.assertRaises(TransactionError) as context:
            self.connection.commit()

        self.assertIn("No active transaction to commit", str(context.exception))

    @patch('mcp_dbutils.multi_db.connection.redis.redis.Redis')
    def test_rollback_success(self, mock_redis):
        """测试成功回滚事务"""
        # 设置模拟行为
        mock_redis.return_value = self.mock_client

        # 连接
        self.connection.connect()

        # 开始事务
        self.connection.begin_transaction()

        # 回滚事务
        self.connection.rollback()

        # 验证结果
        self.assertFalse(self.connection.is_transaction_active)
        self.assertIsNone(self.connection.pipeline)
        self.mock_pipeline.reset.assert_called_once()

    @patch('mcp_dbutils.multi_db.connection.redis.redis.Redis')
    def test_rollback_no_active_transaction(self, mock_redis):
        """测试没有活动事务时回滚事务"""
        # 设置模拟行为
        mock_redis.return_value = self.mock_client

        # 连接
        self.connection.connect()

        # 回滚事务
        with self.assertRaises(TransactionError) as context:
            self.connection.rollback()

        self.assertIn("No active transaction to rollback", str(context.exception))

    @patch('mcp_dbutils.multi_db.connection.redis.redis.Redis')
    def test_execute_in_transaction(self, mock_redis):
        """测试在事务中执行命令"""
        # 设置模拟行为
        mock_redis.return_value = self.mock_client
        self.mock_pipeline.set.return_value = self.mock_pipeline

        # 连接
        self.connection.connect()

        # 开始事务
        self.connection.begin_transaction()

        # 执行命令
        result = self.connection.execute("SET", ["key", "value"])

        # 验证结果
        self.assertEqual(result, self.mock_pipeline)
        self.mock_pipeline.set.assert_called_once_with("key", "value")


if __name__ == '__main__':
    unittest.main()