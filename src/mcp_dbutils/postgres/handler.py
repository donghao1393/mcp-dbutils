"""PostgreSQL database handler implementation"""

import psycopg2
from psycopg2.pool import SimpleConnectionPool
import mcp.types as types

from ..base import DatabaseHandler, DatabaseError
from .config import PostgresConfig

class PostgresHandler(DatabaseHandler):
    @property
    def db_type(self) -> str:
        return 'postgres'

    def __init__(self, config_path: str, database: str, debug: bool = False):
        """Initialize PostgreSQL handler

        Args:
            config_path: Path to configuration file
            database: Database configuration name
            debug: Enable debug mode
        """
        super().__init__(config_path, database, debug)
        self.config = PostgresConfig.from_yaml(config_path, database)

        # No connection pool creation during initialization
        masked_params = self.config.get_masked_connection_info()
        self.log("debug", f"Configuring database with parameters: {masked_params}")
        self.pool = None

    async def get_tables(self) -> list[types.Resource]:
        """Get all table resources"""
        try:
            conn_params = self.config.get_connection_params()
            conn = psycopg2.connect(**conn_params)
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        table_name,
                        obj_description(
                            (quote_ident(table_schema) || '.' || quote_ident(table_name))::regclass,
                            'pg_class'
                        ) as description
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """)
                tables = cur.fetchall()
                return [
                    types.Resource(
                        uri=f"postgres://{self.database}/{table[0]}/schema",
                        name=f"{table[0]} schema",
                        description=table[1] if table[1] else None,
                        mimeType="application/json"
                    ) for table in tables
                ]
        except psycopg2.Error as e:
            error_msg = f"Failed to get table list: [Code: {e.pgcode}] {e.pgerror or str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise DatabaseError(error_msg)
        finally:
            if conn:
                conn.close()

    async def get_schema(self, table_name: str) -> str:
        """Get table schema information"""
        try:
            conn_params = self.config.get_connection_params()
            conn = psycopg2.connect(**conn_params)
            with conn.cursor() as cur:
                # Get column information
                cur.execute("""
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
                columns = cur.fetchall()

                # Get constraint information
                cur.execute("""
                    SELECT
                        conname as constraint_name,
                        contype as constraint_type
                    FROM pg_constraint c
                    JOIN pg_class t ON c.conrelid = t.oid
                    WHERE t.relname = %s
                """, (table_name,))
                constraints = cur.fetchall()

                return str({
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
                })
        except psycopg2.Error as e:
            error_msg = f"Failed to read table schema: [Code: {e.pgcode}] {e.pgerror or str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise DatabaseError(error_msg)
        finally:
            if conn:
                conn.close()

    async def _execute_query(self, sql: str) -> str:
        """Execute SQL query"""
        conn = None
        try:
            conn_params = self.config.get_connection_params()
            conn = psycopg2.connect(**conn_params)
            self.log("debug", f"Executing query: {sql}")

            with conn.cursor() as cur:
                # Start read-only transaction
                cur.execute("BEGIN TRANSACTION READ ONLY")
                try:
                    cur.execute(sql)
                    results = cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    formatted_results = [dict(zip(columns, row)) for row in results]

                    result_text = str({
                        'type': self.db_type,
                        'columns': columns,
                        'rows': formatted_results,
                        'row_count': len(results)
                    })

                    self.log("debug", f"Query completed, returned {len(results)} rows")
                    return result_text
                finally:
                    cur.execute("ROLLBACK")
        except psycopg2.Error as e:
            error_msg = f"[{self.db_type}] Query execution failed: [Code: {e.pgcode}] {e.pgerror or str(e)}"
            raise DatabaseError(error_msg)
        finally:
            if conn:
                conn.close()

    async def get_table_description(self, table_name: str) -> str:
        """Get detailed table description"""
        conn = None
        try:
            conn_params = self.config.get_connection_params()
            conn = psycopg2.connect(**conn_params)
            with conn.cursor() as cur:
                # 获取表的基本信息和注释
                cur.execute("""
                    SELECT obj_description(
                        (quote_ident(table_schema) || '.' || quote_ident(table_name))::regclass,
                        'pg_class'
                    ) as table_comment
                    FROM information_schema.tables 
                    WHERE table_name = %s
                """, (table_name,))
                table_info = cur.fetchone()
                table_comment = table_info[0] if table_info else None

                # 获取列信息
                cur.execute("""
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
                columns = cur.fetchall()

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
                    description.append("")  # Empty line between columns
                
                return "\n".join(description)
                
        except psycopg2.Error as e:
            error_msg = f"Failed to get table description: [Code: {e.pgcode}] {e.pgerror or str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise DatabaseError(error_msg)
        finally:
            if conn:
                conn.close()

    async def get_table_ddl(self, table_name: str) -> str:
        """Get DDL statement for creating table"""
        conn = None
        try:
            conn_params = self.config.get_connection_params()
            conn = psycopg2.connect(**conn_params)
            with conn.cursor() as cur:
                # 获取列定义
                cur.execute("""
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
                columns = cur.fetchall()

                # 获取约束
                cur.execute("""
                    SELECT 
                        conname as constraint_name,
                        pg_get_constraintdef(c.oid) as constraint_def
                    FROM pg_constraint c
                    JOIN pg_class t ON c.conrelid = t.oid
                    WHERE t.relname = %s
                """, (table_name,))
                constraints = cur.fetchall()

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
                cur.execute("""
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
                comments = cur.fetchall()
                
                for comment in comments:
                    if comment[2]:  # table comment
                        ddl.append(f"\nCOMMENT ON TABLE {table_name} IS '{comment[2]}';")
                    if comment[1]:  # column comment
                        ddl.append(f"COMMENT ON COLUMN {table_name}.{comment[0]} IS '{comment[1]}';")
                
                return "\n".join(ddl)
                
        except psycopg2.Error as e:
            error_msg = f"Failed to get table DDL: [Code: {e.pgcode}] {e.pgerror or str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise DatabaseError(error_msg)
        finally:
            if conn:
                conn.close()

    async def get_table_indexes(self, table_name: str) -> str:
        """Get index information for table"""
        conn = None
        try:
            conn_params = self.config.get_connection_params()
            conn = psycopg2.connect(**conn_params)
            with conn.cursor() as cur:
                # 获取索引信息
                cur.execute("""
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
                indexes = cur.fetchall()

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
                
        except psycopg2.Error as e:
            error_msg = f"Failed to get index information: [Code: {e.pgcode}] {e.pgerror or str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise DatabaseError(error_msg)
        finally:
            if conn:
                conn.close()

    async def cleanup(self):
        """Cleanup resources"""
        # Log final stats before cleanup
        self.log("info", f"Final PostgreSQL handler stats: {self.stats.to_dict()}")
