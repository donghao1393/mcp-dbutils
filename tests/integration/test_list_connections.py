import asyncio
import tempfile

import anyio
import mcp.types as types
import pytest
import yaml
from mcp import ClientSession

from mcp_dbutils.base import ConnectionServer
from mcp_dbutils.log import create_logger

# 创建测试用的 logger
logger = create_logger("test-list-connections", True)  # debug=True 以显示所有日志


@pytest.mark.asyncio
async def test_list_connections_tool(postgres_db, sqlite_db, mcp_config):
    """Test the list_connections tool with multiple database connections"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)

        # Create bidirectional streams
        client_to_server_send, client_to_server_recv = (
            anyio.create_memory_object_stream[types.JSONRPCMessage | Exception](10)
        )
        server_to_client_send, server_to_client_recv = (
            anyio.create_memory_object_stream[types.JSONRPCMessage](10)
        )

        # Start server in background
        server_task = asyncio.create_task(
            server.server.run(
                client_to_server_recv,
                server_to_client_send,
                server.server.create_initialization_options(),
                raise_exceptions=True,
            )
        )

        try:
            # Initialize client session
            client = ClientSession(server_to_client_recv, client_to_server_send)
            async with client:
                await client.initialize()

                # List available tools
                response = await client.list_tools()
                tool_names = [tool.name for tool in response.tools]
                assert "dbutils-list-connections" in tool_names

                # Test list_connections tool without checking status
                result = await client.call_tool("dbutils-list-connections", {})
                assert len(result.content) == 1
                assert result.content[0].type == "text"

                # Check that both connections are listed
                assert "Connection: test_pg" in result.content[0].text
                assert "Type: postgres" in result.content[0].text
                assert "Connection: test_sqlite" in result.content[0].text
                assert "Type: sqlite" in result.content[0].text

                # Check that no status is shown when check_status is False
                assert "Status:" not in result.content[0].text

                # Test list_connections tool with status checking
                result = await client.call_tool(
                    "dbutils-list-connections", {"check_status": True}
                )
                assert len(result.content) == 1
                assert result.content[0].type == "text"

                # Check that status is shown when check_status is True
                assert "Status: Available" in result.content[0].text

        finally:
            # Cleanup
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass

            # Close streams
            await client_to_server_send.aclose()
            await client_to_server_recv.aclose()
            await server_to_client_send.aclose()
            await server_to_client_recv.aclose()


@pytest.mark.asyncio
async def test_list_connections_empty_config():
    """Test the list_connections tool with an empty configuration"""
    # Create an empty config
    empty_config = {"connections": {}}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as tmp:
        yaml.dump(empty_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)

        # Create bidirectional streams
        client_to_server_send, client_to_server_recv = (
            anyio.create_memory_object_stream[types.JSONRPCMessage | Exception](10)
        )
        server_to_client_send, server_to_client_recv = (
            anyio.create_memory_object_stream[types.JSONRPCMessage](10)
        )

        # Start server in background
        server_task = asyncio.create_task(
            server.server.run(
                client_to_server_recv,
                server_to_client_send,
                server.server.create_initialization_options(),
                raise_exceptions=True,
            )
        )

        try:
            # Initialize client session
            client = ClientSession(server_to_client_recv, client_to_server_send)
            async with client:
                await client.initialize()

                # Test list_connections tool with empty config
                result = await client.call_tool("dbutils-list-connections", {})
                assert len(result.content) == 1
                assert result.content[0].type == "text"
                assert (
                    "No database connections found in configuration"
                    in result.content[0].text
                )

        finally:
            # Cleanup
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass

            # Close streams
            await client_to_server_send.aclose()
            await client_to_server_recv.aclose()
            await server_to_client_send.aclose()
            await server_to_client_recv.aclose()
