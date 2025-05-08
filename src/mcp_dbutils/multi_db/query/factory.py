"""
查询构建器工厂实现

这个模块实现了查询构建器工厂，用于创建不同类型的数据库查询构建器。
"""

import logging
from typing import Any, Dict, Optional, Type

from ..error.exceptions import ConfigurationError
from .base import QueryBuilder
from .mongo import MongoQueryBuilder
from .redis import RedisCommandBuilder
from .sql import SQLQueryBuilder


class QueryBuilderFactory:
    """
    查询构建器工厂类

    这个类负责创建不同类型的数据库查询构建器。
    """

    def __init__(self):
        """
        初始化查询构建器工厂
        """
        self.logger = logging.getLogger(__name__)
        self.builder_classes = {
            'mysql': SQLQueryBuilder,
            'postgresql': SQLQueryBuilder,
            'sqlite': SQLQueryBuilder,
            'mongodb': MongoQueryBuilder,
            'redis': RedisCommandBuilder,
        }

    def create_query_builder(self, db_type: str) -> QueryBuilder:
        """
        创建查询构建器

        根据数据库类型创建适当类型的查询构建器。

        Args:
            db_type: 数据库类型

        Returns:
            QueryBuilder: 查询构建器实例

        Raises:
            ConfigurationError: 如果不支持的数据库类型
        """
        if not db_type:
            raise ConfigurationError("Database type is required")

        db_type = db_type.lower()

        builder_class = self.builder_classes.get(db_type)

        if not builder_class:
            supported_types = ', '.join(self.builder_classes.keys())
            raise ConfigurationError(
                f"Unsupported database type: {db_type}. "
                f"Supported types are: {supported_types}"
            )

        try:
            if db_type in ('mysql', 'postgresql', 'sqlite'):
                builder = builder_class(db_type)
            else:
                builder = builder_class()

            self.logger.info(f"Created query builder for {db_type}")
            return builder
        except Exception as e:
            self.logger.error(f"Failed to create query builder for {db_type}: {str(e)}")
            raise ConfigurationError(f"Failed to create query builder for {db_type}: {str(e)}")

    def register_builder_class(self, db_type: str, builder_class: Type[QueryBuilder]) -> None:
        """
        注册查询构建器类

        注册自定义的查询构建器类，用于创建特定类型的查询构建器。

        Args:
            db_type: 数据库类型
            builder_class: 查询构建器类
        """
        self.builder_classes[db_type.lower()] = builder_class
        self.logger.info(f"Registered query builder class for {db_type}")

    def get_supported_types(self) -> list:
        """
        获取支持的数据库类型

        Returns:
            list: 支持的数据库类型列表
        """
        return list(self.builder_classes.keys())
