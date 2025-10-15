# create_sample_data.py - COMPLETELY FIXED VERSION
from database import SessionLocal, User, Team, CompanyProfile, Tender, WorkspaceTender
from auth import get_password_hash
from datetime import datetime, timedelta
import json

def create_sample_data():
    db = SessionLocal()
    
    try:
        print("Creating sample data...")
        
        # Clear existing data in correct order (respecting foreign keys)
        try:
            db.query(WorkspaceTender).delete()
            db.query(Tender).delete()
            db.query(CompanyProfile).delete()
            db.query(User).delete()
            db.query(Team).delete()
            db.commit()
        except Exception as e:
            print(f"⚠️  Warning during cleanup: {e}")
            db.rollback()
        
        # Create sample teams FIRST and commit immediately
        teams = [
            Team(name="Construction Pros", plan_tier="pro"),
            Team(name="IT Solutions Ltd", plan_tier="basic"),
            Team(name="Startup Builders", plan_tier="free")
        ]
        db.add_all(teams)
        db.commit()  # COMMIT TEAMS FIRST
        # Refresh to get actual IDs
        for team in teams:
            db.refresh(team)
        print("✅ Teams created")
        
        # Now create users with the committed team IDs
        users = [
            User(
                email="admin@construction.com",
                hashed_password=get_password_hash("password123"),
                full_name="John Construction",
                team_id=teams[0].id,  # Use the actual team ID
                is_team_admin=True,
                created_at=datetime.utcnow()
            ),
            User(
                email="manager@construction.com",
                hashed_password=get_password_hash("password123"),
                full_name="Sarah Manager",
                team_id=teams[0].id,  # Use the actual team ID
                is_team_admin=False,
                created_at=datetime.utcnow()
            ),
            User(
                email="dev@itsolutions.com",
                hashed_password=get_password_hash("password123"),
                full_name="Mike Developer",
                team_id=teams[1].id,  # Use the actual team ID
                is_team_admin=True,
                created_at=datetime.utcnow()
            )
        ]
        db.add_all(users)
        db.commit()
        # Refresh to get actual user IDs
        for user in users:
            db.refresh(user)
        print("✅ Users created")
        
        # Create company profiles
        company_profiles = [
            CompanyProfile(
                team_id=teams[0].id,
                company_name="Construction Pros Pty Ltd",
                industry_sector="Construction",
                services_provided="Road construction, building maintenance, infrastructure development",
                certifications={"CIDB": "Grade 7", "BBBEE": "Level 2", "SARS": "true"},
                geographic_coverage=["Gauteng", "Western Cape", "KwaZulu-Natal"],
                years_experience=12,
                contact_email="info@construction.com",
                contact_phone="+27 11 123 4567",
                updated_at=datetime.utcnow()
            ),
            CompanyProfile(
                team_id=teams[1].id,
                company_name="IT Solutions Ltd",
                industry_sector="Information Technology",
                services_provided="Software development, IT consulting, network infrastructure",
                certifications={"BBBEE": "Level 1", "SARS": "true"},
                geographic_coverage=["Gauteng", "Western Cape"],
                years_experience=8,
                contact_email="contact@itsolutions.com",
                contact_phone="+27 11 987 6543",
                updated_at=datetime.utcnow()
            )
        ]
        db.add_all(company_profiles)
        db.commit()
        print("✅ Company profiles created")
        
        # Create sample tenders
        tenders = [
            Tender(
                tender_id="TENDER-001",
                title="Road Construction and Maintenance - N1 Highway",
                description="Construction and maintenance of N1 highway sections including bridge repairs and road resurfacing. Required: CIDB Grade 6 minimum, 5+ years experience in road construction.",
                province="Gauteng",
                submission_deadline=datetime.utcnow() + timedelta(days=30),
                buyer_organization="Department of Public Works",
                budget_range="R5,000,000 - R10,000,000",
                budget_min=5000000,
                budget_max=10000000,
                source_url="http://example.com/tender001",
                document_url="http://example.com/documents/tender001.pdf",
                created_at=datetime.utcnow()
            ),
            Tender(
                tender_id="TENDER-002",
                title="IT Infrastructure Upgrade - Government Offices",
                description="Upgrade of IT infrastructure across multiple government offices including network setup, server installation, and security systems.",
                province="Western Cape",
                submission_deadline=datetime.utcnow() + timedelta(days=45),
                buyer_organization="Department of Communications",
                budget_range="R2,000,000 - R5,000,000",
                budget_min=2000000,
                budget_max=5000000,
                source_url="http://example.com/tender002",
                document_url="http://example.com/documents/tender002.zip",
                created_at=datetime.utcnow()
            ),
            Tender(
                tender_id="TENDER-003",
                title="School Building Construction - Limpopo Province",
                description="Construction of new school buildings including classrooms, administration block, and sanitation facilities.",
                province="Limpopo",
                submission_deadline=datetime.utcnow() + timedelta(days=60),
                buyer_organization="Department of Basic Education",
                budget_range="R8,000,000 - R15,000,000",
                budget_min=8000000,
                budget_max=15000000,
                source_url="http://example.com/tender003",
                document_url="http://example.com/documents/tender003.pdf",
                created_at=datetime.utcnow()
            ),
            Tender(
                tender_id="TENDER-004",
                title="Security Services - Government Buildings",
                description="Provision of security services for government buildings across multiple provinces.",
                province="National",
                submission_deadline=datetime.utcnow() + timedelta(days=25),
                buyer_organization="Department of Public Service and Administration",
                budget_range="R1,500,000 - R3,000,000",
                budget_min=1500000,
                budget_max=3000000,
                source_url="http://example.com/tender004",
                document_url="http://example.com/documents/tender004.pdf",
                created_at=datetime.utcnow()
            ),
            Tender(
                tender_id="TENDER-005",
                title="Cleaning Services - Provincial Hospitals",
                description="Comprehensive cleaning and sanitation services for provincial healthcare facilities.",
                province="Eastern Cape",
                submission_deadline=datetime.utcnow() + timedelta(days=40),
                buyer_organization="Department of Health",
                budget_range="R800,000 - R1,500,000",
                budget_min=800000,
                budget_max=1500000,
                source_url="http://example.com/tender005",
                document_url="http://example.com/documents/tender005.zip",
                created_at=datetime.utcnow()
            )
        ]
        db.add_all(tenders)
        db.commit()
        # Refresh to get actual tender IDs
        for tender in tenders:
            db.refresh(tender)
        print("✅ Tenders created")
        
        # Add some tenders to workspace - FIXED: Use actual tender IDs and user IDs
        workspace_tenders = [
            WorkspaceTender(
                team_id=teams[0].id,
                tender_id=tenders[0].id,  # Use actual tender ID
                status="interested",
                match_score=85.5,
                last_updated_by=users[0].id,  # Use actual user ID
                notes="Good match with our road construction experience",
                last_updated_at=datetime.utcnow()
            ),
            WorkspaceTender(
                team_id=teams[0].id,
                tender_id=tenders[2].id,  # Use actual tender ID
                status="pending",
                match_score=72.0,
                last_updated_by=users[0].id,  # Use actual user ID
                notes="Need to check CIDB requirements",
                last_updated_at=datetime.utcnow()
            ),
            WorkspaceTender(
                team_id=teams[1].id,
                tender_id=tenders[1].id,  # Use actual tender ID
                status="interested",
                match_score=90.0,
                last_updated_by=users[2].id,  # Use actual user ID
                notes="Perfect match for our IT services",
                last_updated_at=datetime.utcnow()
            )
        ]
        db.add_all(workspace_tenders)
        db.commit()
        print("✅ Workspace entries created")
        
        print("\n🎉 Sample data created successfully!")
        print(f"📊 Summary:")
        print(f"   - {len(teams)} teams")
        print(f"   - {len(users)} users") 
        print(f"   - {len(company_profiles)} company profiles")
        print(f"   - {len(tenders)} tenders")
        print(f"   - {len(workspace_tenders)} workspace entries")
        
        print("\n🔑 Test credentials:")
        print("   Email: admin@construction.com")
        print("   Password: password123")
        print("   Email: dev@itsolutions.com") 
        print("   Password: password123")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        raise  # Re-raise to see the actual error
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()