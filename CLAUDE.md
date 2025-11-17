# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository provides Docker images to run Interactive Brokers Gateway (IB Gateway) and Trader Workstation (TWS) without human interaction in containerized environments. The project includes two main images:

- **ib-gateway**: Headless IB Gateway with VNC access
- **tws-rdesktop**: TWS with full desktop environment via RDP

Key technologies:
- IB Gateway/TWS (financial trading platform)
- IBC (Interactive Brokers Controller) - automates TWS/Gateway login and operation
- Docker multi-stage builds
- Xvfb (virtual framebuffer for headless X11)
- socat (TCP port forwarding from localhost to external connections)
- SSH tunneling for secure remote access
- x11vnc (VNC server for ib-gateway)
- xrdp/xfce (remote desktop for TWS)

## Architecture

### Two-Image System

The project maintains two parallel image types built from templates:

1. **IB Gateway** (`Dockerfile.template` → `stable/Dockerfile`, `latest/Dockerfile`)
   - Lightweight headless gateway
   - Optional VNC access via x11vnc
   - User: `ibgateway` (uid 1000)
   - Config: `/home/ibgateway/Jts/jts.ini`, `/home/ibgateway/ibc/config.ini`

2. **TWS (Trader Workstation)** (`Dockerfile.tws.template` → `stable/Dockerfile.tws`, `latest/Dockerfile.tws`)
   - Full desktop environment based on linuxserver/rdesktop
   - RDP access on port 3389
   - User: `abc` (linuxserver default, uid 1000)
   - Config: `/opt/ibkr/jts.ini`, `/opt/ibc/config.ini`

### Multi-Stage Docker Builds

Both images use multi-stage builds with two stages:

1. **Setup stage**: Downloads and installs IB Gateway/TWS, IBC, and dependencies
2. **Build stage**: Creates minimal production image with only runtime requirements

### Version Management

- Two channels: `stable` and `latest`
- `update.sh` script generates version-specific Dockerfiles from templates
- IB Gateway installers stored as GitHub releases (not downloaded from IB directly)
- Version numbers embedded in build args: `IB_GATEWAY_VERSION`, `IBC_VERSION`

### Runtime Architecture

Container startup sequence (orchestrated by `scripts/run.sh`):

1. **Xvfb** - Virtual X11 server on DISPLAY :1
2. **VNC/RDP** (optional) - Remote access server
3. **Configuration** - Apply environment variables to config templates using `envsubst`
4. **IBC** - Launches IB Gateway/TWS with automated login
5. **Port Forwarding** - socat or SSH tunnel exposes API ports

Port mapping strategy:
- IB Gateway internal ports: 4001 (live), 4002 (paper)
- socat exposes these as: 4003 (live), 4004 (paper)
- docker-compose maps back to: 4001, 4002 on host localhost
- TWS uses 7496/7497 internally, exposed as 7498/7499, mapped to 7496/7497

### Configuration System

Environment variables → Template files → Runtime configs:
- Templates: `*.tmpl` files in `image-files/config/`
- Templates copied to `stable/` and `latest/` directories by `update.sh`
- `scripts/common.sh` applies env vars using `envsubst` unless `CUSTOM_CONFIG=yes`
- Supports Docker secrets via `_FILE` suffix convention (e.g., `TWS_PASSWORD_FILE`)

### Trading Modes

Supports three modes via `TRADING_MODE` env var:
- `paper` - Paper trading account only
- `live` - Live trading account only
- `both` - Run both paper and live in parallel processes within same container

When `TRADING_MODE=both`:
- Separate IBC processes for each mode
- Separate settings paths: `${TWS_SETTINGS_PATH}_paper` and `${TWS_SETTINGS_PATH}_live`
- Separate credentials: `TWS_USERID_PAPER`/`TWS_PASSWORD_PAPER` for paper account

## Building and Testing

### Build Commands

```bash
# Build from templates (required after updating versions)
./update.sh stable 10.37.1k  # or latest version
./update.sh latest 10.39.1i

# Build and run ib-gateway using docker compose
docker compose build --pull
docker compose up

# Build and run TWS
docker compose -f tws-docker-compose.yml build --pull
docker compose -f tws-docker-compose.yml up

# Local build for specific architecture
cd stable  # or latest
docker build -t my-ib-gateway .

# Cross-platform build (e.g., for AWS ECS)
# Uncomment platform: linux/amd64 in docker-compose.yml first
docker compose build --pull
```

