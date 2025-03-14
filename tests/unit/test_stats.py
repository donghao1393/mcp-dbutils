"""Unit tests for resource monitoring functionality"""

from datetime import datetime

from mcp_dbutils.stats import ResourceStats


def test_connection_tracking():
    """Test connection tracking functionality"""
    stats = ResourceStats()

    # Test initial state
    assert stats.active_connections == 0
    assert stats.total_connections == 0
    assert stats.connection_start_time is None

    # Test connection start
    stats.record_connection_start()
    assert stats.active_connections == 1
    assert stats.total_connections == 1
    assert isinstance(stats.connection_start_time, datetime)

    # Test multiple connections
    stats.record_connection_start()
    assert stats.active_connections == 2
    assert stats.total_connections == 2

    # Test connection end
    stats.record_connection_end()
    assert stats.active_connections == 1
    assert stats.total_connections == 2  # Total should not decrease

    # Test connection cleanup
    stats.record_connection_end()
    assert stats.active_connections == 0
    assert stats.total_connections == 2

def test_query_tracking():
    """Test query execution tracking"""
    stats = ResourceStats()

    # Test initial state
    assert stats.query_count == 0
    assert stats.last_query_time is None

    # Test query recording
    stats.record_query()
    assert stats.query_count == 1
    assert isinstance(stats.last_query_time, datetime)

    # Test multiple queries
    stats.record_query()
    assert stats.query_count == 2

def test_error_tracking():
    """Test error tracking functionality"""
    stats = ResourceStats()

    # Test initial state
    assert stats.error_count == 0
    assert stats.last_error_time is None
    assert stats.error_types == {}

    # Test error recording
    stats.record_error("DatabaseError")
    assert stats.error_count == 1
    assert isinstance(stats.last_error_time, datetime)
    assert stats.error_types["DatabaseError"] == 1

    # Test multiple errors
    stats.record_error("ConfigurationError")
    stats.record_error("DatabaseError")
    assert stats.error_count == 3
    assert stats.error_types["DatabaseError"] == 2
    assert stats.error_types["ConfigurationError"] == 1

def test_stats_serialization():
    """Test statistics serialization to dict"""
    stats = ResourceStats()

    # Setup some data
    stats.record_connection_start()
    stats.record_query()
    stats.record_error("TestError")

    # Test serialization
    data = stats.to_dict()
    assert isinstance(data, dict)
    assert data["active_connections"] == 1
    assert data["total_connections"] == 1
    assert data["query_count"] == 1
    assert data["error_count"] == 1
    assert isinstance(data["connection_duration"], (int, float))
    assert data["error_types"]["TestError"] == 1
