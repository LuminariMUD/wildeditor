# Scripts Directory

This directory contains utility scripts for the Wildeditor project.

## Available Scripts

### `setup-server.sh`

Automated server setup script for preparing a Ubuntu/Debian server for Docker deployment.

**Usage:**
```bash
# Copy to your server and run
scp scripts/setup-server.sh user@your-server:/tmp/
ssh user@your-server
chmod +x /tmp/setup-server.sh
/tmp/setup-server.sh
```

**What it does:**
- Installs Docker if not present
- Adds the current user to the docker group
- Creates required application directories
- Sets up basic firewall rules
- Tests the Docker installation

**Requirements:**
- Ubuntu/Debian server
- User with sudo access
- Internet connection

See `docs/backend/SERVER_SETUP.md` for detailed server setup instructions.

## Contributing

When adding new scripts:
1. Make them executable: `chmod +x script-name.sh`
2. Add proper error handling with `set -e`
3. Include usage documentation in this README
4. Test on a clean environment before committing
