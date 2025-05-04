"""Common configuration utilities"""

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal, Optional, Set, Union

import yaml

# Supported connection types
ConnectionType = Literal['sqlite', 'postgres', 'mysql']

# Supported write operations
WriteOperationType = Literal['INSERT', 'UPDATE', 'DELETE']

# Default policy for tables not explicitly listed in write_permissions
DefaultPolicyType = Literal['read_only', 'allow_all']

class WritePermissions:
    """Write permissions configuration"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize write permissions

        Args:
            config: Write permissions configuration dictionary
        """
        self.tables: Dict[str, Set[WriteOperationType]] = {}
        self.default_policy: DefaultPolicyType = 'read_only'

        if config:
            # Parse table permissions
            if 'tables' in config and isinstance(config['tables'], dict):
                for table_name, table_config in config['tables'].items():
                    operations: Set[WriteOperationType] = set()

                    if isinstance(table_config, dict) and 'operations' in table_config:
                        ops = table_config['operations']
                        if isinstance(ops, list):
                            for op in ops:
                                if op in ('INSERT', 'UPDATE', 'DELETE'):
                                    operations.add(op)  # type: ignore

                    # If no operations specified, allow all
                    if not operations:
                        operations = {'INSERT', 'UPDATE', 'DELETE'}  # type: ignore

                    self.tables[table_name] = operations

            # Parse default policy
            if 'default_policy' in config:
                policy = config['default_policy']
                if policy in ('read_only', 'allow_all'):
                    self.default_policy = policy  # type: ignore

    def can_write_to_table(self, table_name: str) -> bool:
        """Check if writing to the table is allowed

        Args:
            table_name: Name of the table

        Returns:
            True if writing to the table is allowed, False otherwise
        """
        # If table is explicitly listed, it's writable
        if table_name in self.tables:
            return True

        # Otherwise, check default policy
        return self.default_policy == 'allow_all'

    def allowed_operations(self, table_name: str) -> Set[WriteOperationType]:
        """Get allowed operations for a table

        Args:
            table_name: Name of the table

        Returns:
            Set of allowed operations
        """
        # If table is explicitly listed, return its allowed operations
        if table_name in self.tables:
            return self.tables[table_name]

        # Otherwise, check default policy
        if self.default_policy == 'allow_all':
            return {'INSERT', 'UPDATE', 'DELETE'}  # type: ignore

        # Default to empty set (no operations allowed)
        return set()  # type: ignore

    def is_operation_allowed(self, table_name: str, operation: WriteOperationType) -> bool:
        """Check if an operation is allowed on a table

        Args:
            table_name: Name of the table
            operation: Operation type

        Returns:
            True if the operation is allowed, False otherwise
        """
        return operation in self.allowed_operations(table_name)

class ConnectionConfig(ABC):
    """Base class for connection configuration"""

    debug: bool = False
    type: ConnectionType  # Connection type
    writable: bool = False  # Whether write operations are allowed
    write_permissions: Optional[WritePermissions] = None  # Write permissions configuration

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

            # Validate write permissions if writable is true
            if db_config.get('writable', False):
                if not isinstance(db_config.get('writable'), bool):
                    raise ValueError(f"Invalid writable value in database configuration {conn_name}: {db_config['writable']}")

                # Validate write_permissions if present
                if 'write_permissions' in db_config and not isinstance(db_config['write_permissions'], dict):
                    raise ValueError(f"Invalid write_permissions in database configuration {conn_name}: {db_config['write_permissions']}")

        return connections

    @classmethod
    def get_debug_mode(cls) -> bool:
        """Get debug mode status"""
        return os.environ.get('MCP_DEBUG', '').lower() in ('1', 'true')
