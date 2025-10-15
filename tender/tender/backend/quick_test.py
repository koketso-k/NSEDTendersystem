# quick_test.py - QUICK SMOKE TEST FOR AI PIPELINE

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_services import AIService
from document_processor import DocumentProcessor

def quick_smoke_test():
    """Quick smoke test to verify basic functionality"""
    print("🚀 Running Quick Smoke Test...")
    
    try:
        # Test AI Service
        ai = AIService()
        sample_text = "Construction tender for road works. Requires CIDB Grade 6 and 3 years experience."
        
        result = ai.analyze_document_content(sample_text)
        print(f"✅ AI Service: Industry={result['industry_sector']}, Score={result['complexity_score']}")
        
        # Test Document Processor
        processor = DocumentProcessor()
        doc_result = processor.process_document("https://example.com/test.pdf")
        print(f"✅ Document Processor: Summary length={len(doc_result.get('summary', ''))}")
        
        # Test Readiness Scoring
        company_profile = {
            "industry_sector": "Construction",
            "certifications": {"CIDB": "Grade 6"},
            "years_experience": 4,
            "geographic_coverage": ["Gauteng"]
        }
        
        tender_req = result['requirements']
        score_result = ai.calculate_readiness_score(tender_req, company_profile)
        print(f"✅ Readiness Scoring: Score={score_result['suitability_score']}/100")
        
        print("🎉 Smoke test passed! Basic AI pipeline is working.")
        return True
        
    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        return False

if __name__ == "__main__":
    quick_smoke_test()