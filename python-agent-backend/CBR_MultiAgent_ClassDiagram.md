# CBR Multi-Agent System - Class Diagram

## 🎯 System Architecture Overview

```mermaid
classDiagram
    %% Main Orchestrator Class
    class CBRMultiAgentOrchestrator {
        -project_client: AIProjectClient
        -search_agent: Agent
        -booking_agent: Agent
        -tool_resources: ToolResources
        -agent_registry: Dict~str, Agent~
        -config: Dict~str, str~
        
        +__init__()
        +initialize_system() : bool
        +orchestrate(user_query: str, session_id: str) : Dict
        +add_agent(agent_config: Dict) : bool
        +get_system_status() : Dict
        +cleanup_agents() : void
        
        -_setup_configuration() : void
        -_initialize_client() : bool
        -_setup_vector_store() : bool
        -_create_agents() : bool
        -_is_booking_query(query: str) : bool
        -_execute_search_agent(query: str, session_id: str) : Dict
        -_execute_booking_agent(query: str, session_id: str) : Dict
        -_extract_last_agent_message(messages) : str
        -_signal_handler(signum, frame) : void
        -_cleanup_on_exit() : void
    }
    
    %% Enhanced Booking Agent
    class CBRBookingAgentEnhanced {
        -project_client: AIProjectClient
        -agent: Agent
        -booking_knowledge: Dict~str, Any~
        -booking_config: Dict~str, Any~
        
        +__init__(project_client: AIProjectClient)
        +create_enhanced_agent(deployment_name: str) : Agent
        +handle_booking_query(query: str, session_id: str) : Dict
        +get_booking_statistics() : Dict
        +cleanup() : void
        
        -_load_booking_knowledge() : Dict
        -_format_steps(steps: List~str~) : str
        -_classify_booking_intent(query: str) : str
        -_enhance_query_with_context(query: str, intent: str) : str
        -_get_booking_context(intent: str) : Dict
        -_extract_last_message(messages) : str
    }
    
    %% Azure AI Project Components
    class AIProjectClient {
        <<Azure SDK>>
        +agents: AgentsOperations
        +vector_stores: VectorStoresOperations
        +files: FilesOperations
        +messages: MessagesOperations
    }
    
    class Agent {
        <<Azure Model>>
        +id: str
        +name: str
        +description: str
        +instructions: str
        +tools: List~Tool~
        +model: str
        +temperature: float
    }
    
    class ToolResources {
        <<Azure Model>>
        +file_search: FileSearchToolResource
        +vector_store_ids: List~str~
    }
    
    class AgentThreadCreationOptions {
        <<Azure Model>>
        +messages: List~Message~
        +tool_resources: ToolResources
    }
    
    %% Tool Types
    class BingGroundingTool {
        <<Tool>>
        +type: "bing_grounding"
        +description: "Search Bing for current CBR.nl information"
    }
    
    class FileSearchTool {
        <<Tool>>
        +type: "file_search"
        +description: "Search vector store for CBR documentation"
    }
    
    class FunctionCallingTool {
        <<Tool>>
        +type: "function_calling"
        +description: "Execute custom booking functions"
    }
    
    %% Configuration Classes
    class BookingConfig {
        +theory_exam: Dict
        +practical_exam: Dict
        +cbr_locations: List~str~
        +cost: float
        +duration_minutes: int
        +advance_booking_days: int
        +cancellation_deadline_hours: int
        +reschedule_limit: int
        +required_documents: List~str~
    }
    
    class BookingKnowledge {
        +booking_steps: Dict
        +common_issues: Dict
        +special_circumstances: Dict
        +theory_exam: List~str~
        +practical_exam: List~str~
    }
    
    %% Response Models
    class OrchestrationResponse {
        +success: bool
        +response: str
        +agent_used: str
        +agent_id: str
        +capabilities: List~str~
        +session_id: str
        +thread_id: str
        +error?: str
    }
    
    class BookingResponse {
        +success: bool
        +response: str
        +booking_intent: str
        +agent_used: str
        +session_id: str
        +thread_id: str
        +booking_context: Dict
        +error?: str
    }
    
    %% Relationships
    CBRMultiAgentOrchestrator --> AIProjectClient : uses
    CBRMultiAgentOrchestrator --> Agent : manages multiple
    CBRMultiAgentOrchestrator --> ToolResources : configures
    CBRMultiAgentOrchestrator --> OrchestrationResponse : returns
    CBRMultiAgentOrchestrator --> CBRBookingAgentEnhanced : can integrate
    
    CBRBookingAgentEnhanced --> AIProjectClient : uses
    CBRBookingAgentEnhanced --> Agent : creates & manages
    CBRBookingAgentEnhanced --> BookingConfig : contains
    CBRBookingAgentEnhanced --> BookingKnowledge : contains
    CBRBookingAgentEnhanced --> BookingResponse : returns
    
    Agent --> BingGroundingTool : uses
    Agent --> FileSearchTool : uses
    Agent --> FunctionCallingTool : uses
    
    AIProjectClient --> Agent : creates
    AIProjectClient --> ToolResources : manages
    AIProjectClient --> AgentThreadCreationOptions : processes
    
    ToolResources --> FileSearchTool : configures
    AgentThreadCreationOptions --> ToolResources : includes
```

