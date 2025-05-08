"""
Redis命令构建器实现

这个模块实现了Redis命令构建器，用于构建Redis命令。
"""

import logging
from typing import Any, Dict, List, Optional

from ..error.exceptions import QueryError
from .base import Query, QueryBuilder


class RedisCommand(Query):
    """
    Redis命令类

    这个类表示一个Redis命令，包含命令名、键和参数。
    """

    def __init__(self, command: str, key: Optional[str] = None, args: Optional[List[Any]] = None):
        """
        初始化Redis命令

        Args:
            command: 命令名
            key: 键
            args: 命令参数
        """
        self.command = command.upper()
        self.key = key
        self.args = args or []

    def get_query_string(self) -> str:
        """
        获取命令字符串

        Returns:
            str: 命令字符串
        """
        # 构建命令字符串
        parts = [self.command]

        if self.key:
            parts.append(self.key)

        if self.args:
            parts.extend([str(arg) for arg in self.args])

        return ' '.join(parts)

    def get_params(self) -> List[Any]:
        """
        获取命令参数

        Returns:
            List[Any]: 命令参数
        """
        params = []

        if self.key:
            params.append(self.key)

        if self.args:
            params.extend(self.args)

        return params


class RedisCommandBuilder(QueryBuilder):
    """
    Redis命令构建器类

    这个类实现了Redis命令构建器，用于构建Redis命令。
    """

    def __init__(self):
        """
        初始化Redis命令构建器
        """
        self.command = None
        self.key = None
        self.args = []
        self.logger = logging.getLogger(__name__)

    def select(self, resource_name: str, fields: Optional[List[str]] = None) -> 'RedisCommandBuilder':
        """
        构建GET命令

        Args:
            resource_name: 键名
            fields: 要获取的字段列表，用于哈希类型

        Returns:
            RedisCommandBuilder: 命令构建器实例
        """
        self.key = resource_name

        if fields and len(fields) > 0:
            # 如果指定了字段，使用HMGET命令
            self.command = 'HMGET'
            self.args = fields
        else:
            # 否则，使用GET命令
            self.command = 'GET'

        return self

    def hgetall(self, resource_name: str) -> 'RedisCommandBuilder':
        """
        构建HGETALL命令

        Args:
            resource_name: 键名

        Returns:
            RedisCommandBuilder: 命令构建器实例
        """
        self.command = 'HGETALL'
        self.key = resource_name

        return self

    def lrange(self, resource_name: str, start: int = 0, end: int = -1) -> 'RedisCommandBuilder':
        """
        构建LRANGE命令

        Args:
            resource_name: 键名
            start: 起始索引
            end: 结束索引

        Returns:
            RedisCommandBuilder: 命令构建器实例
        """
        self.command = 'LRANGE'
        self.key = resource_name
        self.args = [start, end]

        return self

    def smembers(self, resource_name: str) -> 'RedisCommandBuilder':
        """
        构建SMEMBERS命令

        Args:
            resource_name: 键名

        Returns:
            RedisCommandBuilder: 命令构建器实例
        """
        self.command = 'SMEMBERS'
        self.key = resource_name

        return self

    def zrange(self, resource_name: str, start: int = 0, end: int = -1,
              with_scores: bool = False) -> 'RedisCommandBuilder':
        """
        构建ZRANGE命令

        Args:
            resource_name: 键名
            start: 起始索引
            end: 结束索引
            with_scores: 是否返回分数

        Returns:
            RedisCommandBuilder: 命令构建器实例
        """
        self.command = 'ZRANGE'
        self.key = resource_name
        self.args = [start, end]

        if with_scores:
            self.args.append('WITHSCORES')

        return self

    def insert(self, resource_name: str, data: Any) -> 'RedisCommandBuilder':
        """
        构建SET命令

        Args:
            resource_name: 键名
            data: 要设置的数据

        Returns:
            RedisCommandBuilder: 命令构建器实例
        """
        self.key = resource_name

        if isinstance(data, dict):
            # 如果数据是字典，使用HMSET命令
            self.command = 'HMSET'

            # 将字典转换为参数列表
            for key, value in data.items():
                self.args.extend([key, value])
        else:
            # 否则，使用SET命令
            self.command = 'SET'
            self.args = [data]

        return self

    def setex(self, resource_name: str, value: Any, seconds: int) -> 'RedisCommandBuilder':
        """
        构建SETEX命令

        Args:
            resource_name: 键名
            value: 要设置的值
            seconds: 过期时间（秒）

        Returns:
            RedisCommandBuilder: 命令构建器实例
        """
        self.command = 'SETEX'
        self.key = resource_name
        self.args = [seconds, value]

        return self

    def lpush(self, resource_name: str, *values: Any) -> 'RedisCommandBuilder':
        """
        构建LPUSH命令

        Args:
            resource_name: 键名
            values: 要添加的值

        Returns:
            RedisCommandBuilder: 命令构建器实例
        """
        self.command = 'LPUSH'
        self.key = resource_name
        self.args = list(values)

        return self

    def rpush(self, resource_name: str, *values: Any) -> 'RedisCommandBuilder':
        """
        构建RPUSH命令

        Args:
            resource_name: 键名
            values: 要添加的值

        Returns:
            RedisCommandBuilder: 命令构建器实例
        """
        self.command = 'RPUSH'
        self.key = resource_name
        self.args = list(values)

        return self

    def sadd(self, resource_name: str, *values: Any) -> 'RedisCommandBuilder':
        """
        构建SADD命令

        Args:
            resource_name: 键名
            values: 要添加的值

        Returns:
            RedisCommandBuilder: 命令构建器实例
        """
        self.command = 'SADD'
        self.key = resource_name
        self.args = list(values)

        return self

    def zadd(self, resource_name: str, *score_member_pairs: Any) -> 'RedisCommandBuilder':
        """
        构建ZADD命令

        Args:
            resource_name: 键名
            score_member_pairs: 分数和成员对，如 1 'one' 2 'two'

        Returns:
            RedisCommandBuilder: 命令构建器实例
        """
        self.command = 'ZADD'
        self.key = resource_name
        self.args = list(score_member_pairs)

        return self

    def update(self, resource_name: str, data: Any,
              condition: Optional[Dict[str, Any]] = None) -> 'RedisCommandBuilder':
        """
        构建SET命令

        Args:
            resource_name: 键名
            data: 要更新的数据
            condition: 更新条件（Redis不支持条件更新）

        Returns:
            RedisCommandBuilder: 命令构建器实例
        """
        # Redis不支持条件更新，忽略condition参数
        return self.insert(resource_name, data)

    def delete(self, resource_name: str,
              condition: Optional[Dict[str, Any]] = None) -> 'RedisCommandBuilder':
        """
        构建DEL命令

        Args:
            resource_name: 键名
            condition: 删除条件（Redis不支持条件删除）

        Returns:
            RedisCommandBuilder: 命令构建器实例
        """
        # Redis不支持条件删除，忽略condition参数
        self.command = 'DEL'
        self.key = resource_name

        return self

    def expire(self, resource_name: str, seconds: int) -> 'RedisCommandBuilder':
        """
        构建EXPIRE命令

        Args:
            resource_name: 键名
            seconds: 过期时间（秒）

        Returns:
            RedisCommandBuilder: 命令构建器实例
        """
        self.command = 'EXPIRE'
        self.key = resource_name
        self.args = [seconds]

        return self

    def where(self, condition: Dict[str, Any]) -> 'RedisCommandBuilder':
        """
        添加条件（Redis不支持条件查询）

        Args:
            condition: 条件

        Returns:
            RedisCommandBuilder: 命令构建器实例
        """
        # Redis不支持条件查询，忽略condition参数
        self.logger.warning("Redis does not support conditional queries, ignoring condition")
        return self

    def order_by(self, fields: List[str]) -> 'RedisCommandBuilder':
        """
        添加排序（Redis不支持排序查询）

        Args:
            fields: 排序字段列表

        Returns:
            RedisCommandBuilder: 命令构建器实例
        """
        # Redis不支持排序查询，忽略fields参数
        self.logger.warning("Redis does not support ordered queries, ignoring order_by")
        return self

    def limit(self, count: int) -> 'RedisCommandBuilder':
        """
        添加限制（Redis不支持限制查询）

        Args:
            count: 限制数量

        Returns:
            RedisCommandBuilder: 命令构建器实例
        """
        # Redis不支持限制查询，忽略count参数
        self.logger.warning("Redis does not support limited queries, ignoring limit")
        return self

    def offset(self, count: int) -> 'RedisCommandBuilder':
        """
        添加偏移（Redis不支持偏移查询）

        Args:
            count: 偏移数量

        Returns:
            RedisCommandBuilder: 命令构建器实例
        """
        # Redis不支持偏移查询，忽略count参数
        self.logger.warning("Redis does not support offset queries, ignoring offset")
        return self

    def build(self) -> RedisCommand:
        """
        构建Redis命令

        Returns:
            RedisCommand: Redis命令实例
        """
        if not self.command:
            raise QueryError("Command is required")

        return RedisCommand(self.command, self.key, self.args)
