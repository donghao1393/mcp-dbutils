"""
SQLConnection类的单元测试
"""

import unittest
from unittest.mock import MagicMock, patch

from mcp_dbutils.multi_db.connection.sql import SQLConnection
from mcp_dbutils.multi_db.error.exceptions import ConnectionError, TransactionError


class TestSQLConnection(unittest.TestCase):
    """SQLConnection类的测试用例"""

    def setUp(self):
        """测试前的准备工作"""
        self.config = {
            'type': 'mysql',
            'host': 'localhost',
            'port': 3306,
            'database': 'test_db',
            'username': 'test_user',
            'password': 'test_password',
            'pool_size': 5,
            'max_overflow': 10,
            'pool_recycle': 3600,
            'pool_timeout': 30,
            'pool_pre_ping': True,
            'isolation_level': 'READ COMMITTED'
        }
        self.connection = SQLConnection(self.config)
        # 模拟数据库连接
        self.connection.dbapi_connection = MagicMock()
        self.connection.is_transaction_active = False

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.connection.db_type, 'mysql')
        self.assertEqual(self.connection.pool_size, 5)
        self.assertEqual(self.connection.max_overflow, 10)
        self.assertEqual(self.connection.pool_recycle, 3600)
        self.assertEqual(self.connection.pool_timeout, 30)
        self.assertTrue(self.connection.pool_pre_ping)
        self.assertEqual(self.connection.isolation_level, 'READ COMMITTED')
        self.assertEqual(self.connection.savepoint_id, 0)

    @patch('mcp_dbutils.multi_db.connection.sql.SQLConnection._connect_mysql')
    def test_connect_mysql(self, mock_connect_mysql):
        """测试连接MySQL数据库"""
        self.connection.connect()
        mock_connect_mysql.assert_called_once()

    @patch('mcp_dbutils.multi_db.connection.sql.SQLConnection._connect_postgresql')
    def test_connect_postgresql(self, mock_connect_postgresql):
        """测试连接PostgreSQL数据库"""
        self.connection.db_type = 'postgresql'
        self.connection.connect()
        mock_connect_postgresql.assert_called_once()

    @patch('mcp_dbutils.multi_db.connection.sql.SQLConnection._connect_sqlite')
    def test_connect_sqlite(self, mock_connect_sqlite):
        """测试连接SQLite数据库"""
        self.connection.db_type = 'sqlite'
        self.connection.connect()
        mock_connect_sqlite.assert_called_once()

    def test_connect_unsupported(self):
        """测试连接不支持的数据库类型"""
        self.connection.db_type = 'unsupported'
        with self.assertRaises(ConnectionError):
            self.connection.connect()

    def test_disconnect(self):
        """测试断开连接"""
        self.connection.disconnect()
        self.connection.dbapi_connection.close.assert_called_once()
        self.assertIsNone(self.connection.dbapi_connection)

    def test_is_connected(self):
        """测试检查连接状态"""
        # MySQL
        self.connection.dbapi_connection.open = True
        self.assertTrue(self.connection.is_connected())

        # PostgreSQL
        self.connection.db_type = 'postgresql'
        self.connection.dbapi_connection.closed = 0
        self.assertTrue(self.connection.is_connected())

        # SQLite
        self.connection.db_type = 'sqlite'
        cursor_mock = MagicMock()
        self.connection.dbapi_connection.cursor.return_value = cursor_mock
        self.assertTrue(self.connection.is_connected())

    def test_check_connection_health(self):
        """测试检查连接健康状态"""
        cursor_mock = MagicMock()
        self.connection.dbapi_connection.cursor.return_value = cursor_mock
        self.assertTrue(self.connection.check_connection_health())

        # 测试连接不健康的情况
        cursor_mock.execute.side_effect = Exception("Connection error")
        self.assertFalse(self.connection.check_connection_health())

    @patch('mcp_dbutils.multi_db.connection.sql.SQLConnection.disconnect')
    @patch('mcp_dbutils.multi_db.connection.sql.SQLConnection.connect')
    def test_reconnect(self, mock_connect, mock_disconnect):
        """测试重新连接"""
        self.connection.reconnect()
        mock_disconnect.assert_called_once()
        mock_connect.assert_called_once()

    def test_ping(self):
        """测试Ping数据库服务器"""
        # MySQL
        self.assertTrue(self.connection.ping())

        # PostgreSQL
        self.connection.db_type = 'postgresql'
        cursor_mock = MagicMock()
        self.connection.dbapi_connection.cursor.return_value = cursor_mock
        self.assertTrue(self.connection.ping())

        # SQLite
        self.connection.db_type = 'sqlite'
        self.assertTrue(self.connection.ping())

    def test_execute(self):
        """测试执行SQL查询"""
        cursor_mock = MagicMock()
        self.connection.dbapi_connection.cursor.return_value = cursor_mock
        cursor_mock.fetchall.return_value = [('result',)]

        # SELECT查询
        result = self.connection.execute("SELECT * FROM test")
        self.assertEqual(result, [('result',)])
        cursor_mock.execute.assert_called_with("SELECT * FROM test", None)

        # INSERT查询
        cursor_mock.lastrowid = 1
        result = self.connection.execute("INSERT INTO test VALUES (1)")
        self.assertEqual(result, {"affected_rows": cursor_mock.rowcount, "last_insert_id": 1})

    def test_begin_transaction(self):
        """测试开始事务"""
        # 开始新事务
        self.connection.begin_transaction()
        self.assertTrue(self.connection.is_transaction_active)
        self.connection.dbapi_connection.autocommit = False

        # 创建保存点
        self.connection.begin_transaction()
        self.assertEqual(self.connection.savepoint_id, 1)

    def test_commit(self):
        """测试提交事务"""
        self.connection.is_transaction_active = True
        self.connection.commit()
        self.connection.dbapi_connection.commit.assert_called_once()
        self.assertFalse(self.connection.is_transaction_active)
        self.assertEqual(self.connection.savepoint_id, 0)

    def test_rollback(self):
        """测试回滚事务"""
        # 回滚整个事务
        self.connection.is_transaction_active = True
        self.connection.rollback()
        self.connection.dbapi_connection.rollback.assert_called_once()
        self.assertFalse(self.connection.is_transaction_active)
        self.assertEqual(self.connection.savepoint_id, 0)

        # 回滚到保存点
        self.connection.is_transaction_active = True
        self.connection.rollback("sp_1")
        self.connection.dbapi_connection.cursor.return_value.execute.assert_called_with("ROLLBACK TO SAVEPOINT sp_1")

    def test_create_savepoint(self):
        """测试创建保存点"""
        self.connection.is_transaction_active = True
        savepoint_name = self.connection._create_savepoint()
        self.assertEqual(savepoint_name, "sp_1")
        self.assertEqual(self.connection.savepoint_id, 1)
        self.connection.dbapi_connection.cursor.return_value.execute.assert_called_with("SAVEPOINT sp_1")

    def test_release_savepoint(self):
        """测试释放保存点"""
        self.connection.is_transaction_active = True
        self.connection.release_savepoint("sp_1")
        self.connection.dbapi_connection.cursor.return_value.execute.assert_called_with("RELEASE SAVEPOINT sp_1")

    @patch('mcp_dbutils.multi_db.connection.sql.SQLConnection.begin_transaction')
    @patch('mcp_dbutils.multi_db.connection.sql.SQLConnection.commit')
    @patch('mcp_dbutils.multi_db.connection.sql.SQLConnection.rollback')
    def test_transaction_context_manager(self, mock_rollback, mock_commit, mock_begin):
        """测试事务上下文管理器"""
        # 正常情况
        with self.connection.transaction():
            pass
        mock_begin.assert_called_once()
        mock_commit.assert_called_once()
        mock_rollback.assert_not_called()

        # 异常情况
        mock_begin.reset_mock()
        mock_commit.reset_mock()
        with self.assertRaises(ValueError):
            with self.connection.transaction():
                raise ValueError("Test error")
        mock_begin.assert_called_once()
        mock_commit.assert_not_called()
        mock_rollback.assert_called_once()

    def test_execute_batch(self):
        """测试批量执行SQL查询"""
        cursor_mock = MagicMock()
        self.connection.dbapi_connection.cursor.return_value = cursor_mock
        cursor_mock.fetchall.return_value = [('result',)]
        cursor_mock.lastrowid = 1

        params_list = [{'id': 1}, {'id': 2}]
        results = self.connection.execute_batch("INSERT INTO test VALUES (:id)", params_list)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], {"affected_rows": cursor_mock.rowcount, "last_insert_id": 1})
        self.assertEqual(results[1], {"affected_rows": cursor_mock.rowcount, "last_insert_id": 1})

    def test_execute_many(self):
        """测试执行多个SQL查询"""
        cursor_mock = MagicMock()
        self.connection.dbapi_connection.cursor.return_value = cursor_mock
        cursor_mock.rowcount = 2

        params_list = [{'id': 1}, {'id': 2}]
        result = self.connection.execute_many("INSERT INTO test VALUES (:id)", params_list)
        self.assertEqual(result, {"affected_rows": 2})
        cursor_mock.executemany.assert_called_with("INSERT INTO test VALUES (:id)", params_list)


if __name__ == '__main__':
    unittest.main()
