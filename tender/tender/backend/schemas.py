# schemas.py - COMPLETE FIXED VERSION FOR MULTI-TENANT SaaS

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums for better type safety
class PlanTier(str, Enum):
    FREE = "free"
    BASIC = "basic" 
    PRO = "pro"

class TenderStatus(str, Enum):
    PENDING = "pending"
    INTERESTED = "interested"
    NOT_ELIGIBLE = "not_eligible"
    SUBMITTED = "submitted"

class IndustrySector(str, Enum):
    CONSTRUCTION = "Construction"
    IT_SERVICES = "IT Services"
    SECURITY = "Security"
    CLEANING = "Cleaning"
    TRANSPORT = "Transport"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    AGRICULTURE = "Agriculture"
    MINING = "Mining"
    MANUFACTURING = "Manufacturing"
    GENERAL_SERVICES = "General Services"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    team_id: Optional[int] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    team_id: int
    is_team_admin: bool
    plan_tier: str
    team_name: Optional[str] = None
    has_company_profile: Optional[bool] = False
    created_at: datetime

    class Config:
        from_attributes = True

# Team Schemas
class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    plan_tier: PlanTier = PlanTier.FREE

class TeamCreate(TeamBase):
    pass

class TeamResponse(TeamBase):
    id: int
    created_at: datetime
    user_count: int = 0
    company_profile_exists: bool = False

    class Config:
        from_attributes = True

# Company Profile Schemas
class CompanyProfileBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    industry_sector: IndustrySector
    services_provided: str = Field(..., min_length=10, max_length=2000)
    certifications: Dict[str, Any] = Field(default_factory=dict)
    geographic_coverage: List[str] = Field(..., min_items=1)
    years_experience: int = Field(..., ge=0, le=100)
    contact_email: EmailStr
    contact_phone: str = Field(..., min_length=10, max_length=20)

    @validator('geographic_coverage')
    def validate_provinces(cls, v):
        valid_provinces = [
            "Gauteng", "Western Cape", "KwaZulu-Natal", "Eastern Cape",
            "Limpopo", "Mpumalanga", "North West", "Free State", "Northern Cape"
        ]
        for province in v:
            if province not in valid_provinces:
                raise ValueError(f"Invalid province: {province}. Must be one of {valid_provinces}")
        return v

class CompanyProfileCreate(CompanyProfileBase):
    team_id: int

class CompanyProfileUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    industry_sector: Optional[IndustrySector] = None
    services_provided: Optional[str] = Field(None, min_length=10, max_length=2000)
    certifications: Optional[Dict[str, Any]] = None
    geographic_coverage: Optional[List[str]] = Field(None, min_items=1)
    years_experience: Optional[int] = Field(None, ge=0, le=100)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, min_length=10, max_length=20)

class CompanyProfileResponse(CompanyProfileBase):
    id: int
    team_id: int
    updated_at: datetime

    class Config:
        from_attributes = True

# Tender Schemas
class TenderBase(BaseModel):
    tender_id: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=5, max_length=500)
    description: str
    province: str
    submission_deadline: datetime
    buyer_organization: str = Field(..., min_length=1, max_length=255)
    budget_range: str
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    source_url: str
    document_url: Optional[str] = None

    @validator('budget_max')
    def validate_budget_range(cls, v, values):
        if 'budget_min' in values and v is not None and values['budget_min'] is not None:
            if v < values['budget_min']:
                raise ValueError('budget_max must be greater than or equal to budget_min')
        return v

class TenderCreate(TenderBase):
    pass

