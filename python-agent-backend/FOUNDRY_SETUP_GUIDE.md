# Azure AI Foundry Integration - Step-by-Step Setup Guide

## 🎯 **Architecture Overview**

Your new setup will have:
- **2 Specialist Agents** in Azure AI Foundry
- **1 Orchestrator Agent** in Azure AI Foundry  
- **Python Backend** that connects to these agents
- **Existing Chatbot Frontend** (no changes needed)

---

## 📋 **Prerequisites**

✅ **You already have:**
- Azure AI Foundry project set up
- Python backend with chat endpoints

✅ **You need to configure:**
- 3 agents in Azure AI Foundry
- Environment variables
- Agent IDs

---

## 🚀 **Step 1: Create Agents in Azure AI Foundry**

### **1.1 Access Azure AI Foundry**
1. Go to [Azure AI Foundry](https://ai.azure.com)
2. Navigate to your project
3. Go to **"Build"** → **"Agents"**

### **1.2 Create Orchestrator Agent**
```yaml
Name: CBR-Orchestrator
Description: Main coordinator that routes queries to specialist agents
Instructions: |
  You are the CBR Orchestrator Agent. Your role is to:
  1. Analyze incoming user queries about CBR (Dutch driving license authority)
  2. Determine which specialist agent should handle the query
  3. Route queries to the appropriate specialist
  4. Coordinate responses from multiple agents when needed
  
  Available specialists:
  - Agent 1: Theory exams, traffic rules, exam preparation
  - Agent 2: Practical exams, booking, costs, documents
  
  Always provide helpful, accurate information about CBR services.

Model: gpt-4o (or your preferred model)
Tools: Enable Function Calling, Bing Search (optional)
```

### **1.3 Create Agent 1 (Theory Specialist)**
```yaml
Name: CBR-Theory-Agent
Description: Specialist for theory exams and traffic rules
Instructions: |
  You are a CBR Theory Exam Specialist. You excel at:
  
  - Theory exam questions and preparation
  - Traffic rules and regulations (Dutch)
  - Road signs and their meanings
  - Study materials and learning strategies
  - Exam booking for theory tests
  - Practice questions and mock exams
  
  Provide detailed, educational responses about CBR theory content.
  Always be encouraging and helpful for exam preparation.

Model: gpt-4o
Tools: Enable Function Calling, Bing Search for current info
```

### **1.4 Create Agent 2 (Practical Specialist)**
```yaml
Name: CBR-Practical-Agent  
Description: Specialist for practical exams, costs, and booking
Instructions: |
  You are a CBR Practical Exam Specialist. You excel at:
  
  - Practical driving test procedures
  - Driving skills and techniques
  - Exam booking and scheduling
  - CBR costs and pricing (2025)
  - Required documents and forms
  - Test locations and availability
  - Cancellation and rescheduling policies
  
  Provide practical, actionable advice for driving tests and CBR procedures.
  Always include current pricing and booking information when relevant.

Model: gpt-4o
Tools: Enable Function Calling, Bing Search, File Search (for CBR data)
```

---

## 🔧 **Step 2: Get Agent IDs**

### **2.1 Copy Agent IDs**
After creating each agent:
1. Click on the agent name
2. Copy the **Agent ID** (long string starting with `asst_`)
3. Save these IDs:

```
Orchestrator Agent ID: asst_xxxxxxxxxxxxxxxxxx
Agent 1 ID: asst_yyyyyyyyyyyyyyyyyy  
Agent 2 ID: asst_zzzzzzzzzzzzzzzzzz
```

---

## ⚙️ **Step 3: Configure Environment Variables**

### **3.1 Update Your .env File**
Add these new environment variables to your `.env` file:

```bash
# Azure AI Foundry Agents
ORCHESTRATOR_AGENT_ID=asst_xxxxxxxxxxxxxxxxxx
AGENT1_ID=asst_yyyyyyyyyyyyyyyyyy
AGENT2_ID=asst_zzzzzzzzzzzzzzzzzz

# Your existing Azure settings (keep these)
AZURE_AI_FOUNDRY_ENDPOINT=https://your-project.cognitiveservices.azure.com/
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group
AZURE_PROJECT_NAME=your-project-name
```

### **3.2 Alternative: Set in Container/System**
If using dev container or system environment:

```bash
export ORCHESTRATOR_AGENT_ID="asst_xxxxxxxxxxxxxxxxxx"
export AGENT1_ID="asst_yyyyyyyyyyyyyyyyyy" 
export AGENT2_ID="asst_zzzzzzzzzzzzzzzzzz"
```

---

## 🔄 **Step 4: Test the Integration**

### **4.1 Start Your Backend**
```bash
cd /workspaces/CBR-project/python-agent-backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **4.2 Check Agent Status**
```bash
curl http://localhost:8000/api/v1/foundry/status
```

Expected response:
```json
{
  "status": "online",
  "agents": {
    "orchestrator": {
      "status": "online", 
      "name": "CBR-Orchestrator",
      "model": "gpt-4o",
      "id": "asst_xxxxxxxxxxxxxxxxxx"
    },
    "agent1": {
      "status": "online",
      "name": "CBR-Theory-Agent", 
      "model": "gpt-4o",
      "id": "asst_yyyyyyyyyyyyyyyyyy"
    },
    "agent2": {
      "status": "online",
      "name": "CBR-Practical-Agent",
      "model": "gpt-4o", 
      "id": "asst_zzzzzzzzzzzzzzzzzz"
    }
  },
  "thread_id": "thread_xxxxxxxxx"
}
```

### **4.3 Test Chat with Orchestrator**
```bash
curl -X POST http://localhost:8000/api/v1/foundry/orchestrator \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Ik wil informatie over het theorie-examen",
    "session_id": "test-session"
  }'
