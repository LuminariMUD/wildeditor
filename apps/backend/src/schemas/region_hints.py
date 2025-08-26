"""
Pydantic schemas for region hints API validation.

This module defines the request and response models for the region hints
API endpoints, ensuring data validation and serialization.
"""

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


# Enums for validation
class HintCategory(str, Enum):
    """Valid hint categories for the dynamic description engine."""
    ATMOSPHERE = "atmosphere"
    FAUNA = "fauna"
    FLORA = "flora"
    GEOGRAPHY = "geography"
    WEATHER_INFLUENCE = "weather_influence"
    RESOURCES = "resources"
    LANDMARKS = "landmarks"
    SOUNDS = "sounds"
    SCENTS = "scents"
    SEASONAL_CHANGES = "seasonal_changes"
    TIME_OF_DAY = "time_of_day"
    MYSTICAL = "mystical"


class DescriptionStyle(str, Enum):
    """Valid description styles for region profiles."""
    POETIC = "poetic"
    PRACTICAL = "practical"
    MYSTERIOUS = "mysterious"
    DRAMATIC = "dramatic"
    PASTORAL = "pastoral"


class WeatherCondition(str, Enum):
    """Valid weather conditions for hint activation."""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    STORMY = "stormy"
    LIGHTNING = "lightning"


# Base schemas
class RegionHintBase(BaseModel):
    """Base schema for region hints."""
    hint_category: HintCategory = Field(
        ...,
        description="Category of the hint for dynamic descriptions"
    )
    hint_text: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="The descriptive text to be used"
    )
    priority: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Priority 1-10, higher values are selected more often"
    )
    seasonal_weight: Optional[Dict[str, float]] = Field(
        default=None,
        description="Seasonal multipliers: {spring: 1.0, summer: 1.2, ...}"
    )
    weather_conditions: Optional[List[WeatherCondition]] = Field(
        default=["clear", "cloudy", "rainy", "stormy", "lightning"],
        description="Weather conditions when this hint applies"
    )
    time_of_day_weight: Optional[Dict[str, float]] = Field(
        default=None,
        description="Time multipliers: {dawn: 1.0, day: 0.8, ...}"
    )
    resource_triggers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Resource conditions: {vegetation: '>0.7', water: '<0.3'}"
    )
    
    @validator('seasonal_weight')
    def validate_seasonal_weight(cls, v):
        """Validate seasonal weight structure."""
        if v is not None:
            valid_seasons = {"spring", "summer", "autumn", "winter"}
            if not all(season in valid_seasons for season in v.keys()):
                raise ValueError("Seasonal weights must use: spring, summer, autumn, winter")
            if not all(0 <= weight <= 2 for weight in v.values()):
                raise ValueError("Seasonal weights must be between 0 and 2")
        return v
    
    @validator('time_of_day_weight')
    def validate_time_weight(cls, v):
        """Validate time of day weight structure."""
        if v is not None:
            valid_times = {"dawn", "morning", "midday", "afternoon", "evening", "night"}
            if not all(time in valid_times for time in v.keys()):
                raise ValueError(f"Time weights must use: {valid_times}")
            if not all(0 <= weight <= 2 for weight in v.values()):
                raise ValueError("Time weights must be between 0 and 2")
        return v


# Request schemas
class RegionHintCreate(RegionHintBase):
    """Schema for creating a new region hint."""
    ai_agent_id: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Identifier of the AI agent creating this hint"
    )


class RegionHintUpdate(BaseModel):
    """Schema for updating an existing region hint."""
    hint_text: Optional[str] = Field(
        None,
        min_length=10,
        max_length=1000,
        description="Updated descriptive text"
    )
    priority: Optional[int] = Field(
        None,
        ge=1,
        le=10,
        description="Updated priority"
    )
    seasonal_weight: Optional[Dict[str, float]] = None
    weather_conditions: Optional[List[WeatherCondition]] = None
    time_of_day_weight: Optional[Dict[str, float]] = None
    resource_triggers: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = Field(
        None,
        description="Whether the hint is active"
    )


class RegionHintBatchCreate(BaseModel):
    """Schema for creating multiple hints at once."""
    hints: List[RegionHintCreate] = Field(
        ...,
        min_items=1,
        max_items=50,
        description="List of hints to create (max 50)"
    )


