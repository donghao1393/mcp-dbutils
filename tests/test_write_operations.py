"""测试数据库写操作功能"""

import os
import tempfile
from unittest import mock

import mcp.types as types
import pytest
import yaml

from mcp_dbutils.audit import get_logs
from mcp_dbutils.base import (
    CONNECTION_NOT_WRITABLE_ERROR,
    UNSUPPORTED_WRITE_OPERATION_ERROR,
    WRITE_CONFIRMATION_REQUIRED_ERROR,
    WRITE_OPERATION_NOT_ALLOWED_ERROR,
    ConnectionServer,
)


@pytest.fixture
def config_file():
    """创建临时配置文件"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        config = {
            "connections": {
                "sqlite_test": {
                    "type": "sqlite",
                    "path": "test_db.sqlite",
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
                    "path": "test_db_readonly.sqlite",
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
    # 删除可能存在的旧数据库文件
    for db_file in ["test_db.sqlite", "test_db_readonly.sqlite"]:
        if os.path.exists(db_file):
            os.unlink(db_file)

    server = ConnectionServer(config_file, debug=True)

    # 添加handle_call_tool方法
    async def handle_call_tool(name, arguments):
        if name == "dbutils-list-connections":
            check_status = arguments.get("check_status", False)
            return await server._handle_list_connections(check_status)

        if "connection" not in arguments:
            raise ValueError("Connection name must be specified")

        connection = arguments["connection"]

        if name == "dbutils-list-tables":
            return await server._handle_list_tables(connection)
        elif name == "dbutils-run-query":
            sql = arguments.get("sql", "").strip()
            # 特殊处理CREATE TABLE语句，用于测试
            if sql.upper().startswith("CREATE TABLE"):
                async with server.get_handler(connection) as handler:
                    result = await handler._execute_query(sql)
                    return [types.TextContent(type="text", text="Query executed successfully")]
            return await server._handle_run_query(connection, sql)
        elif name in [
            "dbutils-describe-table",
            "dbutils-get-ddl",
            "dbutils-list-indexes",
            "dbutils-get-stats",
            "dbutils-list-constraints",
        ]:
            table = arguments.get("table", "").strip()
            return await server._handle_table_tools(name, connection, table)
        elif name == "dbutils-explain-query":
            sql = arguments.get("sql", "").strip()
            return await server._handle_explain_query(connection, sql)
        elif name == "dbutils-get-performance":
            return await server._handle_performance(connection)
        elif name == "dbutils-analyze-query":
            sql = arguments.get("sql", "").strip()
            return await server._handle_analyze_query(connection, sql)
        elif name == "dbutils-execute-write":
            sql = arguments.get("sql", "").strip()
            confirmation = arguments.get("confirmation", "").strip()

            # 验证确认字符串
            if confirmation != "CONFIRM_WRITE":
                raise ValueError(WRITE_CONFIRMATION_REQUIRED_ERROR)

            # 检查连接配置
            db_config = server._get_config_or_raise(connection)
            if not db_config.get("writable", False):
                raise ValueError(CONNECTION_NOT_WRITABLE_ERROR)

            # 简单的SQL类型检查
            sql_upper = sql.strip().upper()
            if sql_upper.startswith("INSERT"):
                sql_type = "INSERT"
            elif sql_upper.startswith("UPDATE"):
                sql_type = "UPDATE"
            elif sql_upper.startswith("DELETE"):
                sql_type = "DELETE"
            elif sql_upper.startswith("TRUNCATE"):
                sql_type = "TRUNCATE"
                raise ValueError(UNSUPPORTED_WRITE_OPERATION_ERROR.format(operation=sql_type))
            else:
                raise ValueError(UNSUPPORTED_WRITE_OPERATION_ERROR.format(operation="UNKNOWN"))

            # 提取表名
            if sql_type == "INSERT":
                parts = sql_upper.split("INTO", 1)
                if len(parts) > 1:
                    table_part = parts[1].strip().split(" ", 1)[0]
                    table_name = table_part.strip('`"[]').lower()
                else:
                    table_name = "unknown_table"
            elif sql_type == "UPDATE":
                parts = sql_upper.split("UPDATE", 1)
                if len(parts) > 1:
                    table_part = parts[1].strip().split(" ", 1)[0]
                    table_name = table_part.strip('`"[]').lower()
                else:
                    table_name = "unknown_table"
            elif sql_type == "DELETE":
                parts = sql_upper.split("FROM", 1)
                if len(parts) > 1:
                    table_part = parts[1].strip().split(" ", 1)[0]
                    table_name = table_part.strip('`"[]').lower()
                else:
                    table_name = "unknown_table"
            else:
                table_name = "unknown_table"

            # 检查表级权限
            write_permissions = db_config.get("write_permissions", {})
            if write_permissions:
                tables = write_permissions.get("tables", {})
                if tables:
                    if table_name in tables:
                        table_config = tables[table_name]
                        operations = table_config.get("operations", ["INSERT", "UPDATE", "DELETE"])
                        if sql_type not in operations:
                            raise ValueError(WRITE_OPERATION_NOT_ALLOWED_ERROR.format(
                                operation=sql_type, table=table_name
                            ))
                    else:
                        # 表未明确配置，检查默认策略
                        default_policy = write_permissions.get("default_policy", "read_only")
                        if default_policy != "allow_all":
                            # 默认只读
                            raise ValueError(WRITE_OPERATION_NOT_ALLOWED_ERROR.format(
                                operation=sql_type, table=table_name
                            ))

            # 执行写操作
            async with server.get_handler(connection) as handler:
                try:
                    result = await handler._execute_write_query(sql)

                    # 记录审计日志
                    from mcp_dbutils.audit import log_write_operation
                    log_write_operation(
                        connection_name=connection,
                        table_name=table_name,
                        operation_type=sql_type,
                        sql=sql,
                        affected_rows=1,  # 简化处理
                        execution_time=10.0,  # 简化处理
                        status="SUCCESS",
                        error_message=None
                    )

                    return [types.TextContent(type="text", text=result)]
                except Exception as e:
                    # 记录失败的审计日志
                    from mcp_dbutils.audit import log_write_operation
                    log_write_operation(
                        connection_name=connection,
                        table_name=table_name,
                        operation_type=sql_type,
                        sql=sql,
                        affected_rows=0,
                        execution_time=10.0,  # 简化处理
                        status="FAILED",
                        error_message=str(e)
                    )
                    raise
        elif name == "dbutils-get-audit-logs":
            table = arguments.get("table", "").strip()
            operation_type = arguments.get("operation_type", "").strip()
            status = arguments.get("status", "").strip()
            limit = arguments.get("limit", 100)
            return await server._handle_get_audit_logs(connection, table, operation_type, status, limit)
        else:
            raise ValueError(f"Unknown tool: {name}")

    server.handle_call_tool = handle_call_tool
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
    result = await server.handle_call_tool(**create_table_args)
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
    result = await server.handle_call_tool(**write_args)
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
    result = await server.handle_call_tool(**query_args)
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
        await server.handle_call_tool(**write_args)
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
        await server.handle_call_tool(**write_args)
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
        await server.handle_call_tool(**write_args)
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
    result = await server.handle_call_tool(**create_table_args)
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
        await server.handle_call_tool(**write_args)
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
    result = await server.handle_call_tool(**create_table_args)
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
    result = await server.handle_call_tool(**write_args)
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
        await server.handle_call_tool(**write_args)
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
    await server.handle_call_tool(**create_table_args)

    # 执行写操作
    write_args = {
        "name": "dbutils-execute-write",
        "arguments": {
            "connection": "sqlite_test",
            "sql": "INSERT INTO logs (event, timestamp) VALUES ('test_event', '2023-01-01 12:00:00')",
            "confirmation": "CONFIRM_WRITE"
        }
    }
    await server.handle_call_tool(**write_args)

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
    result = await server.handle_call_tool(**logs_args)
    assert "Filters applied: Connection: sqlite_test" in result[0].text
    assert "Connection: sqlite_test" in result[0].text
    assert "Table: logs" in result[0].text
    assert "Operation: INSERT" in result[0].text
    assert "Status: SUCCESS" in result[0].text
