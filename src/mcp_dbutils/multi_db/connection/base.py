"""
连接层基类定义

这个模块定义了连接层的基类，为不同类型的数据库连接提供统一的接口。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

from ..error.exceptions import ConnectionError, TransactionError


class ConnectionBase(ABC):
    """
    所有数据库连接的基类
    
    这个抽象类定义了所有数据库连接必须实现的接口，
    为不同类型的数据库提供统一的连接管理。
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化连接
        
        Args:
            config: 连接配置，包含连接参数
        """
        self.config = config
        self.connection = None
        self.is_transaction_active = False
    
    @abstractmethod
    def connect(self) -> None:
        """
        建立连接
        
        建立到数据库的连接，如果连接已经存在，则重用现有连接。
        
        Raises:
            ConnectionError: 如果连接失败
        """
        pass
        
    @abstractmethod
    def disconnect(self) -> None:
        """
        断开连接
        
        断开与数据库的连接，释放资源。
        如果有活动的事务，会先回滚事务。
        """
        pass
        
    @abstractmethod
    def is_connected(self) -> bool:
        """
        检查连接状态
        
        Returns:
            bool: 如果连接是活动的，则返回True，否则返回False
        """
        pass
        
    @abstractmethod
    def execute(self, query: Any, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        执行查询
        
        执行给定的查询，可以是SQL语句、MongoDB查询或Redis命令。
        
        Args:
            query: 要执行的查询
            params: 查询参数
            
        Returns:
            查询结果
            
        Raises:
            ConnectionError: 如果执行查询时发生错误
        """
        pass
        
    @abstractmethod
    def begin_transaction(self) -> None:
        """
        开始事务
        
        开始一个新的事务。如果已经有一个活动的事务，则抛出异常。
        
        Raises:
            TransactionError: 如果已经有一个活动的事务
        """
        pass
        
    @abstractmethod
    def commit(self) -> None:
        """
        提交事务
        
        提交当前活动的事务。如果没有活动的事务，则抛出异常。
        
        Raises:
            TransactionError: 如果没有活动的事务
        """
        pass
        
    @abstractmethod
    def rollback(self) -> None:
        """
        回滚事务
        
        回滚当前活动的事务。如果没有活动的事务，则抛出异常。
        
        Raises:
            TransactionError: 如果没有活动的事务
        """
        pass
