"""SQLite MCP server implementation"""

import sqlite3
from pathlib import Path
from contextlib import closing
from typing import Optional, List
import mcp.types as types
from importlib.metadata import metadata

from ..base import ConnectionServer
from ..log import create_logger
from .config import SQLiteConfig

# 获取包信息用于日志命名
pkg_meta = metadata("mcp-dbutils")

class SQLiteServer(ConnectionServer):
    def __init__(self, config: SQLiteConfig, config_path: Optional[str] = None):
        """初始化 SQLite 服务器

        Args:
            config: SQLite 配置
        """
        super().__init__(config_path, config.debug)
        self.config = config
        self.config_path = config_path
        self.log = create_logger(f"{pkg_meta['Name']}.db.sqlite", config.debug)

        # 确保数据库目录存在
        db_file = Path(self.config.absolute_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        # 测试连接
        try:
            self.log("debug", f"正在连接: {self.config.get_masked_connection_info()}")
            connection_params = self.config.get_connection_params()
            with closing(sqlite3.connect(**connection_params)) as conn:
                conn.row_factory = sqlite3.Row
            self.log("info", "连接测试成功")
        except sqlite3.Error as e:
            self.log("error", f"连接失败: {str(e)}")
            raise

    def _get_connection(self):
        """获取数据库连接"""
        connection_params = self.config.get_connection_params()
        conn = sqlite3.connect(**connection_params)
        conn.row_factory = sqlite3.Row
        return conn

    async def list_resources(self) -> list[types.Resource]:
        """列出所有表资源"""
        use_default = True
        conn = None
        try:
            connection = arguments.get("connection")
            if connection and self.config_path:
                # 使用指定的数据库连接
                config = SQLiteConfig.from_yaml(self.config_path, connection)
                connection_params = config.get_connection_params()
                masked_params = config.get_masked_connection_info()
                self.log("info", f"使用配置 {connection} 连接: {masked_params}")
                conn = sqlite3.connect(**connection_params)
                conn.row_factory = sqlite3.Row
                use_default = False
            else:
                # 使用默认连接
                conn = self._get_connection()

            with closing(conn) as connection:
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                tables = cursor.fetchall()

                return [
                    types.Resource(
                        uri=f"sqlite://{table[0]}/schema",
                        name=f"{table[0]} schema",
                        mimeType="application/json"
                    ) for table in tables
                ]
        except sqlite3.Error as e:
            error_msg = f"获取表列表失败: {str(e)}"
            self.log("error", error_msg)
            raise

    async def read_resource(self, uri: str) -> str:
        """读取表结构信息"""
        try:
            table_name = uri.split('/')[-2]
            with closing(self._get_connection()) as conn:
                # 获取表结构
                cursor = conn.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()

                # 获取索引信息
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
            error_msg = f"读取表结构失败: {str(e)}"
            self.log("error", error_msg)
            raise

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

        use_default = True
        conn = None
        try:
            connection = arguments.get("connection")
            if connection and self.config_path:
                # 使用指定的数据库连接
                config = SQLiteConfig.from_yaml(self.config_path, connection)
                connection_params = config.get_connection_params()
                masked_params = config.get_masked_connection_info()
                self.log("info", f"使用配置 {connection} 连接: {masked_params}")
                conn = sqlite3.connect(**connection_params)
                conn.row_factory = sqlite3.Row
                use_default = False
            else:
                # 使用默认连接
                conn = self._get_connection()

            with closing(conn) as connection:
                self.log("info", f"执行查询: {sql}")
                cursor = conn.execute(sql)
                results = cursor.fetchall()

                columns = [desc[0] for desc in cursor.description]
                formatted_results = [dict(zip(columns, row)) for row in results]

                result_text = str({
                    'type': 'sqlite',
                    'config_name': connection or 'default',
                    'query_result': {
                        'columns': columns,
                        'rows': formatted_results,
                        'row_count': len(results)
                    }
                })

                self.log("info", f"查询完成，返回{len(results)}行结果")
                return [types.TextContent(type="text", text=result_text)]

        except sqlite3.Error as e:
            error_msg = str({
                'type': 'sqlite',
                'config_name': connection or 'default',
                'error': f"查询执行失败: {str(e)}"
            })
            self.log("error", error_msg)
            return [types.TextContent(type="text", text=error_msg)]

    async def cleanup(self):
        """清理资源"""
        # SQLite不需要特别的清理操作
        pass
