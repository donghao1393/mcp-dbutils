"""PostgreSQL configuration module"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, Literal
from urllib.parse import urlparse
from ..config import DatabaseConfig

def parse_jdbc_url(jdbc_url: str) -> Dict[str, str]:
    """Parse JDBC URL into connection parameters
    
    Args:
        jdbc_url: JDBC URL (e.g. jdbc:postgresql://host:port/dbname)
        
    Returns:
        Dictionary of connection parameters
    """
    if not jdbc_url.startswith('jdbc:postgresql://'):
        raise ValueError("Invalid PostgreSQL JDBC URL format")
    
    # Remove jdbc: prefix and ensure no credentials in URL
    url = jdbc_url[5:]
    if '@' in url:
        raise ValueError("JDBC URL should not contain credentials. Please provide username and password separately.")
    
    # Parse URL
    parsed = urlparse(url)
    
    params = {
        'host': parsed.hostname or 'localhost',
        'port': str(parsed.port or 5432),
        'dbname': parsed.path.lstrip('/') if parsed.path else '',
    }
    
    if not params['dbname']:
        raise ValueError("Database name must be specified in URL")
        
    return params

@dataclass
class PostgresConfig(DatabaseConfig):
    dbname: str
    user: str
    password: str
    host: str = 'localhost'
    port: str = '5432'
    local_host: Optional[str] = None
    type: Literal['postgres'] = 'postgres'

    @classmethod
    def from_yaml(cls, yaml_path: str, db_name: str, local_host: Optional[str] = None) -> 'PostgresConfig':
        """Create configuration from YAML file

        Args:
            yaml_path: Path to YAML configuration file
            db_name: Database configuration name to use
            local_host: Optional local host address
        """
        configs = cls.load_yaml_config(yaml_path)
        if not db_name:
            raise ValueError("Database name must be specified")
        if db_name not in configs:
            available_dbs = list(configs.keys())
            raise ValueError(f"Database configuration not found: {db_name}. Available configurations: {available_dbs}")

        db_config = configs[db_name]
        if 'type' not in db_config:
            raise ValueError("Database configuration must include 'type' field")
        if db_config['type'] != 'postgres':
            raise ValueError(f"Configuration is not PostgreSQL type: {db_config['type']}")

        # Check required credentials
        if not db_config.get('user'):
            raise ValueError("User must be specified in database configuration")
        if not db_config.get('password'):
            raise ValueError("Password must be specified in database configuration")

        # Get connection parameters
        if 'jdbc_url' in db_config:
            # Parse JDBC URL for connection parameters
            params = parse_jdbc_url(db_config['jdbc_url'])
            config = cls(
                dbname=params['dbname'],
                user=db_config['user'],
                password=db_config['password'],
                host=params['host'],
                port=params['port'],
                local_host=local_host,
            )
        else:
            if not db_config.get('dbname'):
                raise ValueError("Database name must be specified in configuration")
            if not db_config.get('host'):
                raise ValueError("Host must be specified in configuration")
            if not db_config.get('port'):
                raise ValueError("Port must be specified in configuration")
            config = cls(
                dbname=db_config['dbname'],
                user=db_config['user'],
                password=db_config['password'],
                host=db_config['host'],
                port=str(db_config['port']),
                local_host=local_host,
            )
        config.debug = cls.get_debug_mode()
        return config

    @classmethod
    def from_jdbc_url(cls, jdbc_url: str, user: str, password: str, 
                     local_host: Optional[str] = None) -> 'PostgresConfig':
        """Create configuration from JDBC URL and credentials
        
        Args:
            jdbc_url: JDBC URL (jdbc:postgresql://host:port/dbname)
            user: Username for database connection
            password: Password for database connection
            local_host: Optional local host address
            
        Raises:
            ValueError: If URL format is invalid or required parameters are missing
        """
        params = parse_jdbc_url(jdbc_url)
        
        config = cls(
            dbname=params['dbname'],
            user=user,
            password=password,
            host=params['host'],
            port=params['port'],
            local_host=local_host,
        )
        config.debug = cls.get_debug_mode()
        return config

    def get_connection_params(self) -> Dict[str, Any]:
        """Get psycopg2 connection parameters"""
        params = {
            'dbname': self.dbname,
            'user': self.user,
            'password': self.password,
            'host': self.local_host or self.host,
            'port': self.port
        }
        return {k: v for k, v in params.items() if v}

    def get_masked_connection_info(self) -> Dict[str, Any]:
        """Return masked connection information for logging"""
        return {
            'dbname': self.dbname,
            'host': self.local_host or self.host,
            'port': self.port
        }
