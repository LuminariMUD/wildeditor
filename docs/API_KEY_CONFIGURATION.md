# API Key Configuration

The Wildeditor frontend requires an API key to perform destructive operations (POST, PUT, DELETE) on the wilderness data. This prevents unauthorized modifications to the database.

## Environment Variable

Set the following environment variable:

```bash
VITE_WILDEDITOR_API_KEY=your_actual_api_key_here
```

## Development Setup

For local development, add the API key to your `.env` file:

```bash
# Copy from .env.example and add:
VITE_WILDEDITOR_API_KEY=dev-key-for-testing
```

## Production Deployment

### Netlify Deployment

1. In your Netlify site dashboard, go to **Site Settings** → **Environment Variables**
2. Add a new variable:
   - **Key**: `VITE_WILDEDITOR_API_KEY`
   - **Value**: The production API key (from GitHub Actions variable `WILDEDITOR_API_KEY`) 

### GitHub Actions Variable

The production API key should be stored as a GitHub Actions variable named `WILDEDITOR_API_KEY`. This variable should be configured in your repository settings under **Settings** → **Secrets and Variables** → **Actions**.

## API Operations Requiring Key

The following operations require the API key:

- **POST /api/regions** - Create new regions
- **PUT /api/regions/{id}** - Update existing regions  
- **DELETE /api/regions/{id}** - Delete regions
- **POST /api/paths** - Create new paths
- **PUT /api/paths/{id}** - Update existing paths
- **DELETE /api/paths/{id}** - Delete paths
- **POST /api/points** - Create new points
- **PUT /api/points/{id}** - Update existing points
- **DELETE /api/points/{id}** - Delete points

Read operations (GET requests) do not require the API key.

## Error Handling

If the API key is missing or invalid, you'll receive:

- **401 Unauthorized**: API key is missing or invalid
- **403 Forbidden**: API key doesn't have permission for this operation

The frontend will display user-friendly error messages for these scenarios.

## Security Notes

- The API key is built into the frontend bundle and is visible to users
- This approach protects against casual tampering but not determined attackers
- The key primarily prevents accidental modifications and basic unauthorized access
- For higher security requirements, consider implementing user-based permissions on the backend
