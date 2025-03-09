import os
import pytest
from pytest_asyncio import fixture
import asyncio
import tempfile
from pathlib import Path
import aiosqlite
import psycopg2
from testcontainers.postgres import PostgresContainer
from typing import AsyncGenerator, Generator, Dict
from urllib.parse import urlparse

# Enable pytest-asyncio for testing
pytest.register_assert_rewrite("tests")
pytestmark = pytest.mark.asyncio

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

@fixture(scope="function")
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

@fixture(scope="function")
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

@fixture(scope="function")
async def mcp_config(postgres_db, sqlite_db) -> Dict:
    """
    Generate MCP server configuration for testing.
    """
    return {
        "connections": {
            "test_pg": postgres_db,
            "test_sqlite": sqlite_db
        }
    }
