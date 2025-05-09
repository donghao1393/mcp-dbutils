"""
MongoDB查询构建器单元测试

这个模块包含MongoDB查询构建器的单元测试。
"""

import unittest

from mcp_dbutils.multi_db.error.exceptions import QueryError
from mcp_dbutils.multi_db.query.mongo import MongoQuery, MongoQueryBuilder


class TestMongoQuery(unittest.TestCase):
    """MongoDB查询单元测试类"""

    def test_init(self):
        """测试初始化"""
        # 创建查询
        query = MongoQuery("users", "find", {"filter": {"age": {"$gt": 18}}})

        # 验证结果
        self.assertEqual(query.collection, "users")
        self.assertEqual(query.operation, "find")
        self.assertEqual(query.params, {"filter": {"age": {"$gt": 18}}})

    def test_get_query_string(self):
        """测试获取查询字符串"""
        # 创建查询
        query = MongoQuery("users", "find", {"filter": {"age": {"$gt": 18}}})

        # 验证结果
        self.assertEqual(query.get_query_string(), "find on users")

    def test_get_params(self):
        """测试获取查询参数"""
        # 创建查询
        query = MongoQuery("users", "find", {"filter": {"age": {"$gt": 18}}})

        # 验证结果
        expected_params = {
            'collection': 'users',
            'operation': 'find',
            'params': {'filter': {'age': {'$gt': 18}}}
        }
        self.assertEqual(query.get_params(), expected_params)


