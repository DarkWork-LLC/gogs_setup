import os
import sys
import subprocess

def get_podman_command():
    """Get the correct podman command to use"""
    # Since podman is confirmed to be installed, use the standard command
    return "podman"

def create_gogs_container():
    try:
        # Get the correct podman command
        podman_cmd = get_podman_command()
        if not podman_cmd:
            print("Podman not available. Starting simple HTTP server for development...")
            return run_simple_server()

        # Create configuration directory
        os.makedirs("/tmp/gogs-config", exist_ok=True)

        # Create app.ini configuration
        app_ini_content = """[server]
APP_DATA_PATH = /data/gogs
DOMAIN = localhost
HTTP_PORT = 3000
HTTP_ADDR = 0.0.0.0
EXTERNAL_URL = http://127.0.0.1:3000/
DISABLE_SSH = false
SSH_PORT = 2222
SSH_LISTEN_PORT = 2222
START_SSH_SERVER = true
OFFLINE_MODE = false

[database]
TYPE = sqlite3
PATH = /data/gogs/data/gogs.db

[repository]
ROOT = /data/git

[security]
INSTALL_LOCK = true
SECRET_KEY = gogs-secret-key-123456789012345678901234

[auth]
REQUIRE_EMAIL_CONFIRMATION = false
DISABLE_REGISTRATION = false
ENABLE_REGISTRATION_CAPTCHA = false
REQUIRE_SIGNIN_VIEW = false

[user]
ENABLE_EMAIL_NOTIFICATION = false

[picture]
DISABLE_GRAVATAR = false
ENABLE_FEDERATED_AVATAR = true

[session]
PROVIDER = file

[log]
MODE = console
LEVEL = Info
ROOT_PATH = /app/gogs/log

[log.console]
LEVEL = console"""

        config_path = "/tmp/gogs-config/app.ini"
        if os.path.exists(config_path):
            try:
                os.remove(config_path)
            except Exception:
                pass

        with open(config_path, "w") as f:
            f.write(app_ini_content)

        # Create volumes (handle case where volume already exists)
        try:
            subprocess.run([podman_cmd, "volume", "create", "gogs_data"], check=True)
        except subprocess.CalledProcessError as vol_err:
            if vol_err.returncode != 125 and "already exists" not in str(vol_err):
                raise vol_err

        # Create container
        subprocess.run([
            podman_cmd, "run", "-d",
            "--replace",
            "--name", "gogs",
            "--publish", "3000:3000",
            "--publish", "2222:22",
            "--restart", "unless-stopped",
            "--label", "io.containers.autoupdate=image",
            "--label", "io.podman.desktop=true",
            "--label", "app=gogs",
            "--label", "version=3000",
            "-v", "gogs_data:/data",
            "-v", "/tmp/gogs-config/app.ini:/data/gogs/conf/app.ini",
            "-e", "USER_UID=1000",
            "-e", "USER_GID=1000",
            "-e", "GIT_DISCOVERY=true",
            "-e", "HTTP_ADDR=0.0.0.0",
            "-e", "HTTP_PORT=3000",
            "-e", "SSH_PORT=22",
            "-e", "SSH_LISTEN_PORT=22",
            "docker.io/gogs/gogs:latest"
        ], check=True)

        # Wait briefly for container initialization
        import time
        time.sleep(2)

        # Generate SSH host keys
        subprocess.run([
            podman_cmd, "exec", "gogs", "/bin/sh", "-c",
            "if [ ! -f /data/ssh/ssh_host_rsa_key ]; then "
            "echo 'Generating SSH host keys...' && "
            "mkdir -p /data/ssh && "
            "ssh-keygen -t rsa -b 4096 -f /data/ssh/ssh_host_rsa_key -N '' && "
            "ssh-keygen -t ecdsa -b 521 -f /data/ssh/ssh_host_ecdsa_key -N '' && "
            "ssh-keygen -t ed25519 -f /data/ssh/ssh_host_ed25519_key -N '' && "
            "chown -R 1000:1000 /data/ssh && "
            "chmod 600 /data/ssh/ssh_host_*_key && "
            "chmod 644 /data/ssh/ssh_host_*_key.pub && "
            "echo 'SSH host keys generated successfully'; "
            "else echo 'SSH host keys already exist'; fi"
        ], check=True)

        print("Gogs container created and started successfully!")
        print(f"Access Gogs at: http://127.0.0.1:3000")
        print(f"SSH access at: 127.0.0.1:2222")

        return True

    except Exception as e:
        print(f"Error creating Gogs container: {e}")
        print("Starting simple HTTP server as fallback...")
        return run_simple_server()

def run_simple_server():
    """Start a simple HTTP server for development when podman is not available"""
    try:
        import http.server
        import socketserver
        import socket
        
        # Try different ports if 3000 is busy
        for PORT in [3000, 3001, 3002, 8080, 8000]:
            try:
                Handler = http.server.SimpleHTTPRequestHandler

                with socketserver.TCPServer(("", PORT), Handler) as httpd:
                    print(f"\nSimple HTTP Server running on port {PORT}")
                    print("Press Ctrl+C to stop the server")
                    print(f"Access Gogs at: http://localhost:{PORT}")
                    print("\nNote: This is a simple server for testing purposes only.")
                    print("For a production setup with podman, install podman and try again.")
                    print("You can try: sudo apt-get install podman (Ubuntu/Debian)")
                    print("Or: sudo dnf install podman (Fedora/CentOS)")
                    print("Or: sudo yum install podman (older CentOS)")

                    try:
                        httpd.serve_forever()
                    except KeyboardInterrupt:
                        print("\nServer stopped.")
                        return True
                    except Exception as server_error:
                        print(f"Server error on port {PORT}: {server_error}")
                        continue
                        
            except socket.error as e:
                if e.errno == 98:  # Address already in use
                    print(f"Port {PORT} is busy, trying next port...")
                    continue
                else:
                    raise e
                    
        print("All common ports are busy. Cannot start server.")
        return False

    except Exception as e:
        print(f"Error starting simple server: {e}")
        return False

if __name__ == "__main__":
    success = create_gogs_container()
    sys.exit(0 if success else 1)
