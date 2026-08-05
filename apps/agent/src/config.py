"""Configuration management for Chat Agent Service"""
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8002
    debug: bool = False
    
    # AI Model Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    model_name: str = "gpt-5.6-sol"
    anthropic_model: str = "claude-fable-5"
    deepseek_model: str = "deepseek-chat"
    model_provider: str = "openai"  # openai, anthropic, or deepseek
    
    # MCP Server Configuration (Single Contact Surface)
    # In Docker, use service name; in dev, use localhost
    wilderness_mcp_url: str = Field(
        default="http://wildeditor-mcp:8001" if os.path.exists("/.dockerenv") else "http://localhost:8001"
    )
    mcp_api_key: Optional[str] = None
    
    # Note: Backend API is accessed only through MCP server now
    # This provides a single contact surface for the agent
    
    # Session Storage Configuration
    storage_backend: str = "memory"  # memory or redis
    redis_url: Optional[str] = "redis://localhost:6379"
    session_ttl: int = 86400  # 24 hours
    
    # CORS Configuration
    frontend_url: str = "http://localhost:5173"
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "https://wildedit.luminarimud.com"],
    )
    
    # Logging Configuration
    log_level: str = "INFO"


settings = Settings()
