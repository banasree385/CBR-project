# CBR Multi-Agent System - Project Overview

## 🏗️ Clean Project Structure

```
python-agent-backend/
├── app/                           # Main application code
│   ├── main.py                   # FastAPI server entry point
│   ├── config_simple.py          # Configuration settings
│   ├── api/                      # API endpoints
│   │   ├── chat.py              # Basic chat endpoints  
│   │   ├── agent.py             # Agent-specific endpoints
│   │   └── multi_agent_chat.py  # Multi-agent system API
│   ├── services/                 # Core business logic
│   │   ├── azure_agent_service.py    # Azure AI integration
│   │   └── multi_agent_system.py     # Multi-agent coordinator
│   ├── models/                   # Data models
│   │   └── chat.py              # Chat message models
│   ├── tools/                    # Custom tools
│   │   └── bing_search.py       # Bing search integration
│   └── utils/                    # Utilities
│       └── logger.py            # Logging configuration
├── data/                         # CBR knowledge base (9 JSON files)
├── static/                       # Web interfaces
│   ├── multi-agent-chatbot.html # Main interface
│   ├── cbr-chatbot.html         # Alternative interface  
│   └── index.html               # Simple interface
├── requirements.txt              # Python dependencies
├── CBR_Functional_Diagram.md     # System flow diagrams
└── CBR_MultiAgent_ClassDiagram.md # Architecture diagrams
```

## 🎯 How It Works

### 1. **Server Entry Point**
- `app/main.py` - FastAPI server with all routes and middleware

### 2. **Multi-Agent System**
- `app/services/multi_agent_system.py` - Contains 6 specialist agents:
  - Theory Exam Agent
  - Practical Exam Agent  
  - Pricing Agent
  - Documents Agent
  - **Booking Agent** (simple version)
  - General CBR Agent

### 3. **API Layer**
- `app/api/multi_agent_chat.py` - Handles multi-agent requests
- Routes user queries to appropriate specialist agents

### 4. **Azure Integration**
- `app/services/azure_agent_service.py` - Manages Azure AI connections
- Handles Bing grounding and vector store search

### 5. **Web Interface**
- `static/multi-agent-chatbot.html` - Main testing interface
- Shows which agent was used for each response

## 🚀 Quick Start

```bash
# Start server
cd /workspaces/CBR-project/python-agent-backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Test in browser
http://localhost:8000/multi-agent-chatbot.html
```

## 🔧 Key Components

1. **Multi-Agent Coordinator** - Routes queries based on intent
2. **Specialist Agents** - Handle specific CBR domains
3. **Azure AI Tools** - Bing search + Vector store
4. **CBR Knowledge Base** - 9 JSON files with procedures
5. **Web Interface** - Real-time chat with agent transparency

## 📊 Current Status

- ✅ **Server running** on port 8000
- ✅ **6 specialist agents** active
- ✅ **Azure AI integrated** with Bing + Vector store  
- ✅ **CBR knowledge base** loaded (9 files)
- ✅ **Web interface** accessible
- 🔄 **Booking agent** can be enhanced later

This clean structure makes it easy to understand the flow, debug issues, and add new features!