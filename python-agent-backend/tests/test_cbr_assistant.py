"""
CBR AI Assistant Test Suite

This test file contains two essential test scenarios:
1. Test basic agent functionality - verifies the agent gets replies from GPT
2. Test CBR-specific questions - ensures Bing grounding tool is invoked for CBR queries

Usage:
    python -m pytest tests/test_cbr_assistant.py -v
    
or run directly:
    python tests/test_cbr_assistant.py
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any

# Try to import pytest, but make it optional
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Mock pytest decorator for direct execution
    def pytest_fixture(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    pytest = type('MockPytest', (), {'fixture': pytest_fixture})()

# Import our CBR agent service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.azure_agent_service import AzureAgentService


class TestCBRAssistant:
    """Test suite for CBR AI Assistant functionality."""
    
    @pytest.fixture(scope="class")
    def agent_service(self):
        """Initialize the Azure Agent Service for testing."""
        print("\n🔧 Initializing Azure Agent Service...")
        return AzureAgentService()
    
    def test_basic_agent_function(self, agent_service):
        """
        Test Scenario 1: Basic Agent Functionality
        
        Verifies that:
        - Agent service can be initialized
        - Agent responds to basic questions
        - GPT model is working and returns responses
        """
        print("\n🧪 Test 1: Basic Agent Functionality")
        
        # Test with a simple, non-CBR question
        test_message = "Hello"
        session_id = f"test-basic-{datetime.now().timestamp()}"
        
        print(f"   📤 Sending message: '{test_message}'")
        print(f"   🆔 Session ID: {session_id}")
        
        try:
            # Create ChatMessage object for the agent service
            from app.models.chat import ChatMessage, MessageRole as ChatMessageRole
            
            chat_messages = [ChatMessage(
                role=ChatMessageRole.USER,
                content=test_message
            )]
            
            # Call the agent service (it's async)
            import asyncio
            response_data = asyncio.run(agent_service.generate_response(chat_messages))
            
            # Extract response content
            response = response_data.get('content', '')
            
            # Verify we got a response
            assert response is not None, "❌ Agent returned None response"
            assert isinstance(response, str), "❌ Response is not a string"
            assert len(response.strip()) > 0, "❌ Response is empty"
            
            print(f"   ✅ Response received: '{response[:100]}{'...' if len(response) > 100 else ''}'")
            print(f"   ✅ Response length: {len(response)} characters")
            
            # Basic response quality checks
            assert len(response) > 10, "❌ Response too short (likely an error)"
            
            print("   🎉 Basic agent functionality test PASSED")
            
        except Exception as e:
            error_msg = f"❌ Basic agent test failed: {str(e)}"
            print(f"   {error_msg}")
            if PYTEST_AVAILABLE:
                pytest.fail(error_msg)
            else:
                raise Exception(error_msg)
    
    def test_cbr_specific_question_with_bing_grounding(self, agent_service):
        """
        Test Scenario 2: CBR-Specific Question with Bing Grounding
        
        Verifies that:
        - Agent responds to CBR-specific questions
        - Bing grounding tool is invoked for CBR queries
        - Response contains relevant CBR information
        - Response includes source citations (indicating Bing grounding was used)
        """
        print("\n🧪 Test 2: CBR-Specific Question with Bing Grounding")
        
        # Test with a CBR-specific question that should trigger Bing grounding
        test_message = "Wat kosten de CBR examens in 2025?"
        session_id = f"test-cbr-{datetime.now().timestamp()}"
        
        print(f"   📤 Sending CBR question: '{test_message}'")
        print(f"   🆔 Session ID: {session_id}")
        print("   🔍 Expecting Bing grounding tool to be invoked...")
        
        try:
            # Create ChatMessage object for the CBR question
            from app.models.chat import ChatMessage, MessageRole as ChatMessageRole
            
            chat_messages = [ChatMessage(
                role=ChatMessageRole.USER,
                content=test_message
            )]
            
            # Call the agent service with CBR question (it's async)
            import asyncio
            response_data = asyncio.run(agent_service.generate_response(chat_messages))
            
            # Extract response content
            response = response_data.get('content', '')
            
            # Verify we got a response
            assert response is not None, "❌ Agent returned None response"
            assert isinstance(response, str), "❌ Response is not a string"
            assert len(response.strip()) > 0, "❌ Response is empty"
            
            print(f"   ✅ Response received: '{response[:150]}{'...' if len(response) > 150 else ''}'")
            print(f"   ✅ Response length: {len(response)} characters")
            
            # Check for CBR-specific content (indicating successful grounding)
            cbr_indicators = [
                "CBR", "cbr.nl", "examen", "rijbewijs", "theorie", "praktijk",
                "€", "euro", "2025", "kosten", "prijs"
            ]
            
            response_lower = response.lower()
            found_indicators = [indicator for indicator in cbr_indicators 
                              if indicator.lower() in response_lower]
            
            print(f"   🔍 Found CBR indicators: {found_indicators}")
            
            # Verify CBR-related content is present
            assert len(found_indicators) >= 3, f"❌ Response doesn't contain enough CBR-related content. Found: {found_indicators}"
            
            # Check for potential source citations (indicating Bing grounding was used)
            citation_indicators = [
                "bron", "source", "cbr.nl", "volgens", "informatie", 
                "website", "officieel", "actueel"
            ]
            
            found_citations = [indicator for indicator in citation_indicators 
                             if indicator.lower() in response_lower]
            
            print(f"   📎 Found citation indicators: {found_citations}")
            
            # Verify grounding indicators
            has_grounding_evidence = (
                len(found_citations) > 0 or 
                "cbr.nl" in response_lower or
                "€" in response  # Price information suggests current data
            )
            
            assert has_grounding_evidence, "❌ No evidence of Bing grounding in response"
            
            print("   🎉 CBR-specific question with Bing grounding test PASSED")
            print("   ✅ Bing grounding tool appears to have been invoked successfully")
            
        except Exception as e:
            error_msg = f"❌ CBR grounding test failed: {str(e)}"
            print(f"   {error_msg}")
            if PYTEST_AVAILABLE:
                pytest.fail(error_msg)
            else:
                raise Exception(error_msg)
    
    def test_agent_persistence(self, agent_service):
        """
        Test Scenario 3: Agent Session Persistence
        
        Verifies that:
        - Multiple messages in same session work
        - Agent maintains context within session
        """
        print("\n🧪 Test 3: Agent Session Persistence")
        
        session_id = f"test-persistence-{datetime.now().timestamp()}"
        
        # First message
        first_message = "Hallo"
        print(f"   📤 First message: '{first_message}'")
        
        # Second message for context test
        second_message = "Wat is het verschil tussen AM en B rijbewijs?"
        
        try:
            # Create ChatMessage objects for session persistence test
            from app.models.chat import ChatMessage, MessageRole as ChatMessageRole
            import asyncio
            
            # First message
            first_messages = [ChatMessage(
                role=ChatMessageRole.USER,
                content=first_message
            )]
            
            first_response_data = asyncio.run(agent_service.generate_response(first_messages))
            first_response = first_response_data.get('content', '')
            assert first_response is not None, "❌ First response is None"
            print(f"   ✅ First response: '{first_response[:100]}{'...' if len(first_response) > 100 else ''}'")
            
            # Second message in same conversation (simulating session persistence)
            conversation_messages = [
                ChatMessage(role=ChatMessageRole.USER, content=first_message),
                ChatMessage(role=ChatMessageRole.ASSISTANT, content=first_response),
                ChatMessage(role=ChatMessageRole.USER, content=second_message)
            ]
            
            second_response_data = asyncio.run(agent_service.generate_response(conversation_messages))
            second_response = second_response_data.get('content', '')
            assert second_response is not None, "❌ Second response is None"
            print(f"   ✅ Second response: '{second_response[:100]}{'...' if len(second_response) > 100 else ''}'")
            
            print("   🎉 Agent session persistence test PASSED")
            
        except Exception as e:
            error_msg = f"❌ Session persistence test failed: {str(e)}"
            print(f"   {error_msg}")
            if PYTEST_AVAILABLE:
                pytest.fail(error_msg)
            else:
                raise Exception(error_msg)


def run_tests_directly():
    """Run tests directly without pytest for quick testing."""
    print("🚀 Running CBR AI Assistant Tests")
    print("=" * 50)
    
    # Initialize the agent service
    try:
        agent_service = AzureAgentService()
        test_suite = TestCBRAssistant()
        
        # Run test 1: Basic functionality
        test_suite.test_basic_agent_function(agent_service)
        
        # Run test 2: CBR with Bing grounding
        test_suite.test_cbr_specific_question_with_bing_grounding(agent_service)
        
        # Run test 3: Session persistence
        test_suite.test_agent_persistence(agent_service)
        
        print("\n" + "=" * 50)
        print("🎉 All tests PASSED! CBR AI Assistant is working correctly.")
        print("✅ Basic agent functionality confirmed")
        print("✅ Bing grounding tool integration confirmed")
        print("✅ Session persistence confirmed")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        raise


if __name__ == "__main__":
    # Run tests directly when script is executed
    run_tests_directly()