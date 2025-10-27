"""
Azure AI Foundry Agent Integration Service
Connects to your 2 agents + 1 orchestrator created in Azure AI Foundry
"""

import asyncio
import time
import os
from typing import Optional, Dict, Any, List
import structlog
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    Agent,
    AgentThread,
    MessageRole,
    ThreadRun,
    RunStatus,
    ThreadMessage,
)
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AccessToken
from azure.core.credentials_async import AsyncTokenCredential
import subprocess
import json
from datetime import datetime, timezone

from app.config_simple import get_settings
from app.models.chat import ChatMessage, MessageRole as ChatMessageRole

logger = structlog.get_logger()
settings = get_settings()


class AIFoundryCredential:
    """Custom credential for Azure AI Foundry with correct scope."""
    
    def __init__(self):
        self._token = None
        self._expires_on = None
    
    def get_token(self, *scopes, **kwargs):
        """Get token with correct scope for AI Foundry."""
        try:
            # Check if we have a valid cached token
            if self._token and self._expires_on:
                now = datetime.now(timezone.utc)
                if now < self._expires_on:
                    return AccessToken(self._token, int(self._expires_on.timestamp()))
            
            # Get fresh token using Azure CLI
            result = subprocess.run([
                'az', 'account', 'get-access-token', 
                '--resource', 'https://ai.azure.com'
            ], capture_output=True, text=True, check=True)
            
            token_data = json.loads(result.stdout)
            self._token = token_data['accessToken']
            
            # Parse expiry
            expires_on_str = token_data['expiresOn']
            self._expires_on = datetime.fromisoformat(expires_on_str.replace('Z', '+00:00'))
            
            return AccessToken(self._token, int(self._expires_on.timestamp()))
            
        except Exception as e:
            logger.error("Failed to get AI Foundry token", error=str(e))
            # Fallback to default credential
            fallback = DefaultAzureCredential()
            return fallback.get_token(*scopes, **kwargs)


