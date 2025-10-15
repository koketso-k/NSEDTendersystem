#!/usr/bin/env python3
"""
QUICK FIX FOR TENDERHUB MAIN.PY ISSUES
Fixes the 422 and 403 errors identified by the doctor
"""

import re
from pathlib import Path

def fix_main_py_issues():
    """Fix the main.py authentication and validation issues"""
    main_py_path = Path("main.py")
    
    if not main_py_path.exists():
        print("❌ main.py not found!")
        return False
    
    # Read the current file
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes_applied = []
    
    # FIX 1: Check if schemas are properly imported and used
    if "UserCreate" not in content or "UserLogin" not in content:
        print("❌ UserCreate/UserLogin schemas might be missing from imports")
    
    # FIX 2: Check authentication dependencies in endpoints
    # Look for endpoints missing authentication
    endpoints_needing_auth = [
        "/auth/me",
        "/tenders/search", 
        "/workspace/tenders",
        "/company-profiles"
    ]
    
    for endpoint in endpoints_needing_auth:
        if endpoint in content:
            # Check if endpoint has current_user dependency
            endpoint_pattern = f'@app[.a-z]*("{re.escape(endpoint)}"'
            if endpoint_pattern in content:
                # Check if it uses current_user
                if "current_user: UserResponse = Depends(get_current_user)" not in content:
                    print(f"⚠️  Endpoint {endpoint} might be missing authentication")
    
    # FIX 3: Add missing company profiles endpoint if needed
    if '"/company-profiles/{team_id}"' not in content:
        print("❌ Company profiles endpoint might be missing or different")
    
    # FIX 4: Check CORS configuration (common 403 cause)
    if "allow_origins" in content:
        origins = re.findall(r'allow_origins=\[([^\]]+)\]', content)
        if origins and "http://localhost:3000" not in origins[0]:
            print("❌ CORS might not include frontend origin")
    
    print("\n🔧 APPLYING FIXES...")
    
    # Apply fix for authentication in tenders/search if needed
    if '@app.post("/tenders/search")' in content:
        if "current_user: UserResponse = Depends(get_current_user)" not in content:
            # Fix the search endpoint authentication
            old_search = '''@app.post("/tenders/search", response_model=SearchResponse, tags=["Tenders"])\nasync def search_tenders(\n    search_data: SearchRequest,\n    db: SessionLocal = Depends(get_db)\n):'''
            
            new_search = '''@app.post("/tenders/search", response_model=SearchResponse, tags=["Tenders"])\nasync def search_tenders(\n    search_data: SearchRequest,\n    current_user: UserResponse = Depends(get_current_user),\n    db: SessionLocal = Depends(get_db)\n):'''
            
            if old_search in content:
                content = content.replace(old_search, new_search)
                fixes_applied.append("Added authentication to /tenders/search")
    
    # Write the fixed content back
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    if fixes_applied:
        print("✅ Fixes applied:")
        for fix in fixes_applied:
            print(f"   - {fix}")
    else:
        print("ℹ️  No automatic fixes needed - issues might be in schema validation")
    
    return True

def check_schema_issues():
    """Check for schema validation issues"""
    schemas_path = Path("schemas.py")
    
    if not schemas_path.exists():
        print("❌ schemas.py not found!")
        return
    
    with open(schemas_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for common schema issues
    required_schemas = ["UserCreate", "UserLogin", "Token", "UserResponse"]
    missing_schemas = []
    
    for schema in required_schemas:
        if f"class {schema}" not in content:
            missing_schemas.append(schema)
    
    if missing_schemas:
        print(f"❌ Missing schemas: {', '.join(missing_schemas)}")
    else:
        print("✅ All required schemas present")

def create_test_client():
    """Create a test client to verify fixes"""
    test_code = '''#!/usr/bin/env python3
"""
Test client to verify the fixes
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_fixes():
    print("🧪 Testing fixed endpoints...")
    
    # Test registration
    test_user = {
        "email": "test_fix@example.com",
        "password": "testpass123",
        "full_name": "Test Fix User"
    }
    
    try:
        # Test registration
        print("1. Testing registration...")
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user, timeout=10)
        print(f"   Registration: HTTP {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
        
        # Test login
        print("2. Testing login...")
        login_response = requests.post(f"{BASE_URL}/auth/login", 
                                     json={"email": test_user["email"], "password": test_user["password"]}, 
                                     timeout=10)
        print(f"   Login: HTTP {login_response.status_code}")
        
        if login_response.status_code == 200:
            token = login_response.json().get('access_token')
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test authenticated endpoints
            print("3. Testing authenticated endpoints...")
            
            # Test /auth/me
            me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
            print(f"   /auth/me: HTTP {me_response.status_code}")
            
            # Test /tenders/search
            search_response = requests.post(f"{BASE_URL}/tenders/search", 
                                          headers=headers, json={}, timeout=10)
            print(f"   /tenders/search: HTTP {search_response.status_code}")
            
        else:
            print(f"   Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_fixes()
'''
    
    with open("test_fixes.py", "w") as f:
        f.write(test_code)
    
    print("✅ Created test_fixes.py - run it to verify fixes")

def main():
    print("🛠️  QUICK FIX FOR TENDERHUB AUTHENTICATION ISSUES")
    print("=" * 50)
    
    # Apply fixes
    fix_main_py_issues()
    check_schema_issues()
    create_test_client()
    
    print("\n🎯 NEXT STEPS:")
    print("1. Run: python test_fixes.py")
    print("2. Check the output for HTTP status codes")
    print("3. If still 422 errors, check your schemas.py for validation rules")
    print("4. If 403 errors, check authentication dependencies in main.py")

if __name__ == "__main__":
    main()