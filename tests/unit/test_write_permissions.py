"""Test write permission checking in base.py"""
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
import yaml

from mcp_dbutils.base import ConfigurationError, ConnectionServer


@pytest.fixture
def config_file():
    """Create a temporary config file for testing"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
        config = {
            "connections": {
                "test_conn": {
                    "type": "sqlite",
                    "database": ":memory:",
                    "writable": True
                },
                "test_conn_readonly": {
                    "type": "sqlite",
                    "database": ":memory:",
                    "writable": False
                },
                "test_conn_with_permissions": {
                    "type": "sqlite",
                    "database": ":memory:",
                    "writable": True,
                    "write_permissions": {
                        "tables": {
                            "users": {
                                "operations": ["INSERT", "UPDATE"]
                            },
                            "products": {
                                "operations": ["INSERT", "UPDATE", "DELETE"]
                            }
                        },
                        "default_policy": "read_only"
                    }
                },
                "test_conn_allow_all": {
                    "type": "sqlite",
                    "database": ":memory:",
                    "writable": True,
                    "write_permissions": {
                        "default_policy": "allow_all"
                    }
                }
            }
        }
        yaml.dump(config, f)
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def connection_server(config_file):
    """Create a ConnectionServer instance for testing"""
    return ConnectionServer(config_file)


class TestWritePermissions:
    """Test write permission checking"""

    @pytest.mark.asyncio
    async def test_check_write_permission_writable(self, connection_server):
        """Test _check_write_permission with writable connection"""
        # Connection is writable and has no specific permissions
        # Method should return None (no exception) if permission is granted
        await connection_server._check_write_permission("test_conn", "users", "INSERT")
        await connection_server._check_write_permission("test_conn", "users", "UPDATE")
        await connection_server._check_write_permission("test_conn", "users", "DELETE")

    @pytest.mark.asyncio
    async def test_check_write_permission_readonly(self, connection_server):
        """Test _check_write_permission with readonly connection"""
        # Connection is not writable
        with pytest.raises(ConfigurationError, match="This connection is not configured for write operations"):
            await connection_server._check_write_permission("test_conn_readonly", "users", "INSERT")

    @pytest.mark.asyncio
    async def test_check_write_permission_with_table_permissions(self, connection_server):
        """Test _check_write_permission with table-specific permissions"""
        # Table 'users' allows INSERT and UPDATE but not DELETE
        await connection_server._check_write_permission("test_conn_with_permissions", "users", "INSERT")
        await connection_server._check_write_permission("test_conn_with_permissions", "users", "UPDATE")

        with pytest.raises(ConfigurationError, match="No permission to perform DELETE operation on table users"):
            await connection_server._check_write_permission("test_conn_with_permissions", "users", "DELETE")

        # Table 'products' allows all operations
        await connection_server._check_write_permission("test_conn_with_permissions", "products", "INSERT")
        await connection_server._check_write_permission("test_conn_with_permissions", "products", "UPDATE")
        await connection_server._check_write_permission("test_conn_with_permissions", "products", "DELETE")

        # Table 'unknown_table' is not explicitly configured, default policy is read_only
        with pytest.raises(ConfigurationError, match="No permission to perform INSERT operation on table unknown_table"):
            await connection_server._check_write_permission("test_conn_with_permissions", "unknown_table", "INSERT")

    @pytest.mark.asyncio
    async def test_check_write_permission_allow_all(self, connection_server):
        """Test _check_write_permission with allow_all default policy"""
        # Default policy is allow_all
        await connection_server._check_write_permission("test_conn_allow_all", "any_table", "INSERT")
        await connection_server._check_write_permission("test_conn_allow_all", "any_table", "UPDATE")
        await connection_server._check_write_permission("test_conn_allow_all", "any_table", "DELETE")

    @pytest.mark.asyncio
    async def test_check_write_permission_case_insensitive(self, connection_server):
        """Test _check_write_permission with different table name case"""
        # Table 'users' in config, but using 'USERS' in query
        await connection_server._check_write_permission("test_conn_with_permissions", "USERS", "INSERT")
        await connection_server._check_write_permission("test_conn_with_permissions", "USERS", "UPDATE")

        with pytest.raises(ConfigurationError, match="No permission to perform DELETE operation on table USERS"):
            await connection_server._check_write_permission("test_conn_with_permissions", "USERS", "DELETE")

        # Table 'products' in config, but using mixed case 'Products' in query
        await connection_server._check_write_permission("test_conn_with_permissions", "Products", "INSERT")
        await connection_server._check_write_permission("test_conn_with_permissions", "Products", "UPDATE")
        await connection_server._check_write_permission("test_conn_with_permissions", "Products", "DELETE")
