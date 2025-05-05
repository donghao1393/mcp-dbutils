"""
测试权限检查器

这个模块测试多数据库支持架构中的权限检查器。
"""

import pytest
from unittest.mock import Mock, patch

from mcp_dbutils.multi_db.permission.checker import PermissionChecker
from mcp_dbutils.multi_db.error.exceptions import PermissionError


class TestPermissionChecker:
    """测试PermissionChecker类"""
    
    def test_init(self):
        """测试初始化"""
        config = {"test_conn": {"type": "mysql"}}
        checker = PermissionChecker(config)
        assert checker.config == config
        
    def test_check_permission_read(self):
        """测试检查读权限"""
        config = {"test_conn": {"type": "mysql"}}
        checker = PermissionChecker(config)
        result = checker.check_permission("test_conn", "test_table", "READ")
        assert result is True
        
    def test_check_permission_connection_not_found(self):
        """测试连接不存在时检查权限"""
        config = {"test_conn": {"type": "mysql"}}
        checker = PermissionChecker(config)
        with pytest.raises(PermissionError) as excinfo:
            checker.check_permission("non_existent", "test_table", "READ")
        assert "Connection 'non_existent' not found" in str(excinfo.value)
        
    def test_check_permission_write_not_writable(self):
        """测试连接不可写时检查写权限"""
        config = {"test_conn": {"type": "mysql", "writable": False}}
        checker = PermissionChecker(config)
        with pytest.raises(PermissionError) as excinfo:
            checker.check_permission("test_conn", "test_table", "INSERT")
        assert "Connection is not writable" in str(excinfo.value)
        
    def test_check_permission_write_allowed(self):
        """测试允许写权限"""
        config = {
            "test_conn": {
                "type": "mysql",
                "writable": True,
                "write_permissions": {
                    "tables": {
                        "test_table": {
                            "operations": ["INSERT"]
                        }
                    }
                }
            }
        }
        checker = PermissionChecker(config)
        result = checker.check_permission("test_conn", "test_table", "INSERT")
        assert result is True
        
    def test_check_permission_write_allowed_all(self):
        """测试允许所有写权限"""
        config = {
            "test_conn": {
                "type": "mysql",
                "writable": True,
                "write_permissions": {
                    "tables": {
                        "test_table": {
                            "operations": ["ALL"]
                        }
                    }
                }
            }
        }
        checker = PermissionChecker(config)
        result = checker.check_permission("test_conn", "test_table", "INSERT")
        assert result is True
        
    def test_check_permission_write_pattern_match(self):
        """测试模式匹配写权限"""
        config = {
            "test_conn": {
                "type": "mysql",
                "writable": True,
                "write_permissions": {
                    "tables": {
                        "test_*": {
                            "operations": ["INSERT"]
                        }
                    }
                }
            }
        }
        checker = PermissionChecker(config)
        result = checker.check_permission("test_conn", "test_table", "INSERT")
        assert result is True
        
    def test_check_permission_write_default_allow_all(self):
        """测试默认允许所有写权限"""
        config = {
            "test_conn": {
                "type": "mysql",
                "writable": True,
                "write_permissions": {
                    "default_policy": "allow_all"
                }
            }
        }
        checker = PermissionChecker(config)
        result = checker.check_permission("test_conn", "test_table", "INSERT")
        assert result is True
        
    def test_check_permission_write_denied(self):
        """测试拒绝写权限"""
        config = {
            "test_conn": {
                "type": "mysql",
                "writable": True,
                "write_permissions": {
                    "default_policy": "read_only",
                    "tables": {
                        "other_table": {
                            "operations": ["INSERT"]
                        }
                    }
                }
            }
        }
        checker = PermissionChecker(config)
        with pytest.raises(PermissionError) as excinfo:
            checker.check_permission("test_conn", "test_table", "INSERT")
        assert "No matching permission rule" in str(excinfo.value)
        
    def test_get_allowed_operations_connection_not_found(self):
        """测试连接不存在时获取允许的操作"""
        config = {"test_conn": {"type": "mysql"}}
        checker = PermissionChecker(config)
        operations = checker.get_allowed_operations("non_existent", "test_table")
        assert operations == ["READ"]
        
    def test_get_allowed_operations_not_writable(self):
        """测试连接不可写时获取允许的操作"""
        config = {"test_conn": {"type": "mysql", "writable": False}}
        checker = PermissionChecker(config)
        operations = checker.get_allowed_operations("test_conn", "test_table")
        assert operations == ["READ"]
        
    def test_get_allowed_operations_exact_match(self):
        """测试精确匹配获取允许的操作"""
        config = {
            "test_conn": {
                "type": "mysql",
                "writable": True,
                "write_permissions": {
                    "tables": {
                        "test_table": {
                            "operations": ["INSERT", "UPDATE"]
                        }
                    }
                }
            }
        }
        checker = PermissionChecker(config)
        operations = checker.get_allowed_operations("test_conn", "test_table")
        assert set(operations) == {"READ", "INSERT", "UPDATE"}
        
    def test_get_allowed_operations_all(self):
        """测试获取所有允许的操作"""
        config = {
            "test_conn": {
                "type": "mysql",
                "writable": True,
                "write_permissions": {
                    "tables": {
                        "test_table": {
                            "operations": ["ALL"]
                        }
                    }
                }
            }
        }
        checker = PermissionChecker(config)
        operations = checker.get_allowed_operations("test_conn", "test_table")
        assert set(operations) == {"READ", "INSERT", "UPDATE", "DELETE"}
        
    def test_get_allowed_operations_pattern_match(self):
        """测试模式匹配获取允许的操作"""
        config = {
            "test_conn": {
                "type": "mysql",
                "writable": True,
                "write_permissions": {
                    "tables": {
                        "test_*": {
                            "operations": ["INSERT"]
                        }
                    }
                }
            }
        }
        checker = PermissionChecker(config)
        operations = checker.get_allowed_operations("test_conn", "test_table")
        assert set(operations) == {"READ", "INSERT"}
        
    def test_get_allowed_operations_default_allow_all(self):
        """测试默认允许所有操作"""
        config = {
            "test_conn": {
                "type": "mysql",
                "writable": True,
                "write_permissions": {
                    "default_policy": "allow_all"
                }
            }
        }
        checker = PermissionChecker(config)
        operations = checker.get_allowed_operations("test_conn", "test_table")
        assert set(operations) == {"READ", "INSERT", "UPDATE", "DELETE"}
        
    def test_get_resource_type(self):
        """测试获取资源类型"""
        checker = PermissionChecker({})
        assert checker._get_resource_type("mysql") == "tables"
        assert checker._get_resource_type("postgresql") == "tables"
        assert checker._get_resource_type("sqlite") == "tables"
        assert checker._get_resource_type("mongodb") == "collections"
        assert checker._get_resource_type("redis") == "keys"
        assert checker._get_resource_type("unknown") == "resources"