### Testing Connection

```bash
# Test API connectivity
python test_connection.py

# Check container logs
docker compose logs -f

# Restart socat if API connection fails
docker exec -it algo-trader-ib-gateway-1 pkill -x socat

# Restart SSH tunnel
docker exec -it algo-trader-ib-gateway-1 pkill -x ssh

# Access VNC (ib-gateway)
# Connect VNC client to localhost:5900

# Access RDP (TWS)
# Connect RDP client to localhost:3370
```

## Important File Locations

### Templates and Configuration
- `Dockerfile.template` - IB Gateway Dockerfile template
- `Dockerfile.tws.template` - TWS Dockerfile template
- `image-files/config/ibgateway/jts.ini.tmpl` - IB Gateway config template
- `image-files/config/ibc/config.ini.tmpl` - IBC config template
- `image-files/scripts/run.sh` - Main startup script for ib-gateway
- `image-files/scripts/common.sh` - Shared functions (port settings, config application)
- `image-files/scripts/run_socat.sh` - Port forwarding with socat
- `image-files/scripts/run_ssh.sh` - SSH tunnel management

### Generated Files (do not edit directly)
- `stable/Dockerfile`, `stable/Dockerfile.tws`
- `latest/Dockerfile`, `latest/Dockerfile.tws`
- All files in `stable/` and `latest/` subdirectories are copied from `image-files/`

### Compose Files
- `docker-compose.yml` - IB Gateway service definition
- `tws-docker-compose.yml` - TWS service definition

## Key Environment Variables

Critical variables that affect architecture:
- `TRADING_MODE`: `paper`|`live`|`both` - Determines which API ports are active
- `TWS_SETTINGS_PATH`: Directory for persistent IB settings (use with volumes)
- `CUSTOM_CONFIG`: If `yes`, disables template processing (mount custom configs)
- `SSH_TUNNEL`: `yes`|`both` - Controls socat vs SSH tunnel for API access
- `GATEWAY_OR_TWS`: Internal var set in Dockerfile, affects port numbers and paths

Security-related:
- `TWS_PASSWORD_FILE`, `SSH_PASSPHRASE_FILE`, `VNC_SERVER_PASSWORD_FILE` - Docker secrets support
- Credentials never stored in image, only passed at runtime

## Development Workflow

### Updating IB Gateway/TWS Version

1. Download new installer from IB and upload to GitHub releases
2. Update version in command: `./update.sh stable 10.XX.XX`
3. Update version in command: `./update.sh latest 10.XX.XX`
4. Update README.md version table
5. Build and test both images
6. Tag and push to container registry

### Modifying Behavior

- **Startup logic**: Edit `image-files/scripts/run.sh` or `image-files/tws-scripts/run_tws.sh`
- **Port forwarding**: Edit `image-files/scripts/run_socat.sh` or `run_ssh.sh`
- **Config templating**: Edit `image-files/scripts/common.sh` (`apply_settings` function)
- **IBC settings**: Edit `image-files/config/ibc/config.ini.tmpl`
- **IB Gateway settings**: Edit `image-files/config/ibgateway/jts.ini.tmpl`

After changes: Run `./update.sh` to propagate to `stable/` and `latest/` directories.

### Cross-Platform Builds

For deploying to AWS ECS or other AMD64 platforms from ARM64 (M1/M2/M3):
1. Uncomment `platform: linux/amd64` in docker-compose.yml
2. Build with `docker compose build --pull`
3. Push to registry
4. Remember to comment out platform line for local development

## aarch64/ARM64 Support

Experimental support for Apple Silicon and Raspberry Pi:
- Requires building locally (no pre-built images)
- Uses Azul Zulu JRE for ARM64 instead of bundled x64 JVM
- Build both ib-gateway and TWS locally, tag appropriately
- See README.md "aarch64 support" section for detailed steps

## Security Considerations

- Default config binds ports to 127.0.0.1 only (not exposed to network)
- IB API protocol is unencrypted and unauthenticated
- For remote access, use SSH tunnels (not direct port exposure)
- SSH tunnel creates remote port on bastion, clients connect via local tunnel
- VNC/RDP only for development/debugging, use SSH tunnel in production
- Never commit `.env` file with real credentials
