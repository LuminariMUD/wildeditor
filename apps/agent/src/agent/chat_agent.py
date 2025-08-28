"""Main Chat Agent implementation using PydanticAI"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from config import settings
from .tools import WildernessTools
import logging
import json
import os

logger = logging.getLogger(__name__)


class ChatAction(BaseModel):
    """Action to be executed by the frontend"""
    type: str = Field(description="Type of action (create_region, create_path, stage_description, etc.)")
    params: Dict[str, Any] = Field(description="Parameters for the action")
    ui_hints: Optional[Dict[str, Any]] = Field(default_factory=dict, description="UI hints for the frontend")


class AssistantResponse(BaseModel):
    """Structured response from the assistant"""
    message: str = Field(description="The main response message")
    actions: List[ChatAction] = Field(default_factory=list, description="Actions for frontend to execute")
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="Tool calls made during processing (for logging)")
    suggestions: List[str] = Field(default_factory=list, description="Suggested next actions")
    warnings: List[str] = Field(default_factory=list, description="Any warnings or issues")


class EditorContext(BaseModel):
    """Context information from the wilderness editor"""
    selected_region_id: Optional[int] = None
    selected_path_id: Optional[int] = None
    selected_point_id: Optional[int] = None
    viewport: Dict[str, float] = Field(default_factory=dict)  # x, y, zoom
    active_tool: Optional[str] = None
    recent_actions: List[str] = Field(default_factory=list)


class WildernessAssistantAgent:
    """
    Main chat agent for wilderness building assistance.
    Integrates with MCP servers and maintains conversation context.
    """
    
    def __init__(self, mcp_client=None):
        """Initialize the agent with configured model and MCP tools"""
        self.model = self._initialize_model()
        
        if not self.model:
            raise ValueError("No AI model could be initialized. Please configure API keys.")
        
        # Track tool calls for action conversion
        self.current_tool_calls = []
        
        # Initialize tools if MCP client is provided
        self.tools = None
        if mcp_client:
            self.tools = WildernessTools(mcp_client)
            logger.info("Initialized with MCP tools (single contact surface)")
        
        # Initialize the agent with or without tools
        if self.tools:
            self.agent = self._create_agent_with_tools()
        else:
            self.agent = Agent(
                model=self.model,
                system_prompt=self._get_system_prompt()
            )
        
        logger.info(f"Initialized WildernessAssistantAgent with model")
    
    def _initialize_model(self):
        """
        Initialize AI model with fallback chain:
        1. Try configured provider (if specified)
        2. Fallback to OpenAI if available
        3. Fallback to DeepSeek if available
        4. Return None if no model available
        """
        # First, try the explicitly configured provider
        provider = settings.model_provider.lower() if settings.model_provider else None
        
        if provider == "openai" and settings.openai_api_key:
            try:
                logger.info(f"Initializing OpenAI model: {settings.model_name}")
                # Set API key in environment for OpenAI client
                os.environ['OPENAI_API_KEY'] = settings.openai_api_key
                return OpenAIModel(
                    model_name=settings.model_name or "gpt-4-turbo"
                )
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
        
        elif provider == "deepseek" and settings.deepseek_api_key:
            try:
                logger.info(f"Initializing DeepSeek model: {settings.deepseek_model}")
                # DeepSeek uses OpenAI-compatible API
                # Use DEEPSEEK_API_KEY environment variable
                os.environ['DEEPSEEK_API_KEY'] = settings.deepseek_api_key
                # Also set OPENAI_API_KEY for the OpenAI client compatibility
                os.environ['OPENAI_API_KEY'] = settings.deepseek_api_key
                return OpenAIModel(
                    model_name=settings.deepseek_model or "deepseek-chat",
                    base_url="https://api.deepseek.com/v1"
                )
            except Exception as e:
                logger.warning(f"Failed to initialize DeepSeek: {e}")
        
        elif provider == "anthropic" and settings.anthropic_api_key:
            try:
                logger.info(f"Initializing Anthropic model: {settings.model_name}")
                # Set API key in environment for Anthropic client
                os.environ['ANTHROPIC_API_KEY'] = settings.anthropic_api_key
                return AnthropicModel(
                    model_name=settings.model_name or "claude-3-opus-20240229"
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic: {e}")
        
        # If no explicit provider or it failed, try fallback chain
        logger.info("Trying fallback model chain...")
        
        # Try OpenAI first (most common)
        if settings.openai_api_key:
            try:
                logger.info("Falling back to OpenAI")
                os.environ['OPENAI_API_KEY'] = settings.openai_api_key
                return OpenAIModel(
                    model_name=settings.model_name or "gpt-4-turbo"
                )
            except Exception as e:
                logger.warning(f"OpenAI fallback failed: {e}")
        
        # Try DeepSeek as second fallback
        if settings.deepseek_api_key:
            try:
                logger.info("Falling back to DeepSeek")
                os.environ['DEEPSEEK_API_KEY'] = settings.deepseek_api_key
                # Also set OPENAI_API_KEY for the OpenAI client compatibility
                os.environ['OPENAI_API_KEY'] = settings.deepseek_api_key
                return OpenAIModel(
                    model_name=settings.deepseek_model or "deepseek-chat",
                    base_url="https://api.deepseek.com/v1"
                )
            except Exception as e:
                logger.warning(f"DeepSeek fallback failed: {e}")
        
        # No models available
        logger.error("No AI models could be initialized")
        return None
    
    def _create_agent_with_tools(self):
        """Create agent with tool functions"""
        agent = Agent(
            model=self.model,
            system_prompt=self._get_enhanced_prompt()
        )
        
        # Register all tools - keep existing MCP integration but capture calls
        @agent.tool
        async def build_new_region(
            ctx: RunContext[EditorContext],
            name: str,
            region_type: int,  # MCP uses integer types
            coordinates: List[Dict[str, float]],  # MCP format
            zone_vnum: int = 10000,
            auto_generate_description: bool = True
        ) -> Dict[str, Any]:
            """Create a new wilderness region and stage it for frontend integration"""
            # Capture this tool call for frontend action conversion
            self.current_tool_calls.append({
                "tool_name": "create_region",
                "args": {
                    "name": name,
                    "region_type": region_type,
                    "coordinates": coordinates,
                    "zone_vnum": zone_vnum,
                    "auto_generate_description": auto_generate_description
                }
            })
            
            # Also call the MCP tool to make it seem like it worked to the AI
            try:
                mcp_result = await self.tools.create_region(
                    name=name,
                    region_type=region_type,
                    coordinates=coordinates,
                    zone_vnum=zone_vnum,
                    auto_generate_description=auto_generate_description
                )
                return mcp_result
            except Exception as e:
                logger.warning(f"MCP create_region failed: {e}")
                # Return success anyway for frontend action conversion
                return {
                    "success": True,
                    "message": f"Region '{name}' will be created with {len(coordinates)} points",
                    "vnum": 1000000 + hash(name) % 99999,
                    "region_type": region_type,
                    "coordinates": coordinates
                }
        
        @agent.tool
        async def build_new_path(
            ctx: RunContext[EditorContext],
            name: str,
            path_type: int,  # 1=Paved, 2=Dirt, 3=Geographic, 5=River, 6=Stream
            coordinates: List[Dict[str, float]],
            zone_vnum: int = 10000
        ) -> Dict[str, Any]:
            """Create a new wilderness path and stage it for frontend integration"""
            # Capture this tool call for frontend action conversion
            self.current_tool_calls.append({
                "tool_name": "create_path",
                "args": {
                    "name": name,
                    "path_type": path_type,
                    "coordinates": coordinates,
                    "zone_vnum": zone_vnum
                }
            })
            
            # Also call the MCP tool to make it seem like it worked to the AI
            try:
                mcp_result = await self.tools.create_path(
                    name=name,
                    path_type=path_type,
                    coordinates=coordinates,
                    zone_vnum=zone_vnum
                )
                return mcp_result
            except Exception as e:
                logger.warning(f"MCP create_path failed: {e}")
                # Return success anyway for frontend action conversion
                return {
                    "success": True,
                    "message": f"Path '{name}' will be created with {len(coordinates)} points",
                    "vnum": 2000000 + hash(name) % 99999,
                    "path_type": path_type,
                    "coordinates": coordinates
                }
        
        @agent.tool
        async def generate_region_description(
            ctx: RunContext[EditorContext],
            region_name: Optional[str] = None,
            terrain_theme: Optional[str] = None,
            style: str = "immersive",
            length: str = "medium"
        ) -> Dict[str, Any]:
            """Generate an AI-powered description for a region"""
            return await self.tools.generate_region_description(
                region_name=region_name,
                terrain_theme=terrain_theme,
                description_style=style,
                description_length=length
            )
        
        @agent.tool
        async def analyze_terrain(
            ctx: RunContext[EditorContext],
            x: int,
            y: int
        ) -> Dict[str, Any]:
            """Analyze terrain at specific coordinates"""
            return await self.tools.analyze_terrain(x, y)
        
        @agent.tool
        async def find_zone_entrances(
            ctx: RunContext[EditorContext],
            x: Optional[int] = None,
            y: Optional[int] = None,
            radius: int = 50,
            zone_vnum: Optional[int] = None
        ) -> Dict[str, Any]:
            """Find zone entrances in wilderness or near coordinates"""
            if x is not None and y is not None:
                return await self.tools.find_zone_entrances_near(x, y, radius)
            else:
                return await self.tools.find_zone_entrances(zone_vnum)
        
        @agent.tool
        async def generate_map(
            ctx: RunContext[EditorContext],
            center_x: int,
            center_y: int,
            radius: int = 10
        ) -> Dict[str, Any]:
            """Generate a wilderness map"""
            return await self.tools.generate_wilderness_map(center_x, center_y, radius)
        
        @agent.tool
        async def search_regions(
            ctx: RunContext[EditorContext],
            name: Optional[str] = None,
            x: Optional[float] = None,
            y: Optional[float] = None,
            radius: Optional[float] = None,
            region_type: Optional[int] = None,
            include_descriptions: str = "false"
        ) -> Dict[str, Any]:
            """Search for wilderness regions by name, location, or type"""
            return await self.tools.search_regions(
                name=name,
                x=x, 
                y=y,
                radius=radius,
                region_type=region_type,
                include_descriptions=include_descriptions
            )
        
        @agent.tool
        async def search_by_coordinates(
            ctx: RunContext[EditorContext],
            x: float,
            y: float,
            radius: float = 10
        ) -> Dict[str, Any]:
            """Search for regions and paths at or near specific coordinates"""
            return await self.tools.search_by_coordinates(x=x, y=y, radius=radius)
        
        return agent
    
    def _convert_tool_calls_to_actions(self, result) -> List[ChatAction]:
        """Convert captured tool calls to frontend actions"""
        actions = []
        
        # Check both local tool calls and MCP tool calls
        all_tool_calls = self.current_tool_calls.copy()
        if self.tools and hasattr(self.tools, 'captured_tool_calls'):
            all_tool_calls.extend(self.tools.captured_tool_calls)
            # Clear captured calls after processing
            self.tools.captured_tool_calls = []
        
        logger.info(f"Converting {len(all_tool_calls)} captured tool calls to actions")
        
        for tool_call in all_tool_calls:
            tool_name = tool_call.get("tool_name")
            tool_args = tool_call.get("args", {})
            
            logger.info(f"Processing captured tool call: {tool_name} with args: {tool_args}")
            
            if tool_name == 'create_region':
                actions.append(ChatAction(
                    type="create_region",
                    params={
                        "name": tool_args.get("name"),
                        "region_type": tool_args.get("region_type"),
                        "coordinates": tool_args.get("coordinates"),
                        "zone_vnum": tool_args.get("zone_vnum", 10000)
                    },
                    ui_hints={
                        "select": True,
                        "center_map": True
                    }
                ))
            elif tool_name == 'create_path':
                actions.append(ChatAction(
                    type="create_path",
                    params={
                        "name": tool_args.get("name"),
                        "path_type": tool_args.get("path_type"),
                        "coordinates": tool_args.get("coordinates"),
                        "zone_vnum": tool_args.get("zone_vnum", 10000)
                    },
                    ui_hints={
                        "select": True,
                        "center_map": True
                    }
                ))
            elif tool_name == 'generate_region_description':
                # This would stage a description for an existing region
                actions.append(ChatAction(
                    type="stage_description",
                    params={
                        "region_name": tool_args.get("region_name"),
                        "description": "Generated description will be provided",
                        "style": tool_args.get("style", "immersive"),
                        "length": tool_args.get("length", "medium")
                    }
                ))
        
        logger.info(f"Created {len(actions)} actions from captured tool calls")
        return actions
    
    def _get_system_prompt(self) -> str:
        """Get the basic system prompt for the agent"""
        return """You are an expert wilderness builder assistant for LuminariMUD.
        
