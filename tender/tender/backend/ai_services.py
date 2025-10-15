# ai_services.py - COMPLETE FIXED VERSION WITH AI ANALYTICS
import requests
from typing import Dict, Any, List, Optional
import json
import re
from datetime import datetime
from document_processor import DocumentProcessor
from mongodb_service import mongodb_service

class AIService:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.industry_keywords = {
            "construction": ["construction", "building", "civil", "engineering", "infrastructure", 
                           "roads", "bridges", "cidb", "earthworks", "paving", "renovation"],
            "it_services": ["software", "technology", "digital", "computer", "system", "network", 
                          "cybersecurity", "it", "information technology", "programming", "database"],
            "security": ["security", "guard", "protection", "surveillance", "patrol", 
                        "access control", "cctv", "alarm", "monitoring", "response"],
            "cleaning": ["cleaning", "sanitation", "hygiene", "maintenance", "janitorial", 
                        "waste management", "cleaning services", "housekeeping", "sanitization"],
            "transport": ["transport", "logistics", "delivery", "shipping", "freight", 
                         "courier", "haulage", "fleet", "vehicles", "logistics"],
            "healthcare": ["medical", "health", "hospital", "clinic", "healthcare", 
                          "patient", "treatment", "medical services"],
            "education": ["education", "training", "school", "university", "learning", 
                         "curriculum", "educational", "teaching"],
            "agriculture": ["agriculture", "farming", "crops", "livestock", "irrigation", 
                           "harvest", "farming equipment"]
        }

    def summarize_document(self, document_url: str, title: str, description: str = None) -> Dict[str, Any]:
        """
        FIXED: Instance method that matches main.py call signature
        Uses fallback strategy when URLs are unavailable
        """
        try:
            # Check if URL is a placeholder or unavailable
            if not document_url or "example.com" in document_url or "etenders.gov.za/content" in document_url:
                print("🔄 Using fallback summarization (URL unavailable)")
                return self._summarize_from_text(title, description)
            
            # Try to process actual document if URL looks real
            try:
                print(f"🔍 Attempting to process document: {document_url}")
                document_result = self.document_processor.process_document(document_url)
                
                if "error" not in document_result:
                    extracted_text = document_result.get("extracted_text_sample", "")
                    if extracted_text:
                        print("✅ Using actual document content for AI analysis")
                        analysis_result = self.analyze_document_content(extracted_text)
                        return {
                            "summary": analysis_result["summary"],
                            "key_points": analysis_result["key_points"],
                            "industry_sector": analysis_result["industry_sector"],
                            "complexity_score": analysis_result["complexity_score"]
                        }
            except Exception as e:
                print(f"⚠️ Document processing failed, using fallback: {e}")
            
            # Fallback to text-based summarization
            print("🔄 Falling back to text-based summarization")
            return self._summarize_from_text(title, description)
            
        except Exception as e:
            print(f"❌ AI summarization error: {e}")
            return self._get_basic_summary(title, description)

    def _summarize_from_text(self, title: str, description: str = None) -> Dict[str, Any]:
        """Generate AI summary from tender title and description"""
        print(f"📝 Generating AI summary from: {title}")
        
        text = f"TENDER TITLE: {title}\n\nDESCRIPTION: {description or 'No detailed description available.'}"
        
        analysis_result = self.analyze_document_content(text)
        
        return {
            "summary": analysis_result["summary"],
            "key_points": analysis_result["key_points"],
            "industry_sector": analysis_result["industry_sector"],
            "complexity_score": analysis_result["complexity_score"],
            "note": "AI analysis based on tender information (document unavailable)"
        }

    def _get_basic_summary(self, title: str, description: str = None) -> Dict[str, Any]:
        """Fallback summary when AI analysis fails"""
        return {
            "summary": f"This tender involves {title}. {description or 'Review full documentation for complete details.'}",
            "key_points": {
                "objective": f"Procurement of {title}",
                "scope": "Various services as specified in tender documentation",
                "deadline": "As per tender notice",
                "budget_range": "To be specified",
                "eligibility_criteria": [
                    "Relevant industry experience",
                    "Valid business registration",
                    "Tax compliance status"
                ]
            },
            "industry_sector": "General Services",
            "complexity_score": 50
        }

    def analyze_document_content(self, text: str) -> Dict[str, Any]:
        """
        REAL AI analysis of document content using advanced text processing
        """
        try:
            if not text or len(text.strip()) < 100:
                return self._get_basic_analysis(text)
            
            text_lower = text.lower()
            
            # Determine industry sector
            industry_sector = self._detect_industry_sector(text_lower)
            
            # Extract key requirements using advanced pattern matching
            requirements = self._extract_requirements(text_lower)
            
            # Generate intelligent summary based on actual content
            summary = self._generate_intelligent_summary(text, industry_sector, requirements)
            
            # Calculate complexity score
            complexity_score = self._calculate_complexity(text)
            
            # Extract key points
            key_points = self._extract_key_points_from_text(text, requirements)
            
            return {
                "industry_sector": industry_sector,
                "summary": summary,
                "key_points": key_points,
                "requirements": requirements,
                "complexity_score": complexity_score,
                "estimated_timeline": self._estimate_timeline(complexity_score, industry_sector),
                "budget_indication": self._estimate_budget_range(text_lower, industry_sector),
                "analysis_confidence": self._calculate_confidence(text),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ AI analysis error: {e}")
            return self._get_basic_analysis(text)

    def _detect_industry_sector(self, text: str) -> str:
        """Intelligently detect the industry sector from text content"""
        sector_scores = {}
        
        for sector, keywords in self.industry_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
                    score += text.count(keyword) * 0.5
            
            sector_scores[sector] = score
        
        # Get sector with highest score
        if sector_scores:
            best_sector = max(sector_scores.items(), key=lambda x: x[1])
            if best_sector[1] > 0:
                return best_sector[0].replace("_", " ").title()
        
        return "General Services"

    def _extract_requirements(self, text: str) -> Dict[str, Any]:
        """Extract specific requirements from tender text"""
        requirements = {
            "required_certifications": [],
            "experience_years": 0,
            "geographic_requirements": [],
            "technical_requirements": [],
            "financial_requirements": [],
            "deadline_info": "",
            "submission_requirements": []
        }
        
        # Extract certifications
        cert_patterns = {
            "CIDB": [r"cidb.*?grade\s*(\w+)", r"cidb.*?(\d+[a-z]*)", r"construction industry"],
            "BBBEE": [r"bbbee.*?level\s*(\d+)", r"bbbee", r"broad-based black economic empowerment"],
            "SARS": [r"sars.*?tax", r"tax clearance", r"tax certificate"],
            "CSD": [r"csd", r"central supplier database"],
            "PSIRA": [r"psira", r"private security"],
            "ISO": [r"iso.*?\d+", r"iso.*?certification"]
        }
        
        for cert, patterns in cert_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    requirements["required_certifications"].append(f"{cert}: {matches[0]}" if matches else cert)
                    break
        
        # Extract experience requirements
        exp_patterns = [
            r"(\d+)\s*years?\s*experience",
            r"minimum\s*of\s*(\d+)\s*years",
            r"at least\s*(\d+)\s*years",
            r"(\d+)\s*years?\s*in.*?experience"
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    years = int(matches[0])
                    if years > requirements["experience_years"]:
                        requirements["experience_years"] = years
                except:
                    pass
        
        # Extract geographic requirements
        provinces = ["gauteng", "western cape", "kwazulu-natal", "eastern cape", 
                    "limpopo", "mpumalanga", "north west", "free state", "northern cape"]
        
        for province in provinces:
            if province in text:
                requirements["geographic_requirements"].append(province.title())
        
        return requirements

    def _generate_intelligent_summary(self, text: str, industry: str, requirements: Dict[str, Any]) -> str:
        """Generate intelligent summary based on actual document content"""
        
        sentences = re.split(r'[.!?]+', text)
        meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Get top sentences
        top_sentences = meaningful_sentences[:3] if meaningful_sentences else ["Procurement of specialized services."]
        
        # Build comprehensive summary
        summary_parts = []
        
        if industry != "General Services":
            summary_parts.append(f"This {industry} tender involves")
        
        if requirements["experience_years"] > 0:
            summary_parts.append(f"requiring {requirements['experience_years']} years of experience")
        
        if requirements["required_certifications"]:
            certs = ", ".join(requirements["required_certifications"][:2])
            summary_parts.append(f"with certifications including {certs}")
        
        # Add top content sentences
        content_summary = " ".join(top_sentences[:2])
        if content_summary:
            summary_parts.append(content_summary)
        
        summary = " ".join(summary_parts)
        
        if len(summary) > 250:
            summary = summary[:247] + "..."
        
        return summary if summary.strip() else "Comprehensive tender requiring detailed review of full documentation."

    def _calculate_complexity(self, text: str) -> int:
        """Calculate complexity score based on document content"""
        if not text:
            return 50
        
        score = 50
        
        # Length factor
        length_factor = min(len(text) / 1000, 2)
        score *= length_factor
        
        # Technical terms factor
        technical_terms = ["specification", "requirement", "compliance", "standard", 
                          "regulation", "certification", "qualification", "mandatory"]
        tech_count = sum(1 for term in technical_terms if term in text.lower())
        score += tech_count * 5
        
        return min(int(score), 100)

    def _estimate_timeline(self, complexity: int, industry: str) -> str:
        """Estimate project timeline based on complexity and industry"""
        base_times = {
            "Construction": 90,
            "It Services": 60,
            "Security": 45,
            "Cleaning": 30,
            "Transport": 45,
            "Healthcare": 60,
            "Education": 75,
            "Agriculture": 50,
            "General Services": 60
        }
        
        base_days = base_times.get(industry, 60)
        adjusted_days = base_days * (complexity / 50)
        
        if adjusted_days < 30:
            return "30 days"
        elif adjusted_days < 60:
            return "45 days"
        elif adjusted_days < 90:
            return "60 days"
        else:
            return "90+ days"

    def _estimate_budget_range(self, text: str, industry: str) -> str:
        """Estimate budget range based on industry and content"""
        # Look for explicit budget mentions
        budget_patterns = [
            r"r\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
            r"rand\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
            r"zar\s*(\d+(?:,\d{3})*(?:\.\d{2})?)"
        ]
        
        for pattern in budget_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    amount_str = matches[0].replace(',', '')
                    amount = float(amount_str)
                    if amount > 1000000:
                        return f"R{amount/1000000:.1f}M - R{amount*1.5/1000000:.1f}M"
                    elif amount > 100000:
                        return f"R{amount/1000:.0f}K - R{amount*1.5/1000:.0f}K"
                except:
                    pass
        
        # Industry-based estimates
        industry_budgets = {
            "Construction": "R5M - R15M",
            "It Services": "R2M - R8M", 
            "Security": "R1M - R5M",
            "Cleaning": "R500K - R2M",
            "Transport": "R1M - R4M",
            "Healthcare": "R3M - R10M",
            "Education": "R2M - R6M",
            "Agriculture": "R1M - R4M",
            "General Services": "R1M - R5M"
        }
        
        return industry_budgets.get(industry, "R1M - R5M")

    def _calculate_confidence(self, text: str) -> str:
        """Calculate confidence level of the analysis"""
        if not text or len(text) < 200:
            return "Low"
        
        indicators = 0
        if len(text) > 1000:
            indicators += 1
        if any(keyword in text.lower() for keyword in ["required", "must", "shall"]):
            indicators += 1
        if any(keyword in text.lower() for keyword in ["deadline", "submission", "closing"]):
            indicators += 1
        
        if indicators >= 3:
            return "High"
        elif indicators >= 2:
            return "Medium"
        else:
            return "Low"

    def _extract_key_points_from_text(self, text: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured key points from analyzed content"""
        key_points = {
            "objective": "Procurement of services as specified",
            "scope": "Various professional services and deliverables",
            "deadline": requirements.get("deadline_info", "As per tender documentation"),
            "budget_range": self._estimate_budget_range(text.lower(), "General Services"),
            "eligibility_criteria": [],
            "key_requirements": [],
            "submission_details": []
        }
        
        # Build eligibility criteria from requirements
        if requirements["experience_years"] > 0:
            key_points["eligibility_criteria"].append(f"Minimum {requirements['experience_years']} years experience")
        
        if requirements["required_certifications"]:
            key_points["eligibility_criteria"].extend(requirements["required_certifications"][:3])
        
        if requirements["geographic_requirements"]:
            key_points["eligibility_criteria"].append(f"Operations in {', '.join(requirements['geographic_requirements'][:2])}")
        
        # Add common requirements if none found
        if not key_points["eligibility_criteria"]:
            key_points["eligibility_criteria"] = [
                "Relevant industry experience",
                "Valid business registration", 
                "Tax compliance status"
            ]
        
        key_points["key_requirements"] = [
            "Detailed project proposal",
            "Pricing schedule", 
            "Company profile and references"
        ]
        
        key_points["submission_details"] = [
            "Complete tender documentation",
            "Submission before deadline",
            "Compliance with all requirements"
        ]
        
        return key_points

    def _get_basic_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback analysis for minimal text"""
        return {
            "industry_sector": "General Services",
            "summary": "Limited information available. Review full tender documentation for complete details.",
            "key_points": {
                "objective": "Procurement of specialized services",
                "scope": "Various professional services as specified",
                "deadline": "As per tender documentation",
                "budget_range": "To be specified",
                "eligibility_criteria": ["Relevant experience", "Valid certifications", "Business registration"],
                "key_requirements": ["Detailed proposal", "Pricing information", "Company documentation"],
                "submission_details": ["Complete documentation", "On-time submission"]
            },
            "requirements": {
                "required_certifications": [],
                "experience_years": 0,
                "geographic_requirements": [],
                "technical_requirements": [],
                "financial_requirements": [],
                "deadline_info": "",
                "submission_requirements": []
            },
            "complexity_score": 50,
            "estimated_timeline": "60 days",
            "budget_indication": "R1M - R5M",
            "analysis_confidence": "Low",
            "analysis_timestamp": datetime.utcnow().isoformat()
        }

    # ========== AI ANALYTICS METHODS ==========

    def analyze_industry_trends(self, tenders: List[Any]) -> List[Dict[str, Any]]:
        """AI-powered analysis of industry trends across tenders"""
        try:
            industry_stats = {}
            total_tenders = len(tenders)
            
            for tender in tenders:
                # Analyze each tender's industry
                text = f"{tender.title} {tender.description or ''}"
                industry = self._detect_industry_sector(text.lower())
                
                if industry not in industry_stats:
                    industry_stats[industry] = {
                        "count": 0,
                        "total_budget": 0,
                        "avg_complexity": 0,
                        "tenders": []
                    }
                
                industry_stats[industry]["count"] += 1
                
                # Estimate budget for this tender
                budget_estimate = self._estimate_budget_from_tender(tender)
                industry_stats[industry]["total_budget"] += budget_estimate
                
                # Calculate complexity
                complexity = self._calculate_complexity(text)
                industry_stats[industry]["avg_complexity"] = (
                    (industry_stats[industry]["avg_complexity"] * (industry_stats[industry]["count"] - 1) + complexity) 
                    / industry_stats[industry]["count"]
                )
                
                # Store tender info
                industry_stats[industry]["tenders"].append({
                    "title": tender.title,
                    "budget_estimate": budget_estimate,
                    "complexity": complexity,
                    "buyer": tender.buyer_organization
                })
            
            # Convert to analytics format
            analytics = []
            for industry, stats in industry_stats.items():
                market_share = (stats["count"] / total_tenders) * 100 if total_tenders > 0 else 0
                avg_budget = stats["total_budget"] / stats["count"] if stats["count"] > 0 else 0
                
                analytics.append({
                    "industry": industry,
                    "tender_count": stats["count"],
                    "market_share_percentage": round(market_share, 1),
                    "total_budget_estimate": stats["total_budget"],
                    "average_budget": round(avg_budget, 2),
                    "average_complexity": round(stats["avg_complexity"], 1),
                    "growth_indicator": self._calculate_growth_indicator(stats["count"], total_tenders),
                    "competition_level": self._estimate_competition_level(industry, stats["count"]),
                    "recommendation": self._generate_industry_recommendation(industry, market_share, stats["avg_complexity"])
                })
            
            # Sort by market share
            analytics.sort(key=lambda x: x["market_share_percentage"], reverse=True)
            return analytics
            
        except Exception as e:
            print(f"❌ Industry trends analysis error: {e}")
            return []

    def analyze_complexity_trends(self, tenders: List[Any]) -> List[Dict[str, Any]]:
        """AI-powered complexity analysis across tenders"""
        try:
            complexity_buckets = {
                "Low (0-30)": {"count": 0, "tenders": [], "total_budget": 0},
                "Medium (31-60)": {"count": 0, "tenders": [], "total_budget": 0},
                "High (61-80)": {"count": 0, "tenders": [], "total_budget": 0},
                "Very High (81-100)": {"count": 0, "tenders": [], "total_budget": 0}
            }
            
            for tender in tenders:
                text = f"{tender.title} {tender.description or ''}"
                complexity = self._calculate_complexity(text)
                budget_estimate = self._estimate_budget_from_tender(tender)
                
                if complexity <= 30:
                    bucket = "Low (0-30)"
                elif complexity <= 60:
                    bucket = "Medium (31-60)"
                elif complexity <= 80:
                    bucket = "High (61-80)"
                else:
                    bucket = "Very High (81-100)"
                
                complexity_buckets[bucket]["count"] += 1
                complexity_buckets[bucket]["total_budget"] += budget_estimate
                complexity_buckets[bucket]["tenders"].append({
                    "title": tender.title,
                    "complexity": complexity,
                    "budget_estimate": budget_estimate,
                    "industry": self._detect_industry_sector(text.lower())
                })
            
            # Convert to analytics format
            analytics = []
            total_tenders = len(tenders)
            
            for bucket_name, bucket_data in complexity_buckets.items():
                if bucket_data["count"] > 0:
                    percentage = (bucket_data["count"] / total_tenders) * 100
                    avg_budget = bucket_data["total_budget"] / bucket_data["count"]
                    
                    analytics.append({
                        "complexity_level": bucket_name,
                        "tender_count": bucket_data["count"],
                        "percentage_of_total": round(percentage, 1),
                        "average_budget": round(avg_budget, 2),
                        "total_budget": bucket_data["total_budget"],
                        "recommended_approach": self._get_complexity_recommendation(bucket_name),
                        "success_probability": self._estimate_success_probability(bucket_name),
                        "typical_timeline": self._get_complexity_timeline(bucket_name)
                    })
            
            return analytics
            
        except Exception as e:
            print(f"❌ Complexity trends analysis error: {e}")
            return []

    def analyze_competition_insights(self, tenders: List[Any]) -> List[Dict[str, Any]]:
        """AI-powered competition and market insights"""
        try:
            buyer_stats = {}
            industry_competition = {}
            
            for tender in tenders:
                text = f"{tender.title} {tender.description or ''}"
                industry = self._detect_industry_sector(text.lower())
                buyer = tender.buyer_organization or "Unknown"
                complexity = self._calculate_complexity(text)
                budget_estimate = self._estimate_budget_from_tender(tender)
                
                # Track buyer statistics
                if buyer not in buyer_stats:
                    buyer_stats[buyer] = {"count": 0, "total_budget": 0, "industries": set()}
                buyer_stats[buyer]["count"] += 1
                buyer_stats[buyer]["total_budget"] += budget_estimate
                buyer_stats[buyer]["industries"].add(industry)
                
                # Track industry competition
                if industry not in industry_competition:
                    industry_competition[industry] = {"tenders": 0, "buyers": set(), "total_budget": 0}
                industry_competition[industry]["tenders"] += 1
                industry_competition[industry]["buyers"].add(buyer)
                industry_competition[industry]["total_budget"] += budget_estimate
            
            # Convert to analytics format
            analytics = []
            
            # Buyer insights
            for buyer, stats in buyer_stats.items():
                avg_budget = stats["total_budget"] / stats["count"]
                industry_diversity = len(stats["industries"])
                
                analytics.append({
                    "insight_type": "buyer_analysis",
                    "buyer_organization": buyer,
                    "tenders_issued": stats["count"],
                    "total_spend": stats["total_budget"],
                    "average_tender_value": round(avg_budget, 2),
                    "industry_diversity": industry_diversity,
                    "procurement_frequency": self._assess_procurement_frequency(stats["count"]),
                    "recommendation": self._generate_buyer_recommendation(buyer, stats["count"], avg_budget)
                })
            
            # Industry competition insights
            for industry, stats in industry_competition.items():
                buyer_count = len(stats["buyers"])
                competition_level = self._calculate_competition_level(buyer_count, stats["tenders"])
                
                analytics.append({
                    "insight_type": "industry_competition",
                    "industry": industry,
                    "total_tenders": stats["tenders"],
                    "unique_buyers": buyer_count,
                    "total_market_size": stats["total_budget"],
                    "competition_level": competition_level,
                    "market_concentration": self._calculate_market_concentration(buyer_count, stats["tenders"]),
                    "opportunity_level": self._assess_opportunity_level(competition_level, stats["total_budget"])
                })
            
            return analytics
            
        except Exception as e:
            print(f"❌ Competition insights analysis error: {e}")
            return []

    # ========== ANALYTICS HELPER METHODS ==========

    def _estimate_budget_from_tender(self, tender: Any) -> float:
        """Estimate budget from tender data"""
        try:
            # Try to extract from budget range
            if tender.budget_range:
                # Parse "R1M - R2M" or similar formats
                numbers = re.findall(r'[\d.]+', tender.budget_range)
                if numbers:
                    return float(numbers[0]) * 1000000  # Convert to numeric
            
            # Fallback: Estimate based on industry
            text = f"{tender.title} {tender.description or ''}"
            industry = self._detect_industry_sector(text.lower())
            industry_budgets = {
                "Construction": 5000000,
                "It Services": 2000000,
                "Security": 1000000,
                "Cleaning": 500000,
                "Transport": 1000000,
                "Healthcare": 3000000,
                "Education": 2000000,
                "Agriculture": 1000000,
                "General Services": 1000000
            }
            return industry_budgets.get(industry, 1000000)
        except:
            return 1000000  # Default fallback

    def _calculate_growth_indicator(self, industry_count: int, total_count: int) -> str:
        """Calculate growth indicator for an industry"""
        market_share = (industry_count / total_count) * 100 if total_count > 0 else 0
        
        if market_share > 30:
            return "Dominant"
        elif market_share > 15:
            return "Growing"
        elif market_share > 5:
            return "Stable"
        else:
            return "Niche"

    def _estimate_competition_level(self, industry: str, tender_count: int) -> str:
        """Estimate competition level for an industry"""
        # High competition industries
        high_comp_industries = ["Construction", "It Services", "Cleaning"]
        
        if industry in high_comp_industries and tender_count > 10:
            return "High"
        elif tender_count > 5:
            return "Medium"
        else:
            return "Low"

    def _generate_industry_recommendation(self, industry: str, market_share: float, complexity: float) -> str:
        """Generate strategic recommendation for an industry"""
        if market_share > 25 and complexity < 60:
            return f"High opportunity in {industry} - Consider expanding capabilities"
        elif market_share > 10 and complexity < 70:
            return f"Good potential in {industry} - Build relevant experience"
        elif complexity > 80:
            return f"Complex {industry} projects - Ensure adequate resources"
        else:
            return f"Monitor {industry} for emerging opportunities"

    def _get_complexity_recommendation(self, complexity_level: str) -> str:
        """Get recommendation based on complexity level"""
        recommendations = {
            "Low (0-30)": "Ideal for new bidders - Straightforward requirements",
            "Medium (31-60)": "Good for experienced bidders - Moderate complexity",
            "High (61-80)": "Requires specialized expertise - Complex requirements",
            "Very High (81-100)": "Major projects only - Significant resources needed"
        }
        return recommendations.get(complexity_level, "Assess carefully before bidding")

    def _estimate_success_probability(self, complexity_level: str) -> str:
        """Estimate success probability based on complexity"""
        probabilities = {
            "Low (0-30)": "High (70-90%)",
            "Medium (31-60)": "Medium (40-70%)", 
            "High (61-80)": "Low (20-40%)",
            "Very High (81-100)": "Very Low (5-20%)"
        }
        return probabilities.get(complexity_level, "Variable")

    def _get_complexity_timeline(self, complexity_level: str) -> str:
        """Get typical timeline based on complexity"""
        timelines = {
            "Low (0-30)": "2-4 weeks",
            "Medium (31-60)": "4-6 weeks",
            "High (61-80)": "6-8 weeks", 
            "Very High (81-100)": "8-12 weeks"
        }
        return timelines.get(complexity_level, "4-6 weeks")

    def _assess_procurement_frequency(self, tender_count: int) -> str:
        """Assess how frequently a buyer procures"""
        if tender_count > 20:
            return "Very Active"
        elif tender_count > 10:
            return "Active"
        elif tender_count > 5:
            return "Moderate"
        else:
            return "Occasional"

    def _generate_buyer_recommendation(self, buyer: str, tender_count: int, avg_budget: float) -> str:
        """Generate recommendation for engaging with a buyer"""
        if tender_count > 15 and avg_budget > 2000000:
            return f"Strategic partner - {buyer} offers consistent high-value opportunities"
        elif tender_count > 8:
            return f"Regular client - Build relationship with {buyer}"
        else:
            return f"Monitor {buyer} for future opportunities"

    def _calculate_competition_level(self, buyer_count: int, tender_count: int) -> str:
        """Calculate competition level in an industry"""
        if tender_count == 0:
            return "Unknown"
        
        concentration = buyer_count / tender_count
        if concentration > 0.7:
            return "Low Competition"
        elif concentration > 0.4:
            return "Medium Competition"
        else:
            return "High Competition"

    def _calculate_market_concentration(self, buyer_count: int, tender_count: int) -> str:
        """Calculate market concentration"""
        if tender_count == 0:
            return "Unknown"
        
        ratio = buyer_count / tender_count
        if ratio > 0.8:
            return "Fragmented"
        elif ratio > 0.5:
            return "Moderate"
        else:
            return "Concentrated"

    def _assess_opportunity_level(self, competition: str, market_size: float) -> str:
        """Assess opportunity level based on competition and market size"""
        if competition == "Low Competition" and market_size > 5000000:
            return "High Opportunity"
        elif competition == "Medium Competition" and market_size > 2000000:
            return "Good Opportunity"
        elif competition == "High Competition":
            return "Competitive Market"
        else:
            return "Evaluate Carefully"

    # Keep the readiness scoring methods from your original file
    def calculate_readiness_score(self, tender_requirements: Dict[str, Any], company_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate readiness score between company profile and tender requirements"""
        try:
            score_breakdown = {}
            total_score = 0
            
            # Certification Match (30 points)
            cert_score = self._calculate_certification_score(tender_requirements, company_profile)
            score_breakdown["certifications"] = cert_score
            total_score += cert_score * 0.3
            
            # Experience Match (25 points)
            exp_score = self._calculate_experience_score(tender_requirements, company_profile)
            score_breakdown["experience"] = exp_score
            total_score += exp_score * 0.25
            
            # Geographic Match (20 points)
            geo_score = self._calculate_geographic_score(tender_requirements, company_profile)
            score_breakdown["geographic_coverage"] = geo_score
            total_score += geo_score * 0.2
            
            # Industry Match (15 points)
            industry_score = self._calculate_industry_score(tender_requirements, company_profile)
            score_breakdown["industry_match"] = industry_score
            total_score += industry_score * 0.15
            
            # Capacity Match (10 points)
            capacity_score = self._calculate_capacity_score(company_profile)
            score_breakdown["capacity"] = capacity_score
            total_score += capacity_score * 0.1
            
            # Generate checklist
            checklist = self._generate_checklist(tender_requirements, company_profile, score_breakdown)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(total_score, checklist)
            
            return {
                "suitability_score": min(round(total_score), 100),
                "checklist": checklist,
                "recommendation": recommendation,
                "scoring_breakdown": score_breakdown,
                "tender_requirements": tender_requirements
            }
            
        except Exception as e:
            print(f"❌ Readiness scoring error: {e}")
            return {
                "suitability_score": 0,
                "checklist": {},
                "recommendation": "Unable to calculate readiness score",
                "scoring_breakdown": {},
                "error": str(e)
            }

    def _calculate_certification_score(self, tender_req: Dict[str, Any], company_profile: Dict[str, Any]) -> float:
        """Calculate certification match score"""
        required_certs = tender_req.get("required_certifications", [])
        company_certs = company_profile.get("certifications", {})
        
        if not required_certs:
            return 100
        
        matched = 0
        for cert in required_certs:
            cert_name = cert.split(":")[0] if ":" in cert else cert
            if any(cert_name.lower() in key.lower() for key in company_certs.keys()):
                matched += 1
        
        return (matched / len(required_certs)) * 100 if required_certs else 100

    def _calculate_experience_score(self, tender_req: Dict[str, Any], company_profile: Dict[str, Any]) -> float:
        """Calculate experience match score"""
        required_exp = tender_req.get("experience_years", 0)
        company_exp = company_profile.get("years_experience", 0)
        
        if required_exp == 0:
            return 100
        
        if company_exp >= required_exp:
            return 100
        else:
            return min((company_exp / required_exp) * 100, 80)

    def _calculate_geographic_score(self, tender_req: Dict[str, Any], company_profile: Dict[str, Any]) -> float:
        """Calculate geographic coverage score"""
        required_provinces = tender_req.get("geographic_requirements", [])
        company_coverage = company_profile.get("geographic_coverage", [])
        
        if not required_provinces:
            return 100
        
        matched = 0
        for province in required_provinces:
            if province in company_coverage:
                matched += 1
        
        return (matched / len(required_provinces)) * 100 if required_provinces else 100

    def _calculate_industry_score(self, tender_req: Dict[str, Any], company_profile: Dict[str, Any]) -> float:
        """Calculate industry match score"""
        tender_industry = tender_req.get("industry_sector", "").lower()
        company_industry = company_profile.get("industry_sector", "").lower()
        company_services = company_profile.get("services_provided", "").lower()
        
        if not tender_industry:
            return 50
        
        if tender_industry in company_industry or company_industry in tender_industry:
            return 100
        
        if tender_industry in company_services:
            return 80
        
        return 30

    def _calculate_capacity_score(self, company_profile: Dict[str, Any]) -> float:
        """Calculate company capacity score"""
        score = 0
        
        if company_profile.get("contact_email") and company_profile.get("contact_phone"):
            score += 40
        
        if company_profile.get("services_provided") and len(company_profile["services_provided"]) > 20:
            score += 30
        
        if company_profile.get("company_name"):
            score += 30
        
        return score

    def _generate_checklist(self, tender_req: Dict[str, Any], company_profile: Dict[str, Any], scores: Dict[str, float]) -> Dict[str, bool]:
        """Generate readiness checklist"""
        checklist = {}
        
        required_certs = tender_req.get("required_certifications", [])
        company_certs = company_profile.get("certifications", {})
        
        for cert in required_certs:
            cert_name = cert.split(":")[0] if ":" in cert else cert
            has_cert = any(cert_name.lower() in key.lower() for key in company_certs.keys())
            checklist[f"Has {cert_name} certification"] = has_cert
        
        required_exp = tender_req.get("experience_years", 0)
        company_exp = company_profile.get("years_experience", 0)
        checklist[f"Meets {required_exp} years experience requirement"] = company_exp >= required_exp
        
        required_provinces = tender_req.get("geographic_requirements", [])
        company_coverage = company_profile.get("geographic_coverage", [])
        
        for province in required_provinces:
            checklist[f"Operates in {province}"] = province in company_coverage
        
        checklist["Has valid contact information"] = bool(company_profile.get("contact_email") and company_profile.get("contact_phone"))
        checklist["Has detailed services description"] = bool(company_profile.get("services_provided") and len(company_profile["services_provided"]) > 20)
        
        return checklist

    def _generate_recommendation(self, score: float, checklist: Dict[str, bool]) -> str:
        """Generate recommendation based on score and checklist"""
        if score >= 90:
            return "Excellent match - Highly recommended to bid"
        elif score >= 75:
            return "Strong suitability - Good candidate for submission"
        elif score >= 60:
            return "Moderate suitability - Consider bidding with improvements"
        elif score >= 40:
            return "Limited suitability - Significant gaps exist"
        else:
            return "Low suitability - Not recommended for bidding"

# Global instance
ai_service = AIService()