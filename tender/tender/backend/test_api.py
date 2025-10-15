import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("🧪 Testing Tender Insight Hub API...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test public endpoints
    try:
        response = requests.post(f"{BASE_URL}/tenders/search", json={"keywords": "construction"})
        print(f"✅ Tender search: {response.status_code} - Found {len(response.json().get('results', []))} tenders")
    except Exception as e:
        print(f"❌ Tender search failed: {e}")
    
    # Test public API endpoints
    try:
        response = requests.get(f"{BASE_URL}/api/enriched-releases")
        print(f"✅ Enriched releases: {response.status_code} - {len(response.json())} items")
    except Exception as e:
        print(f"❌ Enriched releases failed: {e}")
    
    print("\n🎯 API Testing Complete!")

if __name__ == "__main__":
    test_api()
    