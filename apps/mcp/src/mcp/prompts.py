"""
MCP Prompts for Wildeditor

Prompts provide templates and guidance for AI agents to generate
high-quality wilderness content and perform complex operations.
"""

from typing import Dict, Any, List


class PromptRegistry:
    """Registry for MCP prompts"""
    
    def __init__(self):
        self.prompts = {}
        self._register_wilderness_prompts()
    
    def register_prompt(self, name: str, func, description: str, arguments: List[Dict[str, Any]]):
        """Register a prompt"""
        self.prompts[name] = {
            "function": func,
            "description": description,
            "arguments": arguments
        }
    
    def get_prompt(self, name: str):
        """Get a prompt by name"""
        return self.prompts.get(name)
    
    def list_prompts(self) -> List[Dict[str, Any]]:
        """List all available prompts"""
        return [
            {
                "name": name,
                "description": prompt_info["description"],
                "arguments": prompt_info["arguments"]
            }
            for name, prompt_info in self.prompts.items()
        ]
    
    def _register_wilderness_prompts(self):
        """Register wilderness-specific prompts"""
        
        # Region creation prompt
        self.register_prompt(
            "create_region",
            self._create_region_prompt,
            "Generate a detailed wilderness region with rich descriptions and appropriate characteristics",
            [
                {
                    "name": "terrain_type",
                    "description": "The primary terrain type (forest, mountain, desert, etc.)",
                    "required": True
                },
                {
                    "name": "environment",
                    "description": "Environmental conditions (temperate, tropical, arctic, etc.)",
                    "required": False
                },
                {
                    "name": "theme",
                    "description": "Optional theme or mood (mysterious, dangerous, peaceful, etc.)",
                    "required": False
                },
                {
                    "name": "size",
                    "description": "Relative size of the area (small, medium, large)",
                    "required": False
                }
            ]
        )
        
        # Region connection prompt
        self.register_prompt(
            "connect_regions",
            self._connect_regions_prompt,
            "Generate logical connections and paths between wilderness regions",
            [
                {
                    "name": "region1_terrain",
                    "description": "Terrain type of the first region",
                    "required": True
                },
                {
                    "name": "region2_terrain", 
                    "description": "Terrain type of the second region",
                    "required": True
                },
                {
                    "name": "transition_style",
                    "description": "How the regions should transition (gradual, abrupt, etc.)",
                    "required": False
                }
            ]
        )
        
        # Wilderness area design prompt
        self.register_prompt(
            "design_area",
            self._design_area_prompt,
            "Design a cohesive wilderness area with multiple connected regions",
            [
                {
                    "name": "area_theme",
                    "description": "Overall theme for the wilderness area",
                    "required": True
                },
                {
                    "name": "size",
                    "description": "Number of regions to include (3-20)",
                    "required": True
                },
                {
                    "name": "difficulty",
                    "description": "Overall difficulty level (easy, medium, hard)",
                    "required": False
                },
                {
                    "name": "special_features",
                    "description": "Any special features or landmarks to include",
                    "required": False
                }
            ]
        )
        
        # Region analysis prompt
        self.register_prompt(
            "analyze_region",
            self._analyze_region_prompt,
            "Analyze an existing region and provide insights or suggestions for improvement",
            [
                {
                    "name": "region_data",
                    "description": "JSON data of the region to analyze",
                    "required": True
                },
                {
                    "name": "analysis_focus",
                    "description": "What to focus on (description, connections, realism, etc.)",
                    "required": False
                }
            ]
        )
        
        # Path description prompt
        self.register_prompt(
            "describe_path",
            self._describe_path_prompt,
            "Generate detailed descriptions for paths between regions",
            [
                {
                    "name": "from_terrain",
                    "description": "Terrain type of starting region",
                    "required": True
                },
                {
                    "name": "to_terrain",
                    "description": "Terrain type of destination region",
                    "required": True
                },
                {
                    "name": "direction",
                    "description": "Direction of travel (north, south, east, west, etc.)",
                    "required": True
                },
                {
                    "name": "difficulty",
                    "description": "Path difficulty (easy, medium, hard)",
                    "required": False
                },
                {
                    "name": "distance",
                    "description": "Relative distance (short, medium, long)",
                    "required": False
                }
            ]
        )
    
    async def _create_region_prompt(self, terrain_type: str, environment: str = None, 
                                  theme: str = None, size: str = "medium") -> Dict[str, Any]:
        """Generate region creation prompt"""
        
        base_prompt = f"""Create a detailed wilderness region with the following specifications:

**Core Requirements:**
- Terrain Type: {terrain_type}
- Environment: {environment or 'temperate'}
- Size: {size}
{f'- Theme: {theme}' if theme else ''}

**Instructions:**
1. Generate a evocative name that reflects the terrain and character
2. Write a rich, immersive description (100-300 words) that includes:
   - Visual details of the landscape
   - Atmospheric elements (sounds, smells, lighting)
   - Notable features or landmarks
   - Environmental conditions
   - Sense of scale and space

3. Consider how this region fits into a larger wilderness ecosystem
4. Include subtle hints about potential connections to other areas
5. Make the description vivid enough for players to visualize

**Style Guidelines:**
- Use present tense, second person ("You see...")
- Include sensory details beyond just visual
- Create a sense of place and atmosphere
- Avoid overly dramatic or cliché descriptions
- Focus on natural, believable features"""

        terrain_specific = self._get_terrain_specific_guidance(terrain_type)
        environment_specific = self._get_environment_specific_guidance(environment or 'temperate')
        
        return {
            "description": f"Generate a detailed {terrain_type} region",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert wilderness designer creating immersive natural environments for a fantasy world. Focus on realistic, detailed descriptions that help players feel present in the environment."
                },
                {
                    "role": "user", 
                    "content": base_prompt + "\n\n" + terrain_specific + "\n\n" + environment_specific
                }
            ]
        }
    
    async def _connect_regions_prompt(self, region1_terrain: str, region2_terrain: str,
                                    transition_style: str = "gradual") -> Dict[str, Any]:
        """Generate region connection prompt"""
        
        prompt = f"""Design logical paths and transitions between two wilderness regions:

**Region Connection Task:**
- From: {region1_terrain} terrain
- To: {region2_terrain} terrain  
- Transition Style: {transition_style}

**Create:**
1. **Path Description**: How travelers move between these regions
2. **Transition Zone**: How the terrain and environment change
3. **Logical Connections**: Why these regions exist near each other
4. **Travel Details**: 
   - Direction and distance
   - Difficulty level
   - Notable landmarks along the way
   - Potential hazards or points of interest

**Consider:**
- Geographic realism (how terrains naturally connect)
- Elevation changes if applicable
- Weather/climate transitions
- Flora and fauna changes
- Logical placement in a larger landscape

**Output Format:**
Provide both the mechanical details (direction, distance, difficulty) and rich descriptive text for the path itself."""

        return {
            "description": f"Connect {region1_terrain} and {region2_terrain} regions",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a geographic expert designing realistic transitions between different terrain types. Focus on how landscapes naturally connect and change."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
    
    async def _design_area_prompt(self, area_theme: str, size: int, 
                                difficulty: str = "medium", special_features: str = None) -> Dict[str, Any]:
        """Generate area design prompt"""
        
        prompt = f"""Design a cohesive wilderness area with multiple connected regions:

**Area Specifications:**
- Theme: {area_theme}
- Number of Regions: {size}
- Difficulty Level: {difficulty}
{f'- Special Features: {special_features}' if special_features else ''}

**Design Requirements:**
1. **Overall Layout**: Logical geographic arrangement
2. **Region Variety**: Mix of terrain types that fit the theme
3. **Connectivity**: Clear path network between regions
4. **Progression**: Logical flow and difficulty curve
5. **Focal Points**: Central or notable areas that anchor the design

**For Each Region:**
- Terrain type and environment
- Brief description and name
- Role in the overall area
- Connections to other regions

**Area Characteristics:**
- Central theme that unifies all regions
- Natural geographic boundaries
- Internal logic and consistency
- Potential for exploration and discovery

**Consider:**
- How different terrain types support the theme
- Natural barriers and connectors
- Points of interest and landmarks
- Overall navigability and flow"""

        return {
            "description": f"Design {area_theme} wilderness area with {size} regions",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a master wilderness architect creating large-scale natural environments. Design cohesive areas that feel like real, connected ecosystems."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
    
    async def _analyze_region_prompt(self, region_data: str, analysis_focus: str = "overall") -> Dict[str, Any]:
        """Generate region analysis prompt"""
        
        prompt = f"""Analyze the following wilderness region and provide detailed feedback:

**Region Data:**
{region_data}

**Analysis Focus:** {analysis_focus}

**Provide Analysis On:**
1. **Description Quality**: 
   - Clarity and immersion
   - Sensory details and atmosphere
   - Consistency with terrain type
   
2. **Geographic Logic**:
   - Realistic terrain features
   - Environmental consistency
   - Scale and proportions
   
3. **Connectivity**:
   - Exit placement and logic
   - Integration with surrounding areas
   - Navigation clarity
   
4. **Improvement Suggestions**:
   - Specific enhancements to description
   - Additional features or details
   - Better integration opportunities
   
5. **Strengths**:
   - What works well
   - Unique or memorable elements
   - Effective atmospheric details

**Format:**
Provide both summary assessment and specific, actionable suggestions for improvement."""

        return {
            "description": f"Analyze wilderness region focusing on {analysis_focus}",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert wilderness consultant reviewing region designs for quality, realism, and player experience. Provide constructive, specific feedback."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
    
    async def _describe_path_prompt(self, from_terrain: str, to_terrain: str, direction: str,
                                  difficulty: str = "medium", distance: str = "medium") -> Dict[str, Any]:
        """Generate path description prompt"""
        
        prompt = f"""Create a detailed description for a wilderness path:

**Path Specifications:**
- From: {from_terrain} terrain
- To: {to_terrain} terrain
- Direction: {direction}
- Difficulty: {difficulty}
- Distance: {distance}

**Description Requirements:**
1. **Journey Description**: What travelers experience along this path
2. **Terrain Transition**: How the landscape changes from start to end
3. **Landmarks**: Notable features along the way
4. **Challenges**: Obstacles or difficulties appropriate to the difficulty level
5. **Atmosphere**: Mood and sensory details of the journey

**Consider:**
- Realistic terrain transitions
- Weather and environmental factors
- Flora and fauna changes
- Elevation changes if applicable
- Time of day effects
- Seasonal variations

**Style:**
- Present tense, immersive description
- Focus on the traveler's experience
- Include multiple senses
- Build appropriate tension for difficulty level
- 50-150 words for concise but evocative description"""

        return {
            "description": f"Describe {difficulty} path from {from_terrain} to {to_terrain} going {direction}",
            "messages": [
                {
                    "role": "system",
                    "content": "You are creating travel descriptions for wilderness paths. Focus on the journey experience and realistic terrain transitions."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
    
    def _get_terrain_specific_guidance(self, terrain_type: str) -> str:
        """Get terrain-specific guidance"""
        guidance = {
            "forest": """
**Forest-Specific Elements:**
- Tree types and density variations
- Undergrowth and ground cover
- Light filtering through canopy
- Forest sounds (rustling, wildlife)
- Clearings, groves, or thickets
- Fallen logs, moss, forest floor details""",
            
            "mountain": """
**Mountain-Specific Elements:**
- Rock types and formations
- Elevation and steepness
- Views and vistas
- Weather effects (wind, temperature)
- Vegetation changes with altitude
- Geological features (cliffs, caves, peaks)""",
            
            "desert": """
**Desert-Specific Elements:**
- Sand, rock, or mixed terrain
- Heat effects and mirages
- Sparse vegetation types
- Day/night temperature contrasts
- Wind patterns and erosion features
- Oases or water sources""",
            
            "swamp": """
**Swamp-Specific Elements:**
- Water depth and movement
- Vegetation (cypresses, moss, reeds)
- Humidity and moisture effects
- Wildlife sounds and presence
- Muddy ground and firm areas
- Mist and atmospheric effects""",
            
            "plains": """
**Plains-Specific Elements:**
- Grass types and height
- Rolling hills or flat expanse
- Weather visibility (storms, clear skies)
- Wildlife grazing or movement
- Scattered trees or rock formations
- Horizon views and openness""",
            
            "cave": """
**Cave-Specific Elements:**
- Rock formations and textures
- Light sources and darkness
- Echo and sound effects
- Temperature and humidity
- Mineral formations (stalactites, crystals)
- Underground water features""",
            
            "water": """
**Water-Specific Elements:**
- Water clarity and color
- Current strength and direction
- Shoreline characteristics
- Aquatic life visibility
- Reflection and light effects
- Depth indicators and safety"""
        }
        
        return guidance.get(terrain_type, "**General Terrain**: Focus on distinctive features of this terrain type.")
    
    def _get_environment_specific_guidance(self, environment: str) -> str:
        """Get environment-specific guidance"""
        guidance = {
            "temperate": """
**Temperate Climate Effects:**
- Moderate temperatures and seasonal hints
- Balanced humidity and comfortable conditions
- Mixed vegetation appropriate to season
- Pleasant weather with occasional changes""",
            
            "tropical": """
**Tropical Climate Effects:**
- High humidity and warmth
- Lush, dense vegetation
- Frequent rain or recent rainfall evidence
- Rich biodiversity and vibrant colors""",
            
            "arctic": """
**Arctic Climate Effects:**
- Cold temperatures and wind chill
- Snow, ice, or frost presence
- Limited vegetation adapted to cold
- Clear, crisp air and stark beauty""",
            
            "arid": """
**Arid Climate Effects:**
- Dry air and intense heat
- Water-conserving vegetation
- Sun glare and heat shimmer
- Dust and wind-carved features""",
            
            "underground": """
**Underground Environment:**
- Constant temperature
- No weather effects
- Artificial or minimal lighting
- Echo and enclosed atmosphere"""
        }
        
        return guidance.get(environment, "**Climate Neutral**: Focus on terrain rather than specific climate effects.")
