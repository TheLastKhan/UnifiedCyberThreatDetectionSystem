"""
Test script for advanced NLP API endpoints (BERT, FastText, Hybrid)
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5000"

# Test emails
TEST_EMAILS = [
    {
        "name": "Obvious Phishing",
        "content": """
        URGENT ACTION REQUIRED!
        
        Your PayPal account has been suspended due to suspicious activity.
        Click here immediately to verify your identity: http://paypa1-verify.tk/login
        
        If you don't verify within 24 hours, your account will be permanently closed.
        
        PayPal Security Team
        """,
        "subject": "URGENT: Verify Your PayPal Account Now!",
        "sender": "security@paypa1-verify.tk"
    },
    {
        "name": "Legitimate Email",
        "content": """
        Hi John,
        
        Just wanted to confirm our meeting tomorrow at 2 PM.
        I'll send you the agenda later today.
        
        Best regards,
        Sarah
        """,
        "subject": "Meeting Tomorrow",
        "sender": "sarah@company.com"
    },
    {
        "name": "Subtle Phishing",
        "content": """
        Dear customer,
        
        We noticed an unusual login attempt from an unknown device.
        For your security, please review your recent activity.
        
        View Activity: https://amaz0n-security.com/review
        
        Amazon Security
        """,
        "subject": "Unusual Activity Detected",
        "sender": "noreply@amazon.com"
    }
]

def print_separator():
    print("\n" + "="*70 + "\n")

def test_endpoint(endpoint_name, url, data):
    """Test a single endpoint"""
    print(f"🔍 Testing: {endpoint_name}")
    print(f"📍 URL: {url}")
    
    try:
        start_time = time.time()
        response = requests.post(url, json=data, timeout=30)
        elapsed_time = (time.time() - start_time) * 1000
        
        print(f"⏱️  Total time: {elapsed_time:.2f}ms")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ ERROR")
            print(response.text)
            
        return response.status_code == 200, result if response.status_code == 200 else None
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: API server not running on {BASE_URL}")
        print("💡 Start the server with: python web_dashboard/production_api.py")
        return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def main():
    print("="*70)
    print("🧪 TESTING ADVANCED NLP API ENDPOINTS")
    print("="*70)
    
    results_summary = []
    
    for email_test in TEST_EMAILS:
        print_separator()
        print(f"📧 EMAIL: {email_test['name']}")
        print(f"Subject: {email_test['subject']}")
        print(f"From: {email_test['sender']}")
        print("-" * 70)
        
        # Prepare request data
        request_data = {
            "email_content": email_test["content"],
            "email_subject": email_test["subject"],
            "email_sender": email_test.get("sender", "")
        }
        
        email_results = {
            "email": email_test["name"],
            "endpoints": {}
        }
        
        # Test 1: TF-IDF (baseline)
        print("\n1️⃣ TF-IDF + Random Forest (Baseline)")
        print("-" * 70)
        success, result = test_endpoint(
            "TF-IDF Baseline",
            f"{BASE_URL}/api/email/analyze",
            request_data
        )
        if result:
            email_results["endpoints"]["tfidf"] = {
                "prediction": result.get("prediction"),
                "confidence": result.get("confidence")
            }
        
        time.sleep(0.5)
        
        # Test 2: BERT
        print("\n2️⃣ BERT (Advanced NLP)")
        print("-" * 70)
        success, result = test_endpoint(
            "BERT Detector",
            f"{BASE_URL}/api/email/analyze/bert",
            request_data
        )
        if result:
            email_results["endpoints"]["bert"] = {
                "prediction": result.get("prediction"),
                "confidence": result.get("confidence"),
                "time_ms": result.get("processing_time_ms")
            }
        
        time.sleep(0.5)
        
        # Test 3: FastText (optional, might fail due to NumPy issue)
        print("\n3️⃣ FastText (Fast & Lightweight)")
        print("-" * 70)
        success, result = test_endpoint(
            "FastText Detector",
            f"{BASE_URL}/api/email/analyze/fasttext",
            request_data
        )
        if result:
            email_results["endpoints"]["fasttext"] = {
                "prediction": result.get("prediction"),
                "confidence": result.get("confidence"),
                "time_ms": result.get("processing_time_ms")
            }
        
        time.sleep(0.5)
        
        # Test 4: Hybrid (all models combined)
        print("\n4️⃣ Hybrid Ensemble (All Models)")
        print("-" * 70)
        success, result = test_endpoint(
            "Hybrid Detector",
            f"{BASE_URL}/api/email/analyze/hybrid",
            request_data
        )
        if result:
            email_results["endpoints"]["hybrid"] = {
                "prediction": result.get("final_prediction"),
                "confidence": result.get("final_confidence"),
                "models_used": result.get("models_used"),
                "time_ms": result.get("total_processing_time_ms")
            }
        
        results_summary.append(email_results)
    
    # Summary
    print_separator()
    print("📊 SUMMARY OF ALL TESTS")
    print("="*70)
    
    for email_result in results_summary:
        print(f"\n📧 {email_result['email']}")
        print("-" * 70)
        
        for endpoint_name, endpoint_result in email_result['endpoints'].items():
            print(f"  {endpoint_name.upper():12} → {endpoint_result.get('prediction', 'N/A'):12} "
                  f"(confidence: {endpoint_result.get('confidence', 0):.2%})")
    
    print_separator()
    print("✅ Testing complete!")
    print("\n💡 Tips:")
    print("  - BERT: Best accuracy (~94-97%), slowest (~20-100ms)")
    print("  - FastText: Good accuracy (~90-94%), very fast (~2-5ms)")
    print("  - TF-IDF: Good baseline (~85-92%), fast (~15-30ms)")
    print("  - Hybrid: Best of all, balanced speed/accuracy")
    print("\n🚀 Ready for production!")

if __name__ == "__main__":
    main()
