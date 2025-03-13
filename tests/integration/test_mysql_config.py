"""Test MySQL configuration parsing"""

import pytest
import os
import tempfile
import yaml
from mcp_dbutils.mysql.config import MySQLConfig, SSLConfig
from mcp_dbutils.base import ConfigurationError

def test_basic_config():
    """Test basic MySQL configuration parsing"""
    config_data = {
        "connections": {
            "test_mysql": {
                "type": "mysql",
                "host": "localhost",
                "port": 3306,
                "database": "test_db",
                "user": "test_user",
                "password": "test_pass",
                "charset": "utf8mb4"
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(config_data, tmp)
        tmp.flush()
        
        config = MySQLConfig.from_yaml(tmp.name, "test_mysql")
        assert config.type == "mysql"
        assert config.host == "localhost"
        assert config.port == "3306"  # port is converted to string
        assert config.database == "test_db"
        assert config.user == "test_user"
        assert config.password == "test_pass"
        assert config.charset == "utf8mb4"
        assert config.ssl is None

def test_url_config():
    """Test MySQL URL configuration parsing"""
    config_data = {
        "connections": {
            "test_mysql": {
                "type": "mysql",
                "url": "mysql://localhost:3306/test_db?charset=utf8mb4",
                "user": "test_user",
                "password": "test_pass"
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(config_data, tmp)
        tmp.flush()
        
        config = MySQLConfig.from_yaml(tmp.name, "test_mysql")
        assert config.type == "mysql"
        assert config.host == "localhost"
        assert config.port == "3306"
        assert config.database == "test_db"
        assert config.user == "test_user"
        assert config.password == "test_pass"
        assert config.charset == "utf8mb4"

def test_ssl_config():
    """Test MySQL SSL configuration parsing"""
    config_data = {
        "connections": {
            "test_mysql": {
                "type": "mysql",
                "host": "localhost",
                "port": 3306,
                "database": "test_db",
                "user": "test_user",
                "password": "test_pass",
                "charset": "utf8mb4",
                "ssl": {
                    "mode": "verify_identity",
                    "ca": "/path/to/ca.pem",
                    "cert": "/path/to/client-cert.pem",
                    "key": "/path/to/client-key.pem"
                }
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(config_data, tmp)
        tmp.flush()
        
        config = MySQLConfig.from_yaml(tmp.name, "test_mysql")
        assert config.ssl is not None
        assert config.ssl.mode == "verify_identity"
        assert config.ssl.ca == "/path/to/ca.pem"
        assert config.ssl.cert == "/path/to/client-cert.pem"
        assert config.ssl.key == "/path/to/client-key.pem"

def test_ssl_url_config():
    """Test MySQL SSL configuration via URL parameters"""
    config_data = {
        "connections": {
            "test_mysql": {
                "type": "mysql",
                "url": "mysql://localhost:3306/test_db?ssl-mode=verify_identity&ssl-ca=/path/to/ca.pem",
                "user": "test_user",
                "password": "test_pass"
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(config_data, tmp)
        tmp.flush()
        
        config = MySQLConfig.from_yaml(tmp.name, "test_mysql")
        assert config.ssl is not None
        assert config.ssl.mode == "verify_identity"
        assert config.ssl.ca == "/path/to/ca.pem"

def test_invalid_type():
    """Test configuration with invalid database type"""
    config_data = {
        "connections": {
            "test_mysql": {
                "type": "postgres",
                "host": "localhost",
                "database": "test_db",
                "user": "test_user",
                "password": "test_pass"
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(config_data, tmp)
        tmp.flush()
        
        with pytest.raises(ValueError, match="Configuration is not MySQL type"):
            MySQLConfig.from_yaml(tmp.name, "test_mysql")

def test_missing_required_fields():
    """Test configuration with missing required fields"""
    config_data = {
        "connections": {
            "test_mysql": {
                "type": "mysql",
                "host": "localhost"
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(config_data, tmp)
        tmp.flush()
        
        with pytest.raises(ValueError, match="User must be specified"):
            MySQLConfig.from_yaml(tmp.name, "test_mysql")

def test_invalid_ssl_mode():
    """Test configuration with invalid SSL mode"""
    config_data = {
        "connections": {
            "test_mysql": {
                "type": "mysql",
                "host": "localhost",
                "port": 3306,
                "database": "test_db",
                "user": "test_user",
                "password": "test_pass",
                "ssl": {
                    "mode": "invalid_mode"
                }
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as tmp:
        yaml.dump(config_data, tmp)
        tmp.flush()
        
        with pytest.raises(ValueError, match="Invalid ssl-mode"):
            MySQLConfig.from_yaml(tmp.name, "test_mysql")

def test_masked_connection_info():
    """Test that sensitive connection information is properly masked"""
    config = MySQLConfig(
        database="test_db",
        user="test_user",
        password="secret",
        host="localhost",
        port="3306",
        charset="utf8mb4"
    )
    
    masked_info = config.get_masked_connection_info()
    assert "password" not in masked_info
    assert masked_info["database"] == "test_db"
    assert masked_info["host"] == "localhost"
    assert masked_info["port"] == "3306"
    assert masked_info["charset"] == "utf8mb4"
