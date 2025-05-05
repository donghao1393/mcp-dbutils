"""
测试连接池

这个模块测试多数据库支持架构中的连接池。
"""

import pytest
import time
from unittest.mock import Mock, patch

from mcp_dbutils.multi_db.connection.pool import ConnectionPool
from mcp_dbutils.multi_db.error.exceptions import ConfigurationError, ConnectionError


class TestConnectionPool:
    """测试ConnectionPool类"""
    
    def test_init(self):
        """测试初始化"""
        config = {"test_conn": {"type": "mysql"}}
        factory = Mock()
        pool = ConnectionPool(config, factory)
        assert pool.config == config
        assert pool.factory == factory
        assert pool.connections == {}
        assert pool.active_connections == {}
        assert pool.max_idle_time == 300
        assert pool.cleanup_interval == 60
        
    def test_init_default_factory(self):
        """测试默认工厂的初始化"""
        config = {"test_conn": {"type": "mysql"}}
        with patch('mcp_dbutils.multi_db.connection.pool.ConnectionFactory') as mock_factory_class:
            mock_factory = Mock()
            mock_factory_class.return_value = mock_factory
            pool = ConnectionPool(config)
            assert pool.factory == mock_factory
            mock_factory_class.assert_called_once()
            
    @patch('mcp_dbutils.multi_db.connection.pool.time.time')
    def test_get_connection_new(self, mock_time):
        """测试获取新连接"""
        mock_time.return_value = 123456
        config = {"test_conn": {"type": "mysql"}}
        factory = Mock()
        mock_connection = Mock()
        factory.create_connection.return_value = mock_connection
        
        pool = ConnectionPool(config, factory)
        connection = pool.get_connection("test_conn")
        
        assert connection == mock_connection
        factory.create_connection.assert_called_once_with(config["test_conn"])
        mock_connection.connect.assert_called_once()
        assert pool.connections["test_conn"] == mock_connection
        assert pool.active_connections["test_conn"] == (mock_connection, 123456)
        
    @patch('mcp_dbutils.multi_db.connection.pool.time.time')
    def test_get_connection_cached(self, mock_time):
        """测试获取缓存的连接"""
        mock_time.return_value = 123456
        config = {"test_conn": {"type": "mysql"}}
        factory = Mock()
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        
        pool = ConnectionPool(config, factory)
        pool.connections["test_conn"] = mock_connection
        
        connection = pool.get_connection("test_conn")
        
        assert connection == mock_connection
        factory.create_connection.assert_not_called()
        mock_connection.connect.assert_not_called()
        assert pool.active_connections["test_conn"] == (mock_connection, 123456)
        
    @patch('mcp_dbutils.multi_db.connection.pool.time.time')
    def test_get_connection_active(self, mock_time):
        """测试获取活动的连接"""
        mock_time.return_value = 123456
        config = {"test_conn": {"type": "mysql"}}
        factory = Mock()
        mock_connection = Mock()
        
        pool = ConnectionPool(config, factory)
        pool.active_connections["test_conn"] = (mock_connection, 123455)
        
        connection = pool.get_connection("test_conn")
        
        assert connection == mock_connection
        factory.create_connection.assert_not_called()
        assert pool.active_connections["test_conn"] == (mock_connection, 123455)
        
    def test_get_connection_reconnect(self):
        """测试重新连接"""
        config = {"test_conn": {"type": "mysql"}}
        factory = Mock()
        mock_connection = Mock()
        mock_connection.is_connected.return_value = False
        
        pool = ConnectionPool(config, factory)
        pool.connections["test_conn"] = mock_connection
        
        connection = pool.get_connection("test_conn")
        
        assert connection == mock_connection
        factory.create_connection.assert_not_called()
        mock_connection.connect.assert_called_once()
        
    def test_get_connection_reconnect_failed(self):
        """测试重新连接失败"""
        config = {"test_conn": {"type": "mysql"}}
        factory = Mock()
        mock_connection = Mock()
        mock_connection.is_connected.return_value = False
        mock_connection.connect.side_effect = ConnectionError("Failed to connect")
        
        pool = ConnectionPool(config, factory)
        pool.connections["test_conn"] = mock_connection
        
        with pytest.raises(ConnectionError) as excinfo:
            pool.get_connection("test_conn")
        assert "Failed to connect" in str(excinfo.value)
        assert "test_conn" not in pool.connections
        
    def test_get_connection_not_found(self):
        """测试连接配置不存在"""
        config = {"test_conn": {"type": "mysql"}}
        factory = Mock()
        
        pool = ConnectionPool(config, factory)
        
        with pytest.raises(ConfigurationError) as excinfo:
            pool.get_connection("non_existent")
        assert "Connection configuration for 'non_existent' not found" in str(excinfo.value)
        
    def test_get_connection_create_failed(self):
        """测试创建连接失败"""
        config = {"test_conn": {"type": "mysql"}}
        factory = Mock()
        factory.create_connection.side_effect = ConfigurationError("Invalid config")
        
        pool = ConnectionPool(config, factory)
        
        with pytest.raises(ConnectionError) as excinfo:
            pool.get_connection("test_conn")
        assert "Failed to create connection for 'test_conn'" in str(excinfo.value)
        
    def test_release_connection(self):
        """测试释放连接"""
        config = {"test_conn": {"type": "mysql"}}
        factory = Mock()
        mock_connection = Mock()
        mock_connection.is_transaction_active = False
        
        pool = ConnectionPool(config, factory)
        pool.active_connections["test_conn"] = (mock_connection, 123455)
        
        pool.release_connection("test_conn")
        
        assert "test_conn" in pool.active_connections
        mock_connection.rollback.assert_not_called()
        
    def test_release_connection_with_transaction(self):
        """测试释放带事务的连接"""
        config = {"test_conn": {"type": "mysql"}}
        factory = Mock()
        mock_connection = Mock()
        mock_connection.is_transaction_active = True
        
        pool = ConnectionPool(config, factory)
        pool.active_connections["test_conn"] = (mock_connection, 123455)
        
        pool.release_connection("test_conn")
        
        assert "test_conn" in pool.active_connections
        mock_connection.rollback.assert_called_once()
        
    def test_release_connection_not_found(self):
        """测试释放不存在的连接"""
        config = {"test_conn": {"type": "mysql"}}
        factory = Mock()
        
        pool = ConnectionPool(config, factory)
        
        # 不应该抛出异常
        pool.release_connection("non_existent")
        
    def test_close_connection(self):
        """测试关闭连接"""
        config = {"test_conn": {"type": "mysql"}}
        factory = Mock()
        mock_connection = Mock()
        
        pool = ConnectionPool(config, factory)
        pool.connections["test_conn"] = mock_connection
        pool.active_connections["test_conn"] = (mock_connection, 123455)
        
        pool.close_connection("test_conn")
        
        assert "test_conn" not in pool.connections
        assert "test_conn" not in pool.active_connections
        mock_connection.disconnect.assert_called_once()
        
    def test_close_connection_not_found(self):
        """测试关闭不存在的连接"""
        config = {"test_conn": {"type": "mysql"}}
        factory = Mock()
        
        pool = ConnectionPool(config, factory)
        
        # 不应该抛出异常
        pool.close_connection("non_existent")
        
    def test_close_all(self):
        """测试关闭所有连接"""
        config = {"test_conn1": {"type": "mysql"}, "test_conn2": {"type": "postgresql"}}
        factory = Mock()
        mock_connection1 = Mock()
        mock_connection2 = Mock()
        
        pool = ConnectionPool(config, factory)
        pool.connections["test_conn1"] = mock_connection1
        pool.connections["test_conn2"] = mock_connection2
        pool.active_connections["test_conn1"] = (mock_connection1, 123455)
        
        pool.close_all()
        
        assert pool.connections == {}
        assert pool.active_connections == {}
        mock_connection1.disconnect.assert_called_once()
        mock_connection2.disconnect.assert_called_once()
        
    @patch('mcp_dbutils.multi_db.connection.pool.time.time')
    def test_cleanup_idle_connections(self, mock_time):
        """测试清理空闲连接"""
        mock_time.return_value = 123456
        config = {"test_conn1": {"type": "mysql"}, "test_conn2": {"type": "postgresql"}}
        factory = Mock()
        mock_connection1 = Mock()
        mock_connection2 = Mock()
        
        pool = ConnectionPool(config, factory)
        pool.connections["test_conn1"] = mock_connection1
        pool.connections["test_conn2"] = mock_connection2
        pool.active_connections["test_conn1"] = (mock_connection1, 123156)  # 300秒前
        pool.active_connections["test_conn2"] = (mock_connection2, 123356)  # 100秒前
        pool.last_cleanup_time = 123396  # 60秒前
        pool.max_idle_time = 200  # 设置最大空闲时间为200秒
        
        pool._cleanup_idle_connections()
        
        assert "test_conn1" not in pool.connections
        assert "test_conn1" not in pool.active_connections
        assert "test_conn2" in pool.connections
        assert "test_conn2" in pool.active_connections
        mock_connection1.disconnect.assert_called_once()
        mock_connection2.disconnect.assert_not_called()
        
    @patch('mcp_dbutils.multi_db.connection.pool.time.time')
    def test_cleanup_idle_connections_not_time_yet(self, mock_time):
        """测试还未到清理时间"""
        mock_time.return_value = 123456
        config = {"test_conn": {"type": "mysql"}}
        factory = Mock()
        mock_connection = Mock()
        
        pool = ConnectionPool(config, factory)
        pool.connections["test_conn"] = mock_connection
        pool.active_connections["test_conn"] = (mock_connection, 123156)  # 300秒前
        pool.last_cleanup_time = 123426  # 30秒前
        pool.cleanup_interval = 60  # 设置清理间隔为60秒
        
        pool._cleanup_idle_connections()
        
        assert "test_conn" in pool.connections
        assert "test_conn" in pool.active_connections
        mock_connection.disconnect.assert_not_called()
        
    def test_set_max_idle_time(self):
        """测试设置最大空闲时间"""
        config = {"test_conn": {"type": "mysql"}}
        pool = ConnectionPool(config)
        pool.set_max_idle_time(600)
        assert pool.max_idle_time == 600
        
    def test_set_cleanup_interval(self):
        """测试设置清理间隔"""
        config = {"test_conn": {"type": "mysql"}}
        pool = ConnectionPool(config)
        pool.set_cleanup_interval(120)
        assert pool.cleanup_interval == 120
