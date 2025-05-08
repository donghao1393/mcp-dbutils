"""
SQLAdapter类的单元测试
"""

import unittest
from unittest.mock import MagicMock, patch

from mcp_dbutils.multi_db.adapter.sql import SQLAdapter
from mcp_dbutils.multi_db.connection.sql import SQLConnection
from mcp_dbutils.multi_db.error.exceptions import (
    ConnectionError,
    DatabaseError,
    NotImplementedError,
    QueryError,
    ResourceNotFoundError,
)


class TestSQLAdapter(unittest.TestCase):
    """SQLAdapter类的测试用例"""

    def setUp(self):
        """测试前的准备工作"""
        self.connection = MagicMock(spec=SQLConnection)
        self.connection.db_type = 'mysql'
        self.adapter = SQLAdapter(self.connection)

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.adapter.db_type, 'mysql')
        self.assertTrue(self.adapter.features['stored_procedures'])
        self.assertTrue(self.adapter.features['batch_operations'])
        self.assertTrue(self.adapter.features['transactions'])
        self.assertTrue(self.adapter.features['foreign_keys'])
        self.assertTrue(self.adapter.features['views'])
        self.assertTrue(self.adapter.features['triggers'])

        # 测试不支持的数据库类型
        with self.assertRaises(TypeError):
            SQLAdapter(MagicMock())

    def test_execute_query(self):
        """测试执行SQL查询"""
        self.connection.execute.return_value = [('result',)]
        result = self.adapter.execute_query("SELECT * FROM test")
        self.assertEqual(result, [('result',)])
        self.connection.execute.assert_called_with("SELECT * FROM test", None)

        # 测试非只读查询
        with patch('mcp_dbutils.multi_db.adapter.sql.SQLAdapter._is_read_query', return_value=False), \
             self.assertRaises(QueryError):
            self.adapter.execute_query("INSERT INTO test VALUES (1)")

        # 测试连接错误
        self.connection.execute.side_effect = ConnectionError("Connection error")
        with self.assertRaises(ConnectionError):
            self.adapter.execute_query("SELECT * FROM test")

        # 测试其他错误
        self.connection.execute.side_effect = Exception("Other error")
        with self.assertRaises(QueryError):
            self.adapter.execute_query("SELECT * FROM test")

    def test_execute_write(self):
        """测试执行SQL写操作"""
        self.connection.execute.return_value = {"affected_rows": 1, "last_insert_id": 1}
        result = self.adapter.execute_write("INSERT INTO test VALUES (1)")
        self.assertEqual(result, {"affected_rows": 1, "last_insert_id": 1})
        self.connection.execute.assert_called_with("INSERT INTO test VALUES (1)", None)

        # 测试只读查询
        with patch('mcp_dbutils.multi_db.adapter.sql.SQLAdapter._is_read_query', return_value=True), \
             self.assertRaises(QueryError):
            self.adapter.execute_write("SELECT * FROM test")

        # 测试连接错误
        self.connection.execute.side_effect = ConnectionError("Connection error")
        with self.assertRaises(ConnectionError):
            self.adapter.execute_write("INSERT INTO test VALUES (1)")

        # 测试其他错误
        self.connection.execute.side_effect = Exception("Other error")
        with self.assertRaises(QueryError):
            self.adapter.execute_write("INSERT INTO test VALUES (1)")

    def test_list_resources(self):
        """测试列出数据库中的所有表"""
        # 测试MySQL
        self.adapter.db_type = 'mysql'
        self.adapter.execute_query = MagicMock(return_value=[
            ('test_table', 'TABLE', 'InnoDB', 'Test table', '2023-01-01', '2023-01-01')
        ])
        result = self.adapter.list_resources()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'test_table')
        self.assertEqual(result[0]['type'], 'TABLE')
        self.assertEqual(result[0]['engine'], 'InnoDB')
        self.assertEqual(result[0]['comment'], 'Test table')
        self.assertEqual(result[0]['created_at'], '2023-01-01')
        self.assertEqual(result[0]['updated_at'], '2023-01-01')

        # 测试PostgreSQL
        self.adapter.db_type = 'postgresql'
        self.adapter.execute_query = MagicMock(return_value=[
            ('test_table', 'TABLE', None, 'Test table', None, None)
        ])
        result = self.adapter.list_resources()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'test_table')
        self.assertEqual(result[0]['type'], 'TABLE')
        self.assertIsNone(result[0]['engine'])
        self.assertEqual(result[0]['comment'], 'Test table')
        self.assertIsNone(result[0]['created_at'])
        self.assertIsNone(result[0]['updated_at'])

        # 测试SQLite
        self.adapter.db_type = 'sqlite'
        self.adapter.execute_query = MagicMock(return_value=[
            ('test_table', 'TABLE', None, None, None, None)
        ])
        result = self.adapter.list_resources()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'test_table')
        self.assertEqual(result[0]['type'], 'TABLE')
        self.assertIsNone(result[0]['engine'])
        self.assertIsNone(result[0]['comment'])
        self.assertIsNone(result[0]['created_at'])
        self.assertIsNone(result[0]['updated_at'])

        # 测试不支持的数据库类型
        self.adapter.db_type = 'unsupported'
        with self.assertRaises(DatabaseError):
            self.adapter.list_resources()

        # 测试异常情况
        self.adapter.db_type = 'mysql'
        self.adapter.execute_query = MagicMock(side_effect=Exception("Error"))
        with self.assertRaises(DatabaseError):
            self.adapter.list_resources()

    def test_describe_resource(self):
        """测试描述表结构"""
        self.adapter._resource_exists = MagicMock(return_value=True)
        self.adapter._get_columns = MagicMock(return_value=[{'name': 'id', 'type': 'int'}])
        self.adapter._get_indexes = MagicMock(return_value=[{'name': 'PRIMARY', 'columns': ['id']}])
        self.adapter._get_foreign_keys = MagicMock(return_value=[])

        result = self.adapter.describe_resource('test_table')
        self.assertEqual(result['name'], 'test_table')
        self.assertEqual(result['columns'], [{'name': 'id', 'type': 'int'}])
        self.assertEqual(result['indexes'], [{'name': 'PRIMARY', 'columns': ['id']}])
        self.assertEqual(result['foreign_keys'], [])

        # 测试表不存在
        self.adapter._resource_exists = MagicMock(return_value=False)
        with self.assertRaises(ResourceNotFoundError):
            self.adapter.describe_resource('non_existent_table')

    def test_get_resource_stats(self):
        """测试获取表统计信息"""
        # 测试MySQL
        self.adapter.db_type = 'mysql'
        self.adapter._resource_exists = MagicMock(return_value=True)
        self.adapter.execute_query = MagicMock(side_effect=[
            [(100,)],  # 行数
            [(1000, 500, 1500)]  # 大小
        ])

        result = self.adapter.get_resource_stats('test_table')
        self.assertEqual(result['row_count'], 100)
        self.assertEqual(result['data_size'], 1000)
        self.assertEqual(result['index_size'], 500)
        self.assertEqual(result['total_size'], 1500)

        # 测试PostgreSQL
        self.adapter.db_type = 'postgresql'
        self.adapter._resource_exists = MagicMock(return_value=True)
        self.adapter.execute_query = MagicMock(side_effect=[
            [(100,)],  # 行数
            [(1500, 1000, 500)]  # 大小
        ])

        result = self.adapter.get_resource_stats('test_table')
        self.assertEqual(result['row_count'], 100)
        self.assertEqual(result['total_size'], 1500)
        self.assertEqual(result['data_size'], 1000)
        self.assertEqual(result['index_size'], 500)

        # 测试SQLite
        self.adapter.db_type = 'sqlite'
        self.adapter._resource_exists = MagicMock(return_value=True)
        self.adapter.execute_query = MagicMock(return_value=[(100,)])  # 只有行数

        result = self.adapter.get_resource_stats('test_table')
        self.assertEqual(result['row_count'], 100)
        self.assertNotIn('data_size', result)  # SQLite不支持获取表大小

        # 测试不支持的数据库类型
        self.adapter.db_type = 'unsupported'
        self.adapter._resource_exists = MagicMock(return_value=True)
        with self.assertRaises(DatabaseError):
            self.adapter.get_resource_stats('test_table')

        # 测试表不存在
        self.adapter.db_type = 'mysql'
        self.adapter._resource_exists = MagicMock(return_value=False)
        with self.assertRaises(ResourceNotFoundError):
            self.adapter.get_resource_stats('non_existent_table')

        # 测试异常情况
        self.adapter._resource_exists = MagicMock(return_value=True)
        self.adapter.execute_query = MagicMock(side_effect=Exception("Error"))
        with self.assertRaises(DatabaseError):
            self.adapter.get_resource_stats('test_table')

    def test_extract_resource_name(self):
        """测试从SQL查询中提取表名"""
        # INSERT
        self.assertEqual(self.adapter.extract_resource_name("INSERT INTO test VALUES (1)"), "TEST")
        # UPDATE
        self.assertEqual(self.adapter.extract_resource_name("UPDATE test SET id = 1"), "TEST")
        # DELETE
        self.assertEqual(self.adapter.extract_resource_name("DELETE FROM test WHERE id = 1"), "TEST")
        # SELECT
        self.assertEqual(self.adapter.extract_resource_name("SELECT * FROM test WHERE id = 1"), "TEST")
        # 带引号和空格的表名
        self.assertEqual(self.adapter.extract_resource_name("INSERT INTO `test table` VALUES (1)"), "TEST")
        self.assertEqual(self.adapter.extract_resource_name("UPDATE \"test table\" SET id = 1"), "TEST")
        self.assertEqual(self.adapter.extract_resource_name("DELETE FROM [test table] WHERE id = 1"), "TEST")
        # 复杂SELECT查询
        self.assertEqual(self.adapter.extract_resource_name("SELECT t.* FROM test t JOIN other o ON t.id = o.id"), "TEST")
        # 空查询
        self.assertEqual(self.adapter.extract_resource_name(""), "unknown_table")
        # 异常情况
        self.assertEqual(self.adapter.extract_resource_name("INVALID SQL"), "unknown_table")

    def test_is_read_query(self):
        """测试判断查询是否是只读的"""
        self.assertTrue(self.adapter._is_read_query("SELECT * FROM test"))
        self.assertTrue(self.adapter._is_read_query("SHOW TABLES"))
        self.assertTrue(self.adapter._is_read_query("DESCRIBE test"))
        self.assertTrue(self.adapter._is_read_query("EXPLAIN SELECT * FROM test"))
        self.assertFalse(self.adapter._is_read_query("INSERT INTO test VALUES (1)"))
        self.assertFalse(self.adapter._is_read_query("UPDATE test SET id = 1"))
        self.assertFalse(self.adapter._is_read_query("DELETE FROM test WHERE id = 1"))
        self.assertFalse(self.adapter._is_read_query(""))

    def test_resource_exists(self):
        """测试检查表是否存在"""
        # 测试MySQL
        self.adapter.db_type = 'mysql'
        self.adapter.execute_query = MagicMock(return_value=[(1,)])
        self.assertTrue(self.adapter._resource_exists('test_table'))

        self.adapter.execute_query = MagicMock(return_value=[])
        self.assertFalse(self.adapter._resource_exists('non_existent_table'))

        # 测试PostgreSQL
        self.adapter.db_type = 'postgresql'
        self.adapter.execute_query = MagicMock(return_value=[(1,)])
        self.assertTrue(self.adapter._resource_exists('test_table'))

        self.adapter.execute_query = MagicMock(return_value=[])
        self.assertFalse(self.adapter._resource_exists('non_existent_table'))

        # 测试SQLite
        self.adapter.db_type = 'sqlite'
        self.adapter.execute_query = MagicMock(return_value=[(1,)])
        self.assertTrue(self.adapter._resource_exists('test_table'))

        self.adapter.execute_query = MagicMock(return_value=[])
        self.assertFalse(self.adapter._resource_exists('non_existent_table'))

        # 测试不支持的数据库类型
        self.adapter.db_type = 'unsupported'
        # 由于_resource_exists方法捕获了异常并返回False，所以不会抛出DatabaseError
        self.assertFalse(self.adapter._resource_exists('test_table'))

        # 测试异常情况
        self.adapter.db_type = 'mysql'
        self.adapter.execute_query = MagicMock(side_effect=Exception("Error"))
        self.assertFalse(self.adapter._resource_exists('test_table'))

    def test_execute_batch(self):
        """测试批量执行SQL查询"""
        self.connection.execute_batch.return_value = [
            {"affected_rows": 1, "last_insert_id": 1},
            {"affected_rows": 1, "last_insert_id": 2}
        ]
        params_list = [{'id': 1}, {'id': 2}]
        result = self.adapter.execute_batch("INSERT INTO test VALUES (:id)", params_list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {"affected_rows": 1, "last_insert_id": 1})
        self.assertEqual(result[1], {"affected_rows": 1, "last_insert_id": 2})
        self.connection.execute_batch.assert_called_with("INSERT INTO test VALUES (:id)", params_list)

    def test_execute_many(self):
        """测试执行多个SQL查询"""
        self.connection.execute_many.return_value = {"affected_rows": 2}
        params_list = [{'id': 1}, {'id': 2}]
        result = self.adapter.execute_many("INSERT INTO test VALUES (:id)", params_list)
        self.assertEqual(result, {"affected_rows": 2})
        self.connection.execute_many.assert_called_with("INSERT INTO test VALUES (:id)", params_list)

    def test_call_procedure(self):
        """测试调用存储过程"""
        self.adapter.execute_query = MagicMock(return_value=[('result',)])
        result = self.adapter.call_procedure('test_procedure', {'param': 'value'})
        self.assertEqual(result, [('result',)])

        # 测试不支持存储过程的数据库类型
        self.adapter.features['stored_procedures'] = False
        with self.assertRaises(NotImplementedError):
            self.adapter.call_procedure('test_procedure')

    def test_get_views(self):
        """测试获取数据库中的所有视图"""
        self.adapter.execute_query = MagicMock(return_value=[
            ('test_view', 'SELECT * FROM test', 'NONE', 'YES')
        ])
        result = self.adapter.get_views()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'test_view')
        self.assertEqual(result[0]['definition'], 'SELECT * FROM test')
        self.assertEqual(result[0]['check_option'], 'NONE')
        self.assertEqual(result[0]['is_updatable'], 'YES')

        # 测试不支持的数据库类型
        self.adapter.db_type = 'unsupported'
        with self.assertRaises(DatabaseError):
            self.adapter.get_views()

    def test_get_triggers(self):
        """测试获取数据库中的所有触发器"""
        self.adapter.execute_query = MagicMock(return_value=[
            ('test_trigger', 'test_table', 'BEFORE', 'INSERT', 'BEGIN SET NEW.created_at = NOW(); END')
        ])
        result = self.adapter.get_triggers()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'test_trigger')
        self.assertEqual(result[0]['table_name'], 'test_table')
        self.assertEqual(result[0]['timing'], 'BEFORE')
        self.assertEqual(result[0]['event'], 'INSERT')
        self.assertEqual(result[0]['definition'], 'BEGIN SET NEW.created_at = NOW(); END')

        # 测试不支持触发器的数据库类型
        self.adapter.features['triggers'] = False
        with self.assertRaises(NotImplementedError):
            self.adapter.get_triggers()

    def test_get_columns(self):
        """测试获取表的列信息"""
        # 测试MySQL
        self.adapter.db_type = 'mysql'
        self.adapter.execute_query = MagicMock(return_value=[
            ('id', 'int', 'int(11)', 'NO', None, 'Primary key', 'auto_increment'),
            ('name', 'varchar', 'varchar(255)', 'YES', None, 'User name', '')
        ])

        result = self.adapter._get_columns('test_table')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'id')
        self.assertEqual(result[0]['type'], 'int')
        self.assertEqual(result[0]['full_type'], 'int(11)')
        self.assertFalse(result[0]['nullable'])
        self.assertIsNone(result[0]['default'])
        self.assertEqual(result[0]['comment'], 'Primary key')
        self.assertEqual(result[0]['extra'], 'auto_increment')

        self.assertEqual(result[1]['name'], 'name')
        self.assertEqual(result[1]['type'], 'varchar')
        self.assertEqual(result[1]['full_type'], 'varchar(255)')
        self.assertTrue(result[1]['nullable'])
        self.assertIsNone(result[1]['default'])
        self.assertEqual(result[1]['comment'], 'User name')
        self.assertEqual(result[1]['extra'], '')

        # 测试PostgreSQL
        self.adapter.db_type = 'postgresql'
        self.adapter.execute_query = MagicMock(return_value=[
            ('id', 'integer', 'int4', 'NO', 'nextval(\'test_id_seq\'::regclass)', None, None),
            ('name', 'character varying', 'varchar', 'YES', None, None, None)
        ])

        result = self.adapter._get_columns('test_table')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'id')
        self.assertEqual(result[0]['type'], 'integer')
        self.assertEqual(result[0]['full_type'], 'int4')
        self.assertFalse(result[0]['nullable'])
        self.assertEqual(result[0]['default'], 'nextval(\'test_id_seq\'::regclass)')
        self.assertIsNone(result[0]['comment'])
        self.assertIsNone(result[0]['extra'])

        # 测试SQLite
        self.adapter.db_type = 'sqlite'
        self.adapter.execute_query = MagicMock(return_value=[
            (0, 'id', 'INTEGER', 0, None, 1),
            (1, 'name', 'TEXT', 1, None, 0)
        ])

        result = self.adapter._get_columns('test_table')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'id')
        self.assertEqual(result[0]['type'], 'INTEGER')
        self.assertEqual(result[0]['full_type'], 'INTEGER')
        self.assertTrue(result[0]['nullable'])
        self.assertIsNone(result[0]['default'])
        self.assertIsNone(result[0]['comment'])
        self.assertEqual(result[0]['extra'], 'PRIMARY KEY')

        self.assertEqual(result[1]['name'], 'name')
        self.assertEqual(result[1]['type'], 'TEXT')
        self.assertEqual(result[1]['full_type'], 'TEXT')
        self.assertFalse(result[1]['nullable'])
        self.assertIsNone(result[1]['default'])
        self.assertIsNone(result[1]['comment'])
        self.assertIsNone(result[1]['extra'])

        # 测试不支持的数据库类型
        self.adapter.db_type = 'unsupported'
        with self.assertRaises(DatabaseError):
            self.adapter._get_columns('test_table')

    def test_get_indexes(self):
        """测试获取表的索引信息"""
        # 测试MySQL
        self.adapter.db_type = 'mysql'
        self.adapter.execute_query = MagicMock(return_value=[
            ('PRIMARY', 'id', 0, 1),
            ('idx_name', 'name', 1, 1)
        ])

        result = self.adapter._get_indexes('test_table')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'PRIMARY')
        self.assertEqual(result[0]['columns'], ['id'])
        self.assertTrue(result[0]['unique'])

        self.assertEqual(result[1]['name'], 'idx_name')
        self.assertEqual(result[1]['columns'], ['name'])
        self.assertFalse(result[1]['unique'])

        # 测试PostgreSQL
        self.adapter.db_type = 'postgresql'
        self.adapter.execute_query = MagicMock(return_value=[
            ('test_pkey', 'id', 0, 1),
            ('idx_name', 'name', 1, 1)
        ])

        result = self.adapter._get_indexes('test_table')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'test_pkey')
        self.assertEqual(result[0]['columns'], ['id'])
        self.assertTrue(result[0]['unique'])

        # 测试SQLite
        self.adapter.db_type = 'sqlite'
        # 模拟PRAGMA index_list的返回值
        self.adapter.execute_query = MagicMock(side_effect=[
            # 第一次调用返回索引列表
            [(0, 'sqlite_autoindex_test_table_1', 1), (1, 'idx_name', 0)],
            # 第二次调用返回第一个索引的列信息
            [(0, 0, 'id')],
            # 第三次调用返回第二个索引的列信息
            [(0, 0, 'name')]
        ])

        result = self.adapter._get_indexes('test_table')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'sqlite_autoindex_test_table_1')
        self.assertEqual(result[0]['columns'], ['id'])
        self.assertTrue(result[0]['unique'])

        self.assertEqual(result[1]['name'], 'idx_name')
        self.assertEqual(result[1]['columns'], ['name'])
        self.assertFalse(result[1]['unique'])

        # 测试不支持的数据库类型
        self.adapter.db_type = 'unsupported'
        with self.assertRaises(DatabaseError):
            self.adapter._get_indexes('test_table')

    def test_get_foreign_keys(self):
        """测试获取表的外键信息"""
        # 测试MySQL
        self.adapter.db_type = 'mysql'
        self.adapter.execute_query = MagicMock(return_value=[
            ('fk_user_id', 'user_id', 'users', 'id')
        ])

        result = self.adapter._get_foreign_keys('test_table')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'fk_user_id')
        self.assertEqual(result[0]['columns'], ['user_id'])
        self.assertEqual(result[0]['referenced_table'], 'users')
        self.assertEqual(result[0]['referenced_columns'], ['id'])

        # 测试PostgreSQL
        self.adapter.db_type = 'postgresql'
        self.adapter.execute_query = MagicMock(return_value=[
            ('fk_user_id', 'user_id', 'users', 'id')
        ])

        result = self.adapter._get_foreign_keys('test_table')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'fk_user_id')
        self.assertEqual(result[0]['columns'], ['user_id'])
        self.assertEqual(result[0]['referenced_table'], 'users')
        self.assertEqual(result[0]['referenced_columns'], ['id'])

        # 测试SQLite
        self.adapter.db_type = 'sqlite'
        self.adapter.execute_query = MagicMock(return_value=[
            (0, 1, 'users', 'user_id', 'id', 'CASCADE', 'CASCADE', 'NONE')
        ])

        result = self.adapter._get_foreign_keys('test_table')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'fk_test_table_0')
        self.assertEqual(result[0]['columns'], ['user_id'])
        self.assertEqual(result[0]['referenced_table'], 'users')
        self.assertEqual(result[0]['referenced_columns'], ['id'])

        # 测试不支持的数据库类型
        self.adapter.db_type = 'unsupported'
        with self.assertRaises(DatabaseError):
            self.adapter._get_foreign_keys('test_table')


if __name__ == '__main__':
    unittest.main()
