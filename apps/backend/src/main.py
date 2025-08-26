from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging
from .routers.regions import router as regions_router
from .routers.paths import router as paths_router
from .routers.points import router as points_router
from .routers.terrain import router as terrain_router
from .routers.wilderness import router as wilderness_router
from .routers.region_hints import router as region_hints_router
from .routers.mcp_proxy import router as mcp_proxy_router
from .middleware.auth import verify_api_key
from .services.terrain_bridge import is_terrain_bridge_available
import os

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Wildeditor Backend API",
    description="Backend API for the Luminari Wilderness Editor",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Get CORS origins from environment variable or use defaults
# CORS configuration
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,https://wildedit.luminarimud.com,https://wildeditor.luminari.com"
).split(",")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(regions_router, prefix="/api/regions", tags=["Regions"])
app.include_router(paths_router, prefix="/api/paths", tags=["Paths"])
app.include_router(points_router, prefix="/api/points", tags=["Points"])
app.include_router(terrain_router, prefix="/api/terrain", tags=["Terrain"])
app.include_router(wilderness_router, prefix="/api/wilderness", tags=["Wilderness"])

# Include region hints router - nested under regions
app.include_router(region_hints_router, prefix="/api/regions", tags=["Region Hints"])

# Include MCP proxy router for AI services
app.include_router(mcp_proxy_router, prefix="/api/mcp", tags=["MCP Proxy"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    terrain_available = await is_terrain_bridge_available()
    
    return {
        "status": "healthy", 
        "service": "wildeditor-backend",
        "version": "1.0.0",
        "terrain_bridge_available": terrain_available
    }


@app.get("/api/auth/status")
def auth_status(authenticated: bool = Depends(verify_api_key)):
    """Check authentication status"""
    return {
        "authenticated": authenticated,
        "message": "Authentication successful" if authenticated else "No authentication required"
    }

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Wildeditor Backend API",
        "docs_url": "/docs",
        "health_url": "/api/health"
    }

# Add validation error handler for better debugging
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log validation errors for debugging"""
    logger.error(f"Validation error for {request.url.path}")
    logger.error(f"Request body: {await request.body()}")
    logger.error(f"Validation errors: {exc.errors()}")
    
    # Return detailed error for debugging
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": str(exc.body) if hasattr(exc, 'body') else None
        }
    )
