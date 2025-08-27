"""Session management API endpoints"""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class CreateSessionRequest(BaseModel):
    """Create session request model"""
    user_id: Optional[str] = Field(None, description="User identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")


class CreateSessionResponse(BaseModel):
    """Create session response model"""
    session_id: str
    created_at: datetime
    expires_at: datetime


class SessionInfoResponse(BaseModel):
    """Session info response model"""
    session_id: str
    user_id: Optional[str]
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    message_count: int
    context: Dict[str, Any]
    metadata: Dict[str, Any]


class UpdateContextRequest(BaseModel):
    """Update context request model"""
    context: Dict[str, Any] = Field(..., description="Context to update")


async def get_session_manager(request: Request):
    """Get session manager from request"""
    return request.app.state.session_manager


@router.post("/", response_model=CreateSessionResponse)
async def create_session(
    request: CreateSessionRequest,
    session_manager = Depends(get_session_manager)
) -> CreateSessionResponse:
    """
    Create a new chat session
    
    Creates a new session for tracking conversation history and context.
    """
    try:
        # Create session
        session_id = await session_manager.create_session(
            user_id=request.user_id,
            initial_context=request.metadata
        )
        
        # Calculate expiry
        from datetime import timedelta
        expires_at = datetime.utcnow() + timedelta(seconds=session_manager.ttl)
        
        return CreateSessionResponse(
            session_id=session_id,
            created_at=datetime.utcnow(),
            expires_at=expires_at
        )
        
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/{session_id}", response_model=SessionInfoResponse)
async def get_session_info(
    session_id: str,
    session_manager = Depends(get_session_manager)
) -> SessionInfoResponse:
    """
    Get session information
    
    Returns detailed information about the specified session.
    """
    try:
        # Get session data
        session_data = await session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Calculate expiry
        from datetime import timedelta
        expires_at = session_data.metadata.last_activity + timedelta(seconds=session_manager.ttl)
        
        return SessionInfoResponse(
            session_id=session_data.metadata.session_id,
            user_id=session_data.metadata.user_id,
            created_at=session_data.metadata.created_at,
            last_activity=session_data.metadata.last_activity,
            expires_at=expires_at,
            message_count=session_data.metadata.message_count,
            context=session_data.context,
            metadata=session_data.metadata.context
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session info: {str(e)}")


@router.put("/{session_id}/context")
async def update_session_context(
    session_id: str,
    request: UpdateContextRequest,
    session_manager = Depends(get_session_manager)
) -> dict:
    """
    Update session context
    
    Updates the context information for the specified session.
    This is useful for maintaining editor state across messages.
    """
    try:
        success = await session_manager.update_context(session_id, request.context)
        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "message": "Context updated successfully",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating context: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update context: {str(e)}")


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    session_manager = Depends(get_session_manager)
) -> dict:
    """
    Delete a session
    
    Permanently deletes the session and all associated data.
    """
    try:
        if not await session_manager.session_exists(session_id):
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        await session_manager.delete_session(session_id)
        
        return {
            "message": "Session deleted successfully",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")


@router.post("/{session_id}/extend")
async def extend_session(
    session_id: str,
    session_manager = Depends(get_session_manager)
) -> dict:
    """
    Extend session TTL
    
    Extends the session expiration time by the configured TTL.
    """
    try:
        if not await session_manager.session_exists(session_id):
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        await session_manager.storage.extend_ttl(
            f"session:{session_id}",
            session_manager.ttl
        )
        
        return {
            "message": "Session TTL extended",
            "session_id": session_id,
            "ttl_seconds": session_manager.ttl
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extending session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to extend session: {str(e)}")