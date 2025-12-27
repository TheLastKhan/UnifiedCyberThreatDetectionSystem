#!/usr/bin/env python3
"""
BERT Diagnostic on CEAS_08 Dataset
Tests BERT on its original training dataset to verify performance.
"""

import sys
sys.path.append('src')

import pandas as pd
from email_detector.bert_detector import BertEmailDetector

# Load CEAS_08 dataset
print("Loading CEAS_08 dataset...")
df = pd.read_csv('data/processed/dataset/CEAS_08.csv', encoding='utf-8')

# Find text column (should be 'body' based on training)
text_col = 'body' if 'body' in df.columns else None
if text_col is None:
    for col in ['text', 'text_combined', 'message']:
        if col in df.columns:
            text_col = col
            break

if text_col is None:
    print(f"❌ No text column found! Columns: {df.columns.tolist()}")
    sys.exit(1)

df = df[[text_col, 'label']].dropna()
df = df[df[text_col].str.len() > 20]

# Sample 200 for comprehensive test
df_sample = df.sample(n=200, random_state=42).reset_index(drop=True)

print(f"Loaded {len(df_sample)} samples from CEAS_08")
print(f"Phishing: {sum(df_sample['label']==1)}, Legitimate: {sum(df_sample['label']==0)}")

# Load BERT
print("\nLoading BERT model...")
detector = BertEmailDetector(model_path='models/bert_phishing_detector')
print("Model loaded!\n")

# Analyze predictions
correct_phishing = 0
correct_legit = 0
wrong_phishing_as_legit = []
wrong_legit_as_phishing = []

print("Analyzing predictions...")
for i, row in df_sample.iterrows():
    text = row[text_col]
    true_label = row['label']
    
    result = detector.predict(text)
    pred_label = 1 if result.label == 'phishing' else 0
    
    # Check correctness
    if true_label == 1 and pred_label == 1:
        correct_phishing += 1
    elif true_label == 0 and pred_label == 0:
        correct_legit += 1
    elif true_label == 1 and pred_label == 0:
        wrong_phishing_as_legit.append({
            'text_preview': text[:100],
            'score': result.score,
            'confidence': result.confidence
        })
    elif true_label == 0 and pred_label == 1:
        wrong_legit_as_phishing.append({
            'text_preview': text[:100],
            'score': result.score,
            'confidence': result.confidence
        })
    
    if (i + 1) % 50 == 0:
        print(f"  Processed {i+1}/200...")

# Summary
print("\n" + "="*70)
print("BERT DIAGNOSTIC ON CEAS_08 (ORIGINAL TRAINING DATASET)")
print("="*70)

total_phishing = sum(df_sample['label']==1)
total_legit = sum(df_sample['label']==0)

print(f"\n📊 Overall:")
print(f"  Correct Phishing: {correct_phishing}/{total_phishing} ({correct_phishing/total_phishing*100:.1f}%)")
print(f"  Correct Legit: {correct_legit}/{total_legit} ({correct_legit/total_legit*100:.1f}%)")
accuracy = (correct_phishing + correct_legit)/200*100
print(f"  Accuracy: {accuracy:.1f}%")

print(f"\n❌ False Negatives (Phishing → Legit): {len(wrong_phishing_as_legit)}")
if wrong_phishing_as_legit:
    print("  Sample mispredictions:")
    for i, item in enumerate(wrong_phishing_as_legit[:3]):
        print(f"\n  {i+1}. Score: {item['score']:.3f}, Confidence: {item['confidence']:.3f}")
        print(f"     Text: {item['text_preview']}...")

print(f"\n⚠️ False Positives (Legit → Phishing): {len(wrong_legit_as_phishing)}")
if wrong_legit_as_phishing:
    print("  Sample mispredictions:")
    for i, item in enumerate(wrong_legit_as_phishing[:3]):
        print(f"\n  {i+1}. Score: {item['score']:.3f}, Confidence: {item['confidence']:.3f}")
        print(f"     Text: {item['text_preview']}...")

# Comparison
print("\n" + "="*70)
print("📊 COMPARISON:")
print("="*70)
print(f"CEAS_08 (original training): {accuracy:.1f}% accuracy")
print(f"phishing_email.csv (current): 48.2% accuracy (from earlier test)")
print("\n💡 ANALYSIS:")

if accuracy > 95:
    print("✅ BERT performs EXCELLENTLY on CEAS_08!")
    print("⚠️ But poorly on phishing_email.csv")
    print("🔍 CONCLUSION: Dataset mismatch confirmed!")
    print("   → BERT needs retraining on phishing_email.csv for production use.")
elif accuracy > 85:
    print("✅ BERT performs WELL on CEAS_08")
    print("⚠️ Some drift from original training")
    print("   → Consider retraining for best results.")
else:
    print("⚠️ BERT performs POORLY even on original dataset")
    print("   → Model may be corrupted or outdated")
    print("   → Definitely needs retraining!")

print("="*70)
