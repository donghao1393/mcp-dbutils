"""
SQL查询构建器实现

这个模块实现了SQL查询构建器，用于构建SQL查询。
支持复杂查询条件、JOIN操作、GROUP BY和HAVING子句、子查询等高级功能。
"""

import logging
import re
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from ..error.exceptions import QueryError
from .base import Query, QueryBuilder


class Operator(Enum):
    """
    SQL操作符枚举

    定义了SQL查询中使用的操作符。
    """
    EQ = "="  # 等于
    NE = "<>"  # 不等于
    GT = ">"  # 大于
    GE = ">="  # 大于等于
    LT = "<"  # 小于
    LE = "<="  # 小于等于
    IN = "IN"  # 在列表中
    NOT_IN = "NOT IN"  # 不在列表中
    LIKE = "LIKE"  # 模糊匹配
    NOT_LIKE = "NOT LIKE"  # 不匹配
    BETWEEN = "BETWEEN"  # 在范围内
    NOT_BETWEEN = "NOT BETWEEN"  # 不在范围内
    IS_NULL = "IS NULL"  # 为空
    IS_NOT_NULL = "IS NOT NULL"  # 不为空


class Condition:
    """
    SQL条件类

    表示SQL查询中的条件。
    """

    def __init__(self, field: str, operator: Operator, value: Any = None):
        """
        初始化条件

        Args:
            field: 字段名
            operator: 操作符
            value: 值
        """
        self.field = field
        self.operator = operator
        self.value = value

    def __str__(self) -> str:
        """
        返回条件的字符串表示

        Returns:
            str: 条件的字符串表示
        """
        return f"{self.field} {self.operator.value} {self.value}"


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


class JoinType(Enum):
    """
    JOIN类型枚举

    定义了SQL查询中使用的JOIN类型。
    """
    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    FULL = "FULL JOIN"
    CROSS = "CROSS JOIN"


class Join:
    """
    JOIN类

    表示SQL查询中的JOIN操作。
    """

    def __init__(self, table: str, join_type: JoinType, on_condition: str):
        """
        初始化JOIN

        Args:
            table: 表名
            join_type: JOIN类型
            on_condition: ON条件
        """
        self.table = table
        self.join_type = join_type
        self.on_condition = on_condition

    def __str__(self) -> str:
        """
        返回JOIN的字符串表示

        Returns:
            str: JOIN的字符串表示
        """
        return f"{self.join_type.value} {self.table} ON {self.on_condition}"


