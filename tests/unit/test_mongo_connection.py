"""
MongoDB连接单元测试

这个模块包含MongoDB连接的单元测试。
"""

import unittest
from unittest.mock import MagicMock, patch

from pymongo.errors import ConnectionFailure, PyMongoError, ServerSelectionTimeoutError

from mcp_dbutils.multi_db.connection.mongo import MongoConnection
from mcp_dbutils.multi_db.error.exceptions import ConnectionError, TransactionError


class TestMongoConnection(unittest.TestCase):
    """MongoDB连接单元测试类"""

    def setUp(self):
        """设置测试环境"""
        self.config = {
            'host': 'localhost',
            'port': 27017,
            'database': 'test_db',
            'username': 'test_user',
            'password': 'test_password',
            'auth_source': 'admin',
            'timeout': 5000
        }

        # 创建MongoDB连接
        self.connection = MongoConnection(self.config)

        # 模拟MongoClient
        self.mock_client = MagicMock()
        self.mock_db = MagicMock()
        self.mock_client.__getitem__.return_value = self.mock_db
        self.mock_client.admin.command.return_value = {'ok': 1}

        # 模拟session
        self.mock_session = MagicMock()
        self.mock_client.start_session.return_value = self.mock_session

    @patch('mcp_dbutils.multi_db.connection.mongo.MongoClient')
    def test_connect_success(self, mock_mongo_client):
        """测试成功连接"""
        # 设置模拟行为
        mock_mongo_client.return_value = self.mock_client

        # 模拟_build_connection_uri方法
        self.connection._build_connection_uri = MagicMock(return_value="mongodb://localhost:27017/")

        # 执行测试
        self.connection.connect()

        # 验证结果
        self.assertTrue(self.connection.is_connected())
        self.assertEqual(self.connection.db, self.mock_db)
        mock_mongo_client.assert_called_once()
        # ping命令在connect和is_connected中都会被调用，所以不能用assert_called_once_with
        self.mock_client.admin.command.assert_any_call('ping')

    @patch('mcp_dbutils.multi_db.connection.mongo.MongoClient')
    def test_connect_failure(self, mock_mongo_client):
        """测试连接失败"""
        # 设置模拟行为
        mock_mongo_client.return_value = self.mock_client
        self.mock_client.admin.command.side_effect = ConnectionFailure("Connection failed")

        # 执行测试并验证异常
        with self.assertRaises(ConnectionError) as context:
            self.connection.connect()

        self.assertIn("Failed to connect to MongoDB", str(context.exception))
        self.assertFalse(self.connection.is_connected())

    @patch('mcp_dbutils.multi_db.connection.mongo.MongoClient')
    def test_disconnect(self, mock_mongo_client):
        """测试断开连接"""
        # 设置模拟行为
        mock_mongo_client.return_value = self.mock_client

        # 模拟_build_connection_uri方法
        self.connection._build_connection_uri = MagicMock(return_value="mongodb://localhost:27017/")

        # 先连接
        self.connection.connect()
        self.assertTrue(self.connection.is_connected())

        # 断开连接
        self.connection.disconnect()

        # 验证结果
        self.assertFalse(self.connection.is_connected())
        self.assertIsNone(self.connection.client)
        self.assertIsNone(self.connection.db)

    @patch('mcp_dbutils.multi_db.connection.mongo.MongoClient')
    def test_is_connected(self, mock_mongo_client):
        """测试连接状态检查"""
        # 设置模拟行为
        mock_mongo_client.return_value = self.mock_client

        # 模拟_build_connection_uri方法
        self.connection._build_connection_uri = MagicMock(return_value="mongodb://localhost:27017/")

        # 初始状态
        self.assertFalse(self.connection.is_connected())

        # 连接后
        self.connection.connect()
        self.assertTrue(self.connection.is_connected())

        # 连接失败时
        self.mock_client.admin.command.side_effect = PyMongoError("Error")
        self.assertFalse(self.connection.is_connected())

    @patch('mcp_dbutils.multi_db.connection.mongo.MongoClient')
    def test_execute_find(self, mock_mongo_client):
        """测试执行find查询"""
        # 设置模拟行为
        mock_mongo_client.return_value = self.mock_client
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection

        expected_result = [{'name': 'John', 'age': 25}]
        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = iter(expected_result)
        mock_collection.find.return_value = mock_cursor

        # 模拟_build_connection_uri方法
        self.connection._build_connection_uri = MagicMock(return_value="mongodb://localhost:27017/")

        # 连接
        self.connection.connect()

        # 执行查询
        query = {
            'operation': 'find',
            'collection': 'users',
            'params': {
                'filter': {'age': {'$gt': 18}},
                'projection': {'name': 1, 'age': 1},
                'sort': [('age', 1)],
                'limit': 10,
                'skip': 5
            }
        }

        result = self.connection.execute(query)

        # 验证结果
        self.assertEqual(result, expected_result)
        mock_collection.find.assert_called_once_with({'age': {'$gt': 18}}, {'name': 1, 'age': 1})
        mock_cursor.sort.assert_called_once_with([('age', 1)])
        mock_cursor.skip.assert_called_once_with(5)
        mock_cursor.limit.assert_called_once_with(10)

    @patch('mcp_dbutils.multi_db.connection.mongo.MongoClient')
    def test_execute_find_one(self, mock_mongo_client):
        """测试执行find_one查询"""
        # 设置模拟行为
        mock_mongo_client.return_value = self.mock_client
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection

        expected_result = {'name': 'John', 'age': 25}
        mock_collection.find_one.return_value = expected_result

        # 模拟_build_connection_uri方法
        self.connection._build_connection_uri = MagicMock(return_value="mongodb://localhost:27017/")

        # 连接
        self.connection.connect()

        # 执行查询
        query = {
            'operation': 'find_one',
            'collection': 'users',
            'params': {
                'filter': {'name': 'John'},
                'projection': {'name': 1, 'age': 1}
            }
        }

        result = self.connection.execute(query)

        # 验证结果
        self.assertEqual(result, expected_result)
        mock_collection.find_one.assert_called_once_with({'name': 'John'}, {'name': 1, 'age': 1})

    @patch('mcp_dbutils.multi_db.connection.mongo.MongoClient')
    def test_execute_insert_one(self, mock_mongo_client):
        """测试执行insert_one操作"""
        # 设置模拟行为
        mock_mongo_client.return_value = self.mock_client
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection

        mock_result = MagicMock()
        mock_result.inserted_id = '123'
        mock_collection.insert_one.return_value = mock_result

        # 模拟_build_connection_uri方法
        self.connection._build_connection_uri = MagicMock(return_value="mongodb://localhost:27017/")

        # 连接
        self.connection.connect()

        # 执行操作
        query = {
            'operation': 'insert_one',
            'collection': 'users',
            'params': {
                'document': {'name': 'John', 'age': 25}
            }
        }

        result = self.connection.execute(query)

        # 验证结果
        self.assertEqual(result, {'inserted_id': '123'})
        mock_collection.insert_one.assert_called_once_with({'name': 'John', 'age': 25}, session=None)

    @patch('mcp_dbutils.multi_db.connection.mongo.MongoClient')
    def test_execute_update_one(self, mock_mongo_client):
        """测试执行update_one操作"""
        # 设置模拟行为
        mock_mongo_client.return_value = self.mock_client
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection

        mock_result = MagicMock()
        mock_result.matched_count = 1
        mock_result.modified_count = 1
        mock_result.upserted_id = None
        mock_collection.update_one.return_value = mock_result

        # 模拟_build_connection_uri方法
        self.connection._build_connection_uri = MagicMock(return_value="mongodb://localhost:27017/")

        # 连接
        self.connection.connect()

        # 执行操作
        query = {
            'operation': 'update_one',
            'collection': 'users',
            'params': {
                'filter': {'name': 'John'},
                'update': {'$set': {'age': 26}},
                'upsert': False
            }
        }

        result = self.connection.execute(query)

        # 验证结果
        self.assertEqual(result, {
            'matched_count': 1,
            'modified_count': 1,
            'upserted_id': None
        })
        mock_collection.update_one.assert_called_once_with(
            {'name': 'John'}, {'$set': {'age': 26}}, upsert=False, session=None
        )

    @patch('mcp_dbutils.multi_db.connection.mongo.MongoClient')
    def test_execute_delete_one(self, mock_mongo_client):
        """测试执行delete_one操作"""
        # 设置模拟行为
        mock_mongo_client.return_value = self.mock_client
        mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = mock_collection

        mock_result = MagicMock()
        mock_result.deleted_count = 1
        mock_collection.delete_one.return_value = mock_result

        # 模拟_build_connection_uri方法
        self.connection._build_connection_uri = MagicMock(return_value="mongodb://localhost:27017/")

        # 连接
        self.connection.connect()

        # 执行操作
        query = {
            'operation': 'delete_one',
            'collection': 'users',
            'params': {
                'filter': {'name': 'John'}
            }
        }

        result = self.connection.execute(query)

        # 验证结果
        self.assertEqual(result, {'deleted_count': 1})
        mock_collection.delete_one.assert_called_once_with({'name': 'John'}, session=None)

    @patch('mcp_dbutils.multi_db.connection.mongo.MongoClient')
    def test_execute_unsupported_operation(self, mock_mongo_client):
        """测试执行不支持的操作"""
        # 设置模拟行为
        mock_mongo_client.return_value = self.mock_client

        # 模拟_build_connection_uri方法
        self.connection._build_connection_uri = MagicMock(return_value="mongodb://localhost:27017/")

        # 连接
        self.connection.connect()

        # 执行操作
        query = {
            'operation': 'unsupported',
            'collection': 'users'
        }

        # 验证异常
        with self.assertRaises(ConnectionError) as context:
            self.connection.execute(query)

        self.assertIn("Unsupported MongoDB operation", str(context.exception))

    @patch('mcp_dbutils.multi_db.connection.mongo.MongoClient')
    def test_begin_transaction_success(self, mock_mongo_client):
        """测试成功开始事务"""
        # 设置模拟行为
        mock_mongo_client.return_value = self.mock_client

        # 模拟支持事务
        self.connection._supports_transactions = MagicMock(return_value=True)

        # 模拟_build_connection_uri方法
        self.connection._build_connection_uri = MagicMock(return_value="mongodb://localhost:27017/")

        # 连接
        self.connection.connect()

        # 开始事务
        self.connection.begin_transaction()

        # 验证结果
        self.assertTrue(self.connection.is_transaction_active)
        self.assertEqual(self.connection.session, self.mock_session)
        self.mock_client.start_session.assert_called_once()
        self.mock_session.start_transaction.assert_called_once()

    @patch('mcp_dbutils.multi_db.connection.mongo.MongoClient')
    def test_begin_transaction_already_active(self, mock_mongo_client):
        """测试事务已经活动时开始事务"""
        # 设置模拟行为
        mock_mongo_client.return_value = self.mock_client

        # 模拟支持事务
        self.connection._supports_transactions = MagicMock(return_value=True)

        # 模拟_build_connection_uri方法
        self.connection._build_connection_uri = MagicMock(return_value="mongodb://localhost:27017/")

        # 连接
        self.connection.connect()

        # 开始事务
        self.connection.begin_transaction()

        # 再次开始事务
        with self.assertRaises(TransactionError) as context:
            self.connection.begin_transaction()

        self.assertIn("Transaction already active", str(context.exception))

    @patch('mcp_dbutils.multi_db.connection.mongo.MongoClient')
    def test_begin_transaction_not_supported(self, mock_mongo_client):
        """测试不支持事务时开始事务"""
        # 设置模拟行为
        mock_mongo_client.return_value = self.mock_client

        # 模拟不支持事务
        self.connection._supports_transactions = MagicMock(return_value=False)

        # 模拟_build_connection_uri方法
        self.connection._build_connection_uri = MagicMock(return_value="mongodb://localhost:27017/")

        # 连接
        self.connection.connect()

        # 开始事务
        with self.assertRaises(TransactionError) as context:
            self.connection.begin_transaction()

        self.assertIn("MongoDB transactions require a replica set", str(context.exception))

    @patch('mcp_dbutils.multi_db.connection.mongo.MongoClient')
    def test_commit_success(self, mock_mongo_client):
        """测试成功提交事务"""
        # 设置模拟行为
        mock_mongo_client.return_value = self.mock_client

        # 模拟支持事务
        self.connection._supports_transactions = MagicMock(return_value=True)

        # 模拟_build_connection_uri方法
        self.connection._build_connection_uri = MagicMock(return_value="mongodb://localhost:27017/")

        # 连接
        self.connection.connect()

        # 开始事务
        self.connection.begin_transaction()

        # 提交事务
        self.connection.commit()

        # 验证结果
        self.assertFalse(self.connection.is_transaction_active)
        self.assertIsNone(self.connection.session)
        self.mock_session.commit_transaction.assert_called_once()
        self.mock_session.end_session.assert_called_once()

    @patch('mcp_dbutils.multi_db.connection.mongo.MongoClient')
    def test_commit_no_active_transaction(self, mock_mongo_client):
        """测试没有活动事务时提交事务"""
        # 设置模拟行为
        mock_mongo_client.return_value = self.mock_client

        # 模拟_build_connection_uri方法
        self.connection._build_connection_uri = MagicMock(return_value="mongodb://localhost:27017/")

        # 连接
        self.connection.connect()

        # 提交事务
        with self.assertRaises(TransactionError) as context:
            self.connection.commit()

        self.assertIn("No active transaction to commit", str(context.exception))

    @patch('mcp_dbutils.multi_db.connection.mongo.MongoClient')
    def test_rollback_success(self, mock_mongo_client):
        """测试成功回滚事务"""
        # 设置模拟行为
        mock_mongo_client.return_value = self.mock_client

        # 模拟支持事务
        self.connection._supports_transactions = MagicMock(return_value=True)

        # 模拟_build_connection_uri方法
        self.connection._build_connection_uri = MagicMock(return_value="mongodb://localhost:27017/")

        # 连接
        self.connection.connect()

        # 开始事务
        self.connection.begin_transaction()

        # 回滚事务
        self.connection.rollback()

        # 验证结果
        self.assertFalse(self.connection.is_transaction_active)
        self.assertIsNone(self.connection.session)
        self.mock_session.abort_transaction.assert_called_once()
        self.mock_session.end_session.assert_called_once()

    @patch('mcp_dbutils.multi_db.connection.mongo.MongoClient')
    def test_rollback_no_active_transaction(self, mock_mongo_client):
        """测试没有活动事务时回滚事务"""
        # 设置模拟行为
        mock_mongo_client.return_value = self.mock_client

        # 模拟_build_connection_uri方法
        self.connection._build_connection_uri = MagicMock(return_value="mongodb://localhost:27017/")

        # 连接
        self.connection.connect()

        # 回滚事务
        with self.assertRaises(TransactionError) as context:
            self.connection.rollback()

        self.assertIn("No active transaction to rollback", str(context.exception))


if __name__ == '__main__':
    unittest.main()