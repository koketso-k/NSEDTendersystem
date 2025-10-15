# test_mysql.py
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")

try:
    # Parse the URL manually
    if "mysql+pymysql://" in DATABASE_URL:
        url_parts = DATABASE_URL.replace("mysql+pymysql://", "").split("@")
        user_pass = url_parts[0].split(":")
        host_db = url_parts[1].split("/")
        
        username = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ""
        host = host_db[0]
        database = host_db[1] if len(host_db) > 1 else "tender_hub"
        
        # Test direct PyMySQL connection
        connection = pymysql.connect(
            host=host,
            user=username,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                print(f"✅ Direct MySQL connection successful: {result}")
        
except Exception as e:
    print(f"❌ Direct MySQL connection failed: {e}")