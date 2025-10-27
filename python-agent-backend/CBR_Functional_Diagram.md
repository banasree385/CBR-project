# CBR Multi-Agent System - Functional Diagram

## 🎯 System Overview: How It All Works Together

```mermaid
graph TB
    %% User Interface Layer
    subgraph "User Interface Layer"
        UI[Web Interface - chatbot.html]
        WS[WebSocket Connection]
        JS[Frontend JavaScript - chatbot.js]
    end
    
    %% API Gateway Layer
    subgraph "API Gateway Layer"
        FAST[FastAPI Server - main.py]
        AUTH[Authentication Middleware]
        CORS[CORS Middleware]
    end
    
    %% Orchestration Layer
    subgraph "CBR Multi-Agent Orchestration"
        ORCH[CBRMultiAgentOrchestrator]
        ROUTER[Query Router & Intent Classifier]
        REG[Agent Registry]
    end
    
    %% Agent Layer
    subgraph "Specialized Agents"
        SEARCH[CBR Search Agent]
        BOOKING[CBR Booking Agent]
        FUTURE[Future Agents...]
    end
    
    %% Tools & Resources Layer
    subgraph "Tools & Resources"
        BING[Bing Search Tool]
        VECTOR[Vector Store Search]
        FUNC[Function Calling]
        KB[CBR Knowledge Base]
    end
    
    %% Data Layer
    subgraph "Data Sources"
        JSON1[cbr_procedures_2025.json]
        JSON2[cbr_medical_assessment.json] 
        JSON3[cbr_unsafe_driving.json]
        LIVE[Live CBR.nl Data]
    end
    
    %% Azure AI Layer
    subgraph "Azure AI Platform"
        AI[Azure AI Foundry]
        GPT[GPT-4o-mini Model]
        VS[Vector Store]
    end
    
    %% Flow Connections
    UI --> WS
    WS --> FAST
    FAST --> AUTH
    AUTH --> CORS
    CORS --> ORCH
    
    ORCH --> ROUTER
    ROUTER --> REG
    REG --> SEARCH
    REG --> BOOKING
    REG --> FUTURE
    
    SEARCH --> BING
    SEARCH --> VECTOR
    BOOKING --> FUNC
    BOOKING --> BING
    
    BING --> LIVE
    VECTOR --> KB
    KB --> JSON1
    KB --> JSON2
    KB --> JSON3
    
    SEARCH --> AI
    BOOKING --> AI
    AI --> GPT
    AI --> VS
    
    %% Response Flow (dotted lines)
    AI -.-> SEARCH
    AI -.-> BOOKING
    SEARCH -.-> ORCH
    BOOKING -.-> ORCH
    ORCH -.-> FAST
    FAST -.-> WS
    WS -.-> UI
    
    %% Styling
    classDef userLayer fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef apiLayer fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef orchestrationLayer fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef agentLayer fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef toolLayer fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef dataLayer fill:#f1f8e9,stroke:#689f38,stroke-width:2px
    classDef azureLayer fill:#e0f2f1,stroke:#00796b,stroke-width:2px
    
    class UI,WS,JS userLayer
    class FAST,AUTH,CORS apiLayer
    class ORCH,ROUTER,REG orchestrationLayer
    class SEARCH,BOOKING,FUTURE agentLayer
    class BING,VECTOR,FUNC,KB toolLayer
    class JSON1,JSON2,JSON3,LIVE dataLayer
    class AI,GPT,VS azureLayer
```

## 🔄 Request Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant WebUI as Web Interface
    participant FastAPI as FastAPI Server
    participant Orchestrator as CBR Orchestrator
    participant Router as Intent Router
    participant SearchAgent as Search Agent
    participant BookingAgent as Booking Agent
    participant Azure as Azure AI
    participant Tools as Tools & Data
    
    %% User initiates request
    User->>WebUI: "Hoe kan ik theorie-examen boeken?"
    WebUI->>FastAPI: POST /chat/message
    FastAPI->>Orchestrator: orchestrate(query, session_id)
    
    %% Intent classification
    Orchestrator->>Router: classify_intent(query)
    Router-->>Orchestrator: "booking_intent"
    
    %% Route to appropriate agent
    alt Booking Intent
        Orchestrator->>BookingAgent: _execute_booking_agent()
        BookingAgent->>Azure: create_thread_and_process_run()
        Azure->>Tools: Use Function Calling + Bing
        Tools-->>Azure: Booking procedures & current info
        Azure-->>BookingAgent: Comprehensive booking response
        BookingAgent-->>Orchestrator: Formatted response
    else Search Intent
        Orchestrator->>SearchAgent: _execute_search_agent()
        SearchAgent->>Azure: create_thread_and_process_run()
        Azure->>Tools: Use Vector Store + Bing
        Tools-->>Azure: Search results & knowledge
        Azure-->>SearchAgent: Detailed information
        SearchAgent-->>Orchestrator: Formatted response
    end
    
    %% Response back to user
    Orchestrator-->>FastAPI: {success: true, response: "...", agent_used: "..."}
    FastAPI-->>WebUI: JSON response with metadata
    WebUI-->>User: Formatted chat response with tool indicators
    
    Note over User,Tools: End-to-end: ~2-4 seconds with optimization
