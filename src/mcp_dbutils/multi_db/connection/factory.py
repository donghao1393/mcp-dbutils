"""
连接工厂实现

这个模块实现了连接工厂，用于创建不同类型的数据库连接。
"""

import logging
from typing import Any, Dict, Optional, Type

from ..error.exceptions import ConfigurationError
from .base import ConnectionBase
from .mongo import MongoConnection
from .redis import RedisConnection
from .sql import SQLConnection


class ConnectionFactory:
    """
    连接工厂类

    这个类负责创建不同类型的数据库连接。
    """

    def __init__(self):
        """
        初始化连接工厂
        """
        self.logger = logging.getLogger(__name__)
        self.connection_classes = {
            'mysql': SQLConnection,
            'postgresql': SQLConnection,
            'sqlite': SQLConnection,
            'mongodb': MongoConnection,
            'redis': RedisConnection,
        }

    def create_connection(self, config: Dict[str, Any]) -> ConnectionBase:
        """
        创建数据库连接

        根据配置创建适当类型的数据库连接。

        Args:
            config: 连接配置，包含连接参数
                - type: 数据库类型

        Returns:
            ConnectionBase: 数据库连接实例

        Raises:
            ConfigurationError: 如果配置无效或不支持的数据库类型
        """
        if not config:
            raise ConfigurationError("Connection configuration is required")

        db_type = config.get('type', '').lower()

        if not db_type:
            raise ConfigurationError("Database type is required in connection configuration")

        connection_class = self.connection_classes.get(db_type)

        if not connection_class:
            supported_types = ', '.join(self.connection_classes.keys())
            raise ConfigurationError(
                f"Unsupported database type: {db_type}. "
                f"Supported types are: {supported_types}"
            )

        try:
            connection = connection_class(config)
            self.logger.info(f"Created {db_type} connection")
            return connection
        except Exception as e:
            self.logger.error(f"Failed to create {db_type} connection: {str(e)}")
            raise ConfigurationError(f"Failed to create {db_type} connection: {str(e)}")

    def register_connection_class(self, db_type: str, connection_class: Type[ConnectionBase]) -> None:
        """
        注册连接类

        注册自定义的连接类，用于创建特定类型的数据库连接。

        Args:
            db_type: 数据库类型
            connection_class: 连接类
        """
        self.connection_classes[db_type.lower()] = connection_class
        self.logger.info(f"Registered connection class for {db_type}")

    def get_supported_types(self) -> list:
        """
        获取支持的数据库类型

        Returns:
            list: 支持的数据库类型列表
        """
        return list(self.connection_classes.keys())
