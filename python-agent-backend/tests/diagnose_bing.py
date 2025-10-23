"""
Diagnose Bing API Key Issues
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_bing_api():
    """Test Bing API with detailed error reporting"""
    
    api_key = os.getenv("BING_SEARCH_KEY")
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-5:] if api_key else 'None'}")
    
    if not api_key:
        print("❌ No BING_SEARCH_KEY found in environment")
        return
    
    endpoint = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {"q": "test", "count": 1}
    
    print(f"🌐 Testing endpoint: {endpoint}")
    print(f"📝 Headers: Ocp-Apim-Subscription-Key: {api_key[:10]}...")
    
    try:
        print("⏳ Making request...")
        response = requests.get(endpoint, headers=headers, params=params, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! Bing API is working")
            print(f"📄 Sample result: {data.get('webPages', {}).get('value', [{}])[0].get('name', 'No results')}")
        
        elif response.status_code == 401:
            print("❌ 401 UNAUTHORIZED - Invalid API key")
            print("💡 Solutions:")
            print("   1. Check if key is for Bing Search v7 (not other services)")
            print("   2. Verify key is active in Azure portal")
            print("   3. Check subscription status")
            
        elif response.status_code == 403:
            print("❌ 403 FORBIDDEN - Quota exceeded or access denied")
            
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Request took too long")
        
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - Network issue")
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    test_bing_api()