class SQLQueryBuilder(QueryBuilder):
    """
    SQL查询构建器类

    这个类实现了SQL查询构建器，用于构建SQL查询。
    支持复杂查询条件、JOIN操作、GROUP BY和HAVING子句、子查询等高级功能。
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

        # 高级查询功能
        self.joins = []  # JOIN操作列表
        self.group_by_fields = None  # GROUP BY字段列表
        self.having_conditions = None  # HAVING条件
        self.complex_conditions = []  # 复杂条件列表
        self.subqueries = {}  # 子查询字典

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

    def join(self, table: str, join_type: JoinType, on_condition: str) -> 'SQLQueryBuilder':
        """
        添加JOIN子句

        Args:
            table: 表名
            join_type: JOIN类型
            on_condition: ON条件

        Returns:
            SQLQueryBuilder: 查询构建器实例
        """
        self.joins.append(Join(table, join_type, on_condition))
        return self

    def inner_join(self, table: str, on_condition: str) -> 'SQLQueryBuilder':
        """
        添加INNER JOIN子句

        Args:
            table: 表名
            on_condition: ON条件

        Returns:
            SQLQueryBuilder: 查询构建器实例
        """
        return self.join(table, JoinType.INNER, on_condition)

    def left_join(self, table: str, on_condition: str) -> 'SQLQueryBuilder':
        """
        添加LEFT JOIN子句

        Args:
            table: 表名
            on_condition: ON条件

        Returns:
            SQLQueryBuilder: 查询构建器实例
        """
        return self.join(table, JoinType.LEFT, on_condition)

    def right_join(self, table: str, on_condition: str) -> 'SQLQueryBuilder':
        """
        添加RIGHT JOIN子句

        Args:
            table: 表名
            on_condition: ON条件

        Returns:
            SQLQueryBuilder: 查询构建器实例
        """
        return self.join(table, JoinType.RIGHT, on_condition)

    def full_join(self, table: str, on_condition: str) -> 'SQLQueryBuilder':
        """
        添加FULL JOIN子句

        Args:
            table: 表名
            on_condition: ON条件

        Returns:
            SQLQueryBuilder: 查询构建器实例
        """
        return self.join(table, JoinType.FULL, on_condition)

    def cross_join(self, table: str) -> 'SQLQueryBuilder':
        """
        添加CROSS JOIN子句

        Args:
            table: 表名

        Returns:
            SQLQueryBuilder: 查询构建器实例
        """
        return self.join(table, JoinType.CROSS, "1=1")

    def group_by(self, fields: List[str]) -> 'SQLQueryBuilder':
        """
        添加GROUP BY子句

        Args:
            fields: 分组字段列表

        Returns:
            SQLQueryBuilder: 查询构建器实例
        """
        self.group_by_fields = fields
        return self

    def having(self, conditions: Dict[str, Any]) -> 'SQLQueryBuilder':
        """
        添加HAVING子句

        Args:
            conditions: 条件

        Returns:
            SQLQueryBuilder: 查询构建器实例
        """
        self.having_conditions = conditions
        return self

    def add_condition(self, field: str, operator: Operator, value: Any) -> 'SQLQueryBuilder':
        """
        添加复杂条件

        Args:
            field: 字段名
            operator: 操作符
            value: 值

        Returns:
            SQLQueryBuilder: 查询构建器实例
        """
        self.complex_conditions.append(Condition(field, operator, value))
        return self

    def add_subquery(self, name: str, subquery: 'SQLQueryBuilder') -> 'SQLQueryBuilder':
        """
        添加子查询

        Args:
            name: 子查询名称
            subquery: 子查询构建器

        Returns:
            SQLQueryBuilder: 查询构建器实例
        """
        self.subqueries[name] = subquery
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

        # 构建JOIN子句
        for join in self.joins:
            query += f" {join.join_type.value} {self._quote_identifier(join.table)} ON {join.on_condition}"

        # 构建WHERE子句
        params = {}
        where_clauses = []

        # 处理简单条件
        if self.conditions:
            simple_where_clause, simple_where_params = self._build_where_clause(self.conditions)
            where_clauses.append(simple_where_clause)
            params.update(simple_where_params)

        # 处理复杂条件
        if self.complex_conditions:
            complex_where_clauses = []
            for i, condition in enumerate(self.complex_conditions):
                param_name = f"complex_param_{i}"

                if condition.operator in (Operator.IS_NULL, Operator.IS_NOT_NULL):
                    # IS NULL和IS NOT NULL不需要参数
                    complex_where_clauses.append(f"{self._quote_identifier(condition.field)} {condition.operator.value}")
                elif condition.operator in (Operator.IN, Operator.NOT_IN):
                    # IN和NOT IN需要列表参数
                    if not isinstance(condition.value, (list, tuple)):
                        raise QueryError(f"Value for {condition.operator.value} must be a list or tuple")

                    placeholders = []
                    for j, val in enumerate(condition.value):
                        val_param_name = f"{param_name}_{j}"

                        if self.db_type == 'postgresql':
                            placeholders.append(f"%({val_param_name})s")
                        else:
                            placeholders.append(f":{val_param_name}")

                        params[val_param_name] = val

                    complex_where_clauses.append(f"{self._quote_identifier(condition.field)} {condition.operator.value} ({', '.join(placeholders)})")
                elif condition.operator in (Operator.BETWEEN, Operator.NOT_BETWEEN):
                    # BETWEEN和NOT BETWEEN需要两个参数
                    if not isinstance(condition.value, (list, tuple)) or len(condition.value) != 2:
                        raise QueryError(f"Value for {condition.operator.value} must be a list or tuple of length 2")

                    param_name_1 = f"{param_name}_1"
                    param_name_2 = f"{param_name}_2"

                    if self.db_type == 'postgresql':
                        complex_where_clauses.append(f"{self._quote_identifier(condition.field)} {condition.operator.value} %({param_name_1})s AND %({param_name_2})s")
                    else:
                        complex_where_clauses.append(f"{self._quote_identifier(condition.field)} {condition.operator.value} :{param_name_1} AND :{param_name_2}")

                    params[param_name_1] = condition.value[0]
                    params[param_name_2] = condition.value[1]
                else:
                    # 其他操作符
                    if self.db_type == 'postgresql':
                        complex_where_clauses.append(f"{self._quote_identifier(condition.field)} {condition.operator.value} %({param_name})s")
                    else:
                        complex_where_clauses.append(f"{self._quote_identifier(condition.field)} {condition.operator.value} :{param_name}")

                    params[param_name] = condition.value

            if complex_where_clauses:
                where_clauses.append(' AND '.join(complex_where_clauses))

        # 合并所有WHERE子句
        if where_clauses:
            query += f" WHERE {' AND '.join(where_clauses)}"

        # 构建GROUP BY子句
        if self.group_by_fields:
            group_by_clause = ', '.join(self._quote_identifier(field) for field in self.group_by_fields)
            query += f" GROUP BY {group_by_clause}"

            # 构建HAVING子句
            if self.having_conditions:
                having_clause, having_params = self._build_where_clause(self.having_conditions, len(params))
                query += f" HAVING {having_clause}"
                params.update(having_params)

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
        elif self.db_type == 'postgresql' or self.db_type == 'sqlite':
            return f'"{identifier}"'
        else:
            return identifier