# Response schemas
class RegionHintResponse(RegionHintBase):
    """Schema for region hint responses."""
    id: int
    region_vnum: int
    ai_agent_id: Optional[str] = None  # Default to None if not in DB
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Custom validation to handle missing ai_agent_id field."""
        if not hasattr(obj, 'ai_agent_id'):
            # Create a dict from the object if ai_agent_id is missing
            obj_dict = {
                'id': obj.id,
                'region_vnum': obj.region_vnum,
                'hint_category': obj.hint_category,
                'hint_text': obj.hint_text,
                'priority': obj.priority,
                'seasonal_weight': obj.seasonal_weight,
                'weather_conditions': obj.weather_conditions.split(',') if isinstance(obj.weather_conditions, str) else obj.weather_conditions,
                'time_of_day_weight': obj.time_of_day_weight,
                'resource_triggers': obj.resource_triggers,
                'ai_agent_id': None,  # Default value
                'created_at': obj.created_at,
                'updated_at': obj.updated_at,
                'is_active': obj.is_active
            }
            return super().model_validate(obj_dict, **kwargs)
        return super().model_validate(obj, **kwargs)


class RegionHintListResponse(BaseModel):
    """Schema for listing region hints."""
    hints: List[RegionHintResponse]
    total_count: int
    active_count: int
    categories: Dict[str, int] = Field(
        description="Count of hints per category"
    )


# Region Profile schemas
class RegionProfileBase(BaseModel):
    """Base schema for region profiles."""
    overall_theme: str = Field(
        ...,
        min_length=20,
        max_length=1000,
        description="Overall theme description of the region"
    )
    dominant_mood: str = Field(
        ...,
        max_length=100,
        description="Primary mood/atmosphere"
    )
    key_characteristics: List[str] = Field(
        ...,
        min_items=1,
        max_items=20,
        description="Key features of the region"
    )
    description_style: DescriptionStyle = Field(
        default=DescriptionStyle.POETIC,
        description="Preferred writing style"
    )
    complexity_level: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Complexity level 1-5 for descriptions"
    )


class RegionProfileCreate(RegionProfileBase):
    """Schema for creating a region profile."""
    ai_agent_id: Optional[str] = Field(
        default=None,
        max_length=100,
        description="AI agent identifier"
    )


class RegionProfileUpdate(BaseModel):
    """Schema for updating a region profile."""
    overall_theme: Optional[str] = None
    dominant_mood: Optional[str] = None
    key_characteristics: Optional[List[str]] = None
    description_style: Optional[DescriptionStyle] = None
    complexity_level: Optional[int] = Field(None, ge=1, le=5)


class RegionProfileResponse(RegionProfileBase):
    """Schema for region profile responses."""
    region_vnum: int
    ai_agent_id: Optional[str] = None  # Default to None if not in DB
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Custom validation to handle missing ai_agent_id field."""
        if not hasattr(obj, 'ai_agent_id'):
            # Create a dict from the object if ai_agent_id is missing
            obj_dict = {
                'region_vnum': obj.region_vnum,
                'overall_theme': obj.overall_theme,
                'dominant_mood': obj.dominant_mood,
                'key_characteristics': obj.key_characteristics,
                'description_style': obj.description_style,
                'complexity_level': obj.complexity_level,
                'ai_agent_id': None,  # Default value
                'created_at': obj.created_at,
                'updated_at': obj.updated_at
            }
            return super().model_validate(obj_dict, **kwargs)
        return super().model_validate(obj, **kwargs)


# Generation request schemas
class GenerateHintsRequest(BaseModel):
    """Schema for requesting hint generation from a description."""
    description: str = Field(
        ...,
        min_length=100,
        description="Region description to analyze for hints"
    )
    region_name: str = Field(
        ...,
        description="Name of the region"
    )
    region_type: int = Field(
        default=1,
        ge=1,
        le=4,
        description="Region type (1-4)"
    )
    target_hint_count: int = Field(
        default=15,
        ge=5,
        le=30,
        description="Target number of hints to generate"
    )
    include_profile: bool = Field(
        default=True,
        description="Also generate a region profile"
    )
    ai_model: Optional[str] = Field(
        default=None,
        description="Specific AI model to use"
    )


class GenerateHintsResponse(BaseModel):
    """Schema for hint generation response."""
    hints: List[RegionHintCreate] = Field(
        description="Generated hints ready for storage"
    )
    profile: Optional[RegionProfileCreate] = Field(
        default=None,
        description="Generated region profile if requested"
    )
    generation_metadata: Dict[str, Any] = Field(
        description="Metadata about the generation process"
    )
    ai_model_used: str = Field(
        description="AI model that generated the hints"
    )


# Analytics schemas
class HintUsageStats(BaseModel):
    """Schema for hint usage statistics."""
    hint_id: int
    usage_count: int
    last_used: Optional[datetime]
    unique_rooms: int
    average_priority: float
    most_common_weather: Optional[str]
    most_common_time: Optional[str]
    
    class Config:
        from_attributes = True


class RegionHintAnalytics(BaseModel):
    """Schema for region hint analytics."""
    region_vnum: int
    total_hints: int
    active_hints: int
    category_distribution: Dict[str, int]
    average_priority: float
    usage_stats: List[HintUsageStats]
    profile_exists: bool
    last_hint_added: Optional[datetime]