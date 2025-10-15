# generate_test_data.py
from database import SessionLocal, mongo_db
from datetime import datetime
import requests

def generate_test_data():
    print("🎯 GENERATING TEST DATA FOR BOTH DATABASES...")
    
    # Test MongoDB directly
    print("\n1. 📝 Adding test data to MongoDB...")
    
    # Add AI summary
    mongo_db.ai_summaries.insert_one({
        "tender_id": 999,
        "summary": "TEST AI SUMMARY - This is a test to verify MongoDB is working",
        "key_points": ["Test point 1", "Test point 2"],
        "industry_sector": "Construction",
        "complexity_score": 75,
        "created_at": datetime.utcnow()
    })
    print("   ✅ Added test AI summary to MongoDB")
    
    # Add user activity
    mongo_db.user_activities.insert_one({
        "user_id": 999,
        "action": "test_activity",
        "details": {"test": "This verifies MongoDB is storing data"},
        "timestamp": datetime.utcnow()
    })
    print("   ✅ Added test activity to MongoDB")
    
    # Test MySQL
    print("\n2. 💾 Adding test data to MySQL...")
    db = SessionLocal()
    
    # Add test user if not exists
    try:
        db.execute("INSERT OR IGNORE INTO users (email, hashed_password, full_name, team_id) VALUES (?, ?, ?, ?)",
                  ("test@verify.com", "test_hash", "Test User", 1))
        db.commit()
        print("   ✅ Added test user to MySQL")
    except:
        print("   ℹ️ Test user already exists")
    
    # Count records
    user_count = db.execute("SELECT COUNT(*) FROM users").scalar()
    tender_count = db.execute("SELECT COUNT(*) FROM tenders").scalar()
    
    print(f"\n📊 DATABASE COUNTS:")
    print(f"   MySQL - Users: {user_count}, Tenders: {tender_count}")
    print(f"   MongoDB - AI Summaries: {mongo_db.ai_summaries.count_documents({})}")
    print(f"   MongoDB - Activities: {mongo_db.user_activities.count_documents({})}")
    
    db.close()
    print("\n🎉 TEST DATA GENERATED SUCCESSFULLY!")

if __name__ == "__main__":
    generate_test_data()