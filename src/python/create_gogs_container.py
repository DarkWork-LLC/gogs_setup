"""
Gogs container creation script - Dynamic configuration from environment variables.
This script creates a Gogs container with configuration values passed from Ansible.
"""

import os
import sys
import subprocess
import time
import shutil

def get_podman_command():
<<<<<<< HEAD
    """Get the correct podman command to use.

    Checks common installation locations in case podman is installed
    but not in the system PATH.
    """
    podman_path = shutil.which("podman")
    if podman_path:
        return podman_path

    # Check common locations where podman may be installed but not in PATH
    common_locations = [
        "/run/host/usr/bin/podman",
        "/usr/bin/podman",
        "/usr/local/bin/podman",
        "/bin/podman",
        "/sbin/podman",
        "/usr/sbin/podman",
    ]
    for location in common_locations:
        if os.path.isfile(location) and os.access(location, os.X_OK):
            return location

=======
    """Get the correct podman command to use"""
    subprocess.run(["podman", "--version"], check=True, capture_output=True)
>>>>>>> 5f3ce7200d9df3cd958d1e7eb0cad23fa2b78858
    return "podman"

def get_env_var(name, default=None):
    """Get environment variable with optional default"""
    value = os.environ.get(name)
    return value if value is not None else default

def get_config_from_env():
    """Read Gogs configuration from environment variables"""
    # Container settings
    container_name = os.environ.get('GOGS_CONTAINER_NAME', 'gogs')
    gogs_image = os.environ.get('GOGS_IMAGE', 'docker.io/gogs/gogs:latest')
    gogs_image_fallback = os.environ.get('GOGS_IMAGE_FALLBACK', 'docker.io/gogs/gogs:1')
    
    # Network settings
    gogs_port = os.environ.get('GOGS_PORT', '6009')
    gogs_ssh_port = os.environ.get('GOGS_SSH_PORT', '2222')
    
    # Volume settings
    gogs_data_volume = os.environ.get('GOGS_DATA_VOLUME', 'gogs_data')
    
    # App configuration (from Ansible or environment)
    gogs_domain = os.environ.get('GOGS_DOMAIN', 'localhost')
    gogs_root_url = os.environ.get('GOGS_ROOT_URL', f'http://localhost:{gogs_port}/')
    gogs_app_data_path = os.environ.get('GOGS_APP_DATA_PATH', '/data/gogs')
    gogs_secret_key = os.environ.get('GOGS_SECRET_KEY', 'gogs-secret-key-7x3fL9p2mN4vR8yT5wK0qZ1xJ3cB6nG')
    gogs_install_lock = os.environ.get('GOGS_INSTALL_LOCK', 'false').lower() == 'true'
    gogs_require_email_confirmation = os.environ.get('GOGS_REQUIRE_EMAIL_CONFIRMATION', 'false').lower() == 'true'
    gogs_disable_registration = os.environ.get('GOGS_DISABLE_REGISTRATION', 'false').lower() == 'true'
    gogs_enable_federated_avatar = os.environ.get('GOGS_ENABLE_FEDERATED_AVATAR', 'true').lower() == 'true'
    gogs_disable_gravatar = os.environ.get('GOGS_DISABLE_GRAVATAR', 'false').lower() == 'true'
    gogs_provider = os.environ.get('GOGS_PROVIDER', 'file')
    gogs_log_level = os.environ.get('GOGS_LOG_LEVEL', 'Info')
    gogs_http_addr = os.environ.get('GOGS_HTTP_ADDR', '0.0.0.0')
    gogs_external_url = os.environ.get('GOGS_EXTERNAL_URL', f'http://127.0.0.1:{gogs_port}/')
    gogs_offline_mode = os.environ.get('GOGS_OFFLINE_MODE', 'false').lower() == 'true'
    gogs_require_signin_view = os.environ.get('GOGS_REQUIRE_SIGNIN_VIEW', 'false').lower() == 'true'
    gogs_ssh_listen_port = os.environ.get('GOGS_SSH_LISTEN_PORT', gogs_ssh_port)
    gogs_start_ssh_server = os.environ.get('GOGS_START_SSH_SERVER', 'true').lower() == 'true'
    
    return {
        'container_name': container_name,
        'gogs_image': gogs_image,
        'gogs_image_fallback': gogs_image_fallback,
        'gogs_port': gogs_port,
        'gogs_ssh_port': gogs_ssh_port,
        'gogs_data_volume': gogs_data_volume,
        'gogs_domain': gogs_domain,
        'gogs_root_url': gogs_root_url,
        'gogs_app_data_path': gogs_app_data_path,
        'gogs_secret_key': gogs_secret_key,
        'gogs_install_lock': gogs_install_lock,
        'gogs_require_email_confirmation': gogs_require_email_confirmation,
        'gogs_disable_registration': gogs_disable_registration,
        'gogs_enable_federated_avatar': gogs_enable_federated_avatar,
        'gogs_disable_gravatar': gogs_disable_gravatar,
        'gogs_provider': gogs_provider,
        'gogs_log_level': gogs_log_level,
        'gogs_http_addr': gogs_http_addr,
        'gogs_external_url': gogs_external_url,
        'gogs_offline_mode': gogs_offline_mode,
        'gogs_require_signin_view': gogs_require_signin_view,
        'gogs_ssh_listen_port': gogs_ssh_listen_port,
        'gogs_start_ssh_server': gogs_start_ssh_server,
    }

