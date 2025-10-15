# auth.py - COMPLETE FIXED VERSION WITH MULTI-TENANT SUPPORT
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import SessionLocal, User, Team, CompanyProfile
from schemas import UserResponse
import os

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production-12345")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours for better user experience

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    # Ensure subject is string for JWT compliance
    if 'sub' in to_encode:
        to_encode['sub'] = str(to_encode['sub'])
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),  # Issued at
        "type": "access_token"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Verify JWT token and return user ID"""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
        
        # Verify token type
        token_type = payload.get("type")
        if token_type != "access_token":
            raise credentials_exception
            
        return int(user_id)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception

def get_current_user(user_id: int = Depends(verify_token)) -> UserResponse:
    """Get current user with team and plan information"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Get user's team information
        team = db.query(Team).filter(Team.id == user.team_id).first()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        # Get company profile if exists
        company_profile = db.query(CompanyProfile).filter(CompanyProfile.team_id == team.id).first()
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            team_id=user.team_id,
            is_team_admin=user.is_team_admin,
            created_at=user.created_at,
            plan_tier=team.plan_tier,
            team_name=team.name,
            has_company_profile=company_profile is not None
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not validate credentials"
        )
    finally:
        db.close()

def get_current_active_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Get current active user (additional checks can be added here)"""
    # Add any additional active user checks here
    # For example: check if user is suspended, etc.
    return current_user

def check_team_access(current_user: UserResponse, team_id: int) -> bool:
    """Check if user has access to the specified team"""
    return current_user.team_id == team_id

def require_team_access(team_id: int):
    """Dependency to require team access"""
    def dependency(current_user: UserResponse = Depends(get_current_user)):
        if not check_team_access(current_user, team_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this team is denied"
            )
        return current_user
    return dependency

def require_team_admin(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Dependency to require team admin privileges"""
    if not current_user.is_team_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Team admin privileges required"
        )
    return current_user

def check_plan_feature_access(current_user: UserResponse, feature: str) -> bool:
    """Check if user's team has access to specific feature based on plan tier"""
    plan_features = {
        "free": {
            "ai_summary": False,
            "readiness_check": False,
            "export": False,
            "max_users": 1,
            "max_searches": 3,
            "workspace_size": 10
        },
        "basic": {
            "ai_summary": True,
            "readiness_check": True,
            "export": False,
            "max_users": 3,
            "max_searches": float('inf'),
            "workspace_size": 50
        },
        "pro": {
            "ai_summary": True,
            "readiness_check": True,
            "export": True,
            "max_users": float('inf'),
            "max_searches": float('inf'),
            "workspace_size": float('inf')
        }
    }
    
    plan_tier = current_user.plan_tier.lower()
    if plan_tier not in plan_features:
        return False
    
    return plan_features[plan_tier].get(feature, False)

def require_feature_access(feature: str):
    """Dependency to require specific feature access based on plan tier"""
    def dependency(current_user: UserResponse = Depends(get_current_user)):
        if not check_plan_feature_access(current_user, feature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature}' not available on your current plan ({current_user.plan_tier})"
            )
        return current_user
    return dependency

# Feature-specific dependencies for easy use in endpoints
require_ai_access = lambda: require_feature_access("ai_summary")
require_readiness_access = lambda: require_feature_access("readiness_check")
require_export_access = lambda: require_feature_access("export")

def get_user_team_limits(current_user: UserResponse, db) -> Dict[str, Any]:
    """Get user's team limits based on plan tier"""
    # Count current team users
    user_count = db.query(User).filter(User.team_id == current_user.team_id).count()
    
    # Count workspace items if needed
    from database import WorkspaceTender
    workspace_count = db.query(WorkspaceTender).filter(WorkspaceTender.team_id == current_user.team_id).count()
    
    plan_limits = {
        "free": {"max_users": 1, "max_workspace": 10},
        "basic": {"max_users": 3, "max_workspace": 50},
        "pro": {"max_users": float('inf'), "max_workspace": float('inf')}
    }
    
    limits = plan_limits.get(current_user.plan_tier, plan_limits["free"])
    
    return {
        "user_count": user_count,
        "workspace_count": workspace_count,
        "max_users": limits["max_users"],
        "max_workspace": limits["max_workspace"],
        "can_add_user": user_count < limits["max_users"],
        "can_add_workspace": workspace_count < limits["max_workspace"]
    }