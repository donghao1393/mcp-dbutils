"""Integration tests for advanced database tools"""

import asyncio
import pytest
import tempfile
import yaml
import anyio
import mcp.types as types
from mcp import ClientSession
from mcp.shared.exceptions import McpError
from mcp_dbutils.base import ConnectionServer
from mcp_dbutils.log import create_logger

# 创建测试用的 logger
logger = create_logger("test-tools-advanced", True)  # debug=True 以显示所有日志

@pytest.mark.asyncio
async def test_get_stats_tool(postgres_db, sqlite_db, mcp_config):
    """Test the dbutils-get-stats tool with both PostgreSQL and SQLite connections"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)

        # Create bidirectional streams
        client_to_server_send, client_to_server_recv = anyio.create_memory_object_stream[types.JSONRPCMessage | Exception](10)
        server_to_client_send, server_to_client_recv = anyio.create_memory_object_stream[types.JSONRPCMessage](10)

        # Start server in background
        server_task = asyncio.create_task(
            server.server.run(
                client_to_server_recv,
                server_to_client_send,
                server.server.create_initialization_options(),
                raise_exceptions=True
            )
        )

        try:
            # Initialize client session
            client = ClientSession(server_to_client_recv, client_to_server_send)
            async with client:
                await client.initialize()

                # Verify tool is available
                response = await client.list_tools()
                tool_names = [tool.name for tool in response.tools]
                assert "dbutils-get-stats" in tool_names

                # Test PostgreSQL stats
                pg_args = {"connection": "test_pg", "table": "users"}
                result = await client.call_tool("dbutils-get-stats", pg_args)
                assert len(result.content) == 1
                assert result.content[0].type == "text"
                assert "[postgres]" in result.content[0].text
                assert "Table Statistics for users" in result.content[0].text

                # Test SQLite stats
                sqlite_args = {"connection": "test_sqlite", "table": "products"}
                result = await client.call_tool("dbutils-get-stats", sqlite_args)
                assert len(result.content) == 1
                assert result.content[0].type == "text"
                assert "[sqlite]" in result.content[0].text
                assert "Table Statistics for products" in result.content[0].text

        finally:
            # Cleanup
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass

            await client_to_server_send.aclose()
            await client_to_server_recv.aclose()
            await server_to_client_send.aclose()
            await server_to_client_recv.aclose()

@pytest.mark.asyncio
async def test_list_constraints_tool(postgres_db, sqlite_db, mcp_config):
    """Test the dbutils-list-constraints tool with both PostgreSQL and SQLite connections"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)

        client_to_server_send, client_to_server_recv = anyio.create_memory_object_stream[types.JSONRPCMessage | Exception](10)
        server_to_client_send, server_to_client_recv = anyio.create_memory_object_stream[types.JSONRPCMessage](10)

        server_task = asyncio.create_task(
            server.server.run(
                client_to_server_recv,
                server_to_client_send,
                server.server.create_initialization_options(),
                raise_exceptions=True
            )
        )

        try:
            client = ClientSession(server_to_client_recv, client_to_server_send)
            async with client:
                await client.initialize()

                response = await client.list_tools()
                tool_names = [tool.name for tool in response.tools]
                assert "dbutils-list-constraints" in tool_names

                # Test PostgreSQL constraints
                pg_args = {"connection": "test_pg", "table": "users"}
                result = await client.call_tool("dbutils-list-constraints", pg_args)
                assert len(result.content) == 1
                assert result.content[0].type == "text"
                assert "[postgres]" in result.content[0].text
                assert "Constraints for users" in result.content[0].text

                # Test SQLite constraints
                sqlite_args = {"connection": "test_sqlite", "table": "products"}
                result = await client.call_tool("dbutils-list-constraints", sqlite_args)
                assert len(result.content) == 1
                assert result.content[0].type == "text"
                assert "[sqlite]" in result.content[0].text
                assert "Constraints for products" in result.content[0].text

        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass

            await client_to_server_send.aclose()
            await client_to_server_recv.aclose()
            await server_to_client_send.aclose()
            await server_to_client_recv.aclose()

@pytest.mark.asyncio
async def test_explain_query_tool(postgres_db, sqlite_db, mcp_config):
    """Test the dbutils-explain-query tool with both PostgreSQL and SQLite connections"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)

        client_to_server_send, client_to_server_recv = anyio.create_memory_object_stream[types.JSONRPCMessage | Exception](10)
        server_to_client_send, server_to_client_recv = anyio.create_memory_object_stream[types.JSONRPCMessage](10)

        server_task = asyncio.create_task(
            server.server.run(
                client_to_server_recv,
                server_to_client_send,
                server.server.create_initialization_options(),
                raise_exceptions=True
            )
        )

        try:
            client = ClientSession(server_to_client_recv, client_to_server_send)
            async with client:
                await client.initialize()

                response = await client.list_tools()
                tool_names = [tool.name for tool in response.tools]
                assert "dbutils-explain-query" in tool_names

                # Test PostgreSQL explain
                pg_args = {
                    "connection": "test_pg",
                    "sql": "SELECT * FROM users WHERE id > 0"
                }
                result = await client.call_tool("dbutils-explain-query", pg_args)
                assert len(result.content) == 1
                assert result.content[0].type == "text"
                assert "[postgres]" in result.content[0].text
                assert "Query Execution Plan" in result.content[0].text

                # Test SQLite explain
                sqlite_args = {
                    "connection": "test_sqlite",
                    "sql": "SELECT * FROM products WHERE id > 0"
                }
                result = await client.call_tool("dbutils-explain-query", sqlite_args)
                assert len(result.content) == 1
                assert result.content[0].type == "text"
                assert "[sqlite]" in result.content[0].text
                assert "Query Execution Plan" in result.content[0].text

        finally:
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass

            await client_to_server_send.aclose()
            await client_to_server_recv.aclose()
            await server_to_client_send.aclose()
            await server_to_client_recv.aclose()
