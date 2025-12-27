import requests
import json

# Test Dashboard API
d = requests.get('http://localhost:5000/api/dashboard').json()
print("=" * 50)
print("DASHBOARD API:")
print(f"  Phishing Emails: {d.get('phishing_emails', 'N/A')}")
print(f"  Anomalous Requests: {d.get('anomalous_requests', 'N/A')}")
print()

# Test Reports API
r = requests.get('http://localhost:5000/api/reports/summary').json()
print("=" * 50)
print("REPORTS API:")
print(f"  Phishing Count: {r.get('phishing_count', 'N/A')}")
print(f"  Anomalies Count: {r.get('anomalies_count', 'N/A')}")
print(f"  Total Threats: {r.get('total_threats', 'N/A')}")
print()

# Check patterns field
preds = r['recent_predictions']
web_preds = [p for p in preds if p['type'] == 'web']
if web_preds:
    print("=" * 50)
    print("PATTERNS CHECK (first 3 web predictions):")
    for i, p in enumerate(web_preds[:3], 1):
        print(f"  {i}. IP: {p.get('ip_address', 'N/A')}, Patterns: {p.get('patterns_detected', 'MISSING FIELD')}")
