"""
审计日志记录器实现

这个模块实现了审计日志记录器，用于记录数据库操作的审计日志。
"""

import datetime
import json
import logging
import os
import threading
from typing import Any, Dict, List, Optional, Tuple, Union


class AuditLogger:
    """
    审计日志记录器类

    这个类负责记录数据库操作的审计日志，特别是写操作。
    """

    def __init__(self, log_file: Optional[str] = None, log_to_console: bool = False):
        """
        初始化审计日志记录器

        Args:
            log_file: 日志文件路径，如果为None，则使用默认路径
            log_to_console: 是否同时输出到控制台
        """
        self.logger = logging.getLogger(__name__)
        self.log_file = log_file or self._get_default_log_file()
        self.log_to_console = log_to_console
        self.lock = threading.RLock()

        # 在测试环境中不创建目录
        if not os.environ.get('PYTEST_CURRENT_TEST'):
            # 确保日志目录存在
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

    def log_operation(self, connection_name: str, resource_name: str,
                     operation_type: str, user: Optional[str] = None,
                     result: Optional[Dict[str, Any]] = None) -> None:
        """
        记录操作日志

        记录数据库操作的审计日志。

        Args:
            connection_name: 连接名
            resource_name: 资源名
            operation_type: 操作类型
            user: 用户名
            result: 操作结果
        """
        # 只记录写操作
        if operation_type == 'READ':
            return

        with self.lock:
            try:
                # 构建日志条目
                timestamp = datetime.datetime.now().isoformat()
                log_entry = {
                    'timestamp': timestamp,
                    'connection': connection_name,
                    'resource': resource_name,
                    'operation': operation_type,
                    'user': user or 'unknown',
                    'status': 'SUCCESS',
                    'affected_rows': result.get('affected_rows', 0) if result else 0,
                    'last_insert_id': result.get('last_insert_id') if result else None
                }

                # 写入日志文件
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(log_entry) + '\n')

                # 输出到控制台
                if self.log_to_console:
                    self.logger.info(f"Audit: {json.dumps(log_entry)}")
            except Exception as e:
                self.logger.error(f"Failed to log audit entry: {str(e)}")

    def log_failed_operation(self, connection_name: str, resource_name: str,
                            operation_type: str, user: Optional[str] = None,
                            error: Optional[str] = None) -> None:
        """
        记录失败操作日志

        记录失败的数据库操作的审计日志。

        Args:
            connection_name: 连接名
            resource_name: 资源名
            operation_type: 操作类型
            user: 用户名
            error: 错误信息
        """
        # 只记录写操作
        if operation_type == 'READ':
            return

        with self.lock:
            try:
                # 构建日志条目
                timestamp = datetime.datetime.now().isoformat()
                log_entry = {
                    'timestamp': timestamp,
                    'connection': connection_name,
                    'resource': resource_name,
                    'operation': operation_type,
                    'user': user or 'unknown',
                    'status': 'FAILED',
                    'error': error or 'Unknown error'
                }

                # 写入日志文件
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(log_entry) + '\n')

                # 输出到控制台
                if self.log_to_console:
                    self.logger.warning(f"Audit: {json.dumps(log_entry)}")
            except Exception as e:
                self.logger.error(f"Failed to log audit entry: {str(e)}")

    def get_logs(self, limit: int = 100, connection: Optional[str] = None,
                resource: Optional[str] = None, operation: Optional[str] = None,
                status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取日志

        获取审计日志，支持过滤和限制。

        Args:
            limit: 最大返回条数
            connection: 连接名过滤
            resource: 资源名过滤
            operation: 操作类型过滤
            status: 状态过滤

        Returns:
            List[Dict[str, Any]]: 日志条目列表
        """
        logs = []

        with self.lock:
            try:
                if not os.path.exists(self.log_file):
                    return []

                with open(self.log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            log_entry = json.loads(line.strip())

                            # 应用过滤
                            if connection and log_entry.get('connection') != connection:
                                continue

                            if resource and log_entry.get('resource') != resource:
                                continue

                            if operation and log_entry.get('operation') != operation:
                                continue

                            if status and log_entry.get('status') != status:
                                continue

                            logs.append(log_entry)

                            # 应用限制
                            if len(logs) >= limit:
                                break
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                self.logger.error(f"Failed to get audit logs: {str(e)}")

        return logs

    def clear_logs(self) -> None:
        """
        清除日志

        清除所有审计日志。
        """
        with self.lock:
            try:
                if os.path.exists(self.log_file):
                    os.remove(self.log_file)
                    self.logger.info(f"Cleared audit logs: {self.log_file}")
            except Exception as e:
                self.logger.error(f"Failed to clear audit logs: {str(e)}")

    @staticmethod
    def _get_default_log_file() -> str:
        """
        获取默认日志文件路径

        Returns:
            str: 默认日志文件路径
        """
        # 获取当前用户的主目录
        home_dir = os.path.expanduser('~')

        # 构建日志目录
        log_dir = os.path.join(home_dir, '.mcp_dbutils', 'logs')

        # 构建日志文件路径
        log_file = os.path.join(log_dir, 'audit.log')

        return log_file
