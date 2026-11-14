"""Oracle configuration module"""
from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional
from urllib.parse import parse_qs, urlparse

from ..config import ConnectionConfig, WritePermissions

def parse_url(url: str) -> Dict[str, Any]:
    """Parse Oracle URL into connection parameters

    Args:
        url: URL (e.g. oracle://host:port/service?user=xxx&password=xxx)
             or oracle:///?tns=MYTNSNAME&user=xxx&password=xxx

    Returns:
        Dictionary of connection parameters
    """
    if not url.startswith('oracle://'):
        raise ValueError("Invalid Oracle URL format")

    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)

    params = {
        'user': query_params.get('user', [None])[0],
        'password': query_params.get('password', [None])[0],
        'host': parsed.hostname or 'localhost',
        'port': str(parsed.port) if parsed.port else '1521',
        'service_name': parsed.path.lstrip('/') if parsed.path else None,
        'tns': query_params.get('tns', [None])[0],
        'dsn': query_params.get('dsn', [None])[0],
        'thick_mode': query_params.get('thick_mode', ['false'])[0].lower() == 'true',
        'client_lib_dir': query_params.get('client_lib_dir', [None])[0],
    }

    # 优先 dsn > tns > host/port/service_name
    if params['dsn']:
        params['final_dsn'] = params['dsn']
    elif params['tns']:
        params['final_dsn'] = params['tns']
    elif params['host'] and params['service_name']:
        params['final_dsn'] = f"{params['host']}:{params['port']}/{params['service_name']}"
    else:
        raise ValueError("Oracle DSN, TNS, or host/service_name must be specified in URL")

    return params

@dataclass
class OracleConfig(ConnectionConfig):
    user: str
    password: str
    host: Optional[str] = None
    port: Optional[str] = None
    service_name: Optional[str] = None
    tns: Optional[str] = None
    dsn: Optional[str] = None
    url: Optional[str] = None
    local_host: Optional[str] = None
    type: Literal['oracle'] = 'oracle'
    writable: bool = False
    write_permissions: Optional[WritePermissions] = None
    debug: bool = False
    thick_mode: bool = False  # 是否使用 thick mode 连接
    lib_dir: Optional[str] = None  # 可选的 Oracle 客户端库目录

    @classmethod
    def _validate_connection_config(cls, configs: dict, db_name: str) -> dict:
        if not db_name:
            raise ValueError("Connection name must be specified")
        if db_name not in configs:
            available_dbs = list(configs.keys())
            raise ValueError(f"Connection configuration not found: {db_name}. Available configurations: {available_dbs}")

        db_config = configs[db_name]
        if 'type' not in db_config:
            raise ValueError("Connection configuration must include 'type' field")
        if db_config['type'] != 'oracle':
            raise ValueError(f"Configuration is not Oracle type: {db_config['type']}")

        if not db_config.get('user'):
            raise ValueError("User must be specified in connection configuration")
        if not db_config.get('password'):
            raise ValueError("Password must be specified in connection configuration")

        return db_config

    @classmethod
    def _create_config_from_url(cls, db_config: dict, local_host: Optional[str] = None) -> 'OracleConfig':
        params = parse_url(db_config['url'])
        config = cls(
            user=params['user'] or db_config.get('user'),
            password=params['password'] or db_config.get('password'),
            host=params['host'],
            port=params['port'],
            service_name=params['service_name'],
            tns=params['tns'],
            dsn=params['final_dsn'],
            url=db_config['url'],
            local_host=local_host,
            thick_mode=params['thick_mode'] or db_config.get('thick_mode', False),
            lib_dir=db_config.get('client_lib_dir')
        )
        return config

    @classmethod
    def _create_config_from_params(cls, db_config: dict, local_host: Optional[str] = None) -> 'OracleConfig':
        # 支持 dsn/tns/host+service_name 三种方式
        dsn = db_config.get('dsn')
        tns = db_config.get('tns')
        host = db_config.get('host', 'localhost')
        port = str(db_config.get('port', '1521'))
        service_name = db_config.get('service_name')
        final_dsn = dsn or tns
        if not final_dsn and host and service_name:
            final_dsn = f"{host}:{port}/{service_name}"
        if not final_dsn:
            raise ValueError("Oracle DSN, TNS, or host/service_name must be specified in configuration")
        thick_mode = db_config.get('thick_mode', False)
        lib_dir = db_config.get('client_lib_dir')

        config = cls(
            user=db_config['user'],
            password=db_config['password'],
            host=host,
            port=port,
            service_name=service_name,
            tns=tns,
            dsn=final_dsn,
            local_host=local_host,
            thick_mode=thick_mode,
            lib_dir=lib_dir
        )
        return config

    @classmethod
    def from_yaml(cls, yaml_path: str, db_name: str, local_host: Optional[str] = None) -> 'OracleConfig':
        configs = cls.load_yaml_config(yaml_path)
        db_config = cls._validate_connection_config(configs, db_name)
        if 'url' in db_config:
            config = cls._create_config_from_url(db_config, local_host)
        else:
            config = cls._create_config_from_params(db_config, local_host)

        config.writable = db_config.get('writable', False)
        if config.writable and 'write_permissions' in db_config:
            config.write_permissions = WritePermissions(db_config['write_permissions'])

        config.debug = cls.get_debug_mode()
        return config

    @classmethod
    def from_url(
        cls,
        url: str,
        user: str,
        password: str,
        local_host: Optional[str] = None,
        writable: bool = False,
        write_permissions: Optional[Dict[str, Any]] = None,
        thick_mode: bool = False
    ) -> 'OracleConfig':
        params = parse_url(url)
        config = cls(
            user=user,
            password=password,
            host=params['host'],
            port=params['port'],
            service_name=params['service_name'],
            tns=params['tns'],
            dsn=params['final_dsn'],
            url=url,
            local_host=local_host,
            thick_mode=thick_mode,
            writable=writable,
        )
        if writable and write_permissions:
            config.write_permissions = WritePermissions(write_permissions)
        config.debug = cls.get_debug_mode()
        return config

    def get_connection_params(self) -> Dict[str, Any]:
        """Get Oracle connection parameters"""
        dsn = self.dsn or self.tns
        if not dsn and self.host and self.service_name:
            dsn = f"{self.host}:{self.port or '1521'}/{self.service_name}"
        params = {
            'user': self.user,
            'password': self.password,
            'dsn': dsn,
            'thick_mode': self.thick_mode,
        }
        # 支持 local_host 覆盖
        if self.local_host:
            params['dsn'] = f"{self.local_host}:{self.port or '1521'}/{self.service_name}"
        return {k: v for k, v in params.items() if v is not None}

    def get_masked_connection_info(self) -> Dict[str, Any]:
        """Return masked connection information for logging"""
        return {
            'dsn': self.dsn or self.tns or f"{self.host}:{self.port}/{self.service_name}",
            'user': self.user,
            'host': self.local_host or self.host,
            'port': self.port,
            'service_name': self.service_name,
            'thick_mode': self.thick_mode,
        }