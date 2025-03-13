"""Test fixtures and helper classes for integration tests"""

from unittest.mock import MagicMock
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
