# diagnose_data.py
from database import mongo_db, SessionLocal
from sqlalchemy import text
from pprint import pprint
import json
from bson import ObjectId
from datetime import datetime

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def check_readiness_checks():
    print("🔍 CHECKING READINESS CHECKS")
    print("=" * 40)
    
    checks = list(mongo_db.readiness_checks.find().limit(5))
    if checks:
        print(f"Found {len(checks)} readiness checks:")
        for check in checks:
            clean = json.loads(json.dumps(check, cls=JSONEncoder))
            print(f"  - Tender: {clean.get('tender_id')}, Team: {clean.get('team_id')}")
            print(f"    Score: {clean.get('suitability_score', 'N/A')}%")
            print(f"    Date: {clean.get('calculated_at', 'N/A')}")
            print()
    else:
        print("No readiness checks found")

def check_why_no_activity():
    print("\n🔍 CHECKING WHY NO ACTIVITY LOGS")
    print("=" * 40)
    
    # Check if mongodb_service is working
    from mongodb_service import MongoDBService
    mongo_service = MongoDBService()
    
    # Test logging
    print("Testing activity logging...")
    try:
        mongo_service.log_user_activity(
            user_id=1,
            team_id=1, 
            action="diagnostic_test",
            details={"test": "diagnostic check"}
        )
        print("✅ Activity logging test PASSED")
        
        # Check if the test log was saved
        test_logs = list(mongo_db.activity_logs.find({"action": "diagnostic_test"}))
        print(f"Test logs found: {len(test_logs)}")
        
    except Exception as e:
        print(f"❌ Activity logging test FAILED: {e}")

def check_mysql_sample_data():
    print("\n🔍 MYSQL SAMPLE DATA")
    print("=" * 40)
    
    db = SessionLocal()
    try:
        # Sample tenders
        tenders = db.execute(text("SELECT id, tender_id, title FROM tenders LIMIT 3")).fetchall()
        print("Sample Tenders:")
        for tender in tenders:
            print(f"  - {tender[0]}: {tender[1]} - {tender[2]}")
        
        # Sample users
        users = db.execute(text("SELECT id, email, team_id FROM users LIMIT 3")).fetchall()
        print("\nSample Users:")
        for user in users:
            print(f"  - {user[0]}: {user[1]} (Team: {user[2]})")
            
    finally:
        db.close()

def check_mongodb_service_connection():
    print("\n🔍 MONGODB SERVICE CONNECTION")
    print("=" * 40)
    
    try:
        from mongodb_service import MongoDBService
        service = MongoDBService()
        
        # Test basic operations
        stats = service.get_database_stats()
        print("✅ MongoDB Service connected successfully")
        print(f"Database stats: {stats}")
        
    except Exception as e:
        print(f"❌ MongoDB Service connection failed: {e}")

if __name__ == "__main__":
    print("🔧 DATABASE DIAGNOSTIC TOOL")
    print("=" * 50)
    
    check_readiness_checks()
    check_why_no_activity() 
    check_mysql_sample_data()
    check_mongodb_service_connection()
    
    print("\n✅ Diagnostic completed!")