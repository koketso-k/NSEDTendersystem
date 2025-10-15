# REQUIREMENTS SPECIFICATION
## Tender Insight Hub - Refined Requirements Document

**Document Version:** 1.0  
**Date:** August 2025  
**Project:** NSED742-TIH  
**Course:** Software Engineering & Design (NSED742)  

---

## 📋 DOCUMENT OVERVIEW

### Purpose
This document provides a comprehensive specification of functional and non-functional requirements for the Tender Insight Hub platform, serving as the authoritative reference for development teams.

### Scope
This specification covers all system requirements derived from the original project brief, stakeholder analysis, and technical constraints for the semester project.

### Document Structure
- **Functional Requirements:** Core system capabilities and user stories
- **Non-Functional Requirements:** Performance, security, and technical constraints
- **API Requirements:** External interface specifications
- **SaaS Requirements:** Multi-tenant and subscription management
- **Integration Requirements:** Database and third-party system integration

---

## 🎯 FUNCTIONAL REQUIREMENTS

### FR1: User Authentication & Team Management

#### FR1.1 Team Registration
**As a** SME business owner  
**I want to** register my company as a team on the platform  
**So that** I can access tender analysis tools for my business  

**Acceptance Criteria:**
- System captures company name, industry sector, contact information
- Each team is assigned a unique team identifier
- Initial registrant becomes team administrator
- Team is automatically assigned to Free tier

**Priority:** Critical  
**Dependencies:** Database setup (PostgreSQL)

#### FR1.2 User Management
**As a** team administrator  
**I want to** invite and manage team members  
**So that** my team can collaborate on tender opportunities  

**Acceptance Criteria:**
- Administrators can invite users via email
- User roles include 'admin' and 'member'
- Team member count enforced by SaaS tier
- Users can view team member list and roles

**Priority:** High  
**Dependencies:** FR1.1, Authentication system

#### FR1.3 Authentication System
**As a** system user  
**I want to** securely log in and access my team's data  
**So that** my company information remains protected  

**Acceptance Criteria:**
- JWT token-based authentication
- Secure password hashing (bcrypt or similar)
- Session management with appropriate timeouts
- Multi-tenant data isolation enforcement

**Priority:** Critical  
**Dependencies:** Database implementation

### FR2: Tender Search & Discovery

#### FR2.1 Keyword Search
**As a** SME user  
**I want to** search for tenders using free-text keywords  
**So that** I can find relevant procurement opportunities  

**Acceptance Criteria:**
- Search input accepts natural language queries
- Search performed against tender descriptions from OCDS API
- Results returned within 2 seconds for typical queries
- Search history tracked for analytics

**Priority:** Critical  
**Dependencies:** OCDS API integration, Database implementation

#### FR2.2 Advanced Filtering
**As a** user reviewing search results  
**I want to** apply filters to narrow down tender opportunities  
**So that** I can focus on the most relevant options  

**Acceptance Criteria:**
- Filter by province (dropdown selection)
- Filter by submission deadline (date range picker)
- Filter by buyer organization (searchable list)
- Filter by budget range (numeric range slider)
- Filters applied client-side after initial search
- Filter state preserved during session

**Priority:** High  
**Dependencies:** FR2.1, Frontend implementation

#### FR2.3 Results Display & Ranking
**As a** user viewing search results  
**I want to** see tenders ranked by relevance and match score  
**So that** I can prioritize my review effort  

**Acceptance Criteria:**
- Results displayed in paginated list format
- Each result shows title, deadline, buyer, budget summary
- Match scores displayed when available (Basic+ tiers)
- Results dynamically re-ranked when filters applied
- Export functionality for Pro tier users

**Priority:** High  
**Dependencies:** FR2.1, FR4 (Readiness Scoring)

### FR3: Company Profile Management

#### FR3.1 Profile Creation
**As a** team administrator  
**I want to** create a comprehensive company profile  
**So that** the system can accurately assess our tender readiness  

