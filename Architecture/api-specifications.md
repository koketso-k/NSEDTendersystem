# Tender Insight Hub - API Specification

## API Overview

The Tender Insight Hub provides a comprehensive RESTful API built with FastAPI, featuring automatic OpenAPI/Swagger documentation, JWT-based authentication, and multi-tenant access control. The API supports both web application functionality and third-party integrations.

### Base Information
- **Base URL**: `https://api.tenderinsight.co.za/api/v1`
- **Documentation**: `https://api.tenderinsight.co.za/docs` (Swagger UI)
- **Authentication**: JWT Bearer Token
- **Content Type**: `application/json`
- **API Version**: v1

### Authentication Flow
```http
POST /auth/login
Authorization: None
Content-Type: application/json

{
  "email": "user@company.com",
  "password": "secure_password"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "user_id": 123,
    "email": "user@company.com",
    "team_id": 456,
    "role": "admin"
  }
}
```

## Core API Endpoints

### 1. Authentication & User Management

#### POST /auth/login
**Description**: Authenticate user and receive JWT tokens

**Request Body**:
```json
{
  "email": "string",
  "password": "string"
}
```

**Response**: `200 OK`
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "user_id": 123,
    "email": "user@company.com",
    "team_id": 456,
    "role": "admin",
    "team_name": "ABC Construction"
  }
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials
- `422 Unprocessable Entity`: Validation errors

#### POST /auth/refresh
**Description**: Refresh access token using refresh token

**Request Body**:
```json
{
  "refresh_token": "string"
}
```

**Response**: `200 OK`
```json
{
  "access_token": "string",
  "expires_in": 3600
}
```

#### POST /auth/logout
**Description**: Invalidate current session
**Authentication**: Required

**Response**: `200 OK`
```json
{
  "message": "Successfully logged out"
}
```

#### GET /auth/me
**Description**: Get current user information
**Authentication**: Required

**Response**: `200 OK`
```json
{
  "user_id": 123,
  "email": "user@company.com",
  "team_id": 456,
  "role": "admin",
  "team": {
    "team_id": 456,
    "name": "ABC Construction",
    "saas_plan": "Pro"
  },
  "last_login": "2025-08-16T10:30:00Z"
}
```

### 2. Tender Search & Discovery

#### GET /tenders/search
**Description**: Search and filter public tenders with ranking
**Authentication**: Required
**Rate Limiting**: Based on SaaS plan (Free: 3/week, Basic/Pro: Unlimited)

**Query Parameters**:
```
q: string (required) - Search keywords
province: string (optional) - Filter by province
deadline_from: date (optional) - Minimum deadline date
deadline_to: date (optional) - Maximum deadline date
buyer: string (optional) - Filter by buyer organization
budget_min: number (optional) - Minimum budget in ZAR
budget_max: number (optional) - Maximum budget in ZAR
page: integer (default: 1) - Page number
limit: integer (default: 20, max: 100) - Results per page
sort_by: string (default: "relevance") - Sort by: relevance, deadline, budget
```

**Response**: `200 OK`
```json
{
  "results": [
    {
      "tender_id": "ocds-za-2025-001234",
      "title": "Road Construction Services - N1 Highway",
      "description": "Tender for road construction and maintenance...",
      "deadline": "2025-12-31T23:59:59Z",
      "province": "Gauteng",
      "buyer": "South African National Roads Agency",
      "budget": 15000000.00,
      "currency": "ZAR",
      "relevance_score": 0.87,
      "summary": "120-word AI summary...", // Only for Basic/Pro plans
      "readiness_score": 78, // Only if user has company profile
      "source_url": "https://etenders.gov.za/tender/123456",
      "last_updated": "2025-08-15T14:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_results": 156,
    "total_pages": 8,
    "has_next": true,
    "has_previous": false
  },
  "filters_applied": {
    "province": "Gauteng",
    "budget_range": [1000000, 50000000]
  },
  "search_quota": {
    "used": 2,
    "remaining": 1,
    "resets_at": "2025-08-17T00:00:00Z"
  }
}
```

