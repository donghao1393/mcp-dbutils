"""Test logging module"""

import sys
import io
import pytest
from datetime import datetime
from mcp_dbutils.log import create_logger

def test_log_basic_output():
    """Test basic log output functionality"""
    # 捕获stderr输出
    stderr = io.StringIO()
    sys.stderr = stderr
    
    # 创建logger
    logger = create_logger("test")
    
    # 测试日志输出
    test_message = "Test log message"
    logger("info", test_message)
    
    # 验证输出
    output = stderr.getvalue()
    assert "test" in output
    assert "info" in output
    assert test_message in output
    assert output.count("\n") == 1  # 确保只有一行输出
    
    # 还原stderr
    sys.stderr = sys.__stderr__

def test_log_debug_mode():
    """Test debug mode behavior"""
    stderr = io.StringIO()
    sys.stderr = stderr
    
    # 创建debug模式的logger
    logger = create_logger("test", is_debug=True)
    
    # 测试debug日志
    debug_message = "Debug message"
    logger("debug", debug_message)
    
    # 验证debug消息被输出
    output = stderr.getvalue()
    assert debug_message in output
    assert "debug" in output
    
    # 清空输出缓冲
    stderr.truncate(0)
    stderr.seek(0)
    
    # 创建非debug模式的logger
    logger = create_logger("test", is_debug=False)
    
    # 测试debug日志不被输出
    logger("debug", debug_message)
    assert not stderr.getvalue()
    
    sys.stderr = sys.__stderr__

def test_log_timestamp():
    """Test log timestamp format"""
    stderr = io.StringIO()
    sys.stderr = stderr
    
    logger = create_logger("test")
    logger("info", "Test message")
    
    output = stderr.getvalue()
    
    # 验证时间戳格式 (ISO格式带毫秒)
    timestamp = output.split()[0]
    try:
        datetime.fromisoformat(timestamp.rstrip('Z'))
    except ValueError:
        pytest.fail(f"Invalid timestamp format: {timestamp}")
    
    sys.stderr = sys.__stderr__

def test_log_multiple_levels():
    """Test different log levels"""
    stderr = io.StringIO()
    sys.stderr = stderr
    
    logger = create_logger("test")
    
    # 测试不同级别的日志
    levels = ["info", "warning", "error"]
    messages = {
        "info": "Info message",
        "warning": "Warning message",
        "error": "Error message"
    }
    
    for level in levels:
        logger(level, messages[level])
    
    output = stderr.getvalue()
    
    # 验证所有级别的消息都被正确记录
    for level, message in messages.items():
        assert f"[{level}]" in output
        assert message in output
    
    sys.stderr = sys.__stderr__
