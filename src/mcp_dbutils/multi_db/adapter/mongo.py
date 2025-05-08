"""
MongoDB适配器实现

这个模块实现了MongoDB数据库的适配器。
"""

import logging
import re
from typing import Any, Dict, List, Optional

from bson.objectid import ObjectId

from ..connection.mongo import MongoConnection
from ..error.exceptions import (
    ConnectionError,
    DatabaseError,
    QueryError,
    ResourceNotFoundError,
)
from .base import AdapterBase


class MongoAdapter(AdapterBase):
    """
    MongoDB适配器类

    这个类实现了MongoDB数据库的适配器，提供统一的操作接口。
    """

    def __init__(self, connection: MongoConnection):
        """
        初始化MongoDB适配器

        Args:
            connection: MongoDB数据库连接
        """
        super().__init__(connection)
        self.logger = logging.getLogger(__name__)
        self.mongo_connection = connection

    def execute_query(self, query: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> Any:
        """
        执行MongoDB查询

        执行只读MongoDB查询。

        Args:
            query: MongoDB查询，包含操作类型、集合名称和查询参数
            params: 额外的查询参数

        Returns:
            查询结果

        Raises:
            QueryError: 如果执行查询时发生错误
        """
        try:
            # 验证查询是否为只读操作
            operation = query.get('operation', '')
            if operation not in ['find', 'find_one', 'count_documents', 'aggregate', 'distinct']:
                raise QueryError(f"Operation '{operation}' is not a read operation")

            # 执行查询
            return self.connection.execute(query, params)

        except ConnectionError as e:
            raise QueryError(f"MongoDB query execution error: {str(e)}")
        except Exception as e:
            raise QueryError(f"Unexpected error executing MongoDB query: {str(e)}")

    def execute_write(self, query: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> Any:
        """
        执行MongoDB写操作

        执行MongoDB写操作。

        Args:
            query: MongoDB写操作，包含操作类型、集合名称和操作参数
            params: 额外的操作参数

        Returns:
            操作结果

        Raises:
            QueryError: 如果执行写操作时发生错误
        """
        try:
            # 验证查询是否为写操作
            operation = query.get('operation', '')
            if operation not in ['insert_one', 'insert_many', 'update_one', 'update_many', 'delete_one', 'delete_many']:
                raise QueryError(f"Operation '{operation}' is not a write operation")

            # 执行写操作
            return self.connection.execute(query, params)

        except ConnectionError as e:
            raise QueryError(f"MongoDB write operation error: {str(e)}")
        except Exception as e:
            raise QueryError(f"Unexpected error executing MongoDB write operation: {str(e)}")

    def list_resources(self) -> List[Dict[str, Any]]:
        """
        列出数据库中的所有集合

        Returns:
            List[Dict[str, Any]]: 集合列表，每个集合包含名称和类型等信息

        Raises:
            DatabaseError: 如果列出集合时发生错误
        """
        try:
            # 确保连接已建立
            if not self.connection.is_connected():
                self.connection.connect()

            # 获取所有集合
            collections = self.mongo_connection.db.list_collection_names()

            # 构建结果
            result = []
            for collection_name in collections:
                # 获取集合信息
                stats = self._get_collection_stats(collection_name)

                # 构建集合信息
                collection_info = {
                    'name': collection_name,
                    'type': 'COLLECTION',
                    'count': stats.get('count', 0),
                    'size': stats.get('size', 0),
                    'created_at': None,  # MongoDB不直接提供创建时间
                    'updated_at': None,  # MongoDB不直接提供更新时间
                }

                result.append(collection_info)

            return result

        except ConnectionError as e:
            raise DatabaseError(f"Failed to list MongoDB collections: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Unexpected error listing MongoDB collections: {str(e)}")

    def _get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        获取集合统计信息

        Args:
            collection_name: 集合名

        Returns:
            Dict[str, Any]: 集合统计信息
        """
        try:
            # 执行collStats命令获取集合统计信息
            stats = self.mongo_connection.db.command('collStats', collection_name)

            return {
                'count': stats.get('count', 0),
                'size': stats.get('size', 0),
                'avg_obj_size': stats.get('avgObjSize', 0),
                'storage_size': stats.get('storageSize', 0),
                'index_size': stats.get('totalIndexSize', 0),
                'total_size': stats.get('size', 0) + stats.get('totalIndexSize', 0),
            }

        except Exception as e:
            self.logger.warning(f"Failed to get stats for collection {collection_name}: {str(e)}")
            return {
                'count': 0,
                'size': 0,
                'avg_obj_size': 0,
                'storage_size': 0,
                'index_size': 0,
                'total_size': 0,
            }

    def describe_resource(self, resource_name: str) -> Dict[str, Any]:
        """
        描述集合结构

        获取集合的详细信息，如字段结构、索引等。

        Args:
            resource_name: 集合名

        Returns:
            Dict[str, Any]: 集合详细信息

        Raises:
            ResourceNotFoundError: 如果集合不存在
            DatabaseError: 如果描述集合时发生错误
        """
        try:
            # 检查集合是否存在
            if not self._resource_exists(resource_name):
                raise ResourceNotFoundError(f"Collection '{resource_name}' does not exist")

            # 获取集合统计信息
            stats = self._get_collection_stats(resource_name)

            # 获取集合索引
            indexes = self._get_indexes(resource_name)

            # 获取集合字段结构（通过采样文档）
            fields = self._get_fields(resource_name)

            # 构建结果
            result = {
                'name': resource_name,
                'type': 'COLLECTION',
                'count': stats.get('count', 0),
                'size': stats.get('size', 0),
                'avg_obj_size': stats.get('avg_obj_size', 0),
                'storage_size': stats.get('storage_size', 0),
                'index_size': stats.get('index_size', 0),
                'total_size': stats.get('total_size', 0),
                'indexes': indexes,
                'fields': fields,
            }

            return result

        except ResourceNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to describe MongoDB collection '{resource_name}': {str(e)}")

    def _resource_exists(self, resource_name: str) -> bool:
        """
        检查集合是否存在

        Args:
            resource_name: 集合名

        Returns:
            bool: 如果集合存在，则返回True，否则返回False
        """
        try:
            # 确保连接已建立
            if not self.connection.is_connected():
                self.connection.connect()

            # 获取所有集合
            collections = self.mongo_connection.db.list_collection_names()

            return resource_name in collections

        except Exception as e:
            self.logger.error(f"Error checking if collection '{resource_name}' exists: {str(e)}")
            return False

    def _get_indexes(self, collection_name: str) -> List[Dict[str, Any]]:
        """
        获取集合索引

        Args:
            collection_name: 集合名

        Returns:
            List[Dict[str, Any]]: 索引列表
        """
        try:
            # 获取集合索引
            collection = self.mongo_connection.db[collection_name]
            index_info = collection.index_information()

            # 构建索引信息
            indexes = []
            for name, info in index_info.items():
                index = {
                    'name': name,
                    'unique': info.get('unique', False),
                    'columns': [key[0] for key in info['key']],
                    'directions': [key[1] for key in info['key']],
                }
                indexes.append(index)

            return indexes

        except Exception as e:
            self.logger.warning(f"Failed to get indexes for collection {collection_name}: {str(e)}")
            return []

    def _get_fields(self, collection_name: str) -> List[Dict[str, Any]]:
        """
        获取集合字段结构

        通过采样文档推断集合的字段结构。

        Args:
            collection_name: 集合名

        Returns:
            List[Dict[str, Any]]: 字段列表
        """
        try:
            # 获取集合
            collection = self.mongo_connection.db[collection_name]

            # 获取一个样本文档
            sample_doc = collection.find_one()

            if not sample_doc:
                return []

            # 分析文档字段
            fields = []
            for field_name, value in sample_doc.items():
                field_type = type(value).__name__

                # 处理ObjectId类型
                if isinstance(value, ObjectId):
                    field_type = 'ObjectId'

                field = {
                    'name': field_name,
                    'type': field_type,
                    'sample_value': str(value) if isinstance(value, ObjectId) else value,
                }
                fields.append(field)

            return fields

        except Exception as e:
            self.logger.warning(f"Failed to get fields for collection {collection_name}: {str(e)}")
            return []

    def get_resource_stats(self, resource_name: str) -> Dict[str, Any]:
        """
        获取集合统计信息

        获取集合的统计信息，如文档数、大小等。

        Args:
            resource_name: 集合名

        Returns:
            Dict[str, Any]: 集合统计信息

        Raises:
            ResourceNotFoundError: 如果集合不存在
            DatabaseError: 如果获取集合统计信息时发生错误
        """
        try:
            # 检查集合是否存在
            if not self._resource_exists(resource_name):
                raise ResourceNotFoundError(f"Collection '{resource_name}' does not exist")

            # 获取集合统计信息
            stats = self._get_collection_stats(resource_name)

            return stats

        except ResourceNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to get stats for MongoDB collection '{resource_name}': {str(e)}")

    def extract_resource_name(self, query: Dict[str, Any]) -> Optional[str]:
        """
        从MongoDB查询中提取集合名

        从MongoDB查询中提取操作的集合名，用于权限检查。

        Args:
            query: MongoDB查询

        Returns:
            Optional[str]: 集合名，如果无法提取，则返回None
        """
        try:
            # 从查询中提取集合名
            collection_name = query.get('collection')

            if not collection_name:
                return None

            # 返回大写的集合名，与权限配置保持一致
            return collection_name.upper()

        except Exception:
            return None
