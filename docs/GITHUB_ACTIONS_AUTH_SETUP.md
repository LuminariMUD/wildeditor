# GitHub Actions Authentication Setup

## Overview
This guide explains how to configure GitHub secrets for automatic deployment of the Wildeditor backend with API key authentication.

## Required GitHub Secrets

### 1. Database Configuration
- **Secret Name**: `MYSQL_DATABASE_URL`
- **Description**: MySQL database connection string
- **Format**: `mysql+pymysql://username:password@hostname:port/database_name`
- **Example**: `mysql+pymysql://wildeditor_user:secure_password@db.example.com:3306/luminari_mudprod`

### 2. API Authentication ⭐ NEW
- **Secret Name**: `WILDEDITOR_API_KEY`
- **Description**: Secure API key for backend authentication
- **Generate using PowerShell**:
  ```powershell
  [System.Convert]::ToBase64String((1..32 | ForEach-Object {Get-Random -Maximum 256}))
  ```
- **Example**: `ObWDRaWFm57pLZRpUItudM00AOZxOqdwBETVowlNt8g=`

### 3. Server Access
- **Secret Name**: `PRODUCTION_HOST`
- **Description**: Your server's IP address or domain name
- **Example**: `123.456.789.012` or `server.example.com`

- **Secret Name**: `PRODUCTION_USER`
- **Description**: SSH username for deployment
- **Example**: `wildedit` or `ubuntu`

- **Secret Name**: `PRODUCTION_SSH_KEY`
- **Description**: Private SSH key for server access
- **Generate using**:
  ```bash
  ssh-keygen -t ed25519 -f ~/.ssh/wildeditor_deploy -N ""
  ```

## Setting Up GitHub Secrets

### Step 1: Generate the API Key
```powershell
# Run this in PowerShell to generate a secure API key
[System.Convert]::ToBase64String((1..32 | ForEach-Object {Get-Random -Maximum 256}))
```

Copy the generated key (e.g., `ObWDRaWFm57pLZRpUItudM00AOZxOqdwBETVowlNt8g=`)

### Step 2: Add Secrets to GitHub

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret:

#### Database Secret
- **Name**: `MYSQL_DATABASE_URL`
- **Value**: `mysql+pymysql://your_username:your_password@your_host:3306/your_database`

#### API Key Secret ⭐ NEW
- **Name**: `WILDEDITOR_API_KEY`
- **Value**: `ObWDRaWFm57pLZRpUItudM00AOZxOqdwBETVowlNt8g=` (your generated key)

#### Server Secrets
- **Name**: `PRODUCTION_HOST`
- **Value**: `your.server.address.com`

- **Name**: `PRODUCTION_USER`
- **Value**: `your_ssh_username`

- **Name**: `PRODUCTION_SSH_KEY`
- **Value**: (paste your private SSH key)

## What the GitHub Actions Will Do

### Automatic Environment Configuration
The deployment workflow will automatically:

1. **Pull the latest Docker image**
2. **Configure environment variables**:
   ```bash
   MYSQL_DATABASE_URL=<from secret>
   WILDEDITOR_API_KEY=<from secret>
   REQUIRE_AUTH=true
   ENVIRONMENT=production
   DEBUG=false
   PORT=8000
   LOG_LEVEL=INFO
   WORKERS=4
   ENABLE_DOCS=false
   ```

3. **Start the container** with authentication enabled
4. **Verify deployment** including authentication testing

### Authentication Testing
The deployment includes automatic tests:
- ✅ Health endpoint test
- 🔐 Authentication endpoint test with your API key
- 🌐 External connectivity verification

## Using Your Deployed API

### For Administrators/Builders
Once deployed, share the API key with authorized users:

```bash
# Test authentication (replace with your server and API key)
curl -H "Authorization: Bearer ObWDRaWFm57pLZRpUItudM00AOZxOqdwBETVowlNt8g=" \
     http://your-server:8000/api/auth/status

# Expected response:
# {"authenticated": true, "message": "Authentication successful"}
```

### API Endpoints
- **Public (no auth required)**:
  - `GET /api/health` - Health check
  - `GET /api/regions` - View regions
  - `GET /api/paths` - View paths
  - `GET /api/points` - View points

- **Protected (API key required)**:
  - `POST /api/regions` - Create region
  - `PUT /api/regions/{id}` - Update region
  - `DELETE /api/regions/{id}` - Delete region
  - `POST /api/paths` - Create path
  - `PUT /api/paths/{id}` - Update path
  - `DELETE /api/paths/{id}` - Delete path

## Security Notes

### API Key Security
- ✅ The API key is stored as a GitHub secret (encrypted)
- ✅ The key is passed securely to the Docker container
- ✅ The key is not logged or exposed in deployment outputs
- ✅ Only the first 8 characters are shown in logs for debugging

### Recommended Practices
1. **Rotate the API key** periodically by generating a new one and updating the GitHub secret
2. **Limit access** to the GitHub repository to trusted administrators
3. **Monitor usage** via server logs
4. **Use HTTPS** in production (configure reverse proxy/SSL)

## Troubleshooting

### Deployment Fails with "API key not configured"
- Check that `WILDEDITOR_API_KEY` secret is set in GitHub
- Verify the secret name is spelled correctly
- Regenerate the API key if needed

### Authentication not working
- Verify the API key matches exactly (no extra spaces)
- Check container logs: `docker logs wildeditor-backend`
- Test the auth endpoint as shown above

### Container won't start
- Check GitHub Actions logs for detailed error messages
- Verify all required secrets are configured
- Check server has sufficient resources

## Migration from Previous Setup

If you previously deployed without authentication:

1. **Add the new secret**: `WILDEDITOR_API_KEY`
2. **Redeploy**: Push to main branch to trigger deployment
3. **Update frontend**: The new authentication will be automatically used
4. **Share API key**: Give the key to authorized users

The system will automatically enable authentication on the next deployment!

## Example Complete Setup

```bash
# Your GitHub Secrets should look like:
MYSQL_DATABASE_URL=mysql+pymysql://wildeditor_user:SecurePass123@db.luminari.com:3306/luminari_mudprod
WILDEDITOR_API_KEY=ObWDRaWFm57pLZRpUItudM00AOZxOqdwBETVowlNt8g=
PRODUCTION_HOST=server.luminari.com
PRODUCTION_USER=wildedit
PRODUCTION_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmU...
-----END OPENSSH PRIVATE KEY-----
```

Once these are configured, every push to the main branch will automatically deploy your backend with API key authentication enabled! 🚀
