"""
测试连接基类

这个模块测试多数据库支持架构中的连接基类。
"""

from unittest.mock import Mock, patch

import pytest

from mcp_dbutils.multi_db.connection.base import ConnectionBase
from mcp_dbutils.multi_db.error.exceptions import ConnectionError, TransactionError


# 创建一个具体的ConnectionBase子类用于测试
class TestConnection(ConnectionBase):
    """测试用的连接类"""
    
    def connect(self):
        """建立连接"""
        self.connection = Mock()
        
    def disconnect(self):
        """断开连接"""
        self.connection = None
        
    def is_connected(self):
        """检查连接状态"""
        return self.connection is not None
        
    def execute(self, query, params=None):
        """执行查询"""
        if not self.is_connected():
            raise ConnectionError("Not connected")
        return "result"
        
    def begin_transaction(self):
        """开始事务"""
        if not self.is_connected():
            raise ConnectionError("Not connected")
        if self.is_transaction_active:
            raise TransactionError("Transaction already active")
        self.is_transaction_active = True
        
    def commit(self):
        """提交事务"""
        if not self.is_connected():
            raise ConnectionError("Not connected")
        if not self.is_transaction_active:
            raise TransactionError("No active transaction")
        self.is_transaction_active = False
        
    def rollback(self):
        """回滚事务"""
        if not self.is_connected():
            raise ConnectionError("Not connected")
        if not self.is_transaction_active:
            raise TransactionError("No active transaction")
        self.is_transaction_active = False


class TestConnectionBase:
    """测试ConnectionBase类"""
    
    def test_init(self):
        """测试初始化"""
        config = {"host": "localhost", "port": 3306}
        connection = TestConnection(config)
        assert connection.config == config
        assert connection.connection is None
        assert not connection.is_transaction_active
        
    def test_connect_disconnect(self):
        """测试连接和断开连接"""
        connection = TestConnection({})
        assert not connection.is_connected()
        
        connection.connect()
        assert connection.is_connected()
        
        connection.disconnect()
        assert not connection.is_connected()
        
    def test_execute(self):
        """测试执行查询"""
        connection = TestConnection({})
        
        # 未连接时执行查询
        with pytest.raises(ConnectionError):
            connection.execute("SELECT 1")
            
        # 连接后执行查询
        connection.connect()
        result = connection.execute("SELECT 1")
        assert result == "result"
        
    def test_transaction(self):
        """测试事务操作"""
        connection = TestConnection({})
        
        # 未连接时开始事务
        with pytest.raises(ConnectionError):
            connection.begin_transaction()
            
        # 连接后开始事务
        connection.connect()
        connection.begin_transaction()
        assert connection.is_transaction_active
        
        # 重复开始事务
        with pytest.raises(TransactionError):
            connection.begin_transaction()
            
        # 提交事务
        connection.commit()
        assert not connection.is_transaction_active
        
        # 没有活动事务时提交
        with pytest.raises(TransactionError):
            connection.commit()
            
        # 开始新事务并回滚
        connection.begin_transaction()
        assert connection.is_transaction_active
        connection.rollback()
        assert not connection.is_transaction_active
        
        # 没有活动事务时回滚
        with pytest.raises(TransactionError):
            connection.rollback()
            
        # 断开连接后的事务操作
        connection.disconnect()
        with pytest.raises(ConnectionError):
            connection.begin_transaction()
        with pytest.raises(ConnectionError):
            connection.commit()
        with pytest.raises(ConnectionError):
            connection.rollback()
