"""Configuration management for Chat Agent Service"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8002, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # AI Model Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    deepseek_api_key: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    model_name: str = Field(default="gpt-4-turbo", env="MODEL_NAME")
    deepseek_model: str = Field(default="deepseek-chat", env="DEEPSEEK_MODEL")
    model_provider: str = Field(default="openai", env="MODEL_PROVIDER")  # openai, anthropic, or deepseek
    
    # MCP Server Configuration (Single Contact Surface)
    # In Docker, use service name; in dev, use localhost
    wilderness_mcp_url: str = Field(
        default="http://wildeditor-mcp:8001" if os.path.exists("/.dockerenv") else "http://localhost:8001", 
        env="WILDERNESS_MCP_URL"
    )
    mcp_api_key: Optional[str] = Field(default=None, env="MCP_API_KEY")
    
    # Note: Backend API is accessed only through MCP server now
    # This provides a single contact surface for the agent
    
    # Session Storage Configuration
    storage_backend: str = Field(default="memory", env="STORAGE_BACKEND")  # memory or redis
    redis_url: Optional[str] = Field(default="redis://localhost:6379", env="REDIS_URL")
    session_ttl: int = Field(default=86400, env="SESSION_TTL")  # 24 hours
    
    # CORS Configuration
    frontend_url: str = Field(default="http://localhost:5173", env="FRONTEND_URL")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "https://wildedit.luminarimud.com"],
        env="CORS_ORIGINS"
    )
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()