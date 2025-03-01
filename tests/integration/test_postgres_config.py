"""Test PostgreSQL configuration functionality"""
import pytest
import tempfile
import yaml
from mcp_dbutils.postgres.config import PostgresConfig, parse_jdbc_url

def test_parse_jdbc_url():
    """Test JDBC URL parsing"""
    # Test valid URL
    url = "jdbc:postgresql://localhost:5432/testdb"
    params = parse_jdbc_url(url)
    assert params["host"] == "localhost"
    assert params["port"] == "5432"
    assert params["dbname"] == "testdb"

    # Test URL with credentials (should fail)
    with pytest.raises(ValueError, match="should not contain credentials"):
        parse_jdbc_url("jdbc:postgresql://user:pass@localhost:5432/testdb")

    # Test invalid format
    with pytest.raises(ValueError, match="Invalid PostgreSQL JDBC URL format"):
        parse_jdbc_url("postgresql://localhost:5432/testdb")

    # Test missing database name
    with pytest.raises(ValueError, match="Database name must be specified"):
        parse_jdbc_url("jdbc:postgresql://localhost:5432")

def test_from_jdbc_url():
    """Test PostgresConfig creation from JDBC URL"""
    url = "jdbc:postgresql://localhost:5432/testdb"
    config = PostgresConfig.from_jdbc_url(
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

def test_from_yaml_with_jdbc_url(tmp_path):
    """Test PostgresConfig creation from YAML with JDBC URL"""
    config_data = {
        "databases": {
            "test_db": {
                "type": "postgres",
                "jdbc_url": "jdbc:postgresql://localhost:5432/testdb",
                "user": "test_user",
                "password": "test_pass"
            }
        }
    }

    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    config = PostgresConfig.from_yaml(str(config_file), "test_db")
    assert config.dbname == "testdb"
    assert config.host == "localhost"
    assert config.port == "5432"
    assert config.user == "test_user"
    assert config.password == "test_pass"
    assert config.type == "postgres"

def test_required_fields_validation(tmp_path):
    """Test validation of required configuration fields"""
    # Missing user
    config_data = {
        "databases": {
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

    with pytest.raises(ValueError, match="User must be specified"):
        PostgresConfig.from_yaml(str(config_file), "test_db")

    # Missing password
    config_data["databases"]["test_db"]["user"] = "test_user"
    del config_data["databases"]["test_db"]["password"]
    
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    with pytest.raises(ValueError, match="Password must be specified"):
        PostgresConfig.from_yaml(str(config_file), "test_db")

    # Missing host
    config_data["databases"]["test_db"]["password"] = "test_pass"
    del config_data["databases"]["test_db"]["host"]
    
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    with pytest.raises(ValueError, match="Host must be specified"):
        PostgresConfig.from_yaml(str(config_file), "test_db")

    # Missing port
    config_data["databases"]["test_db"]["host"] = "localhost"
    del config_data["databases"]["test_db"]["port"]
    
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    with pytest.raises(ValueError, match="Port must be specified"):
        PostgresConfig.from_yaml(str(config_file), "test_db")

    # Missing database name
    config_data["databases"]["test_db"]["port"] = 5432
    del config_data["databases"]["test_db"]["dbname"]
    
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    with pytest.raises(ValueError, match="Database name must be specified"):
        PostgresConfig.from_yaml(str(config_file), "test_db")
