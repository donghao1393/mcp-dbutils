"""
MongoDB适配器实现

这个模块实现了MongoDB的适配器，将ConnectionHandler接口适配到新架构的ConnectionBase和AdapterBase。
"""

from typing import Any, Dict, List

import mcp.types as types

from ..adapter import MULTI_DB_AVAILABLE, AdaptedConnectionHandler
from ..base import ConnectionHandlerError
from .config import MongoDBConfig


class AdaptedMongoDBHandler(AdaptedConnectionHandler):
    """
    MongoDB适配器实现

    这个类继承自AdaptedConnectionHandler，实现了MongoDB特定的适配逻辑。
    """

    @property
    def db_type(self) -> str:
        """
        返回数据库类型

        Returns:
            str: 数据库类型
        """
        return 'mongodb'

    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置

        从配置文件加载MongoDB配置，并转换为新架构的配置格式。

        Returns:
            Dict[str, Any]: 新架构的配置
        """
        config = MongoDBConfig.from_yaml(self.config_path, self.connection)
        return {
            'type': 'mongodb',
            'host': config.host,
            'port': int(config.port),
            'database': config.database,
            'username': config.username,
            'password': config.password,
            'auth_source': config.auth_source,
            'uri': config.uri,
            'debug': config.debug,
            'writable': config.writable,
            'write_permissions': config.write_permissions.to_dict() if config.write_permissions else None,
        }

    async def get_tables(self) -> list[types.Resource]:
        """
        获取集合资源列表

        Returns:
            list[types.Resource]: 集合资源列表

        Raises:
            ConnectionHandlerError: 如果获取集合列表失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 使用适配器的list_resources方法获取集合列表
            collections = adapter.list_resources()

            # 转换为Resource对象
            return [
                types.Resource(
                    uri=f"mongodb://{self.connection}/{collection['name']}/schema",
                    name=f"{collection['name']} schema",
                    description=f"Documents: {collection['count']}, Size: {collection['size']} bytes",
                    mimeType="application/json"
                ) for collection in collections
            ]
        except Exception as e:
            self.log("error", f"Failed to get collections: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get collections: {str(e)}")

    async def get_schema(self, collection_name: str) -> str:
        """
        获取集合结构信息

        Args:
            collection_name: 集合名

        Returns:
            str: 集合结构信息

        Raises:
            ConnectionHandlerError: 如果获取集合结构失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 使用适配器的describe_resource方法获取集合结构
            collection_info = adapter.describe_resource(collection_name)

            # 转换为字典格式
            schema = {
                'name': collection_info['name'],
                'type': collection_info['type'],
                'fields': collection_info['fields'],
                'indexes': collection_info['indexes'],
            }

            return str(schema)
        except Exception as e:
            self.log("error", f"Failed to get schema for collection {collection_name}: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get schema for collection {collection_name}: {str(e)}")

    async def _execute_query(self, query_str: str) -> str:
        """
        执行MongoDB查询

        Args:
            query_str: MongoDB查询字符串（JSON格式）

        Returns:
            str: 查询结果

        Raises:
            ConnectionHandlerError: 如果执行查询失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 解析查询字符串为字典
            import json
            query = json.loads(query_str)

            # 执行查询
            result = adapter.execute_query(query)

            # 格式化结果
            return self._format_result(result)
        except Exception as e:
            self.log("error", f"Failed to execute query: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to execute query: {str(e)}")

    async def _execute_write_query(self, query_str: str) -> str:
        """
        执行MongoDB写操作

        Args:
            query_str: MongoDB写操作字符串（JSON格式）

        Returns:
            str: 操作结果

        Raises:
            ConnectionHandlerError: 如果执行写操作失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 解析查询字符串为字典
            import json
            query = json.loads(query_str)

            # 执行写操作
            result = adapter.execute_write(query)

            # 格式化结果
            return self._format_result(result)
        except Exception as e:
            self.log("error", f"Failed to execute write operation: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to execute write operation: {str(e)}")

    def _format_result(self, result: Any) -> str:
        """
        格式化结果

        将新架构的结果格式转换为ConnectionHandler的结果格式。

        Args:
            result: 新架构的结果

        Returns:
            str: 格式化后的结果
        """
        # 如果结果是列表或字典，直接转换为字符串
        return str(result)

    async def get_table_description(self, collection_name: str) -> str:
        """
        获取集合描述信息

        Args:
            collection_name: 集合名

        Returns:
            str: 集合描述信息

        Raises:
            ConnectionHandlerError: 如果获取集合描述失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 使用适配器的describe_resource方法获取集合结构
            collection_info = adapter.describe_resource(collection_name)

            # 格式化输出
            description = [
                f"Collection: {collection_info['name']}",
                f"Type: {collection_info['type']}",
                f"Document Count: {collection_info['count']}",
                f"Size: {collection_info['size']} bytes",
                f"Average Object Size: {collection_info['avg_obj_size']} bytes",
                f"Storage Size: {collection_info['storage_size']} bytes",
                f"Index Size: {collection_info['index_size']} bytes",
                f"Total Size: {collection_info['total_size']} bytes\n",
                "Fields:"
            ]

            # 添加字段信息
            for field in collection_info['fields']:
                field_info = [
                    f"  {field['name']} ({field['type']})",
                    f"    Sample Value: {field['sample_value']}"
                ]
                description.extend(field_info)
                description.append("")  # 空行分隔字段

            # 添加索引信息
            description.append("Indexes:")
            for index in collection_info['indexes']:
                index_info = [
                    f"  {index['name']}:",
                    f"    Unique: {index['unique']}",
                    f"    Columns: {', '.join(index['columns'])}",
                    f"    Directions: {', '.join([str(d) for d in index['directions']])}"
                ]
                description.extend(index_info)
                description.append("")  # 空行分隔索引

            return "\n".join(description)
        except Exception as e:
            self.log("error", f"Failed to get description for collection {collection_name}: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get description for collection {collection_name}: {str(e)}")

    async def get_table_stats(self, collection_name: str) -> str:
        """
        获取集合统计信息

        Args:
            collection_name: 集合名

        Returns:
            str: 集合统计信息

        Raises:
            ConnectionHandlerError: 如果获取集合统计失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 使用适配器的get_resource_stats方法获取集合统计信息
            stats = adapter.get_resource_stats(collection_name)

            # 格式化输出
            output = [
                f"Collection Statistics for {collection_name}:",
                f"  Document Count: {stats['count']:,}",
                f"  Size: {stats['size']:,} bytes",
                f"  Average Object Size: {stats['avg_obj_size']:,.1f} bytes",
                f"  Storage Size: {stats['storage_size']:,} bytes",
                f"  Index Size: {stats['index_size']:,} bytes",
                f"  Total Size: {stats['total_size']:,} bytes"
            ]

            return "\n".join(output)
        except Exception as e:
            self.log("error", f"Failed to get statistics for collection {collection_name}: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get statistics for collection {collection_name}: {str(e)}")

    async def get_table_indexes(self, collection_name: str) -> str:
        """
        获取集合索引信息

        Args:
            collection_name: 集合名

        Returns:
            str: 集合索引信息

        Raises:
            ConnectionHandlerError: 如果获取集合索引失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 使用适配器的describe_resource方法获取集合结构
            collection_info = adapter.describe_resource(collection_name)

            # 获取索引信息
            indexes = collection_info['indexes']

            if not indexes:
                return f"No indexes found on collection {collection_name}"

            # 格式化输出
            output = [f"Indexes for collection {collection_name}:"]

            for index in indexes:
                index_info = [
                    f"\nIndex: {index['name']}",
                    f"  Unique: {index['unique']}",
                    f"  Columns: {', '.join(index['columns'])}",
                    f"  Directions: {', '.join([str(d) for d in index['directions']])}"
                ]
                output.extend(index_info)

            return "\n".join(output)
        except Exception as e:
            self.log("error", f"Failed to get indexes for collection {collection_name}: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get indexes for collection {collection_name}: {str(e)}")

    async def explain_query(self, query_str: str) -> str:
        """
        获取查询执行计划

        Args:
            query_str: MongoDB查询字符串（JSON格式）

        Returns:
            str: 查询执行计划

        Raises:
            ConnectionHandlerError: 如果获取查询执行计划失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 解析查询字符串为字典
            import json
            query = json.loads(query_str)

            # 确保查询包含必要的字段
            if 'operation' not in query or 'collection' not in query:
                raise ConnectionHandlerError("Query must include 'operation' and 'collection' fields")

            # 只支持find和aggregate操作的执行计划
            if query['operation'] not in ['find', 'aggregate']:
                raise ConnectionHandlerError(f"Explain is only supported for 'find' and 'aggregate' operations, got '{query['operation']}'")

            # 添加explain选项
            explain_query = query.copy()
            if 'params' not in explain_query:
                explain_query['params'] = {}

            # 对于find操作，添加explain选项
            if query['operation'] == 'find':
                # 创建一个新的查询，使用aggregate和$explain阶段
                explain_query = {
                    'operation': 'aggregate',
                    'collection': query['collection'],
                    'params': {
                        'pipeline': [
                            {'$match': query.get('params', {}).get('filter', {})},
                            {'$explain': {}}
                        ]
                    }
                }
            # 对于aggregate操作，添加$explain阶段
            elif query['operation'] == 'aggregate':
                pipeline = explain_query['params'].get('pipeline', [])
                explain_query['params']['pipeline'] = pipeline + [{'$explain': {}}]

            # 执行查询
            result = adapter.execute_query(explain_query)

            # 格式化输出
            output = ["Query Execution Plan:"]
            output.append(json.dumps(result, indent=2))

            return "\n".join(output)
        except Exception as e:
            self.log("error", f"Failed to explain query: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to explain query: {str(e)}")

    async def test_connection(self) -> bool:
        """
        测试数据库连接

        Returns:
            bool: 如果连接成功，则返回True，否则返回False
        """
        try:
            # 只需要确保连接可以建立，不需要使用连接对象
            self._ensure_connection()
            return True
        except Exception as e:
            self.log("error", f"Connection test failed: {str(e)}")
            return False

    async def cleanup(self):
        """
        清理资源

        关闭连接并清理资源。
        """
        # 记录最终统计信息
        self.log("info", f"Final handler stats: {self.stats.to_dict()}")

        # 关闭连接
        if self._connection and hasattr(self._connection, 'is_connected') and self._connection.is_connected():
            try:
                self.log("debug", f"Closing {self.db_type} connection")
                self._connection.disconnect()
                self._connection = None
                self._adapter = None
            except Exception as e:
                self.log("warning", f"Error closing {self.db_type} connection: {str(e)}")

        # 清理其他资源
        self.log("debug", f"{self.db_type} handler cleanup complete")
