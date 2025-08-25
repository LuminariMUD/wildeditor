"""
AI Service for generating wilderness descriptions using PydanticAI

This service provides AI-powered description generation with multiple provider support
and graceful fallback to template-based generation.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel

logger = logging.getLogger(__name__)

class AIProvider(str, Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
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

class AIService:
    """
    AI Service for generating region descriptions
    
    Supports multiple AI providers with fallback to template generation
    """
    
    def __init__(self):
        """Initialize AI service with configured provider"""
        self.provider = self._get_provider()
        self.model = self._initialize_model()
        self.agent = self._create_agent() if self.model else None
        
        logger.info(f"AI Service initialized with provider: {self.provider}")
    
    def _get_provider(self) -> AIProvider:
        """Determine which AI provider to use based on environment"""
        provider_str = os.getenv("AI_PROVIDER", "none").lower()
        
        # Check if provider is configured
        if provider_str == "openai" and os.getenv("OPENAI_API_KEY"):
            return AIProvider.OPENAI
        elif provider_str == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
            return AIProvider.ANTHROPIC
        elif provider_str == "ollama" and os.getenv("OLLAMA_BASE_URL"):
            return AIProvider.OLLAMA
        else:
            # Try to auto-detect based on available keys
            if os.getenv("OPENAI_API_KEY"):
                return AIProvider.OPENAI
            elif os.getenv("ANTHROPIC_API_KEY"):
                return AIProvider.ANTHROPIC
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
            
            elif self.provider == AIProvider.OLLAMA:
                # For Ollama, we'd need to implement a custom model class
                # or use OpenAI-compatible endpoint
                base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                model_name = os.getenv("OLLAMA_MODEL", "llama2")
                
                # Ollama can use OpenAI-compatible API
                # For Ollama, we need to use a custom provider
                from openai import AsyncOpenAI
                client = AsyncOpenAI(
                    base_url=f"{base_url}/v1",
                    api_key="ollama"  # Ollama doesn't need a real key
                )
                return OpenAIModel(
                    model_name=model_name,
                    provider=client
                )
            
            else:
                logger.info("No AI provider configured, using template generation")
                return None
                
        except Exception as e:
            logger.error(f"Failed to initialize AI model: {e}")
            return None
    
    def _create_agent(self) -> Optional[Agent]:
        """Create PydanticAI agent for description generation"""
        if not self.model:
            return None
        
        try:
            # Create agent with structured output
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
    
    async def generate_description(
        self,
        region_name: str,
        terrain_theme: str,
        style: str = "poetic",
        length: str = "moderate",
        sections: List[str] = None,
        existing_prompt: Dict[str, Any] = None
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
        
        # If no AI available, return None to trigger fallback
        if not self.agent:
            logger.info("AI agent not available, falling back to template")
            return None
        
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
            
            user_content = f"""Create a {style} description for a wilderness region with these specifications:

Region Name: {region_name}
Terrain Theme: {terrain_theme}
Writing Style: {style}
Target Length: {length_guides.get(length, "300-500 words")}

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
                    
                    # Extract the structured result
                    generated = result.data
                    
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
            logger.error(f"AI generation failed: {e}")
            # Return None to trigger fallback to template
            return None
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.agent is not None
    
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