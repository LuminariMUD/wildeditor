"""
AI Service for generating wilderness descriptions using PydanticAI

This service provides AI-powered description generation with multiple provider support
and graceful fallback to template-based generation.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from pydantic_ai import Agent, ModelRetry
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel

logger = logging.getLogger(__name__)

# Try to import DeepSeekProvider - it might not exist in older versions
try:
    from pydantic_ai.providers.deepseek import DeepSeekProvider
    DEEPSEEK_AVAILABLE = True
except ImportError:
    logger.warning("DeepSeekProvider not available in this version of pydantic-ai")
    DEEPSEEK_AVAILABLE = False

class AIProvider(str, Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    DEEPSEEK = "deepseek"
    NONE = "none"

class DescriptionMetadata(BaseModel):
    """Structured output for description metadata"""
    has_historical_context: bool = Field(default=False, description="Contains historical information")
    has_resource_info: bool = Field(default=False, description="Mentions resources or materials")
    has_wildlife_info: bool = Field(default=False, description="Includes wildlife details")
    has_geological_info: bool = Field(default=False, description="Contains geological information")
    has_cultural_info: bool = Field(default=False, description="Includes cultural elements")
    quality_score: float = Field(default=7.0, ge=0, le=9.99, description="Quality score 0-9.99")
    key_features: List[str] = Field(default_factory=list, description="Notable features mentioned")

class GeneratedDescription(BaseModel):
    """Structured output for generated descriptions"""
    description_text: str = Field(description="The full description text")
    metadata: DescriptionMetadata = Field(description="Metadata about the description")
    word_count: int = Field(description="Number of words in description")

class GeneratedHint(BaseModel):
    """Structured output for a single generated hint"""
    category: str = Field(description="Hint category - MUST be one of: atmosphere, fauna, flora, weather_influence, sounds, scents, seasonal_changes, time_of_day, mystical")
    text: str = Field(description="Clean descriptive hint text without formatting")
    priority: int = Field(ge=1, le=10, description="Priority level 1-10")
    weather_conditions: List[str] = Field(
        default_factory=list, 
        description="Applicable weather conditions - ONLY use: clear, cloudy, rainy, stormy, lightning"
    )
    seasonal_weight: Optional[Dict[str, float]] = Field(
        default=None,
        description="Seasonal weights dict with keys: spring, summer, autumn, winter. Values 0.0-2.0 where 0=never, 1=normal, 2=double chance. Set higher values for relevant seasons, lower/zero for others."
    )
    time_of_day_weight: Optional[Dict[str, float]] = Field(
        default=None,
        description="Time weights dict with keys: dawn, morning, midday, afternoon, evening, night. Values 0.0-2.0 where 0=never, 1=normal, 2=double chance."
    )
    
    @field_validator('weather_conditions')
    @classmethod
    def validate_weather(cls, v: List[str]) -> List[str]:
        """Validate and clean weather conditions"""
        valid_weather = {'clear', 'cloudy', 'rainy', 'stormy', 'lightning'}
        # Filter to only valid weather conditions
        cleaned = [w for w in v if w in valid_weather]
        # If all conditions were invalid, return empty list
        return cleaned if cleaned else []

class GeneratedHints(BaseModel):
    """Structured output for generated hints collection"""
    hints: List[GeneratedHint] = Field(description="List of generated categorized hints")
    total_count: int = Field(description="Total number of hints generated")
    categories_used: List[str] = Field(description="Categories that were used")

class AIService:
    """
    AI Service for generating region descriptions
    
    Supports multiple AI providers with fallback to template generation
    """
    
    def __init__(self):
        """Initialize AI service with configured provider"""
        self.provider = self._get_provider()
        self.initialization_error = None
        self.model = self._initialize_model()
        self.agent = self._create_agent() if self.model else None
        # Create separate hint agent with same model but different output type
        self.hint_agent = self._create_hint_agent() if self.model else None
        
        logger.info(f"AI Service initialized with provider: {self.provider} (v1.0.11)")
        logger.info(f"Model: {self.model is not None}, Description Agent: {self.agent is not None}, Hint Agent: {self.hint_agent is not None}")
        if self.hint_agent:
            logger.info(f"Hint agent created successfully with model: {type(self.model)}")
        else:
            logger.warning(f"Failed to create hint agent - model available: {self.model is not None}")
        logger.info(f"Using two specialized agents with the same powerful model")
    
    def _get_provider(self) -> AIProvider:
        """Determine which AI provider to use based on environment"""
        provider_str = os.getenv("AI_PROVIDER", "none").lower()
        
        # Respect explicit AI_PROVIDER setting (even without API key - for fallback chain)
        if provider_str == "openai":
            return AIProvider.OPENAI
        elif provider_str == "anthropic":
            return AIProvider.ANTHROPIC
        elif provider_str == "ollama":
            return AIProvider.OLLAMA
        elif provider_str == "deepseek":
            return AIProvider.DEEPSEEK
        else:
            # Try to auto-detect based on available keys
            if os.getenv("OPENAI_API_KEY"):
                return AIProvider.OPENAI
            elif os.getenv("ANTHROPIC_API_KEY"):
                return AIProvider.ANTHROPIC
            elif os.getenv("DEEPSEEK_API_KEY"):
                return AIProvider.DEEPSEEK
            elif os.getenv("OLLAMA_BASE_URL"):
                return AIProvider.OLLAMA
            else:
                return AIProvider.NONE
    
    def _initialize_model(self) -> Optional[Model]:
        """Initialize the AI model based on provider"""
        try:
            if self.provider == AIProvider.OPENAI:
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    logger.warning("OpenAI API key not found")
                    return None
                
                model_name = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
                # Set OpenAI API key in environment for the client
                os.environ['OPENAI_API_KEY'] = api_key
                return OpenAIModel(
                    model_name=model_name
                )
            
            elif self.provider == AIProvider.ANTHROPIC:
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    logger.warning("Anthropic API key not found")
                    return None
                
                model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
                # Set Anthropic API key in environment for the client
                os.environ['ANTHROPIC_API_KEY'] = api_key
                return AnthropicModel(
                    model_name=model_name
                )
            
            elif self.provider == AIProvider.DEEPSEEK:
                api_key = os.getenv("DEEPSEEK_API_KEY")
                if not api_key:
                    self.initialization_error = "DeepSeek API key not found"
                    logger.warning(self.initialization_error)
                    return None
                
                model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
                
                # Check if DeepSeekProvider is available
                if not DEEPSEEK_AVAILABLE:
                    self.initialization_error = f"DeepSeekProvider not available in pydantic-ai version"
                    logger.warning(self.initialization_error)
                    return None
                
                # Use DeepSeekProvider with OpenAIModel
                try:
                    provider = DeepSeekProvider(api_key=api_key)
                    return OpenAIModel(
                        model_name=model_name,
                        provider=provider
                    )
                except Exception as e:
                    self.initialization_error = f"Failed to initialize DeepSeek: {str(e)}"
                    logger.error(self.initialization_error)
                    return None
            
            elif self.provider == AIProvider.OLLAMA:
                # Ollama doesn't work well with PydanticAI's OpenAI adapter
                # Return None to trigger direct HTTP fallback in generate_description
                logger.info("Ollama selected as provider, will use direct HTTP calls")
                return None
            
            else:
                logger.info("No AI provider configured, using template generation")
                return None
                
        except Exception as e:
            logger.error(f"Failed to initialize AI model: {e}")
            return None
    
    def _create_agent(self) -> Optional[Agent]:
        """Create PydanticAI agent for both description and hint generation"""
        if not self.model:
            return None
        
        try:
            # Create agent for description generation (primary use)
            # Note: For hint generation, we create a separate instance with different output type
            agent = Agent(
                model=self.model,
                output_type=GeneratedDescription,
                instructions="""You are an expert wilderness designer for a fantasy MUD game. 
                Your task is to create rich, immersive descriptions for wilderness regions.
                
                Guidelines:
                - Create vivid, detailed descriptions that help players visualize the environment
                - Include sensory details (sight, sound, smell, touch, temperature)
                - Mention specific flora, fauna, and geographical features
                - Make descriptions practical for game navigation
                - Ensure consistency with the terrain type and theme
                
                Your descriptions should be comprehensive yet engaging, suitable for text-based gameplay."""
            )
            
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create AI agent: {e}")
            return None

    def _create_hint_agent(self) -> Optional[Agent]:
        """Create PydanticAI agent specifically for hint generation"""
        if not self.model:
            return None
        
        try:
            # Create agent with structured hint output using the same powerful model
            hint_agent = Agent(
                model=self.model,
                output_type=GeneratedHints,
                instructions="""You are an expert wilderness designer for a fantasy MUD game. 
                Your task is to analyze region descriptions and generate immersive atmospheric hints.
                
                Guidelines:
                - Generate 8-15 clean, descriptive hints without headers or formatting characters
                - Each hint should be a complete standalone sentence that enhances immersion
                - Categorize hints ONLY using these valid categories: atmosphere, fauna, flora, weather_influence, sounds, scents, seasonal_changes, time_of_day, mystical
                - DO NOT use: geography, landmarks, resources (map these to atmosphere or flora instead)
                - CRITICAL: For weather_conditions, ONLY use these exact values: clear, cloudy, rainy, stormy, lightning
                - Do NOT put time of day (dawn, evening, night) in weather_conditions
                - Do NOT put seasons (winter, summer) in weather_conditions  
                - If a hint is not weather-specific, use an empty list for weather_conditions
                
                STRICT WEIGHT RULES:
                
                TIME OF DAY:
                - EXPLICIT time mentions ("at dusk", "at dawn", "at midnight"): 
                  ONLY that time gets 2.0, ALL others get 0.0
                  Example: "At dusk, flowers unfurl" -> {"dawn": 0.0, "morning": 0.0, "midday": 0.0, "afternoon": 0.0, "evening": 2.0, "night": 0.0}
                - THEMED time (moonlight, stars, nocturnal, darkness):
                  Primary time gets 2.0, adjacent gets 0.5, opposite gets 0.0
                  
                SEASONS:
                - EXPLICIT season mentions ("in winter", "during spring"):
                  ONLY that season gets 2.0, ALL others get 0.0
                - THEMED season (flowers=spring, snow=winter, harvest=autumn, heat=summer):
                  Primary season gets 2.0, adjacent gets 0.5 max, opposite gets 0.0
                  
                GENERAL HINTS: Don't set weights (null) for general hints that apply at all times/seasons.
                
                Your hints should be evocative, detailed, and help players fully immerse in the environment."""
            )
            
            return hint_agent
            
        except Exception as e:
            logger.error(f"Failed to create hint agent: {e}")
            return None
    
    async def generate_description(
        self,
        region_name: str,
        terrain_theme: str,
        style: str = "poetic",
        length: str = "moderate",
        sections: List[str] = None,
        existing_prompt: Dict[str, Any] = None,
        user_prompt: str = ""
    ) -> Dict[str, Any]:
        """
        Generate a region description using AI
        
        Args:
            region_name: Name of the region
            terrain_theme: Primary terrain type/theme
            style: Writing style (poetic, practical, mysterious, dramatic, pastoral)
            length: Target length (brief, moderate, detailed, extensive)
            sections: List of sections to include
            existing_prompt: Pre-formatted prompt from prompt system
        
        Returns:
            Dictionary with generated description and metadata
        """
        
        # If no AI available, check if we should use Ollama or fallback to template
        if not self.agent:
            error_msg = f"Primary AI agent not available. Provider: {self.provider}"
            if self.initialization_error:
                error_msg += f". Error: {self.initialization_error}"
            logger.info(error_msg)
            
            # If Ollama is the selected provider OR we want to try it as fallback
            if self.provider == AIProvider.OLLAMA or (
                self.provider in [AIProvider.OPENAI, AIProvider.ANTHROPIC, AIProvider.DEEPSEEK] and 
                os.getenv("OLLAMA_BASE_URL")
            ):
                logger.info(f"Using Ollama for description generation (provider: {self.provider})")
                result = await self._use_ollama_direct(
                    region_name, terrain_theme, style, length, sections, existing_prompt, user_prompt
                )
                if result:
                    # Add initialization error info to result
                    result['initialization_error'] = self.initialization_error
                return result
            else:
                logger.info("No AI agent available, falling back to template")
                return {
                    "error": "No AI provider available",
                    "initialization_error": self.initialization_error,
                    "provider_attempted": self.provider.value
                }
        
        # Prepare the user prompt
        if existing_prompt and "messages" in existing_prompt:
            # Use existing prompt messages
            messages = existing_prompt["messages"]
            user_content = next(
                (msg["content"] for msg in messages if msg["role"] == "user"),
                ""
            )
        else:
            # Build custom prompt
            length_guides = {
                "brief": "100-200 words",
                "moderate": "300-500 words",
                "detailed": "600-900 words",
                "extensive": "1000+ words"
            }
            
            sections_list = sections or ["overview", "geography", "vegetation", "atmosphere"]
            sections_text = "\n".join(f"- {section.upper()}" for section in sections_list)
            
            # Include user prompt if provided
            user_guidance = ""
            if user_prompt:
                user_guidance = f"\n\nAdditional Guidance:\n{user_prompt}\n"
            
            user_content = f"""Create a {style} description for a wilderness region with these specifications:

