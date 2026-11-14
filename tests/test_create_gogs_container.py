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

    def test_returns_podman(self):
        """Test that get_podman_command returns a valid podman path."""
        command = create_gogs_container.get_podman_command()
        assert command == "podman" or command.endswith("/podman")

    def test_returns_string_not_none(self):
        """Test that get_podman_command returns a non-None string."""
        command = create_gogs_container.get_podman_command()
        assert isinstance(command, str)
        assert command is not None


class TestGetPodmanCommandNone:
    """Tests for get_podman_command returning None."""

    @patch("create_gogs_container.shutil.which", return_value=None)
    @patch("create_gogs_container.os.path.isfile", return_value=False)
    @patch("create_gogs_container.os.access", return_value=False)
    def test_returns_none_when_podman_not_found(self, mock_access, mock_isfile, mock_which):
        """Test that get_podman_command returns None when podman is not installed."""
        command = create_gogs_container.get_podman_command()
        assert command is None

    @patch("create_gogs_container.shutil.which", return_value="/usr/bin/podman")
    def test_returns_podman_path_when_found_in_path(self, mock_which):
        """Test that get_podman_command returns the path when podman is in PATH."""
        command = create_gogs_container.get_podman_command()
        assert command == "/usr/bin/podman"


class TestGetEnvVar:
    """Tests for get_env_var function."""

    def test_get_env_var_returns_default_when_missing(self):
        """Test get_env_var returns default when env var is not set."""
        result = create_gogs_container.get_env_var("NONEXISTENT_VAR_12345", default="my-default")
        assert result == "my-default"

    def test_get_env_var_returns_none_when_missing_no_default(self):
        """Test get_env_var returns None when env var is not set and no default."""
        result = create_gogs_container.get_env_var("NONEXISTENT_VAR_12345")
        assert result is None

    def test_get_env_var_returns_env_value(self):
        """Test get_env_var returns the actual env var value when set."""
        os.environ["TEST_ENV_VAR_XYZ"] = "test-value"
        try:
            result = create_gogs_container.get_env_var("TEST_ENV_VAR_XYZ")
            assert result == "test-value"
        finally:
            del os.environ["TEST_ENV_VAR_XYZ"]


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
        mock_podman_cmd.return_value = "podman"
        mock_os.path.exists.return_value = False
        mock_os.makedirs.return_value = None
        mock_subprocess_run.return_value = MagicMock(returncode=0)

        result = create_gogs_container.create_gogs_container()

        self.assertTrue(mock_subprocess_run.called)
        self.assertTrue(mock_os.path.exists.called)
        self.assertTrue(mock_os.makedirs.called)
        self.assertFalse(mock_run_simple_server.called)
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
        self.assertTrue(mock_run_simple_server.called)


    @patch("create_gogs_container.get_podman_command")
    @patch("create_gogs_container.subprocess.run")
    @patch("create_gogs_container.os")
    @patch("create_gogs_container.run_simple_server")
    def test_run_simple_server_called_on_exception(
        self, mock_run_simple_server, mock_os, mock_subprocess_run, mock_podman_cmd
    ):
        """Test run_simple_server is called when create_gogs_container raises exception."""
        mock_podman_cmd.return_value = "podman"
        mock_os.path.exists.return_value = False
        mock_os.makedirs.return_value = None
        mock_subprocess_run.side_effect = Exception("unexpected error")

        result = create_gogs_container.create_gogs_container()

        self.assertTrue(mock_run_simple_server.called)
        assert result is True

    @patch("create_gogs_container.get_podman_command")
    @patch("create_gogs_container.subprocess.run")
    @patch("create_gogs_container.os")
    @patch("create_gogs_container.run_simple_server")
    def test_volume_create_called_process_error(
        self, mock_run_simple_server, mock_os, mock_subprocess_run, mock_podman_cmd
    ):
        """Test volume create fallback when volume inspect raises CalledProcessError."""
        from subprocess import CalledProcessError
        mock_podman_cmd.return_value = "podman"
        mock_os.path.exists.return_value = False
        mock_os.makedirs.return_value = None

        mock_subprocess_run.side_effect = [
            CalledProcessError(1, "podman volume inspect"),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
        ]

        result = create_gogs_container.create_gogs_container()
        assert result is True

    @patch("create_gogs_container.get_podman_command")
    @patch("create_gogs_container.subprocess.run")
    @patch("create_gogs_container.os")
    @patch("create_gogs_container.run_simple_server")
    def test_volume_create_generic_exception(
        self, mock_run_simple_server, mock_os, mock_subprocess_run, mock_podman_cmd
    ):
        """Test volume create fallback when volume inspect raises generic exception."""
        mock_podman_cmd.return_value = "podman"
        mock_os.path.exists.return_value = False
        mock_os.makedirs.return_value = None

        mock_subprocess_run.side_effect = [
            Exception("volume inspect failed"),
            MagicMock(returncode=0),
            MagicMock(returncode=0),
        ]

        result = create_gogs_container.create_gogs_container()
        assert result is True


