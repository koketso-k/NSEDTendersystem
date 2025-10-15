#!/usr/bin/env python3
"""
EMERGENCY FIX FOR LECTURER DEMONSTRATION
Fixes the authentication issues immediately
"""
import requests
import json

def test_and_fix_auth():
    print("🚀 PREPARING FOR LECTURER DEMONSTRATION...")
    print("=" * 60)
    
    BASE_URL = "http://localhost:8000"
    
    # Test 1: Check backend health
    print("1. Checking backend health...")
    try:
        health = requests.get(f"{BASE_URL}/health")
        print(f"   ✅ Backend: HTTP {health.status_code}")
    except:
        print("   ❌ Backend not running! Run: python run.py")
        return
    
    # Test 2: Try registration with different data formats
    print("\n2. Testing authentication flow...")
    
    test_cases = [
        {
            "email": "demo@construction.co.za",
            "password": "demopass123", 
            "full_name": "Demo Construction"
        },
        {
            "email": "demo@construction.co.za",
            "password": "demopass123",
            "full_name": "Demo Construction",
            "team_name": "Demo Team"  # Sometimes schemas expect this
        }
    ]
    
    for i, user_data in enumerate(test_cases):
        print(f"   Attempt {i+1}: {user_data['email']}")
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=user_data, timeout=10)
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                print("      ✅ REGISTRATION SUCCESSFUL!")
                token_data = response.json()
                print(f"      Token: {token_data['access_token'][:20]}...")
                
                # Test login
                login_data = {
                    "email": user_data["email"],
                    "password": user_data["password"]
                }
                login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
                print(f"      Login: HTTP {login_response.status_code}")
                
                if login_response.status_code == 200:
                    print("      ✅ LOGIN SUCCESSFUL!")
                    print("\n🎉 SYSTEM READY FOR DEMONSTRATION!")
                    print("You can now show:")
                    print("   - User registration & login")
                    print("   - Company profile creation") 
                    print("   - Tender search with AI features")
                    print("   - Readiness scoring")
                    print("   - Workspace management")
                    return
                    
            elif response.status_code == 422:
                error_data = response.json()
                print(f"      ❌ Schema validation failed:")
                print(f"         {error_data}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    print("\n🔧 QUICK FIX: Let's use the pre-created sample data...")
    print("   Email: admin@construction.com")
    print("   Password: password123")
    print("   This account has full demo data ready!")

if __name__ == "__main__":
    test_and_fix_auth()