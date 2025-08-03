# Database Configuration Guide

## Overview

The backend automatically detects whether it's running in development or production and configures the database connection accordingly:

- **Development** (`ENVIRONMENT=development`): Uses remote database server
- **Production** (`ENVIRONMENT=production`): Uses localhost database

## Configuration Options

### Option 1: Individual Components (Recommended)

Set these environment variables:

```bash
ENVIRONMENT=development  # or "production"
DB_HOST=your-database-server.com
DB_USER=wildeditor_user
DB_PASSWORD=your_password
DB_PORT=3306
DB_NAME=luminari_muddev
```

### Option 2: Full Database URL

Alternatively, set the complete URL (overrides individual components):

```bash
MYSQL_DATABASE_URL=mysql+pymysql://user:password@host:port/database
```

## Environment Behavior

### Development Environment
- **Default DB_HOST**: `your-remote-db-server.com` (configure in .env)
- **Purpose**: Connect to shared development database
- **Authentication**: Disabled by default (`REQUIRE_AUTH=false`)
- **Debug**: Enabled
- **API Docs**: Enabled at `/docs`

### Production Environment  
- **Default DB_HOST**: `localhost` (database on same server)
- **Purpose**: Connect to local production database
- **Authentication**: Required (`REQUIRE_AUTH=true`)
- **Debug**: Disabled
- **API Docs**: Disabled for security

## Setup Instructions

### For Development:
1. Copy `.env.development.example` to `.env`
2. Update `DB_HOST` with your remote database server
3. Set `DB_PASSWORD` with your actual password
4. Run: `python src/main.py`

### For Production:
1. Copy `.env.production.example` to `.env`
2. Set secure `WILDEDITOR_API_KEY` and `SECRET_KEY`
3. Configure `DB_PASSWORD` for local database
4. Ensure `ENVIRONMENT=production`
5. Deploy with your preferred method

## Database Connection Logs

The backend will log which database configuration it's using:

```
Development environment detected - using database host: remote-server.com
Production environment detected - using database host: localhost
```

## Troubleshooting

1. **Connection refused**: Check if `DB_HOST` is correct for your environment
2. **Access denied**: Verify `DB_USER` and `DB_PASSWORD`
3. **Database not found**: Ensure `DB_NAME` exists on the target server
4. **Wrong environment**: Check `ENVIRONMENT` variable is set correctly
