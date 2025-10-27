# CBR Multi-Agent Architecture - Demo Block Diagram

## 🏗️ **System Architecture Overview**

```mermaid
graph TB
    %% User Interface Layer
    subgraph "🌐 User Interface Layer"
        UI[Web Chatbot Interface<br/>multi-agent-chatbot.html]
        API_DOC[API Documentation<br/>Swagger UI]
    end

    %% API Gateway Layer
    subgraph "🔌 API Gateway Layer"
        FASTAPI[FastAPI Server<br/>Port 8000]
        HEALTH[Health Endpoint<br/>/health]
        STATUS[Agent Status<br/>/api/v1/foundry/status]
    end

    %% Service Layer
    subgraph "⚙️ Service Layer"
        FOUNDRY_SVC[Foundry Agent Service<br/>foundry_agent_service.py]
        AUTH[Azure AI Credential<br/>AIFoundryCredential]
        RETRY[Retry Logic<br/>3 attempts + backoff]
    end

    %% Azure AI Foundry Layer
    subgraph "☁️ Azure AI Foundry"
        PROJECT[AI Project<br/>prj-kotpagents-croy]
        
        subgraph "🤖 Agents"
            ORCH[Orchestrator Agent<br/>CBR_8_orch<br/>Routes queries]
            AGENT1[Search Agent<br/>cbr_8_search_agent<br/>Provides information]
            AGENT2[Booking Agent<br/>cbr_8_booking_agent<br/>Handles bookings]
        end
        
        THREADS[Thread Management<br/>Conversation context]
        MSGS[Message History<br/>Per session]
    end

    %% Data Layer
    subgraph "📊 Data Layer"
        CBR_DATA[CBR Knowledge Base<br/>License procedures<br/>Renewal processes<br/>Exam booking]
    end

    %% User Flow Connections
    UI --> FASTAPI
    API_DOC --> FASTAPI
    
    FASTAPI --> STATUS
    FASTAPI --> FOUNDRY_SVC
    
    FOUNDRY_SVC --> AUTH
    FOUNDRY_SVC --> RETRY
    
    AUTH --> PROJECT
    PROJECT --> ORCH
    PROJECT --> THREADS
    PROJECT --> MSGS
    
    %% Agent Routing
    ORCH -.->|Routes to| AGENT1
    ORCH -.->|Routes to| AGENT2
    
    AGENT1 --> CBR_DATA
    AGENT2 --> CBR_DATA

    %% Styling
    classDef userLayer fill:#e1f5fe
    classDef apiLayer fill:#f3e5f5
    classDef serviceLayer fill:#e8f5e8
    classDef azureLayer fill:#fff3e0
    classDef agentBox fill:#ffebee
    classDef dataLayer fill:#f1f8e9

    class UI,API_DOC userLayer
    class FASTAPI,HEALTH,STATUS apiLayer
    class FOUNDRY_SVC,AUTH,RETRY serviceLayer
    class PROJECT,THREADS,MSGS azureLayer
    class ORCH,AGENT1,AGENT2 agentBox
    class CBR_DATA dataLayer
```

## 🔄 **Message Flow Diagram**

```mermaid
sequenceDiagram
    participant User
    participant WebUI as Web Interface
    participant API as FastAPI Server
    participant Service as Foundry Service
    participant Azure as Azure AI Foundry
    participant Orch as Orchestrator Agent
    participant Agent1 as Search Agent
    participant Agent2 as Booking Agent

    User->>WebUI: "I need help with license renewal"
    WebUI->>API: POST /api/v1/foundry/orchestrator
    API->>Service: process_message()
    
    Service->>Azure: Create thread & message
    Service->>Orch: Run orchestrator agent
    Orch-->>Service: "Route to Agent 1 for license info"
    Service-->>API: Orchestrator response
    API-->>WebUI: Show routing message
    
    Note over WebUI: Auto-follow-up triggered
    WebUI->>API: POST /api/v1/foundry/agent1
    API->>Service: route_to_specific_agent()
    Service->>Agent1: Run search agent
    Agent1-->>Service: Detailed license renewal info
    Service-->>API: Agent 1 response
    API-->>WebUI: Show detailed information
    WebUI-->>User: Complete response with routing + details
```

## 🎯 **Key Architecture Features**

### **1. Smart Routing System**
- **Orchestrator** analyzes user queries
- **Automatically routes** to appropriate specialist agent
- **Dual response** system (routing + detailed info)

### **2. Reliability Features**
- **Retry Logic**: 3 attempts with 2-second backoff
- **Fallback System**: Mock responses if all attempts fail
- **Thread Recovery**: Creates new threads on retry
- **Health Monitoring**: Real-time agent status

### **3. Azure AI Integration**
- **Real-time Connection**: Direct integration with Azure AI Foundry
- **Thread Management**: Maintains conversation context
- **Message History**: Persistent across sessions
- **Authentication**: Secure token-based access

### **4. User Experience**
- **Consistent Formatting**: Markdown rendering for all responses
- **Agent Identification**: Clear indication of which agent responded
- **Response Times**: Performance metrics displayed
- **Auto-routing**: Seamless experience with automatic follow-ups

## 📋 **Demo Script Points**

### **Show Real-time Architecture**
1. **User Query** → Web interface
2. **API Processing** → FastAPI logs
3. **Azure Integration** → Agent status check
4. **Orchestrator Routing** → Shows routing decision
5. **Agent Response** → Detailed information
6. **Formatted Display** → Professional presentation

### **Highlight Key Benefits**
- ✅ **Real Azure AI agents** (not mock responses)
- ✅ **Intelligent routing** based on query type
- ✅ **Comprehensive responses** with proper formatting
- ✅ **Reliable operation** with retry mechanisms
- ✅ **Scalable architecture** for additional agents

## 🚀 **Live Demo URLs**
- **Web Interface**: http://localhost:8000/static/multi-agent-chatbot.html
- **API Docs**: http://localhost:8000/docs
- **Agent Status**: http://localhost:8000/api/v1/foundry/status
- **Health Check**: http://localhost:8000/health

---

*This architecture demonstrates a production-ready multi-agent system built with Azure AI Foundry, featuring intelligent routing, comprehensive error handling, and professional user experience.*