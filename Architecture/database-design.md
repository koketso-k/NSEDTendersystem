# Tender Insight Hub - Database Design

## Database Architecture Overview

The Tender Insight Hub utilizes a **multi-database architecture** combining PostgreSQL (SQL), MongoDB (NoSQL), and Redis (caching) to optimize performance, scalability, and data consistency across different use cases.

### Database Selection Rationale

| Database | Purpose | Use Cases | Key Benefits |
|----------|---------|-----------|--------------|
| **PostgreSQL** | Source of truth for structured data | Users, Teams, Profiles, Tender metadata | ACID compliance, complex queries, data integrity |
| **MongoDB** | Flexible document storage | AI summaries, scores, logs, analytics | Schema flexibility, high write throughput, nested data |
| **Redis** | High-speed caching | Search results, sessions, rate limiting | In-memory performance, TTL support, atomic operations |

## PostgreSQL Schema Design

### Core Tables

#### 1. Teams Table
```sql
CREATE TABLE teams (
    team_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    saas_plan VARCHAR(20) CHECK (saas_plan IN ('Free', 'Basic', 'Pro')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_teams_saas_plan ON teams(saas_plan);
```

#### 2. Users Table
```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    team_id INTEGER REFERENCES teams(team_id) ON DELETE CASCADE,
    role VARCHAR(10) CHECK (role IN ('admin', 'member')),
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_users_team_id ON users(team_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
```

#### 3. Company Profiles Table
```sql
CREATE TABLE company_profiles (
    profile_id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(team_id) ON DELETE CASCADE,
    company_name VARCHAR(200) NOT NULL,
    sector VARCHAR(100) NOT NULL,
    services TEXT[], -- Array of service types
    cidb_level VARCHAR(10), -- CIDB contractor grading
    bbbee_level VARCHAR(5), -- B-BBEE level (1-8)
    coverage_provinces VARCHAR(100)[], -- Array of provinces
    experience_years INTEGER CHECK (experience_years >= 0),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    website_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_company_profiles_team_id ON company_profiles(team_id);
CREATE INDEX idx_company_profiles_sector ON company_profiles(sector);
CREATE INDEX idx_company_profiles_cidb ON company_profiles(cidb_level) WHERE cidb_level IS NOT NULL;
```

#### 4. Tenders Table
```sql
CREATE TABLE tenders (
    tender_id VARCHAR(50) PRIMARY KEY, -- From OCDS API (e.g., "ocds-123456")
    title TEXT NOT NULL,
    description TEXT,
    deadline TIMESTAMP,
    province VARCHAR(50),
    buyer VARCHAR(100), -- Organ of state
    budget NUMERIC(15,2), -- Budget in ZAR
    currency VARCHAR(3) DEFAULT 'ZAR',
    status VARCHAR(20) DEFAULT 'active',
    source_url VARCHAR(500),
    raw_json JSONB, -- Original OCDS API response
    created_at TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_tenders_deadline ON tenders(deadline) WHERE deadline > NOW();
CREATE INDEX idx_tenders_province ON tenders(province);
CREATE INDEX idx_tenders_buyer ON tenders(buyer);
CREATE INDEX idx_tenders_budget ON tenders(budget);
CREATE INDEX idx_tenders_status ON tenders(status);
-- Full-text search on title and description
CREATE INDEX idx_tenders_search ON tenders USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')));
```

#### 5. Workspace Entries Table
```sql
CREATE TABLE workspace_entries (
    entry_id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(team_id) ON DELETE CASCADE,
    tender_id VARCHAR(50) REFERENCES tenders(tender_id) ON DELETE CASCADE,
    status VARCHAR(20) CHECK (status IN ('Pending', 'Interested', 'Not Eligible', 'Submitted')) DEFAULT 'Pending',
    notes TEXT,
    assigned_to INTEGER REFERENCES users(user_id),
    priority VARCHAR(10) CHECK (priority IN ('Low', 'Medium', 'High')) DEFAULT 'Medium',
    updated_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_workspace_team_status ON workspace_entries(team_id, status);
CREATE INDEX idx_workspace_tender_id ON workspace_entries(tender_id);
CREATE INDEX idx_workspace_assigned_to ON workspace_entries(assigned_to) WHERE assigned_to IS NOT NULL;

-- Composite unique constraint to prevent duplicate entries
CREATE UNIQUE INDEX idx_workspace_unique ON workspace_entries(team_id, tender_id);
```

