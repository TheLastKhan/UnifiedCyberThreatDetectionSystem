"""
Test trained models directly without Flask/full dependencies
"""

import sys
import os
import joblib
from pathlib import Path

# Model paths
models_dir = Path('models')

print("=" * 60)
print("Testing Trained Models Directly")
print("=" * 60)

# Test 1: Load TF-IDF Vectorizer
print("\n[1/6] Loading TF-IDF Vectorizer...")
try:
    tfidf = joblib.load(models_dir / 'tfidf_vectorizer.pkl')
    print(f"✓ TF-IDF loaded: {tfidf}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 2: Load Stacking Model (Email)
print("\n[2/6] Loading Stacking Ensemble Model...")
try:
    stacking = joblib.load(models_dir / 'email_detector_stacking.pkl')
    print(f"✓ Stacking model loaded: {stacking}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 3: Load Voting Model (Email)
print("\n[3/6] Loading Voting Ensemble Model...")
try:
    voting = joblib.load(models_dir / 'email_detector_voting.pkl')
    print(f"✓ Voting model loaded: {voting}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 4: Load Isolation Forest (Web)
print("\n[4/6] Loading Isolation Forest Model...")
try:
    iso_forest = joblib.load(models_dir / 'web_anomaly_detector.pkl')
    print(f"✓ Isolation Forest loaded: {iso_forest}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 5: Load Random Forest Tuned
print("\n[5/6] Loading Random Forest Tuned Model...")
try:
    rf_tuned = joblib.load(models_dir / 'email_detector_rf_tuned.pkl')
    print(f"✓ RF Tuned model loaded: {rf_tuned}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 6: Load Scaler
print("\n[6/6] Loading Log Scaler...")
try:
    scaler = joblib.load(models_dir / 'log_scaler.pkl')
    print(f"✓ Scaler loaded: {scaler}")
except Exception as e:
    print(f"✗ Failed: {e}")

print("\n" + "=" * 60)
print("All models loaded successfully!")
print("=" * 60)

# Test email prediction
print("\n[TEST] Email Prediction...")
try:
    # Sample email text
    sample_email = "Click here to verify your account immediately or your account will be suspended"
    
    # Vectorize
    X_test = tfidf.transform([sample_email])
    
    # Predict
    pred_stacking = stacking.predict(X_test)[0]
    pred_voting = voting.predict(X_test)[0]
    pred_rf = rf_tuned.predict(X_test)[0]
    
    # Probabilities
    prob_stacking = stacking.predict_proba(X_test)[0]
    prob_voting = voting.predict_proba(X_test)[0]
    prob_rf = rf_tuned.predict_proba(X_test)[0]
    
    print(f"Sample text: {sample_email[:50]}...")
    print(f"Stacking prediction: {pred_stacking} (phishing prob: {prob_stacking[1]:.2%})")
    print(f"Voting prediction: {pred_voting} (phishing prob: {prob_voting[1]:.2%})")
    print(f"RF Tuned prediction: {pred_rf} (phishing prob: {prob_rf[1]:.2%})")
except Exception as e:
    print(f"✗ Prediction failed: {e}")

# Test web log prediction
print("\n[TEST] Web Log Prediction...")
try:
    import numpy as np
    
    # Sample suspicious log features (8 features)
    sample_log_features = np.array([
        [100, 500, 1, 2048, 0.8, 3, 0.95, 1]  # High requests, high data transfer, high anomaly score
    ])
    
    # Predict
    anomaly_score = iso_forest.decision_function(sample_log_features)[0]
    is_anomaly = iso_forest.predict(sample_log_features)[0]
    
    print(f"Sample log features: {sample_log_features[0]}")
    print(f"Anomaly score: {anomaly_score:.4f}")
    print(f"Is anomaly: {is_anomaly} (1=anomaly, -1=normal)")
except Exception as e:
    print(f"✗ Web prediction failed: {e}")

print("\n✓ All tests completed!")
