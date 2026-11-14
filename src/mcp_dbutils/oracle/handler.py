import asyncio
import mcp.types as types
import oracledb

from ..base import ConnectionHandler, ConnectionHandlerError
from .config import OracleConfig

COLUMNS_HEADER = "Columns:"

class OracleHandler(ConnectionHandler):
    _lock = asyncio.Lock()

    @property
    def db_type(self) -> str:
        return "oracle"

    def __init__(self, config_path: str, connection: str, debug: bool = False):
        super().__init__(config_path, connection, debug)
        self.config = OracleConfig.from_yaml(config_path, connection)
        masked_params = {**self.config.get_connection_params(), "password": "***"}
        self.log("debug", f"Configuring connection with parameters: {masked_params}")
        self.pool = None
        self.thick_mode = self.config.thick_mode
        if self.thick_mode:
            try:
                if self.config.lib_dir:
                    oracledb.init_oracle_client(lib_dir=self.config.lib_dir)
                else:
                    oracledb.init_oracle_client()
                self.log_info("Oracle Client initialized in thick mode")
            except Exception as e:
                self.log_warning(f"Could not initialize Oracle Client: {e}")
                self.log_warning("Falling back to thin mode")
                self.thick_mode = False

    async def initialize_pool(self, connection_string: str):
        """Initialize the connection pool"""
        async with OracleHandler._lock:
            if self.pool is None:
                try:
                    if self.thick_mode:
                        self.pool = oracledb.create_pool(
                            connection_string,
                            min=2,
                            max=10,
                            increment=1,
                            getmode=oracledb.POOL_GETMODE_WAIT
                        )
                    else:
                        self.pool = oracledb.create_pool_async(
                            connection_string,
                            min=2,
                            max=10,
                            increment=1,
                            getmode=oracledb.POOL_GETMODE_WAIT
                        )
                    self.log_info("Database connection pool initialized")
                except Exception as e:
                    self.log_error(f"Error creating connection pool: {e}")
                    raise
                
    async def close_pool(self):
        """Close the connection pool"""
        if self.pool:
            try:
                if self.thick_mode:
                    self.pool.close()
                else:
                    await self.pool.close()
                self.pool = None
                self.log_info("Connection pool closed")
            except Exception as e:
                self.log_error(f"Error closing connection pool: {e}")
                
    async def get_connection(self):
        # 这里可扩展为连接池，当前直接 connect
        oracle_config = self.config.get_connection_params()
        connection_string = "{user}/{password}@{dsn}".format(
            user=oracle_config.get('user'),
            password=oracle_config.get('password'),
            dsn=oracle_config.get('dsn')
        )
        if self.pool is None:
            await self.initialize_pool(connection_string)
        if self.pool is None:
            raise ConnectionHandlerError("Connection pool is not initialized")
        if self.thick_mode:
            return self.pool.acquire()
        else:
            return await self.pool.acquire()

    async def _check_table_exists(self, cursor, table_name: str) -> None:
        cursor.execute("""
            SELECT COUNT(*) FROM user_tables WHERE table_name = :1
        """, [table_name.upper()])
        count = cursor.fetchone()
        if not count or count[0] == 0:
            raise ConnectionHandlerError(f"Table '{table_name}' doesn't exist")

    async def get_tables(self) -> list[types.Resource]:
        conn = None
        try:
            conn = await self.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT table_name FROM user_tables
            """)
            tables = cur.fetchall()
            return [
                types.Resource(
                    uri=f"oracle://{self.connection}/{row[0]}/schema",
                    name=f"{row[0]} schema",
                    description=None,
                    mimeType="application/json"
                ) for row in tables
            ]
        except Exception as e:
            error_msg = f"Failed to get tables: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def get_schema(self, table_name: str) -> str:
        conn = None
        try:
            conn = await self.get_connection()
            cur = conn.cursor()
            await self._check_table_exists(cur, table_name)
            # 列信息
            cur.execute("""
                SELECT column_name, data_type, nullable FROM user_tab_columns
                WHERE table_name = :1
                ORDER BY column_id
            """, [table_name.upper()])
            columns = cur.fetchall()
            # 约束信息
            cur.execute("""
                SELECT
                    c.constraint_name,
                    c.constraint_type,
                    cc.column_name,
                    c.r_constraint_name,
                    r.table_name AS ref_table,
                    rc.column_name AS ref_column
                FROM user_constraints c
                JOIN user_cons_columns cc
                  ON c.constraint_name = cc.constraint_name
                LEFT JOIN user_constraints r
                  ON c.r_constraint_name = r.constraint_name
                LEFT JOIN user_cons_columns rc
                  ON r.constraint_name = rc.constraint_name
                     AND cc.position = rc.position
                WHERE c.table_name = :1
                ORDER BY c.constraint_name, cc.position
            """, [table_name.upper()])
            rows = cur.fetchall()
            constraints = {}
            for row in rows:
                name, ctype, col, _, ref_table, ref_col = row
                if name not in constraints:
                    constraints[name] = {
                        "name": name,
                        "type": {
                            "P": "PRIMARY KEY",
                            "R": "FOREIGN KEY",
                            "U": "UNIQUE",
                            "C": "CHECK"
                        }.get(ctype, ctype),
                        "columns": []
                    }
                    if ctype == "R":
                        constraints[name]["referenced_table"] = ref_table
                        constraints[name]["referenced_columns"] = []
                constraints[name]["columns"].append(col)
                if ctype == "R" and ref_col:
                    constraints[name]["referenced_columns"].append(ref_col)
            constraint_list = list(constraints.values())
            return str({
                'columns': [{
                    'name': col[0],
                    'type': col[1],
                    'nullable': col[2] == 'Y',
                    'description': None
                } for col in columns],
                'constraints': constraint_list
            })
        except Exception as e:
            error_msg = f"Failed to read table schema: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def _execute_query(self, sql: str) -> str:
        conn = None
        try:
            conn = await self.get_connection()
            self.log("debug", f"Executing query: {sql}")
            cur = conn.cursor()
            sql_upper = sql.strip().upper()
            is_select = sql_upper.startswith("SELECT")
            if is_select:
                cur.execute("SAVEPOINT ro_savepoint")  # Oracle没有SET TRANSACTION READ ONLY
            try:
                cur.execute(sql)
                if not is_select:
                    conn.commit()
                results = cur.fetchall() if is_select else []
                if cur.description is None:
                    return "Query executed successfully"
                columns = [desc[0] for desc in cur.description]
                return str({
                    "columns": columns,
                    "rows": results
                })
            except Exception as e:
                self.log("error", f"Query error: {str(e)}")
                raise ConnectionHandlerError(str(e))
            finally:
                cur.close()
        except Exception as e:
            error_msg = f"[{self.db_type}] Query execution failed: {str(e)}"
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def _execute_write_query(self, sql: str) -> str:
        conn = None
        try:
            sql_upper = sql.strip().upper()
            is_insert = sql_upper.startswith("INSERT")
            is_update = sql_upper.startswith("UPDATE")
            is_delete = sql_upper.startswith("DELETE")
            is_transaction = sql_upper.startswith(("BEGIN", "COMMIT", "ROLLBACK", "SAVEPOINT"))
            if not (is_insert or is_update or is_delete or is_transaction):
                raise ConnectionHandlerError("Only INSERT, UPDATE, DELETE, and transaction statements are allowed for write operations")
            conn = await self.get_connection()
            self.log("debug", f"Executing write operation: {sql}")
            cur = conn.cursor()
            try:
                cur.execute(sql)
                affected_rows = cur.rowcount
                if not is_transaction:
                    conn.commit()
                self.log("debug", f"Write operation executed successfully, affected {affected_rows} rows")
                if is_transaction:
                    return f"Transaction operation executed successfully"
                else:
                    return f"Write operation executed successfully. {affected_rows} row{'s' if affected_rows != 1 else ''} affected."
            except Exception as e:
                if not is_transaction:
                    conn.rollback()
                self.log("error", f"Write operation error: {str(e)}")
                raise ConnectionHandlerError(str(e))
            finally:
                cur.close()
        except Exception as e:
            error_msg = f"[{self.db_type}] Write operation failed: {str(e)}"
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def get_table_description(self, table_name: str) -> str:
        conn = None
        try:
            conn = await self.get_connection()
            cur = conn.cursor()
            await self._check_table_exists(cur, table_name)
            # Oracle没有表注释字段，需查user_tab_comments
            cur.execute("""
                SELECT comments FROM user_tab_comments WHERE table_name = :1
            """, [table_name.upper()])
            table_info = cur.fetchone()
            table_comment = table_info[0] if table_info else None
            # 列信息
            cur.execute("""
                SELECT column_name, data_type, data_default, nullable, data_length, data_precision, data_scale
                FROM user_tab_columns
                WHERE table_name = :1
                ORDER BY column_id
            """, [table_name.upper()])
            columns = cur.fetchall()
            # 列注释
            cur.execute("""
                SELECT column_name, comments FROM user_col_comments WHERE table_name = :1
            """, [table_name.upper()])
            col_comments = {row[0]: row[1] for row in cur.fetchall()}
            description = [
                f"Table: {table_name}",
                f"Comment: {table_comment or 'No comment'}\n",
                COLUMNS_HEADER
            ]
            for col in columns:
                col_info = [
                    f"  {col[0]} ({col[1]})",
                    f"    Nullable: {col[3]}",
                    f"    Default: {col[2] or 'None'}"
                ]
                if col[4]:
                    col_info.append(f"    Length: {col[4]}")
                if col[5]:
                    col_info.append(f"    Precision: {col[5]}")
                if col[6]:
                    col_info.append(f"    Scale: {col[6]}")
                if col[0] in col_comments and col_comments[col[0]]:
                    col_info.append(f"    Comment: {col_comments[col[0]]}")
                description.extend(col_info)
                description.append("")
            return "\n".join(description)
        except Exception as e:
            error_msg = f"Failed to get table description: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def get_table_ddl(self, table_name: str) -> str:
        conn = None
        try:
            conn = await self.get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT dbms_metadata.get_ddl('TABLE', :1) FROM dual",
                [table_name.upper()]
            )
            ddl = cur.fetchone()
            if ddl and ddl[0]:
                return ddl[0].read() if hasattr(ddl[0], "read") else ddl[0]
            return f"Failed to get DDL for table {table_name}"
        except Exception as e:
            error_msg = f"Failed to get table DDL: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def get_table_indexes(self, table_name: str) -> str:
        conn = None
        try:
            conn = await self.get_connection()
            cur = conn.cursor()
            await self._check_table_exists(cur, table_name)
            cur.execute("""
                SELECT index_name, uniqueness FROM user_indexes WHERE table_name = :1
            """, [table_name.upper()])
            indexes = cur.fetchall()
            if not indexes:
                return f"No indexes found on table {table_name}"
            output = []
            for idx in indexes:
                output.append(f"Index: {idx[0]}")
                output.append(f"Type: {idx[1]}")
                output.append(COLUMNS_HEADER)
                cur.execute("""
                    SELECT column_name FROM user_ind_columns
                    WHERE table_name = :1 AND index_name = :2
                    ORDER BY column_position
                """, [table_name.upper(), idx[0]])
                cols = cur.fetchall()
                for col in cols:
                    output.append(f"  - {col[0]}")
                output.append("")
            return "\n".join(output)
        except Exception as e:
            error_msg = f"Failed to get index information: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def get_table_stats(self, table_name: str) -> str:
        conn = None
        try:
            conn = await self.get_connection()
            cur = conn.cursor()
            await self._check_table_exists(cur, table_name)
            cur.execute("""
                SELECT num_rows, blocks, avg_row_len
                FROM user_tables
                WHERE table_name = :1
            """, [table_name.upper()])
            stats = cur.fetchone()
            if not stats:
                return f"No statistics found for table {table_name}"
            output = [
                f"Table Statistics for {table_name}:",
                f"  Estimated Row Count: {stats[0]}",
                f"  Blocks: {stats[1]}",
                f"  Average Row Length: {stats[2]} bytes"
            ]
            return "\n".join(output)
        except Exception as e:
            error_msg = f"Failed to get table statistics: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def get_table_constraints(self, table_name: str) -> str:
        conn = None
        try:
            conn = await self.get_connection()
            cur = conn.cursor()
            await self._check_table_exists(cur, table_name)
            cur.execute("""
                SELECT
                    c.constraint_name,
                    c.constraint_type,
                    cc.column_name,
                    c.r_constraint_name,
                    r.table_name AS ref_table,
                    rc.column_name AS ref_column
                FROM user_constraints c
                JOIN user_cons_columns cc
                  ON c.constraint_name = cc.constraint_name
                LEFT JOIN user_constraints r
                  ON c.r_constraint_name = r.constraint_name
                LEFT JOIN user_cons_columns rc
                  ON r.constraint_name = rc.constraint_name
                     AND cc.position = rc.position
                WHERE c.table_name = :1
                ORDER BY c.constraint_type, c.constraint_name, cc.position
            """, [table_name.upper()])
            constraints = cur.fetchall()
            if not constraints:
                return f"No constraints found on table {table_name}"
            output = [f"Constraints for {table_name}:"]
            current_constraint = None
            constraint_info = []
            for con in constraints:
                if current_constraint != con[0]:
                    if constraint_info:
                        output.extend(constraint_info)
                        output.append("")
                    current_constraint = con[0]
                    constraint_type = {
                        "P": "PRIMARY KEY",
                        "R": "FOREIGN KEY",
                        "U": "UNIQUE",
                        "C": "CHECK"
                    }.get(con[1], con[1])
                    constraint_info = [
                        f"\n{constraint_type} Constraint: {con[0]}",
                        COLUMNS_HEADER
                    ]
                col_info = f"  - {con[2]}"
                if con[1] == "R" and con[4] and con[5]:
                    col_info += f" -> {con[4]}.{con[5]}"
                constraint_info.append(col_info)
            if constraint_info:
                output.extend(constraint_info)
            return "\n".join(output)
        except Exception as e:
            error_msg = f"Failed to get constraint information: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def explain_query(self, sql: str) -> str:
        conn = None
        try:
            conn = await self.get_connection()
            cur = conn.cursor()
            # Oracle EXPLAIN PLAN
            cur.execute("EXPLAIN PLAN FOR " + sql)
            cur.execute("""
                SELECT PLAN_TABLE_OUTPUT FROM TABLE(DBMS_XPLAN.DISPLAY())
            """)
            plan = cur.fetchall()
            output = ["Query Execution Plan:", "=================="]
            for row in plan:
                output.append(row[0])
            return "\n".join(output)
        except Exception as e:
            error_msg = f"Failed to explain query: {str(e)}"
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(error_msg)
        finally:
            if conn:
                conn.close()

    async def test_connection(self) -> bool:
        conn = None
        try:
            conn = await self.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM DUAL")
            return True
        except Exception as e:
            self.log("error", f"Connection test failed: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()

    async def cleanup(self):
        self.log("info", f"Final Oracle handler stats: {self.stats.to_dict()}")
        if hasattr(self, '_connection') and self._connection:
            try:
                self.log("debug", "Closing Oracle connection")
                self._connection.close()
                self._connection = None
            except Exception as e:
                self.log("warning", f"Error closing Oracle connection: {str(e)}")
        self.log("debug", "Oracle handler cleanup complete")