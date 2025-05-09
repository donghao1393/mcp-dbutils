"""Test fixtures and helper classes for integration tests"""

import tempfile
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Dict
from unittest.mock import MagicMock
from urllib.parse import urlparse

import aiosqlite
import psycopg2
import pytest
from testcontainers.mongodb import MongoDbContainer
from testcontainers.mysql import MySqlContainer
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

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

    async def _execute_write_query(self, sql: str):
        return "Write operation executed successfully. 1 row affected."

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

    async def test_connection(self) -> bool:
        return True

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
            port=int(mysql.get_exposed_port(3306)),
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

@pytest.fixture(scope="function")
def mongodb_db():
    """Create a MongoDB test database"""
    mongodb_container = MongoDbContainer("mongo:6.0")
    mongodb_container.with_env("MONGO_INITDB_ROOT_USERNAME", "root")
    mongodb_container.with_env("MONGO_INITDB_ROOT_PASSWORD", "example")

    with mongodb_container as mongodb:
        mongodb.start()

        # 使用pymongo建立连接
        import pymongo
        conn = pymongo.MongoClient(
            host=mongodb.get_container_host_ip(),
            port=int(mongodb.get_exposed_port(27017)),
            username="root",
            password="example",
            authSource="admin"
        )

        try:
            # 创建测试数据库和集合
            db = conn["test_db"]
            collection = db["customers"]

            # 插入测试数据
            collection.insert_many([
                {"name": "Alice", "email": "alice@test.com", "age": 30},
                {"name": "Bob", "email": "bob@test.com", "age": 25}
            ])

            # 创建另一个集合
            products = db["products"]
            products.insert_many([
                {"name": "Laptop", "price": 999.99, "category": "Electronics"},
                {"name": "Phone", "price": 699.99, "category": "Electronics"},
                {"name": "Headphones", "price": 149.99, "category": "Accessories"}
            ])

            yield mongodb
        finally:
            conn.close()

@pytest.fixture(scope="function")
def redis_db():
    """Create a Redis test database"""
    redis_container = RedisContainer("redis:7.0")

    with redis_container as redis:
        redis.start()

        # 使用redis-py建立连接
        import redis as redis_py
        conn = redis_py.Redis(
            host=redis.get_container_host_ip(),
            port=int(redis.get_exposed_port(6379))
        )

        try:
            # 添加测试数据
            conn.set("user:1", "Alice")
            conn.set("user:2", "Bob")

            # 添加哈希数据
            conn.hset("user:1:details", mapping={
                "email": "alice@test.com",
                "age": "30"
            })
            conn.hset("user:2:details", mapping={
                "email": "bob@test.com",
                "age": "25"
            })

            # 添加列表数据
            conn.rpush("recent_users", "user:1", "user:2")

            yield redis
        finally:
            conn.close()

@pytest.fixture
def mcp_config(mysql_db, postgres_db, sqlite_db, mongodb_db, redis_db):
    """Create MCP configuration for database tests"""
    return {
        "connections": {
            "test_mysql": {
                "type": "mysql",
                "host": mysql_db.get_container_host_ip(),
                "port": int(mysql_db.get_exposed_port(3306)),
                "database": "test_db",
                "user": "test_user",
                "password": "test_pass",
                "charset": "utf8mb4"
            },
            "test_pg": postgres_db,
            "test_sqlite": sqlite_db,
            "test_mongodb": {
                "type": "mongodb",
                "host": mongodb_db.get_container_host_ip(),
                "port": int(mongodb_db.get_exposed_port(27017)),
                "database": "test_db",
                "username": "root",
                "password": "example",
                "authSource": "admin"
            },
            "test_redis": {
                "type": "redis",
                "host": redis_db.get_container_host_ip(),
                "port": int(redis_db.get_exposed_port(6379)),
                "database": 0
            }
        }
    }
