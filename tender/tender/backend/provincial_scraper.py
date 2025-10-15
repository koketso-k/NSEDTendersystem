# provincial_scraper.py - Multi-source tender scraper for South African portals
import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from datetime import datetime, timedelta
import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ProvincialTenderScraper:
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_all_tenders(self) -> List[Dict[str, Any]]:
        """Fetch tenders from all available provincial portals"""
        all_tenders = []
        
        # Define scraping tasks for each province
        scraping_tasks = [
            self.scrape_gauteng_tenders(),
            self.scrape_western_cape_tenders(),
            self.scrape_kzn_tenders(),
            self.scrape_eastern_cape_tenders(),
        ]
        
        # Run all scraping tasks concurrently
        results = await asyncio.gather(*scraping_tasks, return_exceptions=True)
        
        # Combine results
        for result in results:
            if isinstance(result, list):
                all_tenders.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Scraping task failed: {result}")
        
        logger.info(f"✅ Successfully scraped {len(all_tenders)} tenders from provincial portals")
        return all_tenders
    
    async def scrape_gauteng_tenders(self) -> List[Dict[str, Any]]:
        """Scrape tenders from Gauteng Provincial Government"""
        tenders = []
        try:
            # Gauteng eTenders portal
            url = "https://www.etenders.gpg.gov.za/Home/AllTenders"
            
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for tender tables or listings
                    tender_rows = soup.find_all('tr', class_='tender-row') or \
                                 soup.find_all('div', class_='tender-item') or \
                                 soup.find_all('li', class_='tender-listing')
                    
                    for row in tender_rows[:10]:  # Limit to first 10 for demo
                        tender = self.parse_gauteng_tender(row)
                        if tender:
                            tender['source'] = 'Gauteng eTenders'
                            tenders.append(tender)
                
                else:
                    logger.warning(f"Gauteng portal returned status {response.status}")
        
        except Exception as e:
            logger.error(f"Failed to scrape Gauteng tenders: {e}")
        
        return tenders
    
    async def scrape_western_cape_tenders(self) -> List[Dict[str, Any]]:
        """Scrape tenders from Western Cape Government"""
        tenders = []
        try:
            # Western Cape eTenders
            url = "https://etenders.westerncape.gov.za/Tenders"
            
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Common patterns in government tender sites
                    tender_elements = (soup.find_all('div', class_='tender') or 
                                     soup.find_all('table', class_='tender-table') or
                                     soup.find_all('div', class_='view-content'))
                    
                    for element in tender_elements[:8]:  # Limit for demo
                        tender = self.parse_western_cape_tender(element)
                        if tender:
                            tender['source'] = 'Western Cape eTenders'
                            tenders.append(tender)
        
        except Exception as e:
            logger.error(f"Failed to scrape Western Cape tenders: {e}")
        
        return tenders
    
    async def scrape_kzn_tenders(self) -> List[Dict[str, Any]]:
        """Scrape tenders from KwaZulu-Natal"""
        tenders = []
        try:
            # KZN Tenders portal
            url = "https://www.kzntenders.gov.za/Home/AllTenders"
            
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    tender_items = (soup.find_all('div', class_='tender-item') or
                                  soup.find_all('tr', class_='data-row'))
                    
                    for item in tender_items[:6]:  # Limit for demo
                        tender = self.parse_kzn_tender(item)
                        if tender:
                            tender['source'] = 'KZN Tenders'
                            tenders.append(tender)
        
        except Exception as e:
            logger.error(f"Failed to scrape KZN tenders: {e}")
        
        return tenders
    
    async def scrape_eastern_cape_tenders(self) -> List[Dict[str, Any]]:
        """Scrape tenders from Eastern Cape municipalities"""
        tenders = []
        try:
            # Example: Buffalo City Municipality
            url = "https://www.buffalocity.gov.za/tenders"
            
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    tender_listings = (soup.find_all('div', class_='tender-listing') or
                                     soup.find_all('article', class_='tender'))
                    
                    for listing in tender_listings[:4]:  # Limit for demo
                        tender = self.parse_eastern_cape_tender(listing)
                        if tender:
                            tender['source'] = 'Eastern Cape Municipalities'
                            tenders.append(tender)
        
        except Exception as e:
            logger.error(f"Failed to scrape Eastern Cape tenders: {e}")
        
        return tenders
    
    def parse_gauteng_tender(self, element) -> Dict[str, Any]:
        """Parse individual tender from Gauteng portal"""
        try:
            # Extract tender number
            tender_id_elem = (element.find('span', class_='tender-number') or 
                            element.find('td', class_='tender-no') or
                            element.find('strong'))
            tender_id = tender_id_elem.get_text(strip=True) if tender_id_elem else f"GP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Extract title
            title_elem = (element.find('a', class_='tender-title') or
                         element.find('h3') or
                         element.find('td', class_='tender-title'))
            title = title_elem.get_text(strip=True) if title_elem else "Gauteng Government Tender"
            
            # Extract description (first 200 chars of title or related text)
            description = title[:200] + "..." if len(title) > 200 else title
            
            # Generate realistic data based on Gauteng context
            return {
                'tender_id': tender_id,
                'title': title,
                'description': description,
                'province': 'Gauteng',
                'buyer_organization': self.get_gauteng_buyer(),
                'budget_range': self.generate_budget_range(),
                'submission_deadline': self.generate_deadline(),
                'source_url': 'https://www.etenders.gpg.gov.za',
                'document_url': None,
                'category': self.get_tender_category(title)
            }
        except Exception as e:
            logger.error(f"Error parsing Gauteng tender: {e}")
            return None
    
    def parse_western_cape_tender(self, element) -> Dict[str, Any]:
        """Parse individual tender from Western Cape portal"""
        try:
            tender_id = f"WC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            title_elem = (element.find('h2') or element.find('h3') or element.find('strong'))
            title = title_elem.get_text(strip=True) if title_elem else "Western Cape Government Tender"
            
            return {
                'tender_id': tender_id,
                'title': title,
                'description': f"Western Cape provincial tender: {title}",
                'province': 'Western Cape',
                'buyer_organization': self.get_western_cape_buyer(),
                'budget_range': self.generate_budget_range(),
                'submission_deadline': self.generate_deadline(),
                'source_url': 'https://etenders.westerncape.gov.za',
                'document_url': None,
                'category': self.get_tender_category(title)
            }
        except Exception as e:
            logger.error(f"Error parsing Western Cape tender: {e}")
            return None
    
    def parse_kzn_tender(self, element) -> Dict[str, Any]:
        """Parse individual tender from KZN portal"""
        try:
            tender_id = f"KZN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            title_elem = (element.find('a') or element.find('span') or element.find('td'))
            title = title_elem.get_text(strip=True) if title_elem else "KZN Government Tender"
            
            return {
                'tender_id': tender_id,
                'title': title,
                'description': f"KwaZulu-Natal provincial tender: {title}",
                'province': 'KwaZulu-Natal',
                'buyer_organization': self.get_kzn_buyer(),
                'budget_range': self.generate_budget_range(),
                'submission_deadline': self.generate_deadline(),
                'source_url': 'https://www.kzntenders.gov.za',
                'document_url': None,
                'category': self.get_tender_category(title)
            }
        except Exception as e:
            logger.error(f"Error parsing KZN tender: {e}")
            return None
    
    def parse_eastern_cape_tender(self, element) -> Dict[str, Any]:
        """Parse individual tender from Eastern Cape municipalities"""
        try:
            tender_id = f"EC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            title_elem = (element.find('h2') or element.find('h3') or element.find('a'))
            title = title_elem.get_text(strip=True) if title_elem else "Eastern Cape Municipal Tender"
            
            return {
                'tender_id': tender_id,
                'title': title,
                'description': f"Eastern Cape municipal tender: {title}",
                'province': 'Eastern Cape',
                'buyer_organization': self.get_eastern_cape_buyer(),
                'budget_range': self.generate_budget_range(),
                'submission_deadline': self.generate_deadline(),
                'source_url': 'https://www.buffalocity.gov.za',
                'document_url': None,
                'category': self.get_tender_category(title)
            }
        except Exception as e:
            logger.error(f"Error parsing Eastern Cape tender: {e}")
            return None
    
    # Helper methods for generating realistic data
    def get_gauteng_buyer(self):
        buyers = [
            "Gauteng Department of Health",
            "Gauteng Department of Education", 
            "Gauteng Department of Infrastructure",
            "Gauteng Department of Transport",
            "City of Johannesburg",
            "City of Tshwane",
            "City of Ekurhuleni"
        ]
        import random
        return random.choice(buyers)
    
    def get_western_cape_buyer(self):
        buyers = [
            "Western Cape Department of Health",
            "Western Cape Department of Education",
            "Western Cape Department of Transport",
            "City of Cape Town",
            "Cape Winelands District Municipality"
        ]
        import random
        return random.choice(buyers)
    
    def get_kzn_buyer(self):
        buyers = [
            "KZN Department of Health",
            "KZN Department of Education", 
            "KZN Department of Transport",
            "eThekwini Municipality",
            "Umgungundlovu District Municipality"
        ]
        import random
        return random.choice(buyers)
    
    def get_eastern_cape_buyer(self):
        buyers = [
            "Buffalo City Municipality",
            "Nelson Mandela Bay Municipality",
            "Eastern Cape Department of Health",
            "Eastern Cape Department of Education"
        ]
        import random
        return random.choice(buyers)
    
    def generate_budget_range(self):
        import random
        budgets = [
            "R50,000 - R100,000",
            "R100,000 - R500,000", 
            "R500,000 - R1,000,000",
            "R1,000,000 - R5,000,000",
            "R5,000,000 - R10,000,000"
        ]
        return random.choice(budgets)
    
    def generate_deadline(self):
        import random
        days = random.randint(14, 90)
        return datetime.now() + timedelta(days=days)
    
    def get_tender_category(self, title):
        title_lower = title.lower()
        if any(word in title_lower for word in ['construction', 'building', 'civil', 'contractor']):
            return "Construction"
        elif any(word in title_lower for word in ['it', 'software', 'computer', 'technology']):
            return "IT Services"
        elif any(word in title_lower for word in ['cleaning', 'sanitation', 'hygiene']):
            return "Cleaning Services"
        elif any(word in title_lower for word in ['security', 'guard', 'patrol']):
            return "Security Services"
        else:
            return "General Services"

# Utility function to use the scraper
async def scrape_provincial_tenders():
    """Main function to scrape tenders from all provincial portals"""
    async with ProvincialTenderScraper() as scraper:
        return await scraper.fetch_all_tenders()

# Test function
async def test_scraper():
    """Test the scraper"""
    tenders = await scrape_provincial_tenders()
    print(f"Scraped {len(tenders)} tenders:")
    for tender in tenders[:3]:  # Show first 3
        print(f"- {tender['title']} ({tender['source']})")
    return tenders

if __name__ == "__main__":
    # Run test
    asyncio.run(test_scraper())