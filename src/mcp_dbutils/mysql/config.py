"""MySQL configuration module"""
from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional
from urllib.parse import parse_qs, urlparse

from ..config import ConnectionConfig, WritePermissions


@dataclass
class SSLConfig:
    """SSL configuration for MySQL connection"""
    mode: Literal['disabled', 'required', 'verify_ca', 'verify_identity'] = 'disabled'
    ca: Optional[str] = None
    cert: Optional[str] = None
    key: Optional[str] = None

def parse_url(url: str) -> Dict[str, Any]:
    """Parse MySQL URL into connection parameters

    Args:
        url: URL (e.g. mysql://host:port/dbname?ssl-mode=verify_identity)

    Returns:
        Dictionary of connection parameters including SSL settings
    """
    if not url.startswith('mysql://'):
        raise ValueError("Invalid MySQL URL format")

    if '@' in url:
        raise ValueError("URL should not contain credentials. Please provide username and password separately.")

    # Parse URL and query parameters
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)

    params = {
        'host': parsed.hostname or 'localhost',
        'port': str(parsed.port or 3306),
        'database': parsed.path.lstrip('/') if parsed.path else '',
        'charset': query_params.get('charset', ['utf8mb4'])[0]
    }

    if not params['database']:
        raise ValueError("MySQL database name must be specified in URL")

    # Parse SSL parameters if present
    ssl_params = {}
    if 'ssl-mode' in query_params:
        mode = query_params['ssl-mode'][0]
        if mode not in ['disabled', 'required', 'verify_ca', 'verify_identity']:
            raise ValueError(f"Invalid ssl-mode: {mode}")
        ssl_params['mode'] = mode

    if 'ssl-ca' in query_params:
        ssl_params['ca'] = query_params['ssl-ca'][0]
    if 'ssl-cert' in query_params:
        ssl_params['cert'] = query_params['ssl-cert'][0]
    if 'ssl-key' in query_params:
        ssl_params['key'] = query_params['ssl-key'][0]

    if ssl_params:
        params['ssl'] = SSLConfig(**ssl_params)

    return params

