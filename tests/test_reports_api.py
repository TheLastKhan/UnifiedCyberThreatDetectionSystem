import requests

# Test Reports API
r = requests.get('http://localhost:5000/api/reports/summary')
data = r.json()

print("=" * 50)
print("REPORTS API RESPONSE:")
print(f"  Phishing Count: {data.get('phishing_count')}")
print(f"  Anomalies Count: {data.get('anomalies_count')}")
print(f"  Total Threats: {data.get('total_threats')}")

# Check email predictions
email_count = len([p for p in data.get('recent_predictions', []) if p['type'] == 'email'])
phishing_in_predictions = len([p for p in data.get('recent_predictions', []) 
                                if p['type'] == 'email' and 
                                p.get('details', '').lower().find('phishing') >= 0])

print("\nIN RECENT PREDICTIONS:")
print(f"  Total Emails: {email_count}")
print(f"  Contains 'phishing' in details: {phishing_in_predictions}")
