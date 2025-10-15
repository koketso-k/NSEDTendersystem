# Tender Insight Hub - System Architecture

## Project Overview

Tender Insight Hub is a **cloud-native SaaS platform** designed to empower South African SMEs by simplifying public tender discovery, document summarization, and application readiness assessment. The system leverages AI-powered summarization and multi-database architecture to deliver scalable, efficient tender management services.

### Key Requirements
- **Backend**: FastAPI (Python)
- **Databases**: PostgreSQL (SQL) + MongoDB (NoSQL) + Redis (Caching)
- **Architecture**: Multi-tenant SaaS with seat-based pricing
- **AI Integration**: Open-source summarization models
- **API**: Public REST API with Swagger documentation

## System Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │  Mobile Apps    │    │  Third-party    │
│   (React/Vue)   │    │                 │    │  Integrations   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │     Load Balancer         │
                    │    (nginx/CloudFlare)     │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │     FastAPI Backend       │
                    │   (Authentication &       │
                    │    Business Logic)        │
                    └─────────────┬─────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                       │                        │
┌───────┴────────┐    ┌─────────┴────────┐    ┌─────────┴────────┐
│   PostgreSQL   │    │     MongoDB      │    │      Redis       │
│ (Structured    │    │  (Documents &    │    │   (Caching &     │
│  Relational)   │    │   AI Results)    │    │   Sessions)      │
└────────────────┘    └──────────────────┘    └──────────────────┘
        │                       │                        │
        └───────────────────────┼────────────────────────┘
                               │
                    ┌──────────┴───────────┐
                    │   Background Jobs    │
                    │   (Celery Workers)   │
                    │                      │
                    │ • AI Summarization   │
                    │ • Score Calculation  │
                    │ • Analytics Refresh  │
                    └──────────────────────┘
```

## Core Components

### 1. FastAPI Backend
**Technology**: FastAPI (Python 3.9+)
**Responsibilities**:
- RESTful API endpoints
- JWT-based authentication
- Multi-tenant access control
- Request validation (Pydantic)
- Rate limiting and security middleware

### 2. Multi-Database Architecture

#### PostgreSQL (Primary SQL Database)
**Role**: Source of truth for structured, transactional data
**Data**: Users, Teams, Company Profiles, Tender Metadata, Workspace Entries
**Why**: ACID compliance, complex queries, data integrity

#### MongoDB (NoSQL Document Store)
**Role**: Flexible document storage for AI results and logs
**Data**: AI Summaries, Readiness Scores, Activity Logs, Analytics Cache
**Why**: Schema flexibility, high write throughput, document-oriented data

#### Redis (In-Memory Cache)
**Role**: High-speed caching and session management
**Data**: Search results, Rate limiting counters, Session data, Temporary locks
**Why**: Sub-millisecond access, TTL support, atomic operations

### 3. AI Pipeline
**Models**: HuggingFace Transformers (bart-large-cnn, t5-small)
**Processing**:
1. PDF text extraction (pdfplumber, PyPDF2)
2. Text preprocessing
3. AI summarization (120-word summaries)
4. Post-processing and storage

### 4. Background Job System
**Technology**: Celery with Redis broker
**Jobs**:
- AI document summarization
- Readiness score recalculation
- Analytics data pre-computation
- Notification processing

## Multi-Tenant Architecture

### Tenant Isolation Strategy
- **PostgreSQL**: Row-level security with team_id filtering
- **MongoDB**: Document-level isolation with team_id embedding
- **Redis**: Key namespacing with "team:{id}:" prefixes
- **API Layer**: JWT-based team_id injection in all queries

### SaaS Pricing Tiers

| Feature | Free | Basic | Pro |
|---------|------|-------|-----|
| Users per team | 1 | 3 | Unlimited |
| Searches per week | 3 | Unlimited | Unlimited |
| AI Features | ❌ | ✅ | ✅ |
| Report Export | ❌ | ❌ | ✅ |
| API Access | Limited | Full | Full |

## Security Architecture

### Authentication & Authorization
- **JWT Tokens**: Stateless authentication with refresh mechanism
- **Role-Based Access**: Admin/Member roles per team
- **API Security**: Rate limiting, CORS policies, input validation
- **Data Protection**: Password hashing, SQL injection prevention

### Security Middleware Stack
```python
# FastAPI Security Middleware
- CORS Middleware
- Rate Limiting (slowapi)
- JWT Authentication
- Pydantic Validation
- Team-based Authorization
- Error Sanitization
```

## API Architecture

### Public API Endpoints

#### GET Endpoints
- `GET /api/enriched-releases` - Filtered tenders with AI summaries
- `GET /api/analytics/spend-by-buyer` - Government spending analytics
- `GET /api/workspace` - User's saved tenders
- `GET /api/profile` - Company profile information

#### POST Endpoints
- `POST /api/summary/extract` - Document summarization
- `POST /api/readiness/check` - Tender suitability scoring
- `POST /api/auth/login` - User authentication
- `POST /api/reports/export` - PDF report generation (Pro only)

### API Documentation
- **Swagger/OpenAPI**: Auto-generated interactive documentation
- **Rate Limiting**: Per-tier request limits
- **Versioning**: URL-based versioning (/api/v1/)

## Data Flow Architecture

### Search & Discovery Flow
1. User inputs keywords → FastAPI
2. Query OCDS eTenders API → Cache in Redis
3. Apply filters (Province, Deadline, Budget)
4. Rank by relevance (TF-IDF/cosine similarity)
5. Return paginated results

### AI Processing Flow
1. Document upload → FastAPI
2. Text extraction → Background job (Celery)
3. AI summarization → Store in MongoDB
4. Readiness scoring → Compare with profile
5. Results cached in Redis

### Analytics Pipeline
1. Nightly aggregation job → PostgreSQL data
2. Compute spend-by-buyer metrics
3. Cache results in Redis (24h TTL)
4. Serve via API to frontend charts

## Scalability Considerations

### Horizontal Scaling
- **API Servers**: Multiple FastAPI instances behind load balancer
- **Database Sharding**: MongoDB horizontal partitioning by team_id
- **Cache Distribution**: Redis Cluster for distributed caching
- **Background Jobs**: Multiple Celery workers

### Performance Optimizations
- **Database Indexing**: Strategic indexes on query patterns
- **Connection Pooling**: SQLAlchemy + asyncpg for PostgreSQL
- **Caching Strategy**: Multi-level caching (Redis → MongoDB → PostgreSQL)
- **CDN Integration**: Static asset delivery via CloudFlare

## Monitoring & Observability

### Health Monitoring
- **Database Health**: Connection pools, query performance
- **API Performance**: Response times, error rates
- **Background Jobs**: Queue lengths, processing times
- **Cache Hit Rates**: Redis performance metrics

### Logging Strategy
- **Structured Logging**: JSON format with correlation IDs
- **User Activity**: MongoDB capped collections
- **Error Tracking**: Exception monitoring and alerting
- **Audit Trail**: Multi-tenant action logging

## Deployment Architecture

### Cloud-Native Deployment
- **Containerization**: Docker containers for all services
- **Orchestration**: Kubernetes or Docker Compose
- **Database Services**: Managed cloud databases (AWS RDS, MongoDB Atlas)
- **Caching**: Redis Cloud or ElastiCache

### CI/CD Pipeline
- **Version Control**: Git with feature branches
- **Testing**: Automated unit/integration tests
- **Deployment**: Blue-green deployments
- **Monitoring**: Real-time health checks and rollback capabilities
