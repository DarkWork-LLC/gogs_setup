# User Guide for Gogs Git Service Setup

This guide provides detailed instructions for setting up and using the Gogs Git service deployment project.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Troubleshooting](#troubleshooting)
6. [Maintenance](#maintenance)

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu/Debian, CentOS/RHEL, or similar)
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Storage**: Minimum 10GB free space
- **Network**: Internet access for package downloads

### Software Requirements

- **Docker** or **Podman** (version 2.0+)
- **Python** 3.8 or higher
- **Ansible** 2.9 or higher
- **Make** (for build automation)

### Installation Commands

#### Docker
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io

# CentOS/RHEL
sudo yum install docker
sudo systemctl start docker
sudo systemctl enable docker
```

#### Podman
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install podman

# CentOS/RHEL
sudo yum install podman
```

#### Python & Ansible
```bash
# Install Python 3.8+
sudo apt-get install python3.8 python3-pip

# Install Ansible
pip3 install ansible
```

## Installation Methods

### Method 1: Docker Setup (Recommended)

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-org/gogs-setup.git
   cd gogs-setup
   ```

2. **Run Docker Setup**
   ```bash
   make docker-setup
   ```

3. **Verify Installation**
   ```bash
   docker ps | grep gogs
   ```

### Method 2: Podman Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-org/gogs-setup.git
   cd gogs-setup
   ```

2. **Run Podman Setup**
   ```bash
   make podman-setup
   ```

3. **Verify Installation**
   ```bash
   podman ps | grep gogs
   ```

### Method 3: Direct Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-org/gogs-setup.git
   cd gogs-setup
   ```

2. **Run Direct Setup**
   ```bash
   ./src/scripts/setup_gogs.sh
   ```

3. **Verify Installation**
   ```bash
   ps aux | grep gogs
   ```

## Configuration

### Environment Variables

The setup scripts use the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `GOGS_VERSION` | Gogs version to install | `latest` |
| `GOGS_PORT` | Port for Gogs service | `3000` |
| `GOGS_DATA_DIR` | Data directory path | `/var/lib/gogs` |
| `GOGS_DB_TYPE` | Database type (sqlite3, mysql, postgres) | `sqlite3` |

### Custom Configuration

To customize the setup, create a `.env` file:

```bash
# .env file
GOGS_VERSION=0.12.3
GOGS_PORT=8080
GOGS_DATA_DIR=/opt/gogs-data
GOGS_DB_TYPE=mysql
```

### Ansible Variables

For advanced configuration, modify the Ansible variables in the playbooks:

```yaml
# src/playbooks/gogs-docker-setup.yml
gogs:
  version: "0.12.3"
  port: 8080
  data_dir: "/opt/gogs-data"
  db_type: "mysql"
  db_host: "localhost"
  db_user: "gogs"
  db_password: "password"
```

## Usage

### Starting Gogs

After installation, Gogs will automatically start. To manually start/stop:

```bash
# Docker
docker start gogs
docker stop gogs

# Podman
podman start gogs
podman stop gogs
```

### Accessing Gogs

Open your web browser and navigate to:

- **Default URL**: `http://localhost:3000`
- **Custom Port**: `http://localhost:PORT` (if configured)

### First-Time Setup

1. Open the Gogs web interface
2. Complete the installation wizard:
   - Set up administrator account
   - Configure database (SQLite, MySQL, or PostgreSQL)
   - Set repository root directory
   - Configure server settings

### Common Operations

#### Creating a Repository

1. Log in to Gogs
2. Click "New Repository"
3. Enter repository details
4. Choose visibility (public/private)
5. Click "Create Repository"

#### Managing Users

1. Log in as administrator
2. Go to "Admin Panel"
3. Navigate to "Users"
4. Add, edit, or delete users

#### Backup and Restore

```bash
# Backup
./src/scripts/backup_gogs.sh

# Restore
./src/scripts/restore_gogs.sh
```

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Check running services
sudo netstat -tulpn | grep :3000

# Kill conflicting process
sudo kill -9 PID
```

#### Permission Denied

```bash
# Fix permissions
sudo chown -R $USER:$USER /var/lib/gogs
sudo chmod -R 755 /var/lib/gogs
```

#### Container Not Starting

```bash
# Check logs
docker logs gogs
podman logs gogs

# Restart container
docker restart gogs
podman restart gogs
```

### Debug Mode

Enable debug logging:

```bash
# Set environment variable
export GOGS_DEBUG=true

# Restart service
docker restart gogs
```

### Logs Location

- **Docker**: `/var/lib/docker/containers/gogs/gogs.log`
- **Podman**: `/var/lib/containers/storage/gogs/gogs.log`
- **Direct**: `/var/log/gogs/gogs.log`

## Maintenance

### Updating Gogs

```bash
# Stop current service
docker stop gogs

# Pull latest version
docker pull gogs/gogs:latest

# Start new version
docker run -d --name gogs gogs/gogs:latest
```

### Cleaning Up

```bash
# Remove old containers
docker system prune -a

# Clean unused images
docker image prune -a
```

### Monitoring

```bash
# Check resource usage
docker stats gogs

# Monitor logs in real-time
docker logs -f gogs
```

## Support

For additional help and support:

- **Documentation**: [Gogs Official Docs](https://gogs.io/docs)
- **Issues**: [GitHub Issues](https://github.com/your-org/gogs-setup/issues)
- **Community**: [Gogs Community Forum](https://discourse.gogs.io/)

## Contributing

We welcome contributions! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) guide for details on how to contribute.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.