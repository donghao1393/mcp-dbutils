"""Test fixtures and helper classes for integration tests"""

import pytest
from unittest.mock import MagicMock
from testcontainers.mysql import MySqlContainer
from mcp_dbutils.base import ConnectionHandler

class _TestConnectionHandler(ConnectionHandler):
    """Test implementation of ConnectionHandler"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 禁用自动记录统计信息
        self.stats.record_connection_start = MagicMock()
        self.stats.record_connection_end = MagicMock()
    
    @property
    def db_type(self) -> str:
        return "test"
        
    async def get_tables(self):
        return []
        
    async def get_schema(self, table_name: str):
        return ""
        
    async def _execute_query(self, sql: str):
        return ""
        
    async def get_table_description(self, table_name: str):
        return ""
        
    async def get_table_ddl(self, table_name: str):
        return ""
        
    async def get_table_indexes(self, table_name: str):
        return ""
        
    async def get_table_stats(self, table_name: str):
        return ""
        
    async def get_table_constraints(self, table_name: str):
        return ""
        
    async def explain_query(self, sql: str):
        return ""
        
    async def cleanup(self):
        pass

# Export the class with the public name
TestConnectionHandler = _TestConnectionHandler

@pytest.fixture(scope="session")
def mysql_db():
    """Create a MySQL test database"""
    with MySqlContainer("mysql:8.0") as mysql:
        # 执行数据库初始化脚本
        with mysql.get_connection() as connection:
            with connection.cursor() as cursor:
                # 创建测试表
                cursor.execute("""
                    CREATE TABLE users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(100) NOT NULL
                    )
                """)
                # 插入测试数据
                cursor.execute("""
                    INSERT INTO users (name, email) VALUES
                    ('Alice', 'alice@test.com'),
                    ('Bob', 'bob@test.com')
                """)
                connection.commit()
        yield mysql

@pytest.fixture
def mcp_config(mysql_db):
    """Create MCP configuration for MySQL tests"""
    return {
        "connections": {
            "test_mysql": {
                "type": "mysql",
                "host": mysql_db.get_container_host_ip(),
                "port": mysql_db.get_exposed_port(3306),
                "database": mysql_db.MYSQL_DATABASE,
                "user": mysql_db.MYSQL_USER,
                "password": mysql_db.MYSQL_PASSWORD,
                "charset": "utf8mb4"
            }
        }
    }
