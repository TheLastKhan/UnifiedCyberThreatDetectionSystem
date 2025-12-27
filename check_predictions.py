from web_dashboard.database import SessionLocal, EmailPrediction

db = SessionLocal()

# Check all predictions (case-insensitive)
all_emails = db.query(EmailPrediction).limit(20).all()

print(f"Total emails in DB: {len(all_emails)}")
print("\nPrediction values (first 10):")
for i, email in enumerate(all_emails[:10], 1):
    print(f"  {i}. prediction='{email.prediction}' (type: {type(email.prediction).__name__})")

# Count by value
from collections import Counter
predictions = [e.prediction for e in all_emails]
counts = Counter(predictions)
print(f"\nPrediction counts:")
for pred, count in counts.items():
    print(f"  '{pred}': {count}")

db.close()
