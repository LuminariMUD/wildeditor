# Wildeditor Backend API

FastAPI backend for Wildeditor Wilderness Management System with terrain bridge integration.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Actions │───▶│   Docker Image  │───▶│ Production Server│
│   CI/CD Pipeline │    │   (GHCR)        │    │ luminarimud.com │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                ┌───────▼───────┐
                                                │  Backend API  │
                                                │  Port 8000    │
                                                └───────┬───────┘
                                                        │
                                        ┌───────────────▼───────────────┐
                                        │      Terrain Bridge           │
                                        │  Game Engine Integration      │
                                        │      Port 8182               │
                                        └───────────────────────────────┘
```

## 📋 Features

### ✅ **Core API Endpoints**
- **Terrain Data**: Real-time terrain queries via game engine
- **Wilderness Rooms**: Room discovery and details
- **Zone Navigation**: Wilderness↔zone connection mapping
- **Spatial Queries**: Advanced region and path analysis
- **Batch Operations**: Efficient bulk data retrieval

### ✅ **Terrain Bridge Integration**
- **Real-time Game Data**: Direct connection to running game engine
- **Spatial Accuracy**: 100% accurate terrain and room data
- **Performance Optimized**: Cached responses and connection pooling
- **Error Handling**: Graceful fallbacks and retry logic

### ✅ **Zone Entrance Discovery**
- **Complete Mapping**: All wilderness→static zone connections
- **Navigation Data**: Direction, destination room, zone information
- **AI Integration**: Full data available to MCP tools

## 📋 Prerequisites

### For GitHub Actions Deployment

1. **GitHub Repository Secrets** (Settings → Secrets and variables → Actions):
   ```
   PRODUCTION_HOST=luminarimud.com
   PRODUCTION_USER=ornir
   PRODUCTION_SSH_KEY=ssh_private_key
   ```

2. **Production Server Requirements**:
   - Ubuntu/Linux with Docker installed
   - Running LuminariMUD game engine (terrain bridge on port 8182)
   - MySQL database with spatial extensions
   - Network connectivity between containers

### For Local Development

1. **Required Software**:
   - Docker and Docker Compose
   - Python 3.11+
   - Access to running game engine or mock terrain bridge

2. **Environment Setup**:
   ```bash
   cd apps/backend
   cp .env.example .env
   # Configure terrain bridge and database connections
   ```

## 🚀 API Endpoints

### Terrain Analysis
```http
GET /api/terrain/at-coordinates?x=0&y=0
GET /api/terrain/batch?x_min=0&y_min=0&x_max=10&y_max=10
```

### Wilderness Rooms
```http
GET /api/wilderness/rooms?limit=50
GET /api/wilderness/rooms/{vnum}
```

### Zone Connections (NEW)
```http
GET /api/wilderness/navigation/entrances
# Returns all wilderness rooms that connect to static zones
```

### Spatial Queries (NEW)  
```http
GET /api/points?x=0&y=0
# Returns regions and paths at coordinates using spatial indexing
```

## 🚀 Deployment Methods

### Method 1: Automatic Deployment via GitHub Actions

1. **Push to main branch** - triggers automatic deployment
2. **GitHub Actions builds** Docker image and pushes to GHCR
3. **Deploys to production** server with --network host
4. **Health checks** verify deployment success
2. **Monitor the workflow** in GitHub Actions tab
3. **Verify deployment** at your production URL

The GitHub Actions workflow will:
- Run tests and linting
- Build Docker image
- Push to GitHub Container Registry
- Deploy to your production server
- Run health checks
- Send notifications

### Method 2: Manual Deployment

#### On Production Server:

```bash
# Clone repository
git clone https://github.com/your-username/wildeditor.git
cd wildeditor/apps/backend

# Create production environment file
cp .env.production .env.production
# Edit with your actual values

# Build and deploy
docker build -t wildeditor-backend -f Dockerfile ../..
docker run -d \
  --name wildeditor-backend \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env.production \
  wildeditor-backend
```

#### Using Docker Compose:

```bash
cd apps/backend
docker-compose up -d
```

### Method 3: Local Testing

#### Linux/macOS:
```bash
cd apps/backend
./deploy.sh deploy
```

### Method 2: Manual Deployment

#### Linux/macOS:
```bash
cd apps/backend
./deploy.sh deploy
```

#### Windows:
```batch
cd apps\backend
deploy.bat deploy
```

## 🔧 Configuration

### Environment Variables

#### Required Settings:
```bash
# Terrain Bridge Connection
TERRAIN_BRIDGE_HOST=localhost
TERRAIN_BRIDGE_PORT=8182
TERRAIN_BRIDGE_TIMEOUT=30

# Database Connection (for spatial queries)
MYSQL_HOST=localhost  
MYSQL_PORT=3306
MYSQL_DATABASE=luminari
MYSQL_USER=wildeditor
MYSQL_PASSWORD=secure_password