#### GET /tenders/{tender_id}
**Description**: Get detailed information about a specific tender
**Authentication**: Required

**Response**: `200 OK`
```json
{
  "tender_id": "ocds-za-2025-001234",
  "title": "Road Construction Services - N1 Highway",
  "description": "Full tender description...",
  "deadline": "2025-12-31T23:59:59Z",
  "province": "Gauteng",
  "buyer": "South African National Roads Agency",
  "budget": 15000000.00,
  "currency": "ZAR",
  "status": "active",
  "documents": [
    {
      "name": "tender_specification.pdf",
      "url": "https://etenders.gov.za/docs/123456.pdf",
      "size_bytes": 2048576
    }
  ],
  "requirements": {
    "cidb_level": "5",
    "bbbee_level": "4",
    "experience_years": 10,
    "certifications": ["ISO 9001", "OHSAS 18001"]
  },
  "summary": {
    "text": "120-word AI summary highlighting key points...",
    "key_points": [
      "Deadline: 31 December 2025",
      "Budget: ZAR 15,000,000",
      "Location: Gauteng Province",
      "CIDB Level 5 required"
    ],
    "generated_at": "2025-08-15T14:30:00Z"
  },
  "readiness_assessment": {
    "score": 78,
    "checklist": {
      "sector_match": {"matched": true, "score": 30},
      "certifications_match": {"matched": true, "score": 25},
      "coverage_match": {"matched": true, "score": 20},
      "experience_match": {"matched": false, "score": 3}
    },
    "recommendation": "Good match - consider applying. Ensure experience documentation is comprehensive."
  }
}
```

### 3. AI Document Processing

#### POST /ai/summary/extract
**Description**: Extract and summarize document content using AI
**Authentication**: Required
**SaaS Restriction**: Basic/Pro plans only

**Request Body** (multipart/form-data):
```
file: File (required) - PDF or ZIP file
language: string (optional, default: "auto") - Language hint for processing
```

