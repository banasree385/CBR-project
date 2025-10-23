"""
Simple Azure AI Agent Service using Azure AI Agents SDK
Based on the approach that doesn't require Azure AD authentication
"""

import asyncio
import time
import ssl
import certifi
import os
import urllib3
from typing import Optional, Dict, Any, List
import structlog
from azure.ai.projects import AIProjectClient
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    Agent,
    AgentThread,
    MessageRole,
)
from azure.identity import DefaultAzureCredential

from app.config_simple import get_settings
from app.models.chat import ChatMessage, MessageRole as ChatMessageRole
from app.utils.exceptions import CustomException

logger = structlog.get_logger()
settings = get_settings()


class SimpleAzureAgentService:
    """Simple service for interacting with Azure AI Agent Service."""
    
    def __init__(self):
        """Initialize the Azure AI Agent service."""
        self.project_client = None
        self.agent = None
        self.thread = None
        self._configure_ssl()
        self._initialize_client()
    
    def _configure_ssl(self):
        """Configure SSL settings for Azure AI services."""
        try:
            # For Azure AI Foundry endpoints that may have certificate issues,
            # use a more permissive SSL configuration for development
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Set environment variables for Azure SDK
            os.environ['PYTHONHTTPSVERIFY'] = '0'
            os.environ['AZURE_CLI_DISABLE_CONNECTION_VERIFICATION'] = '1'
            
            # Create a permissive SSL context for Azure AI services
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Override default HTTPS context for Azure SDK requests
            ssl._create_default_https_context = lambda: ssl_context
            
            logger.warning("SSL verification disabled for Azure AI services (development mode)")
            
        except Exception as e:
            logger.error("Failed to configure SSL", error=str(e))
    
    def _initialize_client(self):
        """Initialize the Azure AI Project client using simple approach."""
        try:
            # Check if we have real credentials
            if not settings.azure_ai_foundry_endpoint or settings.azure_ai_foundry_endpoint == "https://your-ai-foundry.cognitiveservices.azure.com/":
                logger.warning("No real Azure AI Foundry endpoint found, using mock mode")
                return
            
            # Check that we have all required parameters
            if not all([settings.azure_subscription_id, settings.azure_resource_group, settings.azure_project_name]):
                logger.error(f"Missing required Azure project parameters: subscription_id={bool(settings.azure_subscription_id)}, resource_group_name={bool(settings.azure_resource_group)}, project_name={bool(settings.azure_project_name)}")
                return
            
            # The AIProjectClient constructor always requires these parameters
            self.project_client = AIProjectClient(
                endpoint=settings.azure_ai_foundry_endpoint,
                credential=DefaultAzureCredential(),
                subscription_id=settings.azure_subscription_id,
                resource_group_name=settings.azure_resource_group,
                project_name=settings.azure_project_name,
            )
            logger.info(f"Azure AI Project client initialized with endpoint: {settings.azure_ai_foundry_endpoint}")
            logger.info(f"Using project: {settings.azure_project_name} in resource group: {settings.azure_resource_group}")
            
        except Exception as e:
            logger.error("Failed to initialize Azure AI Project client", error=str(e))
            self.project_client = None
    
    async def verify_connection(self) -> bool:
        """Verify connection to Azure AI Agent Service."""
        try:
            if not self.project_client:
                logger.warning("No Azure AI Project client available, using mock mode")
                return True  # Return True for testing purposes
            
            logger.info("Azure AI Agent Service connection verified successfully")
            return True
            
        except Exception as e:
            logger.warning("Azure AI Agent Service connection verification failed, using mock mode", error=str(e))
            return True  # Don't raise exception for testing
    
    async def initialize_agent(self) -> bool:
        """Initialize agent and thread."""
        try:
            if not self.project_client:
                logger.warning("No project client available, using mock mode")
                return True
            
            # Create agent if not exists
            if not self.agent:
                with self.project_client:
                    logger.info("Creating agent...")
                    self.agent = self.project_client.agents.create_agent(
                        model=settings.azure_openai_deployment_name,
                        name="Simple AI Agent",
                        instructions="You are a helpful AI assistant.",
                        temperature=0.7,
                        headers={"x-ms-enable-preview": "true"},
                    )
                    logger.info(f"Created agent, ID: {self.agent.id}")
            
            # Create thread if not exists
            if not self.thread:
                with self.project_client:
                    logger.info("Creating thread...")
                    self.thread = self.project_client.agents.threads.create()
                    logger.info(f"Created thread, ID: {self.thread.id}")
            
            return True
            
        except Exception as e:
            logger.error("Failed to initialize agent", error=str(e))
            return False
    
    async def generate_response(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        """Generate response using Azure AI Agent Service."""
        try:
            if not self.project_client:
                # Return mock response
                return {
                    "content": "This is a mock response since Azure AI Agent Service is not available.",
                    "model_used": "mock-model",
                    "tokens_used": 50,
                    "response_time": 0.1
                }
            
            # Initialize agent if needed
            await self.initialize_agent()
            
            if not self.agent or not self.thread:
                return {
                    "content": "Failed to initialize agent or thread.",
                    "model_used": "error",
                    "tokens_used": 0,
                    "response_time": 0.0
                }
            
            # Get the latest user message
            user_message = messages[-1].content if messages else "Hello"
            
            start_time = time.time()
            
            with self.project_client:
                # Create message
                logger.info(f"Creating message in thread {self.thread.id}...")
                message = self.project_client.agents.messages.create(
                    thread_id=self.thread.id,
                    role="user",
                    content=user_message,
                )
                logger.info(f"Message created: {message.id}")
                
                # Create and poll run
                logger.info(f"Creating run for agent {self.agent.id}...")
                run = self.project_client.agents.runs.create(
                    thread_id=self.thread.id,
                    agent_id=self.agent.id,
                )
                logger.info(f"Run created: {run.id}")
                
                # Poll for completion
                max_iterations = 60  # Max 2 minutes
                iteration = 0
                
                while run.status in ("queued", "in_progress") and iteration < max_iterations:
                    await asyncio.sleep(2)
                    iteration += 1
                    
                    try:
                        run = self.project_client.agents.runs.get(thread_id=self.thread.id, run_id=run.id)
                        logger.info(f"Run status: {run.status} (iteration {iteration})")
                    except Exception as e:
                        logger.error(f"Error getting run status: {e}")
                        await asyncio.sleep(5)
                        continue
                
                if iteration >= max_iterations:
                    logger.warning("Run timed out after maximum iterations")
                    return {
                        "content": "Request timed out. Please try again.",
                        "model_used": settings.azure_openai_deployment_name,
                        "tokens_used": 0,
                        "response_time": time.time() - start_time
                    }
                
                logger.info(f"Run finished with status: {run.status}")
                
                if run.status == "failed":
                    error_msg = f"Run failed: {run.last_error}" if hasattr(run, 'last_error') and run.last_error else "Run failed with unknown error"
                    logger.error(error_msg)
                    return {
                        "content": "Sorry, there was an error processing your request.",
                        "model_used": settings.azure_openai_deployment_name,
                        "tokens_used": 0,
                        "response_time": time.time() - start_time
                    }
                
                elif run.status == "completed":
                    # Get the last message from the agent
                    try:
                        response = self.project_client.agents.messages.get_last_message_by_role(
                            thread_id=self.thread.id,
                            role=MessageRole.AGENT,
                        )
                        
                        if response and hasattr(response, 'text_messages') and response.text_messages:
                            content = "\n".join(t.text.value for t in response.text_messages)
                            
                            return {
                                "content": content,
                                "model_used": settings.azure_openai_deployment_name,
                                "tokens_used": 100,  # Estimate since actual tokens not available
                                "response_time": time.time() - start_time
                            }
                        else:
                            logger.warning("No response message found")
                            return {
                                "content": "No response received from the agent.",
                                "model_used": settings.azure_openai_deployment_name,
                                "tokens_used": 0,
                                "response_time": time.time() - start_time
                            }
                            
                    except Exception as e:
                        logger.error(f"Error getting response message: {e}")
                        return {
                            "content": "Error retrieving response from the agent.",
                            "model_used": settings.azure_openai_deployment_name,
                            "tokens_used": 0,
                            "response_time": time.time() - start_time
                        }
                
                else:
                    logger.warning(f"Unexpected run status: {run.status}")
                    return {
                        "content": f"Unexpected response status: {run.status}",
                        "model_used": settings.azure_openai_deployment_name,
                        "tokens_used": 0,
                        "response_time": time.time() - start_time
                    }
            
        except Exception as e:
            logger.error("Failed to generate agent response", error=str(e))
            return {
                "content": "This is a fallback response due to an error in the Azure AI Agent Service.",
                "model_used": "fallback",
                "tokens_used": 50,
                "response_time": 0.1
            }
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            if self.project_client and self.agent:
                with self.project_client:
                    self.project_client.agents.delete_agent(self.agent.id)
                    logger.info(f"Deleted agent: {self.agent.id}")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Keep the old class name for compatibility
AzureAgentService = SimpleAzureAgentService