#!/usr/bin/env python3
"""
Run the Gogs Ansible playbook or fall back to direct container creation.

This module attempts to run the Gogs setup via Ansible Playbook.
If Ansible is not installed, it falls back to the Python-based
container creation script (create_gogs_container.py). If Podman is
also unavailable, it starts a simple HTTP server for development.
"""

import http.server
import socketserver
import os
import subprocess
import sys

# Resolve project root (two levels up from this file: src/python/ -> project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_ansible_playbook():
    """Run the Gogs Podman setup Ansible playbook.

    Returns True if the playbook ran successfully, False otherwise.
    """
    playbook_path = os.path.join(
        PROJECT_ROOT, "src", "playbooks", "gogs-podman-setup.yml"
    )

    if not os.path.exists(playbook_path):
        print(f"Playbook not found at {playbook_path}")
        return False

    # Check if ansible-playbook command is available
    try:
        subprocess.run(
            ["ansible-playbook", "--version"],
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Ansible not found. Falling back to Python container creation...")
        return False

    # Run the playbook
    print(f"Running Ansible playbook: {playbook_path}")
    try:
        result = subprocess.run(
            ["ansible-playbook", "-i", "localhost,", "-c", "local", playbook_path],
            cwd=PROJECT_ROOT,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running playbook: {e}")
        return False


def run_python_container_creation():
    """Run the Python-based container creation script.

    Returns True if the container was created successfully, False otherwise.
    """
    script_path = os.path.join(PROJECT_ROOT, "src", "python", "create_gogs_container.py")
    if not os.path.exists(script_path):
        print(f"create_gogs_container.py not found at {script_path}")
        return False

    # Add the src/python directory to sys.path so imports work
    python_dir = os.path.join(PROJECT_ROOT, "src", "python")
    if python_dir not in sys.path:
        sys.path.insert(0, python_dir)

    try:
        import create_gogs_container
        result = create_gogs_container.create_gogs_container()
        return result
    except Exception as e:
        print(f"Error in Python container creation: {e}")
        return False


def run_simple_server():
    """Start a simple HTTP server for development when podman is not available."""
    try:
        PORT = 3002
        Handler = http.server.SimpleHTTPRequestHandler

        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"\nSimple HTTP Server running on port {PORT}")
            print("Press Ctrl+C to stop the server")
            print("Access Gogs at: http://localhost:3000")
            print("\nNote: This is a simple server for testing purposes only.")
            print("For a production setup, you'll need to install podman or docker.")

            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped.")
                return True

    except Exception as e:
        print(f"Error starting server: {e}")
        return False


def main():
    """Main entry point: try Ansible, then Python script, then simple server."""
    # Try running the Ansible playbook first
    if run_ansible_playbook():
        print("\nGogs setup complete via Ansible playbook!")
        print("Access Gogs at: http://localhost:3000")
        return True

    # Fall back to Python-based container creation
    print("\nTrying Python-based container creation...")
    if run_python_container_creation():
        print("\nGogs setup complete via Python script!")
        print("Access Gogs at: http://localhost:3000")
        return True

    # Last resort: simple HTTP server for development
    print("\nAll container methods failed. Starting simple HTTP server for development...")
    return run_simple_server()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
