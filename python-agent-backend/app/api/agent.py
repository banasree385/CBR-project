"""
Agent API endpoints for Azure AI Foundry
"""

import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
import structlog

from app.models.agent import (
    Agent, AgentConfig, AgentCreateRequest, AgentUpdateRequest, 
    AgentResponse, AgentMetrics, AgentStatus
)
from app.services.azure_ai_service import AzureAIService
from app.services.gpt_service import GPTService
from app.utils.exceptions import CustomException

logger = structlog.get_logger()

router = APIRouter()

# In-memory storage for demo purposes
agents_store = {}


def get_azure_ai_service() -> AzureAIService:
    """Dependency to get Azure AI service instance."""
    return AzureAIService()


def get_gpt_service() -> GPTService:
    """Dependency to get GPT service instance."""
    return GPTService()


@router.post("/create", response_model=Agent)
async def create_agent(
    request: AgentCreateRequest,
    azure_ai_service: AzureAIService = Depends(get_azure_ai_service)
):
    """Create a new AI agent."""
    
    try:
        # Create agent using Azure AI service
        agent = await azure_ai_service.create_agent(request.config)
        
        # Store agent locally for demo
        agents_store[agent.agent_id] = agent
        
        # Auto-activate if requested
        if request.auto_activate:
            agent.status = AgentStatus.ACTIVE
        
        logger.info("Agent created successfully", agent_id=agent.agent_id, name=agent.config.name)
        return agent
        
    except CustomException:
        raise
    except Exception as e:
        logger.error("Failed to create agent", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "agent_creation_error",
                "message": "Failed to create agent"
            }
        )


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """Get agent details by ID."""
    
    try:
        if agent_id not in agents_store:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "agent_not_found",
                    "message": f"Agent {agent_id} not found"
                }
            )
        
        agent = agents_store[agent_id]
        logger.info("Agent retrieved successfully", agent_id=agent_id)
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get agent", agent_id=agent_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "agent_retrieval_error",
                "message": "Failed to retrieve agent"
            }
        )


@router.get("/", response_model=List[Agent])
async def list_agents():
    """List all agents."""
    
    try:
        agents = list(agents_store.values())
        agents.sort(key=lambda x: x.created_at, reverse=True)
        
        logger.info("Agents listed successfully", agent_count=len(agents))
        return agents
        
    except Exception as e:
        logger.error("Failed to list agents", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "agent_list_error",
                "message": "Failed to list agents"
            }
        )


@router.put("/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: str,
    request: AgentUpdateRequest,
    azure_ai_service: AzureAIService = Depends(get_azure_ai_service)
):
    """Update agent configuration."""
    
    try:
        if agent_id not in agents_store:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "agent_not_found",
                    "message": f"Agent {agent_id} not found"
                }
            )
        
        agent = agents_store[agent_id]
        
        # Update configuration if provided
        if request.config:
            agent.config = request.config
        
        # Update status if provided
        if request.status:
            agent.status = request.status
        
        # Update timestamp
        agent.updated_at = datetime.utcnow()
        
        # Update in Azure AI service (in real implementation)
        # await azure_ai_service.update_agent(agent_id, agent.config)
        
        logger.info("Agent updated successfully", agent_id=agent_id)
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update agent", agent_id=agent_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "agent_update_error",
                "message": "Failed to update agent"
            }
        )


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    azure_ai_service: AzureAIService = Depends(get_azure_ai_service)
):
    """Delete an agent."""
    
    try:
        if agent_id not in agents_store:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "agent_not_found",
                    "message": f"Agent {agent_id} not found"
                }
            )
        
        # Delete from Azure AI service (in real implementation)
        # await azure_ai_service.delete_agent(agent_id)
        
        # Delete from local storage
        del agents_store[agent_id]
        
        logger.info("Agent deleted successfully", agent_id=agent_id)
        return {"message": "Agent deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete agent", agent_id=agent_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "agent_deletion_error",
                "message": "Failed to delete agent"
            }
        )


