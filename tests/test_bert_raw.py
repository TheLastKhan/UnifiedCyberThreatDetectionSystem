#!/usr/bin/env python3
"""Test BERT model directly to check labels"""

from src.email_detector.bert_detector import BertEmailDetector

# Test emails
emails = {
    "Normal": "Hello, this is our weekly company newsletter with updates.",
    "Suspicious": "Your account needs verification. Update payment details.",
    "Phishing": "URGENT! Click here NOW to verify your PayPal account: http://fake-paypal.com",
    "Very Phishing": "🚨 CRITICAL! Your bank account HACKED! Enter SSN and credit card NOW!"
}

print("\n" + "="*60)
print("BERT MODEL RAW OUTPUT TEST")
print("="*60)

detector = BertEmailDetector(model_path="models/bert_finetuned")

for name, text in emails.items():
    print(f"\n📧 {name}:")
    print(f"   Text: {text[:80]}...")
    
    # Raw pipeline output
    import torch
    with torch.no_grad():
        raw_output = detector.pipeline(text, truncation=True)[0]
    
    print(f"   Raw Label: {raw_output['label']}")
    print(f"   Raw Score: {raw_output['score']:.4f}")
    
    # Processed output
    result = detector.predict(text)
    print(f"   → Processed Label: {result.label}")
    print(f"   → Phishing Score: {result.score:.4f}")
    print(f"   → Confidence: {result.confidence:.4f}")

print("\n" + "="*60)
