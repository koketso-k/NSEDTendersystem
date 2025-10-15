# test_complete_pipeline.py - COMPREHENSIVE AI PIPELINE TEST

import sys
import os
import asyncio
from datetime import datetime
import time

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from document_processor import DocumentProcessor
from ai_services import AIService
from readiness_scorer import ReadinessScorer
from database import SessionLocal, CompanyProfile, Tender
from mongodb_service import mongodb_service
from ocds_client import OCDSClient

class CompletePipelineTester:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.ai_service = AIService()
        self.readiness_scorer = ReadinessScorer()
        self.ocds_client = OCDSClient()
        self.db = SessionLocal()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append((test_name, success, details))
        print(f"   {test_name:<40} {status}")
        if details:
            print(f"      📝 {details}")

    def test_1_document_processing(self):
        """Test document processing pipeline"""
        print("\n" + "="*60)
        print("🧪 TEST 1: DOCUMENT PROCESSING PIPELINE")
        print("="*60)
        
        try:
            # Test with a sample document URL
            test_url = "https://www.etenders.gov.za/sample-tender.pdf"
            
            print("📄 Processing sample tender document...")
            start_time = time.time()
            result = self.document_processor.process_document(test_url)
            processing_time = time.time() - start_time
            
            if "error" in result:
                self.log_test("Document Processing", False, f"Error: {result['error']}")
                return False
            
            # Validate results
            checks = [
                ("Summary generated", len(result.get('summary', '')) > 50),
                ("Key points extracted", len(result.get('key_points', {})) > 0),
                ("Text extracted", result.get('original_text_length', 0) > 100),
                ("Reasonable processing time", processing_time < 10.0)
            ]
            
            all_passed = True
            for check_name, check_result in checks:
                if not check_result:
                    all_passed = False
                self.log_test(check_name, check_result)
            
            if all_passed:
                self.log_test("Document Processing Pipeline", True, 
                            f"Processed {result['original_text_length']} chars in {processing_time:.2f}s")
                return True
            else:
                self.log_test("Document Processing Pipeline", False, "Some checks failed")
                return False
                
        except Exception as e:
            self.log_test("Document Processing", False, f"Exception: {str(e)}")
            return False

    def test_2_ai_analysis(self):
        """Test AI analysis pipeline"""
        print("\n" + "="*60)
        print("🧪 TEST 2: AI ANALYSIS PIPELINE")
        print("="*60)
        
        try:
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
            """
            
            print("🤖 Running AI analysis on sample tender...")
            start_time = time.time()
            result = self.ai_service.analyze_document_content(sample_text)
            processing_time = time.time() - start_time
            
            # Validate AI analysis results
            checks = [
                ("Industry detection", result.get('industry_sector') == 'Construction'),
                ("Complexity scoring", 0 <= result.get('complexity_score', 0) <= 100),
                ("Requirements extracted", len(result.get('requirements', {}).get('required_certifications', [])) > 0),
                ("Experience detection", result.get('requirements', {}).get('experience_years', 0) == 5),
                ("Budget estimation", 'R' in result.get('budget_indication', '')),
                ("Confidence level", result.get('analysis_confidence') in ['High', 'Medium', 'Low'])
            ]
            
            all_passed = True
            for check_name, check_result in checks:
                if not check_result:
                    all_passed = False
                self.log_test(check_name, check_result)
            
            if all_passed:
                self.log_test("AI Analysis Pipeline", True, 
                            f"Industry: {result['industry_sector']}, Score: {result['complexity_score']}, Time: {processing_time:.2f}s")
                return True
            else:
                self.log_test("AI Analysis Pipeline", False, "Some AI analysis checks failed")
                return False
                
        except Exception as e:
            self.log_test("AI Analysis", False, f"Exception: {str(e)}")
            return False

    def test_3_readiness_scoring(self):
        """Test readiness scoring pipeline"""
        print("\n" + "="*60)
        print("🧪 TEST 3: READINESS SCORING PIPELINE")
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
                "required_provinces": ["Gauteng"],
                "min_experience": 5,
                "industry_sector": "Construction",
                "technical_requirements": ["Civil works experience", "Building construction expertise"]
            }
            
            print("📈 Testing readiness scoring...")
            start_time = time.time()
            
            # Test with AI service method
            ai_result = self.ai_service.calculate_readiness_score(
                tender_requirements, 
                company_profile_data
            )
            
            # Test with readiness scorer method
            class MockCompanyProfile:
                def __init__(self, data):
                    for key, value in data.items():
                        setattr(self, key, value)
            
            mock_profile = MockCompanyProfile(company_profile_data)
            scorer_result = self.readiness_scorer.calculate_suitability_score(
                mock_profile,
                tender_requirements
            )
            
            processing_time = time.time() - start_time
            
            # Validate scoring results
            checks = [
                ("AI Service Score Range", 0 <= ai_result.get('suitability_score', 0) <= 100),
                ("Scorer Score Range", 0 <= scorer_result.get('suitability_score', 0) <= 100),
                ("AI Checklist Generated", len(ai_result.get('checklist', {})) > 0),
                ("Scorer Checklist Generated", len(scorer_result.get('checklist', {})) > 0),
                ("Recommendation Provided", len(ai_result.get('recommendation', '')) > 10),
                ("Scoring Breakdown", len(ai_result.get('scoring_breakdown', {})) > 0)
            ]
            
            all_passed = True
            for check_name, check_result in checks:
                if not check_result:
                    all_passed = False
                self.log_test(check_name, check_result)
            
            if all_passed:
                self.log_test("Readiness Scoring Pipeline", True, 
                            f"AI Score: {ai_result['suitability_score']}, Scorer Score: {scorer_result['suitability_score']}, Time: {processing_time:.2f}s")
                return True
            else:
                self.log_test("Readiness Scoring Pipeline", False, "Some scoring checks failed")
                return False
                
        except Exception as e:
            self.log_test("Readiness Scoring", False, f"Exception: {str(e)}")
            return False

    def test_4_mongodb_integration(self):
        """Test MongoDB integration"""
        print("\n" + "="*60)
        print("🧪 TEST 4: MONGODB INTEGRATION")
        print("="*60)
        
        try:
            print("💾 Testing MongoDB storage and retrieval...")
            
            # Test AI summary storage
            test_summary_data = {
                "summary": "Test summary for AI pipeline integration test",
                "key_points": {
                    "objective": "Test objective",
                    "scope": "Test scope",
                    "deadline": "Test deadline"
                }
            }
            
            storage_result = mongodb_service.store_ai_summary(
                tender_id=9999,
                document_url="https://test.com/document.pdf",
                summary=test_summary_data["summary"],
                key_points=test_summary_data["key_points"],
                user_id=1,
                team_id=1
            )
            
            # Test readiness score storage
            test_score_data = {
                "suitability_score": 85.5,
                "checklist": {"Test requirement": True},
                "recommendation": "Test recommendation",
                "scoring_breakdown": {"certifications": 90, "experience": 80}
            }
            
            score_storage = mongodb_service.store_readiness_score(
                tender_id=9999,
                company_profile_id=1,
                team_id=1,
                score_data=test_score_data,
                user_id=1
            )
            
            # Test activity logging
            activity_log = mongodb_service.log_user_activity(
                user_id=1,
                team_id=1,
                action="pipeline_test",
                details={"test": "complete_pipeline"}
            )
            
            # Test retrieval
            retrieved_summary = mongodb_service.get_tender_summary(9999)
            analytics = mongodb_service.get_tender_analytics()
            
            checks = [
                ("AI Summary Storage", storage_result),
                ("Readiness Score Storage", score_storage),
                ("Activity Logging", activity_log),
                ("Summary Retrieval", retrieved_summary is not None),
                ("Analytics Query", analytics is not None)
            ]
            
            all_passed = True
            for check_name, check_result in checks:
                if not check_result:
                    all_passed = False
                self.log_test(check_name, check_result)
            
            # Cleanup test data
            try:
                mongodb_service.db.ai_summaries.delete_many({"tender_id": 9999})
                mongodb_service.db.readiness_scores.delete_many({"tender_id": 9999})
            except:
                pass
            
            if all_passed:
                self.log_test("MongoDB Integration", True, "All storage and retrieval operations successful")
                return True
            else:
                self.log_test("MongoDB Integration", False, "Some MongoDB operations failed")
                return False
                
        except Exception as e:
            self.log_test("MongoDB Integration", False, f"Exception: {str(e)}")
            return False

    def test_5_ocds_integration(self):
        """Test OCDS client integration"""
        print("\n" + "="*60)
        print("🧪 TEST 5: OCDS CLIENT INTEGRATION")
        print("="*60)
        
        try:
            print("🌐 Testing OCDS API integration...")
            
            # Test API status
            api_status = self.ocds_client.get_api_status()
            
            # Test tender fetching (small limit for testing)
            tenders = self.ocds_client.fetch_real_tenders(limit=3)
            
            # Test data transformation
            transformed_tenders = []
            for tender in tenders[:2]:  # Test first 2 tenders
                transformed = self.ocds_client.transform_ocds_to_tender(tender)
                if transformed:
                    transformed_tenders.append(transformed)
            
            checks = [
                ("API Status Check", api_status is not None),
                ("Tender Fetching", len(tenders) > 0),
                ("Data Transformation", len(transformed_tenders) > 0),
                ("Tender Structure", all(hasattr(t, 'title') for t in transformed_tenders)),
                ("Budget Extraction", all(hasattr(t, 'budget_range') for t in transformed_tenders))
            ]
            
            all_passed = True
            for check_name, check_result in checks:
                if not check_result:
                    all_passed = False
                self.log_test(check_name, check_result)
            
            if all_passed:
                self.log_test("OCDS Integration", True, 
                            f"Fetched {len(tenders)} tenders, transformed {len(transformed_tenders)}")
                return True
            else:
                self.log_test("OCDS Integration", False, "Some OCDS operations failed")
                return False
                
        except Exception as e:
            self.log_test("OCDS Integration", False, f"Exception: {str(e)}")
            return False

    def test_6_complete_pipeline(self):
        """Test the complete AI pipeline from end to end"""
        print("\n" + "="*60)
        print("🧪 TEST 6: COMPLETE AI PIPELINE")
        print("="*60)
        
        try:
            print("🚀 Testing complete AI pipeline from document to readiness score...")
            start_time = time.time()
            
            # Step 1: Document Processing
            document_url = "https://www.etenders.gov.za/complete-test.pdf"
            doc_result = self.document_processor.process_document(document_url)
            
            if "error" in doc_result:
                self.log_test("Complete Pipeline - Document Processing", False, doc_result["error"])
                return False
            
            self.log_test("Step 1 - Document Processing", True, 
                         f"Processed {doc_result['original_text_length']} characters")
            
            # Step 2: AI Analysis
            extracted_text = doc_result.get("extracted_text_sample", "")
            ai_result = self.ai_service.analyze_document_content(extracted_text)
            
            self.log_test("Step 2 - AI Analysis", True, 
                         f"Industry: {ai_result['industry_sector']}, Complexity: {ai_result['complexity_score']}")
            
            # Step 3: Readiness Scoring
            company_profile = {
                "company_name": "Complete Pipeline Test Co",
                "industry_sector": "Construction",
                "services_provided": "Comprehensive construction and engineering services",
                "certifications": {"CIDB": "Grade 7", "BBBEE": "Level 2", "SARS": "true"},
                "geographic_coverage": ["Gauteng", "Western Cape"],
                "years_experience": 7,
                "contact_email": "test@complete-pipeline.com",
                "contact_phone": "+27 11 999 8888"
            }
            
            readiness_result = self.ai_service.calculate_readiness_score(
                ai_result["requirements"],
                company_profile
            )
            
            self.log_test("Step 3 - Readiness Scoring", True, 
                         f"Score: {readiness_result['suitability_score']}/100")
            
            # Step 4: MongoDB Storage
            storage_success = mongodb_service.store_ai_summary(
                tender_id=10000,
                document_url=document_url,
                summary=ai_result["summary"],
                key_points=ai_result["key_points"],
                user_id=1,
                team_id=1
            )
            
            score_storage = mongodb_service.store_readiness_score(
                tender_id=10000,
                company_profile_id=1,
                team_id=1,
                score_data=readiness_result,
                user_id=1
            )
            
            self.log_test("Step 4 - Data Storage", storage_success and score_storage,
                         f"AI Summary: {'✅' if storage_success else '❌'}, "
                         f"Readiness Score: {'✅' if score_storage else '❌'}")
            
            total_time = time.time() - start_time
            
            # Final validation
            final_checks = [
                ("Document Processing Successful", "error" not in doc_result),
                ("AI Analysis Completed", "industry_sector" in ai_result),
                ("Readiness Score Calculated", "suitability_score" in readiness_result),
                ("Data Storage Successful", storage_success and score_storage),
                ("Reasonable Total Time", total_time < 30.0)
            ]
            
            all_passed = all(check[1] for check in final_checks)
            
            for check_name, check_result in final_checks:
                self.log_test(check_name, check_result)
            
            if all_passed:
                self.log_test("COMPLETE AI PIPELINE", True, 
                            f"🎉 Success! Completed in {total_time:.2f}s - "
                            f"Final Score: {readiness_result['suitability_score']}/100")
                return True
            else:
                self.log_test("COMPLETE AI PIPELINE", False, 
                            f"Pipeline completed with issues in {total_time:.2f}s")
                return False
                
        except Exception as e:
            self.log_test("Complete Pipeline", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 STARTING COMPLETE AI PIPELINE INTEGRATION TESTS")
        print("="*80)
        print("📋 Testing all components: Document Processing → AI Analysis → Readiness Scoring → Data Storage")
        print("="*80)
        
        # Run individual tests
        tests = [
            ("Document Processing", self.test_1_document_processing),
            ("AI Analysis", self.test_2_ai_analysis),
            ("Readiness Scoring", self.test_3_readiness_scoring),
            ("MongoDB Integration", self.test_4_mongodb_integration),
            ("OCDS Integration", self.test_5_ocds_integration),
            ("Complete Pipeline", self.test_6_complete_pipeline)
        ]
        
        for test_name, test_func in tests:
            test_func()
        
        # Print summary
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        print(f"\n🎯 OVERALL RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        # Print detailed results
        print("\n📝 DETAILED RESULTS:")
        for test_name, success, details in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {test_name:<50} {status}")
            if details and not success:
                print(f"      💡 {details}")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! The complete AI pipeline is working correctly.")
            print("   The system is ready for production use with:")
            print("   ✅ Document processing and text extraction")
            print("   ✅ AI-powered analysis and requirement extraction") 
            print("   ✅ Readiness scoring and recommendation")
            print("   ✅ MongoDB data storage and analytics")
            print("   ✅ OCDS API integration for real tender data")
            return True
        else:
            print(f"\n⚠️  {total - passed} tests failed. Please check the implementation.")
            return False

    def cleanup(self):
        """Clean up test data"""
        try:
            # Remove test data from MongoDB
            mongodb_service.db.ai_summaries.delete_many({"tender_id": {"$in": [9999, 10000]}})
            mongodb_service.db.readiness_scores.delete_many({"tender_id": {"$in": [9999, 10000]}})
            print("🧹 Test data cleaned up from MongoDB")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
        finally:
            self.db.close()

def main():
    """Main test runner"""
    tester = CompletePipelineTester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"💥 Test runner crashed: {e}")
        return 1
    finally:
        tester.cleanup()

if __name__ == "__main__":
    # Run the complete test suite
    exit_code = main()
    sys.exit(exit_code)