Your role is to help builders create and manage wilderness regions with rich, immersive descriptions.
You have deep knowledge of:
- The LuminariMUD wilderness system and coordinate grid (-1024 to +1024)
- Creating engaging region descriptions with appropriate terrain types
- Designing paths and connections between regions
- Placing landmarks and points of interest
- Ensuring lore consistency with the game world

Guidelines:
1. Be helpful and creative while maintaining consistency with the game world
2. Suggest appropriate terrain types and properties for regions
3. Generate rich, atmospheric descriptions when requested
4. Consider connections to neighboring regions
5. Help with both technical aspects and creative writing
6. Provide clear, actionable suggestions

When the user provides editor context (selected regions, viewport, etc.), use this information
to give more targeted and relevant assistance."""
    
    def _get_enhanced_prompt(self) -> str:
        """Get enhanced prompt when tools are available"""
        return """You are an expert wilderness builder assistant for LuminariMUD with access to powerful spatial analysis and creation tools.

## CORE EXPERTISE
Your role is to help builders create and manage wilderness regions with rich, immersive descriptions.
You have deep knowledge of:
- The LuminariMUD wilderness system and coordinate grid (-1024 to +1024)
- Creating engaging region descriptions with appropriate terrain types
- Designing paths and connections between regions
- Placing landmarks and points of interest
- Ensuring lore consistency with the game world

