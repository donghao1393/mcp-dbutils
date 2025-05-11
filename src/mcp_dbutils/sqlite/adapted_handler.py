"""
SQLite适配器实现

这个模块实现了SQLite的适配器，将ConnectionHandler接口适配到新架构的ConnectionBase和AdapterBase。
"""

import sqlite3
from typing import Any, Dict

import mcp.types as types

from ..adapter import AdaptedConnectionHandler, MULTI_DB_AVAILABLE
from ..base import ConnectionHandlerError
from .config import SQLiteConfig


class AdaptedSQLiteHandler(AdaptedConnectionHandler):
    """
    SQLite适配器实现

    这个类继承自AdaptedConnectionHandler，实现了SQLite特定的适配逻辑。
    """

    @property
    def db_type(self) -> str:
        """
        返回数据库类型

        Returns:
            str: 数据库类型
        """
        return 'sqlite'

    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置

        从配置文件加载SQLite配置，并转换为新架构的配置格式。

        Returns:
            Dict[str, Any]: 新架构的配置
        """
        config = SQLiteConfig.from_yaml(self.config_path, self.connection)
        return {
            'type': 'sqlite',
            'path': config.path,
            'debug': config.debug,
            'writable': config.writable,
            'write_permissions': config.write_permissions.to_dict() if config.write_permissions else None,
        }

    async def get_tables(self) -> list[types.Resource]:
        """
        获取表资源列表

        Returns:
            list[types.Resource]: 表资源列表

        Raises:
            ConnectionHandlerError: 如果获取表列表失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 使用新架构的连接执行查询
            result = connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in result]

            # 转换为Resource对象
            return [
                types.Resource(
                    uri=f"sqlite://{self.connection}/{table}/schema",
                    name=f"{table} schema",
                    description=None,
                    mimeType="application/json"
                ) for table in tables
            ]
        except Exception as e:
            self.log("error", f"Failed to get tables: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get tables: {str(e)}")

    async def get_schema(self, table_name: str) -> str:
        """
        获取表结构信息

        Args:
            table_name: 表名

        Returns:
            str: 表结构信息

        Raises:
            ConnectionHandlerError: 如果获取表结构失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 使用新架构的连接执行查询
            columns_result = connection.execute(f"PRAGMA table_info({table_name})")
            columns = columns_result.fetchall()

            indexes_result = connection.execute(f"PRAGMA index_list({table_name})")
            indexes = indexes_result.fetchall()

            # 转换为字典格式
            schema = {
                'columns': [{
                    'name': col[1],
                    'type': col[2],
                    'nullable': not col[3],
                    'default': col[4],
                    'primary_key': bool(col[5])
                } for col in columns],
                'indexes': [{
                    'name': idx[1],
                    'unique': bool(idx[2])
                } for idx in indexes]
            }

            return str(schema)
        except Exception as e:
            self.log("error", f"Failed to get schema for table {table_name}: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get schema for table {table_name}: {str(e)}")

    def _format_result(self, result: Any) -> str:
        """
        格式化结果

        将新架构的结果格式转换为ConnectionHandler的结果格式。

        Args:
            result: 新架构的结果

        Returns:
            str: 格式化后的结果
        """
        # 如果结果是游标，转换为字典列表
        if hasattr(result, 'description') and hasattr(result, 'fetchall'):
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()

            # 转换为字典列表
            result_dict = {
                'columns': columns,
                'rows': [dict(zip(columns, row)) for row in rows]
            }

            return str(result_dict)

        # 其他类型的结果直接转换为字符串
        return str(result)

    async def get_table_description(self, table_name: str) -> str:
        """
        获取表描述信息

        Args:
            table_name: 表名

        Returns:
            str: 表描述信息

        Raises:
            ConnectionHandlerError: 如果获取表描述失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 使用新架构的连接执行查询
            result = connection.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            row = result.fetchone()

            if not row:
                return f"Table {table_name} not found"

            return f"Table definition: {row[0]}"
        except Exception as e:
            self.log("error", f"Failed to get description for table {table_name}: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get description for table {table_name}: {str(e)}")

    async def get_table_ddl(self, table_name: str) -> str:
        """
        获取表DDL语句

        Args:
            table_name: 表名

        Returns:
            str: 表DDL语句

        Raises:
            ConnectionHandlerError: 如果获取表DDL失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 使用新架构的连接执行查询
            result = connection.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            row = result.fetchone()

            if not row:
                return f"Table {table_name} not found"

            return row[0]
        except Exception as e:
            self.log("error", f"Failed to get DDL for table {table_name}: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get DDL for table {table_name}: {str(e)}")

    async def get_table_indexes(self, table_name: str) -> str:
        """
        获取表索引信息

        Args:
            table_name: 表名

        Returns:
            str: 表索引信息

        Raises:
            ConnectionHandlerError: 如果获取表索引失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 使用新架构的连接执行查询
            result = connection.execute(f"PRAGMA index_list({table_name})")
            indexes = result.fetchall()

            # 获取每个索引的列信息
            index_info = []
            for idx in indexes:
                index_name = idx[1]
                is_unique = bool(idx[2])

                # 获取索引列
                columns_result = connection.execute(f"PRAGMA index_info({index_name})")
                columns = columns_result.fetchall()

                index_info.append({
                    'name': index_name,
                    'unique': is_unique,
                    'columns': [col[2] for col in columns]
                })

            return str(index_info)
        except Exception as e:
            self.log("error", f"Failed to get indexes for table {table_name}: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get indexes for table {table_name}: {str(e)}")

    async def get_table_stats(self, table_name: str) -> str:
        """
        获取表统计信息

        Args:
            table_name: 表名

        Returns:
            str: 表统计信息

        Raises:
            ConnectionHandlerError: 如果获取表统计失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 使用新架构的连接执行查询
            # SQLite没有内置的表统计信息，我们可以获取一些基本信息
            count_result = connection.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = count_result.fetchone()[0]

            # 获取表结构
            columns_result = connection.execute(f"PRAGMA table_info({table_name})")
            columns = columns_result.fetchall()

            stats = {
                'row_count': row_count,
                'column_count': len(columns),
                'columns': [col[1] for col in columns]
            }

            return str(stats)
        except Exception as e:
            self.log("error", f"Failed to get statistics for table {table_name}: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get statistics for table {table_name}: {str(e)}")

    async def get_table_constraints(self, table_name: str) -> str:
        """
        获取表约束信息

        Args:
            table_name: 表名

        Returns:
            str: 表约束信息

        Raises:
            ConnectionHandlerError: 如果获取表约束失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 使用新架构的连接执行查询
            # 获取主键信息
            pk_result = connection.execute(f"PRAGMA table_info({table_name})")
            pk_columns = [col[1] for col in pk_result.fetchall() if col[5]]

            # 获取外键信息
            fk_result = connection.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = []
            for fk in fk_result.fetchall():
                foreign_keys.append({
                    'id': fk[0],
                    'seq': fk[1],
                    'table': fk[2],
                    'from': fk[3],
                    'to': fk[4],
                    'on_update': fk[5],
                    'on_delete': fk[6],
                    'match': fk[7]
                })

            constraints = {
                'primary_key': pk_columns,
                'foreign_keys': foreign_keys
            }

            return str(constraints)
        except Exception as e:
            self.log("error", f"Failed to get constraints for table {table_name}: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get constraints for table {table_name}: {str(e)}")

    async def explain_query(self, sql: str) -> str:
        """
        获取查询执行计划

        Args:
            sql: SQL查询语句

        Returns:
            str: 查询执行计划

        Raises:
            ConnectionHandlerError: 如果获取查询执行计划失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 使用新架构的连接执行查询
            result = connection.execute(f"EXPLAIN QUERY PLAN {sql}")
            plan = result.fetchall()

            # 转换为字典列表
            columns = [desc[0] for desc in result.description]
            plan_dict = [dict(zip(columns, row)) for row in plan]

            return str(plan_dict)
        except Exception as e:
            self.log("error", f"Failed to explain query: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to explain query: {str(e)}")