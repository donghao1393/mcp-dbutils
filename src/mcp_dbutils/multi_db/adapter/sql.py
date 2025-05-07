"""
SQL适配器实现

这个模块实现了SQL数据库的适配器，支持各种SQL数据库，如MySQL、PostgreSQL等。
提供了查询执行、资源管理、存储过程调用等功能。
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union, Callable

from ..connection.base import ConnectionBase
from ..connection.sql import SQLConnection
from ..error.exceptions import (
    ConnectionError,
    DatabaseError,
    QueryError,
    ResourceNotFoundError,
    NotImplementedError,
)
from .base import AdapterBase


class SQLAdapter(AdapterBase):
    """
    SQL适配器类

    这个类实现了SQL数据库的适配器，提供统一的操作接口。
    支持查询执行、资源管理、存储过程调用、批量操作等功能。
    """

    def __init__(self, connection: SQLConnection):
        """
        初始化SQL适配器

        Args:
            connection: SQL数据库连接
        """
        super().__init__(connection)
        self.logger = logging.getLogger(__name__)

        # 确保连接是SQLConnection类型
        if not isinstance(connection, SQLConnection):
            raise TypeError("Connection must be an instance of SQLConnection")

        self.db_type = connection.db_type

        # 支持的数据库特性
        self.features = {
            'stored_procedures': self.db_type in ('mysql', 'postgresql', 'sqlserver'),
            'batch_operations': True,
            'transactions': True,
            'foreign_keys': True,
            'views': True,
            'triggers': self.db_type in ('mysql', 'postgresql', 'sqlserver', 'sqlite'),
        }

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Tuple]:
        """
        执行SQL查询

        执行只读SQL查询，如SELECT语句。

        Args:
            query: SQL查询语句
            params: 查询参数

        Returns:
            List[Tuple]: 查询结果，每行数据为一个元组

        Raises:
            QueryError: 如果执行查询时发生错误
        """
        try:
            # 确保查询是只读的
            if not self._is_read_query(query):
                raise QueryError("Only read queries are allowed with execute_query")

            result = self.connection.execute(query, params)
            return result
        except ConnectionError as e:
            self.logger.error(f"Connection error executing query: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error executing query: {str(e)}")
            raise QueryError(f"Error executing query: {str(e)}", query=query, cause=e)

    def execute_write(self, query: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行SQL写操作

        执行SQL写操作，如INSERT、UPDATE、DELETE语句。

        Args:
            query: SQL写操作语句
            params: 操作参数

        Returns:
            Dict[str, Any]: 操作结果，包含affected_rows和last_insert_id

        Raises:
            QueryError: 如果执行写操作时发生错误
        """
        try:
            # 确保查询是写操作
            if self._is_read_query(query):
                raise QueryError("Write operations are required with execute_write")

            result = self.connection.execute(query, params)
            return result
        except ConnectionError as e:
            self.logger.error(f"Connection error executing write operation: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error executing write operation: {str(e)}")
            raise QueryError(f"Error executing write operation: {str(e)}", query=query, cause=e)

    def list_resources(self) -> List[Dict[str, Any]]:
        """
        列出数据库中的所有表

        Returns:
            List[Dict[str, Any]]: 表列表，每个表包含名称和类型等信息

        Raises:
            DatabaseError: 如果列出表时发生错误
        """
        try:
            if self.db_type == 'mysql':
                query = """
                SELECT
                    table_name AS name,
                    table_type AS type,
                    engine AS engine,
                    table_comment AS comment,
                    create_time AS created_at,
                    update_time AS updated_at
                FROM
                    information_schema.tables
                WHERE
                    table_schema = DATABASE()
                ORDER BY
                    table_name
                """
            elif self.db_type == 'postgresql':
                query = """
                SELECT
                    tablename AS name,
                    'TABLE' AS type,
                    NULL AS engine,
                    obj_description(pg_class.oid) AS comment,
                    NULL AS created_at,
                    NULL AS updated_at
                FROM
                    pg_catalog.pg_tables
                JOIN
                    pg_catalog.pg_class ON pg_tables.tablename = pg_class.relname
                WHERE
                    schemaname = 'public'
                ORDER BY
                    tablename
                """
            elif self.db_type == 'sqlite':
                query = """
                SELECT
                    name,
                    'TABLE' AS type,
                    NULL AS engine,
                    NULL AS comment,
                    NULL AS created_at,
                    NULL AS updated_at
                FROM
                    sqlite_master
                WHERE
                    type = 'table' AND
                    name NOT LIKE 'sqlite_%'
                ORDER BY
                    name
                """
            else:
                raise DatabaseError(f"Unsupported database type: {self.db_type}")

            result = self.execute_query(query)

            # 转换结果为字典列表
            resources = []
            for row in result:
                if self.db_type == 'mysql' or self.db_type == 'postgresql' or self.db_type == 'sqlite':
                    resources.append({
                        'name': row[0],
                        'type': row[1],
                        'engine': row[2],
                        'comment': row[3],
                        'created_at': row[4],
                        'updated_at': row[5]
                    })

            return resources
        except Exception as e:
            self.logger.error(f"Error listing resources: {str(e)}")
            raise DatabaseError(f"Error listing resources: {str(e)}", cause=e)

    def describe_resource(self, resource_name: str) -> Dict[str, Any]:
        """
        描述表结构

        获取表的详细信息，如列结构、索引等。

        Args:
            resource_name: 表名

        Returns:
            Dict[str, Any]: 表详细信息

        Raises:
            ResourceNotFoundError: 如果表不存在
            DatabaseError: 如果描述表时发生错误
        """
        try:
            # 检查表是否存在
            if not self._resource_exists(resource_name):
                raise ResourceNotFoundError(f"Table '{resource_name}' not found", resource_name=resource_name)

            # 获取列信息
            columns = self._get_columns(resource_name)

            # 获取索引信息
            indexes = self._get_indexes(resource_name)

            # 获取外键信息
            foreign_keys = self._get_foreign_keys(resource_name)

            return {
                'name': resource_name,
                'columns': columns,
                'indexes': indexes,
                'foreign_keys': foreign_keys
            }
        except ResourceNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error describing resource '{resource_name}': {str(e)}")
            raise DatabaseError(f"Error describing resource '{resource_name}': {str(e)}", cause=e)

    def get_resource_stats(self, resource_name: str) -> Dict[str, Any]:
        """
        获取表统计信息

        获取表的统计信息，如行数、大小等。

        Args:
            resource_name: 表名

        Returns:
            Dict[str, Any]: 表统计信息

        Raises:
            ResourceNotFoundError: 如果表不存在
            DatabaseError: 如果获取表统计信息时发生错误
        """
        try:
            # 检查表是否存在
            if not self._resource_exists(resource_name):
                raise ResourceNotFoundError(f"Table '{resource_name}' not found", resource_name=resource_name)

            stats = {}

            # 获取行数
            if self.db_type == 'mysql':
                query = f"SELECT COUNT(*) FROM `{resource_name}`"
            elif self.db_type == 'postgresql' or self.db_type == 'sqlite':
                query = f'SELECT COUNT(*) FROM "{resource_name}"'
            else:
                raise DatabaseError(f"Unsupported database type: {self.db_type}")

            result = self.execute_query(query)
            stats['row_count'] = result[0][0] if result else 0

            # 获取表大小（仅适用于MySQL和PostgreSQL）
            if self.db_type == 'mysql':
                query = """
                SELECT
                    data_length,
                    index_length,
                    data_length + index_length AS total_size
                FROM
                    information_schema.tables
                WHERE
                    table_schema = DATABASE() AND
                    table_name = %s
                """
                result = self.execute_query(query, {'resource_name': resource_name})
                if result:
                    stats['data_size'] = result[0][0]
                    stats['index_size'] = result[0][1]
                    stats['total_size'] = result[0][2]
            elif self.db_type == 'postgresql':
                query = """
                SELECT
                    pg_total_relation_size(%s) AS total_size,
                    pg_relation_size(%s) AS data_size,
                    pg_total_relation_size(%s) - pg_relation_size(%s) AS index_size
                """
                result = self.execute_query(query, {
                    'resource_name1': resource_name,
                    'resource_name2': resource_name,
                    'resource_name3': resource_name,
                    'resource_name4': resource_name
                })
                if result:
                    stats['total_size'] = result[0][0]
                    stats['data_size'] = result[0][1]
                    stats['index_size'] = result[0][2]

            return stats
        except ResourceNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error getting resource stats for '{resource_name}': {str(e)}")
            raise DatabaseError(f"Error getting resource stats for '{resource_name}': {str(e)}", cause=e)

    def extract_resource_name(self, query: str) -> Optional[str]:
        """
        从SQL查询中提取表名

        从SQL查询中提取操作的表名，用于权限检查。

        Args:
            query: SQL查询

        Returns:
            Optional[str]: 表名，如果无法提取，则返回None
        """
        if not query:
            return "unknown_table"

        query = query.strip().upper()

        try:
            # 规范化空白字符，将多行SQL转换为单行
            normalized_query = " ".join(query.split())

            # 提取表名
            if normalized_query.startswith("INSERT INTO"):
                # INSERT INTO table_name ...
                match = normalized_query.split("INTO", 1)[1].strip().split(" ", 1)[0]
                return match.strip('`"[]')
            elif normalized_query.startswith("UPDATE"):
                # UPDATE table_name ...
                match = normalized_query.split("UPDATE", 1)[1].strip().split(" ", 1)[0]
                return match.strip('`"[]')
            elif normalized_query.startswith("DELETE FROM"):
                # DELETE FROM table_name ...
                match = normalized_query.split("FROM", 1)[1].strip().split(" ", 1)[0]
                return match.strip('`"[]')
            elif normalized_query.startswith("SELECT"):
                # SELECT ... FROM table_name ...
                # 这种情况比较复杂，可能涉及多个表和子查询
                # 简单实现，可能不适用于所有情况
                from_parts = normalized_query.split("FROM", 1)
                if len(from_parts) > 1:
                    table_part = from_parts[1].strip().split(" ", 1)[0]
                    return table_part.strip('`"[]')

            return "unknown_table"
        except Exception:
            return "unknown_table"

    def _is_read_query(self, query: str) -> bool:
        """
        判断查询是否是只读的

        Args:
            query: SQL查询

        Returns:
            bool: 如果查询是只读的，则返回True，否则返回False
        """
        if not query:
            return False

        query = query.strip().upper()

        # 简单判断，可能不适用于所有情况
        return query.startswith("SELECT") or query.startswith("SHOW") or query.startswith("DESCRIBE") or query.startswith("EXPLAIN")

    def _resource_exists(self, resource_name: str) -> bool:
        """
        检查表是否存在

        Args:
            resource_name: 表名

        Returns:
            bool: 如果表存在，则返回True，否则返回False
        """
        try:
            if self.db_type == 'mysql':
                query = """
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = DATABASE() AND table_name = %s
                """
            elif self.db_type == 'postgresql':
                query = """
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = %s
                """
            elif self.db_type == 'sqlite':
                query = """
                SELECT 1
                FROM sqlite_master
                WHERE type = 'table' AND name = ?
                """
            else:
                raise DatabaseError(f"Unsupported database type: {self.db_type}")

            result = self.execute_query(query, {'resource_name': resource_name})
            return len(result) > 0
        except Exception as e:
            self.logger.error(f"Error checking if resource '{resource_name}' exists: {str(e)}")
            return False

    def _get_columns(self, resource_name: str) -> List[Dict[str, Any]]:
        """
        获取表的列信息

        Args:
            resource_name: 表名

        Returns:
            List[Dict[str, Any]]: 列信息列表
        """
        try:
            if self.db_type == 'mysql':
                query = """
                SELECT
                    column_name,
                    data_type,
                    column_type,
                    is_nullable,
                    column_default,
                    column_comment,
                    extra
                FROM
                    information_schema.columns
                WHERE
                    table_schema = DATABASE() AND
                    table_name = %s
                ORDER BY
                    ordinal_position
                """
            elif self.db_type == 'postgresql':
                query = """
                SELECT
                    column_name,
                    data_type,
                    udt_name,
                    is_nullable,
                    column_default,
                    NULL AS column_comment,
                    NULL AS extra
                FROM
                    information_schema.columns
                WHERE
                    table_schema = 'public' AND
                    table_name = %s
                ORDER BY
                    ordinal_position
                """
            elif self.db_type == 'sqlite':
                query = f'PRAGMA table_info("{resource_name}")'
            else:
                raise DatabaseError(f"Unsupported database type: {self.db_type}")

            result = self.execute_query(query, {'resource_name': resource_name})

            columns = []
            for row in result:
                if self.db_type == 'mysql' or self.db_type == 'postgresql':
                    columns.append({
                        'name': row[0],
                        'type': row[1],
                        'full_type': row[2],
                        'nullable': row[3] == 'YES',
                        'default': row[4],
                        'comment': row[5],
                        'extra': row[6]
                    })
                elif self.db_type == 'sqlite':
                    columns.append({
                        'name': row[1],
                        'type': row[2],
                        'full_type': row[2],
                        'nullable': row[3] == 0,
                        'default': row[4],
                        'comment': None,
                        'extra': 'PRIMARY KEY' if row[5] == 1 else None
                    })

            return columns
        except Exception as e:
            self.logger.error(f"Error getting columns for '{resource_name}': {str(e)}")
            raise DatabaseError(f"Error getting columns for '{resource_name}': {str(e)}", cause=e)

    def _get_indexes(self, resource_name: str) -> List[Dict[str, Any]]:
        """
        获取表的索引信息

        Args:
            resource_name: 表名

        Returns:
            List[Dict[str, Any]]: 索引信息列表
        """
        try:
            if self.db_type == 'mysql':
                query = """
                SELECT
                    index_name,
                    column_name,
                    non_unique,
                    seq_in_index
                FROM
                    information_schema.statistics
                WHERE
                    table_schema = DATABASE() AND
                    table_name = %s
                ORDER BY
                    index_name, seq_in_index
                """
            elif self.db_type == 'postgresql':
                query = """
                SELECT
                    i.relname AS index_name,
                    a.attname AS column_name,
                    ix.indisunique AS non_unique,
                    a.attnum AS seq_in_index
                FROM
                    pg_index ix
                JOIN
                    pg_class i ON i.oid = ix.indexrelid
                JOIN
                    pg_class t ON t.oid = ix.indrelid
                JOIN
                    pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
                WHERE
                    t.relname = %s
                ORDER BY
                    i.relname, a.attnum
                """
            elif self.db_type == 'sqlite':
                query = f'PRAGMA index_list("{resource_name}")'
            else:
                raise DatabaseError(f"Unsupported database type: {self.db_type}")

            result = self.execute_query(query, {'resource_name': resource_name})

            indexes = {}
            if self.db_type == 'mysql' or self.db_type == 'postgresql':
                for row in result:
                    index_name = row[0]
                    column_name = row[1]
                    non_unique = row[2]

                    if index_name not in indexes:
                        indexes[index_name] = {
                            'name': index_name,
                            'columns': [],
                            'unique': not non_unique
                        }

                    indexes[index_name]['columns'].append(column_name)
            elif self.db_type == 'sqlite':
                for row in result:
                    index_name = row[1]
                    unique = row[2] == 1

                    # 获取索引列
                    index_info_query = f'PRAGMA index_info("{index_name}")'
                    index_info_result = self.execute_query(index_info_query)

                    columns = []
                    for index_info_row in index_info_result:
                        columns.append(index_info_row[2])

                    indexes[index_name] = {
                        'name': index_name,
                        'columns': columns,
                        'unique': unique
                    }

            return list(indexes.values())
        except Exception as e:
            self.logger.error(f"Error getting indexes for '{resource_name}': {str(e)}")
            raise DatabaseError(f"Error getting indexes for '{resource_name}': {str(e)}", cause=e)

    def _get_foreign_keys(self, resource_name: str) -> List[Dict[str, Any]]:
        """
        获取表的外键信息

        Args:
            resource_name: 表名

        Returns:
            List[Dict[str, Any]]: 外键信息列表
        """
        try:
            if self.db_type == 'mysql':
                query = """
                SELECT
                    constraint_name,
                    column_name,
                    referenced_table_name,
                    referenced_column_name
                FROM
                    information_schema.key_column_usage
                WHERE
                    table_schema = DATABASE() AND
                    table_name = %s AND
                    referenced_table_name IS NOT NULL
                ORDER BY
                    constraint_name, ordinal_position
                """
            elif self.db_type == 'postgresql':
                query = """
                SELECT
                    tc.constraint_name,
                    kcu.column_name,
                    ccu.table_name AS referenced_table_name,
                    ccu.column_name AS referenced_column_name
                FROM
                    information_schema.table_constraints tc
                JOIN
                    information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
                JOIN
                    information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
                WHERE
                    tc.constraint_type = 'FOREIGN KEY' AND
                    tc.table_schema = 'public' AND
                    tc.table_name = %s
                ORDER BY
                    tc.constraint_name, kcu.ordinal_position
                """
            elif self.db_type == 'sqlite':
                query = f'PRAGMA foreign_key_list("{resource_name}")'
            else:
                raise DatabaseError(f"Unsupported database type: {self.db_type}")

            result = self.execute_query(query, {'resource_name': resource_name})

            foreign_keys = {}
            if self.db_type == 'mysql' or self.db_type == 'postgresql':
                for row in result:
                    constraint_name = row[0]
                    column_name = row[1]
                    referenced_table = row[2]
                    referenced_column = row[3]

                    if constraint_name not in foreign_keys:
                        foreign_keys[constraint_name] = {
                            'name': constraint_name,
                            'columns': [],
                            'referenced_table': referenced_table,
                            'referenced_columns': []
                        }

                    foreign_keys[constraint_name]['columns'].append(column_name)
                    foreign_keys[constraint_name]['referenced_columns'].append(referenced_column)
            elif self.db_type == 'sqlite':
                for row in result:
                    id = row[0]
                    column_name = row[3]
                    referenced_table = row[2]
                    referenced_column = row[4]

                    constraint_name = f"fk_{resource_name}_{id}"

                    if constraint_name not in foreign_keys:
                        foreign_keys[constraint_name] = {
                            'name': constraint_name,
                            'columns': [],
                            'referenced_table': referenced_table,
                            'referenced_columns': []
                        }

                    foreign_keys[constraint_name]['columns'].append(column_name)
                    foreign_keys[constraint_name]['referenced_columns'].append(referenced_column)

            return list(foreign_keys.values())
        except Exception as e:
            self.logger.error(f"Error getting foreign keys for '{resource_name}': {str(e)}")
            raise DatabaseError(f"Error getting foreign keys for '{resource_name}': {str(e)}", cause=e)

    def execute_batch(self, query: str, params_list: List[Dict[str, Any]]) -> List[Any]:
        """
        批量执行SQL查询

        批量执行给定的SQL查询，每个查询使用不同的参数。

        Args:
            query: SQL查询语句
            params_list: 查询参数列表

        Returns:
            List[Any]: 查询结果列表

        Raises:
            QueryError: 如果执行查询时发生错误
        """
        try:
            return self.connection.execute_batch(query, params_list)
        except ConnectionError as e:
            self.logger.error(f"Connection error executing batch query: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error executing batch query: {str(e)}")
            raise QueryError(f"Error executing batch query: {str(e)}", query=query, cause=e)

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        执行多个SQL查询

        使用executemany执行给定的SQL查询，适用于批量插入或更新。

        Args:
            query: SQL查询语句
            params_list: 查询参数列表

        Returns:
            Dict[str, Any]: 执行结果，包含affected_rows

        Raises:
            QueryError: 如果执行查询时发生错误
        """
        try:
            return self.connection.execute_many(query, params_list)
        except ConnectionError as e:
            self.logger.error(f"Connection error executing many query: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error executing many query: {str(e)}")
            raise QueryError(f"Error executing many query: {str(e)}", query=query, cause=e)

    def call_procedure(self, procedure_name: str, params: Optional[Dict[str, Any]] = None) -> List[Tuple]:
        """
        调用存储过程

        调用数据库中的存储过程。

        Args:
            procedure_name: 存储过程名称
            params: 存储过程参数

        Returns:
            List[Tuple]: 存储过程执行结果

        Raises:
            QueryError: 如果调用存储过程时发生错误
            NotImplementedError: 如果数据库不支持存储过程
        """
        if not self.features['stored_procedures']:
            raise NotImplementedError(f"Database type {self.db_type} does not support stored procedures")

        try:
            if self.db_type == 'mysql':
                # MySQL使用CALL语句调用存储过程
                param_placeholders = []
                if params:
                    for i in range(len(params)):
                        param_placeholders.append(f":param_{i}")

                call_query = f"CALL {procedure_name}({', '.join(param_placeholders)})"

                # 转换参数
                call_params = {}
                if params:
                    for i, (_, value) in enumerate(params.items()):
                        call_params[f"param_{i}"] = value

                return self.execute_query(call_query, call_params)
            elif self.db_type == 'postgresql':
                # PostgreSQL使用SELECT语句调用存储过程
                param_placeholders = []
                if params:
                    for i in range(len(params)):
                        param_placeholders.append(f"%({i})s")

                call_query = f"SELECT * FROM {procedure_name}({', '.join(param_placeholders)})"

                # 转换参数
                call_params = {}
                if params:
                    for i, (_, value) in enumerate(params.items()):
                        call_params[str(i)] = value

                return self.execute_query(call_query, call_params)
            else:
                raise NotImplementedError(f"Calling stored procedures for {self.db_type} is not implemented")
        except ConnectionError as e:
            self.logger.error(f"Connection error calling procedure '{procedure_name}': {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error calling procedure '{procedure_name}': {str(e)}")
            raise QueryError(f"Error calling procedure '{procedure_name}': {str(e)}", query=f"CALL {procedure_name}", cause=e)

    def get_views(self) -> List[Dict[str, Any]]:
        """
        获取数据库中的所有视图

        Returns:
            List[Dict[str, Any]]: 视图列表，每个视图包含名称和定义等信息

        Raises:
            DatabaseError: 如果获取视图时发生错误
        """
        try:
            if self.db_type == 'mysql':
                query = """
                SELECT
                    table_name AS name,
                    view_definition AS definition,
                    check_option AS check_option,
                    is_updatable AS is_updatable
                FROM
                    information_schema.views
                WHERE
                    table_schema = DATABASE()
                ORDER BY
                    table_name
                """
            elif self.db_type == 'postgresql':
                query = """
                SELECT
                    table_name AS name,
                    view_definition AS definition,
                    check_option AS check_option,
                    is_updatable AS is_updatable
                FROM
                    information_schema.views
                WHERE
                    table_schema = 'public'
                ORDER BY
                    table_name
                """
            elif self.db_type == 'sqlite':
                query = """
                SELECT
                    name,
                    sql AS definition,
                    NULL AS check_option,
                    NULL AS is_updatable
                FROM
                    sqlite_master
                WHERE
                    type = 'view'
                ORDER BY
                    name
                """
            else:
                raise DatabaseError(f"Unsupported database type: {self.db_type}")

            result = self.execute_query(query)

            views = []
            for row in result:
                views.append({
                    'name': row[0],
                    'definition': row[1],
                    'check_option': row[2],
                    'is_updatable': row[3]
                })

            return views
        except Exception as e:
            self.logger.error(f"Error getting views: {str(e)}")
            raise DatabaseError(f"Error getting views: {str(e)}", cause=e)

    def get_triggers(self) -> List[Dict[str, Any]]:
        """
        获取数据库中的所有触发器

        Returns:
            List[Dict[str, Any]]: 触发器列表，每个触发器包含名称、表名、事件和定义等信息

        Raises:
            DatabaseError: 如果获取触发器时发生错误
            NotImplementedError: 如果数据库不支持触发器
        """
        if not self.features['triggers']:
            raise NotImplementedError(f"Database type {self.db_type} does not support triggers")

        try:
            if self.db_type == 'mysql':
                query = """
                SELECT
                    trigger_name AS name,
                    event_object_table AS table_name,
                    action_timing AS timing,
                    event_manipulation AS event,
                    action_statement AS definition
                FROM
                    information_schema.triggers
                WHERE
                    trigger_schema = DATABASE()
                ORDER BY
                    trigger_name
                """
            elif self.db_type == 'postgresql':
                query = """
                SELECT
                    trigger_name AS name,
                    event_object_table AS table_name,
                    action_timing AS timing,
                    event_manipulation AS event,
                    action_statement AS definition
                FROM
                    information_schema.triggers
                WHERE
                    trigger_schema = 'public'
                ORDER BY
                    trigger_name
                """
            elif self.db_type == 'sqlite':
                query = """
                SELECT
                    name,
                    tbl_name AS table_name,
                    NULL AS timing,
                    NULL AS event,
                    sql AS definition
                FROM
                    sqlite_master
                WHERE
                    type = 'trigger'
                ORDER BY
                    name
                """
            else:
                raise DatabaseError(f"Unsupported database type: {self.db_type}")

            result = self.execute_query(query)

            triggers = []
            for row in result:
                triggers.append({
                    'name': row[0],
                    'table_name': row[1],
                    'timing': row[2],
                    'event': row[3],
                    'definition': row[4]
                })

            return triggers
        except Exception as e:
            self.logger.error(f"Error getting triggers: {str(e)}")
            raise DatabaseError(f"Error getting triggers: {str(e)}", cause=e)
