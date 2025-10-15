# test_etenders_website.py - FOCUSED DIAGNOSTIC
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def test_main_etenders_website():
    """Test the main National Treasury eTenders website"""
    
    print("🔍 TESTING MAIN NATIONAL TREASURY eTENDERS WEBSITE")
    print("=" * 60)
    print("🌐 Website: https://www.etenders.gov.za")
    print("=" * 60)
    
    test_urls = [
        {
            "name": "Home Page",
            "url": "https://www.etenders.gov.za",
            "type": "html"
        },
        {
            "name": "Tender Search Page", 
            "url": "https://www.etenders.gov.za/Home/Tenders",
            "type": "html"
        },
        {
            "name": "Tender Notices",
            "url": "https://www.etenders.gov.za/Content/TenderNotifications",
            "type": "html"
        },
        {
            "name": "API Endpoint (Potential)",
            "url": "https://www.etenders.gov.za/api/tenders",
            "type": "api"
        },
        {
            "name": "JSON Data (Potential)", 
            "url": "https://www.etenders.gov.za/api/Data/GetTenders",
            "type": "api"
        }
    ]
    
    working_urls = []
    
    for test in test_urls:
        print(f"\n🧪 Testing: {test['name']}")
        print(f"   📍 URL: {test['url']}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/html, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.etenders.gov.za/'
            }
            
            response = requests.get(
                test['url'],
                headers=headers,
                timeout=15,
                verify=True
            )
            
            print(f"   📊 Status Code: {response.status_code}")
            print(f"   📏 Content Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                if test['type'] == 'html':
                    # Parse HTML content
                    soup = BeautifulSoup(response.content, 'html.parser')
                    title = soup.find('title')
                    print(f"   🏷️  Page Title: {title.text if title else 'No title found'}")
                    
                    # Look for tender-related content
                    tender_keywords = ['tender', 'bid', 'procurement', 'rfp', 'request for proposal']
                    page_text = soup.get_text().lower()
                    
                    keyword_matches = [kw for kw in tender_keywords if kw in page_text]
                    if keyword_matches:
                        print(f"   ✅ Found tender keywords: {', '.join(keyword_matches)}")
                    
                    # Look for forms or search functionality
                    forms = soup.find_all('form')
                    inputs = soup.find_all('input')
                    print(f"   📝 Found {len(forms)} forms and {len(inputs)} input fields")
                    
                else:  # API type
                    try:
                        data = response.json()
                        print(f"   ✅ JSON API Response: {len(data)} items" if isinstance(data, list) else "JSON object received")
                    except:
                        print(f"   ⚠️  Not valid JSON, content: {response.text[:200]}...")
                
                working_urls.append(test)
                print(f"   🟢 SUCCESS: Accessible")
                
            elif response.status_code == 403:
                print(f"   🔒 FORBIDDEN: Access denied")
            elif response.status_code == 404:
                print(f"   ❓ NOT FOUND: Endpoint doesn't exist")
            elif response.status_code == 500:
                print(f"   💥 SERVER ERROR: Internal server error")
            else:
                print(f"   🟡 UNEXPECTED: Status {response.status_code}")
                
        except requests.exceptions.SSLError as e:
            print(f"   🔐 SSL ERROR: {e}")
        except requests.exceptions.ConnectionError as e:
            print(f"   🔌 CONNECTION ERROR: {e}")
        except requests.exceptions.Timeout as e:
            print(f"   ⏰ TIMEOUT: {e}")
        except Exception as e:
            print(f"   💥 UNEXPECTED ERROR: {e}")
    
    return working_urls

def analyze_website_structure():
    """Analyze the website structure for potential data extraction"""
    print("\n" + "=" * 60)
    print("🏗️  WEBSITE STRUCTURE ANALYSIS")
    print("=" * 60)
    
    try:
        # Get the main page and analyze structure
        response = requests.get("https://www.etenders.gov.za", timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for common patterns
        print("🔍 Analyzing website structure...")
        
        # Navigation menu
        nav_links = soup.find_all('a', href=True)
        tender_links = [link for link in nav_links if any(keyword in link.get('href', '').lower() for keyword in ['tender', 'bid', 'opportunity', 'notification'])]
        
        print(f"   Found {len(tender_links)} potential tender-related links")
        for link in tender_links[:5]:  # Show first 5
            print(f"     - {link.get('href')}")
        
        # Look for search functionality
        search_forms = soup.find_all('form', {'method': 'get'})
        print(f"   Found {len(search_forms)} potential search forms")
        
        # Look for data tables or listings
        tables = soup.find_all('table')
        lists = soup.find_all(['ul', 'ol'])
        print(f"   Found {len(tables)} tables and {len(lists)} lists")
        
    except Exception as e:
        print(f"   ❌ Analysis failed: {e}")

def check_robots_txt():
    """Check robots.txt for allowed endpoints"""
    print("\n" + "=" * 60)
    print("🤖 ROBOTS.TXT ANALYSIS")
    print("=" * 60)
    
    try:
        response = requests.get("https://www.etenders.gov.za/robots.txt", timeout=10)
        if response.status_code == 200:
            print("📄 Robots.txt found:")
            for line in response.text.split('\n')[:10]:  # Show first 10 lines
                if line.strip() and not line.startswith('#'):
                    print(f"   {line}")
        else:
            print("   No robots.txt found or accessible")
    except Exception as e:
        print(f"   ❌ Could not fetch robots.txt: {e}")

if __name__ == "__main__":
    print("🚀 NATIONAL TREASURY eTENDERS WEBSITE DIAGNOSTIC")
    print("Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Test main website access
    working_urls = test_main_etenders_website()
    
    # Analyze structure
    analyze_website_structure()
    
    # Check robots.txt
    check_robots_txt()
    
    # Summary and recommendations
    print("\n" + "=" * 60)
    print("📋 SUMMARY & RECOMMENDATIONS")
    print("=" * 60)
    
    if working_urls:
        print(f"✅ SUCCESS: Found {len(working_urls)} accessible endpoints")
        print("\n🎯 RECOMMENDED APPROACHES:")
        
        html_endpoints = [url for url in working_urls if url['type'] == 'html']
        api_endpoints = [url for url in working_urls if url['type'] == 'api']
        
        if html_endpoints:
            print("1. 🕸️  WEB SCRAPING APPROACH:")
            print("   - Parse HTML pages for tender listings")
            print("   - Extract tender details from search results")
            print("   - Handle pagination and search filters")
            
        if api_endpoints:
            print("2. 🔌 API APPROACH:")
            print("   - Use discovered JSON endpoints")
            print("   - Implement proper API client")
            print("   - Handle authentication if required")
            
        print("\3. 🎓 EDUCATIONAL APPROACH:")
        print("   - Use structured mock data matching real tender patterns")
        print("   - Demonstrate OCDS data understanding")
        print("   - Build complete system with real integration potential")
        
    else:
        print("❌ No accessible endpoints found.")
        print("\n💡 ALTERNATIVE STRATEGY:")
        print("   Use educational data that demonstrates:")
        print("   - Understanding of SA tender ecosystem")
        print("   - Proper OCDS data structure knowledge") 
        print("   - Real-world API integration patterns")
        print("   - Professional error handling")