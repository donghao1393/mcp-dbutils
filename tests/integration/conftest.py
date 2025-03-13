"""Test fixtures and utility functions for pytest"""

import pytest
from .fixtures import (
    TestConnectionHandler,
    mysql_db,
    mcp_config
)

# Register fixtures
mysql_db = mysql_db
mcp_config = mcp_config
