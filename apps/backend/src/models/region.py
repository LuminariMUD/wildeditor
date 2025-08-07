from sqlalchemy import Column, Integer, String, DateTime
from geoalchemy2 import Geometry
from ..config.config_database import Base

class Region(Base):
    __tablename__ = "region_data"
    
    vnum = Column(Integer, primary_key=True)  # Primary key, not auto-increment
    zone_vnum = Column(Integer, nullable=False)
    name = Column(String(50), nullable=True)  # Nullable as per database schema
    region_type = Column(Integer, nullable=False)  # 1=Geographic, 2=Encounter, 3=Sector Transform, 4=Sector Override
    region_polygon = Column(Geometry('POLYGON'), nullable=True)  # MySQL spatial polygon type - nullable
    region_props = Column(String(255), nullable=False, default="0")  # String to support mob vnums for encounters, required by game
    region_reset_data = Column(String(255), nullable=False, default="")  # Not null but allows empty strings
    region_reset_time = Column(DateTime, nullable=True)  # Make nullable to handle MySQL zero dates gracefully
