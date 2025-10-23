# CBR AI Assistant Tests# Tests for CBR Agent



This directory contains the test suite for the CBR AI Assistant.This folder contains all test files for the CBR agent project.



## Test File## Test Files:

- `test_azure_agent.py` - Basic Azure agent functionality

**`test_cbr_assistant.py`** - Comprehensive test suite with essential scenarios:- `test_cbr_agent.py` - CBR-specific agent testing

- `test_grounding_detection.py` - Verify grounding vs base model

### Test Scenarios- `test_bing_direct.py` - Direct Bing API testing

- `test_tools_monitor.py` - Monitor tool usage

1. **Basic Agent Functionality**- `quick_test.py` - Fast single test

   - Verifies agent responds to basic questions

   - Confirms GPT model is working correctly## Run Tests:

   - Tests response quality and format```bash

cd tests

2. **CBR-Specific Questions with Bing Grounding**python test_azure_agent.py

   - Tests CBR-related questions (e.g., "Wat kosten de CBR examens in 2025?")python test_cbr_agent.py

   - Verifies Bing grounding tool is invoked```
   - Checks for CBR-specific content and source citations
   - Confirms current/live data is returned

3. **Session Persistence**
   - Tests multiple messages in same session
   - Verifies context maintenance

## Running Tests

### Using pytest:
```bash
cd /workspaces/CBR-project/python-agent-backend
python -m pytest tests/test_cbr_assistant.py -v
```

### Direct execution:
```bash
cd /workspaces/CBR-project/python-agent-backend
python tests/test_cbr_assistant.py
```

### Prerequisites

- Azure AI Foundry credentials configured
- CBR agent service running
- Internet connection for Bing grounding

## Expected Results

✅ **All tests pass**: CBR AI Assistant is working correctly  
✅ **Basic functionality**: Agent responds to general questions  
✅ **Bing grounding**: CBR questions trigger live data retrieval  
✅ **Session management**: Context maintained across messages