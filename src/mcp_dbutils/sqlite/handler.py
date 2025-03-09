"""SQLite database handler implementation"""

import sqlite3
from pathlib import Path
from contextlib import closing
import mcp.types as types

from ..base import DatabaseHandler, DatabaseError
from .config import SqliteConfig

class SqliteHandler(DatabaseHandler):
    @property
    def db_type(self) -> str:
        return 'sqlite'

    def __init__(self, config_path: str, database: str, debug: bool = False):
        """Initialize SQLite handler

        Args:
            config_path: Path to configuration file
            database: Database configuration name
            debug: Enable debug mode
        """
        super().__init__(config_path, database, debug)
        self.config = SqliteConfig.from_yaml(config_path, database)

        # Ensure database directory exists
        db_file = Path(self.config.absolute_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        # No connection test during initialization
        self.log("debug", f"Configuring database: {self.config.get_masked_connection_info()}")

    def _get_connection(self):
        """Get database connection"""
        connection_params = self.config.get_connection_params()
        conn = sqlite3.connect(**connection_params)
        conn.row_factory = sqlite3.Row
        return conn

    async def get_tables(self) -> list[types.Resource]:
        """Get all table resources"""
        try:
            with closing(self._get_connection()) as conn:
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                tables = cursor.fetchall()

                return [
                    types.Resource(
                        uri=f"sqlite://{self.database}/{table[0]}/schema",
                        name=f"{table[0]} schema",
                        mimeType="application/json"
                    ) for table in tables
                ]
        except sqlite3.Error as e:
            error_msg = f"Failed to get table list: {str(e)}"
            self.log("error", error_msg)
            raise

    async def get_schema(self, table_name: str) -> str:
        """Get table schema information"""
        try:
            with closing(self._get_connection()) as conn:
                # Get table structure
                cursor = conn.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()

                # Get index information
                cursor = conn.execute(f"PRAGMA index_list({table_name})")
                indexes = cursor.fetchall()

                schema_info = {
                    'columns': [{
                        'name': col['name'],
                        'type': col['type'],
                        'nullable': not col['notnull'],
                        'primary_key': bool(col['pk'])
                    } for col in columns],
                    'indexes': [{
                        'name': idx['name'],
                        'unique': bool(idx['unique'])
                    } for idx in indexes]
                }

                return str(schema_info)
        except sqlite3.Error as e:
            error_msg = f"Failed to read table schema: {str(e)}"
            self.log("error", error_msg)
            raise

    async def _execute_query(self, sql: str) -> str:
        """Execute SQL query"""
        # Check for non-SELECT queries
        sql_lower = sql.lower().strip()
        if not sql_lower.startswith('select'):
            error_msg = "cannot execute DELETE statement"
            if sql_lower.startswith('delete'):
                error_msg = "cannot execute DELETE statement"
            elif sql_lower.startswith('update'):
                error_msg = "cannot execute UPDATE statement"
            elif sql_lower.startswith('insert'):
                error_msg = "cannot execute INSERT statement"
            raise DatabaseError(error_msg)

        try:
            with closing(self._get_connection()) as conn:
                self.log("debug", f"Executing query: {sql}")
                cursor = conn.execute(sql)
                results = cursor.fetchall()

                columns = [desc[0] for desc in cursor.description]
                formatted_results = [dict(zip(columns, row)) for row in results]

                result_text = str({
                    'type': self.db_type,
                    'columns': columns,
                    'rows': formatted_results,
                    'row_count': len(results)
                })

                self.log("debug", f"Query completed, returned {len(results)} rows")
                return result_text

        except sqlite3.Error as e:
            error_msg = f"[{self.db_type}] Query execution failed: {str(e)}"
            raise DatabaseError(error_msg)

    async def get_table_description(self, table_name: str) -> str:
        """Get detailed table description"""
        try:
            with closing(self._get_connection()) as conn:
                # 获取表结构
                cursor = conn.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()

                # 获取表的外键信息
                cursor = conn.execute(f"PRAGMA foreign_key_list({table_name})")
                foreign_keys = cursor.fetchall()

                # 格式化输出
                description = [
                    f"Table: {table_name}\n",
                    "Columns:"
                ]

                for col in columns:
                    col_info = [
                        f"  {col['name']} ({col['type']})",
                        f"    Nullable: {not col['notnull']}",
                        f"    Default: {col['dflt_value'] or 'None'}",
                        f"    Primary Key: {bool(col['pk'])}"
                    ]
                    description.extend(col_info)
                    description.append("")

                if foreign_keys:
                    description.append("Foreign Keys:")
                    for fk in foreign_keys:
                        fk_info = [
                            f"  Column: {fk['from']}",
                            f"    References: {fk['table']}.{fk['to']}",
                            f"    On Delete: {fk['on_delete']}",
                            f"    On Update: {fk['on_update']}"
                        ]
                        description.extend(fk_info)
                        description.append("")

                return "\n".join(description)

        except sqlite3.Error as e:
            error_msg = f"Failed to get table description: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise DatabaseError(error_msg)

    async def get_table_ddl(self, table_name: str) -> str:
        """Get DDL statement for creating table"""
        try:
            with closing(self._get_connection()) as conn:
                # 获取建表语句
                cursor = conn.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                result = cursor.fetchone()
                
                if not result:
                    raise DatabaseError(f"Table {table_name} not found")
                
                ddl = [result[0]]
                
                # 获取创建索引的语句
                cursor = conn.execute(
                    "SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name=? AND sql IS NOT NULL",
                    (table_name,)
                )
                indexes = cursor.fetchall()
                
                if indexes:
                    ddl.append("")  # 空行分隔
                    ddl.extend(idx[0] for idx in indexes)
                
                return "\n".join(ddl)

        except sqlite3.Error as e:
            error_msg = f"Failed to get table DDL: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise DatabaseError(error_msg)

    async def get_table_indexes(self, table_name: str) -> str:
        """Get index information for table"""
        try:
            with closing(self._get_connection()) as conn:
                # 获取索引列表
                cursor = conn.execute(f"PRAGMA index_list({table_name})")
                indexes = cursor.fetchall()

                if not indexes:
                    return f"No indexes found on table {table_name}"

                formatted_indexes = []
                
                for idx in indexes:
                    index_info = [
                        f"Index: {idx['name']}",
                        f"Type: {'UNIQUE' if idx['unique'] else 'INDEX'}"
                    ]
                    
                    # 获取索引列信息
                    cursor = conn.execute(f"PRAGMA index_info({idx['name']})")
                    columns = cursor.fetchall()
                    
                    if columns:
                        index_info.append("Columns:")
                        for col in columns:
                            index_info.append(f"  - {col['name']}")
                    
                    formatted_indexes.extend(index_info)
                    formatted_indexes.append("")  # 空行分隔索引
                
                return "\n".join(formatted_indexes)

        except sqlite3.Error as e:
            error_msg = f"Failed to get index information: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise DatabaseError(error_msg)

    async def cleanup(self):
        """Cleanup resources"""
        # Log final stats before cleanup
        self.log("info", f"Final SQLite handler stats: {self.stats.to_dict()}")
