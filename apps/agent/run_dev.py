#!/usr/bin/env python
"""Development server for Chat Agent"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

if __name__ == "__main__":
    # Set development environment variables if not already set
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("PORT", "8002")
    os.environ.setdefault("DEBUG", "true")
    os.environ.setdefault("LOG_LEVEL", "DEBUG")
    os.environ.setdefault("STORAGE_BACKEND", "memory")
    
    # Load .env file if it exists
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        print(f"Loading environment from {env_path}")
        load_dotenv(env_path)
    else:
        print("No .env file found, using defaults")
    
    # Check for required API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  Warning: No AI model API key configured!")
        print("Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file")
        print("Copy .env.example to .env and add your API key\n")
    
    # Import and run
    import uvicorn
    from src.config import settings
    
    print(f"\n🚀 Starting Chat Agent Service")
    print(f"   Port: {settings.port}")
    print(f"   Model: {settings.model_provider}/{settings.model_name}")
    print(f"   Storage: {settings.storage_backend}")
    print(f"   Debug: {settings.debug}")
    print(f"\n📍 Endpoints:")
    print(f"   Health: http://localhost:{settings.port}/health/")
    print(f"   API Docs: http://localhost:{settings.port}/docs")
    print(f"   Chat API: http://localhost:{settings.port}/api/chat/message")
    print(f"   Session API: http://localhost:{settings.port}/api/session/")
    print("\n")
    
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )