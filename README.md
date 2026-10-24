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

## Requirements

- Docker or Podman
- Python 3.8+
- Ansible
- Make

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.