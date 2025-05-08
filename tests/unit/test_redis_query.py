"""
Redis命令构建器单元测试

这个模块包含Redis命令构建器的单元测试。
"""

import unittest

from mcp_dbutils.multi_db.error.exceptions import QueryError
from mcp_dbutils.multi_db.query.redis import RedisCommand, RedisCommandBuilder


class TestRedisCommand(unittest.TestCase):
    """Redis命令单元测试类"""

    def test_init(self):
        """测试初始化"""
        # 创建命令
        command = RedisCommand("GET", "user:1")

        # 验证结果
        self.assertEqual(command.command, "GET")
        self.assertEqual(command.key, "user:1")
        self.assertEqual(command.args, [])

        # 创建带参数的命令
        command = RedisCommand("HGET", "user:1", ["name"])

        # 验证结果
        self.assertEqual(command.command, "HGET")
        self.assertEqual(command.key, "user:1")
        self.assertEqual(command.args, ["name"])

    def test_get_query_string(self):
        """测试获取命令字符串"""
        # 创建命令
        command = RedisCommand("GET", "user:1")

        # 验证结果
        self.assertEqual(command.get_query_string(), "GET user:1")

        # 创建带参数的命令
        command = RedisCommand("HGET", "user:1", ["name"])

        # 验证结果
        self.assertEqual(command.get_query_string(), "HGET user:1 name")

        # 创建带多个参数的命令
        command = RedisCommand("HMGET", "user:1", ["name", "age"])

        # 验证结果
        self.assertEqual(command.get_query_string(), "HMGET user:1 name age")

    def test_get_params(self):
        """测试获取命令参数"""
        # 创建命令
        command = RedisCommand("GET", "user:1")

        # 验证结果
        self.assertEqual(command.get_params(), ["user:1"])

        # 创建带参数的命令
        command = RedisCommand("HGET", "user:1", ["name"])

        # 验证结果
        self.assertEqual(command.get_params(), ["user:1", "name"])

        # 创建带多个参数的命令
        command = RedisCommand("HMGET", "user:1", ["name", "age"])

        # 验证结果
        self.assertEqual(command.get_params(), ["user:1", "name", "age"])


