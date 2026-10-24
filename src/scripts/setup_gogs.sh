#!/bin/bash

# Setup Gogs with Podman
# This script creates a persistent Gogs installation using Podman

set -e  # Exit on any error

echo "Setting up Gogs with Podman..."

# Create configuration directory
echo "Creating Gogs configuration directory..."
mkdir -p /tmp/gogs-config
rm -f /tmp/gogs-config/app.ini 2>/dev/null || true

# Create app.ini configuration
echo "Creating Gogs app.ini configuration file..."
cat > /tmp/gogs-config/app.ini << 'EOF'
[server]
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
LEVEL = console
EOF

echo "Configuration file created successfully!"

# Stop and remove existing container if it exists
echo "Stopping and removing existing Gogs container if it exists..."
podman stop gogs 2>/dev/null || true
podman rm gogs 2>/dev/null || true

# Create persistent volume
echo "Creating persistent volume for Gogs data..."
podman volume create gogs_data 2>/dev/null || true

# Pull Gogs image
echo "Pulling Gogs image..."
podman pull docker.io/gogs/gogs:latest

# Create and run Gogs container
echo "Creating and running Gogs container..."
podman run -d \
  --replace \
  --name gogs \
  --publish 3000:3000 \
  --publish 2222:22 \
  --restart unless-stopped \
  --label "io.containers.autoupdate=image" \
  --label "io.podman.desktop=true" \
  --label "app=gogs" \
  --label "version=3000" \
  -v gogs_data:/data \
  -v /tmp/gogs-config/app.ini:/data/gogs/conf/app.ini \
  -e USER_UID=1000 \
  -e USER_GID=1000 \
  -e GIT_DISCOVERY=true \
  -e HTTP_ADDR=0.0.0.0 \
  -e HTTP_PORT=3000 \
  -e SSH_PORT=22 \
  -e SSH_LISTEN_PORT=22 \
  docker.io/gogs/gogs:latest

echo "Gogs container created and started!"

# Wait for container to be ready
echo "Waiting for Gogs to start..."
sleep 10

# Generate SSH host keys
echo "Generating SSH host keys..."
podman exec gogs /bin/sh -c '
if [ ! -f /data/ssh/ssh_host_rsa_key ]; then
  echo "Generating SSH host keys..."
  mkdir -p /data/ssh
  ssh-keygen -t rsa -b 4096 -f /data/ssh/ssh_host_rsa_key -N ""
  ssh-keygen -t ecdsa -b 521 -f /data/ssh/ssh_host_ecdsa_key -N ""
  ssh-keygen -t ed25519 -f /data/ssh/ssh_host_ed25519_key -N ""
  chown -R 1000:1000 /data/ssh
  chmod 600 /data/ssh/ssh_host_*_key
  chmod 644 /data/ssh/ssh_host_*_key.pub
  echo "SSH host keys generated successfully"
else
  echo "SSH host keys already exist"
fi'

# Display container status
echo "Container status:"
podman ps --filter name=gogs --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Display access information
echo ""
echo "=================================="
echo "Gogs Setup Complete!"
echo "=================================="
echo "Access Gogs at: http://127.0.0.1:3000"
echo "SSH access at: 127.0.0.1:2222"
echo ""
echo "Container name: gogs"
echo "Restart policy: unless-stopped"
echo ""
echo "Data volumes:"
echo "  - gogs_data → /data (application data and database)"
echo ""
echo "Important notes:"
echo "- The container will automatically restart after system reboot"
echo "- Data persists across container restarts and removals"
echo "- To stop: podman stop gogs"
echo "- To remove: podman rm -v gogs"
echo "- To view logs: podman logs -f gogs"
echo "=================================="

echo "Setup complete!"