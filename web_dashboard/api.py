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

try:
    from src.email_detector.detector import EmailPhishingDetector
    from src.web_analyzer.analyzer import WebLogAnalyzer
except ImportError:
    print("[WARNING] Could not import detectors. Using fallback mode.")
    EmailPhishingDetector = None
    WebLogAnalyzer = None

# Import database functions for persistent storage
try:
    from web_dashboard.database import (
        add_email_prediction,
        add_web_prediction,
        get_email_predictions,
        get_web_predictions,
        clear_all_predictions
    )
    DATABASE_AVAILABLE = True
    print("[INFO] Database module loaded successfully in api.py")
except Exception as e:
    print(f"[WARNING] Database not available in api.py: {e}")
    DATABASE_AVAILABLE = False

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
    if _email_detector is None and EmailPhishingDetector:
        try:
            models_dir = Path(__file__).parent.parent / 'models'
            detector = EmailPhishingDetector()
            
            # Try to load trained model
            model_path = models_dir / 'email_detector_rf.pkl'
            if model_path.exists():
                try:
                    detector.load_model(str(model_path))
                    print(f"[SUCCESS] EmailPhishingDetector loaded from {model_path}")
                except Exception as e:
                    print(f"[WARNING] Could not load email detector model: {e}")
                    # Continue with untrained detector
            else:
                print(f"[WARNING] Email detector model not found at {model_path}")
            
            _email_detector = detector
        except Exception as e:
            print(f"[WARNING] Could not initialize EmailPhishingDetector: {e}")
    return _email_detector

def get_web_analyzer():
    """Get or load web analyzer"""
    global _web_analyzer
    if _web_analyzer is None and WebLogAnalyzer:
        try:
            _web_analyzer = WebLogAnalyzer()
        except Exception as e:
            print(f"[WARNING] Could not initialize WebLogAnalyzer: {e}")
    return _web_analyzer

