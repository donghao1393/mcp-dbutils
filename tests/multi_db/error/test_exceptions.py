"""
测试异常类

这个模块测试多数据库支持架构中的异常类。
"""

import pytest

from mcp_dbutils.multi_db.error.exceptions import (
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    DatabaseError,
    DuplicateKeyError,
    NotImplementedError,
    PermissionError,
    QueryError,
    ResourceNotFoundError,
    TransactionError,
)


class TestDatabaseError:
    """测试DatabaseError类"""

    def test_init(self):
        """测试初始化"""
        error = DatabaseError("Test error")
        assert str(error) == "Test error"
        assert error.get_message() == "Test error"
        assert error.get_cause() is None

    def test_init_with_cause(self):
        """测试带原因的初始化"""
        cause = ValueError("Original error")
        error = DatabaseError("Test error", cause=cause)
        assert str(error) == "Test error"
        assert error.get_message() == "Test error"
        assert error.get_cause() is cause


class TestConnectionError:
    """测试ConnectionError类"""

    def test_init(self):
        """测试初始化"""
        error = ConnectionError("Connection error")
        assert str(error) == "Connection error"
        assert error.get_connection_name() is None

    def test_init_with_connection_name(self):
        """测试带连接名的初始化"""
        error = ConnectionError("Connection error", connection_name="test_conn")
        assert str(error) == "Connection error"
        assert error.get_connection_name() == "test_conn"

    def test_init_with_cause(self):
        """测试带原因的初始化"""
        cause = ValueError("Original error")
        error = ConnectionError("Connection error", connection_name="test_conn", cause=cause)
        assert str(error) == "Connection error"
        assert error.get_connection_name() == "test_conn"
        assert error.get_cause() is cause


class TestAuthenticationError:
    """测试AuthenticationError类"""

    def test_init(self):
        """测试初始化"""
        error = AuthenticationError("Authentication error")
        assert str(error) == "Authentication error"
        assert error.get_connection_name() is None

    def test_init_with_connection_name(self):
        """测试带连接名的初始化"""
        error = AuthenticationError("Authentication error", connection_name="test_conn")
        assert str(error) == "Authentication error"
        assert error.get_connection_name() == "test_conn"


class TestConfigurationError:
    """测试ConfigurationError类"""

    def test_init(self):
        """测试初始化"""
        error = ConfigurationError("Configuration error")
        assert str(error) == "Configuration error"
        assert error.get_cause() is None

    def test_init_with_cause(self):
        """测试带原因的初始化"""
        cause = ValueError("Original error")
        error = ConfigurationError("Configuration error", cause=cause)
        assert str(error) == "Configuration error"
        assert error.get_cause() is cause


class TestResourceNotFoundError:
    """测试ResourceNotFoundError类"""

    def test_init(self):
        """测试初始化"""
        error = ResourceNotFoundError("Resource not found")
        assert str(error) == "Resource not found"
        assert error.get_resource_name() is None

    def test_init_with_resource_name(self):
        """测试带资源名的初始化"""
        error = ResourceNotFoundError("Resource not found", resource_name="test_table")
        assert str(error) == "Resource not found"
        assert error.get_resource_name() == "test_table"

    def test_init_with_cause(self):
        """测试带原因的初始化"""
        cause = ValueError("Original error")
        error = ResourceNotFoundError("Resource not found", resource_name="test_table", cause=cause)
        assert str(error) == "Resource not found"
        assert error.get_resource_name() == "test_table"
        assert error.get_cause() is cause


class TestDuplicateKeyError:
    """测试DuplicateKeyError类"""

    def test_init(self):
        """测试初始化"""
        error = DuplicateKeyError("Duplicate key")
        assert str(error) == "Duplicate key"
        assert error.get_resource_name() is None
        assert error.get_key() is None

    def test_init_with_resource_name_and_key(self):
        """测试带资源名和键的初始化"""
        error = DuplicateKeyError("Duplicate key", resource_name="test_table", key="id")
        assert str(error) == "Duplicate key"
        assert error.get_resource_name() == "test_table"
        assert error.get_key() == "id"

    def test_init_with_cause(self):
        """测试带原因的初始化"""
        cause = ValueError("Original error")
        error = DuplicateKeyError("Duplicate key", resource_name="test_table", key="id", cause=cause)
        assert str(error) == "Duplicate key"
        assert error.get_resource_name() == "test_table"
        assert error.get_key() == "id"
        assert error.get_cause() is cause


class TestPermissionError:
    """测试PermissionError类"""

    def test_init(self):
        """测试初始化"""
        error = PermissionError("Permission denied")
        assert str(error) == "Permission denied"
        assert error.get_connection_name() is None
        assert error.get_resource_name() is None
        assert error.get_operation_type() is None

    def test_init_with_details(self):
        """测试带详细信息的初始化"""
        error = PermissionError(
            "Permission denied",
            connection_name="test_conn",
            resource_name="test_table",
            operation_type="INSERT"
        )
        assert str(error) == "Permission denied"
        assert error.get_connection_name() == "test_conn"
        assert error.get_resource_name() == "test_table"
        assert error.get_operation_type() == "INSERT"

    def test_init_with_cause(self):
        """测试带原因的初始化"""
        cause = ValueError("Original error")
        error = PermissionError(
            "Permission denied",
            connection_name="test_conn",
            resource_name="test_table",
            operation_type="INSERT",
            cause=cause
        )
        assert str(error) == "Permission denied"
        assert error.get_connection_name() == "test_conn"
        assert error.get_resource_name() == "test_table"
        assert error.get_operation_type() == "INSERT"
        assert error.get_cause() is cause


class TestQueryError:
    """测试QueryError类"""

    def test_init(self):
        """测试初始化"""
        error = QueryError("Query error")
        assert str(error) == "Query error"
        assert error.get_query() is None

    def test_init_with_query(self):
        """测试带查询的初始化"""
        error = QueryError("Query error", query="SELECT * FROM test")
        assert str(error) == "Query error"
        assert error.get_query() == "SELECT * FROM test"

    def test_init_with_cause(self):
        """测试带原因的初始化"""
        cause = ValueError("Original error")
        error = QueryError("Query error", query="SELECT * FROM test", cause=cause)
        assert str(error) == "Query error"
        assert error.get_query() == "SELECT * FROM test"
        assert error.get_cause() is cause


class TestTransactionError:
    """测试TransactionError类"""

    def test_init(self):
        """测试初始化"""
        error = TransactionError("Transaction error")
        assert str(error) == "Transaction error"
        assert error.get_transaction_id() is None

    def test_init_with_transaction_id(self):
        """测试带事务ID的初始化"""
        error = TransactionError("Transaction error", transaction_id="tx123")
        assert str(error) == "Transaction error"
        assert error.get_transaction_id() == "tx123"

    def test_init_with_cause(self):
        """测试带原因的初始化"""
        cause = ValueError("Original error")
        error = TransactionError("Transaction error", transaction_id="tx123", cause=cause)
        assert str(error) == "Transaction error"
        assert error.get_transaction_id() == "tx123"
        assert error.get_cause() is cause


class TestNotImplementedError:
    """测试NotImplementedError类"""

    def test_init(self):
        """测试初始化"""
        error = NotImplementedError("Not implemented")
        assert str(error) == "Not implemented"
        assert error.get_cause() is None

    def test_init_with_cause(self):
        """测试带原因的初始化"""
        cause = ValueError("Original error")
        error = NotImplementedError("Not implemented", cause=cause)
        assert str(error) == "Not implemented"
        assert error.get_cause() is cause