Region Name: {region_name}
Terrain Theme: {terrain_theme}
Writing Style: {style}
Target Length: {length_guides.get(length, "300-500 words")}{user_guidance}

Required Sections:
{sections_text}

Create a comprehensive, immersive description that brings this region to life. Include specific details about:
- Visual appearance and landscape features
- Flora and fauna appropriate to the terrain
- Atmospheric elements (weather, lighting, sounds, smells)
- Unique characteristics that make this region memorable
- Practical details for game navigation

Make the description vivid and engaging while maintaining the {style} style throughout."""
        
        try:
            # Generate with retry logic
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    result = await self.agent.run(user_content)
                    
                    # Extract the structured result - handle different result formats
                    if hasattr(result, 'data'):
                        generated = result.data
                    elif hasattr(result, 'output'):
                        generated = result.output
                    else:
                        # For DeepSeek or other providers that might return different structure
                        generated = result
                    
                    return {
                        "generated_description": generated.description_text,
                        "metadata": {
                            "has_historical_context": generated.metadata.has_historical_context,
                            "has_resource_info": generated.metadata.has_resource_info,
                            "has_wildlife_info": generated.metadata.has_wildlife_info,
                            "has_geological_info": generated.metadata.has_geological_info,
                            "has_cultural_info": generated.metadata.has_cultural_info,
                            "quality_score": generated.metadata.quality_score
                        },
                        "word_count": generated.word_count,
                        "character_count": len(generated.description_text),
                        "suggested_quality_score": generated.metadata.quality_score,
                        "region_name": region_name,
                        "ai_provider": self.provider.value,
                        "key_features": generated.metadata.key_features
                    }
                    
                except ModelRetry as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"AI generation retry {attempt + 1}: {e}")
                        continue
                    raise
            
        except Exception as e:
            error_details = f"Primary AI generation failed with {self.provider.value}: {str(e)}"
            logger.error(error_details)
            # Try Ollama fallback if primary provider failed and we're not already using Ollama
            if self.provider != AIProvider.OLLAMA:
                logger.info("Attempting Ollama fallback for description generation")
                result = await self._use_ollama_direct(
                    region_name, terrain_theme, style, length, sections, existing_prompt, user_prompt
                )
                if result:
                    # Add error info from primary provider
                    result['primary_provider_error'] = error_details
                return result
            # Return error details if no fallback available
            return {
                "error": "AI generation failed",
                "error_details": error_details,
                "provider": self.provider.value
            }
    
    async def _use_ollama_direct(
        self,
        region_name: str,
        terrain_theme: str,
        style: str = "poetic",
        length: str = "moderate",
        sections: List[str] = None,
        existing_prompt: Dict[str, Any] = None,
        user_prompt: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Generate description using direct Ollama HTTP API
        
        This method is used when:
        1. Ollama is the primary provider (AI_PROVIDER=ollama)
        2. As a fallback when OpenAI/Anthropic fail
        """
        logger.info(f"Starting Ollama direct generation (provider: {self.provider})")
        try:
            # Check if Ollama is configured and available
            ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
            logger.info(f"Ollama config - URL: {ollama_base_url}, Model: {ollama_model}")
            
            # Use direct HTTP request to Ollama instead of PydanticAI
            # This is more reliable for our fallback use case
            import aiohttp
            import json as json_lib
            
            # Build the prompt content
            if existing_prompt and "messages" in existing_prompt:
                messages = existing_prompt["messages"]
                user_content = next(
                    (msg["content"] for msg in messages if msg["role"] == "user"),
                    ""
                )
            else:
                length_guides = {
                    "brief": "100-200 words",
                    "moderate": "300-500 words", 
                    "detailed": "600-900 words",
                    "extensive": "1000+ words"
                }
                
                sections_list = sections or ["overview", "geography", "vegetation", "atmosphere"]
                sections_text = "\n".join(f"- {section.upper()}" for section in sections_list)
                
                # Include user prompt if provided
                user_guidance = ""
                if user_prompt:
                    user_guidance = f"\n\nAdditional Guidance:\n{user_prompt}\n"
                
                user_content = f"""Create a {style} description for a wilderness region with these specifications:

Region Name: {region_name}
Terrain Theme: {terrain_theme}
Writing Style: {style}
Target Length: {length_guides.get(length, "300-500 words")}{user_guidance}

Required Sections:
{sections_text}

Create a comprehensive, immersive description that brings this region to life."""
            
            # Make direct request to Ollama
            request_data = {
                "model": ollama_model,
                "prompt": user_content,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            }
            
            async with aiohttp.ClientSession() as session:
                logger.info(f"Attempting Ollama request to {ollama_base_url}/api/generate")
                async with session.post(
                    f"{ollama_base_url}/api/generate",
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        logger.error(f"Ollama request failed with status {response.status}")
                        return None
                    
                    response_data = await response.json()
                    generated_text = response_data.get("response", "")
                    
                    if not generated_text:
                        logger.error("Ollama returned empty response")
                        return None
                    
                    # Create a structured response similar to PydanticAI format
                    word_count = len(generated_text.split())
                    
                    # Determine if this is primary or fallback usage
                    provider_name = "ollama" if self.provider == AIProvider.OLLAMA else "ollama_fallback"
                    logger.info(f"Ollama generation successful via direct API (provider: {provider_name})")
                    
                    return {
                        "generated_description": generated_text,
                        "metadata": {
                            "has_historical_context": False,  # Simple fallback metadata
                            "has_resource_info": False,
                            "has_wildlife_info": True,
                            "has_geological_info": True,
                            "has_cultural_info": False,
                            "quality_score": 7.0  # Default score for Ollama
                        },
                        "word_count": word_count,
                        "character_count": len(generated_text),
                        "suggested_quality_score": 7.0,
                        "region_name": region_name,
                        "ai_provider": provider_name,
                        "key_features": []  # Could be enhanced later
                    }
            
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}", exc_info=True)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    async def generate_hints_from_description(self, description: str, region_name: str = "") -> Dict[str, Any]:
        """
        Generate categorized hints from a region description using AI
        
        Args:
            description: The region description text to analyze
            region_name: Optional region name for context
            
        Returns:
            Dictionary with generated hints and metadata
        """
        
        # Check if we have a hint agent to work with
        if not self.hint_agent:
            logger.error("No hint agent available for hint generation")
            return {
                "error": "AI service not available for hint generation",
                "hints": [],
                "ai_provider": "none"
            }
        
        # Create the prompt for hint generation
        user_content = f"""Analyze this wilderness region description and generate immersive atmospheric hints.

Region Description:
{description}

{f'Region Name: {region_name}' if region_name else ''}

Generate 8-15 categorized hints that enhance player immersion. 

CRITICAL: Each hint MUST include these fields:
- category: One of: atmosphere, fauna, flora, weather_influence, sounds, scents, seasonal_changes, time_of_day, mystical
- text: A complete, standalone descriptive sentence
- priority: Number from 1-10 based on impact and uniqueness
- weather_conditions: Array from [clear, cloudy, rainy, stormy, lightning] or empty array
- seasonal_weight: For seasonal hints, dict like {"spring": 0.0, "summer": 0.0, "autumn": 0.2, "winter": 2.0}
- time_of_day_weight: For time hints, dict like {"dawn": 2.0, "morning": 1.2, "midday": 0.5, "afternoon": 0.5, "evening": 0.8, "night": 0.6}

STRICT WEIGHT RULES - BE VERY SPECIFIC:

TIME WEIGHTS:
- EXPLICIT mentions (dusk, dawn, noon, etc): ONLY that time gets weight, all others 0.0
  Example: "At dusk..." → {"dawn": 0.0, "morning": 0.0, "midday": 0.0, "afternoon": 0.0, "evening": 2.0, "night": 0.0}
- THEMED (nocturnal, moonlight, darkness): High for primary time, small for adjacent
  Example: "Moonlight..." → {"dawn": 0.0, "morning": 0.0, "midday": 0.0, "afternoon": 0.0, "evening": 0.5, "night": 2.0}
- General hints: null (no time_of_day_weight at all)

SEASON WEIGHTS:
- EXPLICIT mentions (winter, spring, etc): ONLY that season gets weight, all others 0.0
  Example: "Winter frost..." → {"spring": 0.0, "summer": 0.0, "autumn": 0.0, "winter": 2.0}
- THEMED (flowers, snow, harvest): High for primary season, minimal for adjacent
  Example: "Flowers bloom..." → {"spring": 2.0, "summer": 0.5, "autumn": 0.0, "winter": 0.0}
- General hints: null (no seasonal_weight at all)

WEATHER CONDITIONS:
- Only include if EXPLICITLY weather-dependent
- "When it rains..." → ["rainy"]
- "During storms..." → ["stormy", "lightning"]
- General hints: empty array []

Focus on creating vivid, sensory details that bring the environment to life for text-based gameplay."""

        try:
            # Generate with retry logic
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    logger.info(f"AI hint generation attempt {attempt + 1}, description length: {len(description)}")
                    logger.debug(f"Sending to hint agent: {user_content[:500]}...")
                    
                    # Call the hint agent directly with the user content
                    result = await self.hint_agent.run(user_content)
                    logger.info(f"Hint agent returned result type: {type(result)}")
                    logger.debug(f"Raw result: {str(result)[:500]}...")
                    
                    # Extract the structured result - handle different result formats
                    if hasattr(result, 'data'):
                        generated = result.data
                        logger.info(f"Using result.data: {type(generated)}")
                    elif hasattr(result, 'output'):
                        generated = result.output
                        logger.info(f"Using result.output: {type(generated)}")
                    else:
                        # For DeepSeek or other providers that might return different structure
                        generated = result
                        logger.info(f"Using raw result: {type(generated)}")
                    
                    logger.info(f"Generated object has {len(generated.hints) if hasattr(generated, 'hints') else 'NO'} hints")
                    
                    # If no hints were generated, log why
                    if hasattr(generated, 'hints') and len(generated.hints) == 0:
                        logger.warning("Hint agent returned 0 hints - checking why...")
                        logger.warning(f"Generated object type: {type(generated)}")
                        logger.warning(f"Generated attributes: {dir(generated)}")
                        if hasattr(generated, 'total_count'):
                            logger.warning(f"Total count: {generated.total_count}")
                        if hasattr(generated, 'categories_used'):
                            logger.warning(f"Categories used: {generated.categories_used}")
                    
                    # Validate and clean weather conditions
                    valid_weather = {'clear', 'cloudy', 'rainy', 'stormy', 'lightning'}
                    cleaned_hints = []
                    
                    for hint in generated.hints:
                        # Filter out invalid weather conditions
                        clean_weather = [w for w in hint.weather_conditions if w in valid_weather]
                        
                        # If no valid weather conditions remain, use default set
                        if not clean_weather and hint.weather_conditions:
                            # Had weather conditions but all were invalid - use defaults
                            clean_weather = ['clear', 'cloudy', 'rainy', 'stormy', 'lightning']
                            
                        # Build the hint dict with weights included
                        hint_dict = {
                            "category": hint.category,
                            "text": hint.text,
                            "priority": hint.priority,
                            "weather_conditions": clean_weather,
                            "ai_agent_id": "mcp_ai_hint_generator"
                        }
                        
                        # Add seasonal_weight if provided
                        if hasattr(hint, 'seasonal_weight') and hint.seasonal_weight:
                            hint_dict["seasonal_weight"] = hint.seasonal_weight
                            
                        # Add time_of_day_weight if provided
                        if hasattr(hint, 'time_of_day_weight') and hint.time_of_day_weight:
                            hint_dict["time_of_day_weight"] = hint.time_of_day_weight
                            
                        cleaned_hints.append(hint_dict)
                    
                    return {
                        "hints": cleaned_hints,
                        "total_hints_generated": generated.total_count,
                        "categories_used": generated.categories_used,
                        "ai_provider": self.provider.value,
                        "region_name": region_name,
                        "description_length": len(description)
                    }
                    
                except ModelRetry as e:
                    logger.error(f"ModelRetry exception on attempt {attempt + 1}: {e}")
                    if attempt == max_retries - 1:
                        logger.error(f"Max retries exceeded for hint generation: {e}")
                        raise
                    logger.warning(f"Retrying hint generation (attempt {attempt + 1}): {e}")
                    continue
                except Exception as inner_e:
                    logger.error(f"Exception during hint generation attempt {attempt + 1}: {inner_e}")
                    if attempt == max_retries - 1:
                        raise
                    continue
                    
        except Exception as e:
            import traceback
            logger.error(f"AI hint generation failed: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                "error": f"Failed to generate hints: {str(e)}",
                "hints": [],
                "ai_provider": self.provider.value
            }
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        # Ollama uses direct HTTP so agent is None, but it's still available
        if self.provider == AIProvider.OLLAMA and os.getenv("OLLAMA_BASE_URL"):
            return True
        # DeepSeek requires API key
        if self.provider == AIProvider.DEEPSEEK:
            return self.agent is not None and os.getenv("DEEPSEEK_API_KEY") is not None
        # For other providers, check if agent exists
        return self.agent is not None
    
    def is_hint_agent_available(self) -> bool:
        """Check if hint generation agent is available"""
        # Since we use the same model for both, check if model exists
        return self.model is not None
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current AI provider"""
        return {
            "provider": self.provider.value,
            "available": self.is_available(),
            "model": os.getenv(f"{self.provider.value.upper()}_MODEL", "default")
            if self.provider != AIProvider.NONE else None
        }

# Global AI service instance
_ai_service = None

def get_ai_service() -> AIService:
    """Get or create the global AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service