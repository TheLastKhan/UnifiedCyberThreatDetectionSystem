#!/usr/bin/env python3
"""
BERT Diagnostic Script
Analyzes BERT predictions to identify why accuracy is 48.2% in evaluation vs 100% in production.
"""

import sys
sys.path.append('src')

import pandas as pd
from email_detector.bert_detector import BertEmailDetector

# Load test data
print("Loading test data...")
df = pd.read_csv('data/processed/dataset/phishing_email.csv', encoding='utf-8')

# Find text column
text_col = None
for col in ['body', 'text', 'text_combined', 'message']:
    if col in df.columns:
        text_col = col
        break

df = df[[text_col, 'label']].dropna()
df = df[df[text_col].str.len() > 20]

# Sample 100 for quick analysis
df_sample = df.sample(n=100, random_state=42).reset_index(drop=True)

print(f"Loaded {len(df_sample)} samples")
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
        # FALSE NEGATIVE - missed phishing!
        wrong_phishing_as_legit.append({
            'text_preview': text[:100],
            'score': result.score,
            'confidence': result.confidence
        })
    elif true_label == 0 and pred_label == 1:
        # FALSE POSITIVE - legit marked as phishing
        wrong_legit_as_phishing.append({
            'text_preview': text[:100],
            'score': result.score,
            'confidence': result.confidence
        })
    
    if (i + 1) % 20 == 0:
        print(f"  Processed {i+1}/100...")

# Summary
print("\n" + "="*70)
print("BERT DIAGNOSTIC RESULTS")
print("="*70)

total_phishing = sum(df_sample['label']==1)
total_legit = sum(df_sample['label']==0)

print(f"\n📊 Overall:")
print(f"  Correct Phishing: {correct_phishing}/{total_phishing} ({correct_phishing/total_phishing*100:.1f}%)")
print(f"  Correct Legit: {correct_legit}/{total_legit} ({correct_legit/total_legit*100:.1f}%)")
print(f"  Accuracy: {(correct_phishing + correct_legit)/100*100:.1f}%")

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

# Analysis
print("\n" + "="*70)
print("DIAGNOSIS:")
print("="*70)

if correct_phishing + correct_legit > 85:
    print("✅ BERT is working well! Evaluation script may have had issues.")
elif len(wrong_phishing_as_legit) > len(wrong_legit_as_phishing) * 2:
    print("⚠️ BERT has LOW RECALL - missing many phishing emails!")
    print("   This suggests model needs retraining on phishing data.")
elif len(wrong_legit_as_phishing) > len(wrong_phishing_as_legit) * 2:
    print("⚠️ BERT has LOW PRECISION - too many false alarms!")
    print("   Model may be overfitted to see phishing everywhere.")
else:
    print("⚠️ BERT has BALANCED ERRORS - general performance issue.")
    print("   Consider retraining with current phishing_email.csv dataset.")

print("="*70)