@dataclass
class MySQLConfig(ConnectionConfig):
    database: str
    user: str
    password: str
    host: str = 'localhost'
    port: str = '3306'
    charset: str = 'utf8mb4'
    local_host: Optional[str] = None
    type: Literal['mysql'] = 'mysql'
    url: Optional[str] = None
    ssl: Optional[SSLConfig] = None
    writable: bool = False  # Whether write operations are allowed
    write_permissions: Optional[WritePermissions] = None  # Write permissions configuration

    @classmethod
    def _validate_connection_config(cls, configs: dict, db_name: str) -> dict:
        """验证连接配置是否有效

        Args:
            configs: 配置字典
            db_name: 连接名称

        Returns:
            dict: 数据库配置

        Raises:
            ValueError: 如果配置无效
        """
        if not db_name:
            raise ValueError("Connection name must be specified")
        if db_name not in configs:
            available_dbs = list(configs.keys())
            raise ValueError(f"Connection configuration not found: {db_name}. Available configurations: {available_dbs}")

        db_config = configs[db_name]
        if 'type' not in db_config:
            raise ValueError("Connection configuration must include 'type' field")
        if db_config['type'] != 'mysql':
            raise ValueError(f"Configuration is not MySQL type: {db_config['type']}")

        # Check required credentials
        if not db_config.get('user'):
            raise ValueError("User must be specified in connection configuration")
        if not db_config.get('password'):
            raise ValueError("Password must be specified in connection configuration")

        return db_config

    @classmethod
    def _create_config_from_url(cls, db_config: dict, local_host: Optional[str] = None) -> 'MySQLConfig':
        """从URL创建配置

        Args:
            db_config: 数据库配置
            local_host: 可选的本地主机地址

        Returns:
            MySQLConfig: 配置对象
        """
        # Parse URL for connection parameters
        params = parse_url(db_config['url'])
        config = cls(
            database=params['database'],
            user=db_config['user'],
            password=db_config['password'],
            host=params['host'],
            port=params['port'],
            charset=params['charset'],
            local_host=local_host,
            url=db_config['url'],
            ssl=params.get('ssl')
        )
        return config

    @classmethod
    def _create_config_from_params(cls, db_config: dict, local_host: Optional[str] = None) -> 'MySQLConfig':
        """从参数创建配置

        Args:
            db_config: 数据库配置
            local_host: 可选的本地主机地址

        Returns:
            MySQLConfig: 配置对象

        Raises:
            ValueError: 如果缺少必需参数或SSL配置无效
        """
        if not db_config.get('database'):
            raise ValueError("MySQL database name must be specified in configuration")
        if not db_config.get('host'):
            raise ValueError("Host must be specified in connection configuration")
        if not db_config.get('port'):
            raise ValueError("Port must be specified in connection configuration")

        # Parse SSL configuration if present
        ssl_config = cls._parse_ssl_config(db_config)

        config = cls(
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            port=str(db_config['port']),
            charset=db_config.get('charset', 'utf8mb4'),
            local_host=local_host,
            ssl=ssl_config
        )
        return config

    @classmethod
    def _parse_ssl_config(cls, db_config: dict) -> Optional[SSLConfig]:
        """解析SSL配置

        Args:
            db_config: 数据库配置

        Returns:
            Optional[SSLConfig]: SSL配置或None

        Raises:
            ValueError: 如果SSL配置无效
        """
        if 'ssl' not in db_config:
            return None

        ssl_params = db_config['ssl']
        if not isinstance(ssl_params, dict):
            raise ValueError("SSL configuration must be a dictionary")

        if ssl_params.get('mode') not in [None, 'disabled', 'required', 'verify_ca', 'verify_identity']:
            raise ValueError(f"Invalid ssl-mode: {ssl_params.get('mode')}")

        return SSLConfig(
            mode=ssl_params.get('mode', 'disabled'),
            ca=ssl_params.get('ca'),
            cert=ssl_params.get('cert'),
            key=ssl_params.get('key')
        )

    @classmethod
    def from_yaml(cls, yaml_path: str, db_name: str, local_host: Optional[str] = None) -> 'MySQLConfig':
        """Create configuration from YAML file

        Args:
            yaml_path: Path to YAML configuration file
            db_name: Connection configuration name to use
            local_host: Optional local host address
        """
        configs = cls.load_yaml_config(yaml_path)

        # Validate connection config
        db_config = cls._validate_connection_config(configs, db_name)

        # Create configuration based on URL or parameters
        if 'url' in db_config:
            config = cls._create_config_from_url(db_config, local_host)
        else:
            config = cls._create_config_from_params(db_config, local_host)

        # Parse write permissions
        config.writable = db_config.get('writable', False)
        if config.writable and 'write_permissions' in db_config:
            config.write_permissions = WritePermissions(db_config['write_permissions'])

        config.debug = cls.get_debug_mode()
        return config

    @classmethod
    def from_url(cls, url: str, user: str, password: str,
                local_host: Optional[str] = None,
                writable: bool = False,
                write_permissions: Optional[Dict[str, Any]] = None) -> 'MySQLConfig':
        """Create configuration from URL and credentials

        Args:
            url: URL (mysql://host:port/dbname)
            user: Username for connection
            password: Password for connection
            local_host: Optional local host address
            writable: Whether write operations are allowed
            write_permissions: Write permissions configuration

        Raises:
            ValueError: If URL format is invalid or required parameters are missing
        """
        params = parse_url(url)

        config = cls(
            database=params['database'],
            user=user,
            password=password,
            host=params['host'],
            port=params['port'],
            charset=params['charset'],
            local_host=local_host,
            url=url,
            ssl=params.get('ssl'),
            writable=writable
        )

        # Parse write permissions
        if writable and write_permissions:
            config.write_permissions = WritePermissions(write_permissions)

        config.debug = cls.get_debug_mode()
        return config

    def get_connection_params(self) -> Dict[str, Any]:
        """Get MySQL connection parameters"""
        params = {
            'database': self.database,
            'user': self.user,
            'password': self.password,
            'host': self.local_host or self.host,
            'port': int(self.port),
            'charset': self.charset,
            'use_unicode': True
        }

        # Add SSL parameters if configured
        if self.ssl:
            params['ssl_mode'] = self.ssl.mode
            if self.ssl.ca:
                params['ssl_ca'] = self.ssl.ca
            if self.ssl.cert:
                params['ssl_cert'] = self.ssl.cert
            if self.ssl.key:
                params['ssl_key'] = self.ssl.key

        return {k: v for k, v in params.items() if v is not None}

    def get_masked_connection_info(self) -> Dict[str, Any]:
        """Return masked connection information for logging"""
        return {
            'database': self.database,
            'host': self.local_host or self.host,
            'port': self.port,
            'charset': self.charset
        }
