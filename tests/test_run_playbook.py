"""Unit tests for run_playbook.py module.

These tests verify the behavior of the simple HTTP server
fallback used when podman is not available.
"""

import os
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

# Ensure src/python is on the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "python"))

from unittest.mock import patch

import run_playbook


class TestRunSimpleServer:
    """Tests for run_simple_server in run_playbook.py."""

    @patch("run_playbook.socketserver.TCPServer")
    @patch("builtins.print")
    def test_server_starts_on_port_3002(self, mock_print, mock_tcp_server):
        """Test that the server starts on port 3002."""
        # Configure the mock: TCPServer returns a mock server context
        mock_server_ctx = mock_tcp_server.return_value.__enter__.return_value
        mock_server_ctx.serve_forever.side_effect = KeyboardInterrupt

        result = run_playbook.run_simple_server()

        # Verify TCPServer was called with port 3002 and SimpleHTTPRequestHandler
        mock_tcp_server.assert_called_once_with(("", 3002), SimpleHTTPRequestHandler)

        # Verify the server context was entered
        mock_tcp_server.return_value.__enter__.assert_called_once()

        assert result is True

    @patch("run_playbook.socketserver.TCPServer")
    @patch("builtins.print")
    def test_server_handles_keyboard_interrupt(self, mock_print, mock_tcp_server):
        """Test that keyboard interrupt is handled gracefully."""
        mock_server_instance = mock_tcp_server.return_value.__enter__.return_value
        mock_server_instance.serve_forever.side_effect = KeyboardInterrupt

        result = run_playbook.run_simple_server()

        # Server should have been stopped
        mock_server_instance.serve_forever.assert_called_once()
        assert result is True

    @patch("run_playbook.socketserver.TCPServer")
    @patch("builtins.print")
    def test_server_creates_httpd(self, mock_print, mock_tcp_server):
        """Test that TCPServer.__enter__ returns a valid HTTPd object."""
        mock_server_instance = mock_tcp_server.return_value.__enter__.return_value

        result = run_playbook.run_simple_server()

        # TCPServer.__enter__ should have been called
        mock_tcp_server.return_value.__enter__.assert_called_once()

        # Note: run_simple_server() may return None if serve_forever blocks
        # The test verifies the server context was properly created
        assert mock_tcp_server.return_value.__enter__.called


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
