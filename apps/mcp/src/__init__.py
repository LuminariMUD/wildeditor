"""
Wildeditor MCP Server

Model Context Protocol server providing AI-powered tools for wilderness
region and path management in the Wildeditor backend system.
"""

from .main import app
from .config import settings

__version__ = "1.0.0"
__all__ = ["app", "settings"] 
