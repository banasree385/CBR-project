#!/usr/bin/env python3
"""
Check available models in Azure AI Foundry project
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from config_simple import get_settings

def check_available_models():
    """Check what models are available in the Azure AI Foundry project."""
    print("🔍 Checking Available Models in Azure AI Foundry")
    print("=" * 60)
    
    settings = get_settings()
    
    try:
        # Initialize client
        project_client = AIProjectClient(
            endpoint=settings.azure_ai_foundry_endpoint,
            credential=DefaultAzureCredential(),
            subscription_id=settings.azure_subscription_id,
            resource_group_name=settings.azure_resource_group,
            project_name=settings.azure_project_name,
        )
        
        print(f"Project: {settings.azure_project_name}")
        print(f"Resource Group: {settings.azure_resource_group}")
        print(f"Endpoint: {settings.azure_ai_foundry_endpoint}")
        print()
        
        with project_client:
            try:
                # Try to list available models/deployments
                print("📋 Available models/deployments:")
                
                # Check if we can list connections to see available models
                try:
                    connections = project_client.connections.list()
                    print("Available connections:")
                    for conn in connections:
                        print(f"  - {conn.name} ({conn.connection_type})")
                except Exception as e:
                    print(f"Could not list connections: {e}")
                
                print("\n💡 Common model names to try:")
                print("  - gpt-35-turbo")
                print("  - gpt-4o")
                print("  - gpt-4o-mini")
                print("  - gpt-4-turbo")
                print("  - text-embedding-ada-002")
                
                print("\n🔧 Current configuration uses: gpt-4")
                print("💭 Suggestion: Update AGENT_MODEL_DEPLOYMENT_NAME in .env file")
                
            except Exception as e:
                print(f"Error accessing project details: {e}")
                print("\n💡 Try these common model deployment names:")
                print("  - gpt-35-turbo")
                print("  - gpt-4o")
                print("  - gpt-4o-mini")
        
    except Exception as e:
        print(f"❌ Error connecting to Azure AI Foundry: {e}")
        print("\n💡 Common model deployment names to try:")
        print("  - gpt-35-turbo")
        print("  - gpt-4o") 
        print("  - gpt-4o-mini")

if __name__ == "__main__":
    check_available_models()