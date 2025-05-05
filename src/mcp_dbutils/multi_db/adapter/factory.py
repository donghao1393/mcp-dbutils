"""
适配器工厂实现

这个模块实现了适配器工厂，用于创建不同类型的数据库适配器。
"""

import logging
from typing import Any, Dict, Optional, Type

from ..connection.base import ConnectionBase
from ..connection.sql import SQLConnection
from ..error.exceptions import ConfigurationError
from .base import AdapterBase
from .sql import SQLAdapter


class AdapterFactory:
    """
    适配器工厂类
    
    这个类负责创建不同类型的数据库适配器。
    """
    
    def __init__(self):
        """
        初始化适配器工厂
        """
        self.logger = logging.getLogger(__name__)
        self.adapter_classes = {
            SQLConnection: SQLAdapter,
            # 以下是占位符，将在后续阶段实现
            # MongoConnection: MongoAdapter,
            # RedisConnection: RedisAdapter,
        }
        
    def create_adapter(self, connection: ConnectionBase) -> AdapterBase:
        """
        创建数据库适配器
        
        根据连接类型创建适当类型的数据库适配器。
        
        Args:
            connection: 数据库连接
                
        Returns:
            AdapterBase: 数据库适配器实例
            
        Raises:
            ConfigurationError: 如果不支持的连接类型
        """
        if not connection:
            raise ConfigurationError("Connection is required")
            
        connection_class = connection.__class__
        
        adapter_class = self.adapter_classes.get(connection_class)
        
        if not adapter_class:
            supported_types = ', '.join([cls.__name__ for cls in self.adapter_classes.keys()])
            raise ConfigurationError(
                f"Unsupported connection type: {connection_class.__name__}. "
                f"Supported types are: {supported_types}"
            )
            
        try:
            adapter = adapter_class(connection)
            self.logger.info(f"Created {adapter_class.__name__} for {connection_class.__name__}")
            return adapter
        except Exception as e:
            self.logger.error(f"Failed to create adapter for {connection_class.__name__}: {str(e)}")
            raise ConfigurationError(f"Failed to create adapter for {connection_class.__name__}: {str(e)}")
            
    def register_adapter_class(self, connection_class: Type[ConnectionBase], 
                              adapter_class: Type[AdapterBase]) -> None:
        """
        注册适配器类
        
        注册自定义的适配器类，用于创建特定类型的数据库适配器。
        
        Args:
            connection_class: 连接类
            adapter_class: 适配器类
        """
        self.adapter_classes[connection_class] = adapter_class
        self.logger.info(f"Registered adapter class {adapter_class.__name__} for {connection_class.__name__}")
        
    def get_supported_connection_types(self) -> list:
        """
        获取支持的连接类型
        
        Returns:
            list: 支持的连接类型列表
        """
        return [cls.__name__ for cls in self.adapter_classes.keys()]
