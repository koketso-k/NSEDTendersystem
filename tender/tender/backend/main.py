# main.py - COMPLETE FIXED VERSION WITH AI-POWERED ANALYTICS
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from routes.admin import router as admin_router
import json
import asyncio
import csv
import io
from sqlalchemy import func

from database import SessionLocal, mongo_db, User, Team, CompanyProfile, Tender, WorkspaceTender
from schemas import *
from auth import (
    get_current_user, create_access_token, get_password_hash, verify_password,
    require_team_access, require_team_admin, require_feature_access,
    require_ai_access, require_readiness_access, require_export_access,
    get_user_team_limits, check_plan_feature_access
)
from document_processor import DocumentProcessor
from readiness_scorer import ReadinessScorer
from ai_services import AIService
from ocds_client import OCDSClient
from mongodb_service import MongoDBService

# Initialize FastAPI app
app = FastAPI(
    title="Tender Insight Hub",
    description="AI-powered SaaS platform for South African SMEs to navigate public procurement",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User registration, login, and token management"
        },
        {
            "name": "Tenders", 
            "description": "Search and browse tender opportunities"
        },
        {
            "name": "AI Features",
            "description": "AI-powered document analysis and readiness scoring"
        },
        {
            "name": "Workspace",
            "description": "Manage tender applications and track progress"
        },
        {
            "name": "Company Profiles",
            "description": "Manage company information for better matching"
        },
        {
            "name": "Analytics",
            "description": "Public API endpoints for tender analytics"
        },
        {
            "name": "Team Management",
            "description": "Team and user management for multi-tenant SaaS"
        },
        {
            "name": "Export",
            "description": "Data export functionality for Pro tier"
        }
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add admin routes
app.include_router(admin_router)

# Initialize services
document_processor = DocumentProcessor()
readiness_scorer = ReadinessScorer()
ai_service = AIService()
ocds_client = OCDSClient()
mongodb_service = MongoDBService()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========== AUTHENTICATION ENDPOINTS ==========