**Acceptance Criteria:**
- Profile includes industry sector (required)
- Services provided (multi-select with custom options)
- Certifications (CIDB level, BBBEE rating, others)
- Geographic coverage (province multi-select)
- Years of experience (numeric input)
- Contact information (address, phone, email)

**Priority:** Critical  
**Dependencies:** FR1.1, Database schema

#### FR3.2 Profile Updates
**As a** team member with appropriate permissions  
**I want to** update our company profile information  
**So that** match scoring reflects our current capabilities  

**Acceptance Criteria:**
- Profile editable by administrators and designated members
- Changes trigger recalculation of existing readiness scores
- Profile change history maintained for audit purposes
- Validation prevents incomplete or invalid data entry

**Priority:** High  
**Dependencies:** FR3.1, FR4 (Readiness Scoring)

### FR4: AI-Powered Document Analysis

#### FR4.1 Document Extraction
**As a** system processing tender documents  
**I want to** extract text from PDF and ZIP attachments  
**So that** AI analysis can be performed on tender content  

**Acceptance Criteria:**
- Support for PDF text extraction using appropriate libraries
- Support for ZIP file extraction and processing
- Handle multiple documents within ZIP archives
- Error handling for corrupted or protected files
- Text extraction limited to reasonable file sizes (10MB max)

**Priority:** Critical  
**Dependencies:** Document processing libraries, Storage system

#### FR4.2 AI Summarization
**As a** user viewing a tender opportunity  
**I want to** see an AI-generated summary of tender documents  
**So that** I can quickly understand requirements without reading full documents  

**Acceptance Criteria:**
- Generate 120-word summaries using open-source NLP models
- Summaries emphasize objective, scope, deadline, eligibility criteria
- Model selection from HuggingFace or similar platforms
- Summary quality validation (manual spot-checking during development)
- Summaries stored in MongoDB for performance

**Priority:** High  
**Dependencies:** FR4.1, MongoDB setup, AI model integration

### FR5: Readiness Scoring & Suitability Analysis

#### FR5.1 Automated Scoring
**As a** user interested in a specific tender  
**I want to** see how well my company matches the tender requirements  
**So that** I can make informed decisions about applying  

**Acceptance Criteria:**
- Generate suitability score from 0-100
- Compare tender requirements against company profile
- Consider sector alignment, certification requirements, geographic coverage
- Account for experience level and capacity indicators
- Scores updated when profile changes

**Priority:** High  
**Dependencies:** FR3.1, FR4.2, MongoDB implementation

#### FR5.2 Detailed Match Analysis
**As a** user reviewing a tender match  
**I want to** see a detailed breakdown of matched and unmatched criteria  
**So that** I understand what qualifications I meet or lack  

**Acceptance Criteria:**
- Checklist format showing "Has required CIDB: YES/NO"
- Geographic coverage match indicator
- Sector alignment assessment
- Experience requirement comparison
- Short recommendation text (e.g., "Suitable - low competition expected")
- Clear identification of missing qualifications

**Priority:** High  
**Dependencies:** FR5.1

### FR6: Workspace & Collaboration

#### FR6.1 Tender Workspace
**As a** team member  
**I want to** save interesting tenders to our team workspace  
**So that** we can track and collaborate on opportunities  

**Acceptance Criteria:**
- Save/unsave tenders with single click action
- Workspace shows all saved tenders for the team
- Display tender title, deadline, AI summary, match score
- Persistent storage in PostgreSQL
- Access control by team membership

**Priority:** High  
**Dependencies:** FR1.1, Database implementation

#### FR6.2 Status Tracking
**As a** team member managing our tender pipeline  
**I want to** categorize tenders by their current status  
**So that** we can track our application progress  

**Acceptance Criteria:**
- Status categories: "Pending Review", "Interested", "Not Eligible", "Submitted"
- Team members can update tender status
- Status changes logged with timestamp and user identification
- Status-based filtering in workspace view
- Visual indicators for different statuses

