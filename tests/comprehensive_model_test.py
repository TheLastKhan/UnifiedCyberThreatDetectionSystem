#!/usr/bin/env python3
"""
Comprehensive Model Comparison Test
Tests all three models (BERT, FastText, TF-IDF) with various email types
"""

import requests
import json
import sys

API_URL = 'http://localhost:5001'

test_cases = [
    # ===== CLEARLY LEGITIMATE =====
    {
        'name': 'Business meeting',
        'expected': 'legitimate',
        'subject': 'Meeting Tomorrow',
        'content': 'Hi John, Just a reminder about our meeting tomorrow at 3pm in conference room B. Please bring the project report. Best regards, Sarah.'
    },
    {
        'name': 'Project update',
        'expected': 'legitimate',
        'subject': 'Weekly Report',
        'content': 'Hello team, Attached is the weekly progress report. The deadline has been extended to next Friday. Let me know if you have any questions. Thanks, Mike'
    },
    {
        'name': 'Casual greeting',
        'expected': 'legitimate',
        'subject': 'hi',
        'content': 'hey! whats up? everything is fine!'
    },
    {
        'name': 'Birthday wish',
        'expected': 'legitimate',
        'subject': 'Happy Birthday!',
        'content': 'Happy birthday! Hope you have a great day! Cheers, Tom'
    },
    {
        'name': 'Thank you note',
        'expected': 'legitimate',
        'subject': 'Thanks!',
        'content': 'Thank you so much for your help with the presentation. It went really well. Best, Lisa'
    },
    {
        'name': 'Lunch invitation',
        'expected': 'legitimate',
        'subject': 'Lunch?',
        'content': 'Hey, want to grab lunch today? I was thinking around noon. Let me know!'
    },
    {
        'name': 'Order confirmation',
        'expected': 'legitimate',
        'subject': 'Your Amazon Order',
        'content': 'Thank you for your order! Your package has been shipped and will arrive by Friday. Track your order at amazon.com/orders.'
    },
    {
        'name': 'Newsletter',
        'expected': 'legitimate',
        'subject': 'Weekly Tech News',
        'content': 'This week in tech: Apple announced new products, Google released updates, and Microsoft shared their quarterly results. Read more on our website.'
    },
    {
        'name': 'Job application response',
        'expected': 'legitimate',
        'subject': 'Re: Software Engineer Position',
        'content': 'Dear Applicant, Thank you for applying to our company. We have reviewed your resume and would like to schedule an interview. Please let us know your availability.'
    },
    {
        'name': 'Simple question',
        'expected': 'legitimate',
        'subject': 'Quick question',
        'content': 'Do you have time for a quick call this afternoon? I need to discuss something with you.'
    },
    
    # ===== CLEARLY PHISHING =====
    {
        'name': 'Account suspended',
        'expected': 'phishing',
        'subject': 'URGENT: Account Suspended',
        'content': 'Dear User, Your account has been suspended due to suspicious activity. Click here to verify your identity within 24 hours: http://secure-verify.com/login'
    },
    {
        'name': 'Password reset scam',
        'expected': 'phishing',
        'subject': 'Password Reset Required',
        'content': 'Your password will expire today. Click immediately to reset: http://bit.ly/reset-now. Failure to act will result in account termination.'
    },
    {
        'name': 'Prize scam',
        'expected': 'phishing',
        'subject': 'Congratulations! You Won!',
        'content': 'You have won 1 million dollars! Send your bank account details and SSN to claim your prize immediately.'
    },
    {
        'name': 'PayPal scam',
        'expected': 'phishing',
        'subject': 'PayPal Security Alert',
        'content': 'Dear Customer, We noticed unauthorized access to your PayPal account. Verify your identity now: http://paypa1-secure.ru/verify'
    },
    {
        'name': 'Credential harvest',
        'expected': 'phishing',
        'subject': 'Verify Your Account',
        'content': 'Dear valued customer, Please confirm your credit card number and CVV to avoid account suspension. Click here: http://accounts-verify.tk/update'
    },
    {
        'name': 'Nigerian prince',
        'expected': 'phishing',
        'subject': 'Inheritance Notification',
        'content': 'Dear Friend, I am a Nigerian prince and I need your help to transfer 10 million dollars. Please send your bank account details.'
    },
    {
        'name': 'Bank phishing',
        'expected': 'phishing',
        'subject': 'Important: Bank Account Alert',
        'content': 'Your bank account has been compromised. Login immediately to secure your funds: http://bank-secure-login.com. Enter your PIN and password.'
    },
    {
        'name': 'Apple ID scam',
        'expected': 'phishing',
        'subject': 'Your Apple ID has been locked',
        'content': 'Dear Customer, Your Apple ID has been locked for security reasons. Click here to unlock: http://appleid-verify.ml/unlock. Act within 24 hours.'
    },
    {
        'name': 'Tax refund scam',
        'expected': 'phishing',
        'subject': 'IRS Tax Refund Notification',
        'content': 'You are eligible for a tax refund of $4,500. Click here to claim: http://irs-refund.tk/claim. Provide your SSN and bank details.'
    },
    {
        'name': 'Microsoft scam',
        'expected': 'phishing',
        'subject': 'Microsoft Account Security Alert',
        'content': 'Unusual sign-in activity detected on your Microsoft account. Verify now or your account will be terminated: http://microsoft-verify.ru/secure'
    },
]

