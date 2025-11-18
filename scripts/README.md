# Scripts Directory

This directory contains utility scripts for managing the Shrimp Vision application.

## Main Scripts

### `start.sh` / `start.bat`
**Location:** Root directory (for convenience)

Main startup script that starts both backend and frontend servers. This is the primary entry point for the application.

- **Usage (Linux/macOS):** `./start.sh`
- **Usage (Windows):** `scripts\start.bat`

## Utility Scripts

### `setup.sh`
Initial setup script that installs dependencies and configures the environment.

**Usage:**
```bash
./scripts/setup.sh
```

### `restart.sh`
Restarts the application by stopping existing processes and starting fresh.

**Usage:**
```bash
./scripts/restart.sh
```

### `start-network.sh` / `start-network.bat`
Starts the application with network configuration for cross-device access.

**Usage:**
```bash
./scripts/start-network.sh
```

### `start-cross-subnet.sh`
Starts the application configured for cross-subnet network access.

**Usage:**
```bash
./scripts/start-cross-subnet.sh
```

### `update-heic-support.sh`
Utility script to update HEIC/HEIF image format support.

**Usage:**
```bash
./scripts/update-heic-support.sh
```

## Notes

- All scripts should be run from the project root directory
- Make sure scripts are executable: `chmod +x scripts/*.sh`
- Windows users should use `.bat` files instead of `.sh` files

