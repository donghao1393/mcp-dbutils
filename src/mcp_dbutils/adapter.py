"""
适配层：将ConnectionHandler接口适配到新架构

这个模块实现了适配层，将ConnectionHandler接口适配到新架构的ConnectionBase和AdapterBase。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

import mcp.types as types

from .base import ConnectionHandler, ConnectionHandlerError

# 为了避免在测试时导入MongoDB和Redis，我们使用try-except
try:
    from .multi_db.adapter.base import AdapterBase
    from .multi_db.adapter.factory import AdapterFactory
    from .multi_db.connection.base import ConnectionBase
    from .multi_db.connection.factory import ConnectionFactory
    from .multi_db.error.exceptions import ConnectionError as MultiDBConnectionError
    from .multi_db.error.exceptions import DatabaseError, TransactionError
    MULTI_DB_AVAILABLE = True
except ImportError:
    # 在测试环境中，我们可能没有安装MongoDB和Redis
    # 定义一些占位符类，以便测试可以运行
    class AdapterBase:
        pass

    class AdapterFactory:
        def create_adapter(self, connection):
            return None

    class ConnectionBase:
        pass

    class ConnectionFactory:
        def create_connection(self, config):
            return None

    class MultiDBConnectionError(Exception):
        pass

    class DatabaseError(Exception):
        pass

    class TransactionError(Exception):
        pass

    MULTI_DB_AVAILABLE = False


class AdaptedConnectionHandler(ConnectionHandler, ABC):
    """
    适配层：将ConnectionHandler接口适配到新架构

    这个类继承自ConnectionHandler，但内部使用新架构的ConnectionBase和AdapterBase
    """

    def __init__(self, config_path: str, connection: str, debug: bool = False):
        """
        初始化适配的连接处理器

        Args:
            config_path: 配置文件路径
            connection: 连接名称
            debug: 是否启用调试模式
        """
        super().__init__(config_path, connection, debug)
        # 创建连接工厂
        self.connection_factory = ConnectionFactory()
        # 创建适配器工厂
        self.adapter_factory = AdapterFactory()
        # 连接和适配器实例将在需要时创建
        self._connection = None
        self._adapter = None

    @abstractmethod
    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置

        从配置文件加载配置，并转换为新架构的配置格式。

        Returns:
            Dict[str, Any]: 新架构的配置
        """
        pass

    def _ensure_connection(self) -> Tuple[ConnectionBase, AdapterBase]:
        """
        确保连接已创建并连接

        如果连接尚未创建，则创建连接和适配器。
        如果连接已创建但未连接，则建立连接。

        Returns:
            Tuple[ConnectionBase, AdapterBase]: 连接和适配器

        Raises:
            ConnectionHandlerError: 如果创建连接或适配器失败
        """
        if not self._connection:
            try:
                # 从配置文件加载配置
                config = self._load_config()
                # 创建连接
                self._connection = self.connection_factory.create_connection(config)
                # 创建适配器
                self._adapter = self.adapter_factory.create_adapter(self._connection)
            except (DatabaseError, Exception) as e:
                self.log("error", f"Failed to create connection or adapter: {str(e)}")
                self.stats.record_error(e.__class__.__name__)
                raise ConnectionHandlerError(f"Failed to create connection or adapter: {str(e)}")

        # 确保连接已建立
        try:
            if not self._connection.is_connected():
                self._connection.connect()
        except MultiDBConnectionError as e:
            self.log("error", f"Failed to connect: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to connect: {str(e)}")

        return self._connection, self._adapter

    def _format_result(self, result: Any) -> str:
        """
        格式化结果

        将新架构的结果格式转换为ConnectionHandler的结果格式。

        Args:
            result: 新架构的结果

        Returns:
            str: 格式化后的结果
        """
        # 默认实现，子类可以覆盖
        return str(result)

    async def get_tables(self) -> list[types.Resource]:
        """
        获取表资源列表

        Returns:
            list[types.Resource]: 表资源列表

        Raises:
            ConnectionHandlerError: 如果获取表列表失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 这里需要实现从新架构获取表列表的逻辑
            # 由于新架构没有直接提供获取表列表的方法，我们需要在子类中实现
            # 这里提供一个基本实现，子类可以覆盖
            return []
        except Exception as e:
            self.log("error", f"Failed to get tables: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get tables: {str(e)}")

    async def get_schema(self, table_name: str) -> str:
        """
        获取表结构信息

        Args:
            table_name: 表名

        Returns:
            str: 表结构信息

        Raises:
            ConnectionHandlerError: 如果获取表结构失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 这里需要实现从新架构获取表结构的逻辑
            # 由于新架构没有直接提供获取表结构的方法，我们需要在子类中实现
            # 这里提供一个基本实现，子类可以覆盖
            return "{}"
        except Exception as e:
            self.log("error", f"Failed to get schema for table {table_name}: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get schema for table {table_name}: {str(e)}")

    async def _execute_query(self, sql: str) -> str:
        """
        执行SQL查询

        Args:
            sql: SQL查询语句

        Returns:
            str: 查询结果

        Raises:
            ConnectionHandlerError: 如果执行查询失败
        """
        connection, adapter = self._ensure_connection()
        try:
            result = adapter.execute_query(sql)
            return self._format_result(result)
        except Exception as e:
            self.log("error", f"Failed to execute query: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to execute query: {str(e)}")

    async def _execute_write_query(self, sql: str) -> str:
        """
        执行SQL写入操作

        Args:
            sql: SQL写入语句

        Returns:
            str: 执行结果

        Raises:
            ConnectionHandlerError: 如果执行写入操作失败
        """
        connection, adapter = self._ensure_connection()
        try:
            result = adapter.execute_write(sql)
            return self._format_result(result)
        except Exception as e:
            self.log("error", f"Failed to execute write query: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to execute write query: {str(e)}")

    async def get_table_description(self, table_name: str) -> str:
        """
        获取表描述信息

        Args:
            table_name: 表名

        Returns:
            str: 表描述信息

        Raises:
            ConnectionHandlerError: 如果获取表描述失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 这里需要实现从新架构获取表描述的逻辑
            # 由于新架构没有直接提供获取表描述的方法，我们需要在子类中实现
            # 这里提供一个基本实现，子类可以覆盖
            return f"Description of {table_name}"
        except Exception as e:
            self.log("error", f"Failed to get description for table {table_name}: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get description for table {table_name}: {str(e)}")

    async def get_table_ddl(self, table_name: str) -> str:
        """
        获取表DDL语句

        Args:
            table_name: 表名

        Returns:
            str: 表DDL语句

        Raises:
            ConnectionHandlerError: 如果获取表DDL失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 这里需要实现从新架构获取表DDL的逻辑
            # 由于新架构没有直接提供获取表DDL的方法，我们需要在子类中实现
            # 这里提供一个基本实现，子类可以覆盖
            return f"DDL for {table_name}"
        except Exception as e:
            self.log("error", f"Failed to get DDL for table {table_name}: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get DDL for table {table_name}: {str(e)}")

    async def get_table_indexes(self, table_name: str) -> str:
        """
        获取表索引信息

        Args:
            table_name: 表名

        Returns:
            str: 表索引信息

        Raises:
            ConnectionHandlerError: 如果获取表索引失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 这里需要实现从新架构获取表索引的逻辑
            # 由于新架构没有直接提供获取表索引的方法，我们需要在子类中实现
            # 这里提供一个基本实现，子类可以覆盖
            return f"Indexes for {table_name}"
        except Exception as e:
            self.log("error", f"Failed to get indexes for table {table_name}: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get indexes for table {table_name}: {str(e)}")

    async def get_table_stats(self, table_name: str) -> str:
        """
        获取表统计信息

        Args:
            table_name: 表名

        Returns:
            str: 表统计信息

        Raises:
            ConnectionHandlerError: 如果获取表统计失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 这里需要实现从新架构获取表统计的逻辑
            # 由于新架构没有直接提供获取表统计的方法，我们需要在子类中实现
            # 这里提供一个基本实现，子类可以覆盖
            return f"Statistics for {table_name}"
        except Exception as e:
            self.log("error", f"Failed to get statistics for table {table_name}: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get statistics for table {table_name}: {str(e)}")

    async def get_table_constraints(self, table_name: str) -> str:
        """
        获取表约束信息

        Args:
            table_name: 表名

        Returns:
            str: 表约束信息

        Raises:
            ConnectionHandlerError: 如果获取表约束失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 这里需要实现从新架构获取表约束的逻辑
            # 由于新架构没有直接提供获取表约束的方法，我们需要在子类中实现
            # 这里提供一个基本实现，子类可以覆盖
            return f"Constraints for {table_name}"
        except Exception as e:
            self.log("error", f"Failed to get constraints for table {table_name}: {str(e)}")
            self.stats.record_error(e.__class__.__name__)
            raise ConnectionHandlerError(f"Failed to get constraints for table {table_name}: {str(e)}")

    async def explain_query(self, sql: str) -> str:
        """
        获取查询执行计划

        Args:
            sql: SQL查询语句

        Returns:
            str: 查询执行计划

        Raises:
            ConnectionHandlerError: 如果获取查询执行计划失败
        """
        connection, adapter = self._ensure_connection()
        try:
            # 这里需要实现从新架构获取查询执行计划的逻辑
            # 由于新架构没有直接提供获取查询执行计划的方法，我们需要在子类中实现
            # 这里提供一个基本实现，子类可以覆盖
            return f"Execution plan for: {sql}"
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
            connection, adapter = self._ensure_connection()
            return True
        except Exception as e:
            self.log("error", f"Connection test failed: {str(e)}")
            return False

    async def cleanup(self):
        """
        清理资源

        关闭连接并清理资源。
        """
        # Log final stats before cleanup
        self.log("info", f"Final handler stats: {self.stats.to_dict()}")

        # 关闭连接
        if self._connection and self._connection.is_connected():
            try:
                self.log("debug", f"Closing {self.db_type} connection")
                self._connection.disconnect()
                self._connection = None
                self._adapter = None
            except Exception as e:
                self.log("warning", f"Error closing {self.db_type} connection: {str(e)}")

        # 清理其他资源
        self.log("debug", f"{self.db_type} handler cleanup complete")