# generate_test_data_fixed.py
from database import SessionLocal, mongo_db
from datetime import datetime
from sqlalchemy import text

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
        "created_at": datetime.now()
    })
    print("   ✅ Added test AI summary to MongoDB")
    
    # Add user activity
    mongo_db.user_activities.insert_one({
        "user_id": 999,
        "action": "test_activity",
        "details": {"test": "This verifies MongoDB is storing data"},
        "timestamp": datetime.now()
    })
    print("   ✅ Added test activity to MongoDB")
    
    # Test MySQL
    print("\n2. 💾 Checking data in MySQL...")
    db = SessionLocal()
    
    # Count records using text() wrapper
    user_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
    tender_count = db.execute(text("SELECT COUNT(*) FROM tenders")).scalar()
    profile_count = db.execute(text("SELECT COUNT(*) FROM company_profiles")).scalar()
    
    print(f"\n📊 DATABASE COUNTS:")
    print(f"   MySQL - Users: {user_count}, Tenders: {tender_count}, Profiles: {profile_count}")
    print(f"   MongoDB - AI Summaries: {mongo_db.ai_summaries.count_documents({})}")
    print(f"   MongoDB - Activities: {mongo_db.user_activities.count_documents({})}")
    
    # Show some actual data
    print(f"\n👥 SAMPLE USERS:")
    users = db.execute(text("SELECT email, full_name FROM users LIMIT 3")).fetchall()
    for user in users:
        print(f"   📧 {user.email} - {user.full_name}")
    
    db.close()
    print("\n🎉 TEST COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    generate_test_data()