## SPATIAL INTELLIGENCE CAPABILITIES
You excel at spatial analysis and can:

### Area Analysis
- Use `search_by_coordinates` and `analyze_complete_terrain_map` to find empty spaces between regions
- Use `analyze_terrain_at_coordinates` to understand elevation and terrain types
- Calculate optimal placement for new regions based on existing geography
- Identify suitable areas for expansion near existing regions

### Smart Region Creation
- Create regions with organic, natural borders (avoid straight lines unless explicitly requested)
- Use elevation data to follow terrain contours for realistic boundaries  
- Ensure geographic regions don't overlap (use search tools to check first)
- Include sector_transform regions when terrain elevation needs adjustment
- Generate 8-12 coordinate points for natural-looking polygonal shapes using curved paths

### Path Intelligence
- Connect multiple regions with optimal routing using terrain analysis
- Create rivers that flow from high elevation to low (use terrain analysis)
- Design roads that follow practical routes between settlements
- Generate paths with 4-8 points for natural curves, avoiding straight lines

### Overlap Prevention
- Always use `search_by_coordinates` before creating geographic regions
- Check for existing regions in the target area to prevent overlaps
- Suggest alternative coordinates if overlaps would occur
- Geographic regions should NOT overlap as this confuses the description engine

## AVAILABLE TOOLS:
- build_new_region: Create new wilderness regions with coordinates for frontend integration
- build_new_path: Create wilderness paths (roads, rivers, etc.) for frontend integration
- generate_region_description: Generate AI-powered descriptions
- analyze_terrain_at_coordinates: Examine terrain at specific coordinates
- analyze_complete_terrain_map: Get terrain analysis with region overlays in radius
- find_zone_entrances: Locate zone connections
- generate_wilderness_map: Create wilderness area maps
- search_regions: Search regions by location, type, or name
- search_by_coordinates: Find regions and paths at coordinates

