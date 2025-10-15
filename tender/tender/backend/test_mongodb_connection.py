from database import mongo_db

def test_mongodb():
    print("🧪 Testing MongoDB Connection...")
    
    try:
        # Test if we have real MongoDB
        if hasattr(mongo_db, 'list_collection_names'):
            collections = mongo_db.list_collection_names()
            print(f"✅ Real MongoDB Connected!")
            print(f"📁 Collections: {collections}")
            
            # Test insert
            test_doc = {"test": "MongoDB is working", "timestamp": "now"}
            result = mongo_db["test_collection"].insert_one(test_doc)
            print(f"✅ Insert test - Document ID: {result.inserted_id}")
            
            # Test read
            found = mongo_db["test_collection"].find_one({"_id": result.inserted_id})
            print(f"✅ Read test - Found: {found}")
            
            # Cleanup
            mongo_db["test_collection"].delete_one({"_id": result.inserted_id})
            print("✅ Cleanup completed")
            
        else:
            print("❌ Using Mock MongoDB (not real MongoDB)")
            
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")

if __name__ == "__main__":
    test_mongodb()