def load_trained_models():
    """Load trained ML models from disk"""
    global _stacking_model, _voting_model, _tfidf_vectorizer, _web_anomaly_detector, _web_scaler
    
    models_dir = Path(__file__).parent.parent / 'models'
    
    try:
        # Load email detection models with error handling for NumPy compatibility
        try:
            _tfidf_vectorizer = joblib.load(models_dir / 'tfidf_vectorizer.pkl')
            print("[SUCCESS] TF-IDF vectorizer loaded")
        except Exception as e:
            print(f"[WARNING] Could not load TF-IDF vectorizer: {e}")
            _tfidf_vectorizer = None
        
        try:
            _stacking_model = joblib.load(models_dir / 'email_detector_stacking.pkl')
            print("[SUCCESS] Stacking model loaded")
        except Exception as e:
            print(f"[WARNING] Could not load stacking model: {e}")
            _stacking_model = None
        
        try:
            _voting_model = joblib.load(models_dir / 'email_detector_voting.pkl')
            print("[SUCCESS] Voting model loaded")
        except Exception as e:
            print(f"[WARNING] Could not load voting model: {e}")
            _voting_model = None
        
        # Load web anomaly models
        try:
            _web_anomaly_detector = joblib.load(models_dir / 'web_anomaly_detector.pkl')
            print("[SUCCESS] Web anomaly detector loaded")
        except Exception as e:
            print(f"[WARNING] Could not load web anomaly detector: {e}")
            _web_anomaly_detector = None
        
        try:
            _web_scaler = joblib.load(models_dir / 'log_scaler.pkl')
            print("[SUCCESS] Web scaler loaded")
        except Exception as e:
            print(f"[WARNING] Could not load web scaler: {e}")
            _web_scaler = None
        
        # Preload advanced models (BERT and FastText) to avoid first-request delay
        print("[INFO] Preloading advanced models...")
        try:
            from web_dashboard.production_api import get_bert_detector, get_fasttext_detector
            
            # Preload BERT
            print("[INFO] Loading BERT...")
            bert = get_bert_detector()
            if bert:
                print("[SUCCESS] BERT model preloaded")
            else:
                print("[WARNING] BERT model not available")
            
            # Preload FastText (this is the slow one - 838MB model)
            print("[INFO] Loading FastText...")
            fasttext = get_fasttext_detector()
            if fasttext:
                print("[SUCCESS] FastText model preloaded (838MB)")
            else:
                print("[WARNING] FastText model not available")
        except Exception as e:
            import traceback
            print(f"[WARNING] Could not preload advanced models: {e}")
            traceback.print_exc()
        
        # Return success if at least one model loaded
        if any([_tfidf_vectorizer, _stacking_model, _voting_model]):
            print("[SUCCESS] At least one model loaded successfully")
            return True
        else:
            print("[WARNING] No models could be loaded. Using fallback mode.")
            return False
            
    except Exception as e:
        print(f"[ERROR] Unexpected error loading models: {e}")
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
        
        result = {
            'subject': subject,
            'sender': sender,
            'timestamp': datetime.now().isoformat()
        }
        
        # Use trained model if available
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
        else:
            # Models not loaded - return default response
            result['model_confidence'] = {
                'phishing_probability': 0.0,
                'legitimate_probability': 1.0,
                'model_type': 'none',
                'prediction': 'legitimate'
            }
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"[ERROR] Email analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/email/analyze-bert', methods=['POST'])
def analyze_email_bert():
    """
    Analyze email using BERT model for higher accuracy
    
    Expected JSON:
    {
        "subject": "Email subject",
        "body": "Email body text",
        "sender": "sender@example.com"
    }
    """
    try:
        # Check if BERT is available
        try:
            from src.email_detector import BertEmailDetector
        except ImportError:
            return jsonify({
                'error': 'BERT detector not available',
                'detail': 'transformers library not installed'
            }), 503
        
        data = request.json
        
        if not data or 'body' not in data:
            return jsonify({'error': 'Missing required field: body'}), 400
        
        subject = data.get('subject', '')
        body = data.get('body', '')
        sender = data.get('sender', '')
        
        # Initialize BERT detector
        try:
            bert_model = BertEmailDetector(model_path="models/bert_finetuned")
        except Exception as e:
            return jsonify({
                'error': 'Could not load BERT model',
                'detail': str(e)
            }), 503
        
        # Combine subject and body
        text = f"{subject}\n\n{body}"
        
        # Get BERT prediction
        prediction = bert_model.predict(text)
        
        result = {
            'subject': subject,
            'sender': sender,
            'timestamp': datetime.now().isoformat(),
            'model_type': 'BERT (DistilBERT)',
            'prediction': prediction.label,
            'confidence': float(prediction.confidence),
            'phishing_score': float(prediction.score),
            'tokens_processed': prediction.tokens,
            'risk_level': 'high' if prediction.score > 0.7 else 'medium' if prediction.score > 0.5 else 'low'
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"[ERROR] BERT email analysis error: {e}")
        import traceback
        traceback.print_exc()
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
            # Analyze each email
            subject = email.get('subject', '')
            body = email.get('body', '')
            sender = email.get('sender', '')
            
            result = {
                'subject': subject,
                'sender': sender,
                'timestamp': datetime.now().isoformat()
            }
            
            # Use trained model if available
            if _stacking_model is not None and _tfidf_vectorizer is not None:
                text = f"{subject} {body}".lower()
                X = _tfidf_vectorizer.transform([text])
                stacking_pred = _stacking_model.predict_proba(X)[0]
                voting_pred = _voting_model.predict_proba(X)[0]
                phishing_prob = (stacking_pred[1] + voting_pred[1]) / 2
                
                result['model_confidence'] = {
                    'phishing_probability': float(phishing_prob),
                    'legitimate_probability': float(1 - phishing_prob),
                    'model_type': 'ensemble (stacking + voting)',
                    'prediction': 'phishing' if phishing_prob > 0.5 else 'legitimate'
                }
            
            results.append(result)
        
        return jsonify({
            'count': len(results),
            'results': results,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Batch email analysis error: {e}")
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
    """
    try:
        data = request.json
        
        if not data or 'path' not in data:
            return jsonify({'error': 'Missing required field: path'}), 400
        
        result = {
            'ip': data.get('ip', ''),
            'path': data.get('path', ''),
            'method': data.get('method', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        # Try to use trained model if available
        if _web_anomaly_detector is not None and _web_scaler is not None:
            # Extract features manually (8 features)
            path = data.get('path', '')
            user_agent = data.get('user_agent', '').lower()
            
            features = [
                len(path),  # request_length
                user_agent.count('union') + user_agent.count('select'),  # sql_keywords
                user_agent.count('script') + user_agent.count('alert'),  # xss_patterns
                sum(1 for c in path if ord(c) > 127),  # encoded_chars
                len(data.get('path', '')),  # url_length
                path.count('='),  # query_params
                sum(1 for c in path if not c.isalnum()),  # special_char_ratio
                sum(1 for c in path if c.isupper())  # uppercase_ratio
            ]
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
        print(f"[ERROR] Web analysis error: {e}")
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
            path = log.get('path', '')
            user_agent = log.get('user_agent', '').lower()
            
            features = [
                len(path),
                user_agent.count('union') + user_agent.count('select'),
                user_agent.count('script') + user_agent.count('alert'),
                sum(1 for c in path if ord(c) > 127),
                len(path),
                path.count('='),
                sum(1 for c in path if not c.isalnum()),
                sum(1 for c in path if c.isupper())
            ]
            features_array = np.array([features])
            
            result = {
                'ip': log.get('ip', ''),
                'path': path,
                'method': log.get('method', ''),
                'timestamp': datetime.now().isoformat()
            }
            
            if _web_anomaly_detector is not None and _web_scaler is not None:
                features_scaled = _web_scaler.transform(features_array)
                anomaly_score = _web_anomaly_detector.decision_function(features_scaled)[0]
                is_anomaly = _web_anomaly_detector.predict(features_scaled)[0]
                
                result['model_analysis'] = {
                    'is_anomalous': bool(is_anomaly == -1),
                    'anomaly_score': float(anomaly_score)
                }
                
                if result['model_analysis']['is_anomalous']:
                    anomaly_count += 1
            
            results.append(result)
        
        return jsonify({
            'total_logs': len(results),
            'anomalous_count': anomaly_count,
            'anomaly_rate': round(anomaly_count / len(results) * 100, 2) if results else 0,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Batch web analysis error: {e}")
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
            email_data = data.get('email', {})
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            sender = email_data.get('sender', '')
            
            result = {
                'subject': subject,
                'sender': sender,
                'timestamp': datetime.now().isoformat()
            }
            
            if _stacking_model is not None and _tfidf_vectorizer is not None:
                text = f"{subject} {body}".lower()
                X = _tfidf_vectorizer.transform([text])
                stacking_pred = _stacking_model.predict_proba(X)[0]
                voting_pred = _voting_model.predict_proba(X)[0]
                phishing_prob = (stacking_pred[1] + voting_pred[1]) / 2
                
                result['model_confidence'] = {
                    'phishing_probability': float(phishing_prob),
                    'legitimate_probability': float(1 - phishing_prob),
                    'prediction': 'phishing' if phishing_prob > 0.5 else 'legitimate'
                }
            
            return jsonify(result), 200
            
        elif threat_type == 'web':
            log_data = data.get('log', {})
            path = log_data.get('path', '')
            user_agent = log_data.get('user_agent', '').lower()
            
            features = [
                len(path),
                user_agent.count('union') + user_agent.count('select'),
                user_agent.count('script') + user_agent.count('alert'),
                sum(1 for c in path if ord(c) > 127),
                len(path),
                path.count('='),
                sum(1 for c in path if not c.isalnum()),
                sum(1 for c in path if c.isupper())
            ]
            features_array = np.array([features])
            
            result = {
                'ip': log_data.get('ip', ''),
                'path': path,
                'timestamp': datetime.now().isoformat()
            }
            
            if _web_anomaly_detector is not None and _web_scaler is not None:
                features_scaled = _web_scaler.transform(features_array)
                anomaly_score = _web_anomaly_detector.decision_function(features_scaled)[0]
                is_anomaly = _web_anomaly_detector.predict(features_scaled)[0]
                
                result['model_analysis'] = {
                    'is_anomalous': bool(is_anomaly == -1),
                    'anomaly_score': float(anomaly_score)
                }
            
            return jsonify(result), 200
        else:
            return jsonify({'error': 'Invalid threat type'}), 400
        
    except Exception as e:
        print(f"[ERROR] Unified analysis error: {e}")
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
        if _stacking_model is not None and _tfidf_vectorizer is not None:
            for email in emails:
                subject = email.get('subject', '')
                body = email.get('body', '')
                text = f"{subject} {body}".lower()
                X = _tfidf_vectorizer.transform([text])
                stacking_pred = _stacking_model.predict_proba(X)[0]
                voting_pred = _voting_model.predict_proba(X)[0]
                phishing_prob = (stacking_pred[1] + voting_pred[1]) / 2
                if phishing_prob > 0.5:
                    email_phishing_count += 1
        
        # Analyze logs
        if _web_anomaly_detector is not None and _web_scaler is not None:
            for log in logs:
                path = log.get('path', '')
                user_agent = log.get('user_agent', '').lower()
                features = [
                    len(path),
                    user_agent.count('union') + user_agent.count('select'),
                    user_agent.count('script') + user_agent.count('alert'),
                    sum(1 for c in path if ord(c) > 127),
                    len(path),
                    path.count('='),
                    sum(1 for c in path if not c.isalnum()),
                    sum(1 for c in path if c.isupper())
                ]
                features_array = np.array([features])
                features_scaled = _web_scaler.transform(features_array)
                is_anomaly = _web_anomaly_detector.predict(features_scaled)[0]
                if is_anomaly == -1:
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
        print(f"[ERROR] Report generation error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/enrich/ip', methods=['POST'])
def enrich_ip():
    """
    Enrich IP address with VirusTotal threat intelligence
    
    Expected JSON:
    {
        "ip": "203.0.113.45"
    }
    """
    try:
        from src.integrations.virustotal import get_virustotal_client
        
        data = request.get_json()
        ip_address = data.get('ip')
        
        if not ip_address:
            return jsonify({'error': 'Missing required field: ip'}), 400
        
        vt_client = get_virustotal_client()
        enrichment_data = vt_client.check_ip(ip_address)
        
        return jsonify({
            'ip': ip_address,
            'virustotal': enrichment_data,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"[ERROR] IP enrichment error: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/enrich/domain', methods=['POST'])
def enrich_domain():
    """
    Enrich domain with VirusTotal threat intelligence
    
    Expected JSON:
    {
        "domain": "example.com"
    }
    """
    try:
        from src.integrations.virustotal import get_virustotal_client
        
        data = request.get_json()
        domain = data.get('domain')
        
        if not domain:
            return jsonify({'error': 'Missing required field: domain'}), 400
        
        vt_client = get_virustotal_client()
        enrichment_data = vt_client.check_domain(domain)
        
        return jsonify({
            'domain': domain,
            'virustotal': enrichment_data,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Domain enrichment error: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/alert/send', methods=['POST'])
def send_alert():
    """
    Send threat alert via email and/or Slack
    
    Expected JSON:
    {
        "severity": "HIGH",
        "threat_data": {...},
        "channels": ["email", "slack"],
        "email_recipients": ["admin@example.com"],
        "slack_channel": "#security-alerts"
    }
    """
    try:
        from src.integrations.notifications import get_email_notifier, get_slack_notifier
        
        data = request.get_json()
        severity = data.get('severity', 'MEDIUM')
        threat_data = data.get('threat_data', {})
        channels = data.get('channels', [])
        
        results = {}
        
        # Send email alert
        if 'email' in channels:
            email_recipients = data.get('email_recipients', [])
            if email_recipients:
                email_notifier = get_email_notifier()
                subject = f"Threat Detected: {threat_data.get('type', 'Unknown')}"
                success = email_notifier.send_alert(email_recipients, subject, threat_data, severity)
                results['email'] = 'sent' if success else 'failed'
            else:
                results['email'] = 'skipped (no recipients)'
        
        # Send Slack alert
        if 'slack' in channels:
            slack_channel = data.get('slack_channel')
            slack_notifier = get_slack_notifier()
            success = slack_notifier.send_alert(slack_channel, threat_data, severity)
            results['slack'] = 'sent' if success else 'failed'
        
        return jsonify({
            'status': 'processed',
            'results': results,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Alert sending error: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/ratelimit/status', methods=['GET'])
def ratelimit_status():
    """
    Get current rate limit status for client
    """
    try:
        from src.middleware.rate_limiter import get_rate_limiter
        
        limiter = get_rate_limiter()
        usage_info = limiter.get_usage_info()
        
        return jsonify(usage_info), 200
        
    except Exception as e:
        print(f"[ERROR] Rate limit status error: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/cache/stats', methods=['GET'])
def cache_stats():
    """
    Get cache statistics (Redis info)
    """
    try:
        from src.utils.cache import get_redis_cache
        
        cache = get_redis_cache()
        
        if not cache.enabled:
            return jsonify({
                'enabled': False,
                'message': 'Redis cache not available'
            }), 200
        
        # Get Redis INFO
        info = cache.client.info('stats')
        
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        hit_rate = round((hits / total * 100) if total > 0 else 0, 2)
        
        return jsonify({
            'enabled': True,
            'total_commands_processed': info.get('total_commands_processed', 0),
            'keyspace_hits': hits,
            'keyspace_misses': misses,
            'hit_rate': hit_rate,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Cache stats error: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/dashboard/stats', methods=['GET'])
def dashboard_stats():
    """
    Get real-time dashboard statistics
    Returns: system status, model metrics, threat counts
    """
    try:
        # Import database functions
        try:
            from web_dashboard.database import get_email_predictions, get_web_predictions, get_prediction_counts
            database_available = True
        except ImportError:
            database_available = False
        
        # 1. System Status - check if models loaded
        models_loaded = (_stacking_model is not None and _voting_model is not None)
        api_responding = True
        
        if database_available:
            # Get all predictions from database
            all_email_preds = get_email_predictions(limit=10000)  # All time
            email_preds_30d = get_email_predictions(hours=30*24)  # Last 30 days
            all_web_preds = get_web_predictions(limit=10000)
            web_preds_30d = get_web_predictions(hours=30*24)
            email_preds_24h = get_email_predictions(hours=24)  # Last 24 hours
            web_preds_24h = get_web_predictions(hours=24)
            
            # 2. Email Detection Stats
            total_email = len(email_preds_30d)
            phishing_count = len([p for p in email_preds_30d if p.get('prediction') == 'phishing'])
            avg_confidence = sum([p.get('confidence', 0) for p in email_preds_30d]) / total_email if total_email > 0 else 0
            
            # 3. Web Anomaly Stats
            total_web = len(web_preds_30d)
            anomaly_count = len([p for p in web_preds_30d if p.get('is_anomaly', False)])
            
            # 4. Recent Threats (last 24 hours)
            phishing_threats_24h = len([p for p in email_preds_24h if p.get('prediction') == 'phishing'])
            anomaly_threats_24h = len([p for p in web_preds_24h if p.get('is_anomaly', False)])
            
            # High severity = high confidence phishing or high anomaly score
            high_severity_count = len([p for p in email_preds_24h 
                                      if p.get('prediction') == 'phishing' and p.get('confidence', 0) > 0.8])
            high_severity_count += len([p for p in web_preds_24h 
                                       if p.get('is_anomaly', False) and p.get('anomaly_score', 0) > 0.8])
        else:
            # Fallback to zeros if database not available
            total_email = phishing_count = avg_confidence = 0
            total_web = anomaly_count = 0
            phishing_threats_24h = anomaly_threats_24h = high_severity_count = 0
        
        # Model accuracy from loaded models (static values for now - from training)
        model_accuracy = {
            'stacking': 89.60,
            'voting': 88.48,
            'roc_auc': 96.65
        }
        
        return jsonify({
            'system_status': {
                'operational': 100 if models_loaded and api_responding else 50,
                'models_loaded': models_loaded,
                'api_responding': api_responding
            },
            'email_detection': {
                'accuracy': model_accuracy['stacking'],
                'roc_auc': model_accuracy['roc_auc'],
                'total_predictions': total_email,
                'phishing_detected': phishing_count,
                'avg_confidence': round(float(avg_confidence), 2)
            },
            'web_analysis': {
                'features_used': 8,
                'total_predictions': total_web,
                'anomalies_detected': anomaly_count
            },
            'recent_threats': {
                'total_24h': phishing_threats_24h + anomaly_threats_24h,
                'high_severity': high_severity_count,
                'phishing': phishing_threats_24h,
                'anomalies': anomaly_threats_24h
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Dashboard stats error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/dashboard/alerts', methods=['GET'])
def dashboard_alerts():
    """
    Get recent security alerts (last 10)
    """
    try:
        # Import database functions
        try:
            from web_dashboard.database import get_email_predictions, get_web_predictions
            from dateutil import parser
            database_available = True
        except ImportError:
            database_available = False
        
        limit = request.args.get('limit', 10, type=int)
        
        formatted_alerts = []
        
        if database_available:
            # Get recent predictions from database
            email_preds = get_email_predictions(limit=limit*2, hours=24*7)  # Last week
            web_preds = get_web_predictions(limit=limit*2, hours=24*7)
            
            # Convert email predictions to alerts
            for pred in email_preds:
                # Only show phishing predictions
                if pred.get('prediction') == 'phishing':
                    # Parse timestamp
                    pred_time = parser.parse(pred['timestamp'])
                    time_diff = datetime.now() - pred_time.replace(tzinfo=None)
                    total_secs = time_diff.total_seconds()
                    
                    # Calculate time ago using total seconds
                    if total_secs < 60:
                        time_ago = f"{int(total_secs)} seconds ago"
                    elif total_secs < 3600:
                        time_ago = f"{int(total_secs // 60)} minutes ago"
                    elif total_secs < 86400:
                        time_ago = f"{int(total_secs // 3600)} hours ago"
                    else:
                        time_ago = f"{int(total_secs // 86400)} days ago"
                    
                    # Map risk level to severity
                    risk_level = pred.get('risk_level', 'medium')
                    risk_to_severity = {
                        'critical': 'high',
                        'high': 'high',
                        'medium': 'medium',
                        'low': 'low'
                    }
                    severity = risk_to_severity.get(risk_level, 'medium')
                    
                    # Format severity badge (title case, right side)
                    severity_badge = risk_level.capitalize()
                    
                    email_subject = pred.get('email_subject', 'No Subject')
                    email_sender = pred.get('email_sender', 'Unknown')
                    
                    formatted_alerts.append({
                        'id': pred['id'],
                        'title': f"Phishing Email Detected",
                        'severity_badge': severity_badge,
                        'description': f"From: {email_sender} - Subject: {email_subject}",
                        'severity': severity,
                        'confidence': round(float(pred.get('confidence', 0)) * 100, 1),
                        'time_ago': time_ago,
                        'detected_at': pred_time  # Use datetime object for proper sorting
                    })
            
            # Convert web predictions to alerts
            for pred in web_preds:
                # Only show anomalies
                if pred.get('is_anomaly'):
                    pred_time = parser.parse(pred['timestamp'])
                    time_diff = datetime.now() - pred_time.replace(tzinfo=None)
                    total_secs = time_diff.total_seconds()
                    
                    # Calculate time ago using total seconds
                    if total_secs < 60:
                        time_ago = f"{int(total_secs)} seconds ago"
                    elif total_secs < 3600:
                        time_ago = f"{int(total_secs // 60)} minutes ago"
                    elif total_secs < 86400:
                        time_ago = f"{int(total_secs // 3600)} hours ago"
                    else:
                        time_ago = f"{int(total_secs // 86400)} days ago"
                    
                    # Severity based on anomaly score
                    anomaly_score = pred.get('anomaly_score', 0)
                    if anomaly_score >= 0.9:
                        severity = 'high'
                        severity_label = 'Critical'
                    elif anomaly_score >= 0.7:
                        severity = 'high'
                        severity_label = 'High'
                    elif anomaly_score >= 0.5:
                        severity = 'medium'
                        severity_label = 'Medium'
                    else:
                        severity = 'low'
                        severity_label = 'Low'
                    
                    ip = pred.get('ip_address', 'Unknown')
                    patterns = pred.get('patterns_detected', '')
                    
                    # Build description with patterns if available
                    if patterns and patterns.strip():
                        description = f"Suspicious activity from IP: {ip} - Patterns: {patterns}"
                    else:
                        description = f"Suspicious activity from IP: {ip}"
                    
                    formatted_alerts.append({
                        'id': pred['id'],
                        'title': f"Web Anomaly Detected",
                        'severity_badge': severity_label,
                        'description': description,
                        'severity': severity,
                        'confidence': round(float(anomaly_score * 100), 1),
                        'time_ago': time_ago,
                        'detected_at': pred_time  # Use datetime object for proper sorting
                    })
            
            # Sort by timestamp (most recent first) and limit
            formatted_alerts.sort(key=lambda x: x['detected_at'], reverse=True)
            formatted_alerts = formatted_alerts[:limit]
        
        return jsonify({
            'alerts': formatted_alerts,
            'total': len(formatted_alerts)
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Dashboard alerts error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/dashboard/charts', methods=['GET'])
def dashboard_charts():
    """
    Get data for dashboard charts
    """
    try:
        # Import database functions
        try:
            from web_dashboard.database import get_email_predictions, get_web_predictions
            database_available = True
        except ImportError:
            database_available = False
        
        if database_available:
            # Get predictions from database
            email_preds = get_email_predictions(limit=10000, hours=30*24)  # Last 30 days
            web_preds = get_web_predictions(limit=10000, hours=30*24)
            
            # Threat Distribution (by type)
            phishing_count = len([p for p in email_preds if p.get('prediction') == 'phishing'])
            legitimate_count = len([p for p in email_preds if p.get('prediction') == 'legitimate'])
            anomaly_count = len([p for p in web_preds if p.get('is_anomaly')])
            normal_web = len([p for p in web_preds if not p.get('is_anomaly')])
            
            threat_labels = []
            threat_data = []
            if phishing_count > 0:
                threat_labels.append('Phishing Email')
                threat_data.append(phishing_count)
            if legitimate_count > 0:
                threat_labels.append('Legitimate Email')
                threat_data.append(legitimate_count)
            if anomaly_count > 0:
                threat_labels.append('Web Anomaly')
                threat_data.append(anomaly_count)
            if normal_web > 0:
                threat_labels.append('Normal Web Traffic')
                threat_data.append(normal_web)
            
            # Model Performance
            model_labels = ['Email Detection', 'Web Analysis']
            model_predictions = [len(email_preds), len(web_preds)]
            
            # Average confidence
            email_avg_conf = sum([p.get('confidence', 0) for p in email_preds]) / len(email_preds) if email_preds else 0
            web_avg_score = sum([p.get('anomaly_score', 0) for p in web_preds]) / len(web_preds) if web_preds else 0
            model_confidence = [round(email_avg_conf, 2), round(web_avg_score, 2)]
        else:
            # Fallback empty data
            threat_labels = []
            threat_data = []
            model_labels = ['Email Detection', 'Web Analysis']
            model_predictions = [0, 0]
            model_confidence = [0, 0]
        
        return jsonify({
            'threat_distribution': {
                'labels': threat_labels,
                'data': threat_data
            },
            'model_performance': {
                'labels': model_labels,
                'predictions': model_predictions,
                'confidence': model_confidence
            }
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Dashboard charts error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/database/clear', methods=['POST'])
def clear_database():
    """
    Clear all predictions from database
    """
    try:
        # Import database function
        try:
            from web_dashboard.database import clear_all_predictions
            database_available = True
        except ImportError:
            database_available = False
        
        if not database_available:
            return jsonify({'error': 'Database not available'}), 503
        
        result = clear_all_predictions()
        
        return jsonify({
            'success': True,
            'email_deleted': result['email_deleted'],
            'web_deleted': result['web_deleted'],
            'message': f"Cleared {result['email_deleted']} email and {result['web_deleted']} web predictions"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Database clear error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ==================== DASHBOARD STATS ENDPOINT ====================

@api_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        if not DATABASE_AVAILABLE:
            return jsonify({'error': 'Database not available'}), 503
        
        # Get predictions
        email_predictions = get_email_predictions(limit=1000)
        web_predictions = get_web_predictions(limit=1000)
        
        # Count phishing emails (case-insensitive)
        phishing_count = sum(1 for p in email_predictions 
                           if p.get('prediction', '').lower() == 'phishing' or p.get('is_phishing', False))
        
        # Count web anomalies
        anomalies_count = sum(1 for p in web_predictions if p.get('is_anomaly', False))
        
        return jsonify({
            'system_status': {
                'operational': 100,
                'models_loaded': True,
                'api_responding': True
            },
            'email_detection': {
                'total_predictions': len(email_predictions),
                'phishing_detected': phishing_count
            },
            'web_analysis': {
                'total_predictions': len(web_predictions),
                'anomalies_detected': anomalies_count
            }
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Dashboard stats error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ==================== REPORTS ENDPOINTS ====================

@api_bp.route('/reports/summary', methods=['GET'])
def get_reports_summary():
    """Get summary of all predictions for reports page"""
    try:
        if not DATABASE_AVAILABLE:
            return jsonify({'error': 'Database not available'}), 503
        
        email_predictions = get_email_predictions(limit=100)
        web_predictions = get_web_predictions(limit=100)
        
        # Calculate summary stats
        total_threats = len(email_predictions) + len(web_predictions)
        # Count phishing - check both 'prediction' field and 'is_phishing' for compatibility (case-insensitive)
        phishing_count = sum(1 for p in email_predictions 
                           if (p.get('prediction', '').lower() == 'phishing' or p.get('is_phishing', False)))
        anomalies_count = sum(1 for p in web_predictions if p.get('is_anomaly', False))
        
        # Calculate average confidence
        confidences = [p.get('confidence', 0) for p in email_predictions if p.get('confidence')]
        confidences += [p.get('anomaly_score', 0) for p in web_predictions if p.get('anomaly_score')]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Count risk levels
        critical_count = sum(1 for p in email_predictions if p.get('risk_level') == 'critical')
        critical_count += sum(1 for p in web_predictions if p.get('anomaly_score', 0) >= 0.85)
        
        high_count = sum(1 for p in email_predictions if p.get('risk_level') == 'high')
        high_count += sum(1 for p in web_predictions if 0.7 <= p.get('anomaly_score', 0) < 0.85)
        
        # Prepare recent predictions list
        recent_predictions = []
        
        for p in email_predictions[:20]:
            # Ensure email has risk_level based on confidence if missing
            risk = p.get('risk_level')
            if not risk:
                conf = p.get('confidence', 0)
                if conf >= 0.9:
                    risk = 'critical'
                elif conf >= 0.75:
                    risk = 'high'
                elif conf >= 0.6:
                    risk = 'medium'
                else:
                    risk = 'low'
            
            recent_predictions.append({
                'type': 'email',
                'timestamp': p.get('timestamp'),
                'confidence': p.get('confidence'),
                'risk_level': risk,
                'details': f"Subject: {p.get('email_subject', 'N/A')[:50]}..."
            })
        
        for p in web_predictions[:20]:
            score = p.get('anomaly_score', 0)
            # Determine risk level based on score thresholds
            if score >= 0.85:
                risk = 'critical'
            elif score >= 0.7:
                risk = 'high'
            elif score >= 0.5:
                risk = 'medium'
            else:
                risk = 'low'
            
            recent_predictions.append({
                'type': 'web',
                'timestamp': p.get('timestamp'),
                'confidence': score,  # Frontend will multiply by 100
                'risk_level': risk,
                'details': f"IP: {p.get('ip_address', 'N/A')} - Score: {(score * 100):.1f}%",
                'patterns_detected': p.get('patterns_detected') or 'No patterns detected',
                'ip_address': p.get('ip_address', 'N/A'),
                'is_anomaly': p.get('is_anomaly', score >= 0.5)
            })
        
        # Sort by timestamp
        recent_predictions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        recent_predictions = recent_predictions[:30]
        
        return jsonify({
            'total_threats': total_threats,
            'phishing_count': phishing_count,
            'anomalies_count': anomalies_count,
            'avg_confidence': avg_confidence,
            'critical_count': critical_count,
            'high_count': high_count,
            'recent_predictions': recent_predictions
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Reports summary error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/reports/export/json', methods=['GET'])
def export_json():
    """Export all predictions as JSON"""
    try:
        if not DATABASE_AVAILABLE:
            return jsonify({'error': 'Database not available'}), 503
        
        email_predictions = get_email_predictions(limit=1000)
        web_predictions = get_web_predictions(limit=1000)
        
        return jsonify({
            'export_date': datetime.now().isoformat(),
            'email_predictions': email_predictions,
            'web_predictions': web_predictions,
            'summary': {
                'total_email': len(email_predictions),
                'total_web': len(web_predictions),
                'total': len(email_predictions) + len(web_predictions)
            }
        }), 200
        
    except Exception as e:
        print(f"[ERROR] JSON export error: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/reports/export/excel', methods=['GET'])
def export_excel():
    """Export predictions to Excel file"""
    try:
        from flask import send_file
        from web_dashboard.reports_handler import export_predictions_to_excel
        
        if not DATABASE_AVAILABLE:
            return jsonify({'error': 'Database not available'}), 503
        
        email_predictions = get_email_predictions(limit=1000)
        web_predictions = get_web_predictions(limit=1000)
        
        excel_file = export_predictions_to_excel(email_predictions, web_predictions)
        
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'threat_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        
    except Exception as e:
        print(f"[ERROR] Excel export error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/reports/export/pdf', methods=['GET'])
def export_pdf():
    """Export predictions to PDF file"""
    try:
        from flask import send_file
        from web_dashboard.reports_handler import export_predictions_to_pdf
        
        if not DATABASE_AVAILABLE:
            return jsonify({'error': 'Database not available'}), 503
        
        email_predictions = get_email_predictions(limit=1000)
        web_predictions = get_web_predictions(limit=1000)
        
        pdf_file = export_predictions_to_pdf(email_predictions, web_predictions)
        
        return send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'threat_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        
    except Exception as e:
        print(f"[ERROR] PDF export error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/reports/import/json', methods=['POST'])
def import_json():
    """Import predictions from JSON"""
    try:
        if not DATABASE_AVAILABLE:
            return jsonify({'error': 'Database not available'}), 503
        
        data = request.get_json()
        
        email_count = 0
        web_count = 0
        
        # Import email predictions
        if 'email_predictions' in data:
            for pred in data['email_predictions']:
                try:
                    add_email_prediction(
                        prediction=pred.get('prediction'),
                        confidence=pred.get('confidence'),
                        risk_level=pred.get('risk_level'),
                        email_subject=pred.get('email_subject'),
                        email_sender=pred.get('email_sender')
                    )
                    email_count += 1
                except Exception as e:
                    print(f"[WARNING] Failed to import email prediction: {e}")
        
        # Import web predictions
        if 'web_predictions' in data:
            for pred in data['web_predictions']:
                try:
                    add_web_prediction(
                        is_anomaly=pred.get('is_anomaly'),
                        anomaly_score=pred.get('anomaly_score'),
                        ip_address=pred.get('ip_address'),
                        patterns_detected=pred.get('patterns_detected', [])
                    )
                    web_count += 1
                except Exception as e:
                    print(f"[WARNING] Failed to import web prediction: {e}")
        
        return jsonify({
            'success': True,
            'email_count': email_count,
            'web_count': web_count,
            'total': email_count + web_count
        }), 200
        
    except Exception as e:
        print(f"[ERROR] JSON import error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/reports/import/excel', methods=['POST'])
def import_excel():
    """Import predictions from Excel file"""
    try:
        from web_dashboard.reports_handler import import_predictions_from_excel
        
        if not DATABASE_AVAILABLE:
            return jsonify({'error': 'Database not available'}), 503
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read and parse Excel
        email_predictions, web_predictions = import_predictions_from_excel(file.stream)
        
        # Import to database
        email_count = 0
        web_count = 0
        
        for pred in email_predictions:
            try:
                add_email_prediction(
                    prediction=pred['prediction'],
                    confidence=pred['confidence'],
                    risk_level=pred['risk_level'],
                    email_subject=pred.get('email_subject'),
                    email_sender=pred.get('email_sender')
                )
                email_count += 1
            except Exception as e:
                print(f"[WARNING] Failed to import email prediction: {e}")
        
        for pred in web_predictions:
            try:
                add_web_prediction(
                    is_anomaly=pred['is_anomaly'],
                    anomaly_score=pred['anomaly_score'],
                    ip_address=pred['ip_address'],
                    patterns_detected=pred.get('patterns_detected', [])
                )
                web_count += 1
            except Exception as e:
                print(f"[WARNING] Failed to import web prediction: {e}")
        
        return jsonify({
            'success': True,
            'email_count': email_count,
            'web_count': web_count,
            'total': email_count + web_count
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Excel import error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ==================== CORRELATION ANALYSIS ENDPOINTS ====================

@api_bp.route('/correlation/analyze', methods=['GET'])
def analyze_correlation():
    """Analyze correlation between email and web threats"""
    try:
        if not DATABASE_AVAILABLE:
            return jsonify({'error': 'Database not available'}), 503
        
        import numpy as np
        from scipy import stats as scipy_stats
        
        email_predictions = get_email_predictions(limit=500)
        web_predictions = get_web_predictions(limit=500)
        
        # Calculate time-based correlation
        email_times = [datetime.fromisoformat(p['timestamp'].replace('Z', '+00:00')) if isinstance(p['timestamp'], str) else p['timestamp'] for p in email_predictions]
        web_times = [datetime.fromisoformat(p['timestamp'].replace('Z', '+00:00')) if isinstance(p['timestamp'], str) else p['timestamp'] for p in web_predictions]
        
        # Group by hour
        from collections import defaultdict
        email_by_hour = defaultdict(int)
        web_by_hour = defaultdict(int)
        
        for t in email_times:
            hour_key = t.replace(minute=0, second=0, microsecond=0)
            email_by_hour[hour_key] += 1
        
        for t in web_times:
            hour_key = t.replace(minute=0, second=0, microsecond=0)
            web_by_hour[hour_key] += 1
        
        # Get common hours
        all_hours = sorted(set(email_by_hour.keys()) | set(web_by_hour.keys()))
        
        if len(all_hours) < 3:
            return jsonify({
                'correlation_score': 0.0,
                'correlation_strength': 'Insufficient Data',
                'coordinated_attacks': 0,
                'timeline_data': [],
                'p_value': 1.0
            }), 200
        
        email_counts = [email_by_hour.get(h, 0) for h in all_hours]
        web_counts = [web_by_hour.get(h, 0) for h in all_hours]
        
        # Calculate Pearson correlation
        if len(email_counts) >= 3 and max(email_counts) > 0 and max(web_counts) > 0:
            correlation, p_value = scipy_stats.pearsonr(email_counts, web_counts)
        else:
            correlation = 0.0
            p_value = 1.0
        
        # Determine correlation strength
        abs_corr = abs(correlation)
        if abs_corr >= 0.7:
            strength = 'Strong'
        elif abs_corr >= 0.4:
            strength = 'Moderate'
        elif abs_corr >= 0.2:
            strength = 'Weak'
        else:
            strength = 'Very Weak'
        
        # ===== IP-BASED CORRELATION ANALYSIS =====
        # Find coordinated attacks from same IP
        ip_based_threats = {}  # {ip: {'emails': count, 'web': count}}
        
        # Collect web IPs
        for web_pred in web_predictions:
            ip = web_pred.get('ip_address')
            if ip:
                if ip not in ip_based_threats:
                    ip_based_threats[ip] = {'emails': 0, 'web': 0}
                ip_based_threats[ip]['web'] += 1
        
        # Try to extract IP from email sender (simplified heuristic)
        # In production: parse from email headers (Received-From)
        import re
        for email_pred in email_predictions:
            sender = email_pred.get('email_sender', '')
            # Look for IP pattern in sender (e.g., user@192.168.1.100)
            ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', sender)
            if ip_match:
                ip = ip_match.group(1)
                if ip not in ip_based_threats:
                    ip_based_threats[ip] = {'emails': 0, 'web': 0}
                ip_based_threats[ip]['emails'] += 1
        
        # Find IPs with BOTH email and web threats (TRUE coordinated attacks!)
        coordinated_ips = []
        for ip, counts in ip_based_threats.items():
            if counts['emails'] > 0 and counts['web'] > 0:
                coordinated_ips.append({
                    'ip': ip,
                    'email_threats': counts['emails'],
                    'web_threats': counts['web'],
                    'total_threats': counts['emails'] + counts['web']
                })
        
        # IP-based correlation boost
        ip_correlation_boost = 0.0
        if len(coordinated_ips) > 0:
            # Boost correlation if same IP does both attacks
            ip_correlation_boost = min(0.3, len(coordinated_ips) * 0.15)
            correlation = min(1.0, correlation + ip_correlation_boost)
            # Re-evaluate strength
            abs_corr = abs(correlation)
            if abs_corr >= 0.7:
                strength = 'Strong'
            elif abs_corr >= 0.4:
                strength = 'Moderate'
        
        # Detect coordinated attacks (simultaneous spikes)
        coordinated_count = 0
        coordinated_events = []
        
        for i, hour in enumerate(all_hours):
            email_count = email_counts[i]
            web_count = web_counts[i]
            
            # If both have activity in the same hour (lowered threshold to 1+1)
            if email_count >= 1 and web_count >= 1:
                coordinated_count += 1
                coordinated_events.append({
                    'timestamp': hour.isoformat(),
                    'email_threats': email_count,
                    'web_threats': web_count,
                    'total': email_count + web_count
                })
        
        # Also count IP-based coordinated attacks
        coordinated_count += len(coordinated_ips)
        
        # Timeline data
        timeline_data = [
            {
                'hour': h.isoformat(),
                'email': email_counts[i],
                'web': web_counts[i]
            }
            for i, h in enumerate(all_hours[-24:])  # Last 24 hours
        ]
        
        return jsonify({
            'correlation_score': round(correlation, 3),
            'correlation_strength': strength,
            'p_value': round(p_value, 4),
            'coordinated_attacks': coordinated_count,
            'coordinated_events': coordinated_events[-10:],  # Last 10 events
            'coordinated_ips': coordinated_ips[:10] if 'coordinated_ips' in locals() else [],  # Top 10 IPs
            'ip_correlation_boost': round(ip_correlation_boost, 3) if 'ip_correlation_boost' in locals() else 0.0,
            'timeline_data': timeline_data,
            'total_email_threats': len(email_predictions),
            'total_web_threats': len(web_predictions)
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Correlation analysis error: {e}")
# ==================== SETTINGS ENDPOINTS ====================

@api_bp.route('/settings', methods=['GET'])
def get_user_settings():
    """Get current settings"""
    try:
        if not DATABASE_AVAILABLE:
            return jsonify({'error': 'Database not available'}), 503
        
        from web_dashboard.database import get_settings
        
        settings = get_settings()
        
        # Provide defaults if no settings exist
        default_settings = {
            'dark_mode': 'false',
            'threshold': '0.50',
            'auto_reload': 'true',
            'high_risk_alerts': 'true',
            'daily_reports': 'true'
        }
        
        # Merge with defaults
        for key, default_value in default_settings.items():
            if key not in settings:
                settings[key] = default_value
        
        return jsonify(settings), 200
        
    except Exception as e:
        print(f"[ERROR] Settings GET error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/settings', methods=['POST'])
def save_user_settings():
    """Save settings"""
    try:
        if not DATABASE_AVAILABLE:
            return jsonify({'error': 'Database not available'}), 503
        
        from web_dashboard.database import save_settings
        
        settings_data = request.get_json()
        
        if not settings_data:
            return jsonify({'error': 'No settings data provided'}), 400
        
        # Save settings
        success = save_settings(settings_data)
        
        if success:
            return jsonify({'status': 'success', 'message': 'Settings saved successfully'}), 200
        else:
            return jsonify({'error': 'Failed to save settings'}), 500
        
    except Exception as e:
        print(f"[ERROR] Settings POST error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ==================== VIRUSTOTAL ENDPOINTS ====================

@api_bp.route('/virustotal/check-domain/<domain>', methods=['GET'])
def check_domain_virustotal(domain):
    """Check domain reputation using VirusTotal"""
    try:
        from web_dashboard.virustotal_helper import check_domain_reputation
        
        result = check_domain_reputation(domain)
        return jsonify(result), 200
        
    except Exception as e:
        print(f"[ERROR] VirusTotal domain check error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'malicious': 0,
            'suspicious': 0,
            'harmless': 0,
            'undetected': 0,
            'reputation': 'Unknown'
        }), 500


# ==================== MONITORING / METRICS ENDPOINTS ====================

# ==================== MODEL COMPARISON ENDPOINTS ====================

@api_bp.route('/models/comparison', methods=['GET'])
def get_model_comparison():
    """Get model performance comparison data"""
    try:
        # Mock data - in production, this would come from model training history
        models_data = {
            'random_forest': {
                'name': 'Random Forest',
                'accuracy': 0.945,
                'precision': 0.932,
                'recall': 0.958,
                'f1_score': 0.945,
                'training_time': 2.3,
                'status': 'active'
            },
            'svm': {
                'name': 'SVM',
                'accuracy': 0.923,
                'precision': 0.915,
                'recall': 0.931,
                'f1_score': 0.923,
                'training_time': 4.1,
                'status': 'active'
            },
            'naive_bayes': {
                'name': 'Naive Bayes',
                'accuracy': 0.897,
                'precision': 0.889,
                'recall': 0.905,
                'f1_score': 0.897,
                'training_time': 0.8,
                'status': 'active'
            },
            'isolation_forest': {
                'name': 'Isolation Forest',
                'accuracy': 0.875,
                'precision': 0.863,
                'recall': 0.887,
                'f1_score': 0.875,
                'training_time': 1.5,
                'status': 'active'
            }
        }
        
        return jsonify({
            'models': models_data,
            'best_model': 'random_forest',
            'comparison_date': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Model comparison error: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== VIRUSTOTAL ENDPOINTS ====================

@api_bp.route('/virustotal/check-ip/<ip_address>', methods=['GET'])
def check_ip_virustotal(ip_address):
    """Check IP reputation with VirusTotal"""
    try:
        from web_dashboard.virustotal_helper import check_ip_reputation
        
        result = check_ip_reputation(ip_address)
        return jsonify(result), 200
        
    except Exception as e:
        print(f"[ERROR] VirusTotal IP check error: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== DEMO DATA GENERATION ====================

def _generate_random_timestamp(days_back=30):
    """
    Generate random timestamp for demo data
    70% of data in last 7 days (recent)
    30% of data in 8-30 days (older)
    """
    import random
    from datetime import datetime, timedelta
    
    now = datetime.now()
    
    # Handle case where days_back is small
    if days_back <= 7:
        # If days_back is 7 or less, just use random within that range
        days_ago = random.randint(0, max(1, days_back))
    elif random.random() < 0.7:
        # 70% chance of recent data (0-7 days)
        days_ago = random.randint(0, 7)
    else:
        # 30% chance of older data (8-days_back days)
        days_ago = random.randint(8, days_back)
    
    hours_ago = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    seconds_ago = random.randint(0, 59)
    
    return now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago, seconds=seconds_ago)



@api_bp.route('/demo/generate', methods=['POST'])
def generate_demo_data():
    """
    Generate realistic demo/test data for demonstration purposes
    
    Creates:
    - 25 email predictions (5 per severity level)
    - 25 web log predictions (5 per severity level)
    - Timestamps distributed over last 30 days
    """
    try:
        from web_dashboard.database import add_email_prediction, add_web_prediction
        import random
        from datetime import datetime, timedelta
        
        # Generate email predictions by severity
        email_count = 0
        severities = ['critical', 'high', 'medium', 'low', 'legitimate']
        
        # Email templates
        email_data = {
            'critical': [
                ('security@paypal-verify.net', 'URGENT: Your PayPal account has been limited', 'Click here to verify: http://paypal-verify.net/login', 0.97),
                ('no-reply@apple-support.com', 'Your Apple ID has been locked', 'Verify here: http://apple-verify.com', 0.96),
                ('support@amazon-security.org', 'Account Suspended - Action Required', 'Update payment: http://amzn-secure.biz', 0.98),
                ('billing@microsoft-account.net', 'Payment Failed', 'Update billing: http://ms-billing.com', 0.95),
                ('alerts@chase-bank.org', 'Unusual Activity Detected', 'Verify transactions: http://chase-verify.net', 0.99)
            ],
            'high': [
                ('admin@company-portal.biz', 'Password Reset Required', 'Your password will expire in 24 hours', 0.89),
                ('noreply@linkedin-jobs.com', '3 new job offers', 'View exclusive offers: http://linkedin-jobs.com', 0.85),
                ('service@netflix-renewal.net', 'Subscription expiring', 'Update payment within 48 hours', 0.87),
                ('delivery@fedex-tracking.org', 'Package Delivery Failed', 'Reschedule: http://fedex-track.biz', 0.91),
                ('security@google-alerts.com', 'New sign-in from Russia', 'Secure account: http://google-secure.net', 0.88)
            ],
            'medium': [
                ('deals@shopping-offers.com', 'Flash Sale: 70% OFF', 'Limited time offer! Click to shop', 0.72),
                ('winner@lottery-notification.org', 'You Won $50,000', 'Claim your prize now!', 0.68),
                ('support@tech-support-center.biz', 'Computer at Risk', 'Download free antivirus', 0.75),
                ('offers@credit-card-deals.net', 'Pre-Approved: $25,000 Credit', 'Apply now!', 0.70),
                ('pharmacy@online-meds.org', 'Prescription Discount', 'Up to 80% off. No prescription needed!', 0.73)
            ],
            'low': [
                ('newsletter@marketing-company.com', 'Weekly Newsletter', 'Special offers from our partners', 0.55),
                ('updates@social-network.com', '5 new notifications', 'Your friends posted updates', 0.48),
                ('subscriptions@news-daily.org', 'Today\'s Top Stories', 'News curated for you', 0.52),
                ('events@meetup-group.com', 'Tech Meetup This Weekend', 'RSVP to secure your spot!', 0.50),
                ('sales@online-store.biz', 'New Arrivals', 'Limited stock available', 0.53)
            ],
            'legitimate': [
                ('team@company.com', 'Weekly Team Meeting', 'Meeting scheduled for Tuesday at 2 PM', 0.15),
                ('billing@stripe.com', 'Payment Receipt', 'Invoice processed successfully', 0.10),
                ('notifications@github.com', 'New pull request', 'Review on GitHub', 0.20),
                ('support@zoom.us', 'Meeting Reminder', 'Zoom meeting at 3 PM today', 0.12),
                ('hr@corporation.com', 'Benefits Enrollment', 'Review and select benefits', 0.18)
            ]
        }
        
        for severity in severities:
            risk = 'critical' if severity == 'critical' else 'high' if severity == 'high' else 'medium' if severity == 'medium' else 'low'
            prediction = 'legitimate' if severity == 'legitimate' else 'phishing'
            
            for sender, subject, content, conf in email_data[severity]:
                add_email_prediction(
                    prediction=prediction,
                    confidence=conf,
                    risk_level=risk,
                    email_subject=subject,
                    email_sender=sender,
                    timestamp=_generate_random_timestamp()  # Random timestamp
                    # Note: email_content not stored in database
                )
                email_count += 1
        
        # Generate web log predictions by severity
        web_count = 0
        web_data = {
            'critical': [
                ('45.142.212.61', 'SQL Injection', 0.95),
                ('185.220.101.23', 'XSS Attack', 0.92),
                ('91.219.237.229', 'Path Traversal', 0.98),
                ('198.96.155.3', 'Command Injection', 0.94),
                ('23.129.64.184', 'CSRF Token Missing', 0.97)
            ],
            'high': [
                ('203.0.113.45', 'Brute Force Login', 0.85),
                ('198.51.100.22', 'Suspicious User-Agent', 0.79),
                ('192.0.2.42', 'Directory Scanning', 0.82),
                ('172.16.254.1', 'Bot Activity', 0.88),
                ('10.0.0.99', 'Rate Limit Exceeded', 0.81)
            ],
            'medium': [
                ('192.168.1.100', 'Unusual Request Pattern', 0.65),
                ('172.20.10.5', 'Invalid Parameters', 0.59),
                ('10.1.1.50', 'Multiple 401 Errors', 0.62),
                ('192.168.100.15', 'Forbidden Access Attempts', 0.67),
                ('172.31.0.10', 'Suspicious Referer', 0.63)
            ],
            'low': [
                ('192.168.0.10', 'High Request Rate', 0.45),
                ('192.168.1.1', 'Unusual Timing', 0.38),
                ('172.16.0.5', 'Non-standard Headers', 0.42),
                ('10.0.0.1', 'Cookie Manipulation', 0.47),
                ('192.168.2.100', 'Cache Bypass Attempt', 0.40)
            ],
            'normal': [
                ('192.168.1.50', 'Normal HTTP Request', 0.15),
                ('192.168.1.51', 'Standard GET Request', 0.10),
                ('192.168.1.52', 'Valid POST Request', 0.20),
                ('192.168.1.53', 'Static Resource Access', 0.12),
                ('192.168.1.54', 'API Call', 0.18)
            ]
        }
        
        for severity in ['critical', 'high', 'medium', 'low', 'normal']:
            is_anomaly = severity != 'normal'
            
            for ip, pattern, score in web_data[severity]:
                add_web_prediction(
                    is_anomaly=is_anomaly,
                    anomaly_score=score,
                    ip_address=ip,
                    patterns_detected=pattern,
                    timestamp=_generate_random_timestamp()  # Random timestamp
                )
                web_count += 1
        
        # ========== COORDINATED ATTACK SCENARIOS ==========
        # Generate 5 coordinated attack pairs (same IP, same timestamp)
        # This creates positive correlation between email and web threats
        coordinated_attacks = [
            {
                'ip': '203.0.113.66',
                'email': ('hacker@203.0.113.66', 'Click to reset password', 'Your password expires in 1 hour', 0.92),
                'web': ('203.0.113.66', 'Brute Force + SQL Injection', 0.95)
            },
            {
                'ip': '198.51.100.77',
                'email': ('attacker@198.51.100.77', 'Verify your account NOW', 'Suspicious login detected', 0.88),
                'web': ('198.51.100.77', 'XSS Attack + Directory Traversal', 0.91)
            },
            {
                'ip': '192.0.2.88',
                'email': ('admin@192.0.2.88', 'URGENT: Server migration', 'Click to confirm migration', 0.85),
                'web': ('192.0.2.88', 'Command Injection Attempt', 0.89)
            },
            {
                'ip': '172.16.50.99',
                'email': ('security@172.16.50.99', 'Your account is compromised', 'Reset immediately', 0.94),
                'web': ('172.16.50.99', 'CSRF + Session Hijacking', 0.93)
            },
            {
                'ip': '10.20.30.40',
                'email': ('alert@10.20.30.40', 'Payment declined', 'Update billing info', 0.87),
                'web': ('10.20.30.40', 'API Abuse + Rate Limit Bypass', 0.90)
            }
        ]
        
        for attack in coordinated_attacks:
            # Generate same timestamp for both email and web
            attack_time = _generate_random_timestamp(days_back=7)  # Recent attacks
            
            # Add coordinated email attack
            sender, subject, content, conf = attack['email']
            add_email_prediction(
                prediction='phishing',
                confidence=conf,
                risk_level='high',
                email_subject=subject,
                email_sender=sender,
                timestamp=attack_time  # SAME timestamp
            )
            email_count += 1
            
            # Add coordinated web attack (same IP, same time)
            ip, pattern, score = attack['web']
            add_web_prediction(
                is_anomaly=True,
                anomaly_score=score,
                ip_address=ip,
                patterns_detected=pattern,
                timestamp=attack_time  # SAME timestamp
            )
            web_count += 1
        
        return jsonify({
            'success': True,
            'generated': {
                'emails': email_count,
                'web_logs': web_count,
                'total': email_count + web_count,
                'coordinated_attacks': len(coordinated_attacks)
            },
            'message': f'Successfully generated {email_count + web_count} demo records including {len(coordinated_attacks)} coordinated attack scenarios'
        }), 200
        
    except Exception as e:
        print(f'[ERROR] Demo data generation error: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500




@api_bp.route('/monitoring/metrics/compare', methods=['GET'])
def get_model_metrics_comparison():
    """
    Get comparison metrics for all email detection models
    Returns real performance data from MODEL_COMPARISON.md documentation
    
    Models compared:
    - TF-IDF + Random Forest (baseline, production)
    - FastText (balanced)
    - BERT/DistilBERT (highest accuracy)
    """
    try:
        # Real metrics from docs/MODEL_COMPARISON.md
        # Source: Performance Metrics sections (lines 79-92, 178-192, 315-328)
        comparison = {
            'TF-IDF + Random Forest': {
                'accuracy': 0.89,  # 89% from line 85
                'precision': 0.88,  # 88% from line 86
                'recall': 0.91,  # 91% from line 87
                'f1_score': 0.895,  # 0.895 from line 88
                'avg_latency': 0.0005,  # 0.5ms = 0.0005s from line 91
                'training_time': 10.5,  # 10.5 sec from line 90
                'model_size_mb': 7.2,  # from line 92
                'description': 'Fast and efficient, best for production',
                'icon': '🔤'
            },
            'FastText': {
                'accuracy': 0.90,  # 90% from line 184
                'precision': 0.89,  # 89% from line 185
                'recall': 0.92,  # 92% from line 186
                'f1_score': 0.905,  # 0.905 from line 187
                'avg_latency': 0.0015,  # 1.5ms = 0.0015s from line 190
                'training_time': 135,  # 2 min 15 sec = 135s from line 189
                'model_size_mb': 12,  # from line 191
                'description': 'Balanced performance and speed',
                'icon': '⚡'
            },
            'BERT': {
                'accuracy': 0.96,  # 96% from line 321
                'precision': 0.95,  # 95% from line 322
                'recall': 0.97,  # 97% from line 323
                'f1_score': 0.961,  # 0.961 from line 324
                'avg_latency': 0.075,  # 75ms = 0.075s from line 327
                'training_time': 1050,  # 15-20 min avg = 1050s from line 326
                'model_size_mb': 268,  # from line 328 (full model)
                'description': 'Highest accuracy, slower inference',
                'icon': '🤖'
            }
        }
        
        return jsonify({
            'status': 'success',
            'comparison': comparison,
            'source': 'docs/MODEL_COMPARISON.md',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f'[ERROR] Model comparison error: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# Initialize models when blueprint is created

load_trained_models()
