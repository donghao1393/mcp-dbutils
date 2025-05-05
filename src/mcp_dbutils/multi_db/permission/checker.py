"""
权限检查器实现

这个模块实现了权限检查器，用于检查数据库操作的权限。
"""

import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from ..error.exceptions import PermissionError


class PermissionChecker:
    """
    权限检查器类
    
    这个类负责检查数据库操作的权限，确保操作符合权限规则。
    """
    
    def __init__(self, config: Dict[str, Dict[str, Any]]):
        """
        初始化权限检查器
        
        Args:
            config: 权限配置，键为连接名，值为连接配置
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
    def check_permission(self, connection_name: str, resource_name: str, 
                        operation_type: str) -> bool:
        """
        检查权限
        
        检查指定连接、资源和操作类型的权限。
        
        Args:
            connection_name: 连接名
            resource_name: 资源名
            operation_type: 操作类型
            
        Returns:
            bool: 如果有权限，则返回True，否则返回False
            
        Raises:
            PermissionError: 如果没有权限
        """
        # 检查连接是否存在
        if connection_name not in self.config:
            raise PermissionError(
                f"Connection '{connection_name}' not found",
                connection_name=connection_name,
                resource_name=resource_name,
                operation_type=operation_type
            )
            
        connection_config = self.config[connection_name]
        
        # 检查连接是否可写
        if operation_type != 'READ' and not connection_config.get('writable', False):
            self.logger.warning(
                f"Write operation '{operation_type}' denied for connection '{connection_name}': "
                f"Connection is not writable"
            )
            raise PermissionError(
                f"Write operation '{operation_type}' denied for connection '{connection_name}': "
                f"Connection is not writable",
                connection_name=connection_name,
                resource_name=resource_name,
                operation_type=operation_type
            )
            
        # 如果是读操作，直接允许
        if operation_type == 'READ':
            return True
            
        # 检查写权限
        write_permissions = connection_config.get('write_permissions', {})
        
        # 获取默认策略
        default_policy = write_permissions.get('default_policy', 'read_only')
        
        # 检查资源特定权限
        resource_type = self._get_resource_type(connection_config.get('type', 'mysql'))
        resources = write_permissions.get(resource_type, {})
        
        # 尝试精确匹配
        if resource_name in resources:
            resource_permissions = resources[resource_name]
            allowed_operations = resource_permissions.get('operations', [])
            
            if operation_type in allowed_operations:
                return True
            elif 'ALL' in allowed_operations:
                return True
                
        # 尝试模式匹配
        for pattern, resource_permissions in resources.items():
            if '*' in pattern or '?' in pattern:
                # 将通配符转换为正则表达式
                regex_pattern = pattern.replace('*', '.*').replace('?', '.')
                if re.match(f"^{regex_pattern}$", resource_name):
                    allowed_operations = resource_permissions.get('operations', [])
                    
                    if operation_type in allowed_operations:
                        return True
                    elif 'ALL' in allowed_operations:
                        return True
                        
        # 检查默认策略
        if default_policy == 'allow_all':
            return True
            
        # 默认拒绝
        self.logger.warning(
            f"Operation '{operation_type}' denied for resource '{resource_name}' "
            f"in connection '{connection_name}': No matching permission rule"
        )
        raise PermissionError(
            f"Operation '{operation_type}' denied for resource '{resource_name}' "
            f"in connection '{connection_name}': No matching permission rule",
            connection_name=connection_name,
            resource_name=resource_name,
            operation_type=operation_type
        )
        
    def get_allowed_operations(self, connection_name: str, resource_name: str) -> List[str]:
        """
        获取允许的操作
        
        获取指定连接和资源允许的操作类型列表。
        
        Args:
            connection_name: 连接名
            resource_name: 资源名
            
        Returns:
            List[str]: 允许的操作类型列表
        """
        # 检查连接是否存在
        if connection_name not in self.config:
            return ['READ']
            
        connection_config = self.config[connection_name]
        
        # 如果连接不可写，只允许读操作
        if not connection_config.get('writable', False):
            return ['READ']
            
        # 获取写权限
        write_permissions = connection_config.get('write_permissions', {})
        
        # 获取默认策略
        default_policy = write_permissions.get('default_policy', 'read_only')
        
        # 初始化允许的操作
        allowed_operations = {'READ'}
        
        # 检查资源特定权限
        resource_type = self._get_resource_type(connection_config.get('type', 'mysql'))
        resources = write_permissions.get(resource_type, {})
        
        # 尝试精确匹配
        if resource_name in resources:
            resource_permissions = resources[resource_name]
            operations = resource_permissions.get('operations', [])
            
            if 'ALL' in operations:
                allowed_operations.update(['INSERT', 'UPDATE', 'DELETE'])
            else:
                allowed_operations.update(operations)
                
        # 尝试模式匹配
        for pattern, resource_permissions in resources.items():
            if '*' in pattern or '?' in pattern:
                # 将通配符转换为正则表达式
                regex_pattern = pattern.replace('*', '.*').replace('?', '.')
                if re.match(f"^{regex_pattern}$", resource_name):
                    operations = resource_permissions.get('operations', [])
                    
                    if 'ALL' in operations:
                        allowed_operations.update(['INSERT', 'UPDATE', 'DELETE'])
                    else:
                        allowed_operations.update(operations)
                        
        # 检查默认策略
        if default_policy == 'allow_all':
            allowed_operations.update(['INSERT', 'UPDATE', 'DELETE'])
            
        return list(allowed_operations)
        
    def _get_resource_type(self, db_type: str) -> str:
        """
        获取资源类型
        
        根据数据库类型获取资源类型。
        
        Args:
            db_type: 数据库类型
            
        Returns:
            str: 资源类型
        """
        db_type = db_type.lower()
        
        if db_type in ('mysql', 'postgresql', 'sqlite'):
            return 'tables'
        elif db_type == 'mongodb':
            return 'collections'
        elif db_type == 'redis':
            return 'keys'
        else:
            return 'resources'
