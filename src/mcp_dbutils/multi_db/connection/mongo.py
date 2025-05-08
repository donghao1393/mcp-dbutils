"""
MongoDB连接实现

这个模块实现了MongoDB数据库的连接类。
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError, ServerSelectionTimeoutError

from ..error.exceptions import ConnectionError, TransactionError
from .base import ConnectionBase


class MongoConnection(ConnectionBase):
    """
    MongoDB连接类

    这个类实现了与MongoDB数据库的连接管理。
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化MongoDB连接

        Args:
            config: 连接配置，包含连接参数
                - uri: MongoDB连接URI
                - host: 主机名
                - port: 端口号
                - database: 数据库名
                - username: 用户名
                - password: 密码
                - auth_source: 认证数据库
                - ssl: SSL配置
                - timeout: 连接超时时间
        """
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.db = None
        self.session = None

    def connect(self) -> None:
        """
        建立连接

        建立到MongoDB数据库的连接，如果连接已经存在，则重用现有连接。

        Raises:
            ConnectionError: 如果连接失败
        """
        if self.is_connected():
            return

        try:
            # 构建连接URI
            uri = self._build_connection_uri()

            # 创建MongoDB客户端
            self.client = MongoClient(
                uri,
                serverSelectionTimeoutMS=self.config.get('timeout', 5000),
                connectTimeoutMS=self.config.get('connect_timeout', 5000),
                socketTimeoutMS=self.config.get('socket_timeout', 10000)
            )

            # 检查连接是否成功
            self.client.admin.command('ping')

            # 获取数据库
            db_name = self.config.get('database')
            if not db_name:
                raise ConnectionError("MongoDB database name is required")

            self.db = self.client[db_name]
            self.logger.info(f"Connected to MongoDB database: {db_name}")

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self.client = None
            self.db = None
            raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")
        except Exception as e:
            self.client = None
            self.db = None
            raise ConnectionError(f"Unexpected error connecting to MongoDB: {str(e)}")

    def _build_connection_uri(self) -> str:
        """
        构建MongoDB连接URI

        Returns:
            str: MongoDB连接URI
        """
        # 如果配置中已经提供了URI，直接使用
        if 'uri' in self.config:
            return self.config['uri']

        host = self.config.get('host', 'localhost')
        port = self.config.get('port', 27017)
        username = self.config.get('username')
        password = self.config.get('password')
        auth_source = self.config.get('auth_source', 'admin')

        # 构建基本URI
        if username and password:
            uri = f"mongodb://{username}:{password}@{host}:{port}/?authSource={auth_source}"
        else:
            uri = f"mongodb://{host}:{port}/"

        # 添加其他连接选项
        if self.config.get('replica_set'):
            uri += f"&replicaSet={self.config['replica_set']}"

        if self.config.get('ssl', False):
            uri += "&ssl=true"

        return uri

    def disconnect(self) -> None:
        """
        断开连接

        断开与MongoDB数据库的连接，释放资源。
        如果有活动的事务，会先回滚事务。
        """
        if self.is_connected():
            try:
                if self.is_transaction_active:
                    self.rollback()

                if self.session:
                    self.session.end_session()
                    self.session = None

                if self.client:
                    self.client.close()
                    self.client = None
                    self.db = None
                    self.logger.info("Disconnected from MongoDB")
            except Exception as e:
                self.logger.error(f"Error disconnecting from MongoDB: {str(e)}")

    def is_connected(self) -> bool:
        """
        检查连接状态

        Returns:
            bool: 如果连接是活动的，则返回True，否则返回False
        """
        if not self.client or not self.db:
            return False

        try:
            # 尝试执行ping命令检查连接
            self.client.admin.command('ping')
            return True
        except Exception:
            return False

    def execute(self, query: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> Any:
        """
        执行MongoDB查询

        执行给定的MongoDB查询。

        Args:
            query: MongoDB查询，包含操作类型、集合名称和查询参数
            params: 额外的查询参数

        Returns:
            查询结果

        Raises:
            ConnectionError: 如果执行查询时发生错误
        """
        if not self.is_connected():
            self.connect()

        try:
            operation = query.get('operation')
            collection_name = query.get('collection')

            if not operation or not collection_name:
                raise ConnectionError("MongoDB query must specify operation and collection")

            collection = self.db[collection_name]

            # 合并查询参数
            query_params = query.get('params', {})
            if params:
                query_params.update(params)

            # 执行操作
            if operation == 'find':
                filter_dict = query_params.get('filter', {})
                projection = query_params.get('projection')
                sort = query_params.get('sort')
                limit = query_params.get('limit')
                skip = query_params.get('skip')

                cursor = collection.find(filter_dict, projection)

                if sort:
                    cursor = cursor.sort(sort)
                if skip:
                    cursor = cursor.skip(skip)
                if limit:
                    cursor = cursor.limit(limit)

                return list(cursor)

            elif operation == 'find_one':
                filter_dict = query_params.get('filter', {})
                projection = query_params.get('projection')
                return collection.find_one(filter_dict, projection)

            elif operation == 'insert_one':
                document = query_params.get('document', {})
                result = collection.insert_one(document, session=self.session)
                return {'inserted_id': str(result.inserted_id)}

            elif operation == 'insert_many':
                documents = query_params.get('documents', [])
                result = collection.insert_many(documents, session=self.session)
                return {'inserted_ids': [str(id) for id in result.inserted_ids]}

            elif operation == 'update_one':
                filter_dict = query_params.get('filter', {})
                update = query_params.get('update', {})
                upsert = query_params.get('upsert', False)
                result = collection.update_one(filter_dict, update, upsert=upsert, session=self.session)
                return {
                    'matched_count': result.matched_count,
                    'modified_count': result.modified_count,
                    'upserted_id': str(result.upserted_id) if result.upserted_id else None
                }

            elif operation == 'update_many':
                filter_dict = query_params.get('filter', {})
                update = query_params.get('update', {})
                upsert = query_params.get('upsert', False)
                result = collection.update_many(filter_dict, update, upsert=upsert, session=self.session)
                return {
                    'matched_count': result.matched_count,
                    'modified_count': result.modified_count,
                    'upserted_id': str(result.upserted_id) if result.upserted_id else None
                }

            elif operation == 'delete_one':
                filter_dict = query_params.get('filter', {})
                result = collection.delete_one(filter_dict, session=self.session)
                return {'deleted_count': result.deleted_count}

            elif operation == 'delete_many':
                filter_dict = query_params.get('filter', {})
                result = collection.delete_many(filter_dict, session=self.session)
                return {'deleted_count': result.deleted_count}

            elif operation == 'count_documents':
                filter_dict = query_params.get('filter', {})
                return collection.count_documents(filter_dict)

            elif operation == 'aggregate':
                pipeline = query_params.get('pipeline', [])
                return list(collection.aggregate(pipeline))

            elif operation == 'distinct':
                field = query_params.get('field')
                filter_dict = query_params.get('filter', {})
                return collection.distinct(field, filter_dict)

            else:
                raise ConnectionError(f"Unsupported MongoDB operation: {operation}")

        except PyMongoError as e:
            raise ConnectionError(f"MongoDB query execution error: {str(e)}")
        except Exception as e:
            raise ConnectionError(f"Unexpected error executing MongoDB query: {str(e)}")

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
            # 检查是否支持事务（需要副本集）
            if not self._supports_transactions():
                raise TransactionError("MongoDB transactions require a replica set")

            # 创建会话并开始事务
            self.session = self.client.start_session()
            self.session.start_transaction()
            self.is_transaction_active = True
            self.logger.info("MongoDB transaction started")

        except PyMongoError as e:
            if self.session:
                self.session.end_session()
                self.session = None
            self.is_transaction_active = False
            raise TransactionError(f"Failed to start MongoDB transaction: {str(e)}")

    def _supports_transactions(self) -> bool:
        """
        检查是否支持事务

        Returns:
            bool: 如果支持事务，则返回True，否则返回False
        """
        try:
            # 检查是否为副本集或分片集群
            status = self.client.admin.command("serverStatus")
            process_type = status.get("process", "")

            # mongos表示分片集群，mongod可能是副本集成员
            if process_type == "mongos":
                return True

            # 检查是否为副本集成员
            config = self.client.admin.command("replSetGetConfig")
            return config and "_id" in config

        except Exception:
            # 如果出错，假设不支持事务
            return False

    def commit(self) -> None:
        """
        提交事务

        提交当前活动的事务。如果没有活动的事务，则抛出异常。

        Raises:
            TransactionError: 如果没有活动的事务
        """
        if not self.is_transaction_active or not self.session:
            raise TransactionError("No active transaction to commit")

        try:
            self.session.commit_transaction()
            self.logger.info("MongoDB transaction committed")
        except PyMongoError as e:
            raise TransactionError(f"Failed to commit MongoDB transaction: {str(e)}")
        finally:
            self.session.end_session()
            self.session = None
            self.is_transaction_active = False

    def rollback(self) -> None:
        """
        回滚事务

        回滚当前活动的事务。如果没有活动的事务，则抛出异常。

        Raises:
            TransactionError: 如果没有活动的事务
        """
        if not self.is_transaction_active or not self.session:
            raise TransactionError("No active transaction to rollback")

        try:
            self.session.abort_transaction()
            self.logger.info("MongoDB transaction rolled back")
        except PyMongoError as e:
            self.logger.error(f"Error rolling back MongoDB transaction: {str(e)}")
        finally:
            self.session.end_session()
            self.session = None
            self.is_transaction_active = False
