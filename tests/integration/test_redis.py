"""Test Redis integration"""

import tempfile

import pytest
import yaml

from mcp_dbutils.base import (
    ConnectionHandlerError,
    ConnectionServer,
)
from mcp_dbutils.log import create_logger

# 创建测试用的 logger
logger = create_logger("test-redis", True)  # debug=True 以显示所有日志

@pytest.mark.asyncio
async def test_list_keys(redis_db, mcp_config):
    """Test listing keys in Redis database"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        config_data = mcp_config
        logger("debug", f"Redis config: {config_data}")
        yaml.dump(config_data, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_redis") as handler:
            keys = await handler.get_tables()
            key_names = [key.name for key in keys]
            assert "user:1" in key_names
            assert "user:2" in key_names
            assert "user:1:details" in key_names
            assert "user:2:details" in key_names
            assert "recent_users" in key_names

@pytest.mark.asyncio
async def test_get_key_type(redis_db, mcp_config):
    """Test getting key type information"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_redis") as handler:
            # String key
            schema_str = await handler.get_schema("user:1")
            schema = eval(schema_str)
            assert schema["type"] == "string"
            
            # Hash key
            schema_str = await handler.get_schema("user:1:details")
            schema = eval(schema_str)
            assert schema["type"] == "hash"
            
            # List key
            schema_str = await handler.get_schema("recent_users")
            schema = eval(schema_str)
            assert schema["type"] == "list"

@pytest.mark.asyncio
async def test_execute_get_command(redis_db, mcp_config):
    """Test executing GET command on Redis"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_redis") as handler:
            # GET command
            result_str = await handler.execute_query("GET user:1")
            result = eval(result_str)
            assert result == "Alice"
            
            result_str = await handler.execute_query("GET user:2")
            result = eval(result_str)
            assert result == "Bob"

@pytest.mark.asyncio
async def test_execute_hgetall_command(redis_db, mcp_config):
    """Test executing HGETALL command on Redis"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_redis") as handler:
            # HGETALL command
            result_str = await handler.execute_query("HGETALL user:1:details")
            result = eval(result_str)
            assert result["email"] == "alice@test.com"
            assert result["age"] == "30"

@pytest.mark.asyncio
async def test_execute_lrange_command(redis_db, mcp_config):
    """Test executing LRANGE command on Redis"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_redis") as handler:
            # LRANGE command
            result_str = await handler.execute_query("LRANGE recent_users 0 -1")
            result = eval(result_str)
            assert len(result) == 2
            assert result[0] == "user:1"
            assert result[1] == "user:2"

@pytest.mark.asyncio
async def test_execute_multi_commands(redis_db, mcp_config):
    """Test executing multiple Redis commands"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_redis") as handler:
            # Multiple commands
            commands = [
                "GET user:1",
                "HGET user:1:details email",
                "LLEN recent_users"
            ]
            
            for command in commands:
                result_str = await handler.execute_query(command)
                result = eval(result_str)
                
                if command == "GET user:1":
                    assert result == "Alice"
                elif command == "HGET user:1:details email":
                    assert result == "alice@test.com"
                elif command == "LLEN recent_users":
                    assert result == 2

@pytest.mark.asyncio
async def test_invalid_command(redis_db, mcp_config):
    """Test handling of invalid Redis commands"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_redis") as handler:
            # Invalid command
            with pytest.raises(ConnectionHandlerError):
                await handler.execute_query("INVALID_COMMAND")
                
            # Command with wrong number of arguments
            with pytest.raises(ConnectionHandlerError):
                await handler.execute_query("GET")
                
            # Non-existent key
            result_str = await handler.execute_query("GET nonexistent_key")
            result = eval(result_str)
            assert result is None

@pytest.mark.asyncio
async def test_connection_cleanup(redis_db, mcp_config):
    """Test that Redis connections are properly cleaned up"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_redis") as handler:
            await handler.get_tables()