**Response**: `200 OK`
```json
{
  "summary": {
    "text": "This tender seeks qualified contractors for road construction services along the N1 highway in Gauteng Province. The project involves resurfacing 50km of highway, with a total budget of ZAR 15 million. Deadline for submissions is December 31, 2025. Contractors must hold CIDB Level 5 certification and demonstrate 10+ years of highway construction experience.",
    "word_count": 47,
    "key_points": [
      "Project: Road construction and resurfacing",
      "Location: N1 Highway, Gauteng",
      "Budget: ZAR 15,000,000",
      "Deadline: 31 December 2025",
      "Requirements: CIDB Level 5, 10+ years experience"
    ],
    "metadata": {
      "model_used": "facebook/bart-large-cnn",
      "confidence_score": 0.89,
      "processing_time_ms": 2847,
      "language_detected": "en"
    }
  },
  "extracted_requirements": {
    "cidb_level": "5",
    "experience_years": 10,
    "certifications": ["CIDB Level 5"],
    "location": "Gauteng"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid file format or corrupted file
- `403 Forbidden`: Feature not available for current plan
- `413 Payload Too Large`: File exceeds size limit (50MB)
- `422 Unprocessable Entity`: Could not extract text from document

#### POST /ai/readiness/check
**Description**: Calculate tender readiness score against company profile
**Authentication**: Required
**SaaS Restriction**: Basic/Pro plans only

**Request Body**:
```json
{
  "tender_id": "ocds-za-2025-001234",
  "company_profile_id": 123 // Optional - uses team's default if not provided
}
```

**Response**: `200 OK`
```json
{
  "assessment": {
    "tender_id": "ocds-za-2025-001234",
    "company_profile_id": 123,
    "overall_score": 78,
    "max_possible_score": 100,
    "assessment_date": "2025-08-16T10:30:00Z",
    "checklist": {
      "sector_match": {
        "matched": true,
        "score": 30,
        "max_score": 30,
        "details": "Construction sector matches tender requirements",
        "tender_requirement": "Construction services",
        "company_capability": "General construction and civil engineering"
      },
      "certifications_match": {
        "matched": true,
        "score": 25,
        "max_score": 30,
        "details": "CIDB Level 4 meets minimum Level 3 requirement",
        "tender_requirement": "CIDB Level 3 minimum",
        "company_capability": "CIDB Level 4, B-BBEE Level 2"
      },
      "coverage_match": {
        "matched": true,
        "score": 20,
        "max_score": 20,
        "details": "Company operates in Gauteng Province",
        "tender_requirement": "Gauteng Province",
        "company_capability": ["Gauteng", "Mpumalanga", "Limpopo"]
      },
      "experience_match": {
        "matched": false,
        "score": 3,
        "max_score": 20,
        "details": "8 years experience vs 10 years required",
        "tender_requirement": "10+ years highway construction",
        "company_capability": "8 years general construction"
      }
    },
    "recommendation": {
      "status": "recommended_with_conditions",
      "message": "Good match overall. Consider partnering with more experienced contractor for experience requirements.",
      "action_items": [
        "Gather detailed documentation of highway-related projects",
        "Consider joint venture with experienced highway contractor",
        "Prepare comprehensive project portfolio"
      ],
      "confidence_level": "high"
    }
  }
}
```

### 4. Company Profile Management

#### GET /profile
**Description**: Get team's company profile
**Authentication**: Required

**Response**: `200 OK`
```json
{
  "profile_id": 123,
  "team_id": 456,
  "company_name": "ABC Construction (Pty) Ltd",
  "sector": "Construction & Engineering",
  "services": [
    "Road construction",
    "Building construction",
    "Civil engineering",
    "Project management"
  ],
  "certifications": {
    "cidb_level": "4",
    "bbbee_level": "2",
    "iso_certifications": ["ISO 9001:2015", "ISO 14001:2015"],
    "other_certifications": ["SACPCMP", "ECSA Professional"]
  },
  "coverage_provinces": ["Gauteng", "Mpumalanga", "Limpopo"],
  "experience": {
    "years_in_business": 8,
    "total_projects": 45,
    "total_contract_value": 125000000.00,
    "specializations": ["Highway construction", "Municipal infrastructure"]
  },
  "contact_info": {
    "email": "info@abcconstruction.co.za",
    "phone": "+27 11 123 4567",
    "website": "https://www.abcconstruction.co.za",
    "address": {
      "street": "123 Industrial Road",
      "city": "Johannesburg",
      "province": "Gauteng",
      "postal_code": "2000"
    }
  },
  "created_at": "2025-01-15T09:00:00Z",
  "updated_at": "2025-08-10T14:30:00Z"
}
```

#### PUT /profile
**Description**: Update team's company profile
**Authentication**: Required (Admin role)

**Request Body**:
```json
{
  "company_name": "ABC Construction (Pty) Ltd",
  "sector": "Construction & Engineering",
  "services": ["Road construction", "Building construction"],
  "certifications": {
    "cidb_level": "5",
    "bbbee_level": "2"
  },
  "coverage_provinces": ["Gauteng", "Mpumalanga"],
  "experience": {
    "years_in_business": 9,
    "total_projects": 52
  },
  "contact_info": {
    "email": "info@abcconstruction.co.za",
    "phone": "+27 11 123 4567"
  }
}
```

**Response**: `200 OK`
```json
{
  "message": "Profile updated successfully",
  "profile": { /* Updated profile object */ },
  "scores_recalculated": true,
  "affected_tenders": 23
}
```

### 5. Workspace & Tender Tracking

#### GET /workspace
**Description**: Get team's saved tenders with status tracking
**Authentication**: Required

**Query Parameters**:
```
status: string (optional) - Filter by status: Pending, Interested, Not_Eligible, Submitted
assigned_to: integer (optional) - Filter by assigned user ID
deadline_from: date (optional) - Tenders with deadlines after this date
sort_by: string (default: "updated_at") - Sort by: updated_at, deadline, score
limit: integer (default: 20) - Results per page
page: integer (default: 1) - Page number
```

**Response**: `200 OK`
```json
{
  "workspace_entries": [
    {
      "entry_id": 789,
      "tender": {
        "tender_id": "ocds-za-2025-001234",
        "title": "Road Construction Services - N1 Highway",
        "deadline": "2025-12-31T23:59:59Z",
        "budget": 15000000.00,
        "province": "Gauteng",
        "buyer": "SANRAL"
      },
      "status": "Interested",
      "priority": "High",
      "readiness_score": 78,
      "notes": "Good opportunity - matches our capabilities well",
      "assigned_to": {
        "user_id": 124,
        "email": "project.manager@abcconstruction.co.za",
        "name": "John Smith"
      },
      "tasks": [
        {
          "task_id": 1,
          "description": "Prepare technical proposal",
          "due_date": "2025-12-20T17:00:00Z",
          "completed": false
        }
      ],
      "created_at": "2025-08-15T10:00:00Z",
      "updated_at": "2025-08-16T09:30:00Z",
      "updated_by": {
        "user_id": 123,
        "email": "admin@abcconstruction.co.za"
      }
    }
  ],
  "summary": {
    "total_entries": 15,
    "by_status": {
      "Pending": 5,
      "Interested": 7,
      "Not_Eligible": 2,
      "Submitted": 1
    },
    "high_priority": 3,
    "upcoming_deadlines": 4
  },
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_pages": 1,
    "has_next": false
  }
}
```

#### POST /workspace/save
**Description**: Save a tender to workspace
**Authentication**: Required

**Request Body**:
```json
{
  "tender_id": "ocds-za-2025-001234",
  "status": "Interested",
  "priority": "High",
  "notes": "Excellent opportunity for highway construction",
  "assigned_to": 124
}
```

**Response**: `201 Created`
```json
{
  "entry_id": 789,
  "message": "Tender saved to workspace",
  "readiness_score": 78
}
```

#### PUT /workspace/{entry_id}
**Description**: Update workspace entry
**Authentication**: Required

**Request Body**:
```json
{
  "status": "Submitted",
  "notes": "Proposal submitted on time",
  "priority": "High"
}
```

**Response**: `200 OK`
```json
{
  "message": "Workspace entry updated",
  "entry": { /* Updated entry object */ }
}
```

#### DELETE /workspace/{entry_id}
**Description**: Remove tender from workspace
**Authentication**: Required

**Response**: `200 OK`
```json
{
  "message": "Tender removed from workspace"
}
```

### 6. Analytics & Reporting

#### GET /analytics/spend-by-buyer
**Description**: Get government spending analytics by buyer organization
**Authentication**: Required

**Query Parameters**:
```
period: string (default: "12months") - Time period: 1month, 3months, 6months, 12months, 2years
province: string (optional) - Filter by province
sector: string (optional) - Filter by sector
limit: integer (default: 20) - Number of buyers to return
```

**Response**: `200 OK`
```json
{
  "analytics": {
    "period": "12months", 
    "total_spend": 245000000000.00,
    "total_tenders": 15432,
    "average_tender_value": 15876543.21,
    "buyers": [
      {
        "buyer_name": "Department of Transport",
        "total_spend": 45000000000.00,
        "tender_count": 234,
        "average_tender_value": 192307692.31,
        "percentage_of_total": 18.37,
        "provinces": ["Gauteng", "Western Cape", "KwaZulu-Natal"],
        "top_sectors": ["Infrastructure", "Transportation", "Construction"]
      },
      {
        "buyer_name": "City of Cape Town",
        "total_spend": 12500000000.00,
        "tender_count": 567,
        "average_tender_value": 22045855.48,
        "percentage_of_total": 5.10,
        "provinces": ["Western Cape"],
        "top_sectors": ["Municipal Services", "Infrastructure", "Utilities"]
      }
    ],
    "trends": {
      "monthly_spend": [
        {"month": "2024-09", "spend": 20500000000.00, "tenders": 1234},
        {"month": "2024-10", "spend": 18750000000.00, "tenders": 1156},
        {"month": "2024-11", "spend": 22100000000.00, "tenders": 1389}
      ]
    },
    "generated_at": "2025-08-16T10:30:00Z",
    "cache_expires_at": "2025-08-17T10:30:00Z"
  }
}
```

#### GET /analytics/tender-trends
**Description**: Get tender publication and award trends
**Authentication**: Required

**Query Parameters**:
```
period: string (default: "6months") - Analysis period
group_by: string (default: "month") - Group by: week, month, quarter
province: string (optional) - Filter by province
sector: string (optional) - Filter by sector
```

**Response**: `200 OK`
```json
{
  "trends": {
    "period": "6months",
    "group_by": "month",
    "data_points": [
      {
        "period": "2025-03",
        "published_tenders": 1245,
        "total_value": 15600000000.00,
        "avg_tender_value": 12530120.48,
        "awarded_tenders": 987,
        "award_rate": 79.3,
        "top_sectors": ["Construction", "IT Services", "Professional Services"]
      },
      {
        "period": "2025-04", 
        "published_tenders": 1189,
        "total_value": 18200000000.00,
        "avg_tender_value": 15302774.19,
        "awarded_tenders": 945,
        "award_rate": 79.5,
        "top_sectors": ["Infrastructure", "Construction", "Healthcare"]
      }
    ],
    "insights": {
      "growth_rate": 12.5,
      "seasonal_patterns": "Higher activity in Q2 and Q4",
      "value_concentration": "60% of value in top 10% of tenders"
    }
  }
}
```

#### GET /analytics/team-performance
**Description**: Get team's tender application performance analytics
**Authentication**: Required

**Response**: `200 OK`
```json
{
  "performance": {
    "period": "12months",
    "applications": {
      "total_submitted": 23,
      "awarded": 8,
      "rejected": 12,
      "pending": 3,
      "success_rate": 34.8
    },
    "financial": {
      "total_applied_value": 125000000.00,
      "total_awarded_value": 45000000.00,
      "average_application_value": 5434782.61,
      "largest_award": 12500000.00
    },
    "trends": {
      "monthly_applications": [
        {"month": "2024-09", "submitted": 2, "awarded": 1},
        {"month": "2024-10", "submitted": 3, "awarded": 0},
        {"month": "2024-11", "submitted": 1, "awarded": 1}
      ]
    },
    "readiness_insights": {
      "average_readiness_score": 72.5,
      "score_vs_success_correlation": 0.78,
      "improvement_areas": [
        "CIDB certification level",
        "B-BBEE compliance documentation",
        "Reference project portfolio"
      ]
    }
  }
}
```

### 7. Report Generation (Pro Feature)

#### POST /reports/export
**Description**: Generate and export comprehensive tender reports
**Authentication**: Required
**SaaS Restriction**: Pro plan only

**Request Body**:
```json
{
  "report_type": "workspace_summary", // Options: workspace_summary, tender_analysis, team_performance
  "format": "pdf", // Options: pdf, excel
  "filters": {
    "status": ["Interested", "Submitted"],
    "date_range": {
      "from": "2025-07-01",
      "to": "2025-08-31"
    },
    "include_scores": true,
    "include_summaries": true
  },
  "delivery_method": "download" // Options: download, email
}
```

**Response**: `202 Accepted`
```json
{
  "report_id": "rpt_8f7d6e5c4b3a2910",
  "status": "processing",
  "estimated_completion": "2025-08-16T10:35:00Z",
  "download_url": null,
  "message": "Report generation started. You will receive an email when ready."
}
```

#### GET /reports/{report_id}/status
**Description**: Check report generation status
**Authentication**: Required

**Response**: `200 OK`
```json
{
  "report_id": "rpt_8f7d6e5c4b3a2910",
  "status": "completed", // Options: processing, completed, failed
  "progress": 100,
  "download_url": "https://api.tenderinsight.co.za/reports/download/rpt_8f7d6e5c4b3a2910",
  "expires_at": "2025-08-23T10:35:00Z",
  "file_size_bytes": 2048576,
  "generated_at": "2025-08-16T10:34:47Z"
}
```

#### GET /reports/download/{report_id}
**Description**: Download generated report
**Authentication**: Required

**Response**: `200 OK`
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="workspace_summary_2025-08-16.pdf"
Content-Length: 2048576

[Binary PDF content]
```

