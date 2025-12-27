"""
Quick test of the ensemble voting API endpoint
"""
import requests
import json

url = "http://localhost:5000/api/email/analyze/ensemble"

# Test phishing email
test_data = {
    "email_content": """
    URGENT! Your PayPal account has been suspended.
    Please verify your credit card and CVV immediately.
    Click here: http://paypal-security-verify.com/
    You have 24 hours to act!
    """,
    "email_sender": "security@paypal-verify.com",
    "email_subject": "URGENT: Account Suspended"
}

print("Testing Ensemble Voting API...")
print("="*70)
print(f"Endpoint: {url}")
print(f"\nSending phishing email test...")

try:
    response = requests.post(url, json=test_data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS!")
        print("="*70)
        
        # Ensemble result
        ensemble = result.get('ensemble', {})
        print(f"\n🎯 ENSEMBLE PREDICTION:")
        print(f"   Prediction: {ensemble.get('prediction', 'N/A').upper()}")
        print(f"   Confidence: {ensemble.get('confidence', 0)*100:.1f}%")
        print(f"   Weighted Score: {ensemble.get('weighted_score', 0)*100:.1f}%")
        print(f"   Risk Level: {ensemble.get('risk_level', 'N/A').upper()}")
        print(f"   Models Used: {', '.join(ensemble.get('models_used', []))}")
        print(f"\n   Weights Applied:")
        for model, weight in ensemble.get('weights_applied', {}).items():
            print(f"      {model}: {weight*100:.0f}%")
        
        # Individual models
        models = result.get('models', {})
        if models:
            print(f"\n📊 INDIVIDUAL MODELS:")
            for model_name, model_result in models.items():
                print(f"\n   {model_name.upper()}:")
                print(f"      Prediction: {model_result.get('prediction', 'N/A')}")
                print(f"      Score: {model_result.get('score', 0)*100:.1f}%")
                print(f"      Time: {model_result.get('time_ms', 0):.1f}ms")
        
        print(f"\n⏱️ Total Processing Time: {result.get('total_processing_time_ms', 0):.1f}ms")
        print("="*70)
        
    else:
        print(f"\n❌ ERROR: Status {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Cannot connect to API. Is Docker running?")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
