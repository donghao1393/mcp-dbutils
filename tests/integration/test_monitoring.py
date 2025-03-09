"""Integration tests for resource monitoring"""

import pytest
import tempfile
import yaml
from mcp_dbutils.base import ConnectionServer, ConnectionHandlerError

@pytest.mark.asyncio
async def test_sqlite_monitoring(sqlite_db, mcp_config):
    """Test resource monitoring with SQLite"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)

        async with server.get_handler("test_sqlite") as handler:
            # Connection stats
            stats = handler.stats
            assert stats.active_connections == 1
            assert stats.total_connections == 1

            # Execute queries and check stats
            await handler.execute_query("SELECT * FROM products")
            assert stats.query_count == 1

            await handler.execute_query("SELECT name FROM products")
            assert stats.query_count == 2

            # Test error recording
            try:
                await handler.execute_query("SELECT * FROM nonexistent")
            except ConnectionHandlerError:
                pass

            assert stats.error_count == 1
            assert "ConnectionHandlerError" in stats.error_types

        # After context exit, connection should be closed
        assert stats.active_connections == 0

@pytest.mark.asyncio
async def test_postgres_monitoring(postgres_db, mcp_config):
    """Test resource monitoring with PostgreSQL"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)

        async with server.get_handler("test_pg") as handler:
            # Connection stats
            stats = handler.stats
            assert stats.active_connections == 1
            assert stats.total_connections == 1

            # Execute queries and check stats
            await handler.execute_query("SELECT * FROM users")
            assert stats.query_count == 1

            await handler.execute_query("SELECT name FROM users")
            assert stats.query_count == 2

            # Test error recording
            try:
                await handler.execute_query("SELECT * FROM nonexistent")
            except ConnectionHandlerError:
                pass

            assert stats.error_count == 1
            assert "ConnectionHandlerError" in stats.error_types

            # Test stats serialization
            stats_dict = stats.to_dict()
            assert stats_dict["query_count"] == 3  # Two successful queries + one failed query
            assert stats_dict["error_count"] == 1
            assert isinstance(stats_dict["connection_duration"], (int, float))

        # After context exit, connection should be closed
        assert stats.active_connections == 0