## 🔗 Component Relationships

### **1. Main Orchestrator (`CBRMultiAgentOrchestrator`)**
- **Purpose**: Central hub that manages all agents and routes queries
- **Responsibilities**:
  - Initialize Azure AI client and vector stores
  - Create and manage specialized agents (Search & Booking)
  - Route user queries to appropriate agents based on intent
  - Handle agent lifecycle and cleanup
  - Provide system scaling capabilities

### **2. Enhanced Booking Agent (`CBRBookingAgentEnhanced`)**
- **Purpose**: Specialized agent for handling booking and scheduling queries
- **Key Features**:
  - Intent classification (10+ booking scenarios)
  - Real-world booking procedures and costs
  - Comprehensive CBR location and requirement data
  - Advanced query processing with context enhancement

### **3. Azure AI Integration Layer**
- **Components**: `AIProjectClient`, `Agent`, `ToolResources`
- **Purpose**: Interface with Azure AI Foundry for agent management
- **Capabilities**: Agent creation, thread management, tool integration

## 🎯 Data Flow Architecture

```mermaid
flowchart TD
    A[User Query] --> B[CBRMultiAgentOrchestrator]
    B --> C{Query Classification}
    C -->|Booking Intent| D[CBR Booking Agent]
    C -->|Search Intent| E[CBR Search Agent]
    
    D --> F[Booking Tools]
    F --> G[Function Calling]
    F --> H[Bing Grounding]
    
    E --> I[Search Tools]
    I --> J[Vector Store Search]
    I --> K[Bing Grounding]
    
    J --> L[CBR Knowledge Base]
    L --> M[3 JSON Files]
    M --> N[Procedures, Medical, Safety]
    
    G --> O[Booking Response]
    H --> O
    K --> P[Search Response]
    J --> P
    
    O --> Q[Orchestration Response]
    P --> Q
    Q --> R[User]
    
    style B fill:#e1f5fe
    style D fill:#f3e5f5
    style E fill:#e8f5e8
    style L fill:#fff3e0
```

## 🛠️ Tool Architecture