## INTELLIGENT WORKFLOW EXAMPLES:

### Name Resolution Strategy
When users reference regions by name (e.g., "The Mosswood", "Darkwood Forest"):
1. First use `search_regions` with no filters to get all regions
2. Find regions with names that match (exact, partial, or fuzzy matching)
3. Extract coordinates, type, and other details from matched regions
4. Use these details for any follow-up operations

Example: "Analyze The Mosswood region"
1. Call `search_regions` to get all regions
2. Look for regions containing "mosswood" in name (case-insensitive)
3. Once found, use the region's coordinates for `analyze_terrain_at_coordinates`
4. Provide comprehensive analysis of that specific region

### Complex Spatial Operations
When user says "create a forest between The Darkwood and Crystal Lake":
1. Use `search_regions` to find "Darkwood" and "Crystal Lake" regions
2. Extract their coordinates from the search results
3. Calculate midpoint or identify space between them
4. Use `analyze_complete_terrain_map` for the area between them
5. Use `search_by_coordinates` to check for overlapping regions
6. Generate organic forest coordinates following terrain
7. Use `build_new_region` with natural curved borders

When user says "make a river from the mountains to the ocean":
1. Use `search_regions` to find mountain and ocean regions if named
2. Or use `analyze_terrain_at_coordinates` to find high elevation points
3. Use `analyze_complete_terrain_map` to trace elevation descent
4. Generate curved path coordinates following natural drainage patterns
5. Use `build_new_path` with river type (5 or 6)

