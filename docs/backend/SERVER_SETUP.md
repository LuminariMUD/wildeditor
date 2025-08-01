# Server Setup for GitHub Actions Deployment

This document explains how to set up your production server to work with the GitHub Actions deployment pipeline.

## Problem

The deployment was failing with this error:
```
sudo: a terminal is required to read the password; either use the -S option to read from standard input or configure an askpass helper
sudo: a password is required
Error: Process completed with exit code 1.
```

This happens because GitHub Actions runs non-interactively and cannot provide a password for `sudo` commands.

## Solution

We've updated the deployment process to be a **two-step process**:

1. **One-time server setup** (manual) - Prepares the server with Docker and proper permissions
2. **Automated deployment** (GitHub Actions) - Deploys the application without requiring sudo

## ⚠️ IMPORTANT: Server Must Be Set Up First

**The GitHub Actions deployment will fail if the server hasn't been properly set up first.** The deployment pipeline now assumes the server is already configured and will verify this before attempting deployment.

## Server Setup (Required First Step)

### Option 1: Automated Setup (Recommended)

Run the automated setup script on your server:

```bash
# Copy the setup script to your server
scp scripts/setup-server.sh user@your-server:/tmp/
ssh user@your-server

# Run the setup script
chmod +x /tmp/setup-server.sh
/tmp/setup-server.sh

# Log out and back in to activate docker group membership
exit
ssh user@your-server

# Test Docker access
docker run hello-world
```

### Option 2: Manual Setup

If you prefer to set up manually:

1. **Install Docker** (if not already installed):
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```

2. **Add your user to the docker group**:
   ```bash
   sudo usermod -aG docker $USER
   ```

3. **Log out and back in** to activate the group membership:
   ```bash
   exit
   # SSH back in
   ```

4. **Test Docker access**:
   ```bash
   docker run hello-world
   ```

5. **Create required directories**:
   ```bash
   sudo mkdir -p /opt/wildeditor-backend
   sudo chown $USER:$USER /opt/wildeditor-backend
   sudo mkdir -p /var/log/wildeditor
   sudo chown $USER:$USER /var/log/wildeditor
   ```

## GitHub Secrets Required

Make sure these secrets are configured in your GitHub repository (Settings → Secrets and variables → Actions):

### Required Secrets:
- **`PRODUCTION_HOST`** - Your server's hostname or IP address
- **`PRODUCTION_USER`** - The username for SSH access (e.g., `wildedit`)
- **`PRODUCTION_SSH_KEY`** - The private SSH key for authentication
- **`MYSQL_DATABASE_URL`** - Your MySQL/MariaDB connection string

### Database URL Format:
The `MYSQL_DATABASE_URL` should be in this format:
```
mysql+pymysql://username:password@hostname:port/database_name
```

Example:
```
mysql+pymysql://wildeditor_user:your_password@your-db-server.com:3306/wildeditor_db
```

### How to Add Secrets:
1. Go to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add each secret with its name and value

### Other Available Secrets:
- **`GITHUB_TOKEN`** - Already available in GitHub Actions (no need to add)
- **`SLACK_WEBHOOK_URL`** - Optional, for deployment notifications

## Verification

After setup, you can verify the configuration by running a test deployment or checking:

```bash
# Verify Docker access (should work without sudo)
docker ps

# Verify directories exist
ls -la /opt/wildeditor-backend
ls -la /var/log/wildeditor

# Check user groups
groups | grep docker
```

## Troubleshooting

### "User needs to be in docker group" error

This means the user hasn't been added to the docker group or needs to log out/in:

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in
exit
ssh user@your-server

# Verify
groups | grep docker
```

### "Docker not found" error

Docker isn't installed or not in PATH:

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verify installation
docker --version
```

### Permission denied on directories

The application directories don't have correct permissions:

```bash
sudo chown $USER:$USER /opt/wildeditor-backend
sudo chown $USER:$USER /var/log/wildeditor
```

## Security Notes

- The user only needs to be in the docker group, not have full sudo access
- Docker group membership is equivalent to root access, so only add trusted users
- Consider using Docker rootless mode for additional security in production environments
- Regularly update Docker and the base system for security patches

## Testing the Deployment

Once the server is set up, you can test the deployment by pushing to the main branch or manually triggering the GitHub Actions workflow. The deployment should now complete without sudo password prompts.
