"""
Redis连接实现

这个模块实现了Redis数据库的连接类。
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError

from ..error.exceptions import ConnectionError, TransactionError
from .base import ConnectionBase


class RedisConnection(ConnectionBase):
    """
    Redis连接类

    这个类实现了与Redis数据库的连接管理。
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化Redis连接

        Args:
            config: 连接配置，包含连接参数
                - host: 主机名
                - port: 端口号
                - database: 数据库索引
                - username: 用户名
                - password: 密码
                - ssl: SSL配置
                - timeout: 连接超时时间
                - decode_responses: 是否解码响应
        """
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.pipeline = None

    def connect(self) -> None:
        """
        建立连接

        建立到Redis数据库的连接，如果连接已经存在，则重用现有连接。

        Raises:
            ConnectionError: 如果连接失败
        """
        if self.is_connected():
            return

        try:
            # 构建连接参数
            connection_params = {
                'host': self.config.get('host', 'localhost'),
                'port': self.config.get('port', 6379),
                'db': self.config.get('database', 0),
                'decode_responses': self.config.get('decode_responses', True),
                'socket_timeout': self.config.get('timeout', 5),
                'socket_connect_timeout': self.config.get('connect_timeout', 5),
            }

            # 添加认证信息
            if 'password' in self.config:
                connection_params['password'] = self.config['password']

            if 'username' in self.config:
                connection_params['username'] = self.config['username']

            # 添加SSL配置
            if self.config.get('ssl', False):
                connection_params['ssl'] = True
                connection_params['ssl_cert_reqs'] = self.config.get('ssl_cert_reqs', None)

            # 创建Redis客户端
            self.client = redis.Redis(**connection_params)

            # 测试连接
            self.client.ping()

            self.logger.info(f"Connected to Redis at {connection_params['host']}:{connection_params['port']}")

        except RedisConnectionError as e:
            self.client = None
            raise ConnectionError(f"Failed to connect to Redis: {str(e)}")
        except Exception as e:
            self.client = None
            raise ConnectionError(f"Unexpected error connecting to Redis: {str(e)}")

    def disconnect(self) -> None:
        """
        断开连接

        断开与Redis数据库的连接，释放资源。
        如果有活动的事务，会先回滚事务。
        """
        if self.is_connected():
            try:
                if self.is_transaction_active:
                    self.rollback()

                if self.client:
                    self.client.close()
                    self.client = None
                    self.logger.info("Disconnected from Redis")
            except Exception as e:
                self.logger.error(f"Error disconnecting from Redis: {str(e)}")

    def is_connected(self) -> bool:
        """
        检查连接状态

        Returns:
            bool: 如果连接是活动的，则返回True，否则返回False
        """
        if not self.client:
            return False

        try:
            # 尝试执行ping命令检查连接
            self.client.ping()
            return True
        except Exception:
            return False

    def execute(self, command: str, params: Optional[List[Any]] = None) -> Any:
        """
        执行Redis命令

        执行给定的Redis命令。

        Args:
            command: Redis命令
            params: 命令参数

        Returns:
            命令结果

        Raises:
            ConnectionError: 如果执行命令时发生错误
        """
        if not self.is_connected():
            self.connect()

        try:
            # 如果在事务中，使用pipeline执行命令
            if self.is_transaction_active and self.pipeline:
                method = getattr(self.pipeline, command.lower(), None)
                if not method:
                    raise ConnectionError(f"Unsupported Redis command: {command}")

                if params:
                    return method(*params)
                else:
                    return method()
            else:
                # 否则，直接使用client执行命令
                method = getattr(self.client, command.lower(), None)
                if not method:
                    raise ConnectionError(f"Unsupported Redis command: {command}")

                if params:
                    return method(*params)
                else:
                    return method()

        except RedisError as e:
            raise ConnectionError(f"Redis command execution error: {str(e)}")
        except Exception as e:
            raise ConnectionError(f"Unexpected error executing Redis command: {str(e)}")

    def begin_transaction(self) -> None:
        """
        开始事务

        开始一个新的事务。如果已经有一个活动的事务，则抛出异常。

        Raises:
            TransactionError: 如果已经有一个活动的事务
        """
        if not self.is_connected():
            self.connect()

        if self.is_transaction_active:
            raise TransactionError("Transaction already active")

        try:
            # 创建pipeline并开始事务
            self.pipeline = self.client.pipeline(transaction=True)
            self.is_transaction_active = True
            self.logger.info("Redis transaction started")

        except RedisError as e:
            self.pipeline = None
            self.is_transaction_active = False
            raise TransactionError(f"Failed to start Redis transaction: {str(e)}")

    def commit(self) -> None:
        """
        提交事务

        提交当前活动的事务。如果没有活动的事务，则抛出异常。

        Raises:
            TransactionError: 如果没有活动的事务
        """
        if not self.is_transaction_active or not self.pipeline:
            raise TransactionError("No active transaction to commit")

        try:
            # 执行pipeline中的所有命令
            result = self.pipeline.execute()
            self.logger.info("Redis transaction committed")
            return result

        except RedisError as e:
            raise TransactionError(f"Failed to commit Redis transaction: {str(e)}")
        finally:
            self.pipeline = None
            self.is_transaction_active = False

    def rollback(self) -> None:
        """
        回滚事务

        回滚当前活动的事务。如果没有活动的事务，则抛出异常。

        Raises:
            TransactionError: 如果没有活动的事务
        """
        if not self.is_transaction_active or not self.pipeline:
            raise TransactionError("No active transaction to rollback")

        try:
            # Redis的pipeline不支持显式回滚，只能重置pipeline
            self.pipeline.reset()
            self.logger.info("Redis transaction rolled back")

        except RedisError as e:
            self.logger.error(f"Error rolling back Redis transaction: {str(e)}")
        finally:
            self.pipeline = None
            self.is_transaction_active = False