# API Security
API_KEY=your_secure_api_key
CORS_ORIGINS=["http://localhost:3000","https://wildeditor.com"]
```

#### Production Settings (.env.production):
```bash
PORT=8000
ENVIRONMENT=production
LOG_LEVEL=INFO
WORKERS=4

# Terrain Bridge (Production Game Engine)
TERRAIN_BRIDGE_HOST=localhost
TERRAIN_BRIDGE_PORT=8182

# Database with Spatial Support
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=luminari
MYSQL_USER=wildeditor_user
MYSQL_PASSWORD=production_password

# Security
API_KEY=production_api_key
SECRET_KEY=very_secure_secret_key
DEBUG=false
```

### Terrain Bridge Integration

The backend connects to the LuminariMUD game engine via TCP socket:

```python
# Terrain Bridge Client Configuration
TERRAIN_BRIDGE_CONFIG = {
    "host": "localhost",
    "port": 8182,
    "timeout": 30,
    "retry_attempts": 3,
    "connection_pool": True
}
```

**Available Terrain Bridge Commands:**
- `ping` - Health check
- `get_terrain` - Single coordinate terrain data
- `get_terrain_batch` - Multiple coordinates  
- `get_static_rooms_list` - Wilderness room list
- `get_room_details` - Detailed room information
- `get_wilderness_exits` - Zone entrance discovery

### Database Setup

1. **Spatial Database Requirements**:
   ```sql
   -- MySQL with spatial extensions enabled
   CREATE DATABASE luminari CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. **Required Tables for Spatial Queries**:
   ```sql
   -- Region data with spatial indexing
   CREATE TABLE region_data (
     region_id INT PRIMARY KEY,
     name VARCHAR(255),
     zone_vnum INT,
     region_polygon POLYGON NOT NULL,
     SPATIAL INDEX idx_region_polygon (region_polygon)
   );

   -- Path data with spatial indexing  
   CREATE TABLE path_data (
     path_id INT PRIMARY KEY,
     name VARCHAR(255),
     zone_vnum INT,
     path_linestring LINESTRING NOT NULL,
     SPATIAL INDEX idx_path_linestring (path_linestring)
   );

   -- Optimization tables for fast spatial queries
   CREATE TABLE region_index (
     region_id INT,
     zone_vnum INT,
     x INT,
     y INT,
     INDEX idx_coordinates (x, y),
     INDEX idx_region_zone (region_id, zone_vnum)
   );

   CREATE TABLE path_index (
     path_id INT,
     zone_vnum INT,  
     x INT,
     y INT,
     INDEX idx_coordinates (x, y),
     INDEX idx_path_zone (path_id, zone_vnum)
   );
   ```

3. **Database User Setup**:
   ```sql
   CREATE USER 'wildeditor_user'@'%' IDENTIFIED BY 'secure_password';
   GRANT ALL PRIVILEGES ON luminari.* TO 'wildeditor_user'@'%';
   FLUSH PRIVILEGES;
   ```

## 🧪 Testing

### API Testing with PowerShell
```powershell
# Load test environment
. ./test-terrain-bridge-api.ps1

# Test core functionality
Test-WildernessAPI

# Test specific endpoints
Invoke-RestMethod -Uri "$BASE_URL/api/health"
Invoke-RestMethod -Uri "$BASE_URL/api/terrain/at-coordinates?x=0&y=0" -Headers @{"Authorization" = "Bearer $API_KEY"}
Invoke-RestMethod -Uri "$BASE_URL/api/wilderness/navigation/entrances" -Headers @{"Authorization" = "Bearer $API_KEY"}
```

### Health Monitoring
```bash
# Container health
docker ps | grep wildeditor-backend
docker logs wildeditor-backend

# API health check
curl http://localhost:8000/api/health

# Terrain bridge connectivity
curl http://localhost:8000/api/terrain/at-coordinates?x=0\&y=0 \
  -H "Authorization: Bearer your_api_key"
```
   ```

## 🔍 Monitoring and Debugging

### Health Checks

The API provides several health check endpoints:

```bash
# Basic health check
curl http://localhost:8000/api/health

