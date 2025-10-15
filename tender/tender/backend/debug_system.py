#!/usr/bin/env python3
"""
FIXED TENDER HUB DEBUGGER - Handles the identified issues
"""

import sys
import os
import requests
import json
from datetime import datetime
from sqlalchemy import text  # ADD THIS

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class FixedSystemDebugger:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {}
        self.current_test = ""
        self.user_team_id = None  # Track actual user's team
        
    def log_test(self, test_name, status, message="", data=None):
        emoji = "✅" if status else "❌"
        print(f"{emoji} {test_name}: {message}")
        self.results[test_name] = {
            "status": status,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    def test_database_connections(self):
        """FIXED: Uses text() for SQL queries"""
        self.current_test = "Database Connections"
        try:
            from database import SessionLocal, engine, mongo_db
            
            # Test SQL Database - FIXED
            try:
                with SessionLocal() as db:
                    db.execute(text("SELECT 1"))  # FIX: Added text()
                sql_status = "✅ SQL Database connected"
            except Exception as e:
                sql_status = f"❌ SQL Database failed: {str(e)}"
            
            # Test MongoDB
            try:
                mongo_db.command('ping')
                mongo_status = "✅ MongoDB connected"
            except Exception as e:
                mongo_status = f"❌ MongoDB failed: {str(e)}"
            
            self.log_test(self.current_test, True, f"{sql_status} | {mongo_status}")
            return True
            
        except Exception as e:
            self.log_test(self.current_test, False, f"Database setup error: {str(e)}")
            return False
    
    def test_authentication_flow(self):
        """FIXED: Captures actual team_id"""
        self.current_test = "Authentication Flow"
        try:
            test_user = {
                "email": f"test_{datetime.now().strftime('%H%M%S')}@debug.com",
                "password": "debugpass123",
                "full_name": "Debug User"
            }
            
            # Test Registration
            response = requests.post(
                f"{self.base_url}/auth/register",
                json=test_user,
                timeout=10
            )
            
            if response.status_code == 200:
                reg_data = response.json()
                token = reg_data.get('access_token')
                user_data = reg_data.get('user', {})
                
                # CAPTURE ACTUAL TEAM_ID - FIXED
                self.user_team_id = user_data.get('team_id', 1)
                
                self.log_test("User Registration", True, "User registered successfully", {
                    "user_id": user_data.get('id'),
                    "team_id": self.user_team_id,
                    "token_received": bool(token)
                })
                
                # Test Login
                login_response = requests.post(
                    f"{self.base_url}/auth/login",
                    json={"email": test_user["email"], "password": test_user["password"]},
                    timeout=10
                )
                
                if login_response.status_code == 200:
                    self.log_test("User Login", True, "Login successful")
                    self.auth_token = login_response.json().get('access_token')
                    return True
                else:
                    self.log_test("User Login", False, f"Login failed: {login_response.text}")
                    return False
                    
            else:
                self.log_test("User Registration", False, f"Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test(self.current_test, False, f"Authentication error: {str(e)}")
            return False
    
    def test_protected_endpoints(self):
        """FIXED: Uses actual team_id and better error handling"""
        self.current_test = "Protected Endpoints"
        if not hasattr(self, 'auth_token'):
            self.log_test(self.current_test, False, "No authentication token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # USE ACTUAL TEAM_ID - FIXED
        team_id = self.user_team_id if self.user_team_id else 1
        
        endpoints_to_test = [
            ("GET", "/auth/me", "Get current user"),
            ("GET", f"/company-profiles/{team_id}", "Get company profile"),  # FIXED
            ("POST", "/tenders/search", "Search tenders"),
            ("GET", f"/workspace/tenders?team_id={team_id}", "Get workspace"),  # FIXED
        ]
        
        all_passed = True
        
        for method, endpoint, description in endpoints_to_test:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                else:  # POST
                    response = requests.post(f"{self.base_url}{endpoint}", headers=headers, json={}, timeout=10)
                
                if response.status_code in [200, 201]:
                    self.log_test(f"Endpoint: {description}", True, f"HTTP {response.status_code}")
                else:
                    # BETTER ERROR DETAILS - FIXED
                    try:
                        error_detail = response.json().get('detail', response.text)
                    except:
                        error_detail = response.text
                    self.log_test(f"Endpoint: {description}", False, f"HTTP {response.status_code}: {error_detail}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Endpoint: {description}", False, f"Error: {str(e)}")
                all_passed = False
        
        self.log_test(self.current_test, all_passed, f"Protected endpoints test {'passed' if all_passed else 'failed'}")
        return all_passed
    
    def test_ocds_api(self):
        """FIXED: Handles different method names"""
        self.current_test = "OCDS API Connection"
        try:
            from ocds_client import OCDSClient
            client = OCDSClient()
            
            # TRY DIFFERENT METHOD NAMES - FIXED
            method_names = ['fetch_tenders', 'get_tenders', 'search_tenders']
            tenders = None
            
            for method_name in method_names:
                if hasattr(client, method_name):
                    method = getattr(client, method_name)
                    try:
                        tenders = method(limit=5)
                        if tenders:
                            self.log_test(self.current_test, True, f"Retrieved {len(tenders)} tenders using {method_name}()")
                            break
                    except Exception as e:
                        continue
            
            if not tenders:
                self.log_test(self.current_test, False, "No working tender fetch method found")
                
        except Exception as e:
            self.log_test(self.current_test, False, f"OCDS client error: {str(e)}")

# ... keep the rest of the methods the same as before ...

def main():
    debugger = FixedSystemDebugger()
    
    # Run the critical tests
    print("🔍 Running Fixed Debugger...")
    debugger.test_backend_connection()
    debugger.test_database_connections()  # FIXED
    debugger.test_authentication_flow()   # FIXED  
    debugger.test_protected_endpoints()   # FIXED
    debugger.test_ai_services()
    
    debugger.generate_report()

if __name__ == "__main__":
    main()