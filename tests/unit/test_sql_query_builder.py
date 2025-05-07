"""
SQLQueryBuilder类的单元测试
"""

import unittest

from mcp_dbutils.multi_db.query.sql import (
    SQLQuery,
    SQLQueryBuilder,
    Operator,
    Condition,
    JoinType,
    Join,
)
from mcp_dbutils.multi_db.error.exceptions import QueryError


class TestSQLQuery(unittest.TestCase):
    """SQLQuery类的测试用例"""

    def test_init(self):
        """测试初始化"""
        query = SQLQuery("SELECT * FROM test", {"param": "value"})
        self.assertEqual(query.query, "SELECT * FROM test")
        self.assertEqual(query.params, {"param": "value"})

        # 测试默认参数
        query = SQLQuery("SELECT * FROM test")
        self.assertEqual(query.params, {})

    def test_get_query_string(self):
        """测试获取查询字符串"""
        query = SQLQuery("SELECT * FROM test")
        self.assertEqual(query.get_query_string(), "SELECT * FROM test")

    def test_get_params(self):
        """测试获取查询参数"""
        query = SQLQuery("SELECT * FROM test", {"param": "value"})
        self.assertEqual(query.get_params(), {"param": "value"})


class TestOperator(unittest.TestCase):
    """Operator枚举的测试用例"""

    def test_operators(self):
        """测试操作符枚举值"""
        self.assertEqual(Operator.EQ.value, "=")
        self.assertEqual(Operator.NE.value, "<>")
        self.assertEqual(Operator.GT.value, ">")
        self.assertEqual(Operator.GE.value, ">=")
        self.assertEqual(Operator.LT.value, "<")
        self.assertEqual(Operator.LE.value, "<=")
        self.assertEqual(Operator.IN.value, "IN")
        self.assertEqual(Operator.NOT_IN.value, "NOT IN")
        self.assertEqual(Operator.LIKE.value, "LIKE")
        self.assertEqual(Operator.NOT_LIKE.value, "NOT LIKE")
        self.assertEqual(Operator.BETWEEN.value, "BETWEEN")
        self.assertEqual(Operator.NOT_BETWEEN.value, "NOT BETWEEN")
        self.assertEqual(Operator.IS_NULL.value, "IS NULL")
        self.assertEqual(Operator.IS_NOT_NULL.value, "IS NOT NULL")


class TestCondition(unittest.TestCase):
    """Condition类的测试用例"""

    def test_init(self):
        """测试初始化"""
        condition = Condition("id", Operator.EQ, 1)
        self.assertEqual(condition.field, "id")
        self.assertEqual(condition.operator, Operator.EQ)
        self.assertEqual(condition.value, 1)

    def test_str(self):
        """测试字符串表示"""
        condition = Condition("id", Operator.EQ, 1)
        self.assertEqual(str(condition), "id = 1")


class TestJoinType(unittest.TestCase):
    """JoinType枚举的测试用例"""

    def test_join_types(self):
        """测试JOIN类型枚举值"""
        self.assertEqual(JoinType.INNER.value, "INNER JOIN")
        self.assertEqual(JoinType.LEFT.value, "LEFT JOIN")
        self.assertEqual(JoinType.RIGHT.value, "RIGHT JOIN")
        self.assertEqual(JoinType.FULL.value, "FULL JOIN")
        self.assertEqual(JoinType.CROSS.value, "CROSS JOIN")


class TestJoin(unittest.TestCase):
    """Join类的测试用例"""

    def test_init(self):
        """测试初始化"""
        join = Join("orders", JoinType.INNER, "orders.customer_id = customers.id")
        self.assertEqual(join.table, "orders")
        self.assertEqual(join.join_type, JoinType.INNER)
        self.assertEqual(join.on_condition, "orders.customer_id = customers.id")

    def test_str(self):
        """测试字符串表示"""
        join = Join("orders", JoinType.INNER, "orders.customer_id = customers.id")
        self.assertEqual(str(join), "INNER JOIN orders ON orders.customer_id = customers.id")


