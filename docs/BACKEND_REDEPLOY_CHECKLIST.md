# Backend Redeploy Checklist

When redeploying the backend server, ensure these environment variables are set:

## Required Environment Variables

1. **WILDEDITOR_API_KEY**: Set this to `0Hdn8wEggBM5KW42cAG0r3wVFDc4pYNu` (matches frontend)
2. **REQUIRE_AUTH**: Set to `true` for production authentication
3. **DB_HOST**: Database server hostname
4. **DB_USER**: Database username  
5. **DB_PASSWORD**: Database password
6. **DB_NAME**: Database name (luminari_muddev)
7. **CORS_ORIGINS**: Include the frontend URLs

## Authentication Flow

The backend expects:
- `Authorization: Bearer <API_KEY>` header for POST/PUT/DELETE operations
- GET operations don't require authentication
- The frontend has been updated to send the correct header format

## Endpoints That Should Work After Deploy

- ✅ `GET /api/health` - Health check
- ✅ `GET /api/regions` - List regions
- ✅ `POST /api/regions` - Create region (requires auth)
- ✅ `PUT /api/regions/{vnum}` - Update region (requires auth)
- ✅ `DELETE /api/regions/{vnum}` - Delete region (requires auth)

## Testing After Deploy

Test the API with:
```bash
# Health check
curl http://YOUR_SERVER:8000/api/health

# Create region (with auth)
curl -X POST http://YOUR_SERVER:8000/api/regions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 0Hdn8wEggBM5KW42cAG0r3wVFDc4pYNu" \
  -d '{
    "vnum": 9999,
    "zone_vnum": 1,
    "name": "Test Region",
    "region_type": 1,
    "coordinates": [
      {"x": 100, "y": 100},
      {"x": 200, "y": 100}, 
      {"x": 200, "y": 200},
      {"x": 100, "y": 200}
    ]
  }'
```

## Frontend Configuration

The frontend `.env` file should point to your deployed server:
```
VITE_API_URL=http://YOUR_SERVER:8000/api
VITE_WILDEDITOR_API_KEY=0Hdn8wEggBM5KW42cAG0r3wVFDc4pYNu
```
