"""Common configuration utilities"""

import os
import yaml
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Literal
from pathlib import Path

# Supported connection types
ConnectionType = Literal['sqlite', 'postgres', 'mysql']

class ConnectionConfig(ABC):
    """Base class for connection configuration"""

    debug: bool = False
    type: ConnectionType  # Connection type

    @abstractmethod
    def get_connection_params(self) -> Dict[str, Any]:
        """Get connection parameters"""
        pass

    @abstractmethod
    def get_masked_connection_info(self) -> Dict[str, Any]:
        """Get masked connection information for logging"""
        pass

    @classmethod
    def load_yaml_config(cls, yaml_path: str) -> Dict[str, Any]:
        """Load YAML configuration file

        Args:
            yaml_path: Path to YAML file

        Returns:
            Parsed configuration dictionary
        """
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        if not config or 'connections' not in config:
            raise ValueError("Configuration file must contain 'connections' section")

        # Validate type field in each database configuration
        connections = config['connections']
        for conn_name, db_config in connections.items():
            if 'type' not in db_config:
                raise ValueError(f"Database configuration {conn_name} missing required 'type' field")
            db_type = db_config['type']
            if db_type not in ('sqlite', 'postgres', 'mysql'):
                raise ValueError(f"Invalid type value in database configuration {conn_name}: {db_type}")

        return connections

    @classmethod
    def get_debug_mode(cls) -> bool:
        """Get debug mode status"""
        return os.environ.get('MCP_DEBUG', '').lower() in ('1', 'true')
