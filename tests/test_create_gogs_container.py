"""Unit tests for create_gogs_container.py module.

These tests use mocking to verify that the Gogs container creation
script constructs the correct podman commands without actually
invoking podman.
"""

import os
import sys
from unittest.mock import patch, call, ANY

# Ensure src/python is on the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "python"))

from create_gogs_container import create_gogs_container, get_podman_command


class TestGetPodmanCommand:
    """Tests for get_podman_command()."""

    def test_returns_podman(self):
        """Should return 'podman' string."""
        assert get_podman_command() == "podman"

    def test_returns_string_not_none(self):
        """Should return a non-None string."""
        result = get_podman_command()
        assert isinstance(result, str)
        assert result == "podman"


class TestCreateGogsContainer:
    """Tests for create_gogs_container()."""

    @patch("create_gogs_container.subprocess.run")
    @patch("create_gogs_container.get_podman_command")
    @patch("create_gogs_container.os.makedirs")
    @patch("create_gogs_container.open", create=True)
    @patch("builtins.print")
    def test_full_container_creation_flow(
        self, mock_print, mock_open, mock_makedirs, mock_podman_cmd, mock_subprocess
    ):
        """Test the full container creation flow with mocked subprocess."""
        # Setup mocks
        mock_podman_cmd.return_value = "podman"
        mock_open.return_value.__enter__.return_value.write = lambda x: None

        result = create_gogs_container()

        # Verify os.makedirs was called for /tmp/gogs-config
        mock_makedirs.assert_called_once_with("/tmp/gogs-config", exist_ok=True)

        # Verify podman volume create was called with gogs_data
        mock_subprocess.assert_any_call(
            ["podman", "volume", "create", "gogs_data"],
            check=True,
        )

        # Verify podman run was called with expected arguments
        run_calls = [c.args[0] for c in mock_subprocess.call_args_list if isinstance(c.args[0], list) and "run" in c.args[0]]
        assert len(run_calls) == 1
        run_cmd = run_calls[0]
        assert run_cmd[0] == "podman"
        assert run_cmd[1] == "run"
        assert run_cmd[2] == "-d"

        # Verify podman exec was called for SSH keys
        exec_calls = [c.args[0] for c in mock_subprocess.call_args_list if "exec" in c.args[0]]
        assert len(exec_calls) == 1
        exec_cmd = exec_calls[0]
        # exec_cmd should be ['podman', 'exec', 'gogs', '/bin/sh', '-c', '...ssh_host_rsa_key...']
        assert "ssh_host_rsa_key" in exec_cmd[5]

        assert result is True

    @patch("create_gogs_container.subprocess.run")
    @patch("create_gogs_container.get_podman_command")
    @patch("create_gogs_container.os.makedirs")
    @patch("create_gogs_container.open", create=True)
    @patch("builtins.print")
    @patch("create_gogs_container.run_simple_server")
    def test_container_creation_fallback_on_error(
        self, mock_run_simple_server, mock_print, mock_open, mock_makedirs, mock_podman_cmd, mock_subprocess
    ):
        """Test that fallback to simple server happens on exception."""
        mock_podman_cmd.return_value = "podman"
        mock_subprocess.side_effect = Exception("podman not available")
        mock_run_simple_server.return_value = True

        result = create_gogs_container()

        # Should call run_simple_server as fallback
        mock_run_simple_server.assert_called_once()
        assert result is True

    @patch("create_gogs_container.subprocess.run")
    @patch("create_gogs_container.get_podman_command")
    @patch("create_gogs_container.os.makedirs")
    @patch("create_gogs_container.open", create=True)
    @patch("builtins.print")
    @patch("create_gogs_container.run_simple_server")
    def test_create_gogs_container_with_podman_not_found(
        self, mock_run_simple_server, mock_print, mock_open, mock_makedirs, mock_podman_cmd, mock_subprocess
    ):
        """Test behavior when podman command is not found."""
        mock_podman_cmd.return_value = None
        mock_run_simple_server.return_value = True

        result = create_gogs_container()

        # Should call run_simple_server as fallback
        mock_run_simple_server.assert_called_once()
        assert result is True


class TestModuleStructure:
    """Test that the module has the expected public interface."""

    def test_has_create_gogs_container_function(self):
        """create_gogs_container should be importable."""
        from create_gogs_container import create_gogs_container
        assert callable(create_gogs_container)

    def test_has_get_podman_command_function(self):
        """get_podman_command should be importable."""
        from create_gogs_container import get_podman_command
        assert callable(get_podman_command)

    def test_has_run_simple_server_function(self):
        """run_simple_server should be importable."""
        from create_gogs_container import run_simple_server
        assert callable(run_simple_server)


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
