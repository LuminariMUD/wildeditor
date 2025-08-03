# Frontend API Migration - Luminari Wilderness Editor

## Overview

This document describes the changes made to migrate the frontend from Supabase authentication to work with the new Python FastAPI backend that operates in development mode without authentication.

## Changes Made

### 1. Authentication Bypass

**Problem**: Frontend expected JWT authentication but backend operates without auth in development mode.

**Solution**: 
- Updated `useEditor` hook to check `VITE_DISABLE_AUTH` environment variable
- Modified API calls to work with or without authentication tokens
- Maintained backward compatibility for when authentication is enabled

**Files Changed**:
- `apps/frontend/src/hooks/useEditor.ts`
- `apps/frontend/src/services/api.ts`

### 2. API Data Structure Alignment

**Problem**: Frontend expected different field names and structure than the FastAPI backend provides.

**Solution**: 
- Updated shared types to match the actual API structure
- Added conversion functions between API format and frontend format
- Maintained backward compatibility with optional legacy fields

**API Structure Changes**:

#### Regions
- Primary key: `vnum` (integer) instead of `id` (UUID)
- Field names: `region_type` instead of `type`
- Props: `region_props` (number) instead of `props` (JSON string)
- Additional fields: `region_reset_data`, `region_reset_time`, `region_type_name`, `sector_type_name`

#### Paths  
- Primary key: `vnum` (integer) instead of `id` (UUID)
- Field names: `path_type` instead of `type`
- Props: `path_props` (number) instead of `props` (JSON string)
- Additional fields: `path_type_name`

#### Points
- Simplified structure (no vnum yet in API)
- Direct coordinate instead of nested structure

**Files Changed**:
- `packages/shared/src/types/index.ts`
- `apps/frontend/src/services/api.ts`

### 3. API Response Handling

**Problem**: Backend wraps collection responses in `{data: [...]}` but single items are direct objects.

**Solution**:
- Updated API client to handle both response formats
- Added proper error handling for FastAPI error format
- Improved error messages and debugging

**Files Changed**:
- `apps/frontend/src/services/api.ts`

### 4. Data Conversion Functions

Added helper functions to convert between API format and frontend format:

```typescript
// Convert API regions to frontend format (adds compatibility fields)
const apiRegionToFrontend = (apiRegion: any): Region => ({ ... })

// Convert frontend regions to API format (removes frontend-only fields)  
const frontendRegionToApi = (region: Omit<Region, 'id'>): any => ({ ... })
```

### 5. Environment Configuration

The frontend now respects the `VITE_DISABLE_AUTH=true` setting to bypass authentication entirely:

```env
# apps/frontend/.env
VITE_API_URL=http://localhost:8000/api
VITE_DISABLE_AUTH=true
```

## API Compatibility

### Current Backend Endpoints

The frontend now correctly calls these FastAPI endpoints:

- `GET /api/health` - Health check
- `GET /api/regions` - List all regions  
- `GET /api/regions/{vnum}` - Get specific region
- `POST /api/regions` - Create new region
- `PUT /api/regions/{vnum}` - Update region
- `DELETE /api/regions/{vnum}` - Delete region
- `GET /api/paths` - List all paths
- `GET /api/paths/{vnum}` - Get specific path  
- `POST /api/paths` - Create new path
- `PUT /api/paths/{vnum}` - Update path
- `DELETE /api/paths/{vnum}` - Delete path

### Response Format

**Collections**: Wrapped in `{data: [...]}`
```json
{
  "data": [
    {
      "vnum": 101,
      "name": "Darkwood Forest",
      "region_type": 1,
      "coordinates": [...]
    }
  ]
}
```

**Single Items**: Direct objects
```json
{
  "vnum": 101,
  "name": "Darkwood Forest", 
  "region_type": 1,
  "coordinates": [...]
}
```

## Testing

After these changes, the frontend should:

1. ✅ Load without authentication errors
2. ✅ Connect to the FastAPI backend at `http://localhost:8000/api`  
3. ✅ Fetch and display existing regions and paths
4. ✅ Allow creating new regions and paths
5. ✅ Allow editing existing items
6. ✅ Handle API errors gracefully

## Next Steps

1. **Test with Real Data**: Verify the frontend works with actual MUD database content
2. **Error Handling**: Improve error messages and user feedback
3. **Authentication**: When ready for production, implement API key authentication
4. **Points API**: Complete the Points endpoints in the backend
5. **Type Safety**: Consider using generated types from OpenAPI schema

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure backend allows `http://localhost:5173` in CORS settings
2. **API Connection**: Verify backend is running on port 8000
3. **Data Format**: Check browser network tab for API response format mismatches
4. **Authentication**: Ensure `VITE_DISABLE_AUTH=true` is set correctly

### Debug Mode

Enable debug logging:
```env
VITE_ENABLE_DEBUG=true
```

This will show detailed API calls and responses in the browser console.