```mermaid
classDiagram
    class ToolEcosystem {
        <<interface>>
    }
    
    class BingGroundingTool {
        +search_domain: "cbr.nl"
        +real_time_info: true
        +current_updates: true
    }
    
    class FileSearchTool {
        +vector_store_access: true
        +knowledge_base: "CBR Documentation"
        +semantic_search: true
    }
    
    class FunctionCallingTool {
        +custom_functions: true
        +booking_procedures: true
        +appointment_management: true
    }
    
    ToolEcosystem <|-- BingGroundingTool
    ToolEcosystem <|-- FileSearchTool
    ToolEcosystem <|-- FunctionCallingTool
    
    BingGroundingTool : +search_cbr_website()
    BingGroundingTool : +get_current_info()
    
    FileSearchTool : +search_knowledge_base()
    FileSearchTool : +semantic_query()
    
    FunctionCallingTool : +process_booking_request()
    FunctionCallingTool : +manage_appointments()
```

## 📊 Configuration & Knowledge Models

```mermaid
classDiagram
    class SystemConfiguration {
        +azure_endpoint: str
        +subscription_id: str
        +resource_group: str
        +project_name: str
        +deployment_name: str
    }
    
    class BookingConfiguration {
        +theory_exam_cost: 38.35€
        +practical_exam_cost: 91.65€
        +15_cbr_locations: List
        +booking_deadlines: Dict
        +required_documents: Dict
    }
    
    class KnowledgeBase {
        +procedures_2025: JSON
        +medical_assessment: JSON
        +unsafe_driving: JSON
        +booking_steps: Dict
        +common_issues: Dict
    }
    
    SystemConfiguration --> CBRMultiAgentOrchestrator
    BookingConfiguration --> CBRBookingAgentEnhanced
    KnowledgeBase --> CBRMultiAgentOrchestrator
```

## 🔄 Lifecycle Management

```mermaid
stateDiagram-v2
    [*] --> Initialization
    Initialization --> ClientSetup : Setup Azure Client
    ClientSetup --> VectorStoreSetup : Create Knowledge Base
    VectorStoreSetup --> AgentCreation : Create Specialized Agents
    AgentCreation --> SystemReady : Registration Complete
    
    SystemReady --> QueryProcessing : User Request
    QueryProcessing --> IntentClassification : Analyze Query
    IntentClassification --> BookingAgent : Booking Intent
    IntentClassification --> SearchAgent : Search Intent
    
    BookingAgent --> ResponseGeneration : Process Booking
    SearchAgent --> ResponseGeneration : Process Search
    ResponseGeneration --> SystemReady : Return Response
    
    SystemReady --> Cleanup : Shutdown Signal
    Cleanup --> AgentDeletion : Delete All Agents
    AgentDeletion --> [*] : System Terminated
    
    note right of Cleanup : Prevents cost accumulation
    note right of AgentDeletion : Signal handlers ensure cleanup
```

## 🎯 Key Design Patterns

### **1. Orchestrator Pattern**
- Central coordinator manages multiple specialized agents
- Query routing based on intent classification
- Unified response interface

### **2. Factory Pattern**
- Dynamic agent creation with configuration
- Standardized agent initialization
- Scalable agent addition via `add_agent()`

### **3. Strategy Pattern**
- Different processing strategies for booking vs search queries
- Tool selection based on agent type
- Context-aware response generation

### **4. Observer Pattern**
- Signal handlers for graceful shutdown
- Automatic cleanup on system exit
- Lifecycle event management

## 🔧 Integration Points

1. **Azure AI Foundry**: Primary AI platform integration
2. **Vector Store**: CBR knowledge base with 3 JSON files
3. **Bing Search**: Real-time CBR.nl information
4. **DigiD Integration**: Authentication for booking procedures
5. **CBR.nl API**: (Future) Direct booking system integration

## 📈 Scalability Features

- **Agent Registry**: Dynamic agent management
- **Add Agent Function**: Runtime agent addition
- **Modular Tool System**: Plug-and-play tool architecture
- **Configuration-Driven**: Easy deployment across environments
- **Resource Management**: Automatic cleanup prevents cost accumulation

This architecture provides a robust, scalable foundation for your CBR multi-agent system with clear separation of concerns and comprehensive booking capabilities! 🚀