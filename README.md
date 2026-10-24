# Gogs Git Service Setup

This project provides automated setup scripts and playbooks for deploying Gogs, a self-hosted Git service, using Docker and Podman.

## Features

- **Multiple Deployment Options**: Docker and Podman support
- **Automated Setup**: Ansible playbooks for streamlined deployment
- **Python Integration**: Scripts for container management and playbook execution
- **Shell Scripts**: Direct setup options for quick deployment
- **Build Automation**: Makefile for simplified project management

## Project Structure

```
src/
├── Makefile                    # Build automation
├── playbooks/                  # Ansible playbooks
│   ├── gogs-docker-setup.yml  # Docker deployment
│   ├── gogs-podman-setup.yml  # Podman deployment
│   └── gogs-podman-setup-python.yml  # Podman with Python integration
├── python/                     # Python scripts
│   ├── create_gogs_container.py  # Container creation
│   └── run_playbook.py        # Playbook execution
└── scripts/                    # Shell scripts
    ├── set-env.sh             # Environment setup
    ├── setup_gogs_direct.sh   # Direct setup
    └── setup_gogs.sh          # Main setup script
```

## Quick Start

### Using Docker
```bash
make docker-setup
```

### Using Podman
```bash
make podman-setup
```

### Direct Setup
```bash
./src/scripts/setup_gogs.sh
```

## Backup and Restore

### Export (Backup)
Creates a timestamped tarball containing the full Gogs volume data (repositories, database, SSH keys), configuration (`app.ini`), and container metadata.

```bash
make export
```

The backup file will be created in the current directory as `gogs-backup-YYYYMMDD-HHMMSS.tar.gz`.

### Import (Restore)
Restores Gogs from a previously created backup tarball. Requires the `BACKUP_FILE` parameter.

```bash
make import BACKUP_FILE=/path/to/gogs-backup-YYYYMMDD-HHMMSS.tar.gz
```

Example:
```bash
make import BACKUP_FILE=/home/user/gogs-backup-20261024-120000.tar.gz
```

## Requirements

- Docker or Podman
- Python 3.8+
- Ansible
- Make

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.