#!/usr/bin/env python3
"""
TENDERHUB SYSTEM DOCTOR
Identifies problems, locates the exact file/line, and can auto-fix them
"""

import os
import sys
import re
import inspect
import importlib
from pathlib import Path
import requests
import json
from datetime import datetime

class TenderHubDoctor:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.diagnosis = {}
        self.fixes_applied = []
        
    def diagnose_system(self):
        """Run comprehensive diagnosis"""
        print("🩺 TENDERHUB SYSTEM DOCTOR - Starting Diagnosis...\n")
        
        checks = [
            self.check_backend_health,
            self.check_database_config,
            self.check_auth_system,
            self.check_api_endpoints,
            self.check_file_structure,
            self.check_imports,
            self.check_ocds_client,
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                self.record_issue(f"Check {check.__name__}", f"Check crashed: {e}", "Unknown")
        
        return self.generate_prescription()
    
    def check_backend_health(self):
        """Check if backend is running and healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.record_healthy("Backend", "Backend server is running and healthy")
            else:
                self.record_issue("Backend", f"HTTP {response.status_code}", "Backend server")
        except Exception as e:
            self.record_issue("Backend", f"Not running: {e}", "Backend server", "Start backend with: python run.py")
    
    def check_database_config(self):
        """Check database configurations and connections"""
        issues = []
        
        # Check .env file
        env_file = Path(".env")
        if not env_file.exists():
            issues.append(("Missing .env file", "Create .env with database credentials"))
        else:
            with open(env_file) as f:
                env_content = f.read()
                if "DATABASE_URL" not in env_content:
                    issues.append(("Missing DATABASE_URL", "Add DATABASE_URL to .env"))
                if "MONGO_URL" not in env_content:
                    issues.append(("Missing MONGO_URL", "Add MONGO_URL to .env"))
        
        # Test database connections
        try:
            from database import SessionLocal, engine
            with SessionLocal() as db:
                from sqlalchemy import text
                db.execute(text("SELECT 1"))
            self.record_healthy("SQL Database", "Connection successful")
        except Exception as e:
            error_str = str(e)
            if "text(" in error_str:
                issues.append(("SQLAlchemy text() issue", "database.py", "Add 'from sqlalchemy import text' and wrap raw SQL"))
            else:
                issues.append(("SQL Connection failed", f"database.py: {error_str}"))
        
        try:
            from database import mongo_db
            mongo_db.command('ping')
            self.record_healthy("MongoDB", "Connection successful")
        except Exception as e:
            issues.append(("MongoDB Connection failed", f"database.py: {e}"))
        
        for issue, fix in issues:
            self.record_issue("Database", issue, "database.py/.env", fix)
    
    def check_auth_system(self):
        """Check authentication system"""
        try:
            # Test registration
            test_user = {
                "email": f"doctor_test_{datetime.now().strftime('%H%M%S')}@test.com",
                "password": "doctorpass123",
                "full_name": "Doctor Test User"
            }
            
            response = requests.post(f"{self.base_url}/auth/register", json=test_user, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json().get('user', {})
                team_id = user_data.get('team_id')
                
                # Test protected endpoint with correct team_id
                token = response.json().get('access_token')
                headers = {"Authorization": f"Bearer {token}"}
                
                # Test company profile endpoint
                profile_response = requests.get(
                    f"{self.base_url}/company-profiles/{team_id}", 
                    headers=headers, 
                    timeout=10
                )
                
                if profile_response.status_code == 200:
                    self.record_healthy("Authentication", "Full auth flow working")
                elif profile_response.status_code == 403:
                    self.record_issue("Authentication", "Team access violation in endpoint", 
                                    "main.py company-profile endpoint", 
                                    "Ensure team_id validation uses current_user.team_id")
                else:
                    self.record_issue("Authentication", f"Profile endpoint: {profile_response.status_code}", 
                                    "main.py", "Check company profile endpoint logic")
                    
            else:
                self.record_issue("Authentication", f"Registration failed: {response.status_code}", 
                                "auth.py/main.py", "Check user registration logic")
                
        except Exception as e:
            self.record_issue("Authentication", f"Auth test failed: {e}", "auth.py", "Check authentication service")
    
    def check_api_endpoints(self):
        """Check all API endpoints for issues"""
        endpoints = {
            "/auth/register": "POST",
            "/auth/login": "POST", 
            "/auth/me": "GET",
            "/tenders/search": "POST",
            "/workspace/tenders": "GET",
        }
        
        for endpoint, method in endpoints.items():
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", json={}, timeout=5)
                
                if response.status_code not in [200, 201]:
                    self.record_issue("API Endpoint", f"{endpoint}: HTTP {response.status_code}", 
                                    "main.py", f"Check {endpoint} route implementation")
            except Exception as e:
                self.record_issue("API Endpoint", f"{endpoint}: {e}", "main.py", f"Fix {endpoint} route")
    
    def check_file_structure(self):
        """Verify all required files exist"""
        required_files = [
            "main.py",
            "auth.py", 
            "database.py",
            "schemas.py",
            "ai_services.py",
            "readiness_scorer.py",
            "ocds_client.py",
            "mongodb_service.py",
            "../frontend/main.js",
            "../frontend/style.css",
            "../frontend/components/auth.js",
            "../frontend/components/dashboard.js",
            "../frontend/components/search.js",
            "../frontend/components/workspace.js",
            "../frontend/components/profile.js",
        ]
        
        for file_path in required_files:
            if not Path(file_path).exists():
                self.record_issue("File Structure", f"Missing: {file_path}", file_path, "Create the missing file")
            else:
                self.record_healthy("File Structure", f"Found: {file_path}")
    
    def check_imports(self):
        """Check for import issues in Python files"""
        python_files = [
            "main.py",
            "auth.py",
            "database.py", 
            "schemas.py",
            "ai_services.py",
            "readiness_scorer.py",
            "ocds_client.py",
            "mongodb_service.py",
        ]
        
        for py_file in python_files:
            if Path(py_file).exists():
                try:
                    # Try to import the module
                    module_name = py_file.replace('.py', '')
                    spec = importlib.util.spec_from_file_location(module_name, py_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.record_healthy("Imports", f"{py_file}: No import errors")
                except Exception as e:
                    self.record_issue("Imports", f"{py_file}: {e}", py_file, "Fix import statements")
    
    def check_ocds_client(self):
        """Check OCDS client implementation"""
        try:
            from ocds_client import OCDSClient
            client = OCDSClient()
            
            # Check for required methods
            required_methods = ['fetch_tenders', 'get_tenders', 'search_tenders', 'sync_tenders_to_database']
            found_methods = []
            
            for method in required_methods:
                if hasattr(client, method):
                    found_methods.append(method)
            
            if found_methods:
                self.record_healthy("OCDS Client", f"Has methods: {', '.join(found_methods)}")
            else:
                self.record_issue("OCDS Client", "No tender fetch methods found", "ocds_client.py", 
                                "Implement fetch_tenders() or get_tenders() method")
                
        except Exception as e:
            self.record_issue("OCDS Client", f"Import/init failed: {e}", "ocds_client.py", "Fix OCDS client implementation")
    
    def record_healthy(self, category, message):
        """Record healthy component"""
        if category not in self.diagnosis:
            self.diagnosis[category] = []
        self.diagnosis[category].append({
            "status": "healthy",
            "message": message,
            "file": "N/A",
            "fix": "None needed"
        })
        print(f"✅ {category}: {message}")
    
    def record_issue(self, category, problem, file, fix_suggestion):
        """Record an issue with fix suggestion"""
        if category not in self.diagnosis:
            self.diagnosis[category] = []
        self.diagnosis[category].append({
            "status": "issue",
            "problem": problem,
            "file": file,
            "fix": fix_suggestion
        })
        print(f"❌ {category}: {problem}")
        print(f"   📁 File: {file}")
        print(f"   🔧 Fix: {fix_suggestion}\n")
    
    def auto_fix_issues(self):
        """Attempt to automatically fix common issues"""
        print("\n🛠️  ATTEMPTING AUTO-FIXES...")
        
        fixes = [
            self.fix_sqlalchemy_text,
            self.fix_missing_env,
            self.fix_ocds_methods,
        ]
        
        for fix_func in fixes:
            try:
                fix_func()
            except Exception as e:
                print(f"⚠️  Auto-fix {fix_func.__name__} failed: {e}")
    
    def fix_sqlalchemy_text(self):
        """Fix SQLAlchemy text() import issue"""
        database_file = Path("database.py")
        if database_file.exists():
            with open(database_file, 'r') as f:
                content = f.read()
            
            # Check if text import is missing
            if "from sqlalchemy import text" not in content and "text(" in content:
                # Add the import
                new_content = content.replace(
                    "from sqlalchemy import create_engine",
                    "from sqlalchemy import create_engine, text"
                )
                
                with open(database_file, 'w') as f:
                    f.write(new_content)
                
                self.fixes_applied.append("Added text import to database.py")
                print("✅ Fixed: Added 'text' import to database.py")
    
    def fix_missing_env(self):
        """Create basic .env file if missing"""
        env_file = Path(".env")
        if not env_file.exists():
            env_content = """# Database Configuration
DATABASE_URL=mysql+pymysql://tender_user:tenderpass123@localhost/tender_hub
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DB_NAME=tender_hub

# JWT Authentication
SECRET_KEY=your-super-secret-key-change-in-production-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# External APIs
OCDS_API_URL=https://api.etenders.gov.za/api/ocds

# AI Configuration
HUGGINGFACE_MODEL=facebook/bart-large-cnn
"""
            with open(env_file, 'w') as f:
                f.write(env_content)
            
            self.fixes_applied.append("Created .env file with basic configuration")
            print("✅ Fixed: Created .env file with basic configuration")
    
    def fix_ocds_methods(self):
        """Add basic OCDS methods if missing"""
        ocds_file = Path("ocds_client.py")
        if ocds_file.exists():
            with open(ocds_file, 'r') as f:
                content = f.read()
            
            # Check if fetch_tenders method exists
            if "def fetch_tenders" not in content:
                # Add the method
                fetch_method = '''
    def fetch_tenders(self, limit=50):
        """Fetch tenders from OCDS API with fallback to sample data"""
        try:
            # Try real API
            response = requests.get(f"{self.base_url}/releases", timeout=10)
            if response.status_code == 200:
                return response.json().get('releases', [])[:limit]
        except Exception as e:
            print(f"OCDS API unavailable: {e}")
        
        # Fallback to sample data
        from sample_data import sample_tenders
        return sample_tenders[:limit]
'''
                
                # Insert before the last line (usually the class end)
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip() == '':  # Find first empty line before class end
                        lines.insert(i, fetch_method)
                        break
                
                new_content = '\n'.join(lines)
                with open(ocds_file, 'w') as f:
                    f.write(new_content)
                
                self.fixes_applied.append("Added fetch_tenders method to ocds_client.py")
                print("✅ Fixed: Added fetch_tenders method to ocds_client.py")
    
    def generate_prescription(self):
        """Generate final report with fixes"""
        print("\n" + "="*70)
        print("💊 SYSTEM DOCTOR PRESCRIPTION")
        print("="*70)
        
        total_issues = sum(len([i for i in items if i['status'] == 'issue']) 
                          for items in self.diagnosis.values())
        
        print(f"\n📊 DIAGNOSIS: {total_issues} issues found")
        
        if self.fixes_applied:
            print(f"🔧 AUTO-FIXES APPLIED: {len(self.fixes_applied)}")
            for fix in self.fixes_applied:
                print(f"   ✅ {fix}")
        
        print("\n📋 MANUAL FIXES REQUIRED:")
        for category, items in self.diagnosis.items():
            issues = [i for i in items if i['status'] == 'issue']
            for issue in issues:
                print(f"\n   🚨 {category}")
                print(f"      Problem: {issue['problem']}")
                print(f"      File: {issue['file']}")
                print(f"      Solution: {issue['fix']}")
        
        # Save detailed report
        report = {
            "timestamp": datetime.now().isoformat(),
            "diagnosis": self.diagnosis,
            "fixes_applied": self.fixes_applied,
            "summary": f"{total_issues} issues found"
        }
        
        report_file = f"doctor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Full report saved to: {report_file}")
        
        return total_issues == 0

def main():
    """Run the system doctor"""
    doctor = TenderHubDoctor()
    
    # Run diagnosis
    is_healthy = doctor.diagnose_system()
    
    # Attempt auto-fixes
    doctor.auto_fix_issues()
    
    # Generate final prescription
    final_healthy = doctor.generate_prescription()
    
    if final_healthy:
        print("\n🎉 ALL SYSTEMS HEALTHY! Your TenderHub is ready to run!")
    else:
        print("\n🔧 Apply the manual fixes above, then run the doctor again.")

if __name__ == "__main__":
    main()