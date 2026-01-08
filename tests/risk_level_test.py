#!/usr/bin/env python3
"""
Comprehensive Risk Level & Label Consistency Test
Tests that risk levels (low, medium, high, critical) align with predictions
"""

import requests
import json
from typing import Dict, List, Tuple

API_BASE = "http://localhost:5000/api"

# Test cases with expected risk levels
# Format: (name, subject, body, expected_label, expected_risk_range)
# Risk ranges: "low" (0-30%), "medium" (30-60%), "high" (60-85%), "critical" (85-100%)

TEST_CASES = [
    # ==================== CLEARLY LEGITIMATE (LOW RISK) ====================
    {
        "name": "Friendly hello",
        "subject": "Hi there",
        "body": "Hey! How are you doing? Hope you're having a great day!",
        "expected_label": "legitimate",
        "expected_risk": "low",
        "max_score": 30
    },
    {
        "name": "Team meeting invite",
        "subject": "Team Meeting Tomorrow at 2pm",
        "body": "Hi team, Just a reminder that we have our weekly sync meeting tomorrow at 2pm in Conference Room B. Please bring your project updates. Best regards, Sarah",
        "expected_label": "legitimate",
        "expected_risk": "low",
        "max_score": 30
    },
    {
        "name": "Project status update",
        "subject": "Q4 Project Status",
        "body": "Hi everyone, Attached is the quarterly report for your review. The deadline for feedback is Friday. Let me know if you have any questions. Thanks, Mike",
        "expected_label": "legitimate",
        "expected_risk": "low",
        "max_score": 30
    },
    {
        "name": "Lunch invitation",
        "subject": "Lunch tomorrow?",
        "body": "Hey, want to grab lunch tomorrow? There's a new Italian place downtown I've been wanting to try. Let me know!",
        "expected_label": "legitimate",
        "expected_risk": "low",
        "max_score": 30
    },
    {
        "name": "Thank you note",
        "subject": "Thanks for your help!",
        "body": "I just wanted to say thank you for helping me with the presentation yesterday. It went really well! Coffee's on me next time.",
        "expected_label": "legitimate",
        "expected_risk": "low",
        "max_score": 30
    },
    {
        "name": "Amazon order confirmation",
        "subject": "Your Amazon.com order has shipped",
        "body": "Your order #123-4567890 has been shipped! Track your package at amazon.com/orders. Estimated delivery: January 10. Thank you for shopping with us.",
        "expected_label": "legitimate",
        "expected_risk": "low",
        "max_score": 35
    },
    {
        "name": "LinkedIn connection",
        "subject": "John Smith wants to connect on LinkedIn",
        "body": "Hi, I'd like to add you to my professional network on LinkedIn. We met at the tech conference last week. Looking forward to staying in touch!",
        "expected_label": "legitimate",
        "expected_risk": "low",
        "max_score": 30
    },
    {
        "name": "Birthday wishes",
        "subject": "Happy Birthday!",
        "body": "Wishing you a wonderful birthday filled with joy and happiness! Hope you have an amazing day celebrating with family and friends.",
        "expected_label": "legitimate",
        "expected_risk": "low",
        "max_score": 30
    },
    {
        "name": "Newsletter subscription",
        "subject": "This Week in Tech News",
        "body": "Welcome to our weekly newsletter! This week: Apple announced new products, Google updates Chrome, and Microsoft releases new features. Unsubscribe anytime.",
        "expected_label": "legitimate",
        "expected_risk": "low",
        "max_score": 35
    },
    {
        "name": "Job application response",
        "subject": "Re: Software Engineer Application",
        "body": "Thank you for your application. We reviewed your resume and would like to schedule an interview. Please let us know your availability next week. HR Team",
        "expected_label": "legitimate",
        "expected_risk": "low",
        "max_score": 35
    },
    
    # ==================== SLIGHTLY SUSPICIOUS (MEDIUM-HIGH RISK) ====================
    # These could be legitimate but contain suspicious keywords, so some models may flag them
    {
        "name": "Generic account notice",
        "subject": "Account Update",
        "body": "Your account settings have been updated. If you did not make this change, please contact support.",
        "expected_label": "phishing",  # Contains "account" - suspicious
        "expected_risk": "medium",
        "min_score": 30,
        "max_score": 80
    },
    {
        "name": "Vague security message",
        "subject": "Security Notice",
        "body": "We noticed some activity on your account. For your security, we recommend reviewing your recent activity.",
        "expected_label": "phishing",  # Contains "security", "account" - suspicious
        "expected_risk": "high",
        "min_score": 50,
        "max_score": 100
    },
    
    # ==================== SUSPICIOUS (HIGH RISK) ====================
    {
        "name": "Urgent account warning",
        "subject": "URGENT: Account Issue",
        "body": "There is an urgent issue with your account. Please review immediately to avoid any disruption to your service.",
        "expected_label": "phishing",
        "expected_risk": "high",
        "min_score": 55,
        "max_score": 100
    },
    {
        "name": "Password expiry notice",
        "subject": "Your password will expire",
        "body": "Your password is expiring soon. Click the link below to update your password and maintain access to your account.",
        "expected_label": "phishing",
        "expected_risk": "high",
        "min_score": 55,
        "max_score": 90
    },
    
    # ==================== DEFINITELY PHISHING (CRITICAL RISK) ====================
    {
        "name": "Account suspended scam",
        "subject": "URGENT: Your Account Has Been Suspended!",
        "body": "Your account has been suspended due to suspicious activity! Click here immediately to verify your identity: http://bit.ly/verify-now. Failure to act within 24 hours will result in permanent account deletion.",
        "expected_label": "phishing",
        "expected_risk": "critical",
        "min_score": 85
    },
    {
        "name": "PayPal scam",
        "subject": "PayPal Security Alert - Immediate Action Required",
        "body": "We detected unusual login activity on your PayPal account. Your account has been limited. Confirm your identity now: http://paypa1-security.tk/verify. Enter your password, SSN, and credit card details.",
        "expected_label": "phishing",
        "expected_risk": "critical",
        "min_score": 90
    },
    {
        "name": "Bank credential theft",
        "subject": "Important: Bank Account Alert",
        "body": "Dear Customer, We have detected suspicious activity on your bank account. To prevent unauthorized access, verify your account immediately by clicking: http://bank-secure.ru/verify. Enter your account number, password, and PIN.",
        "expected_label": "phishing",
        "expected_risk": "critical",
        "min_score": 90
    },
    {
        "name": "Prize scam",
        "subject": "Congratulations! You've Won $1,000,000!",
        "body": "CONGRATULATIONS! You have been selected as the winner of our international lottery! To claim your $1,000,000 prize, wire $500 processing fee to our agent. Send your bank details and SSN immediately!",
        "expected_label": "phishing",
        "expected_risk": "critical",
        "min_score": 90
    },
    {
        "name": "Nigerian prince scam",
        "subject": "Urgent Business Proposal - $15 Million",
        "body": "I am Prince Ahmed from Nigeria. My late father left $15 million in a secret bank account. I need your help to transfer this money. You will receive 30% share. Please send your bank account details and $1000 transfer fee.",
        "expected_label": "phishing",
        "expected_risk": "critical",
        "min_score": 85
    },
    {
        "name": "Apple ID phishing",
        "subject": "Your Apple ID has been locked",
        "body": "Your Apple ID has been locked for security reasons. Someone tried to access your account. Click here to unlock: http://apple-verify.ml/unlock. Enter your Apple ID, password, credit card number, and security code.",
        "expected_label": "phishing",
        "expected_risk": "critical",
        "min_score": 90
    },
    {
        "name": "Microsoft scam",
        "subject": "Microsoft Account Security Alert",
        "body": "URGENT: Your Microsoft account will be terminated in 24 hours! Unusual sign-in detected from Russia. Verify immediately: http://microsoft-secure.tk/verify. Provide your email, password, and phone number.",
        "expected_label": "phishing",
        "expected_risk": "critical",
        "min_score": 90
    },
    {
        "name": "Tax refund scam",
        "subject": "IRS Tax Refund Notification",
        "body": "You are eligible for a tax refund of $4,521.00. To receive your refund, verify your identity at: http://irs-refund.cn/claim. Provide your SSN, bank account number, and date of birth.",
        "expected_label": "phishing",
        "expected_risk": "critical",
        "min_score": 90
    },
    {
        "name": "Crypto scam",
        "subject": "Double Your Bitcoin NOW!",
        "body": "LIMITED TIME OFFER! Send 1 BTC and receive 2 BTC back! This is a promotional event by Elon Musk. Send to wallet: 1ABC123XYZ. Act now before it's too late! Only 100 spots remaining!",
        "expected_label": "phishing",
        "expected_risk": "critical",
        "min_score": 85
    },
    {
        "name": "Tech support scam",
        "subject": "Your Computer Has Been Infected!",
        "body": "VIRUS ALERT! Your computer has been infected with malware. Call our tech support immediately at 1-800-FAKE-NUM. Our certified technicians will help you. You need to provide remote access and pay $299 for cleanup.",
        "expected_label": "phishing",
        "expected_risk": "critical",
        "min_score": 85
    },
    {
        "name": "Shipping scam",
        "subject": "Package Delivery Failed - Action Required",
        "body": "Your package could not be delivered. To reschedule delivery, click: http://fedex-delivery.ru/reschedule. Pay the $2.99 redelivery fee with your credit card. Provide card number, expiry, and CVV.",
        "expected_label": "phishing",
        "expected_risk": "critical",
        "min_score": 85
    },
]