### 8. Team Management

#### GET /team
**Description**: Get team information and members
**Authentication**: Required

**Response**: `200 OK`
```json
{
  "team": {
    "team_id": 456,
    "name": "ABC Construction (Pty) Ltd",
    "saas_plan": "Pro",
    "created_at": "2025-01-15T09:00:00Z",
    "plan_expires_at": "2026-01-15T09:00:00Z",
    "features": {
      "max_users": -1, // -1 = unlimited
      "ai_features": true,
      "api_access": true,
      "export_reports": true,
      "monthly_searches": -1 // -1 = unlimited
    }
  },
  "members": [
    {
      "user_id": 123,
      "email": "admin@abcconstruction.co.za",
      "role": "admin",
      "name": "Jane Doe",
      "last_login": "2025-08-16T09:15:00Z",
      "status": "active"
    },
    {
      "user_id": 124,
      "email": "manager@abcconstruction.co.za", 
      "role": "member",
      "name": "John Smith",
      "last_login": "2025-08-15T16:30:00Z",
      "status": "active"
    }
  ],
  "usage_stats": {
    "current_month": {
      "searches_performed": 45,
      "ai_summaries_generated": 23,
      "reports_exported": 3
    },
    "plan_limits": {
      "searches_limit": -1,
      "ai_summaries_limit": -1,
      "reports_limit": -1
    }
  }
}
```

