import requests

# Get reports data
r = requests.get('http://localhost:5000/api/reports/summary')
data = r.json()

print("REPORTS API DATA:")
print(f"  Phishing Count: {data.get('phishing_count')}")
print(f"  Anomalies Count: {data.get('anomalies_count')}")
print(f"  Total Threats: {data.get('total_threats')}")
print()

# Check recent predictions
emails = [p for p in data.get('recent_predictions', []) if p['type'] == 'email']
webs = [p for p in data.get('recent_predictions', []) if p['type'] == 'web']

print(f"Email predictions in recent: {len(emails)}")
print(f"Web predictions in recent: {len(webs)}")
print()

if emails:
    print("First 5 email predictions:")
    for i, e in enumerate(emails[:5], 1):
        print(f"  {i}. {e.get('details', 'N/A')[:50]}")
print()

# Açıklama
print("=" * 60)
print("DURUM:")
print(f"  ✅ Anomalies = {data.get('anomalies_count')} (Web predictions tablosunda is_anomaly=True kayıtlar var)")
print(f"  ❌ Phishing = {data.get('phishing_count')} (Email predictions tablosunda prediction='Phishing' kayıt YOK)")
print()
print("NEDEN?")
print("  - Web anomalies: Önceden web log analysis yapıldı, kayıtlar eklendi")
print("  - Phishing: Email analysis yapılmadı VEYA yapılan tüm emailler 'Legitimate' çıktı")