**Priority:** Medium  
**Dependencies:** FR6.1

#### FR6.3 Team Collaboration
**As a** team member working on tender opportunities  
**I want to** leave notes and assign tasks to colleagues  
**So that** we can coordinate our tender response efforts  

**Acceptance Criteria:**
- Internal notes attached to workspace tender entries
- Task assignment functionality
- @mention notifications for team members
- Note editing and deletion capabilities
- Activity timeline showing all team interactions

**Priority:** Medium  
**Dependencies:** FR6.1, FR1.2

---

## 🚀 NON-FUNCTIONAL REQUIREMENTS

### NFR1: Performance Requirements

#### NFR1.1 Response Time
- Search queries return results within 2 seconds
- Page load times under 3 seconds on standard broadband
- AI summarization completes within 30 seconds per document
- Database queries optimized with appropriate indexing

#### NFR1.2 Throughput
- System supports 100 concurrent users during testing
- API endpoints handle 1000 requests per hour
- Background jobs process 50 documents per hour

#### NFR1.3 Scalability
- Horizontal scaling capability through containerization
- Database sharding considerations for multi-tenant architecture
- Redis caching reduces database load by 60%

### NFR2: Security Requirements

#### NFR2.1 Authentication & Authorization
- JWT tokens with 24-hour expiration
- Password complexity requirements enforced
- Multi-tenant data isolation (100% separation)
- API rate limiting to prevent abuse

#### NFR2.2 Data Protection
- HTTPS encryption for all communications
- Database connections encrypted
- Sensitive data hashing (passwords, tokens)
- Regular security dependency updates

### NFR3: Reliability & Availability

#### NFR3.1 Uptime
- Target 99.5% uptime during development testing
- Graceful degradation when external APIs unavailable
- Database backup and recovery procedures

#### NFR3.2 Error Handling
- Comprehensive error logging
- User-friendly error messages
- Fallback mechanisms for AI processing failures

### NFR4: Usability Requirements

#### NFR4.1 User Interface
- Responsive design supporting mobile and desktop
- Intuitive navigation requiring minimal training
- Accessibility compliance (basic WCAG guidelines)
- Consistent visual design language

#### NFR4.2 User Experience
- Progressive loading for large datasets
- Clear feedback for user actions
- Contextual help and documentation

---

## 🔌 API REQUIREMENTS

### AR1: Public API Endpoints

#### AR1.1 GET /api/enriched-releases
**Purpose:** Retrieve filtered tender data with metadata and AI summaries

**Parameters:**
- `province` (optional): Filter by province code
- `buyer` (optional): Filter by buyer organization
- `deadline_after` (optional): ISO date string
- `limit` (optional): Max results (default 20, max 100)

**Response Format:**
```json
{
  "releases": [
    {
      "tender_id": "ocds-123-abc",
      "title": "Road Construction Project",
      "deadline": "2023-12-31T23:59:59Z",
      "buyer": "Department of Transport",
      "budget": 1200000,
      "ai_summary": "This tender seeks...",
      "suitability_score": 85
    }
  ],
  "pagination": {
    "page": 1,
    "total_pages": 5,
    "total_results": 89
  }
}
```

#### AR1.2 GET /api/analytics/spend-by-buyer
**Purpose:** Provide aggregated government spending data

**Response Format:**
```json
{
  "analytics": [
    {
      "buyer": "Department of Transport",
      "total_budget": 15600000,
      "tender_count": 23,
      "avg_budget": 678260
    }
  ],
  "generated_at": "2023-11-15T10:30:00Z"
}
```

#### AR1.3 POST /api/summary/extract
**Purpose:** Extract and summarize document content

**Request Format:**
- Multipart form data with PDF or DOCX file
- Max file size: 10MB

**Response Format:**
```json
{
  "summary": "This document outlines requirements for...",
  "key_points": [
    "Deadline: 2023-12-31",
    "Budget: ZAR 1.2M",
    "Location: Western Cape"
  ],
  "word_count": 120,
  "processing_time_ms": 2500
}
```

