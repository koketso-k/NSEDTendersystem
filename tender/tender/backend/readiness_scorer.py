# readiness_scorer.py - COMPLETE FIXED VERSION WITH ENHANCED SCORING

from typing import Dict, Any, List, Tuple
from database import CompanyProfile
import json
import re
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class ReadinessScorer:
    def __init__(self):
        # Weights for different scoring components
        self.weights = {
            "certifications": 0.30,    # 30% - Most important for government tenders
            "experience": 0.25,        # 25% - Experience is crucial
            "geographic_coverage": 0.20, # 20% - Geographic requirements
            "sector_match": 0.15,      # 15% - Industry alignment
            "capacity": 0.10           # 10% - Basic company capacity
        }
        
        # South African specific certifications and their importance
        self.certification_importance = {
            "cidb": 10,      # Construction Industry Development Board
            "bbbee": 8,      # Broad-Based Black Economic Empowerment
            "sars": 7,       # Tax Compliance
            "csd": 6,        # Central Supplier Database
            "psira": 5,      # Private Security Industry Regulatory Authority
            "iso": 4,        # ISO Certifications
            "sans": 4,       # South African National Standards
        }
        
        # Industry sector mappings for better matching
        self.industry_mappings = {
            "construction": ["civil", "engineering", "building", "infrastructure", "roads", "bridges"],
            "it_services": ["technology", "software", "digital", "computer", "system", "network"],
            "security": ["protection", "guarding", "surveillance", "patrol", "monitoring"],
            "cleaning": ["sanitation", "hygiene", "maintenance", "janitorial", "waste"],
            "transport": ["logistics", "delivery", "shipping", "freight", "courier"],
            "healthcare": ["medical", "health", "hospital", "clinic", "patient"],
            "education": ["training", "school", "university", "learning", "curriculum"],
            "agriculture": ["farming", "crops", "livestock", "irrigation", "harvest"]
        }

    def extract_tender_requirements(self, tender_description: str, tender_title: str = "") -> Dict[str, Any]:
        """
        Enhanced requirement extraction with South African context
        """
        requirements = {
            "required_certifications": [],
            "required_provinces": [],
            "min_experience": 0,
            "industry_sector": "",
            "technical_requirements": [],
            "financial_requirements": [],
            "submission_requirements": [],
            "deadline_info": "",
            "budget_indication": ""
        }

        # Combine title and description for analysis
        text = (tender_title + " " + (tender_description or "")).lower()
        
        logger.info(f"🔍 Extracting requirements from tender text (length: {len(text)})")

        # Enhanced certification extraction for South African context
        cert_patterns = {
            "CIDB": [
                r"cidb.*?grade\s*(\w+)",
                r"cidb.*?(\d+[a-z]*)",
                r"construction industry development board",
                r"grade\s*(\w+).*?cidb"
            ],
            "BBBEE": [
                r"bbbee.*?level\s*(\d+)",
                r"b-bbee.*?level\s*(\d+)",
                r"broad-based black economic empowerment",
                r"bbbee",
                r"b-bbee"
            ],
            "SARS": [
                r"sars.*?tax",
                r"tax clearance",
                r"tax certificate",
                r"tax compliant"
            ],
            "CSD": [
                r"csd",
                r"central supplier database",
                r"supplier database"
            ],
            "PSIRA": [
                r"psira",
                r"private security",
                r"security industry"
            ],
            "ISO": [
                r"iso.*?(\d+)",
                r"iso.*?certification",
                r"iso.*?standard"
            ],
            "SANS": [
                r"sans.*?(\d+)",
                r"south african national standard"
            ]
        }

        for cert, patterns in cert_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    requirement = f"{cert}"
                    if matches[0] and str(matches[0]).strip():
                        requirement += f": {matches[0]}"
                    requirements["required_certifications"].append(requirement)
                    break

        # Enhanced experience extraction
        exp_patterns = [
            r"(\d+)\s*years?\s*experience",
            r"minimum\s*of\s*(\d+)\s*years",
            r"at least\s*(\d+)\s*years",
            r"(\d+)\s*years?\s*in.*?experience",
            r"experience.*?(\d+)\s*years",
            r"(\d+).*?years.*?experience"
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    years = int(matches[0])
                    if years > requirements["min_experience"]:
                        requirements["min_experience"] = years
                        logger.debug(f"📅 Found experience requirement: {years} years")
                except (ValueError, TypeError):
                    continue

        # Enhanced geographic requirements for South African provinces
        provinces = [
            "gauteng", "western cape", "kwazulu-natal", "eastern cape",
            "limpopo", "mpumalanga", "north west", "free state", "northern cape"
        ]
        
        for province in provinces:
            if province in text:
                requirements["required_provinces"].append(province.title())
                logger.debug(f"📍 Found geographic requirement: {province}")

        # Enhanced industry sector detection
        detected_sector = self._detect_industry_sector(text, tender_title)
        requirements["industry_sector"] = detected_sector
        logger.debug(f"🏭 Detected industry sector: {detected_sector}")

        # Extract technical requirements
        technical_indicators = [
            "software", "hardware", "equipment", "system", "network",
            "infrastructure", "tools", "machinery", "vehicles", "facilities",
            "technology", "digital", "automation"
        ]
        
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            if any(indicator in sentence for indicator in technical_indicators):
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 10 and clean_sentence not in requirements["technical_requirements"]:
                    requirements["technical_requirements"].append(clean_sentence)

        # Extract financial requirements
        financial_patterns = [
            r"budget.*?r\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
            r"amount.*?r\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
            r"value.*?r\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
            r"r\s*(\d+(?:,\d{3})*(?:\.\d{2})?)"
        ]
        
        for pattern in financial_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    amount = float(matches[0].replace(',', ''))
                    if amount > 1000000:
                        requirements["budget_indication"] = f"R{amount/1000000:.1f}M"
                    elif amount > 1000:
                        requirements["budget_indication"] = f"R{amount/1000:.0f}K"
                    else:
                        requirements["budget_indication"] = f"R{amount:,.0f}"
                    break
                except (ValueError, TypeError):
                    continue

        # Extract submission requirements
        submission_keywords = ["proposal", "quotation", "bid", "tender", "document", 
                              "submission", "application", "form", "certificate"]
        
        for sentence in sentences:
            if any(keyword in sentence for keyword in submission_keywords):
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 10 and clean_sentence not in requirements["submission_requirements"]:
                    requirements["submission_requirements"].append(clean_sentence)

        # Extract deadline information
        deadline_patterns = [
            r"closing\s*date.*?(\d{1,2}\s+\w+\s+\d{4})",
            r"deadline.*?(\d{1,2}\s+\w+\s+\d{4})",
            r"submission.*?(\d{1,2}\s+\w+\s+\d{4})",
            r"due.*?(\d{1,2}\s+\w+\s+\d{4})"
        ]
        
        for pattern in deadline_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                requirements["deadline_info"] = matches[0]
                break

        logger.info(f"✅ Extracted {len(requirements['required_certifications'])} certifications, "
                   f"{len(requirements['required_provinces'])} provinces, "
                   f"{requirements['min_experience']} years experience")

        return requirements

    def _detect_industry_sector(self, text: str, title: str) -> str:
        """Detect industry sector from text and title"""
        combined_text = (title + " " + text).lower()
        
        sector_scores = {}
        
        for sector, keywords in self.industry_mappings.items():
            score = 0
            for keyword in keywords:
                if keyword in combined_text:
                    score += 2  # Base score for keyword match
                    # Bonus for multiple occurrences
                    occurrences = combined_text.count(keyword)
                    score += min(occurrences * 0.5, 5)  # Max 5 bonus for frequency
                    
                    # Bonus for keyword in title
                    if keyword in title.lower():
                        score += 3
            
            sector_scores[sector] = score
        
        # Get best matching sector
        if sector_scores:
            best_sector = max(sector_scores.items(), key=lambda x: x[1])
            if best_sector[1] > 2:  # Minimum threshold
                return best_sector[0].replace("_", " ").title()
        
        return "General Services"

    def calculate_suitability_score(self,
                                  company_profile: CompanyProfile,
                                  tender_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive suitability score with detailed breakdown
        """
        logger.info(f"📊 Calculating suitability score for company profile {company_profile.id}")
        
        try:
            score_breakdown = {}
            total_score = 0
            checklist = {}

            # 1. Certification Match (30%)
            cert_score, cert_checklist = self._calculate_certification_score(
                tender_requirements, company_profile
            )
            score_breakdown["certifications"] = cert_score
            total_score += cert_score * self.weights["certifications"]
            checklist.update(cert_checklist)

            # 2. Experience Match (25%)
            exp_score, exp_checklist = self._calculate_experience_score(
                tender_requirements, company_profile
            )
            score_breakdown["experience"] = exp_score
            total_score += exp_score * self.weights["experience"]
            checklist.update(exp_checklist)

            # 3. Geographic Coverage (20%)
            geo_score, geo_checklist = self._calculate_geographic_score(
                tender_requirements, company_profile
            )
            score_breakdown["geographic_coverage"] = geo_score
            total_score += geo_score * self.weights["geographic_coverage"]
            checklist.update(geo_checklist)

            # 4. Sector Match (15%)
            sector_score, sector_checklist = self._calculate_sector_score(
                tender_requirements, company_profile
            )
            score_breakdown["sector_match"] = sector_score
            total_score += sector_score * self.weights["sector_match"]
            checklist.update(sector_checklist)

            # 5. Capacity Assessment (10%)
            capacity_score, capacity_checklist = self._calculate_capacity_score(company_profile)
            score_breakdown["capacity"] = capacity_score
            total_score += capacity_score * self.weights["capacity"]
            checklist.update(capacity_checklist)

            # Final score calculation
            final_score = min(round(total_score), 100)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(final_score, checklist)
            
            # Calculate confidence level
            confidence = self._calculate_confidence_level(final_score, checklist)

            logger.info(f"🎯 Final suitability score: {final_score}/100 (Confidence: {confidence})")

            return {
                "suitability_score": final_score,
                "checklist": checklist,
                "recommendation": recommendation,
                "scoring_breakdown": score_breakdown,
                "tender_requirements": tender_requirements,
                "confidence_level": confidence,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating suitability score: {e}")
            return self._get_error_response(str(e))

    def _calculate_certification_score(self, tender_req: Dict[str, Any], company_profile: CompanyProfile) -> Tuple[float, Dict[str, bool]]:
        """Calculate certification match score with detailed checklist"""
        required_certs = tender_req.get("required_certifications", [])
        company_certs = self._get_company_certifications(company_profile)
        
        checklist = {}
        
        if not required_certs:
            # No certification requirements - full points
            checklist["No certification requirements"] = True
            return 100.0, checklist
        
        matched_certs = 0
        total_required = len(required_certs)
        
        for required_cert in required_certs:
            cert_name = required_cert.split(":")[0].strip().upper() if ":" in required_cert else required_cert.upper()
            has_cert = self._has_certification(company_certs, cert_name)
            
            checklist[f"Has {cert_name} certification"] = has_cert
            
            if has_cert:
                matched_certs += 1
                # Check if specific grade/level matches
                if ":" in required_cert:
                    required_level = required_cert.split(":")[1].strip()
                    level_matches = self._check_certification_level(company_certs, cert_name, required_level)
                    if level_matches:
                        matched_certs += 0.5  # Bonus for exact level match
        
        score = (matched_certs / total_required) * 100 if total_required > 0 else 100
        return min(score, 100), checklist

    def _calculate_experience_score(self, tender_req: Dict[str, Any], company_profile: CompanyProfile) -> Tuple[float, Dict[str, bool]]:
        """Calculate experience match score"""
        required_exp = tender_req.get("min_experience", 0)
        company_exp = company_profile.years_experience or 0
        
        checklist = {
            f"Meets {required_exp} years experience requirement": company_exp >= required_exp
        }
        
        if required_exp == 0:
            # No experience requirement - full points
            checklist["No experience requirements"] = True
            return 100.0, checklist
        
        if company_exp >= required_exp:
            score = 100.0
        else:
            # Partial credit based on how close they are
            ratio = company_exp / required_exp
            if ratio >= 0.8:
                score = 80.0  # Close but not quite
            elif ratio >= 0.6:
                score = 60.0
            elif ratio >= 0.4:
                score = 40.0
            else:
                score = 20.0
        
        # Bonus for exceeding requirements
        if company_exp > required_exp + 5:
            score = min(score + 10, 100)
            checklist["Exceeds experience requirements"] = True
        
        return score, checklist

    def _calculate_geographic_score(self, tender_req: Dict[str, Any], company_profile: CompanyProfile) -> Tuple[float, Dict[str, bool]]:
        """Calculate geographic coverage score"""
        required_provinces = tender_req.get("required_provinces", [])
        company_coverage = self._get_company_geographic_coverage(company_profile)
        
        checklist = {}
        
        if not required_provinces:
            # No geographic requirements - full points
            checklist["No geographic requirements"] = True
            return 100.0, checklist
        
        matched_provinces = 0
        
        for province in required_provinces:
            operates_there = province in company_coverage
            checklist[f"Operates in {province}"] = operates_there
            
            if operates_there:
                matched_provinces += 1
        
        score = (matched_provinces / len(required_provinces)) * 100 if required_provinces else 100
        return score, checklist

    def _calculate_sector_score(self, tender_req: Dict[str, Any], company_profile: CompanyProfile) -> Tuple[float, Dict[str, bool]]:
        """Calculate industry sector match score"""
        tender_sector = tender_req.get("industry_sector", "").lower()
        company_sector = (company_profile.industry_sector or "").lower()
        company_services = (company_profile.services_provided or "").lower()
        
        checklist = {}
        
        if not tender_sector:
            # No specific sector requirement - neutral score
            checklist["No specific industry requirements"] = True
            return 50.0, checklist
        
        # Direct sector match
        direct_match = (
            tender_sector in company_sector or 
            company_sector in tender_sector or
            tender_sector in company_services
        )
        
        checklist[f"Industry matches {tender_sector.title()}"] = direct_match
        
        if direct_match:
            return 100.0, checklist
        
        # Check for related sectors
        related_match = False
        for main_sector, related_terms in self.industry_mappings.items():
            if tender_sector in main_sector:
                for term in related_terms:
                    if term in company_services or term in company_sector:
                        related_match = True
                        checklist[f"Services related to {tender_sector.title()}"] = True
                        break
                if related_match:
                    break
        
        if related_match:
            return 70.0, checklist
        
        # Very weak match
        return 30.0, checklist

    def _calculate_capacity_score(self, company_profile: CompanyProfile) -> Tuple[float, Dict[str, bool]]:
        """Calculate company capacity score"""
        checklist = {}
        score_factors = []
        
        # Contact information
        has_contact = bool(company_profile.contact_email) and bool(company_profile.contact_phone)
        checklist["Has complete contact information"] = has_contact
        score_factors.append(40 if has_contact else 0)
        
        # Services description
        has_detailed_services = bool(company_profile.services_provided and len(company_profile.services_provided.strip()) > 50)
        checklist["Has detailed services description"] = has_detailed_services
        score_factors.append(30 if has_detailed_services else 0)
        
        # Company name
        has_company_name = bool(company_profile.company_name and len(company_profile.company_name.strip()) > 2)
        checklist["Has valid company name"] = has_company_name
        score_factors.append(30 if has_company_name else 0)
        
        score = sum(score_factors)
        return score, checklist

    def _get_company_certifications(self, company_profile: CompanyProfile) -> Dict[str, Any]:
        """Extract certifications from company profile"""
        certs = company_profile.certifications or {}
        
        # Handle different certification formats
        if isinstance(certs, str):
            try:
                certs = json.loads(certs)
            except (json.JSONDecodeError, TypeError):
                certs = {}
        
        return certs

    def _get_company_geographic_coverage(self, company_profile: CompanyProfile) -> List[str]:
        """Extract geographic coverage from company profile"""
        coverage = company_profile.geographic_coverage or []
        
        # Handle different geographic coverage formats
        if isinstance(coverage, str):
            try:
                coverage = json.loads(coverage)
            except (json.JSONDecodeError, TypeError):
                coverage = []
        
        return coverage

    def _has_certification(self, company_certs: Dict[str, Any], cert_name: str) -> bool:
        """Check if company has a specific certification"""
        cert_name_lower = cert_name.lower()
        
        for cert_key, cert_value in company_certs.items():
            if cert_name_lower in cert_key.lower():
                return bool(cert_value) and str(cert_value).strip() not in ['', 'false', 'no', '0']
        
        return False

    def _check_certification_level(self, company_certs: Dict[str, Any], cert_name: str, required_level: str) -> bool:
        """Check if certification level/grade matches requirement"""
        cert_name_lower = cert_name.lower()
        required_level_clean = required_level.lower().strip()
        
        for cert_key, cert_value in company_certs.items():
            if cert_name_lower in cert_key.lower():
                cert_value_str = str(cert_value).lower()
                return required_level_clean in cert_value_str
        
        return False

    def _generate_recommendation(self, score: float, checklist: Dict[str, bool]) -> str:
        """Generate recommendation based on score and checklist"""
        met_requirements = sum(checklist.values())
        total_requirements = len(checklist)
        success_rate = (met_requirements / total_requirements) * 100 if total_requirements > 0 else 0
        
        if score >= 90 and success_rate >= 90:
            return "🎯 EXCELLENT MATCH - Highly recommended to bid. Your company meets or exceeds all major requirements."
        elif score >= 75 and success_rate >= 75:
            return "✅ STRONG SUITABILITY - Good candidate for submission. Address minor gaps before bidding."
        elif score >= 60 and success_rate >= 60:
            return "⚠️ MODERATE SUITABILITY - Consider bidding after addressing key gaps in certifications or experience."
        elif score >= 40:
            return "🔶 LIMITED SUITABILITY - Significant gaps exist. Consider whether this tender aligns with your core capabilities."
        else:
            return "❌ LOW SUITABILITY - Not recommended for bidding. Focus on tenders that better match your company's profile."

    def _calculate_confidence_level(self, score: float, checklist: Dict[str, bool]) -> str:
        """Calculate confidence level of the scoring"""
        total_items = len(checklist)
        if total_items == 0:
            return "Low"
        
        definitive_items = sum(1 for item in checklist.values() if item is not None)
        confidence_ratio = definitive_items / total_items
        
        if confidence_ratio >= 0.8 and score > 70:
            return "High"
        elif confidence_ratio >= 0.6:
            return "Medium"
        else:
            return "Low"

    def _get_error_response(self, error_message: str) -> Dict[str, Any]:
        """Return error response when scoring fails"""
        return {
            "suitability_score": 0,
            "checklist": {"Error occurred during scoring": False},
            "recommendation": f"Unable to calculate score: {error_message}",
            "scoring_breakdown": {},
            "tender_requirements": {},
            "confidence_level": "Low",
            "calculated_at": datetime.utcnow().isoformat(),
            "error": error_message
        }

# Global instance
readiness_scorer = ReadinessScorer()

# Test function
def test_readiness_scorer():
    """Test the readiness scorer with sample data"""
    print("🧪 Testing Readiness Scorer...")
    
    scorer = ReadinessScorer()
    
    # Sample tender requirements
    tender_req = {
        "required_certifications": ["CIDB: Grade 7", "BBBEE: Level 2", "SARS Tax Clearance"],
        "required_provinces": ["Gauteng", "Western Cape"],
        "min_experience": 5,
        "industry_sector": "Construction",
        "technical_requirements": ["Civil works experience", "Building construction"],
        "budget_indication": "R5M - R10M"
    }
    
    # Sample company profile (mock)
    class MockCompanyProfile:
        def __init__(self):
            self.id = 1
            self.company_name = "Test Construction Co"
            self.industry_sector = "Construction"
            self.services_provided = "Civil engineering, building construction, infrastructure development"
            self.certifications = {"CIDB": "Grade 7", "BBBEE": "Level 2", "SARS": "true"}
            self.geographic_coverage = ["Gauteng", "Western Cape", "KwaZulu-Natal"]
            self.years_experience = 8
            self.contact_email = "test@construction.co.za"
            self.contact_phone = "+27 11 123 4567"
    
    company_profile = MockCompanyProfile()
    
    # Test requirement extraction
    print("📋 Testing requirement extraction...")
    sample_text = "Construction tender requiring CIDB Grade 7, 5 years experience, operations in Gauteng."
    requirements = scorer.extract_tender_requirements(sample_text)
    print(f"   - Certifications: {requirements['required_certifications']}")
    print(f"   - Experience: {requirements['min_experience']} years")
    print(f"   - Provinces: {requirements['required_provinces']}")
    
    # Test scoring
    print("📊 Testing readiness scoring...")
    result = scorer.calculate_suitability_score(company_profile, tender_req)
    
    print(f"   - Final Score: {result['suitability_score']}/100")
    print(f"   - Recommendation: {result['recommendation']}")
    print(f"   - Confidence: {result['confidence_level']}")
    print(f"   - Checklist items: {len(result['checklist'])}")
    
    # Print scoring breakdown
    print("   - Scoring Breakdown:")
    for category, score in result['scoring_breakdown'].items():
        print(f"     {category}: {score:.1f}%")
    
    print("✅ Readiness scorer test completed!")

if __name__ == "__main__":
    test_readiness_scorer()