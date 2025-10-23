"""
Test Bing Search Tool Directly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tools.bing_search import BingSearchTool

def test_bing_directly():
    print("🔍 Testing Bing Search Tool Directly")
    
    tool = BingSearchTool()
    
    queries = [
        "theory exam cost",
        "theorie examen kosten",
        "driving license requirements"
    ]
    
    for query in queries:
        print(f"\n--- Searching: {query} ---")
        result = tool.search_cbr(query, max_results=2)
        
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
        elif result.get("results"):
            print(f"✅ Found {len(result['results'])} results:")
            for i, item in enumerate(result["results"], 1):
                print(f"{i}. {item['title']}")
                print(f"   URL: {item['url']}")
                print(f"   Content: {item['snippet'][:100]}...")
        else:
            print("No results found")

if __name__ == "__main__":
    test_bing_directly()