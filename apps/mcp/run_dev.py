"""
Development server runner for MCP server
"""

import uvicorn
import os
from pathlib import Path

def main():
    """Run the MCP server in development mode"""
    # Load environment file if it exists
    env_file = Path(__file__).parent / ".env.development"
    
    # Default environment for development
    os.environ.setdefault("WILDEDITOR_NODE_ENV", "development")
    os.environ.setdefault("WILDEDITOR_MCP_PORT", "8001")
    os.environ.setdefault("WILDEDITOR_LOG_LEVEL", "DEBUG")
    
    # Run with hot reload
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("WILDEDITOR_MCP_PORT", 8001)),
        reload=True,
        env_file=str(env_file) if env_file.exists() else None,
        log_level=os.environ.get("WILDEDITOR_LOG_LEVEL", "debug").lower()
    )

if __name__ == "__main__":
    main()
