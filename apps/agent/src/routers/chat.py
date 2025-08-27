"""Chat API endpoints"""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from agent.chat_agent import EditorContext, AssistantResponse
from session.manager import Message

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatMessageRequest(BaseModel):
    """Chat message request model"""
    message: str = Field(..., description="The user's message")
    session_id: str = Field(..., description="Session ID")
    context: Optional[EditorContext] = Field(None, description="Editor context")
    stream: bool = Field(default=False, description="Enable streaming response")


class ChatMessageResponse(BaseModel):
    """Chat message response model"""
    response: AssistantResponse
    session_id: str
    message_id: str
    timestamp: datetime


class ChatHistoryResponse(BaseModel):
    """Chat history response model"""
    messages: List[Message]
    total_count: int
    session_id: str
    has_more: bool


async def get_dependencies(request: Request):
    """Get application dependencies from request"""
    return {
        "chat_agent": request.app.state.chat_agent,
        "session_manager": request.app.state.session_manager
    }


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    deps: dict = Depends(get_dependencies)
) -> ChatMessageResponse:
    """
    Send a message to the chat agent
    
    This endpoint processes a user message and returns the assistant's response.
    It maintains conversation history within the session.
    """
    chat_agent = deps["chat_agent"]
    session_manager = deps["session_manager"]
    
    try:
        # Verify session exists
        if not await session_manager.session_exists(request.session_id):
            raise HTTPException(status_code=404, detail=f"Session {request.session_id} not found")
        
        # Add user message to history
        user_message = await session_manager.add_message(
            request.session_id,
            "user",
            request.message
        )
        
        if not user_message:
            raise HTTPException(status_code=500, detail="Failed to save user message")
        
        # Get conversation history
        history = await session_manager.get_history_for_agent(request.session_id)
        
        # Update session context if provided
        if request.context:
            await session_manager.update_context(
                request.session_id,
                request.context.model_dump()
            )
        
        # Get response from agent
        response = await chat_agent.chat_with_history(
            request.message,
            history[:-1],  # Exclude the just-added message
            request.context
        )
        
        # Add assistant response to history
        assistant_message = await session_manager.add_message(
            request.session_id,
            "assistant",
            response.message,
            tool_calls=response.tool_calls
        )
        
        if not assistant_message:
            logger.error("Failed to save assistant message")
        
        return ChatMessageResponse(
            response=response,
            session_id=request.session_id,
            message_id=assistant_message.id if assistant_message else "",
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.get("/history", response_model=ChatHistoryResponse)
async def get_history(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
    deps: dict = Depends(get_dependencies)
) -> ChatHistoryResponse:
    """
    Get chat history for a session
    
    Returns the message history for the specified session with pagination support.
    """
    session_manager = deps["session_manager"]
    
    try:
        # Get session data
        session_data = await session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Get messages with pagination
        messages = await session_manager.get_history(session_id, limit, offset)
        total_count = session_data.metadata.message_count
        
        return ChatHistoryResponse(
            messages=messages,
            total_count=total_count,
            session_id=session_id,
            has_more=(offset + len(messages)) < total_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.delete("/history/{session_id}")
async def clear_history(
    session_id: str,
    deps: dict = Depends(get_dependencies)
) -> dict:
    """
    Clear chat history for a session
    
    Removes all messages from the session while preserving the session itself.
    """
    session_manager = deps["session_manager"]
    
    try:
        success = await session_manager.clear_history(session_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "message": "Chat history cleared",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}")