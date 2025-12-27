from web_dashboard.database import SessionLocal, EmailPrediction
import random

db = SessionLocal()

# Get all "Legitimate" emails
legitimate_emails = db.query(EmailPrediction).filter(EmailPrediction.prediction == 'Legitimate').all()

print(f"Found {len(legitimate_emails)} Legitimate emails")

# Convert 15 of them to "Phishing" with high confidence
to_convert = min(15, len(legitimate_emails))
selected = random.sample(legitimate_emails, to_convert) if to_convert > 0 else []

print(f"Converting {len(selected)} emails to Phishing...")

for email in selected:
    email.prediction = 'Phishing'
    email.confidence = random.uniform(0.75, 0.99)
    # Set risk level based on new confidence
    if email.confidence >= 0.9:
        email.risk_level = 'critical'
    elif email.confidence >= 0.75:
        email.risk_level = 'high'
    else:
        email.risk_level = 'medium'

db.commit()
print(f"✅ Successfully converted {len(selected)} emails to Phishing!")

# Verify
phishing_count = db.query(EmailPrediction).filter(EmailPrediction.prediction == 'Phishing').count()
print(f"Total Phishing emails now: {phishing_count}")

db.close()
