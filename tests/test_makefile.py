"""Unit tests for Makefile targets using dry-run simulation.

These tests verify that every Makefile target is syntactically valid
and that its command references resolve correctly against the project
root directory.
"""

import os
import subprocess
import sys

# Paths relative to this test file (tests/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
PYTHON_SCRIPTS = os.path.join(SRC_DIR, "python")
PLAYBOOKS_DIR = os.path.join(SRC_DIR, "playbooks")
SCRIPTS_DIR = os.path.join(SRC_DIR, "scripts")

# List all Makefile targets to test (as they appear in .PHONY)
MAKEFILE_TARGETS = [
    "help",
    "install-deps",
    "build",
    "quick-build",
    "clean",
    "start",
    "stop",
    "restart",
    "status",
    "logs",
    "volumes",
    "lint",
    "desktop",
    "run-python-scripts",
    "run-shell-scripts",
    "export",
    "import",
]


def run_make_dry(target: str, cwd: str = PROJECT_ROOT) -> subprocess.CompletedProcess:
    """Run `make -n <target>` (dry run, no execution) and return result."""
    result = subprocess.run(
        ["make", "-n", target],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result


def test_help_target():
    """make help should print the usage banner without error."""
    result = run_make_dry("help")
    assert result.returncode == 0, f"make help failed: {result.stderr}"
    assert "Gogs Podman Setup" in result.stdout


def test_install_deps_target():
    """make install-deps should be valid (dry run succeeds)."""
    result = run_make_dry("install-deps")
    assert result.returncode == 0, f"make install-deps failed: {result.stderr}"


def test_build_target():
    """make build should be valid (dry run succeeds)."""
    result = run_make_dry("build")
    assert result.returncode == 0, f"make build failed: {result.stderr}"
    # Should reference the correct Python script path
    assert "src/python/run_playbook.py" in result.stdout


def test_quick_build_target():
    """make quick-build should be valid (dry run succeeds)."""
    result = run_make_dry("quick-build")
    assert result.returncode == 0, f"make quick-build failed: {result.stderr}"
    assert "src/python/create_gogs_container.py" in result.stdout


def test_clean_target():
    """make clean should be valid (dry run succeeds)."""
    result = run_make_dry("clean")
    assert result.returncode == 0, f"make clean failed: {result.stderr}"


def test_start_target():
    """make start should be valid (dry run succeeds)."""
    result = run_make_dry("start")
    assert result.returncode == 0, f"make start failed: {result.stderr}"


def test_stop_target():
    """make stop should be valid (dry run succeeds)."""
    result = run_make_dry("stop")
    assert result.returncode == 0, f"make stop failed: {result.stderr}"


def test_restart_target():
    """make restart should be valid (dry run succeeds)."""
    result = run_make_dry("restart")
    assert result.returncode == 0, f"make restart failed: {result.stderr}"


def test_status_target():
    """make status should be valid (dry run succeeds)."""
    result = run_make_dry("status")
    assert result.returncode == 0, f"make status failed: {result.stderr}"
    assert "podman ps" in result.stdout


def test_logs_target():
    """make logs should be valid (dry run succeeds)."""
    result = run_make_dry("logs")
    assert result.returncode == 0, f"make logs failed: {result.stderr}"


def test_volumes_target():
    """make volumes should be valid (dry run succeeds)."""
    result = run_make_dry("volumes")
    assert result.returncode == 0, f"make volumes failed: {result.stderr}"


def test_lint_target():
    """make lint should be valid (dry run succeeds)."""
    result = run_make_dry("lint")
    assert result.returncode == 0, f"make lint failed: {result.stderr}"


def test_desktop_target():
    """make desktop should be valid (dry run succeeds)."""
    result = run_make_dry("desktop")
    assert result.returncode == 0, f"make desktop failed: {result.stderr}"


def test_run_python_scripts_target():
    """make run-python-scripts should be valid (dry run succeeds)."""
    result = run_make_dry("run-python-scripts")
    assert result.returncode == 0, f"make run-python-scripts failed: {result.stderr}"
    assert "src/python/run_playbook.py" in result.stdout


def test_run_shell_scripts_target():
    """make run-shell-scripts should be valid (dry run succeeds)."""
    result = run_make_dry("run-shell-scripts")
    assert result.returncode == 0, f"make run-shell-scripts failed: {result.stderr}"
    assert "src/scripts/setup_gogs.sh" in result.stdout


def test_export_target():
    """make export should be valid (dry run succeeds)."""
    result = run_make_dry("export")
    assert result.returncode == 0, f"make export failed: {result.stderr}"
    assert "Exporting Gogs configuration and data" in result.stdout
    assert "exporting Gogs" in result.stdout.lower() or "tar" in result.stdout.lower()


def test_import_target():
    """make import should be valid (dry run succeeds)."""
    result = run_make_dry("import")
    assert result.returncode == 0, f"make import failed: {result.stderr}"
    assert "Importing Gogs from backup" in result.stdout
    assert "BACKUP_FILE" in result.stdout


def test_all_targets_exist():
    """Every target listed in .PHONY must be a valid make target.

    Uses dry-run (make -n) for all targets as a lighter-weight
    alternative to parsing the make database.
    """
    for target in MAKEFILE_TARGETS:
        result = run_make_dry(target)
        assert result.returncode == 0, (
            f"Target '{target}' not valid (make -n failed: {result.stderr})"
        )


if __name__ == "__main__":
    # Quick sanity run when executed directly
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
