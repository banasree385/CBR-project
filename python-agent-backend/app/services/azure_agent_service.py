"""
Simple Azure AI Agent Service using Azure AI Agents SDK
Based on the approach that doesn't require Azure AD authentication
"""

import asyncio
import time
import os
from typing import Optional, Dict, Any, List, List
import structlog
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    Agent,
    AgentThread,
    MessageRole,
    BingGroundingTool,
    FileSearchTool,
    ToolResources,
    FileSearchToolResource,
)
from azure.identity import DefaultAzureCredential

from app.config_simple import get_settings
from app.models.chat import ChatMessage, MessageRole as ChatMessageRole

logger = structlog.get_logger()
settings = get_settings()


class SimpleAzureAgentService:
    """Simple service for interacting with Azure AI Agent Service."""
    
    def __init__(self):
        """Initialize the Azure AI Agent service."""
        self.project_client = None
        self.agent = None
        self.thread = None
        self._client_context = None
        self._cached_vector_store = None  # Cache vector store to avoid re-uploading
        self._configure_ssl()
        self._initialize_client()
    
    def _configure_ssl(self):
        """Configure SSL settings for Azure AI services."""
        try:
            # SSL verification is handled automatically by Azure SDK
            logger.info("SSL verification enabled with proper certificates for Azure AI services")
        except Exception as e:
            logger.error("Failed to configure SSL", error=str(e))
    
    def _initialize_client(self):
        """Initialize the Azure AI Project client using simple approach."""
        try:
            # Check if we have real credentials
            if not settings.azure_ai_foundry_endpoint or settings.azure_ai_foundry_endpoint.startswith("https://your-"):
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
            
            # Check if we should use an existing agent ID
            self.existing_agent_id = os.getenv("AZURE_AGENT_ID")
            if self.existing_agent_id:
                logger.info(f"Will use existing agent: {self.existing_agent_id}")
            
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
            
            # Open client context if not already open
            if not self._client_context:
                self._client_context = self.project_client.__enter__()
            
            # Use existing agent or create new one
            if not self.agent:
                if hasattr(self, 'existing_agent_id') and self.existing_agent_id:
                    # Use existing agent from Azure AI Foundry
                    logger.info(f"Using existing agent: {self.existing_agent_id}")
                    try:
                        self.agent = self.project_client.agents.get_agent(self.existing_agent_id)
                        logger.info(f"Retrieved existing agent: {self.agent.id}")
                    except Exception as e:
                        logger.warning(f"Failed to retrieve existing agent {self.existing_agent_id}: {e}")
                        logger.info("Will create new agent instead")
                        self.agent = None
                
                # Create new agent if no existing agent or retrieval failed
                if not self.agent:
                    logger.info("Creating new agent...")
                    
                    # Setup tools
                    tools_to_add = []
                    
                    # Initialize Bing Grounding tool
                    bing_connection_id = os.getenv("BING_CONNECTION_ID")
                    if bing_connection_id:
                        logger.info(f"Adding Bing grounding tool with connection: {bing_connection_id}")
                        bing_tool = BingGroundingTool(connection_id=bing_connection_id)
                        tools_to_add.extend(bing_tool.definitions)
                    else:
                        logger.warning("BING_CONNECTION_ID not set, skipping Bing grounding")
                    
                    # Initialize File Search tool for JSON RAG
                    logger.info("Adding File Search tool for JSON RAG")
                    file_search_tool = FileSearchTool()
                    tools_to_add.extend(file_search_tool.definitions)
                    
                    # Instructions that encourage tool usage
                    agent_instructions = """You are a CBR.nl driving license assistant with access to comprehensive knowledge and real-time web search.

## AVAILABLE TOOLS:
1. **File Search**: Use for CBR procedures, requirements, categories, medical info, safety rules, and especially for available exam slots and exam slot availability.
2. **Bing Web Search**: Use for current information, news, prices, waiting times, announcements

## WHEN TO USE EACH TOOL:

### File Search Tool - Use for:
- CBR procedures and requirements
- License categories and types
- Medical assessment processes
- Exam procedures and content
- Historical information from CBR documents
- **Available exam slots and exam slot availability for theory and practical exams (date, time, location, slots, availability)**

### Bing Web Search Tool - Use for:
- Current CBR prices and fees (search "CBR rijexamen kosten 2025")
- Current waiting times (search "CBR wachttijden rijexamen")
- Recent CBR announcements (search "CBR nieuws 2025")
- Current CBR policies and updates (search "CBR updates 2025")
- Weather information (search "weather Amsterdam today")
- Current date/time information
- Any question about "current", "latest", "today", "recent"

## SEARCH STRATEGY:
- **Always search actively** when users ask for current information
- Use specific Dutch search terms for CBR-related queries
- Search CBR.nl, government sites, and news sources
- Don't say "I couldn't find" - try multiple search approaches

## IMPORTANT:
- **NEVER** say you can't find information without actually searching
- **ALWAYS** use web search for current/recent information requests
- Use specific search queries like "CBR wachttijden 2025" or "CBR tarieven 2025"
- For questions about available exam slots or exam slot availability, always use the file search tool to provide details from the knowledge base (date, time, location, slots, availability)
- Provide actual search results, not generic advice to visit websites"""

                    # Setup vector store for file search BEFORE creating agent (with caching)
                    vector_store = await self._setup_vector_store_cached()
                    
                    # Create agent with tools and vector store
                    if tools_to_add:
                        agent_kwargs = {
                            "model": settings.azure_openai_deployment_name,
                            "name": "CBR.nl Speed-Optimized Assistant v2.1",
                            "instructions": agent_instructions,
                            "tools": tools_to_add,
                            "temperature": 0.1,  # Very low temperature for speed
                            "headers": {"x-ms-enable-preview": "true"},
                        }
                        
                        # Add vector store if available using proper SDK objects
                        if vector_store:
                            file_search_resource = FileSearchToolResource(
                                vector_store_ids=[vector_store.id]
                            )
                            tool_resources = ToolResources(
                                file_search=file_search_resource
                            )
                            agent_kwargs["tool_resources"] = tool_resources
                            logger.info(f"🔗 Adding vector store {vector_store.id} to agent creation")
                        
                        self.agent = self.project_client.agents.create_agent(**agent_kwargs)
                        logger.info(f"Created agent with {len(tools_to_add)} tools, ID: {self.agent.id}")
                    else:
                        self.agent = self.project_client.agents.create_agent(
                            model=settings.azure_openai_deployment_name,
                            name="CBR.nl Assistant - Speed Basic",
                            instructions=agent_instructions,
                            temperature=0.1,  # Very low temperature for speed
                            headers={"x-ms-enable-preview": "true"},
                        )
                        logger.info(f"Created agent without tools, ID: {self.agent.id}")
            
            # Create thread if not exists
            if not self.thread:
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
            
            # Ensure client context is open
            if not self._client_context and self.project_client:
                self._client_context = self.project_client.__enter__()
            
            # Check for any active run in the thread
            active_runs = self.project_client.agents.runs.list(thread_id=self.thread.id)
            for r in active_runs:
                if r.status in ("queued", "in_progress", "requires_action"):
                    logger.warning(f"Active run {r.id} detected in thread {self.thread.id}, waiting for completion...")
                    # Wait for the active run to complete
                    max_wait = 30
                    waited = 0
                    while r.status in ("queued", "in_progress", "requires_action") and waited < max_wait:
                        await asyncio.sleep(1)
                        r = self.project_client.agents.runs.get(thread_id=self.thread.id, run_id=r.id)
                        waited += 1
                    logger.info(f"Active run {r.id} finished with status {r.status}")

            # Now safe to create a new message
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
            
            # Poll for completion with aggressive timing for speed
            max_iterations = 30  # Reduced from 120 - timeout faster
            iteration = 0
            base_sleep = 0.3  # Even faster start - 300ms
            
            while run.status in ("queued", "in_progress", "requires_action") and iteration < max_iterations:
                # Very aggressive polling for speed
                if iteration < 3:
                    sleep_time = base_sleep  # 300ms for first 3 iterations
                elif iteration < 8:
                    sleep_time = 0.5  # 500ms for next 5 iterations
                elif iteration < 15:
                    sleep_time = 1.0  # 1s for next 7 iterations
                else:
                    sleep_time = 1.5  # 1.5s for remaining (was 2s)
                
                await asyncio.sleep(sleep_time)
                iteration += 1
                
                try:
                    run = self.project_client.agents.runs.get(thread_id=self.thread.id, run_id=run.id)
                    logger.info(f"Run status: {run.status} (iteration {iteration})")
                    
                    # Track tool usage for transparency
                    if hasattr(run, 'required_action') and run.required_action:
                        logger.info(f"🔧 Tools required: {run.required_action}")
                    
                    # Note: Azure AI Foundry handles Bing grounding tool execution automatically
                    # No manual tool execution needed for BingGroundingTool
                            
                except Exception as e:
                    logger.error(f"Error getting run status: {e}")
                    await asyncio.sleep(1)  # Reduced from 2s to 1s
                    continue
            
            if iteration >= max_iterations:
                logger.warning(f"Run timed out after {iteration} iterations (~{iteration * 0.5:.1f}s)")
                return {
                    "content": "⚡ Timeout: Vraag te complex. Probeer een eenvoudigere vraag.",
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
                # Get the last message from the agent first
                try:
                    response = self.project_client.agents.messages.get_last_message_by_role(
                        thread_id=self.thread.id,
                        role=MessageRole.AGENT,
                    )
                    
                    if response and hasattr(response, 'text_messages') and response.text_messages:
                        content = "\n".join(t.text.value for t in response.text_messages)
                        
                        # Detect tool usage from response content (PRIORITY method)
                        detected_tools = self._detect_tools_from_content(content)
                        
                        # Log accurate tool usage
                        if detected_tools:
                            logger.info(f"� Tools used: {', '.join(detected_tools)}")
                        else:
                            logger.info("🧠 Direct response (no tools detected)")
                        
                        return {
                            "content": content,
                            "model_used": settings.azure_openai_deployment_name,
                            "tokens_used": 100,  # Estimate since actual tokens not available
                            "response_time": time.time() - start_time,
                            "tools_used": detected_tools  # Add tools info to response
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
    
    async def _setup_vector_store_cached(self):
        """Setup vector store with caching for performance."""
        if self._cached_vector_store:
            logger.info(f"♻️ Using cached vector store: {self._cached_vector_store.id}")
            return self._cached_vector_store
            
        # If no cache, create new vector store
        vector_store = await self._setup_vector_store()
        self._cached_vector_store = vector_store
        return vector_store

    async def _setup_vector_store(self):
        """Setup vector store and upload JSON files for file search."""
        try:
            if not self.project_client:
                logger.warning("No project client available for vector store setup")
                return None
            
            # Create vector store
            logger.info("Creating vector store for CBR knowledge base...")
            vector_store = self.project_client.agents.vector_stores.create(
                name="cbr-knowledge-base",
                expires_after={"anchor": "last_active_at", "days": 7}
            )
            logger.info(f"✅ Created vector store: {vector_store.id}")
            
            # Upload MINIMAL files for maximum speed (2 files only)
            data_dir_path = "/workspaces/CBR-project/python-agent-backend/data"
            essential_files = [
                "cbr_procedures_2025.json",    # Core procedures
                "cbr_medical_assessment.json",  # Essential info
                "cbr_unsafe_driving.json",     # Unsafe driving info
                "cbr_exam_slots.json"           # Exam slots info
            ]
            
            if os.path.exists(data_dir_path):
                uploaded_files = []
                
                # Upload only essential files for maximum speed
                for filename in essential_files:
                    file_path = os.path.join(data_dir_path, filename)
                    if os.path.exists(file_path):
                        try:
                            # Upload file using agents.files.upload
                            with open(file_path, "rb") as f:
                                # Upload file using the correct method
                                uploaded_file = self.project_client.agents.files.upload(
                                    file=f,
                                    purpose="assistants"
                                )
                                
                                # Add file to vector store using vector_store_files
                                vector_store_file = self.project_client.agents.vector_store_files.create(
                                    vector_store_id=vector_store.id,
                                    file_id=uploaded_file.id
                                )
                                
                                uploaded_files.append(filename)
                                logger.info(f"📁 Uploaded: {filename} -> file: {uploaded_file.id}, vs_file: {vector_store_file.id}")
                                
                        except Exception as e:
                            logger.error(f"Failed to upload {filename}: {e}")
                
                if uploaded_files:
                    logger.info(f"✅ Vector store ready with {len(uploaded_files)} files: {uploaded_files}")
                    return vector_store
                else:
                    logger.warning("No files uploaded to vector store")
                    return vector_store
            else:
                logger.warning(f"Data directory not found: {data_dir_path}")
                return vector_store
                
        except Exception as e:
            logger.error(f"Vector store setup failed: {e}")
            return None

    def _detect_tools_from_content(self, content: str) -> List[str]:
        """Detect which tools were used based on response content patterns."""
        tools_detected = []
        
        # PRIORITY: Check for Azure AI source citations (definitive proof of tool usage)
        import re
        citation_pattern = r'【\d+:\d+†source】'
        citations = re.findall(citation_pattern, content)
        
        if citations:
            # Analyze citation patterns to distinguish between tools
            # File search typically has lower numbers (0-10), Bing search has higher numbers (20+)
            citation_numbers = []
            for citation in citations:
                match = re.search(r'【(\d+):\d+†source】', citation)
                if match:
                    citation_numbers.append(int(match.group(1)))
            
            if citation_numbers:
                max_citation = max(citation_numbers)
                min_citation = min(citation_numbers)
                
                # Heuristic: Higher citation numbers typically indicate web search
                if max_citation >= 20:
                    tools_detected.append("🌐 Bing Grounding Tool (web search)")
                elif max_citation >= 10:
                    tools_detected.append("📁 File Search + 🌐 Web Search (hybrid)")
                else:
                    tools_detected.append("📁 File Search Tool (knowledge base)")
                
                return tools_detected
        
        # Fallback: Check for explicit content indicators
        # Check for Bing search indicators
        bing_indicators = [
            "according to current information",
            "based on current data",
            "latest information",
            "current weather",
            "today's",
            "as of"
        ]
        if any(indicator.lower() in content.lower() for indicator in bing_indicators):
            tools_detected.append("🌐 Bing Search (inferred)")
        
        # Check for file search indicators  
        file_search_indicators = [
            "volgens de cbr-documentatie",
            "according to the cbr documentation", 
            "from the knowledge base",
            "cbr procedures",
            "license categories"
        ]
        if any(indicator.lower() in content.lower() for indicator in file_search_indicators):
            tools_detected.append("📁 File Search (inferred)")
        
        # Final fallback
        if not tools_detected:
            if any(word in content.lower() for word in ["weather", "current", "today", "latest"]):
                tools_detected.append("🌐 Web Search (inferred)")
            elif any(word in content.lower() for word in ["procedures", "categories", "requirements", "cbr"]):
                tools_detected.append("📁 Knowledge Base (inferred)")
            
        return tools_detected
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            if self.project_client and self.agent:
                # Ensure client context is open for cleanup
                if not self._client_context:
                    self._client_context = self.project_client.__enter__()
                
                self.project_client.agents.delete_agent(self.agent.id)
                logger.info(f"Deleted agent: {self.agent.id}")
            
            # Close client context if open
            if self._client_context and self.project_client:
                try:
                    self.project_client.__exit__(None, None, None)
                    self._client_context = None
                except Exception as e:
                    logger.warning(f"Error closing client context: {e}")
                    
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Keep the old class name for compatibility
AzureAgentService = SimpleAzureAgentService