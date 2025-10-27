"""
Foundry Agent Chat API endpoints
Connects to your 2 agents + orchestrator in Azure AI Foundry
"""

import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import structlog

from app.models.chat import ChatMessage, MessageRole as ChatMessageRole
from app.services.foundry_agent_service import FoundryAgentService

logger = structlog.get_logger()
router = APIRouter()

# Global Foundry Agent Service instance
_foundry_agent_service = None

class FoundryAgentRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    agent_type: Optional[str] = "orchestrator"  # "orchestrator", "agent1", or "agent2"

class FoundryAgentResponse(BaseModel):
    message: str
    agent_used: str
    session_id: str
    response_time_ms: int
    run_id: str
    thread_id: str
    model_used: str

class AgentStatusResponse(BaseModel):
    status: str
    agents: dict
    thread_id: Optional[str] = None

def get_foundry_agent_service() -> FoundryAgentService:
    """Dependency to get Foundry Agent service instance."""
    global _foundry_agent_service
    if _foundry_agent_service is None:
        _foundry_agent_service = FoundryAgentService()
    return _foundry_agent_service

@router.post("/foundry/chat", response_model=FoundryAgentResponse)
async def foundry_agent_chat(
    request: FoundryAgentRequest,
    foundry_service: FoundryAgentService = Depends(get_foundry_agent_service)
):
    """Send a message to Azure AI Foundry agents."""
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or f"foundry_{uuid.uuid4().hex[:8]}"
        
        # Route to appropriate agent
        if request.agent_type == "orchestrator":
            result = await foundry_service.process_message(request.message, session_id)
        elif request.agent_type in ["agent1", "agent2"]:
            result = await foundry_service.route_to_specific_agent(
                request.message, request.agent_type, session_id
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid agent_type: {request.agent_type}. Use 'orchestrator', 'agent1', or 'agent2'"
            )
        
        response = FoundryAgentResponse(
            message=result["content"],
            agent_used=result["agent_used"],
            session_id=result["session_id"],
            response_time_ms=int(result["response_time"] * 1000),
            run_id=result["run_id"],
            thread_id=result["thread_id"],
            model_used=result["model_used"]
        )
        
        logger.info(
            "Foundry agent message processed",
            agent_type=request.agent_type,
            agent_used=result["agent_used"],
            session_id=session_id,
            response_time=result["response_time"]
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to process foundry agent message", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )

@router.post("/foundry/orchestrator", response_model=FoundryAgentResponse)
async def chat_with_orchestrator(
    request: FoundryAgentRequest,
    foundry_service: FoundryAgentService = Depends(get_foundry_agent_service)
):
    """Send a message specifically to the orchestrator agent."""
    request.agent_type = "orchestrator"
    return await foundry_agent_chat(request, foundry_service)

@router.post("/foundry/agent1", response_model=FoundryAgentResponse)
async def chat_with_agent1(
    request: FoundryAgentRequest,
    foundry_service: FoundryAgentService = Depends(get_foundry_agent_service)
):
    """Send a message specifically to Agent 1."""
    request.agent_type = "agent1"
    return await foundry_agent_chat(request, foundry_service)

@router.post("/foundry/agent2", response_model=FoundryAgentResponse)
async def chat_with_agent2(
    request: FoundryAgentRequest,
    foundry_service: FoundryAgentService = Depends(get_foundry_agent_service)
):
    """Send a message specifically to Agent 2."""
    request.agent_type = "agent2"
    return await foundry_agent_chat(request, foundry_service)

@router.get("/foundry/status", response_model=AgentStatusResponse)
async def get_foundry_agent_status(
    foundry_service: FoundryAgentService = Depends(get_foundry_agent_service)
):
    """Get status of all Foundry agents."""
    
    try:
        status = await foundry_service.get_agent_status()
        
        return AgentStatusResponse(
            status=status["status"],
            agents=status["agents"],
            thread_id=status.get("thread_id")
        )
        
    except Exception as e:
        logger.error("Failed to get foundry agent status", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent status: {str(e)}"
        )

@router.get("/foundry/history/{thread_id}")
async def get_conversation_history(
    thread_id: str,
    foundry_service: FoundryAgentService = Depends(get_foundry_agent_service)
):
    """Get conversation history for a thread."""
    
    try:
        history = await foundry_service.get_conversation_history(thread_id)
        
        return {
            "thread_id": thread_id,
            "messages": history,
            "total_messages": len(history)
        }
        
    except Exception as e:
        logger.error("Failed to get conversation history", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get conversation history: {str(e)}"
        )

@router.post("/foundry/new-session")
async def create_new_session(
    foundry_service: FoundryAgentService = Depends(get_foundry_agent_service)
):
    """Create a new conversation session."""
    
    try:
        session_id = await foundry_service.create_new_session()
        
        return {
            "session_id": session_id,
            "message": "New session created successfully"
        }
        
    except Exception as e:
        logger.error("Failed to create new session", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create new session: {str(e)}"
        )

@router.get("/foundry/health")
async def foundry_health_check():
    """Health check for Foundry agents."""
    return {
        "status": "healthy",
        "service": "Azure AI Foundry Agent Integration",
        "supported_agents": [
            "orchestrator",
            "agent1", 
            "agent2"
        ],
        "endpoints": [
            "/foundry/chat",
            "/foundry/orchestrator",
            "/foundry/agent1",
            "/foundry/agent2",
            "/foundry/status"
        ]
    }