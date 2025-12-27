"""
Simple API test
"""

import requests
import json
import time

# Try to connect
for i in range(5):
    try:
        resp = requests.get("http://127.0.0.1:5000/api/health", timeout=2)
        print(f"SUCCESS: API responded with status {resp.status_code}")
        print(f"Response: {resp.json()}")
        break
    except Exception as e:
        print(f"Attempt {i+1}: Waiting for Flask... {e}")
        time.sleep(1)

# Test email analysis
print("\n" + "="*70)
print("Testing Email Analysis")
print("="*70)

try:
    payload = {
        "email_content": "Click here to verify your account or it will be suspended",
        "email_sender": "fake@paypal.org",
        "email_subject": "URGENT: Verify Your Account Now"
    }
    resp = requests.post("http://127.0.0.1:5000/api/email/analyze", json=payload, timeout=5)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
