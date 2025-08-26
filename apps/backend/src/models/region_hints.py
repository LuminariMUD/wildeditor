"""
SQLAlchemy models for the region hints system.

This module defines the database models for storing AI-generated hints
that enhance the dynamic description engine with contextual details.

Tables:
    - RegionHint: Stores categorized descriptive hints for regions
    - RegionProfile: Stores personality/theme profiles for regions
    - HintUsageLog: Tracks hint usage for analytics (optional)
"""

from sqlalchemy import (
    Column, Integer, String, Text, Enum, Boolean, 
    ForeignKey, JSON, TIMESTAMP, DECIMAL, Index
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..config.config_database import Base


class RegionHint(Base):
    """
    Model for storing AI-generated descriptive hints for regions.
    
    Each hint is categorized and includes metadata for contextual usage
    based on weather, season, time of day, and resource states.
    
    Attributes:
        id: Primary key
        region_vnum: Foreign key to region_data table
        hint_category: Category of the hint (atmosphere, fauna, flora, etc.)
        hint_text: The actual descriptive text
        priority: 1-10, higher means more likely to be used
        seasonal_weight: JSON dict with seasonal multipliers
        weather_conditions: Set of weather conditions when hint applies
        time_of_day_weight: JSON dict with time-based multipliers
        resource_triggers: JSON conditions for resource-based activation
        ai_agent_id: Identifier of the AI agent that created this hint
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        is_active: Whether this hint is currently active
    """
    __tablename__ = "region_hints"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to region
    region_vnum = Column(
        Integer, 
        ForeignKey('region_data.vnum', ondelete='CASCADE'),
        nullable=False,
        doc="VNUM of the region this hint belongs to"
    )
    
    # Hint categorization
    hint_category = Column(
        Enum(
            'atmosphere',         # General atmospheric descriptions
            'fauna',             # Animal life descriptions
            'flora',             # Plant life descriptions
            'geography',         # Landform and geological features
            'weather_influence', # How weather affects this region
            'resources',         # Resource availability hints
            'landmarks',         # Notable landmarks or features
            'sounds',            # Ambient sounds
            'scents',            # Ambient smells
            'seasonal_changes',  # How the region changes with seasons
            'time_of_day',       # Day/night variations
            'mystical'           # Magical or mystical elements
        ),
        nullable=False,
        doc="Category of hint for the dynamic description engine"
    )
    
    # Content
    hint_text = Column(
        Text, 
        nullable=False,
        doc="The descriptive text that will be used in dynamic descriptions"
    )
    
    # Usage control
    priority = Column(
        Integer, 
        default=5,
        doc="Priority 1-10, higher values are more likely to be selected"
    )
    
    # Contextual weights (JSON)
    seasonal_weight = Column(
        JSON, 
        default=None,
        doc='Seasonal multipliers e.g. {"spring": 1.0, "summer": 1.2, "autumn": 0.8, "winter": 0.5}'
    )
    
    # Weather conditions (MySQL SET type represented as String)
    weather_conditions = Column(
        String(255),
        default='clear,cloudy,rainy,stormy,lightning',
        doc="Comma-separated weather conditions when this hint applies"
    )
    
    # Time-based weights (JSON)
    time_of_day_weight = Column(
        JSON,
        default=None,
        doc='Time multipliers e.g. {"dawn": 1.0, "day": 1.0, "dusk": 1.2, "night": 0.8}'
    )
    
    # Resource triggers (JSON)
    resource_triggers = Column(
        JSON,
        default=None,
        doc='Resource conditions e.g. {"vegetation": ">0.7", "water": "<0.3"}'
    )
    
    # Metadata
    # ai_agent_id = Column(
    #     String(100),
    #     default=None,
    #     doc="Identifier of the AI agent/model that created this hint"
    # )  # Temporarily disabled - column not in production DB yet
    
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        doc="When this hint was created"
    )
    
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        doc="When this hint was last updated"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        doc="Whether this hint is currently active for use"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_region_category', 'region_vnum', 'hint_category'),
        Index('idx_priority', 'priority'),
        Index('idx_active', 'is_active'),
        Index('idx_created', 'created_at'),
    )


