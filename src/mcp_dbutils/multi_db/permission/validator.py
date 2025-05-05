"""
操作验证器实现

这个模块实现了操作验证器，用于验证数据库操作的有效性。
"""

import logging
import re
from typing import Any

from ..error.exceptions import QueryError


class OperationValidator:
    """
    操作验证器类

    这个类负责验证数据库操作的有效性，确保操作符合规则。
    """

    def __init__(self):
        """
        初始化操作验证器
        """
        self.logger = logging.getLogger(__name__)

    def validate_operation(self, operation_type: str, resource_name: str, query: Any) -> bool:
        """
        验证操作

        验证指定操作类型、资源和查询的有效性。

        Args:
            operation_type: 操作类型
            resource_name: 资源名
            query: 查询

        Returns:
            bool: 如果操作有效，则返回True，否则返回False

        Raises:
            QueryError: 如果操作无效
        """
        try:
            # 验证操作类型
            if operation_type not in ('READ', 'INSERT', 'UPDATE', 'DELETE'):
                raise QueryError(f"Invalid operation type: {operation_type}")

            # 验证资源名
            if not resource_name:
                raise QueryError("Resource name is required")

            # 验证查询
            if not query:
                raise QueryError("Query is required")

            # 验证操作类型和查询的一致性
            if isinstance(query, str):
                # SQL查询
                self._validate_sql_operation(operation_type, resource_name, query)
            else:
                # 非SQL查询，暂不验证
                pass

            return True
        except QueryError as e:
            self.logger.error(f"Operation validation failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in operation validation: {str(e)}")
            raise QueryError(f"Operation validation failed: {str(e)}")

    def _validate_sql_operation(self, operation_type: str, resource_name: str, query: str) -> None:
        """
        验证SQL操作

        验证SQL操作的有效性。

        Args:
            operation_type: 操作类型
            resource_name: 表名
            query: SQL查询

        Raises:
            QueryError: 如果操作无效
        """
        query = query.strip().upper()

        # 验证操作类型和查询的一致性
        if operation_type == 'READ' and not (query.startswith("SELECT") or query.startswith("SHOW") or
               query.startswith("DESCRIBE") or query.startswith("EXPLAIN")):
            raise QueryError(f"Operation type 'READ' does not match query: {query}")
        elif operation_type == 'INSERT' and not query.startswith("INSERT"):
            raise QueryError(f"Operation type 'INSERT' does not match query: {query}")
        elif operation_type == 'UPDATE' and not query.startswith("UPDATE"):
            raise QueryError(f"Operation type 'UPDATE' does not match query: {query}")
        elif operation_type == 'DELETE' and not query.startswith("DELETE"):
            raise QueryError(f"Operation type 'DELETE' does not match query: {query}")

        # 验证资源名和查询的一致性
        # 这是一个简单的验证，可能不适用于所有情况
        if resource_name != "unknown_table":
            # 尝试在查询中找到资源名
            # 这是一个简单的实现，可能不适用于所有情况
            pattern = r'\b' + re.escape(resource_name) + r'\b'
            if not re.search(pattern, query, re.IGNORECASE):
                # 尝试带引号的资源名
                pattern = r'[`"\[]' + re.escape(resource_name) + r'[`"\]]'
                if not re.search(pattern, query, re.IGNORECASE):
                    self.logger.warning(
                        f"Resource name '{resource_name}' not found in query: {query}"
                    )
