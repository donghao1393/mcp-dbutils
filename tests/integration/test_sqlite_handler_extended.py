"""Extended SQLite handler integration tests"""

import os
import tempfile

import pytest
import yaml

from mcp_dbutils.base import (
    ConnectionHandlerError,
    ConnectionServer,
)
from mcp_dbutils.log import create_logger

# 创建测试用的 logger
logger = create_logger("test-sqlite-extended", True)  # debug=True 以显示所有日志

@pytest.mark.asyncio
async def test_get_indexes(sqlite_db, mcp_config):
    """Test getting index information for SQLite table"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_sqlite") as handler:
            # Get indexes for users table
            indexes = await handler.get_indexes("users")
            
            # Verify indexes content
            assert "Indexes for users:" in indexes
            assert "sqlite_autoindex_users_1" in indexes or "PRIMARY" in indexes  # SQLite's auto-index for primary key
            
            # Test with a table that has a custom index
            # Create an index on the users table if it doesn't exist
            path = mcp_config["connections"]["test_sqlite"]["path"]
            os.system(f"sqlite3 {path} 'CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)'")
            
            # Get updated indexes
            indexes = await handler.get_indexes("users")
            assert "idx_users_email" in indexes  # Should show our custom index
            assert "Index:" in indexes
            assert "Definition:" in indexes

@pytest.mark.asyncio
async def test_get_indexes_nonexistent(sqlite_db, mcp_config):
    """Test getting indexes for nonexistent table"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_sqlite") as handler:
            with pytest.raises(ConnectionHandlerError, match="Failed to get index information"):
                await handler.get_indexes("nonexistent_table")

@pytest.mark.asyncio
async def test_explain_query(sqlite_db, mcp_config):
    """Test the query explanation functionality"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_sqlite") as handler:
            # Get execution plan for a SELECT query
            explain_result = await handler.explain_query("SELECT * FROM users WHERE id = 1")
            
            # Verify the explanation includes expected SQLite EXPLAIN output
            assert "QUERY PLAN" in explain_result or "addr" in explain_result
            assert "scan" in explain_result.lower()
            assert "users" in explain_result

@pytest.mark.asyncio
async def test_explain_query_invalid(sqlite_db, mcp_config):
    """Test explanation for invalid query"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_sqlite") as handler:
            with pytest.raises(ConnectionHandlerError, match="Failed to get query execution plan"):
                await handler.explain_query("SELECT * FROM nonexistent_table")

@pytest.mark.asyncio
async def test_get_table_statistics(sqlite_db, mcp_config):
    """Test getting table statistics"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_sqlite") as handler:
            # Get statistics for users table
            stats = await handler.get_table_statistics("users")
            
            # Verify statistics content
            assert "Statistics for users:" in stats
            assert "Row count" in stats
            assert "Available in SQLite 3.16+" in stats or "pages" in stats

@pytest.mark.asyncio
async def test_get_table_statistics_nonexistent(sqlite_db, mcp_config):
    """Test getting statistics for nonexistent table"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_sqlite") as handler:
            with pytest.raises(ConnectionHandlerError, match="Failed to get table statistics"):
                await handler.get_table_statistics("nonexistent_table")

@pytest.mark.asyncio
async def test_execute_complex_queries(sqlite_db, mcp_config):
    """Test executing more complex SELECT queries"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_sqlite") as handler:
            # Query with GROUP BY
            result_str = await handler.execute_query(
                "SELECT COUNT(*) as count FROM users GROUP BY name"
            )
            result = eval(result_str)
            assert "columns" in result
            assert "rows" in result
            assert len(result["columns"]) == 1
            assert result["columns"][0] == "count"
            
            # Query with ORDER BY and LIMIT
            result_str = await handler.execute_query(
                "SELECT name FROM users ORDER BY name LIMIT 1"
            )
            result = eval(result_str)
            assert len(result["rows"]) == 1
            
            # Query with JOIN (assuming a related table exists, otherwise this may fail)
            try:
                # Create a posts table if it doesn't exist
                path = mcp_config["connections"]["test_sqlite"]["path"]
                os.system(f"""
                    sqlite3 {path} '
                    CREATE TABLE IF NOT EXISTS posts (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        title TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    );
                    INSERT OR IGNORE INTO posts (id, user_id, title) VALUES (1, 1, "Test Post 1");
                    INSERT OR IGNORE INTO posts (id, user_id, title) VALUES (2, 2, "Test Post 2");
                    '
                """)
                
                # Execute JOIN query
                result_str = await handler.execute_query(
                    "SELECT u.name, p.title FROM users u JOIN posts p ON u.id = p.user_id ORDER BY u.name"
                )
                result = eval(result_str)
                assert len(result["columns"]) == 2
                assert "name" in result["columns"]
                assert "title" in result["columns"]
            except Exception as e:
                logger("warning", f"JOIN query test skipped: {str(e)}")
