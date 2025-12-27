from web_dashboard.database import get_email_predictions, get_web_predictions

emails = get_email_predictions(limit=100)
webs = get_web_predictions(limit=100)

print(f'Total Emails in DB: {len(emails)}')
print(f'Total Webs in DB: {len(webs)}')
print()

phishing = [e for e in emails if e.get('prediction') == 'Phishing']
legitimate = [e for e in emails if e.get('prediction') == 'Legitimate']
anomalies = [w for w in webs if w.get('is_anomaly')]

print(f'Phishing Emails: {len(phishing)}')
print(f'Legitimate Emails: {len(legitimate)}')
print(f'Web Anomalies: {len(anomalies)}')
print()

print('First 5 emails:')
for i, e in enumerate(emails[:5], 1):
    print(f"  {i}. prediction='{e.get('prediction')}', subject='{e.get('email_subject', 'N/A')[:40]}'")

print()
print('SONUÇ:')
print(f"  Reports'da gösterilmesi gereken: Phishing={len(phishing)}, Anomalies={len(anomalies)}")