#### AR1.4 POST /api/readiness/check
**Purpose:** Calculate company suitability for specific tender

**Request Format:**
```json
{
  "tender_id": "ocds-123-abc",
  "company_profile": {
    "sector": "Construction",
    "cidb_level": "5",
    "provinces": ["WC", "EC"],
    "experience_years": 8
  }
}
```

**Response Format:**
```json
{
  "suitability_score": 85,
  "checklist": {
    "sector_match": true,
    "certification_match": true,
    "geographic_match": true,
    "experience_match": true
  },
  "recommendation": "Suitable - low competition expected",
  "missing_requirements": []
}
```

---

## 💼 SAAS REQUIREMENTS

### SR1: Multi-Tenant Architecture

#### SR1.1 Data Isolation
- Row-level security in PostgreSQL using team_id
- Document-level isolation in MongoDB
- Redis key namespacing by team identifier
- API layer enforcement through JWT team claims

#### SR1.2 Subscription Management
- Automated feature restriction based on plan tier
- Real-time usage tracking for quota enforcement
- Plan upgrade/downgrade workflow (simulated)

### SR2: Tier-Specific Features

#### SR2.1 Free Tier (1 user, 3 searches/week)
- Basic search functionality
- Limited tender viewing
- No AI summarization access
- No readiness scoring
- No export capabilities

#### SR2.2 Basic Tier (3 users, unlimited searches)
- Full search and filtering
- AI summarization enabled
- Readiness scoring available
- Team collaboration features
- Standard workspace functionality

#### SR2.3 Pro Tier (unlimited users, all features)
- All Basic tier features
- Advanced analytics dashboard
- Data export capabilities (CSV, PDF)
- Priority AI processing
- Extended API access

---

## 🔗 INTEGRATION REQUIREMENTS

### IR1: External API Integration

#### IR1.1 OCDS eTenders API
- Real-time tender data synchronization
- Error handling for API unavailability
- Data transformation and normalization
- Incremental updates to avoid duplicate processing

#### IR1.2 AI Model Integration
- HuggingFace model integration for summarization
- Model performance monitoring
- Fallback summarization methods
- Batch processing capabilities for efficiency

### IR2: Database Integration

#### IR2.1 Multi-Database Architecture
- PostgreSQL for ACID-compliant transactional data
- MongoDB for flexible document storage
- Redis for high-performance caching
- Data synchronization between systems
- Consistent backup and recovery procedures

#### IR2.2 Performance Optimization
- Database indexing strategy
- Query optimization guidelines
- Caching layer implementation
- Background job processing with Celery

---

## ✅ ACCEPTANCE CRITERIA

### System-Wide Acceptance Criteria
1. All functional requirements implemented and tested
2. Non-functional requirements verified through testing
3. API endpoints documented and functional
4. Multi-tenant data isolation verified
5. SaaS tier restrictions properly enforced
6. Performance benchmarks achieved
7. Security requirements validated
8. Documentation completed and accurate

### Quality Gates
- **Code Coverage:** Minimum 85% test coverage
- **Performance:** All endpoints respond within SLA times
- **Security:** No high-severity vulnerabilities detected
- **Usability:** User acceptance testing completed successfully

---

## 📈 CHANGE MANAGEMENT

### Requirements Change Process
1. Change request submitted to current Team Lead
2. Impact assessment conducted
3. Team consensus required for approval
4. Documentation updated accordingly
5. Stakeholders notified of changes

### Version Control
- Requirements document version controlled in Git
- Change log maintained in document header
- Regular reviews scheduled with team leads

---

**Document Control:**
- **Version:** 1.0
- **Last Updated:** 10 August 2025
- **Next Review:** [10 August + 2 weeks]
- **Approved By:** S Mthembu
- **Distribution:** All team members, course instructor
