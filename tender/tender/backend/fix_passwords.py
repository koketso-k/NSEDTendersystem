# fix_passwords.py
from database import SessionLocal, User
from auth import get_password_hash

def fix_passwords():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            user.hashed_password = get_password_hash("temp123")
            print(f"✅ Reset password for {user.email}")
        
        db.commit()
        print("✅ All passwords reset to 'temp123'")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_passwords()