#### POST /team/invite
**Description**: Invite new team member
**Authentication**: Required (Admin role)

**Request Body**:
```json
{
  "email": "newuser@abcconstruction.co.za",
  "role": "member",
  "name": "Alice Johnson"
}
```

**Response**: `201 Created`
```json
{
  "invitation_id": "inv_9g8h7f6e5d4c3b2a",
  "message": "Invitation sent successfully",
  "expires_at": "2025-08-23T10:30:00Z"
}
```

#### PUT /team/members/{user_id}
**Description**: Update team member role or status
**Authentication**: Required (Admin role)

**Request Body**:
```json
{
  "role": "admin",
  "status": "active"
}
```

**Response**: `200 OK`
```json
{
  "message": "Member updated successfully",
  "user": { /* Updated user object */ }
}
```

## Error Handling

### Standard Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "request_id": "req_1234567890abcdef",
    "timestamp": "2025-08-16T10:30:00Z"
  }
}
```

### HTTP Status Codes

| Status Code | Description | Common Scenarios |
|-------------|-------------|------------------|
| `200 OK` | Request successful | Successful GET, PUT operations |
| `201 Created` | Resource created | Successful POST operations |
| `202 Accepted` | Request accepted for processing | Background job started |
| `400 Bad Request` | Invalid request format | Malformed JSON, invalid parameters |
| `401 Unauthorized` | Authentication required/failed | Missing or invalid JWT token |
| `403 Forbidden` | Access denied | Insufficient permissions, plan restrictions |
| `404 Not Found` | Resource not found | Invalid tender_id, user_id, etc. |
| `409 Conflict` | Resource conflict | Duplicate workspace entry |
| `413 Payload Too Large` | File too large | Document exceeds 50MB limit |
| `422 Unprocessable Entity` | Validation failed | Invalid field values |
| `429 Too Many Requests` | Rate limit exceeded | API rate limiting |
| `500 Internal Server Error` | Server error | Unexpected server issues |
| `503 Service Unavailable` | Service temporarily unavailable | Maintenance mode, AI service down |

### Error Codes Reference

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `AUTHENTICATION_REQUIRED` | JWT token missing | Include Authorization header |
| `INVALID_TOKEN` | JWT token expired/invalid | Refresh token or re-authenticate |
| `INSUFFICIENT_PERMISSIONS` | User lacks required role | Contact team admin |
| `PLAN_RESTRICTION` | Feature not available for current plan | Upgrade SaaS plan |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait for rate limit reset |
| `QUOTA_EXCEEDED` | Monthly quota reached | Wait for quota reset or upgrade plan |
| `VALIDATION_ERROR` | Request validation failed | Check request format and required fields |
| `RESOURCE_NOT_FOUND` | Requested resource doesn't exist | Verify resource ID |
| `DUPLICATE_RESOURCE` | Resource already exists | Use PUT to update existing resource |
| `AI_SERVICE_UNAVAILABLE` | AI processing service down | Retry later |
| `FILE_PROCESSING_ERROR` | Could not process uploaded file | Check file format and integrity |

## Rate Limiting

### Rate Limit Headers
All API responses include rate limiting headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1692180000
X-RateLimit-Window: 3600
```

