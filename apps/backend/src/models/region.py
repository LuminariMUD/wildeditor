from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Boolean, DECIMAL, TIMESTAMP
from geoalchemy2 import Geometry
from ..config.config_database import Base


class Region(Base):
    __tablename__ = "region_data"

    vnum = Column(Integer, primary_key=True)  # Primary key, not auto-increment
    zone_vnum = Column(Integer, nullable=False)
    name = Column(String(50), nullable=True)  # Nullable as per database schema
    region_type = Column(Integer, nullable=False)  # 1=Geographic, 2=Encounter, 3=Sector Transform, 4=Sector Override
    region_polygon = Column(Geometry('POLYGON'), nullable=True)  # MySQL spatial polygon type - nullable
    region_props = Column(Integer, nullable=True)  # Integer as per actual database schema
    region_reset_data = Column(String(255), nullable=False, default="")  # Not null but allows empty strings
    region_reset_time = Column(DateTime, nullable=True)  # Make nullable to handle MySQL zero dates gracefully
    
    # New description fields
    region_description = Column(Text, nullable=True)  # Long text field for comprehensive descriptions
    description_version = Column(Integer, nullable=True, default=1)
    ai_agent_source = Column(String(100), nullable=True)  # Source of AI-generated description
    last_description_update = Column(TIMESTAMP, nullable=True)  # Auto-updated on change
    description_style = Column(Enum('poetic', 'practical', 'mysterious', 'dramatic', 'pastoral'), nullable=True, default='poetic')
    description_length = Column(Enum('brief', 'moderate', 'detailed', 'extensive'), nullable=True, default='moderate')
    
    # Description metadata flags
    has_historical_context = Column(Boolean, nullable=True, default=False)
    has_resource_info = Column(Boolean, nullable=True, default=False)
    has_wildlife_info = Column(Boolean, nullable=True, default=False)
    has_geological_info = Column(Boolean, nullable=True, default=False)
    has_cultural_info = Column(Boolean, nullable=True, default=False)
    
    # Quality and review fields
    description_quality_score = Column(DECIMAL(3, 2), nullable=True)  # 0.00 to 9.99
    requires_review = Column(Boolean, nullable=True, default=False)
    is_approved = Column(Boolean, nullable=True, default=False)