### Row-Level Security (RLS)

```sql
-- Enable RLS on workspace_entries
ALTER TABLE workspace_entries ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their team's data
CREATE POLICY team_access_policy ON workspace_entries
    USING (team_id = current_setting('app.current_team_id')::INT);

-- Similar policies for other team-specific tables
ALTER TABLE company_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY team_profile_policy ON company_profiles
    USING (team_id = current_setting('app.current_team_id')::INT);
```

## MongoDB Collections Design

### 1. Tender Summaries Collection
```javascript
// Collection: tender_summaries
db.createCollection("tender_summaries", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["tender_id", "summary", "model_used"],
            properties: {
                tender_id: { bsonType: "string" },
                summary: { 
                    bsonType: "string",
                    maxLength: 500 // ~120 words max
                },
                key_points: {
                    bsonType: "array",
                    items: { bsonType: "string" },
                    description: "Key deadline, budget, eligibility points"
                },
                model_used: { 
                    bsonType: "string",
                    enum: ["facebook/bart-large-cnn", "t5-small", "t5-base"]
                },
                processing_time_ms: { bsonType: "int" },
                confidence_score: { 
                    bsonType: "double",
                    minimum: 0.0,
                    maximum: 1.0
                },
                language_detected: { bsonType: "string" },
                created_at: { bsonType: "date" },
                last_updated: { bsonType: "date" }
            }
        }
    }
});

// Indexes
db.tender_summaries.createIndex({ "tender_id": 1 }, { unique: true });
db.tender_summaries.createIndex({ "last_updated": -1 });
db.tender_summaries.createIndex({ "model_used": 1, "created_at": -1 });
```

### 2. Readiness Scores Collection
```javascript
// Collection: readiness_scores
db.createCollection("readiness_scores", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["tender_id", "team_id", "score", "checklist"],
            properties: {
                tender_id: { bsonType: "string" },
                team_id: { bsonType: "int" },
                score: { 
                    bsonType: "int",
                    minimum: 0,
                    maximum: 100
                },
                checklist: {
                    bsonType: "object",
                    required: ["sector_match", "certifications_match", "coverage_match", "experience_match"],
                    properties: {
                        sector_match: { 
                            bsonType: "object",
                            properties: {
                                matched: { bsonType: "bool" },
                                score: { bsonType: "int" },
                                details: { bsonType: "string" }
                            }
                        },
                        certifications_match: {
                            bsonType: "object",
                            properties: {
                                cidb_required: { bsonType: "string" },
                                cidb_company: { bsonType: "string" },
                                bbbee_required: { bsonType: "string" },
                                bbbee_company: { bsonType: "string" },
                                matched: { bsonType: "bool" },
                                score: { bsonType: "int" }
                            }
                        },
                        coverage_match: {
                            bsonType: "object",
                            properties: {
                                tender_province: { bsonType: "string" },
                                company_provinces: { 
                                    bsonType: "array",
                                    items: { bsonType: "string" }
                                },
                                matched: { bsonType: "bool" },
                                score: { bsonType: "int" }
                            }
                        },
                        experience_match: {
                            bsonType: "object",
                            properties: {
                                required_years": { bsonType: "int" },
                                company_years: { bsonType: "int" },
                                matched: { bsonType: "bool" },
                                score: { bsonType: "int" }
                            }
                        }
                    }
                },
                recommendation: { bsonType: "string" },
                algorithm_version: { bsonType: "string" },
                generated_at: { bsonType: "date" }
            }
        }
    }
});

// Indexes
db.readiness_scores.createIndex({ "team_id": 1, "tender_id": 1 }, { unique: true });
db.readiness_scores.createIndex({ "team_id": 1, "score": -1 });
db.readiness_scores.createIndex({ "generated_at": -1 });
```