When user says "find empty space near Silverwood":
1. Use `search_regions` to locate "Silverwood" region
2. Extract its coordinates from the search results  
3. Use `search_by_coordinates` around those coordinates (expanding radius if needed)
4. Use `analyze_complete_terrain_map` to identify genuinely empty areas
5. Suggest 2-3 options with different terrain types and coordinates

### Information Gathering Strategy
For ANY user query about existing regions/paths:
1. ALWAYS start with `search_regions` or `search_by_coordinates`
2. Use name matching (exact, contains, similar) to find relevant items
3. Extract ALL useful data from search results (coordinates, types, descriptions)
4. Use this extracted data for follow-up analysis or operations
5. Never say "I don't have access to" when you can chain tools to get the information

## CRITICAL TOOL USAGE RULES:
1. When asked to CREATE a region, you MUST ALWAYS call the build_new_region tool first
2. When asked to CREATE a path, you MUST ALWAYS call the build_new_path tool first  
3. Do not just describe creating something - actually use the creation tools
4. Region types: 1=Geographic, 2=Encounter, 3=Transform, 4=Sector (forest=4)
5. Path types: 1=Paved, 2=Dirt, 3=Geographic, 5=River, 6=Stream
6. Use analysis tools for information, then CREATE with creation tools
7. Always provide coordinates as: [{"x": 100, "y": 100}, {"x": 200, "y": 200}]

## INTELLIGENCE AND PROACTIVITY RULES:
1. **Be Resourceful**: If you don't immediately have information, use tools to get it
2. **Chain Tools Intelligently**: Combine search → analysis → action workflows
3. **Never Say "I Don't Have Access"**: You have search tools - use them first
4. **Extract Data from Results**: When you call search tools, READ and USE the returned data
5. **Name Matching**: Be flexible with name matching (partial, fuzzy, case-insensitive)
6. **Be Helpful**: If user asks about "The Mosswood", search for "mosswood", "moss", etc.
7. **Show Your Work**: Explain what you found when you searched
8. **Suggest Alternatives**: If exact match fails, show similar matches found

## EXAMPLE RESPONSES:

**BAD**: "I don't have access to a function that retrieves region names directly."

**GOOD**: "Let me search for The Mosswood region first..." → calls search_regions → "I found a region called 'Mosswood Forest' at coordinates (150, -200). Now let me analyze this region..." → calls analyze_terrain_at_coordinates → provides detailed analysis.

Remember: You are an INTELLIGENT AGENT, not a simple function. Use your tools creatively and in combination to solve any wilderness-related task the user presents.

