"""
REST API endpoints for Unified Threat Detection System
Integrates trained models: Stacking Ensemble (email), Isolation Forest (web)
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import json
import sys
import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.email_detector.detector import EmailDetector
from src.web_analyzer.analyzer import WebAnalyzer

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Model cache
_email_detector = None
_web_analyzer = None
_stacking_model = None
_voting_model = None
_tfidf_vectorizer = None
_web_anomaly_detector = None
_web_scaler = None

def get_email_detector():
    """Get or load email detector"""
    global _email_detector
    if _email_detector is None:
        _email_detector = EmailDetector()
    return _email_detector

def get_web_analyzer():
    """Get or load web analyzer"""
    global _web_analyzer
    if _web_analyzer is None:
        _web_analyzer = WebAnalyzer()
    return _web_analyzer

def load_trained_models():
    """Load trained ML models from disk"""
    global _stacking_model, _voting_model, _tfidf_vectorizer, _web_anomaly_detector, _web_scaler
    
    models_dir = Path(__file__).parent.parent / 'models'
    
    try:
        # Load email detection models
        _tfidf_vectorizer = joblib.load(models_dir / 'tfidf_vectorizer.pkl')
        _stacking_model = joblib.load(models_dir / 'email_detector_stacking.pkl')
        _voting_model = joblib.load(models_dir / 'email_detector_voting.pkl')
        
        # Load web anomaly models
        _web_anomaly_detector = joblib.load(models_dir / 'web_anomaly_detector.pkl')
        _web_scaler = joblib.load(models_dir / 'log_scaler.pkl')
        
        print("✅ All trained models loaded successfully")
        return True
    except FileNotFoundError as e:
        print(f"⚠️ Some models not found: {e}")
        print("   Using fallback to basic detectors")
        return False

@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200

@api_bp.route('/email/analyze', methods=['POST'])
def analyze_email():
    """
    Analyze email for phishing/spam using trained Stacking Ensemble
    
    Expected JSON:
    {
        "subject": "Email subject",
        "body": "Email body text",
        "sender": "sender@example.com"
    }
    """
    try:
        data = request.json
        
        if not data or 'body' not in data:
            return jsonify({'error': 'Missing required field: body'}), 400
        
        subject = data.get('subject', '')
        body = data.get('body', '')
        sender = data.get('sender', '')
        
        detector = get_email_detector()
        
        # Analyze with detector
        result = detector.analyze(
            subject=subject,
            body=body,
            sender=sender
        )
        
        # Try to use trained model if available
        if _stacking_model is not None and _tfidf_vectorizer is not None:
            # Combine subject and body for vectorization
            text = f"{subject} {body}".lower()
            
            # Vectorize with TF-IDF
            X = _tfidf_vectorizer.transform([text])
            
            # Get predictions from both models
            stacking_pred = _stacking_model.predict_proba(X)[0]
            voting_pred = _voting_model.predict_proba(X)[0]
            
            # Average predictions
            phishing_prob = (stacking_pred[1] + voting_pred[1]) / 2
            
            result['model_confidence'] = {
                'phishing_probability': float(phishing_prob),
                'legitimate_probability': float(1 - phishing_prob),
                'model_type': 'ensemble (stacking + voting)',
                'threshold': 0.5,
                'prediction': 'phishing' if phishing_prob > 0.5 else 'legitimate'
            }
        
        # Add features
        result['features'] = detector.extract_features(subject, body)
        result['timestamp'] = datetime.now().isoformat()
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Email analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/email/batch', methods=['POST'])
def analyze_emails_batch():
    """
    Batch analyze multiple emails
    
    Expected JSON:
    {
        "emails": [
            {"subject": "...", "body": "..."},
            ...
        ]
    }
    """
    try:
        data = request.json
        emails = data.get('emails', [])
        
        if not emails:
            return jsonify({'error': 'No emails provided'}), 400
        
        results = []
        for email in emails[:100]:  # Limit to 100 emails
            result = request.json = email
            response = analyze_email()
            if response[1] == 200:
                results.append(response[0].json)
        
        return jsonify({
            'count': len(results),
            'results': results,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Batch email analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/web/analyze', methods=['POST'])
def analyze_web_log():
    """
    Analyze web log entry for anomalies using trained Isolation Forest
    
    Expected JSON:
    {
        "ip": "192.168.1.100",
        "method": "POST",
        "path": "/admin/login",
        "status": "401",
        "user_agent": "Mozilla/5.0",
        "timestamp": "20/Sep/2025:14:00:00 +0200"
    }
    """
    try:
        data = request.json
        
        if not data or 'path' not in data:
            return jsonify({'error': 'Missing required field: path'}), 400
        
        analyzer = get_web_analyzer()
        
        # Analyze with analyzer
        result = analyzer.analyze(data)
        
        # Try to use trained model if available
        if _web_anomaly_detector is not None and _web_scaler is not None:
            # Extract features
            features = analyzer.extract_features(data)
            features_array = np.array([features])
            
            # Scale features
            features_scaled = _web_scaler.transform(features_array)
            
            # Predict anomaly
            anomaly_score = _web_anomaly_detector.decision_function(features_scaled)[0]
            is_anomaly = _web_anomaly_detector.predict(features_scaled)[0]
            
            result['model_analysis'] = {
                'is_anomalous': bool(is_anomaly == -1),
                'anomaly_score': float(anomaly_score),
                'model_type': 'isolation_forest',
                'features_used': 8,
                'contamination': 0.1
            }
        
        result['timestamp'] = datetime.now().isoformat()
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Web analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/web/batch', methods=['POST'])
def analyze_web_logs_batch():
    """
    Batch analyze multiple web logs
    
    Expected JSON:
    {
        "logs": [
            {"ip": "...", "method": "...", "path": "..."},
            ...
        ]
    }
    """
    try:
        data = request.json
        logs = data.get('logs', [])
        
        if not logs:
            return jsonify({'error': 'No logs provided'}), 400
        
        results = []
        anomaly_count = 0
        
        for log in logs[:500]:  # Limit to 500 logs
            # Analyze each log
            request.json = log
            response = analyze_web_log()
            
            if response[1] == 200:
                result_data = response[0].json
                results.append(result_data)
                
                if result_data.get('is_anomalous'):
                    anomaly_count += 1
        
        return jsonify({
            'total_logs': len(results),
            'anomalous_count': anomaly_count,
            'anomaly_rate': round(anomaly_count / len(results) * 100, 2) if results else 0,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Batch web analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/unified/analyze', methods=['POST'])
def analyze_unified():
    """
    Unified analysis combining email and web threat detection
    
    Expected JSON:
    {
        "type": "email|web",
        "email": {...},  // if type='email'
        "log": {...}     // if type='web'
    }
    """
    try:
        data = request.json
        threat_type = data.get('type', 'unknown')
        
        if threat_type == 'email':
            request.json = data.get('email', {})
            response = analyze_email()
        elif threat_type == 'web':
            request.json = data.get('log', {})
            response = analyze_web_log()
        else:
            return jsonify({'error': 'Invalid threat type'}), 400
        
        return response
        
    except Exception as e:
        print(f"❌ Unified analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/models/status', methods=['GET'])
def models_status():
    """Get status of loaded ML models"""
    return jsonify({
        'stacking_model': _stacking_model is not None,
        'voting_model': _voting_model is not None,
        'tfidf_vectorizer': _tfidf_vectorizer is not None,
        'web_anomaly_detector': _web_anomaly_detector is not None,
        'web_scaler': _web_scaler is not None,
        'timestamp': datetime.now().isoformat()
    }), 200

@api_bp.route('/models/reload', methods=['POST'])
def reload_models():
    """Reload trained models from disk"""
    success = load_trained_models()
    return jsonify({
        'success': success,
        'timestamp': datetime.now().isoformat()
    }), 200 if success else 500

@api_bp.route('/report/summary', methods=['POST'])
def generate_summary():
    """
    Generate threat summary report
    
    Expected JSON:
    {
        "emails": [...],
        "logs": [...]
    }
    """
    try:
        data = request.json
        emails = data.get('emails', [])
        logs = data.get('logs', [])
        
        email_phishing_count = 0
        log_anomaly_count = 0
        
        # Analyze emails
        for email in emails:
            result = analyze_email.__wrapped__(email)
            if result.get('is_phishing'):
                email_phishing_count += 1
        
        # Analyze logs
        for log in logs:
            result = analyze_web_log.__wrapped__(log)
            if result.get('is_anomalous'):
                log_anomaly_count += 1
        
        return jsonify({
            'email_stats': {
                'total': len(emails),
                'phishing': email_phishing_count,
                'legitimate': len(emails) - email_phishing_count,
                'phishing_rate': round(email_phishing_count / len(emails) * 100, 2) if emails else 0
            },
            'web_stats': {
                'total': len(logs),
                'anomalous': log_anomaly_count,
                'normal': len(logs) - log_anomaly_count,
                'anomaly_rate': round(log_anomaly_count / len(logs) * 100, 2) if logs else 0
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Report generation error: {e}")
        return jsonify({'error': str(e)}), 500

# Initialize models when blueprint is created
load_trained_models()