### 3. User Activity Logs Collection
```javascript
// Collection: user_activity_logs (Capped for automatic rotation)
db.createCollection("user_activity_logs", {
    capped: true,
    size: 50000000, // 50MB max
    max: 100000, // 100k documents max
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["user_id", "team_id", "action", "timestamp"],
            properties: {
                user_id: { bsonType: "int" },
                team_id: { bsonType: "int" },
                action: { 
                    bsonType: "string",
                    enum: ["search", "filter", "save_tender", "status_update", "profile_update", "login", "export"]
                },
                metadata: {
                    bsonType: "object",
                    description: "Action-specific data like search terms, filters applied"
                },
                ip_address: { bsonType: "string" },
                user_agent: { bsonType: "string" },
                timestamp: { bsonType: "date" }
            }
        }
    }
});

// Indexes (limited for capped collections)
db.user_activity_logs.createIndex({ "user_id": 1, "timestamp": -1 });
db.user_activity_logs.createIndex({ "team_id": 1, "action": 1, "timestamp": -1 });
```

### 4. Cached Analytics Collection
```javascript
// Collection: cached_analytics
db.createCollection("cached_analytics", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["analytics_type", "data", "generated_at", "expires_at"],
            properties: {
                analytics_type: {
                    bsonType: "string",
                    enum: ["spend_by_buyer", "tenders_by_province", "monthly_trends", "sector_analysis"]
                },
                data: { bsonType: "object" },
                filters_applied: { bsonType: "object" },
                generated_at: { bsonType: "date" },
                expires_at: { bsonType: "date" },
                generation_time_ms: { bsonType: "int" }
            }
        }
    }
});

// TTL Index for automatic expiry
db.cached_analytics.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 });
db.cached_analytics.createIndex({ "analytics_type": 1, "generated_at": -1 });
```

## Redis Cache Design

### Key Patterns and Data Types

```python
# Cache key patterns with TTL
CACHE_PATTERNS = {
    # Tender metadata cache (6 hours)
    "tender:{tender_id}:metadata": {
        "type": "hash",
        "ttl": 21600,  # 6 hours
        "fields": ["title", "deadline", "buyer", "province", "budget"]
    },
    
    # Search results cache (1 hour)
    "search:{query_hash}:results": {
        "type": "list",
        "ttl": 3600,  # 1 hour
        "description": "Paginated search results with tender IDs"
    },
    
    # Team search quota (resets daily at midnight)
    "team:{team_id}:search_quota": {
        "type": "string",
        "ttl": "midnight_reset",
        "description": "Remaining searches for Free tier teams"
    },
    
    # Pre-computed analytics (24 hours)
    "analytics:spend_by_buyer": {
        "type": "zset",
        "ttl": 86400,  # 24 hours
        "description": "Sorted set of buyers by total spend"
    },
    
    # Processing locks (10 minutes)
    "lock:summary:{tender_id}": {
        "type": "string",
        "ttl": 600,  # 10 minutes
        "description": "Prevent duplicate AI processing"
    },
    
    # User session cache (30 minutes)
    "session:{user_id}:data": {
        "type": "hash",
        "ttl": 1800,  # 30 minutes
        "fields": ["team_id", "role", "last_activity"]
    }
}
```

### Redis Usage Examples

