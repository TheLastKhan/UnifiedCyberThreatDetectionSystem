#!/usr/bin/env python3
"""
Simplified Test API for Email Detection
Runs without Docker, uses local models
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
import time

# Import detectors
from src.email_detector.bert_detector import BertEmailDetector
from src.email_detector.fasttext_detector import FastTextEmailDetector
from src.email_detector.tfidf_detector import TFIDFEmailDetector

app = Flask(__name__)
CORS(app)

# Initialize detectors
print("Loading models...")
bert_detector = None
fasttext_detector = None
tfidf_detector = None

try:
    bert_detector = BertEmailDetector()
    print("✅ BERT loaded")
except Exception as e:
    print(f"❌ BERT failed: {e}")

try:
    fasttext_detector = FastTextEmailDetector()
    print("✅ FastText loaded")
except Exception as e:
    print(f"❌ FastText failed: {e}")

try:
    tfidf_detector = TFIDFEmailDetector()
    print("✅ TF-IDF loaded")
except Exception as e:
    print(f"❌ TF-IDF failed: {e}")

print("Models loaded!")


def get_risk_level(score):
    if score < 0.3:
        return "low"
    elif score < 0.6:
        return "medium"
    elif score < 0.85:
        return "high"
    return "critical"


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})


@app.route('/api/email/analyze/bert', methods=['POST'])
def analyze_bert():
    data = request.json
    email_content = data.get('email_content', '')
    
    if not email_content:
        return jsonify({"error": "email_content is required"}), 400
    
    start = time.time()
    result = bert_detector.predict(email_content)
    elapsed = (time.time() - start) * 1000
    
    return jsonify({
        "model": "BERT",
        "label": result.label,
        "prediction": result.label,
        "phishing_score": result.phishing_score,
        "score": result.phishing_score,
        "confidence": result.confidence,
        "risk_level": get_risk_level(result.phishing_score),
        "processing_time_ms": elapsed
    })


@app.route('/api/email/analyze/fasttext', methods=['POST'])
def analyze_fasttext():
    """FastText now returns average of BERT and TF-IDF for consistency"""
    data = request.json
    email_content = data.get('email_content', '')
    
    if not email_content:
        return jsonify({"error": "email_content is required"}), 400
    
    start = time.time()
    
    # Get BERT and TF-IDF results
    bert_result = bert_detector.predict(email_content)
    tfidf_result = tfidf_detector.predict(email_content)
    
    # Calculate average score
    avg_score = (bert_result.phishing_score + tfidf_result.score) / 2
    
    # Determine label based on average
    label = "phishing" if avg_score > 0.5 else "legitimate"
    
    elapsed = (time.time() - start) * 1000
    
    return jsonify({
        "model": "FastText (BERT+TF-IDF avg)",
        "label": label,
        "prediction": label,
        "phishing_score": avg_score,
        "score": avg_score,
        "confidence": max(avg_score, 1 - avg_score),
        "risk_level": get_risk_level(avg_score),
        "processing_time_ms": elapsed,
        "components": {
            "bert_score": bert_result.phishing_score,
            "tfidf_score": tfidf_result.score
        }
    })


@app.route('/api/email/analyze', methods=['POST'])
def analyze_tfidf():
    data = request.json
    email_content = data.get('email_content', '')
    
    if not email_content:
        return jsonify({"error": "email_content is required"}), 400
    
    start = time.time()
    result = tfidf_detector.predict(email_content)
    elapsed = (time.time() - start) * 1000
    
    return jsonify({
        "model": "TF-IDF",
        "label": result.label,
        "prediction": result.label,
        "phishing_score": result.score,
        "score": result.score,
        "confidence": result.confidence,
        "risk_level": get_risk_level(result.score),
        "processing_time_ms": elapsed,
        "model_confidence": {
            "prediction": result.label,
            "phishing_probability": result.score,
            "legitimate_probability": 1 - result.score,
            "confidence": result.confidence,
            "risk_level": get_risk_level(result.score),
            "model_type": "TF-IDF"
        }
    })


if __name__ == '__main__':
    print("\n🚀 Starting Test API on http://localhost:5001")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=False)
