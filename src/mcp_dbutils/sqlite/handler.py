"""SQLite connection handler implementation"""

import sqlite3
import time

import mcp.types as types

from ..base import ConnectionHandler, ConnectionHandlerError
from .config import SQLiteConfig

# 常量定义
COLUMNS_HEADER = "Columns:"


class SQLiteHandler(ConnectionHandler):
    @property
    def db_type(self) -> str:
        return 'sqlite'

    def __init__(self, config_path: str, connection: str, debug: bool = False):
        """Initialize SQLite handler

        Args:
            config_path: Path to configuration file
            connection: Database connection name
            debug: Enable debug mode
        """
        super().__init__(config_path, connection, debug)
        self.config = SQLiteConfig.from_yaml(config_path, connection)

    async def get_tables(self) -> list[types.Resource]:
        """Get all table resources"""
        try:
            with sqlite3.connect(self.config.path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cur.fetchall()
                return [
                    types.Resource(
                        uri=f"sqlite://{self.connection}/{table[0]}/schema",
                        name=f"{table[0]} schema",
                        mimeType="application/json"
                    ) for table in tables
                ]
        except sqlite3.Error as e:
            error_msg = f"Failed to get table list: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)

    async def get_schema(self, table_name: str) -> str:
        """Get table schema information"""
        try:
            with sqlite3.connect(self.config.path) as conn:
                cur = conn.cursor()
                cur.execute(f"PRAGMA table_info({table_name})")
                columns = cur.fetchall()

                cur.execute(f"PRAGMA index_list({table_name})")
                indexes = cur.fetchall()

                return str({
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
                })
        except sqlite3.Error as e:
            error_msg = f"Failed to read table schema: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)

    async def _execute_query(self, sql: str) -> str:
        """Execute SQL query"""
        try:
            # Check if the query is a DDL statement
            sql_upper = sql.strip().upper()
            is_ddl = sql_upper.startswith(("CREATE", "DROP", "ALTER", "TRUNCATE"))
            is_dml = sql_upper.startswith(("INSERT", "UPDATE", "DELETE"))
            is_select = sql_upper.startswith("SELECT")

            if not (is_select or is_ddl or is_dml):
                raise ConnectionHandlerError("Only SELECT, DDL, and DML statements are allowed")

            conn = sqlite3.connect(self.config.path)
            cur = conn.cursor()

            try:
                start_time = time.time()
                cur.execute(sql)
                conn.commit()
                end_time = time.time()
                elapsed_ms = (end_time - start_time) * 1000
                self.log("debug", f"Query executed in {elapsed_ms:.2f}ms")

                if is_select:
                    # Get column names
                    columns = [description[0] for description in cur.description]
                    # Fetch results and convert to dictionaries
                    results = []
                    for row in cur.fetchall():
                        # Convert each row to a dictionary
                        row_dict = {}
                        for i, col_name in enumerate(columns):
                            row_dict[col_name] = row[i]
                        results.append(row_dict)

                    return str({
                        "columns": columns,
                        "rows": results
                    })
                else:
                    # For DDL/DML statements
                    return "Query executed successfully"
            except sqlite3.Error as e:
                self.log("error", f"Query error: {str(e)}")
                raise ConnectionHandlerError(str(e))
            finally:
                cur.close()
                conn.close()
        except sqlite3.Error as e:
            error_msg = f"[{self.db_type}] Query execution failed: {str(e)}"
            raise ConnectionHandlerError(error_msg)

    async def _execute_write_query(self, sql: str) -> str:
        """Execute SQL write query

        Args:
            sql: SQL write query (INSERT, UPDATE, DELETE)

        Returns:
            str: Execution result

        Raises:
            ConnectionHandlerError: If query execution fails
        """
        try:
            # Check if the query is a write operation
            sql_upper = sql.strip().upper()
            is_insert = sql_upper.startswith("INSERT")
            is_update = sql_upper.startswith("UPDATE")
            is_delete = sql_upper.startswith("DELETE")
            is_transaction = sql_upper.startswith(("BEGIN", "COMMIT", "ROLLBACK"))

            if not (is_insert or is_update or is_delete or is_transaction):
                raise ConnectionHandlerError("Only INSERT, UPDATE, DELETE, and transaction statements are allowed for write operations")

            conn = sqlite3.connect(self.config.path)
            cur = conn.cursor()

            try:
                start_time = time.time()
                cur.execute(sql)
                conn.commit()
                end_time = time.time()
                elapsed_ms = (end_time - start_time) * 1000

                # Get number of affected rows
                affected_rows = cur.rowcount

                self.log("debug", f"Write operation executed in {elapsed_ms:.2f}ms, affected {affected_rows} rows")

                # Return result
                if is_transaction:
                    return f"Transaction operation executed successfully"
                else:
                    return f"Write operation executed successfully. {affected_rows} row{'s' if affected_rows != 1 else ''} affected."
            except sqlite3.Error as e:
                self.log("error", f"Write operation error: {str(e)}")
                raise ConnectionHandlerError(str(e))
            finally:
                cur.close()
                conn.close()
        except sqlite3.Error as e:
            error_msg = f"[{self.db_type}] Write operation failed: {str(e)}"
            raise ConnectionHandlerError(error_msg)

    async def get_table_description(self, table_name: str) -> str:
        """Get detailed table description"""
        try:
            with sqlite3.connect(self.config.path) as conn:
                cur = conn.cursor()
                # 获取表信息
                cur.execute(f"PRAGMA table_info({table_name})")
                columns = cur.fetchall()

                # SQLite不支持表级注释，但我们可以获取表的详细信息
                description = [
                    f"Table: {table_name}\n",
                    COLUMNS_HEADER
                ]

                for col in columns:
                    col_info = [
                        f"  {col[1]} ({col[2]})",
                        f"    Nullable: {'No' if col[3] else 'Yes'}",
                        f"    Default: {col[4] or 'None'}",
                        f"    Primary Key: {'Yes' if col[5] else 'No'}"
                    ]
                    description.extend(col_info)
                    description.append("")  # Empty line between columns

                return "\n".join(description)

        except sqlite3.Error as e:
            error_msg = f"Failed to get table description: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)

    async def get_table_ddl(self, table_name: str) -> str:
        """Get DDL statement for creating table"""
        try:
            with sqlite3.connect(self.config.path) as conn:
                cur = conn.cursor()
                # SQLite provides the complete CREATE statement
                cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                result = cur.fetchone()

                if not result:
                    return f"Table {table_name} not found"

                ddl = result[0]

                # Get indexes
                cur.execute("SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name=?", (table_name,))
                indexes = cur.fetchall()

                # Add index definitions
                if indexes:
                    ddl = ddl + "\n\n-- Indexes:"
                    for idx in indexes:
                        if idx[0]:  # Some internal indexes might have NULL sql
                            ddl = ddl + "\n" + idx[0] + ";"

                return ddl

        except sqlite3.Error as e:
            error_msg = f"Failed to get table DDL: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)

    async def get_table_indexes(self, table_name: str) -> str:
        """Get index information for table"""
        try:
            with sqlite3.connect(self.config.path) as conn:
                cur = conn.cursor()

                # Check if table exists
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                if not cur.fetchone():
                    raise ConnectionHandlerError(f"Table '{table_name}' doesn't exist")

                # 获取索引列表
                cur.execute(f"PRAGMA index_list({table_name})")
                indexes = cur.fetchall()

                if not indexes:
                    return f"No indexes found on table {table_name}"

                formatted_indexes = [f"Indexes for {table_name}:"]

                for idx in indexes:
                    # 获取索引详细信息
                    cur.execute(f"PRAGMA index_info({idx[1]})")
                    index_info = cur.fetchall()

                    # 获取索引的SQL定义
                    cur.execute("SELECT sql FROM sqlite_master WHERE type='index' AND name=?", (idx[1],))
                    sql = cur.fetchone()

                    index_details = [
                        f"\nIndex: {idx[1]}",
                        f"Type: {'UNIQUE' if idx[2] else 'INDEX'}",
                        COLUMNS_HEADER
                    ]

                    for col in index_info:
                        index_details.append(f"  - {col[2]}")

                    if sql and sql[0]:
                        index_details.extend([
                            "Definition:",
                            f"  {sql[0]}"
                        ])

                    formatted_indexes.extend(index_details)

                return "\n".join(formatted_indexes)

        except sqlite3.Error as e:
            error_msg = f"Failed to get index information: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)

    async def get_table_stats(self, table_name: str) -> str:
        """Get table statistics information"""
        try:
            with sqlite3.connect(self.config.path) as conn:
                cur = conn.cursor()

                # Check if table exists
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                if not cur.fetchone():
                    raise ConnectionHandlerError(f"Table '{table_name}' doesn't exist")

                # Get basic table information
                cur.execute(f"PRAGMA table_info({table_name})")
                columns = cur.fetchall()

                # Count rows
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cur.fetchone()[0]

                # Get index information
                cur.execute(f"PRAGMA index_list({table_name})")
                indexes = cur.fetchall()

                # Get page count and size
                cur.execute("PRAGMA page_count")
                page_count = cur.fetchone()[0]
                cur.execute("PRAGMA page_size")
                page_size = cur.fetchone()[0]

                # Calculate total size
                total_size = page_count * page_size

                # Format size in human readable format
                def format_size(size):
                    for unit in ['B', 'KB', 'MB', 'GB']:
                        if size < 1024:
                            return f"{size:.2f} {unit}"
                        size /= 1024
                    return f"{size:.2f} TB"

                # Get column statistics
                column_stats = []
                for col in columns:
                    col_name = col[1]
                    # Get null count
                    cur.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL")
                    null_count = cur.fetchone()[0]
                    # Get distinct value count
                    cur.execute(f"SELECT COUNT(DISTINCT {col_name}) FROM {table_name}")
                    distinct_count = cur.fetchone()[0]

                    column_stats.append({
                        'name': col_name,
                        'type': col[2],
                        'null_count': null_count,
                        'null_percent': (null_count / row_count * 100) if row_count > 0 else 0,
                        'distinct_count': distinct_count
                    })

                # Format output
                output = [
                    f"Table Statistics for {table_name}:",
                    f"  Row Count: {row_count:,}",
                    f"  Total Size: {format_size(total_size)}",
                    f"  Page Count: {page_count:,}",
                    f"  Page Size: {format_size(page_size)}",
                    f"  Index Count: {len(indexes)}\n",
                    "Column Statistics:"
                ]

                for stat in column_stats:
                    col_info = [
                        f"  {stat['name']} ({stat['type']}):",
                        f"    Null Values: {stat['null_count']:,} ({stat['null_percent']:.1f}%)",
                        f"    Distinct Values: {stat['distinct_count']:,}"
                    ]
                    output.extend(col_info)
                    output.append("")  # Empty line between columns

                return "\n".join(output)

        except sqlite3.Error as e:
            error_msg = f"Failed to get table statistics: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)

    async def get_table_constraints(self, table_name: str) -> str:
        """Get constraint information for table"""
        try:
            with sqlite3.connect(self.config.path) as conn:
                cur = conn.cursor()

                # Get table info (includes PRIMARY KEY)
                cur.execute(f"PRAGMA table_info({table_name})")
                columns = cur.fetchall()

                # Get foreign keys
                cur.execute(f"PRAGMA foreign_key_list({table_name})")
                foreign_keys = cur.fetchall()

                # Get indexes (for UNIQUE constraints)
                cur.execute(f"PRAGMA index_list({table_name})")
                indexes = cur.fetchall()

                output = [f"Constraints for {table_name}:"]

                # Primary Key constraints
                pk_columns = [col[1] for col in columns if col[5]]  # col[5] is pk flag
                if pk_columns:
                    output.extend([
                        "\nPrimary Key Constraints:",
                        f"  PRIMARY KEY ({', '.join(pk_columns)})"
                    ])

                # Foreign Key constraints
                if foreign_keys:
                    output.append("\nForeign Key Constraints:")
                    current_fk = None
                    fk_columns = []

                    for fk in foreign_keys:
                        # SQLite foreign_key_list format:
                        # id, seq, table, from, to, on_update, on_delete, match
                        if current_fk != fk[0]:
                            if fk_columns:
                                output.append(f"    ({', '.join(fk_columns)})")
                            current_fk = fk[0]
                            fk_columns = []
                            output.append(f"  FOREIGN KEY:")
                            output.append(f"    Referenced Table: {fk[2]}")
                        fk_columns.append(f"{fk[3]} -> {fk[2]}.{fk[4]}")
                        if fk[5]:  # on_update
                            output.append(f"    ON UPDATE: {fk[5]}")
                        if fk[6]:  # on_delete
                            output.append(f"    ON DELETE: {fk[6]}")

                    if fk_columns:
                        output.append(f"    ({', '.join(fk_columns)})")

                # Unique constraints (from indexes)
                unique_indexes = [idx for idx in indexes if idx[2]]  # idx[2] is unique flag
                if unique_indexes:
                    output.append("\nUnique Constraints:")
                    for idx in unique_indexes:
                        # Get columns in the unique index
                        cur.execute(f"PRAGMA index_info({idx[1]})")
                        index_info = cur.fetchall()
                        columns = [info[2] for info in index_info]  # info[2] is column name
                        output.append(f"  UNIQUE ({', '.join(columns)})")

                # Check constraints
                # Note: SQLite doesn't provide direct access to CHECK constraints through PRAGMA
                # We need to parse the table creation SQL
                cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                create_sql = cur.fetchone()[0]
                if "CHECK" in create_sql.upper():
                    output.append("\nCheck Constraints:")
                    output.append("  See table DDL for CHECK constraints")

                return "\n".join(output)

        except sqlite3.Error as e:
            error_msg = f"Failed to get constraint information: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)

    async def explain_query(self, sql: str) -> str:
        """Get query execution plan"""
        try:
            with sqlite3.connect(self.config.path) as conn:
                cur = conn.cursor()

                # Check if the query is valid by preparing it
                try:
                    # Use prepare to validate the query without executing it
                    conn.execute(f"EXPLAIN {sql}")
                except sqlite3.Error as e:
                    raise ConnectionHandlerError(f"Failed to explain query: {str(e)}")

                # Get EXPLAIN output
                cur.execute(f"EXPLAIN QUERY PLAN {sql}")
                plan = cur.fetchall()

                # Format the output
                output = [
                    "Query Execution Plan:",
                    "==================\n",
                    "Details:",
                    "--------"
                ]

                for step in plan:
                    # EXPLAIN QUERY PLAN format:
                    # id | parent | notused | detail
                    indent = "  " * (step[0] - step[1] if step[1] >= 0 else step[0])
                    output.append(f"{indent}{step[3]}")

                # Add query statistics
                output.extend([
                    "\nNote: SQLite's EXPLAIN QUERY PLAN provides a high-level overview.",
                    "For detailed execution statistics, consider using EXPLAIN (not QUERY PLAN)",
                    "which shows the virtual machine instructions."
                ])

                return "\n".join(output)

        except sqlite3.Error as e:
            error_msg = f"Failed to explain query: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)

    async def test_connection(self) -> bool:
        """Test database connection

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            with sqlite3.connect(self.config.path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT 1")
                return True
        except sqlite3.Error as e:
            self.log("error", f"Connection test failed: {str(e)}")
            return False

    async def cleanup(self):
        """Cleanup resources"""
        # Log final stats
        self.log("info", f"Final SQLite handler stats: {self.stats.to_dict()}")

        # 主动关闭连接
        if hasattr(self, '_connection') and self._connection:
            try:
                self.log("debug", "Closing SQLite connection")
                self._connection.close()
                self._connection = None
            except Exception as e:
                self.log("warning", f"Error closing SQLite connection: {str(e)}")

        # 清理其他资源
        self.log("debug", "SQLite handler cleanup complete")