class RegionProfile(Base):
    """
    Model for storing AI-generated personality profiles for regions.
    
    Each region can have a profile that defines its overall character,
    mood, and key characteristics to ensure consistency in descriptions.
    
    Attributes:
        region_vnum: Primary key and foreign key to region_data
        overall_theme: Text description of the region's overall theme
        dominant_mood: The primary mood/atmosphere of the region
        key_characteristics: JSON array of key features
        description_style: Preferred writing style for this region
        complexity_level: How detailed descriptions should be (1-5)
        ai_agent_id: Identifier of the AI agent that created this profile
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    __tablename__ = "region_profiles"
    
    # Primary key (also foreign key)
    region_vnum = Column(
        Integer,
        ForeignKey('region_data.vnum', ondelete='CASCADE'),
        primary_key=True,
        doc="VNUM of the region this profile describes"
    )
    
    # Theme and mood
    overall_theme = Column(
        Text,
        doc="Overall theme description e.g. 'Ancient mystical forest with elven influences'"
    )
    
    dominant_mood = Column(
        String(100),
        doc="Primary mood e.g. 'Serene, mysterious, slightly melancholic'"
    )
    
    # Characteristics (JSON)
    key_characteristics = Column(
        JSON,
        doc='Key features as JSON array e.g. ["ancient_trees", "elven_ruins", "magical_springs"]'
    )
    
    # Style preferences
    description_style = Column(
        Enum('poetic', 'practical', 'mysterious', 'dramatic', 'pastoral'),
        default='poetic',
        doc="Preferred writing style for this region's descriptions"
    )
    
    complexity_level = Column(
        Integer,
        default=3,
        doc="Complexity level 1-5, how detailed descriptions should be"
    )
    
    # Metadata
    # ai_agent_id = Column(
    #     String(100),
    #     doc="Identifier of the AI agent/model that created this profile"
    # )  # Temporarily disabled - column not in production DB yet
    
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        doc="When this profile was created"
    )
    
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        doc="When this profile was last updated"
    )


class HintUsageLog(Base):
    """
    Model for tracking hint usage in dynamic descriptions.
    
    This table logs when hints are actually used, allowing for
    analytics and optimization of hint selection algorithms.
    
    Attributes:
        id: Primary key
        hint_id: Foreign key to region_hints table
        room_vnum: The room where the hint was used
        player_id: Optional player ID for personalized tracking
        used_at: Timestamp when the hint was used
        weather_condition: Weather at time of use
        season: Season at time of use
        time_of_day: Time of day at use
        resource_state: JSON snapshot of resource levels
    """
    __tablename__ = "hint_usage_log"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to hint
    hint_id = Column(
        Integer,
        ForeignKey('region_hints.id', ondelete='CASCADE'),
        nullable=False,
        doc="ID of the hint that was used"
    )
    
    # Usage context
    room_vnum = Column(
        Integer,
        nullable=False,
        doc="VNUM of the room where hint was displayed"
    )
    
    player_id = Column(
        Integer,
        default=None,
        doc="Optional player ID for personalized tracking"
    )
    
    # Timestamp
    used_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        doc="When this hint was displayed"
    )
    
    # Environmental context
    weather_condition = Column(
        String(20),
        doc="Weather condition at time of use"
    )
    
    season = Column(
        String(10),
        doc="Season at time of use"
    )
    
    time_of_day = Column(
        String(10),
        doc="Time of day at use (dawn, day, dusk, night)"
    )
    
    # Resource state (JSON)
    resource_state = Column(
        JSON,
        default=None,
        doc="Snapshot of resource levels when hint was used"
    )
    
    # Indexes for analytics
    __table_args__ = (
        Index('idx_hint_usage', 'hint_id', 'used_at'),
        Index('idx_room_usage', 'room_vnum', 'used_at'),
    )