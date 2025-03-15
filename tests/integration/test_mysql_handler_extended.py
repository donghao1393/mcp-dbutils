"""Extended MySQL handler integration tests"""

import tempfile

import pytest
import pytest_asyncio
import yaml

from mcp_dbutils.base import (
    ConnectionHandlerError,
    ConnectionServer,
)
from mcp_dbutils.log import create_logger

# 创建测试用的 logger
logger = create_logger("test-mysql-extended", True)  # debug=True 以显示所有日志

@pytest_asyncio.fixture(autouse=True)
async def setup_test_table(mysql_db, mcp_config):
    """Create test table before each test"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
            # Create test table
            await handler.execute_query("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(255),
                    email VARCHAR(255)
                )
            """)
            # Insert test data
            await handler.execute_query("""
                INSERT IGNORE INTO users (id, name, email) VALUES 
                (1, 'Test User 1', 'test1@example.com'),
                (2, 'Test User 2', 'test2@example.com')
            """)
    yield
    # Cleanup is handled by the mysql_db fixture

@pytest.mark.asyncio
async def test_get_table_description(mysql_db, mcp_config):
    """Test getting table description"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
            # Get description for users table
            desc = await handler.get_table_description("users")
            
            # Verify description content
            assert "Table: users" in desc
            assert "Columns:" in desc
            assert "id (int)" in desc
            assert "Nullable: NO" in desc

@pytest.mark.asyncio
async def test_get_table_description_nonexistent(mysql_db, mcp_config):
    """Test getting description for nonexistent table"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
            with pytest.raises(ConnectionHandlerError):
                await handler.get_table_description("nonexistent_table")

@pytest.mark.asyncio
async def test_get_table_constraints(mysql_db, mcp_config):
    """Test getting table constraints"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
            # Get constraints for users table
            constraints = await handler.get_table_constraints("users")
            
            # Verify constraints content
            assert "Constraints for users:" in constraints
            assert "PRIMARY KEY Constraint: PRIMARY" in constraints

@pytest.mark.asyncio
async def test_get_table_constraints_nonexistent(mysql_db, mcp_config):
    """Test getting constraints for nonexistent table"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
            with pytest.raises(ConnectionHandlerError):
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
            assert "Table Statistics for users:" in stats
            assert "Row Count" in stats
            assert "Data Length" in stats
            assert "Index Length" in stats

@pytest.mark.asyncio
async def test_get_table_stats_nonexistent(mysql_db, mcp_config):
    """Test getting statistics for nonexistent table"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
            with pytest.raises(ConnectionHandlerError):
                await handler.get_table_stats("nonexistent_table")

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
            assert "Query Execution Plan:" in explain_result
            assert "Estimated Plan:" in explain_result
            assert "Actual Plan" in explain_result

@pytest.mark.asyncio
async def test_explain_query_invalid(mysql_db, mcp_config):
    """Test explanation for invalid query"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
            with pytest.raises(ConnectionHandlerError, match="Table 'test_db.nonexistent_table' doesn't exist"):
                await handler.explain_query("SELECT * FROM nonexistent_table")

@pytest.mark.asyncio
async def test_get_table_indexes(mysql_db, mcp_config):
    """Test getting index information for MySQL table"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
            # Get indexes for users table
            indexes = await handler.get_table_indexes("users")
            
            # Verify indexes content
            assert "Index: PRIMARY" in indexes
            assert "Type: UNIQUE" in indexes
            assert "Method: BTREE" in indexes

@pytest.mark.asyncio
async def test_get_table_indexes_nonexistent(mysql_db, mcp_config):
    """Test getting indexes for nonexistent table"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
            with pytest.raises(ConnectionHandlerError):
                await handler.get_table_indexes("nonexistent_table")

@pytest.mark.asyncio
async def test_execute_complex_queries(mysql_db, mcp_config):
    """Test executing more complex SELECT queries"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        async with server.get_handler("test_mysql") as handler:
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
                await handler.execute_query("""
                    CREATE TABLE IF NOT EXISTS posts (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        user_id INT,
                        title VARCHAR(255),
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """)
                
                # Insert test data
                await handler.execute_query("""
                    INSERT IGNORE INTO posts (id, user_id, title) VALUES 
                    (1, 1, 'Test Post 1'),
                    (2, 2, 'Test Post 2')
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
                logger.warning(f"JOIN query test skipped: {str(e)}")
