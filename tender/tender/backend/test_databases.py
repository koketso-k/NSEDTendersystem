# test_databases.py - FIXED VERSION (No Deprecation Warnings)

import sys
import os
from datetime import datetime, timezone  # ADD timezone import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import test_database_connections, get_database_stats, mongo_db, SessionLocal, mongo_client
from sqlalchemy import text

def test_both_databases():
    """Test both MySQL and MongoDB connections"""
    print("🚀 TESTING BOTH DATABASES")
    print("=" * 50)
    
    # Test connections
    connection_results = test_database_connections()
    
    # Check MySQL connection
    mysql_connected = connection_results["mysql"]
    print(f"✅ MySQL connection test: {'PASSED' if mysql_connected else 'FAILED'}")
    
    # Check MongoDB connection
    mongodb_connected = connection_results["mongodb"]
    print(f"✅ MongoDB connection test: {'PASSED' if mongodb_connected else 'FAILED'}")
    
    # Print raw connection status
    print(f"✅ MySQL: {mysql_connected}")
    print(f"✅ MongoDB: {mongodb_connected}")
    
    # Get statistics
    stats = get_database_stats()
    
    print(f"\n📊 MySQL Stats: {stats['mysql']}")
    print(f"📊 MongoDB Stats: {stats['mongodb']}")
    
    # Test basic operations
    test_basic_operations()
    
    return connection_results

def test_basic_operations():
    """Test basic database operations"""
    print(f"\n🔧 TESTING BASIC OPERATIONS")
    print("=" * 50)
    
    # Test MySQL operations
    try:
        db = SessionLocal()
        # Test user count
        user_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        print(f"✅ MySQL users count: {user_count}")
        
        # Test tender count
        tender_count = db.execute(text("SELECT COUNT(*) FROM tenders")).scalar()
        print(f"✅ MySQL tenders count: {tender_count}")
        
        db.close()
    except Exception as e:
        print(f"❌ MySQL operations failed: {e}")
    
    # Test MongoDB operations
    if mongo_db is not None:
        try:
            # Test readiness_checks collection
            readiness_count = mongo_db["readiness_checks"].count_documents({})
            print(f"✅ MongoDB readiness_checks count: {readiness_count}")
            
            # Test inserting a test document - FIXED: Use timezone-aware datetime
            test_doc = {"test": "connection", "timestamp": datetime.now(timezone.utc)}
            result = mongo_db["test_collection"].insert_one(test_doc)
            print(f"✅ MongoDB test insert: {result.acknowledged}")
            
            # Clean up test document
            mongo_db["test_collection"].delete_one({"_id": result.inserted_id})
            print("✅ MongoDB test cleanup: completed")
            
        except Exception as e:
            print(f"❌ MongoDB operations failed: {e}")
    else:
        print("❌ MongoDB operations: SKIPPED (no database connection)")

if __name__ == "__main__":
    test_both_databases()