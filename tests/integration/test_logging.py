"""Test MCP logging functionality"""

import pytest
import asyncio
import logging
from unittest.mock import MagicMock, patch, call
from mcp.server import Server
from mcp.types import LoggingMessageNotification

from mcp_dbutils.base import ConnectionHandler, ConnectionServer
from mcp_dbutils.log import create_logger
from . import conftest

TestConnectionHandler = conftest.TestConnectionHandler

@pytest.mark.asyncio
async def test_handler_logging():
    """Test logging in ConnectionHandler"""
    
    # 创建一个模拟的session
    mock_session = MagicMock()
    mock_session.request_context.session.send_log_message = MagicMock()
    
    # 创建测试handler
    handler = TestConnectionHandler("test_config.yaml", "test_conn")
    handler._session = mock_session
    
    # 测试不同级别的日志
    test_levels = ["debug", "info", "notice", "warning", "error", "critical", "alert", "emergency"]
    
    for level in test_levels:
        mock_session.request_context.session.send_log_message.reset_mock()
        message = f"Test {level} message"
        handler.send_log(level, message)
        
        # 验证MCP日志消息被发送
        mock_session.request_context.session.send_log_message.assert_called_with(
            level=level,
            data=message
        )

@pytest.mark.asyncio
async def test_server_logging():
    """Test logging in ConnectionServer"""
    
    # 创建一个模拟的Server和Logger
    mock_server = MagicMock()
    mock_logger = MagicMock()
    
    # 设置mock session和send_log_message
    mock_send_log = MagicMock()
    mock_server.session = MagicMock()
    mock_server.session.send_log_message = mock_send_log
    
    # 创建补丁
    patches = [
        patch("mcp_dbutils.base.Server", return_value=mock_server),
        patch("mcp_dbutils.base.create_logger", return_value=mock_logger)
    ]
    
    # 启动所有补丁
    for p in patches:
        p.start()
        
    try:
        server = ConnectionServer("test_config.yaml")
        
        # 测试不同级别的日志
        test_levels = ["debug", "info", "notice", "warning", "error", "critical", "alert", "emergency"]
        
        for level in test_levels:
            # 重置mock计数
            mock_logger.reset_mock()
            mock_send_log.reset_mock()
            
            message = f"Test {level} message"
            server.send_log(level, message)
            
            # 验证本地日志被写入
            mock_logger.assert_called_once_with(level, message)
            
            # 验证MCP日志消息被发送
            mock_send_log.assert_called_once_with(
                level=level,
                data=message
            )
    finally:
        # 停止所有补丁
        for p in patches:
            p.stop()

@pytest.mark.asyncio
async def test_handler_session_inheritance():
    """Test session inheritance in handlers"""
    
    # 创建一个模拟的Server
    mock_server = MagicMock()
    mock_session = MagicMock()
    mock_request_context = MagicMock()
    mock_request_context.session = mock_session
    mock_session.request_context = mock_request_context
    mock_session.send_log_message = MagicMock()
    mock_server.session = mock_session
    
    # 创建测试配置文件内容
    test_config = {
        "connections": {
            "test_conn": {
                "type": "sqlite"  # 使用sqlite类型
            }
        }
    }
    
    test_handler = TestConnectionHandler("test_config.yaml", "test_conn")
    test_handler.stats.to_dict = MagicMock(return_value={})  # 简化统计信息
    
    with patch("mcp.server.Server", return_value=mock_server), \
         patch("builtins.open"), \
         patch("yaml.safe_load", return_value=test_config), \
         patch("mcp_dbutils.sqlite.handler.SQLiteHandler", return_value=test_handler):
            
        server = ConnectionServer("test_config.yaml")
        server.server = mock_server  # 确保server有正确的session
            
        # 使用get_handler创建handler
        async with server.get_handler("test_conn") as handler:
            # 重置所有mock
            mock_session.send_log_message.reset_mock()
            mock_session.request_context.session.send_log_message.reset_mock()
            
            # 发送测试日志
            message = "Test message"
            handler.send_log("info", message)
            
            # 验证日志消息通过server的session发送
            mock_session.request_context.session.send_log_message.assert_called_with(
                level="info",
                data=message
            )