```python
# Search quota management
async def check_search_quota(team_id: int, saas_plan: str) -> bool:
    if saas_plan != "Free":
        return True
    
    key = f"team:{team_id}:search_quota"
    current_count = await redis.get(key) or 0
    
    if int(current_count) >= 3:  # Free tier limit
        return False
    
    # Increment and set midnight expiry if first search today
    if current_count == 0:
        midnight = get_next_midnight_timestamp()
        await redis.setex(key, midnight - time.time(), 1)
    else:
        await redis.incr(key)
    
    return True

# Analytics caching
async def cache_spend_analytics():
    # Compute from PostgreSQL
    spend_data = await db.execute("""
        SELECT buyer, SUM(budget) as total_spend
        FROM tenders 
        WHERE deadline > NOW() - INTERVAL '1 year'
        GROUP BY buyer
        ORDER BY total_spend DESC
    """)
    
    # Cache as sorted set in Redis
    pipe = redis.pipeline()
    for buyer, spend in spend_data:
        pipe.zadd("analytics:spend_by_buyer", {buyer: spend})
    pipe.expire("analytics:spend_by_buyer", 86400)  # 24h TTL
    await pipe.execute()
```

## Multi-Tenant Data Isolation

### PostgreSQL: Row-Level Security
```sql
-- Function to get current team from JWT context
CREATE OR REPLACE FUNCTION get_current_team_id()
RETURNS INT AS $$
BEGIN
    RETURN COALESCE(current_setting('app.current_team_id', true)::INT, 0);
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- RLS policy for workspace_entries
CREATE POLICY workspace_team_isolation ON workspace_entries
    USING (team_id = get_current_team_id());
```

### MongoDB: Query-Level Filtering
```python
# Always include team_id in MongoDB queries
async def get_readiness_scores(team_id: int, min_score: int = 0):
    return await db.readiness_scores.find({
        "team_id": team_id,
        "score": {"$gte": min_score}
    }).to_list(length=None)

# Compound indexes for efficient tenant queries
db.readiness_scores.create_index([("team_id", 1), ("score", -1)])
```

### Redis: Namespace Isolation
```python
# Prefix all team-specific keys
def get_team_key(team_id: int, key_suffix: str) -> str:
    return f"team:{team_id}:{key_suffix}"

# Example usage
search_quota_key = get_team_key(123, "search_quota")
cached_results_key = get_team_key(123, f"search:{query_hash}")
```

## Data Synchronization Strategy

### Write Operations Flow

1. **PostgreSQL First**: All user actions write to PostgreSQL for ACID compliance
2. **Event Triggers**: Database triggers or application events initiate background jobs
3. **Async Processing**: Celery tasks handle derived data updates
4. **Cache Invalidation**: Redis keys cleared when source data changes

### Background Job Patterns

```python
# AI Summarization Job
@celery.task
async def summarize_tender(tender_id: str):
    # 1. Fetch tender from PostgreSQL
    tender = await db.execute("SELECT title, description FROM tenders WHERE tender_id = %s", tender_id)
    
    # 2. Generate AI summary
    summary = await ai_model.summarize(tender.description)
    
    # 3. Store in MongoDB
    await mongo_db.tender_summaries.insert_one({
        "tender_id": tender_id,
        "summary": summary,
        "model_used": "facebook/bart-large-cnn",
        "created_at": datetime.utcnow()
    })
    
    # 4. Invalidate related caches
    await redis.delete(f"tender:{tender_id}:metadata")

# Score Recalculation Job
@celery.task
async def recalculate_scores(team_id: int):
    # 1. Get updated company profile
    profile = await get_company_profile(team_id)
    
    # 2. Get all team's saved tenders
    tenders = await get_team_tenders(team_id)
    
    # 3. Recalculate scores
    for tender in tenders:
        score = calculate_readiness_score(profile, tender)
        await mongo_db.readiness_scores.replace_one(
            {"team_id": team_id, "tender_id": tender.id},
            score,
            upsert=True
        )
    
    # 4. Clear cached rankings
    await redis.delete(f"team:{team_id}:ranked_tenders")
```

## Performance Optimizations

### Database Indexing Strategy

