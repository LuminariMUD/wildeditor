# Authentication Setup Guide

## Overview

The Wildeditor API now uses simple API key authentication to protect write operations (create, update, delete). 

**Current Status:**
- ✅ **Backend**: API key authentication implemented and ready
- ⏳ **Frontend**: Authentication integration not yet implemented
- 🔧 **Manual Testing**: API can be tested directly with curl/Postman

## Backend Setup (✅ Complete)

### 1. Environment Variables

Add these environment variables to your backend configuration:

```bash
# Required: Your API key (change this to a secure, random string)
WILDEDITOR_API_KEY=your-super-secret-api-key-here-change-this

# Optional: Disable authentication for development (default: true)
REQUIRE_AUTH=true
```

### 2. Generate a Secure API Key

For production, generate a secure API key:

**PowerShell (Windows):**
```powershell
# Method 1: Using .NET crypto (recommended)
[System.Convert]::ToBase64String([System.Security.Cryptography.RNGCryptoServiceProvider]::new().GetBytes(32))

# Method 2: Simple random string
-join ((1..32) | ForEach {[char]((65..90) + (97..122) + (48..57) | Get-Random)})

# Method 3: Using GUID (less secure but simple)
[System.Guid]::NewGuid().ToString("N") + [System.Guid]::NewGuid().ToString("N")
```

**Command Prompt (Windows):**
```cmd
# Generate using PowerShell from CMD
powershell -Command "[System.Convert]::ToBase64String((1..32 | ForEach-Object {Get-Random -Maximum 256}))"
```

**Linux/Mac:**
```bash
# Generate a secure random key
openssl rand -hex 32

# Alternative using /dev/urandom
head /dev/urandom | tr -dc A-Za-z0-9 | head -c 64
```

**Online (if needed):**
- Use a secure password generator like https://passwordsgenerator.net/
- Generate a 64-character random string with letters, numbers, and symbols

### 3. Configuration Files

Update your backend `.env` file:

```bash
# Copy the example and fill in your values
cp apps/backend/.env.example apps/backend/.env

# Edit with your secure API key
nano apps/backend/.env
```

## Frontend Setup (⏳ Pending Implementation)

**Current Status**: The frontend has not yet been updated to use API key authentication.

### What Still Needs to Be Done

The frontend currently still has the original Supabase authentication components, but they need to be updated to:

1. **Replace Supabase Authentication**: Remove Supabase auth hooks and components
2. **Add API Key Input**: Create a simple form for entering the API key
3. **Store API Key**: Save the key locally (localStorage/sessionStorage)
4. **Include in Requests**: Add the API key to all authenticated API requests
5. **Handle Auth Errors**: Show appropriate messages when authentication fails

### Current Behavior

- **Frontend**: Still shows Supabase authentication (non-functional)
- **API Access**: Read operations work, write operations will fail without API key
- **Testing**: Can only test API authentication manually with curl/tools

### Temporary Workaround

For now, you can:
- Use the application in **read-only mode** (view regions, paths, points)
- Test write operations using **curl or API testing tools** with the API key
- Wait for frontend authentication integration

## Usage

### For Administrators/Builders

1. **Get Your API Key**: Contact your system administrator for the API key
2. **Login**: Enter the API key in the authentication form
3. **Access**: You now have full access to create, edit, and delete wilderness data

### For Read-Only Access

- Read operations (viewing regions, paths, points) work without authentication
- Only write operations require the API key

## Security Features

### Protected Endpoints

**Regions:**
- ✅ `GET /api/regions` - Public (read-only)
- ✅ `GET /api/regions/{id}` - Public (read-only)
- 🔐 `POST /api/regions` - Requires API key
- 🔐 `PUT /api/regions/{id}` - Requires API key
- 🔐 `DELETE /api/regions/{id}` - Requires API key
- 🔐 `POST /api/regions/landmarks` - Requires API key

**Paths:**
- ✅ `GET /api/paths` - Public (read-only)
- ✅ `GET /api/paths/{id}` - Public (read-only)
- ✅ `GET /api/paths/types` - Public (read-only)
- 🔐 `POST /api/paths` - Requires API key
- 🔐 `PUT /api/paths/{id}` - Requires API key
- 🔐 `DELETE /api/paths/{id}` - Requires API key

**Points:**
- ✅ `GET /api/points` - Public (read-only)

**System:**
- ✅ `GET /api/health` - Public
- 🔐 `GET /api/auth/status` - Requires API key (for testing)

### Error Responses

**401 Unauthorized:**
```json
{
  "detail": "Authentication required. Please provide API key in Authorization header."
}
```

**401 Invalid Key:**
```json
{
  "detail": "Invalid API key."
}
```

**500 Server Error:**
```json
{
  "detail": "API key not configured on server. Please contact administrator."
}
```

## Testing Authentication

### Test API Key Validation

```bash
# Test with valid API key
curl -H "Authorization: Bearer your-api-key-here" http://localhost:8000/api/auth/status

# Expected response:
# {"authenticated": true, "message": "Authentication successful"}

# Test without API key
curl http://localhost:8000/api/auth/status

# Expected response (if REQUIRE_AUTH=true):
# {"detail": "Authentication required..."}
```

### Test Protected Endpoints

```bash
# Try to create a path without authentication (should fail)
curl -X POST http://localhost:8000/api/paths \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Path", "vnum": 9999, "path_type": 1, "coordinates": [{"x": 0, "y": 0}, {"x": 1, "y": 1}]}'

# Try with API key (should succeed)
curl -X POST http://localhost:8000/api/paths \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key-here" \
  -d '{"name": "Test Path", "vnum": 9999, "path_type": 1, "coordinates": [{"x": 0, "y": 0}, {"x": 1, "y": 1}]}'
```

## Development Mode

For development environments, you can disable authentication:

```bash
# In your .env file
REQUIRE_AUTH=false
```

When disabled:
- All endpoints work without authentication
- The frontend won't prompt for an API key
- The `/api/auth/status` endpoint returns `{"authenticated": true, "message": "No authentication required"}`

## Troubleshooting

### Common Issues

1. **"API key not configured on server"**
   - Set the `WILDEDITOR_API_KEY` environment variable
   - Restart the backend server

2. **"Invalid API key"**
   - Check that your API key matches exactly
   - Ensure no extra spaces or characters

3. **Frontend shows authentication form repeatedly**
   - Clear browser localStorage
   - Check backend logs for authentication errors
   - Verify the API key is correct

### Backend Logs

Enable debug logging to see authentication attempts:

```bash
# In your .env file
DEBUG=true
LOG_LEVEL=DEBUG
```

### Clear Stored API Key

If you need to clear a stored API key:

```javascript
// In browser console
localStorage.removeItem('wildeditor_api_key')
```

## Security Best Practices

1. **Use Strong API Keys**: Generate random, 32+ character keys
2. **Keep Keys Secret**: Don't commit API keys to version control
3. **Rotate Keys**: Change API keys periodically
4. **Use HTTPS**: Always use HTTPS in production
5. **Monitor Access**: Check backend logs for unauthorized attempts

## Migration from Supabase

If you were previously using Supabase authentication:

1. The frontend will automatically switch to API key authentication
2. Remove any Supabase environment variables if desired
3. Update your deployment configuration with the new `WILDEDITOR_API_KEY`

Old Supabase auth hooks and components are preserved but inactive.