@router.post("/{agent_id}/invoke", response_model=AgentResponse)
async def invoke_agent(
    agent_id: str,
    message: str,
    gpt_service: GPTService = Depends(get_gpt_service),
    azure_ai_service: AzureAIService = Depends(get_azure_ai_service)
):
    """Invoke an agent with a message."""
    
    try:
        if agent_id not in agents_store:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "agent_not_found",
                    "message": f"Agent {agent_id} not found"
                }
            )
        
        agent = agents_store[agent_id]
        
        if agent.status != AgentStatus.ACTIVE:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "agent_inactive",
                    "message": f"Agent {agent_id} is not active"
                }
            )
        
        # Generate response using GPT service with agent configuration
        gpt_response = await gpt_service.generate_chat_response(
            user_message=message,
            temperature=agent.config.temperature,
            max_tokens=agent.config.max_tokens,
            system_prompt=agent.config.system_prompt
        )
        
        # Update agent statistics
        agent.total_messages += 1
        agent.last_active = datetime.utcnow()
        agent.updated_at = datetime.utcnow()
        
        # Create agent response
        response = AgentResponse(
            agent_id=agent_id,
            response=gpt_response["content"],
            metadata={
                "model_used": gpt_response["model_used"],
                "tokens_used": gpt_response["tokens_used"],
                "agent_config": {
                    "temperature": agent.config.temperature,
                    "max_tokens": agent.config.max_tokens
                }
            },
            processing_time_ms=gpt_response["response_time_ms"]
        )
        
        logger.info(
            "Agent invoked successfully",
            agent_id=agent_id,
            message_length=len(message),
            response_length=len(response.response)
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to invoke agent", agent_id=agent_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "agent_invocation_error",
                "message": "Failed to invoke agent"
            }
        )


@router.get("/{agent_id}/metrics", response_model=AgentMetrics)
async def get_agent_metrics(agent_id: str):
    """Get agent performance metrics."""
    
    try:
        if agent_id not in agents_store:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "agent_not_found",
                    "message": f"Agent {agent_id} not found"
                }
            )
        
        agent = agents_store[agent_id]
        
        # Calculate metrics (in real implementation, get from monitoring service)
        metrics = AgentMetrics(
            agent_id=agent_id,
            total_sessions=agent.session_count,
            total_messages=agent.total_messages,
            average_response_time_ms=1200.0,  # Mock data
            success_rate=98.5,  # Mock data
            last_24h_messages=25,  # Mock data
            uptime_percentage=99.8  # Mock data
        )
        
        logger.info("Agent metrics retrieved", agent_id=agent_id)
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get agent metrics", agent_id=agent_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "metrics_error",
                "message": "Failed to retrieve agent metrics"
            }
        )


@router.post("/{agent_id}/activate")
async def activate_agent(agent_id: str):
    """Activate an agent."""
    
    try:
        if agent_id not in agents_store:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "agent_not_found",
                    "message": f"Agent {agent_id} not found"
                }
            )
        
        agent = agents_store[agent_id]
        agent.status = AgentStatus.ACTIVE
        agent.updated_at = datetime.utcnow()
        
        logger.info("Agent activated", agent_id=agent_id)
        return {"message": "Agent activated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to activate agent", agent_id=agent_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "agent_activation_error",
                "message": "Failed to activate agent"
            }
        )


@router.post("/{agent_id}/deactivate")
async def deactivate_agent(agent_id: str):
    """Deactivate an agent."""
    
    try:
        if agent_id not in agents_store:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "agent_not_found",
                    "message": f"Agent {agent_id} not found"
                }
            )
        
        agent = agents_store[agent_id]
        agent.status = AgentStatus.INACTIVE
        agent.updated_at = datetime.utcnow()
        
        logger.info("Agent deactivated", agent_id=agent_id)
        return {"message": "Agent deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to deactivate agent", agent_id=agent_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "agent_deactivation_error",
                "message": "Failed to deactivate agent"
            }
        )


@router.get("/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """Get agent status and health information."""
    
    try:
        if agent_id not in agents_store:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "agent_not_found",
                    "message": f"Agent {agent_id} not found"
                }
            )
        
        agent = agents_store[agent_id]
        
        status_info = {
            "agent_id": agent_id,
            "status": agent.status.value,
            "name": agent.config.name,
            "model": agent.config.model,
            "created_at": agent.created_at,
            "updated_at": agent.updated_at,
            "last_active": agent.last_active,
            "total_messages": agent.total_messages,
            "session_count": agent.session_count,
            "capabilities": [cap.value for cap in agent.config.capabilities],
            "health": "healthy" if agent.status == AgentStatus.ACTIVE else "inactive"
        }
        
        logger.info("Agent status retrieved", agent_id=agent_id, status=agent.status.value)
        return status_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get agent status", agent_id=agent_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "status_error",
                "message": "Failed to get agent status"
            }
        )