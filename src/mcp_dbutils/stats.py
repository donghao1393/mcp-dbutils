"""Resource monitoring statistics module"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Tuple
import sys
import statistics

@dataclass
class ResourceStats:
    """Resource statistics tracking"""
    # Connection stats
    active_connections: int = 0
    total_connections: int = 0
    connection_start_time: Optional[datetime] = None

    # Query stats
    query_count: int = 0
    last_query_time: Optional[datetime] = None

    # Error stats
    error_count: int = 0
    last_error_time: Optional[datetime] = None
    error_types: dict[str, int] = None

    # Resource stats
    estimated_memory: int = 0
    
    # Performance monitoring
    query_durations: List[float] = None  # 查询执行时间列表 (秒)
    query_types: dict[str, int] = None   # 查询类型统计 (SELECT, EXPLAIN等)
    slow_queries: List[Tuple[str, float]] = None  # 慢查询记录 (SQL, 时间)
    peak_memory: int = 0  # 峰值内存使用

    def __post_init__(self):
        """Initialize mutable defaults"""
        if self.error_types is None:
            self.error_types = {}
        if self.query_durations is None:
            self.query_durations = []
        if self.query_types is None:
            self.query_types = {}
        if self.slow_queries is None:
            self.slow_queries = []

    def record_connection_start(self):
        """Record new connection start"""
        self.active_connections += 1
        self.total_connections += 1
        self.connection_start_time = datetime.now()

    def record_connection_end(self):
        """Record connection end"""
        self.active_connections = max(0, self.active_connections - 1)

    def record_query(self):
        """Record query execution"""
        self.query_count += 1
        self.last_query_time = datetime.now()

    def record_query_duration(self, sql: str, duration: float):
        """Record query execution time and type

        Args:
            sql: SQL query text
            duration: Execution time in seconds
        """
        self.query_durations.append(duration)
        
        # Record query type
        query_type = sql.strip().split()[0].upper()
        self.query_types[query_type] = self.query_types.get(query_type, 0) + 1
        
        # Record slow queries (over 100ms)
        if duration > 0.1:  # 100ms
            # Keep at most 10 slow queries
            if len(self.slow_queries) >= 10:
                self.slow_queries.pop(0)
            self.slow_queries.append((sql[:100], duration))  # Truncate SQL to avoid excessive length

    def record_error(self, error_type: str):
        """Record error occurrence

        Args:
            error_type: Type/class name of the error
        """
        self.error_count += 1
        self.last_error_time = datetime.now()
        self.error_types[error_type] = self.error_types.get(error_type, 0) + 1

    def update_memory_usage(self, obj: object):
        """Update estimated memory usage

        Args:
            obj: Object to estimate size for
        """
        current_memory = sys.getsizeof(obj)
        self.estimated_memory = current_memory
        self.peak_memory = max(self.peak_memory, current_memory)

    def get_query_time_stats(self) -> dict:
        """Get query time statistics

        Returns:
            Dictionary with min, max, avg, median query times
        """
        if not self.query_durations:
            return {
                "min": 0,
                "max": 0,
                "avg": 0,
                "median": 0
            }
        
        return {
            "min": min(self.query_durations),
            "max": max(self.query_durations),
            "avg": sum(self.query_durations) / len(self.query_durations),
            "median": statistics.median(self.query_durations) if len(self.query_durations) > 0 else 0
        }

    def get_performance_stats(self) -> str:
        """Get formatted performance statistics

        Returns:
            Formatted string with performance statistics
        """
        stats = []
        stats.append(f"Database Performance Statistics")
        stats.append(f"-----------------------------")
        stats.append(f"Query Count: {self.query_count}")
        
        # Query time statistics
        if self.query_durations:
            time_stats = self.get_query_time_stats()
            stats.append(f"Query Times: avg={time_stats['avg']*1000:.2f}ms, min={time_stats['min']*1000:.2f}ms, max={time_stats['max']*1000:.2f}ms, median={time_stats['median']*1000:.2f}ms")
        
        # Query type distribution
        if self.query_types:
            stats.append(f"Query Types:")
            for qtype, count in self.query_types.items():
                percentage = (count / self.query_count) * 100 if self.query_count else 0
                stats.append(f"  - {qtype}: {count} ({percentage:.1f}%)")
        
        # Slow queries
        if self.slow_queries:
            stats.append(f"Slow Queries:")
            for sql, duration in self.slow_queries:
                stats.append(f"  - {duration*1000:.2f}ms: {sql}...")
        
        # Error statistics
        if self.error_count > 0:
            error_rate = (self.error_count / self.query_count) * 100 if self.query_count else 0
            stats.append(f"Error Rate: {error_rate:.2f}% ({self.error_count} errors)")
            stats.append(f"Error Types:")
            for etype, count in self.error_types.items():
                stats.append(f"  - {etype}: {count}")
        
        # Resource usage
        stats.append(f"Memory Usage: current={self.estimated_memory/1024:.2f}KB, peak={self.peak_memory/1024:.2f}KB")
        stats.append(f"Connections: active={self.active_connections}, total={self.total_connections}")
        
        return "\n".join(stats)

    def to_dict(self) -> dict:
        """Convert stats to dictionary for logging

        Returns:
            Dictionary of current statistics
        """
        now = datetime.now()
        connection_duration = None
        if self.connection_start_time:
            connection_duration = (now - self.connection_start_time).total_seconds()

        time_stats = self.get_query_time_stats()
        
        return {
            "active_connections": self.active_connections,
            "total_connections": self.total_connections,
            "connection_duration": connection_duration,
            "query_count": self.query_count,
            "query_times_ms": {
                "min": time_stats["min"] * 1000 if self.query_durations else 0,
                "max": time_stats["max"] * 1000 if self.query_durations else 0,
                "avg": time_stats["avg"] * 1000 if self.query_durations else 0,
                "median": time_stats["median"] * 1000 if self.query_durations else 0
            },
            "query_types": self.query_types,
            "error_count": self.error_count,
            "error_types": self.error_types,
            "estimated_memory_bytes": self.estimated_memory,
            "peak_memory_bytes": self.peak_memory
        }
