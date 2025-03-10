"""PostgreSQL configuration module"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, Literal
from urllib.parse import urlparse, parse_qs
from ..config import ConnectionConfig

@dataclass
class SSLConfig:
    """SSL configuration for PostgreSQL connection"""
    mode: Literal['disable', 'require', 'verify-ca', 'verify-full'] = 'disable'
    cert: Optional[str] = None
    key: Optional[str] = None
    root: Optional[str] = None

def parse_url(url: str) -> Dict[str, Any]:
    """Parse PostgreSQL URL into connection parameters
    
    Args:
        url: URL (e.g. postgresql://host:port/dbname?sslmode=verify-full)
        
    Returns:
        Dictionary of connection parameters including SSL settings
    """
    if not url.startswith('postgresql://'):
        raise ValueError("Invalid PostgreSQL URL format")
    
    if '@' in url:
        raise ValueError("URL should not contain credentials. Please provide username and password separately.")
    
    # Parse URL and query parameters
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    params = {
        'host': parsed.hostname or 'localhost',
        'port': str(parsed.port or 5432),
        'dbname': parsed.path.lstrip('/') if parsed.path else '',
    }
    
    if not params['dbname']:
        raise ValueError("PostgreSQL database name must be specified in URL")

    # Parse SSL parameters if present
    ssl_params = {}
    if 'sslmode' in query_params:
        mode = query_params['sslmode'][0]
        if mode not in ['disable', 'require', 'verify-ca', 'verify-full']:
            raise ValueError(f"Invalid sslmode: {mode}")
        ssl_params['mode'] = mode
        
    if 'sslcert' in query_params:
        ssl_params['cert'] = query_params['sslcert'][0]
    if 'sslkey' in query_params:
        ssl_params['key'] = query_params['sslkey'][0]
    if 'sslrootcert' in query_params:
        ssl_params['root'] = query_params['sslrootcert'][0]
        
    if ssl_params:
        params['ssl'] = SSLConfig(**ssl_params)
        
    return params

@dataclass
class PostgreSQLConfig(ConnectionConfig):
    dbname: str
    user: str
    password: str
    host: str = 'localhost'
    port: str = '5432'
    local_host: Optional[str] = None
    type: Literal['postgres'] = 'postgres'
    url: Optional[str] = None
    ssl: Optional[SSLConfig] = None

    @classmethod
    def from_yaml(cls, yaml_path: str, db_name: str, local_host: Optional[str] = None) -> 'PostgreSQLConfig':
        """Create configuration from YAML file

        Args:
            yaml_path: Path to YAML configuration file
            db_name: Connection configuration name to use
            local_host: Optional local host address
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
        if db_config['type'] != 'postgres':
            raise ValueError(f"Configuration is not PostgreSQL type: {db_config['type']}")

        # Check required credentials
        if not db_config.get('user'):
            raise ValueError("User must be specified in connection configuration")
        if not db_config.get('password'):
            raise ValueError("Password must be specified in connection configuration")

        # Get connection parameters
        if 'url' in db_config:
            # Parse URL for connection parameters
            params = parse_url(db_config['url'])
            config = cls(
                dbname=params['dbname'],
                user=db_config['user'],
                password=db_config['password'],
                host=params['host'],
                port=params['port'],
                local_host=local_host,
                url=db_config['url'],
                ssl=params.get('ssl')
            )
        else:
            if not db_config.get('dbname'):
                raise ValueError("PostgreSQL database name must be specified in configuration")
            if not db_config.get('host'):
                raise ValueError("Host must be specified in connection configuration")
            if not db_config.get('port'):
                raise ValueError("Port must be specified in connection configuration")
            
            # Parse SSL configuration if present
            ssl_config = None
            if 'ssl' in db_config:
                ssl_params = db_config['ssl']
                if not isinstance(ssl_params, dict):
                    raise ValueError("SSL configuration must be a dictionary")
                
                if ssl_params.get('mode') not in [None, 'disable', 'require', 'verify-ca', 'verify-full']:
                    raise ValueError(f"Invalid sslmode: {ssl_params.get('mode')}")
                
                ssl_config = SSLConfig(
                    mode=ssl_params.get('mode', 'disable'),
                    cert=ssl_params.get('cert'),
                    key=ssl_params.get('key'),
                    root=ssl_params.get('root')
                )
            
            config = cls(
                dbname=db_config['dbname'],
                user=db_config['user'],
                password=db_config['password'],
                host=db_config['host'],
                port=str(db_config['port']),
                local_host=local_host,
                ssl=ssl_config
            )
        config.debug = cls.get_debug_mode()
        return config

    @classmethod
    def from_url(cls, url: str, user: str, password: str, 
                local_host: Optional[str] = None) -> 'PostgreSQLConfig':
        """Create configuration from URL and credentials
        
        Args:
            url: URL (postgresql://host:port/dbname)
            user: Username for connection
            password: Password for connection
            local_host: Optional local host address
            
        Raises:
            ValueError: If URL format is invalid or required parameters are missing
        """
        params = parse_url(url)
        
        config = cls(
            dbname=params['dbname'],
            user=user,
            password=password,
            host=params['host'],
            port=params['port'],
            local_host=local_host,
            url=url,
            ssl=params.get('ssl')
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
        
        # Add SSL parameters if configured
        if self.ssl:
            params['sslmode'] = self.ssl.mode
            if self.ssl.cert:
                params['sslcert'] = self.ssl.cert
            if self.ssl.key:
                params['sslkey'] = self.ssl.key
            if self.ssl.root:
                params['sslrootcert'] = self.ssl.root
                
        return {k: v for k, v in params.items() if v}

    def get_masked_connection_info(self) -> Dict[str, Any]:
        """Return masked connection information for logging"""
        return {
            'dbname': self.dbname,
            'host': self.local_host or self.host,
            'port': self.port
        }
