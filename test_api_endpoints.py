"""
Test API endpoints
"""

import requests
import json
from time import sleep

BASE_URL = "http://127.0.0.1:5000/api"

print("=" * 70)
print("Testing Unified Threat Detection API")
print("=" * 70)

# Test 1: Health Check
print("\n[1/7] Health Check - GET /api/health")
try:
    resp = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Models Status
print("\n[2/7] Models Status - GET /api/models/status")
try:
    resp = requests.get(f"{BASE_URL}/models/status", timeout=5)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Email Analysis
print("\n[3/7] Email Analysis - POST /api/email/analyze")
try:
    payload = {
        "subject": "URGENT: Verify Your Account Now",
        "body": "Click here to verify your account or it will be suspended",
        "sender": "fake@paypal.org"
    }
    resp = requests.post(f"{BASE_URL}/email/analyze", json=payload, timeout=5)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test 4: Web Analysis
print("\n[4/7] Web Analysis - POST /api/web/analyze")
try:
    payload = {
        "ip": "203.0.113.45",
        "method": "POST",
        "path": "/admin/login",
        "status": "401",
        "user_agent": "Python-urllib/3.6"
    }
    resp = requests.post(f"{BASE_URL}/web/analyze", json=payload, timeout=5)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test 5: Unified Analysis
print("\n[5/7] Unified Analysis - POST /api/unified/analyze")
try:
    payload = {
        "type": "email",
        "email": {
            "subject": "You Won 1 Million Dollars!",
            "body": "Click here for free money - no verification needed!",
            "sender": "scammer@fake.com"
        }
    }
    resp = requests.post(f"{BASE_URL}/unified/analyze", json=payload, timeout=5)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test 6: Batch Email Analysis
print("\n[6/7] Batch Email Analysis - POST /api/email/batch")
try:
    payload = {
        "emails": [
            {
                "subject": "Team Meeting",
                "body": "Meeting tomorrow at 10 AM",
                "sender": "manager@company.com"
            },
            {
                "subject": "Urgent: Verify Account",
                "body": "Verify your account now or it will be suspended",
                "sender": "fake@gmail.org"
            }
        ]
    }
    resp = requests.post(f"{BASE_URL}/email/batch", json=payload, timeout=5)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test 7: Report Summary
print("\n[7/7] Report Summary - POST /api/report/summary")
try:
    payload = {
        "emails": [
            {"subject": "Test", "body": "Suspicious email", "sender": "fake@scam.com"},
        ],
        "web_logs": []
    }
    resp = requests.post(f"{BASE_URL}/report/summary", json=payload, timeout=5)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
print("API Test Complete!")
print("=" * 70)
