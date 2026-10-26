# Makefile for Gogs Podman Setup
# 
# Usage:
#   make install-deps  - Install required dependencies (ansible, podman)
#   make build         - Create and start Gogs container
#   make clean         - Stop and remove Gogs container and volumes
#   make start         - Start existing Gogs container
#   make stop          - Stop Gogs container
#   make restart       - Restart Gogs container
#   make status        - Show container status
#   make logs          - Show container logs
#   make volumes       - List Gogs volumes
#   make lint          - Check for syntax and configuration issues

.PHONY: help install-deps build clean start stop restart status logs volumes lint desktop run-python-scripts run-shell-scripts export import

# Default target
help:
	@echo "Gogs Podman Setup - Makefile targets:"
	@echo ""
	@echo "  install-deps   - Install required dependencies (ansible, podman)"
	@echo "  build          - Create and start Gogs container (runs ansible playbook)"
	@echo "  quick-build    - Quick setup, skip dependency installation, direct to Python script"
	@echo "  clean          - Stop and remove Gogs container and volumes"
	@echo "  start          - Start existing Gogs container"
	@echo "  stop           - Stop Gogs container"
	@echo "  restart        - Restart Gogs container"
	@echo "  status         - Show container status"
	@echo "  logs           - Show container logs (follow mode)"
	@echo "  volumes        - List Gogs volumes"
	@echo "  lint           - Check for syntax and configuration issues"
	@echo "  desktop        - Show Podman Desktop integration information"
	@echo "  export         - Export Gogs configuration and data to tarball (backup)"
	@echo "  import         - Import Gogs backup from tarball (restore)"
	@echo ""

# Install dependencies
install-deps:
	@echo "Installing dependencies..."
	if ! command -v podman >/dev/null 2>&1; then \
		echo "Warning: podman not found, some features may be limited"; \
	fi
	if ! command -v ansible-playbook >/dev/null 2>&1; then \
		echo "Installing ansible..."; \
		pip install ansible; \
	fi
	
	# Check for newuidmap (required for rootless podman)
	@command -v newuidmap >/dev/null 2>&1 || { \
		echo "Warning: newuidmap not found - installing uidmap package..."; \
		command -v apt-get >/dev/null 2>&1 && sudo apt-get update && sudo apt-get install -y uidmap || true; \
		command -v dnf >/dev/null 2>&1 && sudo dnf install -y shadow-utils || true; \
		command -v yum >/dev/null 2>&1 && sudo yum install -y shadow-utils || true; \
		true; }
	@echo "Dependencies installed."

# Build (run ansible playbook to create and start Gogs)
build: install-deps
	@echo "Setting up Gogs using Ansible playbook (with Python fallback)..."
	@python3 src/python/run_playbook.py
	@echo "Setup complete. Access Gogs at: http://localhost:3000"

# Quick build (skip dependency installation, direct to Python script)
quick-build:
	@echo "Quick setup - skipping dependency installation..."
	@python3 src/python/create_gogs_container.py
	@echo "Setup complete. Access Gogs at: http://localhost:3000"

# Clean (stop and remove container and volumes)
clean:
	@echo "Cleaning up Gogs container and volumes..."
	if command -v podman >/dev/null 2>&1; then \
		echo "Stopping Gogs container..."; \
		podman stop gogs 2>/dev/null || true; \
		echo "Removing Gogs container..."; \
		podman rm -v gogs 2>/dev/null || true; \
		echo "Removing Gogs volumes..."; \
		podman volume rm gogs_data 2>/dev/null || true; \
		echo "Force removing any remaining volumes..."; \
		podman volume prune -f 2>/dev/null || true; \
	else \
		echo "Warning: podman not found, skipping container cleanup"; \
	fi
	@echo "Cleanup complete."

# Start existing container
start:
	@echo "Starting Gogs container..."
	@podman start gogs

# Stop container
stop:
	@echo "Stopping Gogs container..."
	@podman stop gogs

# Restart container
restart: stop start

# Show container status
status:
	@podman ps --filter name=gogs --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Show container logs
logs:
	@podman logs -f gogs

# List volumes
volumes:
	@podman volume ls --filter name=gogs_data

# Lint target - Check for syntax and configuration issues
lint:
	@echo "Running lint checks..."
	@echo "Checking Ansible playbook syntax..."
	@ansible-playbook --syntax-check src/playbooks/gogs-podman-setup.yml
	@echo "Checking YAML syntax in playbook..."
	@python3 -c "import yaml; yaml.safe_load(open('src/playbooks/gogs-podman-setup.yml'))" && echo "YAML syntax OK" || echo "YAML syntax error"
	@echo "Checking Makefile syntax..."
	@make -n help >/dev/null && echo "Makefile syntax OK" || echo "Makefile syntax error"
	@echo "Lint checks complete."

# Podman Desktop integration
desktop:
	@echo "Podman Desktop integration:"

# Run Python scripts
run-python-scripts:
	@echo "Running Python scripts..."
	@python3 src/python/run_playbook.py
	@echo "Python scripts completed."

