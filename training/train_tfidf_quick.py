"""
Quick TF-IDF Model Training Script
===================================
Trains TF-IDF + Random Forest model on email dataset
Estimated time: 2-3 minutes for 31,323 emails
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("="*70)
print("🚀 TF-IDF + Random Forest Training")
print("="*70)

# Step 1: Load data
print("\n[1/4] Loading email dataset...")
start_time = time.time()

from src.utils.data_loader import DataLoader

loader = DataLoader()
texts, labels = loader.load_all_emails()

load_time = time.time() - start_time
print(f"✅ Loaded {len(texts)} emails in {load_time:.2f} seconds")
print(f"   - Phishing: {sum(labels)} emails")
print(f"   - Legitimate: {len(labels) - sum(labels)} emails")

# Step 2: Initialize detector
print("\n[2/4] Initializing TF-IDF detector...")
from src.email_detector.detector import EmailPhishingDetector
import pandas as pd

detector = EmailPhishingDetector()
print("✅ Detector initialized")

# Step 3: Prepare DataFrame
print("\n[3/5] Preparing data...")
emails_df = pd.DataFrame({
    'body': texts,
    'sender': [''] * len(texts),  # Empty senders
    'subject': [''] * len(texts)  # Empty subjects
})
print(f"✅ DataFrame prepared with {len(emails_df)} rows")

# Step 4: Train model
print("\n[4/5] Training model...")
print("   This will take 2-3 minutes...")
train_start = time.time()

detector.train(emails_df, labels)

train_time = time.time() - train_start
print(f"✅ Training completed in {train_time:.2f} seconds ({train_time/60:.1f} minutes)")

# Step 5: Save model
print("\n[4/4] Saving trained model...")
save_start = time.time()

# Create models directory if not exists
os.makedirs('models', exist_ok=True)

# Save model
detector.save_model('models/email_detector_tfidf_trained.pkl')

save_time = time.time() - save_start
total_time = time.time() - start_time

print(f"✅ Model saved to models/email_detector_tfidf_trained.pkl")
print(f"   Save time: {save_time:.2f} seconds")

# Summary
print("\n" + "="*70)
print("📊 TRAINING SUMMARY")
print("="*70)
print(f"Dataset size: {len(texts)} emails")
print(f"Load time: {load_time:.2f}s")
print(f"Train time: {train_time:.2f}s ({train_time/60:.1f} min)")
print(f"Save time: {save_time:.2f}s")
print(f"Total time: {total_time:.2f}s ({total_time/60:.1f} min)")
print("\n✅ TF-IDF model is ready for production!")
print("="*70)

# Test the model
print("\n🧪 Quick Test...")
test_emails = [
    "URGENT! Your PayPal account will be suspended. Click here to verify.",
    "Hi John, meeting at 2 PM tomorrow. Best regards, Sarah"
]

for i, email in enumerate(test_emails, 1):
    result = detector.predict_with_explanation(email, "", "")
    print(f"\n{i}. Email: {email[:60]}...")
    print(f"   Prediction: {result['prediction']}")
    print(f"   Confidence: {result['confidence']:.2f}%")

print("\n" + "="*70)
print("🎉 All done! TF-IDF model trained successfully!")
print("="*70)
