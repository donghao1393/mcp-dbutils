"""PostgreSQL MCP server implementation"""
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from typing import Optional, List
import mcp.types as types
from importlib.metadata import metadata
from ..base import ConnectionServer
from ..log import create_logger
from .config import PostgreSQLConfig

# 获取包信息用于日志命名
pkg_meta = metadata("mcp-dbutils")
class PostgreSQLServer(ConnectionServer):
    def __init__(self, config: PostgreSQLConfig, config_path: Optional[str] = None):
        """初始化PostgreSQL服务器
        Args:
            config: 数据库配置
            config_path: 配置文件路径(可选)
        """
        super().__init__(config_path, config.debug)
        self.config = config
        self.config_path = config_path
        self.log = create_logger(f"{pkg_meta['Name']}.db.postgres", config.debug)
        # 创建连接池
        try:
            conn_params = config.get_connection_params()
            masked_params = config.get_masked_connection_info()
            self.log("debug", f"正在连接数据库，参数: {masked_params}")
            # 测试连接
            test_conn = psycopg2.connect(**conn_params)
            test_conn.close()
            self.log("info", "测试连接成功")
            # 创建连接池
            self.pool = SimpleConnectionPool(1, 5, **conn_params)
            self.log("info", "连接池创建成功")
        except psycopg2.Error as e:
            self.log("error", f"连接失败: [Code: {e.pgcode}] {e.pgerror or str(e)}")
            raise
    async def list_resources(self) -> list[types.Resource]:
        """列出所有表资源"""
        try:
            conn = self.pool.getconn()
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
                        uri=f"postgres://{self.config.host}/{table[0]}/schema",
                        name=f"{table[0]} schema",
                        description=table[1] if table[1] else None,
                        mimeType="application/json"
                    ) for table in tables
                ]
        except psycopg2.Error as e:
            error_msg = f"获取表列表失败: [Code: {e.pgcode}] {e.pgerror or str(e)}"
            self.log("error", error_msg)
            raise
        finally:
            self.pool.putconn(conn)
    async def read_resource(self, uri: str) -> str:
        """读取表结构信息"""
        try:
            table_name = uri.split('/')[-2]
            conn = self.pool.getconn()
            with conn.cursor() as cur:
                # 获取列信息
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
                # 获取约束信息
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
            error_msg = f"读取表结构失败: [Code: {e.pgcode}] {e.pgerror or str(e)}"
            self.log("error", error_msg)
            raise
        finally:
            self.pool.putconn(conn)
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
        # 仅允许SELECT语句
        if not sql.lower().startswith("select"):
            raise ValueError("仅支持SELECT查询")
        connection = arguments.get("connection")
        use_pool = True
        conn = None
        try:
            if connection and self.config_path:
                # 使用指定的数据库连接
                config = PostgreSQLConfig.from_yaml(self.config_path, connection)
                conn_params = config.get_connection_params()
                masked_params = config.get_masked_connection_info()
                self.log("info", f"使用配置 {connection} 连接数据库: {masked_params}")
                conn = psycopg2.connect(**conn_params)
                use_pool = False
            else:
                # 使用现有连接池
                conn = self.pool.getconn()
            self.log("info", f"执行查询: {sql}")
            with conn.cursor() as cur:
                # 启动只读事务
                cur.execute("BEGIN TRANSACTION READ ONLY")
                try:
                    cur.execute(sql)
                    results = cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    formatted_results = [dict(zip(columns, row)) for row in results]
                    result_text = str({
                        'type': 'postgres',
                        'config_name': connection or 'default',
                        'query_result': {
                            'columns': columns,
                            'rows': formatted_results,
                            'row_count': len(results)
                        }
                    })
                    self.log("info", f"查询完成，返回{len(results)}行结果")
                    return [types.TextContent(type="text", text=result_text)]
                finally:
                    cur.execute("ROLLBACK")
        except Exception as e:
            if isinstance(e, psycopg2.Error):
                error = f"查询执行失败: [Code: {e.pgcode}] {e.pgerror or str(e)}"
            else:
                error = f"查询执行失败: {str(e)}"
            error_msg = str({
                'type': 'postgres',
                'config_name': connection or 'default',
                'error': error
            })
            self.log("error", error_msg)
            return [types.TextContent(type="text", text=error_msg)]
        finally:
            if conn:
                if use_pool:
                    self.pool.putconn(conn)
                else:
                    conn.close()
    async def cleanup(self):
        """清理资源"""
        if hasattr(self, 'pool'):
            self.log("info", "关闭连接池")
            self.pool.closeall()