def test_bert(payload):
    try:
        r = requests.post(f'{API_URL}/api/email/analyze/bert', json=payload, timeout=60)
        data = r.json()
        return {
            'pred': data.get('prediction', 'error'),
            'score': data.get('score', 0),
            'risk': data.get('risk_level', 'unknown')
        }
    except Exception as e:
        return {'pred': 'error', 'score': 0, 'risk': str(e)[:20]}

def test_fasttext(payload):
    try:
        r = requests.post(f'{API_URL}/api/email/analyze/fasttext', json=payload, timeout=60)
        data = r.json()
        return {
            'pred': data.get('prediction', 'error'),
            'score': data.get('score', 0),
            'risk': data.get('risk_level', 'unknown')
        }
    except Exception as e:
        return {'pred': 'error', 'score': 0, 'risk': str(e)[:20]}

def test_tfidf(payload):
    try:
        r = requests.post(f'{API_URL}/api/email/analyze', json=payload, timeout=60)
        data = r.json()
        if 'model_confidence' in data:
            mc = data['model_confidence']
            return {
                'pred': mc.get('prediction', 'error'),
                'score': mc.get('phishing_probability', 0),
                'risk': mc.get('risk_level', 'unknown')
            }
        return {'pred': 'error', 'score': 0, 'risk': 'no data'}
    except Exception as e:
        return {'pred': 'error', 'score': 0, 'risk': str(e)[:20]}

def main():
    print('=' * 100)
    print('COMPREHENSIVE MODEL COMPARISON TEST')
    print('=' * 100)
    
    correct_counts = {'BERT': 0, 'FastText': 0, 'TF-IDF': 0}
    total = len(test_cases)
    inconsistent_cases = []
    wrong_predictions = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[{i}/{total}] 📧 {test['name']} (Expected: {test['expected'].upper()})")
        print(f"    Subject: {test['subject']}")
        print('-' * 80)
        
        payload = {
            'email_content': test['content'],
            'email_subject': test['subject']
        }
        
        results = {
            'BERT': test_bert(payload),
            'FastText': test_fasttext(payload),
            'TF-IDF': test_tfidf(payload)
        }
        
        # Print results
        for model, res in results.items():
            pred_emoji = '🔴' if res['pred'] == 'phishing' else '🟢' if res['pred'] == 'legitimate' else '⚪'
            correct = '✅' if res['pred'] == test['expected'] else '❌'
            if res['pred'] == test['expected']:
                correct_counts[model] += 1
            print(f"    {model:10} {pred_emoji} {res['pred']:12} Score: {res['score']:.1%}  Risk: {res['risk']:10} {correct}")
        
        # Check consistency
        preds = [r['pred'] for r in results.values() if r['pred'] != 'error']
        if len(set(preds)) > 1:
            inconsistent_cases.append(test['name'])
            print(f"    ⚠️  MODELS DISAGREE!")
        
        # Track wrong predictions
        for model, res in results.items():
            if res['pred'] != test['expected'] and res['pred'] != 'error':
                wrong_predictions.append({
                    'case': test['name'],
                    'model': model,
                    'expected': test['expected'],
                    'got': res['pred'],
                    'score': res['score']
                })
    
    # Summary
    print('\n' + '=' * 100)
    print('SUMMARY')
    print('=' * 100)
    print(f"\nAccuracy:")
    for model, count in correct_counts.items():
        pct = count / total * 100
        print(f"  {model:10}: {count}/{total} ({pct:.1f}%)")
    
    if inconsistent_cases:
        print(f"\n⚠️  Inconsistent cases ({len(inconsistent_cases)}):")
        for case in inconsistent_cases:
            print(f"  - {case}")
    else:
        print(f"\n✅ All models agree on all cases!")
    
    if wrong_predictions:
        print(f"\n❌ Wrong predictions ({len(wrong_predictions)}):")
        for wp in wrong_predictions:
            print(f"  - {wp['case']}: {wp['model']} predicted {wp['got']} (expected {wp['expected']}, score: {wp['score']:.1%})")
    else:
        print(f"\n✅ All predictions correct!")

if __name__ == '__main__':
    main()
