"""Test fixtures and helper classes for integration tests"""

import pytest
import tempfile
import asyncio
from pathlib import Path
import aiosqlite
import psycopg2
from unittest.mock import MagicMock
from testcontainers.mysql import MySqlContainer
from testcontainers.postgres import PostgresContainer
from testcontainers.core.waiting_utils import wait_for_logs
from mcp_dbutils.base import ConnectionHandler
from typing import AsyncGenerator, Dict
from urllib.parse import urlparse

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

def parse_postgres_url(url: str) -> Dict[str, str]:
    """Parse postgres URL into connection parameters"""
    # Remove postgres+psycopg2:// prefix if present
    if url.startswith('postgresql+psycopg2://'):
        url = url.replace('postgresql+psycopg2://', 'postgresql://')

    parsed = urlparse(url)
    params = {
        'dbname': parsed.path[1:],  # Remove leading '/'
        'user': parsed.username,
        'password': parsed.password,
        'host': parsed.hostname,
        'port': parsed.port or 5432  # Default port if not specified
    }
    return {k: v for k, v in params.items() if v is not None}

@pytest.fixture(scope="session")
def mysql_db():
    """Create a MySQL test database"""
    # 使用构造函数参数而不是with_env方法
    mysql_container = MySqlContainer(
        "mysql:8.0",
        username="test_user",
        password="test_pass",
        dbname="test_db",
        root_password="root_pass"
    )
    
    with mysql_container as mysql:
        mysql.start()
        
        # 使用内置的_connect方法等待MySQL完全准备就绪
        mysql._connect()
        
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

@pytest.fixture(scope="function")
async def postgres_db() -> AsyncGenerator[Dict[str, str], None]:
    """
    Create a temporary PostgreSQL database for testing.
    """
    postgres = PostgresContainer("postgres:15-alpine")
    postgres.start()

    try:
        url = postgres.get_connection_url()
        # Get connection parameters from URL
        conn_params = parse_postgres_url(url)

        # Create direct connection using psycopg2
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()

        # Create test data
        cur.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE
            );

            INSERT INTO users (name, email) VALUES 
                ('Alice', 'alice@test.com'),
                ('Bob', 'bob@test.com');
        """)
        conn.commit()
        cur.close()
        conn.close()

        # Parse URL into connection parameters
        conn_params = parse_postgres_url(url)
        conn_info = {
            "type": "postgres",
            **conn_params
        }
        yield conn_info

    finally:
        postgres.stop()

@pytest.fixture(scope="function")
async def sqlite_db() -> AsyncGenerator[Dict[str, str], None]:
    """
    Create a temporary SQLite database for testing.
    """
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = Path(tmp.name)

        # Create test database file and data
        async with aiosqlite.connect(db_path) as db:
            await db.execute("""
                CREATE TABLE products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL
                );
            """)
            await db.execute("""
                INSERT INTO products (name, price) VALUES 
                    ('Widget', 9.99),
                    ('Gadget', 19.99);
            """)
            await db.commit()

        conn_info = {
            "type": "sqlite",
            "path": str(db_path)
        }
        yield conn_info

        # Clean up
        try:
            db_path.unlink()
        except FileNotFoundError:
            pass

@pytest.fixture
def mcp_config(mysql_db, postgres_db, sqlite_db):
    """Create MCP configuration for database tests"""
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
            },
            "test_pg": postgres_db,
            "test_sqlite": sqlite_db
        }
    }
