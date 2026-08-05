# Deployment Connectivity Troubleshooting Guide

This guide helps you troubleshoot connectivity issues when the GitHub Actions deployment verification fails.

## Common Issues and Solutions

### 1. Firewall Blocking Port 8000

**Check firewall status:**
```bash
# On your server
sudo ufw status

# If UFW is not active, activate it and allow the port
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 8000/tcp
```

**Alternative for iptables:**
```bash
# Check current rules
sudo iptables -L INPUT -n

# Allow port 8000 if needed
sudo iptables -I INPUT -p tcp --dport 8000 -j ACCEPT
```

### 2. Container Not Binding to External Interface

The Docker container might be binding only to localhost. Check the container:

```bash
# Check if container is running
docker ps

# Check container logs
docker logs wildeditor-backend

# Check what ports are bound
ss -tlnp | grep :8000
```

If the port shows as `127.0.0.1:8000` instead of `0.0.0.0:8000`, the container is only accepting local connections.

### 3. Cloud Provider Security Groups

If you're using a cloud provider (AWS, GCP, Azure, etc.), check security groups:

- **AWS**: Check Security Groups in EC2 console
- **GCP**: Check Firewall Rules in VPC console  
- **Azure**: Check Network Security Groups
- **DigitalOcean**: Check Firewalls in networking section

Make sure port 8000 is allowed for inbound traffic.

### 4. Network Address Translation (NAT)

If your server is behind NAT, external connections might not work. Test locally first:

```bash
# On the server, test locally
curl http://localhost:8000/api/health

# Test from outside (if this fails, it's a network issue)
curl http://YOUR_SERVER_IP:8000/api/health
```

## Debugging Steps

### Step 1: Test Container Health
```bash
ssh your-user@your-server
docker exec wildeditor-backend curl http://localhost:8000/api/health
```

### Step 2: Test Local Port Access
```bash
curl http://localhost:8000/api/health
```

### Step 3: Test External Port Access
From your local machine:
```bash
curl http://YOUR_SERVER_IP:8000/api/health
```

### Step 4: Check Container Port Binding
```bash
docker port wildeditor-backend
# Should show: 8000/tcp -> 0.0.0.0:8000
```

## Quick Fixes

### Fix 1: Restart Container with Proper Port Binding
```bash
docker stop wildeditor-backend
docker rm wildeditor-backend

docker run -d \
  --name wildeditor-backend \
  --restart unless-stopped \
  -p 0.0.0.0:8000:8000 \
  -e MYSQL_DATABASE_URL="your_db_url" \
  -e ENVIRONMENT="production" \
  ghcr.io/luminarimud/wildeditor-backend:latest
```

### Fix 2: Open Firewall Port
```bash
sudo ufw allow 8000/tcp
sudo ufw reload
```

### Fix 3: Check Application Binding
Make sure your FastAPI application binds to `0.0.0.0:8000` not `127.0.0.1:8000`.

## Test the Deployment Manually

You can test the deployment verification manually:

```bash
# From your local machine or GitHub Actions runner
timeout 10 bash -c "echo >/dev/tcp/YOUR_SERVER_IP/8000"
curl -v http://YOUR_SERVER_IP:8000/api/health
```

## Temporary Solution: Skip Verification

If you need to deploy without verification, you can temporarily disable the verification step by adding this condition:

```yaml
- name: Verify deployment
  if: false  # Temporarily disable verification
  run: |
    # ... verification steps
```

## Production Considerations

1. **Use a reverse proxy** (nginx) in front of your application
2. **Set up SSL/TLS** for HTTPS
3. **Use a load balancer** for high availability
4. **Configure proper logging** and monitoring
5. **Set up health checks** at the infrastructure level

## Getting Help

If none of these solutions work, provide the following information:

1. Server OS and version
2. Cloud provider (if any)
3. Output of `docker logs wildeditor-backend`
4. Output of `ss -tlnp | grep :8000`
5. Output of `sudo ufw status` or `sudo iptables -L INPUT -n`
6. Network topology (is the server behind a firewall/NAT?)

This will help diagnose the specific networking issue preventing external access to your application.
