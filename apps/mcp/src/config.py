"""
Configuration settings for the MCP server
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """MCP Server configuration settings"""
    
    # Server settings
    node_env: str = "development"
    mcp_port: int = 8001
    host: str = "0.0.0.0"
    
    # Authentication - Two-key system
    api_key: str = ""  # Backend API access (shared with backend)
    mcp_key: str = ""  # MCP operations (for AI agents)
    
    # External services
    backend_url: str = "http://localhost:8000"
    backend_api_base: str = "/api"
    
    # CORS settings
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_prefix = "WILDEDITOR_"
        
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.node_env.lower() == "development"
    
    @property
    def backend_base_url(self) -> str:
        """Get full backend base URL"""
        return f"{self.backend_url}{self.backend_api_base}"
    
    @property
    def cors_origin_list(self) -> list[str]:
        """Get CORS origins as list"""
        if not self.cors_origins:
            return []
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
