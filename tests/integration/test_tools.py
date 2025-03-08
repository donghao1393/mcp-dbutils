import pytest
import tempfile
import yaml
from mcp_dbutils.base import DatabaseServer, ConfigurationError

@pytest.mark.asyncio
async def test_list_tables_tool(postgres_db, sqlite_db, mcp_config):
    """Test the list_tables tool with both PostgreSQL and SQLite databases"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = DatabaseServer(config_path=tmp.name)

        # List available tools
        tools = await server.server.list_tools()
        tool_names = [tool.name for tool in tools]
        assert "list_tables" in tool_names
        assert "query" in tool_names

        # Test list_tables tool with PostgreSQL
        result = await server.server.call_tool(
            name="list_tables",
            arguments={"database": "test_pg"}
        )
        assert len(result) == 1
        assert result[0].type == "text"
        assert "users" in result[0].text

        # Test list_tables tool with SQLite
        result = await server.server.call_tool(
            name="list_tables",
            arguments={"database": "test_sqlite"}
        )
        assert len(result) == 1
        assert result[0].type == "text"
        assert "products" in result[0].text

@pytest.mark.asyncio
async def test_list_tables_tool_errors(postgres_db, mcp_config):
    """Test error cases for list_tables tool"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = DatabaseServer(config_path=tmp.name)

        # Test missing database parameter
        with pytest.raises(ConfigurationError, match="Database configuration name must be specified"):
            await server.server.call_tool(
                name="list_tables",
                arguments={}
            )

        # Test invalid database name
        with pytest.raises(ConfigurationError, match="Database configuration not found"):
            await server.server.call_tool(
                name="list_tables",
                arguments={"database": "nonexistent_db"}
            )
