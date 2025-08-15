# MCP Server Deployment Guide

**Project**: Luminari Wilderness Editor MCP Server  
**Document**: Deployment Guide  
**Version**: 1.0  
**Date**: August 15, 2025  

## 🎯 Deployment Overview

This guide covers deploying the MCP server alongside the existing backend on the same physical server using Docker containers and Nginx reverse proxy.

## 🏗️ Deployment Architecture

### **Same-Server Multi-Container Setup**
```
Internet
    ↓
Nginx Reverse Proxy (Port 80/443)
    ├── /api/*     → Backend Container (Port 8000)
    └── /mcp/*     → MCP Server Container (Port 8001)
         ↓
    MySQL Database (Shared)
```

### **Service Communication**
```
External → Nginx → Backend/MCP Container → Shared Database
Internal → Container Network → Direct communication
```

## 📋 Prerequisites

### **Server Requirements**
- **OS**: Ubuntu 20.04+ or similar Linux distribution
- **Memory**: 4GB+ RAM (2GB increase from current)
- **CPU**: 2+ cores
- **Storage**: 20GB+ available space
- **Network**: Public IP with domain name (optional but recommended)

### **Software Requirements**
- Docker 20.10+
- Docker Compose 2.0+
- Git
- Nginx (if not using containerized version)

### **Environment Variables**
```bash
# Required for both services
MYSQL_DATABASE_URL=mysql+pymysql://user:pass@host:port/database
WILDEDITOR_API_KEY=your-secure-api-key

# Optional configuration
NODE_ENV=production
BACKEND_PORT=8000
MCP_PORT=8001
CORS_ORIGINS=https://your-frontend-domain.com
```

## 🚀 Deployment Methods

### **Method 1: Automated GitHub Actions Deployment (RECOMMENDED)**

#### **Setup Repository Secrets**
1. Navigate to GitHub repository → Settings → Secrets
2. Add the following secrets:
   ```
   PRODUCTION_HOST=your-server-ip-or-domain
   PRODUCTION_USER=your-deployment-user
   PRODUCTION_SSH_KEY=your-private-ssh-key
   MYSQL_DATABASE_URL=your-mysql-connection-string
   WILDEDITOR_API_KEY=your-api-key
   ```

#### **Deployment Process**
1. **Push to main branch** - triggers automatic deployment
2. **Monitor GitHub Actions** - check deployment status
3. **Verify deployment** - test both services

#### **GitHub Actions Workflow Summary**
```yaml
Trigger: Push to main branch
Steps:
  1. Test backend and MCP services
  2. Build Docker images
  3. Push images to registry
  4. Deploy to server via SSH
  5. Run health checks
  6. Rollback if any failures
```

### **Method 2: Manual Deployment**

#### **1. Server Preparation**
```bash
# Create deployment directory
sudo mkdir -p /opt/wildeditor
sudo chown $USER:$USER /opt/wildeditor
cd /opt/wildeditor

# Clone repository
git clone https://github.com/LuminariMUD/wildeditor.git .

# Create environment file
cat > .env << EOF
MYSQL_DATABASE_URL=mysql+pymysql://user:pass@host:port/database
WILDEDITOR_API_KEY=your-secure-api-key
NODE_ENV=production
BACKEND_PORT=8000
MCP_PORT=8001
CORS_ORIGINS=https://your-frontend-domain.com
EOF
```

#### **2. Docker Compose Configuration**
```bash
# Use same-server deployment configuration
cp deployment/docker-compose.same-server.yml docker-compose.yml

# Review and customize nginx configuration
cp deployment/nginx.conf nginx.conf
# Edit nginx.conf to match your domain
```

#### **3. Deploy Services**
```bash
# Build and start services
docker-compose up -d --build

# Monitor startup
docker-compose logs -f

# Verify all services are running
docker-compose ps
```

## 📁 Configuration Files

### **Docker Compose Configuration**
```yaml
# docker-compose.same-server.yml
version: '3.8'

services:
  wildeditor-backend:
    build:
      context: .
      dockerfile: apps/backend/Dockerfile
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    environment:
      - NODE_ENV=${NODE_ENV:-production}
      - MYSQL_DATABASE_URL=${MYSQL_DATABASE_URL}
      - WILDEDITOR_API_KEY=${WILDEDITOR_API_KEY}
    restart: unless-stopped
    networks:
      - wildeditor

  wildeditor-mcp:
    build:
      context: .
      dockerfile: apps/mcp/Dockerfile
    ports:
      - "${MCP_PORT:-8001}:8001"
    environment:
      - NODE_ENV=${NODE_ENV:-production}
      - MYSQL_DATABASE_URL=${MYSQL_DATABASE_URL}
      - WILDEDITOR_API_KEY=${WILDEDITOR_API_KEY}
      - BACKEND_URL=http://wildeditor-backend:8000
    restart: unless-stopped
    depends_on:
      - wildeditor-backend
    networks:
      - wildeditor

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - wildeditor-backend
      - wildeditor-mcp
    restart: unless-stopped
    networks:
      - wildeditor

networks:
  wildeditor:
    driver: bridge
```

### **Nginx Configuration**
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server wildeditor-backend:8000;
    }
    
    upstream mcp {
        server wildeditor-mcp:8001;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=mcp:10m rate=5r/s;
    
    server {
        listen 80;
        server_name your-domain.com;
        
        # Backend API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # MCP Server routes
        location /mcp/ {
            limit_req zone=mcp burst=10 nodelay;
            proxy_pass http://mcp/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Longer timeout for AI operations
            proxy_read_timeout 300s;
            proxy_connect_timeout 30s;
            proxy_send_timeout 300s;
        }
        
        # Health checks
        location /health {
            access_log off;
            proxy_pass http://backend/api/health;
        }
        
        location /mcp-health {
            access_log off;
            proxy_pass http://mcp/health;
        }
    }
}
```

## 🔍 Health Checks and Monitoring

### **Service Health Endpoints**
```bash
# Backend health check
curl http://localhost:8000/api/health
curl http://your-domain.com/health

