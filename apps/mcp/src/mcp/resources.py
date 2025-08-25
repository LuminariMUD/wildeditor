"""
MCP Resources for Wildeditor

Resources provide static or dynamic data that AI agents can access
to understand the wilderness system structure and capabilities.
"""

from typing import Dict, Any, List
import httpx
import json

try:
    # Try relative import (when run as module)
    from ..config import settings
except ImportError:
    # Fall back to absolute import (when run directly)
    from config import settings


class ResourceRegistry:
    """Registry for MCP resources"""
    
    def __init__(self):
        self.resources = {}
        self._register_wilderness_resources()
    
    def register_resource(self, uri: str, func, name: str, description: str):
        """Register a resource"""
        self.resources[uri] = {
            "function": func,
            "name": name,
            "description": description
        }
    
    def get_resource(self, uri: str):
        """Get a resource by URI"""
        return self.resources.get(uri)
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all available resources"""
        return [
            {
                "uri": uri,
                "name": resource_info["name"],
                "description": resource_info["description"],
                "mimeType": "application/json"
            }
            for uri, resource_info in self.resources.items()
        ]
    
    def _register_wilderness_resources(self):
        """Register wilderness-specific resources"""
        
        # Terrain types reference
        self.register_resource(
            "wildeditor://terrain-types",
            self._get_terrain_types,
            "Terrain Types Reference",
            "Complete list of available terrain types and their characteristics"
        )
        
        # Environment types reference
        self.register_resource(
            "wildeditor://environment-types",
            self._get_environment_types,
            "Environment Types Reference",
            "Available environmental conditions and their effects"
        )
        
        # Region statistics
        self.register_resource(
            "wildeditor://region-stats",
            self._get_region_statistics,
            "Region Statistics",
            "Statistical overview of the wilderness system including counts and distributions"
        )
        
        # System schema
        self.register_resource(
            "wildeditor://schema",
            self._get_system_schema,
            "System Schema",
            "Database schema and data structure for regions and paths"
        )
        
        # Recent regions
        self.register_resource(
            "wildeditor://recent-regions",
            self._get_recent_regions,
            "Recently Modified Regions",
            "List of recently created or modified regions"
        )
        
        # System capabilities
        self.register_resource(
            "wildeditor://capabilities",
            self._get_system_capabilities,
            "System Capabilities",
            "Overview of what the Wildeditor system can do and its limitations"
        )
        
        # Wilderness map overview
        self.register_resource(
            "wildeditor://map-overview",
            self._get_map_overview,
            "Wilderness Map Overview",
            "High-level overview of the wilderness map structure and major areas"
        )
    
    async def _get_terrain_types(self) -> Dict[str, Any]:
        """Get terrain types reference"""
        # This would typically come from the backend API
        return {
            "terrain_types": [
                {
                    "name": "forest",
                    "description": "Dense woodland areas with trees and undergrowth",
                    "movement_difficulty": "medium",
                    "common_features": ["trees", "undergrowth", "wildlife"]
                },
                {
                    "name": "mountain",
                    "description": "High elevation rocky terrain",
                    "movement_difficulty": "hard",
                    "common_features": ["peaks", "cliffs", "snow", "caves"]
                },
                {
                    "name": "desert",
                    "description": "Arid landscape with sand and rock",
                    "movement_difficulty": "medium",
                    "common_features": ["sand", "rocks", "oases", "heat"]
                },
                {
                    "name": "swamp",
                    "description": "Wetland areas with standing water",
                    "movement_difficulty": "hard",
                    "common_features": ["water", "mud", "vegetation", "humidity"]
                },
                {
                    "name": "plains",
                    "description": "Open grassland areas",
                    "movement_difficulty": "easy",
                    "common_features": ["grass", "flowers", "open_sky"]
                },
                {
                    "name": "cave",
                    "description": "Underground caverns and tunnels",
                    "movement_difficulty": "medium",
                    "common_features": ["darkness", "stone", "echoes", "minerals"]
                },
                {
                    "name": "water",
                    "description": "Rivers, lakes, and other water bodies",
                    "movement_difficulty": "special",
                    "common_features": ["water", "currents", "fish", "reflection"]
                }
            ],
            "metadata": {
                "total_types": 7,
                "last_updated": "2025-08-15",
                "source": "Wildeditor System"
            }
        }
    
    async def _get_environment_types(self) -> Dict[str, Any]:
        """Get environment types reference"""
        return {
            "environment_types": [
                {
                    "name": "temperate",
                    "description": "Moderate climate with seasonal variation",
                    "temperature_range": "10-25°C",
                    "characteristics": ["seasonal_change", "moderate_rainfall"]
                },
                {
                    "name": "tropical",
                    "description": "Hot and humid with high rainfall",
                    "temperature_range": "20-35°C",
                    "characteristics": ["high_humidity", "heavy_rainfall", "lush_vegetation"]
                },
                {
                    "name": "arctic",
                    "description": "Very cold with snow and ice",
                    "temperature_range": "-20-5°C",
                    "characteristics": ["snow", "ice", "extreme_cold", "limited_vegetation"]
                },
                {
                    "name": "arid",
                    "description": "Hot and dry with little rainfall",
                    "temperature_range": "15-45°C",
                    "characteristics": ["low_rainfall", "high_evaporation", "sparse_vegetation"]
                },
                {
                    "name": "underground",
                    "description": "Cave and tunnel environments",
                    "temperature_range": "constant",
                    "characteristics": ["no_weather", "darkness", "echoes", "mineral_formations"]
                }
            ],
            "metadata": {
                "total_environments": 5,
                "last_updated": "2025-08-15",
                "source": "Wildeditor System"
            }
        }
    
    async def _get_region_statistics(self) -> Dict[str, Any]:
        """Get region statistics from backend"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"X-API-Key": settings.api_key}
                response = await client.get(
                    f"{settings.backend_base_url}/stats/regions",
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    # Return mock data if backend not available
                    return await self._get_mock_statistics()
                    
            except httpx.HTTPError:
                return await self._get_mock_statistics()
    
    async def _get_mock_statistics(self) -> Dict[str, Any]:
        """Return mock statistics when backend unavailable"""
        return {
            "statistics": {
                "total_regions": 0,
                "total_paths": 0,
                "terrain_distribution": {
                    "forest": 0,
                    "mountain": 0,
                    "desert": 0,
                    "plains": 0,
                    "swamp": 0,
                    "cave": 0,
                    "water": 0
                },
                "environment_distribution": {
                    "temperate": 0,
                    "tropical": 0,
                    "arctic": 0,
                    "arid": 0,
                    "underground": 0
                }
            },
            "metadata": {
                "last_updated": "2025-08-15",
                "source": "Mock Data - Backend Unavailable",
                "note": "Backend integration pending - showing sample structure"
            }
        }
    
    async def _get_system_schema(self) -> Dict[str, Any]:
        """Get system schema"""
        return {
            "schema": {
                "region": {
                    "fields": {
                        "id": {"type": "integer", "primary_key": True},
                        "name": {"type": "string", "required": True},
                        "description": {"type": "text", "required": True},
                        "terrain_type": {"type": "string", "required": True},
                        "environment": {"type": "string", "optional": True},
                        "coordinates": {
                            "type": "object",
                            "properties": {
                                "x": {"type": "integer"},
                                "y": {"type": "integer"}, 
                                "z": {"type": "integer"}
                            }
                        },
                        "created_at": {"type": "datetime"},
                        "updated_at": {"type": "datetime"}
                    }
                },
                "path": {
                    "fields": {
                        "id": {"type": "integer", "primary_key": True},
                        "from_region_id": {"type": "integer", "foreign_key": "region.id"},
                        "to_region_id": {"type": "integer", "foreign_key": "region.id"},
                        "direction": {"type": "string"},
                        "distance": {"type": "float"},
                        "difficulty": {"type": "string"},
                        "description": {"type": "text", "optional": True},
                        "created_at": {"type": "datetime"}
                    }
                }
            },
            "relationships": {
                "region_paths": {
                    "type": "one_to_many",
                    "description": "A region can have multiple outgoing paths"
                },
                "bidirectional_paths": {
                    "type": "optional",
                    "description": "Paths can be bidirectional or unidirectional"
                }
            },
            "constraints": {
                "terrain_types": ["forest", "mountain", "desert", "swamp", "plains", "cave", "water"],
                "environment_types": ["temperate", "tropical", "arctic", "arid", "underground"],
                "directions": ["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest", "up", "down"],
                "difficulty_levels": ["easy", "medium", "hard", "extreme"]
            }
        }
    
    async def _get_recent_regions(self) -> Dict[str, Any]:
        """Get recently modified regions"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"X-API-Key": settings.api_key}
                response = await client.get(
                    f"{settings.backend_base_url}/regions/recent",
                    params={"limit": 10},
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"recent_regions": [], "note": "Backend unavailable"}
                    
            except httpx.HTTPError:
                return {"recent_regions": [], "note": "Backend unavailable"}
    
    async def _get_system_capabilities(self) -> Dict[str, Any]:
        """Get system capabilities"""
        return {
            "capabilities": {
                "region_management": {
                    "create": True,
                    "read": True,
                    "update": True,
                    "delete": True,
                    "search": True,
                    "bulk_operations": False
                },
                "path_management": {
                    "create": True,
                    "read": True,
                    "update": True,
                    "delete": True,
                    "pathfinding": True,
                    "validation": True
                },
                "analysis": {
                    "terrain_analysis": True,
                    "connectivity_analysis": True,
                    "statistics": True,
                    "visualization": False
                },
                "ai_features": {
                    "natural_language_creation": True,
                    "intelligent_suggestions": True,
                    "automated_validation": True,
                    "content_generation": True
                }
            },
            "limitations": {
                "max_regions": "unlimited",
                "max_paths_per_region": 20,
                "description_length": 2000,
                "name_length": 100,
                "concurrent_operations": 10
            },
            "version": "1.0.0",
            "last_updated": "2025-08-15"
        }
    
    async def _get_map_overview(self) -> Dict[str, Any]:
        """Get wilderness map overview"""
        async with httpx.AsyncClient() as client:
            try:
                headers = {"X-API-Key": settings.api_key}
                response = await client.get(
                    f"{settings.backend_base_url}/map/overview",
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return await self._get_mock_map_overview()
                    
            except httpx.HTTPError:
                return await self._get_mock_map_overview()
    
    async def _get_mock_map_overview(self) -> Dict[str, Any]:
        """Return mock map overview"""
        return {
            "map_overview": {
                "total_area": "undefined",
                "coordinate_system": "3D (x, y, z)",
                "major_areas": [],
                "notable_features": [],
                "connection_hubs": []
            },
            "metadata": {
                "status": "empty",
                "note": "Wilderness map is currently empty - ready for content creation"
            }
        }
