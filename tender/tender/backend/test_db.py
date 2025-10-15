# test_db.py - Database connection test
import mysql.connector
from database import SessionLocal, Base, engine
import os
from dotenv import load_dotenv

load_dotenv()

def test_mysql_connection():
    print("🧪 Testing MySQL Connection...")
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='J@ck@$$1',
            database='tender_hub'
        )
        print("✅ MySQL connection successful!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()
        print(f"✅ Connected to database: {db_name[0]}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        return False

def test_sqlalchemy_connection():
    print("🧪 Testing SQLAlchemy Connection...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ SQLAlchemy tables created successfully!")
        
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("✅ SQLAlchemy session working!")
        return True
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Database Tests...")
    
    mysql_ok = test_mysql_connection()
    sqlalchemy_ok = test_sqlalchemy_connection()
    
    if mysql_ok and sqlalchemy_ok:
        print("🎉 All database tests passed!")
    else:
        print("❌ Some tests failed.")