# MCP server health check  
curl http://localhost:8001/health
curl http://your-domain.com/mcp-health

# Overall system status
curl http://your-domain.com/api/status
```

### **Docker Health Monitoring**
```bash
# Check container status
docker-compose ps

# View service logs
docker-compose logs wildeditor-backend
docker-compose logs wildeditor-mcp
docker-compose logs nginx

# Monitor resource usage
docker stats

# Check container health
docker inspect wildeditor-backend | grep Health
docker inspect wildeditor-mcp | grep Health
```

### **Automated Health Monitoring Script**
```bash
#!/bin/bash
# health-check.sh

echo "🔍 Checking Wildeditor Services Health..."

# Check backend
if curl -f -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    exit 1
fi

# Check MCP server
if curl -f -s http://localhost:8001/health > /dev/null; then
    echo "✅ MCP server is healthy"
else
    echo "❌ MCP server health check failed"
    exit 1
fi

# Check nginx routing
if curl -f -s http://localhost/health > /dev/null; then
    echo "✅ Nginx routing to backend works"
else
    echo "⚠️ Nginx routing to backend may have issues"
fi

if curl -f -s http://localhost/mcp-health > /dev/null; then
    echo "✅ Nginx routing to MCP works"
else
    echo "⚠️ Nginx routing to MCP may have issues"
fi

echo "🎉 All health checks completed"
```

## 🔒 SSL/HTTPS Configuration

### **Using Let's Encrypt (Recommended)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal setup
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### **Manual SSL Configuration**
```nginx
# Add to nginx.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    
    # Same location blocks as HTTP server
    # ... (copy from HTTP configuration)
}
```

## 🔄 Update and Rollback Procedures

### **Update Procedure**
```bash
# 1. Pull latest changes
cd /opt/wildeditor
git pull origin main

# 2. Backup current environment
docker-compose down
docker tag wildeditor-backend wildeditor-backend:backup
docker tag wildeditor-mcp wildeditor-mcp:backup

# 3. Build and deploy new version
docker-compose up -d --build

# 4. Verify deployment
./deployment/scripts/health-check.sh
```

### **Rollback Procedure**
```bash
# 1. Stop current services
docker-compose down

# 2. Restore backup images
docker tag wildeditor-backend:backup wildeditor-backend:latest
docker tag wildeditor-mcp:backup wildeditor-mcp:latest

# 3. Start backup version
docker-compose up -d

# 4. Verify rollback
./deployment/scripts/health-check.sh
```

## 🐛 Troubleshooting

### **Common Issues**

#### **Services Not Starting**
```bash
# Check logs
docker-compose logs

# Check disk space
df -h

# Check memory usage
free -h

# Restart services
docker-compose restart
```

#### **Database Connection Issues**
```bash
# Test database connectivity
docker-compose exec wildeditor-backend python -c "
from src.config.config_database import get_db
print('Database connection test')
"

# Check environment variables
docker-compose exec wildeditor-backend env | grep MYSQL
```

#### **Authentication Issues**
```bash
# Test API key
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/health

# Check environment variables
docker-compose exec wildeditor-backend env | grep API_KEY
docker-compose exec wildeditor-mcp env | grep API_KEY
```

#### **Network Issues**
```bash
# Check container network
docker network ls
docker network inspect wildeditor_wildeditor

# Check port bindings
docker-compose ps
netstat -tlnp | grep -E ':(80|443|8000|8001)'
```

### **Performance Issues**
```bash
# Monitor resource usage
docker stats

# Check application performance
curl -w "%{time_total}" http://localhost:8000/api/health
curl -w "%{time_total}" http://localhost:8001/health

# Database performance
docker-compose exec wildeditor-backend python -c "
import time
from src.config.config_database import get_db
start = time.time()
# Database query here
print(f'Query time: {time.time() - start}s')
"
```

## 📊 Monitoring and Alerting

### **Log Management**
```bash
# Configure log rotation
sudo cat > /etc/logrotate.d/docker-compose << EOF
/var/lib/docker/containers/*/*.log {
    daily
    rotate 7
    compress
    size 10M
    missingok
    delaycompress
    copytruncate
}
EOF
```

### **Prometheus Metrics (Optional)**
```yaml
# Add to docker-compose.yml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

## 🔧 Performance Optimization

### **Resource Allocation**
```yaml
# Add to docker-compose.yml services
wildeditor-backend:
  deploy:
    resources:
      limits:
        memory: 1G
        cpus: '1.0'
      reservations:
        memory: 512M
        cpus: '0.5'

wildeditor-mcp:
  deploy:
    resources:
      limits:
        memory: 2G
        cpus: '1.5'
      reservations:
        memory: 1G
        cpus: '1.0'
```

### **Database Optimization**
- Connection pooling configuration
- Query optimization
- Index optimization
- Regular maintenance tasks

### **Caching Strategy**
- Nginx static file caching
- Application-level caching
- Database query result caching

## 📞 Support and Maintenance

### **Regular Maintenance Tasks**
- Weekly health check reviews
- Monthly security updates
- Quarterly performance reviews
- Database maintenance and optimization

### **Backup Procedures**
- Daily database backups
- Weekly configuration backups
- Container image backups before updates

### **Emergency Procedures**
- Service restart procedures
- Rollback procedures
- Database recovery procedures
- Emergency contact information

---

**Document Version**: 1.0  
**Last Updated**: August 15, 2025  
**Next Review**: After first production deployment
