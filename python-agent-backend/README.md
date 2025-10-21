# Azure AI Foundry Agent - Python Backend

A Python backend service for Azure AI Foundry agent integration with GPT-4 connectivity.

## Project Structure

```
python-agent-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration and environment variables
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chat.py             # Chat request/response models
│   │   └── agent.py            # Agent models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── azure_ai_service.py # Azure AI Foundry integration
│   │   ├── gpt_service.py      # GPT-4 service integration
│   │   └── auth_service.py     # Azure authentication
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py             # Chat endpoints
│   │   └── agent.py            # Agent management endpoints
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication middleware
│   │   └── cors.py             # CORS configuration
│   └── utils/
│       ├── __init__.py
│       ├── logger.py           # Logging utilities
│       └── exceptions.py       # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_chat.py
│   └── test_agent.py
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Features

- **FastAPI Framework**: High-performance Python web framework
- **Azure AI Foundry Integration**: Direct connection to Azure AI services
- **GPT-4 Connectivity**: OpenAI GPT-4 model integration
- **Authentication**: Azure Active Directory integration
- **Async Support**: Asynchronous request handling
- **Monitoring**: Comprehensive logging and error handling
- **Containerization**: Docker support for deployment

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your Azure and OpenAI credentials
   ```

3. **Run the development server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Chat Endpoint: http://localhost:8000/api/v1/chat
   - Agent Status: http://localhost:8000/api/v1/agent/status

## Environment Variables

- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key
- `AZURE_OPENAI_DEPLOYMENT_NAME`: GPT-4 deployment name
- `AZURE_CLIENT_ID`: Azure AD application client ID
- `AZURE_CLIENT_SECRET`: Azure AD application client secret
- `AZURE_TENANT_ID`: Azure AD tenant ID
- `AZURE_AI_FOUNDRY_ENDPOINT`: Azure AI Foundry endpoint
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)

## API Endpoints

- `POST /api/v1/chat/message`: Send message to agent
- `GET /api/v1/chat/history/{session_id}`: Get chat history
- `POST /api/v1/agent/create`: Create new agent
- `GET /api/v1/agent/status`: Get agent status
- `PUT /api/v1/agent/configure`: Configure agent settings

## Deployment

### Azure Container Instances
```bash
az container create --resource-group your-rg --name ai-agent-backend --image your-image
```

### Azure App Service
```bash
az webapp create --resource-group your-rg --plan your-plan --name ai-agent-backend
```

See detailed deployment instructions in the deployment guide.