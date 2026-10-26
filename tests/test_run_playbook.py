"""Unit tests for run_playbook.py module.

These tests verify the behavior of the Ansible playbook runner and
fallback mechanisms used when podman or ansible are not available.
"""

import os
import sys
from unittest.mock import patch, MagicMock

# Ensure src/python is on the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "python"))

import run_playbook


class TestRunSimpleServer:
    """Tests for run_simple_server in run_playbook.py."""

    @patch("run_playbook.socketserver.TCPServer")
    @patch("builtins.print")
    def test_server_starts_on_port_3002(self, mock_print, mock_tcp_server):
        """Test that the server starts on port 3002."""
        mock_server_ctx = mock_tcp_server.return_value.__enter__.return_value
        mock_server_ctx.serve_forever.side_effect = KeyboardInterrupt

        result = run_playbook.run_simple_server()

        mock_tcp_server.assert_called_once_with(("", 3002), mock_tcp_server.call_args_list[0][0][1])
        mock_tcp_server.return_value.__enter__.assert_called_once()

        assert result is True

    @patch("run_playbook.socketserver.TCPServer")
    @patch("builtins.print")
    def test_server_handles_keyboard_interrupt(self, mock_print, mock_tcp_server):
        """Test that keyboard interrupt is handled gracefully."""
        mock_server_instance = mock_tcp_server.return_value.__enter__.return_value
        mock_server_instance.serve_forever.side_effect = KeyboardInterrupt

        result = run_playbook.run_simple_server()

        mock_server_instance.serve_forever.assert_called_once()
        assert result is True

    @patch("run_playbook.socketserver.TCPServer")
    @patch("builtins.print")
    def test_server_creates_httpd(self, mock_print, mock_tcp_server):
        """Test that TCPServer.__enter__ returns a valid HTTPd object."""
        mock_server_instance = mock_tcp_server.return_value.__enter__.return_value

        result = run_playbook.run_simple_server()

        mock_tcp_server.return_value.__enter__.assert_called_once()
        assert mock_tcp_server.return_value.__enter__.called


class TestRunAnsiblePlaybook:
    """Tests for run_ansible_playbook in run_playbook.py."""

    @patch("run_playbook.subprocess.run")
    @patch("run_playbook.os.path.exists")
    def test_returns_false_when_playbook_not_found(self, mock_exists, mock_run):
        """Test that run_ansible_playbook returns False when playbook file doesn't exist."""
        mock_exists.return_value = False

        result = run_playbook.run_ansible_playbook()

        assert result is False
        mock_run.assert_not_called()

    @patch("run_playbook.subprocess.run")
    @patch("run_playbook.os.path.exists")
    def test_returns_false_when_ansible_not_available(self, mock_exists, mock_run):
        """Test that run_ansible_playbook returns False when ansible-playbook is not found."""
        mock_exists.return_value = True
        mock_run.side_effect = FileNotFoundError("ansible-playbook not found")

        result = run_playbook.run_ansible_playbook()

        assert result is False

    @patch("run_playbook.subprocess.run")
    @patch("run_playbook.os.path.exists")
    def test_returns_true_when_playbook_succeeds(self, mock_exists, mock_run):
        """Test that run_ansible_playbook returns True when playbook succeeds."""
        mock_exists.return_value = True

        version_result = MagicMock(returncode=0)
        play_result = MagicMock(returncode=0)
        mock_run.side_effect = [version_result, play_result]

        result = run_playbook.run_ansible_playbook()

        assert result is True
        assert mock_run.call_count == 2

    @patch("run_playbook.subprocess.run")
    @patch("run_playbook.os.path.exists")
    def test_returns_false_when_playbook_fails(self, mock_exists, mock_run):
        """Test that run_ansible_playbook returns False when playbook fails."""
        mock_exists.return_value = True

        version_result = MagicMock(returncode=0)
        play_result = MagicMock(returncode=1)
        mock_run.side_effect = [version_result, play_result]

        result = run_playbook.run_ansible_playbook()

        assert result is False


class TestRunPythonContainerCreation:
    """Tests for run_python_container_creation in run_playbook.py."""

    @patch("run_playbook.os.path.exists")
    def test_returns_false_when_script_not_found(self, mock_exists):
        """Test that run_python_container_creation returns False when script doesn't exist."""
        mock_exists.return_value = False

        result = run_playbook.run_python_container_creation()

        assert result is False

    @patch("run_playbook.subprocess.run")
    @patch("run_playbook.os.path.exists")
    def test_returns_true_when_container_created(self, mock_exists, mock_run):
        """Test that run_python_container_creation returns True on success."""
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0)
        mock_cgc = MagicMock()
        mock_cgc.create_gogs_container.return_value = True

        # Add the mock module to sys.modules so the import works
        import sys
        old_module = sys.modules.get("create_gogs_container")
        sys.modules["create_gogs_container"] = mock_cgc

        try:
            result = run_playbook.run_python_container_creation()
        finally:
            if old_module is not None:
                sys.modules["create_gogs_container"] = old_module
            else:
                del sys.modules["create_gogs_container"]

        assert result is True
        mock_cgc.create_gogs_container.assert_called_once()

    @patch("run_playbook.subprocess.run")
    @patch("run_playbook.os.path.exists")
    def test_returns_false_on_exception(self, mock_exists, mock_run):
        """Test that run_python_container_creation returns False when create_gogs_container.py is missing."""
        mock_exists.return_value = False  # script doesn't exist

        result = run_playbook.run_python_container_creation()

        assert result is False
        # subprocess.run should not have been called since script is missing
        mock_run.assert_not_called()


        result = run_playbook.run_python_container_creation()

        assert result is False


class TestMain:
    """Tests for main() function in run_playbook.py."""

    @patch("run_playbook.run_simple_server")
    @patch("run_playbook.run_python_container_creation")
    @patch("run_playbook.run_ansible_playbook")
    def test_main_tries_ansible_first(self, mock_ansible, mock_python, mock_server):
        """Test that main() tries ansible first."""
        mock_ansible.return_value = True

        result = run_playbook.main()

        mock_ansible.assert_called_once()
        mock_python.assert_not_called()
        mock_server.assert_not_called()
        assert result is True

    @patch("run_playbook.run_simple_server")
    @patch("run_playbook.run_python_container_creation")
    @patch("run_playbook.run_ansible_playbook")
    def test_main_falls_back_to_python_when_ansible_fails(self, mock_ansible, mock_python, mock_server):
        """Test that main() falls back to Python script when ansible fails."""
        mock_ansible.return_value = False
        mock_python.return_value = True

        result = run_playbook.main()

        mock_ansible.assert_called_once()
        mock_python.assert_called_once()
        mock_server.assert_not_called()
        assert result is True

    @patch("run_playbook.run_simple_server")
    @patch("run_playbook.run_python_container_creation")
    @patch("run_playbook.run_ansible_playbook")
    def test_main_falls_back_to_server_when_all_fail(self, mock_ansible, mock_python, mock_server):
        """Test that main() falls back to simple server when all methods fail."""
        mock_ansible.return_value = False
        mock_python.return_value = False
        mock_server.return_value = True

        result = run_playbook.main()

        mock_ansible.assert_called_once()
        mock_python.assert_called_once()
        mock_server.assert_called_once()
        assert result is True


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
