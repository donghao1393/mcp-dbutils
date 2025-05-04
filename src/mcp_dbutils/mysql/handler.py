"""MySQL connection handler implementation"""

import mcp.types as types
import mysql.connector

from ..base import ConnectionHandler, ConnectionHandlerError
from .config import MySQLConfig

# 常量定义
COLUMNS_HEADER = "Columns:"


class MySQLHandler(ConnectionHandler):
    @property
    def db_type(self) -> str:
        return 'mysql'

    def __init__(self, config_path: str, connection: str, debug: bool = False):
        """Initialize MySQL handler

        Args:
            config_path: Path to configuration file
            connection: Database connection name
            debug: Enable debug mode
        """
        super().__init__(config_path, connection, debug)
        self.config = MySQLConfig.from_yaml(config_path, connection)

        # No connection pool creation during initialization
        masked_params = self.config.get_masked_connection_info()
        self.log("debug", f"Configuring connection with parameters: {masked_params}")
        self.pool = None

    async def _check_table_exists(self, cursor, table_name: str) -> None:
        """检查表是否存在

        Args:
            cursor: 数据库游标
            table_name: 表名

        Raises:
            ConnectionHandlerError: 如果表不存在
        """
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM information_schema.tables
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """, (self.config.database, table_name))
        table_exists = cursor.fetchone()

        # Handle different formats of cursor results (dict or tuple)
        if not table_exists:
            raise ConnectionHandlerError(f"Table '{self.config.database}.{table_name}' doesn't exist")

        # If fetchone returns a dictionary (dictionary=True was used)
        if isinstance(table_exists, dict) and 'count' in table_exists and table_exists['count'] == 0:
            raise ConnectionHandlerError(f"Table '{self.config.database}.{table_name}' doesn't exist")

        # If fetchone returns a tuple
        if isinstance(table_exists, tuple) and table_exists[0] == 0:
            raise ConnectionHandlerError(f"Table '{self.config.database}.{table_name}' doesn't exist")

    async def get_tables(self) -> list[types.Resource]:
        """Get all table resources"""
        conn = None
        try:
            conn_params = self.config.get_connection_params()
            conn = mysql.connector.connect(**conn_params)
            with conn.cursor(dictionary=True) as cur:  # NOSONAR
                cur.execute("""
                    SELECT
                        TABLE_NAME as table_name,
                        TABLE_COMMENT as description
                    FROM information_schema.tables
                    WHERE TABLE_SCHEMA = %s
                """, (self.config.database,))
                tables = cur.fetchall()
                return [
                    types.Resource(
                        uri=f"mysql://{self.connection}/{table['table_name']}/schema",
                        name=f"{table['table_name']} schema",
                        description=table['description'] if table['description'] else None,
                        mimeType="application/json"
                    ) for table in tables
                ]
        except mysql.connector.Error as e:
            error_msg = f"Failed to get tables: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def get_schema(self, table_name: str) -> str:
        """Get table schema information"""
        conn = None
        try:
            conn_params = self.config.get_connection_params()
            conn = mysql.connector.connect(**conn_params)
            with conn.cursor(dictionary=True) as cur:  # NOSONAR
                # Get column information
                cur.execute("""
                    SELECT
                        COLUMN_NAME as column_name,
                        DATA_TYPE as data_type,
                        IS_NULLABLE as is_nullable,
                        COLUMN_COMMENT as description
                    FROM information_schema.columns
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                    ORDER BY ORDINAL_POSITION
                """, (self.config.database, table_name))
                columns = cur.fetchall()

                # Get constraint information
                cur.execute("""
                    SELECT
                        CONSTRAINT_NAME as constraint_name,
                        CONSTRAINT_TYPE as constraint_type
                    FROM information_schema.table_constraints
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                """, (self.config.database, table_name))
                constraints = cur.fetchall()

                return str({
                    'columns': [{
                        'name': col['column_name'],
                        'type': col['data_type'],
                        'nullable': col['is_nullable'] == 'YES',
                        'description': col['description']
                    } for col in columns],
                    'constraints': [{
                        'name': con['constraint_name'],
                        'type': con['constraint_type']
                    } for con in constraints]
                })
        except mysql.connector.Error as e:
            error_msg = f"Failed to read table schema: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def _execute_query(self, sql: str) -> str:
        """Execute SQL query"""
        conn = None
        try:
            conn_params = self.config.get_connection_params()
            conn = mysql.connector.connect(**conn_params)
            self.log("debug", f"Executing query: {sql}")

            with conn.cursor(dictionary=True) as cur:  # NOSONAR
                # Check if the query is a SELECT statement
                sql_upper = sql.strip().upper()
                is_select = sql_upper.startswith("SELECT")

                # Only set read-only transaction for SELECT statements
                if is_select:
                    cur.execute("SET TRANSACTION READ ONLY")
                try:
                    cur.execute(sql)
                    if not is_select:
                        conn.commit()
                    results = cur.fetchall() if is_select else []
                    if cur.description is None:  # DDL statements
                        return "Query executed successfully"
                    columns = [desc[0] for desc in cur.description]
                    return str({
                        "columns": columns,
                        "rows": results
                    })
                except mysql.connector.Error as e:
                    self.log("error", f"Query error: {str(e)}")
                    raise ConnectionHandlerError(str(e))
                finally:
                    cur.close()
        except mysql.connector.Error as e:
            error_msg = f"[{self.db_type}] Query execution failed: {str(e)}"
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def _execute_write_query(self, sql: str) -> str:
        """Execute SQL write query

        Args:
            sql: SQL write query (INSERT, UPDATE, DELETE)

        Returns:
            str: Execution result

        Raises:
            ConnectionHandlerError: If query execution fails
        """
        conn = None
        try:
            # Check if the query is a write operation
            sql_upper = sql.strip().upper()
            is_insert = sql_upper.startswith("INSERT")
            is_update = sql_upper.startswith("UPDATE")
            is_delete = sql_upper.startswith("DELETE")
            is_transaction = sql_upper.startswith(("BEGIN", "COMMIT", "ROLLBACK", "START TRANSACTION"))

            if not (is_insert or is_update or is_delete or is_transaction):
                raise ConnectionHandlerError("Only INSERT, UPDATE, DELETE, and transaction statements are allowed for write operations")

            conn_params = self.config.get_connection_params()
            conn = mysql.connector.connect(**conn_params)
            self.log("debug", f"Executing write operation: {sql}")

            with conn.cursor() as cur:
                try:
                    # Execute the write operation
                    cur.execute(sql)

                    # Get number of affected rows
                    affected_rows = cur.rowcount

                    # Commit the transaction if not in a transaction block
                    if not is_transaction:
                        conn.commit()

                    self.log("debug", f"Write operation executed successfully, affected {affected_rows} rows")

                    # Return result
                    if is_transaction:
                        return f"Transaction operation executed successfully"
                    else:
                        return f"Write operation executed successfully. {affected_rows} row{'s' if affected_rows != 1 else ''} affected."
                except mysql.connector.Error as e:
                    # Rollback on error
                    if not is_transaction:
                        conn.rollback()
                    self.log("error", f"Write operation error: {str(e)}")
                    raise ConnectionHandlerError(str(e))
        except mysql.connector.Error as e:
            error_msg = f"[{self.db_type}] Write operation failed: {str(e)}"
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def get_table_description(self, table_name: str) -> str:
        """Get detailed table description"""
        conn = None
        try:
            conn_params = self.config.get_connection_params()
            conn = mysql.connector.connect(**conn_params)
            with conn.cursor(dictionary=True) as cur:  # NOSONAR
                # Check if table exists
                await self._check_table_exists(cur, table_name)

                # Get table information and comment
                cur.execute("""
                    SELECT
                        TABLE_COMMENT as table_comment
                    FROM information_schema.tables
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                """, (self.config.database, table_name))
                table_info = cur.fetchone()
                table_comment = table_info['table_comment'] if table_info else None

                # Get column information
                cur.execute("""
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
                """, (self.config.database, table_name))
                columns = cur.fetchall()

                # Format output
                description = [
                    f"Table: {table_name}",
                    f"Comment: {table_comment or 'No comment'}\n",
                    COLUMNS_HEADER
                ]

                for col in columns:
                    col_info = [
                        f"  {col['column_name']} ({col['data_type']})",
                        f"    Nullable: {col['is_nullable']}",
                        f"    Default: {col['column_default'] or 'None'}"
                    ]

                    if col['character_maximum_length']:
                        col_info.append(f"    Max Length: {col['character_maximum_length']}")
                    if col['numeric_precision']:
                        col_info.append(f"    Precision: {col['numeric_precision']}")
                    if col['numeric_scale']:
                        col_info.append(f"    Scale: {col['numeric_scale']}")
                    if col['column_comment']:
                        col_info.append(f"    Comment: {col['column_comment']}")

                    description.extend(col_info)
                    description.append("")  # Empty line between columns

                return "\n".join(description)

        except mysql.connector.Error as e:
            error_msg = f"Failed to get table description: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def get_table_ddl(self, table_name: str) -> str:
        """Get DDL statement for creating table"""
        conn = None
        try:
            conn_params = self.config.get_connection_params()
            conn = mysql.connector.connect(**conn_params)
            with conn.cursor(dictionary=True) as cur:  # NOSONAR
                # MySQL provides a SHOW CREATE TABLE statement
                cur.execute(f"SHOW CREATE TABLE {table_name}")
                result = cur.fetchone()
                if result:
                    return result['Create Table']
                return f"Failed to get DDL for table {table_name}"

        except mysql.connector.Error as e:
            error_msg = f"Failed to get table DDL: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def get_table_indexes(self, table_name: str) -> str:
        """Get index information for table"""
        conn = None
        try:
            conn_params = self.config.get_connection_params()
            conn = mysql.connector.connect(**conn_params)
            with conn.cursor(dictionary=True) as cur:  # NOSONAR
                # Check if table exists
                await self._check_table_exists(cur, table_name)

                # Get index information
                cur.execute("""
                    SELECT
                        INDEX_NAME as index_name,
                        COLUMN_NAME as column_name,
                        NON_UNIQUE as non_unique,
                        INDEX_TYPE as index_type,
                        INDEX_COMMENT as index_comment
                    FROM information_schema.statistics
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                    ORDER BY INDEX_NAME, SEQ_IN_INDEX
                """, (self.config.database, table_name))
                indexes = cur.fetchall()

                if not indexes:
                    return f"No indexes found on table {table_name}"

                # Group by index name
                current_index = None
                formatted_indexes = []
                index_info = []

                for idx in indexes:
                    if current_index != idx['index_name']:
                        if index_info:
                            formatted_indexes.extend(index_info)
                            formatted_indexes.append("")
                        current_index = idx['index_name']
                        index_info = [
                            f"Index: {idx['index_name']}",
                            f"Type: {'UNIQUE' if not idx['non_unique'] else 'INDEX'}",
                            f"Method: {idx['index_type']}",
                            COLUMNS_HEADER,
                        ]
                        if idx['index_comment']:
                            index_info.insert(1, f"Comment: {idx['index_comment']}")

                    index_info.append(f"  - {idx['column_name']}")

                if index_info:
                    formatted_indexes.extend(index_info)

                return "\n".join(formatted_indexes)

        except mysql.connector.Error as e:
            error_msg = f"Failed to get index information: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def get_table_stats(self, table_name: str) -> str:
        """Get table statistics information"""
        conn = None
        try:
            conn_params = self.config.get_connection_params()
            conn = mysql.connector.connect(**conn_params)
            with conn.cursor(dictionary=True) as cur:  # NOSONAR
                # Check if table exists
                await self._check_table_exists(cur, table_name)

                # Get table statistics
                cur.execute("""
                    SELECT
                        TABLE_ROWS as table_rows,
                        AVG_ROW_LENGTH as avg_row_length,
                        DATA_LENGTH as data_length,
                        INDEX_LENGTH as index_length,
                        DATA_FREE as data_free
                    FROM information_schema.tables
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                """, (self.config.database, table_name))
                stats = cur.fetchone()

                if not stats:
                    return f"No statistics found for table {table_name}"

                # Get column statistics
                cur.execute("""
                    SELECT
                        COLUMN_NAME as column_name,
                        DATA_TYPE as data_type,
                        COLUMN_TYPE as column_type
                    FROM information_schema.columns
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                    ORDER BY ORDINAL_POSITION
                """, (self.config.database, table_name))
                columns = cur.fetchall()

                # Format the output
                output = [
                    f"Table Statistics for {table_name}:",
                    f"  Estimated Row Count: {stats['table_rows']:,}",
                    f"  Average Row Length: {stats['avg_row_length']} bytes",
                    f"  Data Length: {stats['data_length']:,} bytes",
                    f"  Index Length: {stats['index_length']:,} bytes",
                    f"  Data Free: {stats['data_free']:,} bytes\n",
                    "Column Information:"
                ]

                for col in columns:
                    col_info = [
                        f"  {col['column_name']}:",
                        f"    Data Type: {col['data_type']}",
                        f"    Column Type: {col['column_type']}"
                    ]
                    output.extend(col_info)
                    output.append("")  # Empty line between columns

                return "\n".join(output)

        except mysql.connector.Error as e:
            error_msg = f"Failed to get table statistics: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def get_table_constraints(self, table_name: str) -> str:
        """Get constraint information for table"""
        conn = None
        try:
            conn_params = self.config.get_connection_params()
            conn = mysql.connector.connect(**conn_params)
            with conn.cursor(dictionary=True) as cur:  # NOSONAR
                # Check if table exists
                await self._check_table_exists(cur, table_name)

                # Get constraint information
                cur.execute("""
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
                """, (self.config.database, table_name))
                constraints = cur.fetchall()

                if not constraints:
                    return f"No constraints found on table {table_name}"

                # Format constraints by type
                output = [f"Constraints for {table_name}:"]
                current_constraint = None
                constraint_info = []

                for con in constraints:
                    if current_constraint != con['constraint_name']:
                        if constraint_info:
                            output.extend(constraint_info)
                            output.append("")
                        current_constraint = con['constraint_name']
                        constraint_info = [
                            f"\n{con['constraint_type']} Constraint: {con['constraint_name']}",
                            COLUMNS_HEADER
                        ]

                    col_info = f"  - {con['column_name']}"
                    if con['referenced_table_name']:
                        col_info += f" -> {con['referenced_table_name']}.{con['referenced_column_name']}"
                    constraint_info.append(col_info)

                if constraint_info:
                    output.extend(constraint_info)

                return "\n".join(output)

        except mysql.connector.Error as e:
            error_msg = f"Failed to get constraint information: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def explain_query(self, sql: str) -> str:
        """Get query execution plan"""
        conn = None
        try:
            conn_params = self.config.get_connection_params()
            conn = mysql.connector.connect(**conn_params)
            with conn.cursor(dictionary=True) as cur:  # NOSONAR
                # Get EXPLAIN output
                cur.execute(f"EXPLAIN FORMAT=TREE {sql}")
                explain_result = cur.fetchall()

                # Get EXPLAIN ANALYZE output
                cur.execute(f"EXPLAIN ANALYZE {sql}")
                analyze_result = cur.fetchall()

                output = [
                    "Query Execution Plan:",
                    "==================",
                    "\nEstimated Plan:",
                    "----------------"
                ]
                for row in explain_result:
                    output.append(str(row['EXPLAIN']))

                output.extend([
                    "\nActual Plan (ANALYZE):",
                    "----------------------"
                ])
                for row in analyze_result:
                    output.append(str(row['EXPLAIN']))

                return "\n".join(output)

        except mysql.connector.Error as e:
            error_msg = f"Failed to explain query: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def test_connection(self) -> bool:
        """Test database connection

        Returns:
            bool: True if connection is successful, False otherwise
        """
        conn = None
        try:
            conn_params = self.config.get_connection_params()
            conn = mysql.connector.connect(**conn_params)
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                return True
        except mysql.connector.Error as e:
            self.log("error", f"Connection test failed: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()

    async def cleanup(self):
        """Cleanup resources"""
        # Log final stats before cleanup
        self.log("info", f"Final MySQL handler stats: {self.stats.to_dict()}")

        # 主动关闭连接
        if hasattr(self, '_connection') and self._connection:
            try:
                self.log("debug", "Closing MySQL connection")
                self._connection.close()
                self._connection = None
            except Exception as e:
                self.log("warning", f"Error closing MySQL connection: {str(e)}")

        # 清理其他资源
        self.log("debug", "MySQL handler cleanup complete")
