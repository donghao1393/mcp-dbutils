"""Integration tests for enhanced monitoring features"""

import pytest
import tempfile
import yaml
import time
import json
from datetime import datetime
from mcp_dbutils.base import ConnectionServer, ConnectionHandlerError
from mcp_dbutils.stats import ResourceStats

@pytest.mark.asyncio
async def test_resource_stats_performance_tracking(sqlite_db, mcp_config):
    """Test performance tracking in ResourceStats"""
    # Create a ResourceStats instance
    stats = ResourceStats()
    
    # Record some query durations
    stats.record_query_duration("SELECT * FROM products", 0.05)  # 50ms
    stats.record_query_duration("SELECT name FROM products", 0.02)  # 20ms
    stats.record_query_duration("SELECT * FROM products WHERE price > 10", 0.15)  # 150ms (slow)
    
    # Check query count and types
    assert stats.query_count == 0  # query_count is only incremented by record_query()
    assert "SELECT" in stats.query_types
    assert stats.query_types["SELECT"] == 3
    
    # Check slow queries
    assert len(stats.slow_queries) == 1
    assert stats.slow_queries[0][1] == 0.15
    
    # Check query time stats
    time_stats = stats.get_query_time_stats()
    assert time_stats["min"] == 0.02
    assert time_stats["max"] == 0.15
    assert 0.07 < time_stats["avg"] < 0.08  # (0.05 + 0.02 + 0.15) / 3 = 0.073
    
    # Check performance stats formatting
    perf_stats = stats.get_performance_stats()
    assert "Database Performance Statistics" in perf_stats
    assert "Query Times" in perf_stats
    assert "Query Types" in perf_stats
    assert "SELECT: 3" in perf_stats
    assert "Slow Queries" in perf_stats

@pytest.mark.asyncio
async def test_query_duration_tracking(sqlite_db, mcp_config):
    """Test query duration tracking in database handler"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)

        async with server.get_handler("test_sqlite") as handler:
            # Execute a query and check duration tracking
            await handler.execute_query("SELECT * FROM products")
            
            # Verify that query duration was recorded
            assert len(handler.stats.query_durations) == 1
            assert handler.stats.query_durations[0] > 0
            
            # Verify query type tracking
            assert "SELECT" in handler.stats.query_types
            assert handler.stats.query_types["SELECT"] == 1
            
            # Execute another query
            await handler.execute_query("SELECT name FROM products")
            
            # Verify that query duration was recorded
            assert len(handler.stats.query_durations) == 2
            
            # Verify to_dict includes query times
            stats_dict = handler.stats.to_dict()
            assert "query_times_ms" in stats_dict
            assert "min" in stats_dict["query_times_ms"]
            assert "max" in stats_dict["query_times_ms"]
            assert "avg" in stats_dict["query_times_ms"]

@pytest.mark.asyncio
async def test_get_performance_stats(sqlite_db, mcp_config):
    """Test performance statistics generation"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        
        # Execute some queries to generate stats
        async with server.get_handler("test_sqlite") as handler:
            await handler.execute_query("SELECT * FROM products")
            await handler.execute_query("SELECT name FROM products")
            
            # Intentionally cause an error
            try:
                await handler.execute_query("SELECT * FROM nonexistent")
            except ConnectionHandlerError:
                pass
            
            # Get performance stats directly from handler
            perf_stats = handler.stats.get_performance_stats()
            
            # Verify performance stats content
            assert "Database Performance Statistics" in perf_stats
            assert "Query Count: 3" in perf_stats  # 2 successful + 1 failed
            assert "Query Types" in perf_stats
            assert "SELECT: 2" in perf_stats  # Only successful queries are counted in query_types
            assert "Error Rate" in perf_stats
            
            # Verify query durations are tracked
            assert len(handler.stats.query_durations) == 2  # Only successful queries have durations recorded
            assert len(handler.stats.query_types) == 1  # Only SELECT queries
            
            # Verify error tracking
            assert handler.stats.error_count == 1
            assert "ConnectionHandlerError" in handler.stats.error_types

@pytest.mark.asyncio
async def test_query_analysis(sqlite_db, mcp_config):
    """Test query analysis functionality"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)
        
        async with server.get_handler("test_sqlite") as handler:
            # Get execution plan
            explain_result = await handler.explain_query("SELECT * FROM products")
            assert explain_result  # Should not be empty
            
            # Execute query and measure time
            start_time = datetime.now()
            await handler.execute_query("SELECT * FROM products")
            duration = (datetime.now() - start_time).total_seconds()
            
            # Verify query duration is reasonable
            assert duration > 0
            assert duration < 1.0  # Should be fast for a simple query
            
            # Verify query type tracking
            assert "SELECT" in handler.stats.query_types
            assert handler.stats.query_types["SELECT"] == 1
