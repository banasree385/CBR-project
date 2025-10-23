"""
Agent API endpoints for Azure AI Foundry Agent Service
Simplified for workshop - focus on chat functionality
"""

import asyncio
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
import structlog

from app.models.chat import ChatMessage, MessageRole
from app.services.azure_agent_service import SimpleAzureAgentService
from app.utils.exceptions import CustomException

logger = structlog.get_logger()

router = APIRouter()

# In-memory storage for demo purposes
agent_tasks = {}
agent_metrics = {}


def get_azure_agent_service() -> SimpleAzureAgentService:
    """Dependency to get Azure Agent service instance."""
    return SimpleAzureAgentService()


@router.get("/status")
async def get_agent_status():
    """Get the status of the Azure Agent Service."""
    try:
        azure_agent_service = get_azure_agent_service()
        connection_ok = await azure_agent_service.verify_connection()
        
        return {
            "status": "active" if connection_ok else "inactive",
            "service": "Azure AI Agent Service",
            "timestamp": datetime.utcnow(),
            "message": "Azure Agent Service is running" if connection_ok else "Azure Agent Service connection failed"
        }
        
    except Exception as e:
        logger.error("Failed to get agent status", error=str(e))
        return {
            "status": "error",
            "service": "Azure AI Agent Service", 
            "timestamp": datetime.utcnow(),
            "message": f"Error: {str(e)}"
        }


@router.post("/simple-query")
async def simple_agent_query(
    message: str,
    azure_agent_service: SimpleAzureAgentService = Depends(get_azure_agent_service)
):
    """Send a simple message to the Azure Agent Service."""
    
    try:
        if not message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )
        
        # Create a simple message
        messages = [ChatMessage(
            role=MessageRole.USER,
            content=message
        )]
        
        # Generate response
        response = await azure_agent_service.generate_response(messages)
        
        logger.info("Agent query processed", message_length=len(message))
        
        return {
            "message": message,
            "response": response["content"],
            "model_used": response["model_used"],
            "tokens_used": response["tokens_used"],
            "response_time": response["response_time"],
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to process agent query", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Agent query failed: {str(e)}"
        )


# Additional endpoints can be added here as the workshop progresses
# For now, we keep it simple with just status and simple query endpoints