### Rate Limits by Plan

| Plan | Searches/Week | AI Processing/Month | API Calls/Hour | File Uploads/Day |
|------|---------------|---------------------|----------------|------------------|
| Free | 3 | 0 | 100 | 5 |
| Basic | Unlimited | 100 | 1000 | 50 |
| Pro | Unlimited | Unlimited | 5000 | 200 |

## Webhooks (Pro Feature)

### Webhook Events
Pro plan users can configure webhooks for real-time notifications:

- `tender.new_match` - New tender matches company profile
- `tender.deadline_approaching` - Tender deadline within 7 days
- `workspace.status_changed` - Workspace entry status updated
- `report.generated` - Report generation completed

### Webhook Payload Example
```json
{
  "event": "tender.new_match",
  "timestamp": "2025-08-16T10:30:00Z",
  "team_id": 456,
  "data": {
    "tender_id": "ocds-za-2025-001234",
    "title": "Road Construction Services",
    "readiness_score": 85,
    "deadline": "2025-12-31T23:59:59Z"
  },
  "signature": "sha256=abc123..." // HMAC signature for verification
}
```

## SDK and Integration Examples

### Python SDK Example
```python
from tender_insight import TenderInsightClient

# Initialize client
client = TenderInsightClient(
    api_key="your_api_key",
    base_url="https://api.tenderinsight.co.za/api/v1"
)

# Search tenders
results = client.tenders.search(
    query="construction services",
    province="Gauteng",
    budget_min=1000000
)

# Process with AI
summary = client.ai.summarize_file("tender_document.pdf")

# Save to workspace
client.workspace.save_tender(
    tender_id=results[0].tender_id,
    status="Interested",
    notes="Great opportunity"
)
```

### JavaScript SDK Example
```javascript
import { TenderInsightAPI } from '@tenderinsight/sdk';

const api = new TenderInsightAPI({
  apiKey: 'your_api_key',
  baseURL: 'https://api.tenderinsight.co.za/api/v1'
});

// Search and filter tenders
const tenders = await api.tenders.search({
  query: 'IT services',
  province: 'Western Cape',
  deadlineFrom: '2025-09-01'
});

// Get readiness assessment
const assessment = await api.ai.checkReadiness({
  tenderId: tenders.results[0].tender_id
});

console.log(`Readiness score: ${assessment.overall_score}%`);
```

## API Versioning Strategy

### Version Header
```http
Accept: application/vnd.tenderinsight.v1+json
```

### Backward Compatibility
- API versions are supported for minimum 2 years
- Breaking changes require new version
- Deprecation notices provided 6 months in advance
- Legacy endpoints return deprecation headers

### Migration Guide
When upgrading API versions, refer to:
- Migration guide: `/docs/migration/v1-to-v2`
- Changelog: `/docs/changelog`
- Breaking changes: `/docs/breaking-changes`

This comprehensive API specification provides a complete reference for integrating with the Tender Insight Hub platform, covering all core functionality while maintaining security, scalability, and ease of use.
    "
