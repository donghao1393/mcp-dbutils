"""Test MySQL configuration helper methods"""

import tempfile

import pytest
import yaml

from mcp_dbutils.mysql.config import MySQLConfig, SSLConfig


def test_validate_connection_config():
    """Test _validate_connection_config with valid configuration"""
    config_data = {
        "test_mysql": {
            "type": "mysql",
            "host": "localhost",
            "port": 3306,
            "database": "test_db",
            "user": "test_user",
            "password": "test_pass"
        }
    }
    
    result = MySQLConfig._validate_connection_config(config_data, "test_mysql")
    assert result == config_data["test_mysql"]


def test_validate_connection_config_missing_db_name():
    """Test _validate_connection_config with missing db_name"""
    config_data = {
        "test_mysql": {
            "type": "mysql",
            "host": "localhost"
        }
    }
    
    with pytest.raises(ValueError, match="Connection name must be specified"):
        MySQLConfig._validate_connection_config(config_data, "")


def test_validate_connection_config_missing_connection():
    """Test _validate_connection_config with non-existent connection"""
    config_data = {
        "test_mysql": {
            "type": "mysql",
            "host": "localhost"
        }
    }
    
    with pytest.raises(ValueError, match="Connection configuration not found"):
        MySQLConfig._validate_connection_config(config_data, "nonexistent")


def test_validate_connection_config_missing_type():
    """Test _validate_connection_config with missing type"""
    config_data = {
        "test_mysql": {
            "host": "localhost",
            "user": "test_user",
            "password": "test_pass"
        }
    }
    
    with pytest.raises(ValueError, match="Connection configuration must include 'type' field"):
        MySQLConfig._validate_connection_config(config_data, "test_mysql")


def test_validate_connection_config_wrong_type():
    """Test _validate_connection_config with wrong type"""
    config_data = {
        "test_mysql": {
            "type": "postgres",
            "host": "localhost",
            "user": "test_user",
            "password": "test_pass"
        }
    }
    
    with pytest.raises(ValueError, match="Configuration is not MySQL type"):
        MySQLConfig._validate_connection_config(config_data, "test_mysql")


def test_validate_connection_config_missing_user():
    """Test _validate_connection_config with missing user"""
    config_data = {
        "test_mysql": {
            "type": "mysql",
            "host": "localhost",
            "password": "test_pass"
        }
    }
    
    with pytest.raises(ValueError, match="User must be specified"):
        MySQLConfig._validate_connection_config(config_data, "test_mysql")


def test_validate_connection_config_missing_password():
    """Test _validate_connection_config with missing password"""
    config_data = {
        "test_mysql": {
            "type": "mysql",
            "host": "localhost",
            "user": "test_user"
        }
    }
    
    with pytest.raises(ValueError, match="Password must be specified"):
        MySQLConfig._validate_connection_config(config_data, "test_mysql")


def test_create_config_from_url():
    """Test _create_config_from_url with valid URL"""
    db_config = {
        "url": "mysql://localhost:3306/test_db?charset=utf8mb4",
        "user": "test_user",
        "password": "test_pass"
    }
    
    config = MySQLConfig._create_config_from_url(db_config)
    
    assert config.host == "localhost"
    assert config.port == "3306"
    assert config.database == "test_db"
    assert config.user == "test_user"
    assert config.password == "test_pass"
    assert config.charset == "utf8mb4"
    assert config.url == "mysql://localhost:3306/test_db?charset=utf8mb4"


def test_create_config_from_url_with_ssl():
    """Test _create_config_from_url with SSL parameters"""
    db_config = {
        "url": "mysql://localhost:3306/test_db?ssl-mode=verify_identity&ssl-ca=/path/to/ca.pem",
        "user": "test_user",
        "password": "test_pass"
    }
    
    config = MySQLConfig._create_config_from_url(db_config)
    
    assert config.ssl is not None
    assert config.ssl.mode == "verify_identity"
    assert config.ssl.ca == "/path/to/ca.pem"


def test_create_config_from_url_with_local_host():
    """Test _create_config_from_url with local_host parameter"""
    db_config = {
        "url": "mysql://db.example.com:3306/test_db",
        "user": "test_user",
        "password": "test_pass"
    }
    
    config = MySQLConfig._create_config_from_url(db_config, local_host="127.0.0.1")
    
    assert config.host == "db.example.com"
    assert config.local_host == "127.0.0.1"