class TestRunSimpleServerCreateGogs:
    """Tests for run_simple_server in create_gogs_container module."""

    @patch("builtins.print")
    def test_run_simple_server_prints_and_returns_false(self, mock_print):
        """Test run_simple_server prints warning and returns False."""
        result = create_gogs_container.run_simple_server()
        assert result is False
        mock_print.assert_any_call("WARNING: Podman is not available. Cannot create Gogs container.")

    @patch("builtins.print")
    def test_run_simple_server_exception_handled(self, mock_print):
        """Test run_simple_server handles exceptions gracefully."""
        call_count = [0]
        def printing_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("print failed")
        mock_print.side_effect = printing_side_effect

        result = create_gogs_container.run_simple_server()
        assert result is False


class TestCreateGogsContainerEdgeCases(unittest.TestCase):
    """Additional edge case tests for create_gogs_container."""

    @patch("create_gogs_container.get_podman_command")
    @patch("create_gogs_container.subprocess.run")
    @patch("create_gogs_container.os")
    @patch("create_gogs_container.run_simple_server")
    def test_permission_error_writing_config(
        self, mock_run_simple_server, mock_os, mock_subprocess_run, mock_podman_cmd
    ):
        """Test PermissionError handling when writing app.ini."""
        mock_podman_cmd.return_value = "podman"
        mock_os.path.exists.return_value = True
        mock_os.makedirs.return_value = None
        mock_os.remove.return_value = None
        mock_subprocess_run.return_value = MagicMock(returncode=0)

        real_open = __builtins__.open if not isinstance(__builtins__, dict) else __builtins__["open"]
        call_count = [0]
        def fake_open(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise PermissionError("denied")
            return real_open(*args, **kwargs)

        with patch("builtins.open", side_effect=fake_open):
            result = create_gogs_container.create_gogs_container()
        assert result is True

    @patch("create_gogs_container.get_podman_command")
    @patch("create_gogs_container.subprocess.run")
    @patch("create_gogs_container.os")
    @patch("create_gogs_container.run_simple_server")
    def test_chmod_exception_handled(
        self, mock_run_simple_server, mock_os, mock_subprocess_run, mock_podman_cmd
    ):
        """Test that chmod exception is handled gracefully."""
        mock_podman_cmd.return_value = "podman"
        mock_os.path.exists.return_value = False
        mock_os.makedirs.return_value = None
        mock_os.chmod.side_effect = Exception("chmod failed")
        mock_subprocess_run.return_value = MagicMock(returncode=0)

        result = create_gogs_container.create_gogs_container()
        assert result is True


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

    def test_has_get_env_var_function(self):
        """Test that the module exports get_env_var function."""
        assert hasattr(create_gogs_container, "get_env_var")
        assert callable(create_gogs_container.get_env_var)

    def test_install_lock_is_false(self):
        """Test that INSTALL_LOCK is set to false to enable first-run installer."""
        import inspect
        src = inspect.getsource(create_gogs_container.create_gogs_container)
        assert 'INSTALL_LOCK = false' in src

    def test_ssh_port_config(self):
        """Test SSH port environment variables are configured with f-strings."""
        import inspect
        src = inspect.getsource(create_gogs_container.create_gogs_container)
        assert 'f"SSH_PORT={config[\'gogs_ssh_port\']}"' in src
        assert 'f"SSH_LISTEN_PORT={config[\'gogs_ssh_listen_port\']}"' in src
        assert '--network' in src and 'host' in src