# Run shell scripts
run-shell-scripts:
	@echo "Running shell scripts..."
	@chmod +x src/scripts/*.sh
	@src/scripts/setup_gogs.sh
	@echo "Shell scripts completed."
	@echo "Container labels added for Podman Desktop management:"
	@echo "  - io.podman.desktop=true"
	@echo "  - app=gogs"
	@echo "  - version=3000"
	@echo "  - io.containers.autoupdate=image"
	@echo ""
	@echo "To manage the container in Podman Desktop:"
	@echo "1. Open Podman Desktop"
	@echo "2. The Gogs container should appear in the Containers list"
	@echo "3. You can start/stop/restart the container from the desktop interface"
	@echo "4. View logs and inspect the container through the GUI"

# Export (backup) Gogs configuration and data
# Usage: make export
# Creates a timestamped tarball with: volume data, app.ini config, container metadata

export:
	@echo "Exporting Gogs configuration and data..."
	EXPORT_DIR=$$(mktemp -d); \
	trap 'rm -rf $$EXPORT_DIR' EXIT; \
	if [ ! -d /tmp/gogs-config ] || [ ! -f /tmp/gogs-config/app.ini ]; then \
		echo "Warning: No existing Gogs configuration found at /tmp/gogs-config/app.ini"; \
		echo "You may need to run 'make build' first to create the configuration."; \
	fi; \
	\
	echo "Stopping Gogs container..."; \
	podman stop gogs 2>/dev/null || true; \
	echo "Exporting volume data..."; \
	if [ -d "$$HOME/.local/share/containers/storage/volumes/gogs_data/_data" ]; then \
		tar czf $$EXPORT_DIR/gogs_data.tar.gz -C $$HOME/.local/share/containers/storage/volumes/gogs_data/_data .; \
	elif command -v podman >/dev/null 2>&1; then \
		podman run --rm -v gogs_data:/data -v $$EXPORT_DIR:/export alpine tar czf /export/gogs_data.tar.gz -C /data . 2>/dev/null || { \
			echo "Warning: Some volume data could not be exported. The container may not exist."; \
		}; \
	else \
		echo "Warning: Neither podman nor volume data directory found. Skipping volume export."; \
	fi; \
	\
	echo "Exporting configuration..."; \
	if [ -f /tmp/gogs-config/app.ini ]; then \
		cp /tmp/gogs-config/app.ini $$EXPORT_DIR/app.ini; \
	else \
		echo "# No app.ini found - using default configuration" > $$EXPORT_DIR/app.ini; \
	fi; \
	\
	echo "Exporting container metadata..."; \
	mkdir -p $$EXPORT_DIR/container; \
	podman inspect gogs --format "{{(json .Config)}}" 2>/dev/null | tr -d '\n' > $$EXPORT_DIR/container/config.json 2>/dev/null || echo '{"warning":"No existing container config"}' > $$EXPORT_DIR/container/config.json; \
	BACKUP_FILE=$$(pwd)/gogs-backup-$$(date +%Y%m%d-%H%M%S).tar.gz; \
	tar czf $$BACKUP_FILE -C $$EXPORT_DIR .; \
	\
	echo ""; \
	echo "========================================"; \
	echo "Export complete!"; \
	echo "========================================"; \
	echo "Backup file: $$BACKUP_FILE"; \
	echo ""; \
	echo "To restore this backup, use:"; \
	echo "  make import BACKUP_FILE=$$BACKUP_FILE"; 
	@echo ""

# Import (restore) Gogs from a backup tarball
# Usage: make import BACKUP_FILE=/path/to/backup.tar.gz
import:
	@echo "Importing Gogs from backup..."
	if [ -z "$(BACKUP_FILE)" ]; then \
		echo "Error: BACKUP_FILE parameter is required."; \
		echo "Usage: make import BACKUP_FILE=/path/to/backup.tar.gz"; \
		exit 1; \
	fi; \
	 \
	if [ ! -f "$(BACKUP_FILE)" ]; then \
		echo "Error: Backup file '$(BACKUP_FILE)' not found."; \
		exit 1; \
	fi; \
	 \
	echo "Reading backup metadata..."; \
	BACKUP_DIR=$$(mktemp -d); \
	 tar xzf "$(BACKUP_FILE)" -C $$BACKUP_DIR; \
	 \
	echo "Stopping existing Gogs container if running..."; \
	 podman stop gogs 2>/dev/null || true; \
	 podman rm gogs 2>/dev/null || true; \
	 \
	echo "Creating Gogs data volume..."; \
	 podman volume create gogs_data 2>/dev/null || true; \
	 \
	echo "Restoring volume data..."; \
	if [ -d "$$HOME/.local/share/containers/storage/volumes/gogs_data/_data" ]; then \
		tar xzf $$BACKUP_DIR/gogs_data.tar.gz -C $$HOME/.local/share/containers/storage/volumes/gogs_data/_data; \
	elif command -v podman >/dev/null 2>&1; then \
		podman run --rm -v gogs_data:/data -v $$BACKUP_DIR:/import:ro alpine tar xzf /import/gogs_data.tar.gz -C /data 2>/dev/null || { \
			echo "Warning: Some volume data could not be restored. The container may not have been exported correctly."; \
		}; \
	else \
		echo "Warning: Neither podman nor volume data directory found. Skipping volume restore."; \
	fi; \
	 \
	echo "Restoring configuration..."; \
	 mkdir -p /tmp/gogs-config; \
	 cp $$BACKUP_DIR/app.ini /tmp/gogs-config/app.ini; \
	 \
	echo "Starting Gogs container..."; \
	 python3 src/python/create_gogs_container.py; \
	 \
	echo ""; \
	echo "========================================"; \
	echo "Import complete!"; \
	echo "========================================"; \
	echo "Gogs has been restored from backup:"; \
	echo "  Backup file: $(BACKUP_FILE)"; \
	echo "  Access URL: http://localhost:3000"; \
	echo ""; \
	echo "To manage your Gogs instance, use:"; \
	echo "  make start"; \
	echo "  make stop"; \
	echo "  make restart"; \
	echo "  make logs"; \
	@echo ""
