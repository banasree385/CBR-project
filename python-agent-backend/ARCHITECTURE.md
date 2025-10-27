# CBR Agent Project Architecture

## 🏗️ Simple Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────┤
│  • Web Browser (HTML/JS)                                   │
│  • curl/Postman (API Testing)                              │
│  • Mobile Apps (Future)                                    │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP/REST API Calls
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   API LAYER                                 │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Server (main.py)                                  │
│  ├── /health                                               │
│  ├── /api/v1/chat/message                                  │
│  ├── /api/v1/chat/history                                  │
│  └── /api/v1/agent/*                                       │
└─────────────────┬───────────────────────────────────────────┘
                  │ Python Function Calls
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                 SERVICE LAYER                               │
├─────────────────────────────────────────────────────────────┤
│  Azure Agent Service (azure_agent_service.py)              │
│  ├── Agent Management                                      │
│  ├── Thread Management                                     │
│  ├── Tool Coordination                                     │
│  └── Response Processing                                   │
└─────────────────┬───────────────────────────────────────────┘
                  │ Azure AI SDK Calls
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  AZURE AI LAYER                            │
├─────────────────────────────────────────────────────────────┤
│  Azure AI Foundry Project                                  │
│  ├── GPT-4o Model                                          │
│  ├── Agent Runtime                                         │
│  ├── Tool Orchestration                                    │
│  └── Authentication                                        │
└─────────┬───────────────────────┬───────────────────────────┘
          │                       │
          ▼                       ▼
┌─────────────────────┐   ┌─────────────────────┐
│   KNOWLEDGE TOOLS   │   │    WEB TOOLS        │
├─────────────────────┤   ├─────────────────────┤
│ File Search Tool    │   │ Bing Grounding Tool │
│ ├── Vector Store    │   │ ├── Web Search      │
│ ├── CBR Documents   │   │ ├── Current Info    │
│ └── Semantic Search │   │ └── Real-time Data  │
└─────────────────────┘   └─────────────────────┘
```

## 📁 Directory Structure

```
python-agent-backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config_simple.py     # Configuration and settings
│   ├── api/                 # REST API endpoints
│   │   ├── chat.py          # Chat endpoints
│   │   └── agent.py         # Agent management endpoints
│   ├── services/            # Business logic layer
│   │   └── azure_agent_service.py  # Core Azure AI integration
│   ├── models/              # Pydantic data models
│   ├── tools/               # Custom tool implementations
│   └── utils/               # Utility functions
├── data/                    # CBR knowledge base (JSON files)
├── static/                  # Frontend HTML/CSS/JS files
├── requirements.txt         # Python dependencies
└── .env                     # Environment configuration
```

## 🔄 Data Flow

### 1. **User Request Flow**
```
User Question → FastAPI → Chat API → Azure Agent Service → Azure AI Foundry
```

### 2. **Tool Selection Flow**
```
Azure AI Agent → Analyzes Question → Selects Tool(s) → Executes Search → Returns Results
```

### 3. **Response Flow**
```
Tool Results → Azure AI Agent → Processing → Response → FastAPI → User
```

## 🔧 Key Components

### **FastAPI Layer**
- **Purpose**: REST API server
- **Responsibilities**: 
  - HTTP request handling
  - CORS management
  - Static file serving
  - Error handling

### **Azure Agent Service**
- **Purpose**: Core AI integration
- **Responsibilities**:
  - Agent lifecycle management
  - Tool orchestration
  - Vector store management
  - Response processing

### **Tools System**
- **File Search Tool**: 
  - Searches uploaded CBR documents
  - Uses vector store for semantic search
  - Provides source citations
  
- **Bing Grounding Tool**:
  - Searches web for current information
  - Gets real-time data
  - Accesses latest news/updates

### **Knowledge Base**
- **Format**: JSON files in `/data/` directory
- **Content**: CBR procedures, requirements, regulations
- **Access**: Through vector store and file search tool

## 🌐 External Dependencies

- **Azure AI Foundry**: AI agent hosting and management
- **Azure OpenAI**: GPT-4o model for language processing
- **Bing Search**: Web search for current information
- **Vector Store**: Document storage and semantic search

## 🔒 Security & Configuration

- **Environment Variables**: Stored in `.env` file
- **Azure Authentication**: Using DefaultAzureCredential
- **API Keys**: Secured through Azure Key Vault integration
- **CORS**: Configured for cross-origin requests

## 📊 Tool Usage Patterns

| Question Type | Tool Used | Example |
|---------------|-----------|---------|
| CBR Procedures | File Search | "What are CBR license requirements?" |
| Current Prices | Bing Search | "What are current CBR test costs?" |
| Weather/Time | Bing Search | "What's the weather today?" |
| Historical Info | File Search | "CBR medical assessment process" |

## 🚀 Deployment Architecture

```
Development:
├── Local FastAPI Server (port 8000)
├── Python Virtual Environment
└── Direct Azure AI connection

Production (Future):
├── Docker Container
├── Azure App Service
├── Load Balancer
└── Azure AI Foundry (same)
```

This architecture provides a clean separation of concerns with scalable, maintainable components focused on CBR driving license assistance.