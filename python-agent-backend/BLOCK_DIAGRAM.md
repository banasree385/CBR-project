# CBR Agent - Simple Block Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 USER                                        │
│                          (Web Browser / API Client)                        │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │ HTTP Requests
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            FASTAPI SERVER                                  │
│                               (Port 8000)                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │   Health    │ │    Chat     │ │   Agent     │ │   Static    │          │
│  │ Endpoint    │ │    API      │ │    API      │ │   Files     │          │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘          │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │ Python Calls
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AZURE AGENT SERVICE                                   │
│                       (Core Business Logic)                                │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐              │
│  │ Agent Manager   │ │ Thread Manager  │ │ Tool Detector   │              │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘              │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │ Azure SDK Calls
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AZURE AI FOUNDRY                                    │
│                          (Cloud Platform)                                  │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐              │
│  │   GPT-4o Model  │ │ Agent Runtime   │ │ Authentication  │              │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘              │
└────────────┬────────────────────────────────────┬───────────────────────────┘
             │                                    │
             ▼                                    ▼
┌─────────────────────────────┐         ┌─────────────────────────────┐
│      FILE SEARCH TOOL       │         │    BING GROUNDING TOOL      │
│                             │         │                             │
│ ┌─────────────────────────┐ │         │ ┌─────────────────────────┐ │
│ │     VECTOR STORE        │ │         │ │      WEB SEARCH         │ │
│ │                         │ │         │ │                         │ │
│ │ ┌─────────────────────┐ │ │         │ │ ┌─────────────────────┐ │ │
│ │ │  CBR Documents      │ │ │         │ │ │   Current Info      │ │ │
│ │ │                     │ │ │         │ │ │                     │ │ │
│ │ │ • Procedures        │ │ │         │ │ │ • News              │ │ │
│ │ │ • Requirements      │ │ │         │ │ │ • Prices            │ │ │
│ │ │ • Medical Info      │ │ │         │ │ │ • Weather           │ │ │
│ │ │ • Exam Details      │ │ │         │ │ │ • Wait Times        │ │ │
│ │ └─────────────────────┘ │ │         │ │ └─────────────────────┘ │ │
│ └─────────────────────────┘ │         │ └─────────────────────────┘ │
└─────────────────────────────┘         └─────────────────────────────┘
             ▲                                    ▲
             │                                    │
       ┌─────────────┐                     ┌─────────────┐
       │   LOCAL     │                     │     WEB     │
       │    DATA     │                     │  SOURCES    │
       │             │                     │             │
       │ JSON Files  │                     │ • CBR.nl    │
       │ (9 files)   │                     │ • News      │
       └─────────────┘                     │ • Weather   │
                                           └─────────────┘
```

## 📊 **Data Flow Legend:**

```
USER QUESTION
     ↓
┌──────────────────────────────────────────────────────┐
│ "What are CBR license requirements?"                 │ → File Search Tool
├──────────────────────────────────────────────────────┤
│ "What are current CBR test prices?"                  │ → Bing Search Tool  
├──────────────────────────────────────────────────────┤
│ "What's the weather today?"                          │ → Bing Search Tool
└──────────────────────────────────────────────────────┘
     ↓
TOOL RESPONSE WITH CITATIONS
     ↓
FORMATTED ANSWER TO USER
```

## 🔧 **Component Responsibilities:**

| Component | Purpose | Technology |
|-----------|---------|------------|
| **FastAPI Server** | HTTP API Gateway | Python FastAPI |
| **Azure Agent Service** | Business Logic & AI Integration | Python + Azure SDK |
| **Azure AI Foundry** | AI Agent Hosting & GPT-4o | Microsoft Azure |
| **File Search Tool** | Local Knowledge Search | Vector Store + Embeddings |
| **Bing Grounding** | Real-time Web Search | Bing Search API |

## 🚀 **Request Flow:**

1. **User** → Sends question via HTTP
2. **FastAPI** → Routes to chat endpoint  
3. **Agent Service** → Creates thread & message
4. **Azure AI** → Analyzes question & selects tool
5. **Tool** → Searches knowledge base or web
6. **Response** → Formatted answer with citations
7. **User** → Receives comprehensive answer

## 💾 **Data Sources:**

- **Local**: 9 CBR JSON files (procedures, requirements, medical info)
- **Web**: CBR.nl, news sites, weather services, current information

This block diagram shows the clean separation between presentation (FastAPI), logic (Agent Service), AI (Azure), and data (Tools), making the system modular and scalable.