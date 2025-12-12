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
            _email_detector = EmailPhishingDetector()
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
        # Load email detection models
        _tfidf_vectorizer = joblib.load(models_dir / 'tfidf_vectorizer.pkl')
        _stacking_model = joblib.load(models_dir / 'email_detector_stacking.pkl')
        _voting_model = joblib.load(models_dir / 'email_detector_voting.pkl')
        
        # Load web anomaly models
        _web_anomaly_detector = joblib.load(models_dir / 'web_anomaly_detector.pkl')
        _web_scaler = joblib.load(models_dir / 'log_scaler.pkl')
        
        print("[SUCCESS] All trained models loaded successfully")
        return True
    except FileNotFoundError as e:
        print(f"[WARNING] Some models not found: {e}")
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


# Initialize models when blueprint is created
load_trained_models()