```

## 🎯 Agent Decision Tree

```mermaid
flowchart TD
    START([User Query Received]) --> CLASSIFY{Intent Classification}
    
    CLASSIFY -->|Contains: boeken, inplannen, afspraak, beschikbaar, annuleren| BOOKING[Route to Booking Agent]
    CLASSIFY -->|Contains: theorie, praktijk, regels, kosten, documenten| SEARCH[Route to Search Agent]
    CLASSIFY -->|Ambiguous| DEFAULT[Default to Search Agent]
    
    BOOKING --> BOOKING_TOOLS{Select Tools}
    BOOKING_TOOLS -->|Real-time info needed| BING_B[Bing Search + Function Calling]
    BOOKING_TOOLS -->|Procedure info needed| FUNC_B[Function Calling Only]
    
    SEARCH --> SEARCH_TOOLS{Select Tools}
    SEARCH_TOOLS -->|Current info needed| BING_S[Bing Search + Vector Store]
    SEARCH_TOOLS -->|Knowledge base sufficient| VECTOR_S[Vector Store Only]
    
    BING_B --> RESPONSE_B[Booking Response]
    FUNC_B --> RESPONSE_B
    BING_S --> RESPONSE_S[Search Response]
    VECTOR_S --> RESPONSE_S
    
    RESPONSE_B --> FORMAT[Format & Return]
    RESPONSE_S --> FORMAT
    FORMAT --> END([Response to User])
    
    %% Styling
    classDef startEnd fill:#e8f5e8,stroke:#4caf50,stroke-width:3px
    classDef decision fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    classDef process fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    classDef tools fill:#fce4ec,stroke:#e91e63,stroke-width:2px
    
    class START,END startEnd
    class CLASSIFY,BOOKING_TOOLS,SEARCH_TOOLS decision
    class BOOKING,SEARCH,DEFAULT,RESPONSE_B,RESPONSE_S,FORMAT process
    class BING_B,FUNC_B,BING_S,VECTOR_S tools
```

## 🛠️ Tool Selection Strategy

```mermaid
graph LR
    subgraph "Search Agent Tools"
        ST1[Bing Search] --> ST1_USE["Current CBR.nl info<br/>Price updates<br/>New regulations"]
        ST2[Vector Store] --> ST2_USE["Detailed procedures<br/>Medical requirements<br/>Safety guidelines"]
        ST3[Combined] --> ST3_USE["Comprehensive answers<br/>with current + historical data"]
    end
    
    subgraph "Booking Agent Tools"
        BT1[Function Calling] --> BT1_USE["Booking procedures<br/>Step-by-step guidance<br/>Document requirements"]
        BT2[Bing Search] --> BT2_USE["Current availability<br/>Real-time booking info<br/>System status"]
        BT3[Combined] --> BT3_USE["Complete booking assistance<br/>with live data"]
    end
    
    subgraph "Tool Selection Logic"
        QUERY[User Query] --> ANALYZE{Analyze Query Type}
        ANALYZE -->|"What costs..."| CURRENT[Need Current Info]
        ANALYZE -->|"How to..."| PROCEDURE[Need Procedures]
        ANALYZE -->|"When can I..."| REALTIME[Need Real-time Data]
        
        CURRENT --> USE_BING[Use Bing Search]
        PROCEDURE --> USE_VECTOR[Use Vector Store]
        REALTIME --> USE_BOTH[Use Both Tools]
    end
    
    classDef searchTools fill:#e8f5e8,stroke:#4caf50,stroke-width:2px
    classDef bookingTools fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    classDef logic fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    
    class ST1,ST2,ST3,ST1_USE,ST2_USE,ST3_USE searchTools
    class BT1,BT2,BT3,BT1_USE,BT2_USE,BT3_USE bookingTools
    class QUERY,ANALYZE,CURRENT,PROCEDURE,REALTIME,USE_BING,USE_VECTOR,USE_BOTH logic
