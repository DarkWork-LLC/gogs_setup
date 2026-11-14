"""Unit tests for simple_gogs_server.py module.

These tests verify the behavior of the simple HTTP server
fallback script used when podman is not available.
"""

import os
import sys
import socket
import runpy
from unittest.mock import patch, MagicMock
from http.server import SimpleHTTPRequestHandler

# Ensure src/python is on the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "python"))

from simple_gogs_server import run_simple_server


class TestRunSimpleServer:
    """Tests for run_simple_server in simple_gogs_server.py."""

    @patch("simple_gogs_server.socketserver.TCPServer")
    @patch("builtins.print")
    def test_server_starts_on_port_3000(self, mock_print, mock_tcp_server):
        """Test that the server starts on port 3000."""
        # Configure mock: TCPServer returns a mock server context
        mock_server_ctx = mock_tcp_server.return_value.__enter__.return_value
        mock_server_ctx.serve_forever.side_effect = KeyboardInterrupt

        result = run_simple_server()

        # Verify TCPServer was called with port 3000 and SimpleHTTPRequestHandler
        mock_tcp_server.assert_called_once_with(("", 3000), SimpleHTTPRequestHandler)

        # Verify the server context was entered
        mock_tcp_server.return_value.__enter__.assert_called_once()

        assert result is True

    @patch("simple_gogs_server.socketserver.TCPServer")
    @patch("builtins.print")
    def test_server_handles_keyboard_interrupt(self, mock_print, mock_tcp_server):
        """Test that keyboard interrupt is handled gracefully."""
        mock_server_instance = mock_tcp_server.return_value.__enter__.return_value
        mock_server_instance.serve_forever.side_effect = KeyboardInterrupt

        result = run_simple_server()

        # Server should have been stopped
        mock_server_instance.serve_forever.assert_called_once()
        assert result is True

    @patch("simple_gogs_server.socketserver.TCPServer")
    @patch("builtins.print")
    def test_server_prints_access_url(self, mock_print, mock_tcp_server):
        """Test that the access URL is printed to console."""
        mock_server = mock_tcp_server.return_value.__enter__.return_value
        mock_server.serve_forever.side_effect = KeyboardInterrupt

        run_simple_server()

        # Check that the URL is printed
        url_printed = any(
            "http://mofo-tank:3000" in str(call_args) for call_args in mock_print.call_args_list
        )
        assert url_printed, "Access URL should be printed"

    @patch("simple_gogs_server.socketserver.TCPServer")
    @patch("builtins.print")
    def test_server_prints_port_number(self, mock_print, mock_tcp_server):
        """Test that the port number is printed."""
        mock_server = mock_tcp_server.return_value.__enter__.return_value
        mock_server.serve_forever.side_effect = KeyboardInterrupt

        run_simple_server()

        # Check that port 3000 is printed
        port_printed = any(
            "3000" in str(call_args) for call_args in mock_print.call_args_list
        )
        assert port_printed, "Port number should be printed"

    @patch("simple_gogs_server.socketserver.TCPServer")
    @patch("builtins.print")
    def test_serve_forever_exception_continues(self, mock_print, mock_tcp_server):
        """Test that serve_forever raising exception continues to next port."""
        # First port: serve_forever raises generic exception
        mock_ctx1 = MagicMock()
        mock_ctx1.__enter__.return_value.serve_forever.side_effect = Exception("server error")

        # Second port: serve_forever raises KeyboardInterrupt
        mock_ctx2 = MagicMock()
        mock_ctx2.__enter__.return_value.serve_forever.side_effect = KeyboardInterrupt

        mock_tcp_server.side_effect = [mock_ctx1, mock_ctx2]

        result = run_simple_server()

        assert result is True
        assert mock_tcp_server.call_count >= 2

    @patch("simple_gogs_server.socketserver.TCPServer")
    @patch("builtins.print")
    def test_socket_error_address_in_use(self, mock_print, mock_tcp_server):
        """Test that socket.error with errno 98 continues to next port."""
        err = OSError()
        err.errno = 98
        mock_tcp_server.side_effect = err

        result = run_simple_server()

        assert result is False  # All ports fail with errno 98

    @patch("simple_gogs_server.socketserver.TCPServer")
    @patch("builtins.print")
    def test_all_ports_busy(self, mock_print, mock_tcp_server):
        """Test that when all ports are busy, returns False."""
        err = OSError()
        err.errno = 98
        mock_tcp_server.side_effect = err

        result = run_simple_server()

        assert result is False
        mock_print.assert_any_call("All common ports are busy. Cannot start server.")

    @patch("simple_gogs_server.socketserver.TCPServer")
    @patch("builtins.print")
    def test_outer_exception_handler(self, mock_print, mock_tcp_server):
        """Test that outer exception handler catches errors."""
        mock_tcp_server.side_effect = RuntimeError("Unexpected error")

        result = run_simple_server()

        assert result is False


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