# Detailed system info (development only)
curl http://localhost:8000/api/health/detailed
```

### Logging

#### Docker Logs:
```bash
docker logs wildeditor-backend
```

#### Application Logs:
```bash
# If LOG_FILE is configured
tail -f /var/log/wildeditor/backend.log
```

### Performance Monitoring

#### Container Stats:
```bash
docker stats wildeditor-backend
```

#### Database Connections:
```sql
SHOW PROCESSLIST;
SHOW STATUS LIKE 'Threads_connected';
```

## 🔒 Security Considerations

### Production Checklist:

- [ ] **Environment Variables**: All secrets in `.env.production`
- [ ] **Database Security**: Strong passwords, limited user privileges
- [ ] **Container Security**: Non-root user, minimal base image
- [ ] **Network Security**: Firewall configured, only necessary ports open
- [ ] **SSL/TLS**: HTTPS enabled with valid certificates
- [ ] **CORS**: Properly configured for your frontend domain
- [ ] **API Documentation**: Disabled in production (`ENABLE_DOCS=false`)
- [ ] **Logging**: Sensitive data not logged
- [ ] **Updates**: Regular security updates for base images and dependencies

### Nginx Reverse Proxy (Recommended):

```nginx
server {
    listen 80;
    server_name api.wildeditor.luminari.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 🐛 Troubleshooting

### Common Issues:

#### Container Won't Start:
```bash
# Check logs
docker logs wildeditor-backend

# Check if port is in use
netstat -tlnp | grep 8000

# Verify environment file
cat .env.production
```

#### Database Connection Failed:
```bash
# Test database connectivity from container
docker exec -it wildeditor-backend python -c "
import pymysql
conn = pymysql.connect(host='your_host', user='your_user', password='your_pass')
print('Database connection successful!')
"
```

#### Health Check Failing:
```bash
# Test health endpoint directly
curl -v http://localhost:8000/api/health

# Check container networking
docker inspect wildeditor-backend | grep -A 5 NetworkSettings
```

### Performance Issues:

#### High Memory Usage:
- Increase server resources
- Check for memory leaks in application logs
- Monitor database connection pooling

#### Slow API Responses:
- Check database performance
- Review API endpoint efficiency
- Monitor container resource usage

#### High CPU Usage:
- Check for infinite loops in application code
- Review database query performance
- Consider scaling with multiple workers

## 📊 Scaling and Performance

### Horizontal Scaling:

```bash
# Run multiple containers with load balancer
docker run -d --name wildeditor-backend-1 -p 8001:8000 ...
docker run -d --name wildeditor-backend-2 -p 8002:8000 ...
docker run -d --name wildeditor-backend-3 -p 8003:8000 ...
```

### Vertical Scaling:

```bash
# Increase container resources
docker run -d \
  --memory=2g \
  --cpus=2 \
  --name wildeditor-backend \
  ...
```

### Database Optimization:

```sql
## 🔄 Updates and Maintenance

### Automated Updates (via GitHub Actions):
1. **Push changes** to `main` branch
2. **GitHub Actions** automatically builds and deploys  
3. **Health checks** verify terrain bridge connectivity
4. **Rollback** available via container management

### Manual Updates:
```bash
# Pull latest changes
git pull origin main

# Rebuild and deploy
./deploy.sh deploy

# Check deployment status
docker ps | grep wildeditor-backend
curl http://localhost:8000/api/health
```

### Monitoring and Logs:
```bash
# Application logs
docker logs wildeditor-backend -f

# Terrain bridge connectivity
docker exec wildeditor-backend curl localhost:8182

# Database connectivity  
docker exec wildeditor-backend python -c "
from services.database import get_database_connection
conn = get_database_connection()
print('Database connected:', conn is not None)
"
```

## 🚨 Troubleshooting

### Common Issues

1. **Terrain Bridge Connection Failed**:
   ```bash
   # Check game engine is running
   telnet localhost 8182
   
   # Check container networking
   docker run --rm --network host nicolaka/netshoot telnet localhost 8182
   ```

2. **Database Connection Issues**:
   ```bash
   # Test database connection
   mysql -h localhost -u wildeditor_user -p luminari
   
   # Check spatial extensions
   SHOW ENGINES;  # Look for InnoDB with spatial support
   ```

3. **API Authentication Errors**:
   ```bash
   # Verify API key configuration
   docker exec wildeditor-backend env | grep API_KEY
   
   # Test with correct headers
   curl -H "Authorization: Bearer correct_api_key" http://localhost:8000/api/health
   ```

## 📊 Production Status

**Current Deployment**: ✅ **Live on luminarimud.com:8000**

### Key Metrics:
- **Uptime**: Monitored via health checks
- **Terrain Bridge Connectivity**: Real-time game engine integration
- **API Response Times**: < 50ms for single queries, < 200ms for batch
- **Zone Entrance Discovery**: 116 wilderness→zone connections mapped
- **Spatial Query Performance**: Optimized with spatial indexing

### Architecture Overview:
```
Production Server (luminarimud.com)
├── Backend API (Port 8000)              ✅ Active
├── MCP Server (Port 8001)               ✅ Active  
├── Terrain Bridge (Port 8182)           ✅ Active
├── Game Engine Integration              ✅ Connected
└── Spatial Database                     ✅ Optimized
```

## 📞 Support

- **Documentation**: Check this README and inline comments
- **Logs**: Always check application and container logs first
- **GitHub Issues**: Report bugs and feature requests
- **Health Checks**: Use built-in health endpoints for diagnostics

---

For more detailed information, see the individual configuration files and the main project documentation.
