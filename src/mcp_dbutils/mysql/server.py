"""MySQL MCP server implementation"""
import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool, PooledMySQLConnection
from typing import Optional, List
import mcp.types as types
from importlib.metadata import metadata
from ..base import ConnectionServer
from ..log import create_logger
from .config import MySQLConfig

# 获取包信息用于日志命名
pkg_meta = metadata("mcp-dbutils")

class MySQLServer(ConnectionServer):
    def __init__(self, config: MySQLConfig, config_path: Optional[str] = None):
        """初始化MySQL服务器
        Args:
            config: 数据库配置
            config_path: 配置文件路径(可选)
        """
        super().__init__(config_path, config.debug)
        self.config = config
        self.config_path = config_path
        self.log = create_logger(f"{pkg_meta['Name']}.db.mysql", config.debug)
        # 创建连接池
        try:
            conn_params = config.get_connection_params()
            masked_params = config.get_masked_connection_info()
            self.log("debug", f"正在连接数据库，参数: {masked_params}")
            
            # 测试连接
            test_conn = mysql.connector.connect(**conn_params)
            test_conn.close()
            self.log("info", "测试连接成功")
            
            # 创建连接池配置
            pool_config = {
                'pool_name': 'mypool',
                'pool_size': 5,
                **conn_params
            }
            self.pool = MySQLConnectionPool(**pool_config)
            self.log("info", "连接池创建成功")
        except mysql.connector.Error as e:
            self.log("error", f"连接失败: {str(e)}")
            raise

    async def list_resources(self) -> list[types.Resource]:
        """列出所有表资源"""
        try:
            conn = self.pool.get_connection()
            with conn.cursor(dictionary=True) as cur:
                cur.execute("""
                    SELECT 
                        table_name,
                        table_comment as description
                    FROM information_schema.tables
                    WHERE table_schema = %s
                """, (self.config.database,))
                tables = cur.fetchall()
                return [
                    types.Resource(
                        uri=f"mysql://{self.config.host}/{table['table_name']}/schema",
                        name=f"{table['table_name']} schema",
                        description=table['description'] if table['description'] else None,
                        mimeType="application/json"
                    ) for table in tables
                ]
        except mysql.connector.Error as e:
            error_msg = f"获取表列表失败: {str(e)}"
            self.log("error", error_msg)
            raise
        finally:
            conn.close()

    async def read_resource(self, uri: str) -> str:
        """读取表结构信息"""
        try:
            table_name = uri.split('/')[-2]
            conn = self.pool.get_connection()
            with conn.cursor(dictionary=True) as cur:
                # 获取列信息
                cur.execute("""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_comment as description
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position
                """, (self.config.database, table_name))
                columns = cur.fetchall()

                # 获取约束信息
                cur.execute("""
                    SELECT
                        constraint_name,
                        constraint_type
                    FROM information_schema.table_constraints
                    WHERE table_schema = %s AND table_name = %s
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
            error_msg = f"读取表结构失败: {str(e)}"
            self.log("error", error_msg)
            raise
        finally:
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
        # 仅允许SELECT语句
        if not sql.lower().startswith("select"):
            raise ValueError("仅支持SELECT查询")

        connection = arguments.get("connection")
        use_pool = True
        conn = None
        try:
            if connection and self.config_path:
                # 使用指定的数据库连接
                config = MySQLConfig.from_yaml(self.config_path, connection)
                conn_params = config.get_connection_params()
                masked_params = config.get_masked_connection_info()
                self.log("info", f"使用配置 {connection} 连接数据库: {masked_params}")
                conn = mysql.connector.connect(**conn_params)
                use_pool = False
            else:
                # 使用现有连接池
                conn = self.pool.get_connection()

            self.log("info", f"执行查询: {sql}")
            with conn.cursor(dictionary=True) as cur:
                # 设置只读事务
                cur.execute("SET TRANSACTION READ ONLY")
                try:
                    cur.execute(sql)
                    results = cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    result_text = str({
                        'type': 'mysql',
                        'config_name': connection or 'default',
                        'query_result': {
                            'columns': columns,
                            'rows': results,
                            'row_count': len(results)
                        }
                    })
                    self.log("info", f"查询完成，返回{len(results)}行结果")
                    return [types.TextContent(type="text", text=result_text)]
                finally:
                    cur.execute("ROLLBACK")
        except Exception as e:
            error = f"查询执行失败: {str(e)}"
            error_msg = str({
                'type': 'mysql',
                'config_name': connection or 'default',
                'error': error
            })
            self.log("error", error_msg)
            return [types.TextContent(type="text", text=error_msg)]
        finally:
            if conn:
                if isinstance(conn, PooledMySQLConnection):
                    conn.close()  # 返回到连接池
                else:
                    conn.close()  # 关闭独立连接

    async def cleanup(self):
        """清理资源"""
        if hasattr(self, 'pool'):
            self.log("info", "关闭连接池")
            # MySQL连接池没有直接的closeall方法
            # 当对象被销毁时，连接池会自动关闭
