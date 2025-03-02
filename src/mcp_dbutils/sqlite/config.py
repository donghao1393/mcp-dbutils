"""SQLite configuration module"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, Literal
from urllib.parse import urlparse, parse_qs
from ..config import DatabaseConfig

def parse_jdbc_url(jdbc_url: str) -> Dict[str, str]:
    """Parse JDBC URL into connection parameters

    Args:
        jdbc_url: JDBC URL (e.g. jdbc:sqlite:file:/path/to/database.db or jdbc:sqlite:/path/to/database.db)

    Returns:
        Dictionary of connection parameters

    Raises:
        ValueError: If URL format is invalid
    """
    if not jdbc_url.startswith('jdbc:sqlite:'):
        raise ValueError("Invalid SQLite JDBC URL format")

    # Remove jdbc:sqlite: prefix
    url = jdbc_url[12:]

    # Handle file: prefix
    if url.startswith('file:'):
        url = url[5:]

    # Parse URL
    parsed = urlparse(url)
    path = parsed.path

    # Extract query parameters
    params = {}
    if parsed.query:
        query_params = parse_qs(parsed.query)
        for key, values in query_params.items():
            params[key] = values[0]

    if not path:
        raise ValueError("Database path must be specified in URL")

    return {
        'path': path,
        'parameters': params
    }

@dataclass
class SqliteConfig(DatabaseConfig):
    path: str
    password: Optional[str] = None
    uri: bool = True  # Enable URI mode to support parameters like password
    type: Literal['sqlite'] = 'sqlite'

    @classmethod
    def from_jdbc_url(cls, jdbc_url: str, password: Optional[str] = None) -> 'SqliteConfig':
        """Create configuration from JDBC URL

        Args:
            jdbc_url: JDBC URL (e.g. jdbc:sqlite:file:/path/to/database.db)
            password: Optional password for database encryption

        Returns:
            SqliteConfig instance

        Raises:
            ValueError: If URL format is invalid
        """
        params = parse_jdbc_url(jdbc_url)

        config = cls(
            path=params['path'],
            password=password,
            uri=True
        )
        config.debug = cls.get_debug_mode()
        return config

    @property
    def absolute_path(self) -> str:
        """Return absolute path to database file"""
        return str(Path(self.path).expanduser().resolve())

    def get_connection_params(self) -> Dict[str, Any]:
        """Get sqlite3 connection parameters"""
        if not self.password:
            return {'database': self.absolute_path, 'uri': self.uri}

        # Use URI format if password is provided
        uri = f"file:{self.absolute_path}?mode=rw"
        if self.password:
            uri += f"&password={self.password}"

        return {
            'database': uri,
            'uri': True
        }

    def get_masked_connection_info(self) -> Dict[str, Any]:
        """Return connection information for logging"""
        info = {
            'database': self.absolute_path,
            'uri': self.uri
        }
        if self.password:
            info['password'] = '******'
        return info

    @classmethod
    def from_yaml(cls, yaml_path: str, db_name: str, **kwargs) -> 'SqliteConfig':
        """Create SQLite configuration from YAML

        Args:
            yaml_path: Path to YAML configuration file
            db_name: Database configuration name
        """
        configs = cls.load_yaml_config(yaml_path)

        if db_name not in configs:
            available_dbs = list(configs.keys())
            raise ValueError(f"Database configuration not found: {db_name}. Available configurations: {available_dbs}")

        db_config = configs[db_name]

        if 'type' not in db_config:
            raise ValueError("Database configuration must include 'type' field")
        if db_config['type'] != 'sqlite':
            raise ValueError(f"Configuration is not SQLite type: {db_config['type']}")

        # Check if using JDBC URL configuration
        if 'jdbc_url' in db_config:
            params = parse_jdbc_url(db_config['jdbc_url'])
            config = cls(
                path=params['path'],
                password=db_config.get('password'),
                uri=True
            )
        else:
            if 'path' not in db_config:
                raise ValueError("SQLite configuration must include 'path' field")
            config = cls(
                path=db_config['path'],
                password=db_config.get('password'),
                uri=True
            )

        config.debug = cls.get_debug_mode()
        return config
