"""Test audit module"""

import json
import logging
import os
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from mcp_dbutils.audit import (
    _get_user_context,
    _sanitize_sql,
    _setup_file_handler,
    configure_audit_logging,
    format_logs,
    get_logs,
    log_write_operation,
)


class TestAudit:
    """Test audit module"""

    def setup_method(self):
        """Setup test environment"""
        # Reset audit configuration to default
        from mcp_dbutils.audit import _audit_config, _memory_buffer
        _audit_config.update({
            "enabled": True,
            "file_storage": {
                "enabled": True,
                "path": "logs/audit",
                "max_file_size": 10 * 1024 * 1024,  # 10MB
                "backup_count": 10
            },
            "content": {
                "sanitize_sql": True,
                "include_user_context": True
            }
        })
        _memory_buffer.clear()

    def test_configure_audit_logging(self):
        """Test configure_audit_logging function"""
        # Test with empty config
        configure_audit_logging({})
        from mcp_dbutils.audit import _audit_config
        assert _audit_config["enabled"] is True
        assert _audit_config["file_storage"]["enabled"] is True

        # Test with custom config
        with patch("mcp_dbutils.audit._setup_file_handler") as mock_setup:
            configure_audit_logging({
                "enabled": False,
                "file_storage": {
                    "enabled": False,
                    "path": "custom/path"
                },
                "memory_buffer": {
                    "size": 500
                }
            })
            from mcp_dbutils.audit import _audit_config, _memory_buffer_size
            assert _audit_config["enabled"] is False
            assert _audit_config["file_storage"]["enabled"] is False
            assert _audit_config["file_storage"]["path"] == "custom/path"
            assert _memory_buffer_size == 500
            # File handler should not be setup when file_storage is disabled
            mock_setup.assert_not_called()

    def test_setup_file_handler(self):
        """Test _setup_file_handler function"""
        # Create a temporary directory for logs
        with tempfile.TemporaryDirectory() as temp_dir:
            from mcp_dbutils.audit import _audit_config, audit_logger

            # Configure audit logging to use the temporary directory
            _audit_config["file_storage"]["path"] = temp_dir

            # Remove existing handlers
            for handler in audit_logger.handlers[:]:
                audit_logger.removeHandler(handler)

            # Setup file handler
            _setup_file_handler()

            # Verify that the handler was added
            assert len(audit_logger.handlers) == 1
            assert isinstance(audit_logger.handlers[0], logging.FileHandler)
            assert audit_logger.handlers[0].baseFilename.endswith("dbutils-audit.log")

            # Verify that the directory was created
            assert os.path.exists(temp_dir)

    def test_sanitize_sql(self):
        """Test _sanitize_sql function"""
        # Test with sanitize_sql enabled
        from mcp_dbutils.audit import _audit_config
        _audit_config["content"]["sanitize_sql"] = True

        # Test INSERT statement
        sql = "INSERT INTO users (name, email) VALUES ('John Doe', 'john@example.com')"
        sanitized = _sanitize_sql(sql)
        assert "VALUES (?)" in sanitized
        assert "'John Doe'" not in sanitized

        # Test UPDATE statement with WHERE clause
        sql = "UPDATE users SET name = 'Jane Doe' WHERE id = 123"
        sanitized = _sanitize_sql(sql)
        assert "WHERE id = ?" in sanitized
        assert "123" not in sanitized

        # Test with sanitize_sql disabled
        _audit_config["content"]["sanitize_sql"] = False
        sql = "INSERT INTO users (name) VALUES ('John Doe')"
        sanitized = _sanitize_sql(sql)
        assert sanitized == sql

    def test_get_user_context(self):
        """Test _get_user_context function"""
        # Test with include_user_context enabled
        from mcp_dbutils.audit import _audit_config
        _audit_config["content"]["include_user_context"] = True
        assert _get_user_context() is None  # Default implementation returns None

        # Test with include_user_context disabled
        _audit_config["content"]["include_user_context"] = False
        assert _get_user_context() is None

    def test_log_write_operation(self):
        """Test log_write_operation function"""
        # Test with audit logging enabled
        from mcp_dbutils.audit import _audit_config, _memory_buffer
        _audit_config["enabled"] = True
        _audit_config["file_storage"]["enabled"] = False  # Disable file logging for this test

        # Log a successful operation
        log_write_operation(
            connection_name="test_conn",
            table_name="users",
            operation_type="INSERT",
            sql="INSERT INTO users (name) VALUES ('John Doe')",
            affected_rows=1,
            execution_time=10.5,
            status="SUCCESS"
        )

        # Verify that the log was added to the memory buffer
        assert len(_memory_buffer) == 1
        log = _memory_buffer[0]
        assert log["connection_name"] == "test_conn"
        assert log["table_name"] == "users"
        assert log["operation_type"] == "INSERT"
        assert "VALUES (?)" in log["sql_statement"]
        assert log["affected_rows"] == 1
        assert log["status"] == "SUCCESS"
        assert log["execution_time"] == 10.5

        # Log a failed operation
        log_write_operation(
            connection_name="test_conn",
            table_name="users",
            operation_type="UPDATE",
            sql="UPDATE users SET name = 'Jane Doe' WHERE id = 123",
            affected_rows=0,
            execution_time=5.2,
            status="FAILED",
            error_message="Record not found"
        )

        # Verify that the log was added to the memory buffer
        assert len(_memory_buffer) == 2
        log = _memory_buffer[1]
        assert log["connection_name"] == "test_conn"
        assert log["table_name"] == "users"
        assert log["operation_type"] == "UPDATE"
        assert log["affected_rows"] == 0
        assert log["status"] == "FAILED"
        assert log["execution_time"] == 5.2
        assert log["error_message"] == "Record not found"

        # Test with audit logging disabled
        _audit_config["enabled"] = False
        _memory_buffer.clear()

        log_write_operation(
            connection_name="test_conn",
            table_name="users",
            operation_type="DELETE",
            sql="DELETE FROM users WHERE id = 123",
            affected_rows=1,
            execution_time=3.0,
            status="SUCCESS"
        )

        # Verify that no log was added to the memory buffer
        assert len(_memory_buffer) == 0

    def test_log_write_operation_with_file(self):
        """Test log_write_operation function with file logging"""
        # Create a temporary directory for logs
        with tempfile.TemporaryDirectory() as temp_dir:
            from mcp_dbutils.audit import _audit_config, audit_logger

            # Configure audit logging to use the temporary directory
            _audit_config["enabled"] = True
            _audit_config["file_storage"]["enabled"] = True
            _audit_config["file_storage"]["path"] = temp_dir

            # Remove existing handlers
            for handler in audit_logger.handlers[:]:
                audit_logger.removeHandler(handler)

            # Setup file handler
            _setup_file_handler()

            # Log a write operation
            with patch("mcp_dbutils.audit.audit_logger.info") as mock_info:
                log_write_operation(
                    connection_name="test_conn",
                    table_name="users",
                    operation_type="INSERT",
                    sql="INSERT INTO users (name) VALUES ('John Doe')",
                    affected_rows=1,
                    execution_time=10.5,
                    status="SUCCESS"
                )

                # Verify that the logger was called
                mock_info.assert_called_once()
                log_json = mock_info.call_args[0][0]
                log_data = json.loads(log_json)
                assert log_data["connection_name"] == "test_conn"
                assert log_data["table_name"] == "users"
                assert log_data["operation_type"] == "INSERT"

    def test_get_logs(self):
        """Test get_logs function"""
        from mcp_dbutils.audit import _memory_buffer

        # Add some test logs
        _memory_buffer.clear()
        _memory_buffer.extend([
            {
                "timestamp": "2023-01-01T12:00:00",
                "connection_name": "conn1",
                "table_name": "users",
                "operation_type": "INSERT",
                "sql_statement": "INSERT INTO users VALUES (?)",
                "affected_rows": 1,
                "status": "SUCCESS",
                "execution_time": 10.5,
                "user_context": None
            },
            {
                "timestamp": "2023-01-02T12:00:00",
                "connection_name": "conn1",
                "table_name": "orders",
                "operation_type": "UPDATE",
                "sql_statement": "UPDATE orders SET status = ? WHERE id = ?",
                "affected_rows": 1,
                "status": "SUCCESS",
                "execution_time": 5.2,
                "user_context": None
            },
            {
                "timestamp": "2023-01-03T12:00:00",
                "connection_name": "conn2",
                "table_name": "products",
                "operation_type": "DELETE",
                "sql_statement": "DELETE FROM products WHERE id = ?",
                "affected_rows": 1,
                "status": "FAILED",
                "execution_time": 3.0,
                "error_message": "Foreign key constraint",
                "user_context": None
            }
        ])

        # Test without filters
        logs = get_logs()
        assert len(logs) == 3

        # Test with connection_name filter
        logs = get_logs(connection_name="conn1")
        assert len(logs) == 2
        assert all(log["connection_name"] == "conn1" for log in logs)

        # Test with table_name filter
        logs = get_logs(table_name="users")
        assert len(logs) == 1
        assert logs[0]["table_name"] == "users"

        # Test with operation_type filter
        logs = get_logs(operation_type="DELETE")
        assert len(logs) == 1
        assert logs[0]["operation_type"] == "DELETE"

        # Test with status filter
        logs = get_logs(status="FAILED")
        assert len(logs) == 1
        assert logs[0]["status"] == "FAILED"

        # Test with start_time filter
        logs = get_logs(start_time="2023-01-02T00:00:00")
        assert len(logs) == 2

        # Test with end_time filter
        logs = get_logs(end_time="2023-01-02T23:59:59")
        assert len(logs) == 2

        # Test with limit
        logs = get_logs(limit=1)
        assert len(logs) == 1

    def test_format_logs(self):
        """Test format_logs function"""
        # Test with empty logs
        formatted = format_logs([])
        assert "No audit logs found" in formatted

        # Test with logs
        logs = [
            {
                "timestamp": "2023-01-01T12:00:00",
                "connection_name": "conn1",
                "table_name": "users",
                "operation_type": "INSERT",
                "sql_statement": "INSERT INTO users VALUES (?)",
                "affected_rows": 1,
                "status": "SUCCESS",
                "execution_time": 10.5,
                "user_context": None
            },
            {
                "timestamp": "2023-01-02T12:00:00",
                "connection_name": "conn1",
                "table_name": "orders",
                "operation_type": "UPDATE",
                "sql_statement": "UPDATE orders SET status = ? WHERE id = ?",
                "affected_rows": 1,
                "status": "SUCCESS",
                "execution_time": 5.2,
                "user_context": "admin"
            },
            {
                "timestamp": "2023-01-03T12:00:00",
                "connection_name": "conn2",
                "table_name": "products",
                "operation_type": "DELETE",
                "sql_statement": "DELETE FROM products WHERE id = ?",
                "affected_rows": 0,
                "status": "FAILED",
                "execution_time": 3.0,
                "error_message": "Foreign key constraint",
                "user_context": None
            }
        ]

        formatted = format_logs(logs)
        assert "Audit Logs:" in formatted
        assert "Timestamp: 2023-01-01T12:00:00" in formatted
        assert "Connection: conn1" in formatted
        assert "Table: users" in formatted
        assert "Operation: INSERT" in formatted
        assert "Status: SUCCESS" in formatted
        assert "Affected Rows: 1" in formatted
        assert "Execution Time: 10.50ms" in formatted
        assert "SQL: INSERT INTO users VALUES (?)" in formatted

        # Verify that error message is included
        assert "Error: Foreign key constraint" in formatted

        # Verify that user context is included
        assert "User Context: admin" in formatted

    def test_memory_buffer_size_limit(self):
        """Test memory buffer size limit"""
        import mcp_dbutils.audit
        from mcp_dbutils.audit import _audit_config, _memory_buffer

        # Set a small buffer size
        mcp_dbutils.audit._memory_buffer_size = 2
        _memory_buffer.clear()
        _audit_config["enabled"] = True
        _audit_config["file_storage"]["enabled"] = False

        # Add logs to exceed the buffer size
        log_write_operation(
            connection_name="test_conn",
            table_name="table1",
            operation_type="INSERT",
            sql="INSERT INTO table1 VALUES (1)",
            affected_rows=1,
            execution_time=1.0,
            status="SUCCESS"
        )

        log_write_operation(
            connection_name="test_conn",
            table_name="table2",
            operation_type="INSERT",
            sql="INSERT INTO table2 VALUES (2)",
            affected_rows=1,
            execution_time=1.0,
            status="SUCCESS"
        )

        # Verify that the buffer size is respected
        assert len(_memory_buffer) == 2

        # Add one more log
        log_write_operation(
            connection_name="test_conn",
            table_name="table3",
            operation_type="INSERT",
            sql="INSERT INTO table3 VALUES (3)",
            affected_rows=1,
            execution_time=1.0,
            status="SUCCESS"
        )

        # Verify that the oldest log was removed
        assert len(_memory_buffer) == 2
        assert _memory_buffer[0]["table_name"] == "table2"
        assert _memory_buffer[1]["table_name"] == "table3"