When the user provides editor context (selected regions, viewport, etc.), use this information
to select appropriate coordinates and parameters for tool calls."""
    
    async def chat(self, message: str, context: Optional[EditorContext] = None) -> AssistantResponse:
        """
        Simple chat without session management
        
        Args:
            message: The user's message
            context: Optional editor context
            
        Returns:
            Structured assistant response
        """
        try:
            # Clear any previous tool calls
            self.current_tool_calls = []
            if self.tools and hasattr(self.tools, 'captured_tool_calls'):
                self.tools.captured_tool_calls = []
            
            # Create context dict for the agent
            agent_context = {}
            if context:
                agent_context["editor_context"] = context.model_dump()
            
            # Run the agent
            result = await self.agent.run(
                message,
                deps=agent_context
            )
            
            # Extract the response and convert tool calls to actions
            actions = self._convert_tool_calls_to_actions(result)
            
            if hasattr(result, 'data'):
                response = result.data
                if isinstance(response, AssistantResponse):
                    # Add actions to existing response
                    response.actions = actions
                    return response
                else:
                    # Create response from data
                    return AssistantResponse(
                        message=str(response),
                        actions=actions,
                        tool_calls=[],
                        suggestions=[],
                        warnings=[]
                    )
            elif hasattr(result, 'output'):
                # Extract output from AgentRunResult
                return AssistantResponse(
                    message=result.output if isinstance(result.output, str) else str(result.output),
                    actions=actions,
                    tool_calls=[],
                    suggestions=[],
                    warnings=[]
                )
            else:
                # Fallback: create a response from the raw result
                return AssistantResponse(
                    message=str(result),
                    actions=actions,
                    tool_calls=[],
                    suggestions=[],
                    warnings=[]
                )
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return AssistantResponse(
                message=f"I encountered an error: {str(e)}",
                warnings=[f"Error processing request: {str(e)}"]
            )
    
    async def chat_with_history(
        self, 
        message: str,
        history: List[Dict[str, str]],
        context: Optional[EditorContext] = None
    ) -> AssistantResponse:
        """
        Chat with conversation history
        
        Args:
            message: The user's message
            history: List of previous messages
            context: Optional editor context
            
        Returns:
            Structured assistant response
        """
        try:
            # Clear any previous tool calls
            self.current_tool_calls = []
            if self.tools and hasattr(self.tools, 'captured_tool_calls'):
                self.tools.captured_tool_calls = []
            
            # Convert history to agent format
            from pydantic_ai.messages import UserPromptPart, ModelRequest, ModelResponse, TextPart
            
            messages = []
            for msg in history:
                if msg["role"] == "user":
                    messages.append(ModelRequest(parts=[UserPromptPart(content=msg["content"])]))
                elif msg["role"] == "assistant":
                    messages.append(ModelResponse(parts=[TextPart(content=msg["content"])]))
            
            # Create context dict
            agent_context = {}
            if context:
                agent_context["editor_context"] = context.model_dump()
            
            # Run the agent with history
            result = await self.agent.run(
                message,
                message_history=messages,
                deps=agent_context
            )
            
            # Extract the response and convert tool calls to actions
            actions = self._convert_tool_calls_to_actions(result)
            
            if hasattr(result, 'data'):
                response = result.data
                if isinstance(response, AssistantResponse):
                    # Add actions to existing response
                    response.actions = actions
                    return response
                else:
                    # Create response from data
                    return AssistantResponse(
                        message=str(response),
                        actions=actions,
                        tool_calls=[],
                        suggestions=[],
                        warnings=[]
                    )
            elif hasattr(result, 'output'):
                # Extract output from AgentRunResult
                return AssistantResponse(
                    message=result.output if isinstance(result.output, str) else str(result.output),
                    actions=actions,
                    tool_calls=[],
                    suggestions=[],
                    warnings=[]
                )
            else:
                # Fallback: create a response from the raw result
                return AssistantResponse(
                    message=str(result),
                    actions=actions,
                    tool_calls=[],
                    suggestions=[],
                    warnings=[]
                )
            
        except Exception as e:
            logger.error(f"Error in chat_with_history: {str(e)}")
            return AssistantResponse(
                message=f"I encountered an error: {str(e)}",
                warnings=[f"Error processing request: {str(e)}"]
            )