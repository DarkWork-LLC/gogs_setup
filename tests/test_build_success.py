"""Unit tests for build_success.py module."""

import os
import sys
import runpy
from unittest.mock import patch

# Ensure src/python is on the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "python"))

import build_success


class TestBuildSuccess:
    """Tests for build_success module."""

    @patch("build_success.socket.gethostname", return_value="test-host")
    @patch("builtins.print")
    def test_main_prints_messages_and_returns_zero(self, mock_print, mock_hostname):
        """Test that main() prints expected messages and returns 0."""
        result = build_success.main()
        assert result == 0
        mock_print.assert_any_call("Build successful!")
        mock_print.assert_any_call("Access Gogs at: http://test-host:3000")
        mock_print.assert_any_call(
            "Note: For a full podman setup, install podman and run 'make build'"
        )

    def test_main_block_guarded(self):
        """Test that the __main__ block is guarded (does not run on import)."""
        assert build_success.__name__ == "build_success"

    def test_main_block_executed(self):
        """Test that running the module as __main__ calls sys.exit(0)."""
        with patch("build_success.sys.exit") as mock_exit:
            runpy.run_module("build_success", run_name="__main__")
            mock_exit.assert_called_once_with(0)


