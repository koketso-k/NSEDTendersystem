# setup_mysql.py
import mysql.connector
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

def setup_mysql_database():
    print("🔧 Setting up MySQL database...")
    
    try:
        # Connect to MySQL server (without database)
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='J@ck@$$1'
        )
        
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS tender_hub")
        print("✅ Database 'tender_hub' created or already exists")
        
        cursor.close()
        conn.close()
        
        # Test connection to the specific database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='J@ck@$$1',
            database='tender_hub'
        )
        
        print("✅ MySQL connection successful!")
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ MySQL setup failed: {e}")
        return False

if __name__ == "__main__":
    setup_mysql_database()