# test_activity.py
from mongodb_service import MongoDBService
import time

def test_real_activity():
    mongo_service = MongoDBService()
    
    print("🧪 Testing Real Activity Logging...")
    
    # Simulate user actions
    actions = [
        ("user_login", 1, 1),
        ("tender_search", 1, 1), 
        ("readiness_check", 1, 1),
        ("tender_added_to_workspace", 1, 1)
    ]
    
    for action, user_id, team_id in actions:
        print(f"Logging: {action}")
        mongo_service.log_user_activity(
            user_id=user_id,
            team_id=team_id,
            action=action,
            details={"test": True, "timestamp": time.time()}
        )
        time.sleep(1)
    
    # Check if logs were saved
    print("\n📋 Checking saved logs...")
    from database import mongo_db
    logs = list(mongo_db.activity_logs.find().sort("timestamp", -1).limit(5))
    print(f"Found {len(logs)} activity logs")
    
    for log in logs:
        print(f"  - {log.get('action')} at {log.get('timestamp')}")

if __name__ == "__main__":
    test_real_activity()