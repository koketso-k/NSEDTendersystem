# Create test_mysql_password.py
# test_mysql_password.py - Test MySQL connection
import mysql.connector

def test_mysql_connection():
    print("🔧 Testing MySQL connection...")
    
    # Try different connection methods
    configs = [
        {"host": "localhost", "user": "root", "password": "J@ck@$$1"},
        {"host": "localhost", "user": "root", "password": ""},  # Empty password
        {"host": "localhost", "user": "root", "password": "password"},  # Common password
    ]
    
    for config in configs:
        try:
            print(f"Trying: {config}")
            conn = mysql.connector.connect(**config)
            print(f"✅ SUCCESS with password: {config['password']}")
            conn.close()
            return config['password']
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    return None

if __name__ == "__main__":
    working_password = test_mysql_connection()
    if working_password:
        print(f"🎉 Use this password: {working_password}")
    else:
        print("❌ No password worked. Let's check MySQL service.")