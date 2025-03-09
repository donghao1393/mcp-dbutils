"""SQLite connection handler implementation"""

import sqlite3
import json
from typing import Any
import mcp.types as types

from ..base import ConnectionHandler, ConnectionHandlerError
from .config import SQLiteConfig

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
            # Only allow SELECT statements
            if not sql.strip().upper().startswith("SELECT"):
                raise ConnectionHandlerError("cannot execute DELETE statement")
            
            with sqlite3.connect(self.config.path) as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                self.log("debug", f"Executing query: {sql}")
                
                cur.execute(sql)
                results = cur.fetchall()
                rows = [dict(row) for row in results]

                result_text = str({
                    'type': self.db_type,
                    'columns': list(rows[0].keys()) if rows else [],
                    'rows': rows,
                    'row_count': len(rows)
                })

                self.log("debug", f"Query completed, returned {len(rows)} rows")
                return result_text
        except sqlite3.Error as e:
            error_msg = f"[{self.db_type}] Query execution failed: {str(e)}"
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
                    "Columns:"
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
                cur.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                result = cur.fetchone()
                
                if not result:
                    return f"Table {table_name} not found"
                
                ddl = result[0]
                
                # Get indexes
                cur.execute(f"SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name=?", (table_name,))
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
                        "Columns:"
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
                cur.execute(f"PRAGMA page_count")
                page_count = cur.fetchone()[0]
                cur.execute(f"PRAGMA page_size")
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

    async def cleanup(self):
        """Cleanup resources"""
        # Log final stats
        self.log("info", f"Final SQLite handler stats: {self.stats.to_dict()}")
