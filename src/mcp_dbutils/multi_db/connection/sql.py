"""
SQL数据库连接实现

这个模块实现了SQL数据库的连接类，支持各种SQL数据库，如MySQL、PostgreSQL等。
提供了连接管理、事务处理、查询执行等功能。
"""

import logging
import time
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

from ..error.exceptions import ConnectionError, QueryError, TransactionError
from .base import ConnectionBase


class SQLConnection(ConnectionBase):
    """
    SQL数据库连接类

    这个类实现了与SQL数据库的连接管理，支持各种SQL数据库，如MySQL、PostgreSQL等。
    提供了连接池管理、健康检查、事务处理等功能。
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化SQL连接

        Args:
            config: 连接配置，包含连接参数
                - type: 数据库类型（mysql, postgresql等）
                - host: 主机名
                - port: 端口号
                - database: 数据库名
                - username: 用户名
                - password: 密码
                - ssl: SSL配置
                - timeout: 连接超时时间（秒）
                - pool_size: 连接池大小
                - max_overflow: 连接池最大溢出数
                - pool_recycle: 连接池回收时间（秒）
                - pool_timeout: 连接池超时时间（秒）
                - pool_pre_ping: 是否在使用前检查连接
                - isolation_level: 事务隔离级别
        """
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.dbapi_connection = None
        self.connection_pool = None
        self.db_type = config.get('type', 'mysql').lower()

        # 连接池配置
        self.pool_size = int(config.get('pool_size', 5))
        self.max_overflow = int(config.get('max_overflow', 10))
        self.pool_recycle = int(config.get('pool_recycle', 3600))  # 默认1小时
        self.pool_timeout = int(config.get('pool_timeout', 30))
        self.pool_pre_ping = config.get('pool_pre_ping', True)

        # 事务配置
        self.isolation_level = config.get('isolation_level')
        self.savepoint_id = 0  # 用于生成唯一的保存点ID

    def connect(self) -> None:
        """
        建立连接

        建立到SQL数据库的连接，如果连接已经存在，则重用现有连接。

        Raises:
            ConnectionError: 如果连接失败
        """
        if self.is_connected():
            return

        try:
            # 根据数据库类型选择适当的DBAPI
            if self.db_type == 'mysql':
                self._connect_mysql()
            elif self.db_type == 'postgresql':
                self._connect_postgresql()
            elif self.db_type == 'sqlite':
                self._connect_sqlite()
            else:
                raise ConnectionError(f"Unsupported database type: {self.db_type}")

            self.logger.info(f"Connected to {self.db_type} database at {self.config.get('host', 'localhost')}")
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.db_type} database: {str(e)}")
            raise ConnectionError(f"Failed to connect to {self.db_type} database: {str(e)}")

    def _connect_mysql(self) -> None:
        """
        连接到MySQL数据库

        Raises:
            ConnectionError: 如果连接失败
        """
        try:
            import pymysql
            self.dbapi_connection = pymysql.connect(
                host=self.config.get('host', 'localhost'),
                port=int(self.config.get('port', 3306)),
                user=self.config.get('username', ''),
                password=self.config.get('password', ''),
                database=self.config.get('database', ''),
                charset=self.config.get('charset', 'utf8mb4'),
                connect_timeout=int(self.config.get('timeout', 10)),
                ssl=self.config.get('ssl', None)
            )
        except ImportError:
            self.logger.error("pymysql is not installed. Please install it with 'pip install pymysql'")
            raise ConnectionError("pymysql is not installed. Please install it with 'pip install pymysql'")
        except Exception as e:
            self.logger.error(f"Failed to connect to MySQL database: {str(e)}")
            raise ConnectionError(f"Failed to connect to MySQL database: {str(e)}")

    def _connect_postgresql(self) -> None:
        """
        连接到PostgreSQL数据库

        Raises:
            ConnectionError: 如果连接失败
        """
        try:
            import psycopg2
            self.dbapi_connection = psycopg2.connect(
                host=self.config.get('host', 'localhost'),
                port=int(self.config.get('port', 5432)),
                user=self.config.get('username', ''),
                password=self.config.get('password', ''),
                dbname=self.config.get('database', ''),
                connect_timeout=int(self.config.get('timeout', 10)),
                sslmode=self.config.get('ssl_mode', 'prefer')
            )
        except ImportError:
            self.logger.error("psycopg2 is not installed. Please install it with 'pip install psycopg2-binary'")
            raise ConnectionError("psycopg2 is not installed. Please install it with 'pip install psycopg2-binary'")
        except Exception as e:
            self.logger.error(f"Failed to connect to PostgreSQL database: {str(e)}")
            raise ConnectionError(f"Failed to connect to PostgreSQL database: {str(e)}")

    def _connect_sqlite(self) -> None:
        """
        连接到SQLite数据库

        Raises:
            ConnectionError: 如果连接失败
        """
        try:
            import sqlite3
            self.dbapi_connection = sqlite3.connect(
                self.config.get('database', ':memory:'),
                timeout=float(self.config.get('timeout', 5.0))
            )
        except ImportError:
            self.logger.error("sqlite3 is not available in your Python installation")
            raise ConnectionError("sqlite3 is not available in your Python installation")
        except Exception as e:
            self.logger.error(f"Failed to connect to SQLite database: {str(e)}")
            raise ConnectionError(f"Failed to connect to SQLite database: {str(e)}")

    def disconnect(self) -> None:
        """
        断开连接

        断开与SQL数据库的连接，释放资源。
        如果有活动的事务，会先回滚事务。
        """
        if not self.is_connected():
            return

        try:
            if self.is_transaction_active:
                self.rollback()

            self.dbapi_connection.close()
            self.dbapi_connection = None
            self.logger.info(f"Disconnected from {self.db_type} database")
        except Exception as e:
            self.logger.error(f"Error disconnecting from {self.db_type} database: {str(e)}")
            # 不抛出异常，因为这是清理操作

    def is_connected(self) -> bool:
        """
        检查连接状态

        Returns:
            bool: 如果连接是活动的，则返回True，否则返回False
        """
        if self.dbapi_connection is None:
            return False

        try:
            # 对于不同的数据库类型，检查连接的方式不同
            if self.db_type == 'mysql':
                return self.dbapi_connection.open
            elif self.db_type == 'postgresql':
                return self.dbapi_connection.closed == 0
            elif self.db_type == 'sqlite':
                # SQLite没有明确的方法检查连接状态，尝试执行一个简单的查询
                cursor = self.dbapi_connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                return True
            else:
                return False
        except Exception:
            return False

    def check_connection_health(self) -> bool:
        """
        检查连接健康状态

        执行一个简单的查询来检查连接是否健康。

        Returns:
            bool: 如果连接健康，则返回True，否则返回False
        """
        if not self.is_connected():
            return False

        try:
            cursor = self.dbapi_connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            self.logger.warning(f"Connection health check failed: {str(e)}")
            return False

    def reconnect(self) -> None:
        """
        重新连接

        断开当前连接并重新建立连接。

        Raises:
            ConnectionError: 如果重新连接失败
        """
        self.disconnect()
        self.connect()

    def ping(self) -> bool:
        """
        Ping数据库服务器

        检查与数据库服务器的连接是否正常。

        Returns:
            bool: 如果连接正常，则返回True，否则返回False
        """
        if not self.is_connected():
            return False

        try:
            if self.db_type == 'mysql':
                self.dbapi_connection.ping(reconnect=True)
            else:
                cursor = self.dbapi_connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
            return True
        except Exception as e:
            self.logger.warning(f"Ping failed: {str(e)}")
            return False

    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        执行SQL查询

        执行给定的SQL查询，支持参数化查询。

        Args:
            query: SQL查询语句
            params: 查询参数

        Returns:
            查询结果

        Raises:
            ConnectionError: 如果执行查询时发生错误
        """
        if not self.is_connected():
            self.connect()

        try:
            cursor = self.dbapi_connection.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # 对于SELECT查询，获取结果
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                # 对于非SELECT查询，如果不在事务中，自动提交
                if not self.is_transaction_active:
                    self.dbapi_connection.commit()

                affected_rows = cursor.rowcount
                last_insert_id = None

                # 尝试获取最后插入的ID（不同数据库的方法不同）
                if query.strip().upper().startswith("INSERT"):
                    if self.db_type == 'mysql':
                        last_insert_id = cursor.lastrowid
                    elif self.db_type == 'postgresql':
                        # PostgreSQL需要使用RETURNING子句或currval函数
                        pass
                    elif self.db_type == 'sqlite':
                        last_insert_id = cursor.lastrowid

                cursor.close()
                return {
                    "affected_rows": affected_rows,
                    "last_insert_id": last_insert_id
                }
        except Exception as e:
            self.logger.error(f"Error executing SQL query: {str(e)}")
            if not self.is_transaction_active:
                # 如果不在事务中，尝试回滚以保持一致性
                try:
                    self.dbapi_connection.rollback()
                except Exception:
                    pass
            raise ConnectionError(f"Error executing SQL query: {str(e)}")

    def begin_transaction(self) -> None:
        """
        开始事务

        开始一个新的事务。如果已经有一个活动的事务，则创建一个保存点。

        Raises:
            TransactionError: 如果开始事务失败
        """
        if not self.is_connected():
            self.connect()

        try:
            if not self.is_transaction_active:
                # 开始新事务
                if self.db_type == 'sqlite':
                    # SQLite默认是自动提交模式，需要关闭自动提交
                    self.dbapi_connection.isolation_level = None
                    self.execute("BEGIN TRANSACTION")
                else:
                    # 大多数数据库可以通过设置autocommit=False来开始事务
                    self.dbapi_connection.autocommit = False

                    # 设置事务隔离级别（如果指定）
                    if self.isolation_level and self.db_type in ('mysql', 'postgresql'):
                        self.execute(f"SET TRANSACTION ISOLATION LEVEL {self.isolation_level}")

                self.is_transaction_active = True
                self.logger.info("Transaction started")
            else:
                # 创建保存点
                savepoint_name = self._create_savepoint()
                self.logger.info(f"Created savepoint: {savepoint_name}")

        except Exception as e:
            self.logger.error(f"Error starting transaction: {str(e)}")
            raise TransactionError(f"Error starting transaction: {str(e)}")

    def commit(self) -> None:
        """
        提交事务

        提交当前活动的事务。如果没有活动的事务，则抛出异常。

        Raises:
            TransactionError: 如果没有活动的事务或提交失败
        """
        if not self.is_connected():
            raise TransactionError("Not connected to database")

        if not self.is_transaction_active:
            raise TransactionError("No active transaction to commit")

        try:
            self.dbapi_connection.commit()
            self.is_transaction_active = False
            self.savepoint_id = 0  # 重置保存点ID

            # 恢复自动提交模式
            if self.db_type == 'sqlite':
                self.dbapi_connection.isolation_level = ''
            else:
                self.dbapi_connection.autocommit = True

            self.logger.info("Transaction committed")
        except Exception as e:
            self.logger.error(f"Error committing transaction: {str(e)}")
            raise TransactionError(f"Error committing transaction: {str(e)}")

    def rollback(self, savepoint_name: Optional[str] = None) -> None:
        """
        回滚事务

        回滚当前活动的事务或回滚到指定的保存点。如果没有活动的事务，则抛出异常。

        Args:
            savepoint_name: 保存点名称，如果指定，则回滚到该保存点

        Raises:
            TransactionError: 如果没有活动的事务或回滚失败
        """
        if not self.is_connected():
            raise TransactionError("Not connected to database")

        if not self.is_transaction_active:
            raise TransactionError("No active transaction to rollback")

        try:
            if savepoint_name:
                # 回滚到保存点
                self.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")

                self.logger.info(f"Rolled back to savepoint: {savepoint_name}")
            else:
                # 回滚整个事务
                self.dbapi_connection.rollback()
                self.is_transaction_active = False
                self.savepoint_id = 0  # 重置保存点ID

                # 恢复自动提交模式
                if self.db_type == 'sqlite':
                    self.dbapi_connection.isolation_level = ''
                else:
                    self.dbapi_connection.autocommit = True

                self.logger.info("Transaction rolled back")
        except Exception as e:
            self.logger.error(f"Error rolling back transaction: {str(e)}")
            raise TransactionError(f"Error rolling back transaction: {str(e)}")

    def _create_savepoint(self) -> str:
        """
        创建保存点

        在当前事务中创建一个保存点。

        Returns:
            str: 保存点名称

        Raises:
            TransactionError: 如果创建保存点失败
        """
        if not self.is_transaction_active:
            raise TransactionError("No active transaction to create savepoint")

        try:
            self.savepoint_id += 1
            savepoint_name = f"sp_{self.savepoint_id}"

            self.execute(f"SAVEPOINT {savepoint_name}")

            return savepoint_name
        except Exception as e:
            self.logger.error(f"Error creating savepoint: {str(e)}")
            raise TransactionError(f"Error creating savepoint: {str(e)}")

    def release_savepoint(self, savepoint_name: str) -> None:
        """
        释放保存点

        释放指定的保存点。

        Args:
            savepoint_name: 保存点名称

        Raises:
            TransactionError: 如果释放保存点失败
        """
        if not self.is_transaction_active:
            raise TransactionError("No active transaction to release savepoint")

        try:
            self.execute(f"RELEASE SAVEPOINT {savepoint_name}")

            self.logger.info(f"Released savepoint: {savepoint_name}")
        except Exception as e:
            self.logger.error(f"Error releasing savepoint: {str(e)}")
            raise TransactionError(f"Error releasing savepoint: {str(e)}")

    @contextmanager
    def transaction(self) -> Generator[None, None, None]:
        """
        事务上下文管理器

        提供一个上下文管理器，用于管理事务。
        在上下文结束时自动提交事务，如果发生异常，则回滚事务。

        Example:
            ```python
            with connection.transaction():
                connection.execute("INSERT INTO users (name) VALUES ('John')")
                connection.execute("UPDATE users SET age = 30 WHERE name = 'John'")
            ```

        Yields:
            None

        Raises:
            TransactionError: 如果事务操作失败
        """
        self.begin_transaction()
        try:
            yield
            self.commit()
        except Exception as e:
            self.rollback()
            raise e

    def execute_batch(self, query: str, params_list: List[Dict[str, Any]]) -> List[Any]:
        """
        批量执行SQL查询

        批量执行给定的SQL查询，每个查询使用不同的参数。

        Args:
            query: SQL查询语句
            params_list: 查询参数列表

        Returns:
            List[Any]: 查询结果列表

        Raises:
            ConnectionError: 如果执行查询时发生错误
        """
        if not self.is_connected():
            self.connect()

        results = []

        try:
            cursor = self.dbapi_connection.cursor()

            for params in params_list:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                # 对于SELECT查询，获取结果
                if query.strip().upper().startswith("SELECT"):
                    result = cursor.fetchall()
                    results.append(result)
                else:
                    # 对于非SELECT查询，获取影响的行数和最后插入的ID
                    affected_rows = cursor.rowcount
                    last_insert_id = None

                    # 尝试获取最后插入的ID（不同数据库的方法不同）
                    if query.strip().upper().startswith("INSERT") and (self.db_type == 'mysql' or self.db_type == 'sqlite'):
                        last_insert_id = cursor.lastrowid

                    results.append({
                        "affected_rows": affected_rows,
                        "last_insert_id": last_insert_id
                    })

            # 如果不在事务中，自动提交
            if not self.is_transaction_active:
                self.dbapi_connection.commit()

            cursor.close()
            return results
        except Exception as e:
            self.logger.error(f"Error executing batch SQL query: {str(e)}")
            if not self.is_transaction_active:
                # 如果不在事务中，尝试回滚以保持一致性
                try:
                    self.dbapi_connection.rollback()
                except Exception:
                    pass
            raise ConnectionError(f"Error executing batch SQL query: {str(e)}")

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        执行多个SQL查询

        使用executemany执行给定的SQL查询，适用于批量插入或更新。

        Args:
            query: SQL查询语句
            params_list: 查询参数列表

        Returns:
            Dict[str, Any]: 执行结果，包含affected_rows

        Raises:
            ConnectionError: 如果执行查询时发生错误
        """
        if not self.is_connected():
            self.connect()

        try:
            cursor = self.dbapi_connection.cursor()

            # 不同数据库的executemany参数格式可能不同
            if self.db_type == 'postgresql':
                # PostgreSQL需要使用元组列表
                params_tuple_list = [tuple(params.values()) for params in params_list]
                cursor.executemany(query, params_tuple_list)
            else:
                # MySQL和SQLite可以使用字典列表
                cursor.executemany(query, params_list)

            # 如果不在事务中，自动提交
            if not self.is_transaction_active:
                self.dbapi_connection.commit()

            affected_rows = cursor.rowcount
            cursor.close()

            return {
                "affected_rows": affected_rows
            }
        except Exception as e:
            self.logger.error(f"Error executing many SQL query: {str(e)}")
            if not self.is_transaction_active:
                # 如果不在事务中，尝试回滚以保持一致性
                try:
                    self.dbapi_connection.rollback()
                except Exception:
                    pass
            raise ConnectionError(f"Error executing many SQL query: {str(e)}")
