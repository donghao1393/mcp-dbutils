"""
SQL数据库连接实现

这个模块实现了SQL数据库的连接类，支持各种SQL数据库，如MySQL、PostgreSQL等。
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from ..error.exceptions import ConnectionError, TransactionError
from .base import ConnectionBase


class SQLConnection(ConnectionBase):
    """
    SQL数据库连接类
    
    这个类实现了与SQL数据库的连接管理，支持各种SQL数据库，如MySQL、PostgreSQL等。
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
                - timeout: 连接超时时间
                - pool_size: 连接池大小
                - max_overflow: 连接池最大溢出数
        """
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.dbapi_connection = None
        self.connection_pool = None
        self.db_type = config.get('type', 'mysql')
        
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
        
        开始一个新的事务。如果已经有一个活动的事务，则抛出异常。
        
        Raises:
            TransactionError: 如果已经有一个活动的事务
        """
        if not self.is_connected():
            self.connect()
            
        if self.is_transaction_active:
            raise TransactionError("Transaction already active")
            
        try:
            # 不同数据库开始事务的方式可能不同
            if self.db_type == 'sqlite':
                # SQLite默认是自动提交模式，需要关闭自动提交
                self.dbapi_connection.isolation_level = None
                self.execute("BEGIN TRANSACTION")
            else:
                # 大多数数据库可以通过设置autocommit=False来开始事务
                self.dbapi_connection.autocommit = False
                
            self.is_transaction_active = True
            self.logger.info("Transaction started")
        except Exception as e:
            self.logger.error(f"Error starting transaction: {str(e)}")
            raise TransactionError(f"Error starting transaction: {str(e)}")
        
    def commit(self) -> None:
        """
        提交事务
        
        提交当前活动的事务。如果没有活动的事务，则抛出异常。
        
        Raises:
            TransactionError: 如果没有活动的事务
        """
        if not self.is_connected():
            raise TransactionError("Not connected to database")
            
        if not self.is_transaction_active:
            raise TransactionError("No active transaction to commit")
            
        try:
            self.dbapi_connection.commit()
            self.is_transaction_active = False
            
            # 恢复自动提交模式
            if self.db_type == 'sqlite':
                self.dbapi_connection.isolation_level = ''
            else:
                self.dbapi_connection.autocommit = True
                
            self.logger.info("Transaction committed")
        except Exception as e:
            self.logger.error(f"Error committing transaction: {str(e)}")
            raise TransactionError(f"Error committing transaction: {str(e)}")
        
    def rollback(self) -> None:
        """
        回滚事务
        
        回滚当前活动的事务。如果没有活动的事务，则抛出异常。
        
        Raises:
            TransactionError: 如果没有活动的事务
        """
        if not self.is_connected():
            raise TransactionError("Not connected to database")
            
        if not self.is_transaction_active:
            raise TransactionError("No active transaction to rollback")
            
        try:
            self.dbapi_connection.rollback()
            self.is_transaction_active = False
            
            # 恢复自动提交模式
            if self.db_type == 'sqlite':
                self.dbapi_connection.isolation_level = ''
            else:
                self.dbapi_connection.autocommit = True
                
            self.logger.info("Transaction rolled back")
        except Exception as e:
            self.logger.error(f"Error rolling back transaction: {str(e)}")
            raise TransactionError(f"Error rolling back transaction: {str(e)}")