#### PostgreSQL Indexes
```sql
-- Core performance indexes
CREATE INDEX CONCURRENTLY idx_tenders_active_deadline ON tenders(deadline) 
    WHERE status = 'active' AND deadline > NOW();

CREATE INDEX CONCURRENTLY idx_workspace_team_status_updated ON workspace_entries(team_id, status, updated_at DESC);

-- Partial indexes for common queries
CREATE INDEX CONCURRENTLY idx_users_active_by_team ON users(team_id, email) 
    WHERE is_active = true;

-- Composite indexes for complex filters
CREATE INDEX CONCURRENTLY idx_tenders_search_filter ON tenders(province, budget, deadline) 
    WHERE status = 'active';
```

#### MongoDB Indexes
```javascript
// Compound indexes for tenant-specific queries
db.readiness_scores.createIndex(
    { "team_id": 1, "score": -1, "generated_at": -1 },
    { name: "team_score_time_idx" }
);

// Sparse indexes for optional fields
db.tender_summaries.createIndex(
    { "confidence_score": -1 },
    { sparse: true, name: "confidence_sparse_idx" }
);
```

### Connection Pooling

```python
# PostgreSQL connection pool
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

# MongoDB connection pool
from motor.motor_asyncio import AsyncIOMotorClient

mongo_client = AsyncIOMotorClient(
    MONGODB_URL,
    maxPoolSize=50,
    minPoolSize=5,
    serverSelectionTimeoutMS=5000
)
```

## Backup and Disaster Recovery

### PostgreSQL Backup Strategy
```bash
# Daily automated backups with point-in-time recovery
pg_dump --format=custom --verbose --file=backup_$(date +%Y%m%d).sql tender_insight_db

# WAL archiving for point-in-time recovery
archive_command = 'cp %p /backup/wal_archive/%f'
```

### MongoDB Backup Strategy
```bash
# Daily mongodump with compression
mongodump --uri="mongodb://..." --gzip --archive=backup_$(date +%Y%m%d).gz

# Replica set for automatic failover
# Primary + 2 Secondaries across different availability zones
```

### Redis Persistence
```conf
# Redis configuration for durability
save 900 1      # Save if at least 1 key changed in 900 seconds
save 300 10     # Save if at least 10 keys changed in 300 seconds
save 60 10000   # Save if at least 10000 keys changed in 60 seconds

# AOF persistence for maximum durability
appendonly yes
appendfsync everysec
```

## Migration Strategy

### Database Versioning
```python
# Alembic for PostgreSQL schema migrations
# alembic/versions/001_initial_schema.py
def upgrade():
    op.create_table('teams',
        sa.Column('team_id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('saas_plan', sa.String(20), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, default=sa.func.now())
    )

# MongoDB schema migrations using custom migration system
class MongoMigration_001:
    def upgrade(self):
        # Create collections with validation
        db.create_collection("tender_summaries", {...})
        
    def downgrade(self):
        # Rollback operations
        db.drop_collection("tender_summaries")
```

### Data Migration Scripts
```python
# Example: Migrating from single database to multi-database
async def migrate_to_multi_db():
    # 1. Extract AI results from PostgreSQL JSONB fields
    old_summaries = await pg_db.execute("""
        SELECT tender_id, ai_summary, readiness_score 
        FROM old_tender_analysis_table
    """)
    
    # 2. Insert into MongoDB collections
    for summary in old_summaries:
        await mongo_db.tender_summaries.insert_one({
            "tender_id": summary.tender_id,
            "summary": summary.ai_summary,
            "model_used": "migrated_data",
            "created_at": datetime.utcnow()
        })
    
    # 3. Verify data integrity
    pg_count = await pg_db.scalar("SELECT COUNT(*) FROM old_tender_analysis_table")
    mongo_count = await mongo_db.tender_summaries.count_documents({})
    assert pg_count == mongo_count, "Migration data mismatch"
```

## Monitoring and Maintenance

