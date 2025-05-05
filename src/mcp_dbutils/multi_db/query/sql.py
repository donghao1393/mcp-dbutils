"""
SQL查询构建器实现

这个模块实现了SQL查询构建器，用于构建SQL查询。
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from ..error.exceptions import QueryError
from .base import Query, QueryBuilder


class SQLQuery(Query):
    """
    SQL查询类
    
    这个类表示一个SQL查询，包含查询字符串和参数。
    """
    
    def __init__(self, query: str, params: Optional[Dict[str, Any]] = None):
        """
        初始化SQL查询
        
        Args:
            query: SQL查询字符串
            params: 查询参数
        """
        self.query = query
        self.params = params or {}
        
    def get_query_string(self) -> str:
        """
        获取查询字符串
        
        Returns:
            str: SQL查询字符串
        """
        return self.query
        
    def get_params(self) -> Dict[str, Any]:
        """
        获取查询参数
        
        Returns:
            Dict[str, Any]: 查询参数
        """
        return self.params


class SQLQueryBuilder(QueryBuilder):
    """
    SQL查询构建器类
    
    这个类实现了SQL查询构建器，用于构建SQL查询。
    """
    
    def __init__(self, db_type: str = 'mysql'):
        """
        初始化SQL查询构建器
        
        Args:
            db_type: 数据库类型，支持mysql、postgresql、sqlite
        """
        self.logger = logging.getLogger(__name__)
        self.db_type = db_type.lower()
        self.query_type = None
        self.resource_name = None
        self.fields = None
        self.data = None
        self.conditions = None
        self.order_fields = None
        self.limit_count = None
        self.offset_count = None
        
    def select(self, resource_name: str, fields: Optional[List[str]] = None) -> 'SQLQueryBuilder':
        """
        构建SELECT查询
        
        Args:
            resource_name: 表名
            fields: 要选择的字段列表，如果为None，则选择所有字段
            
        Returns:
            SQLQueryBuilder: 查询构建器实例
        """
        self.query_type = 'SELECT'
        self.resource_name = resource_name
        self.fields = fields
        return self
        
    def insert(self, resource_name: str, data: Dict[str, Any]) -> 'SQLQueryBuilder':
        """
        构建INSERT查询
        
        Args:
            resource_name: 表名
            data: 要插入的数据
            
        Returns:
            SQLQueryBuilder: 查询构建器实例
        """
        self.query_type = 'INSERT'
        self.resource_name = resource_name
        self.data = data
        return self
        
    def update(self, resource_name: str, data: Dict[str, Any], 
              condition: Optional[Dict[str, Any]] = None) -> 'SQLQueryBuilder':
        """
        构建UPDATE查询
        
        Args:
            resource_name: 表名
            data: 要更新的数据
            condition: 更新条件
            
        Returns:
            SQLQueryBuilder: 查询构建器实例
        """
        self.query_type = 'UPDATE'
        self.resource_name = resource_name
        self.data = data
        self.conditions = condition
        return self
        
    def delete(self, resource_name: str, 
              condition: Optional[Dict[str, Any]] = None) -> 'SQLQueryBuilder':
        """
        构建DELETE查询
        
        Args:
            resource_name: 表名
            condition: 删除条件
            
        Returns:
            SQLQueryBuilder: 查询构建器实例
        """
        self.query_type = 'DELETE'
        self.resource_name = resource_name
        self.conditions = condition
        return self
        
    def where(self, condition: Dict[str, Any]) -> 'SQLQueryBuilder':
        """
        添加WHERE条件
        
        Args:
            condition: 条件
            
        Returns:
            SQLQueryBuilder: 查询构建器实例
        """
        self.conditions = condition
        return self
        
    def order_by(self, fields: List[str]) -> 'SQLQueryBuilder':
        """
        添加ORDER BY子句
        
        Args:
            fields: 排序字段列表
            
        Returns:
            SQLQueryBuilder: 查询构建器实例
        """
        self.order_fields = fields
        return self
        
    def limit(self, count: int) -> 'SQLQueryBuilder':
        """
        添加LIMIT子句
        
        Args:
            count: 限制数量
            
        Returns:
            SQLQueryBuilder: 查询构建器实例
        """
        self.limit_count = count
        return self
        
    def offset(self, count: int) -> 'SQLQueryBuilder':
        """
        添加OFFSET子句
        
        Args:
            count: 偏移数量
            
        Returns:
            SQLQueryBuilder: 查询构建器实例
        """
        self.offset_count = count
        return self
        
    def build(self) -> SQLQuery:
        """
        构建SQL查询
        
        Returns:
            SQLQuery: SQL查询实例
            
        Raises:
            QueryError: 如果查询构建失败
        """
        if not self.query_type or not self.resource_name:
            raise QueryError("Query type and resource name are required")
            
        try:
            if self.query_type == 'SELECT':
                return self._build_select()
            elif self.query_type == 'INSERT':
                return self._build_insert()
            elif self.query_type == 'UPDATE':
                return self._build_update()
            elif self.query_type == 'DELETE':
                return self._build_delete()
            else:
                raise QueryError(f"Unsupported query type: {self.query_type}")
        except Exception as e:
            self.logger.error(f"Error building SQL query: {str(e)}")
            raise QueryError(f"Error building SQL query: {str(e)}")
            
    def _build_select(self) -> SQLQuery:
        """
        构建SELECT查询
        
        Returns:
            SQLQuery: SELECT查询实例
        """
        # 构建字段部分
        if self.fields:
            fields_str = ', '.join(self._quote_identifier(field) for field in self.fields)
        else:
            fields_str = '*'
            
        # 构建基本查询
        query = f"SELECT {fields_str} FROM {self._quote_identifier(self.resource_name)}"
        
        # 构建WHERE子句
        params = {}
        if self.conditions:
            where_clause, where_params = self._build_where_clause(self.conditions)
            query += f" WHERE {where_clause}"
            params.update(where_params)
            
        # 构建ORDER BY子句
        if self.order_fields:
            order_clause = ', '.join(self._quote_identifier(field) for field in self.order_fields)
            query += f" ORDER BY {order_clause}"
            
        # 构建LIMIT和OFFSET子句
        if self.limit_count is not None:
            query += f" LIMIT {self.limit_count}"
            
        if self.offset_count is not None:
            query += f" OFFSET {self.offset_count}"
            
        return SQLQuery(query, params)
        
    def _build_insert(self) -> SQLQuery:
        """
        构建INSERT查询
        
        Returns:
            SQLQuery: INSERT查询实例
        """
        if not self.data:
            raise QueryError("Data is required for INSERT query")
            
        # 构建字段和值部分
        fields = []
        placeholders = []
        params = {}
        
        for i, (field, value) in enumerate(self.data.items()):
            fields.append(self._quote_identifier(field))
            param_name = f"param_{i}"
            
            if self.db_type == 'postgresql':
                placeholders.append(f"%({param_name})s")
            else:
                placeholders.append(f":{param_name}")
                
            params[param_name] = value
            
        # 构建查询
        fields_str = ', '.join(fields)
        placeholders_str = ', '.join(placeholders)
        
        query = f"INSERT INTO {self._quote_identifier(self.resource_name)} ({fields_str}) VALUES ({placeholders_str})"
        
        return SQLQuery(query, params)
        
    def _build_update(self) -> SQLQuery:
        """
        构建UPDATE查询
        
        Returns:
            SQLQuery: UPDATE查询实例
        """
        if not self.data:
            raise QueryError("Data is required for UPDATE query")
            
        # 构建SET部分
        set_clauses = []
        params = {}
        
        for i, (field, value) in enumerate(self.data.items()):
            param_name = f"param_{i}"
            
            if self.db_type == 'postgresql':
                set_clauses.append(f"{self._quote_identifier(field)} = %({param_name})s")
            else:
                set_clauses.append(f"{self._quote_identifier(field)} = :{param_name}")
                
            params[param_name] = value
            
        # 构建基本查询
        set_str = ', '.join(set_clauses)
        query = f"UPDATE {self._quote_identifier(self.resource_name)} SET {set_str}"
        
        # 构建WHERE子句
        if self.conditions:
            where_clause, where_params = self._build_where_clause(self.conditions, len(params))
            query += f" WHERE {where_clause}"
            params.update(where_params)
            
        return SQLQuery(query, params)
        
    def _build_delete(self) -> SQLQuery:
        """
        构建DELETE查询
        
        Returns:
            SQLQuery: DELETE查询实例
        """
        # 构建基本查询
        query = f"DELETE FROM {self._quote_identifier(self.resource_name)}"
        
        # 构建WHERE子句
        params = {}
        if self.conditions:
            where_clause, where_params = self._build_where_clause(self.conditions)
            query += f" WHERE {where_clause}"
            params.update(where_params)
            
        return SQLQuery(query, params)
        
    def _build_where_clause(self, conditions: Dict[str, Any], param_offset: int = 0) -> Tuple[str, Dict[str, Any]]:
        """
        构建WHERE子句
        
        Args:
            conditions: 条件
            param_offset: 参数偏移量
            
        Returns:
            Tuple[str, Dict[str, Any]]: WHERE子句和参数
        """
        clauses = []
        params = {}
        
        for i, (field, value) in enumerate(conditions.items()):
            param_name = f"where_param_{i + param_offset}"
            
            if self.db_type == 'postgresql':
                clauses.append(f"{self._quote_identifier(field)} = %({param_name})s")
            else:
                clauses.append(f"{self._quote_identifier(field)} = :{param_name}")
                
            params[param_name] = value
            
        return ' AND '.join(clauses), params
        
    def _quote_identifier(self, identifier: str) -> str:
        """
        引用标识符
        
        根据数据库类型，使用适当的方式引用标识符。
        
        Args:
            identifier: 标识符
            
        Returns:
            str: 引用后的标识符
        """
        if self.db_type == 'mysql':
            return f"`{identifier}`"
        elif self.db_type == 'postgresql':
            return f'"{identifier}"'
        elif self.db_type == 'sqlite':
            return f'"{identifier}"'
        else:
            return identifier