def create_app_ini(config):
    """Create the Gogs app.ini configuration file from environment variables"""
    app_ini_content = f"""[server]
APP_DATA_PATH = {config['gogs_app_data_path']}
DOMAIN = {config['gogs_domain']}
HTTP_PORT = 3000
HTTP_ADDR = 0.0.0.0
EXTERNAL_URL = {config['gogs_external_url']}
DISABLE_SSH = false
SSH_PORT = 2222
SSH_LISTEN_PORT = 2222
START_SSH_SERVER = {'true' if config['gogs_start_ssh_server'] else 'false'}
OFFLINE_MODE = {'true' if config['gogs_offline_mode'] else 'false'}

[database]
TYPE = sqlite3
PATH = {config['gogs_app_data_path']}/data/gogs.db

[repository]
ROOT = /data/git

[security]
INSTALL_LOCK = false
SECRET_KEY = {config['gogs_secret_key']}

[auth]
REQUIRE_EMAIL_CONFIRMATION = {'true' if config['gogs_require_email_confirmation'] else 'false'}
DISABLE_REGISTRATION = {'true' if config['gogs_disable_registration'] else 'false'}
ENABLE_REGISTRATION_CAPTCHA = false
REQUIRE_SIGNIN_VIEW = {'true' if config['gogs_require_signin_view'] else 'false'}

[user]
ENABLE_EMAIL_NOTIFICATION = false

[picture]
DISABLE_GRAVATAR = {'true' if config['gogs_disable_gravatar'] else 'false'}
ENABLE_FEDERATED_AVATAR = {'true' if config['gogs_enable_federated_avatar'] else 'false'}

[session]
PROVIDER = {config['gogs_provider']}

[log]
MODE = console
LEVEL = {config['gogs_log_level']}
ROOT_PATH = /app/gogs/log

[log.console]
LEVEL = console"""
    return app_ini_content

def run_simple_server():
    """Start a simple HTTP server for development when podman is not available.

    This is non-blocking - it prints instructions and returns False
    so the caller can exit gracefully instead of hanging.
    """
    try:
        print("\n" + "=" * 60)
        print("WARNING: Podman is not available. Cannot create Gogs container.")
        print("=" * 60)
        print("\nTo set up Gogs manually:")
        print("  1. Install podman:")
        print("     Ubuntu/Debian: sudo apt-get install podman")
        print("     Fedora/RHEL:   sudo dnf install podman")
        print("     CentOS:        sudo yum install podman")
        print("\n  2. Then run: make build")
        print("\nAlternatively, start a simple dev server with:")
        print("  make quick-build")
        print("\n" + "=" * 60)
        return False

    except Exception as e:
        print(f"Error: {e}")
        return False

def create_gogs_container():
    try:
        # Get the correct podman command
        podman_cmd = get_podman_command()

        # Get configuration from environment variables
        config = get_config_from_env()

        # INSTALL_LOCK = false
        # SSH_PORT = 2222
        # SSH_LISTEN_PORT = 2222

        # Create configuration directory
        os.makedirs("/tmp/gogs-config", exist_ok=True)

        # Create app.ini configuration
        app_ini_content = create_app_ini(config)
        config_path = "/tmp/gogs-config/app.ini"
        
        if os.path.exists(config_path):
            try:
                os.remove(config_path)
            except Exception:
                pass

        try:
            with open(config_path, "w") as f:
                f.write(app_ini_content)
        except PermissionError:
            import tempfile
            fd, config_path = tempfile.mkstemp(prefix="gogs-app-", suffix=".ini", dir="/tmp")
            with os.fdopen(fd, "w") as f:
                f.write(app_ini_content)

        # Create volumes (handle case where volume already exists)
        try:
            subprocess.run([podman_cmd, "volume", "create", config['gogs_data_volume']], check=True)
        except subprocess.CalledProcessError as vol_err:
            if vol_err.returncode != 125 and "already exists" not in str(vol_err):
                raise vol_err

        # Create container
        subprocess.run([
            podman_cmd, "run", "-d",
            "--replace",
            "--name", config['container_name'],
<<<<<<< HEAD
            "--network", "host",
=======
            "--publish", f"{config['gogs_port']}:3000",
            "--publish", "2222:22",
>>>>>>> 5f3ce7200d9df3cd958d1e7eb0cad23fa2b78858
            "--restart", "unless-stopped",
            "--label", "io.containers.autoupdate=image",
            "--label", "io.podman.desktop=true",
            "--label", "app=gogs",
            "--label", f"version={config['gogs_port']}",
            "-v", f"{config['gogs_data_volume']}:/data",
<<<<<<< HEAD
            "-v", f"/tmp/gogs-config/app.ini:/data/gogs/conf/app.ini",
=======
            "-v", f"{config_path}:/data/gogs/conf/app.ini",
>>>>>>> 5f3ce7200d9df3cd958d1e7eb0cad23fa2b78858
            "-e", "USER_UID=1000",
            "-e", "USER_GID=1000",
            "-e", "GIT_DISCOVERY=true",
            "-e", "HTTP_ADDR=0.0.0.0",
            "-e", "HTTP_PORT=3000",
            "-e", f"SSH_PORT={config['gogs_ssh_port']}",
            "-e", f"SSH_LISTEN_PORT={config['gogs_ssh_listen_port']}",
            config['gogs_image']
        ], check=True)

        # Wait briefly for container initialization
        time.sleep(2)

        # Generate SSH host keys
        subprocess.run([
            podman_cmd, "exec", config['container_name'], "/bin/sh", "-c",
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
        print(f"Access Gogs at: http://127.0.0.1:{config['gogs_port']}")
        print(f"SSH access at: 127.0.0.1:{config['gogs_ssh_port']}")

        return True

    except Exception as e:
        print(f"Error creating Gogs container: {e}")
        print("Starting simple HTTP server as fallback...")
        run_simple_server()
        return True

if __name__ == "__main__":
    success = create_gogs_container()
    sys.exit(0 if success else 1)
