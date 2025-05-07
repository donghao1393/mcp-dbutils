"""
异常定义

这个模块定义了多数据库支持架构中使用的异常类。
"""

class DatabaseError(Exception):
    """
    数据库错误基类
    
    所有数据库相关错误的基类。
    """
    
    def __init__(self, message: str, cause: Exception = None):
        """
        初始化数据库错误
        
        Args:
            message: 错误消息
            cause: 原始异常
        """
        super().__init__(message)
        self.cause = cause
        
    def get_message(self) -> str:
        """
        获取错误消息
        
        Returns:
            str: 错误消息
        """
        return str(self)
        
    def get_cause(self) -> Exception:
        """
        获取原始异常
        
        Returns:
            Exception: 原始异常
        """
        return self.cause


class ConnectionError(DatabaseError):
    """
    连接错误
    
    表示数据库连接相关的错误。
    """
    
    def __init__(self, message: str, connection_name: str = None, cause: Exception = None):
        """
        初始化连接错误
        
        Args:
            message: 错误消息
            connection_name: 连接名
            cause: 原始异常
        """
        super().__init__(message, cause)
        self.connection_name = connection_name
        
    def get_connection_name(self) -> str:
        """
        获取连接名
        
        Returns:
            str: 连接名
        """
        return self.connection_name


class AuthenticationError(ConnectionError):
    """
    认证错误
    
    表示数据库认证相关的错误。
    """
    pass


class ConfigurationError(DatabaseError):
    """
    配置错误
    
    表示数据库配置相关的错误。
    """
    pass


class ResourceNotFoundError(DatabaseError):
    """
    资源未找到错误
    
    表示请求的资源（表、集合、键等）不存在。
    """
    
    def __init__(self, message: str, resource_name: str = None, cause: Exception = None):
        """
        初始化资源未找到错误
        
        Args:
            message: 错误消息
            resource_name: 资源名
            cause: 原始异常
        """
        super().__init__(message, cause)
        self.resource_name = resource_name
        
    def get_resource_name(self) -> str:
        """
        获取资源名
        
        Returns:
            str: 资源名
        """
        return self.resource_name


class DuplicateKeyError(DatabaseError):
    """
    重复键错误
    
    表示插入操作违反了唯一性约束。
    """
    
    def __init__(self, message: str, resource_name: str = None, key: str = None, cause: Exception = None):
        """
        初始化重复键错误
        
        Args:
            message: 错误消息
            resource_name: 资源名
            key: 重复的键
            cause: 原始异常
        """
        super().__init__(message, cause)
        self.resource_name = resource_name
        self.key = key
        
    def get_resource_name(self) -> str:
        """
        获取资源名
        
        Returns:
            str: 资源名
        """
        return self.resource_name
        
    def get_key(self) -> str:
        """
        获取重复的键
        
        Returns:
            str: 重复的键
        """
        return self.key


class PermissionError(DatabaseError):
    """
    权限错误
    
    表示操作因权限不足而被拒绝。
    """
    
    def __init__(self, message: str, connection_name: str = None, resource_name: str = None, 
                 operation_type: str = None, cause: Exception = None):
        """
        初始化权限错误
        
        Args:
            message: 错误消息
            connection_name: 连接名
            resource_name: 资源名
            operation_type: 操作类型
            cause: 原始异常
        """
        super().__init__(message, cause)
        self.connection_name = connection_name
        self.resource_name = resource_name
        self.operation_type = operation_type
        
    def get_connection_name(self) -> str:
        """
        获取连接名
        
        Returns:
            str: 连接名
        """
        return self.connection_name
        
    def get_resource_name(self) -> str:
        """
        获取资源名
        
        Returns:
            str: 资源名
        """
        return self.resource_name
        
    def get_operation_type(self) -> str:
        """
        获取操作类型
        
        Returns:
            str: 操作类型
        """
        return self.operation_type


class QueryError(DatabaseError):
    """
    查询错误
    
    表示查询执行过程中发生的错误。
    """
    
    def __init__(self, message: str, query: str = None, cause: Exception = None):
        """
        初始化查询错误
        
        Args:
            message: 错误消息
            query: 查询
            cause: 原始异常
        """
        super().__init__(message, cause)
        self.query = query
        
    def get_query(self) -> str:
        """
        获取查询
        
        Returns:
            str: 查询
        """
        return self.query


class TransactionError(DatabaseError):
    """
    事务错误
    
    表示事务相关的错误。
    """
    
    def __init__(self, message: str, transaction_id: str = None, cause: Exception = None):
        """
        初始化事务错误
        
        Args:
            message: 错误消息
            transaction_id: 事务ID
            cause: 原始异常
        """
        super().__init__(message, cause)
        self.transaction_id = transaction_id
        
    def get_transaction_id(self) -> str:
        """
        获取事务ID
        
        Returns:
            str: 事务ID
        """
        return self.transaction_id


class NotImplementedError(DatabaseError):
    """
    未实现错误
    
    表示请求的功能尚未实现。
    """
    pass
