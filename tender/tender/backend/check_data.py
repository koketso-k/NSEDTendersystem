# check_data.py
from database import mongo_db, SessionLocal
from sqlalchemy import text

# Check MySQL
db = SessionLocal()
try:
    result = db.execute(text("SHOW TABLES"))
    tables = [row[0] for row in result]
    print("✅ MySQL Tables:", tables)
    
    for table in tables:
        count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        print(f"   {table}: {count} records")
finally:
    db.close()

# Check MongoDB
print("✅ MongoDB Collections:")
collections = mongo_db.list_collection_names()
for coll in collections:
    count = mongo_db[coll].count_documents({})
    print(f"   {coll}: {count} documents")