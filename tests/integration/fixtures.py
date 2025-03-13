"""Test fixtures and helper classes for integration tests"""

import pytest
from unittest.mock import MagicMock
from testcontainers.mysql import MySqlContainer
from testcontainers.core.waiting_utils import wait_for_logs
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
    mysql_container = (MySqlContainer("mysql:8.0")
        .with_env("MYSQL_DATABASE", "test_db")
        .with_env("MYSQL_USER", "test_user")
        .with_env("MYSQL_PASSWORD", "test_pass")
        .with_env("MYSQL_ROOT_PASSWORD", "root_pass")
        .with_env("MYSQL_ALLOW_EMPTY_PASSWORD", "no")
        .with_env("MYSQL_RANDOM_ROOT_PASSWORD", "no")
    )
    
    with mysql_container as mysql:
        mysql.start()
        
        # 等待MySQL准备就绪
        wait_for_logs(mysql, "ready for connections", timeout=30)
        
        # 使用mysql-connector-python建立连接
        import mysql.connector as mysql_connector
        conn = mysql_connector.connect(
            host=mysql.get_container_host_ip(),
            port=mysql.get_exposed_port(3306),
            user="test_user",
            password="test_pass",
            database="test_db"
        )
        
        try:
            # 执行数据库初始化脚本
            with conn.cursor() as cursor:
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
                    conn.commit()
            yield mysql
        finally:
            conn.close()

@pytest.fixture
def mcp_config(mysql_db):
    """Create MCP configuration for MySQL tests"""
    return {
        "connections": {
            "test_mysql": {
                "type": "mysql",
                "host": mysql_db.get_container_host_ip(),
                "port": mysql_db.get_exposed_port(3306),
                "database": "test_db",
                "user": "test_user",
                "password": "test_pass",
                "charset": "utf8mb4"
            }
        }
    }
