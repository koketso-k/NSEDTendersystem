# run.py - IMPROVED VERSION
import uvicorn
from main import app
from database import Base, engine, test_database_connections
import sample_data
from real_tender_fetcher import sync_tenders

def initialize_application():
    try:
        print("🚀 Initializing Tender Insight Hub...")
        
        # Test database connections first
        print("🔧 Testing database connections...")
        db_status = test_database_connections()
        
        if not db_status["mysql"]:
            print("❌ MySQL connection failed - cannot continue")
            return False
        
        # Create tables
        print("📊 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Create sample data
        print("👥 Creating sample data...")
        sample_data.create_sample_data()
        
        # Sync real tender data (optional)
        if db_status["mysql"]:
            print("📋 Syncing real tender data...")
            try:
                sync_result = sync_tenders()
                print(f"✅ Tender sync: {sync_result['added']} added, {sync_result['updated']} updated")
            except Exception as e:
                print(f"⚠️  Tender sync failed: {e}")
                print("📝 Using sample tender data only")
        
        print("\n🎉 Application initialized successfully!")
        print("📍 Backend API: http://127.0.0.1:8000")
        print("📚 API Documentation: http://127.0.0.1:8000/docs") 
        print("🖥️  Frontend: Open index.html in your browser or run: python -m http.server 3000")
        print("⏹️  Press CTRL+C to stop the server\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if initialize_application():
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    else:
        print("❌ Failed to start application - check database connections")