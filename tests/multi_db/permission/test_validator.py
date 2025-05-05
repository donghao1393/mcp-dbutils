"""
测试操作验证器

这个模块测试多数据库支持架构中的操作验证器。
"""

from unittest.mock import Mock, patch

import pytest

from mcp_dbutils.multi_db.error.exceptions import QueryError
from mcp_dbutils.multi_db.permission.validator import OperationValidator


class TestOperationValidator:
    """测试OperationValidator类"""
    
    def test_init(self):
        """测试初始化"""
        validator = OperationValidator()
        assert validator.logger is not None
        
    def test_validate_operation_valid(self):
        """测试验证有效操作"""
        validator = OperationValidator()
        result = validator.validate_operation("READ", "test_table", "SELECT * FROM test_table")
        assert result is True
        
    def test_validate_operation_invalid_operation_type(self):
        """测试验证无效操作类型"""
        validator = OperationValidator()
        with pytest.raises(QueryError) as excinfo:
            validator.validate_operation("INVALID", "test_table", "SELECT * FROM test_table")
        assert "Invalid operation type" in str(excinfo.value)
        
    def test_validate_operation_no_resource_name(self):
        """测试验证没有资源名"""
        validator = OperationValidator()
        with pytest.raises(QueryError) as excinfo:
            validator.validate_operation("READ", "", "SELECT * FROM test_table")
        assert "Resource name is required" in str(excinfo.value)
        
    def test_validate_operation_no_query(self):
        """测试验证没有查询"""
        validator = OperationValidator()
        with pytest.raises(QueryError) as excinfo:
            validator.validate_operation("READ", "test_table", None)
        assert "Query is required" in str(excinfo.value)
        
    def test_validate_sql_operation_read_valid(self):
        """测试验证有效的SQL读操作"""
        validator = OperationValidator()
        validator._validate_sql_operation("READ", "test_table", "SELECT * FROM test_table")
        # 没有异常表示验证通过
        
    def test_validate_sql_operation_read_invalid(self):
        """测试验证无效的SQL读操作"""
        validator = OperationValidator()
        with pytest.raises(QueryError) as excinfo:
            validator._validate_sql_operation("READ", "test_table", "INSERT INTO test_table VALUES (1)")
        assert "Operation type 'READ' does not match query" in str(excinfo.value)
        
    def test_validate_sql_operation_insert_valid(self):
        """测试验证有效的SQL插入操作"""
        validator = OperationValidator()
        validator._validate_sql_operation("INSERT", "test_table", "INSERT INTO test_table VALUES (1)")
        # 没有异常表示验证通过
        
    def test_validate_sql_operation_insert_invalid(self):
        """测试验证无效的SQL插入操作"""
        validator = OperationValidator()
        with pytest.raises(QueryError) as excinfo:
            validator._validate_sql_operation("INSERT", "test_table", "SELECT * FROM test_table")
        assert "Operation type 'INSERT' does not match query" in str(excinfo.value)
        
    def test_validate_sql_operation_update_valid(self):
        """测试验证有效的SQL更新操作"""
        validator = OperationValidator()
        validator._validate_sql_operation("UPDATE", "test_table", "UPDATE test_table SET field = 1")
        # 没有异常表示验证通过
        
    def test_validate_sql_operation_update_invalid(self):
        """测试验证无效的SQL更新操作"""
        validator = OperationValidator()
        with pytest.raises(QueryError) as excinfo:
            validator._validate_sql_operation("UPDATE", "test_table", "SELECT * FROM test_table")
        assert "Operation type 'UPDATE' does not match query" in str(excinfo.value)
        
    def test_validate_sql_operation_delete_valid(self):
        """测试验证有效的SQL删除操作"""
        validator = OperationValidator()
        validator._validate_sql_operation("DELETE", "test_table", "DELETE FROM test_table")
        # 没有异常表示验证通过
        
    def test_validate_sql_operation_delete_invalid(self):
        """测试验证无效的SQL删除操作"""
        validator = OperationValidator()
        with pytest.raises(QueryError) as excinfo:
            validator._validate_sql_operation("DELETE", "test_table", "SELECT * FROM test_table")
        assert "Operation type 'DELETE' does not match query" in str(excinfo.value)
        
    def test_validate_sql_operation_resource_name_not_found(self):
        """测试验证资源名不在查询中"""
        validator = OperationValidator()
        # 这应该只产生一个警告，不会抛出异常
        validator._validate_sql_operation("READ", "other_table", "SELECT * FROM test_table")
        # 没有异常表示验证通过，但会有警告日志
