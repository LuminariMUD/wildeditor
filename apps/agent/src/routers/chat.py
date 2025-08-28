"""Chat API endpoints"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from typing import Optional, List, AsyncGenerator
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import json
import asyncio

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


@router.post("/stream")
async def stream_message(
    request: ChatMessageRequest,
    deps: dict = Depends(get_dependencies)
) -> StreamingResponse:
    """
    Send a message to the chat agent with streaming response
    
    This endpoint processes a user message and streams the assistant's response
    using Server-Sent Events (SSE).
    """
    chat_agent = deps["chat_agent"]
    session_manager = deps["session_manager"]
    
    async def generate_response() -> AsyncGenerator[str, None]:
        try:
            # Verify session exists
            if not await session_manager.session_exists(request.session_id):
                yield f"data: {json.dumps({'error': f'Session {request.session_id} not found'})}\n\n"
                return
            
            # Add user message to history
            user_message = await session_manager.add_message(
                request.session_id,
                "user",
                request.message
            )
            
            if not user_message:
                yield f"data: {json.dumps({'error': 'Failed to save user message'})}\n\n"
                return
            
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'message': 'Processing your request...'})}\n\n"
            
            # Get conversation history
            history = await session_manager.get_history_for_agent(request.session_id)
            
            # Update session context if provided
            if request.context:
                await session_manager.update_context(
                    request.session_id,
                    request.context.model_dump()
                )
            
            # Get response from agent with streaming
            try:
                # Check if agent supports streaming
                if hasattr(chat_agent, 'chat_with_history_stream'):
                    # Streaming version
                    async for chunk in chat_agent.chat_with_history_stream(
                        request.message,
                        history[:-1],  # Exclude the just-added message
                        request.context
                    ):
                        if chunk.strip():  # Only send non-empty chunks
                            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                            await asyncio.sleep(0.01)  # Small delay for better UX
                else:
                    # Fallback to non-streaming with simulated chunks
                    yield f"data: {json.dumps({'type': 'status', 'message': 'Thinking...'})}\n\n"
                    
                    response = await chat_agent.chat_with_history(
                        request.message,
                        history[:-1],
                        request.context
                    )
                    
                    # Send tool calls information first
                    if response.tool_calls:
                        for tool_call in response.tool_calls:
                            yield f"data: {json.dumps({'type': 'tool_call', 'tool_name': tool_call.get('tool_name', 'unknown'), 'tool_args': tool_call.get('args', {})})}\n\n"
                            await asyncio.sleep(0.1)  # Small delay to show tool call
                            
                            # Simulate tool result (in real streaming this would come from actual tool execution)
                            tool_name = tool_call.get('tool_name', 'unknown')
                            tool_result_data = {
                                'type': 'tool_result',
                                'tool_result': {
                                    'status': 'completed',
                                    'summary': f'Tool {tool_name} executed successfully'
                                }
                            }
                            yield f"data: {json.dumps(tool_result_data)}\n\n"
                            await asyncio.sleep(0.1)
                    
                    # Send status update
                    yield f"data: {json.dumps({'type': 'status', 'message': 'Generating response...'})}\n\n"
                    
                    # Simulate streaming by splitting response into chunks
                    words = response.message.split()
                    chunk_size = max(3, len(words) // 20)  # Roughly 20 chunks
                    
                    for i in range(0, len(words), chunk_size):
                        chunk = " ".join(words[i:i+chunk_size])
                        if i + chunk_size < len(words):
                            chunk += " "
                        
                        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                        await asyncio.sleep(0.05)  # Simulate typing delay
                    
                    # Send actions if any
                    if response.actions:
                        yield f"data: {json.dumps({'type': 'actions', 'actions': [action.model_dump() for action in response.actions]})}\n\n"
                    
                    # Add assistant response to history
                    assistant_message = await session_manager.add_message(
                        request.session_id,
                        "assistant", 
                        response.message,
                        tool_calls=response.tool_calls
                    )
                    
                    if not assistant_message:
                        logger.error("Failed to save assistant message")
            
            except Exception as e:
                logger.error(f"Error during streaming: {str(e)}")
                yield f"data: {json.dumps({'error': f'Failed to process message: {str(e)}'})}\n\n"
                return
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'complete', 'message': 'Response complete'})}\n\n"
            
        except Exception as e:
            logger.error(f"Error in stream generator: {str(e)}")
            yield f"data: {json.dumps({'error': f'Stream error: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )