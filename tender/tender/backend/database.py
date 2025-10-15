# database.py - COMPLETELY FIXED VERSION

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, text, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import json
from urllib.parse import quote_plus, urlparse
from bson import ObjectId
from fastapi.encoders import jsonable_encoder

load_dotenv()

# DATABASE CONFIGURATION - MySQL with proper URL encoding for special characters
DATABASE_URL = os.getenv("DATABASE_URL", "")

def create_mysql_engine(db_url):
    """Create MySQL engine with proper connection testing"""
    try:
        # Use urllib.parse for proper URL handling
        parsed = urlparse(db_url)
        
        # Encode password properly
        username = parsed.username
        password = quote_plus(parsed.password) if parsed.password else ""
        hostname = parsed.hostname
        database = parsed.path[1:] if parsed.path else "tender_hub"
        port = parsed.port if parsed.port else 3306
        
        # Reconstruct URL with encoded password
        encoded_url = f"mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}"
        
        # Create engine with connection parameters - FIXED VERSION
        engine = create_engine(
            encoded_url, 
            pool_pre_ping=True, 
            pool_recycle=300,
            echo=False,  # Set to True for debugging SQL queries
            future=True  # Use SQLAlchemy 2.0 style
        )
        
        # Test connection - FIXED: Use text() for proper SQL execution
        with engine.connect() as conn:
            # Use text() for raw SQL execution
            result = conn.execute(text("SELECT 1"))
            result.fetchone()  # Actually fetch the result
            print("✅ MySQL database connected successfully!")
        return engine
        
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        return None

# Try MySQL first, then fallback to SQLite
engine = None
if DATABASE_URL and "mysql" in DATABASE_URL:
    engine = create_mysql_engine(DATABASE_URL)

if engine is None:
    print("📝 Falling back to SQLite for development...")
    DATABASE_URL = "sqlite:///./tender_hub.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MONGODB - NoSQL database as REQUIRED by project
try:
    mongo_client = MongoClient(
        os.getenv("MONGO_URL", "mongodb://localhost:27017/"),
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=30000,
        maxPoolSize=50
    )
    mongo_db = mongo_client["tender_hub"]
    
    # Test connection with longer timeout
    mongo_client.admin.command('ping', maxTimeMS=5000)
    print("✅ MongoDB connected successfully")
    
    # FIXED: Skip index creation to avoid conflicts - let mongodb_service handle it
    print("✅ MongoDB indexes will be handled by mongodb_service")
    
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    mongo_client = None
    mongo_db = None

# Custom JSON field for MySQL compatibility
class JSONEncodedDict(TypeDecorator):
    impl = Text
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            try:
                return json.loads(value)
            except:
                return {}
        return {}

# CUSTOM JSON ENCODER FOR ObjectId - FIXES ObjectId SERIALIZATION
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# CUSTOM JSONABLE ENCODER FOR FASTAPI - FIXES ObjectId SERIALIZATION
def custom_jsonable_encoder(obj):
    """Custom JSON encoder that handles ObjectId"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        return {k: custom_jsonable_encoder(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    elif isinstance(obj, list):
        return [custom_jsonable_encoder(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: custom_jsonable_encoder(v) for k, v in obj.items()}
    return obj

# DATABASE MODELS
class User(Base):
    __tablename__ = "users"
   
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    is_team_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
   
    team = relationship("Team", back_populates="users")

class Team(Base):
    __tablename__ = "teams"
   
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    plan_tier = Column(String(50), default="free", nullable=False)  # free, basic, pro
    created_at = Column(DateTime, default=datetime.utcnow)
   
    users = relationship("User", back_populates="team")
    company_profile = relationship("CompanyProfile", back_populates="team", uselist=False)

class CompanyProfile(Base):
    __tablename__ = "company_profiles"
   
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), unique=True, nullable=False)
    company_name = Column(String(255), nullable=False)
    industry_sector = Column(String(255), nullable=False)
    services_provided = Column(Text, nullable=False)
    certifications = Column(JSONEncodedDict)
    geographic_coverage = Column(JSONEncodedDict)
    years_experience = Column(Integer, nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
   
    team = relationship("Team", back_populates="company_profile")

class Tender(Base):
    __tablename__ = "tenders"
   
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tender_id = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    province = Column(String(100))
    submission_deadline = Column(DateTime)
    buyer_organization = Column(String(255))
    budget_range = Column(String(100))
    budget_min = Column(Float)
    budget_max = Column(Float)
    source_url = Column(String(500))
    document_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

class WorkspaceTender(Base):
    __tablename__ = "workspace_tenders"
   
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    tender_id = Column(Integer, ForeignKey("tenders.id"), nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    match_score = Column(Float, nullable=True)
    last_updated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    last_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(Text, nullable=True)

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    print("✅ MySQL database tables created successfully!")
except Exception as e:
    print(f"❌ Error creating tables: {e}")
    raise Exception("Database setup failed - check MySQL connection")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to convert MongoDB documents to JSON-serializable format
def convert_mongo_doc(doc):
    """Convert MongoDB document to JSON-serializable format"""
    if doc is None:
        return None
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, dict):
        return {k: convert_mongo_doc(v) for k, v in doc.items()}
    if isinstance(doc, list):
        return [convert_mongo_doc(item) for item in doc]
    if isinstance(doc, datetime):
        return doc.isoformat()
    return doc

# Helper function to convert MongoDB cursor to list of JSON-serializable docs
def convert_mongo_cursor(cursor):
    """Convert MongoDB cursor to list of JSON-serializable documents"""
    if cursor is None:
        return []
    return [convert_mongo_doc(doc) for doc in cursor]

# Helper function to get database statistics
def get_database_stats():
    """Get statistics for both MySQL and MongoDB"""
    stats = {
        "mysql": {},
        "mongodb": {},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # MySQL stats
    db = SessionLocal()
    try:
        tables = ['users', 'teams', 'company_profiles', 'tenders', 'workspace_tenders']
        for table in tables:
            count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            stats["mysql"][table] = count
    except Exception as e:
        print(f"Error getting MySQL stats: {e}")
        stats["mysql"]["error"] = str(e)
    finally:
        db.close()
    
    # MongoDB stats - FIXED: Use explicit None check instead of truthiness
    if mongo_db is not None:
        try:
            collections = mongo_db.list_collection_names()
            for coll in collections:
                count = mongo_db[coll].count_documents({})
                stats["mongodb"][coll] = count
        except Exception as e:
            print(f"Error getting MongoDB stats: {e}")
            stats["mongodb"]["error"] = str(e)
    else:
        print("⚠️ MongoDB not available for stats collection")
        stats["mongodb"]["error"] = "MongoDB not available"
    
    return stats

# Test database connections
def test_database_connections():
    """Test both database connections"""
    results = {
        "mysql": False,
        "mongodb": False,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Test MySQL
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        results["mysql"] = True
        print("✅ MySQL connection test: PASSED")
    except Exception as e:
        print(f"❌ MySQL connection test: FAILED - {e}")
        results["mysql_error"] = str(e)
    
    # Test MongoDB - FIXED: Use explicit None check instead of truthiness
    if mongo_client is not None:
        try:
            mongo_client.admin.command('ping')
            results["mongodb"] = True
            print("✅ MongoDB connection test: PASSED")
        except Exception as e:
            print(f"❌ MongoDB connection test: FAILED - {e}")
            results["mongodb_error"] = str(e)
    else:
        print("❌ MongoDB connection test: SKIPPED (no client)")
        results["mongodb_error"] = "MongoDB client not available"
    
    return results

# Initialize database connections on import
if __name__ == "__main__":
    print("🔧 Testing database connections...")
    test_database_connections()
    
    print("\n📊 Database statistics:")
    stats = get_database_stats()
    print(f"MySQL: {stats['mysql']}")
    print(f"MongoDB: {stats['mongodb']}")