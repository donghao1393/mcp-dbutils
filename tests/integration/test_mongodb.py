"""Test MongoDB integration"""

import tempfile
import os

import pytest
import yaml

from mcp_dbutils.base import (
    ConnectionHandlerError,
    ConnectionServer,
)
from mcp_dbutils.log import create_logger

# 创建测试用的 logger
logger = create_logger("test-mongodb", True)  # debug=True 以显示所有日志

# 检查是否跳过MongoDB测试
skip_mongodb_tests = os.environ.get("SKIP_MONGODB_TESTS", "false").lower() == "true"
skip_reason = "MongoDB tests are skipped in CI environment"

@pytest.mark.asyncio
@pytest.mark.skipif(skip_mongodb_tests, reason=skip_reason)
async def test_list_collections(mongodb_db, mcp_config):
    """Test listing collections in MongoDB database"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        config_data = mcp_config
        logger("debug", f"MongoDB config: {config_data}")
        yaml.dump(config_data, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mongodb") as handler:
            collections = await handler.get_tables()
            collection_names = [collection.name for collection in collections]
            assert "customers" in collection_names
            assert "products" in collection_names

@pytest.mark.asyncio
@pytest.mark.skipif(skip_mongodb_tests, reason=skip_reason)
async def test_get_schema(mongodb_db, mcp_config):
    """Test getting schema information for a MongoDB collection"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mongodb") as handler:
            schema_str = await handler.get_schema("customers")
            schema = eval(schema_str)

            # MongoDB schema is inferred from documents
            assert "fields" in schema
            assert any(field["name"] == "name" for field in schema["fields"])
            assert any(field["name"] == "email" for field in schema["fields"])
            assert any(field["name"] == "age" for field in schema["fields"])

@pytest.mark.asyncio
@pytest.mark.skipif(skip_mongodb_tests, reason=skip_reason)
async def test_execute_find_query(mongodb_db, mcp_config):
    """Test executing find query on MongoDB"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mongodb") as handler:
            # Simple find query
            query = {
                "operation": "find",
                "collection": "customers",
                "params": {
                    "filter": {}
                }
            }
            result_str = await handler.execute_query(query)
            result = eval(result_str)
            assert len(result["rows"]) == 2

            # Find with filter
            query = {
                "operation": "find",
                "collection": "customers",
                "params": {
                    "filter": {"name": "Alice"}
                }
            }
            result_str = await handler.execute_query(query)
            result = eval(result_str)
            assert len(result["rows"]) == 1
            assert result["rows"][0]["name"] == "Alice"

@pytest.mark.asyncio
@pytest.mark.skipif(skip_mongodb_tests, reason=skip_reason)
async def test_execute_find_one_query(mongodb_db, mcp_config):
    """Test executing find_one query on MongoDB"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mongodb") as handler:
            # Find one query
            query = {
                "operation": "find_one",
                "collection": "customers",
                "params": {
                    "filter": {"name": "Bob"}
                }
            }
            result_str = await handler.execute_query(query)
            result = eval(result_str)
            assert result["name"] == "Bob"
            assert result["email"] == "bob@test.com"

@pytest.mark.asyncio
@pytest.mark.skipif(skip_mongodb_tests, reason=skip_reason)
async def test_execute_aggregate_query(mongodb_db, mcp_config):
    """Test executing aggregate query on MongoDB"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mongodb") as handler:
            # Aggregate query
            query = {
                "operation": "aggregate",
                "collection": "products",
                "params": {
                    "pipeline": [
                        {"$group": {"_id": "$category", "count": {"$sum": 1}, "avg_price": {"$avg": "$price"}}}
                    ]
                }
            }
            result_str = await handler.execute_query(query)
            result = eval(result_str)

            # Find the Electronics category result
            electronics_result = next((item for item in result["rows"] if item["_id"] == "Electronics"), None)
            assert electronics_result is not None
            assert electronics_result["count"] == 2
            assert 800 < electronics_result["avg_price"] < 900  # Average of 999.99 and 699.99

@pytest.mark.asyncio
@pytest.mark.skipif(skip_mongodb_tests, reason=skip_reason)
async def test_invalid_query(mongodb_db, mcp_config):
    """Test handling of invalid MongoDB queries"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mongodb") as handler:
            # Invalid operation
            query = {
                "operation": "invalid_operation",
                "collection": "customers",
                "params": {}
            }
            with pytest.raises(ConnectionHandlerError):
                await handler.execute_query(query)

            # Invalid collection
            query = {
                "operation": "find",
                "collection": "nonexistent_collection",
                "params": {
                    "filter": {}
                }
            }
            # This should not raise an error, just return empty results
            result_str = await handler.execute_query(query)
            result = eval(result_str)
            assert len(result["rows"]) == 0

@pytest.mark.asyncio
@pytest.mark.skipif(skip_mongodb_tests, reason=skip_reason)
async def test_connection_cleanup(mongodb_db, mcp_config):
    """Test that MongoDB connections are properly cleaned up"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mongodb") as handler:
            await handler.get_tables()
