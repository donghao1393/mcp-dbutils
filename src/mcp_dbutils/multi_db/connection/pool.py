"""
连接池实现

这个模块实现了连接池，用于管理数据库连接。
"""

import logging
import threading
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from ..error.exceptions import ConnectionError, ConfigurationError
from .base import ConnectionBase
from .factory import ConnectionFactory


class ConnectionPool:
    """
    连接池类
    
    这个类负责管理数据库连接，包括创建、获取、释放和关闭连接。
    """
    
    def __init__(self, config: Dict[str, Dict[str, Any]], factory: Optional[ConnectionFactory] = None):
        """
        初始化连接池
        
        Args:
            config: 连接配置，键为连接名，值为连接参数
            factory: 连接工厂，如果为None，则创建一个新的工厂
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.factory = factory or ConnectionFactory()
        self.connections = {}  # 连接缓存，键为连接名，值为连接实例
        self.active_connections = {}  # 活动连接，键为连接名，值为(连接实例, 最后使用时间)
        self.lock = threading.RLock()  # 用于线程安全
        self.max_idle_time = 300  # 连接最大空闲时间（秒）
        self.cleanup_interval = 60  # 清理间隔（秒）
        self.last_cleanup_time = time.time()
        
    def get_connection(self, name: str) -> ConnectionBase:
        """
        获取连接
        
        获取指定名称的连接，如果连接不存在，则创建一个新的连接。
        
        Args:
            name: 连接名
            
        Returns:
            ConnectionBase: 数据库连接实例
            
        Raises:
            ConfigurationError: 如果连接配置不存在
            ConnectionError: 如果创建连接失败
        """
        with self.lock:
            # 检查是否需要清理空闲连接
            self._cleanup_idle_connections()
            
            # 检查是否有活动连接
            if name in self.active_connections:
                connection, _ = self.active_connections[name]
                return connection
                
            # 检查是否有缓存连接
            if name in self.connections:
                connection = self.connections[name]
                
                # 确保连接是活动的
                if not connection.is_connected():
                    try:
                        connection.connect()
                    except Exception as e:
                        self.logger.error(f"Failed to reconnect to {name}: {str(e)}")
                        # 移除失效的连接
                        del self.connections[name]
                        raise ConnectionError(f"Failed to reconnect to {name}: {str(e)}")
                
                # 标记为活动连接
                self.active_connections[name] = (connection, time.time())
                return connection
                
            # 创建新连接
            if name not in self.config:
                raise ConfigurationError(f"Connection configuration for '{name}' not found")
                
            try:
                connection = self.factory.create_connection(self.config[name])
                connection.connect()
                
                # 缓存连接
                self.connections[name] = connection
                
                # 标记为活动连接
                self.active_connections[name] = (connection, time.time())
                
                self.logger.info(f"Created new connection for '{name}'")
                return connection
            except Exception as e:
                self.logger.error(f"Failed to create connection for '{name}': {str(e)}")
                raise ConnectionError(f"Failed to create connection for '{name}': {str(e)}")
                
    def release_connection(self, name: str) -> None:
        """
        释放连接
        
        将连接标记为非活动状态，但保留在连接池中以供重用。
        
        Args:
            name: 连接名
        """
        with self.lock:
            if name in self.active_connections:
                connection, _ = self.active_connections[name]
                
                # 如果连接有活动的事务，回滚事务
                if connection.is_transaction_active:
                    try:
                        connection.rollback()
                    except Exception as e:
                        self.logger.warning(f"Failed to rollback transaction on release: {str(e)}")
                
                # 更新最后使用时间
                self.active_connections[name] = (connection, time.time())
                
                self.logger.debug(f"Released connection for '{name}'")
                
    def close_connection(self, name: str) -> None:
        """
        关闭连接
        
        关闭并移除指定的连接。
        
        Args:
            name: 连接名
        """
        with self.lock:
            # 从活动连接中移除
            if name in self.active_connections:
                connection, _ = self.active_connections[name]
                del self.active_connections[name]
            else:
                connection = self.connections.get(name)
                
            # 从连接缓存中移除
            if name in self.connections:
                del self.connections[name]
                
            # 关闭连接
            if connection:
                try:
                    connection.disconnect()
                    self.logger.info(f"Closed connection for '{name}'")
                except Exception as e:
                    self.logger.warning(f"Error closing connection for '{name}': {str(e)}")
                    
    def close_all(self) -> None:
        """
        关闭所有连接
        
        关闭并移除所有连接。
        """
        with self.lock:
            # 复制连接名列表，因为在循环中会修改字典
            connection_names = list(self.connections.keys())
            
            for name in connection_names:
                self.close_connection(name)
                
            self.active_connections.clear()
            self.connections.clear()
            
            self.logger.info("Closed all connections")
            
    def _cleanup_idle_connections(self) -> None:
        """
        清理空闲连接
        
        清理超过最大空闲时间的连接。
        """
        current_time = time.time()
        
        # 检查是否需要清理
        if current_time - self.last_cleanup_time < self.cleanup_interval:
            return
            
        self.last_cleanup_time = current_time
        
        # 找出空闲时间过长的连接
        idle_connections = []
        for name, (_, last_used_time) in self.active_connections.items():
            if current_time - last_used_time > self.max_idle_time:
                idle_connections.append(name)
                
        # 关闭空闲连接
        for name in idle_connections:
            self.logger.info(f"Closing idle connection for '{name}'")
            self.close_connection(name)
            
    def set_max_idle_time(self, seconds: int) -> None:
        """
        设置最大空闲时间
        
        Args:
            seconds: 最大空闲时间（秒）
        """
        self.max_idle_time = seconds
        
    def set_cleanup_interval(self, seconds: int) -> None:
        """
        设置清理间隔
        
        Args:
            seconds: 清理间隔（秒）
        """
        self.cleanup_interval = seconds
