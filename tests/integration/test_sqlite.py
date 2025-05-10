import os
import tempfile


# 检查是否跳过数据库测试
skip_db_tests = os.environ.get("SKIP_DB_TESTS", "false").lower() == "true"
skip_reason = "Database tests are skipped in CI environment"

import pytest
import yaml

from mcp_dbutils.base import (
    ConnectionHandlerError,
    ConnectionServer,
)


@pytest.mark.asyncio
@pytest.mark.skipif(skip_db_tests, reason=skip_reason)
async def test_list_tables(sqlite_db, mcp_config):
    """Test listing tables in SQLite database"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_sqlite") as handler:
            tables = await handler.get_tables()
            table_names = [table.name.replace(" schema", "") for table in tables]
            assert "products" in table_names

            # Check schema information
            schema_str = await handler.get_schema("products")
            schema = eval(schema_str)
            assert schema["columns"][0]["name"] == "id"
            assert schema["columns"][0]["type"] == "INTEGER"
            assert schema["columns"][1]["name"] == "name"
            assert schema["columns"][1]["type"] == "TEXT" 
            assert schema["columns"][2]["name"] == "price"
            assert schema["columns"][2]["type"] == "REAL"
            assert schema["columns"][0]["primary_key"] is True

@pytest.mark.asyncio
@pytest.mark.skipif(skip_db_tests, reason=skip_reason)
async def test_execute_query(sqlite_db, mcp_config):
    """Test executing SELECT queries"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_sqlite") as handler:
                # Simple SELECT
                result_str = await handler.execute_query("SELECT name FROM products ORDER BY price")
                result = eval(result_str)
                assert len(result["rows"]) == 2
                assert result["rows"][0]["name"] == "Widget"  # $9.99
                assert result["rows"][1]["name"] == "Gadget"  # $19.99

                # SELECT with WHERE clause
                result_str = await handler.execute_query(
                    "SELECT * FROM products WHERE price < 10.00"
                )
                result = eval(result_str)
                assert len(result["rows"]) == 1
                assert result["rows"][0]["name"] == "Widget"
                assert float(result["rows"][0]["price"]) == 9.99

@pytest.mark.asyncio
@pytest.mark.skipif(skip_db_tests, reason=skip_reason)
async def test_non_select_query(sqlite_db, mcp_config):
    """Test executing non-SELECT queries"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_sqlite") as handler:
            # 我们现在允许非SELECT查询
            result = await handler.execute_query("DELETE FROM products")
            assert result == "Query executed successfully"

@pytest.mark.asyncio
@pytest.mark.skipif(skip_db_tests, reason=skip_reason)
async def test_invalid_query(sqlite_db, mcp_config):
    """Test handling of invalid SQL queries"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_sqlite") as handler:
            with pytest.raises(ConnectionHandlerError):
                await handler.execute_query("SELECT * FROM nonexistent_table")

@pytest.mark.asyncio
@pytest.mark.skipif(skip_db_tests, reason=skip_reason)
async def test_connection_cleanup(sqlite_db, mcp_config):
    """Test that database connections are properly cleaned up"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_sqlite") as handler:
            await handler.get_tables()