@app.post("/auth/register", response_model=Token, tags=["Authentication"])
async def register(user_data: UserCreate, db: SessionLocal = Depends(get_db)):
    """
    Register a new user and create their team
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create team for the user
    team = Team(
        name=f"{user_data.full_name}'s Team",
        plan_tier="free"  # Default to free tier
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    
    # Create user as team admin
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        team_id=team.id,
        is_team_admin=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token_expires = timedelta(minutes=60 * 24)
    access_token = create_access_token(
        data={"sub": user.id}, 
        expires_delta=access_token_expires
    )
    
    # Get user response with team info
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        team_id=user.team_id,
        is_team_admin=user.is_team_admin,
        created_at=user.created_at,
        plan_tier=team.plan_tier,
        team_name=team.name,
        has_company_profile=False
    )
    
    # Log registration activity
    mongodb_service.log_user_activity(
        user_id=user.id,
        team_id=team.id,
        action="user_registered",
        details={"plan_tier": team.plan_tier}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": access_token_expires.total_seconds(),
        "user": user_response
    }

@app.post("/auth/login", response_model=Token, tags=["Authentication"])
async def login(login_data: UserLogin, db: SessionLocal = Depends(get_db)):
    """
    Login user and return access token
    """
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Get user's team and company profile
    team = db.query(Team).filter(Team.id == user.team_id).first()
    company_profile = db.query(CompanyProfile).filter(CompanyProfile.team_id == user.team_id).first()
    
    # Create access token
    access_token_expires = timedelta(minutes=60 * 24)
    access_token = create_access_token(
        data={"sub": user.id}, 
        expires_delta=access_token_expires
    )
    
    user_response = UserResponse(
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
    
    # Log login activity
    mongodb_service.log_user_activity(
        user_id=user.id,
        team_id=user.team_id,
        action="user_login",
        details={}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": access_token_expires.total_seconds(),
        "user": user_response
    }

@app.get("/auth/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_endpoint(current_user: UserResponse = Depends(get_current_user)):
    """
    Get current user information
    """
    return current_user

@app.post("/auth/refresh", response_model=Token, tags=["Authentication"])
async def refresh_token(current_user: UserResponse = Depends(get_current_user)):
    """
    Refresh access token
    """
    access_token_expires = timedelta(minutes=60 * 24)
    new_access_token = create_access_token(
        data={"sub": current_user.id}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": access_token_expires.total_seconds(),
        "user": current_user
    }

# ========== COMPANY PROFILE ENDPOINTS ==========

@app.post("/company-profiles", response_model=CompanyProfileResponse, tags=["Company Profiles"])
async def create_company_profile(
    profile_data: CompanyProfileCreate, 
    current_user: UserResponse = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    """
    Create or update company profile for user's team
    """
    # Verify user has access to the team
    if current_user.team_id != profile_data.team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create profile for another team"
        )
    
    # Check if profile already exists
    existing_profile = db.query(CompanyProfile).filter(CompanyProfile.team_id == profile_data.team_id).first()
    
    if existing_profile:
        # Update existing profile
        for field, value in profile_data.dict().items():
            setattr(existing_profile, field, value)
        existing_profile.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(existing_profile)
        
        profile_response = CompanyProfileResponse.from_orm(existing_profile)
    else:
        # Create new profile
        profile = CompanyProfile(**profile_data.dict())
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        profile_response = CompanyProfileResponse.from_orm(profile)
    
    # Log profile activity
    mongodb_service.log_user_activity(
        user_id=current_user.id,
        team_id=current_user.team_id,
        action="company_profile_updated",
        details={"profile_id": profile_response.id}
    )
    
    return profile_response

@app.get("/company-profiles/{team_id}", response_model=CompanyProfileResponse, tags=["Company Profiles"])
async def get_company_profile(
    team_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    """
    Get company profile for specified team
    """
    if current_user.team_id != team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another team's profile"
        )
    
    profile = db.query(CompanyProfile).filter(CompanyProfile.team_id == team_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found"
        )
    
    return CompanyProfileResponse.from_orm(profile)

# ========== TENDER SEARCH ENDPOINTS ==========

@app.post("/tenders/search", response_model=SearchResponse, tags=["Tenders"])
async def search_tenders(
    search_data: SearchRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    """
    Search tenders with filtering and keyword matching
    """
    # Check search limits for free tier
    if current_user.plan_tier == "free":
        # Count searches in last week (simplified check)
        recent_searches = mongodb_service.get_user_activity(
            user_id=current_user.id, 
            limit=10
        )
        search_count = len([a for a in recent_searches if a.get("action") == "tender_search"])
        
        if search_count >= 3:  # Free tier limit
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Free tier search limit reached (3 searches per week). Upgrade to Basic or Pro."
            )
    
    query = db.query(Tender)
    
    # Keyword search
    if search_data.keywords:
        keywords = search_data.keywords.lower()
        query = query.filter(
            (Tender.title.ilike(f"%{keywords}%")) |
            (Tender.description.ilike(f"%{keywords}%"))
        )
    
    # Filters
    if search_data.province:
        query = query.filter(Tender.province == search_data.province)
    
    if search_data.buyer_organization:
        query = query.filter(Tender.buyer_organization.ilike(f"%{search_data.buyer_organization}%"))
    
    if search_data.budget_min:
        query = query.filter(Tender.budget_min >= search_data.budget_min)
    
    if search_data.budget_max:
        query = query.filter(Tender.budget_max <= search_data.budget_max)
    
    if search_data.deadline_window:
        deadline_cutoff = datetime.utcnow() + timedelta(days=search_data.deadline_window)
        query = query.filter(Tender.submission_deadline <= deadline_cutoff)
    
    # Execute query
    tenders = query.order_by(Tender.submission_deadline.asc()).limit(100).all()
    
    # Log search activity
    mongodb_service.log_user_activity(
        user_id=current_user.id,
        team_id=current_user.team_id,
        action="tender_search",
        details={
            "keywords": search_data.keywords,
            "result_count": len(tenders),
            "filters": search_data.dict(exclude={"keywords"})
        }
    )
    
    return SearchResponse(
        count=len(tenders),
        results=[TenderResponse.from_orm(tender) for tender in tenders]
    )

@app.get("/tenders/{tender_id}", response_model=TenderResponse, tags=["Tenders"])
async def get_tender(
    tender_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    """
    Get specific tender details
    """
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tender not found"
        )
    
    return TenderResponse.from_orm(tender)

# ========== AI FEATURES ENDPOINTS ==========

@app.post("/api/summary/extract", response_model=SummaryResponse, tags=["AI Features"])
async def extract_summary(
    request: SummaryRequest,
    current_user: UserResponse = Depends(require_ai_access),
    db: SessionLocal = Depends(get_db)
):
    """
    Extract AI summary from tender document (Basic/Pro tiers only)
    """
    tender = db.query(Tender).filter(Tender.id == request.tender_id).first()
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tender not found"
        )
    
    # FIX: Use tender's document_url if not provided in request
    document_url = request.document_url or tender.document_url
    
    if not document_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document URL required but not available for this tender"
        )
    
    try:
        # FIXED: Use the ai_service instance consistently
        result = ai_service.summarize_document(document_url, tender.title, tender.description)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        # Store in MongoDB
        mongodb_service.store_ai_summary(
            tender_id=request.tender_id,
            document_url=document_url,
            summary=result["summary"],
            key_points=result["key_points"],
            user_id=current_user.id,
            team_id=current_user.team_id
        )
        
        # Log AI usage
        mongodb_service.log_user_activity(
            user_id=current_user.id,
            team_id=current_user.team_id,
            action="ai_summary_generated",
            details={"tender_id": request.tender_id}
        )
        
        return SummaryResponse(
            summary=result["summary"],
            key_points=result["key_points"],
            industry_sector=result.get("industry_sector"),
            complexity_score=result.get("complexity_score"),
            tender_id=request.tender_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI summarization failed: {str(e)}"
        )

@app.post("/api/readiness/check", response_model=ReadinessCheckResponse, tags=["AI Features"])
async def check_readiness(
    request: ReadinessCheckRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    """
    Check company readiness for a tender (Basic/Pro tiers only)
    """
    # ADD PLAN CHECK HERE
    if not check_plan_feature_access(current_user, "readiness_check"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Readiness check not available on your current plan"
        )
    
    tender = db.query(Tender).filter(Tender.id == request.tender_id).first()
    company_profile = db.query(CompanyProfile).filter(CompanyProfile.team_id == current_user.team_id).first()
    
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tender not found"
        )
    
    if not company_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found. Please create a company profile first."
        )
    
    # Extract requirements and calculate score
    tender_requirements = readiness_scorer.extract_tender_requirements(
        tender.description, tender.title
    )
    
    result = readiness_scorer.calculate_suitability_score(
        company_profile, tender_requirements
    )
    
    # Store result in MongoDB
    mongodb_service.store_readiness_score(
        tender_id=request.tender_id,
        company_profile_id=company_profile.id,
        team_id=current_user.team_id,
        score_data=result,
        user_id=current_user.id
    )
    
    # Convert checklist to required format
    checklist_items = [
        ChecklistItem(criterion=k, met=v, weight=0.0) 
        for k, v in result.get("checklist", {}).items()
    ]
    
    # Log readiness check
    mongodb_service.log_user_activity(
        user_id=current_user.id,
        team_id=current_user.team_id,
        action="readiness_check_performed",
        details={
            "tender_id": request.tender_id,
            "score": result["suitability_score"]
        }
    )
    
    return ReadinessCheckResponse(
        suitability_score=result["suitability_score"],
        checklist=checklist_items,
        recommendation=result["recommendation"],
        scoring_breakdown=result.get("scoring_breakdown"),
        tender_requirements=result.get("tender_requirements")
    )

# ========== WORKSPACE ENDPOINTS ==========

@app.post("/workspace/tenders", response_model=SuccessResponse, tags=["Workspace"])
async def add_to_workspace(
    workspace_data: WorkspaceTenderCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    """
    Add tender to team workspace
    """
    if workspace_data.team_id != current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot add to another team's workspace"
        )
    
    # Check workspace limits
    limits = get_user_team_limits(current_user, db)
    if not limits["can_add_workspace"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Workspace limit reached ({limits['workspace_count']}/{limits['max_workspace']}). Upgrade plan to add more tenders."
        )
    
    # Check if already in workspace
    existing = db.query(WorkspaceTender).filter(
        WorkspaceTender.team_id == workspace_data.team_id,
        WorkspaceTender.tender_id == workspace_data.tender_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tender already in workspace"
        )
    
    # Add to workspace
    workspace_tender = WorkspaceTender(
        team_id=workspace_data.team_id,
        tender_id=workspace_data.tender_id,
        status=workspace_data.status,
        notes=workspace_data.notes,
        last_updated_by=current_user.id
    )
    
    db.add(workspace_tender)
    db.commit()
    
    # Log workspace activity
    mongodb_service.log_user_activity(
        user_id=current_user.id,
        team_id=current_user.team_id,
        action="tender_added_to_workspace",
        details={"tender_id": workspace_data.tender_id, "status": workspace_data.status}
    )
    
    return SuccessResponse(
        message="Tender added to workspace successfully",
        data={"workspace_id": workspace_tender.id}
    )

@app.get("/workspace/tenders", response_model=List[WorkspaceTenderResponse], tags=["Workspace"])
async def get_workspace_tenders(
    team_id: int,
    status: Optional[str] = None,  # FIXED: Changed from TenderStatus to str
    current_user: UserResponse = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    """
    Get tenders from team workspace with optional status filter
    """
    if team_id != current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another team's workspace"
        )
    
    query = db.query(WorkspaceTender).filter(WorkspaceTender.team_id == team_id)
    
    if status and status != "all":  # FIXED: Handle "all" status
        query = query.filter(WorkspaceTender.status == status)
    
    workspace_tenders = query.order_by(WorkspaceTender.last_updated_at.desc()).all()
    
    # Build response with tender details
    results = []
    for wt in workspace_tenders:
        tender = db.query(Tender).filter(Tender.id == wt.tender_id).first()
        if tender:
            results.append(WorkspaceTenderResponse(
                id=wt.id,
                team_id=wt.team_id,
                tender_id=wt.tender_id,
                status=wt.status,
                match_score=wt.match_score,
                last_updated_by=wt.last_updated_by,
                last_updated_at=wt.last_updated_at,
                notes=wt.notes,
                tender=TenderResponse.from_orm(tender)
            ))
    
    return results

@app.put("/workspace/tenders/{workspace_tender_id}", response_model=SuccessResponse, tags=["Workspace"])
async def update_workspace_tender(
    workspace_tender_id: int,
    update_data: WorkspaceTenderUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    """
    Update workspace tender status or notes
    """
    workspace_tender = db.query(WorkspaceTender).filter(WorkspaceTender.id == workspace_tender_id).first()
    
    if not workspace_tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace tender not found"
        )
    
    if workspace_tender.team_id != current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update another team's workspace"
        )
    
    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(workspace_tender, field, value)
    
    workspace_tender.last_updated_by = current_user.id
    workspace_tender.last_updated_at = datetime.utcnow()
    
    db.commit()
    
    # Log update activity
    mongodb_service.log_user_activity(
        user_id=current_user.id,
        team_id=current_user.team_id,
        action="workspace_tender_updated",
        details={
            "workspace_id": workspace_tender_id,
            "updates": update_data.dict(exclude_unset=True)
        }
    )
    
    return SuccessResponse(message="Workspace tender updated successfully")

@app.delete("/workspace/tenders/{workspace_tender_id}", response_model=SuccessResponse, tags=["Workspace"])
async def remove_from_workspace(
    workspace_tender_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    """
    Remove tender from workspace
    """
    workspace_tender = db.query(WorkspaceTender).filter(WorkspaceTender.id == workspace_tender_id).first()
    
    if not workspace_tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace tender not found"
        )
    
    if workspace_tender.team_id != current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot remove from another team's workspace"
        )
    
    db.delete(workspace_tender)
    db.commit()
    
    # Log removal activity
    mongodb_service.log_user_activity(
        user_id=current_user.id,
        team_id=current_user.team_id,
        action="tender_removed_from_workspace",
        details={"workspace_id": workspace_tender_id}
    )
    
    return SuccessResponse(message="Tender removed from workspace successfully")

# ========== EXPORT ENDPOINTS ==========

@app.get("/export/workspace/csv", tags=["Export"])
async def export_workspace_csv(
    current_user: UserResponse = Depends(require_export_access),
    db: SessionLocal = Depends(get_db)
):
    """
    Export workspace tenders as CSV (Pro tier only)
    """
    # Add rate limiting
    recent_exports = mongodb_service.get_user_activity(
        user_id=current_user.id, 
        action="workspace_exported_csv",
        limit=5
    )
    if len(recent_exports) >= 3:  # Max 3 exports per hour
        raise HTTPException(429, "Export limit reached. Please try again later.")

    # Get workspace tenders
    workspace_tenders = db.query(WorkspaceTender).filter(
        WorkspaceTender.team_id == current_user.team_id
    ).all()
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Tender ID', 'Title', 'Status', 'Match Score', 'Submission Deadline',
        'Buyer Organization', 'Budget Range', 'Notes', 'Last Updated'
    ])
    
    # Write data
    for wt in workspace_tenders:
        tender = db.query(Tender).filter(Tender.id == wt.tender_id).first()
        if tender:
            writer.writerow([
                tender.tender_id,
                tender.title,
                wt.status,
                f"{wt.match_score}%" if wt.match_score else "N/A",
                tender.submission_deadline.strftime('%Y-%m-%d') if tender.submission_deadline else 'N/A',
                tender.buyer_organization,
                tender.budget_range,
                wt.notes or '',
                wt.last_updated_at.strftime('%Y-%m-%d %H:%M')
            ])
    
    # Log export activity
    mongodb_service.log_user_activity(
        user_id=current_user.id,
        team_id=current_user.team_id,
        action="workspace_exported_csv",
        details={"tender_count": len(workspace_tenders)}
    )
    
    return {
        "filename": f"workspace_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        "content": output.getvalue(),
        "content_type": "text/csv"
    }

@app.get("/export/readiness-scores", tags=["Export"])
async def export_readiness_scores(
    current_user: UserResponse = Depends(require_export_access),
    db: SessionLocal = Depends(get_db)
):
    """
    Export readiness scores as JSON (Pro tier only)
    """
    # Get readiness scores from MongoDB
    readiness_scores = mongodb_service.get_team_readiness_scores(current_user.team_id, limit=100)
    
    # Log export activity
    mongodb_service.log_user_activity(
        user_id=current_user.id,
        team_id=current_user.team_id,
        action="readiness_scores_exported",
        details={"score_count": len(readiness_scores)}
    )
    
    return {
        "filename": f"readiness_scores_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        "content": json.dumps(readiness_scores, indent=2, default=str),
        "content_type": "application/json"
    }

# ========== TEAM MANAGEMENT ENDPOINTS ==========

@app.post("/team/invite", response_model=SuccessResponse, tags=["Team Management"])
async def invite_team_member(
    invite_data: dict,
    current_user: UserResponse = Depends(require_team_admin),
    db: SessionLocal = Depends(get_db)
):
    """
    Invite a new member to the team (Team admin only)
    """
    email = invite_data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    
    # Check team member limits
    limits = get_user_team_limits(current_user, db)
    if not limits["can_add_user"]:
        raise HTTPException(
            status_code=403,
            detail=f"Team member limit reached ({limits['user_count']}/{limits['max_users']}). Upgrade plan to add more members."
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # In a real implementation, you would send an invitation email
    # For now, we'll just log the invitation
    
    mongodb_service.log_user_activity(
        user_id=current_user.id,
        team_id=current_user.team_id,
        action="team_member_invited",
        details={"invited_email": email}
    )
    
    return SuccessResponse(
        message=f"Invitation sent to {email}",
        data={"email": email, "invited_by": current_user.full_name}
    )

@app.get("/team/limits", response_model=TeamLimits, tags=["Team Management"])
async def get_team_limits(
    current_user: UserResponse = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    """
    Get current team usage and limits
    """
    return get_user_team_limits(current_user, db)

@app.get("/team/members", response_model=List[UserResponse], tags=["Team Management"])
async def get_team_members(
    current_user: UserResponse = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    """
    Get all team members
    """
    team_members = db.query(User).filter(User.team_id == current_user.team_id).all()
    
    # Get team info for response
    team = db.query(Team).filter(Team.id == current_user.team_id).first()
    company_profile = db.query(CompanyProfile).filter(CompanyProfile.team_id == current_user.team_id).first()
    
    return [
        UserResponse(
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
        for user in team_members
    ]

# ========== PUBLIC API ENDPOINTS ==========

@app.get("/api/enriched-releases", response_model=List[EnrichedTenderResponse], tags=["Analytics"])
async def get_enriched_releases(limit: int = 10, db: SessionLocal = Depends(get_db)):
    """
    Public API: Get enriched tender data with AI summaries
    """
    tenders = db.query(Tender).order_by(Tender.created_at.desc()).limit(limit).all()
    
    result = []
    for tender in tenders:
        # Get AI summary from MongoDB
        summary_doc = mongodb_service.get_tender_summary(tender.id)
        
        result.append(EnrichedTenderResponse(
            tender_id=tender.tender_id,
            title=tender.title,
            description=tender.description,
            province=tender.province,
            submission_deadline=tender.submission_deadline.isoformat() if tender.submission_deadline else None,
            buyer_organization=tender.buyer_organization,
            budget_range=tender.budget_range,
            ai_summary=summary_doc["summary"] if summary_doc else "No summary available",
            key_points=summary_doc["key_points"] if summary_doc else {},
            industry_sector=summary_doc.get("industry_sector") if summary_doc else None,
            complexity_score=summary_doc.get("complexity_score") if summary_doc else None
        ))
    
    return result

@app.get("/api/analytics/spend-by-buyer", response_model=AnalyticsResponse, tags=["Analytics"])
async def get_spend_by_buyer(db: SessionLocal = Depends(get_db)):
    """
    Public API: Get government spending analytics by buyer organization
    """
    spend_analytics = db.query(
        Tender.buyer_organization,
        func.count(Tender.id).label('tender_count'),
        func.avg(Tender.budget_min).label('avg_budget_min'),
        func.avg(Tender.budget_max).label('avg_budget_max')
    ).group_by(Tender.buyer_organization).all()

    analytics = []
    for item in spend_analytics:
        avg_budget = ((item.avg_budget_min or 0) + (item.avg_budget_max or 0)) / 2
        estimated_total = avg_budget * (item.tender_count or 1)
        
        analytics.append(AnalyticsSpendByBuyer(
            buyer=item.buyer_organization or "Unknown",
            tender_count=item.tender_count or 0,
            estimated_total_spend=estimated_total
        ))
    
    return AnalyticsResponse(analytics=analytics)

# ========== AI-POWERED ANALYTICS ENDPOINTS ==========

@app.get("/api/analytics/industry-trends", response_model=AnalyticsResponse, tags=["Analytics"])
async def get_industry_trends(db: SessionLocal = Depends(get_db)):
    """
    AI-powered industry trend analysis across tenders
    """
    try:
        # Check cache first
        cached = mongodb_service.get_cached_analytics("industry_trends")
        if cached:
            print("✅ Using cached industry trends")
            return AnalyticsResponse(analytics=cached)
        
        # Get tenders for analysis
        tenders = db.query(Tender).limit(100).all()
        
        if not tenders:
            return AnalyticsResponse(analytics=[])
        
        # Generate AI-powered insights
        industry_analysis = ai_service.analyze_industry_trends(tenders)
        
        # Cache results for 6 hours
        mongodb_service.cache_analytics("industry_trends", industry_analysis, expiry_hours=6)
        
        print(f"✅ Generated AI industry trends for {len(tenders)} tenders")
        return AnalyticsResponse(analytics=industry_analysis)
        
    except Exception as e:
        print(f"❌ Industry trends analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Industry trends analysis failed: {str(e)}"
        )

@app.get("/api/analytics/complexity-analysis", response_model=AnalyticsResponse, tags=["Analytics"])
async def get_complexity_analysis(db: SessionLocal = Depends(get_db)):
    """
    AI-powered complexity analysis across tenders
    """
    try:
        # Check cache first
        cached = mongodb_service.get_cached_analytics("complexity_analysis")
        if cached:
            print("✅ Using cached complexity analysis")
            return AnalyticsResponse(analytics=cached)
        
        # Get tenders for analysis
        tenders = db.query(Tender).limit(100).all()
        
        if not tenders:
            return AnalyticsResponse(analytics=[])
        
        # Generate AI-powered insights
        complexity_analysis = ai_service.analyze_complexity_trends(tenders)
        
        # Cache results for 6 hours
        mongodb_service.cache_analytics("complexity_analysis", complexity_analysis, expiry_hours=6)
        
        print(f"✅ Generated AI complexity analysis for {len(tenders)} tenders")
        return AnalyticsResponse(analytics=complexity_analysis)
        
    except Exception as e:
        print(f"❌ Complexity analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Complexity analysis failed: {str(e)}"
        )

@app.get("/api/analytics/competition-insights", response_model=AnalyticsResponse, tags=["Analytics"])
async def get_competition_insights(db: SessionLocal = Depends(get_db)):
    """
    AI-powered competition and market insights
    """
    try:
        # Check cache first
        cached = mongodb_service.get_cached_analytics("competition_insights")
        if cached:
            print("✅ Using cached competition insights")
            return AnalyticsResponse(analytics=cached)
        
        # Get tenders for analysis
        tenders = db.query(Tender).limit(100).all()
        
        if not tenders:
            return AnalyticsResponse(analytics=[])
        
        # Generate AI-powered insights
        competition_insights = ai_service.analyze_competition_insights(tenders)
        
        # Cache results for 6 hours
        mongodb_service.cache_analytics("competition_insights", competition_insights, expiry_hours=6)
        
        print(f"✅ Generated AI competition insights for {len(tenders)} tenders")
        return AnalyticsResponse(analytics=competition_insights)
        
    except Exception as e:
        print(f"❌ Competition insights analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Competition insights analysis failed: {str(e)}"
        )

@app.get("/api/analytics/success-predictions", response_model=AnalyticsResponse, tags=["Analytics"])
async def get_success_predictions(
    current_user: UserResponse = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    """
    AI-powered success predictions based on company profile and market data
    """
    try:
        # Get company profile
        company_profile = db.query(CompanyProfile).filter(CompanyProfile.team_id == current_user.team_id).first()
        if not company_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company profile not found. Please create a company profile first."
            )
        
        # Get recent tenders in company's industry
        company_industry = company_profile.industry_sector or "General Services"
        tenders = db.query(Tender).filter(
            Tender.submission_deadline >= datetime.utcnow()
        ).limit(50).all()
        
        # Filter tenders by industry match
        relevant_tenders = []
        for tender in tenders:
            text = f"{tender.title} {tender.description or ''}"
            tender_industry = ai_service._detect_industry_sector(text.lower())
            if tender_industry == company_industry or company_industry in tender_industry:
                relevant_tenders.append(tender)
        
        # Generate success predictions
        predictions = []
        for tender in relevant_tenders[:10]:  # Analyze top 10 relevant tenders
            # Extract requirements
            tender_requirements = readiness_scorer.extract_tender_requirements(
                tender.description, tender.title
            )
            
            # Calculate readiness score
            readiness_result = readiness_scorer.calculate_suitability_score(
                company_profile, tender_requirements
            )
            
            # Generate prediction
            score = readiness_result["suitability_score"]
            if score >= 80:
                prediction = "High Success Probability"
            elif score >= 60:
                prediction = "Medium Success Probability"
            elif score >= 40:
                prediction = "Low Success Probability"
            else:
                prediction = "Very Low Success Probability"
            
            predictions.append({
                "tender_id": tender.id,
                "tender_title": tender.title,
                "readiness_score": score,
                "success_prediction": prediction,
                "key_factors": list(readiness_result.get("checklist", {}).keys())[:3],
                "recommendation": readiness_result.get("recommendation", "Assess carefully")
            })
        
        return AnalyticsResponse(analytics=predictions)
        
    except Exception as e:
        print(f"❌ Success predictions failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Success predictions failed: {str(e)}"
        )

# ========== HEALTH ENDPOINTS ==========

@app.get("/", tags=["Health"])
async def read_root():
    """
    Root endpoint
    """
    return {
        "message": "Tender Insight Hub API is running!",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check(db: SessionLocal = Depends(get_db)):
    """
    Health check endpoint
    """
    # Test database connection
    db_status = "healthy"
    try:
        db.execute("SELECT 1")
    except Exception:
        db_status = "unhealthy"
    
    # Test MongoDB connection
    mongo_status = "healthy"
    try:
        mongodb_service.get_database_stats()
    except Exception:
        mongo_status = "unhealthy"
    
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        database=db_status,
        mongodb=mongo_status
    )

# Background task to cleanup old data
@app.on_event("startup")
async def startup_event():
    """
    Startup tasks
    """
    # Sync some tenders on startup
    try:
        print("🔄 Starting initial tender sync...")
        ocds_client.sync_tenders_to_database(20)
        print("✅ Initial tender sync completed")
    except Exception as e:
        print(f"⚠️ Initial tender sync failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)