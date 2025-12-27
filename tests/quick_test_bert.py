"""
Quick test for BERT endpoint
"""
import requests
import json

# Test simple health check
print("Testing health endpoint...")
try:
    response = requests.get("http://localhost:5001/api/health", timeout=5)
    print(f"✅ Health: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test BERT endpoint
print("\nTesting BERT endpoint...")
data = {
    "email_content": "URGENT! Your PayPal account will be suspended. Click here: http://paypa1-verify.tk",
    "email_subject": "URGENT: Verify Your Account"
}

try:
    response = requests.post(
        "http://localhost:5001/api/email/analyze/bert",
        json=data,
        timeout=30
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ BERT Result:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Try the production API endpoint
print("\nTrying production API routes...")
endpoints = [
    "/api/email/analyze/bert",
    "/api/v1/email/analyze/bert",
    "/email/analyze/bert"
]

for endpoint in endpoints:
    try:
        url = f"http://localhost:5001{endpoint}"
        response = requests.post(url, json=data, timeout=5)
        if response.status_code != 404:
            print(f"✅ Found working endpoint: {endpoint}")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Result: {response.json()}")
            break
        else:
            print(f"❌ {endpoint} - 404")
    except Exception as e:
        print(f"❌ {endpoint} - Error: {e}")
