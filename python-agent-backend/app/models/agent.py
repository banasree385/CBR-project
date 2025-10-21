"""
Agent-related Pydantic models
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    INITIALIZING = "initializing"


class AgentCapability(str, Enum):
    """Agent capability enumeration."""
    CHAT = "chat"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"


class AgentConfig(BaseModel):
    """Agent configuration model."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    model: str = Field(default="gpt-4")
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(1000, ge=1, le=4000)
    system_prompt: Optional[str] = Field(None, max_length=2000)
    capabilities: List[AgentCapability] = Field(default=[AgentCapability.CHAT])
    custom_settings: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "name": "Azure AI Assistant",
                "description": "AI agent specialized in Azure services help",
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1000,
                "system_prompt": "You are an Azure AI expert assistant...",
                "capabilities": ["chat", "analysis"],
                "custom_settings": {
                    "language": "en",
                    "expertise_level": "intermediate"
                }
            }
        }


class Agent(BaseModel):
    """Agent model."""
    agent_id: str
    config: AgentConfig
    status: AgentStatus = AgentStatus.INITIALIZING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None
    session_count: int = 0
    total_messages: int = 0
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "agent_id": "agent_123",
                "config": {
                    "name": "Azure AI Assistant",
                    "model": "gpt-4",
                    "temperature": 0.7
                },
                "status": "active",
                "created_at": "2025-10-21T17:00:00Z",
                "session_count": 10,
                "total_messages": 150
            }
        }


class AgentResponse(BaseModel):
    """Agent response model."""
    agent_id: str
    response: str
    metadata: Optional[Dict[str, Any]] = None
    processing_time_ms: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "agent_123",
                "response": "I can help you with Azure AI services...",
                "metadata": {
                    "confidence": 0.95,
                    "intent": "azure_help"
                },
                "processing_time_ms": 1200.5,
                "timestamp": "2025-10-21T17:00:00Z"
            }
        }


class AgentMetrics(BaseModel):
    """Agent metrics model."""
    agent_id: str
    total_sessions: int = 0
    total_messages: int = 0
    average_response_time_ms: float = 0.0
    success_rate: float = 100.0
    last_24h_messages: int = 0
    uptime_percentage: float = 100.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "agent_123",
                "total_sessions": 25,
                "total_messages": 150,
                "average_response_time_ms": 1100.0,
                "success_rate": 98.5,
                "last_24h_messages": 45,
                "uptime_percentage": 99.8
            }
        }


class AgentCreateRequest(BaseModel):
    """Agent creation request model."""
    config: AgentConfig
    auto_activate: bool = True
    
    class Config:
        schema_extra = {
            "example": {
                "config": {
                    "name": "Custom Azure Assistant",
                    "description": "Specialized agent for Azure support",
                    "model": "gpt-4",
                    "temperature": 0.7
                },
                "auto_activate": True
            }
        }


class AgentUpdateRequest(BaseModel):
    """Agent update request model."""
    config: Optional[AgentConfig] = None
    status: Optional[AgentStatus] = None
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "config": {
                    "temperature": 0.8,
                    "max_tokens": 1500
                },
                "status": "active"
            }
        }