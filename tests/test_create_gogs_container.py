"""Unit tests for create_gogs_container.py module.

These tests verify the container creation script, including the fix
to INSTALL_LOCK (set to false to show the first-run installer) and
the SSH port configuration (2222:22 mapping and SSH_PORT=2222).
"""

import os
import sys
from unittest.mock import patch, MagicMock
import unittest


# Ensure src/python is on the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "python"))

import create_gogs_container
import shutil


class TestGetPodmanCommand:
    """Tests for get_podman_command function."""

    @patch("create_gogs_container.subprocess.run")
    def test_returns_podman(self, mock_run):
        """Test that get_podman_command returns podman."""
        mock_run.return_value = MagicMock(returncode=0)
        command = create_gogs_container.get_podman_command()
        assert command == "podman"

    @patch("create_gogs_container.subprocess.run")
    def test_returns_string_not_none(self, mock_run):
        """Test that get_podman_command returns a non-None string."""
        mock_run.return_value = MagicMock(returncode=0)
        command = create_gogs_container.get_podman_command()
        assert isinstance(command, str)
        assert command is not None


class TestCreateGogsContainer(unittest.TestCase):
    """Tests for create_gogs_container function."""

    @patch("create_gogs_container.get_podman_command")
    @patch("create_gogs_container.os")
    @patch("create_gogs_container.run_simple_server")
    @patch("create_gogs_container.subprocess.run")
    def test_full_container_creation_flow(
        self, mock_subprocess_run, mock_run_simple_server, mock_os, mock_podman_cmd
    ):
        """Test the full container creation flow with podman available."""
        # Configure mocks
        mock_podman_cmd.return_value = "podman"
        mock_os.path.exists.return_value = False  # app.ini doesn't exist
        mock_os.makedirs.return_value = None
        mock_subprocess_run.return_value = MagicMock(returncode=0)

        result = create_gogs_container.create_gogs_container()

        # The function performs file operations and subprocess calls
        # Verify that subprocess.run was called
        self.assertTrue(mock_subprocess_run.called)  # podman run command
        self.assertTrue(mock_os.path.exists.called)  # app.ini path check
        self.assertTrue(mock_os.makedirs.called)     # create config dir
        self.assertFalse(mock_run_simple_server.called)  # No fallback needed
        assert result is True

    @patch("create_gogs_container.get_podman_command")
    @patch("create_gogs_container.subprocess.run")
    @patch("create_gogs_container.os")
    @patch("create_gogs_container.run_simple_server")
    def test_container_creation_fallback_on_error(
        self, mock_run_simple_server, mock_os, mock_subprocess, mock_podman_cmd
    ):
        """Test that the script falls back to simple server on podman not found."""
        mock_os.path.exists.return_value = False
        mock_podman_cmd.side_effect = FileNotFoundError("podman not found")

        result = create_gogs_container.create_gogs_container()

        # When podman is not found, the function falls back to simple server
        self.assertTrue(mock_run_simple_server.called)

    @patch("create_gogs_container.get_podman_command")
    @patch("create_gogs_container.subprocess.run")
    @patch("create_gogs_container.os")
    @patch("create_gogs_container.run_simple_server")
    def test_create_gogs_container_with_podman_not_found(
        self, mock_run_simple_server, mock_os, mock_subprocess, mock_podman_cmd
    ):
        """Test that the script falls back to simple server when podman is not found."""
        mock_os.path.exists.return_value = False
        mock_podman_cmd.side_effect = FileNotFoundError("podman not found")

        result = create_gogs_container.create_gogs_container()

        # When podman is not found, os.makedirs and config creation still happen
        # Then subprocess.run with podman cmd will fail, falling back to simple server
        self.assertTrue(mock_run_simple_server.called)


class TestModuleStructure:
    """Tests for module structure and key configuration values."""

    def test_has_create_gogs_container_function(self):
        """Test that the module exports create_gogs_container function."""
        assert hasattr(create_gogs_container, "create_gogs_container")
        assert callable(create_gogs_container.create_gogs_container)

    def test_has_get_podman_command_function(self):
        """Test that the module exports get_podman_command function."""
        assert hasattr(create_gogs_container, "get_podman_command")
        assert callable(create_gogs_container.get_podman_command)

    def test_has_run_simple_server_function(self):
        """Test that the module exports run_simple_server function."""
        assert hasattr(create_gogs_container, "run_simple_server")
        assert callable(create_gogs_container.run_simple_server)

    def test_install_lock_is_false(self):
        """Test that INSTALL_LOCK is set to false to enable first-run installer."""
        import inspect
        src = inspect.getsource(create_gogs_container.create_gogs_container)
        assert 'INSTALL_LOCK = false' in src

    def test_ssh_port_config(self):
        """Test SSH port is configured as 2222 for both host and container."""
        import inspect
        src = inspect.getsource(create_gogs_container.create_gogs_container)
        assert 'SSH_PORT = 2222' in src
        assert 'SSH_LISTEN_PORT = 2222' in src
        assert '2222:22' in src
