import bcrypt
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "supersecret"  

class AuthService:
    """Handles user authentication and JWT token management."""

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def create_token(self, user_id: str, expires_in=3600):
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
