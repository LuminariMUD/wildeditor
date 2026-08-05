"""Session management API endpoints"""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from datetime import UTC, datetime, timedelta
import logging
from wildeditor_auth import Principal

from security import require_human_editor

logger = logging.getLogger(__name__)

router = APIRouter()


class CreateSessionRequest(BaseModel):
    """Create session request model"""

    model_config = ConfigDict(extra="forbid")

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
    session_manager = Depends(get_session_manager),
    principal: Principal = Depends(require_human_editor),
) -> CreateSessionResponse:
    """
    Create a new chat session
    
    Creates a new session for tracking conversation history and context.
    """
    try:
        # Create session
        session_id = await session_manager.create_session(
            user_id=principal.subject,
            initial_context=request.metadata
        )
        
        # Calculate expiry
        expires_at = datetime.now(UTC) + timedelta(seconds=session_manager.ttl)
        
        return CreateSessionResponse(
            session_id=session_id,
            created_at=datetime.now(UTC),
            expires_at=expires_at
        )
        
    except Exception as exc:
        logger.error("Failed to create a chat session (%s)", type(exc).__name__)
        raise HTTPException(status_code=500, detail="Failed to create session.") from exc


@router.get("/{session_id}", response_model=SessionInfoResponse)
async def get_session_info(
    session_id: str,
    session_manager = Depends(get_session_manager),
    principal: Principal = Depends(require_human_editor),
) -> SessionInfoResponse:
    """
    Get session information
    
    Returns detailed information about the specified session.
    """
    try:
        # Get session data
        session_data = await session_manager.get_owned_session(
            session_id,
            principal.subject,
        )
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Calculate expiry
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
    except Exception as exc:
        logger.error("Failed to read a chat session (%s)", type(exc).__name__)
        raise HTTPException(status_code=500, detail="Failed to get session info.") from exc


@router.put("/{session_id}/context")
async def update_session_context(
    session_id: str,
    request: UpdateContextRequest,
    session_manager = Depends(get_session_manager),
    principal: Principal = Depends(require_human_editor),
) -> dict:
    """
    Update session context
    
    Updates the context information for the specified session.
    This is useful for maintaining editor state across messages.
    """
    try:
        owned_session = await session_manager.get_owned_session(
            session_id,
            principal.subject,
        )
        if not owned_session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        success = await session_manager.update_context(session_id, request.context)
        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "message": "Context updated successfully",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to update chat session context (%s)", type(exc).__name__)
        raise HTTPException(status_code=500, detail="Failed to update context.") from exc


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    session_manager = Depends(get_session_manager),
    principal: Principal = Depends(require_human_editor),
) -> dict:
    """
    Delete a session
    
    Permanently deletes the session and all associated data.
    """
    try:
        if not await session_manager.get_owned_session(session_id, principal.subject):
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        await session_manager.delete_session(session_id)
        
        return {
            "message": "Session deleted successfully",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to delete a chat session (%s)", type(exc).__name__)
        raise HTTPException(status_code=500, detail="Failed to delete session.") from exc


@router.post("/{session_id}/extend")
async def extend_session(
    session_id: str,
    session_manager = Depends(get_session_manager),
    principal: Principal = Depends(require_human_editor),
) -> dict:
    """
    Extend session TTL
    
    Extends the session expiration time by the configured TTL.
    """
    try:
        if not await session_manager.get_owned_session(session_id, principal.subject):
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
    except Exception as exc:
        logger.error("Failed to extend a chat session (%s)", type(exc).__name__)
        raise HTTPException(status_code=500, detail="Failed to extend session.") from exc
