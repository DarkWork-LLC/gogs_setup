#!/bin/bash

# Direct Gogs Setup Script (Docker)
# This script sets up Gogs with Docker and SQLite without requiring Ansible

set -e

# Configuration
CONTAINER_NAME="gogs"
IMAGE="gogs/gogs:latest"
PORT=3000
SSH_PORT=2222
DATA_VOLUME="gogs_data"
CONFIG_DIR="/tmp/gogs-config"

echo "========================================"
echo "Gogs Direct Setup Script"
echo "========================================"

# Check if docker is available
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    echo "Please install Docker and try again"
    exit 1
fi

echo "✓ Docker is available"

# Stop and remove existing container if running
echo "Stopping existing Gogs container..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm -f $CONTAINER_NAME 2>/dev/null || true

# Create persistent volume
echo "Creating persistent volume..."
docker volume create $DATA_VOLUME 2>/dev/null || true

# Pull the image
echo "Pulling Gogs image..."
docker pull $IMAGE

# Create configuration directory
mkdir -p $CONFIG_DIR
rm -f $CONFIG_DIR/app.ini 2>/dev/null || true

# Create app.ini configuration
cat > $CONFIG_DIR/app.ini << EOF
[server]
APP_DATA_PATH = /data/gogs
DOMAIN           = localhost
HTTP_PORT        = $PORT
HTTP_ADDR        = 0.0.0.0
EXTERNAL_URL     = http://127.0.0.1:$PORT/
DISABLE_SSH      = false
SSH_PORT         = $SSH_PORT
SSH_LISTEN_PORT  = $SSH_PORT
START_SSH_SERVER = true
OFFLINE_MODE     = false

[database]
TYPE = sqlite3
PATH = /data/gogs/data/gogs.db

[repository]
ROOT = /data/git

[security]
INSTALL_LOCK = true
SECRET_KEY   = gogs-secret-key-123456789012345678901234

[auth]
REQUIRE_EMAIL_CONFIRMATION = false
DISABLE_REGISTRATION       = false
ENABLE_REGISTRATION_CAPTCHA = false
REQUIRE_SIGNIN_VIEW        = false

[user]
ENABLE_EMAIL_NOTIFICATION = false

[picture]
DISABLE_GRAVATAR        = false
ENABLE_FEDERATED_AVATAR = true

[session]
PROVIDER = file

[log]
MODE      = console
LEVEL     = Info
ROOT_PATH = /app/gogs/log

[log.console]
LEVEL = console
EOF

echo "✓ Configuration file created"

# Create and run the container
echo "Creating and starting Gogs container..."
docker run -d \
    --name $CONTAINER_NAME \
    --publish $PORT:3000 \
    --publish $SSH_PORT:22 \
    --restart unless-stopped \
    --label "app=gogs" \
    --label "version=$PORT" \
    -v $DATA_VOLUME:/data \
    -v $CONFIG_DIR/app.ini:/data/gogs/conf/app.ini \
    -e USER_UID=1000 \
    -e USER_GID=1000 \
    -e GIT_DISCOVERY=true \
    -e HTTP_ADDR=0.0.0.0 \
    -e HTTP_PORT=3000 \
    -e SSH_PORT=22 \
    -e SSH_LISTEN_PORT=22 \
    $IMAGE

# Wait for container to start
echo "Waiting for Gogs to start..."
sleep 10

# Generate SSH host keys
echo "Generating SSH host keys..."
docker exec $CONTAINER_NAME /bin/sh -c '
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

# Get container status
STATUS=$(docker ps --filter name=$CONTAINER_NAME --format '{{.Status}}')
IP=$(docker inspect $CONTAINER_NAME --format '{{.NetworkSettings.IPAddress}}' 2>/dev/null || echo "Not available")

echo ""
echo "========================================"
echo "Gogs Setup Complete!"
echo "========================================"
echo ""
echo "Access Gogs at: http://127.0.0.1:$PORT"
echo "SSH access at: 127.0.0.1:$SSH_PORT"
echo ""
echo "Container name: $CONTAINER_NAME"
echo "Container status: $STATUS"
echo "Container IP: $IP"
echo ""
echo "Data volumes:"
echo "  - $DATA_VOLUME → /data (application data and database)"
echo ""
echo "Important notes:"
echo "  - The container will automatically restart after system reboot"
echo "  - Data persists across container restarts and removals"
echo "  - To stop: docker stop $CONTAINER_NAME"
echo "  - To remove: docker rm -v $CONTAINER_NAME"
echo "  - To view logs: docker logs -f $CONTAINER_NAME"
echo "========================================"