### Database Health Monitoring
```python
# Health check endpoints
@router.get("/health/databases")
async def check_database_health():
    health_status = {}
    
    # PostgreSQL health
    try:
        await pg_db.execute("SELECT 1")
        health_status["postgresql"] = {"status": "healthy", "latency_ms": response_time}
    except Exception as e:
        health_status["postgresql"] = {"status": "unhealthy", "error": str(e)}
    
    # MongoDB health
    try:
        await mongo_client.admin.command("ping")
        health_status["mongodb"] = {"status": "healthy"}
    except Exception as e:
        health_status["mongodb"] = {"status": "unhealthy", "error": str(e)}
    
    # Redis health
    try:
        await redis.ping()
        health_status["redis"] = {"status": "healthy"}
    except Exception as e:
        health_status["redis"] = {"status": "unhealthy", "error": str(e)}
    
    return health_status
```

### Performance Monitoring Queries
```sql
-- PostgreSQL slow query monitoring
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
WHERE mean_time > 1000  -- Queries taking more than 1 second
ORDER BY mean_time DESC;

-- Connection pool monitoring
SELECT 
    state,
    COUNT(*) as connections
FROM pg_stat_activity 
GROUP BY state;
```

```javascript
// MongoDB performance monitoring
db.runCommand({
    "collStats": "readiness_scores",
    "indexDetails": true
})

// Index usage statistics
db.readiness_scores.aggregate([
    { $indexStats: {} }
])
```

### Maintenance Scripts
```python
# Automated cleanup jobs
@celery.task
async def cleanup_old_data():
    # Remove old activity logs (keep 90 days)
    cutoff_date = datetime.utcnow() - timedelta(days=90)
    await mongo_db.user_activity_logs.delete_many({
        "timestamp": {"$lt": cutoff_date}
    })
    
    # Clean up expired cache entries
    await redis.execute_command("SCAN", "0", "MATCH", "temp:*", "COUNT", "1000")
    
    # Vacuum PostgreSQL tables
    await pg_db.execute("VACUUM ANALYZE;")

# Index maintenance
@celery.task
async def rebuild_indexes():
    # PostgreSQL index maintenance
    await pg_db.execute("REINDEX DATABASE tender_insight_db;")
    
    # MongoDB index optimization
    await mongo_db.tender_summaries.reindex()
    await mongo_db.readiness_scores.reindex()
```

## Security Considerations

### Data Encryption
```python
# Database connection encryption
DATABASE_URL = "postgresql+asyncpg://user:pass@host:5432/db?ssl=require"
MONGODB_URL = "mongodb://user:pass@host:27017/db?ssl=true&authSource=admin"

# Field-level encryption for sensitive data
from cryptography.fernet import Fernet

class EncryptedField:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt(self, value: str) -> str:
        return self.cipher.encrypt(value.encode()).decode()
    
    def decrypt(self, encrypted_value: str) -> str:
        return self.cipher.decrypt(encrypted_value.encode()).decode()

# Usage in company profiles for sensitive contact info
encrypted_email = encrypted_field.encrypt(profile.contact_email)
```

### Access Control
```sql
-- PostgreSQL role-based access
CREATE ROLE app_read_only LOGIN PASSWORD 'secure_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_read_only;

CREATE ROLE app_read_write LOGIN PASSWORD 'secure_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_read_write;

-- Restrict sensitive operations
REVOKE ALL ON users FROM app_read_write;
GRANT SELECT, UPDATE(last_login) ON users TO app_read_write;
```

### Audit Logging
```python
# Database operation audit trail
@event.listens_for(User, 'after_update')
def log_user_update(mapper, connection, target):
    audit_log = {
        "table": "users",
        "operation": "update",
        "user_id": target.user_id,
        "changes": get_changed_fields(target),
        "timestamp": datetime.utcnow()
    }
    # Log to MongoDB audit collection
    asyncio.create_task(mongo_db.audit_logs.insert_one(audit_log))
```

