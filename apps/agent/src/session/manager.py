"""Session management for chat conversations"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import uuid
import logging
from .storage import SessionStorage, create_storage

logger = logging.getLogger(__name__)


class SessionMetadata(BaseModel):
    """Session metadata"""
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = 0
    context: Dict[str, Any] = Field(default_factory=dict)


class Message(BaseModel):
    """Chat message model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionData(BaseModel):
    """Complete session data"""
    metadata: SessionMetadata
    messages: List[Message] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)


class SessionManager:
    """Manages chat sessions and message history"""
    
    def __init__(self, storage: SessionStorage, ttl: int = 86400):
        """
        Initialize session manager
        
        Args:
            storage: Storage backend
            ttl: Session TTL in seconds (default 24 hours)
        """
        self.storage = storage
        self.ttl = ttl
        logger.info(f"Initialized SessionManager with TTL {ttl}s")
    
    async def create_session(
        self, 
        user_id: Optional[str] = None,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new session
        
        Args:
            user_id: Optional user identifier
            initial_context: Optional initial context
            
        Returns:
            Session ID
        """
        # Generate session ID
        session_id = f"{user_id or 'anon'}_{uuid.uuid4().hex[:8]}"
        
        # Create session metadata
        metadata = SessionMetadata(
            session_id=session_id,
            user_id=user_id,
            context=initial_context or {}
        )
        
        # Create session data
        session_data = SessionData(
            metadata=metadata,
            context=initial_context or {}
        )
        
        # Save to storage
        await self.storage.save(
            f"session:{session_id}",
            session_data.model_dump(mode="json"),
            self.ttl
        )
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Get session data
        
        Args:
            session_id: Session ID
            
        Returns:
            SessionData or None if not found
        """
        data = await self.storage.load(f"session:{session_id}")
        if data:
            return SessionData(**data)
        return None
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Message]:
        """
        Add a message to session history
        
        Args:
            session_id: Session ID
            role: Message role (user, assistant, system)
            content: Message content
            tool_calls: Optional tool calls
            metadata: Optional metadata
            
        Returns:
            Created message or None if session not found
        """
        # Get session
        session_data = await self.get_session(session_id)
        if not session_data:
            logger.warning(f"Session {session_id} not found")
            return None
        
        # Create message
        message = Message(
            role=role,
            content=content,
            tool_calls=tool_calls,
            metadata=metadata or {}
        )
        
        # Add to history
        session_data.messages.append(message)
        session_data.metadata.message_count += 1
        session_data.metadata.last_activity = datetime.utcnow()
        
        # Save back to storage
        await self.storage.save(
            f"session:{session_id}",
            session_data.model_dump(mode="json"),
            self.ttl
        )
        
        # Extend TTL on activity
        await self.storage.extend_ttl(f"session:{session_id}", self.ttl)
        
        logger.debug(f"Added {role} message to session {session_id}")
        return message
    
    async def get_history(
        self, 
        session_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Message]:
        """
        Get message history for a session
        
        Args:
            session_id: Session ID
            limit: Maximum number of messages to return
            offset: Number of messages to skip
            
        Returns:
            List of messages
        """
        session_data = await self.get_session(session_id)
        if not session_data:
            return []
        
        messages = session_data.messages[offset:]
        if limit:
            messages = messages[:limit]
        
        return messages
    
    async def get_history_for_agent(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[Dict[str, str]]:
        """
        Get message history formatted for the agent
        
        Args:
            session_id: Session ID
            limit: Maximum number of messages
            
        Returns:
            List of message dicts with 'role' and 'content'
        """
        messages = await self.get_history(session_id, limit)
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
            if msg.role in ["user", "assistant"]
        ]
    
    async def update_context(
        self,
        session_id: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Update session context
        
        Args:
            session_id: Session ID
            context: New context to merge
            
        Returns:
            True if successful
        """
        session_data = await self.get_session(session_id)
        if not session_data:
            return False
        
        # Merge context
        session_data.context.update(context)
        session_data.metadata.context.update(context)
        session_data.metadata.last_activity = datetime.utcnow()
        
        # Save back
        await self.storage.save(
            f"session:{session_id}",
            session_data.model_dump(mode="json"),
            self.ttl
        )
        
        logger.debug(f"Updated context for session {session_id}")
        return True
    
    async def clear_history(self, session_id: str) -> bool:
        """
        Clear message history for a session
        
        Args:
            session_id: Session ID
            
        Returns:
            True if successful
        """
        session_data = await self.get_session(session_id)
        if not session_data:
            return False
        
        # Clear messages
        session_data.messages = []
        session_data.metadata.message_count = 0
        session_data.metadata.last_activity = datetime.utcnow()
        
        # Save back
        await self.storage.save(
            f"session:{session_id}",
            session_data.model_dump(mode="json"),
            self.ttl
        )
        
        logger.info(f"Cleared history for session {session_id}")
        return True
    
    async def delete_session(self, session_id: str) -> None:
        """Delete a session"""
        await self.storage.delete(f"session:{session_id}")
        logger.info(f"Deleted session {session_id}")
    
    async def session_exists(self, session_id: str) -> bool:
        """Check if session exists"""
        return await self.storage.exists(f"session:{session_id}")