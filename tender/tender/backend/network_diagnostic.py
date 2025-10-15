# network_diagnostic.py - COMPREHENSIVE NETWORK TEST
import requests
import socket
import ssl
import subprocess
from datetime import datetime

def comprehensive_diagnostic():
    print("🔍 COMPREHENSIVE NETWORK DIAGNOSTIC")
    print("=" * 60)
    
    target_url = "https://www.etenders.gov.za"
    
    # Test 1: Basic DNS Resolution
    print("\n1. 🎯 DNS RESOLUTION TEST")
    try:
        ip = socket.gethostbyname("www.etenders.gov.za")
        print(f"   ✅ DNS Resolution: {ip}")
    except Exception as e:
        print(f"   ❌ DNS Failed: {e}")
    
    # Test 2: Ping Test (if possible)
    print("\n2. 📡 CONNECTIVITY TEST")
    try:
        result = subprocess.run(
            ["ping", "-c", "2", "www.etenders.gov.za"], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("   ✅ Ping successful")
        else:
            print("   ❌ Ping failed")
    except:
        print("   ⚠️  Ping test not available")
    
    # Test 3: SSL Certificate Check
    print("\n3. 🔐 SSL CERTIFICATE CHECK")
    try:
        context = ssl.create_default_context()
        with socket.create_connection(("www.etenders.gov.za", 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname="www.etenders.gov.za") as ssock:
                cert = ssock.getpeercert()
                print(f"   ✅ SSL Certificate: Valid until {cert['notAfter']}")
    except Exception as e:
        print(f"   ❌ SSL Error: {e}")
    
    # Test 4: HTTP Request with Detailed Headers
    print("\n4. 🌐 HTTP REQUEST ANALYSIS")
    try:
        response = requests.get(target_url, timeout=15, verify=True)
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📏 Content Length: {len(response.content)}")
        print(f"   🕒 Response Time: {response.elapsed.total_seconds():.2f}s")
        
        # Check for redirects
        if response.history:
            print(f"   🔄 Redirects: {len(response.history)}")
            for resp in response.history:
                print(f"      {resp.status_code} -> {resp.url}")
        
    except requests.exceptions.SSLError as e:
        print(f"   🔐 SSL Error: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"   🔌 Connection Error: {e}")
    except requests.exceptions.Timeout as e:
        print(f"   ⏰ Timeout: {e}")
    except Exception as e:
        print(f"   💥 Error: {e}")
    
    # Test 5: Network Configuration
    print("\n5. ⚙️  NETWORK CONFIGURATION")
    try:
        # Check if behind proxy
        proxy = requests.utils.get_environ_proxies(target_url)
        if proxy:
            print(f"   🔄 Using Proxy: {proxy}")
        else:
            print("   ✅ No proxy detected")
            
        # Check user agent
        print(f"   🤖 User Agent: {requests.utils.default_user_agent()}")
        
    except Exception as e:
        print(f"   ❌ Config check failed: {e}")

def test_with_different_approaches():
    print("\n" + "=" * 60)
    print("🔄 ALTERNATIVE ACCESS METHODS")
    print("=" * 60)
    
    url = "https://www.etenders.gov.za"
    
    approaches = [
        {"name": "Standard Request", "verify_ssl": True, "timeout": 10},
        {"name": "No SSL Verify", "verify_ssl": False, "timeout": 10},
        {"name": "Different User Agent", "verify_ssl": True, "timeout": 10, 
         "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}},
        {"name": "HTTP (not HTTPS)", "verify_ssl": True, "timeout": 10, 
         "url": "http://www.etenders.gov.za"}
    ]
    
    for approach in approaches:
        print(f"\n🧪 Trying: {approach['name']}")
        try:
            response = requests.get(
                approach.get('url', url),
                verify=approach['verify_ssl'],
                timeout=approach['timeout'],
                headers=approach.get('headers', {})
            )
            print(f"   ✅ Success - Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

if __name__ == "__main__":
    print("🚀 NETWORK ACCESS DIAGNOSTIC TOOL")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Target: https://www.etenders.gov.za")
    
    comprehensive_diagnostic()
    test_with_different_approaches()
    
    print("\n" + "=" * 60)
    print("💡 SOLUTIONS TO TRY")
    print("=" * 60)
    print("1. 🔄 Try different network (mobile hotspot, university WiFi)")
    print("2. 🌐 Use VPN to change your IP location")
    print("3. ⚙️  Ask classmates for their exact request code")
    print("4. 📧 Contact the website administrators")
    print("5. 🎓 Use the educational approach for your project")