class TestMongoQueryBuilder(unittest.TestCase):
    """MongoDB查询构建器单元测试类"""

    def setUp(self):
        """设置测试环境"""
        self.builder = MongoQueryBuilder()

    def test_select(self):
        """测试构建find查询"""
        # 构建查询
        builder = self.builder.select("users", ["name", "age"])

        # 验证结果
        self.assertEqual(builder.collection, "users")
        self.assertEqual(builder.operation, "find")
        self.assertEqual(builder.projection, {"name": 1, "age": 1})

        # 构建查询对象
        query = builder.build()

        # 验证查询对象
        self.assertEqual(query.collection, "users")
        self.assertEqual(query.operation, "find")
        self.assertEqual(query.params["projection"], {"name": 1, "age": 1})

    def test_insert(self):
        """测试构建insert_one查询"""
        # 构建查询
        data = {"name": "John", "age": 25}
        builder = self.builder.insert("users", data)

        # 验证结果
        self.assertEqual(builder.collection, "users")
        self.assertEqual(builder.operation, "insert_one")
        self.assertEqual(builder.document, data)

        # 构建查询对象
        query = builder.build()

        # 验证查询对象
        self.assertEqual(query.collection, "users")
        self.assertEqual(query.operation, "insert_one")
        self.assertEqual(query.params["document"], data)

    def test_insert_many(self):
        """测试构建insert_many查询"""
        # 构建查询
        data = [{"name": "John", "age": 25}, {"name": "Jane", "age": 30}]
        builder = self.builder.insert_many("users", data)

        # 验证结果
        self.assertEqual(builder.collection, "users")
        self.assertEqual(builder.operation, "insert_many")
        self.assertEqual(builder.documents, data)

        # 构建查询对象
        query = builder.build()

        # 验证查询对象
        self.assertEqual(query.collection, "users")
        self.assertEqual(query.operation, "insert_many")
        self.assertEqual(query.params["documents"], data)

    def test_update(self):
        """测试构建update_one查询"""
        # 构建查询
        data = {"name": "John", "age": 26}
        condition = {"name": "John", "age": 25}
        builder = self.builder.update("users", data, condition)

        # 验证结果
        self.assertEqual(builder.collection, "users")
        self.assertEqual(builder.operation, "update_one")
        self.assertEqual(builder.update_data, {"$set": data})
        self.assertEqual(builder.filter, condition)

        # 构建查询对象
        query = builder.build()

        # 验证查询对象
        self.assertEqual(query.collection, "users")
        self.assertEqual(query.operation, "update_one")
        self.assertEqual(query.params["update"], {"$set": data})
        self.assertEqual(query.params["filter"], condition)

    def test_update_with_operators(self):
        """测试构建带操作符的update_one查询"""
        # 构建查询
        data = {"$set": {"age": 26}, "$inc": {"count": 1}}
        condition = {"name": "John"}
        builder = self.builder.update("users", data, condition)

        # 验证结果
        self.assertEqual(builder.collection, "users")
        self.assertEqual(builder.operation, "update_one")
        self.assertEqual(builder.update_data, data)
        self.assertEqual(builder.filter, condition)

        # 构建查询对象
        query = builder.build()

        # 验证查询对象
        self.assertEqual(query.collection, "users")
        self.assertEqual(query.operation, "update_one")
        self.assertEqual(query.params["update"], data)
        self.assertEqual(query.params["filter"], condition)

    def test_update_many(self):
        """测试构建update_many查询"""
        # 构建查询
        data = {"age": 26}
        condition = {"age": 25}
        builder = self.builder.update_many("users", data, condition)

        # 验证结果
        self.assertEqual(builder.collection, "users")
        self.assertEqual(builder.operation, "update_many")
        self.assertEqual(builder.update_data, {"$set": data})
        self.assertEqual(builder.filter, condition)

        # 构建查询对象
        query = builder.build()

        # 验证查询对象
        self.assertEqual(query.collection, "users")
        self.assertEqual(query.operation, "update_many")
        self.assertEqual(query.params["update"], {"$set": data})
        self.assertEqual(query.params["filter"], condition)

    def test_delete(self):
        """测试构建delete_one查询"""
        # 构建查询
        condition = {"name": "John"}
        builder = self.builder.delete("users", condition)

        # 验证结果
        self.assertEqual(builder.collection, "users")
        self.assertEqual(builder.operation, "delete_one")
        self.assertEqual(builder.filter, condition)

        # 构建查询对象
        query = builder.build()

        # 验证查询对象
        self.assertEqual(query.collection, "users")
        self.assertEqual(query.operation, "delete_one")
        self.assertEqual(query.params["filter"], condition)

    def test_delete_many(self):
        """测试构建delete_many查询"""
        # 构建查询
        condition = {"age": 25}
        builder = self.builder.delete_many("users", condition)

        # 验证结果
        self.assertEqual(builder.collection, "users")
        self.assertEqual(builder.operation, "delete_many")
        self.assertEqual(builder.filter, condition)

        # 构建查询对象
        query = builder.build()

        # 验证查询对象
        self.assertEqual(query.collection, "users")
        self.assertEqual(query.operation, "delete_many")
        self.assertEqual(query.params["filter"], condition)

    def test_aggregate(self):
        """测试构建aggregate查询"""
        # 构建查询
        pipeline = [
            {"$match": {"age": {"$gt": 18}}},
            {"$group": {"_id": "$department", "count": {"$sum": 1}}}
        ]
        builder = self.builder.aggregate("users", pipeline)

        # 验证结果
        self.assertEqual(builder.collection, "users")
        self.assertEqual(builder.operation, "aggregate")
        self.assertEqual(builder.pipeline, pipeline)

        # 构建查询对象
        query = builder.build()

        # 验证查询对象
        self.assertEqual(query.collection, "users")
        self.assertEqual(query.operation, "aggregate")
        self.assertEqual(query.params["pipeline"], pipeline)

    def test_distinct(self):
        """测试构建distinct查询"""
        # 构建查询
        field = "department"
        condition = {"age": {"$gt": 18}}
        builder = self.builder.distinct("users", field, condition)

        # 验证结果
        self.assertEqual(builder.collection, "users")
        self.assertEqual(builder.operation, "distinct")
        self.assertEqual(builder.field, field)
        self.assertEqual(builder.filter, condition)

        # 构建查询对象
        query = builder.build()

        # 验证查询对象
        self.assertEqual(query.collection, "users")
        self.assertEqual(query.operation, "distinct")
        self.assertEqual(query.params["field"], field)
        self.assertEqual(query.params["filter"], condition)

    def test_count(self):
        """测试构建count_documents查询"""
        # 构建查询
        condition = {"age": {"$gt": 18}}
        builder = self.builder.count("users", condition)

        # 验证结果
        self.assertEqual(builder.collection, "users")
        self.assertEqual(builder.operation, "count_documents")
        self.assertEqual(builder.filter, condition)

        # 构建查询对象
        query = builder.build()

        # 验证查询对象
        self.assertEqual(query.collection, "users")
        self.assertEqual(query.operation, "count_documents")
        self.assertEqual(query.params["filter"], condition)

    def test_where(self):
        """测试添加过滤条件"""
        # 构建查询
        builder = self.builder.select("users").where({"age": {"$gt": 18}})

        # 验证结果
        self.assertEqual(builder.filter, {"age": {"$gt": 18}})

        # 添加更多条件
        builder.where({"department": "IT"})

        # 验证结果
        self.assertEqual(builder.filter, {"age": {"$gt": 18}, "department": "IT"})

        # 构建查询对象
        query = builder.build()

        # 验证查询对象
        self.assertEqual(query.params["filter"], {"age": {"$gt": 18}, "department": "IT"})

    def test_order_by(self):
        """测试添加排序"""
        # 构建查询
        builder = self.builder.select("users").order_by(["name", "-age"])

        # 验证结果
        self.assertEqual(builder.sort_fields, [("name", 1), ("age", -1)])

        # 构建查询对象
        query = builder.build()

        # 验证查询对象
        self.assertEqual(query.params["sort"], [("name", 1), ("age", -1)])

    def test_limit(self):
        """测试添加限制"""
        # 构建查询
        builder = self.builder.select("users").limit(10)

        # 验证结果
        self.assertEqual(builder.limit_count, 10)

        # 构建查询对象
        query = builder.build()

        # 验证查询对象
        self.assertEqual(query.params["limit"], 10)

    def test_offset(self):
        """测试添加偏移"""
        # 构建查询
        builder = self.builder.select("users").offset(5)

        # 验证结果
        self.assertEqual(builder.skip_count, 5)

        # 构建查询对象
        query = builder.build()

        # 验证查询对象
        self.assertEqual(query.params["skip"], 5)

    def test_upsert_option(self):
        """测试设置upsert选项"""
        # 构建查询
        builder = self.builder.update("users", {"name": "John"}).upsert_option(True)

        # 验证结果
        self.assertTrue(builder.upsert)

        # 构建查询对象
        query = builder.build()

        # 验证查询对象
        self.assertTrue(query.params["upsert"])

    def test_build_without_required_fields(self):
        """测试缺少必要字段时构建查询"""
        # 没有设置集合名
        builder = MongoQueryBuilder()

        # 验证异常
        with self.assertRaises(QueryError) as context:
            builder.build()

        self.assertIn("Collection name and operation are required", str(context.exception))

        # 设置集合名但没有设置操作类型
        builder = MongoQueryBuilder()
        builder.collection = "users"

        # 验证异常
        with self.assertRaises(QueryError) as context:
            builder.build()

        self.assertIn("Collection name and operation are required", str(context.exception))


if __name__ == '__main__':
    unittest.main()