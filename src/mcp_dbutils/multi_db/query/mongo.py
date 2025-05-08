"""
MongoDB查询构建器实现

这个模块实现了MongoDB查询构建器，用于构建MongoDB查询。
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from ..error.exceptions import QueryError
from .base import Query, QueryBuilder


class MongoQuery(Query):
    """
    MongoDB查询类

    这个类表示一个MongoDB查询，包含集合名、操作类型、过滤条件等。
    """

    def __init__(self, collection: str, operation: str,
                params: Optional[Dict[str, Any]] = None):
        """
        初始化MongoDB查询

        Args:
            collection: 集合名
            operation: 操作类型
            params: 查询参数
        """
        self.collection = collection
        self.operation = operation
        self.params = params or {}

    def get_query_string(self) -> str:
        """
        获取查询字符串

        Returns:
            str: 查询字符串
        """
        # MongoDB查询不使用字符串表示，但为了兼容接口，返回一个描述性字符串
        return f"{self.operation} on {self.collection}"

    def get_params(self) -> Dict[str, Any]:
        """
        获取查询参数

        Returns:
            Dict[str, Any]: 查询参数
        """
        return {
            'collection': self.collection,
            'operation': self.operation,
            'params': self.params
        }


class MongoQueryBuilder(QueryBuilder):
    """
    MongoDB查询构建器类

    这个类实现了MongoDB查询构建器，用于构建MongoDB查询。
    """

    def __init__(self):
        """
        初始化MongoDB查询构建器
        """
        self.collection = None
        self.operation = None
        self.filter = {}
        self.projection = None
        self.sort_fields = None
        self.limit_count = None
        self.skip_count = None
        self.document = None
        self.documents = None
        self.update_data = None
        self.upsert = False
        self.pipeline = None
        self.field = None
        self.logger = logging.getLogger(__name__)

    def select(self, resource_name: str, fields: Optional[List[str]] = None) -> 'MongoQueryBuilder':
        """
        构建find查询

        Args:
            resource_name: 集合名
            fields: 要选择的字段列表，如果为None，则选择所有字段

        Returns:
            MongoQueryBuilder: 查询构建器实例
        """
        self.collection = resource_name
        self.operation = 'find'

        # 如果指定了字段，构建投影
        if fields:
            self.projection = {field: 1 for field in fields}

        return self

    def insert(self, resource_name: str, data: Dict[str, Any]) -> 'MongoQueryBuilder':
        """
        构建insert_one查询

        Args:
            resource_name: 集合名
            data: 要插入的数据

        Returns:
            MongoQueryBuilder: 查询构建器实例
        """
        self.collection = resource_name
        self.operation = 'insert_one'
        self.document = data

        return self

    def insert_many(self, resource_name: str, data: List[Dict[str, Any]]) -> 'MongoQueryBuilder':
        """
        构建insert_many查询

        Args:
            resource_name: 集合名
            data: 要插入的数据列表

        Returns:
            MongoQueryBuilder: 查询构建器实例
        """
        self.collection = resource_name
        self.operation = 'insert_many'
        self.documents = data

        return self

    def update(self, resource_name: str, data: Dict[str, Any],
              condition: Optional[Dict[str, Any]] = None) -> 'MongoQueryBuilder':
        """
        构建update_one查询

        Args:
            resource_name: 集合名
            data: 要更新的数据
            condition: 更新条件

        Returns:
            MongoQueryBuilder: 查询构建器实例
        """
        self.collection = resource_name
        self.operation = 'update_one'

        # MongoDB的更新操作需要使用$set等操作符
        if not any(key.startswith('$') for key in data):
            self.update_data = {'$set': data}
        else:
            self.update_data = data

        if condition:
            self.filter = condition

        return self

    def update_many(self, resource_name: str, data: Dict[str, Any],
                   condition: Optional[Dict[str, Any]] = None) -> 'MongoQueryBuilder':
        """
        构建update_many查询

        Args:
            resource_name: 集合名
            data: 要更新的数据
            condition: 更新条件

        Returns:
            MongoQueryBuilder: 查询构建器实例
        """
        self.collection = resource_name
        self.operation = 'update_many'

        # MongoDB的更新操作需要使用$set等操作符
        if not any(key.startswith('$') for key in data):
            self.update_data = {'$set': data}
        else:
            self.update_data = data

        if condition:
            self.filter = condition

        return self

    def delete(self, resource_name: str,
              condition: Optional[Dict[str, Any]] = None) -> 'MongoQueryBuilder':
        """
        构建delete_one查询

        Args:
            resource_name: 集合名
            condition: 删除条件

        Returns:
            MongoQueryBuilder: 查询构建器实例
        """
        self.collection = resource_name
        self.operation = 'delete_one'

        if condition:
            self.filter = condition

        return self

    def delete_many(self, resource_name: str,
                   condition: Optional[Dict[str, Any]] = None) -> 'MongoQueryBuilder':
        """
        构建delete_many查询

        Args:
            resource_name: 集合名
            condition: 删除条件

        Returns:
            MongoQueryBuilder: 查询构建器实例
        """
        self.collection = resource_name
        self.operation = 'delete_many'

        if condition:
            self.filter = condition

        return self

    def aggregate(self, resource_name: str, pipeline: List[Dict[str, Any]]) -> 'MongoQueryBuilder':
        """
        构建aggregate查询

        Args:
            resource_name: 集合名
            pipeline: 聚合管道

        Returns:
            MongoQueryBuilder: 查询构建器实例
        """
        self.collection = resource_name
        self.operation = 'aggregate'
        self.pipeline = pipeline

        return self

    def distinct(self, resource_name: str, field: str,
                condition: Optional[Dict[str, Any]] = None) -> 'MongoQueryBuilder':
        """
        构建distinct查询

        Args:
            resource_name: 集合名
            field: 字段名
            condition: 过滤条件

        Returns:
            MongoQueryBuilder: 查询构建器实例
        """
        self.collection = resource_name
        self.operation = 'distinct'
        self.field = field

        if condition:
            self.filter = condition

        return self

    def count(self, resource_name: str,
             condition: Optional[Dict[str, Any]] = None) -> 'MongoQueryBuilder':
        """
        构建count_documents查询

        Args:
            resource_name: 集合名
            condition: 计数条件

        Returns:
            MongoQueryBuilder: 查询构建器实例
        """
        self.collection = resource_name
        self.operation = 'count_documents'

        if condition:
            self.filter = condition

        return self

    def where(self, condition: Dict[str, Any]) -> 'MongoQueryBuilder':
        """
        添加过滤条件

        Args:
            condition: 条件

        Returns:
            MongoQueryBuilder: 查询构建器实例
        """
        self.filter.update(condition)
        return self

    def order_by(self, fields: List[str]) -> 'MongoQueryBuilder':
        """
        添加排序

        Args:
            fields: 排序字段列表，格式为['field1', '-field2']，
                   其中'-'前缀表示降序排序

        Returns:
            MongoQueryBuilder: 查询构建器实例
        """
        # MongoDB排序使用(field, direction)元组列表
        sort_list = []
        for field in fields:
            if field.startswith('-'):
                sort_list.append((field[1:], -1))  # 降序
            else:
                sort_list.append((field, 1))  # 升序

        self.sort_fields = sort_list
        return self

    def limit(self, count: int) -> 'MongoQueryBuilder':
        """
        添加限制

        Args:
            count: 限制数量

        Returns:
            MongoQueryBuilder: 查询构建器实例
        """
        self.limit_count = count
        return self

    def offset(self, count: int) -> 'MongoQueryBuilder':
        """
        添加跳过

        Args:
            count: 跳过数量

        Returns:
            MongoQueryBuilder: 查询构建器实例
        """
        self.skip_count = count
        return self

    def upsert_option(self, enable: bool = True) -> 'MongoQueryBuilder':
        """
        设置upsert选项

        Args:
            enable: 是否启用upsert

        Returns:
            MongoQueryBuilder: 查询构建器实例
        """
        self.upsert = enable
        return self

    def build(self) -> MongoQuery:
        """
        构建MongoDB查询

        Returns:
            MongoQuery: MongoDB查询实例
        """
        if not self.collection or not self.operation:
            raise QueryError("Collection name and operation are required")

        # 构建查询参数
        params = {}

        # 添加过滤条件
        if self.filter:
            params['filter'] = self.filter

        # 添加投影
        if self.projection:
            params['projection'] = self.projection

        # 添加排序
        if self.sort_fields:
            params['sort'] = self.sort_fields

        # 添加限制
        if self.limit_count is not None:
            params['limit'] = self.limit_count

        # 添加跳过
        if self.skip_count is not None:
            params['skip'] = self.skip_count

        # 添加文档
        if self.document:
            params['document'] = self.document

        # 添加文档列表
        if self.documents:
            params['documents'] = self.documents

        # 添加更新数据
        if self.update_data:
            params['update'] = self.update_data

        # 添加upsert选项
        if self.upsert:
            params['upsert'] = True

        # 添加聚合管道
        if self.pipeline:
            params['pipeline'] = self.pipeline

        # 添加字段
        if self.field:
            params['field'] = self.field

        return MongoQuery(self.collection, self.operation, params)
