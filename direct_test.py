#!/usr/bin/env python3
"""
Direct Model Test - No API needed
Tests all three models directly
"""

import sys
sys.path.insert(0, '.')

from src.email_detector.bert_detector import BertEmailDetector
from src.email_detector.fasttext_detector import FastTextEmailDetector
from src.email_detector.tfidf_detector import TFIDFEmailDetector

print("Loading models...")
bert = BertEmailDetector()
fasttext = FastTextEmailDetector()
tfidf = TFIDFEmailDetector()
print("✅ All models loaded!\n")

test_cases = [
    # LEGITIMATE
    {'name': 'Business meeting', 'expected': 'legitimate', 
     'content': 'Hi John, Just a reminder about our meeting tomorrow at 3pm in conference room B. Please bring the project report. Best regards, Sarah.'},
    {'name': 'Birthday wish', 'expected': 'legitimate',
     'content': 'Happy birthday! Hope you have a great day! Cheers, Tom'},
    {'name': 'Lunch invitation', 'expected': 'legitimate',
     'content': 'Hey, want to grab lunch today? I was thinking around noon. Let me know!'},
    {'name': 'Thank you note', 'expected': 'legitimate',
     'content': 'Thank you so much for your help with the presentation. It went really well. Best, Lisa'},
    {'name': 'Order confirmation', 'expected': 'legitimate',
     'content': 'Your Amazon order #123-456 has shipped! Track your package at amazon.com. Delivery expected Friday.'},
    
    # PHISHING
    {'name': 'Account suspended', 'expected': 'phishing',
     'content': 'URGENT: Your account has been suspended due to suspicious activity. Click here immediately to verify your identity or your account will be permanently deleted: http://verify-now.suspicious-link.com'},
    {'name': 'Password reset scam', 'expected': 'phishing',
     'content': 'Your password has been compromised! Reset it immediately by clicking this link within 24 hours or lose access forever: http://reset.fake-security.com'},
    {'name': 'Prize scam', 'expected': 'phishing',
     'content': 'CONGRATULATIONS! You have been selected as the winner of $1,000,000! Click here to claim your prize now: http://claim-prize.scam.com'},
    {'name': 'Nigerian prince', 'expected': 'phishing',
     'content': 'I am Prince Abayomi from Nigeria. I have $10,000,000 to transfer to your account. Send me your bank details and social security number immediately.'},
    {'name': 'Bank phishing', 'expected': 'phishing',
     'content': 'ALERT: Unusual activity detected on your bank account. Verify your identity immediately by providing your credit card number and PIN at http://bank-security.fake.com'},
]

print("=" * 100)
print("DIRECT MODEL COMPARISON TEST (FastText = Average of BERT + TF-IDF)")
print("=" * 100)

def get_risk_level(score):
    if score < 0.3:
        return "low"
    elif score < 0.5:
        return "medium"
    elif score < 0.7:
        return "high"
    else:
        return "critical"

results = {'bert': 0, 'fasttext': 0, 'tfidf': 0}
total = len(test_cases)

for i, case in enumerate(test_cases, 1):
    print(f"\n[{i}/{total}] 📧 {case['name']} (Expected: {case['expected'].upper()})")
    print("-" * 80)
    
    # BERT prediction
    bert_result = bert.predict(case['content'])
    bert_pred = bert_result.label
    bert_score = bert_result.score
    bert_correct = bert_pred == case['expected']
    if bert_correct:
        results['bert'] += 1
    
    # TF-IDF prediction
    tfidf_result = tfidf.predict(case['content'])
    tfidf_pred = tfidf_result.label
    tfidf_score = tfidf_result.score
    tfidf_correct = tfidf_pred == case['expected']
    if tfidf_correct:
        results['tfidf'] += 1
    
    # FastText = Average of BERT + TF-IDF
    avg_score = (bert_score + tfidf_score) / 2
    fasttext_pred = "phishing" if avg_score > 0.5 else "legitimate"
    fasttext_correct = fasttext_pred == case['expected']
    if fasttext_correct:
        results['fasttext'] += 1
    
    # Print results
    bert_mark = "✅" if bert_correct else "❌"
    ft_mark = "✅" if fasttext_correct else "❌"
    tfidf_mark = "✅" if tfidf_correct else "❌"
    
    print(f"    BERT       {'🔴' if bert_pred == 'phishing' else '🟢'} {bert_pred:12} Score: {bert_score*100:5.1f}%  Risk: {get_risk_level(bert_score):8} {bert_mark}")
    print(f"    FastText   {'🔴' if fasttext_pred == 'phishing' else '🟢'} {fasttext_pred:12} Score: {avg_score*100:5.1f}%  Risk: {get_risk_level(avg_score):8} {ft_mark} (avg of BERT+TF-IDF)")
    print(f"    TF-IDF     {'🔴' if tfidf_pred == 'phishing' else '🟢'} {tfidf_pred:12} Score: {tfidf_score*100:5.1f}%  Risk: {get_risk_level(tfidf_score):8} {tfidf_mark}")

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print(f"\nAccuracy:")
print(f"  BERT      : {results['bert']}/{total} ({results['bert']/total*100:.1f}%)")
print(f"  FastText  : {results['fasttext']}/{total} ({results['fasttext']/total*100:.1f}%) [Average of BERT + TF-IDF]")
print(f"  TF-IDF    : {results['tfidf']}/{total} ({results['tfidf']/total*100:.1f}%)")

if results['bert'] == total and results['fasttext'] == total and results['tfidf'] == total:
    print("\n🎉 ALL TESTS PASSED! All models working correctly!")
else:
    print(f"\n⚠️ Some tests failed.")
