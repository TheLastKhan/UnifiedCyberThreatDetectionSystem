"""
Test script for ML Model Monitoring System (AŞAMA 9)
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000/api/monitoring"


def print_header(title):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_monitoring_health():
    """Test monitoring system health check."""
    print_header("TEST 1: Monitoring Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("[OK] Monitoring System: Healthy")
        print(f"  - Tracked Models: {data['components']['metrics_tracker']['tracked_models']}")
        print(f"  - Active Drift Detectors: {data['components']['drift_detectors']['active_detectors']}")
        print(f"  - Active A/B Tests: {data['components']['ab_tests']['active_experiments']}")
        print(f"  - Active Retraining Pipelines: {data['components']['retraining_pipelines']['active_pipelines']}")
        return True
    else:
        print(f"[FAIL] {response.text}")
        return False


def test_log_prediction():
    """Test logging predictions."""
    print_header("TEST 2: Log Model Predictions")
    
    # Log some predictions
    predictions = [
        {
            "model_name": "email_detector",
            "input_data": {"subject": "Win a free iPhone!", "sender": "scam@test.com"},
            "prediction": "phishing",
            "confidence": 0.95,
            "prediction_time": 0.123,
            "ground_truth": "phishing"
        },
        {
            "model_name": "email_detector",
            "input_data": {"subject": "Meeting tomorrow", "sender": "boss@company.com"},
            "prediction": "legitimate",
            "confidence": 0.98,
            "prediction_time": 0.089,
            "ground_truth": "legitimate"
        },
        {
            "model_name": "web_analyzer",
            "input_data": {"path": "/admin/login", "status": 200},
            "prediction": "normal",
            "confidence": 0.92,
            "prediction_time": 0.056,
            "ground_truth": "normal"
        }
    ]
    
    success_count = 0
    for pred in predictions:
        response = requests.post(f"{BASE_URL}/metrics/log", json=pred)
        if response.status_code == 200:
            success_count += 1
            print(f"[OK] Logged: {pred['model_name']} - {pred['prediction']}")
    
    print(f"\n[STATS] {success_count}/{len(predictions)} predictions logged")
    return success_count == len(predictions)


def test_get_metrics():
    """Test getting model metrics."""
    print_header("TEST 3: Get Model Metrics")
    
    response = requests.get(f"{BASE_URL}/metrics/email_detector")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        metrics = data['metrics']['current']
        print("[OK] Email Detector Metrics:")
        print(f"  - Accuracy: {metrics.get('accuracy', 'N/A')}")
        print(f"  - Precision: {metrics.get('precision', 'N/A')}")
        print(f"  - Recall: {metrics.get('recall', 'N/A')}")
        print(f"  - F1 Score: {metrics.get('f1_score', 'N/A')}")
        print(f"  - Avg Prediction Time: {metrics.get('avg_prediction_time', 'N/A')}s")
        print(f"  - Total Predictions: {data['metrics'].get('total_predictions', 0)}")
        return True
    else:
        print(f"[FAIL] {response.text}")
        return False


def test_compare_models():
    """Test model comparison."""
    print_header("TEST 4: Compare Models")
    
    response = requests.get(f"{BASE_URL}/metrics/compare")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        comparison = data['comparison']
        
        print("[OK] Model Comparison:")
        if comparison['best_accuracy']['model']:
            print(f"  - Best Accuracy: {comparison['best_accuracy']['model']} "
                  f"({comparison['best_accuracy']['value']:.4f})")
        if comparison['best_f1']['model']:
            print(f"  - Best F1 Score: {comparison['best_f1']['model']} "
                  f"({comparison['best_f1']['value']:.4f})")
        if comparison['fastest']['model']:
            print(f"  - Fastest: {comparison['fastest']['model']} "
                  f"({comparison['fastest']['value']:.6f}s)")
        return True
    else:
        print(f"[FAIL] {response.text}")
        return False


def test_drift_detection():
    """Test drift detection."""
    print_header("TEST 5: Drift Detection")
    
    # Add some samples first
    print("Adding drift samples...")
    for i in range(35):
        response = requests.post(
            f"{BASE_URL}/drift/email_detector/sample",
            json={
                "features": {
                    "subject_length": 30 + i,
                    "url_count": 1 + (i % 3),
                    "suspicious_words": 2 + (i % 5)
                }
            }
        )
        if response.status_code != 200:
            print(f"[WARN] Sample {i+1} failed")
    
    print(f"[OK] Added 35 samples\n")
    
    # Get drift summary
    response = requests.get(f"{BASE_URL}/drift/email_detector/summary")
    print(f"Drift Summary Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        summary = data['drift_summary']
        print("[OK] Drift Detection Summary:")
        print(f"  - Total Checks: {summary.get('total_checks', 0)}")
        print(f"  - Drift Detected Count: {summary.get('drift_detected_count', 0)}")
        if summary.get('total_checks', 0) > 0:
            print(f"  - Drift Ratio: {summary.get('drift_ratio', 0):.4f}")
        return True
    else:
        print(f"[FAIL] {response.text}")
        return False


def test_retraining_status():
    """Test retraining pipeline status."""
    print_header("TEST 6: Retraining Pipeline")
    
    # Add training samples
    print("Adding training samples...")
    for i in range(15):
        response = requests.post(
            f"{BASE_URL}/retraining/email_detector/sample",
            json={
                "features": {
                    "subject": f"Sample email {i}",
                    "sender": f"user{i}@test.com"
                },
                "label": "phishing" if i % 2 == 0 else "legitimate",
                "metadata": {"test": True}
            }
        )
    
    print(f"[OK] Added 15 training samples\n")
    
    # Get status
    response = requests.get(f"{BASE_URL}/retraining/email_detector/status")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        buffer_stats = data['buffer_stats']
        
        print("[OK] Retraining Pipeline Status:")
        print(f"  - Buffer Size: {buffer_stats['size']}")
        print(f"  - Ready for Training: {buffer_stats['ready_for_training']}")
        print(f"  - Min Samples Needed: {buffer_stats['min_samples_needed']}")
        if 'label_distribution' in buffer_stats:
            print(f"  - Label Distribution: {buffer_stats['label_distribution']}")
        return True
    else:
        print(f"[FAIL] {response.text}")
        return False


def test_retraining_check():
    """Test retraining decision."""
    print_header("TEST 7: Retraining Decision Check")
    
    response = requests.post(
        f"{BASE_URL}/retraining/email_detector/check",
        json={
            "current_accuracy": 0.85,
            "drift_score": 0.15
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        decision = data['decision']
        
        print("[OK] Retraining Decision:")
        print(f"  - Should Retrain: {decision['should_retrain']}")
        print(f"  - Current Accuracy: {decision['current_accuracy']}")
        print(f"  - Drift Score: {decision['drift_score']}")
        print(f"  - Buffer Size: {decision['buffer_size']}")
        if decision['reasons']:
            print(f"  - Reasons:")
            for reason in decision['reasons']:
                print(f"    * {reason}")
        return True
    else:
        print(f"[FAIL] {response.text}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print(" "*15 + "ML MONITORING TEST SUITE")
    print(" "*20 + "AŞAMA 9")
    print("="*60)
    
    tests = [
        ("Monitoring Health", test_monitoring_health),
        ("Log Predictions", test_log_prediction),
        ("Get Metrics", test_get_metrics),
        ("Compare Models", test_compare_models),
        ("Drift Detection", test_drift_detection),
        ("Retraining Status", test_retraining_status),
        ("Retraining Check", test_retraining_check)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            time.sleep(0.5)
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            results.append((name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\n[STATS] {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! ✅")
    else:
        print(f"\n[WARNING] {total-passed} test(s) failed")


if __name__ == "__main__":
    main()
