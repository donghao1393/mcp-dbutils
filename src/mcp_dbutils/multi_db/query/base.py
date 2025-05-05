"""
查询层基类定义

这个模块定义了查询层的基类，为不同类型的数据库查询构建器提供统一的接口。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union


class Query(ABC):
    """
    查询基类
    
    这个抽象类定义了所有查询必须实现的接口。
    """
    
    @abstractmethod
    def get_query_string(self) -> str:
        """
        获取查询字符串
        
        Returns:
            str: 查询字符串
        """
        pass
        
    @abstractmethod
    def get_params(self) -> Dict[str, Any]:
        """
        获取查询参数
        
        Returns:
            Dict[str, Any]: 查询参数
        """
        pass


class QueryBuilder(ABC):
    """
    查询构建器基类
    
    这个抽象类定义了所有查询构建器必须实现的接口，
    为不同类型的数据库提供统一的查询构建API。
    """
    
    @abstractmethod
    def select(self, resource_name: str, fields: Optional[List[str]] = None) -> 'QueryBuilder':
        """
        构建选择查询
        
        Args:
            resource_name: 资源名
            fields: 要选择的字段列表，如果为None，则选择所有字段
            
        Returns:
            QueryBuilder: 查询构建器实例
        """
        pass
        
    @abstractmethod
    def insert(self, resource_name: str, data: Dict[str, Any]) -> 'QueryBuilder':
        """
        构建插入查询
        
        Args:
            resource_name: 资源名
            data: 要插入的数据
            
        Returns:
            QueryBuilder: 查询构建器实例
        """
        pass
        
    @abstractmethod
    def update(self, resource_name: str, data: Dict[str, Any], 
              condition: Optional[Dict[str, Any]] = None) -> 'QueryBuilder':
        """
        构建更新查询
        
        Args:
            resource_name: 资源名
            data: 要更新的数据
            condition: 更新条件
            
        Returns:
            QueryBuilder: 查询构建器实例
        """
        pass
        
    @abstractmethod
    def delete(self, resource_name: str, 
              condition: Optional[Dict[str, Any]] = None) -> 'QueryBuilder':
        """
        构建删除查询
        
        Args:
            resource_name: 资源名
            condition: 删除条件
            
        Returns:
            QueryBuilder: 查询构建器实例
        """
        pass
        
    @abstractmethod
    def where(self, condition: Dict[str, Any]) -> 'QueryBuilder':
        """
        添加条件
        
        Args:
            condition: 条件
            
        Returns:
            QueryBuilder: 查询构建器实例
        """
        pass
        
    @abstractmethod
    def order_by(self, fields: List[str]) -> 'QueryBuilder':
        """
        添加排序
        
        Args:
            fields: 排序字段列表
            
        Returns:
            QueryBuilder: 查询构建器实例
        """
        pass
        
    @abstractmethod
    def limit(self, count: int) -> 'QueryBuilder':
        """
        添加限制
        
        Args:
            count: 限制数量
            
        Returns:
            QueryBuilder: 查询构建器实例
        """
        pass
        
    @abstractmethod
    def offset(self, count: int) -> 'QueryBuilder':
        """
        添加偏移
        
        Args:
            count: 偏移数量
            
        Returns:
            QueryBuilder: 查询构建器实例
        """
        pass
        
    @abstractmethod
    def build(self) -> Query:
        """
        构建查询
        
        Returns:
            Query: 查询实例
        """
        pass
