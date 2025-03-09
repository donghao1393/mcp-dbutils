import pytest
import tempfile
import yaml
from mcp_dbutils.base import ConnectionServer, ConfigurationError, ConnectionHandlerError
from mcp_dbutils.log import create_logger

# 创建测试用的 logger
logger = create_logger("test-postgres", True)  # debug=True 以显示所有日志

@pytest.mark.asyncio
async def test_list_tables(postgres_db, mcp_config):
    """Test listing tables in PostgreSQL database"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        config_data = mcp_config
        logger("debug", f"PostgreSQL config: {config_data}")
        yaml.dump(config_data, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_pg") as handler:
            tables = await handler.get_tables()
            table_names = [table.name.replace(" schema", "") for table in tables]
            assert "users" in table_names

            # Check schema information
            schema_str = await handler.get_schema("users")
            schema = eval(schema_str)
            assert schema["columns"][0]["name"] == "id"
            assert schema["columns"][0]["type"] == "integer"
            assert schema["columns"][1]["name"] == "name" 
            assert schema["columns"][1]["type"] == "text"
            assert schema["columns"][2]["name"] == "email"
            assert schema["columns"][2]["type"] == "text"

@pytest.mark.asyncio
async def test_execute_query(postgres_db, mcp_config):
    """Test executing SELECT queries"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_pg") as handler:
                # Simple SELECT
                result_str = await handler.execute_query("SELECT name FROM users ORDER BY name")
                result = eval(result_str)
                assert len(result["rows"]) == 2
                assert result["rows"][0]["name"] == "Alice"
                assert result["rows"][1]["name"] == "Bob"

                # SELECT with WHERE clause
                result_str = await handler.execute_query(
                    "SELECT * FROM users WHERE email = 'alice@test.com'"
                )
                result = eval(result_str)
                assert len(result["rows"]) == 1
                assert result["rows"][0]["name"] == "Alice"

@pytest.mark.asyncio
async def test_non_select_query(postgres_db, mcp_config):
    """Test that non-SELECT queries are rejected"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_pg") as handler:
            with pytest.raises(ConnectionHandlerError, match="cannot execute DELETE in a read-only transaction"):
                await handler.execute_query("DELETE FROM users")

@pytest.mark.asyncio
async def test_invalid_query(postgres_db, mcp_config):
    """Test handling of invalid SQL queries"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_pg") as handler:
            with pytest.raises(ConnectionHandlerError):
                await handler.execute_query("SELECT * FROM nonexistent_table")

@pytest.mark.asyncio
async def test_connection_cleanup(postgres_db, mcp_config):
    """Test that database connections are properly cleaned up"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_pg") as handler:
            await handler.get_tables()
