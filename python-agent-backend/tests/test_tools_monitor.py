"""
Monitor Tool Usage in Real-Time
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time
from app.services.azure_agent_service import SimpleAzureAgentService
from app.models.chat import ChatMessage, MessageRole

class ToolMonitor:
    def __init__(self):
        self.tool_calls = []
        self.original_execute = None
    
    def start_monitoring(self):
        # Monkey patch the tool execution to log calls
        from app.tools.bing_search import execute_bing_search_tool
        self.original_execute = execute_bing_search_tool
        
        def monitored_execute(arguments):
            call_info = {
                "timestamp": time.time(),
                "tool": "search_cbr_website", 
                "arguments": arguments,
                "query": arguments.get("query", "")
            }
            self.tool_calls.append(call_info)
            print(f"🔧 TOOL CALLED: {call_info['tool']} with query: '{call_info['query']}'")
            
            result = self.original_execute(arguments)
            print(f"🔧 TOOL RESULT: {len(result)} characters returned")
            return result
        
        # Replace with monitored version
        import app.tools.bing_search
        app.tools.bing_search.execute_bing_search_tool = monitored_execute
    
    def get_tool_usage(self):
        return self.tool_calls

async def test_with_monitoring():
    print("🎯 CBR Agent with Tool Monitoring")
    print("=" * 40)
    
    monitor = ToolMonitor()
    monitor.start_monitoring()
    
    service = SimpleAzureAgentService()
    
    questions = [
        "What does CBR theory exam cost?",  # Should trigger tool
        "What is the weather today?"        # Should NOT trigger tool
    ]
    
    for question in questions:
        print(f"\n📝 Question: {question}")
        
        message = ChatMessage(role=MessageRole.USER, content=question)
        result = await service.generate_response([message])
        
        print(f"💬 Response: {result['content'][:100]}...")
        
        # Check if tools were called
        recent_calls = [call for call in monitor.get_tool_usage() 
                       if time.time() - call['timestamp'] < 30]
        
        if recent_calls:
            print(f"✅ TOOL USAGE CONFIRMED: {len(recent_calls)} tools called")
        else:
            print(f"❌ NO TOOLS USED: Base model response")
    
    await service.cleanup()
    
    print(f"\n📊 Total tool calls: {len(monitor.get_tool_usage())}")

if __name__ == "__main__":
    asyncio.run(test_with_monitoring())