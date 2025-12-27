#!/usr/bin/env python3
"""
Quick TF-IDF Model Tester
Tests the trained model with a known phishing email to diagnose issues.
"""

import pickle
import sys
from pathlib import Path

def test_model():
    print("=" * 60)
    print("TF-IDF MODEL DIAGNOSTIC TEST")
    print("=" * 60)
    
    # Load model and vectorizer
    print("\n1️⃣ Loading model and vectorizer...")
    try:
        model = pickle.load(open('models/email_detector_rf.pkl', 'rb'))
        vectorizer = pickle.load(open('models/tfidf_vectorizer.pkl', 'rb'))
        print(f"   ✅ Model type: {type(model).__name__}")
        print(f"   ✅ Model classes: {model.classes_}")
        print(f"   ✅ Model features: {model.n_features_in_}")
    except Exception as e:
        print(f"   ❌ Error loading model: {e}")
        return
    
    # Test phishing email
    print("\n2️⃣ Testing with known PHISHING email...")
    phishing_email = """
    Dear valued customer,
    
    Your account has been SUSPENDED due to unusual activity.
    Please verify your identity urgently to avoid permanent closure.
    
    Click here to verify: http://paypal-security-verify.com/login.php?user=12345
    
    We need your:
    - Full name
    - Credit card number
    - CVV code
    - Social security number
    
    You must act NOW or your account will be deleted within 24 hours!
    
    PayPal Security Team
    """
    
    try:
        # Vectorize
        X = vectorizer.transform([phishing_email])
        print(f"   ✅ Vectorized: {X.shape} features")
        
        # Predict
        prediction = model.predict(X)[0]
        proba = model.predict_proba(X)[0]
        
        print(f"\n3️⃣ RESULTS:")
        print(f"   Prediction: {prediction} (0=Legitimate, 1=Phishing)")
        print(f"   Probabilities: Legit={proba[0]:.1%}, Phishing={proba[1]:.1%}")
        
        if prediction == 1:
            print(f"\n   ✅ CORRECT! Model detected phishing.")
        else:
            print(f"\n   ❌ WRONG! Model thinks it's legitimate!")
            print(f"   🔍 This indicates a training data or model problem.")
            
    except Exception as e:
        print(f"   ❌ Error during prediction: {e}")
        import traceback
        traceback.print_exc()
    
    # Check feature importance
    print("\n4️⃣ Top 10 important features:")
    try:
        feature_names = vectorizer.get_feature_names_out()
        importances = model.feature_importances_
        top_indices = importances.argsort()[-10:][::-1]
        
        for idx in top_indices:
            print(f"   • {feature_names[idx]}: {importances[idx]:.4f}")
    except Exception as e:
        print(f"   ⚠️ Could not get feature importance: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_model()
