"""
Verify Bing Grounding vs Base Model Knowledge
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from app.services.azure_agent_service import SimpleAzureAgentService
from app.models.chat import ChatMessage, MessageRole

async def test_grounding_vs_base():
    print("🔍 Testing: Bing Grounding vs Base Model Knowledge")
    print("=" * 60)
    
    service = SimpleAzureAgentService()
    
    # Test 1: Ask for very specific, current CBR info that base model unlikely to know
    test_cases = [
        {
            "question": "What is the exact current price of CBR theory exam in 2025?",
            "expectation": "Should use tool to get current price (€41 from our fallback data)"
        },
        {
            "question": "What are CBR practical exam booking procedures in Dutch?", 
            "expectation": "Should search CBR.nl for specific procedures"
        },
        {
            "question": "What is artificial intelligence?",
            "expectation": "General question - might not use tool"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Test Case: {test['question']}")
        print(f"   Expected: {test['expectation']}")
        
        message = ChatMessage(role=MessageRole.USER, content=test['question'])
        
        try:
            result = await service.generate_response([message])
            
            print(f"   Response: {result['content'][:150]}...")
            print(f"   Time: {result['response_time']:.1f}s")
            
            # Analyze response for grounding indicators
            response_text = result['content'].lower()
            grounding_indicators = [
                'according to cbr',
                'cbr website',
                'cbr.nl', 
                '€41',  # Our fallback data
                'visit the cbr',
                'found on cbr'
            ]
            
            found_indicators = [ind for ind in grounding_indicators if ind in response_text]
            
            if found_indicators:
                print(f"   ✅ GROUNDING DETECTED: {found_indicators}")
            else:
                print(f"   ❓ LIKELY BASE MODEL: No grounding indicators found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    await service.cleanup()
    print("\n🎯 Analysis Complete!")

if __name__ == "__main__":
    asyncio.run(test_grounding_vs_base())