def get_risk_level(score: float) -> str:
    """Convert score to risk level"""
    if score < 30:
        return "low"
    elif score < 60:
        return "medium"
    elif score < 85:
        return "high"
    else:
        return "critical"

def test_email(model: str, subject: str, body: str) -> Dict:
    """Test a single email against a model"""
    try:
        email_content = f"Subject: {subject}\n\n{body}"
        response = requests.post(
            f"{API_BASE}/email/analyze/{model}" if model != "tfidf" else f"{API_BASE}/email/analyze",
            json={"email_content": email_content},
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def format_result(label: str, score: float, expected_label: str, expected_risk: str, 
                  min_score: int = 0, max_score: int = 100) -> Tuple[str, bool, bool]:
    """Format and validate result"""
    score_pct = score * 100 if score <= 1 else score
    actual_risk = get_risk_level(score_pct)
    
    # Check label correctness
    label_correct = label.lower() == expected_label.lower()
    
    # Check risk level appropriateness
    risk_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    expected_risk_val = risk_order.get(expected_risk, 0)
    actual_risk_val = risk_order.get(actual_risk, 0)
    
    # Risk is acceptable if within 1 level
    risk_acceptable = abs(expected_risk_val - actual_risk_val) <= 1
    
    # Also check score bounds if specified
    score_in_bounds = True
    if min_score > 0 and score_pct < min_score:
        score_in_bounds = False
    if max_score < 100 and score_pct > max_score:
        score_in_bounds = False
    
    # Emoji indicators
    label_icon = "✅" if label_correct else "❌"
    risk_icon = "✅" if risk_acceptable else "⚠️"
    
    return f"{label_icon} {label:11s} {score_pct:5.1f}% ({actual_risk:8s}) {risk_icon}", label_correct, risk_acceptable

def run_tests():
    """Run all tests"""
    print("=" * 120)
    print("COMPREHENSIVE RISK LEVEL & LABEL CONSISTENCY TEST")
    print("=" * 120)
    print()
    print("Risk Level Ranges: LOW (0-30%) | MEDIUM (30-60%) | HIGH (60-85%) | CRITICAL (85-100%)")
    print()
    
    models = ["bert", "fasttext", "tfidf"]
    results = {m: {"label_correct": 0, "risk_correct": 0, "total": 0} for m in models}
    
    issues = []
    
    for i, test in enumerate(TEST_CASES, 1):
        name = test["name"]
        subject = test["subject"]
        body = test["body"]
        expected_label = test["expected_label"]
        expected_risk = test["expected_risk"]
        min_score = test.get("min_score", 0)
        max_score = test.get("max_score", 100)
        
        print(f"[{i:2d}/{len(TEST_CASES)}] 📧 {name}")
        print(f"        Expected: {expected_label.upper()} | Risk: {expected_risk.upper()}", end="")
        if min_score > 0 or max_score < 100:
            print(f" | Score: {min_score}-{max_score}%", end="")
        print()
        print("-" * 120)
        
        model_results = []
        for model in models:
            result = test_email(model, subject, body)
            
            if "error" in result:
                print(f"    {model.upper():10s} ❌ Error: {result['error']}")
                continue
            
            # Extract prediction - handle different API response formats
            if model == "tfidf":
                # TF-IDF has nested model_confidence structure
                mc = result.get("model_confidence", {})
                label = mc.get("prediction", "unknown")
                score = mc.get("phishing_probability", 0.5)
            else:
                # BERT and FastText have flat response
                label = result.get("label", result.get("prediction", "unknown"))
                score = result.get("phishing_score", result.get("score", 0.5))
            
            formatted, label_ok, risk_ok = format_result(
                label, score, expected_label, expected_risk, min_score, max_score
            )
            
            print(f"    {model.upper():10s} {formatted}")
            
            results[model]["total"] += 1
            if label_ok:
                results[model]["label_correct"] += 1
            if risk_ok:
                results[model]["risk_correct"] += 1
            
            if not label_ok or not risk_ok:
                score_pct = score * 100 if score <= 1 else score
                issues.append({
                    "test": name,
                    "model": model.upper(),
                    "expected": f"{expected_label}/{expected_risk}",
                    "got": f"{label}/{get_risk_level(score_pct)} ({score_pct:.1f}%)",
                    "label_issue": not label_ok,
                    "risk_issue": not risk_ok
                })
            
            model_results.append((model, label, score))
        
        # Check model agreement
        labels = [r[1].lower() for r in model_results]
        if len(set(labels)) > 1:
            print(f"    ⚠️  MODELS DISAGREE ON LABEL!")
        
        print()
    
    # Summary
    print("=" * 120)
    print("SUMMARY")
    print("=" * 120)
    print()
    
    print("Label Accuracy:")
    for model in models:
        r = results[model]
        pct = (r["label_correct"] / r["total"] * 100) if r["total"] > 0 else 0
        print(f"  {model.upper():10s}: {r['label_correct']}/{r['total']} ({pct:.1f}%)")
    
    print()
    print("Risk Level Accuracy (within 1 level tolerance):")
    for model in models:
        r = results[model]
        pct = (r["risk_correct"] / r["total"] * 100) if r["total"] > 0 else 0
        print(f"  {model.upper():10s}: {r['risk_correct']}/{r['total']} ({pct:.1f}%)")
    
    if issues:
        print()
        print(f"⚠️  Issues Found ({len(issues)}):")
        for issue in issues:
            issue_type = []
            if issue["label_issue"]:
                issue_type.append("LABEL")
            if issue["risk_issue"]:
                issue_type.append("RISK")
            print(f"  - {issue['test']} ({issue['model']}): Expected {issue['expected']}, Got {issue['got']} [{', '.join(issue_type)}]")
    else:
        print()
        print("✅ All tests passed! Labels and risk levels are consistent.")
    
    print()
    print("=" * 120)
    
    # Return overall success
    total_label = sum(r["label_correct"] for r in results.values())
    total_risk = sum(r["risk_correct"] for r in results.values())
    total_tests = sum(r["total"] for r in results.values())
    
    return total_label == total_tests and total_risk == total_tests

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
