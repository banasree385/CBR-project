#!/usr/bin/env python3
"""
Direct test of Azure Agent Service without FastAPI
Tests the core functionality of the Azure AI agent
"""

import asyncio
import sys
import os

# Add the app directory to Python path
# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.azure_agent_service import SimpleAzureAgentService
from models.chat import ChatMessage, MessageRole


async def test_azure_agent():
    """Test the Azure agent service directly."""
    print("🚀 Starting Azure Agent Service Test")
    print("=" * 50)
    
    # Initialize the service
    print("1. Initializing Azure Agent Service...")
    service = SimpleAzureAgentService()
    
    # Verify connection
    print("2. Verifying connection...")
    connection_ok = await service.verify_connection()
    print(f"   Connection status: {'✅ OK' if connection_ok else '❌ Failed'}")
    
    # Initialize agent
    print("3. Initializing agent and thread...")
    agent_ok = await service.initialize_agent()
    print(f"   Agent initialization: {'✅ OK' if agent_ok else '❌ Failed'}")
    
    if not agent_ok:
        print("❌ Agent initialization failed. Check your Azure configuration.")
        return
    
    # Test message
    print("4. Testing message generation...")
    test_messages = [
        ChatMessage(role=MessageRole.USER, content="Hello! Can you help me?")
    ]
    
    try:
        response = await service.generate_response(test_messages)
        print("   Response received:")
        print(f"   Content: {response.get('content', 'No content')}")
        print(f"   Model: {response.get('model_used', 'Unknown')}")
        print(f"   Tokens: {response.get('tokens_used', 0)}")
        print(f"   Time: {response.get('response_time', 0):.2f}s")
        print("   ✅ Message test completed")
        
    except Exception as e:
        print(f"   ❌ Message test failed: {e}")
    
    # Test another message
    print("5. Testing another message...")
    test_messages2 = [
        ChatMessage(role=MessageRole.USER, content="What is 2 + 2?")
    ]
    
    try:
        response2 = await service.generate_response(test_messages2)
        print("   Response received:")
        print(f"   Content: {response2.get('content', 'No content')}")
        print(f"   Model: {response2.get('model_used', 'Unknown')}")
        print(f"   Tokens: {response2.get('tokens_used', 0)}")
        print(f"   Time: {response2.get('response_time', 0):.2f}s")
        print("   ✅ Second message test completed")
        
    except Exception as e:
        print(f"   ❌ Second message test failed: {e}")
    
    # Cleanup
    print("6. Cleaning up...")
    try:
        await service.cleanup()
        print("   ✅ Cleanup completed")
    except Exception as e:
        print(f"   ⚠️ Cleanup warning: {e}")
    
    print("=" * 50)
    print("🎉 Azure Agent Service Test Complete!")


def main():
    """Main function to run the test."""
    try:
        # Run the async test
        asyncio.run(test_azure_agent())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()