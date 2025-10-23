"""
Test Bing Search using Azure AI Foundry Connection
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from app.config_simple import get_settings

def test_azure_ai_bing():
    """Test if we can use Bing through Azure AI Foundry"""
    
    settings = get_settings()
    
    print("🔍 Testing Bing through Azure AI Foundry...")
    print(f"🔑 Azure AI Key: {settings.azure_ai_foundry_key[:10]}...{settings.azure_ai_foundry_key[-5:]}")
    
    # Try using Azure AI Foundry key for Bing
    headers = {
        "Ocp-Apim-Subscription-Key": settings.azure_ai_foundry_key,
        "Content-Type": "application/json"
    }
    
    params = {"q": "test CBR", "count": 1}
    
    try:
        response = requests.get(
            "https://api.bing.microsoft.com/v7.0/search", 
            headers=headers, 
            params=params, 
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Azure AI Foundry key works for Bing")
            data = response.json()
            results = data.get('webPages', {}).get('value', [])
            if results:
                print(f"📄 Sample result: {results[0].get('name', 'No title')}")
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if test_azure_ai_bing():
        print("\n💡 Use your Azure AI Foundry key as BING_SEARCH_KEY")
    else:
        print("\n💡 You need a separate Bing Search API key")