class TestRedisCommandBuilder(unittest.TestCase):
    """Redis命令构建器单元测试类"""

    def setUp(self):
        """设置测试环境"""
        self.builder = RedisCommandBuilder()

    def test_select(self):
        """测试构建GET命令"""
        # 构建命令
        builder = self.builder.select("user:1")

        # 验证结果
        self.assertEqual(builder.command, "GET")
        self.assertEqual(builder.key, "user:1")
        self.assertEqual(builder.args, [])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "GET")
        self.assertEqual(command.key, "user:1")
        self.assertEqual(command.args, [])
        self.assertEqual(command.get_query_string(), "GET user:1")

    def test_select_with_fields(self):
        """测试构建HMGET命令"""
        # 构建命令
        builder = self.builder.select("user:1", ["name", "age"])

        # 验证结果
        self.assertEqual(builder.command, "HMGET")
        self.assertEqual(builder.key, "user:1")
        self.assertEqual(builder.args, ["name", "age"])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "HMGET")
        self.assertEqual(command.key, "user:1")
        self.assertEqual(command.args, ["name", "age"])
        self.assertEqual(command.get_query_string(), "HMGET user:1 name age")

    def test_hgetall(self):
        """测试构建HGETALL命令"""
        # 构建命令
        builder = self.builder.hgetall("user:1")

        # 验证结果
        self.assertEqual(builder.command, "HGETALL")
        self.assertEqual(builder.key, "user:1")
        self.assertEqual(builder.args, [])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "HGETALL")
        self.assertEqual(command.key, "user:1")
        self.assertEqual(command.args, [])
        self.assertEqual(command.get_query_string(), "HGETALL user:1")

    def test_lrange(self):
        """测试构建LRANGE命令"""
        # 构建命令
        builder = self.builder.lrange("list:1", 0, 10)

        # 验证结果
        self.assertEqual(builder.command, "LRANGE")
        self.assertEqual(builder.key, "list:1")
        self.assertEqual(builder.args, [0, 10])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "LRANGE")
        self.assertEqual(command.key, "list:1")
        self.assertEqual(command.args, [0, 10])
        self.assertEqual(command.get_query_string(), "LRANGE list:1 0 10")

    def test_smembers(self):
        """测试构建SMEMBERS命令"""
        # 构建命令
        builder = self.builder.smembers("set:1")

        # 验证结果
        self.assertEqual(builder.command, "SMEMBERS")
        self.assertEqual(builder.key, "set:1")
        self.assertEqual(builder.args, [])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "SMEMBERS")
        self.assertEqual(command.key, "set:1")
        self.assertEqual(command.args, [])
        self.assertEqual(command.get_query_string(), "SMEMBERS set:1")

    def test_zrange(self):
        """测试构建ZRANGE命令"""
        # 构建命令
        builder = self.builder.zrange("zset:1", 0, 10, True)

        # 验证结果
        self.assertEqual(builder.command, "ZRANGE")
        self.assertEqual(builder.key, "zset:1")
        self.assertEqual(builder.args, [0, 10, "WITHSCORES"])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "ZRANGE")
        self.assertEqual(command.key, "zset:1")
        self.assertEqual(command.args, [0, 10, "WITHSCORES"])
        self.assertEqual(command.get_query_string(), "ZRANGE zset:1 0 10 WITHSCORES")

    def test_insert(self):
        """测试构建SET命令"""
        # 构建命令
        builder = self.builder.insert("user:1", "John")

        # 验证结果
        self.assertEqual(builder.command, "SET")
        self.assertEqual(builder.key, "user:1")
        self.assertEqual(builder.args, ["John"])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "SET")
        self.assertEqual(command.key, "user:1")
        self.assertEqual(command.args, ["John"])
        self.assertEqual(command.get_query_string(), "SET user:1 John")

    def test_insert_dict(self):
        """测试构建HMSET命令"""
        # 构建命令
        data = {"name": "John", "age": 25}
        builder = self.builder.insert("user:1", data)

        # 验证结果
        self.assertEqual(builder.command, "HMSET")
        self.assertEqual(builder.key, "user:1")
        self.assertEqual(builder.args, ["name", "John", "age", 25])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "HMSET")
        self.assertEqual(command.key, "user:1")
        self.assertEqual(command.args, ["name", "John", "age", 25])
        self.assertEqual(command.get_query_string(), "HMSET user:1 name John age 25")

    def test_setex(self):
        """测试构建SETEX命令"""
        # 构建命令
        builder = self.builder.setex("user:1", "John", 3600)

        # 验证结果
        self.assertEqual(builder.command, "SETEX")
        self.assertEqual(builder.key, "user:1")
        self.assertEqual(builder.args, [3600, "John"])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "SETEX")
        self.assertEqual(command.key, "user:1")
        self.assertEqual(command.args, [3600, "John"])
        self.assertEqual(command.get_query_string(), "SETEX user:1 3600 John")

    def test_lpush(self):
        """测试构建LPUSH命令"""
        # 构建命令
        builder = self.builder.lpush("list:1", "item1", "item2", "item3")

        # 验证结果
        self.assertEqual(builder.command, "LPUSH")
        self.assertEqual(builder.key, "list:1")
        self.assertEqual(builder.args, ["item1", "item2", "item3"])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "LPUSH")
        self.assertEqual(command.key, "list:1")
        self.assertEqual(command.args, ["item1", "item2", "item3"])
        self.assertEqual(command.get_query_string(), "LPUSH list:1 item1 item2 item3")

    def test_rpush(self):
        """测试构建RPUSH命令"""
        # 构建命令
        builder = self.builder.rpush("list:1", "item1", "item2", "item3")

        # 验证结果
        self.assertEqual(builder.command, "RPUSH")
        self.assertEqual(builder.key, "list:1")
        self.assertEqual(builder.args, ["item1", "item2", "item3"])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "RPUSH")
        self.assertEqual(command.key, "list:1")
        self.assertEqual(command.args, ["item1", "item2", "item3"])
        self.assertEqual(command.get_query_string(), "RPUSH list:1 item1 item2 item3")

    def test_sadd(self):
        """测试构建SADD命令"""
        # 构建命令
        builder = self.builder.sadd("set:1", "member1", "member2", "member3")

        # 验证结果
        self.assertEqual(builder.command, "SADD")
        self.assertEqual(builder.key, "set:1")
        self.assertEqual(builder.args, ["member1", "member2", "member3"])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "SADD")
        self.assertEqual(command.key, "set:1")
        self.assertEqual(command.args, ["member1", "member2", "member3"])
        self.assertEqual(command.get_query_string(), "SADD set:1 member1 member2 member3")

    def test_zadd(self):
        """测试构建ZADD命令"""
        # 构建命令
        builder = self.builder.zadd("zset:1", 1, "member1", 2, "member2", 3, "member3")

        # 验证结果
        self.assertEqual(builder.command, "ZADD")
        self.assertEqual(builder.key, "zset:1")
        self.assertEqual(builder.args, [1, "member1", 2, "member2", 3, "member3"])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "ZADD")
        self.assertEqual(command.key, "zset:1")
        self.assertEqual(command.args, [1, "member1", 2, "member2", 3, "member3"])
        self.assertEqual(command.get_query_string(), "ZADD zset:1 1 member1 2 member2 3 member3")

    def test_update(self):
        """测试构建SET命令（通过update方法）"""
        # 构建命令
        builder = self.builder.update("user:1", "John")

        # 验证结果
        self.assertEqual(builder.command, "SET")
        self.assertEqual(builder.key, "user:1")
        self.assertEqual(builder.args, ["John"])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "SET")
        self.assertEqual(command.key, "user:1")
        self.assertEqual(command.args, ["John"])
        self.assertEqual(command.get_query_string(), "SET user:1 John")

    def test_delete(self):
        """测试构建DEL命令"""
        # 构建命令
        builder = self.builder.delete("user:1")

        # 验证结果
        self.assertEqual(builder.command, "DEL")
        self.assertEqual(builder.key, "user:1")
        self.assertEqual(builder.args, [])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "DEL")
        self.assertEqual(command.key, "user:1")
        self.assertEqual(command.args, [])
        self.assertEqual(command.get_query_string(), "DEL user:1")

    def test_expire(self):
        """测试构建EXPIRE命令"""
        # 构建命令
        builder = self.builder.expire("user:1", 3600)

        # 验证结果
        self.assertEqual(builder.command, "EXPIRE")
        self.assertEqual(builder.key, "user:1")
        self.assertEqual(builder.args, [3600])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "EXPIRE")
        self.assertEqual(command.key, "user:1")
        self.assertEqual(command.args, [3600])
        self.assertEqual(command.get_query_string(), "EXPIRE user:1 3600")

    def test_where(self):
        """测试where方法（Redis不支持条件查询）"""
        # 构建命令
        builder = self.builder.select("user:1").where({"name": "John"})

        # 验证结果
        self.assertEqual(builder.command, "GET")
        self.assertEqual(builder.key, "user:1")
        self.assertEqual(builder.args, [])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "GET")
        self.assertEqual(command.key, "user:1")
        self.assertEqual(command.args, [])
        self.assertEqual(command.get_query_string(), "GET user:1")

    def test_order_by(self):
        """测试order_by方法（Redis不支持排序查询）"""
        # 构建命令
        builder = self.builder.select("user:1").order_by(["name", "age"])

        # 验证结果
        self.assertEqual(builder.command, "GET")
        self.assertEqual(builder.key, "user:1")
        self.assertEqual(builder.args, [])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "GET")
        self.assertEqual(command.key, "user:1")
        self.assertEqual(command.args, [])
        self.assertEqual(command.get_query_string(), "GET user:1")

    def test_limit(self):
        """测试limit方法（Redis不支持限制查询）"""
        # 构建命令
        builder = self.builder.select("user:1").limit(10)

        # 验证结果
        self.assertEqual(builder.command, "GET")
        self.assertEqual(builder.key, "user:1")
        self.assertEqual(builder.args, [])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "GET")
        self.assertEqual(command.key, "user:1")
        self.assertEqual(command.args, [])
        self.assertEqual(command.get_query_string(), "GET user:1")

    def test_offset(self):
        """测试offset方法（Redis不支持偏移查询）"""
        # 构建命令
        builder = self.builder.select("user:1").offset(5)

        # 验证结果
        self.assertEqual(builder.command, "GET")
        self.assertEqual(builder.key, "user:1")
        self.assertEqual(builder.args, [])

        # 构建命令对象
        command = builder.build()

        # 验证命令对象
        self.assertEqual(command.command, "GET")
        self.assertEqual(command.key, "user:1")
        self.assertEqual(command.args, [])
        self.assertEqual(command.get_query_string(), "GET user:1")

    def test_build_without_command(self):
        """测试缺少命令时构建命令"""
        # 没有设置命令
        builder = RedisCommandBuilder()

        # 验证异常
        with self.assertRaises(QueryError) as context:
            builder.build()

        self.assertIn("Command is required", str(context.exception))


if __name__ == '__main__':
    unittest.main()