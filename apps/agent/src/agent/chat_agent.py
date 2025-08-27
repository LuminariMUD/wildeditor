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


class AssistantResponse(BaseModel):
    """Structured response from the assistant"""
    message: str = Field(description="The main response message")
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="Tool calls made during processing")
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
    
    def __init__(self, backend_client=None, mcp_client=None):
        """Initialize the agent with configured model and optional tools"""
        self.model = self._initialize_model()
        
        if not self.model:
            raise ValueError("No AI model could be initialized. Please configure API keys.")
        
        # Initialize tools if clients are provided
        self.tools = None
        if backend_client and mcp_client:
            self.tools = WildernessTools(backend_client, mcp_client)
            logger.info("Initialized with MCP and backend tools")
        
        # Initialize the agent with or without tools
        if self.tools:
            self.agent = self._create_agent_with_tools()
        else:
            self.agent = Agent(
                model=self.model,
                result_type=AssistantResponse,
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
                return OpenAIModel(
                    model_name=settings.model_name or "gpt-4-turbo",
                    api_key=settings.openai_api_key
                )
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
        
        elif provider == "deepseek" and settings.deepseek_api_key:
            try:
                logger.info(f"Initializing DeepSeek model: {settings.deepseek_model}")
                # DeepSeek uses OpenAI-compatible API
                return OpenAIModel(
                    model_name=settings.deepseek_model or "deepseek-chat",
                    api_key=settings.deepseek_api_key,
                    base_url="https://api.deepseek.com/v1"
                )
            except Exception as e:
                logger.warning(f"Failed to initialize DeepSeek: {e}")
        
        elif provider == "anthropic" and settings.anthropic_api_key:
            try:
                logger.info(f"Initializing Anthropic model: {settings.model_name}")
                return AnthropicModel(
                    model_name=settings.model_name or "claude-3-opus-20240229",
                    api_key=settings.anthropic_api_key
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic: {e}")
        
        # If no explicit provider or it failed, try fallback chain
        logger.info("Trying fallback model chain...")
        
        # Try OpenAI first (most common)
        if settings.openai_api_key:
            try:
                logger.info("Falling back to OpenAI")
                return OpenAIModel(
                    model_name=settings.model_name or "gpt-4-turbo",
                    api_key=settings.openai_api_key
                )
            except Exception as e:
                logger.warning(f"OpenAI fallback failed: {e}")
        
        # Try DeepSeek as second fallback
        if settings.deepseek_api_key:
            try:
                logger.info("Falling back to DeepSeek")
                return OpenAIModel(
                    model_name=settings.deepseek_model or "deepseek-chat",
                    api_key=settings.deepseek_api_key,
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
            result_type=AssistantResponse,
            system_prompt=self._get_enhanced_prompt()
        )
        
        # Register all tools
        @agent.tool
        async def create_region(
            ctx: RunContext[EditorContext],
            name: str,
            region_type: str,
            coordinates: List[List[float]],
            auto_generate_description: bool = True
        ) -> Dict[str, Any]:
            """Create a new wilderness region"""
            return await self.tools.create_region(
                name, region_type, coordinates,
                auto_generate_description=auto_generate_description
            )
        
        @agent.tool
        async def generate_region_description(
            ctx: RunContext[EditorContext],
            region_name: Optional[str] = None,
            terrain_theme: Optional[str] = None,
            style: str = "immersive"
        ) -> str:
            """Generate an AI-powered description for a region"""
            return await self.tools.generate_region_description(
                region_name, terrain_theme, style
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
            x: int,
            y: int,
            radius: int = 50
        ) -> Dict[str, Any]:
            """Find zone entrances near coordinates"""
            return await self.tools.find_zone_entrances_near(x, y, radius)
        
        @agent.tool
        async def generate_map(
            ctx: RunContext[EditorContext],
            center_x: int,
            center_y: int,
            radius: int = 10
        ) -> Dict[str, Any]:
            """Generate a wilderness map"""
            return await self.tools.generate_wilderness_map(center_x, center_y, radius)
        
        return agent
    
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
        return """You are an expert wilderness builder assistant for LuminariMUD with access to powerful tools.
        
Your role is to help builders create and manage wilderness regions with rich, immersive descriptions.
You have deep knowledge of:
- The LuminariMUD wilderness system and coordinate grid (-1024 to +1024)
- Creating engaging region descriptions with appropriate terrain types
- Designing paths and connections between regions
- Placing landmarks and points of interest
- Ensuring lore consistency with the game world

AVAILABLE TOOLS:
- create_region: Create new wilderness regions with coordinates
- generate_region_description: Generate AI-powered descriptions
- analyze_terrain: Examine terrain at specific coordinates
- find_zone_entrances: Locate nearby zone connections
- generate_map: Create wilderness area maps

Guidelines:
1. Use tools proactively when they would help the user
2. When creating regions, always generate descriptions unless told otherwise
3. Consider terrain analysis before placing new regions
4. Check for nearby features and connections
5. Provide clear explanations of what you're doing with tools
6. Format tool results in a user-friendly way

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
            # Create context dict for the agent
            agent_context = {}
            if context:
                agent_context["editor_context"] = context.model_dump()
            
            # Run the agent
            result = await self.agent.run(
                message,
                deps=agent_context
            )
            
            return result.data
            
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
            # Convert history to agent format
            from pydantic_ai.messages import UserPrompt, ModelTextResponse
            
            messages = []
            for msg in history:
                if msg["role"] == "user":
                    messages.append(UserPrompt(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(ModelTextResponse(content=msg["content"]))
            
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
            
            return result.data
            
        except Exception as e:
            logger.error(f"Error in chat_with_history: {str(e)}")
            return AssistantResponse(
                message=f"I encountered an error: {str(e)}",
                warnings=[f"Error processing request: {str(e)}"]
            )