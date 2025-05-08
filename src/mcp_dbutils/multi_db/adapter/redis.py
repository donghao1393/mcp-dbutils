"""
Redis适配器实现

这个模块实现了Redis数据库的适配器。
"""

import logging
import re
from typing import Any, Dict, List, Optional

from ..connection.redis import RedisConnection
from ..error.exceptions import (
    ConnectionError,
    DatabaseError,
    QueryError,
    ResourceNotFoundError,
)
from .base import AdapterBase


class RedisAdapter(AdapterBase):
    """
    Redis适配器类

    这个类实现了Redis数据库的适配器，提供统一的操作接口。
    """

    # Redis只读命令列表
    READ_COMMANDS = {
        'get', 'mget', 'exists', 'keys', 'scan', 'type', 'ttl', 'pttl', 'strlen',
        'hget', 'hmget', 'hgetall', 'hkeys', 'hvals', 'hexists', 'hlen', 'hscan',
        'llen', 'lindex', 'lrange',
        'scard', 'sismember', 'smembers', 'sscan',
        'zcard', 'zcount', 'zrange', 'zrangebyscore', 'zrank', 'zscore', 'zscan',
        'dbsize', 'info', 'ping', 'time', 'memory', 'dump'
    }

    # Redis写命令列表
    WRITE_COMMANDS = {
        'set', 'mset', 'setex', 'setnx', 'del', 'expire', 'expireat', 'pexpire', 'pexpireat',
        'append', 'incr', 'incrby', 'incrbyfloat', 'decr', 'decrby',
        'hset', 'hmset', 'hdel', 'hincrby', 'hincrbyfloat',
        'lpush', 'lpushx', 'rpush', 'rpushx', 'lpop', 'rpop', 'lset', 'ltrim',
        'sadd', 'srem', 'spop', 'smove',
        'zadd', 'zrem', 'zincrby', 'zremrangebyrank', 'zremrangebyscore',
        'flushdb', 'flushall', 'rename', 'renamenx'
    }

    def __init__(self, connection: RedisConnection):
        """
        初始化Redis适配器

        Args:
            connection: Redis数据库连接
        """
        super().__init__(connection)
        self.logger = logging.getLogger(__name__)
        self.redis_connection = connection

    def execute_query(self, query: str, params: Optional[List[Any]] = None) -> Any:
        """
        执行Redis命令

        执行只读Redis命令。

        Args:
            query: Redis命令
            params: 命令参数

        Returns:
            命令结果

        Raises:
            QueryError: 如果执行命令时发生错误
        """
        try:
            # 验证命令是否为只读命令
            command = query.lower()
            if command not in self.READ_COMMANDS:
                raise QueryError(f"Command '{query}' is not a read command")

            # 执行命令
            return self.connection.execute(query, params)

        except ConnectionError as e:
            raise QueryError(f"Redis query execution error: {str(e)}")
        except Exception as e:
            raise QueryError(f"Unexpected error executing Redis query: {str(e)}")

    def execute_write(self, query: str, params: Optional[List[Any]] = None) -> Any:
        """
        执行Redis写命令

        执行Redis写命令。

        Args:
            query: Redis写命令
            params: 命令参数

        Returns:
            命令结果

        Raises:
            QueryError: 如果执行写命令时发生错误
        """
        try:
            # 验证命令是否为写命令
            command = query.lower()
            if command not in self.WRITE_COMMANDS:
                raise QueryError(f"Command '{query}' is not a write command")

            # 执行命令
            return self.connection.execute(query, params)

        except ConnectionError as e:
            raise QueryError(f"Redis write command execution error: {str(e)}")
        except Exception as e:
            raise QueryError(f"Unexpected error executing Redis write command: {str(e)}")

    def list_resources(self) -> List[Dict[str, Any]]:
        """
        列出数据库中的所有键

        Returns:
            List[Dict[str, Any]]: 键列表，每个键包含名称和类型等信息

        Raises:
            DatabaseError: 如果列出键时发生错误
        """
        try:
            # 确保连接已建立
            if not self.connection.is_connected():
                self.connection.connect()

            # 获取所有键
            keys = self.redis_connection.client.keys('*')

            # 构建结果
            result = []
            for key in keys:
                # 获取键类型
                key_type = self.redis_connection.client.type(key)

                # 获取键过期时间
                ttl = self.redis_connection.client.ttl(key)

                # 获取键大小
                size = self._get_key_size(key, key_type)

                # 构建键信息
                key_info = {
                    'name': key,
                    'type': key_type,
                    'ttl': ttl if ttl > 0 else None,
                    'size': size,
                }

                result.append(key_info)

            return result

        except ConnectionError as e:
            raise DatabaseError(f"Failed to list Redis keys: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Unexpected error listing Redis keys: {str(e)}")

    def _get_key_size(self, key: str, key_type: str) -> int:
        """
        获取键大小

        Args:
            key: 键名
            key_type: 键类型

        Returns:
            int: 键大小（字节）
        """
        try:
            if key_type == 'string':
                return self.redis_connection.client.strlen(key)
            elif key_type == 'hash':
                return len(self.redis_connection.client.hgetall(key))
            elif key_type == 'list':
                return self.redis_connection.client.llen(key)
            elif key_type == 'set':
                return self.redis_connection.client.scard(key)
            elif key_type == 'zset':
                return self.redis_connection.client.zcard(key)
            else:
                return 0

        except Exception as e:
            self.logger.warning(f"Failed to get size for key {key}: {str(e)}")
            return 0

    def describe_resource(self, resource_name: str) -> Dict[str, Any]:
        """
        描述键结构

        获取键的详细信息，如类型、过期时间等。

        Args:
            resource_name: 键名

        Returns:
            Dict[str, Any]: 键详细信息

        Raises:
            ResourceNotFoundError: 如果键不存在
            DatabaseError: 如果描述键时发生错误
        """
        try:
            # 检查键是否存在
            if not self._resource_exists(resource_name):
                raise ResourceNotFoundError(f"Key '{resource_name}' does not exist")

            # 获取键类型
            key_type = self.redis_connection.client.type(resource_name)

            # 获取键过期时间
            ttl = self.redis_connection.client.ttl(resource_name)

            # 获取键大小
            size = self._get_key_size(resource_name, key_type)

            # 获取键内容
            content = self._get_key_content(resource_name, key_type)

            # 构建结果
            result = {
                'name': resource_name,
                'type': key_type,
                'ttl': ttl if ttl > 0 else None,
                'size': size,
                'content': content,
            }

            return result

        except ResourceNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to describe Redis key '{resource_name}': {str(e)}")

    def _resource_exists(self, resource_name: str) -> bool:
        """
        检查键是否存在

        Args:
            resource_name: 键名

        Returns:
            bool: 如果键存在，则返回True，否则返回False
        """
        try:
            # 确保连接已建立
            if not self.connection.is_connected():
                self.connection.connect()

            return bool(self.redis_connection.client.exists(resource_name))

        except Exception as e:
            self.logger.error(f"Error checking if key '{resource_name}' exists: {str(e)}")
            return False

    def _get_key_content(self, key: str, key_type: str) -> Any:
        """
        获取键内容

        Args:
            key: 键名
            key_type: 键类型

        Returns:
            Any: 键内容
        """
        try:
            if key_type == 'string':
                return self.redis_connection.client.get(key)
            elif key_type == 'hash':
                return self.redis_connection.client.hgetall(key)
            elif key_type == 'list':
                return self.redis_connection.client.lrange(key, 0, -1)
            elif key_type == 'set':
                return list(self.redis_connection.client.smembers(key))
            elif key_type == 'zset':
                return self.redis_connection.client.zrange(key, 0, -1, withscores=True)
            else:
                return None

        except Exception as e:
            self.logger.warning(f"Failed to get content for key {key}: {str(e)}")
            return None

    def get_resource_stats(self, resource_name: str) -> Dict[str, Any]:
        """
        获取键统计信息

        获取键的统计信息，如大小、过期时间等。

        Args:
            resource_name: 键名

        Returns:
            Dict[str, Any]: 键统计信息

        Raises:
            ResourceNotFoundError: 如果键不存在
            DatabaseError: 如果获取键统计信息时发生错误
        """
        try:
            # 检查键是否存在
            if not self._resource_exists(resource_name):
                raise ResourceNotFoundError(f"Key '{resource_name}' does not exist")

            # 获取键类型
            key_type = self.redis_connection.client.type(resource_name)

            # 获取键过期时间
            ttl = self.redis_connection.client.ttl(resource_name)

            # 获取键大小
            size = self._get_key_size(resource_name, key_type)

            # 获取键内存使用情况
            try:
                memory_usage = self.redis_connection.client.memory_usage(resource_name)
            except Exception:
                memory_usage = None

            # 构建结果
            result = {
                'type': key_type,
                'ttl': ttl if ttl > 0 else None,
                'size': size,
                'memory_usage': memory_usage,
            }

            return result

        except ResourceNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to get stats for Redis key '{resource_name}': {str(e)}")

    def extract_resource_name(self, query: str) -> Optional[str]:
        """
        从Redis命令中提取键名

        从Redis命令中提取操作的键名，用于权限检查。

        Args:
            query: Redis命令

        Returns:
            Optional[str]: 键名，如果无法提取，则返回None
        """
        try:
            # 将命令拆分为命令名和参数
            parts = query.split()
            if not parts:
                return None

            command = parts[0].lower()

            # 大多数Redis命令的第一个参数是键名
            if len(parts) > 1:
                key = parts[1]

                # 返回大写的键名，与权限配置保持一致
                return key.upper()

            return None

        except Exception:
            return None
