"""
PostgreSQL适配器实现

这个模块实现了PostgreSQL的适配器，将ConnectionHandler接口适配到新架构的ConnectionBase和AdapterBase。
"""

from typing import Any, Dict

import mcp.types as types
import psycopg2

from ..adapter import MULTI_DB_AVAILABLE, AdaptedConnectionHandler
from ..base import ConnectionHandlerError
from .config import PostgreSQLConfig


class AdaptedPostgreSQLHandler(AdaptedConnectionHandler):
    """
    PostgreSQL适配器实现

    这个类继承自AdaptedConnectionHandler，实现了PostgreSQL特定的适配逻辑。
    """

    @property
    def db_type(self) -> str:
        """
        返回数据库类型

        Returns:
            str: 数据库类型
        """
        return 'postgres'

    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置

        从配置文件加载PostgreSQL配置，并转换为新架构的配置格式。

        Returns:
            Dict[str, Any]: 新架构的配置
        """
        config = PostgreSQLConfig.from_yaml(self.config_path, self.connection)
        return {
            'type': 'postgres',
            'host': config.host,
            'port': int(config.port),
            'database': config.dbname,
            'user': config.user,
            'password': config.password,
            'ssl': config.ssl.mode if config.ssl else None,
            'ssl_cert': config.ssl.cert if config.ssl else None,
            'ssl_key': config.ssl.key if config.ssl else None,
            'ssl_root': config.ssl.root if config.ssl else None,
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
        connection, _ = self._ensure_connection()
        try:
            # 使用新架构的连接执行查询
            result = connection.execute("""
                SELECT
                    table_name,
                    obj_description(
                        (quote_ident(table_schema) || '.' || quote_ident(table_name))::regclass,
                        'pg_class'
                    ) as description
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)

            tables = result.fetchall()

            # 转换为Resource对象
            return [
                types.Resource(
                    uri=f"postgres://{self.connection}/{table[0]}/schema",
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
        connection, _ = self._ensure_connection()
        try:
            # 获取列信息
            columns_result = connection.execute("""
                SELECT
                    column_name,
                    data_type,
                    is_nullable,
                    col_description(
                        (quote_ident(table_schema) || '.' || quote_ident(table_name))::regclass,
                        ordinal_position
                    ) as description
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))

            columns = columns_result.fetchall()

            # 获取约束信息
            constraints_result = connection.execute("""
                SELECT
                    conname as constraint_name,
                    contype as constraint_type
                FROM pg_constraint c
                JOIN pg_class t ON c.conrelid = t.oid
                WHERE t.relname = %s
            """, (table_name,))

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
            # 获取表的基本信息和注释
            table_info_result = connection.execute("""
                SELECT obj_description(
                    (quote_ident(table_schema) || '.' || quote_ident(table_name))::regclass,
                    'pg_class'
                ) as table_comment
                FROM information_schema.tables
                WHERE table_name = %s
            """, (table_name,))

            table_info = table_info_result.fetchone()
            table_comment = table_info[0] if table_info else None

            # 获取列信息
            columns_result = connection.execute("""
                SELECT
                    column_name,
                    data_type,
                    column_default,
                    is_nullable,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale,
                    col_description(
                        (quote_ident(table_schema) || '.' || quote_ident(table_name))::regclass,
                        ordinal_position
                    ) as column_comment
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))

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
                    f"    Nullable: {col[3]}",
                    f"    Default: {col[2] or 'None'}"
                ]

                if col[4]:  # character_maximum_length
                    col_info.append(f"    Max Length: {col[4]}")
                if col[5]:  # numeric_precision
                    col_info.append(f"    Precision: {col[5]}")
                if col[6]:  # numeric_scale
                    col_info.append(f"    Scale: {col[6]}")
                if col[7]:  # column_comment
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
            # 获取列定义
            columns_result = connection.execute("""
                SELECT
                    column_name,
                    data_type,
                    column_default,
                    is_nullable,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))

            columns = columns_result.fetchall()

            # 获取约束
            constraints_result = connection.execute("""
                SELECT
                    conname as constraint_name,
                    pg_get_constraintdef(c.oid) as constraint_def
                FROM pg_constraint c
                JOIN pg_class t ON c.conrelid = t.oid
                WHERE t.relname = %s
            """, (table_name,))

            constraints = constraints_result.fetchall()

            # 构建CREATE TABLE语句
            ddl = [f"CREATE TABLE {table_name} ("]

            # 添加列定义
            column_defs = []
            for col in columns:
                col_def = [f"    {col[0]} {col[1]}"]

                if col[4]:  # character_maximum_length
                    col_def[0] = f"{col_def[0]}({col[4]})"
                elif col[5]:  # numeric_precision
                    if col[6]:  # numeric_scale
                        col_def[0] = f"{col_def[0]}({col[5]},{col[6]})"
                    else:
                        col_def[0] = f"{col_def[0]}({col[5]})"

                if col[2]:  # default
                    col_def.append(f"DEFAULT {col[2]}")
                if col[3] == 'NO':  # not null
                    col_def.append("NOT NULL")

                column_defs.append(" ".join(col_def))

            # 添加约束定义
            for con in constraints:
                column_defs.append(f"    CONSTRAINT {con[0]} {con[1]}")

            ddl.append(",\n".join(column_defs))
            ddl.append(");")

            # 添加注释
            comments_result = connection.execute("""
                SELECT
                    c.column_name,
                    col_description(
                        (quote_ident(table_schema) || '.' || quote_ident(table_name))::regclass,
                        c.ordinal_position
                    ) as column_comment,
                    obj_description(
                        (quote_ident(table_schema) || '.' || quote_ident(table_name))::regclass,
                        'pg_class'
                    ) as table_comment
                FROM information_schema.columns c
                WHERE c.table_name = %s
            """, (table_name,))

            comments = comments_result.fetchall()

            for comment in comments:
                if comment[2]:  # table comment
                    ddl.append(f"\nCOMMENT ON TABLE {table_name} IS '{comment[2]}';")
                if comment[1]:  # column comment
                    ddl.append(f"COMMENT ON COLUMN {table_name}.{comment[0]} IS '{comment[1]}';")

            return "\n".join(ddl)
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
                    i.relname as index_name,
                    a.attname as column_name,
                    CASE
                        WHEN ix.indisprimary THEN 'PRIMARY KEY'
                        WHEN ix.indisunique THEN 'UNIQUE'
                        ELSE 'INDEX'
                    END as index_type,
                    am.amname as index_method,
                    pg_get_indexdef(ix.indexrelid) as index_def,
                    obj_description(i.oid, 'pg_class') as index_comment
                FROM pg_class t
                JOIN pg_index ix ON t.oid = ix.indrelid
                JOIN pg_class i ON ix.indexrelid = i.oid
                JOIN pg_am am ON i.relam = am.oid
                JOIN pg_attribute a ON t.oid = a.attrelid
                WHERE t.relname = %s
                AND a.attnum = ANY(ix.indkey)
                ORDER BY i.relname, a.attnum
            """, (table_name,))

            indexes = result.fetchall()

            if not indexes:
                return f"No indexes found on table {table_name}"

            # 按索引名称分组
            current_index = None
            formatted_indexes = []
            index_info = []

            for idx in indexes:
                if current_index != idx[0]:
                    if index_info:
                        formatted_indexes.extend(index_info)
                        formatted_indexes.append("")
                    current_index = idx[0]
                    index_info = [
                        f"Index: {idx[0]}",
                        f"Type: {idx[2]}",
                        f"Method: {idx[3]}",
                        "Columns:",
                    ]
                    if idx[5]:  # index comment
                        index_info.insert(1, f"Comment: {idx[5]}")

                index_info.append(f"  - {idx[1]}")

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
                    c.reltuples::bigint as row_estimate,
                    pg_size_pretty(pg_total_relation_size(c.oid)) as total_size,
                    pg_size_pretty(pg_table_size(c.oid)) as table_size,
                    pg_size_pretty(pg_indexes_size(c.oid)) as index_size,
                    age(c.relfrozenxid) as xid_age,
                    c.relhasindex as has_indexes,
                    c.relpages::bigint as pages,
                    c.relallvisible::bigint as visible_pages
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relname = %s AND n.nspname = 'public'
            """, (table_name,))

            stats = stats_result.fetchone()

            if not stats:
                return f"No statistics found for table {table_name}"

            # 获取列统计信息
            column_stats_result = connection.execute("""
                SELECT
                    a.attname as column_name,
                    s.null_frac * 100 as null_percent,
                    s.n_distinct as distinct_values,
                    pg_column_size(a.attname::text) as approx_width
                FROM pg_stats s
                JOIN pg_attribute a ON a.attrelid = %s::regclass
                    AND a.attnum > 0
                    AND a.attname = s.attname
                WHERE s.schemaname = 'public'
                AND s.tablename = %s
                ORDER BY a.attnum;
            """, (table_name, table_name))

            column_stats = column_stats_result.fetchall()

            # 格式化输出
            output = [
                f"Table Statistics for {table_name}:",
                f"  Estimated Row Count: {stats[0]:,}",
                f"  Total Size: {stats[1]}",
                f"  Table Size: {stats[2]}",
                f"  Index Size: {stats[3]}",
                f"  Transaction ID Age: {stats[4]:,}",
                f"  Has Indexes: {stats[5]}",
                f"  Total Pages: {stats[6]:,}",
                f"  Visible Pages: {stats[7]:,}\n",
                "Column Statistics:"
            ]

            for col in column_stats:
                col_info = [
                    f"  {col[0]}:",
                    f"    Null Values: {col[1]:.1f}%",
                    f"    Distinct Values: {col[2] if col[2] >= 0 else 'Unknown'}",
                    f"    Average Width: {col[3]}"
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
            # 获取所有约束
            result = connection.execute("""
                SELECT
                    con.conname as constraint_name,
                    con.contype as constraint_type,
                    pg_get_constraintdef(con.oid) as definition,
                    CASE con.contype
                        WHEN 'p' THEN 'Primary Key'
                        WHEN 'f' THEN 'Foreign Key'
                        WHEN 'u' THEN 'Unique'
                        WHEN 'c' THEN 'Check'
                        WHEN 't' THEN 'Trigger'
                        ELSE 'Unknown'
                    END as type_desc,
                    con.condeferrable as is_deferrable,
                    con.condeferred as is_deferred,
                    obj_description(con.oid, 'pg_constraint') as comment
                FROM pg_constraint con
                JOIN pg_class rel ON rel.oid = con.conrelid
                JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
                WHERE rel.relname = %s
                ORDER BY con.contype, con.conname
            """, (table_name,))

            constraints = result.fetchall()

            if not constraints:
                return f"No constraints found on table {table_name}"

            # 按约束类型分组
            output = [f"Constraints for {table_name}:"]
            current_type = None

            for con in constraints:
                if current_type != con[3]:
                    current_type = con[3]
                    output.append(f"\n{current_type} Constraints:")

                output.extend([
                    f"  {con[0]}:",
                    f"    Definition: {con[2]}"
                ])

                if con[4]:  # is_deferrable
                    output.append(f"    Deferrable: {'Deferred' if con[5] else 'Immediate'}")

                if con[6]:  # comment
                    output.append(f"    Comment: {con[6]}")

                output.append("")  # 空行分隔约束

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
            # 获取EXPLAIN输出（不执行）
            regular_plan_result = connection.execute("""
                EXPLAIN (FORMAT TEXT, VERBOSE, COSTS)
                {}
            """.format(sql))
            regular_plan = regular_plan_result.fetchall()

            # 获取EXPLAIN ANALYZE输出（实际执行）
            analyze_plan_result = connection.execute("""
                EXPLAIN (ANALYZE, FORMAT TEXT, VERBOSE, COSTS, TIMING)
                {}
            """.format(sql))
            analyze_plan = analyze_plan_result.fetchall()

            output = [
                "Query Execution Plan:",
                "==================",
                "\nEstimated Plan:",
                "----------------"
            ]
            output.extend(line[0] for line in regular_plan)

            output.extend([
                "\nActual Plan (ANALYZE):",
                "----------------------"
            ])
            output.extend(line[0] for line in analyze_plan)

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
        if self._connection and hasattr(self._connection, 'is_connected') and self._connection.is_connected():
            try:
                self.log("debug", f"Closing {self.db_type} connection")
                self._connection.disconnect()
                self._connection = None
                self._adapter = None
            except Exception as e:
                self.log("warning", f"Error closing {self.db_type} connection: {str(e)}")

        # 清理其他资源
        self.log("debug", f"{self.db_type} handler cleanup complete")
