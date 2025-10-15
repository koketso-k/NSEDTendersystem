# test_ai_pipeline.py - COMPREHENSIVE AI PIPELINE INTEGRATION TESTS

import sys
import os
import asyncio
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_services import AIService
from document_processor import DocumentProcessor
from readiness_scorer import ReadinessScorer
from database import SessionLocal, CompanyProfile, Tender
from mongodb_service import mongodb_service

class AIPipelineTester:
    def __init__(self):
        self.ai_service = AIService()
        self.document_processor = DocumentProcessor()
        self.readiness_scorer = ReadinessScorer()
        self.db = SessionLocal()
        
    def test_document_processing(self):
        """Test document processing pipeline"""
        print("\n" + "="*60)
        print("🧪 TEST 1: DOCUMENT PROCESSING PIPELINE")
        print("="*60)
        
        # Test with a sample document URL (will use fallback content)
        test_document_url = "https://example.com/sample-tender.pdf"
        
        try:
            print("📄 Processing sample tender document...")
            result = self.document_processor.process_document(test_document_url)
            
            if "error" in result:
                print(f"❌ Document processing failed: {result['error']}")
                return False
            
            print("✅ Document processing successful!")
            print(f"   - Summary: {result['summary'][:100]}...")
            print(f"   - Text length: {result.get('original_text_length', 0)} characters")
            print(f"   - Key points: {len(result.get('key_points', {}))} items")
            
            # Verify key structure
            required_keys = ['summary', 'key_points', 'original_text_length']
            if all(key in result for key in required_keys):
                print("✅ Document structure validation passed")
                return True
            else:
                print("❌ Document structure validation failed")
                return False
                
        except Exception as e:
            print(f"❌ Document processing test failed: {e}")
            return False

    def test_ai_analysis(self):
        """Test AI analysis pipeline"""
        print("\n" + "="*60)
        print("🧪 TEST 2: AI ANALYSIS PIPELINE")
        print("="*60)
        
        # Sample tender text for analysis
        sample_text = """
        GOVERNMENT TENDER NOTICE
        Tender Number: TDR-2024-1109-001
        Department: Department of Public Works and Infrastructure
        Province: Gauteng
        
        SCOPE OF WORK:
        Construction of new municipal office building including civil works, 
        structural engineering, and finishing. The project requires CIDB Grade 7 
        minimum with 5 years experience in similar construction projects.
        
        ELIGIBILITY CRITERIA:
        - Valid SARS Tax Clearance Certificate
        - BBBEE Level 2 or better
        - CIDB Grade 7 or higher
        - Minimum 5 years construction experience
        - Operations in Gauteng province
        
        BUDGET: R 8,500,000
        CLOSING DATE: 15 December 2024
        
        SUBMISSION REQUIREMENTS:
        Complete tender documentation including technical proposal, pricing schedule, 
        company profile, and all required certificates must be submitted by the closing date.
        """
        
        try:
            print("🤖 Running AI analysis on sample tender...")
            result = self.ai_service.analyze_document_content(sample_text)
            
            print("✅ AI analysis successful!")
            print(f"   - Industry: {result['industry_sector']}")
            print(f"   - Complexity: {result['complexity_score']}/100")
            print(f"   - Confidence: {result['analysis_confidence']}")
            print(f"   - Timeline: {result['estimated_timeline']}")
            print(f"   - Budget: {result['budget_indication']}")
            
            # Test requirement extraction
            requirements = result['requirements']
            print(f"   - Certifications required: {len(requirements['required_certifications'])}")
            print(f"   - Experience required: {requirements['experience_years']} years")
            print(f"   - Geographic requirements: {requirements['geographic_requirements']}")
            
            # Verify analysis structure
            required_keys = ['industry_sector', 'summary', 'complexity_score', 'requirements']
            if all(key in result for key in required_keys):
                print("✅ AI analysis structure validation passed")
                return True
            else:
                print("❌ AI analysis structure validation failed")
                return False
                
        except Exception as e:
            print(f"❌ AI analysis test failed: {e}")
            return False

    def test_ai_summarization_endpoint(self):
        """Test the complete AI summarization endpoint"""
        print("\n" + "="*60)
        print("🧪 TEST 3: AI SUMMARIZATION ENDPOINT")
        print("="*60)
        
        try:
            print("📊 Testing complete AI summarization pipeline...")
            # This tests the static method used by the API endpoint
            test_document_url = "https://example.com/sample-tender.pdf"
            result = AIService.summarize_document(test_document_url)
            
            if "error" in result:
                print(f"❌ AI summarization failed: {result['error']}")
                return False
            
            print("✅ AI summarization successful!")
            print(f"   - Summary: {result['summary'][:150]}...")
            print(f"   - Industry: {result.get('industry_sector', 'N/A')}")
            print(f"   - Complexity: {result.get('complexity_score', 'N/A')}")
            print(f"   - Key points: {len(result.get('key_points', {}))} items")
            
            # Test MongoDB storage integration
            print("💾 Testing MongoDB storage...")
            storage_result = mongodb_service.store_ai_summary(
                tender_id=999,  # Test ID
                document_url=test_document_url,
                summary=result['summary'],
                key_points=result['key_points'],
                user_id=1,
                team_id=1
            )
            
            if storage_result:
                print("✅ MongoDB storage test passed")
                
                # Test retrieval
                stored_summary = mongodb_service.get_tender_summary(999)
                if stored_summary:
                    print("✅ MongoDB retrieval test passed")
                else:
                    print("❌ MongoDB retrieval test failed")
            else:
                print("❌ MongoDB storage test failed")
            
            return storage_result
            
        except Exception as e:
            print(f"❌ AI summarization test failed: {e}")
            return False

    def test_readiness_scoring(self):
        """Test readiness scoring pipeline"""
        print("\n" + "="*60)
        print("🧪 TEST 4: READINESS SCORING PIPELINE")
        print("="*60)
        
        try:
            # Create sample company profile
            company_profile_data = {
                "company_name": "Test Construction Co",
                "industry_sector": "Construction",
                "services_provided": "Civil engineering, building construction, infrastructure development, road works, and structural projects",
                "certifications": {
                    "CIDB": "Grade 7",
                    "BBBEE": "Level 2",
                    "SARS": "true"
                },
                "geographic_coverage": ["Gauteng", "Western Cape", "KwaZulu-Natal"],
                "years_experience": 8,
                "contact_email": "test@construction.co.za",
                "contact_phone": "+27 11 123 4567"
            }
            
            # Create sample tender requirements
            tender_requirements = {
                "required_certifications": ["CIDB: Grade 7", "BBBEE: Level 2", "SARS Tax Clearance"],
                "experience_years": 5,
                "geographic_requirements": ["Gauteng"],
                "industry_sector": "Construction",
                "technical_requirements": ["Civil works experience", "Building construction expertise"]
            }
            
            print("📈 Testing readiness scoring...")
            result = self.ai_service.calculate_readiness_score(
                tender_requirements, 
                company_profile_data
            )
            
            print("✅ Readiness scoring successful!")
            print(f"   - Suitability Score: {result['suitability_score']}/100")
            print(f"   - Recommendation: {result['recommendation']}")
            print(f"   - Checklist items: {len(result['checklist'])}")
            print(f"   - Scoring breakdown: {result['scoring_breakdown']}")
            
            # Test MongoDB storage for readiness scores
            print("💾 Testing readiness score storage...")
            storage_result = mongodb_service.store_readiness_score(
                tender_id=999,
                company_profile_id=1,
                team_id=1,
                score_data=result,
                user_id=1
            )
            
            if storage_result:
                print("✅ Readiness score storage test passed")
            else:
                print("❌ Readiness score storage test failed")
            
            # Verify score makes sense
            if 0 <= result['suitability_score'] <= 100:
                print("✅ Score validation passed")
                return True
            else:
                print("❌ Score validation failed - score out of range")
                return False
                
        except Exception as e:
            print(f"❌ Readiness scoring test failed: {e}")
            return False

    def test_readiness_scorer_integration(self):
        """Test integration with the ReadinessScorer class"""
        print("\n" + "="*60)
        print("🧪 TEST 5: READINESS SCORER INTEGRATION")
        print("="*60)
        
        try:
            # Get a sample company profile from database or create mock
            company_profile = self.db.query(CompanyProfile).first()
            if not company_profile:
                print("⚠️  No company profiles in database, using mock data")
                # Create a mock company profile object
                class MockCompanyProfile:
                    def __init__(self):
                        self.industry_sector = "Construction"
                        self.services_provided = "Construction services"
                        self.certifications = {"CIDB": "Grade 7", "BBBEE": "Level 2"}
                        self.geographic_coverage = ["Gauteng", "Western Cape"]
                        self.years_experience = 10
                        self.contact_email = "test@test.com"
                        self.contact_phone = "0123456789"
                
                company_profile = MockCompanyProfile()
            
            # Sample tender data
            tender_description = """
            Construction of government office building. Required: CIDB Grade 6, 
            5+ years experience, operations in Gauteng. Budget: R5-10 million.
            """
            tender_title = "Government Office Building Construction"
            
            print("🔄 Testing readiness scorer integration...")
            
            # Extract requirements
            requirements = self.readiness_scorer.extract_tender_requirements(
                tender_description, 
                tender_title
            )
            
            print(f"   - Extracted requirements: {len(requirements)} fields")
            
            # Calculate score
            score_result = self.readiness_scorer.calculate_suitability_score(
                company_profile,
                requirements
            )
            
            print("✅ Readiness scorer integration successful!")
            print(f"   - Suitability Score: {score_result['suitability_score']}/100")
            print(f"   - Recommendation: {score_result['recommendation']}")
            print(f"   - Checklist items: {len(score_result['checklist'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ Readiness scorer integration test failed: {e}")
            return False

    def test_mongodb_analytics(self):
        """Test MongoDB analytics functionality"""
        print("\n" + "="*60)
        print("🧪 TEST 6: MONGODB ANALYTICS PIPELINE")
        print("="*60)
        
        try:
            print("📊 Testing MongoDB analytics...")
            
            # Test tender analytics
            tender_analytics = mongodb_service.get_tender_analytics()
            print(f"   - Tender analytics: {tender_analytics}")
            
            # Test popular certifications
            popular_certs = mongodb_service.get_popular_certifications()
            print(f"   - Popular certifications: {len(popular_certs)} found")
            
            # Test industry breakdown
            industry_breakdown = mongodb_service.get_industry_breakdown()
            print(f"   - Industry breakdown: {len(industry_breakdown)} sectors")
            
            # Test activity logging
            log_result = mongodb_service.log_user_activity(
                user_id=1,
                team_id=1,
                action="integration_test",
                details={"test": "mongodb_analytics"}
            )
            print(f"   - Activity logging: {'✅' if log_result else '❌'}")
            
            # Test analytics caching
            cache_data = {"test": "data", "timestamp": datetime.utcnow().isoformat()}
            cache_result = mongodb_service.cache_analytics(
                "test_analytics",
                cache_data,
                expiry_hours=1
            )
            print(f"   - Analytics caching: {'✅' if cache_result else '❌'}")
            
            # Test cache retrieval
            cached_data = mongodb_service.get_cached_analytics("test_analytics")
            print(f"   - Cache retrieval: {'✅' if cached_data else '❌'}")
            
            print("✅ MongoDB analytics tests completed")
            return True
            
        except Exception as e:
            print(f"❌ MongoDB analytics test failed: {e}")
            return False

    def test_complete_pipeline(self):
        """Test the complete AI pipeline from document to readiness score"""
        print("\n" + "="*60)
        print("🧪 TEST 7: COMPLETE AI PIPELINE")
        print("="*60)
        
        try:
            print("🚀 Testing complete AI pipeline...")
            
            # Step 1: Document Processing
            document_url = "https://example.com/complete-test.pdf"
            doc_result = self.document_processor.process_document(document_url)
            
            if "error" in doc_result:
                print("❌ Pipeline failed at document processing")
                return False
            print("✅ Step 1: Document processing completed")
            
            # Step 2: AI Analysis
            extracted_text = doc_result.get("extracted_text_sample", "")
            ai_result = self.ai_service.analyze_document_content(extracted_text)
            print("✅ Step 2: AI analysis completed")
            
            # Step 3: Readiness Scoring (with mock company profile)
            company_profile = {
                "company_name": "Pipeline Test Company",
                "industry_sector": "Construction",
                "services_provided": "Comprehensive construction services",
                "certifications": {"CIDB": "Grade 7", "BBBEE": "Level 2"},
                "geographic_coverage": ["Gauteng", "Western Cape"],
                "years_experience": 7,
                "contact_email": "test@pipeline.com",
                "contact_phone": "+27 11 999 8888"
            }
            
            readiness_result = self.ai_service.calculate_readiness_score(
                ai_result["requirements"],
                company_profile
            )
            print("✅ Step 3: Readiness scoring completed")
            
            # Step 4: MongoDB Storage
            storage_success = mongodb_service.store_ai_summary(
                tender_id=1000,
                document_url=document_url,
                summary=ai_result["summary"],
                key_points=ai_result["key_points"],
                user_id=1,
                team_id=1
            )
            
            if storage_success:
                print("✅ Step 4: MongoDB storage completed")
            else:
                print("❌ Pipeline failed at MongoDB storage")
                return False
            
            print("🎉 COMPLETE AI PIPELINE TEST SUCCESSFUL!")
            print(f"   - Final Readiness Score: {readiness_result['suitability_score']}/100")
            print(f"   - Recommendation: {readiness_result['recommendation']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Complete pipeline test failed: {e}")
            return False

    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 STARTING COMPREHENSIVE AI PIPELINE INTEGRATION TESTS")
        print("="*80)
        
        test_results = []
        
        # Run individual tests
        test_results.append(("Document Processing", self.test_document_processing()))
        test_results.append(("AI Analysis", self.test_ai_analysis()))
        test_results.append(("AI Summarization", self.test_ai_summarization_endpoint()))
        test_results.append(("Readiness Scoring", self.test_readiness_scoring()))
        test_results.append(("Readiness Scorer Integration", self.test_readiness_scorer_integration()))
        test_results.append(("MongoDB Analytics", self.test_mongodb_analytics()))
        test_results.append(("Complete Pipeline", self.test_complete_pipeline()))
        
        # Print summary
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name:<30} {status}")
            if result:
                passed += 1
        
        print(f"\n🎯 RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! AI pipeline is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Please check the implementation.")
            return False

    def cleanup(self):
        """Clean up test data"""
        try:
            # Remove test data from MongoDB
            mongodb_service.db.ai_summaries.delete_many({"tender_id": {"$in": [999, 1000]}})
            mongodb_service.db.readiness_scores.delete_many({"tender_id": {"$in": [999, 1000]}})
            mongodb_service.db.analytics_cache.delete_many({"analytics_type": "test_analytics"})
            print("🧹 Test data cleaned up from MongoDB")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")

def main():
    """Main test runner"""
    tester = AIPipelineTester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"💥 Test runner crashed: {e}")
        return 1
    finally:
        tester.cleanup()
        tester.db.close()

if __name__ == "__main__":
    # Run the tests
    exit_code = main()
    sys.exit(exit_code)