def test_create_config_from_params():
    """Test _create_config_from_params with valid parameters"""
    db_config = {
        "database": "test_db",
        "host": "localhost",
        "port": 3306,
        "user": "test_user",
        "password": "test_pass",
        "charset": "utf8mb4"
    }
    
    config = MySQLConfig._create_config_from_params(db_config)
    
    assert config.database == "test_db"
    assert config.host == "localhost"
    assert config.port == "3306"
    assert config.user == "test_user"
    assert config.password == "test_pass"
    assert config.charset == "utf8mb4"


def test_create_config_from_params_missing_database():
    """Test _create_config_from_params with missing database"""
    db_config = {
        "host": "localhost",
        "port": 3306,
        "user": "test_user",
        "password": "test_pass"
    }
    
    with pytest.raises(ValueError, match="MySQL database name must be specified"):
        MySQLConfig._create_config_from_params(db_config)


def test_create_config_from_params_missing_host():
    """Test _create_config_from_params with missing host"""
    db_config = {
        "database": "test_db",
        "port": 3306,
        "user": "test_user",
        "password": "test_pass"
    }
    
    with pytest.raises(ValueError, match="Host must be specified"):
        MySQLConfig._create_config_from_params(db_config)


def test_create_config_from_params_missing_port():
    """Test _create_config_from_params with missing port"""
    db_config = {
        "database": "test_db",
        "host": "localhost",
        "user": "test_user",
        "password": "test_pass"
    }
    
    with pytest.raises(ValueError, match="Port must be specified"):
        MySQLConfig._create_config_from_params(db_config)


def test_create_config_from_params_with_ssl():
    """Test _create_config_from_params with SSL configuration"""
    db_config = {
        "database": "test_db",
        "host": "localhost",
        "port": 3306,
        "user": "test_user",
        "password": "test_pass",
        "ssl": {
            "mode": "verify_identity",
            "ca": "/path/to/ca.pem",
            "cert": "/path/to/client-cert.pem",
            "key": "/path/to/client-key.pem"
        }
    }
    
    config = MySQLConfig._create_config_from_params(db_config)
    
    assert config.ssl is not None
    assert config.ssl.mode == "verify_identity"
    assert config.ssl.ca == "/path/to/ca.pem"
    assert config.ssl.cert == "/path/to/client-cert.pem"
    assert config.ssl.key == "/path/to/client-key.pem"


def test_parse_ssl_config():
    """Test _parse_ssl_config with valid SSL config"""
    db_config = {
        "ssl": {
            "mode": "verify_identity",
            "ca": "/path/to/ca.pem",
            "cert": "/path/to/client-cert.pem",
            "key": "/path/to/client-key.pem"
        }
    }
    
    ssl_config = MySQLConfig._parse_ssl_config(db_config)
    
    assert ssl_config is not None
    assert ssl_config.mode == "verify_identity"
    assert ssl_config.ca == "/path/to/ca.pem"
    assert ssl_config.cert == "/path/to/client-cert.pem"
    assert ssl_config.key == "/path/to/client-key.pem"


def test_parse_ssl_config_missing_ssl():
    """Test _parse_ssl_config with missing SSL config"""
    db_config = {
        "host": "localhost",
        "port": 3306
    }
    
    ssl_config = MySQLConfig._parse_ssl_config(db_config)
    
    assert ssl_config is None


def test_parse_ssl_config_invalid_type():
    """Test _parse_ssl_config with invalid SSL config type"""
    db_config = {
        "ssl": "enable"  # Should be a dict
    }
    
    with pytest.raises(ValueError, match="SSL configuration must be a dictionary"):
        MySQLConfig._parse_ssl_config(db_config)


def test_parse_ssl_config_invalid_mode():
    """Test _parse_ssl_config with invalid SSL mode"""
    db_config = {
        "ssl": {
            "mode": "invalid_mode",
            "ca": "/path/to/ca.pem"
        }
    }
    
    with pytest.raises(ValueError, match="Invalid ssl-mode"):
        MySQLConfig._parse_ssl_config(db_config) 