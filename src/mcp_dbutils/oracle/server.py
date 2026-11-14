"""Oracle MCP server implementation"""
import asyncio
from typing import Optional
import mcp.types as types
import oracledb

from ..base import LOG_NAME, ConnectionHandlerError, ConnectionServer
from ..log import create_logger
from .config import OracleConfig

class OracleServer(ConnectionServer):
    _lock = asyncio.Lock()
    
    def __init__(self, config: OracleConfig, config_path: Optional[str] = None):
        super().__init__(config_path, config.debug)
        self.config = config
        self.config_path = config_path
        self.log = create_logger(f"{LOG_NAME}.db.oracle", config.debug)
        # Oracle 官方驱动自带连接池，简单场景可直接用 connect
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
                self.log_error(f"Could not initialize Oracle Client: {e}")
                self.log_warn("Falling back to thin mode")
                self.thick_mode = False

    async def initialize_pool(self, connection_string: str):
        """Initialize the connection pool"""
        async with OracleServer._lock:
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
                
    async def get_connection(self, oracle_config: dict) -> oracledb.Connection:
        # 这里可扩展为连接池，当前直接 connect
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

    async def list_resources(self) -> list[types.Resource]:
        """列出所有表资源"""
        conn = None
        try:
            conn = await self.get_connection(self.config.get_connection_params())
            cur = conn.cursor()
            cur.execute("""
                SELECT table_name FROM user_tables
            """)
            tables = cur.fetchall()
            return [
                types.Resource(
                    uri=f"oracle://{self.config.host}/{row[0]}/schema",
                    name=f"{row[0]} schema",
                    description=None,
                    mimeType="application/json"
                ) for row in tables
            ]
        except Exception as e:
            error_msg = f"获取表列表失败: {str(e)}"
            self.log("error", error_msg)
            raise
        finally:
            if conn:
                conn.close()

    async def read_resource(self, uri: str) -> str:
        """读取表结构信息"""
        conn = None
        try:
            table_name = uri.split('/')[-2]
            conn = await self.get_connection(self.config.get_connection_params())
            cur = conn.cursor()
            # 获取列信息
            cur.execute("""
                SELECT
                    column_name,
                    data_type,
                    nullable
                FROM user_tab_columns
                WHERE table_name = :1
                ORDER BY column_id
            """, [table_name.upper()])
            columns = cur.fetchall()

            # 获取约束信息（格式与MySQL一致，见前面handler实现）
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
            error_msg = f"读取表结构失败: {str(e)}"
            self.log("error", error_msg)
            raise
        finally:
            if conn:
                conn.close()

    def get_tools(self) -> list[types.Tool]:
        """获取可用工具列表"""
        return [
            types.Tool(
                name="query",
                description="执行只读SQL查询",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection": {
                            "type": "string",
                            "description": "数据库连接名称（可选）"
                        },
                        "sql": {
                            "type": "string",
                            "description": "SQL查询语句（仅支持SELECT）"
                        }
                    },
                    "required": ["sql"]
                }
            )
        ]

    async def call_tool(self, name: str, arguments: dict) -> list[types.TextContent]:
        """执行工具调用"""
        if name != "query":
            raise ValueError(f"未知工具: {name}")
        sql = arguments.get("sql", "").strip()
        if not sql:
            raise ValueError("SQL查询不能为空")
        if not sql.lower().startswith("select"):
            raise ValueError("仅支持SELECT查询")

        connection = arguments.get("connection")
        conn = None
        results = []
        columns = []

        try:
            if connection and self.config_path:
                # 使用指定的数据库连接
                config = OracleConfig.from_yaml(self.config_path, connection)
                conn_params = config.get_connection_params()
                masked_params = {**conn_params, "password": "***"}
                self.log("info", f"使用配置 {connection} 连接数据库: {masked_params}")
                conn = await self.get_connection(conn_params)
                self.log("info", f"连接成功，使用配置: {masked_params}")
            else:
                # 使用当前配置
                conn = await self.get_connection(self.config.get_connection_params())

            self.log("info", f"执行查询: {sql}")
            cur = conn.cursor()
            try:
                cur.execute(sql)
                results = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
            finally:
                cur.close()

            result_text = str({
                'type': 'oracle',
                'config_name': connection or 'default',
                'query_result': {
                    'columns': columns,
                    'rows': results,
                    'row_count': len(results)
                }
            })
            self.log("info", f"查询完成，返回{len(results)}行结果")
            return [types.TextContent(type="text", text=result_text)]

        except Exception as e:
            error = f"查询执行失败: {str(e)}"
            error_msg = str({
                'type': 'oracle',
                'config_name': connection or 'default',
                'error': error
            })
            self.log("error", error_msg)
            return [types.TextContent(type="text", text=error_msg)]
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    self.log("warning", f"关闭连接时出错: {str(e)}")

    async def cleanup(self):
        """清理资源"""
        self.log("info", "Oracle连接无需显式清理")