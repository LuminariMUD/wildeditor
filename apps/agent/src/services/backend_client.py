"""Backend API client for region and hint operations"""
import httpx
from typing import Optional, Dict, Any, List
import logging
from config import settings

logger = logging.getLogger(__name__)


class BackendClient:
    """Client for interacting with the Wilderness Editor backend API"""
    
    def __init__(self):
        self.base_url = settings.backend_api_url
        self.api_key = settings.backend_api_key
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        logger.info(f"Initialized BackendClient with base URL: {self.base_url}")
    
    async def create_region(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new region"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/regions/",
                json=data,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def update_region(self, region_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing region"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/api/regions/{region_id}",
                json=data,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def delete_region(self, region_id: int) -> bool:
        """Delete a region"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/api/regions/{region_id}",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return True
    
    async def get_regions(
        self, 
        limit: int = 100,
        offset: int = 0,
        type_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get list of regions with optional filtering"""
        params = {"limit": limit, "offset": offset}
        if type_filter:
            params["type"] = type_filter
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/regions",
                params=params,
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_region(self, region_id: int) -> Dict[str, Any]:
        """Get a specific region by ID"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/regions/{region_id}",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def generate_hints(self, vnum: int, description: str, style: str = "dynamic") -> Dict[str, Any]:
        """Generate hints for a region from its description"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/regions/{vnum}/hints/generate",
                json={
                    "description": description,
                    "style": style
                },
                headers=self.headers,
                timeout=60.0  # Longer timeout for AI generation
            )
            response.raise_for_status()
            return response.json()
    
    async def create_hints(self, vnum: int, hints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create hints for a region"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/regions/{vnum}/hints",
                json={"hints": hints},
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_hints(self, vnum: int) -> List[Dict[str, Any]]:
        """Get hints for a region"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/regions/{vnum}/hints",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            return result.get("hints", [])