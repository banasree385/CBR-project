"""
Chat-related Pydantic models
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Individual chat message model."""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="Response creativity")
    max_tokens: Optional[int] = Field(1000, ge=1, le=4000, description="Maximum response tokens")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Hello, I need help with Azure AI services",
                "session_id": "session_123",
                "temperature": 0.7,
                "max_tokens": 1000
            }
        }


class ChatResponse(BaseModel):
    """Chat response model."""
    message: str
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_used: str
    tokens_used: Optional[int] = None
    response_time_ms: Optional[float] = None
    confidence_score: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Hello! I'm here to help you with Azure AI services. What specific questions do you have?",
                "session_id": "session_123",
                "timestamp": "2025-10-21T17:00:00Z",
                "model_used": "gpt-4",
                "tokens_used": 25,
                "response_time_ms": 1200.5
            }
        }


class ChatHistory(BaseModel):
    """Chat history model."""
    session_id: str
    messages: List[ChatMessage]
    total_messages: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "session_123",
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello",
                        "timestamp": "2025-10-21T17:00:00Z"
                    },
                    {
                        "role": "assistant", 
                        "content": "Hello! How can I help you?",
                        "timestamp": "2025-10-21T17:00:01Z"
                    }
                ],
                "total_messages": 2,
                "created_at": "2025-10-21T17:00:00Z",
                "updated_at": "2025-10-21T17:00:01Z"
            }
        }


class ChatSession(BaseModel):
    """Chat session model."""
    session_id: str
    user_id: Optional[str] = None
    title: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    message_count: int = 0
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "session_123",
                "user_id": "user_456",
                "title": "Azure AI Discussion",
                "created_at": "2025-10-21T17:00:00Z",
                "updated_at": "2025-10-21T17:00:00Z",
                "is_active": True,
                "message_count": 5
            }
        }


class ChatError(BaseModel):
    """Chat error model."""
    error_type: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "error_type": "validation_error",
                "message": "Message cannot be empty",
                "timestamp": "2025-10-21T17:00:00Z"
            }
        }