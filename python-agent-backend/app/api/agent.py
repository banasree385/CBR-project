"""
Simple Agent API endpoints for workshop
Perfect for learning basic AI agent functionality
"""

import time
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
import structlog

from app.models.chat import ChatMessage, MessageRole
from app.services.azure_agent_service import SimpleAzureAgentService

logger = structlog.get_logger()

router = APIRouter()


def get_azure_agent_service() -> SimpleAzureAgentService:
    """Get Azure Agent service instance."""
    return SimpleAzureAgentService()


@router.get("/status")
async def get_agent_status():
    """Check if the Azure Agent Service is working."""
    try:
        azure_agent_service = get_azure_agent_service()
        connection_ok = await azure_agent_service.verify_connection()
        
        return {
            "status": "working" if connection_ok else "not_working",
            "service": "Azure AI Agent",
            "timestamp": datetime.utcnow(),
            "message": "Azure Agent is ready!" if connection_ok else "Azure Agent connection failed"
        }
        
    except Exception as e:
        logger.error("Agent status check failed", error=str(e))
        return {
            "status": "error",
            "service": "Azure AI Agent", 
            "timestamp": datetime.utcnow(),
            "message": f"Error: {str(e)}"
        }


@router.post("/ask")
async def ask_agent(
    message: str,
    azure_agent_service: SimpleAzureAgentService = Depends(get_azure_agent_service)
):
    """Ask the AI agent a simple question."""
    
    try:
        if not message.strip():
            raise HTTPException(
                status_code=400,
                detail="Please provide a message to send to the agent"
            )
        
        # Create a simple message for the agent
        start_time = time.time()
        messages = [ChatMessage(
            role=MessageRole.USER,
            content=message
        )]
        
        # Get response from Azure AI agent
        response = await azure_agent_service.generate_response(messages)
        response_time = time.time() - start_time
        
        logger.info("Agent question processed", 
                   message_length=len(message), 
                   response_time=response_time)
        
        return {
            "your_message": message,
            "agent_response": response["content"],
            "model_used": response["model_used"],
            "response_time_seconds": round(response_time, 2),
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Agent question failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Sorry, the agent couldn't process your question: {str(e)}"
        )


# Workshop participants can add more endpoints here as they learn!