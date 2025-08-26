"""
API endpoints for managing region hints and profiles.

This module provides RESTful endpoints for creating, reading, updating,
and deleting region hints and profiles, as well as generating hints
from region descriptions using AI.

Endpoints:
    - GET /api/regions/{vnum}/hints - List all hints for a region
    - POST /api/regions/{vnum}/hints - Create hints for a region
    - PUT /api/regions/{vnum}/hints/{id} - Update a specific hint
    - DELETE /api/regions/{vnum}/hints/{id} - Delete a hint
    - GET /api/regions/{vnum}/profile - Get region profile
    - POST /api/regions/{vnum}/profile - Create/update region profile
    - POST /api/regions/{vnum}/hints/generate - Generate hints from description
    - GET /api/regions/{vnum}/hints/analytics - Get hint usage analytics
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime
import logging

from ..config.config_database import get_db
from ..models.region import Region
from ..models.region_hints import RegionHint, RegionProfile, HintUsageLog
from ..schemas.region_hints import (
    RegionHintCreate,
    RegionHintUpdate,
    RegionHintBatchCreate,
    RegionHintResponse,
    RegionHintListResponse,
    RegionProfileCreate,
    RegionProfileUpdate,
    RegionProfileResponse,
    GenerateHintsRequest,
    GenerateHintsResponse,
    RegionHintAnalytics,
    HintUsageStats,
    HintCategory
)

router = APIRouter()
logger = logging.getLogger(__name__)


# ============================================================================
# HINT ENDPOINTS
# ============================================================================

@router.get("/{vnum}/hints", response_model=RegionHintListResponse)
def list_region_hints(
    vnum: int,
    category: Optional[HintCategory] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    min_priority: Optional[int] = Query(None, ge=1, le=10, description="Minimum priority"),
    db: Session = Depends(get_db)
):
    """
    List all hints for a specific region.
    
    Args:
        vnum: Region VNUM
        category: Optional category filter
        is_active: Optional active status filter
        min_priority: Optional minimum priority filter
        db: Database session
    
    Returns:
        RegionHintListResponse with hints and metadata
    """
    try:
        # Build query - no need to check if region exists, just get hints
        query = db.query(RegionHint).filter(RegionHint.region_vnum == vnum)
        
        if category:
            query = query.filter(RegionHint.hint_category == category)
        
        if is_active is not None:
            query = query.filter(RegionHint.is_active == is_active)
        
        if min_priority:
            query = query.filter(RegionHint.priority >= min_priority)
        
        # Get hints
        hints = query.order_by(RegionHint.priority.desc(), RegionHint.created_at.desc()).all()
        
        # Calculate category distribution
        category_counts = {}
        active_count = 0
        for hint in hints:
            category_counts[hint.hint_category] = category_counts.get(hint.hint_category, 0) + 1
            if hint.is_active:
                active_count += 1
        
        # Convert hints to response format manually to avoid validation issues
        hint_responses = []
        for hint in hints:
            hint_dict = {
                'id': hint.id,
                'region_vnum': hint.region_vnum,
                'hint_category': hint.hint_category,
                'hint_text': hint.hint_text,
                'priority': hint.priority,
                'seasonal_weight': hint.seasonal_weight,
                'weather_conditions': hint.weather_conditions.split(',') if hint.weather_conditions else [],
                'time_of_day_weight': hint.time_of_day_weight,
                'resource_triggers': hint.resource_triggers,
                'agent_id': hint.agent_id,
                'created_at': hint.created_at,
                'updated_at': hint.updated_at,
                'is_active': hint.is_active
            }
            hint_responses.append(hint_dict)
        
        return RegionHintListResponse(
            hints=hint_responses,
            total_count=len(hints),
            active_count=active_count,
            categories=category_counts
        )
    except Exception as e:
        import traceback
        error_detail = f"Error fetching hints for region {vnum}: {str(e)}\nTraceback: {traceback.format_exc()}"
        logger.error(error_detail)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.post("/{vnum}/hints", response_model=List[RegionHintResponse], status_code=status.HTTP_201_CREATED)
def create_region_hints(
    vnum: int,
    request: RegionHintBatchCreate,
    db: Session = Depends(get_db)
):
    """
    Create one or more hints for a region.
    
    Args:
        vnum: Region VNUM
        request: Batch of hints to create
        db: Database session
    
    Returns:
        List of created hints
    """
    # Check if region exists
    region = db.query(Region).filter(Region.vnum == vnum).first()
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region with vnum {vnum} not found"
        )
    
    created_hints = []
    
    try:
        for hint_data in request.hints:
            # Convert weather conditions list to comma-separated string
            weather_str = ",".join(hint_data.weather_conditions) if hint_data.weather_conditions else "clear,cloudy,rainy,stormy,lightning"
            
            hint = RegionHint(
                region_vnum=vnum,
                hint_category=hint_data.hint_category,
                hint_text=hint_data.hint_text,
                priority=hint_data.priority,
                seasonal_weight=hint_data.seasonal_weight,
                weather_conditions=weather_str,
                time_of_day_weight=hint_data.time_of_day_weight,
                resource_triggers=hint_data.resource_triggers
                # ai_agent_id=hint_data.ai_agent_id  # Temporarily disabled - column not in production yet
            )
            db.add(hint)
            created_hints.append(hint)
        
        db.commit()
        
        # Refresh to get IDs
        for hint in created_hints:
            db.refresh(hint)
        
        return [RegionHintResponse.model_validate(hint) for hint in created_hints]
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create hints: {str(e)}"
        )


@router.put("/{vnum}/hints/{hint_id}", response_model=RegionHintResponse)
def update_region_hint(
    vnum: int,
    hint_id: int,
    request: RegionHintUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a specific region hint.
    
    Args:
        vnum: Region VNUM
        hint_id: Hint ID
        request: Update data
        db: Database session
    
    Returns:
        Updated hint
    """
    # Get hint
    hint = db.query(RegionHint).filter(
        and_(
            RegionHint.id == hint_id,
            RegionHint.region_vnum == vnum
        )
    ).first()
    
    if not hint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hint {hint_id} not found for region {vnum}"
        )
    
    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    
    # Convert weather conditions if provided
    if 'weather_conditions' in update_data and update_data['weather_conditions']:
        update_data['weather_conditions'] = ",".join(update_data['weather_conditions'])
    
    for field, value in update_data.items():
        setattr(hint, field, value)
    
    try:
        db.commit()
        db.refresh(hint)
        return RegionHintResponse.model_validate(hint)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update hint: {str(e)}"
        )