class FoundryAgentService:
    """Service to interact with your Azure AI Foundry agents."""
    
    def __init__(self):
        """Initialize the service."""
        self.project_client = None
        self.orchestrator_agent_id = None
        self.agent1_id = None
        self.agent2_id = None
        self.current_thread = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Azure AI Project client."""
        try:
            if not settings.azure_ai_foundry_endpoint or settings.azure_ai_foundry_endpoint.startswith("https://your-"):
                logger.warning("No real Azure AI Foundry endpoint found, service not available")
                return
            
            if not all([settings.azure_subscription_id, settings.azure_resource_group, settings.azure_project_name]):
                logger.error("Missing required Azure project parameters")
                return
            
            self.project_client = AIProjectClient(
                endpoint=settings.azure_ai_foundry_endpoint,
                credential=AIFoundryCredential(),
                subscription_id=settings.azure_subscription_id,
                resource_group_name=settings.azure_resource_group,
                project_name=settings.azure_project_name,
            )
            
            # Get agent IDs from environment variables
            self.orchestrator_agent_id = os.getenv("ORCHESTRATOR_AGENT_ID")
            self.agent1_id = os.getenv("AGENT1_ID")
            self.agent2_id = os.getenv("AGENT2_ID")
            
            logger.info("Azure AI Foundry client initialized")
            logger.info(f"Orchestrator Agent ID: {self.orchestrator_agent_id}")
            logger.info(f"Agent 1 ID: {self.agent1_id}")
            logger.info(f"Agent 2 ID: {self.agent2_id}")
            
        except Exception as e:
            logger.error("Failed to initialize Azure AI Foundry client", error=str(e))
            self.project_client = None
    
    async def initialize(self) -> bool:
        """Initialize the service and verify agent connections."""
        try:
            if not self.project_client:
                logger.warning("No Azure AI Project client available")
                return False
            
            # Verify agents exist
            agents_verified = await self._verify_agents()
            if not agents_verified:
                logger.error("Failed to verify agents")
                return False
            
            # Create a thread for conversations
            await self._create_thread()
            
            logger.info("✅ Foundry Agent Service initialized successfully")
            return True
            
        except Exception as e:
            logger.error("Failed to initialize Foundry Agent Service", error=str(e))
            return False
    
    async def _verify_agents(self) -> bool:
        """Verify that all agents exist in Azure AI Foundry."""
        try:
            required_agents = {
                "Orchestrator": self.orchestrator_agent_id,
                "Agent 1": self.agent1_id,
                "Agent 2": self.agent2_id
            }
            
            for agent_name, agent_id in required_agents.items():
                if not agent_id:
                    logger.error(f"Missing {agent_name} ID in environment variables")
                    return False
                
                try:
                    agent = self.project_client.agents.get_agent(agent_id)
                    logger.info(f"✅ {agent_name} verified: {agent.name}")
                except Exception as e:
                    logger.error(f"❌ Failed to verify {agent_name} ({agent_id})", error=str(e))
                    return False
            
            return True
            
        except Exception as e:
            logger.error("Error verifying agents", error=str(e))
            return False
    
    async def _create_thread(self):
        """Create a new conversation thread."""
        try:
            if not self.project_client:
                return None
            
            self.current_thread = self.project_client.agents.threads.create()
            logger.info(f"Created new thread: {self.current_thread.id}")
            return self.current_thread
            
        except Exception as e:
            logger.error("Failed to create thread", error=str(e))
            return None
    
    async def process_message(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """Process a message through the orchestrator agent with retry logic."""
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                if not self.project_client or not self.orchestrator_agent_id:
                    return await self._mock_response(message)
                
                if not self.current_thread:
                    await self._create_thread()
                
                start_time = time.time()
                
                # Add message to thread
                thread_message = self.project_client.agents.messages.create(
                    thread_id=self.current_thread.id,
                    role="user",
                    content=message
                )
                
                # Run the orchestrator agent
                run = self.project_client.agents.runs.create(
                    thread_id=self.current_thread.id,
                    agent_id=self.orchestrator_agent_id
                )
                
                # Wait for completion
                run = await self._wait_for_run_completion(run.id)
                
                if run.status == RunStatus.COMPLETED:
                    # Get the latest message
                    messages = self.project_client.agents.messages.list(
                        thread_id=self.current_thread.id
                    )
                    
                    # Convert ItemPaged to list and get the most recent message
                    message_list = list(messages)
                    if message_list:
                        latest_message = message_list[0]  # Most recent message
                        response_content = latest_message.content[0].text.value if latest_message.content else "No response generated"
                    else:
                        response_content = "No messages found"
                    
                    response_time = time.time() - start_time
                    
                    return {
                        "content": response_content,
                        "agent_used": "Orchestrator",
                        "session_id": session_id,
                        "response_time": response_time,
                        "tokens_used": 0,  # Azure Agents API doesn't expose token count
                        "model_used": "Azure AI Foundry Agents",
                        "run_id": run.id,
                        "thread_id": self.current_thread.id
                    }
                else:
                    logger.error(f"Run failed with status: {run.status} (attempt {attempt + 1}/{max_retries + 1})")
                    
                    # Try to get more details about the failure
                    try:
                        if hasattr(run, 'last_error') and run.last_error:
                            logger.error(f"Run failure details: {run.last_error}")
                        if hasattr(run, 'failed_at') and run.failed_at:
                            logger.error(f"Run failed at: {run.failed_at}")
                    except Exception as detail_error:
                        logger.error(f"Could not get run failure details: {detail_error}")
                    
                    # If this was the last attempt, fall back to mock
                    if attempt == max_retries:
                        return await self._mock_response(message)
                    
                    # Wait before retry and create new thread
                    await asyncio.sleep(2)
                    self.current_thread = None
                    
            except Exception as e:
                logger.error(f"Error processing message (attempt {attempt + 1}/{max_retries + 1})", error=str(e))
                
                # If this was the last attempt, fall back to mock
                if attempt == max_retries:
                    return await self._mock_response(message)
                
                # Wait before retry and create new thread
                await asyncio.sleep(2)
                self.current_thread = None
    
    async def _wait_for_run_completion(self, run_id: str, max_wait_time: int = 60) -> ThreadRun:
        """Wait for a run to complete."""
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            run = self.project_client.agents.runs.get(
                thread_id=self.current_thread.id,
                run_id=run_id
            )
            
            if run.status in [RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED, RunStatus.EXPIRED]:
                if run.status != RunStatus.COMPLETED:
                    logger.warning(f"Run {run_id} ended with status: {run.status}")
                return run
            
            await asyncio.sleep(1)  # Check every second
        
        # Timeout
        logger.warning(f"Run {run_id} timed out after {max_wait_time} seconds")
        return run
    
    async def route_to_specific_agent(self, message: str, agent_type: str, session_id: str = None) -> Dict[str, Any]:
        """Route message to a specific agent (agent1 or agent2)."""
        try:
            if not self.project_client:
                return await self._mock_response(message, agent_type)
            
            # Determine which agent to use
            if agent_type == "agent1" and self.agent1_id:
                agent_id = self.agent1_id
                agent_name = "Agent 1"
            elif agent_type == "agent2" and self.agent2_id:
                agent_id = self.agent2_id
                agent_name = "Agent 2"
            else:
                logger.error(f"Invalid agent type or missing ID: {agent_type}")
                return await self._mock_response(message, agent_type)
            
            if not self.current_thread:
                await self._create_thread()
            
            start_time = time.time()
            
            # Add message to thread
            self.project_client.agents.messages.create(
                thread_id=self.current_thread.id,
                role="user",
                content=message
            )
            
            # Run the specific agent
            run = self.project_client.agents.runs.create(
                thread_id=self.current_thread.id,
                agent_id=agent_id
            )
            
            # Wait for completion
            run = await self._wait_for_run_completion(run.id)
            
            if run.status == RunStatus.COMPLETED:
                messages = self.project_client.agents.messages.list(
                    thread_id=self.current_thread.id
                )
                
                # Convert ItemPaged to list and get the most recent message
                message_list = list(messages)
                if message_list:
                    latest_message = message_list[0]
                    response_content = latest_message.content[0].text.value if latest_message.content else "No response generated"
                else:
                    response_content = "No messages found"
                
                response_time = time.time() - start_time
                
                return {
                    "content": response_content,
                    "agent_used": agent_name,
                    "session_id": session_id,
                    "response_time": response_time,
                    "tokens_used": 0,
                    "model_used": "Azure AI Foundry Agents",
                    "run_id": run.id,
                    "thread_id": self.current_thread.id
                }
            else:
                logger.error(f"Run failed with status: {run.status}")
                return await self._mock_response(message, agent_type)
                
        except Exception as e:
            logger.error(f"Error routing to {agent_type}", error=str(e))
            return await self._mock_response(message, agent_type)
    
    async def _mock_response(self, message: str, agent_type: str = "orchestrator") -> Dict[str, Any]:
        """Generate a mock response when Azure agents are not available."""
        responses = {
            "orchestrator": "🤖 [Mock Orchestrator] I would analyze your query and route it to the appropriate specialist agent.",
            "agent1": "🔧 [Mock Agent 1] I would handle this request with my specialized capabilities.",
            "agent2": "⚙️ [Mock Agent 2] I would process this request using my domain expertise."
        }
        
        mock_content = responses.get(agent_type, responses["orchestrator"])
        mock_content += f" Your message: '{message[:100]}...'" if len(message) > 100 else f" Your message: '{message}'"
        
        return {
            "content": mock_content,
            "agent_used": f"Mock {agent_type.title()}",
            "session_id": f"mock-{int(time.time())}",
            "response_time": 0.5,
            "tokens_used": 0,
            "model_used": "Mock Agent",
            "run_id": "mock-run",
            "thread_id": "mock-thread"
        }
    
    async def get_conversation_history(self, thread_id: str = None) -> List[Dict[str, Any]]:
        """Get conversation history from the current thread."""
        try:
            if not self.project_client or not self.current_thread:
                return []
            
            use_thread_id = thread_id or self.current_thread.id
            
            messages = self.project_client.agents.messages.list(thread_id=use_thread_id)
            
            # Convert ItemPaged to list
            message_list = list(messages)
            
            history = []
            for message in reversed(message_list):  # Reverse to get chronological order
                history.append({
                    "role": message.role,
                    "content": message.content[0].text.value if message.content else "",
                    "timestamp": message.created_at,
                    "message_id": message.id
                })
            
            return history
            
        except Exception as e:
            logger.error("Error getting conversation history", error=str(e))
            return []
    
    async def create_new_session(self) -> str:
        """Create a new conversation session."""
        try:
            thread = await self._create_thread()
            return thread.id if thread else f"mock-session-{int(time.time())}"
        except Exception as e:
            logger.error("Error creating new session", error=str(e))
            return f"error-session-{int(time.time())}"
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        try:
            if not self.project_client:
                return {
                    "status": "offline",
                    "message": "Azure AI Foundry client not initialized",
                    "agents": {
                        "orchestrator": "offline",
                        "agent1": "offline", 
                        "agent2": "offline"
                    }
                }
            
            agent_status = {}
            agents = {
                "orchestrator": self.orchestrator_agent_id,
                "agent1": self.agent1_id,
                "agent2": self.agent2_id
            }
            
            for agent_name, agent_id in agents.items():
                if agent_id:
                    try:
                        agent = self.project_client.agents.get_agent(agent_id)
                        agent_status[agent_name] = {
                            "status": "online",
                            "name": agent.name,
                            "model": agent.model,
                            "id": agent_id
                        }
                    except Exception as e:
                        agent_status[agent_name] = {
                            "status": "error",
                            "error": str(e),
                            "id": agent_id
                        }
                else:
                    agent_status[agent_name] = {
                        "status": "not_configured",
                        "message": "Agent ID not set in environment variables"
                    }
            
            return {
                "status": "online",
                "agents": agent_status,
                "thread_id": self.current_thread.id if self.current_thread else None
            }
            
        except Exception as e:
            logger.error("Error getting agent status", error=str(e))
            return {
                "status": "error",
                "error": str(e),
                "agents": {}
            }
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            self.current_thread = None
            self.project_client = None
            logger.info("🧹 Foundry Agent Service cleaned up")
        except Exception as e:
            logger.error("Error during cleanup", error=str(e))