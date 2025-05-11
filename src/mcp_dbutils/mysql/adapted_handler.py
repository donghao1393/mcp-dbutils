"""
MySQL适配器实现

这个模块实现了MySQL的适配器，将ConnectionHandler接口适配到新架构的ConnectionBase和AdapterBase。
"""

from typing import Any, Dict

import mcp.types as types
import mysql.connector

from ..adapter import MULTI_DB_AVAILABLE, AdaptedConnectionHandler
from ..base import ConnectionHandlerError
from .config import MySQLConfig


class AdaptedMySQLHandler(AdaptedConnectionHandler):
    """
    MySQL适配器实现

    这个类继承自AdaptedConnectionHandler，实现了MySQL特定的适配逻辑。
    """

    @property
    def db_type(self) -> str:
        """
        返回数据库类型

        Returns:
            str: 数据库类型
        """
        return 'mysql'

    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置

        从配置文件加载MySQL配置，并转换为新架构的配置格式。

        Returns:
            Dict[str, Any]: 新架构的配置
        """
        config = MySQLConfig.from_yaml(self.config_path, self.connection)
        return {
            'type': 'mysql',
            'host': config.host,
            'port': int(config.port),
            'database': config.database,
            'user': config.user,
            'password': config.password,
            'charset': config.charset,
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
            result = connection.execute("""
                SELECT
                    TABLE_NAME as table_name,
                    TABLE_COMMENT as description
                FROM information_schema.tables
                WHERE TABLE_SCHEMA = %s
            """, (connection.config.database,))

            tables = result.fetchall()

            # 转换为Resource对象
            return [
                types.Resource(
                    uri=f"mysql://{self.connection}/{table[0]}/schema",
                    name=f"{table[0]} schema",
                    description=table[1] if table[1] else None,
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
            columns_result = connection.execute("""
                SELECT
                    COLUMN_NAME as column_name,
                    DATA_TYPE as data_type,
                    IS_NULLABLE as is_nullable,
                    COLUMN_COMMENT as description
                FROM information_schema.columns
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """, (connection.config.database, table_name))

            columns = columns_result.fetchall()

            # 获取约束信息
            constraints_result = connection.execute("""
                SELECT
                    CONSTRAINT_NAME as constraint_name,
                    CONSTRAINT_TYPE as constraint_type
                FROM information_schema.table_constraints
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """, (connection.config.database, table_name))

            constraints = constraints_result.fetchall()

            # 转换为字典格式
            schema = {
                'columns': [{
                    'name': col[0],
                    'type': col[1],
                    'nullable': col[2] == 'YES',
                    'description': col[3]
                } for col in columns],
                'constraints': [{
                    'name': con[0],
                    'type': con[1]
                } for con in constraints]
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
        connection, _ = self._ensure_connection()
        try:
            # 获取表信息和注释
            table_info_result = connection.execute("""
                SELECT
                    TABLE_COMMENT as table_comment
                FROM information_schema.tables
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """, (connection.config.database, table_name))

            table_info = table_info_result.fetchone()
            table_comment = table_info[0] if table_info else None

            # 获取列信息
            columns_result = connection.execute("""
                SELECT
                    COLUMN_NAME as column_name,
                    DATA_TYPE as data_type,
                    COLUMN_DEFAULT as column_default,
                    IS_NULLABLE as is_nullable,
                    CHARACTER_MAXIMUM_LENGTH as character_maximum_length,
                    NUMERIC_PRECISION as numeric_precision,
                    NUMERIC_SCALE as numeric_scale,
                    COLUMN_COMMENT as column_comment
                FROM information_schema.columns
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """, (connection.config.database, table_name))

            columns = columns_result.fetchall()

            # 格式化输出
            description = [
                f"Table: {table_name}",
                f"Comment: {table_comment or 'No comment'}\n",
                "Columns:"
            ]

            for col in columns:
                col_info = [
                    f"  {col[0]} ({col[1]})",
                    f"    Nullable: {col[2]}",
                    f"    Default: {col[3] or 'None'}"
                ]

                if col[4]:
                    col_info.append(f"    Max Length: {col[4]}")
                if col[5]:
                    col_info.append(f"    Precision: {col[5]}")
                if col[6]:
                    col_info.append(f"    Scale: {col[6]}")
                if col[7]:
                    col_info.append(f"    Comment: {col[7]}")

                description.extend(col_info)
                description.append("")  # 空行分隔列

            return "\n".join(description)
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
        connection, _ = self._ensure_connection()
        try:
            # MySQL提供了SHOW CREATE TABLE语句
            result = connection.execute(f"SHOW CREATE TABLE {table_name}")
            row = result.fetchone()
            if row:
                return row[1]  # 'Create Table'列
            return f"Failed to get DDL for table {table_name}"
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
        connection, _ = self._ensure_connection()
        try:
            # 获取索引信息
            result = connection.execute("""
                SELECT
                    INDEX_NAME as index_name,
                    COLUMN_NAME as column_name,
                    NON_UNIQUE as non_unique,
                    INDEX_TYPE as index_type,
                    INDEX_COMMENT as index_comment
                FROM information_schema.statistics
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY INDEX_NAME, SEQ_IN_INDEX
            """, (connection.config.database, table_name))

            indexes = result.fetchall()

            if not indexes:
                return f"No indexes found on table {table_name}"

            # 按索引名称分组
            current_index = None
            formatted_indexes = []
            index_info = []

            for idx in indexes:
                if current_index != idx[0]:  # index_name
                    if index_info:
                        formatted_indexes.extend(index_info)
                        formatted_indexes.append("")
                    current_index = idx[0]
                    index_info = [
                        f"Index: {idx[0]}",
                        f"Type: {'UNIQUE' if not idx[2] else 'INDEX'}",  # non_unique
                        f"Method: {idx[3]}",  # index_type
                        "Columns:",
                    ]
                    if idx[4]:  # index_comment
                        index_info.insert(1, f"Comment: {idx[4]}")

                index_info.append(f"  - {idx[1]}")  # column_name

            if index_info:
                formatted_indexes.extend(index_info)

            return "\n".join(formatted_indexes)
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
        connection, _ = self._ensure_connection()
        try:
            # 获取表统计信息
            stats_result = connection.execute("""
                SELECT
                    TABLE_ROWS as table_rows,
                    AVG_ROW_LENGTH as avg_row_length,
                    DATA_LENGTH as data_length,
                    INDEX_LENGTH as index_length,
                    DATA_FREE as data_free
                FROM information_schema.tables
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """, (connection.config.database, table_name))

            stats = stats_result.fetchone()

            if not stats:
                return f"No statistics found for table {table_name}"

            # 获取列统计信息
            columns_result = connection.execute("""
                SELECT
                    COLUMN_NAME as column_name,
                    DATA_TYPE as data_type,
                    COLUMN_TYPE as column_type
                FROM information_schema.columns
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """, (connection.config.database, table_name))

            columns = columns_result.fetchall()

            # 格式化输出
            output = [
                f"Table Statistics for {table_name}:",
                f"  Estimated Row Count: {stats[0]:,}",
                f"  Average Row Length: {stats[1]} bytes",
                f"  Data Length: {stats[2]:,} bytes",
                f"  Index Length: {stats[3]:,} bytes",
                f"  Data Free: {stats[4]:,} bytes\n",
                "Column Information:"
            ]

            for col in columns:
                col_info = [
                    f"  {col[0]}:",
                    f"    Data Type: {col[1]}",
                    f"    Column Type: {col[2]}"
                ]
                output.extend(col_info)
                output.append("")  # 空行分隔列

            return "\n".join(output)
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
        connection, _ = self._ensure_connection()
        try:
            # 获取约束信息
            result = connection.execute("""
                SELECT
                    k.CONSTRAINT_NAME as constraint_name,
                    t.CONSTRAINT_TYPE as constraint_type,
                    k.COLUMN_NAME as column_name,
                    k.REFERENCED_TABLE_NAME as referenced_table_name,
                    k.REFERENCED_COLUMN_NAME as referenced_column_name
                FROM information_schema.key_column_usage k
                JOIN information_schema.table_constraints t
                    ON k.CONSTRAINT_NAME = t.CONSTRAINT_NAME
                    AND k.TABLE_SCHEMA = t.TABLE_SCHEMA
                    AND k.TABLE_NAME = t.TABLE_NAME
                WHERE k.TABLE_SCHEMA = %s
                    AND k.TABLE_NAME = %s
                ORDER BY t.CONSTRAINT_TYPE, k.CONSTRAINT_NAME, k.ORDINAL_POSITION
            """, (connection.config.database, table_name))

            constraints = result.fetchall()

            if not constraints:
                return f"No constraints found on table {table_name}"

            # 按约束类型和名称分组
            output = [f"Constraints for {table_name}:"]
            current_constraint = None
            constraint_info = []

            for con in constraints:
                if current_constraint != con[0]:  # constraint_name
                    if constraint_info:
                        output.extend(constraint_info)
                        output.append("")
                    current_constraint = con[0]
                    constraint_info = [
                        f"\n{con[1]} Constraint: {con[0]}",  # constraint_type, constraint_name
                        "Columns:"
                    ]

                col_info = f"  - {con[2]}"  # column_name
                if con[3]:  # referenced_table_name
                    col_info += f" -> {con[3]}.{con[4]}"  # referenced_column_name
                constraint_info.append(col_info)

            if constraint_info:
                output.extend(constraint_info)

            return "\n".join(output)
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
        connection, _ = self._ensure_connection()
        try:
            # 获取EXPLAIN输出
            explain_result = connection.execute(f"EXPLAIN FORMAT=TREE {sql}")
            explain_rows = explain_result.fetchall()

            # 获取EXPLAIN ANALYZE输出
            analyze_result = connection.execute(f"EXPLAIN ANALYZE {sql}")
            analyze_rows = analyze_result.fetchall()

            output = [
                "Query Execution Plan:",
                "==================",
                "\nEstimated Plan:",
                "----------------"
            ]
            for row in explain_rows:
                output.append(str(row[0]))  # EXPLAIN列

            output.extend([
                "\nActual Plan (ANALYZE):",
                "----------------------"
            ])
            for row in analyze_rows:
                output.append(str(row[0]))  # EXPLAIN列

            return "\n".join(output)
        except Exception as e:
            self.log("error", f"Failed to explain query: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to explain query: {str(e)}")

    async def test_connection(self) -> bool:
        """
        测试数据库连接

        Returns:
            bool: 如果连接成功，则返回True，否则返回False
        """
        try:
            # 只需要确保连接可以建立，不需要使用连接对象
            self._ensure_connection()
            return True
        except Exception as e:
            self.log("error", f"Connection test failed: {str(e)}")
            return False

    async def cleanup(self):
        """
        清理资源

        关闭连接并清理资源。
        """
        # 记录最终统计信息
        self.log("info", f"Final handler stats: {self.stats.to_dict()}")

        # 关闭连接
        if self._connection and self._connection.is_connected():
            try:
                self.log("debug", f"Closing {self.db_type} connection")
                self._connection.disconnect()
                self._connection = None
                self._adapter = None
            except Exception as e:
                self.log("warning", f"Error closing {self.db_type} connection: {str(e)}")

        # 清理其他资源
        self.log("debug", f"{self.db_type} handler cleanup complete")