## Scaling Considerations

### Horizontal Scaling Strategies

#### PostgreSQL Scaling
```python
# Read replicas for query distribution
class DatabaseRouter:
    def __init__(self):
        self.write_db = create_engine(PRIMARY_DB_URL)
        self.read_db = create_engine(READ_REPLICA_URL)
    
    async def execute_read(self, query):
        return await self.read_db.execute(query)
    
    async def execute_write(self, query):
        return await self.write_db.execute(query)

# Connection pooling with multiple databases
from sqlalchemy.pool import NullPool
read_engine = create_async_engine(READ_REPLICA_URL, poolclass=NullPool)
```

#### MongoDB Sharding
```javascript
// Shard key selection for team-based partitioning
sh.enableSharding("tender_insight_db")

// Shard readiness_scores by team_id for even distribution
sh.shardCollection(
    "tender_insight_db.readiness_scores",
    { "team_id": 1 }
)

// Shard tender_summaries by hashed tender_id for random distribution
sh.shardCollection(
    "tender_insight_db.tender_summaries",
    { "tender_id": "hashed" }
)
```

#### Redis Clustering
```python
# Redis Cluster configuration
import redis.asyncio as redis

redis_cluster = redis.RedisCluster(
    startup_nodes=[
        {"host": "redis-node-1", "port": 7000},
        {"host": "redis-node-2", "port": 7000},
        {"host": "redis-node-3", "port": 7000},
    ],
    decode_responses=True,
    skip_full_coverage_check=True
)
```

### Capacity Planning

#### Storage Growth Estimates
```python
# Estimated storage requirements per year
STORAGE_ESTIMATES = {
    "postgresql": {
        "users": "1MB per 1000 users",
        "tenders": "50MB per 10,000 tenders", 
        "workspace_entries": "10MB per 10,000 entries"
    },
    "mongodb": {
        "tender_summaries": "200MB per 10,000 summaries",
        "readiness_scores": "100MB per 10,000 scores",
        "activity_logs": "500MB per month (capped)"
    },
    "redis": {
        "cache": "2GB average working set",
        "sessions": "100MB per 1000 active users"
    }
}
```

#### Performance Benchmarks
```python
# Target performance metrics
PERFORMANCE_TARGETS = {
    "api_response_time": "< 200ms for 95th percentile",
    "search_latency": "< 500ms for complex queries",
    "ai_processing": "< 30 seconds per document",
    "concurrent_users": "1000+ simultaneous users",
    "database_connections": "< 80% pool utilization"
}
```

## Development and Testing

### Database Testing Strategy
```python
# Test database fixtures
@pytest.fixture
async def test_db():
    # Create test database
    test_engine = create_async_engine(TEST_DATABASE_URL)
    
    # Run migrations
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    
    yield test_engine
    
    # Cleanup
    await test_engine.dispose()

# Integration tests with real databases
@pytest.mark.asyncio
async def test_multi_database_sync():
    # Test data consistency across databases
    tender_id = "test-tender-123"
    
    # Insert tender in PostgreSQL
    await pg_db.execute("INSERT INTO tenders (...) VALUES (...)")
    
    # Trigger AI processing
    await summarize_tender.apply_async(args=[tender_id])
    
    # Verify summary in MongoDB
    summary = await mongo_db.tender_summaries.find_one({"tender_id": tender_id})
    assert summary is not None
    assert len(summary["summary"]) <= 500
```

### Development Environment Setup
```yaml
# docker-compose.yml for local development
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: tender_insight_dev
      POSTGRES_USER: dev_user
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  mongodb:
    image: mongo:6.0
    environment:
      MONGO_INITDB_DATABASE: tender_insight_dev
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  mongodb_data:
  redis_data:
```

This comprehensive database design provides a robust foundation for the Tender Insight Hub platform, ensuring scalability, performance, and maintainability while supporting all the required features including AI processing, multi-tenancy, and real-time analytics.
