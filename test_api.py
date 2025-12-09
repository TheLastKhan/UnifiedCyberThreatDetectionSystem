"""
API Test Script - Verify REST endpoints functionality
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_health():
    """Test health check endpoint"""
    print_section("TEST 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_email_analysis():
    """Test email analysis endpoint"""
    print_section("TEST 2: Email Analysis")
    
    email_data = {
        "subject": "URGENT: Your account has been compromised!",
        "body": "Click here immediately to verify your identity: http://fake-bank.malicious.com/verify?user=12345",
        "sender": "security@not-your-bank.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/email/analyze", json=email_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if "model_confidence" in result:
            conf = result["model_confidence"]
            print(f"✅ Prediction: {conf['prediction']}")
            print(f"   Phishing Probability: {conf['phishing_probability']:.2%}")
            print(f"   Model: {conf['model_type']}")
        
        print(f"\nFull Response: {json.dumps(result, indent=2)[:500]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_web_analysis():
    """Test web log analysis endpoint"""
    print_section("TEST 3: Web Log Analysis")
    
    log_data = {
        "ip": "203.0.113.45",
        "method": "POST",
        "path": "/admin/login",
        "status": "401",
        "user_agent": "sqlmap/1.0"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/web/analyze", json=log_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if "model_analysis" in result:
            model = result["model_analysis"]
            print(f"✅ Status: {'Anomalous' if model['is_anomalous'] else 'Normal'}")
            print(f"   Anomaly Score: {model['anomaly_score']:.4f}")
            print(f"   Model: {model['model_type']}")
        
        print(f"\nFull Response: {json.dumps(result, indent=2)[:500]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_models_status():
    """Test model status endpoint"""
    print_section("TEST 4: Models Status")
    
    try:
        response = requests.get(f"{BASE_URL}/api/models/status")
        print(f"Status: {response.status_code}")
        status = response.json()
        
        print("Model Status:")
        for model, loaded in status.items():
            if model != 'timestamp':
                icon = "✅" if loaded else "❌"
                print(f"  {icon} {model}: {loaded}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_batch_email():
    """Test batch email analysis"""
    print_section("TEST 5: Batch Email Analysis")
    
    batch_data = {
        "emails": [
            {
                "subject": "Meeting Tomorrow",
                "body": "Let's meet at 10 AM tomorrow in conference room B.",
                "sender": "colleague@company.com"
            },
            {
                "subject": "Verify Your Account Now!",
                "body": "Your account will be suspended. Click here urgently: http://malicious.fake/verify",
                "sender": "admin@fake-bank.com"
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/email/batch", json=batch_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        
        print(f"✅ Analyzed {result['count']} emails")
        print(f"Response: {json.dumps(result, indent=2)[:500]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Run all API tests"""
    print("\n" + "="*60)
    print(" 🚀 CyberGuard API Test Suite")
    print(" Testing REST Endpoints with Trained Models")
    print("="*60)
    
    tests = [
        ("Health Check", test_health),
        ("Email Analysis", test_email_analysis),
        ("Web Analysis", test_web_analysis),
        ("Models Status", test_models_status),
        ("Batch Email", test_batch_email)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results[name] = False
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        icon = "✅" if result else "❌"
        print(f"{icon} {name}: {'PASSED' if result else 'FAILED'}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! API is functioning correctly.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check logs above.")
    
    return passed == total

if __name__ == "__main__":
    import sys
    
    print("""
    📝 API Test Instructions:
    
    1. Start Flask server:
       python run_dashboard.py
    
    2. In another terminal, run this test:
       python test_api.py
    
    Requirements:
    - Flask server must be running on http://localhost:5000
    - All trained models must be loaded
    - Requests library must be installed
    """)
    
    input("Press Enter to start tests...")
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
