# Azure AI Foundry Agent - Python Backend

A simplified Python backend service for Azure AI Foundry agent integration.

## Project Structure

```
python-agent-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config_simple.py        # Configuration and environment variables
│   ├── models/
│   │   ├── __init__.py
│   │   └── chat.py             # Chat request/response models
│   ├── services/
│   │   ├── __init__.py
│   │   └── azure_agent_service.py # Azure AI Agent Service integration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py             # Chat endpoints
│   │   └── agent.py            # Simplified agent endpoints
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py             # Authentication middleware
│   └── utils/
│       ├── __init__.py
│       ├── logger.py           # Logging utilities
│       └── exceptions.py       # Custom exceptions
├── static/                     # Frontend files
├── requirements.txt
├── .env
├── test_server.py             # Simple server launcher
└── README.md
```

## Features

- **FastAPI Framework**: High-performance Python web framework
- **Azure AI Agent Service**: Direct connection to Azure AI Foundry Agents
- **Simplified Architecture**: Direct Chat API → Azure Agent Service
- **Azure AD Authentication**: Uses DefaultAzureCredential
- **Async Support**: Asynchronous request handling
- **Simple Logging**: Structured logging with structlog

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Azure authentication**:
   ```bash
   az login
   az account set --subscription "your-subscription-id"
   ```

3. **Run the development server**:
   ```bash
   python test_server.py
   ```

4. **Access the API**:
   - API Documentation: http://localhost:8001/docs
   - Chat Interface: http://localhost:8001/chatbot.html
   - Chat API: http://localhost:8001/api/v1/chat/message
   - Agent Status: http://localhost:8001/api/v1/agent/status

## Environment Variables

Required variables in `.env`:
- `AZURE_AI_FOUNDRY_ENDPOINT`: Your Azure AI Foundry project endpoint
- `AZURE_AI_FOUNDRY_KEY`: Azure AI Foundry API key
- `AZURE_SUBSCRIPTION_ID`: Azure subscription ID
- `AZURE_RESOURCE_GROUP_NAME`: Azure resource group name
- `AZURE_PROJECT_NAME`: Azure AI Foundry project name
- `AGENT_MODEL_DEPLOYMENT_NAME`: GPT model deployment name (e.g., gpt41)

## API Endpoints

- `POST /api/v1/chat/message`: Send message to Azure Agent Service
- `GET /api/v1/chat/history/{session_id}`: Get chat history
- `POST /api/v1/agent/status`: Get Azure Agent Service status
- `POST /api/v1/agent/simple-query`: Send simple query to agent

## Architecture

**Simplified Flow:**
```
Frontend → Chat API → Azure Agent Service → Azure AI Foundry → GPT Model
```

This simplified architecture removes unnecessary abstraction layers and connects directly to Azure AI Foundry's Agent Service for creating real agents.