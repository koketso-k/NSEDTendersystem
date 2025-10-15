# check_mongodb.py
from database import mongo_db

# Check AI summaries
summaries = mongo_db.ai_summaries.find().limit(3)
print("🤖 AI Summaries:")
for summary in summaries:
    print(f"  📄 Tender {summary.get('tender_id')}: {summary.get('summary', '')[:50]}...")

# Check user activities
activities = mongo_db.user_activities.find().limit(3) 
print("📱 User Activities:")
for activity in activities:
    print(f"  👤 User {activity.get('user_id')}: {activity.get('action')}")

print("✅ MongoDB is working!")