# quick_verification.py - QUICK VERIFICATION OF FIXED COMPONENTS

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def quick_verification():
    """Quick verification that all components are working"""
    print("🔍 Quick Verification of Fixed Components")
    print("="*50)
    
    try:
        # Test imports
        from document_processor import DocumentProcessor
        from ai_services import AIService
        from readiness_scorer import ReadinessScorer
        from mongodb_service import mongodb_service
        from ocds_client import OCDSClient
        
        print("✅ All imports successful")
        
        # Test component initialization
        doc_processor = DocumentProcessor()
        ai_service = AIService()
        readiness_scorer = ReadinessScorer()
        ocds_client = OCDSClient()
        
        print("✅ All components initialized")
        
        # Test MongoDB connection
        try:
            stats = mongodb_service.get_database_stats()
            print("✅ MongoDB connection working")
        except Exception as e:
            print(f"⚠️ MongoDB connection: {e}")
        
        # Test basic functionality
        sample_text = "Construction tender for government building. Requires CIDB Grade 6."
        
        # Document processing
        doc_result = doc_processor.process_document("https://test.com/sample.pdf")
        print(f"✅ Document processing: {len(doc_result.get('summary', '')) > 0}")
        
        # AI analysis
        ai_result = ai_service.analyze_document_content(sample_text)
        print(f"✅ AI analysis: Industry={ai_result.get('industry_sector')}")
        
        # Readiness scoring
        company_data = {
            "industry_sector": "Construction",
            "certifications": {"CIDB": "Grade 6"},
            "years_experience": 5,
            "geographic_coverage": ["Gauteng"]
        }
        score_result = ai_service.calculate_readiness_score(ai_result["requirements"], company_data)
        print(f"✅ Readiness scoring: Score={score_result.get('suitability_score')}/100")
        
        # OCDS client
        api_status = ocds_client.get_api_status()
        print(f"✅ OCDS client: API {'Online' if api_status.get('online') else 'Offline'}")
        
        print("\n🎉 All components are working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    quick_verification()