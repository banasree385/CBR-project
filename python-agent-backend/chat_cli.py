#!/usr/bin/env python3
"""
Command-line chat interface for Azure AI Agent
Run: python chat_cli.py
"""

import asyncio
import sys
import os
from typing import List

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.azure_agent_service import SimpleAzureAgentService
from models.chat import ChatMessage, MessageRole


class ChatCLI:
    """Command-line chat interface for Azure AI Agent."""
    
    def __init__(self):
        self.service = SimpleAzureAgentService()
        self.chat_history: List[ChatMessage] = []
        self.initialized = False
    
    async def initialize(self):
        """Initialize the agent service."""
        print("🤖 Initializing Azure AI Agent...")
        
        # Verify connection
        if not await self.service.verify_connection():
            print("❌ Failed to connect to Azure AI Foundry")
            return False
        
        # Initialize agent
        if not await self.service.initialize_agent():
            print("❌ Failed to initialize agent")
            return False
        
        print("✅ Agent initialized successfully!")
        self.initialized = True
        return True
    
    async def send_message(self, user_input: str) -> str:
        """Send a message to the agent and get response."""
        if not self.initialized:
            return "❌ Agent not initialized"
        
        # Add user message to history
        user_message = ChatMessage(role=MessageRole.USER, content=user_input)
        self.chat_history.append(user_message)
        
        # Get response from agent
        try:
            print("🤔 Thinking...")
            response = await self.service.generate_response(self.chat_history)
            
            agent_content = response.get('content', 'No response received')
            response_time = response.get('response_time', 0)
            model_used = response.get('model_used', 'unknown')
            
            # Add agent response to history
            agent_message = ChatMessage(role=MessageRole.ASSISTANT, content=agent_content)
            self.chat_history.append(agent_message)
            
            print(f"⚡ Response ({response_time:.1f}s, {model_used})")
            return agent_content
            
        except Exception as e:
            return f"❌ Error: {e}"
    
    def print_welcome(self):
        """Print welcome message."""
        print("=" * 60)
        print("🚀 Azure AI Agent - Command Line Chat")
        print("=" * 60)
        print("Commands:")
        print("  • Type your message and press Enter")
        print("  • Type 'quit', 'exit', or 'bye' to end chat")
        print("  • Type 'clear' to clear chat history")
        print("  • Type 'history' to see conversation history")
        print("=" * 60)
    
    def print_history(self):
        """Print chat history."""
        if not self.chat_history:
            print("📝 No chat history yet")
            return
        
        print("\n📝 Chat History:")
        print("-" * 40)
        for i, msg in enumerate(self.chat_history, 1):
            role_emoji = "👤" if msg.role == MessageRole.USER else "🤖"
            role_name = "You" if msg.role == MessageRole.USER else "Agent"
            print(f"{i}. {role_emoji} {role_name}: {msg.content}")
        print("-" * 40)
    
    async def run(self):
        """Run the chat interface."""
        self.print_welcome()
        
        # Initialize agent
        if not await self.initialize():
            print("❌ Failed to initialize. Exiting...")
            return
        
        print("\n💬 Start chatting! (type 'quit' to exit)")
        print("=" * 60)
        
        try:
            while True:
                # Get user input
                try:
                    user_input = input("\n👤 You: ").strip()
                except KeyboardInterrupt:
                    print("\n\n👋 Chat interrupted. Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Check for commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'clear':
                    self.chat_history.clear()
                    print("🧹 Chat history cleared!")
                    continue
                elif user_input.lower() == 'history':
                    self.print_history()
                    continue
                
                # Send message to agent
                response = await self.send_message(user_input)
                print(f"\n🤖 Agent: {response}")
        
        except Exception as e:
            print(f"\n❌ Chat error: {e}")
        
        finally:
            # Cleanup
            print("\n🧹 Cleaning up...")
            try:
                await self.service.cleanup()
                print("✅ Cleanup completed")
            except:
                pass


async def main():
    """Main function."""
    chat = ChatCLI()
    await chat.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)