"""Test the module initialization and command line entry point"""
import os
import sys
from unittest.mock import MagicMock, patch

import pytest
import yaml

import mcp_dbutils
from mcp_dbutils import main, run_server


@pytest.fixture
def mock_config_file(tmp_path):
    """Create a temporary config file for testing"""
    config_file = tmp_path / "config.yaml"
    config = {
        "connections": {
            "test_conn": {
                "type": "sqlite",
                "database": ":memory:"
            }
        }
    }
    with open(config_file, "w") as f:
        yaml.dump(config, f)
    return str(config_file)


class TestInit:
    """Test the module initialization"""

    @patch("mcp_dbutils.ConnectionServer")
    @patch("argparse.ArgumentParser.parse_args")
    @patch("mcp_dbutils.create_logger")
    async def test_run_server(self, mock_create_logger, mock_parse_args, mock_server, mock_config_file):
        """Test the run_server function"""
        # Setup mocks
        mock_logger = MagicMock()
        mock_create_logger.return_value = mock_logger
        mock_parse_args.return_value = MagicMock(config=mock_config_file, local_host=None)
        mock_server_instance = MagicMock()
        mock_server.return_value = mock_server_instance

        # Run the function
        with patch.object(sys, 'argv', ['mcp_dbutils', '--config', mock_config_file]):
            await run_server()

        # Assertions
        mock_server.assert_called_once()
        mock_server_instance.run.assert_called_once()
        mock_logger.assert_any_call("info", f"MCP Connection Utilities Service v{mcp_dbutils.pkg_meta['Version']}")

    @patch("mcp_dbutils.ConnectionServer")
    @patch("argparse.ArgumentParser.parse_args")
    @patch("mcp_dbutils.create_logger")
    async def test_run_server_with_debug(self, mock_create_logger, mock_parse_args, mock_server, mock_config_file):
        """Test the run_server function with debug mode"""
        # Setup mocks
        mock_logger = MagicMock()
        mock_create_logger.return_value = mock_logger
        mock_parse_args.return_value = MagicMock(config=mock_config_file, local_host=None)
        mock_server_instance = MagicMock()
        mock_server.return_value = mock_server_instance

        # Set debug environment variable
        with patch.dict(os.environ, {"MCP_DEBUG": "true"}), patch.object(sys, 'argv', ['mcp_dbutils', '--config', mock_config_file]):
            await run_server()

        # Assertions
        mock_server.assert_called_once()
        mock_server_instance.run.assert_called_once()
        mock_logger.assert_any_call("debug", "Debug模式已开启")

    @patch("mcp_dbutils.ConnectionServer")
    @patch("argparse.ArgumentParser.parse_args")
    @patch("mcp_dbutils.create_logger")
    async def test_run_server_invalid_config(self, mock_create_logger, mock_parse_args, mock_server, tmp_path):
        """Test the run_server function with invalid config"""
        # Create invalid config file
        invalid_config_file = tmp_path / "invalid_config.yaml"
        with open(invalid_config_file, "w") as f:
            f.write("invalid: yaml")

        # Setup mocks
        mock_logger = MagicMock()
        mock_create_logger.return_value = mock_logger
        mock_parse_args.return_value = MagicMock(config=str(invalid_config_file), local_host=None)

        # Run the function and expect exit
        with patch.object(sys, 'exit') as mock_exit:
            with patch.object(sys, 'argv', ['mcp_dbutils', '--config', str(invalid_config_file)]):
                await run_server()
            mock_exit.assert_called_once_with(1)

    @patch("mcp_dbutils.ConnectionServer")
    @patch("argparse.ArgumentParser.parse_args")
    @patch("mcp_dbutils.create_logger")
    async def test_run_server_empty_connections(self, mock_create_logger, mock_parse_args, mock_server, tmp_path):
        """Test the run_server function with empty connections"""
        # Create config file with empty connections
        empty_config_file = tmp_path / "empty_config.yaml"
        config = {"connections": {}}
        with open(empty_config_file, "w") as f:
            yaml.dump(config, f)

        # Setup mocks
        mock_logger = MagicMock()
        mock_create_logger.return_value = mock_logger
        mock_parse_args.return_value = MagicMock(config=str(empty_config_file), local_host=None)

        # Run the function and expect exit
        with patch.object(sys, 'exit') as mock_exit:
            with patch.object(sys, 'argv', ['mcp_dbutils', '--config', str(empty_config_file)]):
                await run_server()
            mock_exit.assert_called_once_with(1)

    @patch("mcp_dbutils.ConnectionServer")
    @patch("argparse.ArgumentParser.parse_args")
    @patch("mcp_dbutils.create_logger")
    async def test_run_server_exception(self, mock_create_logger, mock_parse_args, mock_server, mock_config_file):
        """Test the run_server function with exception"""
        # Setup mocks
        mock_logger = MagicMock()
        mock_create_logger.return_value = mock_logger
        mock_parse_args.return_value = MagicMock(config=mock_config_file, local_host=None)
        mock_server_instance = MagicMock()
        mock_server_instance.run.side_effect = Exception("Test exception")
        mock_server.return_value = mock_server_instance

        # Run the function and expect exit
        with patch.object(sys, 'exit') as mock_exit:
            with patch.object(sys, 'argv', ['mcp_dbutils', '--config', mock_config_file]):
                await run_server()
            mock_exit.assert_called_once_with(1)

    @patch("mcp_dbutils.asyncio.run")
    def test_main(self, mock_run):
        """Test the main function"""
        main()
        mock_run.assert_called_once()
