"""
测试审计日志记录器

这个模块测试多数据库支持架构中的审计日志记录器。
"""

import json
import os
from unittest.mock import Mock, mock_open, patch

import pytest

from mcp_dbutils.multi_db.permission.audit import AuditLogger


class TestAuditLogger:
    """测试AuditLogger类"""

    @patch('os.path.expanduser')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_init(self, mock_makedirs, mock_exists, mock_expanduser):
        """测试初始化"""
        mock_expanduser.return_value = "/home/user"
        mock_exists.return_value = False

        logger = AuditLogger()

        assert logger.log_file == "/home/user/.mcp_dbutils/logs/audit.log"
        assert not logger.log_to_console
        mock_makedirs.assert_called_once_with("/home/user/.mcp_dbutils/logs")

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_init_custom_log_file(self, mock_makedirs, mock_exists):
        """测试自定义日志文件的初始化"""
        mock_exists.return_value = False

        logger = AuditLogger(log_file="custom/path/audit.log", log_to_console=True)

        assert logger.log_file == "custom/path/audit.log"
        assert logger.log_to_console
        mock_makedirs.assert_called_once_with("custom/path")

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_init_log_dir_exists(self, mock_makedirs, mock_exists):
        """测试日志目录已存在的初始化"""
        mock_exists.return_value = True

        logger = AuditLogger(log_file="custom/path/audit.log")

        mock_makedirs.assert_not_called()

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dumps')
    def test_log_operation(self, mock_dumps, mock_file):
        """测试记录操作日志"""
        mock_dumps.return_value = '{"test": "json"}'

        logger = AuditLogger(log_file="test/audit.log")
        logger.log_operation("test_conn", "test_table", "INSERT", "test_user", {"affected_rows": 1})

        mock_file.assert_called_once_with("test/audit.log", 'a', encoding='utf-8')
        mock_file().write.assert_called_once_with('{"test": "json"}\n')

    @patch('builtins.open', new_callable=mock_open)
    def test_log_operation_read(self, mock_file):
        """测试记录读操作日志"""
        logger = AuditLogger(log_file="test/audit.log")
        logger.log_operation("test_conn", "test_table", "READ", "test_user")

        mock_file.assert_not_called()

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dumps')
    def test_log_failed_operation(self, mock_dumps, mock_file):
        """测试记录失败操作日志"""
        mock_dumps.return_value = '{"test": "json"}'

        logger = AuditLogger(log_file="test/audit.log")
        logger.log_failed_operation("test_conn", "test_table", "INSERT", "test_user", "Error message")

        mock_file.assert_called_once_with("test/audit.log", 'a', encoding='utf-8')
        mock_file().write.assert_called_once_with('{"test": "json"}\n')

    @patch('builtins.open', new_callable=mock_open)
    def test_log_failed_operation_read(self, mock_file):
        """测试记录失败读操作日志"""
        logger = AuditLogger(log_file="test/audit.log")
        logger.log_failed_operation("test_conn", "test_table", "READ", "test_user", "Error message")

        mock_file.assert_not_called()

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_logs_file_not_exists(self, mock_file, mock_exists):
        """测试文件不存在时获取日志"""
        mock_exists.return_value = False

        logger = AuditLogger(log_file="test/audit.log")
        logs = logger.get_logs()

        assert logs == []
        mock_file.assert_not_called()

    @patch('os.path.exists')
    @patch('builtins.open')
    def test_get_logs(self, mock_file, mock_exists):
        """测试获取日志"""
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value = [
            '{"timestamp": "2023-01-01T00:00:00", "connection": "test_conn", "resource": "test_table", "operation": "INSERT", "user": "test_user", "status": "SUCCESS"}\n',
            '{"timestamp": "2023-01-01T00:01:00", "connection": "test_conn", "resource": "other_table", "operation": "UPDATE", "user": "test_user", "status": "SUCCESS"}\n',
            '{"timestamp": "2023-01-01T00:02:00", "connection": "other_conn", "resource": "test_table", "operation": "DELETE", "user": "test_user", "status": "FAILED"}\n'
        ]

        logger = AuditLogger(log_file="/test/audit.log")
        logs = logger.get_logs()

        assert len(logs) == 3
        assert logs[0]["connection"] == "test_conn"
        assert logs[0]["resource"] == "test_table"
        assert logs[0]["operation"] == "INSERT"
        assert logs[1]["resource"] == "other_table"
        assert logs[1]["operation"] == "UPDATE"
        assert logs[2]["connection"] == "other_conn"
        assert logs[2]["status"] == "FAILED"

    @patch('os.path.exists')
    @patch('builtins.open')
    def test_get_logs_with_filters(self, mock_file, mock_exists):
        """测试带过滤条件获取日志"""
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value = [
            '{"timestamp": "2023-01-01T00:00:00", "connection": "test_conn", "resource": "test_table", "operation": "INSERT", "user": "test_user", "status": "SUCCESS"}\n',
            '{"timestamp": "2023-01-01T00:01:00", "connection": "test_conn", "resource": "other_table", "operation": "UPDATE", "user": "test_user", "status": "SUCCESS"}\n',
            '{"timestamp": "2023-01-01T00:02:00", "connection": "other_conn", "resource": "test_table", "operation": "DELETE", "user": "test_user", "status": "FAILED"}\n'
        ]

        logger = AuditLogger(log_file="/test/audit.log")
        logs = logger.get_logs(connection="test_conn", resource="test_table")

        assert len(logs) == 1
        assert logs[0]["connection"] == "test_conn"
        assert logs[0]["resource"] == "test_table"
        assert logs[0]["operation"] == "INSERT"

    @patch('os.path.exists')
    @patch('builtins.open')
    def test_get_logs_with_limit(self, mock_file, mock_exists):
        """测试带限制获取日志"""
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value = [
            '{"timestamp": "2023-01-01T00:00:00", "connection": "test_conn", "resource": "test_table", "operation": "INSERT", "user": "test_user", "status": "SUCCESS"}\n',
            '{"timestamp": "2023-01-01T00:01:00", "connection": "test_conn", "resource": "other_table", "operation": "UPDATE", "user": "test_user", "status": "SUCCESS"}\n',
            '{"timestamp": "2023-01-01T00:02:00", "connection": "other_conn", "resource": "test_table", "operation": "DELETE", "user": "test_user", "status": "FAILED"}\n'
        ]

        logger = AuditLogger(log_file="/test/audit.log")
        logs = logger.get_logs(limit=2)

        assert len(logs) == 2

    @patch('os.path.exists')
    @patch('os.remove')
    def test_clear_logs(self, mock_remove, mock_exists):
        """测试清除日志"""
        mock_exists.return_value = True

        logger = AuditLogger(log_file="test/audit.log")
        logger.clear_logs()

        mock_remove.assert_called_once_with("test/audit.log")

    @patch('os.path.exists')
    @patch('os.remove')
    def test_clear_logs_file_not_exists(self, mock_remove, mock_exists):
        """测试文件不存在时清除日志"""
        mock_exists.return_value = False

        logger = AuditLogger(log_file="test/audit.log")
        logger.clear_logs()

        mock_remove.assert_not_called()

    @patch('os.path.expanduser')
    def test_get_default_log_file(self, mock_expanduser):
        """测试获取默认日志文件路径"""
        mock_expanduser.return_value = "/home/user"

        logger = AuditLogger()
        log_file = logger._get_default_log_file()

        assert log_file == "/home/user/.mcp_dbutils/logs/audit.log"