```

## 📊 System Performance & Optimization

```mermaid
graph TB
    subgraph "Performance Optimization"
        CACHE[Vector Store Caching]
        TEMP[Temperature: 0.1]
        POLL[300ms Polling]
        LIMIT[1-Tool Limit per Agent]
        ENGLISH[English Instructions for Speed]
    end
    
    subgraph "Response Times"
        FAST_Q["Simple queries<br/>(Vector store only)<br/>~800ms"]
        MED_Q["Medium queries<br/>(Single tool)<br/>~2-3 seconds"]
        COMPLEX_Q["Complex queries<br/>(Multiple tools)<br/>~3-5 seconds"]
    end
    
    subgraph "Quality Metrics"
        ACCURACY["High Accuracy<br/>(Grounded responses)"]
        RELEVANCE["Context Relevance<br/>(Intent-based routing)"]
        COMPLETENESS["Complete Information<br/>(Multi-source data)"]
    end
    
    CACHE --> FAST_Q
    TEMP --> ACCURACY
    POLL --> MED_Q
    LIMIT --> COMPLEX_Q
    ENGLISH --> FAST_Q
    
    classDef optimization fill:#e8f5e8,stroke:#4caf50,stroke-width:2px
    classDef performance fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    classDef quality fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    
    class CACHE,TEMP,POLL,LIMIT,ENGLISH optimization
    class FAST_Q,MED_Q,COMPLEX_Q performance
    class ACCURACY,RELEVANCE,COMPLETENESS quality
```

## 🔄 Agent Lifecycle Management

```mermaid
stateDiagram-v2
    [*] --> Initialization
    
    state "System Startup" as Initialization {
        [*] --> LoadConfig
        LoadConfig --> InitAzure
        InitAzure --> SetupVectorStore
        SetupVectorStore --> CreateAgents
        CreateAgents --> RegisterAgents
        RegisterAgents --> [*]
    }
    
    Initialization --> Ready
    
    state "Active Operation" as Ready {
        [*] --> WaitingForQuery
        WaitingForQuery --> ClassifyIntent
        ClassifyIntent --> RouteToAgent
        RouteToAgent --> ProcessQuery
        ProcessQuery --> GenerateResponse
        GenerateResponse --> WaitingForQuery
    }
    
    Ready --> Scaling : Add New Agent
    
    state "System Scaling" as Scaling {
        [*] --> CreateNewAgent
        CreateNewAgent --> RegisterNewAgent
        RegisterNewAgent --> UpdateRouter
        UpdateRouter --> [*]
    }
    
    Scaling --> Ready
    Ready --> Shutdown : Stop Signal
    
    state "System Shutdown" as Shutdown {
        [*] --> SignalReceived
        SignalReceived --> CleanupAgents
        CleanupAgents --> DeleteFromAzure
        DeleteFromAzure --> ClearRegistry
        ClearRegistry --> [*]
    }
    
    Shutdown --> [*]
    
    note right of Shutdown : Prevents cost accumulation\nAutomatic cleanup on exit
```

## 🎯 Key Functional Features

### **1. Intelligent Routing**
- **Intent Classification**: Automatically determines if query is about booking or general CBR information
- **Tool Selection**: Each agent uses appropriate tools based on query requirements
- **Fallback Handling**: Default routing ensures no query goes unanswered

### **2. Multi-Source Information**
- **Real-time Data**: Bing search for current CBR.nl information
- **Knowledge Base**: Vector store with comprehensive CBR procedures
- **Combined Responses**: Merges current and historical data for complete answers

### **3. Scalable Architecture**
- **Dynamic Agent Addition**: `add_agent()` function for runtime scaling
- **Independent Operation**: Agents operate without affecting others
- **Modular Design**: Easy to add new specializations

### **4. Cost Management**
- **Automatic Cleanup**: Signal handlers ensure agents are deleted on shutdown
- **Optimized Performance**: Caching and limits reduce Azure costs
- **Resource Monitoring**: Track agent usage and lifecycle

### **5. User Experience**
- **Fast Responses**: Optimized for 2-4 second response times
- **Tool Transparency**: Users see which tools provided information
- **Consistent Interface**: Unified chat experience regardless of agent used

This functional diagram shows exactly how your CBR multi-agent system processes requests, makes decisions, and delivers intelligent responses to users! 🚀