class TestSQLQueryBuilder(unittest.TestCase):
    """SQLQueryBuilder类的测试用例"""

    def setUp(self):
        """测试前的准备工作"""
        self.builder = SQLQueryBuilder('mysql')

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.builder.db_type, 'mysql')
        self.assertIsNone(self.builder.query_type)
        self.assertIsNone(self.builder.resource_name)
        self.assertIsNone(self.builder.fields)
        self.assertIsNone(self.builder.data)
        self.assertIsNone(self.builder.conditions)
        self.assertIsNone(self.builder.order_fields)
        self.assertIsNone(self.builder.limit_count)
        self.assertIsNone(self.builder.offset_count)
        self.assertEqual(self.builder.joins, [])
        self.assertIsNone(self.builder.group_by_fields)
        self.assertIsNone(self.builder.having_conditions)
        self.assertEqual(self.builder.complex_conditions, [])
        self.assertEqual(self.builder.subqueries, {})

    def test_select(self):
        """测试SELECT查询构建"""
        builder = self.builder.select('customers', ['id', 'name'])
        self.assertEqual(builder.query_type, 'SELECT')
        self.assertEqual(builder.resource_name, 'customers')
        self.assertEqual(builder.fields, ['id', 'name'])
        self.assertIs(builder, self.builder)  # 确保返回的是同一个实例

    def test_insert(self):
        """测试INSERT查询构建"""
        data = {'id': 1, 'name': 'John'}
        builder = self.builder.insert('customers', data)
        self.assertEqual(builder.query_type, 'INSERT')
        self.assertEqual(builder.resource_name, 'customers')
        self.assertEqual(builder.data, data)
        self.assertIs(builder, self.builder)

    def test_update(self):
        """测试UPDATE查询构建"""
        data = {'name': 'John'}
        condition = {'id': 1}
        builder = self.builder.update('customers', data, condition)
        self.assertEqual(builder.query_type, 'UPDATE')
        self.assertEqual(builder.resource_name, 'customers')
        self.assertEqual(builder.data, data)
        self.assertEqual(builder.conditions, condition)
        self.assertIs(builder, self.builder)

    def test_delete(self):
        """测试DELETE查询构建"""
        condition = {'id': 1}
        builder = self.builder.delete('customers', condition)
        self.assertEqual(builder.query_type, 'DELETE')
        self.assertEqual(builder.resource_name, 'customers')
        self.assertEqual(builder.conditions, condition)
        self.assertIs(builder, self.builder)

    def test_where(self):
        """测试WHERE条件"""
        condition = {'id': 1}
        builder = self.builder.where(condition)
        self.assertEqual(builder.conditions, condition)
        self.assertIs(builder, self.builder)

    def test_order_by(self):
        """测试ORDER BY子句"""
        fields = ['name', 'id']
        builder = self.builder.order_by(fields)
        self.assertEqual(builder.order_fields, fields)
        self.assertIs(builder, self.builder)

    def test_limit(self):
        """测试LIMIT子句"""
        builder = self.builder.limit(10)
        self.assertEqual(builder.limit_count, 10)
        self.assertIs(builder, self.builder)

    def test_offset(self):
        """测试OFFSET子句"""
        builder = self.builder.offset(20)
        self.assertEqual(builder.offset_count, 20)
        self.assertIs(builder, self.builder)

    def test_join(self):
        """测试JOIN子句"""
        builder = self.builder.join('orders', JoinType.INNER, 'orders.customer_id = customers.id')
        self.assertEqual(len(builder.joins), 1)
        self.assertEqual(builder.joins[0].table, 'orders')
        self.assertEqual(builder.joins[0].join_type, JoinType.INNER)
        self.assertEqual(builder.joins[0].on_condition, 'orders.customer_id = customers.id')
        self.assertIs(builder, self.builder)

    def test_inner_join(self):
        """测试INNER JOIN子句"""
        builder = self.builder.inner_join('orders', 'orders.customer_id = customers.id')
        self.assertEqual(len(builder.joins), 1)
        self.assertEqual(builder.joins[0].join_type, JoinType.INNER)
        self.assertIs(builder, self.builder)

    def test_left_join(self):
        """测试LEFT JOIN子句"""
        builder = self.builder.left_join('orders', 'orders.customer_id = customers.id')
        self.assertEqual(len(builder.joins), 1)
        self.assertEqual(builder.joins[0].join_type, JoinType.LEFT)
        self.assertIs(builder, self.builder)

    def test_right_join(self):
        """测试RIGHT JOIN子句"""
        builder = self.builder.right_join('orders', 'orders.customer_id = customers.id')
        self.assertEqual(len(builder.joins), 1)
        self.assertEqual(builder.joins[0].join_type, JoinType.RIGHT)
        self.assertIs(builder, self.builder)

    def test_full_join(self):
        """测试FULL JOIN子句"""
        builder = self.builder.full_join('orders', 'orders.customer_id = customers.id')
        self.assertEqual(len(builder.joins), 1)
        self.assertEqual(builder.joins[0].join_type, JoinType.FULL)
        self.assertIs(builder, self.builder)

    def test_cross_join(self):
        """测试CROSS JOIN子句"""
        builder = self.builder.cross_join('orders')
        self.assertEqual(len(builder.joins), 1)
        self.assertEqual(builder.joins[0].join_type, JoinType.CROSS)
        self.assertEqual(builder.joins[0].on_condition, '1=1')
        self.assertIs(builder, self.builder)

    def test_group_by(self):
        """测试GROUP BY子句"""
        fields = ['category', 'status']
        builder = self.builder.group_by(fields)
        self.assertEqual(builder.group_by_fields, fields)
        self.assertIs(builder, self.builder)

    def test_having(self):
        """测试HAVING子句"""
        conditions = {'count': 10}
        builder = self.builder.having(conditions)
        self.assertEqual(builder.having_conditions, conditions)
        self.assertIs(builder, self.builder)

    def test_add_condition(self):
        """测试添加复杂条件"""
        builder = self.builder.add_condition('age', Operator.GT, 18)
        self.assertEqual(len(builder.complex_conditions), 1)
        self.assertEqual(builder.complex_conditions[0].field, 'age')
        self.assertEqual(builder.complex_conditions[0].operator, Operator.GT)
        self.assertEqual(builder.complex_conditions[0].value, 18)
        self.assertIs(builder, self.builder)

    def test_add_subquery(self):
        """测试添加子查询"""
        subquery = SQLQueryBuilder('mysql').select('orders')
        builder = self.builder.add_subquery('recent_orders', subquery)
        self.assertEqual(len(builder.subqueries), 1)
        self.assertEqual(builder.subqueries['recent_orders'], subquery)
        self.assertIs(builder, self.builder)

    def test_build_select(self):
        """测试构建SELECT查询"""
        query = self.builder.select('customers', ['id', 'name']).build()
        self.assertEqual(query.get_query_string(), "SELECT `id`, `name` FROM `customers`")
        self.assertEqual(query.get_params(), {})

    def test_build_select_with_where(self):
        """测试构建带WHERE条件的SELECT查询"""
        query = self.builder.select('customers').where({'id': 1}).build()
        self.assertEqual(query.get_query_string(), "SELECT * FROM `customers` WHERE `id` = :where_param_0")
        self.assertEqual(query.get_params(), {'where_param_0': 1})

    def test_build_select_with_complex_conditions(self):
        """测试构建带复杂条件的SELECT查询"""
        query = self.builder.select('customers').add_condition('age', Operator.GT, 18).build()
        self.assertEqual(query.get_query_string(), "SELECT * FROM `customers` WHERE `age` > :complex_param_0")
        self.assertEqual(query.get_params(), {'complex_param_0': 18})

    def test_build_select_with_join(self):
        """测试构建带JOIN的SELECT查询"""
        query = self.builder.select('customers').inner_join('orders', 'orders.customer_id = customers.id').build()
        self.assertEqual(query.get_query_string(), "SELECT * FROM `customers` INNER JOIN `orders` ON orders.customer_id = customers.id")
        self.assertEqual(query.get_params(), {})

    def test_build_select_with_group_by(self):
        """测试构建带GROUP BY的SELECT查询"""
        query = self.builder.select('orders', ['status', 'COUNT(*) as count']).group_by(['status']).build()
        self.assertEqual(query.get_query_string(), "SELECT `status`, `COUNT(*) as count` FROM `orders` GROUP BY `status`")
        self.assertEqual(query.get_params(), {})

    def test_build_select_with_having(self):
        """测试构建带HAVING的SELECT查询"""
        query = self.builder.select('orders', ['status', 'COUNT(*) as count']).group_by(['status']).having({'count': 10}).build()
        self.assertEqual(query.get_query_string(), "SELECT `status`, `COUNT(*) as count` FROM `orders` GROUP BY `status` HAVING `count` = :where_param_0")
        self.assertEqual(query.get_params(), {'where_param_0': 10})

    def test_build_select_with_order_by(self):
        """测试构建带ORDER BY的SELECT查询"""
        query = self.builder.select('customers').order_by(['name', 'id']).build()
        self.assertEqual(query.get_query_string(), "SELECT * FROM `customers` ORDER BY `name`, `id`")
        self.assertEqual(query.get_params(), {})

    def test_build_select_with_limit_offset(self):
        """测试构建带LIMIT和OFFSET的SELECT查询"""
        query = self.builder.select('customers').limit(10).offset(20).build()
        self.assertEqual(query.get_query_string(), "SELECT * FROM `customers` LIMIT 10 OFFSET 20")
        self.assertEqual(query.get_params(), {})

    def test_build_insert(self):
        """测试构建INSERT查询"""
        query = self.builder.insert('customers', {'id': 1, 'name': 'John'}).build()
        self.assertEqual(query.get_query_string(), "INSERT INTO `customers` (`id`, `name`) VALUES (:param_0, :param_1)")
        self.assertEqual(query.get_params(), {'param_0': 1, 'param_1': 'John'})

    def test_build_update(self):
        """测试构建UPDATE查询"""
        query = self.builder.update('customers', {'name': 'John'}, {'id': 1}).build()
        self.assertEqual(query.get_query_string(), "UPDATE `customers` SET `name` = :param_0 WHERE `id` = :where_param_0")
        self.assertEqual(query.get_params(), {'param_0': 'John', 'where_param_0': 1})

    def test_build_delete(self):
        """测试构建DELETE查询"""
        query = self.builder.delete('customers', {'id': 1}).build()
        self.assertEqual(query.get_query_string(), "DELETE FROM `customers` WHERE `id` = :where_param_0")
        self.assertEqual(query.get_params(), {'where_param_0': 1})

    def test_build_error(self):
        """测试构建查询时的错误处理"""
        # 缺少查询类型和资源名称
        with self.assertRaises(QueryError):
            self.builder.build()

        # 不支持的查询类型
        self.builder.query_type = 'UNSUPPORTED'
        self.builder.resource_name = 'customers'
        with self.assertRaises(QueryError):
            self.builder.build()

        # INSERT查询缺少数据
        self.builder.query_type = 'INSERT'
        with self.assertRaises(QueryError):
            self.builder.build()

        # UPDATE查询缺少数据
        self.builder.query_type = 'UPDATE'
        with self.assertRaises(QueryError):
            self.builder.build()


if __name__ == '__main__':
    unittest.main()
