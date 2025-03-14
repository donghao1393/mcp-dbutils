"""Test fixtures and utility functions for pytest"""


from .fixtures import TestConnectionHandler, mcp_config, mysql_db

# Register fixtures
mysql_db = mysql_db
mcp_config = mcp_config
TestConnectionHandler = TestConnectionHandler
