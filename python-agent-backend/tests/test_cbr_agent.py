"""
Test CBR Agent with Bing Search Tool
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from app.services.azure_agent_service import SimpleAzureAgentService
from app.models.chat import ChatMessage, MessageRole

async def test_cbr_agent():
    print("🚀 Testing CBR Agent with Bing Search Tool")
    print("=" * 50)
    
    service = SimpleAzureAgentService()
    
    # Test messages about CBR
    test_questions = [
        "What are the requirements for getting a Dutch driving license?",
        "How much does a theory exam cost at CBR?",
        "What should I know about the practical driving test?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Testing question: {question}")
        
        message = ChatMessage(role=MessageRole.USER, content=question)
        
        try:
            result = await service.generate_response([message])
            
            print(f"   Response: {result['content'][:200]}...")
            print(f"   Model: {result['model_used']}")
            print(f"   Time: {result['response_time']:.2f}s")
            print("   ✅ Test completed")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    # Cleanup
    try:
        await service.cleanup()
        print("\n✅ Cleanup completed")
    except:
        pass
    
    print("\n🎉 CBR Agent Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_cbr_agent())