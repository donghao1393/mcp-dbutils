"""Test PostgreSQL configuration functionality"""
import pytest
import tempfile
import yaml
from mcp_dbutils.postgres.config import PostgreSQLConfig, parse_url, SSLConfig

def test_parse_url():
    """Test URL parsing"""
    # Test basic URL
    url = "postgresql://localhost:5432/testdb"
    params = parse_url(url)
    assert params["host"] == "localhost"
    assert params["port"] == "5432"
    assert params["dbname"] == "testdb"

    # Test URL with credentials (should fail)
    with pytest.raises(ValueError, match="should not contain credentials"):
        parse_url("postgresql://user:pass@localhost:5432/testdb")

    # Test invalid format
    with pytest.raises(ValueError, match="Invalid PostgreSQL URL format"):
        parse_url("postgres://localhost:5432/testdb")

    # Test missing database name
    with pytest.raises(ValueError, match="PostgreSQL database name must be specified"):
        parse_url("postgresql://localhost:5432")

    # Test URL with SSL parameters
    url = "postgresql://localhost:5432/testdb?sslmode=verify-full&sslcert=/path/to/cert.pem"
    params = parse_url(url)
    assert params["ssl"].mode == "verify-full"
    assert params["ssl"].cert == "/path/to/cert.pem"

    # Test invalid SSL mode
    with pytest.raises(ValueError, match="Invalid sslmode"):
        parse_url("postgresql://localhost:5432/testdb?sslmode=invalid")

def test_from_url():
    """Test PostgreSQLConfig creation from URL"""
    url = "postgresql://localhost:5432/testdb?sslmode=verify-full"
    config = PostgreSQLConfig.from_url(
        url, 
        user="test_user",
        password="test_pass"
    )

    assert config.dbname == "testdb"
    assert config.host == "localhost"
    assert config.port == "5432"
    assert config.user == "test_user"
    assert config.password == "test_pass"
    assert config.type == "postgres"
    assert config.ssl.mode == "verify-full"

def test_from_yaml_with_url(tmp_path):
    """Test PostgreSQLConfig creation from YAML with URL"""
    config_data = {
        "connections": {
            "test_db": {
                "type": "postgres",
                "url": "postgresql://localhost:5432/testdb?sslmode=verify-full",
                "user": "test_user",
                "password": "test_pass"
            }
        }
    }

    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    config = PostgreSQLConfig.from_yaml(str(config_file), "test_db")
    assert config.dbname == "testdb"
    assert config.host == "localhost"
    assert config.port == "5432"
    assert config.user == "test_user"
    assert config.password == "test_pass"
    assert config.type == "postgres"
    assert config.ssl.mode == "verify-full"

def test_from_yaml_with_ssl_config(tmp_path):
    """Test PostgreSQLConfig creation from YAML with SSL configuration"""
    config_data = {
        "connections": {
            "test_db": {
                "type": "postgres",
                "host": "localhost",
                "port": 5432,
                "dbname": "testdb",
                "user": "test_user",
                "password": "test_pass",
                "ssl": {
                    "mode": "verify-full",
                    "cert": "/path/to/cert.pem",
                    "key": "/path/to/key.pem",
                    "root": "/path/to/root.crt"
                }
            }
        }
    }
    
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    config = PostgreSQLConfig.from_yaml(str(config_file), "test_db")
    assert config.ssl is not None
    assert config.ssl.mode == "verify-full"
    assert config.ssl.cert == "/path/to/cert.pem"
    assert config.ssl.key == "/path/to/key.pem"
    assert config.ssl.root == "/path/to/root.crt"

def test_invalid_ssl_config(tmp_path):
    """Test invalid SSL configuration validation"""
    # Invalid SSL mode
    config_data = {
        "connections": {
            "test_db": {
                "type": "postgres",
                "host": "localhost",
                "port": 5432,
                "dbname": "testdb",
                "user": "test_user",
                "password": "test_pass",
                "ssl": {
                    "mode": "invalid_mode"
                }
            }
        }
    }
    
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    with pytest.raises(ValueError, match="Invalid sslmode"):
        PostgreSQLConfig.from_yaml(str(config_file), "test_db")

    # Invalid SSL config type
    config_data["connections"]["test_db"]["ssl"] = "not_a_dict"
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    with pytest.raises(ValueError, match="SSL configuration must be a dictionary"):
        PostgreSQLConfig.from_yaml(str(config_file), "test_db")

def test_required_fields_validation(tmp_path):
    """Test validation of required configuration fields"""
    # Missing user
    config_data = {
        "connections": {
            "test_db": {
                "type": "postgres",
                "host": "localhost",
                "port": 5432,
                "dbname": "testdb",
                "password": "test_pass"
            }
        }
    }
    
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    with pytest.raises(ValueError, match="User must be specified in connection"):
        PostgreSQLConfig.from_yaml(str(config_file), "test_db")

    # Missing password
    config_data["connections"]["test_db"]["user"] = "test_user"
    del config_data["connections"]["test_db"]["password"]
    
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    with pytest.raises(ValueError, match="Password must be specified in connection"):
        PostgreSQLConfig.from_yaml(str(config_file), "test_db")

    # Missing host
    config_data["connections"]["test_db"]["password"] = "test_pass"
    del config_data["connections"]["test_db"]["host"]
    
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    with pytest.raises(ValueError, match="Host must be specified in connection"):
        PostgreSQLConfig.from_yaml(str(config_file), "test_db")

    # Missing port
    config_data["connections"]["test_db"]["host"] = "localhost"
    del config_data["connections"]["test_db"]["port"]
    
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    with pytest.raises(ValueError, match="Port must be specified in connection"):
        PostgreSQLConfig.from_yaml(str(config_file), "test_db")

    # Missing database name
    config_data["connections"]["test_db"]["port"] = 5432
    del config_data["connections"]["test_db"]["dbname"]
    
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    with pytest.raises(ValueError, match="PostgreSQL database name must be specified"):
        PostgreSQLConfig.from_yaml(str(config_file), "test_db")

def test_get_connection_params():
    """Test connection parameters generation with SSL"""
    config = PostgreSQLConfig(
        dbname="testdb",
        user="test_user",
        password="test_pass",
        host="localhost",
        port="5432",
        ssl=SSLConfig(
            mode="verify-full",
            cert="/path/to/cert.pem",
            key="/path/to/key.pem",
            root="/path/to/root.crt"
        )
    )

    params = config.get_connection_params()
    assert params["sslmode"] == "verify-full"
    assert params["sslcert"] == "/path/to/cert.pem"
    assert params["sslkey"] == "/path/to/key.pem"
    assert params["sslrootcert"] == "/path/to/root.crt"
