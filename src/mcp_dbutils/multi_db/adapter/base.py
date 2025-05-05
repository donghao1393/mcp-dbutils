"""
适配器层基类定义

这个模块定义了适配器层的基类，为不同类型的数据库适配器提供统一的接口。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

from ..connection.base import ConnectionBase
from ..error.exceptions import DatabaseError


class AdapterBase(ABC):
    """
    所有数据库适配器的基类
    
    这个抽象类定义了所有数据库适配器必须实现的接口，
    为不同类型的数据库提供统一的操作接口。
    """
    
    def __init__(self, connection: ConnectionBase):
        """
        初始化适配器
        
        Args:
            connection: 数据库连接
        """
        self.connection = connection
    
    @abstractmethod
    def execute_query(self, query: Any, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        执行查询
        
        执行只读查询，如SELECT语句。
        
        Args:
            query: 查询
            params: 查询参数
            
        Returns:
            查询结果
            
        Raises:
            DatabaseError: 如果执行查询时发生错误
        """
        pass
        
    @abstractmethod
    def execute_write(self, query: Any, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        执行写操作
        
        执行写操作，如INSERT、UPDATE、DELETE语句。
        
        Args:
            query: 写操作
            params: 操作参数
            
        Returns:
            操作结果
            
        Raises:
            DatabaseError: 如果执行写操作时发生错误
        """
        pass
        
    @abstractmethod
    def list_resources(self) -> List[Dict[str, Any]]:
        """
        列出资源
        
        列出数据库中的所有资源（表、集合、键等）。
        
        Returns:
            List[Dict[str, Any]]: 资源列表，每个资源包含名称和类型等信息
            
        Raises:
            DatabaseError: 如果列出资源时发生错误
        """
        pass
        
    @abstractmethod
    def describe_resource(self, resource_name: str) -> Dict[str, Any]:
        """
        描述资源
        
        获取资源的详细信息，如表结构、索引等。
        
        Args:
            resource_name: 资源名
            
        Returns:
            Dict[str, Any]: 资源详细信息
            
        Raises:
            DatabaseError: 如果描述资源时发生错误
        """
        pass
        
    @abstractmethod
    def get_resource_stats(self, resource_name: str) -> Dict[str, Any]:
        """
        获取资源统计信息
        
        获取资源的统计信息，如行数、大小等。
        
        Args:
            resource_name: 资源名
            
        Returns:
            Dict[str, Any]: 资源统计信息
            
        Raises:
            DatabaseError: 如果获取资源统计信息时发生错误
        """
        pass
        
    @abstractmethod
    def extract_resource_name(self, query: Any) -> Optional[str]:
        """
        从查询中提取资源名
        
        从查询中提取操作的资源名，用于权限检查。
        
        Args:
            query: 查询
            
        Returns:
            Optional[str]: 资源名，如果无法提取，则返回None
        """
        pass