@router.delete("/{vnum}/hints", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_region_hints(
    vnum: int,
    db: Session = Depends(get_db)
):
    """
    Delete all hints for a region.
    
    Args:
        vnum: Region VNUM
        db: Database session
    
    Returns:
        No content on success
    """
    # Check if region exists
    region = db.query(Region).filter(Region.vnum == vnum).first()
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region with vnum {vnum} not found"
        )
    
    try:
        # Delete all hints for this region
        deleted_count = db.query(RegionHint).filter(
            RegionHint.region_vnum == vnum
        ).delete()
        
        db.commit()
        
        # Log the deletion for audit purposes
        logger.info(f"Deleted {deleted_count} hints for region {vnum}")
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete hints: {str(e)}"
        )


@router.delete("/{vnum}/hints/{hint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_region_hint(
    vnum: int,
    hint_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific region hint.
    
    Args:
        vnum: Region VNUM
        hint_id: Hint ID
        db: Database session
    """
    # Get hint
    hint = db.query(RegionHint).filter(
        and_(
            RegionHint.id == hint_id,
            RegionHint.region_vnum == vnum
        )
    ).first()
    
    if not hint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hint {hint_id} not found for region {vnum}"
        )
    
    try:
        db.delete(hint)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete hint: {str(e)}"
        )


# ============================================================================
# PROFILE ENDPOINTS
# ============================================================================

@router.get("/{vnum}/profile", response_model=RegionProfileResponse)
def get_region_profile(
    vnum: int,
    db: Session = Depends(get_db)
):
    """
    Get the personality profile for a region.
    
    Args:
        vnum: Region VNUM
        db: Database session
    
    Returns:
        Region profile if it exists
    """
    profile = db.query(RegionProfile).filter(RegionProfile.region_vnum == vnum).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile not found for region {vnum}"
        )
    
    return RegionProfileResponse.model_validate(profile)


@router.post("/{vnum}/profile", response_model=RegionProfileResponse)
def create_or_update_region_profile(
    vnum: int,
    request: RegionProfileCreate,
    db: Session = Depends(get_db)
):
    """
    Create or update a region's personality profile.
    
    Args:
        vnum: Region VNUM
        request: Profile data
        db: Database session
    
    Returns:
        Created or updated profile
    """
    # Check if region exists
    region = db.query(Region).filter(Region.vnum == vnum).first()
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region with vnum {vnum} not found"
        )
    
    # Check if profile exists
    profile = db.query(RegionProfile).filter(RegionProfile.region_vnum == vnum).first()
    
    try:
        if profile:
            # Update existing
            for field, value in request.model_dump(exclude_unset=True).items():
                setattr(profile, field, value)
        else:
            # Create new
            profile = RegionProfile(
                region_vnum=vnum,
                **request.model_dump()
            )
            db.add(profile)
        
        db.commit()
        db.refresh(profile)
        return RegionProfileResponse.model_validate(profile)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save profile: {str(e)}"
        )


# ============================================================================
# GENERATION ENDPOINTS
# ============================================================================

@router.post("/{vnum}/hints/generate", response_model=GenerateHintsResponse)
async def generate_region_hints(
    vnum: int,
    request: GenerateHintsRequest,
    db: Session = Depends(get_db)
):
    """
    Generate hints from a region description using AI.
    
    This endpoint analyzes the provided description and generates
    categorized hints suitable for the dynamic description engine.
    
    Args:
        vnum: Region VNUM
        request: Generation parameters including description
        db: Database session
    
    Returns:
        Generated hints and optional profile
    """
    # Check if region exists
    region = db.query(Region).filter(Region.vnum == vnum).first()
    if not region:
        # For testing, we might want to create the region
        # For now, just validate it exists
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region with vnum {vnum} not found"
        )
    
    # TODO: Call MCP service to generate hints
    # For now, return a mock response for testing
    
    mock_hints = [
        RegionHintCreate(
            hint_category=HintCategory.ATMOSPHERE,
            hint_text="Crystalline formations cast prismatic light throughout the cavern, creating rainbow patterns on the walls.",
            priority=8,
            seasonal_weight={"spring": 1.0, "summer": 1.0, "autumn": 1.0, "winter": 1.0},
            weather_conditions=["clear", "cloudy"]
            # ai_agent_id="test_generator"
        ),
        RegionHintCreate(
            hint_category=HintCategory.SOUNDS,
            hint_text="The gentle ping of water droplets echoes musically off the crystal surfaces.",
            priority=7,
            time_of_day_weight={"dawn": 0.8, "day": 1.0, "dusk": 0.9, "night": 1.0}
            # ai_agent_id="test_generator"
        ),
        RegionHintCreate(
            hint_category=HintCategory.FLORA,
            hint_text="Bioluminescent fungi cling to the crystal formations, their soft blue glow pulsing gently.",
            priority=6,
            weather_conditions=["cloudy", "rainy"]
            # ai_agent_id="test_generator"
        )
    ]
    
    mock_profile = None
    if request.include_profile:
        mock_profile = RegionProfileCreate(
            overall_theme="An underground crystal cavern filled with natural crystal formations and bioluminescent life",
            dominant_mood="mystical_wonder",
            key_characteristics=["crystal_formations", "prismatic_light", "echo_chamber", "bioluminescent_fungi"],
            description_style="mysterious",
            complexity_level=4
            # ai_agent_id="test_generator"
        )
    
    return GenerateHintsResponse(
        hints=mock_hints,
        profile=mock_profile,
        generation_metadata={
            "description_length": len(request.description),
            "region_type": request.region_type,
            "target_hints": request.target_hint_count,
            "actual_hints": len(mock_hints)
        },
        ai_model_used="test_generator"
    )


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/{vnum}/hints/analytics", response_model=RegionHintAnalytics)
def get_hint_analytics(
    vnum: int,
    db: Session = Depends(get_db)
):
    """
    Get usage analytics for a region's hints.
    
    Args:
        vnum: Region VNUM
        db: Database session
    
    Returns:
        Analytics data including usage statistics
    """
    # Get all hints for region
    hints = db.query(RegionHint).filter(RegionHint.region_vnum == vnum).all()
    
    if not hints:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hints found for region {vnum}"
        )
    
    # Calculate statistics
    total_hints = len(hints)
    active_hints = sum(1 for h in hints if h.is_active)
    
    # Category distribution
    category_dist = {}
    total_priority = 0
    for hint in hints:
        category_dist[hint.hint_category] = category_dist.get(hint.hint_category, 0) + 1
        total_priority += hint.priority
    
    avg_priority = total_priority / total_hints if total_hints > 0 else 0
    
    # Get usage statistics for each hint
    usage_stats = []
    for hint in hints[:10]:  # Limit to top 10 for performance
        usage_count = db.query(func.count(HintUsageLog.id)).filter(
            HintUsageLog.hint_id == hint.id
        ).scalar()
        
        last_used = db.query(func.max(HintUsageLog.used_at)).filter(
            HintUsageLog.hint_id == hint.id
        ).scalar()
        
        unique_rooms = db.query(func.count(func.distinct(HintUsageLog.room_vnum))).filter(
            HintUsageLog.hint_id == hint.id
        ).scalar()
        
        usage_stats.append(HintUsageStats(
            hint_id=hint.id,
            usage_count=usage_count or 0,
            last_used=last_used,
            unique_rooms=unique_rooms or 0,
            average_priority=hint.priority,
            most_common_weather=None,  # TODO: Implement if needed
            most_common_time=None  # TODO: Implement if needed
        ))
    
    # Check if profile exists
    profile_exists = db.query(RegionProfile).filter(
        RegionProfile.region_vnum == vnum
    ).first() is not None
    
    # Get last hint added date
    last_hint_added = db.query(func.max(RegionHint.created_at)).filter(
        RegionHint.region_vnum == vnum
    ).scalar()
    
    return RegionHintAnalytics(
        region_vnum=vnum,
        total_hints=total_hints,
        active_hints=active_hints,
        category_distribution=category_dist,
        average_priority=avg_priority,
        usage_stats=usage_stats,
        profile_exists=profile_exists,
        last_hint_added=last_hint_added
    )