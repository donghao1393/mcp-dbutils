"""Extended MySQL handler integration tests"""

import tempfile

import pytest
import yaml

from mcp_dbutils.base import (
    ConnectionHandlerError,
    ConnectionServer,
)
from mcp_dbutils.log import create_logger

# 创建测试用的 logger
logger = create_logger("test-mysql-extended", True)  # debug=True 以显示所有日志

@pytest.mark.asyncio
async def test_get_table_description(mysql_db, mcp_config):
    """Test getting table description for MySQL table"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
            # Get table description
            description = await handler.get_table_description("users")
            
            # Verify description content
            assert "Table: users" in description
            assert "Comment:" in description
            assert "Columns:" in description
            assert "id (int)" in description
            assert "name (varchar)" in description
            assert "email (varchar)" in description
            assert "Nullable:" in description
            assert "Default:" in description

@pytest.mark.asyncio
async def test_get_table_description_nonexistent(mysql_db, mcp_config):
    """Test getting description for nonexistent table"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
            with pytest.raises(ConnectionHandlerError, match="Failed to get table description"):
                await handler.get_table_description("nonexistent_table")

@pytest.mark.asyncio
async def test_get_table_constraints(mysql_db, mcp_config):
    """Test getting table constraints"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
            # Get constraints for users table (which has a primary key)
            constraints = await handler.get_table_constraints("users")
            
            # Verify constraints content
            assert "Constraints for users:" in constraints
            assert "PRIMARY KEY" in constraints
            assert "id" in constraints  # Primary key column name

@pytest.mark.asyncio
async def test_get_table_constraints_nonexistent(mysql_db, mcp_config):
    """Test getting constraints for nonexistent table"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
            with pytest.raises(ConnectionHandlerError, match="Failed to get constraint information"):
                await handler.get_table_constraints("nonexistent_table")

@pytest.mark.asyncio
async def test_get_table_stats(mysql_db, mcp_config):
    """Test getting table statistics"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
            # Get statistics for users table
            stats = await handler.get_table_stats("users")
            
            # Verify statistics content
            assert "Statistics for users:" in stats
            assert "Row count" in stats

@pytest.mark.asyncio
async def test_explain_query(mysql_db, mcp_config):
    """Test the query explanation functionality"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
            # Get execution plan for a SELECT query
            explain_result = await handler.explain_query("SELECT * FROM users WHERE id = 1")
            
            # Verify the explanation includes expected MySQL EXPLAIN output
            assert "EXPLAIN" in explain_result
            assert "id" in explain_result
            assert "select_type" in explain_result
            assert "table" in explain_result
            assert "users" in explain_result

@pytest.mark.asyncio
async def test_explain_query_invalid(mysql_db, mcp_config):
    """Test explanation for invalid query"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
            with pytest.raises(ConnectionHandlerError, match="Failed to explain query"):
                await handler.explain_query("SELECT * FROM nonexistent_table")

@pytest.mark.asyncio
async def test_get_table_indexes(mysql_db, mcp_config):
    """Test getting index information"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
            # Get indexes for users table
            indexes = await handler.get_table_indexes("users")
            
            # Verify indexes content
            assert "Indexes for users:" in indexes
            assert "PRIMARY" in indexes  # Primary key index
            
@pytest.mark.asyncio
async def test_get_table_indexes_nonexistent(mysql_db, mcp_config):
    """Test getting indexes for nonexistent table"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
            with pytest.raises(ConnectionHandlerError, match="Failed to get index information"):
                await handler.get_table_indexes("nonexistent_table")
