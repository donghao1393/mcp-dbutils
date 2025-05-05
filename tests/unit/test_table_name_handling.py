"""测试表名处理逻辑，包括大小写敏感性和边界情况"""

from unittest.mock import MagicMock, patch

import pytest

from mcp_dbutils.base import ConfigurationError, ConnectionServer


class TestTableNameHandling:
    """测试表名处理逻辑"""

    @pytest.fixture
    def connection_server(self):
        """创建ConnectionServer实例用于测试"""
        with patch("builtins.open", MagicMock()), \
             patch("yaml.safe_load", return_value={"connections": {
                 "test_conn": {
                     "writable": True,
                     "write_permissions": {
                         "tables": {
                             "users": {"operations": ["INSERT", "UPDATE"]},
                             "PRODUCTS": {"operations": ["INSERT", "UPDATE", "DELETE"]},
                             "Orders": {"operations": ["INSERT"]},
                             "special_table$123": {"operations": ["INSERT"]},
                             "very_long_table_name_with_more_than_thirty_characters": {"operations": ["INSERT"]},
                         },
                         "default_policy": "read_only"
                     }
                 }
             }}):
            server = ConnectionServer("dummy_config.yaml")
            # 直接设置_get_config_or_raise方法的返回值
            server._get_config_or_raise = MagicMock(return_value={
                "writable": True,
                "write_permissions": {
                    "tables": {
                        "users": {"operations": ["INSERT", "UPDATE"]},
                        "PRODUCTS": {"operations": ["INSERT", "UPDATE", "DELETE"]},
                        "Orders": {"operations": ["INSERT"]},
                        "special_table$123": {"operations": ["INSERT"]},
                        "very_long_table_name_with_more_than_thirty_characters": {"operations": ["INSERT"]},
                    },
                    "default_policy": "read_only"
                }
            })
            return server

    @pytest.mark.asyncio
    async def test_table_name_case_sensitivity(self, connection_server):
        """测试表名大小写不敏感性"""
        # 配置中是小写"users"，SQL中使用大写"USERS"
        await connection_server._check_write_permission("test_conn", "USERS", "INSERT")
        await connection_server._check_write_permission("test_conn", "USERS", "UPDATE")

        with pytest.raises(ConfigurationError):
            await connection_server._check_write_permission("test_conn", "USERS", "DELETE")

        # 配置中是大写"PRODUCTS"，SQL中使用小写"products"
        await connection_server._check_write_permission("test_conn", "products", "INSERT")
        await connection_server._check_write_permission("test_conn", "products", "UPDATE")
        await connection_server._check_write_permission("test_conn", "products", "DELETE")

        # 配置中是首字母大写"Orders"，SQL中使用混合大小写"oRdErS"
        await connection_server._check_write_permission("test_conn", "oRdErS", "INSERT")

        with pytest.raises(ConfigurationError):
            await connection_server._check_write_permission("test_conn", "oRdErS", "UPDATE")

    @pytest.mark.asyncio
    async def test_special_characters_in_table_name(self, connection_server):
        """测试表名中的特殊字符"""
        # 表名包含特殊字符
        await connection_server._check_write_permission("test_conn", "special_table$123", "INSERT")

        with pytest.raises(ConfigurationError):
            await connection_server._check_write_permission("test_conn", "special_table$123", "UPDATE")

        # 表名大小写不敏感 + 特殊字符
        await connection_server._check_write_permission("test_conn", "SPECIAL_TABLE$123", "INSERT")

        with pytest.raises(ConfigurationError):
            await connection_server._check_write_permission("test_conn", "SPECIAL_TABLE$123", "UPDATE")

    @pytest.mark.asyncio
    async def test_long_table_name(self, connection_server):
        """测试长表名"""
        # 长表名
        await connection_server._check_write_permission(
            "test_conn",
            "very_long_table_name_with_more_than_thirty_characters",
            "INSERT"
        )

        with pytest.raises(ConfigurationError):
            await connection_server._check_write_permission(
                "test_conn",
                "very_long_table_name_with_more_than_thirty_characters",
                "UPDATE"
            )

        # 长表名 + 大小写不敏感
        await connection_server._check_write_permission(
            "test_conn",
            "VERY_LONG_TABLE_NAME_WITH_MORE_THAN_THIRTY_CHARACTERS",
            "INSERT"
        )

        with pytest.raises(ConfigurationError):
            await connection_server._check_write_permission(
                "test_conn",
                "VERY_LONG_TABLE_NAME_WITH_MORE_THAN_THIRTY_CHARACTERS",
                "UPDATE"
            )

    def test_extract_table_name_edge_cases(self):
        """测试_extract_table_name方法的边界情况"""
        with patch("builtins.open", MagicMock()), \
             patch("yaml.safe_load", return_value={"connections": {}}):
            server = ConnectionServer("dummy_config.yaml")

            # 测试不同SQL语句类型的表名提取
            assert server._extract_table_name("INSERT INTO users VALUES (1, 'test')") == "USERS"
            assert server._extract_table_name("UPDATE users SET name = 'test' WHERE id = 1") == "USERS"
            assert server._extract_table_name("DELETE FROM users WHERE id = 1") == "USERS"

            # 测试带引号的表名
            assert server._extract_table_name('INSERT INTO "users" VALUES (1, "test")') == "USERS"
            assert server._extract_table_name("INSERT INTO `users` VALUES (1, 'test')") == "USERS"
            assert server._extract_table_name("INSERT INTO [users] VALUES (1, 'test')") == "USERS"

            # 测试带模式的表名
            assert server._extract_table_name("INSERT INTO schema.users VALUES (1, 'test')") == "SCHEMA.USERS"
            assert server._extract_table_name("UPDATE public.users SET name = 'test'") == "PUBLIC.USERS"

            # 测试带空格和注释的SQL
            assert server._extract_table_name("INSERT INTO users -- comment\nVALUES (1, 'test')") == "USERS"
            assert server._extract_table_name("INSERT INTO\nusers\nVALUES (1, 'test')") == "USERS"

            # 测试复杂SQL
            complex_sql = """
            INSERT INTO users (id, name, email)
            SELECT id, name, email
            FROM temp_users
            WHERE active = 1
            """
            assert server._extract_table_name(complex_sql) == "USERS"

            # 测试无效SQL
            assert server._extract_table_name("SELECT * FROM users") == "unknown_table"
            assert server._extract_table_name("INVALID SQL") == "unknown_table"
