#!/usr/bin/env python3
"""
Test different model names to find one that works
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from config_simple import get_settings

async def test_model_names():
    """Test different model names to see which ones work."""
    print("🧪 Testing Different Model Names")
    print("=" * 50)
    
    settings = get_settings()
    
    # Common model names to try
    models_to_test = [
        "gpt-4o",
        "gpt-4o-mini", 
        "gpt-35-turbo",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "text-davinci-003"
    ]
    
    try:
        project_client = AIProjectClient(
            endpoint=settings.azure_ai_foundry_endpoint,
            credential=DefaultAzureCredential(),
            subscription_id=settings.azure_subscription_id,
            resource_group_name=settings.azure_resource_group,
            project_name=settings.azure_project_name,
        )
        
        with project_client:
            for model_name in models_to_test:
                print(f"\n🔍 Testing model: {model_name}")
                try:
                    # Try to create an agent with this model
                    agent = project_client.agents.create_agent(
                        model=model_name,
                        name=f"Test Agent - {model_name}",
                        instructions="You are a test agent.",
                        temperature=0.7,
                        headers={"x-ms-enable-preview": "true"},
                    )
                    
                    print(f"  ✅ SUCCESS! Model '{model_name}' is available")
                    print(f"     Agent ID: {agent.id}")
                    
                    # Clean up - delete the test agent
                    try:
                        project_client.agents.delete_agent(agent.id)
                        print(f"     🧹 Cleaned up test agent")
                    except:
                        pass
                    
                    print(f"\n🎉 FOUND WORKING MODEL: {model_name}")
                    print(f"💡 Update your .env file with:")
                    print(f"   AGENT_MODEL_DEPLOYMENT_NAME={model_name}")
                    break
                    
                except Exception as e:
                    print(f"  ❌ FAILED: {e}")
                    if "invalid_engine_error" in str(e):
                        print(f"     Model '{model_name}' is not deployed in your project")
                    continue
            else:
                print(f"\n❌ None of the tested models are available in your project")
                print(f"💡 You may need to deploy a model in Azure AI Foundry first")
        
    except Exception as e:
        print(f"❌ Error connecting to Azure AI Foundry: {e}")

if __name__ == "__main__":
    asyncio.run(test_model_names())