```

### **4.4 Test Specific Agents**
```bash
# Test Agent 1 (Theory)
curl -X POST http://localhost:8000/api/v1/foundry/agent1 \
  -H "Content-Type: application/json" \
  -d '{"message": "Wat zijn de belangrijkste verkeersregels?"}'

# Test Agent 2 (Practical)  
curl -X POST http://localhost:8000/api/v1/foundry/agent2 \
  -H "Content-Type: application/json" \
  -d '{"message": "Hoeveel kost een praktijkexamen?"}'
```

---

## 🌐 **Step 5: Update Frontend (Optional)**

### **5.1 Your Existing Frontend**
Your current chatbot will work without changes! It uses:
- `/api/v1/chat/message` (your existing endpoint)

### **5.2 Add Foundry Agent Options (Optional)**
If you want to add agent selection to your frontend, update your HTML:

```html
<!-- Add to your chatbot HTML -->
<select id="agentSelector">
  <option value="default">Standard Chat</option>
  <option value="orchestrator">Orchestrator Agent</option>
  <option value="agent1">Theory Specialist</option>
  <option value="agent2">Practical Specialist</option>
</select>
```

Update JavaScript to use different endpoints:
```javascript
function sendMessage() {
  const agentType = document.getElementById('agentSelector').value;
  
  let endpoint;
  if (agentType === 'default') {
    endpoint = '/api/v1/chat/message';
  } else {
    endpoint = `/api/v1/foundry/${agentType}`;
  }
  
  // Your existing fetch logic with new endpoint
}
```

---

## 📊 **Step 6: Available API Endpoints**

### **6.1 New Foundry Endpoints**
```
POST /api/v1/foundry/chat          # Route to any agent
POST /api/v1/foundry/orchestrator  # Talk to orchestrator
POST /api/v1/foundry/agent1        # Talk to theory specialist
POST /api/v1/foundry/agent2        # Talk to practical specialist
GET  /api/v1/foundry/status        # Check agent status
GET  /api/v1/foundry/history/{id}  # Get conversation history
POST /api/v1/foundry/new-session   # Create new session
GET  /api/v1/foundry/health        # Health check
```

### **6.2 Your Existing Endpoints (Still Work)**
```
POST /api/v1/chat/message          # Your original chat
GET  /api/v1/chat/history/{id}     # Your original history
GET  /api/v1/chat/sessions         # Your original sessions
```

---

## 🎯 **Step 7: How It Works**

### **7.1 Message Flow**
```
User Message 
    ↓
Python Backend
    ↓
Azure AI Foundry API
    ↓
Your Agents (Orchestrator/Agent1/Agent2)
    ↓
Response Back to User
```

### **7.2 Agent Routing**
- **Orchestrator**: Analyzes and routes queries
- **Agent 1**: Handles theory exam questions
- **Agent 2**: Handles practical exams, costs, booking

### **7.3 Session Management**
- Each conversation creates a "thread" in Azure AI Foundry
- Threads maintain conversation context
- Multiple users can have separate threads

---

## 🔍 **Step 8: Troubleshooting**

### **8.1 Agent IDs Not Working**
```bash
# Check environment variables are set
echo $ORCHESTRATOR_AGENT_ID
echo $AGENT1_ID  
echo $AGENT2_ID

# Verify in Azure AI Foundry
# Go to Agents → Click agent → Copy ID
```

### **8.2 Authentication Issues**
```bash
# Check Azure credentials
az login
az account show

# Verify your Azure AI Foundry endpoint
curl https://your-project.cognitiveservices.azure.com/
```

### **8.3 Mock Mode**
If agents aren't configured, the system automatically falls back to mock responses for testing.

---

## 🚀 **Step 9: Next Steps**

### **9.1 Enhance Agents**
- Add more specific instructions
- Upload CBR knowledge files to agents
- Configure function calling for specific actions

### **9.2 Add Monitoring**
- Track which agents are used most
- Monitor response times
- Log conversation patterns

### **9.3 Scale Up**
- Add more specialist agents
- Implement agent collaboration
- Add user preference learning

---

## 📞 **Need Help?**

### **Quick Test Commands**
```bash
# Check if everything is working
curl http://localhost:8000/api/v1/foundry/health

# Test orchestrator
curl -X POST http://localhost:8000/api/v1/foundry/orchestrator \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I need help with CBR"}'
```

### **Logs to Check**
- Backend logs: Shows agent connections and API calls
- Azure AI Foundry: Shows agent usage and responses
- Browser console: Shows frontend API calls

---

**🎉 You're all set! Your chatbot now has 3 intelligent agents working together in Azure AI Foundry!**