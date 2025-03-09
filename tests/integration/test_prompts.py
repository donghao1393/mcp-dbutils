"""Integration tests for prompts functionality"""

import asyncio
import pytest
import tempfile
import yaml
import anyio
import mcp.types as types
from mcp import ClientSession
import mcp.server.stdio
from mcp_dbutils.base import ConnectionServer
from mcp_dbutils.log import create_logger

# 创建测试用的 logger
logger = create_logger("test-prompts", True)  # debug=True 以显示所有日志

@pytest.mark.asyncio
async def test_prompts_capability(sqlite_db, mcp_config):
    """Test that prompts capability is properly set"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)

        # Get initialization options and verify prompts capability
        init_options = server.server.create_initialization_options()
        assert init_options.capabilities is not None
        assert init_options.capabilities.prompts is not None

@pytest.mark.asyncio
async def test_list_prompts(sqlite_db, mcp_config):
    """Test that list_prompts returns an empty list"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(mcp_config, tmp)
        tmp.flush()
        server = ConnectionServer(config_path=tmp.name)

        # Create bidirectional streams with proper types
        # Client -> Server stream (server receives messages and exceptions)
        client_to_server_send, client_to_server_recv = anyio.create_memory_object_stream[types.JSONRPCMessage | Exception](10)

        # Server -> Client stream (client receives messages)
        server_to_client_send, server_to_client_recv = anyio.create_memory_object_stream[types.JSONRPCMessage](10)

        # Start server in background task with proper stream connections
        server_task = asyncio.create_task(
            server.server.run(
                client_to_server_recv,  # Server reads from client
                server_to_client_send,  # Server writes to client
                server.server.create_initialization_options(),
                raise_exceptions=True  # 让错误更容易调试
            )
        )

        try:
            try:
                # Initialize client with proper stream connections
                logger("debug", "Creating client session")
                client = ClientSession(
                    server_to_client_recv,   # Client reads from server
                    client_to_server_send    # Client writes to server
                )

                async with client:
                    # Initialize the session
                    logger("debug", "Initializing client session")
                    init_response = await client.initialize()
                    logger("debug", f"Client session initialized with response: {init_response}")

                    # Test prompts list with timeout
                    logger("debug", "Sending prompts/list request")
                    try:
                        # 使用 SDK 的 list_prompts 方法
                        response = await asyncio.wait_for(client.list_prompts(), timeout=3.0)
                        logger("debug", f"Got response: {response}")

                        # 验证响应
                        assert isinstance(response.prompts, list)
                        assert len(response.prompts) == 0
                        logger("debug", "Test completed successfully")
                    except asyncio.TimeoutError:
                        logger("error", "Request timed out after 3 seconds")
                        raise
                    except Exception as e:
                        logger("error", f"Request failed: {str(e)}")
                        logger("error", f"Request error type: {type(e)}")
                        raise

            except Exception as e:
                logger("error", f"Test failed with error: {str(e)}")
                logger("error", f"Error type: {type(e)}")
                raise

        except asyncio.TimeoutError:
            logger("error", "Test timed out")
            raise RuntimeError("Test timed out after 3 seconds")

        finally:
            # Clean up
            logger("debug", "Starting cleanup")
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                logger("debug", "Server task cancelled")
            except Exception as e:
                logger("error", f"Error during server cleanup: {str(e)}")

            # Close streams
            try:
                await client_to_server_send.aclose()
                await client_to_server_recv.aclose()
                await server_to_client_send.aclose()
                await server_to_client_recv.aclose()
                logger("debug", "All streams closed")
            except Exception as e:
                logger("error", f"Error during stream cleanup: {str(e)}")