class TenderResponse(TenderBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Workspace Schemas
class WorkspaceTenderBase(BaseModel):
    tender_id: int
    status: TenderStatus = TenderStatus.PENDING
    notes: Optional[str] = Field(None, max_length=1000)

class WorkspaceTenderCreate(WorkspaceTenderBase):
    team_id: int

class WorkspaceTenderUpdate(BaseModel):
    status: Optional[TenderStatus] = None
    notes: Optional[str] = Field(None, max_length=1000)
    match_score: Optional[float] = Field(None, ge=0, le=100)

class WorkspaceTenderResponse(WorkspaceTenderBase):
    id: int
    team_id: int
    match_score: Optional[float]
    last_updated_by: int
    last_updated_at: datetime
    tender: 'TenderResponse'

    class Config:
        from_attributes = True

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[int] = None
    team_id: Optional[int] = None

# Search and AI Schemas
class SearchRequest(BaseModel):
    keywords: str = Field("", max_length=100)
    province: Optional[str] = None
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    buyer_organization: Optional[str] = Field(None, max_length=255)
    deadline_window: Optional[int] = Field(None, ge=1, le=365)  # days

class SearchResponse(BaseModel):
    count: int
    results: List[TenderResponse]

class SummaryRequest(BaseModel):
    document_url: str
    tender_id: int

class SummaryResponse(BaseModel):
    summary: str
    key_points: Dict[str, Any]
    industry_sector: Optional[str] = None
    complexity_score: Optional[int] = Field(None, ge=0, le=100)
    tender_id: int

class ReadinessCheckRequest(BaseModel):
    tender_id: int
    company_profile_id: Optional[int] = None

class ChecklistItem(BaseModel):
    criterion: str
    met: bool
    weight: Optional[float] = None

class ReadinessCheckResponse(BaseModel):
    suitability_score: float = Field(..., ge=0, le=100)
    checklist: List[ChecklistItem]
    recommendation: str
    scoring_breakdown: Optional[Dict[str, float]] = None
    tender_requirements: Optional[Dict[str, Any]] = None

# Analytics and Public API Schemas
class AnalyticsSpendByBuyer(BaseModel):
    buyer: str
    tender_count: int
    estimated_total_spend: float

class AnalyticsResponse(BaseModel):
    analytics: List[AnalyticsSpendByBuyer]

class TenderAnalytics(BaseModel):
    total_checks: int
    avg_score: float
    high_scores: int
    medium_scores: int
    low_scores: int
    success_rate: float

class EnrichedTenderResponse(BaseModel):
    tender_id: str
    title: str
    description: str
    province: str
    submission_deadline: Optional[str]
    buyer_organization: str
    budget_range: str
    ai_summary: str
    key_points: Dict[str, Any]
    industry_sector: Optional[str] = None
    complexity_score: Optional[int] = None

# User Activity and Team Management
class UserActivity(BaseModel):
    user_id: int
    team_id: int
    action: str
    details: Dict[str, Any]
    timestamp: datetime

class TeamInvite(BaseModel):
    email: EmailStr
    role: str = Field("member", pattern="^(member|admin)$")

class TeamLimits(BaseModel):
    user_count: int
    workspace_count: int
    max_users: Union[int, float]
    max_workspace: Union[int, float]
    can_add_user: bool
    can_add_workspace: bool

# Plan and Feature Schemas
class PlanFeatures(BaseModel):
    ai_summary: bool
    readiness_check: bool
    export: bool
    max_users: Union[int, float]
    max_searches: Union[int, float]
    workspace_size: Union[int, float]

class PlanInfo(BaseModel):
    tier: PlanTier
    features: PlanFeatures
    price: Optional[float] = None

# Response wrappers for consistent API responses
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None

# Pagination schemas
class PaginatedResponse(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
    total: int
    total_pages: int
    items: List[Any]

# Health check schema
class HealthCheck(BaseModel):
    status: str
    timestamp: str
    version: str
    database: Optional[str] = None
    mongodb: Optional[str] = None

# ========== ADDED MISSING SCHEMAS ==========

# OCDS API Schema (required by ocds_client.py)
class OCDSTender(BaseModel):
    ocid: str
    title: str
    description: str
    province: str
    submission_deadline: str
    buyer: Dict[str, str]
    value: Dict[str, Any]
    documents: List[Dict[str, str]]

    class Config:
        from_attributes = True

# Team Limits Extended Schema (for main.py compatibility)
class TeamLimitsExtended(BaseModel):
    plan_tier: str
    workspace_count: int
    max_workspace: Union[int, float]
    team_member_count: int
    max_users: Union[int, float]
    can_add_workspace: bool
    can_add_users: bool
    ai_features_enabled: bool
    readiness_check_enabled: bool
    export_enabled: bool

# Export schemas for reporting
class ExportRequest(BaseModel):
    format: str = Field(..., pattern="^(pdf|csv|json)$")
    tenders: List[int] = Field(..., min_items=1)
    include_summary: bool = False
    include_readiness: bool = False

class ExportResponse(BaseModel):
    export_id: str
    format: str
    download_url: str
    generated_at: datetime
    item_count: int

# Forward references for recursive models
WorkspaceTenderResponse.update_forward_refs()