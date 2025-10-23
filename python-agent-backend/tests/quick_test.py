"""
Quick CBR Agent Test with Real Bing API
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from app.services.azure_agent_service import SimpleAzureAgentService
from app.models.chat import ChatMessage, MessageRole

async def quick_test():
    print("🔍 Quick CBR Agent Test")
    
    service = SimpleAzureAgentService()
    
    question = "What does CBR theory exam cost?"
    print(f"Question: {question}")
    
    message = ChatMessage(role=MessageRole.USER, content=question)
    
    try:
        result = await service.generate_response([message])
        print(f"\n✅ Response received:")
        print(f"Content: {result['content']}")
        print(f"Time: {result['response_time']:.1f}s")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    await service.cleanup()

if __name__ == "__main__":
    asyncio.run(quick_test())