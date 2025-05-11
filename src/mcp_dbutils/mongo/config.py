"""MongoDB configuration module"""
from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional
from urllib.parse import parse_qs, urlparse

from ..config import ConnectionConfig, WritePermissions


@dataclass
class MongoDBConfig(ConnectionConfig):
    """MongoDB connection configuration"""
    host: str = 'localhost'
    port: str = '27017'
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    auth_source: str = 'admin'
    uri: Optional[str] = None
    type: Literal['mongodb'] = 'mongodb'
    writable: bool = False  # Whether write operations are allowed
    write_permissions: Optional[WritePermissions] = None  # Write permissions configuration

    @classmethod
    def from_yaml(cls, yaml_path: str, db_name: str) -> 'MongoDBConfig':
        """Create configuration from YAML file

        Args:
            yaml_path: Path to YAML configuration file
            db_name: Connection configuration name to use
        """
        configs = cls.load_yaml_config(yaml_path)
        if not db_name:
            raise ValueError("Connection name must be specified")
        if db_name not in configs:
            available_dbs = list(configs.keys())
            raise ValueError(f"Connection configuration not found: {db_name}. Available configurations: {available_dbs}")

        db_config = configs[db_name]
        if 'type' not in db_config:
            raise ValueError("Connection configuration must include 'type' field")
        if db_config['type'] != 'mongodb':
            raise ValueError(f"Configuration is not MongoDB type: {db_config['type']}")

        # Get connection parameters
        if 'uri' in db_config:
            # Parse URI for connection parameters
            uri = db_config['uri']
            parsed = urlparse(uri)
            
            # Extract database name from URI
            database = parsed.path.lstrip('/') if parsed.path else db_config.get('database')
            if not database:
                raise ValueError("MongoDB database name must be specified in configuration or URI")
            
            # Extract host and port from URI
            host = parsed.hostname or 'localhost'
            port = str(parsed.port or 27017)
            
            # Extract username and password from URI
            username = parsed.username
            password = parsed.password
            
            # Extract auth_source from query parameters
            query_params = parse_qs(parsed.query)
            auth_source = query_params.get('authSource', ['admin'])[0]
            
            config = cls(
                database=database,
                host=host,
                port=port,
                username=username,
                password=password,
                auth_source=auth_source,
                uri=uri
            )
        else:
            # Use explicit configuration parameters
            if 'database' not in db_config:
                raise ValueError("MongoDB database name must be specified in configuration")
            
            config = cls(
                database=db_config['database'],
                host=db_config.get('host', 'localhost'),
                port=str(db_config.get('port', 27017)),
                username=db_config.get('username'),
                password=db_config.get('password'),
                auth_source=db_config.get('auth_source', 'admin')
            )

        # Parse write permissions
        config.writable = db_config.get('writable', False)
        if config.writable and 'write_permissions' in db_config:
            config.write_permissions = WritePermissions(db_config['write_permissions'])

        config.debug = cls.get_debug_mode()
        return config

    def get_connection_params(self) -> Dict[str, Any]:
        """Get MongoDB connection parameters"""
        if self.uri:
            return {'uri': self.uri}
        
        params = {
            'host': self.host,
            'port': int(self.port),
            'database': self.database,
            'auth_source': self.auth_source
        }
        
        if self.username:
            params['username'] = self.username
        if self.password:
            params['password'] = self.password
            
        return params

    def get_masked_connection_info(self) -> Dict[str, Any]:
        """Return masked connection information for logging"""
        info = {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'auth_source': self.auth_source
        }
        
        if self.username:
            info['username'] = self.username
            
        return info
