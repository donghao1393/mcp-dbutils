"""测试数据库写操作功能"""

import asyncio
import json
import os
import tempfile
from unittest import mock

import pytest
import yaml

from mcp_dbutils.audit import get_logs
from mcp_dbutils.base import (
    CONNECTION_NOT_WRITABLE_ERROR,
    ConnectionServer,
    UNSUPPORTED_WRITE_OPERATION_ERROR,
    WRITE_CONFIRMATION_REQUIRED_ERROR,
    WRITE_OPERATION_NOT_ALLOWED_ERROR,
)


@pytest.fixture
def config_file():
    """创建临时配置文件"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        config = {
            "connections": {
                "sqlite_test": {
                    "type": "sqlite",
                    "path": ":memory:",
                    "writable": True,
                    "write_permissions": {
                        "default_policy": "read_only",
                        "tables": {
                            "users": {
                                "operations": ["INSERT", "UPDATE"]
                            },
                            "logs": {
                                "operations": ["INSERT", "UPDATE", "DELETE"]
                            }
                        }
                    }
                },
                "sqlite_readonly": {
                    "type": "sqlite",
                    "path": ":memory:",
                    "writable": False
                }
            }
        }
        yaml.dump(config, f)
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def server(config_file):
    """创建服务器实例"""
    server = ConnectionServer(config_file, debug=True)
    yield server


@pytest.mark.asyncio
async def test_execute_write_query_success(server):
    """测试成功执行写操作"""
    # 创建表
    create_table_args = {
        "name": "dbutils-run-query",
        "arguments": {
            "connection": "sqlite_test",
            "sql": "CREATE TABLE logs (id INTEGER PRIMARY KEY, event TEXT, timestamp TEXT)"
        }
    }
    connection = create_table_args["arguments"]["connection"]
    sql = create_table_args["arguments"]["sql"]
    result = await server._handle_run_query(connection, sql)
    assert "Query executed successfully" in result[0].text

    # 执行写操作
    write_args = {
        "name": "dbutils-execute-write",
        "arguments": {
            "connection": "sqlite_test",
            "sql": "INSERT INTO logs (event, timestamp) VALUES ('test_event', '2023-01-01 12:00:00')",
            "confirmation": "CONFIRM_WRITE"
        }
    }
    connection = write_args["arguments"]["connection"]
    sql = write_args["arguments"]["sql"]
    confirmation = write_args["arguments"]["confirmation"]
    result = await server._handle_execute_write(connection, sql, confirmation)
    assert "Write operation executed successfully" in result[0].text
    assert "1 row affected" in result[0].text

    # 验证数据已写入
    query_args = {
        "name": "dbutils-run-query",
        "arguments": {
            "connection": "sqlite_test",
            "sql": "SELECT * FROM logs"
        }
    }
    connection = query_args["arguments"]["connection"]
    sql = query_args["arguments"]["sql"]
    result = await server._handle_run_query(connection, sql)
    assert "test_event" in result[0].text
    assert "2023-01-01 12:00:00" in result[0].text

    # 验证审计日志
    logs = get_logs(table_name="logs", operation_type="INSERT")
    assert len(logs) > 0
    assert logs[0]["table_name"] == "logs"
    assert logs[0]["operation_type"] == "INSERT"
    assert logs[0]["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_execute_write_query_readonly_connection(server):
    """测试只读连接的写操作"""
    write_args = {
        "name": "dbutils-execute-write",
        "arguments": {
            "connection": "sqlite_readonly",
            "sql": "INSERT INTO logs (event, timestamp) VALUES ('test_event', '2023-01-01 12:00:00')",
            "confirmation": "CONFIRM_WRITE"
        }
    }
    with pytest.raises(Exception) as excinfo:
        connection = write_args["arguments"]["connection"]
        sql = write_args["arguments"]["sql"]
        confirmation = write_args["arguments"]["confirmation"]
        await server._handle_execute_write(connection, sql, confirmation)
    assert CONNECTION_NOT_WRITABLE_ERROR in str(excinfo.value)


@pytest.mark.asyncio
async def test_execute_write_query_without_confirmation(server):
    """测试没有确认的写操作"""
    write_args = {
        "name": "dbutils-execute-write",
        "arguments": {
            "connection": "sqlite_test",
            "sql": "INSERT INTO logs (event, timestamp) VALUES ('test_event', '2023-01-01 12:00:00')",
            "confirmation": "YES"  # 错误的确认字符串
        }
    }
    with pytest.raises(Exception) as excinfo:
        connection = write_args["arguments"]["connection"]
        sql = write_args["arguments"]["sql"]
        confirmation = write_args["arguments"]["confirmation"]
        await server._handle_execute_write(connection, sql, confirmation)
    assert WRITE_CONFIRMATION_REQUIRED_ERROR in str(excinfo.value)


@pytest.mark.asyncio
async def test_execute_write_query_unsupported_operation(server):
    """测试不支持的写操作"""
    write_args = {
        "name": "dbutils-execute-write",
        "arguments": {
            "connection": "sqlite_test",
            "sql": "TRUNCATE TABLE logs",
            "confirmation": "CONFIRM_WRITE"
        }
    }
    with pytest.raises(Exception) as excinfo:
        connection = write_args["arguments"]["connection"]
        sql = write_args["arguments"]["sql"]
        confirmation = write_args["arguments"]["confirmation"]
        await server._handle_execute_write(connection, sql, confirmation)
    assert "Unsupported SQL operation" in str(excinfo.value)


@pytest.mark.asyncio
async def test_execute_write_query_unauthorized_table(server):
    """测试未授权表的写操作"""
    # 创建表
    create_table_args = {
        "name": "dbutils-run-query",
        "arguments": {
            "connection": "sqlite_test",
            "sql": "CREATE TABLE unauthorized_table (id INTEGER PRIMARY KEY, data TEXT)"
        }
    }
    connection = create_table_args["arguments"]["connection"]
    sql = create_table_args["arguments"]["sql"]
    result = await server._handle_run_query(connection, sql)
    assert "Query executed successfully" in result[0].text

    # 尝试写入未授权的表
    write_args = {
        "name": "dbutils-execute-write",
        "arguments": {
            "connection": "sqlite_test",
            "sql": "INSERT INTO unauthorized_table (data) VALUES ('test_data')",
            "confirmation": "CONFIRM_WRITE"
        }
    }
    with pytest.raises(Exception) as excinfo:
        connection = write_args["arguments"]["connection"]
        sql = write_args["arguments"]["sql"]
        confirmation = write_args["arguments"]["confirmation"]
        await server._handle_execute_write(connection, sql, confirmation)
    assert "No permission to perform" in str(excinfo.value)


@pytest.mark.asyncio
async def test_execute_write_query_unauthorized_operation(server):
    """测试未授权操作的写操作"""
    # 创建表
    create_table_args = {
        "name": "dbutils-run-query",
        "arguments": {
            "connection": "sqlite_test",
            "sql": "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)"
        }
    }
    connection = create_table_args["arguments"]["connection"]
    sql = create_table_args["arguments"]["sql"]
    result = await server._handle_run_query(connection, sql)
    assert "Query executed successfully" in result[0].text

    # 执行授权的操作
    write_args = {
        "name": "dbutils-execute-write",
        "arguments": {
            "connection": "sqlite_test",
            "sql": "INSERT INTO users (name, email) VALUES ('Test User', 'test@example.com')",
            "confirmation": "CONFIRM_WRITE"
        }
    }
    connection = write_args["arguments"]["connection"]
    sql = write_args["arguments"]["sql"]
    confirmation = write_args["arguments"]["confirmation"]
    result = await server._handle_execute_write(connection, sql, confirmation)
    assert "Write operation executed successfully" in result[0].text

    # 尝试执行未授权的操作
    write_args = {
        "name": "dbutils-execute-write",
        "arguments": {
            "connection": "sqlite_test",
            "sql": "DELETE FROM users WHERE id = 1",
            "confirmation": "CONFIRM_WRITE"
        }
    }
    with pytest.raises(Exception) as excinfo:
        connection = write_args["arguments"]["connection"]
        sql = write_args["arguments"]["sql"]
        confirmation = write_args["arguments"]["confirmation"]
        await server._handle_execute_write(connection, sql, confirmation)
    assert "No permission to perform DELETE operation on table users" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_audit_logs(server):
    """测试获取审计日志"""
    # 创建表
    create_table_args = {
        "name": "dbutils-run-query",
        "arguments": {
            "connection": "sqlite_test",
            "sql": "CREATE TABLE logs (id INTEGER PRIMARY KEY, event TEXT, timestamp TEXT)"
        }
    }
    connection = create_table_args["arguments"]["connection"]
    sql = create_table_args["arguments"]["sql"]
    await server._handle_run_query(connection, sql)

    # 执行写操作
    write_args = {
        "name": "dbutils-execute-write",
        "arguments": {
            "connection": "sqlite_test",
            "sql": "INSERT INTO logs (event, timestamp) VALUES ('test_event', '2023-01-01 12:00:00')",
            "confirmation": "CONFIRM_WRITE"
        }
    }
    connection = write_args["arguments"]["connection"]
    sql = write_args["arguments"]["sql"]
    confirmation = write_args["arguments"]["confirmation"]
    await server._handle_execute_write(connection, sql, confirmation)

    # 获取审计日志
    logs_args = {
        "name": "dbutils-get-audit-logs",
        "arguments": {
            "connection": "sqlite_test",
            "table": "logs",
            "operation_type": "INSERT",
            "status": "SUCCESS",
            "limit": 10
        }
    }
    connection = logs_args["arguments"]["connection"]
    table = logs_args["arguments"]["table"]
    operation_type = logs_args["arguments"]["operation_type"]
    status = logs_args["arguments"]["status"]
    limit = logs_args["arguments"]["limit"]
    result = await server._handle_get_audit_logs(connection, table, operation_type, status, limit)
    assert "Audit Logs" in result[0].text
    assert "Connection: sqlite_test" in result[0].text
    assert "Table: logs" in result[0].text
    assert "Operation: INSERT" in result[0].text
    assert "Status: SUCCESS" in result[0].text
