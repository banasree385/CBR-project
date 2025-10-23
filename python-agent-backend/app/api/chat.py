"""
Chat API endpoints for Azure AI Foundry Agent
"""

import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
import structlog

from app.models.chat import (
    ChatRequest, ChatResponse, ChatHistory, ChatSession, ChatMessage, MessageRole
)
from app.services.azure_agent_service import SimpleAzureAgentService

logger = structlog.get_logger()

router = APIRouter()

# In-memory storage for demo purposes
# In production, use a proper database
chat_sessions = {}
chat_histories = {}

# Global Azure Agent Service instance (singleton)
_azure_agent_service = None


def get_azure_agent_service() -> SimpleAzureAgentService:
    """Dependency to get Azure Agent service instance."""
    global _azure_agent_service
    if _azure_agent_service is None:
        _azure_agent_service = SimpleAzureAgentService()
    return _azure_agent_service


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    azure_agent_service: SimpleAzureAgentService = Depends(get_azure_agent_service)
):
    """Send a message to the AI agent and get a response."""
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"
        
        # Get or create chat history
        if session_id not in chat_histories:
            chat_histories[session_id] = []
        
        conversation_history = chat_histories[session_id]
        
        # Add user message to conversation history
        user_message = ChatMessage(
            role=MessageRole.USER,
            content=request.message
        )
        conversation_history.append(user_message)
        
        # Generate response using Azure Agent Service
        agent_response = await azure_agent_service.generate_response(conversation_history)
        
        # Create response message
        assistant_message = ChatMessage(
            role=MessageRole.ASSISTANT,
            content=agent_response["content"],
            metadata={
                "model_used": agent_response["model_used"],
                "tokens_used": agent_response["tokens_used"],
                "response_time": agent_response["response_time"]
            }
        )
        
        # Update conversation history
        chat_histories[session_id].append(assistant_message)
        
        # Update session info
        if session_id not in chat_sessions:
            chat_sessions[session_id] = ChatSession(
                session_id=session_id,
                title=request.message[:50] + "..." if len(request.message) > 50 else request.message
            )
        
        chat_sessions[session_id].updated_at = datetime.utcnow()
        chat_sessions[session_id].message_count = len(chat_histories[session_id])
        
        # Create response
        response = ChatResponse(
            message=agent_response["content"],
            session_id=session_id,
            model_used=agent_response["model_used"],
            tokens_used=agent_response["tokens_used"],
            response_time_ms=int(agent_response["response_time"] * 1000)  # Convert to milliseconds
        )
        
        logger.info(
            "Chat message processed successfully",
            session_id=session_id,
            message_length=len(request.message),
            response_length=len(response.message),
            tokens_used=response.tokens_used
        )
        
        return response
        
    except Exception as e:
        logger.error("Failed to process chat message", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "message_processing_error",
                "message": "Failed to process your message"
            }
        )


@router.get("/history/{session_id}", response_model=ChatHistory)
async def get_chat_history(session_id: str):
    """Get chat history for a session."""
    
    try:
        if session_id not in chat_histories:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "session_not_found",
                    "message": f"Chat session {session_id} not found"
                }
            )
        
        messages = chat_histories[session_id]
        session = chat_sessions.get(session_id)
        
        history = ChatHistory(
            session_id=session_id,
            messages=messages,
            total_messages=len(messages),
            created_at=session.created_at if session else datetime.utcnow(),
            updated_at=session.updated_at if session else datetime.utcnow()
        )
        
        logger.info("Chat history retrieved", session_id=session_id, message_count=len(messages))
        return history
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get chat history", session_id=session_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "history_retrieval_error",
                "message": "Failed to retrieve chat history"
            }
        )


@router.get("/sessions", response_model=List[ChatSession])
async def list_chat_sessions():
    """List all chat sessions."""
    
    try:
        sessions = list(chat_sessions.values())
        sessions.sort(key=lambda x: x.updated_at, reverse=True)
        
        logger.info("Chat sessions listed", session_count=len(sessions))
        return sessions
        
    except Exception as e:
        logger.error("Failed to list chat sessions", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "session_list_error",
                "message": "Failed to list chat sessions"
            }
        )


@router.delete("/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session and its history."""
    
    try:
        if session_id not in chat_sessions:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "session_not_found",
                    "message": f"Chat session {session_id} not found"
                }
            )
        
        # Delete session and history
        del chat_sessions[session_id]
        if session_id in chat_histories:
            del chat_histories[session_id]
        
        logger.info("Chat session deleted", session_id=session_id)
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete chat session", session_id=session_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "session_deletion_error",
                "message": "Failed to delete chat session"
            }
        )


@router.post("/sessions/{session_id}/clear")
async def clear_chat_history(session_id: str):
    """Clear chat history for a session."""
    
    try:
        if session_id not in chat_sessions:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "session_not_found",
                    "message": f"Chat session {session_id} not found"
                }
            )
        
        # Clear history but keep session
        chat_histories[session_id] = []
        chat_sessions[session_id].message_count = 0
        chat_sessions[session_id].updated_at = datetime.utcnow()
        
        logger.info("Chat history cleared", session_id=session_id)
        return {"message": "Chat history cleared successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to clear chat history", session_id=session_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "history_clear_error",
                "message": "Failed to clear chat history"
            }
        )


# Additional advanced endpoints can be added here as workshop progresses
# Keeping it simple for now with core chat functionality